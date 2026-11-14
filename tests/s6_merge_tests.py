#!/usr/bin/env python3
"""scripts/s6_merge_lr.py 합성 시험 (2026-11-14). GPU와 실제 결과를 쓰지 않는다. 결과 폴더는 임시 폴더에 만든다.
시험: 검증 r이 높은 실행을 고름, 같으면 작은 learning rate, 두 번째 실행의 0 후보는 그 실행의 0이 아닌 최고 후보로 바꿈,
본 실행의 0 후보(A-1)는 그대로 인정, C-2는 합친 C-1의 실행을 따름, symlink가 원래 폴더를 가리킴, 다시 돌려도 같음, model.pt 여부 기록.
사용: s6_merge_tests.py
"""
import sys as _sys
_sys.dont_write_bytecode = True
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "s6_merge_lr.py"


def cand(lr, **kw):
    return dict(dict(d=64, input_wd=100.0, lr=lr, lam=None, alpha=None, rank=None, feature_wd=None), **kw)


def put(root, cond, cid, val, lr, model=False, **kw):
    """후보 폴더 하나(done.json, test_pred.npz 자리). model=True면 고른 모델처럼 model.pt와 outputs를 둔다."""
    f = root / "outer_fold1" / cond / f"{cid}_seed0"
    f.mkdir(parents=True)
    (f / "done.json").write_text(json.dumps(dict(val_score=val, candidate=cand(lr, **kw), run_key=root.name, candidate_id=cid)))
    (f / "test_pred.npz").write_text("")
    if model:
        (f / "model.pt").write_text("")
        (f / "outputs").mkdir()
        (f / "outputs" / "done.json").write_text("{}")
    return f"{cond}/{cid}_seed0"


def select(root, cond, rel, zero=False):
    (root / "outer_fold1" / cond).mkdir(parents=True, exist_ok=True)
    (root / "outer_fold1" / cond / "selected.json").write_text(json.dumps(dict(run_key=root.name, seeds={"0": rel}, zero_selected=zero)))


def build(tmp):
    main, second = tmp / "main", tmp / "second"
    for r in (main, second):
        (r / "outer_fold1" / "plan").mkdir(parents=True)
    a_main = put(main, "brain_only", "a1main", 0.33, 1e-3, model=True)
    select(main, "brain_only", a_main)
    a_sec = put(second, "brain_only", "a1sec", 0.29, 1e-4, model=True)
    select(second, "brain_only", a_sec)
    # A-2: 두 번째 실행이 0 후보를 골랐다. 0이 아닌 최고 후보(0.28)와 본 실행(0.32)을 비교해 본 실행
    select(main, "brain_only_distill", put(main, "brain_only_distill", "a2m", 0.32, 1e-3, model=True, alpha=0.25))
    put(second, "brain_only_distill", "a2s1", 0.28, 1e-4, alpha=0.25)
    put(second, "brain_only_distill", "a2s2", 0.27, 1e-4, alpha=0.5)
    select(second, "brain_only_distill", a_sec, zero=True)
    # LS: 같은 값이면 작은 learning rate(두 번째 실행)
    select(main, "control_label_smoothing", put(main, "control_label_smoothing", "lsm", 0.31, 1e-3, model=True))
    select(second, "control_label_smoothing", put(second, "control_label_smoothing", "lss", 0.31, 1e-4, model=True))
    # B-1: 본 실행이 0 후보(A-1)를 골랐고 그 값이 더 높다
    select(main, "brain_only_featdec", a_main, zero=True)
    select(second, "brain_only_featdec", put(second, "brain_only_featdec", "b1s", 0.30, 1e-4, model=True))
    for cond, vm, vs in (("control_feature_shuffle", 0.30, 0.29), ("control_stimulus_shuffle", 0.30, 0.305), ("brain_decoded_additive", 0.31, 0.335)):
        select(main, cond, put(main, cond, cond[:4] + "m", vm, 1e-3, model=True))
        select(second, cond, put(second, cond, cond[:4] + "s", vs, 1e-4, model=True))
    # C-1: 두 번째 실행이 높다. C-2는 두 번째 실행의 것을 따른다(본 실행 C-2 값이 더 높아도)
    select(main, "brain_decoded", put(main, "brain_decoded", "c1m", 0.25, 1e-3, model=True, lam=1.0, rank=4))
    select(second, "brain_decoded", put(second, "brain_decoded", "c1s", 0.34, 1e-4, model=True, lam=0.1, rank=2))
    select(main, "brain_decoded_distill", put(main, "brain_decoded_distill", "c2m", 0.40, 1e-3, model=True, lam=1.0, rank=4, alpha=0.25))
    select(second, "brain_decoded_distill", put(second, "brain_decoded_distill", "c2s", 0.335, 1e-4, model=True, lam=0.1, rank=2, alpha=0.5))
    return main, second


def run(main, second, out):
    return subprocess.run([sys.executable, str(SCRIPT), "--main", str(main), "--second", str(second), "--out", str(out), "--folds", "1"], capture_output=True, text=True)


def main_test():
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        m, s = build(tmp)
        out = tmp / "merged"
        p = run(m, s, out)
        assert p.returncode == 0, p.stderr
        fo = out / "outer_fold1"
        sel = {c: json.loads((fo / c / "selected.json").read_text()) for c in os.listdir(fo) if (fo / c / "selected.json").exists()}
        expect = dict(brain_only_distill=("main", "a2m"), control_label_smoothing=("second", "lss"), brain_only_featdec=("main", "a1main"),
                      control_feature_shuffle=("main", "contm"), control_stimulus_shuffle=("second", "conts"), brain_decoded_additive=("second", "brais"),
                      brain_decoded=("second", "c1s"), brain_decoded_distill=("second", "c2s"))
        for cond, (src, cid) in expect.items():
            got = sel[cond]
            assert got["source_run"] == src, (cond, got["source_run"])
            target = (fo / got["seeds"]["0"]).resolve()
            assert target.name == f"{cid}_seed0", (cond, target)
            assert target.parent.parent.parent.name == ("main" if src == "main" else "second"), (cond, target)
            assert (fo / got["seeds"]["0"] / "test_pred.npz").exists(), cond
        assert sel["brain_only_featdec"]["zero_selected"] and sel["brain_only_featdec"]["seeds"]["0"].startswith("brain_only/")
        assert (fo / "brain_only").resolve() == (m / "outer_fold1" / "brain_only").resolve()
        assert (fo / "plan").resolve() == (m / "outer_fold1" / "plan").resolve()
        assert not (fo / "brain_only" / "selected.json").resolve().is_relative_to(s)
        rec = pd.read_csv(out / "merge_record.tsv", sep="\t").set_index("condition")
        assert abs(rec.loc["brain_only_distill", "second_val"] - 0.28) < 1e-9  # 0 후보 대신 0이 아닌 최고 후보
        assert bool(rec.loc["brain_decoded", "has_model"]) and bool(rec.loc["brain_decoded_distill", "has_model"])
        # 다시 돌려도 같은 결과로 멈추지 않는다
        p2 = run(m, s, out)
        assert p2.returncode == 0, p2.stderr
        # 다른 곳을 가리키는 symlink가 있으면 멈춘다
        (fo / "control_feature_shuffle" / "contm_seed0").unlink()
        (fo / "control_feature_shuffle" / "contm_seed0").symlink_to(tmp)
        p3 = run(m, s, out)
        assert p3.returncode != 0
    print("s6_merge_tests 통과")


if __name__ == "__main__":
    main_test()
