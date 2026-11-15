#!/usr/bin/env python3
"""S9 경로 평가(K1, K1a)와 S10 K1, 14개 차원 표의 합성 자료 시험 (2026-11-15). 실제 정답, 실제 예측, 실제 특징, GPU를 쓰지 않는다. 결과 폴더는 임시 폴더에 만든다.
S4 head와 시험 출력은 S4 코드(s4_feature_model의 FeatureModel, Coordinates, save_state, predict)로 만들고, 확인은 head 가중치로 직접 낸 손 계산과 비교한다.
시험: decoded features의 눈금 바꾸기(ridge 원래 척도, C-1 학습 fold 4개 눈금 -> K1 head D_k 눈금), K1과 K1a head 출력, K1a의 1~9점 되돌리기,
N8 보정(검증 fold 통계, 평균만 옮기는 차원, 시험 fold를 쓰지 않음), head 출처 확인(저장된 S4 출력, 판의 rank, K1a 눈금), 빠진 입력 거절과 점검용 표시,
S10 K1(정서별 r, 같은 seed 짝, ridge판의 A-1 seed마다 짝, BH 묶음), 14개 차원 표((1), (2), (3)과 (3) − (1), [미확인] 칸, seed 요약), 출처 대조(S9 출력 해시, S4, S6 plan).
사용(레포 최상위): python tests/s10_k1_tests.py
"""
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1] / "src"))  # 코드는 src에 있다
_sys.dont_write_bytecode = True
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "4")
import numpy as np
import pandas as pd
import torch

import s4_common as c
import s4_feature_model as fm
import s10_inputs as I
import s10_stats as st
import s9_path_eval as pe
import s10_k1 as K

RESULTS = []
N_EMO, N_DIM = 34, 14
EMOTIONS = [f"emo{e}" for e in range(N_EMO)]
PIDS = ["sub-01", "sub-02"]
SEEDS = (0, 1, 2)
DV, DC = I.DIMS["vision"], I.DIMS["caption"]
N_BOOT = 40


def check(name, ok):
    RESULTS.append((name, bool(ok)))
    print("통과" if ok else "실패", name, flush=True)


def raises(fn, exc=(ValueError, SystemExit), text=None):
    try:
        fn()
    except exc as e:
        return text is None or text in str(e)
    return False


def fake_split():
    """fold 6개, fold마다 run 2개, run마다 영상 6개(72개)."""
    rows, vid = [], 1
    for k in range(1, 7):
        for j in range(2):
            run = (k - 1) * 2 + j + 1
            for _ in range(6):
                rows.append(dict(split_id="fake", video_id=vid, content_id=vid, canonical_id=vid, run_index=run, run_group=run, fold=k))
                vid += 1
    return pd.DataFrame(rows)


SPLIT = fake_split()
FOLD_OF = dict(zip(SPLIT.video_id, SPLIT.fold))
MISSING_02 = [3, 20, 50]  # sub-02에 없는 영상
PVIDEOS = {"sub-01": SPLIT.video_id.to_numpy(), "sub-02": np.array([v for v in SPLIT.video_id if v not in MISSING_02])}
RNG = np.random.default_rng(5)
FEAT = (RNG.standard_normal((len(SPLIT), DV + DC)) * 0.5 + 0.3).astype(np.float32)
Y_EMO = RNG.random((len(SPLIT), N_EMO)) * (RNG.random((len(SPLIT), N_EMO)) < 0.7)
Y_DIM = 1 + 8 * RNG.random((len(SPLIT), N_DIM))


def fake_features(split, ids):
    at = np.asarray(ids) - 1
    return {"vision": FEAT[at, :DV], "caption": FEAT[at, DV:]}


I.actual_features = fake_features  # 실제 S3 파일을 읽지 않는다
TMP = Path(tempfile.mkdtemp(prefix="s10_k1_tests_"))


def manual_head(state, xh):
    """head 가중치로 직접 낸 출력(K1 head D_k 눈금 입력). FeatureModel을 쓰지 않는다."""
    w = {k: v.double().numpy() for k, v in state["state_dict"].items()}
    v, cap = xh[:, :DV], xh[:, DV:]
    z = v @ w["a.weight"].T + w["a.bias"] + cap @ w["b.weight"].T + w["b.bias"]
    if int(state["r"]):
        z = z + ((v @ w["A.weight"].T) * (cap @ w["B.weight"].T)) @ w["U.weight"].T
    return z


def head_coords(coord):
    return np.concatenate([coord["visual_mean"], coord["caption_mean"]]), np.concatenate([coord["visual_std"], coord["caption_std"]])


# 합성 S4, S5, S6

def build_s4(root, ranks=(0, 2), k1a_coord_shift=False):
    ids, folds = SPLIT.video_id.to_numpy(), SPLIT.fold.to_numpy()
    for task, kind, n_out, y in (("stimulus", "emotions", N_EMO, Y_EMO), ("k1a", "dimensions", N_DIM, Y_DIM)):
        spec = fm.Spec(kind=kind)
        d = fm.Data(ids, folds, FEAT[:, :DV], FEAT[:, DV:], y.astype(np.float32))
        for k in range(1, 7):
            out = root / task / f"fold{k}"
            out.mkdir(parents=True)
            dk = d.mask([f for f in range(1, 7) if f != k])
            coord = fm.Coordinates(d.v[dk], d.cap[dk], d.y[dk] if task == "k1a" else None)
            if task == "k1a" and k1a_coord_shift and k == 3:
                coord.vm = coord.vm + 1e-3  # K1 head와 다른 입력 눈금
            np.savez(out / "coordinates.npz", **coord.arrays())
            te = d.mask([k])
            pred = {"video_id": d.ids[te]}
            for h, r in zip(("additive", "interaction"), ranks):
                torch.manual_seed(100 * k + r + (7 if task == "k1a" else 0))
                model = fm.FeatureModel(DV, DC, n_out, r)
                with torch.no_grad():
                    for p in model.parameters():
                        p.mul_(3.0)
                row = pd.Series(dict(r=r, weight_decay=1e-3, lr=1e-4, epochs=10))
                fm.save_state(out / f"head_{h}.pt", model, row, coord)
                z, p_ = fm.predict(spec, model, d, coord, te, "cpu")
                if task == "stimulus":
                    pred[f"{h}_logit"], pred[f"{h}_p"] = z, p_
                else:
                    pred[f"{h}_z"], pred[f"{h}_score"] = z, z * coord.ys + coord.ym
            if task == "stimulus":
                pred["logit"], pred["p"] = pred["additive_logit"], pred["additive_p"]
            np.savez(out / "test_pred.npz", **pred)
            (out / "done.json").write_text(json.dumps(dict(task=dict(task=task, k=k, name=f"fold{k}"))))


def ridge_decoded(q, ids, salt):
    """ridge decoded features(원래 척도): 실제 특징을 줄이고 잡음을 더한 값. 참가자와 용도마다 다르다."""
    rng = np.random.default_rng(1000 * PIDS.index(q) + salt)
    x = 0.4 * FEAT[np.asarray(ids) - 1].astype(np.float64) + 0.2 + rng.standard_normal((len(ids), DV + DC)) * 0.3
    x[:, 7] = 1e-4 * rng.standard_normal(len(ids)) + 2.0  # 분산이 아주 작은 Vision 차원(O35)
    return x


def split_layers(x):
    arrs = {}
    for i, n in enumerate(pe.VISION_LAYERS):
        arrs[n] = x[:, i * 1408:(i + 1) * 1408].astype(np.float32)
    for i, n in enumerate(pe.CAPTION_LAYERS):
        arrs[n] = x[:, DV + i * 1024:DV + (i + 1) * 1024].astype(np.float32)
    return arrs


def build_s5(root):
    for q in PIDS:
        for k in range(1, 7):
            d = root / f"{q}_fold{k}"
            d.mkdir(parents=True)
            vt = np.array([v for v in PVIDEOS[q] if FOLD_OF[v] == k])
            np.savez(d / "test_pred.npz", video_id=vt, **split_layers(ridge_decoded(q, vt, k)))
            dk = [f for f in range(1, 7) if f != k]
            vo = np.concatenate([[v for v in PVIDEOS[q] if FOLD_OF[v] == j] for j in dk]).astype(np.int64)
            fo = np.array([FOLD_OF[v] for v in vo])
            xo = np.concatenate([ridge_decoded(q, vo[fo == j], 50 + 10 * k + j) for j in dk])
            np.savez(d / "inner_oof_target.npz", video_id=vo, inner_fold=fo, **split_layers(xo))
            (d / "done.json").write_text("{}")


def c1_decoded(q, ids, seed, salt):
    rng = np.random.default_rng(7000 + 100 * seed + 10 * PIDS.index(q) + salt)
    return 0.5 * FEAT[np.asarray(ids) - 1].astype(np.float64) - 0.1 + rng.standard_normal((len(ids), DV + DC)) * 0.4


def a1_pred(ids, seed, salt):
    rng = np.random.default_rng(9000 + 10 * seed + salt)
    return np.clip(Y_EMO[np.asarray(ids) - 1] * 0.5 + rng.random((len(ids), N_EMO)) * 0.3, 0, 1)


def build_s6(root, seeds=SEEDS, a1_seeds=SEEDS):
    for k in range(1, 7):
        fo = root / f"outer_fold{k}"
        (fo / "plan").mkdir(parents=True)
        val = k % 6 + 1
        pid, vid, role = [], [], []
        for q in PIDS:
            for v in PVIDEOS[q]:
                pid.append(q), vid.append(int(v)), role.append(2 if FOLD_OF[v] == k else 1 if FOLD_OF[v] == val else 0)
        np.savez(fo / "plan" / "rows.npz", participant=np.array(pid), video_id=np.array(vid), role=np.array(role))
        tr = np.array([v for v in SPLIT.video_id if FOLD_OF[v] not in (k, val)])
        f = FEAT[tr - 1].astype(np.float64)
        m, s = f.mean(0), f.std(0)
        np.savez(fo / "plan" / "standardization.npz", visual_mean=m[:DV], visual_std=s[:DV], caption_mean=m[DV:], caption_std=s[DV:])
        for cond, sd_list in (("brain_decoded", seeds), ("brain_only", a1_seeds)):
            (fo / cond).mkdir()
            seeds_map = {}
            for sd in sd_list:
                rel = f"{cond}/cand_seed{sd}"
                d = fo / rel
                (d / "outputs").mkdir(parents=True)
                (d / "done.json").write_text("{}")
                seeds_map[str(sd)] = rel
                if cond == "brain_decoded":
                    for which, wanted in (("test", 2), ("val", 1)):
                        pp, vv, xs = [], [], []
                        for q in PIDS:
                            ids = np.array([v for v in PVIDEOS[q] if (FOLD_OF[v] == k if wanted == 2 else FOLD_OF[v] == val)])
                            x = (c1_decoded(q, ids, sd, k + (0 if wanted == 2 else 20)) - m) / s  # 학습 fold 4개의 D9 눈금으로 저장
                            pp.append(np.full(len(ids), q)), vv.append(ids), xs.append(x)
                        x = np.concatenate(xs)
                        np.savez(d / "outputs" / f"decoded_{which}.npz", participant=np.concatenate(pp), video_id=np.concatenate(vv), v_hat=x[:, :DV].astype(np.float32), c_hat=x[:, DV:].astype(np.float32))
                    (d / "outputs" / "done.json").write_text("{}")
                else:
                    pp, vv, ps = [], [], []
                    for q in PIDS:
                        ids = np.array([v for v in PVIDEOS[q] if FOLD_OF[v] == k])
                        pp.append(np.full(len(ids), q)), vv.append(ids), ps.append(a1_pred(ids, sd, k + 3 * PIDS.index(q)))
                    np.savez(d / "test_pred.npz", participant=np.concatenate(pp), video_id=np.concatenate(vv), p=np.concatenate(ps))
            (fo / cond / "selected.json").write_text(json.dumps(dict(condition=cond, seeds=seeds_map, zero_selected=False)))


def build_b4(root):
    for q in PIDS:
        for k in range(1, 7):
            d = root / f"{q}_fold{k}"
            d.mkdir(parents=True)
            vt = np.array([v for v in PVIDEOS[q] if FOLD_OF[v] == k])
            rng = np.random.default_rng(300 + 10 * k + PIDS.index(q))
            np.savez(d / "pred.npz", video_id=vt, dimension_main=Y_DIM[vt - 1] * 0.3 + rng.standard_normal((len(vt), N_DIM)))
            (d / "done.json").write_text("{}")


S4, S5, S6, B4 = TMP / "s4", TMP / "s5", TMP / "s6", TMP / "ridge"
build_s4(S4)
build_s5(S5)
build_s6(S6)
build_b4(B4)


def s9(out, s4=S4, s5=S5, s6=S6, **kw):
    return pe.run(s4, s5, s6, out, SPLIT, pvideos=PVIDEOS, **kw)


def s10(s9_dir, out, s4=S4, s6=S6, **kw):
    return K.run(s9_dir, s6, B4, s4, out, SPLIT, Y_EMO, Y_DIM, EMOTIONS, n_boot=N_BOOT, pvideos=PVIDEOS, **kw)


# S9

def t_s9():
    s9(TMP / "pe")
    done = json.loads((TMP / "pe" / "done.json").read_text())
    check("S9 단위: ridge 6 fold와 C-1 seed 3개 × 6 fold, 점검용 표시 없음", len(done["units"]) == 6 + 18 and not done["partial_check"])
    k, q = 2, "sub-02"
    val = k % 6 + 1
    coord = dict(np.load(S4 / "stimulus" / f"fold{k}" / "coordinates.npz"))
    hm, hs = head_coords(coord)
    st_add = torch.load(S4 / "stimulus" / f"fold{k}" / "head_additive.pt", weights_only=True)
    st_int = torch.load(S4 / "stimulus" / f"fold{k}" / "head_interaction.pt", weights_only=True)
    u = np.load(TMP / "pe" / "units" / f"ridge_fold{k}.npz")
    m = u["participant"] == q
    vt = u["video_id"][m]
    x = ridge_decoded(q, vt, k)
    xh = (x - hm) / hs
    check("ridge 시험 영상 = 그 참가자의 fold block 영상", np.array_equal(vt, [v for v in PVIDEOS[q] if FOLD_OF[v] == k]))
    check("K1 보정 전(ridge): 원래 척도 -> K1 head D_k 눈금 -> 더하기 head = 손 계산", np.allclose(u["k1_additive_uncorrected_logit"][m], manual_head(st_add, xh), atol=2e-3, rtol=1e-4))
    check("K1 상호작용 head의 확률 = sigmoid(손 계산)", np.allclose(u["k1_interaction_uncorrected_p"][m], 1 / (1 + np.exp(-manual_head(st_int, xh))), atol=2e-4))
    vv = np.array([v for v in PVIDEOS[q] if FOLD_OF[v] == val])
    dk = [f for f in range(1, 7) if f != k]
    xo = np.concatenate([ridge_decoded(q, [v for v in PVIDEOS[q] if FOLD_OF[v] == j], 50 + 10 * k + j) for j in dk])
    vo = np.concatenate([[v for v in PVIDEOS[q] if FOLD_OF[v] == j] for j in dk])
    dv = (xo[np.isin(vo, vv)] - hm) / hs
    av = (FEAT[vv - 1].astype(np.float64) - hm) / hs
    mu_hat, sd_hat, mu, sd = dv.mean(0), dv.std(0), av.mean(0), av.std(0)
    shift = np.zeros(DV + DC, bool)
    shift[:DV] = sd_hat[:DV] < 0.01 * np.median(sd_hat[:DV])
    shift[DV:] = sd_hat[DV:] < 0.01 * np.median(sd_hat[DV:])
    corr = np.where(shift, xh - mu_hat + mu, mu + sd / np.where(shift, 1, sd_hat) * (xh - mu_hat))
    pi = list(u["n8_participant"]).index(q)
    check("N8 통계는 H2 검증 fold의 안쪽 fold 밖 ridge 예측과 같은 영상의 실제 특징(O34)", np.allclose(u["n8_mu_hat"][pi], mu_hat) and np.allclose(u["n8_sd"][pi], sd))
    check("O35 평균만 옮기는 차원: 분산이 아주 작은 Vision 차원 하나", u["n8_shift_only"][pi].sum() == 1 and u["n8_shift_only"][pi][7] == shift[7] == True)
    check("K1 보정판(ridge) = 보정한 입력의 손 계산", np.allclose(u["k1_additive_corrected_logit"][m], manual_head(st_add, corr), atol=2e-3, rtol=1e-4))
    n8c = pd.read_csv(TMP / "pe" / "n8_counts.tsv", sep="\t")
    row = n8c[(n8c.source == "ridge") & (n8c.fold == k) & (n8c.participant == q) & (n8c.target == "vision")].iloc[0]
    check("n8_counts.tsv에 평균만 옮긴 차원 수와 검증 영상 수", row.n_shift_only == 1 and row.n_val_videos == len(vv))
    ka = dict(np.load(S4 / "k1a" / f"fold{k}" / "coordinates.npz"))
    ka_int = torch.load(S4 / "k1a" / f"fold{k}" / "head_interaction.pt", weights_only=True)
    zc = manual_head(ka_int, corr)
    check("K1a 보정판 1~9점 = z × target_std + target_mean(04 S9)", np.allclose(u["k1a_interaction_corrected_score"][m], zc * ka["target_std"] + ka["target_mean"], atol=5e-3, rtol=1e-4)
          and np.allclose(u["k1a_interaction_corrected_z"][m], zc, atol=2e-3, rtol=1e-4))
    # C-1: 학습 fold 4개의 D9 눈금으로 저장된 값을 원래 척도로 되돌린 뒤 K1 head 눈금으로
    seed = 1
    u1 = np.load(TMP / "pe" / "units" / f"c1_seed{seed}_fold{k}.npz")
    m1 = u1["participant"] == q
    v1 = u1["video_id"][m1]
    xc = c1_decoded(q, v1, seed, k)
    xs = np.load(S6 / f"outer_fold{k}" / "plan" / "standardization.npz")
    xc32 = ((xc - np.concatenate([xs["visual_mean"], xs["caption_mean"]])) / np.concatenate([xs["visual_std"], xs["caption_std"]])).astype(np.float32)
    xc_back = xc32.astype(np.float64) * np.concatenate([xs["visual_std"], xs["caption_std"]]) + np.concatenate([xs["visual_mean"], xs["caption_mean"]])
    check("K1 보정 전(C-1): 학습 fold 4개 눈금 -> 원래 척도 -> K1 head 눈금(N3, O20)", np.allclose(u1["k1_interaction_uncorrected_logit"][m1], manual_head(st_int, (xc_back - hm) / hs), atol=2e-3, rtol=1e-4))
    vv1 = np.array([v for v in PVIDEOS[q] if FOLD_OF[v] == val])
    xcv = c1_decoded(q, vv1, seed, k + 20)
    pi1 = list(u1["n8_participant"]).index(q)
    check("C-1 N8 통계는 그 seed의 decoded_val(H2 검증 fold)에서(O34)", np.allclose(u1["n8_mu_hat"][pi1], ((xcv - hm) / hs).mean(0), atol=1e-4))
    hc = pd.read_csv(TMP / "pe" / "head_check.tsv", sep="\t")
    check("head 확인: 6 fold × K1, K1a × 두 판, S4 저장 출력과 같다", len(hc) == 24 and (hc.max_abs_diff <= pe.HEAD_CHECK_TOL).all())


def t_s9_guards():
    bad = TMP / "s4_bad"
    shutil.copytree(S4, bad)
    z = dict(np.load(bad / "stimulus" / "fold4" / "test_pred.npz"))
    z["interaction_logit"] = z["interaction_logit"] + 0.01
    np.savez(bad / "stimulus" / "fold4" / "test_pred.npz", **z)
    check("읽은 head가 S4 저장 시험 출력과 다르면 멈춘다", raises(lambda: s9(TMP / "pe_bad1", s4=bad), text="S4가 저장한 시험 출력과 다르다"))
    bad2 = TMP / "s4_rank"
    build_s4(bad2, ranks=(2, 4))
    check("더하기판 head의 rank가 0이 아니면 멈춘다(O17)", raises(lambda: s9(TMP / "pe_bad2", s4=bad2), text="O17"))
    bad3 = TMP / "s4_coord"
    build_s4(bad3, k1a_coord_shift=True)
    check("K1a 입력 눈금이 K1 head와 다르면 멈춘다(04 S4)", raises(lambda: s9(TMP / "pe_bad3", s4=bad3), text="K1a Stimulus Model의 입력 눈금"))
    s6b = TMP / "s6_two_seeds"
    build_s6(s6b, seeds=(0, 1))
    check("C-1 seed 2가 없으면 결과를 내지 않는다(G14)", raises(lambda: s9(TMP / "pe_b", s6=s6b), text="빠진 입력"))
    s9(TMP / "pe_partial", s6=s6b, partial_check=True)
    done = json.loads((TMP / "pe_partial" / "done.json").read_text())
    check("--partial-check는 있는 단위만 내고 점검용으로 표시한다", done["partial_check"] and done["note"] == I.PARTIAL_NOTE and len(done["units"]) == 6 + 12
          and (pd.read_csv(TMP / "pe_partial" / "missing.tsv", sep="\t").seed == 2).all())
    check("S10은 점검용 S9 결과를 --partial-check 없이 읽지 않는다", raises(lambda: s10(TMP / "pe_partial", TMP / "k1_p"), text="점검용"))
    s5b = TMP / "s5_val"
    shutil.copytree(S5, s5b)
    z = dict(np.load(s5b / "sub-01_fold5" / "inner_oof_target.npz"))
    keep = ~((z["inner_fold"] == 6) & (np.arange(len(z["inner_fold"])) % 5 == 0))
    np.savez(s5b / "sub-01_fold5" / "inner_oof_target.npz", **{n: a[keep] for n, a in z.items()})
    check("ridge 검증 fold 영상이 그 참가자의 block 영상과 다르면 멈춘다", raises(lambda: s9(TMP / "pe_bad4", s5=s5b), text="검증 fold 6"))


# S10

def t_k1():
    s10(TMP / "pe", TMP / "k1")
    sc = pd.read_csv(TMP / "k1" / "k1_scores.tsv", sep="\t")
    per = pd.read_csv(TMP / "k1" / "k1_per_emotion.tsv", sep="\t")
    q, seed = "sub-02", 1
    vids = np.array(sorted(PVIDEOS[q]))
    a1 = np.concatenate([a1_pred([v for v in PVIDEOS[q] if FOLD_OF[v] == k], seed, k + 3) for k in range(1, 7)])
    order = np.argsort(np.concatenate([[v for v in PVIDEOS[q] if FOLD_OF[v] == k] for k in range(1, 7)]))
    r_a1 = st.pearson_columns(Y_EMO[vids - 1], a1[order])
    got = per[(per.source == "A-1") & (per.seed == seed) & (per.participant == q)].sort_values("emotion", key=lambda s: s.str[3:].astype(int)).r.to_numpy()
    check("K1 A-1 정서별 r = 6 fold를 모은 r(2-3)", np.allclose(got, r_a1, equal_nan=True))
    path = []
    for k in range(1, 7):
        u = np.load(TMP / "pe" / "units" / f"c1_seed{seed}_fold{k}.npz")
        m = u["participant"] == q
        path.append((u["video_id"][m], u["k1_additive_corrected_p"][m]))
    pv = np.concatenate([a for a, _ in path])
    pp = np.concatenate([b for _, b in path])[np.argsort(pv)]
    r_path = st.pearson_columns(Y_EMO[vids - 1], pp)
    got = per[(per.source == "C-1") & (per["head"] == "additive") & (per.calibration == "corrected") & (per.seed == seed) & (per.participant == q)]
    check("K1 경로 평가(C-1, 더하기, 보정판) 정서별 r", np.allclose(got.sort_values("emotion", key=lambda s: s.str[3:].astype(int)).r.to_numpy(), r_path, equal_nan=True))
    d = pd.read_csv(TMP / "k1" / "k1_differences.tsv", sep="\t")
    row = d[(d.source == "C-1") & (d["head"] == "additive") & (d.calibration == "corrected") & (d.seed == seed) & (d.participant == q)]
    keep = np.isfinite(r_path)
    check("K1 차이는 같은 seed의 A-1과 짝(점수 차이 = 정서 r 평균의 차이)", len(row) == 1 and row.a1_seed.iloc[0] == seed and np.isclose(row.estimate.iloc[0], r_path[keep].mean() - r_a1[keep].mean()))
    rr = d[(d.source == "ridge") & (d["head"] == "interaction") & (d.calibration == "uncorrected") & (d.participant == q)]
    check("K1 ridge판은 A-1의 seed마다 짝짓는다", sorted(rr.a1_seed.tolist()) == list(SEEDS))
    check("K1 차이에 구간과 p가 있고 비율 열이 없다(K1, N6)", d.ci_low.notna().all() and d.p_raw.between(0, 1).all() and not any(col.startswith(("ratio", "pct", "percent", "share")) for col in d.columns))
    de = pd.read_csv(TMP / "k1" / "k1_differences_per_emotion.tsv", sep="\t")
    g = de[(de.comparison == row.comparison.iloc[0]) & (de.participant == q)]
    check("K1 정서별 차이: BH 묶음은 참가자마다, 비교마다 34개(I9)", len(g) == N_EMO and (g.family_size == np.isfinite(g.p_raw).sum()).all() and np.allclose(g.p_bh, st.bh(g.p_raw.to_numpy()), equal_nan=True))
    ss = pd.read_csv(TMP / "k1" / "k1_seed_summary.tsv", sep="\t")
    check("K1 seed 요약: A-1과 C-1 점수, 차이의 seed 3개 평균과 표준편차(G14)", (ss[ss.source.isin(["A-1", "C-1"])].n_seeds == 3).all() and set(ss.what) == {"점수", "차이(경로 평가 − A-1)"})
    n8 = pd.read_csv(TMP / "k1" / "n8_shift_only.tsv", sep="\t")
    check("O35 평균만 옮긴 차원 수 표가 S10 출력에 있다", {"source", "seed", "fold", "participant", "target", "n_shift_only"} <= set(n8.columns))


def t_dimensions():
    t = pd.read_csv(TMP / "k1" / "dimensions14.tsv", sep="\t")
    check("14개 차원 표 하나에 (1) B4, (2) 실제 특징, (3) decoded features", set(t.source) == {"B4", "Stimulus", "ridge", "C-1"} and set(t.dimension) == set(c.DIMENSIONS)
          and (t.rating_reliability == "[미확인]").all())
    q = "sub-01"
    vids = np.array(sorted(PVIDEOS[q]))
    b4 = np.concatenate([np.load(B4 / f"{q}_fold{k}" / "pred.npz")["dimension_main"] for k in range(1, 7)])
    r_b4 = st.pearson_columns(Y_DIM[vids - 1], b4)
    got = t[(t.source == "B4") & (t.participant == q)].set_index("dimension").loc[list(c.DIMENSIONS)].r.to_numpy()
    check("(1) B4 ridge 차원별 r = dimension_main을 모은 r", np.allclose(got, r_b4))
    stim = np.concatenate([np.load(S4 / "k1a" / f"fold{k}" / "test_pred.npz")["interaction_score"] for k in range(1, 7)])
    got = t[(t.source == "Stimulus") & (t["head"] == "interaction") & (t.participant == q)].set_index("dimension").loc[list(c.DIMENSIONS)].r.to_numpy()
    check("(2) 실제 특징 Stimulus Model은 그 참가자의 시험 영상에서 낸다", np.allclose(got, st.pearson_columns(Y_DIM[vids - 1], stim[vids - 1])))
    path = np.concatenate([np.load(TMP / "pe" / "units" / f"ridge_fold{k}.npz")["k1a_additive_uncorrected_score"][np.load(TMP / "pe" / "units" / f"ridge_fold{k}.npz")["participant"] == q] for k in range(1, 7)])
    r_p = st.pearson_columns(Y_DIM[vids - 1], path)
    row = t[(t.source == "ridge") & (t["head"] == "additive") & (t.calibration == "uncorrected") & (t.participant == q)].set_index("dimension").loc[list(c.DIMENSIONS)]
    check("(3) − (1) 차이 = 같은 참가자, 같은 영상의 r 차이", np.allclose(row.r.to_numpy(), r_p) and np.allclose(row.diff_vs_b4.to_numpy(), r_p - r_b4))
    check("(3)의 BH 묶음은 참가자마다, 비교마다 14개 차원", (row.bh_family_size == N_DIM).all() and np.allclose(row.p_bh.to_numpy(), st.bh(row.p_raw.to_numpy())) and (row.label == K.EXPLORATORY).all())
    check("(1), (2) 행에는 차이 칸이 비어 있다", t[t.source.isin(["B4", "Stimulus"])].diff_vs_b4.isna().all())
    check("C-1판은 seed마다 행이 있다", sorted(t[t.source == "C-1"].seed.dropna().unique().astype(int).tolist()) == list(SEEDS))
    ss = pd.read_csv(TMP / "k1" / "dimensions14_seed_summary.tsv", sep="\t")
    check("14개 차원 seed 요약(C-1판, r와 (1)과의 차이)", (ss.n_seeds == 3).all() and {"r_mean", "r_sd", "diff_vs_b4_mean", "diff_vs_b4_sd"} <= set(ss.columns))


def t_s10_guards():
    pe_t = TMP / "pe_tamper"
    shutil.copytree(TMP / "pe", pe_t)
    z = dict(np.load(pe_t / "units" / "ridge_fold1.npz"))
    z["k1_additive_uncorrected_p"] = z["k1_additive_uncorrected_p"] * 0.9
    np.savez(pe_t / "units" / "ridge_fold1.npz", **z)
    check("S9 출력이 done.json의 sha256과 다르면 읽지 않는다", raises(lambda: s10(pe_t, TMP / "k1_t"), text="sha256"))
    s4o = TMP / "s4_other"
    build_s4(s4o)
    z = dict(np.load(s4o / "k1a" / "fold2" / "test_pred.npz"))
    z["additive_score"] = z["additive_score"] + 1.0
    np.savez(s4o / "k1a" / "fold2" / "test_pred.npz", **z)
    check("S9가 읽은 것과 다른 S4 결과를 주면 멈춘다", raises(lambda: s10(TMP / "pe", TMP / "k1_s4", s4=s4o), text="S9가 읽은 K1a 시험 예측과 다르다"))
    s6o = TMP / "s6_other"
    build_s6(s6o)
    z = dict(np.load(s6o / "outer_fold3" / "plan" / "rows.npz"))
    z["role"] = z["role"].copy()
    z["role"][0] = 0 if z["role"][0] != 0 else 1
    np.savez(s6o / "outer_fold3" / "plan" / "rows.npz", **z)
    check("S9가 쓴 것과 다른 S6 plan이면 멈춘다", raises(lambda: s10(TMP / "pe", TMP / "k1_s6", s6=s6o), text="plan/rows.npz"))
    s6a = TMP / "s6_a1two"
    build_s6(s6a, a1_seeds=(0, 1))
    s9(TMP / "pe_a1two", s6=s6a)
    check("A-1 seed 2가 없으면 최종 표를 내지 않는다", raises(lambda: s10(TMP / "pe_a1two", TMP / "k1_a", s6=s6a), text="빠진 입력"))
    s10(TMP / "pe_a1two", TMP / "k1_a2", s6=s6a, partial_check=True)
    info = json.loads((TMP / "k1_a2" / "run_info.json").read_text())
    d = pd.read_csv(TMP / "k1_a2" / "k1_differences.tsv", sep="\t")
    check("--partial-check: 있는 seed로만 계산하고 점검용으로 표시한다", info["note"] == I.PARTIAL_NOTE and info["a1_seeds"] == [0, 1] and set(d[d.source == "C-1"].seed.astype(int)) == {0, 1})


def main():
    for f in (t_s9, t_s9_guards, t_k1, t_dimensions, t_s10_guards):
        f()
    shutil.rmtree(TMP, ignore_errors=True)
    bad = [n for n, ok in RESULTS if not ok]
    print("통과", len(RESULTS) - len(bad), "실패", len(bad), bad)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
