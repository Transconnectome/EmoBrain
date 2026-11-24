#!/usr/bin/env python3
"""S3 코드의 회귀 시험 (2026-11-05). 영상 프레임 시각과 합성 조각만 쓴다. 뇌 반응과 정서 정답은 읽지 않고, 출력은 임시 폴더에만 쓴다.

Codex 검토(2026-11-05_s3_code_e09c351)가 재현한 네 문제가 다시 나오지 않는지 본다.
"""
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1] / "src"))  # 코드는 src에 있다
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
    from torchvision.transforms import InterpolationMode
    from torchvision.transforms.v2 import functional as TF
    rng = np.random.default_rng(0)
    f = rng.integers(0, 256, (2, 101, 203, 3), dtype=np.uint8)  # 비대칭 잡음. 순서가 다르면 화소가 달라진다
    mean, std = np.zeros(3, np.float32), np.ones(3, np.float32)
    got = V.to_input(f, 50, 50, mean, std, 2, "cpu")
    t = torch.from_numpy(f).permute(0, 3, 1, 2)
    nh, nw = c.scaled_shape(101, 203, 50)
    first_resize = TF.resize(t, [nh, nw], interpolation=InterpolationMode.BILINEAR, antialias=True)[:, :, :, (nw - 50) // 2:(nw - 50) // 2 + 50].float().div(255.0)
    side = 101
    left = (203 - side) // 2
    first_crop = TF.resize(t[:, :, :, left:left + side], [50, 50], interpolation=InterpolationMode.BILINEAR, antialias=True).float().div(255.0)
    ok("크기 조정 뒤 가운데 자르기와 화소까지 같다", got.shape == (2, 3, 50, 50) and bool(torch.allclose(got, first_resize)))
    ok("자른 뒤 줄이는 옛 순서와는 다르다", not bool(torch.allclose(got, first_crop)))
    got = V.to_input(f, 57, 50, mean, std, 2, "cpu")
    nh, nw = c.scaled_shape(101, 203, 57)
    full = TF.resize(t, [nh, nw], interpolation=InterpolationMode.BILINEAR, antialias=True)
    top, left = (nh - 50) // 2, (nw - 50) // 2
    ok("짧은 변과 자르는 크기가 달라도(V-JEPA 2 방식) 가운데를 자른다", got.shape == (2, 3, 50, 50) and bool(torch.allclose(got, full[:, :, top:top + 50, left:left + 50].float().div(255.0))))
    for name, cfg in V.CONFIG.items():
        _, _, _, short, crop = V.official_values(c.hf_snapshot(cfg["checkpoint"])["path"])
        ok(f"{name}의 크기가 설정 파일과 같다({short}, {crop})", (short, crop) == (cfg["short"], cfg["crop"]))
    ramp = np.tile(np.linspace(0, 255, 200).astype(np.uint8)[None, None, :, None], (1, 100, 1, 3))
    crops = V.three_crops(ramp, 50, 2)
    means = [float(z.float().mean()) for z in crops]
    ok("세 위치가 왼쪽, 가운데, 오른쪽이다", len(crops) == 3 and all(z.shape == (1, 3, 50, 50) for z in crops) and means[0] < means[1] < means[2])
    tall = np.tile(np.linspace(0, 255, 200).astype(np.uint8)[None, :, None, None], (1, 1, 100, 3))
    means = [float(z.float().mean()) for z in V.three_crops(tall, 50, 2)]
    ok("세로 영상의 세 위치가 위, 가운데, 아래다", means[0] < means[1] < means[2])


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
    def reseal(name):
        d = c.OUT / name
        m = json.loads((d / "manifest.json").read_text())
        m["file_sha256"] = {f: c.sha256(d / f) for f in m["file_sha256"]}
        (d / "manifest.json").write_text(json.dumps(m))
    pd.DataFrame(dict(video_id=np.repeat([1, 2, 3, 4, 5, 7], 20))).to_csv(c.OUT / "deberta/per_caption_video_id.tsv", sep="\t", index=False)
    rejects("캡션 파일이 기록과 다르면 거절한다", col.deberta)
    reseal("deberta")
    rejects("해시가 맞아도 캡션의 영상 번호 오류를 거절한다", col.deberta)
    text("mpnet", shape=(768,), caption=False)
    col.mpnet()
    ok("MPNet 정상 통과", True)
    x = np.ones((6, 768), np.float32)
    x[0, 0] = np.nan
    np.save(c.OUT / "mpnet/video_mean.npy", x)
    rejects("MPNet의 파일 변경을 거절한다", col.mpnet)
    reseal("mpnet")
    rejects("해시가 맞아도 MPNet의 NaN을 거절한다", col.mpnet)
    text("mpnet", shape=(768,), caption=False)
    m = json.loads((c.OUT / "mpnet/manifest.json").read_text())
    m["code_dirty_at_extraction"] = True
    (c.OUT / "mpnet/manifest.json").write_text(json.dumps(m))
    rejects("커밋 전 코드로 뽑은 캡션 결과를 거절한다", col.mpnet)
    os.environ["S3_ALLOW_DIRTY_COLLECT"] = "1"
    col.mpnet()
    ok("시험에서만 커밋 전 결과를 모을 수 있다", True)
    del os.environ["S3_ALLOW_DIRTY_COLLECT"]
    vjepa_parts(table)
    s = json.loads((c.OUT / "vjepa2/spec_s1.json").read_text())
    s["code_dirty_at_extraction"] = True
    (c.OUT / "vjepa2/spec_s1.json").write_text(json.dumps(s))
    rejects("커밋 전 코드로 뽑은 조각을 거절한다", lambda: col.vision("vjepa2"))


def test_text_provenance():
    """계산 중에 입력이나 코드가 바뀌면 나중 값을 기록하지 않고 멈춘다."""
    import s3_text as X
    keep = c.CAPTIONS
    tmp = TMP / "captions.csv"
    lines = ["video_id,description"] + [f'{v},"scene {v}"' for v in range(1, c.N_VIDEOS + 1) for _ in range(20)]
    tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    c.CAPTIONS = tmp
    frozen = X.freeze_inputs(False)
    vid, text = X.load_captions(False, frozen["raw"], frozen["words"])
    tmp.write_text("\n".join(lines).replace("scene", "changed") + "\n", encoding="utf-8")
    ok("고정한 내용으로 처리한다", text[0] == "scene 1")
    rejects("계산 중 캡션이 바뀌면 멈춘다", lambda: X.assert_unchanged(frozen, False))
    ok("기록할 해시는 처리한 내용의 해시다", frozen["captions_sha256"] != c.sha256(tmp))
    c.CAPTIONS = keep
    frozen = X.freeze_inputs(True)
    ok("정서어 목록을 함께 고정한다", len(frozen["words"]) == 181 and frozen["affect_words_sha256"] != "")
    X.assert_unchanged(frozen, True)
    bad = dict(frozen, code_sha256=dict(frozen["code_sha256"], **{"s3_text.py": "옛코드"}))
    rejects("계산 중 코드가 바뀌면 멈춘다", lambda: X.assert_unchanged(bad, True))
    # 모델을 불러오는 동안 파일과 커밋이 바뀌어도 실행 중인 코드의 값을 기록하고, 계산 전에 멈춘다
    real_sha, real_head = c.sha256, c.git_head
    c.sha256 = lambda p: "나중해시" if str(p).endswith(".py") else real_sha(p)
    c.git_head = lambda: "나중커밋"
    later = X.freeze_inputs(True)
    ok("불러오는 동안 바뀌어도 시작 때의 커밋과 해시를 기록한다", later["extraction_commit"] == c.START_HEAD and later["code_sha256"]["s3_text.py"] == c.START_CODE["s3_text.py"])
    rejects("불러오는 동안 코드가 바뀌면 계산 전에 멈춘다", lambda: X.assert_unchanged(later, True))
    rejects("시각 추출도 시작 뒤 코드가 바뀌면 멈춘다", lambda: c.make_spec("later", ["s3_common.py"], allow_dirty=True))
    c.sha256, c.git_head = real_sha, real_head


def test_author_check():
    """h5py가 없는 환경에서도 비교 함수만 본다."""
    import types
    sys.modules.setdefault("h5py", types.ModuleType("h5py"))
    import s3_author_check as A
    x = np.random.default_rng(0).normal(size=(5, 20))
    r = A.compare("m", x.copy(), x.copy(), 6)
    ok("같은 값은 r 1, 차이 0", abs(r["r_same_min"] - 1) < 1e-9 and r["max_abs_diff"] == 0 and r["n_constant_ours"] == 0)
    bad = x.copy()
    bad[0, 0] = np.nan
    rejects("우리 특징의 NaN을 거절한다", lambda: A.compare("m", bad, x.copy(), 6))
    rejects("저자 특징의 NaN을 거절한다", lambda: A.compare("m", x.copy(), bad, 6))
    flat = x[:4].copy()
    flat[1] = 3.0
    r = A.compare("m", flat, flat.copy(), 6)
    ok("상수 벡터는 따로 센다", r["n_constant_ours"] == 1 and r["n_r_same"] == 3 and np.isfinite(r["r_same_min"]))
    expect = [np.corrcoef(flat[i], flat[(i + 1) % 4])[0, 1] for i in (2, 3)]  # 원래 순서의 짝 가운데 상수 행이 없는 것
    ok("다음 영상 짝은 원래 순서를 지킨다", r["n_r_next"] == 2 and abs(r["r_next_video_median"] - float(np.median(expect))) < 1e-9)
    one = np.full((4, 20), 3.0)
    one[0] = x[0]
    r = A.compare("m", one, one.copy(), 6)
    ok("비상수 행이 하나면 다음 영상 비교는 계산 불가다", r["n_r_same"] == 1 and r["n_r_next"] == 0 and np.isnan(r["r_next_video_median"]))
    r = A.compare("m", np.zeros((4, 20)), np.zeros((4, 20)), 6)
    ok("모두 상수여도 멈추지 않고 계산 불가로 적는다", r["n_r_same"] == 0 and np.isnan(r["r_same_min"]) and r["max_abs_diff"] == 0)
    r = A.compare("m", np.full((4, 1024), 0.1), np.full((4, 1024), 0.1), 6)
    ok("0.1 같은 값의 상수도 상수로 본다", r["n_constant_ours"] == 4 and r["n_r_same"] == 0)


def test_video_root():
    """Codex 9d35ea0 필수 2. 영상 경로는 video_root 기준이고, 레포 표에는 절대 경로가 없다."""
    import paths as P
    raw = pd.read_csv(c.STIMULI, sep="\t", comment="#")
    ok("data/stimuli.tsv의 path는 모두 상대 경로다", not any(Path(x).is_absolute() for x in raw.path))
    ok("stimuli.tsv에 서버 경로가 없다", "/pscratch" not in c.STIMULI.read_text())
    t = c.stimulus_table()
    ok("영상 경로는 video_root에 붙는다", all(str(x).startswith(str(P.VIDEO_ROOT) + "/") for x in t.path))
    old = P.VIDEO_ROOT
    try:
        P.VIDEO_ROOT = Path("/tmp/다른_서버/videos")
        ok("video_root를 바꾸면 경로가 따라 바뀐다", c.stimulus_table().path.iloc[0] == "/tmp/다른_서버/videos/" + raw.path.iloc[0])
    finally:
        P.VIDEO_ROOT = old


if __name__ == "__main__":
    test_video_root()
    test_windows()
    test_screen()
    test_repeat_boundary()
    test_spec_rejects_stale_parts()
    test_collector()
    test_text_provenance()
    test_author_check()
    print("통과", len(PASS), "실패", len(FAIL), FAIL)
    sys.exit(1 if FAIL else 0)
