#!/bin/zsh
# 跑一臂评测：./eval/run-arm.sh <臂名> <提示词文件> [题目目录]
# 题目目录默认 eval/questions，产出写到 eval/out/<臂名>-<题名>.md
set -u
CODEX="${CODEX:-/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex}"
ROOT="${EVAL_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
ARM=$1
P=$2
QDIR="${3:-$ROOT/eval/questions}"
OUT="$ROOT/eval/out"
mkdir -p "$OUT"

for f in "$QDIR"/*.md; do
  b=$(basename "$f" .md)
  if [ -s "$OUT/$ARM-$b.md" ]; then echo "skip $b"; continue; fi
  echo "### $(date +%H:%M:%S) $ARM $b"
  "$CODEX" exec --skip-git-repo-check -C "$ROOT" -s workspace-write \
    -c "model_instructions_file=\"$P\"" -c 'model_max_output_tokens=8000' \
    -o "$OUT/$ARM-$b.md" < "$f" > "$OUT/$ARM-$b.log" 2>&1
  echo "exit=$? size=$(wc -c < "$OUT/$ARM-$b.md" 2>/dev/null)"
done
echo "DONE-$ARM"
