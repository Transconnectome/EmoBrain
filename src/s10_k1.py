#!/usr/bin/env python3
"""S10 경로 평가(K1)와 14개 차원 표(B4, K1a) (04 S10, 01 K1, K1a, B4, N6, N8, N11, G14, I9, 2-3, 2-6, 6-1, O4, O20, O35, 2026-11-15). GPU 없음.

입력
- S9 경로 평가 예측(s9_path_eval.py의 출력 폴더): done.json에 적힌 출력 sha256과 파일이 같아야 읽는다. --partial-check로 낸 S9 결과는 이 단계도 --partial-check일 때만 읽는다.
- S6 결과 폴더: A-1 Brain → Emotion(brain_only)의 selected.json seed마다 6 fold 시험 예측(test_pred.npz의 p). s10_performance와 같은 함수로 읽는다.
  S9가 C-1 decoded features를 읽을 때 쓴 plan/rows.npz와 sha256이 같아야 한다(같은 분할의 행).
- S5 ridge 폴더(<output_root>/s5_ridge/ridge): 참가자, fold마다 pred.npz의 dimension_main(B4 주 비교판, N15). 사람 평정 1~9점 값 그대로의 ridge다.
- S4 결과 폴더: k1a/fold<k>/test_pred.npz의 additive_score, interaction_score(실제 Vision feature와 Caption feature를 넣은 K1a Stimulus Model). S9가 읽은 파일과 sha256이 같아야 한다.
- 사람 평정: 정서 34개(비율)와 14개 차원(1~9점 평균)을 s4_common.load_scores로 읽는다.
행 대조(N11): 모든 판이 참가자마다 같은 영상 행이어야 한다. 다르면 멈춘다.
계산(s10_stats, s10_performance와 같은 규칙)
- 참가자마다 6 fold를 모은 시험 영상에서 정서(차원)마다 Pearson r을 한 번 낸다(2-3). 계산할 수 없는 r은 빼고 그 수와 이유를 적는다(2-6).
- bootstrap 10,000회(I5): 영상 단위, 같은 내용 영상 묶음(canonical_id)은 함께, s10_performance와 같은 난수 seed. 모든 판과 5명에 같은 뽑힌 횟수를 쓴다(6-1).
- 구간은 basic 95%, 차이의 p는 중심을 맞춘 양측 bootstrap 검정(O4 (3)). 5명 평균은 참가자 값의 평균이다.
- 차이를 내는 두 판에서 계산할 수 있는 정서(차원)가 다르면 멈춘다(s10_performance와 같다).
K1(정서 34개, 보조)
- 판: A-1(seed마다), 경로 평가 ridge판과 C-1판(C-1판은 seed마다). 각각 더하기 head와 상호작용 head, 보정 전과 보정판(N8).
- 절대 성능: 정서별 r과 구간(k1_per_emotion.tsv), 참가자 점수(계산할 수 있는 정서의 r 평균)와 구간(k1_scores.tsv).
- 차이(경로 평가 − A-1): C-1판은 같은 seed의 A-1과, ridge판은 A-1의 seed마다 짝짓는다. 참가자 점수 차이(k1_differences.tsv)와
  정서별 차이(k1_differences_per_emotion.tsv, 탐색, BH-FDR은 참가자마다, 비교마다 34개 정서, I9). 비율은 내지 않는다(K1, N6). [사전] 15개의 Holm에 넣지 않는다.
14개 차원(B4, K1a, 보조). 표 하나(dimensions14.tsv)에 세 성능을 나란히 둔다
- (1) B4 ridge의 뇌 직접 decoding(주 비교판), (2) 실제 특징을 넣은 Stimulus Model(더하기, 상호작용. 참고값이고 상한이 아니다),
  (3) decoded features를 넣은 Stimulus Model(ridge판, C-1판 × 더하기, 상호작용 × 보정 전, 보정판. C-1판은 seed마다).
- 차원마다 참가자별 r과 구간, 5명 평균. (3)의 행에는 (1)과의 차이, 구간, p, BH-FDR(탐색, 참가자마다, 비교마다 14개 차원)을 함께 적는다. [사전] 15개의 Holm에 넣지 않는다.
- 차원별 평정 신뢰도 칸(rating_reliability)은 [미확인]이다(K1a, 04 기록 칸 S0). 분석에 넣거나 빼는 조건으로 쓰지 않는다.
seed(G14): A-1과 C-1판은 seed마다 내고 평균과 표준편차를 따로 낸다(k1_seed_summary.tsv, dimensions14_seed_summary.tsv). 예측을 seed끼리 평균하지 않는다.
그 밖의 표: n8_shift_only.tsv(N8에서 평균만 옮긴 차원 수, O35. S9의 n8_counts.tsv), coverage.tsv, missing.tsv(빠진 것이 있을 때), run_info.json
사용: s10_k1.py --path-eval-dir <S9 경로 평가 폴더> --s6-dir <S6 결과 폴더> --s5-ridge-dir <S5 ridge 폴더> --s4-dir <S4 결과 폴더> --out <출력 폴더> --design-freeze <커밋>
      [--n-boot 10000] [--partial-check] [--overwrite]
"""
import argparse
import json
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd

import s4_common as c
import s10_inputs as I
import s10_performance as perf
import s10_stats as st

N_FOLDS = 6
EXPECTED_SEEDS = (0, 1, 2)  # G14
HEADS = ("additive", "interaction")  # O17
CALIBRATIONS = ("uncorrected", "corrected")  # N8
RELIABILITY = "[미확인]"  # K1a. 개별 평정이 없어 계산할 수 없고(2-6) 원문에서 값을 찾지 못했다
EXPLORATORY = "탐색(BH-FDR)"
PERF_LABEL = {"B4": "(1) B4 ridge 뇌 직접 decoding", "Stimulus": "(2) Stimulus Model, 실제 특징(참고값, 상한 아님)", "ridge": "(3) Stimulus Model, ridge decoded features", "C-1": "(3) Stimulus Model, C-1 decoded features"}
UNIT = re.compile(r"^(ridge|c1_seed(\d+))_fold(\d+)$")


def key_name(key):
    src, head, cal, seed = key
    return src if head is None else f"{src} {head}" + ("" if cal is None else f" {cal}")


# 읽기

def load_s9(s9_dir, partial_check):
    """S9 결과. done.json의 출력 sha256과 파일이 같아야 한다. 돌려주는 값: (기록, 단위 이름 -> 배열 dict)."""
    d = Path(s9_dir)
    if not (d / "done.json").exists():
        raise SystemExit(f"{d}/done.json이 없다. S9 경로 평가가 끝나지 않았다")
    info = json.loads((d / "done.json").read_text())
    if info.get("stage") != "S9 path evaluation (K1, K1a)":
        raise SystemExit(f"{d}: S9 경로 평가 결과가 아니다")
    if info.get("partial_check") and not partial_check:
        raise SystemExit(f"{d}: S9 결과가 점검용(--partial-check)이라 최종 표에 쓰지 않는다")
    units = {}
    for rel, h in info["outputs"].items():
        if c.sha256(d / rel) != h:
            raise SystemExit(f"{d / rel}: done.json에 적힌 sha256과 다르다")
        units[Path(rel).stem] = dict(np.load(d / rel))
    return info, units


def s9_hash(info, suffix):
    """S9가 읽은 입력 가운데 경로가 suffix로 끝나는 파일의 sha256(없으면 None)."""
    hits = {h for p, h in info["inputs"].items() if Path(p).as_posix().endswith(suffix)}
    if len(hits) > 1:
        raise SystemExit(f"S9 기록에 {suffix}가 내용이 다른 둘 이상의 파일로 있다")
    return next(iter(hits)) if hits else None


def by_participant(pid, vid, arr):
    out = {}
    for q in np.unique(pid):
        m = pid == q
        o = np.argsort(vid[m])
        out[str(q)] = (vid[m][o], np.asarray(arr, np.float64)[m][o])
    return out


def stack_folds(parts):
    """fold -> 참가자 -> (영상, 값)을 참가자 -> (영상, 값)으로. 6 fold가 모두 있어야 한다."""
    out = {}
    for k in sorted(parts):
        for q, (v, x) in parts[k].items():
            out.setdefault(q, []).append((v, x))
    res = {}
    for q, items in out.items():
        v = np.concatenate([a for a, _ in items])
        x = np.concatenate([b for _, b in items])
        if len(set(v.tolist())) != len(v):
            raise ValueError(f"{q}: 한 영상이 두 fold에 있다")
        o = np.argsort(v)
        res[q] = (v[o], x[o])
    return res


def s9_versions(units, prefix, n_out, split):
    """S9 단위에서 판마다 참가자 -> (영상, 값). prefix는 k1(p) 또는 k1a(score). 돌려주는 값: 판 키 -> 참가자 -> (영상, 값), 빠진 목록."""
    fold_of = dict(zip(split.video_id.astype(int), split.fold.astype(int)))
    parts, missing = {}, []
    for name, z in units.items():
        m = UNIT.match(name)
        if not m:
            raise SystemExit(f"S9 단위 이름 {name}을 알 수 없다")
        src, seed, k = ("ridge", None, int(m.group(3))) if m.group(1) == "ridge" else ("C-1", int(m.group(2)), int(m.group(3)))
        pid, vid = z["participant"].astype(str), z["video_id"].astype(np.int64)
        if any(fold_of.get(int(v)) != k for v in vid):
            raise ValueError(f"S9 {name}: fold {k}의 시험 영상이 아닌 행이 있다")
        for h in HEADS:
            for cal in CALIBRATIONS:
                col = f"{prefix}_{h}_{cal}_{'p' if prefix == 'k1' else 'score'}"
                x = np.asarray(z[col], np.float64)
                if x.shape != (len(vid), n_out) or not np.isfinite(x).all():
                    raise ValueError(f"S9 {name}: {col}의 크기 {x.shape}가 다르거나 NaN이 있다")
                parts.setdefault((src, h, cal, seed), {})[k] = by_participant(pid, vid, x)
    want = [("ridge", None)] + [("C-1", s) for s in EXPECTED_SEEDS]
    for src, seed in want:
        for k in range(1, N_FOLDS + 1):
            if (src, HEADS[0], CALIBRATIONS[0], seed) not in parts or k not in parts[src, HEADS[0], CALIBRATIONS[0], seed]:
                missing.append(dict(source=f"S9 {src}", seed="" if seed is None else seed, fold=k, participant="", path="units/" + ("ridge" if seed is None else f"c1_seed{seed}") + f"_fold{k}.npz"))
    out = {key: stack_folds(p) for key, p in parts.items() if len(p) == N_FOLDS}
    return out, missing


def load_a1(s6_dir, split, info9, n_emotions):
    """A-1 seed마다 6 fold 시험 예측. 돌려주는 값: seed -> 참가자 -> (영상, p), coverage 행, 빠진 목록."""
    found = perf.find_predictions(s6_dir)
    f = found[found.condition == "brain_only"] if len(found) else found
    cov, missing, out = [], [], {}
    plan_rows = {}
    for k in range(1, N_FOLDS + 1):
        p = Path(s6_dir) / f"outer_fold{k}" / "plan" / "rows.npz"
        if p.exists():
            h = s9_hash(info9, f"outer_fold{k}/plan/rows.npz")
            if h is not None and c.sha256(p) != h:
                raise SystemExit(f"{p}: S9가 C-1 decoded features를 읽을 때 쓴 plan/rows.npz와 다르다. 같은 S6 결과 폴더를 준다")
            plan_rows[k] = perf.plan_test_rows(s6_dir, k)
    for s in EXPECTED_SEEDS:
        paths = {}
        for k in range(1, N_FOLDS + 1):
            hit = f[(f.fold == k) & (f.seed == s)] if len(f) else f
            ok = len(hit) and hit.iloc[0].status == "ok" and k in plan_rows
            cov.append(dict(source="A-1", seed=s, fold=k, participant="", status="ok" if ok else "없음", path=hit.iloc[0].path if len(hit) else str(Path(s6_dir) / f"outer_fold{k}" / "brain_only")))
            if ok:
                paths[k] = hit.iloc[0].path
            else:
                missing.append(dict(source="A-1", seed=s, fold=k, participant="", path=cov[-1]["path"]))
        if len(paths) == N_FOLDS:
            out[s] = perf.load_condition(paths, split, plan_rows, n_emotions)
    extra = sorted(set(int(x) for x in f.seed.dropna()) - set(EXPECTED_SEEDS)) if len(f) else []
    if extra:
        raise ValueError(f"A-1 seed {extra}는 G14의 seed(0, 1, 2)가 아니다")
    return out, cov, missing


def load_b4(ridge_dir, split, pvideos, pids):
    """B4 주 비교판(S5 ridge pred.npz의 dimension_main). 돌려주는 값: 참가자 -> (영상, (영상, 14)), coverage 행, 빠진 목록."""
    fold_of = dict(zip(split.video_id.astype(int), split.fold.astype(int)))
    parts, cov, missing = {}, [], []
    for q in pids:
        for k in range(1, N_FOLDS + 1):
            d = Path(ridge_dir) / f"{q}_fold{k}"
            ok = (d / "pred.npz").exists() and (d / "done.json").exists()
            cov.append(dict(source="B4 ridge", seed="", fold=k, participant=q, status="ok" if ok else "없음", path=str(d / "pred.npz")))
            if not ok:
                missing.append(dict(source="B4 ridge", seed="", fold=k, participant=q, path=str(d / "pred.npz")))
                continue
            z = np.load(d / "pred.npz")
            v = z["video_id"].astype(np.int64)
            want = sorted(int(t) for t in pvideos[q] if fold_of[int(t)] == k)
            if sorted(v.tolist()) != want or len(set(v.tolist())) != len(v):
                raise ValueError(f"{d}/pred.npz: 시험 영상이 그 참가자의 fold {k} block 영상과 다르다")
            x = np.asarray(z["dimension_main"], np.float64)
            if x.shape != (len(v), len(c.DIMENSIONS)) or not np.isfinite(x).all():
                raise ValueError(f"{d}/pred.npz: dimension_main의 크기 {x.shape}가 다르거나 NaN이 있다")
            o = np.argsort(v)
            parts.setdefault(k, {})[q] = (v[o], x[o])
    full = {k: p for k, p in parts.items() if len(p) == len(pids)}
    return (stack_folds(full) if len(full) == N_FOLDS else {}), cov, missing


def load_stimulus_k1a(s4_dir, split, info9, pvideos, pids):
    """실제 특징을 넣은 K1a Stimulus Model(S4 k1a test_pred.npz). 돌려주는 값: head -> 참가자 -> (영상, (영상, 14)), coverage 행, 빠진 목록."""
    parts, cov, missing = {}, [], []
    for k in range(1, N_FOLDS + 1):
        p = Path(s4_dir) / "k1a" / f"fold{k}" / "test_pred.npz"
        ok = p.exists() and (p.parent / "done.json").exists()
        cov.append(dict(source="Stimulus K1a", seed="", fold=k, participant="", status="ok" if ok else "없음", path=str(p)))
        if not ok:
            missing.append(dict(source="Stimulus K1a", seed="", fold=k, participant="", path=str(p)))
            continue
        h = s9_hash(info9, f"k1a/fold{k}/test_pred.npz")
        if h is None or c.sha256(p) != h:
            raise SystemExit(f"{p}: S9가 읽은 K1a 시험 예측과 다르다(다른 S4 결과 폴더). 같은 S4 결과를 준다")
        z = np.load(p)
        v = z["video_id"].astype(np.int64)
        fold_ids = np.sort(split.video_id[split.fold == k].astype(np.int64).to_numpy())
        if not np.array_equal(v, fold_ids):
            raise ValueError(f"{p}: 영상이 fold {k}의 개발 영상과 다르다")
        for hd in HEADS:
            x = np.asarray(z[f"{hd}_score"], np.float64)
            if x.shape != (len(v), len(c.DIMENSIONS)) or not np.isfinite(x).all():
                raise ValueError(f"{p}: {hd}_score의 크기 {x.shape}가 다르거나 NaN이 있다")
            for q in pids:
                at = np.isin(v, pvideos[q])
                parts.setdefault(hd, {}).setdefault(k, {})[q] = (v[at], x[at])
    out = {hd: stack_folds(p) for hd, p in parts.items() if len(p) == N_FOLDS}
    return out, cov, missing


def same_rows(versions):
    """N11. 모든 판이 참가자마다 같은 영상 행인지. 돌려주는 값: 참가자 -> 영상."""
    ref_key = next(iter(versions))
    ref = {q: v for q, (v, _) in versions[ref_key].items()}
    for key, by_q in versions.items():
        if set(by_q) != set(ref) or any(not np.array_equal(by_q[q][0], ref[q]) for q in ref):
            raise ValueError(f"{key_name(key)}의 행이 {key_name(ref_key)}와 다르다. 같은 참가자, 같은 영상 행에서만 비교한다(N11)")
    return ref


# 계산

def pooled(versions, videos, split, y_split, n_boot):
    """판마다, 참가자마다 정서(차원)별 r과 bootstrap r. 모든 판, 5명에 같은 뽑힌 횟수."""
    pids = sorted(videos)
    U = np.array(sorted(set().union(*[set(v.tolist()) for v in videos.values()])), np.int64)
    sp = split.set_index("video_id").loc[U]
    spos = {v: i for i, v in enumerate(split.video_id.astype(int).tolist())}
    yU = np.asarray(y_split, np.float64)[[spos[int(v)] for v in U]]
    pos = {q: np.searchsorted(U, videos[q]) for q in pids}
    codes, n_units = st.unit_codes(sp.canonical_id.to_numpy())
    W = st.bootstrap_counts(n_units, n_boot, np.random.default_rng(perf.BOOT_SEED))  # s10_performance와 같은 seed
    res = dict(pids=pids, r={}, boot={}, reason={}, keep={}, yq={}, n_units=n_units)
    for q in pids:
        yq = yU[pos[q]]
        res["yq"][q] = yq
        rb = st.boot_r(W[:, codes[pos[q]]], yq, {key: versions[key][q][1] for key in versions})
        for key in versions:
            p = versions[key][q][1]
            res["r"][key, q] = st.pearson_columns(yq, p)
            res["boot"][key, q] = rb[key]
            res["reason"][key, q] = st.noncomputable_reason(yq, p)
            res["keep"][key, q] = np.isfinite(res["r"][key, q])
    return res


def absolute_rows(res, key, names, label):
    """판 하나의 참가자별, 5명 평균 정서(차원)별 r과 구간."""
    rows = []
    pids = res["pids"]
    for q in pids:
        r, b = res["r"][key, q], res["boot"][key, q]
        lo, hi = st.basic_ci(r, b)
        yq = res["yq"][q]
        for e, n in enumerate(names):
            rows.append(dict(**label, participant=q, target=n, r=r[e], ci_low=lo[e], ci_high=hi[e], n_videos=len(yq), n_nonzero=int((yq[:, e] != 0).sum()),
                             rating_var=float(yq[:, e].var()), computable=bool(res["keep"][key, q][e]), reason=res["reason"][key, q][e] or "", n_participants=1))
    r5 = perf.nanmean0(np.stack([res["r"][key, q] for q in pids]))
    b5 = perf.nanmean0(np.stack([res["boot"][key, q] for q in pids]))
    lo, hi = st.basic_ci(r5, b5)
    n_part = np.stack([res["keep"][key, q] for q in pids]).sum(0)
    for e, n in enumerate(names):
        rows.append(dict(**label, participant="mean5", target=n, r=r5[e], ci_low=lo[e], ci_high=hi[e], n_videos=np.nan, n_nonzero=np.nan, rating_var=np.nan,
                         computable=bool(n_part[e] > 0), reason="" if n_part[e] == len(pids) else f"{len(pids) - n_part[e]}명 계산 불가", n_participants=int(n_part[e])))
    return rows


def check_keep(res, ka, kb, q, names):
    if not np.array_equal(res["keep"][ka, q], res["keep"][kb, q]):
        diff = [names[e] for e in np.flatnonzero(res["keep"][ka, q] != res["keep"][kb, q])]
        raise ValueError(f"{key_name(ka)} 대 {key_name(kb)} {q}: 계산할 수 있는 항목이 다르다({diff}). 어느 항목으로 평균할지 정해지지 않았다")


def target_differences(res, ka, kb, names):
    """항목(정서, 차원)마다 a − b의 차이, 구간, p, BH(참가자마다, 5명 평균도 따로, 이 비교의 항목 묶음). 돌려주는 값: 참가자 -> dict."""
    pids = res["pids"]
    out = {}
    for q in pids:
        check_keep(res, ka, kb, q, names)
    for q in pids + ["mean5"]:
        if q == "mean5":
            d = perf.nanmean0(np.stack([res["r"][ka, x] for x in pids])) - perf.nanmean0(np.stack([res["r"][kb, x] for x in pids]))
            db = perf.nanmean0(np.stack([res["boot"][ka, x] for x in pids])) - perf.nanmean0(np.stack([res["boot"][kb, x] for x in pids]))
        else:
            d, db = res["r"][ka, q] - res["r"][kb, q], res["boot"][ka, q] - res["boot"][kb, q]
        lo, hi = st.basic_ci(d, db)
        p = st.centered_p(d, db)
        out[q] = dict(estimate=d, ci_low=lo, ci_high=hi, p_raw=p, p_bh=st.bh(p), family_size=int(np.isfinite(p).sum()), n_boot_valid=np.isfinite(db).sum(0))
    return out


def score_of(res, key, q):
    """참가자 점수(계산할 수 있는 항목의 r 평균)와 bootstrap 값. q가 mean5면 5명 평균."""
    if q == "mean5":
        parts = [score_of(res, key, x) for x in res["pids"]]
        return float(np.mean([a for a, _ in parts])), np.mean(np.stack([b for _, b in parts]), 0)
    keep = res["keep"][key, q]
    return (float(res["r"][key, q][keep].mean()) if keep.any() else np.nan), st.mean_over(res["boot"][key, q], keep)


# K1

def k1_tables(path_versions, a1, videos, split, y, emotions, n_boot):
    versions = {**{("A-1", None, None, s): by for s, by in a1.items()}, **path_versions}
    res = pooled(versions, videos, split, y, n_boot)
    lab = lambda key: dict(source=key[0], head=key[1] or "", calibration=key[2] or "", seed=key[3] if key[3] is not None else np.nan, version=key_name(key))
    per = [row for key in versions for row in absolute_rows(res, key, emotions, lab(key))]
    scores = []
    for key in versions:
        for q in res["pids"] + ["mean5"]:
            th, b = score_of(res, key, q)
            lo, hi = st.basic_ci(th, b)
            n_used = int(res["keep"][key, q].sum()) if q != "mean5" else np.nan
            scores.append(dict(**lab(key), participant=q, score_r=th, ci_low=float(lo), ci_high=float(hi), n_emotions_used=n_used,
                               n_noncomputable=int(sum((~res["keep"][key, x]).sum() for x in ([q] if q != "mean5" else res["pids"])))))
    diffs, diff_emo = [], []
    for key in path_versions:
        partners = [s for s in a1 if key[3] is None or s == key[3]]  # C-1판은 같은 seed, ridge판은 A-1의 seed마다
        for s in partners:
            kb = ("A-1", None, None, s)
            base = dict(**lab(key), a1_seed=s, comparison=f"{key_name(key)} − A-1(seed {s})")
            per_t = target_differences(res, key, kb, emotions)
            for q in res["pids"] + ["mean5"]:
                ta, ba = score_of(res, key, q)
                tb, bb = score_of(res, kb, q)
                d, db = ta - tb, ba - bb
                lo, hi = st.basic_ci(d, db)
                diffs.append(dict(base, participant=q, score_path=ta, score_a1=tb, estimate=d, ci_low=float(lo), ci_high=float(hi), p_raw=float(st.centered_p(d, db)),
                                  n_boot_valid=int(np.isfinite(db).sum()), statistic="34개 정서 평균 r의 차이(경로 평가 − A-1)", label="보조(방향 없음, Holm 15개 밖)"))
                t = per_t[q]
                for e, n in enumerate(emotions):
                    diff_emo.append(dict(base, participant=q, emotion=n, estimate=t["estimate"][e], ci_low=t["ci_low"][e], ci_high=t["ci_high"][e], p_raw=t["p_raw"][e], p_bh=t["p_bh"][e],
                                         family_size=t["family_size"], label=EXPLORATORY))
    per = pd.DataFrame(per).rename(columns={"target": "emotion"})
    scores, diffs, diff_emo = pd.DataFrame(scores), pd.DataFrame(diffs), pd.DataFrame(diff_emo)
    seed_rows = []
    sc = scores[scores.source.isin(["A-1", "C-1"])]
    if len(sc):
        s1 = st.seed_summary(sc, ["source", "head", "calibration", "version", "participant"], ["score_r"])
        s1.insert(0, "what", "점수")
        seed_rows.append(s1)
    if len(diffs):
        d2 = diffs.copy()
        d2["seed"] = d2.a1_seed  # C-1판은 같은 seed끼리 짝이고, ridge판의 seed 변동은 짝지은 A-1의 seed다
        s2 = st.seed_summary(d2, ["source", "head", "calibration", "version", "participant"], ["estimate"])
        s2.insert(0, "what", "차이(경로 평가 − A-1)")
        seed_rows.append(s2)
    seed = pd.concat(seed_rows, ignore_index=True) if seed_rows else pd.DataFrame()
    return dict(k1_per_emotion=per, k1_scores=scores, k1_differences=diffs, k1_differences_per_emotion=diff_emo, k1_seed_summary=seed), res


# 14개 차원

def dimension_tables(b4, stim, path_versions, videos, split, y, n_boot):
    versions = {("B4", None, None, None): b4, **{("Stimulus", h, None, None): by for h, by in stim.items()}, **path_versions}
    res = pooled(versions, videos, split, y, n_boot)
    dims = list(c.DIMENSIONS)
    rows = []
    b4_key = ("B4", None, None, None)
    for key in versions:
        lab = dict(performance=PERF_LABEL[key[0]], source=key[0], head=key[1] or "", calibration=key[2] or "", seed=key[3] if key[3] is not None else np.nan, version=key_name(key))
        ab = absolute_rows(res, key, dims, lab)
        if key[0] in ("ridge", "C-1"):
            dd = target_differences(res, key, b4_key, dims)
            for row in ab:
                t, e = dd[row["participant"]], dims.index(row["target"])
                row.update(diff_vs_b4=t["estimate"][e], diff_ci_low=t["ci_low"][e], diff_ci_high=t["ci_high"][e], p_raw=t["p_raw"][e], p_bh=t["p_bh"][e], bh_family_size=t["family_size"], label=EXPLORATORY)
        rows += ab
    t = pd.DataFrame(rows).rename(columns={"target": "dimension"})
    for col in ("diff_vs_b4", "diff_ci_low", "diff_ci_high", "p_raw", "p_bh", "bh_family_size", "label"):
        if col not in t.columns:
            t[col] = np.nan
    t["rating_reliability"] = RELIABILITY
    cs = t[t.source == "C-1"]
    seed = st.seed_summary(cs, ["performance", "source", "head", "calibration", "version", "participant", "dimension"], ["r", "diff_vs_b4"]) if len(cs) else pd.DataFrame()
    return dict(dimensions14=t, dimensions14_seed_summary=seed), res


# 실행

def run(s9_dir, s6_dir, ridge_dir, s4_dir, out, split, y_emotions, y_dimensions, emotions, *, n_boot=st.N_RESAMPLE, partial_check=False, overwrite=False, extra_info=None, pvideos=None):
    started = time.time()
    out = I.prepare_out(out, overwrite)
    if np.asarray(y_emotions).shape != (len(split), len(emotions)) or np.asarray(y_dimensions).shape != (len(split), len(c.DIMENSIONS)):
        raise ValueError("사람 평정의 크기가 split, 정서 수, 차원 수와 다르다")
    info9, units = load_s9(s9_dir, partial_check)
    pvideos = I.participant_videos(split) if pvideos is None else pvideos
    pids = [q for q in I.HK_PIDS if q in pvideos]
    k1_paths, miss_9 = s9_versions(units, "k1", len(emotions), split)
    k1a_paths, _ = s9_versions(units, "k1a", len(c.DIMENSIONS), split)
    a1, cov_a1, miss_a1 = load_a1(s6_dir, split, info9, len(emotions))
    b4, cov_b4, miss_b4 = load_b4(ridge_dir, split, pvideos, pids)
    stim, cov_st, miss_st = load_stimulus_k1a(s4_dir, split, info9, pvideos, pids)
    missing = miss_9 + miss_a1 + miss_b4 + miss_st
    I.require_complete(missing, partial_check, "K1, 14개 차원")
    tables = {}
    if a1 and k1_paths:
        videos = same_rows({**{("A-1", None, None, s): by for s, by in a1.items()}, **k1_paths})
        t, _ = k1_tables(k1_paths, a1, videos, split, y_emotions, emotions, n_boot)
        tables.update(t)
    if b4 and stim and k1a_paths:
        videos = same_rows({("B4", None, None, None): b4, **{("Stimulus", h, None, None): by for h, by in stim.items()}, **k1a_paths})
        t, _ = dimension_tables(b4, stim, k1a_paths, videos, split, y_dimensions, n_boot)
        tables.update(t)
    if not tables:
        raise SystemExit("6 fold가 모두 있는 판이 없어 표를 낼 수 없다")
    n8 = Path(s9_dir) / "n8_counts.tsv"
    if n8.exists():
        tables["n8_shift_only"] = pd.read_csv(n8, sep="\t")
    tables["coverage"] = pd.DataFrame(cov_a1 + cov_b4 + cov_st)
    if missing:
        tables["missing"] = pd.DataFrame(missing)
    info = dict(stage="S10 K1, 14개 차원(B4, K1a)", s9_dir=str(s9_dir), s9_code_commit=info9.get("code_commit"), s9_partial_check=bool(info9.get("partial_check")), s6_dir=str(s6_dir),
                ridge_dir=str(ridge_dir), s4_dir=str(s4_dir), participants=pids, a1_seeds=sorted(a1), c1_seeds=sorted({k[3] for k in k1_paths if k[0] == "C-1"}),
                k1_versions=[key_name(k) for k in k1_paths], dimension_versions=[key_name(k) for k in k1a_paths], tables=sorted(tables),
                settings=dict(n_boot=n_boot, boot_seed=perf.BOOT_SEED, bootstrap_unit="video", ci_level=st.CI_LEVEL, expected_seeds=EXPECTED_SEEDS),
                partial_check=bool(missing), **(extra_info or {}))
    if missing:
        info["note"] = I.PARTIAL_NOTE
    if n_boot != st.N_RESAMPLE:
        info["note_resample"] = f"재표집 횟수가 I5의 {st.N_RESAMPLE}회와 다르다. 점검용 실행이다"
    return I.write_out(out, tables, info, started)


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 경로 평가(K1)와 14개 차원 표(B4, K1a)")
    ap.add_argument("--path-eval-dir", required=True, help="S9 경로 평가 결과 폴더(s9_path_eval.py의 --out)")
    ap.add_argument("--s6-dir", required=True, help="S6 결과 폴더(A-1 시험 예측. S9에 준 것과 같은 폴더)")
    ap.add_argument("--s5-ridge-dir", required=True, help="S5 ridge 폴더(<output_root>/s5_ridge/ridge, B4)")
    ap.add_argument("--s4-dir", required=True, help="S4 결과 폴더(S9에 준 것과 같은 폴더)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", required=True)
    ap.add_argument("--n-boot", type=int, default=st.N_RESAMPLE)
    ap.add_argument("--partial-check", action="store_true", help="빠진 입력이 있어도 6 fold가 모두 있는 판으로 읽기, 행 대조, 계산만 점검한다. 결과로 쓰지 않는다")
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args(argv)
    c.guard(a.design_freeze)
    split = c.load_split()
    y_em, cols = c.load_scores(split, "emotions")
    y_dim, _ = c.load_scores(split, "dimensions")
    inputs = {"split_hk_dev.tsv": c.sha256(c.SPLITS / "split_hk_dev.tsv"), "labels": c.sha256(c.LABELS), "label_map_34.tsv": c.sha256(c.LABEL_MAP)}
    info = run(a.path_eval_dir, a.s6_dir, a.s5_ridge_dir, a.s4_dir, a.out, split, y_em, y_dim, I.emotion_names(cols), n_boot=a.n_boot, partial_check=a.partial_check,
               overwrite=a.overwrite, extra_info=dict(design_freeze=a.design_freeze, inputs=inputs))
    print(f"끝: {a.out} ({info['elapsed_seconds']}초)")


if __name__ == "__main__":
    main()
