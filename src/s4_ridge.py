#!/usr/bin/env python3
"""S4 뇌 없는 ridge (04 S4, 01 D12, O18, O20, O22, 3-4, 2026-11-06).

- d12: V-JEPA 2의 40개 block 각각으로 캡션 목표(4,096차원)와 저수준 시각 특징(6,558개)을 예측한다. 뇌와 정서를 쓰지 않는다. 이 결과로 목표 block을 다시 고르지 않는다(3-2).
    바깥 분할은 run fold 6개다. λ는 안쪽 5겹의 차원 평균 R²로 하나 고른다. 보고값은 원래 척도로 되돌린 시험 예측을 모아 낸 차원별 R²의 평균이다(O20).
- noemo: DeBERTa 캡션 특징(원 캡션, 정서어 제거 캡션)으로 정서 34개를 예측한다(3-4, SI). 정서 ridge 문헌판의 규칙이다. 정서마다 안쪽 5겹 평균 r로 λ를 고르고 D_k 전체로 학습한다(O18). 정답은 비율 그대로다(B3).

λ 후보는 10^1부터 10^6까지 로그 간격 10개다(O18). 표준화는 regression마다 그 학습 자료로 맞춘다(N3). 고른 λ가 후보의 끝인 횟수를 표에 적고 후보를 넓히지 않는다.
사용: s4_ridge.py --task d12 --design-freeze <커밋> [--device cuda]
"""
import argparse
import json
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

import s4_common as c

LAMBDAS = np.logspace(1, 6, 10)  # O18. Horikawa(2025) 공개 decoding 코드 mcap_setParams.m의 lowL 1, highL 6, 10개
BLOCKS = list(range(40))


def ridge_paths(xtr, ytr, xte, lambdas=LAMBDAS):
    """λ마다 시험 예측을 돌려준다. 절편은 학습 평균으로 처리한다. 돌려주는 값: λ 수 × 시험 × 출력."""
    xm, ym = xtr.mean(0), ytr.mean(0)
    u, s, vh = torch.linalg.svd(xtr - xm, full_matrices=False)
    uty = u.T @ (ytr - ym)
    xv = (xte - xm) @ vh.T
    out = []
    for lam in lambdas:
        out.append(ym + xv @ ((s / (s**2 + lam))[:, None] * uty))
    out = torch.stack(out)
    if not torch.isfinite(out).all():
        raise ValueError("ridge 예측에 NaN 또는 Inf가 있다")
    return out


def r2_columns(y, p):
    """열마다 R². 분모는 그 자료의 평균 기준이다. 상수 열은 NaN이다."""
    ss = ((y - y.mean(0)) ** 2).sum(0)
    return torch.where(ss > 0, 1 - ((y - p) ** 2).sum(0) / ss.clamp_min(1e-30), torch.full_like(ss, float("nan")))


def r_columns(y, p):
    """열마다 Pearson r. y가 상수인 열은 NaN, 예측이 상수이면 선택 계산에서 0으로 센다(O6)."""
    yc, pc = y - y.mean(0), p - p.mean(0)
    den = torch.sqrt((yc**2).sum(0) * (pc**2).sum(0))
    r = torch.where(den > 0, (yc * pc).sum(0) / den.clamp_min(1e-30), torch.zeros_like(den))
    return torch.where((yc**2).sum(0) > 0, r, torch.full_like(r, float("nan")))


def pred_dir(out):
    """D12의 block별 시험 예측을 모으는 임시 폴더. 다시 시작하면 처음부터 쓴다."""
    p = Path(str(out) + "_predictions_tmp")
    p.mkdir(parents=True, exist_ok=True)
    return p


def d12(split, device, out, run):
    started = time.time()
    ids, folds = split.video_id.to_numpy(), split.fold.to_numpy()
    blocks = np.load(c.FEATURES / "vjepa2/blocks.npy", mmap_mode="r")
    c.check_dev(ids, split)
    if blocks.shape[0] != 2196:
        raise ValueError("blocks: 영상이 2,196개가 아니다")
    targets = dict(caption=c.load_rows(c.CAPTION_TARGET, ids, split), lowlevel=c.load_rows(c.LOWLEVEL, ids, split))
    run.check()
    rows, per_dim, preds = [], {}, {}
    for b in BLOCKS:
        x = torch.as_tensor(c.finite(np.asarray(blocks[ids - 1, b], np.float64), f"block {b + 1}"), device=device)
        for name, yy in targets.items():
            y = torch.as_tensor(yy.astype(np.float64), device=device)
            pred = torch.zeros_like(y)
            ks = sorted(set(folds.tolist()))
            picks = {}
            for k in ks:
                p, chosen = _one_fold_d12(x, y, folds, k, device)
                pred[folds == k] = p  # 원래 척도로 되돌린 값이다(O20)
                picks[k] = chosen
            r2 = r2_columns(y, pred).cpu().numpy()
            rows.append(dict(block=b + 1, target=name, mean_r2=float(np.nanmean(r2)), median_r2=float(np.nanmedian(r2)), n_lambda_at_ends=sum(v in (0, len(LAMBDAS) - 1) for v in picks.values()), lambda_index=",".join(str(picks[k]) for k in ks)))
            per_dim[f"block{b + 1}_{name}"] = r2.astype(np.float32)
            preds[name] = pred.cpu().numpy().astype(np.float32)
        np.savez(pred_dir(out) / f"block{b + 1:02d}.npz", video_id=ids, **preds)
        print("block", b + 1, flush=True)
    with c.Atomic(out) as tmp:
        pd.DataFrame(rows).to_csv(tmp / "d12.tsv", sep="\t", index=False, float_format="%.6g")
        np.savez(tmp / "d12_r2_per_dimension.npz", **per_dim)
        os.rename(pred_dir(out), tmp / "predictions")
        run.check()
        json.dump(dict(run.prov, **c.timing(started)), open(tmp / "done.json", "w"), indent=1)


def _standardize(x, rows):
    m, s = x[rows].mean(0), x[rows].std(0, unbiased=False)
    if (s <= 0).any():
        raise ValueError("학습 자료에서 표준편차가 0인 차원이 있다")
    return (x - m) / s, m, s


def _one_fold_d12(x, y, folds, k, device):
    """바깥 fold k 하나. 안쪽 5겹의 차원 평균 R²로 λ를 하나 고른다(O22). 입력과 목표의 표준화는 regression마다 그 학습 자료로 한다(N3). 돌려주는 값: 원래 척도의 시험 예측, λ 번호."""
    dk = folds != k
    scores = []
    for j in sorted(set(folds[dk].tolist())):
        tr, va = dk & (folds != j), folds == j
        zx, _, _ = _standardize(x, tr)
        zy, _, _ = _standardize(y, tr)
        paths = ridge_paths(zx[tr], zy[tr], zx[va])
        scores.append(torch.stack([r2_columns(zy[va], p).nanmean() for p in paths]))
    s = torch.stack(scores).mean(0)
    if not torch.isfinite(s).all():
        raise ValueError("D12의 선택 점수를 낼 수 없다")
    pick = int(s.argmax())
    zx, _, _ = _standardize(x, dk)
    zy, ym, ys = _standardize(y, dk)
    return ridge_paths(zx[dk], zy[dk], zx[folds == k], [LAMBDAS[pick]])[0] * ys + ym, pick


def emotion_ridge(x, y, folds, device):
    """정서 ridge 문헌판의 규칙(O18). 정서마다 λ를 고른다. 돌려주는 값: 시험 예측, fold마다 고른 λ 번호."""
    xt = torch.as_tensor(c.finite(x, "ridge 입력").astype(np.float64), device=device)
    yt = torch.as_tensor(c.finite(y, "ridge 정답").astype(np.float64), device=device)
    n, q = yt.shape
    pred = torch.zeros((n, q), dtype=torch.float64, device=device)
    chosen = {}
    for k in sorted(set(folds.tolist())):
        dk = folds != k
        scores = []
        for j in sorted(set(folds[dk].tolist())):
            tr, va = dk & (folds != j), folds == j
            z, _, _ = _standardize(xt, tr)
            paths = ridge_paths(z[tr], yt[tr], z[va])
            scores.append(torch.stack([r_columns(yt[va], p) for p in paths]))
        s = torch.stack(scores).nanmean(0)  # y가 상수인 겹은 계산 불가라 빠진다
        if s.isnan().any():
            raise ValueError("어떤 정서의 정답이 모든 안쪽 겹에서 상수라 λ를 고를 수 없다")
        pick = s.argmax(0)  # λ 앞쪽이 먼저 잡힌다
        z, _, _ = _standardize(xt, dk)
        paths = ridge_paths(z[dk], yt[dk], z[folds == k])
        pred[folds == k] = paths.gather(0, pick[None, None, :].expand(1, int((folds == k).sum()), q))[0]
        chosen[k] = pick.cpu().numpy()
    return pred.cpu().numpy(), chosen


def noemo(split, device, out, run):
    started = time.time()
    ids, folds = split.video_id.to_numpy(), split.fold.to_numpy()
    y, cols = c.load_scores(split, "emotions")
    run.check()
    rows, preds = [], dict(video_id=ids)
    for name, feat in (("original", c.CAPTION_TARGET), ("no_emotion_words", c.CAPTION_NO_EMOTION)):
        pred, chosen = emotion_ridge(c.load_rows(feat, ids, split), y, folds, device)
        preds[name] = pred.astype(np.float32)
        for k, v in chosen.items():
            preds[f"{name}_lambda_index_fold{k}"] = v
        r = c.pearson(y, pred)
        ends = np.mean([np.isin(v, [0, len(LAMBDAS) - 1]) for v in chosen.values()], 0)
        rows += [dict(caption=name, emotion=e, r=float(ri), frac_lambda_at_ends=float(f)) for e, ri, f in zip(cols, r, ends)]
    with c.Atomic(out) as tmp:
        pd.DataFrame(rows).to_csv(tmp / "noemo_ridge.tsv", sep="\t", index=False, float_format="%.6g")
        np.savez(tmp / "noemo_ridge_pred.npz", **preds)
        run.check()
        json.dump(dict(run.prov, **c.timing(started)), open(tmp / "done.json", "w"), indent=1)


def input_paths(task):
    if task == "d12":
        return {"vjepa2_blocks": c.FEATURES / "vjepa2/blocks.npy", "caption_target": c.FEATURES / f"{c.CAPTION_TARGET}.npy", "lowlevel": c.FEATURES / f"{c.LOWLEVEL}.npy"}
    return {"caption_target": c.FEATURES / f"{c.CAPTION_TARGET}.npy", "caption_no_emotion": c.FEATURES / f"{c.CAPTION_NO_EMOTION}.npy", "labels": c.LABELS}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, choices=["d12", "noemo"])
    ap.add_argument("--design-freeze", default="")
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    c.guard(a.design_freeze)
    out = c.OUT / f"ridge_{a.task}"
    run = c.Run(a.design_freeze, input_paths(a.task), task=a.task, lambdas=LAMBDAS.tolist())
    if c.done_or_new(out, run.key):
        print("건너뜀", out)
        return
    split = c.load_split()
    (d12 if a.task == "d12" else noemo)(split, a.device, out, run)


if __name__ == "__main__":
    main()
