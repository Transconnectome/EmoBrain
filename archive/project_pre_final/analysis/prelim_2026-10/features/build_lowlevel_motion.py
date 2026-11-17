#!/usr/bin/env python3
"""색·밝기·선명도·움직임 저수준 특징 (2026-10-31, CPU).

기존 저수준 특징 (EmoViS Sadeghi 142차원) 은 정지 화면이라 움직임이 없다. 여기서는 영상 전체를 초당 8장, 긴 변 96 px 로 풀어서
프레임마다 값을 잰 뒤 시간 평균·표준편차 등으로 요약한다.
  색 (14)    : 평균 R·G·B, 채도 평균·SD, 색조 원형 평균 (sin, cos, 채도 가중), 색조 12구간 비율 중 대표 3개 대신 colorfulness (Hasler & Süsstrunk),
               따뜻한 색 (적·주황·황) 비율, 차가운 색 (청·녹) 비율, 어두운 화소 비율, 밝은 화소 비율
  밝기 (6)   : 휘도 평균·공간 SD (대비)·시간 SD, 선명도 (라플라시안 분산) 평균·SD, 가장자리 밀도
  움직임 (12): 연속 프레임 절대 차이 평균·SD·최댓값·90 백분위, 장면 전환 비율 (큰 차이), 움직임 증가 최대치 (갑작스러운 시작),
               3×3 격자 중 가운데 대비 가장자리 움직임 비, 위·아래·좌·우 절반 움직임 차이 2개, 움직임 시간 집중도 (최댓값/평균)
출력: <특징 폴더>/lowlevel_motion.npy + lowlevel_motion_video_id.tsv + lowlevel_motion_columns.txt
사용: python build_lowlevel_motion.py [--ids ...]
"""
import argparse
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

FFMPEG = "/pscratch/sd/s/sjmoon/swift_PTL2/bin/ffmpeg"
FFPROBE = "/pscratch/sd/s/sjmoon/swift_PTL2/bin/ffprobe"
COLS = ["mean_r", "mean_g", "mean_b", "sat_mean", "sat_sd", "hue_sin", "hue_cos", "colorfulness", "warm_frac", "cool_frac",
        "dark_frac", "bright_frac", "lum_mean", "lum_contrast", "lum_time_sd", "sharp_mean", "sharp_sd", "edge_density",
        "motion_mean", "motion_sd", "motion_max", "motion_p90", "cut_frac", "motion_onset", "motion_center_ratio",
        "motion_topbottom", "motion_leftright", "motion_peakiness"]


def frames(path):
    w, h = map(int, subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                    "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True).stdout.strip().split(",")[:2])
    s = 96 / max(w, h); W, H = max(8, int(w * s) // 2 * 2), max(8, int(h * s) // 2 * 2)
    raw = subprocess.run([FFMPEG, "-v", "error", "-i", str(path), "-vf", f"fps=8,scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3).astype(np.float32) / 255.0


def hsv(fr):
    mx, mn = fr.max(-1), fr.min(-1); d = mx - mn + 1e-6
    r, g, b = fr[..., 0], fr[..., 1], fr[..., 2]
    hue = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    return hue, np.where(mx > 0, (mx - mn) / (mx + 1e-6), 0), mx


def features(fr):
    hue, sat, val = hsv(fr)
    lum = 0.299 * fr[..., 0] + 0.587 * fr[..., 1] + 0.114 * fr[..., 2]
    rg, yb = fr[..., 0] - fr[..., 1], 0.5 * (fr[..., 0] + fr[..., 1]) - fr[..., 2]
    colorful = np.sqrt(rg.std() ** 2 + yb.std() ** 2) + 0.3 * np.sqrt(rg.mean() ** 2 + yb.mean() ** 2)
    colored = sat > 0.2
    warm = colored & ((hue < 60) | (hue >= 330)); cool = colored & (hue >= 90) & (hue < 270)
    lap = np.abs(lum[:, :-2, 1:-1] + lum[:, 2:, 1:-1] + lum[:, 1:-1, :-2] + lum[:, 1:-1, 2:] - 4 * lum[:, 1:-1, 1:-1])
    sharp = lap.reshape(len(lum), -1).var(1)
    gx, gy = np.diff(lum, axis=2)[:, :-1, :], np.diff(lum, axis=1)[:, :, :-1]
    edge = (np.sqrt(gx ** 2 + gy ** 2) > 0.1).mean()
    hw = (sat * np.exp(1j * np.deg2rad(hue))).mean()
    out = [*fr.reshape(-1, 3).mean(0), sat.mean(), sat.std(), hw.imag, hw.real, colorful, warm.mean(), cool.mean(),
           (lum < 0.15).mean(), (lum > 0.85).mean(), lum.mean(), lum.reshape(len(lum), -1).std(1).mean(), lum.reshape(len(lum), -1).mean(1).std(),
           sharp.mean(), sharp.std(), edge]
    if len(lum) >= 2:
        D = np.abs(np.diff(lum, axis=0)); m = D.reshape(len(D), -1).mean(1)
        H, W = lum.shape[1:]; ch, cw = slice(H // 3, 2 * H // 3), slice(W // 3, 2 * W // 3)
        center = D[:, ch, cw].mean(); periph = (D.sum((1, 2)) - D[:, ch, cw].sum((1, 2))).sum() / (D[0].size - D[0, ch, cw].size) / len(D)
        out += [m.mean(), m.std(), m.max(), np.percentile(m, 90), (m > 0.15).mean(), np.diff(m).max() if len(m) > 1 else 0.0,
                center / (periph + 1e-6), D[:, : H // 2].mean() - D[:, H // 2:].mean(), D[:, :, : W // 2].mean() - D[:, :, W // 2:].mean(),
                m.max() / (m.mean() + 1e-6)]
    else:
        out += [0.0] * 10
    return np.array(out, np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos", type=Path, default=Path("/pscratch/sd/s/sjmoon/EmoViS/data/raw/CowenEmotionVideos"))
    ap.add_argument("--out", type=Path, default=Path("/pscratch/sd/s/sjmoon/transfer/emobrain_lab_features_20261026"))
    ap.add_argument("--ids"); a = ap.parse_args()
    ids = [int(x) for x in a.ids.split(",")] if a.ids else list(range(1, 2197))
    X = []
    for k, v in enumerate(ids):
        X.append(features(frames(a.videos / f"{v:04d}.mp4")))
        if k % 200 == 0:
            print(f"[{k + 1}/{len(ids)}] video {v}", flush=True)
    X = np.stack(X); assert X.shape[1] == len(COLS) and np.isfinite(X).all()
    if a.ids:
        print(pd.DataFrame(X, index=ids, columns=COLS).round(3).T.to_string()); return
    np.save(a.out / "lowlevel_motion.npy", X)
    pd.DataFrame(dict(video_id=ids)).to_csv(a.out / "lowlevel_motion_video_id.tsv", sep="\t", index=False)
    (a.out / "lowlevel_motion_columns.txt").write_text("\n".join(COLS))
    print("저장", X.shape)


if __name__ == "__main__":
    main()
