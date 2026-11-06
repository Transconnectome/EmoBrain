#!/usr/bin/env python3
"""S5 결과 점검과 층별 지표 (04 S5의 확인 기준, 01 O19, O20, N3, 2026-11-06).

확인: 64개 층 × 5명, 14개 차원 × 5명 × 6 fold의 두 판이 모두 있고, 시험 영상이 정해진 목록과 정확히 같으며, 값이 온전하고, 같은 역할의 입력은 내용이 같다.
지표: 시험 예측을 원래 척도로 모아 낸 차원별 r 평균(O20)과, 같은 fold 안 영상 식별(O19, 그 fold의 D_k 좌표), λ가 끝값인 횟수. 순열 기준은 S10이다.
사용: s5_collect.py --design-freeze <커밋>
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

import s4_common as c
import s5_common as d5
from s5_decoding import layer_name, load_targets

MANIFEST = c.CODE_DIR / "manifests/s5"


def check_pred(path, expected, keys):
    """keys: 이름 -> 출력 수. 영상과 크기와 값이 맞지 않으면 멈춘다."""
    t = np.load(path)
    ids = t["video_id"].tolist()
    if len(ids) != len(set(ids)):
        raise SystemExit(f"{path}: 같은 영상이 두 번 있다")
    if sorted(ids) != sorted(expected):
        raise SystemExit(f"{path}: 시험 영상이 정해진 목록과 다르다({len(ids)}개, 기대 {len(expected)}개)")
    for k, n in keys.items():
        if t[k].shape[0] != len(ids) or t[k].shape[1:] != (n if isinstance(n, tuple) else (n,)):
            raise SystemExit(f"{path}: {k}의 크기 {t[k].shape}가 다르다")
        if not np.isfinite(t[k]).all():
            raise SystemExit(f"{path}: {k}에 NaN 또는 Inf가 있다")
    return t


def check_runs(out, names, design_freeze=None):
    seen, code, freeze = {}, None, set()
    for n in names:
        d = json.loads((Path(out) / n / "done.json").read_text())
        code = d["code_sha256"] if code is None else code
        if d["code_sha256"] != code:
            raise SystemExit(f"{n}: 다른 코드로 만든 결과다")
        freeze.add(d["design_freeze"])
        for role, h in d["inputs"].items():
            if seen.setdefault(role, h) != h:
                raise SystemExit(f"{n}: 입력 {role}의 내용이 다른 결과와 다르다")
    if len(freeze) != 1 or (design_freeze is not None and freeze != {design_freeze}):
        raise SystemExit(f"결과의 설계 동결 커밋이 다르다: {freeze}")
    return seen


def identification(pred, true):
    """O19. A의 예측과 A의 실제의 r이 A의 예측과 B의 실제의 r보다 크면 1이다. 같은 fold의 모든 B를 평균하고 모든 A를 평균한다."""
    a = pred - pred.mean(1, keepdims=True)
    b = true - true.mean(1, keepdims=True)
    a = a / np.linalg.norm(a, axis=1, keepdims=True)
    b = b / np.linalg.norm(b, axis=1, keepdims=True)
    s = a @ b.T
    d = np.diag(s)
    n = len(s)
    if n < 2:
        raise ValueError("식별에는 영상이 둘 이상 있어야 한다")
    wins = (d[:, None] > s).sum(1)  # 자기 자신은 같아서 세지 않는다
    return float((wins / (n - 1)).mean())


def layer_metrics(preds, targets, split, participant):
    """preds: fold -> 예측 파일 값. targets: 층 -> split 순서의 실제 특징."""
    pos = {v: i for i, v in enumerate(split.video_id.tolist())}
    rows = []
    for layer, y in targets.items():
        name = layer_name(layer)
        all_pred, all_true, ids = [], [], []
        for k, t in preds.items():
            r = c.roles(k)
            dk = np.isin(split.fold.to_numpy(), r["dk"])
            m, s = y[dk].astype(np.float64).mean(0), y[dk].astype(np.float64).std(0)
            at = [pos[v] for v in t["video_id"].tolist()]
            true = y[at]
            ids.append(identification((t[name] - m) / s, (true - m) / s))
            all_pred.append(t[name]), all_true.append(true)
        r = c.pearson(np.concatenate(all_true), np.concatenate(all_pred))
        rows.append(dict(participant=participant, model=layer[0], layer=layer[1], mean_r=float(np.nanmean(r)), n_dim_not_computable=int(np.isnan(r).sum()), identification=float(np.mean(ids))))
    return pd.DataFrame(rows)


def expected_tests(split, table, s):
    t = table[table.participant == f"sub-{s}"]
    return {k: t.video_id[t.video_id.isin(split.video_id[split.fold == k])].tolist() for k in range(1, c.N_FOLDS + 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--design-freeze", default="")
    a = ap.parse_args()
    c.guard(a.design_freeze)
    split = c.load_split()
    table = pd.read_csv(d5.BLOCKS, sep="\t")
    blocks = pd.read_csv(c.S2 / "content_blocks_assignment.tsv", sep="\t")
    targets = load_targets(split)
    names, metric, chosen = [], [], []
    keys = {layer_name(l): len(targets[l][0]) for l in targets}
    for s in d5.HK:
        exp = expected_tests(split, table, s)
        preds = {}
        for k in range(1, c.N_FOLDS + 1):
            d = d5.OUT / "decoding" / f"sub-{s}_fold{k}"
            names.append(f"decoding/sub-{s}_fold{k}")
            preds[k] = check_pred(d / "test_pred.npz", exp[k], keys)
            t = pd.read_csv(d / "chosen.tsv", sep="\t")
            t.insert(0, "fold", k), t.insert(0, "participant", s)
            chosen.append(t)
            names.append(f"ridge/sub-{s}_fold{k}")
            check_pred(d5.OUT / "ridge" / f"sub-{s}_fold{k}" / "pred.npz", exp[k], dict(emotion_main=34, emotion_literature=34, dimension_main=14, dimension_literature=14))
            for task in ("soft_bce", "signal"):
                names.append(f"{task}/sub-{s}_fold{k}")
                check_pred(d5.OUT / task / f"sub-{s}_fold{k}" / "pred.npz", exp[k], dict(pred=34))
            names.append(f"h2020/sub-{s}_fold{k}")
            check_pred(d5.OUT / "h2020" / f"sub-{s}_fold{k}" / "pred.npz", exp[k], dict(pred=34, pred_by_roi=(370, 34)))
            for b in sorted(blocks.block.unique().tolist()):
                want = sorted(set(exp[k]) & set(blocks.video_id[blocks.block == b]))
                for kind in ("excluded", "control"):
                    names.append(f"zone/sub-{s}_block{b}_fold{k}_{kind}")
                    check_pred(d5.OUT / "zone" / f"sub-{s}_block{b}_fold{k}_{kind}" / "pred.npz", want, dict(pred=34))
        metric.append(layer_metrics(preds, targets, split, f"sub-{s}"))
    for name in ("length", "lowlevel"):
        for k in range(1, c.N_FOLDS + 1):
            names.append(f"video/{name}_fold{k}")
            check_pred(d5.OUT / "video" / f"{name}_fold{k}" / "pred.npz", split.video_id[split.fold == k].tolist(), dict(pred=34))
    check_runs(d5.OUT, names, a.design_freeze)
    MANIFEST.mkdir(parents=True, exist_ok=True)
    pd.concat(chosen).to_csv(MANIFEST / "decoding_lambda.tsv", sep="\t", index=False, float_format="%.6g")
    pd.concat(metric).to_csv(MANIFEST / "decoding_layer_metrics.tsv", sep="\t", index=False, float_format="%.6g")
    print("층별 표를 저장했다", MANIFEST, flush=True)


if __name__ == "__main__":
    main()
