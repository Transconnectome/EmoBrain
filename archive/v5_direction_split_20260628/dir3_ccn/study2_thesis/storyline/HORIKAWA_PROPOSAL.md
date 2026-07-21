# Track 1 Proposal: Emotion Representation Structure in Horikawa Dataset

**Target:** NeurIPS Workshop paper (UniReps / NeuroAI)
**Date:** 2026-04-19
**Status:** v1 proposal

---

## 0. Executive Summary

인간 뇌의 감정 표상 구조를 **label-free, multi-level, tri-axial** 관점에서 체계적으로 characterize한다. Horikawa (2020) dataset의 2185개 감정 비디오 반응을 (a) V-JEPA2 foundation model의 factor-region alignment로, (b) sparse autoencoder (SAE)로 discovery되는 compositional components로, (c) Gromov-Wasserstein Optimal Transport (GW-OT)를 이용한 brain-stimulus-behavior 삼각 구조 비교로 분석한다. 언어적 감정 범주를 분석 target이 아닌 post-hoc interpretation으로만 사용함으로써, 기존 range-bound categorical/dimensional framework의 한계를 우회한다.

---

## 1. Background and Motivation

### 1.1 Emotion neuroscience의 현재 상태

감정 뇌과학은 크게 다음 프레임워크들에 의존한다:

**범주적 프레임워크 (Categorical):**
- Ekman 6 basic emotions, Cowen & Keltner 27 emotions
- "Fear", "joy", "disgust" 등 언어적 범주를 뇌 신호의 ground truth로 사용
- Decoding target = emotion labels
- 대표 연구: Horikawa et al. 2020 (iScience), Kragel & LaBar 2015

**차원적 프레임워크 (Dimensional):**
- Russell's circumplex: valence × arousal 2D
- Barrett's core affect + conceptualization
- Decoding target = continuous dimensions
- 대표 연구: Du et al. 2023 (iScience), Posner et al.

**계산적 프레임워크 (Computational):**
- Scherer appraisal theory: goal-relevance, control, certainty 등
- Reinforcement learning 기반 emotion computation
- 대표 연구: Moors et al. 2013, "Emotions as computations" 2022

### 1.2 공통 한계

위 프레임워크들은 공통적으로 **언어적/행동적 범주를 뇌 신호의 ground truth로 간주**한다:
- 감정 label을 decoding target으로 사용
- RSA model RDM을 label similarity 기반으로 구성
- Brain region 해석을 emotion 이름으로 labeling

그러나:
1. **언어적 범주 (joy, fear)는 descriptive framework** — 인간이 서로 소통하기 위해 만든 구조
2. **뇌가 실제로 감정을 이 범주대로 structure한다는 보장 없음** — correlate해도 동치 아님
3. **범주 경계가 fuzzy하고 문화 의존적** — 번역에서 1-to-1 대응 안 되는 경우 많음
4. **Novelty 한계** — 언어 label로 분석하면 언어 구조를 반복하여 발견할 뿐

### 1.3 최근 돌파구의 징후

2024-2025에 label-free 접근의 개척적 연구가 등장:

- **Jang & Kragel 2025 (J Neurosci)**: Amygdala를 DNN으로 encoding한 후 deep image synthesis로 **감정 label 없이** amygdala subregion별 선호 자극 생성
- **Lee et al. 2025 (Communications Psychology)**: CEBRA로 awe의 ambivalent neural representation을 label 없이 발견
- **Takeda et al. 2025 (iScience)**: Gromov-Wasserstein Optimal Transport로 cross-individual brain representation alignment — 자극 label 불필요
- **Sartzetaki et al. 2025 (ICLR)**: Video foundation model factor-region alignment를 systematic 분석 (BMD dataset, action domain)
- **Ferrante et al. 2025 (Communications Biology)**: "Brain Algebra" — fMRI visual representation이 compositional 구조

**공통점:** 언어적 범주를 분석 출발점으로 삼지 않고 뇌 구조를 직접 characterize.

**문제점:** 감정 영역에 대한 **체계적, multi-level, whole-brain** label-free characterization 미존재.

---

## 2. Research Question

### 2.1 Main Research Question

> **"감정 자극에 대한 인간 뇌의 표상은 언어적 감정 범주와 독립적으로 characterize했을 때 어떤 구조를 드러내며, 이 구조는 자극 표상 (video foundation model) 및 행동적 감정 평가와 어떻게 대응하는가?"**

### 2.2 Sub-questions

**SQ1 — Factor-region alignment (representation 1st layer):**
Video foundation model (V-JEPA2)의 서로 다른 factor들 (layer depth, temporal vs spatial encoding, semantic abstraction level)이 뇌의 서로 다른 emotion-related region과 어떻게 align하는가? 이 alignment 패턴은 감정 유형에 따라 어떻게 달라지는가?

**SQ2 — Compositional components (representation 2nd layer):**
뇌의 감정 관련 활동을 sparse overcomplete decomposition (SAE)으로 분해하면 어떤 compositional components가 발견되는가? 서로 다른 언어적 감정 범주가 이 components 공간에서 어떻게 표현되는가 — pure single component? 여러 component의 superposition?

**SQ3 — Tri-axial structural alignment:**
세 축 — Brain (fMRI), Stimulus (V-JEPA2 features), Behavior (48 emotion ratings) — 의 표상 기하학이 Gromov-Wasserstein Optimal Transport로 비교했을 때 어떻게 대응하는가? 어디서 구조가 일치하고 어디서 어긋나는가? 이 divergence는 특정 감정 유형에 편향되는가?

**SQ4 — Emotion space geometry:**
Factor-region mapping과 component decomposition에서 발견되는 latent space에서 언어적 감정 범주들이 어떻게 배치되는가? Cluster? Continuous gradient? Compositional 조합? 기존 Cowen 27-emotion 구조와 어떻게 관계하는가?

---

## 3. Research Gap

### 3.1 What is known

**Factor-region alignment (visual domain):**
- Sartzetaki et al. 2025 (ICLR): 99 video models의 layer-wise factor × 17 visual ROI RSA (BMD dataset, action recognition). **Finding: temporal modeling이 early visual cortex alignment의 핵심**, action classification이 late visual에 중요.
- Khosla et al. 2021 (Science Advances): multiscale features + temporal integration이 visual cortex 예측 향상.
- Conwell et al. 2022/2024: image model 비교, 데이터 다양성이 representational alignment의 가장 큰 요인.

**Compositional brain representation (visual domain):**
- Ferrante et al. 2025 (Communications Biology): fMRI visual representation이 algebraic composition 가능 — "skateboard + winter = snowboard in winter scene". **Emotion words**도 일부 테스트 (happy/sad). Static image concepts.
- "Neural population geometry and optimal coding of tasks with shared latent structure" (Nat Neurosci 2025): 공유 latent structure를 가진 task들의 기하학적 속성 분석.
- Kragel 2019 (Sci Adv): EmoNet CNN이 뇌의 emotion schema와 대응.

**Cross-domain alignment:**
- Takeda et al. 2025 (iScience): Gromov-Wasserstein으로 NSD dataset 8 subjects 간 brain representation alignment — label 없이 unsupervised. **Brain-brain alignment만**.
- Thual et al. 2025 (J Neurosci Methods): Neuroscience용 GW-OT toolbox 공개.

**Horikawa dataset:**
- Horikawa et al. 2020 (iScience): 34 category decoding, distributed across transmodal regions.
- Du et al. 2023 (iScience): Affective space의 topographic representation, PCA 기반.

### 3.2 What is missing

위 선행을 종합하면 다음이 공백:

1. **감정 영역에 대한 factor-region alignment** — Sartzetaki는 action recognition (BMD). Emotion 특화 factor-region 분석 없음.

2. **감정 fMRI에 sparse autoencoder 적용** — LLM interpretability (Anthropic, OpenAI) 분야에서 SAE가 monosemantic features를 발견하는 데 성공. 뇌 데이터 적용은 제한적이며 **감정 fMRI에 적용된 사례 없음**.

3. **Brain-Stimulus-Behavior tri-axial 구조 비교** — Takeda는 brain-brain (cross-individual). Stimulus representation + brain + behavior 세 축을 동시에 GW-OT로 비교한 연구 없음.

4. **Multi-level label-free framework** — 개별 선행은 단일 수준 (factor OR components OR alignment). 세 수준을 통합하여 감정 표상을 characterize한 연구 없음.

### 3.3 Gap statement (한 줄)

> 감정 뇌과학에서 label-free multi-level (factor / components / tri-axial) 표상 characterization framework가 부재하며, 기존 연구는 단일 수준이거나 visual / action domain에 제한됨.

---

## 4. Hypotheses

### H1 — Factor-region differentiation in emotion domain
Video foundation model의 서로 다른 factor (low-level temporal, mid-level spatial, deep semantic)가 서로 다른 emotion-related brain region과 systematic하게 align한다.

**Specific prediction:**
- Low-level temporal factor (V-JEPA2 early layers, <0.3 depth): 초기 visual cortex (V1-V3), 일부 subcortical (superior colliculus, pulvinar)와 높은 alignment
- Mid-level spatial factor (V-JEPA2 mid layers, 0.3-0.7): Occipital-temporal cortex (LOC, FFA, PPA)
- Deep semantic factor (V-JEPA2 late layers, >0.7): Transmodal regions (STS, TPJ, DMN, vmPFC)

**Falsifiable:** Uniform alignment across all factors-regions, or no layer-dependent structure.

### H2 — Emotion-specific factor profile
감정 유형마다 dominant factor profile이 다르다. 감각 reactive emotion과 contextual/cognitive emotion이 factor level에서 구별된다.

**Specific prediction:**
- Disgust, surprise, fear: low-to-mid level factor dominant (fast sensory-driven)
- Joy, awe, nostalgia, aesthetic appreciation: deep/semantic factor dominant (requires integration)
- Anger: mixed profile (sensory + social context)

**Falsifiable:** All emotions show identical factor profile, or random distribution.

### H3 — Compositional brain emotion representation (SAE)
SAE로 decompose했을 때 뇌의 감정 관련 활동이 sparse compositional components로 표현된다. 언어적 감정 범주는 이 components의 조합 패턴이다.

**Specific prediction:**
- Meaningful SAE features ~100-300 개 (K=2000 initial, most inactive)
- 각 feature = 특정 brain parcel 조합 + 특정 video 유형 활성 profile
- 감정 간 component 공유 존재 — 예: disgust와 fear가 "threat feature" 공유, joy와 awe가 "positive valuation feature" 공유
- 일부 감정 = pure (적은 component), 일부 = compound (많은 component의 superposition)

**Falsifiable:** SAE components가 noise 수준 또는 uninterpretable. 감정 간 component 공유 없음 (각 감정 = 고유 feature set).

### H4 — Tri-axial structural correspondence
Brain, Stimulus (V-JEPA2 latent), Behavior (48 emotion ratings) 세 공간의 표상 구조가 GW-OT로 비교했을 때 partial alignment를 보인다.

**Specific prediction:**
- Brain ↔ Stimulus GW distance < Brain ↔ Behavior GW distance (stimulus는 직접 입력, behavior는 사후 해석)
- Divergence 지점 (pattern mismatch)가 특정 감정에 편향 (예: awe, empathic pain 등 subjective/contextual emotion)
- Layer-wise V-JEPA2 GW-OT가 specific layer에서 peak alignment (neither too early nor too late)

**Falsifiable:** GW distance가 chance 수준. Alignment가 감정 편향 없이 uniform.

### H5 — Pure vs compound emotion dichotomy
일부 감정 (sensory reactive)은 적은 수의 components로 표현되는 "pure" 감정. 다른 감정 (contextual/abstract)은 많은 components의 superposition인 "compound" 감정.

**Specific prediction:**
- Pure emotion 후보: disgust, fear, surprise (sensory-reactive, low-level factor dominant)
- Compound emotion 후보: awe (positive + dread), empathic pain (self + other), nostalgia (present + past)
- Compound emotion이 Lee et al. 2025 (Awe CEBRA)와 일관된 ambivalent neural structure를 보임

**Falsifiable:** 모든 감정이 균일한 component 개수로 표현됨.

---

## 5. Methodology

### 5.1 Data

**Horikawa 2020 dataset:**
- 5 subjects × 2185 unique videos × 450 parcels
- 각 video = 3초
- Parcellation: Schaefer 400 cortical + 50 subcortical (Tian atlas)
- Emotion annotation: 34 category + 14 affective dimension = 48 target (Cowen & Keltner 2017 protocol)
- 전처리 완료, V-JEPA2 features (32 layers) 이미 추출
- Audio: video에 포함 (optional Whisper extraction)

### 5.2 Emotion-relevant ROI grouping

450 parcels을 emotion-related functional networks로 그룹:

- **Subcortical (Tian S3):** amygdala (subregions: LB, CM, SF), hippocampus, insula (anterior/posterior), thalamus, striatum, superior colliculus
- **Limbic cortex:** subgenual cingulate, orbitofrontal cortex, vmPFC
- **Default Mode Network (DMN):** medial prefrontal, posterior cingulate, angular gyrus
- **Social-emotional networks:** STS, TPJ, FFA, EBA
- **Sensory (for control):** V1-V4, auditory cortex
- **Dorsal/salience:** dorsal anterior cingulate, anterior insula, parietal operculum

### 5.3 Method explanations

---

#### 5.3.1 Representational Similarity Analysis (RSA)

**Intuition:**
두 시스템 (뇌와 모델)이 같은 자극을 어떻게 표상하는지 비교하려 한다. 직접 비교는 불가능 — 차원이 다르고 좌표 해석이 다르다. 하지만 "자극 A와 자극 B가 얼마나 유사한가"라는 **pairwise similarity**는 공통 지표.

RSA는 이 insight를 활용:
1. 각 시스템에서 N개 자극의 pairwise similarity matrix (RDM; Representational Dissimilarity Matrix) 계산
2. 두 RDM을 correlation (Spearman 또는 Pearson)으로 비교
3. 높은 상관 = 두 시스템이 자극을 유사하게 구조화함

**Math:**

For brain ROI with voxel vectors $v_s$ for subject $s$ and N videos:
$$B_s[i,j] = 1 - r(v_s^{(i)}, v_s^{(j)})$$
where $r$ is Pearson correlation.

For model layer $l$ with feature vectors $f_l$:
$$M_l[i,j] = 1 - r(f_l^{(i)}, f_l^{(j)})$$

Alignment score:
$$R_l^{(s)} = \rho(B_s, M_l)$$
where $\rho$ is Spearman correlation of vectorized RDMs.

**Noise ceiling:**
- Upper noise ceiling: 각 subject RDM을 mean RDM과 correlation (상한)
- Lower noise ceiling: leave-one-out (하한)
- Model score는 noise ceiling로 normalize해서 "percentage of explainable variance"로 해석

**Application in SQ1:**
각 emotion ROI × V-JEPA2 layer pair에 대해 RSA 계산. Factor-region alignment map 생성.

---

#### 5.3.2 Sparse Autoencoder (SAE)

**Intuition:**
뇌의 activity pattern을 decompose하여 해석 가능한 "feature" 혹은 "concept"을 찾는다. PCA는 principal components를 찾지만 dense하고 해석 어려움. SAE는 overcomplete하고 sparse하게 만들어서 각 feature가 한 개념만 담도록 (monosemantic).

**LLM interpretability 맥락:**
Bricken et al. (Anthropic 2023), Cunningham et al. (OpenAI 2024)가 SAE를 LLM activation에 적용하여 "dog", "tuesday", "Golden Gate Bridge" 같은 구체적 concept features 발견. SAE는 overcompleteness와 sparsity가 결합되어 monosemantic한 dictionary 학습을 유도.

**Architecture:**
Input: $x \in \mathbb{R}^D$ (D = 450 parcels)
Bottleneck: $z \in \mathbb{R}^K$ with $K \gg D$ (예: K = 2000)
Output: $\hat{x} = W_d z$

$$z = \text{TopK}(W_e x + b)$$

where TopK keeps only the K_active largest activations (e.g., K_active = 30).

**Loss:**
$$\mathcal{L} = \|x - \hat{x}\|_2^2 + \lambda \|z\|_1$$

L1 penalty encourages sparsity; TopK enforces hard sparsity.

**Interpretation per feature:**
For feature $k$:
- Brain map: decoder weight $W_d[:, k] \in \mathbb{R}^{450}$ → spatial pattern
- Video activation profile: $\{z_k^{(i)}\}_{i=1}^{2185}$ → what stimuli activate this
- Emotion correlation: correlate $z_k^{(i)}$ with each of 48 emotion ratings
- Stability: check consistency across subjects

**Application in SQ2:**
Train SAE on Horikawa fMRI (2185 × 450). Discover K_active ~100-300 meaningful features. Analyze:
- Each emotion category의 average component activation profile
- Pure (few active components) vs compound (many components) emotions
- Shared components across emotions (e.g., "threat feature" activated by both fear and disgust)

---

#### 5.3.3 Gromov-Wasserstein Optimal Transport (GW-OT)

**Intuition:**
두 공간 (e.g., 뇌와 자극)이 서로 다른 차원이라 직접 비교 불가. 하지만 각 공간 내부의 pairwise 거리 구조는 비교 가능. GW-OT는 "한 공간의 거리 구조를 다른 공간의 거리 구조로 얼마나 잘 mapping할 수 있는가"를 측정.

비유: 서울 지하철 노선도와 도쿄 지하철 노선도. 좌표는 다르지만 "역 간 거리 관계"로 구조적 유사도 비교 가능. GW-OT가 "강남역 ↔ 시부야역" 같은 대응을 자동 발견.

**Formal setup:**
Space X (예: brain): points $\{x_1, ..., x_n\}$ with distance matrix $D_X \in \mathbb{R}^{n \times n}$
Space Y (예: stimulus): points $\{y_1, ..., y_m\}$ with distance matrix $D_Y \in \mathbb{R}^{m \times m}$

**Objective:**
Find coupling matrix $T \in \mathbb{R}_+^{n \times m}$ (transport plan) minimizing:
$$\mathcal{L}(T) = \sum_{i,j,k,l} |D_X[i,j] - D_Y[k,l]|^q T_{ik} T_{jl}$$

Subject to marginal constraints: $T \mathbf{1}_m = \mu$, $T^\top \mathbf{1}_n = \nu$ (mass conservation).

Parameter $q = 2$ typically.

**Key properties:**
- **Label-free**: no external correspondence needed
- **Structure-preserving**: preserves pairwise distances
- **Interpretable**: T provides soft correspondence between points
- **Symmetric**: GW(X, Y) = GW(Y, X)

**GW distance (scalar):**
$$GW(X, Y) = \min_T \mathcal{L}(T)^{1/q}$$

Low GW distance = two spaces have similar intrinsic structure.

**Transport plan T:**
$T_{ij}$ = probability mass transported from point $i$ in X to point $j$ in Y. Soft correspondence.

**Entropic regularization (for computation):**
Exact GW-OT is NP-hard. Practical implementations use entropic regularization:
$$\mathcal{L}_\epsilon(T) = \mathcal{L}(T) - \epsilon H(T)$$
where $H(T) = -\sum_{ij} T_{ij} \log T_{ij}$ is entropy.

Solved via Sinkhorn-like iterations.

**Neuroscience application (Thual et al. 2025, Takeda et al. 2025):**
- Brain A와 Brain B의 structural alignment
- Stimulus representation과 brain alignment

**Tri-axial extension (novel in our work):**
Three spaces:
- $D_{brain}$ (2185 × 2185): brain pattern distances
- $D_{stim}$ (2185 × 2185): V-JEPA2 feature distances
- $D_{behav}$ (2185 × 2185): emotion rating distances

Three pairwise GW-OT:
1. $GW(brain, stim)$, $T_{bs}$
2. $GW(brain, behav)$, $T_{bb}$
3. $GW(stim, behav)$, $T_{sb}$

Per-video warping score:
$$w_i^{(bs)} = \sum_j |D_{brain}[i,j] - D_{stim}[\sigma(i), \sigma(j)]|$$
where $\sigma$ is most likely correspondence from $T_{bs}$.

High warping = brain structure at video $i$ diverges from stimulus structure.

**Application in SQ3, SQ4:**
- GW distances quantify tri-axial structural similarity
- Transport plans reveal which videos map to which
- Warping scores identify emotion-specific divergences
- Layer-wise GW-OT (per V-JEPA2 layer) identifies which processing level best matches brain

**Implementation:**
- POT (Python Optimal Transport) library
- Thual et al. 2025 neuroscience toolbox
- Entropic regularization with epsilon tuning
- Bootstrap for confidence intervals

---

#### 5.3.4 Brain Algebra test (compositional algebra)

**Intuition (Ferrante et al. 2025):**
If brain representations are compositional, then arithmetic combinations of representation vectors should produce meaningful new representations. Similar to word2vec's famous "king - man + woman = queen".

**Method:**
1. For emotion category $c$, compute mean brain pattern:
$$\bar{b}_c = \frac{1}{|V_c|} \sum_{v \in V_c} b_v$$

2. Define arithmetic hypothesis:
$$\bar{b}_{c_1} + \bar{b}_{c_2} \approx \bar{b}_{c_3}?$$

Example: $\bar{b}_{joy} + \bar{b}_{sad} \approx \bar{b}_{bittersweet}?$

3. Test via:
- Distance: $\|\bar{b}_{c_1} + \bar{b}_{c_2} - \bar{b}_{c_3}\|$ vs chance
- Decoding: does predicted $\bar{b}_{c_3}$ classify as $c_3$ videos?

**Systematicity test:**
If multiple composition rules hold across many emotion triples, this supports algebraic structure.

**Application in SQ2:**
Extend Ferrante's static visual concept test to evoked emotion responses on Horikawa videos.

---

### 5.4 Analysis pipeline summary

```
Pipeline:

Step 1: Feature extraction
  - V-JEPA2 32-layer features on 2185 videos
  - Aggregation: temporal pooling within each 3s video

Step 2: Brain preprocessing
  - Schaefer 450 parcellation (done)
  - Trial averaging across repetitions
  - Optional: CEBRA task-specific latent (for SAE comparison)

Step 3: Analysis 1 — Factor-region RSA (SQ1, H1-H2)
  - 17 emotion ROI × 32 layer RSA
  - Permutation significance
  - Noise ceiling
  - Emotion-specific subset RSA

Step 4: Analysis 2 — Tri-axial GW-OT (SQ3, H4)
  - Compute D_brain, D_stim (per layer), D_behav
  - Pairwise GW-OT with entropic regularization
  - Per-video warping scores
  - Layer-wise GW distance

Step 5: Analysis 3 — SAE components (SQ2, H3, H5)
  - Train SAE on brain (2185 × 450)
  - Extract K_active meaningful features
  - Per-feature: brain map, activation profile, emotion correlation
  - Pure/compound classification per emotion

Step 6: Analysis 4 — Brain Algebra test (SQ2, H3)
  - Systematic arithmetic tests across emotion pairs
  - Compare: disgust + fear, joy + surprise, etc.

Step 7: Analysis 5 — Emotion geometry (SQ4, H5)
  - Plot emotion centroids in SAE component space
  - Compare with Cowen 27-emotion semantic space
  - Cluster vs gradient structure

Step 8: Integration
  - Cross-analysis: factor-aligned regions vs SAE component regions
  - Tri-axial alignment × compositional structure
```

---

## 6. Expected Outcomes

### Workshop paper (4-8 pages) core findings

1. **Factor × emotion region alignment map** — which V-JEPA2 factors align with which emotion-relevant brain regions
2. **Emotion-specific factor profiles** — disgust/fear vs joy/awe 다른 factor dependence
3. **Tri-axial structural similarity** — Brain-Stim-Behav 삼각 GW-OT 정량화
4. **Sparse compositional components** — K_active meaningful features per emotion
5. **Pure/compound emotion classification** — Lee 2025 Awe finding을 전체 감정으로 확장

### If all hypotheses supported

"감정 뇌 표상이 factor-region 수준에서 systematic organization을 보이고, compositional components로 분해 가능하며, stimulus-behavior 공간과 tri-axial alignment를 형성함. 범주적 감정은 component 조합의 특정 영역으로 emerge."

### Fallback narratives
- H1 부분 성공: Factor-region mapping이 emotion region에 uniform — "emotion encoding은 factor-independent" (의미 있는 negative)
- H3 실패: SAE components가 interpretable하지 않음 — compositional 가설 기각, 다른 decomposition 필요
- H4 실패: Tri-axial alignment가 chance — "감정에서 brain, stimulus, behavior는 구조적으로 독립" (surprising finding)

---

## 7. Key References (detailed)

### 7.1 Direct precedents

**Sartzetaki et al. 2025 (ICLR)**
— "One hundred neural networks and brains watching videos: Lessons from alignment"
— 99 video models × 10 subjects × BMD dataset (action recognition)
— Factor-region RSA framework, classical 방법 (raw voxel, Spearman RDMs)
— Finding: temporal modeling → early visual, action task → late visual
— **우리가 확장하는 것:** Emotion domain, 우리 Horikawa dataset, 우리는 SAE + GW-OT 결합

**Ferrante et al. 2025 (Communications Biology)**
— "Evidence for compositionality in fMRI visual representations via Brain Algebra"
— Static visual concept의 algebraic 조합, NSD dataset
— "Winter + skateboard = snowboard in winter" 같은 arithmetic test
— 일부 emotion words (happy/sad) 포함
— **우리가 확장하는 것:** Evoked emotion responses (not concept words), V-JEPA2 latent space, 체계적 emotion-specific testing

**Takeda et al. 2025 (iScience)**
— "Unsupervised alignment reveals structural commonalities and differences in neural representations of natural scenes across individuals and brain areas"
— GW-OT 기반 cross-individual brain alignment, NSD dataset
— 발견: 초기 visual 영역은 잘 align, RSC/MTL은 덜
— **우리가 확장하는 것:** Brain-brain에서 Brain-Stimulus-Behavior 삼각으로

**Horikawa et al. 2020 (iScience)**
— "The neural representation of visually evoked emotion is high-dimensional, categorical, and distributed across transmodal brain regions"
— 우리 데이터셋의 원 논문
— 34 category를 decoding target으로 사용 (label-based)
— 27 distinct cluster 발견 (Cowen 17과 align)
— **우리가 다르게:** Label-free approach, multi-level analysis, V-JEPA2 modern feature

### 7.2 Methodological foundations

**Bricken et al. 2023 (Anthropic)**
— "Towards monosemanticity: decomposing language models with dictionary learning"
— SAE를 LLM에 적용하여 해석 가능한 features 발견
— Overcomplete (K >> D), sparse, monosemantic
— **방법론 import** — 우리는 이를 fMRI emotion에 first-application

**Cunningham et al. 2024 (OpenAI)**
— "Scaling and evaluating sparse autoencoders"
— SAE scaling laws, evaluation metrics
— TopK SAE, BatchTopK 변형
— **Technical reference**

**Thual et al. 2025 (Journal of Neuroscience Methods)**
— "Unsupervised alignment in neuroscience: Introducing a toolbox for Gromov-Wasserstein optimal transport"
— GW-OT neuroscience-specific implementation
— Python toolbox 공개
— **직접 사용할 tool**

**Schneider et al. 2023 (Nature) — CEBRA**
— "Learnable latent embeddings for joint behavioural and neural analysis"
— Contrastive learning for neural latent
— Self-supervised or label-informed
— **Alternative baseline** for SAE comparison

### 7.3 Theoretical background

**Cowen & Keltner 2017 (PNAS)**
— "Self-report captures 27 distinct categories of emotion bridged by continuous gradients"
— 2185 video 감정 분류 체계 구축 — 우리 데이터의 annotation 원천
— **이론적 baseline** (우리는 이 범주를 post-hoc reference로만)

**Kragel & LaBar 2016 (Trends in Cognitive Sciences)**
— "Decoding the nature of emotion in the brain"
— Categorical vs dimensional emotion debate in fMRI
— **이론적 맥락**

**Meta AI 2025 — V-JEPA2**
— "V-JEPA 2: Self-supervised video models enable understanding, prediction and planning"
— 1M+ hours video, self-supervised, 32 layers
— Algonauts 2025 우승 TRIBE의 backbone
— **Stimulus encoder**

### 7.4 Secondary references

- Kragel et al. 2019 (Sci Adv) — EmoNet precedent
- Jang & Kragel 2025 (J Neurosci) — Amygdala label-free encoding
- Lee et al. 2025 (Comms Psych) — Awe CEBRA, ambivalent emotion
- Du et al. 2023 (iScience) — Affective space topography
- Wang/Kragel/Satpute 2026 (Nat Comms) — Emotion knowledge maps

---

## 8. Risks and Mitigation

### 8.1 Methodological risks

**Risk:** SAE components가 noise일 가능성 (n=5 + 감정 data 작음)
**Mitigation:**
- Multiple random seeds training
- Cross-subject consistency check
- Simulation: random data에 SAE 돌려서 null distribution 비교
- Fallback: SAE 대신 ICA 사용

**Risk:** GW-OT computational cost (O(N²) × 3 pairs)
**Mitigation:**
- Entropic regularization with POT library (efficient Sinkhorn)
- Subset videos (예: most reliable 1500) if needed
- GPU acceleration

**Risk:** Factor-region alignment가 TRF 계층 재발견에 그침 (기존 지식)
**Mitigation:**
- Emotion-specific analysis에 집중 (H2)
- Per-emotion profile 차이가 novelty
- Tri-axial alignment (SQ3)가 TRF 넘어선 부분

### 8.2 Theoretical risks

**Risk:** "Sartzetaki emotion replication" 인상
**Mitigation:**
- Multi-level framework (factor + components + tri-axial)
- SAE + GW-OT은 Sartzetaki 없는 것
- Emotion-specific finding 강조

**Risk:** Brain Algebra (Ferrante)와 너무 유사
**Mitigation:**
- Evoked response (not concept static)
- V-JEPA2 latent space anchor
- Tri-axial framework

### 8.3 Data risks

**Risk:** n=5 통계 power 제약
**Mitigation:**
- Group-level analysis primary
- Individual-level as supplementary
- Noise ceiling normalization
- Bootstrap confidence intervals

---

## 9. Novelty Statement (workshop submission 준비)

> "We present the first systematic multi-level, label-free characterization of human brain's emotion representation. Using Horikawa et al. 2020's dataset of 2185 emotional videos, we combine (a) V-JEPA2 foundation model factor-region alignment following Sartzetaki et al. 2025's framework but extended to emotion domain, (b) Sparse Autoencoder decomposition — Anthropic-style dictionary learning applied to emotion fMRI for the first time, and (c) Tri-axial Gromov-Wasserstein Optimal Transport across Brain, Stimulus, and Behavior representation spaces — extending Takeda et al. 2025's brain-brain GW-OT framework. Results reveal [emotion-specific factor profiles / compositional component structure / tri-axial divergence map, depending on actual outcomes], supporting [or challenging, depending] a label-free understanding of brain's emotion organization."

---

## 10. Target Venue

**Primary:** NeurIPS 2026 UniReps workshop
- Representation alignment 주제 특화
- Multi-system (brain, AI model, behavior) alignment perfect fit
- 4-8 page format

**Secondary:** NeurIPS 2026 NeuroAI workshop
- Brain × AI 교차
- V-JEPA2 사용 정당화

**Deadline:** NeurIPS 2026 workshop 제출 ~August 2026
**우리 timeline:** June까지 paper draft, August까지 polish

---

## 11. References

### Direct precedents (positioning)

1. **Sartzetaki, C., Roig, G., Snoek, C.G.M., & Groen, I.I.A.** (2025). One hundred neural networks and brains watching videos: Lessons from alignment. *International Conference on Learning Representations (ICLR 2025)*. https://openreview.net/forum?id=LM4PYXBId5

2. **Ferrante, M., Boccato, T., & Toschi, N.** (2025). Evidence for compositionality in fMRI visual representations via Brain Algebra. *Communications Biology*, 8, 942. https://doi.org/10.1038/s42003-025-08706-4

3. **Takeda, K., Abe, K., Kitazono, J., & Oizumi, M.** (2025). Unsupervised alignment reveals structural commonalities and differences in neural representations of natural scenes across individuals and brain areas. *iScience*, 28, 112298. https://doi.org/10.1016/j.isci.2025.112298

4. **Horikawa, T., Cowen, A.S., Keltner, D., & Kamitani, Y.** (2020). The neural representation of visually evoked emotion is high-dimensional, categorical, and distributed across transmodal brain regions. *iScience*, 23(5), 101060. https://doi.org/10.1016/j.isci.2020.101060

5. **Du, C., Fu, K., Li, J., & He, H.** (2023). Topographic representation of visually evoked emotional experiences in the human cerebral cortex. *iScience*, 26(6), 106842. https://doi.org/10.1016/j.isci.2023.106842

### Method foundations

6. **Bricken, T., Templeton, A., Batson, J., et al.** (2023). Towards monosemanticity: Decomposing language models with dictionary learning. *Anthropic Transformer Circuits Thread*. https://transformer-circuits.pub/2023/monosemantic-features

7. **Cunningham, H., Ewart, A., Riggs, L., Huben, R., & Sharkey, L.** (2024). Sparse autoencoders find highly interpretable features in language models. *International Conference on Learning Representations (ICLR 2024)*.

8. **Gao, L., la Tour, T.D., Tillman, H., et al.** (2024). Scaling and evaluating sparse autoencoders. *OpenAI Technical Report*. https://cdn.openai.com/papers/sparse-autoencoders.pdf

9. **Thual, A., Benchetrit, Y., Geilert, F., et al.** (2025). Unsupervised alignment in neuroscience: Introducing a toolbox for Gromov-Wasserstein optimal transport. *Journal of Neuroscience Methods*, 415, 110369. https://doi.org/10.1016/j.jneumeth.2025.110369

10. **Peyré, G., Cuturi, M., & Solomon, J.** (2016). Gromov-Wasserstein averaging of kernel and distance matrices. *International Conference on Machine Learning (ICML 2016)*, PMLR 48:2664-2672.

11. **Schneider, S., Lee, J.H., & Mathis, M.W.** (2023). Learnable latent embeddings for joint behavioural and neural analysis. *Nature*, 617, 360-368. https://doi.org/10.1038/s41586-023-06031-6

12. **Kriegeskorte, N., Mur, M., & Bandettini, P.** (2008). Representational similarity analysis — connecting the branches of systems neuroscience. *Frontiers in Systems Neuroscience*, 2:4. https://doi.org/10.3389/neuro.06.004.2008

13. **Nili, H., Wingfield, C., Walther, A., Su, L., Marslen-Wilson, W., & Kriegeskorte, N.** (2014). A toolbox for representational similarity analysis. *PLoS Computational Biology*, 10(4), e1003553. https://doi.org/10.1371/journal.pcbi.1003553

### Video foundation models

14. **Assran, M., Duval, Q., Misra, I., et al.** (2025). V-JEPA 2: Self-supervised video models enable understanding, prediction and planning. *arXiv preprint arXiv:2506.09985*. https://arxiv.org/abs/2506.09985

15. **d'Ascoli, S., Deruelle, A., Joubert, C., et al.** (2026). TRIBE v2: A trimodal foundation model for fMRI prediction. *arXiv preprint arXiv:2507.22229*.

### Related emotion neuroscience

16. **Cowen, A.S., & Keltner, D.** (2017). Self-report captures 27 distinct categories of emotion bridged by continuous gradients. *Proceedings of the National Academy of Sciences*, 114(38), E7900-E7909. https://doi.org/10.1073/pnas.1702247114

17. **Kragel, P.A., & LaBar, K.S.** (2015). Multivariate neural biomarkers of emotional states are categorically distinct. *Social Cognitive and Affective Neuroscience*, 10(11), 1437-1448. https://doi.org/10.1093/scan/nsv032

18. **Kragel, P.A., & LaBar, K.S.** (2016). Decoding the nature of emotion in the brain. *Trends in Cognitive Sciences*, 20(6), 444-455. https://doi.org/10.1016/j.tics.2016.03.011

19. **Kragel, P.A., Reddan, M.C., LaBar, K.S., & Wager, T.D.** (2019). Emotion schemas are embedded in the human visual system. *Science Advances*, 5(7), eaaw4358. https://doi.org/10.1126/sciadv.aaw4358

20. **Jang, G., & Kragel, P.A.** (2025). Understanding human amygdala function with artificial neural networks. *Journal of Neuroscience*, 45(18), e1436242025. https://doi.org/10.1523/JNEUROSCI.1436-24.2025

21. **Lee, J., Han, D.D., Oh, S.Y., & Cha, J.** (2025). Awe is characterized as an ambivalent affect in the human behavior and cortex. *Communications Psychology*, 3, 123. https://doi.org/10.1038/s44271-025-00299-2

22. **Wang, Y., Kragel, P.A., & Satpute, A.B.** (2026). Map-like representations of emotion knowledge in hippocampal-prefrontal systems. *Nature Communications*, 17, 68240. https://doi.org/10.1038/s41467-025-68240-z

23. **Kragel, P.A., & LaBar, K.S.** (2019). The role of the default mode network in discrete emotion. *NeuroImage*.

### Vision-brain alignment (comparable methodology)

24. **Khosla, M., Murty, N.A.R., & Kanwisher, N.** (2021). A highly selective response to food in human visual cortex revealed by hypothesis-free voxel decomposition. *Science Advances*, 7(43), eabh0098.

25. **Conwell, C., Prince, J.S., Kay, K.N., Alvarez, G.A., & Konkle, T.** (2022/2024). What can 1.8 billion regressions tell us about the pressures shaping high-level visual representation in brains and machines? *Nature Communications*, 15, 53147. https://doi.org/10.1038/s41467-024-53147-y

26. **Conwell, C., Graham, D., Konkle, T., Alvarez, G.A., & Vessel, E.A.** (2025). The perceptual primacy of feeling: Affectless visual machines explain a majority of variance in human visually evoked affect. *Proceedings of the National Academy of Sciences*.

27. **Wang, A.Y., Kay, K., Naselaris, T., Tarr, M.J., & Wehbe, L.** (2023). Better models of human high-level visual cortex emerge from natural language supervision with a large and diverse dataset. *Nature Machine Intelligence*, 5, 1415-1426. https://doi.org/10.1038/s42256-023-00753-y

28. **St-Yves, G., Allen, E.J., Wu, Y., Kay, K., & Naselaris, T.** (2023). Brain-optimized deep neural network models of human visual areas learn non-hierarchical representations. *Nature Communications*, 14, 3329. https://doi.org/10.1038/s41467-023-38674-4

29. **Sucholutsky, I., Muttenthaler, L., Weller, A., et al.** (2023). Getting aligned on representational alignment. *arXiv preprint arXiv:2310.13018*.

### Theoretical background

30. **Russell, J.A.** (1980). A circumplex model of affect. *Journal of Personality and Social Psychology*, 39(6), 1161-1178.

31. **Barrett, L.F.** (2017). The theory of constructed emotion: an active inference account of interoception and categorization. *Social Cognitive and Affective Neuroscience*, 12(1), 1-23.

32. **Lindquist, K.A., Wager, T.D., Kober, H., Bliss-Moreau, E., & Barrett, L.F.** (2012). The brain basis of emotion: a meta-analytic review. *Behavioral and Brain Sciences*, 35(3), 121-143. https://doi.org/10.1017/S0140525X11000446

33. **Scherer, K.R.** (2001). Appraisal considered as a process of multilevel sequential checking. *Appraisal processes in emotion: Theory, methods, research*, 92(120), 57.

### Secondary references

34. **Chen, D., & He, H.** (2022). Brain-JEPA: Brain dynamics foundation model with gradient positioning and spatiotemporal masking. *Advances in Neural Information Processing Systems (NeurIPS 2024)*. https://arxiv.org/abs/2409.19407

35. **Tang, J., LeBel, A., Jain, S., & Huth, A.G.** (2023). Semantic reconstruction of continuous language from non-invasive brain recordings. *Nature Neuroscience*, 26, 858-866. https://doi.org/10.1038/s41593-023-01304-9

36. **Glasser, M.F., Coalson, T.S., Robinson, E.C., et al.** (2016). A multi-modal parcellation of human cerebral cortex. *Nature*, 536(7615), 171-178.

37. **Schaefer, A., Kong, R., Gordon, E.M., et al.** (2018). Local-global parcellation of the human cerebral cortex from intrinsic functional connectivity MRI. *Cerebral Cortex*, 28(9), 3095-3114.

### Extended bibliography (comprehensive literature review)

#### Emotion neuroscience — foundational

38. **Hamann, S.** (2012). Mapping discrete and dimensional emotions onto the brain: controversies and consensus. *Trends in Cognitive Sciences*, 16(9), 458-466. *→ Foundational theoretical debate: categorical vs dimensional emotion in brain*

39. **Barrett, L.F., & Satpute, A.B.** (2013). Large-scale brain networks in affective and social neuroscience: towards an integrative functional architecture of the brain. *Current Opinion in Neurobiology*, 23(3), 361-372. *→ Functional architecture framework for emotion-related networks*

40. **Pessoa, L.** (2017). A network model of the emotional brain. *Trends in Cognitive Sciences*, 21(5), 357-371. *→ Network-based emotion theory, supports transmodal distribution*

41. **Roy, M., Shohamy, D., & Wager, T.D.** (2012). Ventromedial prefrontal-subcortical systems and the generation of affective meaning. *Trends in Cognitive Sciences*, 16(3), 147-156. *→ vmPFC in affective value encoding*

42. **Nummenmaa, L., Hari, R., Hietanen, J.K., & Glerean, E.** (2018). Maps of subjective feelings. *Proceedings of the National Academy of Sciences*, 115(37), 9198-9203. *→ Subjective feeling space structure, 100 feelings organized*

43. **Saarimäki, H., Gotsopoulos, A., Jääskeläinen, I.P., Lampinen, J., Vuilleumier, P., Hari, R., Sams, M., & Nummenmaa, L.** (2016/2018). Distributed affective space represents multiple emotion categories across the human brain. *SCAN*, 13(5), 471-482. *→ Distributed emotion representations across cortex*

#### Semantic and visual mapping

44. **Huth, A.G., de Heer, W.A., Griffiths, T.L., Theunissen, F.E., & Gallant, J.L.** (2016). Natural speech reveals the semantic maps that tile human cerebral cortex. *Nature*, 532(7600), 453-458. *→ Semantic atlas precedent, relevant for semantic factor analysis*

45. **Popham, S.F., Huth, A.G., Bilenko, N.Y., Deniz, F., Gao, J.S., Nunez-Elizalde, A.O., & Gallant, J.L.** (2021). Visual and linguistic semantic representations are aligned at the border of human visual cortex. *Nature Neuroscience*, 24(11), 1628-1636. *→ Visual-linguistic semantic alignment, relevant for SAE component interpretation*

46. **Margulies, D.S., Ghosh, S.S., Goulas, A., Falkiewicz, M., Huntenburg, J.M., Langs, G., et al.** (2016). Situating the default-mode network along a principal gradient of macroscale cortical organization. *Proceedings of the National Academy of Sciences*, 113(44), 12574-12579. *→ Principal gradient anchor for "transmodal" regions in emotion*

47. **Lettieri, G., Handjaras, G., Ricciardi, E., Leo, A., Papale, P., Betta, M., Pietrini, P., & Cecchetti, L.** (2019). Emotionotopy in the human right temporo-parietal cortex. *Nature Communications*, 10, 5568. *→ Emotion topography — direct precedent for emotion region organization*

#### Emotion-specific neural networks

48. **Liu, R., Kim, T., & Phan, K.L.** (2024). Emergence of emotion selectivity in deep neural networks trained to recognize visual objects. *PLOS Computational Biology*, 20(3), e1011943. *→ Emotion selectivity emerges in object-trained DNNs — critical context for our V-JEPA2 application*

49. **Bio-Inspired Deep Neural Network Models for Visual Emotion Processing** (2025). *→ Biological grounding for DNN emotion models*

50. **Kragel, P.A., Kano, M., Van Oudenhove, L., et al.** (2018). Generalizable representations of pain, cognitive control, and negative emotion in medial frontal cortex. *Nature Neuroscience*, 21, 283-289. *→ Cross-category emotion signature precedent*

51. **Chen, F., Lei, F., Shulman, D., et al.** (2021). A distributed fMRI-based signature for the subjective experience of fear. *Nature Communications*, 12, 2772. *→ Fear signature, distributed representation*

52. **Reddan, M.C., Wager, T.D., & Schiller, D.** (2024). A neural signature for the subjective experience of threat anticipation under uncertainty. *Nature Communications*. *→ Threat anticipation signature (SUITAS)*

53. **Kragel, P.A., & LaBar, K.S.** (2024). Neural predictors of fear depend on the situation. *Journal of Neuroscience*. *→ Situation-dependent fear encoding*

#### Retinotopy and visual cortex emotion

54. **Bo, K., Cui, L., Yin, S., Hu, Z., Hong, X., Kim, S., Keil, A., & Ding, M.** (2021). Decoding neural representations of affective scenes in retinotopic visual cortex. *Cerebral Cortex*, 31(6), 3047-3063. *→ Affective scene processing in retinotopic V1-V4*

55. **Liu, T., Fu, J.Z., Chai, Y., Japee, S., Chen, G., Ungerleider, L.G., & Merriam, E.P.** (2022). Layer-specific, retinotopically-diffuse modulation in human visual cortex in response to viewing emotionally expressive faces. *Nature Communications*, 13, 6302. *→ Amygdala-V1 feedback, layer-specific emotion modulation*

56. **Sadeghi, S., Smith, F., Damasio, H., & Smith, M.L.** (2023). Direct perception of affective valence from vision. *eLife*, 12, e88414. *→ Visual valence model (VVM), low-level affect from image statistics*

57. **Phelan, H.L., & Keltner, D.** (2024). Visual looming is a primitive for human emotion. *Current Biology*, 34(17), 3918-3927. *→ Superior colliculus emotion primitive, low-level motion*

#### Occipital-temporal tuning and compositional structure

58. **[Occipital-temporal cortical tuning to semantic and affective features of natural images predicts associated behavioral responses]** (2024). *Nature Communications* or similar. *→ OTC as co-processor of semantic + affect, directly relevant to SQ1-SQ3*

59. **Hebart, M.N., Contier, O., Teichmann, L., Rockter, A.F., Zheng, C.Y., Kidder, A., Corriveau, A., Vaziri-Pashkam, M., & Baker, C.I.** (2023). THINGS-data, a multimodal collection of large-scale datasets for investigating object representations in human brain and behavior. *eLife*, 12, e82580. *→ Large-scale object representation dataset (comparison context)*

60. **[Distributed representations of behaviour-derived object dimensions in the human visual system]** (2024). *→ Object dimension representation, relevant for SAE component interpretation*

61. **[Hierarchical organization of social action features along the lateral visual pathway]** (2024). *→ Social feature hierarchy, relevant for social-emotion feature mapping*

62. **[Functional architecture of cerebral cortex during naturalistic movie watching]** (2024). *→ Cortical architecture during movie — context for static vs naturalistic*

#### Emotion theory and taxonomy

63. **Hochman, Y., Cowen, A.S., & Keltner, D.** (2024). A shared structure for emotion experiences from narratives, videos, and everyday life. *Nature Human Behaviour*. *→ Cross-modal shared emotion structure*

64. **Cowen, A.S., & Keltner, D.** (2021). Semantic space theory: A computational approach to emotion. *Trends in Cognitive Sciences*, 25(2), 124-136. *→ Theoretical framework for Cowen emotion categories*

65. **Lindquist, K.A., & Barrett, L.F.** (2014). Cognitive approaches to emotions. *Current Directions in Psychological Science*. *→ Cognitive/constructionist emotion theory*

66. **Barrett, L.F., & Lindquist, K.A.** (2014). Population coding of affect across stimuli, modalities and individuals. *Journal of Cognitive Neuroscience*. *→ Affect population coding framework*

#### Classical DNN brain encoding

67. **Wen, H., Shi, J., Zhang, Y., Lu, K.H., Cao, J., & Liu, Z.** (2018). Neural encoding and decoding with deep learning for dynamic natural vision. *Cerebral Cortex*, 28(12), 4136-4160. *→ Classical DNN-brain encoding, pre-V-JEPA2 era precedent*

68. **Allen, E.J., St-Yves, G., Wu, Y., Breedlove, J.L., Prince, J.S., Dowdle, L.T., Nau, M., Caron, B., Pestilli, F., Charest, I., et al.** (2022). A massive 7T fMRI dataset to bridge cognitive neuroscience and artificial intelligence. *Nature Neuroscience*, 25, 116-126. *→ NSD dataset (comparison context)*

69. **Conwell, C., Prince, J.S., Alvarez, G.A., & Konkle, T.** (2023). A large-scale examination of inductive biases shaping high-level visual representation in brains and machines. *preprint/Nature Communications*. *→ Inductive biases in brain-model alignment (different from 2024 paper)*

70. **[Brain Dissection: fMRI-trained networks reveal spatial selectivity in processing natural images]** (2023). *→ Brain-optimized model interpretability, relevant for SAE interpretation*

#### Language-brain alignment

71. **Toneva, M., & Wehbe, L.** (2019). Interpreting and improving natural-language processing (in machines) with natural language-processing (in the brain). *Advances in Neural Information Processing Systems (NeurIPS 2019)*. *→ NLP-brain alignment precedent*

72. **Schrimpf, M., Blank, I.A., Tuckute, G., Kauf, C., Hosseini, E.A., Kanwisher, N., Tenenbaum, J.B., & Fedorenko, E.** (2021). The neural architecture of language: Integrative modeling converges on predictive processing. *Proceedings of the National Academy of Sciences*, 118(45), e2105646118. *→ Language brain architecture via predictive processing*

73. **[Language-specific representation of emotion-concept knowledge causally supports emotion inference]** (2024). *→ Language-emotion concept representation*

74. **[Unveiling Multi-level and Multi-modal Semantic Representations in the Human Brain using LLMs]** (2024). *→ Multi-modal semantic via LLM, relevant for semantic factor analysis*

#### Multimodal and foundation model alignment

75. **Oota, S.R., Trouvain, N., Alexandre, F., & Hinaut, X.** (2025). Alignment of auditory artificial networks with massive individual fMRI brain data leads to generalisable improvements in brain encoding and downstream tasks. *→ Audio-brain alignment*

76. **Du, C., Du, C., Fu, K., et al.** (2025). Bridging the behavior-neural gap: A multimodal AI reveals the brain's geometry of emotion more accurately than human self-reports. *Nature Human Behaviour* or similar. *→ MLLM predicts brain emotion geometry — direct competitor/supporter*

77. **[Multi-modal brain encoding models for multi-modal stimuli]** (2025). *→ Multimodal encoding*

78. **[Stacked Regression using Off-the-shelf, Stimulus-tuned and Fine-tuned Neural Networks for Predicting fMRI Brain Responses to Movies (Algonauts 2025 Report)]** (2025). *→ Algonauts 2025 method*

79. **[Instruction-Tuned Video-Audio Models Elucidate Functional Specialization in the Brain]** (2025). *→ Task-tuned multimodal alignment*

80. **[SIM: Surface-based fMRI analysis for inter-subject multimodal decoding]** (2025). *→ Surface-based cross-subject alignment*

81. **Oota, S.R., Moussa, N., Alexandre, F., Hinaut, X., et al.** (2026). Brain-tuning improves generalizability and efficiency of brain alignment in speech models. *→ Brain-tuning methodology*

82. **Moussa, N., et al.** (2026). Improving semantic understanding in speech language models via brain-tuning. *→ Brain-tuning for semantic LLMs*

83. **[Brain-aligning of semantic vectors improves neural decoding of visual stimuli]** (2026). *→ Brain-aligned semantic vectors*

#### Clinical and affective signatures

84. **[A neurofunctional signature of affective arousal generalizes across valence domains and distinguishes subjective experience from autonomic reactivity]** (2025). *→ BAAS brain arousal signature, key comparison to Raut arousal embedding*

85. **[A systems identification approach using Bayes factors to deconstruct the brain bases of emotion regulation]** (2024). *→ Systems identification for emotion regulation*

86. **[Common and distinct neurofunctional signatures of dynamic naturalistic emotion regulation strategies]** (2026). *→ Dynamic emotion regulation signatures*

87. **Mapping the emotional homunculus with fMRI** (2024). *→ Somatotopic emotion representation*

#### Dataset and infrastructure

88. **Aliko, S., Huang, J., Gheorghiu, F., Meliss, S., & Skipper, J.I.** (2020). A naturalistic neuroimaging database for understanding the brain using ecological stimuli. *Scientific Data*, 7, 347. *→ Naturalistic neuroimaging database (used by Jang & Kragel 2025)*

89. **[Naturalistic Stimuli in Affective Neuroimaging: A Review]** (2021). *→ Methodological review for naturalistic affective neuroimaging*

90. **[Probing neurodynamics of experienced emotions—a Hitchhiker's guide to film fMRI]** (2023). *→ Film fMRI methodology primer*

91. **[A 7T fMRI dataset of synthetic images for out-of-distribution modeling of vision]** (2025). *→ Synthetic images (OOD context)*

#### Mind captioning and reconstruction (context)

92. **Tang, J., LeBel, A., Jain, S., & Huth, A.G.** (2023). Semantic reconstruction of continuous language from non-invasive brain recordings. *Nature Neuroscience*, 26, 858-866. *→ Already cited, dual citation with Mind captioning 2024*

93. **[Mind captioning: Evolving descriptive text of mental content from human brain activity]** (2024/2025). *Science Advances*. *→ Brain-to-language generation*

94. **[Reanimating Images using Neural Representations of Dynamic Stimuli]** (2025). *→ Dynamic stimulus decoding*

95. **[Scaling laws for decoding images from brain activity]** (2025). *→ Scaling in brain decoding*

#### Cross-subject generalization

96. **[ICLR-2025: Toward generalizing visual brain decoding to unseen subjects]** (2025). *ICLR 2025*. *→ Cross-subject generalization — relevant for n=5 limitation*

97. **[Heritability of movie-evoked brain activity and connectivity]** (2025). *→ Heritability of naturalistic brain response*

#### Emotion-specific ROI and pathways

98. **[Decoding affect in emotional body language: valence representation in the action observation network]** (2025). *→ Body language affect decoding*

99. **[Processing of natural scenes in the human pulvinar]** (2025). *→ Subcortical pulvinar scene processing*

100. **[Personalized brain decoding of spontaneous pain in individuals with chronic pain]** (2026). *→ Individual differences, personalized decoding*

#### Development

101. **[Large-scale encoding of emotion concepts becomes increasingly similar between individuals from childhood to adolescence]** (2023). *Nature Neuroscience*. *→ Developmental convergence of emotion representation*

#### Context — foundation model landscape

102. **[fMRI-LM: Foundation model for fMRI]** (2025). *→ fMRI foundation model landscape*

103. **[Using goal-driven deep learning models to understand sensory cortex]** (2025). *→ Yamins-DiCarlo style goal-driven encoding framework*

104. **[Affective computing has changed: the foundation model disruption]** (2026). *→ Foundation models in affective computing*

105. **[Bridging Discrete and Continuous: A Multimodal Strategy for Complex Emotion Detection]** (2024). *→ Discrete-continuous emotion bridging*

106. **[Deep learning reveals what facial expressions mean to people in different cultures]** (2024). *→ Cross-cultural facial emotion*

107. **[Achieving more human brain-like vision via human EEG representational alignment]** (2026). *→ EEG alignment complement (different modality)*

108. **[Human-like Affective Cognition in Foundation Models]** (2026). *→ Foundation model affective cognition*

### v1.3 — Web search additions (verified for venue quality)

From supplementary web search, filtered by: Q1 journals / top conferences / CCN / tutorial track / recent arXiv (<1 year) only.

#### Methodological — SAE / neural latent discovery

109. **[NLDisco: A Pipeline for Interpretable Neural Latent Discovery]** (2025). *Data on the Brain & Mind Tutorial Track, NeurIPS 2025*. https://data-brain-mind.github.io/tutorials/nldisco-a-pipeline-for-interpretable-neural-latent-discovery/ *→ Direct pipeline for sparse encoder-decoder on neural data — ready-to-use framework for our SAE analysis*

110. **[TRACE: Task-Relevant Autoencoder via Classifier Enhancement]** (2025). *Scientific Reports*, 15, 83867. https://www.nature.com/articles/s41598-024-83867-6 *→ Task-relevant autoencoding; >12% improvement in decoding accuracy via classifier-enhanced constraint*

#### GW-OT methodological advances

111. **Thual, A., Tran, H., Zemskova, T., Courty, N., Flamary, R., Dehaene, S., & Thirion, B.** (2022). Aligning individual brains with fused unbalanced Gromov-Wasserstein. *Advances in Neural Information Processing Systems (NeurIPS 2022)*. https://arxiv.org/abs/2206.09398 *→ FUGW — foundational paper for neuroscience GW-OT; Takeda 2025 toolbox builds on this*

#### Compositional representation

112. **Ito, T., Klinger, T., Schultz, D.H., Murray, J.D., Cole, M.W., & Rigotti, M.** (2022). Compositional generalization through abstract representations in human and artificial neural networks. *Advances in Neural Information Processing Systems (NeurIPS 2022)*, 35, 32225-32239. *→ Compositional generalization via abstract representations — theoretical grounding*

113. **Skerry, A.E., & Saxe, R.** (2015). Neural representations of emotion are organized around abstract event features. *Current Biology*, 25(15), 1945-1954. *→ Abstract event features in emotion representation*

#### Component Process Model (CPM) — emotion theory

114. **Mohammadi, G., Van De Ville, D., & Vuilleumier, P.** (2023). Brain networks subserving functional core processes of emotions identified with componential modeling. *Cerebral Cortex*, 33(12), 7993-8004. https://doi.org/10.1093/cercor/bhad048 *→ CPM-based fMRI analysis of emotion brain networks — from Emo-FilM's home team (EPFL). Direct precedent for component-based emotion analysis.*

#### Hyperalignment — cross-subject alignment

115. **Haxby, J.V., Guntupalli, J.S., Nastase, S.A., & Feilong, M.** (2020). Hyperalignment: Modeling shared information encoded in idiosyncratic cortical topographies. *eLife*, 9, e56601. https://doi.org/10.7554/eLife.56601 *→ Core hyperalignment framework — relevant for n=5 extension*

116. **[Boosting Hyperalignment Performance with Age-specific Templates]** (2025). *eLife*, reviewed preprint. https://doi.org/10.7554/eLife.110566 *→ Age-specific hyperalignment — cross-subject generalization methodology*

117. **[Functional Inter-Subject Alignment Outperforms Anatomical Alignment]** (2025). *CCN 2025*. *→ Functional vs anatomical alignment comparison*

### Removed from v1.3 (failed venue criteria)

- ~~Neural Entropic OT (arXiv 2312.07397, Dec 2023)~~ — >1 year preprint-only, no venue
- ~~Brain Decoding Survey (arXiv 2503.15978)~~ — borderline timing, preprint-only survey

### v1.4 — ICLR 2026 additions

Filter criteria: ICLR 2026 accepted papers, posters, or recent (within 1 year) submissions on OpenReview.

#### fMRI Foundation Models

118. **[SLIM-Brain: A Data- and Training-Efficient Foundation Model for fMRI Data Analysis]** (2026). *ICLR 2026*. https://openreview.net/forum?id=fFgzAQAUqs *→ Atlas-free fMRI foundation model, data-efficient (3% of standard pretraining data). Directly relevant to our n=5 Horikawa — potential alternative to Brain-JEPA for brain representation. Addresses small-data regime explicitly.*

119. **[PRISM: Decoding Visual Stimuli with fMRI]** (2026). *ICLR 2026 Poster*. https://iclr.cc/virtual/2026/poster/10011227 *→ fMRI → structured text space → object-centric diffusion for visual stimulus reconstruction. Achieves 8% reduction in perceptual loss over prior SOTA. Context for fMRI decoding landscape.*

120. **[Brain encoding models based on binding multiple modalities across audio, language, and vision]** (2026). *ICLR 2026*. https://openreview.net/forum?id=3NMYMLL92j *→ Multimodal brain encoding framework — relevant for comparing to V-JEPA2 single-modality approach*

#### Sparse Autoencoder advances (ICLR 2026)

121. **[AbsTopK: Rethinking Sparse Autoencoders]** (2026). *ICLR 2026*. https://openreview.net/pdf/ac9d8c1ff00c4036c97381b77ecf7d5f01270c5f.pdf *→ AbsTopK reformulation of sparse autoencoders — most recent SAE methodology. Directly applicable to our SAE implementation on fMRI.*

122. **[Mechanistic Interpretability with Sparse Autoencoder Neural Operators (SAE-NOs)]** (2026). *ICLR 2026 (submission)*. https://arxiv.org/abs/2510.02917 *→ SAE extended to infinite-dimensional function spaces via neural operators. Important extension relevant for potentially scaling our SAE analysis.*

#### GW-OT methodological advances (ICLR 2026)

123. **[REALIGN: Regularized Procedure Alignment with Matching Video Embeddings via Partial Gromov-Wasserstein Optimal Transport]** (2026). *ICLR 2026 (submission)*. https://openreview.net/forum?id=kop52LaSAB *→ Partial GW-OT for video temporal alignment. Methodology extension directly relevant to our tri-axial GW-OT on V-JEPA2 video features.*

---

*v1.4 — 2026-04-19 (ICLR 2026 papers added — 6 new entries)*
