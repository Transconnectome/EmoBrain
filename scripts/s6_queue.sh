#!/bin/bash
# S6 분할 여러 개(6-2 구역 분할, 6-4a 묶음, HK 최종 모델)를 빈 login node GPU에 차례로 띄우는 실행기를 login node에서 오래 도는 CPU 프로세스(nohup)로 켠다.
# GPU는 쓰지 않는다. sbatch를 내지 않는다. 규칙과 이유는 scripts/s6_queue.py 머리말. 먼저 --dry-run으로 어림을 본다.
# 사용(레포 최상위): bash scripts/s6_queue.sh <tag> <run worktree> <동결 커밋> <작업 TSV 절대 경로> [s6_queue.py 옵션]
set -euo pipefail
source "$(dirname "$0")/_env.sh"
TAG="${1:?tag}"; RUN_ROOT="${2:?run worktree}"; FREEZE="${3:?동결 커밋}"; JOBS="${4:?작업 TSV}"; shift 4
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1
ARGS=(--tag "$TAG" --run-root "$RUN_ROOT" --freeze "$FREEZE" --jobs "$JOBS" "$@")
for x in "$@"; do
    if [ "$x" = "--dry-run" ]; then
        exec "$PY" "$ROOT/scripts/s6_queue.py" "${ARGS[@]}"
    fi
done
LOG="$(dirname "$JOBS")/s6_queue_${TAG}.log"
nohup "$PY" "$ROOT/scripts/s6_queue.py" "${ARGS[@]}" >> "$LOG" 2>&1 < /dev/null &
echo "queue 실행기 pid $! (host $(hostname)), log $LOG"
