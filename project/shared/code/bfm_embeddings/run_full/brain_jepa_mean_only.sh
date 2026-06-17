#!/bin/bash
# EmoBrain — Brain-JEPA mean padding only re-extraction (NUM_FRAMES=16, center-crop).
# 5 subj × 2 init × mean = 10 cells.  ~1-2h on 1 GPU.
# Old extracts (T=20, first 16) archived as brain_jepa_LEGACY_T20first16_*.
set -e
cd /pscratch/sd/s/sjmoon/EmoBrain

LEAF_DIR="code/bfm_embeddings/extract_embedding/brain_jepa"
LOG_DIR="output/logs/brain_jepa_T16center"
mkdir -p "${LOG_DIR}"

START_ALL=$(date +%s)
echo "============================================================"
echo "Brain-JEPA NUM_FRAMES=16 center-crop re-extraction"
echo "Start: $(date)"
echo "============================================================"

COUNT=0
TOTAL=10
for leaf in "${LEAF_DIR}"/brain_jepa_resting_mean_sub-*.sh "${LEAF_DIR}"/brain_jepa_scratch_mean_sub-*.sh; do
  COUNT=$((COUNT + 1))
  name=$(basename "${leaf}" .sh)
  LOG="${LOG_DIR}/${name}.log"
  short="${name#brain_jepa_}"
  init=$(echo "$short" | cut -d_ -f1)
  pad=$(echo "$short" | cut -d_ -f2)
  sub=$(echo "$short" | cut -d_ -f3-)
  OUT_PT="output/embeddings/brain_jepa_${init}_pad-${pad}/${sub}.pt"
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
echo "Done in $((END_ALL - START_ALL))s. New extracts at output/embeddings/brain_jepa_*_pad-mean/"
echo "Probe: bash code/probes/wrappers/bfm/Brain-JEPA/{V_binary,A_binary,V_reg,A_reg}.sh"
echo "============================================================"
