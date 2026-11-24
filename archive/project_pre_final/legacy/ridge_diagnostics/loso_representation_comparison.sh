#!/bin/bash
# Cross-subject (LOSO) comparison of brain representations.
# Question: does a pretrained BFM transfer across subjects better than ROI mean,
# i.e. is there a reason to use a BFM that ridge on ROI mean cannot supply?
# CPU-only, read-only (writes one JSON report). No sbatch.
#
# Usage.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/loso_representation_comparison.sh
#   bash .../loso_representation_comparison.sh roi_schaefer400tian50_mean swift_NewE96_SL20_resting_pad-zero
#
# With no arguments every variant under project/shared/output/embeddings/ is run
# (35 representations, roughly 10-20 minutes).

set -euo pipefail

REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
VENV_ACTIVATE=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

source "${VENV_ACTIVATE}"
python3 "${REPO_ROOT}/project/scripts/loso_representation_comparison.py" "$@"
