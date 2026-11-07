#!/usr/bin/env python3
"""S5 정서 기준선과 14개 차원 ridge (04 S5, 01 I7, I10, N15, N16, B4, O18, O23, O24, O25, 2026-11-06). 기준선은 통과 조건이 아니다(6-1).

과제
- ridge: 참가자, fold마다 voxel 입력의 정서 34개와 14개 차원 ridge. 주 비교판(검증 fold 하나, N15)과 문헌판(안쪽 5겹, H3). 평균 예측의 값도 저장한다(O25).
- soft_bce: 같은 입력의 선형 sigmoid, soft BCE(N16, O24).
- signal: 뇌 전체 평균과 block 신호 크기(I7). 주 비교판의 규칙이다.
- video: 영상 길이의 자연로그(O23)와 저수준 시각 특징(3-6). 뇌를 쓰지 않아 fold마다 하나이고, 시험은 개발 영상 전체다. 주 비교판의 규칙이다.
- zone: 내용 구역 제외와 학습량 대조의 정서 ridge 주 비교판(6-2, I10).
- h2020: Horikawa 외(2020)의 복셀 선택 ridge(I7). ROI마다, 목표마다 상위 500 voxel, λ는 logspace(1, 4, 20), 안쪽 5겹으로 목표마다 고른다. 이어 붙인 안쪽 예측의 r을 쓰고, ensemble은 안쪽 r 0.095 이상인 ROI의 평균이다(공개 코드). 코드와 달리 전체 표본 z-score는 옮기지 않는다(H5).
h2020은 원문 재현이 아니다. 전체 표본 z-score를 하지 않고(H5), ROI 선택을 바깥 fold마다 그 D_k 안에서 하며, 기준을 넘는 ROI가 없을 때 시험 성능이 아니라 안쪽 r로 ROI를 고른다. ROI 지도와 분할도 다르다. 방법 절에 함께 적는다.
정답은 값 그대로 쓴다(B3, B4). 편상관과 순열 검정은 S10이다. 사용: s5_baselines.py --task ridge --participant 01 --design-freeze <커밋>
"""
import argparse
import json
import time

import numpy as np
import pandas as pd
import torch

import s4_common as c
import s5_common as d5


def split_idx(fold, k):
    r = c.roles(k)
    return np.flatnonzero(np.isin(fold, r["train"])), np.flatnonzero(fold == r["val"]), np.flatnonzero(fold == k), r


def ridge_task(brain, y_em, y_dim, k, device):
    """y_em, y_dim: brain 행 순서의 정답. 입력과 정답은 값 그대로 넘긴다."""
    tr, va, te, r = split_idx(brain.fold, k)
    x = d5.as_tensor(brain.X, device)
    y = d5.as_tensor(np.concatenate([y_em, y_dim], 1), device)
    main, pick_main = d5.main_version(x, y, tr, va, te)
    lit, pick_lit = d5.literature_version(x, y, brain.fold, r["dk"], te)
    n = y_em.shape[1]
    dk = np.isin(brain.fold, r["dk"])
    return dict(video_id=brain.video_id[te], emotion_main=main[:, :n].cpu().numpy(), dimension_main=main[:, n:].cpu().numpy(), emotion_literature=lit[:, :n].cpu().numpy(), dimension_literature=lit[:, n:].cpu().numpy(), lambda_main=pick_main.cpu().numpy(), lambda_literature=pick_lit.cpu().numpy(), mean_prediction=np.asarray(y_em[dk], np.float64).mean(0))


def make_optimizer(model, lr, wd):
    """weight decay는 weight에만 적용한다(O16과 같은 규칙. 뇌 입력 기준선의 적용은 01 보류된 결정 3과 함께 확인한다)."""
    return torch.optim.AdamW([dict(params=[model.weight], weight_decay=wd), dict(params=[model.bias], weight_decay=0.0)], lr=lr)


def soft_bce_train(ztr, ytr, zva, yva, wd, lr, settings, device):
    """조기 종료는 검증 soft BCE, 가장 낮았던 epoch의 가중치로 되돌린다(G13, O6)."""
    torch.manual_seed(settings["seed"])
    g = torch.Generator().manual_seed(settings["seed"])
    model = torch.nn.Linear(ztr.shape[1], ytr.shape[1]).to(device)
    opt = make_optimizer(model, lr, wd)
    best, best_state, best_score, best_epoch, wait = float("inf"), None, None, 0, 0
    for epoch in range(1, settings["max_epochs"] + 1):
        model.train()
        order = torch.randperm(len(ztr), generator=g).to(device)
        for i in range(0, len(order), settings["batch"]):
            b = order[i:i + settings["batch"]]
            opt.zero_grad(set_to_none=True)
            torch.nn.functional.binary_cross_entropy_with_logits(model(ztr[b]), ytr[b]).backward()
            opt.step()
        model.eval()
        with torch.no_grad():
            out = model(zva)
            if not torch.isfinite(out).all():
                raise ValueError("검증 출력에 NaN 또는 Inf가 있다")
            loss = torch.nn.functional.binary_cross_entropy_with_logits(out, yva).item()
        if loss < best:
            best, best_epoch, wait = loss, epoch, 0
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
            best_score = d5.r_selection(yva, torch.sigmoid(out)).nanmean().item()
        else:
            wait += 1
            if wait >= settings["patience"]:
                break
    if not np.isfinite(best_score):
        raise ValueError("선택 점수를 낼 수 없다")
    model.load_state_dict(best_state)
    return model, best, best_score, best_epoch


def soft_bce_task(brain, y_em, k, device, settings=d5.SOFT_BCE, decays=d5.SOFT_BCE_DECAYS, lrs=d5.SOFT_BCE_LRS):
    tr, va, te, _ = split_idx(brain.fold, k)
    x = d5.as_tensor(brain.X, device)
    z, _, _ = d5.standardize(x, tr)
    z = z.float()
    y = torch.as_tensor(np.asarray(y_em, np.float32), device=device)
    rows, chosen = [], None
    for wd in decays:
        for lr in lrs:
            model, loss, score, epoch = soft_bce_train(z[tr], y[tr], z[va], y[va], wd, lr, settings, device)
            rows.append(dict(weight_decay=wd, lr=lr, val_loss=loss, val_r=score, epoch=epoch))
            if chosen is None or score > chosen[1]:  # 같으면 작은 weight decay, 작은 learning rate(O6)
                chosen = (model, score, wd, lr)
    with torch.no_grad():
        p = torch.sigmoid(chosen[0](z[te])).cpu().numpy()
    return dict(video_id=brain.video_id[te], pred=c.finite(p, "soft BCE 예측")), pd.DataFrame(rows), dict(weight_decay=chosen[2], lr=chosen[3])


def video_task(x, y, fold, ids, k, device):
    """뇌를 쓰지 않는 기준선. 시험은 fold k의 개발 영상이고, 정답은 값 그대로다."""
    tr, va, te, _ = split_idx(fold, k)
    pred, pick = d5.main_version(d5.as_tensor(x, device), d5.as_tensor(y, device), tr, va, te)
    return dict(video_id=ids[te], pred=pred.cpu().numpy(), lambda_index=pick.cpu().numpy())


def zone_task(brain, y_em, split, block, k, kind, device, blocks=None, control=None):
    """학습 자료는 c.zone_sets가 정하고, 그중 이 참가자에게 block이 있는 영상만 쓴다."""
    train_ids, test_ids = c.zone_sets(split, block, k, kind, blocks, control)
    r = c.roles(k)
    fold_of = dict(zip(split.video_id, split.fold))
    tr_ids = [v for v in train_ids if fold_of[v] in r["train"]]
    va_ids = [v for v in train_ids if fold_of[v] == r["val"]]
    tr, va, te = brain.rows(tr_ids), brain.rows(va_ids), brain.rows(test_ids)
    pred, pick = d5.main_version(d5.as_tensor(brain.X, device), d5.as_tensor(y_em, device), tr, va, te)
    return dict(video_id=brain.video_id[te], pred=pred.cpu().numpy(), lambda_index=pick.cpu().numpy())


def h2020_fit(x, y, tr, te, lambdas, n_voxels):
    """목표마다 학습 자료의 상관 절댓값 상위 voxel을 고르고 λ마다 예측한다. 돌려주는 값은 λ × 시험 × 목표이고 원래 척도다."""
    z, _, _ = d5.standardize(x, tr)
    zy, ym, ys = d5.standardize(y, tr)
    ztr, zte, ty = z[tr], z[te], zy[tr]
    corr = ztr.T @ ty / len(tr)
    top = corr.abs().topk(min(n_voxels, x.shape[1]), dim=0).indices  # 선택 voxel × 목표
    q = y.shape[1]
    xq = ztr[:, top.T]  # 학습 × 목표 × 선택 voxel
    xq = xq.permute(1, 0, 2)
    xx = xq.transpose(1, 2) @ xq
    xy = (xq.transpose(1, 2) @ ty.T[:, :, None])
    values, vectors = torch.linalg.eigh(xx)
    vty = vectors.transpose(1, 2) @ xy
    te_x = zte[:, top.T].permute(1, 0, 2)
    out = []
    for lam in lambdas:
        w = vectors @ (vty / (values.clamp_min(0) + float(lam))[:, :, None])
        p = (te_x @ w)[:, :, 0].T
        out.append(p * ys + ym)
    out = torch.stack(out)
    if not torch.isfinite(out).all():
        raise ValueError("복셀 선택 ridge의 예측에 NaN 또는 Inf가 있다")
    return out


def h2020_roi(x, y, fold, dk_folds, te, lambdas=d5.H2020_LAMBDAS, n_voxels=d5.H2020_VOXELS):
    """ROI 하나. 안쪽 예측을 이어 붙인 r로 목표마다 λ를 고르고 D_k 전체로 학습한다."""
    dk = np.flatnonzero(np.isin(fold, dk_folds))
    merged, truth = [], []
    for j in dk_folds:
        tr, va = dk[fold[dk] != j], dk[fold[dk] == j]
        merged.append(h2020_fit(x, y, tr, va, lambdas, n_voxels))
        truth.append(y[va])
    merged, truth = torch.cat(merged, 1), torch.cat(truth)
    scores = torch.stack([d5.r_selection(truth, p) for p in merged])
    pick = d5.pick_per_target(scores)
    paths = h2020_fit(x, y, dk, te, lambdas, n_voxels)
    return paths.gather(0, pick[None, None, :].expand(1, len(te), y.shape[1]))[0], pick, scores.gather(0, pick[None])[0]


def h2020_ensemble(pred_by_roi, val_r, threshold=d5.H2020_ENSEMBLE_THRESHOLD):
    """공개 코드의 ensemble. 목표마다 안쪽 r이 기준 이상인 ROI의 예측을 평균하고, 없으면 안쪽 r이 가장 높은 ROI를 쓴다.
    공개 코드는 없을 때 시험 성능이 가장 높은 ROI를 쓰지만 시험 정보를 쓰지 않으려고 안쪽 r로 바꿨다(H5). pred_by_roi: 시험 × ROI × 목표."""
    use = val_r >= threshold
    count = use.sum(0)
    mean = (pred_by_roi * use[None]).sum(1) / np.maximum(count, 1)
    best = val_r.argmax(0)
    fallback = pred_by_roi[:, best, np.arange(pred_by_roi.shape[2])]
    return np.where(count > 0, mean, fallback), count


def h2020_task(brain, y_em, k, device, lambdas=d5.H2020_LAMBDAS, n_voxels=d5.H2020_VOXELS):
    r = c.roles(k)
    te = np.flatnonzero(brain.fold == k)
    y = d5.as_tensor(y_em, device)
    x = d5.as_tensor(brain.X, device)
    preds, picks, scores = [], [], []
    for pos in brain.roi_positions:
        p, pick, score = h2020_roi(x[:, torch.as_tensor(pos, device=device)], y, brain.fold, r["dk"], te, lambdas, n_voxels)
        preds.append(p.cpu().numpy().astype(np.float32))
        picks.append(pick.cpu().numpy())
        scores.append(score.cpu().numpy())
    pred_by_roi, val_r = np.stack(preds, 1), np.stack(scores)
    ensemble, count = h2020_ensemble(pred_by_roi, val_r)
    return dict(video_id=brain.video_id[te], pred=ensemble.astype(np.float32), n_roi_in_ensemble=count, pred_by_roi=pred_by_roi, val_r_by_roi=val_r.astype(np.float32), lambda_index=np.stack(picks))


def log_length(split):
    t = pd.read_csv(d5.STIMULI, sep="\t", comment="#").set_index("video_number").container_duration_s
    return np.log(t.loc[split.video_id].to_numpy(np.float64))[:, None]


def save(out, run, arrays, started, table=None, **extra):
    with c.Atomic(out) as tmp:
        np.savez(tmp / "pred.npz", **arrays)
        if table is not None:
            table.to_csv(tmp / "selection.tsv", sep="\t", index=False, float_format="%.6g")
        run.check()
        json.dump(dict(run.prov, **c.timing(started), **extra), open(tmp / "done.json", "w"), indent=1)
    print("저장", out, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, choices=["ridge", "soft_bce", "signal", "video", "zone", "h2020"])
    ap.add_argument("--participant", default="", choices=[""] + d5.HK)
    ap.add_argument("--design-freeze", default="")
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    c.guard(a.design_freeze)
    s = a.participant
    if a.task != "video" and not s:
        raise SystemExit("--participant가 필요하다")
    inputs = {"labels": c.LABELS}
    if a.task in ("ridge", "soft_bce", "zone", "h2020"):
        inputs.update({f"response:sub-{s}": d5.response_path(s), f"roi:sub-{s}": d5.roi_path(s)})
    if a.task == "signal":
        inputs[f"raw_response:sub-{s}"] = d5.response_path(s, normalized=False)
    if a.task == "video":
        inputs.update(stimuli=d5.STIMULI, lowlevel=c.FEATURES / f"{c.LOWLEVEL}.npy")
    run = d5.Run(a.design_freeze, inputs, task=a.task, lambdas=d5.LAMBDAS.tolist(), h2020_lambdas=d5.H2020_LAMBDAS.tolist(), soft_bce=d5.SOFT_BCE, decays=d5.SOFT_BCE_DECAYS, learning_rates=d5.SOFT_BCE_LRS)
    split = c.load_split()
    y_em, _ = c.load_scores(split, "emotions")
    y_dim, _ = c.load_scores(split, "dimensions")
    folds = range(1, c.N_FOLDS + 1)
    if a.task == "video":
        ids, fold = split.video_id.to_numpy(), split.fold.to_numpy()
        inputs_video = dict(length=log_length(split), lowlevel=c.load_rows(c.LOWLEVEL, ids, split))
        run.check()
        for name, x in inputs_video.items():
            for k in folds:
                out = d5.OUT / "video" / f"{name}_fold{k}"
                if not c.done_or_new(out, run.key):
                    started = time.time()
                    save(out, run, video_task(x, y_em, fold, ids, k, a.device), started, baseline=name, fold=k)
        return
    if a.task == "signal":
        x, ids = d5.signal_baseline_input(s, split)
        y = d5.align(y_em, split, ids)
        fold = d5.align(split.fold.to_numpy(), split, ids)
        run.check()
        for k in folds:
            out = d5.OUT / "signal" / f"sub-{s}_fold{k}"
            if not c.done_or_new(out, run.key):
                started = time.time()
                save(out, run, video_task(x, y, fold, ids, k, a.device), started, participant=s, fold=k)
        return
    brain = d5.load_brain(s, split)
    y = d5.align(y_em, split, brain.video_id)
    run.check()
    if a.task == "zone":
        for b in range(1, 6):
            for k in folds:
                for kind in ("excluded", "control"):
                    out = d5.OUT / "zone" / f"sub-{s}_block{b}_fold{k}_{kind}"
                    if not c.done_or_new(out, run.key):
                        started = time.time()
                        save(out, run, zone_task(brain, y, split, b, k, kind, a.device), started, participant=s, block=b, fold=k, kind=kind)
        return
    for k in folds:
        out = d5.OUT / a.task / f"sub-{s}_fold{k}"
        if c.done_or_new(out, run.key):
            continue
        started = time.time()
        if a.task == "ridge":
            save(out, run, ridge_task(brain, y, d5.align(y_dim, split, brain.video_id), k, a.device), started, participant=s, fold=k)
        elif a.task == "soft_bce":
            arrays, table, chosen = soft_bce_task(brain, y, k, a.device)
            save(out, run, arrays, started, table, participant=s, fold=k, chosen=chosen)
        else:
            save(out, run, h2020_task(brain, y, k, a.device), started, participant=s, fold=k)


if __name__ == "__main__":
    main()
