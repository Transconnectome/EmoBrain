#!/usr/bin/env python3
"""perturb_quick.py 결과 정리와 그림 (2026-10-31). matplotlib 이 있는 환경 (swift_PTL2) 에서 실행.

변화량 = (조작 후 예측 − 원본 예측) / 원본 예측의 영상 사이 SD (범주별). 영상 평균과 영상 사이 t 값을 낸다.
출력: <OUT>/13_perturbation/quick/{shift_summary.tsv, fig_quick_perturbation.png}
"""
from pathlib import Path

import numpy as np
import pandas as pd

OD = Path("/pscratch/sd/s/sjmoon/EmoBrain/project/output/prelim_2026-10/13_perturbation/quick")
SHOW = ["joy", "amusement", "adoration", "aesthetic appreciation", "awe", "calmness", "nostalgia", "sadness", "fear", "horror", "disgust", "boredom"]


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    P = pd.concat([pd.read_csv(f, sep="\t") for f in sorted(OD.glob("predictions_*.tsv"))], ignore_index=True)
    orig = P[P.condition == "orig"].set_index(["model", "video_id", "category"]).pred
    sd = P[P.condition == "orig"].groupby(["model", "category"]).pred.std()
    P = P.join(orig.rename("orig"), on=["model", "video_id", "category"])
    P["delta"] = (P.pred - P.orig) / P.set_index(["model", "category"]).index.map(sd).values
    g = P[P.condition != "orig"].groupby(["model", "condition", "level", "category"])["delta"]
    S = pd.DataFrame(dict(mean_shift=g.mean(), t=g.mean() / (g.std() / np.sqrt(g.count())), n=g.count())).reset_index()
    S.to_csv(OD / "shift_summary.tsv", sep="\t", index=False, float_format="%.4f")
    models = list(P.model.unique())
    fig, axes = plt.subplots(len(models), 2, figsize=(13, 5 * len(models)), squeeze=False)
    cmap = plt.get_cmap("tab20")
    for i, m in enumerate(models):
        for j, (cond, levels) in enumerate([("sat", [0, 0.5, 1.0, 1.5, 2.0]), ("bright", [0.5, 0.75, 1.0, 1.25, 1.5])]):
            ax = axes[i, j]
            for k, c in enumerate(SHOW):
                ys = [0.0 if lv == 1.0 else S[(S.model == m) & (S.condition == cond) & (S.level == lv) & (S.category == c)].mean_shift.iloc[0]
                      for lv in levels]
                ax.plot(levels, ys, "-o", ms=3, color=cmap(k), label=c)
            ax.axhline(0, color="k", lw=0.6); ax.axvline(1.0, color="gray", lw=0.6, ls=":")
            ax.set_xlabel({"sat": "saturation (x original; 0 = grayscale)", "bright": "brightness (x original)"}[cond])
            ax.set_ylabel("change in predicted rating\n(SD across videos)")
            ax.set_title(f"{m.upper()}: {'saturation' if cond == 'sat' else 'brightness'}")
            if j == 1:
                ax.legend(fontsize=7, loc="center left", bbox_to_anchor=(1.01, 0.5))
    fig.tight_layout(); fig.savefig(OD / "fig_quick_perturbation.png", dpi=140); plt.close(fig)
    for m in models:
        for cond, lv in [("sat", 0.0), ("bright", 0.5), ("bright", 1.5)]:
            s = S[(S.model == m) & (S.condition == cond) & (S.level == lv)].sort_values("mean_shift")
            print(m, cond, lv, "내려감:", ", ".join(f"{r.category} {r.mean_shift:+.2f}" for r in s.head(4).itertuples()),
                  "| 올라감:", ", ".join(f"{r.category} {r.mean_shift:+.2f}" for r in s.tail(4).itertuples()))


if __name__ == "__main__":
    main()
