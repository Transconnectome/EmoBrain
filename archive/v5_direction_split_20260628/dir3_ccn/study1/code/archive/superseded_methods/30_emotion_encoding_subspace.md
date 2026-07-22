# Exp 30 — Emotion-encoding subspace of V-JEPA2 (M2)

**Role in framework**: This is M2 of the M1/M2/M3 framework. Identifies which V-JEPA2 PCs encode emotion information, independently of brain.

## Purpose

The accepted CCN abstract showed that V-JEPA2 has a brain-aligned subspace (M1, 3 PCs survive). It did NOT measure which V-JEPA2 PCs encode emotion. Without M2, the abstract's "affective subspace" naming is unsupported (Leap 1).

This script provides M2 so M3 (overlap) can be computed.

## Inputs

- `data/raw/video_embeddings/vjepa2_embeddings.npy` shape (2196, 1408)
- `horikawa_meta_data_with_dimension_binary.csv` providing per-stimulus 34 category scores + arousal + valence
- No brain data needed — this is model-only analysis

## Pipeline

1. PCA of V-JEPA2 to 100 PCs (variance-based, seed 42).
2. For each PC, two kinds of measurement:

### Continuous regression (matches abstract metric)
- Per PC × per target: ridge regression with 5-fold shuffled CV
- 36 targets: 34 emotion categories + arousal + valence
- Metric: R² (max-clipped to 0 for consistency), Pearson r on CV predictions

### Categorical decoding (Bao/Conwell-style)
- Per PC: multinomial logistic regression with stratified 5-fold CV
- Target: per-stimulus top-rated category (argmax of 34 category scores)
- Filter: only categories with ≥10 samples included
- Metrics: top-1 accuracy, top-5 accuracy, ROC-AUC (one-vs-rest)

## Outputs

`study1/data/exp30_emotion_encoding_subspace.npz` with:
- `r2_cont`: (100, 36) per-PC continuous regression R²
- `pearson_cont`: (100, 36) Pearson r
- `top1_acc`, `top5_acc`, `auc_ovr`: (100,) categorical decoding metrics
- `cat_mean_r2`: (100,) mean R² over 34 categories (for ranking)
- `target_names`: human-readable target labels

## Interpretation

`cat_mean_r2` ranking identifies which PCs are most emotion-relevant. This ranking is then compared with M1 (brain-predictable PCs) in Exp 32 to compute M3 (overlap).

## Runtime estimate

- 100 PCs × (5-fold CV × 36 targets continuous + 5-fold CV categorical multinomial) on 32 CPUs
- ~30-90 min wall time

## Outcome usage

The output goes into Exp 32 (M3 overlap analysis) which compares:
- Top-K PCs by brain alignment (M1, from Exp 19 / Exp 29)
- Top-K PCs by emotion encoding (M2, from this script)

Quantification via Jaccard, Spearman rank correlation, permutation null. The overlap pattern is the central scientific finding of the project.

## Status

- 2026-05-26: script + SLURM written. Awaiting user sbatch.
- Independent of Exp 29 (R² clipping check). Can run in parallel.
- 2026-05-27: bug fix (`multi_class='multinomial'` removed in newer sklearn) + multi-metric collection rule applied. Now collects 7 continuous metrics + 8 categorical metrics per PC. Intermediate save added so categorical-step crash does not lose continuous results.
