#!/usr/bin/env python3
"""S4 결과 점검과 요약 표 (04 S4의 확인 기준, 2026-11-06). 특징 모델 결과는 사전 분석이다(E6, N43).

확인
- 모든 결과가 같은 코드, 같은 S2 표, 같은 설계 동결 커밋에서 나왔고, 같은 역할의 입력은 경로와 상관없이 내용이 같다. 같은 과제의 결과는 설정도 같다.
- 시험 예측은 정해진 시험 영상을 정확히 한 번씩 담는다(누락, 중복, 범위 밖 금지). 평가에도 그 목록만 쓴다.
- OOF 영상이 그 fold의 H2 학습 fold와 정확히 같고, 저장한 값에 NaN과 Inf가 없으며, 행 수가 영상 수와 같다.
- K1a의 입력 좌표가 K1 head와 같다.
출력: manifests/s4/feature_model_selection.tsv(fold별 epoch, r, weight decay), OUT/summary/의 성능 표. 사용: s4_collect.py --design-freeze <커밋>
"""
import argparse
import json

import numpy as np
import pandas as pd

import s4_common as c

MANIFEST = c.CODE_DIR / "manifests/s4"
FOLD_TASKS = ("stimulus", "k1a", "noemo")
ALL_TASKS = ("stimulus", "k1a", "noemo", "zone", "baseline")
N_OUT = dict(stimulus=34, noemo=34, zone=34, baseline=34, k1a=14)
PRED_KEYS = dict(stimulus=("logit", "p", "additive_logit", "additive_p", "interaction_logit", "interaction_p"), noemo=("logit", "p"), zone=("logit", "p"), baseline=("logit", "p"), k1a=("additive_z", "additive_score", "interaction_z", "interaction_score"))


def _load(path):
    return json.loads((path / "chosen.json").read_text())


def fold_ids(split, k):
    return split.video_id[split.fold == k].tolist()


def expected_tests(split, task, blocks=None):
    """과제의 결과 폴더 이름 -> 시험 영상. 구역은 그 구역과 그 fold의 영상이다."""
    if task in FOLD_TASKS:
        return {f"fold{k}": fold_ids(split, k) for k in range(1, c.N_FOLDS + 1)}
    if task == "baseline":
        return {f"{m}_fold{k}": fold_ids(split, k) for m in c.BASELINE_FEATURES for k in range(1, c.N_FOLDS + 1)}
    blocks = pd.read_csv(c.S2 / "content_blocks_assignment.tsv", sep="\t") if blocks is None else blocks
    out = {}
    for b in sorted(blocks.block.unique().tolist()):
        for k in range(1, c.N_FOLDS + 1):
            ids = sorted(set(blocks.video_id[blocks.block == b]) & set(fold_ids(split, k)))
            for kind in ("excluded", "control"):
                out[f"block{b}_fold{k}_{kind}"] = ids
    return out


def check_pred(path, expected, keys, n_out):
    """파일의 영상이 expected와 정확히 같고 값이 온전해야 한다. 어긋나면 멈춘다."""
    t = np.load(path)
    ids = t["video_id"].tolist()
    if len(ids) != len(set(ids)):
        raise SystemExit(f"{path}: 같은 영상이 두 번 있다")
    if sorted(ids) != sorted(expected):
        raise SystemExit(f"{path}: 시험 영상이 정해진 목록과 다르다({len(ids)}개, 기대 {len(expected)}개)")
    for k in keys:
        if t[k].shape != (len(ids), n_out):
            raise SystemExit(f"{path}: {k}의 크기 {t[k].shape}가 (영상 {len(ids)}, 출력 {n_out})과 다르다")
        if not np.isfinite(t[k]).all():
            raise SystemExit(f"{path}: {k}에 NaN 또는 Inf가 있다")
    return t


def check_oof(path, expected, n_out):
    t = check_pred(path, expected, ("logit", "p_raw", "p_clipped"), n_out)
    if not ((t["p_clipped"] >= 0) & (t["p_clipped"] <= 1)).all() or not np.array_equal(t["p_clipped"], np.clip(t["p_raw"], 0, 1)):
        raise SystemExit(f"{path}: 자른 값이 자르기 전 값과 맞지 않는다")
    return t


def check_folds(split, out=None, tasks=ALL_TASKS, blocks=None, n_out=None):
    out = c.OUT if out is None else out
    n_out = N_OUT if n_out is None else n_out
    for task in tasks:
        for name, ids in expected_tests(split, task, blocks).items():
            check_pred(out / task / name / "test_pred.npz", ids, PRED_KEYS[task], n_out[task])
    for k in range(1, c.N_FOLDS + 1):
        r = c.roles(k)
        check_oof(out / "stimulus" / f"fold{k}" / "oof.npz", split.video_id[split.fold.isin(r["train"])].tolist(), n_out["stimulus"])
        coord = np.load(out / "stimulus" / f"fold{k}" / "coordinates.npz")
        k1a = np.load(out / "k1a" / f"fold{k}" / "coordinates.npz")
        for n in ("visual_mean", "visual_std", "caption_mean", "caption_std"):
            if not np.array_equal(coord[n], k1a[n]):
                raise SystemExit(f"fold {k}: K1a의 입력 좌표가 K1 head와 다르다")


def check_runs(out, names, design_freeze=None, current=None):
    """모든 결과가 같은 코드, 같은 동결 커밋에서 나왔고 같은 역할의 입력이 같은 내용인지 본다. 경로는 비교하지 않는다. 다른 폴더의 사본이어도 내용이 다르면 잡힌다.
    같은 과제의 결과는 설정도 같아야 한다. current는 역할 -> 해시 함수이고, 주면 지금 파일과도 맞춘다."""
    seen, code, freeze, settings = {}, None, set(), {}
    for n in names:
        d = json.loads((out / n / "done.json").read_text())
        if code is None:
            code = d["code_sha256"]
        if d["code_sha256"] != code:
            raise SystemExit(f"{n}: 다른 코드로 만든 결과다")
        freeze.add(d["design_freeze"])
        for role, h in d["inputs"].items():
            if seen.setdefault(role, h) != h:
                raise SystemExit(f"{n}: 입력 {role}의 내용이 다른 결과와 다르다")
        task = n.split("/")[0]
        if settings.setdefault(task, d["settings"]) != d["settings"]:
            raise SystemExit(f"{n}: 같은 과제인데 설정이 다르다")
    if len(freeze) != 1 or (design_freeze is not None and freeze != {design_freeze}):
        raise SystemExit(f"결과의 설계 동결 커밋이 다르다: {freeze}")
    if current is not None:
        for role, h in seen.items():
            if current(role) != h:
                raise SystemExit(f"지금의 {role}가 결과를 만들 때와 다르다")
    return seen


def selection_table(out=None, tasks=ALL_TASKS):
    """fold별 고른 epoch, rank r, weight decay, learning rate. 구역과 baseline 특징은 block, kind, feature 열로 구별한다."""
    out = c.OUT if out is None else out
    rows = []
    if "stimulus" in tasks:
        for k in range(1, c.N_FOLDS + 1):
            for n, v in _load(out / "stimulus" / f"fold{k}").items():
                rows.append(dict(model="Stimulus Model", fold=k, version=n, **v))
            oof = json.loads((out / "stimulus" / f"fold{k}" / "done.json").read_text())["oof_chosen"]
            rows.append(dict(model="Stimulus Model", fold=k, version="nested_oof", **oof))
    if "k1a" in tasks:
        for k in range(1, c.N_FOLDS + 1):
            for n, v in _load(out / "k1a" / f"fold{k}").items():
                rows.append(dict(model="K1a", fold=k, version=n, **v))
    if "noemo" in tasks:
        for k in range(1, c.N_FOLDS + 1):
            rows.append(dict(model="noemo", fold=k, version="all_ranks", **_load(out / "noemo" / f"fold{k}")))
    if "zone" in tasks:
        for b in range(1, 6):
            for k in range(1, c.N_FOLDS + 1):
                for kind in ("excluded", "control"):
                    rows.append(dict(model="zone", fold=k, version="all_ranks", block=b, kind=kind, **_load(out / "zone" / f"block{b}_fold{k}_{kind}")))
    if "baseline" in tasks:
        for m in c.BASELINE_FEATURES:
            for k in range(1, c.N_FOLDS + 1):
                rows.append(dict(model="baseline", fold=k, version="all_ranks", feature=m, **_load(out / "baseline" / f"{m}_fold{k}")))
    t = pd.DataFrame(rows)
    t["at_cap"] = t.epochs >= c.MAX_EPOCHS  # 탐색 범위의 끝이 선택됐다는 뜻이다. 그 뒤로 좋아지는지는 확인하지 않았다
    return t


def check_d12(path, ids, n_blocks=40, n_caption=4096, n_lowlevel=6558):
    """D12의 표, 차원별 R², block별 원래 척도 시험 예측. 없거나 크기가 다르면 멈춘다."""
    t = pd.read_csv(path / "d12.tsv", sep="\t")
    want = sorted((b, n) for b in range(1, n_blocks + 1) for n in ("caption", "lowlevel"))
    if sorted(zip(t.block, t.target)) != want:
        raise SystemExit(f"{path}: d12.tsv의 block과 목표가 다르다")
    r2 = np.load(path / "d12_r2_per_dimension.npz")
    sizes = dict(caption=n_caption, lowlevel=n_lowlevel)
    for b in range(1, n_blocks + 1):
        p = np.load(path / "predictions" / f"block{b:02d}.npz")
        if p["video_id"].tolist() != list(ids):
            raise SystemExit(f"{path}: block {b}의 시험 영상이 개발 영상과 다르다")
        for n, q in sizes.items():
            if r2[f"block{b}_{n}"].shape != (q,) or p[n].shape != (len(ids), q) or not np.isfinite(p[n]).all():
                raise SystemExit(f"{path}: block {b}의 {n} 크기나 값이 잘못됐다")


def check_noemo_ridge(path, ids, n_emotion=34, n_folds=c.N_FOLDS):
    """정서어 제거판 ridge의 표와 예측, fold별 λ 번호."""
    t = pd.read_csv(path / "noemo_ridge.tsv", sep="\t")
    if sorted(t.caption.value_counts().to_dict().items()) != [("no_emotion_words", n_emotion), ("original", n_emotion)]:
        raise SystemExit(f"{path}: noemo_ridge.tsv의 행이 다르다")
    p = np.load(path / "noemo_ridge_pred.npz")
    if p["video_id"].tolist() != list(ids):
        raise SystemExit(f"{path}: 시험 영상이 개발 영상과 다르다")
    for n in ("original", "no_emotion_words"):
        if p[n].shape != (len(ids), n_emotion) or not np.isfinite(p[n]).all():
            raise SystemExit(f"{path}: {n} 예측의 크기나 값이 잘못됐다")
        for k in range(1, n_folds + 1):
            if p[f"{n}_lambda_index_fold{k}"].shape != (n_emotion,):
                raise SystemExit(f"{path}: {n}의 fold {k} λ 번호가 없다")


def check_window_change(path, n_videos, n_blocks=4):
    """창 사이 변화 표. 영벡터로 계산 불가인 값은 허용하고 그 건수가 요약에 있어야 한다."""
    t = pd.read_csv(path / "window_change.tsv", sep="\t")
    if len(t) != n_videos * n_blocks or t.video_id.nunique() != n_videos:
        raise SystemExit(f"{path}: window_change.tsv의 행 수가 다르다")
    s = pd.read_csv(path / "window_change_summary.tsv", sep="\t")
    if len(s) != n_blocks or not {"n_valid", "n_not_computable"} <= set(s.columns):
        raise SystemExit(f"{path}: 요약 표가 다르다")


def pooled(out, task, expected, y, ids, key):
    """정해진 시험 영상의 예측을 한 번씩 모아 출력별 r을 낸다. 비율과 되돌린 점수는 원래 척도라 그대로 모은다(O20, K1a)."""
    pos = {v: i for i, v in enumerate(ids.tolist())}
    p = np.full(y.shape, np.nan)
    rows = []
    for name, want in expected.items():
        t = check_pred(out / task / name / "test_pred.npz", want, (key,), y.shape[1])
        at = [pos[v] for v in t["video_id"].tolist()]
        if set(at) & set(rows):
            raise SystemExit(f"{name}: 다른 결과와 영상이 겹친다")
        p[at] = t[key]
        rows += at
    return c.pearson(y[rows], p[rows]), len(rows)


def summaries(split, y_em, y_dim, em_cols, dim_cols, out=None, blocks=None):
    out = c.OUT if out is None else out
    ids = split.video_id.to_numpy()
    folds = expected_tests(split, "stimulus")
    r, _ = pooled(out, "stimulus", folds, y_em, ids, "p")
    stim = pd.DataFrame(dict(emotion=em_cols, r=r))
    for v in ("additive", "interaction"):
        stim[f"r_{v}"], _ = pooled(out, "stimulus", folds, y_em, ids, f"{v}_p")
    stim["r_no_emotion_words"], _ = pooled(out, "noemo", folds, y_em, ids, "p")
    for m in c.BASELINE_FEATURES:
        stim[f"r_baseline_{m}"], _ = pooled(out, "baseline", {f"{m}_fold{k}": folds[f"fold{k}"] for k in range(1, c.N_FOLDS + 1)}, y_em, ids, "p")
    k1a = pd.DataFrame(dict(dimension=dim_cols))
    for v in ("additive", "interaction"):
        k1a[f"r_{v}"], _ = pooled(out, "k1a", folds, y_dim, ids, f"{v}_score")
    z = []
    zone = expected_tests(split, "zone", blocks)
    for b in sorted({int(n.split("_")[0][5:]) for n in zone}):
        for kind in ("excluded", "control"):
            want = {n: v for n, v in zone.items() if n.startswith(f"block{b}_") and n.endswith(kind)}
            r, n = pooled(out, "zone", want, y_em, ids, "p")
            z.append(pd.DataFrame(dict(block=b, kind=kind, emotion=em_cols, r=r, n_test=n)))
    return stim, k1a, pd.concat(z, ignore_index=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--design-freeze", default="")
    a = ap.parse_args()
    c.guard(a.design_freeze)
    split = c.load_split()
    blocks = pd.read_csv(c.S2 / "content_blocks_assignment.tsv", sep="\t")
    names = [f"{t}/{n}" for t in ALL_TASKS for n in expected_tests(split, t, blocks)] + ["ridge_d12", "ridge_noemo", "window_change"]
    paths = c.role_paths()
    check_runs(c.OUT, names, a.design_freeze, current=lambda role: c.sha256(paths[role]))
    check_folds(split, blocks=blocks)
    ids = split.video_id.tolist()
    check_d12(c.OUT / "ridge_d12", ids)
    check_noemo_ridge(c.OUT / "ridge_noemo", ids)
    windows = np.load(c.FEATURES / "vjepa2/windows_per_video.npz")
    check_window_change(c.OUT / "window_change", len(set(int(k[1:]) for k in windows.files) & set(ids)))
    MANIFEST.mkdir(parents=True, exist_ok=True)
    sel = selection_table()
    sel.to_csv(MANIFEST / "feature_model_selection.tsv", sep="\t", index=False, float_format="%.6g")
    y_em, em_cols = c.load_scores(split, "emotions")
    y_dim, dim_cols = c.load_scores(split, "dimensions")
    stim, k1a, zone = summaries(split, y_em, y_dim, em_cols, dim_cols, blocks=blocks)
    (c.OUT / "summary").mkdir(exist_ok=True)
    stim.to_csv(c.OUT / "summary/feature_model_test_r.tsv", sep="\t", index=False, float_format="%.6g")
    k1a.to_csv(c.OUT / "summary/k1a_test_r.tsv", sep="\t", index=False, float_format="%.6g")
    zone.to_csv(c.OUT / "summary/zone_test_r.tsv", sep="\t", index=False, float_format="%.6g")
    print(sel.to_string(index=False))


if __name__ == "__main__":
    main()
