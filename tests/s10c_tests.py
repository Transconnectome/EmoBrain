#!/usr/bin/env python3
"""src/s10_sensitivity.py 합성 시험 (2026-11-16). 실제 자료와 GPU를 쓰지 않는다.
시험: 같은 예측끼리는 차이 0, p 1. 다른 폴더의 두 조건 차이가 손 계산 r의 차이와 같다. plan 시험 행이 다르면 멈춘다. 5명 평균 점수는 참가자 점수의 평균이다.
사용(src에서): python ../tests/s10c_tests.py
"""
import sys as _sys
_sys.dont_write_bytecode = True
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.getcwd())
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import pandas as pd

import s10_stats as st
import s10_sensitivity as sens
import s10_tests as T

RESULTS = []


def check(name, ok):
    RESULTS.append((name, bool(ok)))
    print(("통과 " if ok else "실패 ") + name, flush=True)


def main():
    split = T.fake_split()
    y = T.fake_y(split)
    emotions = [f"emo{i}" for i in range(T.N_EMO)]
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        d1, d2 = tmp / "s6_one", tmp / "s6_two"
        truth = T.build_s6(d1, split, y)
        T.build_s6(d2, split, y)
        pairs = [dict(name="same", dir_a=str(d1), cond_a="brain_only", dir_b=str(d2), cond_b="brain_only"),
                 dict(name="diff", dir_a=str(d1), cond_a="brain_only_featdec", dir_b=str(d2), cond_b="brain_only")]
        sens.run(pairs, tmp / "out", split, y, emotions, n_boot=50)
        pe = pd.read_csv(tmp / "out" / "per_emotion.tsv", sep="\t")
        sc = pd.read_csv(tmp / "out" / "scores.tsv", sep="\t")
        same = pe[pe.pair == "same"]
        check("같은 예측끼리는 정서별 차이 0, 중심 맞춘 p 1", np.allclose(same["diff"].fillna(0), 0) and (same.p_raw.dropna() == 1).all())
        ya, pa = T.pooled(truth, ("brain_only_featdec", 0), "sub-01", y, split)
        yb, pb = T.pooled(truth, ("brain_only", 0), "sub-01", y, split)
        want = st.pearson_columns(ya, pa) - st.pearson_columns(yb, pb)
        got = pe[(pe.pair == "diff") & (pe.participant == "sub-01")]["diff"].to_numpy()
        check("다른 폴더 두 조건의 정서별 차이 = 손 계산 r의 차이", np.allclose(got, want, equal_nan=True))
        s = sc[sc.pair == "diff"].set_index("participant")
        check("5명 평균 점수는 참가자 점수의 평균", np.isclose(s.loc["mean5", "score_a"], s.drop("mean5").score_a.mean()))
        check("정서별 BH는 계산 가능한 정서 수만큼", (pe[pe.pair == "diff"].family_size == T.N_EMO - 1).all())
        bad = tmp / "s6_bad"
        T.build_s6(bad, split, y, drop_row=True)
        try:
            sens.run([dict(name="bad", dir_a=str(d1), cond_a="brain_only", dir_b=str(bad), cond_b="brain_only")], tmp / "out_bad", split, y, emotions, n_boot=10)
            stopped = False
        except (SystemExit, ValueError):
            stopped = True
        check("두 폴더의 시험 행이 다르면 멈춘다", stopped)
    bad_n = [n for n, ok in RESULTS if not ok]
    print("통과", len(RESULTS) - len(bad_n), "실패", len(bad_n), bad_n)
    sys.exit(1 if bad_n else 0)


if __name__ == "__main__":
    main()
