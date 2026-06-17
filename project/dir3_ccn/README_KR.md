# CCN_Emotion

**자기지도 비디오 모델의 brain-predictable 부분공간에서의 fine-grained emotion structure.**

CCN 2026 accepted poster (Moon, 2026년 8월, 뉴욕). Camera-ready 마감 2026-06-11 AoE.

---

## 중심 포지셔닝 (2026-05-26 lock)

**Affectless machines 가설의 brain validation** (Conwell et al., 2025; Bao et al., 2024).

두 최근 발견이 자기지도 시각 모델이 어떤 emotion supervision 없이 자연 시각 통계로부터 emotion 관련 표상을 emergent 로 발달시킨다는 점을 확립. Bao et al. (2024) 가 model 내부에서 (object-recognition CNN 의 internal 뉴런이 emotion-selective). Conwell et al. (2025) 가 행동에서 (affectless visual model 이 인간 affective rating 분산의 majority 설명). 어느 쪽도 brain 을 보지 않음.

CCN_Emotion 이 그 빈자리를 채운다. 조작적 질문:

> **자기지도 비디오 모델에서 발달하는 emergent emotion 표상이 인간 뇌가 감정 영상을 처리할 때 사용하는 시각 표상과 일치하는가.**

V-JEPA2 내부의 subspace overlap 질문으로 testable. Brain-aligned subspace (M1, Brain-JEPA 로부터 예측 가능한 V-JEPA2 PCs) 와 emotion-encoding subspace (M2, emotion rating 을 예측하는 V-JEPA2 PCs) 가 각각 정량화되고, 그 overlap (M3) 이 중심 finding. High overlap 은 affectless machines 가설을 신경 수준에서 지지. Disjoint subspace 는 가설을 model 내부와 행동에 한정, emotion construction 의 reentry 관점 지지.

전체 framework: [Paper/framework_EN.md](Paper/framework_EN.md) / [Paper/framework_KR.md](Paper/framework_KR.md).

---

## 프로젝트 내러티브 (8 단계 흐름)

**1. 관찰한 것.** V-JEPA2 는 감정 라벨을 한 번도 본 적 없는 자기지도 비디오 모델이다. 2,196 개 감정 영상에 대한 V-JEPA2 의 100 개 주요 주성분을 가져와, Brain-JEPA 가 인코딩한 사람들의 뇌 반응으로부터 선형 예측 가능한 것이 어느 것인지 물었다. 통계 보정 후 단 3 개만 살아남았다. 그 3 개 위에서 비디오들은 34 개 이산 감정 카테고리 라벨로 더 sharp 하게 cluster 되며, arousal-valence 차원으로는 덜 퍼진다 (full V-JEPA2 공간의 1.26 대비 비율 1.44). 패턴은 5 명 subject 전부에서 안정적.

**2. Abstract 가 주장한 것, 그리고 그게 왜 점프인지.** Abstract 는 이 3-PC 영역을 "affective subspace" 로 명명하고 감정 schema 가 시각 통계에 내재한다는 증거로 해석했다. 차분히 다시 읽으면, 측정과 주장 사이에 두 개의 interpretive leap 가 있다. **Leap 1**: 3 개 PC 는 정의상 V-JEPA2 의 시각 feature axis 다. 이를 "affective" 라고 부르는 것은 categorical clustering 이 affect-relevant structure 를 반영한다고 전제하는 것이다 (Cowen-Keltner 자극 셋 안에서 emotion category label 과 함께 변동하는 visual category 통계 — 얼굴, 장면, 모션 패턴 — 가 아니라). **Leap 2**: 인용된 근거 (Kragel 2019, Conwell 2025) 는 자기지도 비디오 모델에 대한 이 메커니즘을 입증하지 않는다. Kragel 은 supervised emotion classifier 를 썼고, Conwell 은 brain 측정 없이 행동만 봤다.

**3. 정직하게 거기 있는 것.** 그 leap 들 없이 데이터가 입증하는 것은 **V-JEPA2 와 subject-invariant brain response 사이의 category-friendly visual readout channel** 이다. V-JEPA2 의 시각 feature axis 3 개가 brain 에 추적되고, 그 axis 위에서 이 자극 셋의 비디오들이 연속 affect 보다 emotion category label 로 더 잘 분리된다. 그게 경험적 발견이다.

**4. 우리가 진짜 알고 싶은 것.** 정직한 finding 위에서, 중심 질문은 brain 이 readout 하는 visual 정보가 무엇인가다.
(a) 일반 visual recognition (object, scene, face, motion) 이 emotion category label 과 우연히 함께 변동하는 것,
(b) 일반 visual recognition 너머의 무엇이지만 어떤 vision model 에든 존재하는 것, 또는
(c) 자기지도 비디오 사전학습이 emergent representation 으로 특이하게 만드는 것.

**5. 어떻게 답하나.** 두 단계 통제 실험. **통제 1 (Pillar 2)**: 일반 visual baseline (object 는 DINOv2, scene 은 Places365, motion 은 optical flow, 저수준 통계는 Sadeghi 2024) 를 partial out 하고 categorical-vs-dimensional 비율이 살아남는지 본다. 사라지면 (a) 확정. **통제 2 (Pillar 3)**: untrained V-JEPA2 (random init), ImageNet-supervised ViT-L, VideoMAE 에서 전체 pipeline 을 돌린다. V-JEPA2 만 나오면 (c) 지지. 모두 같이 나오면 (b) 가 맞는 해석.

**6. 세 가지 가능한 결말, 모두 정직하다.** 시나리오 (c) 는 NeurIPS 또는 Nature Communications 급 발견 (자기지도 비디오 사전학습이 brain-readable affect-relevant 시각 구조를 emergent property 로 만든다). 시나리오 (b) 는 Conwell 2025 의 brain 버전 (어떤 visual representation 도 표준 task 너머의 category-organized affect 구조를 담는다). 시나리오 (a) 는 CCN poster 수준에서 프로젝트를 마무리하고 camera-ready 약화를 강제한다. 핵심은 선호하는 결말에 안착하는 것이 아니다. 핵심은 실제로 알아내는 것.

**7. 왜 중요한가, 세 청자에게.** **감정 신경과학** 에게는, Kragel et al. (2019) 의 "감정 schema 가 visual cortex 에 내재" 결과를 자기지도 모델로 업데이트하여, emotion-supervised classifier 에서 오는 순환성을 제거하고, 시각 표상이 중립 재료인가 (Barrett 2017) 이미 affect-relevant 인가에 대한 구성주의 논쟁에 직접 증거를 제공. **AI/ML** 에게는, 자기지도 비디오 사전학습이 "general visual learning" 인지 아니면 자연 영상 통계가 emergent 로 affect-relevant 구조를 담는지를 묻는다. **방법론적으로**, brain-predictable subspace 식별을 within-model interpretability 도구로 도입한다 — Sartzetaki et al. (2025, ICLR) 의 across-model alignment decomposition 의 자연스러운 within-model 쌍.

**8. 문헌 안에서의 위치.** 직접적 경험 benchmark 는 **Horikawa et al. (2020)** — 같은 데이터셋, 같은 근본 질문, 그들의 primitive 2020 년 visual baseline 을 foundation-model 렌즈로 업그레이드. 방법론적 benchmark 는 **Sartzetaki et al. (2025, ICLR)** — 그들이 100 개 모델 across video-to-brain alignment 를 분해했고 우리는 단일 모델 within alignment 를 분해. EmoViS (같은 데이터셋의 별개 프로젝트) 는 across-model 감정 질문을 다루고, CCN_Emotion 은 within-model 분해를 다룬다. 두 프로젝트는 보완적, 중복 아님.

### 한 줄 요약

감정 라벨을 한 번도 본 적 없는 자기지도 비디오 모델이 그럼에도 brain 이 추적하는 작은 표상 조각을 갖고 있고, 그 조각 안에서 비디오들이 연속 affect 보다 이산 emotion category 로 더 잘 cluster 된다. 그게 emotion 영상이 시각적으로 cluster 되어 있는 trivial 반영인지, 자기지도 비디오 학습이 emergent 한 affect-relevant 시각 표상을 만든다는 증거인지, 후속 통제 실험이 결정한다.

---

## 이 프로젝트가 묻는 것

자기지도 비디오 모델 (V-JEPA2) 은 어떤 감정 supervision도 없이 수십억 프레임의 자연 영상으로부터 시각 표상을 학습한다. 이 표상을 감정 영상을 보는 사람의 whole-brain fMRI embedding (Brain-JEPA) 에 ridge regression 으로 회귀시키면, V-JEPA2 의 적은 수의 방향만이 brain 으로부터 선형 예측 가능한 부분공간으로 살아남는다.

**이 V-JEPA2 의 brain-predictable 부분공간은 실제로 무엇을 표상하는가?**

CCN abstract 의 경험적 발견은, 이 부분공간이 compact 함에도 불구하고 (Brain-JEPA → V-JEPA2 ridge 후 3 개 PC 가 FDR 보정 통과), dimensional 보다 categorical 하게 조직됨이다. Categorical (34 Cowen-Keltner 감정 카테고리) mean R² 가 dimensional (arousal-valence) mean R² 의 1.44 배이고, full V-JEPA2 100-PC 공간에서는 1.26 배다. 이 패턴은 Horikawa et al. (2020) 5 명 모든 subject 에서 일관되며, VGG19 visual feature 와 73-dim semantic feature 를 통제한 후에도 약화되지만 사라지지 않는다.

Abstract 는 이를 "자기지도 학습이 spontaneously categorical 한 affective subspace 를 생성한다" 로 framing 했다. 그러나 이 framing 은 abstract 가 포함하지 않은 baseline 통제를 요구한다. 후속 프로젝트는 이 주장을 엄밀히 검증하는 것.

---

## 정직한 framing (2026-05-26 확정)

V-JEPA2 는 비디오만 본다. 따라서 Brain-JEPA ↔ V-JEPA2 alignment 는 **정의상 visual statistics 다**. 흥미로운 질문은 "alignment 가 visual 인가" (그렇다, 자명히) 가 아니라 **어떤 종류의 visual structure 가 brain-readable 인가** 다.

이것은 Sartzetaki et al. (2025, ICLR) "One Hundred Neural Networks and Brains Watching Videos: Lessons from Alignment" 이 across-model 수준에서 던진 질문의 within-model 쌍둥이다. Sartzetaki 는 어떤 모델 특성 (temporal processing, action classification, FLOPs) 이 video-to-brain alignment 를 결정하는지를 물었다. CCN_Emotion 은 V-JEPA2 내부의 어떤 component 가 brain-aligned 신호를 담는지, 그리고 그 신호가 generic visual baseline 으로 흡수되는지 아니면 자기지도 비디오 사전학습에 특이적인지를 묻는다.

### 3-pillar

1. **Existence (존재).** V-JEPA2 의 compact, brain-readable 부분공간이 존재함 (3 PCs survive FDR). Abstract 에 이미 보임.

2. **Specificity (특이성).** 이 부분공간의 categorical 조직화가 generic visual baseline (저수준 통계, object recognition, scene categorization, motion energy) 통제 후에도 잔존함. Abstract 는 부분적 테스트 만 있음 (VGG19 + 73-dim semantic). 후속 작업은 DINOv2 (object), Places365 (scene), optical flow (motion) 을 추가 confound term 으로 넣어야 함.

3. **Self-supervised contribution (자기지도 학습의 기여).** Untrained ViT 와 ImageNet-supervised ViT baseline 은 같은 categorical-vs-dimensional 패턴을 만들지 않음. Abstract 는 이를 테스트하지 않음. 후속 작업은 untrained V-JEPA2 (random init), ImageNet-supervised ViT-L, 가능하면 VideoMAE 비교 필요.

Pillar 2 와 3 이 성립하면, V-JEPA2 의 brain-readable 부분공간은 표준 visual recognition task 로 흡수되지 않고 random 또는 supervised baseline 으로 만들어지지 않는, 카테고리 조직화된 visual structure 를 담는다. 이것이 방어 가능한 "자기지도 비디오 사전학습이 affective visual signal 을 담는다" 주장이다. Pillar 2, 3 없이는 abstract 는 overclaim.

### 금지 표현

- "Self-supervised learning spontaneously produces a categorical subspace" (Pillar 3 baseline 없이)
- "The brain is categorical" (분석은 visual-to-brain mapping 이지 brain 자체가 아님)
- "Subjective emotion is categorical" (행동 측정 0개)
- "V-JEPA2 learned emotion" (V-JEPA2 는 emotion supervision 없음)
- "Brain reads out emotion structure from V-JEPA2" — "emotion structure" 정의 없이 사용 금지

`notes/narrative_v2.md` 에 전체 추론 정리.

---

## EmoViS 와의 관계

[EmoViS](../EmoViS/) 는 별개 프로젝트 (이 프로젝트의 파생 아님). 동일 Horikawa 데이터셋으로 더 넓은 질문을 다룬다. Sensory-to-semantic 모델 스펙트럼 (VideoMAE, DINOv2, V-JEPA2, CLIP, Caption+LLM) 중 어떤 family 가 raw BOLD 로 직접 구축된 stimulus-level brain geometry 와 가장 잘 일치하는가.

세 프로젝트가 하나의 논리 사슬을 이룬다.

- **Sartzetaki 2025 (ICLR)** — 100 개 모델 전반에서 무엇이 video-to-brain alignment 를 만드는가. *"alignment 의 의미가 무엇인가" 의 anchor.*
- **EmoViS** — sensory-to-semantic 모델 스펙트럼 전반에서 무엇이 stimulus-level emotional brain geometry 와 일치하는가. *Across-model emotion alignment.*
- **CCN_Emotion (이 프로젝트)** — V-JEPA2 내부에서 brain 이 무엇을 readout 하고, 그것이 generic visual baseline 으로 흡수되는가. *Within-model emotion alignment.*

CCN_Emotion 과 EmoViS 는 데이터 (Horikawa fMRI, V-JEPA2 features) 를 공유하지만 다른 질문에 답한다.

---

## 저장소 구조

```
CCN_Emotion/
├── CLAUDE.md                    프로젝트 지침 (폴더 규칙, narrative, 데이터 fact)
├── README.md / README_KR.md     이 파일
├── .gitignore
├── Paper/                       accept 된 abstract + camera-ready 자료 (작성 예정)
│   └── ccn2026_accepted.pdf
├── notes/                       narrative 메모, camera-ready 계획
│   ├── narrative_v2.md          전체 3-pillar narrative + Sartzetaki anchor
│   ├── camera_ready_plan.md     6/11 mechanical + text 수정 체크리스트
│   └── archive/                 옛 direction 문서, 옛 result summary
├── data/
│   └── raw/                     raw 입력 (.gitignore 처리)
│       ├── brain_embeddings/      Brain-JEPA 768-dim, 5 subj × 2196
│       ├── video_embeddings/      V-JEPA2 1408-dim + CLIP 512-dim
│       ├── videos/                CowenEmotionVideos (2196 mp4)
│       ├── feature/               Horikawa .mat features
│       ├── raw_fmri/fmri_raw.npy  5 × 2196 × 450 parcels
│       ├── semantic_features.csv
│       └── vision_features.csv
├── logs/                        프로젝트 공통 SLURM 로그
├── study1/                      메인 페이퍼: V-JEPA2 brain-predictable subspace
│   ├── code/                    active 스크립트 12 개 + RESULTS_EXP*.md + experiment spec
│   │   └── archive/             figure generator + superseded 탐색 스크립트
│   │       ├── README.md        archive 안에 뭐가 왜 있는지
│   │       └── extraction_infra/  재사용 가능한 추출/로더 스크립트
│   ├── data/                    중간 RSM, PC projection, ridge weight
│   ├── logs/
│   └── results/figures/         51 개 figure (paper Fig 1-2 + exp14-19 supplementary)
└── study2_thesis/               평행 thesis chapter 워크스트림 (별도 scope)
    ├── code/                    ch1, ch2 분석 (Glasser parcellation, ROI decoding, gradient, VP)
    ├── data/, results/, figures/, logs/, reference/, storyline/
```

---

## 정리 이력 (2026-05-26)

이 날짜 이전, 디렉토리는 세 워크스트림이 root 에 엉켜 있었다.

- **워크스트림 A** (root-level `01_~07_*.py`, `RESULTS_FULL.md`, `RESULTS_SUMMARY.md`, `CCN_draft.md`): 옛 V-JEPA2-vs-CLIP overall + per-emotion CKA 분석. Accept 된 abstract 는 이 framing 에서 pivot.
- **워크스트림 B** (`CCN2026/`): CCN 페이퍼가 된 brain-predictable subspace 분석.
- **워크스트림 C** (`main/`, `storyline/`): thesis chapter 분석 (ROI decoding, principal gradient, variance partitioning).

재구성:
- 워크스트림 B → `study1/` (CCN 페이퍼).
- 워크스트림 C → `study2_thesis/`.
- 워크스트림 A 분석 스크립트 + 파생 결과 ~226 MB (`cka_results/`, `subject_blocks/`, `raw_fmri_outputs/`, 옛 `figures/`) → 사용자 지시로 삭제. 워크스트림 A 의 추출 인프라 (V-JEPA2 다운로드, embedding 추출, CLIP 추출, layer-wise 추출) 는 재사용 가치 있어서 `study1/code/archive/extraction_infra/` 에 보존.
- Raw 입력 `data/raw/` 로 통합.
- Accept 된 PDF → `Paper/ccn2026_accepted.pdf`.
- One-time metadata helper 와 `CowenEmotionVideos.zip` (1.7 GB, unzip 된 `videos/` 와 중복) → 삭제.

총 크기 4.0 GB → 2.1 GB.

각 archive 서브 디렉토리에 무엇이 왜 있는지는 `study1/code/archive/README.md` 참고.

---

## 프로젝트가 가는 방향

### Tier 0 — Camera-ready (마감 2026-06-11)
Text 수준 수정만 ("not intended to be a significant revision"). "Spontaneously produces" 주장 약화, ratio 비교와 partial R² 의 구체적 통계 추가, baseline 부재 한계를 1 문장으로 명시. Mechanical: 새 LaTeX 템플릿, deanonymization, LLM-use disclosure. `notes/camera_ready_plan.md` 참고.

### Tier 1 — Pillar 2 baseline 통제 (2026-05-26 ~ 2026-06-02)
DINOv2 (object), Places365 (scene), optical flow (motion) feature 추출. 각각을 partial 한 후 V-JEPA2 brain-predictable subspace 의 partial R² 계산. 목표: categorical 조직화가 어떤 단일 표준 visual recognition task 로도 흡수되지 않음을 보임. 결과는 8월 포스터의 supplementary panel.

### Tier 2 — Pillar 3 모델 baseline (2026-06-03 ~ 2026-06-16)
Untrained V-JEPA2 (random init, 동일 아키텍처), ImageNet-supervised ViT-L, VideoMAE 의 embedding 추출. 각각 동일 pipeline (100 PCs → ridge → categorical/dimensional ratio) 실행. 목표: brain-aligned categorical 조직화가 아키텍처 또는 임의 사전학습이 아니라 자기지도 비디오 사전학습에 특이함을 보임. 결과는 8월 포스터.

### Tier 3 — Mechanistic depth (2026-06-17 ~ 2026-08-03)
Layer-wise V-JEPA2 (블록 4, 8, ..., 40) brain-aligned ratio. Brain region-wise breakdown (Schaefer parcel, network). PC1 stimulus 해석 (top-k 유사/비유사 영상). Horikawa fMRI 의 split-half reliability 로 noise ceiling. 8월 포스터 발표를 위한 story 성숙화.

### Tier 4 — 풀 페이퍼 (포스터 후)
Cross-validation 재설계, cross-dataset replication (가능하면 Kragel emotion fMRI), decoding accuracy, Barrett constructionism vs Sartzetaki cross-model alignment 결과와의 이론 framing 정렬. Target venue 미정 (NeurIPS, Nature Communications 등).

---

## 핵심 참고문헌

- **Horikawa et al. (2020)** — fMRI 데이터셋; 5 subj × 2196 감정 영상.
- **Cowen & Keltner (2017, *PNAS*)** — 27 카테고리 감정 분류 + 영상 stimulus pool.
- **Assran et al. (2025)** — V-JEPA 2 (분석 대상 자기지도 비디오 모델).
- **Kim et al. (2024, *NeurIPS*)** — Brain-JEPA brain foundation model.
- **Sartzetaki et al. (2025, *ICLR*)** — "alignment 의 의미가 무엇인가" anchor: 100 개 video model × brain, 무엇이 alignment 를 결정하는가.
- **Conwell et al. (2025, *PNAS*)** — affectless visual machine 이 visually evoked affective behavior 를 설명 (behavioral 선례).
- **Doerig et al. (2025, *Nature Machine Intelligence*)** — LLM caption embedding 이 high-level visual brain 과 align (semantic side 신경 선례).
- **Kornblith et al. (2019, *ICML*)** — CKA representational similarity 메트릭.
- **Kriegeskorte et al. (2008)** — RSA 기초 논문.
