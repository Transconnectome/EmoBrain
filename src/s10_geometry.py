#!/usr/bin/env python3
"""S10 네트워크별 정서 표현의 형식(geometry) 탐색 (11/16 석진 님 결정. 결과를 본 뒤 더한 탐색 분석, 01 기록 칸). GPU 없음.

묻는 것: 정서 관련 뇌 정보가 네트워크마다 다른 형식으로 있는가. 내용을 넘어 일반화하는 저차원 축(valence 같은 차원)인가,
내용에 묶인 고차원 범주 구분인가. 시간 순서(처리 단계)는 이 자료로 볼 수 없다. 영상마다 반응이 하나이기 때문이다.

decoder(모든 분석이 같다): 네트워크(CAB-NP 13묶음, S2 roi_table의 group)에 든 ROI의 voxel 합집합만으로 s5_common.main_version(ridge,
학습 행으로 표준화, 목표마다 검증 fold의 r로 λ 선택, λ 후보 O18). 목표는 정서 34개와 정서 차원 14개(사람 평정).
- 검증 자료에서 정답이 상수라 λ를 고를 수 없는 목표는 그 분할에서 예측을 NaN으로 두고 채점에서 뺀다(그 수를 남긴다).

fit(참가자마다)
- outer: 바깥 fold k(H2 역할)마다 시험 fold 예측. 영상마다 한 번씩 시험된다. (b), (c)가 쓴다.
- zone: 6-2의 분할(s4_common.zone_sets. 구역 b의 fold k 영상을 시험, 구역 b와 fold k를 뺀 영상으로 학습)과 학습량 대조(같은 수를 무작위로 뺌).
  학습 자료 가운데 H2 검증 fold의 영상으로 λ를 고른다. 구역 b의 영상이 구역 5개 × fold 6개에서 한 번씩 시험되므로 방식(excluded, control)마다
  모든 개발 영상의 예측이 하나씩 생긴다. (a)가 쓴다.
저장(레포 밖 --out): fit/sub-0X.npz(video_id, 네트워크 이름, outer_pred 네트워크 × 영상 × 48, zone_excluded_pred, zone_control_pred, nan_counts)와 done.json.
summarize: 다섯 명의 fit을 읽어 (a)(b)(c)의 표를 낸다. 규칙은 summarize 함수의 머리말.
사용: s10_geometry.py fit --participant 01 --out <폴더> --design-freeze <커밋> [--threads 16]
      s10_geometry.py summarize --out <폴더> --design-freeze <커밋>
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

import s4_common as c
import s5_common as d5

N_BLOCKS = 5
KINDS = ("excluded", "control")
VAD = ("valence", "arousal", "dominance")


def targets(split, video_id):
    y, ecols = c.load_scores(split, "emotions")
    d, dcols = c.load_scores(split, "dimensions")
    names = pd.read_csv(c.LABEL_MAP, sep="\t").set_index("score_col").loc[ecols, "name"].tolist()
    dnames = [x.replace("_score", "") for x in dcols]
    T = np.concatenate([np.asarray(y, np.float64), np.asarray(d, np.float64)], 1)
    return d5.align(T, split, video_id), names, dnames


def network_positions(brain):
    """네트워크 이름 -> brain.X의 열 위치(그 네트워크 ROI들의 voxel 합집합)."""
    roi = pd.read_csv(c.S2 / "roi_table.tsv", sep="\t").sort_values("roi_index")
    if len(roi) != len(brain.roi_positions):
        raise ValueError("ROI 표의 ROI 수가 뇌 자료와 다르다")
    out = {}
    for g, rows in roi.groupby("group", sort=False):
        out[g] = np.unique(np.concatenate([brain.roi_positions[int(i)] for i in rows.roi_index]))
    return out


def ridge(x, T, tr, va, te):
    """s5_common.main_version. 검증 자료에서 정답이 상수인 목표는 NaN으로 둔다. 돌려주는 값: 시험 예측(numpy), NaN으로 둔 목표 수."""
    keep = (T[va].std(0) > 0) & (T[tr].std(0) > 0)
    out = np.full((len(te), T.shape[1]), np.nan)
    if keep.any():
        y = d5.as_tensor(T[:, keep], "cpu")
        p, _ = d5.main_version(x, y, tr, va, te)
        out[:, keep] = p.numpy()
    return out, int((~keep).sum())


def fit(s, out, split, threads):
    torch.set_num_threads(threads)
    brain = d5.load_brain(s, split)
    T, names, dnames = targets(split, brain.video_id)
    nets = network_positions(brain)
    vid = np.asarray(brain.video_id)
    row_of = {v: i for i, v in enumerate(vid.tolist())}
    fold = np.asarray(brain.fold)
    blocks = pd.read_csv(c.S2 / "content_blocks_assignment.tsv", sep="\t")
    control = pd.read_csv(c.S2 / "content_block_control_samples.tsv", sep="\t")
    n, m = len(vid), T.shape[1]
    outer = np.full((len(nets), n, m), np.nan, np.float32)
    zone = {k: np.full((len(nets), n, m), np.nan, np.float32) for k in KINDS}
    nan_counts = []
    X = torch.as_tensor(np.asarray(brain.X))
    for j, (g, pos) in enumerate(nets.items()):
        started = time.time()
        x = X[:, torch.as_tensor(pos)].double()
        for k in range(1, c.N_FOLDS + 1):
            r = c.roles(k)
            tr, va, te = np.flatnonzero(np.isin(fold, r["train"])), np.flatnonzero(fold == r["val"]), np.flatnonzero(fold == k)
            p, bad = ridge(x, T, tr, va, te)
            outer[j, te] = p
            nan_counts.append(dict(network=g, analysis="outer", block=0, fold=k, kind="", n_nan_targets=bad))
            for b in range(1, N_BLOCKS + 1):
                for kind in KINDS:
                    train_ids, test_ids = c.zone_sets(split, b, k, kind, blocks=blocks, control=control)
                    tri = np.array([row_of[v] for v in train_ids if v in row_of])
                    tei = np.array([row_of[v] for v in test_ids if v in row_of])
                    if not len(tei):
                        continue
                    tr_z, va_z = tri[np.isin(fold[tri], r["train"])], tri[fold[tri] == r["val"]]
                    p, bad = ridge(x, T, tr_z, va_z, tei)
                    zone[kind][j, tei] = p
                    nan_counts.append(dict(network=g, analysis="zone", block=b, fold=k, kind=kind, n_nan_targets=bad))
        print(f"sub-{s} {g} ({len(pos)} voxel) {time.time() - started:.0f}초", flush=True)
    out = Path(out) / "fit"
    out.mkdir(parents=True, exist_ok=True)
    np.savez(out / f"sub-{s}.npz", video_id=vid, networks=np.array(list(nets)), n_voxels=np.array([len(p) for p in nets.values()]),
             targets=np.array(names + dnames), outer_pred=outer, zone_excluded_pred=zone["excluded"], zone_control_pred=zone["control"])
    pd.DataFrame(nan_counts).to_csv(out / f"sub-{s}_nan_counts.tsv", sep="\t", index=False)


def colr(a, b):
    """열마다 Pearson r. NaN 행은 열마다 뺀다."""
    out = np.full(a.shape[1], np.nan)
    for i in range(a.shape[1]):
        ok = np.isfinite(a[:, i]) & np.isfinite(b[:, i])
        if ok.sum() > 2 and a[ok, i].std() > 0 and b[ok, i].std() > 0:
            out[i] = np.corrcoef(a[ok, i], b[ok, i])[0, 1]
    return out


def vad_pairs(split, D, dnames):
    """같은 바깥 fold 안에서 표준화한 VAD 공간의 최근접 영상(자기 자신 뺌). 순서 없는 쌍으로 겹침을 지운다. 사람 평정만 쓰고 모델 결과는 보지 않는다."""
    idx = [dnames.index(v) for v in VAD]
    z = (D[:, idx] - D[:, idx].mean(0)) / D[:, idx].std(0)
    vid = split.video_id.to_numpy()
    pairs = set()
    for k in range(1, c.N_FOLDS + 1):
        rows = np.flatnonzero(split.fold.to_numpy() == k)
        zz = z[rows]
        d2 = ((zz[:, None] - zz[None]) ** 2).sum(-1)
        np.fill_diagonal(d2, np.inf)
        nn = d2.argmin(1)
        for a, b in zip(rows, rows[nn]):
            pairs.add((int(min(vid[a], vid[b])), int(max(vid[a], vid[b])), k))
    return pd.DataFrame(sorted(pairs), columns=["video_a", "video_b", "fold"])


def summarize(out, split):
    """(a) 내용을 넘는 일반화: 방식마다 구역별로 영상에 걸친 r을 내고 구역 5개를 평균한다. 일반화 비율 = r(구역 제외) / r(학습량 대조), 차이도 낸다.
    (b) 차원 환원성: 바깥 fold마다 학습 fold 4개 + 검증 fold의 실제 평정으로 차원 → 정서 선형 규칙(최소제곱)을 맞추고, 그 fold의 뇌에서 읽은
        차원 예측(보정 없음)에 적용한다. 정서별 r(직접) − r(차원 경유). 차원은 14개판과 VAD 3개판.
    (c) 정서가 비슷한 영상 사이의 범주 구분: VAD 최근접 쌍과 이름표 73개 최근접 쌍(S2 pairs_unordered)에서 r(직접 예측의 차이, 실제 평정의 차이).
    모두 참가자, 네트워크, 정서마다 내고 5명 평균을 더한다. 구간과 검정은 아직 없다(탐색)."""
    out = Path(out)
    fits = {}
    for s in d5.HK:
        z = np.load(out / "fit" / f"sub-{s}.npz", allow_pickle=True)
        fits[s] = {k: z[k] for k in z.files}
    tnames = fits[d5.HK[0]]["targets"].tolist()
    nets = fits[d5.HK[0]]["networks"].tolist()
    ne = 34
    names, dnames = tnames[:ne], tnames[ne:]
    vadi = [dnames.index(v) for v in VAD]
    Tall, _, _ = targets(split, split.video_id.to_numpy())
    blocks = pd.read_csv(c.S2 / "content_blocks_assignment.tsv", sep="\t")
    block_of = dict(zip(blocks.video_id, blocks.block))
    fold_of = dict(zip(split.video_id, split.fold))
    pos_all = {v: i for i, v in enumerate(split.video_id.tolist())}
    vpairs = vad_pairs(split, Tall[:, ne:], dnames)
    cpairs = pd.read_csv(c.S2 / "pairs_unordered.tsv", sep="\t")
    rows_a, rows_b, rows_c = [], [], []
    for s, f in fits.items():
        vid = f["video_id"]
        T = Tall[[pos_all[v] for v in vid]]
        blk = np.array([block_of[v] for v in vid])
        row = {v: i for i, v in enumerate(vid.tolist())}
        for j, g in enumerate(nets):
            # (a)
            for kind in KINDS:
                P = f[f"zone_{kind}_pred"][j].astype(np.float64)
                rb = np.stack([colr(T[blk == b], P[blk == b]) for b in range(1, N_BLOCKS + 1)])
                for t, nm in enumerate(tnames):
                    rows_a.append(dict(participant=f"sub-{s}", network=g, n_voxels=int(f["n_voxels"][j]), target=nm, kind=kind, r=np.nanmean(rb[:, t])))
            # (b)
            P = f["outer_pred"][j].astype(np.float64)
            r_direct = colr(T[:, :ne], P[:, :ne])
            for label, di in (("dims14", list(range(len(dnames)))), ("vad3", vadi)):
                via = np.full((len(vid), ne), np.nan)
                for k in range(1, c.N_FOLDS + 1):
                    te = np.array([fold_of[v] == k for v in vid])
                    trv = split.fold.to_numpy() != k
                    A = np.c_[np.ones(trv.sum()), Tall[trv][:, ne:][:, di]]
                    beta = np.linalg.lstsq(A, Tall[trv][:, :ne], rcond=None)[0]
                    Dp = P[te][:, ne:][:, di]
                    ok = np.isfinite(Dp).all(1)
                    tmp = np.full((te.sum(), ne), np.nan)
                    tmp[ok] = np.c_[np.ones(ok.sum()), Dp[ok]] @ beta
                    via[te] = tmp
                r_via = colr(T[:, :ne], via)
                for e, nm in enumerate(names):
                    rows_b.append(dict(participant=f"sub-{s}", network=g, dims=label, emotion=nm, r_direct=r_direct[e], r_via=r_via[e], loss=r_direct[e] - r_via[e]))
            # (c)
            for label, pt in (("vad", vpairs), ("content", cpairs)):
                keep = [(a, b) for a, b in zip(pt.video_a, pt.video_b) if a in row and b in row]
                ia, ib = np.array([row[a] for a, _ in keep]), np.array([row[b] for _, b in keep])
                dy, dp = T[ib, :ne] - T[ia, :ne], P[ib, :ne] - P[ia, :ne]
                rr = colr(dy, dp)
                for e, nm in enumerate(names):
                    rows_c.append(dict(participant=f"sub-{s}", network=g, pairs=label, n_pairs=len(keep), emotion=nm, r=rr[e]))
    A, B, C = pd.DataFrame(rows_a), pd.DataFrame(rows_b), pd.DataFrame(rows_c)
    A.to_csv(out / "a_content_generalization.tsv", sep="\t", index=False)
    B.to_csv(out / "b_dimension_route.tsv", sep="\t", index=False)
    C.to_csv(out / "c_matched_pairs.tsv", sep="\t", index=False)
    vpairs.to_csv(out / "vad_pairs.tsv", sep="\t", index=False)
    return A, B, C


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 네트워크별 정서 표현 형식 탐색")
    ap.add_argument("step", choices=["fit", "summarize"])
    ap.add_argument("--participant", choices=d5.HK)
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", required=True)
    ap.add_argument("--threads", type=int, default=16)
    a = ap.parse_args(argv)
    c.guard(a.design_freeze)
    split = c.load_split()
    started = time.time()
    if a.step == "fit":
        if a.participant is None:
            raise SystemExit("fit은 --participant가 필요하다")
        fit(a.participant, a.out, split, a.threads)
        info = dict(step="fit", participant=a.participant)
    else:
        summarize(a.out, split)
        info = dict(step="summarize")
    info.update(design_freeze=a.design_freeze, code_commit=c.START_HEAD, code_dirty=c.START_DIRTY, elapsed_seconds=round(time.time() - started, 1))
    Path(a.out).mkdir(parents=True, exist_ok=True)
    tag = info["step"] + (f"_sub-{a.participant}" if a.participant else "")
    (Path(a.out) / f"run_info_{tag}.json").write_text(json.dumps(info, indent=1, ensure_ascii=False))
    print(f"끝: {tag} {info['elapsed_seconds']}초", flush=True)


if __name__ == "__main__":
    main()
