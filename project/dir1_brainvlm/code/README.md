# `project/dir1_brainvlm/code/` (Direction 1)

EmoBrain 의 Direction 1 (BrainVLM) main scope. 자세한 계획은 [`ACTION_PLAN.md`](../../ACTION_PLAN.md) Direction 1 의 Action 1.1 ~ 1.3.

## Goal

Qwen3-VL backbone (UMBRELLA_qwen ABCD-pretrained) 위에 Horikawa fMRI 를 token 으로 주입. LoRA fine-tune 으로 emotion VQA / V/A score / Cat34 distribution 의 multi-task 자연어 + numeric 출력.

## 예정 파일

| 파일 | 역할 |
|------|------|
| `load_brainvlm.py` | UMBRELLA_qwen ABCD-pretrained checkpoint loader |
| `fmri_patchify.py` | Horikawa 4D fMRI → 2D ROI-based representation → VLM token |
| `prompt_template.py` | Emotion VQA / V/A / Cat34 multi-task prompt 디자인 |
| `multitask_head.py` | V/A regression + Cat34 distribution 의 task-specific head |
| `train_pilot.py` | LoRA fine-tune main entry, fold 1 pilot |
| `eval_emotion.py` | Phase 1 ROI baseline 과 emotion task 비교 |
| `wrappers/*.sh` | SLURM (`m4641` gpu queue, A100 80GB) |

## 환경

`/pscratch/sd/s/sjmoon/brainvlm_qwen_env` 활성화 후 사용.

## 결과 저장

`results/brainvlm/`.
