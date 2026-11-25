#!/bin/bash
# MC 개인 모델과 네트워크 교란(src/s8_mc_individual.py). train은 GPU(참가자 한 명의 A-1, C-1, 개당 1시간 안팎), perturb는 추론만.
# 사용(레포 최상위): CUDA_VISIBLE_DEVICES=0 bash scripts/s8_mc_individual.sh train <s6_brain_final_for_mc> <출력 폴더> <커밋> <참가자 02~06>
#                   bash scripts/s8_mc_individual.sh perturb <s6_brain_final_for_mc> <출력 폴더> <커밋> <s8_mc 폴더> <개인 모델 폴더>
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
STEP="${1:?train|perturb}"; FINAL="${2:?s6_brain_final_for_mc}"; OUT="${3:?출력 폴더}"; FREEZE="${4:?동결 커밋}"
cd "$ROOT/src"
if [ "$STEP" = train ]; then
    "$PY" s8_mc_individual.py train --final "$FINAL" --out "$OUT" --participants "${5:?참가자}" --design-freeze "$FREEZE" --device cuda
else
    "$PY" s8_mc_individual.py perturb --final "$FINAL" --out "$OUT" --transfer "${5:?s8_mc}" --individual "${6:?개인 모델 폴더}" --design-freeze "$FREEZE" --device cuda
fi
