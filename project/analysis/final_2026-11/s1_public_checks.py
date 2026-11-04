#!/usr/bin/env python3
"""S1: 참가자별 voxel 수와 공개 자료 대조 (2026-11-04).

voxel_counts.tsv        : HK 5명, MC 6명의 block 수와 voxel 수 (QC 뒤 배열 모양)
subcortex_definition.tsv: Horikawa 외(2020) 공개 코드 roiInf.mat의 피질하 10개 정의와, PickAtlas 표준 공간 voxel 수
original_folds.tsv      : 공개 코드의 run → fold 배정(1~10, 11~20, ..., 51~61)과 우리 분할(horikawa_rungroup6_v1)
화면 출력               : semantic_features.csv와 공개 semantic.mat의 차이, 레포 category.mat과 공개 파일의 md5
입력 공개 파일은 PM/atlas_sources/horikawa2020_figshare/ (feature.tar.gz, roiInf.mat)
"""
import hashlib
import tarfile
from io import BytesIO
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
import scipy.io as sio

PM = Path("/pscratch/sd/s/sjmoon")
REPO = PM / "EmoBrain"
MAN = REPO / "project/analysis/final_2026-11/manifests"
PUB = PM / "atlas_sources/horikawa2020_figshare"
ATLAS = PM / "atlas_sources/wfu_pickatlas/official/WFU_PickAtlas_3.0.5b/wfu_pickatlas"


def voxel_counts():
    rows = []
    for co, root, ver, subs in [("HK", "Horikawa", "v3_qc", "01 02 03 04 05"), ("MC", "MindCaptioning", "v2_qc", "01 02 03 04 05 06")]:
        for s in subs.split():
            a = np.load(PM / root / f"sub-{s}/{ver}/sub-{s}_blocks_common36_qc_runz.npy", mmap_mode="r")
            rows.append(dict(cohort=co, participant=f"sub-{s}", n_blocks=a.shape[0], n_voxels=a.shape[1]))
    t = pd.DataFrame(rows)
    t.to_csv(MAN / "voxel_counts.tsv", sep="\t", index=False)
    print(t.to_string(index=False))


def labels(txt):
    out = {}
    for line in open(txt, errors="ignore"):
        p = [s.strip() for s in line.strip().split("\t") if s.strip()]
        if len(p) >= 2 and p[0].isdigit():
            out[p[1].replace(" ", "_")] = int(p[0])
    return out


def subcortex():
    r = sio.loadmat(PUB / "roiInf.mat", squeeze_me=True, struct_as_record=False)["roiInf"].subcortex
    rows = []
    for d, n in zip(np.atleast_1d(r.roiDescrip), np.atleast_1d(r.roiName)):
        keys = sorted({str(x) for x in np.atleast_1d(n)})
        rec = dict(roi=str(d), original_keys=",".join(keys), left_right_merged=len(keys) == 2 or "brodmann_area_34" in keys[0] or "Caudate" in keys[0] or "Putamen" in keys[0] or "Hypothalamus" in keys[0])
        for ver, tag in [("MNI_atlas_templates", "mni_templates"), ("TD-ICBM_MNI_atlas_templates", "td_icbm")]:
            total = 0
            for k in keys:
                body = k.replace("pickatlas_r_w", "")
                if body.startswith("aal_MNI_V4_"):
                    file, lab = "aal_MNI_V4", body[len("aal_MNI_V4_"):]
                else:
                    file = "_".join(body.split("_")[:2])
                    lab = body[len(file) + 1:]
                img = ATLAS / ver / f"{file}.nii"
                if not img.exists():
                    total = None
                    break
                total += int((np.asarray(nib.load(img).dataobj) == labels(ATLAS / ver / f"{file}.txt")[lab]).sum())
            rec[f"n_voxels_2mm_{tag}"] = total
        rows.append(rec)
    t = pd.DataFrame(rows)
    t.to_csv(MAN / "subcortex_definition.tsv", sep="\t", index=False)
    print(t.to_string(index=False))


def folds():
    s = pd.read_csv(REPO / "docs/reports/prelim_2026-10/splits/horikawa_rungroup6_v1.tsv", sep="\t")
    r = s.groupby("run_index").fold.first().to_frame("our_fold_file").reset_index()
    r["original_run"] = r.run_index + 1
    r["original_fold_1based"] = pd.cut(r.original_run, [0, 10, 20, 30, 40, 50, 61], labels=[1, 2, 3, 4, 5, 6]).astype(int)
    r.to_csv(MAN / "original_folds.tsv", sep="\t", index=False)
    print(pd.crosstab(r.original_fold_1based, r.our_fold_file).to_string())


def public_files():
    with tarfile.open(PUB / "feature.tar.gz") as t:
        sem = sio.loadmat(BytesIO(t.extractfile("data/feature/semantic.mat").read()), squeeze_me=True, struct_as_record=False)["L"]
        cat_md5 = hashlib.md5(t.extractfile("data/feature/category.mat").read()).hexdigest()
    c = pd.read_csv(PM / "Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/semantic_features.csv")
    a = c.iloc[:, 1:].to_numpy(float)
    print("semantic_features.csv", a.shape, "public", np.shape(sem.feat), "same names and order", [str(x) for x in c.columns[1:]] == [str(x) for x in np.atleast_1d(sem.featname)], "max abs diff", float(np.abs(a - np.asarray(sem.feat, float)).max()))
    arch = REPO / "archive/v5_direction_split_20260628/dir3_ccn/data/raw/feature/category.mat"
    print("category.mat md5 public", cat_md5, "repo archive", hashlib.md5(arch.read_bytes()).hexdigest())


if __name__ == "__main__":
    voxel_counts()
    subcortex()
    folds()
    public_files()
