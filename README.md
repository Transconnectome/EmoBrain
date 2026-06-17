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

## Three Directions

| Direction | 핵심 아이디어 | 주요 reference |
|-----------|----------------|----------------|
| **Direction 1. BrainVLM** | Qwen3-VL VLM 의 fMRI patchifier + LoRA fine-tune. 자연어와 numeric 으로 emotion VQA / V/A / Cat34 distribution 동시 출력. | MindLLM 2025, UMBRAE 2024, Mind Captioning 2025, MedBLIP 2023, BLIP-2 2023, LLaVA 2023 |
| **Direction 2. fMRI-LM** | Wei 2026 paper 의 fMRI-LM architecture (Brain-JEPA-like tokenizer + GPT-2/Qwen3 LLM + SigLIP + GRL + F2F+F2T+T2T) 차용 후 emotion specific 으로 발전. LLM tokenizer 활용 방향. | fMRI-LM (Wei 2026, arXiv 2511.21760) |
| **Direction 3. CCN. Contextualized representation + 새 task design** | Video model embedding 으로 learning clustering → context 반영된 clustering → brain 이 그 context 학습 (Brain-Video alignment). 같은 emotion 안에서 context 별 sub-cluster 가 나타나는지 검증. | TRIBE 2025, VIBE 2025, CineBrain 2025, Doerig 2024, BraVL 2023 |

D1 + D2 는 main paper path (EmoBrain). D3 는 CCN 발표용 별도 axis (`project/dir3_ccn/` 안에 self-contained).

## Tasks (3 종류)

| 종류 | 설명 | 적용 dataset |
|------|------|----------------|
| **A. 기존 언어 task (공통)** | V/A binary (Q1 vs Q4), V/A regression, categorical classification (threshold 기준 선택) | Horikawa + Emo-FilM 둘 다 |
| **B. 새로운 공통 task (공통)** | independent dataset 에도 적용되는 label 을 어떻게 만들 것인가. clustering 이 한 방법일 수 있음. task design 결정 중. | Horikawa + Emo-FilM 둘 다 |
| **C. 개별 dataset task** | Horikawa = visual feature 위주. Emo-FilM = narratives + dynamics 반영. | dataset 특화 |

**Phase 1 측정 완료** (Horikawa 만): V/A binary, V/A regression, Cat34 multilabel, Cat34 soft. ROI baseline + chance + frozen BFM.

## Data (2 datasets)

| Dataset | Subjects | Stim | 특성 | 상태 |
|---------|----------|------|------|------|
| **Horikawa** naturalistic video fMRI | 5 | 2185 | Cowen 34-cat + 14-dim + V/A. visual feature 위주. | 사용 중 |
| **Emo-FilM** | TBD | TBD | narratives + temporal dynamics 강조 | 다운로드 예정 |

부수 데이터. Qwen-VL caption (2185 자극), V-JEPA2 / CLIP / DINOv2 / VideoMAE pretrained+scratch (Horikawa 자극).

**2 × 2 grid (Direction × Dataset)**.

| | Horikawa | Emo-FilM |
|--|----------|------------|
| **D1. BrainVLM** | (BrainVLM, Horikawa) | (BrainVLM, Emo-FilM) |
| **D2. fMRI-LM** | (fMRI-LM, Horikawa) | (fMRI-LM, Emo-FilM) |

D3 (CCN) 은 별도 axis 로 dir3_ccn 안에서 진행.

## Repository Layout

```
EmoBrain/
├── project/                ← 모든 분석 활동 (self-contained per-direction + shared)
│   ├── dir1_brainvlm/{code,data,output,results}/
│   ├── dir2_multimodal/{code,data,output,results}/
│   │   └── code/legacy_phase2/   (v4 Brain+Video framework, Direction 2 reuse base)
│   └── shared/{code,data,output,results}/   (두 direction 이 공유)
│       └── results/background/    (Phase 1 benchmark)
├── external/                ← vendored repos + checkpoints/ (pretrained, 이전 baseline/)
├── docs/                    ← masterplan + notes + reports + reference + templates + workflows + figures
├── Paper/                   ← paper draft workspace
├── archive/                 ← v4 framing 보존 + legacy + weekly + v4_results
├── tools/                   ← project-wide maintenance utility
└── 7 root .md (README, README_KR, CONTEXT_FEEL, ACTION_PLAN, CLAUDE, CODEX, ONBOARDING)
```

## Status (2026-06-08)

Branch `sj_NEW_20260608_perlmutter` 의 EmoBrain framing 이 active. Background benchmark (Phase 1 frozen BFM 측정 + audit + Cat34 threshold 0.10 재측정) 모두 완료. 다음 step 은 Direction 1 BrainVLM pilot + Direction 2 Multimodal Alignment pilot 의 병행 launch (Hackathon 5 일 단위).

상세 forward plan 은 `docs/masterplan_v3_emobrain.md`, ground-level weekly action 은 `ACTION_PLAN.md` 참조.
