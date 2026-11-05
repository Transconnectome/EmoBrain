#!/usr/bin/env python3
"""S3 공통: 참가자가 본 영상을 재현하고 프레임을 고른다 (04 S3, 01 3-2, O10, O11, 2026-11-05).

자료는 영상 파일, 캡션, stimuli.tsv뿐이다. 뇌 반응과 정서 정답은 읽지 않는다.

규칙
- 제시 길이: 8초 미만 영상은 반복해 8.0초에서 자르고(04 정할 것 11), 8초 이상은 한 번 그대로다. HK 기록에서 정한 값이고 MC에도 같은 특징을 쓴다(정할 것 13).
- O10: 시간축에서 t_k = k / f마다, 그 시각에 화면에 떠 있던 원래 프레임을 고른다. 보간하지 않는다. 장 수는 floor(제시 길이 × f)다.
- O11: 프레임 수 N이 창 W 이하이면 한 입력이고 N이 홀수면 마지막 한 장을 뺀다. N이 W를 넘으면 W장씩 겹치지 않게 자르고 마지막 창은 끝에 맞춘다. 이때 프레임을 빼지 않는다.
- 화면: 가운데 정사각형(원본의 짧은 변)을 잘라 모델 입력 크기로 줄인다. TimeSformer를 뺀 모든 모델과 저수준 특징이 같은 화면 범위를 쓴다.
"""
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[3]
STIMULI = REPO / "prereg_v2/manifests/stimuli.tsv"
CAPTIONS = REPO / "project/shared/data/caption_ck20.csv"
OUT = REPO / "project/output/final_2026-11/s3_features"
SHORT_PRESENTATION_S = 8.0  # 04 정할 것 11
N_VIDEOS = 2196
FFMPEG, FFPROBE = "/pscratch/sd/s/sjmoon/swift_PTL2/bin/ffmpeg", "/pscratch/sd/s/sjmoon/swift_PTL2/bin/ffprobe"  # 시스템 ffmpeg에는 h264 복호기가 없다(prereg_v2 crosswalk_audit.json과 같은 복호기)
EPS = 1e-9  # 초 단위 부동소수 오차만 막는다


def stimulus_table():
    s = pd.read_csv(STIMULI, sep="\t", comment="#").set_index("video_number").sort_index()
    if len(s) != N_VIDEOS or not (s.index.to_numpy() == np.arange(1, N_VIDEOS + 1)).all():
        raise ValueError("stimuli.tsv가 영상 2,196개가 아니다")
    return s[["path", "container_duration_s", "sha256", "n_decoded_frames"]]


def presented_seconds(duration):
    return SHORT_PRESENTATION_S if duration < SHORT_PRESENTATION_S else float(duration)


def frame_pts(path):
    """복호기가 실제로 내는 프레임의 시각(초). 첫 프레임을 0으로 맞춘다. 수가 read_frames의 출력과 같아야 한다."""
    out = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries", "frame=best_effort_timestamp_time", "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True).stdout
    pts = np.array([float(x.split(",")[0]) for x in out.split() if x.split(",")[0] not in ("", "N/A")])
    if len(pts) == 0 or (np.diff(pts) <= 0).any():
        raise ValueError(f"프레임 시각이 증가하지 않는다: {path}")
    return pts - pts[0]


def pick_by_time(pts, duration, fps):
    """O10. 원래 프레임 번호를 돌려준다."""
    p = presented_seconds(duration)
    n = int(np.floor(p * fps + EPS))
    t = np.arange(n) / fps
    if duration < SHORT_PRESENTATION_S:
        t = np.mod(t, duration)
    return np.maximum(np.searchsorted(pts, t + EPS, side="right") - 1, 0)


def presented_native_sequence(pts, duration):
    """제시 시간축에서 화면에 나온 원래 프레임의 순서(O14). 8초 미만은 반복해 8.0초 안의 프레임만 남긴다."""
    p = presented_seconds(duration)
    if duration >= SHORT_PRESENTATION_S:
        return np.arange(len(pts))
    keep, r = [], 0
    while r * duration < p - EPS:
        keep.append(np.flatnonzero(pts + r * duration < p - EPS))
        r += 1
    return np.concatenate(keep)


def windows(n, w):
    """O11. 입력마다의 시작 번호와 끝 번호(끝 미포함)."""
    if n <= 0:
        raise ValueError("프레임이 없다")
    if n <= w:
        return [(0, n - (n % 2))]
    starts = list(range(0, n - w + 1, w))
    if starts[-1] != n - w:
        starts.append(n - w)
    return [(s, s + w) for s in starts]


def read_frames(path, indices, shape_hint=None):
    """필요한 프레임만 메모리에 남긴다. 긴 고해상도 영상도 전체를 올리지 않는다. 돌려주는 배열은 (len(indices), H, W, 3) uint8이다."""
    indices = np.asarray(indices)
    want = np.unique(indices)
    info = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
    st = json.loads(info)["streams"][0]
    h, w = int(st["height"]), int(st["width"])
    proc = subprocess.Popen([FFMPEG, "-v", "error", "-i", str(path), "-map", "0:v:0", "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)  # 필요한 프레임만 읽고 끊으면 나는 파이프 오류를 숨긴다. 수는 아래에서 확인한다
    size = h * w * 3
    kept, i, j = {}, 0, 0
    while j < len(want):
        buf = proc.stdout.read(size)
        if len(buf) < size:
            break
        if i == want[j]:
            kept[int(i)] = np.frombuffer(buf, np.uint8).reshape(h, w, 3)
            j += 1
        i += 1
    proc.stdout.close()
    proc.terminate()
    proc.wait()
    if j != len(want):
        raise ValueError(f"프레임을 다 읽지 못했다: {path} {j}/{len(want)}")
    return np.stack([kept[int(k)] for k in indices])


def center_square(frames):
    """가운데 정사각형(짧은 변). 입력 (T, H, W, 3), 출력 (T, S, S, 3)."""
    h, w = frames.shape[1:3]
    s = min(h, w)
    top, left = (h - s) // 2, (w - s) // 2
    return frames[:, top:top + s, left:left + s]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(2**22), b""):
            h.update(b)
    return h.hexdigest()


def git_head():
    return subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


def hf_snapshot(name):
    """내려받은 가중치의 판(revision)을 돌려준다. 기록(M2)에 쓴다."""
    from huggingface_hub import snapshot_download
    p = Path(snapshot_download(name, local_files_only=True))
    return dict(checkpoint=name, revision=p.name, weights_sha256={f.name: sha256(f) for f in sorted(p.iterdir()) if f.suffix in (".safetensors", ".bin")})


def part_path(model, video_id):
    return OUT / model / "parts" / f"v{int(video_id):04d}.npz"


def todo_ids(model, ids):
    return [v for v in ids if not part_path(model, v).exists()]


def save_part(model, video_id, **arrays):
    """쓰다 끊겨도 깨진 파일이 남지 않게 임시 이름으로 쓰고 옮긴다."""
    p = part_path(model, video_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp.npz")
    np.savez(tmp, **arrays)
    tmp.replace(p)


def parse_ids(text):
    """'1-20' 또는 '1,5,9'. 비우면 전체."""
    if not text:
        return list(range(1, N_VIDEOS + 1))
    out = []
    for x in text.split(","):
        a, _, b = x.partition("-")
        out += list(range(int(a), int(b or a) + 1))
    return out
