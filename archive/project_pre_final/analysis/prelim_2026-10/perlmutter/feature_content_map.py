#!/usr/bin/env python3
"""V-JEPA 2 와 사람 캡션이 각각 무엇을 잡아냈나 (2026-10-30, 자극 수준, 뇌 없음).

1. 감정별: V-JEPA 2 에만 있는 정보, 둘 다 가진 정보, 캡션에만 있는 정보 (feature_overlap.py 의 emotion_partition_by_category.tsv 를 읽음).
   저수준 특징(EmoViS Sadeghi 방식 142차원: RGB·색상·Gabor·대칭성·AlexNet conv1, 정지 화면이라 움직임 없음) 이 캡션 위에 더하는 정보도 같은 stacking 으로 계산 (단독도 같은 보정을 거침).
2. 장면 개념별: Horikawa 의미 73 (사람이 붙인 장면 개념, 평정자 비율) 을 V-JEPA 2, VideoMAE, CLIP, DINOv2, VGG19 fc8, 캡션, 저수준 특징으로 각각 ridge 예측 (6겹 OOF) 한 r.
출력: <OUT>/12_feature_overlap/{emotion_partition_lowlevel.tsv, concept_prediction.tsv}. 그림은 feature_content_figures.py (matplotlib 이 있는 환경)
사용: python feature_content_map.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import feature_overlap as fo  # noqa: E402

LOW = Path("/pscratch/sd/s/sjmoon/EmoViS/study1/results/00_embeddings/sadeghi/sadeghi_low_level.npy")


def main():
    od = fo.rs.OUT / "12_feature_overlap"
    split = pd.read_csv(fo.rs.bb.SPLIT, sep="\t")
    split = split[split.analysis_row & ~split.exclude_duplicate & (split.video_id <= 2185)].set_index("video_id")
    vids = split.index.values; fold = split.fold.values
    F = fo.rs.load_features()
    V = F["vjepa2_vitg_final"].loc[vids].values.astype(np.float64)
    S = F["caption_human_mpnet"].loc[vids].values.astype(np.float64)
    C = F["hk_semantic73"].loc[vids]; concepts = list(C.columns); C = C.values.astype(np.float64)
    low = np.load(LOW).astype(np.float64)[vids - 1]
    cats, Y, _ = fo.rs.cl.labels_for(vids)
    base = np.zeros_like(Y)
    for f in np.unique(fold):
        base[fold == f] = Y[fold != f].mean(0)

    pl, ps = fo.stack_parts(low, Y, fold), fo.stack_parts(S, Y, fold)
    r2_low, r2_cap = fo.r2(Y, fo.stacked_one(pl, Y, fold), base), fo.r2(Y, fo.stacked_one(ps, Y, fold), base)
    r2_both = fo.r2(Y, fo.stacked(pl, ps, Y, fold), base)
    lowtab = pd.DataFrame(dict(category=cats, r2_lowlevel=r2_low, r2_caption=r2_cap, r2_both=r2_both,
                               lowlevel_only=r2_both - r2_cap, caption_only=r2_both - r2_low, common=r2_low + r2_cap - r2_both))
    lowtab.to_csv(od / "emotion_partition_lowlevel.tsv", sep="\t", index=False, float_format="%.4f")

    def concept_r(X):
        P, _ = fo.ridge_oof(X, C, fold)
        return np.array([np.corrcoef(C[:, j], P[:, j])[0, 1] for j in range(C.shape[1])])
    ctab = pd.DataFrame(dict(concept=concepts, r_vjepa2=concept_r(V), r_caption=concept_r(S), r_lowlevel=concept_r(low),
                             prevalence=C.mean(0)))
    for n in ["videomae", "clip_vitl14", "dinov2", "hk_vision1000"]:
        ctab[f"r_{n}"] = concept_r(F[n].loc[vids].values.astype(np.float64))
    ctab["vjepa2_minus_caption"] = ctab.r_vjepa2 - ctab.r_caption
    ctab.sort_values("vjepa2_minus_caption", ascending=False).to_csv(od / "concept_prediction.tsv", sep="\t", index=False, float_format="%.4f")

    print(lowtab.sort_values("r2_lowlevel", ascending=False).head(10).to_string(index=False))
    print(ctab.sort_values("vjepa2_minus_caption", ascending=False).to_string(index=False))


if __name__ == "__main__":
    main()
