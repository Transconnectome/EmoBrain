#!/usr/bin/env python3
"""S10 6-2 학습에서 제외한 내용 구역(처음 보는 장면) (04 S10 처음 보는 장면, 01 6-2, 4-3, 6-1, O4, O20, 2026-11-15). GPU 없음.

입력: S6 구역 분할 결과 폴더(S6_OUT=s6_brain_zone). 분할마다 <폴더>/zone_block<b>_fold<k>_<excluded|control>/{plan, brain_only, brain_decoded}.
- 구역 5개(S2 content_blocks.tsv) × fold 6개 × 제외 방식 2개 × 조건 2개가 모두 있어야 최종 표를 낸다. 빠지면 목록을 적고 멈춘다(--partial-check는 점검용).
- 확인: plan.json의 학습, 검증, 시험 영상이 c.zone_sets(4-3의 표)와 같고, 두 제외 방식의 시험 영상이 같다. 예측 행은 plan/rows.npz의 시험 행과 같다(N11).
  같은 구역에서 네 설정(A-1, C-1 × 구역 제외, 학습량 대조)의 참가자별 영상이 같다.
계산(01 6-2, 04 S10)
- 구역마다 6 fold의 시험 예측을 모아 참가자별, 정서별 r을 낸다. 다섯 구역을 섞은 r 하나로 대신하지 않는다.
- 평가 정서 목록: 구역마다 그 구역 시험 영상에서 사람 평정이 모두 같은 정서만 뺀다. 네 설정에 같은 목록을 쓰고 구역마다 정서 수를 낸다.
  어느 참가자의 구역 영상에서만 평정이 상수가 되는 정서는 그 구역에서 모든 참가자의 평가 목록에서 뺀다(11/17 석진 님 결정. 참가자 사이 목록을 같게 둔다).
  뺀 정서는 zone_emotions.tsv의 rating_constant_in_participant에, 정서별 표의 reason에 적는다.
- 모델이 상수만 예측한 정서는 사람 평정이 상수인 경우와 따로 세고, 그 구역에서 네 설정 모두의 평균에서 뺀다. 어느 모델, 어느 정서인지 적는다.
  뺄 범위(그 참가자만, 모든 참가자)는 문서가 정하지 않아 --constant-prediction-scope로 받고 기본값이 없다. 상수 예측이 없으면 묻지 않는다.
- 요약값: 구역마다 평가 정서의 r 평균, 다섯 구역을 같은 무게로 평균한 "다섯 내용 구역의 평균 성능". 5명 평균은 참가자 값의 평균이다.
- 낼 것: 절대 성능(구역 제외), 학습량 대조의 성능, 하락폭(대조 − 제외), 두 모델의 차이(C-1 − A-1), 구역별 결과.
  "더 높다"(구역 제외 성능의 차이, [사전] 처음 보는 장면)와 "덜 떨어진다"(하락폭의 차이, 방향 없음)는 따로 낸다.
- 정서별로 남은 0이 아닌 학습 영상 수(두 제외 방식, plan.json의 학습과 검증 영상. S2 content_block_nonzero.tsv와 대조), 시험 쪽 사람 평정 분포.
- C-1 decoded features의 2-1 지표(차원별 r 평균, O20의 원래 척도, 구역마다 6 fold를 모음). 관찰 값만 낸다.
- 보조 모델(ridge, Stimulus Model)의 구역 결과는 입력이 아직 없어 넣지 않는다.
재표집(6-1, I5, O4 (3)): 영상 단위 bootstrap 10,000회(같은 내용 묶음은 함께, 1부와 같은 seed). 모든 구역, 설정, 5명에 같은 뽑힌 횟수를 쓴다.
  구간은 basic 95%, 차이의 p는 중심을 맞춘 양측 검정이다. --bootstrap-unit run은 민감도다.
출력(레포 밖 --out): zone_summary.tsv, prereg_pvalues.tsv, zone_per_emotion.tsv, zone_emotions.tsv, constant_predictions.tsv, training_nonzero.tsv, test_rating_distribution.tsv,
  c1_zone_decoding.tsv, coverage.tsv, run_info.json
사용: s10_zone.py --zone-dir <S6 구역 결과 폴더> --out <출력 폴더> --design-freeze <커밋> [--constant-prediction-scope participant|all] [--bootstrap-unit video|run] [--n-boot 10000] [--partial-check] [--overwrite]
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

MODELS = ("brain_only", "brain_decoded")  # A-1, C-1(상호작용 head). s6_common.ZONE_CONDITIONS
KINDS = ("excluded", "control")
SHORT = {"brain_only": "A-1", "brain_decoded": "C-1"}
SCOPES = ("participant", "all")
TEST_ID = "처음 보는 장면"


def plan_name(b, k, kind):
    return f"zone_block{b}_fold{k}_{kind}"


def load_runs(zone_dir, split, blocks_table, control_table, y):
    """모든 구역 분할. 돌려주는 값: preds[(seed, 조건, 방식, 구역, fold)] = 참가자 -> (영상, p), decoded[...] = 참가자 -> (영상, vision, caption), 기록, 빠진 목록."""
    blocks = sorted(blocks_table.block.unique())
    preds, decoded, cov, missing, nonzero = {}, {}, [], [], []
    for b in blocks:
        for k in range(1, I.N_FOLDS + 1):
            tests = {}
            for kind in KINDS:
                d = Path(zone_dir) / plan_name(b, k, kind)
                if not (d / "plan" / "plan.json").exists():
                    for cond in MODELS:
                        missing.append(dict(block=b, fold=k, kind=kind, condition=cond, what="plan"))
                    continue
                plan = json.loads((d / "plan" / "plan.json").read_text())
                train_val, test = c.zone_sets(split, b, k, kind, blocks_table, control_table)
                if sorted(plan["train"] + plan["val"]) != sorted(train_val) or sorted(plan["test"]) != sorted(test):
                    raise ValueError(f"{d}: plan.json의 영상이 4-3의 구역 분할(c.zone_sets)과 다르다")
                tests[kind] = sorted(test)
                pos = {v: i for i, v in enumerate(split.video_id.astype(int).tolist())}
                for part in ("train", "val"):
                    yy = y[[pos[int(v)] for v in plan[part]]]
                    nonzero.append(dict(block=b, fold=k, kind=kind, part=part, n_videos=len(plan[part]), **{f"e{e}": int((yy[:, e] > 0).sum()) for e in range(y.shape[1])}))
                want = I.plan_test_rows(d)
                for cond in MODELS:
                    seeds = I.selected_seeds(d, cond)
                    if not seeds:
                        missing.append(dict(block=b, fold=k, kind=kind, condition=cond, what="selected.json"))
                        continue
                    for seed, sd in seeds.items():
                        path = sd / "test_pred.npz"
                        if not path.exists():
                            missing.append(dict(block=b, fold=k, kind=kind, condition=cond, what=f"seed {seed} test_pred.npz"))
                            continue
                        preds[seed, cond, kind, b, k] = I.load_test_pred(path, want, y.shape[1])
                        cov.append(dict(block=b, fold=k, kind=kind, condition=cond, seed=seed, path=str(path), n_rows=len(want)))
                        if cond == "brain_decoded":
                            if (sd / "outputs" / "decoded_test.npz").exists():
                                decoded[seed, kind, b, k] = I.load_decoded(sd, d, want)
                            else:
                                missing.append(dict(block=b, fold=k, kind=kind, condition=cond, what=f"seed {seed} outputs/decoded_test.npz"))
            if len(tests) == 2 and tests["excluded"] != tests["control"]:
                raise ValueError(f"구역 {b} fold {k}: 두 제외 방식의 시험 영상이 다르다")
    return preds, decoded, pd.DataFrame(cov), missing, pd.DataFrame(nonzero)


def pool(preds, seed, cond, kind, b):
    """한 설정, 한 구역의 6 fold를 모은다. fold가 빠지면 None."""
    items = [preds.get((seed, cond, kind, b, k)) for k in range(1, I.N_FOLDS + 1)]
    if any(x is None for x in items):
        return None
    out = {}
    for q in sorted(set().union(*[set(x) for x in items])):
        v = np.concatenate([x[q][0] for x in items if q in x])
        p = np.concatenate([x[q][1] for x in items if q in x])
        o = np.argsort(v)
        out[q] = (v[o], p[o])
    return out


def analyze_seed(seed, preds, split, y, emotions, blocks_table, W, codes, upos, scope):
    """seed 하나. 돌려주는 값: 표들. 설정 = (조건, 방식)."""
    ypos = {v: i for i, v in enumerate(split.video_id.astype(int).tolist())}
    settings = [(m, k) for m in MODELS for k in KINDS]
    zone_rows, emo_rows, list_rows, const_rows = [], [], [], []
    score, sboot = {}, {}  # (설정, 구역, 참가자) -> 값, (B,)
    for b in sorted(int(x) for x in blocks_table.block.unique()):
        pooled = {s: pool(preds, seed, s[0], s[1], b) for s in settings}
        have = [s for s in settings if pooled[s] is not None]
        if not have:
            continue
        zv = zone_videos(blocks_table, split, b)
        yz = y[[ypos[v] for v in zv]]
        zone_ok = ~st.constant_columns(yz)
        pids = sorted(pooled[have[0]])
        for s in have:
            if sorted(pooled[s]) != pids or any(not np.array_equal(pooled[s][q][0], pooled[have[0]][q][0]) for q in pids):
                raise ValueError(f"구역 {b}: 설정 {s}의 참가자별 영상이 다른 설정과 다르다(N11)")
        part_const = np.zeros(len(emotions), bool)  # 11/17 석진 님 결정: 어느 참가자의 구역 영상에서만 상수인 정서는 모든 참가자에서 뺀다
        for q in pids:
            part_const |= st.constant_columns(y[[ypos[int(v)] for v in pooled[have[0]][q][0]]]) & zone_ok
        evaluated = zone_ok & ~part_const
        list_rows.append(dict(seed=seed, block=b, n_test_videos=len(zv), n_evaluated=int(evaluated.sum()), rating_constant=",".join(emotions[e] for e in np.flatnonzero(~zone_ok)),
                              rating_constant_in_participant=",".join(emotions[e] for e in np.flatnonzero(part_const)),
                              settings_found=",".join(f"{SHORT[m]} {k}" for m, k in have)))
        drop = {q: np.zeros(len(emotions), bool) for q in pids}
        for q in pids:
            for s in have:
                cp = st.constant_columns(pooled[s][q][1]) & evaluated
                for e in np.flatnonzero(cp):
                    const_rows.append(dict(seed=seed, block=b, participant=q, model=SHORT[s[0]], kind=s[1], emotion=emotions[e]))
                drop[q] |= cp
        if any(d.any() for d in drop.values()):
            if scope not in SCOPES:
                raise SystemExit(f"구역 {b}: 상수만 예측한 정서가 있다. 그 정서를 뺄 범위를 --constant-prediction-scope {SCOPES}로 정해야 한다(문서가 정하지 않음)")
            if scope == "all":
                every = np.any(np.stack(list(drop.values())), 0)
                drop = {q: every for q in pids}
        for q in pids:
            v, _ = pooled[have[0]][q]
            pos = np.array([upos[int(x)] for x in v])
            yq = y[[ypos[int(x)] for x in v]]
            keep = evaluated & ~drop[q]
            rb = st.boot_r(W[:, codes[pos]], yq, {s: pooled[s][q][1] for s in have})
            for s in have:
                r = st.pearson_columns(yq, pooled[s][q][1])
                score[s, b, q] = float(r[keep].mean())
                sboot[s, b, q] = st.mean_over(rb[s], keep)
                lo, hi = st.basic_ci(r, rb[s])
                for e in range(len(emotions)):
                    emo_rows.append(dict(seed=seed, block=b, participant=q, model=SHORT[s[0]], kind=s[1], emotion=emotions[e], r=r[e], ci_low=lo[e], ci_high=hi[e],
                                         evaluated=bool(evaluated[e]), used_in_mean=bool(keep[e]),
                                         reason="rating_constant" if not zone_ok[e] else ("rating_constant_in_participant" if part_const[e] else ("constant_prediction_excluded" if drop[q][e] else ""))))
            list_rows[-1][f"n_used_{q}"] = int(keep.sum())
    return score, sboot, dict(zone_per_emotion=pd.DataFrame(emo_rows), zone_emotions=pd.DataFrame(list_rows), constant_predictions=pd.DataFrame(const_rows, columns=["seed", "block", "participant", "model", "kind", "emotion"]))


def zone_videos(blocks_table, split, b):
    """구역 b의 개발 영상(모든 fold). 구역의 시험 영상을 6 fold에 걸쳐 모은 것과 같다."""
    dev = set(split.video_id.astype(int))
    return sorted(int(v) for v in blocks_table.video_id[blocks_table.block == b] if int(v) in dev)


def summarize(seed, score, sboot, blocks):
    """구역별 값과 다섯 구역 평균. 차이는 C-1 − A-1, 하락폭은 대조 − 제외."""
    rows, pre = [], []
    pids = sorted({q for (_, _, q) in score})
    scopes = [(f"구역 {b}", [b]) for b in blocks] + [("다섯 구역 평균", list(blocks))]
    for label, bs in scopes:
        for q in pids + ["mean5"]:
            val, bt = {}, {}
            for m in MODELS:
                for k in KINDS:
                    s = (m, k)
                    qs = pids if q == "mean5" else [q]
                    if not all((s, b, x) in score for b in bs for x in qs):
                        continue
                    val[s] = float(np.mean([np.mean([score[s, b, x] for b in bs]) for x in qs]))
                    bt[s] = np.mean([np.mean([sboot[s, b, x] for b in bs], 0) for x in qs], 0)
            def add(model, quantity, est, b, test=False, note=""):
                lo, hi = I.ci_row(est, b)
                p = float(st.centered_p(est, b)) if test else np.nan
                rows.append(dict(seed=seed, participant=q, scope=label, model=model, quantity=quantity, estimate=est, ci_low=lo, ci_high=hi, p_raw=p, note=note,
                                 n_boot_valid=int(np.isfinite(b).sum())))
                return p
            for m in MODELS:
                ex, ct = (m, "excluded"), (m, "control")
                if ex in val:
                    add(SHORT[m], "구역 제외 성능(절대)", val[ex], bt[ex])
                if ct in val:
                    add(SHORT[m], "학습량 대조 성능", val[ct], bt[ct])
                if ex in val and ct in val:
                    add(SHORT[m], "하락폭(대조 − 제외)", val[ct] - val[ex], bt[ct] - bt[ex])
            a, cc = ("brain_only", "excluded"), ("brain_decoded", "excluded")
            if a in val and cc in val:
                p = add("C-1 − A-1", "구역 제외 성능의 차이(더 높다)", val[cc] - val[a], bt[cc] - bt[a], test=True,
                        note="[사전] 처음 보는 장면" if label == "다섯 구역 평균" else "구역별 결과")
                if label == "다섯 구역 평균":
                    pre.append(dict(test_id=TEST_ID, family=q, seed=seed, estimate=val[cc] - val[a], p_raw=p, statistic="다섯 내용 구역의 평균 성능의 차이(C-1 − A-1), 중심 맞춘 양측 bootstrap p",
                                    source="s10_zone", analysis="all"))
            if all((m, k) in val for m in MODELS for k in KINDS):
                da = val["brain_only", "control"] - val["brain_only", "excluded"]
                dc = val["brain_decoded", "control"] - val["brain_decoded", "excluded"]
                ba = bt["brain_only", "control"] - bt["brain_only", "excluded"]
                bc = bt["brain_decoded", "control"] - bt["brain_decoded", "excluded"]
                add("C-1 − A-1", "하락폭의 차이(덜 떨어진다)", dc - da, bc - ba, test=True, note="따로 판정, 방향을 정하지 않음(6-2)")
    return pd.DataFrame(rows), pd.DataFrame(pre, columns=["test_id", "family", "seed", "estimate", "p_raw", "statistic", "source", "analysis"])


def decoding_rows(decoded, split, blocks):
    """C-1 decoded features의 2-1 지표. 구역마다 6 fold를 모은다. 관찰 값만 낸다."""
    rows = []
    for (seed, kind) in sorted({(s, k) for (s, k, _, _) in decoded}):
        for b in blocks:
            items = [decoded.get((seed, kind, b, k)) for k in range(1, I.N_FOLDS + 1)]
            if any(x is None for x in items):
                continue
            for q in sorted(items[0]):
                v = np.concatenate([x[q][0] for x in items])
                vis = np.concatenate([x[q][1] for x in items])
                cap = np.concatenate([x[q][2] for x in items])
                feats = I.actual_features(split, v)
                for name, pred in (("vision", vis), ("caption", cap)):
                    m, nn, _ = I.decoding_scores(feats[name].astype(np.float64), pred)
                    rows.append(dict(seed=seed, kind=kind, block=b, participant=q, feature=name, mean_dim_r=m, n_dims_noncomputable=nn, n_videos=len(v)))
    t = pd.DataFrame(rows)
    if len(t):
        m5 = t.groupby(["seed", "kind", "block", "feature"], as_index=False).mean_dim_r.mean().assign(participant="mean5")
        t = pd.concat([t, m5], ignore_index=True)
    return t


def nonzero_table(nonzero, emotions):
    """정서별 0이 아닌 학습 영상 수(plan.json의 학습, 검증). S2 content_block_nonzero.tsv와 대조한다."""
    long = nonzero.melt(id_vars=["block", "fold", "kind", "part", "n_videos"], var_name="e", value_name="n_nonzero")
    long["emotion"] = [emotions[int(x[1:])] for x in long.e]
    long = long.drop(columns="e")
    s2 = pd.read_csv(c.S2 / "content_block_nonzero.tsv", sep="\t")
    col = {("excluded", "train"): "n_nonzero_excluded", ("control", "train"): "n_nonzero_control", ("excluded", "val"): "n_nonzero_excluded_val", ("control", "val"): "n_nonzero_control_val"}
    ref = s2.set_index(["block", "fold", "emotion"])
    long["s2_value"] = [ref.loc[(b, k, e), col[kind, part]] if (b, k, e) in ref.index else np.nan for b, k, e, kind, part in zip(long.block, long.fold, long.emotion, long.kind, long.part)]
    long["matches_s2"] = long.n_nonzero == long.s2_value
    return long


def rating_distribution(split, y, emotions, blocks_table):
    ypos = {v: i for i, v in enumerate(split.video_id.astype(int).tolist())}
    rows = []
    for b in sorted(int(x) for x in blocks_table.block.unique()):
        yy = y[[ypos[v] for v in zone_videos(blocks_table, split, b)]]
        for e in range(len(emotions)):
            x = yy[:, e]
            rows.append(dict(block=b, emotion=emotions[e], n_videos=len(x), n_nonzero=int((x > 0).sum()), mean=x.mean(), sd=x.std(), median=float(np.median(x)),
                             q90=float(np.quantile(x, 0.9)), max=x.max()))
    return pd.DataFrame(rows)


def run(zone_dir, out, split, y, emotions, *, scope=None, boot_unit="video", n_boot=st.N_RESAMPLE, partial_check=False, overwrite=False, extra_info=None, blocks_table=None, control_table=None):
    started = time.time()
    out = I.prepare_out(out, overwrite)
    if scope is not None and scope not in SCOPES:
        raise ValueError(f"--constant-prediction-scope는 {SCOPES} 가운데 하나다")
    if boot_unit not in ("video", "run"):
        raise ValueError("bootstrap 단위는 video(주) 또는 run(민감도)이다")
    blocks_table = pd.read_csv(c.S2 / "content_blocks_assignment.tsv", sep="\t") if blocks_table is None else blocks_table
    control_table = pd.read_csv(c.S2 / "content_block_control_samples.tsv", sep="\t") if control_table is None else control_table
    blocks = sorted(int(b) for b in blocks_table.block.unique())
    preds, decoded, cov, missing, nonzero = load_runs(zone_dir, split, blocks_table, control_table, y)
    I.require_complete(missing, partial_check, "6-2")
    if not preds:
        raise SystemExit("읽은 구역 예측이 없다")
    U = np.array(sorted(set(split.video_id.astype(int)) & set(blocks_table.video_id.astype(int))), np.int64)
    upos = {int(v): i for i, v in enumerate(U)}
    sp = split.set_index("video_id").loc[U]
    codes, n_units = st.unit_codes(sp.canonical_id.to_numpy() if boot_unit == "video" else sp.run_index.to_numpy())
    W = st.bootstrap_counts(n_units, n_boot, np.random.default_rng(perf.BOOT_SEED)).astype(np.float64)
    tables = {}
    for seed in sorted({k[0] for k in preds}):
        score, sboot, t = analyze_seed(seed, preds, split, y, emotions, blocks_table, W, codes, upos, scope)
        summ, pre = summarize(seed, score, sboot, blocks)
        t.update(zone_summary=summ, prereg_pvalues=pre)
        for k, v in t.items():
            tables[k] = pd.concat([tables[k], v], ignore_index=True) if k in tables else v
    tables["training_nonzero"] = nonzero_table(nonzero, emotions) if len(nonzero) else pd.DataFrame()
    tables["test_rating_distribution"] = rating_distribution(split, y, emotions, blocks_table)
    tables["c1_zone_decoding"] = decoding_rows(decoded, split, blocks)
    tables["coverage"] = cov
    if missing:
        tables["missing"] = pd.DataFrame(missing)
    nz = tables["training_nonzero"]
    info = dict(stage="S10 6-2 zone", zone_dir=str(zone_dir), blocks=blocks, settings=dict(n_boot=n_boot, boot_seed=perf.BOOT_SEED, bootstrap_unit=boot_unit, constant_prediction_scope=scope),
                n_constant_predictions=len(tables["constant_predictions"]), training_nonzero_matches_s2=bool(nz.matches_s2.all()) if len(nz) else None,
                auxiliary_models="ridge와 Stimulus Model의 구역 결과는 입력이 없어 넣지 않았다", partial_check=bool(missing), **(extra_info or {}))
    if missing:
        info["note"] = I.PARTIAL_NOTE
    if n_boot != st.N_RESAMPLE:
        info["note_resample"] = f"재표집 횟수가 I5의 {st.N_RESAMPLE}회와 다르다. 점검용 실행이다"
    return I.write_out(out, tables, info, started)


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 6-2 내용 구역 제외")
    ap.add_argument("--zone-dir", required=True, help="<output_root>/s6_brain_zone")
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", required=True)
    ap.add_argument("--constant-prediction-scope", choices=SCOPES, default=None, help="상수 예측 정서를 그 참가자에서만 뺄지 모든 참가자에서 뺄지. 문서가 정하지 않아 기본값이 없다. 상수 예측이 있을 때만 필요하다")
    ap.add_argument("--bootstrap-unit", choices=("video", "run"), default="video")
    ap.add_argument("--n-boot", type=int, default=st.N_RESAMPLE)
    ap.add_argument("--partial-check", action="store_true")
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args(argv)
    c.guard(a.design_freeze)
    split = c.load_split()
    y, cols = c.load_scores(split, "emotions")
    info = run(a.zone_dir, a.out, split, np.asarray(y, np.float64), I.emotion_names(cols), scope=a.constant_prediction_scope, boot_unit=a.bootstrap_unit, n_boot=a.n_boot,
               partial_check=a.partial_check, overwrite=a.overwrite, extra_info=dict(design_freeze=a.design_freeze))
    print(f"끝: {a.out} ({info['elapsed_seconds']}초)")


if __name__ == "__main__":
    main()
