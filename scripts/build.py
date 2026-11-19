#!/usr/bin/env python3
"""Build a Codex base-instruction file from the template already on this machine.

The base template is read from the Codex client's own model cache
(~/.codex/models_cache.json), the anchored edits in .patch/ are applied, and the
rules in rules/zh.rules.md are appended. Nothing from OpenAI's template is stored
in this repository; the build reproduces it from the copy the client downloaded.

Typical use:

    python3 scripts/build.py --list
    python3 scripts/build.py                    # build with the generic profile
    python3 scripts/build.py --verify ~/.codex/prompts/codex-plain-style.md
    python3 scripts/build.py --output ~/.codex/prompts/codex-plain-style.md

Exit codes: 0 ok, 1 build error (anchor mismatch, unknown model, output mismatch).
"""

import argparse
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPEC_PATH = os.path.join(ROOT, ".patch", "plain-style.edits.json")
RULES_PATH = os.path.join(ROOT, "rules", "zh.rules.md")
PROFILES_PATH = os.path.join(ROOT, "rules", "profiles.toml")
DEFAULT_CACHE = os.path.expanduser("~/.codex/models_cache.json")
DEFAULT_OUTPUT = os.path.expanduser("~/.codex/prompts/codex-plain-style.md")


class BuildError(Exception):
    pass


def read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise BuildError(f"file not found: {path}")
    except json.JSONDecodeError as exc:
        raise BuildError(f"not valid JSON: {path} ({exc})")


def read_text(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise BuildError(f"file not found: {path}")


def load_base_from_cache(cache_path, slug):
    data = read_json(cache_path)
    models = data.get("models") or []
    for m in models:
        if m.get("slug") == slug:
            tpl = (m.get("model_messages") or {}).get("instructions_template")
            if not tpl:
                raise BuildError(f"model {slug!r} has no instructions_template in the cache")
            return tpl, data.get("client_version"), data.get("fetched_at")
    slugs = ", ".join(repr(m.get("slug")) for m in models)
    raise BuildError(f"model {slug!r} not in cache. Available slugs: {slugs}")


def list_models(cache_path):
    data = read_json(cache_path)
    print(f"cache: {cache_path}")
    print(f"client_version: {data.get('client_version')}  fetched_at: {data.get('fetched_at')}")
    print()
    for m in data.get("models") or []:
        tpl = (m.get("model_messages") or {}).get("instructions_template") or ""
        vis = m.get("visibility") or ""
        print(f"  {m.get('slug'):<22} {len(tpl):>7} chars  {vis}")


def parse_profiles(text):
    """Minimal TOML subset: [section] headers and key = "string" lines."""
    profiles, current = {}, None
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1].strip()
            profiles.setdefault(current, {})
            continue
        if "=" not in line or current is None:
            raise BuildError(f"profiles.toml line {n}: cannot parse {raw!r}")
        key, _, value = line.partition("=")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] == '"':
            value = value[1:-1]
        profiles[current][key.strip()] = value
    if not profiles:
        raise BuildError(f"no profiles in {PROFILES_PATH}")
    return profiles


def render_rules(template, values):
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    leftover = [seg.split("}}")[0] for seg in template.split("{{")[1:]]
    if leftover:
        raise BuildError(f"unfilled placeholders in rules: {', '.join(leftover)}")
    return template


def find_line(lines, prefix, edit_id):
    hits = [i for i, line in enumerate(lines) if line.startswith(prefix)]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        raise BuildError(
            f"edit {edit_id!r}: no line starts with {prefix[:70]!r}. "
            "The base template has changed; update .patch/plain-style.edits.json.")
    raise BuildError(
        f"edit {edit_id!r}: {len(hits)} lines start with {prefix[:70]!r}; the anchor is ambiguous.")


def apply_edits(base, edits):
    text = base.rstrip()
    for e in edits:
        op = e["op"]
        if op == "replace_paragraph":
            i = find_line(text.split("\n"), e["anchor"], e["id"])
            lines = text.split("\n")
            before = lines[:i]
            after = lines[i + 1:]
            if before and before[-1] != "" and op == "replace_paragraph":
                pass  # keep original spacing; paragraph is replaced in place
            text = "\n".join(before + [e["new"]] + after)
        elif op == "insert_paragraph_before":
            lines = text.split("\n")
            i = find_line(lines, e["anchor"], e["id"])
            text = "\n".join(lines[:i] + [e["new"], ""] + lines[i:])
        elif op == "replace_range":
            start = find_line(text.split("\n"), e["from"], e["id"])
            end = find_line(text.split("\n"), e["until"], e["id"])
            if end <= start:
                raise BuildError(f"edit {e['id']!r}: until-line comes before from-line")
            lines = text.split("\n")
            text = "\n".join(lines[:start] + [e["replacement"]] + lines[end:])
        else:
            raise BuildError(f"edit {e['id']!r}: unknown op {op!r}")
    return text


def build(args):
    if args.base_file:
        base = read_text(args.base_file)
        source = f"file {args.base_file}"
        version = fetched = None
    else:
        base, version, fetched = load_base_from_cache(args.cache, args.model)
        source = f"cache {args.cache}"

    spec = read_json(SPEC_PATH)
    profiles = parse_profiles(read_text(PROFILES_PATH))
    local_profiles_path = os.path.join(ROOT, "rules", "profiles.local.toml")
    if os.path.exists(local_profiles_path):
        profiles.update(parse_profiles(read_text(local_profiles_path)))
    if args.profile not in profiles:
        raise BuildError(
            f"profile {args.profile!r} not found; available: {', '.join(sorted(profiles))}")
    rules = render_rules(read_text(RULES_PATH), profiles[args.profile]).rstrip()

    edited = apply_edits(base, spec["edits"])
    final = edited + "\n\n" + rules + "\n"
    return final, source, version, fetched


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--model", default="gpt-6.2-sol",
                    help="model slug whose instructions_template to use (default: gpt-6.2-sol)")
    ap.add_argument("--cache", default=DEFAULT_CACHE, help="path to models_cache.json")
    ap.add_argument("--base-file", help="use this file as the base template instead of the cache")
    ap.add_argument("--profile", default="generic", help="profile name in rules/profiles.toml")
    ap.add_argument("--output", default=DEFAULT_OUTPUT, help="where to write the result")
    ap.add_argument("--list", action="store_true", help="list models in the cache and exit")
    ap.add_argument("--dry-run", action="store_true", help="print the result, write nothing")
    ap.add_argument("--verify", metavar="FILE",
                    help="compare the built result with FILE and exit 0 only if identical")
    ap.add_argument("--force", action="store_true",
                    help="allow writing outside ~/.codex/prompts without --verify")
    args = ap.parse_args(argv)

    try:
        if args.list:
            list_models(args.cache)
            return 0
        final, source, version, fetched = build(args)
    except BuildError as exc:
        print(f"build failed: {exc}", file=sys.stderr)
        return 1

    meta = [f"base: {source}"]
    if version:
        meta.append(f"client_version: {version}")
    if fetched:
        meta.append(f"fetched_at: {fetched}")
    meta.append(f"length: {len(final)} chars")
    print("\n".join(meta), file=sys.stderr)

    if args.verify:
        existing = read_text(args.verify)
        if existing == final:
            print(f"identical to {args.verify}", file=sys.stderr)
            return 0
        print(f"DIFFERS from {args.verify} (built {len(final)} chars, file {len(existing)} chars)",
              file=sys.stderr)
        return 1

    if args.dry_run:
        sys.stdout.write(final)
        return 0

    out = os.path.abspath(os.path.expanduser(args.output))
    if not args.force and not out.startswith(os.path.expanduser("~/.codex/prompts") + os.sep):
        print(f"refusing to write {out} without --force or --verify", file=sys.stderr)
        return 1
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if os.path.exists(out):
        stamp = time.strftime("%Y%m%d-%H%M%S")
        backup = f"{out}.bak-{stamp}"
        shutil.copy2(out, backup)
        print(f"backed up previous file to {backup}", file=sys.stderr)
    with open(out, "w", encoding="utf-8") as f:
        f.write(final)
    print(f"wrote {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
