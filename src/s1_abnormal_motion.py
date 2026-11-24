#!/usr/bin/env python3
"""S1: 튀는 블록 5개와 sub-03 run 31~33의 머리 움직임(FD)과 신호 급변(DVARS) 비교 (B6 재결정 전 확인, 2026-11-03).

블록: v3_qc samples 표의 fd_max_window(반응 구간 앞뒤의 FD 최대)와 std_dvars_max_window(같은 구간의 표준화 DVARS 최대)를
     그 참가자의 개발 블록(MC 72개와 같은 내용, 나중 중복 제외) 분포 안의 백분위로 비교한다.
run: v3_qc runs_qc 표의 fd_mean, fd_max, censor_frac, std_dvars_mean, frac_std_dvars_gt_1_5를 sub-03 run 61개 안의 백분위로 비교한다.
참고 기준(PREPROCESSING_FINAL.md 1.2절, 이미 적용됨): 반응 구간 ±2 volume에 FD > 0.9 mm가 있는 블록 제외, run은 평균 FD > 0.5 mm 등.
출력: manifests/abnormal_motion_check.tsv와 표준 출력
사용: python s1_abnormal_motion.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import s1_abnormal_blocks as ab  # noqa: E402

BLOCKS = [("02", 892), ("02", 289), ("02", 312), ("03", 1158), ("04", 879)]
RUNS = [("03", 31), ("03", 32), ("03", 33)]
RUN_COLS = ["fd_mean", "fd_max", "censor_frac", "std_dvars_mean", "frac_std_dvars_gt_1_5"]


def pct(x, v):
    return round(100 * float((np.asarray(x) < v).mean()), 1)


def main():
    drop = ab.mc72_videos(); rows = []
    for sub, vid in BLOCKS:
        T = pd.read_csv(ab.PM / f"Horikawa/sub-{sub}/v3_qc/sub-{sub}_samples_qc_usable.tsv", sep="\t")
        D = T[~T.video_id.isin(drop) & ~T.exclude_duplicate.astype(bool)]
        b = D[D.video_id == vid].iloc[0]
        rows.append(dict(kind="block", participant=f"sub-{sub}", item=f"video {vid}", where=f"{b.session} {b.run}",
                         fd=b.fd_max_window, fd_pct=pct(D.fd_max_window, b.fd_max_window),
                         dvars=b.std_dvars_max_window, dvars_pct=pct(D.std_dvars_max_window, b.std_dvars_max_window),
                         fd_median_all=D.fd_max_window.median(), dvars_median_all=D.std_dvars_max_window.median()))
    for sub, ri in RUNS:
        R = pd.read_csv(ab.PM / f"Horikawa/sub-{sub}/v3_qc/sub-{sub}_runs_qc.tsv", sep="\t")
        r = R[R.run_index == ri].iloc[0]
        rows.append(dict(kind="run", participant=f"sub-{sub}", item=f"run_index {ri}", where=r.run,
                         fd=r.fd_mean, fd_pct=pct(R.fd_mean, r.fd_mean), dvars=r.std_dvars_mean, dvars_pct=pct(R.std_dvars_mean, r.std_dvars_mean),
                         fd_median_all=R.fd_mean.median(), dvars_median_all=R.std_dvars_mean.median(),
                         fd_max=r.fd_max, censor_frac=r.censor_frac, frac_dvars_gt_1_5=r.frac_std_dvars_gt_1_5))
    O = pd.DataFrame(rows); O.to_csv(ab.OUT / "abnormal_motion_check.tsv", sep="\t", index=False, float_format="%.4g")
    print(O.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
