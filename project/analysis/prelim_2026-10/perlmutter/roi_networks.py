#!/usr/bin/env python3
"""영역 묶음별 분석: 어느 뇌 영역이 정서 평정 예측을 담고, 그중 얼마가 캡션 경로로 재현되며, V-JEPA 2 위에 무엇을 더하나 (2026-10-28).

묶음 (469개 영역): Schaefer 400 의 7개 네트워크 (피질만), 소뇌 (Cereb7N 14), 편도체 (Tian S3 4), 해마 (8),
  그 밖 피질하 (40), 시상하부·뇌간 (3), 전체 (all).
조건 (피험자별 같은 행·fold, 모두 ridge. 34개 범주도 비율에 ridge 라 soft BCE 기준선보다 값이 조금 낮다)
  <묶음>:direct       : 묶음 → 정서
  <묶음>:via_caption  : 묶음 → 사람 캡션 임베딩 → 캡션 → 정서 모델 (학습 영상의 실제 캡션으로 학습한 모델)
  <묶음>+vjepa        : [묶음, V-JEPA 2] 를 열마다 표준화해 이어 붙인 입력 → 정서 (규제 강도 하나)
  vjepa_only, caption_only : 내용만 (기준)
뇌 → 캡션: 묶음별 캡션 임베딩 열의 r 평균, 같은 fold 안 영상 짝 구별 정확도 (우연 0.5).
주의: 묶음 크기가 3~93개 영역으로 달라 성능 비교는 크기의 영향을 받는다. r 비율은 성능 비율이며 공유 정보의 비율이 아니다.
출력: project/output/prelim_2026-10/08_roi_networks/
사용: python roi_networks.py --sub 01 [--max-folds 1] | --summarize
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import run_stage1 as rs  # noqa: E402

bb, cl = rs.bb, rs.cl
OUT = rs.OUT / "08_roi_networks"
S_NAME, V_NAME = "caption_human_mpnet", "vjepa2_vitg_final"
ORDER = ["Vis", "SomMot", "DorsAttn", "SalVentAttn", "Limbic", "Cont", "Default", "Cerebellum",
         "Amygdala", "Hippocampus", "OtherSubcortex", "Hypothal+Brainstem", "all"]


def roi_groups(sub):
    """load_subject 와 같은 유효 영역 순서로 각 열의 묶음 이름."""
    rows = pd.read_csv(rs.OUT / f"roi_blocks/Horikawa_sub-{sub}_roi469_rows.tsv", sep="\t")
    R = np.load(rs.OUT / f"roi_blocks/Horikawa_sub-{sub}_roi469_runz.npy")
    info = pd.read_csv(rs.OUT / f"roi_blocks/Horikawa_sub-{sub}_roi469_info.tsv", sep="\t")
    keep = ~rows.exclude_duplicate.astype(bool).values
    valid = info.roi_valid.values & np.isfinite(R[keep]).all(0)
    name, net = info.name.astype(str), info.network.values
    g = np.where(name.str.startswith("7Networks"), net, "").astype(object)
    g[name.str.startswith("Cereb7N").values] = "Cerebellum"
    g[name.str.contains("AMY").values] = "Amygdala"
    g[name.str.startswith("HIP").values] = "Hippocampus"
    g[(net == "Subcortex") & (g == "")] = "OtherSubcortex"
    g[np.isin(net, ["Hypothalamus", "Brainstem"])] = "Hypothal+Brainstem"
    assert (g != "").all(), "묶음 없는 영역"
    return g[valid]


def run_subject(sub, max_folds=None):
    t0 = time.time(); OUT.mkdir(parents=True, exist_ok=True)
    rows, fold, FB, Y34, names, Y14, meta = rs.load_subject(sub)
    vids = rows.video_id.values; B = FB["brain_roi469"]; pid = f"sub-{sub}"
    grp = roi_groups(sub); assert len(grp) == B.shape[1]
    cols = {gname: (np.ones(B.shape[1], bool) if gname == "all" else grp == gname) for gname in ORDER}
    F = rs.load_features(); S = F[S_NAME].loc[vids].values; V = F[V_NAME].loc[vids].values
    obs14 = np.isfinite(Y14).all(1)
    folds = np.unique(fold)[:max_folds] if max_folds else np.unique(fold)
    Zhat = {gname: np.full(S.shape, np.nan) for gname in ORDER}; acc = {gname: [] for gname in ORDER}; preds = []
    for f in folds:
        tr, te = fold != f, fold == f
        for gname, c in cols.items():                                     # 뇌 → 캡션 (Y 와 무관, fold 마다 한 번)
            Btr, Bte = cl.std_fit(B[tr][:, c], B[te][:, c])
            Zhat[gname][te], _ = bb.fit_predict_a14(Btr, S[tr], Bte, fold[tr])
            m = S[tr].mean(0); a = Zhat[gname][te] - m; b_ = S[te] - m
            a /= np.linalg.norm(a, axis=1, keepdims=True) + 1e-12; b_ /= np.linalg.norm(b_, axis=1, keepdims=True) + 1e-12
            Sm = a @ b_.T; dg = np.diag(Sm); acc[gname].append(np.mean([(dg[i] > np.delete(Sm[i], i)).mean() for i in range(len(Sm))]))
        for space, Y, mask, dims in [("A34", Y34, np.ones(len(fold), bool), names), ("A14", Y14, obs14, bb.DIMS14)]:
            trm, tem = tr & mask, te & mask; g = fold[trm]; Ytr = Y[trm]; idx = np.flatnonzero(tem); n = len(idx)
            conds = {}
            Str, Ste = cl.std_fit(S[trm], S[tem]); mu_s, sd_s = S[trm].mean(0), S[trm].std(0); sd_s[sd_s == 0] = 1
            Xvia = [Ste] + [(Zhat[gname][tem] - mu_s) / sd_s for gname in ORDER]   # 캡션 → 정서 모델 하나에 평가 입력만 바꿈
            P, _ = bb.fit_predict_a14(Str, Ytr, np.vstack(Xvia), g)
            conds["caption_only"] = P[:n]
            for i, gname in enumerate(ORDER):
                conds[f"{gname}:via_caption"] = P[(i + 1) * n:(i + 2) * n]
            Vtr, Vte = cl.std_fit(V[trm], V[tem]); conds["vjepa_only"], _ = bb.fit_predict_a14(Vtr, Ytr, Vte, g)
            for gname, c in cols.items():
                Btr, Bte = cl.std_fit(B[trm][:, c], B[tem][:, c])
                conds[f"{gname}:direct"], _ = bb.fit_predict_a14(Btr, Ytr, Bte, g)
                X = np.hstack([B[:, c], V]); Xtr, Xte = cl.std_fit(X[trm], X[tem])
                conds[f"{gname}+vjepa"], _ = bb.fit_predict_a14(Xtr, Ytr, Xte, g)
            mu = Ytr.mean(0)
            for cond, PP in conds.items():
                for j, d in enumerate(dims):
                    preds.append(pd.DataFrame(dict(participant_id=pid, video_id=vids[idx], outer_fold=int(f), input_condition=cond,
                                                   target_space=space, dimension=d, y_true=Y[idx, j], y_pred=PP[:, j], train_mean=mu[j])))
        print(f"  {pid} fold {f} 완료 ({time.time() - t0:.0f}초)", flush=True)
    pred = pd.concat(preds, ignore_index=True)
    pred.to_csv(OUT / f"predictions_{pid}.tsv.gz", sep="\t", index=False, float_format="%.6g")
    dim, _ = bb.evaluate(pred, sub)
    dim.to_csv(OUT / f"dimension_metrics_{pid}.tsv", sep="\t", index=False, float_format="%.5f")
    ev = np.isin(fold, folds)
    b2c = [dict(participant_id=pid, group=gname, n_rois=int(cols[gname].sum()),
                caption_r_mean=float(np.nanmean([bb.pearson(S[ev, j], Zhat[gname][ev, j]) for j in range(S.shape[1])])),
                pair_identification=float(np.mean(acc[gname]))) for gname in ORDER]
    pd.DataFrame(b2c).to_csv(OUT / f"brain_to_caption_{pid}.tsv", sep="\t", index=False, float_format="%.5f")
    (OUT / f"run_info_{pid}.json").write_text(json.dumps(dict(folds=[int(x) for x in folds], seconds=round(time.time() - t0),
                                                             n_rois={k: int(v.sum()) for k, v in cols.items()}), indent=1))
    print(pd.DataFrame(b2c).round(3).to_string(index=False)); print(f"{pid} 완료 ({time.time() - t0:.0f}초)")


def summarize():
    D = pd.concat([pd.read_csv(f, sep="\t") for f in sorted(OUT.glob("dimension_metrics_sub-*.tsv"))])
    C = pd.concat([pd.read_csv(f, sep="\t") for f in sorted(OUT.glob("brain_to_caption_sub-*.tsv"))])
    rows = []
    for space, g in D.groupby("target_space", sort=False):
        per = g.groupby(["participant_id", "input_condition"]).r_oof.mean().unstack()
        for gname in ORDER:
            d, v, p = per[f"{gname}:direct"], per[f"{gname}:via_caption"], per[f"{gname}+vjepa"] - per["vjepa_only"]
            cc = C[C.group == gname]
            rows.append(dict(target_space=space, group=gname, n_rois=int(cc.n_rois.median()),
                             r_direct=d.mean(), r_direct_min=d.min(), r_direct_max=d.max(),
                             r_via_caption=v.mean(), via_minus_direct=(v - d).mean(), n_subj_via_ge_direct=int((v >= d).sum()),
                             plus_vjepa_gain=p.mean(), plus_vjepa_gain_min=p.min(), n_subj_plus_gain=int((p > 0).sum()),
                             caption_r_mean=cc.caption_r_mean.mean(), pair_identification=cc.pair_identification.mean()))
        rows.append(dict(target_space=space, group="(내용만) caption / vjepa", r_direct=per.caption_only.mean(), r_via_caption=per.vjepa_only.mean()))
    S = pd.DataFrame(rows); S.to_csv(OUT / "summary.tsv", sep="\t", index=False, float_format="%.4f")
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    print(S.round(3).to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--sub"); ap.add_argument("--summarize", action="store_true")
    ap.add_argument("--max-folds", type=int, help="smoke test 용으로 앞의 fold 몇 개만")
    a = ap.parse_args()
    summarize() if a.summarize else run_subject(a.sub, a.max_folds)
