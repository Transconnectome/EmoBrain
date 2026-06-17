# Thesis Option A — Horikawa Main

**Focus:** 감정 관련 뇌 표상의 구조 — representation characterization
**Dataset:** Horikawa 2020 (main) + Emo-FilM (optional secondary for validation)
**Core methodology:** Static representation analysis with modern DL methods
**Date:** 2026-04-19 (v1)

---

## 1. Research Question

### Main RQ
> **"감정 자극에 대한 뇌의 표상 구조는 어떻게 조직되어 있는가? Video foundation model의 서로 다른 factor (temporal, semantic, layer depth)가 이 표상의 어느 측면과 align하며, 이 alignment 구조에서 어떤 components가 발견되고, 서로 다른 감정이 이 component 공간에서 어떻게 구별되는가?"**

### Sub-questions

**SQ1 (Factor-region alignment — Sartzetaki extension)**
V-JEPA2의 각 layer/factor가 어느 emotion-related brain region과 align하는가? 감정 유형에 따라 이 alignment profile이 어떻게 다른가?

**SQ2 (Tri-axial structural alignment)**
Brain, Stimulus (video model), Behavior (emotion ratings) 세 축의 표상 기하학은 서로 어떻게 대응하며, 어디서 구조가 일치하고 어디서 어긋나는가?

**SQ3 (Compositional structure)**
Brain의 감정 관련 활동은 compositional한 components로 decompose되는가? 서로 다른 감정은 이 components의 서로 다른 조합으로 표현되는가?

**SQ4 (Emotion space geometry)**
Brain component space에서 감정 유형들 간 기하학적 관계는 무엇이며, 기존 emotion theory (Cowen 27 emotions, Russell valence-arousal)와 어떻게 대응하는가?

---

## 2. Theoretical Gap

### 현재 field 상태

**Sartzetaki 2025 (ICLR)**: Video model factor × visual cortex region alignment 체계적 분석 — 하지만 **BMD (action recognition) 데이터, emotion label 없음**. 감정 특화 factor-region 분석 공백.

**Horikawa 2020 (iScience)**: 감정을 34 category로 decode — 언어 범주를 ground truth로 사용. Categorical vs dimensional 이분법 안에 갇힘.

**Brain Algebra (Ferrante 2025, Comms Bio)**: 뇌 visual representation이 compositional — 하지만 static visual concepts (object, season 등). 감정 특화 compositional 검증 없음.

**Takeda 2025 (iScience)**: Gromov-Wasserstein OT를 brain-brain alignment에 적용 — NSD images. Brain × Stimulus × Behavior 삼각 비교 미적용.

### Gap 통합

감정 자극에 대한 뇌의 표상 구조를:
1. **Label-free**로 (언어 범주를 사전 target 아닌 post-hoc reference로)
2. **Factor-region 수준 + Component 수준** 둘 다에서 
3. **Brain, Stimulus, Behavior 삼각 구조**에서
4. **Modern DL methodology** (V-JEPA2, SAE, GW-OT)로

체계적으로 characterize한 연구가 없다.

---

## 3. Hypotheses

### H1 — Factor-region differentiation (Sartzetaki emotion extension)
> V-JEPA2의 서로 다른 factor들이 서로 다른 emotion-relevant brain region과 systematic하게 align한다.
> 
> 구체 예측: Temporal modeling factor는 limbic/subcortical, semantic/deep factor는 DMN/transmodal과 alignment가 높음.

**Falsifiable:** 모든 emotion region이 동일 factor와 align하면 기각. 또는 factor와 무관한 uniform alignment면 기각.

### H2 — Emotion-specific factor profile
> 감정 유형마다 dominant factor가 다르다.
>
> 구체 예측: 감각 중심 감정 (disgust, surprise) = low-level + motion factor. 맥락 중심 감정 (awe, nostalgia) = deep/semantic factor.

**Falsifiable:** 모든 감정이 동일 factor profile을 공유하면 기각.

### H3 — Tri-axial structural correspondence
> Brain, Stimulus, Behavior 세 표상 공간의 기하학이 GW-OT로 align 가능한 structural similarity를 가진다.
>
> 구체 예측: Brain-Stimulus alignment > Brain-Behavior alignment (stimulus는 입력이고 behavior는 해석이므로).

**Falsifiable:** 두 공간의 GW-OT distance가 chance 수준이면 기각.

### H4 — Compositional brain representation for emotion
> 감정 관련 뇌 활동은 sparse compositional components의 조합으로 표현된다.
>
> 구체 예측: 서로 다른 감정 범주가 동일 components의 다른 조합으로 표현됨. 예: Joy = c1+c3+c7, Nostalgia = c1+c3+c12 (c1, c3 공유).

**Falsifiable:** SAE로 components 발견되지만 감정 범주 간 systematic 조합 structure 없으면 기각.

### H5 — Pure vs compound emotion dichotomy
> 일부 감정은 적은 수의 components로 표현되는 "pure" 감정, 다른 감정은 많은 components의 superposition인 "compound" 감정.
>
> 구체 예측 (Awe 논문 Lee 2025 연장): Awe, empathic pain 같은 감정이 compound 구조. Disgust, fear 같은 감정이 more pure.

**Falsifiable:** 모든 감정이 균일한 component 개수로 표현되면 기각.

### H6 — Emotion space geometry reflects known theory (partially)
> Brain의 component space에서 감정 간 거리/위치가 Cowen 27-emotion 구조의 일부를 반영하지만 완전히 일치하지는 않는다.
>
> 구체 예측: Category cluster가 일부 드러나지만 boundary가 fuzzy함 (Cowen의 "continuous gradients between categories"와 일치).

**Falsifiable:** 완전 일치 (trivial replication) 또는 완전 불일치 (새 구조)면 re-interpret.

---

## 4. Methodology

### 4.1 Data

**Horikawa 2020:**
- 5 subjects × 2185 videos × 450 parcels (Schaefer 400 cortical + 50 subcortical)
- Each video: 3 seconds
- Labels: 34 emotion categories + 14 affective dimensions = 48 targets (Cowen & Keltner annotation)
- 이미 전처리 완료

**Emo-FilM (optional secondary):**
- 30 subjects × 14 films × 2.5h total
- Moment-by-moment emotion rating (50 CPM items, 본인 rating)
- Role: cross-dataset validation (SQ4 extension, H3 robustness)

### 4.2 Stimulus processing

**V-JEPA2 (Meta 2025, self-supervised video transformer):**
- Frame-wise features from each video (32 layers available)
- Layer-wise extraction: low-level (layer 0-8), mid (9-20), deep (21-32)
- Aggregation: temporal pooling per 3s video → single feature vector per layer per video

**추가 features (comparison):**
- vision.mat (2185 × 1000): low/mid-level visual features (Gabor-like)
- semantic.mat (2185 × 73): concept-level semantic features
- CLIP embeddings (2185 × 512): vision-language aligned

### 4.3 Brain processing

**Level 1 (classical baseline):**
- Raw fMRI (Schaefer 450 parcels)
- Subject-level and group-averaged

**Level 2 (task-specific DL, optional):**
- SAE on fMRI (Anthropic-style, overcomplete sparse dictionary)
- 450d → K-dim sparse features (K = 2000 candidates, sparsity ~20-50 active)
- Self-supervised, no labels used
- **BFM (Brain-JEPA) 사용 안 함** — pretraining mismatch 우려

### 4.4 Main analyses

#### Analysis 1 — Factor-region alignment (SQ1)

**Sartzetaki-style on emotion domain:**

```
For each emotion-related ROI (limbic, STS, TPJ, DMN, insula, amygdala, etc.):
  For each V-JEPA2 layer l (0-32):
    1. Compute RDM_brain (2185 × 2185) from fMRI in ROI
    2. Compute RDM_model_l (2185 × 2185) from V-JEPA2 layer l features
    3. Compute Spearman correlation of RDMs
    4. Output: alignment score per ROI × layer

Statistical test: permutation, Bonferroni-corrected
Noise ceiling: inter-subject variability
```

**Output:** Factor × emotion region alignment map.

#### Analysis 2 — Emotion-specific factor profile (SQ1, H2)

```
For each emotion category c (34 cat + 14 dim):
  Videos_c = videos high on category c
  
  For each ROI and each layer:
    Alignment restricted to Videos_c subset
  
  Output: per emotion, factor profile across regions
  
Compare: 
  disgust profile vs joy profile
  Categorical emotions clustering
```

**Output:** Emotion × factor × region tensor.

#### Analysis 3 — Tri-axial GW-OT (SQ2, H3)

**Three distance matrices (all 2185 × 2185):**

```
D_brain:    Video-to-video brain pattern distances (from fMRI)
D_stim:     Video-to-video V-JEPA2 feature distances
D_behav:    Video-to-video behavior label distances (48 targets)
```

**Pairwise GW-OT:**

```
1. Brain ↔ Stim:  GW distance + optimal transport plan T_bs
2. Brain ↔ Behav: GW distance + transport plan T_bb  
3. Stim ↔ Behav:  GW distance + transport plan T_sb (baseline)

Analysis:
- GW distance magnitude (how structurally similar)
- Transport plan analysis (which videos map to which)
- Per-video "warping score" (where structure diverges)
- Layer-wise GW per V-JEPA2 layer (which layer best matches brain)
```

**Method reference:** Thual et al. 2025 (J Neurosci Methods) neuroscience GW-OT toolbox.

**Output:** Tri-axial structural alignment quantified + divergence map.

#### Analysis 4 — Compositional components (SQ3, H4, H5)

**Sparse Autoencoder on fMRI:**

```
Input: fMRI (2185 × 450) 
   or (10,925 × 450) if subject-stacked

SAE architecture:
  Encoder: 450 → 2000 (sparse, L1 regularization)
  Decoder: 2000 → 450
  Sparsity: ~20-50 active features per input

Training: MSE reconstruction + L1 sparsity
```

**Post-hoc analysis per component:**

```
For each meaningful sparse feature (K_active ~100-300):
  1. Brain map: 450d decoder weights (where this feature resides)
  2. Video activation profile: 2185 activation values (what activates this)
  3. Emotion correlation: K_active × 48 matrix
  4. Feature stability: subject-level consistency check
```

**Output:** Component dictionary with spatial + functional interpretation.

#### Analysis 5 — Compositional algebra test (Brain Algebra extension for emotion, H4)

**Ferrante 2025 approach adapted:**

```
For pairs of emotion categories (c1, c2):
  Pattern_c1 = avg fMRI for videos high on c1
  Pattern_c2 = avg fMRI for videos high on c2
  
  Composition tests:
    a) Pattern_c1 + Pattern_c2 ≈ Pattern_compound?
       (e.g., Nostalgia + Joy = Bittersweet?)
    
    b) Pattern_c1 - Pattern_valence ≈ ?
       (e.g., Anger - NegValence = Arousal-only?)
    
    c) Arithmetic predictions test via fMRI-to-image decoding 
       (if applicable with generative models)
```

**Systematicity test:** Does the same composition rule hold across many emotion pairs?

**Output:** Compositional structure validation (or falsification).

#### Analysis 6 — Emotion space geometry (SQ4, H6)

```
After components discovered:
  
  Each emotion category → centroid in component space
  
  Analyses:
    - Cluster structure (how separate categories are)
    - Gradient structure (valence-arousal axes visible?)
    - Topology: which emotions are "neighbors"?
    - Compare with Cowen 27-emotion semantic space (SH-CCA)
  
  Visualization:
    - UMAP / t-SNE of component space
    - Ego-graph per emotion
```

**Output:** Emotion geometry map + theory comparison.

#### Analysis 7 — RepE directions (supplementary)

**Representation Engineering on brain component space:**

```
For each emotion axis (e.g., valence, arousal, or category pairs):
  1. Find direction in component space via linear probe
  2. Test vector arithmetic: 
     "Fear direction" - "Arousal direction" = ?
     "Joy direction" + "Social direction" = ?
  3. Validate on held-out videos
```

**Output:** Emotion directions in brain space + vector arithmetic validation.

### 4.5 Integration

```
Analysis 1-2 → Factor-region-emotion tensor
Analysis 3   → Tri-axial structural map  
Analysis 4-5 → Component compositional structure
Analysis 6   → Emotion geometry
Analysis 7   → Direction vectors

Cross-analysis:
  - Factor dominant for emotion X == component dominant for emotion X?
  - GW-OT divergence regions == high-novel-component regions?
  - Emotion geometry from components vs from behavior
```

**Narrative:** 감정 자극에 대한 뇌 표상은 **factor 수준에서 region-specific alignment**를 보이고, **component 수준에서 compositional structure**를 가지며, 이 두 수준이 **tri-axial 구조로 stimulus, behavior와 연결**되어 있다.

---

## 5. Novelty Positioning

### Against direct precedents

| Paper | 그들이 한 것 | 우리가 다르게 |
|-------|-----------|-------------|
| **Sartzetaki 2025 (ICLR)** | Factor × region on BMD (actions) | Emotion domain + compositional + GW-OT + components |
| **Horikawa 2020** | 34 category decoding | Label-free, component-based, factor analysis |
| **Brain Algebra (Ferrante 2025)** | Visual concepts compositional | Emotion-specific + V-JEPA2 latent + tri-axial |
| **Takeda 2025 GW-OT** | Brain-brain cross-individual | Brain-Stimulus-Behavior tri-axial for emotion |
| **Awe paper (Lee 2025)** | Single emotion (awe), CEBRA, EEG | All 48 emotions, SAE, fMRI |
| **Du 2023 topographic** | Affective space PCA | Compositional SAE + GW-OT + Sartzetaki factor |

### Unique contribution
**"Factor-region alignment + compositional components + tri-axial alignment" 세 요소를 동시에 적용해 감정 표상을 체계적으로 characterize한 연구 없음.** 각 요소 개별 선례 있으나 combination은 공백.

---

## 6. Risks

### 방법론적 risks
- SAE components의 interpretability 불확실 (noise일 가능성)
- GW-OT tri-axial 계산 부담 (O(N²) × 3)
- n=5 통계 power 제약 (individual-level 신뢰성)

### 이론적 risks
- Brain Algebra가 이미 감정 일부 test함 → replication 인상
- Compositional 결과가 trivial 할 수 있음 (emotion 조합이 당연히 compositional)
- Factor-region alignment가 TRF 계층 재발견에 그칠 수 있음

### Dynamic 포기의 대가
- "감정은 process"라는 네 원래 직감을 포기
- Dynamic 못 다룸 (Horikawa 3초 제약)
- Arousal embedding (Raut 2025) 직접 대응 불가

---

## 7. Feasibility (2-month plan)

```
Week 1: 
  - V-JEPA2 layer-wise features on Horikawa 검증 (이미 추출됨)
  - SAE 구현 + training pipeline 구축
  - Schaefer 450 parcel grouping for emotion ROIs

Week 2:
  - Analysis 1 (factor-region RSA) 수행
  - Layer-wise alignment maps 생성
  - Permutation statistics

Week 3:
  - Analysis 2 (emotion-specific factor profile)
  - SAE training convergence
  - Component 발견 + 해석

Week 4:
  - Analysis 3 (GW-OT tri-axial) 
  - Tri-axial alignment quantification
  - Divergence analysis

Week 5:
  - Analysis 4-5 (compositional test, Brain Algebra extension)
  - Systematicity validation

Week 6:
  - Analysis 6 (emotion geometry)
  - Analysis 7 (RepE, if time)
  - (Optional) Emo-FilM validation

Week 7:
  - Integration + cross-analysis
  - Figures (8-10 main)

Week 8:
  - Writing (intro, methods, results)
  - Revision
```

**Feasibility assessment:** 높음. 모든 data 준비됨. 각 analysis가 독립적이어서 진행 문제 없으면 안정적 완성.

---

## 8. Expected Outcome

### Primary contribution
1. **Emotion domain Sartzetaki extension** (factor × emotion region alignment)
2. **Tri-axial structural characterization** (Brain × Stimulus × Behavior)
3. **Compositional brain emotion representation** (SAE + Brain Algebra)
4. **Integrated framework** for label-free emotion representation

### If all hypotheses supported
"감정 표상이 factor-region, component 수준에서 체계적 구조 + tri-axial alignment를 가지며 compositional로 조직됨" — 감정 뇌과학에 새로운 characterization framework 제공.

### Fallback narratives
- H4 기각 → "compositional 아니다" empirical 증거 (의미 있는 negative)
- H1 부분 성공 → "일부 factor-region mapping만 작동" descriptive finding
- H3 GW-OT 실패 → "tri-axial alignment가 non-trivial" (structure 복잡함 시사)

모든 시나리오에 defensible narrative 존재.

---

## 9. Key References

**Direct precedents (positioning):**
- Sartzetaki et al. ICLR 2025 — Factor × region RSA framework
- Ferrante et al. Comms Biology 2025 — Brain Algebra compositionality
- Takeda et al. iScience 2025 — GW-OT for neuroscience
- Horikawa et al. iScience 2020 — Dataset origin, categorical framing

**Methodological foundations:**
- Bricken et al. Anthropic 2023/2024 — Sparse Autoencoders
- Cunningham et al. OpenAI 2024 — Scaling SAEs
- Thual et al. J Neurosci Methods 2025 — GW-OT toolbox
- Meta 2025 — V-JEPA2

**Theoretical background:**
- Cowen & Keltner PNAS 2017 — 27 emotion categories
- Kragel & LaBar Trends Cogn Sci 2016 — Nature of emotion in brain
- Russell 1980 — Circumplex model (contrast)
- Barrett & Lindquist 2012 — Constructionism (contrast)

**Secondary (cite for context):**
- Awe CEBRA (Lee 2025 Comms Psych) — Label-free precedent
- Jang & Kragel J Neurosci 2025 — Amygdala systems ID
- Kragel 2019 EmoNet — Emotion schemas in vision

---

*v1 — 2026-04-19*
