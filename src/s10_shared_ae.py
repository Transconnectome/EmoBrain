#!/usr/bin/env python3
"""S10 6-4i ①과 ③(01 6-4i, 11/22). Shared-AE(Yi 외, ICLR 2025)의 공식 코드(external/repos/Shared-AE, commit fa5e74b)를 세 modality(뇌, Vision, 캡션 잔차)에 쓴다. CPU.

공식 코드에서 그대로 가져오는 것
- CS 손실: n_modalities/multi_loss.py의 csLoss(kernel exp(−거리² / ksize), r = log(√(mean Gxx · mean Gzz) / mean Gxz)).
- inverse CS: 가중치 / csLoss(two_modalities/train.py, n_modalities/train.py의 weight/loss).
- 손실 조립: 재구성 MSE에 입력 차원 수를 곱해 더한다(train.py의 loss1 * pose_dim * newW, 창 크기 1이라 newW = 1).
- 구조: encoder 출력 embedding(512) → modality마다 선형층(lamdba, bottleneck = 칸 차원 합) → 공유 칸과 고유 칸 선형층(n_modalities/modeldecodeorth2.py의
  imagedense, imagepreviate) → [고유, 공유]를 받는 modality별 decoder. 공식 세 modality 코드는 공유 칸 층의 입력 크기가 bottleneck × 3으로 적혀 있어
  그대로는 돌지 않는다(자기 bottleneck만 받는 논문 식 si = Ws zi + bs로 고침).
- optimizer: Adam, learning rate 1e-4, batch 256(논문), 마지막 모델. 학습 길이는 논문의 gradient step 수(STEPS)에 맞춘다(epoch 100은 논문 자료에서 약 3,200 step).
논문 값(석진 님 11/22 "논문값으로 일단 진행"): kernel 크기 15(논문 A.9 "σ = 15"를 공식 코드의 kernel_size 자리에 둠), CS와 inverse CS 가중치 5(논문의 2AFC 생쥐 자료,
  세 modality 시연도 이 자료). 잠재 차원 d는 논문 A.9.2처럼 재구성 손실로 고른다(D_CANDIDATES, 검증 fold, 최소값의 1% 안 가장 작은 값).
공식 코드와 다른 점(01 6-4i에 표로 적음)
- encoder: 공식은 시계열 창을 받는 1D ResNet-18이다. 우리 입력은 영상당 벡터 하나라 MLP(입력 → 512)로 바꾼다. decoder도 같은 이유로 MLP.
- 뇌는 공유 칸이 둘이다. s_vis는 Vision과, s_sit는 캡션 잔차와 짝이다(두 modality 손실을 짝마다 쓴다). Vision은 [t_vis, q_vis], 캡션 잔차는 [t_sit, q_sit].
- 표본 짝 손실(우리가 더함): 공식 CS 항은 배치 안 모든 쌍의 kernel 평균이라 같은 영상끼리 맞추지 않는다. ③에 필요해 공유 칸 짝에 Barlow Twins
  (Zbontar 외, 2021) 교차상관 손실을 더한다. 비대각 가중치 5e-3(원 논문), 합은 d로 나눔, 가중치는 공유 CS 항과 같은 5.
손실 = Σ_m MSE_m × 차원_m + 5 × [CS(s_vis, t_vis) + CS(s_sit, t_sit)]
       + 5 / CS(s_vis, p) + 5 / CS(s_sit, p) + 5 / CS(t_vis, q_vis) + 5 / CS(t_sit, q_sit) + 5 / CS(p, q_vis) + 5 / CS(p, q_sit)
       + 5 × [BT(s_vis, t_vis) + BT(s_sit, t_sit)]
변형: trained, shuffled(학습과 검증 행에서 캡션 구역 안 뇌와 장면의 짝을 섞음. 시험은 원래 짝).
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
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

import s4_common as c
import s10_align_data as A

OFFICIAL = c.REPO / "external" / "repos" / "Shared-AE"
OFFICIAL_COMMIT = "fa5e74b5067adbe0784d3c6142ded9740631bd59"
EMB = 512  # 공식 encoder 출력 embedding 크기
KERNEL = 15.0  # 논문 A.9
WEIGHT = 5.0  # 논문 A.9, 2AFC 자료
OFF_DIAG = 5e-3  # Barlow Twins 원 논문
LR, BATCH = 1e-4, 256  # 논문 3절과 A.7
STEPS = 3200  # 논문 3D Shapes의 gradient step 수(학습 8,000개 / batch 256 = 32 step × 100 epoch). 우리 학습 행은 약 1,400개라 100 epoch면 약 600 step으로 수렴하지 않는다
D_CANDIDATES = (4, 8, 16, 32)
D_TOL = 0.01
SEEDS = (0, 1, 2, 3, 4)
VARIANTS = ("trained", "shuffled")
PARTS = ("s_vis", "s_sit", "p", "t_vis", "q_vis", "t_sit", "q_sit")
SLOTS = dict(brain=("s_vis", "s_sit", "p"), vision=("t_vis", "q_vis"), resid=("t_sit", "q_sit"))
BOOT_SEED = 20261115


def official_cs():
    """공식 csLoss. 저장소 commit이 고정한 값과 다르면 멈춘다."""
    import subprocess
    head = subprocess.run(["git", "-C", str(OFFICIAL), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    if head != OFFICIAL_COMMIT:
        raise SystemExit(f"external/repos/Shared-AE가 {OFFICIAL_COMMIT[:7]}이 아니다({head[:7]}). git submodule update --init external/repos/Shared-AE")
    if str(OFFICIAL) not in sys.path:
        sys.path.insert(0, str(OFFICIAL))
    from n_modalities.multi_loss import csLoss
    return csLoss(KERNEL)


def build(dims, d, seed):
    """공식 modeldecodeorth2.Decoder의 구조를 벡터 입력에 맞춘 것. dims: modality -> 입력 차원."""
    import torch
    import torch.nn as nn
    torch.manual_seed(seed)
    m = nn.Module()
    m.enc = nn.ModuleDict({k: nn.Sequential(nn.Linear(dims[k], EMB), nn.ReLU()) for k in SLOTS})  # 공식 ResNet encoder 자리
    m.lamdba = nn.ModuleDict({k: nn.Linear(EMB, d * len(SLOTS[k])) for k in SLOTS})
    m.head = nn.ModuleDict({s: nn.Linear(d * len(SLOTS[k]), d) for k in SLOTS for s in SLOTS[k]})  # imagedense, imagepreviate 자리
    m.dec = nn.ModuleDict({k: nn.Sequential(nn.Linear(d * len(SLOTS[k]), EMB), nn.ReLU(), nn.Linear(EMB, dims[k])) for k in SLOTS})
    m.d = d
    return m


def encode(m, xb, xv, xr):
    z = {}
    for k, x in (("brain", xb), ("vision", xv), ("resid", xr)):
        h = m.lamdba[k](m.enc[k](x))
        for s in SLOTS[k]:
            z[s] = m.head[s](h)
    return z


def barlow(a, b):
    """Barlow Twins 교차상관 손실(Zbontar 외, 2021). 배치 안 표준화, 대각과 비대각 합을 차원 수로 나눔."""
    import torch
    a = (a - a.mean(0)) / (a.std(0) + 1e-6)
    b = (b - b.mean(0)) / (b.std(0) + 1e-6)
    cc = a.T @ b / len(a)
    on = torch.diagonal(cc)
    off = cc - torch.diag(on)
    return ((1 - on).pow(2).sum() + OFF_DIAG * off.pow(2).sum()) / a.shape[1]


def losses(m, cs, xb, xv, xr):
    """공식 train.py의 손실 조립(재구성 MSE × 차원 + 가중치 × CS + 가중치 / CS)에 짝 손실을 더한 것. 돌려주는 값: (전체, 재구성 MSE 합(차원 곱 전))."""
    import torch
    z = encode(m, xb, xv, xr)
    mse = 0.0
    rec = 0.0
    for k, x in (("brain", xb), ("vision", xv), ("resid", xr)):
        e = ((m.dec[k](torch.cat([z[s] for s in SLOTS[k]], 1)) - x) ** 2).mean()
        mse = mse + e * x.shape[1]
        rec = rec + e
    shared = cs(z["s_vis"], z["t_vis"]) + cs(z["s_sit"], z["t_sit"])
    inv = sum(WEIGHT / cs(z[a], z[b]) for a, b in (("s_vis", "p"), ("s_sit", "p"), ("t_vis", "q_vis"), ("t_sit", "q_sit"), ("p", "q_vis"), ("p", "q_sit")))
    pair = barlow(z["s_vis"], z["t_vis"]) + barlow(z["s_sit"], z["t_sit"])
    return mse + WEIGHT * shared + inv + WEIGHT * pair, rec


def train(m, cs, X, tr, va, scene_rows, seed):
    """X: modality -> 텐서(모든 행). scene_rows: 뇌 행 i에 짝지을 장면 행(학습과 검증 행에만 씀). STEPS 고정, 마지막 모델(논문).
    돌려주는 값: epoch마다 검증 재구성 MSE와 전체 손실 기록."""
    import torch
    g = torch.Generator().manual_seed(seed)
    opt = torch.optim.Adam(m.parameters(), lr=LR)
    sr = torch.as_tensor(scene_rows)
    tr_t, va_t = torch.as_tensor(tr), torch.as_tensor(va)
    curve, step = [], 0
    while step < STEPS:
        epoch = len(curve)
        m.train()
        order = tr_t[torch.randperm(len(tr_t), generator=g)]
        for i in range(0, len(order), BATCH):
            b = order[i:i + BATCH]
            if len(b) < 32 or step >= STEPS:
                continue
            step += 1
            loss, _ = losses(m, cs, X["brain"][b], X["vision"][sr[b]], X["resid"][sr[b]])
            if not torch.isfinite(loss):
                raise ValueError(f"학습 손실이 유한하지 않다(epoch {epoch})")
            opt.zero_grad()
            loss.backward()
            opt.step()
        m.eval()
        with torch.no_grad():
            vl, vr = losses(m, cs, X["brain"][va_t], X["vision"][sr[va_t]], X["resid"][sr[va_t]])
        curve.append((float(vl), float(vr)))
    return dict(steps=step, epochs=len(curve), val_loss_last=curve[-1][0], val_rec_last=curve[-1][1], val_rec_curve=[r for _, r in curve], val_loss_curve=[l for l, _ in curve])


def latents(m, X):
    import torch
    m.eval()
    with torch.no_grad():
        z = encode(m, X["brain"], X["vision"], X["resid"])
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
    cs = official_cs()
    vid, fold, Xn, info = fold_inputs(a.out, a.participant, k, split)
    X = {kk: torch.as_tensor(v, dtype=torch.float32) for kk, v in Xn.items()}
    dims = {kk: v.shape[1] for kk, v in Xn.items()}
    r = c.roles(k)
    tr, va = np.flatnonzero(np.isin(fold, r["train"])), np.flatnonzero(fold == r["val"])
    ident = np.arange(len(vid))
    cand = {}
    for d in D_CANDIDATES:
        m = build(dims, d, 0)
        cand[d] = (train(m, cs, X, tr, va, ident, 0), m)
    mses = {d: v[0]["val_rec_last"] for d, v in cand.items()}
    lo = min(mses.values())
    d_pick = min(d for d, v in mses.items() if v <= lo * (1 + D_TOL))
    log = dict(participant=q, fold=k, scene=info, d_val_mse=mses, d_hist={d: v[0] for d, v in cand.items()}, d=d_pick, runs={}, official_commit=OFFICIAL_COMMIT,
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
                hist = train(m, cs, X, tr, va, rows, seed)
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
                                                    settings=dict(official_commit=OFFICIAL_COMMIT, emb=EMB, kernel=KERNEL, weight=WEIGHT, off_diag=OFF_DIAG, lr=LR, batch=BATCH, steps=STEPS,
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
