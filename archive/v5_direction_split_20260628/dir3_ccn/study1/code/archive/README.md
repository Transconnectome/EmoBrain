# study1/code/archive/

Scripts no longer in active rotation. Kept for two reasons:
1. **Figure generators** that produced the CCN 2026 paper figures (regenerate-on-demand is non-trivial).
2. **Exploratory analyses** whose intermediate `.npz` outputs (in `study1/data/`) are referenced in `RESULTS_EXP*.md` notes.

Do not delete without checking which figure or RESULTS_EXP*.md depends on the script.

## Contents

### Figure generators (used to produce the accepted CCN abstract)

- `20_make_nature_figures.py` — Nature-style figures.
- `22_generate_main_figures.py` — main paper figures (figure1_ccn, figure2_ccn likely from here).
- `24_generate_all_figures.py` — full figure set.
- `25_quick_cca100_figure.py` — CCA-100 supplementary figure.
- `generate_figures.py` — general figure helper.

### Exploratory analyses (referenced in RESULTS_EXP*.md)

- `03_procrustes.py` — Procrustes alignment between brain and V-JEPA2 RSMs.
- `04_crossspace_rsa.py` — cross-space RSA.
- `05_k_sweep.py` — number-of-PCs sweep for brain-predictable subspace.
- `06_umap.py` — UMAP visualization of representations.
- `07_raw_rsm_rsa_cka.py` / `08_raw_k_sweep.py` / `09_raw_umap.py` — raw-fMRI counterparts.
- `12_dimensional_emotion_analysis.py` / `12_raw_cat_vs_dim_14d.py` / `12_subspace_cat_vs_dim*.py` — categorical-vs-dimensional ratio variants (14-dim, raw, subspace).
- `14_robustness_confound_sensitivity.py` — VGG19 + semantic confound regression (the "attenuated but preserved" result in the abstract).
- `15_subject_stability_alpha_resampling.py` — per-subject ratio stability.
- `16_incremental_baseline_benchmark.py` / `16_incremental_baseline_benchmark_14d.py` — incremental baseline benchmarks.
- `19_subjectwise_direct_decoding.py` — per-subject direct decoding control.
- `21b_cca_100_noperm.py` — CCA with k=100, no permutation.
- `exp13_vision_semantic.py` / `exp13_vision_semantic_14d.py` — vision + semantic feature experiment (related to the abstract's confound regression).

### `extraction_infra/`

Infrastructure scripts (download, embedding extraction) reusable for future analyses (e.g. layer-wise breakdown, alternative model embedding extraction). Kept because they are not specific to the superseded V-JEPA2-vs-CLIP analysis.

- `01_download_vjepa2.py` — V-JEPA2 model download from HuggingFace.
- `02_extract_video_embeddings.py` / `extract_video_embeddings.py` — V-JEPA2 video embedding extraction.
- `03_extract_layer_embeddings.py` — V-JEPA2 **layer-wise** embedding extraction (relevant to Tier 3 layer-wise analysis in `notes/narrative_v2.md`).
- `03_load_brain_embeddings.py` — Brain-JEPA embedding loader.
- `05_extract_clip_embeddings.py` — CLIP embedding extraction (CLIP is no longer in the main paper but the script is useful for any static-image baseline).

## Removed on 2026-05-26

The following workstream-A (V-JEPA2 ↔ CLIP overall + per-emotion CKA) analysis scripts and outputs were deleted because the paper pivoted away from that framing (see `notes/archive/CCN_draft.md` for the superseded narrative). Outputs were ~226 MB.

- `04_layer_geometry_comparison.py`, `04_train_subject_blocks.py`
- `06_cka_analysis.py`, `06b_significance.py`, `06c_emotion_rsm_analysis.py`, `06d_affective_dim_analysis.py`
- `07_plot_figures.py`, `07_raw_fmri_rsa.py`
- `cka_results/`, `raw_fmri_outputs/`, `subject_blocks/`, old `figures/` (figure1_overall_cka, figure2_per_emotion_cka)

Also deleted: one-time metadata helpers `ccn_dim14_metadata.py`, `update_metadata_14d.py`.
