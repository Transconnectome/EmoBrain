#!/usr/bin/env python3
"""S4 결과 점검과 요약 표 (04 S4의 확인 기준, 2026-11-06). 특징 모델 결과는 사전 분석이다(E6, N43).

확인: OOF 영상이 그 fold의 H2 학습 fold에만 있고, 시험 예측이 시험 fold에만 있으며, 표준화 통계에 시험 fold가 들어가지 않았고, K1a의 입력 좌표가 K1 head와 같다.
출력: manifests/s4/feature_model_selection.tsv(fold별 epoch, r, weight decay), OUT/summary/의 성능 표. 사용: s4_collect.py --design-freeze <커밋>
"""
import argparse
import json

import numpy as np
import pandas as pd

import s4_common as c

MANIFEST = c.CODE_DIR / "manifests/s4"


def _load(path):
    return json.loads((path / "chosen.json").read_text())


def selection_table(out=None):
    out = c.OUT if out is None else out
    rows = []
    for k in range(1, c.N_FOLDS + 1):
        ch = _load(out / "tvs" / f"fold{k}")
        for n, v in ch.items():
            rows.append(dict(model="T_VS", fold=k, version=n, **v))
        oof = json.loads((out / "tvs" / f"fold{k}" / "done.json").read_text())["oof_chosen"]
        rows.append(dict(model="T_VS", fold=k, version="nested_oof", **oof))
        for n, v in _load(out / "k1a" / f"fold{k}").items():
            rows.append(dict(model="K1a", fold=k, version=n, **v))
    return pd.DataFrame(rows)


def check_folds(split, out=None):
    """04 S4의 확인 기준. 어긋나면 멈춘다."""
    out = c.OUT if out is None else out
    fold_of = dict(zip(split.video_id, split.fold))
    for k in range(1, c.N_FOLDS + 1):
        r = c.roles(k)
        d = out / "tvs" / f"fold{k}"
        o = np.load(d / "oof.npz")
        if sorted(o["video_id"].tolist()) != sorted(split.video_id[split.fold.isin(r["train"])].tolist()):
            raise SystemExit(f"fold {k}: OOF 영상이 H2 학습 fold와 다르다")
        if not ((o["p_clipped"] >= 0) & (o["p_clipped"] <= 1)).all() or (o["p_raw"].shape != o["logit"].shape):
            raise SystemExit(f"fold {k}: OOF 값이 범위를 벗어났다")
        te = np.load(d / "test_pred.npz")["video_id"]
        if {fold_of[v] for v in te.tolist()} != {k}:
            raise SystemExit(f"fold {k}: 시험 예측이 시험 fold 밖에 있다")
        coord = np.load(d / "coordinates.npz")
        k1a = np.load(out / "k1a" / f"fold{k}" / "coordinates.npz")
        for n in ("visual_mean", "visual_std", "caption_mean", "caption_std"):
            if not np.array_equal(coord[n], k1a[n]):
                raise SystemExit(f"fold {k}: K1a의 입력 좌표가 K1 head와 다르다")


def pooled(out, task, names, y, ids, key):
    """fold의 시험 예측을 모아 출력별 r을 낸다. 비율과 되돌린 점수는 원래 척도라 그대로 모은다(O20, K1a)."""
    pos = {v: i for i, v in enumerate(ids.tolist())}
    p = np.full(y.shape, np.nan)
    seen = []
    for n in names:
        t = np.load(out / task / n / "test_pred.npz")
        p[[pos[v] for v in t["video_id"].tolist()]] = t[key]
        seen += t["video_id"].tolist()
    rows = [pos[v] for v in seen]
    return c.pearson(y[rows], p[rows]), len(rows)


def summaries(split, y_em, y_dim, em_cols, dim_cols, out=None):
    out = c.OUT if out is None else out
    ids = split.video_id.to_numpy()
    folds = [f"fold{k}" for k in range(1, c.N_FOLDS + 1)]
    r, _ = pooled(out, "tvs", folds, y_em, ids, "p")
    tvs = pd.DataFrame(dict(emotion=em_cols, r=r))
    r0, _ = pooled(out, "noemo", folds, y_em, ids, "p")
    tvs["r_no_emotion_words"] = r0
    k1a = pd.DataFrame(dict(dimension=dim_cols))
    for v in ("additive", "interaction"):
        k1a[f"r_{v}"], _ = pooled(out, "k1a", folds, y_dim, ids, f"{v}_score")
    z = []
    for b in range(1, 6):
        for kind in ("excluded", "control"):
            r, n = pooled(out, "zone", [f"block{b}_fold{k}_{kind}" for k in range(1, c.N_FOLDS + 1)], y_em, ids, "p")
            z.append(pd.DataFrame(dict(block=b, kind=kind, emotion=em_cols, r=r, n_test=n)))
    return tvs, k1a, pd.concat(z, ignore_index=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--design-freeze", default="")
    a = ap.parse_args()
    c.guard(a.design_freeze)
    split = c.load_split()
    check_folds(split)
    MANIFEST.mkdir(parents=True, exist_ok=True)
    sel = selection_table()
    sel.to_csv(MANIFEST / "feature_model_selection.tsv", sep="\t", index=False, float_format="%.6g")
    y_em, em_cols = c.load_scores(split, "emotions")
    y_dim, dim_cols = c.load_scores(split, "dimensions")
    tvs, k1a, zone = summaries(split, y_em, y_dim, em_cols, dim_cols)
    (c.OUT / "summary").mkdir(exist_ok=True)
    tvs.to_csv(c.OUT / "summary/feature_model_test_r.tsv", sep="\t", index=False, float_format="%.6g")
    k1a.to_csv(c.OUT / "summary/k1a_test_r.tsv", sep="\t", index=False, float_format="%.6g")
    zone.to_csv(c.OUT / "summary/zone_test_r.tsv", sep="\t", index=False, float_format="%.6g")
    print(sel.to_string(index=False))


if __name__ == "__main__":
    main()
