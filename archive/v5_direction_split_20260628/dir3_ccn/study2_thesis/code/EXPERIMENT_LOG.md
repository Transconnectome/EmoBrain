# Experiment Log — main/code/

**모든 실험의 목적, 방법, 입출력, 결과를 빠짐없이 기록.**  
코드를 만들 때마다 여기에 추가. 결과가 나오면 결과도 추가.

---

## 01_glasser_parcellation.py

**상태:** 실행 중 (2026-04-12)

### 목적
Horikawa (2020) 원본과 동일한 parcellation(Glasser HCP-MMP1)으로 fMRI를 re-parcellate.
현재 Schaefer 400+50=450 parcels만 있는데, Horikawa는 Glasser 360+10=370을 사용.
두 parcellation 결과를 비교하고, Horikawa 원본과 직접 비교 가능하게 만들기 위함.

### 방법
```
Raw voxel fMRI (74, 91, 81) per frame
  → Glasser HCP-MMP1 atlas (360 cortical regions)
  → Tian S1 subcortical atlas (10 subcortical regions)
  → NiftiLabelsMasker (nilearn) → region 평균
  → frame 평균 → stimulus당 하나의 벡터
```

### 입력
```
/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/img/
  sub-01_stimulus_1/frame_0.pt ~ frame_4.pt (각 74×91×81)
  ...
  sub-05_stimulus_2196/
```

### 출력
```
main/results/glasser_parcellation/
  fmri_glasser.npy     (5, 2196, 370)
  sub-XX_glasser.npz   개별 subject 데이터
```

### 비교 대상
```
기존: fmri_raw.npy (5, 2196, 450) — Schaefer 400+50
새로: fmri_glasser.npy (5, 2196, 370) — Glasser 360+10
```

### 결과
*(실행 완료 후 기록)*

---

## 02_ch1_brain_to_behavior.py

**상태:** 대기 중 (2026-04-12)

### 목적
Chapter 1: Brain → Behavior baseline. 뇌에서 감정이 얼마나 디코딩되는가?
Horikawa (2020) 재현 + 14 affective dimensions 확장.

### 방법
```
Input:  Raw fMRI 5명 평균 (2196, 450 Schaefer parcels)
Output: 48 targets (34 emotion categories + 14 affective dimensions)
        모든 target z-score 후 디코딩 (scale 공정성)
Method: Ridge regression (alpha=1.0), 5-fold CV, R²
추가:   Subject별 개별 디코딩 (5명 각각)
        Confound check: R² vs target std 상관
```

### 입력
```
fmri_raw.npy (5, 2196, 450)
horikawa_meta_data_with_dimension_binary.csv (34 cat)
horikawa_meta_data_with_14dims.csv (14 dim)
```

### 출력
```
main/results/ch1_brain_to_behavior.npz
  r2_group:   (48,) — 5명 평균 fMRI로 디코딩
  r2_subject: (5, 48) — 개별 subject 디코딩
```

### 비판적 체크 포인트
- Cat scores는 sparse (74% zeros), Dim scores는 1-9 범위 → z-score로 통일
- R²와 target std 상관 → 분포 artifact 확인
- Subject-level consistency → 5명 평균이 개인차를 숨기는지

### 결과 (2026-04-12)

```
Group (5명 평균 fMRI):
  Cat mean R²:  0.026
  Dim mean R²:  0.061
  Cat/Dim ratio: 0.42  → 차원 > 범주!
  Targets with R²>0.01: 16/48

Top 5:
  Uncomfortable 0.292 (cat), Safety 0.168 (dim), Control 0.162 (dim),
  Valence 0.146 (dim), Aesthetic appreciation 0.135 (cat)

R²=0인 targets: 31/34 categories, 6/14 dimensions
  Arousal=0 (의외), Dominance=0, Attention=0

Subject-level:
  S1: cat=0.014, dim=0.008
  S2-S5: 대부분 cat<0.01, dim<0.01
  → n=5 한계 명확

Confound: R² vs target std r=0.450, p=0.001
```

### 해석

1. Cat/Dim=0.42는 이전 brain-pred subspace Cat/VA=1.44와 **반대**
   → 하지만 Reverse Cat/VA=0.60과 일관
   → "뇌 전체는 차원 편향, AI와 공유하는 부분은 범주 편향"
   → 이것이 ???의 첫 번째 단서

2. Arousal=0 문제: z-scoring 때문인지, parcellation 때문인지 확인 필요
   → 원본 scale로도 테스트 필요

3. 31/34 categories = 0: Horikawa는 수십 개 유의했는데 우리는 3개만
   → 방법 차이: parcel(450) vs voxel-level, simple ridge vs banded ridge
   → parcel 평균이 voxel-level 감정 정보를 날렸을 가능성

4. Confound r=0.45: dim의 std가 크니까 dim이 잘 나오는 건 부분적 artifact

### 재실행 결과 (2026-04-12, RidgeCV + 원본 scale + 2185개)
*(상세 결과는 위에)*

---

## 03_ch1c_roi_decoding.py

**상태:** 대기 중 (2026-04-12)

### 목적
Chapter 1-C: ROI별 감정 디코딩 지도.
"어떤 뇌 영역(network)이 어떤 감정을 인코딩하는가?"
Horikawa의 transmodal > unimodal 발견 재현 + Chapter 3 비교 baseline.

### 방법
```
ROI 정의 (theory-driven, Yeo 7 networks + subcortical):
  Vis (61 parcels): 초기 시각
  SomMot (77): 체성감각/운동
  DorsAttn (46): 배측 주의
  SalVentAttn (47): 현저성/복측 주의 (insula 포함)
  Limbic (26): 변연계 (OFC, temporal pole)
  Cont (52): 인지 제어 (dACC, dlPFC)
  Default (91): DMN (mPFC, TPJ, angular gyrus, PCC)
  Subcortical (50): Tian S3 (amygdala, hippocampus 등)

각 network의 parcels만 사용 → 48 targets 디코딩
Method: RidgeCV, 5-fold CV, Pearson r + R²
```

### 입력
```
fmri_raw.npy (5, 2185, 450) — unique만
48 targets (34 cat + 14 dim) — 원본 scale
```

### 출력
```
ch1c_roi_decoding.npz
  r_roi: (8 networks, 48 targets)
  r2_roi: (8 networks, 48 targets)
```

### 검증 포인트
- Horikawa 예측: Default/SalVentAttn(transmodal) > Vis/SomMot(unimodal)
- Cat/Dim ratio가 network별로 다른가?
- 이 결과가 Chapter 3에서 AI-unique ROI와 비교됨

### 결과 (2026-04-12)

```
Network ranking (mean r across 48 targets):
  1. Default(DMN)   0.342  ← Horikawa와 일관
  2. Cont           0.315
  3. DorsAttn       0.313
  4. SomMot         0.312
  5. SalVentAttn    0.312
  6. Vis            0.288
  7. Limbic         0.252
  8. Subcortical    0.224

Transmodal vs Unimodal:
  Unimodal (Vis+SomMot):     cat r=0.282
  Transmodal (Default+SalVA+Limb): cat r=0.281
  → 거의 동등. Horikawa처럼 뚜렷한 차이 안 남 (network 묶기 해상도 문제?)

Cat/Dim ratio: 모든 network에서 dim > cat (0.67~0.87)
  가장 범주적: Limbic (0.87)
  가장 차원적: Subcortical (0.67)

Video Identification: 모든 network에서 cat > dim
  Default: cat 76.9% > dim 65.1%  ← Horikawa와 일관

네트워크별 특기:
  Vis: Aesthetic appreciation (0.49)
  Default: Safety (0.52), Control (0.52), Valence (0.52)
  SalVentAttn: Empathic pain (0.49)
```

---

### 재실행 결과 (2026-04-12, RidgeCV + 원본 scale + 2185개)

```
방법 변경: Ridge(alpha=1.0) → RidgeCV(alpha 자동 최적화)
         z-scored targets → 원본 scale
         2196 → 2185 (11개 반복 제거)

Group (5명 평균):
  Cat mean r=0.355, R²=0.142
  Dim mean r=0.445, R²=0.207
  Cat/Dim ratio: r=0.80, R²=0.69
  Targets with r>0.095: 47/48

  Top 5: Uncomfortable(0.64), Safety(0.57), Control(0.56),
         Valence(0.55), Aesthetic appreciation(0.55)
  Bottom: Joy(0.08), Contempt(0.13), Fear(0.15)
  Arousal: r=0.31 (해결됨)

Video Identification (pairwise, chance 50%):
  Category (34): 81.1%  ← Horikawa 81.9%와 거의 일치
  Dimension (14): 67.8% ← Horikawa 68.7%와 거의 일치
  All (48): 63.8%
  → cat > dim 패턴 재현 완료

Subject-level:
  모든 subject에서 45-48/48 targets r>0.095
  Mean: cat r=0.292, dim r=0.350

핵심 해석:
  - Video identification으로 Horikawa 거의 완벽 재현
  - 개별 r 기준: dim > cat (r=0.80), 하지만 identification: cat > dim
  - 이전 실패(alpha=1.0)는 hyperparameter 문제였음
  - Arousal도 RidgeCV로 해결 (r=0.31)
```

---

## 04_ch1_noise_ceiling.py

**상태:** 완료 (2026-04-12)

### 목적
Noise ceiling 계산으로 Cat vs Dim 비교를 공정하게.
"dim > cat이 진짜인지, noise ceiling artifact인지?"

### 방법
```
Method 1: Subject-level decoding
  각 subject(1명) fMRI → 48 targets → subject별 r
  → subject/group ratio = 개인 안정성

Method 2: LOO Noise Ceiling
  4명 평균 fMRI → 48 targets → r (5번 반복)
  → lower NC

Method 3: fMRI ISC
  parcel별 subject 간 Pearson r
```

### 결과

```
NC 정규화 핵심:
                Group r   Subj r   LOO NC    S/G ratio
  Category (34)  0.355    0.292    0.348     0.822
  Dimension (14) 0.445    0.350    0.433     0.788

  Raw Cat/Dim = 0.799 (dim > cat)
  Subject-level Cat/Dim = 0.834 (격차 줄어듦)
  NC 정규화 (group/LOO) Cat/Dim = 0.994 (거의 동등!)

  → "dim > cat은 NC artifact. 정규화하면 cat ≈ dim."
  → Cat S/G(0.822) > Dim S/G(0.788): cat이 개인 수준에서 더 안정적
  → ISC mean = 0.151 (15% subject 간 일관성)
  → 최불안정: Joy(42%), Fear(67%)
  → 최안정: Sexual desire(89%), Aesthetic apprec(88%)
```

---

## 05_ch1d_principal_gradient.py

**상태:** 완료 (2026-04-12)

### 목적
PG1(unimodal↔transmodal) vs 감정 디코딩 성능 관계.
Horikawa/Margulies 예측: transmodal에서 감정 인코딩 강함.

### 방법
```
fMRI FC matrix (400 cortical) → cosine similarity → SpectralEmbedding
→ PG1 (Margulies 대용)
→ network별 PG1 vs Ch1-C 디코딩 r → Spearman 상관
```

### 결과

```
PG1 순서: Vis(-) < DorsAttn < Limbic < SomMot < SalVentAttn < Cont < Default(+)
→ Margulies와 일관 (Default = transmodal 끝)

PG1 vs 디코딩 (Spearman, n=7 networks):
  All r:    ρ=+0.571, p=0.180
  Cat r:    ρ=+0.607, p=0.148  
  Dim r:    ρ=+0.714, p=0.071
  Cat/Dim:  ρ=-0.643, p=0.119

방향은 예상대로 (transmodal→디코딩↑) 하지만 n=7이라 비유의.
Cat/Dim vs PG1 음의 상관 = transmodal에서 dim이 상대적으로 더 강함.
```

---

## 06_ch1e_rsa.py

**상태:** 완료 (2026-04-12)

### 목적
RSA로 뇌 표상 구조가 범주적인지 차원적인지 확인. Horikawa 재현.

### 결과

```
Group RSA (n=500 subsample):
  Brain vs Category (34): ρ = 0.118
  Brain vs Dimension (14): ρ = 0.064
  → Cat > Dim (1.84배) — Horikawa 재현!

ROI별: 모든 8 networks에서 Cat > Dim
  1위 Default(0.127), 최하 Subcortical(0.054)

Subject-level: 5명 모두 cat > dim 일관
  cat ρ=0.080±0.007, dim ρ=0.043±0.009

핵심 해석:
  디코딩(r): dim > cat → 개별 차원 예측력은 dim이 높음
  RSA(ρ):   cat > dim → 뇌의 구조적 조직은 범주적
  VidID(%): cat > dim → 비디오 구별은 범주 패턴이 우세
  → 세 metric이 일관되게 "뇌 구조 = 범주적" 지지
```

---

---

# CHAPTER 1 전체 결과 상세 (2026-04-12)

## 1-A: 전체 디코딩 (Raw fMRI 450 → 48 targets, RidgeCV, 5-fold, 2185 unique)

| Target                    |  Pearson r |       R² |  Subj mean r |   LOO NC |   S/G% |   RSA ρ |  Type |
|---------------------------|------------|----------|--------------|----------|--------|---------|-------|
| Uncomfortable             |     0.6384 |   0.4076 |       0.5499 |   0.6263 |  86.1% | -0.0315 |   cat |
| Safety                    |     0.5651 |   0.3192 |       0.4571 |   0.5503 |  80.9% | -0.0216 |   dim |
| Control                   |     0.5582 |   0.3113 |       0.4492 |   0.5432 |  80.5% | -0.0180 |   dim |
| Valence                   |     0.5536 |   0.3063 |       0.4288 |   0.5389 |  77.4% | -0.0163 |   dim |
| Aesthetic appreciation    |     0.5485 |   0.2999 |       0.4833 |   0.5395 |  88.1% | -0.0445 |   cat |
| Approach                  |     0.5475 |   0.2997 |       0.4213 |   0.5312 |  76.9% | -0.0132 |   dim |
| Empathic pain             |     0.5418 |   0.2935 |       0.4455 |   0.5344 |  82.2% | -0.0265 |   cat |
| Amusement                 |     0.5130 |   0.2624 |       0.4367 |   0.5023 |  85.1% | -0.0196 |   cat |
| Excitement                |     0.5121 |   0.2607 |       0.4365 |   0.4961 |  85.2% | -0.0270 |   cat |
| Interest                  |     0.4950 |   0.2444 |       0.4173 |   0.4770 |  84.3% | -0.0159 |   cat |
| Upswing                   |     0.4935 |   0.2429 |       0.3753 |   0.4776 |  76.0% | -0.0062 |   dim |
| Effort                    |     0.4891 |   0.2376 |       0.3787 |   0.4728 |  77.4% |  0.0047 |   dim |
| Anxiety                   |     0.4840 |   0.2334 |       0.4198 |   0.4725 |  86.7% | -0.0237 |   cat |
| Fairness                  |     0.4787 |   0.2282 |       0.3710 |   0.4647 |  77.5% | -0.0114 |   dim |
| Nostalgia                 |     0.4610 |   0.2119 |       0.3575 |   0.4489 |  77.5% | -0.0144 |   cat |
| Certainty                 |     0.4539 |   0.2057 |       0.3518 |   0.4410 |  77.5% | -0.0134 |   dim |
| Annoyance                 |     0.4467 |   0.1995 |       0.3833 |   0.4390 |  85.8% | -0.0404 |   cat |
| Relief                    |     0.4177 |   0.1744 |       0.3571 |   0.4100 |  85.5% | -0.0040 |   cat |
| Commitment                |     0.4145 |   0.1717 |       0.3427 |   0.4054 |  82.7% | -0.0055 |   dim |
| Identity                  |     0.4091 |   0.1672 |       0.3322 |   0.4003 |  81.2% | -0.0060 |   dim |
| Surprise                  |     0.4084 |   0.1648 |       0.3379 |   0.3976 |  82.7% | -0.0085 |   cat |
| Adoration                 |     0.4079 |   0.1664 |       0.3393 |   0.4071 |  83.2% | -0.0284 |   cat |
| Calmness                  |     0.4045 |   0.1635 |       0.3371 |   0.3967 |  83.3% | -0.0223 |   cat |
| Sadness                   |     0.4030 |   0.1611 |       0.3168 |   0.3864 |  78.6% | -0.0441 |   cat |
| Romance                   |     0.3939 |   0.1547 |       0.3303 |   0.3920 |  83.8% | -0.0325 |   cat |
| Craving                   |     0.3763 |   0.1385 |       0.2927 |   0.3618 |  77.8% | -0.0339 |   cat |
| Awe                       |     0.3703 |   0.1344 |       0.3216 |   0.3691 |  86.8% | -0.0175 |   cat |
| Entrancement              |     0.3691 |   0.1362 |       0.2878 |   0.3567 |  78.0% | -0.0302 |   cat |
| Obstruction               |     0.3636 |   0.1322 |       0.2892 |   0.3555 |  79.5% |  0.0033 |   dim |
| Attention                 |     0.3304 |   0.1090 |       0.2667 |   0.3228 |  80.7% |  0.0082 |   dim |
| Guilt                     |     0.3163 |   0.0997 |       0.2589 |   0.3119 |  81.9% | -0.0262 |   cat |
| Confusion                 |     0.3154 |   0.0986 |       0.2242 |   0.3020 |  71.1% | -0.0200 |   cat |
| Arousal                   |     0.3125 |   0.0973 |       0.2574 |   0.3062 |  82.4% |  0.0000 |   dim |
| Horror                    |     0.3074 |   0.0935 |       0.2640 |   0.3031 |  85.9% | -0.0145 |   cat |
| Awkwardness               |     0.3063 |   0.0937 |       0.2531 |   0.2997 |  82.6% | -0.0115 |   cat |
| Boredom                   |     0.3016 |   0.0907 |       0.2431 |   0.2951 |  80.6% | -0.0100 |   cat |
| Sexual desire             |     0.2966 |   0.0879 |       0.2644 |   0.2938 |  89.2% | -0.0210 |   cat |
| Sympathy                  |     0.2949 |   0.0815 |       0.2370 |   0.2879 |  80.4% | -0.0082 |   cat |
| Anger                     |     0.2807 |   0.0786 |       0.2238 |   0.2742 |  79.8% | -0.0155 |   cat |
| Envy                      |     0.2656 |   0.0674 |       0.2227 |   0.2627 |  83.8% | -0.0088 |   cat |
| Triumph                   |     0.2607 |   0.0678 |       0.1965 |   0.2516 |  75.4% | -0.0049 |   cat |
| Dominance                 |     0.2551 |   0.0641 |       0.1814 |   0.2452 |  71.1% | -0.0024 |   dim |
| Admiration                |     0.2257 |   0.0506 |       0.1837 |   0.2264 |  81.4% | -0.0068 |   cat |
| Disgust                   |     0.2074 |   0.0405 |       0.1570 |   0.1976 |  75.7% | -0.0013 |   cat |
| Satisfaction              |     0.1510 |   0.0216 |       0.1248 |   0.1489 |  82.6% | -0.0100 |   cat |
| Fear                      |     0.1507 |   0.0226 |       0.1004 |   0.1440 |  66.7% | -0.0069 |   cat |
| Contempt                  |     0.1300 |   0.0165 |       0.0965 |   0.1267 |  74.3% | -0.0043 |   cat |
| Joy                       |     0.0779 |   0.0025 |       0.0330 |   0.0778 |  42.3% |  0.0004 |   cat |
| **CAT MEAN**              |     0.3553 |   0.1418 |       0.2922 |   0.3476 |  80.4% | -0.0187 |       |
| **DIM MEAN**              |     0.4446 |   0.2066 |       0.3502 |   0.4325 |  78.7% | -0.0070 |       |

**Video Identification (pairwise, chance 50%):**
  Category (34): 81.1%  (Horikawa: 81.9%)
  Dimension (14): 67.8% (Horikawa: 68.7%)
  All (48): 63.8%

## 1-C: ROI별 디코딩 (8 networks)

| Network         |   Cat r |   Dim r |  Cat R² |  Dim R² |  C/D r | VidID cat | VidID dim | VidID all |
|-----------------|---------|---------|---------|---------|--------|-----------|-----------|-----------|
| Vis             |  0.2706 |  0.3311 |  0.0864 |  0.1150 |  0.817 |     73.7% |     61.6% |     58.1% |
| SomMot          |  0.2930 |  0.3591 |  0.0998 |  0.1342 |  0.816 |     75.1% |     62.8% |     59.1% |
| DorsAttn        |  0.2922 |  0.3649 |  0.0983 |  0.1386 |  0.801 |     74.8% |     61.9% |     58.7% |
| SalVentAttn     |  0.2850 |  0.3785 |  0.0925 |  0.1494 |  0.753 |     74.2% |     63.2% |     59.9% |
| Limbic          |  0.2412 |  0.2764 |  0.0663 |  0.0798 |  0.873 |     69.1% |     58.0% |     55.6% |
| Cont            |  0.2928 |  0.3702 |  0.0959 |  0.1434 |  0.791 |     74.4% |     63.0% |     59.4% |
| Default         |  0.3157 |  0.4054 |  0.1102 |  0.1729 |  0.779 |     76.9% |     65.1% |     61.3% |
| Subcortical     |  0.1959 |  0.2910 |  0.0468 |  0.0908 |  0.673 |     64.8% |     57.7% |     54.9% |

## 1-D: Principal Gradient

| Network         |      PG1 |
|-----------------|----------|
| Vis             |  -0.0075 |
| SomMot          |  -0.0015 |
| DorsAttn        |  -0.0095 |
| SalVentAttn     |   0.0009 |
| Limbic          |  -0.0059 |
| Cont            |   0.0023 |
| Default         |   0.0026 |

PG1 vs Cat r: ρ=0.607 (p=0.148)
PG1 vs Dim r: ρ=0.714 (p=0.071)
PG1 vs All r: ρ=0.571 (p=0.180)
PG1 vs C/D:   ρ=-0.643 (p=0.119)

## 1-E: RSA (n=500 subsample)

Group: Cat ρ=0.1178, Dim ρ=0.0642, VA ρ=0.0411

| Network         |   Cat ρ |   Dim ρ |    VA ρ |
|-----------------|---------|---------|---------|
| Vis             |  0.0658 |  0.0296 |  0.0232 |
| SomMot          |  0.0998 |  0.0596 |  0.0410 |
| DorsAttn        |  0.1029 |  0.0429 |  0.0205 |
| SalVentAttn     |  0.1082 |  0.0568 |  0.0274 |
| Limbic          |  0.0746 |  0.0339 |  0.0217 |
| Cont            |  0.1025 |  0.0648 |  0.0444 |
| Default         |  0.1267 |  0.0668 |  0.0402 |
| Subcortical     |  0.0535 |  0.0352 |  0.0252 |

Subject: cat ρ=0.0799±0.0068, dim ρ=0.0430±0.0090

## Noise Ceiling

ISC mean: 0.1510, range [-0.0070, 0.5060]

|                 |  Group r |   Subj r |   LOO NC |    S/G |
|-----------------|----------|----------|----------|--------|
| Category        |   0.3553 |   0.2922 |   0.3476 |  0.804 |
| Dimension       |   0.4446 |   0.3502 |   0.4325 |  0.787 |

Subject-level:
  S1: cat r=0.3180, dim r=0.3789
  S2: cat r=0.2900, dim r=0.3411
  S3: cat r=0.2949, dim r=0.3435
  S4: cat r=0.2886, dim r=0.3497
  S5: cat r=0.2694, dim r=0.3378

## 종합: Cat vs Dim

| Metric | Cat | Dim | Cat>Dim? |
|--------|-----|-----|----------|
| Pearson r | 0.3553 | 0.4446 | NO |
| R² | 0.1418 | 0.2066 | NO |
| NC normalized | ~1.0 | ~1.0 | 동등 |
| Video ID | 81.1% | 67.8% | YES |
| RSA | 0.1178 | 0.0642 | YES |

결론: 개별 예측력(r)은 dim이 높지만, 구조적 조직(RSA)과 패턴 구별력(VidID)은 cat이 우세. NC 정규화하면 개별 예측력도 동등. 뇌의 감정 표상은 범주적으로 조직됨.

## 1-E RSA 상세 (빠졌던 값 추가)

### Per-emotion RSA (48 targets, sorted by ρ)

| Target                    |    RSA ρ |          p |  Type |
|---------------------------|----------|------------|-------|
| Attention                 |   0.0082 |   3.81e-03 |   dim |
| Effort                    |   0.0047 |   1.00e-01 |   dim |
| Obstruction               |   0.0033 |   2.40e-01 |   dim |
| Joy                       |   0.0004 |   8.87e-01 |   cat |
| Arousal                   |   0.0000 |   9.99e-01 |   dim |
| Disgust                   |  -0.0013 |   6.54e-01 |   cat |
| Dominance                 |  -0.0024 |   3.92e-01 |   dim |
| Relief                    |  -0.0040 |   1.54e-01 |   cat |
| Contempt                  |  -0.0043 |   1.25e-01 |   cat |
| Triumph                   |  -0.0049 |   8.08e-02 |   cat |
| Commitment                |  -0.0055 |   5.10e-02 |   dim |
| Identity                  |  -0.0060 |   3.51e-02 |   dim |
| Upswing                   |  -0.0062 |   2.95e-02 |   dim |
| Admiration                |  -0.0068 |   1.61e-02 |   cat |
| Fear                      |  -0.0069 |   1.55e-02 |   cat |
| Sympathy                  |  -0.0082 |   3.67e-03 |   cat |
| Surprise                  |  -0.0085 |   2.71e-03 |   cat |
| Envy                      |  -0.0088 |   1.99e-03 |   cat |
| Satisfaction              |  -0.0100 |   4.17e-04 |   cat |
| Boredom                   |  -0.0100 |   4.10e-04 |   cat |
| Fairness                  |  -0.0114 |   5.59e-05 |   dim |
| Awkwardness               |  -0.0115 |   4.57e-05 |   cat |
| Approach                  |  -0.0132 |   3.33e-06 |   dim |
| Certainty                 |  -0.0134 |   2.39e-06 |   dim |
| Nostalgia                 |  -0.0144 |   3.60e-07 |   cat |
| Horror                    |  -0.0145 |   2.79e-07 |   cat |
| Anger                     |  -0.0155 |   4.70e-08 |   cat |
| Interest                  |  -0.0159 |   1.80e-08 |   cat |
| Valence                   |  -0.0163 |   8.43e-09 |   dim |
| Awe                       |  -0.0175 |   6.49e-10 |   cat |
| Control                   |  -0.0180 |   2.00e-10 |   dim |
| Amusement                 |  -0.0196 |   4.22e-12 |   cat |
| Confusion                 |  -0.0200 |   1.72e-12 |   cat |
| Sexual desire             |  -0.0210 |   1.04e-13 |   cat |
| Safety                    |  -0.0216 |   2.54e-14 |   dim |
| Calmness                  |  -0.0223 |   3.64e-15 |   cat |
| Anxiety                   |  -0.0237 |   6.32e-17 |   cat |
| Guilt                     |  -0.0262 |   2.19e-20 |   cat |
| Empathic pain             |  -0.0265 |   8.66e-21 |   cat |
| Excitement                |  -0.0270 |   1.53e-21 |   cat |
| Adoration                 |  -0.0284 |   1.27e-23 |   cat |
| Entrancement              |  -0.0302 |   1.31e-26 |   cat |
| Uncomfortable             |  -0.0315 |   8.01e-29 |   cat |
| Romance                   |  -0.0325 |   1.70e-30 |   cat |
| Craving                   |  -0.0339 |   5.34e-33 |   cat |
| Annoyance                 |  -0.0404 |   2.75e-46 |   cat |
| Sadness                   |  -0.0441 |   7.76e-55 |   cat |
| Aesthetic appreciation    |  -0.0445 |   1.30e-55 |   cat |
| **CAT MEAN**              |  -0.0187 |            |       |
| **DIM MEAN**              |  -0.0070 |            |       |

### Subject-level RSA

| Subject | Cat ρ  | Dim ρ  |
|---------|--------|--------|
| S1      | 0.0921 | 0.0426 |
| S2      | 0.0768 | 0.0322 |
| S3      | 0.0775 | 0.0349 |
| S4      | 0.0717 | 0.0569 |
| S5      | 0.0814 | 0.0486 |
| Mean    | 0.0799±0.0068 | 0.0430±0.0090 |


---

## 07_ch2_0_forward_reverse_cca.py

**상태:** 완료 (2026-04-12)

### 목적
CCN 분석을 2185 unique + RidgeCV로 재실행. Raw fMRI + CLIP 추가.
Chapter 2 variance partitioning의 motivation.

### A. Forward: Brain → AI Model PC (R²)

#### Raw fMRI → V-JEPA2 PC
| PC | R² |
|----|------|
| 1 | 0.4840 |
| 2 | 0.3464 |
| 3 | 0.4299 |
| 4 | 0.2730 |
| 5 | 0.2493 |
| 6 | 0.1743 |
| 7 | 0.0841 |
| 8 | 0.1032 |
| 9 | 0.1897 |
| 10 | 0.1725 |
| 11 | 0.1071 |
| 12 | 0.1781 |
| 13 | 0.0667 |
| 14 | 0.0624 |
| 15 | 0.0867 |
| 16 | 0.0506 |
| 17 | 0.0582 |
| 18 | 0.0422 |
| 19 | 0.0611 |
| 20 | 0.0168 |
| **Significant** | **20/20** |

#### Raw fMRI → CLIP PC
| PC | R² |
|----|------|
| 1 | 0.4191 |
| 2 | 0.4435 |
| 3 | 0.3730 |
| 4 | 0.2328 |
| 5 | 0.3479 |
| 6 | 0.2475 |
| 7 | 0.2272 |
| 8 | 0.1791 |
| 9 | 0.1399 |
| 10 | 0.1905 |
| 11 | 0.0502 |
| 12 | 0.0969 |
| 13 | 0.0907 |
| 14 | 0.0913 |
| 15 | 0.0508 |
| 16 | 0.0493 |
| 17 | 0.0992 |
| 18 | 0.0720 |
| 19 | 0.0827 |
| 20 | 0.0324 |
| **Significant** | **20/20** |

#### Brain-JEPA → V-JEPA2 PC
| PC | R² |
|----|------|
| 1 | 0.4134 |
| 2 | 0.1967 |
| 3 | 0.2236 |
| 4 | 0.1311 |
| 5 | 0.0921 |
| 6 | 0.0611 |
| 7 | 0.0325 |
| 8 | 0.0389 |
| 9 | 0.0573 |
| 10 | 0.0886 |
| 11 | 0.0469 |
| 12 | 0.0781 |
| 13 | 0.0364 |
| 14 | 0.0329 |
| 15 | 0.0324 |
| 16 | 0.0138 |
| 17 | 0.0162 |
| 18 | 0.0000 |
| 19 | 0.0000 |
| 20 | 0.0092 |
| **Significant** | **17/20** |

#### Brain-JEPA → CLIP PC
| PC | R² |
|----|------|
| 1 | 0.3553 |
| 2 | 0.2304 |
| 3 | 0.2610 |
| 4 | 0.1299 |
| 5 | 0.1939 |
| 6 | 0.1216 |
| 7 | 0.1539 |
| 8 | 0.0860 |
| 9 | 0.0836 |
| 10 | 0.0349 |
| 11 | 0.0208 |
| 12 | 0.0255 |
| 13 | 0.0371 |
| 14 | 0.0252 |
| 15 | 0.0097 |
| 16 | 0.0303 |
| 17 | 0.0282 |
| 18 | 0.0117 |
| 19 | 0.0453 |
| 20 | 0.0126 |
| **Significant** | **19/20** |

### B. Reverse: AI Model → Brain PC (R²)

#### V-JEPA2 → Raw fMRI PC
| PC | R² |
|----|------|
| 1 | 0.0346 |
| 2 | 0.3198 |
| 3 | 0.4588 |
| 4 | 0.2927 |
| 5 | 0.2993 |
| 6 | 0.1620 |
| 7 | 0.1958 |
| 8 | 0.1639 |
| 9 | 0.1420 |
| 10 | 0.0988 |
| 11 | 0.1088 |
| 12 | 0.1009 |
| 13 | 0.0519 |
| 14 | 0.0526 |
| 15 | 0.0972 |
| 16 | 0.0943 |
| 17 | 0.0823 |
| 18 | 0.0429 |
| 19 | 0.0300 |
| 20 | 0.1238 |
| **Significant** | **20/20** |

#### CLIP → Raw fMRI PC
| PC | R² |
|----|------|
| 1 | 0.0360 |
| 2 | 0.3023 |
| 3 | 0.4480 |
| 4 | 0.3033 |
| 5 | 0.2788 |
| 6 | 0.1515 |
| 7 | 0.2016 |
| 8 | 0.1724 |
| 9 | 0.1036 |
| 10 | 0.1034 |
| 11 | 0.0983 |
| 12 | 0.0721 |
| 13 | 0.0587 |
| 14 | 0.0542 |
| 15 | 0.0791 |
| 16 | 0.1047 |
| 17 | 0.0839 |
| 18 | 0.0408 |
| 19 | 0.0097 |
| 20 | 0.1206 |
| **Significant** | **19/20** |

#### V-JEPA2 → Brain-JEPA PC
| PC | R² |
|----|------|
| 1 | 0.1901 |
| 2 | 0.1265 |
| 3 | 0.1764 |
| 4 | 0.1276 |
| 5 | 0.1234 |
| 6 | 0.0464 |
| 7 | 0.0593 |
| 8 | 0.0241 |
| 9 | 0.1244 |
| 10 | 0.0428 |
| 11 | 0.0462 |
| 12 | 0.1155 |
| 13 | 0.0377 |
| 14 | 0.0572 |
| 15 | 0.0307 |
| 16 | 0.0196 |
| 17 | 0.0202 |
| 18 | 0.0744 |
| 19 | 0.0375 |
| 20 | 0.0202 |
| **Significant** | **20/20** |

### C. CCA

#### Raw fMRI ↔ V-JEPA2 (PCA50 → CCA30)
| CC | r |
|----|------|
| 1 | 0.7646 |
| 2 | 0.7558 |
| 3 | 0.7033 |
| 4 | 0.6261 |
| 5 | 0.5665 |
| 6 | 0.5374 |
| 7 | 0.5247 |
| 8 | 0.4774 |
| 9 | 0.4273 |
| 10 | 0.4094 |
| 11 | 0.3919 |
| 12 | 0.3660 |
| 13 | 0.3462 |
| 14 | 0.3292 |
| 15 | 0.3094 |
| 16 | 0.2853 |
| 17 | 0.2713 |
| 18 | 0.2677 |
| 19 | 0.2621 |
| 20 | 0.2481 |
| 21 | 0.2323 |
| 22 | 0.2176 |
| 23 | 0.2003 |
| 24 | 0.1966 |
| 25 | 0.1857 |
| 26 | 0.1780 |
| 27 | 0.1692 |
| 28 | 0.1554 |
| 29 | 0.1426 |
| 30 | 0.1417 |
| **CCs r>0.3** | **15/30** |

#### Raw fMRI ↔ CLIP (PCA50 → CCA30)
| CC | r |
|----|------|
| 1 | 0.7674 |
| 2 | 0.7527 |
| 3 | 0.7170 |
| 4 | 0.6242 |
| 5 | 0.5554 |
| 6 | 0.5241 |
| 7 | 0.5089 |
| 8 | 0.4816 |
| 9 | 0.4468 |
| 10 | 0.4151 |
| 11 | 0.3896 |
| 12 | 0.3652 |
| 13 | 0.3437 |
| 14 | 0.3195 |
| 15 | 0.3177 |
| 16 | 0.3124 |
| 17 | 0.2775 |
| 18 | 0.2673 |
| 19 | 0.2498 |
| 20 | 0.2409 |
| 21 | 0.2292 |
| 22 | 0.2184 |
| 23 | 0.2077 |
| 24 | 0.1940 |
| 25 | 0.1879 |
| 26 | 0.1780 |
| 27 | 0.1712 |
| 28 | 0.1597 |
| 29 | 0.1564 |
| 30 | 0.1473 |
| **CCs r>0.3** | **16/30** |

#### Brain-JEPA ↔ V-JEPA2 (PCA50 → CCA30)
| CC | r |
|----|------|
| 1 | 0.7341 |
| 2 | 0.6088 |
| 3 | 0.5628 |
| 4 | 0.5214 |
| 5 | 0.4728 |
| 6 | 0.4234 |
| 7 | 0.4098 |
| 8 | 0.3732 |
| 9 | 0.3414 |
| 10 | 0.3233 |
| 11 | 0.3151 |
| 12 | 0.2892 |
| 13 | 0.2783 |
| 14 | 0.2670 |
| 15 | 0.2556 |
| 16 | 0.2411 |
| 17 | 0.2277 |
| 18 | 0.2181 |
| 19 | 0.2124 |
| 20 | 0.2066 |
| 21 | 0.1916 |
| 22 | 0.1759 |
| 23 | 0.1688 |
| 24 | 0.1646 |
| 25 | 0.1596 |
| 26 | 0.1463 |
| 27 | 0.1414 |
| 28 | 0.1309 |
| 29 | 0.1251 |
| 30 | 0.1215 |
| **CCs r>0.3** | **11/30** |

### Summary

| Comparison | Forward (R²>0.01) | Reverse (R²>0.01) | CCA (r>0.3) |
|------------|-------------------|-------------------|-------------|
| Raw↔V-JEPA2 | 20/20 | 20/20 | 15/30 |
| Raw↔CLIP | 20/20 | 19/20 | 16/30 |
| BJ↔V-JEPA2 | 17/20 | 20/20 | 11/30 |
| BJ↔CLIP | 19/20 | — | — |

### ⚠️ 핵심 변화 (CCN 결과 vs 현재)

이전 CCN (Ridge alpha=1.0, 2196개, Brain-JEPA only):
  Forward: 3개 유의, Reverse: 0개 유의

현재 (RidgeCV, 2185개, Raw fMRI + Brain-JEPA):
  Forward Raw→V-JEPA2: 20/20 전부 유의
  Reverse V-JEPA2→Raw: 20/20 전부 유의 ← 이전과 완전히 다름!
  Forward BJ→V-JEPA2: 17/20
  Reverse V-JEPA2→BJ: 20/20

→ **이전의 "비대칭" 결과는 alpha 고정(1.0) artifact였을 가능성.**
→ RidgeCV로 최적화하면 Forward도 Reverse도 다 유의.
→ Chapter 2의 motivation이 바뀔 수 있음.
→ 하지만 R² 크기는 여전히 다를 수 있으므로 상세 비교 필요.


---

## 08_ch2_1_variance_partitioning.py

**상태:** 부분 완료 (2026-04-12) — confound control 진행 중

### 목적
Chapter 2 핵심: fMRI에서 AI가 설명하는 부분(shared)과 못하는 부분(unique=???) 분리.
"뇌에 AI가 모르는 감정 정보가 있는가?"

### 방법
```
Step 1: AI embedding → fMRI 예측 (cross-validated, parcel별 RidgeCV)
  → fmri_predicted (AI-shared), fmri_residual (AI-unique)
Step 2: 각각에서 48 targets 디코딩 (RidgeCV, 5-fold)
  Total: fMRI 전체 → emotion
  Shared: fMRI predicted → emotion  
  Unique: fMRI residual → emotion (= ???)
```

### 결과 (V-JEPA2 / CLIP)

#### V-JEPA2 렌즈 (1408d)

fMRI variance explained by V-JEPA2: **16.0%**

| Target                 | Total r | Shared r | Unique r | Type |
|------------------------|---------|----------|----------|------|
| Empathic pain          |  0.5418 |   0.4169 |   0.4157 |  cat |
| Valence                |  0.5536 |   0.4616 |   0.4130 |  dim |
| Control                |  0.5582 |   0.4797 |   0.3944 |  dim |
| Approach               |  0.5475 |   0.4749 |   0.3897 |  dim |
| Upswing                |  0.4935 |   0.3577 |   0.3887 |  dim |
| Effort                 |  0.4891 |   0.4104 |   0.3703 |  dim |
| Fairness               |  0.4787 |   0.3757 |   0.3396 |  dim |
| Safety                 |  0.5651 |   0.5394 |   0.3386 |  dim |
| Certainty              |  0.4539 |   0.3857 |   0.3351 |  dim |
| Entrancement           |  0.3691 |   0.2357 |   0.3280 |  cat |
| Nostalgia              |  0.4610 |   0.4057 |   0.3182 |  cat |
| Identity               |  0.4091 |   0.3704 |   0.2790 |  dim |
| Relief                 |  0.4177 |   0.4302 |   0.2647 |  cat |
| Interest               |  0.4950 |   0.5136 |   0.2511 |  cat |
| Obstruction            |  0.3636 |   0.3339 |   0.2509 |  dim |
| Anxiety                |  0.4840 |   0.5158 |   0.2483 |  cat |
| Confusion              |  0.3154 |   0.2406 |   0.2480 |  cat |
| Annoyance              |  0.4467 |   0.4447 |   0.2454 |  cat |
| Uncomfortable          |  0.6384 |   0.7244 |   0.2446 |  cat |
| Commitment             |  0.4145 |   0.4479 |   0.2321 |  dim |

|                | Total  | Shared | Unique |
|----------------|--------|--------|--------|
| Cat mean r     | 0.3553 | 0.3948 | 0.1754 |
| Dim mean r     | 0.4446 | 0.3902 | 0.3019 |
| Cat/Dim        | 0.799  | 1.012  | 0.581  |

**✓ AI-unique에서 범주 감정 디코딩됨 (cat r=0.175) → ??? 존재!**

#### CLIP 렌즈 (512d)

fMRI variance explained by CLIP: **15.7%**

|                | Total  | Shared | Unique |
|----------------|--------|--------|--------|
| Cat mean r     | 0.3553 | 0.4785 | 0.1127 |
| Dim mean r     | 0.4446 | 0.5083 | 0.2210 |
| Cat/Dim        | 0.799  | 0.941  | 0.510  |

**✓ AI-unique에서도 디코딩됨 (cat r=0.113)**

#### Confound Control (V-JEPA2 + Vision + Semantic, 부분 결과)

fMRI variance explained: **17.1%** (V-JEPA2 alone 16.0%에서 +1.1%)

Unique (AI+Vis+Sem 전부 제거 후):
  Cat mean r: **0.1390** (V-JEPA2 alone unique: 0.1754)
  Dim mean r: **0.2631** (V-JEPA2 alone unique: 0.3019)

→ vision+semantic 추가해도 unique가 살아남음!
→ **"모든 feature로도 설명 못하는 뇌 고유 감정 정보 존재"**

### 핵심 해석

```
1. ??? 존재 확인! (전제 충족 ✓)
   V-JEPA2 unique: cat r=0.175, dim r=0.302
   CLIP unique: cat r=0.113, dim r=0.221
   AI+Vis+Sem unique: cat r=0.139, dim r=0.263
   → 어떤 feature 조합으로도 제거 안 되는 뇌 고유 감정 정보

2. V-JEPA2가 fMRI의 16%만 설명
   → 84%가 AI가 모르는 부분
   → 이 84% 중 감정 정보가 있음 = ???

3. Unique에서 dim > cat (ratio 0.58)
   → ???는 범주보다 차원 쪽에 많음
   → 뇌 고유 정보 = 차원적 처리(VA, approach, control 등)?
   → 이건 Ch3에서 더 분석 필요

4. Shared에서 cat ≈ dim (V-JEPA2: ratio 1.01)
   → AI가 공유하는 부분은 cat/dim 동등

5. V-JEPA2 vs CLIP:
   V-JEPA2 unique cat r=0.175 > CLIP unique cat r=0.113
   → V-JEPA2가 CLIP보다 fMRI를 더 잘 설명 → CLIP 빼고 남는 unique가 더 큼
   → 아니, 반대: V-JEPA2로 빼도 남는 게 0.175 > CLIP으로 빼도 남는 0.113
   → V-JEPA2가 덜 빼니까 더 많이 남음 = V-JEPA2의 설명력이 낮거나 다른 부분 설명
```


### Confound Control 최종 결과 (2026-04-12)

```
CONFOUND CONTROL SUMMARY:
                             Cat unique  Dim unique  C/D    fMRI%
V-JEPA2 only                 0.1754      0.3019     0.581  16.0%
CLIP only                    0.1127      0.2210     0.510  15.7%
V-JEPA2+Vis+Sem              0.1390      0.2631     0.528  17.1%
CLIP+Vis+Sem                 0.0976      0.2103     0.464  16.2%

핵심:
  - 모든 조건에서 AI-unique > 0 → ??? 존재 확인!
  - AI+Vision+Semantic 전부 빼도 cat r=0.098~0.139 남음
  - "어떤 feature로도 설명 못하는 뇌 고유 감정 정보 존재"
  - Unique에서 dim > cat (ratio 0.46~0.58)
    → ???는 차원적 처리에 더 많이 존재
  - V-JEPA2 unique > CLIP unique (V-JEPA2가 덜 설명 → 더 많이 남음)
  - Vision+Semantic 추가해도 fMRI 설명력 +1% 수준 (16%→17%)
    → AI embedding이 vision/semantic 대부분 이미 포함

CLIP 결과 특이점:
  - Craving, Joy, Satisfaction은 unique r < 0 (음수)
  - CLIP이 이 감정들을 "과잉 설명"하여 residual에서 역전됨
```


### Ch2-1 전체 상세 결과 (48 targets × 4 조건, 2026-04-12)

#### V-JEPA2 렌즈 (fMRI var explained: 16.0%)

| Target                    | Total r | Shared r | Unique r | Type |
|---------------------------|---------|----------|----------|------|
| Empathic pain             |  0.5418 |   0.4169 |   0.4157 |  cat |
| Valence                   |  0.5536 |   0.4616 |   0.4130 |  dim |
| Control                   |  0.5582 |   0.4797 |   0.3944 |  dim |
| Approach                  |  0.5475 |   0.4749 |   0.3897 |  dim |
| Upswing                   |  0.4935 |   0.3577 |   0.3887 |  dim |
| Effort                    |  0.4891 |   0.4104 |   0.3703 |  dim |
| Fairness                  |  0.4787 |   0.3757 |   0.3396 |  dim |
| Safety                    |  0.5651 |   0.5394 |   0.3386 |  dim |
| Certainty                 |  0.4539 |   0.3857 |   0.3351 |  dim |
| Entrancement              |  0.3691 |   0.2357 |   0.3280 |  cat |
| Nostalgia                 |  0.4610 |   0.4057 |   0.3182 |  cat |
| Identity                  |  0.4091 |   0.3704 |   0.2790 |  dim |
| Relief                    |  0.4177 |   0.4302 |   0.2647 |  cat |
| Interest                  |  0.4950 |   0.5136 |   0.2511 |  cat |
| Obstruction               |  0.3636 |   0.3339 |   0.2509 |  dim |
| Anxiety                   |  0.4840 |   0.5158 |   0.2483 |  cat |
| Confusion                 |  0.3154 |   0.2406 |   0.2480 |  cat |
| Annoyance                 |  0.4467 |   0.4447 |   0.2454 |  cat |
| Uncomfortable             |  0.6384 |   0.7244 |   0.2446 |  cat |
| Commitment                |  0.4145 |   0.4479 |   0.2321 |  dim |
| Sadness                   |  0.4030 |   0.4363 |   0.2297 |  cat |
| Amusement                 |  0.5130 |   0.5595 |   0.2274 |  cat |
| Romance                   |  0.3939 |   0.4716 |   0.2082 |  cat |
| Attention                 |  0.3304 |   0.2786 |   0.2071 |  dim |
| Awe                       |  0.3703 |   0.5019 |   0.2012 |  cat |
| Envy                      |  0.2656 |   0.2714 |   0.1928 |  cat |
| Sympathy                  |  0.2949 |   0.2726 |   0.1916 |  cat |
| Anger                     |  0.2807 |   0.2680 |   0.1735 |  cat |
| Triumph                   |  0.2607 |   0.2669 |   0.1684 |  cat |
| Adoration                 |  0.4079 |   0.5833 |   0.1644 |  cat |
| Surprise                  |  0.4084 |   0.5049 |   0.1618 |  cat |
| Admiration                |  0.2257 |   0.2030 |   0.1576 |  cat |
| Dominance                 |  0.2551 |   0.2059 |   0.1525 |  dim |
| Excitement                |  0.5121 |   0.6494 |   0.1513 |  cat |
| Awkwardness               |  0.3063 |   0.3062 |   0.1505 |  cat |
| Arousal                   |  0.3125 |   0.3406 |   0.1352 |  dim |
| Disgust                   |  0.2074 |   0.1962 |   0.1234 |  cat |
| Horror                    |  0.3074 |   0.4040 |   0.1208 |  cat |
| Boredom                   |  0.3016 |   0.3889 |   0.1199 |  cat |
| Sexual desire             |  0.2966 |   0.3697 |   0.1108 |  cat |
| Aesthetic appreciation    |  0.5485 |   0.7288 |   0.0975 |  cat |
| Fear                      |  0.1507 |   0.1614 |   0.0954 |  cat |
| Calmness                  |  0.4045 |   0.5580 |   0.0930 |  cat |
| Guilt                     |  0.3163 |   0.4412 |   0.0867 |  cat |
| Craving                   |  0.3763 |   0.4942 |   0.0660 |  cat |
| Contempt                  |  0.1300 |   0.2037 |   0.0368 |  cat |
| Satisfaction              |  0.1510 |   0.1841 |   0.0357 |  cat |
| Joy                       |  0.0779 |   0.0689 |   0.0340 |  cat |
| **CAT MEAN**              |  0.3553 |   0.3948 |   0.1754 |      |
| **DIM MEAN**              |  0.4446 |   0.3902 |   0.3019 |      |
| **Cat/Dim**               |   0.799 |    1.012 |    0.581 |      |

#### CLIP 렌즈 (fMRI var explained: 15.7%)

| Target                    | Total r | Shared r | Unique r | Type |
|---------------------------|---------|----------|----------|------|
| Empathic pain             |  0.5418 |   0.5729 |   0.3216 |  cat |
| Upswing                   |  0.4935 |   0.4929 |   0.3089 |  dim |
| Control                   |  0.5582 |   0.6038 |   0.2874 |  dim |
| Valence                   |  0.5536 |   0.6382 |   0.2737 |  dim |
| Entrancement              |  0.3691 |   0.3010 |   0.2729 |  cat |
| Approach                  |  0.5475 |   0.6396 |   0.2717 |  dim |
| Effort                    |  0.4891 |   0.5482 |   0.2581 |  dim |
| Certainty                 |  0.4539 |   0.5075 |   0.2452 |  dim |
| Fairness                  |  0.4787 |   0.5546 |   0.2355 |  dim |
| Nostalgia                 |  0.4610 |   0.5345 |   0.2290 |  cat |
| Safety                    |  0.5651 |   0.6749 |   0.2110 |  dim |
| Confusion                 |  0.3154 |   0.3307 |   0.2072 |  cat |
| Identity                  |  0.4091 |   0.4903 |   0.2017 |  dim |
| Annoyance                 |  0.4467 |   0.4972 |   0.1883 |  cat |
| Attention                 |  0.3304 |   0.3427 |   0.1797 |  dim |
| Obstruction               |  0.3636 |   0.4364 |   0.1782 |  dim |
| Relief                    |  0.4177 |   0.5232 |   0.1715 |  cat |
| Excitement                |  0.5121 |   0.6589 |   0.1623 |  cat |
| Dominance                 |  0.2551 |   0.2806 |   0.1595 |  dim |
| Commitment                |  0.4145 |   0.5535 |   0.1572 |  dim |
| Amusement                 |  0.5130 |   0.6571 |   0.1569 |  cat |
| Triumph                   |  0.2607 |   0.2717 |   0.1488 |  cat |
| Anxiety                   |  0.4840 |   0.6094 |   0.1463 |  cat |
| Awe                       |  0.3703 |   0.5648 |   0.1446 |  cat |
| Interest                  |  0.4950 |   0.6366 |   0.1417 |  cat |
| Awkwardness               |  0.3063 |   0.3758 |   0.1373 |  cat |
| Admiration                |  0.2257 |   0.2612 |   0.1356 |  cat |
| Arousal                   |  0.3125 |   0.3524 |   0.1258 |  dim |
| Romance                   |  0.3939 |   0.5700 |   0.1245 |  cat |
| Calmness                  |  0.4045 |   0.5825 |   0.1211 |  cat |
| Horror                    |  0.3074 |   0.4373 |   0.1122 |  cat |
| Boredom                   |  0.3016 |   0.3966 |   0.1038 |  cat |
| Anger                     |  0.2807 |   0.4144 |   0.0980 |  cat |
| Aesthetic appreciation    |  0.5485 |   0.7664 |   0.0855 |  cat |
| Sexual desire             |  0.2966 |   0.3527 |   0.0853 |  cat |
| Guilt                     |  0.3163 |   0.4392 |   0.0834 |  cat |
| Sadness                   |  0.4030 |   0.6419 |   0.0783 |  cat |
| Envy                      |  0.2656 |   0.3744 |   0.0765 |  cat |
| Fear                      |  0.1507 |   0.2126 |   0.0722 |  cat |
| Adoration                 |  0.4079 |   0.6917 |   0.0708 |  cat |
| Sympathy                  |  0.2949 |   0.4851 |   0.0644 |  cat |
| Uncomfortable             |  0.6384 |   0.8178 |   0.0558 |  cat |
| Surprise                  |  0.4084 |   0.7090 |   0.0511 |  cat |
| Disgust                   |  0.2074 |   0.2515 |   0.0486 |  cat |
| Contempt                  |  0.1300 |   0.2231 |   0.0378 |  cat |
| Craving                   |  0.3763 |   0.6677 |  -0.0221 |  cat |
| Joy                       |  0.0779 |   0.1864 |  -0.0314 |  cat |
| Satisfaction              |  0.1510 |   0.2537 |  -0.0465 |  cat |
| **CAT MEAN**              |  0.3553 |   0.4785 |   0.1127 |      |
| **DIM MEAN**              |  0.4446 |   0.5083 |   0.2210 |      |
| **Cat/Dim**               |   0.799 |    0.941 |    0.510 |      |

#### Confound Control Summary

| Condition              | Cat unique | Dim unique | Cat/Dim | fMRI explained |
|------------------------|------------|------------|---------|----------------|
| V-JEPA2 only           |     0.1754 |     0.3019 |   0.581 |          16.0% |
| CLIP only              |     0.1127 |     0.2210 |   0.510 |          15.7% |
| V-JEPA2+Vis+Sem        |     0.1390 |     0.2631 |   0.528 |          17.1% |
| CLIP+Vis+Sem           |     0.0976 |     0.2103 |   0.464 |          16.2% |

