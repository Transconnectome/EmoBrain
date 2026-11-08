#!/usr/bin/env python3
"""feature_content_map.py · feature_overlap.py 가 쓴 표로 그림 두 장 (2026-10-30). matplotlib 이 있는 환경에서 실행.
fig_emotion_partition.png : 감정별 V-JEPA 2 에만 있는 정보 / 둘 다 가진 정보 / 캡션에만 있는 정보, 그리고 캡션 위에 V-JEPA 2·저수준 특징이 더하는 정보
fig_concepts.png          : 장면 개념 73개를 캡션(x)과 V-JEPA 2(y)로 예측한 r
"""
from pathlib import Path

import numpy as np
import pandas as pd

OD = Path("/pscratch/sd/s/sjmoon/EmoBrain/project/output/prelim_2026-10/12_feature_overlap")
NOT_CK = {"envy", "guilt", "contempt", "disappointment", "pride", "triumph", "sympathy"}  # D31 보조 요약에서 빼는 7개


def main():
    part = pd.read_csv(OD / "emotion_partition_by_category.tsv", sep="\t")
    part = part[(part.semantic == "사람 캡션") & (part.visual == "V-JEPA 2 (영상)")].set_index("category")
    low = pd.read_csv(OD / "emotion_partition_lowlevel.tsv", sep="\t").set_index("category")
    t = pd.DataFrame(dict(vonly=part.r2_both - part.r2_semantic, common=part.r2_visual + part.r2_semantic - part.r2_both,
                          conly=part.r2_both - part.r2_visual)).clip(lower=0)
    t["lowonly"] = low.lowlevel_only.clip(lower=0)
    t = t.sort_values("vonly")
    ctab = pd.read_csv(OD / "concept_prediction.tsv", sep="\t")
    figures(t, ctab, OD)
    model_grid(OD, ctab)


def figures(t, ctab, od):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 10), gridspec_kw=dict(width_ratios=[3, 1]), sharey=True)
    y = np.arange(len(t)); labels = [f"{c} *" if c in NOT_CK else c for c in t.index]
    a1.barh(y, t.vonly, color="#2b6cb0", label="V-JEPA 2 only")
    a1.barh(y, t.common, left=t.vonly, color="#8e7cc3", label="shared (both)")
    a1.barh(y, t.conly, left=t.vonly + t.common, color="#e08a2b", label="caption only")
    a1.set_yticks(y); a1.set_yticklabels(labels, fontsize=9); a1.set_xlabel("explained variance of rating (R², stimulus level)")
    a1.set_title("Emotion information: V-JEPA 2 vs human captions\nblue+purple = V-JEPA 2 alone, purple+orange = caption alone, whole bar = both"); a1.legend(loc="lower right", fontsize=9)
    a2.barh(y + 0.2, t.vonly, height=0.4, color="#2b6cb0", label="V-JEPA 2 added to caption")
    a2.barh(y - 0.2, t.lowonly, height=0.4, color="#3a9e6f", label="low-level added to caption")
    a2.set_xlabel("R²(caption + X) − R²(caption alone)"); a2.set_xlim(0, None)
    a2.set_title("What vision adds to captions"); a2.legend(loc="lower right", fontsize=8)
    fig.text(0.01, 0.005, "* not distinct in Cowen & Keltner 2017 (D31 supplement excludes); near-zero R², values unstable", fontsize=8)
    fig.tight_layout(); fig.savefig(od / "fig_emotion_partition.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 9))
    ax.scatter(ctab.r_caption, ctab.r_vjepa2, s=20 + 400 * ctab.prevalence, c=ctab.vjepa2_minus_caption, cmap="coolwarm_r",
               vmin=-0.3, vmax=0.3, edgecolor="k", lw=0.4)
    lim = [min(ctab.r_caption.min(), ctab.r_vjepa2.min()) - 0.05, 1]
    ax.plot(lim, lim, "k--", lw=0.7)
    d = ctab.vjepa2_minus_caption
    pick = pd.concat([ctab.loc[d.nlargest(12).index], ctab.loc[d.nsmallest(12).index]])
    for _, r in pick.iterrows():
        ax.annotate(r.concept, (r.r_caption, r.r_vjepa2), fontsize=7.5, xytext=(3, 2), textcoords="offset points")
    ax.set_xlabel("predicted from human captions (r)"); ax.set_ylabel("predicted from V-JEPA 2 (r)")
    ax.set_title("Scene concepts (Horikawa 73): above line = V-JEPA 2 captures better\nblue = V-JEPA 2 better, red = captions better; size = prevalence")
    ax.set_xlim(lim); ax.set_ylim(lim); fig.tight_layout(); fig.savefig(od / "fig_concepts.png", dpi=150); plt.close(fig)


def model_grid(od, ctab):
    """시각 모델 다섯 개 비교: 감정별 '캡션 위에 더하는 정보', 장면 개념별 r(모델) − r(캡션)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    models = [("V-JEPA 2 (영상)", "V-JEPA 2\nvideo, no text", "r_vjepa2"), ("VideoMAE (영상)", "VideoMAE\nvideo, action labels", "r_videomae"),
              ("DINOv2 (이미지)", "DINOv2\nimage, no text", "r_dinov2"), ("CLIP (이미지)", "CLIP\nimage + text", "r_clip_vitl14"),
              ("VGG19 fc8 (이미지)", "VGG19 fc8\nimage, labels", "r_hk_vision1000")]
    part = pd.read_csv(od / "emotion_partition_by_category.tsv", sep="\t")
    part = part[part.semantic == "사람 캡션"]
    E = pd.DataFrame({lab: part[part.visual == key].set_index("category").eval("r2_both - r2_semantic") for key, lab, _ in models})
    E = E.loc[E.max(1).sort_values(ascending=False).index]
    d = pd.DataFrame({lab: ctab.set_index("concept")[col] - ctab.set_index("concept").r_caption for _, lab, col in models})
    d = d.loc[d.mean(1).sort_values(ascending=False).index]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 13), gridspec_kw=dict(width_ratios=[1, 1]))
    im = a1.imshow(E.values, cmap="Blues", vmin=0, vmax=0.08, aspect="auto")
    a1.set_yticks(range(len(E))); a1.set_yticklabels([f"{c} *" if c in NOT_CK else c for c in E.index], fontsize=8)
    a1.set_xticks(range(len(models))); a1.set_xticklabels([m[1] for m in models], fontsize=8)
    for i in range(E.shape[0]):
        for j in range(E.shape[1]):
            v = E.values[i, j]
            if v >= 0.02:
                a1.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=6.5, color="w" if v > 0.05 else "k")
    a1.set_title("Emotion: information the model adds to captions\nR²(caption + model) − R²(caption)", fontsize=10)
    fig.colorbar(im, ax=a1, fraction=0.04)
    im2 = a2.imshow(d.values, cmap="RdBu", vmin=-0.6, vmax=0.6, aspect="auto")
    a2.set_yticks(range(len(d))); a2.set_yticklabels(d.index, fontsize=6.5)
    a2.set_xticks(range(len(models))); a2.set_xticklabels([m[1] for m in models], fontsize=8)
    a2.set_title("Scene concepts (Horikawa 73): r(model) − r(caption)\nblue = model better, red = caption better", fontsize=10)
    fig.colorbar(im2, ax=a2, fraction=0.04)
    fig.text(0.01, 0.005, "* not distinct in Cowen & Keltner 2017; near-zero R², unstable", fontsize=8)
    fig.tight_layout(); fig.savefig(od / "fig_visual_models.png", dpi=150); plt.close(fig)


if __name__ == "__main__":
    main()
