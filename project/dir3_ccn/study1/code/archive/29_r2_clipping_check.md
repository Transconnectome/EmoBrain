# Exp 29 — R² clipping artifact check

**Purpose**: Test whether the original brain-predictable PC definition (PC1/PC2/PC3 survive FDR) is robust to two methodological choices that may inflate false positives.

## Issue

The original permutation test (`19_permutation_test.py`, `23_reverse_pca_ridge.py`) applies:
1. `r2 = max(cv_r2, 0)` to both observed and null R²
2. `KFold(shuffle=False)` (sequential 5-fold)

**Concern 1 — clipping**: when observed R² is small (e.g. PC2=0.075, PC3=0.088), clipped null distributions pile mass at zero. Any null run that gave a negative R² (model worse than mean baseline) becomes zero, making `null >= obs` artificially likely. This inflates p-values toward 1, but the FDR direction depends on the relative behavior of clipped null vs clipped observed.

**Concern 2 — CV split**: sequential KFold without shuffling can leak if the Horikawa stimulus ordering is correlated with emotion category or any other structure.

## Inputs

- `/pscratch/sd/s/sjmoon/FEELIN/project/dir3_ccn/data/raw/brain_embeddings/brain_jepa_embeddings.npy` shape (5, 2196, 768)
- `/pscratch/sd/s/sjmoon/FEELIN/project/dir3_ccn/data/raw/video_embeddings/vjepa2_embeddings.npy` shape (2196, 1408)

## Pipeline

1. PCA of V-JEPA2 → 100 PCs (variance-based, seed 42).
2. For each PC (top 20 by raw R²), Brain-JEPA group-mean → ridge regression (alpha=1.0).
3. Compute observed R² in 4 variants: {raw, clipped} × {sequential, shuffled} CV.
4. Permutation test n=1000 in the same 4 variants. Permute target across stimuli.
5. FDR (Benjamini-Hochberg) over 100 PCs.

## Outputs

- `study1/data/exp29_r2_clipping_check.npz` with per-PC R², p-values (raw and clipped), FDR-corrected q-values, and null distributions.
- Console output: which PCs survive FDR under each variant.

## Interpretation rules

| Outcome | Implication for paper claim |
|---|---|
| All 4 variants agree on PC1/PC2/PC3 surviving | Claim robust. No change needed. |
| Clipped survives 3 PCs, raw survives only PC1 | "3-PC subspace" framing is a clipping artifact. Camera-ready must shift to "PC1-dominant subspace" + note that PC2/PC3 do not survive without clipping. |
| Sequential survives more PCs than shuffled | Possible CV leakage. Need to investigate stimulus ordering. |
| All variants survive only PC1 | Single-axis story. Major framing change required. |

## Runtime estimate

- 1000 permutations × 20 PCs × 4 variants × ~0.5 s per CV = ~3-4 hours wall time on 32 CPUs.
- Set wall time to 2 hours and parallelize over CV variants if needed.

## Status

- 2026-05-26: script + SLURM written. Awaiting user sbatch.
