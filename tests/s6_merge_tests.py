#!/usr/bin/env python3
"""scripts/s6_merge_lr.py 합성 시험 (2026-11-14). GPU와 실제 결과를 쓰지 않는다. 결과 폴더는 임시 폴더에 만든다.
시험: 검증 r이 높은 실행을 고름, 같으면 작은 learning rate, 두 번째 실행의 0 후보는 그 실행의 0이 아닌 최고 후보로 바꿈,
본 실행의 0 후보(A-1)는 그대로 인정, C-2는 합친 C-1의 실행을 따름, symlink가 원래 폴더를 가리킴, 다시 돌려도 같음, model.pt 여부 기록.
11/15 D, E: D-2는 합친 D-1의 실행을 따름, 짝 학습(D-4)은 선택표의 네 짝 평균으로 비교, A~C를 합친 폴더에 더해도 A~C 기록은 그대로.
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
SCRIPT = Path(os.environ.get("S6_MERGE_SCRIPT", REPO / "scripts" / "s6_merge_lr.py"))


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


def put_paired(root, cond, cid, val, lr, model=True):
    """짝 학습(D-4) 후보 하나. 후보 폴더에는 done.json이 없고 pair 넷과 ensemble만 있다. 검증 r은 selected.json의 선택표(rows)에만 있다."""
    f = root / "outer_fold1" / cond / f"{cid}_seed0"
    for j in (3, 4, 5, 6):
        (f / f"pair{j}").mkdir(parents=True)
        (f / f"pair{j}" / "done.json").write_text(json.dumps(dict(val_score=val + 0.01 * (j - 4.5), candidate=cand(lr), held_fold=j)))
        if model:
            (f / f"pair{j}" / "model.pt").write_text("")
    (f / "ensemble").mkdir()
    (f / "ensemble" / "done.json").write_text(json.dumps(dict(pairs=[])))
    (f / "ensemble" / "test_pred.npz").write_text("")
    rel = f"{cond}/{cid}_seed0"
    (root / "outer_fold1" / cond / "selected.json").write_text(json.dumps(dict(run_key=root.name, candidate=cand(lr), seeds={"0": rel}, zero_selected=False, rows=[dict(candidate_id=cid, val_score=val), dict(candidate_id="other", val_score=val - 0.05)])))
    return rel


def build_de(main, second):
    """A~C를 합친 뒤 더하는 D, E. build()가 만든 두 실행에 더한다."""
    a_main = "brain_only/a1main_seed0"
    # D-1: 두 번째 실행이 높다. D-2는 본 실행 D-2가 더 높아도 두 번째 실행의 것을 따른다
    select(main, "brain_decoded_sep", put(main, "brain_decoded_sep", "d1m", 0.30, 1e-3, model=True, lam=1.0, rank=4))
    select(second, "brain_decoded_sep", put(second, "brain_decoded_sep", "d1s", 0.32, 1e-4, model=True, lam=0.1, rank=2))
    select(main, "brain_decoded_sep_distill", put(main, "brain_decoded_sep_distill", "d2m", 0.45, 1e-3, lam=1.0, rank=4, alpha=0.25))
    put(second, "brain_decoded_sep_distill", "d2s", 0.31, 1e-4, lam=0.1, rank=2, alpha=0.5)
    select(second, "brain_decoded_sep_distill", "brain_decoded_sep/d1s_seed0", zero=True)  # α = 0이 골림: 그 실행의 D-1 모델 그대로
    # D-3: 본 실행이 높다
    select(main, "brain_features_only", put(main, "brain_features_only", "d3m", 0.28, 1e-3, rank=2))
    select(second, "brain_features_only", put(second, "brain_features_only", "d3s", 0.27, 1e-4, rank=1))
    # D-4(짝 학습): 두 번째 실행의 네 짝 평균이 높다. 짝마다의 값(0.29 ± 0.015)이 아니라 선택표의 평균으로 비교한다
    put_paired(main, "brain_frozen_feature_encoder", "d4m", 0.26, 1e-3)
    put_paired(second, "brain_frozen_feature_encoder", "d4s", 0.29, 1e-4)
    # E-고정: 본 실행이 0 후보(A-1, 0.33)를 골랐다
    select(main, "brain_only_repr_frozen", a_main, zero=True)
    select(second, "brain_only_repr_frozen", put(second, "brain_only_repr_frozen", "efs", 0.31, 1e-4, lam=1.0))
    # E-학습: 두 번째 실행이 0 후보를 골랐다. 0이 아닌 최고 후보(0.34)가 본 실행(0.32)보다 높다
    select(main, "brain_only_repr_trained", put(main, "brain_only_repr_trained", "etm", 0.32, 1e-3, lam=1.0))
    put(second, "brain_only_repr_trained", "ets1", 0.34, 1e-4, lam=1.0)
    put(second, "brain_only_repr_trained", "ets2", 0.30, 1e-4, lam=0.1)
    select(second, "brain_only_repr_trained", "brain_only/a1sec_seed0", zero=True)


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


def run(main, second, out, *extra):
    return subprocess.run([sys.executable, str(SCRIPT), "--main", str(main), "--second", str(second), "--out", str(out), "--folds", "1", *extra], capture_output=True, text=True)


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
        (fo / "control_feature_shuffle" / "contm_seed0").unlink()
        (fo / "control_feature_shuffle" / "contm_seed0").symlink_to(m / "outer_fold1" / "control_feature_shuffle" / "contm_seed0")
        de_test(tmp, m, s, out)
    print("s6_merge_tests 통과")


def de_test(tmp, m, s, out):
    fo = out / "outer_fold1"
    before = pd.read_csv(out / "merge_record.tsv", sep="\t")
    # D, E 선택이 없는 실행으로 DE를 합치면 멈춘다
    p0 = run(m, s, tmp / "merged_empty", "--conditions", "DE")
    assert p0.returncode != 0
    build_de(m, s)
    p = run(m, s, out, "--conditions", "DE")
    assert p.returncode == 0, p.stderr
    sel = {c: json.loads((fo / c / "selected.json").read_text()) for c in os.listdir(fo) if (fo / c / "selected.json").exists()}
    expect = dict(brain_decoded_sep=("second", "d1s"), brain_decoded_sep_distill=("second", "d1s"), brain_features_only=("main", "d3m"),
                  brain_frozen_feature_encoder=("second", "d4s"), brain_only_repr_frozen=("main", "a1main"), brain_only_repr_trained=("second", "ets1"))
    for cond, (src, cid) in expect.items():
        got = sel[cond]
        assert got["source_run"] == src, (cond, got["source_run"])
        target = (fo / got["seeds"]["0"]).resolve()
        assert target.name == f"{cid}_seed0", (cond, target)
        assert target.parent.parent.parent.name == ("main" if src == "main" else "second"), (cond, target)
    assert sel["brain_only_repr_frozen"]["zero_selected"] and sel["brain_only_repr_frozen"]["seeds"]["0"].startswith("brain_only/")
    assert sel["brain_decoded_sep_distill"]["zero_selected"] and sel["brain_decoded_sep_distill"]["seeds"]["0"] == "brain_decoded_sep/d1s_seed0"
    assert abs(sel["brain_frozen_feature_encoder"]["val_score"] - 0.29) < 1e-9
    assert (fo / sel["brain_frozen_feature_encoder"]["seeds"]["0"] / "ensemble" / "test_pred.npz").exists()
    rec = pd.read_csv(out / "merge_record.tsv", sep="\t")
    ac = rec[rec.condition.isin(before.condition)].reset_index(drop=True)
    assert ac.equals(before), "A~C 기록이 바뀌었다"
    de = rec[~rec.condition.isin(before.condition)].set_index("condition")
    assert set(de.index) == set(expect), set(de.index)
    assert abs(de.loc["brain_frozen_feature_encoder", "main_val"] - 0.26) < 1e-9 and bool(de.loc["brain_frozen_feature_encoder", "has_model"])
    assert abs(de.loc["brain_only_repr_trained", "second_val"] - 0.34) < 1e-9
    # 다시 돌려도 같은 결과, 기록 행 수도 같다
    p2 = run(m, s, out, "--conditions", "DE")
    assert p2.returncode == 0, p2.stderr
    assert len(pd.read_csv(out / "merge_record.tsv", sep="\t")) == len(rec)
    # AC를 다시 돌려도 D, E 기록을 지우지 않는다
    p4 = run(m, s, out)
    assert p4.returncode == 0, p4.stderr
    assert set(pd.read_csv(out / "merge_record.tsv", sep="\t").condition) == set(rec.condition)
    # 고른 후보의 행이 선택표에 없으면 멈춘다
    sj = s / "outer_fold1" / "brain_frozen_feature_encoder" / "selected.json"
    d = json.loads(sj.read_text())
    d["rows"] = [r for r in d["rows"] if r["candidate_id"] != "d4s"]
    sj.write_text(json.dumps(d))
    p3 = run(m, s, tmp / "merged_bad", "--conditions", "DE")
    assert p3.returncode != 0 and "검증 r을 찾지 못했다" in p3.stderr, p3.stderr
    sj.write_text(json.dumps(dict(d, rows=d["rows"] + [dict(candidate_id="d4s", val_score=0.29)])))
    # 한 실행에만 선택이 있으면 비교 없이 고르지 않고 missing으로 남긴다. 따라가는 조건도 합치지 않는다
    gone = m / "outer_fold1" / "brain_decoded_sep" / "selected.json"
    gone.rename(gone.with_suffix(".bak"))
    p5 = run(m, s, tmp / "merged_missing", "--conditions", "DE")
    assert p5.returncode == 0 and "합치지 않음 fold 1 brain_decoded_sep" in p5.stderr, p5.stderr
    fm = tmp / "merged_missing" / "outer_fold1"
    assert not (fm / "brain_decoded_sep" / "selected.json").exists() and not (fm / "brain_decoded_sep_distill" / "selected.json").exists()
    rm = pd.read_csv(tmp / "merged_missing" / "merge_record.tsv", sep="\t").set_index("condition")
    assert rm.loc["brain_decoded_sep", "chosen"] == "missing" and rm.loc["brain_decoded_sep_distill", "chosen"] == "missing"
    assert (fm / "brain_features_only" / "selected.json").exists()
    gone.with_suffix(".bak").rename(gone)
    # 따라가는 조건의 0 후보가 합친 앞 조건과 다른 후보를 가리키면 멈춘다
    sd = s / "outer_fold1" / "brain_decoded_sep_distill" / "selected.json"
    other = put(s, "brain_decoded_sep", "d1s2", 0.20, 1e-4, lam=1.0, rank=8)  # 그 실행이 고르지 않은 D-1 후보
    sd.write_text(json.dumps(dict(json.loads(sd.read_text()), seeds={"0": other})))
    p6 = run(m, s, tmp / "merged_zero_bad", "--conditions", "DE")
    assert p6.returncode != 0 and "다른 후보를 가리킨다" in p6.stderr, p6.stderr


if __name__ == "__main__":
    main_test()
