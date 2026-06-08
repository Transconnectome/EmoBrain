# EmoBrain

**Vision-Language Model + Brain-Video Multimodal 정렬에 기반한 active emotion brain decoding.**

(Internal / repo name = EmoBrain. Branch `sj_NEW_20260608_perlmutter` 의 새 framing.)

## 한 줄 요약

Naturalistic video fMRI 에서 emotion 표상을 학습하기 위해 두 axis 를 함께 진행한다. (1) **BrainVLM** axis 가 fMRI 를 VLM / LLM 의 token 으로 주입해 emotion VQA / caption / V/A score 를 자연어로 multi-task 출력한다. (2) **Brain-Video Multimodal** axis 가 brain encoder 와 video encoder 의 contrastive alignment 로 brain 이 video baseline 위에 추가하는 unique emotion variance 를 정량화한다.

## Motivation

지금 방향이 active brain VLM / multimodal 로 정리된 근거.

- **Frozen brain foundation model (BFM) 의 한계**. 본 프로젝트 Phase 1 측정에서 frozen BFM (Brain-JEPA, NeuroSTORM, SwiFT 6 종) 의 모든 emotion task (V/A binary, V/A regression, Cat34 multilabel, Cat34 soft) 가 단순 ROI mean BOLD + Ridge regression baseline 을 넘지 못함. 상세는 `reports/phase1_audit_20260604/` 참조.
- **VLM / LLM 기반 brain decoding 의 부상**. MindLLM (2025), UMBRAE (ECCV 2024), Mind Captioning (Horikawa, Science Advances 2025) 등이 BFM 의 frozen embedding 단독 결과보다 일관되게 우수.
- **Multimodal brain alignment 의 성숙**. TRIBE (Meta FAIR, Algonauts 2025 1 위), Doerig 2024, CineBrain 등이 brain unique contribution 을 video baseline 위에서 정량화하는 framework 를 확립.

## Two Axes

| Axis | 핵심 아이디어 | 주요 reference |
|------|----------------|----------------|
| **Direction 1. BrainVLM** | VLM (Qwen3-VL) 의 fMRI patchifier 로 brain volume 을 token 화, LoRA fine-tune, emotion 의 multi-task 자연어 출력 | MindLLM, UMBRAE, Mind Captioning, MedBLIP, BLIP-2, LLaVA |
| **Direction 2. Brain-Video Multimodal** | Brain encoder + Video encoder contrastive alignment, brain unique variance 정량화 | TRIBE, VIBE, CineBrain, Doerig, BraVL |

BFM 은 Direction 1 의 vision modality 후보가 아니지만 Direction 2 의 brain encoder 로 활용 가능.

## Tasks

| Task | 설명 |
|------|------|
| V/A Binary | Q1 vs Q4 quartile |
| V/A Regression | Continuous score 예측 |
| Cat34 Multilabel | 자극당 34 emotion 의 0/1 vector, threshold 0.10 |
| Cat34 Soft Distribution | 자극당 34 차원 distribution |
| Mixed Valence | Positive / Negative / Mixed, Vaccaro 2024 |
| Caption Embedding Regression | Brain → caption embedding |
| Emotion VQA | "이 brain state 의 emotion 은?" 자연어 응답 |

## Status (2026-06-08)

Background benchmark (Phase 1 frozen BFM 측정 + Cat34 threshold 0.10 재측정 + audit) 모두 완료. 다음 step 은 Direction 1 BrainVLM pilot + Direction 2 Multimodal Alignment pilot 의 병행 launch (Hackathon 5 일).

자세한 forward plan 은 `docs/masterplan_v3_emobrain.md` 와 `ACTION_PLAN.md` 참조.
