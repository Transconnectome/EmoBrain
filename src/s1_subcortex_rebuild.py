#!/usr/bin/env python3
"""S1: 피질하 10개를 PickAtlas에서 새로 만들어 저자 공개 mask, FreeSurfer aseg와 비교한다 (04 정할 것 5, 7, 2026-11-04).

(가) 공개 mask + sub-03만 새로 만듦과 (나) 11명 모두 새로 만듦을 해부학적 위치로만 비교하기 위한 표다.
뇌 반응, 정서 점수, 모델 성능은 읽지 않는다. 이 표의 숫자가 높은 쪽을 자동으로 고르지 않는다.
aseg는 수작업 정답이 아니고 지도와 정의도 다르므로(ex) Talairach Daemon 조가비핵 대 FreeSurfer 조가비핵), 위치에 큰 이상이 있는지 보는 용도다.

변환: s1_subcortex_rebuild.sh가 PickAtlas MNI_atlas_templates/MNI_T1.nii를 참가자 T1w에 ANTs로 직접 등록한다.
       MNI 공간끼리 같다고 놓지 않기 위해서이고, 설정은 antsRegistrationSyNQuick.sh 기본값(-t s)이다.
복셀화 후보 두 개(미리 고정, 팽창이나 문턱을 더하지 않음)
  nn_2mm      : 지도 라벨을 우리 2 mm 격자로 최근접 이웃으로 바로 옮긴다
  overlap_2mm : 지도 라벨을 T1w 1 mm로 최근접 이웃으로 옮긴 뒤, ROI에 속한 1 mm voxel의 중심이 드는 2 mm voxel을 모두 포함한다. 정확한 부피 교차 판정이 아니다
입력: <work>/<tag>_<atlas>_{nn2mm,t1w}.nii.gz, manifests/subcortex_definition.tsv, s1_original_rois의 npz
출력: <work>/<tag>_new_masks.npz, <work>/<tag>_check.tsv, --summary로 manifests/subcortex_rebuild_check.tsv
"""
import argparse
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
import paths as P

PM = P.DATA_ROOT
REPO = P.REPO
MAN = P.S1
PUB = P.OUT / "s1_original_rois"
WORK = P.OUT / "s1_subcortex_rebuild"
ATLAS = PM / "atlas_sources/wfu_pickatlas/official/WFU_PickAtlas_3.0.5b/wfu_pickatlas/MNI_atlas_templates"
COHORT = {"hk": ("Horikawa", "v3", "01 02 03 04 05"), "mc": ("MindCaptioning", "v2", "01 02 03 04 05 06")}
ASEG = {"hyppocampus": [17, 53], "thalamus": [10, 49], "amygdala": [18, 54], "caudate": [11, 50], "putamen": [12, 51], "pallidum": [13, 52], "brainstem": [16], "cerebellum": [7, 8, 46, 47]}


def labels(txt):
    out = {}
    for line in open(txt, errors="ignore"):
        p = [s.strip() for s in line.strip().split("\t") if s.strip()]
        if len(p) >= 2 and p[0].isdigit():
            out[p[1].replace(" ", "_")] = int(p[0])
    return out


def roi_parts():
    """ROI 이름 → [(지도 파일, 라벨 번호), ...]. 공개 코드의 키에서 푼다."""
    t = pd.read_csv(MAN / "subcortex_definition.tsv", sep="\t")
    parts = {}
    for _, r in t.iterrows():
        items = []
        for k in r.original_keys.split(","):
            body = k.replace("pickatlas_r_w", "")
            if body.startswith("aal_MNI_V4_"):
                file, lab = "aal_MNI_V4", body[len("aal_MNI_V4_"):]
            else:
                file = "_".join(body.split("_")[:2])
                lab = body[len(file) + 1:]
            items.append((file, labels(ATLAS / f"{file}.txt")[lab]))
        parts[r.roi] = items
    assert len(parts) == 10, len(parts)
    return parts


def dice(a, b):
    return float(2 * (a & b).sum() / max(1, a.sum() + b.sum()))


def best_z(v, ref):
    """z축만 −40~+40 mm(2 mm 간격). 감기지 않게 좌표를 옮긴다. 돌려주는 값은 (Dice, mm)."""
    p = np.argwhere(v)
    best = (-1.0, 0)
    for k in range(-20, 21):
        q = p + np.array([0, 0, k])
        q = q[(q >= 0).all(1) & (q < np.array(ref.shape)).all(1)]
        d = 2 * float(ref[tuple(q.T)].sum()) / max(1, len(q) + int(ref.sum()))
        if d > best[0] or (d == best[0] and k == 0):
            best = (d, 2 * k)
    return best


def on_grid(img, m):
    ii = np.indices(m.shape).reshape(3, -1).T
    j = np.round(nib.affines.apply_affine(np.linalg.inv(img.affine), nib.affines.apply_affine(m.affine, ii))).astype(int)
    ok = ((j >= 0) & (j < np.array(img.shape[:3]))).all(1)
    a = np.asarray(img.dataobj)
    o = np.zeros(len(ii), a.dtype)
    o[ok] = a[tuple(j[ok].T)]
    return o.reshape(m.shape)


def overlap_to_grid(flag, img1mm, m):
    """ROI에 속한 1 mm voxel의 중심이 드는 2 mm voxel을 모두 True로 한다. np.round의 반칸 동점은 짝수 인덱스로 간다."""
    out = np.zeros(m.shape, bool)
    p = np.argwhere(flag)
    if len(p) == 0:
        return out
    j = np.round(nib.affines.apply_affine(np.linalg.inv(m.affine), nib.affines.apply_affine(img1mm.affine, p))).astype(int)
    j = j[((j >= 0) & (j < np.array(m.shape))).all(1)]
    out[tuple(j.T)] = True
    return out


def one(cohort, sub):
    root, ver, _ = COHORT[cohort]
    tag = f"{cohort}_sub-{sub}"
    m = nib.load(PM / root / f"sub-{sub}/{ver}_qc/sub-{sub}_mask_qc.nii.gz")
    mask = np.asarray(m.dataobj) > 0
    aseg = on_grid(nib.load(PM / root / f"sub-{sub}/{ver}/atlas/T1w_aseg_raw.nii.gz"), m)
    z = np.load(PUB / f"{tag}_rois.npz")
    ijk = z["ijk"].astype(int)
    names = [str(x) for x in z["roi"]]
    keep = ((ijk >= 0) & (ijk < np.array(m.shape))).all(1)
    parts = roi_parts()
    nn = {f: np.asarray(nib.load(WORK / f"{tag}_{f}_nn2mm.nii.gz").dataobj) for f in {x[0] for v in parts.values() for x in v}}
    t1 = {f: nib.load(WORK / f"{tag}_{f}_t1w.nii.gz") for f in nn}
    t1d = {f: np.asarray(i.dataobj) for f, i in t1.items()}
    rows, new = [], {"nn_2mm": {}, "overlap_2mm": {}}
    for roi, items in parts.items():
        pub = np.zeros(m.shape, bool)
        pub[tuple(ijk[keep & z["member"][:, names.index(roi)]].T)] = True
        a = np.zeros(m.shape, bool)
        b = np.zeros(m.shape, bool)
        for f, lab in items:
            a |= nn[f] == lab
            b |= overlap_to_grid(t1d[f] == lab, t1[f], m)
        new["nn_2mm"][roi], new["overlap_2mm"][roi] = a, b
        ref = np.isin(aseg, ASEG[roi]) if roi in ASEG else None
        for method, v in [("public", pub), ("nn_2mm", a), ("overlap_2mm", b)]:
            rec = dict(cohort=cohort, participant=f"sub-{sub}", roi=roi, method=method, n_in_grid=int(v.sum()), n_in_qc_mask=int((v & mask).sum()), dice_vs_public=round(dice(v, pub), 3))
            if ref is not None:
                d, zmm = best_z(v, ref)
                rec.update(n_aseg=int(ref.sum()), dice_vs_aseg=round(dice(v, ref), 3), best_z_mm=zmm, dice_best_z=round(d, 3))
            rows.append(rec)
    pd.DataFrame(rows).to_csv(WORK / f"{tag}_check.tsv", sep="\t", index=False)
    rn = list(parts)
    np.savez_compressed(WORK / f"{tag}_new_masks.npz", roi=np.array(rn), affine=m.affine, shape=np.array(m.shape), **{k: np.stack([new[k][r] for r in rn]) for k in new})
    print(tag, "done", flush=True)


def summary():
    want = [f"{c}_sub-{s}" for c, (_, _, subs) in COHORT.items() for s in subs.split()]
    missing = [t for t in want if not (WORK / f"{t}_check.tsv").exists()]
    if missing:
        raise ValueError(f"빠진 참가자: {missing}")
    T = pd.concat([pd.read_csv(WORK / f"{t}_check.tsv", sep="\t") for t in want])
    T.to_csv(MAN / "subcortex_rebuild_check.tsv", sep="\t", index=False)
    pd.set_option("display.width", 200)
    s3 = (T.cohort == "hk") & (T.participant == "sub-03")
    o = T[~s3]
    print("== 나머지 10명, ROI별 평균 ==")
    print(o.pivot_table(index="roi", columns="method", values="n_in_grid").round(0).astype(int).to_string())
    print(o[o.method != "public"].pivot_table(index="roi", columns="method", values="dice_vs_public").round(3).to_string())
    print(o[o.dice_vs_aseg.notna()].pivot_table(index="roi", columns="method", values="dice_vs_aseg").round(3).to_string())
    print("|best_z_mm| 최댓값:", o[o.best_z_mm.notna()].assign(a=lambda d: d.best_z_mm.abs()).groupby("method").a.max().to_dict())
    print("== HK sub-03 ==")
    print(T[s3].sort_values(["roi", "method"])[["roi", "method", "n_in_grid", "n_in_qc_mask", "dice_vs_public", "dice_vs_aseg", "best_z_mm", "dice_best_z"]].to_string(index=False))
    print("QC mask 안 최솟값:", T.groupby("method").n_in_qc_mask.min().to_dict())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cohort", choices=list(COHORT))
    ap.add_argument("--sub")
    ap.add_argument("--summary", action="store_true")
    a = ap.parse_args()
    if a.summary:
        summary()
    else:
        one(a.cohort, a.sub)


if __name__ == "__main__":
    main()
