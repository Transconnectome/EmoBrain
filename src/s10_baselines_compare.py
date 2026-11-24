#!/usr/bin/env python3
"""S10 HK에서 뇌 모델과 단순 모델, 선행 정서 decoder의 비교(11/19 석진 님 "빈 칸 다 채우자"). GPU 없음, 새로 학습하지 않는다.

모델
- 뇌 모델(S6 최종 결과 s6_brain_final, seed 0): A-1, C-1, D-3, D-4.
- S5 기준선(s5_ridge): ridge(주 비교판 emotion_main), MLP, GED, ML-BVAE, EmoGrowth(seed 0). 같은 바깥 fold 6개, 같은 시험 영상.
계산(s10_per_emotion의 HK와 같음)
- 참가자마다, 정서마다 6 fold의 시험 예측을 모아 Pearson r. 34개 평균과 27개판(Cowen & Keltner 7개 제외) 평균, 5명 평균.
- 차이: 각 뇌 모델 − ridge, 각 뇌 모델 − MLP, 각 기준선 − A-1. 내용 묶음 단위 bootstrap 10,000회(BOOT_SEED 20261115, 모든 모델과 5명에 같은 재표집),
  basic 95% 구간, 중심 맞춘 양측 p, 5명 중 같은 방향 수.
- 시험 영상은 모든 모델에서 같아야 한다(s10_performance.same_rows). 다르면 멈춘다.
출력(레포 밖 --out): scores.tsv, differences.tsv, run_info.json
사용: s10_baselines_compare.py --s6-dir <s6_brain_final> --s5-dir <s5_ridge> --out <폴더>
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

import s4_common as c
import s10_performance as PF
import s10_stats as st

BOOT_SEED = 20261115
CK7 = ("pride", "triumph", "contempt", "disappointment", "sympathy", "guilt", "envy")
BRAIN = {"brain_only": "A-1", "brain_decoded": "C-1", "brain_features_only": "D-3", "brain_frozen_feature_encoder": "D-4"}
BASE = {"ridge": "ridge", "mlp": "MLP", "ged": "GED", "mlbvae": "ML-BVAE", "emogrowth": "EmoGrowth"}


def load_baseline(s5, name, pids):
    out = {}
    for q in pids:
        vids, preds = [], []
        for k in range(1, PF.N_FOLDS + 1):
            z = np.load(Path(s5) / name / f"sub-{q[-2:]}_fold{k}" / "pred.npz")
            p = z["emotion_main"] if name == "ridge" else z["emotion_seeds"][list(z["seeds"]).index(0)]
            vids.append(z["video_id"].astype(np.int64))
            preds.append(np.asarray(p, np.float64))
        v, p = np.concatenate(vids), np.concatenate(preds)
        o = np.argsort(v)
        out[q] = (v[o], p[o])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s6-dir", required=True)
    ap.add_argument("--s5-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n-boot", type=int, default=st.N_RESAMPLE)
    a = ap.parse_args()
    t0 = time.time()
    split = c.load_split()
    y, cols = c.load_scores(split, "emotions")
    lm = pd.read_csv(c.LABEL_MAP, sep="\t")
    emotions = lm.set_index("score_col").loc[cols, "name"].tolist()
    ck = np.array([e in CK7 for e in emotions])
    found = PF.find_predictions(a.s6_dir)
    plan_rows = {k: PF.plan_test_rows(a.s6_dir, k) for k in range(1, PF.N_FOLDS + 1)}
    data = {}
    for cond, lab in BRAIN.items():
        f = found[(found.condition == cond) & (found.seed == 0) & (found.status == "ok")]
        if sorted(f.fold.tolist()) != list(range(1, PF.N_FOLDS + 1)):
            raise SystemExit(f"{cond}: seed 0의 6 fold 예측이 다 있지 않다")
        data[lab] = PF.load_condition(dict(zip(f.fold.astype(int), f.path)), split, plan_rows, y.shape[1])
    pids = sorted(data["A-1"])
    for name, lab in BASE.items():
        data[lab] = load_baseline(a.s5_dir, name, pids)
    videos = PF.same_rows(data)
    U = np.array(sorted(set().union(*[set(v.tolist()) for v in videos.values()])), np.int64)
    sp = split.set_index("video_id").loc[U]
    pos_split = {v: i for i, v in enumerate(split.video_id.tolist())}
    yU = np.asarray(y, np.float64)[[pos_split[v] for v in U]]
    codes, n_units = st.unit_codes(sp.canonical_id.to_numpy())
    W = st.bootstrap_counts(n_units, a.n_boot, np.random.default_rng(BOOT_SEED))
    point, boot = {}, {}
    for q in pids:
        pos = np.searchsorted(U, videos[q])
        yq = yU[pos]
        rb = st.boot_r(W[:, codes[pos]], yq, {m: data[m][q][1] for m in data})
        for m in data:
            point.setdefault(m, []).append(st.pearson_columns(yq, data[m][q][1]))
            boot.setdefault(m, []).append(rb[m])
    sets = {"34": np.ones(len(emotions), bool), "27": ~ck}
    rows = []
    for m in data:
        for setname, msk in sets.items():
            for i, q in enumerate(pids):
                rows.append(dict(model=m, participant=q, set=setname, r=float(np.nanmean(point[m][i][msk]))))
            rows.append(dict(model=m, participant="mean5", set=setname, r=float(np.mean([np.nanmean(point[m][i][msk]) for i in range(len(pids))]))))
    pairs = [(m, "ridge") for m in BRAIN.values()] + [(m, "MLP") for m in BRAIN.values()] + [(b, "A-1") for b in ("ridge", "MLP", "GED", "ML-BVAE", "EmoGrowth")]
    diffs = []
    for ma, mb in pairs:
        for setname, msk in sets.items():
            per = [np.nanmean(point[ma][i][msk]) - np.nanmean(point[mb][i][msk]) for i in range(len(pids))]
            d = float(np.mean(per))
            db = np.mean([np.nanmean(boot[ma][i][:, msk], 1) - np.nanmean(boot[mb][i][:, msk], 1) for i in range(len(pids))], 0)
            lo, hi = st.basic_ci(np.array([d]), db[:, None])
            p = st.centered_p(np.array([d]), db[:, None])
            diffs.append(dict(comparison=f"{ma} − {mb}", set=setname, diff=d, ci_low=float(lo[0]), ci_high=float(hi[0]), p=float(p[0]),
                              n_positive=int(sum(x > 0 for x in per)), n_negative=int(sum(x < 0 for x in per)), **{f"diff_{q}": per[i] for i, q in enumerate(pids)}))
    o = Path(a.out)
    o.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(o / "scores.tsv", sep="\t", index=False)
    D = pd.DataFrame(diffs)
    D.to_csv(o / "differences.tsv", sep="\t", index=False)
    info = dict(models=list(data), participants=pids, n_videos_union=len(U), n_bootstrap_units=n_units, n_boot=a.n_boot, boot_seed=BOOT_SEED,
                code_commit=c.START_HEAD, code_dirty=c.START_DIRTY, seconds=round(time.time() - t0, 1))
    (o / "run_info.json").write_text(json.dumps(info, indent=1))
    S = pd.DataFrame(rows)
    print(S[S.participant == "mean5"].pivot_table(index="model", columns="set", values="r").round(3).to_string())
    print(D[["comparison", "set", "diff", "ci_low", "ci_high", "n_positive"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
