#!/bin/bash
# S6 한 조건의 후보 일부만 같은 실행 번호로 학습한다(GPU). 학습 코드는 run worktree의 src를 그대로 쓴다. 규칙은 scripts/s6_candidates.py 머리말.
# 사용: bash s6_candidates.sh <run worktree> --plan outer_fold<k> --conditions brain_only,brain_only_distill --config <설정 절대 경로> --design-freeze <커밋> --target <조건>:<id>,<id> [--device cuda]
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_ROOT="${1:?run worktree}"; shift
source "$RUN_ROOT/scripts/_env.sh"  # run worktree의 환경과 경로. src로 cd한다
export OMP_NUM_THREADS=8
"$PY" "$HERE/s6_candidates.py" "$@"
