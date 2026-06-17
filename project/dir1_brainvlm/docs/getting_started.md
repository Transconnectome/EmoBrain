# D1 BrainVLM Getting Started

EmoBrain Direction 1. Qwen3-VL + Schaefer-450 ROI patchify + LoRA + multi-task heads.
Forward 설계는 `design.md`, repo-wide context 는 `/pscratch/sd/s/sjmoon/EmoBrain/CONTEXT_EMOBRAIN.md`.

## 0. TL;DR

```bash
# (one-time) env check
ls /pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python

# smoke test (login node, no GPU, ~2 min)
bash /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/scripts/smoke_test.sh

# pilot 학습 (사용자 사전 승인 후, A100 1 장, ~6 시간)
sbatch /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/scripts/train_pilot_path_a.sh
```

## 1. 환경

| 항목 | 경로 |
|------|------|
| Python env (LLM, Qwen3-VL) | `/pscratch/sd/s/sjmoon/brainvlm_qwen_env` |
| Python env (smoke, dataset only) | `/pscratch/sd/s/sjmoon/tribev2/.venv` |
| Reference 구현 (submodule) | `external/repos/BrainVLM/UMBRELLA_qwen/project/` |
| NERSC account | `m4641` |
| GPU queue | `regular -C gpu --gpus-per-node=1` (A100 80GB) |

`brainvlm_qwen_env` 의 실측 stack. torch 2.11.0+cu130, transformers 4.57.0, peft 0.19.2.dev0. Qwen3-VL 사용 시 transformers 가 Qwen3VL 지원 minor 이상이어야 한다 (4.57+ 확인 완료).

## 2. Repository 구조

```
project/dir1_brainvlm/
├── code/
│   ├── data/{patchify.py, dataset.py}   ROI 2D grid + BrainVQADataset
│   ├── model/brainvlm_path_a.py         Qwen3-VL bridge + V/A head + Cat34 head
│   ├── loss/multitask.py                CE + MSE + KL combination
│   ├── train/train_pilot.py             pilot entry (--smoke for skeleton run)
│   ├── eval/eval_emotion.py             V/A r, Cat34 multilabel/soft metrics
│   └── analysis/token_distribution.py   ABCD vs Horikawa KL (pretrained 도착 후)
├── scripts/
│   ├── smoke_test.sh                    login-node smoke
│   └── train_pilot_path_a.sh            SLURM gpu queue
├── docs/{design.md, getting_started.md}
├── data/, output/, results/             per-direction artifact (생성됨)
```

## 3. 입력 데이터

모두 `project/shared/data/` 아래. Phase 1 에서 이미 추출된 자원 재사용.

| 파일 | 의미 | 상태 |
|------|------|------|
| `horikawa_5fold.csv` | 5-fold stim-stratified split (per-stim subject 5 명) | 존재 |
| `roi_timeseries_schaefer400tian50/sub-XX_<stim>.npy` | (T, 450) ROI time series | **확인 필요**. 없으면 추출 필요 |
| `stimulus_features/qwen_vl_captions.jsonl` | per-stim Qwen-VL caption | **확인 필요** |
| `va_continuous_z.csv` | per-stim V/A z-score | **확인 필요** |
| `cat34_soft_distribution.csv` | per-stim 34-cat soft distribution | **확인 필요** |

위 파일 부재 시 `project/shared/code/probes/` 의 추출 wrapper 를 먼저 돌려야 한다.

## 4. Smoke test

목적. dataset → patchify → head → loss flow 검증. backbone load 안 함.

```bash
bash /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/scripts/smoke_test.sh
```

성공 기준.
- `[smoke] OK` 출력
- `output/smoke_<timestamp>/smoke_ckpt.pt` 저장
- `mse_va`, `kl_cat34` 가 step 에 따라 감소 (랜덤 head 라 절댓값은 의미 없음, 흐름만 확인)

실패 시. 대부분 입력 파일 부재. log 확인 후 `project/shared/data/` 부터 점검.

## 5. Pilot 학습 (A100)

```bash
# 사용자 사전 승인 후
sbatch /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/scripts/train_pilot_path_a.sh
```

현재 `train_pilot.py` 의 non-smoke path 는 `NotImplementedError`. Qwen3VL backbone 통합 후 활성화 (Action 1.2 의 multi-task head + LoRA 통합 단계). 통합 작업.

1. `BrainVLMPathA.attach_backbones(vision_tower, llm)` 에 `Qwen3VLForConditionalGeneration` 의 vision/LLM 주입.
2. `peft.get_peft_model` 로 LoRA 적용 (cfg.lora_target_modules).
3. forward 에서 image → vision_tower → projector → LLM 의 cross-attention 으로 통합.
4. caption CE 는 LLM 의 standard LM loss, V/A + Cat34 는 LLM 의 last hidden state 평균 풀링 후 head.

UMBRELLA_qwen 의 monkey-patch (`patch_embed_qwen_NoPool.PatchEmbedQwen`, `CustomNoPoolingTriPlanarMerger`) 가 참고 자료.

## 6. Evaluation

`code/eval/eval_emotion.py` 의 3 함수.

```python
from project.dir1_brainvlm.code.eval.eval_emotion import (
    va_regression_metrics, cat34_multilabel_metrics, cat34_soft_metrics,
)
```

비교 baseline 은 `project/shared/results/background/phase1/`.
Gate (Direction 1). V/A Pearson r 가 ROI baseline (V 0.40, A 0.23) 보다 **+0.03 이상** + paired bootstrap p < 0.05.

## 7. Known limitations + open items

- ABCD pretrained BrainVLM checkpoint 부재. Scratch 시작 또는 collaborator 로부터 확보 필요.
- Schaefer 2D grid (L1) 만 구현. L2 (cortical flatmap), L3 (ROI×time matrix) ablation 은 Action 1.1 가 끝난 후.
- Synthetic descriptor corpus (V/A + Cat34 → instruction template) 합성 스크립트는 별도 작업. 현재는 Qwen-VL caption 만 supervision.

## 8. 다음 단계 ordering

1. Smoke test PASS 확인.
2. ROI time series + caption + targets 파일 확인 (없으면 추출).
3. Qwen3-VL backbone 통합 (`train_pilot.py` 의 NotImplementedError 제거).
4. Tiny pilot (10 stim, 1 epoch) on GPU 로 multi-task forward + LoRA backprop 검증.
5. Fold 1 full pilot.
6. Evaluation + Phase 1 baseline 비교.

`ACTION_PLAN.md` 의 Action 1.1 ~ 1.3 가 위 단계의 ground-level 대응.
