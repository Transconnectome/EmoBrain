#!/usr/bin/env python3
"""GED 식 영역 하위 구역 평균 (2026-10-28).

GED (Huang et al., MICCAI 2022; utils.area_pooling) 는 영역마다 voxel 좌표의 최소~최대 범위를 축마다 n 등분해 n³ 개 직육면체로 나누고
각 직육면체 안 voxel 반응을 평균한다 (빈 직육면체는 0). 같은 규칙을 우리 지도(Schaefer400 + TianS3 + HypoBNST + Cereb7N + Brainstem,
469개 영역)와 v3_qc 블록 반응(run 안 z)에 적용한다. 영역 안 공간 정보를 영역 평균보다 많이 남긴다.
출력: runs/features/sub-XX_subroi<n>.npy (사용 가능한 블록 행 × 469 × n³, float32). 행 순서 = roi_blocks/Horikawa_sub-XX_roi469_rows.tsv
사용: python build_subroi_features.py --sub 01 [--n 4] [--max-rows 64]
"""
import argparse
import time
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd

HK = Path("/pscratch/sd/s/sjmoon/Horikawa")
ATLAS = "Schaefer400x7N+TianS3+HypoBNST+Cereb7N+Brainstem"
OUT = Path(__file__).resolve().parent / "runs/features"


def bins_for(sub, n):
    q, base = HK / f"sub-{sub}/v3_qc", HK / f"sub-{sub}/v3"
    mimg = nib.load(str(q / f"sub-{sub}_mask_qc.nii.gz")); M = np.asarray(mimg.dataobj) > 0
    aimg = nib.load(str(base / "atlas" / f"sub-{sub}_space-T1w_atlas-{ATLAS}_dseg.nii.gz"))
    assert aimg.shape == M.shape and np.allclose(aimg.affine, mimg.affine, atol=1e-4)
    lab = pd.read_csv(base / "atlas" / f"sub-{sub}_atlas-{ATLAS}_labels.tsv", sep="\t")
    roi_of = np.asarray(aimg.dataobj)[M].astype(int); ijk = np.argwhere(M)          # Y 열 순서 = M 의 C 순서
    pos = {r: i for i, r in enumerate(lab.roi_id.values)}
    bin_id = np.full(len(roi_of), -1)
    for r, i in pos.items():
        idx = np.flatnonzero(roi_of == r)
        if len(idx) == 0:
            continue
        c = ijk[idx]; b = np.zeros(len(idx), int)
        for ax in range(3):
            edges = np.linspace(c[:, ax].min(), c[:, ax].max(), n + 1)
            b = b * n + np.searchsorted(edges[1:-1], c[:, ax], side="right")          # 아래 경계 포함, 마지막 칸은 최대값 포함
        bin_id[idx] = i * n ** 3 + b
    return bin_id, len(lab), M.sum()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--sub", required=True); ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--max-rows", type=int, help="smoke test 용")
    a = ap.parse_args(); t0 = time.time(); OUT.mkdir(parents=True, exist_ok=True)
    bin_id, n_roi, n_vox = bins_for(a.sub, a.n)
    Y = np.load(HK / f"sub-{a.sub}/v3_qc/sub-{a.sub}_blocks_common36_qc_runz.npy", mmap_mode="r")
    assert Y.shape[1] == n_vox
    keep = bin_id >= 0; order = np.argsort(bin_id[keep], kind="stable"); cols = np.flatnonzero(keep)[order]; sb = bin_id[keep][order]
    nb = n_roi * a.n ** 3; ids = np.arange(nb)
    starts = np.searchsorted(sb, ids); ends = np.searchsorted(sb, ids, side="right"); cnt = ends - starts
    n_rows = min(len(Y), a.max_rows) if a.max_rows else len(Y)
    F = np.zeros((n_rows, nb), np.float32)
    for i0 in range(0, n_rows, 64):
        sl = slice(i0, min(i0 + 64, n_rows))
        X = np.asarray(Y[sl], np.float64)[:, cols]
        cs = np.concatenate([np.zeros((X.shape[0], 1)), np.cumsum(X, 1)], 1)
        with np.errstate(invalid="ignore", divide="ignore"):
            F[sl] = np.where(cnt > 0, (cs[:, ends] - cs[:, starts]) / np.maximum(cnt, 1), 0).astype(np.float32)
    F = F.reshape(n_rows, n_roi, a.n ** 3)
    tag = f"sub-{a.sub}_subroi{a.n}" + (f"_first{n_rows}" if a.max_rows else "")
    np.save(OUT / f"{tag}.npy", F)
    print(f"sub-{a.sub}: {F.shape}, 비어 있지 않은 하위 구역 {100 * (cnt > 0).mean():.1f}% ({time.time() - t0:.0f}초)")


if __name__ == "__main__":
    main()
