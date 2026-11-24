#!/bin/bash
# S1: 공개 자료(HK figshare 11988351, MC figshare 25808179)에서 참가자별 ROI를 읽어 우리 격자로 옮기고 큰 파일은 지운다.
# HK는 참가자마다 Session1 h5(약 2 GB)만 받아 읽는다. MC는 testPerception mat(약 200 MB). 통신 위주, login node 약 20분.
# 코드나 QC mask가 바뀌면 완료 표시가 맞지 않아 그 참가자를 다시 읽는다. 어느 단계든 실패하면 멈추고 DONE을 쓰지 않는다.
# 세션과 분리해 실행: setsid nohup bash $ROOT/scripts/s1_original_rois.sh > $OUT_ROOT/logs/s1_original_rois.log 2>&1 &
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
PY="$PY_CPU"
CODE=s1_original_rois.py
HKD=$DATA_ROOT/atlas_sources/horikawa2020_figshare
MCD=$DATA_ROOT/atlas_sources/mindcaptioning_figshare
DONE=$OUT_ROOT/s1_original_rois/DONE
export PYTHONDONTWRITEBYTECODE=1
rm -f "$DONE"
url() { curl -sS -m 60 "https://api.figshare.com/v2/articles/$1" | "$PY" -I -c "import sys,json;print([f['download_url'] for f in json.load(sys.stdin)['files'] if f['name']=='$2'][0])"; }
sig() { cat "$CODE" "$1" | sha256sum | cut -d' ' -f1; }
for n in 1 2 3 4 5; do
  s=0$n; H5="$HKD/data/fmri/Subject$n/preprocessed/fmri_Subject${n}_Session1.h5"; MASK=$DATA_ROOT/Horikawa/sub-$s/v3_qc/sub-${s}_mask_qc.nii.gz
  if [ "$(cat "$HKD/done_sub-$s" 2>/dev/null || true)" != "$(sig "$MASK")" ]; then
    # tar가 첫 h5를 찾으면 끝내므로 curl은 SIGPIPE로 끝난다. 그래서 파이프 종료 코드 대신 파일이 있는지 본다.
    [ -f "$H5" ] || (cd "$HKD" && curl -sSL --max-time 1800 "$(url 11988351 Subject${n}_preprocessed_fmri.tar.gz)" | tar -xz --wildcards --occurrence=1 '*Session1.h5') || true
    [ -f "$H5" ]
    "$PY" "$CODE" --cohort hk --sub "$s" --path "$H5"
    rm -f "$H5"; sig "$MASK" > "$HKD/done_sub-$s"
  fi
done
rm -rf "$HKD/data"
for n in 1 2 3 4 5 6; do
  s=0$n; M="$MCD/testPerception_S$n.mat"; MASK=$DATA_ROOT/MindCaptioning/sub-$s/v2_qc/sub-${s}_mask_qc.nii.gz
  if [ "$(cat "$MCD/done_sub-$s" 2>/dev/null || true)" != "$(sig "$MASK")" ]; then
    [ -f "$M" ] || curl -sSL --fail --max-time 900 -o "$M" "$(url 25808179 testPerception_S$n.mat)"
    "$PY" "$CODE" --cohort mc --sub "$s" --path "$M"
    rm -f "$M"; sig "$MASK" > "$MCD/done_sub-$s"
  fi
done
"$PY" "$CODE" --sources
"$PY" "$CODE" --summary
date > "$DONE"
