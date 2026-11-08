#!/usr/bin/env python3
"""S3: 영상별 조각을 모델별 파일로 모으고 04 S3의 확인 기준을 검사하며 추출 기록(M2)을 남긴다 (2026-11-05).

사용: s3_collect.py vjepa2 videomae timesformer clip lowlevel deberta mpnet
커밋 전 코드로 뽑은 시험 출력은 거절한다. 시험에서만 S3_ALLOW_DIRTY_COLLECT=1을 준다.
출력(<output_root>/s3_features/<모델>/)
  vjepa2: blocks.npy(2196, 40, 1408), target.npy(2196, 5632, block 10, 20, 30, 40), windows_per_video.npz(창으로 나뉜 영상의 창별 값), video_info.tsv
  videomae, timesformer: blocks.npy, target.npy(block 3, 6, 9, 12), video_info.tsv
  clip: image.npy(2196, 512), video_info.tsv
  lowlevel: motion_energy.npy(2196, 6555), rgb_median.npy(2196, 3), lowlevel.npy(2196, 6558), video_info.tsv
  deberta: target.npy(층 6, 12, 18, 24). 원판과 정서어 제거판이 모두 있어야 한다
  mpnet: 검사만 한다
모든 조각의 사양이 하나이고 지금 코드와 같아야 한다. 추출 커밋과 모으는 커밋을 따로 적는다.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

import s3_common as c

TARGET_POS = dict(vjepa2=[9, 19, 29, 39], videomae=[0, 1, 2, 3], timesformer=[2, 5, 8, 11])  # 저장 순서에서의 위치. videomae는 3, 6, 9, 12만 저장했다
SHAPES = dict(vjepa2=(40, 1408), videomae=(4, 768), timesformer=(12, 768), clip=(512,))
TARGET_DIM = dict(vjepa2=5632, videomae=3072, timesformer=3072)
WINDOW = dict(vjepa2=64, videomae=16)
CODE = dict(vjepa2=["s3_common.py", "s3_vision.py"], videomae=["s3_common.py", "s3_vision.py"], timesformer=["s3_common.py", "s3_vision.py"], clip=["s3_common.py", "s3_vision.py"], lowlevel=["s3_common.py", "s3_lowlevel.py"], deberta=["s3_common.py", "s3_text.py"], mpnet=["s3_common.py", "s3_text.py"])


def fail(text):
    raise SystemExit(text)


def finite(x, name, shape=None):
    x = np.asarray(x)
    if shape is not None and x.shape != shape:
        fail(f"{name}: 차원이 다르다 {x.shape}, 기대 {shape}")
    if not np.isfinite(x).all():
        fail(f"{name}: NaN이나 무한대가 있다")


def reject_dirty(name, record):
    if record.get("code_dirty_at_extraction") and os.environ.get("S3_ALLOW_DIRTY_COLLECT") != "1":
        fail(f"{name}: 커밋 전 코드로 뽑은 결과다. 본 실행 결과로 모을 수 없다")


def load_parts(model):
    ids = range(1, c.N_VIDEOS + 1)
    miss = [v for v in ids if not c.part_path(model, v).exists()]
    if miss:
        fail(f"{model}: 빠진 영상 {len(miss)}개, 앞쪽 {miss[:10]}")
    parts = []
    for v in ids:
        with np.load(c.part_path(model, v)) as z:
            parts.append({k: z[k] for k in z.files})
    specs = {str(p["spec_id"]) if "spec_id" in p else "없음" for p in parts}
    if len(specs) != 1 or "없음" in specs:
        fail(f"{model}: 조각의 사양이 하나가 아니다 {sorted(specs)[:5]}")
    spec_id = specs.pop()
    f = c.OUT / model / f"spec_{spec_id}.json"
    if not f.exists():
        fail(f"{model}: 사양 파일이 없다 {f}")
    spec = json.loads(f.read_text())
    for name in CODE[model]:
        if spec["code_sha256"].get(name) != c.sha256(c.CODE_DIR / name):
            fail(f"{model}: 추출 때의 {name}와 지금 코드가 다르다. 다시 뽑아야 한다")
    reject_dirty(model, spec)
    if spec["stimuli_sha256"] != c.sha256(c.STIMULI):
        fail(f"{model}: 입력 기록이 추출 때와 다르다")
    return parts, spec


def write_manifest(model, spec, files, **extra):
    d = c.OUT / model
    info = dict(model=model, collection_commit=c.git_head(), extraction=spec, file_sha256={f: c.sha256(d / f) for f in files}, **extra)
    (d / "manifest.json").write_text(json.dumps(info, ensure_ascii=False, indent=1))


def video_info(parts, model, spec):
    t = c.stimulus_table()
    n_native = np.array([int(p["n_native_frames"]) for p in parts])
    dur = t.container_duration_s.to_numpy(float)
    if not all(float(p["duration_s"]) == d for p, d in zip(parts, dur)):
        fail(f"{model}: 영상 길이가 기록과 다르다")
    df = pd.DataFrame(dict(video_id=np.arange(1, c.N_VIDEOS + 1), duration_s=dur, presented_s=[c.presented_seconds(d) for d in dur], n_native_frames=n_native, native_frames_per_s=n_native / dur))
    if "n_frames" in parts[0]:
        df["n_frames"] = [int(p["n_frames"]) for p in parts]
        if model in WINDOW or model == "clip":
            short = dur < c.SHORT_PRESENTATION_S
            if not (df.n_frames.to_numpy()[short] == 32).all():
                fail(f"{model}: 8초 미만 영상의 프레임 수가 32장이 아니다")
    df.to_csv(c.OUT / model / "video_info.tsv", sep="\t", index=False)
    return df


def vision(model):
    parts, spec = load_parts(model)
    d = c.OUT / model
    x = np.stack([p["mean"] for p in parts]).astype(np.float32)
    finite(x, model, (c.N_VIDEOS,) + SHAPES[model])
    video_info(parts, model, spec)
    files = ["video_info.tsv"]
    if model == "clip":
        np.save(d / "image.npy", x)
        files.append("image.npy")
    else:
        np.save(d / "blocks.npy", x)
        target = x[:, TARGET_POS[model]].reshape(len(x), -1)
        if target.shape[1] != TARGET_DIM[model]:
            fail(f"{model}: 목표 차원이 다르다 {target.shape}")
        np.save(d / "target.npy", target)
        files += ["blocks.npy", "target.npy"]
    if model in WINDOW:
        w = WINDOW[model]
        multi = {}
        for i, p in enumerate(parts):
            expected = c.windows(int(p["n_frames"]), w)
            if [tuple(r) for r in p["windows"].tolist()] != expected:
                fail(f"{model} 영상 {i + 1}: 창 목록이 규칙과 다르다")
            per = p["per_window"]
            finite(per, f"{model} 영상 {i + 1} 창별 값", (len(expected),) + SHAPES[model])
            if not np.allclose(per.mean(0), p["mean"], rtol=1e-5, atol=1e-5):
                fail(f"{model} 영상 {i + 1}: 평균이 창 평균과 다르다")
            if len(expected) > 1:
                multi[f"v{i + 1:04d}"] = per
        np.savez(d / "windows_per_video.npz", **multi)
        files.append("windows_per_video.npz")
        print(model, "창으로 나뉜 영상", len(multi))
    write_manifest(model, spec, files)
    print(model, x.shape, "확인 통과")


def lowlevel():
    parts, spec = load_parts("lowlevel")
    d = c.OUT / "lowlevel"
    me = np.stack([p["motion_energy"] for p in parts]).astype(np.float32)
    rgb = np.stack([p["rgb_median"] for p in parts]).astype(np.float32)
    finite(me, "motion_energy", (c.N_VIDEOS, 6555))
    finite(rgb, "rgb_median", (c.N_VIDEOS, 3))
    video_info(parts, "lowlevel", spec)
    np.save(d / "motion_energy.npy", me)
    np.save(d / "rgb_median.npy", rgb)
    np.save(d / "lowlevel.npy", np.hstack([me, rgb]))
    write_manifest("lowlevel", spec, ["video_info.tsv", "motion_energy.npy", "rgb_median.npy", "lowlevel.npy"])
    print("lowlevel 확인 통과")


def text_check(name, shape, n_per_caption=None):
    d = c.OUT / name
    if not (d / "manifest.json").exists():
        fail(f"{name}: 없거나 끝나지 않았다(manifest.json 없음)")
    info = json.loads((d / "manifest.json").read_text())
    for f, h in info["file_sha256"].items():
        if not (d / f).exists() or c.sha256(d / f) != h:
            fail(f"{name}: {f}가 없거나 기록과 다르다")
    reject_dirty(name, info)
    model = name.split("_")[0]
    for f in CODE[model]:
        if info["code_sha256"].get(f) != c.sha256(c.CODE_DIR / f):
            fail(f"{name}: 추출 때의 {f}와 지금 코드가 다르다")
    x = np.load(d / "video_mean.npy")
    finite(x, name, shape)
    ids = pd.read_csv(d / "per_caption_video_id.tsv", sep="\t").video_id.to_numpy()
    if not (np.repeat(np.arange(1, c.N_VIDEOS + 1), 20) == ids).all():
        fail(f"{name}: 캡션의 영상 번호가 2,196개 × 20개 순서가 아니다")
    if n_per_caption:
        y = np.load(d / "per_caption.npy", mmap_mode="r")
        finite(y, name + " 캡션별", n_per_caption)
    return d, x, info


def deberta():
    for name, words in (("deberta", 0), ("deberta_no_emotion_words", 181)):
        d, x, info = text_check(name, (c.N_VIDEOS, 24, 1024), (c.N_VIDEOS * 20, 24, 1024))
        if info["n_affect_words"] != words:
            fail(f"{name}: 정서어 수가 {words}개가 아니다")
        np.save(d / "target.npy", x[:, [5, 11, 17, 23]].reshape(len(x), -1))
        info["target_sha256"] = c.sha256(d / "target.npy")
        info["collection_commit"] = c.git_head()
        (d / "manifest.json").write_text(json.dumps(info, ensure_ascii=False, indent=1))
        print(name, "목표 4,096, 확인 통과")


def mpnet():
    text_check("mpnet", (c.N_VIDEOS, 768))
    print("mpnet 확인 통과")


if __name__ == "__main__":
    for m in sys.argv[1:]:
        dict(lowlevel=lowlevel, deberta=deberta, mpnet=mpnet).get(m, lambda m=m: vision(m))()
