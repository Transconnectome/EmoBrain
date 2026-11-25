#!/usr/bin/env python3
"""S10 6-3 MC 시청 전이 (04 S10 MC 시청 전이, 01 6-3, 6-1, G14, O4 (1), (5), O30, 2026-11-15). GPU 없음.

입력: S8 결과(s8_mc_transfer.py). <S8 폴더>/<조건>/seed<k>/mc-0X/{done.json, test_pred_wd<고른 값>.npz, scoring.npz}.
- 조건 A-1, C-1 × seed 0, 1, 2 × MC 참가자 5명(S2~S6, MC_PIDS)이 모두 있어야 최종 표를 낸다. 빠지면 목록을 적고 멈춘다(--partial-check는 점검용).
- done.json의 hk_plan이 final_for_mc가 아니면(S8 확인용 실행) 멈춘다. --allow-check-run을 주면 읽기 점검만 한다.
- 확인: 시험 영상이 72개이고 서로 다른 내용이며, 한 참가자의 두 조건, 세 seed가 같은 영상과 같은 사람 평정(scoring.npz)을 쓴다.
계산(01 6-3)
- 참가자별, 정서별로 72개 영상에 걸친 Pearson r. 34개를 평균해 참가자 점수를 낸다. seed마다 따로 내고, seed 3개를 참가자처럼 다루지 않는다(평균과 표준편차만, G14).
- 72개 시험 영상에서 사람 평정이 모두 같은 정서는 두 조건 모두에서 빼고 그 수를 낸다.
- 예측이 일정한 정서는 따로 적고, 한 모델에서만 빼지 않고 두 모델에서 함께 뺀다. 뺄 범위(그 참가자와 seed만, 모든 참가자와 seed)는 문서가 정하지 않아
  --constant-prediction-scope로 받고 기본값이 없다. 상수 예측이 없으면 묻지 않는다.
- 검정(6-1 규칙, O4 (5) 보정 없음): 각 모델의 점수 대 순열 기준(72개 안에서 섞음, O4 (1), 한쪽 p), 두 모델의 차이(C-1 − A-1)의 basic 95% 구간과 중심 맞춘 양측 p.
  bootstrap은 72개 영상 단위 10,000회다. 시험 영상이 72개뿐이라 구간이 넓을 수 있다(표의 note).
- C-1 decoded features의 2-1 지표: HK 최종 모델의 D9 통계(scoring.npz, O30)로 되돌린 원래 척도에서 72개 영상의 차원별 r 평균. 관찰 값만 낸다.
출력(레포 밖 --out): mc_scores.tsv, mc_comparison.tsv, mc_per_emotion.tsv, mc_seed_summary.tsv, mc_decoding.tsv, constant_predictions.tsv, coverage.tsv, run_info.json
사용: s10_mc.py --mc-dir <S8 결과 폴더> --out <출력 폴더> --design-freeze <커밋> [--constant-prediction-scope unit|all] [--n-boot 10000] [--n-perm 10000] [--partial-check] [--allow-check-run] [--overwrite]
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

import s4_common as c
import s10_inputs as I
import s10_performance as perf
import s10_stats as st

MODELS = ("brain_only", "brain_decoded")
SHORT = {"brain_only": "A-1", "brain_decoded": "C-1"}
SEEDS = (0, 1, 2)  # G14, 6-3
MC_PIDS = tuple(f"mc-0{i}" for i in range(2, 7))  # 11/25 석진 님: S1은 MC에서 뺀다(이유는 01 6-3)
SCOPES = ("unit", "all")
WIDE_NOTE = "시험 영상이 72개뿐이라 구간이 넓을 수 있다(6-3). 보정 없음(O4 (5))"


def load_units(mc_dir, allow_check_run):
    """돌려주는 값: (조건, seed, 참가자) -> dict(video_id, p, y, decoded, stats), 기록, 빠진 목록."""
    units, rows, missing = {}, [], []
    for cond in MODELS:
        for seed in SEEDS:
            for q in MC_PIDS:
                d = Path(mc_dir) / cond / f"seed{seed}" / q
                if not (d / "done.json").exists():
                    missing.append(dict(condition=cond, seed=seed, participant=q))
                    continue
                done = json.loads((d / "done.json").read_text())
                hk_plan = done.get("settings", {}).get("hk_plan")
                if hk_plan != "final_for_mc" and not allow_check_run:
                    raise SystemExit(f"{d}: hk_plan이 {hk_plan}이다. S8 확인용 실행은 결과로 쓰지 않는다(--allow-check-run은 읽기 점검만)")
                if done.get("condition") != cond or int(done.get("seed")) != seed or done.get("participant") != q:
                    raise ValueError(f"{d}: done.json의 조건, seed, 참가자가 폴더와 다르다")
                wd = float(done["chosen_input_wd"])
                pred = np.load(d / f"test_pred_wd{wd:g}.npz")
                sc = np.load(d / "scoring.npz")
                vid = pred["video_id"].astype(np.int64)
                if not np.array_equal(vid, sc["video_id"].astype(np.int64)) or len(vid) != 72 or len(set(vid.tolist())) != 72:
                    raise ValueError(f"{d}: 시험 영상이 72개가 아니거나 예측과 채점 파일의 영상이 다르다")
                o = np.argsort(vid)  # 영상 번호 순서로 맞춘다. 모든 참가자, 조건, seed에서 같은 자리가 같은 영상이다
                p = np.asarray(pred["p"], np.float64)[o]
                if p.shape != (72, 34) or not np.isfinite(p).all():
                    raise ValueError(f"{d}: 예측 크기 {p.shape}가 다르거나 NaN이 있다")
                u = dict(video_id=vid[o], p=p, y=np.asarray(sc["y"], np.float64)[o], hk_plan=hk_plan, input_wd=wd)
                if cond == "brain_decoded":
                    u["decoded"] = {"vision": (np.asarray(pred["v_hat"], np.float64) * sc["visual_std"] + sc["visual_mean"])[o],
                                    "caption": (np.asarray(pred["c_hat"], np.float64) * sc["caption_std"] + sc["caption_mean"])[o]}
                    u["actual"] = {"vision": np.asarray(sc["vision"], np.float64)[o], "caption": np.asarray(sc["caption"], np.float64)[o]}
                units[cond, seed, q] = u
                rows.append(dict(condition=cond, seed=seed, participant=q, path=str(d), hk_plan=hk_plan, chosen_input_wd=wd, n_videos=len(vid)))
    return units, pd.DataFrame(rows), missing


def run(mc_dir, out, *, scope=None, n_boot=st.N_RESAMPLE, n_perm=st.N_RESAMPLE, partial_check=False, allow_check_run=False, overwrite=False, extra_info=None, emotions=None):
    started = time.time()
    out = I.prepare_out(out, overwrite)
    if scope is not None and scope not in SCOPES:
        raise ValueError(f"--constant-prediction-scope는 {SCOPES} 가운데 하나다")
    emotions = I.emotion_names() if emotions is None else emotions
    units, cov, missing = load_units(mc_dir, allow_check_run)
    I.require_complete(missing, partial_check, "6-3")
    if not units:
        raise SystemExit("읽은 MC 결과가 없다")
    pids = sorted({q for _, _, q in units})
    ref = {}
    for (cond, seed, q), u in units.items():  # 한 참가자의 모든 단위가 같은 영상, 같은 사람 평정
        r = ref.setdefault(q, (u["video_id"], u["y"]))
        if not (np.array_equal(r[0], u["video_id"]) and np.allclose(r[1], u["y"])):
            raise ValueError(f"{q}: 조건이나 seed 사이에 시험 영상이나 사람 평정이 다르다")
    vids0, y0 = ref[pids[0]]
    for q in pids:
        if not np.array_equal(ref[q][0], vids0):
            raise ValueError("MC 참가자마다 시험 영상 72개가 다르다")
    rating_const = st.constant_columns(y0)  # 72개에서 평정이 모두 같은 정서(참가자마다 같은 72개)
    const_rows = []
    for (cond, seed, q), u in sorted(units.items()):
        for e in np.flatnonzero(st.constant_columns(u["p"]) & ~rating_const):
            const_rows.append(dict(condition=SHORT[cond], seed=seed, participant=q, emotion=emotions[e]))
    drop = {}
    if const_rows:
        if scope is None:
            raise SystemExit(f"예측이 일정한 정서가 있다({len(const_rows)}개). 두 모델에서 함께 뺄 범위를 --constant-prediction-scope {SCOPES}로 정해야 한다(문서가 정하지 않음)")
        ct = pd.DataFrame(const_rows)
        names = set(ct.emotion) if scope == "all" else None
        for (cond, seed, q) in units:
            sel = names if scope == "all" else set(ct.emotion[(ct.seed == seed) & (ct.participant == q)])
            drop[seed, q] = np.isin(emotions, list(sel))
    rng_b = np.random.default_rng(perf.BOOT_SEED)
    W = st.bootstrap_counts(72, n_boot, rng_b).astype(np.float64)  # 72개 영상 단위, 모든 참가자와 seed 공통
    perm = st.block_permutations(np.zeros(72, int), n_perm, np.random.default_rng(perf.PERM_SEED)) if n_perm > 0 else np.empty((0, 72), np.int32)  # O4 (1). 72개 안에서
    scores, comps, emo, dec = [], [], [], []
    seeds = sorted({s for _, s, _ in units})
    for seed in seeds:
        sc, sb, sn = {}, {}, {}
        for q in pids:
            keyq = [m for m in MODELS if (m, seed, q) in units]
            if not keyq:
                continue
            yq = ref[q][1]  # 영상 번호 순서(load_units). 모든 참가자에서 같은 자리가 같은 영상이라 재표집과 순열을 함께 쓴다
            preds = {m: units[m, seed, q]["p"] for m in keyq}
            keep = ~rating_const & ~drop.get((seed, q), np.zeros(len(emotions), bool))
            rb = st.boot_r(W, yq, preds)
            rn = st.permuted_r(perm, np.arange(72), yq, preds) if n_perm > 0 else {m: np.empty((0, len(emotions))) for m in keyq}
            for m in keyq:
                r = st.pearson_columns(yq, preds[m])
                kp = keep & np.isfinite(r)
                if (keep & ~np.isfinite(r)).any():
                    raise SystemExit(f"{q} seed {seed} {SHORT[m]}: 상수 예측 외의 이유로 계산할 수 없는 r이 있다")
                sc[m, q], sb[m, q] = float(r[kp].mean()), st.mean_over(rb[m], kp)
                sn[m, q] = st.mean_over(rn[m], kp)
                lo, hi = st.basic_ci(r, rb[m])
                ep = st.permutation_p(r, rn[m]) if n_perm > 0 else np.full(len(emotions), np.nan)
                for e in range(len(emotions)):
                    emo.append(dict(seed=seed, participant=q, model=SHORT[m], emotion=emotions[e], r=r[e], ci_low=lo[e], ci_high=hi[e], p_perm=ep[e],
                                    used_in_mean=bool(kp[e]), reason="rating_constant" if rating_const[e] else ("constant_prediction_excluded" if not keep[e] else ""), label="탐색, 보정 없음"))
            if "brain_decoded" in keyq:
                u = units["brain_decoded", seed, q]
                for fname in ("vision", "caption"):
                    m_, nn, _ = I.decoding_scores(u["actual"][fname], u["decoded"][fname])
                    dec.append(dict(seed=seed, participant=q, feature=fname, mean_dim_r=m_, n_dims_noncomputable=nn, n_videos=72))
        for m in MODELS:
            qs = [q for q in pids if (m, q) in sc]
            if not qs:
                continue
            sc[m, "mean_mc"] = float(np.mean([sc[m, q] for q in qs]))
            sb[m, "mean_mc"] = np.mean(np.stack([sb[m, q] for q in qs]), 0)
            sn[m, "mean_mc"] = np.mean(np.stack([sn[m, q] for q in qs]), 0)
            for q in qs + ["mean_mc"]:
                lo, hi = I.ci_row(sc[m, q], sb[m, q])
                nl = sn[m, q]
                scores.append(dict(seed=seed, participant=q, model=SHORT[m], score_r=sc[m, q], ci_low=lo, ci_high=hi, null_mean=float(np.nanmean(nl)) if len(nl) else np.nan,
                                   p_perm=float(st.permutation_p(sc[m, q], nl)) if len(nl) else np.nan, n_emotions_used=int((~rating_const & ~drop.get((seed, q), np.zeros(34, bool))).sum()) if q != "mean_mc" else np.nan,
                                   n_rating_constant=int(rating_const.sum()), note=WIDE_NOTE))
        for q in [x for x in pids if all((m, x) in sc for m in MODELS)] + (["mean_mc"] if all((m, "mean_mc") in sc for m in MODELS) else []):
            d, b = sc["brain_decoded", q] - sc["brain_only", q], sb["brain_decoded", q] - sb["brain_only", q]
            lo, hi = I.ci_row(d, b)
            comps.append(dict(seed=seed, participant=q, comparison="C-1 − A-1", estimate=d, ci_low=lo, ci_high=hi, p_raw=float(st.centered_p(d, b)), note=WIDE_NOTE))
    st_scores = pd.DataFrame(scores)
    tables = dict(mc_scores=st_scores, mc_comparison=pd.DataFrame(comps), mc_per_emotion=pd.DataFrame(emo), mc_decoding=pd.DataFrame(dec),
                  mc_seed_summary=st.seed_summary(st_scores, ["participant", "model"], ["score_r"]) if len(st_scores) else pd.DataFrame(),
                  constant_predictions=pd.DataFrame(const_rows, columns=["condition", "seed", "participant", "emotion"]), coverage=cov)
    if missing:
        tables["missing"] = pd.DataFrame(missing)
    check_run = any(u["hk_plan"] != "final_for_mc" for u in units.values())
    info = dict(stage="S10 6-3 MC", mc_dir=str(mc_dir), settings=dict(n_boot=n_boot, n_perm=n_perm, boot_seed=perf.BOOT_SEED, perm_seed=perf.PERM_SEED, constant_prediction_scope=scope),
                n_rating_constant=int(rating_const.sum()), rating_constant=[emotions[e] for e in np.flatnonzero(rating_const)], n_constant_predictions=len(const_rows),
                partial_check=bool(missing), s8_check_run=check_run, note_wide=WIDE_NOTE, **(extra_info or {}))
    if missing or check_run:
        info["note"] = I.PARTIAL_NOTE if missing else "S8 확인용 실행(hk_plan이 final_for_mc가 아님)을 읽은 점검이다. 결과로 쓰지 않는다"
    if n_perm != st.N_RESAMPLE or n_boot != st.N_RESAMPLE:
        info["note_resample"] = f"재표집 횟수가 I5의 {st.N_RESAMPLE}회와 다르다. 점검용 실행이다"
    return I.write_out(out, tables, info, started)


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 6-3 MC 시청 전이")
    ap.add_argument("--mc-dir", required=True, help="S8 결과 폴더(<output_root>/s8_mc)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", required=True)
    ap.add_argument("--constant-prediction-scope", choices=SCOPES, default=None, help="예측이 일정한 정서를 두 모델에서 뺄 범위. 문서가 정하지 않아 기본값이 없다")
    ap.add_argument("--n-boot", type=int, default=st.N_RESAMPLE)
    ap.add_argument("--n-perm", type=int, default=st.N_RESAMPLE)
    ap.add_argument("--partial-check", action="store_true")
    ap.add_argument("--allow-check-run", action="store_true", help="S8 확인용 실행(hk_plan outer_fold<k>)을 읽기 점검으로만 읽는다")
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args(argv)
    c.guard(a.design_freeze)
    info = run(a.mc_dir, a.out, scope=a.constant_prediction_scope, n_boot=a.n_boot, n_perm=a.n_perm, partial_check=a.partial_check, allow_check_run=a.allow_check_run,
               overwrite=a.overwrite, extra_info=dict(design_freeze=a.design_freeze))
    print(f"끝: {a.out} ({info['elapsed_seconds']}초)")


if __name__ == "__main__":
    main()
