#!/usr/bin/env python3
"""S10 6-4b 네트워크 단위 입력 교란과 그 ROI판 (04 S9, S10 영역과 다중비교, 01 6-4b, 6-4의 ROI판, 6-1 2-4행, O3, O4 (3), I5, 2026-11-15). GPU 없음.

입력: S9 perturb 결과(<S9 perturb 폴더>/outer_fold<k>_seed<s>/, s9_saved_models.py)
- perturb_sums.npz: fold마다, 참가자마다 원래 예측과 교란 예측(묶음 13개와 ROI 370개 × 20회)의 합, 제곱합, 사람 평정과의 곱의 합, 배정표
- perturb_pred.npz(행 열쇠와 영상별 원래 예측), perturb_pred_<조건>.npy(단위 × 반복 × 행 × 34 영상별 교란 예측). float32 확률이다.
  11/15 석진 님 승인으로 S9가 함께 저장한다. 영상별 예측이 없는 폴더(11/15 전 S9 형식)는 빠진 입력으로 센다.
- 6 fold가 모두 있어야 최종 표를 낸다. 빠지면 빠진 fold를 적고 멈춘다(--partial-check는 점검용).
- 확인
  - 행의 영상은 그 fold의 시험 영상이고, 저장된 사람 평정의 합과 제곱합이 사람 평정 파일에서 다시 낸 값과 같다. 단위(묶음, ROI)의 이름과 순서가 fold마다 같다.
  - 영상별 예측의 행 열쇠(참가자, 영상)와 단위가 perturb_sums.npz와 같고, 참가자마다 더하면 저장된 합과 같다(원래 예측, 모든 단위와 반복). 확률은 0~1이다.
  - 영상별 예측으로 낸 r이 저장된 합으로 낸 r(11/15 전의 점추정)과 같다.
  - 묶음 단위의 이름은 S2 일치도 표의 묶음(13개)과 같다. Holm 13의 묶음이다.
  - --s6-dir를 주면 원래 예측의 합이 S6 시험 예측(test_pred.npz)의 합과 같은지 본다.
계산(점추정은 11/15 전과 같다)
- 참가자마다 6 fold의 영상을 모아 정서별 r(2-3과 같은 방식)을 낸다. 원래 예측의 r과 교란 예측의 r을 반복마다 내고,
  성능 하락 = 원래 점수 − 교란 점수를 반복마다 낸 뒤 20회를 평균한다(04 S9). 점수는 원래 예측에서 계산할 수 있는 정서의 r 평균이다(2-3).
- 두 모델(A-1, C-1)의 하락과 하락폭 차이(C-1 − A-1)를 단위마다, 참가자마다, 5명 평균으로 낸다. 묶음은 정서별 값도 낸다. 13묶음의 참가자 간 일치도(S2)를 붙인다.
- 두 모델에서 계산할 수 있는 정서가 다르면 멈춘다(어느 정서로 평균할지 2-3이 정하지 않았다. s10_performance와 같은 규칙).
재표집(6-1, O4 (3), I5)
- 1부(s10_performance)와 같은 영상 단위 bootstrap이다. 같은 내용 영상 묶음(canonical_id)을 함께 뽑고, 같은 난수 seed(perf.BOOT_SEED)와 횟수(10,000)를 쓴다.
  두 모델, 모든 단위, 5명에 같은 뽑힌 횟수를 쓴다.
- 재표집마다 뽑힌 영상으로 원래 r과 반복 20회 각각의 교란 r을 다시 내 반복마다 하락을 내고, 20회를 --repeat-handling대로 합친다. 예측을 반복끼리 먼저 평균하지 않는다.
- 구간은 basic 95%, p는 중심을 맞춘 양측 검정 (1 + #(|θ* − θ| ≥ |θ|)) / (B + 1)이다. 각 모델의 하락과 하락폭 차이를 0과 비교한다.
다중비교(04 S10 다중비교, 01 6-4). 보정 묶음은 표의 열(..._family, ..._family_size)과 run_info.json에 적는다.
- [Holm 13] 13묶음의 하락폭 차이: seed마다, 5명 평균의 묶음과 참가자마다의 묶음에 각각 Holm(6-1 2-4행). 확인된 참가자 수를 보정 전과 후로 센다(유의수준 0.05, 11/15 석진 님).
- 탐색(BH-FDR)
  - 묶음별 각 모델의 하락: 묶음 구성을 문서가 정하지 않아 --drop-bh-family로 받는다. by_model은 seed, 참가자(5명 평균 따로), 모델마다 13개. pooled는 seed, 참가자마다 26개.
  - ROI판: seed, 참가자(5명 평균 따로), 값(A-1 하락, C-1 하락, 하락폭 차이)마다 ROI 370개(01 6-4 ROI판의 "참가자와 목표마다 ROI 370개").
  - 묶음 안 정서별: seed, 참가자(5명 평균 따로), 묶음, 값마다 34개 정서(01 6-4).
문서가 정하지 않아 기본값 없이 받는 것(04 기록 칸에 올릴 것)
- --repeat-handling fixed|resample. fixed는 배정표를 고정하고 재표집마다 20회를 모두 다시 낸 뒤 평균한다(2-2의 대조 100회와 같은 방식. 구간은 배정표 조건부다).
  resample은 재표집마다 20회도 복원 추출해 뽑힌 횟수로 평균한다(배정 변동을 구간에 넣음). 관찰 값은 둘 다 20회 평균이다.
- --drop-bh-family by_model|pooled
- --partial-check에서는 둘을 비워도 된다. --repeat-handling이 없으면 재표집 없이 점추정만 낸다.
실행 시간: 재표집이 단위 383 × 모델 2 × 참가자 5번이다. --workers로 단위를 나눠 돌린다(결과는 workers 수와 무관하다). 시간은 scripts/s10_perturb.sh 머리말.
출력(레포 밖 --out): network_drops.tsv, network_drops_per_emotion.tsv, network_confirmed.tsv, roi_drops.tsv, coverage.tsv, arrays.npz(단위 × 참가자 × 정서의 하락 점추정), run_info.json
사용: s10_perturb.py --perturb-dir <S9 perturb 폴더> --out <출력 폴더> --design-freeze <커밋> --repeat-handling fixed|resample --drop-bh-family by_model|pooled
      [--s6-dir <S6 결과 폴더>] [--n-boot 10000] [--workers 1] [--alpha 0.05] [--partial-check] [--overwrite]
"""
import argparse
import multiprocessing as mp
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd

import s4_common as c
import s10_inputs as I
import s10_performance as perf
import s10_stats as st

MODELS = ("brain_only", "brain_decoded")  # A-1, C-1. s9_saved_models.PERTURB_CONDITIONS
SHORT = {"brain_only": "A1", "brain_decoded": "C1"}
QUANTITIES = {"A1": "A-1 하락", "C1": "C-1 하락", "difference": "하락폭 차이(C-1 − A-1)"}
DIFF = "C-1 − A-1"
PRED_FILE, PRED_ARRAY = "perturb_pred.npz", "perturb_pred_{}.npy"  # s9_saved_models.PRED_FILE, PRED_ARRAY와 같다
REPEAT_HANDLING = ("fixed", "resample")
DROP_BH_FAMILIES = ("by_model", "pooled")
REPEAT_SEED = 20261117  # resample일 때 반복을 다시 뽑는 난수 seed. 결과를 보지 않고 정했고 run_info.json에 남긴다
ALPHA = 0.05  # 11/15 석진 님. Holm 뒤 유의수준(s10_holm15와 같음)
BOOT_CHUNK = 1000  # 재표집을 나눠 계산하는 크기(메모리). 결과와 무관하다
SUM_TOL = dict(rtol=1e-9, atol=1e-9)  # 영상별 float32 값을 float64로 더한 합과 S9 GPU 합의 차이(더하는 순서)만 허용한다
R_TOL = 1e-7  # 영상별 r과 합으로 낸 r의 차이 허용치. 합의 뺄셈 오차만 허용하고, 행이 어긋나면 이보다 훨씬 크게 다르다
_CTX = {}  # 단위 계산(unit_result)이 읽는 자료. fork한 worker가 그대로 물려받는다


def find_runs(perturb_dir):
    rows = []
    for d in sorted(Path(perturb_dir).iterdir()):
        m = re.fullmatch(r"outer_fold(\d+)_seed(\d+)", d.name)
        if not m or not d.is_dir():
            continue
        if not ((d / "perturb_sums.npz").exists() and (d / "done.json").exists()):
            status = "끝나지 않음"
        elif not ((d / PRED_FILE).exists() and all((d / PRED_ARRAY.format(x)).exists() for x in MODELS)):
            status = "영상별 예측 없음(11/15 전 S9 형식. 새 S9로 다시 돌린다)"
        else:
            status = "ok"
        rows.append(dict(seed=int(m.group(2)), fold=int(m.group(1)), path=str(d), status=status))
    t = pd.DataFrame(rows, columns=["seed", "fold", "path", "status"])
    if t.empty:
        raise SystemExit(f"{perturb_dir}: outer_fold<k>_seed<s> 폴더가 없다")
    missing = []
    for s in sorted(t.seed.unique()):
        have = set(t.fold[(t.seed == s) & (t.status == "ok")])
        missing += [dict(seed=s, fold=k, status=(t.status[(t.seed == s) & (t.fold == k)].tolist() or ["폴더 없음"])[0]) for k in range(1, I.N_FOLDS + 1) if k not in have]
    return t, missing


def pooled_r(sums, sum_y, sum_yy, n):
    """fold 합을 모은 r. sums: [..., 3(합, 제곱합, y와의 곱의 합), 참가자, 34]. 예측이나 사람 평정의 분산이 0이면 NaN(2-6). 영상별 r과 대조하는 데 쓴다."""
    sp, spp, spy = sums[..., 0, :, :], sums[..., 1, :, :], sums[..., 2, :, :]
    n = n[:, None]
    vp, vy = spp - sp ** 2 / n, sum_yy - sum_y ** 2 / n
    cov = spy - sp * sum_y / n
    bad = (vp <= st.REL_TOL * np.abs(spp)) | (vy <= st.REL_TOL * np.abs(sum_yy))
    with np.errstate(invalid="ignore", divide="ignore"):
        r = cov / np.sqrt(np.where(bad, 1.0, vp * vy))
    return np.where(bad, np.nan, r)


def sums_of(onehot, p, y):
    """참가자마다의 합, 제곱합, y와의 곱의 합. onehot: (행, 참가자), p: (..., 행, 34), y: (행, 34). 돌려주는 값: (..., 3, 참가자, 34)."""
    p = np.asarray(p, np.float64)
    return np.stack([onehot.T @ p, onehot.T @ (p * p), onehot.T @ (p * y)], -3)


def check_prob(a, what):
    if not np.isfinite(a).all() or (a < 0).any() or (a > 1).any():
        raise ValueError(f"{what}: 예측 확률에 NaN이 있거나 0~1을 벗어났다")


def load_fold(path, k, split, y):
    """한 fold의 합과 영상별 예측. 큰 교란 예측은 memmap으로 두고 단위마다 읽는다."""
    path = Path(path)
    npz = np.load(path / "perturb_sums.npz")
    z = {name: npz[name] for name in npz.files}  # npz는 꺼낼 때마다 다시 읽으므로 한 번만 꺼낸다
    fold_of = dict(zip(split.video_id.astype(int), split.fold.astype(int)))
    ypos = {v: i for i, v in enumerate(split.video_id.astype(int).tolist())}
    vid, pid = z["video_id"].astype(np.int64), z["participant"].astype(str)
    if any(fold_of[int(v)] != k for v in vid):
        raise ValueError(f"{path}: fold {k}의 시험 영상이 아닌 행이 있다")
    names = sorted(np.unique(pid))
    yy = y[[ypos[int(v)] for v in vid]]
    for i, q in enumerate(names):  # 참가자 축의 순서는 이름 순서여야 한다. 사람 평정 합으로 확인한다
        m = pid == q
        if not (np.allclose(z["sum_y"][i], yy[m].sum(0), atol=1e-6) and np.allclose(z["sum_yy"][i], (yy[m] ** 2).sum(0), atol=1e-6) and z["n"][i] == m.sum()):
            raise ValueError(f"{path}: {q}의 저장된 사람 평정 합이 다시 낸 값과 다르다. 참가자 축 순서나 행이 맞지 않는다")
    pv = np.load(path / PRED_FILE)
    if not (np.array_equal(pv["video_id"].astype(np.int64), vid) and np.array_equal(pv["participant"].astype(str), pid)):
        raise ValueError(f"{path}: 영상별 예측의 행 열쇠(참가자, 영상)가 perturb_sums.npz와 다르다")
    if not (np.array_equal(pv["unit_kind"].astype(str), z["unit_kind"].astype(str)) and np.array_equal(pv["unit_name"].astype(str), z["unit_name"].astype(str))):
        raise ValueError(f"{path}: 영상별 예측의 단위가 perturb_sums.npz와 다르다")
    onehot = np.stack([pid == q for q in names], 1).astype(np.float64)
    repeats, n_units = int(z["donors"].shape[0]), len(z["unit_kind"])
    base, pert = {}, {}
    for cond in MODELS:
        b = pv[f"{cond}_base"]
        if b.dtype != np.float32 or b.shape != (len(vid), y.shape[1]):
            raise ValueError(f"{path}: {cond}_base의 자료형 {b.dtype}이나 크기 {b.shape}가 다르다")
        check_prob(b, f"{path} {cond} 원래 예측")
        if not np.allclose(sums_of(onehot, b, yy), z[f"{cond}_base"], **SUM_TOL):
            raise ValueError(f"{path}: {cond} 영상별 원래 예측의 합이 perturb_sums.npz와 다르다")
        a = np.load(path / PRED_ARRAY.format(cond), mmap_mode="r")
        if a.dtype != np.float32 or a.shape != (n_units, repeats, len(vid), y.shape[1]):
            raise ValueError(f"{path}: {PRED_ARRAY.format(cond)}의 자료형 {a.dtype}이나 크기 {a.shape}가 다르다(단위 {n_units} × 반복 {repeats} × 행 {len(vid)} × 정서)")
        base[cond], pert[cond] = b.astype(np.float64), a
    return dict(z=z, participants=names, video_id=vid, participant=pid, y=yy, onehot=onehot, base=base, pert=pert, repeats=repeats)


def check_base_against_s6(s6_dir, k, seed, fold, pids):
    """원래 예측의 합이 S6 시험 예측의 합과 같은지(같은 모델, 같은 행)."""
    for cond in MODELS:
        seeds = I.selected_seeds(Path(s6_dir) / f"outer_fold{k}", cond)
        if not seeds or seed not in seeds:
            raise ValueError(f"S6 fold {k} {cond} seed {seed}의 선택이 없다")
        want = I.plan_test_rows(Path(s6_dir) / f"outer_fold{k}")
        p = I.load_test_pred(seeds[seed] / "test_pred.npz", want, 34)
        base = fold["z"][f"{cond}_base"]
        for i, q in enumerate(pids):
            if not np.allclose(base[0, i], p[q][1].sum(0), atol=1e-2, rtol=1e-4):
                raise ValueError(f"fold {k} {cond} {q}: S9 원래 예측의 합이 S6 시험 예측의 합과 다르다")


def combine_repeats(d, counts):
    """d: (B, 반복, ...) 재표집마다 반복별 값. counts가 None이면 반복 평균(fixed), 아니면 (B, 반복) 뽑힌 횟수로 가중 평균(resample). 쓰인 반복에 NaN이 있으면 NaN."""
    if counts is None:
        return d.mean(1)
    w = counts.reshape(counts.shape + (1,) * (d.ndim - 2)).astype(np.float64)
    used = w > 0
    out = (np.where(used, d, 0.0) * w).sum(1) / w.sum(1)
    out[(np.isnan(d) & used).any(1)] = np.nan
    return out


def boot_rows(W, code, chunk=BOOT_CHUNK):
    """재표집 뽑힌 횟수(B, 단위)를 이 참가자의 행으로 옮겨 chunk씩 float64로 낸다."""
    for b0 in range(0, len(W), chunk):
        yield W[b0:b0 + chunk][:, code].astype(np.float64)


def test_values(est, boot):
    """구간과 중심을 맞춘 양측 p. boot이 None이면(재표집 없음) NaN."""
    est = np.asarray(est, np.float64)
    if boot is None:
        nan = np.full(est.shape, np.nan)
        return nan, nan, nan, np.zeros(est.shape, int)
    lo, hi = st.basic_ci(est, boot)
    return lo, hi, st.centered_p(est, boot), np.isfinite(boot).sum(0)


def unit_result(u):
    """단위 u의 관찰 값과 재표집. 두 모델, 5명. 돌려주는 값: 점수 행(참가자와 5명 평균), 묶음이면 정서별 행, 정서별 하락 점추정."""
    C = _CTX
    pids, folds, R = C["pids"], C["folds"], C["repeats"]
    kind, name = C["kinds"][u], C["units"][u]
    do_boot = C["W"] is not None
    obs, boot, emo, emo_boot, pscore = {}, {}, {}, {}, {}
    for cond in MODELS:
        sl = {}
        for k, f in folds.items():
            a = np.asarray(f["pert"][cond][u], np.float64)  # 반복 × 행 × 34
            check_prob(a, f"fold {k} {cond} {kind} {name}")
            if not np.allclose(sums_of(f["onehot"], a, f["y"]), f["z"][f"{cond}_perturbed"][u], **SUM_TOL):
                raise ValueError(f"fold {k} {cond} {kind} {name}: 영상별 교란 예측의 합이 perturb_sums.npz와 다르다")
            sl[k] = a
        r_sums = pooled_r(sum(f["z"][f"{cond}_perturbed"][u] for f in folds.values()), C["sum_y"], C["sum_yy"], C["n"])  # 반복 × 참가자 × 34
        for i, q in enumerate(pids):
            P = np.concatenate([sl[k][:, C["idx"][k][q], :] for k in folds], axis=1)  # 반복 × 영상 × 34
            yq, keep = C["yq"][q], C["keep"][cond, q]
            X = P.transpose(1, 0, 2).reshape(len(yq), R * yq.shape[1])  # 열 순서: 반복, 정서
            r_obs = st.pearson_columns(np.tile(yq, (1, R)), X).reshape(R, -1)
            if not np.allclose(r_obs, r_sums[:, i], atol=R_TOL, equal_nan=True):
                raise ValueError(f"{cond} {kind} {name} {q}: 영상별 예측의 r이 저장된 합으로 낸 r과 다르다")
            if (np.isnan(r_obs) & keep[None]).any():
                raise SystemExit(f"{cond} {kind} {name} {q}: 원래 예측에서는 계산할 수 있지만 교란 뒤 r을 계산할 수 없는 정서가 있다. 이 경우의 규칙은 문서에 없다")
            ps = r_obs[:, keep].mean(1)  # 반복마다 교란 점수
            pscore[cond, q] = float(ps.mean())
            obs[cond, q] = float((C["bscore"][cond, q] - ps).mean())
            emo[cond, q] = (C["rbase"][cond, q][None] - r_obs).mean(0)  # 정서별 하락(11/15 전과 같음. 계산할 수 없는 정서는 NaN)
            if do_boot:
                col_of = np.tile(np.arange(yq.shape[1]), R)
                rb = np.concatenate([st.boot_r_paired(w, X, yq, col_of) for w in boot_rows(C["W"], C["code"][q])]).reshape(-1, R, yq.shape[1])
                base_b = C["rbase_boot"][cond, q]  # B × 34
                d = st.mean_over(base_b, keep)[:, None] - st.mean_over(rb, keep)  # B × 반복
                boot[cond, q] = combine_repeats(d, C["counts"])
                if kind == "group":
                    emo_boot[cond, q] = combine_repeats(base_b[:, None, :] - rb, C["counts"])
    rows, emo_rows = [], []
    est_all = {cond: np.array([obs[cond, q] for q in pids]) for cond in MODELS}
    for q in pids + ["mean5"]:
        row = dict(unit_index=u, unit_kind=kind, unit=name, participant=q)
        values = {}
        for cond in MODELS:
            s = SHORT[cond]
            if q == "mean5":
                est, b = float(est_all[cond].mean()), (np.mean(np.stack([boot[cond, x] for x in pids]), 0) if do_boot else None)
                row.update({f"base_score_{s}": float(np.mean([C["bscore"][cond, x] for x in pids])), f"perturbed_score_{s}": float(np.mean([pscore[cond, x] for x in pids])), f"n_emotions_{s}": np.nan})
            else:
                est, b = obs[cond, q], (boot[cond, q] if do_boot else None)
                row.update({f"base_score_{s}": C["bscore"][cond, q], f"perturbed_score_{s}": pscore[cond, q], f"n_emotions_{s}": int(C["keep"][cond, q].sum())})
            values[s] = (est, b)
        values["difference"] = (values["C1"][0] - values["A1"][0], values["C1"][1] - values["A1"][1] if do_boot else None)
        for s, (est, b) in values.items():
            lo, hi, p, nv = test_values(est, b)
            col = "drop_difference" if s == "difference" else f"drop_{s}"
            pre = "difference" if s == "difference" else f"drop_{s}"
            row.update({col: est, f"{pre}_ci_low": float(lo), f"{pre}_ci_high": float(hi), f"{pre}_p_raw": float(p), f"{pre}_n_boot_valid": int(nv)})
        rows.append(row)
        if kind != "group":
            continue
        ev = {}
        for cond in MODELS:
            if q == "mean5":
                ev[SHORT[cond]] = (perf.nanmean0(np.stack([emo[cond, x] for x in pids])), perf.nanmean0(np.stack([emo_boot[cond, x] for x in pids])) if do_boot else None)
            else:
                ev[SHORT[cond]] = (emo[cond, q], emo_boot[cond, q] if do_boot else None)
        ev["difference"] = (ev["C1"][0] - ev["A1"][0], ev["C1"][1] - ev["A1"][1] if do_boot else None)
        for s, (est, b) in ev.items():
            lo, hi, p, nv = test_values(est, b)
            pb = st.bh(p)  # 탐색. seed, 참가자(5명 평균 따로), 묶음, 값마다 34개 정서(01 6-4)
            for e in range(len(est)):
                emo_rows.append(dict(unit=name, participant=q, quantity=QUANTITIES[s], emotion=C["emotions"][e], estimate=est[e], ci_low=lo[e], ci_high=hi[e], p_raw=p[e], p_bh=pb[e],
                                     n_boot_valid=int(nv[e]), family_size=int(np.isfinite(p).sum()), bh_family="seed, 참가자(5명 평균 따로), 묶음, 값마다 34개 정서", label="탐색(BH-FDR)"))
    return dict(rows=rows, emotion_rows=emo_rows, emotion_drop={cond: np.stack([emo[cond, q] for q in pids]) for cond in MODELS})


def holm_by(t, p_col, by, out_col):
    t[out_col] = np.nan
    for _, g in t.groupby(by, sort=False):
        t.loc[g.index, out_col] = st.holm(g[p_col].to_numpy(np.float64))
    return t


def bh_by(t, p_col, by, out_col, size_col):
    t[out_col], t[size_col] = np.nan, 0
    for _, g in t.groupby(by, sort=False):
        p = g[p_col].to_numpy(np.float64)
        t.loc[g.index, out_col] = st.bh(p)
        t.loc[g.index, size_col] = int(np.isfinite(p).sum())
    return t


def correct_networks(nd, drop_family, do_boot):
    """[Holm 13] 하락폭 차이, 탐색 BH 각 모델의 하락(--drop-bh-family)."""
    nd = holm_by(nd, "difference_p_raw", ["seed", "participant"], "difference_p_holm")
    nd["difference_family"] = "[사전] Holm 13: seed, 참가자(5명 평균 따로)마다 13묶음의 하락폭 차이"
    nd["difference_family_size"] = nd.groupby(["seed", "participant"]).difference_p_raw.transform(lambda s: int(np.isfinite(s).sum()))
    for s in ("A1", "C1"):
        nd[f"drop_{s}_p_bh"], nd[f"drop_{s}_family_size"] = np.nan, 0
    if drop_family == "by_model":
        for s in ("A1", "C1"):
            nd = bh_by(nd, f"drop_{s}_p_raw", ["seed", "participant"], f"drop_{s}_p_bh", f"drop_{s}_family_size")
        nd["drop_family"] = "탐색(BH-FDR) by_model: seed, 참가자(5명 평균 따로), 모델마다 13묶음"
    elif drop_family == "pooled":
        for _, g in nd.groupby(["seed", "participant"], sort=False):
            p = np.concatenate([g.drop_A1_p_raw.to_numpy(np.float64), g.drop_C1_p_raw.to_numpy(np.float64)])
            adj = st.bh(p)
            nd.loc[g.index, "drop_A1_p_bh"], nd.loc[g.index, "drop_C1_p_bh"] = adj[:len(g)], adj[len(g):]
            nd.loc[g.index, ["drop_A1_family_size", "drop_C1_family_size"]] = int(np.isfinite(p).sum())
        nd["drop_family"] = "탐색(BH-FDR) pooled: seed, 참가자(5명 평균 따로)마다 두 모델의 26개"
    else:
        nd["drop_family"] = "정하지 않음(--drop-bh-family 없음, 점검용)"
    if not do_boot:
        nd["difference_family"] = "재표집 없음(--repeat-handling 없음, 점검용)"
    return nd


def correct_rois(rd):
    """ROI판 탐색 BH: seed, 참가자(5명 평균 따로), 값마다 ROI 370개(01 6-4)."""
    for pre in ("drop_A1", "drop_C1", "difference"):
        rd = bh_by(rd, f"{pre}_p_raw", ["seed", "participant"], f"{pre}_p_bh", f"{pre}_family_size")
    rd["family"] = "탐색(BH-FDR): seed, 참가자(5명 평균 따로), 값(A-1 하락, C-1 하락, 하락폭 차이)마다 ROI 370개"
    return rd


def confirmed_counts(nd, alpha):
    """[Holm 13] 묶음마다 하락폭 차이가 확인된 참가자 수(6-1). 보정 전과 후, 추정 방향(양수는 C-1의 하락이 더 큼)."""
    part = nd[nd.participant != "mean5"]
    rows = []
    for (seed, unit), g in part.groupby(["seed", "unit"], sort=False):
        raw, adj = g.difference_p_raw < alpha, g.difference_p_holm < alpha
        rows.append(dict(seed=seed, unit=unit, n_participants=len(g), n_confirmed_before_holm=int(raw.sum()), n_confirmed_after_holm=int(adj.sum()),
                         n_after_holm_C1_drop_larger=int((adj & (g.drop_difference > 0)).sum()), n_after_holm_A1_drop_larger=int((adj & (g.drop_difference < 0)).sum()), alpha=alpha))
    return pd.DataFrame(rows)


def prepare_seed(folds, split, emotions, n_boot, repeat_handling):
    """참가자마다 6 fold의 행을 모으고, 재표집 뽑힌 횟수와 원래 예측의 재표집 r을 미리 낸다. unit_result가 읽을 _CTX를 돌려준다."""
    ref = next(iter(folds.values()))
    pids = ref["participants"]
    idx = {k: {q: np.flatnonzero(f["participant"] == q) for q in pids} for k, f in folds.items()}
    vq = {q: np.concatenate([f["video_id"][idx[k][q]] for k, f in folds.items()]) for q in pids}
    yq = {q: np.concatenate([f["y"][idx[k][q]] for k, f in folds.items()]) for q in pids}
    ctx = dict(pids=pids, folds=folds, idx=idx, yq=yq, repeats=ref["repeats"], emotions=emotions,
               kinds=ref["z"]["unit_kind"].astype(str), units=ref["z"]["unit_name"].astype(str),
               sum_y=sum(f["z"]["sum_y"] for f in folds.values()), sum_yy=sum(f["z"]["sum_yy"] for f in folds.values()), n=sum(f["z"]["n"] for f in folds.values()))
    info = {}
    ctx["rbase"], ctx["keep"], ctx["bscore"] = {}, {}, {}
    for cond in MODELS:
        r_sums = pooled_r(sum(f["z"][f"{cond}_base"] for f in folds.values()), ctx["sum_y"], ctx["sum_yy"], ctx["n"])
        for i, q in enumerate(pids):
            bq = np.concatenate([f["base"][cond][idx[k][q]] for k, f in folds.items()])
            r = st.pearson_columns(yq[q], bq)
            if not np.allclose(r, r_sums[i], atol=R_TOL, equal_nan=True):
                raise ValueError(f"{cond} {q}: 영상별 원래 예측의 r이 저장된 합으로 낸 r과 다르다")
            ctx["rbase"][cond, q], ctx["keep"][cond, q] = r, np.isfinite(r)
            ctx["bscore"][cond, q] = float(r[np.isfinite(r)].mean())
            ctx.setdefault("base_q", {})[cond, q] = bq
    for q in pids:
        if not np.array_equal(ctx["keep"]["brain_only", q], ctx["keep"]["brain_decoded", q]):
            diff = [emotions[e] for e in np.flatnonzero(ctx["keep"]["brain_only", q] != ctx["keep"]["brain_decoded", q])]
            raise ValueError(f"{q}: 두 모델에서 계산할 수 있는 정서가 다르다({diff}). 하락폭 차이를 어느 정서로 평균할지 정해지지 않았다")
    ctx["W"], ctx["counts"] = None, None
    if repeat_handling is not None and n_boot > 0:
        U = np.array(sorted(set().union(*[set(v.tolist()) for v in vq.values()])), np.int64)
        sp = split.set_index("video_id").loc[U]
        codes, n_units = st.unit_codes(sp.canonical_id.to_numpy())  # 1부와 같은 단위(같은 내용 영상 묶음)
        W = st.bootstrap_counts(n_units, n_boot, np.random.default_rng(perf.BOOT_SEED))  # 1부와 같은 seed. 1부와 영상 목록이 같으면 같은 재표집이다
        ctx["W"], ctx["code"] = W, {q: codes[np.searchsorted(U, vq[q])] for q in pids}
        ctx["rbase_boot"] = {}
        for cond in MODELS:
            for q in pids:
                ctx["rbase_boot"][cond, q] = np.concatenate([st.boot_r(w, yq[q], {cond: ctx["base_q"][cond, q]})[cond] for w in boot_rows(W, ctx["code"][q])])
        if repeat_handling == "resample":
            R = ctx["repeats"]
            pick = np.random.default_rng(REPEAT_SEED).integers(0, R, size=(n_boot, R))
            ctx["counts"] = np.stack([np.bincount(row, minlength=R) for row in pick])  # 두 모델, 모든 단위, 5명에 같은 반복 뽑기
        info.update(n_videos_union=len(U), n_bootstrap_units=int(n_units))
    return ctx, info


def run(perturb_dir, out, split, y, emotions, *, repeat_handling=None, drop_bh_family=None, n_boot=st.N_RESAMPLE, workers=1, alpha=ALPHA, s6_dir=None,
        partial_check=False, overwrite=False, extra_info=None, agreement=None):
    started = time.time()
    if repeat_handling is not None and repeat_handling not in REPEAT_HANDLING:
        raise ValueError(f"--repeat-handling은 {REPEAT_HANDLING} 가운데 하나다")
    if drop_bh_family is not None and drop_bh_family not in DROP_BH_FAMILIES:
        raise ValueError(f"--drop-bh-family는 {DROP_BH_FAMILIES} 가운데 하나다")
    if not partial_check and (repeat_handling is None or drop_bh_family is None):
        raise SystemExit(f"문서가 정하지 않은 두 선택을 주어야 한다: --repeat-handling {REPEAT_HANDLING}, --drop-bh-family {DROP_BH_FAMILIES}(기본값 없음)")
    out = I.prepare_out(out, overwrite)
    runs, missing = find_runs(perturb_dir)
    I.require_complete(missing, partial_check, "6-4b")
    agreement = pd.read_csv(c.S2 / "agreement_hk_13groups.tsv", sep="\t") if agreement is None else agreement
    tables = {k: [] for k in ("network_drops", "network_drops_per_emotion", "roi_drops")}
    arrays, cov, seed_info = {}, [], {}
    for seed in sorted(runs.seed.unique()):
        ok = runs[(runs.seed == seed) & (runs.status == "ok")].sort_values("fold")
        if ok.empty:
            continue
        folds = {int(r.fold): load_fold(r.path, int(r.fold), split, y) for r in ok.itertuples()}
        ref = next(iter(folds.values()))
        pids, kinds, units = ref["participants"], ref["z"]["unit_kind"].astype(str), ref["z"]["unit_name"].astype(str)
        for k, f in folds.items():
            if f["participants"] != pids or f["repeats"] != ref["repeats"] or not (np.array_equal(f["z"]["unit_kind"].astype(str), kinds) and np.array_equal(f["z"]["unit_name"].astype(str), units)):
                raise ValueError(f"fold {k}: 참가자, 반복 수나 교란 단위가 다른 fold와 다르다")
            if s6_dir:
                check_base_against_s6(s6_dir, k, int(seed), f, pids)
            cov.append(dict(seed=seed, fold=k, n_rows=len(f["video_id"]), n_units=len(units), n_repeats=f["repeats"], donor_seed=int(f["z"]["donor_seed"])))
        groups = set(units[kinds == "group"])
        if groups != set(agreement.group):
            raise ValueError(f"묶음 단위 {sorted(groups)}가 S2 일치도 표의 묶음 {sorted(agreement.group)}과 다르다(Holm 13의 묶음)")
        ctx, info = prepare_seed(folds, split, emotions, n_boot, repeat_handling)
        seed_info[int(seed)] = info
        _CTX.clear()
        _CTX.update(ctx)
        try:
            if workers > 1:
                with mp.get_context("fork").Pool(workers) as pool:
                    results = list(pool.imap(unit_result, range(len(units)), chunksize=1))
            else:
                results = [unit_result(u) for u in range(len(units))]
        finally:
            _CTX.clear()
        for res in results:
            kind = res["rows"][0]["unit_kind"]
            tables["network_drops" if kind == "group" else "roi_drops"] += [dict(seed=seed, **r, difference=DIFF, n_folds=len(folds)) for r in res["rows"]]
            tables["network_drops_per_emotion"] += [dict(seed=seed, **r) for r in res["emotion_rows"]]
        for cond in MODELS:
            arrays[f"emotion_drop:{cond}:seed{seed}"] = np.stack([res["emotion_drop"][cond] for res in results]).astype(np.float32)
    do_boot = repeat_handling is not None and n_boot > 0
    nd = pd.DataFrame(tables["network_drops"])
    nd = correct_networks(nd, drop_bh_family, do_boot)
    nd = nd.merge(agreement.rename(columns={"group": "unit", "median": "agreement_median", "min": "agreement_min", "max": "agreement_max", "count": "agreement_n_roi"}), on="unit", how="left")
    if nd.agreement_median.isna().any():
        raise ValueError("13묶음 이름이 S2 일치도 표와 맞지 않는다")
    rd = correct_rois(pd.DataFrame(tables["roi_drops"])) if tables["roi_drops"] else pd.DataFrame()
    out_tables = dict(network_drops=nd, network_drops_per_emotion=pd.DataFrame(tables["network_drops_per_emotion"]), network_confirmed=confirmed_counts(nd, alpha),
                      roi_drops=rd, coverage=runs.merge(pd.DataFrame(cov), on=["seed", "fold"], how="left") if cov else runs)
    if missing:
        out_tables["missing"] = pd.DataFrame(missing)
    families = {"[사전] Holm 13": "seed, 참가자(5명 평균 따로)마다 13묶음의 하락폭 차이(C-1 − A-1)",
                "탐색 묶음별 각 모델의 하락": {"by_model": "seed, 참가자(5명 평균 따로), 모델마다 13묶음", "pooled": "seed, 참가자(5명 평균 따로)마다 26개"}.get(drop_bh_family, "정하지 않음"),
                "탐색 ROI판": "seed, 참가자(5명 평균 따로), 값(A-1 하락, C-1 하락, 하락폭 차이)마다 ROI 370개",
                "탐색 묶음 안 정서별": "seed, 참가자(5명 평균 따로), 묶음, 값마다 34개 정서"}
    info = dict(stage="S10 6-4b perturb", perturb_dir=str(perturb_dir), s6_dir=str(s6_dir) if s6_dir else None, difference=DIFF, repeat_handling=repeat_handling,
                drop_bh_family=drop_bh_family, correction_families=families, alpha=alpha,
                resampling=dict(n_boot=n_boot if do_boot else 0, boot_seed=perf.BOOT_SEED, unit="같은 내용 영상 묶음(canonical_id), 1부와 같음", ci_level=st.CI_LEVEL,
                                repeat_seed=REPEAT_SEED if repeat_handling == "resample" else None, per_seed=seed_info),
                workers=workers, partial_check=bool(missing) or not do_boot, **(extra_info or {}))
    if missing:
        info["note"] = I.PARTIAL_NOTE
    elif not do_boot:
        info["note"] = "점검용 실행: 재표집 없이 점추정만 냈다(--repeat-handling 없음 또는 --n-boot 0). 결과로 쓰지 않는다"
    return I.write_out(out, out_tables, info, started, arrays)


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 6-4b 네트워크 단위 입력 교란과 ROI판")
    ap.add_argument("--perturb-dir", required=True, help="<S9_OUT>/perturb/<S6 결과 폴더 이름>")
    ap.add_argument("--s6-dir", default=None, help="원래 예측의 합을 S6 시험 예측과 대조할 S6 결과 폴더(선택)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", required=True)
    ap.add_argument("--repeat-handling", choices=REPEAT_HANDLING, default=None, help="20회 반복이 재표집에 들어가는 방식. 문서가 정하지 않아 기본값이 없다")
    ap.add_argument("--drop-bh-family", choices=DROP_BH_FAMILIES, default=None, help="묶음별 각 모델 하락의 탐색 BH 묶음. 문서가 정하지 않아 기본값이 없다")
    ap.add_argument("--n-boot", type=int, default=st.N_RESAMPLE)
    ap.add_argument("--workers", type=int, default=1, help="단위를 나눠 계산할 프로세스 수. 결과와 무관하다")
    ap.add_argument("--alpha", type=float, default=ALPHA, help="확인된 참가자 수를 셀 유의수준. 0.05(11/15 석진 님)")
    ap.add_argument("--partial-check", action="store_true")
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args(argv)
    c.guard(a.design_freeze)
    split = c.load_split()
    y, cols = c.load_scores(split, "emotions")
    info = run(a.perturb_dir, a.out, split, np.asarray(y, np.float64), I.emotion_names(cols), repeat_handling=a.repeat_handling, drop_bh_family=a.drop_bh_family,
               n_boot=a.n_boot, workers=a.workers, alpha=a.alpha, s6_dir=a.s6_dir, partial_check=a.partial_check, overwrite=a.overwrite,
               extra_info=dict(design_freeze=a.design_freeze))
    print(f"끝: {a.out} ({info['elapsed_seconds']}초)")


if __name__ == "__main__":
    main()
