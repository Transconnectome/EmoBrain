# Experiment 13: Vision/Semantic Confound Control

**Date**: 2026-04-02  
**Script**: `exp13_vision_semantic.py`  
**Result file**: `results/vision_semantic_partial_results.npz`  
**Figures**:
- `figures/partial_rsa_vision_semantic.png`
- `figures/partial_r2_vision_semantic.png`

---

## What Was Computed

### Experiment A: Partial RSA
- Confound RSMs:
  - vision-feature cosine RSM from `vision_features.csv`
  - semantic-feature cosine RSM from `semantic_features.csv`
- For each neural/model RSM pair:
  - `original RSA = Spearman(rsm_a, rsm_b)`
  - `partial RSA = Spearman(resid_a, resid_b)`
  - where `resid_a`, `resid_b` are residuals after linear regression on the 2 confound RSM vectors

### Experiment B: Partial R² of brain-predictable subspace
- Brain-predictable PCs:
  - **V-JEPA2**: PC1, PC2, PC3
  - **CLIP**: PC1, PC2, PC3, PC5, PC6, PC7
- Targets:
  - 34 emotion categories
  - Arousal, Valence, Dominance
- For each CV fold:
  - regress out `vision + semantic` confounds from training PCs and targets
  - apply the train-fit confound model to test fold
  - train Ridge on residualized train data
  - evaluate R² on residualized test data
- Stored outputs:
  - `r2_original_*`: exact same `pred` baseline values as Exp 12
  - `r2_partial_*`: confound-controlled residual prediction

### Note
- `r2_original_vjepa` is exactly identical to `results/brain_pred_subspace_prediction.npz:r2_pred_vjepa`
- `r2_original_clip` is exactly identical to `results/brain_pred_subspace_prediction.npz:r2_pred_clip`
- `Retained = Partial / Original`
- When `Original R² = 0`, retained fraction is not interpretable; table shows `0.000000`

---

## Partial RSA

| Source | Model | Original RSA | Partial RSA | Delta | p-value |
|---|---:|---:|---:|---:|---:|
| Brain-JEPA | V-JEPA2 | -0.007063 | -0.004500 | +0.002562 | 2.812e-12 |
| Brain-JEPA | CLIP | -0.069710 | -0.068558 | +0.001153 | 0.000e+00 |
| Raw fMRI | V-JEPA2 | 0.095617 | 0.077626 | -0.017992 | 0.000e+00 |
| Raw fMRI | CLIP | 0.088632 | 0.071745 | -0.016888 | 0.000e+00 |

### Direct Numeric Summary
- Brain-JEPA vs V-JEPA2: `-0.007063 -> -0.004500`
- Brain-JEPA vs CLIP: `-0.069710 -> -0.068558`
- Raw fMRI vs V-JEPA2: `0.095617 -> 0.077626`
- Raw fMRI vs CLIP: `0.088632 -> 0.071745`

---

## V-JEPA2

- Brain-predictable PCs: `[1, 2, 3]`
- Mean R² emotions: `original=0.054990`, `partial=0.005117`, `retained=0.093044`
- Mean R² A/V/D: `original=0.025439`, `partial=0.002932`, `retained=0.115245`
- cat/dim ratio:
  - original: `2.161681`
  - partial: `1.745254`

| Target | Original R² | Partial R² | Delta | Retained |
|---|---:|---:|---:|---:|
| Admiration | 0.023496 | 0.000000 | -0.023496 | 0.000000 |
| Adoration | 0.080494 | 0.007245 | -0.073249 | 0.090007 |
| Aesthetic appreciation | 0.323135 | 0.051488 | -0.271648 | 0.159338 |
| Amusement | 0.115904 | 0.004238 | -0.111666 | 0.036562 |
| Anger | 0.011802 | 0.000000 | -0.011802 | 0.000000 |
| Anxiety | 0.061135 | 0.000395 | -0.060740 | 0.006460 |
| Awe | 0.022231 | 0.000000 | -0.022231 | 0.000000 |
| Awkwardness | 0.030796 | 0.000000 | -0.030796 | 0.000000 |
| Boredom | 0.019606 | 0.000000 | -0.019606 | 0.000000 |
| Calmness | 0.136112 | 0.061010 | -0.075102 | 0.448232 |
| Confusion | 0.000000 | 0.000000 | +0.000000 | 0.000000 |
| Contempt | 0.000000 | 0.000000 | +0.000000 | 0.000000 |
| Craving | 0.016605 | 0.005333 | -0.011272 | 0.321142 |
| Disgust | 0.008802 | 0.000000 | -0.008802 | 0.000000 |
| Empathic pain | 0.074097 | 0.000000 | -0.074097 | 0.000000 |
| Entrancement | 0.002384 | 0.000000 | -0.002384 | 0.000000 |
| Excitement | 0.200124 | 0.009684 | -0.190441 | 0.048389 |
| Fear | 0.000000 | 0.000000 | +0.000000 | 0.000000 |
| Horror | 0.057006 | 0.006776 | -0.050231 | 0.118858 |
| Interest | 0.059754 | 0.001976 | -0.057778 | 0.033071 |
| Joy | 0.002780 | 0.000000 | -0.002780 | 0.000000 |
| Nostalgia | 0.016698 | 0.000000 | -0.016698 | 0.000000 |
| Relief | 0.057564 | 0.000000 | -0.057564 | 0.000000 |
| Romance | 0.079292 | 0.000000 | -0.079292 | 0.000000 |
| Sadness | 0.009389 | 0.002711 | -0.006678 | 0.288786 |
| Satisfaction | 0.007147 | 0.002982 | -0.004164 | 0.417309 |
| Sexual desire | 0.031337 | 0.000000 | -0.031337 | 0.000000 |
| Surprise | 0.044951 | 0.000000 | -0.044951 | 0.000000 |
| Sympathy | 0.005896 | 0.001858 | -0.004038 | 0.315090 |
| Triumph | 0.012807 | 0.005493 | -0.007314 | 0.428933 |
| Uncomfortable | 0.171491 | 0.002799 | -0.168692 | 0.016322 |
| Annoyance | 0.105711 | 0.007731 | -0.097980 | 0.073130 |
| Envy | 0.029347 | 0.002244 | -0.027103 | 0.076455 |
| Guilt | 0.051776 | 0.000000 | -0.051776 | 0.000000 |
| Arousal | 0.065094 | 0.008795 | -0.056299 | 0.135113 |
| Valence | 0.011222 | 0.000000 | -0.011222 | 0.000000 |
| Dominance | 0.000000 | 0.000000 | +0.000000 | 0.000000 |

### Top 10 Emotions By Partial R²

| Rank | Emotion | Original R² | Partial R² | Delta | Retained |
|---:|---|---:|---:|---:|---:|
| 1 | Calmness | 0.136112 | 0.061010 | -0.075102 | 0.448232 |
| 2 | Aesthetic appreciation | 0.323135 | 0.051488 | -0.271648 | 0.159338 |
| 3 | Excitement | 0.200124 | 0.009684 | -0.190441 | 0.048389 |
| 4 | Annoyance | 0.105711 | 0.007731 | -0.097980 | 0.073130 |
| 5 | Adoration | 0.080494 | 0.007245 | -0.073249 | 0.090007 |
| 6 | Horror | 0.057006 | 0.006776 | -0.050231 | 0.118858 |
| 7 | Triumph | 0.012807 | 0.005493 | -0.007314 | 0.428933 |
| 8 | Craving | 0.016605 | 0.005333 | -0.011272 | 0.321142 |
| 9 | Amusement | 0.115904 | 0.004238 | -0.111666 | 0.036562 |
| 10 | Satisfaction | 0.007147 | 0.002982 | -0.004164 | 0.417309 |

### A/V/D
- Arousal: `0.065094 -> 0.008795`
- Valence: `0.011222 -> 0.000000`
- Dominance: `0.000000 -> 0.000000`

---

## CLIP

- Brain-predictable PCs: `[1, 2, 3, 5, 6, 7]`
- Mean R² emotions: `original=0.165878`, `partial=0.013403`, `retained=0.080801`
- Mean R² A/V/D: `original=0.129741`, `partial=0.008595`, `retained=0.066250`
- cat/dim ratio:
  - original: `1.278530`
  - partial: `1.559354`

| Target | Original R² | Partial R² | Delta | Retained |
|---|---:|---:|---:|---:|
| Admiration | 0.026622 | 0.000000 | -0.026622 | 0.000000 |
| Adoration | 0.142386 | 0.000000 | -0.142386 | 0.000000 |
| Aesthetic appreciation | 0.447327 | 0.093505 | -0.353822 | 0.209031 |
| Amusement | 0.339656 | 0.049430 | -0.290227 | 0.145528 |
| Anger | 0.181774 | 0.014517 | -0.167257 | 0.079863 |
| Anxiety | 0.203644 | 0.014503 | -0.189142 | 0.071215 |
| Awe | 0.209649 | 0.000000 | -0.209649 | 0.000000 |
| Awkwardness | 0.091264 | 0.000000 | -0.091264 | 0.000000 |
| Boredom | 0.101085 | 0.000000 | -0.101085 | 0.000000 |
| Calmness | 0.165505 | 0.056444 | -0.109060 | 0.341043 |
| Confusion | 0.029090 | 0.000000 | -0.029090 | 0.000000 |
| Contempt | 0.049327 | 0.000000 | -0.049327 | 0.000000 |
| Craving | 0.148219 | 0.000000 | -0.148219 | 0.000000 |
| Disgust | 0.084713 | 0.000000 | -0.084713 | 0.000000 |
| Empathic pain | 0.196400 | 0.003818 | -0.192582 | 0.019441 |
| Entrancement | 0.056352 | 0.002025 | -0.054327 | 0.035938 |
| Excitement | 0.286630 | 0.025940 | -0.260690 | 0.090499 |
| Fear | 0.038490 | 0.005329 | -0.033161 | 0.138454 |
| Horror | 0.170896 | 0.032251 | -0.138645 | 0.188717 |
| Interest | 0.253596 | 0.023548 | -0.230048 | 0.092856 |
| Joy | 0.028893 | 0.000000 | -0.028893 | 0.000000 |
| Nostalgia | 0.210044 | 0.000000 | -0.210044 | 0.000000 |
| Relief | 0.181839 | 0.019169 | -0.162670 | 0.105418 |
| Romance | 0.123616 | 0.002769 | -0.120848 | 0.022399 |
| Sadness | 0.192205 | 0.016171 | -0.176034 | 0.084135 |
| Satisfaction | 0.054351 | 0.003109 | -0.051242 | 0.057205 |
| Sexual desire | 0.105767 | 0.000000 | -0.105767 | 0.000000 |
| Surprise | 0.330832 | 0.040950 | -0.289882 | 0.123779 |
| Sympathy | 0.195932 | 0.030591 | -0.165341 | 0.156130 |
| Triumph | 0.043598 | 0.000000 | -0.043598 | 0.000000 |
| Uncomfortable | 0.537881 | 0.009488 | -0.528393 | 0.017640 |
| Annoyance | 0.188162 | 0.008700 | -0.179461 | 0.046239 |
| Envy | 0.102990 | 0.003449 | -0.099541 | 0.033487 |
| Guilt | 0.121121 | 0.000000 | -0.121121 | 0.000000 |
| Arousal | 0.062126 | 0.000000 | -0.062126 | 0.000000 |
| Valence | 0.270625 | 0.025786 | -0.244839 | 0.095283 |
| Dominance | 0.056473 | 0.000000 | -0.056473 | 0.000000 |

### Top 10 Emotions By Partial R²

| Rank | Emotion | Original R² | Partial R² | Delta | Retained |
|---:|---|---:|---:|---:|---:|
| 1 | Aesthetic appreciation | 0.447327 | 0.093505 | -0.353822 | 0.209031 |
| 2 | Calmness | 0.165505 | 0.056444 | -0.109060 | 0.341043 |
| 3 | Amusement | 0.339656 | 0.049430 | -0.290227 | 0.145528 |
| 4 | Surprise | 0.330832 | 0.040950 | -0.289882 | 0.123779 |
| 5 | Horror | 0.170896 | 0.032251 | -0.138645 | 0.188717 |
| 6 | Sympathy | 0.195932 | 0.030591 | -0.165341 | 0.156130 |
| 7 | Excitement | 0.286630 | 0.025940 | -0.260690 | 0.090499 |
| 8 | Interest | 0.253596 | 0.023548 | -0.230048 | 0.092856 |
| 9 | Relief | 0.181839 | 0.019169 | -0.162670 | 0.105418 |
| 10 | Sadness | 0.192205 | 0.016171 | -0.176034 | 0.084135 |

### A/V/D
- Arousal: `0.062126 -> 0.000000`
- Valence: `0.270625 -> 0.025786`
- Dominance: `0.056473 -> 0.000000`

---

## Minimal Takeaways From The Saved Numbers

- `Partial RSA`:
  - Brain-JEPA pairings changed only slightly and stayed negative.
  - Raw fMRI pairings stayed positive but were reduced after confound control.
- `Partial R²`:
  - For both V-JEPA2 and CLIP, mean predictive R² dropped sharply after controlling vision/semantic confounds.
  - V-JEPA2 retained about `9.3%` of original mean category R² and `11.5%` of original mean A/V/D R².
  - CLIP retained about `8.1%` of original mean category R² and `6.6%` of original mean A/V/D R².
- Largest surviving partial values:
  - V-JEPA2: `Calmness = 0.061010`, `Aesthetic appreciation = 0.051488`
  - CLIP: `Aesthetic appreciation = 0.093505`, `Calmness = 0.056444`

