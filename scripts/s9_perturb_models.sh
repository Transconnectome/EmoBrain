#!/bin/bash
# S9 네트워크 교란의 모델 확장과 정서 head 입력 표현 저장(src/s9_perturb_models.py). GPU 1장, login node, 약 1시간(어림). 규칙은 파이썬 파일 머리말.
# 사용(레포 최상위): CUDA_VISIBLE_DEVICES=<번호> bash scripts/s9_perturb_models.sh <S6 최종> <s6_brain_depth2> <s6_brain_depth4> <출력 폴더 절대 경로> <동결 커밋> [--folds 1,2]
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
cd "$ROOT/src"
"$PY" s9_perturb_models.py --s6-dir "${1:?S6 최종}" --depth2-dir "${2:?depth2}" --depth4-dir "${3:?depth4}" --out "${4:?출력 폴더}" --design-freeze "${5:?동결 커밋}" "${@:6}"
