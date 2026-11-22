#!/usr/bin/env python3
"""S10 6-4i ①과 ③(01 6-4i, 11/22). Shared-AE(Yi 외, 2025)를 세 modality(뇌, Vision, 캡션 잔차)로 넓히고 표본 짝 손실을 더한 모델. CPU.

모델(참가자마다, 바깥 fold k마다, seed마다)
- 입력: s10_align_data의 뇌 PCA, Vision PCA, 캡션 잔차(모두 학습 행 크기 맞춤).
- modality마다 MLP encoder(256 → HIDDEN → 잠재)와 decoder(잠재 → HIDDEN → 256). 잠재 칸의 차원은 모두 d.
  뇌 [s_vis, s_sit, p], Vision [t_vis, q_vis], 캡션 잔차 [t_sit, q_sit].
- 손실(원 논문 식 5를 넓힘, 가중치 W = 5):
  재구성 MSE 셋 + W × CS(s_vis, t_vis), CS(s_sit, t_sit)
  + W × inverse CS(s_vis, p), (s_sit, p), (s_vis, s_sit), (t_vis, q_vis), (t_sit, q_sit), (p, q_vis), (p, q_sit)
  + W × 짝 손실(s_vis, t_vis), (s_sit, t_sit).
  CS는 Gaussian Parzen 추정(원 논문 식 2, 3), σ²는 배치 안 제곱 거리 중앙값의 절반(값의 크기에 따라 뜻이 바뀌지 않게). inverse CS는 1 / (CS + EPS)(공개 코드의 weight / loss 꼴).
  짝 손실은 Barlow Twins(Zbontar 외, 2021)의 교차상관 손실. 대각과 비대각 합을 d로 나눠 d가 달라도 크기가 같게 한다(비대각 가중치 5e-3은 원 논문).
- 학습: Adam, learning rate 1e-4, batch 256(원 논문). 최대 MAX_EPOCHS(계산 예산), 검증 fold 전체 손실로 조기 종료(patience PATIENCE).
- d: D_CANDIDATES 가운데 seed 0의 검증 재구성 손실이 최소값의 1% 안에 드는 가장 작은 값(원 논문 A.9.2). 다른 seed와 대조에도 같은 d.
- 변형: trained, shuffled(학습과 검증 행에서 캡션 구역 안 뇌와 장면의 짝을 섞음. 시험은 원래 짝).
읽기(readout, 참가자마다, 6 fold의 시험 예측을 모아서). 정서와 장면을 읽는 ridge는 검증 fold 행으로 학습하고 λ는 검증 fold 안 내용 묶음 5겹으로 고른다
(모델이 학습한 행의 잠재는 시험 행과 분포가 달라서다, 11/22 비판 agent 검토).
- 정렬: 공유 칸 짝의 차원별 상관(시험, 학습 행 값도 함께).
- 정서: vis = s_vis, vis_sit = [s_vis, s_sit], all = [s_vis, s_sit, p], 장면 쪽 scene_vis = t_vis, scene_vis_sit = [t_vis, t_sit], 참고 pca = 뇌 PCA 256.
- ③ 옮기기: 장면 쪽 [t_vis, t_sit]로 학습한 ridge를 뇌 쪽 [s_vis, s_sit]의 시험 행에. 바닥(floor)은 뇌 PCA → [t_vis, t_sit] ridge(학습 행) 뒤 같은 ridge.
- 칸 사이 섞임: 시험 증분 R²(s_sit가 s_vis 위에 더하는 Vision 정보, p가 [s_vis, s_sit] 위에 더하는 Vision과 캡션 잔차 정보).
- 제시 순서 변수(s10_align_data.order_inputs) → p의 시험 R²(기술 값).
요약: H2 = Δsit_brain과 6-4d x의 편순위상관(Δsit_scene 통제), ③ 모양 = 옮긴 r과 뇌 쪽 직접 r의 편상관(장면 쪽 r 통제). 내용 묶음 bootstrap.
출력(레포 밖 <out>/shared_ae): fit/sub-0X/fold{k}_{변형}_seed{s}.npz(잠재), fit/sub-0X/run_info_fold{k}.json, readout/sub-0X.npz, summary/*.tsv
사용: s10_shared_ae.py fit --participant 01 --fold 1 --out <폴더> --design-freeze <커밋> [--threads 2]
      s10_shared_ae.py readout --participant 01 --out <폴더> --design-freeze <커밋>
      s10_shared_ae.py summarize --out <폴더> --stats-root <s10_stats>
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

import s4_common as c
import s10_align_data as A

HIDDEN = 256
WEIGHT = 5.0  # 원 논문 2AFC(생쥐 신경, 행동) 값
OFF_DIAG = 5e-3  # Barlow Twins 원 논문
EPS = 1e-3
LR, BATCH = 1e-4, 256
MAX_EPOCHS, PATIENCE = 600, 50  # 600은 계산 예산
D_CANDIDATES = (4, 8, 16, 32)
D_TOL = 0.01
SEEDS = (0, 1, 2, 3, 4)
VARIANTS = ("trained", "shuffled")
PARTS = ("s_vis", "s_sit", "p", "t_vis", "q_vis", "t_sit", "q_sit")

BOOT_SEED = 20261115


def mlp(i, o):
    import torch.nn as nn
    return nn.Sequential(nn.Linear(i, HIDDEN), nn.ReLU(), nn.Linear(HIDDEN, o))


def build(dims, d, seed):
    """dims: modality -> 입력 차원. 뇌는 칸 3개, 나머지는 2개."""
    import torch
    import torch.nn as nn
    torch.manual_seed(seed)
    n = dict(brain=3, vision=2, resid=2)
    m = nn.Module()
    m.enc = nn.ModuleDict({k: mlp(dims[k], n[k] * d) for k in ("brain", "vision", "resid")})
    m.dec = nn.ModuleDict({k: mlp(n[k] * d, dims[k]) for k in ("brain", "vision", "resid")})
    m.d = d
    return m


def encode(m, xb, xv, xr):
    d = m.d
    zb, zv, zr = m.enc["brain"](xb), m.enc["vision"](xv), m.enc["resid"](xr)
    return dict(s_vis=zb[:, :d], s_sit=zb[:, d:2 * d], p=zb[:, 2 * d:], t_vis=zv[:, :d], q_vis=zv[:, d:], t_sit=zr[:, :d], q_sit=zr[:, d:]), (zb, zv, zr)


def sq_dists(a, b):
    return (a.pow(2).sum(1)[:, None] + b.pow(2).sum(1)[None, :] - 2 * a @ b.T).clamp_min(0)


def cs_div(a, b):
    """Cauchy-Schwarz divergence의 Parzen 추정(Yi 외, 2025 식 2, 3). 두 Parzen 창(분산 σ²)의 곱의 적분은 분산 2σ² kernel이다.
    σ²는 [a; b] 안의 제곱 거리 중앙값의 절반(기울기 없음). 정규화 상수는 비에서 지워진다."""
    import torch
    with torch.no_grad():
        z = torch.cat([a, b])
        dd = sq_dists(z, z)
        s2 = (dd[~torch.eye(len(z), dtype=torch.bool)].median() / 2).clamp_min(1e-8)
    k = lambda x, y: torch.exp(-sq_dists(x, y) / (4 * s2)).mean()
    return -2 * torch.log(k(a, b)) + torch.log(k(a, a)) + torch.log(k(b, b))


def barlow(a, b):
    """Barlow Twins 교차상관 손실(Zbontar 외, 2021). 배치 안 표준화, 대각과 비대각 합을 차원 수로 나눔."""
    import torch
    a = (a - a.mean(0)) / (a.std(0) + 1e-6)
    b = (b - b.mean(0)) / (b.std(0) + 1e-6)
    cc = a.T @ b / len(a)
    on = torch.diagonal(cc)
    off = cc - torch.diag(on)
    return ((1 - on).pow(2).sum() + OFF_DIAG * off.pow(2).sum()) / a.shape[1]


def losses(m, xb, xv, xr):
    z, (zb, zv, zr) = encode(m, xb, xv, xr)
    mse = sum(((m.dec[k](zz) - x) ** 2).mean() for k, zz, x in (("brain", zb, xb), ("vision", zv, xv), ("resid", zr, xr)))
    cs = cs_div(z["s_vis"], z["t_vis"]) + cs_div(z["s_sit"], z["t_sit"])
    inv = sum(1.0 / (cs_div(z[a], z[b]) + EPS) for a, b in (("s_vis", "p"), ("s_sit", "p"), ("s_vis", "s_sit"), ("t_vis", "q_vis"), ("t_sit", "q_sit"), ("p", "q_vis"), ("p", "q_sit")))
    pair = barlow(z["s_vis"], z["t_vis"]) + barlow(z["s_sit"], z["t_sit"])
    return mse + WEIGHT * (cs + inv + pair), mse


def train(m, X, tr, va, scene_rows, seed):
    """X: modality -> 텐서(모든 행). scene_rows: 장면 modality에서 쓸 행(뇌 행 i에 짝지을 장면 행). 학습 행과 검증 행에만 쓴다.
    돌려주는 값: 학습 기록(dict)."""
    import torch
    g = torch.Generator().manual_seed(seed)
    opt = torch.optim.Adam(m.parameters(), lr=LR)
    sr = torch.as_tensor(scene_rows)
    tr_t, va_t = torch.as_tensor(tr), torch.as_tensor(va)
    best, best_state, best_epoch, bad = np.inf, None, -1, 0
    for epoch in range(MAX_EPOCHS):
        m.train()
        order = tr_t[torch.randperm(len(tr_t), generator=g)]
        for i in range(0, len(order), BATCH):
            b = order[i:i + BATCH]
            if len(b) < 32:
                continue
            loss, _ = losses(m, X["brain"][b], X["vision"][sr[b]], X["resid"][sr[b]])
            opt.zero_grad()
            loss.backward()
            opt.step()
        m.eval()
        with torch.no_grad():
            vl, vm = losses(m, X["brain"][va_t], X["vision"][sr[va_t]], X["resid"][sr[va_t]])
        if not torch.isfinite(vl):
            raise ValueError("검증 손실이 NaN이다")
        if vl.item() < best:
            best, best_epoch, bad, best_mse = vl.item(), epoch, 0, vm.item()
            best_state = {k: v.clone() for k, v in m.state_dict().items()}
        else:
            bad += 1
            if bad >= PATIENCE:
                break
    m.load_state_dict(best_state)
    return dict(best_val_loss=best, best_val_mse=best_mse, best_epoch=best_epoch, epochs_run=epoch + 1)


def latents(m, X):
    import torch
    m.eval()
    with torch.no_grad():
        z, _ = encode(m, X["brain"], X["vision"], X["resid"])
    return {k: v.numpy().astype(np.float32) for k, v in z.items()}


def fold_inputs(out, participant, k, split):
    vid, fold, xb, _, _ = A.load_brain_pca(out, participant, k)
    sc, info = A.scene_inputs(vid, fold, k, split)
    return vid, fold, dict(brain=xb, vision=sc["vision"], resid=sc["caption_resid"]), info


def fit(a):
    """참가자 한 명, 바깥 fold 하나. d 고르기(seed 0), trained seed 5개, shuffled seed 5개."""
    import torch
    c.guard(a.design_freeze)
    torch.set_num_threads(a.threads)
    split = c.load_split()
    q, k = f"sub-{a.participant}", int(a.fold)
    o = Path(a.out) / "shared_ae"
    (o / "fit" / q).mkdir(parents=True, exist_ok=True)
    started = time.time()
    vid, fold, Xn, info = fold_inputs(a.out, a.participant, k, split)
    X = {kk: torch.as_tensor(v, dtype=torch.float32) for kk, v in Xn.items()}
    dims = {kk: v.shape[1] for kk, v in Xn.items()}
    r = c.roles(k)
    tr, va = np.flatnonzero(np.isin(fold, r["train"])), np.flatnonzero(fold == r["val"])
    ident = np.arange(len(vid))
    cand = {}
    for d in D_CANDIDATES:
        m = build(dims, d, 0)
        cand[d] = (train(m, X, tr, va, ident, 0), m)
    mses = {d: v[0]["best_val_mse"] for d, v in cand.items()}
    lo = min(mses.values())
    d_pick = min(d for d, v in mses.items() if v <= lo * (1 + D_TOL))
    log = dict(participant=q, fold=k, scene=info, d_val_mse=mses, d_hist={d: v[0] for d, v in cand.items()}, d=d_pick, runs={},
               design_freeze=a.design_freeze, code_commit=c.START_HEAD, code_dirty=c.START_DIRTY)
    zones = A.zone_of(vid)
    for seed in SEEDS:
        for variant in VARIANTS:
            if variant == "trained" and seed == 0:
                hist, m = cand[d_pick]
            else:
                rows = ident.copy()
                if variant == "shuffled":
                    rng = np.random.default_rng(BOOT_SEED + 1000 * k + seed)
                    rows[tr] = A.zone_shuffle(tr, zones, rng)
                    rows[va] = A.zone_shuffle(va, zones, rng)
                m = build(dims, d_pick, seed)
                hist = train(m, X, tr, va, rows, seed)
            np.savez(o / "fit" / q / f"fold{k}_{variant}_seed{seed}.npz", video_id=vid, fold=fold, **latents(m, X))
            log["runs"][f"{variant}_seed{seed}"] = hist
    log["seconds"] = round(time.time() - started, 1)
    (o / "fit" / q / f"run_info_fold{k}.json").write_text(json.dumps(log, indent=1, default=float))
    print(json.dumps(dict(participant=q, fold=k, d=d_pick, d_val_mse=mses, seconds=log["seconds"])), flush=True)


# ---------- 읽기 ----------

def readout(out, participant, split):
    """참가자 한 명의 6 fold, 두 변형, seed 5개. 정서와 장면을 읽는 ridge는 검증 fold 행으로 학습(λ는 검증 fold 안 내용 묶음 5겹).
    <out>/shared_ae/readout/sub-0X.npz."""
    q = f"sub-{participant}"
    o = Path(out) / "shared_ae"
    canon = split.set_index("video_id").canonical_id
    res = {}
    for k in range(1, c.N_FOLDS + 1):
        vid, fold, Xn, _ = fold_inputs(out, participant, k, split)
        y, _, _ = A.ratings(split, vid)
        r = c.roles(k)
        tr, va, te = (np.flatnonzero(np.isin(fold, r["train"])), np.flatnonzero(fold == r["val"]), np.flatnonzero(fold == r["test"]))
        g = canon.loc[vid[va]].to_numpy()
        nuis = A.zfit(A.order_inputs(participant, vid, k, split), tr)
        pca = A.zfit(Xn["brain"], tr)
        res.setdefault("test_video_id", []).append(vid[te])
        res.setdefault("test_y", []).append(y[te])
        res.setdefault("pred_pca", []).append(A.ridge_cv(pca[va], y[va], g, [pca[te]])[0])
        for variant in VARIANTS:
            for seed in SEEDS:
                z = np.load(o / "fit" / q / f"fold{k}_{variant}_seed{seed}.npz")
                if not np.array_equal(z["video_id"], vid):
                    raise ValueError("잠재와 입력의 영상 순서가 다르다")
                Z = {p: A.zfit(z[p], tr) for p in PARTS}
                tag = f"{variant}_seed{seed}"
                brain_sh, scene_sh = np.c_[Z["s_vis"], Z["s_sit"]], np.c_[Z["t_vis"], Z["t_sit"]]
                ins = dict(vis=Z["s_vis"], vis_sit=brain_sh, all=np.c_[brain_sh, Z["p"]], scene_vis=Z["t_vis"], scene_vis_sit=scene_sh)
                for name, x in ins.items():
                    res.setdefault(f"pred_{name}_{tag}", []).append(A.ridge_cv(x[va], y[va], g, [x[te]])[0])
                # ③ 옮기기: 장면 쪽 검증 행으로 학습한 ridge를 뇌 쪽 시험 행에. 바닥: 뇌 PCA → 장면 잠재(학습 행) 뒤 같은 ridge.
                t_hat = A.ridge_val(pca, np.c_[z["t_vis"], z["t_sit"]].astype(np.float64), tr, va, pca[te])
                sm, ss = np.c_[z["t_vis"], z["t_sit"]][tr].mean(0), np.c_[z["t_vis"], z["t_sit"]][tr].std(0)
                floor_in = (t_hat - sm) / np.where(ss > 0, ss, 1.0)
                pt, pf = A.ridge_cv(scene_sh[va], y[va], g, [brain_sh[te], floor_in])
                res.setdefault(f"pred_transfer_{tag}", []).append(pt)
                res.setdefault(f"pred_floor_{tag}", []).append(pf)
                # 정렬(시험, 학습)
                for a_, b_ in (("s_vis", "t_vis"), ("s_sit", "t_sit")):
                    res.setdefault(f"align_test_{a_}_{tag}", []).append(np.nanmean(A.col_r(Z[a_][te], Z[b_][te])))
                    res.setdefault(f"align_train_{a_}_{tag}", []).append(np.nanmean(A.col_r(Z[a_][tr], Z[b_][tr])))
                    res.setdefault(f"latent_{a_}_{tag}", []).append(Z[a_][te])
                    res.setdefault(f"latent_{b_}_{tag}", []).append(Z[b_][te])
                # 칸 사이 섞임(증분 R², 시험)
                r2 = lambda xs, tgt: A.r2_weighted(Xn[tgt][te], A.ridge_cv(xs[va], Xn[tgt][va], g, [xs[te]], per_target=False)[0])
                inc = dict(sit_adds_vision=r2(brain_sh, "vision") - r2(Z["s_vis"], "vision"),
                           p_adds_vision=r2(ins["all"], "vision") - r2(brain_sh, "vision"),
                           p_adds_resid=r2(ins["all"], "resid") - r2(brain_sh, "resid"))
                res.setdefault(f"mix_{tag}", []).append(np.array([inc[x] for x in MIX]))
                # 제시 순서 변수 → p (기술 값)
                res.setdefault(f"order_p_{tag}", []).append(A.r2_weighted(Z["p"][te], A.ridge_cv(nuis[va], Z["p"][va], g, [nuis[te]], per_target=False)[0]))
    o2 = o / "readout"
    o2.mkdir(parents=True, exist_ok=True)
    arrays = {k_: (np.array(v) if (k_.startswith(("align_", "mix_", "order_"))) else np.concatenate(v)) for k_, v in res.items()}
    np.savez(o2 / f"{q}.npz", **arrays)
    print(f"{q} readout 저장", flush=True)


MIX = ("sit_adds_vision", "p_adds_vision", "p_adds_resid")


# ---------- 요약 ----------

def summarize(a):
    import s10_stats as st
    split = c.load_split()
    o = Path(a.out) / "shared_ae"
    R = {q: dict(np.load(o / "readout" / f"sub-{q}.npz")) for q in A.PARTICIPANTS}
    _, names, keep27 = A.ratings(split, split.video_id.to_numpy()[:1])
    xmap = A.key_test_x(a.stats_root)
    x27 = np.array([xmap.get(e, np.nan) for e in names])[keep27]
    U = np.array(sorted(set().union(*[set(R[q]["test_video_id"].tolist()) for q in R])), np.int64)
    codes, n_units = st.unit_codes(split.set_index("video_id").loc[U].canonical_id.to_numpy())
    W = st.bootstrap_counts(n_units, a.n_boot, np.random.default_rng(BOOT_SEED))
    reads = ("vis", "vis_sit", "all", "scene_vis", "scene_vis_sit", "transfer", "floor")
    point, boot, seed_point = {}, {}, {}
    for q in A.PARTICIPANTS:
        d = R[q]
        w = W[:, codes[np.searchsorted(U, d["test_video_id"])]]
        preds = {"pca": d["pred_pca"]}
        for v in VARIANTS:
            for name in reads:
                preds[f"{name}|{v}"] = np.mean([d[f"pred_{name}_{v}_seed{s}"] for s in SEEDS], 0)
                for s in SEEDS:
                    seed_point[(q, name, v, s)] = st.pearson_columns(d["test_y"], d[f"pred_{name}_{v}_seed{s}"])
        point[q] = {m: st.pearson_columns(d["test_y"], p) for m, p in preds.items()}
        boot[q] = st.boot_r(w, d["test_y"], preds)
        # 정렬 bootstrap(시험 잠재를 모아 차원별 r, seed 평균)
        for v in VARIANTS:
            for a_, b_ in (("s_vis", "t_vis"), ("s_sit", "t_sit")):
                pts = [np.nanmean(st.pearson_columns(d[f"latent_{a_}_{v}_seed{s}"], d[f"latent_{b_}_{v}_seed{s}"])) for s in SEEDS]
                bts = [np.nanmean(st.boot_r(w, d[f"latent_{a_}_{v}_seed{s}"], {"x": d[f"latent_{b_}_{v}_seed{s}"]})["x"], 1) for s in SEEDS]
                point[q][f"align {a_}~{b_}|{v}"] = float(np.mean(pts))
                boot[q][f"align {a_}~{b_}|{v}"] = np.mean(bts, 0)
    P = A.PARTICIPANTS
    sets = {"34": np.ones(len(names), bool), "27": keep27}
    rows = []
    for m in point[P[0]]:
        if m.startswith("align"):
            per = [point[q][m] for q in P]
            rows += [dict(read=m, participant=q, set="차원 평균", r=per[i]) for i, q in enumerate(P)] + [dict(read=m, participant="mean5", set="차원 평균", r=float(np.mean(per)))]
            continue
        for sn, msk in sets.items():
            per = [float(np.nanmean(point[q][m][msk])) for q in P]
            rows += [dict(read=m, participant=q, set=sn, r=per[i]) for i, q in enumerate(P)] + [dict(read=m, participant="mean5", set=sn, r=float(np.mean(per)))]

    def diff(ma, mb, label, sn="34"):
        if ma.startswith("align"):
            per = [point[q][ma] - point[q][mb] for q in P]
            db = np.mean([boot[q][ma] - boot[q][mb] for q in P], 0)
        else:
            msk = sets[sn]
            per = [float(np.nanmean(point[q][ma][msk]) - np.nanmean(point[q][mb][msk])) for q in P]
            db = np.mean([np.nanmean(boot[q][ma][:, msk], 1) - np.nanmean(boot[q][mb][:, msk], 1) for q in P], 0)
        dd = float(np.mean(per))
        lo, hi = st.basic_ci(np.array([dd]), db[:, None])
        return dict(comparison=label, a=ma, b=mb, set=sn if not ma.startswith("align") else "차원 평균", diff=dd, ci_low=float(lo[0]), ci_high=float(hi[0]),
                    p=float(st.centered_p(np.array([dd]), db[:, None])[0]), n_positive=int(sum(x > 0 for x in per)), n_negative=int(sum(x < 0 for x in per)))
    diffs = []
    for a_, b_ in (("s_vis", "t_vis"), ("s_sit", "t_sit")):
        diffs.append(diff(f"align {a_}~{b_}|trained", f"align {a_}~{b_}|shuffled", f"① 정렬 {a_}~{b_}: trained − shuffled"))
    for sn in sets:
        for v in VARIANTS:
            diffs.append(diff(f"vis_sit|{v}", f"vis|{v}", f"Δsit_brain ({v})", sn))
            diffs.append(diff(f"scene_vis_sit|{v}", f"scene_vis|{v}", f"Δsit_scene ({v})", sn))
            diffs.append(diff(f"all|{v}", f"vis_sit|{v}", f"Δpriv, 기술 값 ({v})", sn))
        diffs.append(diff("transfer|trained", "floor|trained", "③ 옮긴 r − 선형 2단계 바닥", sn))
        diffs.append(diff("transfer|trained", "transfer|shuffled", "③ 옮긴 r: trained − shuffled", sn))
        diffs.append(diff("transfer|trained", "vis_sit|trained", "③ 옮긴 r − 뇌 쪽 직접", sn))
        diffs.append(diff("all|trained", "pca", "세 칸 − 뇌 PCA 256", sn))
    # 정서별 표
    per_e = []
    for e, name in enumerate(names):
        row = dict(emotion=name, in27=bool(keep27[e]))
        for m in point[P[0]]:
            if not m.startswith("align"):
                row[m] = float(np.mean([point[q][m][e] for q in P]))
        per_e.append(row)
    PE = pd.DataFrame(per_e)
    PE["dsit_brain"] = PE["vis_sit|trained"] - PE["vis|trained"]
    PE["dsit_scene"] = PE["scene_vis_sit|trained"] - PE["scene_vis|trained"]
    PE["dpriv"] = PE["all|trained"] - PE["vis_sit|trained"]
    PE.loc[PE.in27, "x_key_test"] = x27
    # H2: 편순위상관(Δsit_brain, x | Δsit_scene), 참가자마다와 5명 평균, seed마다
    rng = np.random.default_rng(BOOT_SEED)
    perms = np.stack([rng.permutation(len(x27)) for _ in range(a.n_perm)])
    h2 = []

    def h2_row(who, seed, db, ds):
        rho = A.partial_spearman(db, x27, ds)
        null = np.array([A.partial_spearman(db, x27[pp], ds) for pp in perms]) if seed == "mean" else None
        return dict(participant=who, seed=seed, partial_rho=rho, plain_rho=float(pd.Series(db).corr(pd.Series(x27), method="spearman")),
                    p_perm=float((1 + (np.abs(null) >= abs(rho)).sum()) / (a.n_perm + 1)) if null is not None else np.nan)
    for q in P + ("mean5",):
        if q == "mean5":
            db, ds = PE.loc[PE.in27, "dsit_brain"].to_numpy(), PE.loc[PE.in27, "dsit_scene"].to_numpy()
        else:
            db = (point[q]["vis_sit|trained"] - point[q]["vis|trained"])[keep27]
            ds = (point[q]["scene_vis_sit|trained"] - point[q]["scene_vis|trained"])[keep27]
        h2.append(h2_row(q, "mean", db, ds))
    for s in SEEDS:
        db = np.mean([(seed_point[(q, "vis_sit", "trained", s)] - seed_point[(q, "vis", "trained", s)])[keep27] for q in P], 0)
        ds = np.mean([(seed_point[(q, "scene_vis_sit", "trained", s)] - seed_point[(q, "scene_vis", "trained", s)])[keep27] for q in P], 0)
        h2.append(h2_row("mean5", s, db, ds))
    # ③ 모양: 옮긴 r과 뇌 쪽 직접 r의 정서 간 편상관(장면 쪽 시험 r 통제), 34개, bootstrap
    shape = []
    tb = np.mean([boot[q]["transfer|trained"] for q in P], 0)
    bb = np.mean([boot[q]["vis_sit|trained"] for q in P], 0)
    sb = np.mean([boot[q]["scene_vis_sit|trained"] for q in P], 0)
    pc = A.partial_pearson(PE["transfer|trained"].to_numpy(), PE["vis_sit|trained"].to_numpy(), PE["scene_vis_sit|trained"].to_numpy())
    pcb = np.array([A.partial_pearson(tb[i], bb[i], sb[i]) if np.isfinite(tb[i]).all() and np.isfinite(bb[i]).all() and np.isfinite(sb[i]).all() else np.nan for i in range(len(tb))])
    lo, hi = st.basic_ci(np.array([pc]), pcb[:, None])
    shape.append(dict(read="③ 옮긴 r ~ 뇌 쪽 직접 r | 장면 쪽 r (34개 정서, 5명 평균)", partial_r=pc, ci_low=float(lo[0]), ci_high=float(hi[0]),
                      plain_r=float(np.corrcoef(PE["transfer|trained"], PE["vis_sit|trained"])[0, 1])))
    # 칸 사이 섞임과 제시 순서(기술 값)
    mix_rows, order_rows, align_tr = [], [], []
    for q in P:
        d = R[q]
        for v in VARIANTS:
            mx = np.mean([d[f"mix_{v}_seed{s}"] for s in SEEDS], 0).mean(0)
            mix_rows += [dict(participant=q, variant=v, read=MIX[j], incremental_r2=float(mx[j])) for j in range(len(MIX))]
            order_rows.append(dict(participant=q, variant=v, read="제시 순서 변수 → p, 시험 R²", r2=float(np.mean([d[f"order_p_{v}_seed{s}"] for s in SEEDS]))))
            for a_ in ("s_vis", "s_sit"):
                align_tr.append(dict(participant=q, variant=v, pair=a_, train=float(np.mean([d[f"align_train_{a_}_{v}_seed{s}"] for s in SEEDS])),
                                     test_fold_mean=float(np.mean([d[f"align_test_{a_}_{v}_seed{s}"] for s in SEEDS]))))
    MX = pd.DataFrame(mix_rows)
    mix_cmp = MX.pivot_table(index=["participant", "read"], columns="variant", values="incremental_r2").reset_index()
    mix_cmp["trained_minus_shuffled"] = mix_cmp["trained"] - mix_cmp["shuffled"]
    o2 = o / "summary"
    o2.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(o2 / "scores.tsv", sep="\t", index=False)
    pd.DataFrame(diffs).to_csv(o2 / "differences.tsv", sep="\t", index=False)
    PE.to_csv(o2 / "per_emotion.tsv", sep="\t", index=False)
    pd.DataFrame(h2).to_csv(o2 / "h2_partial_rho.tsv", sep="\t", index=False)
    pd.DataFrame(shape).to_csv(o2 / "transfer_shape.tsv", sep="\t", index=False)
    mix_cmp.to_csv(o2 / "mixing.tsv", sep="\t", index=False)
    pd.DataFrame(order_rows).to_csv(o2 / "order.tsv", sep="\t", index=False)
    pd.DataFrame(align_tr).to_csv(o2 / "alignment_train_test.tsv", sep="\t", index=False)
    d_used = {}
    for q in P:
        for k in range(1, c.N_FOLDS + 1):
            d_used[f"{q}_fold{k}"] = json.loads((o / "fit" / f"sub-{q}" / f"run_info_fold{k}.json").read_text())["d"]
    (o2 / "run_info.json").write_text(json.dumps(dict(participants=P, n_boot=a.n_boot, n_perm=a.n_perm, boot_seed=BOOT_SEED, n_units=n_units, d_used=d_used,
                                                    settings=dict(hidden=HIDDEN, weight=WEIGHT, off_diag=OFF_DIAG, lr=LR, batch=BATCH, max_epochs=MAX_EPOCHS, patience=PATIENCE,
                                                                  d_candidates=D_CANDIDATES, d_tol=D_TOL, seeds=SEEDS), code_commit=c.START_HEAD, code_dirty=c.START_DIRTY), indent=1, ensure_ascii=False))
    S = pd.DataFrame(rows)
    print(S[S.participant == "mean5"].pivot_table(index="read", columns="set", values="r").round(3).to_string())
    print(pd.DataFrame(diffs).round(3).to_string(index=False))
    print(pd.DataFrame(h2).round(3).to_string(index=False))
    print(pd.DataFrame(shape).round(3).to_string(index=False))
    print(mix_cmp.groupby("read")[["trained", "shuffled", "trained_minus_shuffled"]].mean().round(4).to_string(), flush=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 6-4i ① Shared-AE와 ③")
    ap.add_argument("step", choices=("fit", "readout", "summarize"))
    ap.add_argument("--participant")
    ap.add_argument("--fold", type=int)
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", default="")
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--stats-root")
    ap.add_argument("--n-boot", type=int, default=10_000)
    ap.add_argument("--n-perm", type=int, default=10_000)
    a = ap.parse_args(argv)
    if a.step == "fit":
        if not (a.participant and a.fold):
            raise SystemExit("fit에는 --participant와 --fold가 필요하다")
        fit(a)
    elif a.step == "readout":
        c.guard(a.design_freeze)
        readout(a.out, a.participant, c.load_split())
    else:
        summarize(a)


if __name__ == "__main__":
    main()
