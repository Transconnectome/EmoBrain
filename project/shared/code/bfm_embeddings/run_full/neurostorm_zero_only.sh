#!/bin/bash
# FEELIN — NeuroSTORM zero padding extraction.
# 5 subj × 2 init × zero = 10 cells. ~30min-1h on 1 GPU.
set -e
cd /pscratch/sd/s/sjmoon/FEELIN

LEAF_DIR="code/bfm_embeddings/extract_embedding/neurostorm"
LOG_DIR="output/logs/neurostorm_zero"
mkdir -p "${LOG_DIR}"

START_ALL=$(date +%s)
echo "============================================================"
echo "NeuroSTORM padding=zero extraction"
echo "Start: $(date)"
echo "============================================================"

COUNT=0
TOTAL=10
for leaf in "${LEAF_DIR}"/neurostorm_resting_zero_sub-*.sh "${LEAF_DIR}"/neurostorm_scratch_zero_sub-*.sh; do
  COUNT=$((COUNT + 1))
  name=$(basename "${leaf}" .sh)
  LOG="${LOG_DIR}/${name}.log"
  short="${name#neurostorm_}"
  init=$(echo "$short" | cut -d_ -f1)
  pad=$(echo "$short" | cut -d_ -f2)
  sub=$(echo "$short" | cut -d_ -f3-)
  OUT_PT="output/embeddings/neurostorm_${init}_pad-${pad}/${sub}.pt"
  if [ -f "$OUT_PT" ]; then
    echo "[${COUNT}/${TOTAL}] SKIP ${name} (exists)"
    continue
  fi
  echo "[${COUNT}/${TOTAL}] ${name}  → ${LOG}"
  START=$(date +%s)
  bash "${leaf}" > "${LOG}" 2>&1
  END=$(date +%s)
  echo "  done in $((END - START))s"
done

END_ALL=$(date +%s)
echo "============================================================"
echo "Done in $((END_ALL - START_ALL))s. New extracts at output/embeddings/neurostorm_*_pad-zero/"
echo "============================================================"
