#!/usr/bin/env python3
"""KHBM 초록용 빠른 예비 분석 (2026-11-03). 본 실험(docs/final)이 아니라 사전 분석이다. 결과는 논문 결과로 쓰지 않는다(M6).

자료: Horikawa 5명, 분할 horikawa_rungroup6_v1. MC 최종 시험 72개와 같은 내용의 영상을 모두 빼고, 1363도 뺀다
      (1349와 같은 내용인데 지금 분할에서 다른 fold에 있다. 새 분할은 S2에서 만든다). 입력은 469개 지도의 5명 공통 영역 평균(466개).
      정답은 규범 평정 34개, 특징은 10월 캐시(V-JEPA 2 마지막 block, 사람 캡션 MPNet). 본 실험의 voxel 입력, 네 지점 특징과 다르다.
단계
  linear : 참가자별 soft BCE 선형(뇌만), 자극 수준 soft BCE 선형(캡션 특징, 시각 특징), 참가자별 ridge feature decoding과 영상 식별(O19).
  mlp    : 5명 공유 MLP(참가자별 입력층 466 → d, 공유 층 하나). 조건은 직접 학습, 특징 맞히기 연습, 짝 섞은 특징 맞히기 연습,
           주 조건(상호작용 head, 더하기 head), 출력 distillation, label smoothing.
           z = g(H) + a(v̂) + b(ĉ) + U[(Av̂) ⊙ (Bĉ)], 정서 손실은 v̂, ĉ로 흐르지 않는다(G8). 후보와 선택은 G9, H2, L9, O6을 따른다
           (바깥 fold k의 검증은 다음 fold, 선택은 검증 정서별 r 평균, 조기 종료는 검증 soft BCE, patience 30, 최대 300 epoch).
           AdamW lr 1e-3, weight decay 0.01, batch 64(G13). d = 128, dropout 0.3은 10월 MLP에서 가져온 값이다.
           teacher는 V-JEPA 2와 캡션을 이어 붙인 ridge의 nested OOF 출력(H2 학습 fold 4개 안의 안쪽 4겹, E4)이다.
  swap   : 주 조건 시험 영상에서 바꿔 끼우기(4-2, O2, O3). 짝은 같은 시험 fold의 이름표 73개 최근접 영상. 시각만, 캡션만, 둘 다.
           대응 = 쌍에 걸친 r(Δp, Δy), 효과 = 실제 대응 − 같은 길이 무작위 방향 대조의 평균(100회).
  hierarchy: 평정을 시각에만, 캡션에만, 둘 다, 나머지로 나눠(hierarchy_components.py의 중첩 구조) 영역 묶음마다 ridge로 decoding. V = V-JEPA 2, S = 사람 캡션(MPNet).
  summary: 표를 만든다. 순열 null(같은 run 안에서 예측을 섞음, 1,000회)과 영상 bootstrap(1,000회)을 함께 낸다.
출력: project/output/prelim_2026-10/17_khbm_pilot/
사용: python khbm_pilot.py --stage linear | hierarchy | mlp --fold 0 | swap | summary
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.linear_model import RidgeCV
from torch import nn

sys.path.insert(0, str(Path(__file__).parent))
import run_stage1 as rs  # noqa: E402

cl, bb = rs.cl, rs.bb
OD = rs.OUT / "17_khbm_pilot"
MAN = rs.REPO / "project/analysis/final_2026-11/manifests"
CROSSWALK = rs.REPO / "prereg_v2/manifests/stimulus_crosswalk.tsv"
SUBS = ["01", "02", "03", "04", "05"]
D, DROP, LR, WD, BATCH, MAX_EP, PATIENCE = 128, 0.3, 1e-3, 0.01, 64, 300, 30
LAMS, ALPHAS, RANKS = [0.1, 1.0], [0.25, 0.5], [1, 2, 4, 8]
SEEDS = [0, 1, 2]
RIDGE = np.logspace(0, 6, 13)
torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "6")))


def dev_filter(vid):
    cw = pd.read_csv(CROSSWALK, sep="\t", comment="#")
    mc = set(pd.read_csv(MAN / "mc_test72.tsv", sep="\t").canonical_stimulus_id)
    drop = set(cw.video_number[cw.canonical_stimulus_id.isin(mc)]) | {1363}
    return ~np.isin(vid, list(drop))


def common_cols():
    valid = {}
    for s in SUBS:
        rows = pd.read_csv(rs.OUT / f"roi_blocks/Horikawa_sub-{s}_roi469_rows.tsv", sep="\t")
        R = np.load(rs.OUT / f"roi_blocks/Horikawa_sub-{s}_roi469_runz.npy")
        info = pd.read_csv(rs.OUT / f"roi_blocks/Horikawa_sub-{s}_roi469_info.tsv", sep="\t")
        valid[s] = info.roi_valid.values & np.isfinite(R[~rows.exclude_duplicate.astype(bool).values]).all(0)
    common = np.logical_and.reduce(list(valid.values()))
    return {s: np.flatnonzero(common[valid[s]]) for s in SUBS}, int(common.sum())


def load_all():
    """참가자별 행(개발 영상), 공통 영역 반응. 정답과 특징은 영상 표로."""
    F = rs.load_features(); cols, n_roi = common_cols(); P = {}
    for s in SUBS:
        rows, fold, FB, *_ = rs.load_subject(s)
        keep = dev_filter(rows.video_id.values)
        P[s] = dict(vid=rows.video_id.values[keep], fold=fold[keep], run=rows.run_index.values[keep], B=FB["brain_roi469"][keep][:, cols[s]])
    vids = np.unique(np.concatenate([P[s]["vid"] for s in SUBS]))
    names, Y, _ = cl.labels_for(vids); assert np.isfinite(Y).all()
    V = F["vjepa2_vitg_final"].loc[vids].values.astype(np.float64)
    C = F["caption_human_mpnet"].loc[vids].values.astype(np.float64)
    L = F["hk_semantic73"].loc[vids].values.astype(np.float64)
    fv = {}
    for s in SUBS:
        fv.update(dict(zip(P[s]["vid"], P[s]["fold"])))
    vf = np.array([fv[v] for v in vids])
    return dict(P=P, vids=vids, names=names, Y=Y, V=V, C=C, L=L, vf=vf, n_roi=n_roi)


def corr_cols(a, b):
    a = a - a.mean(0); b = b - b.mean(0); den = np.sqrt((a ** 2).sum(0) * (b ** 2).sum(0))
    with np.errstate(invalid="ignore", divide="ignore"):
        return (a * b).sum(0) / den


# ---------- linear ----------
def identification(pred, true):
    """같은 fold 안 영상 식별(O19): 영상 A의 decoded와 A 실제의 r이 decoded와 다른 영상 B 실제의 r보다 크면 1."""
    p = (pred - pred.mean(1, keepdims=True)); t = (true - true.mean(1, keepdims=True))
    p /= np.linalg.norm(p, axis=1, keepdims=True); t /= np.linalg.norm(t, axis=1, keepdims=True)
    R = p @ t.T; d = np.diag(R)[:, None]; n = len(R)
    return ((d > R).sum(1)) / (n - 1)


def stage_linear(A, only_sub=None):
    OD.mkdir(parents=True, exist_ok=True); rowsB, rowsS, rowsF = [], [], []
    vids, vf, Y, names = A["vids"], A["vf"], A["Y"], A["names"]; pos = {v: i for i, v in enumerate(vids)}
    stim_done = (OD / "linear_stimulus.tsv").exists()
    for name, X in ([] if stim_done else [("캡션 특징", A["C"]), ("시각 특징", A["V"]), ("캡션 + 시각", np.hstack([A["C"], A["V"]]))]):
        P = np.zeros_like(Y)
        for f in np.unique(vf):
            tr, te = vf != f, vf == f
            Xtr, Xte = cl.std_fit(X[tr], X[te]); P[te], _ = cl.emotion_fit("A34", Xtr, Y[tr], Xte, vf[tr])
        r = corr_cols(P, Y); rowsS.append(dict(input=name, mean_r=np.nanmean(r), **dict(zip(names, r)))); print(name, round(np.nanmean(r), 4), flush=True)
    if not stim_done:
        pd.DataFrame(rowsS).to_csv(OD / "linear_stimulus.tsv", sep="\t", index=False, float_format="%.4f")
    for s in ([only_sub] if only_sub else SUBS):
        p = A["P"][s]; idx = np.array([pos[v] for v in p["vid"]]); Yp = Y[idx]; fold = p["fold"]; P = np.zeros_like(Yp)
        for f in np.unique(fold):
            tr, te = fold != f, fold == f
            Xtr, Xte = cl.std_fit(p["B"][tr], p["B"][te]); P[te], _ = cl.emotion_fit("A34", Xtr, Yp[tr], Xte, fold[tr])
        r = corr_cols(P, Yp); rowsB.append(dict(participant=f"sub-{s}", n_videos=len(idx), mean_r=np.nanmean(r), **dict(zip(names, r))))
        np.savez(OD / f"linear_brain_sub-{s}.npz", vid=p["vid"], fold=fold, run=p["run"], P=P, Y=Yp)
        for tname, T in [("시각 특징", A["V"]), ("캡션 특징", A["C"])]:
            Tp = T[idx]; Phat = np.zeros_like(Tp); ids = []
            for f in np.unique(fold):
                tr, te = fold != f, fold == f
                Xtr, Xte = cl.std_fit(p["B"][tr], p["B"][te]); mu, sd = Tp[tr].mean(0), Tp[tr].std(0); sd[sd == 0] = 1
                Z = RidgeCV(alphas=RIDGE).fit(Xtr, (Tp[tr] - mu) / sd).predict(Xte)
                Phat[te] = Z * sd + mu; ids.append(identification(Z, (Tp[te] - mu) / sd))
            rowsF.append(dict(participant=f"sub-{s}", feature=tname, dim_mean_r=np.nanmean(corr_cols(Phat, Tp)), identification=np.concatenate(ids).mean()))
        print(f"sub-{s}", round(rowsB[-1]["mean_r"], 4), rowsF[-2:], flush=True)
    tag = f"_sub-{only_sub}" if only_sub else ""
    pd.DataFrame(rowsB).to_csv(OD / f"linear_brain{tag}.tsv", sep="\t", index=False, float_format="%.4f")
    pd.DataFrame(rowsF).to_csv(OD / f"feature_decoding_ridge{tag}.tsv", sep="\t", index=False, float_format="%.4f")


# ---------- mlp ----------
class Net(nn.Module):
    def __init__(self, n_roi, dv, dc, features=False, readout=False, rank=0):
        super().__init__()
        self.inp = nn.ModuleList([nn.Linear(n_roi, D) for _ in SUBS])
        self.enc = nn.Sequential(nn.GELU(), nn.Dropout(DROP), nn.Linear(D, D), nn.GELU(), nn.Dropout(DROP))
        self.g = nn.Linear(D, 34); self.features, self.readout, self.rank = features, readout, rank
        if features:
            self.fv, self.fc = nn.Linear(D, dv), nn.Linear(D, dc)
        if readout:
            self.a, self.b = nn.Linear(dv, 34), nn.Linear(dc, 34)
            if rank:
                self.A, self.B, self.U = nn.Linear(dv, rank, bias=False), nn.Linear(dc, rank, bias=False), nn.Linear(rank, 34, bias=False)

    def encode(self, x, sid):
        h = torch.zeros(len(x), D)
        for i in sid.unique():
            m = sid == i; h[m] = self.inp[int(i)](x[m])
        return self.enc(h)

    def head(self, h, v, c):
        z = self.g(h)
        if self.readout:
            z = z + self.a(v) + self.b(c)
            if self.rank:
                z = z + self.U(self.A(v) * self.B(c))
        return z

    def forward(self, x, sid):
        h = self.encode(x, sid); v, c = (self.fv(h), self.fc(h)) if self.features else (None, None)
        z = self.head(h, v.detach() if self.readout else None, c.detach() if self.readout else None)
        return z, v, c


def fold_data(A, k):
    """바깥 fold k: 시험 k, 검증 k+1, 학습 나머지 4개. 표준화는 D_k(시험 뺀 5개 fold) 통계(0-3 표)."""
    val = (k + 1) % 6; out = {}; vids = A["vids"]; pos = {v: i for i, v in enumerate(vids)}
    dk = A["vf"] != k
    mv, sv = A["V"][dk].mean(0), A["V"][dk].std(0); sv[sv == 0] = 1
    mc, sc = A["C"][dk].mean(0), A["C"][dk].std(0); sc[sc == 0] = 1
    Vz, Cz = (A["V"] - mv) / sv, (A["C"] - mc) / sc
    for split, mask_fn in [("train", lambda f: (f != k) & (f != val)), ("val", lambda f: f == val), ("test", lambda f: f == k)]:
        X, S, I = [], [], []
        for i, s in enumerate(SUBS):
            p = A["P"][s]; m0 = p["fold"] != k
            mu, sd = p["B"][m0].mean(0), p["B"][m0].std(0); sd[sd == 0] = 1
            m = mask_fn(p["fold"])
            X.append((p["B"][m] - mu) / sd); S.append(np.full(m.sum(), i)); I.append(np.array([pos[v] for v in p["vid"][m]]))
        out[split] = (torch.tensor(np.vstack(X), dtype=torch.float32), torch.tensor(np.concatenate(S)), np.concatenate(I))
    out["Vz"], out["Cz"] = torch.tensor(Vz, dtype=torch.float32), torch.tensor(Cz, dtype=torch.float32)
    out["Y"] = torch.tensor(A["Y"], dtype=torch.float32); out["norm"] = (mv, sv, mc, sc)
    return out


def teacher_scores(A, k):
    """H2 학습 fold 4개 안의 안쪽 4겹 nested OOF(E4). 바깥 시험과 검증 fold는 쓰지 않는다."""
    val = (k + 1) % 6; idx = np.flatnonzero((A["vf"] != k) & (A["vf"] != val)); X = np.hstack([A["V"], A["C"]])[idx]; Y = A["Y"][idx]; g = A["vf"][idx]
    T = np.zeros_like(Y)
    for h in np.unique(g):
        a, b = g != h, g == h
        Xa, Xb = cl.std_fit(X[a], X[b]); T[b] = np.clip(RidgeCV(alphas=RIDGE).fit(Xa, Y[a]).predict(Xb), 1e-4, 1 - 1e-4)
    full = np.full_like(A["Y"], np.nan); full[idx] = T
    return torch.tensor(full, dtype=torch.float32)


def bce(z, y):
    return nn.functional.binary_cross_entropy_with_logits(z, y)


def val_score(net, d):
    net.eval(); X, S, I = d["val"]
    with torch.no_grad():
        z, _, _ = net(X, S)
    y = d["Y"][I]
    p = torch.sigmoid(z).numpy(); yn = y.numpy(); sn = S.numpy(); rs_ = []
    for i in range(len(SUBS)):
        r = corr_cols(p[sn == i], yn[sn == i]); r[~np.isfinite(r)] = 0; rs_.append(r[yn[sn == i].std(0) > 0].mean())
    return bce(z, y).item(), float(np.mean(rs_))


def train(A, d, cond, seed, lam=0.0, alpha=0.0, rank=0, teacher=None, perm=None):
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    features = cond in ("aux", "aux_shuffled", "main_add", "main_int"); readout = cond in ("main_add", "main_int")
    net = Net(A["n_roi"], A["V"].shape[1], A["C"].shape[1], features, readout, rank)
    opt = torch.optim.AdamW(net.parameters(), lr=LR, weight_decay=WD)
    X, S, I = d["train"]; n = len(X); Y = d["Y"]; I_t = torch.as_tensor(I)
    mean_y = Y[I_t].mean(0); fi = I_t if perm is None else torch.as_tensor(perm)[I_t]
    best, best_state, wait, ep_best = np.inf, None, 0, 0
    for ep in range(1, MAX_EP + 1):
        net.train(); order = rng.permutation(n)
        for j in range(0, n, BATCH):
            b = torch.as_tensor(order[j:j + BATCH]); ib = I_t[b]; y = Y[ib]
            if cond == "distill":
                y = (1 - alpha) * y + alpha * teacher[ib]
            elif cond == "smooth":
                y = (1 - alpha) * y + alpha * mean_y
            z, v, c = net(X[b], S[b]); loss = bce(z, y)
            if features:
                fb = fi[b]; loss = loss + lam * 0.5 * (((v - d["Vz"][fb]) ** 2).mean() + ((c - d["Cz"][fb]) ** 2).mean())
            opt.zero_grad(); loss.backward(); opt.step()
        v_bce, _ = val_score(net, d)
        if v_bce < best - 1e-5:
            best, wait, ep_best = v_bce, 0, ep; best_state = {k: t.clone() for k, t in net.state_dict().items()}
        else:
            wait += 1
            if wait >= PATIENCE:
                break
    net.load_state_dict(best_state); _, v_r = val_score(net, d)
    return net, v_r, ep_best


def test_outputs(net, d, keep_features=False):
    net.eval(); X, S, I = d["test"]
    with torch.no_grad():
        z, v, c = net(X, S)
    out = dict(sid=S.numpy(), idx=I, p=torch.sigmoid(z).numpy())
    if v is not None and keep_features:
        mv, sv, mc, sc = d["norm"]
        out["v"] = (v.numpy() * sv + mv).astype(np.float32); out["c"] = (c.numpy() * sc + mc).astype(np.float32)
    return out


def decoded_id(net, d):
    """참가자별 같은 fold 안 영상 식별(O19). D9 좌표."""
    net.eval(); X, S, I = d["test"]; rows = {}
    with torch.no_grad():
        _, v, c = net(X, S)
    for i in range(len(SUBS)):
        m = (S == i).numpy()
        rows[i] = (identification(v[m].numpy().astype(np.float64), d["Vz"][I[m]].numpy().astype(np.float64)).tolist(),
                   identification(c[m].numpy().astype(np.float64), d["Cz"][I[m]].numpy().astype(np.float64)).tolist())
    return rows


def stage_mlp(A, k):
    t0 = time.time(); (OD / "mlp").mkdir(parents=True, exist_ok=True); d = fold_data(A, k); T = teacher_scores(A, k)
    n_vid = len(A["vids"]); perm_rng = np.random.default_rng(1000 + k)
    tr_v = np.unique(d["train"][2]); perm = np.arange(n_vid)
    while True:
        p_ = perm_rng.permutation(tr_v)
        if (p_ != tr_v).all():
            break
    perm[tr_v] = p_
    grids = {"direct": [dict()], "aux": [dict(lam=l) for l in LAMS], "aux_shuffled": [dict(lam=l, perm=perm) for l in LAMS],
             "main_add": [dict(lam=l) for l in LAMS], "main_int": [dict(lam=l, rank=r) for l in LAMS for r in RANKS],
             "distill": [dict(alpha=a, teacher=T) for a in ALPHAS], "smooth": [dict(alpha=a) for a in ALPHAS]}
    sel = []; direct_vr, direct_outs = None, {}
    def show(g):
        return {x: g[x] for x in g if x in ("lam", "alpha", "rank")}
    for cond, grid in grids.items():
        trials = [(lambda t: (t[1], t[2], g, t[0]))(train(A, d, cond, 0, **g)) for g in grid]
        vr, ep, g, net = max(trials, key=lambda x: x[0])
        zero = cond in ("aux", "distill") and direct_vr > vr  # G9, G10: 0 후보는 직접 학습과 같으므로 다시 학습하지 않는다
        if zero:
            for sd_, o in direct_outs.items():
                np.savez_compressed(OD / "mlp" / f"test_fold{k}_{cond}_seed{sd_}.npz", **o)
            sel.append(dict(fold=k, cond=cond, val_r=direct_vr, zero_selected=True))
            print(f"fold {k} {cond}: 0 후보(직접 학습)가 뽑힘 val r {direct_vr:.4f} ({time.time() - t0:.0f}초)", flush=True)
            continue
        if cond == "direct":
            direct_vr = vr
        sel.append(dict(fold=k, cond=cond, val_r=vr, epochs=ep, zero_selected=False, **show(g)))
        nets = {0: net}
        for sd_ in SEEDS[1:]:
            nets[sd_] = train(A, d, cond, sd_, **g)[0]
        for sd_, n_ in nets.items():
            o = test_outputs(n_, d, keep_features=(cond == "main_int" and sd_ == 0))
            np.savez_compressed(OD / "mlp" / f"test_fold{k}_{cond}_seed{sd_}.npz", **o)
            if cond == "direct":
                direct_outs[sd_] = o
            if cond in ("main_int", "main_add"):
                torch.save(dict(state=n_.state_dict(), rank=n_.rank), OD / "mlp" / f"model_fold{k}_{cond}_seed{sd_}.pt")
            if cond == "main_int":
                ids = decoded_id(n_, d)
                pd.DataFrame([dict(fold=k, seed=sd_, participant=f"sub-{SUBS[i]}", id_visual=np.mean(ids[i][0]), id_caption=np.mean(ids[i][1])) for i in ids]).to_csv(
                    OD / "mlp" / f"decoded_id_fold{k}_seed{sd_}.tsv", sep="\t", index=False, float_format="%.4f")
        print(f"fold {k} {cond} {show(g)} val r {vr:.4f} ep {ep} ({time.time() - t0:.0f}초)", flush=True)
    pd.DataFrame(sel).to_csv(OD / "mlp" / f"selected_fold{k}.tsv", sep="\t", index=False, float_format="%.4f")


# ---------- hierarchy ----------
def stage_hierarchy(A):
    import hierarchy_components as hc
    od = OD / "hierarchy"; od.mkdir(parents=True, exist_ok=True)
    vids, f_sp, Y = A["vids"], A["vf"], A["Y"]
    FC = hc.fold_components(Y, [A["V"]], A["C"], f_sp); D = Y.shape[1]
    yh = {k: np.zeros_like(Y) for k in "vsb"}; base = np.zeros_like(Y)
    for ff, (_, _, (pv, ps, pb)) in FC.items():
        te = f_sp == ff; yh["v"][te], yh["s"][te], yh["b"][te] = pv, ps, pb; base[te] = Y[f_sp != ff].mean(0)
    r2 = {k: np.mean(1 - ((Y - p) ** 2).sum(0) / ((Y - base) ** 2).sum(0)) for k, p in yh.items()}
    part = dict(r2_visual=r2["v"], r2_caption=r2["s"], r2_both=r2["b"], visual_only=r2["b"] - r2["s"], caption_only=r2["b"] - r2["v"], shared=r2["v"] + r2["s"] - r2["b"])
    print(part, flush=True); pd.DataFrame([part]).to_csv(od / "stimulus_partition.tsv", sep="\t", index=False, float_format="%.4f")
    rows = []; pos = {v: i for i, v in enumerate(vids)}
    for s in SUBS:
        rws, bfold, FB, *_ = rs.load_subject(s); B = FB["brain_roi469"]; groups = hc.roi_group_names(s)
        sidx = np.array([pos.get(x, -1) for x in rws.video_id.values]); use = sidx >= 0; plan = {}
        for f in np.unique(f_sp):
            inv_tr = np.full(len(vids), -1); inv_tr[f_sp != f] = np.arange((f_sp != f).sum())
            inv_te = np.full(len(vids), -1); inv_te[f_sp == f] = np.arange((f_sp == f).sum())
            rtr, rte = use & (bfold != f), use & (bfold == f)
            plan[f] = (rtr, rte, FC[f][0][inv_tr[sidx[rtr]]], FC[f][1][inv_te[sidx[rte]]])
        for g in list(dict.fromkeys(groups)) + ["Whole brain"]:
            Xg = B if g == "Whole brain" else B[:, groups == g]
            T = np.full((len(B), len(hc.NAMES) * D), np.nan); P = T.copy()
            for f, (rtr, rte, Ttr, Tte) in plan.items():
                mu, sd = Xg[rtr].mean(0), Xg[rtr].std(0); sd[sd == 0] = 1
                P[rte] = RidgeCV(alphas=hc.ALPHAS, alpha_per_target=True).fit((Xg[rtr] - mu) / sd, Ttr).predict((Xg[rte] - mu) / sd); T[rte] = Tte
            ok = np.isfinite(T).all(1); Tc, Pc = T.copy(), P.copy()
            for f in plan:
                m = (bfold == f) & ok; Tc[m] -= Tc[m].mean(0); Pc[m] -= Pc[m].mean(0)
            r = corr_cols(Pc[ok], Tc[ok])
            for ci, k in enumerate(hc.NAMES):
                rows.append(dict(participant=f"sub-{s}", group=g, n_roi=int(Xg.shape[1]), component=k, r=np.nanmean(r[ci * D:(ci + 1) * D])))
        print(f"sub-{s} 완료", flush=True)
    R = pd.DataFrame(rows); R.to_csv(od / "group_component_r.tsv", sep="\t", index=False, float_format="%.4f")
    W = R.groupby(["group", "component"]).r.mean().unstack(1); print(W.round(3).to_string())
    cort = [g for g in R.group.unique() if g.split("_")[0] in hc.NET_RANK]; rank = pd.Series({g: hc.NET_RANK[g.split("_")[0]] for g in cort})
    G = R[R.group.isin(cort)].groupby(["participant", "component"]).apply(lambda d: d.set_index("group").r.reindex(cort).corr(rank.reindex(cort), method="spearman"), include_groups=False).unstack(1)
    print(G.round(3).to_string()); print(G.mean().round(3).to_string()); G.to_csv(od / "gradient.tsv", sep="\t", float_format="%.3f")


# ---------- swap ----------
def stage_swap(A):
    (OD / "swap").mkdir(parents=True, exist_ok=True); rows = []; names = A["names"]; L = A["L"]; Y = A["Y"]; vf = A["vf"]
    pairs = {}
    for k in range(6):
        idx = np.flatnonzero(vf == k); Dm = ((L[idx][:, None] - L[idx][None]) ** 2).mean(-1); np.fill_diagonal(Dm, np.inf)
        pairs[k] = dict(zip(idx, idx[Dm.argmin(1)]))
    dist = [np.sqrt(((L[a] - L[b]) ** 2).mean()) for k in pairs for a, b in pairs[k].items()]
    print(f"쌍 {len(dist)}개, 이름표 거리 중앙값 {np.median(dist):.3f}", flush=True)
    for cond in ["main_int", "main_add"]:
        for seed in SEEDS:
            acc = {(i, m): [[], []] for i in range(5) for m in ["visual", "caption", "both"]}
            rng = np.random.default_rng(seed + 77)
            ctrl_store = {(i, m): [[] for _ in range(100)] for i in range(5) for m in ["visual", "caption", "both"]}
            y_store = {(i, m): [] for i in range(5) for m in ["visual", "caption", "both"]}
            for k in range(6):
                ck = torch.load(OD / "mlp" / f"model_fold{k}_{cond}_seed{seed}.pt", weights_only=False); d = fold_data(A, k)
                net = Net(A["n_roi"], A["V"].shape[1], A["C"].shape[1], True, True, ck["rank"]); net.load_state_dict(ck["state"]); net.eval()
                X, S, I = d["test"]
                with torch.no_grad():
                    h = net.encode(X, S); v, c = net.fv(h), net.fc(h)
                    gh = net.g(h)
                def score(hg, vv, cc):
                    z = hg + net.a(vv) + net.b(cc)
                    return z + net.U(net.A(vv) * net.B(cc)) if net.rank else z
                for i in range(5):
                    rowsi = np.flatnonzero(S.numpy() == i); here = {int(I[r]): r for r in rowsi}
                    ra, rb = [], []
                    for a, b in pairs[k].items():
                        if a in here and b in here:
                            ra.append(here[a]); rb.append(here[b])
                    ra, rb = np.array(ra), np.array(rb); dy = Y[I[rb]] - Y[I[ra]]
                    with torch.no_grad():
                        base = score(gh[ra], v[ra], c[ra]); pbase = torch.sigmoid(base)
                        for m, (vs, cs) in dict(visual=(v[rb], c[ra]), caption=(v[ra], c[rb]), both=(v[rb], c[rb])).items():
                            zs = score(gh[ra], vs, cs); acc[(i, m)][0].append((torch.sigmoid(zs) - pbase).numpy()); y_store[(i, m)].append(dy)
                        for rep in range(100):
                            rcand = rng.integers(0, len(rowsi), len(ra)); rc = rowsi[rcand]
                            bad = (rc == ra) | (rc == rb)
                            while bad.any():
                                rc[bad] = rowsi[rng.integers(0, len(rowsi), bad.sum())]; bad = (rc == ra) | (rc == rb)
                            dv_ = v[rc] - v[ra]; dc_ = c[rc] - c[ra]
                            lv = (v[rb] - v[ra]).norm(dim=1, keepdim=True) / dv_.norm(dim=1, keepdim=True).clamp_min(1e-8)
                            lc = (c[rb] - c[ra]).norm(dim=1, keepdim=True) / dc_.norm(dim=1, keepdim=True).clamp_min(1e-8)
                            vr_, cr_ = v[ra] + dv_ * lv, c[ra] + dc_ * lc
                            for m, (vs, cs) in dict(visual=(vr_, c[ra]), caption=(v[ra], cr_), both=(vr_, cr_)).items():
                                ctrl_store[(i, m)][rep].append((torch.sigmoid(score(gh[ra], vs, cs)) - pbase).numpy())
            for i in range(5):
                for m in ["visual", "caption", "both"]:
                    dp = np.vstack(acc[(i, m)][0]); dy = np.vstack(y_store[(i, m)]); r_real = corr_cols(dp, dy)
                    r_ctrl = np.mean([corr_cols(np.vstack(ctrl_store[(i, m)][rep]), dy) for rep in range(100)], axis=0)
                    for j, e in enumerate(names):
                        rows.append(dict(cond=cond, seed=seed, participant=f"sub-{SUBS[i]}", path=m, emotion=e, r_real=r_real[j], r_ctrl=r_ctrl[j], n_pairs=len(dp)))
            print(cond, seed, "완료", flush=True)
    pd.DataFrame(rows).to_csv(OD / "swap" / "swap_effects.tsv", sep="\t", index=False, float_format="%.4f")


# ---------- summary ----------
def stage_summary(A):
    names = A["names"]; Y = A["Y"]; rows = []; store = {}; conds = ["direct", "aux", "aux_shuffled", "main_add", "main_int", "distill", "smooth"]
    for cond in conds:
        for seed in SEEDS:
            pp = {i: [] for i in range(5)}; ii = {i: [] for i in range(5)}
            for k in range(6):
                o = np.load(OD / "mlp" / f"test_fold{k}_{cond}_seed{seed}.npz")
                for i in range(5):
                    m = o["sid"] == i; pp[i].append(o["p"][m]); ii[i].append(o["idx"][m])
            for i in range(5):
                p = np.vstack(pp[i]); idx = np.concatenate(ii[i]); store[(cond, seed, i)] = (idx, p)
                r = corr_cols(p, Y[idx]); rows.append(dict(cond=cond, seed=seed, participant=f"sub-{SUBS[i]}", mean_r=np.nanmean(r), n_nan=int(np.isnan(r).sum()), n_videos=len(idx), **dict(zip(names, r))))
    R = pd.DataFrame(rows); R.to_csv(OD / "mlp_scores.tsv", sep="\t", index=False, float_format="%.4f")
    by = R.groupby(["cond", "participant"]).mean_r.mean().unstack(0); seed_sd = R.groupby(["cond", "seed"]).mean_r.mean().groupby("cond").std()
    print(by.round(4).to_string()); print("5명 평균\n", by.mean().round(4).to_string()); print("seed SD\n", seed_sd.round(4).to_string())
    sel = pd.concat([pd.read_csv(OD / "mlp" / f"selected_fold{k}.tsv", sep="\t") for k in range(6)]); sel.to_csv(OD / "mlp_selected.tsv", sep="\t", index=False); print(sel.to_string())
    ids = pd.concat([pd.read_csv(f, sep="\t") for f in sorted((OD / "mlp").glob("decoded_id_fold*_seed*.tsv"))])
    dec = []
    for i in range(5):
        pv, pc, ii = [], [], []
        for k in range(6):
            o = np.load(OD / "mlp" / f"test_fold{k}_main_int_seed0.npz"); m = o["sid"] == i; pv.append(o["v"][m]); pc.append(o["c"][m]); ii.append(o["idx"][m])
        ii = np.concatenate(ii); dec.append(dict(participant=f"sub-{SUBS[i]}", r_visual=np.nanmean(corr_cols(np.vstack(pv).astype(np.float64), A["V"][ii])), r_caption=np.nanmean(corr_cols(np.vstack(pc).astype(np.float64), A["C"][ii]))))
    dec = pd.DataFrame(dec).merge(ids.groupby("participant")[["id_visual", "id_caption"]].mean().reset_index()); dec.to_csv(OD / "feature_decoding_main.tsv", sep="\t", index=False, float_format="%.4f"); print(dec.round(4).to_string()); print(dec.mean(numeric_only=True).round(4).to_string())
    rng = np.random.default_rng(20261103); nv = len(A["vids"]); boots = 1000; lines = []
    for a, b in [("aux", "direct"), ("main_int", "aux"), ("main_int", "direct"), ("main_add", "direct"), ("main_int", "main_add"), ("distill", "direct"), ("distill", "smooth"), ("smooth", "direct"), ("aux", "aux_shuffled"), ("aux", "distill")]:
        d_ = by[a] - by[b]; bs = np.zeros(boots)
        vbs = rng.integers(0, nv, (boots, nv))
        for t in range(boots):
            w = np.bincount(vbs[t], minlength=nv); vals = []
            for i in range(5):
                ra = []
                for c_ in (a, b):
                    per = []
                    for s in SEEDS:
                        idx, p = store[(c_, s, i)]; wi = np.repeat(np.arange(len(idx)), w[idx]); per.append(np.nanmean(corr_cols(p[wi], Y[idx][wi])))
                    ra.append(np.mean(per))
                vals.append(ra[0] - ra[1])
            bs[t] = np.mean(vals)
        lo, hi = 2 * d_.mean() - np.percentile(bs, 97.5), 2 * d_.mean() - np.percentile(bs, 2.5)
        lines.append(dict(a=a, b=b, mean_diff=d_.mean(), min=d_.min(), max=d_.max(), n_pos=int((d_ > 0).sum()), ci_lo=lo, ci_hi=hi)); print(lines[-1], flush=True)
    pd.DataFrame(lines).to_csv(OD / "mlp_contrasts.tsv", sep="\t", index=False, float_format="%.4f")
    pr = []
    for i in range(5):
        idx, p = store[("direct", 0, i)]; run = A["P"][SUBS[i]]; rmap = dict(zip(run["vid"], run["run"])); runs = np.array([rmap[A["vids"][j]] for j in idx]); obs = np.nanmean(corr_cols(p, Y[idx])); nulls = []
        rp = np.random.default_rng(100 + i)
        for _ in range(1000):
            perm = np.arange(len(idx))
            for r_ in np.unique(runs):
                m = np.flatnonzero(runs == r_); perm[m] = rp.permutation(m)
            nulls.append(np.nanmean(corr_cols(p, Y[idx][perm])))
        nulls = np.array(nulls); pr.append(dict(participant=f"sub-{SUBS[i]}", obs=obs, null_mean=nulls.mean(), null_max=nulls.max(), p=(1 + (nulls >= obs).sum()) / 1001))
    print(pd.DataFrame(pr).round(4).to_string()); pd.DataFrame(pr).to_csv(OD / "permutation_direct.tsv", sep="\t", index=False, float_format="%.4f")
    if (OD / "swap/swap_effects.tsv").exists():
        S = pd.read_csv(OD / "swap/swap_effects.tsv", sep="\t"); S["effect"] = S.r_real - S.r_ctrl
        P = S.groupby(["cond", "participant", "path", "seed"])[["r_real", "r_ctrl", "effect"]].mean().groupby(["cond", "participant", "path"]).mean().reset_index()
        T = P.groupby(["cond", "path"]).agg(r_real=("r_real", "mean"), r_ctrl=("r_ctrl", "mean"), effect=("effect", "mean"), eff_min=("effect", "min"), eff_max=("effect", "max"), n_pos=("effect", lambda x: int((x > 0).sum()))).round(4)
        print(T.to_string()); T.to_csv(OD / "swap/swap_summary.tsv", sep="\t")
        E = S[S.cond == "main_int"].groupby(["emotion", "path"]).effect.mean().unstack(1); E["caption_minus_visual"] = E.caption - E.visual
        E.sort_values("caption_minus_visual").round(4).to_csv(OD / "swap/swap_by_emotion.tsv", sep="\t"); print(E.sort_values("caption_minus_visual").round(3).to_string())


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--stage", required=True); ap.add_argument("--fold", type=int); ap.add_argument("--sub"); a = ap.parse_args()
    A = load_all(); print(f"개발 영상 {len(A['vids'])}개, 공통 영역 {A['n_roi']}개, 참가자별 행 " + ", ".join(str(len(A['P'][s]['vid'])) for s in SUBS), flush=True)
    assert not set(pd.read_csv(MAN / "mc_test72.tsv", sep="\t").mc_video_id) & set(A["vids"]), "MC 시험 영상이 남아 있다"
    if a.stage == "linear":
        stage_linear(A, a.sub)
    elif a.stage == "mlp":
        stage_mlp(A, a.fold)
    elif a.stage == "swap":
        stage_swap(A)
    elif a.stage == "hierarchy":
        stage_hierarchy(A)
    elif a.stage == "summary":
        stage_summary(A)
    (OD / "run_info.json").write_text(json.dumps(dict(n_videos=len(A["vids"]), n_roi=A["n_roi"], D=D, dropout=DROP, lr=LR, wd=WD, batch=BATCH, max_ep=MAX_EP, patience=PATIENCE, lams=LAMS, alphas=ALPHAS, ranks=RANKS, seeds=SEEDS), indent=1))


if __name__ == "__main__":
    main()
