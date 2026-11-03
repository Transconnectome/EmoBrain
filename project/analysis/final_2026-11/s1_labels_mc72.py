#!/usr/bin/env python3
"""S1 실행 전 확인 가운데 두 가지 (04_claude_code_workorder.md S1, 2026-11-03).

1. 34개 라벨 열 대조(N2): 레포 정답 파일 project/shared/data/cowen_horikawa_labels.csv의 score_0~33은
   project/shared/data/cowen34_order.txt(알파벳 순)로 이름을 붙여 왔다. 원 범주 이름이 든 Horikawa 형식의 특징 파일
   (archive/.../dir3_ccn/data/raw/feature/category.mat, L.feat 2,196 × 34, L.featname)과 같은 이름의 열끼리 값을 비교한다.
   하나라도 다르면 오류로 멈춘다(04 S1: 어긋난 채로는 어떤 학습도 돌리지 않는다).
2. MC 최종 시험 영상 72개 목록과 그 중복(0절, B2, 6-3): MC 6명의 samples 표에서 part == test인 영상을 모은다(6명이 같아야 함).
   같은 내용의 영상은 prereg_v2/manifests/stimulus_crosswalk.tsv의 canonical_stimulus_id로 찾는다.
   HK 분석 영상(분할 파일의 analysis_row이고 exclude_duplicate가 아닌 행) 가운데 이 72개의 내용에 해당하는 영상 수와,
   그것을 뺀 개발 영상 수를 센다.
출력: project/analysis/final_2026-11/manifests/{label_map_34.tsv, mc_test72.tsv}와 표준 출력의 요약
사용: python s1_labels_mc72.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.io as sio

REPO = Path(__file__).resolve().parents[3]
PM = Path("/pscratch/sd/s/sjmoon")
OUT = Path(__file__).resolve().parent / "manifests"
LABELS = REPO / "project/shared/data/cowen_horikawa_labels.csv"
ORDER = REPO / "project/shared/data/cowen34_order.txt"
CATEGORY = REPO / "archive/v5_direction_split_20260628/dir3_ccn/data/raw/feature/category.mat"
CROSSWALK = REPO / "prereg_v2/manifests/stimulus_crosswalk.tsv"
SPLIT = REPO / "docs/reports/prelim_2026-10/splits/horikawa_rungroup6_v1.tsv"
MC_SUBJECTS = ["01", "02", "03", "04", "05", "06"]


def label_map():
    lab = pd.read_csv(LABELS).set_index("stim_num_int").sort_index()
    order = [x.strip() for x in ORDER.read_text().splitlines() if x.strip()]
    assert len(order) == 34 and list(lab.index) == list(range(1, 2186)), "정답 파일 형식이 예상과 다름"
    L = sio.loadmat(CATEGORY, squeeze_me=True, struct_as_record=False)["L"]
    feat = np.asarray(L.feat, float); names = [str(x) for x in np.atleast_1d(L.featname)]
    assert feat.shape == (2196, 34) and len(names) == 34
    rows = []
    for i, name in enumerate(order):
        key = name[0].upper() + name[1:].replace(" ", "_")
        if key not in names:
            raise SystemExit(f"오류: score_{i}의 이름 '{name}'이 category.mat에 없음")
        j = names.index(key)
        s = lab[f"score_{i}"].values.astype(float); m = feat[:2185, j]
        rows.append(dict(score_col=f"score_{i}", name=name, category_mat_col=j, category_mat_name=key,
                         max_abs_diff=float(np.abs(s - m).max()), n_nonzero=int((s > 0).sum())))
    T = pd.DataFrame(rows)
    bad = T[T.max_abs_diff > 1e-9]
    if len(bad):
        raise SystemExit(f"오류: 값이 다른 열 {len(bad)}개\n{bad.to_string(index=False)}")
    return T


def mc_test72():
    sets = []
    for s in MC_SUBJECTS:
        sm = pd.read_csv(PM / f"MindCaptioning/sub-{s}/v2_qc/sub-{s}_samples_qc_usable.tsv", sep="\t")
        sets.append(sorted(sm.loc[sm.part == "test", "video_id"].unique()))
    assert all(x == sets[0] for x in sets), "MC 참가자마다 시험 영상이 다름"
    test = sets[0]; assert len(test) == 72, len(test)
    cw = pd.read_csv(CROSSWALK, sep="\t", comment="#")
    canon = dict(zip(cw.video_number, cw.canonical_stimulus_id))
    by_canon = cw.groupby("canonical_stimulus_id").video_number.apply(sorted).to_dict()
    split = pd.read_csv(SPLIT, sep="\t"); ana = split[split.analysis_row & ~split.exclude_duplicate]
    ana_videos = set(ana.video_id)
    rows = []
    for v in test:
        c = canon[v]; same = by_canon[c]
        rows.append(dict(mc_video_id=v, canonical_stimulus_id=c, same_content_videos=",".join(map(str, same)),
                         hk_analysis_videos=",".join(str(x) for x in same if x in ana_videos)))
    T = pd.DataFrame(rows)
    excl = {int(x) for s in T.hk_analysis_videos for x in s.split(",") if x}
    dev = sorted(ana_videos - excl)
    return T, len(ana_videos), len(excl), len(dev)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    lm = label_map(); lm.to_csv(OUT / "label_map_34.tsv", sep="\t", index=False)
    print(f"[라벨] 34개 모두 category.mat의 같은 이름 열과 값이 같음(최대 차이 {lm.max_abs_diff.max():.1e})")
    T, n_ana, n_excl, n_dev = mc_test72(); T.to_csv(OUT / "mc_test72.tsv", sep="\t", index=False)
    multi = T[T.same_content_videos.str.contains(",")]
    print(f"[MC 72개] 6명 모두 같은 72개. 같은 내용 영상이 둘 이상인 시험 영상 {len(multi)}개: "
          + "; ".join(f"{r.mc_video_id} -> {r.same_content_videos}" for r in multi.itertuples()))
    print(f"[영상 집합] HK 분석 영상 {n_ana}개, 그중 MC 72개의 내용에 해당 {n_excl}개, 개발 영상 {n_dev}개")
    no_hk = T[T.hk_analysis_videos == ""]
    if len(no_hk):
        print("  HK 분석 영상에 없는 MC 시험 영상:", list(no_hk.mc_video_id))


if __name__ == "__main__":
    main()
