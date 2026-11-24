#!/bin/bash
#SBATCH --account=m5187
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:05:00
#SBATCH --job-name=emobrain_brain_decoding_summary
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoBrain/project/baseline/brain_decoding/runs/logs/%x-%j.log
# Re-summarize an existing run without refitting (run.sh already calls this).
# Usage: bash /pscratch/sd/s/sjmoon/EmoBrain/project/baseline/brain_decoding/summarize.sh EXPERIMENT_ID
set -euo pipefail
/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python \
    /pscratch/sd/s/sjmoon/EmoBrain/project/baseline/brain_decoding/summarize.py "$@"
