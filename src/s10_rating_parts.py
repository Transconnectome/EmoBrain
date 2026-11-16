#!/usr/bin/env python3
"""S10 평정을 부분으로 나눠 영역마다 읽기 (01 6-4c, 11/16 석진 님 결정. 결과를 본 뒤 더한 탐색 분석). GPU 없음.

개념(11/16 석진 님과 맞춤): 감각 → 의미 → 저차원(valence, arousal) → 고차원(정서 범주). 고차원 = 저차원 + 의미.
시간 순서는 이 자료로 볼 수 없으므로, 영역에 따라 어느 부분이 읽히는지를 본다. 장면 묶음과 k-means는 쓰지 않는다.

평정의 부분(뇌 자료를 쓰지 않음. 바깥 fold k마다 D_k(시험 fold를 뺀 영상)로만 규칙을 정한다)
- valence
  - V부분: Vision feature(S3 vjepa2 target)로 예측한 valence. "보이는 것만으로 알 수 있는 valence"
  - 나머지: valence − V부분
  - 나머지의 C부분: Caption feature(S3 정서어 181개를 지운 deberta target)로 예측한 나머지. "의미를 알아야 알 수 있는 valence"
- arousal: valence와 같은 세 부분(11/16 석진 님 지적으로 첫 실행 뒤에 더함. 처음 판은 valence만 나눴다)
- 정서 범주 34개
  - VA부분: 사람 valence, arousal 평정으로 예측한 범주 평정(절편 있는 최소제곱, D_k로 맞춤)
  - 나머지: 범주 평정 − VA부분
  - 나머지의 C부분, V부분: Caption feature, Vision feature로 각각 예측한 나머지
- feature → 평정 규칙은 ridge(s5_common.DualRidge, 학습 행으로 표준화)다. λ는 D_k 안쪽 5겹의 r 평균으로 목표마다 고른다(s5_common.literature_version과 같은 규칙).
  D_k 영상의 값은 안쪽 5겹의 바깥 예측(자기 평정을 보지 않은 규칙의 예측)이고, 시험 fold 영상의 값은 D_k 전체로 맞춘 규칙의 예측이다.
  그래서 시험 fold의 평정은 어떤 규칙에도 들어가지 않는다. VA부분의 최소제곱은 계수가 3개라 D_k 안에서 바로 맞춘다.

뇌로 읽기: 네트워크 13개마다 그 ROI들의 voxel 합집합(s10_geometry.network_positions)으로 위 부분들을 ridge(s5_common.main_version, H2 분할)로 읽는다.
바깥 fold k의 학습, 검증 행은 fold k의 부분 값을, 시험 행은 같은 fold k의 부분 값을 목표로 한다. 6 fold의 시험 예측을 모아 r을 한 번 낸다.

미리 적는 가설(계산 전, 11/16)
- 가. valence의 나머지(특히 C부분)는 연합 네트워크(Default, Frontoparietal, Cingulo-Opercular, Language)에서 시각 네트워크(Visual1, Visual2)보다 잘 읽힌다.
  V부분에 대한 나머지의 비율도 연합 네트워크가 더 높다.
- 나. 정서 범주의 나머지(VA로 설명되지 않는 부분)는 Caption feature가 Vision feature보다 더 설명한다(평정과 feature만의 계산).
  예외로 craving, aesthetic appreciation처럼 보이는 것과 직접 이어지는 범주는 Vision feature 쪽일 수 있다.
- 다. 정서 범주의 나머지는 연합 네트워크에서 시각 네트워크보다 잘 읽힌다. 예외는 나와 같다.
- 비교: 연합 4개 평균 − 시각 2개 평균의 r 차이를 미리 정한 대비로 둔다. 범주는 34개 정서 r의 평균과 정서별 값을 함께 낸다. 탐색이라 다중비교 보정을 하지 않는다.
- 구간: s10_geometry_checks와 같은 bootstrap(같은 내용 영상 묶음 canonical_id, BOOT_SEED, 10,000회, 5명에 같은 무게).

사용: s10_rating_parts.py parts --out <폴더> --design-freeze <커밋>
      s10_rating_parts.py fit --participant 01 --out <폴더> --design-freeze <커밋> [--threads 16]
      s10_rating_parts.py summarize --out <폴더> --design-freeze <커밋>
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
import s10_geometry as geo
import s10_geometry_checks as gc
import s10_stats as st

ASSOC = ("Default", "Frontoparietal", "Cingulo-Opercular", "Language")
VISUAL = ("Visual1", "Visual2")
NE = 34


def crossfit(x, y, fold, k):
    """바깥 fold k의 규칙. x torch(영상 × feature), y torch(영상 × 목표). 돌려주는 값: (영상 × 목표) numpy.
    D_k 행은 안쪽 겹의 바깥 예측, 시험 fold 행은 D_k 전체로 맞춘 규칙의 예측. λ는 안쪽 겹 r 평균으로 목표마다 고른다."""
    dk_folds = [f for f in range(1, c.N_FOLDS + 1) if f != k]
    dk, te = np.flatnonzero(np.isin(fold, dk_folds)), np.flatnonzero(fold == k)
    L = len(d5.LAMBDAS)
    oof = torch.zeros((L, len(fold), y.shape[1]), dtype=y.dtype)
    scores = []
    for j in dk_folds:
        tr, va = dk[fold[dk] != j], dk[fold[dk] == j]
        d = d5.DualRidge(x, tr, dict(val=va))
        fitted = d.fit(y[tr])
        paths = torch.stack([d.predict("val", fitted, lam) for lam in d5.LAMBDAS])
        oof[:, va] = paths
        scores.append(torch.stack([d5.r_selection(y[va], paths[i]) for i in range(L)]))
    pick = d5.pick_per_target(torch.stack(scores).nanmean(0))
    out = oof.gather(0, pick[None, None, :].expand(1, len(fold), y.shape[1]))[0]
    d = d5.DualRidge(x, dk, dict(test=te))
    fitted = d.fit(y[dk])
    paths = torch.stack([d.predict("test", fitted, lam) for lam in d5.LAMBDAS])
    out[te] = paths.gather(0, pick[None, None, :].expand(1, len(te), y.shape[1]))[0]
    return out.numpy()


DIMS = ("valence", "arousal")


def part_names(names):
    return ([f"{d}|{p}" for d in DIMS for p in ("V", "rest", "rest_C")] + [f"{e}|VA" for e in names] + [f"{e}|rest" for e in names]
            + [f"{e}|rest_C" for e in names] + [f"{e}|rest_V" for e in names])


def parts(out, split, threads):
    """바깥 fold마다 모든 개발 영상의 부분 값(split 순서). parts.npz: parts (fold 6 × 영상 × 부분), video_id, part 이름."""
    torch.set_num_threads(threads)
    vid, fold = split.video_id.to_numpy(), split.fold.to_numpy()
    T, names, dnames = geo.targets(split, vid)
    E = T[:, :NE]
    VA = T[:, [NE + dnames.index("valence"), NE + dnames.index("arousal")]]
    xv = d5.as_tensor(c.load_rows(c.VISUAL_TARGET, vid, split), "cpu")
    xc = d5.as_tensor(c.load_rows(c.CAPTION_NO_EMOTION, vid, split), "cpu")
    pn = part_names(names)
    P = np.full((c.N_FOLDS, len(vid), len(pn)), np.nan)
    for k in range(1, c.N_FOLDS + 1):
        dk = fold != k
        dimv = T[:, [NE + dnames.index(d) for d in DIMS]]
        v_part = crossfit(xv, d5.as_tensor(dimv, "cpu"), fold, k)
        v_rest = dimv - v_part
        v_rest_c = crossfit(xc, d5.as_tensor(v_rest, "cpu"), fold, k)
        dim_parts = np.concatenate([np.c_[v_part[:, i], v_rest[:, i], v_rest_c[:, i]] for i in range(len(DIMS))], 1)
        A = np.c_[np.ones(dk.sum()), VA[dk]]
        beta = np.linalg.lstsq(A, E[dk], rcond=None)[0]
        e_va = np.c_[np.ones(len(vid)), VA] @ beta
        e_rest = E - e_va
        rt = d5.as_tensor(e_rest, "cpu")
        e_rest_c, e_rest_v = crossfit(xc, rt, fold, k), crossfit(xv, rt, fold, k)
        P[k - 1] = np.c_[dim_parts, e_va, e_rest, e_rest_c, e_rest_v]
        print(f"부분 fold {k} 끝", flush=True)
    if not np.isfinite(P).all():
        raise ValueError("부분 값에 NaN이 있다")
    o = Path(out)
    o.mkdir(parents=True, exist_ok=True)
    np.savez(o / "parts.npz", parts=P, video_id=vid, part=np.array(pn), emotions=np.array(names))
    # 평정과 feature만의 계산(가설 나): 시험 fold 값을 모아 낸 r
    te_vals = {}
    for k in range(1, c.N_FOLDS + 1):
        te = fold == k
        for i, p in enumerate(pn):
            te_vals.setdefault(p, np.zeros(len(vid)))[te] = P[k - 1, te, i]
    rows = [dict(target=d, r_V_of_whole=np.corrcoef(te_vals[f"{d}|V"], T[:, NE + dnames.index(d)])[0, 1],
                 r_C_of_rest=np.corrcoef(te_vals[f"{d}|rest_C"], te_vals[f"{d}|rest"])[0, 1]) for d in DIMS]
    for j, e in enumerate(names):
        rows.append(dict(target=e, r_VA_of_whole=np.corrcoef(te_vals[f"{e}|VA"], E[:, j])[0, 1],
                         r_C_of_rest=np.corrcoef(te_vals[f"{e}|rest_C"], te_vals[f"{e}|rest"])[0, 1],
                         r_V_of_rest=np.corrcoef(te_vals[f"{e}|rest_V"], te_vals[f"{e}|rest"])[0, 1]))
    pd.DataFrame(rows).to_csv(o / "parts_features_only.tsv", sep="\t", index=False)


def fit(s, out, split, threads, n_boot):
    torch.set_num_threads(threads)
    z = np.load(Path(out) / "parts.npz", allow_pickle=True)
    P, pvid, pn = z["parts"], z["video_id"], z["part"].tolist()
    brain = d5.load_brain(s, split)
    vid, fold = np.asarray(brain.video_id), np.asarray(brain.fold)
    pos = {v: i for i, v in enumerate(pvid.tolist())}
    rows = np.array([pos[v] for v in vid.tolist()])
    Pk = P[:, rows]  # fold × 이 참가자 영상 × 부분
    truth = np.full((len(vid), len(pn)), np.nan)
    for k in range(1, c.N_FOLDS + 1):
        truth[fold == k] = Pk[k - 1, fold == k]
    nets = geo.network_positions(brain)
    W = gc.boot_weights(split, vid, n_boot).double().numpy()
    pred = np.full((len(nets), len(vid), len(pn)), np.nan, np.float32)
    point = np.full((len(nets), len(pn)), np.nan)
    boot = np.full((n_boot, len(nets), len(pn)), np.nan, np.float32)
    X = torch.as_tensor(np.asarray(brain.X))
    for j, (g, p) in enumerate(nets.items()):
        started = time.time()
        x = X[:, torch.as_tensor(p)].double()
        for k in range(1, c.N_FOLDS + 1):
            r = c.roles(k)
            tr, va, te = np.flatnonzero(np.isin(fold, r["train"])), np.flatnonzero(fold == r["val"]), np.flatnonzero(fold == k)
            yk = Pk[k - 1]
            pr, bad = geo.ridge(x, yk, tr, va, te)
            if bad:
                raise ValueError(f"{g} fold {k}: 정답이 상수인 부분이 있다")
            pred[j, te] = pr
        Pj = pred[j].astype(np.float64)
        point[j] = st.boot_r(np.ones((1, len(vid))), truth, dict(p=Pj))["p"][0]
        boot[:, j] = st.boot_r(W, truth, dict(p=Pj))["p"]
        print(f"sub-{s} {g} ({len(p)} voxel) {time.time() - started:.0f}초", flush=True)
    o = Path(out) / "fit"
    o.mkdir(parents=True, exist_ok=True)
    tmp = o / f"sub-{s}.tmp.npz"
    np.savez(tmp, video_id=vid, networks=np.array(list(nets)), part=np.array(pn), pred=pred, truth=truth, point=point, boot=boot)
    tmp.rename(o / f"sub-{s}.npz")


def summarize(out):
    """parts_brain.tsv: 네트워크, 부분마다 5명 평균 r과 구간, 참가자별 r. contrast.tsv: 미리 정한 대비(연합 4개 평균 − 시각 2개 평균)와
    범주 34개 평균판, 네트워크 쌍의 차이는 내지 않는다. 구간은 basic bootstrap 95%, p는 중심을 맞춘 양측 bootstrap p."""
    out = Path(out)
    F = [np.load(out / "fit" / f"sub-{s}.npz", allow_pickle=True) for s in d5.HK]
    nets, pn = F[0]["networks"].tolist(), F[0]["part"].tolist()
    pt = np.stack([f["point"] for f in F])  # 5 × 망 × 부분
    bt = np.stack([f["boot"] for f in F]).mean(0)  # B × 망 × 부분 (같은 무게라 재표집마다 평균)
    m = pt.mean(0)
    lo, hi = st.basic_ci(m, bt)
    rows = []
    for j, g in enumerate(nets):
        for i, p in enumerate(pn):
            t, part = p.split("|")
            rows.append(dict(network=g, target=t, part=part, r=m[j, i], lo=lo[j, i], hi=hi[j, i], **{f"r_sub-{s}": pt[q, j, i] for q, s in enumerate(d5.HK)}))
    pd.DataFrame(rows).to_csv(out / "parts_brain.tsv", sep="\t", index=False)
    ia, iv = [nets.index(g) for g in ASSOC], [nets.index(g) for g in VISUAL]
    con_p = m[ia].mean(0) - m[iv].mean(0)
    con_b = bt[:, ia].mean(1) - bt[:, iv].mean(1)
    rows = []
    for i, p in enumerate(pn):
        t, part = p.split("|")
        a, b = st.basic_ci(con_p[i], con_b[:, i])
        rows.append(dict(target=t, part=part, assoc_minus_visual=con_p[i], lo=float(a), hi=float(b), p=float(st.centered_p(con_p[i], con_b[:, i]))))
    for part in ("VA", "rest", "rest_C", "rest_V"):
        idx = [i for i, p in enumerate(pn) if p.endswith(f"|{part}") and p.split("|")[0] not in DIMS]
        cp, cb = con_p[idx].mean(), con_b[:, idx].mean(1)
        a, b = st.basic_ci(cp, cb)
        rows.append(dict(target="emotion_mean34", part=part, assoc_minus_visual=cp, lo=float(a), hi=float(b), p=float(st.centered_p(cp, cb))))
    pd.DataFrame(rows).to_csv(out / "contrast.tsv", sep="\t", index=False)
    mean_rows = []
    for j, g in enumerate(nets):
        for part in ("VA", "rest", "rest_C", "rest_V"):
            idx = [i for i, p in enumerate(pn) if p.endswith(f"|{part}") and p.split("|")[0] not in DIMS]
            v = m[j, idx].mean()
            a, b = st.basic_ci(v, bt[:, j, idx].mean(1))
            mean_rows.append(dict(network=g, part=part, r_mean34=v, lo=float(a), hi=float(b)))
    pd.DataFrame(mean_rows).to_csv(out / "parts_brain_emotion_mean.tsv", sep="\t", index=False)


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 평정을 부분으로 나눠 영역마다 읽기")
    ap.add_argument("step", choices=["parts", "fit", "summarize"])
    ap.add_argument("--participant", choices=d5.HK)
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", required=True)
    ap.add_argument("--threads", type=int, default=16)
    ap.add_argument("--n-boot", type=int, default=st.N_RESAMPLE)
    a = ap.parse_args(argv)
    c.guard(a.design_freeze)
    split = c.load_split()
    started = time.time()
    if a.step == "parts":
        parts(a.out, split, a.threads)
        tag = "parts"
    elif a.step == "fit":
        if a.participant is None:
            raise SystemExit("fit은 --participant가 필요하다")
        fit(a.participant, a.out, split, a.threads, a.n_boot)
        tag = f"fit_sub-{a.participant}"
    else:
        summarize(a.out)
        tag = "summarize"
    info = dict(step=a.step, participant=a.participant, n_boot=a.n_boot, boot_seed=gc.BOOT_SEED, design_freeze=a.design_freeze,
                code_commit=c.START_HEAD, code_dirty=c.START_DIRTY, elapsed_seconds=round(time.time() - started, 1))
    Path(a.out).mkdir(parents=True, exist_ok=True)
    (Path(a.out) / f"run_info_{tag}.json").write_text(json.dumps(info, indent=1, ensure_ascii=False))
    print(f"끝: {tag} {info['elapsed_seconds']}초", flush=True)


if __name__ == "__main__":
    main()
