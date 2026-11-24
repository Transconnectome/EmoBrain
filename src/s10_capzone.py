#!/usr/bin/env python3
"""S10 Dec-바(01 6-2b) 요약: 캡션으로 묶은 상황을 학습에서 통째로 뺀 분할에서 A-1, C-1, D-3, D-4(11/22). GPU 없음.

입력: S6 결과 폴더 s6_brain_capzone. 분할마다 capzone_block<b>_fold<k>_<excluded|control>/{plan, brain_only, brain_decoded,
brain_features_only, brain_frozen_feature_encoder}. A-1은 s6_train, C-1, D-3, D-4는 s9_capzone_models.py가 학습했다.
- 구역 5개(S2 caption_blocks_assignment.tsv) × fold 6개 × 제외 방식 2개 × 모델 4개가 모두 있어야 최종 표를 낸다. 빠지면 목록을 적고 멈춘다.
- 확인: plan.json의 영상이 c.zone_sets(캡션 구역 표)와 같고, 두 제외 방식의 시험 영상이 같고, 예측 행이 plan/rows.npz의 시험 행과 같다.
  같은 구역에서 여덟 설정(모델 4 × 제외 방식 2)의 참가자별 영상이 같다.
계산은 6-2(src/s10_zone.py)와 같다
- 구역마다 6 fold의 시험 예측을 모아 참가자별, 정서별 r. 평가 정서 목록과 상수 처리도 6-2와 같다(--constant-prediction-scope).
- 요약값: 구역마다 평가 정서의 r 평균, 다섯 구역을 같은 무게로 평균한 값. 5명 평균은 참가자 값의 평균.
- 모델마다 구역 제외 성능, 학습량 대조 성능, 하락폭(대조 − 제외).
- 비교(01 6-2b): 모델마다 (모델 − A-1)의 "구역 제외 성능의 차이(더 높다)"와 "하락폭의 차이(덜 떨어진다)"를 따로 낸다.
  중심은 D-3 − A-1이다. 하락폭의 차이(D-3 하락폭 − A-1 하락폭)가 0보다 크면, 처음 보는 상황에서 A-1이 D-3보다 덜 떨어진 것이다.
- 정서별: 정서마다 다섯 구역 평균의 하락폭(그 정서를 평가한 구역만)을 모델마다 내고, (모델 − A-1)의 하락폭 차이에 basic 95% 구간,
  중심 맞춘 양측 p, 정서 34개의 BH를 붙인다(탐색). 5명 중 같은 방향 수도 낸다.
재표집: 영상 단위 bootstrap 10,000회(같은 내용 묶음은 함께, 6-2와 같은 seed). 모든 구역, 설정, 5명에 같은 뽑힌 횟수.
출력(레포 밖 --out): capzone_summary.tsv, capzone_drop_per_emotion.tsv, capzone_per_emotion.tsv, capzone_emotions.tsv, constant_predictions.tsv,
  training_nonzero.tsv, test_rating_distribution.tsv, coverage.tsv, run_info.json
사용: s10_capzone.py --capzone-dir <s6_brain_capzone> --out <폴더> --design-freeze <커밋> [--constant-prediction-scope participant|all] [--n-boot 10000] [--overwrite]
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

import s4_common as c
import s6_common as S
import s10_inputs as I
import s10_performance as perf
import s10_stats as st
from s10_zone import KINDS, SCOPES, pool, rating_distribution, zone_videos

MODELS = ("brain_only", "brain_decoded", "brain_features_only", "brain_frozen_feature_encoder")
SHORT = {"brain_only": "A-1", "brain_decoded": "C-1", "brain_features_only": "D-3", "brain_frozen_feature_encoder": "D-4"}
REF = "brain_only"


def plan_name(b, k, kind):
    return f"capzone_block{b}_fold{k}_{kind}"


def pred_path(sd, cond):
    """짝 학습 조건(D-4)은 네 짝 평균(ensemble)이 시험 예측이다."""
    return sd / "ensemble" / "test_pred.npz" if S.CONDITIONS[cond].paired else sd / "test_pred.npz"


def load_runs(cap_dir, split, blocks_table, control_table, y):
    blocks = sorted(int(b) for b in blocks_table.block.unique())
    preds, cov, missing, nonzero = {}, [], [], []
    pos = {v: i for i, v in enumerate(split.video_id.astype(int).tolist())}
    for b in blocks:
        for k in range(1, I.N_FOLDS + 1):
            tests = {}
            for kind in KINDS:
                d = Path(cap_dir) / plan_name(b, k, kind)
                if not (d / "plan" / "plan.json").exists():
                    missing += [dict(block=b, fold=k, kind=kind, condition=m, what="plan") for m in MODELS]
                    continue
                plan = json.loads((d / "plan" / "plan.json").read_text())
                train_val, test = c.zone_sets(split, b, k, kind, blocks_table, control_table)
                if sorted(plan["train"] + plan["val"]) != sorted(train_val) or sorted(plan["test"]) != sorted(test):
                    raise ValueError(f"{d}: plan.json의 영상이 캡션 구역 분할(c.zone_sets)과 다르다")
                tests[kind] = sorted(test)
                yy = y[[pos[int(v)] for v in plan["train"]]]
                nonzero.append(dict(block=b, fold=k, kind=kind, n_videos=len(plan["train"]), **{f"e{e}": int((yy[:, e] > 0).sum()) for e in range(y.shape[1])}))
                want = I.plan_test_rows(d)
                for cond in MODELS:
                    seeds = I.selected_seeds(d, cond)
                    if not seeds:
                        missing.append(dict(block=b, fold=k, kind=kind, condition=cond, what="selected.json"))
                        continue
                    for seed, sd in seeds.items():
                        path = pred_path(sd, cond)
                        if not path.exists():
                            missing.append(dict(block=b, fold=k, kind=kind, condition=cond, what=f"seed {seed} {path.name}"))
                            continue
                        preds[seed, cond, kind, b, k] = I.load_test_pred(path, want, y.shape[1])
                        cov.append(dict(block=b, fold=k, kind=kind, condition=cond, seed=seed, path=str(path), n_rows=len(want)))
            if len(tests) == 2 and tests["excluded"] != tests["control"]:
                raise ValueError(f"구역 {b} fold {k}: 두 제외 방식의 시험 영상이 다르다")
    return preds, pd.DataFrame(cov), missing, pd.DataFrame(nonzero)


def analyze_seed(seed, preds, split, y, emotions, blocks_table, W, codes, upos, scope):
    ypos = {v: i for i, v in enumerate(split.video_id.astype(int).tolist())}
    settings = [(m, k) for m in MODELS for k in KINDS]
    emo_rows, list_rows, const_rows = [], [], []
    score, sboot = {}, {}
    E, B = len(emotions), W.shape[0]
    dsum, dbsum, dcnt = {}, {}, {}  # (모델, 참가자) -> 정서별 하락폭 합, bootstrap 합, 구역 수
    for b in sorted(int(x) for x in blocks_table.block.unique()):
        pooled = {s: pool(preds, seed, s[0], s[1], b) for s in settings}
        if any(pooled[s] is None for s in settings):
            raise SystemExit(f"구역 {b}: 여덟 설정 가운데 빠진 것이 있다")
        zv = zone_videos(blocks_table, split, b)
        zone_ok = ~st.constant_columns(y[[ypos[v] for v in zv]])
        pids = sorted(pooled[settings[0]])
        for s in settings:
            if sorted(pooled[s]) != pids or any(not np.array_equal(pooled[s][q][0], pooled[settings[0]][q][0]) for q in pids):
                raise ValueError(f"구역 {b}: 설정 {s}의 참가자별 영상이 다른 설정과 다르다(N11)")
        part_const = np.zeros(E, bool)
        for q in pids:
            part_const |= st.constant_columns(y[[ypos[int(v)] for v in pooled[settings[0]][q][0]]]) & zone_ok
        evaluated = zone_ok & ~part_const
        list_rows.append(dict(seed=seed, block=b, n_test_videos=len(zv), n_evaluated=int(evaluated.sum()),
                              rating_constant=",".join(emotions[e] for e in np.flatnonzero(~zone_ok)),
                              rating_constant_in_participant=",".join(emotions[e] for e in np.flatnonzero(part_const))))
        drop = {q: np.zeros(E, bool) for q in pids}
        for q in pids:
            for s in settings:
                cp = st.constant_columns(pooled[s][q][1]) & evaluated
                const_rows += [dict(seed=seed, block=b, participant=q, model=SHORT[s[0]], kind=s[1], emotion=emotions[e]) for e in np.flatnonzero(cp)]
                drop[q] |= cp
        if any(d.any() for d in drop.values()):
            if scope not in SCOPES:
                raise SystemExit(f"구역 {b}: 상수만 예측한 정서가 있다. 뺄 범위를 --constant-prediction-scope {SCOPES}로 정해야 한다(문서가 정하지 않음)")
            if scope == "all":
                every = np.any(np.stack(list(drop.values())), 0)
                drop = {q: every for q in pids}
        for q in pids:
            v, _ = pooled[settings[0]][q]
            upos_q = np.array([upos[int(x)] for x in v])
            yq = y[[ypos[int(x)] for x in v]]
            keep = evaluated & ~drop[q]
            rb = st.boot_r(W[:, codes[upos_q]], yq, {s: pooled[s][q][1] for s in settings})
            r = {s: st.pearson_columns(yq, pooled[s][q][1]) for s in settings}
            for s in settings:
                score[s, b, q] = float(r[s][keep].mean())
                sboot[s, b, q] = st.mean_over(rb[s], keep)
                lo, hi = st.basic_ci(r[s], rb[s])
                emo_rows += [dict(seed=seed, block=b, participant=q, model=SHORT[s[0]], kind=s[1], emotion=emotions[e], r=r[s][e], ci_low=lo[e], ci_high=hi[e],
                                  used_in_mean=bool(keep[e])) for e in range(E)]
            for m in MODELS:
                d_pt = np.where(keep, r[m, "control"] - r[m, "excluded"], 0.0)
                d_bt = np.where(keep[None, :], rb[m, "control"] - rb[m, "excluded"], 0.0)
                dsum[m, q] = dsum.get((m, q), np.zeros(E)) + d_pt
                dbsum[m, q] = dbsum.get((m, q), np.zeros((B, E))) + d_bt
                dcnt[m, q] = dcnt.get((m, q), np.zeros(E)) + keep
    with np.errstate(invalid="ignore", divide="ignore"):
        dmean = {k: dsum[k] / dcnt[k] for k in dsum}
        dbmean = {k: dbsum[k] / dcnt[k][None, :] for k in dbsum}
    return score, sboot, dmean, dbmean, dict(capzone_per_emotion=pd.DataFrame(emo_rows), capzone_emotions=pd.DataFrame(list_rows),
                                             constant_predictions=pd.DataFrame(const_rows, columns=["seed", "block", "participant", "model", "kind", "emotion"]))


def summarize(seed, score, sboot, blocks):
    rows = []
    pids = sorted({q for (_, _, q) in score})
    for label, bs in [(f"구역 {b}", [b]) for b in blocks] + [("다섯 구역 평균", list(blocks))]:
        for q in pids + ["mean5"]:
            qs = pids if q == "mean5" else [q]
            val = {s: float(np.mean([np.mean([score[s, b, x] for b in bs]) for x in qs])) for s in [(m, k) for m in MODELS for k in KINDS]}
            bt = {s: np.mean([np.mean([sboot[s, b, x] for b in bs], 0) for x in qs], 0) for s in val}
            per = {s: [float(np.mean([score[s, b, x] for b in bs])) for x in pids] for s in val}

            def add(model, quantity, est, boot, test=False, per_q=None):
                lo, hi = I.ci_row(est, boot)
                row = dict(seed=seed, participant=q, scope=label, model=model, quantity=quantity, estimate=est, ci_low=lo, ci_high=hi,
                           p_raw=float(st.centered_p(est, boot)) if test else np.nan, n_boot_valid=int(np.isfinite(boot).sum()))
                if per_q is not None and q == "mean5":
                    row.update(n_positive=int(sum(x > 0 for x in per_q)), n_negative=int(sum(x < 0 for x in per_q)))
                rows.append(row)

            for m in MODELS:
                ex, ct = (m, "excluded"), (m, "control")
                add(SHORT[m], "구역 제외 성능(절대)", val[ex], bt[ex])
                add(SHORT[m], "학습량 대조 성능", val[ct], bt[ct])
                add(SHORT[m], "하락폭(대조 − 제외)", val[ct] - val[ex], bt[ct] - bt[ex])
            for m in MODELS:
                if m == REF:
                    continue
                ex, rex = (m, "excluded"), (REF, "excluded")
                add(f"{SHORT[m]} − A-1", "구역 제외 성능의 차이(더 높다)", val[ex] - val[rex], bt[ex] - bt[rex], test=True,
                    per_q=[a - b for a, b in zip(per[ex], per[rex])])
                dm = val[m, "control"] - val[m, "excluded"]
                dr = val[REF, "control"] - val[REF, "excluded"]
                bm = bt[m, "control"] - bt[m, "excluded"]
                br = bt[REF, "control"] - bt[REF, "excluded"]
                pm = [a - b for a, b in zip(per[m, "control"], per[m, "excluded"])]
                pr = [a - b for a, b in zip(per[REF, "control"], per[REF, "excluded"])]
                add(f"{SHORT[m]} − A-1", "하락폭의 차이(덜 떨어진다)", dm - dr, bm - br, test=True, per_q=[a - b for a, b in zip(pm, pr)])
    return pd.DataFrame(rows)


def drop_per_emotion(seed, dmean, dbmean, emotions):
    pids = sorted({q for (_, q) in dmean})
    rows = []
    mean5 = {m: np.nanmean(np.stack([dmean[m, q] for q in pids]), 0) for m in MODELS}
    boot5 = {m: np.nanmean(np.stack([dbmean[m, q] for q in pids]), 0) for m in MODELS}
    for m in MODELS:
        lo, hi = st.basic_ci(mean5[m], boot5[m])
        rows += [dict(seed=seed, model=SHORT[m], quantity="하락폭(대조 − 제외)", emotion=emotions[e], estimate=mean5[m][e], ci_low=lo[e], ci_high=hi[e]) for e in range(len(emotions))]
    for m in MODELS:
        if m == REF:
            continue
        d, db = mean5[m] - mean5[REF], boot5[m] - boot5[REF]
        lo, hi = st.basic_ci(d, db)
        p = st.centered_p(d, db)
        ok = np.isfinite(p)
        q_bh = np.full(len(p), np.nan)
        q_bh[ok] = st.bh(p[ok])
        per = np.stack([dmean[m, q] - dmean[REF, q] for q in pids])
        rows += [dict(seed=seed, model=f"{SHORT[m]} − A-1", quantity="하락폭의 차이(덜 떨어진다)", emotion=emotions[e], estimate=d[e], ci_low=lo[e], ci_high=hi[e],
                      p_raw=p[e], p_bh=q_bh[e], n_positive=int((per[:, e] > 0).sum()), n_negative=int((per[:, e] < 0).sum())) for e in range(len(emotions))]
    return pd.DataFrame(rows)


def nonzero_table(nonzero, emotions):
    long = nonzero.melt(id_vars=["block", "fold", "kind", "n_videos"], var_name="e", value_name="n_nonzero")
    long["emotion"] = [emotions[int(x[1:])] for x in long.e]
    long = long.drop(columns="e")
    ref = pd.read_csv(c.S2 / "caption_block_nonzero.tsv", sep="\t").set_index(["block", "fold", "emotion"])
    col = {"excluded": "n_nonzero_excluded", "control": "n_nonzero_control"}
    long["s2_value"] = [ref.loc[(b, k, e), col[kind]] if (b, k, e) in ref.index else np.nan for b, k, e, kind in zip(long.block, long.fold, long.emotion, long.kind)]
    long["matches_s2"] = long.n_nonzero == long.s2_value
    return long


def run(cap_dir, out, split, y, emotions, *, scope=None, n_boot=st.N_RESAMPLE, overwrite=False, extra_info=None):
    started = time.time()
    out = I.prepare_out(out, overwrite)
    blocks_table, control_table = (pd.read_csv(p, sep="\t") for p in S.CAPTION_BLOCKS)
    blocks = sorted(int(b) for b in blocks_table.block.unique())
    preds, cov, missing, nonzero = load_runs(cap_dir, split, blocks_table, control_table, y)
    I.require_complete(missing, False, "Dec-바")
    U = np.array(sorted(set(split.video_id.astype(int)) & set(blocks_table.video_id.astype(int))), np.int64)
    upos = {int(v): i for i, v in enumerate(U)}
    codes, n_units = st.unit_codes(split.set_index("video_id").loc[U].canonical_id.to_numpy())
    W = st.bootstrap_counts(n_units, n_boot, np.random.default_rng(perf.BOOT_SEED)).astype(np.float64)
    tables = {}
    for seed in sorted({k[0] for k in preds}):
        score, sboot, dmean, dbmean, t = analyze_seed(seed, preds, split, y, emotions, blocks_table, W, codes, upos, scope)
        t.update(capzone_summary=summarize(seed, score, sboot, blocks), capzone_drop_per_emotion=drop_per_emotion(seed, dmean, dbmean, emotions))
        for k, v in t.items():
            tables[k] = pd.concat([tables[k], v], ignore_index=True) if k in tables else v
    tables["training_nonzero"] = nonzero_table(nonzero, emotions)
    tables["test_rating_distribution"] = rating_distribution(split, y, emotions, blocks_table)
    tables["coverage"] = cov
    info = dict(stage="S10 Dec-바 caption zones", capzone_dir=str(cap_dir), blocks=blocks, models={m: SHORT[m] for m in MODELS},
                settings=dict(n_boot=n_boot, boot_seed=perf.BOOT_SEED, bootstrap_unit="video", constant_prediction_scope=scope),
                n_constant_predictions=len(tables["constant_predictions"]), training_nonzero_matches_s2=bool(tables["training_nonzero"].matches_s2.all()), **(extra_info or {}))
    if n_boot != st.N_RESAMPLE:
        info["note_resample"] = f"재표집 횟수가 I5의 {st.N_RESAMPLE}회와 다르다. 점검용 실행이다"
    return I.write_out(out, tables, info, started)


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 Dec-바 캡션 구역 제외: A-1, C-1, D-3, D-4")
    ap.add_argument("--capzone-dir", required=True, help="<output_root>/s6_brain_capzone")
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", required=True)
    ap.add_argument("--constant-prediction-scope", choices=SCOPES, default=None)
    ap.add_argument("--n-boot", type=int, default=st.N_RESAMPLE)
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args(argv)
    c.guard(a.design_freeze)
    split = c.load_split()
    y, cols = c.load_scores(split, "emotions")
    info = run(a.capzone_dir, a.out, split, np.asarray(y, np.float64), I.emotion_names(cols), scope=a.constant_prediction_scope, n_boot=a.n_boot,
               overwrite=a.overwrite, extra_info=dict(design_freeze=a.design_freeze))
    print(f"끝: {a.out} ({info['elapsed_seconds']}초)")


if __name__ == "__main__":
    main()
