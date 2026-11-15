#!/usr/bin/env python3
"""S9 경로 평가(K1)와 그 14개 차원판(K1a)의 예측 (04 S9, 01 K1, K1a, N3, N7, N8, O17, O20, O34, O35, G14, 2026-11-15). GPU 없음, 학습 없음.

하는 일: 실제 Vision feature와 Caption feature로 학습해 고정한 Stimulus Model의 head(S4)에 뇌에서 decoding한 두 특징만 넣어 정서(K1, 34개)와 정서 차원(K1a, 14개)을 낸다.
뇌 모델과 Stimulus Model은 더 학습하지 않는다. ROI token 경로는 넣지 않는다.

넣는 decoded features(K1, K1a가 같은 값을 쓴다)
- ridge: S5 층별 ridge의 시험 예측(test_pred.npz)을 이어 붙인 값(O21. V-JEPA 2 block 10, 20, 30, 40 5,632차원, DeBERTa 층 6, 12, 18, 24 4,096차원, 원래 척도).
- C-1(Brain + Decoded Feature → Emotion, 상호작용 head): S6 selected.json의 seed마다 outputs/decoded_test.npz. 학습 fold 4개의 D9 눈금이라 그 분할의 plan/standardization.npz로 원래 척도로 되돌린다(O20, s10_inputs.load_decoded).
- 두 값 모두 원래 척도에서 K1 head의 D_k 눈금(S4 stimulus/fold<k>/coordinates.npz)으로 바꾼다(N3, s6_common.to_k1_head와 같은 식).
head(O17, K1a)
- K1: S4 stimulus/fold<k>/head_additive.pt(r = 0), head_interaction.pt(r ∈ {1, 2, 4, 8}). 출력은 logit과 sigmoid 확률.
- K1a: S4 k1a/fold<k>/head_*.pt. 출력은 표준화한 값 z와, fold의 사람 평정 표준화 통계(target_mean, target_std)로 되돌린 1~9점 값(04 S9).
- K1a의 입력 눈금이 K1 head와 같아야 한다(04 S4 확인 기준). 다르면 멈춘다. 같으므로 N8 보정 통계도 K1의 것을 그대로 쓴다(K1a).
- 읽은 head에 실제 특징을 넣은 출력이 S4가 저장한 시험 예측(test_pred.npz)과 같은지 fold마다 확인한다(head_check.tsv). 다르면 멈춘다.
크기 보정(N8, O34, O35). 보정 전 판과 보정판을 둘 다 낸다. 시험 결과로 둘 중 하나를 고르지 않는다.
- 통계는 바깥 fold k의 H2 검증 fold(k 다음 fold) 영상에서, K1 head 눈금으로 낸다. 사람 평정과 시험 fold는 쓰지 않는다.
  ridge는 S5 inner_oof_target.npz에서 그 검증 fold를 뺀 안쪽 모델의 예측(고른 λ), C-1은 그 seed가 낸 outputs/decoded_val.npz다. 참가자마다 따로 낸다.
- μ̂, σ̂는 decoded features의, μ, σ는 같은 영상의 실제 특징의 차원별 평균과 표준편차(모집단 식)다. 보정은 v̂' = μ + (σ / σ̂)(v̂ − μ̂).
- σ̂_j가 같은 목표(Vision 또는 Caption) 안 σ̂ 중앙값의 1% 미만이면 평균만 옮긴다(v̂' = v̂ − μ̂ + μ). 그 차원 수를 목표, fold, seed, 참가자마다 적는다(n8_counts.tsv).
  σ̂ 중앙값이 0이면 문서로 정할 수 없는 경우라 멈춘다.
빠진 입력: S4 head 두 종류(6 fold), S5 decoding(5명 × 6 fold), C-1 seed 0, 1, 2(G14)의 decoded_test와 decoded_val(6 fold)이 모두 있어야 결과를 낸다.
  --partial-check면 있는 것만 계산하고 done.json에 partial_check를 남긴다. S10(s10_k1.py)은 --partial-check 없이 그 결과를 읽지 않는다.
출처(M1, CLAUDE_EmoBrain 5절): 읽은 모든 입력 파일의 sha256을 읽기 전에 내고 저장 전에 다시 본다. 출력 파일의 sha256도 done.json에 남긴다.
출력(레포 밖 --out)
- units/<ridge|c1_seed<s>>_fold<k>.npz: participant, video_id, k1_<head>_<보정>_logit, k1_<head>_<보정>_p(행 × 34), k1a_<head>_<보정>_z, k1a_<head>_<보정>_score(행 × 14).
  head는 additive, interaction, 보정은 uncorrected, corrected. 같은 파일에 N8 통계 n8_participant, n8_mu_hat, n8_sd_hat, n8_mu, n8_sd, n8_shift_only(참가자 × 9,728).
- n8_counts.tsv, head_check.tsv, coverage.tsv, missing.tsv(빠진 것이 있을 때), done.json
사용: s9_path_eval.py --s4-dir <S4 결과 폴더> --s5-dir <S5 decoding 폴더> --s6-dir <S6 결과 폴더> --out <출력 폴더> --design-freeze <커밋> [--partial-check] [--overwrite]
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

import s4_common as c
import s10_inputs as I
from s4_feature_model import FeatureModel

N_FOLDS = 6
EXPECTED_SEEDS = (0, 1, 2)  # G14. C-1은 seed 3개가 모두 있어야 한다
HEADS = ("additive", "interaction")  # O17. 더하기판(r = 0)과 상호작용판(r ∈ {1, 2, 4, 8})
INTERACTION_RANKS = (1, 2, 4, 8)  # E2, O17
CALIBRATIONS = ("uncorrected", "corrected")  # N8
SHIFT_ONLY_FRACTION = 0.01  # O35. 같은 목표 안 σ̂ 중앙값의 1%
VISION_LAYERS = ("vjepa2_10", "vjepa2_20", "vjepa2_30", "vjepa2_40")  # O21
CAPTION_LAYERS = ("deberta_06", "deberta_12", "deberta_18", "deberta_24")
DV, DC = I.DIMS["vision"], I.DIMS["caption"]
N_EMOTIONS, N_DIMENSIONS = 34, 14
HEAD_CHECK_TOL = 1e-4  # 저장된 S4 시험 출력과 다시 낸 출력의 허용 차이(float32 계산 순서 차이를 넘는 값만 걸러 낸다). 결과 값이 아니다
CODE_FILES = ("s9_path_eval.py", "s10_inputs.py", "s4_feature_model.py", "s4_common.py")


def code_hashes():
    return {n: c.sha256(c.CODE_DIR / n) for n in CODE_FILES}


class Inputs:
    """읽은 입력 파일의 sha256. 읽기 전에 내고(add), 저장 전에 다시 본다(check)."""

    def __init__(self):
        self.hashes = {}

    def add(self, path):
        path = Path(path)
        key = str(path)
        if key not in self.hashes:
            self.hashes[key] = c.sha256(path)
        return path

    def check(self):
        for p, h in self.hashes.items():
            if c.sha256(p) != h:
                raise SystemExit(f"시작 뒤 입력이 바뀌었다: {p}")


# 읽기

def load_head(path, n_out, inputs):
    """S4 save_state 형식의 head. 돌려주는 값: (FeatureModel, 기록 dict)."""
    s = torch.load(inputs.add(path), map_location="cpu", weights_only=True)
    r = int(s["r"])
    model = FeatureModel(DV, DC, n_out, r)
    model.load_state_dict(s["state_dict"])
    model.eval()
    meta = {k: (np.asarray(v, np.float64) if torch.is_tensor(v) else v) for k, v in s.items() if k != "state_dict"}
    return model, meta


def head_dir_ok(d):
    return all((Path(d) / f).exists() for f in ("done.json", "coordinates.npz", "test_pred.npz", "head_additive.pt", "head_interaction.pt"))


def load_fold_heads(s4_dir, k, inputs):
    """fold k의 K1 head 두 개와 K1a head 두 개, K1 head 눈금, K1a 사람 평정 표준화 통계. 출처와 판(O17)을 확인한다."""
    out = {}
    for task, n_out in (("stimulus", N_EMOTIONS), ("k1a", N_DIMENSIONS)):
        d = Path(s4_dir) / task / f"fold{k}"
        done = json.loads(inputs.add(d / "done.json").read_text())
        t = done.get("task", {})
        if t.get("task") != task or int(t.get("k", -1)) != k:
            raise ValueError(f"{d}: done.json의 과제({t})가 {task} fold {k}가 아니다")
        coord = dict(np.load(inputs.add(d / "coordinates.npz")))
        heads = {}
        for h in HEADS:
            model, meta = load_head(d / f"head_{h}.pt", n_out, inputs)
            rank = int(meta["r"])
            if (h == "additive" and rank != 0) or (h == "interaction" and rank not in INTERACTION_RANKS):
                raise ValueError(f"{d}/head_{h}.pt: rank {rank}가 O17의 판과 맞지 않는다")
            for name in ("visual_mean", "visual_std", "caption_mean", "caption_std") + (("target_mean", "target_std") if task == "k1a" else ()):
                if not np.array_equal(np.asarray(meta[name], np.float64), np.asarray(coord[name], np.float64)):
                    raise ValueError(f"{d}/head_{h}.pt: {name}가 coordinates.npz와 다르다")
            heads[h] = dict(model=model, rank=rank, epochs=int(meta["epochs"]), weight_decay=float(meta["weight_decay"]), lr=float(meta["lr"]))
        out[task] = dict(dir=d, coord=coord, heads=heads, test_pred=dict(np.load(inputs.add(d / "test_pred.npz"))))
    a, b = out["stimulus"]["coord"], out["k1a"]["coord"]
    for name in ("visual_mean", "visual_std", "caption_mean", "caption_std"):
        if not np.array_equal(a[name], b[name]):
            raise ValueError(f"fold {k}: K1a Stimulus Model의 입력 눈금({name})이 K1 head와 다르다(04 S4 확인 기준)")
    for name in ("visual_std", "caption_std"):
        if (np.asarray(a[name]) <= 0).any():
            raise ValueError(f"fold {k}: K1 head 눈금에 표준편차가 0 이하인 차원이 있다")
    return out


def to_head(x, coord):
    """원래 척도 (행, 9,728) -> K1 head의 D_k 눈금(N3)."""
    m = np.concatenate([coord["visual_mean"], coord["caption_mean"]]).astype(np.float64)
    s = np.concatenate([coord["visual_std"], coord["caption_std"]]).astype(np.float64)
    return (np.asarray(x, np.float64) - m) / s


def apply_head(model, xh):
    """K1 head 눈금의 (행, 9,728)을 head에 넣는다. S4 predict와 같이 float32로 계산한다. 돌려주는 값: 출력(sigmoid 전 또는 z), float64."""
    x = torch.as_tensor(c.finite(xh, "head 입력"), dtype=torch.float32)
    with torch.no_grad():
        out = model(x[:, :DV], x[:, DV:]).numpy().astype(np.float64)
    return c.finite(out, "head 출력")


def check_heads(fh, k, split, fold_videos):
    """실제 특징을 넣은 출력이 S4가 저장한 시험 출력과 같은지(head를 맞게 읽었는지) 확인한다. 돌려주는 값: 기록 행."""
    rows = []
    feats = I.actual_features(split, fold_videos)
    xh = to_head(np.concatenate([feats["vision"], feats["caption"]], 1), fh["stimulus"]["coord"])
    for task, key in (("stimulus", "logit"), ("k1a", "z")):
        tp = fh[task]["test_pred"]
        if not np.array_equal(np.asarray(tp["video_id"], np.int64), np.asarray(fold_videos, np.int64)):
            raise ValueError(f"fold {k} {task}: S4 test_pred의 영상이 fold {k}의 개발 영상과 다르다")
        for h, hd in fh[task]["heads"].items():
            got = apply_head(hd["model"], xh)
            saved = np.asarray(tp[f"{h}_{key}"], np.float64)
            diff = float(np.max(np.abs(got - saved))) if saved.shape == got.shape else np.inf
            rows.append(dict(fold=k, model="K1" if task == "stimulus" else "K1a", head=h, rank=hd["rank"], epochs=hd["epochs"], n_videos=len(fold_videos), max_abs_diff=diff))
            if not diff <= HEAD_CHECK_TOL:
                raise ValueError(f"fold {k} {task} {h}: 읽은 head의 출력이 S4가 저장한 시험 출력과 다르다(최대 차이 {diff}). head나 눈금을 잘못 읽었다")
    return rows


def concat_layers(z, path):
    x = np.concatenate([np.asarray(z[n], np.float64) for n in VISION_LAYERS + CAPTION_LAYERS], 1)
    if x.shape[1] != DV + DC or not np.isfinite(x).all():
        raise ValueError(f"{path}: 이어 붙인 decoded features의 크기 {x.shape}가 다르거나 NaN이 있다")
    return x


def ridge_files(s5_dir, q, k):
    d = Path(s5_dir) / f"{q}_fold{k}"
    return [d / "done.json", d / "test_pred.npz", d / "inner_oof_target.npz"]


def load_ridge(s5_dir, q, k, val_fold, fold_of, pvideos):
    """S5 ridge의 시험 decoded features와 H2 검증 fold의 안쪽 fold 밖 decoded features(O34). 원래 척도."""
    d = Path(s5_dir) / f"{q}_fold{k}"
    zt = np.load(d / "test_pred.npz")
    vt = zt["video_id"].astype(np.int64)
    want_t = sorted(int(v) for v in pvideos[q] if fold_of[int(v)] == k)
    if len(set(vt.tolist())) != len(vt) or sorted(vt.tolist()) != want_t:
        raise ValueError(f"{d}/test_pred.npz: 시험 영상이 그 참가자의 fold {k} block 영상과 다르다")
    xt = concat_layers(zt, d / "test_pred.npz")
    zo = np.load(d / "inner_oof_target.npz")
    at = zo["inner_fold"].astype(int) == val_fold
    vv = zo["video_id"].astype(np.int64)[at]
    want_v = sorted(int(v) for v in pvideos[q] if fold_of[int(v)] == val_fold)
    if len(set(vv.tolist())) != len(vv) or sorted(vv.tolist()) != want_v:
        raise ValueError(f"{d}/inner_oof_target.npz: 검증 fold {val_fold}의 영상이 그 참가자의 block 영상과 다르다")
    xv = concat_layers({n: np.asarray(zo[n])[at] for n in VISION_LAYERS + CAPTION_LAYERS}, d / "inner_oof_target.npz")
    ot, ov = np.argsort(vt), np.argsort(vv)
    return (vt[ot], xt[ot]), (vv[ov], xv[ov])


def c1_files(plan, seed_dir):
    return [Path(seed_dir) / f for f in ("outputs/decoded_test.npz", "outputs/decoded_val.npz", "outputs/done.json", "done.json")] + [Path(plan) / "plan" / f for f in ("standardization.npz", "rows.npz")]


def load_c1(plan, seed_dir, pids):
    """C-1 한 seed의 시험, 검증 decoded features(원래 척도). 돌려주는 값: 참가자 -> ((시험 영상, 값), (검증 영상, 값))."""
    te = I.load_decoded(seed_dir, plan, I.plan_rows(plan, "test"), "test")
    va = I.load_decoded(seed_dir, plan, I.plan_rows(plan, "val"), "val")
    if set(te) != set(va) or set(te) != set(pids):
        raise ValueError(f"{seed_dir}: 시험과 검증의 참가자 {sorted(te)}, {sorted(va)}가 {pids}와 다르다")
    return {q: ((te[q][0], np.concatenate(te[q][1:], 1)), (va[q][0], np.concatenate(va[q][1:], 1))) for q in te}


# N8

def n8_stats(dec_val_h, act_val_h):
    """N8, O34, O35. K1 head 눈금에서 차원별 평균과 표준편차. 돌려주는 값: dict(mu_hat, sd_hat, mu, sd, shift_only, median_sd_hat)."""
    mu_hat, sd_hat = dec_val_h.mean(0), dec_val_h.std(0)
    mu, sd = act_val_h.mean(0), act_val_h.std(0)
    shift = np.zeros(DV + DC, bool)
    med = {}
    for name, sl in (("vision", slice(0, DV)), ("caption", slice(DV, DV + DC))):
        m = float(np.median(sd_hat[sl]))
        if not m > 0:
            raise ValueError(f"N8: {name} decoded features의 σ̂ 중앙값이 0이라 O35의 기준을 정할 수 없다")
        shift[sl] = sd_hat[sl] < SHIFT_ONLY_FRACTION * m
        med[name] = m
    return dict(mu_hat=mu_hat, sd_hat=sd_hat, mu=mu, sd=sd, shift_only=shift, median_sd_hat=med)


def n8_apply(xh, s):
    """v̂' = μ + (σ / σ̂)(v̂ − μ̂). 평균만 옮기는 차원은 v̂' = v̂ − μ̂ + μ(O35)."""
    scale = np.where(s["shift_only"], 1.0, s["sd"] / np.where(s["shift_only"], 1.0, s["sd_hat"]))
    return s["mu"] + scale * (xh - s["mu_hat"])


# 한 단위(ridge 또는 C-1 seed 하나, fold 하나)

def unit_predictions(fh, by_q, split, k, source, seed):
    """by_q: 참가자 -> ((시험 영상, 원래 척도 값), (검증 영상, 원래 척도 값)). 돌려주는 값: 저장할 배열 dict, N8 개수 행."""
    coord = fh["stimulus"]["coord"]
    k1a_coord = fh["k1a"]["coord"]
    cols = {f"{m}_{h}_{cal}_{x}": [] for m, xs in (("k1", ("logit", "p")), ("k1a", ("z", "score"))) for h in HEADS for cal in CALIBRATIONS for x in xs}
    pid, vid, n8 = [], [], {x: [] for x in ("mu_hat", "sd_hat", "mu", "sd", "shift_only")}
    count_rows = []
    for q in sorted(by_q):
        (vt, xt), (vv, xv) = by_q[q]
        feats = I.actual_features(split, vv)
        act_h = to_head(np.concatenate([feats["vision"], feats["caption"]], 1), coord)
        st8 = n8_stats(to_head(xv, coord), act_h)
        for x in n8:
            n8[x].append(st8[x])
        for name, sl in (("vision", slice(0, DV)), ("caption", slice(DV, DV + DC))):
            count_rows.append(dict(source=source, seed=seed, fold=k, participant=q, target=name, n_dims=sl.stop - sl.start, n_shift_only=int(st8["shift_only"][sl].sum()),
                                   median_sd_hat=st8["median_sd_hat"][name], n_val_videos=len(vv)))
        xh = {"uncorrected": to_head(xt, coord)}
        xh["corrected"] = n8_apply(xh["uncorrected"], st8)
        for cal, x in xh.items():
            for h in HEADS:
                z = apply_head(fh["stimulus"]["heads"][h]["model"], x)
                cols[f"k1_{h}_{cal}_logit"].append(z)
                cols[f"k1_{h}_{cal}_p"].append(np.exp(-np.logaddexp(0.0, -z)))  # sigmoid. 큰 |z|에서 넘치지 않는 꼴
                zd = apply_head(fh["k1a"]["heads"][h]["model"], x)
                cols[f"k1a_{h}_{cal}_z"].append(zd)
                cols[f"k1a_{h}_{cal}_score"].append(zd * np.asarray(k1a_coord["target_std"], np.float64) + np.asarray(k1a_coord["target_mean"], np.float64))  # 04 S9. 1~9점 척도로 되돌린다
        pid.append(np.full(len(vt), q))
        vid.append(vt)
    arrays = dict(participant=np.concatenate(pid), video_id=np.concatenate(vid).astype(np.int64), **{k_: np.concatenate(v) for k_, v in cols.items()},
                  n8_participant=np.array(sorted(by_q)), **{f"n8_{x}": np.stack(v) for x, v in n8.items()})
    return arrays, count_rows


# 실행

def collect(s4_dir, s5_dir, s6_dir, split, pvideos, inputs):
    """있는 입력과 빠진 입력. 읽을 파일의 sha256을 읽기 전에 낸다. decoded features는 단위마다 계산할 때 읽는다(메모리).
    돌려주는 값: fold -> head, ridge 단위 fold -> 참가자 목록, C-1 단위 seed -> fold -> (plan, seed 폴더), coverage 표, missing 행."""
    pids = [q for q in I.HK_PIDS if q in pvideos]
    heads, ridge, c1, cov, missing = {}, {}, {}, [], []
    for k in range(1, N_FOLDS + 1):
        ok = all(head_dir_ok(Path(s4_dir) / t / f"fold{k}") for t in ("stimulus", "k1a"))
        where = str(Path(s4_dir) / "{stimulus,k1a}" / f"fold{k}")
        cov.append(dict(source="S4 head", seed="", fold=k, participant="", status="ok" if ok else "없음", path=where))
        if not ok:
            missing.append(dict(source="S4 head", seed="", fold=k, participant="", path=where))
            continue
        heads[k] = load_fold_heads(s4_dir, k, inputs)
        for q in pids:
            files = ridge_files(s5_dir, q, k)
            ok = all(f.exists() for f in files)
            cov.append(dict(source="ridge", seed="", fold=k, participant=q, status="ok" if ok else "없음", path=str(files[1].parent)))
            if not ok:
                missing.append(dict(source="ridge", seed="", fold=k, participant=q, path=str(files[1].parent)))
                continue
            for f in files:
                inputs.add(f)
            ridge.setdefault(k, []).append(q)
        plan = Path(s6_dir) / f"outer_fold{k}"
        seeds = (I.selected_seeds(plan, "brain_decoded") if plan.is_dir() else None) or {}
        if seeds:
            inputs.add(plan / "brain_decoded" / "selected.json")
        for s in sorted(set(EXPECTED_SEEDS) | set(seeds)):
            if s not in EXPECTED_SEEDS:
                raise ValueError(f"{plan}: C-1 seed {s}는 G14의 seed(0, 1, 2)가 아니다")
            d = seeds.get(s)
            files = c1_files(plan, d) if d is not None else []
            ok = d is not None and all(f.exists() for f in files)
            where = str(d) if d is not None else str(plan / "brain_decoded" / "selected.json")
            cov.append(dict(source="C-1", seed=s, fold=k, participant="", status="ok" if ok else "없음", path=where))
            if not ok:
                missing.append(dict(source="C-1", seed=s, fold=k, participant="", path=where))
                continue
            for f in files:
                inputs.add(f)
            c1.setdefault(s, {})[k] = (plan, d)
    return heads, ridge, c1, pd.DataFrame(cov), missing


def run(s4_dir, s5_dir, s6_dir, out, split, *, partial_check=False, overwrite=False, extra_info=None, pvideos=None):
    started = time.time()
    out = I.prepare_out(out, overwrite)
    code0 = code_hashes()
    pvideos = I.participant_videos(split) if pvideos is None else pvideos
    pids = [q for q in I.HK_PIDS if q in pvideos]
    fold_of = dict(zip(split.video_id.astype(int), split.fold.astype(int)))
    inputs = Inputs()
    for p in (c.SPLITS / "split_hk_dev.tsv", c.SPLITS / "fold_roles.tsv", c.S2 / "participant_blocks_hk.tsv"):
        if p.exists():
            inputs.add(p)
    heads, ridge, c1, cov, missing = collect(s4_dir, s5_dir, s6_dir, split, pvideos, inputs)
    I.require_complete(missing, partial_check, "K1, K1a 경로 평가 예측")
    if not heads:
        raise SystemExit("읽은 S4 head가 없다")
    fold_ids = {k: np.sort(split.video_id[split.fold == k].astype(np.int64).to_numpy()) for k in range(1, N_FOLDS + 1)}
    check_rows = [r for k, fh in sorted(heads.items()) for r in check_heads(fh, k, split, fold_ids[k])]
    units, counts = {}, []
    for k, qs in sorted(ridge.items()):
        val = c.roles(k)["val"]
        by_q = {q: load_ridge(s5_dir, q, k, val, fold_of, pvideos) for q in qs}
        units[f"ridge_fold{k}"], cr = unit_predictions(heads[k], by_q, split, k, "ridge", "")
        counts += cr
        del by_q
        print(f"K1 ridge fold {k} 끝 ({time.time() - started:.0f}초)", flush=True)
    for s, by_k in sorted(c1.items()):
        for k, (plan, d) in sorted(by_k.items()):
            by_q = load_c1(plan, d, pids)
            units[f"c1_seed{s}_fold{k}"], cr = unit_predictions(heads[k], by_q, split, k, "C-1", s)
            counts += cr
            del by_q
            print(f"K1 C-1 seed {s} fold {k} 끝 ({time.time() - started:.0f}초)", flush=True)
    inputs.check()
    if code_hashes() != code0:
        raise SystemExit("시작 뒤 코드가 바뀌었다")
    info = dict(stage="S9 path evaluation (K1, K1a)", s4_dir=str(s4_dir), s5_dir=str(s5_dir), s6_dir=str(s6_dir), code_commit=c.START_HEAD, code_dirty=c.START_DIRTY, code_sha256=code0,
                inputs=inputs.hashes, settings=dict(heads=HEADS, interaction_ranks=INTERACTION_RANKS, calibrations=CALIBRATIONS, shift_only_fraction=SHIFT_ONLY_FRACTION, expected_seeds=EXPECTED_SEEDS,
                vision_layers=VISION_LAYERS, caption_layers=CAPTION_LAYERS, head_check_tol=HEAD_CHECK_TOL, torch=torch.__version__),
                heads={k: {t: {h: {x: v for x, v in hd.items() if x != "model"} for h, hd in fh[t]["heads"].items()} for t in ("stimulus", "k1a")} for k, fh in heads.items()},
                units=sorted(units), partial_check=bool(missing), **(extra_info or {}))
    if missing:
        info["note"] = I.PARTIAL_NOTE
    with c.Atomic(out) as tmp:
        (tmp / "units").mkdir()
        outputs = {}
        for name, arrays in units.items():
            np.savez(tmp / "units" / f"{name}.npz", **arrays)
            outputs[f"units/{name}.npz"] = c.sha256(tmp / "units" / f"{name}.npz")
        I.write_tsv(pd.DataFrame(counts), tmp / "n8_counts.tsv")
        I.write_tsv(pd.DataFrame(check_rows), tmp / "head_check.tsv")
        I.write_tsv(cov, tmp / "coverage.tsv")
        if missing:
            I.write_tsv(pd.DataFrame(missing), tmp / "missing.tsv")
        info["outputs"] = outputs
        info["elapsed_seconds"] = round(time.time() - started, 1)
        (tmp / "done.json").write_text(json.dumps(info, indent=1, ensure_ascii=False, default=str))
    return info


def main(argv=None):
    ap = argparse.ArgumentParser(description="S9 경로 평가(K1, K1a) 예측. 고정한 Stimulus Model head에 decoded features를 넣는다")
    ap.add_argument("--s4-dir", required=True, help="S4 결과 폴더(stimulus/fold<k>, k1a/fold<k>가 있는 곳)")
    ap.add_argument("--s5-dir", required=True, help="S5 decoding 폴더(<output_root>/s5_ridge/decoding)")
    ap.add_argument("--s6-dir", required=True, help="S6 결과 폴더(합친 폴더. outer_fold<k>/brain_decoded/selected.json)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", required=True)
    ap.add_argument("--partial-check", action="store_true", help="빠진 입력이 있어도 있는 것만 계산한다. 점검용이고 S10이 --partial-check 없이 읽지 않는다")
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args(argv)
    c.guard(a.design_freeze)
    split = c.load_split()
    info = run(a.s4_dir, a.s5_dir, a.s6_dir, a.out, split, partial_check=a.partial_check, overwrite=a.overwrite, extra_info=dict(design_freeze=a.design_freeze))
    print(f"끝: {a.out} ({info['elapsed_seconds']}초, 단위 {len(info['units'])}개)")


if __name__ == "__main__":
    main()
