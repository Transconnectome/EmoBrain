#!/usr/bin/env python3
"""0단계 보고서용 그림 3장 (2026-10-22). 이미 계산한 표만 읽는다.
  fig_label_correlation.png   : 34개 감정 상관 (군집 순서)
  fig_label_diagnostics.png   : 감정별 라벨 신뢰도 / 저수준 시각 특징이 설명하는 비율 / 영상 길이가 설명하는 비율
  fig_brain_reliability.png   : 네트워크별 피험자 간 일치도, MindCaptioning 반복 신뢰도, Horikawa 같은 내용 쌍 짝 찾기
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.cluster.hierarchy import leaves_list, linkage  # noqa: E402
from scipy.spatial.distance import squareform  # noqa: E402

P = Path("/storage/bigdata/EmoBrain_response/prelim")
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e6e6e6"
S1, S2 = "#2a78d6", "#eb6834"   # 범주 1·2 (검증 통과)
plt.rcParams.update({"font.family": "Noto Sans CJK JP", "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False})
NETS = ["Vis", "DorsAttn", "SalVentAttn", "Default", "Cont", "SomMot", "Limbic", "Subcortex", "Brainstem", "Hypothalamus"]


def fig_corr():
    R = pd.read_csv(P / "label_structure_emotion_corr.tsv", sep="\t", index_col=0)
    Z = linkage(squareform(1 - R.values, checks=False), "average"); o = leaves_list(Z); R = R.iloc[o, o]
    cmap = LinearSegmentedColormap.from_list("div", ["#184f95", "#6da7ec", "#f0efec", "#f0a3a2", "#e34948", "#a62b2a"])
    fig, ax = plt.subplots(figsize=(10.5, 9.5))
    im = ax.imshow(np.where(np.eye(len(R), dtype=bool), np.nan, R.values), cmap=cmap, vmin=-0.8, vmax=0.8)
    ax.set_xticks(range(len(R))); ax.set_xticklabels(R.columns, rotation=60, ha="right"); ax.set_yticks(range(len(R))); ax.set_yticklabels(R.index)
    for i in range(len(R)):
        for j in range(len(R)):
            v = R.values[i, j]
            if i != j and abs(v) >= 0.3:
                ax.text(j, i, f"{v:.2f}".replace("0.", "."), ha="center", va="center", fontsize=6, color="#ffffff" if abs(v) >= 0.55 else INK)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02); cb.set_label("영상 간 Pearson 상관 (|r| ≥ 0.3 만 숫자 표시)"); cb.outline.set_visible(False)
    ax.set_title("감정 34개끼리의 상관 (Horikawa 분석 영상 2,181개, 비슷한 감정끼리 모은 순서)", loc="left", fontsize=12, color=INK, pad=10)
    fig.savefig(P / "fig_label_correlation.png", dpi=160, bbox_inches="tight", facecolor="#ffffff"); plt.close(fig)


def fig_diag():
    E = pd.read_csv(P / "label_distribution_emotions.tsv", sep="\t")
    rel = pd.read_csv(P / "label_structure_reliability.tsv", sep="\t").set_index("감정").라벨신뢰도
    low = pd.read_csv(P / "label_lowlevel_r2.tsv", sep="\t"); low = low[low.라벨.str.startswith("감정:")]; low.index = low.라벨.str[3:]
    dur = pd.read_csv(P / "label_structure_duration_r2.tsv", sep="\t"); dur = dur[dur.라벨.str.startswith("감정:")]; dur.index = dur.라벨.str[3:]
    names = E.감정.tolist(); y = np.arange(len(names))
    fig, axes = plt.subplots(1, 4, figsize=(13, 9.5), sharey=True, gridspec_kw={"width_ratios": [1.1, 1.1, 1, 1], "wspace": 0.16})
    panels = [(E.set_index("감정")["0.5이상"].reindex(names).values, "점수 0.5 이상 영상 수", "{:.0f}", None),
              (rel.reindex(names).values, "라벨 신뢰도 (평정자 잡음 대비)", "{:.2f}", (0, 1.08)),
              (low.저수준특징_R2.reindex(names).clip(lower=0).values, "저수준 시각 특징 33개가\n설명하는 비율 (교차검증 R²)", "{:.3f}", None),
              (dur.영상길이로_설명_R2.reindex(names).clip(lower=0).values, "영상 길이가 설명하는 비율\n(교차검증 R²)", "{:.3f}", None)]
    for ax, (v, title, fmt, lim) in zip(axes, panels):
        ax.barh(y, v, color=S1, height=0.68)
        ax.set_title(title, loc="left", fontsize=10, color=INK); ax.grid(axis="x", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
        xm = lim[1] if lim else np.nanmax(v) * 1.3
        ax.set_xlim(0, xm)
        for i, val in enumerate(v):
            if np.isfinite(val):
                ax.text(val + xm * 0.01, i, fmt.format(val), va="center", fontsize=7, color=MUTED)
        ax.tick_params(axis="y", length=0)
    axes[0].set_yticks(y); axes[0].set_yticklabels(names); axes[0].set_ylim(len(names) - 0.5, -0.6)
    fig.suptitle("감정별 진단 (Horikawa 분석 영상 2,181개, 평균 점수 순)", x=0.1, ha="left", fontsize=12, color=INK, y=0.96)
    fig.savefig(P / "fig_label_diagnostics.png", dpi=160, bbox_inches="tight", facecolor="#ffffff"); plt.close(fig)


def fig_brain():
    hk = pd.read_csv(P / "reliability/Horikawa_isc_roi469.tsv", sep="\t").groupby("network").피험자간일치도_평균.median()
    mc = pd.read_csv(P / "reliability/MindCaptioning_isc_roi469.tsv", sep="\t").groupby("network").피험자간일치도_평균.median()
    mcrep = {s: json.loads((P / f"reliability/MindCaptioning_sub-{s}_within.json").read_text())["네트워크별_voxel신뢰도_중앙값"] for s in ["01", "02", "03", "04", "05", "06"]}
    hkdup = {s: json.loads((P / f"reliability/Horikawa_sub-{s}_within.json").read_text())["네트워크별_반복"] for s in ["01", "02", "03", "04", "05"]}
    y = np.arange(len(NETS))
    fig, axes = plt.subplots(1, 3, figsize=(14, 5.2), sharey=True, gridspec_kw={"wspace": 0.12})
    ax = axes[0]; h = 0.36
    ax.barh(y - h / 2 - 0.01, hk.reindex(NETS).values, height=h, color=S1, label="Horikawa (5명)")
    ax.barh(y + h / 2 + 0.01, mc.reindex(NETS).values, height=h, color=S2, label="MindCaptioning (6명)")
    for i, (a, b) in enumerate(zip(hk.reindex(NETS).values, mc.reindex(NETS).values)):
        ax.text(a + 0.01, i - h / 2, f"{a:.2f}", va="center", fontsize=7, color=MUTED); ax.text(b + 0.01, i + h / 2, f"{b:.2f}", va="center", fontsize=7, color=MUTED)
    ax.set_title("피험자 간 일치도 (영역별, 네트워크 중앙값)\n한 명 vs 나머지 평균의 영상 간 상관", loc="left", fontsize=10, color=INK)
    ax.legend(frameon=False, loc="lower right"); ax.set_xlim(0, 0.72)
    ax = axes[1]
    for k, s in enumerate(mcrep):
        v = [mcrep[s].get(n, np.nan) for n in NETS]
        ax.scatter(v, y + (k - 2.5) * 0.06, s=14, color=S2, alpha=0.75, linewidths=0)
    med = [np.nanmedian([mcrep[s].get(n, np.nan) for s in mcrep]) for n in NETS]
    ax.scatter(med, y, marker="|", s=260, color=INK, linewidths=2, label="6명 중앙값")
    ax.set_title("MindCaptioning 반복 신뢰도 (voxel 중앙값)\n시험 영상 72개 × 5회, 점 = 피험자", loc="left", fontsize=10, color=INK)
    ax.axvline(0, color=MUTED, linewidth=0.8); ax.legend(frameon=False, loc="lower right"); ax.set_xlim(-0.2, 0.65)
    ax = axes[2]
    for k, s in enumerate(hkdup):
        v = [hkdup[s].get(n, {}).get("짝찾기", np.nan) for n in NETS]
        ax.scatter(v, y + (k - 2) * 0.07, s=14, color=S1, alpha=0.75, linewidths=0)
    mean = [np.nanmean([hkdup[s].get(n, {}).get("짝찾기", np.nan) for s in hkdup]) for n in NETS]
    ax.scatter(mean, y, marker="|", s=260, color=INK, linewidths=2, label="5명 평균")
    ax.axvline(0.5, color=MUTED, linewidth=1, linestyle=(0, (3, 3))); ax.text(0.505, len(NETS) - 0.45, "우연 수준 0.5", fontsize=7, color=MUTED)
    ax.set_title("Horikawa 같은 내용 영상 15쌍의 짝 찾기\n반응 패턴으로 짝을 고른 비율, 점 = 피험자", loc="left", fontsize=10, color=INK)
    ax.legend(frameon=False, loc="lower right"); ax.set_xlim(0.25, 1.0)
    for ax in axes:
        ax.grid(axis="x", color=GRID, linewidth=0.8); ax.set_axisbelow(True); ax.tick_params(axis="y", length=0)
    axes[0].set_yticks(y); axes[0].set_yticklabels(NETS); axes[0].invert_yaxis()
    fig.suptitle("같은 영상에 대한 뇌 반응의 안정성 (네트워크별, 감정 라벨 사용 안 함)", x=0.08, ha="left", fontsize=12, color=INK, y=1.04)
    fig.savefig(P / "fig_brain_reliability.png", dpi=160, bbox_inches="tight", facecolor="#ffffff"); plt.close(fig)


if __name__ == "__main__":
    fig_corr(); fig_diag(); fig_brain(); print("그림 3장 저장")
