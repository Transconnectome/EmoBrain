#!/usr/bin/env python3
"""S10 D-4의 기준선: encoder 없이, D-4 정서 head와 같은 행으로 학습한 ridge(11/21, 비판 agent 검토의 "반드시 고칠 것" 2). CPU, 몇 분.

왜
- D-4(01 5-A)의 정서 head는 짝마다 held fold 영상(약 350개)으로만 학습하고 네 짝의 예측을 평균한다. 학습하지 않은 encoder 대조(0.036)는
  head의 검증 손실이 거의 줄지 않아(학습 손실만 내려감) "encoder가 없을 때의 값"으로 쓰기 어렵다.
- 그래서 encoder 없이 같은 행으로 선형 모델을 학습하면 얼마나 읽히는지 낸다. D-4가 이 값보다 높은 만큼이 고정한 encoder가 더한 것이다.
계산
- 참가자마다(입력층이 참가자마다인 것과 같다), 바깥 fold k마다(s4_common.roles), 학습 fold 4개의 j마다
  학습 = fold j 영상, 검증 = 바깥 검증 fold 영상, 시험 = fold k 영상. D-4의 head용 분할(s6_common.inner_plans)과 같다.
- ridge는 s5_common.main_version(학습 행으로 입력 표준화, 검증 fold로 정서마다 λ, 후보 LAMBDAS). 시험 예측은 네 짝의 평균이다.
- 입력 둘: voxel(그 참가자의 고유 voxel 전체), roi_mean(ROI 370개마다 voxel 평균. 저장된 반응 그대로 평균한다).
요약(summarize)
- 참가자마다, 정서마다 6 fold의 시험 예측을 모아 Pearson r. 34개 평균과 27개판 평균, 5명 평균.
- 함께 읽는 모델: A-1(최종 폴더), D-4(학습하지 않은 encoder 대조와 짝, 후보가 같은 주 비교 실행), 학습하지 않은 encoder 대조.
- 차이: 두 기준선 각각 − D-4, − 대조, − A-1. 내용 묶음 bootstrap 10,000회(BOOT_SEED 20261115, 모든 모델과 5명에 같은 재표집), basic 95% 구간, 중심 맞춘 양측 p,
  5명 중 같은 방향 수. 시험 행은 모든 모델에서 같아야 한다.
출력(레포 밖 --out): fit/sub-0X.npz(video_id, voxel, roi_mean), summary/{scores.tsv, differences.tsv, per_emotion.tsv, run_info.json}
사용: s10_pair_ridge.py fit --participant 01 --out <폴더> --design-freeze <커밋> [--threads 8]
      s10_pair_ridge.py summarize --out <폴더> --s6-final <s6_brain_final> --d4-root <s6_brain_grid_main> --control <s9_untrained_encoder>
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

import s4_common as c

BOOT_SEED = 20261115
CK7 = ("pride", "triumph", "contempt", "disappointment", "sympathy", "guilt", "envy")
INPUTS = ("voxel", "roi_mean")
LABEL = {"voxel": "짝 구조 ridge(voxel)", "roi_mean": "짝 구조 ridge(ROI 평균)"}
D4, CONTROL = "brain_frozen_feature_encoder", "brain_frozen_untrained_encoder"


def pair_rows(fold, k):
    """바깥 fold k의 짝 넷. 돌려주는 값: [(j, 학습 행, 검증 행, 시험 행)]. fold는 행마다의 fold 번호다."""
    r = c.roles(k)
    val, test = np.flatnonzero(fold == r["val"]), np.flatnonzero(fold == r["test"])
    return [(j, np.flatnonzero(fold == j), val, test) for j in r["train"]]


def features(brain):
    x = np.asarray(brain.X, np.float64)
    return {"voxel": x, "roi_mean": np.stack([x[:, p].mean(1) for p in brain.roi_positions], 1)}


def fit_one(x, y, fold):
    """한 참가자, 한 입력. 시험 fold마다 네 짝 예측의 평균. 돌려주는 값: 행 순서의 예측(행 × 정서)."""
    import torch
    import s5_common as d5
    xt, yt = torch.as_tensor(x).double(), torch.as_tensor(y).double()
    out = np.full(y.shape, np.nan)
    for k in range(1, c.N_FOLDS + 1):
        preds = []
        for _, tr, va, te in pair_rows(fold, k):
            p, _ = d5.main_version(xt, yt, tr, va, te)
            preds.append(p.numpy())
        out[te] = np.mean(preds, 0)
    c.finite(out, "짝 구조 ridge 예측")
    return out


def fit(a):
    import torch
    import s5_common as d5
    c.guard(a.design_freeze)
    torch.set_num_threads(a.threads)
    started = time.time()
    split = c.load_split()
    brain = d5.load_brain(a.participant, split)
    scores, _ = c.load_scores(split, "emotions")
    pos = {v: i for i, v in enumerate(split.video_id.tolist())}
    y = np.asarray(scores, np.float64)[[pos[v] for v in brain.video_id.tolist()]]
    fold = np.asarray(brain.fold)
    res = {name: fit_one(x, y, fold) for name, x in features(brain).items()}
    o = Path(a.out) / "fit"
    o.mkdir(parents=True, exist_ok=True)
    np.savez(o / f"{brain.participant}.npz", video_id=np.asarray(brain.video_id, np.int64), **res)
    info = dict(participant=brain.participant, n_rows=int(len(fold)), n_voxels=int(brain.X.shape[1]), n_roi=len(brain.roi_positions),
                head_rows_per_pair={k: [int(len(tr)) for _, tr, _, _ in pair_rows(fold, k)] for k in range(1, c.N_FOLDS + 1)},
                design_freeze=a.design_freeze, code_commit=c.START_HEAD, code_dirty=c.START_DIRTY, seconds=round(time.time() - started, 1))
    (Path(a.out) / f"run_info_fit_{brain.participant}.json").write_text(json.dumps(info, indent=1))
    print(json.dumps(info), flush=True)


def summarize(a):
    import s10_performance as PF
    import s10_stats as st
    split = c.load_split()
    y, cols = c.load_scores(split, "emotions")
    lm = pd.read_csv(c.LABEL_MAP, sep="\t")
    emotions = lm.set_index("score_col").loc[cols, "name"].tolist()
    ck = np.array([e in CK7 for e in emotions])
    folds = range(1, PF.N_FOLDS + 1)
    found = PF.find_predictions(a.s6_final)
    f = found[(found.condition == "brain_only") & (found.seed == 0) & (found.status == "ok")]
    if sorted(f.fold.tolist()) != list(folds):
        raise SystemExit("A-1: seed 0의 6 fold 예측이 다 있지 않다")
    paths = {"A-1": dict(zip(f.fold.astype(int), f.path)), "D-4": {}, "D-4 대조(학습하지 않은 encoder)": {}}
    for k in folds:
        sel = json.loads((Path(a.d4_root) / f"outer_fold{k}" / D4 / "selected.json").read_text())
        paths["D-4"][k] = Path(a.d4_root) / f"outer_fold{k}" / sel["seeds"]["0"] / "ensemble" / "test_pred.npz"
        hits = sorted((Path(a.control) / f"outer_fold{k}" / CONTROL).glob("*_seed0/ensemble/test_pred.npz"))
        if len(hits) != 1:
            raise SystemExit(f"outer_fold{k}: 대조 예측이 {len(hits)}개다")
        paths["D-4 대조(학습하지 않은 encoder)"][k] = hits[0]
    plan_rows = {k: PF.plan_test_rows(a.s6_final, k) for k in folds}
    data = {m: PF.load_condition(p, split, plan_rows, y.shape[1]) for m, p in paths.items()}
    pids = sorted(data["A-1"])
    for name in INPUTS:
        data[LABEL[name]] = {}
        for q in pids:
            z = np.load(Path(a.out) / "fit" / f"{q}.npz")
            o = np.argsort(z["video_id"])
            data[LABEL[name]][q] = (z["video_id"][o].astype(np.int64), np.asarray(z[name], np.float64)[o])
    videos = PF.same_rows(data)
    U = np.array(sorted(set().union(*[set(v.tolist()) for v in videos.values()])), np.int64)
    sp = split.set_index("video_id").loc[U]
    spos = {v: i for i, v in enumerate(split.video_id.tolist())}
    yU = np.asarray(y, np.float64)[[spos[v] for v in U]]
    codes, n_units = st.unit_codes(sp.canonical_id.to_numpy())
    W = st.bootstrap_counts(n_units, a.n_boot, np.random.default_rng(BOOT_SEED))
    point, boot = {}, {}
    for q in pids:
        pos = np.searchsorted(U, videos[q])
        rb = st.boot_r(W[:, codes[pos]], yU[pos], {m: data[m][q][1] for m in data})
        for m in data:
            point.setdefault(m, []).append(st.pearson_columns(yU[pos], data[m][q][1]))
            boot.setdefault(m, []).append(rb[m])
    sets = {"34": np.ones(len(emotions), bool), "27": ~ck}
    rows = []
    for m in data:
        for sn, msk in sets.items():
            per = [float(np.nanmean(point[m][i][msk])) for i in range(len(pids))]
            rows += [dict(model=m, participant=q, set=sn, r=per[i]) for i, q in enumerate(pids)]
            rows.append(dict(model=m, participant="mean5", set=sn, r=float(np.mean(per))))
    diffs = []
    for name in INPUTS:
        for ref in ("D-4", "D-4 대조(학습하지 않은 encoder)", "A-1"):
            ma = LABEL[name]
            for sn, msk in sets.items():
                per = [float(np.nanmean(point[ma][i][msk]) - np.nanmean(point[ref][i][msk])) for i in range(len(pids))]
                d = float(np.mean(per))
                db = np.mean([np.nanmean(boot[ma][i][:, msk], 1) - np.nanmean(boot[ref][i][:, msk], 1) for i in range(len(pids))], 0)
                lo, hi = st.basic_ci(np.array([d]), db[:, None])
                diffs.append(dict(comparison=f"{ma} − {ref}", set=sn, diff=d, ci_low=float(lo[0]), ci_high=float(hi[0]), p=float(st.centered_p(np.array([d]), db[:, None])[0]),
                                  n_positive=int(sum(x > 0 for x in per)), n_negative=int(sum(x < 0 for x in per))))
    per_e = pd.DataFrame([dict(emotion=emotions[e], ck27=not ck[e], **{m: float(np.mean([point[m][i][e] for i in range(len(pids))])) for m in data}) for e in range(len(emotions))])
    o = Path(a.out) / "summary"
    o.mkdir(parents=True, exist_ok=True)
    S, D = pd.DataFrame(rows), pd.DataFrame(diffs)
    S.to_csv(o / "scores.tsv", sep="\t", index=False)
    D.to_csv(o / "differences.tsv", sep="\t", index=False)
    per_e.to_csv(o / "per_emotion.tsv", sep="\t", index=False)
    (o / "run_info.json").write_text(json.dumps(dict(models=list(data), participants=pids, n_videos_union=len(U), n_bootstrap_units=n_units, n_boot=a.n_boot, boot_seed=BOOT_SEED,
                                                   s6_final=str(a.s6_final), d4_root=str(a.d4_root), control=str(a.control), code_commit=c.START_HEAD, code_dirty=c.START_DIRTY), indent=1, ensure_ascii=False))
    print(S[S.participant == "mean5"].pivot_table(index="model", columns="set", values="r").round(3).to_string())
    print(D.round(3).to_string(index=False), flush=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 D-4의 기준선: 짝 구조 ridge")
    ap.add_argument("step", choices=("fit", "summarize"))
    ap.add_argument("--participant")
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", default="")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--s6-final")
    ap.add_argument("--d4-root")
    ap.add_argument("--control")
    ap.add_argument("--n-boot", type=int, default=10_000)
    a = ap.parse_args(argv)
    if a.step == "fit":
        if not a.participant:
            raise SystemExit("fit에는 --participant가 필요하다")
        fit(a)
    else:
        if not (a.s6_final and a.d4_root and a.control):
            raise SystemExit("summarize에는 --s6-final, --d4-root, --control이 필요하다")
        summarize(a)


if __name__ == "__main__":
    main()
