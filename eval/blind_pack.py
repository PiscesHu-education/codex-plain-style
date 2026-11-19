#!/usr/bin/env python3
"""Build blind rating packs: one folder per question, three anonymised answers.

    python3 eval/blind_pack.py --raw /tmp/eval/raw --out /tmp/eval/blind \
        --key /tmp/eval/key.json

Produces <out>/q01/question.md and answer-X.md / answer-Y.md / answer-Z.md,
with the version shuffled per question under a fixed seed so the mapping is
reproducible but not guessable from order. <key> stores q -> {X/Y/Z: arm};
keep it out of the raters' hands.

Raters must not see the key, the raw/ directory, or each other's scores.
"""

import argparse
import glob
import json
import os
import random
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
QDIR = os.path.join(ROOT, "eval", "questions")
SEED = 20261119


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raw", required=True, help="raw/<arm>/<question>.md from extract.py")
    ap.add_argument("--out", required=True, help="blind pack output directory")
    ap.add_argument("--key", required=True, help="where to write the q -> arm key (JSON)")
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    keys = sorted(os.path.basename(p)[:-3] for p in glob.glob(os.path.join(QDIR, "*.md")))
    if os.path.exists(args.out):
        shutil.rmtree(args.out)
    os.makedirs(args.out)

    key = {}
    for i, k in enumerate(keys, 1):
        d = os.path.join(args.out, f"q{i:02d}")
        os.makedirs(d)
        q = open(os.path.join(QDIR, k + ".md"), encoding="utf-8").read().strip()
        open(os.path.join(d, "question.md"), "w", encoding="utf-8").write(q + "\n")
        arms = ["A", "B", "C"]
        rng.shuffle(arms)
        key[f"q{i:02d}"] = dict(zip("XYZ", arms))
        for code, arm in zip("XYZ", arms):
            src = os.path.join(args.raw, arm, k + ".md")
            if not os.path.exists(src):
                print(f"missing {src} — run extract.py first and read its "
                      "missing-list; a reworded question no longer matches "
                      "rollouts recorded before the reword",
                      file=sys.stderr)
                return 1
            open(os.path.join(d, f"answer-{code}.md"), "w", encoding="utf-8").write(
                open(src, encoding="utf-8").read())
    json.dump(key, open(args.key, "w", encoding="utf-8"), indent=1)
    print(f"{len(keys)} packs -> {args.out}; key -> {args.key}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
