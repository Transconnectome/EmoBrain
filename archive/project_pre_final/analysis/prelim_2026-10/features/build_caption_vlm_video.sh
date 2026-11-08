#!/bin/bash
#SBATCH -A m5187_g -C gpu -q regular -N 1 --gpus-per-node=4 -t 06:00:00 -J caption_vlm_video
#SBATCH -o /pscratch/sd/s/sjmoon/EmoBrain/project/output/prelim_2026-10/logs/caption_vlm_video/slurm_%j.out
# 영상 입력 VLM 캡션 (build_caption_vlm_video.py). 단계:
#   bash build_caption_vlm_video.sh pilot   확인 목록 54개 (11_caption_qc/review_list.json). GPU 1장, 약 5~10분
#   bash build_caption_vlm_video.sh all     영상 2185개. GPUS 에 적은 GPU 마다 shard 하나 (GPU 1장이면 약 4~5시간). pilot 에서 끝낸 영상은 건너뜀
#   bash build_caption_vlm_video.sh merge   captions.json + mpnet 임베딩 (CPU)
# 모델: 기본 Qwen/Qwen2.5-VL-7B-Instruct (v1 과 같은 모델). MODEL=Qwen/Qwen3-VL-8B-Instruct 로 바꾸면 캐시에 없을 때 처음에 내려받는다 (약 17 GB).
# GPU: GPUS="0" 또는 GPUS="0,1,2,3" (기본: 보이는 GPU 전부).
# 여러 노드로 나누기 (로그인 노드는 GPU 1장): 노드마다 SHARD=0 NSHARDS=3, SHARD=1 NSHARDS=3, SHARD=2 NSHARDS=3 bash ... all
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/features/build_caption_vlm_video.py
FEAT=/pscratch/sd/s/sjmoon/transfer/emobrain_lab_features_20261026
BUNDLE=/pscratch/sd/s/sjmoon/transfer/emobrain_stimulus_features_20261025
VIDEOS=/pscratch/sd/s/sjmoon/EmoViS/data/raw/CowenEmotionVideos
REVIEW=/pscratch/sd/s/sjmoon/EmoBrain/project/output/prelim_2026-10/11_caption_qc/review_list.json
LOG=/pscratch/sd/s/sjmoon/EmoBrain/project/output/prelim_2026-10/logs/caption_vlm_video
MODEL=${MODEL:-Qwen/Qwen2.5-VL-7B-Instruct}
export HF_HOME=/pscratch/sd/s/sjmoon/.cache/huggingface
if [ -d "$HF_HOME/hub/models--${MODEL//\//--}" ]; then export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1; fi
mkdir -p "$LOG"; TAG=$(basename "$MODEL")
COMMON=(--model "$MODEL" --feat "$FEAT" --bundle "$BUNDLE" --videos "$VIDEOS")
case "${1:-}" in
  pilot|all)
    GPUS=${GPUS:-$(nvidia-smi --query-gpu=index --format=csv,noheader | paste -sd,)}
    IFS=, read -ra G <<< "$GPUS"
    if [ "$1" = pilot ]; then
      IDS=$("$PY" -c "import json; r=json.load(open('$REVIEW')); s=[]; [s.append(v) for k in ['gross','substitution_top','audit_random'] for v in r[k] if v not in s]; print(','.join(map(str,s)))")
      CUDA_VISIBLE_DEVICES=${G[0]} "$PY" "$CODE" generate "${COMMON[@]}" --ids "$IDS" 2>&1 | tee "$LOG/${TAG}_pilot.log"
    else
      if [ -n "${SHARD:-}" ]; then
        CUDA_VISIBLE_DEVICES=${G[0]} "$PY" "$CODE" generate "${COMMON[@]}" --shard "$SHARD" --nshards "$NSHARDS" > "$LOG/${TAG}_shard${SHARD}of${NSHARDS}.log" 2>&1 &
      else
        for k in "${!G[@]}"; do
          CUDA_VISIBLE_DEVICES=${G[$k]} "$PY" "$CODE" generate "${COMMON[@]}" --shard "$k" --nshards "${#G[@]}" > "$LOG/${TAG}_shard${k}of${#G[@]}.log" 2>&1 &
        done
      fi
      wait; echo "생성 끝. bash $0 merge 를 돌리면 된다."
    fi ;;
  merge)
    "$PY" "$CODE" merge "${COMMON[@]}" --device cpu 2>&1 | tee "$LOG/${TAG}_merge.log" ;;
  *) echo "사용: bash $0 pilot|all|merge"; exit 1 ;;
esac
