# Exp 29 — M1 brain-aligned subspace (generic, all models)

**Role**: M1 of M1/M2/M3 framework. Brain-aligned PC identification, applicable to any video model.

## What it does

For a given video model embedding (V-JEPA2, CLIP, DINOv2, VideoMAE, untrained, supervised):

1. PCA → 100 PCs (variance-based).
2. Ridge regression: Brain-JEPA group-mean → each PC, 5-fold CV.
3. Permutation test (n=1000) on top-20 PCs by raw R².
4. FDR (Benjamini-Hochberg) over 100 PCs.
5. Surviving PCs = brain-aligned subspace.

**Multi-variant**: sequential CV vs shuffled CV, raw null vs clipped null.

**Multi-metric per PC**: R² (raw), R² (clipped), Pearson r on CV predictions, Spearman r.

## Inputs

- `data/raw/video_embeddings/emovis_{model}.npy` (2185, *)
- `data/raw/brain_embeddings/brain_jepa_embeddings.npy` (5, 2196, 768) → sliced to `[:, :2185, :]`

## Models supported

```
vjepa2_pretrained   vjepa2_scratch    (= untrained, Pillar 3 baseline)
clip_pretrained     clip_scratch
dinov2_pretrained   dinov2_scratch
videomae_pretrained videomae_scratch
```

## Usage

```bash
# V-JEPA2 primary
sbatch 29_m1_brain_alignment.sh vjepa2_pretrained

# CLIP primary
sbatch 29_m1_brain_alignment.sh clip_pretrained

# Pillar 3 baselines (architecture comparison)
sbatch 29_m1_brain_alignment.sh vjepa2_scratch
sbatch 29_m1_brain_alignment.sh dinov2_pretrained
sbatch 29_m1_brain_alignment.sh videomae_pretrained
```

## Output

`study1/data/exp29_m1_brain_alignment_{model}.npz` with per-CV-variant:
- `{cv}_r2_raw`, `{cv}_r2_clipped` — observed R²
- `{cv}_pearson_r`, `{cv}_spearman_r`
- `{cv}_p_raw`, `{cv}_p_clip` — permutation p-values
- `{cv}_q_raw`, `{cv}_q_clip` — FDR-corrected q-values
- `{cv}_null_raw_dist`, `{cv}_null_clip_dist` — null distributions

Plus: `pcs` (the 100 PCs themselves), `cumulative_variance`.

## Interpretation

Compare `q_clip` (original method) vs `q_raw` (no artifact):
- If same PCs survive → clipping doesn't matter for this model, original framing OK.
- If different → clipping was an artifact. PCs that only survive under `q_clip` are fragile.

For V-JEPA2: original abstract claims 3 PCs (PC1, PC2, PC3). If `q_raw` gives only PC1, "3-PC subspace" becomes "PC1-only subspace".

For CLIP: unknown. FEELIN data suggests CLIP > V-JEPA2 in emotion encoding, but brain alignment is a separate question.

## Runtime

~2-3 hours on 32 CPUs.

## Status

2026-05-28: written, generic, awaiting sbatch on multiple models.
