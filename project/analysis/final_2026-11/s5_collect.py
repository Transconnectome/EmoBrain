#!/usr/bin/env python3
"""S5 결과 점검과 층별 지표 (04 S5의 확인 기준, 01 O19, O20, N3, 2026-11-06).

확인: 64개 층 × 5명, 14개 차원 × 5명 × 6 fold의 두 판과 O34의 안쪽 fold 밖 예측, λ 선택 기록이 모두 있고, 시험 영상이 정해진 목록과 정확히 같으며, 값이 온전하다.
결과끼리 코드, 동결 커밋, 같은 역할의 입력 내용이 같고, 같은 과제는 설정도 같으며, 지금 파일이 결과를 만들 때와 같다.
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


def check_array(t, key, shape, path, low=None, high=None, integer=False):
    """필수 배열의 크기와 값의 범위. low 이상 high 미만. integer면 정수 배열이어야 한다(λ 번호, ROI 수)."""
    if key not in t:
        raise SystemExit(f"{path}: {key}가 없다")
    v = t[key]
    if v.shape != tuple(shape):
        raise SystemExit(f"{path}: {key}의 크기 {v.shape}가 {tuple(shape)}와 다르다")
    if integer and not np.issubdtype(v.dtype, np.integer):
        raise SystemExit(f"{path}: {key}가 정수가 아니다")
    if not np.isfinite(v).all():
        raise SystemExit(f"{path}: {key}에 NaN 또는 Inf가 있다")
    if low is not None and ((v < low).any() or (v >= high).any()):
        raise SystemExit(f"{path}: {key}의 값이 범위를 벗어났다")


def check_inner_oof(path, dk_ids, fold_of, keys):
    """O34. 영상은 그 참가자의 D_k와 정확히 같고, inner_fold는 영상의 실제 fold다."""
    t = check_pred(path, dk_ids, keys)
    if "inner_fold" not in t or t["inner_fold"].tolist() != [fold_of[v] for v in t["video_id"].tolist()]:
        raise SystemExit(f"{path}: inner_fold가 영상의 실제 fold와 다르다")
    return t


def check_chosen(path, layers, n_lambda):
    """기대한 층이 한 번씩 있고 λ 번호가 범위 안이다."""
    t = pd.read_csv(path, sep="\t")
    if sorted(zip(t.model, t.layer)) != sorted(layers):
        raise SystemExit(f"{path}: 층 목록이 다르다")
    if not np.issubdtype(t.lambda_index.dtype, np.integer) or ((t.lambda_index < 0) | (t.lambda_index >= n_lambda)).any():
        raise SystemExit(f"{path}: λ 번호가 범위를 벗어났다")
    return t


def check_baseline(out, task, name, expected, n_emotion=34, n_dimension=14, n_roi=370):
    """과제별 필수 파일과 배열. out은 결과 폴더의 뿌리다."""
    path = Path(out) / task / name / "pred.npz"
    n = len(d5.LAMBDAS)
    if task == "ridge":
        t = check_pred(path, expected, dict(emotion_main=n_emotion, emotion_literature=n_emotion, dimension_main=n_dimension, dimension_literature=n_dimension))
        check_array(t, "lambda_main", (n_emotion + n_dimension,), path, 0, n, integer=True)
        check_array(t, "lambda_literature", (n_emotion + n_dimension,), path, 0, n, integer=True)
        check_array(t, "mean_prediction", (n_emotion,), path, 0, 1.000001)
    elif task == "soft_bce":
        t = check_pred(path, expected, dict(pred=n_emotion))
        if len(pd.read_csv(Path(out) / task / name / "selection.tsv", sep="\t")) != len(d5.SOFT_BCE_DECAYS):
            raise SystemExit(f"{path}: weight decay 후보 표가 맞지 않다")
    elif task in ("signal", "video", "zone"):
        t = check_pred(path, expected, dict(pred=n_emotion))
        check_array(t, "lambda_index", (n_emotion,), path, 0, n, integer=True)
    elif task == "h2020":
        t = check_pred(path, expected, dict(pred=n_emotion, pred_by_roi=(n_roi, n_emotion)))
        check_array(t, "val_r_by_roi", (n_roi, n_emotion), path)
        check_array(t, "lambda_index", (n_roi, n_emotion), path, 0, len(d5.H2020_LAMBDAS), integer=True)
        check_array(t, "n_roi_in_ensemble", (n_emotion,), path, 0, n_roi + 1, integer=True)  # 0은 기준을 넘는 ROI가 없어 안쪽 r이 가장 높은 ROI를 쓴 경우다
    else:
        raise ValueError(task)
    return t


def check_runs(out, names, design_freeze=None, current=None):
    """결과끼리 코드와 동결 커밋이 같고, 같은 역할의 입력 내용이 같고, 같은 과제는 설정이 같다. 경로는 비교하지 않는다.
    current는 역할 -> 지금 파일의 해시 함수다. 주면 지금 파일과도 맞춘다. 경로가 같아도 내용이 바뀌었으면 멈춘다."""
    seen, code, freeze, settings = {}, None, set(), {}
    for n in names:
        d = json.loads((Path(out) / n / "done.json").read_text())
        code = d["code_sha256"] if code is None else code
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


def role_paths():
    """역할 이름 -> 지금 설정의 파일. 실행 코드의 역할 이름과 같다."""
    out = {f"s2:{p.name}": p for p in d5.S2_TABLES}
    out.update(vjepa2_blocks=c.FEATURES / "vjepa2/blocks.npy", deberta_video_mean=c.FEATURES / "deberta/video_mean.npy", labels=c.LABELS, stimuli=d5.STIMULI, lowlevel=c.FEATURES / f"{c.LOWLEVEL}.npy")
    for s in d5.HK:
        out.update({f"response:sub-{s}": d5.response_path(s), f"raw_response:sub-{s}": d5.response_path(s, normalized=False), f"roi:sub-{s}": d5.roi_path(s)})
    return out


def identification(pred, true):
    """O19. A의 예측과 A의 실제의 r이 A의 예측과 B의 실제의 r보다 크면 1이다. 같은 fold의 모든 B를 평균하고 모든 A를 평균한다."""
    a = pred - pred.mean(1, keepdims=True)
    b = true - true.mean(1, keepdims=True)
    na, nb = np.linalg.norm(a, axis=1, keepdims=True), np.linalg.norm(b, axis=1, keepdims=True)
    if not ((na > 0).all() and (nb > 0).all()):  # 문서에 처리 규칙이 없다. 0점이나 우연 수준으로 바꾸지 않고 멈춘다
        raise ValueError("차원에 걸쳐 상수인 벡터가 있어 영상 식별의 상관을 계산할 수 없다")
    a, b = a / na, b / nb
    s = a @ b.T
    d = np.diag(s)
    n = len(s)
    if n < 2:
        raise ValueError("식별에는 영상이 둘 이상 있어야 한다")
    wins = (d[:, None] > s).sum(1)  # 자기 자신은 같아서 세지 않는다
    return float((wins / (n - 1)).mean())


def layer_metrics(preds, targets, split, participant, participant_ids):
    """preds: fold -> 예측 파일 값. targets: 층 -> split 순서의 실제 특징. participant_ids: 그 참가자에게 block이 있는 영상.
    식별의 눈금은 decoder와 같이 그 참가자의 D_k 영상으로 맞춘다(N3, O19)."""
    has = np.isin(split.video_id.to_numpy(), list(participant_ids))
    pos = {v: i for i, v in enumerate(split.video_id.tolist())}
    rows = []
    for layer, y in targets.items():
        name = layer_name(layer)
        all_pred, all_true, ids = [], [], []
        for k, t in preds.items():
            r = c.roles(k)
            dk = np.isin(split.fold.to_numpy(), r["dk"]) & has
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
    paths = role_paths()
    start = {role: c.sha256(p) for role, p in paths.items()}  # 읽기 전에 낸다
    targets = load_targets(split)
    names, metric, chosen = [], [], []
    keys = {layer_name(l): len(targets[l][0]) for l in targets}
    target_keys = {layer_name(l): keys[layer_name(l)] for l in d5.TARGET_LAYERS}
    fold_of = dict(zip(split.video_id.tolist(), split.fold.tolist()))
    for s in d5.HK:
        exp = expected_tests(split, table, s)
        preds = {}
        for k in range(1, c.N_FOLDS + 1):
            d = d5.OUT / "decoding" / f"sub-{s}_fold{k}"
            names.append(f"decoding/sub-{s}_fold{k}")
            preds[k] = check_pred(d / "test_pred.npz", exp[k], keys)
            check_inner_oof(d / "inner_oof_target.npz", sum((exp[f] for f in c.roles(k)["dk"]), []), fold_of, target_keys)
            t = check_chosen(d / "chosen.tsv", d5.LAYERS, len(d5.LAMBDAS))
            t.insert(0, "fold", k), t.insert(0, "participant", s)
            chosen.append(t)
            for task in ("ridge", "soft_bce", "signal", "h2020"):
                names.append(f"{task}/sub-{s}_fold{k}")
                check_baseline(d5.OUT, task, f"sub-{s}_fold{k}", exp[k])
            for b in sorted(blocks.block.unique().tolist()):
                want = sorted(set(exp[k]) & set(blocks.video_id[blocks.block == b]))
                for kind in ("excluded", "control"):
                    n = f"sub-{s}_block{b}_fold{k}_{kind}"
                    names.append(f"zone/{n}")
                    check_baseline(d5.OUT, "zone", n, want)
        metric.append(layer_metrics(preds, targets, split, f"sub-{s}", sum(exp.values(), [])))
    for name in ("length", "lowlevel"):
        for k in range(1, c.N_FOLDS + 1):
            names.append(f"video/{name}_fold{k}")
            check_baseline(d5.OUT, "video", f"{name}_fold{k}", split.video_id[split.fold == k].tolist())
    check_runs(d5.OUT, names, a.design_freeze, current=lambda role: start[role])
    table_lambda, table_metric = pd.concat(chosen), pd.concat(metric)
    if {role: c.sha256(p) for role, p in paths.items()} != start:  # 수집 중에 바뀌었으면 저장하지 않는다
        raise SystemExit("수집 중 입력이 바뀌었다")
    MANIFEST.mkdir(parents=True, exist_ok=True)
    table_lambda.to_csv(MANIFEST / "decoding_lambda.tsv", sep="\t", index=False, float_format="%.6g")
    table_metric.to_csv(MANIFEST / "decoding_layer_metrics.tsv", sep="\t", index=False, float_format="%.6g")
    print("층별 표를 저장했다", MANIFEST, flush=True)


if __name__ == "__main__":
    main()
