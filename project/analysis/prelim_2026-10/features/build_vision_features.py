#!/usr/bin/env python3
"""다른 시각 모델 임베딩을 랩서버 표준 형식(<이름>.npy + <이름>_video_id.tsv)으로 바꾼다 (2026-10-28).

  clip_vitl14 : CLIP ViT-L/14 영상 인코더, 3 프레임 pooler 평균 (1024)
  dinov2      : DINOv2, 3 프레임 CLS 평균 (1536)
  videomae    : VideoMAE, 16 프레임 토큰 평균 (1280)
원본은 자극 묶음 embeddings/ 의 *_pretrained_final.npy (2185 행 = 영상 1~2185). 2186~2196 은 canonical 영상(1~11) 행을 복사.
Horikawa VGG19 1000 범주(hk_vision1000)는 run_stage1.load_features 가 Horikawa metadata 에서 바로 읽는다.
사용: python build_vision_features.py --bundle <자극 묶음> --out <특징 폴더>
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import build_lab_features as blf  # noqa: E402

MODELS = {"clip_vitl14": "clip/clip_pretrained_final.npy", "dinov2": "dinov2/dinov2_pretrained_final.npy",
          "videomae": "videomae/videomae_pretrained_final.npy"}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--bundle", type=Path, required=True); ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    canon = blf.read_crosswalk(a.bundle)
    with open(a.out / "MANIFEST.tsv", "a") as man:
        for name, rel in MODELS.items():
            d = (a.bundle / "embeddings" / rel).parent
            assert np.array_equal(np.load(d / "stim_idx.npy"), np.arange(2185)), f"{name} 행 순서가 영상 1~2185 가 아님"
            X = blf.expand_2185(np.load(a.bundle / "embeddings" / rel), canon).astype(np.float32)
            assert np.isfinite(X).all()
            np.save(a.out / f"{name}.npy", X)
            pd.DataFrame(dict(video_id=np.arange(1, blf.N_VIDEOS + 1))).to_csv(a.out / f"{name}_video_id.tsv", sep="\t", index=False)
            man.write(f"{name}\t{X.shape[0]}\t{X.shape[1]}\t{blf.sha256(a.out / f'{name}.npy')}\tembeddings/{rel}; 2186~2196 = canonical 1~11 행\n")
            print(name, X.shape)


if __name__ == "__main__":
    main()
