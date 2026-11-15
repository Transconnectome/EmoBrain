#!/bin/bash
# S10 합성 자료 시험(1부 tests/s10_tests.py, 2부 tests/s10b_tests.py, K1과 14개 차원 tests/s10_k1_tests.py). 실제 정답, 실제 예측, GPU를 쓰지 않는다. configs/env.sh의 EMOBRAIN_PYTHON_CPU가 있으면 그림 시험도 한다. 사용(레포 최상위): bash scripts/s10_tests.sh
set -euo pipefail
source "$(dirname "$0")/_env.sh"
export OMP_NUM_THREADS=4 CUDA_VISIBLE_DEVICES=''
"$PY" "$ROOT/tests/s10_tests.py" "$@"
"$PY" "$ROOT/tests/s10b_tests.py"
"$PY" "$ROOT/tests/s10_k1_tests.py"
