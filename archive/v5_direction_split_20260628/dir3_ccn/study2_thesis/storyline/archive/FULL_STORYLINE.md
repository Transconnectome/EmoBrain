# The Brain-Predictable Subspace of V-JEPA2 is Categorically Organized

**Full Research Storyline — From Motivation to Current Results**  
**Last updated:** 2026-04-09

---

## 0. One-Sentence Summary

> 뇌가 self-supervised video model(V-JEPA2)에서 선택적으로 읽을 수 있는 표상 축은 범주 감정(categorical emotion)으로 조직되어 있다. 반대로 V-JEPA2는 뇌의 어떤 주요 축도 읽을 수 없다. 이 비대칭은 뇌가 V-JEPA2 안의 숨겨진 affective subspace를 능동적으로 선택함을 시사한다.

---

## 1. Motivation

### 배경

V-JEPA2는 감정 레이블 없이, 오직 비디오의 시각적 패턴만으로 학습한 self-supervised video model이다. 이런 모델의 표상이 인간 뇌의 표상과 부분적으로 정렬된다는 것이 선행 연구들에서 보고되어 왔다.

### 핵심 질문

> **뇌가 V-JEPA2에서 "읽을 수 있는" 부분은 정확히 무엇인가?**
> **그리고 그 부분이 감정과 관련이 있는가?**

V-JEPA2는 1,408차원의 표상 공간을 가진다. 뇌가 이 전부를 읽을 수 있는 것은 아닐 거다. 일부만 읽을 수 있다면, 그 일부는 어떤 의미를 가지는가?

---

## 2. Data

| 데이터 | 형태 | 설명 |
|--------|------|------|
| V-JEPA2 embedding | (2196, 1408) | 비디오 모델이 본 것 |
| Brain-JEPA embedding | (5, 2196, 768) → mean → (2196, 768) | 뇌가 반응한 것 (5명 평균) |
| 34 emotion ratings | (2196, 34) | 범주 감정 행동 rating |
| Arousal/Valence | (2196, 2) | 연속 감정 차원 |

- 자극: 2,196개 감정 유발 비디오 클립 (~3초, Cowen & Keltner 2017)
- 뇌 데이터: Horikawa et al. (2020), 5명, 전뇌 fMRI, 3T

---

## 3. Analysis 1: Forward PCA+Ridge — "V-JEPA2의 축 중에서 뇌가 읽는 것은?"

### 방법

```
Step 1: V-JEPA2 (2196, 1408) → PCA → 100개 PC
        PCA는 V-JEPA2 데이터만 본다. 뇌 데이터는 관여 안 함.
        축 정의 주체 = V-JEPA2 단독 (분산 기준)

Step 2: 각 PC에 대해 독립적으로:
        X = Brain-JEPA (2196, 768)
        y = V-JEPA2 PC_i 값 (2196,)
        Ridge regression (5-fold CV) → R²

Step 3: Permutation test (n=1000) + FDR correction (BH, q<0.05)
        PC_i 값을 무작위 shuffle → null R² → p-value
```

### Figure 1A: R² per V-JEPA2 PC

X축: V-JEPA2 PC index (1~40)  
Y축: R² (Brain-JEPA → V-JEPA2 PC 예측 정확도)

- 파란 막대: brain-predictable PCs (PC1, 2, 3) — FDR q < 0.001
- 회색 막대: brain-unpredictable PCs — R² ≈ 0
- 별표 (*): permutation test 유의

**결과:**

| PC | R² | FDR q | Brain-predictable? |
|----|-----|-------|--------------------|
| **PC1** | **0.373** | < 0.001 | Yes |
| **PC2** | **0.075** | < 0.001 | Yes |
| **PC3** | **0.088** | < 0.001 | Yes |
| PC4 | 0.000 | < 0.001 (clipping artifact, excluded) | No |
| PC5–100 | 0.000 | 1.000 | No |

→ **100개 축 중 딱 3개만 뇌가 읽을 수 있다.**

### Figure 1B: Brain-predictable PCs는 감정과 더 연결된다

X축: Brain-predictable (n=3) vs Brain-unpredictable (n=97)  
Y축: mean max |r| with 34 emotions

- 파란 막대 + 흰 점: brain-predictable PC들의 평균 max|r| → 높음
- 회색 막대 + 흰 점: brain-unpredictable PC들 → 낮음

> 뇌가 선택적으로 읽는 V-JEPA2의 축이 바로 감정 표상이다.

---

## 4. Analysis 2: 범주 감정 vs 연속 감정

### 방법

```
X = brain-pred subspace (PC1-3, 3차원)
y = 34개 감정 범주 각각 / Arousal / Valence
Ridge regression (5-fold CV) → R²
```

### Figure 2A: 34 emotion + Arousal/Valence decoding R²

X축: 감정 카테고리 (R² 내림차순) + Arousal, Valence  
Y축: Decoding R²

- 파란 막대 (34개): 범주 감정 R²
- 빨간 막대 (2개): Arousal, Valence R²
- 점선: 각 그룹의 평균

**Top 10 decoded emotions:**

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

### Figure 2B: Category / V-A ratio

X축: Brain-pred subspace vs Full V-JEPA2  
Y축: mean R²_cat / mean R²_VA

| Subspace | Cat R² | AV R² | Cat/VA Ratio |
|----------|--------|-------|--------------|
| **Brain-pred (PC1-3)** | 0.055 | 0.038 | **1.44** |
| Full space (100 PCs) | 0.170 | 0.135 | 1.26 |

> Brain-predictable subspace는 범주 감정에 **불균형적으로 편향**됨 (ratio 1.44 > 1.26).

---

## 5. Analysis 3: Reverse PCA+Ridge — "V-JEPA2가 뇌의 축을 읽을 수 있는가?"

### 왜 이 분석이 필요한가

Analysis 1은 Brain → V-JEPA2 PC 방향이었다. 반대 방향도 확인해야 완전한 그림이 된다.

```
Forward:  Brain(768)    → Ridge → V-JEPA2 PC_i   "뇌가 V-JEPA2의 어떤 축을 읽는가?"
Reverse:  V-JEPA2(1408) → Ridge → Brain PC_j     "V-JEPA2가 뇌의 어떤 축을 설명하는가?"
```

### 방법

```
Step 1: Brain-JEPA mean (2196, 768) → PCA → 100개 Brain PC
Step 2: V-JEPA2 (2196, 1408) → Ridge → Brain PC_j 예측 (5-fold CV)
Step 3: Permutation test (n=1000) + FDR correction
```

### 결과: 완전한 비대칭

```
Forward:  Brain → V-JEPA2 PC → 3개 유의 (R²=0.373, 0.088, 0.075)
Reverse:  V-JEPA2 → Brain PC → 0개 유의 (모든 R²=0.000)
```

**V-JEPA2는 뇌의 어떤 주요 분산 축도 예측할 수 없다.**

### Brain PCA 분산 구조

| Brain PC | 분산 설명 비율 | 누적 |
|----------|-------------|------|
| BPC1 | 32.7% | 32.7% |
| BPC2 | 16.3% | 49.0% |
| BPC3 | 12.0% | 61.0% |
| BPC4 | 6.7% | 67.6% |
| BPC5 | 6.2% | 73.8% |

→ Brain PC1이 전체 분산의 32.7%를 차지하지만, V-JEPA2로 예측 불가 (R²=0).

### Brain PC들의 감정 프로필

| Brain PC | var% | Top emotion | A | V |
|----------|------|------------|---|---|
| BPC1 | 32.7 | Annoyance (-0.22) | -0.10 | +0.08 |
| BPC2 | 16.3 | Guilt (+0.15) | +0.15 | +0.06 |
| BPC3 | 12.0 | Interest (-0.20) | ~0 | +0.19 |
| BPC4 | 6.7 | Amusement (+0.18) | -0.10 | -0.10 |
| BPC5 | 6.2 | Relief (-0.11) | ~0 | -0.11 |

→ Brain PC들의 감정 상관이 V-JEPA2 brain-pred PC들보다 **약함** (max|r| ≈ 0.1–0.2 vs 0.3–0.4).

### Brain PC들의 감정 디코딩: VA > Category

| Brain subspace | Cat R² | AV R² | Cat/VA Ratio |
|---------------|--------|-------|--------------|
| Brain PC1-3 | 0.016 | 0.026 | **0.61** |
| Brain PC1-10 | 0.043 | 0.071 | **0.60** |
| Brain all 100 | 0.055 | 0.091 | **0.60** |

→ **Cat/VA ratio = 0.60** — VA가 범주보다 더 잘 디코딩됨. Forward의 1.44와 **완전히 반대.**

### Figure: Forward vs Reverse 3-panel comparison

**Panel A:** Forward R² — PC1-3만 높고 나머지 0  
**Panel B:** Reverse R² — 전부 0 (빈 그래프)  
**Panel C:** CCA — 점진적 감소

### Figure: Forward vs Reverse Cat/VA ratio

- Forward (Brain→Video): **1.44** (범주 > VA)
- Reverse (Video→Brain): **0.60** (VA > 범주)

---

## 6. Analysis 4: CCA — "뇌와 V-JEPA2가 함께 찾는 공유 축은?"

### 방법

```
V-JEPA2 (2196, 1408) → StandardScaler → PCA(100) → (2196, 100)  [분산 69.3% 보존]
Brain   (2196, 768)  → StandardScaler → PCA(100) → (2196, 100)  [분산 99.5% 보존]
                              ↓
                    CCA(100 components)
양쪽에서 동시에 상관을 최대화하는 방향 쌍을 찾는다
```

### Figure: CCA 100 canonical correlation spectrum

X축: CC index (1~100)  
Y축: Canonical correlation (r)

- 초록 (r > 0.3): substantial 공유 — 27개
- 연두 (0.1 < r < 0.3): 약한 공유 — 48개
- 회색 (r < 0.1): 무시 가능 — 25개

**CCA 100 결과 (PCA 100 → CCA 100):**

| 구간 | CCs | r 범위 |
|------|-----|--------|
| CC1-5 | 강한 공유 | 0.77 – 0.57 |
| CC6-15 | 중간 공유 | 0.52 – 0.39 |
| CC16-27 | 약-중간 | 0.37 – 0.31 |
| CC28-75 | 약한 공유 | 0.30 – 0.10 |
| CC76-100 | 무시 가능 | 0.09 – 0.00 |

**Top 5 CCs:**

| CC | r |
|----|---|
| CC1 | **0.774** |
| CC2 | 0.679 |
| CC3 | 0.649 |
| CC4 | 0.608 |
| CC5 | 0.572 |

**유의성 (Permutation n=1000, FDR q<0.05):**
- 88/100 CC 유의
- CC83 (r=0.063) 부터 비유의
- r > 0.3: 27개 (substantial), r > 0.1: 75개

**CC 감정 프로필 (CCA 100 최종 결과):**

| CC | r | Top emotion | 2nd | 3rd | A | V |
|----|---|-----------|-----|-----|---|---|
| CC1 | **0.774** | **Annoyance (+0.46)** | Interest (+0.34) | Anxiety (+0.34) | +0.24 | -0.15 |
| CC2 | 0.679 | **Aesthetic apprec. (-0.44)** | Excitement (-0.37) | Relief (-0.30) | -0.11 | +0.02 |
| CC3 | 0.649 | Interest (-0.18) | Empathic pain (+0.18) | Anxiety (-0.17) | +0.01 | +0.03 |
| CC4 | 0.608 | Uncomfortable (-0.29) | Sadness (+0.22) | Surprise (-0.20) | -0.12 | +0.02 |
| CC5 | 0.571 | Aesthetic apprec. (-0.19) | Amusement (+0.18) | Excitement (-0.13) | -0.08 | +0.01 |
| CC6 | 0.522 | **Uncomfortable (+0.33)** | Awe (-0.27) | Adoration (-0.24) | +0.02 | -0.19 |
| CC7 | 0.495 | Uncomfortable (+0.18) | Nostalgia (-0.18) | Sympathy (-0.14) | +0.02 | +0.17 |
| CC8 | 0.494 | **Adoration (-0.27)** | Awe (-0.16) | Guilt (+0.15) | +0.08 | -0.07 |
| CC9 | 0.460 | Empathic pain (+0.20) | Nostalgia (+0.18) | Sympathy (+0.16) | -0.04 | -0.17 |
| CC10 | 0.457 | Uncomfortable (+0.16) | Surprise (+0.14) | Aesthetic apprec. (+0.11) | -0.01 | +0.10 |

→ 각 CC가 **구체적 범주 감정**과 연결. Arousal/Valence 상관은 약함.
→ CC1=Annoyance/불안축, CC2=미학/흥분축, CC4=불편/슬픔축, CC6=불편/경외축, CC8=사랑축, CC9=공감축

**디코딩 비교:**

| Method | Dims | Cat R² | AV R² | Cat/VA |
|--------|------|--------|-------|--------|
| CCA-sig (88) | 88 | 0.180 | 0.161 | 1.12 |
| CCA-all (100) | 100 | 0.182 | 0.155 | 1.17 |
| PCA PC1-3 | 3 | 0.053 | 0.035 | **1.51** |
| PCA all 100 | 100 | 0.182 | 0.155 | 1.17 |

**참여자 간 안정성 (CCA 100):**

| Subject | CC1 | CC2 | CC3 |
|---------|-----|-----|-----|
| 1 | 0.737 | 0.611 | 0.569 |
| 2 | 0.714 | 0.622 | 0.613 |
| 3 | 0.706 | 0.618 | 0.553 |
| 4 | 0.732 | 0.597 | 0.564 |
| 5 | 0.708 | 0.556 | 0.530 |
| **Mean ± SD** | **0.719 ± 0.013** | | |

---

## 7. 전체 비교: 세 가지 방법이 말하는 것

### Spectrum 비교

```
Forward PCA+Ridge:    ███░░░░░░░░░░░░░░░░░  3/100 유의
Reverse PCA+Ridge:    ░░░░░░░░░░░░░░░░░░░░  0/100 유의
CCA:                  ████████████████████░  27/100 substantial (r>0.3)
```

### 감정 디코딩 비교

| Method | Dims | Cat R² | AV R² | Cat/VA Ratio |
|--------|------|--------|-------|--------------|
| Forward PCA PC1-3 | 3 | 0.055 | 0.038 | **1.44** |
| Forward PCA PC1-10 | 10 | 0.109 | 0.070 | **1.55** |
| Forward PCA all 100 | 100 | 0.170 | 0.135 | 1.26 |
| CCA-sig (88, PCA100) | 88 | 0.180 | 0.161 | 1.12 |
| CCA-all (100, PCA100) | 100 | 0.182 | 0.155 | 1.17 |
| Reverse Brain PC1-3 | 3 | 0.016 | 0.026 | **0.61** |
| Reverse Brain PC1-10 | 10 | 0.043 | 0.071 | **0.60** |
| Reverse Brain all 100 | 100 | 0.055 | 0.091 | **0.60** |

### 핵심 발견

**1. 방향 비대칭 (Forward ≠ Reverse)**
- Brain → V-JEPA2 PC: 3개 유의 (R² up to 0.37)
- V-JEPA2 → Brain PC: 0개 유의 (모든 R²=0)
- → 뇌가 V-JEPA2를 능동적으로 읽는 것이지, V-JEPA2가 뇌를 반영하는 게 아니다

**2. 감정 구조 비대칭 (Category vs VA)**
- Forward brain-pred subspace: Cat/VA = 1.44 (범주 > VA)
- Reverse brain PCs: Cat/VA = 0.60 (VA > 범주)
- → 뇌의 전반적 분산 구조는 VA 편향이지만, V-JEPA2를 읽을 때는 범주를 선택적으로 추출

**3. CCA가 보여주는 풍부한 공유 구조**
- 27개 CC with r > 0.3 (CC1=0.774)
- 참여자 간 안정적 (SD=0.013)
- CC들이 구체적 범주 감정과 연결 (Annoyance, Aesthetic appreciation, ...)

---

## 8. 해석: 왜 이런 비대칭이 나오는가?

### 뇌의 주요 분산 ≠ 감정

Brain PC1 (분산 32.7%)은 감정이 아니라 저수준 처리(시각, 주의 등)에 가까울 가능성이 높다:
- max|r| = 0.22 (약한 감정 상관)
- V-JEPA2가 이걸 예측 못함 = V-JEPA2가 인코딩하는 시각 특성과 뇌의 주요 활동이 다름

### V-JEPA2의 주요 분산 중 일부 = 뇌의 감정 표상과 겹침

V-JEPA2 PC1 (분산 가장 큼)은 뇌가 예측 가능 (R²=0.37):
- 이건 V-JEPA2의 시각적 주요 특성이 우연히 뇌의 감정 반응과 겹쳤기 때문
- PC1의 max|r| ≈ 0.44 (Annoyance) — 강한 감정 상관

### 결론

> 뇌의 표상 공간과 V-JEPA2의 표상 공간은 전체적으로 정렬되어 있지 않다.
> 그러나 V-JEPA2 안에 "숨겨진" 감정 하위 공간이 존재하고,
> 뇌는 이것을 선택적으로 읽는다.
> 이 하위 공간은 VA가 아닌 범주 감정으로 조직되어 있다.

---

## 9. Summary of All Key Numbers

| Metric | Value |
|--------|-------|
| **Data** | |
| V-JEPA2 dim | 1,408 |
| Brain-JEPA dim | 768 |
| Videos | 2,196 |
| Subjects | 5 |
| **Forward PCA+Ridge (Brain → V-JEPA2 PC)** | |
| Significant PCs | 3 (PC1, 2, 3) |
| PC1 R² | 0.373 |
| PC2 R² | 0.075 |
| PC3 R² | 0.088 |
| Cat/VA ratio (brain-pred) | 1.44 |
| Top decoded emotion | Aesthetic appreciation (R²=0.323) |
| **Reverse PCA+Ridge (V-JEPA2 → Brain PC)** | |
| Significant PCs | **0** |
| All R² | **0.000** |
| Cat/VA ratio (Brain PCs) | **0.60** |
| Brain PC1 var explained | 32.7% |
| **CCA (PCA100 → CCA100, final)** | |
| CC1 canonical r | 0.774 |
| Significant CCs (FDR<0.05) | 88/100 |
| CCs with r > 0.3 | 27 |
| CCs with r > 0.1 | 75 |
| CC1 subject stability (SD) | 0.013 |
| Cat/VA ratio (CCA-sig 88) | 1.12 |
| Cat/VA ratio (CCA-all 100) | 1.17 |
| **Statistics** | |
| Permutation test n | 1,000 |
| FDR method | Benjamini-Hochberg, q < 0.05 |

---

## 10. Figure Index

All figures: `/pscratch/sd/s/sjmoon/EmoFM/main/figures/`

| Figure | File | Content |
|--------|------|---------|
| 1A | `figure1_brain_predictable_subspace` | R² per V-JEPA2 PC (40개, PC1-3 파랑) |
| 1B | (same) | Mean max\|r\| brain-pred vs unpred |
| 2A | `figure2_categorical_organization` | 34 emotion + AV decoding R² |
| 2B | (same) | Cat/VA ratio: brain-pred(1.44) vs full(1.26) |
| 3A | `figure3_cca_shared_space` | Canonical correlations + null 95th %ile |
| 3B | (same) | CC1-5 × emotion heatmap |
| 4A | `figure4_method_comparison` | Decoding R²: 4 methods |
| 4B | (same) | Cat/VA ratio: 4 methods |
| 5 | `figure5_subject_cca_stability` | Subject-level CCA |
| 6 | `figure6_cca_full_heatmap` | All CCs × 34 emotions |
| 7 | `figure7_pca_vs_cca_comparison` | A: PCA R², B: CCA r, C: Cat/VA ratio |
| NEW | `figure_cca100_spectrum` | CCA 100 CC spectrum (초록/연두/회색) |
| NEW | `figure_three_methods_comparison` | Forward / Reverse / CCA 나란히 |
| NEW | `figure_forward_vs_reverse_ratio` | Cat/VA ratio: 1.44 vs 0.60 |

---

## 11. Code Index

| Script | What it does | Bash |
|--------|-------------|------|
| `10_cka_rsa_dim_analysis.py` | Forward: Brain → V-JEPA2 PC R² | `run_10.sh` |
| `11_pc_emotion_correlation.py` | PC × 34 emotion Spearman r | `run_11.sh` |
| `17_av2d_comparison.py` | Emotion decoding from brain-pred subspace | `run_17_av2d.sh` |
| `19_permutation_test.py` | Permutation test for forward PCA+Ridge | `run_19_*.sh` |
| `21_cca_brain_video.py` | CCA 100: Brain ↔ V-JEPA2 + permutation | `run_21_cca.sh` |
| `21b_cca_100_noperm.py` | CCA 100 fast (no permutation) | `run_21b_cca100.sh` |
| `23_reverse_pca_ridge.py` | Reverse: V-JEPA2 → Brain PC + permutation | `run_23_reverse.sh` |
| `24_generate_all_figures.py` | All figures (Fig 1-8) | `run_24_figures.sh` |
| `25_quick_cca100_figure.py` | Quick CCA100 + Forward/Reverse figures | `run_25_quick_fig.sh` |

---

## 12. Next Steps

### 진행 중
- CCA 100 permutation test (run_21_cca.sh, 진행 중)
- CCA 100 emotion correlation + decoding (run_21b_cca100.sh)

### 즉시 가능
1. **Variance Partitioning** — Behavior = f(Stimulus) + f(Brain) + shared
2. **Brain Residual** — V-JEPA2로 설명 못하는 뇌의 고유 감정 정보
3. **Partial Mantel** — r(brain, behavior | stimulus) > 0?

### 장기 방향
4. **Brain-tuning** — V-JEPA2를 뇌 반응에 fine-tune
5. **Multi-model** — V-JEPA2 vs VideoMAE vs CLIP 비교
6. **자체 fMRI** — 한국 참여자, VE-8/EMDB 자극

---

## 13. Publication Plan

| Venue | Deadline | Status |
|-------|----------|--------|
| CCN 2026 (2-page) | Submitted | Analysis 1+2 |
| NeurIPS 2026 Workshop | Sep-Oct 2026 | All analyses |
| IEEE TAFFC (journal) | Rolling | + Brain-tuning |
