#!/bin/bash
# S1: 피질하 10개를 PickAtlas에서 11명 모두 새로 만들어 저자 공개 mask, aseg와 비교한다 (04 정할 것 5, 7). 뇌 반응은 읽지 않는다.
# PickAtlas의 MNI_T1.nii를 T1w에 ANTs로 직접 등록한다. 3명씩 병렬, 참가자당 8 thread, 약 12분. CPU, login node.
# 어느 단계든 실패하면 멈추고 DONE을 쓰지 않는다.
# 세션과 분리해 실행: setsid nohup bash $ROOT/scripts/s1_subcortex_rebuild.sh > $OUT_ROOT/logs/s1_subcortex_rebuild.log 2>&1 &
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
PY="$PY_CPU"
CODE=s1_subcortex_rebuild.py
SELF=$ROOT/scripts/s1_subcortex_rebuild.sh
WORK=$OUT_ROOT/s1_subcortex_rebuild
ATLAS=$DATA_ROOT/atlas_sources/wfu_pickatlas/official/WFU_PickAtlas_3.0.5b/wfu_pickatlas/MNI_atlas_templates
IMG=docker:nipreps/fmriprep:25.0.0
export PYTHONDONTWRITEBYTECODE=1
mkdir -p "$WORK"

one() {
  c=$1; s=$2; tag=${c}_sub-$s
  if [ "$c" = hk ]; then
    T1=$DATA_ROOT/Horikawa/fmriprep/horikawa_preprocess_sub$s/fmriprep/output/sub-$s/ses-anatomy/anat/sub-${s}_ses-anatomy_desc-preproc_T1w.nii.gz
    REF=$DATA_ROOT/Horikawa/sub-$s/v3_qc/sub-${s}_mask_qc.nii.gz
  else
    T1=$DATA_ROOT/MindCaptioning/fmriprep/sub-$s/output/sub-$s/ses-anat/anat/sub-${s}_ses-anat_desc-preproc_T1w.nii.gz
    REF=$DATA_ROOT/MindCaptioning/sub-$s/v2_qc/sub-${s}_mask_qc.nii.gz
  fi
  [ -f "$T1" ] && [ -f "$REF" ]
  P=$WORK/${tag}_
  if [ ! -f "${P}1Warp.nii.gz" ]; then
    shifter --image=$IMG antsRegistrationSyNQuick.sh -d 3 -f "$T1" -m "$ATLAS/MNI_T1.nii" -o "$P" -t s -n 8 > "${P}registration.log" 2>&1
  fi
  for f in aal_MNI_V4 TD_brodmann TD_hemisphere TD_label; do
    shifter --image=$IMG antsApplyTransforms -d 3 -i "$ATLAS/$f.nii" -r "$REF" -t "${P}1Warp.nii.gz" -t "${P}0GenericAffine.mat" -n NearestNeighbor -o "${P}${f}_nn2mm.nii.gz" > /dev/null
    shifter --image=$IMG antsApplyTransforms -d 3 -i "$ATLAS/$f.nii" -r "$T1" -t "${P}1Warp.nii.gz" -t "${P}0GenericAffine.mat" -n NearestNeighbor -o "${P}${f}_t1w.nii.gz" > /dev/null
  done
  "$PY" "$CODE" --cohort "$c" --sub "$s"
  rm -f "${P}"*_t1w.nii.gz "${P}"*_nn2mm.nii.gz "${P}Warped.nii.gz" "${P}InverseWarped.nii.gz"
}

if [ "${1:-}" = one ]; then
  one "$2" "$3"
  exit 0
fi

rm -f "$WORK/DONE"
printf '%s\n' "hk 03" "hk 01" "hk 02" "hk 04" "hk 05" "mc 01" "mc 02" "mc 03" "mc 04" "mc 05" "mc 06" | xargs -P 3 -L 1 bash "$SELF" one
"$PY" "$CODE" --summary
date > "$WORK/DONE"
