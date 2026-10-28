#!/usr/bin/env python3
"""공정 비교용 분할표 두 가지 (2026-10-28).

  ours : horikawa_rungroup6_v1. run 묶음 6겹, 같은 내용은 같은 fold, 같은 내용의 나중 제시 제외. 5명 공통.
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


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    split = pd.read_csv(SPLIT, sep="\t").set_index("video_id")
    for sub in ["01", "02", "03", "04", "05"]:
        rows = pd.read_csv(ROI / f"Horikawa_sub-{sub}_roi469_rows.tsv", sep="\t").reset_index().rename(columns={"index": "row"})
        o = rows[~rows.exclude_duplicate.astype(bool)].copy(); o["fold"] = split.loc[o.video_id, "fold"].values
        o[["row", "video_id", "fold"]].to_csv(OUT / f"ours_sub-{sub}.tsv", sep="\t", index=False)
        lit = rows.copy(); lit["fold"] = -1
        for k, (_, te) in enumerate(KFold(n_splits=10, shuffle=True, random_state=0).split(lit)):
            lit.iloc[te, lit.columns.get_loc("fold")] = k
        lit[["row", "video_id", "fold"]].to_csv(OUT / f"lit_sub-{sub}.tsv", sep="\t", index=False)
        same = lit.groupby("content_id").fold.nunique()
        print(f"sub-{sub}: ours {len(o)}행 6겹 | lit {len(lit)}행 10겹, 같은 내용 반복 제시 {int(lit.content_id.duplicated(keep=False).sum())}행 "
              f"(학습·평가에 나뉜 같은 내용 {int((same > 1).sum())}개)")


if __name__ == "__main__":
    main()
