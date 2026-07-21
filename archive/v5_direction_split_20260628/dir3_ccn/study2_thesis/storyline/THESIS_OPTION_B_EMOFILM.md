# Thesis Option B — Emo-FilM Main

**Focus:** 감정 관련 뇌 활동의 latent dynamics — temporal process characterization
**Dataset:** Emo-FilM (main) + Horikawa (optional for state space validation)
**Core methodology:** Latent dynamical systems analysis with modern DL methods
**Date:** 2026-04-19 (v1)

---

## 1. Research Question

### Main RQ
> **"영화 시청 중 감정 관련 뇌 활동은 정적 패턴이 아니라 latent dynamical system으로 이해되는가? 서로 다른 감정은 이 dynamical space에서 어떤 특징적 signature (time scale, trajectory shape, stability)로 구별되는가?"**

### Sub-questions

**SQ1 (Latent space structure)**
감정 관련 뇌 활동의 latent space는 어떤 기하학 (manifold 차원, 형태, 영역 분포)을 가지는가?

**SQ2 (Dynamical signatures)**
이 latent space 위 trajectory의 dynamical 특성 (attractor, flow field, time constant, stability)은 무엇인가? 감정 유형마다 signature가 어떻게 다른가?

**SQ3 (Stimulus-driven trajectory)**
시각 입력 (V-JEPA2 features)이 brain trajectory의 방향/속도를 어떻게 driving하는가?

**SQ4 (Emotion transitions)**
감정 간 전환 (disgust → neutral, fear → relief)은 smooth drift인가 discrete bifurcation인가? 전환 구조에 systematic 패턴이 있는가?

---

## 2. Theoretical Gap

### 현재 field의 기본 가정

감정 뇌과학은 감정을 **snapshot** (상태, 범주, 차원의 좌표, 패턴)으로 다뤄옴:
- 범주적 (Horikawa, Kragel): "이 패턴 = fear"
- 차원적 (Russell, Raut): "이 점 = (valence, arousal)"
- 구성주의 (Barrett): "core affect + concept 조합"
- 지각-우선 (Conwell): "시각 특성의 직접 결과"

모든 접근이 **정적 표상**을 감정의 기본 단위로 취급.

### 이 가정이 놓치는 것

1. **감정은 phenomenologically 시간적 현상**
   - 공포는 쌓이고, 놀람은 전환하며, 기쁨은 발현
   - Snapshot은 이 본질을 지움

2. **서로 다른 감정은 dynamical 성격이 근본적으로 다를 수 있음**
   - Disgust = 즉각 attractor 수렴 (fast)
   - Joy = 점진적 buildup (slow)
   - 정적 패턴 비교로는 이 차이 포착 불가

3. **감각-감정 변환은 정의상 temporal process**
   - Endpoint snapshot으로는 변환 과정 놓침
   - 실시간 시청 중 궤적만이 과정을 드러냄

4. **동일 감정 내부의 강도 스펙트럼**
   - Anger: 짜증 → 격노 연속 변이
   - 정적 "anger 패턴" 하나로 뭉개지만 trajectory는 궤적 길이/속도로 자연스럽게 표현

### Methodological gap (이 theoretical gap 풀 수 있는 도구)

Modern deep learning latent dynamics methods (CEBRA, BCNE, T-PHATE, Neural ODE, SLDS)가 motor/sensory neuroscience에서는 활용되지만 **감정 fMRI에 체계적 적용 거의 없음**:
- Dynamic fMRI networks of emotion (eLife 2025): classical HMM + Gaussian fitting
- eNeuro 2025 music HMM: classical HMM
- Arousal embedding (Nature 2025): scalar-based, not deep latent
- Pessoa threat trajectories: classical linear dimensionality reduction

**DL latent dynamics × emotion fMRI = 공백**

### Gap 한 줄

> 감정 뇌과학이 snapshot 가정에 갇혀 감정의 **시간적 구성 + 유형별 dynamical 차이 + 변환 과정**을 직접 포착하지 못하며, 이를 풀 수 있는 modern DL latent dynamics methodology가 감정 domain에 적용된 선례가 없다.

---

## 3. Hypotheses

### H1 — Distinct dynamical signatures per emotion
> 서로 다른 감정은 정적 패턴뿐만 아니라 **dynamical 성격** (time scale, trajectory shape, stability)에서 구별된다.
>
> 구체 예측:
> - Disgust trajectory: 짧은 time constant + 빠른 수렴 (strong attractor)
> - Joy trajectory: 긴 time constant + 느린 drift (weak attractor)
> - Anger spectrum (짜증 → 격노): trajectory 길이의 연속 변이

**Falsifiable:** 모든 감정 유형이 동일 time constant / flow 구조를 보이면 기각.

### H2 — Fast-onset vs slow-building emotion dichotomy
> 감정 유형은 **stability 구조**에 따라 구분된다.
>
> 구체 예측:
> - Fast-onset attractor 감정: disgust, surprise, fear, startle (sensory-reactive)
> - Slow-building drift 감정: joy, nostalgia, awe, aesthetic (constructed)

**Falsifiable:** 이 dichotomy가 bimodal 아닌 연속적이면 수정, 완전 랜덤이면 기각.

### H3 — Stimulus-driven trajectory perturbation (SQ3)
> 시각 자극의 변화가 brain trajectory 방향/속도를 **체계적으로 driving**한다.
>
> 구체 예측:
> - V-JEPA2 feature의 Δt → brain trajectory의 Δt 예측 가능
> - Layer-wise: low-level feature 변화는 early visual trajectory driving, deep feature는 transmodal trajectory driving
> - Stimulus 제거 시 endogenous dynamics가 drift하지만 stimulus re-introduction 시 복귀

**Falsifiable:** Stimulus feature가 trajectory를 예측 못 하거나, trajectory가 순수 endogenous dominant면 기각.

### H4 — Emotion transitions as bifurcations
> 감정 전환은 smooth continuous drift가 아니라 특정 bifurcation point에서 **discrete-like jump**를 포함한다.
>
> 구체 예측:
> - 영화의 강한 감정 전환 장면 (surprise, 반전 등)에서 trajectory discontinuity
> - 자연스러운 감정 변화 (joy → relief)에서 smooth drift
> - Bifurcation 지점이 narrative context와 상관

**Falsifiable:** 모든 전환이 smooth면 기각. Discrete jump가 없으면 drift 모델이 충분.

### H5 — Cross-subject trajectory consistency
> 같은 영화 시청 중 subjects 간 brain trajectory가 high-dimensional space에서 일정 수준 align된다 (공유 dynamics).
>
> 구체 예측:
> - 감정 관련 영역에서는 inter-subject alignment 높음
> - Default mode / endogenous 영역에서는 alignment 낮음
> - Alignment가 narrative의 강한 감정 지점에서 peak

**Falsifiable:** Alignment 전혀 없으면 dynamics 주장 self-refuting.

### H6 (optional) — Cross-dataset shared state space
> Horikawa에서 발견된 emotion-evoked brain state들과 Emo-FilM에서 trajectory가 통과하는 영역이 **공유 latent space**에서 대응한다.
>
> 구체 예측: Horikawa "fear 영역" ↔ Emo-FilM 공포 장면의 trajectory 통과 영역

**Role:** Cross-dataset validation. 성공 = generalizable findings. 실패 = context-specific (여전히 의미 있음).

---

## 4. Methodology

### 4.1 Data

**Emo-FilM (primary):**
- 30 subjects × 14 films × 2.5 hours total
- Moment-by-moment emotion rating (50 CPM items — Component Process Model)
- 본인 rating (self-annotation, crowd-sourced 아님)
- Physiological data (ECG, GSR, respiration) — optional for arousal control
- 연속 TR 시계열 (TR = 2s 가정)

**Horikawa (optional secondary for H6):**
- 5 subjects × 2185 videos × 450 parcels
- 34 cat + 14 dim labels
- Role: state space validation, stimulus diversity sampling

### 4.2 Stimulus processing

**V-JEPA2 (Meta 2025):**
- Frame-wise feature extraction (temporal resolution matched to TR)
- Each TR (2s) → averaged V-JEPA2 features for that window
- Layer-wise: 32 layers available

**Audio (optional):**
- Whisper embedding or wav2vec2 for soundtrack
- TRIBE 2026 보여줌: multimodal (audio + video) alignment 개선

### 4.3 Brain processing

**Parcellation:**
- Schaefer 400 cortical + 50 subcortical = 450 parcels
- Same as Horikawa for cross-dataset compatibility

**Latent space extraction (Level 2 task-specific DL):**

**Primary method — BCNE (Nature Comp Sci 2025):**
- Convolutional network-based embedding
- Unsupervised, captures brain trajectories
- Output: low-dimensional manifold (e.g., 10-30 dim) + trajectory per subject

**Alternative/Complementary — T-PHATE (Nature Comp Sci 2023):**
- Temporal potential of heat-diffusion
- Naturalistic fMRI validated
- Denoised trajectory visualization

**Alternative — CEBRA (Nature 2023, self-supervised mode):**
- Contrastive latent embedding
- No auxiliary variables (purely self-supervised)

**BFM (Brain-JEPA, fMRI-LM) 사용 안 함** — pretraining mismatch 우려.

### 4.4 Main analyses

#### Analysis 1 — Manifold geometry (SQ1)

```
Apply BCNE / T-PHATE to fMRI time series per subject
→ Low-dim latent trajectory (subject × time × K-dim)

Analyses:
  1. Manifold dimensionality (K)
  2. Manifold curvature / topology
  3. Density distribution (where on manifold)
  4. Inter-subject manifold comparison
```

**Output:** Geometry of emotion-related latent space.

#### Analysis 2 — Per-emotion dynamical signatures (SQ2, H1, H2)

**Time constant extraction:**

```
For each emotion-labeled segment in Emo-FilM:
  1. Extract trajectory segment (TRs labeled as emotion X)
  2. Fit autocorrelation function
  3. Extract time constant τ (decay rate)
  4. Extract stability (variance around mean)
  5. Extract trajectory length / speed
```

**Dynamical system fitting:**

```
Option A: Neural ODE (Chen 2018, torchdiffeq)
  dx/dt = f_θ(x, t)
  Learn vector field per emotion
  Extract: fixed points, flow field, Lyapunov exponent

Option B: gpSLDS (NeurIPS 2024)
  Switching linear dynamical system with GP
  Within each state: linear dynamics (interpretable)
  Between states: GP-smooth transitions

Option C: SING (NeurIPS 2025)
  Stochastic differential equation inference
  Natural gradient VI
  Uncertainty quantification (good for n=30)

Option D: Neural Koopman (BRICK, IEEE TMI 2025)
  Linear operators in lifted space
  Task-related dynamics emphasis
```

**Per-emotion output:** τ, trajectory shape, attractor depth, stability.

**Testing H1:** Compare τ/shape across emotions statistically.
**Testing H2:** k-means or bimodal test on emotion-level dynamical signatures.

#### Analysis 3 — Stimulus-driven trajectory (SQ3, H3)

```
V-JEPA2 feature time series ↔ Brain trajectory time series

Cross-correlation / Granger causality:
  Does V-JEPA2_feature(t-k) predict Brain_trajectory(t)?
  
Encoding model:
  f: V-JEPA2 features → brain trajectory change (dΔx/dt)
  Per-layer encoding: which layer drives which trajectory aspect
  
Perturbation / ablation:
  Trajectory prediction with vs without stimulus input
  Endogenous vs stimulus-driven variance decomposition
```

**Output:** Stimulus-driven dynamics quantification + layer-wise decomposition.

#### Analysis 4 — Emotion transition structure (SQ4, H4)

```
Identify transition moments in Emo-FilM (emotion rating change points)

At each transition:
  1. Pre-transition trajectory segment
  2. Post-transition trajectory segment
  3. Transition speed (Δx/Δt)
  4. Discontinuity metric (sudden direction change?)

Bifurcation analysis:
  Neural ODE / Koopman at transition points
  Fixed point structure change
  Phase space portrait before/after

Classification:
  Smooth drift vs discrete jump
  Correlation with narrative event strength
```

**Output:** Transition typology + bifurcation map.

#### Analysis 5 — Cross-subject alignment (H5)

```
30 subjects × same film trajectories

Method: Shared Response Model (SRM) or Hyperalignment
  Or: Procrustes / dynamic time warping

Per-ROI alignment score across subjects
  Where does dynamics converge (shared)?
  Where diverge (individual)?
  
Narrative-aligned: 
  Alignment peak at emotionally intense scenes?
```

**Output:** Inter-subject dynamics consistency map.

#### Analysis 6 (optional) — Cross-dataset validation (H6)

```
Apply same V-JEPA2 features + same latent space method to both:
  Horikawa: 2185 discrete snapshots → state space points
  Emo-FilM: continuous trajectory

Test: 
  Does Emo-FilM trajectory pass through Horikawa-discovered state regions?
  GW-OT between Horikawa state distribution and Emo-FilM trajectory density
```

**Output:** Cross-dataset shared state space (generalization claim).

### 4.5 Integration

```
Analysis 1 → Latent geometry
Analysis 2 → Dynamical signatures per emotion
Analysis 3 → Stimulus coupling
Analysis 4 → Transitions
Analysis 5 → Inter-subject consistency
Analysis 6 → Cross-dataset robustness

Cross-analysis:
  Do fast-attractor emotions (H2) correspond to stimulus-heavy driven (H3)?
  Do transitions (H4) occur at low cross-subject alignment moments (H5)?
  Emotion signature (H1) preserved across datasets (H6)?
```

**Narrative:** 감정은 snapshot이 아니라 **dynamical process**이며, 감정 유형마다 distinct dynamical signature를 가지고, stimulus가 이 dynamics를 systematic하게 driving한다.

---

## 5. Novelty Positioning

### Against direct precedents

| Paper | 그들이 한 것 | 우리가 다르게 |
|-------|-----------|-------------|
| **Dynamic fMRI networks of emotion (eLife 2025)** | Classical ICA + Gaussian fitting, Forrest Gump | DL latent dynamics (BCNE/Neural ODE), Emo-FilM, systematic per-emotion signatures |
| **Arousal embedding (Raut Nature 2025)** | Arousal as universal scalar manifold, mouse + human | Emotion-specific dynamics, distinguishes arousal from emotion-type dynamics |
| **Pessoa threat trajectories (eLife 2024)** | Threat specific, classical dim reduction | Full emotion spectrum, DL latent methods |
| **BCNE (Nat Comp Sci 2025)** | General brain dynamics (not emotion-specific) | Emotion domain application + per-emotion characterization |
| **T-PHATE (Nat Comp Sci 2023)** | General naturalistic fMRI | Emotion-specific + combined with dynamical system ID |
| **Awe CEBRA (Lee 2025 Comms Psych)** | Single emotion (awe), EEG | Full emotion spectrum, fMRI, dynamical signatures |
| **Sartzetaki 2025** | Static RSA, action recognition | Dynamic trajectory analysis, emotion |

### Unique contribution

**"Modern DL latent dynamics methods를 emotion fMRI에 systematic 적용하여, 감정 유형별 dynamical signature를 정량화하고, stimulus-driven trajectory perturbation을 characterize한 최초의 연구."**

- DL 방법론 novelty: field에 아직 적용 없음
- Per-emotion signature: Pessoa 단일 감정 → 전체 spectrum
- Stimulus coupling: 기존 dynamic 연구에 없음

---

## 6. Risks

### 방법론적 risks

- **BCNE/Neural ODE fMRI 적용 검증 부족** (motor/sensory 위주, 감정 적용 선례 적음)
- **n=30이지만 14 films 제약** — stimulus variation 제한
- **TR=2s의 시간 해상도 한계** — fast dynamics (ms-s scale) 못 잡음
- **Emo-FilM 전처리 부담** (1-3주)

### 이론적 risks

- **Arousal embedding (Raut 2025)에 흡수 가능성** — dynamics가 arousal projection에 불과하다는 반박
  - 대응: Arousal regression out 후 residual dynamics 분석
- **H1 기각 시 fallback 필요** — 감정 유형별 signature 차이가 없으면 thesis 약화
  - Fallback: "emotion이 homogeneous dynamical class" 라는 negative 결론도 의미 있음
- **H4 (bifurcation) 가 너무 strong claim** — discrete jump 발견 안 되면 smooth model로 후퇴

### Data / pipeline risks

- Emo-FilM 50 items vs Horikawa 34+14 labels → cross-dataset comparison 어려움
- 30 subjects naturalistic fMRI → inter-subject variability 큼
- CPM annotation의 theoretical baseline (Barrett/Scherer framework)이 우리 claim과 상충 가능

---

## 7. Feasibility (2-month plan)

```
Week 1:
  - Emo-FilM 데이터 다운로드 + 전처리 시작
  - V-JEPA2 feature 추출 on Emo-FilM frames
  - Schaefer 450 parcellation on Emo-FilM fMRI
  - BCNE / T-PHATE 환경 구축

Week 2:
  - Emo-FilM 전처리 완료
  - Analysis 1 (manifold geometry) 수행
  - Latent space 추출 per subject

Week 3:
  - Analysis 2 (per-emotion dynamics)
  - Neural ODE / gpSLDS 구현 + training
  - Time constant 추출

Week 4:
  - Analysis 2 완성 (signatures per emotion)
  - H1, H2 test
  - Emotion typology 초안

Week 5:
  - Analysis 3 (stimulus-driven trajectory)
  - V-JEPA2 layer-wise encoding
  - H3 test

Week 6:
  - Analysis 4 (transitions, bifurcations)
  - Analysis 5 (cross-subject alignment)

Week 7:
  - Analysis 6 (Horikawa cross-validation, if time)
  - Integration + cross-analysis
  - Figures

Week 8:
  - Writing
  - Revision
```

**Feasibility assessment:** 중간. Emo-FilM 전처리 risk가 가장 큼. DL latent dynamics 구현 복잡도 medium. 핵심 analysis (1-3)는 2개월에 가능하지만 full scope (all 6)는 빠듯.

**Minimum viable outcome:** Analysis 1 + 2 + 3 완성 = "감정별 dynamical signature + stimulus coupling" — 이것만으로도 thesis 성립.

---

## 8. Expected Outcome

### Primary contribution

1. **First systematic DL latent dynamics analysis of emotion fMRI**
2. **Per-emotion dynamical signature quantification** (Pessoa 단일 감정 → spectrum 확장)
3. **Stimulus-driven trajectory mechanism** (기존 dynamic 연구에 없는 측면)
4. **Theoretical reframing**: 감정 = dynamical process (snapshot 가정 challenge)

### If all hypotheses supported

"감정은 snapshot이 아니라 dynamical system의 trajectory이며, 감정 유형마다 distinct signature를 가지고, stimulus input이 이 dynamics를 systematic하게 driving함" — 감정 뇌과학의 새로운 framework.

### Fallback narratives

- H1/H2 기각 → "감정은 homogeneous dynamical class" (negative 결과, 의미 있음)
- H3 기각 → "Trajectory는 주로 endogenous, stimulus 영향 제한적" (반대로 흥미로움)
- H4 기각 → "감정 전환은 smooth, bifurcation 아님" (simpler model)
- H5 기각 → "Dynamics가 highly individual" (개인차 중심 future work)
- H6 기각 → "Context dependency 강함" (Horikawa ≠ Emo-FilM)

모든 시나리오에 defensible narrative.

---

## 9. Key References

**Direct precedents (positioning):**
- Raut et al. Nature 2025 — Arousal universal embedding (major threat, must address)
- Dynamic fMRI networks of emotion, eLife 2025 — Direct precedent, classical methods
- Pessoa 2024 eLife — Threat trajectories, classical
- Sartzetaki 2025 ICLR — V-JEPA2 factor-region on BMD (actions)

**Methodological foundations:**
- BCNE: Zhou et al. Nature Comp Sci 2025 — Brain-dynamic CNN embedding
- T-PHATE: Busch et al. Nature Comp Sci 2023 — Temporal manifold for fMRI
- CEBRA: Schneider et al. Nature 2023 — Contrastive neural embedding
- Neural ODE: Chen et al. NeurIPS 2018 — Continuous dynamics learning
- gpSLDS: NeurIPS 2024 — GP switching linear dynamical systems
- SING: NeurIPS 2025 — Stochastic DE inference
- Neural Koopman BRICK: IEEE TMI 2025 — Linear dynamics in lifted space

**Theoretical background:**
- Barrett & Lindquist 2012 — Constructed emotion theory
- Hasson 2008 — Temporal receptive fields (TRF hierarchy)
- Mathis et al. Nat Rev Neurosci 2025 — Joint brain-behavior modeling review

**Complementary (cite for context):**
- V-JEPA2 paper (Meta 2025)
- Horikawa 2020 iScience (cross-validation)
- Awe CEBRA (Lee 2025) — label-free precedent
- Brain Algebra (Ferrante 2025) — compositionality
- Map-like emotion knowledge (Wang/Kragel 2025) — hierarchical emotion maps

---

*v1 — 2026-04-19*
