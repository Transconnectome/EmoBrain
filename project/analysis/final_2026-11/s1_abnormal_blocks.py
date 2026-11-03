#!/usr/bin/env python3
"""S1: HK 이상 block과 이상 run 목록(B6, 04_claude_code_workorder.md S1, 2026-11-03).

0단계 코드(project/analysis/prelim_2026-10/prelim/confound_and_block_check.py, 연구실 서버에서 실행)와 같은 정의를
Perlmutter의 v3_qc 사본에 다시 적용한다. 0단계 결과 표는 연구실 서버에만 있어 목록을 여기서 다시 만든다.
- 블록 신호 크기 = QC 후 정규화 전 블록 반응(blocks_common36_qc.npy)의 voxel 간 표준편차
- 이상 block: 피험자 안에서 블록 신호 크기의 강건 z(중앙값, MAD × 1.4826)의 절댓값 > 5, 또는 run 안 z 반응(blocks_common36_qc_runz.npy)의 최대 절댓값 > 15
- 이상 run: run마다 블록 신호 크기의 중앙값을 내고, 그 run 중앙값들의 강건 z 절댓값 > 4
0단계 보고서의 수(이상 block sub-02 3, sub-03 1, sub-04 1, 이상 run sub-03 1)와 맞는지 확인한다. 정의는 바꾸지 않는다.
출력: manifests/abnormal_blocks_hk.tsv(이상 block과 이상 run에 속한 행), 표준 출력 요약
사용: python s1_abnormal_blocks.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

PM = Path("/pscratch/sd/s/sjmoon")
OUT = Path(__file__).resolve().parent / "manifests"
HK = ["01", "02", "03", "04", "05"]
STAGE0 = {"01": (0, 0), "02": (3, 0), "03": (1, 1), "04": (1, 0), "05": (0, 0)}


def mad(x):
    x = np.asarray(x, float); return 1.4826 * np.median(np.abs(x - np.median(x)))


def one(sub):
    d = PM / f"Horikawa/sub-{sub}/v3_qc"
    T = pd.read_csv(d / f"sub-{sub}_samples_qc_usable.tsv", sep="\t")
    raw = np.load(d / f"sub-{sub}_blocks_common36_qc.npy", mmap_mode="r")
    rz = np.load(d / f"sub-{sub}_blocks_common36_qc_runz.npy", mmap_mode="r")
    assert raw.shape == rz.shape and raw.shape[0] == len(T)
    sd, mx = np.zeros(len(T)), np.zeros(len(T))
    for i in range(0, len(T), 64):
        sl = slice(i, min(i + 64, len(T)))
        sd[sl] = np.asarray(raw[sl], np.float64).std(1); mx[sl] = np.abs(np.asarray(rz[sl], np.float64)).max(1)
    B = T[["qc_row", "row", "video_id", "content_id", "session", "run", "run_index"]].copy()
    B["block_sd"] = sd; B["runz_absmax"] = mx
    m = mad(sd); B["block_sd_robust_z"] = (sd - np.median(sd)) / (m if m > 0 else 1)
    B["abnormal_block"] = (B.block_sd_robust_z.abs() > 5) | (B.runz_absmax > 15)
    R = B.groupby("run_index").block_sd.median()
    rm = mad(R.values); rz_run = (R - R.median()) / (rm if rm > 0 else 1)
    bad_runs = set(rz_run.index[rz_run.abs() > 4])
    B["abnormal_run"] = B.run_index.isin(bad_runs)
    B.insert(0, "participant", f"sub-{sub}")
    return B, bad_runs, rz_run


def main():
    rows = []
    for s in HK:
        B, bad_runs, rz_run = one(s)
        nb, nr = int(B.abnormal_block.sum()), len(bad_runs)
        same = (nb, nr) == STAGE0[s]
        print(f"sub-{s}: 이상 block {nb}, 이상 run {nr} {sorted(bad_runs)} (0단계 보고 {STAGE0[s]}, {'같음' if same else '다름'})", flush=True)
        rows.append(B[B.abnormal_block | B.abnormal_run])
    A = pd.concat(rows, ignore_index=True)
    A.to_csv(OUT / "abnormal_blocks_hk.tsv", sep="\t", index=False, float_format="%.4g")
    print(A[A.abnormal_block][["participant", "video_id", "content_id", "session", "run", "run_index", "block_sd_robust_z", "runz_absmax"]].to_string(index=False))
    print("이상 run에 속한 블록 수:", A[A.abnormal_run].groupby("participant").size().to_dict())


if __name__ == "__main__":
    main()
