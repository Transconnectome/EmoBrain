# Affective Characterization

**Role**: Characterize video-model dimensions with continuous fine-grained emotion profiles and broad affective dimensions.

## What it does

For each model PC (1..100), measure how well it predicts emotion via:

### Continuous regression
Targets: 34 emotion category scores + arousal + valence (= 36 targets)
Metrics per (PC, target):
- R² (raw, can be negative)
- R² (max-clipped at 0)
- Pearson r on CV predictions
- Spearman r on CV predictions
- MAE
- RMSE
- Explained variance score

### Categorical decoding
Target: per-stimulus top-rated category (filtered to ≥10 samples per class)
Metrics per PC:
- Top-1 accuracy
- Top-5 accuracy
- ROC-AUC (One-vs-Rest, macro)
- ROC-AUC (One-vs-One, macro)
- Macro F1
- Weighted F1
- Cohen's kappa
- Matthews correlation coefficient

## Inputs

- `data/raw/video_embeddings/emovis_{model}.npy` (2185, *)
- `data/raw/feature/categcontinuous.mat` for the continuous 34D emotion profile
- `data/raw/feature/dimension.mat` for arousal and valence

## Usage

```bash
sbatch run_affective_characterization.sh vjepa2_pretrained
sbatch run_affective_characterization.sh clip_pretrained
sbatch run_affective_characterization.sh dinov2_pretrained
sbatch run_affective_characterization.sh videomae_pretrained
# Pillar 3 baselines:
sbatch run_affective_characterization.sh vjepa2_scratch
sbatch run_affective_characterization.sh clip_scratch
```

## Output

`study1/data/affective_characterization/affective_characterization_{model}.npz` with:
- `cont_*` — 7 continuous metrics × 100 PCs × 36 targets
- `cat_*` — 8 categorical metrics × 100 PCs
- `cat_mean_r2`, `av_mean_r2` — per-PC mean R² for emotion categories vs arousal-valence
- `pcs` — the 100 PCs themselves

## Interpretation

For each PC, multiple measures of "how much emotion info is in this PC."
Top emotion-encoding PCs by `top1_acc` or `auc_ovr_macro` define the **emotion-encoding subspace (M2)**.

Compare these profiles with the shared-alignment output for descriptive screening. The active cortical-transformation module performs its own leakage-controlled shared-space analysis.

## Expected pattern from EmoBrain

EmoBrain linear probe results (stim_level, pretrained):
- CLIP: Cat34 top-1 bal_acc = 0.383, V-reg Pearson r = 0.683
- V-JEPA2: Cat34 top-1 bal_acc = 0.293, V-reg Pearson r = 0.470

So **CLIP M2 should be stronger than V-JEPA2 M2 overall**. The question is which specific PCs carry the emotion encoding for each model.

## Runtime

~1-2 hours on 32 CPUs.

## Status

2026-05-28: refactored generic, awaiting sbatch.
