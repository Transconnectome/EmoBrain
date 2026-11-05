#!/usr/bin/env python3
"""S3 시각 모델 특징: V-JEPA 2(주), VideoMAE, TimeSformer, CLIP (04 S3, 01 3-1, 3-2, O10, O11, O14, O15, 2026-11-05).

사용: s3_vision.py --model vjepa2 [--ids 1-20] [--device cuda]
저장: project/output/final_2026-11/s3_features/<모델>/parts/v0001.npz. 이미 있는 영상은 건너뛴다. 파일로 모으는 일은 s3_collect.py가 한다.

층 번호는 1부터 센다. hidden_states[i]가 i번째 block의 출력이고 0번(embedding)은 쓰지 않는다(O15).
V-JEPA 2의 hidden_states[40]은 마지막 정규화층을 거친 값이다(transformers 4.57 VJEPA2Encoder). VideoMAE와 TimeSformer의 hidden_states에는 정규화층이 없다.
"""
import argparse

import numpy as np
import torch
from torchvision.transforms.v2 import functional as TF
from torchvision.transforms import InterpolationMode

import s3_common as c

CONFIG = dict(
    vjepa2=dict(checkpoint="facebook/vjepa2-vitg-fpc64-256", fps=4, window=64, size=256, layers=list(range(1, 41))),
    videomae=dict(checkpoint="MCG-NJU/videomae-base", fps=4, window=16, size=224, layers=[3, 6, 9, 12]),
    timesformer=dict(checkpoint="facebook/timesformer-base-finetuned-k400", size=224, layers=list(range(1, 13))),
    clip=dict(checkpoint="openai/clip-vit-base-patch16", fps=4, size=224),
)
RESAMPLE = InterpolationMode.BICUBIC


def normalization(name):
    """체크포인트의 공식 값(04 S3). 전처리 설정에서 읽는다."""
    from transformers import AutoImageProcessor, AutoVideoProcessor
    try:
        p = AutoVideoProcessor.from_pretrained(name, local_files_only=True)
    except Exception:
        p = AutoImageProcessor.from_pretrained(name, local_files_only=True)
    return np.asarray(p.image_mean, np.float32), np.asarray(p.image_std, np.float32)


def to_input(frames, size, mean, std, device):
    """(T, H, W, 3) uint8 → (T, 3, size, size) 정규화. 가운데 정사각형은 부르는 쪽에서 자른다."""
    x = torch.from_numpy(frames).permute(0, 3, 1, 2)
    x = TF.resize(x, [size, size], interpolation=RESAMPLE, antialias=True).float().div(255.0).clamp(0, 1)
    m, s = torch.tensor(mean).view(1, 3, 1, 1), torch.tensor(std).view(1, 3, 1, 1)
    return ((x - m) / s).to(device)


def run_vjepa2(model, x, layers):
    h = model(pixel_values_videos=x[None], skip_predictor=True, output_hidden_states=True).hidden_states
    if len(h) != 41:
        raise ValueError(f"block 수가 40이 아니다: {len(h) - 1}")
    return torch.stack([h[i].mean(1)[0] for i in layers]).cpu().numpy().astype(np.float32)


def run_videomae(model, x, layers):
    h = model(pixel_values=x[None], output_hidden_states=True).hidden_states
    return torch.stack([h[i].mean(1)[0] for i in layers]).cpu().numpy().astype(np.float32)


def timesformer_clips(pts, duration):
    """O14. 공개 코드의 추출 부분이 없어(04 S1) 01의 서술대로 구성한다. 반복 재현 영상의 프레임 순서에 적용한다."""
    seq = c.presented_native_sequence(pts, duration)
    pos = np.arange(0, len(seq), 32)
    if len(pos) < 8:
        return [seq[np.linspace(0, len(seq) - 1, 8).round().astype(int)]]
    starts = list(range(0, len(pos) - 8 + 1, 8))
    if starts[-1] != len(pos) - 8:
        starts.append(len(pos) - 8)
    return [seq[pos[s:s + 8]] for s in starts]


def three_crops(frames, size):
    """짧은 변을 size로 줄이고 긴 변을 따라 세 위치(왼쪽, 가운데, 오른쪽 또는 위, 가운데, 아래)를 자른다."""
    t, h, w = frames.shape[:3]
    nh, nw = (size, int(round(w * size / h))) if h <= w else (int(round(h * size / w)), size)
    x = TF.resize(torch.from_numpy(frames).permute(0, 3, 1, 2), [nh, nw], interpolation=RESAMPLE, antialias=True)
    spare = max(nh, nw) - size
    out = []
    for off in (0, spare // 2, spare):
        out.append(x[:, :, off:off + size, :size] if nh >= nw else x[:, :, :size, off:off + size])
    return out


def extract(a):
    cfg = CONFIG[a.model]
    device = a.device
    table = c.stimulus_table()
    mean, std = normalization(cfg["checkpoint"])
    if a.model == "vjepa2":
        from transformers import VJEPA2Model as M
    elif a.model == "videomae":
        from transformers import VideoMAEModel as M
    elif a.model == "timesformer":
        from transformers import TimesformerModel as M
    else:
        from transformers import CLIPModel as M
    model = M.from_pretrained(cfg["checkpoint"], local_files_only=True, attn_implementation="eager" if a.model == "timesformer" else None).to(device).eval()
    ids = c.todo_ids(a.model, c.parse_ids(a.ids))
    print(a.model, "할 영상", len(ids), flush=True)
    for n, v in enumerate(ids):
        path, duration = table.path[v], float(table.container_duration_s[v])
        pts = c.frame_pts(path)
        with torch.no_grad():
            if a.model in ("vjepa2", "videomae"):
                idx = c.pick_by_time(pts, duration, cfg["fps"])
                frames = c.center_square(c.read_frames(path, idx))
                win = c.windows(len(idx), cfg["window"])
                fn = run_vjepa2 if a.model == "vjepa2" else run_videomae
                per = np.stack([fn(model, to_input(frames[s:e], cfg["size"], mean, std, device), cfg["layers"]) for s, e in win])
                c.save_part(a.model, v, mean=per.mean(0), per_window=per if len(win) > 1 else np.empty(0), n_frames=len(idx), windows=np.array(win))
            elif a.model == "timesformer":
                clips = timesformer_clips(pts, duration)
                sums = []
                for clip in clips:
                    for crop in three_crops(c.read_frames(path, clip), cfg["size"]):
                        x = crop.float().div(255.0).clamp(0, 1)
                        m, s = torch.tensor(mean).view(1, 3, 1, 1), torch.tensor(std).view(1, 3, 1, 1)
                        x = ((x - m) / s).to(device)
                        h = model(pixel_values=x[None], output_hidden_states=True).hidden_states
                        sums.append(torch.stack([h[i][:, 1:].mean(1)[0] for i in cfg["layers"]]).cpu().numpy().astype(np.float32))  # CLS token은 뺀다
                c.save_part(a.model, v, mean=np.mean(sums, 0), n_clips=len(clips))
            else:
                idx = c.pick_by_time(pts, duration, cfg["fps"])
                frames = c.center_square(c.read_frames(path, idx))
                x = to_input(frames, cfg["size"], mean, std, device)
                out = torch.cat([model.get_image_features(pixel_values=x[i:i + 64]) for i in range(0, len(x), 64)])
                out = torch.nn.functional.normalize(out, dim=1).mean(0)
                c.save_part(a.model, v, mean=torch.nn.functional.normalize(out, dim=0).cpu().numpy().astype(np.float32), n_frames=len(idx))
        if n % 50 == 0:
            print(n, "/", len(ids), "영상", v, flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=list(CONFIG), required=True)
    ap.add_argument("--ids", default="")
    ap.add_argument("--device", default="cuda")
    extract(ap.parse_args())
