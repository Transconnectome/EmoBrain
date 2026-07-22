# CCN Minimal Reproduction Inputs

This manifest accompanies `CCN_REPRO_INPUTS_20260722.tar.gz`. The archive is
for transfer to another analysis server and must not be committed to GitHub.

## Included Inputs

| Relative path | Purpose |
|---|---|
| `data/raw/raw_fmri/fmri_raw.npy` | Five-subject raw parcel BOLD targets |
| `data/raw/video_embeddings/emovis_vjepa2_pretrained.npy` | Dereferenced pretrained V-JEPA2 embeddings |
| `data/raw/feature/vision.mat` | Visual control features |
| `data/raw/feature/semantic.mat` | Semantic control features |
| `data/raw/feature/categcontinuous.mat` | Continuous 34D affective profiles |
| `data/raw/feature/dimension.mat` | Arousal-valence and other dimensions |
| `study1/data/corrected_reanalysis/brain_jepa_native_1patch.npy` | Corrected frozen Brain-JEPA embeddings |
| `study1/data/corrected_reanalysis/brain_jepa_native_1patch.json` | Embedding provenance and hashes |
| `study2_thesis/results/ch1d_principal_gradient.npz` | Principal cortical gradient |
| `resources/Schaefer2018_400Parcels_7Networks_order_FSLMNI152_2mm.nii.gz` | Schaefer 400/Yeo 7 atlas |

The video embedding is a symlink in the original CCN tree. The transfer archive
contains the 12.3 MB target file under the expected CCN-relative filename.

## Restore

Extract the archive at the CCN project root:

```bash
tar -xzf CCN_REPRO_INPUTS_20260722.tar.gz
```

Move or point `--schaefer-atlas` to the included file under `resources/` when
regenerating brain figures. Analysis code, exact commands, results, and figure
captions are contained in `CCN_POSTER_HANDOFF_20260722.zip` and the GitHub CCN
subproject.

## Not Included

- Model checkpoints or original Brain-JEPA repository.
- Per-subject pre-stack embedding NPZ files, because the validated stacked NPY
  and its provenance JSON are sufficient for all current CCN analyses.
- Full generated result arrays, because the poster handoff includes the confirmed
  shared-alignment NPZ and all key result tables.
