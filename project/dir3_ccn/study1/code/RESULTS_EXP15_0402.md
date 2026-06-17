# Results: Experiment 15 (Subject Stability, Resampling, Alpha Sensitivity)

Date: 0402  
Source file: `results/exp15_stability_results.npz`  
Figures:
- `figures/exp15_subject_stability.png`
- `figures/exp15_alpha_sensitivity.png`

## Goal

Experiment 15 was designed to test whether the main findings from Exp 12 and Exp 13 are stable across:

1. individual subjects,
2. stimulus resampling,
3. ridge regularization strength (`alpha`).

The script used was `15_subject_stability_alpha_resampling.py`.

## What Was Computed

### 1. Subject-wise brain-predictable PC stability

- For each subject separately, brain embeddings were used to predict each model PC.
- A PC was marked as "brain-predictable" if cross-validated `R^2 > 0.01`.
- This was done for the first 100 PCs of V-JEPA2 and CLIP.

### 2. Resampling stability

- Using the mean-subject brain-predictable PC mask from Exp 12,
- the Exp 12 target prediction analysis was repeated on 100 random half-splits of stimuli,
- and the summary statistics were recorded:
  - mean category `R^2`
  - mean A/V/D `R^2`
  - category-to-dimension ratio

### 3. Ridge alpha sensitivity

- Exp 12 and Exp 13 were recomputed at:
  - `alpha = 0.1`
  - `alpha = 1.0`
  - `alpha = 10.0`
  - `alpha = 100.0`

## Main Takeaways

### Subject stability

- The brain-predictable PC set was extremely sparse.
- V-JEPA2 mean mask selected 3 PCs: `PC1, PC2, PC3`.
- CLIP mean mask selected 6 PCs: `PC1, PC2, PC3, PC5, PC6, PC7`.
- At the subject level, however, only a smaller core subset survived consistently:
  - V-JEPA2: `PC1` in all 5 subjects, `PC3` in 2/5 subjects
  - CLIP: `PC1` in all 5 subjects, `PC2` in 2/5 subjects
- This means the most stable part of the brain-readable subspace is even smaller than the mean-subject estimate.

### Resampling stability

- The Exp 12 pattern was stable under 100 random half-splits.
- V-JEPA2 remained category-dominant:
  - mean category `R^2 = 0.0506`
  - mean A/V/D `R^2 = 0.0230`
  - category/dimension ratio `= 2.3056`
- CLIP remained more balanced:
  - mean category `R^2 = 0.1569`
  - mean A/V/D `R^2 = 0.1256`
  - category/dimension ratio `= 1.2544`

### Alpha sensitivity

- The overall conclusions were effectively unchanged across `alpha = 0.1` to `100.0`.
- V-JEPA2 remained low-magnitude but category-skewed.
- CLIP remained stronger overall than V-JEPA2 in Exp 12 and Exp 13.
- Exp 13 partial results increased only slightly at larger alpha, but no qualitative reversal occurred.

## 1. Subject-Wise Brain-Predictable PC Stability

### Mean-subject masks

- V-JEPA2 mean mask: `PC1, PC2, PC3`
- CLIP mean mask: `PC1, PC2, PC3, PC5, PC6, PC7`

### Subject-level selected PCs

#### V-JEPA2

| Subject | Selected PCs (`R^2 > 0.01`) | Count |
|---|---:|---:|
| 1 | `1` | 1 |
| 2 | `1, 3` | 2 |
| 3 | `1, 3` | 2 |
| 4 | `1` | 1 |
| 5 | `1` | 1 |

#### CLIP

| Subject | Selected PCs (`R^2 > 0.01`) | Count |
|---|---:|---:|
| 1 | `1` | 1 |
| 2 | `1, 2` | 2 |
| 3 | `1, 2` | 2 |
| 4 | `1` | 1 |
| 5 | `1` | 1 |

### PC selection frequency across subjects

#### V-JEPA2

| PC | Frequency across 5 subjects |
|---:|---:|
| 1 | 1.00 |
| 3 | 0.40 |
| all others | 0.00 |

#### CLIP

| PC | Frequency across 5 subjects |
|---:|---:|
| 1 | 1.00 |
| 2 | 0.40 |
| all others | 0.00 |

### Pairwise Jaccard overlap between subjects

Off-diagonal mean Jaccard overlap:

- V-JEPA2: `0.700`
- CLIP: `0.700`

#### V-JEPA2 Jaccard matrix

| Subject | 1 | 2 | 3 | 4 | 5 |
|---|---:|---:|---:|---:|---:|
| 1 | 1.0 | 0.5 | 0.5 | 1.0 | 1.0 |
| 2 | 0.5 | 1.0 | 1.0 | 0.5 | 0.5 |
| 3 | 0.5 | 1.0 | 1.0 | 0.5 | 0.5 |
| 4 | 1.0 | 0.5 | 0.5 | 1.0 | 1.0 |
| 5 | 1.0 | 0.5 | 0.5 | 1.0 | 1.0 |

#### CLIP Jaccard matrix

| Subject | 1 | 2 | 3 | 4 | 5 |
|---|---:|---:|---:|---:|---:|
| 1 | 1.0 | 0.5 | 0.5 | 1.0 | 1.0 |
| 2 | 0.5 | 1.0 | 1.0 | 0.5 | 0.5 |
| 3 | 0.5 | 1.0 | 1.0 | 0.5 | 0.5 |
| 4 | 1.0 | 0.5 | 0.5 | 1.0 | 1.0 |
| 5 | 1.0 | 0.5 | 0.5 | 1.0 | 1.0 |

## 2. Resampling Stability

100 random half-splits of the stimuli were used.

### Summary distributions

#### V-JEPA2

| Metric | Mean | 2.5% | Median | 97.5% |
|---|---:|---:|---:|---:|
| Mean category `R^2` | 0.0506 | 0.0450 | 0.0506 | 0.0548 |
| Mean A/V/D `R^2` | 0.0230 | 0.0128 | 0.0230 | 0.0320 |
| Category/dimension ratio | 2.3056 | 1.6130 | 2.2065 | 3.7747 |

#### CLIP

| Metric | Mean | 2.5% | Median | 97.5% |
|---|---:|---:|---:|---:|
| Mean category `R^2` | 0.1569 | 0.1461 | 0.1573 | 0.1654 |
| Mean A/V/D `R^2` | 0.1256 | 0.1108 | 0.1259 | 0.1430 |
| Category/dimension ratio | 1.2544 | 1.0903 | 1.2491 | 1.4280 |

### Top-5 emotion stability across resamples

This counts how often each emotion appeared in the top-5 predicted category emotions across 100 half-splits.

#### V-JEPA2

| Emotion | Top-5 count |
|---|---:|
| Excitement | 100 |
| Uncomfortable | 100 |
| Aesthetic appreciation | 100 |
| Calmness | 83 |
| Amusement | 79 |
| Annoyance | 37 |
| Romance | 1 |

All remaining emotions had count `0`.

#### CLIP

| Emotion | Top-5 count |
|---|---:|
| Uncomfortable | 100 |
| Aesthetic appreciation | 100 |
| Amusement | 100 |
| Excitement | 94 |
| Surprise | 93 |
| Interest | 13 |

All remaining emotions had count `0`.

## 3. Ridge Alpha Sensitivity

### Full alpha table

| Alpha | Exp12 cat V-JEPA2 | Exp12 dim V-JEPA2 | Exp12 cat CLIP | Exp12 dim CLIP | Exp13 partial cat V-JEPA2 | Exp13 partial dim V-JEPA2 | Exp13 partial cat CLIP | Exp13 partial dim CLIP |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.1 | 0.0550 | 0.0254 | 0.1659 | 0.1297 | 0.0051 | 0.0029 | 0.0134 | 0.0086 |
| 1.0 | 0.0550 | 0.0254 | 0.1659 | 0.1297 | 0.0051 | 0.0029 | 0.0134 | 0.0086 |
| 10.0 | 0.0550 | 0.0254 | 0.1660 | 0.1298 | 0.0051 | 0.0030 | 0.0135 | 0.0086 |
| 100.0 | 0.0551 | 0.0254 | 0.1661 | 0.1296 | 0.0053 | 0.0031 | 0.0139 | 0.0089 |

### Interpretation

- Exp 12 results are nearly numerically identical across the tested alpha range.
- Exp 13 partial results are also stable, with only a mild upward drift at larger alpha.
- No alpha value changes the qualitative ranking:
  - CLIP > V-JEPA2 in overall predictive magnitude
  - V-JEPA2 remains more category-skewed than CLIP
  - partial Exp 13 performance remains much lower than original Exp 12 performance

## Overall Interpretation

Experiment 15 supports the robustness of the current story rather than changing it.

1. The brain-readable model subspace is genuinely very small.
2. The most stable cross-subject core is even smaller than the mean-subject estimate.
3. The Exp 12 category-vs-dimension pattern is stable under resampling.
4. The Exp 12 and Exp 13 conclusions are not sensitive to reasonable ridge alpha choices.

The strongest supplementary message from Exp 15 is that the key conclusions do not depend on one lucky split, one subject averaging step, or one arbitrary regularization setting.
