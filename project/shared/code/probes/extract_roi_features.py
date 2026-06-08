"""
Schaefer 17n400p + Tian S3 50 = 450 ROI mean BOLD feature 추출.

Source: /pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_preprocess_JEPA_ROI/time_series/
        sub-XX/stimulus_N/{fMRI.Schaefer17n400p.csv.gz, fMRI.Tian_Subcortex_S3_3T.csv.gz}

각 stimulus 의 (450, T) ROI time-series 를 시간 axis 로 mean 해서 (450,) feature vector.
모든 2185 canonical stimulus 를 stack → (2185, 450) embedding tensor 저장.

Output: /pscratch/sd/s/sjmoon/FEELIN/project/shared/output/embeddings/roi_schaefer400tian50_mean/sub-XX.pt

Format: BFM extraction .pt 와 동일 (key: embeddings, stim_num, padding_ratio, ...).
이렇게 하면 unified probe pipeline 이 BFM embedding 처럼 처리 가능.

CANONICAL stimulus_num: 1..2185 (project_decisions.md 2185 canonical count).
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import torch

ROI_ROOT = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_preprocess_JEPA_ROI/time_series")
OUT_ROOT = Path("/pscratch/sd/s/sjmoon/FEELIN/project/shared/output/embeddings")
CANONICAL_N = 2185


def load_stim_features(subj_dir: Path, stim_num: int):
    """Return (450,) mean ROI feature for one stimulus, or None if missing."""
    stim_dir = subj_dir / f"stimulus_{stim_num}"
    cort = stim_dir / "fMRI.Schaefer17n400p.csv.gz"
    subc = stim_dir / "fMRI.Tian_Subcortex_S3_3T.csv.gz"
    if not cort.exists() or not subc.exists():
        return None, 0
    cort_df = pd.read_csv(cort)
    subc_df = pd.read_csv(subc)
    # columns: label_name, T1, T2, ...
    cort_ts = cort_df.iloc[:, 1:].values.astype(np.float32)  # (400, T)
    subc_ts = subc_df.iloc[:, 1:].values.astype(np.float32)  # (50, T)
    T = cort_ts.shape[1]
    assert subc_ts.shape[1] == T, f"T mismatch stim_{stim_num}: cort {T} vs subc {subc_ts.shape[1]}"
    combined = np.concatenate([cort_ts, subc_ts], axis=0)  # (450, T)
    return combined.mean(axis=1).astype(np.float32), T


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subjects", default="sub-01,sub-02,sub-03,sub-04,sub-05",
                    help="comma-separated subjects")
    ap.add_argument("--out_tag", default="roi_schaefer400tian50_mean",
                    help="output dir name under output/embeddings/")
    args = ap.parse_args()

    subjects = [s.strip() for s in args.subjects.split(",")]
    out_dir = OUT_ROOT / args.out_tag
    out_dir.mkdir(parents=True, exist_ok=True)

    for subj in subjects:
        subj_dir = ROI_ROOT / subj
        if not subj_dir.exists():
            print(f"[skip] {subj}: dir not found at {subj_dir}")
            continue
        print(f"\n=== {subj} ===")
        feats = []
        stim_nums = []
        original_Ts = []
        missing = []
        for stim_num in range(1, CANONICAL_N + 1):
            feat, T = load_stim_features(subj_dir, stim_num)
            if feat is None:
                missing.append(stim_num)
                continue
            feats.append(feat)
            stim_nums.append(stim_num)
            original_Ts.append(T)
            if stim_num % 500 == 0:
                print(f"  ...{stim_num}/{CANONICAL_N}")

        if missing:
            print(f"  [warn] {len(missing)} missing stimuli: first 5 = {missing[:5]}")

        emb = np.stack(feats, axis=0)  # (N, 450)
        stim_arr = np.asarray(stim_nums, dtype=np.int64)
        T_arr = np.asarray(original_Ts, dtype=np.int64)
        # padding_ratio: ROI features 는 시간 mean 으로 처리됐으니 padding 의미 없지만
        # downstream pipeline 호환 위해 0 으로 채움
        pad_ratio = np.zeros(len(feats), dtype=np.float32)

        payload = {
            "embeddings": torch.from_numpy(emb),
            "stim_num": torch.from_numpy(stim_arr),
            "padding_ratio": torch.from_numpy(pad_ratio),
            "original_T": torch.from_numpy(T_arr),
            "init": "n/a",
            "padding": "time_mean",
            "seed": 0,
            "model": "roi_schaefer17n400p_tian_S3_50_mean",
            "embed_dim": 450,
            "version": "v1",
        }
        out_path = out_dir / f"{subj}.pt"
        torch.save(payload, out_path)
        print(f"  saved {out_path}")
        print(f"    shape: {emb.shape}, T range: [{T_arr.min()}, {T_arr.max()}], "
              f"feat min/max/mean: {emb.min():.3f} / {emb.max():.3f} / {emb.mean():.3f}")


if __name__ == "__main__":
    main()
