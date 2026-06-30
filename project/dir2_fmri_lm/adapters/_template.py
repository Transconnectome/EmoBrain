"""Template adapter. Raw fMRI -> fMRI-LM HDF5 schema.

Output schema (official fMRI-LM/dataset.py 기준):

    data/<DATASET>/fmri/<ATLAS>/
    ├── data_resampled.h5
    │     time_series/sample_{i}: (N_rois, N_timepoints) float32
    │     metadata/subjects:      (N_samples,) bytes
    │     metadata/sessions:      (N_samples,) bytes
    ├── normalization_params.npz
    │     medians (N_rois,) iqrs (N_rois,)    # if --norm robust
    │     mean    (N_rois,) std  (N_rois,)    # if --norm std
    └── descriptors_rewritten/
          fc_descriptors.csv        # required if --desc_type fc
          ica_descriptors.csv       # required if --desc_type ica
          gradient_descriptors.csv  # optional
          graph_descriptors.csv     # optional

이 파일은 협업자가 새 dataset 에 대해 복사해서 채우는 template.
구체 dataset adapter 는 같은 폴더에 `horikawa.py`, `emo_film.py` 등으로 추가.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import h5py
import numpy as np


def write_h5(
    out_path: Path,
    time_series: list[np.ndarray],
    subjects: list[str],
    sessions: list[str],
) -> None:
    """time_series[i]: (N_rois, N_timepoints) float32."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(out_path, "w") as f:
        ts_grp = f.create_group("time_series")
        for i, ts in enumerate(time_series):
            ts_grp.create_dataset(f"sample_{i}", data=ts.astype(np.float32))
        meta = f.create_group("metadata")
        meta.create_dataset("subjects", data=np.array(subjects, dtype="S64"))
        meta.create_dataset("sessions", data=np.array(sessions, dtype="S64"))


def write_normalization_params(out_path: Path, time_series: list[np.ndarray], norm: str = "robust") -> None:
    """Stack along time, compute per-ROI stats."""
    cat = np.concatenate(time_series, axis=1)  # (N_rois, sum_T)
    if norm == "robust":
        medians = np.median(cat, axis=1)
        q75 = np.percentile(cat, 75, axis=1)
        q25 = np.percentile(cat, 25, axis=1)
        iqrs = q75 - q25
        np.savez(out_path, medians=medians, iqrs=iqrs)
    elif norm == "std":
        mean = cat.mean(axis=1)
        std = cat.std(axis=1)
        np.savez(out_path, mean=mean, std=std)
    else:
        raise ValueError(f"unknown norm {norm}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", required=True, help="data/<DATASET>/fmri/<ATLAS>/")
    p.add_argument("--norm", choices=["robust", "std"], default="robust")
    args = p.parse_args()

    raise NotImplementedError(
        "This is a template. Copy this file to adapters/<dataset_name>.py and implement:\n"
        "  1. Load your raw fMRI volumes per subject/session\n"
        "  2. Apply atlas (Schaefer-400 + Tian-S3 50 = 450 ROI is fMRI-LM default)\n"
        "  3. Return time_series list of (450, T) per sample\n"
        "  4. Call write_h5 + write_normalization_params"
    )


if __name__ == "__main__":
    main()
