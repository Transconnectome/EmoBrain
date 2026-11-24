#!/usr/bin/env python3
"""S10 geometry 확인 분석 (11/16 석진 님 승인. 결과를 본 뒤 더한 탐색 분석, 01 기록 칸). GPU 없음.

s10_geometry의 (a)(내용을 넘는 일반화)를 네트워크 13개 모두에 대해 구간과 두 대조로 확인하고, Bernardi 외(2020)의 CCGP와
shattering dimensionality(SD)를 낸다. 차원은 valence와 arousal 두 개만 쓴다(11/16 석진 님. core affect의 두 축).

변형(variant). 분할과 ridge는 같고 입력만 바꾼다.
- raw: 네트워크 voxel 그대로. zone 계산은 s10_geometry fit과 같은 식이다(시험이 같은 값인지 본다).
- global: 뇌 전체 평균과 voxel 간 표준편차(s5_common.signal_baseline_input, I7 정의)로 설명되는 부분을 voxel마다 최소제곱으로 뺀다.
  계수는 그 분할의 가중치 학습 행으로만 맞춘다.
- size0, size1, size2: 네트워크마다 voxel을 그 참가자의 가장 작은 네트워크 크기만큼 무작위로 뽑는다(seed 고정, 세 번).

분석
- zone: s10_geometry (a)와 같은 분할(6-2의 구역 제외와 학습량 대조)과 같은 ridge(s5_common.main_version). 목표는 valence, arousal.
  구역마다 영상에 걸친 r을 내고 구역 5개를 평균한다. 떨어진 폭 = r(구역 제외) − r(학습량 대조).
- 조건(Bernardi 외 2020의 condition): 내용 구역 5개 × 그 차원의 높음, 낮음 = 10개. 높음, 낮음은 구역 안에서 사람 평정의 순위로 반씩 나눈다
  (같은 값은 video_id 순서, 홀수면 높음 쪽이 하나 많다). 구역과 차원이 겹치지 않게 하려는 것이다. 개발 영상 2,109개로 한 번 정하고 뇌 자료는 보지 않는다.
- dichotomy: 조건 10개를 5개씩 나누는 126가지. 그 가운데 하나가 차원 자체(높음 대 낮음)다. 라벨은 ±1.
- SD: 바깥 fold마다 가중치 학습 fold로 126개 dichotomy를 한꺼번에 ridge로 학습하고(λ는 검증 fold의 r로 목표마다), 시험 fold를 예측한다.
  dichotomy마다 AUC를 내고 126개를 평균한다. AUC에서 영상마다 1/(그 조건의 영상 수) 무게를 준다(Bernardi는 조건마다 시행 수를 맞췄다).
- CCGP: 조건 둘(c1, c2)을 빼고 나머지 8개 조건으로 학습해 c1 대 c2를 시험한다(AUC). c1과 c2를 다른 쪽에 두는 dichotomy마다 낸다.
  한 dichotomy의 CCGP는 그 dichotomy의 25가지 (c1, c2) AUC 평균이다. 바깥 fold 구조를 지킨다. 학습은 가중치 학습 fold, λ는 검증 fold,
  시험은 시험 fold의 c1, c2 영상이고 6 fold의 예측을 모아 AUC를 한 번 낸다. 입력 표준화(와 global의 회귀)는 그 바깥 fold의 가중치 학습 fold 전체
  (조건과 무관)로 한 번 한다. 시험 fold는 쓰지 않는다.
- Bernardi 외 2020과 다른 점: 정확도 대신 AUC(조건 크기가 다르므로 문턱값에 기대지 않으려고), 신경 집단 대신 voxel, 시행 대신 영상, 선형 SVM 대신 ridge.
- bootstrap: s10_performance와 같은 단위(같은 내용 영상 묶음, split의 canonical_id), 같은 seed(BOOT_SEED), 10,000회.
  영상마다 뽑힌 횟수를 무게로 쓰고 5명에 같은 무게를 쓴다. 그래서 재표집마다 5명 평균을 낼 수 있다.
저장(레포 밖 --out): fit/sub-0X_<variant>.npz. summarize가 표를 낸다(규칙은 summarize 머리말).
사용: s10_geometry_checks.py fit --participant 01 --variant raw --out <폴더> --design-freeze <커밋> [--threads 16]
      s10_geometry_checks.py summarize --out <폴더> --design-freeze <커밋>
"""
import argparse
import itertools
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

import s4_common as c
import s5_common as d5
import s10_geometry as geo
import s10_stats as st

BOOT_SEED = 20261115  # s10_performance.BOOT_SEED와 같은 값(같은 재표집)
SIZE_SEED = 20261116
DIMS = ("valence", "arousal")
VARIANTS = ("raw", "global", "size0", "size1", "size2")
N_COND = 2 * geo.N_BLOCKS
DICHOTOMIES = [frozenset(x) for x in itertools.combinations(range(N_COND), N_COND // 2) if 0 in x]  # 126
SIDE = np.array([[k in d for k in range(N_COND)] for d in DICHOTOMIES])  # (126, 10) 조건 0이 있는 쪽이면 참
DIM_DICHOTOMY = DICHOTOMIES.index(frozenset(range(0, N_COND, 2)))  # 낮음 조건(짝수) 대 높음 조건(홀수)
PAIRS = list(itertools.combinations(range(N_COND), 2))  # 45


def conditions(split, dname, blocks):
    """split 순서의 영상마다 조건 번호 = 2 × (구역 − 1) + (높음이면 1)."""
    D, _, dnames = geo.targets(split, split.video_id.to_numpy())
    val = D[:, 34 + dnames.index(dname)]
    vid = split.video_id.to_numpy()
    blk = blocks.set_index("video_id").loc[vid, "block"].to_numpy()
    cond = np.full(len(vid), -1)
    for b in range(1, geo.N_BLOCKS + 1):
        idx = np.flatnonzero(blk == b)
        order = np.lexsort((vid[idx], val[idx]))
        high = np.zeros(len(idx), bool)
        high[order[len(idx) // 2:]] = True
        cond[idx] = 2 * (b - 1) + high
    if (cond < 0).any():
        raise ValueError("구역이 없는 영상이 있다")
    return cond


def residualize(x, C, rows):
    """x(영상 × voxel)에서 C(영상 × 3: 1, 뇌 전체 평균, voxel 간 표준편차)로 설명되는 부분을 뺀다. 계수는 rows로만 맞춘다."""
    Ct = torch.as_tensor(C, dtype=x.dtype)
    r = torch.as_tensor(rows)
    beta = torch.linalg.lstsq(Ct[r], x[r]).solution
    return x - Ct @ beta


def gram_ridge(G, Y, tr, va, te):
    """s5_common.DualRidge와 main_version과 같은 식. G는 이미 표준화한 입력의 kernel(모든 행 × 모든 행), Y는 torch(행 × 목표)."""
    tr, va, te = (torch.as_tensor(a) for a in (tr, va, te))
    vals, vecs = torch.linalg.eigh(G[tr][:, tr])
    vals = vals.clamp_min(0)
    ym = Y[tr].mean(0)
    uty = vecs.T @ (Y[tr] - ym)
    cva, cte = G[va][:, tr] @ vecs, G[te][:, tr] @ vecs

    def pred(cross, lam):
        return ym + cross @ ((1 / (vals + float(lam)))[:, None] * uty)

    pick = d5.pick_per_target(torch.stack([d5.r_selection(Y[va], pred(cva, lam)) for lam in d5.LAMBDAS]))
    paths = torch.stack([pred(cte, lam) for lam in d5.LAMBDAS])
    out = paths.gather(0, pick[None, None, :].expand(1, len(te), Y.shape[1]))[0]
    if not torch.isfinite(out).all():
        raise ValueError("ridge 예측에 NaN 또는 Inf가 있다")
    return out


def wauc(score, pos, w):
    """무게를 준 AUC. score (n,), pos bool (n,), w torch (B, n) 0 이상의 무게. 같은 점수는 반으로 센다. 돌려주는 값 numpy (B,).
    한쪽 무게 합이 0인 재표집은 NaN이다."""
    score, pos = np.asarray(score, np.float64), np.asarray(pos, bool)
    if not np.isfinite(score).all():
        raise ValueError("AUC 점수에 NaN이 있다")
    o = np.argsort(score, kind="stable")
    s = score[o]
    W = w.index_select(1, torch.as_tensor(o))
    pt = torch.as_tensor(pos[o])
    wn, wp = W * (~pt), W * pt
    starts = np.r_[0, np.flatnonzero(np.diff(s)) + 1]
    if len(starts) < len(s):  # 같은 점수 묶음은 묶어서 센다
        gn = torch.as_tensor(np.add.reduceat(wn.numpy(), starts, axis=1))
        gp = torch.as_tensor(np.add.reduceat(wp.numpy(), starts, axis=1))
    else:
        gn, gp = wn, wp
    below = torch.cumsum(gn, 1) - gn
    num = (gp * (below + 0.5 * gn)).sum(1).double().numpy()
    den = (gp.sum(1).double() * gn.sum(1).double()).numpy()
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(den > 0, num / den, np.nan)


def boot_weights(split, vid, n_boot):
    """s10_performance와 같은 단위(canonical_id)와 seed. split 전체에서 뽑고 이 참가자의 영상 행으로 옮긴다. torch (B, 영상) float32."""
    codes, n_units = st.unit_codes(split.canonical_id.to_numpy())
    W = st.bootstrap_counts(n_units, n_boot, np.random.default_rng(BOOT_SEED))
    pos = {v: i for i, v in enumerate(split.video_id.tolist())}
    return torch.as_tensor(W[:, codes[[pos[v] for v in vid.tolist()]]].astype(np.float32))


def network_inputs(nets, variant, s):
    """네트워크 이름 -> 열 위치. size 변형은 가장 작은 네트워크 크기만큼 무작위로 뽑는다."""
    if not variant.startswith("size"):
        return {g: p for g, p in nets.items()}
    n_min, draw = min(len(p) for p in nets.values()), int(variant[4:])
    out = {}
    for j, (g, p) in enumerate(nets.items()):
        rng = np.random.default_rng([SIZE_SEED, int(s), j, draw])
        out[g] = np.sort(rng.choice(p, n_min, replace=False))
    return out


def fit(s, variant, out, split, threads, n_boot):
    torch.set_num_threads(threads)
    brain = d5.load_brain(s, split)
    vid = np.asarray(brain.video_id)
    T, _, dnames = geo.targets(split, vid)
    Y = T[:, [34 + dnames.index(d) for d in DIMS]]
    nets = network_inputs(geo.network_positions(brain), variant, s)
    row_of = {v: i for i, v in enumerate(vid.tolist())}
    fold = np.asarray(brain.fold)
    blocks = pd.read_csv(c.S2 / "content_blocks_assignment.tsv", sep="\t")
    control = pd.read_csv(c.S2 / "content_block_control_samples.tsv", sep="\t")
    blk = blocks.set_index("video_id").loc[vid, "block"].to_numpy()
    C = None
    if variant == "global":
        g, gid = d5.signal_baseline_input(s, split)
        if not np.array_equal(np.asarray(gid), vid):
            raise ValueError("뇌 전체 신호의 영상 순서가 뇌 자료와 다르다")
        C = np.c_[np.ones(len(vid)), g]
    cond = {d: d5.align(conditions(split, d, blocks), split, vid) for d in DIMS}
    W = boot_weights(split, vid, n_boot)
    n, nn = len(vid), len(nets)
    res = dict(video_id=vid, networks=np.array(list(nets)), n_voxels=np.array([len(p) for p in nets.values()]), variant=variant, dims=np.array(DIMS),
               zone_excluded_pred=np.full((nn, n, 2), np.nan, np.float32), zone_control_pred=np.full((nn, n, 2), np.nan, np.float32),
               a_point=np.full((2, nn, 2), np.nan), a_boot=np.full((2, n_boot, nn, 2), np.nan, np.float32))
    for d in DIMS:
        res[f"{d}_cond"] = cond[d]
        res[f"{d}_sd_pred"] = np.full((nn, n, len(DICHOTOMIES)), np.nan, np.float32)
        res[f"{d}_sd_auc"] = np.full((nn, len(DICHOTOMIES)), np.nan)
        res[f"{d}_sd_boot"] = np.full((n_boot, nn), np.nan, np.float32)
        res[f"{d}_ccgp_auc"] = np.full((nn, len(PAIRS), len(DICHOTOMIES)), np.nan)
        res[f"{d}_ccgp_dim_pred"] = np.full((nn, len(PAIRS), n), np.nan, np.float32)
        res[f"{d}_ccgp_dim_boot"] = np.full((n_boot, nn), np.nan, np.float32)
    X = torch.as_tensor(np.asarray(brain.X))
    for j, (g, pos) in enumerate(nets.items()):
        started = time.time()
        x = X[:, torch.as_tensor(pos)].double()
        # zone
        for k in range(1, c.N_FOLDS + 1):
            r = c.roles(k)
            for b in range(1, geo.N_BLOCKS + 1):
                for kind in geo.KINDS:
                    train_ids, test_ids = c.zone_sets(split, b, k, kind, blocks=blocks, control=control)
                    tri = np.array([row_of[v] for v in train_ids if v in row_of])
                    tei = np.array([row_of[v] for v in test_ids if v in row_of])
                    if not len(tei):
                        continue
                    tr_z, va_z = tri[np.isin(fold[tri], r["train"])], tri[fold[tri] == r["val"]]
                    xx = residualize(x, C, tr_z) if C is not None else x
                    p, bad = geo.ridge(xx, Y, tr_z, va_z, tei)
                    if bad:
                        raise ValueError(f"{g} 구역 {b} fold {k}: 정답이 상수인 목표가 있다")
                    res[f"zone_{kind}_pred"][j, tei] = p
        for i, kind in enumerate(geo.KINDS):
            P = res[f"zone_{kind}_pred"][j].astype(np.float64)
            if not np.isfinite(P).all():
                raise ValueError(f"{g}: 예측이 없는 영상이 있다")
            pb, bb = [], []
            for b in range(1, geo.N_BLOCKS + 1):
                m = blk == b
                pb.append(st.boot_r(np.ones((1, m.sum())), Y[m], dict(p=P[m]))["p"][0])
                bb.append(st.boot_r(W[:, torch.as_tensor(np.flatnonzero(m))].double().numpy(), Y[m], dict(p=P[m]))["p"])
            res["a_point"][i, j] = np.mean(pb, 0)
            res["a_boot"][i, :, j] = np.mean(bb, 0)
        # SD, CCGP
        Lab = {d: torch.as_tensor(np.where(SIDE[:, cond[d]].T, 1.0, -1.0)) for d in DIMS}
        pair_pred = {d: [np.full((n, int((SIDE[:, a] != SIDE[:, b]).sum())), np.nan) for a, b in PAIRS] for d in DIMS}
        for k in range(1, c.N_FOLDS + 1):
            r = c.roles(k)
            tr, va, te = np.flatnonzero(np.isin(fold, r["train"])), np.flatnonzero(fold == r["val"]), np.flatnonzero(fold == k)
            xx = residualize(x, C, tr) if C is not None else x
            z, _, _ = d5.standardize(xx, torch.as_tensor(tr))
            G = z @ z.T
            del z
            for d in DIMS:
                L, cd = Lab[d], cond[d]
                res[f"{d}_sd_pred"][j, te] = gram_ridge(G, L, tr, va, te).numpy()
                for q, (a, b) in enumerate(PAIRS):
                    use = SIDE[:, a] != SIDE[:, b]
                    out_ab = np.isin(cd, (a, b))
                    p = gram_ridge(G, L[:, torch.as_tensor(np.flatnonzero(use))], tr[~out_ab[tr]], va[~out_ab[va]], te[out_ab[te]])
                    pair_pred[d][q][te[out_ab[te]]] = p.numpy()
        for d in DIMS:
            cd = cond[d]
            cw = 1.0 / pd.Series(cd).map(pd.Series(cd).value_counts()).to_numpy()
            cwt = torch.as_tensor(cw[None], dtype=torch.float32)
            Wc, acc = W * cwt, np.zeros(W.shape[0])
            for t in range(len(DICHOTOMIES)):
                pos_t = SIDE[t, cd]
                sc = res[f"{d}_sd_pred"][j, :, t].astype(np.float64)
                res[f"{d}_sd_auc"][j, t] = wauc(sc, pos_t, cwt)[0]
                acc += wauc(sc, pos_t, Wc)
            res[f"{d}_sd_boot"][:, j] = acc / len(DICHOTOMIES)
            del Wc
            dim_boot = []
            for q, (a, b) in enumerate(PAIRS):
                use = np.flatnonzero(SIDE[:, a] != SIDE[:, b])
                rows = np.flatnonzero(np.isin(cd, (a, b)))
                P = pair_pred[d][q][rows]
                if not np.isfinite(P).all():
                    raise ValueError(f"{g} {d} 조건 {a}, {b}: 예측이 없는 영상이 있다")
                for u, t in enumerate(use):
                    res[f"{d}_ccgp_auc"][j, q, t] = wauc(P[:, u], SIDE[t, cd[rows]], torch.ones((1, len(rows))))[0]
                if DIM_DICHOTOMY in use:
                    u = int(np.flatnonzero(use == DIM_DICHOTOMY)[0])
                    res[f"{d}_ccgp_dim_pred"][j, q, rows] = P[:, u]
                    dim_boot.append(wauc(P[:, u], SIDE[DIM_DICHOTOMY, cd[rows]], W[:, torch.as_tensor(rows)]))
            if len(dim_boot) != 25:
                raise ValueError("차원 dichotomy의 (c1, c2) 조합이 25개가 아니다")
            res[f"{d}_ccgp_dim_boot"][:, j] = np.nanmean(dim_boot, 0)
        print(f"sub-{s} {variant} {g} ({len(pos)} voxel) {time.time() - started:.0f}초", flush=True)
    o = Path(out) / "fit"
    o.mkdir(parents=True, exist_ok=True)
    tmp = o / f"sub-{s}_{variant}.tmp.npz"
    np.savez(tmp, **res)
    tmp.rename(o / f"sub-{s}_{variant}.npz")


def summarize(out, split):
    """5명을 모아 표를 낸다. 점 추정은 5명 평균, 구간은 basic bootstrap 95%(s10_stats.basic_ci), 차이의 p는 중심을 맞춘 양측 bootstrap p.
    size는 세 번 뽑은 값을 평균한다(재표집 무게가 같아 재표집마다 평균할 수 있다).
    a_drop.tsv: 변형, 네트워크, 차원마다 r(학습량 대조), r(구역 제외), 떨어진 폭과 구간, 비율, 참가자별 폭.
    ccgp_sd.tsv: 변형, 설계(차원), 네트워크마다 그 차원의 CCGP와 구간, SD와 구간, 그 차원의 CCGP가 126개 dichotomy 가운데 몇 번째인지.
    pairwise.tsv: 변형, 지표마다 네트워크 쌍의 차이(앞 − 뒤), 구간, p. 탐색이라 다중비교 보정을 하지 않는다.
    dichotomies.tsv: 변형, 설계, 네트워크, dichotomy마다 CCGP와 decoding AUC(5명 평균)."""
    out = Path(out)
    F = {}
    for s in d5.HK:
        for v in VARIANTS:
            z = np.load(out / "fit" / f"sub-{s}_{v}.npz", allow_pickle=True)
            F[s, v] = {k: z[k] for k in z.files}
    nets = F[d5.HK[0], "raw"]["networks"].tolist()
    groups = dict(raw=["raw"], global_signal_removed=["global"], size_matched=["size0", "size1", "size2"])

    def gather(key, vs):
        """참가자 × (뽑기 평균)."""
        return np.stack([np.mean([F[s, v][key] for v in vs], 0) for s in d5.HK])

    rows_a, rows_c, rows_p, rows_d = [], [], [], []
    for gname, vs in groups.items():
        pt, bt = gather("a_point", vs), gather("a_boot", vs)  # (5, 2, nn, 2), (5, 2, B, nn, 2)
        drop_p, drop_b = (pt[:, 0] - pt[:, 1]).mean(0), (bt[:, 0] - bt[:, 1]).mean(0)  # (nn, 2), (B, nn, 2)
        lo, hi = st.basic_ci(drop_p, drop_b)
        for j, g in enumerate(nets):
            for i, d in enumerate(DIMS):
                per = pt[:, 0, j, i] - pt[:, 1, j, i]
                rows_a.append(dict(variant=gname, network=g, dimension=d, n_voxels=int(np.mean([F[s, vs[0]]["n_voxels"][j] for s in d5.HK])),
                                   r_control=pt[:, 1, j, i].mean(), r_excluded=pt[:, 0, j, i].mean(), drop=drop_p[j, i], drop_lo=lo[j, i], drop_hi=hi[j, i],
                                   ratio=pt[:, 0, j, i].mean() / pt[:, 1, j, i].mean(), **{f"drop_sub-{s}": x for s, x in zip(d5.HK, per)}))
        meas = {f"drop_{d}": (drop_p[:, i], drop_b[:, :, i]) for i, d in enumerate(DIMS)}
        for d in DIMS:
            cg_p = gather(f"{d}_ccgp_auc", vs)  # (5, nn, 45, 126)
            cg_dich = np.nanmean(cg_p, 2).mean(0)  # (nn, 126) dichotomy마다 25쌍 평균, 5명 평균
            sd_auc = gather(f"{d}_sd_auc", vs).mean(0)  # (nn, 126)
            cd_b = gather(f"{d}_ccgp_dim_boot", vs).mean(0)  # (B, nn)
            sd_b = gather(f"{d}_sd_boot", vs).mean(0)
            cd_p, sd_p = cg_dich[:, DIM_DICHOTOMY], sd_auc.mean(1)
            clo, chi = st.basic_ci(cd_p, cd_b)
            slo, shi = st.basic_ci(sd_p, sd_b)
            per_c = np.nanmean(cg_p, 2)[:, :, DIM_DICHOTOMY]
            for j, g in enumerate(nets):
                rank = int((cg_dich[j] > cg_dich[j, DIM_DICHOTOMY]).sum()) + 1
                rows_c.append(dict(variant=gname, design=d, network=g, ccgp_dim=cd_p[j], ccgp_lo=clo[j], ccgp_hi=chi[j], ccgp_dim_rank_of_126=rank,
                                   ccgp_other_mean=np.delete(cg_dich[j], DIM_DICHOTOMY).mean(), decoding_auc_dim=sd_auc[j, DIM_DICHOTOMY],
                                   sd=sd_p[j], sd_lo=slo[j], sd_hi=shi[j], **{f"ccgp_sub-{s}": x for s, x in zip(d5.HK, per_c[:, j])}))
                for t, dich in enumerate(DICHOTOMIES):
                    rows_d.append(dict(variant=gname, design=d, network=g, dichotomy=t, side=",".join(map(str, sorted(dich))), is_dimension=t == DIM_DICHOTOMY,
                                       ccgp=cg_dich[j, t], decoding_auc=sd_auc[j, t]))
            meas[f"ccgp_{d}"], meas[f"sd_{d}"] = (cd_p, cd_b), (sd_p, sd_b)
        for m, (p, b) in meas.items():
            for ja, jb in itertools.combinations(range(len(nets)), 2):
                dp, db = p[ja] - p[jb], b[:, ja] - b[:, jb]
                lo, hi = st.basic_ci(dp, db)
                rows_p.append(dict(variant=gname, measure=m, network_a=nets[ja], network_b=nets[jb], diff=dp, lo=float(lo), hi=float(hi), p=float(st.centered_p(dp, db))))
    tabs = dict(a_drop=rows_a, ccgp_sd=rows_c, pairwise=rows_p, dichotomies=rows_d)
    for name, rows in tabs.items():
        pd.DataFrame(rows).to_csv(out / f"{name}.tsv", sep="\t", index=False)
    return tabs


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 geometry 확인 분석")
    ap.add_argument("step", choices=["fit", "summarize"])
    ap.add_argument("--participant", choices=d5.HK)
    ap.add_argument("--variant", choices=VARIANTS)
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", required=True)
    ap.add_argument("--threads", type=int, default=16)
    ap.add_argument("--n-boot", type=int, default=st.N_RESAMPLE)
    a = ap.parse_args(argv)
    c.guard(a.design_freeze)
    split = c.load_split()
    started = time.time()
    if a.step == "fit":
        if a.participant is None or a.variant is None:
            raise SystemExit("fit은 --participant와 --variant가 필요하다")
        fit(a.participant, a.variant, a.out, split, a.threads, a.n_boot)
        tag = f"fit_sub-{a.participant}_{a.variant}"
    else:
        summarize(a.out, split)
        tag = "summarize"
    info = dict(step=a.step, participant=a.participant, variant=a.variant, n_boot=a.n_boot, boot_seed=BOOT_SEED, size_seed=SIZE_SEED, design_freeze=a.design_freeze,
                code_commit=c.START_HEAD, code_dirty=c.START_DIRTY, elapsed_seconds=round(time.time() - started, 1))
    Path(a.out).mkdir(parents=True, exist_ok=True)
    (Path(a.out) / f"run_info_{tag}.json").write_text(json.dumps(info, indent=1, ensure_ascii=False))
    print(f"끝: {tag} {info['elapsed_seconds']}초", flush=True)


if __name__ == "__main__":
    main()
