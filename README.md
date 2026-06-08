# EmoBrain

**Active brain decoding for emotion via Vision-Language Models and Brain-Video Multimodal alignment.**

(Internal / repo name = EmoBrain. Branch `sj_NEW_20260608_perlmutter` 의 new framing.)

## 한 줄 요약

Naturalistic video fMRI 에서 emotion 표상을 학습하기 위해 두 axis 를 함께 진행한다. (1) **BrainVLM** axis 가 fMRI 를 VLM / LLM 의 token 으로 주입해 emotion VQA / caption / V/A score 를 자연어로 multi-task 출력한다. (2) **Brain-Video Multimodal** axis 가 brain encoder 와 video encoder 의 contrastive alignment 로 brain 이 video baseline 위에 추가하는 unique emotion variance 를 정량화한다.

## Motivation

지금 방향이 active brain VLM / multimodal 로 정리된 근거.

- **Frozen brain foundation model (BFM) 의 한계**. 본 프로젝트의 Phase 1 측정에서 frozen BFM (Brain-JEPA, NeuroSTORM, SwiFT 6 종) 의 모든 emotion task (V/A binary, V/A regression, Cat34 multilabel, Cat34 soft) 가 단순 ROI mean BOLD + Ridge regression baseline 을 넘지 못함. Phase 1 audit 결과 `docs/reports/phase1_audit_20260604/` 참조.
- **VLM / LLM 기반 brain decoding 의 부상**. MindLLM (2025), UMBRAE (ECCV 2024), Mind Captioning (Horikawa, Science Advances 2025) 등이 BFM 의 frozen embedding 단독 결과보다 일관되게 우수. 표상의 semantic manifold 를 LLM / VLM 으로 가져온 뒤 brain-side adapter 만 학습하는 paradigm 이 표준화.
- **Multimodal brain alignment 의 성숙**. TRIBE (Meta FAIR, Algonauts 2025 1 위, V-JEPA2 + Wav2Vec2-BERT + Llama 통합), Doerig 2024 (NSD 에서 vision DNN 이 LLM caption embedding 보다 고차 시각피질을 더 잘 잡음), CineBrain (audiovisual + fMRI) 등이 brain 의 added value 를 video baseline 위에서 정량화하는 framework 를 확립.

본 프로젝트는 위 두 흐름을 emotion specific 한 두 axis 로 통합한다.

## Two Axes

| Axis | 핵심 아이디어 | 주요 reference |
|------|----------------|----------------|
| **Direction 1. BrainVLM** | UMBRELLA_qwen (Qwen3-VL backbone) 또는 동등한 VLM 의 fMRI patchifier 로 brain volume 을 token 화, LLM context 에 주입, LoRA fine-tune 으로 emotion VQA + Cat34 distribution + V/A score 동시 출력 | MindLLM 2025, UMBRAE 2024, Mind Captioning 2025, MedBLIP 2023, BLIP-2 2023, LLaVA 2023 |
| **Direction 2. Brain-Video Multimodal** | Brain encoder (Brain-JEPA 등 BFM 활용 가능) 와 video encoder (V-JEPA2) 의 contrastive alignment 학습, brain unique variance = joint − video-only 정량화, subject-invariant 표상 학습 추가 | TRIBE 2025, VIBE 2025, Multi-modal brain encoding 2025, CineBrain 2025, Doerig 2024, BraVL 2023 |

두 axis 는 서로 보완. BrainVLM 이 generative + multi-task 측면, Multimodal 이 brain 의 정량적 contribution 측면을 다룬다. BFM 은 Direction 1 의 vision modality 의 적합 후보가 아니지만 Direction 2 의 brain encoder 로는 활용 가능.

## Tasks

| Task | 설명 |
|------|------|
| V/A Binary Classification | Quartile-based, Q1 vs Q4 |
| V/A Regression | Continuous score 1-9 (V), 2-8.67 (A) |
| Cat34 Multilabel Classification | 자극당 34 개 emotion 의 binary label vector, threshold 0.10 (= 1/10 raters, 자연 단위) |
| Cat34 Soft Distribution Regression | 자극당 34 차원 probability distribution, KL divergence 학습 |
| Mixed Valence Categorization | Positive / Negative / Mixed 의 3-way, Vaccaro 2024 가설 검증 |
| Caption Embedding Regression (Direction 1 specific) | Brain → Qwen-VL caption embedding mapping |
| Emotion VQA (Direction 1 specific) | "이 brain state 가 어떤 emotion 을 표현하는가" 의 자연어 응답 |

Phase 1 측정 완료. 1-4. 계획. 5-7.

## Data

- **Horikawa naturalistic video fMRI**. 5 subject × 2185 video stimulus (canonical). Cowen 34 emotion category rating + 14 affective dimension rating 동반.
- **Qwen-VL caption**. 2185 자극 모두 caption embedding 추출 완료.
- **Video features**. CLIP, DINOv2, VideoMAE, V-JEPA2 의 pretrained + scratch.
- **Independent datasets (future)**. Emo-FilM, StudyForrest, CineBrain, NNDb, Affective Videos for cross-dataset generalization.

## Repository Layout

- `project/dir1_brainvlm/{code,data,output,results}/` - Direction 1 self-contained mini-project
- `project/dir2_multimodal/{code,data,output,results}/` - Direction 2 (포함 `code/legacy_phase2/` = v4 Brain+Video framework reuse base)
- `code/` - shared (probes, bfm_embeddings, ssl_pretrain, analysis, tools)
- `data/` - shared input (Horikawa splits, target matrix, stim feature)
- `output/` - shared raw extraction (embeddings, logs, slurm)
- `results/background/` - Phase 1 benchmark 결과
- `external/` - vendored repos + `checkpoints/` (pretrained model weight, 이전 `baseline/`)
- `docs/` - forward plan + `notes/` + `reports/` + `reference/` 통합
- `Paper/` - paper draft 작업 공간 (framework, methodology)
- `archive/` - v4 framing 보존 + `legacy_archive/` + `weekly/` + `v4_results/`

## Status (2026-06-08)

Branch `sj_NEW_20260608_perlmutter` 의 EmoBrain framing 이 active. Background benchmark (Phase 1 frozen BFM 측정 + audit + Cat34 threshold 0.10 재측정) 모두 완료. 다음 step 은 Direction 1 BrainVLM pilot + Direction 2 Multimodal Alignment pilot 의 병행 launch (Hackathon 5 일 단위).

상세 forward plan 은 `docs/masterplan_v3_emobrain.md`, ground-level weekly action 은 `ACTION_PLAN.md` 참조.
