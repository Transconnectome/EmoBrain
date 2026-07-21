# Results: Experiment 16 (14-Dimension Version)

Date: 0402  
Source file: `results/exp16_incremental_baseline_results_14d.npz`  
Metadata: `/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_14dims.csv`  
Figures:
- `figures/exp16_incremental_benchmark_14d.png`
- `figures/exp16_incremental_scatter_14d.png`

## Goal

This is the 14-dimension re-run of Exp 16.

Question:

> Beyond explicit vision and semantic features, do brain-predictable model PCs still add predictive value for 34 emotion categories and 14 affective dimensions?

Compared models:

1. `Vision + Semantic`
2. `V-JEPA2 brain-predictable PCs only`
3. `CLIP brain-predictable PCs only`
4. `Vision + Semantic + V-JEPA2 PCs`
5. `Vision + Semantic + CLIP PCs`

## Brain-Predictable PC Sets

- V-JEPA2: `PC1, PC2, PC3`
- CLIP: `PC1, PC2, PC3, PC5, PC6, PC7`

## Main Takeaways

### Baseline summary

| Model | Mean category `R²` | Mean 14-dim `R²` | Category/dimension ratio |
|---|---:|---:|---:|
| Vision + Semantic baseline | 0.0796 | 0.0943 | 0.844 |
| V-JEPA2 PCs only | 0.0550 | 0.0306 | 1.794 |
| CLIP PCs only | 0.1659 | 0.1802 | 0.921 |
| Baseline + V-JEPA2 PCs | 0.0818 | 0.0958 | 0.853 |
| Baseline + CLIP PCs | 0.0861 | 0.1082 | 0.796 |

### Incremental gain over baseline

| Added feature set | Mean category delta `R²` | Mean 14-dim delta `R²` |
|---|---:|---:|
| V-JEPA2 PCs | +0.0022 | +0.0015 |
| CLIP PCs | +0.0065 | +0.0139 |

So in the 14D setting:

- V-JEPA2 adds a small positive increment
- CLIP adds a clearer increment
- the CLIP increment is especially strong for the 14 affective dimensions

This is stronger than the 3D version in one important sense:

- once the target space includes 14 dimensions, CLIP’s extra value beyond vision+semantic is even more clearly dimension-heavy.

## Top Incremental Emotion Gains

### Baseline + V-JEPA2 PCs vs Baseline

| Rank | Emotion | Baseline `R²` | Combined `R²` | Delta |
|---:|---|---:|---:|---:|
| 1 | Aesthetic appreciation | 0.3549 | 0.3936 | +0.0387 |
| 2 | Excitement | 0.0907 | 0.1049 | +0.0141 |
| 3 | Adoration | 0.1427 | 0.1546 | +0.0118 |
| 4 | Amusement | 0.0114 | 0.0178 | +0.0063 |
| 5 | Interest | 0.0632 | 0.0691 | +0.0059 |
| 6 | Craving | 0.3873 | 0.3911 | +0.0038 |
| 7 | Uncomfortable | 0.6769 | 0.6773 | +0.0004 |

### Baseline + CLIP PCs vs Baseline

| Rank | Emotion | Baseline `R²` | Combined `R²` | Delta |
|---:|---|---:|---:|---:|
| 1 | Aesthetic appreciation | 0.3549 | 0.4115 | +0.0567 |
| 2 | Amusement | 0.0114 | 0.0654 | +0.0540 |
| 3 | Excitement | 0.0907 | 0.1165 | +0.0258 |
| 4 | Interest | 0.0632 | 0.0850 | +0.0218 |
| 5 | Surprise | 0.4791 | 0.4976 | +0.0185 |
| 6 | Empathic pain | 0.2008 | 0.2176 | +0.0168 |
| 7 | Sadness | 0.0000 | 0.0166 | +0.0166 |
| 8 | Adoration | 0.1427 | 0.1518 | +0.0090 |
| 9 | Uncomfortable | 0.6769 | 0.6796 | +0.0027 |
| 10 | Craving | 0.3873 | 0.3881 | +0.0008 |

## Top Incremental Dimension Gains

### Baseline + V-JEPA2 PCs vs Baseline

| Rank | Dimension | Baseline `R²` | Combined `R²` | Delta |
|---:|---|---:|---:|---:|
| 1 | Effort | 0.0072 | 0.0222 | +0.0150 |
| 2 | Safety | 0.3051 | 0.3101 | +0.0049 |
| 3 | Control | 0.2420 | 0.2463 | +0.0043 |
| 4 | Approach | 0.2463 | 0.2480 | +0.0017 |
| 5 | Valence | 0.2974 | 0.2979 | +0.0004 |

### Baseline + CLIP PCs vs Baseline

| Rank | Dimension | Baseline `R²` | Combined `R²` | Delta |
|---:|---|---:|---:|---:|
| 1 | Control | 0.2420 | 0.2894 | +0.0474 |
| 2 | Safety | 0.3051 | 0.3387 | +0.0336 |
| 3 | Fairness | 0.0896 | 0.1211 | +0.0315 |
| 4 | Valence | 0.2974 | 0.3212 | +0.0238 |
| 5 | Effort | 0.0072 | 0.0297 | +0.0225 |
| 6 | Approach | 0.2463 | 0.2671 | +0.0208 |
| 7 | Upswing | 0.1329 | 0.1478 | +0.0148 |

## Full Target-Wise Results

Columns:
- `Baseline`: vision + semantic
- `VJ only`: V-JEPA2 PCs only
- `CLIP only`: CLIP PCs only
- `Base+VJ`: baseline + V-JEPA2 PCs
- `Base+CLIP`: baseline + CLIP PCs
- `Delta VJ`: `Base+VJ - Baseline`
- `Delta CLIP`: `Base+CLIP - Baseline`

| Target | Baseline | VJ only | CLIP only | Base+VJ | Base+CLIP | Delta VJ | Delta CLIP |
|---|---:|---:|---:|---:|---:|---:|---:|
| Admiration | 0.000000 | 0.023496 | 0.026622 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Adoration | 0.142744 | 0.080494 | 0.142386 | 0.154573 | 0.151755 | 0.011830 | 0.009012 |
| Aesthetic appreciation | 0.354885 | 0.323135 | 0.447327 | 0.393607 | 0.411549 | 0.038721 | 0.056664 |
| Amusement | 0.011439 | 0.115904 | 0.339656 | 0.017770 | 0.065420 | 0.006331 | 0.053981 |
| Anger | 0.000000 | 0.011802 | 0.181774 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Anxiety | 0.000000 | 0.061135 | 0.203644 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Awe | 0.000000 | 0.022231 | 0.209649 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Awkwardness | 0.000000 | 0.030796 | 0.091264 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Boredom | 0.000000 | 0.019606 | 0.101085 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Calmness | 0.000000 | 0.136112 | 0.165505 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Confusion | 0.000000 | 0.000000 | 0.029090 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Contempt | 0.000000 | 0.000000 | 0.049327 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Craving | 0.387342 | 0.016605 | 0.148219 | 0.391113 | 0.388101 | 0.003771 | 0.000758 |
| Disgust | 0.000000 | 0.008802 | 0.084713 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Empathic pain | 0.200788 | 0.074097 | 0.196400 | 0.199967 | 0.217560 | -0.000821 | 0.016772 |
| Entrancement | 0.000000 | 0.002384 | 0.056352 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Excitement | 0.090722 | 0.200124 | 0.286630 | 0.104858 | 0.116521 | 0.014136 | 0.025799 |
| Fear | 0.000000 | 0.000000 | 0.038490 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Horror | 0.000000 | 0.057006 | 0.170896 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Interest | 0.063203 | 0.059754 | 0.253596 | 0.069071 | 0.084996 | 0.005867 | 0.021793 |
| Joy | 0.000000 | 0.002780 | 0.028893 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Nostalgia | 0.298390 | 0.016698 | 0.210044 | 0.295096 | 0.297647 | -0.003294 | -0.000743 |
| Relief | 0.000000 | 0.057564 | 0.181839 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Romance | 0.000000 | 0.079292 | 0.123616 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Sadness | 0.000000 | 0.009389 | 0.192205 | 0.000000 | 0.016567 | 0.000000 | 0.016567 |
| Satisfaction | 0.000000 | 0.007147 | 0.054351 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Sexual desire | 0.000000 | 0.031337 | 0.105767 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Surprise | 0.479121 | 0.044951 | 0.330832 | 0.477605 | 0.497592 | -0.001515 | 0.018471 |
| Sympathy | 0.000000 | 0.005896 | 0.195932 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Triumph | 0.000000 | 0.012807 | 0.043598 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Uncomfortable | 0.676904 | 0.171491 | 0.537881 | 0.677337 | 0.679602 | 0.000433 | 0.002698 |
| Annoyance | 0.000000 | 0.105711 | 0.188162 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Envy | 0.000000 | 0.029347 | 0.102990 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Guilt | 0.000000 | 0.051776 | 0.121121 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Approach | 0.246288 | 0.026594 | 0.247301 | 0.247966 | 0.267053 | 0.001678 | 0.020765 |
| Arousal | 0.000000 | 0.065094 | 0.062126 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Attention | 0.000000 | 0.048041 | 0.057471 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Certainty | 0.000000 | 0.025622 | 0.174822 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Commitment | 0.000000 | 0.065314 | 0.107109 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Control | 0.242039 | 0.044288 | 0.315647 | 0.246316 | 0.289434 | 0.004277 | 0.047395 |
| Dominance | 0.000000 | 0.000000 | 0.056473 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Effort | 0.007207 | 0.024002 | 0.188186 | 0.022173 | 0.029713 | 0.014966 | 0.022505 |
| Fairness | 0.089581 | 0.007004 | 0.277119 | 0.089007 | 0.121128 | -0.000574 | 0.031547 |
| Identity | 0.000000 | 0.028679 | 0.116022 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Obstruction | 0.000000 | 0.014739 | 0.144117 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Safety | 0.305142 | 0.068490 | 0.325869 | 0.310077 | 0.338706 | 0.004935 | 0.033564 |
| Upswing | 0.132941 | 0.000000 | 0.179295 | 0.128370 | 0.147752 | -0.004571 | 0.014811 |
| Valence | 0.297432 | 0.011222 | 0.270625 | 0.297853 | 0.321184 | 0.000421 | 0.023752 |

## Interpretation

The 14D benchmark makes the supplementary point stronger.

1. Brain-predictable PCs are not redundant with explicit vision+semantic features.
2. CLIP adds more information than V-JEPA2 beyond that baseline.
3. The biggest CLIP gains are not only in emotion categories, but also in broader affective dimensions:
   `Control`, `Safety`, `Fairness`, `Valence`, `Effort`, `Approach`, `Upswing`.

So the cleanest claim is:

- explicit vision+semantic features explain a large part of the target space,
- but brain-predictable model PCs, especially CLIP PCs, still contribute additional non-redundant affective information,
- and that additional information is especially visible in the 14-dimensional affective description space.
