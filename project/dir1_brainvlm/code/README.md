# D1 BrainVLM code

EmoBrain Direction 1. Path A (Qwen3-VL + linear projection + LoRA + multi-task heads).
자세한 계획은 [`ACTION_PLAN.md`](../../../ACTION_PLAN.md) Direction 1 의 Action 1.1 ~ 1.3, 설계는 [`docs/design.md`](../docs/design.md), 사용법은 [`docs/getting_started.md`](../docs/getting_started.md).

## Subpackages

| Path | 책임 |
|------|------|
| `data/patchify.py` | (T, 450) ROI time series -> (3, 224, 224) 2D Schaefer grid image (L1 layout) |
| `data/dataset.py` | `BrainVQADataset`. fMRI image + V/A + Cat34 + caption + prompt |
| `model/brainvlm_path_a.py` | `BrainVLMPathA` wrapper. vision-to-LLM projector + V/A head + Cat34 head + LoRA hooks |
| `loss/multitask.py` | CE (caption) + MSE (V/A) + KL (Cat34 soft) combination |
| `train/train_pilot.py` | pilot entry. `--smoke` runs skeleton flow with synthetic batch (no backbone, no file I/O) |
| `eval/eval_emotion.py` | V/A regression, Cat34 multilabel (threshold 0.10), Cat34 soft metrics |
| `analysis/token_distribution.py` | ABCD vs Horikawa token KL divergence (placeholder until pretrained ckpt arrives) |

## Smoke test

```bash
bash /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/scripts/smoke_test.sh
```

Skeleton-only. backbone load 안 함, 실제 데이터 파일 부재 시에도 통과.

## 환경

`/pscratch/sd/s/sjmoon/brainvlm_qwen_env` (transformers 4.57.0, peft 0.19.2.dev0, torch 2.11.0) 활성화 후 backbone-integrated 학습. Skeleton smoke 는 `/pscratch/sd/s/sjmoon/tribev2/.venv` 에서 충분.

## 결과 저장

per-direction. `project/dir1_brainvlm/output/`, `project/dir1_brainvlm/results/`. shared 자원 (Phase 1 baseline, BFM embeddings 등) 은 `project/shared/`.
