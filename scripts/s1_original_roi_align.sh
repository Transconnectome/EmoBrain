#!/bin/bash
# S1: 원 논문 ROI의 해부학적 정렬(11명)과 Talairach Daemon 판 비교(HK 5명). s1_original_rois.sh 뒤에 실행 (CPU, login node 약 10분).
# 어느 단계든 실패하면 멈춘다. ANTs의 오류 출력은 로그에 남긴다.
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
PY="$PY_CPU"
CODE=s1_original_roi_align.py
TMP=$OUT_ROOT/s1_original_rois/td_warped
ATLAS=$DATA_ROOT/atlas_sources/wfu_pickatlas/official/WFU_PickAtlas_3.0.5b/wfu_pickatlas
export PYTHONDONTWRITEBYTECODE=1
"$PY" "$CODE" alignment
mkdir -p "$TMP"
for s in 01 02 03 04 05; do
  XF=$DATA_ROOT/Horikawa/fmriprep/horikawa_preprocess_sub$s/fmriprep/output/sub-$s/ses-anatomy/anat/sub-${s}_ses-anatomy_from-MNI152NLin2009cAsym_to-T1w_mode-image_xfm.h5
  REF=$DATA_ROOT/Horikawa/sub-$s/v3_qc/sub-${s}_mask_qc.nii.gz
  for v in MNI_atlas_templates TD-ICBM_MNI_atlas_templates; do
    for f in TD_brodmann TD_hemisphere TD_label; do
      shifter --image=docker:nipreps/fmriprep:25.0.0 antsApplyTransforms -d 3 -i "$ATLAS/$v/$f.nii" -r "$REF" -t "$XF" -n NearestNeighbor -o "$TMP/sub-${s}_${v}_$f.nii.gz" > /dev/null
    done
  done
done
"$PY" "$CODE" td "$TMP"
rm -rf "$TMP"
