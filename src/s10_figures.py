#!/usr/bin/env python3
"""S10 그림 (04 S10, 01 2-3, 2-6, 6-1의 "결과를 읽는 단위", 2026-11-15). GPU 없음, torch를 쓰지 않는다.

s10_performance.py가 쓴 표만 읽는다. 분석 폴더(all, common5)와 seed마다 두 그림을 그린다.
- per_emotion_r_seed<s>.png: 조건마다 정서 34개의 r(5명 평균)과 basic bootstrap 95% 구간. 계산할 수 없는 정서는 빈 자리로 둔다.
- participant_scores_seed<s>.png: 조건마다 참가자 5명의 점수(34개 정서 평균 r)와 5명 평균, 그 구간.
글꼴에 한글이 없을 수 있어 조건 이름은 fig_label(묶음 이름 또는 코드 이름)을 쓴다.
사용: s10_figures.py --out <s10_performance의 출력 폴더>
"""
import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def order_conditions(t):
    """그림의 조건 순서. 묶음 이름(A-1, A-2, B-1, ...) 순이고 나머지는 뒤에 둔다."""
    labels = t[["condition", "fig_label"]].drop_duplicates()
    return labels.sort_values("fig_label", key=lambda s: s.map(lambda x: (0, x) if len(x) <= 4 and x[:1] in "ABCDE" else (1, x))).condition.tolist()


def per_emotion_figure(t, path, title):
    conds = order_conditions(t)
    emotions = list(dict.fromkeys(t.emotion))
    x = np.arange(len(emotions))
    fig, axes = plt.subplots(len(conds), 1, figsize=(14, 2.2 * len(conds) + 1.2), sharex=True, sharey=True, squeeze=False)
    for ax, cond in zip(axes[:, 0], conds):
        g = t[t.condition == cond].set_index("emotion").reindex(emotions)
        ax.axhline(0, color="0.6", lw=0.8)
        ax.errorbar(x, g.r, yerr=[g.r - g.ci_low, g.ci_high - g.r], fmt="o", ms=3.5, lw=1, capsize=2, color="tab:blue")
        ax.set_ylabel("r")
        label = g.fig_label.dropna().iloc[0]
        ax.set_title(label if label == cond else f"{label} ({cond})", fontsize=9, loc="left")
        ax.grid(axis="y", color="0.9")
    axes[-1, 0].set_xticks(x)
    axes[-1, 0].set_xticklabels(emotions, rotation=70, ha="right", fontsize=8)
    fig.suptitle(title, fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def participant_figure(t, path, title):
    conds = order_conditions(t)
    fig, ax = plt.subplots(figsize=(max(6, 1.1 * len(conds) + 2), 4.5))
    ax.axhline(0, color="0.6", lw=0.8)
    for i, cond in enumerate(conds):
        g = t[t.condition == cond]
        part = g[g.participant != "mean5"].sort_values("participant")
        ax.scatter(i + np.linspace(-0.15, 0.15, len(part)), part.score_r, s=18, color="tab:gray", zorder=2)
        m = g[g.participant == "mean5"].iloc[0]
        ax.errorbar(i + 0.3, m.score_r, yerr=[[m.score_r - m.ci_low], [m.ci_high - m.score_r]], fmt="D", ms=5, color="black", capsize=3, zorder=3)
    ax.set_xticks(range(len(conds)))
    ax.set_xticklabels([t[t.condition == x].fig_label.iloc[0] for x in conds], rotation=40, ha="right", fontsize=8)
    ax.set_ylabel("participant score (mean r over computable emotions)")
    ax.set_title(title + "\ngray: participants, black: 5-participant mean with basic bootstrap 95% CI", fontsize=9)
    ax.grid(axis="y", color="0.9")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def draw(out):
    out = Path(out)
    made = []
    for analysis in ("all", "common5"):
        d = out / analysis
        if not (d / "per_emotion.tsv").exists():
            continue
        pe = pd.read_csv(d / "per_emotion.tsv", sep="\t")
        ps = pd.read_csv(d / "participant_scores.tsv", sep="\t")
        for seed in sorted(pe.seed.dropna().unique()):
            s = int(seed)
            sub = pe[(pe.seed == seed) & (pe.participant == "mean5")]
            per_emotion_figure(sub, d / f"per_emotion_r_seed{s}.png", f"Per-emotion r, 5-participant mean with basic bootstrap 95% CI ({analysis}, seed {s})")
            participant_figure(ps[ps.seed == seed], d / f"participant_scores_seed{s}.png", f"Participant scores ({analysis}, seed {s})")
            made += [d / f"per_emotion_r_seed{s}.png", d / f"participant_scores_seed{s}.png"]
    if not made:
        raise SystemExit(f"{out}: 그릴 표가 없다")
    return made


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 그림")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    for p in draw(a.out):
        print("그림", p)


if __name__ == "__main__":
    main()
