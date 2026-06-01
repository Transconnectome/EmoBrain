#!/bin/bash
# Master script: SwiFT 6 variants (NewE36 → NewE96 → NewE192 → UAH_5M → UAH_51M → UAH_202M)
# 의 A_reg probe 를 sequential 하게 실행. 한 GPU 노드에서 다 처리.
# 예상 시간: ~20-30min × 6 = 2-3h.
set -e

echo "============================================================"
echo "A_reg: SwiFT 6 variants sequential probe"
echo "Start: $(date)"
echo "============================================================"
START_ALL=$(date +%s)

for variant in SwiFT_NewE36 SwiFT_NewE96 SwiFT_NewE192 SwiFT_UAH_5M SwiFT_UAH_51M SwiFT_UAH_202M; do
  echo ""
  echo ">>> [${variant}] A_reg 시작 $(date)"
  START=$(date +%s)
  bash /pscratch/sd/s/sjmoon/FEELIN/code/probes/wrappers/bfm/${variant}/A_reg.sh
  END=$(date +%s)
  echo ">>> [${variant}] A_reg 끝 (elapsed $((END - START))s)"
done

END_ALL=$(date +%s)
echo ""
echo "============================================================"
echo "A_reg all 6 variants done. Total: $((END_ALL - START_ALL))s"
echo "============================================================"
