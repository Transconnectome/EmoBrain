#!/usr/bin/env python3
"""캡션의 평가어(cute, scary 등)가 캡션 우위를 얼마나 만드나, 시각 모델은 평가어를 맞히나 (2026-10-31, 자극 수준).

1. 평가어를 지운 캡션: caption_human_noemo_mpnet (build_caption_noemo.py, 정서·평가어 181개 삭제, cute·beautiful·scary 포함).
   34개 범주 R² 를 원 캡션과 비교하고, V-JEPA 2 와의 분할 (V-JEPA 2 에만 있는 정보 / 둘 다 / 캡션에만 있는 정보) 을 다시 낸다.
2. 평가어 예측: 영상마다 사람 캡션 20개 중 그 평가어를 쓴 비율을 시각 특징으로 ridge 6겹 OOF 예측한 r.
   20개 영상 이상에 나온 평가어만. 비교 기준으로 action_object_test.py 의 동작·물체 단어 평균 r 을 함께 적는다.
출력: <OUT>/12_feature_overlap/{caption_noemo_partition.tsv, caption_noemo_partition_by_category.tsv, evaluative_words.tsv}
사용: python evaluative_words_test.py
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import feature_overlap as fo  # noqa: E402

EVAL = ("cute adorable sweet lovely beautiful gorgeous pretty funny hilarious silly scary creepy terrifying frightening horrifying "
        "disgusting gross nasty dirty ugly weird strange happy sad angry aggressive dangerous violent brutal painful cruel poor weak "
        "sick dead peaceful calm romantic sexy hot excited").split()
VISUAL = {"vjepa2_vitg_final": "V-JEPA 2 (영상)", "videomae": "VideoMAE (영상)", "dinov2": "DINOv2 (이미지)",
          "clip_vitl14": "CLIP (이미지)", "hk_vision1000": "VGG19 fc8 (이미지)"}
MIN_VIDEOS = 20


def main():
    od = fo.rs.OUT / "12_feature_overlap"
    split = pd.read_csv(fo.rs.bb.SPLIT, sep="\t")
    split = split[split.analysis_row & ~split.exclude_duplicate & (split.video_id <= 2185)].set_index("video_id")
    vids = split.index.values; fold = split.fold.values
    F = fo.rs.load_features()
    cats, Y, _ = fo.rs.cl.labels_for(vids)
    base = np.zeros_like(Y)
    for f in np.unique(fold):
        base[fold == f] = Y[fold != f].mean(0)
    X = {n: F[n].loc[vids].values.astype(np.float64) for n in ["caption_human_mpnet", "caption_human_noemo_mpnet", "vjepa2_vitg_final", "clip_vitl14"]}
    parts = {n: fo.stack_parts(x, Y, fold) for n, x in X.items()}
    single = {n: fo.r2(Y, fo.stacked_one(p, Y, fold), base) for n, p in parts.items()}
    rows, bycat = [], []
    for s in ["caption_human_mpnet", "caption_human_noemo_mpnet"]:
        for v in ["vjepa2_vitg_final", "clip_vitl14"]:
            rb = fo.r2(Y, fo.stacked(parts[v], parts[s], Y, fold), base); rv, rs_ = single[v], single[s]
            rows.append(dict(caption=s, visual=VISUAL[v], r2_visual=rv.mean(), r2_caption=rs_.mean(), r2_both=rb.mean(),
                             visual_only=(rb - rs_).mean(), caption_only=(rb - rv).mean(), common=(rv + rs_ - rb).mean()))
            bycat += [dict(caption=s, visual=VISUAL[v], category=c, r2_visual=rv[k], r2_caption=rs_[k], r2_both=rb[k]) for k, c in enumerate(cats)]
    pd.DataFrame(rows).to_csv(od / "caption_noemo_partition.tsv", sep="\t", index=False, float_format="%.4f")
    pd.DataFrame(bycat).to_csv(od / "caption_noemo_partition_by_category.tsv", sep="\t", index=False, float_format="%.4f")
    print(pd.DataFrame(rows).to_string(index=False))

    cap = pd.read_csv("/pscratch/sd/s/sjmoon/transfer/emobrain_stimulus_features_20261025/captions/caption_ck20.csv", encoding="utf-8-sig")
    cap = cap[cap.video_id.isin(vids)]
    T, words = [], []
    for w in EVAL:
        pat = re.compile(r"\b" + w + r"\b", re.I)
        share = cap.assign(h=cap.description.fillna("").str.contains(pat)).groupby("video_id").h.mean().reindex(vids).fillna(0).values
        if (share > 0).sum() >= MIN_VIDEOS:
            T.append(share); words.append(w)
    T = np.array(T).T; out = []
    for key, lab in VISUAL.items():
        P, _ = fo.ridge_oof(F[key].loc[vids].values.astype(np.float64), T, fold)
        out += [dict(model=lab, word=w, n_videos=int((T[:, j] > 0).sum()), r=np.corrcoef(T[:, j], P[:, j])[0, 1]) for j, w in enumerate(words)]
    df = pd.DataFrame(out); df.to_csv(od / "evaluative_words.tsv", sep="\t", index=False, float_format="%.4f")
    print(df.pivot_table(index="word", columns="model", values="r").round(2).to_string())
    print(df.groupby("model").r.mean().round(3).to_string())


if __name__ == "__main__":
    main()
