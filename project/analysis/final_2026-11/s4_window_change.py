#!/usr/bin/env python3
"""S4 긴 영상의 window 사이 변화 (04 S4, 01 3-2, 2026-11-06). 뇌와 정서를 쓰지 않는다. 결과로 평균 규칙을 바꾸지 않는다. 정보 손실량으로 읽지 않는다.

지표. 목표에 쓰는 V-JEPA 2 block 10, 20, 30, 40마다, 개발 영상의 평균과 표준편차로 표준화한 좌표에서 cosine distance(1 − cosine similarity)를 쓴다.
- within: 한 영상 안 window 쌍 사이 거리의 평균
- to_mean: 각 window와 그 영상 평균 특징(실제 목표) 사이 거리의 평균
- other_video: 그 영상 평균 특징과 무작위로 고른 다른 개발 영상 500개의 평균 특징 사이 거리의 중앙값(seed 20261106)
- ratio: within / other_video. window 사이 차이가 영상 사이 차이에 비해 얼마나 큰지 읽는다.

대상은 window로 나뉜 개발 영상이다. MC 72개는 읽지 않는다. 사용: s4_window_change.py --design-freeze <커밋>
"""
import argparse
import json

import numpy as np
import pandas as pd

import s4_common as c

TARGET_BLOCKS = {10: 9, 20: 19, 30: 29, 40: 39}
SEED = 20261106


def cosine_distance(a, b):
    """영벡터가 있으면 NaN(계산 불가)이다. 작은 수로 바꾸지 않고 summarize에서 건수를 적는다."""
    na, nb = np.linalg.norm(a, axis=-1, keepdims=True), np.linalg.norm(b, axis=-1, keepdims=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        return 1 - ((a / na) * (b / nb)).sum(-1)


def video_rows(per_window, mean_z, m, s, others):
    """per_window: window × 차원(원래 척도). 표준화 뒤 지표를 돌려준다."""
    z = (per_window - m) / s
    i, j = np.triu_indices(len(z), 1)
    return dict(within=float(cosine_distance(z[i], z[j]).mean()), to_mean=float(cosine_distance(z, mean_z[None]).mean()), other_video=float(np.median(cosine_distance(mean_z[None], others))))


def compute(windows, blocks, ids):
    """windows: video_id -> window × 40 × 1408. blocks: split 순서의 영상 × 40 × 1408."""
    rng = np.random.default_rng(SEED)
    rows = []
    for block, b in TARGET_BLOCKS.items():
        x = np.asarray(blocks[:, b], np.float64)
        m, s = c.fit_standardizer(x)
        z = (x - m) / s
        for v, per in sorted(windows.items()):
            pos = int(np.where(ids == v)[0][0])
            pool = np.delete(np.arange(len(ids)), pos)
            others = z[rng.choice(pool, size=min(500, len(pool)), replace=False)]
            r = video_rows(c.finite(np.asarray(per[:, b], np.float64), f"영상 {v}의 window"), z[pos], m, s, others)
            with np.errstate(invalid="ignore", divide="ignore"):
                ratio = r["within"] / r["other_video"]
            rows.append(dict(video_id=int(v), block=block, n_windows=len(per), ratio=ratio, **r))
    return pd.DataFrame(rows)


def summarize(table):
    """block마다 중앙값과 함께 유효한 영상 수와 계산 불가 영상 수를 적는다."""
    s = table.groupby("block")[["within", "to_mean", "other_video", "ratio"]].median().reset_index()
    valid = table.assign(valid=np.isfinite(table[["within", "to_mean", "other_video", "ratio"]]).all(axis=1)).groupby("block").valid
    s["n_valid"], s["n_not_computable"] = valid.sum().to_numpy(), (~table.assign(valid=np.isfinite(table[["within", "to_mean", "other_video", "ratio"]]).all(axis=1)).valid).groupby(table.block).sum().to_numpy()
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--design-freeze", default="")
    a = ap.parse_args()
    c.guard(a.design_freeze)
    out = c.OUT / "window_change"
    run = c.Run(a.design_freeze, {"vjepa2_windows": c.FEATURES / "vjepa2/windows_per_video.npz", "vjepa2_blocks": c.FEATURES / "vjepa2/blocks.npy"}, seed=SEED)
    if c.done_or_new(out, run.key):
        return
    split = c.load_split()
    ids = split.video_id.to_numpy()
    w = np.load(c.FEATURES / "vjepa2/windows_per_video.npz")
    dev = set(ids.tolist())
    windows = {int(k[1:]): w[k] for k in w.files if int(k[1:]) in dev}
    blocks = np.load(c.FEATURES / "vjepa2/blocks.npy", mmap_mode="r")
    table = compute(windows, np.asarray(blocks[ids - 1]), ids)
    summary = summarize(table)
    with c.Atomic(out) as tmp:
        table.to_csv(tmp / "window_change.tsv", sep="\t", index=False, float_format="%.6g")
        summary.to_csv(tmp / "window_change_summary.tsv", sep="\t", index=False, float_format="%.6g")
        run.check()
        json.dump(dict(run.prov, n_videos=len(windows)), open(tmp / "done.json", "w"), indent=1)
    print(summary.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
