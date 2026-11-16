#!/usr/bin/env python3
"""S3 저수준 시각 특징 6,558개: 움직임 에너지 6,555개와 RGB 중앙값 3개 (04 S3, 01 3-6, O10, O12, O13, 2026-11-05). GPU가 필요 없다.

사용: s3_lowlevel.py --ids 1-100
움직임 에너지(Du 외, 2023의 설정, pymoten): 초당 15장, 96 × 96, L*, 공간 주파수 {0, 2, 4, 8, 16, 32}, 시간 주파수 {0, 2, 4} Hz, 방향 8개.
O12: 참가자가 본 영상 전체를 한 번에 넣고, 반복까지 포함한 전체 영상의 앞 5프레임과 뒤 5프레임을 뺀 뒤 시간 평균한다. 필터 폭 floor(15 × 2/3) = 10이 기본값과 다르면 멈춘다.
O13: 초당 4장 프레임의 가운데 정사각형에서 R, G, B 채널별 중앙값을 내 시간 평균한다. 값은 정규화 전 0~255다.
"""
import argparse
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, P.need("pymoten_dir"))
import moten  # noqa: E402
from moten.colorspace import rgb2lab  # noqa: E402

import s3_common as c  # noqa: E402
import paths as P

PYMOTEN_VERSION = "0.1.3"
SPATIAL, TEMPORAL, DIRECTIONS = [0, 2, 4, 8, 16, 32], [0, 2, 4], [0, 45, 90, 135, 180, 225, 270, 315]
FPS_MOTION, FPS_RGB, SIZE, TRIM = 15, 4, 96, 5


def pyramid():
    p = moten.pyramids.MotionEnergyPyramid(stimulus_vhsize=(SIZE, SIZE), stimulus_fps=FPS_MOTION, temporal_frequencies=TEMPORAL, spatial_frequencies=SPATIAL, spatial_directions=DIRECTIONS)
    if p.nfilters != 6555:
        raise ValueError(f"필터 수가 6,555개가 아니다: {p.nfilters}")
    if int(p.definition.filter_temporal_width) != 10:
        raise ValueError(f"필터 폭이 10이 아니다: {p.definition.filter_temporal_width}")
    return p


def luminance(frames):
    """(T, H, W, 3) uint8 → (T, 96, 96) L*(0~100). 짧은 변을 96으로 줄이고 가운데를 자른다(3-2, 3-6)."""
    h, w = frames.shape[1:3]
    nh, nw = c.scaled_shape(h, w, SIZE)
    top, left = (nh - SIZE) // 2, (nw - SIZE) // 2
    small = np.stack([np.asarray(Image.fromarray(f).resize((nw, nh), Image.BICUBIC))[top:top + SIZE, left:left + SIZE] for f in frames]).astype(np.float64) / 255.0
    return np.stack([rgb2lab(f)[..., 0] for f in small])


def main(a):
    table = c.stimulus_table()
    p = pyramid()
    spec_id = c.make_spec("lowlevel", ["s3_common.py", "s3_lowlevel.py"], allow_dirty=a.allow_dirty, package="pymoten " + PYMOTEN_VERSION, fps_motion=FPS_MOTION, fps_rgb=FPS_RGB, size=SIZE, spatial_frequencies=SPATIAL, temporal_frequencies=TEMPORAL, directions=DIRECTIONS, trim_each_end=TRIM, filter_width=10, nonlinearity="pymoten 기본 log(x + 1e-5)", screen_motion="짧은 변을 96으로 줄인 뒤 가운데를 자름, PIL bicubic", screen_rgb="줄이지 않은 원래 화소의 가운데 정사각형")
    ids = c.todo_ids("lowlevel", c.parse_ids(a.ids), spec_id)
    print("사양", spec_id, "할 영상", len(ids), flush=True)
    for n, v in enumerate(ids):
        c.check_video(table, v)
        path, duration = table.path[v], float(table.container_duration_s[v])
        pts = c.frame_pts(path)
        frames = c.read_frames(path, c.pick_by_time(pts, duration, FPS_MOTION))
        out = p.project_stimulus(luminance(frames), dtype="float32")  # 기본 출력 비선형 log(x + 1e-5)
        if len(out) <= 2 * TRIM:
            raise ValueError(f"영상 {v}: 프레임이 너무 적다 {len(out)}")
        me = out[TRIM:-TRIM].mean(0).astype(np.float32)
        rgb = c.center_square(c.read_frames(path, c.pick_by_time(pts, duration, FPS_RGB)))
        med = np.median(rgb.reshape(len(rgb), -1, 3), axis=1).mean(0).astype(np.float32)
        c.save_part("lowlevel", v, spec_id, motion_energy=me, rgb_median=med, n_frames_motion=len(frames), n_frames_rgb=len(rgb), n_native_frames=len(pts), duration_s=duration)
        if n % 20 == 0:
            print(n, "/", len(ids), "영상", v, flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", default="")
    ap.add_argument("--allow-dirty", action="store_true", help="시험용. 커밋 전 코드로 돌린다")
    main(ap.parse_args())
