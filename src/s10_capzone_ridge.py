#!/usr/bin/env python3
"""S10 Dec-바(01 6-2b)의 ridge판과 CCGP(11/19 석진 님 "CCGP 진행", "Dec-바 모두 진행"). CPU.

분할: 캡션 구역 분할(capzone) 60개. 영상은 s6_common.plan_capzone과 같다(구역 b의 시험 fold 영상이 시험, 나머지 fold가 학습과 검증).
- excluded: 학습과 검증에서 구역 b를 통째로 뺀다. control: 같은 수의 영상을 무작위로 뺀다(구역 b가 학습에 남음).
읽는 목표(같은 분할, 같은 ridge)
- 평정: 정서 34개의 사람 평정(0~1). Dec-바의 영역별 비교와 캡션 예측기에 쓴다.
- high/low: 정서마다 그 영상이 속한 캡션 구역 안에서 사람 평정이 구역 중앙값보다 크면 1, 아니면 0(01 CCGP 정의의 "구역 안에서 사람 평정 순위로 반씩"). CCGP에 쓴다.
입력
- 뇌: 참가자마다 네트워크 13개와 뇌 전체의 voxel(s5_common.load_brain, 6-4d와 같음).
- 캡션: Caption feature 정서어 제거판(뇌 없음, 참가자와 무관). 캡션 예측기다.
ridge: s5_common.main_version(학습 행으로 표준화, 검증 fold로 목표마다 λ, 후보 LAMBDAS).
요약(summarize)
- Dec-바 ridge: 구역마다 6 fold의 시험 예측을 모아 정서별 r(참가자마다). 하락폭 = r(control) − r(excluded). 다섯 구역의 평균.
- CCGP: excluded 분할의 high/low decoder(다른 네 구역에서만 학습)가 처음 보는 구역 b의 high/low를 가르는 AUC(6 fold를 모음, 우연 0.5).
  같은 구역을 학습에 둔 control 분할의 AUC를 함께 낸다. 구역마다 high와 low를 함께 빼므로 Bernardi 외(2020)의 "서로 다른 구역의 두 조건을 빼는" 판에서
  구역 정보가 예측을 거꾸로 끄는 문제(01 11/16)가 없다. Bernardi 외와 다른 점: 정확도 대신 AUC, 신경 집단 대신 voxel, 시행 대신 영상, 선형 SVM 대신 ridge.
- summarize는 참가자마다의 값과 구역 평균을 낸다. 참가자 평균의 구간과 판정은 결과를 본 뒤 정하지 않고, 다음 단계(Dec-바 요약)에서 6-2와 같은 규칙으로 낸다.
출력(레포 밖 --out): fit/sub-0X.npz, fit/caption.npz(분할 × 시험 영상 × 목표 예측), per_emotion_r.tsv, per_emotion_ccgp.tsv, summary_r.tsv, summary_ccgp.tsv, run_info*.json
사용: s10_capzone_ridge.py fit --participant 01|caption --out <폴더> --design-freeze <커밋> [--threads 16]
      s10_capzone_ridge.py summarize --out <폴더> --design-freeze <커밋>
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

import s4_common as c
import s5_common as d5
import s10_geometry as geo
import s6_common as S

KINDS = ("excluded", "control")
BLOCKS = (1, 2, 3, 4, 5)
CK7 = ("pride", "triumph", "contempt", "disappointment", "sympathy", "guilt", "envy")


def plans(split):
    return {(b, k, kind): S.plan_capzone(split, b, k, kind) for b in BLOCKS for k in range(1, c.N_FOLDS + 1) for kind in KINDS}


def targets(split, vid):
    """평정 34개와 high/low 34개. 행은 vid 순서."""
    y, cols = c.load_scores(split, "emotions")
    y = np.asarray(d5.align(np.asarray(y, np.float64), split, vid), np.float64)
    blocks = pd.read_csv(S.CAPTION_BLOCKS[0], sep="\t").set_index("video_id").block
    yall = np.asarray(c.load_scores(split, "emotions")[0], np.float64)
    ball = blocks.reindex(split.video_id).to_numpy()
    med = {b: np.median(yall[ball == b], 0) for b in BLOCKS}
    bv = blocks.reindex(vid).to_numpy()
    hl = np.stack([(y[i] > med[bv[i]]).astype(np.float64) for i in range(len(vid))])
    return np.concatenate([y, hl], 1), cols


def fit(who, out, split, threads):
    torch.set_num_threads(threads)
    P = plans(split)
    if who == "caption":
        vid = split.video_id.to_numpy()
        feats = {"caption": np.asarray(c.load_rows(c.CAPTION_NO_EMOTION, vid, split), np.float64)}
    else:
        brain = d5.load_brain(who, split)
        vid = np.asarray(brain.video_id)
        X = np.asarray(brain.X)
        nets = geo.network_positions(brain)
        nets["whole_brain"] = np.arange(X.shape[1])
        feats = {g: X[:, p] for g, p in nets.items()}
    Y, cols = targets(split, vid)
    pos = {v: i for i, v in enumerate(vid.tolist())}
    rows = lambda ids: np.array([pos[v] for v in ids if v in pos])
    res = {}
    for g, x in feats.items():
        started = time.time()
        xt = torch.as_tensor(x).double()  # 6-4d와 같이 float64(평정 목표가 float64)
        for (b, k, kind), pl in P.items():
            tr, va, te = rows(pl.train), rows(pl.val), rows(pl.test)
            pr, bad = geo.ridge(xt, Y, tr, va, te)
            res[f"{g}|{b}|{k}|{kind}"] = (vid[te], pr.astype(np.float32), bad)
        print(f"{who} {g} {time.time() - started:.0f}초", flush=True)
    o = Path(out) / "fit"
    o.mkdir(parents=True, exist_ok=True)
    np.savez(o / (f"sub-{who}.npz" if who != "caption" else "caption.npz"), keys=np.array(list(res)), cols=np.array(cols),
             **{f"vid::{k}": v[0] for k, v in res.items()}, **{f"pred::{k}": v[1] for k, v in res.items()}, **{f"bad::{k}": np.array(v[2]) for k, v in res.items()})


def auc(y, s):
    """Mann-Whitney AUC. 한쪽 이름표만 있으면 NaN."""
    y = np.asarray(y) > 0.5
    n1, n0 = int(y.sum()), int((~y).sum())
    if n1 == 0 or n0 == 0:
        return np.nan
    r = pd.Series(s).rank().to_numpy()
    return float((r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def summarize(out, split):
    o = Path(out)
    files = sorted((o / "fit").glob("*.npz"))
    if len(files) != 6:
        raise SystemExit(f"fit 결과가 6개(참가자 5명 + caption)가 아니다: {[f.name for f in files]}")
    cols = None
    rows_r, rows_a = [], []
    for f in files:
        z = np.load(f)
        cols = z["cols"].tolist() if cols is None else cols
        who = f.stem.replace("sub-", "")
        keys = z["keys"].tolist()
        groups = sorted({k.split("|")[0] for k in keys})
        for g in groups:
            for b in BLOCKS:
                for kind in KINDS:
                    vids = np.concatenate([z[f"vid::{g}|{b}|{k}|{kind}"] for k in range(1, c.N_FOLDS + 1)])
                    pred = np.concatenate([z[f"pred::{g}|{b}|{k}|{kind}"] for k in range(1, c.N_FOLDS + 1)])
                    Y, _ = targets(split, vids)
                    ne = len(cols)
                    for e in range(ne):
                        yr, pr = Y[:, e], pred[:, e]
                        ok = np.isfinite(pr)
                        r = float(np.corrcoef(yr[ok], pr[ok])[0, 1]) if ok.sum() > 2 and yr[ok].std() > 0 and pr[ok].std() > 0 else np.nan
                        rows_r.append(dict(who=who, input=g, block=b, kind=kind, emotion=cols[e], r=r, n=int(ok.sum())))
                        yh, ph = Y[:, ne + e], pred[:, ne + e]
                        okh = np.isfinite(ph)
                        rows_a.append(dict(who=who, input=g, block=b, kind=kind, emotion=cols[e], auc=auc(yh[okh], ph[okh]), n_high=int(yh[okh].sum()), n=int(okh.sum())))
    R, A = pd.DataFrame(rows_r), pd.DataFrame(rows_a)
    lm = pd.read_csv(c.LABEL_MAP, sep="\t").set_index("score_col").name
    for t in (R, A):
        t["emotion"] = t.emotion.map(lambda s: lm.get(s, s))
        t["ck27"] = ~t.emotion.isin(CK7)
    R.to_csv(o / "per_emotion_r.tsv", sep="\t", index=False)
    A.to_csv(o / "per_emotion_ccgp.tsv", sep="\t", index=False)
    pr = R.pivot_table(index=["who", "input", "block", "emotion", "ck27"], columns="kind", values="r").reset_index()
    pr["drop"] = pr.control - pr.excluded
    pa = A.pivot_table(index=["who", "input", "block", "emotion", "ck27"], columns="kind", values="auc").reset_index()
    out_r, out_a = [], []
    for setname, m in (("34", lambda t: t.index == t.index), ("27", lambda t: t.ck27)):
        g = pr[m(pr)].groupby(["who", "input"])[["excluded", "control", "drop"]].mean().reset_index().assign(set=setname)
        out_r.append(g)
        h = pa[m(pa)].groupby(["who", "input"])[["excluded", "control"]].mean().reset_index().assign(set=setname)
        out_a.append(h)
    pd.concat(out_r).to_csv(o / "summary_r.tsv", sep="\t", index=False)
    pd.concat(out_a).rename(columns={"excluded": "ccgp_auc", "control": "control_auc"}).to_csv(o / "summary_ccgp.tsv", sep="\t", index=False)
    print(pd.concat(out_a).query("set == '27'").groupby("input")[["excluded", "control"]].mean().round(3).to_string())


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=("fit", "summarize"))
    ap.add_argument("--participant", choices=list(d5.HK) + ["caption"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", required=True)
    ap.add_argument("--threads", type=int, default=16)
    a = ap.parse_args(argv)
    c.guard(a.design_freeze)
    split = c.load_split()
    started = time.time()
    if a.step == "fit":
        if not a.participant:
            raise SystemExit("fit에는 --participant가 필요하다")
        fit(a.participant, a.out, split, a.threads)
        tag = f"fit_{a.participant}"
    else:
        summarize(a.out, split)
        tag = "summarize"
    info = dict(step=a.step, participant=a.participant, design_freeze=a.design_freeze, code_commit=c.START_HEAD, code_dirty=c.START_DIRTY, seconds=round(time.time() - started, 1))
    (Path(a.out) / f"run_info_{tag}.json").write_text(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
