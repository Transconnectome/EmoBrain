#!/bin/bash
# Read-only recon so the assistant can see current state (configs, trainer
# schema, encoder names, env deps) without ls/cat access. Writes one file.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/state_check.sh
set -uo pipefail
ROOT=/pscratch/sd/s/sjmoon/EmoBrain
PY=/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python
OUT=$ROOT/project/output/state_check.txt
mkdir -p "$ROOT/project/output"
cd "$ROOT"
{
  echo "===== configs in project/code/configs ====="
  ls -1 project/code/configs/ 2>&1
  echo
  echo "===== any vit/e1/bfm/e2 config contents ====="
  for f in project/code/configs/*vit* project/code/configs/*e1* project/code/configs/*bfm* project/code/configs/*e2* project/code/configs/*student*; do
    [ -f "$f" ] && { echo "--- $f"; cat "$f"; echo; }
  done 2>/dev/null
  echo "===== trainer.py (config keys it reads) ====="
  grep -nE "cfg\[|cfg.get|args\.|add_argument|brain_source|hard_kind|out_json|HorikawaDataset|make_collate|forward_batch" project/code/training/trainer.py 2>&1 | head -60
  echo
  echo "===== registered encoders + their register names ====="
  $PY -c "import sys; sys.path.insert(0,'.'); from project.code.brain_encoder.registry import available; print(available())" 2>&1
  grep -rn "register_encoder(" project/code/brain_encoder/*.py 2>&1
  echo
  echo "===== brainvlm_qwen_env deps ====="
  $PY -c "import importlib.util as u; [print(m, bool(u.find_spec(m))) for m in ['pandas','sklearn','scipy','numpy','torch','yaml','nibabel','transformers','peft']]" 2>&1
} > "$OUT" 2>&1
echo "wrote $OUT"
