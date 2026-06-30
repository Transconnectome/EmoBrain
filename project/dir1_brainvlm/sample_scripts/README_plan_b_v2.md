# Plan B v2. Qwen3-VL family 3 size × VA binary + VA regression

작성 2026-06-24. v1 (Qwen3-VL 2B + lr 5e-4 + epoch 50) 의 VA binary 박살 (best acc 0.597 vs Phase 1 ROI ridge baseline balAcc 0.720) 의 회복 plan.

32B 는 사용자 결정 으로 제외 (cost / OOM risk).

## v1 → v2 의 변경

- **lr** 5e-4 → **1e-4** (1/5). v1 의 epoch 6 peak 후 collapse 의 overfit 회피.
- **epoch** 50 → **10** + best ckpt 자동 selection.
- **warmup** 25 → 50.
- **logging_steps** 20 → 50.
- **eval_steps** 100 → 500 (이미 v1 의 후반 에 조정).
- **backbone** 3 size 비교 (2B / 4B / 8B).
- **ICL** 3-round 유지 (data 재생성 회피).

## 파일 list

### yaml (6 개)

```
project/config/
  umbrella_Qwen3VL2B_train_Horikawa_Emotion_ROI_VA_binary_v2.yaml
  umbrella_Qwen3VL2B_train_Horikawa_Emotion_ROI_VA_regression_v2.yaml
  umbrella_Qwen3VL4B_train_Horikawa_Emotion_ROI_VA_binary_v2.yaml
  umbrella_Qwen3VL4B_train_Horikawa_Emotion_ROI_VA_regression_v2.yaml
  umbrella_Qwen3VL8B_train_Horikawa_Emotion_ROI_VA_binary_v2.yaml
  umbrella_Qwen3VL8B_train_Horikawa_Emotion_ROI_VA_regression_v2.yaml
```

### sh launcher (6 task sh + 3 model RUN sh)

**모델 별 통합 launcher (권장. 한 모델 = 한 sh)**

```
sample_scripts/
  RUN_Qwen3VL2B_v2.sh    ← 2B 의 binary + regression sequential
  RUN_Qwen3VL4B_v2.sh    ← 4B 의 binary + regression sequential
  RUN_Qwen3VL8B_v2.sh    ← 8B 의 binary + regression sequential
```

**Task 별 sh (RUN 의 internal building block. task 별 launch 필요 시)**

```
sample_scripts/
  UMBRELLA_ROI_Horikawa_Emotion_VA_binary_Qwen3VL2B_v2.sh
  UMBRELLA_ROI_Horikawa_Emotion_VA_regression_Qwen3VL2B_v2.sh
  UMBRELLA_ROI_Horikawa_Emotion_VA_binary_Qwen3VL4B_v2.sh
  UMBRELLA_ROI_Horikawa_Emotion_VA_regression_Qwen3VL4B_v2.sh
  UMBRELLA_ROI_Horikawa_Emotion_VA_binary_Qwen3VL8B_v2.sh
  UMBRELLA_ROI_Horikawa_Emotion_VA_regression_Qwen3VL8B_v2.sh
```

모든 sh 에 `chmod +x` 적용 됨.

## Launch (NERSC. login 노드 = GPU 없음. sbatch 필수)

### 권장 (모델 별 sbatch wrapper)

```bash
# 3 모델 모두 동시 submit. 각자 다른 compute 노드 의 GPU 1 개.
sbatch /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/sample_scripts/sbatch_Qwen3VL2B_v2.sh
sbatch /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/sample_scripts/sbatch_Qwen3VL4B_v2.sh
sbatch /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/sample_scripts/sbatch_Qwen3VL8B_v2.sh
```

각 sbatch wrapper 의 SLURM directive.
- `-A m4641` (NERSC account).
- `-C gpu` (A100).
- `-q regular`.
- `-N 1` + `--gpus-per-node=1`.
- `-t 16:00:00` (2B), `24:00:00` (4B), `36:00:00` (8B).

queue status 확인.
```bash
squeue --me
sacct -j <jobid> --format=JobID,JobName,State,Elapsed,MaxRSS
```

### salloc + bash (interactive 디버깅 용)

```bash
salloc -A m4641 -C gpu -q interactive -N 1 --gpus-per-node=1 -t 2:00:00
# allocate 받으면.
bash /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/sample_scripts/RUN_Qwen3VL2B_v2.sh
```

### Task 별 launch (필요 시, sbatch 안 거치고)

salloc 또는 sbatch 후.

```bash
# Qwen3-VL-2B-Instruct VA binary 만
bash /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/sample_scripts/UMBRELLA_ROI_Horikawa_Emotion_VA_binary_Qwen3VL2B_v2.sh

# Qwen3-VL-4B-Instruct VA regression 만
bash /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/sample_scripts/UMBRELLA_ROI_Horikawa_Emotion_VA_regression_Qwen3VL4B_v2.sh
```

### 주의. login 노드 에서 bash 직접 = GPU 없음 으로 stuck

`torchrun --nproc_per_node=1` 가 GPU 못 찾아서 학습 안 시작. 반드시 compute 노드 (sbatch / salloc) 에서.

### NERSC sbatch wrapper (필요 시)

각 sh 를 SLURM submission script 로 wrap. 예시.

```bash
#!/bin/bash
#SBATCH -A m4641
#SBATCH -C gpu
#SBATCH -q regular
#SBATCH -N 1
#SBATCH --gpus-per-node=1               # 32B 는 --gpus-per-node=4
#SBATCH -t 12:00:00                     # 2B/4B = 6 hr, 8B = 10 hr, 32B = 24 hr
#SBATCH -J vlm_v2
#SBATCH -o /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/logs/%x_%j.out
#SBATCH -e /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/logs/%x_%j.err

bash /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/sample_scripts/UMBRELLA_ROI_Horikawa_Emotion_VA_binary_Qwen3VL2B_v2.sh
```

## 예상 cost (A100 80GB 기준)

| Backbone | batch × accum | per epoch | 10 epoch 시간 | task 2 개 |
|---|---|---|---|---|
| Qwen3-VL-2B | 4 × 16 (64) | ~30-40 min | 5-7 hr | 10-14 hr |
| Qwen3-VL-4B | 2 × 32 (64) | ~50-60 min | 8-10 hr | 16-20 hr |
| Qwen3-VL-8B | 2 × 32 (64) | ~80-100 min | 14-17 hr | 28-34 hr |

총 3 backbone × 2 task = 약 **55-70 GPU hour** (single GPU 환산).

병렬 launch 가능 (각자 별도 GPU). 3 모델 동시 launch 시 wall-clock = 가장 느린 8B 의 ~30 hr ≈ 하루 + 6 hr.

## Output

| Backbone × Task | ckpt 위치 | eval 위치 |
|---|---|---|
| Qwen3VL2B × VA binary | output/horikawa_emotion_va_binary_Qwen3VL2B_v2/ | output/horikawa_emotion_va_binary_Qwen3VL2B_v2_eval/ |
| Qwen3VL2B × VA regression | output/horikawa_emotion_va_regression_Qwen3VL2B_v2/ | output/horikawa_emotion_va_regression_Qwen3VL2B_v2_eval/ |
| Qwen3VL4B × VA binary | output/horikawa_emotion_va_binary_Qwen3VL4B_v2/ | ... |
| Qwen3VL4B × VA regression | output/horikawa_emotion_va_regression_Qwen3VL4B_v2/ | ... |
| Qwen3VL8B × VA binary | output/horikawa_emotion_va_binary_Qwen3VL8B_v2/ | ... |
| Qwen3VL8B × VA regression | output/horikawa_emotion_va_regression_Qwen3VL8B_v2/ | ... |
| Qwen3VL32B × VA binary | output/horikawa_emotion_va_binary_Qwen3VL32B_v2/ | ... |
| Qwen3VL32B × VA regression | output/horikawa_emotion_va_regression_Qwen3VL32B_v2/ | ... |

## 평가 target (반복)

| Task | Phase 1 ROI ridge baseline | 우리 target |
|---|---|---|
| V binary (Q1 vs Q4) | **balAcc 0.720, AUROC 0.789** | balAcc ≥ 0.72 |
| V regression | **Pearson r 0.416** | r ≥ 0.40 |
| A binary | balAcc 0.638, AUROC 0.678 | balAcc ≥ 0.64 |
| A regression | Pearson r 0.233 | r ≥ 0.23 |

## Risk + Warning

- **32B OOM risk.** A100 80GB single 으로 batch 1 불가능 할 수 있음. multi-GPU (NUM_GPUS=4 또는 8) 권장. 또는 DeepSpeed ZeRO-3 의 sharding 설정 필요.
- **Monkey patch 호환.** 모든 backbone 이 `transformers.models.qwen3_vl.modeling_qwen3_vl` 의 동일 class 사용 (같은 family) → drop-in 호환.
- **자동 resume.** 모든 sh 에 LATEST_CKPT 의 자동 detect 박혀 있음. 중단 후 같은 sh 다시 실행 하면 자동 resume.
- **wandb API key.** yaml 의 `wandb.API_KEY` 의 placeholder 를 본인 key 로 교체 하거나, sh 에 `--no-wandb` 플래그 추가.
- **HF download.** 첫 launch 시 backbone ckpt 자동 download. HF_HOME = `/pscratch/sd/s/sjmoon/huggingface`.

## v2 학습 후 의 다음 step

1. 4 backbone 의 best ckpt 의 eval 결과 수집.
2. baseline target 과 비교. *어느 backbone size* 가 baseline 이기거나 비슷.
3. baseline 이긴 backbone 의 setup 으로 Cat34 4 stage 학습 launch.
4. baseline 못 넘 으면 다음 옵션 결정. Plan C (token output 폐기 + regression head 직접 attach), Stage B (다른 family backbone), D2 fMRI-LM 우선.

---

상세 spine + rationale = `Paper/framework_EN.md` + `Paper/framework_KR.md` 의 §Status + §Sub-claims.
Decision log = `docs/notes/project_decisions.md` 의 2026-06-24 entry.
