#!/usr/bin/env python3
"""src/s8_mc_transfer.py 합성 시험 (2026-11-15). 실제 MC 반응, 사람 평정, GPU를 쓰지 않는다.
시험: 공유 가중치 고정과 입력층만 학습, 후보와 lr × weight decay 제외, 시험 반응의 반복 평균, 빠진 run 행을 읽지 않음,
MC 72개가 학습에 섞이면 멈춤, 반복 수가 표와 다르면 멈춤, 검증 r로 고르고 후보별 시험 예측 저장.
11/17: D 묶음(D-1, D-3, D-4). encoder 2 입력층만 feature 손실로 맞추고 검증 feature MSE로 고름, 정서 head는 HK 값 그대로, encoder 2 캐시를 D-1과 D-3이 함께 씀,
D-4는 짝 예측 평균, D-1은 정서 encoder 입력층만 맞춤, encoder 2가 다르면 캐시에서 멈춤.
사용(src에서): python ../tests/s8_tests.py
"""
import sys as _sys
_sys.dont_write_bytecode = True
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.getcwd())
import numpy as np
import pandas as pd
import torch

import s6_common as S
import s6_model as M
import s8_mc_transfer as X

RESULTS = []


def check(name, ok):
    RESULTS.append((name, bool(ok)))
    print(("통과 " if ok else "실패 ") + name, flush=True)


def stops(f):
    try:
        f()
    except (ValueError, SystemExit):
        return True
    return False


def hk_model(decoded):
    torch.manual_seed(0)
    return M.BrainModel({"sub-01": [5, 7, 3], "sub-02": [4, 6, 5]}, 8, feature_head=decoded, decoded=decoded, rank=1 if decoded else None, tokenizer="linear", voxel_sampling=0.375).eval()


def tables():
    """참가자 sub-01. 학습 6영상, 검증 4영상, 시험 72영상(2~3회 반복), 빠진 run 2행."""
    rows, q = [], 0
    for v in range(101, 107):
        rows.append(("sub-01", v, v, q, "s", 0, "train", 1, "input_train")); q += 1
    for v in range(107, 111):
        rows.append(("sub-01", v, v, q, "s", 0, "train", 1, "input_val")); q += 1
    reps = {}
    for v in range(1, 73):
        reps[v] = 2 + (v % 2)
        for r in range(reps[v]):
            rows.append(("sub-01", v, v, q, "t", 1, "test", r + 1, "test_72")); q += 1
    for v in (1, 2):
        rows.append(("sub-01", v, v, q, "s", 9, "train", 1, "excluded_test_runs")); q += 1
    blocks = pd.DataFrame(rows, columns=["participant", "video_id", "canonical_id", "qc_row", "session", "run_index", "part", "rep", "role"])
    repeats = pd.DataFrame([("sub-01", v, v, n) for v, n in reps.items()], columns=["participant", "video_id", "canonical_id", "n_repeats"])
    idmap = pd.DataFrame([(v, v, np.nan if v <= 72 else v, str(v), v <= 72) for v in list(range(1, 73)) + list(range(101, 111))],
                         columns=["mc_video_id", "canonical_id", "hk_dev_video_id", "hk_analysis_video_ids", "is_mc_test_72"])
    return blocks, repeats, idmap, q


def encoder2(seed):
    torch.manual_seed(seed)
    return M.BrainModel({"sub-01": [5, 7, 3], "sub-02": [4, 6, 5]}, 8, feature_head=True, decoded=False, rank=None, tokenizer="linear", voxel_sampling=0.375).eval()


def d_group(fd, spec, tmp, g):
    """11/17. D-1, D-3, D-4의 MC 전이."""
    import copy
    fe_cand = dict(d=8, input_wd=100.0, lr=1e-3, lam=None, alpha=None, rank=None, feature_wd=None)
    fe = encoder2(1)
    out = tmp / "enc"
    out.mkdir()
    fitted, wd = X.fit_encoder2(fe, fe_cand, 0, "mc-01", fd, spec, out, log=lambda m: None)
    sel = pd.read_csv(out / "selection.tsv", sep="\t").dropna(subset=["val_score"])
    check("encoder 2 입력층 후보 다섯, 검증 feature MSE가 가장 낮은 값을 고른다", len(pd.read_csv(out / "selection.tsv", sep="\t")) == 5 and wd == sel.sort_values(["val_score", "input_wd"], ascending=[False, True]).input_wd.iloc[0])
    check("encoder 2는 MC 입력층 W, b만 바뀌고 나머지는 HK 값이다", set(torch.load(out / "input_layer.pt")) == {"input_layer.weights.mc-01", "input_layer.input_bias.mc-01"}
          and all(torch.equal(v, fe.state_dict()[k]) for k, v in fitted.state_dict().items() if not k.startswith(X.SHARED_SKIP)))
    check("맞춘 encoder 2는 고정 상태다", not any(q.requires_grad for q in fitted.parameters()) and not fitted.training)
    d3 = M.FeatureHeadModel(copy.deepcopy(fe), 1).eval()
    for q in (d3.a.weight, d3.b.weight, d3.U.weight):
        torch.nn.init.normal_(q)
    mc3 = X.copy_head(M.FeatureHeadModel(fitted, 1), d3, "feature_model.")
    check("D-3 정서 head는 HK 값 그대로다", all(torch.equal(mc3.state_dict()[k], d3.state_dict()[k]) for k in d3.state_dict() if not k.startswith("feature_model.")))
    root = tmp / "root"
    m3 = dict(candidate=dict(d=8, input_wd=100.0, lr=1e-3, lam=None, alpha=None, rank=1, feature_wd=None))
    u3 = tmp / "u3"
    u3.mkdir()
    X.run_unit_dgroup("brain_features_only", [d3], m3, fe_cand, 0, "mc-01", fd, spec, u3, root, "test", {}, log=lambda m: None)
    z3 = np.load(u3 / "test_pred_final.npz")
    enc_dir = root / "encoder2" / "seed0" / "mc-01"
    check("D-3 시험 예측 72 × 34와 encoder 2 캐시", z3["p"].shape == (72, 34) and (enc_dir / "done.json").exists())
    stamp = (enc_dir / "input_layer.pt").stat().st_mtime_ns
    main = hk_model(True)
    d1 = M.SeparateDecodedModel(copy.deepcopy(main), copy.deepcopy(fe)).eval()
    m1 = dict(candidate=dict(d=8, input_wd=100.0, lr=1e-3, lam=1.0, alpha=None, rank=1, feature_wd=None))
    u1 = tmp / "u1"
    u1.mkdir()
    X.run_unit_dgroup("brain_decoded_sep", [d1], m1, fe_cand, 0, "mc-01", fd, spec, u1, root, "test", {}, log=lambda m: None)
    check("D-1과 D-3은 같은 encoder 2 캐시를 쓴다(다시 맞추지 않음)", (enc_dir / "input_layer.pt").stat().st_mtime_ns == stamp)
    check("D-1은 정서 encoder 입력층만 저장한다", set(torch.load(u1 / "input_layer_main.pt")) == {"main.input_layer.weights.mc-01", "main.input_layer.input_bias.mc-01"}
          and np.load(u1 / "test_pred_final.npz")["p"].shape == (72, 34))
    other = M.SeparateDecodedModel(copy.deepcopy(main), encoder2(7)).eval()
    u1b = tmp / "u1b"
    u1b.mkdir()
    check("encoder 2가 다르면 캐시에서 멈춘다", stops(lambda: X.run_unit_dgroup("brain_decoded_sep", [other], m1, fe_cand, 0, "mc-01", fd, spec, u1b, root, "test", {}, log=lambda m: None)))
    pairs = [(2, M.FrozenEncoderModel(encoder2(2)).eval()), (3, M.FrozenEncoderModel(encoder2(3)).eval())]
    u4 = tmp / "u4"
    u4.mkdir()
    _, extra = X.run_unit_dgroup("brain_frozen_feature_encoder", pairs, dict(candidate=dict(d=8, input_wd=100.0, lr=1e-3, lam=None, alpha=None, rank=None, feature_wd=None)), fe_cand, 0, "mc-01", fd, spec, u4, root, "test", {}, log=lambda m: None)
    each = []
    for j, hk in pairs:
        fe_j = X.load_encoder2(hk.feature_model, "mc-01", fd, root / f"encoder2_pair{j}" / "seed0" / "mc-01")
        each.append(torch.sigmoid(X.predict_z(X.copy_head(M.FrozenEncoderModel(fe_j), hk, "feature_model."), fd, spec)).numpy())
    check("D-4는 짝마다 encoder 2를 맞추고 예측 평정을 평균한다", np.allclose(np.load(u4 / "test_pred_final.npz")["p"], np.mean(each, 0), atol=1e-5) and extra["n_pairs"] == 2)


def main():
    check("후보는 lr × weight decay < 1", X.wds_for(1e-3) == [0.01, 0.1, 1.0, 10.0, 100.0] and X.wds_for(1e-4) == list(X.INPUT_WDS))
    hk = hk_model(True)
    mc = X.adapt(hk, "mc-01", [6, 4, 3])
    names = {n for n, p in mc.named_parameters() if p.requires_grad}
    check("입력층 W, b만 학습한다", names == {"input_layer.weights.mc-01", "input_layer.input_bias.mc-01"})
    same = all(torch.equal(v, hk.state_dict()[k]) for k, v in mc.state_dict().items() if not k.startswith(X.SHARED_SKIP))
    check("공유 가중치(e(r) 포함)는 HK 값 그대로다", same and "input_layer.roi_embedding" in mc.state_dict())
    groups = M.parameter_groups(mc, 1e-3, 100.0)
    placed = {id(p) for g in groups for p in g["params"]}
    check("AdamW 묶음에는 학습하는 두 파라미터만 들어간다", placed == {id(p) for p in mc.parameters() if p.requires_grad})

    blocks, repeats, idmap, n_rows = tables()
    mc72 = set(range(1, 73))
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        n_cols = 20
        g = np.random.default_rng(0)
        raw = g.normal(size=(n_rows, n_cols)).astype(np.float32)
        raw[-2:] = np.nan  # 빠진 run 행. 읽으면 finite 검사에서 멈춘다
        columns = np.array([0, 1, 2, 3, 4, 5, 4, 5, 6, 7, 8, 10, 11, 12])
        np.savez(tmp / "roi.npz", columns=columns, offsets=np.array([0, 6, 10, 14]), n_columns=n_cols)
        data = X.load_mc("01", blocks, repeats, idmap, mc72, raw=raw, roi=tmp / "roi.npz")
        check("빠진 run 행은 읽지 않는다(NaN이 있어도 멈추지 않음)", np.isfinite(data["X_tv"]).all() and np.isfinite(data["X_te"]).all())
        te = blocks[blocks.role == "test_72"]
        unique = np.unique(columns)
        want = np.stack([raw[te[te.video_id == v].qc_row.to_numpy()][:, unique].mean(0) for v in range(1, 73)])
        check("시험 반응은 영상마다 반복 평균이다", np.allclose(data["X_te"], want, atol=1e-6) and list(data["n_repeats"][:3]) == [3, 2, 3])
        check("학습, 검증 block 수와 역할", len(data["X_tv"]) == 10 and (data["role_tv"] == 0).sum() == 6 and (data["role_tv"] == 1).sum() == 4)
        bad = blocks.copy()
        bad.loc[bad.video_id == 106, ["video_id", "canonical_id"]] = 5  # 학습 영상이 시험 72개 가운데 하나
        check("MC 시험 영상이 학습에 섞이면 멈춘다", stops(lambda: X.mc_rows("01", bad, repeats, idmap, mc72)))
        rep2 = repeats.copy()
        rep2.loc[0, "n_repeats"] += 1
        check("반복 수가 표와 다르면 멈춘다", stops(lambda: X.mc_rows("01", blocks, rep2, idmap, mc72)))

        counts = [len(p) for p in data["positions"]]
        stats = dict(visual_mean=np.zeros(M.VISUAL_DIM), visual_std=np.ones(M.VISUAL_DIM), caption_mean=np.zeros(M.CAPTION_DIM), caption_std=np.ones(M.CAPTION_DIM))
        tg = dict(y_tv=g.uniform(0, 1, (10, 34)).astype(np.float32), v_tv=g.normal(size=(10, M.VISUAL_DIM)).astype(np.float32),
                  c_tv=g.normal(size=(10, M.CAPTION_DIM)).astype(np.float32), y_te=g.uniform(0, 1, (72, 34)).astype(np.float32))
        fd = X.mc_fold("mc-01", data, tg, stats, "cpu")
        check("FoldData의 시험 행은 정답 bank 밖이다", (fd.row_bank[fd.rows("test")] == -1).all() and len(fd.rows("test")) == 72 and fd.voxel_counts["mc-01"] == counts)
        spec = S.Spec(batch=4, max_epochs=3, patience=2)
        meta = dict(candidate=dict(d=8, input_wd=100.0, lr=1e-3, lam=1.0, alpha=None, rank=1, feature_wd=None))
        out = tmp / "unit"
        out.mkdir()
        chosen, rows = X.run_unit(hk, meta, "brain_decoded", 0, "mc-01", fd, spec, out, log=lambda m: None)
        sel = pd.read_csv(out / "selection.tsv", sep="\t")
        ok = sel.dropna(subset=["val_score"])
        check("후보 다섯 개를 모두 학습하고 검증 r이 가장 높은 값을 고른다", len(sel) == 5 and chosen == ok.sort_values(["val_score", "input_wd"], ascending=[False, True]).input_wd.iloc[0])
        check("후보별 시험 예측과 고른 입력층을 저장한다", all((out / f"test_pred_wd{w:g}.npz").exists() for w in ok.input_wd) and (out / "input_layer.pt").exists())
        z = np.load(out / f"test_pred_wd{chosen:g}.npz")
        check("시험 예측은 72개 영상, decoded features 포함", z["p"].shape == (72, 34) and z["v_hat"].shape == (72, M.VISUAL_DIM))
        saved = torch.load(out / "input_layer.pt")
        check("저장한 입력층은 MC 참가자의 W, b뿐이다", set(saved) == {"input_layer.weights.mc-01", "input_layer.input_bias.mc-01"})
        d_group(fd, spec, tmp, g)
    bad = [n for n, ok in RESULTS if not ok]
    print("통과", len(RESULTS) - len(bad), "실패", len(bad), bad)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
