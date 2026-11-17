#!/usr/bin/env python3
"""34개 범주 soft BCE 선형 student: 내용 teacher 예측을 섞은 target 으로 학습 (2026-10-28).

기준선과 같은 모델(L2 선형 sigmoid + soft BCE, 같은 λ 격자·안쪽 묶음·warm start). target = (1 - w)·실제 평정 + w·teacher 예측.
teacher 예측은 teacher_cache.py 의 교차검증 밖 예측 (0~1 로 자름). (w, λ) 는 차원마다 안쪽 검증의 실제 평정 soft BCE 로 고른다.
w = 0 은 랩서버 soft BCE 뇌 단독 기준선과 같은 계산이다 (재현 대조).
조건: softbce_w0 (뇌 단독 기준선), softbce_wsel (안쪽에서 고른 w)
가중치: weights_sub-XX.npz 에 fold 마다 두 조건의 선형 가중치(표준화한 469개 영역 + 절편 × 34개 범주)를 저장한다 (해석용).
사용: python softbce_student.py --sub 01 | --summarize
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import teacher_cache as tc  # noqa: E402

bb, cl = tc.bb, tc.rs.cl
OUT = tc.rs.OUT / "07_students/softbce"
WS = [0.0, 0.5, 0.75, 1.0]
LAM = bb.LAM_BCE


def run_subject(sub):
    t0 = time.time(); OUT.mkdir(parents=True, exist_ok=True)
    d = np.load(tc.CACHE / f"sub-{sub}.npz")
    B, fold, Y, vids, names = d["B"].astype(np.float64), d["fold"], d["Y34"], d["vids"], list(d["names"])
    pid = f"sub-{sub}"; preds, sel = [], []; bb.OPT_LOG.clear(); W0s, Wss, folds_done = [], [], []
    for f in np.unique(fold):
        trm, tem = fold != f, fold == f; g = fold[trm]; Ytr = Y[trm]; K = Ytr.shape[1]; idx = np.flatnonzero(tem)
        err = np.zeros((len(WS), len(LAM), K))
        for h in np.unique(g):
            a, b = g != h, g == h
            T = np.clip(d[f"T_A34_f{f}_h{h}"], 1e-4, 1 - 1e-4)
            Ba, Bb = cl.std_fit(B[trm][a], B[trm][b])
            for i, w in enumerate(WS):
                for j, th in enumerate(bb.fit_softbce_path(Ba, (1 - w) * Ytr[a] + w * T, LAM)):
                    err[i, j] += bb.softbce(Ytr[b], bb.predict_softbce(Bb, th)).sum(0)
        wi, li = np.unravel_index(err.reshape(-1, K).argmin(0), err.shape[:2])
        l0 = err[0].argmin(0)
        T = np.clip(d[f"T_A34_f{f}"], 1e-4, 1 - 1e-4)
        Btr, Bte = cl.std_fit(B[trm], B[tem])
        paths = {i: bb.fit_softbce_path(Btr, (1 - WS[i]) * Ytr + WS[i] * T, LAM) for i in sorted(set(wi) | {0})}
        P0 = np.column_stack([bb.predict_softbce(Bte, paths[0][l0[k]])[:, k] for k in range(K)])
        Ps = np.column_stack([bb.predict_softbce(Bte, paths[wi[k]][li[k]])[:, k] for k in range(K)])
        W0s.append(np.column_stack([paths[0][l0[k]][:, k] for k in range(K)]))
        Wss.append(np.column_stack([paths[wi[k]][li[k]][:, k] for k in range(K)])); folds_done.append(int(f))
        mu = Ytr.mean(0)
        for cond, P in [("softbce_w0", P0), ("softbce_wsel", Ps)]:
            for k, dim in enumerate(names):
                preds.append(pd.DataFrame(dict(participant_id=pid, video_id=vids[idx], outer_fold=int(f), input_condition=cond,
                                               target_space="A34", dimension=dim, y_true=Y[idx, k], y_pred=P[:, k], train_mean=mu[k])))
        sel += [dict(participant_id=pid, outer_fold=int(f), dimension=dim, w_selected=WS[wi[k]], lambda_selected=float(LAM[li[k]]),
                     lambda_w0=float(LAM[l0[k]]))
                for k, dim in enumerate(names)]
        print(f"  {pid} fold {f} 완료 ({time.time() - t0:.0f}초)", flush=True)
    np.savez(OUT / f"weights_{pid}.npz", W0=np.stack(W0s), Wsel=np.stack(Wss), folds=np.array(folds_done), names=np.array(names))
    pred = pd.concat(preds, ignore_index=True)
    pred.to_csv(OUT / f"predictions_{pid}.tsv.gz", sep="\t", index=False, float_format="%.6g")
    pd.DataFrame(sel).to_csv(OUT / f"selected_w_{pid}.tsv", sep="\t", index=False)
    dim, _ = bb.evaluate(pred, sub)
    dim.to_csv(OUT / f"dimension_metrics_{pid}.tsv", sep="\t", index=False, float_format="%.5f")
    (OUT / f"run_info_{pid}.json").write_text(json.dumps(dict(ws=WS, seconds=round(time.time() - t0),
                                                             softbce_convergence=bb.convergence_summary()), ensure_ascii=False, indent=1))
    print(dim.groupby("input_condition", sort=False).r_oof.mean().round(4).to_string())
    print(f"{pid} 완료 ({time.time() - t0:.0f}초)")


def summarize():
    D = pd.concat([pd.read_csv(f, sep="\t") for f in sorted(OUT.glob("dimension_metrics_sub-*.tsv"))])
    h = D.pivot_table(index=["participant_id", "dimension"], columns="input_condition", values="r_oof")
    per = h.groupby("participant_id").mean(); dlt = per.softbce_wsel - per.softbce_w0
    lab = pd.read_csv(tc.rs.LAB_REPORT / "02_brain/dimension_metrics.tsv", sep="\t")
    lab = lab[(lab.input_condition == "brain_roi469") & (lab.target_space == "A34")].set_index(["participant_id", "dimension"]).r_oof
    rep = (h.softbce_w0 - lab.reindex(h.index)).abs()
    print(f"w0 재현: 랩서버 기준선과 |Δr| 최대 {rep.max():.5f}")
    print(per.round(4).to_string()); print(f"평균 {per.mean().round(4).to_dict()} | 증가 피험자 {(dlt > 0).sum()}/5, 범위 {dlt.min():.4f}~{dlt.max():.4f}")
    print(f"5명 평균 증가 범주 {int(((h.softbce_wsel - h.softbce_w0).groupby('dimension').mean() > 0).sum())}/34")


def effect_size(n_boot=2000):
    """이득의 크기와 불확실성. 평가 영상을 영상 번호 단위로 5명 함께 복원 추출 (모델 재학습 없음, 평가 표본의 변동만 반영)."""
    P = pd.concat([pd.read_csv(f, sep="\t") for f in sorted(OUT.glob("predictions_sub-*.tsv.gz"))])
    vids = np.unique(P.video_id); rng = np.random.RandomState(0)
    Wv = np.stack([np.bincount(rng.randint(0, len(vids), len(vids)), minlength=len(vids)) for _ in range(n_boot)]).astype(float)
    pos = {v: i for i, v in enumerate(vids)}
    def wr(W, y, p):                                         # 가중 Pearson r (행 = bootstrap)
        s = W.sum(1, keepdims=True); my, mp = W @ y / s[:, 0], W @ p / s[:, 0]
        cyp = W @ (y * p) / s[:, 0] - my * mp; cyy = W @ (y * y) / s[:, 0] - my ** 2; cpp = W @ (p * p) / s[:, 0] - mp ** 2
        return cyp / np.sqrt(cyy * cpp)
    boot, point = {}, {}
    for (pid, dim), g in P.groupby(["participant_id", "dimension"]):
        a = g[g.input_condition == "softbce_w0"].sort_values("video_id"); b = g[g.input_condition == "softbce_wsel"].sort_values("video_id")
        assert (a.video_id.values == b.video_id.values).all()
        W = Wv[:, [pos[v] for v in a.video_id]]; y = a.y_true.values
        boot[(pid, dim)] = (wr(W, y, a.y_pred.values), wr(W, y, b.y_pred.values))
        point[(pid, dim)] = (bb.pearson(y, a.y_pred.values), bb.pearson(y, b.y_pred.values),
                             ((y - a.y_pred) ** 2).sum(), ((y - b.y_pred) ** 2).sum(), ((y - a.train_mean) ** 2).sum())
    subs = sorted({k[0] for k in boot}); dims = sorted({k[1] for k in boot})
    d_sub = {s: np.mean([boot[(s, d)][1] - boot[(s, d)][0] for d in dims], axis=0) for s in subs}
    d_all = np.mean([d_sub[s] for s in subs], axis=0)
    print(f"Δr (5명 평균) bootstrap 95% CI [{np.percentile(d_all, 2.5):+.4f}, {np.percentile(d_all, 97.5):+.4f}], Δr ≤ 0 비율 {(d_all <= 0).mean():.4f}")
    for s in subs:
        print(f"  {s}: CI [{np.percentile(d_sub[s], 2.5):+.4f}, {np.percentile(d_sub[s], 97.5):+.4f}]")
    pt = pd.DataFrame([dict(participant_id=k[0], dimension=k[1], r0=v[0], r1=v[1], er0=1 - v[2] / v[4], er1=1 - v[3] / v[4])
                       for k, v in point.items()])
    rel = pd.read_csv(tc.rs.REPO / "docs/reports/prelim_2026-10/stage0/tables/label_structure_reliability.tsv", sep="\t").set_index("감정")["라벨신뢰도"]
    pt["ceil"] = np.sqrt(pt.dimension.map(rel))
    m = pt.groupby("participant_id")[["r0", "r1", "er0", "er1"]].mean().mean()
    print(f"r 평균 {m.r0:.4f} → {m.r1:.4f} (상대 +{100 * (m.r1 / m.r0 - 1):.1f}%) | 오차 감소율(설명 분산) {100 * m.er0:.2f}% → {100 * m.er1:.2f}% "
          f"(상대 +{100 * (m.er1 / m.er0 - 1):.1f}%)")
    q = pt.assign(n0=pt.r0 / pt.ceil, n1=pt.r1 / pt.ceil, f0=pt.r0 ** 2 / pt.ceil ** 2, f1=pt.r1 ** 2 / pt.ceil ** 2).groupby("participant_id")[["n0", "n1", "f0", "f1"]].mean().mean()
    print(f"신뢰도 상한으로 나눈 r {q.n0:.3f} → {q.n1:.3f} | 설명 가능한 분산 중 설명한 비율 (r²/신뢰도) {100 * q.f0:.1f}% → {100 * q.f1:.1f}%")
    dd = (pt.r1 - pt.r0).groupby(pt.dimension).mean().sort_values()
    print(f"범주별 Δr (5명 평균): 최소 {dd.iloc[0]:+.4f} ({dd.index[0]}), 중앙값 {dd.median():+.4f}, 최대 {dd.iloc[-1]:+.4f} ({dd.index[-1]}), 양수 {(dd > 0).sum()}/{len(dd)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--sub"); ap.add_argument("--summarize", action="store_true")
    ap.add_argument("--effect-size", action="store_true")
    a = ap.parse_args()
    effect_size() if a.effect_size else summarize() if a.summarize else run_subject(a.sub)
