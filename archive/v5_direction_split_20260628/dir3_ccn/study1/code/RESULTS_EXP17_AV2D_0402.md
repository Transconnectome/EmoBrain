# Results: Experiment 17 (Arousal-Valence 2D Comparison)

Date: 0402  
Source file: `results/exp17_av2d_results.npz`  
Metadata: `/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_14dims.csv`  
Raw fMRI input: `/pscratch/sd/s/sjmoon/EmoFM/raw_fmri_results/fmri_raw.npy`  
Figures:
- `figures/exp17_av2d_model_targets.png`
- `figures/exp17_av2d_raw_k_sweep.png`
- `figures/exp17_av2d_summary.png`

## Goal

This experiment revisits the category-vs-dimension question using only two affective dimensions:

- `Arousal`
- `Valence`

The same target set was used across three representations:

1. V-JEPA2 brain-predictable subspace
2. CLIP brain-predictable subspace
3. Raw fMRI

So the full target space here is:

- 34 emotion categories
- 2 affective dimensions (`Arousal`, `Valence`)

## Brain-Predictable PC Sets

- V-JEPA2: `PC1, PC2, PC3`
- CLIP: `PC1, PC2, PC3, PC5, PC6, PC7`

## Main Takeaways

### V-JEPA2

- Pred subspace mean category `R² = 0.0550`
- Pred subspace mean A/V `R² = 0.0382`
- Category/A-V ratio `= 1.441`

So with only `Arousal + Valence`, V-JEPA2 still looks category-skewed.

### CLIP

- Pred subspace mean category `R² = 0.1659`
- Pred subspace mean A/V `R² = 0.1664`
- Category/A-V ratio `= 0.997`

So CLIP is almost exactly balanced between categories and A/V in the 2D setting.

### Raw fMRI

At `k=27`:
- Mean category `R² = 0.1075`
- Mean A/V `R² = 0.1431`
- Category/A-V ratio `= 0.751`

At full `450D`:
- Mean category `R² = 0.0258`
- Mean A/V `R² = 0.0730`
- Category/A-V ratio `= 0.353`

So raw fMRI is clearly more A/V-heavy than category-heavy.

## Summary Table

| Representation | Setting | Mean category `R²` | Mean A/V `R²` | Category/A-V ratio |
|---|---|---:|---:|---:|
| V-JEPA2 | Brain-predictable PCs | 0.0550 | 0.0382 | 1.441 |
| V-JEPA2 | Unpredictable PCs | 0.1027 | 0.0800 | 1.284 |
| V-JEPA2 | All 100 PCs | 0.1703 | 0.1353 | 1.258 |
| CLIP | Brain-predictable PCs | 0.1659 | 0.1664 | 0.997 |
| CLIP | Unpredictable PCs | 0.1017 | 0.1193 | 0.852 |
| CLIP | All 100 PCs | 0.2904 | 0.3071 | 0.946 |
| Raw fMRI | PCA `k=27` | 0.1075 | 0.1431 | 0.751 |
| Raw fMRI | Full `450D` | 0.0258 | 0.0730 | 0.353 |

## Raw fMRI k-Sweep

| k | Mean category `R²` | Mean A/V `R²` | Category/A-V ratio |
|---:|---:|---:|---:|
| 3 | 0.0330 | 0.0382 | 0.8653 |
| 5 | 0.0523 | 0.0563 | 0.9277 |
| 7 | 0.0683 | 0.0709 | 0.9633 |
| 10 | 0.0865 | 0.1142 | 0.7569 |
| 15 | 0.0921 | 0.1138 | 0.8091 |
| 20 | 0.1018 | 0.1302 | 0.7814 |
| 25 | 0.1061 | 0.1396 | 0.7601 |
| 27 | 0.1075 | 0.1431 | 0.7514 |
| 30 | 0.1088 | 0.1466 | 0.7422 |
| 34 | 0.1102 | 0.1489 | 0.7396 |
| 40 | 0.1112 | 0.1470 | 0.7565 |
| 50 | 0.1140 | 0.1517 | 0.7513 |
| 75 | 0.1166 | 0.1605 | 0.7260 |
| 100 | 0.1154 | 0.1609 | 0.7177 |

## Strongest Signals

### V-JEPA2 brain-predictable subspace

Top 10 emotion categories:

| Rank | Emotion | Pred `R²` | All-PC `R²` |
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

A/V:

| Dimension | Pred `R²` | All-PC `R²` |
|---|---:|---:|
| Arousal | 0.0651 | 0.0889 |
| Valence | 0.0112 | 0.1817 |

### CLIP brain-predictable subspace

Top 10 emotion categories:

| Rank | Emotion | Pred `R²` | All-PC `R²` |
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

A/V:

| Dimension | Pred `R²` | All-PC `R²` |
|---|---:|---:|
| Arousal | 0.0621 | 0.1355 |
| Valence | 0.2706 | 0.4787 |

### Raw fMRI at `k=27`

Top 10 emotion categories:

| Rank | Emotion | `R² @ k=27` | `R² @ full450` |
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

A/V:

| Dimension | `R² @ k=27` | `R² @ full450` |
|---|---:|---:|
| Arousal | 0.0681 | 0.0000 |
| Valence | 0.2181 | 0.1461 |

## Full Target-Wise Results

Columns:
- `VJ pred`: V-JEPA2 brain-predictable subspace
- `VJ unpred`: V-JEPA2 unpredictable subspace
- `VJ all`: all 100 V-JEPA2 PCs
- `CLIP pred`: CLIP brain-predictable subspace
- `CLIP unpred`: CLIP unpredictable subspace
- `CLIP all`: all 100 CLIP PCs
- `Raw k27`: raw fMRI PCA `k=27`
- `Raw full`: raw fMRI full `450D`

| Target | VJ pred | VJ unpred | VJ all | CLIP pred | CLIP unpred | CLIP all | Raw k27 | Raw full |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Admiration | 0.023496 | 0.000000 | 0.002701 | 0.026622 | 0.030848 | 0.069546 | 0.027598 | 0.000000 |
| Adoration | 0.080494 | 0.267673 | 0.359657 | 0.142386 | 0.393330 | 0.546158 | 0.139063 | 0.000000 |
| Aesthetic appreciation | 0.323135 | 0.168748 | 0.550928 | 0.447327 | 0.146814 | 0.650459 | 0.233541 | 0.135140 |
| Amusement | 0.115904 | 0.180494 | 0.321917 | 0.339656 | 0.091285 | 0.471085 | 0.212581 | 0.077383 |
| Anger | 0.011802 | 0.051209 | 0.067057 | 0.181774 | 0.032473 | 0.232063 | 0.047553 | 0.000000 |
| Anxiety | 0.061135 | 0.165983 | 0.239447 | 0.203644 | 0.160941 | 0.391989 | 0.188895 | 0.051021 |
| Awe | 0.022231 | 0.221851 | 0.253794 | 0.209649 | 0.149256 | 0.384971 | 0.133998 | 0.000000 |
| Awkwardness | 0.030796 | 0.048706 | 0.083853 | 0.091264 | 0.024170 | 0.128058 | 0.072846 | 0.000000 |
| Boredom | 0.019606 | 0.083231 | 0.122826 | 0.101085 | 0.051224 | 0.173849 | 0.083553 | 0.000000 |
| Calmness | 0.136112 | 0.128374 | 0.317568 | 0.165505 | 0.144205 | 0.361124 | 0.113117 | 0.000000 |
| Confusion | 0.000000 | 0.007203 | 0.009453 | 0.029090 | 0.054512 | 0.093441 | 0.076096 | 0.000000 |
| Contempt | 0.000000 | 0.020372 | 0.020796 | 0.049327 | 0.000000 | 0.059550 | 0.011505 | 0.000000 |
| Craving | 0.016605 | 0.338593 | 0.364263 | 0.148219 | 0.440930 | 0.639435 | 0.072003 | 0.000000 |
| Disgust | 0.008802 | 0.000000 | 0.000000 | 0.084713 | 0.000000 | 0.054150 | 0.022219 | 0.000000 |
| Empathic pain | 0.074097 | 0.095258 | 0.182275 | 0.196400 | 0.148318 | 0.367122 | 0.266970 | 0.120476 |
| Entrancement | 0.002384 | 0.000000 | 0.006593 | 0.056352 | 0.011152 | 0.077427 | 0.095072 | 0.000000 |
| Excitement | 0.200124 | 0.152736 | 0.395510 | 0.286630 | 0.136445 | 0.466280 | 0.210654 | 0.110743 |
| Fear | 0.000000 | 0.000000 | 0.000000 | 0.038490 | 0.000000 | 0.012323 | 0.000000 | 0.000000 |
| Horror | 0.057006 | 0.062925 | 0.144722 | 0.170896 | 0.008505 | 0.208261 | 0.066202 | 0.000000 |
| Interest | 0.059754 | 0.196321 | 0.266689 | 0.253596 | 0.152531 | 0.429975 | 0.185706 | 0.062572 |
| Joy | 0.002780 | 0.000000 | 0.000000 | 0.028893 | 0.000000 | 0.009398 | 0.000000 | 0.000000 |
| Nostalgia | 0.016698 | 0.131809 | 0.156147 | 0.210044 | 0.069851 | 0.299905 | 0.131919 | 0.002055 |
| Relief | 0.057564 | 0.072027 | 0.155151 | 0.181839 | 0.035602 | 0.261588 | 0.127025 | 0.000000 |
| Romance | 0.079292 | 0.124061 | 0.223460 | 0.123616 | 0.241802 | 0.387931 | 0.128751 | 0.000000 |
| Sadness | 0.009389 | 0.183236 | 0.197498 | 0.192205 | 0.280825 | 0.525133 | 0.116120 | 0.000000 |
| Satisfaction | 0.007147 | 0.000000 | 0.000000 | 0.054351 | 0.040509 | 0.110902 | 0.020331 | 0.000000 |
| Sexual desire | 0.031337 | 0.085236 | 0.122138 | 0.105767 | 0.009882 | 0.126023 | 0.082296 | 0.000000 |
| Surprise | 0.044951 | 0.223447 | 0.276275 | 0.330832 | 0.243738 | 0.607380 | 0.110189 | 0.000000 |
| Sympathy | 0.005896 | 0.032220 | 0.043999 | 0.195932 | 0.063171 | 0.279468 | 0.041795 | 0.000000 |
| Triumph | 0.012807 | 0.030601 | 0.046547 | 0.043598 | 0.028998 | 0.076664 | 0.048094 | 0.000000 |
| Uncomfortable | 0.171491 | 0.300459 | 0.498979 | 0.537881 | 0.136667 | 0.727499 | 0.322580 | 0.291873 |
| Annoyance | 0.105711 | 0.067778 | 0.182832 | 0.188162 | 0.053350 | 0.259957 | 0.178872 | 0.026453 |
| Envy | 0.029347 | 0.000000 | 0.024083 | 0.102990 | 0.060852 | 0.176399 | 0.032068 | 0.000000 |
| Guilt | 0.051776 | 0.051820 | 0.151706 | 0.121121 | 0.014822 | 0.207844 | 0.057138 | 0.000000 |
| Arousal | 0.065094 | 0.003703 | 0.088923 | 0.062126 | 0.058523 | 0.135484 | 0.068101 | 0.000000 |
| Valence | 0.011222 | 0.156240 | 0.181673 | 0.270625 | 0.180027 | 0.478706 | 0.218121 | 0.146069 |

## Interpretation

The 2D result is useful because it separates the effect of using many dimensions from the simpler question of just `Arousal + Valence`.

The pattern is:

1. V-JEPA2 remains category-leaning even in the 2D setting.
2. CLIP becomes almost perfectly balanced between categories and A/V.
3. Raw fMRI remains more A/V-weighted than category-weighted.

So the story across target spaces now looks consistent:

- `3D (A/V/D)`: V-JEPA2 category-skewed, CLIP more mixed
- `2D (A/V)`: V-JEPA2 category-skewed, CLIP nearly balanced, raw fMRI A/V-heavy
- `14D`: V-JEPA2 still category-leaning, CLIP and raw fMRI become more dimension-heavy

That makes the broad interpretation stronger:

- the neural and model spaces are not purely category-based,
- but the balance depends on representation type and on how rich the affective dimension set is.
