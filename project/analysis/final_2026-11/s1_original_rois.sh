#!/bin/bash
# S1: 공개 자료(HK figshare 11988351, MC figshare 25808179)에서 참가자별 ROI를 읽어 우리 격자로 옮기고 큰 파일은 지운다.
# HK는 참가자마다 Session1 h5(약 2 GB)만 받아 읽는다. MC는 testPerception mat(약 200 MB). 통신 위주, login node 약 20분.
# 세션과 분리해 실행: setsid nohup bash /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11/s1_original_rois.sh > /pscratch/sd/s/sjmoon/EmoBrain/project/output/final_2026-11/logs/s1_original_rois.log 2>&1 &
set -uo pipefail
PY=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11/s1_original_rois.py
HKD=/pscratch/sd/s/sjmoon/atlas_sources/horikawa2020_figshare
MCD=/pscratch/sd/s/sjmoon/atlas_sources/mindcaptioning_figshare
export PYTHONDONTWRITEBYTECODE=1
url() { curl -s -m 60 "https://api.figshare.com/v2/articles/$1" | "$PY" -I -c "import sys,json;print([f['download_url'] for f in json.load(sys.stdin)['files'] if f['name']=='$2'][0])"; }
for n in 1 2 3 4 5; do
  s=0$n; H5="$HKD/data/fmri/Subject$n/preprocessed/fmri_Subject${n}_Session1.h5"
  if [ ! -f "$HKD/done_sub-$s" ]; then
    [ -f "$H5" ] || (cd "$HKD" && curl -sL --max-time 1800 "$(url 11988351 Subject${n}_preprocessed_fmri.tar.gz)" | tar -xz --wildcards --occurrence=1 '*Session1.h5')
    "$PY" "$CODE" --cohort hk --sub "$s" --path "$H5" && rm -f "$H5" && touch "$HKD/done_sub-$s"
  fi
done
rm -rf "$HKD/data"
for n in 1 2 3 4 5 6; do
  s=0$n; M="$MCD/testPerception_S$n.mat"
  if [ ! -f "$MCD/done_sub-$s" ]; then
    [ -f "$M" ] || curl -sL --max-time 900 -o "$M" "$(url 25808179 testPerception_S$n.mat)"
    "$PY" "$CODE" --cohort mc --sub "$s" --path "$M" && rm -f "$M" && touch "$MCD/done_sub-$s"
  fi
done
"$PY" "$CODE" --summary
date > /pscratch/sd/s/sjmoon/EmoBrain/project/output/final_2026-11/s1_original_rois/DONE
