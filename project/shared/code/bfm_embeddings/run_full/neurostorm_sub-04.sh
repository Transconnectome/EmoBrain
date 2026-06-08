#!/bin/bash
# FEELIN — neurostorm, sub-04 only (2 leaf: 2 init x mean padding)
# Sequential, resume-safe (skips existing .pt).
set -e
cd /pscratch/sd/s/sjmoon/FEELIN

MODEL_TAG="neurostorm"
OUT_PREFIX="neurostorm"
LEAF_DIR="/pscratch/sd/s/sjmoon/FEELIN/project/shared/code/bfm_embeddings/extract_embedding/${MODEL_TAG}"
LOG_DIR="/pscratch/sd/s/sjmoon/FEELIN/project/shared/output/logs/${MODEL_TAG}"
mkdir -p "${LOG_DIR}"

LEAFS=("${LEAF_DIR}"/neurostorm_*_sub-04.sh)
TOTAL="${#LEAFS[@]}"
COUNT=0
START_ALL=$(date +%s)

echo "============================================================"
echo "${MODEL_TAG} sub-04 extraction (${TOTAL} runs)"
echo "Start: $(date)"
echo "============================================================"

for leaf in "${LEAFS[@]}"; do
  COUNT=$((COUNT + 1))
  name=$(basename "${leaf}" .sh)
  short="${name#${MODEL_TAG}_}"
  init=$(echo "$short" | cut -d_ -f1)
  pad=$(echo "$short" | cut -d_ -f2)
  sub=$(echo "$short" | cut -d_ -f3-)
  LOG="${LOG_DIR}/${name}.log"
  OUT_PT="/pscratch/sd/s/sjmoon/FEELIN/project/shared/output/embeddings/${OUT_PREFIX}_${init}_pad-${pad}/${sub}.pt"

  if [ -f "$OUT_PT" ]; then
    echo "[${COUNT}/${TOTAL}] SKIP ${name} (already exists)"
    continue
  fi

  echo "[${COUNT}/${TOTAL}] ${name} -> ${LOG}"
  START=$(date +%s)
  bash "${leaf}" > "${LOG}" 2>&1
  END=$(date +%s)
  echo "  done in $((END - START))s"
done

END_ALL=$(date +%s)
echo "============================================================"
echo "${MODEL_TAG} sub-04 done. Total: $((END_ALL - START_ALL))s"
echo "============================================================"
