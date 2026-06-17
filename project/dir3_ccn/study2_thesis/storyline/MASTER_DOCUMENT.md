# Emotion Foundation Model — Master Document

**모든 결과, 해석, 논의, 설계를 총망라한 문서**  
**Last updated:** 2026-04-10

---

# Part A: 프로젝트 개요

## 프로젝트 목표

> **Emotion Foundation Model 개발: 사람의 감정을 잘 포착하는 모델을 만든다. 뇌 데이터를 활용해서.**

## 배경

V-JEPA2는 감정 레이블 없이 비디오의 시각적 패턴만으로 학습한 self-supervised video model이다. 이런 모델의 표상이 인간 뇌의 표상과 부분적으로 정렬된다는 것이 보고되어 왔지만, "뭘" 공유하는지, 특히 감정 차원에서의 alignment는 연구된 적 없다.

## 핵심 질문

1. 뇌가 V-JEPA2에서 "읽을 수 있는" 부분은 정확히 무엇인가?
2. 그 부분이 감정과 관련이 있는가?
3. 관련된다면, 연속 감정(VA)인가 범주 감정(categorical)인가?
4. 뇌 신호를 이용해 V-JEPA2의 감정 표상을 개선할 수 있는가?

---

# Part B: 데이터

## 현재 사용 중인 데이터

### Horikawa 2020 (메인)

| 항목 | 내용 |
|------|------|
| 참여자 | 5명 (건강한 성인, 일본) |
| 자극 | 2,196개 감정 유발 비디오 클립 (~3초, ~5프레임) |
| fMRI | 3T, 전뇌 |
| 감정 레이블 | 34 범주 (Cowen & Keltner 2017) + Valence + Arousal |
| 레이블 출처 | **Crowd-sourced** (fMRI 참여자 5명과 별도 집단이 rating) |
| 특징 | image-like 짧은 클립, 이미 전처리 완료 |

### 이미 추출된 임베딩

| 파일 | 형태 | 설명 |
|------|------|------|
| `vjepa2_embeddings.npy` | (2196, 1408) | V-JEPA2 ViT-G |
| `clip_embeddings.npy` | (2196, 512) | CLIP baseline |
| `brain_jepa_embeddings.npy` | (5, 2196, 768) | Brain-JEPA (resting-state 모델) |
| `fmri_raw.npy` | (5, 2196, 450) | Raw fMRI (450 parcel) |

## 추가 데이터셋 (사용 예정)

### Emo-FilM 2025

| 항목 | 내용 |
|------|------|
| 참여자 | 30명 (fMRI) + 44명 (rater) |
| 자극 | 14개 단편 영화, 총 2.5시간 |
| fMRI | 3T, resting-state 포함 |
| 감정 레이블 | 50개 항목 (discrete emotions + appraisal + motivation + expression + feeling) |
| 특징 | fMRI 참여자 본인도 rating함 (crowd-sourced 아님), physiological data 포함 |
| 공개 | [GitHub](https://github.com/MIPLabCH/Emo-FilM) |

**Horikawa 보완:** n=5→30, 3초→2.5시간, crowd-sourced→본인 rating, 34→50 감정

### ReelMo 2025

| 항목 | 내용 |
|------|------|
| 참여자 | 20명 (fMRI, Jojo Rabbit 시청) + 161명 (행동, 60편 영화) |
| 자극 | fMRI: Jojo Rabbit 풀타임 영화 (2시간), 행동: 60편 영화 |
| fMRI | 40시간 분량 |
| 감정 레이블 | 20개 감정, **moment-by-moment** rating |
| 특징 | 유일하게 풀타임 영화 + 시간 연속 감정 annotation |
| 공개 | [Nature Scientific Data](https://www.nature.com/articles/s41597-025-05159-6) |

**고유 가치:** 시간 역학(temporal dynamics) 분석 가능. 감정 전환, 내러티브 효과.

### HCP Movie-Watching

| 항목 | 내용 |
|------|------|
| 참여자 | 176명 |
| 자극 | 영화 클립 (독립 + 할리우드), 1-4.3분, 총 1시간 |
| fMRI | **7T** (고해상도) |
| 감정 레이블 | **없음** (행동 trait만: NEO-FFI 성격 등) |
| 특징 | 대규모, 고품질, 개인차 분석 가능 |
| 공개 | [HCP](https://github.com/datalad-datasets/hcp_movies) |

**고유 가치:** n=176으로 개인차 분석. 7T 고해상도. 감정 레이블은 LLM으로 생성 가능.

### NSD (Natural Scenes Dataset)

| 항목 | 내용 |
|------|------|
| 참여자 | 8명 |
| 자극 | 73,000장 COCO 이미지 |
| fMRI | **7T**, 30-40 세션/참여자 |
| 감정 레이블 | **VA annotation 있음** (범주 없음, LLM으로 생성 가능) |
| 특징 | image 데이터셋. Horikawa(video)와 image vs video 비교 가능 |
| 공개 | [naturalscenesdataset.org](https://naturalscenesdataset.org/) |

### IAPS fMRI (Hsiao et al. 2024)

| 항목 | 내용 |
|------|------|
| 참여자 | 56명 |
| 자극 | 90 IAPS 이미지 |
| fMRI | 3T |
| 감정 레이블 | VA (positive/negative/neutral 3조건) |
| 특징 | 표준화 자극, n=56으로 큼 |
| 공개 | [NeuroVault](https://neurovault.org/collections/16284/) |

## 4개 데이터셋의 역할 분담

```
Horikawa  → 발견 + 증명 (Q1: 뇌가 범주적으로 읽는가, Q2: brain-tuning)
Emo-FilM  → 재현 + 확장 (n↑, 긴 자극, 풍부한 감정, 본인 rating)
ReelMo    → 시간 역학 (moment-by-moment, 감정 전환, 내러티브)
HCP-movie → 규모 + 개인차 (176명, 7T, 감정 레이블 없이도 alignment 분석)
```

NSD, IAPS는 image vs video 비교에 사용 가능.

## 데이터 품질 점검 필요 사항 (Horikawa)

### A. 감정 분포 균형

34개 감정별 rating > 0.3인 비디오 수:
```
Joy:      0.0% → 사실상 데이터 없음
Fear:     0.0%
Disgust:  0.2% (약 4개)
Anger:    1.3%
Sadness:  4.1%
Surprise: 4.1%

vs
Amusement: 29.6%
Awe:       11.2%
Aesthetic appreciation: 10.0%
```

→ 6 basic emotion이 디코딩 안 되는 건 모델 문제가 아니라 **데이터 문제.**

### B. fMRI 품질

5명 참여자별 SNR, head motion, outlier 확인 필요.

### C. Inter-Subject Correlation (ISC)

각 비디오에 대해 5명 fMRI의 참여자 간 상관. ISC 낮은 비디오 = 개인차 큰 비디오.

**ISC가 낮은 비디오는 제외가 아니라 분석 대상:**
- ISC 높은 비디오의 감정 특성 vs ISC 낮은 비디오의 감정 특성
- ISC가 낮은 이유: 감정 자체가 모호? 같은 감정인데 처리 방식이 다름?
- ISC별 Cat/VA ratio 차이?

### D. 행동 Rating과 fMRI 매칭

Horikawa의 감정 rating = crowd-sourced (fMRI 참여자 5명과 별도 집단).
→ fMRI 참여자가 실제로 느낀 감정과 crowd-sourced rating이 다를 수 있음.
→ 이 gap이 디코딩 성능의 상한을 제한.
→ Emo-FilM은 본인 rating이라 이 문제 없음 → 비교 가치.

### E. 비디오 제외 기준

- 모든 감정 < 0.1인 비디오 (감정적으로 모호)
- fMRI 품질 나쁜 비디오
- ISC 극히 낮은 비디오 → 제외보다 분석 우선

---

# Part C: 완료된 분석과 결과

## Analysis 1: Forward PCA+Ridge — "V-JEPA2의 축 중에서 뇌가 읽는 것은?"

### 방법

```
V-JEPA2 (2196, 1408) → PCA → 100 PCs (V-JEPA2 분산 기준으로 축 정의)
Brain-JEPA mean (2196, 768) → Ridge → V-JEPA2 PC_i 예측 (5-fold CV)
각 PC 독립적으로 R² 산출
Permutation test (n=1000) + FDR correction (BH, q<0.05)
```

축 정의 주체 = V-JEPA2 단독. 뇌는 시험 응시자.

### 결과

**Brain-JEPA 기준:**

| PC | R² | FDR q | 유의? |
|----|-----|-------|------|
| PC1 | 0.373 | <0.001 | Yes |
| PC2 | 0.075 | <0.001 | Yes |
| PC3 | 0.088 | <0.001 | Yes |
| PC4 | 0.000 (artifact) | — | Excluded |
| PC5-100 | 0.000 | 1.000 | No |

→ **100개 중 3개만 유의.** 이 3개 = "brain-predictable subspace."

**Raw fMRI 기준:**

| PC | Brain-JEPA R² | Raw fMRI R² |
|----|-------------|-------------|
| PC1 | 0.373 | 0.354 |
| PC2 | 0.075 | **0.227** |
| PC3 | 0.088 | **0.307** |
| PC4 | 0.000 | **0.147** |
| PC5 | 0.000 | **0.083** |
| PC6 | 0.000 | **0.036** |

→ Raw fMRI에서는 **6개** 유의. Brain-JEPA가 신호 절반 손실.

### Figure 1

- **1A:** R² per V-JEPA2 PC (40개 표시). 파란=brain-pred(3개), 회색=unpred, *=유의.
- **1B:** Brain-pred vs unpred의 mean max|r| with 34 emotions.

---

## Analysis 2: 감정 디코딩 — "그 축들은 범주적인가?"

### 방법

```
X = brain-pred subspace (PC1-3, 3차원)
y = 34개 감정 각각 / Arousal / Valence
Ridge regression (5-fold CV) → R²
```

### 결과

**Top 10 decoded emotions (brain-pred subspace):**

| Rank | Emotion | R² |
|------|---------|-----|
| 1 | Aesthetic appreciation | 0.323 |
| 2 | Excitement | 0.200 |
| 3 | Uncomfortable | 0.172 |
| 4 | Calmness | 0.136 |
| 5 | Amusement | 0.116 |
| 6 | Annoyance | 0.106 |
| 7 | Adoration | 0.081 |
| 8 | Romance | 0.079 |
| 9 | Empathic pain | 0.074 |
| 10 | Anxiety | 0.061 |

**6 Basic Emotion:**

| Emotion | R² | Rank (/34) | Strong% |
|---------|-----|-----------|---------|
| Surprise | 0.045 | 15 | 4.1% |
| Anger | 0.012 | 25 | 1.3% |
| Sadness | 0.009 | 26 | 4.1% |
| Disgust | 0.009 | 27 | 0.2% |
| Joy | 0.003 | 30 | 0.0% |
| Fear | 0.000 | 32 | 0.0% |

→ 6 basic 전부 하위권. 원인: 데이터에서 이 감정들이 거의 태깅되지 않음 (Joy 0개, Fear 0개).

**Cat/VA Ratio:**

| Subspace | Cat R² | AV R² | Cat/VA |
|----------|--------|-------|--------|
| Brain-pred (PC1-3) BJ | 0.055 | 0.038 | **1.44** |
| Brain-pred (PC1-6) Raw | 0.076 | 0.045 | **1.68** |
| Full space (100 PCs) | 0.170 | 0.135 | 1.26 |

→ Brain-pred subspace가 범주 감정에 편향. Raw fMRI가 더 범주적 (1.68 > 1.44).

### Figure 2

- **2A:** 34 emotion + AV decoding R² (sorted bars). 파란=범주, 빨간=VA.
- **2B:** Cat/VA ratio: brain-pred(1.44) vs full(1.26).

---

## Analysis 3: Reverse PCA+Ridge — "V-JEPA2가 뇌의 축을 읽을 수 있는가?"

### 방법

```
Brain-JEPA mean (2196, 768) → PCA → 100 Brain PCs
V-JEPA2 (2196, 1408) → Ridge → Brain PC_j 예측 (5-fold CV)
Permutation test (n=1000) + FDR correction
```

### 결과

**완전한 비대칭:**

```
Forward:  Brain → V-JEPA2 PC → 3~6개 유의 (R² up to 0.37)
Reverse:  V-JEPA2 → Brain PC → 0개 유의 (모든 R²=0.000)
(Raw fMRI에서도 Reverse는 전부 R²=0.000)
```

**Brain PCA 분산 구조:**

| Brain PC | 분산% | 누적 | V-JEPA2→R² | Top emotion |
|----------|-------|------|-----------|------------|
| BPC1 | 32.7% | 32.7% | 0.000 | Annoyance (-0.22) |
| BPC2 | 16.3% | 49.0% | 0.000 | Guilt (+0.15) |
| BPC3 | 12.0% | 61.0% | 0.000 | Interest (-0.20) |
| BPC4 | 6.7% | 67.6% | 0.000 | Amusement (+0.18) |
| BPC5 | 6.2% | 73.8% | 0.000 | Relief (-0.11) |

**Brain PCs 감정 디코딩: VA > Category**

| Brain subspace | Cat R² | AV R² | Cat/VA |
|---------------|--------|-------|--------|
| Brain PC1-3 | 0.016 | 0.026 | **0.61** |
| Brain PC1-10 | 0.043 | 0.071 | **0.60** |
| Brain all 100 | 0.055 | 0.091 | **0.60** |

→ **Forward Cat/VA=1.44~1.68 vs Reverse Cat/VA=0.60 — 완전히 뒤집힘.**

### Figure

- `figure_three_methods_comparison`: Forward R² / Reverse R²(=0) / CCA r 나란히.
- `figure_forward_vs_reverse_ratio`: Cat/VA 1.44 vs 0.60.

---

## Analysis 4: CCA — "뇌와 V-JEPA2가 함께 찾는 공유 축은?"

### 방법

```
V-JEPA2 (2196, 1408) → StandardScaler → PCA(100) → (2196, 100) [분산 69.3% 보존]
Brain-JEPA (2196, 768) → StandardScaler → PCA(100) → (2196, 100) [분산 99.5% 보존]
CCA(100 components)
양쪽에서 동시에 상관 최대화하는 방향 쌍을 찾음
Permutation test (n=1000) + FDR correction
```

축 정의 = 양쪽 공동 (상관 기준). PCA+Ridge와의 차이: PCA+Ridge는 V-JEPA2가 단독으로 축 정의, CCA는 양쪽이 함께.

### 결과

**유의성:** 88/100 CC 유의 (FDR q<0.05). CC83(r=0.063)부터 비유의.

**Canonical correlations:**

| 구간 | CCs | r 범위 |
|------|-----|--------|
| CC1-5 | 강한 공유 | 0.774 – 0.572 |
| CC6-15 | 중간 | 0.522 – 0.389 |
| CC16-27 | 약-중간 | 0.368 – 0.307 |
| CC28-75 | 약한 | 0.297 – 0.102 |
| CC76-100 | 무시 | 0.093 – 0.002 |

CCs with r > 0.3: **27개** (substantial).

**CC 감정 프로필 (Top 10):**

| CC | r | Top emotion | 2nd | 3rd | A | V |
|----|---|-----------|-----|-----|---|---|
| CC1 | 0.774 | Annoyance (+0.46) | Interest (+0.34) | Anxiety (+0.34) | +0.24 | -0.15 |
| CC2 | 0.679 | Aesthetic apprec. (-0.44) | Excitement (-0.37) | Relief (-0.30) | -0.11 | +0.02 |
| CC3 | 0.649 | Interest (-0.18) | Empathic pain (+0.18) | Anxiety (-0.17) | +0.01 | +0.03 |
| CC4 | 0.608 | Uncomfortable (-0.29) | Sadness (+0.22) | Surprise (-0.20) | -0.12 | +0.02 |
| CC5 | 0.571 | Aesthetic apprec. (-0.19) | Amusement (+0.18) | Excitement (-0.13) | -0.08 | +0.01 |
| CC6 | 0.522 | Uncomfortable (+0.33) | Awe (-0.27) | Adoration (-0.24) | +0.02 | -0.19 |
| CC7 | 0.495 | Uncomfortable (+0.18) | Nostalgia (-0.18) | Sympathy (-0.14) | +0.02 | +0.17 |
| CC8 | 0.494 | Adoration (-0.27) | Awe (-0.16) | Guilt (+0.15) | +0.08 | -0.07 |
| CC9 | 0.460 | Empathic pain (+0.20) | Nostalgia (+0.18) | Sympathy (+0.16) | -0.04 | -0.17 |
| CC10 | 0.457 | Uncomfortable (+0.16) | Surprise (+0.14) | Aesthetic apprec. (+0.11) | -0.01 | +0.10 |

→ CC들이 VA가 아닌 **구체적 범주 감정**과 연결.
→ CC1=불쾌/관심축, CC2=미학/흥분축, CC4=불편/슬픔축, CC8=사랑축, CC9=공감축.

**디코딩:**

| Method | Dims | Cat R² | AV R² | Cat/VA |
|--------|------|--------|-------|--------|
| CCA-sig (88) | 88 | 0.180 | 0.161 | 1.12 |
| CCA-all (100) | 100 | 0.182 | 0.155 | 1.17 |
| PCA PC1-3 | 3 | 0.053 | 0.035 | **1.51** |
| PCA all 100 | 100 | 0.182 | 0.155 | 1.17 |

→ CCA(88)와 PCA(100) 절대 R²는 비슷하지만 Cat/VA는 PCA(3)이 가장 높음.

**참여자 안정성:** CC1 mean = 0.719 ± 0.013 (5명).

### PCA+Ridge vs CCA 비교

| | PCA+Ridge | CCA |
|---|---|---|
| 축 정의 | V-JEPA2 단독 (분산) | 양쪽 공동 (상관) |
| 뇌 역할 | 시험 응시자 | 공동 참여자 |
| 유의한 축 | 3개 (엄격) | 88개 (관대) |
| Substantial | 3개 | 27개 (r>0.3) |
| Cat/VA | 1.51 (높음) | 1.12 (중간) |
| 강점 | 선택성 명확 | 숨겨진 공유도 발견 |
| 약점 | V-JEPA2 분산 기준 편향 | N 크면 뭐든 유의 |

→ CCA = 큰 그림(숲), PCA+Ridge = 날카로운 주장(나무). 보완 관계.

### Figure 3-7

- **3A:** CCA canonical correlations (30개, 이전 버전).
- **3B:** CC1-5 × emotion heatmap.
- **5:** Subject-level CCA stability.
- **6:** All CCs × 34 emotions full heatmap.
- **7:** PCA vs CCA side-by-side (R² spectrum, r spectrum, Cat/VA).
- `figure_cca100_spectrum`: CC1-100 전체 (초록/연두/회색 3단계).

---

## Exp26: 기본 해석 분석

### Rating 분포 Artifact 확인

```
R² vs Rating Std:  r=0.480, p=0.004 ⚠️ (부분적 confound)
R² vs Rating Mean: r=0.384, p=0.025 ⚠️
```

R²의 ~23%가 분산으로 설명. 77%는 분산과 무관한 진짜 신호.

Aesthetic appreciation: Std=0.154 (Amusement 0.233보다 작은데 R² 1위) → 분산만으로 설명 안 됨.

### AV Regress Out — 범주가 VA의 위장인가?

```
방법: 각 감정 rating에서 VA 성분 제거 (linear regression 잔차) → 잔차로 디코딩

결과:
  AV 제거 전: Mean R² = 0.055
  AV 제거 후: Mean R² = 0.054
  유지율: 97.6%

개별 감정:
  Aesthetic appreciation: 101% 유지
  Amusement: 130% (VA가 노이즈였음)
  Romance: 148%
  Anxiety: 41% (VA 성분 컸음)
```

**결론: 범주 감정 정보는 VA와 독립적. VA의 위장이 아님.** Cowen & Keltner (2017) 지지.

### Raw fMRI vs Brain-JEPA

```
Brain-JEPA: PC1-3 (3개 유의), Cat/VA=1.44
Raw fMRI:   PC1-6 (6개 유의), Cat/VA=1.68

뇌에서 직접 감정 디코딩:
  Raw fMRI: Cat R²=0.026, AV R²=0.073, Cat/VA=0.35
  Brain-JEPA: Cat R²=0.010, AV R²=0.033, Cat/VA=0.32
  V-JEPA2 직접: 전부 R²=0.000
```

**Brain-JEPA가 task fMRI 신호 절반 이상 손실.** Resting-state에서 학습했기 때문.

### 감정 Rating PCA 차원 수

```
80% 분산 = 12차원, 90% = 18, 95% = 23, 99% = 29
CCA substantial CCs (r>0.3) = 27개
Cowen (2017) = ~27 범주
```

수치적 일치. 뇌-비디오 공유 차원 수 ≈ 감정 범주 차원 수.

---

## Exp27: Deep Analysis

### 6 Basic Emotion 왜 안 나오는가

```
6 Basic:  mean R²=0.013, Strong%=1.6%
Other 28: mean R²=0.064, Strong%=5.6%

R² 상관:
  R² vs Std:        r=0.480, p=0.004
  R² vs Strong%:    r=0.398, p=0.020
  R² vs MaxCorr:    r=0.273, p=0.119 (비유의)
```

핵심 원인: Horikawa의 34범주 체계에서 "Joy", "Fear" 같은 넓은 라벨이 거의 안 눌림. Cowen 체계의 세분화 범주(Amusement, Excitement)가 더 적합.

### Rank-Normalized R²

```
Original vs Ranked R² 상관: r=0.971
```

분포를 균일하게 바꿔도 순서 거의 불변. **R² 순서는 분포 artifact 아님.**

### Variance Partitioning (Stimulus × Brain × Behavior)

```
각 감정: R²(V-JEPA2 PC1-3) + R²(Brain-JEPA) + R²(합쳐서) → 분해

Mean across 34:
  Stimulus unique:  0.014
  Brain unique:     0.003
  Shared:           0.041
```

대부분 shared. Brain unique 작음 (Brain-JEPA 한계 가능성).
예외: Uncomfortable — brain unique = 0.102.

### Brain Residual

```
Brain-JEPA에서 V-JEPA2 성분 제거 → 잔차로 감정 디코딩:
  Cat R² = 0.000, AV R² = 0.004
```

Brain-JEPA 잔차에 감정 정보 없음. → Brain-JEPA가 인코딩하는 감정 ≈ V-JEPA2와 공유되는 부분.

⚠️ Brain-JEPA 한계일 수 있음. Raw fMRI에서 재확인 필요.

### Emotion Clustering

```
brain-pred space (PC1-3)에서 34 감정 계층적 군집:

Cluster 1 (R²=0.102): Aesthetic appreciation, Excitement, Uncomfortable, Calmness, ...
  → visually distinctive 감정

Cluster 2 (R²=0.042): Anxiety, Horror, Interest, Annoyance, ...
  → 중간

Cluster 3 (R²=0.035): Amusement, Anger, Disgust, Joy, Romance, ...
  → visually ambiguous 감정 (6 basic 대부분 여기)
```

### Partial Mantel Test

```
Stimulus ↔ Brain:    r=0.075
Stimulus ↔ Behavior: r=0.160
Brain ↔ Behavior:    r=-0.039
Partial (Brain ↔ Behavior | Stimulus): r=-0.031
```

Brain ↔ Behavior 음수. Brain-JEPA RSM이 감정 RSM과 반대. Brain-JEPA 한계 가능성. Raw fMRI 재확인 필요.

### V-JEPA2 vs CLIP

```
Brain → PC prediction:
  V-JEPA2: PC1(0.373), PC2(0.075), PC3(0.088) → 3개
  CLIP:    PC1(0.261), PC2(0.156), PC3(0.127), PC5(0.115), PC6(0.017), PC7(0.013) → 6개
```

CLIP이 brain-pred PC 더 많음 (6 vs 3). V-JEPA2는 PC1 집중(0.373), CLIP은 분산.

→ V-JEPA2가 무조건 최선이 아님. 추가 비교 필요.

---

# Part D: 해석

## Forward-Reverse 비대칭의 의미

```
Forward:  Brain → V-JEPA2 PC: 3~6개 유의, Cat/VA=1.44~1.68
Reverse:  V-JEPA2 → Brain PC: 0개 유의, R²=0.000 (Raw에서도 동일)
```

**왜 이런 비대칭?**

V-JEPA2: self-supervised → 시각 패턴이 주요 분산. 감정은 부산물로 암묵적 인코딩. PC1에 시각+감정 섞여 있음.

뇌: BPC1(32.7%) = 저수준 시각 처리, 주의, default mode 등. 감정은 소수 차원에 분산. V-JEPA2는 외부 자극만 봄 → 뇌의 내적 처리(주의, 기억, 자기참조) 모름 → Brain PC 예측 불가.

**핵심:** 뇌가 V-JEPA2를 능동적으로 읽는 것이지, V-JEPA2가 뇌를 반영하는 게 아님.

## Cat/VA 뒤집힘의 이론적 의미

```
Brain PCs → Cat/VA = 0.60 (VA 편향)
Brain-pred PCs → Cat/VA = 1.44~1.68 (범주 편향)
```

**Barrett vs Cowen 논쟁과 연결:**

Barrett (constructionist): 감정의 기본은 VA (core affect). → Brain PCs의 VA 편향과 일관.
Cowen (categorical): 감정은 이산적 범주. → Brain-pred의 범주 편향과 일관.

**새로운 해석:** 둘 다 맞지만 역할이 다르다.
- VA = 뇌의 내적 기본 좌표계 (Barrett이 맞음)
- 범주 = 외부 자극에서 추출하는 인식 코드 (Cowen이 맞음)
- **뇌는 VA를 기본으로 하되, 외부 시각 자극에서는 범주를 선택적으로 추출한다.**

## AV Independence — 범주는 VA의 부산물이 아니다

AV regress out 후 97.6% 유지. 이건 Cowen & Keltner (2017) 강하게 지지: 감정 범주는 VA로 환원 불가능.

## CCA ~27개 CC ≈ Cowen의 27 범주

감정 rating PCA: 95% 분산에 23차원, 99%에 29차원 → ~27. CCA substantial CCs: 27개. 수치적 일치. 뇌-비디오 공유 차원 수 = 감정 범주 수. (suggestive, 증명 아님)

## Brain-JEPA의 한계

Resting-state에서 학습 → task fMRI 신호 절반 손실 (6→3 PC, Cat/VA 1.68→1.44). 뇌에서 직접 디코딩도 Raw가 2.5배 높음. Partial Mantel에서 음수 나온 것도 Brain-JEPA RSM 문제일 수 있음.

→ **Raw fMRI를 메인으로, Brain-JEPA는 비교용으로.**

## Aesthetic Appreciation이 가장 높은 이유

부분적으로 rating 분포 (R²-Std r=0.48), 하지만 Std가 가장 높은 게 아닌데 R²가 1위. V-JEPA2의 시각적 특성이 미적 감상과 직결될 가능성 (Chatterjee & Vartanian 2014, Vessel et al. 2012). Rank normalize 후에도 1위 유지 (r=0.97).

---

# Part E: 참고 논문과 포지셔닝

## 핵심 참고 논문

### 1. VCA: Biologically Inspired Visual Emotion Processing (bioRxiv 2025)

- **뭘 했나:** CLIP-ViT + amygdala 모듈 → VA 예측 + amygdala fMRI alignment
- **결과:** Valence r≈0.9, Arousal r≈0.7. 학습 후 amygdala fMRI와 alignment 증가.
- **한계:** image only, amygdala only, VA only, post-hoc alignment

### 2. 100 Neural Networks and Brains Watching Videos (ICLR 2025)

- **뭘 했나:** 99개 image/video 모델의 뇌 alignment 대규모 벤치마킹
- **결과:** temporal modeling → 초기 시각 영역, classification task → 고수준 영역, 복잡도↔alignment 음의 상관
- **한계:** **emotion을 안 봤음** → 우리가 채울 gap

### 3. Human-like Affective Cognition in Foundation Models (arXiv 2409.11733)

- **뭘 했나:** GPT-4, Claude, Gemini의 감정 이해 능력 평가
- **결과:** LLM이 인간 수준의 감정 추론. Chain-of-thought으로 향상.
- **우리에게:** LLM이 감정을 이해하므로 LLM token space = 감정적으로 구조화된 target space

### 4. fMRI-LM (arXiv 2511.21760)

- **뭘 했나:** fMRI → discrete tokens → GPT-2 token space alignment
- **방법:** Transformer + VQ tokenizer, 450 ROI, domain-adversarial + contrastive loss
- **우리에게:** fMRI-LM 방식으로 brain-tuning 가능. 450 ROI = 우리 raw fMRI와 호환.

### 5. Brain-tuning (Moussa & Toneva, NeurIPS 2025)

- **뭘 했나:** HuBERT/Wav2Vec2를 fMRI에 LoRA fine-tune → brain alignment + downstream 향상
- **결과:** 5x data efficiency, 50% alignment 향상, downstream 저하 없음
- **우리에게:** 방법론적 선례. Speech → Video/Emotion으로 확장.

## 우리의 포지셔닝 (vs VCA)

```
VCA (2025):
  Image + Amygdala + VA + Post-hoc alignment

우리:
  Video + 전뇌 + 범주 감정 + Direct brain supervision (brain-tuning)

4가지 확장:
  (1) Image → Video (temporal emotion dynamics)
  (2) Amygdala → 전뇌 (distributed emotion representation, Horikawa 2020)
  (3) VA → Categorical (AV regress out 97.6%, Cowen 지지)
  (4) Post-hoc → Direct supervision (brain-tuning)
```

---

# Part F: 아직 해야 할 것

## 데이터 점검

- [ ] 34 감정 분포 상세 (비디오 수, 강도, 희소성)
- [ ] Subject별 fMRI 품질 (SNR, motion)
- [ ] ISC 계산 + ISC별 감정 특성
- [ ] ISC 낮은 비디오의 의미 분석 (감정 모호? 처리 방식 차이?)
- [ ] Crowd-sourced rating 특성 확인

## ROI 분석

- [ ] Theory-driven emotion ROIs 정의 (Lindquist 2012, Kober 2008)
  - Amygdala, Anterior Insula, ACC, mPFC, OFC, STS
- [ ] 450 parcels에서 매핑
- [ ] Theory ROIs vs Data-driven ROIs vs 전체 vs ROI 밖
- [ ] → 감정이 특정 영역에 집중? 분산 표상? (Horikawa 2020 주장 검증)

## 엄밀한 디코딩

- [ ] Regression: R², Pearson r, MSE, Spearman ρ
- [ ] Classification: binary (상위 25% vs 하위 25%), AUC-ROC, balanced accuracy, F1
- [ ] Multi-label: 34개 동시 예측, Hamming loss, macro F1
- [ ] CV: video-level 5-fold + leave-one-subject-out

## 모델 비교

- [ ] DINOv2 임베딩 추출 (2196 비디오)
- [ ] VideoMAE 임베딩 추출
- [ ] 4개 모델 동일 분석: Forward/Reverse, Cat/VA ratio, 감정 디코딩
- [ ] Image vs Video model 비교 (Horikawa가 image-like이니까)
- [ ] 모델 선택 기준: (a) self-supervised, (b) temporal, (c) brain alignment, (d) emotion 정보

## Raw fMRI 전체 재분석

- [ ] Raw fMRI로: Variance Partitioning, Brain Residual, Partial Mantel
- [ ] Brain-JEPA 한계 보완

## Brain-Tuning

### Stage 1: Proof of concept (Horikawa)

```
5가지 조건:
  (a) Vanilla V-JEPA2
  (b) Brain-tuned (Raw fMRI, 450)
  (c) Brain-tuned (Brain-JEPA, 768)
  (d) Behavior-tuned (34 categories)
  (e) Behavior-tuned (VA only)

방법: V-JEPA2 embedding(1408) → Linear adapter → target → L2 loss
평가: adapted embedding → linear probe → 34 emotion + VA (held-out 220 videos)

핵심 비교:
  (b) vs (d): 뇌 > 행동?
  (b) vs (e): 뇌 > VA? (특히 범주에서)
  (b) vs (c): Raw > Brain-JEPA?
```

### Stage 2: Scale-up (Emo-FilM)

```
Emo-FilM 30명으로 brain-tuning scaling
Multi-subject training (Moussa 방식)
```

## 추가 데이터셋

### Emo-FilM

- [ ] 데이터 다운로드 + 전처리
- [ ] V-JEPA2 임베딩 추출 (영화 클립 → 3초 단위 or 전체)
- [ ] Q1 재현 (Forward/Reverse, Cat/VA)
- [ ] 50개 감정 항목 분석 (appraisal 포함)

### ReelMo

- [ ] Jojo Rabbit fMRI 데이터 접근
- [ ] Moment-by-moment alignment 변화 분석
- [ ] 감정 전환점 분석

### HCP-movie

- [ ] 데이터 접근 + 전처리
- [ ] 176명 Forward/Reverse/CCA
- [ ] 개인차 분석 (NEO-FFI 성격 등)
- [ ] (가능하면) LLM으로 감정 annotation 생성

---

# Part G: Brain Foundation Model 선택지

| 모델 | 학습 데이터 | 입출력 | 장단점 |
|------|-----------|--------|--------|
| Brain-JEPA | Resting-state | fMRI→embedding(768) | Subject-invariant, 하지만 task 신호 손실 |
| BrainSN | Resting + naturalistic task (1256h) | fMRI→embedding | Task 보존 가능, 확인 필요 |
| TRIBE v2 | Naturalistic task (451h) | 자극→predicted fMRI | Encoding model (방향 다름), 내부 표상 활용 가능 |
| fMRI-LM | Resting + task | fMRI→LLM tokens | LLM space alignment, 450 ROI 호환 |
| Raw fMRI | — | 없음 (원본) | 신호 손실 없음, 노이즈, participant-specific |

### TRIBE v2 활용 방안

TRIBE v2는 fMRI를 입력으로 안 받음 (자극→뇌 방향). 직접 대체 불가. 하지만:

```
방법 1: TRIBE v2 내부 표상을 V-JEPA2 대안으로 사용
  → "이미 brain-aligned된 비디오 표상" → brain-tuning 안 해도 되는 간접 증거

방법 2: TRIBE v2 predicted fMRI를 데이터 증강으로
  → Horikawa 비디오 → TRIBE v2 → predicted fMRI → n=5 한계 우회

방법 3: 비교군으로
  → TRIBE predicted fMRI vs 실제 fMRI → 차이 = 뇌의 고유 정보
```

### fMRI-LM Token 방식

```
fMRI (450 ROIs) → Transformer + VQ → discrete tokens → LLM space (GPT-2)
V-JEPA2 (1408) → projection → 같은 LLM space
→ 공통 space에서 alignment

장점: LLM space가 이미 감정 의미를 인코딩 (논문 3: LLM 감정 이해 인간 수준)
→ 단순 L2 loss보다 의미적으로 풍부한 supervision
```

---


---

# Part H: 전체 Experiment Raw 수치 — 빠짐없이

## Exp 01-02: Brain-JEPA RSM + Subject CKA

rsa_cross_subject ((5, 5)):
  row0: [1.0000, 0.3320, 0.3185, 0.2853, 0.3293]
  row1: [0.3320, 1.0000, 0.3809, 0.3589, 0.4122]
  row2: [0.3185, 0.3809, 1.0000, 0.3270, 0.3672]
  row3: [0.2853, 0.3589, 0.3270, 1.0000, 0.3603]
  row4: [0.3293, 0.4122, 0.3672, 0.3603, 1.0000]
off_diag_mean: [0.3472]
off_diag_std: [0.0342]

Subject CKA:
  cka_vjepa_per_subj: [0.054835, 0.063292, 0.055383, 0.045845, 0.072584]
  cka_clip_per_subj: [0.047351, 0.060017, 0.050774, 0.051293, 0.060269]
  delta_per_subj: [0.007484, 0.003274, 0.004609, -0.005448, 0.012314]
  mean_cka_vjepa: [0.058388]
  mean_cka_clip: [0.053941]

## Exp 03-04: Cross-space RSA (34 emotions)
| Emotion                   |    Brain |   V-JEPA2 |     CLIP |
|---------------------------|----------|-----------|----------|
| Admiration                |  -0.0188 |    0.0146 |  -0.0140 |
| Adoration                 |   0.0057 |    0.0919 |   0.0815 |
| Aesthetic appreciation    |   0.0226 |   -0.1273 |  -0.0027 |
| Amusement                 |  -0.0826 |    0.1803 |   0.1335 |
| Anger                     |  -0.0021 |    0.0283 |   0.0315 |
| Anxiety                   |  -0.0369 |    0.0393 |   0.1299 |
| Awe                       |  -0.0436 |   -0.0067 |   0.0918 |
| Awkwardness               |   0.0160 |    0.0446 |   0.0145 |
| Boredom                   |  -0.0011 |   -0.0431 |  -0.0931 |
| Calmness                  |   0.0370 |   -0.0822 |  -0.0529 |
| Confusion                 |  -0.0266 |    0.0277 |   0.0931 |
| Contempt                  |  -0.0033 |   -0.0011 |  -0.0192 |
| Craving                   |   0.0308 |    0.0045 |   0.0166 |
| Disgust                   |  -0.0001 |    0.0236 |  -0.0012 |
| Empathic pain             |   0.0268 |    0.0640 |   0.0447 |
| Entrancement              |  -0.0148 |    0.0480 |   0.0564 |
| Excitement                |  -0.0126 |   -0.1031 |   0.0190 |
| Fear                      |   0.0096 |   -0.0086 |  -0.0149 |
| Horror                    |  -0.0199 |    0.0203 |   0.0160 |
| Interest                  |  -0.0275 |    0.0625 |   0.1510 |
| Joy                       |   0.0034 |    0.0171 |   0.0096 |
| Nostalgia                 |  -0.0026 |    0.0678 |   0.1356 |
| Relief                    |  -0.0682 |   -0.0571 |   0.0479 |
| Romance                   |  -0.0061 |    0.0984 |   0.0178 |
| Sadness                   |   0.0386 |    0.0085 |  -0.0175 |
| Satisfaction              |  -0.0061 |    0.0130 |  -0.0186 |
| Sexual desire             |  -0.0150 |    0.0336 |   0.0478 |
| Surprise                  |   0.0501 |    0.0187 |   0.0425 |
| Sympathy                  |  -0.0183 |    0.0420 |   0.0403 |
| Triumph                   |  -0.0403 |    0.0011 |  -0.0105 |
| Uncomfortable             |   0.0620 |    0.0303 |   0.0660 |
| Annoyance                 |  -0.1085 |    0.1510 |   0.2200 |
| Envy                      |  -0.0226 |    0.0730 |   0.0634 |
| Guilt                     |  -0.0374 |    0.0380 |   0.0135 |

## Exp 05: K-sweep (CKA/RSA)
|    k |  CKA(b,vj) |  CKA(b,cl) |  RSA(b,vj) |  RSA(b,cl) |
|------|------------|------------|------------|------------|
|    3 |     0.1172 |     0.0955 |     0.0964 |     0.0932 |
|    5 |     0.1175 |     0.0949 |     0.1034 |     0.0969 |
|    7 |     0.1192 |     0.1005 |     0.1067 |     0.1011 |
|   10 |     0.1218 |     0.1072 |     0.1124 |     0.1077 |
|   15 |     0.1258 |     0.1087 |     0.1181 |     0.1082 |
|   20 |     0.1260 |     0.1093 |     0.1189 |     0.1081 |
|   25 |     0.1265 |     0.1094 |     0.1197 |     0.1079 |
|   27 |     0.1266 |     0.1094 |     0.1196 |     0.1076 |
|   30 |     0.1266 |     0.1096 |     0.1196 |     0.1078 |
|   34 |     0.1268 |     0.1098 |     0.1199 |     0.1079 |
|   40 |     0.1270 |     0.1101 |     0.1199 |     0.1081 |
|   50 |     0.1272 |     0.1101 |     0.1202 |     0.1083 |
|   75 |     0.1276 |     0.1104 |     0.1204 |     0.1080 |
|  100 |     0.1278 |     0.1106 |     0.1205 |     0.1080 |

## Exp 06: Procrustes
  k_used: [27.0000]
  disparity_vjepa: [0.9380]
  disparity_clip: [0.9385]
  emotion_error_vjepa: [0.0201, 0.0189, 0.0182, 0.0201, 0.0191, 0.0199, 0.0196, 0.0184, 0.0192, 0.0175, 0.0194, 0.0195, 0.0168, 0.0196, 0.0181, 0.0201, 0.0188, 0.0185, 0.0194, 0.0197, 0.0191, 0.0198, 0.0205, 0.0192, 0.0174, 0.0199, 0.0200, 0.0171, 0.0197, 0.0202, 0.0166, 0.0208, 0.0201, 0.0215]
  emotion_error_clip: [0.0202, 0.0190, 0.0183, 0.0202, 0.0191, 0.0200, 0.0197, 0.0182, 0.0192, 0.0176, 0.0193, 0.0196, 0.0169, 0.0195, 0.0181, 0.0200, 0.0189, 0.0185, 0.0195, 0.0198, 0.0192, 0.0198, 0.0205, 0.0192, 0.0175, 0.0200, 0.0202, 0.0164, 0.0197, 0.0203, 0.0163, 0.0208, 0.0200, 0.0217]

## Exp 07: Raw fMRI RSA/CKA
  cross_subj_off_diag_mean: [0.0831]
  cross_subj_off_diag_std: [0.0183]
  rsm_mean_stats: [-0.8261, 1.0000, 0.0010, 0.1753]
  rsa_raw: [0.0057, 0.0179, 0.0420, 0.0116, 0.0139, 0.0224, 0.0108, 0.0097, 0.0091, 0.0254, 0.0130, 0.0019, 0.0190, 0.0075, 0.0207, 0.0263, 0.0272, 0.0071, 0.0119, 0.0232, 0.0024, 0.0247, 0.0117, 0.0143, 0.0181, 0.0050, 0.0172, 0.0234, 0.0157, 0.0080, 0.0303, 0.0351, 0.0208, 0.0173]
  rsa_vjepa2: [0.0146, 0.0919, -0.1273, 0.1803, 0.0283, 0.0393, -0.0067, 0.0446, -0.0431, -0.0822, 0.0277, -0.0011, 0.0045, 0.0236, 0.0640, 0.0480, -0.1031, -0.0086, 0.0203, 0.0625, 0.0171, 0.0678, -0.0571, 0.0984, 0.0085, 0.0130, 0.0336, 0.0187, 0.0420, 0.0011, 0.0303, 0.1510, 0.0730, 0.0380]
  rsa_clip: [-0.0140, 0.0815, -0.0027, 0.1335, 0.0315, 0.1299, 0.0918, 0.0145, -0.0931, -0.0529, 0.0931, -0.0192, 0.0166, -0.0012, 0.0447, 0.0564, 0.0190, -0.0149, 0.0160, 0.1510, 0.0096, 0.1356, 0.0479, 0.0178, -0.0175, -0.0186, 0.0478, 0.0425, 0.0403, -0.0105, 0.0660, 0.2200, 0.0634, 0.0135]
  alignment: [0.0057, 0.0179, -0.1273, 0.0116, 0.0139, 0.0224, -0.0067, 0.0097, -0.0431, -0.0822, 0.0130, -0.0011, 0.0045, 0.0075, 0.0207, 0.0263, -0.1031, -0.0086, 0.0119, 0.0232, 0.0024, 0.0247, -0.0571, 0.0143, 0.0085, 0.0050, 0.0172, 0.0187, 0.0157, 0.0011, 0.0303, 0.0351, 0.0208, 0.0173]
  divergence: [0.0089, 0.0740, 0.1693, 0.1687, 0.0144, 0.0169, 0.0174, 0.0349, 0.0521, 0.1076, 0.0147, 0.0030, 0.0144, 0.0161, 0.0433, 0.0218, 0.1303, 0.0157, 0.0084, 0.0393, 0.0146, 0.0431, 0.0688, 0.0842, 0.0096, 0.0080, 0.0164, 0.0047, 0.0263, 0.0069, 0.0000, 0.1159, 0.0522, 0.0208]
  cka_mean_vjepa: [0.1515]
  cka_mean_clip: [0.1702]
  cka_delta: [-0.0187]
  cka_vjepa_per_subj: [0.0698, 0.0958, 0.0919, 0.0639, 0.0761]
  cka_clip_per_subj: [0.0760, 0.1101, 0.0985, 0.0784, 0.0838]
  cka_delta_per_subj: [-0.0063, -0.0143, -0.0066, -0.0145, -0.0077]
  p_val_vjepa: [0.0000]
  p_val_clip: [0.0000]
  p_val_delta: [1.0000]
  ci_vjepa: [0.1510, 0.1734]
  ci_clip: [0.1751, 0.1938]
  ci_delta: [-0.0321, -0.0128]

## Exp 10: Brain-predictable dimensions (100 PCs)
|   PC |   V-JEPA2 R² |    CLIP R² |
|------|--------------|------------|
|    1 |     0.372842 |   0.261256 |
|    2 |     0.074791 |   0.155886 |
|    3 |     0.087770 |   0.127107 |
|    4 |     0.000317 |   0.000000 |
|    5 |     0.000000 |   0.115421 |
|    6 |     0.000000 |   0.016697 |
|    7 |     0.000000 |   0.012504 |
|    8 |     0.000000 |   0.000000 |
|    9 |     0.000000 |   0.000000 |
|   10 |     0.000000 |   0.000000 |
|   11 |     0.000000 |   0.000000 |
|   12 |     0.000000 |   0.000000 |
|   13 |     0.000000 |   0.000000 |
|   14 |     0.000000 |   0.000000 |
|   15 |     0.000000 |   0.000000 |
|   16 |     0.000000 |   0.000000 |
|   17 |     0.000000 |   0.000000 |
|   18 |     0.000000 |   0.000000 |
|   19 |     0.000000 |   0.000000 |
|   20 |     0.000000 |   0.000000 |
|   21 |     0.000000 |   0.000000 |
|   22 |     0.000000 |   0.000000 |
|   23 |     0.000000 |   0.000000 |
|   24 |     0.000000 |   0.000000 |
|   25 |     0.000000 |   0.000000 |
|   26 |     0.000000 |   0.000000 |
|   27 |     0.000000 |   0.000000 |
|   28 |     0.000000 |   0.000000 |
|   29 |     0.000000 |   0.000000 |
|   30 |     0.000000 |   0.000000 |
|   31 |     0.000000 |   0.000000 |
|   32 |     0.000000 |   0.000000 |
|   33 |     0.000000 |   0.000000 |
|   34 |     0.000000 |   0.000000 |
|   35 |     0.000000 |   0.000000 |
|   36 |     0.000000 |   0.000000 |
|   37 |     0.000000 |   0.000000 |
|   38 |     0.000000 |   0.000000 |
|   39 |     0.000000 |   0.000000 |
|   40 |     0.000000 |   0.000000 |
|   41 |     0.000000 |   0.000000 |
|   42 |     0.000000 |   0.000000 |
|   43 |     0.000000 |   0.000000 |
|   44 |     0.000000 |   0.000000 |
|   45 |     0.000000 |   0.000000 |
|   46 |     0.000000 |   0.000000 |
|   47 |     0.000000 |   0.000000 |
|   48 |     0.000000 |   0.000000 |
|   49 |     0.000000 |   0.000000 |
|   50 |     0.000000 |   0.000000 |
|   51 |     0.000000 |   0.000000 |
|   52 |     0.000000 |   0.000000 |
|   53 |     0.000000 |   0.000000 |
|   54 |     0.000000 |   0.000000 |
|   55 |     0.000000 |   0.000000 |
|   56 |     0.000000 |   0.000000 |
|   57 |     0.000000 |   0.000000 |
|   58 |     0.000000 |   0.000000 |
|   59 |     0.000000 |   0.000000 |
|   60 |     0.000000 |   0.000000 |
|   61 |     0.000000 |   0.000000 |
|   62 |     0.000000 |   0.000000 |
|   63 |     0.000000 |   0.000000 |
|   64 |     0.000000 |   0.000000 |
|   65 |     0.000000 |   0.000000 |
|   66 |     0.000000 |   0.000000 |
|   67 |     0.000000 |   0.000000 |
|   68 |     0.000000 |   0.000000 |
|   69 |     0.000000 |   0.000000 |
|   70 |     0.000000 |   0.000000 |
|   71 |     0.000000 |   0.000000 |
|   72 |     0.000000 |   0.000000 |
|   73 |     0.000000 |   0.000000 |
|   74 |     0.000000 |   0.000000 |
|   75 |     0.000000 |   0.000000 |
|   76 |     0.000000 |   0.000000 |
|   77 |     0.000000 |   0.000000 |
|   78 |     0.000000 |   0.000000 |
|   79 |     0.000000 |   0.000000 |
|   80 |     0.000000 |   0.000000 |
|   81 |     0.000000 |   0.000000 |
|   82 |     0.000000 |   0.000000 |
|   83 |     0.000000 |   0.000000 |
|   84 |     0.000000 |   0.000000 |
|   85 |     0.000000 |   0.000000 |
|   86 |     0.000000 |   0.000000 |
|   87 |     0.000000 |   0.000000 |
|   88 |     0.000000 |   0.000000 |
|   89 |     0.000000 |   0.000000 |
|   90 |     0.000000 |   0.000000 |
|   91 |     0.000000 |   0.000000 |
|   92 |     0.000000 |   0.000000 |
|   93 |     0.000000 |   0.000000 |
|   94 |     0.000000 |   0.000000 |
|   95 |     0.000000 |   0.000000 |
|   96 |     0.000000 |   0.000000 |
|   97 |     0.000000 |   0.000000 |
|   98 |     0.000000 |   0.000000 |
|   99 |     0.000000 |   0.000000 |
|  100 |     0.000000 |   0.000000 |

## Exp 11: V-JEPA2 PC1-10 × 34 Emotions (Spearman r)

### PC1
| Emotion                   |        r |
|---------------------------|----------|
| Aesthetic appreciation    |  -0.3277 |
| Annoyance                 |  +0.3253 |
| Calmness                  |  -0.2880 |
| Amusement                 |  +0.2626 |
| Excitement                |  -0.2403 |
| Interest                  |  +0.2098 |
| Anxiety                   |  +0.2034 |
| Guilt                     |  +0.2004 |
| Horror                    |  +0.1972 |
| Envy                      |  +0.1759 |
| Uncomfortable             |  -0.1736 |
| Craving                   |  -0.1640 |
| Boredom                   |  -0.1457 |
| Sexual desire             |  +0.1436 |
| Surprise                  |  -0.1435 |
| Nostalgia                 |  +0.1415 |
| Romance                   |  +0.1280 |
| Entrancement              |  +0.1213 |
| Anger                     |  +0.1063 |
| Admiration                |  +0.1006 |
| Sympathy                  |  +0.0943 |
| Sadness                   |  -0.0722 |
| Disgust                   |  +0.0669 |
| Satisfaction              |  +0.0666 |
| Adoration                 |  +0.0607 |
| Triumph                   |  +0.0589 |
| Confusion                 |  +0.0524 |
| Awe                       |  +0.0462 |
| Joy                       |  +0.0445 |
| Fear                      |  -0.0285 |
| Empathic pain             |  +0.0238 |
| Relief                    |  -0.0200 |
| Contempt                  |  +0.0005 |
| Awkwardness               |  -0.0001 |
| Arousal                   |  +0.1408 |
| Valence                   |  -0.1259 |
| Dominance                 |  +0.0422 |

### PC2
| Emotion                   |        r |
|---------------------------|----------|
| Aesthetic appreciation    |  +0.3544 |
| Excitement                |  +0.3276 |
| Adoration                 |  -0.2791 |
| Relief                    |  +0.2544 |
| Romance                   |  -0.2409 |
| Amusement                 |  -0.1881 |
| Interest                  |  +0.1826 |
| Anxiety                   |  +0.1732 |
| Awkwardness               |  -0.1708 |
| Uncomfortable             |  -0.1491 |
| Empathic pain             |  -0.1243 |
| Surprise                  |  -0.1190 |
| Awe                       |  +0.1132 |
| Annoyance                 |  +0.1029 |
| Nostalgia                 |  +0.0978 |
| Confusion                 |  +0.0901 |
| Calmness                  |  +0.0875 |
| Joy                       |  -0.0866 |
| Horror                    |  +0.0861 |
| Envy                      |  -0.0804 |
| Sexual desire             |  +0.0638 |
| Sadness                   |  -0.0613 |
| Disgust                   |  -0.0573 |
| Satisfaction              |  -0.0565 |
| Contempt                  |  -0.0548 |
| Fear                      |  -0.0504 |
| Admiration                |  -0.0483 |
| Triumph                   |  +0.0417 |
| Sympathy                  |  -0.0314 |
| Craving                   |  -0.0228 |
| Anger                     |  -0.0166 |
| Entrancement              |  +0.0101 |
| Boredom                   |  +0.0059 |
| Guilt                     |  +0.0040 |
| Arousal                   |  +0.2254 |
| Valence                   |  -0.0823 |
| Dominance                 |  -0.0234 |

### PC3
| Emotion                   |        r |
|---------------------------|----------|
| Uncomfortable             |  -0.3034 |
| Empathic pain             |  -0.2384 |
| Guilt                     |  +0.2369 |
| Surprise                  |  -0.1921 |
| Amusement                 |  +0.1526 |
| Craving                   |  -0.1512 |
| Annoyance                 |  +0.1349 |
| Sexual desire             |  +0.1342 |
| Admiration                |  +0.1330 |
| Horror                    |  +0.1099 |
| Awkwardness               |  -0.1076 |
| Disgust                   |  +0.0999 |
| Satisfaction              |  +0.0963 |
| Excitement                |  +0.0949 |
| Aesthetic appreciation    |  +0.0945 |
| Anger                     |  +0.0924 |
| Anxiety                   |  +0.0922 |
| Awe                       |  +0.0892 |
| Triumph                   |  +0.0831 |
| Sympathy                  |  +0.0769 |
| Boredom                   |  +0.0709 |
| Calmness                  |  +0.0656 |
| Envy                      |  +0.0655 |
| Adoration                 |  -0.0650 |
| Interest                  |  +0.0605 |
| Sadness                   |  +0.0543 |
| Romance                   |  +0.0542 |
| Relief                    |  +0.0533 |
| Entrancement              |  +0.0515 |
| Nostalgia                 |  -0.0396 |
| Contempt                  |  +0.0280 |
| Fear                      |  -0.0228 |
| Joy                       |  +0.0202 |
| Confusion                 |  +0.0070 |
| Arousal                   |  +0.0297 |
| Valence                   |  +0.0615 |
| Dominance                 |  +0.0426 |

### PC4
| Emotion                   |        r |
|---------------------------|----------|
| Amusement                 |  +0.2186 |
| Awe                       |  -0.2167 |
| Sadness                   |  +0.1867 |
| Boredom                   |  +0.1808 |
| Aesthetic appreciation    |  -0.1591 |
| Interest                  |  -0.1500 |
| Awkwardness               |  +0.1423 |
| Anxiety                   |  -0.1310 |
| Romance                   |  +0.1215 |
| Satisfaction              |  +0.1203 |
| Contempt                  |  +0.1098 |
| Craving                   |  -0.1029 |
| Confusion                 |  +0.1028 |
| Calmness                  |  -0.0920 |
| Nostalgia                 |  -0.0858 |
| Anger                     |  +0.0635 |
| Guilt                     |  +0.0630 |
| Disgust                   |  +0.0558 |
| Excitement                |  -0.0512 |
| Sexual desire             |  -0.0511 |
| Annoyance                 |  -0.0494 |
| Triumph                   |  +0.0477 |
| Relief                    |  -0.0405 |
| Envy                      |  +0.0380 |
| Admiration                |  +0.0344 |
| Uncomfortable             |  +0.0294 |
| Surprise                  |  +0.0269 |
| Entrancement              |  -0.0267 |
| Joy                       |  -0.0241 |
| Empathic pain             |  -0.0135 |
| Adoration                 |  +0.0129 |
| Horror                    |  -0.0113 |
| Fear                      |  -0.0039 |
| Sympathy                  |  -0.0019 |
| Arousal                   |  -0.0498 |
| Valence                   |  +0.0231 |
| Dominance                 |  +0.1154 |

### PC5
| Emotion                   |        r |
|---------------------------|----------|
| Boredom                   |  -0.1683 |
| Sympathy                  |  +0.1645 |
| Surprise                  |  +0.1586 |
| Aesthetic appreciation    |  -0.1425 |
| Entrancement              |  +0.1412 |
| Nostalgia                 |  +0.1242 |
| Envy                      |  +0.1236 |
| Relief                    |  -0.1170 |
| Excitement                |  -0.1145 |
| Interest                  |  +0.0988 |
| Anxiety                   |  +0.0911 |
| Uncomfortable             |  +0.0821 |
| Sexual desire             |  +0.0776 |
| Anger                     |  +0.0719 |
| Horror                    |  +0.0611 |
| Annoyance                 |  +0.0603 |
| Guilt                     |  +0.0594 |
| Adoration                 |  +0.0577 |
| Awkwardness               |  -0.0512 |
| Amusement                 |  -0.0511 |
| Sadness                   |  -0.0468 |
| Calmness                  |  -0.0464 |
| Confusion                 |  -0.0450 |
| Admiration                |  +0.0360 |
| Empathic pain             |  +0.0340 |
| Joy                       |  +0.0257 |
| Contempt                  |  +0.0250 |
| Craving                   |  -0.0238 |
| Satisfaction              |  +0.0192 |
| Fear                      |  +0.0180 |
| Disgust                   |  +0.0169 |
| Triumph                   |  -0.0163 |
| Romance                   |  +0.0035 |
| Awe                       |  -0.0027 |
| Arousal                   |  +0.0527 |
| Valence                   |  -0.0369 |
| Dominance                 |  +0.0066 |

### PC6
| Emotion                   |        r |
|---------------------------|----------|
| Interest                  |  -0.1645 |
| Uncomfortable             |  +0.1496 |
| Anxiety                   |  -0.1474 |
| Nostalgia                 |  -0.1150 |
| Surprise                  |  +0.1059 |
| Sadness                   |  +0.0927 |
| Boredom                   |  +0.0918 |
| Awe                       |  -0.0837 |
| Awkwardness               |  +0.0793 |
| Amusement                 |  +0.0696 |
| Relief                    |  -0.0654 |
| Aesthetic appreciation    |  -0.0594 |
| Romance                   |  +0.0587 |
| Sympathy                  |  -0.0519 |
| Envy                      |  -0.0453 |
| Contempt                  |  +0.0412 |
| Sexual desire             |  -0.0395 |
| Confusion                 |  -0.0387 |
| Disgust                   |  +0.0379 |
| Adoration                 |  +0.0377 |
| Excitement                |  -0.0367 |
| Joy                       |  -0.0346 |
| Empathic pain             |  -0.0303 |
| Calmness                  |  +0.0233 |
| Admiration                |  -0.0220 |
| Triumph                   |  +0.0164 |
| Anger                     |  -0.0153 |
| Satisfaction              |  +0.0136 |
| Horror                    |  -0.0124 |
| Guilt                     |  +0.0075 |
| Annoyance                 |  -0.0064 |
| Entrancement              |  +0.0044 |
| Craving                   |  +0.0007 |
| Fear                      |  -0.0007 |
| Arousal                   |  -0.0601 |
| Valence                   |  +0.0844 |
| Dominance                 |  +0.0619 |

### PC7
| Emotion                   |        r |
|---------------------------|----------|
| Craving                   |  -0.1689 |
| Horror                    |  -0.1255 |
| Uncomfortable             |  -0.1135 |
| Triumph                   |  -0.1054 |
| Nostalgia                 |  +0.0985 |
| Aesthetic appreciation    |  -0.0903 |
| Adoration                 |  +0.0857 |
| Sympathy                  |  +0.0843 |
| Fear                      |  -0.0763 |
| Anger                     |  +0.0757 |
| Boredom                   |  -0.0711 |
| Interest                  |  +0.0679 |
| Amusement                 |  +0.0672 |
| Anxiety                   |  +0.0633 |
| Surprise                  |  -0.0617 |
| Envy                      |  +0.0608 |
| Relief                    |  -0.0532 |
| Joy                       |  +0.0485 |
| Contempt                  |  +0.0429 |
| Disgust                   |  +0.0428 |
| Awkwardness               |  -0.0417 |
| Sexual desire             |  +0.0405 |
| Awe                       |  +0.0401 |
| Guilt                     |  -0.0353 |
| Admiration                |  -0.0351 |
| Calmness                  |  -0.0326 |
| Satisfaction              |  -0.0316 |
| Empathic pain             |  +0.0305 |
| Excitement                |  -0.0297 |
| Sadness                   |  -0.0208 |
| Confusion                 |  +0.0173 |
| Annoyance                 |  +0.0169 |
| Romance                   |  +0.0150 |
| Entrancement              |  +0.0050 |
| Arousal                   |  -0.0368 |
| Valence                   |  -0.0835 |
| Dominance                 |  -0.0505 |

### PC8
| Emotion                   |        r |
|---------------------------|----------|
| Boredom                   |  -0.2177 |
| Interest                  |  +0.1789 |
| Nostalgia                 |  +0.1520 |
| Annoyance                 |  +0.1506 |
| Awe                       |  +0.1475 |
| Anxiety                   |  +0.1399 |
| Surprise                  |  -0.1383 |
| Sadness                   |  -0.1255 |
| Craving                   |  -0.1152 |
| Uncomfortable             |  -0.0968 |
| Aesthetic appreciation    |  -0.0952 |
| Anger                     |  +0.0897 |
| Envy                      |  +0.0893 |
| Sympathy                  |  +0.0849 |
| Adoration                 |  +0.0783 |
| Relief                    |  -0.0684 |
| Sexual desire             |  +0.0683 |
| Entrancement              |  +0.0644 |
| Fear                      |  -0.0619 |
| Excitement                |  -0.0610 |
| Triumph                   |  -0.0570 |
| Amusement                 |  +0.0469 |
| Empathic pain             |  +0.0467 |
| Joy                       |  +0.0442 |
| Satisfaction              |  -0.0302 |
| Guilt                     |  -0.0252 |
| Horror                    |  +0.0242 |
| Calmness                  |  -0.0182 |
| Romance                   |  +0.0169 |
| Admiration                |  -0.0165 |
| Disgust                   |  +0.0157 |
| Awkwardness               |  -0.0144 |
| Confusion                 |  +0.0100 |
| Contempt                  |  -0.0082 |
| Arousal                   |  +0.0748 |
| Valence                   |  -0.0893 |
| Dominance                 |  -0.0330 |

### PC9
| Emotion                   |        r |
|---------------------------|----------|
| Uncomfortable             |  +0.1429 |
| Interest                  |  +0.1091 |
| Anxiety                   |  +0.1045 |
| Annoyance                 |  +0.0813 |
| Sadness                   |  -0.0746 |
| Surprise                  |  +0.0741 |
| Relief                    |  -0.0740 |
| Awe                       |  -0.0685 |
| Horror                    |  +0.0674 |
| Calmness                  |  -0.0599 |
| Sexual desire             |  +0.0598 |
| Romance                   |  -0.0557 |
| Awkwardness               |  +0.0529 |
| Aesthetic appreciation    |  -0.0495 |
| Craving                   |  -0.0472 |
| Entrancement              |  +0.0471 |
| Excitement                |  -0.0471 |
| Adoration                 |  -0.0369 |
| Empathic pain             |  -0.0363 |
| Nostalgia                 |  +0.0298 |
| Fear                      |  +0.0297 |
| Admiration                |  +0.0258 |
| Satisfaction              |  -0.0231 |
| Disgust                   |  +0.0227 |
| Envy                      |  +0.0160 |
| Confusion                 |  +0.0156 |
| Guilt                     |  +0.0142 |
| Joy                       |  -0.0133 |
| Contempt                  |  -0.0097 |
| Triumph                   |  -0.0092 |
| Amusement                 |  -0.0062 |
| Boredom                   |  +0.0044 |
| Anger                     |  +0.0009 |
| Sympathy                  |  -0.0003 |
| Arousal                   |  +0.0204 |
| Valence                   |  -0.0497 |
| Dominance                 |  -0.0043 |

### PC10
| Emotion                   |        r |
|---------------------------|----------|
| Uncomfortable             |  +0.1310 |
| Amusement                 |  -0.1208 |
| Excitement                |  +0.1122 |
| Romance                   |  -0.0976 |
| Sadness                   |  -0.0976 |
| Aesthetic appreciation    |  +0.0933 |
| Surprise                  |  +0.0930 |
| Craving                   |  +0.0911 |
| Relief                    |  +0.0903 |
| Adoration                 |  -0.0744 |
| Sympathy                  |  -0.0663 |
| Annoyance                 |  -0.0660 |
| Disgust                   |  -0.0581 |
| Satisfaction              |  -0.0519 |
| Interest                  |  -0.0494 |
| Contempt                  |  -0.0416 |
| Fear                      |  +0.0403 |
| Anger                     |  -0.0382 |
| Nostalgia                 |  -0.0373 |
| Awe                       |  -0.0366 |
| Anxiety                   |  -0.0316 |
| Admiration                |  -0.0292 |
| Entrancement              |  -0.0289 |
| Triumph                   |  +0.0260 |
| Horror                    |  +0.0228 |
| Awkwardness               |  +0.0226 |
| Envy                      |  -0.0225 |
| Boredom                   |  -0.0199 |
| Sexual desire             |  -0.0183 |
| Joy                       |  +0.0158 |
| Calmness                  |  -0.0115 |
| Confusion                 |  -0.0083 |
| Empathic pain             |  -0.0049 |
| Guilt                     |  +0.0005 |
| Arousal                   |  +0.1073 |
| Valence                   |  +0.0121 |
| Dominance                 |  +0.0619 |

## Exp 17: Brain-pred vs Full decoding (36 targets)
| Target                    |  Brain-pred |     Full |        Δ |
|---------------------------|-------------|----------|----------|
| Admiration                |      0.0235 |   0.0027 |  -0.0208 |
| Adoration                 |      0.0805 |   0.3597 |  +0.2792 |
| Aesthetic appreciation    |      0.3231 |   0.5509 |  +0.2278 |
| Amusement                 |      0.1159 |   0.3219 |  +0.2060 |
| Anger                     |      0.0118 |   0.0671 |  +0.0553 |
| Anxiety                   |      0.0611 |   0.2394 |  +0.1783 |
| Awe                       |      0.0222 |   0.2538 |  +0.2316 |
| Awkwardness               |      0.0308 |   0.0839 |  +0.0531 |
| Boredom                   |      0.0196 |   0.1228 |  +0.1032 |
| Calmness                  |      0.1361 |   0.3176 |  +0.1815 |
| Confusion                 |      0.0000 |   0.0095 |  +0.0095 |
| Contempt                  |      0.0000 |   0.0208 |  +0.0208 |
| Craving                   |      0.0166 |   0.3643 |  +0.3477 |
| Disgust                   |      0.0088 |   0.0000 |  -0.0088 |
| Empathic pain             |      0.0741 |   0.1823 |  +0.1082 |
| Entrancement              |      0.0024 |   0.0066 |  +0.0042 |
| Excitement                |      0.2001 |   0.3955 |  +0.1954 |
| Fear                      |      0.0000 |   0.0000 |  +0.0000 |
| Horror                    |      0.0570 |   0.1447 |  +0.0877 |
| Interest                  |      0.0598 |   0.2667 |  +0.2069 |
| Joy                       |      0.0028 |   0.0000 |  -0.0028 |
| Nostalgia                 |      0.0167 |   0.1561 |  +0.1394 |
| Relief                    |      0.0576 |   0.1552 |  +0.0976 |
| Romance                   |      0.0793 |   0.2235 |  +0.1442 |
| Sadness                   |      0.0094 |   0.1975 |  +0.1881 |
| Satisfaction              |      0.0071 |   0.0000 |  -0.0071 |
| Sexual desire             |      0.0313 |   0.1221 |  +0.0908 |
| Surprise                  |      0.0450 |   0.2763 |  +0.2313 |
| Sympathy                  |      0.0059 |   0.0440 |  +0.0381 |
| Triumph                   |      0.0128 |   0.0465 |  +0.0337 |
| Uncomfortable             |      0.1715 |   0.4990 |  +0.3275 |
| Annoyance                 |      0.1057 |   0.1828 |  +0.0771 |
| Envy                      |      0.0293 |   0.0241 |  -0.0053 |
| Guilt                     |      0.0518 |   0.1517 |  +0.0999 |
| Arousal                   |      0.0651 |   0.0889 |  +0.0238 |
| Valence                   |      0.0112 |   0.1817 |  +0.1705 |
| Cat mean                  |      0.0550 |   0.1703 | |
| AV mean                   |      0.0382 |   0.1353 | |
| Cat/VA ratio              |       1.441 |    1.258 | |

## Exp 18: Subject-wise (6 rows × 36 targets)
| Target                    |   Mean |     S1 |     S2 |     S3 |     S4 |     S5 |
|---------------------------|--------|--------|--------|--------|--------|--------|
| Admiration                | 0.0235 | 0.0000 | 0.0221 | 0.0221 | 0.0000 | 0.0000 |
| Adoration                 | 0.0805 | 0.0006 | 0.0085 | 0.0085 | 0.0006 | 0.0006 |
| Aesthetic appreciation    | 0.3231 | 0.1368 | 0.1646 | 0.1646 | 0.1368 | 0.1368 |
| Amusement                 | 0.1159 | 0.0510 | 0.0673 | 0.0673 | 0.0510 | 0.0510 |
| Anger                     | 0.0118 | 0.0081 | 0.0118 | 0.0118 | 0.0081 | 0.0081 |
| Anxiety                   | 0.0611 | 0.0333 | 0.0387 | 0.0387 | 0.0333 | 0.0333 |
| Awe                       | 0.0222 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Awkwardness               | 0.0308 | 0.0000 | 0.0025 | 0.0025 | 0.0000 | 0.0000 |
| Boredom                   | 0.0196 | 0.0148 | 0.0181 | 0.0181 | 0.0148 | 0.0148 |
| Calmness                  | 0.1361 | 0.0954 | 0.1135 | 0.1135 | 0.0954 | 0.0954 |
| Confusion                 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Contempt                  | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Craving                   | 0.0166 | 0.0100 | 0.0169 | 0.0169 | 0.0100 | 0.0100 |
| Disgust                   | 0.0088 | 0.0000 | 0.0056 | 0.0056 | 0.0000 | 0.0000 |
| Empathic pain             | 0.0741 | 0.0000 | 0.0610 | 0.0610 | 0.0000 | 0.0000 |
| Entrancement              | 0.0024 | 0.0022 | 0.0030 | 0.0030 | 0.0022 | 0.0022 |
| Excitement                | 0.2001 | 0.0619 | 0.0682 | 0.0682 | 0.0619 | 0.0619 |
| Fear                      | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Horror                    | 0.0570 | 0.0341 | 0.0454 | 0.0454 | 0.0341 | 0.0341 |
| Interest                  | 0.0598 | 0.0321 | 0.0364 | 0.0364 | 0.0321 | 0.0321 |
| Joy                       | 0.0028 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Nostalgia                 | 0.0167 | 0.0033 | 0.0061 | 0.0061 | 0.0033 | 0.0033 |
| Relief                    | 0.0576 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Romance                   | 0.0793 | 0.0135 | 0.0129 | 0.0129 | 0.0135 | 0.0135 |
| Sadness                   | 0.0094 | 0.0056 | 0.0080 | 0.0080 | 0.0056 | 0.0056 |
| Satisfaction              | 0.0071 | 0.0000 | 0.0041 | 0.0041 | 0.0000 | 0.0000 |
| Sexual desire             | 0.0313 | 0.0113 | 0.0241 | 0.0241 | 0.0113 | 0.0113 |
| Surprise                  | 0.0450 | 0.0084 | 0.0321 | 0.0321 | 0.0084 | 0.0084 |
| Sympathy                  | 0.0059 | 0.0008 | 0.0043 | 0.0043 | 0.0008 | 0.0008 |
| Triumph                   | 0.0128 | 0.0029 | 0.0117 | 0.0117 | 0.0029 | 0.0029 |
| Uncomfortable             | 0.1715 | 0.0328 | 0.1526 | 0.1526 | 0.0328 | 0.0328 |
| Annoyance                 | 0.1057 | 0.0770 | 0.1009 | 0.1009 | 0.0770 | 0.0770 |
| Envy                      | 0.0293 | 0.0189 | 0.0225 | 0.0225 | 0.0189 | 0.0189 |
| Guilt                     | 0.0518 | 0.0149 | 0.0528 | 0.0528 | 0.0149 | 0.0149 |
| Arousal                   | 0.0651 | 0.0161 | 0.0164 | 0.0164 | 0.0161 | 0.0161 |
| Valence                   | 0.0112 | 0.0040 | 0.0084 | 0.0084 | 0.0040 | 0.0040 |

## Exp 19: Permutation Test (100 PCs)
n_perm=1000
|   PC |          R² |       p |  q(FDR) |  Sig |
|------|-------------|---------|---------|------|
|    1 |    0.372855 |  0.0000 |  0.0000 |    Y |
|    2 |    0.074784 |  0.0000 |  0.0000 |    Y |
|    3 |    0.087835 |  0.0000 |  0.0000 |    Y |
|    4 |    0.000251 |  0.0000 |  0.0000 |    Y |
|    5 |    0.000000 |  1.0000 |  1.0000 |    N |
|    6 |    0.000000 |  1.0000 |  1.0000 |    N |
|    7 |    0.000000 |  1.0000 |  1.0000 |    N |
|    8 |    0.000000 |  1.0000 |  1.0000 |    N |
|    9 |    0.000000 |  1.0000 |  1.0000 |    N |
|   10 |    0.000000 |  1.0000 |  1.0000 |    N |
|   11 |    0.000000 |  1.0000 |  1.0000 |    N |
|   12 |    0.000000 |  1.0000 |  1.0000 |    N |
|   13 |    0.000000 |  1.0000 |  1.0000 |    N |
|   14 |    0.000000 |  1.0000 |  1.0000 |    N |
|   15 |    0.000000 |  1.0000 |  1.0000 |    N |
|   16 |    0.000000 |  1.0000 |  1.0000 |    N |
|   17 |    0.000000 |  1.0000 |  1.0000 |    N |
|   18 |    0.000000 |  1.0000 |  1.0000 |    N |
|   19 |    0.000000 |  1.0000 |  1.0000 |    N |
|   20 |    0.000000 |  1.0000 |  1.0000 |    N |
|   21 |    0.000000 |  1.0000 |  1.0000 |    N |
|   22 |    0.000000 |  1.0000 |  1.0000 |    N |
|   23 |    0.000000 |  1.0000 |  1.0000 |    N |
|   24 |    0.000000 |  1.0000 |  1.0000 |    N |
|   25 |    0.000000 |  1.0000 |  1.0000 |    N |
|   26 |    0.000000 |  1.0000 |  1.0000 |    N |
|   27 |    0.000000 |  1.0000 |  1.0000 |    N |
|   28 |    0.000000 |  1.0000 |  1.0000 |    N |
|   29 |    0.000000 |  1.0000 |  1.0000 |    N |
|   30 |    0.000000 |  1.0000 |  1.0000 |    N |
|   31 |    0.000000 |  1.0000 |  1.0000 |    N |
|   32 |    0.000000 |  1.0000 |  1.0000 |    N |
|   33 |    0.000000 |  1.0000 |  1.0000 |    N |
|   34 |    0.000000 |  1.0000 |  1.0000 |    N |
|   35 |    0.000000 |  1.0000 |  1.0000 |    N |
|   36 |    0.000000 |  1.0000 |  1.0000 |    N |
|   37 |    0.000000 |  1.0000 |  1.0000 |    N |
|   38 |    0.000000 |  1.0000 |  1.0000 |    N |
|   39 |    0.000000 |  1.0000 |  1.0000 |    N |
|   40 |    0.000000 |  1.0000 |  1.0000 |    N |
|   41 |    0.000000 |  1.0000 |  1.0000 |    N |
|   42 |    0.000000 |  1.0000 |  1.0000 |    N |
|   43 |    0.000000 |  1.0000 |  1.0000 |    N |
|   44 |    0.000000 |  1.0000 |  1.0000 |    N |
|   45 |    0.000000 |  1.0000 |  1.0000 |    N |
|   46 |    0.000000 |  1.0000 |  1.0000 |    N |
|   47 |    0.000000 |  1.0000 |  1.0000 |    N |
|   48 |    0.000000 |  1.0000 |  1.0000 |    N |
|   49 |    0.000000 |  1.0000 |  1.0000 |    N |
|   50 |    0.000000 |  1.0000 |  1.0000 |    N |
|   51 |    0.000000 |  1.0000 |  1.0000 |    N |
|   52 |    0.000000 |  1.0000 |  1.0000 |    N |
|   53 |    0.000000 |  1.0000 |  1.0000 |    N |
|   54 |    0.000000 |  1.0000 |  1.0000 |    N |
|   55 |    0.000000 |  1.0000 |  1.0000 |    N |
|   56 |    0.000000 |  1.0000 |  1.0000 |    N |
|   57 |    0.000000 |  1.0000 |  1.0000 |    N |
|   58 |    0.000000 |  1.0000 |  1.0000 |    N |
|   59 |    0.000000 |  1.0000 |  1.0000 |    N |
|   60 |    0.000000 |  1.0000 |  1.0000 |    N |
|   61 |    0.000000 |  1.0000 |  1.0000 |    N |
|   62 |    0.000000 |  1.0000 |  1.0000 |    N |
|   63 |    0.000000 |  1.0000 |  1.0000 |    N |
|   64 |    0.000000 |  1.0000 |  1.0000 |    N |
|   65 |    0.000000 |  1.0000 |  1.0000 |    N |
|   66 |    0.000000 |  1.0000 |  1.0000 |    N |
|   67 |    0.000000 |  1.0000 |  1.0000 |    N |
|   68 |    0.000000 |  1.0000 |  1.0000 |    N |
|   69 |    0.000000 |  1.0000 |  1.0000 |    N |
|   70 |    0.000000 |  1.0000 |  1.0000 |    N |
|   71 |    0.000000 |  1.0000 |  1.0000 |    N |
|   72 |    0.000000 |  1.0000 |  1.0000 |    N |
|   73 |    0.000000 |  1.0000 |  1.0000 |    N |
|   74 |    0.000000 |  1.0000 |  1.0000 |    N |
|   75 |    0.000000 |  1.0000 |  1.0000 |    N |
|   76 |    0.000000 |  1.0000 |  1.0000 |    N |
|   77 |    0.000000 |  1.0000 |  1.0000 |    N |
|   78 |    0.000000 |  1.0000 |  1.0000 |    N |
|   79 |    0.000000 |  1.0000 |  1.0000 |    N |
|   80 |    0.000000 |  1.0000 |  1.0000 |    N |
|   81 |    0.000000 |  1.0000 |  1.0000 |    N |
|   82 |    0.000000 |  1.0000 |  1.0000 |    N |
|   83 |    0.000000 |  1.0000 |  1.0000 |    N |
|   84 |    0.000000 |  1.0000 |  1.0000 |    N |
|   85 |    0.000000 |  1.0000 |  1.0000 |    N |
|   86 |    0.000000 |  1.0000 |  1.0000 |    N |
|   87 |    0.000000 |  1.0000 |  1.0000 |    N |
|   88 |    0.000000 |  1.0000 |  1.0000 |    N |
|   89 |    0.000000 |  1.0000 |  1.0000 |    N |
|   90 |    0.000000 |  1.0000 |  1.0000 |    N |
|   91 |    0.000000 |  1.0000 |  1.0000 |    N |
|   92 |    0.000000 |  1.0000 |  1.0000 |    N |
|   93 |    0.000000 |  1.0000 |  1.0000 |    N |
|   94 |    0.000000 |  1.0000 |  1.0000 |    N |
|   95 |    0.000000 |  1.0000 |  1.0000 |    N |
|   96 |    0.000000 |  1.0000 |  1.0000 |    N |
|   97 |    0.000000 |  1.0000 |  1.0000 |    N |
|   98 |    0.000000 |  1.0000 |  1.0000 |    N |
|   99 |    0.000000 |  1.0000 |  1.0000 |    N |
|  100 |    0.000000 |  1.0000 |  1.0000 |    N |

## Exp 21: CCA (PCA100→CCA100, permutation 1000)
n_pca=100, n_cc=100, n_perm=1000

|  CC |      r |      q |  S |                    Top1 |     r1 |                 Top2 |     r2 |                 Top3 |     r3 |      A |      V |
|-----|--------|--------|----|-------------------------|--------|----------------------|--------|----------------------|--------|--------|--------|
|   1 | 0.7737 | 0.0000 |  Y | Annoyance               | +0.456 | Interest             | +0.337 | Anxiety              | +0.335 | +0.237 | -0.151 |
|   2 | 0.6792 | 0.0000 |  Y | Aesthetic appreciation  | -0.437 | Excitement           | -0.368 | Relief               | -0.297 | -0.111 | +0.018 |
|   3 | 0.6492 | 0.0000 |  Y | Interest                | -0.184 | Empathic pain        | +0.180 | Anxiety              | -0.171 | +0.012 | +0.025 |
|   4 | 0.6082 | 0.0000 |  Y | Uncomfortable           | -0.292 | Sadness              | +0.220 | Surprise             | -0.204 | -0.120 | +0.023 |
|   5 | 0.5715 | 0.0000 |  Y | Aesthetic appreciation  | -0.187 | Amusement            | +0.181 | Excitement           | -0.134 | -0.078 | +0.009 |
|   6 | 0.5217 | 0.0000 |  Y | Uncomfortable           | +0.327 | Awe                  | -0.266 | Adoration            | -0.241 | +0.021 | -0.190 |
|   7 | 0.4952 | 0.0000 |  Y | Uncomfortable           | +0.177 | Nostalgia            | -0.175 | Sympathy             | -0.143 | +0.023 | +0.169 |
|   8 | 0.4941 | 0.0000 |  Y | Adoration               | -0.268 | Awe                  | -0.158 | Guilt                | +0.145 | +0.080 | -0.068 |
|   9 | 0.4604 | 0.0000 |  Y | Empathic pain           | +0.197 | Nostalgia            | +0.184 | Sympathy             | +0.163 | -0.037 | -0.166 |
|  10 | 0.4574 | 0.0000 |  Y | Uncomfortable           | +0.162 | Surprise             | +0.144 | Aesthetic appreciation | +0.113 | -0.010 | +0.099 |
|  11 | 0.4385 | 0.0000 |  Y | Amusement               | -0.139 | Adoration            | -0.126 | Romance              | -0.094 | +0.001 | -0.031 |
|  12 | 0.4280 | 0.0000 |  Y | Awe                     | +0.177 | Aesthetic appreciation | +0.167 | Interest             | -0.141 | -0.004 | +0.196 |
|  13 | 0.4151 | 0.0000 |  Y | Confusion               | -0.155 | Adoration            | +0.154 | Romance              | +0.118 | -0.047 | +0.137 |
|  14 | 0.4008 | 0.0000 |  Y | Uncomfortable           | +0.181 | Contempt             | -0.100 | Annoyance            | +0.085 | +0.060 | -0.002 |
|  15 | 0.3895 | 0.0000 |  Y | Craving                 | +0.106 | Surprise             | +0.097 | Interest             | -0.088 | +0.035 | +0.131 |
|  16 | 0.3680 | 0.0000 |  Y | Interest                | -0.121 | Nostalgia            | -0.118 | Relief               | +0.116 | +0.041 | +0.124 |
|  17 | 0.3610 | 0.0000 |  Y | Annoyance               | +0.105 | Empathic pain        | +0.091 | Surprise             | -0.067 | -0.046 | -0.078 |
|  18 | 0.3573 | 0.0000 |  Y | Awe                     | +0.139 | Uncomfortable        | -0.113 | Adoration            | +0.113 | +0.051 | +0.015 |
|  19 | 0.3484 | 0.0000 |  Y | Adoration               | -0.073 | Sadness              | +0.068 | Awe                  | -0.055 | -0.038 | -0.019 |
|  20 | 0.3331 | 0.0000 |  Y | Annoyance               | -0.059 | Interest             | -0.055 | Aesthetic appreciation | +0.054 | -0.038 | +0.016 |
|  21 | 0.3360 | 0.0000 |  Y | Empathic pain           | +0.056 | Horror               | -0.048 | Contempt             | +0.047 | -0.044 | -0.020 |
|  22 | 0.3283 | 0.0000 |  Y | Empathic pain           | -0.065 | Uncomfortable        | -0.063 | Aesthetic appreciation | +0.060 | +0.054 | -0.022 |
|  23 | 0.3247 | 0.0000 |  Y | Awe                     | -0.084 | Craving              | +0.071 | Interest             | -0.056 | +0.002 | -0.012 |
|  24 | 0.3178 | 0.0000 |  Y | Boredom                 | -0.075 | Romance              | +0.045 | Empathic pain        | +0.040 | +0.017 | -0.003 |
|  25 | 0.3135 | 0.0000 |  Y | Craving                 | +0.133 | Awe                  | -0.105 | Adoration            | -0.077 | +0.017 | +0.000 |
|  26 | 0.3069 | 0.0000 |  Y | Craving                 | +0.114 | Surprise             | +0.095 | Confusion            | -0.064 | -0.016 | +0.036 |
|  27 | 0.3065 | 0.0000 |  Y | Anger                   | -0.072 | Craving              | -0.071 | Sadness              | -0.061 | +0.018 | +0.028 |
|  28 | 0.2967 | 0.0000 |  Y | Aesthetic appreciation  | -0.070 | Anger                | +0.063 | Surprise             | -0.059 | +0.016 | -0.010 |
|  29 | 0.2955 | 0.0000 |  Y | Excitement              | +0.083 | Aesthetic appreciation | +0.071 | Adoration            | -0.064 | +0.025 | -0.028 |
|  30 | 0.2870 | 0.0000 |  Y | Uncomfortable           | +0.073 | Relief               | -0.042 | Boredom              | -0.035 | +0.025 | -0.003 |
|  31 | 0.2775 | 0.0000 |  Y | Amusement               | +0.133 | Interest             | -0.116 | Sexual desire        | -0.091 | -0.056 | +0.044 |
|  32 | 0.2746 | 0.0000 |  Y | Surprise                | -0.062 | Uncomfortable        | +0.056 | Excitement           | +0.044 | +0.028 | -0.038 |
|  33 | 0.2730 | 0.0000 |  Y | Fear                    | +0.078 | Amusement            | -0.068 | Adoration            | -0.062 | -0.000 | -0.030 |
|  34 | 0.2679 | 0.0000 |  Y | Craving                 | +0.068 | Amusement            | -0.056 | Nostalgia            | -0.056 | +0.013 | +0.055 |
|  35 | 0.2613 | 0.0000 |  Y | Adoration               | +0.096 | Awe                  | +0.075 | Aesthetic appreciation | -0.065 | +0.045 | +0.035 |
|  36 | 0.2557 | 0.0000 |  Y | Awe                     | -0.075 | Romance              | -0.061 | Uncomfortable        | +0.050 | +0.002 | -0.057 |
|  37 | 0.2490 | 0.0000 |  Y | Awe                     | +0.096 | Craving              | -0.086 | Adoration            | +0.075 | +0.051 | +0.023 |
|  38 | 0.2427 | 0.0000 |  Y | Entrancement            | +0.059 | Sadness              | -0.051 | Excitement           | +0.045 | +0.035 | +0.001 |
|  39 | 0.2364 | 0.0000 |  Y | Empathic pain           | +0.050 | Triumph              | +0.047 | Confusion            | -0.046 | -0.019 | +0.015 |
|  40 | 0.2287 | 0.0000 |  Y | Nostalgia               | -0.090 | Anxiety              | -0.085 | Boredom              | +0.081 | +0.037 | +0.074 |
|  41 | 0.2312 | 0.0000 |  Y | Awe                     | +0.099 | Craving              | -0.074 | Entrancement         | -0.066 | +0.013 | +0.041 |
|  42 | 0.2235 | 0.0000 |  Y | Anxiety                 | -0.068 | Romance              | +0.067 | Uncomfortable        | -0.066 | -0.024 | +0.041 |
|  43 | 0.2189 | 0.0000 |  Y | Guilt                   | -0.039 | Contempt             | +0.039 | Excitement           | -0.033 | -0.018 | -0.023 |
|  44 | 0.2164 | 0.0000 |  Y | Relief                  | -0.087 | Horror               | -0.084 | Surprise             | -0.081 | -0.038 | -0.030 |
|  45 | 0.2144 | 0.0000 |  Y | Awkwardness             | +0.049 | Aesthetic appreciation | +0.044 | Contempt             | -0.040 | -0.030 | -0.022 |
|  46 | 0.2072 | 0.0000 |  Y | Calmness                | -0.068 | Craving              | +0.067 | Romance              | -0.063 | +0.016 | -0.059 |
|  47 | 0.2061 | 0.0000 |  Y | Surprise                | -0.080 | Horror               | -0.053 | Uncomfortable        | -0.052 | -0.066 | -0.020 |
|  48 | 0.2018 | 0.0000 |  Y | Anger                   | -0.055 | Disgust              | -0.052 | Uncomfortable        | -0.051 | -0.005 | +0.035 |
|  49 | 0.1951 | 0.0000 |  Y | Amusement               | +0.073 | Craving              | -0.066 | Romance              | +0.051 | -0.035 | -0.003 |
|  50 | 0.1908 | 0.0000 |  Y | Amusement               | -0.066 | Surprise             | +0.065 | Craving              | +0.058 | +0.021 | +0.012 |
|  51 | 0.1869 | 0.0000 |  Y | Adoration               | +0.120 | Amusement            | +0.073 | Surprise             | -0.065 | +0.010 | +0.069 |
|  52 | 0.1867 | 0.0000 |  Y | Romance                 | +0.057 | Surprise             | -0.056 | Uncomfortable        | -0.056 | -0.099 | +0.012 |
|  53 | 0.1790 | 0.0000 |  Y | Craving                 | -0.085 | Awe                  | +0.062 | Horror               | +0.053 | +0.022 | +0.022 |
|  54 | 0.1762 | 0.0000 |  Y | Craving                 | -0.082 | Sadness              | +0.063 | Amusement            | +0.059 | -0.016 | +0.011 |
|  55 | 0.1681 | 0.0000 |  Y | Horror                  | +0.068 | Aesthetic appreciation | +0.060 | Empathic pain        | -0.060 | +0.055 | +0.025 |
|  56 | 0.1660 | 0.0000 |  Y | Uncomfortable           | -0.059 | Romance              | +0.047 | Envy                 | -0.042 | +0.026 | +0.026 |
|  57 | 0.1641 | 0.0000 |  Y | Awkwardness             | +0.057 | Satisfaction         | +0.055 | Boredom              | +0.054 | -0.021 | -0.004 |
|  58 | 0.1620 | 0.0000 |  Y | Sadness                 | +0.062 | Sexual desire        | +0.060 | Uncomfortable        | -0.048 | +0.011 | +0.024 |
|  59 | 0.1577 | 0.0000 |  Y | Horror                  | -0.077 | Interest             | -0.064 | Adoration            | +0.055 | -0.056 | +0.030 |
|  60 | 0.1550 | 0.0000 |  Y | Surprise                | -0.059 | Interest             | +0.051 | Aesthetic appreciation | -0.050 | -0.019 | -0.034 |
|  61 | 0.1539 | 0.0000 |  Y | Sympathy                | +0.099 | Envy                 | +0.089 | Craving              | +0.087 | +0.003 | -0.076 |
|  62 | 0.1463 | 0.0000 |  Y | Guilt                   | +0.055 | Aesthetic appreciation | -0.052 | Amusement            | +0.049 | -0.005 | +0.004 |
|  63 | 0.1403 | 0.0000 |  Y | Fear                    | +0.056 | Anxiety              | -0.056 | Nostalgia            | -0.055 | -0.006 | +0.055 |
|  64 | 0.1352 | 0.0013 |  Y | Uncomfortable           | -0.100 | Craving              | -0.078 | Awe                  | +0.071 | +0.003 | +0.022 |
|  65 | 0.1295 | 0.0063 |  Y | Aesthetic appreciation  | +0.072 | Empathic pain        | -0.053 | Sympathy             | -0.052 | +0.040 | +0.044 |
|  66 | 0.1271 | 0.0000 |  Y | Sadness                 | +0.047 | Surprise             | -0.047 | Confusion            | -0.042 | +0.002 | -0.007 |
|  67 | 0.1251 | 0.0000 |  Y | Contempt                | +0.048 | Amusement            | +0.039 | Empathic pain        | +0.031 | -0.031 | +0.001 |
|  68 | 0.1234 | 0.0000 |  Y | Craving                 | +0.061 | Awe                  | +0.055 | Adoration            | +0.054 | +0.008 | +0.053 |
|  69 | 0.1205 | 0.0000 |  Y | Craving                 | -0.058 | Boredom              | +0.046 | Amusement            | -0.036 | -0.023 | -0.033 |
|  70 | 0.1191 | 0.0000 |  Y | Surprise                | +0.070 | Entrancement         | +0.062 | Awe                  | -0.059 | -0.017 | -0.012 |
|  71 | 0.1152 | 0.0000 |  Y | Calmness                | +0.061 | Craving              | -0.060 | Sympathy             | +0.057 | -0.026 | -0.027 |
|  72 | 0.1099 | 0.0000 |  Y | Excitement              | +0.054 | Confusion            | -0.049 | Uncomfortable        | +0.047 | +0.027 | -0.004 |
|  73 | 0.1045 | 0.0000 |  Y | Surprise                | +0.104 | Triumph              | -0.051 | Amusement            | -0.047 | +0.011 | -0.035 |
|  74 | 0.1038 | 0.0000 |  Y | Adoration               | +0.120 | Romance              | +0.080 | Aesthetic appreciation | -0.069 | -0.012 | +0.030 |
|  75 | 0.1015 | 0.0000 |  Y | Excitement              | -0.073 | Adoration            | +0.066 | Envy                 | +0.065 | -0.015 | -0.016 |
|  76 | 0.0929 | 0.0000 |  Y | Aesthetic appreciation  | +0.070 | Anger                | +0.053 | Awkwardness          | -0.044 | +0.016 | +0.003 |
|  77 | 0.0893 | 0.0000 |  Y | Sadness                 | +0.080 | Guilt                | +0.075 | Uncomfortable        | -0.065 | -0.002 | +0.046 |
|  78 | 0.0822 | 0.0098 |  Y | Uncomfortable           | +0.077 | Surprise             | +0.052 | Sadness              | -0.042 | -0.016 | -0.030 |
|  79 | 0.0800 | 0.0013 |  Y | Calmness                | +0.084 | Sexual desire        | -0.049 | Surprise             | -0.047 | -0.025 | +0.034 |
|  80 | 0.0773 | 0.0000 |  Y | Boredom                 | +0.052 | Awe                  | -0.047 | Fear                 | +0.044 | -0.024 | -0.002 |
|  81 | 0.0722 | 0.0074 |  Y | Craving                 | +0.058 | Romance              | +0.056 | Awe                  | +0.048 | +0.032 | +0.045 |
|  82 | 0.0706 | 0.0000 |  Y | Amusement               | -0.062 | Interest             | +0.057 | Boredom              | -0.055 | +0.050 | -0.028 |
|  83 | 0.0628 | 0.0789 |  N | Adoration               | -0.083 | Romance              | -0.082 | Sexual desire        | +0.070 | +0.027 | -0.032 |
|  84 | 0.0606 | 0.0291 |  Y | Surprise                | -0.097 | Awkwardness          | +0.046 | Sexual desire        | +0.038 | -0.014 | +0.013 |
|  85 | 0.0575 | 0.0259 |  Y | Craving                 | +0.064 | Adoration            | +0.061 | Interest             | -0.055 | +0.013 | +0.064 |
|  86 | 0.0530 | 0.0584 |  N | Uncomfortable           | -0.069 | Confusion            | +0.057 | Craving              | -0.052 | -0.011 | +0.011 |
|  87 | 0.0507 | 0.0226 |  Y | Adoration               | +0.077 | Anger                | -0.052 | Empathic pain        | -0.048 | -0.011 | +0.060 |
|  88 | 0.0476 | 0.0157 |  Y | Uncomfortable           | -0.066 | Amusement            | -0.054 | Contempt             | +0.050 | -0.029 | -0.032 |
|  89 | 0.0431 | 0.0341 |  Y | Anxiety                 | -0.045 | Interest             | -0.041 | Envy                 | -0.040 | +0.009 | +0.024 |
|  90 | 0.0366 | 0.2723 |  N | Adoration               | -0.055 | Sadness              | -0.053 | Horror               | +0.046 | +0.016 | -0.031 |
|  91 | 0.0339 | 0.1923 |  N | Confusion               | -0.055 | Contempt             | -0.051 | Calmness             | +0.045 | +0.018 | +0.042 |
|  92 | 0.0325 | 0.0341 |  Y | Excitement              | -0.053 | Sympathy             | +0.043 | Empathic pain        | +0.043 | -0.007 | -0.011 |
|  93 | 0.0259 | 0.3469 |  N | Sadness                 | -0.057 | Horror               | -0.054 | Nostalgia            | +0.052 | -0.037 | -0.033 |
|  94 | 0.0235 | 0.2054 |  N | Surprise                | +0.057 | Confusion            | -0.034 | Calmness             | +0.033 | +0.022 | +0.018 |
|  95 | 0.0182 | 0.4592 |  N | Adoration               | +0.055 | Satisfaction         | -0.044 | Amusement            | +0.039 | -0.003 | -0.018 |
|  96 | 0.0146 | 0.4909 |  N | Uncomfortable           | +0.047 | Satisfaction         | -0.039 | Empathic pain        | -0.036 | +0.037 | +0.015 |
|  97 | 0.0114 | 0.4592 |  N | Guilt                   | +0.059 | Interest             | -0.058 | Aesthetic appreciation | -0.053 | -0.050 | -0.002 |
|  98 | 0.0061 | 0.8360 |  N | Guilt                   | -0.073 | Awkwardness          | -0.046 | Aesthetic appreciation | +0.041 | +0.007 | -0.019 |
|  99 | 0.0060 | 0.1989 |  N | Craving                 | +0.048 | Boredom              | +0.039 | Relief               | -0.032 | -0.029 | +0.019 |
| 100 | 0.0020 | 0.2832 |  N | Sadness                 | +0.074 | Romance              | +0.055 | Aesthetic appreciation | -0.053 | +0.013 | -0.028 |

Subject-level (CC1-10):
|  CC |      S1 |      S2 |      S3 |      S4 |      S5 |    Mean |     SD |
|-----|---------|---------|---------|---------|---------|---------|--------|
|   1 | 0.7369 | 0.7144 | 0.7056 | 0.7321 | 0.7082 | 0.7194 | 0.0127 |
|   2 | 0.6109 | 0.6221 | 0.6182 | 0.5967 | 0.5555 | 0.6007 | 0.0242 |
|   3 | 0.5687 | 0.6133 | 0.5531 | 0.5639 | 0.5301 | 0.5658 | 0.0272 |
|   4 | 0.5357 | 0.5245 | 0.5386 | 0.5270 | 0.4931 | 0.5238 | 0.0162 |
|   5 | 0.5182 | 0.4839 | 0.4943 | 0.5001 | 0.4520 | 0.4897 | 0.0219 |
|   6 | 0.4603 | 0.4619 | 0.4798 | 0.4750 | 0.4483 | 0.4651 | 0.0112 |
|   7 | 0.4428 | 0.4465 | 0.4720 | 0.4433 | 0.4308 | 0.4471 | 0.0136 |
|   8 | 0.4369 | 0.4405 | 0.4218 | 0.4267 | 0.4178 | 0.4288 | 0.0087 |
|   9 | 0.4238 | 0.4171 | 0.4136 | 0.4152 | 0.4089 | 0.4157 | 0.0048 |
|  10 | 0.4080 | 0.4013 | 0.3959 | 0.3981 | 0.4025 | 0.4012 | 0.0041 |

Decoding comparison (36 targets each):

### r2_cca_sig
| Target                    |       R² |
|---------------------------|----------|
| Admiration                |   0.0129 |
| Adoration                 |   0.3831 |
| Aesthetic appreciation    |   0.5329 |
| Amusement                 |   0.3329 |
| Anger                     |   0.0862 |
| Anxiety                   |   0.2565 |
| Awe                       |   0.2746 |
| Awkwardness               |   0.0925 |
| Boredom                   |   0.1309 |
| Calmness                  |   0.3142 |
| Confusion                 |   0.0120 |
| Contempt                  |   0.0498 |
| Craving                   |   0.3542 |
| Disgust                   |   0.0117 |
| Empathic pain             |   0.2045 |
| Entrancement              |   0.0159 |
| Excitement                |   0.4025 |
| Fear                      |   0.0000 |
| Horror                    |   0.1556 |
| Interest                  |   0.2778 |
| Joy                       |   0.0000 |
| Nostalgia                 |   0.1475 |
| Relief                    |   0.1638 |
| Romance                   |   0.2250 |
| Sadness                   |   0.1844 |
| Satisfaction              |   0.0013 |
| Sexual desire             |   0.1403 |
| Surprise                  |   0.3127 |
| Sympathy                  |   0.0515 |
| Triumph                   |   0.0492 |
| Uncomfortable             |   0.5394 |
| Annoyance                 |   0.1994 |
| Envy                      |   0.0320 |
| Guilt                     |   0.1639 |
| Arousal                   |   0.1039 |
| Valence                   |   0.2181 |
| Cat=0.1797 AV=0.1610 ratio=1.116

### r2_cca_all
| Target                    |       R² |
|---------------------------|----------|
| Admiration                |   0.0031 |
| Adoration                 |   0.3966 |
| Aesthetic appreciation    |   0.5580 |
| Amusement                 |   0.3314 |
| Anger                     |   0.0818 |
| Anxiety                   |   0.2599 |
| Awe                       |   0.2721 |
| Awkwardness               |   0.0912 |
| Boredom                   |   0.1269 |
| Calmness                  |   0.3275 |
| Confusion                 |   0.0087 |
| Contempt                  |   0.0479 |
| Craving                   |   0.3718 |
| Disgust                   |   0.0038 |
| Empathic pain             |   0.2037 |
| Entrancement              |   0.0093 |
| Excitement                |   0.4211 |
| Fear                      |   0.0000 |
| Horror                    |   0.1564 |
| Interest                  |   0.2726 |
| Joy                       |   0.0000 |
| Nostalgia                 |   0.1460 |
| Relief                    |   0.1606 |
| Romance                   |   0.2285 |
| Sadness                   |   0.2069 |
| Satisfaction              |   0.0000 |
| Sexual desire             |   0.1397 |
| Surprise                  |   0.3167 |
| Sympathy                  |   0.0498 |
| Triumph                   |   0.0384 |
| Uncomfortable             |   0.5485 |
| Annoyance                 |   0.1965 |
| Envy                      |   0.0277 |
| Guilt                     |   0.1688 |
| Arousal                   |   0.1011 |
| Valence                   |   0.2089 |
| Cat=0.1815 AV=0.1550 ratio=1.171

### r2_pca_3
| Target                    |       R² |
|---------------------------|----------|
| Admiration                |   0.0018 |
| Adoration                 |   0.0885 |
| Aesthetic appreciation    |   0.3299 |
| Amusement                 |   0.1074 |
| Anger                     |   0.0132 |
| Anxiety                   |   0.0736 |
| Awe                       |   0.0513 |
| Awkwardness               |   0.0301 |
| Boredom                   |   0.0100 |
| Calmness                  |   0.1477 |
| Confusion                 |   0.0000 |
| Contempt                  |   0.0000 |
| Craving                   |   0.0091 |
| Disgust                   |   0.0000 |
| Empathic pain             |   0.0238 |
| Entrancement              |   0.0041 |
| Excitement                |   0.1965 |
| Fear                      |   0.0000 |
| Horror                    |   0.0609 |
| Interest                  |   0.0634 |
| Joy                       |   0.0000 |
| Nostalgia                 |   0.0248 |
| Relief                    |   0.0602 |
| Romance                   |   0.0795 |
| Sadness                   |   0.0041 |
| Satisfaction              |   0.0000 |
| Sexual desire             |   0.0284 |
| Surprise                  |   0.1105 |
| Sympathy                  |   0.0058 |
| Triumph                   |   0.0088 |
| Uncomfortable             |   0.1276 |
| Annoyance                 |   0.0969 |
| Envy                      |   0.0271 |
| Guilt                     |   0.0282 |
| Arousal                   |   0.0609 |
| Valence                   |   0.0095 |
| Cat=0.0533 AV=0.0352 ratio=1.514

### r2_pca_10
| Target                    |       R² |
|---------------------------|----------|
| Admiration                |   0.0190 |
| Adoration                 |   0.1540 |
| Aesthetic appreciation    |   0.4680 |
| Amusement                 |   0.2048 |
| Anger                     |   0.0578 |
| Anxiety                   |   0.1614 |
| Awe                       |   0.1369 |
| Awkwardness               |   0.0750 |
| Boredom                   |   0.1219 |
| Calmness                  |   0.2138 |
| Confusion                 |   0.0124 |
| Contempt                  |   0.0158 |
| Craving                   |   0.0453 |
| Disgust                   |   0.0217 |
| Empathic pain             |   0.0759 |
| Entrancement              |   0.0175 |
| Excitement                |   0.3653 |
| Fear                      |   0.0070 |
| Horror                    |   0.0941 |
| Interest                  |   0.1755 |
| Joy                       |   0.0026 |
| Nostalgia                 |   0.0809 |
| Relief                    |   0.1150 |
| Romance                   |   0.0960 |
| Sadness                   |   0.0485 |
| Satisfaction              |   0.0204 |
| Sexual desire             |   0.1002 |
| Surprise                  |   0.2051 |
| Sympathy                  |   0.0390 |
| Triumph                   |   0.0232 |
| Uncomfortable             |   0.2606 |
| Annoyance                 |   0.1546 |
| Envy                      |   0.0451 |
| Guilt                     |   0.0789 |
| Arousal                   |   0.0760 |
| Valence                   |   0.0649 |
| Cat=0.1092 AV=0.0704 ratio=1.550

### r2_pca_100
| Target                    |       R² |
|---------------------------|----------|
| Admiration                |   0.0031 |
| Adoration                 |   0.3966 |
| Aesthetic appreciation    |   0.5580 |
| Amusement                 |   0.3314 |
| Anger                     |   0.0818 |
| Anxiety                   |   0.2599 |
| Awe                       |   0.2721 |
| Awkwardness               |   0.0912 |
| Boredom                   |   0.1269 |
| Calmness                  |   0.3275 |
| Confusion                 |   0.0087 |
| Contempt                  |   0.0479 |
| Craving                   |   0.3718 |
| Disgust                   |   0.0038 |
| Empathic pain             |   0.2037 |
| Entrancement              |   0.0093 |
| Excitement                |   0.4211 |
| Fear                      |   0.0000 |
| Horror                    |   0.1564 |
| Interest                  |   0.2726 |
| Joy                       |   0.0000 |
| Nostalgia                 |   0.1460 |
| Relief                    |   0.1606 |
| Romance                   |   0.2285 |
| Sadness                   |   0.2069 |
| Satisfaction              |   0.0000 |
| Sexual desire             |   0.1397 |
| Surprise                  |   0.3167 |
| Sympathy                  |   0.0498 |
| Triumph                   |   0.0384 |
| Uncomfortable             |   0.5485 |
| Annoyance                 |   0.1965 |
| Envy                      |   0.0277 |
| Guilt                     |   0.1688 |
| Arousal                   |   0.1011 |
| Valence                   |   0.2089 |
| Cat=0.1815 AV=0.1550 ratio=1.171

## Exp 23: Reverse PCA+Ridge (20 Brain PCs)
|  BPC |       R² |      MSE |   Var% |             Top emotion |      r |      A |      V |
|------|----------|----------|--------|-------------------------|--------|--------|--------|
|    1 |   0.0000 |   5.7824 |  32.66 | Annoyance               | -0.223 | -0.102 | +0.075 |
|    2 |   0.0000 |   2.8736 |  16.27 | Guilt                   | +0.147 | +0.145 | +0.064 |
|    3 |   0.0000 |   2.1417 |  11.99 | Interest                | -0.204 | -0.003 | +0.190 |
|    4 |   0.0000 |   1.2835 |   6.68 | Amusement               | +0.183 | -0.103 | -0.098 |
|    5 |   0.0000 |   1.0631 |   6.16 | Relief                  | -0.105 | -0.004 | -0.106 |
|    6 |   0.0000 |   0.9979 |   5.08 | Awe                     | +0.172 | -0.024 | +0.152 |
|    7 |   0.0000 |   0.6384 |   3.60 | Nostalgia               | -0.178 | -0.029 | +0.197 |
|    8 |   0.0000 |   0.6867 |   2.86 | Amusement               | -0.084 | -0.084 | -0.078 |
|    9 |   0.0000 |   0.3164 |   1.86 | Aesthetic appreciation  | +0.197 | +0.011 | +0.011 |
|   10 |   0.0000 |   0.3149 |   1.49 | Excitement              | +0.121 | +0.022 | +0.014 |
|   11 |   0.0000 |   0.3031 |   1.44 | Adoration               | -0.089 | +0.016 | -0.006 |
|   12 |   0.0000 |   0.1990 |   1.12 | Annoyance               | +0.176 | +0.083 | -0.018 |
|   13 |   0.0000 |   0.1864 |   0.87 | Annoyance               | -0.121 | -0.049 | +0.078 |
|   14 |   0.0000 |   0.1335 |   0.67 | Aesthetic appreciation  | -0.108 | -0.011 | +0.036 |
|   15 |   0.0000 |   0.1225 |   0.56 | Uncomfortable           | +0.083 | +0.040 | -0.012 |
|   16 |   0.0000 |   0.1178 |   0.53 | Horror                  | +0.079 | +0.072 | -0.011 |
|   17 |   0.0000 |   0.1041 |   0.49 | Interest                | -0.081 | -0.027 | +0.030 |
|   18 |   0.0000 |   0.0990 |   0.47 | Uncomfortable           | -0.206 | +0.041 | -0.047 |
|   19 |   0.0000 |   0.0867 |   0.42 | Adoration               | -0.092 | +0.026 | -0.081 |
|   20 |   0.0000 |   0.0649 |   0.32 | Uncomfortable           | -0.073 | +0.019 | +0.019 |

### r2_decode_Brain_PC1_3
| Target                    |       R² |
|---------------------------|----------|
| Admiration                |   0.0020 |
| Adoration                 |   0.0034 |
| Aesthetic appreciation    |   0.0078 |
| Amusement                 |   0.0086 |
| Anger                     |   0.0062 |
| Anxiety                   |   0.0365 |
| Awe                       |   0.0156 |
| Awkwardness               |   0.0119 |
| Boredom                   |   0.0054 |
| Calmness                  |   0.0003 |
| Confusion                 |   0.0024 |
| Contempt                  |   0.0000 |
| Craving                   |   0.0000 |
| Disgust                   |   0.0000 |
| Empathic pain             |   0.0249 |
| Entrancement              |   0.0114 |
| Excitement                |   0.0314 |
| Fear                      |   0.0000 |
| Horror                    |   0.0192 |
| Interest                  |   0.0450 |
| Joy                       |   0.0000 |
| Nostalgia                 |   0.0219 |
| Relief                    |   0.0393 |
| Romance                   |   0.0000 |
| Sadness                   |   0.0109 |
| Satisfaction              |   0.0005 |
| Sexual desire             |   0.0300 |
| Surprise                  |   0.0266 |
| Sympathy                  |   0.0122 |
| Triumph                   |   0.0264 |
| Uncomfortable             |   0.0352 |
| Annoyance                 |   0.0587 |
| Envy                      |   0.0151 |
| Guilt                     |   0.0224 |
| Arousal                   |   0.0260 |
| Valence                   |   0.0255 |
| Cat=0.0156 AV=0.0258 ratio=0.606

### r2_decode_Brain_PC1_10
| Target                    |       R² |
|---------------------------|----------|
| Admiration                |   0.0092 |
| Adoration                 |   0.0355 |
| Aesthetic appreciation    |   0.0698 |
| Amusement                 |   0.0638 |
| Anger                     |   0.0363 |
| Anxiety                   |   0.0720 |
| Awe                       |   0.0748 |
| Awkwardness               |   0.0249 |
| Boredom                   |   0.0095 |
| Calmness                  |   0.0277 |
| Confusion                 |   0.0350 |
| Contempt                  |   0.0000 |
| Craving                   |   0.0145 |
| Disgust                   |   0.0080 |
| Empathic pain             |   0.0805 |
| Entrancement              |   0.0537 |
| Excitement                |   0.0864 |
| Fear                      |   0.0044 |
| Horror                    |   0.0277 |
| Interest                  |   0.0753 |
| Joy                       |   0.0000 |
| Nostalgia                 |   0.0795 |
| Relief                    |   0.1050 |
| Romance                   |   0.0422 |
| Sadness                   |   0.0241 |
| Satisfaction              |   0.0090 |
| Sexual desire             |   0.0503 |
| Surprise                  |   0.0459 |
| Sympathy                  |   0.0263 |
| Triumph                   |   0.0285 |
| Uncomfortable             |   0.0814 |
| Annoyance                 |   0.0971 |
| Envy                      |   0.0285 |
| Guilt                     |   0.0297 |
| Arousal                   |   0.0336 |
| Valence                   |   0.1089 |
| Cat=0.0428 AV=0.0712 ratio=0.602

### r2_decode_Brain_all_100
| Target                    |       R² |
|---------------------------|----------|
| Admiration                |   0.0000 |
| Adoration                 |   0.0742 |
| Aesthetic appreciation    |   0.1253 |
| Amusement                 |   0.0843 |
| Anger                     |   0.0055 |
| Anxiety                   |   0.1348 |
| Awe                       |   0.0951 |
| Awkwardness               |   0.0214 |
| Boredom                   |   0.0000 |
| Calmness                  |   0.0412 |
| Confusion                 |   0.0276 |
| Contempt                  |   0.0000 |
| Craving                   |   0.0019 |
| Disgust                   |   0.0000 |
| Empathic pain             |   0.1731 |
| Entrancement              |   0.0534 |
| Excitement                |   0.1216 |
| Fear                      |   0.0000 |
| Horror                    |   0.0012 |
| Interest                  |   0.1297 |
| Joy                       |   0.0000 |
| Nostalgia                 |   0.1303 |
| Relief                    |   0.1145 |
| Romance                   |   0.0546 |
| Sadness                   |   0.0460 |
| Satisfaction              |   0.0000 |
| Sexual desire             |   0.0158 |
| Surprise                  |   0.0773 |
| Sympathy                  |   0.0000 |
| Triumph                   |   0.0000 |
| Uncomfortable             |   0.2146 |
| Annoyance                 |   0.1115 |
| Envy                      |   0.0000 |
| Guilt                     |   0.0000 |
| Arousal                   |   0.0196 |
| Valence                   |   0.1630 |
| Cat=0.0546 AV=0.0913 ratio=0.597

## Exp 26: Comprehensive Interpretation
R² vs Std: r=0.4797, p=0.004093
R² vs Mean: r=0.3842, p=0.024867

| Emotion                   |     R² |   Mean |    Std |   Skew |   NZ% |  AV-resid |   Ret% |
|---------------------------|--------|--------|--------|--------|-------|-----------|--------|
| Admiration                | 0.0235 |  0.036 |  0.071 |   2.44 | 27.8% |    0.0291 | 124.0% |
| Adoration                 | 0.0805 |  0.059 |  0.122 |   2.57 | 28.3% |    0.0895 | 111.2% |
| Aesthetic appreciation    | 0.3231 |  0.079 |  0.154 |   2.37 | 33.3% |    0.3270 | 101.2% |
| Amusement                 | 0.1159 |  0.204 |  0.233 |   1.02 | 64.1% |    0.1504 | 129.7% |
| Anger                     | 0.0118 |  0.017 |  0.059 |   4.62 | 10.7% |    0.0121 | 102.9% |
| Anxiety                   | 0.0611 |  0.066 |  0.125 |   2.64 | 35.2% |    0.0250 |  41.0% |
| Awe                       | 0.0222 |  0.107 |  0.141 |   1.42 | 52.5% |    0.0249 | 111.9% |
| Awkwardness               | 0.0308 |  0.027 |  0.069 |   4.18 | 21.0% |    0.0195 |  63.3% |
| Boredom                   | 0.0196 |  0.044 |  0.082 |   2.71 | 33.3% |    0.0149 |  76.2% |
| Calmness                  | 0.1361 |  0.037 |  0.087 |   3.60 | 25.2% |    0.1225 |  90.0% |
| Confusion                 | 0.0000 |  0.062 |  0.105 |   2.54 | 39.9% |    0.0000 |   0.0% |
| Contempt                  | 0.0000 |  0.011 |  0.032 |   3.73 | 11.2% |    0.0000 |   0.0% |
| Craving                   | 0.0166 |  0.022 |  0.114 |   6.27 |  7.2% |    0.0120 |  72.0% |
| Disgust                   | 0.0088 |  0.014 |  0.042 |   3.89 | 12.7% |    0.0094 | 107.0% |
| Empathic pain             | 0.0741 |  0.087 |  0.198 |   2.74 | 28.4% |    0.0834 | 112.5% |
| Entrancement              | 0.0024 |  0.026 |  0.079 |   4.31 | 16.2% |    0.0046 | 194.9% |
| Excitement                | 0.2001 |  0.044 |  0.089 |   2.64 | 28.5% |    0.1943 |  97.1% |
| Fear                      | 0.0000 |  0.007 |  0.027 |   4.29 |  8.1% |    0.0000 |   0.0% |
| Horror                    | 0.0570 |  0.048 |  0.082 |   2.28 | 36.3% |    0.0386 |  67.8% |
| Interest                  | 0.0598 |  0.078 |  0.154 |   2.27 | 31.3% |    0.0243 |  40.6% |
| Joy                       | 0.0028 |  0.005 |  0.020 |   4.92 |  5.2% |    0.0069 | 247.9% |
| Nostalgia                 | 0.0167 |  0.064 |  0.139 |   2.80 | 28.3% |    0.0000 |   0.0% |
| Relief                    | 0.0576 |  0.113 |  0.130 |   1.46 | 63.5% |    0.0532 |  92.4% |
| Romance                   | 0.0793 |  0.081 |  0.129 |   2.00 | 42.9% |    0.1170 | 147.6% |
| Sadness                   | 0.0094 |  0.033 |  0.112 |   4.33 | 14.5% |    0.0020 |  21.2% |
| Satisfaction              | 0.0071 |  0.007 |  0.032 |   7.49 |  6.6% |    0.0078 | 108.9% |
| Sexual desire             | 0.0313 |  0.018 |  0.064 |   5.03 | 12.1% |    0.0196 |  62.6% |
| Surprise                  | 0.0450 |  0.031 |  0.127 |   4.68 |  8.6% |    0.0441 |  98.1% |
| Sympathy                  | 0.0059 |  0.048 |  0.125 |   3.66 | 22.3% |    0.0137 | 232.3% |
| Triumph                   | 0.0128 |  0.041 |  0.067 |   1.99 | 35.4% |    0.0204 | 159.5% |
| Uncomfortable             | 0.1715 |  0.053 |  0.180 |   3.78 | 12.2% |    0.1970 | 114.9% |
| Annoyance                 | 0.1057 |  0.091 |  0.119 |   1.59 | 52.5% |    0.0802 |  75.9% |
| Envy                      | 0.0293 |  0.033 |  0.076 |   3.19 | 23.0% |    0.0280 |  95.4% |
| Guilt                     | 0.0518 |  0.019 |  0.061 |   4.39 | 13.9% |    0.0538 | 103.8% |
| MEAN                      | 0.0550 | | | | |    0.0537 |  97.6% |

Raw fMRI vs Brain-JEPA → V-JEPA2 PC:
|  PC |   Raw fMRI |   Brain-JEPA |        Δ |
|-----|------------|--------------|----------|
|   1 |     0.3540 |       0.3728 |  +0.0188 |
|   2 |     0.2274 |       0.0748 |  -0.1526 |
|   3 |     0.3068 |       0.0878 |  -0.2190 |
|   4 |     0.1469 |       0.0003 |  -0.1466 |
|   5 |     0.0825 |       0.0000 |  -0.0825 |
|   6 |     0.0361 |       0.0000 |  -0.0361 |
|   7 |     0.0000 |       0.0000 |  +0.0000 |
|   8 |     0.0000 |       0.0000 |  +0.0000 |
|   9 |     0.0036 |       0.0000 |  -0.0036 |
|  10 |     0.0000 |       0.0000 |  +0.0000 |

### Raw fMRI → emotion decoding
| Target                    |       R² |
|---------------------------|----------|
| Admiration                |   0.0000 |
| Adoration                 |   0.0000 |
| Aesthetic appreciation    |   0.1351 |
| Amusement                 |   0.0774 |
| Anger                     |   0.0000 |
| Anxiety                   |   0.0510 |
| Awe                       |   0.0000 |
| Awkwardness               |   0.0000 |
| Boredom                   |   0.0000 |
| Calmness                  |   0.0000 |
| Confusion                 |   0.0000 |
| Contempt                  |   0.0000 |
| Craving                   |   0.0000 |
| Disgust                   |   0.0000 |
| Empathic pain             |   0.1205 |
| Entrancement              |   0.0000 |
| Excitement                |   0.1107 |
| Fear                      |   0.0000 |
| Horror                    |   0.0000 |
| Interest                  |   0.0626 |
| Joy                       |   0.0000 |
| Nostalgia                 |   0.0021 |
| Relief                    |   0.0000 |
| Romance                   |   0.0000 |
| Sadness                   |   0.0000 |
| Satisfaction              |   0.0000 |
| Sexual desire             |   0.0000 |
| Surprise                  |   0.0000 |
| Sympathy                  |   0.0000 |
| Triumph                   |   0.0000 |
| Uncomfortable             |   0.2919 |
| Annoyance                 |   0.0265 |
| Envy                      |   0.0000 |
| Guilt                     |   0.0000 |
| Arousal                   |   0.0000 |
| Valence                   |   0.1461 |
| Cat=0.0258 AV=0.0730 ratio=0.353

### Brain-JEPA → emotion decoding
| Target                    |       R² |
|---------------------------|----------|
| Admiration                |   0.0000 |
| Adoration                 |   0.0000 |
| Aesthetic appreciation    |   0.0821 |
| Amusement                 |   0.0000 |
| Anger                     |   0.0000 |
| Anxiety                   |   0.0026 |
| Awe                       |   0.0000 |
| Awkwardness               |   0.0000 |
| Boredom                   |   0.0000 |
| Calmness                  |   0.0000 |
| Confusion                 |   0.0000 |
| Contempt                  |   0.0000 |
| Craving                   |   0.0000 |
| Disgust                   |   0.0000 |
| Empathic pain             |   0.0327 |
| Entrancement              |   0.0000 |
| Excitement                |   0.0387 |
| Fear                      |   0.0000 |
| Horror                    |   0.0000 |
| Interest                  |   0.0000 |
| Joy                       |   0.0000 |
| Nostalgia                 |   0.0011 |
| Relief                    |   0.0000 |
| Romance                   |   0.0000 |
| Sadness                   |   0.0000 |
| Satisfaction              |   0.0000 |
| Sexual desire             |   0.0000 |
| Surprise                  |   0.0006 |
| Sympathy                  |   0.0000 |
| Triumph                   |   0.0000 |
| Uncomfortable             |   0.1920 |
| Annoyance                 |   0.0000 |
| Envy                      |   0.0000 |
| Guilt                     |   0.0000 |
| Arousal                   |   0.0000 |
| Valence                   |   0.0652 |
| Cat=0.0103 AV=0.0326 ratio=0.316

### V-JEPA2 → emotion decoding
| Target                    |       R² |
|---------------------------|----------|
| Admiration                |   0.0000 |
| Adoration                 |   0.0000 |
| Aesthetic appreciation    |   0.0000 |
| Amusement                 |   0.0000 |
| Anger                     |   0.0000 |
| Anxiety                   |   0.0000 |
| Awe                       |   0.0000 |
| Awkwardness               |   0.0000 |
| Boredom                   |   0.0000 |
| Calmness                  |   0.0000 |
| Confusion                 |   0.0000 |
| Contempt                  |   0.0000 |
| Craving                   |   0.0000 |
| Disgust                   |   0.0000 |
| Empathic pain             |   0.0000 |
| Entrancement              |   0.0000 |
| Excitement                |   0.0000 |
| Fear                      |   0.0000 |
| Horror                    |   0.0000 |
| Interest                  |   0.0000 |
| Joy                       |   0.0000 |
| Nostalgia                 |   0.0000 |
| Relief                    |   0.0000 |
| Romance                   |   0.0000 |
| Sadness                   |   0.0000 |
| Satisfaction              |   0.0000 |
| Sexual desire             |   0.0000 |
| Surprise                  |   0.0000 |
| Sympathy                  |   0.0000 |
| Triumph                   |   0.0000 |
| Uncomfortable             |   0.0000 |
| Annoyance                 |   0.0000 |
| Envy                      |   0.0000 |
| Guilt                     |   0.0000 |
| Arousal                   |   0.0000 |
| Valence                   |   0.0000 |
| Cat=0.0000 AV=0.0000 ratio=0.000

Emotion PCA (34 components):
|  PC |    Var% |   Cumul% |
|-----|---------|----------|
|   1 |  19.69% |   19.69% |
|   2 |  13.04% |   32.73% |
|   3 |  10.11% |   42.84% |
|   4 |   8.09% |   50.93% |
|   5 |   6.26% |   57.19% |
|   6 |   4.68% |   61.87% |
|   7 |   4.04% |   65.91% |
|   8 |   3.63% |   69.54% |
|   9 |   3.09% |   72.64% |
|  10 |   2.95% |   75.59% |
|  11 |   2.62% |   78.21% |
|  12 |   2.47% |   80.68% |
|  13 |   2.29% |   82.97% |
|  14 |   1.96% |   84.93% |
|  15 |   1.68% |   86.61% |
|  16 |   1.55% |   88.16% |
|  17 |   1.20% |   89.37% |
|  18 |   1.15% |   90.52% |
|  19 |   1.11% |   91.63% |
|  20 |   1.03% |   92.66% |
|  21 |   0.94% |   93.60% |
|  22 |   0.90% |   94.50% |
|  23 |   0.88% |   95.38% |
|  24 |   0.78% |   96.16% |
|  25 |   0.72% |   96.88% |
|  26 |   0.69% |   97.57% |
|  27 |   0.59% |   98.16% |
|  28 |   0.52% |   98.68% |
|  29 |   0.46% |   99.14% |
|  30 |   0.28% |   99.42% |
|  31 |   0.18% |   99.60% |
|  32 |   0.17% |   99.77% |
|  33 |   0.15% |   99.92% |
|  34 |   0.08% |  100.00% |

## Exp 27: Deep Analysis

### 34 emotions 전체 통계
| Emotion                   |     R² |   Std |   NZ% |  Str% |  MaxCr |  RankR² | Basic |
|---------------------------|--------|-------|-------|-------|--------|---------|-------|
| Aesthetic appreciation    | 0.3231 | 0.154 | 33.3% | 10.0% |  0.557 |  0.2618 |       |
| Excitement                | 0.2001 | 0.089 | 28.5% |  3.2% |  0.557 |  0.1844 |       |
| Uncomfortable             | 0.1715 | 0.180 | 12.2% |  6.7% |  0.306 |  0.1462 |       |
| Calmness                  | 0.1361 | 0.087 | 25.2% |  2.9% |  0.511 |  0.0877 |       |
| Amusement                 | 0.1159 | 0.233 | 64.1% | 29.6% |  0.364 |  0.1147 |       |
| Annoyance                 | 0.1057 | 0.119 | 52.5% |  7.0% |  0.216 |  0.1279 |       |
| Adoration                 | 0.0805 | 0.122 | 28.3% |  6.4% |  0.623 |  0.0762 |       |
| Romance                   | 0.0793 | 0.129 | 42.9% |  7.8% |  0.623 |  0.0577 |       |
| Empathic pain             | 0.0741 | 0.198 | 28.4% | 10.9% |  0.399 |  0.0710 |       |
| Anxiety                   | 0.0611 | 0.125 | 35.2% |  6.1% |  0.764 |  0.0657 |       |
| Interest                  | 0.0598 | 0.154 | 31.3% | 10.6% |  0.764 |  0.0658 |       |
| Relief                    | 0.0576 | 0.130 | 63.5% |  9.7% |  0.361 |  0.0548 |       |
| Horror                    | 0.0570 | 0.082 | 36.3% |  2.2% |  0.349 |  0.0417 |       |
| Guilt                     | 0.0518 | 0.061 | 13.9% |  1.2% |  0.392 |  0.0830 |       |
| Surprise                  | 0.0450 | 0.127 |  8.6% |  4.1% |  0.306 |  0.0676 |   YES |
| Sexual desire             | 0.0313 | 0.064 | 12.1% |  1.3% |  0.292 |  0.0355 |       |
| Awkwardness               | 0.0308 | 0.069 | 21.0% |  1.3% |  0.218 |  0.0383 |       |
| Envy                      | 0.0293 | 0.076 | 23.0% |  2.1% |  0.626 |  0.0384 |       |
| Admiration                | 0.0235 | 0.071 | 27.8% |  1.0% |  0.365 |  0.0114 |       |
| Awe                       | 0.0222 | 0.141 | 52.5% | 11.2% |  0.352 |  0.0202 |       |
| Boredom                   | 0.0196 | 0.082 | 33.3% |  2.2% |  0.196 |  0.0157 |       |
| Nostalgia                 | 0.0167 | 0.139 | 28.3% |  7.6% |  0.534 |  0.0128 |       |
| Craving                   | 0.0166 | 0.114 |  7.2% |  2.6% |  0.153 |  0.0461 |       |
| Triumph                   | 0.0128 | 0.067 | 35.4% |  0.8% |  0.341 |  0.0032 |       |
| Anger                     | 0.0118 | 0.059 | 10.7% |  1.3% |  0.441 |  0.0163 |   YES |
| Sadness                   | 0.0094 | 0.112 | 14.5% |  4.1% |  0.177 |  0.0000 |   YES |
| Disgust                   | 0.0088 | 0.042 | 12.7% |  0.2% |  0.412 |  0.0124 |   YES |
| Satisfaction              | 0.0071 | 0.032 |  6.6% |  0.1% |  0.392 |  0.0085 |       |
| Sympathy                  | 0.0059 | 0.125 | 22.3% |  5.1% |  0.626 |  0.0106 |       |
| Joy                       | 0.0028 | 0.020 |  5.2% |  0.0% |  0.353 |  0.0011 |   YES |
| Entrancement              | 0.0024 | 0.079 | 16.2% |  2.0% |  0.433 |  0.0042 |       |
| Fear                      | 0.0000 | 0.027 |  8.1% |  0.0% |  0.227 |  0.0000 |   YES |
| Contempt                  | 0.0000 | 0.032 | 11.2% |  0.0% |  0.441 |  0.0000 |       |
| Confusion                 | 0.0000 | 0.105 | 39.9% |  4.3% |  0.203 |  0.0000 |       |

### Raw fMRI Forward/Reverse (20 PCs)
|  PC |   Fwd R² |   Rev R² |
|-----|----------|----------|
|   1 |   0.3540 |   0.0000 |
|   2 |   0.2274 |   0.0000 |
|   3 |   0.3068 |   0.0000 |
|   4 |   0.1469 |   0.0000 |
|   5 |   0.0825 |   0.0000 |
|   6 |   0.0361 |   0.0000 |
|   7 |   0.0000 |   0.0000 |
|   8 |   0.0000 |   0.0000 |
|   9 |   0.0036 |   0.0000 |
|  10 |   0.0000 |   0.0000 |
|  11 |   0.0000 |   0.0000 |
|  12 |   0.0000 |   0.0000 |
|  13 |   0.0000 |   0.0000 |
|  14 |   0.0000 |   0.0000 |
|  15 |   0.0000 |   0.0000 |
|  16 |   0.0000 |   0.0000 |
|  17 |   0.0000 |   0.0000 |
|  18 |   0.0000 |   0.0000 |
|  19 |   0.0000 |   0.0000 |
|  20 |   0.0000 |   0.0000 |
raw_pred_mask: [ True  True  True  True  True  True False False False False False False
 False False False False False False False False]

### Raw fMRI brain-pred emotion decoding
| Target                    |       R² |
|---------------------------|----------|
| Admiration                |   0.0271 |
| Adoration                 |   0.0818 |
| Aesthetic appreciation    |   0.3717 |
| Amusement                 |   0.1568 |
| Anger                     |   0.0297 |
| Anxiety                   |   0.1082 |
| Awe                       |   0.0758 |
| Awkwardness               |   0.0647 |
| Boredom                   |   0.0975 |
| Calmness                  |   0.1564 |
| Confusion                 |   0.0030 |
| Contempt                  |   0.0132 |
| Craving                   |   0.0347 |
| Disgust                   |   0.0095 |
| Empathic pain             |   0.0769 |
| Entrancement              |   0.0115 |
| Excitement                |   0.2427 |
| Fear                      |   0.0000 |
| Horror                    |   0.0587 |
| Interest                  |   0.1113 |
| Joy                       |   0.0042 |
| Nostalgia                 |   0.0387 |
| Relief                    |   0.0810 |
| Romance                   |   0.0909 |
| Sadness                   |   0.0457 |
| Satisfaction              |   0.0178 |
| Sexual desire             |   0.0425 |
| Surprise                  |   0.0908 |
| Sympathy                  |   0.0237 |
| Triumph                   |   0.0125 |
| Uncomfortable             |   0.2008 |
| Annoyance                 |   0.1126 |
| Envy                      |   0.0377 |
| Guilt                     |   0.0622 |
| Arousal                   |   0.0698 |
| Valence                   |   0.0209 |
| Cat=0.0763 AV=0.0454 ratio=1.681

### Variance Partitioning (34 emotions)
| Emotion                   |    Stim |   Brain |  Shared |   Total |
|---------------------------|---------|---------|---------|---------|
| Admiration                |  0.0000 |  0.0000 |  0.0235 |  0.0000 |
| Adoration                 |  0.0000 |  0.0000 |  0.0805 |  0.0000 |
| Aesthetic appreciation    |  0.2055 |  0.0000 |  0.1177 |  0.2876 |
| Amusement                 |  0.0223 |  0.0000 |  0.0936 |  0.0223 |
| Anger                     |  0.0000 |  0.0000 |  0.0118 |  0.0000 |
| Anxiety                   |  0.0074 |  0.0000 |  0.0537 |  0.0100 |
| Awe                       |  0.0000 |  0.0000 |  0.0222 |  0.0000 |
| Awkwardness               |  0.0000 |  0.0000 |  0.0308 |  0.0000 |
| Boredom                   |  0.0000 |  0.0000 |  0.0196 |  0.0000 |
| Calmness                  |  0.0053 |  0.0000 |  0.1308 |  0.0053 |
| Confusion                 |  0.0000 |  0.0000 |  0.0000 |  0.0000 |
| Contempt                  |  0.0000 |  0.0000 |  0.0000 |  0.0000 |
| Craving                   |  0.0000 |  0.0000 |  0.0166 |  0.0000 |
| Disgust                   |  0.0000 |  0.0000 |  0.0088 |  0.0000 |
| Empathic pain             |  0.0322 |  0.0000 |  0.0419 |  0.0648 |
| Entrancement              |  0.0000 |  0.0000 |  0.0024 |  0.0000 |
| Excitement                |  0.1125 |  0.0000 |  0.0876 |  0.1512 |
| Fear                      |  0.0000 |  0.0000 |  0.0000 |  0.0000 |
| Horror                    |  0.0000 |  0.0000 |  0.0570 |  0.0000 |
| Interest                  |  0.0000 |  0.0000 |  0.0598 |  0.0000 |
| Joy                       |  0.0000 |  0.0000 |  0.0028 |  0.0000 |
| Nostalgia                 |  0.0040 |  0.0000 |  0.0127 |  0.0051 |
| Relief                    |  0.0000 |  0.0000 |  0.0576 |  0.0000 |
| Romance                   |  0.0000 |  0.0000 |  0.0793 |  0.0000 |
| Sadness                   |  0.0000 |  0.0000 |  0.0094 |  0.0000 |
| Satisfaction              |  0.0000 |  0.0000 |  0.0071 |  0.0000 |
| Sexual desire             |  0.0000 |  0.0000 |  0.0313 |  0.0000 |
| Surprise                  |  0.0141 |  0.0000 |  0.0309 |  0.0147 |
| Sympathy                  |  0.0000 |  0.0000 |  0.0059 |  0.0000 |
| Triumph                   |  0.0000 |  0.0000 |  0.0128 |  0.0000 |
| Uncomfortable             |  0.0819 |  0.1024 |  0.0896 |  0.2739 |
| Annoyance                 |  0.0000 |  0.0000 |  0.1057 |  0.0000 |
| Envy                      |  0.0000 |  0.0000 |  0.0293 |  0.0000 |
| Guilt                     |  0.0000 |  0.0000 |  0.0518 |  0.0000 |
| MEAN                      |  0.0143 |  0.0030 |  0.0407 |  0.0246 |

### Brain Residual (36 targets)
| Target                    |       R² |
|---------------------------|----------|
| Admiration                |   0.0000 |
| Adoration                 |   0.0000 |
| Aesthetic appreciation    |   0.0000 |
| Amusement                 |   0.0000 |
| Anger                     |   0.0000 |
| Anxiety                   |   0.0000 |
| Awe                       |   0.0000 |
| Awkwardness               |   0.0000 |
| Boredom                   |   0.0000 |
| Calmness                  |   0.0000 |
| Confusion                 |   0.0000 |
| Contempt                  |   0.0000 |
| Craving                   |   0.0000 |
| Disgust                   |   0.0000 |
| Empathic pain             |   0.0000 |
| Entrancement              |   0.0000 |
| Excitement                |   0.0000 |
| Fear                      |   0.0000 |
| Horror                    |   0.0000 |
| Interest                  |   0.0000 |
| Joy                       |   0.0000 |
| Nostalgia                 |   0.0000 |
| Relief                    |   0.0000 |
| Romance                   |   0.0000 |
| Sadness                   |   0.0000 |
| Satisfaction              |   0.0000 |
| Sexual desire             |   0.0000 |
| Surprise                  |   0.0000 |
| Sympathy                  |   0.0000 |
| Triumph                   |   0.0000 |
| Uncomfortable             |   0.0000 |
| Annoyance                 |   0.0000 |
| Envy                      |   0.0000 |
| Guilt                     |   0.0000 |
| Arousal                   |   0.0000 |
| Valence                   |   0.0081 |

### Clustering

3-cluster:
  Cluster 1 (n=9): ['Aesthetic appreciation', 'Boredom', 'Calmness', 'Craving', 'Excitement', 'Fear', 'Sadness', 'Surprise', 'Uncomfortable']
  Cluster 2 (n=10): ['Anxiety', 'Awe', 'Confusion', 'Horror', 'Interest', 'Nostalgia', 'Relief', 'Sexual desire', 'Triumph', 'Annoyance']
  Cluster 3 (n=15): ['Admiration', 'Adoration', 'Amusement', 'Anger', 'Awkwardness', 'Contempt', 'Disgust', 'Empathic pain', 'Entrancement', 'Joy', 'Romance', 'Satisfaction', 'Sympathy', 'Envy', 'Guilt']

5-cluster:
  Cluster 1 (n=9): ['Aesthetic appreciation', 'Boredom', 'Calmness', 'Craving', 'Excitement', 'Fear', 'Sadness', 'Surprise', 'Uncomfortable']
  Cluster 2 (n=2): ['Awe', 'Relief']
  Cluster 3 (n=8): ['Anxiety', 'Confusion', 'Horror', 'Interest', 'Nostalgia', 'Sexual desire', 'Triumph', 'Annoyance']
  Cluster 4 (n=3): ['Adoration', 'Awkwardness', 'Empathic pain']
  Cluster 5 (n=12): ['Admiration', 'Amusement', 'Anger', 'Contempt', 'Disgust', 'Entrancement', 'Joy', 'Romance', 'Satisfaction', 'Sympathy', 'Envy', 'Guilt']

### Partial Mantel
  Stim↔Brain: r=0.0750
  Stim↔Behav: r=0.1596
  Brain↔Behav: r=-0.0389
  Partial(Brain↔Behav|Stim): r=-0.0314, p=1.44e-28

### V-JEPA2 vs CLIP (Brain→PC)
|  PC |   V-JEPA2 |     CLIP |
|-----|-----------|----------|
|   1 |    0.3728 |   0.2613 |
|   2 |    0.0748 |   0.1559 |
|   3 |    0.0878 |   0.1271 |
|   4 |    0.0003 |   0.0000 |
|   5 |    0.0000 |   0.1154 |
|   6 |    0.0000 |   0.0167 |
|   7 |    0.0000 |   0.0125 |
|   8 |    0.0000 |   0.0000 |
|   9 |    0.0000 |   0.0000 |
|  10 |    0.0000 |   0.0000 |
---

# Part I: 핵심 수치 총 정리

| Metric | Value |
|--------|-------|
| **Data** | |
| V-JEPA2 dim | 1,408 |
| Brain-JEPA dim | 768 |
| Raw fMRI parcels | 450 |
| CLIP dim | 512 |
| Videos | 2,196 |
| Subjects | 5 |
| Emotions | 34 categories + Arousal + Valence |
| **Forward PCA+Ridge (Brain-JEPA)** | |
| Significant PCs | 3 (PC1, 2, 3) |
| PC1 R² | 0.373 |
| PC2 R² | 0.075 |
| PC3 R² | 0.088 |
| **Forward PCA+Ridge (Raw fMRI)** | |
| Significant PCs | 6 (PC1-6) |
| PC1 R² | 0.354 |
| PC2 R² | 0.227 |
| PC3 R² | 0.307 |
| PC4 R² | 0.147 |
| **Reverse PCA+Ridge** | |
| Significant PCs (both BJ and Raw) | **0** |
| All R² | **0.000** |
| **CCA (PCA100→CCA100)** | |
| CC1 canonical r | 0.774 |
| Significant CCs (FDR<0.05) | 88/100 |
| CCs with r > 0.3 | 27 |
| CC1 subject stability (SD) | 0.013 |
| **Cat/VA Ratios** | |
| Forward brain-pred (BJ, 3 PCs) | 1.44 |
| Forward brain-pred (Raw, 6 PCs) | **1.68** |
| Forward full space (100 PCs) | 1.26 |
| CCA-sig (88 CCs) | 1.12 |
| Reverse Brain PCs | **0.60** |
| **AV Regress Out** | |
| Retention after VA removal | **97.6%** |
| **Rating Distribution** | |
| R² vs Std correlation | r=0.480, p=0.004 |
| Rank-normalized R² correlation | r=0.971 |
| **Emotion PCA dimensionality** | |
| 95% variance | 23 dims |
| 99% variance | 29 dims |
| **Brain-JEPA vs Raw fMRI** | |
| Brain-pred PCs (BJ vs Raw) | 3 vs 6 |
| Emotion decoding Cat R² (BJ vs Raw) | 0.010 vs 0.026 |
| **V-JEPA2 vs CLIP** | |
| Brain-pred PCs (V-JEPA2 vs CLIP) | 3 vs 6 |
| **Statistics** | |
| Permutation test n | 1,000 |
| FDR method | Benjamini-Hochberg, q < 0.05 |
