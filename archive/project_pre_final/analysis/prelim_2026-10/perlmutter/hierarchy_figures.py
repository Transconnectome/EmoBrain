#!/usr/bin/env python3
"""hierarchy_components.py 결과의 그림과 위계 판정 (2026-10-31). matplotlib 이 있는 환경 (swift_PTL2) 에서 실행.

시각 묶음 (visual 열) 마다
1. 묶음별 디코딩 r (fold 안 평균을 뺀 r, 피험자 평균 ± SD), 부분마다 한 줄. 피질 16묶음은 네트워크 순서 (Vis → Default), 그 뒤 피질하·소뇌·뇌 전체.
2. 위계 기울기: 피질 16묶음에서 네트워크 순위와 각 부분 r 의 Spearman 을 피험자마다. 캡션 쪽 비율 = 캡션에만 r / (캡션에만 r + 시각에만 r) 도 참고로.
3. 판정 (README 에 실행 전에 적은 기준): 조작 확인 (자극 수준 캡션에만 설명력, Vis 캡션에만 r) 과 주 판정 (캡션에만 r 의 Spearman, 4/5 명 양 + 평균 ≥ 0.3).
그림: 위 패널은 마지막 시각 묶음 (V-JEPA 2 + DINOv2) 의 부분별 r, 아래 패널은 판정에 쓰는 캡션에만 r 을 두 시각 묶음으로 비교. A14 는 arousal 패널 추가.
출력: <OUT>/16_hierarchy/{gradient.tsv, caption_share.tsv, fig_hierarchy_A34.png, fig_hierarchy_A14.png}
"""
from pathlib import Path

import numpy as np
import pandas as pd

OD = Path("/pscratch/sd/s/sjmoon/EmoBrain/project/output/prelim_2026-10/16_hierarchy")
CORTEX = ["Vis", "SomMot", "DorsAttn_Post", "DorsAttn_Front", "SalVentAttn_Post", "SalVentAttn_FrontIns", "SalVentAttn_Med",
          "Limbic_OFC", "Limbic_TempPole", "Cont_ParTemp", "Cont_PFC", "Cont_Med", "Default_Temp", "Default_Par", "Default_PFC", "Default_pCunPCC"]
SUBC = ["Hippocampus", "Amygdala", "Thalamus", "Striatum", "NAc", "Pallidum", "Hypothal+BNST+Brainstem", "Cerebellum"]
ORDER = CORTEX + SUBC + ["Whole brain"]
NET_RANK = {"Vis": 1, "SomMot": 2, "DorsAttn": 3, "SalVentAttn": 4, "Limbic": 5, "Cont": 6, "Default": 7}
COMP = [("시각에만", "visual only", "#d62728"), ("둘 다", "shared", "#9467bd"), ("캡션에만", "caption only", "#1f77b4"),
        ("나머지", "residual (neither)", "#7f7f7f"), ("평정 전체", "full rating", "k")]
VIS_STYLE = {"V-JEPA 2": ("--", "#9ecae1"), "V-JEPA 2 + DINOv2": ("-", "#08519c")}
MIN_SUM = 0.05


def spearman(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float); ok = np.isfinite(a) & np.isfinite(b)
    return pd.Series(a[ok]).rank().corr(pd.Series(b[ok]).rank())


def caption_share(R):
    w = R.pivot_table(index=["visual", "space", "participant", "group"], columns="component", values="r_mean").reset_index()
    tot = w["캡션에만"] + w["시각에만"]
    w["caption_share"] = np.where(tot >= MIN_SUM, w["캡션에만"] / tot, np.nan)
    w[["visual", "space", "participant", "group", "시각에만", "캡션에만", "caption_share"]].to_csv(
        OD / "caption_share.tsv", sep="\t", index=False, float_format="%.4f")
    return w


def gradient(R, W):
    rows = []
    rank = [NET_RANK[g.split("_")[0]] for g in CORTEX]
    for (vis, sp, sub), d in R[R.group.isin(CORTEX)].groupby(["visual", "space", "participant"]):
        w = d.pivot(index="group", columns="component", values="r_mean").loc[CORTEX]
        cs = W[(W.visual == vis) & (W.space == sp) & (W.participant == sub)].set_index("group").caption_share
        res = dict(visual=vis, space=sp, participant=sub, rho_caption_share=spearman(rank, cs.loc[CORTEX]))
        for k, *_ in COMP:
            res[f"rho_{k}"] = spearman(rank, w[k])
        rows.append(res)
    G = pd.DataFrame(rows)
    G.to_csv(OD / "gradient.tsv", sep="\t", index=False, float_format="%.3f")
    return G


def verdict(S, G, P):
    for vis in G.visual.unique():
        g = G[(G.visual == vis) & (G.space == "A34")].rho_캡션에만.values
        vis_r = S[(S.visual == vis) & (S.space == "A34") & (S.group == "Vis") & (S.component == "캡션에만")].r_mean.iloc[0]
        cap = P[(P.visual == vis) & (P.space == "A34")].caption_only.iloc[0] if P is not None and (P.visual == vis).any() else np.nan
        ok = (g > 0).sum() >= 4 and g.mean() >= 0.3
        print(f"[{vis}] 자극 수준 캡션에만 설명력 {cap:.3f} | Vis 캡션에만 r {vis_r:.3f} | "
              f"캡션에만 r 과 위계 순위 Spearman 평균 {g.mean():+.2f}, 피험자별 {' '.join(f'{x:+.2f}' for x in g)} → {'있음' if ok else '없음'}")


def fig(S, W, sp, out, arousal=False):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    vis_main = "V-JEPA 2 + DINOv2" if (S.visual == "V-JEPA 2 + DINOv2").any() else "V-JEPA 2"
    d = S[(S.space == sp) & (S.visual == vis_main)]
    x = np.arange(len(ORDER))
    nrow = 3 if arousal else 2
    f, axes = plt.subplots(nrow, 1, figsize=(15, 4.3 * nrow), sharex=True)
    for k, lab, col in COMP:
        e = d[d.component == k].set_index("group").reindex(ORDER)
        axes[0].errorbar(x, e.r_mean, yerr=e.r_sd, fmt="-o", ms=4, lw=1.2, capsize=2, color=col, label=lab)
        if arousal:
            axes[2].plot(x, e.r_arousal, "-o", ms=4, lw=1.2, color=col, label=lab)
    for vis, (ls, col) in VIS_STYLE.items():
        if not (S.visual == vis).any():
            continue
        e = S[(S.space == sp) & (S.visual == vis) & (S.component == "캡션에만")].set_index("group").reindex(ORDER)
        axes[1].errorbar(x, e.r_mean, yerr=e.r_sd, fmt=ls + "o", ms=4, lw=1.4, capsize=2, color=col, label=f"caption only, visual = {vis}")
        w = W[(W.space == sp) & (W.visual == vis)]
        for _, ws in w.groupby("participant"):
            axes[1].plot(x, ws.set_index("group")["캡션에만"].reindex(ORDER), "o", ms=2.5, color=col, alpha=0.4)
    axes[0].set_ylabel("decoding r (mean over\ndimensions, 5 subjects)")
    axes[0].set_title(f"{'34 categories' if sp == 'A34' else '14 dimensions'}: brain decoding of each part of the emotion rating (visual = {vis_main})")
    axes[1].set_ylabel("decoding r of the\ncaption-only part")
    axes[1].set_title("caption-only part: does it rise toward higher cortex once more visual information is removed? (dots = subjects)")
    axes[1].legend(fontsize=8, loc="upper left", bbox_to_anchor=(1.005, 1.0))
    if arousal:
        axes[2].set_ylabel("decoding r, arousal only"); axes[2].set_title(f"arousal (visual = {vis_main})")
    for ax in axes:
        ax.axhline(0, color="k", lw=0.5)
        for b in (len(CORTEX) - 0.5, len(CORTEX) + len(SUBC) - 0.5):
            ax.axvline(b, color="gray", lw=0.8, ls="--")
        for i in range(1, len(CORTEX)):
            if CORTEX[i].split("_")[0] != CORTEX[i - 1].split("_")[0]:
                ax.axvline(i - 0.5, color="gray", lw=0.4, ls=":")
    axes[0].legend(fontsize=8, loc="upper left", bbox_to_anchor=(1.005, 1.0))
    axes[-1].set_xticks(x); axes[-1].set_xticklabels(ORDER, rotation=60, ha="right", fontsize=8)
    f.tight_layout(); f.savefig(out, dpi=140); plt.close(f)


def main():
    R = pd.read_csv(OD / "group_component_r.tsv", sep="\t"); S = pd.read_csv(OD / "summary.tsv", sep="\t")
    for T in (R, S):
        if "visual" not in T.columns:
            T.insert(0, "visual", "V-JEPA 2")
    P = pd.read_csv(OD / "stimulus_partition.tsv", sep="\t") if (OD / "stimulus_partition.tsv").exists() else None
    W = caption_share(R); G = gradient(R, W)
    for (vis, sp), g in G.groupby(["visual", "space"]):
        print(f"{vis} · {sp} 피질 16묶음, 네트워크 순위와의 Spearman (피험자 5명)")
        for c in [c for c in G.columns if c.startswith("rho_")]:
            v = g[c].values
            print(f"  {c:24s} 평균 {np.nanmean(v):+.3f}  피험자별 {' '.join(f'{x:+.3f}' for x in v)}")
    print("판정 (34개 범주)"); verdict(S, G, P)
    fig(S, W, "A34", OD / "fig_hierarchy_A34.png")
    fig(S, W, "A14", OD / "fig_hierarchy_A14.png", arousal=True)


if __name__ == "__main__":
    main()
