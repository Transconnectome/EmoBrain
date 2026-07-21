# Results: Experiment 13 (14-Dimension Version)

Date: 0402  
Source file: `results/vision_semantic_partial_results_14d.npz`  
Metadata: `/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_14dims.csv`  
Figures:
- `figures/partial_rsa_vision_semantic_14d.png`
- `figures/partial_r2_vision_semantic_14d.png`

## Goal

This is the 14-dimension re-run of Exp 13.

Question:

> After regressing out explicit vision and semantic confounds, how much emotion-related and dimension-related signal remains in the brain-predictable model subspace?

This analysis has two parts:

1. Partial RSA at the RSM level
2. Partial `R²` at the target-prediction level

Targets:
- 34 emotion categories
- 14 affective dimensions

## Brain-Predictable PC Sets

- V-JEPA2: `PC1, PC2, PC3`
- CLIP: `PC1, PC2, PC3, PC5, PC6, PC7`

## Main Takeaways

### Partial RSA

The RSA changes are modest but consistently downward.

| Neural source | Model | Original RSA | Partial RSA | Delta | p-value |
|---|---|---:|---:|---:|---:|
| Brain-JEPA | V-JEPA2 | -0.0071 | -0.0045 | +0.0026 | 2.81e-12 |
| Brain-JEPA | CLIP | -0.0697 | -0.0686 | +0.0012 | 0.00e+00 |
| Raw fMRI | V-JEPA2 | 0.0956 | 0.0776 | -0.0180 | 0.00e+00 |
| Raw fMRI | CLIP | 0.0886 | 0.0717 | -0.0169 | 0.00e+00 |

### Partial target prediction

Both models lose most of their predictive signal after controlling vision+semantic confounds.

#### V-JEPA2

- Mean category `R²`: `0.0550 -> 0.0051`
- Retained fraction: `0.093`
- Mean 14-dim `R²`: `0.0306 -> 0.0026`
- Retained fraction: `0.086`

#### CLIP

- Mean category `R²`: `0.1659 -> 0.0134`
- Retained fraction: `0.081`
- Mean 14-dim `R²`: `0.1802 -> 0.0191`
- Retained fraction: `0.106`

This means the 14D analysis reinforces the same general conclusion as the 3D version:

- a substantial amount of affective signal overlaps with explicit vision/semantic structure,
- but the post-control residual is not completely zero.

## Strongest Residual Signals After Confound Control

### V-JEPA2: top partial emotions

| Rank | Emotion | Original `R²` | Partial `R²` | Delta |
|---:|---|---:|---:|---:|
| 1 | Calmness | 0.1361 | 0.0610 | -0.0751 |
| 2 | Aesthetic appreciation | 0.3231 | 0.0515 | -0.2716 |
| 3 | Excitement | 0.2001 | 0.0097 | -0.1904 |
| 4 | Annoyance | 0.1057 | 0.0077 | -0.0980 |
| 5 | Adoration | 0.0805 | 0.0072 | -0.0732 |
| 6 | Horror | 0.0570 | 0.0068 | -0.0502 |
| 7 | Triumph | 0.0128 | 0.0055 | -0.0073 |
| 8 | Craving | 0.0166 | 0.0053 | -0.0113 |
| 9 | Amusement | 0.1159 | 0.0042 | -0.1117 |
| 10 | Satisfaction | 0.0071 | 0.0030 | -0.0042 |

### V-JEPA2: top partial dimensions

| Rank | Dimension | Original `R²` | Partial `R²` | Delta |
|---:|---|---:|---:|---:|
| 1 | Effort | 0.0240 | 0.0120 | -0.0120 |
| 2 | Arousal | 0.0651 | 0.0088 | -0.0563 |
| 3 | Safety | 0.0685 | 0.0076 | -0.0609 |
| 4 | Control | 0.0443 | 0.0072 | -0.0371 |
| 5 | Approach | 0.0266 | 0.0014 | -0.0252 |

### CLIP: top partial emotions

| Rank | Emotion | Original `R²` | Partial `R²` | Delta |
|---:|---|---:|---:|---:|
| 1 | Aesthetic appreciation | 0.4473 | 0.0935 | -0.3538 |
| 2 | Calmness | 0.1655 | 0.0564 | -0.1091 |
| 3 | Amusement | 0.3397 | 0.0494 | -0.2902 |
| 4 | Surprise | 0.3308 | 0.0410 | -0.2899 |
| 5 | Horror | 0.1709 | 0.0323 | -0.1386 |
| 6 | Sympathy | 0.1959 | 0.0306 | -0.1653 |
| 7 | Excitement | 0.2866 | 0.0259 | -0.2607 |
| 8 | Interest | 0.2536 | 0.0235 | -0.2300 |
| 9 | Relief | 0.1818 | 0.0192 | -0.1627 |
| 10 | Sadness | 0.1922 | 0.0162 | -0.1760 |

### CLIP: top partial dimensions

| Rank | Dimension | Original `R²` | Partial `R²` | Delta |
|---:|---|---:|---:|---:|
| 1 | Control | 0.3156 | 0.0680 | -0.2477 |
| 2 | Safety | 0.3259 | 0.0549 | -0.2710 |
| 3 | Fairness | 0.2771 | 0.0371 | -0.2400 |
| 4 | Valence | 0.2706 | 0.0258 | -0.2448 |
| 5 | Obstruction | 0.1441 | 0.0184 | -0.1258 |
| 6 | Approach | 0.2473 | 0.0181 | -0.2292 |
| 7 | Upswing | 0.1793 | 0.0161 | -0.1632 |
| 8 | Certainty | 0.1748 | 0.0148 | -0.1600 |
| 9 | Effort | 0.1882 | 0.0107 | -0.1775 |
| 10 | Attention | 0.0575 | 0.0037 | -0.0538 |

## Full Target-Wise Results

Columns:
- `VJ orig`: V-JEPA2 original `R²`
- `VJ part`: V-JEPA2 partial `R²`
- `VJ delta`: `part - orig`
- `CLIP orig`: CLIP original `R²`
- `CLIP part`: CLIP partial `R²`
- `CLIP delta`: `part - orig`

| Target | VJ orig | VJ part | VJ delta | CLIP orig | CLIP part | CLIP delta |
|---|---:|---:|---:|---:|---:|---:|
| Admiration | 0.023496 | 0.000000 | -0.023496 | 0.026622 | 0.000000 | -0.026622 |
| Adoration | 0.080494 | 0.007245 | -0.073249 | 0.142386 | 0.000000 | -0.142386 |
| Aesthetic appreciation | 0.323135 | 0.051488 | -0.271648 | 0.447327 | 0.093505 | -0.353822 |
| Amusement | 0.115904 | 0.004238 | -0.111666 | 0.339656 | 0.049430 | -0.290227 |
| Anger | 0.011802 | 0.000000 | -0.011802 | 0.181774 | 0.014517 | -0.167257 |
| Anxiety | 0.061135 | 0.000395 | -0.060740 | 0.203644 | 0.014503 | -0.189142 |
| Awe | 0.022231 | 0.000000 | -0.022231 | 0.209649 | 0.000000 | -0.209649 |
| Awkwardness | 0.030796 | 0.000000 | -0.030796 | 0.091264 | 0.000000 | -0.091264 |
| Boredom | 0.019606 | 0.000000 | -0.019606 | 0.101085 | 0.000000 | -0.101085 |
| Calmness | 0.136112 | 0.061010 | -0.075102 | 0.165505 | 0.056444 | -0.109060 |
| Confusion | 0.000000 | 0.000000 | 0.000000 | 0.029090 | 0.000000 | -0.029090 |
| Contempt | 0.000000 | 0.000000 | 0.000000 | 0.049327 | 0.000000 | -0.049327 |
| Craving | 0.016605 | 0.005333 | -0.011272 | 0.148219 | 0.000000 | -0.148219 |
| Disgust | 0.008802 | 0.000000 | -0.008802 | 0.084713 | 0.000000 | -0.084713 |
| Empathic pain | 0.074097 | 0.000000 | -0.074097 | 0.196400 | 0.003818 | -0.192582 |
| Entrancement | 0.002384 | 0.000000 | -0.002384 | 0.056352 | 0.002025 | -0.054327 |
| Excitement | 0.200124 | 0.009684 | -0.190441 | 0.286630 | 0.025940 | -0.260690 |
| Fear | 0.000000 | 0.000000 | 0.000000 | 0.038490 | 0.005329 | -0.033161 |
| Horror | 0.057006 | 0.006776 | -0.050231 | 0.170896 | 0.032251 | -0.138645 |
| Interest | 0.059754 | 0.001976 | -0.057778 | 0.253596 | 0.023548 | -0.230048 |
| Joy | 0.002780 | 0.000000 | -0.002780 | 0.028893 | 0.000000 | -0.028893 |
| Nostalgia | 0.016698 | 0.000000 | -0.016698 | 0.210044 | 0.000000 | -0.210044 |
| Relief | 0.057564 | 0.000000 | -0.057564 | 0.181839 | 0.019169 | -0.162670 |
| Romance | 0.079292 | 0.000000 | -0.079292 | 0.123616 | 0.002769 | -0.120848 |
| Sadness | 0.009389 | 0.002711 | -0.006678 | 0.192205 | 0.016171 | -0.176034 |
| Satisfaction | 0.007147 | 0.002982 | -0.004164 | 0.054351 | 0.003109 | -0.051242 |
| Sexual desire | 0.031337 | 0.000000 | -0.031337 | 0.105767 | 0.000000 | -0.105767 |
| Surprise | 0.044951 | 0.000000 | -0.044951 | 0.330832 | 0.040950 | -0.289882 |
| Sympathy | 0.005896 | 0.001858 | -0.004038 | 0.195932 | 0.030591 | -0.165341 |
| Triumph | 0.012807 | 0.005493 | -0.007314 | 0.043598 | 0.000000 | -0.043598 |
| Uncomfortable | 0.171491 | 0.002799 | -0.168692 | 0.537881 | 0.009488 | -0.528393 |
| Annoyance | 0.105711 | 0.007731 | -0.097980 | 0.188162 | 0.008700 | -0.179461 |
| Envy | 0.029347 | 0.002244 | -0.027103 | 0.102990 | 0.003449 | -0.099541 |
| Guilt | 0.051776 | 0.000000 | -0.051776 | 0.121121 | 0.000000 | -0.121121 |
| Approach | 0.026594 | 0.001365 | -0.025229 | 0.247301 | 0.018138 | -0.229163 |
| Arousal | 0.065094 | 0.008795 | -0.056299 | 0.062126 | 0.000000 | -0.062126 |
| Attention | 0.048041 | 0.000000 | -0.048041 | 0.057471 | 0.003682 | -0.053788 |
| Certainty | 0.025622 | 0.000000 | -0.025622 | 0.174822 | 0.014831 | -0.159991 |
| Commitment | 0.065314 | 0.000038 | -0.065276 | 0.107109 | 0.000000 | -0.107109 |
| Control | 0.044288 | 0.007161 | -0.037127 | 0.315647 | 0.067981 | -0.247666 |
| Dominance | 0.000000 | 0.000000 | 0.000000 | 0.056473 | 0.000000 | -0.056473 |
| Effort | 0.024002 | 0.012020 | -0.011983 | 0.188186 | 0.010707 | -0.177479 |
| Fairness | 0.007004 | 0.000000 | -0.007004 | 0.277119 | 0.037145 | -0.239974 |
| Identity | 0.028679 | 0.000000 | -0.028679 | 0.116022 | 0.000325 | -0.115697 |
| Obstruction | 0.014739 | 0.000000 | -0.014739 | 0.144117 | 0.018361 | -0.125756 |
| Safety | 0.068490 | 0.007597 | -0.060893 | 0.325869 | 0.054869 | -0.271000 |
| Upswing | 0.000000 | 0.000000 | 0.000000 | 0.179295 | 0.016051 | -0.163243 |
| Valence | 0.011222 | 0.000000 | -0.011222 | 0.270625 | 0.025786 | -0.244839 |

## Interpretation

The 14D confound-control result is very clear.

1. Expanding from 3 dimensions to 14 does not rescue the signal after confound control.
2. Most of the predictive variance in both models still overlaps with explicit vision and semantic structure.
3. CLIP retains slightly more 14D variance than V-JEPA2 after control.
4. The residual signals that survive are selective:
   `Calmness`, `Aesthetic appreciation`, `Control`, `Safety`, `Fairness`, `Valence`, and `Effort` remain among the strongest.

So the main claim should still be moderate:

- the readable subspace is affectively meaningful,
- but much of that affective structure is shared with lower-level visual and semantic organization.
