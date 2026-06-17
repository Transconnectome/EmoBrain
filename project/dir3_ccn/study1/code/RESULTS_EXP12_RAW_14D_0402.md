# Results: Experiment 12 (Raw fMRI, 14-Dimension Version)

Date: 0402  
Source file: `results/raw_exp12_14d_results.npz`  
Metadata: `/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_14dims.csv`  
Raw fMRI input: `/pscratch/sd/s/sjmoon/EmoFM/raw_fmri_results/fmri_raw.npy`  
Figures:
- `figures/raw_exp12_14d_k_sweep.png`
- `figures/raw_exp12_14d_targets.png`

## Goal

This is the raw-fMRI analogue of Exp 12 using the 14-dimension target space.

Question:

> When raw fMRI is used directly as the neural representation, does it predict 34 emotion categories better than 14 affective dimensions, or vice versa?

Targets:
- 34 emotion categories
- 14 affective dimensions  
  `Approach, Arousal, Attention, Certainty, Commitment, Control, Dominance, Effort, Fairness, Identity, Obstruction, Safety, Upswing, Valence`

## Main Takeaways

The result is clear: raw fMRI is more dimension-weighted than category-weighted in the 14D setting.

At `k = 27`:
- Mean category `R² = 0.1075`
- Mean 14-dim `R² = 0.1557`
- Category/dimension ratio `= 0.6907`

At full `450D`:
- Mean category `R² = 0.0258`
- Mean 14-dim `R² = 0.0610`
- Category/dimension ratio `= 0.4229`

So:

1. Raw fMRI predicts the 14 affective dimensions better than the 34 categories.
2. This is already true at `k=27`, and becomes even more dimension-heavy at full `450D`.
3. `k=27` performs much better than full `450D` for both categories and dimensions, consistent with a low-dimensional affective geometry and with overfitting/noise hurting the unreduced full feature space.

## k-Sweep Summary

| k | Mean category `R²` | Mean 14-dim `R²` | Category/dimension ratio |
|---:|---:|---:|---:|
| 3 | 0.0330 | 0.0428 | 0.7721 |
| 5 | 0.0523 | 0.0544 | 0.9619 |
| 7 | 0.0683 | 0.0785 | 0.8700 |
| 10 | 0.0865 | 0.1223 | 0.7071 |
| 15 | 0.0921 | 0.1237 | 0.7443 |
| 20 | 0.1018 | 0.1428 | 0.7126 |
| 25 | 0.1061 | 0.1501 | 0.7070 |
| 27 | 0.1075 | 0.1557 | 0.6907 |
| 30 | 0.1088 | 0.1589 | 0.6845 |
| 34 | 0.1102 | 0.1586 | 0.6945 |
| 40 | 0.1112 | 0.1579 | 0.7042 |
| 50 | 0.1140 | 0.1636 | 0.6968 |
| 75 | 0.1166 | 0.1726 | 0.6751 |
| 100 | 0.1154 | 0.1779 | 0.6489 |

## Reference Settings

### k = 27

| Metric | Value |
|---|---:|
| Mean category `R²` | 0.1075 |
| Mean 14-dim `R²` | 0.1557 |
| Category/dimension ratio | 0.6907 |

### Full 450D raw fMRI

| Metric | Value |
|---|---:|
| Mean category `R²` | 0.0258 |
| Mean 14-dim `R²` | 0.0610 |
| Category/dimension ratio | 0.4229 |

## Top Signals at k = 27

### Top 10 emotion categories

| Rank | Emotion | `R² @ k=27` | `R² @ full 450D` |
|---:|---|---:|---:|
| 1 | Uncomfortable | 0.3226 | 0.2919 |
| 2 | Empathic pain | 0.2670 | 0.1205 |
| 3 | Aesthetic appreciation | 0.2335 | 0.1351 |
| 4 | Amusement | 0.2126 | 0.0774 |
| 5 | Excitement | 0.2107 | 0.1107 |
| 6 | Anxiety | 0.1889 | 0.0510 |
| 7 | Interest | 0.1857 | 0.0626 |
| 8 | Annoyance | 0.1789 | 0.0265 |
| 9 | Adoration | 0.1391 | 0.0000 |
| 10 | Awe | 0.1340 | 0.0000 |

### Top 10 affective dimensions

| Rank | Dimension | `R² @ k=27` | `R² @ full 450D` |
|---:|---|---:|---:|
| 1 | Safety | 0.2493 | 0.1677 |
| 2 | Control | 0.2436 | 0.1624 |
| 3 | Valence | 0.2181 | 0.1461 |
| 4 | Approach | 0.2155 | 0.1286 |
| 5 | Effort | 0.1821 | 0.0752 |
| 6 | Upswing | 0.1771 | 0.0949 |
| 7 | Certainty | 0.1735 | 0.0139 |
| 8 | Fairness | 0.1613 | 0.0657 |
| 9 | Commitment | 0.1353 | 0.0000 |
| 10 | Identity | 0.1281 | 0.0000 |

## Full Target-Wise Results

Columns:
- `k27`: raw fMRI PCA `k=27`
- `full450`: raw fMRI full `450D`

| Target | `R² @ k=27` | `R² @ full450` |
|---|---:|---:|
| Admiration | 0.027598 | 0.000000 |
| Adoration | 0.139063 | 0.000000 |
| Aesthetic appreciation | 0.233541 | 0.135140 |
| Amusement | 0.212581 | 0.077383 |
| Anger | 0.047553 | 0.000000 |
| Anxiety | 0.188895 | 0.051021 |
| Awe | 0.133998 | 0.000000 |
| Awkwardness | 0.072846 | 0.000000 |
| Boredom | 0.083553 | 0.000000 |
| Calmness | 0.113117 | 0.000000 |
| Confusion | 0.076096 | 0.000000 |
| Contempt | 0.011505 | 0.000000 |
| Craving | 0.072003 | 0.000000 |
| Disgust | 0.022219 | 0.000000 |
| Empathic pain | 0.266970 | 0.120476 |
| Entrancement | 0.095072 | 0.000000 |
| Excitement | 0.210654 | 0.110743 |
| Fear | 0.000000 | 0.000000 |
| Horror | 0.066202 | 0.000000 |
| Interest | 0.185706 | 0.062572 |
| Joy | 0.000000 | 0.000000 |
| Nostalgia | 0.131919 | 0.002055 |
| Relief | 0.127025 | 0.000000 |
| Romance | 0.128751 | 0.000000 |
| Sadness | 0.116120 | 0.000000 |
| Satisfaction | 0.020331 | 0.000000 |
| Sexual desire | 0.082296 | 0.000000 |
| Surprise | 0.110189 | 0.000000 |
| Sympathy | 0.041795 | 0.000000 |
| Triumph | 0.048094 | 0.000000 |
| Uncomfortable | 0.322580 | 0.291873 |
| Annoyance | 0.178872 | 0.026453 |
| Envy | 0.032068 | 0.000000 |
| Guilt | 0.057138 | 0.000000 |
| Approach | 0.215483 | 0.128636 |
| Arousal | 0.068101 | 0.000000 |
| Attention | 0.074495 | 0.000000 |
| Certainty | 0.173494 | 0.013921 |
| Commitment | 0.135331 | 0.000000 |
| Control | 0.243610 | 0.162397 |
| Dominance | 0.048974 | 0.000000 |
| Effort | 0.182146 | 0.075235 |
| Fairness | 0.161266 | 0.065683 |
| Identity | 0.128079 | 0.000000 |
| Obstruction | 0.104140 | 0.000000 |
| Safety | 0.249320 | 0.167702 |
| Upswing | 0.177055 | 0.094928 |
| Valence | 0.218121 | 0.146069 |

## Interpretation

The raw-fMRI 14D result does not look category-dominant. It looks dimension-dominant.

Compared with the model-subspace analyses, this is an important contrast:

1. Raw fMRI itself predicts broad affective dimensions more strongly than emotion categories.
2. The strongest raw-fMRI dimensions are `Safety`, `Control`, `Valence`, `Approach`, `Effort`, and `Upswing`.
3. So the direct neural signal appears more dimension-heavy than the V-JEPA2 brain-predictable subspace, and also more dimension-heavy than the original 3D framing suggested.

The cleanest summary is:

> In the 14D target space, raw fMRI favors broad affective dimensions over fine-grained emotion categories, and this pattern is already visible at the low-dimensional reference point `k=27`.
