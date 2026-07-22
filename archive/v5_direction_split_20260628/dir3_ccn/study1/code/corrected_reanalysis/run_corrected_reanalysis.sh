#!/bin/bash
# Usage: bash run_corrected_reanalysis.sh {prepare|shared-screen|shared-confirm|geometry|cortical|content} [shared_rank]

set -euo pipefail

ROOT="/pscratch/sd/s/sjmoon/EmoBrain/archive/v5_direction_split_20260628/dir3_ccn"
CODE="$ROOT/study1/code"
PYTHON="/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python"
BRAIN="$ROOT/study1/data/corrected_reanalysis/brain_jepa_native_1patch.npy"
DATA_OUT="$ROOT/study1/data/corrected_reanalysis"
RESULT_OUT="$ROOT/study1/results/corrected_reanalysis"
STAGE="${1:-}"

export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-32}"
export MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK:-32}"
export OPENBLAS_NUM_THREADS="${SLURM_CPUS_PER_TASK:-32}"
export PYTHONDONTWRITEBYTECODE=1
export MPLCONFIGDIR="$ROOT/study1/data/.matplotlib"
mkdir -p "$DATA_OUT" "$RESULT_OUT" "$ROOT/study1/logs" "$MPLCONFIGDIR"

usage() {
  echo "Usage: bash $0 {prepare|shared-screen|shared-confirm|geometry|cortical|content} [shared_rank]"
}

require_brain() {
  if [[ ! -f "$BRAIN" ]]; then
    echo "Corrected CCN input is missing: $BRAIN"
    echo "Run: bash $0 prepare"
    exit 2
  fi
}

case "$STAGE" in
  prepare)
    cd "$CODE/corrected_reanalysis"
    if [[ -f "$BRAIN" ]]; then
      "$PYTHON" -u prepare_corrected_brain_embeddings.py --check-only
      echo "Existing corrected CCN input retained: $BRAIN"
    else
      "$PYTHON" -u prepare_corrected_brain_embeddings.py
    fi
    ;;

  shared-screen)
    require_brain
    cd "$CODE/shared_alignment"
    "$PYTHON" -u run_shared_alignment.py \
      --model vjepa2_pretrained \
      --brain-path "$BRAIN" \
      --output-dir "$DATA_OUT/shared_alignment_screen" \
      --n-perm 0 \
      --n-pc 100
    ;;

  shared-confirm)
    require_brain
    cd "$CODE/shared_alignment"
    "$PYTHON" -u run_shared_alignment.py \
      --model vjepa2_pretrained \
      --brain-path "$BRAIN" \
      --output-dir "$DATA_OUT/shared_alignment_confirm" \
      --n-perm "${CCN_N_PERM:-1000}" \
      --n-pc 100 \
      --n-test-pcs 20
    ;;

  geometry)
    require_brain
    cd "$CODE/content_affect_partition"
    "$PYTHON" -u run_content_affect_partition.py \
      --brain-path "$BRAIN" \
      --geometry-only \
      --output-dir "$RESULT_OUT/content_affect_geometry"
    ;;

  cortical)
    require_brain
    SHARED_RANK="${2:-3}"
    cd "$CODE/cortical_transformation"
    "$PYTHON" -u run_cortical_transformation.py \
      --brain-path "$BRAIN" \
      --output-dir "$RESULT_OUT/cortical_transformation" \
      --shared-rank "$SHARED_RANK" \
      --n-pca 100 \
      --max-rank 20 \
      --n-folds 5 \
      --n-shuffles "${CCN_N_SHUFFLES:-100}"
    ;;

  content)
    require_brain
    cd "$CODE/content_affect_partition"
    "$PYTHON" -u run_content_affect_partition.py \
      --brain-path "$BRAIN" \
      --output-dir "$RESULT_OUT/content_affect_partition"
    ;;

  *)
    usage
    exit 2
    ;;
esac

echo "Corrected CCN stage complete: $STAGE"
