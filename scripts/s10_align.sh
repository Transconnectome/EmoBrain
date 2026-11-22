#!/bin/bash
# S10 6-4i(01): 뇌 표현과 장면 표현의 정렬. GPU 없음, 로그인 노드 CPU.
# 사용(레포 최상위): bash scripts/s10_align.sh <단계> <동결 커밋> [그 밖의 옵션]
#   단계 brain:  참가자 5명의 뇌 PCA(src/s10_align_data.py brain)
#   단계 usae:   ② Universal SAE와 ③(src/s10_usae.py select, fit, summarize). ①(Shared-AE)은 11/22 AffectLab으로 넘김
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
STEP="${1:?단계(brain, usae)}"; FREEZE="${2:?설계 동결 커밋}"; shift 2
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=4 MKL_NUM_THREADS=4
OUT="$OUT_ROOT/s10_stats/alignment"; mkdir -p "$LOGS/s10_alignment"
case "$STEP" in
  brain)
    for s in 01 02 03 04 05; do "$PY" s10_align_data.py brain --participant "$s" --out "$OUT" --design-freeze "$FREEZE" --threads 4 "$@" & done; wait ;;
  usae)
    # 공식 USAE 패키지가 그림용으로 matplotlib, opencv, scikit-image를 import한다. 학습 환경에 없으면 따로 설치한 폴더를 USAE_EXTRA_SITE로 준다(configs/env.sh).
    # 1) fold마다 개념 수와 k 고르기(공식 교차 복원 R² 기준, 검증 fold) 2) 고른 값으로 seed 5개 × 세 변형 학습과 읽기 3) 요약
    for k in 1 2 3 4 5 6; do "$PY" s10_usae.py select --fold "$k" --out "$OUT" --design-freeze "$FREEZE" --threads 4 > "$LOGS/s10_alignment/usae_select_fold$k.log" 2>&1 & done; wait
    for k in 1 2 3 4 5 6; do "$PY" s10_usae.py fit --fold "$k" --from-select --out "$OUT" --design-freeze "$FREEZE" --threads 4 > "$LOGS/s10_alignment/usae_fit_fold$k.log" 2>&1 & done; wait
    "$PY" s10_usae.py summarize --out "$OUT" ;;
  *) echo "단계는 brain, usae 가운데 하나" >&2; exit 1 ;;
esac
