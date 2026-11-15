#!/usr/bin/env python3
"""[사전] 15개의 Holm 보정 (04 S10 다중비교, 01 6-1, 2026-11-15). GPU 없음, 몇 초.

입력: S10 단계들이 쓴 보정 전 p 파일(열 test_id, family, seed, p_raw, estimate). 지금은 s10_performance의 prereg_pvalues.tsv(2-3 여섯)만 있다.
- 15개의 이름은 s10_stats.PREREG_15, 묶음은 5명 평균(mean5)과 참가자마다(sub-01~sub-05)다(6-1). 묶음마다 따로 보정한다.
- 묶음마다 15개가 모두 있어야 보정한다. 하나라도 없으면 어느 묶음에서 무엇이 없는지 쓰고 보정 값을 내지 않는다(종료 코드 1).
- 15개 밖의 이름, 같은 검정과 묶음과 seed가 둘 이상인 행은 멈춘다.
- seed: ridge처럼 seed가 없는 검정은 seed 칸을 비운다. 한 검정과 묶음에 seed가 여럿이면 --seed로 하나를 고르게 한다. seed별 p를 어떻게 묶을지는 문서가 정하지 않았다.
- 검정마다 보정 전과 후에 확인된 참가자 수를 센다(6-1). 유의수준은 Holm 보정 뒤 0.05다(11/15 석진 님).
사용: s10_holm15.py --inputs <p 파일> [<p 파일> ...] --out <출력 파일> [--seed 0] [--alpha 0.05]
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import s10_stats as st


def read_inputs(paths):
    frames = []
    for p in paths:
        t = pd.read_csv(p, sep="\t", dtype={"seed": "string"})
        lack = {"test_id", "family", "seed", "p_raw"} - set(t.columns)
        if lack:
            raise SystemExit(f"{p}: 열 {sorted(lack)}가 없다")
        t["input"] = str(p)
        frames.append(t)
    t = pd.concat(frames, ignore_index=True)
    t["seed"] = t["seed"].fillna("")
    unknown = sorted(set(t.test_id) - set(st.PREREG_15))
    if unknown:
        raise SystemExit(f"[사전] 15개 밖의 이름이 있다: {unknown}")
    bad_family = sorted(set(t.family) - set(st.FAMILIES))
    if bad_family:
        raise SystemExit(f"알 수 없는 묶음: {bad_family}")
    dup = t[t.duplicated(["test_id", "family", "seed"], keep=False)]
    if not dup.empty:
        raise SystemExit(f"같은 검정, 묶음, seed의 p가 둘 이상이다:\n{dup[['test_id', 'family', 'seed', 'input']].to_string(index=False)}")
    if not np.isfinite(t.p_raw.astype(float)).all() or ((t.p_raw <= 0) | (t.p_raw > 1)).any():
        raise SystemExit("p가 (0, 1] 밖이거나 비었다")
    return t


def pick_seed(t, seed):
    """검정과 묶음마다 p 하나. seed가 없는 검정(빈 칸)은 어느 seed와도 쓴다."""
    if seed is not None:
        t = t[(t.seed == "") | (t.seed == str(seed))]
    many = t.groupby(["test_id", "family"]).size()
    many = many[many > 1]
    if len(many):
        raise SystemExit(f"한 검정과 묶음에 seed가 여럿이다({len(many)}개). seed별 p를 어떻게 묶을지는 문서가 정하지 않았다. --seed로 하나를 고른다")
    return t


def missing_table(t):
    rows = []
    for fam in st.FAMILIES:
        have = set(t.test_id[t.family == fam])
        for test in st.PREREG_15:
            if test not in have:
                rows.append(dict(family=fam, test_id=test))
    return pd.DataFrame(rows, columns=["family", "test_id"])


def correct(t, alpha=None):
    """묶음마다 15개에 Holm. 15개가 다 있는 묶음만 받는다."""
    out = []
    for fam in st.FAMILIES:
        g = t[t.family == fam].set_index("test_id").loc[list(st.PREREG_15)].reset_index()
        g["p_holm"] = st.holm(g.p_raw.astype(float).to_numpy())
        g["family_size"] = len(g)
        out.append(g)
    res = pd.concat(out, ignore_index=True)
    if alpha is None:
        return res, None
    part = res[res.family != "mean5"]  # 6-1. 효과가 확인된 사람 수를 보정 전과 후로 센다
    est = part.estimate.astype(float) if "estimate" in part.columns else pd.Series(np.nan, index=part.index)
    flags = pd.DataFrame(dict(test_id=part.test_id, raw=part.p_raw.astype(float) < alpha, adj=part.p_holm < alpha))
    flags["adj_positive"] = flags.adj & (est > 0)
    flags["adj_negative"] = flags.adj & (est < 0)
    count = flags.groupby("test_id", sort=False).agg(n_confirmed_before_holm=("raw", "sum"), n_confirmed_after_holm=("adj", "sum"),
                                                    n_after_holm_estimate_positive=("adj_positive", "sum"), n_after_holm_estimate_negative=("adj_negative", "sum"))
    count = count.reindex(list(st.PREREG_15)).reset_index()
    count["alpha"] = alpha
    return res, count


def main(argv=None):
    ap = argparse.ArgumentParser(description="[사전] 15개 Holm 보정")
    ap.add_argument("--inputs", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--alpha", type=float, default=0.05, help="확인된 참가자 수를 셀 유의수준. 0.05(11/15 석진 님)")
    a = ap.parse_args(argv)
    t = pick_seed(read_inputs(a.inputs), a.seed)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    miss = missing_table(t)
    if not miss.empty:
        path = out.with_name(out.stem + "_missing.tsv")
        miss.to_csv(path, sep="\t", index=False)
        by_test = miss.groupby("test_id", sort=False).family.apply(lambda s: ",".join(s)).reindex([x for x in st.PREREG_15 if x in set(miss.test_id)])
        print(f"[사전] 15개 가운데 없는 것이 있어 보정하지 않는다({len(miss)}칸). 목록: {path}", file=sys.stderr)
        for test, fams in by_test.items():
            print(f"  없음: {test} ({fams})", file=sys.stderr)
        return 1
    res, count = correct(t, a.alpha)
    res.to_csv(out, sep="\t", index=False)
    if count is not None:
        count.to_csv(out.with_name(out.stem + "_counts.tsv"), sep="\t", index=False)
    print(f"끝: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
