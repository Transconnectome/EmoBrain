#!/bin/bash
#SBATCH --account=m5187
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --cpus-per-task=4
#SBATCH --mem=12G
#SBATCH --time=00:30:00
#SBATCH --job-name=emobrain_brain_decoding
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoBrain/project/baseline/brain_decoding/runs/logs/%x-%j.log
# Brain-only decoding baseline (ridge vs training mean), one target per job.
# Usage: sbatch /pscratch/sd/s/sjmoon/EmoBrain/project/baseline/brain_decoding/run.sh TARGET EXPERIMENT_ID [AUDIT_DIR]
#   TARGET = cat34 | affect14; EXPERIMENT_ID must be new (runs are never overwritten).
set -euo pipefail
if [[ $# -lt 2 || $# -gt 3 ]]; then
    echo "Expected TARGET EXPERIMENT_ID [AUDIT_DIR]" >&2
    exit 2
fi
REPO=/pscratch/sd/s/sjmoon/EmoBrain
HERE=$REPO/project/baseline/brain_decoding
PY=/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python
TARGET=$1
EXP=$2
AUDIT=${3:-$REPO/project/output/audits/pilot_data/audit_20261008T044941Z}
cd "$REPO"
export OPENBLAS_NUM_THREADS=4
export OMP_NUM_THREADS=4
srun --cpu-bind=cores "$PY" -m project.scripts.run_pilot \
    --audit-dir "$AUDIT" --target "$TARGET" \
    --config "$HERE/config.json" --output-root "$HERE/runs" \
    --codebook-contract "$HERE/codebook/$TARGET.json" --experiment-id "$EXP" --execute
"$PY" "$HERE/summarize.py" "$EXP"
