#!/usr/bin/env python3
"""영상 모델의 시간 정보가 평균 특징에도 남아 있나: 캡션의 동작 단어 대 물체 단어 예측 (2026-10-30, 자극 수준).

target: 영상마다 사람 캡션 20개 중 그 단어(어간)를 쓴 비율. 40개 영상 이상에서 나온 단어만.
  동작 단어 : 가장 흔한 표기가 -ing 이고 앞에 관사·수사가 오는 비율 < 0.2 (예: dancing, falling)
  물체 단어 : 앞에 관사·수사가 오는 비율 ≥ 0.5 이고 -ing 표기가 아님 (예: gun, dog)
각 시각 특징으로 ridge 6겹 OOF 예측 후 단어별 r. 캡션 특징은 target 을 만든 자료라 넣지 않는다.
출력: <OUT>/12_feature_overlap/{action_object_words.tsv, action_object_summary.tsv}
사용: python action_object_test.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "features"))
import feature_overlap as fo  # noqa: E402
import caption_vlm_qc as cq  # noqa: E402

MODELS = {"vjepa2_vitg_final": "V-JEPA 2 (영상)", "videomae": "VideoMAE (영상)", "dinov2": "DINOv2 (이미지)",
          "clip_vitl14": "CLIP (이미지)", "hk_vision1000": "VGG19 fc8 (이미지)"}
MIN_VIDEOS = 40


def main():
    split = pd.read_csv(fo.rs.bb.SPLIT, sep="\t")
    split = split[split.analysis_row & ~split.exclude_duplicate & (split.video_id <= 2185)].set_index("video_id")
    vids = split.index.values; fold = split.fold.values
    cap = pd.read_csv("/pscratch/sd/s/sjmoon/transfer/emobrain_stimulus_features_20261025/captions/caption_ck20.csv", encoding="utf-8-sig")
    cap = cap[cap.video_id.isin(vids)]
    texts = cap.description.fillna("").astype(str)
    noun = cq.noun_ratio(texts.tolist())
    surf = {}
    for t in texts:
        for s, w in cq.words(t):
            surf.setdefault(s, {}).setdefault(w, 0); surf[s][w] += 1
    rep = {s: max(ws, key=ws.get) for s, ws in surf.items()}
    share = {}
    for v, g in cap.groupby("video_id"):
        n = len(g)
        for s in {s for t in g.description.fillna("") for s, _ in cq.words(t)}:
            share.setdefault(s, {})[v] = share.get(s, {}).get(v, 0) + 0
        for t in g.description.fillna(""):
            for s in {s for s, _ in cq.words(t)}:
                share[s][v] += 1 / n
    kind = {}
    for s, d in share.items():
        if s == "person" or len(d) < MIN_VIDEOS:
            continue
        if rep[s].endswith("ing") and noun.get(s, 1) < 0.2:
            kind[s] = "action"
        elif noun.get(s, 0) >= 0.5 and not rep[s].endswith("ing"):
            kind[s] = "object"
    words = sorted(kind)
    T = np.array([[share[s].get(v, 0.0) for s in words] for v in vids])
    print(f"동작 단어 {sum(k == 'action' for k in kind.values())}개, 물체 단어 {sum(k == 'object' for k in kind.values())}개", flush=True)
    F = fo.rs.load_features(); out = []
    for key, lab in MODELS.items():
        X = F[key].loc[vids].values.astype(np.float64)
        P, _ = fo.ridge_oof(X, T, fold)
        r = [np.corrcoef(T[:, j], P[:, j])[0, 1] for j in range(T.shape[1])]
        out += [dict(model=lab, word=rep[s], kind=kind[s], n_videos=len(share[s]), r=rr) for s, rr in zip(words, r)]
        print(lab, flush=True)
    df = pd.DataFrame(out); od = fo.rs.OUT / "12_feature_overlap"
    df.to_csv(od / "action_object_words.tsv", sep="\t", index=False, float_format="%.4f")
    summ = df.groupby(["model", "kind"]).r.mean().unstack()
    summ["action_minus_object"] = summ.action - summ.object
    summ.to_csv(od / "action_object_summary.tsv", sep="\t", float_format="%.4f")
    print(summ.to_string())
    piv = df.pivot_table(index=["word", "kind"], columns="model", values="r")
    print(piv[piv.index.get_level_values("kind") == "action"].round(2).to_string())


if __name__ == "__main__":
    main()
