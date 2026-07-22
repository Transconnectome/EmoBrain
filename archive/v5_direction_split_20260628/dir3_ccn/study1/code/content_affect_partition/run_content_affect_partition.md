# Content-Affect Partition

## Scientific Question

Is affective cortical geometry inherited from stimulus-computable visual-semantic content, or does fine-grained affect explain complementary brain variance beyond that content?

## Why No Video PCA

The primary V-JEPA2 predictor is the raw 1408-dimensional embedding. Kernel ridge regression supports different input and target dimensions directly, so PCA is not required for dimension matching. Linear CKA also compares feature matrices with different numbers of columns.

PCA is used only on the 34D emotion profile to construct explicit dimension-matched controls (`k=2,3,5,10,20,34`). It is never used on V-JEPA2 in this module.

## Encoding Models

- `video`: raw 1408D V-JEPA2
- `content`: 1000D visual plus 73D semantic features
- `video_content`: all video and content features
- `vc_av`: video + content + arousal/valence
- `vc_eK`: video + content + emotion-profile PCA rank K

All models use identical held-out stimulus folds. Kernel-ridge alpha is selected inside each outer training fold using a held-out subset and group-mean BOLD; final predictions retain all five subjects separately.

## Primary Contrasts

- `unique_e34_vc`: 34D affect beyond raw V-JEPA2 and visual-semantic content
- `matched_2d_vs_av`: emotion-profile PCA-2D versus arousal-valence with matched dimensionality
- `fine_grained_vs_av`: full 34D profile versus arousal-valence
- `resolution_34d_vs_2d`: information gained by increasing affective resolution from 2D to 34D
- `unique_video_given_content` and `unique_content_given_video`: video/content variance partition

## Brain Figures

The main figure contains:

1. raw video + visual-semantic encoding `R2`
2. unique 34D affect beyond video + content
3. full 34D advantage over arousal-valence
4. 34D-versus-2D affective resolution gain

Network summaries, principal-gradient effects, subject-wise tests, FDR values, and NIfTI parcel maps are saved alongside the figure.

## Inputs

- `data/raw/video_embeddings/emovis_vjepa2_pretrained.npy`
- `data/raw/brain_embeddings/brain_jepa_embeddings.npy`
- `data/raw/raw_fmri/fmri_raw.npy`
- `data/raw/feature/vision.mat`
- `data/raw/feature/semantic.mat`
- `data/raw/feature/categcontinuous.mat`
- `data/raw/feature/dimension.mat`

## Outputs

Default directory: `study1/results/content_affect_partition/`

- `direct_geometry_cka.csv`
- `content_affect_partition_results.npz`
- `map_statistics_subjectwise.csv`
- `map_statistics_group.csv`
- `network_summary_subjectwise.csv`
- `gradient_summary_subjectwise.csv`
- `parcel_maps_group.csv`
- `content_affect_brain_maps.png/.pdf`
- `content_affect_network_summary.png/.pdf`
- `brain_map_*.nii.gz`
- `run_config.json`

## Usage

```bash
# Pipeline validation
/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python run_content_affect_partition.py --smoke

# Full analysis
sbatch run_content_affect_partition.sh

# Direct no-PCA CKA only
/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python run_content_affect_partition.py \
  --geometry-only \
  --output-dir ../../results/content_affect_partition/geometry_only
```

## Guardrails

- A positive 34D increment is affectively meaningful but not automatically emotion-specific; the visual-semantic control defines the tested content baseline.
- A 34D-versus-A/V difference is interpreted only alongside the PCA-2D matched comparison and rank sweep.
- Cross-validated commonality can be negative and is descriptive.
- Parcel-gradient correlations require spatially informed nulls before parcel-level inference.
- Five subjects are the inferential units; 400 parcels are not 400 independent observations.
