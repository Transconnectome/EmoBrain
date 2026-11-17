#!/usr/bin/env python3
"""EmoBrain 선행 점검: 라벨 분포 자체 (2026-10-22). Horikawa 분석 영상 2,181개 (같은 내용 중복의 나중 제시 15개 제외).

감정 34개: 점수(그 감정을 고른 평정자 비율) 구간별 영상 수, 0 인 영상 수, 높은 점수 영상 수, 1위 감정인 영상 수, 분포 모양.
척도 14개: 1~9 점수 분포.
출력: prelim/label_distribution_emotions.tsv, label_distribution_bins.tsv, label_distribution_scales.tsv,
      fig_label_distribution_emotions.png, fig_label_distribution_scales.png
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, LogNorm  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

OUT = Path("/storage/bigdata/EmoBrain_response/prelim")
LAB = Path("/scratch/connectome/seokjin14/EmoBrain/project/shared/data")
META = Path("/storage/bigdata/Horikawa/metadata/horikawa_meta_data_with_dimension_binary.csv")
DIMS14 = ["valence", "arousal", "dominance", "approach", "attention", "certainty", "commitment", "control",
          "effort", "fairness", "identity", "obstruction", "safety", "upswing"]
BLUE = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]
INK, MUTED, GRID = "#1f1f1f", "#6b6b6b", "#e6e6e6"
plt.rcParams.update({"font.family": "Noto Sans CJK JP", "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False})


def main():
    names = [l.strip() for l in open(LAB / "cowen34_order.txt") if l.strip()]
    D = pd.read_csv(META); D.index = D.stimulus_num.str.replace("stimulus_", "").astype(int)
    Y = D[[f"score_{i}" for i in range(34)]].copy(); Y.columns = names
    C = pd.read_csv(LAB / "cowen_horikawa_labels.csv"); C.index = C.stim_num_int
    Z = C[[f"{d}_score" for d in DIMS14]].copy(); Z.columns = DIMS14
    T = pd.read_csv("/storage/bigdata/Horikawa/response_t1w/sub-01/v3/sub-01_samples.tsv", sep="\t")
    T = T[~T.exclude_duplicate.astype(bool)].drop_duplicates("video_id")
    vids = T.video_id.values; Y = Y.loc[vids]; Zv = Z.reindex(vids)
    n = len(vids)

    # 감정별 요약
    top = pd.Series((Y.values == Y.values.max(1, keepdims=True)).sum(0), index=names)
    rows = []
    for e in names:
        y = Y[e].values; nz = y[y > 0]
        rows.append({"감정": e, "평균": y.mean(), "0인_영상수": int((y == 0).sum()), "0보다큰_영상수": int((y > 0).sum()),
                     "0.2이상": int((y >= 0.2).sum()), "0.3이상": int((y >= 0.3).sum()), "0.5이상": int((y >= 0.5).sum()),
                     "0.7이상": int((y >= 0.7).sum()), "1위인_영상수": int(top[e]),
                     "0보다큰_영상의_중앙값": float(np.median(nz)) if len(nz) else np.nan,
                     "90퍼센트값": float(np.percentile(y, 90)), "최대": float(y.max()), "왜도": float(stats.skew(y))})
    E = pd.DataFrame(rows).sort_values("평균", ascending=False).reset_index(drop=True)
    E.to_csv(OUT / "label_distribution_emotions.tsv", sep="\t", index=False, float_format="%.3f")
    edges = [0, 1e-9, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0 + 1e-9]
    labels = ["0", "~0.1", "~0.2", "~0.3", "~0.4", "~0.5", "~0.6", "~0.7", "~0.8", "~0.9", "~1.0"]
    Bm = pd.DataFrame({e: np.histogram(Y[e].values, bins=edges)[0] for e in E.감정}).T; Bm.columns = labels
    Bm.to_csv(OUT / "label_distribution_bins.tsv", sep="\t")

    # 그림 1: 감정별 점수 구간 영상 수 (열지도) + 1위 감정 영상 수 (막대)
    cmap = LinearSegmentedColormap.from_list("blue", BLUE); cmap.set_bad("#ffffff")
    fig = plt.figure(figsize=(11, 10.5))
    gs = fig.add_gridspec(2, 2, width_ratios=[4.2, 1.3], height_ratios=[34, 0.7], wspace=0.04, hspace=0.12)
    ax = fig.add_subplot(gs[0, 0]); axb = fig.add_subplot(gs[0, 1], sharey=ax); cax = fig.add_subplot(gs[1, 0])
    M = Bm.values.astype(float); Mm = np.ma.masked_where(M == 0, M)
    im = ax.imshow(Mm, aspect="auto", cmap=cmap, norm=LogNorm(vmin=1, vmax=n))
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            if M[i, j] > 0:
                ax.text(j, i, f"{int(M[i, j])}", ha="center", va="center", fontsize=7,
                        color="#ffffff" if M[i, j] >= 150 else INK)
    ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels); ax.set_yticks(range(len(Bm))); ax.set_yticklabels(Bm.index)
    ax.xaxis.tick_top(); ax.xaxis.set_label_position("top")
    ax.set_xlabel("감정 점수 (그 감정을 고른 평정자 비율) 구간", labelpad=6); ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_xticks(np.arange(-0.5, len(labels)), minor=True); ax.set_yticks(np.arange(-0.5, len(Bm)), minor=True)
    ax.grid(which="minor", color="#ffffff", linewidth=2); ax.tick_params(which="minor", length=0)
    cb = fig.colorbar(im, cax=cax, orientation="horizontal"); cb.set_label("칸 안 숫자 = 영상 수 (색은 로그 눈금)", color=INK)
    cb.outline.set_visible(False)
    tv = top.reindex(Bm.index).values
    axb.barh(range(len(tv)), tv, color=BLUE[8], height=0.7); plt.setp(axb.get_yticklabels(), visible=False); axb.tick_params(axis="y", length=0)
    axb.xaxis.tick_top(); axb.xaxis.set_label_position("top")
    for i, v in enumerate(tv):
        axb.text(v + 8, i, str(int(v)), va="center", fontsize=7, color=INK)
    axb.set_xlabel("1위 감정인 영상 수"); axb.spines["left"].set_visible(False); axb.grid(axis="x", color=GRID, linewidth=0.8)
    axb.set_axisbelow(True); axb.set_xlim(0, max(tv) * 1.18); ax.set_ylim(len(Bm) - 0.5, -0.5)
    fig.suptitle(f"감정 34개의 점수 분포 (Horikawa 분석 영상 {n}개, 평균 점수 순)", x=0.06, ha="left", fontsize=12, color=INK, y=0.955)
    fig.savefig(OUT / "fig_label_distribution_emotions.png", dpi=160, bbox_inches="tight", facecolor="#ffffff"); plt.close(fig)

    # 척도 14개
    srows = []
    for d in DIMS14:
        z = Zv[d].dropna().values
        srows.append({"척도": d, "영상수": len(z), "평균": z.mean(), "표준편차": z.std(), "최소": z.min(), "25퍼센트": np.percentile(z, 25),
                      "중앙값": np.median(z), "75퍼센트": np.percentile(z, 75), "최대": z.max(), "왜도": stats.skew(z), "고유값수": len(np.unique(z))})
    S = pd.DataFrame(srows); S.to_csv(OUT / "label_distribution_scales.tsv", sep="\t", index=False, float_format="%.3f")
    fig, axes = plt.subplots(2, 7, figsize=(14, 4.6), sharey=True)
    for ax, d in zip(axes.ravel(), DIMS14):
        z = Zv[d].dropna().values
        ax.hist(z, bins=np.arange(1, 9.01, 0.5), color=BLUE[8], edgecolor="#ffffff", linewidth=1.5)
        ax.axvline(np.median(z), color=INK, linewidth=1, linestyle=(0, (2, 2)))
        ax.set_title(d, fontsize=10, color=INK, loc="left"); ax.set_xlim(1, 9); ax.set_xticks([1, 5, 9])
        ax.grid(axis="y", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
    for ax in axes[:, 0]:
        ax.set_ylabel("영상 수")
    fig.suptitle(f"정서 척도 14개의 점수 분포 (1~9 평균 평정, 점선 = 중앙값, 영상 {int(Zv.notna().all(1).sum())}개)", x=0.01, ha="left", fontsize=12, color=INK)
    fig.tight_layout(rect=[0, 0, 1, 0.92]); fig.savefig(OUT / "fig_label_distribution_scales.png", dpi=160, bbox_inches="tight", facecolor="#ffffff"); plt.close(fig)

    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 20)
    print(E.round(3).to_string(index=False)); print(); print(S.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
