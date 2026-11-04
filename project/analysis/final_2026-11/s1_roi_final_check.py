#!/usr/bin/env python3
"""S1: 제안한 ROI 370개(피질 360개는 저자 지도, 피질하 10개는 11명 모두 새 mask)를 실제로 묶어 점검한다 (04 정할 것 5, 6, 7, 2026-11-04).

보는 것
  1) 뇌 배열의 열 번호 연결: ROI 좌표 → QC mask 열 번호가 배열의 voxel 수와 맞는지
  2) 공통 ROI: 11명 모두 QC mask 안에 voxel이 남는 ROI 수, 가장 적은 곳
  3) 피질과 피질하의 겹침, ROI별 voxel 수의 합과 고유 voxel 수(가중치 수)
  4) 시상하부와 측좌핵(BA34)의 위치: aseg에 같은 이름의 구조가 없어, 어느 aseg 구조에 드는지 저자 지도와 나란히 본다
     시상하부는 FreeSurfer VentralDC(28, 60) 안에 있는 구조이므로 VentralDC 비율을 본다
  5) 등록 이상 참가자가 없는지: aseg 8종의 참가자별 Dice 최솟값, 시상, 뇌간, 소뇌의 3차원 최적 이동(±3 voxel, 감기지 않음)
뇌 반응, 정서 점수, 모델 성능은 읽지 않는다.
출력: manifests/roi_final_check.tsv(참가자 × ROI), 나머지는 화면
"""
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd

PM = Path("/pscratch/sd/s/sjmoon")
REPO = PM / "EmoBrain"
MAN = REPO / "project/analysis/final_2026-11/manifests"
PUB = REPO / "project/output/final_2026-11/s1_original_rois"
NEW = REPO / "project/output/final_2026-11/s1_subcortex_rebuild"
COHORT = {"hk": ("Horikawa", "v3", "01 02 03 04 05"), "mc": ("MindCaptioning", "v2", "01 02 03 04 05 06")}
ASEG = {"hyppocampus": [17, 53], "thalamus": [10, 49], "amygdala": [18, 54], "caudate": [11, 50], "putamen": [12, 51], "pallidum": [13, 52], "brainstem": [16], "cerebellum": [7, 8, 46, 47]}
NAMES = {0: "밖", 2: "백질", 41: "백질", 3: "피질", 42: "피질", 4: "뇌실", 43: "뇌실", 5: "뇌실", 44: "뇌실", 7: "소뇌백질", 46: "소뇌백질", 8: "소뇌", 47: "소뇌", 10: "시상", 49: "시상", 11: "미상핵", 50: "미상핵", 12: "조가비핵", 51: "조가비핵", 13: "창백핵", 52: "창백핵", 14: "3뇌실", 16: "뇌간", 17: "해마", 53: "해마", 18: "편도체", 54: "편도체", 24: "CSF", 26: "측좌핵", 58: "측좌핵", 28: "VentralDC", 60: "VentralDC", 30: "혈관", 62: "혈관", 77: "백질저신호", 85: "시신경교차"}


def on_grid(img, m):
    ii = np.indices(m.shape).reshape(3, -1).T
    j = np.round(nib.affines.apply_affine(np.linalg.inv(img.affine), nib.affines.apply_affine(m.affine, ii))).astype(int)
    ok = ((j >= 0) & (j < np.array(img.shape[:3]))).all(1)
    a = np.asarray(img.dataobj)
    o = np.zeros(len(ii), a.dtype)
    o[ok] = a[tuple(j[ok].T)]
    return o.reshape(m.shape)


def dice(a, b):
    return float(2 * (a & b).sum() / max(1, a.sum() + b.sum()))


def shifted(points, ref, s):
    q = points + np.asarray(s)
    q = q[((q >= 0) & (q < np.array(ref.shape))).all(1)]
    return 2 * float(ref[tuple(q.T)].sum()) / max(1, len(q) + int(ref.sum()))


def best3d(v, ref):
    p = np.argwhere(v)
    best = (-1.0, (0, 0, 0))
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            for dz in range(-3, 4):
                d = shifted(p, ref, (dx, dy, dz))
                if d > best[0] or (d == best[0] and (dx, dy, dz) == (0, 0, 0)):
                    best = (d, (dx, dy, dz))
    return best


def top(v, aseg, k=4):
    lab, n = np.unique(aseg[v], return_counts=True)
    o = np.argsort(-n)[:k]
    return ", ".join(f"{NAMES.get(int(lab[i]), int(lab[i]))} {100 * n[i] / v.sum():.0f}%" for i in o)


def main():
    rows, part, loc = [], [], []
    for cohort, (root, ver, subs) in COHORT.items():
        for s in subs.split():
            tag = f"{cohort}_sub-{s}"
            m = nib.load(PM / root / f"sub-{s}/{ver}_qc/sub-{s}_mask_qc.nii.gz")
            mask = np.asarray(m.dataobj) > 0
            n_col = np.load(PM / root / f"sub-{s}/{ver}_qc/sub-{s}_blocks_common36_qc_runz.npy", mmap_mode="r").shape[1]
            assert int(mask.sum()) == n_col, (tag, int(mask.sum()), n_col)
            col = np.full(mask.shape, -1, np.int64)
            col[mask] = np.arange(n_col)
            aseg = on_grid(nib.load(PM / root / f"sub-{s}/{ver}/atlas/T1w_aseg_raw.nii.gz"), m)
            z = np.load(PUB / f"{tag}_rois.npz")
            ijk, M, names = z["ijk"].astype(int), z["member"], [str(x) for x in z["roi"]]
            keep = ((ijk >= 0) & (ijk < np.array(mask.shape))).all(1)
            nz = np.load(NEW / f"{tag}_new_masks.npz")
            assert tuple(nz["shape"]) == mask.shape and np.array_equal(nz["affine"], m.affine), tag
            new = {str(r): nz["overlap_2mm"][i] for i, r in enumerate(nz["roi"])}
            assert len(new) == 10 and all(n in names for n in new)
            used = np.zeros(mask.shape, np.int32)
            cortex_union, sub_union = np.zeros(mask.shape, bool), np.zeros(mask.shape, bool)
            for c, name in enumerate(names):
                if name in new:
                    vol, kind = new[name], "subcortex"
                    sub_union |= vol
                else:
                    vol = np.zeros(mask.shape, bool)
                    vol[tuple(ijk[keep & M[:, c]].T)] = True
                    kind = "cortex"
                    cortex_union |= vol
                cols = col[vol & mask]
                assert (cols >= 0).all() and len(np.unique(cols)) == len(cols)
                used += (vol & mask).astype(np.int32)
                rows.append(dict(cohort=cohort, participant=f"sub-{s}", roi=name, kind=kind, source="저자 지도" if kind == "cortex" else "새 mask(1 mm 중심 방식)", n_in_grid=int(vol.sum()), n_in_qc_mask=len(cols), frac_in_qc=round(len(cols) / max(1, int(vol.sum())), 3)))
            part.append(dict(tag=tag, n_col=n_col, sum_roi=int(used.sum()), unique=int((used > 0).sum()), overlap_cx_sub=int((cortex_union & sub_union & mask).sum()), rate_several=round(float((used > 1).sum() / max(1, (used > 0).sum())), 3)))
            dmin, bad = 1.0, []
            for roi, labs in ASEG.items():
                r = np.isin(aseg, labs)
                d = dice(new[roi], r)
                dmin = min(dmin, d)
                if roi in ["thalamus", "brainstem", "cerebellum"]:
                    b = best3d(new[roi], r)
                    bad.append(f"{roi[:4]}{b[1]}")
            part[-1].update(aseg_dice_min=round(dmin, 3), best3d=" ".join(bad))
            pubv = {}
            for roi in ["hypothalamus", "nuc_accum"]:
                v = np.zeros(mask.shape, bool)
                v[tuple(ijk[keep & M[:, names.index(roi)]].T)] = True
                pubv[roi] = v
            loc.append(dict(tag=tag, hypo_vdc_new=round(float(np.isin(aseg[new["hypothalamus"]], [28, 60]).mean()), 2), hypo_vdc_pub=round(float(np.isin(aseg[pubv["hypothalamus"]], [28, 60]).mean()), 2), hypo_new=top(new["hypothalamus"], aseg, 3), hypo_pub=top(pubv["hypothalamus"], aseg, 3), ba34_new=top(new["nuc_accum"], aseg, 3), ba34_pub=top(pubv["nuc_accum"], aseg, 3)))
            print(tag, "ok", flush=True)
    T = pd.DataFrame(rows)
    T.to_csv(MAN / "roi_final_check.tsv", sep="\t", index=False)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 60)
    print(pd.DataFrame(part).to_string(index=False))
    print(pd.DataFrame(loc).to_string(index=False))
    pid = T.cohort + T.participant
    good = T[T.n_in_qc_mask > 0].groupby("roi").size()
    print("참가자 수", pid.nunique(), "ROI 수", T.roi.nunique(), "11명 모두 QC 안에 voxel이 있는 ROI", int((good == 11).sum()))
    print("가장 적은 곳:\n", T.sort_values("n_in_qc_mask").head(6)[["cohort", "participant", "roi", "n_in_grid", "n_in_qc_mask", "frac_in_qc"]].to_string(index=False))
    r = T[(T.n_in_qc_mask >= 10) & (T.frac_in_qc >= 0.2)].groupby("roi").size()
    print("10개 이상, 20% 이상이면", int((r == 11).sum()), "개. 빠지는 ROI", sorted(set(T.roi) - set(r[r == 11].index)))
    print(T[T.kind == "subcortex"].groupby(["roi"]).n_in_qc_mask.agg(["min", "median", "max"]).astype(int).to_string())


if __name__ == "__main__":
    main()
