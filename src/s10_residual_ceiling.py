#!/usr/bin/env python3
"""S10 6-4d 잔차의 noise ceiling (11/18 석진 님. 비판 agent 11/17의 반드시 고칠 것 1). CPU, 수 초. 기술 분석이고 판정은 없다.

질문: 장면 표현으로 예측되는 부분을 뺀 평정(잔차)에, 평정자 표본 잡음 말고 읽을 만한 변동이 남아 있는가.
"잔차를 뇌가 거의 읽지 못한다"는 6-4d 결과가 뇌에 정보가 없어서인지, 잔차가 잡음뿐이어서인지 가르기 위한 값이다.
- 범주 34개의 값은 평정자 n명 가운데 그 범주를 고른 비율 p다. 영상 v의 표본 잡음 분산은 p(1 − p) / (n − 1)로 추정한다(이항 표본 비율의 불편 추정).
  n은 manifests/s1/rater_count_inferred.tsv의 추정 평정자 수다(비율의 눈금에서 추정한 값이라 근사).
- 잔차 = p − (장면 표현의 교차 예측). 교차 예측은 그 영상을 뺀 학습 영상으로 맞춘 값이라 그 영상의 표본 잡음을 담지 않는다. 그래서 잔차의 잡음 분산도 같다.
- 판(T = 평정 그대로, Sw, V, C, Sall 잔차)과 범주마다, 영상들에 걸쳐 signal_fraction = 1 − 평균 잡음 분산 / 잔차 분산, ceiling_r = sqrt(max(signal_fraction, 0)).
  ceiling_r은 잡음 없는 참값을 완벽히 맞히는 예측이 낼 수 있는 r의 상한이다.
- 6-4d scores.tsv의 뇌 decoding r(5명 평균)을 ceiling_r로 나눈 값(ratio)을 함께 낸다. valence, arousal은 1~9점 평균이라 이 식이 맞지 않아 뺀다.
입력: s10_stats/beyond_scene/{targets.npz, scores.tsv}, manifests/s1/rater_count_inferred.tsv, 분할 표(video_id → content_id)
출력(--out, 기본 beyond_scene/residual_ceiling/): ceiling.tsv(판 × 범주), summary.tsv(판 × 네트워크의 34개 평균), run_info.json
사용: s10_residual_ceiling.py --stats <s10_stats/beyond_scene> [--out <폴더>]
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

import paths as P
import s4_common as c

RATERS = P.S1 / "rater_count_inferred.tsv"
READS = ("T", "Sw", "V", "C", "Sall")


def run(stats, out):
    z = np.load(Path(stats) / "targets.npz")
    targets = [str(t) for t in z["target"]]
    reads = [str(r) for r in z["read"]]
    if reads != list(READS):
        raise SystemExit(f"판 순서가 다르다: {reads}")
    vids = z["video_id"]
    split = c.load_split().set_index("video_id")
    rc = pd.read_csv(RATERS, sep="\t").set_index("content_id").n_inferred
    n = rc.loc[split.loc[vids, "content_id"].to_numpy()].to_numpy(np.float64)
    if np.isnan(n).any() or (n < 2).any():
        raise SystemExit("평정자 수가 없거나 2명보다 적은 영상이 있다")
    t_idx = reads.index("T")
    rows = []
    for k, tg in enumerate(targets):
        if tg in ("valence", "arousal"):
            continue
        p = z["truth"][t_idx, :, k]
        if p.min() < -1e-9 or p.max() > 1 + 1e-9:
            raise SystemExit(f"{tg}: 평정이 0~1 비율이 아니다")
        noise = np.mean(p * (1 - p) / (n - 1))
        for j, rd in enumerate(reads):
            v = z["truth"][j, :, k]
            var = float(np.var(v, ddof=1))
            sf = 1.0 - noise / var if var > 0 else np.nan
            rows.append(dict(read=rd, target=tg, residual_var=var, noise_var=noise, signal_fraction=sf, ceiling_r=float(np.sqrt(max(sf, 0.0))) if np.isfinite(sf) else np.nan))
    ce = pd.DataFrame(rows)
    sc = pd.read_csv(Path(stats) / "scores.tsv", sep="\t")
    sc = sc[sc.is_category][["network", "read", "target", "r", "verdict"]]
    m = sc.merge(ce, on=["read", "target"], how="left")
    m["ratio"] = m.r / m.ceiling_r
    o = Path(out)
    o.mkdir(parents=True, exist_ok=True)
    ce.to_csv(o / "ceiling.tsv", sep="\t", index=False)
    m.to_csv(o / "ceiling_with_decoding.tsv", sep="\t", index=False)
    summ = m.groupby(["network", "read"]).agg(mean_r=("r", "mean"), mean_ceiling_r=("ceiling_r", "mean"), mean_signal_fraction=("signal_fraction", "mean"),
                                              median_ratio=("ratio", "median")).reset_index()
    summ.to_csv(o / "summary.tsv", sep="\t", index=False)
    return dict(n_videos=len(vids), n_categories=int(ce.target.nunique()), rater_n_range=[float(n.min()), float(n.max())], rater_n_median=float(np.median(n)))


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 6-4d 잔차의 noise ceiling")
    ap.add_argument("--stats", required=True)
    ap.add_argument("--out", default="")
    a = ap.parse_args(argv)
    out = a.out or str(Path(a.stats) / "residual_ceiling")
    info = run(a.stats, out)
    info.update(stage="S10 6-4d 잔차 noise ceiling", stats=str(a.stats), code_commit=c.START_HEAD, code_dirty=c.START_DIRTY)
    (Path(out) / "run_info.json").write_text(json.dumps(info, indent=1, ensure_ascii=False))
    print(json.dumps(info, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
