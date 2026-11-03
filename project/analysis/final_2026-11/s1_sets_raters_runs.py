#!/usr/bin/env python3
"""S1 실행 전 확인 가운데 지도와 관계없는 네 가지 (04_claude_code_workorder.md S1, 2026-11-03).

1. 중복 15개의 구성(B2): 분할 파일에서 같은 content_id가 둘인 파일 쌍마다 어느 쪽이 먼저 제시되었고 어느 쪽을 남겼는지.
   제시 순서는 run_index(전체 run 순서), 같은 run이면 events_audited.tsv의 stimulus_index_in_run.
   거의 같은 내용 쌍 1349, 1363(B2: 둘 다 남기고 같은 fold로 묶음)도 함께 적는다.
2. 평정자 수 역산(B8): 영상마다 34개 비율 p에 대해 p × n이 모두 정수에 가까운(차이 2e-3 이하) 가장 작은 n(1~60).
   값이 다섯 자리로 저장되어 있어 허용 오차를 둔다. 역산한 n은 가중치나 신뢰도 계산에 쓰지 않는다.
   n이 17을 넘는 영상 목록과 중복 영상의 겹침을 센다.
3. MC run 구성(6-3, O29): MC 6명의 QC 전 samples 표에서 학습 세션 run을 run_index 순서로 적고,
   시험 영상(test_video_in_train_session)이 든 run, 입력층 학습 자료(나머지 run의 학습 블록)의 수를 센다. QC 뒤 남은 수도 함께.
4. 8초 반복의 종료 시점(3-2): events_audited.tsv(5명)의 블록 길이와 stimuli.tsv의 영상 길이를 비교한다.
   블록 길이는 TR(2초) 단위이고 "영상 제시 + 뒤따르는 2초 휴지"다(PREPROCESSING_FINAL.md 2.3절).
출력: manifests/{duplicates_15.tsv, rater_count_inferred.tsv, mc_train_runs.tsv, presentation_length.tsv}와 표준 출력 요약
사용: python s1_sets_raters_runs.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[3]
PM = Path("/pscratch/sd/s/sjmoon")
OUT = Path(__file__).resolve().parent / "manifests"
SPLIT = REPO / "docs/reports/prelim_2026-10/splits/horikawa_rungroup6_v1.tsv"
EVENTS = REPO / "prereg_v2/manifests/events_audited.tsv"
STIMULI = REPO / "prereg_v2/manifests/stimuli.tsv"
LABELS = REPO / "project/shared/data/cowen_horikawa_labels.csv"
HK = ["01", "02", "03", "04", "05"]
MC = ["01", "02", "03", "04", "05", "06"]
TOL, NMAX = 2e-3, 60


def duplicates():
    sp = pd.read_csv(SPLIT, sep="\t")
    ev = pd.read_csv(EVENTS, sep="\t", comment="#")
    ev = ev[(ev.participant_id == "sub-01") & ~ev.is_baseline.astype(bool)]
    order = ev.set_index(ev.stimulus_number.astype(int)).stimulus_index_in_run
    rows = []
    for cid, g in sp.groupby("content_id"):
        if len(g) < 2:
            continue
        g = g.assign(within=g.video_id.map(order)).sort_values(["run_index", "within"])
        first, later = g.iloc[0], g.iloc[1]
        kept = g[~g.exclude_duplicate.astype(bool)].video_id.tolist()
        rows.append(dict(content_id=cid, first_presented=int(first.video_id), later_presented=int(later.video_id),
                         run_index_first=int(first.run_index), run_index_later=int(later.run_index),
                         kept=",".join(map(str, kept)), kept_is_first=kept == [int(first.video_id)],
                         fold_kept=",".join(str(int(x)) for x in g[~g.exclude_duplicate.astype(bool)].fold)))
    D = pd.DataFrame(rows)
    nd = sp[sp.video_id.isin([1349, 1363])][["video_id", "content_id", "run_index", "fold", "exclude_duplicate"]]
    return D, nd


def raters():
    lab = pd.read_csv(LABELS).set_index("stim_num_int").sort_index()
    P = lab[[f"score_{i}" for i in range(34)]].values.astype(float)
    n_inf = np.full(len(P), np.nan)
    for k, p in enumerate(P):
        for n in range(1, NMAX + 1):
            if np.abs(p * n - np.round(p * n)).max() <= TOL:
                n_inf[k] = n; break
    return pd.DataFrame(dict(content_id=lab.index, n_inferred=n_inf))


def mc_runs():
    rows, summ = [], []
    for s in MC:
        m = pd.read_csv(PM / f"MindCaptioning/sub-{s}/v2/sub-{s}_samples.tsv", sep="\t")
        q = pd.read_csv(PM / f"MindCaptioning/sub-{s}/v2_qc/sub-{s}_samples_qc_usable.tsv", sep="\t")
        tr = m[m.part == "train"]
        for (ri, ses, run), g in tr.groupby(["run_index", "session", "run"]):
            has_test = bool(g.test_video_in_train_session.astype(bool).any())
            gq = q[(q.part == "train") & (q.run_index == ri)]
            rows.append(dict(participant=f"sub-{s}", run_index=int(ri), session=ses, run=run, n_blocks=len(g),
                             has_test_videos=has_test, n_blocks_after_qc=len(gq),
                             used_for_input_layer=not has_test))
        R = pd.DataFrame([r for r in rows if r["participant"] == f"sub-{s}"])
        summ.append(dict(participant=f"sub-{s}", train_runs=len(R), runs_with_test=int(R.has_test_videos.sum()),
                         test_run_positions=",".join(str(i + 1) for i, h in enumerate(R.sort_values("run_index").has_test_videos) if h),
                         input_layer_blocks=int(R.loc[R.used_for_input_layer, "n_blocks"].sum()),
                         input_layer_blocks_after_qc=int(R.loc[R.used_for_input_layer, "n_blocks_after_qc"].sum())))
    return pd.DataFrame(rows), pd.DataFrame(summ)


def presentation():
    ev = pd.read_csv(EVENTS, sep="\t", comment="#")
    ev = ev[~ev.is_baseline.astype(bool)].copy()
    st = pd.read_csv(STIMULI, sep="\t", comment="#").set_index("video_number")
    ev["video_s"] = ev.stimulus_number.astype(int).map(st.container_duration_s)
    ev["block_s"] = ev.duration_sec
    ev["short"] = ev.video_s < 8
    ev["block_minus_video_minus_rest"] = ev.block_s - 2 - np.where(ev.short, 8.0, ev.video_s)
    return ev[["participant_id", "session", "run", "stimulus_number", "video_s", "block_s", "short", "block_minus_video_minus_rest"]]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    D, nd = duplicates(); D.to_csv(OUT / "duplicates_15.tsv", sep="\t", index=False)
    print(f"[중복] 같은 content_id 파일 쌍 {len(D)}개, 먼저 제시된 쪽을 남긴 쌍 {int(D.kept_is_first.sum())}개")
    print(D.to_string(index=False))
    print("[1349/1363]", nd.to_dict("records"))

    R = raters(); R.to_csv(OUT / "rater_count_inferred.tsv", sep="\t", index=False)
    dup_c = set(D.content_id) | {1349}
    over = R[R.n_inferred > 17]
    print(f"[평정자 수 역산] 정해진 영상 {int(R.n_inferred.notna().sum())}/{len(R)}, 분포 {R.n_inferred.describe()[['min', '50%', 'max']].to_dict()}")
    print(f"  17 초과 {len(over)}개 (중복 내용과 겹침 {len(set(over.content_id) & dup_c)}개): {over.content_id.tolist()[:30]}")
    print("  n 값별 개수(상위):", R.n_inferred.value_counts().head(12).to_dict())

    M, MS = mc_runs(); M.to_csv(OUT / "mc_train_runs.tsv", sep="\t", index=False)
    print("[MC run]"); print(MS.to_string(index=False))

    P = presentation()
    S = P.groupby(["participant_id", "short"]).agg(n=("block_s", "size"), block_min=("block_s", "min"), block_max=("block_s", "max"),
                                                  extra_min=("block_minus_video_minus_rest", "min"),
                                                  extra_max=("block_minus_video_minus_rest", "max")).reset_index()
    S.to_csv(OUT / "presentation_length.tsv", sep="\t", index=False, float_format="%.3f")
    print("[제시 길이] short = 영상 8초 미만. extra = 블록 − 2초 휴지 − 제시 길이(짧은 영상은 8초로 가정)"); print(S.to_string(index=False))


if __name__ == "__main__":
    main()
