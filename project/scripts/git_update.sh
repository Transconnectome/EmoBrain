#!/bin/bash
# Blackout backup: stage our code/docs/configs + the E1 ViT result JSON, guard
# against large files, commit, push. Run:
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/git_update.sh
set -uo pipefail
cd /pscratch/sd/s/sjmoon/EmoBrain

# our tree only (project/, docs/, CLAUDE.md, tools/, Paper/); gitignore handles
# large binaries and project/output|shared/output. Never stage external/*.
git add -A project docs CLAUDE.md tools Paper 2>/dev/null || git add -A project docs CLAUDE.md
# small result JSONs for the record (past the project/output gitignore)
git add -f project/output/e1_vit_direct_qwen3vl4b.json project/output/e1_vit_smoke.json 2>/dev/null || true

echo "===== staged ====="
git status --short | head -60

echo "===== large-file guard (>5MB) ====="
BIG=0
while read -r f; do
  [ -f "$f" ] || continue
  s=$(stat -c%s "$f" 2>/dev/null || echo 0)
  if [ "$s" -gt 5000000 ]; then echo "ABORT: big file staged: $f ($((s/1000000))MB)"; BIG=1; fi
done < <(git diff --cached --name-only)
if [ "$BIG" -ne 0 ]; then echo "unstaging and aborting."; git reset -q; exit 1; fi

git commit -q -F - <<'MSG'
[TRAIN] First real Qwen3-VL run + canonical rules + Brain-JEPA native fix

- Canonical rules (CLAUDE.md): encoders E1 ViT / E2 BFM only; Qwen3-VL-4B backbone;
  raw/ridge are baselines not encoders; short-window transfer framing for Brain-JEPA.
- backbone_qwen: Qwen3VLForConditionalGeneration + last-valid-token pooling
  (handles internal multimodal padding). Verified: forward + full training loop
  on GPU.
- Brain-JEPA load_pretrained: skip non-learned sin/cos emb_h (native one-patch)
  instead of the legacy 10->1 average; validation confirmed native > legacy on
  emotion_34d (0.0003 -> 0.0087, p=0.029). import_corrected_brain_jepa registers
  brain_jepa_pretrained_native_mean.
- Training infra: run_qwen3vl launcher, e1/e2 direct/teacher/distill configs,
  train_teacher/cache_soft_labels/train_student_distill with provenance guards.
- Result: E1 ViT direct brain-only student trains (val 0 -> 0.172 over 8 epochs),
  held-out test profile pearson 0.154. Pipeline is live; fusion/distillation next.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
MSG

git push origin main 2>&1 | tail -3
echo "[git_update] done"
