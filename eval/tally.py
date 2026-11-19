#!/usr/bin/env python3
"""Aggregate blind scores back onto the three arms.

Score files live in one directory, one per rater (j1.md, j2.md, ...). Each line
holds one rating, four integers on the 0-3 scale of rubric-v2:

    q05 X 3 3 2 2
    q05 Y 3 3 2 2

Columns after the letter are: 一眼看到重点 / 结构服务内容 / 读完的意愿 / 能直接
抄用的句子. For rubric v1 (six dimensions of 0-2) the script still sums whatever
is present; pass --dims to name the columns.

    python3 eval/tally.py --key /tmp/eval/key.json --scores /tmp/eval/scores
"""

import argparse
import glob
import json
import os
import re
import sys

PAT = re.compile(r"(q\d\d)\s+([XYZ])\s+((?:\d\s*)+)")
DEFAULT_DIMS = ["一眼看到重点", "结构服务内容", "读完的意愿", "能直接抄用的句子"]


def load(path):
    rows = {}
    for line in open(path, encoding="utf-8"):
        m = PAT.search(line)
        if not m:
            continue
        rows[(m.group(1), m.group(2))] = [int(x) for x in m.group(3).split()]
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--key", required=True, help="q -> {X/Y/Z: arm} mapping")
    ap.add_argument("--scores", required=True, help="directory of per-rater score files")
    ap.add_argument("--dims", nargs="+", default=DEFAULT_DIMS)
    args = ap.parse_args()

    key = json.load(open(args.key, encoding="utf-8"))
    judges = {os.path.basename(p)[:-3]: load(p)
              for p in sorted(glob.glob(os.path.join(args.scores, "j*.md")))}
    if not judges:
        print("no score files found", file=sys.stderr)
        return 1
    print("entries per judge:", {k: len(v) for k, v in judges.items()})

    arm_sums, arm_dims, per_q = {}, {}, {}
    width = len(args.dims)
    for judge, rows in judges.items():
        for (q, code), sc in rows.items():
            arm = key[q][code]
            sc = (sc + [0] * width)[:width]
            arm_sums[arm] = arm_sums.get(arm, 0) + sum(sc)
            dims = arm_dims.setdefault(arm, [0] * width)
            for i, x in enumerate(sc):
                dims[i] += x
            per_q.setdefault(q, {}).setdefault(arm, []).append(sum(sc))

    print("\nsum by arm:")
    for arm in sorted(arm_sums):
        print(f"  {arm}: sum={arm_sums[arm]}")
    print("\nper dimension (each cell = sum over questions and raters):")
    print("  arm  " + "  ".join(f"{d:>8}" for d in args.dims) + "  total")
    for arm in sorted(arm_dims):
        print(f"  {arm}    " + "  ".join(f"{x:8d}" for x in arm_dims[arm])
              + f"  {sum(arm_dims[arm])}")
    print("\nper question:")
    for q in sorted(per_q):
        cells = "  ".join(f"{a}={per_q[q].get(a, [])}" for a in sorted(per_q[q]))
        print(f"  {q}: {cells}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
