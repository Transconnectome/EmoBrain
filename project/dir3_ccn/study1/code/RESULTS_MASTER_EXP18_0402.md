# CCN Results Master Document (Updated Through Experiment 18)

Date: 0402  
Scope: Experiments / scripts 01-18, including 3D, 14D, raw-fMRI, A/V 2D, and subject-wise follow-ups.

## 0. What This Document Is

This is the updated master results document for the CCN analysis series.

Compared with [RESULTS_MASTER_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_MASTER_0402.md), this version adds:

- Exp 12 re-run with 14 affective dimensions
- Exp 13 re-run with 14 affective dimensions
- Exp 16 re-run with 14 affective dimensions
- Raw-fMRI Exp 12 analogue with 14 affective dimensions
- Arousal/Valence 2D comparison (Exp 17)
- Subject-wise claim check (Exp 18)

One note up front:

- `Exp 14` script exists, but no result file was found in `results/` at the time this document was written.

## 1. Data and Main Question

Core inputs:

- Brain-JEPA embeddings: `(2196, 768)` mean over 5 subjects
- Raw fMRI: `(5, 2196, 450)`
- V-JEPA2 embeddings: `(2196, 1408)`
- CLIP embeddings: `(2196, 512)`
- Emotion metadata: 34 continuous emotion scores
- Affective targets used across variants:
  - 3D: `Arousal`, `Valence`, `Dominance`
  - 14D: `Approach`, `Arousal`, `Attention`, `Certainty`, `Commitment`, `Control`, `Dominance`, `Effort`, `Fairness`, `Identity`, `Obstruction`, `Safety`, `Upswing`, `Valence`
  - 2D: `Arousal`, `Valence`

Main question:

> How much of the shared neural-computational structure is affective, how low-dimensional is it, and is it better described by fine-grained emotion categories or broader affective dimensions?

## 2. Methods and Terms

Short glossary:

- `Embedding`: vector representation of each stimulus.
- `PCA`: dimensionality reduction used to test how many dimensions are needed.
- `RSM`: representational similarity matrix, usually stimulus-by-stimulus cosine similarity.
- `RSA`: correlation between RSMs, used to compare geometry across spaces.
- `CKA`: scale-invariant similarity measure between spaces.
- `Procrustes`: alignment error after optimal linear transformation.
- `Ridge CV R²`: prediction accuracy with regularized regression under cross-validation.
- `Brain-predictable PCs`: model PCs that can be predicted from neural embeddings above threshold.
- `Partial RSA / Partial R²`: neural-model alignment or prediction after regressing out vision/semantic confounds.

## 3. Highest-Level Conclusions

Across all analyses through Exp 18, the most stable conclusions are:

1. Neural-computational alignment is effectively low-dimensional and saturates around `k ≈ 27`.
2. The brain does not appear to read the full model space; it reads a much smaller subspace.
3. That readable subspace is affectively meaningful.
4. But a substantial fraction of the affective signal overlaps with explicit visual and semantic structure.
5. The category-vs-dimension balance depends strongly on both the representation and the dimensional target space:
   - V-JEPA2 is the most category-leaning.
   - CLIP is more mixed, and becomes dimension-heavier as the target space becomes richer.
   - Raw fMRI is the most dimension-heavy in the richer target spaces.
6. Subject-wise follow-up shows that V-JEPA2's category-leaning tendency is much more stable than CLIP's, while some CLIP dimension-heavy tendencies depend more strongly on subject averaging.

## 4. Results by Analysis Stage

### 4.1 Core geometry: Scripts 01-10

The early analyses established the geometric backbone of the story.

Key takeaways:

- Brain-JEPA had strong cross-subject consistency compared with raw fMRI.
- Raw fMRI kept more direct emotion information than Brain-JEPA.
- Neural-model alignment and emotion predictability both saturated around `k ≈ 27`.
- The same low-dimensional regime appeared across Brain-JEPA, raw fMRI, and model spaces.

Main references:

- [RESULTS_MASTER_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_MASTER_0402.md)
- [RESULTS_FULL_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_FULL_0402.md)

Representative numbers already established:

- Brain-JEPA subject-consistency was much higher than raw fMRI.
- Raw fMRI decoding plateaued near the same `k ≈ 27` regime.
- Brain-JEPA and raw fMRI both supported the idea of a compact shared geometry rather than a very high-dimensional one.

### 4.2 Experiment 11: Brain-predictable PC × emotion correlation

Reference:
- [RESULTS_EXP11_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP11_0402.md)

What it established:

- Only a very small number of model PCs were strongly brain-predictable.
- Those PCs showed meaningful correlations with emotion labels.
- This motivated the subspace interpretation used in Exp 12 and Exp 13.

### 4.3 Experiment 12 (3D): brain-predictable subspace, categories vs A/V/D

Reference:
- [RESULTS_EXP12_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP12_0402.md)

Main numbers:

| Model | Mean category `R²` | Mean A/V/D `R²` | Category/dimension ratio |
|---|---:|---:|---:|
| V-JEPA2 pred subspace | 0.0550 | 0.0254 | 2.162 |
| CLIP pred subspace | 0.1659 | 0.1297 | 1.279 |

Interpretation:

- V-JEPA2 was strongly category-leaning in the 3D setting.
- CLIP was still category > dimension, but much less so.

### 4.4 Experiment 13 (3D): vision / semantic confound control

Reference:
- [RESULTS_EXP13_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP13_0402.md)

Main numbers:

| Model | Original mean category `R²` | Partial mean category `R²` | Original mean A/V/D `R²` | Partial mean A/V/D `R²` |
|---|---:|---:|---:|---:|
| V-JEPA2 | 0.0550 | 0.0051 | 0.0254 | 0.0029 |
| CLIP | 0.1659 | 0.0134 | 0.1297 | 0.0086 |

Interpretation:

- Most affective predictability overlapped with vision/semantic structure.
- But the residual was not exactly zero.

### 4.5 Experiment 15: stability and alpha sensitivity

Reference:
- [RESULTS_EXP15_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP15_0402.md)

What it showed:

- The brain-readable subspace is very small.
- Across subjects, the most stable core was even smaller than the mean-subject mask.
- Resampling preserved the main qualitative story.
- Alpha sensitivity did not reverse the central findings.

Representative numbers:

- V-JEPA2 mean-subject mask: `PC1, PC2, PC3`
- CLIP mean-subject mask: `PC1, PC2, PC3, PC5, PC6, PC7`
- Subject-level stable core:
  - V-JEPA2: mainly `PC1`, with `PC3` in 2/5 subjects
  - CLIP: mainly `PC1`, with `PC2` in 2/5 subjects

### 4.6 Experiment 16 (3D): incremental benchmark over vision + semantic baseline

Reference:
- [RESULTS_EXP16_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP16_0402.md)

Main numbers:

| Added feature set | Mean category delta `R²` | Mean A/V/D delta `R²` |
|---|---:|---:|
| V-JEPA2 PCs | +0.0022 | +0.0001 |
| CLIP PCs | +0.0065 | +0.0079 |

Interpretation:

- Model PCs are not fully redundant with explicit vision + semantic features.
- CLIP adds more incremental variance than V-JEPA2.

## 5. 14-Dimension Re-Runs

### 5.1 Experiment 12 (14D)

Reference:
- [RESULTS_EXP12_14D_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP12_14D_0402.md)

Main numbers:

| Model | Mean category `R²` | Mean 14D `R²` | Category/dimension ratio |
|---|---:|---:|---:|
| V-JEPA2 pred subspace | 0.0550 | 0.0306 | 1.794 |
| CLIP pred subspace | 0.1659 | 0.1802 | 0.921 |

Interpretation:

- V-JEPA2 remained category-leaning.
- CLIP no longer looked category-dominant; it became slightly dimension-heavier.

This is a major update relative to the 3D result.

### 5.2 Experiment 13 (14D)

Reference:
- [RESULTS_EXP13_14D_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP13_14D_0402.md)

Main numbers:

| Model | Original mean category `R²` | Partial mean category `R²` | Original mean 14D `R²` | Partial mean 14D `R²` |
|---|---:|---:|---:|---:|
| V-JEPA2 | 0.0550 | 0.0051 | 0.0306 | 0.0026 |
| CLIP | 0.1659 | 0.0134 | 0.1802 | 0.0191 |

Interpretation:

- The broad conclusion from 3D Exp 13 survives the 14D re-run.
- Much of the signal still overlaps with explicit vision/semantic structure.
- CLIP retains slightly more residual 14D variance than V-JEPA2.

### 5.3 Experiment 16 (14D)

Reference:
- [RESULTS_EXP16_14D_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP16_14D_0402.md)

Main numbers:

| Added feature set | Mean category delta `R²` | Mean 14D delta `R²` |
|---|---:|---:|
| V-JEPA2 PCs | +0.0022 | +0.0015 |
| CLIP PCs | +0.0065 | +0.0139 |

Interpretation:

- CLIP’s incremental value becomes even clearer in the richer 14D target space.
- The extra contribution beyond vision+semantic is especially strong for broad affective dimensions.

## 6. Raw fMRI Follow-Up

### 6.1 Raw Exp 12 analogue with 14D

Reference:
- [RESULTS_EXP12_RAW_14D_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP12_RAW_14D_0402.md)

Main numbers:

| Raw fMRI setting | Mean category `R²` | Mean 14D `R²` | Category/dimension ratio |
|---|---:|---:|---:|
| PCA `k=27` | 0.1075 | 0.1557 | 0.691 |
| Full `450D` | 0.0258 | 0.0610 | 0.423 |

Interpretation:

- Raw fMRI is clearly dimension-heavier than category-heavier in the 14D space.
- `k=27` works much better than full `450D`, consistent with low-dimensional affective structure and high-dimensional noise.

This result is important because it shows that direct neural data itself becomes dimension-dominant once the target space is broadened beyond 3D.

## 7. Experiment 17: Arousal / Valence 2D Comparison

Reference:
- [RESULTS_EXP17_AV2D_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP17_AV2D_0402.md)

Main numbers:

| Representation | Setting | Mean category `R²` | Mean A/V `R²` | Category/A-V ratio |
|---|---|---:|---:|---:|
| V-JEPA2 | Brain-predictable PCs | 0.0550 | 0.0382 | 1.441 |
| CLIP | Brain-predictable PCs | 0.1659 | 0.1664 | 0.997 |
| Raw fMRI | PCA `k=27` | 0.1075 | 0.1431 | 0.751 |
| Raw fMRI | Full `450D` | 0.0258 | 0.0730 | 0.353 |

Interpretation:

- V-JEPA2 remains category-leaning in 2D.
- CLIP becomes almost exactly balanced.
- Raw fMRI remains A/V-heavy.

This makes the transition across target spaces especially informative:

- 3D: V-JEPA2 category-skewed, CLIP mixed
- 2D: V-JEPA2 category-skewed, CLIP nearly balanced, raw fMRI A/V-heavy
- 14D: V-JEPA2 still category-leaning, CLIP and raw fMRI more dimension-heavy

## 8. Experiment 18: Subject-wise Claim Check

Reference:
- [RESULTS_EXP18_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP18_0402.md)

What it tested:

- whether the group-level category-vs-dimension claims survive when brain-predictable PCs are defined separately for each individual subject
- whether the readable subspace size and orientation are robust to replacing the group-mean Brain-JEPA representation with single-subject Brain-JEPA representations

Main numbers:

| Neural representation | V-JEPA2 predictable PCs | CLIP predictable PCs |
|---|---:|---:|
| Mean | 3 | 6 |
| Subject 1 | 1 | 1 |
| Subject 2 | 2 | 2 |
| Subject 3 | 2 | 2 |
| Subject 4 | 1 | 1 |
| Subject 5 | 1 | 1 |

Agreement with the group-level orientation:

| Ontology | V-JEPA2 | CLIP |
|---|---:|---:|
| 3D | 5/5 | 5/5 |
| 14D | 5/5 | 3/5 |
| 2D | 5/5 | 0/5 |

Interpretation:

- V-JEPA2 remains consistently category-leaning across all five subjects in `3D`, `14D`, and `2D`
- the readable subspace remains very small at the subject level, with `PC1` forming the most stable core axis
- CLIP is less stable than V-JEPA2 across subjects
- specifically, CLIP's mean-level `14D` dimension-heavy tendency is only partially stable, and its `2D` near-balance is not reproduced at the individual-subject level

This makes the final interpretation more precise:

- V-JEPA2's category-leaning tendency is robust to subject-wise analysis
- CLIP's category-vs-dimension balance is more sensitive to group averaging and target ontology

## 9. Integrated Interpretation

The strongest integrated interpretation through Exp 18 is:

1. The shared neural-computational geometry is low-dimensional, with a stable saturation regime around `k ≈ 27`.
2. The brain-readable part of model space is very small.
3. That small readable subspace is affective, but not cleanly isolated from visual and semantic structure.
4. V-JEPA2 tends to be the most category-leaning representation.
5. V-JEPA2's category-leaning tendency remains stable at the subject level.
6. CLIP is more mixed and becomes increasingly dimension-heavy as the dimensional target space is expanded, but some of these tendencies are less stable across individual subjects.
7. Raw fMRI itself is already dimension-heavy in the richer target spaces.

So the safest overall claim is no longer:

> the neural signal is mainly category-based

but rather:

> the neural and model spaces share a small, affectively meaningful, low-dimensional geometry; the category-vs-dimension balance depends on both the representation and the richness of the affective target space.

## 10. Practical Claim Guidance

Claims that now look strong:

- There is a compact shared geometry around `k ≈ 27`.
- The readable model subspace is much smaller than the full model space.
- That readable subspace is affectively meaningful.
- Vision and semantic confounds explain a substantial portion of the observed affective signal.
- V-JEPA2 remains category-leaning even under subject-wise follow-up.
- Raw fMRI and CLIP become more dimension-heavy when the affective target ontology is broadened.

Claims that now need caution:

- "The neural signal is primarily category-based."
- "V-JEPA2 is globally more brain-like than CLIP."
- "A/V/D results generalize straightforwardly to richer affective spaces."
- "CLIP is uniformly dimension-heavy or uniformly balanced at the individual-subject level."

## 11. File Index

Core prior master:
- [RESULTS_MASTER_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_MASTER_0402.md)

Detailed result documents:
- [RESULTS_EXP11_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP11_0402.md)
- [RESULTS_EXP12_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP12_0402.md)
- [RESULTS_EXP13_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP13_0402.md)
- [RESULTS_EXP15_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP15_0402.md)
- [RESULTS_EXP16_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP16_0402.md)
- [RESULTS_EXP12_14D_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP12_14D_0402.md)
- [RESULTS_EXP13_14D_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP13_14D_0402.md)
- [RESULTS_EXP16_14D_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP16_14D_0402.md)
- [RESULTS_EXP12_RAW_14D_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP12_RAW_14D_0402.md)
- [RESULTS_EXP17_AV2D_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP17_AV2D_0402.md)
- [RESULTS_EXP18_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP18_0402.md)

Missing result file:

- `Exp 14`: script exists, but `results/exp14_robustness_results.npz` was not found when this document was generated.

## 12. Embedded Detailed Records

This section inlines the detailed result records directly into this master file so that the document can be read as a single self-contained results archive.

### 12.1 Experiment 11: Brain-Predictable PC × Emotion Correlation

Goal:

- determine what the brain-predictable V-JEPA2 / CLIP PCs actually represent
- test whether the readable PCs are affective rather than generic perceptual axes

Method:

1. PCA to 100 PCs for V-JEPA2 and CLIP
2. Spearman correlation between each PC and 34 emotion scores
3. Spearman correlation between each PC and `Arousal / Valence / Dominance`
4. FDR correction
5. compare brain-predictable PCs vs brain-unpredictable PCs

Main conclusion:

- the result supports the strong affective-subspace reading
- brain-predictable PCs showed much larger emotion correlations than unpredictable PCs

#### V-JEPA2: brain-predictable PCs

- selected PCs: `PC1, PC2, PC3`

| PC | Brain predictability `R²` | Explained variance | Max `|r|` with emotion | FDR-significant emotions |
|---|---:|---:|---:|---:|
| PC1 | 0.3728 | 17.02% | 0.3277 | 26 |
| PC2 | 0.0748 | 5.53% | 0.3544 | 24 |
| PC3 | 0.0878 | 5.07% | 0.3034 | 25 |

Top associations:

- `PC1`: `Aesthetic appreciation -0.3277`, `Annoyance +0.3253`, `Calmness -0.2880`
- `PC2`: `Aesthetic appreciation +0.3544`, `Excitement +0.3276`, `Adoration -0.2791`
- `PC3`: `Uncomfortable -0.3034`, `Empathic pain -0.2384`, `Guilt +0.2369`

A/V/D:

- `PC1`: `Arousal +0.1408`, `Valence -0.1259`, `Dominance +0.0422`
- `PC2`: `Arousal +0.2254`, `Valence -0.0823`, `Dominance -0.0234`
- `PC3`: `Arousal +0.0297`, `Valence +0.0615`, `Dominance +0.0426`

Brain-predictable vs unpredictable comparison:

| Model | n brain-predictable PCs | Mean max `|r|` brain-predictable | Mean max `|r|` brain-unpredictable | Delta |
|---|---:|---:|---:|---:|
| V-JEPA2 | 3 | 0.3285 | 0.0903 | +0.2382 |

#### CLIP: brain-predictable PCs

- selected PCs: `PC1, PC2, PC3, PC5, PC6, PC7`

| PC | Brain predictability `R²` | Explained variance | Max `|r|` with emotion | FDR-significant emotions |
|---|---:|---:|---:|---:|
| PC1 | 0.2613 | 8.27% | 0.4512 | 28 |
| PC2 | 0.1559 | 6.26% | 0.4726 | 18 |
| PC3 | 0.1271 | 5.17% | 0.2269 | 24 |
| PC5 | 0.1154 | 3.47% | 0.3497 | 20 |
| PC6 | 0.0167 | 2.93% | 0.3131 | 29 |
| PC7 | 0.0125 | 2.45% | 0.4029 | 27 |

Top associations:

- `PC1`: `Annoyance -0.4512`, `Uncomfortable +0.4162`, `Surprise +0.3637`
- `PC2`: `Aesthetic appreciation -0.4726`, `Excitement -0.4029`, `Uncomfortable +0.3613`
- `PC3`: `Guilt -0.2269`, `Awe +0.2142`, `Horror -0.2088`
- `PC5`: `Uncomfortable +0.3497`, `Sadness -0.2740`, `Horror +0.2724`
- `PC6`: `Nostalgia +0.3131`, `Interest +0.3107`, `Sympathy +0.2923`
- `PC7`: `Empathic pain +0.4029`, `Amusement -0.2917`, `Romance -0.2856`

Brain-predictable vs unpredictable comparison:

| Model | n brain-predictable PCs | Mean max `|r|` brain-predictable | Mean max `|r|` brain-unpredictable | Delta |
|---|---:|---:|---:|---:|
| CLIP | 6 | 0.3660 | 0.1004 | +0.2656 |

Summary interpretation:

- the readable model PCs are strongly affective
- this motivates the subspace analyses in Exp 12 and Exp 13

### 12.2 Experiment 12: Brain-Predictable Subspace vs Category / A/V/D

Brain-predictable PC sets:

- V-JEPA2: `PC1, PC2, PC3`
- CLIP: `PC1, PC2, PC3, PC5, PC6, PC7`

#### Full summary table

| Model | Subspace | Mean category `R²` | Mean A/V/D `R²` | Category/dimension ratio |
|---|---|---:|---:|---:|
| V-JEPA2 | Brain-predictable PCs | 0.0550 | 0.0254 | 2.162 |
| V-JEPA2 | Unpredictable PCs | 0.1027 | 0.0533 | 1.926 |
| V-JEPA2 | All 100 PCs | 0.1703 | 0.0903 | 1.886 |
| CLIP | Brain-predictable PCs | 0.1659 | 0.1297 | 1.279 |
| CLIP | Unpredictable PCs | 0.1017 | 0.0842 | 1.208 |
| CLIP | All 100 PCs | 0.2904 | 0.2260 | 1.285 |

#### V-JEPA2 top emotions and A/V/D

Top 10 emotion categories:

| Rank | Emotion | Pred `R²` | All `R²` | Efficiency |
|---:|---|---:|---:|---:|
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

Bottom 5:

| Emotion | Pred `R²` | All `R²` |
|---|---:|---:|
| Joy | 0.0028 | 0.0000 |
| Entrancement | 0.0024 | 0.0066 |
| Confusion | 0.0000 | 0.0095 |
| Contempt | 0.0000 | 0.0208 |
| Fear | 0.0000 | 0.0000 |

A/V/D:

| Dimension | Pred `R²` | All `R²` | Efficiency |
|---|---:|---:|---:|
| Arousal | 0.0651 | 0.0889 | 0.732 |
| Valence | 0.0112 | 0.1817 | 0.062 |
| Dominance | 0.0000 | 0.0004 | 0.000 |

#### CLIP top emotions and A/V/D

Top 10 emotion categories:

| Rank | Emotion | Pred `R²` | All `R²` | Efficiency |
|---:|---|---:|---:|---:|
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

Bottom 5:

| Emotion | Pred `R²` | All `R²` |
|---|---:|---:|
| Triumph | 0.0436 | 0.0767 |
| Fear | 0.0385 | 0.0123 |
| Confusion | 0.0291 | 0.0934 |
| Joy | 0.0289 | 0.0094 |
| Admiration | 0.0266 | 0.0695 |

A/V/D:

| Dimension | Pred `R²` | All `R²` | Efficiency |
|---|---:|---:|---:|
| Arousal | 0.0621 | 0.1355 | 0.459 |
| Valence | 0.2706 | 0.4787 | 0.565 |
| Dominance | 0.0565 | 0.0639 | 0.884 |

Interpretation:

- V-JEPA2 is clearly category-skewed in 3D
- CLIP is still category > dimension, but much less so

### 12.3 Experiment 13: Vision / Semantic Confound Control

#### Partial RSA

| Source | Model | Original RSA | Partial RSA | Delta | p-value |
|---|---:|---:|---:|---:|---:|
| Brain-JEPA | V-JEPA2 | -0.007063 | -0.004500 | +0.002562 | 2.812e-12 |
| Brain-JEPA | CLIP | -0.069710 | -0.068558 | +0.001153 | 0.000e+00 |
| Raw fMRI | V-JEPA2 | 0.095617 | 0.077626 | -0.017992 | 0.000e+00 |
| Raw fMRI | CLIP | 0.088632 | 0.071745 | -0.016888 | 0.000e+00 |

#### Partial target prediction summary

| Model | Mean category `R²` original | Mean category `R²` partial | Mean A/V/D `R²` original | Mean A/V/D `R²` partial | Category retained | Dimension retained |
|---|---:|---:|---:|---:|---:|---:|
| V-JEPA2 | 0.054990 | 0.005117 | 0.025439 | 0.002932 | 0.0930 | 0.1152 |
| CLIP | 0.165878 | 0.013403 | 0.129741 | 0.008595 | 0.0808 | 0.0663 |

#### V-JEPA2 top partial residual emotions

| Rank | Emotion | Original `R²` | Partial `R²` | Delta | Retained |
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

#### CLIP top partial residual emotions

| Rank | Emotion | Original `R²` | Partial `R²` | Delta | Retained |
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

A/V/D:

| Model | Arousal | Valence | Dominance |
|---|---|---|---|
| V-JEPA2 | `0.065094 -> 0.008795` | `0.011222 -> 0.000000` | `0.000000 -> 0.000000` |
| CLIP | `0.062126 -> 0.000000` | `0.270625 -> 0.025786` | `0.056473 -> 0.000000` |

Interpretation:

- most affective signal overlaps with explicit vision/semantic structure
- residual affective signal remains, but it is much smaller

### 12.4 Experiment 15: Subject Stability, Resampling, Alpha Sensitivity

#### Subject-wise predictable PCs

| Model | Mean-subject mask | Subject-level stable core |
|---|---|---|
| V-JEPA2 | `PC1, PC2, PC3` | `PC1` in 5/5, `PC3` in 2/5 |
| CLIP | `PC1, PC2, PC3, PC5, PC6, PC7` | `PC1` in 5/5, `PC2` in 2/5 |

Per-subject selected PCs:

| Subject | V-JEPA2 | CLIP |
|---|---|---|
| 1 | `1` | `1` |
| 2 | `1, 3` | `1, 2` |
| 3 | `1, 3` | `1, 2` |
| 4 | `1` | `1` |
| 5 | `1` | `1` |

#### Resampling stability

| Model | Mean category `R²` | Mean dimension `R²` | Category/dimension ratio | 95% interval for ratio |
|---|---:|---:|---:|---:|
| V-JEPA2 | 0.0506 | 0.0230 | 2.3056 | 1.6130 - 3.7747 |
| CLIP | 0.1569 | 0.1256 | 1.2544 | 1.0903 - 1.4280 |

Top-5 emotion stability counts:

| Model | Stable top emotions |
|---|---|
| V-JEPA2 | `Excitement 100`, `Uncomfortable 100`, `Aesthetic appreciation 100`, `Calmness 83`, `Amusement 79` |
| CLIP | `Uncomfortable 100`, `Aesthetic appreciation 100`, `Amusement 100`, `Excitement 94`, `Surprise 93` |

#### Alpha sensitivity

| Alpha | Exp12 cat VJ | Exp12 dim VJ | Exp12 cat CLIP | Exp12 dim CLIP | Exp13 cat VJ | Exp13 dim VJ | Exp13 cat CLIP | Exp13 dim CLIP |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.1 | 0.0550 | 0.0254 | 0.1659 | 0.1297 | 0.0051 | 0.0029 | 0.0134 | 0.0086 |
| 1.0 | 0.0550 | 0.0254 | 0.1659 | 0.1297 | 0.0051 | 0.0029 | 0.0134 | 0.0086 |
| 10.0 | 0.0550 | 0.0254 | 0.1660 | 0.1298 | 0.0051 | 0.0030 | 0.0135 | 0.0086 |
| 100.0 | 0.0551 | 0.0254 | 0.1661 | 0.1296 | 0.0053 | 0.0031 | 0.0139 | 0.0089 |

Interpretation:

- subject-level stable core is even smaller than the mean-level mask
- resampling and alpha choices do not change the qualitative story

### 12.5 Experiment 16: Incremental Baseline Benchmark

#### Model family summary

| Model | Mean category `R²` | Mean A/V/D `R²` | Category/dimension ratio |
|---|---:|---:|---:|
| Vision + Semantic baseline | 0.0796 | 0.0991 | 0.8027 |
| V-JEPA2 PCs only | 0.0550 | 0.0254 | 2.1615 |
| CLIP PCs only | 0.1659 | 0.1297 | 1.2785 |
| Baseline + V-JEPA2 PCs | 0.0818 | 0.0993 | 0.8238 |
| Baseline + CLIP PCs | 0.0861 | 0.1071 | 0.8042 |

Incremental gain:

| Added feature set | Mean category delta `R²` | Mean A/V/D delta `R²` |
|---|---:|---:|
| V-JEPA2 PCs | +0.0022 | +0.0001 |
| CLIP PCs | +0.0065 | +0.0079 |

Top incremental targets:

| Model | Strongest gains |
|---|---|
| Baseline + V-JEPA2 | `Aesthetic appreciation +0.0387`, `Excitement +0.0141`, `Adoration +0.0118` |
| Baseline + CLIP | `Aesthetic appreciation +0.0567`, `Amusement +0.0540`, `Excitement +0.0258`, `Valence +0.0238`, `Interest +0.0218` |

Interpretation:

- model PCs are not fully redundant with explicit vision+semantic features
- the extra contribution is modest
- CLIP adds more incremental variance than V-JEPA2

### 12.6 Experiment 12 (14D): Category vs 14 Dimensions

#### Summary table

| Model | Subspace | Mean category `R²` | Mean 14D `R²` | Category/dimension ratio |
|---|---|---:|---:|---:|
| V-JEPA2 | Brain-predictable PCs | 0.0550 | 0.0306 | 1.794 |
| V-JEPA2 | Unpredictable PCs | 0.1027 | 0.0912 | 1.126 |
| V-JEPA2 | All 100 PCs | 0.1703 | 0.1304 | 1.305 |
| CLIP | Brain-predictable PCs | 0.1659 | 0.1802 | 0.921 |
| CLIP | Unpredictable PCs | 0.1017 | 0.1095 | 0.929 |
| CLIP | All 100 PCs | 0.2904 | 0.3095 | 0.938 |

#### Strongest dimensions in the brain-predictable subspace

V-JEPA2:

| Rank | Dimension | Pred `R²` | All `R²` |
|---:|---|---:|---:|
| 1 | Safety | 0.0685 | 0.2813 |
| 2 | Commitment | 0.0653 | 0.1974 |
| 3 | Arousal | 0.0651 | 0.0889 |
| 4 | Attention | 0.0480 | 0.0452 |
| 5 | Control | 0.0443 | 0.2261 |

CLIP:

| Rank | Dimension | Pred `R²` | All `R²` |
|---:|---|---:|---:|
| 1 | Safety | 0.3259 | 0.5245 |
| 2 | Control | 0.3156 | 0.4389 |
| 3 | Fairness | 0.2771 | 0.3701 |
| 4 | Valence | 0.2706 | 0.4787 |
| 5 | Approach | 0.2473 | 0.4739 |

Interpretation:

- V-JEPA2 remains category-skewed
- CLIP becomes slightly dimension-heavy in the richer 14D space

### 12.7 Experiment 13 (14D): Confound-Controlled Residuals

#### Partial RSA

| Neural source | Model | Original RSA | Partial RSA | Delta | p-value |
|---|---|---:|---:|---:|---:|
| Brain-JEPA | V-JEPA2 | -0.0071 | -0.0045 | +0.0026 | 2.81e-12 |
| Brain-JEPA | CLIP | -0.0697 | -0.0686 | +0.0012 | 0.00e+00 |
| Raw fMRI | V-JEPA2 | 0.0956 | 0.0776 | -0.0180 | 0.00e+00 |
| Raw fMRI | CLIP | 0.0886 | 0.0717 | -0.0169 | 0.00e+00 |

#### Partial prediction summary

| Model | Mean category `R²` original | Mean category `R²` partial | Mean 14D `R²` original | Mean 14D `R²` partial | Category retained | 14D retained |
|---|---:|---:|---:|---:|---:|---:|
| V-JEPA2 | 0.0550 | 0.0051 | 0.0306 | 0.0026 | 0.093 | 0.086 |
| CLIP | 0.1659 | 0.0134 | 0.1802 | 0.0191 | 0.081 | 0.106 |

Top residual dimensions:

| Model | Strongest surviving 14D residuals |
|---|---|
| V-JEPA2 | `Effort 0.0120`, `Arousal 0.0088`, `Safety 0.0076`, `Control 0.0072` |
| CLIP | `Control 0.0680`, `Safety 0.0549`, `Fairness 0.0371`, `Valence 0.0258`, `Obstruction 0.0184` |

Interpretation:

- the 14D rerun does not rescue the signal after confound control
- most signal still overlaps with explicit vision/semantic structure
- CLIP retains slightly more residual 14D structure than V-JEPA2

### 12.8 Experiment 16 (14D): Incremental Benchmark

#### Baseline summary

| Model | Mean category `R²` | Mean 14D `R²` | Category/dimension ratio |
|---|---:|---:|---:|
| Vision + Semantic baseline | 0.0796 | 0.0943 | 0.844 |
| V-JEPA2 PCs only | 0.0550 | 0.0306 | 1.794 |
| CLIP PCs only | 0.1659 | 0.1802 | 0.921 |
| Baseline + V-JEPA2 PCs | 0.0818 | 0.0958 | 0.853 |
| Baseline + CLIP PCs | 0.0861 | 0.1082 | 0.796 |

Incremental gain:

| Added feature set | Mean category delta `R²` | Mean 14D delta `R²` |
|---|---:|---:|
| V-JEPA2 PCs | +0.0022 | +0.0015 |
| CLIP PCs | +0.0065 | +0.0139 |

Top incremental dimensions:

| Model | Strongest gains |
|---|---|
| Baseline + V-JEPA2 | `Effort +0.0150`, `Safety +0.0049`, `Control +0.0043` |
| Baseline + CLIP | `Control +0.0474`, `Safety +0.0336`, `Fairness +0.0315`, `Valence +0.0238`, `Effort +0.0225`, `Approach +0.0208` |

Interpretation:

- CLIP’s incremental value becomes clearer in the 14D target space
- the additional variance beyond baseline is especially strong for broad affective dimensions

### 12.9 Raw fMRI Analogue of Exp 12 (14D)

#### k-sweep summary

| k | Mean category `R²` | Mean 14D `R²` | Category/dimension ratio |
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

Reference settings:

| Setting | Mean category `R²` | Mean 14D `R²` | Category/dimension ratio |
|---|---:|---:|---:|
| Raw fMRI PCA `k=27` | 0.1075 | 0.1557 | 0.6907 |
| Raw fMRI full `450D` | 0.0258 | 0.0610 | 0.4229 |

Strongest raw 14D dimensions at `k=27`:

| Rank | Dimension | `R² @ k=27` | `R² @ full450` |
|---:|---|---:|---:|
| 1 | Safety | 0.2493 | 0.1677 |
| 2 | Control | 0.2436 | 0.1624 |
| 3 | Valence | 0.2181 | 0.1461 |
| 4 | Approach | 0.2155 | 0.1286 |
| 5 | Effort | 0.1821 | 0.0752 |

Interpretation:

- raw fMRI is dimension-heavier than category-heavier in the 14D space
- this supports the idea that direct neural signal itself becomes dimension-dominant once the target ontology is broadened

### 12.10 Experiment 17: Arousal / Valence 2D Comparison

#### Summary table

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

Raw k-sweep:

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

Interpretation:

- V-JEPA2 remains category-skewed in 2D
- CLIP becomes almost exactly balanced
- raw fMRI remains A/V-heavy

### 12.11 Experiment 18: Subject-wise Claim Check

#### Predictable PC counts

| Neural representation | V-JEPA2 predictable PCs | CLIP predictable PCs |
|---|---:|---:|
| Mean | 3 | 6 |
| Subject 1 | 1 | 1 |
| Subject 2 | 2 | 2 |
| Subject 3 | 2 | 2 |
| Subject 4 | 1 | 1 |
| Subject 5 | 1 | 1 |

Predictable PC identities:

- V-JEPA2 mean: `PC1, PC2, PC3`
- V-JEPA2 subjects: `subj1=PC1`, `subj2=PC1,PC3`, `subj3=PC1,PC3`, `subj4=PC1`, `subj5=PC1`
- CLIP mean: `PC1, PC2, PC3, PC5, PC6, PC7`
- CLIP subjects: `subj1=PC1`, `subj2=PC1,PC2`, `subj3=PC1,PC2`, `subj4=PC1`, `subj5=PC1`

#### Subject-wise category-vs-dimension balance

3D:

| Neural representation | V-JEPA2 ratio | CLIP ratio |
|---|---:|---:|
| Mean | 2.162 | 1.279 |
| Subject 1 | 2.937 | 2.591 |
| Subject 2 | 3.969 | 3.768 |
| Subject 3 | 3.969 | 3.768 |
| Subject 4 | 2.937 | 2.591 |
| Subject 5 | 2.937 | 2.591 |

14D:

| Neural representation | V-JEPA2 ratio | CLIP ratio |
|---|---:|---:|
| Mean | 1.794 | 0.921 |
| Subject 1 | 1.715 | 0.991 |
| Subject 2 | 2.361 | 1.375 |
| Subject 3 | 2.361 | 1.375 |
| Subject 4 | 1.715 | 0.991 |
| Subject 5 | 1.715 | 0.991 |

2D:

| Neural representation | V-JEPA2 ratio | CLIP ratio |
|---|---:|---:|
| Mean | 1.441 | 0.997 |
| Subject 1 | 1.958 | 1.727 |
| Subject 2 | 2.646 | 2.549 |
| Subject 3 | 2.646 | 2.549 |
| Subject 4 | 1.958 | 1.727 |
| Subject 5 | 1.958 | 1.727 |

Agreement with the group-mean orientation:

| Ontology | V-JEPA2 | CLIP |
|---|---:|---:|
| 3D | 5/5 | 5/5 |
| 14D | 5/5 | 3/5 |
| 2D | 5/5 | 0/5 |

Interpretation:

- V-JEPA2 remains stable across subjects in `3D`, `14D`, and `2D`
- CLIP is less stable than V-JEPA2 at the subject level
- CLIP’s `14D` dimension-heavy tendency is only partially stable
- CLIP’s `2D` near-balance is not reproduced at the individual-subject level

## 13. Fully Embedded Detailed Documents

This section embeds the full detailed result records directly into this master file. The goal is that `RESULTS_MASTER_EXP18_0402.md` can be read as a single self-contained archive without having to open separate experiment documents.

### 13.1 Full Record: Experiment 11

Source: [RESULTS_EXP11_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP11_0402.md)

**Date**: 2026-04-02  
**Script**: `11_pc_emotion_correlation.py`  
**기반**: Script 10 Exp 3 결과 (brain-predictable PC 목록)

---

## 왜 했는가

Script 10 (Exp 3)에서 brain이 V-JEPA2의 상위 3개 PC, CLIP의 6개 PC만 decode할 수 있다는 결과가 나왔다.  
이 PC들이 **무엇을 represent하는지** 알아야 paper의 main claim을 결정할 수 있다.

- **시나리오 A**: brain-predictable PC ↔ 감정과 높은 상관 → "Brain selectively reads the affective subspace"
- **시나리오 B**: 일부만 감정 관련 → "Brain-model alignment captures both affective and perceptual dimensions"
- **시나리오 C**: brain-predictable PC ↔ 감정과 무관 → "Brain-model alignment is driven by perceptual structure"

---

## 방법

1. V-JEPA2 (2196, 1408), CLIP (2196, 512) 각각 PCA 100개 PC 추출
2. 각 PC × 34개 감정 score Spearman r 계산 → (100, 34) 행렬
3. Arousal / Valence / Dominance score와도 Spearman r 계산
4. FDR correction (Benjamini-Hochberg, 3400개 test)
5. Script 10의 R²(brain→PC)와 결합 → brain-predictable (R²>0.01) vs unpredictable 비교

---

## 결론: **시나리오 A 확정**

Brain-predictable PC들이 **모두** 감정과 강하게 correlate.  
Brain-pred PC의 mean max|r| = 0.33~0.37 vs unpredictable = 0.09 → **약 3.6~4.5배 차이**

> **"Brain selectively reads the affective subspace of video representations"**

---

## V-JEPA2 결과

### Brain-predictable PCs (R² > 0.01): **PC1, PC2, PC3** (n=3)

---

#### PC1 — R²=0.3728, explained var=17.02%, max|r|=0.3277, FDR-sig emotions=26

| 감정 | Spearman r | FDR q |
|------|-----------|-------|
| Aesthetic appreciation | −0.3277 | 4.77e-53 |
| Annoyance | +0.3253 | 2.21e-52 |
| Calmness | −0.2880 | 1.81e-40 |

AVD: Arousal=+0.1408 (q=3.00e-09), Valence=−0.1259 (q=1.94e-07), Dominance=+0.0422 (q=0.184)

→ **calm/aesthetic(−) ↔ annoying(+)** 축. 뇌가 가장 강하게 decode하는 차원 (R²=0.37).

---

#### PC2 — R²=0.0748, explained var=5.53%, max|r|=0.3544, FDR-sig emotions=24

| 감정 | Spearman r | FDR q |
|------|-----------|-------|
| Aesthetic appreciation | +0.3544 | 1.89e-62 |
| Excitement | +0.3276 | 4.77e-53 |
| Adoration | −0.2791 | 6.62e-38 |

AVD: Arousal=+0.2254 (q=3.19e-24), Valence=−0.0823 (q=2.43e-03), Dominance=−0.0234 (q=0.524)

→ **aesthetic/exciting(+) ↔ adoration(−)** 축.

---

#### PC3 — R²=0.0878, explained var=5.07%, max|r|=0.3034, FDR-sig emotions=25

| 감정 | Spearman r | FDR q |
|------|-----------|-------|
| Uncomfortable | −0.3034 | 3.85e-45 |
| Empathic pain | −0.2384 | 2.67e-27 |
| Guilt | +0.2369 | 5.70e-27 |

AVD: Arousal=+0.0297 (q=0.399), Valence=+0.0615 (q=0.031), Dominance=+0.0426 (q=0.180)

→ **guilt(+) ↔ uncomfortable/empathic pain(−)** 축.

---

### Brain-pred vs Unpred 비교 (V-JEPA2)

| | n PCs | mean max\|r\| across 34 emotions |
|---|---|---|
| Brain-predictable | 3 | **0.3285** |
| Brain-unpredictable | 97 | 0.0903 |
| Δ | | **+0.2382** |

### Max|r| per emotion: brain-pred vs unpred (V-JEPA2)

| 감정 | pred max\|r\| | unpred max\|r\| |
|------|--------------|----------------|
| Admiration | 0.1330 | 0.0778 |
| Adoration | 0.2791 | 0.2003 |
| Aesthetic appreciation | **0.3544** | 0.1591 |
| Amusement | 0.2626 | 0.2186 |
| Anger | 0.1063 | 0.0900 |
| Anxiety | 0.2034 | 0.1474 |
| Awe | 0.1132 | 0.2167 |
| Awkwardness | 0.1708 | 0.1423 |
| Boredom | 0.1457 | 0.2177 |
| Calmness | **0.2880** | 0.0964 |
| Confusion | 0.0901 | 0.1154 |
| Contempt | 0.0548 | 0.1098 |
| Craving | 0.1640 | 0.1689 |
| Disgust | 0.0999 | 0.0668 |
| Empathic pain | **0.2384** | 0.1067 |
| Entrancement | 0.1213 | 0.1412 |
| Excitement | **0.3276** | 0.1145 |
| Fear | 0.0504 | 0.0775 |
| Horror | 0.1972 | 0.1255 |
| Interest | 0.2098 | 0.1789 |
| Joy | 0.0866 | 0.0667 |
| Nostalgia | 0.1415 | 0.1520 |
| Relief | 0.2544 | 0.1170 |
| Romance | 0.2409 | 0.1471 |
| Sadness | 0.0722 | 0.1867 |
| Satisfaction | 0.0963 | 0.1203 |
| Sexual desire | 0.1436 | 0.0972 |
| Surprise | 0.1921 | 0.1586 |
| Sympathy | 0.0943 | 0.1645 |
| Triumph | 0.0831 | 0.1054 |
| Uncomfortable | **0.3034** | 0.1787 |
| Annoyance | **0.3253** | 0.1506 |
| Envy | 0.1759 | 0.1236 |
| Guilt | **0.2369** | 0.0812 |

---

## CLIP 결과

### Brain-predictable PCs (R² > 0.01): **PC1, PC2, PC3, PC5, PC6, PC7** (n=6)

---

#### PC1 — R²=0.2613, explained var=8.27%, max|r|=0.4512, FDR-sig emotions=28

| 감정 | Spearman r | FDR q |
|------|-----------|-------|
| Annoyance | −0.4512 | 2.35e-107 |
| Uncomfortable | +0.4162 | 8.51e-90 |
| Surprise | +0.3637 | 5.90e-67 |

AVD: Arousal=−0.1337 (q=8.71e-09), Valence=+0.1983 (q=3.86e-19), Dominance=+0.0293 (q=0.376)

---

#### PC2 — R²=0.1559, explained var=6.26%, max|r|=0.4726, FDR-sig emotions=18

| 감정 | Spearman r | FDR q |
|------|-----------|-------|
| Aesthetic appreciation | −0.4726 | 4.70e-119 |
| Excitement | −0.4029 | 9.71e-84 |
| Uncomfortable | +0.3613 | 4.59e-66 |

AVD: Arousal=−0.1213 (q=2.51e-07), Valence=+0.0905 (q=4.06e-04), Dominance=+0.0967 (q=1.14e-04)

→ 전체 데이터에서 가장 강한 단일 상관. **aesthetic/exciting(−) ↔ uncomfortable(+)** 축.

---

#### PC3 — R²=0.1271, explained var=5.17%, max|r|=0.2269, FDR-sig emotions=24

| 감정 | Spearman r | FDR q |
|------|-----------|-------|
| Guilt | −0.2269 | 3.59e-25 |
| Awe | +0.2142 | 2.14e-22 |
| Horror | −0.2088 | 2.86e-21 |

AVD: Arousal=+0.0237 (q=0.481), Valence=+0.1238 (q=1.46e-07), Dominance=−0.0755 (q=4.94e-03)

---

#### PC4 — R²=0.0000 (brain-unpredictable, 참고용)

AVD: Arousal=+0.1777 (q=...), Valence=−0.2059 (q=...) → A/V와는 correlate하지만 brain이 decode 못함

---

#### PC5 — R²=0.1154, explained var=3.47%, max|r|=0.3497, FDR-sig emotions=20

| 감정 | Spearman r | FDR q |
|------|-----------|-------|
| Uncomfortable | +0.3497 | 1.17e-61 |
| Sadness | −0.2740 | 5.65e-37 |
| Horror | +0.2724 | 1.57e-36 |

AVD: Arousal=+0.1777 (q=1.65e-15), Valence=+0.0577 (q=4.44e-02), Dominance=+0.0454 (q=0.132)

---

#### PC6 — R²=0.0167, explained var=2.93%, max|r|=0.3131, FDR-sig emotions=29

| 감정 | Spearman r | FDR q |
|------|-----------|-------|
| Nostalgia | +0.3131 | 9.42e-49 |
| Interest | +0.3107 | 4.89e-48 |
| Sympathy | +0.2923 | 3.02e-42 |

AVD: Arousal=−0.0132 (q=0.720), Valence=−0.2768 (q=9.97e-38), Dominance=−0.1779 (q=1.65e-15)

---

#### PC7 — R²=0.0125, explained var=2.45%, max|r|=0.4029, FDR-sig emotions=27

| 감정 | Spearman r | FDR q |
|------|-----------|-------|
| Empathic pain | +0.4029 | 9.71e-84 |
| Amusement | −0.2917 | 4.49e-42 |
| Romance | −0.2856 | 2.75e-40 |

AVD: Arousal=−0.0655 (q=1.84e-02), Valence=−0.3169 (q=6.12e-50), Dominance=−0.0641 (q=2.14e-02)

---

### Brain-pred vs Unpred 비교 (CLIP)

| | n PCs | mean max\|r\| across 34 emotions |
|---|---|---|
| Brain-predictable | 6 | **0.3694** |
| Brain-unpredictable | 94 | 0.0818 |
| Δ | | **+0.2877** |

### Max|r| per emotion: brain-pred vs unpred (CLIP)

| 감정 | pred max\|r\| | unpred max\|r\| |
|------|--------------|----------------|
| Admiration | 0.1477 | 0.1331 |
| Adoration | 0.2868 | **0.4484** |
| Aesthetic appreciation | **0.4726** | 0.1678 |
| Amusement | 0.2993 | 0.1546 |
| Anger | 0.2224 | 0.0820 |
| Anxiety | 0.3445 | 0.1583 |
| Awe | 0.2670 | 0.2186 |
| Awkwardness | 0.2624 | 0.1435 |
| Boredom | 0.2426 | 0.1159 |
| Calmness | 0.2437 | 0.1968 |
| Confusion | 0.1684 | 0.1848 |
| Contempt | 0.1344 | 0.0721 |
| Craving | 0.2723 | 0.1942 |
| Disgust | 0.2014 | 0.0643 |
| Empathic pain | **0.4029** | 0.2546 |
| Entrancement | 0.2180 | 0.1050 |
| Excitement | **0.4029** | 0.1626 |
| Fear | 0.1790 | 0.0787 |
| Horror | 0.2724 | 0.1356 |
| Interest | 0.3473 | 0.1371 |
| Joy | 0.1126 | 0.0770 |
| Nostalgia | 0.3131 | 0.1666 |
| Relief | 0.3108 | 0.1279 |
| Romance | 0.2856 | **0.3524** |
| Sadness | 0.2740 | 0.1513 |
| Satisfaction | 0.2037 | 0.0979 |
| Sexual desire | 0.2632 | 0.0926 |
| Surprise | **0.3637** | 0.1321 |
| Sympathy | 0.2923 | 0.1099 |
| Triumph | 0.2037 | 0.1226 |
| Uncomfortable | **0.4162** | 0.1566 |
| Annoyance | **0.4512** | 0.1332 |
| Envy | 0.2850 | 0.1054 |
| Guilt | 0.2269 | 0.0954 |

※ Adoration, Romance는 unpred PC에서 오히려 높음 (0.45, 0.35) — 예외적 감정

---

## 반복 등장 감정 (V-JEPA2 + CLIP brain-pred PCs 공통)

| 감정 | V-JEPA2 pred max\|r\| | CLIP pred max\|r\| | 해석 |
|------|----------------------|-------------------|------|
| Aesthetic appreciation | **0.3544** | **0.4726** | 두 모델 모두 가장 강한 상관 |
| Annoyance | **0.3253** | **0.4512** | 두 모델 모두 top |
| Uncomfortable | **0.3034** | **0.4162** | 두 모델 모두 top |
| Excitement | 0.3276 | 0.4029 | 두 모델 모두 높음 |
| Empathic pain | 0.2384 | 0.4029 | 공통 |
| Calmness | 0.2880 | 0.2437 | 공통 |
| Guilt | 0.2369 | 0.2269 | 공통 |

→ 두 모델(V-JEPA2, CLIP)이 공유하는 감정 구조를 뇌가 선택적으로 decode.

---

## 생성된 Figure

| 파일 | 내용 |
|------|------|
| `figures/pc_emotion_heatmap.png` | 상위 20 PC × 34 emotion Spearman r heatmap (*=brain-pred, ·=FDR-sig) |
| `figures/pc_brain_pred_emotion.png` | Brain-pred vs unpred PC의 max\|r\| bar chart (34 emotions) |
| `figures/pc_r2_vs_emotion_scatter.png` | R²(brain) vs max emotion\|r\| scatter (점 크기=설명분산) |
| `figures/pc_avd_heatmap.png` | 상위 20 PC × Arousal/Valence/Dominance heatmap (수치 표기) |

---

## CCN Claim 확정

### Main Claim

> **"Brain selectively reads the affective subspace of video representations"**

- V-JEPA2 1408차원 중 brain이 decode하는 3개 PC: 전부 감정과 강하게 correlate  
  (FDR-sig 24~26개 감정, mean max|r|=0.33 vs unpred 0.09, Δ=+0.24)
- CLIP 512차원 중 brain이 decode하는 6개 PC: 모두 감정과 강하게 correlate  
  (FDR-sig 18~29개 감정, mean max|r|=0.37 vs unpred 0.08, Δ=+0.29)

### 전체 스토리라인 (Script 10 + 11)

1. Brain은 video model 고차원 표상(1408-dim, 512-dim)의 **극히 일부**만 표상 (3~6개 PC)
2. 이 소수 차원들은 **감정 구조와 강하게 aligned** — affective subspace
3. Brain이 decode하지 못하는 나머지 94~97개 차원의 감정 상관은 낮음 (mean max|r|≈0.09)
4. CKA(brain, model)이 k≈27에서 포화 → affective subspace를 포착하는 데 ~27차원이면 충분
5. Aesthetic appreciation, Annoyance, Uncomfortable이 두 모델 모두에서 반복 등장  
   → 뇌가 읽는 것은 모델 특이적이 아닌, **video representation의 공통 affective structure**

### 주의: AVD와의 관계

- A/V/D 상관은 전반적으로 낮음 (|r| < 0.32)
- brain이 decode하는 PC가 단순 arousal/valence 축이 아님
- **고차원 감정 카테고리 (Aesthetic, Annoying, Uncomfortable, Empathic pain 등)**를 반영

---

## 저장 파일

```
results/pc_emotion_correlation.npz
  corr_vjepa_emo        (100, 34) — V-JEPA2 PC × emotion Spearman r
  pval_vjepa_emo        (100, 34) — raw p-values
  pval_vjepa_emo_fdr    (100, 34) — BH FDR q-values
  corr_clip_emo         (100, 34)
  pval_clip_emo         (100, 34)
  pval_clip_emo_fdr     (100, 34)
  corr_vjepa_avd        (100, 3)  — PC × Arousal/Valence/Dominance
  pval_vjepa_avd_fdr    (100, 3)
  corr_clip_avd         (100, 3)
  pval_clip_avd_fdr     (100, 3)
  emotion_labels        (34,)
  avd_labels            (3,)
  r2_vjepa              (100,)    — from Script 10 Exp 3
  r2_clip               (100,)
  brain_pred_mask_vjepa (100,)    — R² > 0.01 (int8)
  brain_pred_mask_clip  (100,)
  vjepa_var_ratio       (100,)    — PCA explained variance ratio
  clip_var_ratio        (100,)
```

### 13.2 Full Record: Experiment 12 (3D)

Source: [RESULTS_EXP12_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP12_0402.md)

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

### 13.3 Full Record: Experiment 13 (3D)

Source: [RESULTS_EXP13_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP13_0402.md)

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

### 13.4 Full Record: Experiment 15

Source: [RESULTS_EXP15_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP15_0402.md)

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

### 13.5 Full Record: Experiment 16 (3D)

Source: [RESULTS_EXP16_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP16_0402.md)

Date: 0402  
Source file: `results/exp16_incremental_baseline_results.npz`  
Figures:
- `figures/exp16_incremental_benchmark.png`
- `figures/exp16_incremental_scatter.png`

## Goal

Experiment 16 tested a reviewer-facing question directly:

> If vision and semantic features are already available, do brain-predictable video-model PCs still add anything?

To answer this, five models were compared:

1. `Vision + Semantic`
2. `V-JEPA2 brain-predictable PCs only`
3. `CLIP brain-predictable PCs only`
4. `Vision + Semantic + V-JEPA2 PCs`
5. `Vision + Semantic + CLIP PCs`

The key quantity was incremental `R^2`:

- `Delta_vjepa = R^2(baseline + V-JEPA2 PCs) - R^2(baseline)`
- `Delta_clip = R^2(baseline + CLIP PCs) - R^2(baseline)`

## Main Takeaways

### Overall summary

- The `Vision + Semantic` baseline already predicts a meaningful portion of variance.
- Adding brain-predictable V-JEPA2 PCs gives a small positive gain overall:
  - mean category gain `= +0.0022`
  - mean A/V/D gain `= +0.0001`
- Adding brain-predictable CLIP PCs gives a clearer gain:
  - mean category gain `= +0.0065`
  - mean A/V/D gain `= +0.0079`

### What this means

- The answer is not "vision+semantic is enough."
- Brain-predictable model PCs do add information beyond explicit vision/semantic features.
- But the extra contribution is modest, not huge.
- CLIP adds more incremental variance than V-JEPA2 under this benchmark.

This makes Exp 16 a useful supplementary control:

- it defends the use of model PCs,
- but it also shows that much of the explainable structure is already shared with explicit vision/semantic features.

## Brain-Predictable PC Counts

Using the same threshold as Exp 12 (`R^2 > 0.01`):

- V-JEPA2 selected PCs: `1, 2, 3` (`n = 3`)
- CLIP selected PCs: `1, 2, 3, 5, 6, 7` (`n = 6`)

## Summary of Model Families

| Model | Mean category `R^2` | Mean A/V/D `R^2` | Category/dimension ratio |
|---|---:|---:|---:|
| Vision + Semantic baseline | 0.0796 | 0.0991 | 0.8027 |
| V-JEPA2 PCs only | 0.0550 | 0.0254 | 2.1615 |
| CLIP PCs only | 0.1659 | 0.1297 | 1.2785 |
| Baseline + V-JEPA2 PCs | 0.0818 | 0.0993 | 0.8238 |
| Baseline + CLIP PCs | 0.0861 | 0.1071 | 0.8042 |

## Incremental Gain Over Baseline

| Added feature set | Mean category delta `R^2` | Mean A/V/D delta `R^2` |
|---|---:|---:|
| V-JEPA2 PCs | +0.0022 | +0.0001 |
| CLIP PCs | +0.0065 | +0.0079 |

## Top Incremental Emotions

### Baseline + V-JEPA2 PCs vs Baseline

| Rank | Emotion | Baseline `R^2` | Combined `R^2` | Delta |
|---:|---|---:|---:|---:|
| 1 | Aesthetic appreciation | 0.3549 | 0.3936 | +0.0387 |
| 2 | Excitement | 0.0907 | 0.1049 | +0.0141 |
| 3 | Adoration | 0.1427 | 0.1546 | +0.0118 |
| 4 | Amusement | 0.0114 | 0.0178 | +0.0063 |
| 5 | Interest | 0.0632 | 0.0691 | +0.0059 |
| 6 | Craving | 0.3873 | 0.3911 | +0.0038 |
| 7 | Uncomfortable | 0.6769 | 0.6773 | +0.0004 |
| 8 | Calmness | 0.0000 | 0.0000 | +0.0000 |
| 9 | Contempt | 0.0000 | 0.0000 | +0.0000 |
| 10 | Confusion | 0.0000 | 0.0000 | +0.0000 |

### Baseline + CLIP PCs vs Baseline

| Rank | Emotion | Baseline `R^2` | Combined `R^2` | Delta |
|---:|---|---:|---:|---:|
| 1 | Aesthetic appreciation | 0.3549 | 0.4115 | +0.0567 |
| 2 | Amusement | 0.0114 | 0.0654 | +0.0540 |
| 3 | Excitement | 0.0907 | 0.1165 | +0.0258 |
| 4 | Valence | 0.2974 | 0.3212 | +0.0238 |
| 5 | Interest | 0.0632 | 0.0850 | +0.0218 |
| 6 | Surprise | 0.4791 | 0.4976 | +0.0185 |
| 7 | Empathic pain | 0.2008 | 0.2176 | +0.0168 |
| 8 | Sadness | 0.0000 | 0.0166 | +0.0166 |
| 9 | Adoration | 0.1427 | 0.1518 | +0.0090 |
| 10 | Uncomfortable | 0.6769 | 0.6796 | +0.0027 |

## Full Target-Wise Results

Columns:

- `Baseline`: Vision + Semantic
- `V-JEPA2 only`: brain-predictable V-JEPA2 PCs only
- `CLIP only`: brain-predictable CLIP PCs only
- `Base+VJ`: Vision + Semantic + V-JEPA2 PCs
- `Base+CLIP`: Vision + Semantic + CLIP PCs
- `Delta VJ`: `Base+VJ - Baseline`
- `Delta CLIP`: `Base+CLIP - Baseline`

| Target | Baseline | V-JEPA2 only | CLIP only | Base+VJ | Base+CLIP | Delta VJ | Delta CLIP |
|---|---:|---:|---:|---:|---:|---:|---:|
| Admiration | 0.0000 | 0.0235 | 0.0266 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Adoration | 0.1427 | 0.0805 | 0.1424 | 0.1546 | 0.1518 | +0.0118 | +0.0090 |
| Aesthetic appreciation | 0.3549 | 0.3231 | 0.4473 | 0.3936 | 0.4115 | +0.0387 | +0.0567 |
| Amusement | 0.0114 | 0.1159 | 0.3397 | 0.0178 | 0.0654 | +0.0063 | +0.0540 |
| Anger | 0.0000 | 0.0118 | 0.1818 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Anxiety | 0.0000 | 0.0611 | 0.2036 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Awe | 0.0000 | 0.0222 | 0.2096 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Awkwardness | 0.0000 | 0.0308 | 0.0913 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Boredom | 0.0000 | 0.0196 | 0.1011 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Calmness | 0.0000 | 0.1361 | 0.1655 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Confusion | 0.0000 | 0.0000 | 0.0291 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Contempt | 0.0000 | 0.0000 | 0.0493 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Craving | 0.3873 | 0.0166 | 0.1482 | 0.3911 | 0.3881 | +0.0038 | +0.0008 |
| Disgust | 0.0000 | 0.0088 | 0.0847 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Empathic pain | 0.2008 | 0.0741 | 0.1964 | 0.2000 | 0.2176 | -0.0008 | +0.0168 |
| Entrancement | 0.0000 | 0.0024 | 0.0564 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Excitement | 0.0907 | 0.2001 | 0.2866 | 0.1049 | 0.1165 | +0.0141 | +0.0258 |
| Fear | 0.0000 | 0.0000 | 0.0385 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Horror | 0.0000 | 0.0570 | 0.1709 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Interest | 0.0632 | 0.0598 | 0.2536 | 0.0691 | 0.0850 | +0.0059 | +0.0218 |
| Joy | 0.0000 | 0.0028 | 0.0289 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Nostalgia | 0.2984 | 0.0167 | 0.2100 | 0.2951 | 0.2976 | -0.0033 | -0.0007 |
| Relief | 0.0000 | 0.0576 | 0.1818 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Romance | 0.0000 | 0.0793 | 0.1236 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Sadness | 0.0000 | 0.0094 | 0.1922 | 0.0000 | 0.0166 | +0.0000 | +0.0166 |
| Satisfaction | 0.0000 | 0.0071 | 0.0544 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Sexual desire | 0.0000 | 0.0313 | 0.1058 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Surprise | 0.4791 | 0.0450 | 0.3308 | 0.4776 | 0.4976 | -0.0015 | +0.0185 |
| Sympathy | 0.0000 | 0.0059 | 0.1959 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Triumph | 0.0000 | 0.0128 | 0.0436 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Uncomfortable | 0.6769 | 0.1715 | 0.5379 | 0.6773 | 0.6796 | +0.0004 | +0.0027 |
| Annoyance | 0.0000 | 0.1057 | 0.1882 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Envy | 0.0000 | 0.0293 | 0.1030 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Guilt | 0.0000 | 0.0518 | 0.1211 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Arousal | 0.0000 | 0.0651 | 0.0621 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Valence | 0.2974 | 0.0112 | 0.2706 | 0.2979 | 0.3212 | +0.0004 | +0.0238 |
| Dominance | 0.0000 | 0.0000 | 0.0565 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |

## Interpretation

The cleanest reading of Exp 16 is:

1. Explicit vision and semantic features already explain a substantial amount of affective variance.
2. Brain-predictable model PCs are not redundant, because they still improve prediction beyond that baseline.
3. The incremental contribution is larger for CLIP than for V-JEPA2 in this setting.
4. The added value is selective rather than uniform, with the clearest gains for:
   - Aesthetic appreciation
   - Amusement
   - Excitement
   - Interest
   - Valence

So Exp 16 supports a moderate claim, not an extreme one:

- model PCs do contain information that is not fully recoverable from simple vision+semantic features,
- but much of the total explainable structure is still shared with those explicit features.

### 13.6 Full Record: Experiment 12 (14D)

Source: [RESULTS_EXP12_14D_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP12_14D_0402.md)

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

### 13.7 Full Record: Experiment 13 (14D)

Source: [RESULTS_EXP13_14D_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP13_14D_0402.md)

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

### 13.8 Full Record: Experiment 16 (14D)

Source: [RESULTS_EXP16_14D_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP16_14D_0402.md)

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

### 13.9 Full Record: Experiment 12 Raw fMRI (14D)

Source: [RESULTS_EXP12_RAW_14D_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP12_RAW_14D_0402.md)

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

### 13.10 Full Record: Experiment 17 (A/V 2D)

Source: [RESULTS_EXP17_AV2D_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP17_AV2D_0402.md)

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

### 13.11 Full Record: Experiment 18 (Subject-wise)

Source: [RESULTS_EXP18_0402.md](/pscratch/sd/s/sjmoon/EmoFM/CCN/RESULTS_EXP18_0402.md)

Date: 0402  
Script: [18_subjectwise_claim_check.py](/pscratch/sd/s/sjmoon/EmoFM/CCN/18_subjectwise_claim_check.py)  
Result file: [exp18_subjectwise_claim_check.npz](/pscratch/sd/s/sjmoon/EmoFM/CCN/results/exp18_subjectwise_claim_check.npz)

## 1. What This Experiment Tested

The goal of Exp 18 was simple:

- define brain-predictable video-model PCs separately for the group-mean Brain-JEPA representation and for each of the 5 individual subjects
- re-run the Exp 12 style category-vs-dimension comparison at the subject level
- check whether the core group-level claim is preserved per subject

The experiment covered three target ontologies:

- `3D`: 34 emotions + `Arousal`, `Valence`, `Dominance`
- `14D`: 34 emotions + 14 affective dimensions
- `2D`: 34 emotions + `Arousal`, `Valence`

## 2. Brain-predictable PC Counts

The group-mean representation produced a larger readable subspace than any individual subject.

| Neural representation | V-JEPA2 predictable PCs | CLIP predictable PCs |
|---|---:|---:|
| Mean | 3 | 6 |
| Subject 1 | 1 | 1 |
| Subject 2 | 2 | 2 |
| Subject 3 | 2 | 2 |
| Subject 4 | 1 | 1 |
| Subject 5 | 1 | 1 |

Predictable PC identities:

- V-JEPA2 mean: `PC1, PC2, PC3`
- V-JEPA2 subjects:
  - Subject 1: `PC1`
  - Subject 2: `PC1, PC3`
  - Subject 3: `PC1, PC3`
  - Subject 4: `PC1`
  - Subject 5: `PC1`
- CLIP mean: `PC1, PC2, PC3, PC5, PC6, PC7`
- CLIP subjects:
  - Subject 1: `PC1`
  - Subject 2: `PC1, PC2`
  - Subject 3: `PC1, PC2`
  - Subject 4: `PC1`
  - Subject 5: `PC1`

Interpretation:

- the group-mean Brain-JEPA representation exposes a larger brain-predictable subspace than any single subject
- the most stable core remains very small
- `PC1` is the dominant shared readable axis for both V-JEPA2 and CLIP

## 3. Subject-wise Category-vs-Dimension Balance

### 3.1 3D Targets: 34 Emotions + A/V/D

#### V-JEPA2

| Neural representation | Mean category `R²` | Mean A/V/D `R²` | Ratio |
|---|---:|---:|---:|
| Mean | 0.0550 | 0.0254 | 2.162 |
| Subject 1 | 0.0197 | 0.0067 | 2.937 |
| Subject 2 | 0.0328 | 0.0083 | 3.969 |
| Subject 3 | 0.0328 | 0.0083 | 3.969 |
| Subject 4 | 0.0197 | 0.0067 | 2.937 |
| Subject 5 | 0.0197 | 0.0067 | 2.937 |

#### CLIP

| Neural representation | Mean category `R²` | Mean A/V/D `R²` | Ratio |
|---|---:|---:|---:|
| Mean | 0.1659 | 0.1297 | 1.279 |
| Subject 1 | 0.0391 | 0.0151 | 2.591 |
| Subject 2 | 0.0775 | 0.0206 | 3.768 |
| Subject 3 | 0.0775 | 0.0206 | 3.768 |
| Subject 4 | 0.0391 | 0.0151 | 2.591 |
| Subject 5 | 0.0391 | 0.0151 | 2.591 |

Agreement with the group-mean claim:

- V-JEPA2: `5/5` subjects matched the mean-level `category > dimension` orientation
- CLIP: `5/5` subjects matched the mean-level `category > dimension` orientation

Interpretation:

- the 3D result is highly stable at the subject level
- if the ontology is restricted to A/V/D, both models remain category-leaning in every subject

### 3.2 14D Targets: 34 Emotions + 14 Dimensions

#### V-JEPA2

| Neural representation | Mean category `R²` | Mean 14D `R²` | Ratio |
|---|---:|---:|---:|
| Mean | 0.0550 | 0.0306 | 1.794 |
| Subject 1 | 0.0197 | 0.0115 | 1.715 |
| Subject 2 | 0.0328 | 0.0139 | 2.361 |
| Subject 3 | 0.0328 | 0.0139 | 2.361 |
| Subject 4 | 0.0197 | 0.0115 | 1.715 |
| Subject 5 | 0.0197 | 0.0115 | 1.715 |

#### CLIP

| Neural representation | Mean category `R²` | Mean 14D `R²` | Ratio |
|---|---:|---:|---:|
| Mean | 0.1659 | 0.1802 | 0.921 |
| Subject 1 | 0.0391 | 0.0395 | 0.991 |
| Subject 2 | 0.0775 | 0.0563 | 1.375 |
| Subject 3 | 0.0775 | 0.0563 | 1.375 |
| Subject 4 | 0.0391 | 0.0395 | 0.991 |
| Subject 5 | 0.0391 | 0.0395 | 0.991 |

Agreement with the group-mean claim:

- V-JEPA2: `5/5` subjects matched the mean-level `category > dimension` orientation
- CLIP: `3/5` subjects matched the mean-level `dimension >= category` orientation

Interpretation:

- V-JEPA2 remains robustly category-leaning even at the subject level in the richer 14D target space
- CLIP is less stable than V-JEPA2 in 14D
- the group-level `CLIP -> dimension-heavy` result is present, but not uniformly strong across subjects

### 3.3 2D Targets: 34 Emotions + A/V

#### V-JEPA2

| Neural representation | Mean category `R²` | Mean A/V `R²` | Ratio |
|---|---:|---:|---:|
| Mean | 0.0550 | 0.0382 | 1.441 |
| Subject 1 | 0.0197 | 0.0101 | 1.958 |
| Subject 2 | 0.0328 | 0.0124 | 2.646 |
| Subject 3 | 0.0328 | 0.0124 | 2.646 |
| Subject 4 | 0.0197 | 0.0101 | 1.958 |
| Subject 5 | 0.0197 | 0.0101 | 1.958 |

#### CLIP

| Neural representation | Mean category `R²` | Mean A/V `R²` | Ratio |
|---|---:|---:|---:|
| Mean | 0.1659 | 0.1664 | 0.997 |
| Subject 1 | 0.0391 | 0.0227 | 1.727 |
| Subject 2 | 0.0775 | 0.0304 | 2.549 |
| Subject 3 | 0.0775 | 0.0304 | 2.549 |
| Subject 4 | 0.0391 | 0.0227 | 1.727 |
| Subject 5 | 0.0391 | 0.0227 | 1.727 |

Agreement with the group-mean claim:

- V-JEPA2: `5/5` subjects matched the mean-level `category > dimension` orientation
- CLIP: `0/5` subjects matched the mean-level near-balanced / dimension-leaning orientation

Interpretation:

- V-JEPA2 is again stable
- CLIP’s mean-level near-balance in 2D is not reproduced at the individual-subject level
- the CLIP 2D result appears to be more dependent on subject averaging than the V-JEPA2 result

## 4. Main Takeaways

The most important result of Exp 18 is that the group-level story is not uniformly fragile, but it is not uniformly equally stable either.

What looks robust:

- V-JEPA2 remains category-leaning in `3D`, `14D`, and `2D` for all 5 subjects
- the readable subspace remains very small at both group and subject levels
- `PC1` is the dominant shared readable axis

What now needs more caution:

- CLIP’s `14D` dimension-heavy tendency is only partially stable at the subject level
- CLIP’s `2D` near-balanced result is not reproduced in any single subject
- the CLIP mean-level result should therefore be framed as a group-level tendency rather than a uniformly subject-level effect

## 5. Implication for the Main Claim

Exp 18 strengthens the following claim:

> The readable part of video-model space is very small, and V-JEPA2’s readable subspace is consistently category-leaning across subjects and target ontologies.

Exp 18 weakens or at least qualifies the following stronger claim:

> CLIP is uniformly dimension-heavy or uniformly balanced at the individual-subject level.

So after Exp 18, the safest interpretation is:

- V-JEPA2 shows stable subject-level category dominance
- CLIP shows a stronger dependence on group averaging, especially in `2D` and partly in `14D`
- therefore, the category-vs-dimension balance is representation-dependent and aggregation-dependent

## 6. Output Files

- Result array: [exp18_subjectwise_claim_check.npz](/pscratch/sd/s/sjmoon/EmoFM/CCN/results/exp18_subjectwise_claim_check.npz)
- Ratio figure: [exp18_subjectwise_ratios.png](/pscratch/sd/s/sjmoon/EmoFM/CCN/figures/exp18_subjectwise_ratios.png)
- PC-count figure: [exp18_subjectwise_pc_counts.png](/pscratch/sd/s/sjmoon/EmoFM/CCN/figures/exp18_subjectwise_pc_counts.png)
