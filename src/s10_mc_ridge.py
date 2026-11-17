#!/usr/bin/env python3
"""S10 6-3의 ridge 기준선 (11/17 석진 님 요청. 6-3 결과를 본 뒤 더한 비교). GPU 없음.

묻는 것: HK에서 학습한 공유 모델을 MC로 옮긴 결과(A-1, C-1)가, 같은 MC 자료로 맞춘 선형 decoder보다 나은가?
비교하는 decoder(모두 사람 평정 34개를 맞히고, 시험은 6-3과 같은 MC 시험 영상 72개의 반복 평균)
- within_voxel: MC 참가자마다 자기 시청 학습 block(s8의 input_train)으로 voxel → 정서 ridge(s5_common.main_version), λ는 input_val로 목표마다 고른다.
  깊은 모델의 입력층을 맞춘 것과 같은 자료, 같은 검증 규칙이고 HK 자료를 쓰지 않는다.
- within_roimean: 같은 것을 ROI 370개의 voxel 평균으로 한다.
- hk_roimean: HK 5명의 개발 영상에서 ROI 370개 평균 → 정서 ridge를 맞춘 뒤(HK 최종 모델과 같은 final_roles: fold 1 검증, fold 2~6 학습,
  5명의 행을 모음), MC 참가자에게 그대로 적용한다. MC 자료로는 표준화 통계만 맞춘다(그 참가자의 학습, 검증 block).
  사람 사이 voxel 대응 없이 할 수 있는 전이다. ROI 평균은 참가자마다 자기 학습 행으로 표준화한다.
채점: s10_mc와 같다. 72개 영상에서 정서별 Pearson r, 34개 평균, 참가자 6명 평균. 깊은 모델(A-1, C-1)은 s8_mc의 seed마다 고른 후보(done.json의
  chosen_input_wd)의 시험 예측을 읽어 seed 3개의 r을 평균한다. 차이의 구간은 72개 영상의 bootstrap(10,000회, BOOT_SEED, 6명 같은 무게)이다.
출력(레포 밖 --out): scores.tsv(참가자, decoder마다 34개 평균 r), per_emotion.tsv, comparison.tsv(C-1 − 각 decoder, A-1 − 각 decoder), preds.npz.
사용: s10_mc_ridge.py --mc-dir <s8_mc> --out <폴더> --design-freeze <커밋> [--threads 16]
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
import s8_mc_transfer as M8
import s10_stats as st
import s6_common as S

BOOT_SEED = 20261115
DEEP = {"A-1": "brain_only", "C-1": "brain_decoded"}
SEEDS = (0, 1, 2)
DUMMY_STATS = dict(visual_mean=0.0, visual_std=1.0, caption_mean=0.0, caption_std=1.0)


def roi_means(X, positions):
    return np.stack([np.asarray(X[:, p], np.float64).mean(1) for p in positions], 1)


def zscore(x, rows):
    m, s = x[rows].mean(0), x[rows].std(0)
    s = np.where(s > 0, s, 1.0)
    return (x - m) / s


def ridge_fit_predict(x, y, tr, va, te):
    p, _ = d5.main_version(d5.as_tensor(x, "cpu"), d5.as_tensor(y, "cpu"), tr, va, te)
    return p.numpy()


def hk_roimean_model(split):
    """HK 5명, 개발 영상 전체. 돌려주는 값: ROI 평균(참가자마다 표준화)과 사람 평정을 모은 행, 학습/검증 행 번호."""
    r = c.final_roles()
    xs, ys, roles = [], [], []
    for s in d5.HK:
        b = d5.load_brain(s, split)
        x = roi_means(np.asarray(b.X), b.roi_positions)
        fold = np.asarray(b.fold)
        tr = np.isin(fold, r["train"])
        x = zscore(x, np.flatnonzero(tr | (fold == r["val"])))
        T, _ = c.load_scores(split, "emotions")
        y = d5.align(np.asarray(T, np.float64), split, b.video_id)
        xs.append(x), ys.append(y), roles.append(np.where(tr, 0, np.where(fold == r["val"], 1, -1)))
    x, y, role = np.concatenate(xs), np.concatenate(ys), np.concatenate(roles)
    if (role < 0).any():
        raise ValueError("final_roles 밖의 HK 행이 있다")
    return x, y, np.flatnonzero(role == 0), np.flatnonzero(role == 1)


def deep_preds(mc_dir, cond, pid, video_te):
    out = []
    for seed in SEEDS:
        d = Path(mc_dir) / cond / f"seed{seed}" / pid
        done = json.loads((d / "done.json").read_text())
        z = np.load(d / f"test_pred_wd{float(done['chosen_input_wd']):g}.npz")
        if not np.array_equal(z["video_id"], video_te):
            raise ValueError(f"{cond} seed {seed} {pid}: 시험 영상 순서가 다르다")
        out.append(z["p"].astype(np.float64))
    return out


def run(mc_dir, out, split, threads):
    torch.set_num_threads(threads)
    blocks, repeats, idmap = (pd.read_csv(p, sep="\t") for p in (M8.MC_BLOCKS, M8.MC_REPEATS, M8.ID_MAP))
    mc72_table = pd.read_csv(d5.MC72, sep="\t")
    mc72 = S.mc_video_ids()
    names = pd.read_csv(c.LABEL_MAP, sep="\t").name.tolist()
    xh, yh, trh, vah = hk_roimean_model(split)
    print(f"HK ROI 평균 행 {len(xh)}", flush=True)
    preds, ys, rows_s, rows_e = {}, {}, [], []
    for s in M8.MC:
        pid = f"mc-{s}"
        data = M8.load_mc(s, blocks, repeats, idmap, mc72)
        tg = M8.targets(data["video_tv"], data["video_te"], idmap, split, DUMMY_STATS, mc72_table)
        role = data["role_tv"]
        tr, va = np.flatnonzero(role == 0), np.flatnonzero(role == 1)
        n_tv = len(data["X_tv"])
        te = np.arange(n_tv, n_tv + len(data["X_te"]))
        y = np.concatenate([tg["y_tv"], tg["y_te"]]).astype(np.float64)
        Xv = np.concatenate([data["X_tv"], data["X_te"]]).astype(np.float64)
        Xr = roi_means(Xv, data["positions"])
        P = {}
        P["within_voxel"] = ridge_fit_predict(Xv, y, tr, va, te)
        P["within_roimean"] = ridge_fit_predict(Xr, y, tr, va, te)
        xz = zscore(Xr, np.concatenate([tr, va]))
        xa = np.concatenate([xh, xz[te]])
        P["hk_roimean"] = ridge_fit_predict(xa, np.concatenate([yh, y[te]]), trh, vah, np.arange(len(xh), len(xa)))
        for name, cond in DEEP.items():
            P[name] = deep_preds(mc_dir, cond, pid, data["video_te"])
        preds[pid], ys[pid] = P, tg["y_te"].astype(np.float64)
        for name, p in P.items():
            rr = np.mean([st.pearson_columns(ys[pid], q) for q in p], 0) if isinstance(p, list) else st.pearson_columns(ys[pid], p)
            rows_s.append(dict(participant=pid, decoder=name, score_r=float(np.nanmean(rr))))
            rows_e += [dict(participant=pid, decoder=name, emotion=n, r=float(v)) for n, v in zip(names, rr)]
        print(f"{pid}: " + ", ".join(f"{r['decoder']} {r['score_r']:.3f}" for r in rows_s[-len(P):]), flush=True)
    S_ = pd.DataFrame(rows_s)
    S_ = pd.concat([S_, S_.groupby("decoder", as_index=False).score_r.mean().assign(participant="mean_mc")], ignore_index=True)
    # 차이의 구간: 72개 영상 bootstrap, 6명 같은 무게(영상 순서가 6명 모두 같아야 한다)
    W = st.bootstrap_counts(72, st.N_RESAMPLE, np.random.default_rng(BOOT_SEED)).astype(np.float64)
    boot = {}
    for pid, P in preds.items():
        for name, p in P.items():
            ps = p if isinstance(p, list) else [p]
            boot.setdefault(name, []).append(np.mean([st.mean_over(st.boot_r(W, ys[pid], dict(q=q))["q"], np.ones(34, bool)) for q in ps], 0))
    bm = {k: np.mean(v, 0) for k, v in boot.items()}
    pt = S_[S_.participant == "mean_mc"].set_index("decoder").score_r
    comp = []
    for a in ("C-1", "A-1"):
        for b in ("within_voxel", "within_roimean", "hk_roimean") + (("A-1",) if a == "C-1" else ()):
            dp, db = pt[a] - pt[b], bm[a] - bm[b]
            lo, hi = st.basic_ci(dp, db)
            per = S_[S_.participant != "mean_mc"].pivot_table(index="participant", columns="decoder", values="score_r")
            comp.append(dict(comparison=f"{a} − {b}", estimate=dp, ci_low=float(lo), ci_high=float(hi), p=float(st.centered_p(dp, db)),
                             n_participants_positive=int(((per[a] - per[b]) > 0).sum())))
    o = Path(out)
    o.mkdir(parents=True, exist_ok=True)
    S_.to_csv(o / "scores.tsv", sep="\t", index=False)
    pd.DataFrame(rows_e).to_csv(o / "per_emotion.tsv", sep="\t", index=False)
    pd.DataFrame(comp).to_csv(o / "comparison.tsv", sep="\t", index=False)
    np.savez(o / "preds.npz", **{f"{pid}|{k}": (np.mean(v, 0) if isinstance(v, list) else v) for pid, P in preds.items() for k, v in P.items()})


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 6-3 ridge 기준선")
    ap.add_argument("--mc-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", required=True)
    ap.add_argument("--threads", type=int, default=16)
    a = ap.parse_args(argv)
    c.guard(a.design_freeze)
    split = c.load_split()
    started = time.time()
    run(a.mc_dir, a.out, split, a.threads)
    info = dict(stage="S10 6-3 ridge 기준선", mc_dir=str(a.mc_dir), boot_seed=BOOT_SEED, n_boot=st.N_RESAMPLE, design_freeze=a.design_freeze,
                code_commit=c.START_HEAD, code_dirty=c.START_DIRTY, elapsed_seconds=round(time.time() - started, 1))
    (Path(a.out) / "run_info.json").write_text(json.dumps(info, indent=1, ensure_ascii=False))
    print(f"끝: {info['elapsed_seconds']}초", flush=True)


if __name__ == "__main__":
    main()
