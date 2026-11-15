#!/usr/bin/env python3
"""S6 두 실행(learning rate 1e-3 본 실행과 1e-4 실행)을 조건과 fold마다 검증 r로 합친다 (01 7-L, 11/14 석진 님). GPU 없음.

규칙
- A-1(brain_only): 본 실행 그대로. 본 실행의 A-1 grid가 이미 learning rate {1e-5, 1e-4, 1e-3}을 모두 포함했다.
- 따라가는 조건: C-2(brain_decoded_distill)는 합친 C-1을 고른 실행의 C-2를, D-2(brain_decoded_sep_distill)는 합친 D-1을 고른 실행의 D-2를 쓴다
  (G9. distillation 조건은 앞 조건의 λ, r을 따르고 α만 고른다).
- 나머지 조건: 두 실행이 각자 고른 후보(selected.json)의 검증 r을 비교해 높은 쪽. 같으면 작은 learning rate(O6).
  한 실행에만 선택이 있으면 비교하지 않고 그 조건을 합치지 않는다(merge_record에 missing으로 남김). 나중에 빠진 쪽이 끝나면 다시 돌린다.
  두 번째 실행에서 0 후보(그 실행의 A-1, G10)가 골렸으면 그 실행의 0이 아닌 후보 가운데 가장 높은 것을 쓴다. 0 후보는 고른 A-1(본 실행)만 인정한다.
  따라가는 조건의 0 후보(α = 0)는 같은 실행의 앞 조건 모델이다(ex) C-2의 0 = 그 실행이 고른 C-1). 합친 폴더의 앞 조건이 같은 후보를 가리킬 때만 인정한다.
- 검증 r은 후보 폴더의 done.json(val_score)에서 읽는다. 짝 학습(D-4)은 후보 폴더에 done.json이 없으므로 selected.json의 선택표에 적힌 네 짝 평균을 읽는다.
- --conditions AC(기본)는 A~C, DE는 D, E를 합친다. 이미 만든 폴더에 더할 수 있고, merge_record.tsv는 이번에 합친 조건의 행만 바꾼다.
- 결과 폴더는 원래 결과를 옮기지 않고 symlink로 만든다. 조건마다 selected.json(고른 후보, 출처 실행, 비교한 값)과 merge_record.tsv를 남긴다.
- 학습한 결과만 읽고 시험 fold의 정답은 읽지 않는다. 고르는 값은 검증 r뿐이다.
사용: python scripts/s6_merge_lr.py --main <본 실행 폴더> --second <1e-4 실행 폴더> --out <합친 폴더> [--folds 1-6] [--conditions AC|DE]
"""
import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd

GROUPS = dict(
    AC=dict(merged=("brain_only_distill", "control_label_smoothing", "control_stimulus_shuffle", "brain_only_featdec", "control_feature_shuffle", "brain_decoded", "brain_decoded_additive"),
            follow={"brain_decoded_distill": "brain_decoded"}),
    DE=dict(merged=("brain_decoded_sep", "brain_features_only", "brain_frozen_feature_encoder", "brain_only_repr_frozen", "brain_only_repr_trained"),
            follow={"brain_decoded_sep_distill": "brain_decoded_sep"}),
)
MERGED = GROUPS["AC"]["merged"]  # 이전 이름(시험과 다른 스크립트가 읽는다)


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
    done_path = Path(root) / f"outer_fold{k}" / rel / "done.json"
    done = json.loads(done_path.read_text()) if done_path.exists() else {}
    if done.get("val_score") is not None:
        return dict(val=float(done["val_score"]), lr=float(done["candidate"]["lr"]), rel=rel, cand=done["candidate"], run_key=sel["run_key"], zero=bool(sel["zero_selected"]))
    # 짝 학습(D-4): 후보 폴더에는 짝마다의 done.json만 있다. 선택표에서 고른 후보의 행(네 짝 평균)을 읽는다
    cid = Path(rel).name.rsplit("_seed", 1)[0]
    rows = [r for r in sel.get("rows", []) if r.get("candidate_id") == cid]
    if len(rows) != 1 or rows[0].get("val_score") is None:
        raise SystemExit(f"fold {k} {cond}: 고른 후보 {cid}의 검증 r을 찾지 못했다")
    return dict(val=float(rows[0]["val_score"]), lr=float(sel["candidate"]["lr"]), rel=rel, cand=sel["candidate"], run_key=sel["run_key"], zero=bool(sel["zero_selected"]))


def best_nonzero(root, k, cond):
    """0 후보가 골렸을 때 그 실행의 0이 아닌 후보 가운데 검증 r이 가장 높은 것."""
    rows = []
    for f in (Path(root) / f"outer_fold{k}" / cond).glob("*_seed0/done.json"):
        d = json.loads(f.read_text())
        if not d.get("diverged") and d.get("val_score") is not None:
            rows.append(dict(val=float(d["val_score"]), lr=float(d["candidate"]["lr"]), rel=f"{cond}/{f.parent.name}", cand=d["candidate"], run_key=d["run_key"], zero=False))
    return max(rows, key=lambda r: (r["val"], -r["lr"])) if rows else None


def has_model(root, k, r):
    """S9(바꿔 끼우기, 흐트러뜨리기)는 model.pt와 outputs가 있는 후보만 읽는다. 짝 학습은 네 짝의 model.pt와 평균 예측(ensemble)이 있어야 한다."""
    p = Path(root) / f"outer_fold{k}" / r["rel"]
    pairs = sorted(p.glob("pair*"))
    if pairs:
        return all((q / "model.pt").exists() for q in pairs) and (p / "ensemble" / "done.json").exists()
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
    ap.add_argument("--conditions", default="AC", choices=sorted(GROUPS))
    a = ap.parse_args()
    main_root, second_root, out = Path(a.main).resolve(), Path(a.second).resolve(), Path(a.out)
    group = GROUPS[a.conditions]
    record, missing = [], []
    for k in folds_of(a.folds):
        fo = out / f"outer_fold{k}"
        link(main_root / f"outer_fold{k}" / "plan", fo / "plan")
        link(main_root / f"outer_fold{k}" / "brain_only", fo / "brain_only")
        pick = {}
        for cond in group["merged"]:
            m, s = chosen(main_root, k, cond), chosen(second_root, k, cond)
            if s is not None and s["zero"]:
                s = best_nonzero(second_root, k, cond)
            options = [(r, root, name) for r, root, name in ((m, main_root, "main"), (s, second_root, "second")) if r is not None]
            if not options:
                raise SystemExit(f"fold {k} {cond}: 두 실행 모두 고른 후보가 없다")
            if len(options) == 1:  # 한쪽 실행이 끝나지 않았다. 비교 없이 고르지 않는다
                missing.append((k, cond, "main" if m is None else "second"))
                record.append(dict(fold=k, condition=cond, main_val=m["val"] if m else None, main_lr=m["lr"] if m else None, second_val=s["val"] if s else None, second_lr=s["lr"] if s else None, chosen="missing", chosen_lr=None, chosen_val=None, has_model=False, candidate=None))
                continue
            r, root, name = max(options, key=lambda t: (t[0]["val"], -t[0]["lr"]))
            pick[cond] = name
            write(fo, cond, root, r, name)
            record.append(dict(fold=k, condition=cond, main_val=m["val"] if m else None, main_lr=m["lr"] if m else None, second_val=s["val"] if s else None, second_lr=s["lr"] if s else None, chosen=name, chosen_lr=r["lr"], chosen_val=r["val"], has_model=has_model(root, k, r), candidate=json.dumps(r["cand"], sort_keys=True)))
        for cond, lead in group["follow"].items():
            if lead not in pick:
                missing.append((k, cond, f"{lead}를 합치지 못함"))
                record.append(dict(fold=k, condition=cond, main_val=None, main_lr=None, second_val=None, second_lr=None, chosen="missing", chosen_lr=None, chosen_val=None, has_model=False, candidate=None))
                continue
            lead_root = main_root if pick[lead] == "main" else second_root
            r = chosen(lead_root, k, cond)
            if r is None:
                raise SystemExit(f"fold {k}: 고른 {lead}와 같은 실행에 {cond} 선택이 없다")
            write(fo, cond, lead_root, r, pick[lead], zero_from=("brain_only", lead))
            record.append(dict(fold=k, condition=cond, main_val=None, main_lr=None, second_val=None, second_lr=None, chosen=pick[lead], chosen_lr=r["lr"], chosen_val=r["val"], has_model=has_model(lead_root, k, r), candidate=json.dumps(r["cand"], sort_keys=True)))
    new = pd.DataFrame(record)
    path = out / "merge_record.tsv"
    if path.exists():  # 이미 합친 다른 조건의 행은 두고 이번 조건의 행만 바꾼다
        old = pd.read_csv(path, sep="\t")
        new = pd.concat([old[~old.condition.isin(new.condition.unique())], new], ignore_index=True)
    new.to_csv(path, sep="\t", index=False)
    print(pd.DataFrame(record).groupby("condition").chosen.value_counts().to_string())
    for k, cond, why in missing:
        print(f"합치지 않음 fold {k} {cond}: {why} 선택 없음", file=sys.stderr)


def write(fo, cond, root, r, name, zero_from=("brain_only",)):
    """합친 폴더의 조건 폴더. 고른 후보 폴더를 symlink로 두고 selected.json을 쓴다.
    0 후보면 이미 연결한 A-1 폴더(따라가는 조건은 앞 조건 폴더)를 가리키고, 합친 폴더의 그 경로가 원래 실행의 같은 후보인지 확인한다."""
    folder = fo / cond
    folder.mkdir(parents=True, exist_ok=True)
    target = Path(root) / fo.name / r["rel"]
    rel = r["rel"]
    if r["zero"]:  # 0 후보는 고른 A-1 모델(G10), 따라가는 조건은 같은 실행이 고른 앞 조건 모델이다
        if rel.split("/", 1)[0] not in zero_from:
            raise SystemExit(f"{fo.name} {cond}: 0 후보가 {' 또는 '.join(zero_from)}가 아니다({rel})")
        if not (fo / rel).exists() or (fo / rel).resolve() != target.resolve():
            raise SystemExit(f"{fo.name} {cond}: 0 후보 {rel}가 합친 폴더에서 다른 후보를 가리킨다")
    else:
        link(target, folder / Path(rel).name)
        rel = f"{cond}/{Path(rel).name}"
    sel = dict(condition=cond, candidate=r["cand"], seeds={"0": rel}, zero_selected=r["zero"], source_run=name, source_root=str(root), run_key=r["run_key"], val_score=r["val"])
    (folder / "selected.json").write_text(json.dumps(sel, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
