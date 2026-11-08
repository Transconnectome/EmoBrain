#!/bin/bash
# S2 분할 목록 파일. split_hk_dev.tsv와 fold_roles.tsv에서 manifests/s2/splits/<실행 단위>/{train,val,test}.txt를 만든다. --check는 비교만 한다. CPU, 1초.
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
PYTHONDONTWRITEBYTECODE=1 "$PY_CPU" s2_split_files.py "$@"
