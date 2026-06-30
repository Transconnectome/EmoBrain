#!/usr/bin/env bash
# Horikawa adapter launcher (D2 fMRI-LM).
#
# Usage:
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/dir2_fmri_lm/adapters/horikawa_RUN.sh
#
# Runs SMOKE first (2 subjects x 50 stimuli), then the full conversion if SMOKE
# returns 0. Output:
#   /pscratch/sd/s/sjmoon/EmoBrain/project/dir2_fmri_lm/data/horikawa_emotion/ROI_Schaefer400Tian50__SMOKE/
#   /pscratch/sd/s/sjmoon/EmoBrain/project/dir2_fmri_lm/data/horikawa_emotion/ROI_Schaefer400Tian50/

set -euo pipefail

REPO_ROOT="/pscratch/sd/s/sjmoon/EmoBrain"
ADAPTER_DIR="${REPO_ROOT}/project/dir2_fmri_lm/adapters"
OUT_ROOT="${REPO_ROOT}/project/dir2_fmri_lm/data/horikawa_emotion/ROI_Schaefer400Tian50"
LOG_DIR="${REPO_ROOT}/project/shared/output/logs/dir2_fmri_lm/adapter_horikawa"
mkdir -p "${LOG_DIR}"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
SMOKE_LOG="${LOG_DIR}/smoke_${TIMESTAMP}.log"
FULL_LOG="${LOG_DIR}/full_${TIMESTAMP}.log"

# ------------------------------------------------------------------
# Activate env. Prefer brainvlm_qwen_env if it has h5py, otherwise tribev2.
# (Empirically tribev2 has h5py + pandas + numpy; brainvlm_qwen_env does not
#  ship h5py by default. The probe below picks the right one at runtime.)
# ------------------------------------------------------------------

BRAINVLM_ENV="/pscratch/sd/s/sjmoon/brainvlm_qwen_env"
TRIBEV2_VENV="/pscratch/sd/s/sjmoon/tribev2/.venv"

probe_env() {
    local pybin="$1"
    "${pybin}" - <<'PY' >/dev/null 2>&1
import h5py, numpy, pandas  # noqa: F401
PY
}

if probe_env "${BRAINVLM_ENV}/bin/python"; then
    export PATH="${BRAINVLM_ENV}/bin:${PATH}"
    PYBIN="${BRAINVLM_ENV}/bin/python"
    echo "[env] using brainvlm_qwen_env"
elif probe_env "${TRIBEV2_VENV}/bin/python"; then
    # shellcheck disable=SC1090
    source "${TRIBEV2_VENV}/bin/activate"
    PYBIN="${TRIBEV2_VENV}/bin/python"
    echo "[env] using tribev2"
else
    echo "[env] FATAL: no env has h5py + numpy + pandas" >&2
    exit 1
fi

# Run as a module so relative imports work.
cd "${REPO_ROOT}"

# ------------------------------------------------------------------
# SMOKE
# ------------------------------------------------------------------
echo "[smoke] starting at $(date), log -> ${SMOKE_LOG}"
"${PYBIN}" -m project.dir2_fmri_lm.adapters.horikawa \
    --smoke \
    --out-dir "${OUT_ROOT}" \
    --norm robust \
    --t-fixed 16 \
    --cat-threshold 0.10 \
    --log-level INFO \
    2>&1 | tee "${SMOKE_LOG}"

SMOKE_STATUS=${PIPESTATUS[0]}
if [[ "${SMOKE_STATUS}" -ne 0 ]]; then
    echo "[smoke] FAILED (exit ${SMOKE_STATUS}). Aborting before full run." >&2
    exit "${SMOKE_STATUS}"
fi
echo "[smoke] OK"

# ------------------------------------------------------------------
# FULL
# ------------------------------------------------------------------
echo "[full] starting at $(date), log -> ${FULL_LOG}"
"${PYBIN}" -m project.dir2_fmri_lm.adapters.horikawa \
    --out-dir "${OUT_ROOT}" \
    --norm robust \
    --t-fixed 16 \
    --cat-threshold 0.10 \
    --log-level INFO \
    2>&1 | tee "${FULL_LOG}"

FULL_STATUS=${PIPESTATUS[0]}
if [[ "${FULL_STATUS}" -ne 0 ]]; then
    echo "[full] FAILED (exit ${FULL_STATUS})." >&2
    exit "${FULL_STATUS}"
fi

echo
echo "[done] Horikawa D2 adapter complete."
echo "  smoke log: ${SMOKE_LOG}"
echo "  full  log: ${FULL_LOG}"
echo "  output  : ${OUT_ROOT}/"
