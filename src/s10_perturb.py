#!/usr/bin/env python3
"""S10 6-4b 네트워크 단위 입력 교란 (04 S9, S10 영역, 01 6-4b, 6-1 2-4행, O3, 2026-11-15). GPU 없음.

입력: S9 perturb 결과(<S9 perturb 폴더>/outer_fold<k>_seed<s>/perturb_sums.npz, s9_saved_models.py).
- 저장된 것은 fold마다, 참가자마다 원래 예측과 교란 예측(묶음 13개와 ROI 370개 × 20회)의 합, 제곱합, 사람 평정과의 곱의 합이다.
- 6 fold가 모두 있어야 최종 표를 낸다. 빠지면 빠진 fold를 적고 멈춘다(--partial-check는 점검용).
- 확인: 행의 영상은 그 fold의 시험 영상이고, 저장된 사람 평정의 합과 제곱합이 사람 평정 파일에서 다시 낸 값과 같다. 단위(묶음, ROI)의 이름과 순서가 fold마다 같다.
  --s6-dir를 주면 원래 예측의 합이 S6 시험 예측(test_pred.npz)의 합과 같은지 본다.
계산
- 참가자마다 fold의 합을 모아 정서별 r(6 fold를 모은 r, 2-3과 같은 방식)을 낸다. 원래 예측의 r과 교란 예측의 r을 반복마다 내고,
  성능 하락 = 원래 점수 − 교란 점수를 반복마다 낸 뒤 20회를 평균한다(04 S9). 점수는 원래 예측에서 계산할 수 있는 정서의 r 평균이다(2-3).
- 두 모델(A-1, C-1)의 하락과 하락폭 차이(C-1 − A-1)를 묶음마다, 참가자마다, 5명 평균으로 낸다. 정서별 값도 낸다. 13묶음의 참가자 간 일치도(S2)를 붙인다(04 S10 영역).
하지 않는 것(문서와 저장 형식이 맞지 않음, 04 기록 칸에 올릴 것)
- 04 S10은 하락폭 차이의 불확실성(구간)과 13묶음 Holm, 나머지 BH를 요구한다. S9는 참가자별 합만 저장해 영상 단위 재표집을 할 수 없다.
  그래서 구간과 p를 내지 않고 표에 그 사실을 적는다. 영상별 원래, 교란 예측을 저장하도록 S9를 고치거나 다른 불확실성 계산을 정해야 한다.
출력(레포 밖 --out): network_drops.tsv, network_drops_per_emotion.tsv, roi_drops.tsv, coverage.tsv, arrays.npz(단위 × 참가자 × 정서의 하락), run_info.json
사용: s10_perturb.py --perturb-dir <S9 perturb 폴더> --out <출력 폴더> --design-freeze <커밋> [--s6-dir <S6 결과 폴더>] [--partial-check] [--overwrite]
"""
import argparse
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
DIFF = "C-1 − A-1"
NO_UNCERTAINTY = "구간과 p 없음: S9 perturb가 참가자별 합만 저장해 영상 단위 재표집을 할 수 없다(04 S10과 저장 형식이 맞지 않음)"


def find_runs(perturb_dir):
    rows = []
    for d in sorted(Path(perturb_dir).iterdir()):
        m = re.fullmatch(r"outer_fold(\d+)_seed(\d+)", d.name)
        if not m or not d.is_dir():
            continue
        ok = (d / "perturb_sums.npz").exists() and (d / "done.json").exists()
        rows.append(dict(seed=int(m.group(2)), fold=int(m.group(1)), path=str(d), status="ok" if ok else "끝나지 않음"))
    t = pd.DataFrame(rows, columns=["seed", "fold", "path", "status"])
    if t.empty:
        raise SystemExit(f"{perturb_dir}: outer_fold<k>_seed<s> 폴더가 없다")
    missing = []
    for s in sorted(t.seed.unique()):
        have = set(t.fold[(t.seed == s) & (t.status == "ok")])
        missing += [dict(seed=s, fold=k) for k in range(1, I.N_FOLDS + 1) if k not in have]
    return t, missing


def pooled_r(sums, sum_y, sum_yy, n):
    """fold 합을 모은 r. sums: [..., 3(합, 제곱합, y와의 곱의 합), 참가자, 34]. 예측이나 사람 평정의 분산이 0이면 NaN(2-6)."""
    sp, spp, spy = sums[..., 0, :, :], sums[..., 1, :, :], sums[..., 2, :, :]
    n = n[:, None]
    vp, vy = spp - sp ** 2 / n, sum_yy - sum_y ** 2 / n
    cov = spy - sp * sum_y / n
    bad = (vp <= st.REL_TOL * np.abs(spp)) | (vy <= st.REL_TOL * np.abs(sum_yy))
    with np.errstate(invalid="ignore", divide="ignore"):
        r = cov / np.sqrt(np.where(bad, 1.0, vp * vy))
    return np.where(bad, np.nan, r)


def load_fold(path, k, split, y, pids_expected=None):
    z = np.load(Path(path) / "perturb_sums.npz")
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
    return dict(z=z, participants=names, video_id=vid, participant=pid)


def check_base_against_s6(s6_dir, k, seed, fold, pids):
    """원래 예측의 합이 S6 시험 예측의 합과 같은지(같은 모델, 같은 행)."""
    for j, cond in enumerate(MODELS):
        seeds = I.selected_seeds(Path(s6_dir) / f"outer_fold{k}", cond)
        if not seeds or seed not in seeds:
            raise ValueError(f"S6 fold {k} {cond} seed {seed}의 선택이 없다")
        want = I.plan_test_rows(Path(s6_dir) / f"outer_fold{k}")
        p = I.load_test_pred(seeds[seed] / "test_pred.npz", want, 34)
        base = fold["z"][f"{cond}_base"]
        for i, q in enumerate(pids):
            if not np.allclose(base[0, i], p[q][1].sum(0), atol=1e-2, rtol=1e-4):
                raise ValueError(f"fold {k} {cond} {q}: S9 원래 예측의 합이 S6 시험 예측의 합과 다르다")


def run(perturb_dir, out, split, y, emotions, *, s6_dir=None, partial_check=False, overwrite=False, extra_info=None, agreement=None):
    started = time.time()
    out = I.prepare_out(out, overwrite)
    runs, missing = find_runs(perturb_dir)
    I.require_complete(missing, partial_check, "6-4b")
    agreement = pd.read_csv(c.S2 / "agreement_hk_13groups.tsv", sep="\t") if agreement is None else agreement
    tables = {k: [] for k in ("network_drops", "network_drops_per_emotion", "roi_drops")}
    arrays, cov = {}, []
    for seed in sorted(runs.seed.unique()):
        ok = runs[(runs.seed == seed) & (runs.status == "ok")].sort_values("fold")
        if ok.empty:
            continue
        folds = {int(r.fold): load_fold(r.path, int(r.fold), split, y) for r in ok.itertuples()}
        ref = next(iter(folds.values()))
        pids, kinds, units = ref["participants"], ref["z"]["unit_kind"].astype(str), ref["z"]["unit_name"].astype(str)
        for k, f in folds.items():
            if f["participants"] != pids or not (np.array_equal(f["z"]["unit_kind"].astype(str), kinds) and np.array_equal(f["z"]["unit_name"].astype(str), units)):
                raise ValueError(f"fold {k}: 참가자나 교란 단위가 다른 fold와 다르다")
            if s6_dir:
                check_base_against_s6(s6_dir, k, int(seed), f, pids)
            cov.append(dict(seed=seed, fold=k, n_rows=len(f["video_id"]), n_units=len(units), n_repeats=int(f["z"]["donors"].shape[0]), donor_seed=int(f["z"]["donor_seed"])))
        sum_y = sum(f["z"]["sum_y"] for f in folds.values())
        sum_yy = sum(f["z"]["sum_yy"] for f in folds.values())
        n = sum(f["z"]["n"] for f in folds.values())
        res = {}
        for cond in MODELS:
            base = pooled_r(sum(f["z"][f"{cond}_base"] for f in folds.values()), sum_y, sum_yy, n)  # 참가자 × 34
            pert = pooled_r(sum(f["z"][f"{cond}_perturbed"] for f in folds.values()), sum_y, sum_yy, n)  # 단위 × 반복 × 참가자 × 34
            keep = np.isfinite(base)
            if (np.isnan(pert) & keep[None, None]).any():
                raise SystemExit(f"{cond} seed {seed}: 원래 예측에서는 계산할 수 있지만 교란 뒤 r을 계산할 수 없는 정서가 있다. 이 경우의 규칙은 문서에 없다")
            bscore = np.array([base[i][keep[i]].mean() for i in range(len(pids))])
            pscore = np.stack([np.where(keep[i], pert[..., i, :], np.nan) for i in range(len(pids))], -2)  # 단위 × 반복 × 참가자 × 34
            pscore = np.nanmean(pscore, -1)  # 단위 × 반복 × 참가자
            res[cond] = dict(base=base, keep=keep, bscore=bscore, drop=(bscore[None, None] - pscore).mean(1), emo_drop=(base[None, None] - pert).mean(1),
                             pscore=pscore.mean(1))
            arrays[f"emotion_drop:{cond}:seed{seed}"] = res[cond]["emo_drop"].astype(np.float32)
        for u, (kind, unit) in enumerate(zip(kinds, units)):
            for i, q in enumerate(pids + ["mean5"]):
                vals = {}
                for cond, short in zip(MODELS, ("A1", "C1")):
                    r = res[cond]
                    if q == "mean5":
                        vals.update({f"base_score_{short}": float(r["bscore"].mean()), f"perturbed_score_{short}": float(r["pscore"][u].mean()), f"drop_{short}": float(r["drop"][u].mean())})
                    else:
                        vals.update({f"base_score_{short}": float(r["bscore"][i]), f"perturbed_score_{short}": float(r["pscore"][u, i]), f"drop_{short}": float(r["drop"][u, i]),
                                     f"n_emotions_{short}": int(r["keep"][i].sum())})
                row = dict(seed=seed, unit_kind=kind, unit=unit, participant=q, **vals, drop_difference=vals["drop_C1"] - vals["drop_A1"], difference=DIFF,
                           n_folds=len(folds), uncertainty=NO_UNCERTAINTY)
                tables["network_drops" if kind == "group" else "roi_drops"].append(row)
            if kind == "group":
                for i, q in enumerate(pids + ["mean5"]):
                    a = res["brain_only"]["emo_drop"][u]
                    b = res["brain_decoded"]["emo_drop"][u]
                    if q == "mean5":
                        a, b = perf.nanmean0(a), perf.nanmean0(b)
                    else:
                        a, b = a[i], b[i]
                    for e in range(len(emotions)):
                        tables["network_drops_per_emotion"].append(dict(seed=seed, unit=unit, participant=q, emotion=emotions[e], drop_A1=a[e], drop_C1=b[e], drop_difference=b[e] - a[e], difference=DIFF))
    nd = pd.DataFrame(tables["network_drops"])
    nd = nd.merge(agreement.rename(columns={"group": "unit", "median": "agreement_median", "min": "agreement_min", "max": "agreement_max", "count": "agreement_n_roi"}), on="unit", how="left")
    if nd.agreement_median.isna().any():
        raise ValueError("13묶음 이름이 S2 일치도 표와 맞지 않는다")
    out_tables = dict(network_drops=nd, network_drops_per_emotion=pd.DataFrame(tables["network_drops_per_emotion"]), roi_drops=pd.DataFrame(tables["roi_drops"]),
                      coverage=runs.merge(pd.DataFrame(cov), on=["seed", "fold"], how="left") if cov else runs)
    if missing:
        out_tables["missing"] = pd.DataFrame(missing)
    info = dict(stage="S10 6-4b perturb", perturb_dir=str(perturb_dir), s6_dir=str(s6_dir) if s6_dir else None, difference=DIFF, uncertainty=NO_UNCERTAINTY,
                holm_13="내지 않음(구간과 p가 없다)", partial_check=bool(missing), **(extra_info or {}))
    if missing:
        info["note"] = I.PARTIAL_NOTE
    return I.write_out(out, out_tables, info, started, arrays)


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 6-4b 네트워크 단위 입력 교란")
    ap.add_argument("--perturb-dir", required=True, help="<output_root>/s9_saved_models/perturb/<S6 결과 폴더 이름>")
    ap.add_argument("--s6-dir", default=None, help="원래 예측의 합을 S6 시험 예측과 대조할 S6 결과 폴더(선택)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", required=True)
    ap.add_argument("--partial-check", action="store_true")
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args(argv)
    c.guard(a.design_freeze)
    split = c.load_split()
    y, cols = c.load_scores(split, "emotions")
    info = run(a.perturb_dir, a.out, split, np.asarray(y, np.float64), I.emotion_names(cols), s6_dir=a.s6_dir, partial_check=a.partial_check, overwrite=a.overwrite,
               extra_info=dict(design_freeze=a.design_freeze))
    print(f"끝: {a.out} ({info['elapsed_seconds']}초)")


if __name__ == "__main__":
    main()
