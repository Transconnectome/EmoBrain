#!/usr/bin/env python3
"""S5 합성 자료 시험 (2026-11-06). 실제 정답과 실제 뇌 반응은 읽지 않는다. 표(S2 manifest)만 쓴다."""
import json
import os
import sys
import tempfile
from pathlib import Path

os.environ["S5_OUT"] = tempfile.mkdtemp(prefix="s5_tests_")
import numpy as np
import pandas as pd
import torch

import s4_common as c
import s5_baselines as b5
import s5_collect as col
import s5_common as d5
import s5_decoding as dec

RESULTS = []


def check(name, ok):
    RESULTS.append((name, bool(ok)))
    print("통과" if ok else "실패", name, flush=True)


def stops(f, errors=(SystemExit, ValueError)):
    try:
        f()
    except errors:
        return True
    return False


def synth(n=120, p=30, q=3, seed=0):
    g = np.random.default_rng(seed)
    X = g.normal(size=(n, p)).astype(np.float32)
    W = g.normal(size=(p, q))
    y = X @ W / np.sqrt(p) + 0.3 * g.normal(size=(n, q))
    brain = d5.BrainSet("sub-01", X, np.arange(1, n + 1), np.arange(n) % 6 + 1, [np.arange(0, 12), np.arange(10, 30)], p)
    return brain, y


def t_dual():
    g = torch.Generator().manual_seed(0)
    x = torch.randn(40, 15, generator=g, dtype=torch.float64)
    y = torch.randn(40, 3, generator=g, dtype=torch.float64)
    tr, te = np.arange(30), np.arange(30, 40)
    m = d5.DualRidge(x, tr, dict(te=te))
    p = m.predict("te", m.fit(y[tr]), 10.0)
    z, _, _ = d5.standardize(x, tr)
    zt = z[tr]
    beta = torch.linalg.solve(zt.T @ zt + 10 * torch.eye(15, dtype=torch.float64), zt.T @ (y[tr] - y[tr].mean(0)))
    check("dual ridge가 primal 닫힌 해와 같다", torch.allclose(p, y[tr].mean(0) + z[te] @ beta, atol=1e-8))
    x2 = x.clone()
    x2[te] += 100
    m2 = d5.DualRidge(x2, tr, dict(te=tr[:3]))
    check("입력 표준화에 시험 행이 들어가지 않는다(N3)", torch.allclose(m2.values, m.values))
    y2 = torch.randn(40, 7, generator=g, dtype=torch.float64)
    check("목표가 늘어도 같은 분해를 쓴다", m.predict("te", m.fit(y2[tr]), 10.0).shape == (10, 7))
    check("λ 후보는 10^1~10^6의 로그 간격 10개다(O18)", len(d5.LAMBDAS) == 10 and abs(d5.LAMBDAS[0] - 10) < 1e-9 and abs(d5.LAMBDAS[-1] - 1e6) < 1e-3)
    check("Horikawa 2020 후보는 10~10,000의 20개, 500 voxel이다(I7)", len(d5.H2020_LAMBDAS) == 20 and abs(d5.H2020_LAMBDAS[-1] - 1e4) < 1e-6 and d5.H2020_VOXELS == 500)


def t_selection():
    y = torch.tensor([[0.0, 1.0], [0.0, 2.0], [0.0, 3.0]], dtype=torch.float64)
    p = torch.tensor([[0.1, 2.0], [0.2, 2.0], [0.3, 2.0]], dtype=torch.float64)
    r = d5.r_selection(y, p)
    check("정답이 상수면 NaN, 예측이 상수면 0이다(O6)", r[0].isnan() and r[1] == 0)
    check("NaN 예측은 오류다", stops(lambda: d5.r_selection(y, torch.full_like(y, float("nan")))))
    check("정답이 상수인 목표는 λ를 고르지 않고 멈춘다", stops(lambda: d5.pick_per_target(torch.tensor([[float("nan")], [float("nan")]]))))
    s = torch.tensor([[0.5, 0.1], [0.5, 0.9]])
    check("점수가 같으면 작은 λ다(O6)", d5.pick_per_target(s).tolist() == [0, 1])


def t_versions():
    brain, y = synth()
    x = d5.as_tensor(brain.X, "cpu")
    yt = d5.as_tensor(y, "cpu")
    tr, va, te, r = b5.split_idx(brain.fold, 1)
    check("H2: 검증은 다음 fold, 학습은 나머지 4개다", set(brain.fold[va]) == {2} and set(brain.fold[tr]) == {3, 4, 5, 6} and set(brain.fold[te]) == {1})
    p, pick = d5.main_version(x, yt, tr, va, te)
    check("주 비교판은 목표마다 λ를 고른다(N15)", pick.shape == (3,) and p.shape == (len(te), 3))
    y2 = y.copy()
    y2[brain.fold == 1] += 50
    p2, pick2 = d5.main_version(x, d5.as_tensor(y2, "cpu"), tr, va, te)
    check("시험 fold의 정답을 바꿔도 주 비교판이 같다", torch.equal(p, p2) and torch.equal(pick, pick2))
    y4 = y.copy()
    y4[brain.fold == 2] = -y4[brain.fold == 2]
    one = np.array([100.0])
    a1, _ = d5.main_version(x, yt, tr, va, te, one)
    a2, _ = d5.main_version(x, d5.as_tensor(y4, "cpu"), tr, va, te, one)
    check("검증 fold의 정답은 학습에 들어가지 않고 선택에만 쓰인다(N15)", torch.equal(a1, a2))
    d = d5.DualRidge(x, tr, dict(test=te))
    a = d.predict("test", d.fit(yt[tr]), float(d5.LAMBDAS[int(pick[0])]))[:, 0]
    check("주 비교판의 예측은 학습 fold 4개로 학습한 모델의 값이다", torch.allclose(a, p[:, 0]))
    l, pl = d5.literature_version(x, yt, brain.fold, r["dk"], te)
    check("문헌판은 안쪽 5겹으로 고른다(H3)", pl.shape == (3,) and l.shape == p.shape)
    l2, pl2 = d5.literature_version(x, d5.as_tensor(y2, "cpu"), brain.fold, r["dk"], te)
    check("시험 fold의 정답을 바꿔도 문헌판이 같다", torch.equal(l, l2) and torch.equal(pl, pl2))
    dk = np.flatnonzero(np.isin(brain.fold, r["dk"]))
    d = d5.DualRidge(x, dk, dict(test=te))
    a = d.predict("test", d.fit(yt[dk]), float(d5.LAMBDAS[int(pl[0])]))[:, 0]
    check("문헌판의 예측은 D_k 전체로 학습한 모델의 값이다", torch.allclose(a, l[:, 0]))
    g = np.random.default_rng(1)
    check("입력의 NaN은 표준화에서 멈춘다", stops(lambda: d5.standardize(torch.tensor([[1.0], [1.0]]), [0, 1])))
    y_dim = g.normal(size=(120, 2))
    res = b5.ridge_task(brain, y, y_dim, 1, "cpu")
    check("정서와 14개 차원을 두 판 모두 저장한다(B4)", res["emotion_main"].shape == (20, 3) and res["dimension_main"].shape == (20, 2) and res["emotion_literature"].shape == (20, 3) and res["dimension_literature"].shape == (20, 2))
    dk_mask = np.isin(brain.fold, c.roles(1)["dk"])
    check("평균 예측은 D_k의 평균이다(O25)", np.allclose(res["mean_prediction"], y[dk_mask].mean(0)))
    single = b5.ridge_task(brain, y, y_dim * 1000, 1, "cpu")
    check("정답 크기를 바꿔도 예측은 그만큼 바뀐다(값 그대로 씀)", np.allclose(single["dimension_main"], res["dimension_main"] * 1000, atol=1e-6))


def t_decoding():
    brain, _ = synth()
    g = np.random.default_rng(2)
    W = g.normal(size=(30, 6))
    layers = [("vjepa2", 10), ("deberta", 6)]
    targets = {l: brain.X @ (W * (i + 1)) / np.sqrt(30) + 0.2 * g.normal(size=(120, 6)) + 5 for i, l in enumerate(layers)}
    pred, table, curves, oof = dec.decode_fold(brain, targets, layers, [layers[0]], 1, "cpu")
    check("층마다 λ를 하나 고른다(O18)", len(table) == 2 and table.lambda_index.between(0, 9).all())
    check("끝값 선택을 표에 적는다(O18)", "at_end" in table.columns)
    check("시험 예측은 시험 fold 영상이다", set(brain.fold[np.isin(brain.video_id, pred["video_id"])]) == {1})
    check("예측은 원래 척도다(O20)", abs(pred["vjepa2_10"].mean() - targets[layers[0]][brain.fold == 1].mean()) < 1)
    check("주 목표 층만 안쪽 fold 밖 예측을 저장한다(O34)", "vjepa2_10" in oof and "deberta_06" not in oof)
    check("안쪽 fold 밖 예측은 D_k 영상이고 시험 fold가 없다", set(brain.fold[np.isin(brain.video_id, oof["video_id"])]) == {2, 3, 4, 5, 6} and len(oof["video_id"]) == int((brain.fold != 1).sum()))
    check("안쪽 표시 fold가 그 영상의 fold와 같다", (brain.fold[oof["video_id"] - 1] == oof["inner_fold"]).all())
    t2 = {l: v.copy() for l, v in targets.items()}
    for l in t2:
        t2[l][brain.fold == 1] += 50
    pred2, table2, _, oof2 = dec.decode_fold(brain, t2, layers, [layers[0]], 1, "cpu")
    check("시험 fold의 실제 특징을 바꿔도 결과가 같다(H5)", np.array_equal(pred["vjepa2_10"], pred2["vjepa2_10"]) and table.lambda_index.tolist() == table2.lambda_index.tolist() and np.array_equal(oof["vjepa2_10"], oof2["vjepa2_10"]))
    b2 = d5.BrainSet(brain.participant, brain.X.copy(), brain.video_id, brain.fold, brain.roi_positions)
    b2.X[brain.fold == 1] = b2.X[brain.fold == 1] * 3 + 7
    d = dec.decode_fold(b2, targets, layers, [layers[0]], 1, "cpu")
    check("시험 fold의 뇌 입력을 바꿔도 학습과 선택은 같다(H5)", d[1].lambda_index.tolist() == table.lambda_index.tolist() and np.array_equal(d[3]["vjepa2_10"], oof["vjepa2_10"]))
    t3 = {l: v.copy() for l, v in targets.items()}
    j = 3
    t3[layers[0]][brain.fold == j] += 100
    _, _, _, oof3 = dec.decode_fold(brain, t3, layers, [layers[0]], 1, "cpu")
    # λ 하나로 고정해 fold j의 fold 밖 예측에 그 fold의 특징이 들어가지 않음을 본다
    one = np.array([100.0])
    _, _, _, o0 = dec.decode_fold(brain, targets, layers, [layers[0]], 1, "cpu", lambdas=one)
    _, _, _, o1 = dec.decode_fold(brain, t3, layers, [layers[0]], 1, "cpu", lambdas=one)
    rows = o0["inner_fold"] == j
    check("안쪽 겹의 실제 특징을 바꿔도 그 겹의 fold 밖 예측은 같다(N3)", np.allclose(o0["vjepa2_10"][rows], o1["vjepa2_10"][rows]))
    check("다른 겹의 예측은 달라진다", not np.allclose(o0["vjepa2_10"][~rows], o1["vjepa2_10"][~rows]))
    check("층은 64개이고 주 목표는 8개다", len(d5.LAYERS) == 64 and len(d5.TARGET_LAYERS) == 8 and set(d5.TARGET_LAYERS) <= set(d5.LAYERS))


def t_identification():
    t = np.random.default_rng(0).normal(size=(10, 20))
    check("예측이 정답과 같으면 식별은 1이다", col.identification(t, t) == 1)
    check("예측이 무관하면 식별은 0.5 근처다", 0.3 < col.identification(np.random.default_rng(1).normal(size=(200, 20)), np.random.default_rng(2).normal(size=(200, 20))) < 0.7)
    p = t.copy()
    p[0] = t[1]
    v = col.identification(p, t)
    check("틀린 영상은 정확도를 낮춘다", v < 1)
    a = np.array([[1.0, 2, 3], [3, 2, 1]])
    check("같은 값은 이긴 것으로 세지 않는다(크면 1, 아니면 0)", col.identification(a, a[[0, 0]]) == 0.0)


def t_layer_metrics():
    n = 60
    split = pd.DataFrame(dict(video_id=np.arange(1, n + 1), fold=np.arange(n) % 6 + 1))
    y = np.random.default_rng(0).normal(size=(n, 8)).astype(np.float32) * 3 + 2
    preds = {k: dict(video_id=split.video_id[split.fold == k].to_numpy(), vjepa2_10=y[split.fold == k]) for k in range(1, 7)}
    m = col.layer_metrics(preds, {("vjepa2", 10): y}, split, "sub-01")
    check("완벽한 예측의 차원별 r 평균과 식별이 1이다(O19, O20)", abs(m.mean_r[0] - 1) < 1e-6 and m.identification[0] == 1)


def t_soft_bce():
    brain, y = synth(n=120, p=30, q=3)
    p = 1 / (1 + np.exp(-y))
    s = dict(lr=1e-2, batch=16, max_epochs=30, patience=5, seed=0)
    a, tab, wd = b5.soft_bce_task(brain, p, 1, "cpu", settings=s)
    b, tab2, _ = b5.soft_bce_task(brain, p, 1, "cpu", settings=s)
    check("soft BCE 선형의 후보는 weight decay 3개다(O24)", d5.SOFT_BCE_DECAYS == (1e-4, 1e-3, 1e-2) and len(tab) == 3)
    check("같은 seed면 같은 예측이다", np.array_equal(a["pred"], b["pred"]))
    check("예측은 0~1이다", ((a["pred"] >= 0) & (a["pred"] <= 1)).all())
    check("조기 종료로 멈춘 epoch를 적는다", (tab.epoch <= 30).all() and (tab.epoch >= 1).all())
    check("G13 값을 쓴다", d5.SOFT_BCE == dict(lr=1e-3, batch=64, max_epochs=300, patience=30, seed=0))
    p2 = p.copy()
    p2[brain.fold == 1] = 1 - p2[brain.fold == 1]
    c2, tab3, _ = b5.soft_bce_task(brain, p2, 1, "cpu", settings=s)
    check("시험 fold의 정답을 바꿔도 예측이 같다", np.array_equal(a["pred"], c2["pred"]) and tab.val_r.equals(tab3.val_r))
    m = torch.nn.Linear(4, 2)
    o = b5.make_optimizer(m, 1e-3, 0.5)
    check("weight decay는 weight에만 적용한다", o.param_groups[0]["weight_decay"] == 0.5 and o.param_groups[1]["weight_decay"] == 0.0)


def t_h2020():
    g = np.random.default_rng(0)
    n, v = 60, 40
    X = g.normal(size=(n, v))
    y = X[:, :2] + 0.1 * g.normal(size=(n, 2))
    x, yt = d5.as_tensor(X, "cpu"), d5.as_tensor(y, "cpu")
    tr, te = np.arange(48), np.arange(48, 60)
    lam = np.array([10.0, 100.0])
    p = b5.h2020_fit(x, yt, tr, te, lam, 5)
    z, _, _ = d5.standardize(x, tr)
    zy, ym, ys = d5.standardize(yt, tr)
    idx = (z[tr].T @ zy[tr, 0] / len(tr)).abs().topk(5).indices
    w = torch.linalg.solve(z[tr][:, idx].T @ z[tr][:, idx] + 100 * torch.eye(5, dtype=torch.float64), z[tr][:, idx].T @ zy[tr, 0])
    check("복셀 선택 ridge가 목표별 상위 voxel의 닫힌 해와 같다(I7)", torch.allclose(p[1, :, 0], z[te][:, idx] @ w * ys[0] + ym[0], atol=1e-8))
    X2 = X.copy()
    X2[te] += 100
    y2 = y.copy()
    y2[te] = -y2[te]
    p2 = b5.h2020_fit(d5.as_tensor(X2, "cpu"), d5.as_tensor(y2, "cpu"), tr, tr[:12], lam, 5)
    p3 = b5.h2020_fit(x, yt, tr, tr[:12], lam, 5)
    check("voxel 선택과 표준화에 시험 행이 들어가지 않는다(H5)", torch.allclose(p2, p3))
    small = b5.h2020_fit(x[:, :3], yt, tr, te, lam, 500)
    check("ROI voxel이 500보다 적으면 전부 쓴다", small.shape == (2, 12, 2))
    fold = np.arange(n) % 6 + 1
    out, pick, score = b5.h2020_roi(x, yt, fold, c.roles(1)["dk"], np.flatnonzero(fold == 1), lam, 5)
    check("목표마다 λ를 고르고 D_k로 학습한다", pick.shape == (2,) and out.shape == (10, 2) and score.shape == (2,))
    pr = np.arange(24.0).reshape(2, 3, 4)  # 시험 2 × ROI 3 × 목표 4
    val = np.array([[0.2, 0.0, 0.2, 0.0], [0.1, 0.05, 0.0, 0.0], [0.0, 0.01, 0.2, 0.0]])
    e, cnt = b5.h2020_ensemble(pr, val)
    check("ensemble은 기준 이상 ROI의 평균이다", np.allclose(e[0, 0], (pr[0, 0, 0] + pr[0, 1, 0]) / 2) and cnt.tolist() == [2, 0, 2, 0])
    check("기준을 넘는 ROI가 없으면 안쪽 r이 가장 높은 ROI다", np.allclose(e[0, 1], pr[0, 1, 1]))


def t_video_zone():
    brain, y = synth()
    res = b5.video_task(np.log(np.arange(1, 121))[:, None], y, brain.fold, brain.video_id, 1, "cpu")
    check("길이 기준선은 fold의 모든 영상을 시험한다", sorted(res["video_id"].tolist()) == brain.video_id[brain.fold == 1].tolist() and res["pred"].shape == (20, 3))
    split = pd.DataFrame(dict(video_id=np.arange(1, 121), content_id=np.arange(1, 121), fold=np.arange(120) % 6 + 1))
    blocks = pd.DataFrame(dict(video_id=split.video_id, fold=split.fold, block=(np.arange(120) % 5) + 1))
    r = c.roles(1)
    tr_ids = split.video_id[split.fold.isin(r["train"])].tolist()
    va_ids = split.video_id[split.fold == r["val"]].tolist()
    ntr = sum(blocks.set_index("video_id").block[v] != 1 for v in tr_ids)
    nva = sum(blocks.set_index("video_id").block[v] != 1 for v in va_ids)
    control = pd.DataFrame(dict(block=1, fold=1, role=["train"] * ntr + ["val"] * nva, video_id=tr_ids[:ntr] + va_ids[:nva]))
    a = b5.zone_task(brain, y, split, 1, 1, "excluded", "cpu", blocks, control)
    b = b5.zone_task(brain, y, split, 1, 1, "control", "cpu", blocks, control)
    inb = set(blocks.video_id[blocks.block == 1])
    check("구역 시험은 그 구역과 그 fold의 영상이다", set(a["video_id"]) <= inb and set(split.fold[np.isin(split.video_id, a["video_id"])]) == {1})
    check("두 제외 방식의 시험 영상이 같다(4-3)", a["video_id"].tolist() == b["video_id"].tolist())
    y2 = y.copy()
    y2[np.isin(brain.video_id, list(inb))] += 50
    a2 = b5.zone_task(brain, y2, split, 1, 1, "excluded", "cpu", blocks, control)
    check("구역 제외 학습은 빠진 구역의 정답을 쓰지 않는다", np.array_equal(a["pred"], a2["pred"]))
    b3 = d5.BrainSet(brain.participant, brain.X[brain.video_id != a["video_id"][0]], brain.video_id[brain.video_id != a["video_id"][0]], brain.fold[brain.video_id != a["video_id"][0]], brain.roi_positions)
    a3 = b5.zone_task(b3, y[brain.video_id != a["video_id"][0]], split, 1, 1, "excluded", "cpu", blocks, control)
    check("block이 없는 영상은 그 참가자에서 빠진다(B7)", a3["pred"].shape[0] == a["pred"].shape[0] - 1)


def t_boundaries():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        table = pd.DataFrame(dict(participant="sub-99", video_id=[11, 22, 33], content_id=[11, 22, 33], qc_row=[5, 1, 3]))
        cw = pd.Series({11: 1011, 22: 1022, 33: 1033, 44: 1044})
        check("허용 행은 qc_row 순서다", d5.allowed_rows("99", table, cw, []).qc_row.tolist() == [1, 3, 5])
        check("MC 72개와 같은 내용이 있으면 멈춘다", stops(lambda: d5.allowed_rows("99", table, cw, [1022])))
        check("표에 없는 영상이 있으면 멈춘다", stops(lambda: d5.allowed_rows("99", table, pd.Series({11: 1011}), [])))
        check("허용되지 않은 반응 행은 읽지 않는다", stops(lambda: d5.read_rows(np.zeros((6, 2)), [0], [1, 3, 5])))
        raw = np.arange(60, dtype=np.float32).reshape(6, 10)
        np.save(td / "raw.npy", raw)
        np.savez(td / "roi.npz", columns=np.array([1, 2, 2, 7]), offsets=np.array([0, 3, 4]), n_columns=np.array(10))
        split = pd.DataFrame(dict(video_id=[11, 22, 33], fold=[1, 2, 3]))
        b = d5.load_brain("99", split, td / "raw.npy", td / "roi.npz", table, cw, [])
        check("겹치는 voxel은 한 번만 쓴다", b.X.shape == (3, 3) and b.n_voxels_with_overlap == 4)
        check("block 값을 허용 행에서 읽는다", np.array_equal(b.X[0], raw[1][[1, 2, 7]]) and b.video_id.tolist() == [22, 33, 11])
        check("ROI 위치가 고유 voxel 열을 가리킨다", b.roi_positions[0].tolist() == [0, 1, 1] and b.roi_positions[1].tolist() == [2])
        check("fold가 영상에 맞는다", b.fold.tolist() == [2, 3, 1])
        check("개발 영상이 아닌 행은 멈춘다", stops(lambda: d5.load_brain("99", pd.DataFrame(dict(video_id=[11, 22], fold=[1, 2])), td / "raw.npy", td / "roi.npz", table, cw, [])))
        bad = raw.copy()
        bad[1, 2] = np.nan
        np.save(td / "bad.npy", bad)
        check("읽은 반응의 NaN에서 멈춘다", stops(lambda: d5.load_brain("99", split, td / "bad.npy", td / "roi.npz", table, cw, [])))
        np.savez(td / "wrong.npz", columns=np.array([1]), offsets=np.array([0, 1]), n_columns=np.array(11))
        check("열 수가 다르면 멈춘다", stops(lambda: d5.load_brain("99", split, td / "raw.npy", td / "wrong.npz", table, cw, [])))
        sig, ids = d5.signal_baseline_input("99", split, td / "raw.npy", table, cw, [])
        check("block 통계는 block마다 voxel 평균과 표준편차다(I7, 04 S1)", ids.tolist() == [22, 33, 11] and np.allclose(sig[0], [raw[1].mean(), raw[1].std()]))
        f = td / "x.npy"
        np.save(f, np.zeros(2))
        r1 = d5.Run(None, {"a": f}, task="t")
        np.save(f, np.ones(2))
        check("입력이 바뀌면 멈춘다", stops(r1.check))
        check("입력이 다르면 실행 번호가 다르다", d5.Run(None, {"a": f}, task="t").key != r1.key)
        check("S2 표와 블록 표가 실행 번호에 들어간다", "s2:participant_blocks_hk.tsv" in r1.hashes and "s2:mc_test72.tsv" in r1.hashes)
    for args in (("",), ("0" * 40,)):
        check(f"동결 커밋 없이는 실제 실행이 멈춘다({args[0][:4]})", stops(lambda: c.guard(*args)))
    s = c.load_split()
    t = pd.read_csv(d5.BLOCKS, sep="\t")
    check("참가자 block은 모두 개발 영상이다", set(t.video_id) <= set(s.video_id))
    for p in d5.HK:
        d5.allowed_rows(p)
    check("다섯 명의 허용 행 표가 MC 72개와 겹치지 않는다", True)


def t_collect():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        np.savez(td / "a.npz", video_id=np.array([1, 2]), pred=np.zeros((2, 3)))
        col.check_pred(td / "a.npz", [2, 1], dict(pred=3))
        check("영상이 빠지면 멈춘다", stops(lambda: col.check_pred(td / "a.npz", [1, 2, 3], dict(pred=3))))
        np.savez(td / "b.npz", video_id=np.array([1, 1]), pred=np.zeros((2, 3)))
        check("같은 영상이 두 번이면 멈춘다", stops(lambda: col.check_pred(td / "b.npz", [1, 1], dict(pred=3))))
        check("크기가 다르면 멈춘다", stops(lambda: col.check_pred(td / "a.npz", [1, 2], dict(pred=2))))
        p = np.zeros((2, 3))
        p[0, 0] = np.nan
        np.savez(td / "c.npz", video_id=np.array([1, 2]), pred=p)
        check("NaN이 있으면 멈춘다", stops(lambda: col.check_pred(td / "c.npz", [1, 2], dict(pred=3))))
        for n, h, f in (("x", "1", "a"), ("y", "1", "a")):
            (td / n).mkdir()
            (td / n / "done.json").write_text(json.dumps(dict(code_sha256="c", design_freeze=f, inputs=dict(r=h))))
        col.check_runs(td, ["x", "y"])
        (td / "y/done.json").write_text(json.dumps(dict(code_sha256="c", design_freeze="a", inputs=dict(r="2"))))
        check("같은 역할의 입력 내용이 다르면 멈춘다", stops(lambda: col.check_runs(td, ["x", "y"])))
        (td / "y/done.json").write_text(json.dumps(dict(code_sha256="d", design_freeze="a", inputs=dict(r="1"))))
        check("코드가 다르면 멈춘다", stops(lambda: col.check_runs(td, ["x", "y"])))
    table = pd.DataFrame(dict(participant="sub-01", video_id=[1, 2, 7]))
    split = pd.DataFrame(dict(video_id=np.arange(1, 13), fold=np.arange(12) % 6 + 1))
    e = col.expected_tests(split, table, "01")
    check("참가자의 시험 영상은 그 block이 있는 영상이다", e[1] == [1, 7] and e[2] == [2] and e[3] == [])


def main():
    for f in (t_dual, t_selection, t_versions, t_decoding, t_identification, t_layer_metrics, t_soft_bce, t_h2020, t_video_zone, t_boundaries, t_collect):
        f()
    bad = [n for n, ok in RESULTS if not ok]
    print("통과", len(RESULTS) - len(bad), "실패", len(bad), bad)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
