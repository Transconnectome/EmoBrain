# Results: Experiment 12 (14-Dimension Version)

Date: 0402  
Source file: `results/brain_pred_subspace_prediction_14d.npz`  
Metadata: `/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_14dims.csv`  
Figures:
- `figures/brain_pred_subspace_r2_all_14d.png`
- `figures/brain_pred_subspace_scatter_14d.png`
- `figures/brain_pred_efficiency_14d.png`

## Goal

This is the 14-dimension re-run of Exp 12.

Question:

> Does the brain-predictable subspace explain primarily 34 emotion categories, or does it align just as strongly with a broader 14-dimensional affective description?

Targets:
- 34 emotion category scores
- 14 affective dimensions  
  `Approach, Arousal, Attention, Certainty, Commitment, Control, Dominance, Effort, Fairness, Identity, Obstruction, Safety, Upswing, Valence`

## Brain-Predictable PC Sets

- V-JEPA2: `PC1, PC2, PC3` (`n = 3`)
- CLIP: `PC1, PC2, PC3, PC5, PC6, PC7` (`n = 6`)

## Main Takeaways

### V-JEPA2

- Pred subspace mean category `R² = 0.0550`
- Pred subspace mean 14-dim `R² = 0.0306`
- Category/dimension ratio `= 1.794`

This means V-JEPA2 still looks category-skewed even after expanding from 3 A/V/D dimensions to 14 dimensions.

### CLIP

- Pred subspace mean category `R² = 0.1659`
- Pred subspace mean 14-dim `R² = 0.1802`
- Category/dimension ratio `= 0.921`

So CLIP no longer looks category-dominant in the 14D setting. Its brain-predictable subspace explains broad affective dimensions at least as well as emotion categories, and slightly better on average.

## Summary Table

| Model | Subspace | Mean category `R²` | Mean 14-dim `R²` | Category/dimension ratio |
|---|---|---:|---:|---:|
| V-JEPA2 | Brain-predictable PCs | 0.0550 | 0.0306 | 1.794 |
| V-JEPA2 | Unpredictable PCs | 0.1027 | 0.0912 | 1.126 |
| V-JEPA2 | All 100 PCs | 0.1703 | 0.1304 | 1.305 |
| CLIP | Brain-predictable PCs | 0.1659 | 0.1802 | 0.921 |
| CLIP | Unpredictable PCs | 0.1017 | 0.1095 | 0.929 |
| CLIP | All 100 PCs | 0.2904 | 0.3095 | 0.938 |

## Top Signals in Brain-Predictable Subspace

### V-JEPA2: top emotion categories

| Rank | Emotion | Pred subspace `R²` | All-100-PC `R²` |
|---:|---|---:|---:|
| 1 | Aesthetic appreciation | 0.3231 | 0.5509 |
| 2 | Excitement | 0.2001 | 0.3955 |
| 3 | Uncomfortable | 0.1715 | 0.4990 |
| 4 | Calmness | 0.1361 | 0.3176 |
| 5 | Amusement | 0.1159 | 0.3219 |
| 6 | Annoyance | 0.1057 | 0.1828 |
| 7 | Adoration | 0.0805 | 0.3597 |
| 8 | Romance | 0.0793 | 0.2235 |
| 9 | Empathic pain | 0.0741 | 0.1823 |
| 10 | Anxiety | 0.0611 | 0.2394 |

### V-JEPA2: top affective dimensions

| Rank | Dimension | Pred subspace `R²` | All-100-PC `R²` |
|---:|---|---:|---:|
| 1 | Safety | 0.0685 | 0.2813 |
| 2 | Commitment | 0.0653 | 0.1974 |
| 3 | Arousal | 0.0651 | 0.0889 |
| 4 | Attention | 0.0480 | 0.0452 |
| 5 | Control | 0.0443 | 0.2261 |
| 6 | Identity | 0.0287 | 0.0970 |
| 7 | Approach | 0.0266 | 0.1860 |
| 8 | Certainty | 0.0256 | 0.1207 |
| 9 | Effort | 0.0240 | 0.1213 |
| 10 | Obstruction | 0.0147 | 0.0559 |

### CLIP: top emotion categories

| Rank | Emotion | Pred subspace `R²` | All-100-PC `R²` |
|---:|---|---:|---:|
| 1 | Uncomfortable | 0.5379 | 0.7275 |
| 2 | Aesthetic appreciation | 0.4473 | 0.6505 |
| 3 | Amusement | 0.3397 | 0.4711 |
| 4 | Surprise | 0.3308 | 0.6074 |
| 5 | Excitement | 0.2866 | 0.4663 |
| 6 | Interest | 0.2536 | 0.4300 |
| 7 | Nostalgia | 0.2100 | 0.2999 |
| 8 | Awe | 0.2096 | 0.3850 |
| 9 | Anxiety | 0.2036 | 0.3920 |
| 10 | Empathic pain | 0.1964 | 0.3671 |

### CLIP: top affective dimensions

| Rank | Dimension | Pred subspace `R²` | All-100-PC `R²` |
|---:|---|---:|---:|
| 1 | Safety | 0.3259 | 0.5245 |
| 2 | Control | 0.3156 | 0.4389 |
| 3 | Fairness | 0.2771 | 0.3701 |
| 4 | Valence | 0.2706 | 0.4787 |
| 5 | Approach | 0.2473 | 0.4739 |
| 6 | Effort | 0.1882 | 0.3476 |
| 7 | Upswing | 0.1793 | 0.2813 |
| 8 | Certainty | 0.1748 | 0.2971 |
| 9 | Obstruction | 0.1441 | 0.2087 |
| 10 | Identity | 0.1160 | 0.2596 |

## Full Target-Wise Results

Columns:
- `VJ pred`: V-JEPA2 brain-predictable subspace
- `VJ unpred`: V-JEPA2 unpredictable subspace
- `VJ all`: all 100 V-JEPA2 PCs
- `CLIP pred`: CLIP brain-predictable subspace
- `CLIP unpred`: CLIP unpredictable subspace
- `CLIP all`: all 100 CLIP PCs

| Target | VJ pred | VJ unpred | VJ all | CLIP pred | CLIP unpred | CLIP all |
|---|---:|---:|---:|---:|---:|---:|
| Admiration | 0.023496 | 0.000000 | 0.002701 | 0.026622 | 0.030848 | 0.069546 |
| Adoration | 0.080494 | 0.267673 | 0.359657 | 0.142386 | 0.393330 | 0.546158 |
| Aesthetic appreciation | 0.323135 | 0.168748 | 0.550928 | 0.447327 | 0.146814 | 0.650459 |
| Amusement | 0.115904 | 0.180494 | 0.321917 | 0.339656 | 0.091285 | 0.471085 |
| Anger | 0.011802 | 0.051209 | 0.067057 | 0.181774 | 0.032473 | 0.232063 |
| Anxiety | 0.061135 | 0.165983 | 0.239447 | 0.203644 | 0.160941 | 0.391989 |
| Awe | 0.022231 | 0.221851 | 0.253794 | 0.209649 | 0.149256 | 0.384971 |
| Awkwardness | 0.030796 | 0.048706 | 0.083853 | 0.091264 | 0.024170 | 0.128058 |
| Boredom | 0.019606 | 0.083231 | 0.122826 | 0.101085 | 0.051224 | 0.173849 |
| Calmness | 0.136112 | 0.128374 | 0.317568 | 0.165505 | 0.144205 | 0.361124 |
| Confusion | 0.000000 | 0.007203 | 0.009453 | 0.029090 | 0.054512 | 0.093441 |
| Contempt | 0.000000 | 0.020372 | 0.020796 | 0.049327 | 0.000000 | 0.059550 |
| Craving | 0.016605 | 0.338593 | 0.364263 | 0.148219 | 0.440930 | 0.639435 |
| Disgust | 0.008802 | 0.000000 | 0.000000 | 0.084713 | 0.000000 | 0.054150 |
| Empathic pain | 0.074097 | 0.095258 | 0.182275 | 0.196400 | 0.148318 | 0.367122 |
| Entrancement | 0.002384 | 0.000000 | 0.006593 | 0.056352 | 0.011152 | 0.077427 |
| Excitement | 0.200124 | 0.152736 | 0.395510 | 0.286630 | 0.136445 | 0.466280 |
| Fear | 0.000000 | 0.000000 | 0.000000 | 0.038490 | 0.000000 | 0.012323 |
| Horror | 0.057006 | 0.062925 | 0.144722 | 0.170896 | 0.008505 | 0.208261 |
| Interest | 0.059754 | 0.196321 | 0.266689 | 0.253596 | 0.152531 | 0.429975 |
| Joy | 0.002780 | 0.000000 | 0.000000 | 0.028893 | 0.000000 | 0.009398 |
| Nostalgia | 0.016698 | 0.131809 | 0.156147 | 0.210044 | 0.069851 | 0.299905 |
| Relief | 0.057564 | 0.072027 | 0.155151 | 0.181839 | 0.035602 | 0.261588 |
| Romance | 0.079292 | 0.124061 | 0.223460 | 0.123616 | 0.241802 | 0.387931 |
| Sadness | 0.009389 | 0.183236 | 0.197498 | 0.192205 | 0.280825 | 0.525133 |
| Satisfaction | 0.007147 | 0.000000 | 0.000000 | 0.054351 | 0.040509 | 0.110902 |
| Sexual desire | 0.031337 | 0.085236 | 0.122138 | 0.105767 | 0.009882 | 0.126023 |
| Surprise | 0.044951 | 0.223447 | 0.276275 | 0.330832 | 0.243738 | 0.607380 |
| Sympathy | 0.005896 | 0.032220 | 0.043999 | 0.195932 | 0.063171 | 0.279468 |
| Triumph | 0.012807 | 0.030601 | 0.046547 | 0.043598 | 0.028998 | 0.076664 |
| Uncomfortable | 0.171491 | 0.300459 | 0.498979 | 0.537881 | 0.136667 | 0.727499 |
| Annoyance | 0.105711 | 0.067778 | 0.182832 | 0.188162 | 0.053350 | 0.259957 |
| Envy | 0.029347 | 0.000000 | 0.024083 | 0.102990 | 0.060852 | 0.176399 |
| Guilt | 0.051776 | 0.051820 | 0.151706 | 0.121121 | 0.014822 | 0.207844 |
| Approach | 0.026594 | 0.152280 | 0.186010 | 0.247301 | 0.202591 | 0.473906 |
| Arousal | 0.065094 | 0.003703 | 0.088923 | 0.062126 | 0.058523 | 0.135484 |
| Attention | 0.048041 | 0.000000 | 0.045172 | 0.057471 | 0.014115 | 0.095853 |
| Certainty | 0.025622 | 0.086987 | 0.120680 | 0.174822 | 0.103778 | 0.297093 |
| Commitment | 0.065314 | 0.123364 | 0.197356 | 0.107109 | 0.236252 | 0.356747 |
| Control | 0.044288 | 0.172848 | 0.226056 | 0.315647 | 0.097538 | 0.438890 |
| Dominance | 0.000000 | 0.000000 | 0.000386 | 0.056473 | 0.000000 | 0.063906 |
| Effort | 0.024002 | 0.079487 | 0.121292 | 0.188186 | 0.138301 | 0.347556 |
| Fairness | 0.007004 | 0.115301 | 0.128350 | 0.277119 | 0.069865 | 0.370131 |
| Identity | 0.028679 | 0.062541 | 0.097029 | 0.116022 | 0.123978 | 0.259552 |
| Obstruction | 0.014739 | 0.033648 | 0.055916 | 0.144117 | 0.050128 | 0.208688 |
| Safety | 0.068490 | 0.202844 | 0.281343 | 0.325869 | 0.176070 | 0.524530 |
| Upswing | 0.000000 | 0.087335 | 0.095944 | 0.179295 | 0.081140 | 0.281321 |
| Valence | 0.011222 | 0.156240 | 0.181673 | 0.270625 | 0.180027 | 0.478706 |

## Interpretation

The 14D re-run changes the story in an important way.

1. V-JEPA2 still supports a category-leaning interpretation.
2. CLIP does not. In the 14D analysis, CLIP is at least as dimension-heavy as category-heavy.
3. This means the earlier `category > A/V/D` framing was partly dependent on using only 3 dimensions.
4. With a richer affective ontology, CLIP in particular appears to align strongly with broad affective dimensions such as `Safety`, `Control`, `Fairness`, `Valence`, and `Approach`.

So the 14D result is more nuanced than the 3D result:

- V-JEPA2 remains relatively category-skewed.
- CLIP looks more mixed, and even slightly dimension-dominant.
