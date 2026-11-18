#!/usr/bin/env python3
"""s10_mc_dgroup 합성 자료 시험(실제 결과는 읽지 않는다). src에서 실행: python ../tests/s10_mc_dgroup_tests.py"""
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import s10_mc_dgroup as G  # noqa: E402

FAILED = []


def check(name, ok):
    print(("통과 " if ok else "실패 ") + name, flush=True)
    if not ok:
        FAILED.append(name)


def make(root, noise):
    """조건마다 잡음 크기가 다른 예측을 만든다. 잡음이 작을수록 r이 높다."""
    rng = np.random.default_rng(0)
    vid = np.arange(1000, 1072)
    y = rng.random((72, 34))
    for cond, short in G.CONDS.items():
        for q in G.PIDS:
            d = Path(root) / cond / "seed0" / q
            d.mkdir(parents=True)
            p = np.clip(y + rng.normal(0, noise[short], y.shape), 0.001, 0.999)
            order = rng.permutation(72)  # 저장 순서를 섞어도 영상 번호로 맞추는지
            done = dict(condition=cond, participant=q, settings=dict(hk_plan="final_for_mc"))
            if short in ("D-3", "D-4"):
                done["pred_file"] = "test_pred_final.npz"
                np.savez(d / "test_pred_final.npz", video_id=vid[order], p=p[order])
            else:
                done["chosen_input_wd"] = 100.0
                np.savez(d / "test_pred_wd100.npz", video_id=vid[order], p=p[order])
            np.savez(d / "scoring.npz", video_id=vid[order], y=y[order])
            (d / "done.json").write_text(json.dumps(done))


with tempfile.TemporaryDirectory() as tmp:
    make(tmp, {"A-1": 0.2, "C-1": 0.15, "D-3": 0.6, "D-4": 0.2})
    G.run(tmp, Path(tmp) / "out", n_boot=200)
    import pandas as pd
    d = pd.read_csv(Path(tmp) / "out" / "differences.tsv", sep="\t", dtype={"set": str}).set_index(["comparison", "set"])
    check("잡음이 큰 D-3은 A-1보다 낮다고 판정", d.loc[("D-3 - A-1", "34"), "verdict"] == "A-1보다 낮다")
    check("잡음이 같은 D-4는 A-1과 구별되지 않는다", d.loc[("D-4 - A-1", "34"), "verdict"] == "A-1과 구별되지 않는다")
    check("구간이 평균 차이를 감싼다", (d.ci_low <= d.mean_diff).all() and (d.mean_diff <= d.ci_high).all())
    s = pd.read_csv(Path(tmp) / "out" / "scores.tsv", sep="\t", dtype={"set": str})
    check("27개판 점수가 있다", set(s.set.astype(str)) == {"34", "27"})

with tempfile.TemporaryDirectory() as tmp:
    make(tmp, {"A-1": 0.2, "C-1": 0.2, "D-3": 0.2, "D-4": 0.2})
    bad = Path(tmp) / "brain_features_only" / "seed0" / "mc-03" / "scoring.npz"
    z = dict(np.load(bad))
    z["y"] = z["y"] + 0.01
    np.savez(bad, **z)
    try:
        G.run(tmp, Path(tmp) / "out", n_boot=10)
        check("사람 평정이 다른 조건은 멈춘다", False)
    except SystemExit:
        check("사람 평정이 다른 조건은 멈춘다", True)

print(f"통과 {4 + 1 - len(FAILED)} 실패 {len(FAILED)} {FAILED}")
sys.exit(1 if FAILED else 0)
