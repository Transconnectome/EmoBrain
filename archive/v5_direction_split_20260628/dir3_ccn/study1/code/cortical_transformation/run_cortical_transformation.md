# Cortical Transformation

## Purpose

This is the primary brain-centric analysis for the updated CCN poster. It asks where a compact V-JEPA2/Brain-JEPA shared representation is expressed in cortex and where affective annotations explain raw BOLD variance beyond that representation.

The script does not interpret 34 ratings as discrete cortical categories. `categcontinuous.mat` supplies a continuous 34-dimensional affective profile; `dimension.mat` supplies arousal and valence.

## Leakage Control

For held-out subject `s` and each outer stimulus fold:

1. Average Brain-JEPA embeddings over the other four subjects.
2. Fit video PCA, brain PCA, and cross-view SVD using training stimuli only.
3. Transform held-out videos into shared scores.
4. Train parcel-wise encoding models on subject `s`'s training-stimulus BOLD.
5. Predict subject `s`'s held-out-stimulus BOLD.

Thus the held-out subject is excluded from shared-subspace discovery, and all reported parcel metrics use out-of-fold stimulus predictions.

## Models And Contrasts

Encoding models:

- `shared`: prespecified number of cross-view shared scores
- `shared_e34`: shared scores plus 34D continuous emotion profile
- `shared_av`: shared scores plus arousal and valence
- `video`: full cross-validated V-JEPA2 PCA scores
- `video_e34`: video scores plus 34D profile
- `video_av`: video scores plus arousal and valence

Primary parcel maps:

- `shared`: held-out `R2(shared)`
- `unique_e34_shared`: `R2(shared + E34) - R2(shared)`
- `fine_grained_advantage`: `R2(shared + E34) - R2(shared + AV)`
- `unique_e34_video`: `R2(video + E34) - R2(video)`

Raw, unclipped `R2` is primary. Pearson and Spearman maps for every base model are also saved.

## Shared-Rank Workflow

The default cortical run uses the accepted rank 3 as a prespecified starting value. The same run saves held-out cross-view correlations for components `1..max-rank` and shuffled-correspondence nulls in `shared_rank_diagnostics.csv`.

Use these diagnostics to choose a stable rank before the final run, then pass it explicitly with `--shared-rank K`. Do not choose rank from cortical-map outcomes.

## Inputs

- `data/raw/video_embeddings/emovis_vjepa2_pretrained.npy`: `(2185, 1408)`
- `data/raw/brain_embeddings/brain_jepa_embeddings.npy`: `(5, 2196, 768)`
- `data/raw/raw_fmri/fmri_raw.npy`: `(5, 2196, 450)`; first 400 parcels are cortical
- `data/raw/feature/categcontinuous.mat`: continuous 34D profile
- `data/raw/feature/dimension.mat`: 14 dimensions, including arousal and valence
- `study2_thesis/results/ch1d_principal_gradient.npz`: independent 400-parcel principal gradient
- cached Schaefer 400 / 7-network NIfTI, or `--schaefer-atlas PATH`

Only the first 2185 unique stimuli are used in the full analysis.

## Outputs

Default directory: `study1/results/cortical_transformation/`

- `cortical_transformation_results.npz`: all model metrics and contrast maps by subject
- `parcel_maps_group.csv`: group maps, subject SEM, network, and gradient coordinate
- `shared_rank_diagnostics.csv`: held-out cross-view component results
- `shared_rank_group_summary.csv`: group correlation, interval, null percentile, and stability by component
- `network_summary_subjectwise.csv`
- `gradient_summary_subjectwise.csv`
- `map_means_subjectwise.csv`
- `hierarchy_contrasts_subjectwise.csv`
- `hierarchy_group_statistics.csv`
- `cortical_transformation_summary.png/.pdf`
- `brain_map_*.nii.gz` and `cortical_brain_maps.png/.pdf`
- `run_config.json`

With `--save-predictions`, OOF predictions are written to `study1/data/cortical_transformation/`.

## Commands

Smoke test:

```bash
/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python run_cortical_transformation.py --smoke
```

Full analysis:

```bash
/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python run_cortical_transformation.py \
  --shared-rank 3 \
  --n-pca 100 \
  --max-rank 20 \
  --n-folds 5 \
  --n-shuffles 100
```

## Interpretation Guardrails

- A shared map localizes information recoverable across the two foundation models; it is not automatically affect-specific.
- Positive unique 34D variance means the ratings improve held-out BOLD prediction beyond the stated baseline.
- Fine-grained advantage means the 34D profile improves prediction more than A/V under matched folds and regularization. It does not imply 34 discrete neural modules.
- Principal-gradient parcel correlations are descriptive until a spatial-autocorrelation-aware null is added. Cross-subject network and planned contrasts are the primary tests.
- The target cortical hierarchy claim is used only if effects are consistent across subjects and survive the full-video control.
