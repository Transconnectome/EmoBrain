#!/usr/bin/env python3
"""S4 합성 자료 시험 (2026-11-06). 실제 정답과 뇌 반응은 읽지 않는다. 표(S2 manifest)와 특징 파일의 존재만 쓴다."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

os.environ["S4_OUT"] = tempfile.mkdtemp(prefix="s4_tests_")
import numpy as np
import pandas as pd
import torch

import s4_collect as col
import s4_common as c
import s4_feature_model as fm
import s4_ridge as rg
import s4_window_change as wc

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


def synth(n=120, dv=12, dc=8, q=3, seed=1, dims=False):
    g = np.random.default_rng(seed)
    v, cap = g.normal(size=(n, dv)).astype(np.float32), g.normal(size=(n, dc)).astype(np.float32)
    s = v[:, :q] + cap[:, :q] + 0.3 * g.normal(size=(n, q))
    y = s if dims else 1 / (1 + np.exp(-s))
    return fm.Data(np.arange(1, n + 1), np.arange(n) % 6 + 1, v, cap, y.astype(np.float32))


FAST = fm.Spec(max_epochs=3, batch=16, candidates=((0, 1e-3), (2, 1e-3)))


def t_model():
    v, cap = torch.randn(5, 12), torch.randn(5, 8)
    m0, m2 = fm.FeatureModel(12, 8, 3, 0), fm.FeatureModel(12, 8, 3, 2)
    check("r = 0에는 상호작용 항이 없다", not hasattr(m0, "U") and hasattr(m2, "U"))
    check("a, b는 편향이 있고 A, B, U는 편향이 없다(O5)", m2.a.bias is not None and m2.b.bias is not None and m2.A.bias is None and m2.B.bias is None and m2.U.bias is None)
    check("상호작용 꼴이 E2와 같다", torch.allclose(m2(v, cap), m2.a(v) + m2.b(cap) + m2.U(m2.A(v) * m2.B(cap))))
    v2, c2 = torch.randn(5, 12), torch.randn(5, 8)
    i = m0(v2, c2) - m0(v, c2) - m0(v2, cap) + m0(v, cap)
    check("더하기판의 결합 지표는 0이다", i.abs().max() < 1e-5)


def t_candidates():
    check("후보는 r 5개와 weight decay 3개이고 순서가 O6의 동점 규칙이다", fm.CANDIDATES[0] == (0, 1e-4) and fm.CANDIDATES[-1] == (8, 1e-2) and len(fm.CANDIDATES) == 15)
    t = pd.DataFrame(fm.CANDIDATES, columns=["r", "weight_decay"])
    t["epochs"], t["val_r"] = 5, 0.5
    check("점수가 같으면 가장 작은 r과 weight decay를 고른다", fm.choose(t).r == 0 and fm.choose(t).weight_decay == 1e-4)
    t.loc[(t.r == 4) & (t.weight_decay == 1e-3), "val_r"] = 0.9
    check("가장 큰 점수를 고른다", fm.choose(t).r == 4)
    check("더하기판은 r = 0 안에서 고른다(O17)", fm.choose(t, [0]).r == 0)
    check("상호작용판은 r > 0 안에서 고른다(O17)", fm.choose(t, [1, 2, 8]).r > 0 and fm.choose(t, [1, 2, 8]).val_r == 0.5)


def t_r_selection():
    y = torch.tensor([[0.0, 1.0], [0.0, 2.0], [0.0, 3.0]])
    p = torch.tensor([[0.3, 1.0], [0.1, 2.0], [0.2, 3.0]])
    keep = y.amax(0) > y.amin(0)
    check("y가 상수인 정서는 선택 계산에서 뺀다(O6)", abs(fm._r_selection(p, y, keep).item() - 1) < 1e-5)
    y2 = torch.tensor([[0.0, 1.0], [1.0, 2.0], [2.0, 3.0]])
    p2 = torch.tensor([[0.5, 1.0], [0.5, 2.0], [0.5, 3.0]])
    check("예측이 상수인 정서는 r = 0으로 센다(O6)", abs(fm._r_selection(p2, y2, y2.amax(0) > y2.amin(0)).item() - 0.5) < 1e-5)


def t_search_rule():
    """epoch는 겹 평균 곡선으로 정하고 겹마다 따로 정하지 않는다."""
    curves = {1: np.array([3.0, 1.0, 3.0]), 2: np.array([1.0, 2.0, 0.0])}
    scores = {1: np.array([0.1, 0.2, 0.3]), 2: np.array([0.4, 0.6, 0.8])}
    orig = fm.train
    fm.train = lambda spec, r, wd, fold, va, keep_preds=False, device="cpu": (None, curves[fold], scores[fold], None)
    try:
        t, mc, _ = fm.search(fm.Spec(max_epochs=3, candidates=((0, 1e-3),)), {1: (1, None), 2: (2, None)}, "cpu")
    finally:
        fm.train = orig
    check("epoch 수는 겹 평균 곡선의 최소다(O16)", int(t.epochs[0]) == 2 and abs(mc[0, 1] - 1.5) < 1e-9)
    check("그 epoch의 r을 겹 평균한다(O16)", abs(t.val_r[0] - 0.4) < 1e-9)


def t_reproducible():
    d = synth()
    coord = fm.Coordinates(d.v, d.cap)
    tr = coord.tensors(d.v, d.cap, d.y, "cpu")
    a, *_ = fm.train(FAST, 2, 1e-3, tr)
    b, *_ = fm.train(FAST, 2, 1e-3, tr)
    check("같은 seed면 같은 가중치다(O32)", all(torch.equal(x, y) for x, y in zip(a.state_dict().values(), b.state_dict().values())))
    _, cu, _, _ = fm.train(FAST, 0, 1e-3, tr, va=tr)
    check("최대 epoch까지 곡선을 다 그린다(겹마다 멈추지 않는다)", len(cu) == 3)


def _tvs(d, k=1, spec=FAST):
    with tempfile.TemporaryDirectory() as t:
        out = Path(t)
        fm.task_tvs(spec, d, k, "cpu", out)
        return {f.name: dict(np.load(f)) if f.suffix == ".npz" else torch.load(f, weights_only=False) if f.suffix == ".pt" else None for f in out.iterdir()}


def same(a, b):
    return all(np.array_equal(a[k], b[k]) for k in a)


def t_leak():
    d = synth()
    base = _tvs(d)
    oof = base["oof.npz"]
    r = c.roles(1)
    check("OOF 영상은 H2 학습 fold에만 있다(E4)", set(d.folds[oof["video_id"] - 1].tolist()) == set(r["train"]) and len(oof["video_id"]) == int(d.mask(r["train"]).sum()))
    check("OOF 값은 0~1이고 자르기 전 값을 함께 저장한다(E4)", ((oof["p_clipped"] >= 0) & (oof["p_clipped"] <= 1)).all() and "p_raw" in oof and "logit" in oof)
    check("시험 예측은 시험 fold 영상이다", set(d.folds[base["test_pred.npz"]["video_id"] - 1].tolist()) == {1})
    m = base["coordinates.npz"]
    dk = d.mask(r["dk"])
    check("표준화는 D_k의 평균과 표준편차다(N3, H4)", np.allclose(m["visual_mean"], d.v[dk].astype(np.float64).mean(0)) and np.allclose(m["caption_std"], d.cap[dk].astype(np.float64).std(0)))
    t = synth()
    te = t.mask([1])
    t.v[te] += 5
    t.cap[te] -= 3
    t.y[te] = 1 - t.y[te]
    a = _tvs(t)
    check("시험 fold를 바꿔도 표준화가 같다", same(base["coordinates.npz"], a["coordinates.npz"]))
    check("시험 fold를 바꿔도 OOF가 같다", same(base["oof.npz"], a["oof.npz"]))
    check("시험 fold를 바꿔도 head가 같다", all(torch.equal(x, y) for x, y in zip(base["head_additive.pt"]["state_dict"].values(), a["head_additive.pt"]["state_dict"].values())))
    t = synth()
    t.y[t.mask([r["val"]])] = 1 - t.y[t.mask([r["val"]])]
    a = _tvs(t)
    check("H2 검증 fold의 정답을 바꿔도 OOF가 같다(E4, 정할 것 2)", same(base["oof.npz"], a["oof.npz"]))
    check("H2 검증 fold의 정답은 K1 head 학습에는 들어간다(D_k, O17)", not all(torch.equal(x, y) for x, y in zip(base["head_additive.pt"]["state_dict"].values(), a["head_additive.pt"]["state_dict"].values())))
    # 안쪽 겹 j의 OOF는 그 겹의 정답으로 학습하지 않는다. 선택 경로가 끼지 않게 epoch 1, 후보 1개로 본다
    one = fm.Spec(max_epochs=1, batch=16, candidates=((2, 1e-3),))
    def oof_only(x):
        return fm.nested_oof(one, x, fm.Coordinates(x.v, x.cap), x.mask(r["train"]), "cpu")[0]
    b0 = oof_only(synth())
    j = r["train"][0]
    t = synth()
    t.y[t.mask([j])] = 1 - t.y[t.mask([j])]
    b1 = oof_only(t)
    rows = np.isin(b0["video_id"], t.ids[t.mask([j])])
    check("안쪽 겹의 정답을 바꿔도 그 겹의 OOF는 같다(fold 밖 출력)", np.array_equal(b0["logit"][rows], b1["logit"][rows]))
    check("안쪽 겹의 정답을 바꾸면 다른 겹의 OOF는 달라진다", not np.array_equal(b0["logit"][~rows], b1["logit"][~rows]))


def t_chosen_epoch_used():
    """OOF는 고른 후보와 고른 epoch의 출력이다."""
    d = synth()
    coord = fm.Coordinates(d.v, d.cap)
    rows = d.mask([3, 4, 5, 6])
    oof, table, _, row = fm.nested_oof(FAST, d, coord, rows, "cpu")
    j = 3
    tr, va = rows & (d.folds != j), rows & (d.folds == j)
    m, *_ = fm.train(FAST, int(row.r), float(row.weight_decay), coord.tensors(d.v[tr], d.cap[tr], d.y[tr], "cpu"), epochs=int(row.epochs))
    lo, _ = fm.predict(FAST, m, d, coord, va, "cpu")
    keep = np.isin(oof["video_id"], d.ids[va])
    check("OOF는 고른 epoch까지 학습한 모델의 출력과 같다(O16)", np.allclose(oof["logit"][keep], lo, atol=1e-5))


def t_k1a():
    d = synth(dims=True)
    with tempfile.TemporaryDirectory() as t:
        out = Path(t)
        fm.task_k1a(fm.Spec(kind="dimensions", max_epochs=3, batch=16, candidates=((0, 1e-3), (2, 1e-3))), d, 1, "cpu", out)
        m = np.load(out / "coordinates.npz")
        p = np.load(out / "test_pred.npz")
        ok_stat = np.allclose(m["target_mean"], d.y[d.mask(c.roles(1)["dk"])].astype(np.float64).mean(0))
        ok_back = np.allclose(p["additive_score"], p["additive_z"] * m["target_std"] + m["target_mean"], atol=1e-4)
        files = {f.name for f in out.iterdir()}
        ch = json.loads((out / "chosen.json").read_text())
    check("K1a 정답은 D_k로 표준화한다(N3)", ok_stat)
    check("K1a 예측은 표준화를 되돌려 저장한다", ok_back)
    check("K1a는 더하기판과 상호작용판을 둘 다 저장한다", {"head_additive.pt", "head_interaction.pt"} <= files and ch["additive"]["r"] == 0 and ch["interaction"]["r"] > 0)
    s = fm.Spec(kind="dimensions")
    x = torch.tensor([[2.0]])
    check("K1a 출력은 sigmoid를 쓰지 않고 손실은 MSE다", s.predict(x).item() == 2.0 and abs(s.loss(x, torch.tensor([[1.0]])).item() - 1.0) < 1e-6)


def t_zones():
    split = c.load_split()
    blocks = pd.read_csv(c.S2 / "content_blocks_assignment.tsv", sep="\t")
    fold_of = dict(zip(split.video_id, split.fold))
    ok = dict(nob=True, test=True, nok=True, ctrl_has=False, same=True)
    for b in range(1, 6):
        inb = set(blocks.video_id[blocks.block == b].tolist())
        for k in range(1, 7):
            ex, te = c.zone_sets(split, b, k, "excluded")
            ct, te2 = c.zone_sets(split, b, k, "control")
            ok["nob"] &= not (set(ex) & inb)
            ok["test"] &= set(te) <= inb and {fold_of[v] for v in te} == {k} and te == te2
            ok["nok"] &= k not in {fold_of[v] for v in ex + ct}
            ok["ctrl_has"] |= bool(set(ct) & inb)
            ok["same"] &= len(ex) == len(ct)
    check("구역 제외 학습에 빠진 구역이 없다(4-3)", ok["nob"])
    check("시험 영상은 그 구역과 그 fold의 영상이다", ok["test"])
    check("어느 학습에도 시험 fold가 없다(H5)", ok["nok"])
    check("학습량 대조는 그 구역을 후보에서 빼지 않는다(정할 것 8)", ok["ctrl_has"])
    check("두 제외 방식의 영상 수가 같다(J3)", ok["same"])
    tasks = fm.enumerate_tasks("zone")
    check("구역 5 × fold 6 × 제외 방식 2 = 60개 과제다", len(tasks) == 60 and len({t["name"] for t in tasks}) == 60)


def t_task_counts():
    check("tvs, k1a, noemo는 fold마다 하나다", all(len(fm.enumerate_tasks(t)) == 6 for t in ("tvs", "k1a", "noemo")))
    parts = [t["name"] for i in range(4) for t in fm.enumerate_tasks("zone")[i::4]]
    check("나눠 돌려도 빠지거나 겹치는 과제가 없다", sorted(parts) == sorted(t["name"] for t in fm.enumerate_tasks("zone")))


def t_boundaries():
    split = c.load_split()
    mp = pd.read_csv(c.S2 / "hk_mc_id_map.tsv", sep="\t")
    mc = pd.to_numeric(mp.hk_analysis_video_ids[mp.is_mc_test_72].astype(str).str.split(",").str[0]).astype(int).tolist()
    raised = False
    try:
        c.load_rows(c.VISUAL_TARGET, np.array(mc[:3]), split)
    except ValueError:
        raised = True
    check("MC 72개의 특징은 읽지 못한다", raised)
    check("개발 영상에 MC 72개가 없다", not (set(mc) & set(split.video_id.tolist())))
    check("fold 역할이 표와 같다", c.roles(1)["val"] == 2 and c.roles(6)["val"] == 1 and c.roles(6)["train"] == [2, 3, 4, 5])
    check("6-3 모델의 검증 fold는 1이다(O7)", c.final_roles()["val"] == 1 and c.final_roles()["train"] == [2, 3, 4, 5, 6])
    for name, args in (("동결 커밋 없이는 멈춘다", ("",)), ("조상이 아닌 커밋이면 멈춘다", ("0000000000000000000000000000000000000000",))):
        stopped = False
        try:
            c.guard(*args)
        except SystemExit:
            stopped = True
        check(name, stopped)
    with tempfile.TemporaryDirectory() as t:
        p = Path(t) / "a"
        try:
            with c.Atomic(p) as tmp:
                (tmp / "x").write_text("1")
                raise RuntimeError
        except RuntimeError:
            pass
        check("도중에 실패하면 결과 폴더가 남지 않는다", not p.exists() and not list(Path(t).iterdir()))
        with c.Atomic(p) as tmp:
            (tmp / "done.json").write_text(json.dumps(dict(run_key="a")))
        check("같은 실행의 결과는 건너뛴다", c.done_or_new(p, "a"))
        check("다른 실행의 결과가 있으면 멈춘다", stops(lambda: c.done_or_new(p, "b")))
    raised = False
    try:
        c.fit_standardizer(np.ones((5, 2)))
    except ValueError:
        raised = True
    check("표준편차 0인 차원은 조용히 넘기지 않는다", raised)


def t_scores_mapping():
    split = c.load_split()
    with tempfile.TemporaryDirectory() as t:
        p = Path(t) / "labels.csv"
        cols = pd.read_csv(c.LABEL_MAP, sep="\t").score_col.tolist()
        df = pd.DataFrame({"stim_num_int": np.arange(1, 2186)})
        for i, n in enumerate(cols):
            df[n] = df.stim_num_int * 1000 + i
        for n in c.DIMENSIONS:
            df[f"{n}_score"] = df.stim_num_int + 0.5
        df.to_csv(p, index=False)
        old = c.LABELS
        c.LABELS = p
        try:
            y, _ = c.load_scores(split, "emotions")
            d, dn = c.load_scores(split, "dimensions")
        finally:
            c.LABELS = old
    check("정답은 video_id가 아니라 content_id로 붙는다", (split.video_id != split.content_id).any() and (y[:, 0] == split.content_id.to_numpy() * 1000).all())
    check("정답 34개와 차원 14개의 크기가 맞다", y.shape[1] == 34 and d.shape[1] == 14 and (d[:, 0] == split.content_id.to_numpy() + 0.5).all())


def t_ridge():
    g = torch.Generator().manual_seed(0)
    x, y, xt = torch.randn(40, 6, generator=g, dtype=torch.float64), torch.randn(40, 3, generator=g, dtype=torch.float64), torch.randn(7, 6, generator=g, dtype=torch.float64)
    lam = 10.0
    p = rg.ridge_paths(x, y, xt, [lam])[0]
    xc, yc = x - x.mean(0), y - y.mean(0)
    beta = torch.linalg.solve(xc.T @ xc + lam * torch.eye(6, dtype=torch.float64), xc.T @ yc)
    check("ridge 경로가 닫힌 해와 같다", torch.allclose(p, y.mean(0) + (xt - x.mean(0)) @ beta))
    check("λ 후보는 10^0부터 10^6까지 13개다(O18)", len(rg.LAMBDAS) == 13 and rg.LAMBDAS[0] == 1 and abs(rg.LAMBDAS[-1] - 1e6) < 1e-6 and abs(rg.LAMBDAS[1] - 10**0.5) < 1e-9)
    yy = torch.tensor([[1.0], [2.0], [3.0]], dtype=torch.float64)
    check("R²는 완벽한 예측에서 1, 평균 예측에서 0이다", abs(rg.r2_columns(yy, yy).item() - 1) < 1e-9 and abs(rg.r2_columns(yy, torch.full_like(yy, 2.0)).item()) < 1e-9)
    check("상수 목표의 R²는 계산 불가다", rg.r2_columns(torch.ones((3, 1), dtype=torch.float64), yy).isnan().all())
    n = 180
    folds = np.arange(n) % 6 + 1
    gn = np.random.default_rng(0)
    X = gn.normal(size=(n, 10))
    Y = X[:, :3] + 0.1 * gn.normal(size=(n, 3))
    xt_, yt_ = torch.as_tensor(X), torch.as_tensor(Y)
    p1, pick1 = rg._one_fold_d12(xt_, yt_, folds, 1, "cpu")
    x2, y2 = X.copy(), Y.copy()
    x2[folds == 1] += 100
    y2[folds == 1] -= 100
    _, pick2 = rg._one_fold_d12(torch.as_tensor(x2), torch.as_tensor(y2), folds, 1, "cpu")
    check("D12의 λ 선택에 시험 fold가 들어가지 않는다", pick1 == pick2)
    pred, ch = rg.emotion_ridge(X.astype(np.float32), Y.astype(np.float32), folds, "cpu")
    check("정서 ridge는 정서마다 λ를 고른다(O18)", ch[1].shape == (3,) and pred.shape == Y.shape and (c.pearson(Y, pred) > 0.8).all())
    Y2 = Y.copy()
    Y2[folds == 1] = 1 - Y2[folds == 1]
    pred2, _ = rg.emotion_ridge(X.astype(np.float32), Y2.astype(np.float32), folds, "cpu")
    check("정서 ridge의 시험 예측은 그 fold의 정답을 쓰지 않는다", np.allclose(pred[folds == 1], pred2[folds == 1]))


def t_window():
    a = np.array([[1.0, 0.0]])
    b = np.array([[0.0, 1.0]])
    check("코사인 거리: 직교 1, 같으면 0", abs(wc.cosine_distance(a, b)[0] - 1) < 1e-9 and abs(wc.cosine_distance(a, a)[0]) < 1e-9)
    g = np.random.default_rng(0)
    blocks = g.normal(size=(30, 40, 16))
    ids = np.arange(1, 31)
    win = np.stack([blocks[4], blocks[4]])
    t = wc.compute({5: win}, blocks, ids)
    check("창이 모두 같으면 창 사이 거리는 0이다", (t.within.abs() < 1e-9).all())
    check("목표 block 네 개마다 값을 낸다", sorted(t.block) == [10, 20, 30, 40] and (t.other_video > 0).all())


def _small_results(out):
    split = pd.DataFrame(dict(video_id=np.arange(1, 121), content_id=np.arange(1, 121), fold=np.arange(120) % 6 + 1))
    d, dd = synth(), synth(dims=True)
    run = c.Run(None, [])
    k1 = fm.Spec(kind="dimensions", max_epochs=2, batch=16, candidates=((0, 1e-3), (2, 1e-3)))
    for t_ in fm.enumerate_tasks("tvs"):
        fm.run_one(t_, FAST, d, split, "cpu", out / "tvs" / t_["name"], run)
    for t_ in fm.enumerate_tasks("k1a"):
        fm.run_one(t_, k1, dd, split, "cpu", out / "k1a" / t_["name"], run)
    return split, d, run


def t_end_to_end():
    with tempfile.TemporaryDirectory() as t:
        out = Path(t)
        split, d, run = _small_results(out)
        tasks = ("tvs", "k1a")
        col.check_folds(split, out, tasks)
        sel = col.selection_table(out)
        check("fold별 epoch, r, weight decay의 표가 있다", len(sel) == 6 * (4 + 2) and {"r", "weight_decay", "epochs"} <= set(sel.columns))
        folds = col.expected_tests(split, "tvs")
        r, n = col.pooled(out, "tvs", folds, d.y, d.ids, "p")
        check("fold를 모으면 모든 영상의 예측이 쓰인다", n == 120 and len(r) == 3)
        f1 = out / "tvs" / "fold1" / "test_pred.npz"
        ok = dict(np.load(f1))
        ok_ids = ok["video_id"]
        def damaged(**kw):
            np.savez(f1, **dict(ok, **kw))
        damaged(video_id=np.array([2]), logit=np.zeros((1, 3)), p=np.zeros((1, 3)))
        check("시험 예측이 시험 fold 밖이면 점검이 멈춘다", stops(lambda: col.check_folds(split, out, tasks)))
        damaged(video_id=ok_ids[:-1], logit=ok["logit"][:-1], p=ok["p"][:-1])
        check("시험 영상이 빠지면 점검이 멈춘다(Codex 3)", stops(lambda: col.check_folds(split, out, tasks)))
        check("시험 영상이 빠지면 r도 내지 않는다(Codex 3)", stops(lambda: col.pooled(out, "tvs", folds, d.y, d.ids, "p")))
        two = np.r_[ok_ids, ok_ids[:1]]
        damaged(video_id=two, logit=np.r_[ok["logit"], ok["logit"][:1]], p=np.r_[ok["p"], ok["p"][:1]])
        check("같은 영상이 두 번 있으면 점검이 멈춘다(Codex 3)", stops(lambda: col.check_folds(split, out, tasks)))
        damaged(p=ok["p"][:-1])
        check("값의 행 수가 영상 수와 다르면 멈춘다(Codex 3)", stops(lambda: col.check_folds(split, out, tasks)))
        bad = ok["p"].copy()
        bad[0, 0] = np.nan
        damaged(p=bad)
        check("시험 예측에 NaN이 있으면 멈춘다(Codex 2)", stops(lambda: col.check_folds(split, out, tasks)))
        np.savez(f1, **ok)
        f2 = out / "tvs" / "fold1" / "oof.npz"
        oo = dict(np.load(f2))
        for key, val in (("p_raw", np.nan), ("logit", np.inf)):
            x = oo[key].copy()
            x[0, 0] = val
            np.savez(f2, **dict(oo, **{key: x}))
            check(f"OOF의 {key}가 깨지면 멈춘다(Codex 2)", stops(lambda: col.check_folds(split, out, tasks)))
        np.savez(f2, **oo)
        col.check_folds(split, out, tasks)
        np.savez(out / "k1a" / "fold2" / "coordinates.npz", **{k: v + 1 for k, v in np.load(out / "tvs" / "fold2" / "coordinates.npz").items()})
        check("K1a 좌표가 K1 head와 다르면 점검이 멈춘다", stops(lambda: col.check_folds(split, out, tasks)))
        names = [f"tvs/fold{k}" for k in range(1, 7)]
        col.check_runs(out, names)
        dn = out / "tvs" / "fold3" / "done.json"
        j = json.loads(dn.read_text())
        j2 = json.loads(json.dumps(j))
        key = next(iter(j2["inputs"]))
        j2["inputs"][key] = "다른 해시"
        dn.write_text(json.dumps(j2))
        check("입력 내용이 다른 결과가 섞이면 멈춘다(Codex 1)", stops(lambda: col.check_runs(out, names)))
        j2 = dict(j, design_freeze="abc")
        dn.write_text(json.dumps(j2))
        check("동결 커밋이 다른 결과가 섞이면 멈춘다", stops(lambda: col.check_runs(out, names)))
        dn.write_text(json.dumps(j))
        check("지금 파일이 결과를 만들 때와 다르면 멈춘다", stops(lambda: col.check_runs(out, names, current=lambda p: "다른 해시")))
    blocks = pd.DataFrame(dict(video_id=[1, 2, 7, 13], block=[1, 1, 2, 1]))
    split = pd.DataFrame(dict(video_id=np.arange(1, 121), fold=np.arange(120) % 6 + 1))
    z = col.expected_tests(split, "zone", blocks)
    check("구역 시험의 기대 목록은 그 구역과 그 fold의 영상이다", z["block1_fold1_excluded"] == [1, 13] and z["block1_fold1_control"] == [1, 13] and z["block2_fold1_excluded"] == [7] and z["block1_fold2_excluded"] == [2])


def t_inputs():
    """Codex 1. 입력이 바뀌면 재사용하지 않고, 계산 중 바뀌면 저장하지 않는다."""
    with tempfile.TemporaryDirectory() as t:
        out = Path(t)
        f = out / "feature.npy"
        np.save(f, np.zeros(3))
        split = pd.DataFrame(dict(video_id=np.arange(1, 121), content_id=np.arange(1, 121), fold=np.arange(120) % 6 + 1))
        d = synth()
        run = c.Run(None, [f], task="tvs")
        task = fm.enumerate_tasks("tvs")[0]
        fm.run_one(task, FAST, d, split, "cpu", out / "r", run)
        before = dict(np.load(out / "r" / "test_pred.npz"))
        fm.run_one(task, FAST, d, split, "cpu", out / "r", run)
        check("같은 입력이면 끝난 결과를 건너뛴다", same(before, np.load(out / "r" / "test_pred.npz")))
        np.save(f, np.ones(3))
        run2 = c.Run(None, [f], task="tvs")
        check("입력 내용이 다르면 실행 번호가 다르다", run.key != run2.key)
        check("입력이 바뀐 뒤 같은 폴더로 돌리면 옛 결과를 쓰지 않고 멈춘다(Codex 1)", stops(lambda: fm.run_one(task, FAST, d, split, "cpu", out / "r", run2)))
        check("설정이 다르면 실행 번호가 다르다", c.Run(None, [f], task="tvs").key != c.Run(None, [f], task="k1a").key)
        check("동결 커밋이 다르면 실행 번호가 다르다", c.Run("a", [f]).key != c.Run("b", [f]).key)
        run3 = c.Run(None, [f], task="tvs")
        np.save(f, np.zeros(3))
        check("읽은 뒤 입력이 바뀌면 멈춘다(Codex 1)", stops(run3.check))
        orig = fm.task_tvs
        run4 = c.Run(None, [f], task="tvs")
        def change_during(*a):
            np.save(f, np.full(3, 7.0))
            return orig(*a)
        fm.task_tvs = change_during
        try:
            check("계산 중 입력이 바뀌면 저장하지 않는다(Codex 1)", stops(lambda: fm.run_one(task, FAST, d, split, "cpu", out / "s", run4)) and not (out / "s").exists())
        finally:
            fm.task_tvs = orig
        check("실행 번호에 S2 표가 들어간다", all(str(p) in c.Run(None, []).hashes for p in c.S2_TABLES))
    check("특징 모델의 입력 목록이 과제와 맞다", "deberta_no_emotion_words" in str(fm.input_paths("noemo")[1]) and "deberta/target" in str(fm.input_paths("tvs")[1]) and c.LABELS in fm.input_paths("k1a"))
    check("ridge의 입력 목록이 과제와 맞다", c.LABELS not in rg.input_paths("d12") and c.LABELS in rg.input_paths("noemo"))


def t_nonfinite():
    """Codex 2. 계산 실패를 정상 값으로 바꾸지 않는다."""
    y = torch.tensor([[0.0], [1.0], [2.0]])
    keep = y.amax(0) > y.amin(0)
    check("NaN 예측은 선택 점수 0이 아니라 오류다", stops(lambda: fm._r_selection(torch.full((3, 1), float("nan")), y, keep)))
    check("정답이 모두 상수이면 점수를 내지 않는다", stops(lambda: fm._r_selection(torch.ones((3, 1)), torch.ones((3, 1)), torch.tensor([False]))))
    t = pd.DataFrame([(0, 1e-3, 5, np.nan), (2, 1e-3, 5, 0.8)], columns=["r", "weight_decay", "epochs", "val_r"])
    check("점수가 NaN인 후보가 있으면 첫 후보를 고르지 않고 멈춘다", stops(lambda: fm.choose(t)))
    check("표준화 입력의 NaN은 통과시키지 않는다", stops(lambda: c.fit_standardizer(np.array([[1.0], [np.nan]]))))
    d = synth()
    d.cap[3, 1] = np.nan
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        check("특징에 NaN이 있으면 완료로 저장하지 않는다", stops(lambda: fm.run_one(fm.enumerate_tasks("noemo")[0], FAST, d, pd.DataFrame(dict(video_id=d.ids)), "cpu", out / "x", c.Run(None, []))) and not (out / "x").exists())
    d = synth()
    d.v[d.mask([1])] = np.inf
    coord = fm.Coordinates(d.v[~d.mask([1])], d.cap[~d.mask([1])])
    check("시험 fold 입력의 Inf도 통과시키지 않는다", stops(lambda: coord.tensors(d.v, d.cap, d.y, "cpu")))
    x = torch.ones((4, 2), dtype=torch.float64)
    x[0, 0] = float("nan")
    check("ridge 입력의 NaN이 조용히 넘어가지 않는다", stops(lambda: rg.ridge_paths(x, torch.ones((4, 1), dtype=torch.float64), torch.ones((1, 2), dtype=torch.float64), [1.0]), errors=(ValueError, RuntimeError, torch.linalg.LinAlgError)))
    n = 60
    folds = np.arange(n) % 6 + 1
    X, Y = np.random.default_rng(0).normal(size=(n, 4)).astype(np.float32), np.ones((n, 2), np.float32)
    check("정답이 모든 겹에서 상수인 정서는 λ를 고르지 않고 멈춘다", stops(lambda: rg.emotion_ridge(X, Y, folds, "cpu")))
    X2 = X.copy()
    X2[0, 0] = np.nan
    check("정서 ridge 입력의 NaN은 통과시키지 않는다", stops(lambda: rg.emotion_ridge(X2, np.random.default_rng(1).random((n, 2)).astype(np.float32), folds, "cpu")))


def t_window_zero():
    """Codex 보완 2. 영벡터는 계산 불가로 세고 값을 만들지 않는다."""
    blocks = np.tile(np.array([-1.0, 0.0, 1.0])[:, None, None], (1, 40, 4))
    per = np.stack([-np.ones((40, 4)), np.ones((40, 4))])
    t = wc.compute({2: per}, blocks, np.arange(1, 4))
    s = wc.summarize(t)
    check("영벡터인 영상은 계산 불가로 센다", t.ratio.isna().all() and (s.n_not_computable == 1).all() and (s.n_valid == 0).all())


def main():
    for f in (t_model, t_candidates, t_r_selection, t_search_rule, t_reproducible, t_leak, t_chosen_epoch_used, t_k1a, t_zones, t_task_counts, t_boundaries, t_scores_mapping, t_ridge, t_window, t_inputs, t_nonfinite, t_window_zero, t_end_to_end):
        f()
    bad = [n for n, ok in RESULTS if not ok]
    print("통과", len(RESULTS) - len(bad), "실패", len(bad), bad)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
