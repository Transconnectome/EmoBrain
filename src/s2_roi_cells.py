#!/usr/bin/env python3
"""ROI 칸 번호 (11/9 석진 님, 입력층 점검의 칸 평균).

같은 Horikawa 2020 자료의 선행 모델(GED, ML-BVAE, EmoGrowth)이 쓴 ROI pooling을 따른다. ROI마다 그 voxel들의 좌표 범위를
x, y, z 축마다 n등분해 n³칸으로 나누고, voxel마다 몇 번째 칸인지 적는다(01 5-5의 "(가) 칸 평균"). n = 2(8칸)는 EmoGrowth의 고정값이다.
칸 평균 자체는 S6의 입력층(s6_model.RoiCellInput)이 학습 자료를 읽을 때 낸다. 여기서는 voxel의 칸 번호만 만든다.

입력: s2_manifest/roi_voxels/hk_sub-XX.npz(ROI마다 QC mask의 열 번호), 원자료의 QC mask(열 번호 = mask의 NumPy 기본 순서).
출력: s2_manifest/roi_cells/hk_sub-XX.npz. cells는 roi_voxels의 columns와 같은 순서(ROI 순서로 이어 붙인 열, 겹치는 voxel은 ROI마다 한 번씩).
사용: s2_roi_cells.py [--check]
"""
import argparse
import hashlib
import sys

import numpy as np

import paths as P
import s5_common as d5

N_SPLIT = 2  # 축마다 나누는 수. 8칸(EmoGrowth)
OUT = P.OUT / "s2_manifest/roi_cells"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def mask_path(s):
    return d5.PM / f"Horikawa/sub-{s}/v3_qc/sub-{s}_mask_qc.nii.gz"


def cell_ids(ijk, n=N_SPLIT):
    """ROI 하나의 voxel 좌표(행 × 3)를 받아 칸 번호(0 ~ n³ − 1)를 낸다. 축마다 그 ROI의 최소~최대 좌표를 n등분한다."""
    ijk = np.asarray(ijk, np.int64)
    if ijk.ndim != 2 or ijk.shape[1] != 3 or len(ijk) == 0:
        raise ValueError("좌표는 voxel × 3이고 비어 있지 않아야 한다")
    lo, span = ijk.min(0), ijk.max(0) - ijk.min(0) + 1
    b = np.minimum((ijk - lo) * n // span, n - 1)
    return (b[:, 0] * n * n + b[:, 1] * n + b[:, 2]).astype(np.int8)


def build(s):
    import nibabel as nib
    z = np.load(d5.roi_path(s))
    mpath = mask_path(s)
    if sha(mpath) != str(z["mask_sha256"]):
        raise SystemExit(f"sub-{s}: QC mask가 ROI 표를 만들 때와 다르다")
    mask = np.asarray(nib.load(mpath).dataobj) > 0
    if tuple(mask.shape) != tuple(z["shape"]) or int(mask.sum()) != int(z["n_columns"]):
        raise SystemExit(f"sub-{s}: mask 크기나 voxel 수가 ROI 표와 다르다")
    ijk = np.argwhere(mask)  # 열 번호 = mask의 NumPy 기본 순서(s2_manifest)
    cols, off = z["columns"], z["offsets"]
    cells = np.concatenate([cell_ids(ijk[cols[off[r]:off[r + 1]]]) for r in range(len(off) - 1)])
    return dict(cells=cells, n_split=np.int64(N_SPLIT), roi=z["roi"], offsets=off, mask_sha256=z["mask_sha256"], roi_file_sha256=np.array(sha(d5.roi_path(s))))


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--check", action="store_true", help="만든 파일이 지금 ROI 표, mask와 같은지만 본다")
    args = a.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    bad = 0
    for s in d5.HK:
        new = build(s)
        path = OUT / f"hk_sub-{s}.npz"
        if args.check:
            old = np.load(path)
            same = np.array_equal(old["cells"], new["cells"]) and str(old["roi_file_sha256"]) == str(new["roi_file_sha256"])
            print(f"sub-{s}", "같음" if same else "다름")
            bad += not same
            continue
        np.savez_compressed(path, **new)
        filled = [len(np.unique(new["cells"][new["offsets"][r]:new["offsets"][r + 1]])) for r in range(len(new["offsets"]) - 1)]
        print(f"sub-{s} voxel {len(new['cells'])}, ROI마다 voxel이 있는 칸 수: 최소 {min(filled)}, 중앙값 {int(np.median(filled))}, 최대 {max(filled)}", flush=True)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
