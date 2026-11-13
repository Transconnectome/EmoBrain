#!/bin/bash
# S6 A-1 후보 grid를 빈 login node GPU 여러 장에 나눠 띄우는 실행기를 login node에서 오래 도는 CPU 프로세스(nohup)로 켠다. GPU는 쓰지 않는다. sbatch를 내지 않는다.
# 규칙과 이유는 scripts/s6_grid.py 머리말. 먼저 --dry-run으로 묶음과 어림을 본다.
# 사용(레포 최상위): bash scripts/s6_grid.sh <run worktree> <동결 커밋> <설정 상대 경로> <출력 폴더 절대 경로> [s6_grid.py 옵션]
set -euo pipefail
source "$(dirname "$0")/_env.sh"
RUN_ROOT="${1:?run worktree}"; FREEZE="${2:?동결 커밋}"; CONFIG="${3:?설정}"; S6OUT="${4:?출력 폴더}"; shift 4
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1
ARGS=(--run-root "$RUN_ROOT" --freeze "$FREEZE" --config "$CONFIG" --s6-out "$S6OUT" "$@")
for x in "$@"; do
    if [ "$x" = "--dry-run" ]; then
        exec "$PY" "$ROOT/scripts/s6_grid.py" "${ARGS[@]}"
    fi
done
LOG="$(dirname "$S6OUT")/logs/s6_grid_$(basename "$S6OUT").log"
mkdir -p "$(dirname "$LOG")"
nohup "$PY" "$ROOT/scripts/s6_grid.py" "${ARGS[@]}" >> "$LOG" 2>&1 < /dev/null &
echo "grid 실행기 pid $! (host $(hostname)), log $LOG"
