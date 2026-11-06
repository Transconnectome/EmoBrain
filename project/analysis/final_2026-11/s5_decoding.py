#!/usr/bin/env python3
"""S5 층별 feature decoding (04 S5, 01 2-1, H3, O18, O20, O21, O34, 2026-11-06).

참가자, 바깥 fold마다 V-JEPA 2 block 40개와 DeBERTa 층 24개에 ridge decoder를 따로 둔다.
- λ는 층마다 D_k 안쪽 5겹의 차원별 r 평균으로 하나 고른다(O18). 표준화는 regression마다 그 학습 자료로 한다(N3).
- 고른 λ로 D_k 전체에서 학습해 시험 fold를 예측한다. 예측은 원래 척도로 저장한다(O20).
- 주 목표 층(O21)은 안쪽 5겹의 fold 밖 예측도 저장한다. N8의 ridge 보정 통계에 쓴다(O34).
결과는 보고만 하고, 이 결과로 목표 층을 다시 고르지 않는다. 뇌 입력 외의 정답은 읽지 않는다. 순열 검정은 S10이다.
사용: s5_decoding.py --participant 01 --design-freeze <커밋> [--device cuda]
"""
import argparse
import json

import numpy as np
import pandas as pd
import torch

import s4_common as c
import s5_common as d5


def load_targets(split):
    """split 순서의 층별 특징. 개발 영상의 행만 읽는다."""
    ids = split.video_id.to_numpy()
    c.check_dev(ids, split)
    v = np.load(c.FEATURES / "vjepa2/blocks.npy", mmap_mode="r")
    t = np.load(c.FEATURES / "deberta/video_mean.npy", mmap_mode="r")
    out = {}
    for b in d5.VISUAL_LAYERS:
        out[("vjepa2", b)] = c.finite(np.asarray(v[ids - 1, b - 1], np.float32), f"vjepa2 block {b}")
    for l in d5.CAPTION_LAYERS:
        out[("deberta", l)] = c.finite(np.asarray(t[ids - 1, l - 1], np.float32), f"deberta 층 {l}")
    return out


def layer_name(layer):
    return f"{layer[0]}_{layer[1]:02d}"


def decode_fold(brain, targets_by_row, layers, target_layers, k, device, lambdas=d5.LAMBDAS):
    """targets_by_row: 층 -> brain 행 순서의 특징(원래 척도). 돌려주는 값: 시험 예측, 선택표, 곡선, 안쪽 fold 밖 예측."""
    r = c.roles(k)
    x = d5.as_tensor(brain.X, device)
    dk = np.flatnonzero(np.isin(brain.fold, r["dk"]))
    test = np.flatnonzero(brain.fold == k)
    scores = {layer: [] for layer in layers}
    inner_preds = {layer: {} for layer in target_layers}
    inner_rows = {}
    for j in r["dk"]:
        tr, va = dk[brain.fold[dk] != j], dk[brain.fold[dk] == j]
        inner_rows[j] = va
        model = d5.DualRidge(x, tr, dict(val=va))
        for layer in layers:
            y = d5.as_tensor(targets_by_row[layer], device)
            zy, ym, ys = d5.standardize(y, tr)
            fitted = model.fit(zy[tr])
            per_lambda = []
            keep = []
            for lam in lambdas:
                p = model.predict("val", fitted, lam)
                per_lambda.append(d5.r_selection(zy[va], p))
                if layer in inner_preds:
                    keep.append((p * ys + ym).cpu().numpy().astype(np.float32))
            scores[layer].append(torch.stack(per_lambda).nanmean(1))  # 차원별 r 평균(O18)
            if layer in inner_preds:
                inner_preds[layer][j] = np.stack(keep)
        del model
    curves, rows, chosen = {}, [], {}
    for layer in layers:
        s = torch.stack(scores[layer])  # 겹 × λ
        mean = s.mean(0)
        if not torch.isfinite(mean).all():
            raise ValueError(f"{layer}: 선택 점수를 낼 수 없다")
        i = int(mean.argmax())  # 같으면 작은 λ
        chosen[layer] = i
        curves[layer_name(layer)] = mean.cpu().numpy()
        rows.append(dict(model=layer[0], layer=layer[1], lambda_index=i, lam=float(lambdas[i]), at_end=i in (0, len(lambdas) - 1), val_r=float(mean[i])))
    model = d5.DualRidge(x, dk, dict(test=test))
    preds = {}
    for layer in layers:
        y = d5.as_tensor(targets_by_row[layer], device)
        zy, ym, ys = d5.standardize(y, dk)
        fitted = model.fit(zy[dk])
        preds[layer_name(layer)] = c.finite((model.predict("test", fitted, lambdas[chosen[layer]]) * ys + ym).cpu().numpy().astype(np.float32), "시험 예측")
    oof = dict(video_id=np.concatenate([brain.video_id[inner_rows[j]] for j in r["dk"]]), inner_fold=np.concatenate([np.full(len(inner_rows[j]), j) for j in r["dk"]]))
    for layer in target_layers:
        oof[layer_name(layer)] = np.concatenate([inner_preds[layer][j][chosen[layer]] for j in r["dk"]])
    return dict(video_id=brain.video_id[test], **preds), pd.DataFrame(rows), curves, oof


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--participant", required=True, choices=d5.HK)
    ap.add_argument("--design-freeze", default="")
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    c.guard(a.design_freeze)
    s = a.participant
    run = d5.Run(a.design_freeze, {f"response:sub-{s}": d5.response_path(s), f"roi:sub-{s}": d5.roi_path(s), "vjepa2_blocks": c.FEATURES / "vjepa2/blocks.npy", "deberta_video_mean": c.FEATURES / "deberta/video_mean.npy"}, task="decoding", lambdas=d5.LAMBDAS.tolist())
    split = c.load_split()
    brain = d5.load_brain(s, split)
    targets = {layer: d5.align(v, split, brain.video_id) for layer, v in load_targets(split).items()}
    run.check()
    for k in range(1, c.N_FOLDS + 1):
        out = d5.OUT / "decoding" / f"sub-{s}_fold{k}"
        if c.done_or_new(out, run.key):
            print("건너뜀", out, flush=True)
            continue
        with c.Atomic(out) as tmp:
            pred, table, curves, oof = decode_fold(brain, targets, d5.LAYERS, d5.TARGET_LAYERS, k, a.device)
            np.savez(tmp / "test_pred.npz", **pred)
            np.savez(tmp / "inner_oof_target.npz", **oof)
            np.savez(tmp / "curves.npz", **curves)
            table.to_csv(tmp / "chosen.tsv", sep="\t", index=False, float_format="%.6g")
            run.check()
            json.dump(dict(run.prov, participant=s, fold=k, n_voxels=brain.X.shape[1], n_voxels_with_overlap=brain.n_voxels_with_overlap), open(tmp / "done.json", "w"), indent=1)
        print("저장", out, flush=True)


if __name__ == "__main__":
    main()
