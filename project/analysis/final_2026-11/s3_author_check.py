#!/usr/bin/env python3
"""S3: 추출한 DeBERTa와 TimeSformer 특징을 저자 공개 특징(figshare 25808179 feature.zip)과 비교한다 (2026-11-05). 뇌 반응과 정서 정답은 읽지 않는다.

사용: s3_author_check.py (s3_collect.py 뒤). 출력: manifests/s3/author_feature_check.tsv
DeBERTa는 같아야 한다(공개 코드로 층과 token 평균을 확인함). TimeSformer는 공개 코드에 추출 부분이 없어 같다고 기대하지 않고 값만 적는다(O14).
"""
import h5py
import numpy as np
import pandas as pd

import s3_common as c

AUTHOR = c.Path("/pscratch/sd/s/sjmoon/atlas_sources/mindcaptioning_figshare/author_features/feature/video")
OUTFILE = c.CODE_DIR / "manifests/s3/author_feature_check.tsv"


def author(model, layer):
    with h5py.File(AUTHOR / model / f"layer{layer:02d}.mat", "r") as h:
        return np.array(h["feat"], np.float64).T


def compare(name, ours, a, layer):
    if ours.shape != a.shape:
        raise SystemExit(f"{name} 층 {layer}: 차원이 다르다 {ours.shape} {a.shape}")
    # NaN은 어떤 비교도 거짓으로 만들어 성공처럼 보인다. 입력부터 거절한다
    if not np.isfinite(ours).all() or not np.isfinite(a).all():
        raise SystemExit(f"{name} 층 {layer}: 우리 특징이나 저자 특징에 NaN이나 무한대가 있다")
    x, y = ours - ours.mean(1, keepdims=True), a - a.mean(1, keepdims=True)
    constant = ((x**2).sum(1) == 0) | ((y**2).sum(1) == 0)  # 상수 벡터는 상관을 정의할 수 없다. 따로 세고 r 요약에서 뺀다
    keep = ~constant
    x, y = x[keep], y[keep]
    r = (x * y).sum(1) / np.sqrt((x**2).sum(1) * (y**2).sum(1))
    nxt = np.roll(y, -1, axis=0)
    rn = (x * nxt).sum(1) / np.sqrt((x**2).sum(1) * (nxt**2).sum(1))
    return dict(model=name, layer=layer, n_videos=int(len(constant)), n_constant=int(constant.sum()), r_same_min=float(r.min()), r_same_median=float(np.median(r)), r_next_video_median=float(np.median(rn)), max_abs_diff=float(np.abs(ours - a).max()))


def main():
    rows = []
    d = np.load(c.OUT / "deberta/video_mean.npy", mmap_mode="r")
    for i, l in zip([5, 11, 17, 23], [6, 12, 18, 24]):
        rows.append(compare("deberta-large", np.asarray(d[:, i], np.float64), author("deberta-large", l), l))
    t = np.load(c.OUT / "timesformer/blocks.npy", mmap_mode="r")
    for i, l in zip([2, 5, 8, 11], [3, 6, 9, 12]):
        rows.append(compare("timesformer", np.asarray(t[:, i], np.float64), author("timesformer", l), l))
    OUTFILE.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(OUTFILE, sep="\t", index=False, float_format="%.8g")
    print(df.round(6).to_string(index=False))
    bad = df[(df.model == "deberta-large") & ~(df.max_abs_diff <= 1e-3)]  # NaN도 실패로 잡히게 부정으로 쓴다
    if len(bad):
        raise SystemExit("DeBERTa가 저자 특징과 다르다")


if __name__ == "__main__":
    main()
