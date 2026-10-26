#!/usr/bin/env python3
"""Horikawa 주 데이터의 평가 분할 (2026-10-22, split_id = horikawa_rungroup6_v1).

규칙
  - 나누는 단위는 영상이 아니라 run 이다. 같은 run 의 영상은 모두 같은 fold 에 들어간다
    (이웃 블록의 혈류 반응이 겹쳐 학습·평가가 섞이는 것을 막기 위함).
  - 같은 내용 영상 쌍(content_id 가 같은 두 영상)이 들어 있는 run 들은 하나로 묶어 같은 fold 에 둔다.
  - 묶음(연결 성분)을 6개 fold 에 분석 영상 수가 고르도록 배정한다 (큰 묶음부터, 영상이 가장 적은 fold 로). 라벨은 쓰지 않는다.
  - 5명 모두 같은 61개 run(같은 영상 묶음)을 같은 순서로 봤으므로 한 분할을 모든 피험자에게 쓴다 (평가 영상이 피험자 간에 같다).
    run 은 사람 간 공통인 run_index(0~60, 시간 순서)로 정의한다. 세션 경계(ses/run 이름)는 사람마다 달라 쓰지 않는다
    (예: run_index 6 = sub-01 ses-02 run-01 = sub-02 ses-01 run-07).
  - 안쪽 분할(설정 고르기)은 바깥 학습 fold 5개를 그대로 5겹으로 쓴다 (원 논문의 바깥 6 / 안쪽 5).
출력: /storage/bigdata/EmoBrain_response/splits/horikawa_rungroup6_v1.tsv, .json
"""
import json
from pathlib import Path

import pandas as pd

R = Path("/storage/bigdata/Horikawa/response_t1w")
OUT = Path("/storage/bigdata/EmoBrain_response/splits")
SPLIT_ID = "horikawa_rungroup6_v1"
K = 6


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # 피험자 간 제시 구성이 같은지 확인
    cols = ["video_id", "content_id", "run_index", "onset_sec", "exclude_duplicate"]
    tabs = {s: pd.read_csv(R / f"sub-{s}/v3/sub-{s}_samples.tsv", sep="\t")[cols] for s in ["01", "02", "03", "04", "05"]}
    for s, t in tabs.items():
        assert t.reset_index(drop=True).equals(tabs["01"].reset_index(drop=True)), f"sub-{s} 제시 구성이 sub-01 과 다름"
    T = tabs["01"].copy()
    assert T.video_id.is_unique, "같은 영상 번호가 두 번 제시됨"

    # run 묶기: 같은 내용 쌍이 다른 run 에 있으면 합친다 (union-find)
    parent = {r: r for r in T.run_index.unique()}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for c, g in T.groupby("content_id"):
        rs = g.run_index.unique()
        for r in rs[1:]:
            parent[find(r)] = find(rs[0])
    T["run_group"] = T.run_index.map(find)
    sizes = T[~T.exclude_duplicate.astype(bool)].groupby("run_group").size().sort_values(ascending=False)
    sizes = sizes.reindex(sorted(sizes.index, key=lambda g: (-sizes[g], g)))   # 크기 순, 같으면 번호 순 (재현 가능)
    load = [0] * K; fold_of = {}
    for g, n in sizes.items():
        f = min(range(K), key=lambda k: (load[k], k)); fold_of[g] = f; load[f] += n
    T["fold"] = T.run_group.map(fold_of)
    T["analysis_row"] = ~T.exclude_duplicate.astype(bool)
    T["split_id"] = SPLIT_ID
    T = T[["split_id", "video_id", "content_id", "run_index", "run_group", "fold", "exclude_duplicate", "analysis_row"]]
    T.to_csv(OUT / f"{SPLIT_ID}.tsv", sep="\t", index=False)

    # 검증
    assert T.groupby("run_index").fold.nunique().max() == 1, "한 run 이 두 fold 에 걸침"
    assert T.groupby("content_id").fold.nunique().max() == 1, "같은 내용 쌍이 다른 fold 에 있음"
    A = T[T.analysis_row]
    summ = {"split_id": SPLIT_ID, "dataset": "Horikawa (주 데이터)", "피험자": ["01", "02", "03", "04", "05"],
            "분할_단위": "run (같은 내용 쌍이 든 run 은 묶음)", "바깥_fold_수": K, "안쪽": "바깥 학습 fold 5개를 그대로 5겹",
            "run_수": int(T.run_index.nunique()), "run_묶음_수": int(T.run_group.nunique()),
            "합쳐진_run_묶음": {int(g): sorted(int(r) for r in T[T.run_group == g].run_index.unique())
                            for g in T.run_group.unique() if T[T.run_group == g].run_index.nunique() > 1},
            "fold별_분석영상수": {int(k): int(v) for k, v in A.groupby("fold").size().items()},
            "fold별_run수": {int(k): int(v) for k, v in T.groupby("fold").run_index.nunique().items()},
            "fold별_run_index": {int(k): sorted(int(x) for x in v.unique()) for k, v in T.groupby("fold").run_index},
            "분석영상_총수": int(len(A)), "전체영상_총수": int(len(T)),
            "생성코드": "/storage/bigdata/EmoBrain_response/code/splits/make_horikawa_split.py"}
    (OUT / f"{SPLIT_ID}.json").write_text(json.dumps(summ, ensure_ascii=False, indent=1))
    print(json.dumps(summ, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
