# EmoBrain. Framework (KR)

(Branch `sj_NEW_20260608_perlmutter` 의 EmoBrain framing 으로 재작성. 이전 v4 framework 는 `archive/v4_20260602/Paper/framework_KR.md`.)

## 제목 (working)

EmoBrain. Vision-Language Model 과 Brain-Video Multimodal 정렬에 기반한 active emotion brain decoding.

## Big question

Brain 에서 mixed / complex emotion 의 구조를 효과적으로 잡기 위한 model 과 task design 은 무엇인가? 구체적으로, frozen brain foundation model 의 한계를 active fine-tune + multimodal alignment 로 어떻게 보완할 수 있는가?

## Motivation

세 근거가 본 framework 를 active brain VLM + multimodal direction 으로 이끈다.

1. **Frozen BFM 의 한계가 측정으로 확정됨**. 본 프로젝트의 Phase 1 (`docs/reports/phase1_audit_20260604/`) 에서 Brain-JEPA, NeuroSTORM, SwiFT 6 종의 frozen embedding 위의 linear / MLP probe 가 단순 ROI mean BOLD + Ridge / Logistic regression baseline 을 V/A binary, V/A regression, Cat34 multilabel, Cat34 soft distribution 4 task 에서 모두 넘지 못함. 원인은 Horikawa 자극의 짧은 시계열 (T 중앙값 5 TR) 과 BFM 입력의 평균 63 ~ 70% zero padding.
2. **VLM / LLM 기반 brain decoding 의 부상**. MindLLM, UMBRAE, Mind Captioning, MedBLIP, BLIP-2, LLaVA 등이 frozen LLM / VLM 을 prior 로 활용하고 brain-side adapter 만 학습하는 paradigm 으로 brain-to-text / brain-to-image SOTA 를 달성.
3. **Multimodal brain alignment 의 standard 정립**. TRIBE (Algonauts 2025 1 위), VIBE, Multi-modal brain encoding, CineBrain, Doerig, BraVL 등이 brain unique contribution 을 video baseline 위에서 variance partitioning 으로 정량화하는 framework 를 확립.

EmoBrain 은 이 두 흐름을 emotion specific 한 두 axis 로 통합한다.

## Two Axes

### Direction 1. BrainVLM

fMRI 를 vision-language model 의 새 vision modality 로 통합. Qwen3-VL backbone + fMRI patchifier + 2D ROI-based brain representation + LoRA fine-tune + emotion VQA / caption / V/A score / Cat34 distribution 의 자연어와 numeric multi-task 출력.

### Direction 2. Brain-Video Multimodal

Brain encoder + V-JEPA2 video feature 의 공통 embedding space contrastive alignment + variance partitioning 으로 brain unique contribution 의 정량화. Subject-invariant 학습 옵션.

두 axis 는 complementary. BrainVLM 이 generative / multi-task 측면, Multimodal 이 정량적 contribution 측면. BFM 은 main task 가 아니지만 Direction 2 의 brain encoder 후보로 활용 가능.

## Sub-claims (falsifiable)

- **SC1**. BrainVLM 의 V/A Pearson r 와 Cat34 macro AUROC 가 Phase 1 의 best ROI baseline 보다 의미있게 높다.
- **SC2**. Brain-video joint 가 video-only baseline 위로 +0.05 이상 Pearson r 향상 + paired bootstrap p < 0.05.
- **SC3**. 두 axis 가 Cat34 soft distribution + mixed valence 3-way 에서 BFM frozen 보다 의미있게 높다.
- **Null**. 위 효과가 noise 수준 → negative result 도 publishable.

## Tasks

| Task | Phase 1 측정 | EmoBrain 평가 대상 |
|------|---------------|---------------------|
| V/A Binary | 완료 | Direction 1 + 2 |
| V/A Regression | 완료 | Direction 1 + 2 |
| Cat34 Multilabel (threshold 0.10) | 재측정 진행 중 | Direction 1 + 2 |
| Cat34 Soft Distribution | 재측정 진행 중 | Direction 1 + 2 |
| Mixed Valence (Vaccaro 2024) | 미측정 | Direction 1 + 2 |
| Caption Embedding Regression | 미측정 | Direction 1 specific |
| Emotion VQA | 미측정 | Direction 1 specific |

## Datasets

- Horikawa naturalistic video fMRI (main). 5 subj × 2185 stim. Cowen 34-cat + 14-dim + V/A.
- Cross-dataset (Phase 5). Emo-FilM, CineBrain, StudyForrest, NNDb, Affective Videos.

## Reference

영문 framework `Paper/framework_EN.md` 의 reference list 참조. 주요 reference 동일.
