#!/usr/bin/env python3
"""S10 6-4i ②와 ③(01 6-4i, 11/22). Universal Sparse Autoencoder(Thasarathan 외, ICML 2025)의 공식 코드
(external/repos/UniversalSAE, commit 8bfee2b)로 뇌 5명, Vision feature, Caption feature가 같이 쓰는 개념 사전을 학습한다. CPU.

공식 코드에서 그대로 쓰는 것(uni_demo.py, config.yaml, universal_sae/train.py)
- 모델: overcomplete.sae.TopKSAE(encoder_module "mlp_bn_1" = Linear → BatchNorm → ReLU, TopK, 사전 방향 l2 정규화, decoder = 개념 활성 @ 사전).
- 학습 함수: universal_sae.train.train_cross_prediction_saes(매 step 모델 i를 무작위로 골라 그 개념 활성으로 모든 모델을 복원하고 손실을 더한 뒤
  모델 i의 optimizer만 step, gradient clipping 1.0). monitoring 0(그림과 wandb 기록 끔, WANDB_MODE=disabled). 체크포인트는 공식 함수가 실행 폴더에 쓰므로
  임시 폴더에서 돌리고 지운다.
- 손실: overcomplete.sae.losses.top_k_auxiliary_loss_L1(L1 평균 + 0.1 × 안 고른 개념 절반으로 남은 오차 맞히기).
- optimizer와 scheduler: 모델마다 AdamW(LR, weight decay 1e-5), CosineScheduler(LR → 1e-6, warmup 1 epoch, 시작 1e-6),
  total_iters = 표본 수 / batch × epoch(uni_demo.py와 같은 식). batch 32, gradient clipping 1.0.
- learning rate와 학습 길이(11/22 석진 님 결정): 공식 config(3e-4, 30 epoch)로는 우리 자료(학습 영상 약 1,300개)에서 학습되지 않았다. fold 1, 개념 50, k 5, seed 0에서
  Vision 하나만 넣은 SAE도 시험 자기 복원 R² 0.05였다. 공식 사전은 개념 방향을 늘 길이 1로 두므로 복원 크기는 encoder BatchNorm의 크기 변수로만 맞춰지는데,
  3e-4에서는 이 값이 모델마다 받는 갱신 수백 번 안에 맞춰지지 않는다. 공식 학습 함수의 기본값 3e-3에서는 Vision 하나 0.60(학습 행 PCA 5개 성분 0.60과 같음),
  일곱 모델은 300 epoch에서 0.03, 1,000 epoch에서 뇌 자기 복원 0.13~0.18, 캡션 0.38, 뇌 → 캡션 0.11~0.13이었다. 그래서 3e-3, 1,000 epoch를 쓴다.
공식 코드와 다른 점(01 6-4i에 적음)
- 입력: 일곱 모델 모두 원 특징을 학습 행으로 차원마다 표준화한 뒤 PCA 256(s10_align_data). 원 논문 모델은 가장 커도 768차원.
- 뇌 다섯 모델의 복원 손실에 1/5씩 가중치(일곱 가운데 다섯인 뇌에 공통인 분산에 사전이 맞춰지지 않게). 공식 학습 함수는 그대로 두고,
  모델마다 decode를 감싸 지금 복원하는 모델 이름을 기록하고 손실 함수에 그 가중치를 곱하는 wrapper만 넣는다.
- 개념 수 K와 k: --k-concepts, --topk로 받는다(석진 님 결정 대기, 01 6-4i). select 단계는 추천안이다. 공식 코드의 hyperparameter 탐색 기준
  (train.py _avg_non_diagonal, 모델 사이 교차 복원 R²의 대각 밖 평균)을 검증 fold에 쓰고 후보는 Zeng(2026)의 범위(K 25, 50, 100 × k 2, 5).
- 변형: trained, shuffled(학습과 검증 행에서 캡션 구역 안 장면 행만 섞음, 다섯 뇌끼리 짝은 그대로), untrained(학습 없음. seed 재현 기준용).
읽기(시험 행): 7 × 7 복원 R², 개념마다 모델별 켜지는 비율과 평균 활성, 뇌 평균 활성과 장면 활성의 상관, 다섯 뇌의 참가자 사이 상관,
  ③ 옮기기(장면 쪽 개념 활성으로 학습한 정서 ridge를 각 뇌 encoder의 시험 활성에, 직접과 선형 2단계 바닥),
  뇌 전용 후보 점검(장면 PCA → 뇌 평균 활성의 시험 r, 제시 순서 변수 → 각 뇌 활성의 시험 r, 시험 행 섞기 1,000회 null의 95번째 백분위).
출력(레포 밖 <out>/usae): fit/fold{k}_{변형}_seed{s}.npz(Z, D), select/fold{k}.json, readout/fold{k}.npz, summary/*.tsv
사용: s10_usae.py select --fold 1 --out <폴더> --design-freeze <커밋>
      s10_usae.py fit --fold 1 --out <폴더> --design-freeze <커밋> (--k-concepts 50 --topk 5 | --from-select)
      s10_usae.py summarize --out <폴더>
환경: 공식 패키지가 그림용으로 matplotlib, opencv, scikit-image를 import한다. 학습 환경을 건드리지 않도록 이것만 따로 설치한 폴더를 USAE_EXTRA_SITE로 준다.
"""
import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

import s4_common as c
import s10_align_data as A

OFFICIAL = c.REPO / "external" / "repos" / "UniversalSAE"
OFFICIAL_COMMIT = "8bfee2bd5eaa4355c2cb6543bb17f5c3ae7a3928"
LR, FINAL_LR, WEIGHT_DECAY = 3e-3, 1e-6, 1e-5  # LR은 uni_demo.py prepare_and_train_universal_sae의 기본값(config.yaml의 3e-4로는 우리 자료에서 학습되지 않음, 11/22 석진 님 결정)
BATCH, EPOCHS, WARMUP_EPOCHS, CLIP = 32, 1000, 1.0, 1.0  # batch, warmup, clipping은 config.yaml과 uni_demo.py. EPOCHS는 공식 30 대신 1,000(11/22 석진 님 결정, 아래 docstring)
ENCODER, DICT_NORM = "mlp_bn_1", "l2"  # config.yaml sae_params
SELECT_GRID = [(25, 2), (25, 5), (50, 2), (50, 5), (100, 2), (100, 5)]  # Zeng(2026) 부록 D의 K, k 범위
SEEDS = (0, 1, 2, 3, 4)
VARIANTS = ("trained", "shuffled", "untrained")
N_NULL = 1000
BOOT_SEED = 20261115


def official():
    """공식 저장소의 모듈. commit이 고정한 값과 다르면 멈춘다."""
    import subprocess
    head = subprocess.run(["git", "-C", str(OFFICIAL), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    if head != OFFICIAL_COMMIT:
        raise SystemExit(f"external/repos/UniversalSAE가 {OFFICIAL_COMMIT[:7]}이 아니다({head[:7]}). git submodule update --init external/repos/UniversalSAE")
    os.environ.setdefault("WANDB_MODE", "disabled")
    extra = os.environ.get("USAE_EXTRA_SITE")
    for p in ([extra] if extra else []) + [str(OFFICIAL)]:
        if p not in sys.path:
            sys.path.insert(0, p)
    from overcomplete.sae import TopKSAE
    from overcomplete.sae.optimizer import CosineScheduler
    from overcomplete.sae.losses import top_k_auxiliary_loss_L1, top_k_auxiliary_loss
    import universal_sae.train as UT
    return TopKSAE, CosineScheduler, dict(L1=top_k_auxiliary_loss_L1, L2=top_k_auxiliary_loss), UT


def models_of():
    return tuple(f"sub-{q}" for q in A.PARTICIPANTS) + ("vision", "caption")


def weights_of(names):
    nb = sum(n.startswith("sub-") for n in names)
    return {n: (1.0 / nb if n.startswith("sub-") else 1.0) for n in names}


class Acts:
    """공식 학습 함수가 받는 꼴: ({모델: (1, 차원)}, 라벨). rows는 쓰는 행, scene_rows는 장면 모델에서 행 r에 짝지을 행."""

    def __init__(self, X, names, rows, scene_rows):
        self.X, self.names, self.rows, self.scene_rows = X, names, np.asarray(rows), np.asarray(scene_rows)

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        r = int(self.rows[i])
        return {n: self.X[n][int(self.scene_rows[r]) if n in ("vision", "caption") else r][None, :] for n in self.names}, 0


def train_official(X, names, tr, scene_rows, n_concepts, topk, seed, workdir, variant, divide_norm=False, loss="L1"):
    """공식 TopKSAE와 train_cross_prediction_saes로 학습. untrained면 초기화만. 돌려주는 값: {모델: SAE}."""
    import torch
    TopKSAE, CosineScheduler, crits, UT = official()
    crit = crits[loss]  # config.yaml loss_criterion(L1이 기본, L2는 공식 선택지)
    torch.manual_seed(seed)
    saes = {n: TopKSAE(input_shape=X[n].shape[1], n_components=n_concepts, top_k=topk, encoder_module=ENCODER,
                       dictionary_normalization=DICT_NORM, device="cpu") for n in names}
    if variant == "untrained":
        return saes
    w = weights_of(names)
    current = {"m": None}
    for n, sae in saes.items():  # 지금 복원하는 모델 이름을 기록하는 wrapper(공식 함수는 decode 바로 뒤에 손실을 부른다)
        orig = sae.decode
        def dec(z, _o=orig, _n=n):
            current["m"] = _n
            return _o(z)
        sae.decode = dec

    def criterion(x, x_hat, pre_codes, codes, dictionary):
        return w[current["m"]] * crit(x, x_hat, pre_codes, codes, dictionary)
    criterion.__name__ = crit.__name__
    ds = Acts(X, names, tr, scene_rows)
    g = torch.Generator().manual_seed(seed)
    loader = torch.utils.data.DataLoader(ds, batch_size=BATCH, shuffle=True, generator=g, num_workers=0)
    total, warm = int(len(ds) / BATCH * EPOCHS), int(len(ds) / BATCH * WARMUP_EPOCHS)
    opts = {n: torch.optim.AdamW(saes[n].parameters(), lr=LR, weight_decay=WEIGHT_DECAY) for n in names}
    scheds = {n: CosineScheduler(opts[n], LR, FINAL_LR, total_iters=total, warmup_iters=warm, start_warmup_value=1e-6) for n in names}
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    here = os.getcwd()
    os.chdir(workdir)  # 공식 함수가 ./weights/에 체크포인트를 쓴다
    try:
        UT.train_cross_prediction_saes(saes, loader, criterion, opts, scheds, model_zoo={n: {} for n in names}, nb_epochs=EPOCHS, clip_grad=CLIP,
                                       monitoring=0, device="cpu", seeded=True, model_name=f"{variant}_seed{seed}", divide_norm=divide_norm)
    finally:
        os.chdir(here)
        shutil.rmtree(workdir, ignore_errors=True)
    for n, sae in saes.items():
        del sae.decode  # wrapper를 떼고 원래 method로
    return saes


def codes_and_dicts(saes, X, names):
    """평가 모드의 개념 활성 Z(모델, 행, 개념)와 사전 D(모델, 개념, 차원)."""
    import torch
    Z, D = [], []
    with torch.no_grad():
        for n in names:
            saes[n].eval()
            Z.append(saes[n].encode(X[n])[1].numpy())
            D.append(saes[n].get_dictionary().numpy())
    return np.stack(Z).astype(np.float32), np.stack(D).astype(np.float32)


def offdiag_r2(Z, D, Xn, rows):
    """encoder i → decoder j 복원 R²(rows)의 대각 밖 평균(공식 _avg_non_diagonal과 같은 값)과 7 × 7 표."""
    M = len(Xn)
    R = np.array([[A.r2_weighted(Xn[j][rows], Z[i][rows] @ D[j]) for j in range(M)] for i in range(M)])
    return float(R[~np.eye(M, dtype=bool)].mean()), R


def common_videos(out):
    """5명이 모두 가진 영상(뇌 PCA 파일 기준)."""
    sets = [set(np.load(Path(out) / "brain_pca" / f"sub-{q}.npz")["video_id"].tolist()) for q in A.PARTICIPANTS]
    return np.array(sorted(set.intersection(*sets)), np.int64)


def fold_inputs(out, k, split):
    vid = common_videos(out)
    fold = split.set_index("video_id").fold.loc[vid].to_numpy(np.int64)
    X, nets = [], []
    for q in A.PARTICIPANTS:
        v, f, x, net, net_names = A.load_brain_pca(out, q, k)
        where = {x_: i for i, x_ in enumerate(v.tolist())}
        X.append(x[[where[x_] for x_ in vid.tolist()]])
        nets.append(net)
    sc, info = A.scene_inputs(vid, fold, k, split)
    X += [sc["vision"], sc["caption"]]
    return vid, fold, X, np.stack(nets), net_names, info


def select(a):
    """추천안: 검증 fold의 교차 복원 R²(대각 밖 평균)로 K, k를 고른다(seed 0, trained). <out>/usae/select/fold{k}.json"""
    import torch
    c.guard(a.design_freeze)
    torch.set_num_threads(a.threads)
    split = c.load_split()
    k = int(a.fold)
    vid, fold, Xn, _, _, _ = fold_inputs(a.out, k, split)
    names = models_of()
    X = {n: torch.as_tensor(x, dtype=torch.float32) for n, x in zip(names, Xn)}
    r = c.roles(k)
    tr, va = np.flatnonzero(np.isin(fold, r["train"])), np.flatnonzero(fold == r["val"])
    o = Path(a.out) / "usae" / "select"
    o.mkdir(parents=True, exist_ok=True)
    rows = []
    for K, kk in SELECT_GRID:
        saes = train_official(X, names, tr, np.arange(len(vid)), K, kk, 0, o / f"tmp_fold{k}_{K}_{kk}", "trained")
        Z, D = codes_and_dicts(saes, X, names)
        score, R = offdiag_r2(Z, D, Xn, va)
        rows.append(dict(k_concepts=K, topk=kk, val_offdiag_r2=score, val_brain_to_scene_r2=float(R[:5, 5:].mean()), dead_on_val=int(((Z[:, va] > 0).sum((0, 1)) == 0).sum())))
        print(json.dumps(rows[-1]), flush=True)
    best = max(rows, key=lambda x: x["val_offdiag_r2"])
    (o / f"fold{k}.json").write_text(json.dumps(dict(fold=k, grid=rows, chosen=best, criterion="공식 train.py _avg_non_diagonal(검증 fold)", code_commit=c.START_HEAD), indent=1))


def fit(a):
    import torch
    c.guard(a.design_freeze)
    torch.set_num_threads(a.threads)
    split = c.load_split()
    k = int(a.fold)
    if a.from_select:
        ch = json.loads((Path(a.out) / "usae" / "select" / f"fold{k}.json").read_text())["chosen"]
        K, kk = int(ch["k_concepts"]), int(ch["topk"])
    else:
        if not (a.k_concepts and a.topk):
            raise SystemExit("--k-concepts와 --topk를 주거나 --from-select를 쓴다(01 6-4i, 석진 님 결정)")
        K, kk = int(a.k_concepts), int(a.topk)
    o = Path(a.out) / "usae" / "fit"
    o.mkdir(parents=True, exist_ok=True)
    started = time.time()
    vid, fold, Xn, nets, net_names, info = fold_inputs(a.out, k, split)
    names = models_of()
    X = {n: torch.as_tensor(x, dtype=torch.float32) for n, x in zip(names, Xn)}
    r = c.roles(k)
    tr, va = np.flatnonzero(np.isin(fold, r["train"])), np.flatnonzero(fold == r["val"])
    zones = A.zone_of(vid)
    log = dict(fold=k, k_concepts=K, topk=kk, from_select=bool(a.from_select), n_videos=int(len(vid)), n_train=int(len(tr)), scene=info, runs={},
               official_commit=OFFICIAL_COMMIT, design_freeze=a.design_freeze, code_commit=c.START_HEAD, code_dirty=c.START_DIRTY)
    for seed in SEEDS:
        for variant in VARIANTS:
            rows = np.arange(len(vid))
            if variant == "shuffled":
                rng = np.random.default_rng(BOOT_SEED + 1000 * k + seed)
                rows[tr] = A.zone_shuffle(tr, zones, rng)
                rows[va] = A.zone_shuffle(va, zones, rng)
            saes = train_official(X, names, tr, rows, K, kk, seed, o / f"tmp_fold{k}_{variant}_seed{seed}", variant)
            Z, D = codes_and_dicts(saes, X, names)
            vr, _ = offdiag_r2(Z, D, Xn, va)
            np.savez(o / f"fold{k}_{variant}_seed{seed}.npz", video_id=vid, fold=fold, Z=Z, D=D, models=np.array(names))
            log["runs"][f"{variant}_seed{seed}"] = dict(val_offdiag_r2=vr, dead_on_val=int(((Z[:, va] > 0).sum((0, 1)) == 0).sum()))
            print(json.dumps(dict(fold=k, variant=variant, seed=seed, **log["runs"][f"{variant}_seed{seed}"], seconds=round(time.time() - started, 1))), flush=True)
    np.savez(o / f"fold{k}_networks.npz", nets=nets, names=np.array(net_names))
    log["seconds"] = round(time.time() - started, 1)
    (o / f"run_info_fold{k}.json").write_text(json.dumps(log, indent=1, default=float))
    readout(a.out, k, split)


def readout(out, k, split):
    """fold k의 시험 행 읽기. <out>/usae/readout/fold{k}.npz"""
    o = Path(out) / "usae"
    vid, fold, Xn, nets, net_names, _ = fold_inputs(out, k, split)
    names = models_of()
    nb = len(A.PARTICIPANTS)
    r = c.roles(k)
    tr, va, te = (np.flatnonzero(np.isin(fold, r["train"])), np.flatnonzero(fold == r["val"]), np.flatnonzero(fold == r["test"]))
    y, _, _ = A.ratings(split, vid)
    g = split.set_index("video_id").canonical_id.loc[vid[va]].to_numpy()
    scene_pca = A.zfit(np.c_[Xn[-2], Xn[-1]], tr)
    order = [A.zfit(A.order_inputs(q, vid, k, split), tr) for q in A.PARTICIPANTS]
    rng = np.random.default_rng(BOOT_SEED + k)
    perms = np.stack([rng.permutation(len(te)) for _ in range(N_NULL)])
    res = dict(video_id=vid[te], y=y[te], models=np.array(names),
               sst_scene=sum(((Xn[j][te] - Xn[j][te].mean(0)) ** 2).sum(1) for j in (len(names) - 2, len(names) - 1)))
    for variant in VARIANTS:
        for seed in SEEDS:
            f = np.load(o / "fit" / f"fold{k}_{variant}_seed{seed}.npz")
            if not np.array_equal(f["video_id"], vid):
                raise ValueError("영상 순서가 다르다")
            Z, D = f["Z"].astype(np.float64), f["D"].astype(np.float64)
            n_con = Z.shape[2]
            tag = f"{variant}_seed{seed}"
            R2 = np.array([[A.r2_weighted(Xn[j][te], Z[i][te] @ D[j]) for j in range(len(names))] for i in range(len(names))])
            res[f"r2_{tag}"] = R2
            res[f"sse_b2s_{tag}"] = np.stack([sum(((Xn[j][te] - (Z[qi][te] @ D[j])) ** 2).sum(1) for j in (len(names) - 2, len(names) - 1)) for qi in range(nb)])
            res[f"Z_{tag}"] = Z[:, te].astype(np.float32)
            res[f"D_{tag}"] = D.astype(np.float32)
            if variant == "untrained":
                continue
            # ③ 옮기기
            scene_code = (Z[-2] + Z[-1]) / 2
            sc = A.zfit(scene_code, tr)
            pt, pd_, pf = [], [], []
            for qi in range(nb):
                bz = A.zfit(Z[qi], tr)
                pca = A.zfit(Xn[qi], tr)
                t_hat = A.ridge_val(pca, scene_code, tr, va, pca[te])
                fl = (t_hat - scene_code[tr].mean(0)) / np.where(scene_code[tr].std(0) > 0, scene_code[tr].std(0), 1.0)
                a1, a2 = A.ridge_cv(sc[va], y[va], g, [bz[te], fl])
                pt.append(a1)
                pf.append(a2)
                pd_.append(A.ridge_cv(bz[va], y[va], g, [bz[te]])[0])
            res[f"pred_transfer_{tag}"], res[f"pred_direct_{tag}"], res[f"pred_floor_{tag}"] = np.stack(pt), np.stack(pd_), np.stack(pf)
            res[f"pred_scene_own_{tag}"] = A.ridge_cv(sc[va], y[va], g, [sc[te]])[0]
            # 뇌 전용 후보 점검(개념마다)
            brain_avg = Z[:nb].mean(0)
            live = brain_avg[te].std(0) > 0
            sp = np.full(n_con, np.nan)
            sp_null = np.full(n_con, np.nan)
            if live.any():
                pr = A.ridge_cv(scene_pca[va], brain_avg[va][:, live], g, [scene_pca[te]])[0]
                yt = brain_avg[te][:, live]
                sp[live] = A.col_r(yt, pr)
                sp_null[live] = np.nanpercentile(np.stack([A.col_r(yt[pp], pr) for pp in perms]), 95, axis=0)
            op = np.full((nb, n_con), np.nan)
            op_null = np.full((nb, n_con), np.nan)
            for qi in range(nb):
                lv = Z[qi][te].std(0) > 0
                if lv.any():
                    pr = A.ridge_cv(order[qi][va], Z[qi][va][:, lv], g, [order[qi][te]])[0]
                    yt = Z[qi][te][:, lv]
                    op[qi, lv] = A.col_r(yt, pr)
                    op_null[qi, lv] = np.nanpercentile(np.stack([A.col_r(yt[pp], pr) for pp in perms]), 95, axis=0)
            res[f"scene_pred_r_{tag}"], res[f"scene_pred_null95_{tag}"] = sp, sp_null
            res[f"order_r_{tag}"], res[f"order_null95_{tag}"] = op, op_null
    res["nets"], res["net_names"] = nets, np.array(net_names)
    (o / "readout").mkdir(parents=True, exist_ok=True)
    np.savez(o / "readout" / f"fold{k}.npz", **res)
    print(f"fold{k} readout 저장", flush=True)


# ---------- 요약 ----------

def hungarian_r(a, b):
    """a, b: (행, 개념) 활성. 개념 짝(Hungarian, 1 − r)과 짝마다 r. 활성이 상수인 개념의 r은 0으로 둔다."""
    from scipy.optimize import linear_sum_assignment
    za = (a - a.mean(0)) / np.where(a.std(0) > 0, a.std(0), np.inf)
    zb = (b - b.mean(0)) / np.where(b.std(0) > 0, b.std(0), np.inf)
    C = za.T @ zb / len(a)
    ri, ci = linear_sum_assignment(-C)
    out = np.zeros(a.shape[1])
    out[ri] = C[ri, ci]
    return out


def summarize(a):
    import s10_stats as st
    split = c.load_split()
    o = Path(a.out) / "usae"
    names = models_of()
    nb = len(A.PARTICIPANTS)
    _, emo_names, keep27 = A.ratings(split, split.video_id.to_numpy()[:1])
    F = {k: dict(np.load(o / "readout" / f"fold{k}.npz")) for k in range(1, c.N_FOLDS + 1)}
    # 7 × 7 R²(시험, 6 fold, seed 평균)
    r2_rows = []
    for v in VARIANTS:
        M = np.mean([[F[k][f"r2_{v}_seed{s}"] for s in SEEDS] for k in F], (0, 1))
        for i in range(len(names)):
            r2_rows += [dict(variant=v, encoder=names[i], decoder=names[j], r2=float(M[i, j])) for j in range(len(names))]
    R2 = pd.DataFrame(r2_rows)
    # 정렬 판정: 뇌 encoder → 장면 decoder R²(뇌 다섯 × 장면 둘 평균), trained − shuffled, 내용 묶음 bootstrap
    vid_all = np.concatenate([F[k]["video_id"] for k in F])
    codes, n_units = st.unit_codes(split.set_index("video_id").loc[vid_all].canonical_id.to_numpy())
    W = st.bootstrap_counts(n_units, a.n_boot, np.random.default_rng(BOOT_SEED)).astype(np.float64)
    Wv = W[:, codes]

    sst = np.concatenate([F[k]["sst_scene"] for k in F])
    per, db = [], []
    for qi in range(nb):
        vals, bs = {}, {}
        for v in ("trained", "shuffled"):
            e = np.concatenate([np.mean([F[k][f"sse_b2s_{v}_seed{s}"][qi] for s in SEEDS], 0) for k in F])
            vals[v] = 1 - e.sum() / sst.sum()
            bs[v] = 1 - (Wv @ e) / (Wv @ sst)
        per.append(vals["trained"] - vals["shuffled"])
        db.append(bs["trained"] - bs["shuffled"])
    dd, dbm = float(np.mean(per)), np.mean(db, 0)
    lo, hi = st.basic_ci(np.array([dd]), dbm[:, None])
    align = pd.DataFrame([dict(comparison="② 뇌 encoder → 장면 decoder R²: trained − shuffled", diff=dd, ci_low=float(lo[0]), ci_high=float(hi[0]),
                               p=float(st.centered_p(np.array([dd]), dbm[:, None])[0]), n_positive=int(sum(x > 0 for x in per)), n_negative=int(sum(x < 0 for x in per)))])
    # ③ 옮기기(참가자마다 6 fold 시험 예측 모아 r), bootstrap
    yall = np.concatenate([F[k]["y"] for k in F])
    preds = {}
    for name in ("transfer", "direct", "floor"):
        for v in ("trained", "shuffled"):
            for qi in range(nb):
                preds[(name, v, qi)] = np.concatenate([np.mean([F[k][f"pred_{name}_{v}_seed{s}"][qi] for s in SEEDS], 0) for k in F])
    scene_own = np.concatenate([np.mean([F[k][f"pred_scene_own_trained_seed{s}"] for s in SEEDS], 0) for k in F])
    point, boot = {}, {}
    for qi in range(nb):
        pp = {f"{n}|{v}": preds[(n, v, qi)] for n in ("transfer", "direct", "floor") for v in ("trained", "shuffled")}
        pp["scene_own"] = scene_own
        point[qi] = {m: st.pearson_columns(yall, p) for m, p in pp.items()}
        boot[qi] = st.boot_r(W[:, codes], yall, pp)
    sets = {"34": np.ones(len(emo_names), bool), "27": keep27}
    rows, diffs = [], []
    for m in point[0]:
        for sn, msk in sets.items():
            pr = [float(np.nanmean(point[qi][m][msk])) for qi in range(nb)]
            rows += [dict(read=m, participant=names[qi], set=sn, r=pr[qi]) for qi in range(nb)] + [dict(read=m, participant="mean5", set=sn, r=float(np.mean(pr)))]
    for ma, mb, label in (("transfer|trained", "floor|trained", "③ 옮긴 r − 선형 2단계 바닥"), ("transfer|trained", "transfer|shuffled", "③ 옮긴 r: trained − shuffled"),
                          ("transfer|trained", "direct|trained", "③ 옮긴 r − 뇌 쪽 직접")):
        for sn, msk in sets.items():
            pr = [float(np.nanmean(point[qi][ma][msk]) - np.nanmean(point[qi][mb][msk])) for qi in range(nb)]
            dd = float(np.mean(pr))
            dbb = np.mean([np.nanmean(boot[qi][ma][:, msk], 1) - np.nanmean(boot[qi][mb][:, msk], 1) for qi in range(nb)], 0)
            lo, hi = st.basic_ci(np.array([dd]), dbb[:, None])
            diffs.append(dict(comparison=label, set=sn, diff=dd, ci_low=float(lo[0]), ci_high=float(hi[0]), p=float(st.centered_p(np.array([dd]), dbb[:, None])[0]),
                              n_positive=int(sum(x > 0 for x in pr)), n_negative=int(sum(x < 0 for x in pr))))
    te_ = np.mean([point[qi]["transfer|trained"] for qi in range(nb)], 0)
    di_ = np.mean([point[qi]["direct|trained"] for qi in range(nb)], 0)
    so_ = np.mean([point[qi]["scene_own"] for qi in range(nb)], 0)
    tb = np.mean([boot[qi]["transfer|trained"] for qi in range(nb)], 0)
    dbb = np.mean([boot[qi]["direct|trained"] for qi in range(nb)], 0)
    sbb = np.mean([boot[qi]["scene_own"] for qi in range(nb)], 0)
    pc = A.partial_pearson(te_, di_, so_)
    pcb = np.array([A.partial_pearson(tb[i], dbb[i], sbb[i]) if np.isfinite(tb[i]).all() and np.isfinite(dbb[i]).all() and np.isfinite(sbb[i]).all() else np.nan for i in range(len(tb))])
    lo, hi = st.basic_ci(np.array([pc]), pcb[:, None])
    shape = pd.DataFrame([dict(read="③ 옮긴 r ~ 뇌 쪽 직접 r | 장면 쪽 r (34개 정서, 5명 평균)", partial_r=pc, ci_low=float(lo[0]), ci_high=float(hi[0]), plain_r=float(np.corrcoef(te_, di_)[0, 1]))])
    # 개념(fold마다, seed 0 기준): 켜지는 비율, 장면과의 일치, 참가자 사이 상관, 후보 점검, seed 재현
    concept_rows, card_rows = [], []
    for k in F:
        f0 = F[k]
        Zs = {s: f0[f"Z_trained_seed{s}"].astype(np.float64) for s in SEEDS}
        Zu = [f0[f"Z_untrained_seed{s}"].astype(np.float64) for s in SEEDS]
        ref = Zs[0][:nb].mean(0)
        null = np.concatenate([hungarian_r(ref, u[:nb].mean(0)) for u in Zu])
        thr = float(np.percentile(null, 95))
        reap = np.stack([hungarian_r(ref, Zs[s][:nb].mean(0)) > thr for s in SEEDS[1:]]).sum(0) + 1
        Z = Zs[0]
        te_vid = f0["video_id"]
        y = f0["y"]
        cw, vocab = None, None
        try:
            import s10_content as CT
            cw, vocab, _ = CT.caption_words(te_vid)
        except Exception as ex:  # 캡션 단어는 카드 설명용이다. 실패하면 이유를 남기고 빈칸으로 둔다
            print("캡션 단어를 읽지 못했다:", ex, flush=True)
        cap = pd.read_csv(__import__("s3_common").CAPTIONS, encoding="utf-8-sig").groupby("video_id").description.first()
        Dmean = np.mean([f0["D_trained_seed0"][qi] @ f0["nets"][qi] for qi in range(nb)], 0)  # (개념, 네트워크)
        for ci in range(Z.shape[2]):
            b5 = Z[:nb, :, ci]
            ba = b5.mean(0)
            fire = (Z[:, :, ci] > 0).mean(1)
            cross = [np.corrcoef(b5[i], b5[j])[0, 1] for i in range(nb) for j in range(i + 1, nb) if b5[i].std() > 0 and b5[j].std() > 0]
            def rr(u, v):
                return float(np.corrcoef(u, v)[0, 1]) if u.std() > 0 and v.std() > 0 else np.nan
            row = dict(fold=k, concept=ci, **{f"fire_{names[m]}": float(fire[m]) for m in range(len(names))},
                       fire_brain_mean=float(fire[:nb].mean()), mean_act_brain=float(Z[:nb, :, ci].mean()), mean_act_vision=float(Z[-2, :, ci].mean()), mean_act_caption=float(Z[-1, :, ci].mean()),
                       r_brainavg_vision=rr(ba, Z[-2, :, ci]), r_brainavg_caption=rr(ba, Z[-1, :, ci]), cross_subject_r=float(np.mean(cross)) if cross else np.nan,
                       scene_pred_r=float(f0["scene_pred_r_trained_seed0"][ci]), scene_pred_null95=float(f0["scene_pred_null95_trained_seed0"][ci]),
                       order_r_mean5=float(np.nanmean(f0["order_r_trained_seed0"][:, ci])), order_null95_mean5=float(np.nanmean(f0["order_null95_trained_seed0"][:, ci])),
                       seeds_reappear=int(reap[ci]), seed_null95=thr)
            # 참가자 사이 상관의 bootstrap 하한(시험 영상, 내용 묶음)
            if cross:
                cc, nu = st.unit_codes(split.set_index("video_id").loc[te_vid].canonical_id.to_numpy())
                Wb = st.bootstrap_counts(nu, 2000, np.random.default_rng(BOOT_SEED + ci))[:, cc]
                pairs = [(i, j) for i in range(nb) for j in range(i + 1, nb) if b5[i].std() > 0 and b5[j].std() > 0]
                bmat = np.mean([st.boot_r(Wb, b5[i][:, None], {"x": b5[j][:, None]})["x"][:, 0] for i, j in pairs], 0)
                lo, hi = st.basic_ci(np.array([row["cross_subject_r"]]), bmat[:, None])
                row["cross_subject_ci_low"] = float(lo[0])
            else:
                row["cross_subject_ci_low"] = np.nan
            row["brain_common_unpredicted"] = bool(row["cross_subject_ci_low"] > 0 and not (row["scene_pred_r"] > row["scene_pred_null95"])
                                                   and not (row["order_r_mean5"] > row["order_null95_mean5"]) and row["seeds_reappear"] >= 4)
            er = np.array([rr(ba, y[:, e]) for e in range(len(emo_names))])
            top = np.argsort(-np.nan_to_num(er, nan=-9))[:3]
            vids = te_vid[np.argsort(-Z[:, :, ci].mean(0))[:6]]
            words = ""
            if cw is not None and ba.std() > 0:
                wr = A.col_r(cw, np.repeat(ba[:, None], cw.shape[1], 1))
                words = ", ".join(vocab[i] for i in np.argsort(-np.nan_to_num(wr, nan=-9))[:8])
            nets = f0["net_names"].tolist()
            nt = np.argsort(-np.abs(Dmean[ci]))[:3]
            card_rows.append(dict(fold=k, concept=ci, top_emotions="; ".join(f"{emo_names[e]} {er[e]:.2f}" for e in top), caption_words=words,
                                  top_networks="; ".join(f"{nets[n]} {Dmean[ci, n]:+.2f}" for n in nt),
                                  top_videos=" | ".join(f"{v}: {cap.get(v, '')}" for v in vids)))
            concept_rows.append(row)
    C = pd.DataFrame(concept_rows)
    o2 = o / "summary"
    o2.mkdir(parents=True, exist_ok=True)
    R2.to_csv(o2 / "r2_matrix.tsv", sep="\t", index=False)
    align.to_csv(o2 / "alignment.tsv", sep="\t", index=False)
    pd.DataFrame(rows).to_csv(o2 / "transfer_scores.tsv", sep="\t", index=False)
    pd.DataFrame(diffs).to_csv(o2 / "transfer_differences.tsv", sep="\t", index=False)
    shape.to_csv(o2 / "transfer_shape.tsv", sep="\t", index=False)
    C.to_csv(o2 / "concepts.tsv", sep="\t", index=False)
    pd.DataFrame(card_rows).to_csv(o2 / "concept_cards.tsv", sep="\t", index=False)
    (o2 / "run_info.json").write_text(json.dumps(dict(models=names, official_commit=OFFICIAL_COMMIT, epochs=EPOCHS, batch=BATCH, lr=LR, seeds=SEEDS, n_boot=a.n_boot, n_null=N_NULL,
                                                    code_commit=c.START_HEAD, code_dirty=c.START_DIRTY), indent=1, ensure_ascii=False))
    print(R2[R2.variant == "trained"].pivot(index="encoder", columns="decoder", values="r2").round(3).to_string())
    print(align.round(4).to_string(index=False))
    print(pd.DataFrame(diffs).round(3).to_string(index=False))
    print(shape.round(3).to_string(index=False))
    print("뇌 공통이면서 두 feature로 예측되지 않는 개념:", int(C.brain_common_unpredicted.sum()), "/", len(C), flush=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 6-4i ② Universal SAE(공식 코드)와 ③")
    ap.add_argument("step", choices=("select", "fit", "readout", "summarize"))
    ap.add_argument("--fold", type=int)
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", default="")
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--k-concepts", type=int)
    ap.add_argument("--topk", type=int)
    ap.add_argument("--from-select", action="store_true")
    ap.add_argument("--n-boot", type=int, default=10_000)
    a = ap.parse_args(argv)
    if a.step in ("select", "fit", "readout") and not a.fold:
        raise SystemExit(f"{a.step}에는 --fold가 필요하다")
    if a.step == "select":
        select(a)
    elif a.step == "fit":
        fit(a)
    elif a.step == "readout":
        c.guard(a.design_freeze)
        readout(a.out, int(a.fold), c.load_split())
    else:
        summarize(a)


if __name__ == "__main__":
    main()
