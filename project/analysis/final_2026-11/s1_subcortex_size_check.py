#!/usr/bin/env python3
"""S1: 저자 공개 피질하 mask가 새 mask보다 큰 이유가 경계 처리인지 잰다 (04 정할 것 7, 2026-11-04).

궁금한 것: 저자 키 이름은 pickatlas_r_w...로, 지도를 개인 공간으로 옮긴 뒤(w) 기능 영상 격자로 다시 보간한(r) 것으로 보인다.
이진 지도를 선형 보간하면 경계 voxel이 0과 1 사이 값을 갖고, 어느 문턱에서 자르느냐에 따라 크기가 달라진다.
그래서 같은 변환으로 ROI를 선형 보간한 뒤 문턱을 바꿔 가며 voxel 수와 공개 mask와의 Dice를 본다.
저자의 실제 문턱은 공개 코드에 없다. 이 표는 설명을 확인하는 진단이고, 문턱을 고르는 근거로 자동으로 쓰지 않는다. 뇌 반응은 읽지 않는다.
입력: s1_subcortex_rebuild의 변환(<work>/<tag>_1Warp.nii.gz, _0GenericAffine.mat), s1_original_rois의 npz
출력: manifests/subcortex_size_check.tsv
"""
import argparse
import subprocess
import tempfile
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
import scipy.ndimage as ndi

PM = Path("/pscratch/sd/s/sjmoon")
REPO = PM / "EmoBrain"
MAN = REPO / "project/analysis/final_2026-11/manifests"
PUB = REPO / "project/output/final_2026-11/s1_original_rois"
WORK = REPO / "project/output/final_2026-11/s1_subcortex_rebuild"
ATLAS = PM / "atlas_sources/wfu_pickatlas/official/WFU_PickAtlas_3.0.5b/wfu_pickatlas/MNI_atlas_templates"
COHORT = {"hk": ("Horikawa", "v3", "01 02 03 04 05"), "mc": ("MindCaptioning", "v2", "01 02 03 04 05 06")}
THRESHOLDS = [0.5, 0.25, 0.1, 0.001]  # 0.001은 "조금이라도 걸치면 포함"을 숫자로 쓴 것이다.
ASEG = {"hyppocampus": [17, 53], "thalamus": [10, 49], "amygdala": [18, 54], "caudate": [11, 50], "putamen": [12, 51], "pallidum": [13, 52], "brainstem": [16], "cerebellum": [7, 8, 46, 47]}
IMG = "docker:nipreps/fmriprep:25.0.0"


def labels(txt):
    out = {}
    for line in open(txt, errors="ignore"):
        p = [s.strip() for s in line.strip().split("\t") if s.strip()]
        if len(p) >= 2 and p[0].isdigit():
            out[p[1].replace(" ", "_")] = int(p[0])
    return out


def roi_binary():
    t = pd.read_csv(MAN / "subcortex_definition.tsv", sep="\t")
    out = {}
    for _, r in t.iterrows():
        v = None
        for k in r.original_keys.split(","):
            body = k.replace("pickatlas_r_w", "")
            if body.startswith("aal_MNI_V4_"):
                file, lab = "aal_MNI_V4", body[len("aal_MNI_V4_"):]
            else:
                file = "_".join(body.split("_")[:2])
                lab = body[len(file) + 1:]
            img = nib.load(ATLAS / f"{file}.nii")
            b = np.asarray(img.dataobj) == labels(ATLAS / f"{file}.txt")[lab]
            v = b if v is None else (v | b)
        out[r.roi] = (v, img.affine)
    return out


def dice(a, b):
    return float(2 * (a & b).sum() / max(1, a.sum() + b.sum()))


def on_grid(img, m):
    ii = np.indices(m.shape).reshape(3, -1).T
    j = np.round(nib.affines.apply_affine(np.linalg.inv(img.affine), nib.affines.apply_affine(m.affine, ii))).astype(int)
    ok = ((j >= 0) & (j < np.array(img.shape[:3]))).all(1)
    a = np.asarray(img.dataobj)
    o = np.zeros(len(ii), a.dtype)
    o[ok] = a[tuple(j[ok].T)]
    return o.reshape(m.shape)


def best_z(v, ref):
    p = np.argwhere(v)
    best = (-1.0, 0)
    for k in range(-20, 21):
        q = p + np.array([0, 0, k])
        q = q[(q >= 0).all(1) & (q < np.array(ref.shape)).all(1)]
        d = 2 * float(ref[tuple(q.T)].sum()) / max(1, len(q) + int(ref.sum()))
        if d > best[0] or (d == best[0] and k == 0):
            best = (d, 2 * k)
    return best


def one(cohort, sub):
    root, ver, _ = COHORT[cohort]
    tag = f"{cohort}_sub-{sub}"
    ref = PM / root / f"sub-{sub}/{ver}_qc/sub-{sub}_mask_qc.nii.gz"
    m = nib.load(ref)
    mask = np.asarray(m.dataobj) > 0
    aseg = on_grid(nib.load(PM / root / f"sub-{sub}/{ver}/atlas/T1w_aseg_raw.nii.gz"), m)
    z = np.load(PUB / f"{tag}_rois.npz")
    ijk = z["ijk"].astype(int)
    names = [str(x) for x in z["roi"]]
    keep = ((ijk >= 0) & (ijk < np.array(m.shape))).all(1)
    rois = roi_binary()
    rows = []
    with tempfile.TemporaryDirectory(dir=WORK) as td:
        cmds = []
        for roi, (v, aff) in rois.items():
            nib.save(nib.Nifti1Image(v.astype(np.float32), aff), f"{td}/{roi}.nii.gz")
            cmds.append(f'antsApplyTransforms -d 3 -i {td}/{roi}.nii.gz -r {ref} -t {WORK}/{tag}_1Warp.nii.gz -t {WORK}/{tag}_0GenericAffine.mat -n Linear -o {td}/{roi}_lin.nii.gz')
        subprocess.run(["shifter", f"--image={IMG}", "bash", "-c", " && ".join(cmds)], check=True, stdout=subprocess.DEVNULL)
        for roi, (v, _) in rois.items():
            pub = np.zeros(m.shape, bool)
            pub[tuple(ijk[keep & z["member"][:, names.index(roi)]].T)] = True
            lin = np.asarray(nib.load(f"{td}/{roi}_lin.nii.gz").dataobj)
            rec = dict(cohort=cohort, participant=f"sub-{sub}", roi=roi, n_atlas_2mm=int(v.sum()), n_atlas_dilated_1=int(ndi.binary_dilation(v, ndi.generate_binary_structure(3, 3)).sum()), n_public=int(pub.sum()))
            for th in THRESHOLDS:
                w = lin >= th
                rec[f"n_ge_{th}"] = int(w.sum())
                rec[f"dice_public_ge_{th}"] = round(dice(w, pub), 3)
                rec[f"n_qc_ge_{th}"] = int((w & mask).sum())
                if roi in ASEG:
                    rec[f"dice_aseg_ge_{th}"] = round(dice(w, np.isin(aseg, ASEG[roi])), 3)
            if roi in ASEG:
                r = np.isin(aseg, ASEG[roi])
                rec["dice_aseg_public"] = round(dice(pub, r), 3)
                rec["best_z_mm_ge_0.001"] = best_z(lin >= 0.001, r)[1]
            rows.append(rec)
    pd.DataFrame(rows).to_csv(WORK / f"{tag}_size.tsv", sep="\t", index=False)
    print(tag, "done", flush=True)


def summary():
    want = [f"{c}_sub-{s}" for c, (_, _, subs) in COHORT.items() for s in subs.split()]
    missing = [t for t in want if not (WORK / f"{t}_size.tsv").exists()]
    if missing:
        raise ValueError(f"빠진 참가자: {missing}")
    T = pd.concat([pd.read_csv(WORK / f"{t}_size.tsv", sep="\t") for t in want])
    T.to_csv(MAN / "subcortex_size_check.tsv", sep="\t", index=False)
    pd.set_option("display.width", 220)
    o = T[~((T.cohort == "hk") & (T.participant == "sub-03"))]
    cols = ["n_atlas_2mm", "n_atlas_dilated_1", "n_public"] + [f"n_ge_{t}" for t in THRESHOLDS]
    g = o.groupby("roi")[cols].mean().round(1).sort_values("n_public")
    print(g.to_string())
    print("크기 비(문턱별 ÷ 공개):")
    print(g[[f"n_ge_{t}" for t in THRESHOLDS]].div(g.n_public, axis=0).round(2).to_string())
    print("공개 mask와 Dice:")
    print(o.groupby("roi")[[f"dice_public_ge_{t}" for t in THRESHOLDS]].mean().round(3).reindex(g.index).to_string())
    print("10개 ROI 평균 Dice:", o[[f"dice_public_ge_{t}" for t in THRESHOLDS]].mean().round(3).to_dict())
    a = o[o.dice_aseg_public.notna()]
    print("aseg와 Dice (10명, 8종 ROI별 평균):")
    print(a.groupby("roi")[["dice_aseg_public"] + [f"dice_aseg_ge_{t}" for t in THRESHOLDS]].mean().round(3).to_string())
    print("8종 평균:", a[["dice_aseg_public"] + [f"dice_aseg_ge_{t}" for t in THRESHOLDS]].groupby(a.roi).mean().mean().round(3).to_dict())
    print("|best_z_mm| >0 규칙, 10명:", a["best_z_mm_ge_0.001"].abs().value_counts().sort_index().to_dict())
    s3 = T[(T.cohort == "hk") & (T.participant == "sub-03")]
    print("HK sub-03:")
    print(s3[["roi", "n_public", "n_ge_0.001", "n_qc_ge_0.001", "dice_aseg_public", "dice_aseg_ge_0.001", "best_z_mm_ge_0.001"]].to_string(index=False))
    print("QC 안 최솟값(>0 규칙):", int(T["n_qc_ge_0.001"].min()), "시상하부 10명 평균 QC 안:", round(o[o.roi == "hypothalamus"]["n_qc_ge_0.001"].mean(), 1))


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
