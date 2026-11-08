#!/usr/bin/env python3
"""뇌 → 특징 디코딩 지표 (2026-10-29). run_stage1.py 의 <특징>:content 단위가 저장한 OOF 예측을 다시 읽어 계산만 한다 (재학습 없음).

지표 (모든 중심화·기준은 바깥 fold 의 학습 평균)
  차원별      r_mean · r_median · frac_r_gt_0p1 : 특징 차원마다 예측과 실제의 Pearson r
              r2_mean · frac_r2_gt_0          : 차원마다 R² = 1 − SSE/SST(학습 평균 예측). 값 자체를 맞혔는지
  영상별      profile_r                       : 영상마다 예측 벡터와 실제 벡터의 상관 (차원 방향), 평균
  식별        pair_identification             : 같은 평가 fold 의 다른 영상 하나와 짝지었을 때 정답이 더 비슷한 비율 (우연 50%)
              top1_of_100 · top5_of_100       : 정답 + 같은 fold 무작위 오답 99개 중 정답 순위 1위·5위 이내 비율 (우연 1%·5%, 20회 추첨 평균)
비슷함은 학습 평균을 뺀 벡터의 cosine (기존 짝 구별과 같은 정의).
출력: <OUT>/04_brain_features/feature_decoding_metrics_by_subject.tsv, feature_decoding_metrics.tsv
사용: python feature_decoding_metrics.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import run_stage1 as rs  # noqa: E402

FEATURES = ["caption_human_mpnet", "clip_vitl14", "vjepa2_vitg_final", "dinov2", "hk_vision1000", "hk_semantic73", "videomae"]
KIND = {"caption_human_mpnet": "의미 (사람 캡션)", "clip_vitl14": "이미지 (언어 정렬)", "vjepa2_vitg_final": "영상",
        "dinov2": "이미지", "hk_vision1000": "이미지 (VGG19 fc8)", "hk_semantic73": "사람 개념 annotation", "videomae": "영상"}
N_CAND, N_DRAW, SEED = 100, 20, 0


def unit_cos(X):
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)


def metrics(Z, Zhat, fold, rng):
    sse, sst, rows_r, prof, pair, top1, top5 = 0, 0, [], [], [], [], []
    r = np.array([np.corrcoef(Z[:, j], Zhat[:, j])[0, 1] if Z[:, j].std() > 0 else np.nan for j in range(Z.shape[1])])
    sse = np.zeros(Z.shape[1]); sst = np.zeros(Z.shape[1])
    for f in np.unique(fold):
        tr, te = fold != f, fold == f
        mu = Z[tr].mean(0); a = Zhat[te] - mu; b = Z[te] - mu
        sse += ((Z[te] - Zhat[te]) ** 2).sum(0); sst += (b ** 2).sum(0)
        prof += [np.corrcoef(a[i], b[i])[0, 1] for i in range(len(a))]
        S = unit_cos(a) @ unit_cos(b).T; d = np.diag(S); n = len(S)
        pair += [(d[i] > np.delete(S[i], i)).mean() for i in range(n)]
        for i in range(n):
            others = np.delete(np.arange(n), i)
            for _ in range(N_DRAW):
                cand = rng.choice(others, N_CAND - 1, replace=False)
                rank = 1 + (S[i, cand] > d[i]).sum()
                top1.append(rank == 1); top5.append(rank <= 5)
    r2 = 1 - sse / np.where(sst > 0, sst, np.nan)
    return dict(n_dims=Z.shape[1], r_mean=np.nanmean(r), r_median=np.nanmedian(r), frac_r_gt_0p1=np.nanmean(r > 0.1),
                r2_mean=np.nanmean(r2), frac_r2_gt_0=np.nanmean(r2 > 0), profile_r=np.nanmean(prof),
                pair_identification=np.mean(pair), top1_of_100=np.mean(top1), top5_of_100=np.mean(top5))


def main():
    F = rs.load_features(); od = rs.OUT / "04_brain_features"; out = []
    for sub in ["01", "02", "03", "04", "05"]:
        rows, fold, *_ = rs.load_subject(sub); vids = rows.video_id.values; rng = np.random.default_rng(SEED)
        for name in FEATURES:
            p = od / "predictions" / f"sub-{sub}_{name}_brain_predicted.npy"
            Zhat = np.load(p).astype(np.float64); Z = F[name].loc[vids].values
            assert Zhat.shape == Z.shape, (p, Zhat.shape, Z.shape)
            out.append(dict(participant_id=f"sub-{sub}", feature=name, kind=KIND[name], **metrics(Z, Zhat, fold, rng)))
            print(out[-1], flush=True)
    df = pd.DataFrame(out)
    df.to_csv(od / "feature_decoding_metrics_by_subject.tsv", sep="\t", index=False, float_format="%.4f")
    g = df.groupby(["feature", "kind"], sort=False).mean(numeric_only=True).reset_index().sort_values("pair_identification", ascending=False)
    g.to_csv(od / "feature_decoding_metrics.tsv", sep="\t", index=False, float_format="%.4f")
    print(g.to_string(index=False))


if __name__ == "__main__":
    main()
