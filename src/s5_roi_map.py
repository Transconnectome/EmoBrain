#!/usr/bin/env python3
"""S5 370개 ROI 지도 (01 6-4의 ROI 지도, 11/13 석진 님. 2026-11-13).

참가자, 바깥 fold, ROI마다 그 ROI의 voxel만으로 ridge를 따로 학습해 시험 fold를 예측한다.
- 목표: 정서 34개(사람 평정), Vision feature(vjepa2/target, 5,632차원), Caption feature(deberta/target, 4,096차원). 뇌 모델의 feature 목표와 같은 파일이다.
- 분할과 선택: 뇌 모델과 정서 ridge 주 비교판의 H2 규칙. 학습 fold 4개로 학습하고, 검증 fold로 λ를 고르고, 시험 fold를 예측한다.
  λ 후보는 모든 ridge와 같은 LAMBDAS(O18)다. 정서는 정서마다 그 정서의 검증 r로 고른다(N15와 같음).
  Vision feature와 Caption feature는 묶음마다 검증 fold의 차원별 r 평균으로 하나를 고른다(O18의 선택 지표를 H2 분할에 적용).
  시험 fold는 고르는 데 쓰지 않는다. 입력 표준화는 학습 행으로만 한다(DualRidge, N3).
- 저장: 정서는 시험 예측(시험 행 × ROI × 34)을 그대로 둔다. feature는 6 fold를 모아 차원별 r을 낼 수 있도록(O19) ROI와 차원마다
  시험 예측의 합, 제곱합, 실제 값과의 곱의 합을 저장하고, 실제 값의 합과 제곱합은 fold마다 따로 둔다. 예측 전체는 너무 커서 두지 않는다.
- 이 지도는 "그 ROI의 신호만으로 그 값을 예측할 수 있었다"까지를 보여 준다(6-4a의 해석). Horikawa 외(2020)의 영역별 decoding을 같은 자료에서
  우리 분할과 규칙으로 다시 한 것이고, Vision feature와 Caption feature로 넓혔다. 순열 검정과 다중비교는 S10이다.
사용: s5_roi_map.py --participant 01 --design-freeze <커밋> [--folds 1,2] [--device cuda]
"""
import argparse
import json
import time

import numpy as np
import torch

import s4_common as c
import s5_common as d5

GROUPS = ("vision", "caption")


def split_idx(fold, k):
    r = c.roles(k)
    return np.flatnonzero(np.isin(fold, r["train"])), np.flatnonzero(fold == r["val"]), np.flatnonzero(fold == k)


def mean_r(y, p):
    """열마다 r을 내고 평균한다. 정답이 상수인 열은 뺀다(r_selection의 NaN)."""
    return torch.nanmean(d5.r_selection(y, p))


def roi_fit(x, y_em, feats, tr, va, te, lambdas=d5.LAMBDAS):
    """ROI 하나. x: 행 × 그 ROI voxel. y_em: 행 × 34. feats: 이름 -> 행 × 차원.
    돌려주는 것: 정서 시험 예측, 정서 λ 번호, feature 묶음마다 (고른 λ 번호, 시험 예측)."""
    d = d5.DualRidge(x, tr, dict(val=va, test=te))
    fitted = d.fit(y_em[tr])
    scores = torch.stack([d5.r_selection(y_em[va], d.predict("val", fitted, lam)) for lam in lambdas])
    pick = d5.pick_per_target(scores)
    paths = torch.stack([d.predict("test", fitted, lam) for lam in lambdas])
    em = paths.gather(0, pick[None, None, :].expand(1, len(te), y_em.shape[1]))[0]
    out = {}
    for name, f in feats.items():
        ff = d.fit(f[tr])
        val_r = torch.stack([mean_r(f[va], d.predict("val", ff, lam)) for lam in lambdas])
        if val_r.isnan().any():
            raise ValueError(f"{name}: 검증 r을 낼 수 없는 λ가 있다")
        j = int(val_r.argmax())  # 같으면 작은 λ(argmax는 첫 번째)
        out[name] = (j, d.predict("test", ff, lambdas[j]))
    return em, pick, out


def roi_map_task(brain, y_em, feats, k, device, lambdas=d5.LAMBDAS):
    """바깥 fold k. brain.X 행 순서의 정답을 받는다. ROI마다 따로 학습한다."""
    tr, va, te = split_idx(brain.fold, k)
    if not len(tr) or not len(va) or not len(te):
        raise ValueError(f"fold {k}: 학습, 검증, 시험 행 가운데 빈 것이 있다")
    x_all = torch.as_tensor(np.asarray(brain.X), device=device)
    y = d5.as_tensor(y_em, device)
    f = {n: d5.as_tensor(v, device) for n, v in feats.items()}
    n_roi = len(brain.roi_positions)
    em_pred = np.empty((len(te), n_roi, y.shape[1]), np.float32)
    em_pick = np.empty((n_roi, y.shape[1]), np.int16)
    sums = {n: dict(p=np.empty((n_roi, v.shape[1])), pp=np.empty((n_roi, v.shape[1])), py=np.empty((n_roi, v.shape[1]))) for n, v in f.items()}
    picks = {n: np.empty(n_roi, np.int16) for n in f}
    for r, pos in enumerate(brain.roi_positions):
        x = x_all[:, torch.as_tensor(pos, device=device)].double()
        em, pick, out = roi_fit(x, y, f, tr, va, te, lambdas)
        em_pred[:, r], em_pick[r] = em.cpu().numpy(), pick.cpu().numpy()
        for n, (j, p) in out.items():
            yt = f[n][te]
            sums[n]["p"][r], sums[n]["pp"][r], sums[n]["py"][r] = p.sum(0).cpu().numpy(), (p * p).sum(0).cpu().numpy(), (p * yt).sum(0).cpu().numpy()
            picks[n][r] = j
    arrays = dict(video_id=brain.video_id[te], emotion_pred=em_pred, emotion_lambda_index=em_pick, n_test=np.array(len(te)))
    for n in f:
        yt = f[n][te]
        arrays.update({f"{n}_sum_p": sums[n]["p"], f"{n}_sum_pp": sums[n]["pp"], f"{n}_sum_py": sums[n]["py"], f"{n}_lambda_index": picks[n],
                       f"{n}_sum_y": yt.sum(0).cpu().numpy(), f"{n}_sum_yy": (yt * yt).sum(0).cpu().numpy()})
    return arrays


def pooled_r(parts, name):
    """fold별 합을 모아 ROI × 차원의 Pearson r을 낸다(O19, 6 fold를 모은 시험 영상). parts: fold별 pred.npz."""
    n = sum(int(z["n_test"]) for z in parts)
    sp, spp, spy = (sum(z[f"{name}_{s}"] for z in parts) for s in ("sum_p", "sum_pp", "sum_py"))
    sy, syy = (sum(z[f"{name}_{s}"] for z in parts) for s in ("sum_y", "sum_yy"))
    cov = spy - sp * sy / n
    var_p, var_y = spp - sp ** 2 / n, syy - sy ** 2 / n
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where((var_p > 0) & (var_y > 0), cov / np.sqrt(var_p * var_y), np.nan)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--participant", required=True, choices=d5.HK)
    ap.add_argument("--design-freeze", default="")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--folds", default="", help="바깥 fold 일부만(ex) 1,2). 비우면 6개 모두")
    a = ap.parse_args()
    c.guard(a.design_freeze)
    s = a.participant
    inputs = {"labels": c.LABELS, f"response:sub-{s}": d5.response_path(s), f"roi:sub-{s}": d5.roi_path(s),
              "visual_target": c.FEATURES / f"{c.VISUAL_TARGET}.npy", "caption_target": c.FEATURES / f"{c.CAPTION_TARGET}.npy"}
    run = d5.Run(a.design_freeze, inputs, task="roi_map", lambdas=d5.LAMBDAS.tolist(), feature_lambda="group, validation mean r")
    split = c.load_split()
    y_em, _ = c.load_scores(split, "emotions")
    folds = [int(x) for x in a.folds.split(",")] if a.folds else list(range(1, c.N_FOLDS + 1))
    if not set(folds) <= set(range(1, c.N_FOLDS + 1)):
        raise SystemExit("바깥 fold는 1~6이다")
    brain = d5.load_brain(s, split)
    y = d5.align(y_em, split, brain.video_id)
    feats = dict(vision=c.load_rows(c.VISUAL_TARGET, brain.video_id, split), caption=c.load_rows(c.CAPTION_TARGET, brain.video_id, split))
    run.check()
    for k in folds:
        out = d5.OUT / "roi_map" / f"sub-{s}_fold{k}"
        if c.done_or_new(out, run.key):
            continue
        started = time.time()
        arrays = roi_map_task(brain, y, feats, k, a.device)
        with c.Atomic(out) as tmp:
            np.savez(tmp / "pred.npz", **arrays)
            run.check()
            json.dump(dict(run.prov, **c.timing(started), participant=s, fold=k, n_roi=len(brain.roi_positions)), open(tmp / "done.json", "w"), indent=1)
        print("저장", out, f"{time.time() - started:.0f}초", flush=True)


if __name__ == "__main__":
    main()
