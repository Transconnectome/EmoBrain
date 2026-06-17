# generate_figures_aligned.py

## Purpose
Regenerate the two CCN 2026 camera-ready figures using **"Brain-aligned / Brain-unaligned"**
terminology (the camera-ready text switched away from the accepted version's
"Brain-predictable / Brain-unpredictable"). Analysis content is byte-for-byte the same
as `archive/generate_figures.py`; only the visible labels and the file paths changed.

## Why
The figure PDFs in `study1/results/figures/figure{1,2}_ccn.pdf` still carry the old
"Brain-predictable" axis/legend labels, which now conflict with the camera-ready captions
("brain-aligned"). This script produces label-consistent figures.

## Inputs (read from `study1/data/`)
- `brain_predictable_dims.npz`  -> `r2_vjepa_per_dim` (100,)
- `pc_emotion_correlation.npz`  -> `brain_pred_mask_vjepa` (100,), `corr_vjepa_emo` (100,34), `emotion_labels`
- `exp17_av2d_results.npz`      -> `r2_pred_vjepa` (36,), `r2_all_vjepa` (36,), `dim_labels`
- `exp18_subjectwise_claim_check.npz` -> `r2_2d_vjepa` (6,36)

## Outputs
- `study1/results/figures/figure1_ccn.pdf` + `.png`   (archival copy)
- `study1/results/figures/figure2_ccn.pdf` + `.png`
- `ccn2026_template/figure1_ccn.pdf`                  (used by `camera_ready.tex`)
- `ccn2026_template/figure2_ccn.pdf`

## Label mapping vs. archive version
| old | new |
|---|---|
| Brain-predictable (n=3) | Brain-aligned (n=3) |
| Brain-unpredictable (n=97) | Brain-unaligned (n=97) |
| Brain-pred subspace | Brain-aligned subspace |
| brain-pred subspace -> target | brain-aligned subspace -> target |

## Reproduced numbers (printed to stdout, sanity check)
- Brain-aligned ratio = 1.441, Full-space ratio = 1.258
- Per-subject ratios = [1.958, 2.646, 2.646, 1.958, 1.958]

## Run
```bash
sbatch generate_figures_aligned.sh
```
After it completes, recompile `ccn2026_template/camera_ready.tex` (figures are already
referenced there by basename, no .tex edit needed).
