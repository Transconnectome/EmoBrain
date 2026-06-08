# EmoBrain. Framework (EN)

(Re-written for the EmoBrain framing on branch `sj_NEW_20260608_perlmutter`. Previous v4 framework is preserved in `archive/v4_20260602/Paper/framework_EN.md`.)

## Title (working)

EmoBrain. Active brain decoding for emotion via Vision-Language Models and Brain-Video Multimodal alignment.

## Big question

Brain 에서 mixed / complex emotion 의 구조를 효과적으로 잡기 위한 model 과 task design 은 무엇인가? 구체적으로, frozen brain foundation model 의 한계를 active fine-tune + multimodal alignment 로 어떻게 보완할 수 있는가?

## Motivation

세 가지 근거가 본 framework 를 active brain VLM + multimodal direction 으로 이끈다.

1. **Frozen BFM 의 한계가 측정으로 확정됨**. 본 프로젝트의 Phase 1 (`reports/phase1_audit_20260604/`) 에서 Brain-JEPA, NeuroSTORM, SwiFT 6 종의 frozen embedding 위의 linear / MLP probe 가 단순 ROI mean BOLD + Ridge / Logistic regression baseline 을 V/A binary, V/A regression, Cat34 multilabel, Cat34 soft distribution 4 task 에서 모두 못 넘음. 원인은 Horikawa 자극의 짧은 시계열 (T 중앙값 5 TR) 과 BFM 입력의 평균 63 ~ 70% zero padding.
2. **VLM / LLM 기반 brain decoding 의 부상**. MindLLM (Qiu 2025, arXiv 2502.15786), UMBRAE (ECCV 2024), Mind Captioning (Horikawa, Science Advances 2025), MedBLIP (2023), BLIP-2 (ICML 2023), LLaVA (NeurIPS 2023) 등이 frozen LLM / VLM 을 prior 로 활용하고 brain-side adapter (linear projection + Q-Former + LoRA) 만 학습하는 paradigm 으로 brain-to-text / brain-to-image SOTA 를 달성.
3. **Multimodal brain alignment 의 standard 정립**. TRIBE (Meta FAIR, Algonauts 2025 1 위, V-JEPA2 + Wav2Vec2-BERT + Llama 통합), VIBE (video-only baseline 비교), Multi-modal brain encoding (Singh 2025), CineBrain (2025), Doerig (2024), BraVL (TPAMI 2023) 등이 brain unique contribution 을 video baseline 위에서 variance partitioning 으로 정량화하는 framework 를 확립.

EmoBrain 은 위 두 흐름을 emotion specific 한 두 axis 로 통합한다.

## Two Axes

### Direction 1. BrainVLM

fMRI 를 vision-language model 의 새 vision modality 로 통합한다. UMBRELLA_qwen 의 fMRI patchifier 로 brain volume 을 2D ROI-based 형태로 변환 후 token 화, Qwen3-VL backbone 의 LLM context 에 주입, LoRA fine-tune 으로 emotion VQA / caption / V/A score / Cat34 distribution 을 한 모델이 자연어와 numeric 으로 multi-task 출력.

### Direction 2. Brain-Video Multimodal

Brain encoder (Brain-JEPA frozen 또는 학습 가능 BFM) 와 V-JEPA2 video feature 를 공통 embedding space 로 contrastive alignment. 자극 단위 (자극 1 개 = brain 1 vec + video 1 vec) 정적 alignment + symmetric InfoNCE loss. Subject-invariant 학습 옵션 추가 (같은 자극의 다른 subject brain 끼리도 가까워지도록). Evaluation 은 variance partitioning 으로 brain unique variance = joint − video-only 의 paired bootstrap 정량화.

두 axis 는 complementary. BrainVLM 이 generative + multi-task 측면을, Multimodal 이 brain 의 정량적 contribution 측면을 다룬다. BFM 자체는 main task 가 아니지만 Direction 2 의 brain encoder 후보로 활용 가능.

## Sub-claims (falsifiable)

- **SC1 (BrainVLM gain)**. Direction 1 의 LoRA fine-tuned BrainVLM 의 V/A Pearson r 와 Cat34 macro AUROC 가 Phase 1 의 best ROI baseline 보다 의미있게 높다.
- **SC2 (Brain unique variance)**. Direction 2 의 brain-video joint 가 video-only baseline 위로 +0.05 이상의 Pearson r 향상을 보이고 paired bootstrap p < 0.05.
- **SC3 (Mixed emotion fine structure)**. 두 axis 가 Cat34 soft distribution 의 mean Pearson r 과 mixed valence 3-way categorization 에서 BFM frozen baseline 보다 의미있게 높다.
- **Null**. 위 세 sub-claim 의 효과가 noise 수준 → "active brain VLM / multimodal alignment 가 frozen BFM 보다 의미있는 gain 을 주지 못함" 의 negative result 도 그 자체로 publishable.

## Tasks

| Task | Phase 1 측정 | EmoBrain 평가 대상 |
|------|---------------|---------------------|
| V/A Binary Classification (Q1 vs Q4) | 완료 | Direction 1 + 2 |
| V/A Regression (continuous) | 완료 | Direction 1 + 2 |
| Cat34 Multilabel Classification (threshold 0.10) | 재측정 진행 중 | Direction 1 + 2 |
| Cat34 Soft Distribution Regression | 재측정 진행 중 | Direction 1 + 2 |
| Mixed Valence Categorization (Vaccaro 2024) | 미측정 | Direction 1 + 2 |
| Caption Embedding Regression | 미측정 | Direction 1 specific |
| Emotion VQA / free-form caption | 미측정 | Direction 1 specific |

## Datasets

- Horikawa naturalistic video fMRI (main). 5 subj × 2185 stim. Cowen 34-cat + 14-dim + V/A.
- Cross-dataset (Phase 5). Emo-FilM, CineBrain, StudyForrest, NNDb, Affective Videos.

## Reference

(Selected.)

- Qiu et al. 2025. MindLLM. Subject-Agnostic and Versatile Model for fMRI-to-Text Decoding. arXiv 2502.15786.
- Horikawa 2025. Mind Captioning. Evolving descriptive text of mental content from human brain activity. Science Advances.
- Xia et al. 2024. UMBRAE. Unified Multimodal Brain Decoding. ECCV.
- Chen et al. 2023. MedBLIP. Bootstrapping Language-Image Pre-training from 3D Medical Images and Texts. arXiv 2305.10799.
- Li et al. 2023. BLIP-2. Bootstrapping Language-Image Pre-training with Frozen Image Encoders and LLMs. ICML.
- Liu et al. 2023. LLaVA. Visual Instruction Tuning. NeurIPS Oral.
- Meta FAIR + ENS 2025. TRIBE. TRImodal Brain Encoder for whole-brain fMRI response prediction. arXiv 2507.22229.
- Singh et al. 2025. Multi-modal brain encoding models for multi-modal stimuli. arXiv 2505.20027.
- Cao et al. 2025. CineBrain. Naturalistic audiovisual narrative dataset with fMRI + EEG. arXiv 2503.06940.
- Doerig et al. 2024. Organization of high-level visual cortex aligned with visual rather than abstract linguistic information. bioRxiv.
- Du et al. 2023. BraVL. Brain-Visual-Linguistic tri-modal alignment. TPAMI.
- Cowen + Keltner 2017. Self-report captures 27 distinct categories of emotion bridged by continuous gradients. PNAS.
- Vaccaro 2024. Mixed valence framework. (Reference 확정 필요.)
- Horikawa 2020. The neural representation of visually evoked emotion is high-dimensional, categorical, and distributed across transmodal brain regions. iScience.
