#!/bin/bash
# Blackout backup: stage our code/docs + E1 result JSON, guard large files,
# commit, push. Diagnostic: prints commit/push exit codes so failures are visible.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/git_update.sh
set -uo pipefail
cd /pscratch/sd/s/sjmoon/EmoBrain

git add -A project docs CLAUDE.md tools Paper 2>/dev/null || git add -A project docs CLAUDE.md
git add -f project/output/e1_vit_direct_qwen3vl4b.json project/output/e1_vit_smoke.json 2>/dev/null || true

echo "===== staged ====="
git status --short | grep -vE '^\?\?' | head -80

echo "===== large-file guard (>5MB) ====="
BIG=0
while read -r f; do
  [ -f "$f" ] || continue
  s=$(stat -c%s "$f" 2>/dev/null || echo 0)
  if [ "$s" -gt 5000000 ]; then echo "BIG: $f ($((s/1000000))MB)"; BIG=1; fi
done < <(git diff --cached --name-only)
if [ "$BIG" -ne 0 ]; then echo "ABORT: large file staged. unstaging."; git reset -q; exit 1; fi

if git diff --cached --quiet; then
  echo "NOTHING STAGED -> nothing to commit"
else
  MSGFILE="$(mktemp)"
  printf '%s\n' "[TRAIN] Qwen3-VL runner + E1 ViT result + BJ native fix + canonical rules" \
    "" \
    "run_qwen3vl launcher, qwen/e1-smoke/state-check scripts, E1 ViT direct" \
    "result (held-out test profile pearson 0.154), Brain-JEPA emb_h skip fix." > "$MSGFILE"
  git commit -F "$MSGFILE"      # NOT quiet: show summary or the error
  echo "commit exit=$?"
  rm -f "$MSGFILE"
fi

echo "===== push ====="
git push origin main
echo "push exit=$?"
echo "===== last commit now ====="
git log --oneline -1
