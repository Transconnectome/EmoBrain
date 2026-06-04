# FEEL

**Universal Emotion Code in Naturalistic Brain Data**

(Internal / repo name = Foundation Model for Emotion Embedding Learning. Paper title = "Universal Emotion Code in Naturalistic Brain Data" 또는 "Transferable Emotion Brain Foundation Model".)


## 한 줄 요약

여러 명의 다른 사람이, 여러 종류의 영상을 볼 때 brain 에 공통으로 떠오르는 emotion representation 이 있는지 (universal emotion code) 를 검증하는 project. 다양한 naturalistic emotion fMRI dataset 을 모아 self-supervised learning 으로 학습하고, 그 representation 이 새 dataset / 새 subject / 새 emotion 어휘로도 보존되는지 측정한다.


## Motivation

Affective neuroscience 의 미해결 질문 하나.

> "공포" 라는 emotion 이 brain 에 *universal code* 로 존재하는가, 아니면 각 사람마다, 각 자극마다, 각 paradigm 마다 *다른 representation* 인가?

Wager 의 universal pain signature 시도 (Neurologic pain signature, 2013) 가 통증에 대해 던졌던 질문의 emotion 판이다. Cowen 2020 Nat Hum Behav 는 brain 의 emotion 이 high-dimensional 하고 transmodal region 에 분산됨을 보였지만, *cross-dataset / cross-subject invariance* 는 검증 안 됐다. FEEL 은 그 빈 자리를 채운다.

왜 지금 가능한가. Foundation model 의 multi-source pretrain 방법이 성숙했고, 여러 naturalistic emotion fMRI dataset 이 OpenNeuro 에 공개됐고, sentence-transformer / CLIP-text 같은 emotion-text embedding space 가 사용 가능하다. 셋을 잇는 adaptation recipe 가 universal code 의 measurement device.


## Big Question

> Brain 에 paradigm, label taxonomy, subject 의 surface variation 을 가로지르는 *universal emotion code* 가 존재하는가? Multi-source naturalistic emotion fMRI 의 adaptation 으로 그 universal code 를 학습하고 검증할 수 있는가?


## Sub-claims (falsifiable, 4 개)

학습된 representation 이 다음 4 measurement 를 모두 통과하면 universal code 의 강한 evidence. 일부만 통과하면 partial evidence. 모두 fail 하면 universal code 없음 (negative result paper).

1. **Multi-source pretrain invariance**. Universal code 가 있다면 multi-source pretrain (Horikawa + Emo-FilM + StudyForrest + Affective Videos) 의 representation 이 single-source pretrain (Horikawa only) 보다 cross-dataset transfer 에서 더 invariant.
2. **ROI localization**. Universal code 는 brain 의 특정 ROI / network 에 localize 되어야 함 (Cowen 2020 의 transmodal 가설 비교).
3. **Subject-invariant alignment**. Subject-invariant SSL 학습 후 같은 stimulus 의 다른 subject 의 representation 이 의미 있게 alignment.
4. **Null hypothesis**. 위 셋 모두 acquisition floor 안에 있음 → "universal code 없음, emotion 은 paradigm/context/subject-specific representation" 결론.


## Approach: 3 Track

학습된 representation 을 3 가지 angle 에서 측정해서 triangulated evidence 를 만든다.

| Track | 답하는 질문 | Main / Supp |
|---|---|---|
| **A** | Multi-source self-supervised pretrain 이 emotion-relevant invariance 를 자연스럽게 emerge 시키는가? | Main |
| **B** | Brain unique contribution (video 가 못 잡는 부분) 의 universal component 가 cross-dataset 으로 preserve 되는가? | Main |
| **C** | Universal code 의 generative 표현이 cross-dataset 으로 consistent 한가? | Supplementary |

Track A 와 Track B 의 결과가 *converge* 하면 universal code 의 강한 evidence. Track C 는 BrainVLM 의 generative output 으로 보조 evidence 만 제공 (자원 부담 + LLM visual bias 때문에 main 아님).


## Build Recipe (5 block)

5 subject × 2185 stimulus 로는 emotion brain foundation model 을 from-scratch pretrain 불가. **Pretrained brain backbone + 소수 multi-source SSL pretrain + emotion-text embedding space adaptation** 이 honest scope.

```
fMRI ─► [A] 450-ROI parcel (Schaefer-400 + Tian-50)
        │
        ▼ [B] Brain backbone (default Brain-JEPA, swap axis SwiFT / NeuroSTORM)
        │
        ▼ [C] Track A SSL pretrain
            (1) Subject-invariant contrastive  ← priority 1
            (2) Multi-source masked AE          ← priority 1
            (3) Brain-stimulus contrastive      ← priority 2
        │
        ▼ [D] LoRA adaptation
        │
        ▼ [E] frozen emotion-text embedding space (sentence-transformer / CLIP-text)
        │
        ▼ multi-source pooling
        ▼ evaluation. Tasks + Cross-dataset 4 strategies
```

### Block A. 450-ROI parcel input

- **Schaefer-400 17-network + Tian-50 subcortical** = 450 ROI mean time series
- 이유. Dataset / scanner / TR 이 달라도 같은 ROI 정의 → cross-dataset 통합의 substrate. 4D volume (SwiFT, NeuroSTORM) 도 비교 axis 로 유지하지만 default 는 ROI

### Block B. Brain backbone

| 후보 | 입력 | 상태 | 역할 |
|---|---|---|---|
| **Brain-JEPA** (default) | 450 ROI | 추출 완료 | Block B default. ABCD resting 으로 pretrained. 작은 LoRA adapter 로 emotion-specialized reshape |
| **SwiFT** (NewE96 + 5 변종) | 4D volume | NewE96 완료, 변종 진행 중 | Backbone swap 비교 |
| **NeuroSTORM** | 4D volume | 추출 완료 | Backbone swap 비교 |
| BrainLM | 제외 | 490 TR × A424 atlas 고정 → Horikawa 비호환 | scope 제외 |

**왜 Brain-JEPA 가 default 인가**. ROI 입력이라 cross-dataset substrate 와 잘 맞음. Pretrained on ABCD (수만 subject) 라 prior 강함. JEPA-style latent prediction objective 가 SSL pretrain 의 다음 stage 와 호환. 단 confirmation 은 Track A 의 backbone ablation 에서.

### Block C. Track A SSL pretrain (5 후보, priority 순)

#### (1) Subject-invariant SSL (priority 1, main)

**무엇을 하나**. 같은 stimulus 를 본 여러 subject 의 brain response 가 서로 비슷한 representation 으로 mapping 되도록 contrastive 학습.

**왜**. "Universal" 의 첫 번째 의미는 subject-invariance. 만약 같은 video 를 본 subject A 와 subject B 의 brain representation 이 학습 후 cosine ~ 1 이 된다면, *subject 의 surface variation 위에서 보존되는 emotion code 가 brain 에 있다* 의 직접 evidence.

**어떻게 (구체적 loss)**.
- Triplet (stim_k, subj_A, subj_B). Anchor = brain_Ak, positive = brain_Bk, negative = brain_Am (다른 stim).
- InfoNCE loss. `L = -log(exp(sim(brain_Ak, brain_Bk) / τ) / Σ_m exp(sim(brain_Ak, brain_Am) / τ))`
- τ = temperature (0.07 default, ablation 0.05-0.5)
- Hard negative sampling (closest non-matching stim 우선)
- Backbone freeze, projection head + LoRA 만 학습

**Expected outcome**.
- 학습 후 subject-pair cosine 가 random baseline 보다 의미 있게 증가
- 증가 폭이 transmodal ROI (STS, TPJ, mPFC) 에서 가장 큼 (Cowen 2020 가설)
- Sub-claim 3 의 직접 evidence

**자원**. GPU A100 × 2-3 일.

#### (2) Multi-source masked autoencoder (priority 1, main, BrainLM-style)

**무엇을 하나**. 4 dataset (Horikawa + Emo-FilM + StudyForrest + Affective Videos) 의 fMRI 를 모두 모으고, brain 의 일부 ROI 의 활동을 가린 후 나머지로 가린 부분을 *재구성* 하도록 학습.

**왜**. "Universal" 의 두 번째 의미는 paradigm-invariance. Multi-source pretrain 후 representation 이 single-source pretrain 보다 cross-dataset transfer 에서 더 invariant 하면, *paradigm 의 surface variation 위에서 보존되는 brain dynamics 의 invariant 구조* 가 있다는 evidence.

**어떻게 (구체적 loss)**.
- 450 ROI 중 30% mask (random 또는 spatially structured)
- Backbone forward → masked ROI 의 activity 예측
- MSE reconstruction loss
- 4 dataset 같은 model. Dataset 별 token embedding (header) 으로 dataset identity 만 표시
- Per-batch dataset 비례 sampling
- Single-source baseline (Horikawa only) 와 ablation 비교

**Expected outcome**.
- Multi-source pretrain 의 cross-dataset Pearson r > Single-source pretrain Pearson r (의미 있는 차이)
- Sub-claim 1 의 직접 evidence

**자원**. GPU A100 × 1-2 주 (4 dataset × 학습 epoch).

#### (3) Brain-stimulus contrastive, TRIBE-style (priority 2, main 가능하면)

**무엇을 하나**. Brain representation 과 video representation (V-JEPA2 / CLIP / DINOv2 로 추출한 stim feature) 을 같은 latent space 로 alignment.

**왜**. Universal code 가 stimulus-driven (즉 stim 의 어떤 abstract attribute 의 brain 표상) 이면 brain ↔ stimulus alignment 가 자연스럽게 emerge. Brain unique 가 stim 과 분리된 axis (e.g. subjective experience) 라면 alignment 안 됨. 두 경우의 분리가 universal code 의 *origin* 을 알려준다.

**어떻게**.
- Brain encoder output (z_brain_k) ↔ V-JEPA2 feature (z_stim_k) 의 cosine ↑
- 다른 stim 과는 ↓
- InfoNCE contrastive (Brain-stim pair)
- V-JEPA2 는 EmoViS 의 추출본 reuse (data/stimulus_features/ symlink)

**Expected outcome**.
- Brain ↔ stimulus alignment 가 emerge 하면 "universal code 의 일부가 stim-driven"
- Alignment 가 약하면 "brain unique 가 stim 과 분리"
- 두 결과 모두 paper 의 contribution

**자원**. GPU A100 × 2-3 일.

#### (4) Curriculum pretrain (priority 3, optional)

**무엇을 하나**. 3-stage 학습. Stage 1 = resting state SSL (Brain-JEPA 의 ABCD prior, 이미 한 stage), Stage 2 = naturalistic movie SSL (HCP 7T movie 같은 long-form data), Stage 3 = emotion-aware fine-tune (Horikawa).

**왜**. Universal code 의 prior 가 어느 stage 에서 emerge 하는지 ablation. Resting → movie 가 stage gap 크니까, 중간 stage 가 universal code 의 emergence 에 critical 한지 확인.

**자원**. GPU 1-2 주.

#### (5) Distillation (priority 3, optional)

**무엇을 하나**. 큰 BFM (Brain-JEPA full) 의 representation 을 작은 specialized model 로 transfer. Teacher 의 output 을 student 가 imitate.

**왜**. Universal code 의 *효율적 표현* 방법. Inference cost 줄이기 위한 보조.

**자원**. GPU 며칠.

### Block D. LoRA adaptation

- SSL pretrain 후 backbone 위에 LoRA (rank 8-16) 추가
- Backbone freeze, LoRA 만 학습
- Loss = (Block E 의 emotion-text contrastive) + (보조 V/A regression + Cowen 34-cat regression + 14-dim regression)

### Block E. Emotion-text embedding space

- **Sentence-transformer (mpnet-base, frozen)** 또는 **CLIP-text (ViT-L/14, frozen)** 의 text embedding space 를 emotion 의 universal space 로 사용
- Cowen 34-cat 의 각 emotion 을 문장으로 변환. 예. "A video that evokes admiration", "A video that evokes contempt"
- Cowen 14-dim 도 동일 방식
- OV description (Track A 의 strategy 3 의 출력) 도 같은 space 로
- 모든 emotion target 이 같은 text space 의 vector 로 표현 → cross-dataset / cross-taxonomy 의 unified target


## Tasks (we design new ones, V/A 가 아님)

Phase 1-2 의 측정에서 group-level V/A 가 video 에 의해 saturate 됨을 확정했다 (CLIP 0.97 vs brain best 0.74). 따라서 universal code 의 evidence 는 V/A 가 아닌 *invariance / cross-dataset preservation* 의 axis 에서 측정해야 한다. 다음 5 가지 새 task 를 우리가 직접 설계한다.

### Task 1. Cross-dataset emotion-text alignment retrieval

- **Input**. 다른 dataset (Emo-FilM, StudyForrest, NNDb) 의 stimulus 에 대한 brain response
- **Method**. Trained encoder (Block B + C + D) 로 brain → emotion-text space 사영. Target dataset 의 native label (어떤 어휘든) 도 같은 text space 에 embedding. Cosine similarity 로 retrieval
- **Metric**. Top-1 / top-5 accuracy, mean reciprocal rank, top-1 vs random baseline
- **Expected outcome**. Universal code 가 있다면 native label retrieval 이 random 보다 의미 있게 높음

### Task 2. Same-emotion RDM preservation (cross-dataset RSA)

- **Input**. Horikawa 와 Emo-FilM 에서 *같은 emotion label* (예. fear) 로 라벨된 stimulus 의 brain response
- **Method**. 각 dataset 의 brain RDM 계산 (Schaefer-400 ROI-wise). Cross-dataset RDM correlation (Spearman r)
- **Metric**. RDM correlation, FDR-corrected p value, ROI 별 distribution
- **Expected outcome**. Universal code 가 있는 ROI 에서 cross-dataset RDM correlation 이 의미 있게 high

### Task 3. ROI-wise universal map

- **Input**. 4 dataset 의 fMRI + 학습된 encoder
- **Method**. Schaefer-400 의 각 ROI 별로 Sub-claim 1-3 의 metric 계산. ROI 가 모두 통과하면 *universal code 의 candidate location*
- **Metric**. ROI 별 universal-code score (composite of multi-source invariance + subject alignment + cross-dataset RDM preservation)
- **Expected outcome**. Universal code 가 transmodal / DMN region 에 localize (Cowen 2020 가설) 또는 다른 분포 발견

### Task 4. Subject-alignment metric (post Track A SSL)

- **Input**. 같은 stimulus 의 다른 subject 의 brain (Horikawa 5 subj × 2185 stim)
- **Method**. Track A 의 (1) subject-invariant SSL 학습 전/후 의 subject-pair cosine similarity 비교
- **Metric**. Mean cosine pre vs post, paired bootstrap p
- **Expected outcome**. Subject-invariant SSL 후 subject alignment 가 의미 있게 증가하면 universal code 의 subject-invariance evidence

### Task 5. Caption-baseline brain unique variance (confound control)

- **Input**. Stimulus 의 Qwen-VL caption + caption 의 sentence-transformer text embedding (B_caption) + brain encoder output (B_brain)
- **Method**. Variance partitioning. (a) Caption-only probe 의 emotion prediction performance, (b) Brain-only probe, (c) Joint probe. Brain unique variance = Joint - Caption.
- **Metric**. Brain unique r², paired bootstrap p value
- **Expected outcome**. Brain unique variance > 0 이면 "brain 에 caption embedding 으로 설명되지 않는 emotion-specific 정보 있음" (Doerig 2025 의 LLM-baseline 위협 통과)


## Cross-dataset Evaluation: 4 Strategies

다른 dataset (Emo-FilM, StudyForrest, NNDb 등) 은 emotion label taxonomy 가 모두 다르다 (13-discrete vs 8-emotion vs label-free). 같은 representation 으로 평가하려면 4 가지 전략을 조합.

### Strategy 1. Shared text-embedding zero-shot retrieval (main)

**무엇**. Trained encoder 로 brain → emotion-text space 로 사영. 새 dataset 의 native label 도 같은 text space 에 embedding. Retrieval.

**왜 main**. 어떤 dataset 의 어떤 label 도 *학습 없이* 평가 가능. Universal code 의 transfer 의 가장 직접적 측정.

**구체 flow**.
1. Brain encoder freeze (Track A + D 학습 끝)
2. Target dataset 의 stim → brain → encoder → z_brain
3. Target dataset 의 native label (예. Emo-FilM 의 13 discrete emotions) → sentence-transformer → z_label
4. argmax_label cos(z_brain, z_label) = predicted label

**Metric**. Top-1 / top-5 accuracy, mean reciprocal rank, vs random chance baseline + acquisition null baseline.

**Expected outcome**. Universal code 가 있다면 random + null 보다 의미 있게 높음.

### Strategy 2. Label-space intersection (safe sanity)

**무엇**. Target dataset 의 axis 만 잘라서 평가. 가장 보수적, reviewer-friendly.

**왜**. Universal code 의 핵심 axis 가 정확히 cross-dataset 으로 보존되는지 직접 측정. 어휘 mismatch 위험 제거.

**구체**.
- Emo-FilM 의 13 discrete + 42 CPM 항목 중 Cowen 34-cat 과 *직접 mapping 가능한 axis 만* 선택 (예. fear, anger, sad)
- Within-dataset Pearson r 또는 balanced accuracy
- StudyForrest 의 V/A 도 동일 방식

**Metric**. Within-dataset r / accuracy, ComBat 적용 전후 비교.

**Expected outcome**. Cross-dataset axis 에서 transfer r > 0 + acquisition null 의 2σ 위.

### Strategy 3. MLLM universal annotator (frozen artifact)

**무엇**. OV-MER (Lian 2025 ICML) 의 label generation pipeline 을 local LLM (Qwen2.5-72B-VL 또는 Llama-3.3-70B-VL) 으로 frozen artifact 화. 모든 dataset 의 stim 에 같은 open-vocabulary label 부여.

**왜**. Dataset 마다 label space 가 다른 문제를 *통일된 LLM-generated label space* 로 우회. Cross-dataset 비교의 universal annotator.

**구체 flow**.
1. Local LLM (Qwen2.5-72B-VL) 으로 stim video → CLUE-Multi description 생성
2. 같은 LLM 으로 CLUE-Multi → open-vocabulary emotion label set (평균 3-5 개)
3. Generated label artifact 를 Hugging Face dataset 으로 release (hash 명시, reproducibility 보장)
4. 모든 dataset 에 적용 → 같은 OV label space 공유
5. Brain → emotion-text space → OV label set 의 retrieval (set-based F-score)

**Metric**. Set-based F-score (OV-MER 의 metric), cross-dataset OV label agreement.

**왜 GPT-3.5 안 쓰는가**. OV-MER 의 원본 pipeline 은 GPT-3.5 API. Deprecation 위험 + reproducibility 감점. Local LLM 으로 frozen 시키면 영구 보존.

### Strategy 4. Representational alignment, label-free (NNDb)

**무엇**. Stimulus matching 만 있으면 label 없이 가능. NNDb 의 86 subject × 10 movies (라벨 없음) 같은 데이터셋에 적용.

**왜**. Label 이 없는 large dataset 도 universal code 의 evidence 로 사용 가능 (sample size 확장).

**구체**.
- Brain RDM (subject × stim) 계산
- Stim 에 대한 video feature (V-JEPA2 / CLIP) RDM 과의 RSA
- Subject 간 brain signal 의 ISC (inter-subject correlation) → noise ceiling

**Metric**. RDM correlation (Spearman r), ISC.

**Expected outcome**. Universal code 가 있는 ROI 에서 cross-subject brain RDM 의 일관성 + stim feature 와의 RSA.


## Statistical Validation (Critic-informed control, 필수)

3 가지 control 을 모든 cross-dataset 결과에 의무 적용.

### 1. Acquisition control (ComBat + null baseline)

- **ComBat harmonization** (Fortin et al. 2018 NeuroImage). Dataset / scanner / TR / atlas 의 nuisance 변동을 제거. Site = dataset, covariate = age / sex / TR.
- **Acquisition null baseline** 2 종.
  - (a) **Phase-scrambled brain signal**. Brain time series 의 spectral statistics 유지하되 emotion 관련 structure 제거 → 같은 pipeline 으로 학습 / 평가 → chance ceiling
  - (b) **Trivial ROI mean encoder**. Acquisition mismatch 만 통과하는 trivial model → acquisition floor
- **2σ rule**. Transfer Δ 가 max(null) 의 2σ 이상일 때만 의미 있다고 *prespecify* (post-hoc 안 함)
- **이유**. Sripada et al. 2020 NeuroImage 는 cross-dataset connectome transfer 의 60-70% variance 가 acquisition 으로 설명됨을 보고. Control 없으면 universality claim 의 대부분이 noise

### 2. Caption baseline (Task 5)

- 위 "Tasks" 의 Task 5 와 동일
- 모든 brain-only universality claim 의 confound control 로 의무 적용

### 3. Subject-level bootstrap CI

- 모든 metric 은 5 subject 의 bootstrap (1000 resampling) 으로 95% CI 보고
- Single point estimate 안 함 (5 subject power 부족 인정)


## Independent Datasets

| Dataset | Subj × Stim | Label | Role |
|---|---|---|---|
| **Horikawa** | 5 × 2185 (1 min clips) | Cowen 34-cat behavioral consensus | Base, Track A pretrain source, Track B testbed |
| **Emo-FilM** (Cordoni 2025 Nat SciData) | 30 × 14 films (2.5h) | 13 discrete + 42 CPM, 1 Hz | Multi-source pretrain + transfer test |
| **StudyForrest** | 20 × Forrest Gump 2h | 8 portrayed emotion + V/A | Multi-source pretrain + transfer test |
| **NNDb** (Aliko 2020) | 86 × 10 movies | 없음 (label-free) | Strategy 4 RSA |
| **Affective Videos** (ds000205) | 11 × 32×4 trials | V/A | Multi-source pretrain |
| **Koide-Majima** | (옵션) | 80 emotion labels | Multi-source pretrain (접근 가능 시) |


## Target Hierarchy

| Tier | Target |
|---|---|
| **Primary** | Cross-dataset emotion-text alignment + Cowen 34-cat multilabel + Cowen 14-dim regression + OV description retrieval |
| **Reference (floor)** | V/A binary + V/A continuous regression |

V/A 는 Phase 1-2 에서 video CLIP 이 saturate 함이 확정 (CLIP V_binary 0.971). 따라서 floor / sanity check 로만 사용.


## Measured Results (Phase 1-2, framing 의 evidence)

### Phase 1 (frozen probe)

- ROI Schaefer400+Tian50 mean (linear, pooled). V_binary AUROC 0.7889 ± 0.0119
- Best BFM. Brain-JEPA resting zero (linear). V_binary 0.7402 ± 0.0365
- Best video. CLIP_pretrained. V_binary 0.9708
- **결론**. ROI mean > all BFM. Brain backbone 정교화 (SwiFT 5M~264M, padding 4 mode, 2 init) 가 V/A 에 effect 없음.

### Phase 2 (trained integration, 4 architecture × 4 brain-only method)

| Method | V_binary AUROC | A_binary | V_reg r |
|---|---|---|---|
| **Video CLIP only (Phase 1)** | **0.9708** | 0.8003 | 0.7645 |
| D late fusion (joint) | 0.9718 | 0.8025 | - |
| A token transformer (joint) | 0.9670 | 0.7919 | 0.7628 |
| B cross-attention (joint) | 0.9663 | 0.7863 | - |
| C contrastive joint | 0.9606 | 0.7699 | - |
| Brain-only best (multitask) | 0.7235 | 0.6645 | 0.2296 |

**결론**. Joint - Video baseline = +0.001 (noise). 4 fusion architecture 어느 것도 video baseline 위로 의미 있게 향상 못 함. Brain 의 group-level emotion label 추가 contribution = 0.

### Phase 3a (BrainVLM)

Fold 1 학습 완료 (loss 1.94 → 0.151). Inference V_reg r = NaN (XML parsing failure 의심), MAE 2.55 (V) / 2.81 (A). Scale mismatch (prompt 1-5 vs Cowen 1-9). **Track C supplementary 로 demote**.

### 의의 (왜 universal code framing 으로 갔는가)

Group-level V/A 는 video 가 saturate. Brain unique signal 은 다음 4 축에서만 가능하다.
1. Multi-dim emotion geometry (Cowen 34-cat / 14-dim)
2. Transmodal ROI localization
3. Subject-conditioned variability
4. Cross-dataset / cross-taxonomy preservation

이 4 축의 공통 motif = **invariance**. Universal emotion code 가 그 invariance 의 scientific 표현. v4 final 의 Track A + Track B 가 이 4 축을 측정.


## Phase Status

| Phase | Track | 상태 |
|---|---|---|
| Phase 1 Foundation (frozen probe + SwiFT padding ablation + 6 SwiFT variants) | (사전 검증) | ✅ 완료 |
| Phase 2 통합 학습 (4 architecture A/B/C/D + brain-only 4 method + Cat34 task) | (사전 검증) | ✅ 측정 완료. Universal code framing 으로 pivot |
| Phase 3a BrainVLM | Track C supp | 🔄 Fold 1 완료, parsing fix 추가 |
| **Phase 3b** Track A (SSL pretrain + LoRA adaptation) | Track A main | 🆕 v4 main path |
| **Phase 3c** Track B (Brain+Video framework + task 재설계) | Track B main | 🆕 v4 main path (병행) |
| Phase 4 Synthesis + submission | (통합) | 대기 |
| Phase 5 **Future Extensions** (Context-aware text modulation + Individual differences) | v5 candidates | 🔮 추후 |

자세한 phase 별 weekly action 은 [`ACTION_PLAN.md`](ACTION_PLAN.md).
Forward plan + go-no-go + agent review = [`docs/masterplan_v2.md`](docs/masterplan_v2.md).
Phase 1 결과. [`reports/phase1_wrapup/main.pdf`](reports/phase1_wrapup/main.pdf).
Phase 2 결과. [`reports/phase2_wrapup/main.pdf`](reports/phase2_wrapup/main.pdf).
Decision log. [`notes/project_decisions.md`](notes/project_decisions.md).


## Git Workflow

- 현재 active branch = `v4_20260602_perlmutter`
- 새 framing 으로 pivot 필요하면 새 branch (`v5_YYYYMMDD_perlmutter`)
- Paper 단계에서 main 으로 merge


## Repository Map

```
FEEL/
├── 7 root .md (README, README_KR, CONTEXT_FEEL, ONBOARDING, CLAUDE, CODEX, ACTION_PLAN)
├── docs/masterplan_v2.md              # Forward plan v4 final (Big Q, sub-claim, tracks, go-no-go)
├── Paper/framework_{EN,KR}.md         # Canonical narrative
├── Paper/methodology.md               # Canonical experimental methods
├── reports/
│   ├── phase{1,2}_wrapup/main.pdf     # Phase wrap-up papers
│   ├── phase1_foundation.md
│   ├── ppt_slides.md + ppt_slides_figs/
│   └── {reviews, status}/
├── weekly/                            # Weekly tracking (unified)
│   ├── 2026-06-01/{plan, checkins, results, wrapup}.md
│   ├── README.md, TEMPLATE
├── data/
│   ├── stimulus_features/             # EmoViS symlinks (V-JEPA2, CLIP, DINOv2, VideoMAE, Qwen-VL)
│   ├── independent/ (NEW)             # Emo-FilM, StudyForrest, NNDb, Affective Videos (OpenNeuro)
│   └── {horikawa_split, canonical_stimuli}.csv
├── code/
│   ├── bfm_embeddings/                # BFM extraction
│   ├── probes/                        # Phase 1 unified frozen probe
│   ├── phase2/                        # Phase 2 4 architecture + brain-only (Track B reuse)
│   ├── brainvlm/                      # Phase 3a (Track C supp)
│   ├── ssl_pretrain/ (NEW, Track A)   # Subject-invariant + multi-source masked + brain-stimulus
│   ├── cross_dataset/ (NEW)           # LoRA, emotion-text space, ComBat, evaluators, OV-MER local LLM
│   └── analysis/                      # Figures, ablation
├── output/embeddings/                 # BFM .pt (proper mean)
├── results/                           # Probe / training 결과
├── baseline/                          # BFM checkpoints
├── external/                          # Vendored model code
├── reference/
│   ├── papers/                        # PDF (Lian2025_OV-MER, Doerig2025, TRIBE_v2, Processing_fMRI, arxiv_2604.03619v1)
│   ├── {datasets, papers, task, training_strategy, code_resources}.md
│   └── v4_history_labserver_framing.md
├── notes/{benchmark_design, project_decisions}.md
├── scripts/                           # Utility (check_md_completeness, build_project_status)
├── templates/                         # Card templates (experiment_card, paper_note, etc.)
├── _archive/                          # Legacy versions
└── workflows/                         # Operating workflow
```
