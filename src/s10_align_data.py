#!/usr/bin/env python3
"""S10 6-4i 공통 입력(01 6-4i, 11/22). ①(s10_shared_ae.py), ②(s10_usae.py)가 같이 쓴다. CPU.

입력(모두 정서 평정을 보지 않는다)
- 뇌: 참가자마다 voxel 반응(s5_common.load_brain, MC 72개는 읽기 전에 뺌). 바깥 fold k마다 학습 fold 행으로 표준화하고 PCA N_PC개.
- Vision feature: V-JEPA 2 target(5,632차원, encoder 2와 같음). Caption feature: 정서어를 지운 DeBERTa(4,096차원, 6-4d의 C).
  둘 다 바깥 fold k마다, 그 실행에서 쓰는 영상의 학습 fold 행으로 표준화하고 PCA N_PC개.
- 캡션 잔차(①의 셋째 modality): 캡션 PCA에서 Vision PCA로 맞힐 수 있는 부분을 뺀 것. ridge(λ는 검증 fold R²로 하나 고름),
  학습 fold 행은 학습 fold끼리 cross-fitting(6-4d와 같은 방식), 검증과 시험 행은 학습 fold 넷으로 맞춘 ridge로 뺀다.
- 크기 맞춤: modality마다 학습 행에서 좌표 제곱 평균이 1이 되게 나눈다(USAE의 모델별 표준화와 같은 뜻).
brain 단계(참가자마다 한 번): <out>/brain_pca/sub-0X.npz. video_id, fold, fold k마다 PCA 점수(행 × N_PC), 설명 분산 비,
  네트워크 13개마다 성분 적재값의 평균(N_PC × 13, ② 개념의 네트워크 무게용).
사용: s10_align_data.py brain --participant 01 --out <폴더> --design-freeze <커밋> [--threads 8]
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

import s4_common as c

N_PC = 256
VISION, CAPTION = "vjepa2/target", "deberta_no_emotion_words/target"
PARTICIPANTS = ("01", "02", "03", "04", "05")
KEY_TEST = "key_test_v3_GO_GR"  # 6-4d 셋째 판, x = 뇌 없이 object relations가 objects 위에 더하는 정도
CK7 = ("pride", "triumph", "contempt", "disappointment", "sympathy", "guilt", "envy")


def standardize_pca(x, train, n_pc=N_PC):
    """학습 행으로 표준화하고 PCA. 돌려주는 값: (모든 행의 점수, 성분(n_pc × 열), 설명 분산 비). 학습 행 수보다 많은 성분은 만들지 않는다."""
    x = np.asarray(x, np.float64)
    m, s = c.fit_standardizer(x[train])
    z = (x - m) / s
    zt = z[train]
    n = min(n_pc, len(train) - 1)
    g = zt @ zt.T  # 학습 행 수 × 학습 행 수
    w, u = np.linalg.eigh(g)
    order = np.argsort(w)[::-1][:n]
    w, u = np.clip(w[order], 0, None), u[:, order]
    comps = (u.T @ zt) / np.sqrt(w)[:, None]  # 단위 길이 성분
    ratio = w / np.trace(g)
    return c.finite(z @ comps.T, "PCA 점수"), comps, ratio


def scale_rms(x, train):
    """학습 행의 좌표 제곱 평균이 1이 되게 나눈다."""
    s = float(np.sqrt(np.mean(np.asarray(x[train], np.float64) ** 2)))
    if not s > 0:
        raise ValueError("크기가 0인 입력")
    return x / s


def ridge_fit(x, y, lam):
    """절편 있는 다출력 ridge. 돌려주는 값: (가중치, 절편)."""
    mx, my = x.mean(0), y.mean(0)
    xc, yc = x - mx, y - my
    w = np.linalg.solve(xc.T @ xc + lam * np.eye(x.shape[1]), xc.T @ yc)
    return w, my - mx @ w


def r2_weighted(y, p):
    """분산 가중 R²(열 전체의 잔차 제곱합 / 전체 제곱합)."""
    y, p = np.asarray(y, np.float64), np.asarray(p, np.float64)
    return float(1.0 - ((y - p) ** 2).sum() / ((y - y.mean(0)) ** 2).sum())


def caption_residual(cap, vis, fold, k, lambdas=None):
    """①의 캡션 잔차. 학습 fold 행은 학습 fold끼리 cross-fitting, 검증과 시험 행은 학습 fold 넷으로 맞춘 ridge. λ는 검증 fold R²로 하나."""
    import s5_common as d5
    lambdas = d5.LAMBDAS if lambdas is None else lambdas
    r = c.roles(k)
    tr, va = np.flatnonzero(np.isin(fold, r["train"])), np.flatnonzero(fold == r["val"])
    scores = []
    for lam in lambdas:
        w, b = ridge_fit(vis[tr], cap[tr], lam)
        scores.append(r2_weighted(cap[va], vis[va] @ w + b))
    lam = float(lambdas[int(np.argmax(scores))])
    pred = np.full(cap.shape, np.nan)
    w, b = ridge_fit(vis[tr], cap[tr], lam)
    rest = np.flatnonzero(~np.isin(fold, r["train"]))
    pred[rest] = vis[rest] @ w + b
    for j in r["train"]:
        inner_tr, inner_te = np.flatnonzero(np.isin(fold, [f for f in r["train"] if f != j])), np.flatnonzero(fold == j)
        w, b = ridge_fit(vis[inner_tr], cap[inner_tr], lam)
        pred[inner_te] = vis[inner_te] @ w + b
    c.finite(pred, "캡션 잔차 예측")
    return cap - pred, dict(lambda_=lam, val_r2=float(max(scores)))


def scene_inputs(video_ids, fold, k, split, residual=True):
    """바깥 fold k의 Vision PCA, 캡션 PCA(, 캡션 잔차). 표준화와 PCA는 video_ids 가운데 학습 fold 행으로만 맞춘다."""
    tr = np.flatnonzero(np.isin(fold, c.roles(k)["train"]))
    vis, _, rv = standardize_pca(c.load_rows(VISION, video_ids, split), tr)
    cap, _, rc = standardize_pca(c.load_rows(CAPTION, video_ids, split), tr)
    info = dict(vision_var_ratio=float(rv.sum()), caption_var_ratio=float(rc.sum()))
    out = dict(vision=scale_rms(vis, tr), caption=scale_rms(cap, tr))
    if residual:
        res, ri = caption_residual(out["caption"], out["vision"], fold, k)
        out["caption_resid"] = scale_rms(res, tr)
        info.update(caption_resid=ri)
    return out, info


def load_brain_pca(out, participant, k):
    """brain 단계의 결과에서 fold k의 PCA 점수(학습 행 크기 맞춤 뒤). 돌려주는 값: (video_id, fold, 점수, 네트워크 적재 평균, 네트워크 이름)."""
    z = np.load(Path(out) / "brain_pca" / f"sub-{participant}.npz")
    vid, fold = z["video_id"].astype(np.int64), z["fold"].astype(np.int64)
    x = z[f"pcs_fold{k}"].astype(np.float64)
    tr = np.flatnonzero(np.isin(fold, c.roles(k)["train"]))
    return vid, fold, scale_rms(x, tr), z[f"net_fold{k}"], z["networks"].tolist()


def ratings(split, video_ids):
    """34개 정서 평정(행 = video_ids 순서)과 이름, 27개판 표시."""
    y, cols = c.load_scores(split, "emotions")
    pos = {v: i for i, v in enumerate(split.video_id.tolist())}
    lm = pd.read_csv(c.LABEL_MAP, sep="\t")
    names = lm.set_index("score_col").loc[cols, "name"].tolist()
    return np.asarray(y, np.float64)[[pos[v] for v in np.asarray(video_ids).tolist()]], names, np.array([e not in CK7 for e in names])


def key_test_x(stats_root):
    """6-4d 셋째 판(GO 대 GR)의 정서별 x(뇌 전체 행). 돌려주는 값: 정서 이름 -> x."""
    t = pd.read_csv(Path(stats_root) / KEY_TEST / "points.tsv", sep="\t")
    t = t[t.network == "whole_brain"]
    if len(t) != 27:
        raise ValueError("핵심 시험 x가 27개 정서가 아니다")
    return dict(zip(t.emotion, t.x.astype(float)))


def zone_of(video_ids):
    """6-2b 캡션 구역(다섯 구역). 짝 섞기 대조가 이 구역 안에서만 섞는다."""
    import s6_common as S
    b = pd.read_csv(S.CAPTION_BLOCKS[0], sep="\t").set_index("video_id").block
    z = b.reindex(np.asarray(video_ids)).to_numpy()
    if pd.isna(z).any():
        raise ValueError("캡션 구역이 없는 영상이 있다")
    return z.astype(np.int64)


def zone_shuffle(video_rows, zones, rng):
    """video_rows(행 번호) 안에서, 같은 캡션 구역끼리만 짝을 섞은 순열. 돌려주는 값: 길이가 같은 행 번호 배열(섞인 장면 행)."""
    rows = np.asarray(video_rows)
    out = rows.copy()
    for z in np.unique(zones[rows]):
        sel = np.flatnonzero(zones[rows] == z)
        out[sel] = rows[sel][rng.permutation(len(sel))]
    return out


def brain(a):
    import s5_common as d5
    import s10_geometry as geo
    c.guard(a.design_freeze)
    import torch
    torch.set_num_threads(a.threads)
    started = time.time()
    split = c.load_split()
    b = d5.load_brain(a.participant, split)
    fold = np.asarray(b.fold, np.int64)
    nets = geo.network_positions(b)
    res, info = {}, dict(participant=b.participant, n_rows=int(len(fold)), n_voxels=int(b.X.shape[1]), n_pc=N_PC, folds={})
    for k in range(1, c.N_FOLDS + 1):
        tr = np.flatnonzero(np.isin(fold, c.roles(k)["train"]))
        pcs, comps, ratio = standardize_pca(b.X, tr)
        res[f"pcs_fold{k}"] = pcs.astype(np.float32)
        res[f"net_fold{k}"] = np.stack([comps[:, p].mean(1) for p in nets.values()], 1).astype(np.float32)
        res[f"ratio_fold{k}"] = ratio.astype(np.float32)
        info["folds"][k] = dict(n_train=int(len(tr)), var_ratio=float(ratio.sum()))
    o = Path(a.out) / "brain_pca"
    o.mkdir(parents=True, exist_ok=True)
    np.savez(o / f"{b.participant}.npz", video_id=np.asarray(b.video_id, np.int64), fold=fold, networks=np.array(list(nets)), **res)
    info.update(design_freeze=a.design_freeze, code_commit=c.START_HEAD, code_dirty=c.START_DIRTY, seconds=round(time.time() - started, 1))
    (o / f"run_info_{b.participant}.json").write_text(json.dumps(info, indent=1))
    print(json.dumps(info), flush=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 6-4i 공통 입력")
    ap.add_argument("step", choices=("brain",))
    ap.add_argument("--participant", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", default="")
    ap.add_argument("--threads", type=int, default=8)
    brain(ap.parse_args(argv))


if __name__ == "__main__":
    main()
