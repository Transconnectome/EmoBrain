#!/bin/bash
# Usage:
#   bash export_poster_figures.sh
#   bash export_poster_figures.sh --watch-minutes 270 --interval-seconds 120

set -euo pipefail

ROOT="/pscratch/sd/s/sjmoon/EmoBrain/archive/v5_direction_split_20260628/dir3_ccn"
PYTHON="/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python"

export PYTHONDONTWRITEBYTECODE=1
export MPLCONFIGDIR="$ROOT/study1/data/.matplotlib"
mkdir -p "$MPLCONFIGDIR" "$ROOT/study1/results/poster_export"

cd "$ROOT/study1/code/poster_figures"
"$PYTHON" -u export_poster_figures.py "$@"
