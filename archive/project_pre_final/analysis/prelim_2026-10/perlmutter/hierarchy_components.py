#!/usr/bin/env python3
"""정서 평정의 '시각에만 / 둘 다 / 캡션에만 / 나머지' 정보를 뇌 영역 묶음마다 디코딩하고 피질 위계 위에 놓기 (2026-10-31).

1. 자극 수준 분해 (뇌 없음, 분할 horikawa_rungroup6_v1 6겹): V = 시각 특징 묶음 (--visual), S = 정서·평가어 지운 사람 캡션.
     --visual "V-JEPA 2"          : V-JEPA 2 마지막 층
     --visual "V-JEPA 2 + DINOv2" : V-JEPA 2 와 DINOv2 (초당 2장). 둘 다 언어·라벨 감독 없이 학습한 시각 모델이라
                                    '캡션에만' 이 '시각 너머' 를 뜻하게 된다. CLIP 은 캡션과 맞추도록 학습해 언어 정보도 지우므로 넣지 않는다.
   시각 모델마다 ridge 예측을 만들고, ŷ_V 는 시각 예측들의 선형 결합, ŷ_S 는 캡션 예측의 보정, ŷ_VS 는 전부의 선형 결합 (차원마다, stacking).
     시각에만 = ŷ_VS − ŷ_S,  캡션에만 = ŷ_VS − ŷ_V,  둘 다 = ŷ_V + ŷ_S − ŷ_VS,  나머지 = y − ŷ_VS   (합 = y)
   34개 범주와 14개 차원 각각.
   중첩 구조: 뇌 디코딩의 평가 fold f 마다, 학습 영상과 평가 영상의 네 부분을 모두 fold f 를 뺀 자료로만 다시 만든다.
   (한 번의 OOF 분해를 모든 fold 에 같이 쓰면, 학습 영상의 '나머지' 가 평가 영상의 평정으로 학습된 자극 모델에서 나와
   평가 영상과 비슷한 학습 영상의 목표값이 반대로 밀리고, 디코딩 r 이 음으로 치우친다. 첫 실행에서 확인.)
   학습 영상: fold f 를 뺀 영상 안의 안쪽 OOF 예측에 보정·stacking 을 같은 자료로 맞춰 적용. 평가 영상: fold f 를 뺀 전체로 맞춘 예측에 같은 보정·stacking.
   평가 영상 쪽 예측을 fold 마다 모은 것이 한 번의 6겹 OOF 분해이며, 자극 수준 설명력 (stimulus_partition.tsv) 과 components_stimulus.npz 에 쓴다.
2. 뇌 디코딩: 피험자마다 영역 평균 (roi_blocks) 을 묶음별로 ridge (출력마다 규제 선택), 같은 6겹. 부분마다 디코딩 예측과 실제의 r 을
   차원 평균. 원래 평정 y 도 함께. r_mean 은 평가 fold 마다 예측·실제의 평균을 뺀 뒤의 r, r_pooled 는 빼지 않은 r.
묶음: 피질은 Schaefer 7 네트워크의 세부 영역 (예: Default_PFC), 피질하는 Tian S3 구조별, 시상하부·BNST·뇌간, 소뇌, 그리고 뇌 전체.
위계 순서: Vis, SomMot, DorsAttn, SalVentAttn, Limbic, Cont, Default (Margulies 2016 의 주 기울기 순서를 따른 관례), 그 뒤 피질하·소뇌.
출력: <OUT>/16_hierarchy/{components_stimulus.npz, stimulus_partition.tsv, group_component_r.tsv, summary.tsv}. 모두 visual 열로 시각 묶음을 구별하고,
  다른 시각 묶음의 기존 행은 남긴 채 이번 묶음의 행만 바꾼다.
사용: python hierarchy_components.py --visual "V-JEPA 2 + DINOv2" [--stimulus-only]
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, RidgeCV

sys.path.insert(0, str(Path(__file__).parent))
import feature_overlap as fo  # noqa: E402

rs = fo.rs
VISUAL = {"V-JEPA 2": ["vjepa2_vitg_final"], "V-JEPA 2 + DINOv2": ["vjepa2_vitg_final", "dinov22fps"]}
NET_RANK = {"Vis": 1, "SomMot": 2, "DorsAttn": 3, "SalVentAttn": 4, "Limbic": 5, "Cont": 6, "Default": 7}
CORTEX = {"Vis": ["Vis"], "SomMot": ["SomMot"], "DorsAttn_Post": ["DorsAttn_Post"], "DorsAttn_Front": ["DorsAttn_FEF", "DorsAttn_PrCv"],
          "SalVentAttn_Post": ["SalVentAttn_ParOper", "SalVentAttn_TempOcc", "SalVentAttn_TempOccPar", "SalVentAttn_PrC"],
          "SalVentAttn_FrontIns": ["SalVentAttn_FrOperIns", "SalVentAttn_PFCl"], "SalVentAttn_Med": ["SalVentAttn_Med"],
          "Limbic_OFC": ["Limbic_OFC"], "Limbic_TempPole": ["Limbic_TempPole"],
          "Cont_PFC": ["Cont_PFCl", "Cont_PFCmp", "Cont_PFCv", "Cont_OFC"], "Cont_ParTemp": ["Cont_Par", "Cont_Temp"], "Cont_Med": ["Cont_Cing", "Cont_pCun"],
          "Default_Par": ["Default_Par"], "Default_Temp": ["Default_Temp"], "Default_PFC": ["Default_PFC", "Default_PFCdPFCm", "Default_PFCv"],
          "Default_pCunPCC": ["Default_pCunPCC"]}
SUB = [("Amygdala", ["lAMY", "mAMY"]), ("Hippocampus", ["HIP-"]), ("Thalamus", ["THA-"]), ("Striatum", ["CAU-", "PUT-"]), ("NAc", ["NAc-"]),
       ("Pallidum", ["aGP", "pGP"]), ("Hypothal+BNST+Brainstem", ["Hypothalamus", "BNST", "Brain-Stem"])]
NAMES = ["시각에만", "캡션에만", "둘 다", "나머지", "평정 전체"]
ALPHAS = np.logspace(-1, 6, 15)


def roi_group_names(sub):
    """load_subject 와 같은 유효 영역 순서로 세부 묶음 이름."""
    rows = pd.read_csv(rs.OUT / f"roi_blocks/Horikawa_sub-{sub}_roi469_rows.tsv", sep="\t")
    R = np.load(rs.OUT / f"roi_blocks/Horikawa_sub-{sub}_roi469_runz.npy")
    info = pd.read_csv(rs.OUT / f"roi_blocks/Horikawa_sub-{sub}_roi469_info.tsv", sep="\t")
    keep = ~rows.exclude_duplicate.astype(bool).values
    valid = info.roi_valid.values & np.isfinite(R[keep]).all(0)
    out = []
    for nm in info.name.astype(str):
        g = ""
        if nm.startswith("7Networks"):
            sub_ = "_".join(nm.split("_")[2:-1])
            g = next(k for k, v in CORTEX.items() if sub_ in v)
        elif nm.startswith("Cereb7N"):
            g = "Cerebellum"
        else:
            g = next((k for k, pats in SUB if any(nm.startswith(p) or p in nm for p in pats)), "")
        assert g, nm
        out.append(g)
    return np.array(out, object)[valid]


def parts_from(yv, ys, yvs, Y):
    """NAMES 순서로 가로로 붙인다."""
    return np.hstack([yvs - ys, yvs - yv, yv + ys - yvs, Y - yvs, Y])


def fold_components(Y, Xvs, X_s, fold):
    """바깥 fold f 마다 (학습 영상의 네 부분, 평가 영상의 네 부분, 평가 영상의 (ŷ_V, ŷ_S, ŷ_VS)). 모두 fold f 를 뺀 자료로만 만든다."""
    pvs = [fo.stack_parts(X, Y, fold) for X in Xvs]; ps = fo.stack_parts(X_s, Y, fold)
    out = {}
    for f in np.unique(fold):
        tr, te = fold != f, fold == f
        v_in = [p[f][0] for p in pvs]; v_out = [p[f][1] for p in pvs]; s_in, s_out = ps[f]
        D = Y.shape[1]; Ytr = Y[tr]
        P = {k: (np.zeros((tr.sum(), D)), np.zeros((te.sum(), D))) for k in ("v", "s", "vs")}
        for d in range(D):
            Vi = np.column_stack([a[:, d] for a in v_in]); Vo = np.column_stack([a[:, d] for a in v_out])
            for k, A_in, A_out in [("v", Vi, Vo), ("s", s_in[:, [d]], s_out[:, [d]]), ("vs", np.c_[Vi, s_in[:, d]], np.c_[Vo, s_out[:, d]])]:
                lr = LinearRegression().fit(A_in, Ytr[:, d])
                P[k][0][:, d] = lr.predict(A_in); P[k][1][:, d] = lr.predict(A_out)
        out[f] = (parts_from(P["v"][0], P["s"][0], P["vs"][0], Ytr), parts_from(P["v"][1], P["s"][1], P["vs"][1], Y[te]),
                  (P["v"][1], P["s"][1], P["vs"][1]))
    return out


def merge_write(new, path, key="visual", vis=None, **kw):
    """기존 표에서 이번 시각 묶음의 행만 바꿔 쓴다 (visual 열이 없던 옛 표는 V-JEPA 2 로 본다)."""
    if path.exists():
        old = pd.read_csv(path, sep="\t")
        if key not in old.columns:
            old.insert(0, key, "V-JEPA 2")
        new = pd.concat([old[old[key] != vis], new], ignore_index=True)
    new.to_csv(path, sep="\t", index=False, **kw)
    return new


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--visual", default="V-JEPA 2", choices=list(VISUAL))
    ap.add_argument("--stimulus-only", action="store_true", help="자극 수준 분해만 (뇌 디코딩 생략)"); a = ap.parse_args()
    od = rs.OUT / "16_hierarchy"; od.mkdir(parents=True, exist_ok=True)
    split = pd.read_csv(rs.bb.SPLIT, sep="\t")
    split = split[split.analysis_row & ~split.exclude_duplicate & (split.video_id <= 2185)].set_index("video_id")
    vids = split.index.values; fold = split.fold.values; F = rs.load_features()
    cats, Y34, Y14 = rs.cl.labels_for(vids)
    Xvs = [F[n].loc[vids].values.astype(float) for n in VISUAL[a.visual]]; Xs = F["caption_human_noemo_mpnet"].loc[vids].values.astype(float)
    ok14 = np.isfinite(Y14).all(1)
    spaces = {"A34": (vids, fold, Y34, Xvs, Xs), "A14": (vids[ok14], fold[ok14], Y14[ok14], [X[ok14] for X in Xvs], Xs[ok14])}
    desc, FC, part = {}, {}, []
    for sp, (v, f, Y, A, B) in spaces.items():
        D = Y.shape[1]; FC[sp] = fold_components(Y, A, B, f)
        C = np.zeros((len(v), len(NAMES) * D)); yhat = {k: np.zeros_like(Y) for k in ("v", "s", "vs")}; base = np.zeros_like(Y)
        for ff, (_, te_parts, (pv, pss, pvs)) in FC[sp].items():
            te = f == ff; C[te] = te_parts; yhat["v"][te], yhat["s"][te], yhat["vs"][te] = pv, pss, pvs; base[te] = Y[f != ff].mean(0)
        desc.update({f"{a.visual}__{sp}__{k}": C[:, i * D:(i + 1) * D] for i, k in enumerate(NAMES)}); desc[f"{a.visual}__{sp}__vids"] = v
        r2 = {k: np.mean(1 - ((Y - p) ** 2).sum(0) / ((Y - base) ** 2).sum(0)) for k, p in yhat.items()}
        part.append(dict(visual=a.visual, space=sp, r2_visual=r2["v"], r2_caption=r2["s"], r2_both=r2["vs"], visual_only=r2["vs"] - r2["s"],
                         caption_only=r2["vs"] - r2["v"], shared=r2["v"] + r2["s"] - r2["vs"]))
        print(sp, "자극 수준", {k: round(x, 4) for k, x in part[-1].items() if k not in ("visual", "space")}, flush=True)
    merge_write(pd.DataFrame(part), od / "stimulus_partition.tsv", vis=a.visual, float_format="%.4f")
    npz = od / "components_stimulus.npz"
    if npz.exists():
        old = dict(np.load(npz, allow_pickle=True))
        old = {(k if k.count("__") == 2 else f"V-JEPA 2__{k}"): x for k, x in old.items() if not k.startswith(f"{a.visual}__")}
        desc = {**old, **desc}
    np.savez(npz, **desc)
    if a.stimulus_only:
        return
    rows = []
    for sub in ["01", "02", "03", "04", "05"]:
        rws, bfold, FB, *_ = rs.load_subject(sub)
        B = FB["brain_roi469"]; groups = roi_group_names(sub); assert len(groups) == B.shape[1]
        plan = {}  # 공간 → fold → (학습 행, 평가 행, 학습 목표, 평가 목표)
        for sp, (v, f_sp, Y, *_) in spaces.items():
            pos = {x: i for i, x in enumerate(v)}; sidx = np.array([pos.get(x, -1) for x in rws.video_id.values]); use = sidx >= 0
            assert (f_sp[sidx[use]] == bfold[use]).all(), "자극 fold 와 뇌 fold 불일치"
            plan[sp] = {}
            for f in np.unique(f_sp):
                inv_tr = np.full(len(v), -1); inv_tr[f_sp != f] = np.arange((f_sp != f).sum())
                inv_te = np.full(len(v), -1); inv_te[f_sp == f] = np.arange((f_sp == f).sum())
                rtr, rte = use & (bfold != f), use & (bfold == f)
                plan[sp][f] = (rtr, rte, FC[sp][f][0][inv_tr[sidx[rtr]]], FC[sp][f][1][inv_te[sidx[rte]]])
        for g in list(dict.fromkeys(groups)) + ["Whole brain"]:
            Xg = B if g == "Whole brain" else B[:, groups == g]
            for sp, folds in plan.items():
                D = spaces[sp][2].shape[1]
                T = np.full((len(B), len(NAMES) * D), np.nan); P = T.copy()
                for f, (rtr, rte, Ttr, Tte) in folds.items():
                    mu, sd = Xg[rtr].mean(0), Xg[rtr].std(0); sd[sd == 0] = 1
                    P[rte] = RidgeCV(alphas=ALPHAS, alpha_per_target=True).fit((Xg[rtr] - mu) / sd, Ttr).predict((Xg[rte] - mu) / sd)
                    T[rte] = Tte
                okr = np.isfinite(T).all(1)
                Tc, Pc = T.copy(), P.copy()  # fold 안 평균을 뺀 r
                for f in folds:
                    m = (bfold == f) & okr; Tc[m] -= Tc[m].mean(0); Pc[m] -= Pc[m].mean(0)
                cor = lambda A, Bm, j: np.corrcoef(A[okr, j], Bm[okr, j])[0, 1]
                for ci, k in enumerate(NAMES):
                    js = [j for j in range(ci * D, (ci + 1) * D) if T[okr, j].std() > 0]
                    rows.append(dict(visual=a.visual, participant=f"sub-{sub}", group=g, n_roi=int(Xg.shape[1]), space=sp, component=k,
                                     r_mean=np.nanmean([cor(Tc, Pc, j) for j in js]), r_pooled=np.nanmean([cor(T, P, j) for j in js]),
                                     r_arousal=(cor(Tc, Pc, ci * D + 1) if sp == "A14" else np.nan)))
            print(sub, g, flush=True)
    R = merge_write(pd.DataFrame(rows), od / "group_component_r.tsv", vis=a.visual, float_format="%.4f")
    S = R.groupby(["visual", "space", "group", "component"]).agg(
        r_mean=("r_mean", "mean"), r_sd=("r_mean", "std"), n_pos=("r_mean", lambda x: int((x > 0).sum())),
        r_pooled=("r_pooled", "mean"), r_arousal=("r_arousal", "mean"), n_roi=("n_roi", "mean")).reset_index()
    S["net_rank"] = S.group.map(lambda g: NET_RANK.get(g.split("_")[0], np.nan))
    S.to_csv(od / "summary.tsv", sep="\t", index=False, float_format="%.4f")
    print(S[(S.space == "A34") & (S.visual == a.visual)].pivot(index="group", columns="component", values="r_mean").round(3).to_string())


if __name__ == "__main__":
    main()
