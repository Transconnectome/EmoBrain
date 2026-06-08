# `project/dir2_multimodal/code/` (Direction 2)

EmoBrain 의 Direction 2 (Multimodal Alignment) main scope. 자세한 계획은 [`ACTION_PLAN.md`](../../ACTION_PLAN.md) Direction 2 의 Action 2.1 ~ 2.3.

## Goal

Brain encoder (Brain-JEPA frozen 또는 학습 가능 BFM) + V-JEPA2 video feature 의 contrastive alignment. Brain unique variance = Joint − Video-only 정량화.

## 예정 파일 (신규)

| 파일 | 역할 |
|------|------|
| `train_align.py` | InfoNCE symmetric contrastive loss main entry |
| `projection_head.py` | Brain (768 / 450) + Video (1408) → 공통 512-dim space MLP |
| `variance_partition.py` | Joint / Video-only / Brain-only 의 paired bootstrap |
| `eval_emotion.py` | V/A regression + Cat34 multilabel 평가 |
| `wrappers/*.sh` | SLURM (`m4641` gpu / cpu queue) |

## `legacy_phase2/`

v4 framing 의 Brain+Video framework 코드. Direction 2 의 재활용 base.
- Architecture A / B / C / D 의 4 가지 brain-video fusion variant.
- `train_contrastive.py`, `train_supervised.py`, `probe_contrastive.py`, `encoding_brain_to_video.py`, `subject_variability.py` 등.
- 신규 train_align 작성 시 reference 로 활용.

## 환경

`/pscratch/sd/s/sjmoon/tribev2/.venv` (Direction 2 는 brainvlm_qwen_env 와 별개).

## 결과 저장

`project/shared/results/multimodal/`.
