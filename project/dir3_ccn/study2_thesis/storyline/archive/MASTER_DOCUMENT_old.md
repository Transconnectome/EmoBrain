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

# Part H: 초기 분석 결과 (Exp 01~16) — 상세

**이 섹션의 상세 수치는 다음 파일에 있음:**
- `CCN2026/RESULTS_MASTER_0402.md` (1164줄, exp1~19 전체 상세)
- `main/storyline/ALL_RAW_RESULTS.md` (1607줄, 모든 npz 원본 dump)

### Exp 01-02: Brain-JEPA RSM + Subject 간 일관성

```
Brain-JEPA cross-subject RSM consistency (Spearman r):
         Subj1   Subj2   Subj3   Subj4   Subj5
Subj1   1.000   0.332   0.318   0.285   0.329
Subj2   0.332   1.000   0.381   0.359   0.412
Subj3   0.318   0.381   1.000   0.327   0.367
Subj4   0.285   0.359   0.327   1.000   0.360
Subj5   0.329   0.412   0.367   0.360   1.000

off-diagonal mean = 0.347 ± 0.034

Per-subject CKA:
  Subject  CKA(brain,V-JEPA2)  CKA(brain,CLIP)
  1        0.0548              0.0474
  2        0.0633              0.0600
  3        0.0554              0.0508
  4        0.0458              0.0513
  5        0.0726              0.0603
  Mean     0.0584              0.0539
```

### Exp 03-04: Cross-space RSA (34 emotions)

Brain-JEPA, V-JEPA2, CLIP 각각의 RSM과 34개 감정 kernel의 Spearman r.
상위 감정 (V-JEPA2 기준): Amusement(0.180), Aesthetic apprec.(-0.127), Excitement(-0.103).
→ 상세 34개 전부: RESULTS_MASTER_0402.md Section 6 참조.

### Exp 05 + 08: K-sweep (차원 수 분석)

```
Brain-JEPA k-sweep CKA (brain vs V-JEPA2):
  k=3:  0.0233   k=10: 0.0407   k=27: 0.0534
  k=50: 0.0569   k=100: 0.0584

→ k=27 근방에서 사실상 포화.
→ 27차원이면 brain-video alignment의 대부분을 포착.
```

### Exp 10: Brain-predictable dimensions

```
Brain-JEPA → V-JEPA2 PC prediction (Ridge CV R²):
  V-JEPA2: PC1=0.3728, PC2=0.0748, PC3=0.0878, PC4=0.0003, 나머지 ~0
  → brain-pred PCs = PC1, PC2, PC3

Brain-JEPA → CLIP PC prediction:
  CLIP: PC1=0.2613, PC2=0.1559, PC3=0.1271, PC5=0.1154, PC6=0.0167, PC7=0.0125
  → brain-pred PCs = PC1-3, PC5-7 (6개)
```

### Exp 11: PC × Emotion Correlation

```
V-JEPA2 brain-pred PCs (PC1-3):
  PC1 top emotions: Annoyance(+0.44), Uncomfortable(-0.33), Interest(+0.32)
  PC2 top emotions: Aesthetic apprec.(+0.46), Excitement(+0.37)
  PC3 top emotions: Interest(-0.18), Anxiety(-0.17)

Brain-pred mean max|r| = 높음
Brain-unpred mean max|r| = 낮음
→ 뇌가 읽는 축이 감정과 더 강하게 연결
```

### Exp 12: Category vs Dimension 설명력

```
Brain-pred subspace → 34 emotion vs A/V/D decoding:
  Brain-JEPA: Cat R²=0.055, AV R²=0.038, Cat/VA=1.44
  Raw fMRI:   Cat R²=0.076, AV R²=0.045, Cat/VA=1.68

Full space (100 PCs):
  Cat R²=0.170, AV R²=0.135, Cat/VA=1.26
```

### Exp 13: Vision/Semantic Confound Control

```
Vision + Semantic features를 confound로 통제:
  → partial R² 감소함
  → "보이는 감정 효과의 일부는 저수준 시각/의미 confound 때문"
  → 하지만 완전히 사라지지 않음 → 감정 고유 신호 존재
  → 상세: RESULTS_EXP13_0402.md 참조
```

### Exp 14: Robustness 분석

```
PCA 차원 수, Ridge alpha 등 hyperparameter 변경해도 결과 안정적.
→ 상세: exp14_robustness_results.npz
```

### Exp 15: Subject Stability (Bootstrap)

```
5명 중 부분집합으로 resampling → brain-pred PC 안정성 확인.
→ 상세: exp15_stability_results.npz
```

### Exp 16: Incremental Baseline

```
차원을 점진적으로 늘리면서 디코딩:
  k=3 → k=10 → k=27 → k=50 → k=100
  → 감정 디코딩은 k=27 근방에서 사실상 포화
```

### Exp 18: Subject-wise Claim Check

```
5명 개별로 brain-pred subspace → emotion decoding:
  Mean Cat/VA ratio across subjects = 비슷한 패턴 유지
  → group-level 결과가 individual-level에서도 재현
  → 상세: RESULTS_EXP18_0402.md
```

### Exp 19: Permutation Test

```
n=1000 permutation, FDR BH q<0.05:
  PC1: R²=0.373, p=0.000, q=0.000
  PC2: R²=0.075, p=0.000, q=0.000
  PC3: R²=0.088, p=0.000, q=0.000
  PC4: R²=0.000, p=0.000, q=0.000 (clipping artifact → excluded)
  PC5-100: R²=0.000, p=1.000

→ PC1-3만 유의. PC4는 artifact (R²=0.000251, null 전부 0으로 clipping).
```

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
