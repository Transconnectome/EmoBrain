# 결과 해석 + 실험 설계 종합 문서

**Last updated:** 2026-04-10

---

## 1. Exp26: 기본 해석 분석 결과

### 1.1 Rating 분포와 R²의 관계 — Artifact 확인

**뭘 했나:** 34개 감정의 디코딩 R²가 rating의 통계적 특성(분산, 평균 등) 때문인지 확인.

**결과:**
```
R² vs Rating Std:  r=0.480, p=0.004  ⚠️ 상관 있음
R² vs Rating Mean: r=0.384, p=0.025  ⚠️ 상관 있음
```

R²의 약 23%가 rating 분산으로 설명됨. **부분적 confound이지만 전부 artifact는 아님** (77%는 분산과 무관).

Aesthetic appreciation: Std=0.154인데 Amusement(0.233)이나 Empathic pain(0.198)보다 낮음. 그런데 R²는 가장 높음(0.323). → 분산만으로 설명 안 되는 진짜 신호가 있음.

### 1.2 AV Regress Out — 범주 디코딩이 VA의 위장인가?

**뭘 했나:** 34개 감정 rating에서 Arousal/Valence로 설명되는 부분을 제거(linear regression으로 잔차 추출). 잔차로 brain-pred subspace 디코딩.

**왜 필요한가:** "범주 감정 디코딩이 잘 된다"고 했는데, 사실은 VA를 예측한 것이고 VA 조합으로 범주가 따라온 것일 수 있음. 이걸 배제해야 "진짜 범주적"이라고 주장 가능.

**결과:**
```
AV 제거 전: Mean R² = 0.055
AV 제거 후: Mean R² = 0.054
유지율: 97.6%
```

개별 감정:
- Aesthetic appreciation: 101% 유지 (VA와 무관)
- Amusement: 130% (VA 제거하니 오히려 개선 — VA가 노이즈였음)
- Romance: 148% (같은 현상)
- Anxiety: 41% (이건 VA 성분이 컸음 — 각성도와 겹침)

**결론:** brain-pred subspace의 범주 감정 정보는 VA와 독립적. VA의 위장이 아님.

**이론적 의미:** Cowen & Keltner (2017) 지지 — 감정 범주는 VA로 환원 불가능한 독립적 구조.

### 1.3 Raw fMRI vs Brain-JEPA

**뭘 했나:** 동일 분석을 Brain-JEPA(768차원) 대신 Raw fMRI(450 parcel)로 실행하여 Brain-JEPA가 신호를 왜곡하는지 확인.

**왜 필요한가:** Brain-JEPA는 resting-state fMRI에서 학습됨. 우리 데이터는 task fMRI(감정 비디오 시청). Brain-JEPA가 task-specific 신호를 제대로 인코딩하는지 확인 필수.

**결과:**

Forward (뇌 → V-JEPA2 PC 예측):
```
                Raw fMRI    Brain-JEPA
  PC1:          0.354       0.373      (비슷)
  PC2:          0.227       0.075      (Raw가 3배)
  PC3:          0.307       0.088      (Raw가 3.5배)
  PC4:          0.147       0.000      (Raw는 예측 가능, BJ는 불가)
  PC5:          0.083       0.000      (동일)
  PC6:          0.036       0.000      (동일)

Brain-pred PCs: Raw fMRI → 6개, Brain-JEPA → 3개
```

뇌에서 직접 감정 디코딩:
```
                Cat R²    AV R²    Cat/VA
Raw fMRI:       0.026     0.073    0.35
Brain-JEPA:     0.010     0.033    0.32
```

**결론:** 
- Brain-JEPA가 task fMRI의 감정 신호를 **절반 이상 잃음** (6개→3개)
- "3개만 유의"는 뇌의 한계가 아니라 **Brain-JEPA의 한계**
- Raw fMRI를 메인으로 써야 완전한 그림이 나옴

### 1.4 감정 Rating PCA 차원 수 vs CCA CC 수

**뭘 했나:** 34개 감정 rating 자체가 실제로 몇 차원인지 PCA로 확인. CCA에서 나온 substantial CC 수와 비교.

**결과:**
```
감정 rating PCA:
  80% 분산 = 12차원
  90% 분산 = 18차원
  95% 분산 = 23차원
  99% 분산 = 29차원

CCA substantial CCs (r > 0.3): 27개
Cowen & Keltner (2017): ~27개 범주
```

**해석:** 감정 rating 자체가 23~29차원 구조. CCA 공유 축 27개와 수치적으로 일치. 뇌-비디오 공유 구조의 차원 수 ≈ 감정 범주 차원 수. 다만 이건 suggestive이지 증명은 아님 — CC들이 실제로 27개 범주에 1:1 대응되는지 추가 검증 필요.

---

## 2. Exp27: Deep Analysis 결과

### 2.1 6 Basic Emotion이 왜 안 나오는가

**뭘 했나:** Ekman의 6 basic emotion(Anger, Disgust, Fear, Joy, Sadness, Surprise)이 디코딩 하위권인 이유를 분석. Rating 분포, 비디오 수, 감정 간 중복도, V-JEPA2 시각적 분리도 확인.

**결과:**
```
6 Basic:  mean R²=0.013, Strong%(rating>0.3인 비디오 비율)=1.6%
Other 28: mean R²=0.064, Strong%=5.6%

개별 수치:
  Joy:      Strong% = 0.0% (2196개 중 rating>0.3인 비디오가 0개)
  Fear:     Strong% = 0.0%
  Disgust:  Strong% = 0.2% (약 4개)
  Anger:    Strong% = 1.3%
  Sadness:  Strong% = 4.1%
  Surprise: Strong% = 4.1%

vs
  Amusement: Strong% = 29.6%
  Aesthetic appreciation: Strong% = 10.0%
```

**R²와 각 요인의 상관:**
```
R² vs Std:        r=0.480, p=0.004
R² vs Strong%:    r=0.398, p=0.020
R² vs MaxCorr:    r=0.273, p=0.119 (비유의)
```

**해석:**

6 basic emotion이 안 나오는 핵심 원인: **Horikawa 데이터에서 이 감정들을 강하게 느끼는 비디오가 거의 없음.**

Horikawa는 Cowen & Keltner의 34범주 체계를 사용. 이 체계에서 "Joy"보다 "Amusement", "Excitement" 같은 세분화 감정이 더 많이 태깅됨. "Joy"라는 라벨이 너무 넓어서 Horikawa 비디오에서 거의 안 눌린 것.

→ 6 basic emotion 실패는 **모델 문제가 아니라 rating 데이터의 특성.** 이 자극 세트에서는 Cowen의 세분화 범주가 더 적합.

### 2.2 Rank-Normalized R²

**뭘 했나:** 34개 감정 rating을 rank 변환(균일 분포)하여 분포 차이 효과 제거 후 재디코딩.

**왜 필요한가:** Exp26에서 R²-Std 상관(r=0.48)이 있었으므로, 분포를 동일하게 만든 후에도 순서가 유지되는지 확인.

**결과:**
```
Original vs Ranked R² 상관: r=0.971
```

순서가 거의 안 바뀜. Aesthetic appreciation이 여전히 1위. **R² 순서는 rating 분포 artifact가 아님 확인.**

### 2.3 Raw fMRI Forward/Reverse 전체 결과

**Forward: Raw fMRI → V-JEPA2 PC**
```
PC1: R²=0.354, PC2: R²=0.227, PC3: R²=0.307, PC4: R²=0.147, PC5: R²=0.083, PC6: R²=0.036
→ 6개 유의 (Brain-JEPA에서는 3개)
```

**Reverse: V-JEPA2 → Raw fMRI PC**
```
모든 PC: R²=0.000
→ Raw fMRI에서도 여전히 0개 유의
```

**핵심:** Forward-Reverse 비대칭은 Brain-JEPA artifact가 아님. Raw fMRI에서도 동일한 비대칭 → **진짜 뇌-비디오 구조적 비대칭.**

**Raw fMRI brain-pred 감정 디코딩:**
```
Raw fMRI brain-pred (6 PCs): Cat R²=0.076, AV R²=0.045, Cat/VA=1.68
Brain-JEPA brain-pred (3 PCs): Cat R²=0.055, AV R²=0.038, Cat/VA=1.44
```

Raw fMRI가 Cat/VA ratio도 더 높음. 원본 뇌 신호가 더 범주적.

### 2.4 Variance Partitioning

**뭘 했나:** 각 감정에 대해 V-JEPA2(stimulus)와 Brain-JEPA(brain) 각각/합쳐서 설명하는 분산을 분해.

```
Stimulus unique  = R²(stim) - shared
Brain unique     = R²(brain) - shared
Shared           = R²(stim) + R²(brain) - R²(both)
```

**결과:**
```
Mean across 34 emotions:
  Stimulus unique:  0.014
  Brain unique:     0.003
  Shared:           0.041
  Total (combined): 0.025
```

대부분의 감정 정보는 stimulus와 brain이 **공유.** Brain unique = 0.003으로 작음.

예외: Uncomfortable (brain unique = 0.102) — 이 감정만 뇌 고유 기여가 큼.

**주의:** 이건 Brain-JEPA 기반. Raw fMRI로 하면 brain unique가 더 클 수 있음 (Brain-JEPA가 신호를 잃으니까).

### 2.5 Brain Residual

**뭘 했나:** Brain-JEPA에서 V-JEPA2로 설명되는 부분을 빼고(linear regression 잔차), 잔차로 감정 디코딩.

**의도:** "V-JEPA2에 없는, 뇌만의 고유 감정 정보가 있는가?"

**결과:**
```
Brain residual → emotion decoding:
  Cat R² = 0.000
  AV R² = 0.004
```

Brain-JEPA의 감정 정보가 대부분 V-JEPA2와 공유 → 잔차에 감정이 거의 없음.

**⚠️ 해석 주의:** Brain-JEPA가 resting-state 모델이라 task-specific 고유 정보를 이미 잃어버린 상태. Raw fMRI로 동일 분석하면 결과가 다를 수 있음.

### 2.6 Emotion Clustering

**뭘 했나:** brain-pred subspace (PC1-3)에서 34개 감정이 어떻게 군집되는지 계층적 군집 분석.

```
3-cluster solution:
  Cluster 1 (R²=0.102): Aesthetic appreciation, Excitement, Uncomfortable, 
    Calmness, Boredom, Craving, Fear, Sadness, Surprise
    → brain-pred space에서 잘 디코딩되는 감정들

  Cluster 2 (R²=0.042): Anxiety, Horror, Interest, Annoyance,
    Confusion, Nostalgia, Relief, Sexual desire, Triumph
    → 중간 그룹

  Cluster 3 (R²=0.035): Amusement, Anger, Disgust, Joy, Romance,
    Admiration, Awkwardness, Contempt, Empathic pain, Entrancement,
    Satisfaction, Sympathy, Envy, Guilt
    → 잘 안 되는 그룹 (6 basic emotion 대부분 여기)
```

**해석:** Cluster 1은 시각적으로 구별 가능한(visually distinctive) 감정들. Cluster 3은 시각적으로 모호한 감정들.

### 2.7 Partial Mantel Test

**뭘 했나:** Stimulus/Brain/Behavior 세 RSM(Representational Similarity Matrix)의 관계. 특히 stimulus를 통제한 후에도 brain-behavior 관련이 있는지.

**결과:**
```
Stimulus ↔ Brain:    r=0.075
Stimulus ↔ Behavior: r=0.160
Brain ↔ Behavior:    r=-0.039
Partial (Brain ↔ Behavior | Stimulus): r=-0.031, p=1.44e-28
```

**Brain ↔ Behavior 상관이 음수.** Brain-JEPA의 RSM 구조가 행동 감정 RSM과 반대.

**⚠️ 해석:** Brain-JEPA가 resting-state 기반이라, 비디오 간 유사성이 감정이 아닌 다른 기준으로 정의됐을 가능성. Raw fMRI로 재확인 필요.

### 2.8 V-JEPA2 vs CLIP

**뭘 했나:** Brain → V-JEPA2 PC 예측과 Brain → CLIP PC 예측 비교.

**결과:**
```
Brain → V-JEPA2: PC1(0.373), PC2(0.075), PC3(0.088) → 3개 유의
Brain → CLIP:    PC1(0.261), PC2(0.156), PC3(0.127), PC5(0.115), PC6(0.017), PC7(0.013) → 6개 유의
```

**해석:** CLIP이 brain-pred PC가 더 많음(6 vs 3). V-JEPA2는 PC1에 집중(0.373), CLIP은 여러 PC에 분산. 

→ V-JEPA2가 무조건 더 좋은 건 아님. 모델 선택에 추가 비교 필요.

---

## 3. Forward-Reverse 비대칭의 신경과학적 해석

### 결과 요약

```
Forward (Brain → V-JEPA2 PC):  3~6개 유의, Cat/VA=1.44~1.68
Reverse (V-JEPA2 → Brain PC):  0개 유의, 모든 R²=0.000 (Raw에서도 동일)
```

### 왜 이런 비대칭이 나오는가

**V-JEPA2의 표상:**
- Self-supervised → 시각적 패턴이 주요 분산
- 감정은 시각 특성의 부산물로 **암묵적** 인코딩
- PC1에 시각+감정이 섞여 있음 → 뇌가 여기서 감정을 추출 가능

**뇌의 표상:**
- Brain PC1(32.7%) = 저수준 시각 처리, 주의, default mode 등
- 감정은 뇌 분산의 소수 차원에 분산
- V-JEPA2는 외부 자극만 보고 뇌의 내적 처리(주의, 기억, 자기참조)를 모름
- → V-JEPA2 → Brain PC 예측 불가

**Cat/VA 뒤집힘:**
```
Brain PCs (뇌의 주요 분산): Cat/VA = 0.60 → VA 편향
Brain-pred PCs (뇌가 V-JEPA2에서 읽는 것): Cat/VA = 1.44~1.68 → 범주 편향
```

**신경과학적 해석:**
- Barrett의 core affect(VA)가 뇌의 기본 좌표계 → Brain PCA에서 VA 우세
- Cowen의 categorical emotion이 자극-특이적 처리에서 활성화 → brain-pred에서 범주 우세
- **새로운 주장: VA는 내적 상태의 좌표계, 범주는 자극-특이적 인식 코드. 둘 다 존재하지만 역할이 다르다.**

---

## 4. 교수님 피드백 — "Science가 없다"

### 문제

지금까지의 결과는 전부 **관찰(observation):**
```
"뇌가 3개 축을 읽는다" → so what?
"범주적이다" → so what?
"비대칭이다" → so what?
```

### Science가 되려면

```
관찰 → 가설 → 실험적 개입 → 검증

관찰: 뇌의 범주 코드가 VA와 독립적 (AV regress out 97.6%)
가설: 뇌의 범주 코드로 V-JEPA2를 tuning하면 범주 감정 예측이 VA tuning보다 좋아진다
실험: brain-tuned vs VA-tuned vs behavior-tuned
검증: 범주 감정에서 Δ R²가 유의한가?
```

### 프로젝트 목표

> **Emotion Foundation Model = 사람의 감정을 잘 포착하는 모델 개발. 뇌 데이터를 활용.**

지금까지는 "왜 뇌가 필요한가"의 motivation. 모델 개발 자체는 아직 안 함.

---

## 5. 아직 해결 안 된 문제들

### 5.1 모델 선택 — V-JEPA2가 최선인가?

현재 V-JEPA2를 쓰는 이유가 "있으니까"뿐. 비교 후 선택해야 함.

**후보:** V-JEPA2, CLIP, DINOv2, VideoMAE, InternVideo2

**선택 기준:**
```
(a) Self-supervised (감정 라벨 없이 학습) → brain supervision 효과 보려면 필요
(b) Video 처리 (temporal modeling) → 감정은 시간에 따라 변함
(c) 뇌 alignment 높음 → brain-tuning 출발점이 좋아야
(d) 감정 정보가 latent space에 존재 → tuning으로 꺼낼 수 있어야
```

**해야 할 것:** DINOv2, VideoMAE 임베딩 추출 → 동일 분석 → 비교

**현재 CLIP 결과:** Brain-pred 6개 PC (V-JEPA2는 3개). V-JEPA2가 무조건 낫다고 할 수 없음.

### 5.2 Raw fMRI — 왜 450 parcels?

**현재:** Schaefer 400 cortical + 50 subcortical = 450 parcels.

**선택지:**
```
(a) 450 parcels (현재) — parcel 내 평균, 노이즈 감소, fMRI-LM과 호환
(b) Voxel-level (~30K) — 최대 해상도, 노이즈 많음, 차원 너무 높음
(c) Emotion-specific ROIs만 (~20-50 regions) — 가설 기반, 해석 가능
(d) 다른 parcellation (Glasser 360, AAL 116)
```

**ROI 별 분석 필수:**
```
이론 기반 (Theory-driven):
  Lindquist et al. (2012), Kober et al. (2008) meta-analysis 기반
  핵심 영역: Amygdala, Anterior Insula, ACC, mPFC, OFC, STS

데이터 기반 (Data-driven):
  450 parcels 중 감정 예측력 높은 상위 K개 선택 (nested CV)

비교:
  Theory ROIs vs Data-driven ROIs vs 전체 450 vs ROI 밖 나머지
  → 감정이 특정 영역에 집중? 분산 표상? → Horikawa (2020) 주장 검증
```

### 5.3 데이터 품질 점검

반드시 필요한 분석:

**A. 감정 분포 균형**
```
34 감정별: 비디오 수, rating 강도 분포, 희소성
Joy: Strong% = 0.0% → 사실상 학습 불가능
→ 모델 문제 vs 데이터 문제 구분에 필수
```

**B. fMRI 품질**
```
5명 참여자별: SNR, head motion, outlier run 확인
특정 참여자가 나쁘면 결과를 왜곡할 수 있음
```

**C. Inter-Subject Correlation (ISC)**
```
각 비디오에 대해 5명 fMRI의 참여자 간 상관
ISC 높음 = stimulus-driven 반응 (공통)
ISC 낮음 = person-driven 반응 (개인차)
```

**ISC가 낮은 비디오의 의미 (제외가 아니라 분석):**
```
질문: ISC 낮은 비디오는 감정적으로 어떤 특성?
  ISC 높음 → 보편적 감정 (Fear, Disgust 등)?
  ISC 낮음 → 주관적 감정 (Nostalgia, Awkwardness 등)?

추가 분석:
  ISC 높은 비디오만 → Cat/VA ratio = ?
  ISC 낮은 비디오만 → Cat/VA ratio = ?
  → 공유 반응이 범주적? 개인 반응이 범주적?
  
  ISC 낮은 비디오의 rating 분포:
  → 감정 자체가 모호한가? (모든 감정 < 0.1)
  → 감정은 명확한데 뇌 반응만 다른가? (같은 감정, 다른 처리)
```

**D. 행동 Rating과 fMRI의 관계**
```
Horikawa의 감정 rating = crowd-sourced (fMRI 참여자 5명과 별도 집단)
→ fMRI 참여자가 실제로 느낀 감정과 crowd-sourced rating이 다를 수 있음
→ 이 gap이 디코딩 성능의 상한을 제한
```

**E. 비디오 제외 기준**
```
고려 대상:
  - 모든 감정 < 0.1인 비디오 (감정적으로 모호)
  - fMRI 품질 나쁜 비디오 (motion artifact)
  - ISC 극히 낮은 비디오 (공통 반응 없음) → 단, 제외보다 분석 우선
```

### 5.4 감정 디코딩 방법론

**현재 문제:**
```
Ridge regression → 5-fold CV → R²만 보고 있음.
Classification 안 함. Multi-label 안 함. 
Cross-validation이 video-level만.
```

**엄밀한 디코딩:**

Regression:
```
Target: 감정 rating 연속값
Metrics: R², Pearson r, MSE, Spearman ρ
```

Classification:
```
Target: binary (상위 25% vs 하위 25%)
Metrics: AUC-ROC, Balanced accuracy, F1
```

Multi-label:
```
Target: 34개 동시 예측
Metrics: Hamming loss, Sample-averaged AUC, Macro F1
```

Cross-validation:
```
(1) 5-fold CV on videos (현재)
(2) Leave-one-subject-out CV (참여자 일반화)
(3) 둘 다 보고
```

### 5.5 데이터셋 호환성

```
Horikawa:   ~3-5초 클립, 2196개, 34 emotion (crowd-sourced)
Emo-FilM:   수 분 영화 클립, 다른 emotion taxonomy?
ReelMo:     영화 기반
NeuroEmo:   감정 비디오
```

**근본적 문제:** 3초 vs 3분 클립은 V-JEPA2 처리가 완전히 다름.

**선택지:**
```
Option A: Horikawa만으로 완결 (깔끔, 일관적, 즉시 가능)
Option B: 각 데이터셋 독립 분석 (같은 프레임워크, 다른 데이터)
Option C: Horikawa 메인 + 외부 데이터 validation only
```

긴 자극 처리: 클립을 3초 구간으로 잘라서 V-JEPA2 임베딩 + 대응 fMRI TR 매칭 → Horikawa와 동일 프레임워크

---

## 6. Brain Foundation Model 선택지

### Brain-JEPA의 한계 (실험으로 확인됨)

```
학습: resting-state fMRI only
문제: task fMRI 신호 절반 손실 (6개 → 3개 PC)
결과: Raw fMRI가 모든 면에서 더 좋음
```

### 대안

| 모델 | 학습 데이터 | 특징 |
|------|-----------|------|
| Brain-JEPA | Resting-state only | Subject-invariant, task 신호 손실 |
| **BrainSN** | Resting + naturalistic task (1256시간) | Task 신호 보존 가능성 |
| **TRIBE v2** | Naturalistic (영화, 팟캐스트) | Encoding model (자극→뇌 방향) |
| fMRI-LM | Resting + task | LLM 토큰 공간 변환 |
| Raw fMRI | — | 신호 손실 없음, 노이즈 있음, participant-specific |

### fMRI-LM 토큰 공간 활용 가능성

```
fMRI-LM 방식:
  fMRI (450 ROIs) → Transformer + VQ → discrete tokens → LLM space (GPT-2)
  3가지 alignment loss: reconstruction + domain-adversarial + contrastive

우리 프로젝트에 적용:
  fMRI → fMRI-LM → LLM token space (이미 감정 의미가 구조화됨)
  V-JEPA2 → projection → 같은 LLM token space
  → 공통 공간에서 alignment

장점:
  LLM이 이미 감정을 잘 이해 (논문 2: GPT-4 감정 추론 인간 수준)
  → LLM space = 감정적으로 잘 구조화된 target space
  → 단순 L2 loss (Moussa 방식)보다 의미적으로 풍부한 supervision
```

---

## 7. 논문 스토리라인 (Option B: Emotion Foundation Model)

```
Part 1 — 왜 뇌가 필요한가? (현재 결과 = motivation)

  1. V-JEPA2에 감정이 "숨어" 있다
     → 기본으로는 안 나오지만 (V-JEPA2 직접 디코딩 ~0)
     → 뇌가 읽는 3~6개 축에서는 범주 감정이 나옴 (R² up to 0.32)

  2. 뇌의 감정 코드는 VA와 독립적인 범주 구조
     → AV 제거 후 97.6% 유지
     → 행동 VA rating만으로는 이 정보를 제공할 수 없을 수 있음

  3. 비대칭: 뇌가 능동적으로 선택
     → V-JEPA2 → 뇌는 안 됨 (Reverse R²=0)
     → 뇌의 범주 코드는 V-JEPA2에 암묵적으로만 존재
     → 뇌 supervision이 이걸 "꺼내는" 역할

Part 2 — 어떻게 뇌를 넣을 것인가? (brain-tuning = main experiment)

  조건 비교:
    (a) Vanilla V-JEPA2
    (b) Brain-tuned (Raw fMRI)
    (c) Brain-tuned (Brain-JEPA)
    (d) Behavior-tuned (34 categories)
    (e) Behavior-tuned (VA only)

  핵심 질문:
    (b) vs (d): 뇌 > 행동?
    (b) vs (e): 뇌 > VA? (특히 범주에서)
    (b) vs (c): Raw > Brain-JEPA?

Part 3 — 결과 + 해석 (아직 없음)

  Neuroscience prediction:
    뇌의 범주 코드가 VA와 독립 (Part 1에서 확인)
    → brain-tuned가 VA-tuned보다 범주 감정에서 더 향상
    → 이게 확인되면: "뇌가 행동 rating에 없는 범주 감정 정보 제공"

  Emotion Foundation Model claim:
    → "뇌 supervision이 감정 예측을 향상시킨다"
    → "특히 범주 감정에서, VA supervision으로는 얻을 수 없는 개선"
```

---

## 8. 즉시 해야 할 것 (우선순위)

```
이번 주:
  1. 데이터 품질 점검
     - 34 감정 분포, fMRI 품질, ISC, crowd-sourced rating 특성
  
  2. ROI 정의
     - Lindquist/Kober meta-analysis → emotion ROIs 매핑
     - 450 parcels에서 해당 parcel 번호 확인

다음 주:
  3. 엄밀한 디코딩 재실행
     - Regression + Classification + Multi-label
     - 전체 vs Emotion ROI vs Non-emotion ROI
  
  4. 추가 모델 임베딩 추출
     - DINOv2, VideoMAE → 2196 비디오
     - 4개 모델 동일 분석 → base 모델 선택

그 다음:
  5. Raw fMRI로 전체 분석 재실행
     - Variance partitioning, brain residual, partial Mantel
     - Brain-JEPA 한계 보완

  6. Brain-tuning Stage 1
     - 간단한 adapter (데이터 이미 있으니 빠름)
     - 5가지 조건 비교
```
