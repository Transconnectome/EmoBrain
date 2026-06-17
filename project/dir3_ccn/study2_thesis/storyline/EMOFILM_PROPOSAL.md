# Track 2 Proposal: Emotion as Dynamical System — Latent Dynamics in Emo-FilM

**Target:** Master's thesis (main contribution)
**Date:** 2026-04-19
**Status:** v1 proposal

---

## 0. Executive Summary

인간의 감정을 **정적 표상 (state, category, dimension)이 아니라 latent dynamical system의 trajectory로 재정의**하고, 이를 Emo-FilM dataset (30 subjects × 14 films × 2.5 hours)의 연속 fMRI 시계열에서 empirical하게 규명한다. Modern deep learning latent dynamics 방법들 (BCNE, T-PHATE, Neural ODE, SLDS, Neural Koopman)을 감정 fMRI에 **first systematic application**하여 (a) 감정 유형별 distinct dynamical signatures (time scale, attractor, trajectory shape), (b) 시각 자극 변화가 이끄는 trajectory 변화, (c) 감정 간 전환의 dynamical 구조를 정량화한다. 기존 감정 뇌과학의 snapshot 가정을 theoretically challenge하고 methodologically modernize한다.

---

## 1. Background and Motivation

### 1.1 The snapshot assumption in emotion neuroscience

감정 뇌과학은 수십 년간 다음 공통 가정 위에 서 있었다:

> **"감정 = 자극 또는 상태에 의해 evoke되는 뇌의 정적 패턴이며, 이 패턴으로부터 감정을 decode하거나 이 패턴의 위치를 map할 수 있다."**

이 가정이 명시적으로 나타나는 곳:

- **Categorical decoding (Ekman, Horikawa 2020, Kragel 2019 EmoNet):** "이 pattern = fear"
- **Dimensional mapping (Russell, Du 2023):** "이 좌표 = (valence, arousal)"
- **Constructionism (Barrett, Lindquist):** "Core affect (dimensional pattern) + conceptualization = emotion"
- **Perception-primacy (Conwell 2025):** "Visual features → affect rating, pattern 중심"

이 모든 접근은 **시간적 정보를 평균하거나 무시하고 snapshot pattern을 감정의 기본 단위로 취급**한다.

### 1.2 Phenomenological reality

하지만 감정의 phenomenological 본성은 근본적으로 temporal이다:

- **Fear는 쌓인다** — 공포 영화에서 긴장이 점진적으로 누적, 최고조 후 해소
- **Surprise는 전환이다** — 순간적 상태 변화, 이후 급격한 decay
- **Joy는 발현한다** — 천천히 빌드업, 지속, 점진적 soft landing
- **Sadness는 persistent한 drift** — 쉽게 사라지지 않음
- **Disgust는 즉각적 반사** — 자극 → 반응 → 짧은 회피 트레일
- **Anger는 spectrum** — 짜증 → 불만 → 분노 → 격노 연속 변이

이 phenomenology는 **각 감정이 distinct temporal structure**를 가진다는 강력한 직관을 제공한다. 같은 valence-arousal 좌표에 있더라도 disgust와 fear는 time scale, onset speed, decay pattern이 다르다.

### 1.3 Empirical evidence for temporal specificity

실제로 emotion phenomenology의 temporal heterogeneity에 대한 empirical 증거는 점점 축적되고 있다:

- **Temporal receptive field hierarchy (Hasson et al. 2008; Chen et al. 2016):** 뇌 영역마다 다른 temporal integration window. Visual cortex 짧음, transmodal/DMN 김. **일반 지각에서 검증. 감정에서는 미검증.**
- **Emotional "accumulation" in medial prefrontal (Chang et al.):** vmPFC 활동이 영화 시청 중 점진적 축적
- **Dynamic connectivity studies (eLife 2025 Dynamic fMRI networks of emotion):** Forrest Gump 시청 중 4 emotion networks의 time course가 감정에 따라 다름. **고전 방법 (ICA + Gaussian curve fitting)으로 분석.**

### 1.4 Methodological gap

**Modern deep learning latent dynamics methods가 감정 fMRI에 거의 적용되지 않음:**

| Method | 적용 분야 | 감정 적용 여부 |
|--------|---------|-----------|
| **CEBRA (Nature 2023)** | Motor cortex, calcium imaging, hippocampus | ❌ (Awe EEG만 — Lee 2025) |
| **BCNE (Nat Comp Sci 2025)** | General brain trajectory | ❌ |
| **T-PHATE (Nat Comp Sci 2023)** | Naturalistic fMRI (Sherlock, Friends) | ❌ |
| **Neural ODE (NeurIPS 2018)** | Spike trains, calcium | ❌ |
| **gpSLDS (NeurIPS 2024)** | Various | ❌ |
| **SING SDE (NeurIPS 2025)** | Latent dynamics | ❌ |
| **Neural Koopman (IEEE TMI 2025)** | ABIDE, HCP (general fMRI) | ❌ |

**Emotion fMRI dynamics 연구는 거의 전부 classical methods에 머물러 있다.**

### 1.5 The paradigm shift opportunity

이 gap이 의미하는 것:
1. **Theoretical opportunity**: "감정 = snapshot" 가정을 empirical하게 도전 가능
2. **Methodological opportunity**: Modern DL dynamics tools를 first-apply
3. **Scientific opportunity**: 감정의 temporal heterogeneity (disgust vs joy)를 정량화 가능
4. **Convergent phenomenon**: Phenomenology + field consensus + tool availability가 수렴

---

## 2. Research Question

### 2.1 Main Research Question

> **"자연스러운 감정 자극 (영화) 시청 중 뇌의 감정 관련 활동은 정적 패턴이 아니라 latent dynamical system의 trajectory로 이해되는가? 서로 다른 감정 유형은 이 dynamical space에서 어떤 고유한 signature (time scale, trajectory shape, stability, attractor depth)로 구별되는가?"**

### 2.2 Sub-questions

**SQ1 — Latent space geometry:**
감정 관련 뇌 활동의 latent space는 어떤 기하학 (차원, manifold 형태, 영역 분포)을 가지는가? 이 공간이 Emo-FilM과 Horikawa에서 공통적으로 발견되는가?

**SQ2 — Per-emotion dynamical signatures:**
서로 다른 감정은 latent space에서 어떤 dynamical 특성으로 구별되는가? Time constant, trajectory length, attractor depth, stability — 각 감정의 고유 signature는?

**SQ3 — Fast vs slow emotion typology:**
감정을 "fast-onset attractor" (disgust, surprise)와 "slow-building drift" (joy, nostalgia)로 dynamical typology 분류 가능한가? 이 분류가 bimodal인가 continuous인가?

**SQ4 — Stimulus-driven trajectory:**
시각 자극 (V-JEPA2 feature time series)의 변화가 뇌 trajectory의 방향/속도를 어떻게 driving하는가? Endogenous dynamics와 stimulus-driven dynamics를 분리 가능한가? V-JEPA2의 어느 layer가 어느 trajectory aspect를 driving하는가?

**SQ5 — Emotion transitions:**
감정 간 전환 (예: 긴장 → 안도, 중립 → 놀람)은 smooth continuous drift인가 discrete bifurcation인가? 전환 구조에 systematic 패턴이 있는가? Narrative event strength와 correlate하는가?

**SQ6 — Cross-subject dynamical consistency:**
30명이 같은 영화를 볼 때 trajectory가 서로 얼마나 align되는가? 어느 영역/감정에서 alignment가 높고 어디서 divergent한가?

---

## 3. Research Gap

### 3.1 What is known

**Theoretical:**
- 감정의 temporal phenomenology는 Barrett's constructionism, Scherer's appraisal theory 등에서 이론적 언급은 있으나 **empirical dynamical characterization 부재**.
- Hasson 2008 TRF hierarchy: 뇌 영역의 intrinsic timescale gradient (visual fast, transmodal slow). **감정에는 미적용.**

**Empirical (classical methods):**
- **eLife 2025 "Dynamic fMRI networks of emotion"**: Forrest Gump 영화 fMRI, 4 emotion networks의 time course 차이. **ICA + Gaussian curve fitting으로 분석.** Dynamic 관찰은 했으나 per-emotion systematic signature 없음.
- **eNeuro 2025 music HMM**: 음악에 의한 감정 전환을 HMM으로 분석. **Discrete state 가정.**
- **Pessoa 2024 eLife**: Threat trajectory analysis. **Linear dimensionality reduction**, single emotion.
- **Raut et al. Nature 2025**: Arousal이 brain dynamics의 universal 1-d manifold. **Mouse + human, 감정 특화 아님.**

**Empirical (modern DL):**
- **BCNE (Nat Comp Sci 2025)**: 뇌 trajectory의 unsupervised manifold. **감정 미적용.**
- **T-PHATE (Nat Comp Sci 2023)**: fMRI naturalistic manifold. **감정 미적용.**
- **Lee et al. 2025 (Comms Psych)**: Awe를 CEBRA로 **EEG** 분석. 단일 감정, EEG only.

### 3.2 What is missing — the core gap

위 선행을 종합하면 세 가지 공백이 교차하는 자리:

1. **Emotion-specific dynamical signatures** — Pessoa single emotion, eLife 4 network coarse. 전체 감정 spectrum의 체계적 signature 정량화 없음.
2. **Modern DL latent dynamics on emotion fMRI** — CEBRA/BCNE/Neural ODE/SLDS 등 최신 tools가 감정 fMRI에 거의 미적용.
3. **Stimulus-driven trajectory decomposition** — eLife dynamic은 stimulus-driven을 분리 안 함. V-JEPA2 layer-wise encoding과 brain trajectory coupling 분석 없음.

### 3.3 Gap statement

> 감정 뇌과학에서 **(a) modern DL latent dynamics methodology를 활용한, (b) 전체 감정 spectrum을 대상으로, (c) stimulus-driven vs endogenous dynamics를 분리한, (d) 체계적 dynamical characterization**이 부재하다.

### 3.4 Why does this gap matter?

1. **Theoretical:** 감정의 본성을 "무엇 (what)"이 아닌 "어떻게 (how)"로 재정의 가능
2. **Methodological:** Field에 새로운 toolkit 도입 — 후속 연구의 기반
3. **Clinical:** 감정 장애 (우울증, PTSD)의 dynamics-level biomarker 가능성
4. **AI alignment:** Emotion model을 static label 대신 trajectory-based로 학습

---

## 4. Hypotheses

### H1 — Distinct dynamical signatures per emotion
서로 다른 감정은 정적 brain pattern뿐만 아니라 **dynamical 성격** (time constant, trajectory shape, stability, attractor depth)에서 체계적으로 구별된다.

**Specific predictions:**
- Disgust trajectory: 짧은 time constant (τ ~ 2-4 TRs), 빠른 수렴, strong attractor
- Joy trajectory: 긴 time constant (τ ~ 10+ TRs), 느린 drift, weak attractor
- Fear trajectory: medium time constant, pre-event anticipation build-up
- Surprise: discontinuity at onset, rapid decay

**Falsifiable:** 모든 감정이 동일 time constant / 동일 flow 구조. 또는 noise 수준 차이.

### H2 — Fast-onset vs slow-building emotion dichotomy
감정 유형은 **stability 구조**에 따라 크게 두 class로 분류된다.

**Specific predictions:**
- **Fast-onset attractors** (sensory-reactive): disgust, surprise, fear, startle. 빠른 trajectory convergence, 짧은 지속.
- **Slow-building drifts** (constructed): joy, nostalgia, awe, aesthetic appreciation, satisfaction. 점진적 buildup, 긴 지속.
- **Intermediate:** anger (spectrum), empathic pain (social context)

**Falsifiable:** Bimodal structure가 아니라 uniform distribution.

### H3 — Stimulus-driven trajectory coupling
V-JEPA2 feature time series가 brain trajectory 변화를 systematic하게 driving한다.

**Specific predictions:**
- Cross-correlation: V-JEPA2 feature Δt → Brain trajectory Δt 예측 가능 (lag ~1-3 TRs)
- Layer-wise: early layers (motion, edge) → early visual trajectory driving. Deep layers (semantic) → transmodal trajectory driving.
- Endogenous + driven decomposition: Brain trajectory = f(stimulus_V-JEPA2) + endogenous. Residual endogenous component 존재.

**Falsifiable:** Stimulus feature가 trajectory를 예측 못 하거나 (uncoupled), 전적으로 endogenous.

### H4 — Emotion transitions as bifurcations
감정 간 전환은 smooth continuous drift가 아니라 특정 bifurcation point에서 **discrete-like jump**를 포함한다.

**Specific predictions:**
- 영화의 강한 감정 전환 장면 (반전, 충격적 발견)에서 trajectory discontinuity detected
- 자연스러운 감정 변화 (joy → calm)는 smooth drift
- Bifurcation 지점이 narrative event strength와 상관

**Falsifiable:** 모든 전환이 smooth, 또는 모두 discrete — 변이 없음.

### H5 — Cross-subject trajectory consistency
30명이 같은 영화를 보는 동안 trajectory가 **shared dynamics**를 보인다.

**Specific predictions:**
- Emotion-related regions에서 inter-subject trajectory alignment 높음
- Default mode / endogenous에서 alignment 낮음
- Alignment peak가 narrative의 emotionally intense moments와 일치
- Individual differences = endogenous trajectory amplitude (shared structure + individual scaling)

**Falsifiable:** 완전 random alignment (no shared dynamics) — self-refuting.

### H6 (optional, cross-dataset validation)
Horikawa (discrete 3s clips)와 Emo-FilM (continuous movies)에서 emotion-evoked brain state가 **공유 latent space**에서 대응한다.

**Specific predictions:**
- Horikawa fear video states ⊂ Emo-FilM fear-moment trajectory 영역
- GW-OT cross-dataset distance < chance
- Context effect (narrative vs isolated) = trajectory length 차이이지 공간 위치 차이 아님

**Falsifiable:** 두 데이터셋 latent space가 disjoint — context dependency가 전체를 다르게 만듬.

---

## 5. Methodology

### 5.1 Data

**Emo-FilM dataset (primary):**
- 30 subjects × 14 films × total ~2.5 hours
- Moment-by-moment emotion annotation: 50 items (Component Process Model framework; Scherer)
- **본인 rating (self-annotation), not crowd-sourced**
- Physiological: ECG, GSR, respiration (optional for arousal control)
- TR = 2s 가정 (standard)
- **Preprocessing 완료, 다른 서버에서 이미 가용**

**Horikawa dataset (optional, H6 validation):**
- 5 subjects × 2185 videos × 450 parcels
- 34 cat + 14 dim emotion ratings
- Role: cross-dataset state space validation

### 5.2 Stimulus processing

**V-JEPA2 (Meta 2025):**
- 1M+ hours video self-supervised pretraining
- 32-layer transformer architecture
- Temporal structure: attention over frames
- 각 TR (2s window)에서 V-JEPA2 features 추출
- Layer-wise: 32개 feature streams per time point

**Audio (optional):**
- Whisper 또는 Wav2vec2 embedding
- TRIBE 2026이 multimodal audio-video improve 보임
- Time-synchronized to fMRI TRs

### 5.3 Brain processing

**Parcellation:**
- Schaefer 400 cortical + 50 subcortical = 450 parcels
- Emo-FilM 서버에서 이미 전처리 완료
- Standard preprocessing: motion correction, slice timing, spatial smoothing (if applicable)

**Latent space extraction:**

Three candidate methods (for SQ1):

#### Method A (primary): BCNE (Brain-dynamic Convolutional Network Embedding)
**Reference:** Zhou et al. 2025 (Nature Computational Science)

**Intuition:**
Unsupervised deep learning method that discovers low-dimensional manifold structure in fMRI time series. Convolutional architecture captures temporal-spatial correlations; recursive manifold optimization refines embedding quality.

**Technical:**
- Input: fMRI (subjects × TR × 450 parcels)
- Conv encoder: captures temporal-spatial correlations
- Recursive manifold optimization: progressively incorporates deeper-level constraints from latent representation
- Deterministic mapping: new data can be projected to learned manifold
- Output: K-dim latent embedding per time point per subject (K ~ 10-30)

**Advantages over UMAP/t-SNE:**
- Temporal-aware (preserves time structure)
- Deterministic (not stochastic per-run)
- Denoised trajectory
- Published validation on naturalistic fMRI (movie watching)

**Application:**
Fit BCNE on Emo-FilM fMRI time series. Extract brain state trajectory per subject.

#### Method B (secondary/comparison): T-PHATE
**Reference:** Busch et al. 2023 (Nature Computational Science)

**Intuition:**
Temporal Potential of Heat-diffusion for Affinity-based Transition Embedding. Nonlinear manifold learning specifically for time-series data, exploiting autocorrelation structure to denoise.

**Technical:**
- Heat diffusion on data graph with temporal autocorrelation weighting
- Affinity-based transitions across time
- Output: low-dim embedding preserving temporal flow

**Application:**
Complementary to BCNE. Different inductive bias. Validation.

#### Method C (alternative): CEBRA (self-supervised mode)
**Reference:** Schneider et al. 2023 (Nature)

**Intuition:**
Contrastive learning for neural latent embedding. Can use auxiliary variables (behavior, time) or purely self-supervised.

**Technical:**
- InfoNCE loss: pull temporally adjacent samples together, push distant apart
- Neural network encoder
- Output: consistent low-dim embedding across subjects/sessions

**Application:**
Time-contrastive mode (no labels). Compare with BCNE latent structure.

### 5.4 Dynamical system identification

Once latent space extracted, characterize dynamics:

#### Method D (primary): Neural ODE
**Reference:** Chen et al. 2018 (NeurIPS)

**Intuition:**
Neural network학습한 연속 시간 dynamics. State x evolves continuously according to learned vector field f(x, t).

**Technical:**
$$\frac{dx}{dt} = f_\theta(x, t)$$

where $f_\theta$ is a neural network with parameters $\theta$.

**Learning:**
Given observed trajectory $\{x_t\}_{t=0}^T$, optimize $\theta$ to minimize trajectory prediction error. Uses adjoint method for gradient computation.

**Output:**
- Learned vector field $f_\theta$ (represents "forces" at each latent state)
- Can analyze: fixed points (where $f = 0$), flow field, Lyapunov exponents, attractor basins

**Application:**
Fit Neural ODE per emotion (or per emotional segment). Compare learned vector fields.

#### Method E: SLDS (Switching Linear Dynamical Systems)
**Reference:** gpSLDS (NeurIPS 2024)

**Intuition:**
Brain dynamics may have discrete states (emotions?) each with own linear dynamics. SLDS models discrete state transitions + continuous linear dynamics within each state.

**Technical:**
$$x_{t+1} = A_{z_t} x_t + b_{z_t} + \epsilon$$
$$z_t \sim \text{Markov transitions with probabilities } \pi$$

where $z_t$ is discrete state, $A_{z_t}$ is state-specific transition matrix.

**gpSLDS extension:**
Uses Gaussian Process to smooth state-specific dynamics, avoiding hard switches.

**Output:**
- Number of states K (interpretable as "emotion states"?)
- Per-state linear dynamics (eigenvalues = time constants)
- Transition matrix (state-to-state probabilities)

**Application:**
Fit SLDS on Emo-FilM trajectory. Compare discovered states with behavioral emotion labels.

#### Method F (alternative): SING — SDE Inference via Natural Gradients
**Reference:** NeurIPS 2025

**Intuition:**
Stochastic differential equation learning. Brain is noisy; deterministic ODE may miss stochasticity.

**Technical:**
$$dx = f_\theta(x) dt + \sigma_\theta(x) dW$$

where $W$ is Brownian motion, $\sigma$ is state-dependent noise.

**Output:**
- Drift $f$ and diffusion $\sigma$
- Uncertainty quantification per trajectory segment
- Noise-corrupted attractor analysis

**Application:**
Useful for small-sample uncertainty (n=30 but per-subject variance high).

#### Method G (alternative): Neural Koopman Operator
**Reference:** Lusch et al. 2018; Neural Koopman BRICK (IEEE TMI 2025)

**Intuition:**
Nonlinear dynamics become linear in appropriate "lifted" space. Koopman operator acts linearly on observables. Neural network learns the lifting.

**Technical:**
$$\mathcal{K} [g(x)] = g(f(x))$$

Koopman $\mathcal{K}$ is linear operator on functions $g$ of state $x$, acting on their composition with dynamics $f$.

Neural Koopman: learn encoder $\phi$ to lifted space where dynamics are linear:
$$\phi(x_{t+1}) = K \phi(x_t)$$

**Output:**
- Eigenvalues of $K$: oscillation frequencies, decay rates
- Eigenmodes: coherent dynamical patterns
- Linear control-theoretic analysis in lifted space

**Application:**
BRICK variant (IEEE TMI 2025) specifically for fMRI. Apply to emotion trajectories.

### 5.5 Analysis pipeline

```
Step 0: Environment setup
  - Port Emo-FilM data to working server
  - Verify V-JEPA2 feature extraction compatible with film frames
  - Install: torch, torchdiffeq, cebra, pot (for GW-OT if cross-dataset)

Step 1: Latent space extraction (SQ1)
  - Apply BCNE on Emo-FilM fMRI per subject
  - Output: subject × TR × K-dim latent
  - Compare with T-PHATE for robustness
  - Compute manifold geometry: dimensionality, curvature

Step 2: Per-emotion trajectory analysis (SQ2, H1)
  - Segment latent trajectories by moment-by-moment emotion labels
  - Per emotion: compute autocorrelation, extract time constant τ
  - Per emotion: compute trajectory length, speed, variance
  - Compare signatures across emotions (statistical tests)

Step 3: Dynamical system fitting (SQ2, H1, H2)
  - Option A: Neural ODE per emotion — vector field + fixed points
  - Option B: gpSLDS on full trajectory — discover states automatically
  - Option C: SING SDE with uncertainty
  - Compare outputs, select best-fitting per emotion

Step 4: Typology test (SQ3, H2)
  - K-means or bimodality test on emotion-level dynamical metrics
  - Disgust/surprise/fear cluster vs joy/nostalgia/awe cluster?
  - Statistical significance: permutation-based

Step 5: Stimulus-driven trajectory (SQ4, H3)
  - V-JEPA2 features time-aligned to fMRI TRs
  - Cross-correlation: V-JEPA2 feature(t-k) ↔ brain trajectory Δ(t)
  - Encoding model: features → trajectory velocity
  - Layer-wise: which layer drives which trajectory aspect
  - Endogenous vs driven variance decomposition

Step 6: Emotion transition analysis (SQ5, H4)
  - Identify emotion change points from moment-by-moment ratings
  - Trajectory discontinuity metric at transitions
  - Bifurcation analysis: fixed point structure change
  - Compare: narrative strong vs weak transitions

Step 7: Cross-subject alignment (SQ6, H5)
  - Shared Response Model (SRM) on 30 subjects' trajectories
  - Or: dynamic time warping per emotion segment
  - Alignment score per region × emotion
  - Individual difference characterization

Step 8 (optional): Cross-dataset validation (H6)
  - Apply same latent space method to Horikawa
  - GW-OT between Horikawa state distribution and Emo-FilM trajectory density
  - Test: do Horikawa fear-video states lie in Emo-FilM fear-moment trajectory regions?
```

### 5.6 Chapter-by-chapter thesis structure

```
Chapter 1: Introduction
  1.1 Phenomenological temporality of emotion
  1.2 Snapshot assumption in emotion neuroscience
  1.3 Paradigm shift potential: emotion as dynamical system
  1.4 Research questions and hypotheses
  1.5 Thesis organization

Chapter 2: Theoretical Framework and Related Work
  2.1 Emotion theories: categorical, dimensional, constructionist
  2.2 Dynamical systems in neuroscience
  2.3 Temporal receptive fields and brain dynamics
  2.4 Recent advances in DL latent dynamics
  2.5 Gap and contribution

Chapter 3: Methods
  3.1 Emo-FilM dataset
  3.2 V-JEPA2 feature extraction
  3.3 Latent space methods: BCNE, T-PHATE, CEBRA
  3.4 Dynamical system methods: Neural ODE, SLDS, Koopman, SING
  3.5 Analysis pipeline

Chapter 4: Results
  4.1 Latent space geometry of emotion-related brain activity
  4.2 Per-emotion dynamical signatures
  4.3 Fast-onset vs slow-building typology
  4.4 Stimulus-driven vs endogenous decomposition
  4.5 Emotion transitions and bifurcations
  4.6 Cross-subject consistency

Chapter 5: Discussion
  5.1 Emotion as dynamical system: theoretical implications
  5.2 Comparison with classical dynamical emotion studies (eLife 2025, Pessoa 2024)
  5.3 Comparison with arousal universal embedding (Raut Nature 2025)
  5.4 Methodological contributions
  5.5 Limitations (n=30 × 14 films, TR=2s, subjective ratings)
  5.6 Future work: cross-dataset, fMRI+MEG, individual differences

Chapter 6: Conclusion
```

---

## 6. Detailed Method Explanations

### 6.1 Why Latent Dynamics?

**Problem with raw fMRI time series:**
- 450 parcels × thousands of TRs = high-dimensional noisy signal
- Much of variance is task-unrelated (motion, respiration, noise)
- Direct analysis of raw signals obscures structure

**Solution: Latent dynamical systems**
Assume observed brain activity $x_t \in \mathbb{R}^{450}$ is generated by low-dimensional latent state $z_t \in \mathbb{R}^K$ ($K \ll 450$) with dynamics:
$$z_{t+1} = g(z_t, u_t) + \epsilon$$
$$x_t = h(z_t) + \eta$$

where $u_t$ is external input (stimulus), $\epsilon$ and $\eta$ are noise.

**Goal:** Infer $z_t$, $g$, $h$ from observed $x_t$.

**Why:**
- Low-dim $z_t$ captures meaningful "state"
- Function $g$ captures temporal evolution rules
- Analyses (time constant, attractor, etc.) happen in clean latent space

### 6.2 BCNE (detail)

**From Zhou et al. 2025 Nature Computational Science:**

**Problem with UMAP/t-SNE:**
- Ignore temporal order
- Stochastic (different runs = different embeddings)
- No new-data projection

**BCNE solution:**
1. **Convolutional architecture:** captures temporospatial correlations in time series
2. **Recursive manifold optimization:** progressively refine latent structure from coarse to fine
3. **Deterministic encoder:** new data projects reproducibly
4. **Deeper-level constraints:** uses latent itself to refine

**Pipeline:**
```
Input: fMRI time series X (T × D)
Encoder (CNN): X → Z (T × K)
Loss: reconstruction + manifold smoothness + temporal continuity
Recursive: use learned Z to refine encoder
Output: Z trajectory + deterministic mapping for test data
```

**Validated on:**
- Cognitive event segmentation
- Learning stages
- Active vs passive movement

**Why perfect for our use:**
- Naturalistic fMRI (movie)
- Unsupervised (label-free)
- Temporal trajectory extraction
- Deterministic (compare across subjects reliably)

### 6.3 Neural ODE (detail)

**From Chen et al. 2018 NeurIPS:**

**Setting:**
Given trajectory $\{x_t\}$, want to learn dynamics that generated it.

**Forward:**
$$x(t) = x(0) + \int_0^t f_\theta(x(\tau), \tau) d\tau$$

Integrate ODE from initial condition.

**Adjoint method (backward):**
$$\frac{da(t)}{dt} = -a(t)^T \frac{\partial f_\theta}{\partial x}$$

Solve adjoint ODE backward in time to compute gradients — memory efficient.

**Interpretation of learned $f$:**
- $f(x^*) = 0$: fixed point (stable if eigenvalues of Jacobian are negative)
- Flow field: vector $f$ at each point tells direction of motion
- Lyapunov exponent: exponential divergence of nearby trajectories

**Emotion application:**
Fit Neural ODE per emotion segment. Compare:
- Disgust ODE: strong attractor (all nearby trajectories converge)
- Joy ODE: weaker attractor or drift (slower convergence)
- Fear ODE: pre-attractor build-up region?

Eigenvalue analysis at fixed points:
- Real negative eigenvalues → stable attractor
- Complex eigenvalues → oscillation
- Real positive → unstable (shouldn't happen in good model)

### 6.4 SLDS (detail)

**From Linderman et al. 2017 + gpSLDS (NeurIPS 2024):**

**Model:**
Discrete state $z_t \in \{1, ..., K\}$ with Markov transitions:
$$P(z_{t+1} | z_t) = \pi[z_t, z_{t+1}]$$

Continuous state $x_t$ given discrete state:
$$x_{t+1} = A_{z_t} x_t + b_{z_t} + \epsilon_t$$

Observations:
$$y_t = C x_t + \eta_t$$

**Inference:**
- Forward-backward algorithm on discrete states
- Kalman filter on continuous
- Variational EM for parameters

**gpSLDS extension:**
Replace discrete hard switches with Gaussian Process smoothing:
$$x_{t+1} \sim \mathcal{GP}(f(x_t, z_t))$$

Allows smooth transitions between state dynamics.

**Emotion interpretation:**
- $K$ = number of discovered emotion states (compare with behavioral labels)
- $A_k$ eigenvalues = time constants per state
- $\pi$ = emotion transition probabilities
- States may or may not correspond to human-labeled emotions

### 6.5 Neural Koopman (detail)

**From Lusch et al. 2018; BRICK 2025:**

**Koopman operator theory:**
For autonomous nonlinear dynamics $x_{t+1} = f(x_t)$, the Koopman operator $\mathcal{K}$ is linear operator on observable functions:
$$\mathcal{K}g(x) = g(f(x))$$

$\mathcal{K}$ is infinite-dimensional but linear. Finite-dimensional invariant subspaces allow tractable analysis.

**Deep learning approach:**
Learn encoder $\phi: \mathbb{R}^D \to \mathbb{R}^M$ (lifted space) such that:
$$\phi(f(x)) = K \phi(x)$$

where $K$ is learnable linear operator.

**Learning objective:**
$$\mathcal{L} = \|\phi(x_{t+1}) - K\phi(x_t)\|^2 + \|x_t - \text{decode}(\phi(x_t))\|^2$$

**Interpretation of K:**
- Eigenvalues $\lambda_i$: $|\lambda_i| < 1$ decaying modes, $|\lambda_i| = 1$ oscillating, $|\lambda_i| > 1$ growing
- Eigenvectors = Koopman eigenfunctions = coherent dynamical patterns

**BRICK variant (IEEE TMI 2025):**
Specifically for fMRI. Incorporates control signal (external input = stimulus).

**Emotion application:**
- Eigenmodes across emotions: do different emotions have different dominant modes?
- Decay rates: emotion-specific time scales
- Control module: how stimulus input drives dynamics

### 6.6 Cross-correlation and Granger causality for stimulus driving

**For SQ4 (stimulus → trajectory):**

**Cross-correlation:**
$$r_k = \frac{\text{cov}(s_{t-k}, \dot{z}_t)}{\sigma_s \sigma_{\dot{z}}}$$

where $s_t$ is V-JEPA2 feature (or single component), $\dot{z}_t$ is trajectory velocity.

**Granger causality:**
Does adding stimulus history improve prediction of trajectory beyond trajectory's own history?

Compare:
- $M_1$: $\dot{z}_t$ predicted from $\{z_{t-1}, ..., z_{t-p}\}$
- $M_2$: $\dot{z}_t$ predicted from $\{z_{t-1}, ..., z_{t-p}\} \cup \{s_{t-1}, ..., s_{t-q}\}$

$M_2$ significantly better → stimulus "Granger causes" trajectory.

**Encoding model:**
Linear regression: $\dot{z}_t = \beta \cdot s_t^{(l)}$ per V-JEPA2 layer $l$.

$R^2$ per layer = which layer best predicts trajectory changes.

---

## 7. Risks and Mitigation

### 7.1 Methodological risks

**Risk:** BCNE/Neural ODE on emotion fMRI has no precedent — may not work
**Mitigation:**
- Have 3 latent methods (BCNE, T-PHATE, CEBRA) — if one fails, try others
- Have 4 dynamics methods (Neural ODE, SLDS, SING, Koopman) — diverse tools
- Simulation validation: generate synthetic trajectories with known dynamics, check methods recover them

**Risk:** n=30 with 14 films = limited stimulus variation
**Mitigation:**
- Group-level analyses primary
- SING for uncertainty quantification
- Per-film analysis as robustness check
- Emo-FilM is relatively large compared to peer studies

**Risk:** TR=2s limits fast dynamics detection
**Mitigation:**
- Frame hypotheses as TR-scale (multiple TRs = "fast", tens of TRs = "slow")
- Acknowledge as limitation; future MEG/EEG direction

### 7.2 Theoretical risks

**Risk:** Raut et al. Nature 2025 arousal embedding may explain all dynamics
**Mitigation:**
- Explicitly test arousal-controlled analysis
- Regress arousal out, check residual dynamics
- Show arousal explains PART but emotion-specific signatures remain
- Frame as complementary, not competing

**Risk:** eLife 2025 dynamic fMRI networks of emotion may have done similar findings
**Mitigation:**
- Explicit differentiation: they use classical ICA/Gaussian fitting; we use DL latent dynamics
- Our per-emotion signatures are finer
- Our stimulus-driven decomposition is novel

**Risk:** H1 (distinct signatures) may fail — emotions homogeneous
**Mitigation:**
- Negative result is still scientifically meaningful ("emotions are homogeneous dynamical class")
- Fallback: focus on H3 (stimulus-driven) and H5 (cross-subject), which may independently succeed

### 7.3 Data risks

**Risk:** Emo-FilM preprocessing compatibility with our pipeline
**Mitigation:** Already preprocessed; verify TR, parcellation, format on Day 1.

**Risk:** V-JEPA2 feature extraction on Emo-FilM frames (not Horikawa videos)
**Mitigation:** Same model, just re-run. 1-2 days.

---

## 8. Expected Outcomes

### 8.1 Primary contribution

1. **First systematic DL latent dynamics characterization of emotion fMRI**
2. **Per-emotion dynamical signature quantification** — extends Pessoa (single emotion) to full spectrum
3. **Stimulus-driven vs endogenous trajectory decomposition** — novel in emotion domain
4. **Theoretical reframing** — emotion as dynamical process, not snapshot pattern

### 8.2 Full-success narrative

"감정은 정적 pattern이 아니라 뇌의 latent dynamical system 위 trajectory이다. 서로 다른 감정은 distinct signatures (time scale, attractor, trajectory shape)로 구별되며, 이 signatures는 sensory-reactive와 constructed-contextual 두 class로 분류된다. 시각 자극이 trajectory를 systematic하게 driving하되 endogenous component가 공존한다. 이 framework은 감정 뇌과학의 기본 가정 (snapshot)을 theoretically challenge하고 methodologically modernize한다."

### 8.3 Fallback narratives (각 hypothesis별)

- H1 실패 → "Emotions are dynamically homogeneous — distinct patterns but same temporal structure"
- H2 실패 → "Emotion typology is continuous, not dichotomous"
- H3 실패 → "Trajectories are predominantly endogenous, stimulus input is permissive not driving"
- H4 실패 → "Emotion transitions are smooth — bifurcation only in narrative-induced shocks"
- H5 실패 → "Individual dynamics dominate — emotion is personal, not universal"
- H6 실패 → "Context-specific — Horikawa evoked ≠ Emo-FilM sustained"

모든 실패 시나리오도 **scientific finding**이며 thesis contribution.

---

## 9. Key References (detailed)

### 9.1 Direct precedents (emotion dynamics)

**"Dynamic fMRI networks of emotion" (Janssen et al. 2025, eLife)**
- Forrest Gump 영화 fMRI, 4 감정 networks의 time course
- ICA + Gaussian curve fitting — **classical methods**
- **우리가 다르게:** BCNE/Neural ODE 등 DL latent dynamics, 체계적 per-emotion signatures

**"Emotions in the brain are dynamic and contextually dependent" (eNeuro 2025)**
- 음악-induced emotion의 HMM 분석
- **Discrete states 가정**
- **우리가 다르게:** Continuous latent dynamics, HMM보다 풍부한 state-within dynamics (SLDS)

**Pessoa group (2024 eLife, others)**
- Threat trajectory analysis with linear methods
- **Single emotion focus**
- **우리가 다르게:** 전체 감정 spectrum, nonlinear DL methods

**Raut et al. (Nature 2025)**
- Arousal as universal 1-d manifold
- Mouse + human, pupil-based
- **우리가 다르게:** Emotion-specific dynamics 넘어 arousal로 환원 안 됨을 test

### 9.2 Latent dynamics methods foundations

**BCNE (Zhou et al. 2025, Nature Computational Science)**
- Brain-dynamic convolutional-network-based embedding
- Unsupervised trajectory extraction
- Validated on multiple fMRI datasets

**T-PHATE (Busch et al. 2023, Nature Computational Science)**
- Temporal manifold learning
- Heat diffusion + temporal autocorrelation
- Naturalistic fMRI (Sherlock, Friends)

**CEBRA (Schneider et al. 2023, Nature)**
- Contrastive neural embedding
- Label-informed or self-supervised
- Motor cortex + calcium imaging

**Neural ODE (Chen et al. 2018, NeurIPS)**
- Continuous-time neural networks
- Adjoint method
- Foundation for modern dynamical learning

**gpSLDS (Linderman et al. NeurIPS 2024)**
- Gaussian Process Switching Linear Dynamical Systems
- Smooth transitions between discrete-like states

**SING (NeurIPS 2025)**
- Stochastic DE Inference with Natural Gradients
- Uncertainty quantification

**Neural Koopman BRICK (IEEE TMI 2025)**
- Koopman operator for fMRI
- Task-related control module

### 9.3 Theoretical background

**Hasson et al. 2008 (Nature Neuroscience)**
- Temporal receptive field hierarchy in visual cortex
- Foundation for "slow vs fast regions" concept

**Chen et al. 2016 (Neuron)**
- Hierarchical processing of natural events
- TRF in naturalistic viewing

**Barrett & Lindquist 2012 (Behavioral Brain Sciences)**
- Theory of constructed emotion
- Core affect + conceptualization
- Implicit temporal process

**Mathis et al. 2025 (Nature Reviews Neuroscience)**
- "Joint modelling of brain and behaviour dynamics with AI"
- Review of DL latent dynamics methods in neuroscience

### 9.4 Cross-dataset validation

**Horikawa et al. 2020 (iScience)** — cross-dataset source for H6
**Takeda et al. 2025 (iScience)** — GW-OT neuroscience toolbox for cross-dataset
**Thual et al. 2025 (J Neurosci Methods)** — GW-OT implementation

---

## 10. Novelty Statement (thesis opening)

> "Emotion neuroscience has long treated emotion as static brain patterns — categorical states, dimensional coordinates, or response profiles frozen in time. This thesis argues and empirically demonstrates that emotion is more fundamentally understood as a dynamical system: a trajectory through latent neural space with characteristic temporal signatures. Using the Emo-FilM dataset (30 subjects watching naturalistic films with moment-by-moment emotion ratings) and modern deep learning methods for latent dynamical system identification (BCNE, Neural ODE, gpSLDS, Neural Koopman), we perform the first systematic characterization of emotion as dynamics: extracting per-emotion dynamical signatures (time scales, attractor structure, trajectory shape), identifying a fast-onset vs slow-building typology across emotion categories, decomposing trajectories into stimulus-driven and endogenous components via V-JEPA2 video features, and analyzing emotion transition structure. These results reframe emotion — both theoretically and methodologically — from representation to process."

---

## 11. Timeline for Master's Thesis

**Given Emo-FilM preprocessed and available:**

```
Weeks 1-2: Pipeline setup
  - Port Emo-FilM to working server
  - V-JEPA2 feature extraction on film frames
  - BCNE / T-PHATE / CEBRA environment

Weeks 2-3: Latent space extraction
  - BCNE training
  - Manifold geometry analysis
  - Per-subject trajectory

Weeks 3-5: Dynamical characterization
  - Per-emotion segmentation
  - Time constant, signature extraction
  - Neural ODE / SLDS fitting
  - H1, H2 testing

Weeks 5-6: Stimulus coupling
  - V-JEPA2 feature time alignment
  - Cross-correlation, Granger causality
  - Layer-wise encoding
  - H3 testing

Weeks 6-7: Transitions + cross-subject
  - Bifurcation analysis (H4)
  - Cross-subject alignment (H5)
  - Cross-dataset validation (H6, if time)

Week 7-8: Writing
  - Chapters 1, 3, 4, 5 draft
  - Figures
  - Final revision
```

---

## 12. References

### Direct precedents (emotion dynamics)

1. **Janssen, N., Elvira, U.K.A., Janssen, J., & van Erp, T.G.M.** (2025). Dynamic fMRI networks of emotion. *eLife*, reviewed preprint. https://elifesciences.org/reviewed-preprints/106070

2. **[Music HMM study]** (2025). Emotions in the brain are dynamic and contextually dependent: Using music to measure affective transitions. *eNeuro*, 12(7), ENEURO.0184-24.2025.

3. **Pessoa, L., et al.** (2024). Human brain dynamics and spatiotemporal trajectories during threat processing. *eLife*, 13:102539.

4. **Raut, R.V., Rosenthal, Z.P., Wang, X., Miao, Z., Zhang, Z., Lee, J.-M., Raichle, M.E., Bauer, A.Q., Brunton, S.L., Brunton, B.W., & Kutz, J.N.** (2025). Arousal as a universal embedding for spatiotemporal brain dynamics. *Nature*, 647(8089), 454-461. https://doi.org/10.1038/s41586-025-09544-4

5. **Saarimäki, H., Glerean, E., Smirnov, D., Mynttinen, H., Jääskeläinen, I.P., Sams, M., & Nummenmaa, L.** (2022). Classification of emotion categories based on functional connectivity patterns of the human brain. *NeuroImage*, 247, 118800.

### Latent dynamics methods (emotion fMRI에 미적용 — 우리가 first-apply)

6. **Zhou, Z., Liu, J., Wu, W.E., Fang, R., Liu, S., et al.** (2025). Revealing neurocognitive and behavioral patterns through unsupervised manifold learning of dynamic brain data. *Nature Computational Science*, 5, 911. https://doi.org/10.1038/s43588-025-00911-9 [BCNE]

7. **Busch, E.L., Huang, J., Benz, A., Wallenstein, T., Lajoie, G., Wolf, G., Krishnaswamy, S., & Turk-Browne, N.B.** (2023). Multi-view manifold learning of human brain-state trajectories. *Nature Computational Science*, 3, 240-253. https://doi.org/10.1038/s43588-023-00419-0 [T-PHATE]

8. **Schneider, S., Lee, J.H., & Mathis, M.W.** (2023). Learnable latent embeddings for joint behavioural and neural analysis. *Nature*, 617, 360-368. https://doi.org/10.1038/s41586-023-06031-6 [CEBRA]

9. **Chen, R.T.Q., Rubanova, Y., Bettencourt, J., & Duvenaud, D.** (2018). Neural ordinary differential equations. *Advances in Neural Information Processing Systems (NeurIPS 2018)*, 31, 6571-6583.

10. **Linderman, S.W., Johnson, M.J., Miller, A.C., Adams, R.P., Blei, D.M., & Paninski, L.** (2017). Bayesian learning and inference in recurrent switching linear dynamical systems. *Artificial Intelligence and Statistics (AISTATS 2017)*, PMLR 54:914-922. [Original SLDS]

11. **[gpSLDS reference]** (2024). Modeling latent neural dynamics with Gaussian Process switching linear dynamical systems. *Advances in Neural Information Processing Systems (NeurIPS 2024)*.

12. **[SING reference]** (2025). SING: SDE inference via natural gradients. *Advances in Neural Information Processing Systems (NeurIPS 2025)*.

13. **Lusch, B., Kutz, J.N., & Brunton, S.L.** (2018). Deep learning for universal linear embeddings of nonlinear dynamics. *Nature Communications*, 9, 4950. https://doi.org/10.1038/s41467-018-07210-0 [Deep Koopman]

14. **Chow, D., Dan, X., Styner, M., & Wu, G.** (2024). Understanding brain dynamics through neural Koopman operator with structure-function coupling. *MICCAI 2024*. https://doi.org/10.1007/978-3-031-72069-7_48

15. **[BRICK]** (2025). Understanding brain functional dynamics through neural Koopman operator with control mechanism. *IEEE Transactions on Medical Imaging*.

### Related label-free / data-driven approaches

16. **Lee, J., Han, D.D., Oh, S.Y., & Cha, J.** (2025). Awe is characterized as an ambivalent affect in the human behavior and cortex. *Communications Psychology*, 3, 123. https://doi.org/10.1038/s44271-025-00299-2

17. **Jang, G., & Kragel, P.A.** (2025). Understanding human amygdala function with artificial neural networks. *Journal of Neuroscience*, 45(18), e1436242025.

18. **Takeda, K., Abe, K., Kitazono, J., & Oizumi, M.** (2025). Unsupervised alignment reveals structural commonalities and differences in neural representations of natural scenes across individuals and brain areas. *iScience*, 28, 112298.

19. **Thual, A., Benchetrit, Y., Geilert, F., et al.** (2025). Unsupervised alignment in neuroscience: Introducing a toolbox for Gromov-Wasserstein optimal transport. *Journal of Neuroscience Methods*, 415, 110369.

### Theoretical background

20. **Hasson, U., Yang, E., Vallines, I., Heeger, D.J., & Rubin, N.** (2008). A hierarchy of temporal receptive windows in human cortex. *Journal of Neuroscience*, 28(10), 2539-2550. https://doi.org/10.1523/JNEUROSCI.5487-07.2008

21. **Chen, J., Leong, Y.C., Honey, C.J., Yong, C.H., Norman, K.A., & Hasson, U.** (2016). Shared memories reveal shared structure in neural activity across individuals. *Nature Neuroscience*, 20(1), 115-125.

22. **Runyan, C.A., Piasini, E., Panzeri, S., & Harvey, C.D.** (2017). Distinct timescales of population coding across cortex. *Nature*, 548, 92-96.

23. **Chien, H.-Y.S., & Honey, C.J.** (2020). Constructing and forgetting temporal context in the human cerebral cortex. *Neuron*, 106(4), 675-686.

24. **Murray, J.D., Bernacchia, A., Freedman, D.J., et al.** (2014). A hierarchy of intrinsic timescales across primate cortex. *Nature Neuroscience*, 17, 1661-1663.

### Emotion theory (for conceptual grounding)

25. **Barrett, L.F.** (2017). The theory of constructed emotion: an active inference account of interoception and categorization. *Social Cognitive and Affective Neuroscience*, 12(1), 1-23.

26. **Barrett, L.F., & Lindquist, K.A.** (2012). The brain basis of emotion: a meta-analytic review. *Behavioral and Brain Sciences*, 35(3), 121-143.

27. **Scherer, K.R.** (2001). Appraisal considered as a process of multilevel sequential checking. *Appraisal processes in emotion: Theory, methods, research*, 92(120), 57. [Component Process Model — basis for Emo-FilM annotation]

28. **Moors, A., Ellsworth, P.C., Scherer, K.R., & Frijda, N.H.** (2013). Appraisal theories of emotion: State of the art and future development. *Emotion Review*, 5(2), 119-124.

29. **Juechems, K., & Summerfield, C.** (2022). Emotions as computations. *Neuroscience & Biobehavioral Reviews*, 143, 104977.

### Review and methodological surveys

30. **Mathis, M.W., Perez Rotondo, A., Chang, E.F., Tolias, A.S., & Mathis, A.** (2025). Joint modelling of brain and behaviour dynamics with AI. *Nature Reviews Neuroscience*. https://doi.org/10.1038/s41583-025-00996-1

31. **Doerig, A., Sommers, R.P., Seeliger, K., Richards, B., Ismael, J., Lindsay, G.W., ... & Kietzmann, T.C.** (2023). The neuroconnectionist research programme. *Nature Reviews Neuroscience*, 24, 431-450.

32. **Sucholutsky, I., Muttenthaler, L., Weller, A., et al.** (2023). Getting aligned on representational alignment. *arXiv preprint arXiv:2310.13018*.

### Emo-FilM and related datasets

33. **Morgenroth, E., Saviola, F., Gilardeau, J., et al.** (2025). Emo-FilM: A multimodal dataset for affective neuroscience using naturalistic stimuli. *Scientific Data*, 12, 04803. https://doi.org/10.1038/s41597-025-04803-5

34. **Horikawa, T., Cowen, A.S., Keltner, D., & Kamitani, Y.** (2020). The neural representation of visually evoked emotion is high-dimensional, categorical, and distributed across transmodal brain regions. *iScience*, 23(5), 101060.

35. **Sonkusare, S., Breakspear, M., & Guo, C.** (2019). Naturalistic stimuli in neuroscience: critically acclaimed. *Trends in Cognitive Sciences*, 23(8), 699-714.

### Video foundation models (stimulus encoder)

36. **Assran, M., Duval, Q., Misra, I., et al.** (2025). V-JEPA 2: Self-supervised video models enable understanding, prediction and planning. *arXiv preprint arXiv:2506.09985*. https://arxiv.org/abs/2506.09985

37. **Tong, Z., Song, Y., Wang, J., & Wang, L.** (2022). VideoMAE: Masked autoencoders are data-efficient learners for self-supervised video pre-training. *Advances in Neural Information Processing Systems (NeurIPS 2022)*, 35, 10078-10093.

38. **Radford, A., Kim, J.W., Hallacy, C., et al.** (2021). Learning transferable visual models from natural language supervision. *International Conference on Machine Learning (ICML 2021)* [CLIP].

### Key dynamical neuroscience precedents

39. **Shine, J.M., Breakspear, M., Bell, P.T., Ehgoetz Martens, K., Shine, R., Koyejo, O., Sporns, O., & Poldrack, R.A.** (2019). Human cognition involves the dynamic integration of neural activity and neuromodulatory systems. *Nature Neuroscience*, 22, 289-296.

40. **Shine, J.M.** (2019). The thalamus integrates the macrosystems of the brain to facilitate complex, adaptive brain network dynamics. *Progress in Neurobiology*, 180, 101634.

41. **Pandarinath, C., O'Shea, D.J., Collins, J., et al.** (2018). Inferring single-trial neural population dynamics using sequential auto-encoders. *Nature Methods*, 15, 805-815. [LFADS — sequential VAE foundation]

42. **Zhou, D., & Wei, X.X.** (2020). Learning identifiable and interpretable latent models of high-dimensional neural activity using pi-VAE. *Advances in Neural Information Processing Systems (NeurIPS 2020)*, 33, 7234-7247. [pi-VAE]

43. **Kao, J.C., Nuyujukian, P., Ryu, S.I., Churchland, M.M., Cunningham, J.P., & Shenoy, K.V.** (2015). Single-trial dynamics of motor cortex and their applications to brain-machine interfaces. *Nature Communications*, 6, 7759.

### Preprocessing and parcellation

44. **Schaefer, A., Kong, R., Gordon, E.M., et al.** (2018). Local-global parcellation of the human cerebral cortex from intrinsic functional connectivity MRI. *Cerebral Cortex*, 28(9), 3095-3114.

45. **Tian, Y., Margulies, D.S., Breakspear, M., & Zalesky, A.** (2020). Topographic organization of the human subcortex unveiled with functional connectivity gradients. *Nature Neuroscience*, 23, 1421-1432.

### Related dynamics applied to cognitive/neural data

46. **Cohen, M.X.** (2011). It's about time. *Frontiers in Human Neuroscience*, 5, 2.

47. **Saarimäki, H., Ejtehadian, L.F., Glerean, E., Jääskeläinen, I.P., Vuilleumier, P., Sams, M., & Nummenmaa, L.** (2018). Distributed affective space represents multiple emotion categories across the human brain. *Social Cognitive and Affective Neuroscience*, 13(5), 471-482.

48. **Kragel, P.A., Kano, M., Van Oudenhove, L., Ly, H.G., Dupont, P., Rubio, A., Delon-Martin, C., Bonaz, B.L., Manuck, S.B., Gianaros, P.J., Ceko, M., Reynolds Losin, E.A., Woo, C.W., Nichols, T.E., & Wager, T.D.** (2018). Generalizable representations of pain, cognitive control, and negative emotion in medial frontal cortex. *Nature Neuroscience*, 21, 283-289.

### Comprehensive neural representations (multimodal, related to SQ4)

49. **[Comprehensive neural representations through multimodal DL]** (2025). *eLife*, reviewed preprint 107607.

50. **Khosla, M., Murty, N.A.R., & Kanwisher, N.** (2021). Cortical response to naturalistic stimuli is largely predictable with deep neural networks. *Science Advances*, 7(22), eabe7547.

### Brain Algebra / compositional (context)

51. **Ferrante, M., Boccato, T., & Toschi, N.** (2025). Evidence for compositionality in fMRI visual representations via Brain Algebra. *Communications Biology*, 8, 942.

### Additional precedents (emotion dynamics and naturalistic viewing)

52. **Bo, K., Cui, L., Yin, S., Hu, Z., Hong, X., Kim, S., Keil, A., & Ding, M.** (2022). Decoding the temporal dynamics of affective scene processing. *NeuroImage*, 261, 119532. https://doi.org/10.1016/j.neuroimage.2022.119532
    *→ Direct precedent for H1-H2: uses EEG-fMRI + MVPA + temporal generalization to characterize temporal stability of affective responses; precedes our DL latent dynamics approach*

53. **Chang, L.J., Jolly, E., Cheong, J.H., Rapuano, K.M., Greenstein, N., Chen, P.-H.A., & Manning, J.R.** (2021). Endogenous variation in ventromedial prefrontal cortex state dynamics during naturalistic viewing reflects affective experience. *Science Advances*, 7, eabf7129. https://doi.org/10.1126/sciadv.abf7129
    *→ Core precedent for H5 cross-subject alignment: vmPFC state dynamics during 45-min TV drama. State-transition characterization mirrors our BCNE/Neural ODE approach*

54. **Finn, E.S., & Bandettini, P.A.** (2021). Movie-watching outperforms rest for functional connectivity-based prediction of behavior. *NeuroImage*, 235, 117963. https://doi.org/10.1016/j.neuroimage.2021.117963
    *→ Justifies naturalistic stimulus choice over resting-state; movie clips with high social/emotional content best predict traits*

55. **Kringelbach, M.L., Sanz Perl, Y., Tagliazucchi, E., & Deco, G.** (2023). Toward naturalistic neuroscience: Mechanisms underlying the flattening of brain hierarchy in movie-watching compared to rest and task. *Science Advances*, 9(2), eade6049. https://doi.org/10.1126/sciadv.ade6049
    *→ Brain hierarchy flattening during movie-watching via GCAT framework; relevant to H4 (transitions) and stimulus-driven vs endogenous decomposition (SQ4)*

56. **Sato, W., Kochiyama, T., Abe, N., Asano, K., & Yoshikawa, S.** (2026). Neural network dynamics associated with facial and subjective emotional responses. *Communications Biology*, 9, 91. https://doi.org/10.1038/s42003-025-09361-5
    *→ Dynamic causal modeling of emotion networks; facial vs subjective dissociation. Supports multi-component emotion analysis (H1)*

57. **Gao, C., Ajith, S., & Peelen, M.V.** (2025). Object representations drive emotion schemas across a large and diverse set of daily-life scenes. *Communications Biology*, 8, 697. https://doi.org/10.1038/s42003-025-08145-1
    *→ Object representations (V-JEPA proxy) predict affect without explicit emotion labels; supports SQ4 stimulus-driven trajectory hypothesis*

58. **Li, X., Zhou, Y., Dvornek, N., Zhang, M., Gao, S., Zhuang, J., Scheinost, D., Staib, L.H., Ventola, P., & Duncan, J.S.** (2021). BrainGNN: Interpretable Brain Graph Neural Network for fMRI Analysis. *Medical Image Analysis*, 74, 102233. https://doi.org/10.1016/j.media.2021.102233
    *→ Graph neural network for interpretable ROI discovery; methodological alternative for complementing latent dynamics analysis*

### Extended bibliography (comprehensive literature review)

#### Naturalistic emotion dynamics (additional precedents)

59. **Aliko, S., Huang, J., Gheorghiu, F., Meliss, S., & Skipper, J.I.** (2020). A naturalistic neuroimaging database for understanding the brain using ecological stimuli. *Scientific Data*, 7, 347. *→ Naturalistic neuroimaging database — relevant context for Emo-FilM*

60. **[Dynamic brain connectivity predicts emotional arousal during naturalistic movie-watching]** (2025). *→ Direct precedent: dynamic connectivity × emotion arousal in movies*

61. **[Integration of affective cues in context-rich and dynamic scenes varies across individuals]** (2025). *→ Context-dependent affective integration*

62. **[Common and distinct neurofunctional signatures of dynamic naturalistic emotion regulation strategies]** (2026). *→ Dynamic emotion regulation signatures*

63. **[Functional architecture of cerebral cortex during naturalistic movie watching]** (2024). *→ Cortical architecture during naturalistic viewing*

64. **[Processing of natural scenes in the human pulvinar]** (2025). *→ Subcortical involvement in naturalistic scene processing*

65. **[A systems identification approach using Bayes factors to deconstruct the brain bases of emotion regulation]** (2024). *→ Systems identification framework for emotion regulation*

66. **[Representational differentiation and integration within the hippocampal circuit during naturalistic stimuli]** (2026). *→ Hippocampal dynamics during naturalistic viewing*

#### Emotion-specific neural signatures (arousal, threat, valence)

67. **[A neurofunctional signature of affective arousal generalizes across valence domains and distinguishes subjective experience from autonomic reactivity]** (2025). *Nature Communications*. *→ BAAS arousal signature — critical contrast with Raut 2025 arousal embedding*

68. **Reddan, M.C., Wager, T.D., et al.** (2024). A neural signature for the subjective experience of threat anticipation under uncertainty. *Nature Communications*. *→ SUITAS threat anticipation signature*

69. **Chen, F., et al.** (2021). A distributed fMRI-based signature for the subjective experience of fear. *Nature Communications*, 12, 2772. *→ Distributed fear signature*

70. **[Decoding of arousal and valence from fMRI data obtained during emotion inductions]** (2026). *→ Arousal/valence decoding during induced emotion*

71. **[Neural Predictors of Fear Depend on the Situation]** (2024). *→ Situation-dependent fear encoding*

72. **Kragel, P.A., et al.** (2018). Generalizable representations of pain, cognitive control, and negative emotion in medial frontal cortex. *Nature Neuroscience*, 21, 283-289. *→ Negative emotion signature*

73. **[Mapping the emotional homunculus with fMRI]** (2024). *→ Somatotopic emotion representation*

74. **[Decoding affect in emotional body language: valence representation in the action observation network]** (2025). *→ Body language affect decoding in AON*

75. **[Neural representation of mixed feelings during real-time processing of negative words in pun-humor]** (2025). *→ Mixed feelings decoding, relevant for compound emotion hypothesis*

#### Principal gradient and cortical organization

76. **Margulies, D.S., Ghosh, S.S., Goulas, A., Falkiewicz, M., Huntenburg, J.M., Langs, G., et al.** (2016). Situating the default-mode network along a principal gradient of macroscale cortical organization. *Proceedings of the National Academy of Sciences*, 113(44), 12574-12579. *→ Principal gradient — foundational for understanding DMN emotion dynamics*

77. **Pessoa, L.** (2017). A network model of the emotional brain. *Trends in Cognitive Sciences*, 21(5), 357-371. *→ Network emotion theory*

78. **Barrett, L.F., & Satpute, A.B.** (2013). Large-scale brain networks in affective and social neuroscience. *Current Opinion in Neurobiology*, 23(3), 361-372. *→ Functional architecture for emotion*

79. **Lettieri, G., Handjaras, G., Ricciardi, E., Leo, A., Papale, P., Betta, M., Pietrini, P., & Cecchetti, L.** (2019). Emotionotopy in the human right temporo-parietal cortex. *Nature Communications*, 10, 5568. *→ Topographic emotion organization — direct precedent for H1 signature hypothesis*

#### Emotion theory and taxonomy

80. **Hamann, S.** (2012). Mapping discrete and dimensional emotions onto the brain: controversies and consensus. *Trends in Cognitive Sciences*, 16(9), 458-466. *→ Foundational theoretical debate categorical vs dimensional*

81. **Hochman, Y., Cowen, A.S., & Keltner, D.** (2024). A shared structure for emotion experiences from narratives, videos, and everyday life. *Nature Human Behaviour*. *→ Cross-modal shared emotion structure*

82. **Cowen, A.S., & Keltner, D.** (2021). Semantic space theory: A computational approach to emotion. *Trends in Cognitive Sciences*, 25(2), 124-136. *→ Theoretical framework for 27-emotion space*

83. **Roy, M., Shohamy, D., & Wager, T.D.** (2012). Ventromedial prefrontal-subcortical systems and affective meaning. *Trends in Cognitive Sciences*, 16(3), 147-156. *→ vmPFC affective value, relevant for SQ2 vmPFC dynamics*

84. **Nummenmaa, L., Hari, R., Hietanen, J.K., & Glerean, E.** (2018). Maps of subjective feelings. *Proceedings of the National Academy of Sciences*, 115(37), 9198-9203. *→ Subjective feeling space organization*

85. **Saarimäki, H., Gotsopoulos, A., Jääskeläinen, I.P., Lampinen, J., Vuilleumier, P., Hari, R., Sams, M., & Nummenmaa, L.** (2016/2018). Distributed affective space represents multiple emotion categories across the human brain. *SCAN*, 13(5), 471-482. *→ Already cited (47), dual context*

86. **[Emergence of Emotion Selectivity in Deep Neural Networks Trained to Recognize Visual Objects]** (2024). *PLOS Computational Biology*. *→ Liu et al. — emotion emerges in object DNNs; important for SQ4 endogenous vs driven*

87. **[Biologically Inspired Deep Neural Network Models for Visual Emotion Processing]** (2025). *→ Biological grounding for emotion DNN models*

88. **Sadeghi, S., Smith, F., Damasio, H., & Smith, M.L.** (2023). Direct perception of affective valence from vision. *eLife*, 12, e88414. *→ Visual valence model (VVM), low-level affect precedent*

89. **Phelan, H.L., & Keltner, D.** (2024). Visual looming is a primitive for human emotion. *Current Biology*, 34(17), 3918-3927. *→ Superior colliculus emotion primitive — low-level temporal dynamics*

90. **Bo, K., Cui, L., et al.** (2021). Decoding neural representations of affective scenes in retinotopic visual cortex. *Cerebral Cortex*, 31(6), 3047-3063. *→ Retinotopic affect processing*

91. **Liu, T., Fu, J.Z., et al.** (2022). Layer-specific, retinotopically-diffuse modulation in human visual cortex in response to viewing emotionally expressive faces. *Nature Communications*, 13, 6302. *→ Amygdala-V1 feedback dynamics*

#### Multimodal encoding and brain foundation models

92. **Chen, D., & He, H.** (2024). Brain-JEPA: Brain dynamics foundation model with gradient positioning and spatiotemporal masking. *Advances in Neural Information Processing Systems (NeurIPS 2024)*. https://arxiv.org/abs/2409.19407 *→ Brain foundation model alternative (we do not use, but cite as field context)*

93. **d'Ascoli, S., Deruelle, A., Joubert, C., et al.** (2026). TRIBE v2: A trimodal foundation model for fMRI prediction. *arXiv preprint arXiv:2507.22229*. *→ TRIBE v2 — state-of-the-art brain encoding, Algonauts 2025 winner*

94. **Oota, S.R., Trouvain, N., Alexandre, F., & Hinaut, X.** (2025). Alignment of auditory artificial networks with massive individual fMRI brain data leads to generalisable improvements in brain encoding and downstream tasks. *→ Audio-brain alignment methodology*

95. **Du, C., Fu, K., et al.** (2025). Bridging the behavior-neural gap: A multimodal AI reveals the brain's geometry of emotion more accurately than human self-reports. *→ MLLM predicts brain emotion geometry — critical competitor/supporter*

96. **[Comprehensive Neural Representations of Naturalistic Stimuli through Multimodal Deep Learning]** (2025). *eLife*. *→ Already cited (49), dual context*

97. **[Instruction-Tuned Video-Audio Models Elucidate Functional Specialization in the Brain]** (2025). *→ Task-tuned multimodal alignment*

98. **[MULTI-MODAL BRAIN ENCODING MODELS FOR MULTI-MODAL STIMULI]** (2025). *→ Multimodal brain encoding*

99. **[Stacked Regression using Off-the-shelf, Stimulus-tuned and Fine-tuned Neural Networks for Predicting fMRI Brain Responses to Movies (Algonauts 2025 Report)]** (2025). *→ Algonauts 2025 method*

100. **[SIM: Surface-based fMRI analysis for inter-subject multimodal decoding]** (2025). *→ Surface-based cross-subject multimodal*

101. **Oota, S.R., Moussa, N., et al.** (2026). Brain-tuning improves generalizability and efficiency of brain alignment in speech models. *→ Brain-tuning for model-brain alignment*

102. **Moussa, N., et al.** (2026). Improving semantic understanding in speech language models via brain-tuning. *→ Brain-tuning for semantic understanding*

103. **[Brain-aligning of semantic vectors improves neural decoding of visual stimuli]** (2026). *→ Brain-aligned semantic representations*

#### LLM and language-brain alignment

104. **Toneva, M., & Wehbe, L.** (2019). Interpreting and improving natural-language processing (in machines) with natural language-processing (in the brain). *NeurIPS 2019*. *→ NLP-brain alignment precedent*

105. **Schrimpf, M., Blank, I.A., Tuckute, G., et al.** (2021). The neural architecture of language: Integrative modeling converges on predictive processing. *Proceedings of the National Academy of Sciences*, 118(45), e2105646118. *→ Language brain architecture*

106. **[Unveiling Multi-level and Multi-modal Semantic Representations in the Human Brain using LLMs]** (2024). *→ Multi-level semantic LLM-brain alignment*

107. **[Language-specific representation of emotion-concept knowledge causally supports emotion inference]** (2024). *→ Language-emotion concept causality*

108. **Tang, J., LeBel, A., Jain, S., & Huth, A.G.** (2023). Semantic reconstruction of continuous language from non-invasive brain recordings. *Nature Neuroscience*, 26, 858-866. *→ Language decoder precedent for brain-content mapping*

109. **[Mind captioning: Evolving descriptive text of mental content from human brain activity]** (2024/2025). *Science Advances*. *→ Brain-to-language generation*

#### Reconstruction and decoding (context)

110. **[Reanimating Images using Neural Representations of Dynamic Stimuli]** (2025). *→ Dynamic stimulus reconstruction*

111. **[Scaling laws for decoding images from brain activity]** (2025). *→ Scaling in brain decoding*

112. **[ICLR-2025: Toward generalizing visual brain decoding to unseen subjects]** (2025). *ICLR 2025*. *→ Cross-subject generalization — relevant for H5*

#### Individual variability and cross-subject

113. **[Heritability of movie-evoked brain activity and connectivity]** (2025). *eLife*. *→ Heritability of naturalistic brain response*

114. **[Personalized brain decoding of spontaneous pain in individuals with chronic pain]** (2026). *→ Personalized decoding for individual differences*

#### Compositional and structured representation (dual with Ferrante)

115. **Wang, Y., Kragel, P.A., & Satpute, A.B.** (2026). Map-like representations of emotion knowledge in hippocampal-prefrontal systems. *Nature Communications*, 17, 68240. *→ Map-like hippocampal emotion — contrasts and complements trajectory framework*

116. **[Distributed representations of behaviour-derived object dimensions in the human visual system]** (2024). *→ Distributed object representation — relevant for trajectory component interpretation*

117. **[Hierarchical organization of social action features along the lateral visual pathway]** (2024). *→ Social feature hierarchy*

118. **[Occipital-temporal cortical tuning to semantic and affective features of natural images predicts associated behavioral responses]** (2024). *→ OTC as semantic+affect co-processor*

#### Development and emotion concept formation

119. **[Large-scale encoding of emotion concepts becomes increasingly similar between individuals from childhood to adolescence]** (2023). *Nature Neuroscience*. *→ Developmental convergence — relevant context for individual differences*

#### Dataset descriptors and methodology reviews

120. **Hebart, M.N., et al.** (2023). THINGS-data, a multimodal collection of large-scale datasets. *eLife*, 12, e82580. *→ Dataset context*

121. **Allen, E.J., et al.** (2022). A massive 7T fMRI dataset (NSD). *Nature Neuroscience*, 25, 116-126. *→ Dataset context*

122. **[A 7T fMRI dataset of synthetic images for out-of-distribution modeling of vision]** (2025). *→ OOD dataset context*

123. **[Naturalistic Stimuli in Affective Neuroimaging: A Review]** (2021). *→ Methodological review*

124. **[Probing neurodynamics of experienced emotions—a Hitchhiker's guide to film fMRI]** (2023). *→ Film fMRI methodology guide*

#### Emotion context and theoretical landscape

125. **Lindquist, K.A., & Barrett, L.F.** (2014). Cognitive approaches to emotions. *Current Directions*. *→ Cognitive emotion theory*

126. **Barrett, L.F., & Lindquist, K.A.** (2014). Population coding of affect. *Journal of Cognitive Neuroscience*. *→ Affect population coding*

127. **[Bridging Discrete and Continuous: A Multimodal Strategy for Complex Emotion Detection]** (2024). *→ Discrete-continuous bridging for emotion*

128. **[Deep learning reveals what facial expressions mean to people in different cultures]** (2024). *→ Cross-cultural emotion (context)*

129. **[Affective computing has changed: the foundation model disruption]** (2026). *→ Foundation model landscape in affective computing*

#### Foundation model and goal-driven modeling

130. **Yamins, D.L.K., & DiCarlo, J.J.** (2016/2025). Using goal-driven deep learning models to understand sensory cortex. *Nature Neuroscience*. *→ Goal-driven modeling framework (updated 2025 version)*

131. **[fMRI-LM: Foundation model for fMRI]** (2025). *→ fMRI foundation model alternative*

132. **[Achieving more human brain-like vision via human EEG representational alignment]** (2026). *→ EEG-alignment complement (different modality)*

133. **[Human-like Affective Cognition in Foundation Models]** (2026). *→ LLM affective cognition*

134. **[Decoding Emotion in the Deep: A Systematic Study of How LLMs Represent, Retain, and Express Emotion]** (2025). *→ LLM emotion representation (context)*

#### Systems biology and preprints

135. **[Neuroscience Computational and Systems Biology Reviewed Preprint]** (2025). *→ Systems-level review/preprint*

### v1.3 — Web search additions (filtered by venue rules)

Filter criteria: Q1 journals / top conferences (NeurIPS, ICLR, ICML, CVPR, CCN, MICCAI) including tutorial/workshop tracks / arXiv <1 year (April 2025+). Excluded: MDPI, OpenReview submissions without accept confirmation, arXiv >1 year preprint-only.

#### Naturalistic emotion + EEG-fMRI

136. **[An fMRI-informed EEG model of the amygdala is associated with salience network dynamics during naturalistic emotional stimulation]** (2025). *Molecular Psychiatry*. https://www.nature.com/articles/s41380-025-03418-x *→ Direct precedent for amygdala dynamics during naturalistic emotional stimuli (relevant to H1 per-emotion signatures)*

137. **[Multi-Scale Anti-Correlated Neural States Dominate Naturalistic Whole-Brain Activity]** (2025). *eLife*, reviewed preprint 109116. *→ Multi-scale neural states in naturalistic viewing — state-based dynamics framework*

#### Component Process Model (CPM) — Emo-FilM theoretical basis

138. **Mohammadi, G., Van De Ville, D., & Vuilleumier, P.** (2023). Brain networks subserving functional core processes of emotions identified with componential modeling. *Cerebral Cortex*, 33(12), 7993-8004. https://doi.org/10.1093/cercor/bhad048 *→ CPM fMRI from Emo-FilM's home team (EPFL, Vuilleumier group). Directly grounds Emo-FilM's 50-item CPM annotation scheme. Key precedent.*

#### Dynamical systems — Neural ODE / Koopman (verified venues only)

139. **[Balanced Neural ODEs: Nonlinear Model Order]** (2025). *ICLR 2025*. https://proceedings.iclr.cc/paper_files/paper/2025/file/6fca3ed3c54ffeae947ae668a0841ab2-Paper-Conference.pdf *→ Neural ODE variants at ICLR — methodological comparison*

#### Manifold dynamics — shared state space

140. **[Large-scale neural dynamics in a shared low-dimensional state space reflect cognitive and attentional dynamics]** (2023/2025). *eLife*, 12, e85487. https://elifesciences.org/articles/85487 *→ Shared low-D state space in cognition — supports H1 latent space framework*

#### Hyperalignment — cross-subject alignment (H5)

141. **Haxby, J.V., Guntupalli, J.S., Nastase, S.A., & Feilong, M.** (2020). Hyperalignment: Modeling shared information encoded in idiosyncratic cortical topographies. *eLife*, 9, e56601. https://doi.org/10.7554/eLife.56601 *→ Core hyperalignment framework — for H5 cross-subject trajectory consistency*

142. **[Boosting Hyperalignment Performance with Age-specific Templates]** (2025). *eLife*, reviewed preprint. https://doi.org/10.7554/eLife.110566 *→ Age-specific alignment templates*

143. **[Functional Inter-Subject Alignment Outperforms Anatomical Alignment]** (2025). *CCN 2025*. *→ Functional vs anatomical alignment benchmark*

#### Emotion abstract representation

144. **Skerry, A.E., & Saxe, R.** (2015). Neural representations of emotion are organized around abstract event features. *Current Biology*, 25(15), 1945-1954. *→ Abstract event feature organization in emotion*

#### TRIBE v2 detailed reference (state-of-the-art benchmark)

145. **d'Ascoli, S., Banville, H., Cathelain, T., et al.** (2026). TRIBE: TRImodal Brain Encoder for whole-brain fMRI response prediction. *arXiv preprint arXiv:2507.22229* (July 2025, within 1-year window). Repo: https://github.com/facebookresearch/tribev2 *→ State-of-the-art brain encoding (V-JEPA2 + LLaMA 3.2 + Wav2Vec-BERT trained on 1115h fMRI, 700+ subjects). Algonauts 2025 winner. Primary benchmark/comparison.*

#### Sparse autoencoder for neuroscience

146. **[NLDisco: A Pipeline for Interpretable Neural Latent Discovery]** (2025). *Data on the Brain & Mind Tutorial Track, NeurIPS 2025*. https://data-brain-mind.github.io/tutorials/nldisco-a-pipeline-for-interpretable-neural-latent-discovery/ *→ Direct SAE pipeline for neural data*

147. **[TRACE: Task-Relevant Autoencoder via Classifier Enhancement]** (2025). *Scientific Reports*, 15, 83867. *→ Classifier-enhanced autoencoder for brain decoding*

#### Core affect (historical precedent)

148. **Kim, H., Adolphs, R., O'Doherty, J.P., & Shimojo, S.** (2017). Identifying core affect in individuals from fMRI responses to dynamic naturalistic audiovisual stimuli. *PLOS ONE*, 12, e0161589. https://doi.org/10.1371/journal.pone.0161589 *→ Older naturalistic affect fMRI precedent (PLOS ONE — included for historical context of the specific experimental paradigm)*

### Removed from v1.3 (failed venue criteria)

- ~~CineBrain arXiv 2503.06940~~ — March 2025 preprint-only, borderline timing
- ~~Whole-Brain Sustained Emotional Experience bioRxiv (2022)~~ — preprint-only, >1yr
- ~~Network analyses CPM Current Psychology 2024~~ — Springer mid-tier, not Q1
- ~~Koopman-NODE arXiv 2411.12940 (Nov 2024)~~ — >1yr preprint-only
- ~~KoNODE OpenReview~~ — submission only, not confirmed accepted
- ~~Koopman Universal OpenReview~~ — submission only, not confirmed accepted
- ~~**FIRE MDPI Mathematics 2026**~~ — **MDPI (explicit exclusion rule)**

### v1.4 — ICLR 2026 additions

Filter criteria: ICLR 2026 accepted papers, posters, or recent submissions.

#### Brain dynamics framework (CRITICAL)

149. **[Brain Dynamics with Optimal Control (BDO)]** (2026). *ICLR 2026*. https://openreview.net/pdf?id=N51nP3TBwR *→ **Directly relevant to our thesis.** Addresses BrainLM/Brain-JEPA limitation of treating fMRI time-series as image-like fixed grids. Proposes explicit brain dynamics framework with optimal control, handling heterogeneous TR datasets. Contrasts and complements our BCNE/Neural ODE approach — key theoretical and methodological grounding.*

150. **[Disentangling Shared and Private Neural Dynamics]** (2026). *ICLR 2026 (submission)*. https://arxiv.org/pdf/2510.25023 *→ **Critical for H5 cross-subject alignment.** Models regional communication through shared latent trajectories within common subspace with private dynamics orthogonal. Provides technical framework for separating shared from individual-specific trajectory components in our 30-subject Emo-FilM analysis.*

#### Latent flow matching for dynamics

151. **[Learning Patient-Specific Disease Dynamics With Latent Flow Matching For Longitudinal Imaging Generation]** (2026). *ICLR 2026 Poster*. https://iclr.cc/virtual/2026/poster/10008459 *→ Flow matching approach for temporal evolution in brain imaging. Alternative to Neural ODE for our trajectory modeling. Disease context but methodology is general.*

#### fMRI Foundation Models

152. **[SLIM-Brain: A Data- and Training-Efficient Foundation Model for fMRI Data Analysis]** (2026). *ICLR 2026*. https://openreview.net/forum?id=fFgzAQAUqs *→ Atlas-free fMRI foundation model. Alternative to Brain-JEPA for pretrained brain representation. Data-efficient (3% of standard FM pretraining data) — relevant for 30-subject Emo-FilM.*

153. **[PRISM: Decoding Visual Stimuli with fMRI]** (2026). *ICLR 2026 Poster*. https://iclr.cc/virtual/2026/poster/10011227 *→ fMRI decoding via structured text space + object-centric diffusion. Context for fMRI decoding framework.*

#### Multimodal brain encoding

154. **[Brain encoding models based on binding multiple modalities across audio, language, and vision]** (2026). *ICLR 2026*. https://openreview.net/forum?id=3NMYMLL92j *→ Multimodal brain encoding with audio, language, vision — highly relevant for Emo-FilM multimodal stimuli (video + audio + narrative).*

#### Dynamical systems methodology

155. **[Balanced Neural ODEs: Nonlinear Model Order]** (2025). *ICLR 2025*. https://proceedings.iclr.cc/paper_files/paper/2025/file/6fca3ed3c54ffeae947ae668a0841ab2-Paper-Conference.pdf *→ Neural ODE variants (already in v1.3 — preserved here for ICLR continuity)*

---

*v1.4 — 2026-04-19 (ICLR 2026 papers added — 6 new high-impact entries including BDO and Disentangling Shared/Private)*
