#!/usr/bin/env python3
"""비교 사다리 그림과 학습 곡선 그림 (2026-10-24). 이미 계산한 표만 읽는다."""
import glob
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

S = Path("/storage/bigdata/EmoBrain_response/stage1"); FIG = S / "figures"; FIG.mkdir(exist_ok=True)
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e6e6e6"
C_CONTENT, C_BRAIN, C_VIA = "#eb6834", "#2a78d6", "#1baf7a"
plt.rcParams.update({"font.family": "Noto Sans CJK JP", "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False})
# 모든 막대를 피험자별 같은 학습·평가 영상(04_brain_features ladder)에서 그린다
ROWS = [("내용만", "저수준 시각 33개", "lowlevel_L", C_CONTENT, "ladder"), ("내용만", "Horikawa 시각 1000개 (VGG19)", "hk_vision1000", C_CONTENT, "ladder"),
        ("내용만", "Horikawa 의미 73개", "hk_semantic73", C_CONTENT, "ladder"),
        ("뇌만", "뇌 469개 영역", "brain_roi469", C_BRAIN, "ladder"),
        ("뇌 → 내용 → 감정", "뇌 → 저수준 → 감정", "brain→lowlevel_L→emotion", C_VIA, "ladder"),
        ("뇌 → 내용 → 감정", "뇌 → 시각 1000 → 감정", "brain→hk_vision1000→emotion", C_VIA, "ladder"),
        ("뇌 → 내용 → 감정", "뇌 → 의미 73 → 감정", "brain→hk_semantic73→emotion", C_VIA, "ladder"),
        ("뇌 + 내용", "뇌 + 저수준", "brain+lowlevel_L", C_BRAIN, "ladder"), ("뇌 + 내용", "뇌 + 시각 1000", "brain+hk_vision1000", C_BRAIN, "ladder"),
        ("뇌 + 내용", "뇌 + 의미 73", "brain+hk_semantic73", C_BRAIN, "ladder")]


def ladder():
    st = pd.read_csv(S / "03_stimulus/dimension_metrics.tsv", sep="\t")
    br = pd.read_csv(S / "02_brain/dimension_metrics.tsv", sep="\t")
    ld = pd.concat([pd.read_csv(f, sep="\t") for f in sorted(glob.glob(str(S / "04_brain_features/ladder_dimension_metrics_sub-*.tsv")))])
    src = {"stim": st, "brain": br, "ladder": ld}
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.8), sharey=True, gridspec_kw={"wspace": 0.08})
    for ax, (space, title) in zip(axes, [("A34", "34개 감정 범주 (A34)"), ("A14", "14개 정서 척도 (A14)")]):
        ypos, y, prev = [], 0, None
        for fam, lab, cond, col, s in ROWS:
            if prev is not None and fam != prev:
                y += 0.6
            prev = fam; ypos.append(y)
            d = src[s]; d = d[(d.input_condition == cond) & (d.target_space == space)]
            per = d.groupby("participant_id").r_oof.mean()
            m = per.mean()
            hollow = fam == "뇌 + 내용"
            ax.barh(y, m, height=0.72, color="white" if hollow else col, edgecolor=col, linewidth=1.8, hatch="////" if hollow else None)
            if len(per) > 1:
                ax.hlines(y, per.min(), per.max(), color=INK, linewidth=1.2); ax.vlines([per.min(), per.max()], y - 0.15, y + 0.15, color=INK, linewidth=1.2)
            ax.text(max(m, per.max()) + 0.012, y, f"{m:.2f}", va="center", fontsize=8.5, color=INK)
            y += 1
        ax.set_yticks(ypos); ax.set_yticklabels([r[1] for r in ROWS]); ax.tick_params(axis="y", length=0)
        ax.set_ylim(max(ypos) + 0.7, min(ypos) - 0.7)   # 위에서 아래로 (세로축 공유라 invert 를 두 번 하지 않음)
        ax.set_xlim(0, 0.72); ax.grid(axis="x", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
        ax.set_title(title, loc="left", fontsize=11, color=INK); ax.set_xlabel("감정(척도)별 영상 간 r 의 평균 (처음 보는 영상)")
    from matplotlib.patches import Patch
    h = [Patch(facecolor=C_CONTENT, label="내용만 (뇌 없음, 같은 평가 영상)"), Patch(facecolor=C_BRAIN, label="뇌만"),
         Patch(facecolor=C_VIA, label="뇌에서 읽은 내용으로 감정"), Patch(facecolor="white", edgecolor=C_BRAIN, hatch="////", label="뇌 + 내용 함께")]
    axes[0].legend(handles=h, loc="upper left", bbox_to_anchor=(-0.45, -0.1), ncol=4, frameon=False, fontsize=9.5)
    fig.suptitle("비교 사다리: 피험자별 같은 평가 영상에서 내용만, 뇌만, 뇌 → 내용, 뇌 + 내용 (Horikawa 5명, 검은 선 = 5명 범위)", x=0.02, ha="left", fontsize=12.5, color=INK, y=0.99)
    fig.savefig(FIG / "fig_ladder.png", dpi=160, bbox_inches="tight", facecolor="#ffffff"); plt.close(fig)


def learning_curve():
    s = pd.read_csv(S / "05_learning_curve/summary_by_subject_repeat.tsv", sep="\t", dtype={"n_train_target": str})
    # 영상 하나당 스캔 시간: 실제 run 길이(볼륨 × TR 2초)의 합 / 제시 영상 수
    secs = []
    for sub in ["01", "02", "03", "04", "05"]:
        r = pd.read_csv(f"/storage/bigdata/Horikawa/response_t1w/sub-{sub}/v3_qc/sub-{sub}_runs_qc.tsv", sep="\t")
        secs.append(r.n_volumes.sum() * 2.0 / r.blocks_total.sum())
    per_video = float(np.mean(secs))
    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    for lab, col in [("A34 전체 34개", C_BRAIN), ("A14 척도 14개", C_CONTENT)]:
        g = s[s.묶음 == lab]
        full = g[g.n_train_target == "all"].set_index("participant_id").r_mean
        g = g.assign(pct=[100 * r / full[p] for p, r in zip(g.participant_id, g.r_mean)])
        a = g.groupby("n_train_target", sort=False).agg(n=("n_train_actual", "mean"), m=("pct", "mean"), lo=("pct", "min"), hi=("pct", "max"))
        a = a.sort_values("n")
        ax.fill_between(a.n, a.lo, a.hi, color=col, alpha=0.15, linewidth=0)
        ax.plot(a.n, a.m, color=col, linewidth=2, marker="o", markersize=7, label=f"{lab} (전체일 때 r {full.mean():.2f})")
        for n, m in zip(a.n, a.m):
            if lab.startswith("A34"):
                ax.text(n, m + 3, f"{m:.0f}%", ha="center", fontsize=8.5, color=INK)
    for yref in (80, 90):
        ax.axhline(yref, color=MUTED, linewidth=0.8, linestyle=(0, (3, 3))); ax.text(155, yref + 0.8, f"{yref}%", fontsize=8, color=MUTED)
    ticks = [176, 319, 609, 924, 1215, 1793]   # 1520 은 1793 과 글자가 겹쳐 눈금 글자만 뺌
    ax.set_xscale("log"); ax.minorticks_off()
    ax.set_xticks(ticks); ax.set_xticklabels([f"{t}\n(약 {t * per_video / 3600:.1f}시간)" for t in ticks], fontsize=8.5)
    ax.set_xlim(150, 2100); ax.set_ylim(40, 105)
    ax.set_xlabel(f"학습에 쓴 영상 수 (로그 눈금, 괄호 = 그만큼 보여 주는 스캔 시간, 영상당 약 {per_video:.0f}초)")
    ax.set_ylabel("전체 학습량 대비 예측 성능 (%)")
    ax.grid(axis="y", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="lower right")
    ax.set_title("학습 곡선: 학습 영상을 줄이면 뇌 → 감정 예측이 얼마나 떨어지나 (5명, 띠 = 5명×반복 범위)", loc="left", fontsize=11.5, color=INK)
    fig.savefig(FIG / "fig_learning_curve.png", dpi=160, bbox_inches="tight", facecolor="#ffffff"); plt.close(fig)
    print(f"영상당 스캔 시간 {per_video:.1f}초")


if __name__ == "__main__":
    ladder(); learning_curve(); print("그림 저장:", FIG)
