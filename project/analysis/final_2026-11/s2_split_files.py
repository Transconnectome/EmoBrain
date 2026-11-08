#!/usr/bin/env python3
"""S2 분할 목록 파일 (01 0-2, H2, O7, 2026-11-08).

분할의 원본은 manifests/s2/split_hk_dev.tsv(영상별 fold)와 fold_roles.tsv(fold별 역할) 두 표 하나뿐이다.
이 스크립트는 두 표에서 실행 단위별 영상 목록을 만든다. 손으로 고치지 않는다. 표가 바뀌면 다시 만든다.

출력: manifests/s2/splits/<실행 단위>/{train,val,test}.txt. 한 줄에 video_id 하나, 오름차순, 머리글 없음.
- outer_fold1 ~ outer_fold6: 바깥 fold k가 test, 다음 fold가 val(H2), 나머지 4개가 train
- final_for_mc: HK 최종 모델(O7). fold 1이 val, fold 2~6이 train, test.txt는 비어 있다
fold 번호는 split_hk_dev.tsv의 fold 열과 같은 1~6이다. 파일럿(pilot_fold<k>)은 outer_fold<k>의 train, val만 쓴다.

--check는 파일을 쓰지 않고 지금 파일이 두 표와 같은지만 본다. 다르면 0이 아닌 값으로 끝난다.
사용: s2_split_files.py [--check]
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

S2 = Path(__file__).resolve().parent / "manifests/s2"
SPLITS = S2 / "splits"
PARTS = ("train", "val", "test")


def folds_of(text):
    return [int(x) for x in str(text).split(",")] if str(text) not in ("", "nan") else []


def expected(split=None, roles=None):
    """실행 단위 -> {train, val, test: 정렬된 video_id 목록}. 두 표만으로 정한다."""
    split = pd.read_csv(S2 / "split_hk_dev.tsv", sep="\t") if split is None else split
    roles = pd.read_csv(S2 / "fold_roles.tsv", sep="\t") if roles is None else roles
    if not split.video_id.is_unique:
        raise ValueError("split_hk_dev.tsv에 같은 video_id가 두 번 있다")
    ids = lambda fs: sorted(int(v) for v in split.video_id[split.fold.isin(fs)])
    out = {}
    for row in roles.itertuples(index=False):
        if row.role == "outer":
            k = int(row.test_fold)
            out[f"outer_fold{k}"] = dict(train=ids(folds_of(row.train_folds)), val=ids([int(row.val_fold)]), test=ids([k]))
        elif row.role == "final_for_mc_O7":
            out["final_for_mc"] = dict(train=ids(folds_of(row.train_folds)), val=ids([int(row.val_fold)]), test=[])
        else:
            raise ValueError(f"fold_roles.tsv의 알 수 없는 역할: {row.role}")
    for name, sets in out.items():
        a, b, t = (set(sets[p]) for p in PARTS)
        if a & b or a & t or b & t:
            raise ValueError(f"{name}: train, val, test가 겹친다")
        if name.startswith("outer_fold") and len(a | b | t) != len(split):
            raise ValueError(f"{name}: 세 목록을 합쳐도 개발 영상 전체가 아니다")
    return out


def read_list(path):
    text = Path(path).read_text().split()
    return [int(x) for x in text]


def write(sets):
    for name, parts in sets.items():
        d = SPLITS / name
        d.mkdir(parents=True, exist_ok=True)
        for p in PARTS:
            (d / f"{p}.txt").write_text("".join(f"{v}\n" for v in parts[p]))


def check(sets):
    """파일과 표가 다른 곳을 돌려준다. 빈 목록이면 같다."""
    bad = []
    on_disk = {p.name for p in SPLITS.iterdir() if p.is_dir()} if SPLITS.exists() else set()
    if on_disk != set(sets):
        bad.append(f"실행 단위 폴더가 다르다(파일 {sorted(on_disk)}, 표 {sorted(sets)})")
    for name, parts in sets.items():
        for p in PARTS:
            f = SPLITS / name / f"{p}.txt"
            if not f.exists() or read_list(f) != parts[p]:
                bad.append(f"{name}/{p}.txt")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    sets = expected()
    if not a.check:
        write(sets)
    bad = check(sets)
    if bad:
        sys.exit("분할 목록 파일이 두 표와 다르다: " + ", ".join(bad))
    for name, parts in sets.items():
        print(name, *(f"{p} {len(parts[p])}" for p in PARTS))


if __name__ == "__main__":
    main()
