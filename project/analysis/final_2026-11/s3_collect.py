#!/usr/bin/env python3
"""S3: 영상별 조각을 모델별 파일로 모으고 04 S3의 확인 기준을 검사하며 추출 기록(M2)을 남긴다 (2026-11-05).

사용: s3_collect.py vjepa2 videomae timesformer clip lowlevel
출력(project/output/final_2026-11/s3_features/<모델>/)
  vjepa2: blocks.npy(2196, 40, 1408), target.npy(2196, 5632, block 10, 20, 30, 40), windows_per_video.npz(창으로 나뉜 영상의 창별 값)
  videomae, timesformer: blocks.npy, target.npy(block 3, 6, 9, 12)
  clip: image.npy(2196, 512)
  lowlevel: motion_energy.npy(2196, 6555), rgb_median.npy(2196, 3), lowlevel.npy(2196, 6558)
캡션 특징(deberta, mpnet)은 s3_text.py가 바로 파일로 쓴다. deberta는 여기서 target.npy(층 6, 12, 18, 24)를 만든다.
"""
import json
import sys

import numpy as np

import s3_common as c

VISION_LAYER_POS = dict(vjepa2=[9, 19, 29, 39], videomae=[0, 1, 2, 3], timesformer=[2, 5, 8, 11])  # 저장 순서에서의 위치. videomae는 3, 6, 9, 12만 저장했다
SHAPES = dict(vjepa2=(40, 1408), videomae=(4, 768), timesformer=(12, 768), clip=(512,))
CHECKPOINT = dict(vjepa2="facebook/vjepa2-vitg-fpc64-256", videomae="MCG-NJU/videomae-base", timesformer="facebook/timesformer-base-finetuned-k400", clip="openai/clip-vit-base-patch16")


def collect_parts(model, key):
    miss = c.todo_ids(model, range(1, c.N_VIDEOS + 1))
    if miss:
        raise SystemExit(f"{model}: 빠진 영상 {len(miss)}개, 앞쪽 {miss[:10]}")
    return [np.load(c.part_path(model, v)) for v in range(1, c.N_VIDEOS + 1)]


def check(x, name):
    if len(x) != c.N_VIDEOS or not np.isfinite(x).all():
        raise SystemExit(f"{name}: 영상 수가 다르거나 NaN이 있다 {x.shape}")
    print(name, x.shape, "확인 통과")


def write_manifest(model, extra, files):
    d = c.OUT / model
    from huggingface_hub import __version__ as _  # noqa: F401
    info = dict(model=model, code_commit=c.git_head(), code_sha256={f: c.sha256(c.REPO / "project/analysis/final_2026-11" / f) for f in ("s3_common.py", "s3_vision.py", "s3_text.py", "s3_lowlevel.py", "s3_collect.py")}, stimuli_sha256=c.sha256(c.STIMULI), short_presentation_s=c.SHORT_PRESENTATION_S, decoder=c.FFMPEG, file_sha256={f: c.sha256(d / f) for f in files}, **extra)
    (d / "manifest.json").write_text(json.dumps(info, ensure_ascii=False, indent=1))


def vision(model):
    d = c.OUT / model
    parts = collect_parts(model, "mean")
    x = np.stack([p["mean"] for p in parts]).astype(np.float32)
    check(x, model)
    if x.shape[1:] != SHAPES[model]:
        raise SystemExit(f"{model}: 차원이 다르다 {x.shape}")
    extra = dict(c.hf_snapshot(CHECKPOINT[model]))
    if model == "clip":
        np.save(d / "image.npy", x)
        files = ["image.npy"]
        extra.update(fps=4, pooling="프레임별 투영 벡터를 L2 정규화해 평균하고 다시 정규화")
    else:
        np.save(d / "blocks.npy", x)
        target = x[:, VISION_LAYER_POS[model]].reshape(len(x), -1)
        np.save(d / "target.npy", target)
        files = ["blocks.npy", "target.npy"]
        extra.update(layers="hidden_states[i], i는 1부터, 0번(embedding) 제외", target_dim=target.shape[1])
        if model == "vjepa2":
            n = np.array([int(p["n_frames"]) for p in parts])
            t = c.stimulus_table()
            short = t.container_duration_s.to_numpy() < c.SHORT_PRESENTATION_S
            if not (n[short] == 32).all():
                raise SystemExit("8초 미만 영상의 프레임 수가 32장이 아니다")
            multi = {f"v{i + 1:04d}": parts[i]["per_window"] for i in np.flatnonzero(n > 64)}
            np.savez(d / "windows_per_video.npz", **multi)
            np.save(d / "n_frames.npy", n)
            files += ["windows_per_video.npz", "n_frames.npy"]
            print("창으로 나뉜 영상", len(multi))
            if target.shape[1] != 5632:
                raise SystemExit("V-JEPA 2 목표가 5,632차원이 아니다")
            extra.update(fps=4, window=64, input_size=256, last_block_normed=True, screen="가운데 정사각형 뒤 256, bicubic, antialias", pooling="입력 안 token 평균, 창이 여럿이면 창 평균")
    write_manifest(model, extra, files)


def lowlevel():
    d = c.OUT / "lowlevel"
    parts = collect_parts("lowlevel", "motion_energy")
    me = np.stack([p["motion_energy"] for p in parts]).astype(np.float32)
    rgb = np.stack([p["rgb_median"] for p in parts]).astype(np.float32)
    check(me, "motion_energy")
    if me.shape[1] != 6555 or rgb.shape[1] != 3:
        raise SystemExit("저수준 특징의 차원이 다르다")
    np.save(d / "motion_energy.npy", me)
    np.save(d / "rgb_median.npy", rgb)
    np.save(d / "lowlevel.npy", np.hstack([me, rgb]))
    write_manifest("lowlevel", dict(package="pymoten 0.1.3", fps_motion=15, size=96, trim_each_end=5, nonlinearity="pymoten 기본 log(x + 1e-5)", fps_rgb=4), ["motion_energy.npy", "rgb_median.npy", "lowlevel.npy"])


def deberta_target():
    for name in ("deberta", "deberta_no_emotion_words"):
        d = c.OUT / name
        if not (d / "video_mean.npy").exists():
            print(name, "없음. 건너뜀")
            continue
        x = np.load(d / "video_mean.npy")
        check(x, name)
        if x.shape[1:] != (24, 1024):
            raise SystemExit("DeBERTa 차원이 다르다")
        np.save(d / "target.npy", x[:, [5, 11, 17, 23]].reshape(len(x), -1))
        print(name, "목표", 4096)


if __name__ == "__main__":
    for m in sys.argv[1:]:
        if m == "lowlevel":
            lowlevel()
        elif m == "deberta":
            deberta_target()
        else:
            vision(m)
