# Experiment 12: Brain-Predictable Subspace — Category vs Dimension 설명력 비교

**Date**: 2026-04-02  
**Script**: `12_subspace_cat_vs_dim.py`  
**기반**: Exp 11의 brain-pred mask (V-JEPA2 PC1~3, CLIP PC1,2,3,5,6,7)

---

## 실험 목적

Brain-predictable subspace (소수 PC)가 설명하는 것이  
**고차원 감정 카테고리(34개)**인가, **A/V/D 저차원 affective dimension**인가?

---

## 방법

- brain-pred PCs만 feature로 사용 (`pred`)
- brain-unpred PCs만 feature로 사용 (`unpred`)
- 전체 100 PCs feature로 사용 (`all`)
- 각각에 대해 34개 emotion score + Arousal/Valence/Dominance를 Ridge 5-fold CV로 예측 → R²
- Efficiency = R²(pred) / R²(all): pred subspace가 전체 정보의 몇 %를 커버하는가
- 단, `all R² < 0.05`인 target은 모델 전체가 사실상 예측하지 못한 경우로 보고 efficiency 해석에서 제외 (`—`)

---

## Brain-pred PC 목록

- **V-JEPA2**: PC1, PC2, PC3 (n=3, indices [0,1,2])
- **CLIP**: PC1, PC2, PC3, PC5, PC6, PC7 (n=6, indices [0,1,2,4,5,6])

---

## 전체 Raw 결과 테이블

### V-JEPA2

| Target | pred R² | unpred R² | all R² | eff (pred/all) |
|--------|---------|-----------|--------|----------------|
| Admiration | 0.0235 | 0.0000 | 0.0027 | — |
| Adoration | 0.0805 | 0.2677 | 0.3597 | 0.224 |
| Aesthetic appreciation | **0.3231** | 0.1687 | 0.5509 | 0.587 |
| Amusement | 0.1159 | 0.1805 | 0.3219 | 0.360 |
| Anger | 0.0118 | 0.0512 | 0.0671 | 0.176 |
| Anxiety | 0.0611 | 0.1660 | 0.2394 | 0.255 |
| Awe | 0.0222 | 0.2219 | 0.2538 | 0.088 |
| Awkwardness | 0.0308 | 0.0487 | 0.0839 | 0.367 |
| Boredom | 0.0196 | 0.0832 | 0.1228 | 0.160 |
| Calmness | 0.1361 | 0.1284 | 0.3176 | 0.429 |
| Confusion | 0.0000 | 0.0072 | 0.0095 | — |
| Contempt | 0.0000 | 0.0204 | 0.0208 | — |
| Craving | 0.0166 | 0.3386 | 0.3643 | 0.046 |
| Disgust | 0.0088 | 0.0000 | 0.0000 | — |
| Empathic pain | 0.0741 | 0.0953 | 0.1823 | 0.407 |
| Entrancement | 0.0024 | 0.0000 | 0.0066 | — |
| Excitement | **0.2001** | 0.1527 | 0.3955 | 0.506 |
| Fear | 0.0000 | 0.0000 | 0.0000 | — |
| Horror | 0.0570 | 0.0629 | 0.1447 | 0.394 |
| Interest | 0.0598 | 0.1963 | 0.2667 | 0.224 |
| Joy | 0.0028 | 0.0000 | 0.0000 | — |
| Nostalgia | 0.0167 | 0.1318 | 0.1561 | 0.107 |
| Relief | 0.0576 | 0.0720 | 0.1552 | 0.371 |
| Romance | 0.0793 | 0.1241 | 0.2235 | 0.355 |
| Sadness | 0.0094 | 0.1832 | 0.1975 | 0.048 |
| Satisfaction | 0.0071 | 0.0000 | 0.0000 | — |
| Sexual desire | 0.0313 | 0.0852 | 0.1221 | 0.257 |
| Surprise | 0.0450 | 0.2234 | 0.2763 | 0.163 |
| Sympathy | 0.0059 | 0.0322 | 0.0440 | — |
| Triumph | 0.0128 | 0.0306 | 0.0465 | — |
| Uncomfortable | **0.1715** | 0.3005 | 0.4990 | 0.344 |
| Annoyance | 0.1057 | 0.0678 | 0.1828 | 0.578 |
| Envy | 0.0293 | 0.0000 | 0.0241 | — |
| Guilt | 0.0518 | 0.0518 | 0.1517 | 0.341 |
| **Arousal** | **0.0651** | 0.0037 | 0.0889 | **0.732** |
| **Valence** | **0.0112** | 0.1562 | 0.1817 | **0.062** |
| **Dominance** | **0.0000** | 0.0000 | 0.0004 | — |

**Summary (V-JEPA2):**
- mean R²(34 cat) — pred: **0.0550**, all: 0.1703
- mean R²(A/V/D) — pred: **0.0254**, all: 0.0903
- **ratio cat/dim (pred subspace): 2.162**
- mean efficiency cat: 0.295 (`all R² >= 0.05` target만 포함; n=23)
- mean efficiency dim: 0.397 (`Arousal`, `Valence`만 포함; `Dominance` 제외)

---

### CLIP

| Target | pred R² | unpred R² | all R² | eff (pred/all) |
|--------|---------|-----------|--------|----------------|
| Admiration | 0.0266 | 0.0308 | 0.0695 | 0.383 |
| Adoration | 0.1424 | 0.3933 | 0.5462 | 0.261 |
| Aesthetic appreciation | **0.4473** | 0.1468 | 0.6505 | 0.688 |
| Amusement | **0.3397** | 0.0913 | 0.4711 | 0.721 |
| Anger | 0.1818 | 0.0325 | 0.2321 | 0.783 |
| Anxiety | 0.2036 | 0.1609 | 0.3920 | 0.520 |
| Awe | 0.2096 | 0.1493 | 0.3850 | 0.545 |
| Awkwardness | 0.0913 | 0.0242 | 0.1281 | 0.713 |
| Boredom | 0.1011 | 0.0512 | 0.1738 | 0.581 |
| Calmness | 0.1655 | 0.1442 | 0.3611 | 0.458 |
| Confusion | 0.0291 | 0.0545 | 0.0934 | 0.311 |
| Contempt | 0.0493 | 0.0000 | 0.0595 | 0.828 |
| Craving | 0.1482 | 0.4409 | 0.6394 | 0.232 |
| Disgust | 0.0847 | 0.0000 | 0.0542 | 1.564 |
| Empathic pain | **0.1964** | 0.1483 | 0.3671 | 0.535 |
| Entrancement | 0.0564 | 0.0112 | 0.0774 | 0.728 |
| Excitement | **0.2866** | 0.1364 | 0.4663 | 0.615 |
| Fear | 0.0385 | 0.0000 | 0.0123 | — |
| Horror | 0.1709 | 0.0085 | 0.2083 | 0.821 |
| Interest | **0.2536** | 0.1525 | 0.4300 | 0.590 |
| Joy | 0.0289 | 0.0000 | 0.0094 | — |
| Nostalgia | 0.2100 | 0.0699 | 0.2999 | 0.700 |
| Relief | 0.1818 | 0.0356 | 0.2616 | 0.695 |
| Romance | 0.1236 | 0.2418 | 0.3879 | 0.319 |
| Sadness | 0.1922 | 0.2808 | 0.5251 | 0.366 |
| Satisfaction | 0.0544 | 0.0405 | 0.1109 | 0.490 |
| Sexual desire | 0.1058 | 0.0099 | 0.1260 | 0.839 |
| **Surprise** | **0.3308** | 0.2437 | 0.6074 | 0.545 |
| Sympathy | 0.1959 | 0.0632 | 0.2795 | 0.701 |
| Triumph | 0.0436 | 0.0290 | 0.0767 | 0.569 |
| **Uncomfortable** | **0.5379** | 0.1367 | 0.7275 | 0.739 |
| Annoyance | 0.1882 | 0.0534 | 0.2600 | 0.724 |
| Envy | 0.1030 | 0.0609 | 0.1764 | 0.584 |
| Guilt | 0.1211 | 0.0148 | 0.2078 | 0.583 |
| **Arousal** | **0.0621** | 0.0585 | 0.1355 | **0.459** |
| **Valence** | **0.2706** | 0.1800 | 0.4787 | **0.565** |
| **Dominance** | **0.0565** | 0.0000 | 0.0639 | **0.884** |

**Summary (CLIP):**
- mean R²(34 cat) — pred: **0.1659**, all: 0.2904
- mean R²(A/V/D) — pred: **0.1297**, all: 0.2260
- **ratio cat/dim (pred subspace): 1.279**
- mean efficiency cat: 0.617 (`all R² >= 0.05` target만 포함; n=32)
- mean efficiency dim: 0.636 (3개 dimension 모두 포함)

---

## Top/Bottom 감정 (pred subspace R² 기준)

### V-JEPA2 Top 10

| 순위 | 감정 | pred R² | all R² | eff |
|------|------|---------|--------|-----|
| 1 | Aesthetic appreciation | 0.3231 | 0.5509 | 0.587 |
| 2 | Excitement | 0.2001 | 0.3955 | 0.506 |
| 3 | Uncomfortable | 0.1715 | 0.4990 | 0.344 |
| 4 | Calmness | 0.1361 | 0.3176 | 0.429 |
| 5 | Amusement | 0.1159 | 0.3219 | 0.360 |
| 6 | Annoyance | 0.1057 | 0.1828 | 0.578 |
| 7 | Adoration | 0.0805 | 0.3597 | 0.224 |
| 8 | Romance | 0.0793 | 0.2235 | 0.355 |
| 9 | Empathic pain | 0.0741 | 0.1823 | 0.407 |
| 10 | Anxiety | 0.0611 | 0.2394 | 0.255 |

### V-JEPA2 Bottom 5

| 감정 | pred R² | all R² | eff |
|------|---------|--------|-----|
| Joy | 0.0028 | 0.0000 | — |
| Entrancement | 0.0024 | 0.0066 | — |
| Confusion | 0.0000 | 0.0095 | — |
| Contempt | 0.0000 | 0.0208 | — |
| Fear | 0.0000 | 0.0000 | — |

### CLIP Top 10

| 순위 | 감정 | pred R² | all R² | eff |
|------|------|---------|--------|-----|
| 1 | Uncomfortable | 0.5379 | 0.7275 | 0.739 |
| 2 | Aesthetic appreciation | 0.4473 | 0.6505 | 0.688 |
| 3 | Amusement | 0.3397 | 0.4711 | 0.721 |
| 4 | Surprise | 0.3308 | 0.6074 | 0.545 |
| 5 | Excitement | 0.2866 | 0.4663 | 0.615 |
| 6 | Interest | 0.2536 | 0.4300 | 0.590 |
| 7 | Nostalgia | 0.2100 | 0.2999 | 0.700 |
| 8 | Awe | 0.2096 | 0.3850 | 0.545 |
| 9 | Anxiety | 0.2036 | 0.3920 | 0.520 |
| 10 | Empathic pain | 0.1964 | 0.3671 | 0.535 |

### CLIP Bottom 5

| 감정 | pred R² | all R² | eff |
|------|---------|--------|-----|
| Triumph | 0.0436 | 0.0767 | 0.569 |
| Fear | 0.0385 | 0.0123 | — |
| Confusion | 0.0291 | 0.0934 | 0.311 |
| Joy | 0.0289 | 0.0094 | — |
| Admiration | 0.0266 | 0.0695 | 0.383 |

---

## A/V/D 상세

| | V-JEPA2 pred | V-JEPA2 all | V-JEPA2 eff | CLIP pred | CLIP all | CLIP eff |
|---|---|---|---|---|---|---|
| Arousal | 0.0651 | 0.0889 | 0.732 | 0.0621 | 0.1355 | 0.459 |
| Valence | 0.0112 | 0.1817 | 0.062 | **0.2706** | 0.4787 | 0.565 |
| Dominance | 0.0000 | 0.0004 | — | 0.0565 | 0.0639 | 0.884 |
| **mean** | **0.0254** | 0.0903 | 0.397* | **0.1297** | 0.2260 | 0.636 |

\* V-JEPA2 dimension efficiency mean은 `all R² >= 0.05` 기준으로 `Arousal`, `Valence`만 포함.

---

## 결론

### 시나리오 판정

**V-JEPA2: 시나리오 A** — cat/dim ratio = **2.16**  
→ brain-pred subspace (3 PCs)가 A/V/D보다 감정 카테고리를 2배 이상 잘 설명  
→ Valence(0.011), Dominance(0.000)는 거의 설명 못 함  
→ "Brain selectively reads category-level affective structure, not just valence/arousal"

**CLIP: 시나리오 B** — cat/dim ratio = **1.28**  
→ 감정 카테고리와 A/V/D 설명력이 비슷  
→ Valence는 0.2706으로 높음 (cat 평균 0.166과 유사한 수준)  
→ "Brain-predictable subspace captures both affective categories and dimensional structure"

### 두 모델 공통

- brain-pred subspace로 가장 잘 설명되는 감정: **Uncomfortable, Aesthetic appreciation, Amusement, Excitement**
- 가장 안 되는 감정: **Confusion, Fear, Joy** (R²≈0)
- Craving, Adoration, Surprise는 unpred subspace R²가 pred보다 오히려 높음 → brain이 안 읽는 차원에 해당 감정 정보가 있음

### Horikawa (2020)과의 비교

- Horikawa (2020): fMRI에서 감정 카테고리 > A/V/D 설명력
- 본 결과 (V-JEPA2): brain-pred subspace에서 cat/dim ratio = 2.16 → **동일 패턴 재확인**
- CLIP에서는 ratio = 1.28로 약함 → V-JEPA2 brain-pred subspace가 Horikawa의 finding과 더 일치

---

## 저장 파일

```
results/brain_pred_subspace_prediction.npz
  target_names          (37,)  — 34 emotions + A/V/D
  emotion_labels        (34,)
  dim_labels            (3,)
  r2_pred_vjepa         (37,)  — brain-pred subspace → target R²
  r2_unpred_vjepa       (37,)
  r2_all_vjepa          (37,)
  pred_idx_vjepa        (3,)   = [0,1,2]
  r2_pred_clip          (37,)
  r2_unpred_clip        (37,)
  r2_all_clip           (37,)
  pred_idx_clip         (6,)   = [0,1,2,4,5,6]

figures/
  brain_pred_subspace_r2_all.png   — Figure A: 37 targets bar
  brain_pred_subspace_scatter.png  — Figure B: pred vs all scatter
  brain_pred_efficiency.png        — Figure C: efficiency bar
```
