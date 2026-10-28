#!/usr/bin/env python3
"""공정 비교용 분할표 두 가지 (2026-10-28).

  ours : horikawa_rungroup6_v1. run 묶음 6겹, 같은 내용은 같은 fold, 같은 내용의 나중 제시 제외. 5명 공통.
  ours10, ours46 : ours 와 같은 run 묶음(46개)을 유지하고 fold 수만 늘림. ours10 = 영상 수를 맞춘 10겹 (학습 약 90%),
         ours46 = run 묶음 하나씩 빼는 46겹 (학습 약 98%). 학습 자료를 늘렸을 때의 효과를 누출 없이 본다.
  lit  : 문헌(GED, ML-BVAE, AESL) 방식. 피험자마다 사용 가능한 모든 제시(중복 포함)를 무작위 10겹 (KFold shuffle, seed 0).
         같은 run 의 인접 영상, 같은 내용의 반복 제시가 학습과 평가에 함께 들어갈 수 있다.
행은 Perlmutter v3_qc 의 사용 가능한 블록 (roi_blocks/Horikawa_sub-XX_roi469_rows.tsv 와 같은 순서).
출력: runs/protocols/<protocol>_sub-XX.tsv (row = roi_blocks 행 번호, video_id, fold)
사용: python make_protocols.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold

REPO = Path("/pscratch/sd/s/sjmoon/EmoBrain")
ROI = REPO / "project/output/prelim_2026-10/roi_blocks"
SPLIT = REPO / "docs/reports/prelim_2026-10/splits/horikawa_rungroup6_v1.tsv"
OUT = Path(__file__).resolve().parent / "runs/protocols"


GROUP10 = {}


def group10(split):
    """run 묶음 46개를 분석 영상 수가 고르게 10겹으로 (큰 묶음부터 가장 작은 fold 에 넣음, 라벨은 보지 않음)."""
    size = split[split.analysis_row].groupby("run_group").size().sort_values(ascending=False)
    load = [0] * 10; out = {}
    for g, n in size.items():
        k = int(np.argmin(load)); out[g] = k; load[k] += n
    return out, load


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    split = pd.read_csv(SPLIT, sep="\t").set_index("video_id")
    m, load = group10(split.reset_index()); GROUP10.update(m)
    print(f"ours10 fold 별 분석 영상 수: {sorted(load)} | ours46 run 묶음 {split.run_group.nunique()}개")
    for sub in ["01", "02", "03", "04", "05"]:
        rows = pd.read_csv(ROI / f"Horikawa_sub-{sub}_roi469_rows.tsv", sep="\t").reset_index().rename(columns={"index": "row"})
        o = rows[~rows.exclude_duplicate.astype(bool)].copy(); o["fold"] = split.loc[o.video_id, "fold"].values
        o[["row", "video_id", "fold"]].to_csv(OUT / f"ours_sub-{sub}.tsv", sep="\t", index=False)
        rg = split.loc[o.video_id, "run_group"].values
        o.assign(fold=pd.factorize(rg, sort=True)[0])[["row", "video_id", "fold"]].to_csv(OUT / f"ours46_sub-{sub}.tsv", sep="\t", index=False)
        o.assign(fold=pd.Series(rg).map(GROUP10).values)[["row", "video_id", "fold"]].to_csv(OUT / f"ours10_sub-{sub}.tsv", sep="\t", index=False)
        lit = rows.copy(); lit["fold"] = -1
        for k, (_, te) in enumerate(KFold(n_splits=10, shuffle=True, random_state=0).split(lit)):
            lit.iloc[te, lit.columns.get_loc("fold")] = k
        lit[["row", "video_id", "fold"]].to_csv(OUT / f"lit_sub-{sub}.tsv", sep="\t", index=False)
        same = lit.groupby("content_id").fold.nunique()
        print(f"sub-{sub}: ours {len(o)}행 6겹 | lit {len(lit)}행 10겹, 같은 내용 반복 제시 {int(lit.content_id.duplicated(keep=False).sum())}행 "
              f"(학습·평가에 나뉜 같은 내용 {int((same > 1).sum())}개)")


if __name__ == "__main__":
    main()
