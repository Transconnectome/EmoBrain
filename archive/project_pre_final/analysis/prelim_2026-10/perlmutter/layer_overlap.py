#!/usr/bin/env python3
"""V-JEPA 2·CLIP 층별로 캡션과의 겹침과 정서 예측 기여 (2026-10-30, 자극 수준, 뇌 없음).

층별 특징: EmoViS study1_19·20 (V-JEPA 2 블록 4~40 중 10개, CLIP ViT-L/14 블록 2~24 중 12개, 공간 평균). 행 = 영상 1~2185.
층마다: 사람 캡션과의 CKA, VideoMAE(픽셀 복원 학습, 감각 쪽 기준)와의 CKA, 34개 범주 R² (층만), 사람 캡션 위에 더하는 정보와 둘 다 가진 정보 (feature_overlap.py 와 같은 stacking).
출력: <OUT>/12_feature_overlap/layerwise.tsv
사용: python layer_overlap.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import feature_overlap as fo  # noqa: E402

EMB = Path("/pscratch/sd/s/sjmoon/EmoViS/study1/results/00_embeddings")
LAYERS = {"V-JEPA 2": ("vjepa2_layerwise/vjepa2_layer_{:02d}.npy", range(4, 41, 4)),
          "CLIP": ("clip_layerwise/clip_layer_{:02d}.npy", range(2, 25, 2))}


def main():
    split = pd.read_csv(fo.rs.bb.SPLIT, sep="\t")
    split = split[split.analysis_row & ~split.exclude_duplicate & (split.video_id <= 2185)].set_index("video_id")
    vids = split.index.values; fold = split.fold.values
    F = fo.rs.load_features()
    cap = F["caption_human_mpnet"].loc[vids].values.astype(np.float64)
    mae = F["videomae"].loc[vids].values.astype(np.float64)
    _, Y, _ = fo.rs.cl.labels_for(vids)
    zc, zm = fo.zscore(cap), fo.zscore(mae)
    r2_cap = fo.r2(Y, *fo.ridge_oof(cap, Y, fold)); parts_cap = fo.stack_parts(cap, Y, fold)
    base = np.zeros_like(Y)
    for f in np.unique(fold):
        base[fold == f] = Y[fold != f].mean(0)
    rows = []
    for model, (pat, layers) in LAYERS.items():
        for L in layers:
            X = np.load(EMB / pat.format(L))[vids - 1].astype(np.float64); z = fo.zscore(X)
            r2_l = fo.r2(Y, *fo.ridge_oof(X, Y, fold))
            r2_b = fo.r2(Y, fo.stacked(fo.stack_parts(X, Y, fold), parts_cap, Y, fold), base)
            rows.append(dict(model=model, layer=L, cka_caption=fo.cka(z, zc), cka_videomae=fo.cka(z, zm),
                             r2_layer=r2_l.mean(), r2_caption=r2_cap.mean(), r2_both=r2_b.mean(),
                             unique_layer=(r2_b - r2_cap).mean(), shared=(r2_l + r2_cap - r2_b).mean()))
            print(rows[-1], flush=True)
    out = fo.rs.OUT / "12_feature_overlap" / "layerwise.tsv"
    pd.DataFrame(rows).to_csv(out, sep="\t", index=False, float_format="%.4f")
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
