#!/usr/bin/env python3
"""공정 비교 baseline 요약: 모든 예측에 같은 지표 묶음(perlmutter/metrics_panel.py)을 적용한다 (2026-10-28).

포함: runs/<protocol>/<입력>_<모델>/predictions_sub-*.tsv.gz, 그리고 ours 프로토콜에서 이미 돌린 우리 모델
(soft BCE 선형 student, MLP student; project/output/prelim_2026-10/07_students/).
추가 지표: mae_sum34_minmax (GED 처럼 감정마다 전체 영상의 최소~최대로 0~1 정규화한 target 에서 계산한 34개 합산 MAE),
GED 의 test_selected_mae_sum34 (평가 세트에서 가장 좋은 epoch 의 MAE; 문헌식 선택이라 결과로 쓰지 않고 차이만 본다).
출력: runs/summary_by_subject.tsv, runs/summary.tsv
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = Path("/pscratch/sd/s/sjmoon/EmoBrain")
sys.path.insert(0, str(REPO / "project/analysis/prelim_2026-10/perlmutter"))
import metrics_panel as mp  # noqa: E402

rs = mp.rs


def sources():
    for d in sorted((HERE / "runs").glob("*/*_*")):
        fs = sorted(d.glob("predictions_sub-0?.tsv.gz"))
        if fs:
            yield d.parent.name, d.name, fs
    for name, pat in [("softbce_student", "07_students/softbce/predictions_sub-*.tsv.gz"), ("mlp_student", "07_students/mlp/predictions_sub-*.tsv.gz")]:
        fs = sorted(rs.OUT.glob(pat))
        if fs:
            yield "ours", name, fs


def main():
    names, Y34, _ = rs.cl.labels_for(np.arange(1, 2197)); lo, hi = Y34.min(0), Y34.max(0)
    span = dict(zip(names, np.where(hi > lo, hi - lo, 1))); low = dict(zip(names, lo))
    rows = []
    for proto, model, fs in sources():
        P = pd.concat([pd.read_csv(f, sep="\t") for f in fs])
        for (pid, cond, space), g in P.groupby(["participant_id", "input_condition", "target_space"]):
            dm = pd.DataFrame([mp.dim_metrics(h, space) for _, h in g.groupby("dimension")]).mean()
            r = dict(protocol=proto, model=model, condition=cond, target_space=space, participant_id=pid, **dm.to_dict(), **mp.profile_metrics(g, space))
            if space == "A34":
                gg = g.assign(yt=(g.y_true - g.dimension.map(low)) / g.dimension.map(span), yp=(g.y_pred - g.dimension.map(low)) / g.dimension.map(span))
                r["mae_sum34_minmax"] = (gg.yt - gg.yp).abs().groupby(gg.video_id).sum().mean()
            cf = HERE / "runs" / proto / model / f"ged_curves_{pid}.tsv"
            if cf.exists():
                c = pd.read_csv(cf, sep="\t"); r["test_selected_mae_sum34"] = c.groupby("fold").test_mae_sum.min().mean()
                r["val_selected_mae_sum34"] = c.loc[c.groupby("fold").val_mae_sum.idxmin()].test_mae_sum.mean()
            rows.append(r)
    R = pd.DataFrame(rows); R.to_csv(HERE / "runs/summary_by_subject.tsv", sep="\t", index=False, float_format="%.5f")
    S = R.groupby(["target_space", "protocol", "model", "condition"]).mean(numeric_only=True)
    S.to_csv(HERE / "runs/summary.tsv", sep="\t", float_format="%.4f")
    key = ["pearson", "spearman", "r2", "soft_bce", "auc_ge01", "map27", "mae_sum34", "mae_sum34_minmax", "micro_f1", "profile_r", "pair_id",
           "test_selected_mae_sum34", "val_selected_mae_sum34"]
    pd.set_option("display.width", 300); pd.set_option("display.max_columns", 40)
    for sp in ["A34", "A14"]:
        if sp in S.index.get_level_values(0):
            print(f"== {sp}"); print(S.loc[sp][[k for k in key if k in S.columns]].dropna(axis=1, how="all").round(3).to_string())


if __name__ == "__main__":
    main()
