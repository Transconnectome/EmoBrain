#!/usr/bin/env python3
"""S6 두 실행(learning rate 1e-3 본 실행과 1e-4 실행)을 조건과 fold마다 검증 r로 합친다 (01 7-L, 11/14 석진 님). GPU 없음.

규칙
- A-1(brain_only): 본 실행 그대로. 본 실행의 A-1 grid가 이미 learning rate {1e-5, 1e-4, 1e-3}을 모두 포함했다.
- C-2(brain_decoded_distill): 합친 C-1을 고른 실행의 C-2를 쓴다(G9. C-2는 C-1의 λ, r을 따르고 α만 고른다).
- 나머지 조건: 두 실행이 각자 고른 후보(selected.json)의 검증 r을 비교해 높은 쪽. 같으면 작은 learning rate(O6).
  두 번째 실행에서 0 후보(그 실행의 A-1, G10)가 골렸으면 그 실행의 0이 아닌 후보 가운데 가장 높은 것을 쓴다. 0 후보는 고른 A-1(본 실행)만 인정한다.
- 결과 폴더는 원래 결과를 옮기지 않고 symlink로 만든다. 조건마다 selected.json(고른 후보, 출처 실행, 비교한 값)과 merge_record.tsv를 남긴다.
- 학습한 결과만 읽고 시험 fold의 정답은 읽지 않는다. 고르는 값은 검증 r(done.json의 val_score)뿐이다.
사용: python scripts/s6_merge_lr.py --main <본 실행 폴더> --second <1e-4 실행 폴더> --out <합친 폴더> [--folds 1-6]
"""
import argparse
import json
import os
from pathlib import Path

import pandas as pd

MERGED = ("brain_only_distill", "control_label_smoothing", "control_stimulus_shuffle", "brain_only_featdec", "control_feature_shuffle", "brain_decoded", "brain_decoded_additive")


def folds_of(spec):
    a, _, b = spec.partition("-")
    return list(range(int(a), int(b or a) + 1))


def chosen(root, k, cond):
    """그 실행이 고른 후보. (검증 r, learning rate, 후보 폴더의 outer_fold 기준 상대 경로, 후보, run_key, 0 후보 여부). 없으면 None."""
    p = Path(root) / f"outer_fold{k}" / cond / "selected.json"
    if not p.exists():
        return None
    sel = json.loads(p.read_text())
    rel = sel["seeds"]["0"]
    done = json.loads((Path(root) / f"outer_fold{k}" / rel / "done.json").read_text())
    return dict(val=float(done["val_score"]), lr=float(done["candidate"]["lr"]), rel=rel, cand=done["candidate"], run_key=sel["run_key"], zero=bool(sel["zero_selected"]))


def best_nonzero(root, k, cond):
    """0 후보가 골렸을 때 그 실행의 0이 아닌 후보 가운데 검증 r이 가장 높은 것."""
    rows = []
    for f in (Path(root) / f"outer_fold{k}" / cond).glob("*_seed0/done.json"):
        d = json.loads(f.read_text())
        if not d.get("diverged") and d.get("val_score") is not None:
            rows.append(dict(val=float(d["val_score"]), lr=float(d["candidate"]["lr"]), rel=f"{cond}/{f.parent.name}", cand=d["candidate"], run_key=d["run_key"], zero=False))
    return max(rows, key=lambda r: (r["val"], -r["lr"])) if rows else None


def has_model(root, k, r):
    """S9(바꿔 끼우기, 흐트러뜨리기)는 model.pt와 outputs가 있는 후보만 읽는다. 시험 r은 test_pred.npz만 쓴다."""
    p = Path(root) / f"outer_fold{k}" / r["rel"]
    return (p / "model.pt").exists() and (p / "outputs" / "done.json").exists()


def link(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.is_symlink() or dst.exists():
        if dst.is_symlink() and os.readlink(dst) == str(src):
            return
        raise SystemExit(f"{dst}가 이미 있다. 지우고 다시 합친다")
    dst.symlink_to(src)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--main", required=True)
    ap.add_argument("--second", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--folds", default="1-6")
    a = ap.parse_args()
    main_root, second_root, out = Path(a.main).resolve(), Path(a.second).resolve(), Path(a.out)
    record = []
    for k in folds_of(a.folds):
        fo = out / f"outer_fold{k}"
        link(main_root / f"outer_fold{k}" / "plan", fo / "plan")
        link(main_root / f"outer_fold{k}" / "brain_only", fo / "brain_only")
        pick = {}
        for cond in MERGED:
            m, s = chosen(main_root, k, cond), chosen(second_root, k, cond)
            if s is not None and s["zero"]:
                s = best_nonzero(second_root, k, cond)
            options = [(r, root, name) for r, root, name in ((m, main_root, "main"), (s, second_root, "second")) if r is not None]
            if not options:
                raise SystemExit(f"fold {k} {cond}: 두 실행 모두 고른 후보가 없다")
            r, root, name = max(options, key=lambda t: (t[0]["val"], -t[0]["lr"]))
            pick[cond] = name
            write(fo, cond, root, r, name)
            record.append(dict(fold=k, condition=cond, main_val=m["val"] if m else None, main_lr=m["lr"] if m else None, second_val=s["val"] if s else None, second_lr=s["lr"] if s else None, chosen=name, chosen_lr=r["lr"], chosen_val=r["val"], has_model=has_model(root, k, r), candidate=json.dumps(r["cand"], sort_keys=True)))
        c1_root = main_root if pick["brain_decoded"] == "main" else second_root
        r = chosen(c1_root, k, "brain_decoded_distill")
        if r is None:
            raise SystemExit(f"fold {k}: 고른 C-1과 같은 실행에 C-2 선택이 없다")
        write(fo, "brain_decoded_distill", c1_root, r, pick["brain_decoded"])
        record.append(dict(fold=k, condition="brain_decoded_distill", main_val=None, main_lr=None, second_val=None, second_lr=None, chosen=pick["brain_decoded"], chosen_lr=r["lr"], chosen_val=r["val"], has_model=has_model(c1_root, k, r), candidate=json.dumps(r["cand"], sort_keys=True)))
    pd.DataFrame(record).to_csv(out / "merge_record.tsv", sep="\t", index=False)
    print(pd.DataFrame(record).groupby("condition").chosen.value_counts().to_string())


def write(fo, cond, root, r, name):
    """합친 폴더의 조건 폴더. 고른 후보 폴더를 symlink로 두고 selected.json을 쓴다. 0 후보면 A-1 폴더를 가리킨다."""
    folder = fo / cond
    folder.mkdir(parents=True, exist_ok=True)
    target = Path(root) / fo.name / r["rel"]
    rel = r["rel"]
    if r["zero"]:  # 0 후보는 고른 A-1 모델이다(G10). A-1 폴더는 이미 brain_only로 연결되어 있다
        if not rel.startswith("brain_only/"):
            raise SystemExit(f"{fo.name} {cond}: 0 후보가 A-1이 아니다")
    else:
        link(target, folder / Path(rel).name)
        rel = f"{cond}/{Path(rel).name}"
    sel = dict(condition=cond, candidate=r["cand"], seeds={"0": rel}, zero_selected=r["zero"], source_run=name, source_root=str(root), run_key=r["run_key"], val_score=r["val"])
    (folder / "selected.json").write_text(json.dumps(sel, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
