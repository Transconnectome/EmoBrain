#!/bin/bash
# S10 6-4i(01): 뇌 표현과 장면 표현의 정렬. GPU 없음, 로그인 노드 CPU.
# 사용(레포 최상위): bash scripts/s10_align.sh <단계> <동결 커밋> [그 밖의 옵션]
#   단계 brain:  참가자 5명의 뇌 PCA(src/s10_align_data.py brain)
#   단계 shared: ① Shared-AE와 ③(src/s10_shared_ae.py fit, 참가자마다) 뒤 summarize
#   단계 usae:   ② Universal SAE와 ③(src/s10_usae.py fit, fold마다) 뒤 summarize
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
STEP="${1:?단계(brain, shared, usae)}"; FREEZE="${2:?설계 동결 커밋}"; shift 2
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=4 MKL_NUM_THREADS=4
OUT="$OUT_ROOT/s10_stats/alignment"; mkdir -p "$LOGS/s10_alignment"
case "$STEP" in
  brain)
    for s in 01 02 03 04 05; do "$PY" s10_align_data.py brain --participant "$s" --out "$OUT" --design-freeze "$FREEZE" --threads 4 "$@" & done; wait ;;
  shared)
    # 참가자 5명 × 바깥 fold 6개를 동시에 JOBS개(각 2코어, 사용자당 32코어 한도 안)
    JOBS="${JOBS:-10}"
    for s in 01 02 03 04 05; do for k in 1 2 3 4 5 6; do echo "$s $k"; done; done | \
      xargs -P "$JOBS" -n 2 sh -c '"$0" s10_shared_ae.py fit --participant "$1" --fold "$2" --out "'"$OUT"'" --design-freeze "'"$FREEZE"'" --threads 2 > "'"$LOGS"'/s10_alignment/shared_fit_sub-$1_fold$2.log" 2>&1' "$PY"
    for s in 01 02 03 04 05; do "$PY" s10_shared_ae.py readout --participant "$s" --out "$OUT" --design-freeze "$FREEZE" & done; wait
    "$PY" s10_shared_ae.py summarize --out "$OUT" --stats-root "$OUT_ROOT/s10_stats" ;;
  usae)
    for k in 1 2 3 4 5 6; do "$PY" s10_usae.py fit --fold "$k" --out "$OUT" --design-freeze "$FREEZE" --threads 2 > "$LOGS/s10_alignment/usae_fold$k.log" 2>&1 & done; wait
    "$PY" s10_usae.py summarize --out "$OUT" ;;
  *) echo "단계는 brain, shared, usae 가운데 하나" >&2; exit 1 ;;
esac
