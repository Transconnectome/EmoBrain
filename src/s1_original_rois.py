#!/usr/bin/env python3
"""S1: 원 논문 공개 자료에 든 참가자별 ROI를 우리 T1w 2 mm 격자로 옮겨 voxel 수와 공통 ROI를 센다 (2026-11-04).

입력
  HK: figshare 11988351의 fmri_SubjectN_Session1.h5 (metadata에 voxel 좌표와 ROI 표시)
  MC: figshare 25808179의 testPerception_SN.mat (metainf.xyz, roiind_value, roiname)
  ROI 370개의 이름: Horikawa 외(2020) 공개 코드의 roiInf.mat (hcp360 360개, subcortex 10개, 피질하는 좌우를 합침)
출력
  <output_root>/s1_original_rois/{hk,mc}_sub-XX_rois.npz (좌표와 ROI 표시, git 밖)
  같은 폴더 {hk,mc}_sub-XX_{voxels,grid}.tsv, --summary로 manifests/original_roi_voxels.tsv, original_roi_grid.tsv
  --sources로 manifests/original_roi_sources.tsv (figshare 파일 이름, 크기, md5와 판)
확인하는 것
  좌표가 우리 mask_qc 격자에 정확히 놓이는지(residual), 우리 QC mask 안의 voxel 수, voxel이 여러 ROI에 드는 수,
  해부 점검: 7 네트워크 표시(Vis, Default)와 우리 Schaefer400x7N 지도의 Dice.
이 표로 설계를 정하지 않는다. 어느 지도를 쓸지는 석진 님이 정한다(04 정할 것 3).
"""
import argparse
import json
import urllib.request
from pathlib import Path

import h5py
import nibabel as nib
import numpy as np
import pandas as pd
import scipy.io as sio
import paths as P

PM = P.DATA_ROOT
REPO = P.REPO
OUT = P.OUT / "s1_original_rois"
MAN = P.S1
ROI_INF = PM / "atlas_sources/horikawa2020_figshare/roiInf.mat"
COHORT = {"hk": ("Horikawa", "v3"), "mc": ("MindCaptioning", "v2")}
EXPECTED = {"hk": ["01", "02", "03", "04", "05"], "mc": ["01", "02", "03", "04", "05", "06"]}
MAX_GRID_RESIDUAL = 1e-3  # voxel. 좌표가 격자에 놓이지 않으면 반올림하지 않고 멈춘다.


def roi_sets():
    r = sio.loadmat(ROI_INF, squeeze_me=True, struct_as_record=False)["roiInf"]
    rows = []
    for d, n in zip(np.atleast_1d(r.hcp360.roiDescrip), np.atleast_1d(r.hcp360.roiName)):
        rows.append((str(d), "cortex", sorted({str(x) for x in np.atleast_1d(n)})))
    for d, n in zip(np.atleast_1d(r.subcortex.roiDescrip), np.atleast_1d(r.subcortex.roiName)):
        rows.append((str(d), "subcortex", sorted({str(x) for x in np.atleast_1d(n)})))
    assert len(rows) == 370, len(rows)
    return rows


def read_hk(path):
    with h5py.File(path, "r") as h:
        m = h["metadata"]
        key = [v.decode() for v in m["key"][()].ravel()]
        val = m["value"][()]
    assert val.shape[0] == len(key), val.shape
    assert len(set(key)) == len(key), "metadata key 중복"
    ix = {k: i for i, k in enumerate(key)}
    vd = val[ix["VoxelData"]] == 1
    xyz = np.c_[[val[ix[c]][vd] for c in ("voxel_x", "voxel_y", "voxel_z")]].T
    names = [k for k in key if k.startswith(("hcp180", "pickatlas", "yeo2011_7"))]
    flag = {k: val[ix[k]][vd] == 1 for k in names}
    return xyz, flag


def read_mc(path):
    with h5py.File(path, "r") as h:
        mi = h["metainf"]
        names = ["".join(chr(c) for c in h[r][()].ravel()) for r in mi["roiname"][()].ravel()]
        val = mi["roiind_value"][()]
        xyz = mi["xyz"][()]
    assert len(set(names)) == len(names), "roiname 중복"
    if val.shape[0] != len(names):
        val = val.T
    if xyz.shape[1] != 3:
        xyz = xyz.T
    assert val.shape[0] == len(names) and xyz.shape[1] == 3 and val.shape[1] == xyz.shape[0], (val.shape, xyz.shape)
    flag = {n: val[i] == 1 for i, n in enumerate(names) if n.startswith(("hcp180", "pickatlas", "yeo2011_7"))}
    return xyz.astype(np.float64), flag


def dice(a, b):
    return float(2 * (a & b).sum() / max(1, a.sum() + b.sum()))


def one(cohort, sub, path):
    root, ver = COHORT[cohort]
    xyz, flag = (read_hk if cohort == "hk" else read_mc)(path)
    mimg = nib.load(PM / root / f"sub-{sub}/{ver}_qc/sub-{sub}_mask_qc.nii.gz")
    mask = np.asarray(mimg.dataobj) > 0
    raw = nib.affines.apply_affine(np.linalg.inv(mimg.affine), xyz)
    assert np.isfinite(xyz).all(), "좌표에 유한하지 않은 값"
    resid = float(np.abs(raw - np.round(raw)).max())
    if resid > MAX_GRID_RESIDUAL:
        raise ValueError(f"{cohort} sub-{sub}: 좌표가 격자에 놓이지 않음 (잔차 {resid})")
    ijk = np.round(raw).astype(int)
    inb = ((ijk >= 0) & (ijk < np.array(mask.shape))).all(1)
    inmask = np.zeros(len(ijk), bool)
    inmask[inb] = mask[tuple(ijk[inb].T)]
    sets = roi_sets()
    for k, f in flag.items():
        assert f.shape == (len(ijk),), (k, f.shape)
    M = np.zeros((len(ijk), len(sets)), bool)
    rows = []
    for c, (name, kind, keys) in enumerate(sets):
        missing = [k for k in keys if k not in flag]
        assert not missing, missing
        f = np.any([flag[k] for k in keys], 0)
        M[:, c] = f
        rows.append(dict(cohort=cohort, participant=f"sub-{sub}", roi=name, kind=kind, n_orig=int(f.sum()), n_in_qc_mask=int((f & inmask).sum())))
    atlas = PM / root / f"sub-{sub}/{ver}/atlas"
    D = np.asarray(nib.load(atlas / f"sub-{sub}_space-T1w_atlas-Schaefer400x7N_dseg.nii.gz").dataobj)
    lab = pd.read_csv(atlas / f"sub-{sub}_atlas-Schaefer400x7N_labels.tsv", sep="\t")
    cn = [x for x in lab.columns if "name" in x or "label" in x][0]
    ci = [x for x in lab.columns if "id" in x or "index" in x][0]

    def vol(keys):
        f = np.any([flag[k] for k in keys], 0) & inb
        o = np.zeros(mask.shape, bool)
        o[tuple(ijk[f].T)] = True
        return o

    def ours(tag):
        return np.isin(D, lab[lab[cn].str.contains(tag)][ci].values)

    grid = dict(cohort=cohort, participant=f"sub-{sub}", n_orig_voxels=len(ijk), grid_residual=resid, n_in_grid=int(inb.sum()),
                n_in_qc_mask=int(inmask.sum()), n_qc_mask=int(mask.sum()), n_in_any_roi=int(M.any(1).sum()), n_in_several_rois=int((M.sum(1) > 1).sum()),
                dice_vis=dice(vol(["yeo2011_7_r_lh.7Networks_1", "yeo2011_7_r_rh.7Networks_1"]), ours("_Vis_")),
                dice_default=dice(vol(["yeo2011_7_r_lh.7Networks_7", "yeo2011_7_r_rh.7Networks_7"]), ours("_Default_")))
    OUT.mkdir(parents=True, exist_ok=True)
    tag = f"{cohort}_sub-{sub}"
    np.savez_compressed(OUT / f"{tag}_rois.npz", ijk=ijk.astype(np.int16), in_qc_mask=inmask, member=M, roi=np.array([s[0] for s in sets]), affine=mimg.affine, shape=np.array(mask.shape))
    pd.DataFrame(rows).to_csv(OUT / f"{tag}_voxels.tsv", sep="\t", index=False)
    pd.DataFrame([grid]).to_csv(OUT / f"{tag}_grid.tsv", sep="\t", index=False, float_format="%.4g")
    print(grid, flush=True)


def summary():
    want = [f"{c}_sub-{s}" for c, subs in EXPECTED.items() for s in subs]
    missing = [t for t in want if not (OUT / f"{t}_voxels.tsv").exists() or not (OUT / f"{t}_grid.tsv").exists()]
    if missing:
        raise ValueError(f"빠진 참가자: {missing}")
    V = pd.concat([pd.read_csv(OUT / f"{t}_voxels.tsv", sep="\t") for t in want])
    G = pd.concat([pd.read_csv(OUT / f"{t}_grid.tsv", sep="\t") for t in want])
    names = [s[0] for s in roi_sets()]
    for (c, p), d in V.groupby(["cohort", "participant"]):
        if d.roi.tolist() != names:
            raise ValueError(f"{c} {p}: ROI 370개의 이름이나 순서가 다름")
    V.to_csv(MAN / "original_roi_voxels.tsv", sep="\t", index=False)
    G.to_csv(MAN / "original_roi_grid.tsv", sep="\t", index=False)
    print(G.to_string(index=False))
    V["frac"] = V.n_in_qc_mask / V.n_orig
    for cohort, d in V.groupby("cohort"):
        c = d[d.kind == "cortex"].groupby("roi").n_orig.mean()
        s = d[d.kind == "subcortex"].groupby("roi").n_orig.mean().round(1)
        print(cohort, "cortex n_orig mean min, median, max", round(c.min(), 1), round(c.median(), 1), round(c.max(), 1))
        print(cohort, "subcortex n_orig mean", s.to_dict())
    n_part = V.participant.astype(str).add(V.cohort).nunique()
    for label, ok in [("in mask > 0", V.n_in_qc_mask > 0), ("in mask >= 10 and frac >= 0.2 (roi_valid rule)", (V.n_in_qc_mask >= 10) & (V.frac >= 0.2))]:
        good = V[ok].groupby("roi").size()
        print(label, "ROIs valid in all", n_part, "participants:", int((good == n_part).sum()), "not all:", sorted(set(V.roi) - set(good[good == n_part].index)))
    print("lowest frac in mask:\n", V.sort_values("frac").head(12)[["cohort", "participant", "roi", "n_orig", "n_in_qc_mask", "frac"]].round(3).to_string(index=False))
    print("n_in_qc_mask min by kind:\n", V.groupby(["cohort", "kind"]).n_in_qc_mask.min().to_string())


def sources():
    rows = []
    want = {"11988351": [f"Subject{n}_preprocessed_fmri.tar.gz" for n in range(1, 6)] + ["feature.tar.gz"], "25808179": [f"testPerception_S{n}.mat" for n in range(1, 7)]}
    for art, names in want.items():
        with urllib.request.urlopen(f"https://api.figshare.com/v2/articles/{art}", timeout=60) as r:
            d = json.load(r)
        files = {f["name"]: f for f in d["files"]}
        for n in names:
            f = files[n]
            rows.append(dict(figshare_article=art, doi=d["doi"], version=d.get("version"), file=n, size=f["size"], md5=f.get("computed_md5") or f.get("supplied_md5")))
    t = pd.DataFrame(rows)
    t.to_csv(MAN / "original_roi_sources.tsv", sep="\t", index=False)
    print(t.to_string(index=False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cohort", choices=list(COHORT))
    ap.add_argument("--sub")
    ap.add_argument("--path", type=Path)
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--sources", action="store_true")
    a = ap.parse_args()
    if a.sources:
        sources()
    elif a.summary:
        summary()
    else:
        one(a.cohort, a.sub, a.path)


if __name__ == "__main__":
    main()
