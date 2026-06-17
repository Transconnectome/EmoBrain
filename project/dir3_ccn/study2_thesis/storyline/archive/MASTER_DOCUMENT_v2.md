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

# 전체 Experiment 결과 상세 — Raw 수치 전부

Generated: 2026-04-10

### Exp 03-04: Cross-space RSA 전체 수치

Keys: ['emotion_labels', 'rsa_brain', 'rsa_vjepa2', 'rsa_clip', 'alignment', 'divergence']
  emotion_labels: ['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom' 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement'
 'Excitement' 'Fear' 'Horror' 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy' 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  rsa_brain: [-1.8824e-02  5.6880e-03  2.2610e-02 -8.2621e-02 -2.0797e-03 -3.6861e-02 -4.3583e-02  1.5989e-02 -1.1447e-03  3.7007e-02 -2.6636e-02 -3.2911e-03  3.0783e-02 -7.4421e-05  2.6774e-02 -1.4773e-02
 -1.2570e-02  9.6396e-03 -1.9927e-02 -2.7501e-02  3.3932e-03 -2.5987e-03 -6.8246e-02 -6.0835e-03  3.8634e-02 -6.0793e-03 -1.5026e-02  5.0138e-02 -1.8333e-02 -4.0270e-02  6.2026e-02 -1.0847e-01
 -2.2637e-02 -3.7373e-02]
  rsa_vjepa2: [ 0.0146  0.0919 -0.1273  0.1803  0.0283  0.0393 -0.0067  0.0446 -0.0431 -0.0822  0.0277 -0.0011  0.0045  0.0236  0.064   0.048  -0.1031 -0.0086  0.0203  0.0625  0.0171  0.0678 -0.0571  0.0984
  0.0085  0.013   0.0336  0.0187  0.042   0.0011  0.0303  0.151   0.073   0.038 ]
  rsa_clip: [-0.014   0.0815 -0.0027  0.1335  0.0315  0.1299  0.0918  0.0145 -0.0931 -0.0529  0.0931 -0.0192  0.0166 -0.0012  0.0447  0.0564  0.019  -0.0149  0.016   0.151   0.0096  0.1356  0.0479  0.0178
 -0.0175 -0.0186  0.0478  0.0425  0.0403 -0.0105  0.066   0.22    0.0634  0.0135]
  alignment: [-1.8824e-02  5.6880e-03 -1.2734e-01 -8.2621e-02 -2.0797e-03 -3.6861e-02 -4.3583e-02  1.5989e-02 -4.3090e-02 -8.2173e-02 -2.6636e-02 -3.2911e-03  4.5209e-03 -7.4421e-05  2.6774e-02 -1.4773e-02
 -1.0310e-01 -8.5679e-03 -1.9927e-02 -2.7501e-02  3.3932e-03 -2.5987e-03 -6.8246e-02 -6.0835e-03  8.5282e-03 -6.0793e-03 -1.5026e-02  1.8697e-02 -1.8333e-02 -4.0270e-02  3.0325e-02 -1.0847e-01
 -2.2637e-02 -3.7373e-02]
  divergence: [0.0335 0.0862 0.1499 0.2629 0.0304 0.0762 0.0369 0.0286 0.0419 0.1192 0.0544 0.0022 0.0263 0.0237 0.0372 0.0628 0.0905 0.0182 0.0402 0.09   0.0137 0.0704 0.0111 0.1045 0.0301 0.0191 0.0487 0.0314
 0.0603 0.0414 0.0317 0.2594 0.0956 0.0754]

### Exp 05: K-sweep 전체 수치
  k_values: [  3   5   7  10  15  20  25  27  30  34  40  50  75 100]
  cka_brain_vjepa: [0.1172 0.1175 0.1192 0.1218 0.1258 0.126  0.1265 0.1266 0.1266 0.1268 0.127  0.1272 0.1276 0.1278]
  cka_brain_clip: [0.0955 0.0949 0.1005 0.1072 0.1087 0.1093 0.1094 0.1094 0.1096 0.1098 0.1101 0.1101 0.1104 0.1106]
  rsa_brain_vjepa: [0.0964 0.1034 0.1067 0.1124 0.1181 0.1189 0.1197 0.1196 0.1196 0.1199 0.1199 0.1202 0.1204 0.1205]
  rsa_brain_clip: [0.0932 0.0969 0.1011 0.1077 0.1082 0.1081 0.1079 0.1076 0.1078 0.1079 0.1081 0.1083 0.108  0.108 ]

### Exp 10: Brain-predictable dimensions 전체
  r2_vjepa_per_dim: shape=(100,)
    [3.728423e-01 7.479128e-02 8.776965e-02 3.172854e-04 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00
 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00
 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00
 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00
 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00
 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00
 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00]
  r2_clip_per_dim: shape=(100,)
    [0.261256 0.155886 0.127107 0.       0.115421 0.016697 0.012504 0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.
 0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.
 0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.
 0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.
 0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.       0.      ]
  cumul_vjepa_var_order: shape=(100,)
    [0.372842 0.447634 0.535403 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721
 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721
 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721
 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721
 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721]
  cumul_clip_var_order: shape=(100,)
    [0.261256 0.417142 0.544249 0.544249 0.65967  0.676366 0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887
 0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887
 0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887
 0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887
 0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887 ]
  cumul_vjepa_sorted: shape=(100,)
    [0.372842 0.460612 0.535403 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721
 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721
 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721
 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721
 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721 0.535721]
  cumul_clip_sorted: shape=(100,)
    [0.261256 0.417142 0.544249 0.65967  0.676366 0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887
 0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887
 0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887
 0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887
 0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887  0.68887 ]
  vjepa_pca_var_ratio: shape=(100,)
    [0.170205 0.055267 0.050697 0.036616 0.035396 0.028826 0.027737 0.025041 0.021312 0.018787 0.017021 0.016604 0.015712 0.014239 0.013781 0.012509 0.012238 0.011715 0.010971 0.010133 0.009867 0.00944
 0.00884  0.008639 0.00843  0.008125 0.007995 0.007522 0.007438 0.007116 0.006636 0.006542 0.006279 0.005913 0.005747 0.005589 0.005311 0.004958 0.004889 0.004882 0.004751 0.004617 0.004455 0.004256
 0.004209 0.004175 0.004008 0.003804 0.00378  0.003633 0.003596 0.003544 0.003378 0.00334  0.003273 0.003173 0.003095 0.003047 0.002964 0.002861 0.002779 0.002733 0.002689 0.002622 0.002545 0.002501
 0.002418 0.002397 0.002225 0.002175 0.002145 0.002139 0.002095 0.002037 0.001969 0.001912 0.001899 0.001841 0.001798 0.001779 0.001703 0.001675 0.001642 0.001592 0.001564 0.001546 0.001536 0.001501
 0.00149  0.001448 0.001434 0.00139  0.001376 0.001368 0.001343 0.001335 0.001312 0.001265 0.001245 0.001234]
  clip_pca_var_ratio: shape=(100,)
    [0.082673 0.062611 0.051655 0.040069 0.034714 0.029342 0.02453  0.021204 0.019874 0.01597  0.014516 0.01421  0.013267 0.012747 0.011776 0.010788 0.01044  0.010067 0.009198 0.008906 0.008497 0.008306
 0.008001 0.007823 0.007691 0.007488 0.006665 0.006561 0.00611  0.005972 0.005914 0.005704 0.005536 0.005316 0.005178 0.005117 0.004924 0.0048   0.004652 0.004562 0.004419 0.004311 0.004176 0.004128
 0.004093 0.003913 0.003861 0.003825 0.003746 0.003656 0.003625 0.003536 0.003448 0.003348 0.003318 0.003255 0.003245 0.00314  0.003048 0.003015 0.002979 0.002906 0.002835 0.0028   0.002762 0.002728
 0.002687 0.002669 0.002612 0.00258  0.002545 0.002489 0.002459 0.002422 0.002403 0.002343 0.002341 0.002292 0.002256 0.002247 0.002223 0.002161 0.002153 0.002135 0.002108 0.002069 0.002035 0.001999
 0.001986 0.001984 0.001932 0.001922 0.001909 0.001874 0.001805 0.001802 0.001794 0.001729 0.001713 0.001707]
  sat_vjepa_var_order: shape=()
    3
  sat_clip_var_order: shape=()
    5
  sat_vjepa_sorted: shape=()
    3
  sat_clip_sorted: shape=()
    4

### Exp 11: PC x Emotion Correlation
Keys: ['corr_vjepa_emo', 'pval_vjepa_emo', 'pval_vjepa_emo_fdr', 'corr_clip_emo', 'pval_clip_emo', 'pval_clip_emo_fdr', 'corr_vjepa_avd', 'pval_vjepa_avd_fdr', 'corr_clip_avd', 'pval_clip_avd_fdr', 'emotion_labels', 'avd_labels', 'r2_vjepa', 'r2_clip', 'brain_pred_mask_vjepa', 'brain_pred_mask_clip', 'vjepa_var_ratio', 'clip_var_ratio']
  corr_vjepa_emo shape: (100, 34)
  PC1: [('Aesthetic appreciation', -0.3277), ('Annoyance', 0.3253), ('Calmness', -0.288), ('Amusement', 0.2626), ('Excitement', -0.2403)]
  PC2: [('Aesthetic appreciation', 0.3544), ('Excitement', 0.3276), ('Adoration', -0.2791), ('Relief', 0.2544), ('Romance', -0.2409)]
  PC3: [('Uncomfortable', -0.3034), ('Empathic pain', -0.2384), ('Guilt', 0.2369), ('Surprise', -0.1921), ('Amusement', 0.1526)]
  PC4: [('Amusement', 0.2186), ('Awe', -0.2167), ('Sadness', 0.1867), ('Boredom', 0.1808), ('Aesthetic appreciation', -0.1591)]
  PC5: [('Boredom', -0.1683), ('Sympathy', 0.1645), ('Surprise', 0.1586), ('Aesthetic appreciation', -0.1425), ('Entrancement', 0.1412)]
  PC6: [('Interest', -0.1645), ('Uncomfortable', 0.1496), ('Anxiety', -0.1474), ('Nostalgia', -0.115), ('Surprise', 0.1059)]
  PC7: [('Craving', -0.1689), ('Horror', -0.1255), ('Uncomfortable', -0.1135), ('Triumph', -0.1054), ('Nostalgia', 0.0985)]
  PC8: [('Boredom', -0.2177), ('Interest', 0.1789), ('Nostalgia', 0.152), ('Annoyance', 0.1506), ('Awe', 0.1475)]
  PC9: [('Uncomfortable', 0.1429), ('Interest', 0.1091), ('Anxiety', 0.1045), ('Annoyance', 0.0813), ('Sadness', -0.0746)]
  PC10: [('Uncomfortable', 0.131), ('Amusement', -0.1208), ('Excitement', 0.1122), ('Romance', -0.0976), ('Sadness', -0.0976)]
  brain_pred_mask_vjepa: [1 1 1 0 0 0 0 0 0 0]
  brain_pred_mask_clip: [1 1 1 0 1 1 1 0 0 0]
  V-JEPA2 PC x AVD (top 5 PCs):
    PC1: A=+0.1408 V=-0.1259 D=+0.0422
    PC2: A=+0.2254 V=-0.0823 D=-0.0234
    PC3: A=+0.0297 V=+0.0615 D=+0.0426
    PC4: A=-0.0498 V=+0.0231 D=+0.1154
    PC5: A=+0.0527 V=-0.0369 D=+0.0066

### Exp 12: Brain-pred subspace emotion decoding (34 cat)
Keys: ['target_names', 'emotion_labels', 'dim_labels', 'r2_pred_vjepa', 'r2_unpred_vjepa', 'r2_all_vjepa', 'pred_idx_vjepa', 'r2_pred_clip', 'r2_unpred_clip', 'r2_all_clip', 'pred_idx_clip']
  target_names: ['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom' 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement'
 'Excitement' 'Fear' 'Horror' 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy' 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt'
 'Arousal' 'Valence' 'Dominance']
  emotion_labels: ['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom' 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement'
 'Excitement' 'Fear' 'Horror' 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy' 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  dim_labels: ['Arousal' 'Valence' 'Dominance']
  r2_pred_vjepa: [0.0235 0.0805 0.3231 0.1159 0.0118 0.0611 0.0222 0.0308 0.0196 0.1361 0.     0.     0.0166 0.0088 0.0741 0.0024 0.2001 0.     0.057  0.0598 0.0028 0.0167 0.0576 0.0793 0.0094 0.0071 0.0313 0.045
 0.0059 0.0128 0.1715 0.1057 0.0293 0.0518 0.0651 0.0112 0.    ]
  r2_unpred_vjepa: [0.     0.2677 0.1687 0.1805 0.0512 0.166  0.2219 0.0487 0.0832 0.1284 0.0072 0.0204 0.3386 0.     0.0953 0.     0.1527 0.     0.0629 0.1963 0.     0.1318 0.072  0.1241 0.1832 0.     0.0852 0.2234
 0.0322 0.0306 0.3005 0.0678 0.     0.0518 0.0037 0.1562 0.    ]
  r2_all_vjepa: [2.7007e-03 3.5966e-01 5.5093e-01 3.2192e-01 6.7057e-02 2.3945e-01 2.5379e-01 8.3853e-02 1.2283e-01 3.1757e-01 9.4531e-03 2.0796e-02 3.6426e-01 0.0000e+00 1.8227e-01 6.5927e-03 3.9551e-01 0.0000e+00
 1.4472e-01 2.6669e-01 0.0000e+00 1.5615e-01 1.5515e-01 2.2346e-01 1.9750e-01 0.0000e+00 1.2214e-01 2.7627e-01 4.3999e-02 4.6547e-02 4.9898e-01 1.8283e-01 2.4083e-02 1.5171e-01 8.8923e-02 1.8167e-01
 3.8625e-04]
  pred_idx_vjepa: [0 1 2]
  r2_pred_clip: [0.0266 0.1424 0.4473 0.3397 0.1818 0.2036 0.2096 0.0913 0.1011 0.1655 0.0291 0.0493 0.1482 0.0847 0.1964 0.0564 0.2866 0.0385 0.1709 0.2536 0.0289 0.21   0.1818 0.1236 0.1922 0.0544 0.1058 0.3308
 0.1959 0.0436 0.5379 0.1882 0.103  0.1211 0.0621 0.2706 0.0565]
  r2_unpred_clip: [0.0308 0.3933 0.1468 0.0913 0.0325 0.1609 0.1493 0.0242 0.0512 0.1442 0.0545 0.     0.4409 0.     0.1483 0.0112 0.1364 0.     0.0085 0.1525 0.     0.0699 0.0356 0.2418 0.2808 0.0405 0.0099 0.2437
 0.0632 0.029  0.1367 0.0534 0.0609 0.0148 0.0585 0.18   0.    ]
  r2_all_clip: [0.0695 0.5462 0.6505 0.4711 0.2321 0.392  0.385  0.1281 0.1738 0.3611 0.0934 0.0595 0.6394 0.0542 0.3671 0.0774 0.4663 0.0123 0.2083 0.43   0.0094 0.2999 0.2616 0.3879 0.5251 0.1109 0.126  0.6074
 0.2795 0.0767 0.7275 0.26   0.1764 0.2078 0.1355 0.4787 0.0639]
  pred_idx_clip: [0 1 2 4 5 6]

### Exp 13: Vision/Semantic confound control
Keys: ['source_names', 'model_names', 'rsa_original', 'rsa_partial', 'rsa_pvalue', 'emotion_labels', 'dim_labels', 'target_names', 'pred_idx_vjepa', 'pred_idx_clip', 'r2_original_vjepa', 'r2_partial_vjepa', 'r2_original_clip', 'r2_partial_clip']
  source_names: ['Brain-JEPA' 'Raw fMRI']
  model_names: ['V-JEPA2' 'CLIP']
  emotion_labels: ['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom' 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement'
 'Excitement' 'Fear' 'Horror' 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy' 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  dim_labels: ['Arousal' 'Valence' 'Dominance']
  target_names: ['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom' 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement'
 'Excitement' 'Fear' 'Horror' 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy' 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt'
 'Arousal' 'Valence' 'Dominance']
  pred_idx_vjepa: [0 1 2]
  pred_idx_clip: [0 1 2 4 5 6]
  r2_original_vjepa: [0.0235 0.0805 0.3231 0.1159 0.0118 0.0611 0.0222 0.0308 0.0196 0.1361 0.     0.     0.0166 0.0088 0.0741 0.0024 0.2001 0.     0.057  0.0598 0.0028 0.0167 0.0576 0.0793 0.0094 0.0071 0.0313 0.045
 0.0059 0.0128 0.1715 0.1057 0.0293 0.0518 0.0651 0.0112 0.    ]
  r2_partial_vjepa: [0.     0.0072 0.0515 0.0042 0.     0.0004 0.     0.     0.     0.061  0.     0.     0.0053 0.     0.     0.     0.0097 0.     0.0068 0.002  0.     0.     0.     0.     0.0027 0.003  0.     0.
 0.0019 0.0055 0.0028 0.0077 0.0022 0.     0.0088 0.     0.    ]
  r2_original_clip: [0.0266 0.1424 0.4473 0.3397 0.1818 0.2036 0.2096 0.0913 0.1011 0.1655 0.0291 0.0493 0.1482 0.0847 0.1964 0.0564 0.2866 0.0385 0.1709 0.2536 0.0289 0.21   0.1818 0.1236 0.1922 0.0544 0.1058 0.3308
 0.1959 0.0436 0.5379 0.1882 0.103  0.1211 0.0621 0.2706 0.0565]
  r2_partial_clip: [0.     0.     0.0935 0.0494 0.0145 0.0145 0.     0.     0.     0.0564 0.     0.     0.     0.     0.0038 0.002  0.0259 0.0053 0.0323 0.0235 0.     0.     0.0192 0.0028 0.0162 0.0031 0.     0.041
 0.0306 0.     0.0095 0.0087 0.0034 0.     0.     0.0258 0.    ]

### Exp 14: Robustness
Keys: ['thresholds', 'n_pred_vjepa', 'n_pred_clip', 'exp12_mean_cat_vjepa', 'exp12_mean_dim_vjepa', 'exp12_mean_cat_clip', 'exp12_mean_dim_clip', 'exp13_partial_cat_vjepa', 'exp13_partial_dim_vjepa', 'exp13_partial_cat_clip', 'exp13_partial_dim_clip', 'exp12_boot_vjepa', 'exp12_boot_clip', 'exp13_boot_vjepa', 'exp13_boot_clip', 'ci_exp12_vjepa', 'ci_exp12_clip', 'ci_exp13_vjepa', 'ci_exp13_clip', 'confound_sets', 'emotion_labels', 'dim_labels', 'target_names', 'confound_ablation_r2_vjepa', 'confound_ablation_r2_clip', 'confound_ablation_rsa']
  thresholds: [0.005 0.01  0.02  0.03  0.05 ]
  n_pred_vjepa: [3 3 3 3 3]
  n_pred_clip: [6 6 4 4 4]
  exp12_mean_cat_vjepa: [0.055 0.055 0.055 0.055 0.055]
  exp12_mean_dim_vjepa: [0.0254 0.0254 0.0254 0.0254 0.0254]
  exp12_mean_cat_clip: [0.1659 0.1659 0.1142 0.1142 0.1142]
  exp12_mean_dim_clip: [0.1297 0.1297 0.0413 0.0413 0.0413]
  exp13_partial_cat_vjepa: [0.0051 0.0051 0.0051 0.0051 0.0051]
  exp13_partial_dim_vjepa: [0.0029 0.0029 0.0029 0.0029 0.0029]
  exp13_partial_cat_clip: [0.0134 0.0134 0.0111 0.0111 0.0111]
  exp13_partial_dim_clip: [0.0086 0.0086 0.0011 0.0011 0.0011]
  ci_exp12_vjepa: [[0.0551 0.0232 1.5268]
 [0.0584 0.0298 1.9773]
 [0.0626 0.0389 2.5044]]
  ci_exp12_clip: [[0.1624 0.1162 1.1512]
 [0.17   0.136  1.2559]
 [0.1774 0.1508 1.4086]]
  ci_exp13_vjepa: [[9.6558e-04 0.0000e+00 2.6080e-01]
 [3.9218e-03 0.0000e+00 1.2813e+07]
 [8.7862e-03 1.3707e-02 7.8670e+07]]
  ci_exp13_clip: [[1.6210e-03 0.0000e+00 2.4442e-01]
 [5.6089e-03 0.0000e+00 2.5682e+07]
 [1.0142e-02 1.9723e-02 9.7191e+07]]
  confound_sets: ['vision_only' 'semantic_only' 'vision_semantic']
  emotion_labels: ['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom' 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement'
 'Excitement' 'Fear' 'Horror' 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy' 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  dim_labels: ['Arousal' 'Valence' 'Dominance']
  target_names: ['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom' 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement'
 'Excitement' 'Fear' 'Horror' 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy' 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt'
 'Arousal' 'Valence' 'Dominance']
  confound_ablation_rsa: ["{'vision_only': {'Brain-JEPA': {'V-JEPA2': (np.float64(-0.007062931282308947), np.float64(-0.0078071694043384005)), 'CLIP': (np.float64(-0.06971020476765742), np.float64(-0.07021268820705448))}, 'Raw fMRI': {'V-JEPA2': (np.float64(0.09561730537876985), np.float64(0.08463917878466468)), 'CLIP': (np.float64(0.08863207203584224), np.float64(0.07941565968107915))}}, 'semantic_only': {'Brain-JEPA': {'V-JEPA2': (np.float64(-0.007062931282308947), np.float64(-0.003131982801696355)), 'CLIP': (np.float64(-0.06971020476765742), np.float64(-0.06809515756786676))}, 'Raw fMRI': {'V-JEPA2': (np.float64(0.09561730537876985), np.float64(0.08148384230808607)), 'CLIP': (np.float64(0.08863207203584224), np.float64(0.07427900811700669))}}, 'vision_semantic': {'Brain-JEPA': {'V-JEPA2': (np.float64(-0.007062931282308947), np.float64(-0.004500470034535597)), 'CLIP': (np.float64(-0.06971020476765742), np.float64(-0.06855760166379064))}, 'Raw fMRI': {'V-JEPA2': (np.float64(0.09561730537876985), np.float64(0.07762574421543185)), 'CLIP': (np.float64(0.08863207203584224), np.float64(0.07174453425766851))}}}"]

### Exp 15: Subject stability
Keys: ['subj_r2_vjepa', 'subj_r2_clip', 'subj_mask_vjepa', 'subj_mask_clip', 'mean_mask_vjepa', 'mean_mask_clip', 'jaccard_vjepa', 'jaccard_clip', 'selection_freq_vjepa', 'selection_freq_clip', 'resample_summary_vjepa', 'resample_summary_clip', 'top5_freq_vjepa', 'top5_freq_clip', 'alpha', 'exp12_cat_vjepa', 'exp12_dim_vjepa', 'exp12_cat_clip', 'exp12_dim_clip', 'exp13_cat_vjepa', 'exp13_dim_vjepa', 'exp13_cat_clip', 'exp13_dim_clip', 'emotion_labels', 'dim_labels']
  jaccard_vjepa: [[1.  0.5 0.5 1.  1. ]
 [0.5 1.  1.  0.5 0.5]
 [0.5 1.  1.  0.5 0.5]
 [1.  0.5 0.5 1.  1. ]
 [1.  0.5 0.5 1.  1. ]]
  jaccard_clip: [[1.  0.5 0.5 1.  1. ]
 [0.5 1.  1.  0.5 0.5]
 [0.5 1.  1.  0.5 0.5]
 [1.  0.5 0.5 1.  1. ]
 [1.  0.5 0.5 1.  1. ]]
  top5_freq_vjepa: [  0   0 100  79   0   0   0   0   0  83   0   0   0   0   0   0 100   0   0   0   0   0   0   1   0   0   0   0   0   0 100  37   0   0]
  top5_freq_clip: [  0   0 100 100   0   0   0   0   0   0   0   0   0   0   0   0  94   0   0  13   0   0   0   0   0   0   0  93   0   0 100   0   0   0]
  alpha: [  0.1   1.   10.  100. ]
  exp12_cat_vjepa: [0.055  0.055  0.055  0.0551]
  exp12_dim_vjepa: [0.0254 0.0254 0.0254 0.0254]
  exp12_cat_clip: [0.1659 0.1659 0.166  0.1661]
  exp12_dim_clip: [0.1297 0.1297 0.1298 0.1296]
  exp13_cat_vjepa: [0.0051 0.0051 0.0051 0.0053]
  exp13_dim_vjepa: [0.0029 0.0029 0.003  0.0031]
  exp13_cat_clip: [0.0134 0.0134 0.0135 0.0139]
  exp13_dim_clip: [0.0086 0.0086 0.0086 0.0089]
  emotion_labels: ['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom' 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement'
 'Excitement' 'Fear' 'Horror' 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy' 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  dim_labels: ['Arousal' 'Valence' 'Dominance']

### Exp 16: Incremental baseline
Keys: ['target_names', 'emotion_labels', 'dim_labels', 'pred_idx_vjepa', 'pred_idx_clip', 'r2_baseline', 'r2_vjepa_only', 'r2_clip_only', 'r2_combined_vjepa', 'r2_combined_clip', 'delta_vjepa', 'delta_clip']
  target_names: ['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom' 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement'
 'Excitement' 'Fear' 'Horror' 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy' 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt'
 'Arousal' 'Valence' 'Dominance']
  emotion_labels: ['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom' 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement'
 'Excitement' 'Fear' 'Horror' 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy' 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  dim_labels: ['Arousal' 'Valence' 'Dominance']
  pred_idx_vjepa: [0 1 2]
  pred_idx_clip: [0 1 2 4 5 6]
  r2_baseline: [0.     0.1427 0.3549 0.0114 0.     0.     0.     0.     0.     0.     0.     0.     0.3873 0.     0.2008 0.     0.0907 0.     0.     0.0632 0.     0.2984 0.     0.     0.     0.     0.     0.4791
 0.     0.     0.6769 0.     0.     0.     0.     0.2974 0.    ]
  r2_vjepa_only: [0.0235 0.0805 0.3231 0.1159 0.0118 0.0611 0.0222 0.0308 0.0196 0.1361 0.     0.     0.0166 0.0088 0.0741 0.0024 0.2001 0.     0.057  0.0598 0.0028 0.0167 0.0576 0.0793 0.0094 0.0071 0.0313 0.045
 0.0059 0.0128 0.1715 0.1057 0.0293 0.0518 0.0651 0.0112 0.    ]
  r2_clip_only: [0.0266 0.1424 0.4473 0.3397 0.1818 0.2036 0.2096 0.0913 0.1011 0.1655 0.0291 0.0493 0.1482 0.0847 0.1964 0.0564 0.2866 0.0385 0.1709 0.2536 0.0289 0.21   0.1818 0.1236 0.1922 0.0544 0.1058 0.3308
 0.1959 0.0436 0.5379 0.1882 0.103  0.1211 0.0621 0.2706 0.0565]
  r2_combined_vjepa: [0.     0.1546 0.3936 0.0178 0.     0.     0.     0.     0.     0.     0.     0.     0.3911 0.     0.2    0.     0.1049 0.     0.     0.0691 0.     0.2951 0.     0.     0.     0.     0.     0.4776
 0.     0.     0.6773 0.     0.     0.     0.     0.2979 0.    ]
  r2_combined_clip: [0.     0.1518 0.4115 0.0654 0.     0.     0.     0.     0.     0.     0.     0.     0.3881 0.     0.2176 0.     0.1165 0.     0.     0.085  0.     0.2976 0.     0.     0.0166 0.     0.     0.4976
 0.     0.     0.6796 0.     0.     0.     0.     0.3212 0.    ]
  delta_vjepa: [ 0.      0.0118  0.0387  0.0063  0.      0.      0.      0.      0.      0.      0.      0.      0.0038  0.     -0.0008  0.      0.0141  0.      0.      0.0059  0.     -0.0033  0.      0.
  0.      0.      0.     -0.0015  0.      0.      0.0004  0.      0.      0.      0.      0.0004  0.    ]
  delta_clip: [ 0.      0.009   0.0567  0.054   0.      0.      0.      0.      0.      0.      0.      0.      0.0008  0.      0.0168  0.      0.0258  0.      0.      0.0218  0.     -0.0007  0.      0.
  0.0166  0.      0.      0.0185  0.      0.      0.0027  0.      0.      0.      0.      0.0238  0.    ]

### Exp 17: AV2D comparison (brain-pred vs full, 36 targets)
Keys: ['metadata_path', 'fmri_path', 'target_names', 'emotion_labels', 'dim_labels', 'dim_cols', 'pred_idx_vjepa', 'pred_idx_clip', 'r2_pred_vjepa', 'r2_unpred_vjepa', 'r2_all_vjepa', 'r2_pred_clip', 'r2_unpred_clip', 'r2_all_clip', 'raw_k_values', 'raw_mean_cat', 'raw_mean_dim', 'raw_cat_dim_ratio', 'r2_raw_k27', 'r2_raw_full']
  metadata_path: ['/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_14dims.csv']
  fmri_path: ['/pscratch/sd/s/sjmoon/EmoFM/raw_fmri_results/fmri_raw.npy']
  target_names: ['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom' 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement'
 'Excitement' 'Fear' 'Horror' 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy' 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt'
 'Arousal' 'Valence']
  emotion_labels: ['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom' 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement'
 'Excitement' 'Fear' 'Horror' 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy' 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  dim_labels: ['Arousal' 'Valence']
  dim_cols: ['arousal_score' 'valence_score']
  pred_idx_vjepa: [0 1 2]
  pred_idx_clip: [0 1 2 4 5 6]
  r2_pred_vjepa: [0.0235 0.0805 0.3231 0.1159 0.0118 0.0611 0.0222 0.0308 0.0196 0.1361 0.     0.     0.0166 0.0088 0.0741 0.0024 0.2001 0.     0.057  0.0598 0.0028 0.0167 0.0576 0.0793 0.0094 0.0071 0.0313 0.045
 0.0059 0.0128 0.1715 0.1057 0.0293 0.0518 0.0651 0.0112]
  r2_unpred_vjepa: [0.     0.2677 0.1687 0.1805 0.0512 0.166  0.2219 0.0487 0.0832 0.1284 0.0072 0.0204 0.3386 0.     0.0953 0.     0.1527 0.     0.0629 0.1963 0.     0.1318 0.072  0.1241 0.1832 0.     0.0852 0.2234
 0.0322 0.0306 0.3005 0.0678 0.     0.0518 0.0037 0.1562]
  r2_all_vjepa: [0.0027 0.3597 0.5509 0.3219 0.0671 0.2394 0.2538 0.0839 0.1228 0.3176 0.0095 0.0208 0.3643 0.     0.1823 0.0066 0.3955 0.     0.1447 0.2667 0.     0.1561 0.1552 0.2235 0.1975 0.     0.1221 0.2763
 0.044  0.0465 0.499  0.1828 0.0241 0.1517 0.0889 0.1817]
  r2_pred_clip: [0.0266 0.1424 0.4473 0.3397 0.1818 0.2036 0.2096 0.0913 0.1011 0.1655 0.0291 0.0493 0.1482 0.0847 0.1964 0.0564 0.2866 0.0385 0.1709 0.2536 0.0289 0.21   0.1818 0.1236 0.1922 0.0544 0.1058 0.3308
 0.1959 0.0436 0.5379 0.1882 0.103  0.1211 0.0621 0.2706]
  r2_unpred_clip: [0.0308 0.3933 0.1468 0.0913 0.0325 0.1609 0.1493 0.0242 0.0512 0.1442 0.0545 0.     0.4409 0.     0.1483 0.0112 0.1364 0.     0.0085 0.1525 0.     0.0699 0.0356 0.2418 0.2808 0.0405 0.0099 0.2437
 0.0632 0.029  0.1367 0.0534 0.0609 0.0148 0.0585 0.18  ]
  r2_all_clip: [0.0695 0.5462 0.6505 0.4711 0.2321 0.392  0.385  0.1281 0.1738 0.3611 0.0934 0.0595 0.6394 0.0542 0.3671 0.0774 0.4663 0.0123 0.2083 0.43   0.0094 0.2999 0.2616 0.3879 0.5251 0.1109 0.126  0.6074
 0.2795 0.0767 0.7275 0.26   0.1764 0.2078 0.1355 0.4787]
  raw_k_values: [  3   5   7  10  15  20  25  27  30  34  40  50  75 100]
  raw_mean_cat: [0.033  0.0523 0.0683 0.0865 0.0921 0.1018 0.1061 0.1075 0.1088 0.1102 0.1112 0.114  0.1166 0.1154]
  raw_mean_dim: [0.0382 0.0563 0.0709 0.1142 0.1138 0.1302 0.1396 0.1431 0.1466 0.1489 0.147  0.1517 0.1605 0.1609]
  raw_cat_dim_ratio: [0.8653 0.9277 0.9633 0.7569 0.8091 0.7814 0.7601 0.7514 0.7422 0.7396 0.7565 0.7513 0.726  0.7177]
  r2_raw_k27: [0.0276 0.1391 0.2335 0.2126 0.0476 0.1889 0.134  0.0728 0.0836 0.1131 0.0761 0.0115 0.072  0.0222 0.267  0.0951 0.2107 0.     0.0662 0.1857 0.     0.1319 0.127  0.1288 0.1161 0.0203 0.0823 0.1102
 0.0418 0.0481 0.3226 0.1789 0.0321 0.0571 0.0681 0.2181]
  r2_raw_full: [0.     0.     0.1351 0.0774 0.     0.051  0.     0.     0.     0.     0.     0.     0.     0.     0.1205 0.     0.1107 0.     0.     0.0626 0.     0.0021 0.     0.     0.     0.     0.     0.
 0.     0.     0.2919 0.0265 0.     0.     0.     0.1461]

### Exp 18: Subject-wise claim check
Keys: ['row_labels', 'ontology_order', 'model_order', 'emotion_labels', 'dim3_labels', 'dim14_labels', 'dim2_labels', 'r2_pc_vjepa', 'r2_pc_clip', 'mask_vjepa', 'mask_clip', 'pc_count_vjepa', 'pc_count_clip', 'r2_3d_vjepa', 'r2_3d_clip', 'r2_14d_vjepa', 'r2_14d_clip', 'r2_2d_vjepa', 'r2_2d_clip', 'agreement_3d_vjepa', 'agreement_3d_clip', 'agreement_14d_vjepa', 'agreement_14d_clip', 'agreement_2d_vjepa', 'agreement_2d_clip', 'agreement_rate_3d_vjepa', 'agreement_rate_3d_clip', 'agreement_rate_14d_vjepa', 'agreement_rate_14d_clip', 'agreement_rate_2d_vjepa', 'agreement_rate_2d_clip']
  row_labels: shape=(6,)
    ['mean' 'subj1' 'subj2' 'subj3' 'subj4' 'subj5']
  ontology_order: shape=(3,)
    ['3D' '14D' '2D']
  model_order: shape=(2,)
    ['vjepa' 'clip']
  emotion_labels: shape=(34,)
    ['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom' 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement'
 'Excitement' 'Fear' 'Horror' 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy' 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  dim3_labels: shape=(3,)
    ['Arousal' 'Valence' 'Dominance']
  dim14_labels: shape=(14,)
    ['Approach' 'Arousal' 'Attention' 'Certainty' 'Commitment' 'Control' 'Dominance' 'Effort' 'Fairness' 'Identity' 'Obstruction' 'Safety' 'Upswing' 'Valence']
  dim2_labels: shape=(2,)
    ['Arousal' 'Valence']
  pc_count_vjepa: shape=(6,)
    [3 1 2 2 1 1]
  pc_count_clip: shape=(6,)
    [6 1 2 2 1 1]
  r2_3d_vjepa: shape=(6, 37)
    row0: [0.0235 0.0805 0.3231 0.1159 0.0118 0.0611 0.0222 0.0308 0.0196 0.1361 0.     0.     0.0166 0.0088 0.0741 0.0024 0.2001 0.     0.057  0.0598 0.0028 0.0167 0.0576 0.0793 0.0094 0.0071 0.0313 0.045
 0.0059 0.0128 0.1715 0.1057 0.0293 0.0518 0.0651 0.0112 0.    ]
    row1: [0.     0.0006 0.1368 0.051  0.0081 0.0333 0.     0.     0.0148 0.0954 0.     0.     0.01   0.     0.     0.0022 0.0619 0.     0.0341 0.0321 0.     0.0033 0.     0.0135 0.0056 0.     0.0113 0.0084
 0.0008 0.0029 0.0328 0.077  0.0189 0.0149 0.0161 0.004  0.    ]
    row2: [2.2101e-02 8.4905e-03 1.6458e-01 6.7348e-02 1.1766e-02 3.8673e-02 2.5520e-05 2.5134e-03 1.8129e-02 1.1349e-01 0.0000e+00 0.0000e+00 1.6926e-02 5.6261e-03 6.1031e-02 3.0095e-03 6.8212e-02 0.0000e+00
 4.5418e-02 3.6435e-02 0.0000e+00 6.1303e-03 0.0000e+00 1.2885e-02 8.0425e-03 4.0967e-03 2.4104e-02 3.2113e-02 4.3244e-03 1.1708e-02 1.5261e-01 1.0086e-01 2.2468e-02 5.2767e-02 1.6409e-02 8.3975e-03
 0.0000e+00]
    row3: [2.2101e-02 8.4905e-03 1.6458e-01 6.7348e-02 1.1766e-02 3.8673e-02 2.5520e-05 2.5134e-03 1.8129e-02 1.1349e-01 0.0000e+00 0.0000e+00 1.6926e-02 5.6261e-03 6.1031e-02 3.0095e-03 6.8212e-02 0.0000e+00
 4.5418e-02 3.6435e-02 0.0000e+00 6.1303e-03 0.0000e+00 1.2885e-02 8.0425e-03 4.0967e-03 2.4104e-02 3.2113e-02 4.3244e-03 1.1708e-02 1.5261e-01 1.0086e-01 2.2468e-02 5.2767e-02 1.6409e-02 8.3975e-03
 0.0000e+00]
    row4: [0.     0.0006 0.1368 0.051  0.0081 0.0333 0.     0.     0.0148 0.0954 0.     0.     0.01   0.     0.     0.0022 0.0619 0.     0.0341 0.0321 0.     0.0033 0.     0.0135 0.0056 0.     0.0113 0.0084
 0.0008 0.0029 0.0328 0.077  0.0189 0.0149 0.0161 0.004  0.    ]
    row5: [0.     0.0006 0.1368 0.051  0.0081 0.0333 0.     0.     0.0148 0.0954 0.     0.     0.01   0.     0.     0.0022 0.0619 0.     0.0341 0.0321 0.     0.0033 0.     0.0135 0.0056 0.     0.0113 0.0084
 0.0008 0.0029 0.0328 0.077  0.0189 0.0149 0.0161 0.004  0.    ]
  r2_3d_clip: shape=(6, 37)
    row0: [0.0266 0.1424 0.4473 0.3397 0.1818 0.2036 0.2096 0.0913 0.1011 0.1655 0.0291 0.0493 0.1482 0.0847 0.1964 0.0564 0.2866 0.0385 0.1709 0.2536 0.0289 0.21   0.1818 0.1236 0.1922 0.0544 0.1058 0.3308
 0.1959 0.0436 0.5379 0.1882 0.103  0.1211 0.0621 0.2706 0.0565]
    row1: [0.     0.0068 0.099  0.0781 0.0348 0.0987 0.0092 0.0052 0.0372 0.0375 0.     0.     0.033  0.0115 0.     0.0211 0.056  0.0152 0.0023 0.1061 0.0016 0.0302 0.     0.     0.02   0.     0.0747 0.1371
 0.0305 0.     0.1451 0.177  0.0502 0.0126 0.0082 0.0372 0.    ]
    row2: [0.     0.0756 0.3939 0.1789 0.0345 0.1438 0.0813 0.0673 0.0361 0.118  0.     0.     0.0368 0.0123 0.0133 0.0215 0.2226 0.0154 0.0077 0.1589 0.0017 0.0369 0.0912 0.0636 0.0241 0.     0.0775 0.1834
 0.033  0.     0.2649 0.1764 0.0515 0.0119 0.0202 0.0406 0.0009]
    row3: [0.     0.0756 0.3939 0.1789 0.0345 0.1438 0.0813 0.0673 0.0361 0.118  0.     0.     0.0368 0.0123 0.0133 0.0215 0.2226 0.0154 0.0077 0.1589 0.0017 0.0369 0.0912 0.0636 0.0241 0.     0.0775 0.1834
 0.033  0.     0.2649 0.1764 0.0515 0.0119 0.0202 0.0406 0.0009]
    row4: [0.     0.0068 0.099  0.0781 0.0348 0.0987 0.0092 0.0052 0.0372 0.0375 0.     0.     0.033  0.0115 0.     0.0211 0.056  0.0152 0.0023 0.1061 0.0016 0.0302 0.     0.     0.02   0.     0.0747 0.1371
 0.0305 0.     0.1451 0.177  0.0502 0.0126 0.0082 0.0372 0.    ]
    row5: [0.     0.0068 0.099  0.0781 0.0348 0.0987 0.0092 0.0052 0.0372 0.0375 0.     0.     0.033  0.0115 0.     0.0211 0.056  0.0152 0.0023 0.1061 0.0016 0.0302 0.     0.     0.02   0.     0.0747 0.1371
 0.0305 0.     0.1451 0.177  0.0502 0.0126 0.0082 0.0372 0.    ]
  r2_14d_vjepa: shape=(6, 48)
    row0: [0.0235 0.0805 0.3231 0.1159 0.0118 0.0611 0.0222 0.0308 0.0196 0.1361 0.     0.     0.0166 0.0088 0.0741 0.0024 0.2001 0.     0.057  0.0598 0.0028 0.0167 0.0576 0.0793 0.0094 0.0071 0.0313 0.045
 0.0059 0.0128 0.1715 0.1057 0.0293 0.0518 0.0266 0.0651 0.048  0.0256 0.0653 0.0443 0.     0.024  0.007  0.0287 0.0147 0.0685 0.     0.0112]
    row1: [0.     0.0006 0.1368 0.051  0.0081 0.0333 0.     0.     0.0148 0.0954 0.     0.     0.01   0.     0.     0.0022 0.0619 0.     0.0341 0.0321 0.     0.0033 0.     0.0135 0.0056 0.     0.0113 0.0084
 0.0008 0.0029 0.0328 0.077  0.0189 0.0149 0.0218 0.0161 0.     0.0165 0.0075 0.0301 0.     0.0059 0.0072 0.     0.009  0.0426 0.     0.004 ]
    row2: [2.2101e-02 8.4905e-03 1.6458e-01 6.7348e-02 1.1766e-02 3.8673e-02 2.5520e-05 2.5134e-03 1.8129e-02 1.1349e-01 0.0000e+00 0.0000e+00 1.6926e-02 5.6261e-03 6.1031e-02 3.0095e-03 6.8212e-02 0.0000e+00
 4.5418e-02 3.6435e-02 0.0000e+00 6.1303e-03 0.0000e+00 1.2885e-02 8.0425e-03 4.0967e-03 2.4104e-02 3.2113e-02 4.3244e-03 1.1708e-02 1.5261e-01 1.0086e-01 2.2468e-02 5.2767e-02 2.1005e-02 1.6409e-02
 2.0518e-02 1.4344e-02 7.6130e-03 3.1308e-02 0.0000e+00 1.8116e-02 4.9648e-03 0.0000e+00 9.0673e-03 4.2883e-02 0.0000e+00 8.3975e-03]
    row3: [2.2101e-02 8.4905e-03 1.6458e-01 6.7348e-02 1.1766e-02 3.8673e-02 2.5520e-05 2.5134e-03 1.8129e-02 1.1349e-01 0.0000e+00 0.0000e+00 1.6926e-02 5.6261e-03 6.1031e-02 3.0095e-03 6.8212e-02 0.0000e+00
 4.5418e-02 3.6435e-02 0.0000e+00 6.1303e-03 0.0000e+00 1.2885e-02 8.0425e-03 4.0967e-03 2.4104e-02 3.2113e-02 4.3244e-03 1.1708e-02 1.5261e-01 1.0086e-01 2.2468e-02 5.2767e-02 2.1005e-02 1.6409e-02
 2.0518e-02 1.4344e-02 7.6130e-03 3.1308e-02 0.0000e+00 1.8116e-02 4.9648e-03 0.0000e+00 9.0673e-03 4.2883e-02 0.0000e+00 8.3975e-03]
    row4: [0.     0.0006 0.1368 0.051  0.0081 0.0333 0.     0.     0.0148 0.0954 0.     0.     0.01   0.     0.     0.0022 0.0619 0.     0.0341 0.0321 0.     0.0033 0.     0.0135 0.0056 0.     0.0113 0.0084
 0.0008 0.0029 0.0328 0.077  0.0189 0.0149 0.0218 0.0161 0.     0.0165 0.0075 0.0301 0.     0.0059 0.0072 0.     0.009  0.0426 0.     0.004 ]
    row5: [0.     0.0006 0.1368 0.051  0.0081 0.0333 0.     0.     0.0148 0.0954 0.     0.     0.01   0.     0.     0.0022 0.0619 0.     0.0341 0.0321 0.     0.0033 0.     0.0135 0.0056 0.     0.0113 0.0084
 0.0008 0.0029 0.0328 0.077  0.0189 0.0149 0.0218 0.0161 0.     0.0165 0.0075 0.0301 0.     0.0059 0.0072 0.     0.009  0.0426 0.     0.004 ]
  r2_14d_clip: shape=(6, 48)
    row0: [0.0266 0.1424 0.4473 0.3397 0.1818 0.2036 0.2096 0.0913 0.1011 0.1655 0.0291 0.0493 0.1482 0.0847 0.1964 0.0564 0.2866 0.0385 0.1709 0.2536 0.0289 0.21   0.1818 0.1236 0.1922 0.0544 0.1058 0.3308
 0.1959 0.0436 0.5379 0.1882 0.103  0.1211 0.2473 0.0621 0.0575 0.1748 0.1071 0.3156 0.0565 0.1882 0.2771 0.116  0.1441 0.3259 0.1793 0.2706]
    row1: [0.     0.0068 0.099  0.0781 0.0348 0.0987 0.0092 0.0052 0.0372 0.0375 0.     0.     0.033  0.0115 0.     0.0211 0.056  0.0152 0.0023 0.1061 0.0016 0.0302 0.     0.     0.02   0.     0.0747 0.1371
 0.0305 0.     0.1451 0.177  0.0502 0.0126 0.0696 0.0082 0.0116 0.0623 0.0114 0.1158 0.     0.0117 0.061  0.0022 0.0268 0.1346 0.0004 0.0372]
    row2: [0.     0.0756 0.3939 0.1789 0.0345 0.1438 0.0813 0.0673 0.0361 0.118  0.     0.     0.0368 0.0123 0.0133 0.0215 0.2226 0.0154 0.0077 0.1589 0.0017 0.0369 0.0912 0.0636 0.0241 0.     0.0775 0.1834
 0.033  0.     0.2649 0.1764 0.0515 0.0119 0.0781 0.0202 0.0371 0.0804 0.0651 0.1296 0.0009 0.0137 0.066  0.0532 0.0323 0.1717 0.     0.0406]
    row3: [0.     0.0756 0.3939 0.1789 0.0345 0.1438 0.0813 0.0673 0.0361 0.118  0.     0.     0.0368 0.0123 0.0133 0.0215 0.2226 0.0154 0.0077 0.1589 0.0017 0.0369 0.0912 0.0636 0.0241 0.     0.0775 0.1834
 0.033  0.     0.2649 0.1764 0.0515 0.0119 0.0781 0.0202 0.0371 0.0804 0.0651 0.1296 0.0009 0.0137 0.066  0.0532 0.0323 0.1717 0.     0.0406]
    row4: [0.     0.0068 0.099  0.0781 0.0348 0.0987 0.0092 0.0052 0.0372 0.0375 0.     0.     0.033  0.0115 0.     0.0211 0.056  0.0152 0.0023 0.1061 0.0016 0.0302 0.     0.     0.02   0.     0.0747 0.1371
 0.0305 0.     0.1451 0.177  0.0502 0.0126 0.0696 0.0082 0.0116 0.0623 0.0114 0.1158 0.     0.0117 0.061  0.0022 0.0268 0.1346 0.0004 0.0372]
    row5: [0.     0.0068 0.099  0.0781 0.0348 0.0987 0.0092 0.0052 0.0372 0.0375 0.     0.     0.033  0.0115 0.     0.0211 0.056  0.0152 0.0023 0.1061 0.0016 0.0302 0.     0.     0.02   0.     0.0747 0.1371
 0.0305 0.     0.1451 0.177  0.0502 0.0126 0.0696 0.0082 0.0116 0.0623 0.0114 0.1158 0.     0.0117 0.061  0.0022 0.0268 0.1346 0.0004 0.0372]
  r2_2d_vjepa: shape=(6, 36)
    row0: [0.0235 0.0805 0.3231 0.1159 0.0118 0.0611 0.0222 0.0308 0.0196 0.1361 0.     0.     0.0166 0.0088 0.0741 0.0024 0.2001 0.     0.057  0.0598 0.0028 0.0167 0.0576 0.0793 0.0094 0.0071 0.0313 0.045
 0.0059 0.0128 0.1715 0.1057 0.0293 0.0518 0.0651 0.0112]
    row1: [0.     0.0006 0.1368 0.051  0.0081 0.0333 0.     0.     0.0148 0.0954 0.     0.     0.01   0.     0.     0.0022 0.0619 0.     0.0341 0.0321 0.     0.0033 0.     0.0135 0.0056 0.     0.0113 0.0084
 0.0008 0.0029 0.0328 0.077  0.0189 0.0149 0.0161 0.004 ]
    row2: [2.2101e-02 8.4905e-03 1.6458e-01 6.7348e-02 1.1766e-02 3.8673e-02 2.5520e-05 2.5134e-03 1.8129e-02 1.1349e-01 0.0000e+00 0.0000e+00 1.6926e-02 5.6261e-03 6.1031e-02 3.0095e-03 6.8212e-02 0.0000e+00
 4.5418e-02 3.6435e-02 0.0000e+00 6.1303e-03 0.0000e+00 1.2885e-02 8.0425e-03 4.0967e-03 2.4104e-02 3.2113e-02 4.3244e-03 1.1708e-02 1.5261e-01 1.0086e-01 2.2468e-02 5.2767e-02 1.6409e-02 8.3975e-03]
    row3: [2.2101e-02 8.4905e-03 1.6458e-01 6.7348e-02 1.1766e-02 3.8673e-02 2.5520e-05 2.5134e-03 1.8129e-02 1.1349e-01 0.0000e+00 0.0000e+00 1.6926e-02 5.6261e-03 6.1031e-02 3.0095e-03 6.8212e-02 0.0000e+00
 4.5418e-02 3.6435e-02 0.0000e+00 6.1303e-03 0.0000e+00 1.2885e-02 8.0425e-03 4.0967e-03 2.4104e-02 3.2113e-02 4.3244e-03 1.1708e-02 1.5261e-01 1.0086e-01 2.2468e-02 5.2767e-02 1.6409e-02 8.3975e-03]
    row4: [0.     0.0006 0.1368 0.051  0.0081 0.0333 0.     0.     0.0148 0.0954 0.     0.     0.01   0.     0.     0.0022 0.0619 0.     0.0341 0.0321 0.     0.0033 0.     0.0135 0.0056 0.     0.0113 0.0084
 0.0008 0.0029 0.0328 0.077  0.0189 0.0149 0.0161 0.004 ]
    row5: [0.     0.0006 0.1368 0.051  0.0081 0.0333 0.     0.     0.0148 0.0954 0.     0.     0.01   0.     0.     0.0022 0.0619 0.     0.0341 0.0321 0.     0.0033 0.     0.0135 0.0056 0.     0.0113 0.0084
 0.0008 0.0029 0.0328 0.077  0.0189 0.0149 0.0161 0.004 ]
  r2_2d_clip: shape=(6, 36)
    row0: [0.0266 0.1424 0.4473 0.3397 0.1818 0.2036 0.2096 0.0913 0.1011 0.1655 0.0291 0.0493 0.1482 0.0847 0.1964 0.0564 0.2866 0.0385 0.1709 0.2536 0.0289 0.21   0.1818 0.1236 0.1922 0.0544 0.1058 0.3308
 0.1959 0.0436 0.5379 0.1882 0.103  0.1211 0.0621 0.2706]
    row1: [0.     0.0068 0.099  0.0781 0.0348 0.0987 0.0092 0.0052 0.0372 0.0375 0.     0.     0.033  0.0115 0.     0.0211 0.056  0.0152 0.0023 0.1061 0.0016 0.0302 0.     0.     0.02   0.     0.0747 0.1371
 0.0305 0.     0.1451 0.177  0.0502 0.0126 0.0082 0.0372]
    row2: [0.     0.0756 0.3939 0.1789 0.0345 0.1438 0.0813 0.0673 0.0361 0.118  0.     0.     0.0368 0.0123 0.0133 0.0215 0.2226 0.0154 0.0077 0.1589 0.0017 0.0369 0.0912 0.0636 0.0241 0.     0.0775 0.1834
 0.033  0.     0.2649 0.1764 0.0515 0.0119 0.0202 0.0406]
    row3: [0.     0.0756 0.3939 0.1789 0.0345 0.1438 0.0813 0.0673 0.0361 0.118  0.     0.     0.0368 0.0123 0.0133 0.0215 0.2226 0.0154 0.0077 0.1589 0.0017 0.0369 0.0912 0.0636 0.0241 0.     0.0775 0.1834
 0.033  0.     0.2649 0.1764 0.0515 0.0119 0.0202 0.0406]
    row4: [0.     0.0068 0.099  0.0781 0.0348 0.0987 0.0092 0.0052 0.0372 0.0375 0.     0.     0.033  0.0115 0.     0.0211 0.056  0.0152 0.0023 0.1061 0.0016 0.0302 0.     0.     0.02   0.     0.0747 0.1371
 0.0305 0.     0.1451 0.177  0.0502 0.0126 0.0082 0.0372]
    row5: [0.     0.0068 0.099  0.0781 0.0348 0.0987 0.0092 0.0052 0.0372 0.0375 0.     0.     0.033  0.0115 0.     0.0211 0.056  0.0152 0.0023 0.1061 0.0016 0.0302 0.     0.     0.02   0.     0.0747 0.1371
 0.0305 0.     0.1451 0.177  0.0502 0.0126 0.0082 0.0372]
  agreement_3d_vjepa: shape=(5,)
    [1 1 1 1 1]
  agreement_3d_clip: shape=(5,)
    [1 1 1 1 1]
  agreement_14d_vjepa: shape=(5,)
    [1 1 1 1 1]
  agreement_14d_clip: shape=(5,)
    [1 0 0 1 1]
  agreement_2d_vjepa: shape=(5,)
    [1 1 1 1 1]
  agreement_2d_clip: shape=(5,)
    [0 0 0 0 0]
  agreement_rate_3d_vjepa: shape=(1,)
    [1.]
  agreement_rate_3d_clip: shape=(1,)
    [1.]
  agreement_rate_14d_vjepa: shape=(1,)
    [1.]
  agreement_rate_14d_clip: shape=(1,)
    [0.6]
  agreement_rate_2d_vjepa: shape=(1,)
    [1.]
  agreement_rate_2d_clip: shape=(1,)
    [0.]

### Exp 19: Permutation test
  r2_obs (first 10): [3.728548e-01 7.478392e-02 8.783486e-02 2.510667e-04 0.000000e+00
 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00]
  p_values (first 10): [0. 0. 0. 0. 1. 1. 1. 1. 1. 1.]
  p_corrected (first 10): [0. 0. 0. 0. 1. 1. 1. 1. 1. 1.]
  brain_pred_mask (first 10): [ True  True  True  True False False False False False False]
  n_perm: 1000

### Exp 21: CCA (PCA100 → CCA100)
  n_pca=100, n_cc=100, n_perm=1000
  cc_r (all 100): [0.7737 0.6792 0.6492 0.6082 0.5715 0.5217 0.4952 0.4941 0.4604 0.4574 0.4385 0.428  0.4151 0.4008 0.3895 0.368  0.361  0.3573 0.3484 0.3331 0.336  0.3283 0.3247 0.3178 0.3135 0.3069 0.3065 0.2967
 0.2955 0.287  0.2775 0.2746 0.273  0.2679 0.2613 0.2557 0.249  0.2427 0.2364 0.2287 0.2312 0.2235 0.2189 0.2164 0.2144 0.2072 0.2061 0.2018 0.1951 0.1908 0.1869 0.1867 0.179  0.1762 0.1681 0.166
 0.1641 0.162  0.1577 0.155  0.1539 0.1463 0.1403 0.1352 0.1295 0.1271 0.1251 0.1234 0.1205 0.1191 0.1152 0.1099 0.1045 0.1038 0.1015 0.0929 0.0893 0.0822 0.08   0.0773 0.0722 0.0706 0.0628 0.0606
 0.0575 0.053  0.0507 0.0476 0.0431 0.0366 0.0339 0.0325 0.0259 0.0235 0.0182 0.0146 0.0114 0.0061 0.006  0.002 ]
  sig_mask sum: 88
  p_corrected (first 20): [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
  CC1 r=0.7737: A=+0.237 V=-0.151 top=[('Annoyance', 0.456), ('Interest', 0.337), ('Anxiety', 0.335)]
  CC2 r=0.6792: A=-0.111 V=+0.018 top=[('Aesthetic appreciation', -0.437), ('Excitement', -0.368), ('Relief', -0.297)]
  CC3 r=0.6492: A=+0.012 V=+0.025 top=[('Interest', -0.184), ('Empathic pain', 0.18), ('Anxiety', -0.171)]
  CC4 r=0.6082: A=-0.120 V=+0.023 top=[('Uncomfortable', -0.292), ('Sadness', 0.22), ('Surprise', -0.204)]
  CC5 r=0.5715: A=-0.078 V=+0.009 top=[('Aesthetic appreciation', -0.187), ('Amusement', 0.181), ('Excitement', -0.134)]
  CC6 r=0.5217: A=+0.021 V=-0.190 top=[('Uncomfortable', 0.327), ('Awe', -0.266), ('Adoration', -0.241)]
  CC7 r=0.4952: A=+0.023 V=+0.169 top=[('Uncomfortable', 0.177), ('Nostalgia', -0.175), ('Sympathy', -0.143)]
  CC8 r=0.4941: A=+0.080 V=-0.068 top=[('Adoration', -0.268), ('Awe', -0.158), ('Guilt', 0.145)]
  CC9 r=0.4604: A=-0.037 V=-0.166 top=[('Empathic pain', 0.197), ('Nostalgia', 0.184), ('Sympathy', 0.163)]
  CC10 r=0.4574: A=-0.010 V=+0.099 top=[('Uncomfortable', 0.162), ('Surprise', 0.144), ('Aesthetic appreciation', 0.113)]
  r2_cca_sig: cat=0.1797 AV=0.1610 ratio=1.116
  r2_cca_all: cat=0.1815 AV=0.1550 ratio=1.171
  r2_pca_3: cat=0.0533 AV=0.0352 ratio=1.514
  r2_pca_10: cat=0.1092 AV=0.0704 ratio=1.550
  r2_pca_100: cat=0.1815 AV=0.1550 ratio=1.171
  cc_r_per_subj[:,0] (CC1): [0.7369 0.7144 0.7056 0.7321 0.7082]

### Exp 23: Reverse PCA+Ridge (V-JEPA2 → Brain PC)
  r2_obs (first 20): [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
  mse_obs (first 10): [5.7824 2.8736 2.1417 1.2835 1.0631 0.9979 0.6384 0.6867 0.3164 0.3149]
  sig_mask sum: 0
  brain_pca_var_ratio (first 10): [32.66 16.27 11.99  6.68  6.16  5.08  3.6   2.86  1.86  1.49]%
  BPC1: A=-0.102 V=+0.075 top=[('Annoyance', -0.223), ('Uncomfortable', 0.178), ('Surprise', 0.171)]
  BPC2: A=+0.145 V=+0.064 top=[('Guilt', 0.147), ('Empathic pain', -0.146), ('Horror', 0.133)]
  BPC3: A=-0.003 V=+0.190 top=[('Interest', -0.204), ('Nostalgia', -0.185), ('Anxiety', -0.185)]
  BPC4: A=-0.103 V=-0.098 top=[('Amusement', 0.183), ('Uncomfortable', -0.176), ('Surprise', -0.158)]
  BPC5: A=-0.004 V=-0.106 top=[('Relief', -0.105), ('Entrancement', 0.104), ('Calmness', -0.095)]
  r2_decode_Brain_PC1_3: cat=0.0156 AV=0.0258 ratio=0.606
  r2_decode_Brain_PC1_10: cat=0.0428 AV=0.0712 ratio=0.602
  r2_decode_Brain_all_100: cat=0.0546 AV=0.0913 ratio=0.597

### Exp 26: Comprehensive interpretation
  r2_vs_std: r=0.480 p=0.0041
  r2_vs_mean: r=0.384 p=0.0249
  emo_mean: [0.036 0.059 0.079 0.204 0.017 0.066 0.107 0.027 0.044 0.037 0.062 0.011 0.022 0.014 0.087 0.026 0.044 0.007 0.048 0.078 0.005 0.064 0.113 0.081 0.033 0.007 0.018 0.031 0.048 0.041 0.053 0.091 0.033
 0.019]
  emo_std: [0.071 0.122 0.154 0.233 0.059 0.125 0.141 0.069 0.082 0.087 0.105 0.032 0.114 0.042 0.198 0.079 0.089 0.027 0.082 0.154 0.02  0.139 0.13  0.129 0.112 0.032 0.064 0.127 0.125 0.067 0.18  0.119 0.076
 0.061]
  emo_skewness: [2.44 2.57 2.37 1.02 4.62 2.64 1.42 4.18 2.71 3.6  2.54 3.73 6.27 3.89 2.74 4.31 2.64 4.29 2.28 2.27 4.92 2.8  1.46 2.   4.33 7.49 5.03 4.68 3.66 1.99 3.78 1.59 3.19 4.39]
  emo_nonzero: [0.278 0.283 0.333 0.641 0.107 0.352 0.525 0.21  0.333 0.252 0.399 0.112 0.072 0.127 0.284 0.162 0.285 0.081 0.363 0.313 0.052 0.283 0.635 0.429 0.145 0.066 0.121 0.086 0.223 0.354 0.122 0.525 0.23
 0.139]
  r2_fmri_to_vpc (10): [0.354  0.2274 0.3068 0.1469 0.0825 0.0361 0.     0.     0.0036 0.    ]
  r2_bj_to_vpc (10): [3.7284e-01 7.4791e-02 8.7770e-02 3.1729e-04 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00]
  r2_fmri_emo: cat=0.0258 AV=0.0730 ratio=0.353
    all 36: [0.     0.     0.1351 0.0774 0.     0.051  0.     0.     0.     0.     0.     0.     0.     0.     0.1205 0.     0.1107 0.     0.     0.0626 0.     0.0021 0.     0.     0.     0.     0.     0.
 0.     0.     0.2919 0.0265 0.     0.     0.     0.1461]
  r2_bj_emo: cat=0.0103 AV=0.0326 ratio=0.316
    all 36: [0.     0.     0.0821 0.     0.     0.0026 0.     0.     0.     0.     0.     0.     0.     0.     0.0327 0.     0.0387 0.     0.     0.     0.     0.0011 0.     0.     0.     0.     0.     0.0006
 0.     0.     0.192  0.     0.     0.     0.     0.0652]
  r2_vjepa_emo: cat=0.0000 AV=0.0000 ratio=0.000
    all 36: [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
  emo_pca_var (all): [0.1969 0.1304 0.1011 0.0809 0.0626 0.0468 0.0404 0.0363 0.0309 0.0295 0.0262 0.0247 0.0229 0.0196 0.0168 0.0155 0.012  0.0115 0.0111 0.0103 0.0094 0.009  0.0088 0.0078 0.0072 0.0069 0.0059 0.0052
 0.0046 0.0028 0.0018 0.0017 0.0015 0.0008]
  r2_residual (AV regress out): [0.0291 0.0895 0.327  0.1504 0.0121 0.025  0.0249 0.0195 0.0149 0.1225 0.     0.     0.012  0.0094 0.0834 0.0046 0.1943 0.     0.0386 0.0243 0.0069 0.     0.0532 0.117  0.002  0.0078 0.0196 0.0441
 0.0137 0.0204 0.197  0.0802 0.028  0.0538]

### Exp 27: Deep analysis
Keys: ['vjepa_separability', 'emo_max_corr', 'emo_strong', 'r2_ranked', 'r2_raw_fwd', 'r2_raw_rev', 'r2_raw_pred_emo', 'raw_pred_mask', 'vp_results', 'r2_brain_resid', 'clusters_3', 'clusters_5', 'emo_profiles_bp', 'r_mantel_sb', 'r_mantel_sbeh', 'r_mantel_bbeh', 'r_partial_mantel', 'p_partial_mantel', 'r2_clip_fwd', 'emotion_labels']
  vjepa_separability: [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
  emo_max_corr: [0.365 0.623 0.557 0.364 0.441 0.764 0.352 0.218 0.196 0.511 0.203 0.441 0.153 0.412 0.399 0.433 0.557 0.227 0.349 0.764 0.353 0.534 0.361 0.623 0.177 0.392 0.292 0.306 0.626 0.341 0.306 0.216 0.626
 0.392]
  emo_strong: [ 1.   6.4 10.  29.6  1.3  6.1 11.2  1.3  2.2  2.9  4.3  0.   2.6  0.2 10.9  2.   3.2  0.   2.2 10.6  0.   7.6  9.7  7.8  4.1  0.1  1.3  4.1  5.1  0.8  6.7  7.   2.1  1.2]%
  r2_ranked: [0.0114 0.0762 0.2618 0.1147 0.0163 0.0657 0.0202 0.0383 0.0157 0.0877 0.     0.     0.0461 0.0124 0.071  0.0042 0.1844 0.     0.0417 0.0658 0.0011 0.0128 0.0548 0.0577 0.     0.0085 0.0355 0.0676
 0.0106 0.0032 0.1462 0.1279 0.0384 0.083 ]
  r2_raw_fwd (20): [0.354  0.2274 0.3068 0.1469 0.0825 0.0361 0.     0.     0.0036 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.    ]
  r2_raw_rev (20): [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
  raw_pred_mask: [ True  True  True  True  True  True False False False False False False
 False False False False False False False False]
  r2_raw_pred_emo: cat=0.0763 AV=0.0454 ratio=1.681
    all 36: [0.0271 0.0818 0.3717 0.1568 0.0297 0.1082 0.0758 0.0647 0.0975 0.1564 0.003  0.0132 0.0347 0.0095 0.0769 0.0115 0.2427 0.     0.0587 0.1113 0.0042 0.0387 0.081  0.0909 0.0457 0.0178 0.0425 0.0908
 0.0237 0.0125 0.2008 0.1126 0.0377 0.0622 0.0698 0.0209]
  vp_results shape: (34, 4) (34 emotions x [stim_unique, brain_unique, shared, total])
  vp_results mean: stim=0.0143 brain=0.0030 shared=0.0407 total=0.0246
    Aesthetic appreciation: stim=0.2055 brain=0.0000 shared=0.1177 total=0.2876
    Amusement: stim=0.0223 brain=0.0000 shared=0.0936 total=0.0223
    Anxiety: stim=0.0074 brain=0.0000 shared=0.0537 total=0.0100
    Empathic pain: stim=0.0322 brain=0.0000 shared=0.0419 total=0.0648
    Excitement: stim=0.1125 brain=0.0000 shared=0.0876 total=0.1512
    Surprise: stim=0.0141 brain=0.0000 shared=0.0309 total=0.0147
    Uncomfortable: stim=0.0819 brain=0.1024 shared=0.0896 total=0.2739
  r2_brain_resid: [0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.
 0.     0.     0.     0.     0.     0.     0.     0.0081]
  clusters_3: [3 3 1 3 3 2 2 3 1 1 2 3 1 3 3 3 1 1 2 2 3 2 2 3 1 3 2 1 3 2 1 2 3 3]
  clusters_5: [5 4 1 5 5 3 2 4 1 1 3 5 1 5 4 5 1 1 3 3 5 3 2 5 1 5 3 1 5 3 1 3 5 5]
  r_mantel_sb=0.0750
  r_mantel_sbeh=0.1596
  r_mantel_bbeh=-0.0389
  r_partial_mantel=-0.0314 p=1.44e-28
  r2_clip_fwd (10): [0.2613 0.1559 0.1271 0.     0.1154 0.0167 0.0125 0.     0.     0.    ]
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
