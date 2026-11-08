#!/bin/bash
# 캡션 변형 특징을 만들고(변형당 CPU 약 7분), 그 특징만 쓴 teacher 로 선형 pilot 을 피험자 5명 병렬로. bash 로 실행.
# 인자: 변형 이름들 (scrambled bow animals food people affiliation harm sexual sports nature bodily random1 random2)
# bash /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/features/caption_variants.sh scrambled bow animals food
set -euo pipefail
F=/pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/features
P=/pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 OMP_NUM_THREADS=16 MKL_NUM_THREADS=16 PYTHONDONTWRITEBYTECODE=1
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python $F/build_caption_variants.py --bundle /pscratch/sd/s/sjmoon/transfer/emobrain_stimulus_features_20261025 \
  --out /pscratch/sd/s/sjmoon/transfer/emobrain_lab_features_20261026 --device cpu --only "$(IFS=,; echo "$*")"
names=()
for v in "$@"; do
  case $v in
    scrambled) names+=(caption_human_scrambled_mpnet) ;;
    bow) names+=(caption_bow_tfidf) ;;
    random*) names+=(caption_minus_${v}_mpnet) ;;
    *) names+=(caption_minus_${v}_mpnet) ;;
  esac
done
bash $P/teacher_controls.sh "${names[@]}"
