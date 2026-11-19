#!/usr/bin/env python3
"""S2 캡션 구역(D-바, 상황 묶음 빼고 시험. 11/18 석진 님 "뿌려놓고 돌려놓긴 하자"; 06 5절 D-바, 6절 "6-2와 같은 형식"). CPU, 1분 안쪽.

6-2의 내용 구역(4-3, s2_manifest.stage_blocks)은 이름표 73개로 묶었다. D-바는 캡션으로 묶은 상황 하나를 통째로 학습에서 뺀다.
절차는 stage_blocks와 같고 묶는 공간만 다르다.
- 공간: Caption feature 정서어 제거판(deberta_no_emotion_words/target, 4,096차원). 정서 단어를 뺀 캡션이라 묶음이 정서 평정 자체로 나뉘지 않는다.
  개발 영상에서 차원마다 표준화하고 PCA 50개(random_state 0)로 줄인 뒤 묶는다. 4,096차원을 그대로 쓰면 거리가 대부분의 작은 차원에 좌우되기 때문이다(설계 선택).
- 묶음: k-means 5개(n_init 10, random_state 0, 4-3과 같은 수), 번호는 크기 순. 같은 설정으로 두 번 돌려 배정이 같은지 확인한다.
- 분할: 4-3의 표와 같다(s4_common.zone_sets). 시험 = 시험 fold의 그 묶음 영상, 구역 제외 = 나머지 fold에서 그 묶음을 뺀 영상,
  학습량 대조 = 학습 fold와 검증 fold에서 구역 제외와 같은 수를 무작위로 뽑은 영상(그 묶음을 후보에서 빼지 않음). 대조 표본의 seed는 4-3과 다른 값이다.
- 거리 점검: 시험 영상과 가장 가까운 학습 영상의 거리(PCA 공간의 제곱 평균 제곱근)가 구역 제외에서 대조보다 늘어나는지 묶음, fold마다 적는다(4-3과 같은 지표).
- 함께 적는 것: 묶음마다 크기, 중심에 가장 가까운 영상 5개와 그 첫 캡션, 4-3 이름표 구역과의 교차표, 정서별 0이 아닌 학습 영상 수, 참가자별 block 수.
정서 정답은 0이 아닌 학습 영상 수에만 쓴다. 묶음과 거리에는 쓰지 않는다.
출력(manifests/s2/, 대표 캡션 원문은 레포 밖 <output_root>/s2_manifest/caption_blocks_samples.tsv): caption_blocks_assignment.tsv, caption_block_control_samples.tsv, caption_blocks.tsv, caption_block_distance.tsv, caption_block_nonzero.tsv,
  caption_block_participant_counts.tsv, caption_block_label_zone_crosstab.tsv, caption_blocks_info.json
사용: s2_caption_blocks.py
"""
import hashlib
import json

import numpy as np
import pandas as pd
import sklearn
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

import s2_manifest as M2
import s3_common as c3

N_PCA = 50
SEED_CAPTION_CONTROL = 20261118  # 학습량 대조 표본. 4-3(20261104)과 다르게 둔다
SEED_CAPTION_DISTANCE = 20261119  # 거리 점검의 20번 반복
FEATURE = c3.OUT / "deberta_no_emotion_words" / "target.npy"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    D = M2.load_split()
    vids = D.video_id.to_numpy()
    F = np.load(FEATURE)
    if F.shape[0] != 2196:
        raise SystemExit(f"캡션 특징의 행이 2196개가 아니다: {F.shape}")
    Xd = F[vids - 1].astype(np.float64)
    sd = Xd.std(0)
    Z = (Xd - Xd.mean(0)) / np.where(sd > 0, sd, 1)
    pca = PCA(n_components=N_PCA, random_state=0).fit(Z)
    X = pca.transform(Z)
    fit = lambda: KMeans(n_clusters=M2.N_BLOCKS, n_init=10, random_state=0).fit_predict(X)
    lab = fit()
    assert np.array_equal(lab, fit()), "같은 설정으로 다시 돌린 묶음 배정이 다르다"
    order = pd.Series(lab).value_counts().index.tolist()
    block = np.array([order.index(x) + 1 for x in lab])
    D["block"] = block
    M2.tsv(D[["video_id", "fold", "block"]], "caption_blocks_assignment.tsv")
    cap = pd.read_csv(c3.CAPTIONS, encoding="utf-8-sig").groupby("video_id").description.first()
    rows = []
    for z in range(1, M2.N_BLOCKS + 1):
        m = block == z
        near = vids[m][np.argsort(((X[m] - X[m].mean(0)) ** 2).sum(1))[:5]]
        rows.append(dict(block=z, n_videos=int(m.sum()), sample_videos=",".join(map(str, near)), sample_captions=" | ".join(str(cap.get(int(v), "")) for v in near)))
    M2.tsv(pd.DataFrame(rows).drop(columns="sample_captions"), "caption_blocks.tsv")  # 캡션 원문은 레포 밖에만 둔다
    M2.BIG.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(M2.BIG / "caption_blocks_samples.tsv", sep="\t", index=False)
    print(pd.DataFrame(rows)[["block", "n_videos", "sample_videos"]].to_string(index=False))
    zones = pd.read_csv(M2.where("content_blocks_assignment.tsv"), sep="\t").set_index("video_id").block.reindex(vids).to_numpy()
    ct = pd.crosstab(pd.Series(block, name="caption_block"), pd.Series(zones, name="label_zone"))
    M2.tsv(ct.reset_index(), "caption_block_label_zone_crosstab.tsv")
    print("캡션 묶음 × 이름표 구역\n", ct.to_string())
    emo, Y = M2.labels34()
    content = D.content_id.to_numpy()
    fold = D.fold.to_numpy()
    P = pd.read_csv(M2.where("participant_blocks_hk.tsv"), sep="\t")
    dist, ctrl, nz, counts = [], [], [], []
    for z in range(1, M2.N_BLOCKS + 1):
        for k in range(1, M2.K + 1):
            val = k % M2.K + 1  # H2: 시험 fold의 다음 fold가 검증
            te = (fold == k) & (block == z)
            tr_pool, va_pool = (fold != k) & (fold != val), fold == val
            tr_ex, va_ex = tr_pool & (block != z), va_pool & (block != z)
            n_tr, n_va = int(tr_ex.sum()), int(va_ex.sum())
            idx_tr, idx_va = np.flatnonzero(tr_pool), np.flatnonzero(va_pool)
            d_ex = M2.label_distance(X[te], X[tr_ex]).min(1)
            rng = np.random.default_rng([SEED_CAPTION_DISTANCE, z, k])
            d_ct = np.mean([M2.label_distance(X[te], X[rng.choice(idx_tr, n_tr, replace=False)]).min(1) for _ in range(20)], 0)
            rng = np.random.default_rng([SEED_CAPTION_CONTROL, z, k])
            p_tr = np.sort(rng.choice(idx_tr, n_tr, replace=False))
            p_va = np.sort(rng.choice(idx_va, n_va, replace=False))
            d_fx = M2.label_distance(X[te], X[p_tr]).min(1)
            dist.append(dict(block=z, fold=k, val_fold=val, n_test=int(te.sum()), n_train_excluded=n_tr, n_val_excluded=n_va, median_excluded=float(np.median(d_ex)), median_control=float(np.median(d_ct)),
                             ratio=float(np.median(d_ex) / np.median(d_ct)), frac_test_farther=float((d_ex > d_ct + M2.TIE_TOL).mean()), median_control_fixed=float(np.median(d_fx)), ratio_fixed=float(np.median(d_ex) / np.median(d_fx))))
            ctrl += [dict(block=z, fold=k, role="train", video_id=int(v)) for v in vids[p_tr]] + [dict(block=z, fold=k, role="val", video_id=int(v)) for v in vids[p_va]]
            yy = dict(ex_tr=Y[content[tr_ex] - 1], ct_tr=Y[content[p_tr] - 1])
            nz += [dict(block=z, fold=k, emotion=e, n_nonzero_excluded=int((yy["ex_tr"][:, i] > 0).sum()), n_nonzero_control=int((yy["ct_tr"][:, i] > 0).sum())) for i, e in enumerate(emo)]
            sets = dict(excluded_train=vids[tr_ex], excluded_val=vids[va_ex], control_train=vids[p_tr], control_val=vids[p_va], test=vids[te])
            for pp, g in P.groupby("participant"):
                have = set(g.video_id)
                counts.append(dict(block=z, fold=k, participant=pp, **{f"n_{name}": int(sum(int(v) in have for v in vv)) for name, vv in sets.items()}))
    Dt = pd.DataFrame(dist)
    M2.tsv(Dt, "caption_block_distance.tsv")
    M2.tsv(pd.DataFrame(ctrl), "caption_block_control_samples.tsv")
    M2.tsv(pd.DataFrame(nz), "caption_block_nonzero.tsv")
    M2.tsv(pd.DataFrame(counts), "caption_block_participant_counts.tsv")
    print(Dt.groupby("block").agg(n_test_min=("n_test", "min"), n_test_max=("n_test", "max"), ratio_min=("ratio", "min"), ratio_med=("ratio", "median"), farther=("frac_test_farther", "mean")).round(3).to_string())
    N = pd.DataFrame(nz)
    print("정서별 0이 아닌 학습 영상 수 최솟값(구역 제외):", N.groupby("block").n_nonzero_excluded.min().to_dict())
    info = dict(code="src/s2_caption_blocks.py", code_sha256=sha(__file__), feature=str(FEATURE.relative_to(c3.OUT)), feature_sha256=sha(FEATURE), n_pca=N_PCA, pca_explained=float(pca.explained_variance_ratio_.sum()),
                kmeans=dict(n_clusters=M2.N_BLOCKS, n_init=10, random_state=0), seed_control=SEED_CAPTION_CONTROL, seed_distance=SEED_CAPTION_DISTANCE, sklearn=sklearn.__version__,
                n_ratio_le_1=int((Dt.ratio <= 1).sum()), output_sha256={f: sha(M2.where(f)) for f in ("caption_blocks_assignment.tsv", "caption_block_control_samples.tsv")})
    (M2.OUT / "caption_blocks_info.json").write_text(json.dumps(info, indent=1, ensure_ascii=False))
    print(json.dumps({k: info[k] for k in ("pca_explained", "n_ratio_le_1")}), flush=True)


if __name__ == "__main__":
    main()
