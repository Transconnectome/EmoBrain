# Native-Length Validation

This is the strongest direct test of the one-patch adapter. It requires an ROI array
with shape `(samples, 450, T)` or `(samples, T, 450)` and `T >= 160`.

For each sample the script compares:

- one native 160-TR Brain-JEPA embedding;
- ten native-position 16-TR embeddings;
- the mean of the ten short embeddings.

It reports full-to-short CKA, RSA, nearest-neighbor preservation, window-wise
geometry, and cross-validated prediction of native-length embedding PCs. All metrics
are repeated for pretrained and scratch models.

The input must already use Brain-JEPA-compatible ROI ordering and scaling. Supply
the exact training-compatible `medians` and `iqrs` through `--normalization-params`
when available. The script will not silently estimate incompatible normalization.

Run:

```bash
bash run_native_length_validation.sh /path/to/rest_timeseries.npy
```

or for NPZ:

```bash
bash run_native_length_validation.sh /path/to/rest_timeseries.npz timeseries
```

No suitable long rs-fMRI array currently exists inside `external/Brain-JEPA`; the
original repository contains code and checkpoint only. This script is ready when an
appropriate internal dataset path is supplied.
