#!/bin/bash
# EmoBrain — SwiFT NewE96 의 cyclic_replicate padding 만 추가 추출.
# T frames 를 SL=20 까지 cyclic 반복 (e.g. T=5 → f0..f4, f0..f4, f0..f4, f0..f4).
# 5 subject × 2 init (resting + scratch) = 10 cells. ~1-2h on 1 GPU.
set -e
cd /pscratch/sd/s/sjmoon/EmoBrain

PYTHON=/pscratch/sd/s/sjmoon/swift_PTL2/bin/python
OUT_ROOT=/pscratch/sd/s/sjmoon/EmoBrain/project/shared/output/embeddings
LIB=code/bfm_embeddings/_lib/swift.py
LOG_DIR=output/logs/swift_NewE96_SL20_cyclic
mkdir -p "${LOG_DIR}"

INITS=(resting scratch)
SUBJECTS=(sub-01 sub-02 sub-03 sub-04 sub-05)

TOTAL=$((${#INITS[@]} * ${#SUBJECTS[@]}))
COUNT=0
START_ALL=$(date +%s)
echo "============================================================"
echo "SwiFT NewE96 × cyclic_replicate × 2 init × 5 subj  →  ${TOTAL} runs"
echo "Start: $(date)"
echo "============================================================"

for init in "${INITS[@]}"; do
  for sub in "${SUBJECTS[@]}"; do
    COUNT=$((COUNT + 1))
    OUT_PT="${OUT_ROOT}/swift_NewE96_SL20_${init}_pad-cyclic_replicate/${sub}.pt"
    LOG="${LOG_DIR}/swift_NewE96_${init}_${sub}.log"
    if [ -f "${OUT_PT}" ]; then
      echo "[${COUNT}/${TOTAL}] SKIP ${init}/${sub} (exists)"
      continue
    fi
    echo "[${COUNT}/${TOTAL}] swift_NewE96_${init}_cyclic_replicate_${sub}  → ${LOG}"
    START=$(date +%s)
    ${PYTHON} ${LIB} \
      --model_name NewUAH_newE96 \
      --output_tag NewE96_SL20 \
      --init "${init}" \
      --padding cyclic_replicate \
      --subject "${sub}" \
      --seed 0 \
      --batch_size 4 \
      --num_workers 2 \
      --out_root "${OUT_ROOT}" \
      > "${LOG}" 2>&1
    END=$(date +%s)
    echo "  done in $((END - START))s"
  done
done

END_ALL=$(date +%s)
echo "============================================================"
echo "Done. Total: $((END_ALL - START_ALL))s"
echo "Embeddings at ${OUT_ROOT}/swift_NewE96_SL20_*_pad-cyclic_replicate/"
echo "다음:"
echo "  bash code/probes/wrappers/bfm/SwiFT_padding_cyclic_only/V_binary.sh  (등 4개)"
echo "============================================================"
