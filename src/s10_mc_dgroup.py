#!/usr/bin/env python3
"""S10 6-3 MC 전이 확장: D-3, D-4를 A-1, C-1과 비교(01 6-3의 "MC 전이를 A-1, B-1, C-1, D-1, D-3, D-4로 넓힘", 11/17 결과 전 읽는 규칙). GPU 없음.

입력: <S8 폴더>/<조건>/seed0/mc-0X/{done.json, 예측 파일, scoring.npz}. 조건은 A-1(brain_only), C-1(brain_decoded), D-3(brain_features_only), D-4(brain_frozen_feature_encoder).
  D 묶음의 HK 전체 모델은 seed 0만 있으므로(01) 네 조건 모두 seed 0만 비교한다. 예측 파일은 done.json의 pred_file(D 묶음) 또는 test_pred_wd<고른 값>.npz(A-1, C-1).
- 확인: 시험 영상 72개, 서로 다름, 한 참가자의 네 조건이 같은 영상과 같은 사람 평정을 쓴다.
계산(s10_mc.py와 같은 원리)
- 참가자별, 정서별로 72개 영상에 걸친 Pearson r, 34개 평균(사전 판). 27개판(Cowen & Keltner 7개를 뺀 것, 01 0절)도 함께 낸다.
  72개에서 사람 평정이 모두 같은 정서는 모든 조건에서 뺀다. 예측이 일정한 정서가 있으면 그 참가자의 모든 조건에서 뺀다(s10_mc의 unit 범위와 같음).
- 차이(D-3 − A-1, D-4 − A-1, D-3 − C-1, D-4 − C-1): 5명 평균의 basic 95% 구간과 중심 맞춘 양측 p(72개 영상 단위 bootstrap 10,000회, s10_mc와 같은 perf.BOOT_SEED와 st.bootstrap_counts, st.boot_r), 같은 방향인 참가자 수.
- 01의 읽는 규칙: D-3, D-4가 "A-1과 같거나 높으면" "정서 평정을 읽는 능력이 장면 feature 경로만으로 새 사람에게 옮겨 간다"고 쓴다.
  코드의 판정: 구간 상한 < 0이고 5명 가운데 4명 이상이 음수면 "A-1보다 낮다", 구간 하한 > 0이고 4명 이상 양수면 "A-1보다 높다", 그 밖은 "A-1과 구별되지 않는다".
  6-3과 같은 판정 기준(5명 평균 구간과 5명 가운데 4명 이상 같은 방향)이다. 11/25까지는 MC 6명에 5명 이상이었고, S1을 빼면서 바꿨다. 보정은 하지 않는다(O4 (5)).
출력(--out): scores.tsv(조건 × 참가자 × 판), differences.tsv, per_emotion.tsv, run_info.json
- 11/18 --with-b1: B-1(brain_only_featdec, 06 5절 "C-1의 이득이 특징을 거쳐 읽어서인지, 학습 때 특징을 더 배워서인지")을 더한다.
  더하는 차이: C-1 − B-1, B-1 − A-1. 기존 네 차이와 판정 규칙은 그대로다. 출력 폴더를 따로 준다.
사용: s10_mc_dgroup.py --mc-dir <S8 폴더> --out <출력 폴더> [--n-boot 10000] [--with-b1]
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

CONDS = {"brain_only": "A-1", "brain_decoded": "C-1", "brain_features_only": "D-3", "brain_frozen_feature_encoder": "D-4"}
PIDS = tuple(f"mc-0{i}" for i in range(2, 7))  # 11/25 석진 님: S1은 MC에서 뺀다(이유는 01 6-3)
MIN_SAME = 4  # 5명 가운데 4명 이상 같은 방향(6명일 때는 5명 이상이었다)
CK7 = ("pride", "triumph", "contempt", "disappointment", "sympathy", "guilt", "envy")
PAIRS = (("D-3", "A-1"), ("D-4", "A-1"), ("D-3", "C-1"), ("D-4", "C-1"))


def load(mc_dir):
    units = {}
    for cond, short in CONDS.items():
        for q in PIDS:
            d = Path(mc_dir) / cond / "seed0" / q
            if not (d / "done.json").exists():
                raise SystemExit(f"{d}: 끝나지 않았다")
            done = json.loads((d / "done.json").read_text())
            if done.get("settings", {}).get("hk_plan") != "final_for_mc" or done.get("condition") != cond or done.get("participant") != q:
                raise SystemExit(f"{d}: done.json이 폴더와 다르거나 final_for_mc가 아니다")
            pf = done.get("pred_file") or f"test_pred_wd{float(done['chosen_input_wd']):g}.npz"
            pred, sc = np.load(d / pf), np.load(d / "scoring.npz")
            vid = pred["video_id"].astype(np.int64)
            if not np.array_equal(vid, sc["video_id"].astype(np.int64)) or len(set(vid.tolist())) != 72:
                raise SystemExit(f"{d}: 시험 영상이 72개가 아니거나 예측과 채점의 영상이 다르다")
            o = np.argsort(vid)
            p = np.asarray(pred["p"], np.float64)[o]
            if p.shape != (72, 34) or not np.isfinite(p).all():
                raise SystemExit(f"{d}: 예측 크기가 다르거나 NaN이 있다")
            units[short, q] = dict(video_id=vid[o], p=p, y=np.asarray(sc["y"], np.float64)[o])
    for q in PIDS:
        ref = units["A-1", q]
        for short in CONDS.values():
            u = units[short, q]
            if not np.array_equal(u["video_id"], ref["video_id"]) or not np.array_equal(u["y"], ref["y"]):
                raise SystemExit(f"{q} {short}: A-1과 시험 영상이나 사람 평정이 다르다")
    return units


def col_r(y, p):
    """y, p: 영상 × 정서. 돌려주는 값: 정서별 Pearson r."""
    yc, pc = y - y.mean(0), p - p.mean(0)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (yc * pc).sum(0) / np.sqrt((yc ** 2).sum(0) * (pc ** 2).sum(0))


def run(mc_dir, out, n_boot=st.N_RESAMPLE):
    t0 = time.time()
    units = load(mc_dir)
    names = pd.read_csv(c.LABEL_MAP, sep="\t").name.tolist()
    k27 = np.array([n not in CK7 for n in names])
    y0 = units["A-1", PIDS[0]]["y"]
    const_y = y0.std(0) == 0
    keep = {}
    for q in PIDS:
        ok = ~const_y
        for short in CONDS.values():
            ok &= units[short, q]["p"].std(0) > 0
        keep[q] = ok
    W = st.bootstrap_counts(72, n_boot, np.random.default_rng(perf.BOOT_SEED)).astype(np.float64)  # s10_mc와 같은 재표집
    score, boot, per = {}, {}, []
    for q in PIDS:
        for short in CONDS.values():
            u = units[short, q]
            r = col_r(u["y"], u["p"])
            br = st.boot_r(W, u["y"], {"p": u["p"]})["p"]  # (B, 정서)
            for e, n in enumerate(names):
                per.append(dict(participant=q, model=short, emotion=n, r=r[e], kept=bool(keep[q][e]), in_27=bool(k27[e])))
            for tag, m in (("34", keep[q]), ("27", keep[q] & k27)):
                score[short, q, tag] = float(np.nanmean(r[m]))
                boot[short, q, tag] = np.nanmean(br[:, m], axis=1)
    rows = [dict(model=s, participant=q, set=tag, r=score[s, q, tag]) for (s, q, tag) in score]
    diffs = []
    for a, b in PAIRS:
        for tag in ("34", "27"):
            d_q = np.array([score[a, q, tag] - score[b, q, tag] for q in PIDS])
            d = float(d_q.mean())
            bd = np.mean([boot[a, q, tag] - boot[b, q, tag] for q in PIDS], axis=0)
            lo, hi = st.basic_ci(d, bd)
            p = st.centered_p(d, bd)
            neg, pos = int((d_q < 0).sum()), int((d_q > 0).sum())
            verdict = (f"{b}보다 낮다" if hi < 0 and neg >= MIN_SAME else f"{b}보다 높다" if lo > 0 and pos >= MIN_SAME else f"{b}과 구별되지 않는다")
            diffs.append(dict(comparison=f"{a} - {b}", set=tag, mean_diff=d, ci_low=lo, ci_high=hi, p=p, n_negative=neg, n_positive=pos, verdict=verdict,
                              **{f"diff_{q}": float(v) for q, v in zip(PIDS, d_q)}))
    o = Path(out)
    o.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(o / "scores.tsv", sep="\t", index=False)
    pd.DataFrame(diffs).to_csv(o / "differences.tsv", sep="\t", index=False)
    pd.DataFrame(per).to_csv(o / "per_emotion.tsv", sep="\t", index=False)
    info = dict(stage="S10 6-3 MC 전이 D 묶음 비교", mc_dir=str(mc_dir), n_boot=n_boot, boot_seed=perf.BOOT_SEED, n_constant_rating=int(const_y.sum()),
                n_dropped_constant_prediction={q: int((~keep[q] & ~const_y).sum()) for q in PIDS}, code_commit=c.START_HEAD, code_dirty=c.START_DIRTY,
                seconds=round(time.time() - t0, 1))
    (o / "run_info.json").write_text(json.dumps(info, indent=1, ensure_ascii=False))
    return info


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 MC 전이 D-3, D-4 대 A-1, C-1")
    ap.add_argument("--mc-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n-boot", type=int, default=st.N_RESAMPLE)
    ap.add_argument("--with-b1", action="store_true", help="11/18. B-1을 더하고 C-1 − B-1, B-1 − A-1을 낸다")
    a = ap.parse_args(argv)
    if a.with_b1:
        global CONDS, PAIRS
        CONDS = {**CONDS, "brain_only_featdec": "B-1"}
        PAIRS = PAIRS + (("C-1", "B-1"), ("B-1", "A-1"))
    print(json.dumps(run(a.mc_dir, a.out, a.n_boot), ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
