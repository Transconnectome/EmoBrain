#!/usr/bin/env python3
"""S10 구조 비교와 민감도 (11/16 석진 님). 서로 다른 S6 결과 폴더에 있는 두 모델을 같은 시험 행에서 비교한다. GPU 없음.

쓰임
- F7(N22): ROI token 평균판(emotion query 대신 ROI token 370개 평균) 대 emotion query판. A-1 ROI token 평균판 대 A-1, C-1 ROI token 평균판 대 C-1.
- F3: A-1 encoder block 2개, 4개 대 1개(11/15, 11/16 민감도. 본 설계는 결과와 상관없이 바꾸지 않는다).

계산(s10_stats와 s10_performance의 읽기, 계산을 그대로 쓴다)
- 쌍 하나 = (이름, A 폴더, A 조건, B 폴더, B 조건). 차이는 A − B.
- 참가자마다, 정서마다 6 fold의 시험 예측을 모아 Pearson r을 한 번 낸다(2-3). 두 모델의 시험 행이 같아야 한다(N11). plan의 시험 행도 두 폴더가 같아야 한다.
- 참가자 점수는 두 모델 모두 계산할 수 있는 정서의 r 평균, 5명 평균은 참가자 점수의 평균이다.
- 영상 단위 bootstrap 10,000회(같은 내용 영상 묶음은 함께, 두 모델과 5명에 같은 재표집, 6-1). basic 95% 구간, 중심을 맞춘 양측 p(O4 (3)).
- 정서별 차이는 탐색으로 표시하고 BH-FDR을 쓴다(참가자마다, 쌍마다 34개. 5명 평균도 따로). [사전] 15개의 Holm에 넣지 않고 방향을 미리 정하지 않는다.
- seed 0만 쓴다(seed 1, 2는 11/15에 미룸).
출력(레포 밖 --out): per_emotion.tsv, scores.tsv, run_info.json
사용: s10_sensitivity.py --pair "이름|A 폴더|A 조건|B 폴더|B 조건" [--pair ...] --out <출력 폴더> --design-freeze <커밋> [--n-boot 10000] [--overwrite]
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

import s4_common as c
import s10_performance as perf
import s10_stats as st

SEED = 0


def parse_pair(text):
    parts = [x.strip() for x in text.split("|")]
    if len(parts) != 5 or not all(parts):
        raise SystemExit(f"--pair는 '이름|A 폴더|A 조건|B 폴더|B 조건'이다: {text}")
    return dict(name=parts[0], dir_a=parts[1], cond_a=parts[2], dir_b=parts[3], cond_b=parts[4])


def load_one(s6_dir, cond, split, n_emo):
    """한 폴더의 한 조건(seed 0) 6 fold 예측과 plan의 시험 행."""
    # 그 조건의 selected.json만 읽는다. 실행 폴더에는 조건이 아닌 폴더(ex) feature_encoder_oof)도 있다
    if cond not in perf.S.CONDITIONS:
        raise SystemExit(f"{cond}: 알 수 없는 조건")
    paths = {}
    for k in range(1, perf.N_FOLDS + 1):
        fo = Path(s6_dir) / f"outer_fold{k}"
        sel_path = fo / cond / "selected.json"
        if not sel_path.exists():
            raise SystemExit(f"{sel_path}가 없다. 6 fold가 모두 끝나야 비교한다")
        rel = json.loads(sel_path.read_text())["seeds"].get(str(SEED))
        path = perf.pred_file(fo, cond, rel) if rel else None
        if path is None or not Path(path).exists():
            raise SystemExit(f"{s6_dir} fold {k} {cond} seed {SEED}: 예측 파일이 없다")
        paths[k] = str(path)
    plan_rows = {k: perf.plan_test_rows(s6_dir, k) for k in range(1, perf.N_FOLDS + 1)}
    return perf.load_condition(paths, split, plan_rows, n_emo), plan_rows


def compare(pair, split, y_split, emotions, n_boot):
    n_emo = len(emotions)
    a, rows_a = load_one(pair["dir_a"], pair["cond_a"], split, n_emo)
    b, rows_b = load_one(pair["dir_b"], pair["cond_b"], split, n_emo)
    if rows_a != rows_b:
        raise SystemExit(f"{pair['name']}: 두 폴더의 plan 시험 행이 다르다(N11)")
    videos = perf.same_rows({"A": a, "B": b})
    pids = sorted(videos)
    U = np.array(sorted(set().union(*[set(v.tolist()) for v in videos.values()])), np.int64)
    sp = split.set_index("video_id").loc[U]
    pos_split = {v: i for i, v in enumerate(split.video_id.tolist())}
    yU = np.asarray(y_split, np.float64)[[pos_split[v] for v in U]]
    pos = {q: np.searchsorted(U, videos[q]) for q in pids}
    codes, n_units = st.unit_codes(sp.canonical_id.to_numpy())
    W = st.bootstrap_counts(n_units, n_boot, np.random.default_rng(perf.BOOT_SEED))
    r_obs, r_boot, keep = {}, {}, {}
    for q in pids:
        yq = yU[pos[q]]
        preds = {"A": a[q][1], "B": b[q][1]}
        rb = st.boot_r(W[:, codes[pos[q]]], yq, preds)
        for m in ("A", "B"):
            r_obs[m, q] = st.pearson_columns(yq, preds[m])
            r_boot[m, q] = rb[m]
        keep[q] = np.isfinite(r_obs["A", q]) & np.isfinite(r_obs["B", q])
    del W
    emo_rows, score_rows = [], []

    def emit(who, ra, rb_, ba, bb, kp):
        d, db = ra - rb_, ba - bb
        lo, hi = st.basic_ci(d, db)
        p = st.centered_p(d, db)
        pb = np.full(n_emo, np.nan)
        pb[kp] = st.bh(p[kp])
        for e in range(n_emo):
            emo_rows.append(dict(pair=pair["name"], participant=who, emotion=emotions[e], r_a=ra[e], r_b=rb_[e], diff=d[e], ci_low=lo[e], ci_high=hi[e], p_raw=p[e], p_bh=pb[e],
                                 family_size=int(kp.sum()), computable=bool(kp[e]), label="탐색(BH-FDR)"))
        sa, sb = float(np.mean(ra[kp])), float(np.mean(rb_[kp]))
        bsa, bsb = st.mean_over(ba, kp), st.mean_over(bb, kp)
        lo, hi = st.basic_ci(sa - sb, bsa - bsb)
        score_rows.append(dict(pair=pair["name"], participant=who, score_a=sa, score_b=sb, diff=sa - sb, ci_low=float(lo), ci_high=float(hi),
                               p_raw=float(st.centered_p(sa - sb, bsa - bsb)), n_emotions=int(kp.sum())))
        return bsa - bsb

    boots = []
    for q in pids:
        boots.append(emit(q, r_obs["A", q], r_obs["B", q], r_boot["A", q], r_boot["B", q], keep[q]))
    kp5 = np.stack([keep[q] for q in pids]).all(0)
    ra5 = np.nanmean(np.stack([r_obs["A", q] for q in pids]), 0)
    rb5 = np.nanmean(np.stack([r_obs["B", q] for q in pids]), 0)
    ba5 = np.nanmean(np.stack([r_boot["A", q] for q in pids]), 0)
    bb5 = np.nanmean(np.stack([r_boot["B", q] for q in pids]), 0)
    emit("mean5", ra5, rb5, ba5, bb5, kp5)
    # 5명 평균 점수는 참가자 점수의 평균이다(정서별 5명 평균 r의 평균이 아님)
    s5 = [r for r in score_rows if r["participant"] != "mean5"]
    m5 = [r for r in score_rows if r["participant"] == "mean5"][0]
    da = float(np.mean([r["score_a"] for r in s5])) - float(np.mean([r["score_b"] for r in s5]))
    db5 = np.mean(np.stack(boots), 0)
    lo, hi = st.basic_ci(da, db5)
    m5.update(score_a=float(np.mean([r["score_a"] for r in s5])), score_b=float(np.mean([r["score_b"] for r in s5])), diff=da, ci_low=float(lo), ci_high=float(hi), p_raw=float(st.centered_p(da, db5)))
    return emo_rows, score_rows, dict(n_units=n_units, rows={q: int(len(videos[q])) for q in pids})


def run(pairs, out, split, y_split, emotions, *, n_boot=st.N_RESAMPLE, overwrite=False, extra_info=None):
    started = time.time()
    out = Path(out)
    if out.exists() and any(out.iterdir()) and not overwrite:
        raise SystemExit(f"{out}가 비어 있지 않다. --overwrite를 주면 덮어쓴다")
    out.mkdir(parents=True, exist_ok=True)
    emo, scores, info = [], [], {}
    for pair in pairs:
        e, s, i = compare(pair, split, y_split, emotions, n_boot)
        emo += e
        scores += s
        info[pair["name"]] = dict(pair, **i)
    pd.DataFrame(emo).to_csv(out / "per_emotion.tsv", sep="\t", index=False)
    pd.DataFrame(scores).to_csv(out / "scores.tsv", sep="\t", index=False)
    run_info = dict(pairs=info, n_boot=n_boot, boot_seed=perf.BOOT_SEED, seed=SEED, elapsed_seconds=round(time.time() - started, 1), **(extra_info or {}))
    (out / "run_info.json").write_text(json.dumps(run_info, indent=1, ensure_ascii=False, default=str))
    return run_info


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 구조 비교와 민감도(다른 S6 폴더의 두 모델)")
    ap.add_argument("--pair", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", required=True)
    ap.add_argument("--n-boot", type=int, default=st.N_RESAMPLE)
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args(argv)
    c.guard(a.design_freeze)
    split = c.load_split()
    y, cols = c.load_scores(split, "emotions")
    emotions = pd.read_csv(c.LABEL_MAP, sep="\t").set_index("score_col").loc[cols, "name"].tolist()
    info = run([parse_pair(x) for x in a.pair], a.out, split, y, emotions, n_boot=a.n_boot, overwrite=a.overwrite, extra_info=dict(design_freeze=a.design_freeze))
    print(f"끝: {a.out} ({info['elapsed_seconds']}초, 쌍 {len(info['pairs'])}개)")


if __name__ == "__main__":
    main()
