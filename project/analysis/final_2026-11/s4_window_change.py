#!/usr/bin/env python3
"""S4 긴 영상의 창 사이 변화량 (04 S4, 01 3-2, 2026-11-06). 뇌와 정서를 쓰지 않는다. 결과로 평균 규칙을 바꾸지 않는다.

지표. 목표에 쓰는 V-JEPA 2 block 10, 20, 30, 40마다, 개발 영상의 평균과 표준편차로 표준화한 좌표에서 코사인 거리(1 − 코사인)를 쓴다.
- within: 한 영상 안 창 쌍 사이 거리의 평균
- to_mean: 각 창과 그 영상 평균 특징(실제 목표) 사이 거리의 평균
- other_video: 그 영상 평균 특징과 무작위로 고른 다른 개발 영상 500개의 평균 특징 사이 거리의 중앙값(seed 20261106)
- ratio: within / other_video. 창 사이 차이가 영상 사이 차이에 비해 얼마나 큰지 읽는다.

대상은 창으로 나뉜 개발 영상이다. MC 72개는 읽지 않는다. 사용: s4_window_change.py --design-freeze <커밋>
"""
import argparse
import json

import numpy as np
import pandas as pd

import s4_common as c

TARGET_BLOCKS = {10: 9, 20: 19, 30: 29, 40: 39}
SEED = 20261106


def cosine_distance(a, b):
    a, b = a / np.linalg.norm(a, axis=-1, keepdims=True), b / np.linalg.norm(b, axis=-1, keepdims=True)
    return 1 - (a * b).sum(-1)


def video_rows(per_window, mean_z, m, s, others):
    """per_window: 창 × 차원(원래 척도). 표준화 뒤 지표를 돌려준다."""
    z = (per_window - m) / s
    i, j = np.triu_indices(len(z), 1)
    return dict(within=float(cosine_distance(z[i], z[j]).mean()), to_mean=float(cosine_distance(z, mean_z[None]).mean()), other_video=float(np.median(cosine_distance(mean_z[None], others))))


def compute(windows, blocks, ids):
    """windows: video_id -> 창 × 40 × 1408. blocks: split 순서의 영상 × 40 × 1408."""
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
            r = video_rows(np.asarray(per[:, b], np.float64), z[pos], m, s, others)
            rows.append(dict(video_id=int(v), block=block, n_windows=len(per), ratio=r["within"] / r["other_video"], **r))
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--design-freeze", default="")
    a = ap.parse_args()
    c.guard(a.design_freeze)
    split = c.load_split()
    ids = split.video_id.to_numpy()
    out = c.OUT / "window_change"
    prov = c.provenance(a.design_freeze)
    if c.done_or_new(out, prov["code_sha256"]):
        return
    w = np.load(c.FEATURES / "vjepa2/windows_per_video.npz")
    dev = set(ids.tolist())
    windows = {int(k[1:]): w[k] for k in w.files if int(k[1:]) in dev}
    blocks = np.load(c.FEATURES / "vjepa2/blocks.npy", mmap_mode="r")
    table = compute(windows, np.asarray(blocks[ids - 1]), ids)
    summary = table.groupby("block")[["within", "to_mean", "other_video", "ratio"]].median().reset_index()
    with c.Atomic(out) as tmp:
        table.to_csv(tmp / "window_change.tsv", sep="\t", index=False, float_format="%.6g")
        summary.to_csv(tmp / "window_change_summary.tsv", sep="\t", index=False, float_format="%.6g")
        json.dump(dict(prov, n_videos=len(windows)), open(tmp / "done.json", "w"), indent=1)
    print(summary.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
