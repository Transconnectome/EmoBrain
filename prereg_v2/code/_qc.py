"""Shared paths and helpers for the preprocessing census (q0 to q4).

The census answers one question per stage of the existing preprocessing chain
and ends in a per-stage verdict: keep, or redo from which stage. It reads
data only; every artifact goes under prereg_v2/qc.

Chain being audited
-------------------
  step6  run-level z-scored MNI BOLD           not on this system
  step7  per-presentation segments (NIfTI)     EmoViS/data/raw/step7_voxel
    -> horikawa_parcellation.py (nilearn NiftiLabelsMasker, mean, no brain mask)
  ROI CSV per stimulus                         Horikawa_embedding/.../time_series
    -> EmoBrain/project/scripts/build_roi_timeseries.py
  roi_timeseries/sub-XX.pt                     EmoBrain/project/shared/data
  fmri_raw.npy                                 EmoViS/data/raw
  step7 -> MONAI (builder not accessible)
  filtered frames                              Horikawa_embedding/horikawa_filtered_MNI_to_TRs
"""
from __future__ import annotations

from pathlib import Path

from _assets import MANIFESTS, PREREG_ROOT, SCRATCH  # noqa: F401

QC = PREREG_ROOT / "qc"
QC_ATLAS = QC / "atlas"
QC_ROI = QC / "roi_runs"       # reconstructed ROI run time series (large, gitignored)
QC_MASKS = QC / "masks"

STEP7 = SCRATCH / "EmoViS/data/raw/step7_voxel"
ROI_CSV = SCRATCH / "Horikawa_embedding/horikawa_preprocess_JEPA_ROI/time_series"
FRAMES = SCRATCH / "Horikawa_embedding/horikawa_filtered_MNI_to_TRs/img"
PT_DIR = SCRATCH / "EmoBrain/project/shared/data/roi_timeseries"
FMRI_RAW = SCRATCH / "EmoViS/data/raw/fmri_raw.npy"

ATLAS_DIR = SCRATCH / "EmoDe/Foundation_baseline/Brain-JEPA/atlas"
SCHAEFER = ATLAS_DIR / "Schaefer2018_400Parcels_17Networks_order_FSLMNI152_2mm.nii.gz"
TIAN = ATLAS_DIR / "Tian_Subcortex_S3_3T.nii"

SUBJECTS = ["sub-01", "sub-02", "sub-03", "sub-04", "sub-05"]
TR = 2.0
GRID_SHAPE = (97, 115, 97)
# Recovered empirically in this audit: frame = max(step7, 0)[12:86, 12:103, 1:82]
FRAME_CROP = (slice(12, 86), slice(12, 103), slice(1, 82))
