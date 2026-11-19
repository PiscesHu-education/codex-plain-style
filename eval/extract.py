#!/usr/bin/env python3
"""Pull each arm's answer for every question out of Codex rollout files.

run-arm.sh writes one file per (arm, question), but the rollout JSONL under
~/.codex/sessions/ is the authoritative record: it carries the prompt that was
actually in effect (session_meta.payload.base_instructions.text), so an answer
can never be attributed to the wrong arm.

    python3 eval/extract.py --out /tmp/eval/raw
    python3 eval/extract.py --out /tmp/eval/raw --date 2026-11-18

Arm fingerprint: the character length of base_instructions. Edit ARMS when a
new prompt version is introduced; the build's --list shows template lengths.

Matching: the first user message in a rollout is the injected AGENTS.md block,
the second is the real question. Answers are matched to eval/questions/*.md by
their first 120 characters, and the longest assistant message is kept per
(arm, question).

wb901-scope.md was reworded on 2026-11-19 to remove a lesson-specific noun, so
rollouts recorded before that date no longer match it and the run reports
12/13. The recorded figures in results.md come from the pre-rewording run; see
"已知限制" in method.md.
"""

import argparse
import collections
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
QDIR = os.path.join(ROOT, "eval", "questions")

# base_instructions length -> arm label. Update per evaluation round.
ARMS = {
    27750: "B",   # stock template
    27508: "A",   # previous revision (v27508)
    24309: "C",   # current
    24310: "C",
}
MATCH_PREFIX = 120


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def load_questions():
    qs = {}
    for p in sorted(glob.glob(os.path.join(QDIR, "*.md"))):
        key = os.path.basename(p)[:-3]
        qs[key] = norm(open(p, encoding="utf-8").read())
    return qs


def run(sessions_dir, qs):
    out = collections.defaultdict(dict)
    files = sorted(glob.glob(os.path.join(sessions_dir, "*.jsonl")))
    for f in files:
        try:
            lines = open(f, encoding="utf-8").read().splitlines()
            meta = json.loads(lines[0])
        except (OSError, IndexError, json.JSONDecodeError):
            continue
        payload = meta.get("payload") or {}
        instr = (payload.get("base_instructions") or {}).get("text", "")
        arm = ARMS.get(len(instr))
        if not arm:
            continue
        users, asst = [], []
        for ln in lines[1:]:
            try:
                o = json.loads(ln)
            except json.JSONDecodeError:
                continue
            if o.get("type") != "response_item":
                continue
            q = o.get("payload") or {}
            if q.get("type") != "message":
                continue
            txt = "".join(c.get("text", "") for c in q.get("content", []) if isinstance(c, dict))
            if q.get("role") == "user":
                users.append(txt)
            elif q.get("role") == "assistant" and txt.strip():
                asst.append(txt)
        if len(users) < 2:
            continue
        question = norm(users[1])
        hit = [k for k, v in qs.items()
               if v[:MATCH_PREFIX] in question or question[:MATCH_PREFIX] in v]
        if not hit:
            continue
        best = max(asst, key=len) if asst else ""
        if len(best) > len(out[arm].get(hit[0], "")):
            out[arm][hit[0]] = best
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sessions", default=os.path.expanduser("~/.codex/sessions"),
                    help="Codex sessions directory (default: ~/.codex/sessions)")
    ap.add_argument("--date", default="2026/11/18",
                    help="subdirectory of the sessions dir, e.g. 2026/11/18")
    ap.add_argument("--out", required=True, help="output directory for raw/<arm>/<question>.md")
    args = ap.parse_args()

    sessions_dir = os.path.join(args.sessions, args.date)
    qs = load_questions()
    got = run(sessions_dir, qs)

    missing = False
    for arm in sorted(set(ARMS.values())):
        d = os.path.join(args.out, arm)
        os.makedirs(d, exist_ok=True)
        for k, v in got[arm].items():
            open(os.path.join(d, k + ".md"), "w", encoding="utf-8").write(v)
        gaps = sorted(set(qs) - set(got[arm]))
        print(f"{arm}: {len(got[arm])}/{len(qs)} answers"
              + (f"  missing {gaps}" if gaps else ""))
        missing = missing or bool(gaps)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
