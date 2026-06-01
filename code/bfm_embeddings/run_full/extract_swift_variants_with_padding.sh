#!/bin/bash
# FEELIN — SwiFT 5 변종 (NewE36, NewE192, UAH_5M, UAH_51M, UAH_202M) 을
# SwiFT padding ablation 결과의 best padding 으로 추출.
# 5 subject × 2 init (resting + scratch) × 5 variant = 50 cell.
#
# 사용법:
#   bash extract_swift_variants_with_padding.sh <padding>
#   <padding>: mean | replicate | zero | spatial_only
#
# (NewE96 은 이미 main grid 에서 추출 완료라 제외.
#  UAH_806M / 3B / NEWdeepE192 / SL60 / HCP 모델은 scope 밖.)
set -e

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <padding>   # padding ∈ {mean, replicate, zero, spatial_only}"
  echo "Hint: best padding 은 results/phase1/swift_padding_ablation_summary.csv 의 mean test_main 최고값 기준."
  exit 1
fi

PADDING="$1"
case "$PADDING" in
  mean|replicate|zero|spatial_only) ;;
  *) echo "ERROR: unknown padding '$PADDING'. Must be one of: mean, replicate, zero, spatial_only"; exit 1 ;;
esac

cd /pscratch/sd/s/sjmoon/FEELIN
PYTHON=/pscratch/sd/s/sjmoon/swift_PTL2/bin/python
OUT_ROOT=/pscratch/sd/s/sjmoon/FEELIN/output/embeddings
LIB=code/bfm_embeddings/_lib/swift.py

# variant_tag : internal model_name (NewE96 = main grid 에 이미 있음, 제외)
declare -A VARIANT_MODELS=(
  [NewE36_SL20]=NewUAH_newE36
  [NewE192_SL20]=NewUAH_newE192
  [UAH_5M_SL20]=UAH_P1_5M
  [UAH_51M_SL20]=UAH_P2_51M
  [UAH_202M_SL20]=UAH_P3_202M
)

INITS=(resting scratch)
SUBJECTS=(sub-01 sub-02 sub-03 sub-04 sub-05)
LOG_DIR="output/logs/swift_variants_pad-${PADDING}"
mkdir -p "${LOG_DIR}"

TOTAL=$((${#VARIANT_MODELS[@]} * ${#INITS[@]} * ${#SUBJECTS[@]}))
COUNT=0
START_ALL=$(date +%s)
echo "============================================================"
echo "SwiFT 3 variants × 2 init × 5 subj × padding=${PADDING}  →  ${TOTAL} runs"
echo "Start: $(date)"
echo "============================================================"

for tag in "${!VARIANT_MODELS[@]}"; do
  model_name="${VARIANT_MODELS[$tag]}"
  for init in "${INITS[@]}"; do
    for sub in "${SUBJECTS[@]}"; do
      COUNT=$((COUNT + 1))
      OUT_PT="${OUT_ROOT}/swift_${tag}_${init}_pad-${PADDING}/${sub}.pt"
      LOG="${LOG_DIR}/swift_${tag}_${init}_${sub}.log"
      if [ -f "${OUT_PT}" ]; then
        echo "[${COUNT}/${TOTAL}] SKIP swift_${tag}_${init}_${PADDING}_${sub} (exists)"
        continue
      fi
      echo "[${COUNT}/${TOTAL}] swift_${tag}_${init}_${PADDING}_${sub}  → ${LOG}"
      START=$(date +%s)
      ${PYTHON} ${LIB} \
        --model_name "${model_name}" \
        --output_tag "${tag}" \
        --init "${init}" \
        --padding "${PADDING}" \
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
done

END_ALL=$(date +%s)
echo "============================================================"
echo "Done. Total: $((END_ALL - START_ALL))s.  Embeddings at ${OUT_ROOT}/swift_*_pad-${PADDING}/"
echo "다음: bash code/probes/wrappers/bfm/SwiFT_variants.sh ${PADDING}"
echo "============================================================"
