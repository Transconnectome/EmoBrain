# Decoding Workshop (2026-06-08) 협업 2 미팅 자료

**슬롯**. 10:40-11:10 (30 분)
**주제**. 협업 2 정서 자극·반응 메타데이터의 텍스트화와 뇌영상 표현 생성
**참여 lab**. 이상아 교수님 (MixedEmo, 정서-맥락 fMRI/EEG) × 문태섭 교수님 (TabLeT, 뇌영상 압축 표현) × 차지욱 교수님 (Emo-FilM, 정서 뇌 기초모델)
**우리 lab 의 역할**. 정서 동영상을 이용한 fMRI 데이터 (Horikawa, Emo-FilM) 의 텍스트화 + 정서 뇌 기초모델 (FEEL) 의 backbone 제공

이 자료는 워크샵 참여자 (다른 lab 의 연구원, 처음 우리 프로젝트를 보는 사람) 를 대상으로 작성됨. 모든 약어와 개념은 처음 등장 시 풀어 설명.

---

## 목차

1. 협업 2 한 줄 정의 (왜 우리가 함께 모이는가)
2. 우리가 사용하는 핵심 데이터셋 3 가지 (Horikawa, Emo-FilM, MixedEmo)
3. 우리 lab 이 Horikawa 데이터로 지금까지 한 것들 (Phase 1-3a 측정 결과)
4. 우리 새 프로젝트 FEEL = Foundation Model for Emotion Embedding Learning
5. 앞으로 할 것들 (Track A, B, C + standard baseline + future extensions)
6. Neuro-AI SOTA (2025-2026) 와 우리 프로젝트의 연결
7. 협업 2 에서 우리가 기여할 부분 (텍스트화 + 뇌영상 표현)
8. 워크샵에서 함께 결정할 것들

---

## 1. 협업 2 한 줄 정의

> 정서 동영상 자극, 사람의 정서 반응, 행동 평정 메타데이터, fMRI / EEG 데이터를 *대규모 언어모델 (LLM)* 과 *뇌영상 표현 모델* 이 함께 사용할 수 있는 학습자료로 정리하는 작업.

쉽게 말하면, 영화를 본 뇌 데이터를 그냥 .nii 파일로 두지 않고 **AI 가 학습할 수 있는 형태로 텍스트와 함께 묶는 작업**.

### 왜 필요한가

뇌 데이터를 GPT 같은 LLM 또는 CLIP 같은 vision-language model 과 연결하려면, fMRI 파일만 있어서는 부족하다. 모델이 학습하거나 해석할 수 있는 형태로 아래 정보가 함께 정리되어야 한다.

| 정보 층위 | 준비할 내용 | 예시 |
|---|---|---|
| 자극 설명 | 참여자가 본 동영상의 장면, 대상, 맥락, 정서 단서 | "어두운 공간에 혼자 있는 사람", "위협적 장면" |
| 시간 정보 | 자극 제시 시간, 장면 전환, 시행 구간, fMRI 시간창 | 시행 번호, 영화 시간, 20 TR window |
| 사람 반응 | 참여자의 정서 평정, 행동 반응, 개인차 변수 | 긍정/부정, 각성도, 불안 척도 |
| 뇌 데이터 | fMRI, EEG, 전처리 상태, 입력 형태 | 전처리 완료 여부, 뇌영상 볼륨, EEG 주파수 |
| 텍스트 학습자료 | 자극-반응-뇌 데이터 관계 설명 문장 | "이 시간창에서 참여자는 높은 각성을 보였고, 해당 장면은 위협 단서가 포함" |
| 뇌영상 표현 | TabLeT / 압축 autoencoder 로 만든 표현 | 시간창별 표현 벡터, 시행별 token |

협업 2 는 단순히 뇌영상을 토큰으로 압축하는 일이 아니다. **동영상 자극과 사람 반응의 의미 정보를 텍스트로 만들고, 그 텍스트 자료를 뇌영상 표현과 시행 또는 시간창 단위로 정렬하는 것** 이 핵심이다.

---

## 2. 우리가 사용하는 핵심 데이터셋 3 가지

### 2.1 Horikawa 데이터 (우리 lab 주관)

**한 줄**. 5 명의 참여자가 약 2,185 개의 짧은 동영상 (각 약 1 분) 을 보면서 측정한 fMRI 데이터. 동영상마다 사람들이 매긴 정서 점수 (총 34 개의 정서 카테고리) 가 함께 있다.

**Citation**. Horikawa, Cowen, Keltner, Kamitani (2020 Cell Reports). "The neural representation of visually evoked emotion is high-dimensional, categorical, and distributed across transmodal brain regions."

**자세히**.
- **참여자**. 5 명 (sub-01 ~ sub-05). 같은 자극을 모두 본 fMRI 데이터.
- **자극**. 2,185 개 short video clip (각 약 1 분). 각자 다양한 emotion 을 evoke 하는 영상.
  - Cowen & Keltner 2017 PNAS 의 "27 distinct emotions evoked by videos" 의 후속 fMRI 실험.
- **Emotion label**. Cowen 의 34 개 emotion category. 각 영상마다 다수의 외부 평가자가 0-1 사이 점수 부여 후 평균 → 영상당 34-dim soft distribution 보유.
- **추가 metadata**. Valence (긍정-부정, 1-9), Arousal (각성도, 1-9), Cowen 14 개 affective dimension.
- **TR / Scanner**. 3T Siemens, TR 2 s.
- **Stimulus 0**. resting baseline (16 TR). 분석 시 제외 → canonical 2,185 stim.

**우리 lab 의 처리 상태**.
- 5 subject × 2,185 stim 모두 ROI parcel 추출 완료 (Schaefer-400 + Tian-50 = 450 ROI).
- 5-fold stim-stratified CV (Valence × Arousal quartile joint stratification) 설정 완료. `data/horikawa_5fold.csv`.
- Brain-JEPA, SwiFT (6 variants), NeuroSTORM 의 frozen embedding 모두 추출 (output/embeddings/).

**Horikawa 가 우리에게 중요한 이유**. 짧은 video × 다양한 emotion 의 *brain side phenotype* 을 가장 잘 보존한 dataset. Cowen 의 34-cat 이라는 *multi-dimensional emotion taxonomy* 로 학습 / 평가 가능.

### 2.2 Emo-FilM (차지욱 교수님 lab Emo-FilM / Horikawa 정서 fMRI)

**한 줄**. 30 명이 14 개의 짧은 영화 (총 약 2.5 시간) 를 보면서 측정한 fMRI 데이터. 영화의 *시간축에 따라* 1 Hz 로 50 개의 정서 변수가 계속 평가됨.

**Citation**. Cordoni, Welbourn, Vincent, Saive, Bobin, Sander (2025 Scientific Data). "Emo-FilM. A multimodal dataset for affective neuroscience using naturalistic stimuli."

**자세히**.
- **참여자**. 30 명. fMRI 30 명 + 별도 emotion rating 평가자 44 명.
- **자극**. 14 개 short film (총 2.5 시간). Naturalistic stimulus.
- **Emotion annotation**. 50 개 항목.
  - 13 discrete emotion (Plutchik 기반)
  - 42 항목의 Component Process Model (CPM) 변수 = appraisal + motivation + motor expression + physiological response + subjective feeling 의 5 도메인.
  - **1 Hz continuous rating** (영화 진행 중 시간축마다 평가).
- **추가 modality**. 호흡, 심박, 전기피부반응 (electrodermal activity) 1,000 Hz.
- **TR / Scanner**. 3T Siemens, TR 1.3 s, multiband acceleration MB=3.
- **공개**. OpenNeuro BIDS 형식.

**중요 차이 (Horikawa 와 비교)**.
- Horikawa = 짧은 clip × 많은 stim × group-consensus emotion rating.
- Emo-FilM = 긴 narrative × 적은 stim × 시간축 continuous emotion rating + 풍부한 physiology.
- 둘은 *상호 보완*. Horikawa = "stim 의 evoked emotion 의 brain code". Emo-FilM = "긴 context 의 emotion dynamics 의 brain code".

**구현 저장소** (차지욱 교수님 lab). `Transconnectome/BEACON-T`, `beacon_t/data/hdf5/emofilm.py`.

**확인 필요사항**. BEACON-T 상태 문서의 "Horikawa 5 명 / 27 정서 범주" 항목과 emofilm.py 의 "Emo-FilM 30 명 / 50 변수" 항목이 같은 자산인지 정리 필요.

### 2.3 MixedEmo (이상아 교수님 lab)

**한 줄**. 92 명이 *장소 이미지 + 정서 단서 이미지* 의 5 가지 조합을 보면서 측정한 fMRI / EEG 데이터. 같은 참여자에서 fMRI 와 EEG 둘 다 측정.

**자세히**.
- **참여자**. 92 명. 현재 62 명 분석 완료, 30 명 미완료.
- **자극 설계**. 장소 이미지 (예. 공원, 거리, 실내) × 정서 단서 이미지 (예. 행복한 표정, 두려운 표정) 의 조합.
- **5 조건**.
  1. 중립 장소 + 중립 단서
  2. 부정 장소 + 부정 단서
  3. 긍정 장소 + 긍정 단서
  4. 긍정 장소 + 부정 단서 (mixed)
  5. 부정 장소 + 긍정 단서 (mixed)
- **Modality**. fMRI + EEG, 동일 참여자.
- **기존 결과**. 앞쪽 대상피질 (anterior cingulate cortex) 하위영역의 기능적 해리, 불안 척도의 개인차, EEG theta 바이오마커.
- **텍스트화 대상**. 장소 이미지 설명, 정서 단서 이미지 설명, 조건명, 시행 순서, 참여자 반응, 정서 평정, 개인차 변수 (불안 척도 등).

**Horikawa / Emo-FilM 과 비교**.
- Horikawa / Emo-FilM = 영상 자극.
- MixedEmo = 정지 이미지 조합 + 명시적 emotion mixture 조건. *Context-emotion congruency* 의 brain mechanism 직접 평가 가능.

---

## 3. 우리 lab 이 Horikawa 데이터로 지금까지 한 것들

우리 프로젝트의 코드명은 **FEEL = Foundation Model for Emotion Embedding Learning** (이전 이름은 FEELIN 이었음). v4 final framing 으로 정리 (2026-06-02). Branch `v4_20260602_perlmutter` 에 모든 결과 저장.

3 단계의 측정을 완료했고, 각 단계의 결과가 다음 단계의 framing 을 결정했다.

### 3.1 Phase 1 (Frozen probe benchmark)

**무엇을 했나**. Horikawa fMRI 의 *frozen embedding* 을 다음 모델들에서 추출 후, V/A binary classification 같은 emotion task 에 linear 또는 MLP probe 학습.

**측정한 model**.
- ROI Schaefer-400 + Tian-50 = 450 ROI 의 단순 mean BOLD signal
- Brain-JEPA (ROI 입력)
- SwiFT 6 variants (NewE36, NewE96, NewE192, UAH 5M, UAH 51M, UAH 202M, 4D volume 입력)
- NeuroSTORM (4D volume 입력)
- Video models (Phase 1 의 reference): CLIP, V-JEPA2, DINOv2, VideoMAE, Qwen-VL caption

**핵심 finding (numeric, V_binary AUROC 기준)**.

| Model | V_binary AUROC | 의미 |
|---|---|---|
| **ROI Schaefer400+Tian50 mean (linear, pooled)** | **0.7889 ± 0.0119** | 가장 단순한 baseline 이 brain encoder 들 중 best |
| Best BFM (Brain-JEPA resting zero linear) | 0.7402 ± 0.0365 | 정교한 BFM 이 ROI mean 보다 약함 |
| SwiFT 모든 variant | 0.65 ~ 0.70 | Size effect 없음. 5M, 51M, 202M 다 비슷 |
| **CLIP_pretrained (video only)** | **0.9708** | Video model 단독이 brain model 다 압도 |

**해석**.
1. Brain 정교화 (BFM 의 capacity, padding strategy 등) 가 group-level emotion 측정에 효과 없음.
2. Phase 1 의 V/A label 은 *외부 평가자 collective consensus* 라서 video 의 attribute 에 가깝다. 그래서 video model 이 단독으로 0.97 saturation.
3. Brain 의 added value 가 group-level V/A 에는 없음 = trivially confirm.

### 3.2 Phase 2 (Trained integration benchmark)

**무엇을 했나**. Brain + Video 의 joint 학습. Phase 1 finding 이 frozen probe 의 한계일 수 있어서 *학습된 fusion* 으로 brain conditioning 의 added value 측정.

**4 fusion architecture**.
- A. Token transformer (BrainVLM style. fMRI 가 LLM token 으로 주입)
- B. Cross-attention (fMRI 가 query, video 가 key/value)
- C. Contrastive joint (brain + video shared latent)
- D. Late fusion (각자 처리 후 concat)

**4 brain-only method** (video 없이 brain 만으로 정교한 학습).
- I. Supervised MLP
- II. CLIP distillation
- III. Multitask
- IV. Subject-aware

**핵심 finding (V_binary AUROC 기준)**.

| Method | V_binary AUROC | Δ vs CLIP-only |
|---|---|---|
| **D late fusion (joint)** | **0.9718 ± 0.0082** | **+0.001 (noise)** |
| A token transformer | 0.9670 ± 0.0111 | -0.004 |
| B cross-attention | 0.9663 ± 0.0087 | -0.005 |
| C contrastive joint | 0.9606 ± 0.0084 | -0.010 |
| CLIP-only (Phase 1 reference) | 0.9708 | - |
| Brain-only best (III multitask) | 0.7235 ± 0.0209 | -0.247 |

**V_reg Pearson r**. A token 0.7628 vs CLIP 0.7645 = -0.002
**A_binary AUROC**. D late fusion 0.8025 vs CLIP 0.8003 = +0.002

**해석**.
- 4 fusion architecture *모두* video baseline 을 의미 있게 못 넘음. Δ = noise.
- "Brain + video fusion 으로 emotion task 의 성능을 향상" 가설 = falsified.
- Group-level emotion 의 brain 추가 contribution = 0.
- **하지만 brain 의 unique value 가 없다는 의미는 아님**. Group-level V/A 라는 *raw axis* 에서 video saturate 한 것일 뿐, brain unique signal 은 *다른 axis* 에 있을 수 있다.

### 3.3 Phase 3a (BrainVLM, supplementary)

**무엇을 했나**. fMRI 를 LLM token 으로 변환해서 emotion caption 생성 (UMBRELLA_qwen 의 Qwen3-VL backbone 활용).

**결과**.
- Fold 1 학습 완료 (loss 1.94 → 0.151).
- Inference V_reg Pearson r = NaN (XML parsing failure 의심), MAE 2.55.
- Scale mismatch (prompt 1-5 vs Cowen actual 1-9).

**해석**. Generative path 의 baseline 시도. 추가 학습 risk 대비 evidence 약해서 *supplementary* 로 demote.

### 3.4 Phase 1-2 가 우리에게 가르쳐 준 것

Group-level V/A axis 는 video 가 saturate. Brain unique signal 은 **다음 4 axis 에서만 발견 가능**.

1. **Multi-dimensional geometry**. V/A 가 아닌 high-dim emotion (34-cat, 14-dim, OV description) 의 brain organization
2. **Transmodal localization**. 특정 brain region (STS, TPJ, mPFC 등 transmodal regions) 의 emotion specific representation
3. **Subject-conditioned variability**. Subject 마다 같은 stim 에 대한 다른 emotion 의 brain mapping
4. **Cross-dataset transfer**. Horikawa 에서 학습한 representation 이 다른 dataset 으로 보존되는지

이 4 axis 의 공통 motif = *invariance*. 즉 어떤 surface variation 위에서 보존되는 emotion code 가 brain 에 있는지의 질문.

이게 우리 새 framing 의 출발점.

---

## 4. 우리 새 프로젝트 FEEL = Foundation Model for Emotion Embedding Learning

### 4.1 Big Question

> Brain 에 paradigm, label taxonomy, subject 의 surface variation 을 가로지르는 *universal emotion code* 가 존재하는가? Multi-source naturalistic emotion fMRI 의 adaptation 으로 그 universal code 를 학습하고 검증할 수 있는가?

쉽게 말하면.
> "공포" 같은 emotion 이 *사람마다, 자극마다, paradigm 마다 다른 brain pattern* 인가, 아니면 *공통 universal code* 가 brain 에 있는가?

이건 Wager 의 "universal pain signature" (통증의 universal brain code 발견 시도, Wager 2013) 의 emotion 판이다. Affective neuroscience 의 미해결 질문.

### 4.2 4 Falsifiable sub-claim

1. **Multi-source pretrain invariance**. Universal code 가 있다면, 여러 dataset (Horikawa + Emo-FilM + StudyForrest + Affective Videos) 의 multi-source SSL pretrain 이 single-source pretrain 보다 cross-dataset transfer 에서 더 invariant.
2. **ROI localization**. Universal code 는 brain 의 특정 ROI / network 에 localize (Cowen 2020 transmodal 가설 비교).
3. **Subject-invariant alignment**. Subject-invariant SSL 학습 후 같은 stim 의 다른 subject 의 representation 이 의미 있게 alignment.
4. **Null hypothesis**. 위 세 metric 모두 acquisition floor 안 → "universal code 없음, emotion 은 paradigm/subject-specific representation" 결론. **이것 자체도 publishable negative result**.

### 4.3 Build recipe (FEEL 의 architecture)

5 명 × 2,185 stim 으로는 emotion brain foundation model 을 from-scratch pretrain 불가. 그래서 **이미 학습된 두 foundation model 을 잇는 adaptation** 이 honest scope.

```
fMRI (Schaefer-400 + Tian-50 = 450 ROI)
   │
   ▼
BFM backbone (default Brain-JEPA, ABCD ~10,000명 resting state pretrained)
   │  frozen (backbone weight 안 건드림)
   ▼
SSL pretrain (subject-invariant + multi-source masked)
   │  brain 자체 dynamics 학습 (emotion label 안 봄)
   ▼
LoRA adaptation (작은 추가 weight 만 학습)
   │  emotion-specific 적응
   ▼
Projection head (Linear / MLP ablation)
   │
   ▼
z_emo (brain emotion latent, 256-d)
   ↕  InfoNCE contrastive loss
t_emo (emotion-text latent, 768-d)
   │
   ▲
Text encoder (3 후보 ablation, frozen)
- mpnet-base (default, generic semantic)
- CLIP-text ViT-L/14 (vision-language, Cowen evoked-emotion 과 match)
- LEIA-LM-base (emotion-specialized, Aroyehun et al. 2023)
   │
Emotion text ("a video that evokes admiration")
```

**핵심 idea**. 두 거대 model (BFM × emotion-text space) 의 *작은 사이* 만 우리가 학습. 이게 "5 명 데이터로 만든 foundation model" 의 정직한 정의.

### 4.4 2 Main Track + 1 Supplementary

| Track | 답하는 sub-question | 학습 / 측정 |
|---|---|---|
| **Track A (main). BFM SSL pretrain + LoRA adaptation** | Multi-source SSL pretrain 이 emotion-relevant invariance 를 emerge 시키는가? | Pretrain 후 cross-dataset invariance metric (subject alignment, paradigm alignment, ROI-wise transfer) |
| **Track B (main). Brain+Video framework reuse + task 재설계** | Brain unique 의 universal component 가 cross-dataset 으로 preserve 되는가? | Phase 2 framework 그대로 reuse + task 가 V/A 대신 universal code probe |
| **Track C (supplementary). BrainVLM generative** | Universal code 의 generative 표현이 cross-dataset 으로 consistent 한가? | Phase 3a parsing fix + Appendix figure |

Track A + Track B 의 *converging evidence* 가 paper 의 강점.

### 4.5 V4 final 의 핵심 변화 (이전 framing 과의 차이)

| 측면 | 이전 v3 (2026-05-19) | 새 v4 final (2026-06-02) |
|---|---|---|
| Big Q | 4 architecture × 3 encoder 중 best 비교 | Universal emotion code 의 존재 검증 |
| Target hierarchy | V/A 와 34-cat 동등 | V/A 강등 (floor), Cowen 34-cat / 14-dim / OV-text 승격 |
| BrainVLM 위상 | Phase 3a main path | Supplementary (LLM visual bias + 자원 부담) |
| Cross-dataset 전략 | 명확히 없음 | shared text-embedding zero-shot main + 3 보조 |

---

## 5. 앞으로 할 것들

### 5.1 Standard baseline suite (모든 task 의 의무)

새 task 학습 결과의 *맥락* 을 만들기 위한 표준 baseline. 모든 main result 와 *반드시 함께* reporting.

| Baseline | 목적 |
|---|---|
| Chance / Label permutation | Null distribution, p-value |
| Class proportion (majority predictor) | 최소 floor |
| ROI mean + Ridge / Logistic / Multinomial / Multi-output | Linear baseline (task type 별) |
| Random Forest on ROI | Nonlinear baseline |
| Phase 1 best BFM frozen | BFM baseline (no SSL pretrain). V_binary 0.7402 |
| Video baseline (CLIP) | Group-level emotion ceiling. V_binary 0.9708 |

"Baseline 없는 result 는 unreliable" 원칙. Code 는 `code/baselines/baseline_suite.py` 로 일괄.

### 5.2 Phase 3a (Track C). BrainVLM parsing fix

이미 fold 1 학습 완료. Inference 의 XML parsing 만 수정. Appendix supplementary 만.

### 5.3 Phase 3b (Track A main). Multi-source SSL pretrain + LoRA adaptation

**Sub-phase 1 (Horikawa only). Subject-invariant SSL + LoRA adaptation**.
- Subject-invariant contrastive learning. 같은 stim 의 다른 subject 의 brain representation 을 contrastive 로 align.
- 학습 후 subject alignment metric 측정 = sub-claim 3 의 direct evidence.

**Sub-phase 2 (4 dataset). Multi-source masked autoencoder**.
- Horikawa + Emo-FilM + StudyForrest + Affective Videos 통합.
- 450 ROI 중 30% mask → MSE reconstruction.
- Single-source vs multi-source 의 *cross-dataset invariance 차이* = sub-claim 1 의 direct evidence.

**Sub-phase 3. LoRA adaptation + emotion-text alignment**.
- 3 emotion-text encoder × 2 projection head (Linear / MLP) × backbone = ablation grid.
- Cross-dataset evaluation 4 전략.
  1. Shared text-embedding zero-shot retrieval (main)
  2. Label-space intersection probe (안전)
  3. MLLM universal annotator (OV-MER pipeline, local LLM frozen artifact)
  4. RSA / ISC ceiling (label-free)

### 5.4 Phase 3c (Track B main). Brain+Video framework reuse + task 재설계

- Phase 2 의 4 architecture (A/B/C/D joint) 그대로 reuse.
- 단 task 가 V/A 가 아니라 *universal code probe*.
  - Task 1. Cross-dataset emotion-text alignment.
  - Task 2. Same-emotion RDM preservation across datasets.
  - Task 3. ROI-wise universal map.
- Brain-only vs Brain+Video 차이 = universal code 의 *brain-unique* component 의 직접 evidence.

### 5.5 Phase 4 (Synthesis + submission)

- Track A + Track B 통합 표.
- EmoViS branch 결과 통합 검토.
- Paper draft + Infographic + Code release v1.0.
- Submission target.
  - Nat Hum Behav / Nat Commun (universal code 강한 evidence)
  - NeurIPS dataset & benchmark track (multi-source SSL pretrain recipe + 4 cross-dataset 전략 + MLLM artifact release)
  - Imaging Neuroscience (engineering + cross-dataset)
- Paper title 후보 (Bommasani 2021 FM 정의 scale 미달 reviewer bias 회피).
  - "Universal Emotion Code in Naturalistic Brain Data via Multi-source Self-supervised Adaptation"
  - "Transferable Emotion Brain Foundation Model from Naturalistic fMRI"

### 5.6 Phase 5 (Future, post-submission v5)

V4 main 의 universal code 가 first. 그 위에 추가될 2 extension.

```
Brain emotion representation =
    Universal code              (v4 main)
  + Context-conditional         (v5 Extension 1. text-based modulation)
  + Individual differences      (v5 Extension 2. subject embedding + residual)
  + Acquisition noise           (control. ComBat)
```

- **Extension 1. Context-aware emotion (text 형식)**. 영화 subtitle / scene caption 의 text embedding 으로 stimulus 의 context modulation. StudyForrest narrative, Emo-FilM 1 Hz continuous rating 으로 측정.
- **Extension 2. Individual differences**.
  - (a) Subject embedding (TRIBE v2 / Défossez 2023 style)
  - (b) Track A 의 subject-invariant SSL 의 *non-aligned residual* PCA + 행동 metric correlation

---

## 6. Neuro-AI SOTA (2025-2026) 와 우리 프로젝트의 연결

이 section 은 사전 자료 (Notion 의 Neuro-AI SOTA 2025-2026) 의 핵심 SOTA 들과 우리 FEEL 의 *경쟁 / 보완* 관계를 정리.

### 6.1 직접 경쟁 영역 (FEEL 의 차별화 필요)

**(A) Brain Foundation Model (fMRI) 경쟁**.

| SOTA | 우리 FEEL 의 위치 |
|---|---|
| **NeuroSTORM** (Nat Biomed Eng 2026.04). 28.65M frame, 50K+ subj. 4D fMRI volume 직접 학습. 17 진단 task SOTA | FEEL 은 emotion-specialized adaptation. NeuroSTORM 의 backbone 위에 LoRA adaptation 도 가능 (backbone swap ablation). 우리 backbone 후보의 하나. |
| **Brain-Semantoks** (ICLR 2026). Semantic tokenizer + self-distillation. Brain-JEPA 능가 주장 | FEEL 의 default backbone (Brain-JEPA) 직접 비교 대상. Brain-Semantoks 가 우리 backbone ablation 의 candidate. |
| **Brain Harmony** (NeurIPS 2025). 구조 MRI + 기능 fMRI 통합 (1D token). | Modality 통합은 우리 v4 main scope 아니지만 v5 또는 다음 cycle 의 보완. |
| **BrainIAC** (Nat Neurosci 2026.02). 48,965 brain MRI. 자기지도 + 대조학습. | 범용 brain MRI FM. FEEL 의 transfer baseline 으로 활용 가능. |
| **SLIM-Brain** (ICLR 2025). 3% data 로 atlas-free voxel FM. | 데이터 효율적 접근법. FEEL 의 small-data SSL pretrain 과 idea 공유. 참고 가능. |
| **fMRI-LM** (arXiv 2025.11). 3-stage. neural tokenizer → LLM 적응 → instruction tuning. | LLM 정렬 fMRI 이해. FEEL 의 emotion-text alignment 와 idea 공유. 직접 비교 보다는 보완. |

**우리 차별화 포인트**.
- Universal emotion code 라는 *명확한 scientific question* (단순 task accuracy 가 아님).
- Multi-source SSL pretrain 의 invariance 측정 (single vs multi-source 차이).
- 4 cross-dataset evaluation 전략의 표준화 (text-embedding zero-shot + intersection + MLLM annotator + RSA).
- Caption baseline confound control (Doerig 2025 의 LLM-baseline 위협 직접 대응).

### 6.2 보완 영역 (FEEL 이 활용)

**(B) LLM-Brain alignment**.
- **fMRI-LM / NOBEL**. LLM 을 brain signal 해석의 backbone 으로 활용 → FEEL 의 emotion-text alignment recipe 와 idea 공유. Future cycle 에서 활용 가능.
- **Brain2Qwerty** (Meta 2025.02). EEG/MEG 기반 타이핑. Brain-to-text decoding 의 정확도 reference.

**(C) Vision-Language Model for Neuroscience**.
- **NeuroVLM** (bioRxiv 2026.02). 30,000 brain image-text pair. Text-to-neuroimage / neuroimage-to-text 양방향 생성. → FEEL 의 Track C (BrainVLM supplementary) 의 reference.
- **MindBridge** (CVPR 2024 Highlight). Cross-subject brain decoding framework. → Sub-claim 3 (subject-invariant alignment) 의 reference.

**(D) Affect-Contextualized Perception**.
- **Geometric Hyperscanning of Affect Under Active Inference** (IWAI 2025). Active inference 기반 정서 모델 + Forman-Ricci 곡률 기반 inter-brain network. → 우리 협업 2 의 affect-contextualized perception 의 이론적 보완.
- **Mechanistic Interpretability of Emotion Inference in LLMs** (Bana et al. ACL Findings 2025). LLM 내 정서 표현이 특정 영역에 localize. → FEEL 의 *emotion-text space 와 brain 의 alignment* 가 LLM 의 emotion organization 과 어떻게 매핑되는지의 question 으로 연결 가능.
- **MER 2025** (ACM Multimedia 2025). 정서 컴퓨팅 + LLM. Categorical → generative emotion recognition 패러다임 전환. → 우리 cross-dataset 전략 3 (OV-MER pipeline) 의 직접 출처.

**(E) Cross-species 및 시각 피질 FM**.
- **Multiscale Organization of Neuronal Activity** (Cell 2024.10). 5 종에서 보존된 다척도 신경활동. → 종간 보존 구조의 *생물학적 근거*. FEEL 의 universal code 가설의 cross-species 근거.
- **Foundation Model of Neural Activity** (Nature 2025.04). 마우스 시각피질 FM 이 새 자극 / 세포 유형 예측. → FEEL 의 *new dataset 으로 transfer* 의 동물 모델 정밀 reference.

### 6.3 보완 (FEEL 이 활용 + 보완)

**Brain Foundation Model Survey (arXiv 2503.00580)**. 분야 전체 조망.
**Non-Invasive Brain Decoding FM Survey (bioRxiv 2025.11)**. FM 의 표현 / 정렬 / 생성 3 축 분류. FEEL 의 framing 정립에 참고.

### 6.4 핵심 정리

FEEL 의 *우리 lab 만의 contribution* 은 SOTA 와 다른 3 가지 axis.

1. **Scientific question 중심**. "Brain accuracy" 보다 "Universal emotion code 의 존재 여부" 라는 falsifiable scientific claim.
2. **Multi-source SSL pretrain 의 invariance 직접 측정**. Single-source vs multi-source 비교가 evidence 의 핵심.
3. **4 cross-dataset evaluation 전략의 표준화**. Metadata 빈약한 dataset 도 평가 가능한 framework + frozen MLLM annotator artifact release.

---

## 7. 협업 2 에서 우리가 기여할 부분 (텍스트화 + 뇌영상 표현)

### 7.1 우리가 가져올 자산

| 항목 | 출처 | 현재 상태 |
|---|---|---|
| Horikawa 5 subj × 2,185 stim ROI parcel | 우리 lab | ✅ 추출 완료 (Schaefer-400 + Tian-50) |
| Horikawa fMRI 의 BFM frozen embedding | 우리 lab | ✅ Brain-JEPA / SwiFT 6 variants / NeuroSTORM 모두 |
| Cowen 34-cat soft distribution per stim | 외부 (Cowen 2017/2020) | ✅ Horikawa metadata 에 통합 |
| V/A binary / regression subset | 우리 lab | ✅ `data/horikawa_*_binary_subset.csv` |
| 5-fold stim-stratified CV split | 우리 lab | ✅ `data/horikawa_5fold.csv` |
| Cowen 34-cat 의 문장화 텍스트 (예. "a video that evokes admiration") | 우리 lab (FEEL Action 11) | 🆕 진행 예정 |
| Emo-FilM 30 subj × 14 films preprocessing + ROI parcel | 우리 lab (BEACON-T) | 확인 필요 (`beacon_t/data/hdf5/emofilm.py` 와 정합성 점검) |
| 4-dataset OV label (Qwen2.5-72B 또는 Llama-3.3-70B 의 OV-MER pipeline output) | 우리 lab (FEEL Action 15) | 🆕 진행 예정 (협업 2 의 텍스트화 결과로 release 가능) |

### 7.2 협업 2 의 작업 매핑 (FEEL 의 어떤 step 이 협업 2 에 기여하는가)

| 협업 2 작업 | FEEL 의 어떤 action |
|---|---|
| **자극 의미자료화**. 동영상의 장면 / 정서 단서를 텍스트로 | FEEL Action 11 (Cowen 34-cat 의 문장화) + Action 15 (OV-MER local LLM annotator pipeline) |
| **사람 반응 의미자료화**. 정서 평정 / 행동 / 개인차 표준 용어 | FEEL Action 11 의 14-dim 문장화 + 4 dataset 별 행동 metric 정리 (Horikawa V/A + Emo-FilM CPM 50 항목 mapping) |
| **뇌영상 표현 생성**. fMRI 를 TabLeT 또는 다른 표현 모델 입력 | FEEL 의 BFM frozen embedding (Brain-JEPA, SwiFT, NeuroSTORM) 직접 제공 + 학습 후 z_emo 표현 |
| **텍스트 학습자료 생성**. 자극-반응-뇌 데이터 관계 문장 | FEEL Action 11 + 15 의 combined output. "Stim k 에서 Subject A 가 emotion {evoked} 를 felt, brain pattern 은 {z_emo}" 형식 |
| **협업 3 전달**. BEACON-T 평가 명세 | FEEL 의 standard baseline suite (Action 0) + 4 cross-dataset evaluation 전략 → BEACON-T 표준평가에 그대로 활용 |

### 7.3 워크샵에서 결정할 것 (우리 lab 관점)

1. **Horikawa 와 Emo-FilM 중 어떤 데이터를 먼저 텍스트화할지**.
   - 우리 추천. Horikawa 부터 (이미 ROI parcel + 5-fold split 등 인프라 완성). Emo-FilM 은 BEACON-T 의 emofilm.py 와의 정합성 확인 후 W2 부터.
2. **Cowen 34-cat 문장화의 표준 형식**.
   - 우리 추천. "a video that evokes {emotion_name} with intensity {score}" 의 template. Sentence-transformer embedding 직접 가능.
3. **공통 emotion 좌표계**.
   - Horikawa Cowen 34-cat ↔ Emo-FilM 13 discrete + 42 CPM 의 *closest mapping table* 작성 필요. 우리 lab 이 mapping 초안 제공 가능.
4. **TabLeT 와 우리 BFM frozen embedding 의 비교 / 통합 방식**.
   - 옵션 A. TabLeT 가 BFM embedding 위에 추가 압축 단계.
   - 옵션 B. TabLeT 와 BFM 가 parallel benchmark.
   - 우리 추천. 옵션 B 부터 (TabLeT 의 코드 공유 가능 범위 확정 후 옵션 A 검토).
5. **OV-MER pipeline 의 frozen artifact 공동 사용**.
   - 우리 lab 이 만들 4-dataset OV label artifact (Qwen2.5-72B 또는 Llama-3.3-70B) 를 협업 2 의 common asset 으로 제공 가능. Reproducibility 강함 (frozen checkpoint hash 공개).

### 7.4 W30 / W90 실행안 (협업 2 일정)

**워크샵 후 30 일 (2026-07-08). 1 차 학습자료와 뇌영상 표현 생성**.
- Horikawa 의 자극 / 반응 텍스트 자료 생성 (FEEL Action 11 + 15).
- 같은 stim 의 BFM embedding 표 + TabLeT 표현 비교 (병행).
- 텍스트 자료와 뇌영상 표현의 alignment 표 작성.

**워크샵 후 90 일 (2026-09-06). LLM 활용 가능한 정서-뇌 학습자료 v1**.
- 정서 자극 / 반응 텍스트 학습자료 v1 (Horikawa + Emo-FilM 일부).
- 뇌영상 표현 파일 + alignment table.
- 협업 3 의 BEACON-T 평가에 넘길 데이터 명세서 v1.
- FEEL 의 Track A Sub-phase 1 결과 (subject-invariant SSL 의 alignment metric 1차).

---

## 8. 워크샵에서 함께 결정할 것들 (전체 미팅 관점)

1. **MixedEmo vs Emo-FilM vs Horikawa 의 우선순위**. 데이터별 처리 상태가 다름. Horikawa 가 인프라 완성, Emo-FilM 다음, MixedEmo 는 92 명 중 30 명 미완료라 가장 후순위.
2. **자극 설명 / 반응 설명 / 정서 변수 설명의 표준 형식**.
   - 우리 추천 template. "Stim {id} in {dataset}. Visual content: {caption}. Audio: {audio_desc}. Evoked emotion: {Cowen 34-cat distribution} or {Emo-FilM CPM 50 vector}. Subject {id} reported: {V/A or continuous rating}. Brain time-window {start}-{end}s shows pattern {z_emo}."
3. **TabLeT 의 입력 조건과 코드 공유 범위**.
4. **LLM 용 학습자료의 최소 필수 필드**.
5. **협업 리드 학생 1 명 + 30 일 / 90 일 Gantt chart 초안**.
6. **OV-MER frozen artifact 의 release 일정과 권한 (Hugging Face 또는 BEACON-T 의 일부?)**.

---

## 부록 A. Phase 1-2 numeric 결과 (evidence 보존)

### Phase 1 frozen probe (V_binary AUROC, per-subject mean ± std)

| Feature | Init | Padding | Head | Mode | AUROC | n cells |
|---|---|---|---|---|---|---|
| ROI Schaefer400+Tian50 | n/a | time_mean | linear | pooled | **0.7889 ± 0.0119** | 5 |
| ROI Schaefer400+Tian50 | n/a | time_mean | linear | per_subject | 0.7885 ± 0.0263 | 25 |
| Brain-JEPA | resting | zero | linear | per_subject | 0.7402 ± 0.0365 | 25 |
| Brain-JEPA | resting | zero | linear | pooled | 0.7376 ± 0.0194 | 5 |
| NeuroSTORM | resting | mean | linear | per_subject | 0.7292 ± 0.0361 | 25 |
| SwiFT NewE96 | resting | zero | linear | pooled | 0.6884 ± 0.0166 | 5 |
| SwiFT UAH 202M | scratch | zero | linear | per_subject | 0.6911 ± 0.0368 | 25 |
| CLIP_pretrained | n/a | n/a | linear | n/a | **0.9708** | - |

### Phase 2 trained integration (V_binary AUROC)

| Method | Kind | AUROC | Δ vs CLIP |
|---|---|---|---|
| D late fusion (joint) | joint | **0.9718 ± 0.0082** | **+0.001** |
| A token transformer | joint | 0.9670 ± 0.0111 | -0.004 |
| B cross-attention | joint | 0.9663 ± 0.0087 | -0.005 |
| C contrastive joint | joint | 0.9606 ± 0.0084 | -0.010 |
| Brain-only III multitask | brain-only | 0.7235 ± 0.0209 | -0.247 |
| Brain-only II distillation | brain-only | 0.7214 ± 0.0186 | -0.249 |
| Brain-only IV subject-aware | brain-only | 0.7206 ± 0.0172 | -0.250 |
| Brain-only I supervised | brain-only | 0.7165 ± 0.0192 | -0.254 |
| C contrastive (brain only path) | joint | 0.7123 ± 0.0137 | -0.258 |

### Phase 2 다른 task 도 같은 패턴

V_reg Pearson r. A token 0.7628 vs CLIP 0.7645 = -0.002.
A_binary AUROC. D late fusion 0.8025 vs CLIP 0.8003 = +0.002.

**결론**. 4 fusion architecture *모두* video baseline 위로 의미 있는 향상 없음. 이게 v4 framing 의 motivation.

---

## 부록 B. FEEL repo structure (협업 자료 location)

```
/pscratch/sd/s/sjmoon/EmoBrain/         # repo path (이름 유지)
├── README.md                          # FEEL 한 줄 정의 + framing
├── ACTION_PLAN.md                     # week-level action (Phase 3a/3b/3c/4/5)
├── CONTEXT_EMOBRAIN.md                    # agent / 협업자 reference
├── docs/masterplan_v2.md              # forward plan v4 final (Section 6 = Standard baseline suite)
├── data/
│   ├── horikawa_5fold.csv             # CV split
│   ├── stimulus_features/             # EmoViS feature symlinks
│   └── independent/                   # Emo-FilM / StudyForrest / NNDb / Affective Videos (Phase 3b 다운로드)
├── code/
│   ├── baselines/baseline_suite.py    # Standard baseline suite (모든 task 의무)
│   ├── ssl_pretrain/                  # Track A SSL pretrain (Phase 3b)
│   ├── cross_dataset/                 # LoRA adaptation + 4 eval 전략 (Phase 3b)
│   ├── phase2/                        # Phase 2 Brain+Video framework (Track B reuse)
│   └── brainvlm/                      # Phase 3a BrainVLM (Track C supp)
├── output/embeddings/                 # BFM frozen embedding (Brain-JEPA, SwiFT, NeuroSTORM)
├── results/
│   ├── phase1/                        # Phase 1 frozen probe 결과 (위 부록 A)
│   ├── phase2/                        # Phase 2 trained integration 결과
│   ├── brainvlm/                      # Phase 3a fold 1
│   └── phase3_universal_code/         # Phase 3b/3c 결과 (NEW)
├── reports/
│   ├── phase1_wrapup/main.pdf         # Phase 1 보고서 (15 p)
│   └── phase2_wrapup/main.pdf         # Phase 2 보고서
├── figures/feel_architecture.html     # FEEL Track A architecture diagram (4 sub-phase 통합)
└── reference/papers/                  # 주요 reference PDF
    ├── Lian2025_OV-MER.pdf
    ├── Doerig2025_Aligning_representations.pdf
    ├── TRIBE_v2.pdf
    └── ...
```

**GitHub**. `Transconnectome/FEELIN` (branch `v4_20260602_perlmutter`).

---

## 부록 C. 주요 reference (협업 2 관련)

### 우리 lab Phase 1-2 의 근거

- Cowen, Keltner (2017 PNAS). Self-report captures 27 distinct categories of emotion bridged by continuous gradients.
- Cowen, Keltner (2020 Nat Hum Behav). The neural representation of visually evoked emotion is high-dimensional, categorical, and distributed across transmodal brain regions.
- Horikawa, Cowen, Keltner, Kamitani (2020 Cell Reports). The neural representation of visually evoked emotion is high-dimensional, categorical, and distributed.

### Multi-source naturalistic emotion fMRI

- Cordoni et al. (2025 Scientific Data). Emo-FilM. A multimodal dataset for affective neuroscience.
- Aliko, Huang, Gheorghiu, Meliss, Skipper (2020). A naturalistic neuroimaging database (NNDb). Sci Data.
- Hanke et al. (StudyForrest). A high-resolution 7-Tesla fMRI dataset from complex natural stimulation.

### FEEL 의 build recipe 의 근거

- Goh et al. (2024 ICML). Brain-JEPA. Brain Dynamics Foundation Model with Gradient Positioning and Spatiotemporal Masking.
- Caro et al. (2023 NeurIPS). BrainLM. A foundation model for brain activity recordings.
- Fortin et al. (2018 NeuroImage). Harmonization of cortical thickness measurements across scanners and sites (ComBat).
- Aroyehun et al. (2023 EPJ Data Science). LEIA. Linguistic Embeddings for the Identification of Affect.

### Caption baseline 의 위협

- Doerig et al. (2025 Nat Mach Intell). The Semantic Scale of LLMs and brain alignment.
- Conwell et al. (2022/2025). Aligning machine and human visual representations across abstraction levels.

### Cross-dataset 전략의 출처

- Lian et al. (2025 ICML). OV-MER. Towards Open-Vocabulary Multimodal Emotion Recognition.
- Défossez et al. (2023). Decoding speech perception from non-invasive brain recordings (subject embedding).

### Phase 2 측정 결과의 의의 (group-level V/A 의 video saturation)

- Wager et al. (2013 N Engl J Med). An fMRI-based neurologic signature of physical pain (universal signature 시도의 출발).
- Sripada et al. (2020 NeuroImage). Network identification from connectome-wide and beyond. (acquisition confound 의 정량)

### Workshop 사전자료 (Notion) 의 SOTA list

별도 첨부된 "Neuro-AI SOTA 2025-2026" 문서의 7 카테고리 (Brain FM fMRI / EEG FM / Neural Decoding / Cross-species / Affect-Contextualized Perception / VLM for Neuroscience / Calcium Imaging) 의 모든 reference 는 Section 6 의 정리 참고.

---

## 마치는 말

처음 보시는 분들께. FEEL 은 *small data 의 honest scope* 의 emotion brain foundation model 이다. 5 명 × 2,185 stim 으로 from-scratch FM 은 못 만든다. 그래서 두 거대 model (Brain-JEPA × emotion-text space) 사이를 *작은 adaptation* 으로 잇는다.

이 작은 adaptation 의 결과가 *paradigm, subject, label taxonomy 의 surface variation 위에서 보존* 되는지가 universal emotion code 의 직접 evidence 다.

협업 2 의 텍스트화 + 뇌영상 표현 작업은 FEEL 의 *evaluation 표면* 을 만드는 작업이다. 우리가 만든 표면 위에서 BEACON-T 의 표준평가 (협업 3) 가 진행되고, 협업 2 의 텍스트 학습자료가 FEEL 의 emotion-text alignment 의 *new training material* 이 된다.

워크샵에서 만납시다.
