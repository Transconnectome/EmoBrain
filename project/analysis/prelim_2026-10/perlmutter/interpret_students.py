#!/usr/bin/env python3
"""student 해석: 피험자·감정별 차이, 영상별 변화, 네트워크별 내용/잔차 분해, 디코더 가중치 (2026-10-28).

모두 저장된 예측·가중치만 읽는다 (모델 재학습 없음).
  --subject-emotion : soft BCE student (34개 범주) 의 피험자 × 범주 Δr, 영상 bootstrap 95% CI, 내용/잔차 성분 분해
  --videos          : 영상마다 34개 범주 예측 오차(제곱합)의 변화. 5명 공통으로 좋아지거나 나빠진 영상과 사람 캡션
  --networks        : 영역 묶음별 뇌 단독(ridge) 예측의 내용/잔차 성분 분해
  --weights         : soft BCE 가중치의 활성 패턴 (학습 자료 공분산 × 가중치). 영역 묶음별 변화, 피험자 간 일치도
내용/잔차 분해: 실제 평정 y = t + e (t = 내용 teacher 의 평가 영상 예측, e = 나머지).
  r(p, y) = cov(p, t)/(sd_p sd_y) + cov(p, e)/(sd_p sd_y) 로 예측 성능을 두 성분의 기여로 나눈다.
  t 는 06_linear_distill 의 teacher_content (V-JEPA 2 + 사람 캡션 ridge, 같은 fold 의 학습 영상으로 학습).
출력: project/output/prelim_2026-10/09_interpretation/
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import roi_networks as rn  # noqa: E402

rs, bb = rn.rs, rn.bb
O = rs.OUT
OUT = O / "09_interpretation"
KEY = ["participant_id", "video_id", "dimension"]


def load_softbce():
    S = pd.concat([pd.read_csv(f, sep="\t") for f in sorted((O / "07_students/softbce").glob("predictions_sub-*.tsv.gz"))])
    W = S.pivot_table(index=KEY, columns="input_condition", values="y_pred").reset_index()
    Y = S[S.input_condition == "softbce_w0"][KEY + ["y_true", "train_mean"]]
    return W.merge(Y, on=KEY)


def teacher_test(space):
    T = pd.concat([pd.read_csv(f, sep="\t") for f in sorted((O / "06_linear_distill/vjepa2_vitg_final+caption_human_mpnet").glob("predictions_sub-*.tsv.gz"))])
    return T[(T.input_condition == "teacher_content") & (T.target_space == space)][KEY + ["y_pred"]].rename(columns={"y_pred": "t"})


def contrib(p, y, t):
    sp, sy = p.std(), y.std()
    return np.cov(p, t, bias=True)[0, 1] / (sp * sy), np.cov(p, y - t, bias=True)[0, 1] / (sp * sy)


def subject_emotion(n_boot=2000):
    D = load_softbce().merge(teacher_test("A34"), on=KEY)
    rng = np.random.RandomState(0); rows = []
    for (pid, dim), g in D.groupby(["participant_id", "dimension"]):
        y, p0, p1, t = g.y_true.values, g.softbce_w0.values, g.softbce_wsel.values, g.t.values
        r0, r1 = bb.pearson(y, p0), bb.pearson(y, p1)
        bs = []
        for _ in range(n_boot):
            i = rng.randint(0, len(y), len(y)); bs.append(bb.pearson(y[i], p1[i]) - bb.pearson(y[i], p0[i]))
        c0, c1 = contrib(p0, y, t), contrib(p1, y, t)
        rows.append(dict(participant_id=pid, dimension=dim, n_nonzero=int((y > 0).sum()), r_w0=r0, r_wsel=r1, delta=r1 - r0,
                         ci_lo=np.percentile(bs, 2.5), ci_hi=np.percentile(bs, 97.5),
                         content_w0=c0[0], resid_w0=c0[1], content_gain=c1[0] - c0[0], resid_gain=c1[1] - c0[1]))
    R = pd.DataFrame(rows); OUT.mkdir(parents=True, exist_ok=True)
    R.to_csv(OUT / "subject_emotion_softbce.tsv", sep="\t", index=False, float_format="%.4f")
    E = R.groupby("dimension").agg(delta=("delta", "mean"), n_subj_pos=("delta", lambda x: int((x > 0).sum())),
                                   n_subj_ci_pos=("ci_lo", lambda x: int((x > 0).sum())), r_w0=("r_w0", "mean"),
                                   content_gain=("content_gain", "mean"), resid_gain=("resid_gain", "mean"),
                                   resid_w0=("resid_w0", "mean")).sort_values("delta", ascending=False)
    E.to_csv(OUT / "emotion_softbce.tsv", sep="\t", float_format="%.4f")
    P = R.groupby("participant_id").agg(delta=("delta", "mean"), n_dims_pos=("delta", lambda x: int((x > 0).sum())),
                                        n_dims_ci_pos=("ci_lo", lambda x: int((x > 0).sum())), r_w0=("r_w0", "mean"),
                                        content_gain=("content_gain", "mean"), resid_gain=("resid_gain", "mean"))
    P.to_csv(OUT / "subject_softbce.tsv", sep="\t", float_format="%.4f")
    pd.set_option("display.width", 220); pd.set_option("display.max_rows", 60)
    print("== 피험자별"); print(P.round(4).to_string())
    print("== 범주별 (5명)"); print(E.round(4).to_string())
    piv = R.pivot(index="dimension", columns="participant_id", values="delta")
    cc = piv.corr(); print(f"범주별 이득 패턴의 피험자 간 상관 (평균): {cc.values[np.triu_indices(5, 1)].mean():.3f}")


def videos():
    D = load_softbce().merge(teacher_test("A34"), on=KEY)
    D["se0"] = (D.y_true - D.softbce_w0) ** 2; D["se1"] = (D.y_true - D.softbce_wsel) ** 2; D["set"] = (D.y_true - D.t) ** 2
    V = D.groupby(["participant_id", "video_id"])[["se0", "se1", "set"]].sum().reset_index()
    V["gain"] = V.se0 - V.se1                                         # 양수 = student 가 그 영상의 34개 범주를 더 잘 맞힘
    piv = V.pivot(index="video_id", columns="participant_id", values="gain")
    cc = piv.corr().values[np.triu_indices(piv.shape[1], 1)]
    A = V.groupby("video_id").agg(gain=("gain", "mean"), n_subj_pos=("gain", lambda x: int((x > 0).sum())), n_subj=("gain", "size"),
                                  se_w0=("se0", "mean"), se_teacher=("set", "mean")).reset_index()
    cap = pd.read_csv("/pscratch/sd/s/sjmoon/transfer/emobrain_stimulus_features_20261025/captions/caption_ck20.csv", encoding="utf-8-sig")
    first = cap.groupby("video_id").description.first()
    Y = D[D.participant_id == D.participant_id.iloc[0]].pivot_table(index="video_id", columns="dimension", values="y_true")
    top3 = Y.apply(lambda r: ", ".join(f"{k} {v:.2f}" for k, v in r.sort_values(ascending=False).head(3).items()), axis=1)
    A["caption"] = A.video_id.map(first); A["top_emotions"] = A.video_id.map(top3)
    A.sort_values("gain", ascending=False).to_csv(OUT / "videos_softbce.tsv", sep="\t", index=False, float_format="%.4f")
    from scipy.stats import spearmanr
    rho = spearmanr(A.gain, A.se_teacher); rho0 = spearmanr(A.gain, A.se_w0)
    print(f"영상 {len(A)}개 | 좋아진 영상 비율 {(A.gain > 0).mean():.3f} | 5명 모두 좋아짐 {(A.n_subj_pos == 5).sum()}, 5명 모두 나빠짐 {(A.n_subj_pos == 0).sum()}")
    print(f"영상별 이득의 피험자 간 상관 평균 {cc.mean():.3f} | 이득 vs teacher 오차 순위상관 {rho.correlation:+.3f} | 이득 vs 뇌 단독 오차 {rho0.correlation:+.3f}")
    pd.set_option("display.max_colwidth", 90); pd.set_option("display.width", 250)
    cols = ["video_id", "gain", "n_subj_pos", "top_emotions", "caption"]
    print("== 가장 좋아진 영상"); print(A.sort_values("gain", ascending=False)[cols].head(12).round(3).to_string(index=False))
    print("== 가장 나빠진 영상"); print(A.sort_values("gain")[cols].head(8).round(3).to_string(index=False))


def video_characteristics():
    """영상별 이득(5명 평균)이 영상의 자료 특성으로 설명되는지: 길이, 평정 분포, 머리 움직임, 오차, 의미 개념 73개."""
    from scipy.stats import spearmanr
    A = pd.read_csv(OUT / "videos_softbce.tsv", sep="\t").set_index("video_id")
    lab = pd.read_csv(rs.REPO / "project/shared/data/cowen_horikawa_labels.csv").set_index("stim_num_int")
    Y = lab.reindex(A.index)[[f"score_{i}" for i in range(34)]].values
    pn = Y / np.clip(Y.sum(1, keepdims=True), 1e-9, None)
    smp = pd.concat([pd.read_csv(f"/pscratch/sd/s/sjmoon/Horikawa/sub-{s}/v3_qc/sub-{s}_samples_qc_usable.tsv", sep="\t") for s in ["01", "02", "03", "04", "05"]])
    smp = smp[~smp.exclude_duplicate.astype(bool)].groupby("video_id")[["duration_sec", "fd_max_window", "std_dvars_max_window"]].mean()
    X = pd.DataFrame(dict(duration=smp.duration_sec.reindex(A.index).values, fd=smp.fd_max_window.reindex(A.index).values,
                          dvars=smp.std_dvars_max_window.reindex(A.index).values, peak=Y.max(1), total=Y.sum(1),
                          n_ge01=(Y >= .1).sum(1), entropy=-(pn * np.log(np.clip(pn, 1e-12, None))).sum(1),
                          err_w0=A.se_w0.values, err_teacher=A.se_teacher.values), index=A.index)
    sem = pd.read_csv("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/semantic_features.csv")
    sem.index = sem.pop("stimulus_num").str.replace("stimulus_", "").astype(int); sem = sem.reindex(A.index)
    rows = [dict(feature=c, kind="자료 특성", rho=spearmanr(X[c], A.gain, nan_policy="omit").correlation) for c in X]
    rows += [dict(feature=c, kind="의미 개념", rho=spearmanr(sem[c], A.gain, nan_policy="omit").correlation) for c in sem if sem[c].std() > 0]
    R = pd.DataFrame(rows).assign(abs_rho=lambda d: d.rho.abs()).sort_values("abs_rho", ascending=False)
    R.to_csv(OUT / "video_gain_characteristics.tsv", sep="\t", index=False, float_format="%.4f")
    Z = X.rank().fillna(X.rank().mean()); yv = A.gain.rank()
    D = np.column_stack([np.ones(len(Z)), Z.values]); b = np.linalg.lstsq(D, yv, rcond=None)[0]
    r2 = 1 - ((yv - D @ b) ** 2).sum() / ((yv - yv.mean()) ** 2).sum()
    print(f"영상 {len(A)}개 | 자료 특성 {X.shape[1]}개로 이득 순위 분산의 {100 * r2:.1f}% 설명 (순위 회귀)")
    print(R[R.kind == "자료 특성"].round(3).to_string(index=False))
    print("== 이득과 관련이 큰 의미 개념 (상위 12)"); print(R[R.kind == "의미 개념"].head(12).round(3).to_string(index=False))


def networks():
    rows = []
    for space in ["A34", "A14"]:
        P = pd.concat([pd.read_csv(f, sep="\t") for f in sorted((O / "08_roi_networks").glob("predictions_sub-*.tsv.gz"))])
        P = P[(P.target_space == space) & P.input_condition.str.endswith(":direct")].merge(teacher_test(space), on=KEY)
        for (pid, cond, dim), g in P.groupby(["participant_id", "input_condition", "dimension"]):
            c, e = contrib(g.y_pred.values, g.y_true.values, g.t.values)
            rows.append(dict(target_space=space, participant_id=pid, group=cond.split(":")[0], dimension=dim,
                             r=bb.pearson(g.y_true.values, g.y_pred.values), content=c, resid=e))
    R = pd.DataFrame(rows)
    S = R.groupby(["target_space", "group", "participant_id"])[["r", "content", "resid"]].mean().groupby(["target_space", "group"]).agg(["mean", "min"])
    S.columns = [f"{a}_{b}" for a, b in S.columns]
    S["resid_share_pct"] = 100 * S.resid_mean / S.r_mean
    S = S.reindex([(sp, gname) for sp in ["A34", "A14"] for gname in rn.ORDER])
    S.to_csv(OUT / "networks_content_resid.tsv", sep="\t", float_format="%.4f")
    pd.set_option("display.width", 220); print(S.round(4).to_string())


def weights():
    """soft BCE 가중치의 활성 패턴 (학습 자료 공분산 × 가중치, fold 평균). 469개 영역 id 로 맞춰 피험자 간 비교."""
    import teacher_cache as tc
    from itertools import combinations
    info = pd.read_csv(O / "roi_blocks/Horikawa_sub-01_roi469_info.tsv", sep="\t")
    maps, names = {}, None
    for f in sorted((O / "07_students/softbce").glob("weights_sub-*.npz")):
        pid = f.stem.replace("weights_", ""); sub = pid[-2:]
        w = np.load(f); d = np.load(tc.CACHE / f"{pid}.npz"); B = d["B"].astype(np.float64); fold = d["fold"]; names = list(w["names"])
        rows = pd.read_csv(O / f"roi_blocks/Horikawa_{pid}_roi469_rows.tsv", sep="\t")
        R = np.load(O / f"roi_blocks/Horikawa_{pid}_roi469_runz.npy"); inf = pd.read_csv(O / f"roi_blocks/Horikawa_{pid}_roi469_info.tsv", sep="\t")
        valid = inf.roi_valid.values & np.isfinite(R[~rows.exclude_duplicate.astype(bool).values]).all(0)
        A = {}
        for key in ["W0", "Wsel"]:
            acc = []
            for i, fo in enumerate(w["folds"]):
                Xtr = B[fold != fo]; Z = (Xtr - Xtr.mean(0)) / np.where(Xtr.std(0) > 0, Xtr.std(0), 1)
                acc.append((Z.T @ Z / len(Z)) @ w[key][i][:-1])
            full = np.full((len(valid), len(names)), np.nan); full[valid] = np.mean(acc, 0); A[key] = full
        maps[pid] = A
    grp = np.array(rn.roi_groups.__wrapped__(info) if hasattr(rn.roi_groups, "__wrapped__") else None, dtype=object) if False else None
    name, net = info.name.astype(str), info.network.values
    g = np.where(name.str.startswith("7Networks"), net, "").astype(object)
    g[name.str.startswith("Cereb7N").values] = "Cerebellum"; g[name.str.contains("AMY").values] = "Amygdala"
    g[name.str.startswith("HIP").values] = "Hippocampus"; g[(net == "Subcortex") & (g == "")] = "OtherSubcortex"
    g[np.isin(net, ["Hypothalamus", "Brainstem"])] = "Hypothal+Brainstem"
    subs = sorted(maps); out = []
    for k, emo in enumerate(names):
        A0 = np.stack([maps[s]["W0"][:, k] for s in subs]); A1 = np.stack([maps[s]["Wsel"][:, k] for s in subs])
        ok = np.isfinite(A0).all(0)
        cons = lambda M: np.mean([np.corrcoef(M[i, ok], M[j, ok])[0, 1] for i, j in combinations(range(len(subs)), 2)])
        same = np.mean([np.corrcoef(A0[i, ok], A1[i, ok])[0, 1] for i in range(len(subs))])
        rec = dict(dimension=emo, pattern_r_w0_vs_wsel=same, subj_consistency_w0=cons(A0), subj_consistency_wsel=cons(A1))
        m0, m1 = np.nanmean(A0, 0), np.nanmean(A1, 0)                 # 5명 평균 패턴
        for gname in rn.ORDER[:-1]:
            sel = g == gname
            rec[f"{gname}_w0"] = np.nanmean(m0[sel]); rec[f"{gname}_delta"] = np.nanmean(m1[sel] - m0[sel])
        top = np.argsort(-np.nan_to_num(m1, nan=-9))[:5]
        rec["top_rois_wsel"] = "; ".join(f"{name.iloc[i]}" for i in top)
        out.append(rec)
    W = pd.DataFrame(out).set_index("dimension"); OUT.mkdir(parents=True, exist_ok=True)
    W.to_csv(OUT / "weights_patterns_by_emotion.tsv", sep="\t", float_format="%.5f")
    np.savez(OUT / "activation_patterns.npz", **{f"{s}_{key}": maps[s][key] for s in subs for key in ["W0", "Wsel"]}, names=np.array(names),
             roi_names=info.name.values, groups=g)
    E = pd.read_csv(OUT / "emotion_softbce.tsv", sep="\t").set_index("dimension")
    W = W.join(E[["delta"]]).sort_values("delta", ascending=False)
    pd.set_option("display.width", 260); pd.set_option("display.max_colwidth", 120)
    print(f"뇌 단독 대 student 패턴 상관 (평균) {W.pattern_r_w0_vs_wsel.mean():.3f} | 피험자 간 패턴 일치도 w0 {W.subj_consistency_w0.mean():.3f} → wsel {W.subj_consistency_wsel.mean():.3f}")
    from scipy.stats import spearmanr
    print(f"감정별 이득 vs 패턴 변화량(1 − 상관) 순위상관 {spearmanr(W.delta, 1 - W.pattern_r_w0_vs_wsel).correlation:+.2f}")
    cols = ["delta", "pattern_r_w0_vs_wsel", "subj_consistency_w0", "subj_consistency_wsel"]
    print(W[cols].round(3).to_string())
    dcols = [f"{gname}_delta" for gname in rn.ORDER[:-1]]
    print("== 네트워크별 패턴 변화 (5명 평균 활성 패턴의 student − 뇌 단독, 영역 평균; 이득 상위·하위 감정)")
    print(pd.concat([W.head(8), W.tail(6)])[dcols].rename(columns=lambda c: c.replace("_delta", "")).round(4).to_string())
    print("== student 패턴의 상위 영역 (이득 상위 6개 감정)"); print(W.head(6)[["top_rois_wsel"]].to_string())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for k in ["subject-emotion", "videos", "video-characteristics", "networks", "weights"]:
        ap.add_argument(f"--{k}", action="store_true")
    a = ap.parse_args(); OUT.mkdir(parents=True, exist_ok=True)
    if a.subject_emotion:
        subject_emotion()
    if a.videos:
        videos()
    if a.video_characteristics:
        video_characteristics()
    if a.networks:
        networks()
    if a.weights:
        weights()
