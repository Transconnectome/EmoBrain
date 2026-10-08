#!/bin/bash
#SBATCH --account=m5187
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --cpus-per-task=4
#SBATCH --mem=12G
#SBATCH --time=00:30:00
#SBATCH --job-name=emobrain_brain_decoding
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoBrain/project/baseline/brain_decoding/runs/logs/%x-%j.log
# Brain-only decoding baseline (ridge vs training mean), one target per run.
# Usage (login node): bash /pscratch/sd/s/sjmoon/EmoBrain/project/baseline/brain_decoding/run.sh TARGET EXPERIMENT_ID [PARTICIPANT]
#   TARGET = cat34 | affect14; EXPERIMENT_ID must be new (runs are never overwritten);
#   PARTICIPANT defaults to config.json (mindcaptioning/sub-01), e.g. horikawa/sub-01.
#   AUDIT_DIR env var overrides the audit folder.
#   Outside SLURM it passes --login-node (4 BLAS threads, ~2-3 GB RAM, a few minutes);
#   the execution host is recorded in the run's metadata.json.
set -euo pipefail
if [[ $# -lt 2 || $# -gt 3 ]]; then
    echo "Expected TARGET EXPERIMENT_ID [PARTICIPANT]" >&2
    exit 2
fi
REPO=/pscratch/sd/s/sjmoon/EmoBrain
HERE=$REPO/project/baseline/brain_decoding
PY=/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python
TARGET=$1
EXP=$2
AUDIT=${AUDIT_DIR:-$REPO/project/output/audits/pilot_data/audit_20261008T072736Z}
mkdir -p "$HERE/runs/logs"
exec > >(tee -a "$HERE/runs/logs/$EXP.log") 2>&1
WHERE=()
[[ $# -eq 3 ]] && WHERE+=(--participant "$3")
[[ -z "${SLURM_JOB_ID:-}" ]] && WHERE+=(--login-node)
cd "$REPO"
export OPENBLAS_NUM_THREADS=4
export OMP_NUM_THREADS=4
"$PY" -m project.scripts.run_pilot \
    --audit-dir "$AUDIT" --target "$TARGET" \
    --config "$HERE/config.json" --output-root "$HERE/runs" \
    --codebook-contract "$HERE/codebook/$TARGET.json" --experiment-id "$EXP" \
    --execute "${WHERE[@]}"
"$PY" "$HERE/summarize.py" "$EXP"
