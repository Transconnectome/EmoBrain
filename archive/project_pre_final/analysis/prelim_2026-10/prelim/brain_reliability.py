#!/usr/bin/env python3
"""EmoBrain 선행 점검 0-8: 같은 영상에 대한 뇌 반응이 얼마나 안정적인가 (라벨은 쓰지 않음, 2026-10-22).

--subject : 피험자 하나
   1) 기본 지도 469개 영역 평균 블록 반응을 만들어 저장 (나중 예측 분석 입력으로도 씀)
   2) 피험자 안 반복 신뢰도
      Horikawa      : 같은 내용 영상 15쌍(두 번 제시)의 반응 패턴 상관. 같은 쌍 vs 다른 쌍, 15개 중 짝 찾기 정확도
      MindCaptioning: 시험 영상 72개 × 5회. voxel·영역별 홀수/짝수 회차 평균의 상관(Spearman-Brown 보정), 72개 중 짝 찾기 정확도
--group   : 같은 데이터의 피험자끼리 영역 반응이 얼마나 같은가 (피험자 간 일치도: 한 명 vs 나머지 평균의 상관)
   Horikawa 는 5명 제시 순서가 같아서, 일치도에는 영상 효과와 순서 효과가 함께 들어간다.
입력: response_t1w/sub-XX/{v3_qc|v2_qc} 블록(run 안 z), mask_qc, 기본 지도
출력: /storage/bigdata/EmoBrain_response/prelim/reliability/, roi_blocks/
"""
import argparse
import json
import time
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd

OUT = Path("/storage/bigdata/EmoBrain_response/prelim")
ATLAS = "Schaefer400x7N+TianS3+HypoBNST+Cereb7N+Brainstem"
DS = {"horikawa": ("Horikawa", "v3", ["01", "02", "03", "04", "05"]),
      "mindcaptioning": ("MindCaptioning", "v2", ["01", "02", "03", "04", "05", "06"])}


def corr_rows(A, B):
    """행끼리 상관 행렬 (A: n×p, B: m×p) → n×m."""
    A = A - A.mean(1, keepdims=True); B = B - B.mean(1, keepdims=True)
    A /= np.linalg.norm(A, axis=1, keepdims=True) + 1e-12; B /= np.linalg.norm(B, axis=1, keepdims=True) + 1e-12
    return A @ B.T


def corr_cols(A, B):
    """열끼리 상관 (같은 열 번호끼리)."""
    A = A - A.mean(0); B = B - B.mean(0)
    den = np.sqrt((A * A).sum(0) * (B * B).sum(0))
    return np.where(den > 0, (A * B).sum(0) / np.where(den > 0, den, 1), np.nan)


def ident_acc(S):
    """정사각 상관 행렬에서 대각(같은 영상)이 그 행의 다른 값보다 큰 비율 (쌍 비교 정확도, 기준 0.5)."""
    n = S.shape[0]; d = np.diag(S)
    return float(np.mean([(d[i] > np.delete(S[i], i)).mean() for i in range(n)]))


def run_subject(ds, sub):
    t0 = time.time(); root, ver, _ = DS[ds]
    base = Path(f"/storage/bigdata/{root}/response_t1w/sub-{sub}")
    q = base / f"{ver}_qc"
    T = pd.read_csv(q / f"sub-{sub}_samples_qc_usable.tsv", sep="\t")
    Y = np.load(q / f"sub-{sub}_blocks_common36_qc_runz.npy", mmap_mode="r")
    mimg = nib.load(str(q / f"sub-{sub}_mask_qc.nii.gz")); M = np.asarray(mimg.dataobj) > 0
    aimg = nib.load(str(base / ver / "atlas" / f"sub-{sub}_space-T1w_atlas-{ATLAS}_dseg.nii.gz"))
    assert aimg.shape == M.shape and np.allclose(aimg.affine, mimg.affine, atol=1e-4), "지도 격자 다름"
    assert Y.shape == (len(T), M.sum()), f"모양 불일치 {Y.shape} vs {(len(T), M.sum())}"
    lab = pd.read_csv(base / ver / "atlas" / f"sub-{sub}_atlas-{ATLAS}_labels.tsv", sep="\t")
    valid = pd.read_csv(q / f"sub-{sub}_roi_valid.tsv", sep="\t"); valid = valid[valid.atlas == ATLAS].set_index("roi_id")
    roi_of = np.asarray(aimg.dataobj)[M].astype(int)
    ids = lab.roi_id.values
    order = np.argsort(roi_of, kind="stable"); sorted_roi = roi_of[order]
    starts = np.searchsorted(sorted_roi, ids); ends = np.searchsorted(sorted_roi, ids, side="right"); nvox = ends - starts
    # 1) 영역 평균 (voxel 0개 영역은 NaN)
    R = np.full((len(T), len(ids)), np.nan, np.float32)
    for i0 in range(0, len(T), 64):
        sl = slice(i0, min(i0 + 64, len(T)))
        X = np.asarray(Y[sl], np.float64)[:, order]
        cs = np.concatenate([np.zeros((X.shape[0], 1)), np.cumsum(X, 1)], 1)
        with np.errstate(invalid="ignore", divide="ignore"):
            R[sl] = ((cs[:, ends] - cs[:, starts]) / np.where(nvox > 0, nvox, np.nan)).astype(np.float32)
    od = OUT / "roi_blocks"; od.mkdir(parents=True, exist_ok=True)
    np.save(od / f"{root}_sub-{sub}_roi469_runz.npy", R)
    info = lab[["roi_id", "name", "hemi", "network"]].copy(); info["n_vox_qc"] = nvox
    info["roi_valid"] = [bool(valid.roi_valid.get(r, False)) for r in ids]
    info.to_csv(od / f"{root}_sub-{sub}_roi469_info.tsv", sep="\t", index=False)
    T.to_csv(od / f"{root}_sub-{sub}_roi469_rows.tsv", sep="\t", index=False)
    net = info.network.values
    summ = dict(데이터=root, 피험자=f"sub-{sub}", 블록수=len(T), 유효영역수=int(info.roi_valid.sum()))

    # 2) 피험자 안 반복 신뢰도
    rd = OUT / "reliability"; rd.mkdir(parents=True, exist_ok=True)
    if ds == "horikawa":
        g = T.groupby("content_id").filter(lambda x: len(x) == 2).sort_values(["content_id", "onset_sec"])
        first = g[~g.exclude_duplicate.astype(bool)]; second = g[g.exclude_duplicate.astype(bool)]
        first = first[first.content_id.isin(second.content_id)].sort_values("content_id")
        second = second[second.content_id.isin(first.content_id)].sort_values("content_id")
        A = np.asarray(Y[first.index.values], np.float64); B = np.asarray(Y[second.index.values], np.float64)
        S = corr_rows(A, B); Sr = corr_rows(np.nan_to_num(R[first.index.values]), np.nan_to_num(R[second.index.values]))
        off = S[~np.eye(len(S), dtype=bool)]
        summ.update(반복쌍수=int(len(S)), 같은쌍_패턴상관_평균=float(np.diag(S).mean()), 다른쌍_패턴상관_평균=float(off.mean()),
                    짝찾기정확도_voxel=ident_acc(S), 짝찾기정확도_영역=ident_acc(Sr))
        # 네트워크별 같은 쌍 vs 다른 쌍 (영역 단위 voxel 로 계산)
        netres = {}
        for n_ in np.unique(net):
            cols = np.concatenate([order[starts[k]:ends[k]] for k in np.flatnonzero(net == n_)])
            if len(cols) < 50:
                continue
            Sn = corr_rows(A[:, cols], B[:, cols])
            netres[n_] = dict(같은쌍=float(np.diag(Sn).mean()), 다른쌍=float(Sn[~np.eye(len(Sn), dtype=bool)].mean()), 짝찾기=ident_acc(Sn), voxel수=int(len(cols)))
        summ["네트워크별_반복"] = netres
    else:
        te = T[T.part == "test"].copy()
        te["rep_i"] = te.groupby("video_id").cumcount() + 1
        vids = sorted(te.video_id.unique()); odd, even = [], []
        for v in vids:
            r = te[te.video_id == v]
            o = r[r.rep_i % 2 == 1].index.values; e = r[r.rep_i % 2 == 0].index.values
            odd.append(o); even.append(e)
        keep = [i for i in range(len(vids)) if len(odd[i]) and len(even[i])]
        vids = [vids[i] for i in keep]; odd = [odd[i] for i in keep]; even = [even[i] for i in keep]
        Ao = np.stack([np.asarray(Y[ix], np.float64).mean(0) for ix in odd]); Ae = np.stack([np.asarray(Y[ix], np.float64).mean(0) for ix in even])
        rv = corr_cols(Ao, Ae); rv_sb = 2 * rv / (1 + rv)
        Ro = np.stack([np.nanmean(R[ix], 0) for ix in odd]); Re = np.stack([np.nanmean(R[ix], 0) for ix in even])
        rr = corr_cols(Ro, Re); rr_sb = 2 * rr / (1 + rr)
        S = corr_rows(Ao, Ae)
        pd.DataFrame({"roi_id": ids, "name": info.name, "network": net, "반쪽상관": rr, "보정신뢰도": rr_sb}).to_csv(
            rd / f"{root}_sub-{sub}_test_repeat_roi.tsv", sep="\t", index=False, float_format="%.4f")
        vol = np.zeros(M.shape, np.float32); vol[M] = np.nan_to_num(rv_sb)
        nib.save(nib.Nifti1Image(vol, mimg.affine), str(rd / f"{root}_sub-{sub}_test_repeat_voxel_reliability.nii.gz"))
        vox_net = np.empty(M.sum(), object); vox_net[:] = "지도밖"
        for k, n_ in enumerate(net):
            vox_net[order[starts[k]:ends[k]]] = n_
        summ.update(시험영상수=len(vids), voxel신뢰도_중앙값=float(np.nanmedian(rv_sb)), voxel신뢰도_0p3넘는비율=float(np.nanmean(rv_sb > 0.3)),
                    영역신뢰도_중앙값=float(np.nanmedian(rr_sb)), 짝찾기정확도_voxel=ident_acc(S),
                    네트워크별_voxel신뢰도_중앙값={n_: float(np.nanmedian(rv_sb[vox_net == n_])) for n_ in np.unique(vox_net)})
    summ["초"] = round(time.time() - t0)
    (rd / f"{root}_sub-{sub}_within.json").write_text(json.dumps(summ, ensure_ascii=False, indent=1))
    print(json.dumps(summ, ensure_ascii=False, indent=1))


def run_group(ds):
    root, ver, subs = DS[ds]; od = OUT / "roi_blocks"; rd = OUT / "reliability"; rd.mkdir(parents=True, exist_ok=True)
    mats, info = {}, None
    for s in subs:
        T = pd.read_csv(od / f"{root}_sub-{s}_roi469_rows.tsv", sep="\t"); R = np.load(od / f"{root}_sub-{s}_roi469_runz.npy")
        inf = pd.read_csv(od / f"{root}_sub-{s}_roi469_info.tsv", sep="\t"); info = inf if info is None else info
        use = np.ones(len(T), bool)
        if "exclude_duplicate" in T:
            use &= ~T.exclude_duplicate.astype(bool).values
        if "part" in T and ds == "mindcaptioning":
            use &= (T.part == "train").values & ~T.test_video_in_train_session.astype(bool).values
        df = pd.DataFrame(R[use], index=T.video_id.values[use]); df = df[~df.index.duplicated()]
        df.loc[:, ~inf.roi_valid.values] = np.nan
        mats[s] = df
    common = sorted(set.intersection(*[set(m.index) for m in mats.values()]))
    A = np.stack([mats[s].loc[common].values for s in subs])          # 피험자 × 영상 × 영역
    isc = np.full((len(subs), A.shape[2]), np.nan)
    for i in range(len(subs)):
        others = np.nanmean(np.delete(A, i, 0), 0)
        isc[i] = corr_cols(A[i], others)
    tab = info[["roi_id", "name", "hemi", "network"]].copy()
    for i, s in enumerate(subs):
        tab[f"sub-{s}"] = isc[i]
    tab["피험자간일치도_평균"] = np.nanmean(isc, 0)
    tab.to_csv(rd / f"{root}_isc_roi469.tsv", sep="\t", index=False, float_format="%.4f")
    netsum = tab.groupby("network").피험자간일치도_평균.agg(["median", "max", "count"]).sort_values("median", ascending=False)
    summ = dict(데이터=root, 공통영상수=len(common), 피험자=subs, 영역일치도_중앙값=float(np.nanmedian(tab.피험자간일치도_평균)),
                영역일치도_0p1넘는영역수=int((tab.피험자간일치도_평균 > 0.1).sum()),
                상위10영역={r.name: round(r.피험자간일치도_평균, 3) for r in tab.sort_values("피험자간일치도_평균", ascending=False).head(10).itertuples()},
                네트워크별_중앙값={k: round(v, 3) for k, v in netsum["median"].items()})
    (rd / f"{root}_isc_summary.json").write_text(json.dumps(summ, ensure_ascii=False, indent=1))
    print(json.dumps(summ, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", action="store_true"); ap.add_argument("--group", action="store_true")
    ap.add_argument("--dataset"); ap.add_argument("--sub")
    a = ap.parse_args()
    if a.subject:
        run_subject(a.dataset, a.sub)
    elif a.group:
        run_group(a.dataset)
