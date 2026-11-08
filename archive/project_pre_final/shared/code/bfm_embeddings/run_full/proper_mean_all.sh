#!/bin/bash
# Proper mean padding 으로 5 subject × 3 BFM (SwiFT NewE96 + Brain-JEPA + NeuroSTORM) × 2 init
# = 30 cell 전체 추출. 단일 GPU sequential.
#
# 사용법:
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/shared/code/bfm_embeddings/run_full/proper_mean_all.sh
#
# Resume-safe (이미 추출된 .pt 자동 skip).
# 1 GPU 예상 시간: ~3-4 시간.

set -e

RUN_FULL=/pscratch/sd/s/sjmoon/EmoBrain/project/shared/code/bfm_embeddings/run_full

for sub in sub-01 sub-02 sub-03 sub-04 sub-05; do
  for model in swift_NewE96_SL20 brain_jepa neurostorm; do
    wrapper="${RUN_FULL}/${model}_${sub}.sh"
    echo ""
    echo "============================================================"
    echo "[ALL] $(date +%H:%M:%S) ${model} ${sub}"
    echo "============================================================"
    bash "${wrapper}"
  done
done

echo ""
echo "============================================================"
echo "[ALL] proper mean extraction complete."
echo "============================================================"
