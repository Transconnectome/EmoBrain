#!/bin/bash
# FEELIN — swift_UAH_51M_SL20 full run
# 10 leaf scripts 를 순차 실행. Resume 가능 (이미 있는 npz skip).

set -e
cd /pscratch/sd/s/sjmoon/FEELIN

MODEL_TAG="swift_UAH_51M_SL20"
OUT_PREFIX="swift_UAH_51M_SL20"
LEAF_DIR="code/bfm_embeddings/extract_embedding/${MODEL_TAG}"
LOG_DIR="output/logs/${MODEL_TAG}"
mkdir -p "${LOG_DIR}"

LEAFS=("${LEAF_DIR}"/*.sh)
TOTAL="${#LEAFS[@]}"
COUNT=0
START_ALL=$(date +%s)

echo "============================================================"
echo "${MODEL_TAG} full extraction (${TOTAL} runs)"
echo "Start: $(date)"
echo "============================================================"

for leaf in "${LEAFS[@]}"; do
  COUNT=$((COUNT + 1))
  name=$(basename "${leaf}" .sh)            # ex: swift_NewE96_SL20_resting_replicate_sub-01
  short="${name#${MODEL_TAG}_}"             # resting_replicate_sub-01
  init=$(echo "$short" | cut -d_ -f1)       # resting
  pad=$(echo "$short" | cut -d_ -f2)        # replicate
  sub=$(echo "$short" | cut -d_ -f3-)       # sub-01
  LOG="${LOG_DIR}/${name}.log"
  OUT_PT="output/embeddings/${OUT_PREFIX}_${init}_pad-${pad}/${sub}.pt"

  if [ -f "$OUT_PT" ]; then
    echo "[${COUNT}/${TOTAL}] SKIP ${name} (already exists)"
    continue
  fi

  echo "[${COUNT}/${TOTAL}] ${name} → ${LOG}"
  START=$(date +%s)
  bash "${leaf}" > "${LOG}" 2>&1
  END=$(date +%s)
  echo "  done in $((END - START))s"
done

END_ALL=$(date +%s)
echo "============================================================"
echo "${MODEL_TAG} done. Total: $((END_ALL - START_ALL))s"
echo "============================================================"
