#!/usr/bin/env python3
"""S3 코드의 회귀 시험 (2026-11-05). 영상 프레임 시각과 합성 조각만 쓴다. 뇌 반응과 정서 정답은 읽지 않고, 출력은 임시 폴더에만 쓴다.

Codex 검토(2026-11-05_s3_code_e09c351)가 재현한 네 문제가 다시 나오지 않는지 본다.
"""
import json
import os
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd

TMP = Path(tempfile.mkdtemp(prefix="s3_tests_"))
os.environ["S3_OUT"] = str(TMP)
import s3_common as c  # noqa: E402

PASS, FAIL = [], []


def ok(name, cond):
    (PASS if cond else FAIL).append(name)
    print("통과" if cond else "실패", name, flush=True)


def rejects(name, fn):
    try:
        fn()
    except SystemExit:
        ok(name, True)
        return
    ok(name, False)


def test_repeat_boundary():
    """정확한 분수 계산과 비교한다. 실제 재현 영상 243, 8, 23을 포함한다."""
    t = c.stimulus_table()
    errs = 0
    for v in t.index[t.container_duration_s < c.SHORT_PRESENTATION_S]:
        L = float(t.container_duration_s[v])
        Lf = Fraction(str(L))
        for f in (4, 15):
            n = int(c.SHORT_PRESENTATION_S * f)
            r = c.repeat_phase(np.arange(n) / f, L)
            exact = np.array([float(Fraction(k, f) % Lf) for k in range(n)])
            errs += int((np.abs(r - exact) > 1e-8).sum())
    ok(f"반복 위상이 정확한 분수 계산과 같다(어긋난 시점 {errs})", errs == 0)
    pts = c.frame_pts(t.path[243])
    idx = c.pick_by_time(pts, float(t.container_duration_s[243]), 4)
    ok("영상 243의 4.0초(k=16)는 첫 프레임이다", idx[16] == 0)
    idx15 = c.pick_by_time(pts, float(t.container_duration_s[243]), 15)
    ok("영상 243의 15 fps 경계(k=36, 60, 72, 84, 108)는 첫 프레임이다", all(idx15[k] == 0 for k in (36, 60, 72, 84, 108)))
    ok("영상 8의 4 fps k=21은 첫 프레임이다", c.pick_by_time(c.frame_pts(t.path[8]), float(t.container_duration_s[8]), 4)[21] == 0)
    ok("영상 23의 15 fps k=72는 첫 프레임이다", c.pick_by_time(c.frame_pts(t.path[23]), float(t.container_duration_s[23]), 15)[72] == 0)


def test_windows():
    ok("창 규칙", c.windows(33, 64) == [(0, 32)] and c.windows(64, 64) == [(0, 64)] and c.windows(65, 64) == [(0, 64), (1, 65)] and c.windows(130, 64) == [(0, 64), (64, 128), (66, 130)])


def test_screen():
    import torch  # noqa: F401
    import s3_vision as V
    f = np.zeros((2, 100, 200, 3), np.uint8)
    f[:, :, 50:150] = 255  # 가운데 정사각형만 흰색. 줄인 뒤 가운데를 자르면 흰색만 남아야 한다
    mean, std = np.zeros(3, np.float32), np.ones(3, np.float32)
    x = V.to_input(f, 50, mean, std, 2, "cpu")
    ok("크기 조정 뒤 가운데 자르기", x.shape == (2, 3, 50, 50) and float(x[:, :, :, 2:-2].min()) > 0.99)
    tall = np.zeros((1, 200, 100, 3), np.uint8)
    ok("세 위치 자르기의 모양", all(z.shape == (1, 3, 50, 50) for z in V.three_crops(tall, 50, 2)) and len(V.three_crops(tall, 50, 2)) == 3)


def test_spec_rejects_stale_parts():
    d = TMP / "stale"
    (d / "parts").mkdir(parents=True)
    c.save_part("stale", 1, "aaaa", mean=np.zeros(3))
    ok("사양이 같은 조각은 건너뛴다", c.todo_ids("stale", [1, 2], "aaaa") == [2])
    rejects("사양이 다른 조각은 멈춘다", lambda: c.todo_ids("stale", [1, 2], "bbbb"))
    np.savez(c.part_path("stale", 3), mean=np.zeros(3))
    rejects("사양이 없는 옛 조각은 멈춘다", lambda: c.todo_ids("stale", [3], "aaaa"))


def small_world(col):
    """영상 6개로 줄인 합성 세계."""
    c.N_VIDEOS = 6
    table = pd.DataFrame(dict(path="x", container_duration_s=[3.0, 3.0, 16.3, 20.0, 9.0, 3.0], sha256="x", n_decoded_frames=10), index=range(1, 7))
    c.stimulus_table = lambda: table
    return table


def write_spec(model, spec_id, files):
    d = c.OUT / model
    d.mkdir(parents=True, exist_ok=True)
    (d / f"spec_{spec_id}.json").write_text(json.dumps(dict(spec_id=spec_id, extraction_commit="x", code_sha256={f: c.sha256(c.CODE_DIR / f) for f in files}, stimuli_sha256=c.sha256(c.STIMULI))))


def vjepa_parts(table, **change):
    import s3_collect as col
    write_spec("vjepa2", "s1", col.CODE["vjepa2"])
    for v in table.index:
        dur = float(table.container_duration_s[v])
        n = int(np.floor(c.presented_seconds(dur) * 4 + c.EPS))
        win = c.windows(n, 64)
        per = np.ones((len(win),) + col.SHAPES["vjepa2"], np.float32)
        c.save_part("vjepa2", v, "s1", mean=per.mean(0), per_window=per, n_frames=n, windows=np.array(win), n_native_frames=30, duration_s=dur)


def test_collector():
    import s3_collect as col
    table = small_world(col)
    col_fn = lambda: col.vision("vjepa2")  # noqa: E731
    vjepa_parts(table)
    col_fn()
    ok("정상 조각은 통과한다", (c.OUT / "vjepa2/target.npy").exists() and np.load(c.OUT / "vjepa2/target.npy").shape == (6, 5632))
    z = np.load(c.OUT / "vjepa2/windows_per_video.npz")
    ok("65프레임 영상의 창별 값이 저장된다", "v0003" in z.files and z["v0003"].shape[0] == 2)
    m = json.loads((c.OUT / "vjepa2/manifest.json").read_text())
    ok("추출 커밋과 모으는 커밋을 따로 적는다", m["extraction"]["extraction_commit"] == "x" and m["collection_commit"] != "x")

    def edit(v, **kw):
        with np.load(c.part_path("vjepa2", v)) as q:
            d = {k: q[k] for k in q.files}
        d.update(kw)
        np.savez(c.part_path("vjepa2", v), **d)
    p = col.SHAPES["vjepa2"]
    bad = np.ones((2,) + p, np.float32)
    bad[0, 0, 0] = np.nan
    edit(3, per_window=bad)
    rejects("창별 값의 NaN을 거절한다", col_fn)
    vjepa_parts(table)
    edit(3, per_window=np.empty(0), windows=np.array([(0, 64)]))
    rejects("창이 빠진 65프레임 영상을 거절한다", col_fn)
    vjepa_parts(table)
    edit(1, mean=np.full(p, np.nan, np.float32))
    rejects("평균의 NaN을 거절한다", col_fn)
    vjepa_parts(table)
    edit(1, mean=np.zeros(p, np.float32))
    rejects("창 평균과 다른 평균을 거절한다", col_fn)
    vjepa_parts(table)
    edit(2, spec_id="다른사양")
    rejects("사양이 섞인 조각을 거절한다", col_fn)
    vjepa_parts(table)
    c.part_path("vjepa2", 6).unlink()
    rejects("빠진 영상을 거절한다", col_fn)
    vjepa_parts(table)
    s = json.loads((c.OUT / "vjepa2/spec_s1.json").read_text())
    s["code_sha256"]["s3_vision.py"] = "옛코드"
    (c.OUT / "vjepa2/spec_s1.json").write_text(json.dumps(s))
    rejects("옛 코드로 뽑은 조각을 거절한다", col_fn)

    write_spec("lowlevel", "s2", col.CODE["lowlevel"])
    for v in table.index:
        c.save_part("lowlevel", v, "s2", motion_energy=np.ones(6555, np.float32), rgb_median=np.ones(3, np.float32), n_native_frames=30, duration_s=float(table.container_duration_s[v]))
    col.lowlevel()
    ok("저수준 정상 통과", (c.OUT / "lowlevel/lowlevel.npy").exists())
    c.save_part("lowlevel", 2, "s2", motion_energy=np.ones(6555, np.float32), rgb_median=np.array([np.nan, 1, 1], np.float32), n_native_frames=30, duration_s=3.0)
    rejects("RGB의 NaN을 거절한다", col.lowlevel)

    def text(name, words=0, shape=(24, 1024), caption=True):
        d = c.OUT / name
        d.mkdir(parents=True, exist_ok=True)
        np.save(d / "video_mean.npy", np.ones((6,) + shape, np.float32))
        files = ["video_mean.npy", "per_caption_video_id.tsv"]
        if caption:
            np.save(d / "per_caption.npy", np.ones((120,) + shape, np.float32))
            files.append("per_caption.npy")
        pd.DataFrame(dict(video_id=np.repeat(np.arange(1, 7), 20))).to_csv(d / "per_caption_video_id.tsv", sep="\t", index=False)
        (d / "manifest.json").write_text(json.dumps(dict(n_affect_words=words, code_sha256={f: c.sha256(c.CODE_DIR / f) for f in col.CODE["deberta"]}, file_sha256={f: c.sha256(d / f) for f in files})))
    text("deberta")
    rejects("정서어 제거판이 없으면 거절한다", col.deberta)
    text("deberta_no_emotion_words", 181)
    col.deberta()
    ok("DeBERTa 두 판 정상 통과", np.load(c.OUT / "deberta/target.npy").shape == (6, 4096))
    text("deberta")
    (c.OUT / "deberta/per_caption.npy").unlink()
    rejects("캡션별 파일이 없으면 거절한다", col.deberta)
    text("deberta")
    pd.DataFrame(dict(video_id=np.repeat([1, 2, 3, 4, 5, 7], 20))).to_csv(c.OUT / "deberta/per_caption_video_id.tsv", sep="\t", index=False)
    rejects("캡션의 영상 번호 오류를 거절한다", col.deberta)
    text("mpnet", shape=(768,), caption=False)
    col.mpnet()
    ok("MPNet 정상 통과", True)
    x = np.ones((6, 768), np.float32)
    x[0, 0] = np.nan
    np.save(c.OUT / "mpnet/video_mean.npy", x)
    rejects("MPNet의 파일 변경과 NaN을 거절한다", col.mpnet)


if __name__ == "__main__":
    test_windows()
    test_screen()
    test_repeat_boundary()
    test_spec_rejects_stale_parts()
    test_collector()
    print("통과", len(PASS), "실패", len(FAIL), FAIL)
    sys.exit(1 if FAIL else 0)
