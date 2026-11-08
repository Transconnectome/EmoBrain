#!/usr/bin/env python3
"""S6 합성 자료 시험 (04 S6의 확인 기준, 2026-11-07). 실제 정답과 실제 뇌 반응은 읽지 않는다. 표(S2 manifest, ROI 표)만 쓴다.
사용: s6_tests.py        단위 시험 전체
      s6_tests.py --timing  실제 voxel 수의 합성 입력으로 CPU 학습 한 step의 시간과 메모리 어림(d = 64는 어림용 값이고 후보가 아니다)
"""
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1] / "src"))  # 코드는 src에 있다
import inspect
import json
import re
import os
import resource
import sys
import tempfile
import time
from pathlib import Path

os.environ["S6_OUT"] = tempfile.mkdtemp(prefix="s6_tests_")
import numpy as np
import pandas as pd
import torch
from torch.nn import functional as F

import s4_common as c
import s4_feature_model as fm
import s5_common as d5
import s6_common as S
import s6_model as M
import s6_train as T
from s6_model import ac

RESULTS = []
FAST = S.Spec(batch=16, max_epochs=3, patience=30)
KS = ((8, 1e-3), (12, 1e-2))
ROI_SIZES = (6, 5, 9, 4, 7)
FIRST_ID = 3001  # MC 표의 번호(최대 2,196)와 겹치지 않는 합성 영상 번호


def check(name, ok):
    RESULTS.append((name, bool(ok)))
    print("통과" if ok else "실패", name, flush=True)


def stops(f, errors=(SystemExit, ValueError)):
    try:
        f()
    except errors:
        return True
    return False


class World:
    """합성 자료. 영상 n개, 참가자 5명, ROI 5개(겹치는 voxel 있음). 한 사람은 영상 하나를 보지 않았다."""

    def __init__(self, n=48, seed=0):
        g = np.random.default_rng(seed)
        self.n = n
        self.split = pd.DataFrame(dict(video_id=np.arange(FIRST_ID, FIRST_ID + n), fold=np.arange(n) % 6 + 1))
        latent = g.normal(size=(n, 6))
        self.y = (1 / (1 + np.exp(-(latent @ g.normal(size=(6, 34)))))).astype(np.float32)
        self.v = (latent @ g.normal(size=(6, M.VISUAL_DIM)) + g.normal(size=(n, M.VISUAL_DIM))).astype(np.float32)
        self.cap = (latent @ g.normal(size=(6, M.CAPTION_DIM)) + g.normal(size=(n, M.CAPTION_DIM))).astype(np.float32)
        self.brains = {}
        for p in range(5):
            voxels = 20 + p
            X = (latent @ g.normal(size=(6, voxels)) + g.normal(size=(n, voxels))).astype(np.float32)
            order = g.permutation(n)[: n - (1 if p == 4 else 0)]
            pos, start = [], 0
            for size in ROI_SIZES:
                pos.append(np.arange(start, min(start + size, voxels)))
                start = max(0, start + size - 2) % voxels  # 이웃 ROI와 겹치게 한다
            pid = f"sub-0{p + 1}"
            self.brains[pid] = d5.BrainSet(pid, X[order], self.split.video_id.to_numpy()[order], self.split.fold.to_numpy()[order], pos, sum(len(x) for x in pos))
        self.g = g

    def plan(self, k=1):
        return S.plan_outer(self.split, k)

    def stimulus(self, plan, seed=1):
        g = np.random.default_rng(seed)
        return dict(video_id=np.array(plan.train), p_clipped=g.uniform(0.05, 0.95, size=(len(plan.train), 34)).astype(np.float32))

    def fold(self, k=1, **kw):
        plan = self.plan(k)
        kw.setdefault("stimulus", self.stimulus(plan))
        return S.prepare_fold(self.brains, self.split, self.y, self.v, self.cap, plan, **kw)


def run_for(root, **settings):
    f = Path(root) / "input.bin"
    if not f.exists():
        f.write_bytes(b"synthetic")
    return S.Run(None, {"synthetic": f}, **settings)


def small_model(fd, condition, **cand):
    base = dict(d=8, input_wd=1e-3, lr=1e-3, lam=None, alpha=None, rank=None, feature_wd=None) | cand
    torch.manual_seed(0)
    return S.build_model(condition, base, fd.voxel_counts), base


def t_audition():
    """지침(CLAUDE_EmoBrain 5절): audition_codex의 방어 조건과 검증 함수를 이 구현에 통과시킨다."""
    tests = (ac.verify_readout_and_loss, ac.verify_gradient_routes, ac.verify_swap_algebra, ac.verify_length_matching_and_undefined_cases, ac.verify_control_and_fold_aggregation, ac.verify_shuffle_and_application)
    original = ac.DecodedFeatureReadout
    for label, cls in (("원본", original), ("S6 구현", M.AuditionReadout)):
        ac.DecodedFeatureReadout = cls
        try:
            for f in tests:
                with torch.random.fork_rng(devices=[]):
                    f()
                check(f"audition_codex {f.__name__} ({label})", True)
        except Exception as e:  # 실패를 그대로 적는다
            check(f"audition_codex {label}: {type(e).__name__} {e}", False)
        finally:
            ac.DecodedFeatureReadout = original


def t_structure():
    w = World()
    fd = w.fold()
    rows = fd.rows("train")[:12]
    for name in ("brain_only", "brain_only_distill", "control_label_smoothing", "control_stimulus_shuffle", "brain_only_repr_frozen", "brain_only_repr_trained"):
        m, _ = small_model(fd, name)
        check(f"{name}에는 feature head가 없다", not m.readout.has_feature_head and not hasattr(m.readout, "a"))
    m, _ = small_model(fd, "brain_decoded", rank=2)
    m.eval()
    o = m(fd.batch(rows))
    check("출력 크기: 34개 정서, 5,632, 4,096", o.z.shape == (12, 34) and o.v_hat.shape == (12, 5632) and o.c_hat.shape == (12, 4096))
    check("attention 크기: head 4, query, ROI token", o.emotion_attention.shape == (12, 4, 34, 5) and o.feature_attention.shape == (12, 4, 2, 5))
    check("query끼리 self-attention이 없고 FFN이 없다(F4, O26)", not any("linear1" in n for n, _ in m.readout.named_parameters()))
    enc = m.encoder.block
    check("encoder는 pre-LN, head 4, FFN 2d, GELU, dropout 0.1, 마지막 LayerNorm(F3, O26)", enc.norm_first and enc.self_attn.num_heads == 4 and enc.linear1.out_features == 16 and enc.activation is F.gelu and enc.dropout.p == 0.1 and isinstance(m.encoder.final_norm, torch.nn.LayerNorm))
    check("a, b는 편향이 있고 A, B, U는 편향이 없다(O5)", m.readout.a.bias is not None and m.readout.b.bias is not None and m.readout.A.bias is None and m.readout.B.bias is None and m.readout.U.bias is None)
    check("d가 4의 배수가 아니면 멈춘다", stops(lambda: M.BrainModel(fd.voxel_counts, 6)))
    check("참가자마다 ROI 수가 다르면 멈춘다", stops(lambda: M.RoiInput(dict(a=[2, 3], b=[2]), 8)))
    check("빈 ROI가 있으면 멈춘다(C6)", stops(lambda: M.RoiInput(dict(a=[2, 0]), 8)))
    check("rank 3은 없다", stops(lambda: M.Readout(8, feature_head=True, decoded=True, rank=3)))
    check("decoded 없이 rank를 주면 멈춘다", stops(lambda: M.Readout(8, feature_head=True, rank=2)))
    # ROI token은 그 ROI의 voxel만으로 만든다
    inp = M.RoiInput(dict(a=[3, 2, 4]), 8)
    x = torch.randn(4, 9)
    t0 = inp.token("a", x)
    x2 = x.clone()
    x2[:, 3:5] += 1.0
    t1 = inp.token("a", x2)
    check("ROI token은 그 ROI의 voxel만 받는다(5-5)", torch.equal(t0[:, 0], t1[:, 0]) and torch.equal(t0[:, 2], t1[:, 2]) and not torch.equal(t0[:, 1], t1[:, 1]))
    manual = x[:, :3] @ inp.weights["a"][:3] + inp.input_bias["a"][0] + inp.roi_embedding[0]
    check("t = W x + b + e(C4)", torch.allclose(t0[:, 0], manual))
    inp.zero_grad()
    inp.token("a", x)[:, 1].sum().backward()
    g = inp.weights["a"].grad
    check("ROI token의 기울기는 그 ROI의 W에만 간다", g[3:5].abs().sum() > 0 and g[:3].abs().sum() == 0 and g[5:].abs().sum() == 0)
    # 묶음의 행 순서를 지킨다
    m.eval()
    whole = T.collect(m, fd.rows("test"), T.brain_forward(fd), 64)["z"]
    pieces = T.collect(m, fd.rows("test"), T.brain_forward(fd), 3)["z"]
    check("묶음 크기가 달라도 행 순서와 값이 같다", torch.allclose(whole, pieces, atol=1e-5))
    b = fd.batch(fd.rows("test"))
    check("참가자가 섞인 묶음에서 행 위치가 맞다", b.n == len(fd.rows("test")) and sum(len(v) for v in b.positions.values()) == b.n)
    one = T.brain_forward(fd)(m, fd.rows("test")[:1]).z
    check("한 행씩 넣어도 같은 값이다", torch.allclose(one[0], whole[0], atol=1e-5))


def t_stop_gradient():
    w = World()
    fd = w.fold()
    rows = fd.rows("train")[:16]
    for name, kw in (("brain_decoded", dict(rank=2, lam=0.1)), ("brain_decoded_additive", dict(rank=0, lam=1.0)), ("brain_decoded_distill", dict(rank=4, lam=0.1, alpha=0.5)), ("brain_decoded_pool", dict(rank=2, lam=0.1))):
        m, cand = small_model(fd, name, **kw)
        m.eval()  # dropout을 꺼 기울기를 정확히 비교한다
        out = m(fd.batch(rows))
        cfg = S.CONDITIONS[name]
        target = fd.train_target(rows, cfg.target if cfg.target == "stimulus" else "human", cand["alpha"])
        T.soft_bce(out.z, target).backward()
        feature_none = all(p.grad is None or not p.grad.any() for p in m.readout.feature_head.parameters())
        check(f"{name}: 정서 손실의 기울기가 feature head로 가지 않는다(G8)", feature_none)
        check(f"{name}: 정서 손실의 기울기가 ROI 경로로 encoder와 입력층까지 간다", all(p.grad is not None and p.grad.abs().sum() > 0 for p in m.encoder.parameters()) and all(m.input_layer.weights[p].grad.abs().sum() > 0 for p in fd.batch(rows).xs))
        check(f"{name}: 정서 손실이 a, b를 학습시킨다", m.readout.a.weight.grad.abs().sum() > 0 and m.readout.b.weight.grad.abs().sum() > 0)
        m.zero_grad(set_to_none=True)
        out = m(fd.batch(rows))
        v, cap = fd.feature_targets(rows)
        L_feat = (F.mse_loss(out.v_hat, v) + F.mse_loss(out.c_hat, cap)) / 2
        L_feat.backward()
        only_feat = {n: p.grad.clone() for n, p in m.readout.feature_head.named_parameters()}
        check(f"{name}: feature 손실은 feature head와 encoder로 간다", all(g.abs().sum() > 0 for g in only_feat.values()) and all(p.grad.abs().sum() > 0 for p in m.encoder.parameters()))
        check(f"{name}: feature 손실은 a, b로 가지 않는다", m.readout.a.weight.grad is None and m.readout.b.weight.grad is None)
        m.zero_grad(set_to_none=True)
        T.make_loss(name, cand, fd)(m(fd.batch(rows)), rows).backward()
        check(f"{name}: 전체 손실에서 feature head 기울기는 λ × feature 손실의 기울기뿐이다", all(torch.allclose(p.grad, cand["lam"] * only_feat[n], rtol=1e-4, atol=1e-7) for n, p in m.readout.feature_head.named_parameters()))
    m, _ = small_model(fd, "brain_decoded", rank=2)
    m.eval()
    H = m.encode(fd.batch(rows))
    before = m.readout(H).z.detach().clone()
    with torch.no_grad():
        m.readout.feature_head.visual.weight.add_(0.5)
    check("stop-gradient는 값을 막지 않는다. v̂가 바뀌면 z가 바뀐다", not torch.allclose(m.readout(H).z, before))


def t_gradient_allowed():
    """G8 허용판(11/8 석진 님). 구조와 후보는 조건 3과 같고, 정서 손실의 기울기가 feature head까지 간다는 것만 다르다."""
    w = World()
    fd = w.fold()
    rows = fd.rows("train")[:16]
    m, cand = small_model(fd, "brain_decoded_grad", rank=2, lam=0.1)
    m.eval()
    T.soft_bce(m(fd.batch(rows)).z, fd.train_target(rows, "human", None)).backward()
    check("brain_decoded_grad: 정서 손실의 기울기가 feature head로 간다", any(p.grad is not None and p.grad.abs().sum() > 0 for p in m.readout.feature_head.parameters()))
    torch.manual_seed(0)
    a = S.build_model("brain_decoded", cand, fd.voxel_counts)
    torch.manual_seed(0)
    b = S.build_model("brain_decoded_grad", cand, fd.voxel_counts)
    a.eval(), b.eval()
    check("허용판과 조건 3은 같은 가중치에서 같은 출력을 낸다(기울기만 다르다)", torch.equal(a(fd.batch(rows)).z, b(fd.batch(rows)).z))
    check("허용판의 후보는 조건 3과 같다", S.candidates("brain_decoded_grad", base=dict(d=8, input_wd=0.0, lr=1e-3)) == S.candidates("brain_decoded", base=dict(d=8, input_wd=0.0, lr=1e-3)))
    check("허용판은 내용 구역 제외 분할에서 돌리지 않는다", "brain_decoded_grad" not in S.ZONE_CONDITIONS)
    check("기울기 허용은 decoded 조건에만 있다", stops(lambda: M.Readout(8, stop_gradient=False)))
    check("허용판 밖의 모든 조건은 stop-gradient다", all(c.stop_gradient for n, c in S.CONDITIONS.items() if n != "brain_decoded_grad"))


def t_s6_rules_1108():
    """11/8 석진 님 결정. learning rate 후보, 발산한 후보 건너뛰기, 값이 변하지 않는 voxel."""
    check("learning rate 후보는 1e-5, 1e-4, 1e-3이다", S.LEARNING_RATES == (1e-5, 1e-4, 1e-3))
    check("1e-2는 후보로 줄 수 없다", stops(lambda: S._check_lrs((1e-3, 1e-2))))
    base = dict(d=8, input_wd=0.0, lr=1e-3, lam=None, alpha=None, rank=None, feature_wd=None)
    r = lambda **kw: dict(base, candidate_id="x", val_score=0.5, val_loss=0.7, best_epoch=3, source_condition=None, source_id=None, diverged=False) | kw
    check("발산한 후보는 고르지 않는다", S.select_best([r(lr=1e-3, val_score=float("nan"), diverged=True), r(lr=1e-4, val_score=0.2)])["lr"] == 1e-4)
    check("모든 후보가 발산하면 멈춘다", stops(lambda: S.select_best([r(val_score=float("nan"), diverged=True)])))
    check("발산 표시가 없는 NaN 점수는 여전히 멈춘다", stops(lambda: S.select_best([r(val_score=float("nan")), r(lr=1e-4)])))
    # 값이 변하지 않는 voxel
    w = World()
    pid = "sub-01"
    b = w.brains[pid]
    X = np.array(b.X, copy=True)
    plan = w.plan(1)
    role_train = np.isin(b.video_id, plan.train)
    X[role_train, 3] = 2.5  # 학습 행에서만 상수
    w.brains[pid] = d5.BrainSet(pid, X, b.video_id, b.fold, b.roi_positions, b.n_voxels_with_overlap)
    fd = w.fold()
    st = fd.voxel_stats[pid]
    check("학습 행에서 상수인 voxel을 표시한다", bool(st["constant"][3]) and int(st["constant"].sum()) == 1)
    check("그 voxel은 학습, 검증, 시험 모든 행에서 0이다", bool((fd.x[pid][:, 3] == 0).all()))
    check("다른 voxel은 그대로 표준화한다", bool((fd.x[pid][:, 4] != 0).any()))
    # 발산한 후보는 기록하고 다음 후보로 넘어간다
    with tempfile.TemporaryDirectory() as td:
        real_fit = T.fit
        def fake_fit(model, fd_, spec, **kw):
            if kw["lr"] == 1e-3:
                raise T.Diverged("epoch 1: 합성 발산")
            return real_fit(model, fd_, spec, **kw)
        T.fit = fake_fit
        try:
            w2, fd2, run2, runner = pipeline(Path(td), conditions=["brain_only"])
            sel = runner.selected("brain_only")
            dirs = list((Path(td) / "outer_fold1" / "brain_only").glob("*_seed0"))
            div = [json.loads((d / "done.json").read_text()) for d in dirs]
            check("발산한 후보의 기록이 남는다", any(x.get("diverged") for x in div))
            check("발산한 후보에는 모델 파일이 없다", all(not (d / "model.pt").exists() for d, x in zip(dirs, div) if x.get("diverged")))
            check("발산하지 않은 후보에서 고른다", sel["candidate"]["lr"] == 1e-4)
            check("선택표에 발산 표시가 있다", any(row.get("diverged") for row in sel["rows"]))
            sel_dir = Path(td) / "outer_fold1" / sel["seeds"]["0"]
            def always(model, fd_, spec, **kw):
                raise T.Diverged("합성 발산")
            T.fit = always
            cand = sel["candidate"]
            check("고른 설정의 seed 1이 발산하면 멈춘다", stops(lambda: runner.train_one("brain_only", cand, 7), (ValueError,)))
        finally:
            T.fit = real_fit


def t_numeric_divergence():
    """Codex 0a36925 필수 1. 실제 forward, backward에서 생긴 비유한 값도 Diverged가 된다. shape 오류는 그대로 난다."""
    w = World()
    fd = w.fold()
    m, cand = small_model(fd, "brain_decoded", rank=2, lam=0.1)
    real_step = torch.optim.AdamW.step
    def poisoned(self, *a, **k):
        out = real_step(self, *a, **k)
        with torch.no_grad():
            m.input_layer.roi_embedding.fill_(float("inf"))
        return out
    torch.optim.AdamW.step = poisoned
    try:
        loss_fn = T.make_loss("brain_decoded", cand, fd)
        check("가중치가 Inf가 되면 Diverged다", stops(lambda: T.fit(m, fd, FAST, lr=1e-3, input_wd=1e-3, feature_wd=None, loss_fn=loss_fn, forward=T.brain_forward(fd), seed=0), (T.Diverged,)))
    finally:
        torch.optim.AdamW.step = real_step
    m2, _ = small_model(fd, "brain_decoded", rank=2, lam=0.1)
    hook = m2.readout.feature_head.register_forward_hook(lambda mod, inp, out: (out[0] * float("nan"), out[1], out[2]))
    check("forward의 v_hat이 NaN이면 Diverged다", stops(lambda: T.fit(m2, fd, FAST, lr=1e-3, input_wd=1e-3, feature_wd=None, loss_fn=T.make_loss("brain_decoded", cand, fd), forward=T.brain_forward(fd), seed=0), (T.Diverged,)))
    hook.remove()
    m3, _ = small_model(fd, "brain_decoded", rank=2, lam=0.1)
    m3.input_layer.weights["sub-01"].register_hook(lambda g: g * float("inf"))
    check("기울기가 Inf이면 가중치를 바꾸기 전에 Diverged다", stops(lambda: T.fit(m3, fd, FAST, lr=1e-3, input_wd=1e-3, feature_wd=None, loss_fn=T.make_loss("brain_decoded", cand, fd), forward=T.brain_forward(fd), seed=0), (T.Diverged,)))
    try:
        T.numeric(lambda: M.ac._tensor(torch.zeros(2, 3), "x", (2, 4)), "시험")
        kind = None
    except Exception as e:  # noqa: BLE001
        kind = type(e)
    check("shape 오류는 Diverged로 바꾸지 않는다", kind is ValueError)
    check("NaN 검사 문구는 Diverged로 바꾼다", stops(lambda: T.numeric(lambda: M.ac._tensor(torch.full((2, 4), float("nan")), "x", (2, 4)), "시험"), (T.Diverged,)))


def t_prelim_config():
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "c.json"
        f.write_text(json.dumps(dict(k_candidates=[[64, 0.01]], learning_rates=[1e-4], seeds=[0])))
        cfg = S.load_config(f)
        check("예비 설정은 seed를 줄일 수 있다", cfg.seeds == (0,) and S.Spec(seeds=cfg.seeds).seeds == (0,))
        f.write_text(json.dumps(dict(k_candidates=[[64, 0.01]], seeds=[1])))
        check("seed 0 없이 줄일 수 없다", stops(lambda: S.load_config(f)))
    check("발표용 예비 설정 파일을 읽는다", S.load_config(S.CONFIGS / "run_config_prelim_20261108.json").seeds == (0,))


def t_featdec_independent():
    w = World()
    fd = w.fold()
    rows = fd.rows("val")
    m, cand = small_model(fd, "brain_only_featdec", lam=0.1)
    m.eval()
    before = m(fd.batch(rows)).z.detach().clone()
    with torch.no_grad():
        for p in m.readout.feature_head.parameters():
            p.add_(1.0)
    after = m(fd.batch(rows))
    check("조건 2: 값을 바꿔도 Emotion이 그대로다(5-A)", torch.equal(after.z, before))
    check("조건 2: z = g(H)", torch.equal(after.z, after.g))
    check("조건 2: Emotion 계산에 decoded features를 넣는 층이 없다", not any(hasattr(m.readout, x) for x in "abABU") and stops(lambda: m.readout.combine(after.g, after.v_hat, after.c_hat)))
    train = fd.rows("train")[:8]
    m.zero_grad(set_to_none=True)
    T.soft_bce(m(fd.batch(train)).z, fd.y(train)).backward()
    check("조건 2: 정서 손실은 feature head로 가지 않는다", all(p.grad is None for p in m.readout.feature_head.parameters()))
    m.zero_grad(set_to_none=True)
    T.make_loss("brain_only_featdec", cand, fd)(m(fd.batch(train)), train).backward()
    check("조건 2: feature 손실은 공유 encoder를 학습시킨다", all(p.grad.abs().sum() > 0 for p in m.encoder.parameters()))


def t_interaction_index():
    w = World()
    fd = w.fold()
    rows = fd.rows("test")
    pairs = (rows[:6], rows[6:12])
    for name, kw, expect in (("brain_decoded_additive", dict(rank=0), "zero"), ("brain_decoded", dict(rank=4), "nonzero"), ("brain_decoded_pool", dict(rank=2), "nonzero")):
        m, _ = small_model(fd, name, **kw)
        m.eval()
        with torch.no_grad():
            a, b = m(fd.batch(pairs[0])), m(fd.batch(pairs[1]))
            z, p, I = ac.swap_2x2(m.readout, a.g, a.v_hat, a.c_hat, b.v_hat, b.c_hat)
        if expect == "zero":
            check("더하기 head: 결합 지표 I가 수치 오차 안에서 0이다", I.abs().max() < 2e-5)
            md = m.double()
            with torch.no_grad():
                va, ca, vb, cb = (t.double() for t in (a.v_hat, a.c_hat, b.v_hat, b.c_hat))
                _, pd2, Id = ac.swap_2x2(md.readout, a.g.double(), va, ca, vb, cb)
            check("더하기 head: float64에서 I가 1e-10 안이다", Id.abs().max() < 1e-10)
            check("더하기 head여도 확률 척도의 차이는 0이 아니다(O2)", (pd2[:, 1, 1] - pd2[:, 1, 0] - pd2[:, 0, 1] + pd2[:, 0, 0]).abs().max() > 1e-6)
        else:
            check(f"{name}: 결합 지표 I가 0이 아니다(양성 대조)", I.abs().max() > 1e-6)
            check(f"{name}: I는 logit으로 계산한다", torch.allclose(I, z[:, 1, 1] - z[:, 0, 1] - z[:, 1, 0] + z[:, 0, 0], atol=1e-5))


def t_distill_formula():
    g = torch.Generator().manual_seed(1)
    z = torch.randn(50, 34, generator=g, dtype=torch.float64)
    y, t = torch.rand(50, 34, generator=g, dtype=torch.float64), torch.rand(50, 34, generator=g, dtype=torch.float64)
    for alpha in S.ALPHAS:
        one = F.binary_cross_entropy_with_logits(z, (1 - alpha) * y + alpha * t)
        two = (1 - alpha) * F.binary_cross_entropy_with_logits(z, y) + alpha * F.binary_cross_entropy_with_logits(z, t)
        check(f"distillation 두 식의 값이 같다(α = {alpha})", abs((one - two).item()) < 1e-12)
    w = World()
    fd = w.fold()
    rows = fd.rows("train")
    tt = dict(zip(fd.plan.train, w.stimulus(fd.plan)["p_clipped"]))
    pos = {v: i for i, v in enumerate(w.split.video_id)}
    expected = np.stack([0.75 * w.y[pos[int(v)]] + 0.25 * tt[int(v)] for v in fd.row_video[rows]])
    check("조건 4의 목표는 (1 − α) y + α t다", np.allclose(fd.train_target(rows, "stimulus", 0.25).numpy(), expected, atol=1e-6))
    m, cand = small_model(fd, "brain_only_distill", alpha=0.25)
    m.eval()
    out = m(fd.batch(rows[:8]))
    with torch.no_grad():
        got = T.make_loss("brain_only_distill", cand, fd)(out, rows[:8])
        y8, t8 = fd.y(rows[:8]), fd.t_bank[fd._bank_index(rows[:8])]
        by_terms = 0.75 * F.binary_cross_entropy_with_logits(out.z, y8) + 0.25 * F.binary_cross_entropy_with_logits(out.z, t8)
    check("학습 손실이 (1 − α) L_emotion + α L_distillation과 같다(5-A)", abs((got - by_terms).item()) < 1e-5)
    m, cand = small_model(fd, "brain_decoded_distill", alpha=0.5, lam=0.1, rank=2)
    m.eval()
    out = m(fd.batch(rows[:8]))
    with torch.no_grad():
        got = T.make_loss("brain_decoded_distill", cand, fd)(out, rows[:8])
        v, cap = fd.feature_targets(rows[:8])
        by_terms = 0.5 * F.binary_cross_entropy_with_logits(out.z, y8) + 0.5 * F.binary_cross_entropy_with_logits(out.z, t8) + 0.1 * (F.mse_loss(out.v_hat, v) + F.mse_loss(out.c_hat, cap)) / 2
    check("조건 5의 손실이 5-A의 식과 같다", abs((got - by_terms).item()) < 1e-4)
    ybar = fd.y(rows).mean(0)
    check("label smoothing의 평균은 학습 행에서만 낸다(G11)", torch.allclose(fd.y_train_mean, ybar, atol=1e-5))
    lsm = fd.train_target(rows[:4], "mean", 0.5)
    check("label smoothing 목표는 (1 − α) y + α ȳ다", torch.allclose(lsm, 0.5 * fd.y(rows[:4]) + 0.5 * ybar, atol=1e-5))


def trajectory(fd, condition, seed=0, **cand):
    """같은 seed로 학습하며 epoch마다 가중치 해시를 남긴다."""
    T.seed_everything(seed)
    m, cand = small_model(fd, condition, **cand)
    T.seed_everything(seed)
    digests = []
    spec = S.Spec(batch=16, max_epochs=3, patience=100)
    shuffle = None
    if condition in S.NEEDS_SHUFFLE:
        shuffle = S.shuffle_plan(WORLD_SPLIT[0], fd.plan, seed)
    res = T.fit(m, fd, spec, lr=cand["lr"], input_wd=cand["input_wd"], feature_wd=cand["feature_wd"], loss_fn=T.make_loss(condition, cand, fd, shuffle), forward=T.brain_forward(fd), seed=seed, on_epoch=lambda e, model, loss: digests.append(M.state_digest(model)))
    return digests, res, m


WORLD_SPLIT = [None]


def t_boundaries():
    w = World()
    WORLD_SPLIT[0] = w.split
    fd = w.fold()
    test, val, train = fd.rows("test"), fd.rows("val"), fd.rows("train")
    plan = fd.plan
    r = c.roles(1)
    check("fold 규칙: 바깥 1이 시험, 2가 검증, 3~6이 학습(H2)", set(w.split.fold[w.split.video_id.isin(plan.test)]) == {1} and set(w.split.fold[w.split.video_id.isin(plan.val)]) == {2} and set(w.split.fold[w.split.video_id.isin(plan.train)]) == {3, 4, 5, 6} and r["val"] == 2)
    p6 = w.plan(6)
    check("바깥 fold 6의 검증은 fold 1이다", set(w.split.fold[w.split.video_id.isin(p6.val)]) == {1} and set(w.split.fold[w.split.video_id.isin(p6.test)]) == {6})
    check("시험 영상은 bank에 없다", not set(plan.test) & set(fd.bank_ids))
    by_video = {}
    for v, role in zip(fd.row_video.tolist(), fd.row_role.tolist()):
        by_video.setdefault(v, set()).add(role)
    check("한 영상의 행은 항상 같은 쪽에 있다(H6)", all(len(x) == 1 for x in by_video.values()))
    check("시험 행의 정답은 꺼낼 수 없다", stops(lambda: fd.y(test)))
    check("시험 행의 feature는 꺼낼 수 없다", stops(lambda: fd.feature_targets(test)))
    check("시험 행에 학습 목표를 만들 수 없다", stops(lambda: fd.train_target(test, "human")))
    check("검증 행에 학습 목표를 만들 수 없다", stops(lambda: fd.train_target(val, "stimulus", 0.5)))
    check("검증 영상에는 Stimulus 예측 평정이 없다(E4)", torch.isnan(fd.t_bank[fd._bank_index(val)]).all() and not torch.isnan(fd.t_bank[fd._bank_index(train)]).any())
    bad = w.stimulus(plan)
    bad["video_id"] = np.array(plan.train[:-1] + plan.val[:1])
    check("Stimulus 예측 평정에 검증 영상이 있으면 멈춘다", stops(lambda: w.fold(stimulus=bad)))
    bad = w.stimulus(plan)
    bad["p_clipped"][0, 0] = 1.5
    check("Stimulus 예측 평정이 0~1을 벗어나면 멈춘다", stops(lambda: w.fold(stimulus=bad)))
    check("Multimodal 입력은 준비하지 않으면 시험 행에 없다", stops(lambda: fd.multimodal_inputs(test)))
    check("기본값에서 시험 feature가 메모리에 없다", fd.test_vision is None and fd.test_caption is None)
    # 시험 행의 정답과 feature를 NaN으로 넘겨도 된다(실제 실행은 읽지 않는다)
    pos = np.isin(w.split.video_id, plan.test)
    y2, v2, c2 = w.y.copy(), w.v.copy(), w.cap.copy()
    y2[pos], v2[pos], c2[pos] = np.nan, np.nan, np.nan
    fd_nan = S.prepare_fold(w.brains, w.split, y2, v2, c2, plan, stimulus=w.stimulus(plan))
    a, res_a, ma = trajectory(fd, "brain_decoded", rank=2, lam=0.1)
    b, res_b, mb = trajectory(fd_nan, "brain_decoded", rank=2, lam=0.1)
    check("시험 영상의 정답과 feature가 NaN이어도 학습이 똑같다", a == b and res_a.val_loss == res_b.val_loss)
    # 검증 영상의 정답을 바꿔도 학습 경로는 같고, 조기 종료 값만 바뀐다
    posv = np.isin(w.split.video_id, plan.val)
    for name, kw in (("brain_only", {}), ("brain_only_featdec", dict(lam=0.1)), ("brain_decoded", dict(rank=2, lam=0.1)), ("brain_only_distill", dict(alpha=0.5)), ("brain_decoded_distill", dict(rank=2, lam=0.1, alpha=0.5)), ("control_label_smoothing", dict(alpha=0.5)), ("control_stimulus_shuffle", dict(alpha=0.5)), ("control_feature_shuffle", dict(lam=0.1))):
        fd1 = w.fold()
        base, res0, _ = trajectory(fd1, name, **kw)
        y3 = w.y.copy()
        y3[posv] = 1 - y3[posv]
        v3, c3 = w.v.copy(), w.cap.copy()
        v3[posv], c3[posv] = v3[posv] + 5, c3[posv] - 5
        fd3 = S.prepare_fold(w.brains, w.split, y3, v3, c3, plan, stimulus=w.stimulus(plan))
        changed, res3, _ = trajectory(fd3, name, **kw)
        check(f"{name}: 검증 영상의 정답과 feature를 바꿔도 가중치 경로가 같다", base == changed)
        check(f"{name}: 조기 종료 값은 검증 정답으로 계산한다", res0.history.val_loss.tolist() != res3.history.val_loss.tolist())
        fd4 = S.prepare_fold(w.brains, w.split, w.y, w.v, w.cap, plan, stimulus=w.stimulus(plan, seed=9))
        changed, _, _ = trajectory(fd4, name, **kw)
        if S.CONDITIONS[name].target in ("stimulus", "stimulus_shuffled"):
            check(f"{name}: 학습 영상의 Stimulus 예측 평정을 바꾸면 경로가 바뀐다(양성 대조)", base != changed)
    # 시험, 검증 fold의 뇌 반응을 바꿔도 학습과 표준화가 같다
    brains = {}
    for pid, b0 in w.brains.items():
        X = b0.X.copy()
        X[np.isin(b0.video_id, plan.test + plan.val)] += 3.0
        brains[pid] = d5.BrainSet(pid, X, b0.video_id, b0.fold, b0.roi_positions, b0.n_voxels_with_overlap)
    fd5 = S.prepare_fold(brains, w.split, w.y, w.v, w.cap, plan, stimulus=w.stimulus(plan))
    same = all(np.array_equal(fd.voxel_stats[p]["mean"], fd5.voxel_stats[p]["mean"]) and np.array_equal(fd.voxel_stats[p]["std"], fd5.voxel_stats[p]["std"]) for p in fd.participants)
    check("시험과 검증 fold의 뇌 반응은 voxel 표준화에 들어가지 않는다", same)
    base, _, m1 = trajectory(fd, "brain_only")
    changed, _, m2 = trajectory(fd5, "brain_only")
    check("시험과 검증 fold의 뇌 반응을 바꿔도 학습 경로가 같다", base == changed)
    m1.eval(), m2.eval()
    check("시험 예측은 시험 뇌 반응을 쓴다(양성 대조)", not torch.allclose(T.collect(m1, test, T.brain_forward(fd), 16)["z"], T.collect(m2, test, T.brain_forward(fd5), 16)["z"]))
    # 겹치거나 경계를 넘는 분할
    bad_plan = S.Plan("outer_fold1", 1, plan.train, plan.val, plan.test + plan.val[:1])
    check("학습, 검증, 시험이 겹치면 멈춘다", stops(lambda: S.prepare_fold(w.brains, w.split, w.y, w.v, w.cap, bad_plan)))
    bad_plan = S.Plan("outer_fold1", 1, plan.train + [1], plan.val, plan.test)
    check("MC 72개의 영상이 있으면 멈춘다", stops(lambda: S.check_plan(bad_plan, pd.concat([w.split, pd.DataFrame(dict(video_id=[1], fold=[3]))]), None)))
    bad = {k: v for k, v in w.brains.items()}
    x0 = w.brains["sub-01"]
    bad["sub-01"] = d5.BrainSet("sub-01", x0.X, np.r_[x0.video_id[:-1], x0.video_id[0]], x0.fold, x0.roi_positions)
    check("한 영상의 행이 둘이면 멈춘다", stops(lambda: S.prepare_fold(bad, w.split, w.y, w.v, w.cap, plan)))
    # 실제 표: 정답을 읽지 않는다
    real = c.load_split()
    check("실제 표: 개발 영상에 MC 72개와 그 중복이 없다", not set(real.video_id) & set(S.mc_video_ids()))
    for k in range(1, 7):
        p = S.plan_outer(real, k)
        S.check_plan(p, real)
        if len(p.train) + len(p.val) + len(p.test) != 2109:
            check(f"실제 표: fold {k}의 영상 수", False)
    check("실제 표: 6 fold 모두 분할이 맞다", True)
    pf = S.plan_final(real)
    S.check_plan(pf, real)
    check("실제 표: HK 최종 모델은 fold 1이 검증이고 시험이 없다(O7)", set(real.fold[real.video_id.isin(pf.val)]) == {1} and pf.test == [])
    pz = S.plan_zone(real, 1, 1, "excluded")
    S.check_plan(pz, real)
    blocks = pd.read_csv(c.S2 / "content_blocks_assignment.tsv", sep="\t")
    in_block = set(blocks.video_id[blocks.block == 1])
    check("실제 표: 빠진 구역은 학습과 검증에 없다(6-2)", not (set(pz.train) | set(pz.val)) & in_block and set(pz.test) <= in_block)
    check("대조군과 조건 6, 7은 구역 제외에 돌리지 않는다", stops(lambda: S.check_conditions("zone_block1_fold1_excluded", ["control_label_smoothing"])) and stops(lambda: S.check_conditions("final_for_mc", ["brain_only_repr_frozen"])))
    pp = S.plan_pilot(real, 1)
    check("파일럿은 시험 fold를 쓰지 않는다(S7)", pp.test == [] and not set(pp.train + pp.val) & set(real.video_id[real.fold == 1]))
    fdp = S.prepare_fold(w.brains, w.split, w.y, w.v, w.cap, S.plan_pilot(w.split, 1), stimulus=w.stimulus(plan))
    check("파일럿에서는 시험 행의 뇌 반응을 메모리에 올리지 않는다", len(fdp.rows("test")) == 0 and sum(len(x) for x in fdp.x.values()) == len(fdp.rows("train")) + len(fdp.rows("val")))


def t_load_known():
    w = World()
    plan = w.plan(1)
    seen = dict(scores=[], rows=[])
    old_scores, old_rows = c.load_scores, c.load_rows

    def fake_scores(split, kind):
        seen["scores"].extend(split.video_id.tolist())
        return np.zeros((len(split), 34), np.float32), []

    def fake_rows(name, ids, split):
        seen["rows"].extend(np.asarray(ids).tolist())
        return np.zeros((len(ids), M.VISUAL_DIM if name == c.VISUAL_TARGET else M.CAPTION_DIM), np.float32)

    c.load_scores, c.load_rows = fake_scores, fake_rows
    try:
        y, v, cap = T.load_known(w.split, plan)
        check("실제 실행은 시험 영상의 사람 평정을 읽지 않는다", not set(seen["scores"]) & set(plan.test))
        check("실제 실행은 시험 영상의 feature를 읽지 않는다", not set(seen["rows"]) & set(plan.test))
        pos = np.isin(w.split.video_id, plan.test)
        check("시험 행은 NaN으로 남는다", np.isnan(y[pos]).all() and np.isnan(v[pos]).all())
        seen["scores"].clear()
        seen["rows"].clear()
        T.load_known(w.split, plan, include_test_features=True)
        check("참고용 Multimodal 때도 시험 영상의 사람 평정은 읽지 않는다", not set(seen["scores"]) & set(plan.test) and set(plan.test) <= set(seen["rows"]))
    finally:
        c.load_scores, c.load_rows = old_scores, old_rows


def t_shuffle():
    w = World()
    WORLD_SPLIT[0] = w.split
    fd = w.fold()
    plan = fd.plan
    s0 = S.shuffle_plan(w.split, plan, 0)
    mapping = dict(s0.mapping)
    check("O1: 받는 영상과 주는 영상이 모두 학습 영상이다", set(mapping) == set(mapping.values()) == set(plan.train))
    check("O1: 자기 영상으로 다시 배정되지 않는다", all(a != b for a, b in mapping.items()))
    check("O1: 후보가 달라도 같은 fold와 seed면 같은 순열이다", S.shuffle_plan(w.split, plan, 0) == s0)
    check("O1: seed가 다르면 순열이 다르다", dict(S.shuffle_plan(w.split, plan, 1).mapping) != mapping)
    check("O1: 바깥 fold가 다르면 순열이 다르다", dict(S.shuffle_plan(w.split, w.plan(3), 0).mapping) != mapping)
    rows = fd.rows("train")
    v_of = lambda r: int(fd.row_video[r])
    pos = {v: i for i, v in enumerate(fd.bank_ids)}
    target = fd.train_target(rows, "stimulus_shuffled", 0.5, s0).numpy()
    ok_own, ok_same = True, True
    first = {}
    for i, r in enumerate(rows):
        vid = v_of(r)
        expect = 0.5 * fd.y_bank[pos[vid]].numpy() + 0.5 * fd.t_bank[pos[mapping[vid]]].numpy()
        ok_own &= np.allclose(target[i], expect, atol=1e-6)
        if vid in first:
            ok_same &= np.array_equal(first[vid], target[i])
        first[vid] = target[i]
    check("Stimulus 출력 섞기: 사람 평정은 자기 영상, t는 주는 영상이다", ok_own)
    check("Stimulus 출력 섞기: 같은 영상의 5명 행은 같은 목표를 받는다", ok_same)
    check("Stimulus 출력 섞기: 검증과 시험 행에는 만들 수 없다", stops(lambda: fd.train_target(fd.rows("val"), "stimulus_shuffled", 0.5, s0)) and stops(lambda: fd.train_target(fd.rows("test"), "stimulus_shuffled", 0.5, s0)))
    row_ids = fd.row_video[rows].tolist()
    sv, sc, donors = ac.apply_shuffled_scene_pairs(s0, row_ids, fd.bank_ids, fd.vision_bank, fd.caption_bank, split="train")
    check("feature 짝 섞기: 시각과 캡션을 같은 영상에서 함께 가져온다(G12)", all(torch.equal(sv[i], fd.vision_bank[pos[d]]) and torch.equal(sc[i], fd.caption_bank[pos[d]]) for i, d in enumerate(donors)))
    per_video = {}
    for vid, d in zip(row_ids, donors):
        per_video.setdefault(vid, set()).add(d)
    check("feature 짝 섞기: 같은 영상의 행은 같은 목표다", all(len(x) == 1 for x in per_video.values()))
    check("feature 짝 섞기: 검증 영상을 학습 행으로 넣으면 멈춘다", stops(lambda: ac.apply_shuffled_scene_pairs(s0, plan.val[:2], fd.bank_ids, fd.vision_bank, fd.caption_bank, split="train")))
    uv, _, same = ac.apply_shuffled_scene_pairs(s0, plan.val[:2], fd.bank_ids, fd.vision_bank, fd.caption_bank, split="validation")
    check("feature 짝 섞기: 검증 자료는 섞지 않는다", same == tuple(plan.val[:2]) and torch.equal(uv[0], fd.vision_bank[pos[plan.val[0]]]))
    m, cand = small_model(fd, "control_feature_shuffle", lam=0.1)
    m.eval()
    batch = rows[:8]
    out = m(fd.batch(batch))
    got = T.make_loss("control_feature_shuffle", cand, fd, s0)(out, batch)
    dv, dc, _ = ac.apply_shuffled_scene_pairs(s0, fd.row_video[batch].tolist(), fd.bank_ids, fd.vision_bank, fd.caption_bank, split="train")
    expect = F.binary_cross_entropy_with_logits(out.g, fd.y(batch)) + 0.1 * (F.mse_loss(out.v_hat, dv) + F.mse_loss(out.c_hat, dc)) / 2
    check("feature 짝 섞기: 손실은 조건 2의 꼴이고 사람 평정은 그대로다", abs((got - expect).item()) < 1e-5)
    check("순열 없이 대조군을 돌리면 멈춘다", stops(lambda: T.make_loss("control_feature_shuffle", cand, fd)))
    check("구역 제외에는 순열을 만들지 않는다(G6)", stops(lambda: S.shuffle_plan(w.split, S.Plan("zone_block1_fold1_excluded", 1, plan.train, plan.val, plan.test), 0)))
    real = c.load_split()
    ps = S.shuffle_plan(real, S.plan_outer(real, 1), 0)
    mp = dict(ps.mapping)
    fold_of = dict(zip(real.video_id, real.fold))
    check("실제 표: 순열이 H2 학습 fold 안에만 있고 자기 배정이 없다", all(fold_of[a] in (3, 4, 5, 6) and fold_of[b] in (3, 4, 5, 6) and a != b for a, b in mp.items()) and not set(mp) & set(S.mc_video_ids()))


def t_standardization():
    w = World()
    fd = w.fold()
    plan = fd.plan
    ok_stats, ok_z = True, True
    for pid, b in w.brains.items():
        rows = np.isin(b.video_id, plan.train)
        m, s = b.X[rows].astype(np.float64).mean(0), b.X[rows].astype(np.float64).std(0)
        ok_stats &= np.allclose(fd.voxel_stats[pid]["mean"], m) and np.allclose(fd.voxel_stats[pid]["std"], s)
        i = fd.participants.index(pid)
        tr = fd.row_local[(fd.row_participant == i) & (fd.row_role == 0)]
        x = fd.x[pid][tr].numpy()
        ok_z &= np.allclose(x.mean(0), 0, atol=1e-5) and np.allclose(x.std(0), 1, atol=1e-5)
    check("voxel 표준화는 참가자별 학습 행의 통계다(C5, N3)", ok_stats)
    check("학습 행에서 표준화한 voxel은 평균 0, 표준편차 1이다", ok_z)
    at = np.isin(w.split.video_id, plan.train)
    check("feature 목표는 학습 영상의 차원별 통계다(D9, N3)", np.allclose(fd.feature_stats["visual_mean"], w.v[at].astype(np.float64).mean(0)) and np.allclose(fd.feature_stats["caption_std"], w.cap[at].astype(np.float64).std(0)))
    tr = [fd.bank_ids.index(v) for v in plan.train]
    vz = fd.vision_bank[tr].numpy()
    check("학습 영상의 v는 평균 0, 표준편차 1이다", np.allclose(vz.mean(0), 0, atol=1e-5) and np.allclose(vz.std(0), 1, atol=1e-5))
    x = w.brains["sub-01"]
    Xc = x.X.copy()
    Xc[:, 0] = 1.0
    bad = dict(w.brains)
    bad["sub-01"] = d5.BrainSet("sub-01", Xc, x.video_id, x.fold, x.roi_positions)
    fdc = S.prepare_fold(bad, w.split, w.y, w.v, w.cap, plan)
    check("상수인 voxel은 멈추지 않고 표시한 뒤 0으로 둔다(11/8 석진 님)", bool(fdc.voxel_stats["sub-01"]["constant"][0]) and bool((fdc.x["sub-01"][:, 0] == 0).all()))
    # K1: 학습 fold 4개의 눈금 -> 원래 척도 -> D_k 눈금
    r = c.roles(1)
    dk = np.isin(w.split.fold, r["dk"])
    coord = fm.Coordinates(w.v[dk], w.cap[dk])
    arr = coord.arrays()
    z_v, z_c = fd.vision_bank[:5].numpy(), fd.caption_bank[:5].numpy()
    hv, hc = S.to_k1_head(z_v, z_c, fd.feature_stats, arr)
    orig_v = z_v.astype(np.float64) * fd.feature_stats["visual_std"] + fd.feature_stats["visual_mean"]
    bank5 = [list(w.split.video_id).index(v) for v in fd.bank_ids[:5]]
    check("K1 변환: 원래 척도로 되돌린 값이 원래 feature와 같다(N3)", np.allclose(orig_v, w.v[bank5], atol=1e-3))
    check("K1 변환: D_k 눈금 값은 (원래 값 − D_k 평균) / D_k 표준편차다", np.allclose(hv, (w.v[bank5].astype(np.float64) - coord.vm) / coord.vs, atol=1e-3) and np.allclose(hc, (w.cap[bank5].astype(np.float64) - coord.cm) / coord.cs, atol=1e-3))
    check("K1 변환: 학습 fold 눈금과 D_k 눈금은 다르다(되돌리지 않으면 틀린다)", not np.allclose(hv, z_v, atol=1e-3))
    bad_arr = dict(arr, visual_std=np.zeros_like(coord.vs))
    check("K1 변환: 표준편차가 0이면 멈춘다", stops(lambda: S.to_k1_head(z_v, z_c, fd.feature_stats, bad_arr)))


def t_early_stop():
    w = World()
    fd = w.fold()
    m, cand = small_model(fd, "brain_only")
    old = T.validation_loss
    series = iter([1.0, 0.9, 0.5, 0.6, 0.7, 0.8, 0.1, 0.1])
    T.validation_loss = lambda z, y: next(series)
    snaps = {}
    try:
        res = T.fit(m, fd, S.Spec(batch=16, max_epochs=20, patience=3), lr=1e-3, input_wd=1e-3, feature_wd=None, loss_fn=T.make_loss("brain_only", cand, fd), forward=T.brain_forward(fd), seed=0, on_epoch=lambda e, model, loss: snaps.__setitem__(e, M.state_digest(model)))
    finally:
        T.validation_loss = old
    check("조기 종료: patience가 차면 멈춘다", res.n_epochs == 6)
    check("조기 종료: 가장 낮은 epoch를 고른다(O6)", res.best_epoch == 3 and res.val_loss == 0.5)
    check("조기 종료: 그 epoch의 가중치로 되돌린다(O6)", M.state_digest(m) == snaps[3] and snaps[6] != snaps[3])
    m, cand = small_model(fd, "brain_only")
    series = iter([0.5, 0.5, 0.5, 0.5, 0.5])
    T.validation_loss = lambda z, y: next(series)
    try:
        res = T.fit(m, fd, S.Spec(batch=16, max_epochs=5, patience=30), lr=1e-3, input_wd=1e-3, feature_wd=None, loss_fn=T.make_loss("brain_only", cand, fd), forward=T.brain_forward(fd), seed=0)
    finally:
        T.validation_loss = old
    check("조기 종료: 같은 값이면 앞선 epoch다, 최대 epoch에서 멈춘다", res.best_epoch == 1 and res.n_epochs == 5)
    m, cand = small_model(fd, "brain_only")
    T.validation_loss = lambda z, y: float("nan")
    try:
        check("검증 손실이 NaN이면 멈춘다", stops(lambda: T.fit(m, fd, FAST, lr=1e-3, input_wd=1e-3, feature_wd=None, loss_fn=T.make_loss("brain_only", cand, fd), forward=T.brain_forward(fd), seed=0)))
    finally:
        T.validation_loss = old
    m, cand = small_model(fd, "brain_only")
    check("학습 손실이 NaN이면 멈춘다", stops(lambda: T.fit(m, fd, FAST, lr=1e-3, input_wd=1e-3, feature_wd=None, loss_fn=lambda o, r: o.z.sum() * float("nan"), forward=T.brain_forward(fd), seed=0)))
    check("기본값은 G13이다", S.Spec().batch == 64 and S.Spec().max_epochs == 300 and S.Spec().patience == 30)
    a = trajectory(fd, "brain_decoded", rank=2, lam=0.1)
    b = trajectory(fd, "brain_decoded", rank=2, lam=0.1)
    z = trajectory(fd, "brain_decoded", seed=1, rank=2, lam=0.1)
    check("같은 seed는 같은 가중치를 낸다(O32)", a[0] == b[0])
    check("다른 seed는 다른 가중치를 낸다", a[0] != z[0])


def t_input_only():
    sig = list(inspect.signature(M.BrainModel.forward).parameters)
    check("BrainModel.forward의 입력은 brain 하나다", sig == ["self", "brain"])
    check("BrainBatch에는 뇌 입력만 있다", set(M.BrainBatch.__dataclass_fields__) == {"xs", "positions", "n"})
    fd = World().fold()
    m, _ = small_model(fd, "brain_decoded", rank=2)
    check("BrainModel은 텐서를 직접 받지 않는다", stops(lambda: m(torch.zeros(2, 5)), (TypeError,)))
    check("BrainModel에 feature를 함께 넘길 수 없다", stops(lambda: m(fd.batch(fd.rows("test")), torch.zeros(1)), (TypeError,)))


def t_weight_groups():
    fd = World().fold()
    all_ok, bad = True, []
    for name, cfg in S.CONDITIONS.items():
        for rank in (((0,) if cfg.additive else (1, 8)) if cfg.decoded else (None,)):
            cand = dict(d=8, rank=rank)
            m = S.build_model(name, cand, fd.voxel_counts)
            if cfg.representation == "frozen":
                for p in m.readout.emotion_linears.parameters():
                    p.requires_grad_(False)
            groups = M.parameter_groups(m, 1e-3, 3e-3, 2e-3 if cfg.multimodal else None)
            ids = [id(p) for g in groups for p in g["params"]]
            named = dict(m.named_parameters())
            trainable = {id(p) for p in named.values() if p.requires_grad}
            all_ok &= len(ids) == len(set(ids)) and set(ids) == trainable
            assign = M.parameter_assignment(m)
            norm = {id(p) for mod in m.modules() if isinstance(mod, torch.nn.LayerNorm) for p in mod.parameters(recurse=False)}
            for n, p in named.items():
                expect = "frozen" if not p.requires_grad else "no_decay" if id(p) in norm or n.startswith("input_layer.input_bias.") or n.endswith(("bias", "in_proj_bias")) else "input_weight" if n.startswith("input_layer.weights.") else "feature_token" if n in ("vision_token.weight", "caption_token.weight") else "other"
                if assign[n] != expect:
                    all_ok = False
                    bad.append((name, n, assign[n], expect))
            decays = {g["name"]: g["weight_decay"] for g in groups}
            all_ok &= decays["input_weight"] == 3e-3 and decays["other"] == 0.01 and decays["no_decay"] == 0.0 and decays.get("feature_token", 2e-3) == 2e-3
    check(f"weight decay: 모든 조건의 모든 파라미터가 정확히 한 묶음에 든다{bad[:2] if bad else ''}", all_ok)
    m = S.build_model("brain_decoded", dict(d=8, rank=2), fd.voxel_counts)
    assign = M.parameter_assignment(m)
    named = dict(m.named_parameters())
    check("묶음: 입력층 W는 후보 묶음이다", assign["input_layer.weights.sub-01"] == "input_weight")
    check("묶음: b(s, r)와 모든 bias, LayerNorm은 0이다", assign["input_layer.input_bias.sub-01"] == "no_decay" and assign["readout.a.bias"] == "no_decay" and assign["encoder.final_norm.weight"] == "no_decay" and assign["encoder.block.norm1.weight"] == "no_decay" and assign["readout.emotion_query.query_norm.weight"] == "no_decay" and assign["encoder.block.self_attn.out_proj.bias"] == "no_decay")
    check("묶음: ROI embedding, query, linear와 attention의 weight는 0.01이다", all(assign[n] == "other" for n in ("input_layer.roi_embedding", "readout.emotion_query.query", "readout.feature_head.readout.query", "readout.a.weight", "readout.A.weight", "readout.U.weight", "readout.feature_head.visual.weight", "readout.emotion_linears.0.weight", "encoder.block.linear1.weight", "encoder.block.self_attn.out_proj.weight")))
    mha = [n for n in named if "self_attn" in n or "attention" in n]
    check("묶음: attention의 입력 투영도 묶음이 정해진다", all(assign[n] in ("other", "no_decay") for n in mha) and len(mha) >= 3)
    check("이름을 모르는 파라미터는 묶음을 정하지 않고 멈춘다", stops(lambda: M.parameter_group_name("readout.new_gate", False)))
    mm = S.build_model("multimodal", dict(d=8), fd.voxel_counts)
    check("Multimodal Model은 특징 선형층 weight decay가 없으면 멈춘다(O5)", stops(lambda: M.parameter_groups(mm, 1e-3, 1e-3)))
    check("Multimodal Model의 특징 선형층 bias는 0이다", M.parameter_assignment(mm)["vision_token.bias"] == "no_decay" and M.parameter_assignment(mm)["caption_token.weight"] == "feature_token")
    # AdamW가 실제로 묶음대로 줄이는지 본다. 기울기가 0이면 weight decay만 작동한다
    lr, wd = 1e-2, 3e-1
    before = {n: p.detach().clone() for n, p in m.named_parameters()}
    opt = torch.optim.AdamW(M.parameter_groups(m, lr, wd))
    for p in m.parameters():
        p.grad = torch.zeros_like(p)
    opt.step()
    after = dict(m.named_parameters())
    ok = torch.allclose(after["input_layer.weights.sub-01"], before["input_layer.weights.sub-01"] * (1 - lr * wd), atol=1e-6)
    ok &= torch.allclose(after["input_layer.roi_embedding"], before["input_layer.roi_embedding"] * (1 - lr * 0.01), atol=1e-6)
    ok &= torch.allclose(after["readout.emotion_query.query"], before["readout.emotion_query.query"] * (1 - lr * 0.01), atol=1e-6)
    ok &= torch.equal(after["input_layer.input_bias.sub-01"], before["input_layer.input_bias.sub-01"])
    ok &= torch.equal(after["readout.a.bias"], before["readout.a.bias"]) and torch.equal(after["encoder.final_norm.weight"], before["encoder.final_norm.weight"])
    check("AdamW가 묶음의 값대로 가중치를 줄인다(기울기 0으로 확인)", ok)


def t_candidates():
    base = dict(d=8, input_wd=1e-3, lr=1e-3)
    decoded = dict(lam=0.1, rank=2)
    Ks = [(4 * (i + 1), 1e-3) for i in range(6)]
    lens = {n: len(S.candidates(n, k_candidates=Ks, base=base, decoded=decoded)) for n in S.CONDITIONS if n not in S.POOLED}
    plan = S.planned_runs(6)
    total = 0
    for n, count in lens.items():
        check(f"후보 수 + seed 2가 7-L과 같다: {n} = {count + 2}", count + 2 == plan[n])
        total += count + 2
    ladder = sum(plan[n] for n in ("brain_only", "brain_only_featdec", "brain_decoded", "brain_decoded_additive", "brain_only_distill", "brain_decoded_distill"))
    check(f"사다리는 K = 6에서 fold마다 {ladder}회, 6 fold 468회(7-L)", ladder * 6 == 468)
    controls = sum(plan[n] for n in ("control_label_smoothing", "control_stimulus_shuffle", "control_feature_shuffle"))
    check("대조군은 6 fold 144회(7-L)", controls * 6 == 144)
    g16 = sum(plan[n] for n in ("multimodal", "brain_only_repr_frozen", "brain_only_repr_trained"))
    check("조건 6, 7은 6 fold 162회(7-L)", g16 * 6 == 162)
    pool = plan["brain_only_pool"] + plan["brain_decoded_pool"]
    check("평균 pooling판은 6 fold 36회(O31)", pool * 6 == 36)
    check("모든 조건에 learning rate 후보 세 개가 있다(G13)", all({x["lr"] for x in S.candidates(n, k_candidates=Ks, base=base, decoded=decoded)} == set(S.LEARNING_RATES) for n in lens))
    lam_only = S.candidates("brain_only_featdec", base=base)
    check("조건 2는 λ = 0.1, 1.0만 새로 학습한다(G9)", {x["lam"] for x in lam_only} == {0.1, 1.0})
    check("조건 3은 λ 0이 없고 r은 1, 2, 4, 8이다", {x["lam"] for x in S.candidates("brain_decoded", base=base)} == {0.1, 1.0} and {x["rank"] for x in S.candidates("brain_decoded", base=base)} == {1, 2, 4, 8})
    check("더하기 head의 r은 0이다", {x["rank"] for x in S.candidates("brain_decoded_additive", base=base)} == {0})
    d5c = S.candidates("brain_decoded_distill", base=base, decoded=decoded)
    check("조건 5는 조건 3에서 고른 λ와 r을 고정한다", {x["lam"] for x in d5c} == {0.1} and {x["rank"] for x in d5c} == {2} and {x["alpha"] for x in d5c} == {0.25, 0.5})
    check("d와 입력층 weight decay는 brain_only의 선택을 따른다(5-5)", all(x["d"] == 8 and x["input_wd"] == 1e-3 for n in lens if n != "brain_only" for x in S.candidates(n, base=base, decoded=decoded)))
    check("조건 6, 7은 λ 0.1, 1.0이다", {x["lam"] for x in S.candidates("brain_only_repr_frozen", base=base)} == {0.1, 1.0} == {x["lam"] for x in S.candidates("brain_only_repr_trained", base=base)})
    check("Multimodal Model은 특징 선형층 weight decay를 고른다(O5)", {x["feature_wd"] for x in S.candidates("multimodal", base=base)} == {1e-4, 1e-3, 1e-2})
    check("K가 없으면 멈춘다(S7)", stops(lambda: S.candidates("brain_only")))
    check("d가 4의 배수가 아니면 멈춘다", stops(lambda: S.candidates("brain_only", k_candidates=[(6, 1e-3)])))
    check("learning rate가 G13 밖이면 멈춘다", stops(lambda: S.candidates("brain_only", k_candidates=KS, learning_rates=(3e-4,))))
    check("brain_only 없이 다른 조건을 정할 수 없다", stops(lambda: S.candidates("brain_decoded")))
    check("조건 5는 조건 3의 선택이 있어야 한다", stops(lambda: S.candidates("brain_decoded_distill", base=base)))
    check("평균 pooling판은 후보를 고르지 않는다(O31)", stops(lambda: S.candidates("brain_only_pool", base=base)))
    follow = S.candidates("brain_decoded", base=base, lr_follows_brain_only=True)
    check("S7에서 줄이면 brain_only에서 고른 learning rate만 쓴다(G13)", {x["lr"] for x in follow} == {1e-3} and len(follow) == 8)
    good = S._cand(**base, lam=0.1, rank=2)
    S.check_candidate("brain_decoded", good)
    check("α = 0을 학습으로 돌리면 멈춘다", stops(lambda: S.check_candidate("brain_only_distill", S._cand(**base, alpha=0.0))))
    check("λ = 0을 조건 3으로 돌리면 멈춘다", stops(lambda: S.check_candidate("brain_decoded", S._cand(**base, lam=0.0, rank=2))))
    check("더하기 head에 r을 주면 멈춘다", stops(lambda: S.check_candidate("brain_decoded_additive", good)))
    check("상호작용 head에 r = 0을 주면 멈춘다", stops(lambda: S.check_candidate("brain_decoded", S._cand(**base, lam=0.1, rank=0))))
    check("feature 없는 조건에 λ를 주면 멈춘다", stops(lambda: S.check_candidate("brain_only", S._cand(**base, lam=0.1))))
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "c.json"
        f.write_text(json.dumps(dict(k_candidates=[[32, 0.001], [64, 0.01]], learning_rates=[1e-3], extra=1)))
        check("설정에 모르는 키가 있으면 멈춘다", stops(lambda: S.load_config(f)))
        f.write_text(json.dumps(dict(k_candidates=[[32, 0.001], [64, 0.01]])))
        cfg = S.load_config(f)
        check("설정을 읽는다", cfg.k_candidates == ((32, 1e-3), (64, 1e-2)) and cfg.learning_rates == S.LEARNING_RATES)
    check("S7 전의 설정 틀은 실제 실행을 시작하지 못한다", stops(lambda: S.load_config(S.CONFIGS / "run_config.template.json")))


def t_selection():
    rows = lambda **kw: dict(d=8, input_wd=1e-3, lr=1e-3, lam=None, alpha=None, rank=None, feature_wd=None, val_score=0.5) | kw
    check("큰 점수를 고른다", S.select_best([rows(val_score=0.4), rows(val_score=0.6, lr=1e-2)])["lr"] == 1e-2)
    check("같은 점수면 d가 작은 쪽(O6)", S.select_best([rows(d=16), rows(d=8)])["d"] == 8)
    check("같은 점수면 λ가 작은 쪽", S.select_best([rows(lam=1.0), rows(lam=0.1)])["lam"] == 0.1)
    check("같은 점수면 α가 작은 쪽", S.select_best([rows(alpha=0.5), rows(alpha=0.0)])["alpha"] == 0.0)
    check("같은 점수면 r이 작은 쪽", S.select_best([rows(rank=8), rows(rank=2)])["rank"] == 2)
    check("같은 점수면 weight decay가 작은 쪽", S.select_best([rows(input_wd=1e-2), rows(input_wd=1e-3)])["input_wd"] == 1e-3)
    check("같은 점수면 learning rate가 작은 쪽", S.select_best([rows(lr=1e-2), rows(lr=1e-4)])["lr"] == 1e-4)
    check("순서: d가 λ보다 먼저다", S.select_best([rows(d=8, lam=1.0), rows(d=16, lam=0.1)])["d"] == 8)
    check("시험 값이 있으면 멈춘다(H5)", stops(lambda: S.select_best([rows(test_score=0.9)])))
    check("점수가 NaN이면 첫 후보로 넘어가지 않고 멈춘다", stops(lambda: S.select_best([rows(val_score=float("nan"))])))
    g = np.random.default_rng(0)
    y = g.uniform(size=(40, 34))
    y[:, 3] = 0.2  # 상수 정답
    p = y + 0.1 * g.normal(size=y.shape)
    names = np.array(["a"] * 20 + ["b"] * 20)
    v = S.validation_score(p, y, names)
    expect = []
    for n in ("a", "b"):
        at = names == n
        rs = c.pearson(p[at], y[at])
        expect.append(np.nanmean(np.delete(rs, 3)))
    check("선택 점수는 참가자별 r을 낸 뒤 평균한다. y가 상수인 정서는 뺀다(O6)", abs(v - np.mean(expect)) < 1e-12)
    pc = p.copy()
    pc[:, 0] = 0.5
    ra = c.pearson(pc[names == "a"], y[names == "a"])
    ra[0] = 0
    rb = c.pearson(pc[names == "b"], y[names == "b"])
    rb[0] = 0
    check("예측이 상수인 정서는 선택 계산에서만 0으로 센다(O6)", abs(S.validation_score(pc, y, names) - np.mean([np.nanmean(np.delete(ra, 3)), np.nanmean(np.delete(rb, 3))])) < 1e-12)
    check("예측이 NaN이면 멈춘다", stops(lambda: S.validation_score(p * np.nan, y, names)))
    check("모든 y가 상수이면 멈춘다", stops(lambda: S.validation_score(p, np.ones_like(y), names)))
    source = [rows(val_score=0.7, lr=1e-3, candidate_id="x", source_condition=None, source_id=None), rows(val_score=0.6, lr=1e-2, candidate_id="y", source_condition=None, source_id=None), rows(val_score=0.9, d=16, candidate_id="z", source_condition=None, source_id=None)]
    z = S.zero_rows("brain_only_distill", source, dict(d=8, input_wd=1e-3))
    check("0 후보는 앞 조건의 같은 d, weight decay 행으로 채운다(G9)", len(z) == 2 and all(x["alpha"] == 0.0 and x["source_condition"] == "brain_only" for x in z))
    check("앞 조건이 없는 조건에는 0 후보가 없다", S.zero_rows("brain_decoded", source, source[0]) == [])


def pipeline(root, w=None, config=None, spec=FAST, conditions=None):
    w = w or World()
    WORLD_SPLIT[0] = w.split
    fd = w.fold(include_test_features=True)
    run = run_for(root, plan="outer_fold1", spec=str(spec))
    runner = T.FoldRunner(fd, w.split, run, spec, config or S.Config(KS, (1e-4, 1e-3)), Path(root) / "outer_fold1")
    for name in conditions or S.ORDER:
        runner.run_condition(name)
    return w, fd, run, runner


def t_pipeline():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        w, fd, run, runner = pipeline(root)
        out = root / "outer_fold1"
        selected = {n: runner.selected(n) for n in S.ORDER}
        expect_trained = 0
        for n in S.ORDER:
            sel = selected[n]
            if n in S.POOLED:
                expect_trained += 3
            else:
                n_cand = len(S.candidates(n, k_candidates=KS, base=selected["brain_only"]["candidate"], decoded=selected["brain_decoded"]["candidate"], learning_rates=(1e-4, 1e-3)))
                expect_trained += n_cand + (0 if sel["zero_selected"] else 2)
        check(f"전체 조건의 학습 횟수가 계획과 같다({len(runner.trained)}회)", len(runner.trained) == expect_trained)
        d = selected["brain_only"]["candidate"]["d"]
        check("고른 d가 후보 안에 있고 다른 조건도 같은 d, 입력층 weight decay를 쓴다(5-5)", (d, selected["brain_only"]["candidate"]["input_wd"]) in KS and all(selected[n]["candidate"]["d"] == d and selected[n]["candidate"]["input_wd"] == selected["brain_only"]["candidate"]["input_wd"] for n in S.ORDER))
        check("평균 pooling판은 표준 실행의 설정을 그대로 쓴다(O31)", {k: selected["brain_decoded_pool"]["candidate"][k] for k in ("d", "input_wd", "lam", "rank", "lr")} == {k: selected["brain_decoded"]["candidate"][k] for k in ("d", "input_wd", "lam", "rank", "lr")})
        check("조건 5는 조건 3의 λ와 r을 쓴다", selected["brain_decoded_distill"]["candidate"]["rank"] == selected["brain_decoded"]["candidate"]["rank"] and selected["brain_decoded_distill"]["candidate"]["lam"] == selected["brain_decoded"]["candidate"]["lam"])
        # 저장(M1)
        ok_m1 = True
        for n in S.ORDER:
            for rel in selected[n]["seeds"].values():
                path = out / rel
                done = json.loads((path / "done.json").read_text())
                ok_m1 &= all((path / f).exists() for f in ("model.pt", "history.tsv", "val_pred.npz", "test_pred.npz", "parameter_groups.json", "outputs/done.json", "outputs/test_outputs.npz"))
                ok_m1 &= all(k in done for k in ("run_key", "code_commit", "inputs", "settings", "candidate", "best_epoch", "val_score", "val_loss", "elapsed_seconds", "parameter_counts")) and "s2:split_hk_dev.tsv" in done["inputs"]
        check("M1: 고른 모델의 config, 커밋, 입력 해시, 체크포인트, 예측이 남는다", ok_m1)
        check("M1: 분할 기록과 표준화 통계가 남는다", all((out / "plan" / f).exists() for f in ("plan.json", "rows.npz", "standardization.npz", "done.json")))
        stats = np.load(out / "plan/standardization.npz")
        check("표준화 파일의 값이 쓰인 통계와 같다", np.array_equal(stats["visual_mean"], fd.feature_stats["visual_mean"]) and np.array_equal(stats["voxel_std:sub-02"], fd.voxel_stats["sub-02"]["std"]))
        check("M1: 선택 기록에 d, weight decay, λ, α, r, lr, epoch가 있다", set(pd.read_csv(out / "brain_decoded/selection.tsv", sep="\t").columns) >= {"d", "input_wd", "lam", "alpha", "rank", "lr", "best_epoch", "val_score"})
        check("선택표에 시험 값이 없다", not any("test" in x for n in S.ORDER if n not in S.POOLED for x in pd.read_csv(out / n / "selection.tsv", sep="\t").columns))
        # 후보별 시험 예측(N24)
        cand_dirs = [p for p in (out / "brain_decoded").glob("*_seed0")]
        check("N24: 후보마다 시험 예측이 저장된다", len(cand_dirs) == 16 and all((p / "test_pred.npz").exists() for p in cand_dirs))
        keep = {out / r for r in selected["brain_decoded"]["seeds"].values()}
        check("고르지 않은 후보의 체크포인트는 지운다", all((p / "model.pt").exists() == (p in keep) for p in cand_dirs))
        # 시험 행, 검증 행, 형식
        test, val = fd.rows("test"), fd.rows("val")
        dec = out / selected["brain_decoded"]["seeds"]["0"]
        tt = np.load(dec / "outputs/test_outputs.npz")
        check("시험 예측은 시험 행을 정확히 담는다", sorted(zip(tt["participant"].tolist(), tt["video_id"].tolist())) == sorted(zip(fd.participant_names(test).tolist(), fd.row_video[test].tolist())))
        check("시험 예측은 logit과 확률을 함께 둔다", np.allclose(tt["p"], 1 / (1 + np.exp(-tt["logit"].astype(np.float64))), atol=1e-5))
        dt, dv = np.load(dec / "outputs/decoded_test.npz"), np.load(dec / "outputs/decoded_val.npz")
        check("decoded features는 시험과 검증 fold 모두 저장된다", dt["v_hat"].shape == (len(test), 5632) and dt["c_hat"].shape == (len(test), 4096) and dv["v_hat"].shape == (len(val), 5632))
        check("decoded features의 행이 맞다", dv["video_id"].tolist() == fd.row_video[val].tolist() and dt["video_id"].tolist() == fd.row_video[test].tolist())
        ae, af = np.load(dec / "outputs/attention_emotion_test.npy"), np.load(dec / "outputs/attention_feature_test.npy")
        check("attention: emotion query와 feature query의 값이 저장된다", ae.shape == (len(test), 4, 34, 5) and af.shape == (len(test), 4, 2, 5) and np.allclose(ae.sum(-1), 1, atol=1e-4))
        acc = pd.read_csv(dec / "outputs/decoding_accuracy.tsv", sep="\t")
        check("decoding 정확도는 학습과 검증 영상으로 기록한다(5-0)", set(acc.split) == {"train", "val"} and set(acc.target) == {"vision", "caption"} and acc.mse.notna().all() and len(acc) == 20)
        check("조건 2도 decoding 정확도를 기록한다", (out / selected["brain_only_featdec"]["seeds"]["0"] / "outputs/decoding_accuracy.tsv").exists() or selected["brain_only_featdec"]["zero_selected"])
        check("feature head가 없는 조건에는 decoded 파일이 없다", not (out / selected["brain_only"]["seeds"]["0"] / "outputs/decoded_test.npz").exists())
        check("평균 pooling판에는 emotion attention이 없고 feature attention은 있다", not (out / selected["brain_decoded_pool"]["seeds"]["0"] / "outputs/attention_emotion_test.npy").exists() and (out / selected["brain_decoded_pool"]["seeds"]["0"] / "outputs/attention_feature_test.npy").exists())
        # 다시 읽은 모델이 같은 값을 낸다, 시험 입력은 뇌뿐이다
        m, meta = M.load_checkpoint(dec / "model.pt")
        z = T.collect(m, test, T.brain_forward(fd), 16)["z"].numpy()
        check("체크포인트를 다시 읽으면 시험 예측이 같다", np.allclose(z, tt["logit"], atol=1e-6) and meta["condition"] == "brain_decoded")
        hidden = {k: getattr(fd, k).clone() for k in ("y_bank", "vision_bank", "caption_bank")}
        hidden_t = fd.t_bank.clone()
        fd.y_bank.fill_(float("nan")), fd.vision_bank.fill_(float("nan")), fd.caption_bank.fill_(float("nan")), fd.t_bank.fill_(float("nan"))
        same_all = True
        for n in S.ORDER:
            if n == "multimodal":
                continue
            path = out / selected[n]["seeds"]["0"]
            mm, _ = M.load_checkpoint(path / "model.pt")
            same_all &= np.allclose(T.collect(mm, test, T.brain_forward(fd), 16)["z"].numpy(), np.load(path / "test_pred.npz")["logit"], atol=1e-6)
        check("시험 입력은 Brain뿐이다: 정답과 feature를 모두 NaN으로 지워도 13개 조건의 시험 예측이 같다", same_all)
        for k, v in hidden.items():
            getattr(fd, k).copy_(v)
        fd.t_bank.copy_(hidden_t)
        # 모든 조건에서 조기 종료와 선택은 실제 y다
        y_val = fd.y(val).numpy()
        ok_loss, ok_score, ok_hist = True, True, True
        for n in S.ORDER:
            for rel in selected[n]["seeds"].values():
                path = out / rel
                done = json.loads((path / "done.json").read_text())
                vp = np.load(path / "val_pred.npz")
                loss = F.binary_cross_entropy_with_logits(torch.as_tensor(vp["logit"]), torch.as_tensor(y_val)).item()
                hist = pd.read_csv(path / "history.tsv", sep="\t")
                ok_loss &= abs(loss - done["val_loss"]) < 1e-5
                ok_hist &= abs(hist.val_loss.min() - done["val_loss"]) < 1e-9 and hist.val_loss.argmin() + 1 == done["best_epoch"]
                ok_score &= abs(S.validation_score(vp["p"], y_val, vp["participant"]) - done["val_score"]) < 1e-5
        check("조기 종료 값이 모든 조건에서 실제 y의 정서 soft BCE다", ok_loss)
        check("고른 epoch는 그 값이 가장 낮은 epoch다", ok_hist)
        check("선택 점수가 모든 조건에서 실제 y의 r 평균이다", ok_score)
        # 대조군의 순열 저장
        ok_sh = True
        for n in ("control_stimulus_shuffle", "control_feature_shuffle"):
            for seed, rel in selected[n]["seeds"].items():
                sj = json.loads((out / rel / "shuffle.json").read_text())
                ok_sh &= dict(map(tuple, sj["mapping"])) == dict(S.shuffle_plan(w.split, fd.plan, int(seed)).mapping) and sj["seed"] == int(seed)
        check("O1: 순열과 그 seed가 저장되고 다시 만든 값과 같다", ok_sh)
        rows0 = pd.read_csv(out / "control_feature_shuffle/selection.tsv", sep="\t")
        maps = {json.dumps(json.loads((out / "control_feature_shuffle" / f"{i}_seed0" / "shuffle.json").read_text())["mapping"]) for i in rows0.candidate_id}
        check("O1: 같은 fold와 seed에서는 λ가 달라도 같은 순열이다", len(maps) == 1)
        # 조건 6, 7
        mm_sel = selected["multimodal"]
        ok_pair = True
        for n in ("brain_only_repr_frozen", "brain_only_repr_trained"):
            for seed, rel in selected[n]["seeds"].items():
                tj = json.loads((out / rel / "teacher.json").read_text())
                ok_pair &= tj["seed"] == int(seed) and tj["checkpoint_sha256"] == c.sha256(out / mm_sel["seeds"][seed] / "model.pt")
                st = np.load(out / rel / "representation_stats.npz")
                ok_pair &= st["mean"].shape == (34, mm_sel["candidate"]["d"])
        check("조건 6, 7은 같은 seed의 Multimodal Model과 짝짓고 그 해시를 남긴다(O5)", ok_pair)
        check("Multimodal Model의 시험 예측은 참고로 남는다(G16)", (out / mm_sel["seeds"]["0"] / "test_pred.npz").exists())
        froz, _ = M.load_checkpoint(out / selected["brain_only_repr_frozen"]["seeds"]["0"] / "model.pt")
        teach, _ = M.load_checkpoint(out / mm_sel["seeds"]["0"] / "model.pt")
        check("조건 6: 학습 뒤 head가 Multimodal Model의 head와 같다", all(torch.equal(a, b) for a, b in zip(froz.readout.emotion_linears.state_dict().values(), teach.emotion_linears.state_dict().values())))
        pg = json.loads((out / selected["brain_only_repr_frozen"]["seeds"]["0"] / "parameter_groups.json").read_text())
        check("조건 6: 저장한 묶음에서 head는 frozen이다", all(v == "frozen" for k, v in pg.items() if "emotion_linears" in k))
        tr, _ = M.load_checkpoint(out / selected["brain_only_repr_trained"]["seeds"]["0"] / "model.pt")
        check("조건 7: 학습 뒤 head가 복사한 값에서 달라졌다", not all(torch.equal(a, b) for a, b in zip(tr.readout.emotion_linears.state_dict().values(), teach.emotion_linears.state_dict().values())))
        # 건너뛰기
        again = T.FoldRunner(fd, w.split, run, FAST, S.Config(KS, (1e-4, 1e-3)), out)
        for n in S.ORDER:
            again.run_condition(n)
        check("같은 실행 번호면 끝난 결과를 건너뛴다", again.trained == [])
        other = run_for(root, plan="outer_fold1", spec="다른 설정")
        check("실행 번호가 다르면 섞지 않고 멈춘다", stops(lambda: T.FoldRunner(fd, w.split, other, FAST, S.Config(KS, (1e-4, 1e-3)), out)))
        check("앞 조건의 선택이 없으면 멈춘다", stops(lambda: T.FoldRunner(fd, w.split, run, FAST, S.Config(KS, (1e-4, 1e-3)), root / "빈곳").run_condition("brain_decoded")))
        wrong = run_for(root, plan="다른 분할")
        t2 = T.FoldRunner(fd, w.split, wrong, FAST, S.Config(KS, (1e-4, 1e-3)), root / "다른곳")
        (root / "다른곳/brain_only").mkdir(parents=True)
        (root / "다른곳/brain_only/selected.json").write_text((out / "brain_only/selected.json").read_text())
        check("다른 실행의 선택을 쓰지 않는다", stops(lambda: t2.selected("brain_only")))
        # 부호를 뒤집은 test_pred 파일을 넣어도 선택이 그대로다
        before = (out / "brain_decoded/selected.json").read_text()
        for p in (out / "brain_decoded").glob("*_seed0"):
            np.savez(p / "test_pred.npz", broken=np.zeros(1))
        again.run_condition("brain_decoded")
        check("선택은 시험 예측 파일을 읽지 않는다", (out / "brain_decoded/selected.json").read_text() == before)


def t_representation_unit():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        w, fd, run, runner = pipeline(root, config=S.Config(((8, 1e-3),), (1e-3,)), conditions=["brain_only", "multimodal"])
        teacher = runner.teacher(0)
        digest = M.state_digest(teacher.model)
        cand = S._cand(d=8, input_wd=1e-3, lr=1e-3, lam=1.0)
        rows = fd.rows("train")[:16]
        for name, frozen in (("brain_only_repr_frozen", True), ("brain_only_repr_trained", False)):
            T.seed_everything(0)
            m = S.build_model(name, cand, fd.voxel_counts)
            m.load_head_from(teacher.model, frozen=frozen)
            check(f"{name}: head 값이 Multimodal Model과 같게 시작한다", all(torch.equal(a, b) for a, b in zip(m.readout.emotion_linears.state_dict().values(), teacher.model.emotion_linears.state_dict().values())))
            check(f"{name}: head가 Multimodal Model과 메모리를 공유하지 않는다", all(a is not b for a, b in zip(m.readout.emotion_linears.parameters(), teacher.model.emotion_linears.parameters())))
            check(f"{name}: Multimodal Model의 encoder와 입력층은 복사하지 않는다", not torch.equal(m.encoder.final_norm.weight, teacher.model.encoder.final_norm.weight) or not torch.equal(m.input_layer.roi_embedding, teacher.model.input_layer.roi_embedding))
            start_head = {k: v.clone() for k, v in m.readout.emotion_linears.state_dict().items()}
            start_enc = {k: v.clone() for k, v in m.encoder.state_dict().items()}
            start_input = m.input_layer.weights["sub-01"].detach().clone()
            loss_fn = T.make_loss(name, cand, fd, teacher=teacher)
            m.train()
            out = T.brain_forward(fd)(m, rows)
            T.soft_bce(out.z, fd.y(rows)).backward()
            enc_grad = all(p.grad is not None and p.grad.abs().sum() > 0 for p in m.encoder.parameters())
            inp_grad = m.input_layer.weights["sub-01"].grad.abs().sum() > 0
            check(f"{name}: L_emotion의 기울기가 encoder와 입력층까지 간다(5-A)", enc_grad and inp_grad)
            if frozen:
                check("조건 6: head에는 기울기가 쌓이지 않는다", all(p.grad is None for p in m.readout.emotion_linears.parameters()))
            else:
                check("조건 7: head에도 기울기가 간다", all(p.grad is not None and p.grad.abs().sum() > 0 for p in m.readout.emotion_linears.parameters()))
            m.zero_grad(set_to_none=True)
            spec = S.Spec(batch=16, max_epochs=2, patience=30)
            T.fit(m, fd, spec, lr=1e-2, input_wd=1e-3, feature_wd=None, loss_fn=loss_fn, forward=T.brain_forward(fd), seed=0)
            same_head = all(torch.equal(v, start_head[k]) for k, v in m.readout.emotion_linears.state_dict().items())
            check(f"{name}: 학습 뒤 head가 {'그대로다' if frozen else '바뀐다'}", same_head == frozen)
            check(f"{name}: encoder와 입력층은 바뀐다", not all(torch.equal(v, start_enc[k]) for k, v in m.encoder.state_dict().items()) and not torch.equal(start_input, m.input_layer.weights["sub-01"].detach()))
            check(f"{name}: Multimodal 원본이 바뀌지 않는다", M.state_digest(teacher.model) == digest)
        check("Multimodal 원본은 기울기를 받지 않는다", all(not p.requires_grad for p in teacher.model.parameters()) and not teacher.model.training)
        m = S.build_model("brain_only_repr_frozen", cand, fd.voxel_counts)
        m.load_head_from(teacher.model, frozen=True)
        names = {n for g in M.parameter_groups(m, 1e-3, 1e-3) for n in [g["name"]]}
        opt_ids = {id(p) for g in M.parameter_groups(m, 1e-3, 1e-3) for p in g["params"]}
        check("조건 6: 고정한 head는 optimizer에 들어가지 않는다", not any(id(p) in opt_ids for p in m.readout.emotion_linears.parameters()) and "frozen" not in names)
        # L_representation의 값
        m.eval()
        rows = fd.rows("train")[:8]
        out = m(fd.batch(rows))
        with torch.no_grad():
            got = T.make_loss("brain_only_repr_frozen", cand, fd, teacher=teacher)(out, rows)
            pos = torch.as_tensor(teacher.position[rows])
            expect = T.soft_bce(out.z, fd.y(rows)) + 1.0 * ((out.o - teacher.o[pos]) / teacher.std).pow(2).mean()
        check("조건 6: 손실 = L_emotion + λ × 표준화한 표현의 MSE(O5)", abs((got - expect).item()) < 1e-4)
        z_raw = out.z.detach()
        check("조건 6: 고정 head에는 학습 좌표 그대로 표현을 넣는다(O5)", torch.allclose(torch.cat([teacher.model.emotion_linears[e](out.o[:, e]) for e in range(34)], 1), z_raw, atol=1e-6))
        train_rows = fd.rows("train")
        o_all = T.collect(teacher.model, train_rows, T.multimodal_forward(fd), 16, ("o",))["o"].numpy()
        check("표현의 표준화 통계는 Multimodal Model이 학습한 행에서 낸다(O5)", np.allclose(teacher.mean.numpy(), o_all.astype(np.float64).mean(0), atol=1e-5) and np.allclose(teacher.std.numpy(), o_all.astype(np.float64).std(0), atol=1e-5))
        # Multimodal Model: 실제 feature가 입력이다
        mm = teacher.model
        val = fd.rows("val")[:6]
        v, cap = fd.feature_targets(val)
        b = fd.batch(val)
        check("Multimodal Model은 실제 feature를 입력으로 받는다", not torch.allclose(mm(b, v, cap).z, mm(b, v + 1, cap).z) and not torch.allclose(mm(b, v, cap).z, mm(b, v, cap + 1).z))
        check("Multimodal Model의 token 수는 ROI + 2다", mm(b, v, cap).emotion_attention.shape[-1] == 7)
        check("Multimodal Model은 시험 feature 없이 시험 행을 낼 수 없다", stops(lambda: w.fold().multimodal_inputs(fd.rows("test"))))
        test = fd.rows("test")
        a, c2 = fd.multimodal_inputs(test)
        expected = [list(w.split.video_id).index(int(x)) for x in fd.row_video[test]]
        check("Multimodal Model의 시험 입력도 학습 fold 통계로 표준화한다", np.allclose(a.numpy(), (w.v[expected] - fd.feature_stats["visual_mean"]) / fd.feature_stats["visual_std"], atol=1e-4))


def t_zero_selected():
    old = S.validation_score
    S.validation_score = lambda p, y, names: 0.5  # 모두 같은 점수면 O6의 동점 규칙으로 0 후보가 뽑힌다
    try:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            w, fd, run, runner = pipeline(root, conditions=["brain_only", "brain_only_distill", "brain_only_featdec", "brain_decoded", "brain_decoded_distill"])
            out = root / "outer_fold1"
            for name, src, key in (("brain_only_distill", "brain_only", "alpha"), ("brain_only_featdec", "brain_only", "lam"), ("brain_decoded_distill", "brain_decoded", "alpha")):
                sel, source = runner.selected(name), runner.selected(src)
                check(f"{name}: 0이 뽑힌 fold를 표시한다(G10)", sel["zero_selected"] and sel["candidate"][key] == 0.0 and sel["source_condition"] == src)
                check(f"{name}: 그 fold의 결과는 앞 조건의 모델이다(G10)", sel["seeds"] == source["seeds"])
                check(f"{name}: 새 seed를 학습하지 않는다", not any(c0 == name and s != 0 for c0, _, s in runner.trained))
                table = pd.read_csv(out / name / "selection.tsv", sep="\t")
                check(f"{name}: 선택표에 0 후보와 그 출처가 있다", (table[key] == 0).sum() >= 1 and set(table.source_condition.dropna()) == {src})
            check("동점이면 작은 d, 작은 learning rate를 고른다", runner.selected("brain_only")["candidate"]["d"] == 8 and runner.selected("brain_only")["candidate"]["lr"] == 1e-4)
            check("0 후보를 고르면 조건 5의 결과도 조건 3의 r을 유지한다", runner.selected("brain_decoded_distill")["candidate"]["rank"] == runner.selected("brain_decoded")["candidate"]["rank"])
    finally:
        S.validation_score = old


def t_guard():
    with tempfile.TemporaryDirectory():
        called = []
        old = (T.load_known, S.load_brains, S.load_config)
        T.load_known = lambda *a, **k: called.append("known")
        S.load_brains = lambda *a, **k: called.append("brain")
        try:
            check("동결 커밋 없이는 실제 실행이 멈춘다", stops(lambda: T.main(["--plan", "outer_fold1", "--conditions", "brain_only", "--config", str(S.CONFIGS / "run_config.template.json")]), (SystemExit,)))
            check("없는 커밋을 주면 멈춘다", stops(lambda: T.main(["--plan", "outer_fold1", "--conditions", "brain_only", "--config", str(S.CONFIGS / "run_config.template.json"), "--design-freeze", "0" * 40]), (SystemExit,)))
            check("멈출 때 자료를 읽지 않았다", called == [])
        finally:
            T.load_known, S.load_brains = old[0], old[1]
    src = (c.CODE_DIR / "s6_train.py").read_text() + (c.CODE_DIR / "s6_common.py").read_text()
    check("뇌 반응은 허용 행 검사(d5.allowed_rows)와 행 읽기(d5.read_rows)로만 읽고 배열을 직접 인덱싱하지 않는다", "d5.allowed_rows(" in src and "d5.read_rows(raw" in src and not re.search(r"\braw\[(?![\"'])", src) and src.count("np.load(d5.response_path") == 1)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        table = pd.DataFrame(dict(participant="sub-99", video_id=[3001, 3002, 3003], content_id=[1, 2, 3], qc_row=[5, 1, 3]))
        cw = pd.Series({3001: 11, 3002: 12, 3003: 13})
        raw = np.arange(60, dtype=np.float32).reshape(6, 10)
        np.save(td / "raw.npy", raw)
        roi = ["a", "b"]
        np.savez(td / "roi.npz", columns=np.array([1, 2, 2, 7]), offsets=np.array([0, 3, 4]), n_columns=np.array(10), roi=np.array(roi))
        split = pd.DataFrame(dict(video_id=[3001, 3002, 3003], fold=[1, 2, 3]))
        out = S.load_brains(split, [3001, 3002, 3003], ["99"], raw_path=td / "raw.npy", roi_file=td / "roi.npz", table=table, crosswalk=cw, mc72=[])
        check("load_brains는 허용 행의 값을 읽는다", out["sub-99"].video_id.tolist() == [3002, 3003, 3001] and np.array_equal(out["sub-99"].X[0], raw[1][[1, 2, 7]]))
        check("MC 72개와 같은 내용의 행이 있으면 멈춘다", stops(lambda: S.load_brains(split, [3001, 3002, 3003], ["99"], raw_path=td / "raw.npy", roi_file=td / "roi.npz", table=table, crosswalk=cw, mc72=[12])))
        with np.load(d5.roi_path("01")) as z, np.load(d5.roi_path("05")) as y:
            check("실제 ROI 표: 다섯 명 중 두 명의 ROI 순서가 같다", z["roi"].tolist() == y["roi"].tolist() and len(z["roi"]) == 370)
    counts = dict(a=[3, 4, 5], b=[2, 2, 2])
    table = T.weight_table([8, 16], voxel_counts=counts)
    row = table[(table.condition == "brain_only") & (table.d == 8)].iloc[0]
    check("F8: 입력층 가중치는 d × (ROI별 voxel 수의 합)이다", row.input_weight == 8 * 18 and row.input_bias == 8 * 3 * 2 and row.roi_embedding == 8 * 3)
    additive = table[(table.condition == "brain_decoded_additive") & (table.d == 8)].iloc[0]
    rank8 = table[(table.condition == "brain_decoded") & (table.d == 8) & (table["rank"] == 8)].iloc[0]
    check("F8: 조건 3의 r마다 줄이 있고 상호작용 head가 더 크다", rank8.shared - additive.shared == 8 * (5632 + 4096) + 34 * 8 and set(table[table.condition == "brain_decoded"]["rank"].astype(int)) == {1, 2, 4, 8})
    frozen = table[(table.condition == "brain_only_repr_frozen") & (table.d == 8)].iloc[0]
    check("F8: 조건 6은 고정한 head를 학습 수에서 뺀다", frozen.frozen == 34 * 9 and frozen.trainable == row.trainable - 34 * 9)


def timing():
    """실제 voxel 수로 학습 한 step을 측정한다. 값은 합성 난수이고 실제 뇌 반응과 정답을 읽지 않는다. d는 어림용이다. S6_TIMING_DEVICE로 장치를 고른다."""
    device = os.environ.get("S6_TIMING_DEVICE", "cpu")
    sync = torch.cuda.synchronize if device.startswith("cuda") else (lambda: None)
    counts = {}
    for s in d5.HK:
        with np.load(d5.roi_path(s)) as z:
            counts[f"sub-{s}"] = np.diff(z["offsets"]).tolist()
            unique = len(np.unique(z["columns"]))
    table = pd.read_csv(d5.BLOCKS, sep="\t")
    print("참가자별 행 수", table.groupby("participant").size().to_dict(), "ROI별 voxel 합", {k: sum(v) for k, v in counts.items()})
    torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "4")))
    results = []
    for d in (64,):
        for name, cand in (("brain_only", dict(d=d, input_wd=1e-3, lr=1e-3, lam=None, alpha=None, rank=None, feature_wd=None)), ("brain_decoded", dict(d=d, input_wd=1e-3, lr=1e-3, lam=0.1, alpha=None, rank=8, feature_wd=None)), ("brain_only_featdec", dict(d=d, input_wd=1e-3, lr=1e-3, lam=0.1, alpha=None, rank=None, feature_wd=None))):
            torch.manual_seed(0)
            built = time.time()
            m = S.build_model(name, cand, counts).to(device)
            built = time.time() - built
            opt = torch.optim.AdamW(M.parameter_groups(m, cand["lr"], cand["input_wd"]))
            params = sum(p.numel() for p in m.parameters())
            xs, positions = {}, {}
            at = 0
            for pid, v in counts.items():
                xs[pid] = torch.randn(13, sum(v), device=device)
                positions[pid] = torch.arange(at, at + 13, device=device)
                at += 13
            b = M.BrainBatch(xs, positions, at)
            y = torch.rand(at, 34, device=device)
            vt, ct = torch.randn(at, M.VISUAL_DIM, device=device), torch.randn(at, M.CAPTION_DIM, device=device)
            m.train()
            spent = []
            for step in range(4):
                sync()
                t0 = time.time()
                opt.zero_grad(set_to_none=True)
                out = m(b)
                loss = T.soft_bce(out.z, y)
                if name != "brain_only":
                    loss = loss + 0.1 * (F.mse_loss(out.v_hat, vt) + F.mse_loss(out.c_hat, ct)) / 2
                loss.backward()
                opt.step()
                sync()
                spent.append(time.time() - t0)
            m.eval()
            t0 = time.time()
            with torch.no_grad():
                m(b)
            sync()
            forward = time.time() - t0
            if device.startswith("cuda"):
                print("GPU 최대 메모리 GB", round(torch.cuda.max_memory_allocated() / 1024**3, 2), flush=True)
            rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024**2
            results.append(dict(condition=name, d=d, n_params=params, param_gb=params * 4 / 1024**3, step_seconds=float(np.median(spent[1:])), eval_seconds=forward, build_seconds=built, peak_rss_gb=rss, batch_rows=at))
            print(results[-1], flush=True)
            del m, opt, b, xs
    rows = len(table)
    unique_gb = rows * unique * 4 / 1024**3
    print(f"개발 block {rows}행 × 고유 voxel 약 {unique}개 × 4 byte = 뇌 입력 {unique_gb:.1f} GB (d와 무관, 시험 행 포함)")
    print("학습 행 약 2/3 =", rows * 4 // 6, "행, batch 64에서 epoch당", rows * 4 // 6 // 64, "step")
    for r in results:
        print(f"{r['condition']}: 가중치 {r['param_gb']:.2f} GB, AdamW 상태와 가장 낮은 epoch 사본을 더하면 약 {r['param_gb'] * 4:.2f} GB")


def t_read_boundary():
    """Codex 1. 원본 배열을 인덱싱하기 전에 이번 실행의 영상으로 줄인다. 파일럿은 시험 영상의 반응을 읽지 않는다."""
    class Recorder:
        def __init__(self, a):
            self.a, self.shape, self.read = a, a.shape, []
        def __getitem__(self, rows):
            self.read += np.asarray(rows).tolist()
            return self.a[rows]
    n = 24
    split = pd.DataFrame(dict(video_id=np.arange(1, n + 1), fold=np.arange(n) % 6 + 1))
    table = pd.DataFrame(dict(participant="sub-01", video_id=np.arange(1, n + 1), qc_row=np.arange(n)[::-1].copy()))
    cw = pd.Series({v: f"c{v}" for v in range(1, n + 1)})
    with tempfile.TemporaryDirectory() as td:
        roi = Path(td) / "roi.npz"
        np.savez(roi, roi=np.array(["a", "b"]), offsets=np.array([0, 3, 5]), columns=np.array([0, 1, 2, 2, 3]), n_columns=np.array(4))
        rec = Recorder(np.arange(n * 4, dtype=np.float32).reshape(n, 4) + np.random.default_rng(0).normal(size=(n, 4)).astype(np.float32))
        plan = S.plan_pilot(split, 1)
        keep = list(plan.train) + list(plan.val) + list(plan.test)
        b = S.load_brain_subset("01", split, keep, roi_file=roi, table=table, crosswalk=cw, mc72=[], raw=rec)
        test_ids = set(split.video_id[split.fold == 1].tolist())
        read_ids = {int(table.video_id[table.qc_row == r].iloc[0]) for r in rec.read}
        check("파일럿은 바깥 시험 영상의 뇌 반응을 읽지 않는다(Codex 1)", not (read_ids & test_ids) and len(plan.test) == 0 and set(b.video_id.tolist()) == set(keep))
        check("읽은 행이 영상과 맞게 붙는다", all(np.allclose(b.X[i], rec.a[int(table.qc_row[table.video_id == v].iloc[0])][[0, 1, 2, 3]]) for i, v in enumerate(b.video_id)))
        rec2 = Recorder(rec.a)
        outer = S.plan_outer(split, 1) if hasattr(S, "plan_outer") else None
        if outer is not None:
            S.load_brain_subset("01", split, list(outer.train) + list(outer.val) + list(outer.test), roi_file=roi, table=table, crosswalk=cw, mc72=[], raw=rec2)
            check("일반 바깥 평가는 시험 영상의 반응도 읽는다", {int(table.video_id[table.qc_row == r].iloc[0]) for r in rec2.read} >= test_ids)
        check("MC와 같은 내용이 표에 있으면 읽기 전에 멈춘다", stops(lambda: S.load_brain_subset("01", split, keep, roi_file=roi, table=table, crosswalk=cw, mc72=["c3"], raw=Recorder(rec.a))))
        bad = table.copy()
        bad.loc[0, "qc_row"] = -1
        check("음수 qc_row는 읽기 전에 멈춘다", stops(lambda: S.load_brain_subset("01", split, keep, roi_file=roi, table=bad, crosswalk=cw, mc72=[], raw=Recorder(rec.a))))


def t_stimulus_source():
    """Codex 2. S4 완료 기록과 입력을 대조한다."""
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "done.json"
        cur = {r: f"h_{r}" for r in S.STIMULUS_REQUIRED_ROLES}
        check("S4 완료 기록이 없으면 멈춘다(Codex 2)", stops(lambda: S.check_stimulus_source(p, 1, cur)))
        good = dict(task=dict(task="stimulus", k=1, name="fold1"), inputs=dict(cur), run_key="rk")
        p.write_text(json.dumps(good))
        check("입력이 같으면 S4 실행 번호를 돌려준다", S.check_stimulus_source(p, 1, cur) == "rk")
        p.write_text(json.dumps(dict(good, inputs=dict(cur, labels="old"))))
        check("S4가 쓴 사람 평정이 지금과 다르면 멈춘다(Codex 2)", stops(lambda: S.check_stimulus_source(p, 1, cur)))
        p.write_text(json.dumps(dict(good, task=dict(task="stimulus", k=2))))
        check("바깥 fold가 다르면 멈춘다", stops(lambda: S.check_stimulus_source(p, 1, cur)))
        p.write_text(json.dumps(dict(good, task=dict(task="noemo", k=1))))
        check("다른 S4 과제의 출력이면 멈춘다", stops(lambda: S.check_stimulus_source(p, 1, cur)))
        p.write_text(json.dumps(dict(good, inputs=dict(cur, other="x"))))
        check("지금 확인할 수 없는 S4 입력이 있으면 멈춘다", stops(lambda: S.check_stimulus_source(p, 1, cur)))
        no_labels = {r: h for r, h in cur.items() if r != "labels"}
        p.write_text(json.dumps(dict(good, inputs=no_labels)))
        check("S4 기록에 사람 평정 해시가 빠지면 멈춘다(Codex 50b4724)", stops(lambda: S.check_stimulus_source(p, 1, cur)))
        no_s2 = {r: h for r, h in cur.items() if r != "s2:fold_roles.tsv"}
        p.write_text(json.dumps(dict(good, inputs=no_s2)))
        check("S4 기록에 S2 표 해시가 빠지면 멈춘다(Codex 50b4724)", stops(lambda: S.check_stimulus_source(p, 1, cur)))
        p.write_text(json.dumps({k2: v2 for k2, v2 in good.items() if k2 != "inputs"}))
        check("S4 기록에 inputs 자체가 없으면 멈춘다(Codex 50b4724)", stops(lambda: S.check_stimulus_source(p, 1, cur)))
        check("필수 역할은 S4 stimulus 과제가 실제로 기록하는 역할과 같다", S.STIMULUS_REQUIRED_ROLES == {"visual_target", "caption_target", "labels"} | {f"s2:{q.name}" for q in c.S2_TABLES})
    check("S6 입력 목록에 S4 완료 기록이 들어간다", "stimulus_done" in S.input_paths(S.plan_pilot(pd.DataFrame(dict(video_id=np.arange(1, 25), fold=np.arange(24) % 6 + 1)), 1), participants=[]))


def t_split_files():
    """분할 목록 파일. 실제 목록은 두 표에서 다시 낸 것과 같고, 파일이 다르면 멈추고, 파일럿은 test.txt를 쓰지 않는다. video_id만 읽는다."""
    import s2_split_files as sf
    sets = sf.expected()
    check("manifests/s2/splits가 두 분할 표와 같다", sf.check(sets) == [])
    real = c.load_split()
    for k in range(1, 7):
        p, q = S.load_plan(f"outer_fold{k}", real), S.parse_plan(f"outer_fold{k}", real)
        check(f"outer_fold{k}는 목록 파일과 분할 표가 같다", (p.train, p.val, p.test) == tuple(sorted(x) for x in (q.train, q.val, q.test)))
    check("final_for_mc는 목록 파일과 분할 표가 같다", S.load_plan("final_for_mc", real).val == sorted(S.parse_plan("final_for_mc", real).val))
    pilot = S.load_plan("pilot_fold3", real)
    check("파일럿은 시험 목록이 비어 있다", pilot.test == [] and set(S.split_files(pilot)) == {"split:train", "split:val"})
    check("바깥 평가의 Run 입력에 목록 파일 세 개가 들어간다", {"split:train", "split:val", "split:test"} <= set(S.input_paths(S.load_plan("outer_fold2", real), participants=[])))
    with tempfile.TemporaryDirectory() as td:
        for name, parts in sets.items():
            (Path(td) / name).mkdir()
            for part, ids in parts.items():
                (Path(td) / name / f"{part}.txt").write_text("".join(f"{v}\n" for v in ids))
        check("복사한 목록으로도 같은 분할을 읽는다", S.load_plan("outer_fold1", real, splits=td).test == sets["outer_fold1"]["test"])
        moved = sets["outer_fold1"]["test"][0]
        (Path(td) / "outer_fold1/val.txt").write_text("".join(f"{v}\n" for v in sets["outer_fold1"]["val"] + [moved]))
        check("목록 파일이 분할 표와 다르면 멈춘다", stops(lambda: S.load_plan("outer_fold1", real, splits=td), (SystemExit,)))


def t_stimulus_shape():
    """Codex 3. 배열 크기가 다르면 복제하지 않고 멈춘다."""
    ids = np.arange(1, 17)
    pos = {int(v): i for i, v in enumerate(ids)}
    ok = S.stimulus_bank(dict(video_id=ids, p_clipped=np.full((16, 34), 0.3)), ids.tolist(), pos, (16, 34))
    check("정상 배열은 붙는다", ok.shape == (16, 34) and np.allclose(ok, 0.3))
    check("한 열만 있으면 멈춘다(Codex 3)", stops(lambda: S.stimulus_bank(dict(video_id=ids, p_clipped=np.full((16, 1), 0.3)), ids.tolist(), pos, (16, 34))))
    check("한 행만 있으면 멈춘다(Codex 3)", stops(lambda: S.stimulus_bank(dict(video_id=ids, p_clipped=np.full((1, 34), 0.3)), ids.tolist(), pos, (16, 34))))
    check("영상 ID가 중복이면 멈춘다", stops(lambda: S.stimulus_bank(dict(video_id=np.r_[ids[:-1], ids[:1]], p_clipped=np.full((16, 34), 0.3)), ids.tolist(), pos, (16, 34))))
    check("영상 ID가 정수가 아니면 멈춘다", stops(lambda: S.stimulus_bank(dict(video_id=ids.astype(float), p_clipped=np.full((16, 34), 0.3)), ids.tolist(), pos, (16, 34))))


def main():
    if "--timing" in sys.argv:
        timing()
        return
    started = time.time()
    for f in (t_read_boundary, t_split_files, t_stimulus_source, t_stimulus_shape, t_audition, t_structure, t_stop_gradient, t_gradient_allowed, t_s6_rules_1108, t_numeric_divergence, t_prelim_config, t_featdec_independent, t_interaction_index, t_distill_formula, t_boundaries, t_load_known, t_shuffle, t_standardization, t_early_stop, t_input_only, t_weight_groups, t_candidates, t_selection, t_representation_unit, t_pipeline, t_zero_selected, t_guard):
        t0 = time.time()
        try:
            f()
        except Exception as e:  # 시험 묶음이 끝까지 돌도록 예외도 실패로 센다
            import traceback
            traceback.print_exc()
            check(f"{f.__name__} 예외: {type(e).__name__}: {e}", False)
        print(f"-- {f.__name__} {time.time() - t0:.1f}초", flush=True)
    bad = [n for n, ok in RESULTS if not ok]
    print("통과", len(RESULTS) - len(bad), "실패", len(bad), bad)
    print(f"전체 {time.time() - started:.1f}초")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
