#!/usr/bin/env python3
"""핵심 3 결과 그림: 차원별 영상 간 r (뇌 469영역 vs 기준선), 피험자 5명 범위 (2026-10-24)."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

O = Path("/storage/bigdata/EmoBrain_response/stage1/02_brain")
FIG = Path("/storage/bigdata/EmoBrain_response/stage1/figures"); FIG.mkdir(parents=True, exist_ok=True)
INK, MUTED, GRID, GRAY = "#0b0b0b", "#52514e", "#e6e6e6", "#9a9890"
S1, S2 = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "Noto Sans CJK JP", "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False})


def panel(ax, d, space, title):
    d = d[d.target_space == space]
    b = d[d.input_condition == "brain_roi469"].groupby("dimension").r_oof.agg(["mean", "min", "max"]).sort_values("mean")
    L = d[d.input_condition == "lowlevel_L"].groupby("dimension").r_oof.mean().reindex(b.index)
    o = d[d.input_condition.isin(["duration", "brain_global"])].groupby(["dimension", "input_condition"]).r_oof.mean().unstack().max(1).reindex(b.index)
    y = np.arange(len(b))
    ax.hlines(y, b["min"], b["max"], color=S1, linewidth=2, alpha=0.35)
    ax.scatter(b["mean"], y, s=36, color=S1, zorder=3, label="뇌 469개 영역 평균 (5명 평균, 선 = 5명 범위)")
    ax.scatter(L, y, s=30, color=S2, marker="D", zorder=3, label="저수준 시각 특징 33개")
    ax.scatter(o, y, s=40, color=GRAY, marker="|", zorder=2, linewidths=2, label="영상 길이·뇌 전체 신호 중 큰 값")
    ax.axvline(0, color=MUTED, linewidth=0.8)
    ax.set_yticks(y); ax.set_yticklabels(b.index); ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
    ax.set_title(title, loc="left", fontsize=11, color=INK)
    ax.set_xlabel("영상 간 Pearson r (처음 보는 영상, run 묶음 6겹)")


def main():
    d = pd.read_csv(O / "dimension_metrics.tsv", sep="\t")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 9.5), gridspec_kw={"width_ratios": [1, 1], "wspace": 0.35})
    panel(a1, d, "A34", "34개 감정 범주 (A34, soft BCE 선형)")
    panel(a2, d, "A14", "14개 정서 척도 (A14, ridge)")
    a2.set_ylim(-0.8, 13.8)
    a1.set_xlim(-0.12, 0.8); a2.set_xlim(-0.12, 0.8)
    h, l = a1.get_legend_handles_labels()
    a1.legend(h, l, loc="upper left", bbox_to_anchor=(-0.05, -0.07), ncol=3, frameon=False, fontsize=9.5)
    fig.suptitle("Horikawa 뇌 단독 기준선: 차원별 예측 정확도 (피험자 5명)", x=0.06, ha="left", fontsize=13, color=INK, y=0.97)
    fig.savefig(FIG / "fig_core3_dimension_r.png", dpi=160, bbox_inches="tight", facecolor="#ffffff"); plt.close(fig)
    print("저장:", FIG / "fig_core3_dimension_r.png")


if __name__ == "__main__":
    main()
