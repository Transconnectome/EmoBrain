#!/usr/bin/env python3
"""S10 주 지표, 보조 지표, 조건 비교, 전제 검정 (04 S10, 01 2-3, 2-4, 2-6, 6-0, 6-1, B7, G10, G14, I5, N11, N12, N19, O4, O25, 2026-11-15). GPU 없음.

입력: S6 결과 폴더(s6_merge_lr.py로 합친 폴더 포함)
- outer_fold<k>/<조건>/selected.json의 seeds(seed -> outer_fold<k> 기준 상대 경로)를 따라 시험 예측(test_pred.npz의 p)을 읽는다.
  짝 학습 조건(D-4, D-3 짝)은 <상대 경로>/ensemble/test_pred.npz(네 짝 평균, s6_train._ensemble)다.
- 0 후보가 골린 fold(zero_selected, G10)는 상대 경로가 앞 조건의 폴더를 가리킨다. 그대로 따르고 coverage.tsv에 적는다.
- 6 fold 가운데 빠진 fold가 있는 조건과 seed는 계산하지 않고 coverage.tsv에 적는다. 그 조건이 든 비교는 comparisons.tsv에 빠졌다고 적는다.
- 행 대조(N11): fold마다 예측 행(참가자, 영상)이 S6 plan/rows.npz의 시험 행과 같아야 하고, 모든 조건과 seed가 같은 행이어야 한다. 다르면 멈춘다.
- 사람 평정은 S4~S6과 같은 s4_common.load_scores로 읽는다. 뇌 모델이 아닌 encoder 2(정서 출력 없음)와 Multimodal Model(시험 입력에 feature, G16 참고 성능)은 이 표에 넣지 않는다.
계산(s10_stats)
- 참가자마다 정서별 r 하나(6 fold를 모음, 2-3), R²(6-0), MAE와 평정 0, 0 초과로 나눈 MAE(N19), 평균 예측 대비 오차 감소(O25). 0이 아닌 영상 수, 평정 분산, bootstrap 구간(2-6).
- 참가자 점수는 계산할 수 있는 정서의 r 평균, 5명 평균은 참가자 점수의 평균. 계산할 수 없는 r의 수를 센다(N12).
- bootstrap 10,000회(I5): 영상 단위이고 같은 내용 영상 묶음(split의 canonical_id)은 함께 뽑는다. 모든 조건, seed, 5명에 같은 재표집을 쓴다(6-1).
- [사전] 2-3 여섯 비교(6-1 표)와 보조 비교: 차이, basic 95% 구간, 중심을 맞춘 양측 p(O4 (3)). 정서별 차이는 탐색이고 BH-FDR(참가자마다, 비교마다 34개, I9).
  비교하는 두 조건에서 계산할 수 있는 정서가 다르면 멈춘다(어느 정서로 평균할지 2-3이 정하지 않았다).
- 0행 전제 검정(O4 (4)): A-1과 C-1 각각 34개 정서 평균 r을 순열 기준과 비교한다. 순열 10,000회, 같은 시험 fold와 같은 원래 run 안에서만 섞는다(O4 (1)). Holm 2개 묶음(5명 평균, 참가자마다).
- seed마다 점수를 내고 평균과 표준편차를 낸다(G14). 예측을 seed끼리 평균하지 않는다.
출력(레포 밖 --out)
- all/: 참가자가 가진 영상 전체. common5/: 5명 공통 영상만(B7). 두 폴더에 같은 표를 쓴다.
  per_emotion.tsv, participant_scores.tsv, seed_summary.tsv, comparisons.tsv, comparisons_per_emotion.tsv, premise_tests.tsv, premise_per_emotion.tsv, noncomputable.tsv
- prereg_pvalues.tsv: [사전] 비교의 보정 전 p(all만). s10_holm15.py가 15개를 모아 Holm을 적용한다.
- coverage.tsv(조건, seed, fold마다 읽은 파일과 0 후보 여부), rows.tsv(참가자별 영상 수), run_info.json(입력 해시, 설정, 시간)
그림은 s10_figures.py가 그린다(scripts/s10_performance.sh가 이어서 부른다).
정하지 못한 것은 옵션으로 받고 기본값을 두지 않는다.
- --dk-mean: O25의 D_k 평균을 참가자의 D_k 영상(participant), 5명의 D_k 행(rows), D_k 영상(videos) 가운데 무엇으로 낼지
- --split-content-pairs: 같은 내용 영상 쌍이 다른 run에 있을 때 순열에서 각자 자기 run 안에서 섞을지(주지 않으면 멈춘다)
사용: s10_performance.py --s6-dir <S6 결과 폴더> --out <출력 폴더> --dk-mean participant|rows|videos --design-freeze <커밋> [--split-content-pairs] [--bootstrap-unit video|run] [--n-boot 10000] [--n-perm 10000] [--overwrite]
"""
import argparse
import json
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

import s4_common as c
import s6_common as S
import s10_stats as st

N_FOLDS = 6
# 6-1 표 2-3 행. (이름, 앞 조건, 뒤 조건, 예상 방향). 차이는 앞 − 뒤다
PREREG_23 = (
    ("2-3(가)", "brain_only_featdec", "brain_only", "앞이 높다"),
    ("2-3(나)", "brain_decoded", "brain_only_featdec", "없음"),
    ("2-3(다)", "brain_only_distill", "brain_only", "없음"),
    ("2-3(라)", "brain_only_distill", "control_label_smoothing", "없음"),
    ("2-3(마)", "brain_only_featdec", "brain_only_distill", "없음"),
    ("2-3(바)", "brain_decoded_distill", "brain_decoded", "없음"),
)
# 보조 비교(6-1 다중비교, G6, G16)와 1-2 (가). Holm 15개에 넣지 않고 방향을 예측하지 않는다
AUXILIARY = (
    ("G6 Stimulus 예측 올바른 대응 대 섞은 대응", "brain_only_distill", "control_stimulus_shuffle", "없음"),
    ("G6 feature 올바른 대응 대 섞은 대응", "brain_only_featdec", "control_feature_shuffle", "없음"),
    ("G16 E-고정 대 C-1", "brain_only_repr_frozen", "brain_decoded", "없음"),
    ("G16 E-고정 대 A-1", "brain_only_repr_frozen", "brain_only", "없음"),
    ("G16 E-학습 대 C-1", "brain_only_repr_trained", "brain_decoded", "없음"),
    ("G16 E-학습 대 A-1", "brain_only_repr_trained", "brain_only", "없음"),
    ("1-2(가) 상호작용 head 대 더하기 head", "brain_decoded", "brain_decoded_additive", "없음"),
)
PREMISE = ("brain_only", "brain_decoded")  # 6-1 0행, O4 (4)
NOT_BRAIN = {"feature_encoder": "정서를 내지 않는다(encoder 2)", "multimodal": "시험 입력에 Vision feature와 Caption feature가 들어간다(G16 참고 성능)"}
DK_MODES = ("participant", "rows", "videos")
BOOT_SEED, PERM_SEED = 20261115, 20261116  # 재표집 난수 seed. run_info.json에 남긴다
PERM_CHUNK = 200


def display(cond):
    return S.DISPLAY.get(cond, cond)


def nanmean0(a):
    """첫 축의 NaN을 빼고 평균. 모두 NaN이면 NaN이다."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return np.nanmean(a, 0)


def write_tsv(t, path):
    """seed 열은 정수로 쓴다(빈 칸은 비워 둔다)."""
    t = t.copy()
    if "seed" in t.columns:
        t["seed"] = pd.to_numeric(t["seed"]).astype("Int64")
    t.to_csv(path, sep="\t", index=False)


def fig_label(cond):
    """그림 글꼴에 한글이 없을 수 있어 묶음 이름이 ASCII가 아니면 코드 이름을 쓴다."""
    d = display(cond)
    return d if d.isascii() else cond


# 읽기

def pred_file(fold_dir, condition, rel):
    """selected.json의 상대 경로에서 시험 예측 파일. 짝 학습 조건은 네 짝 평균(ensemble)이다."""
    if condition not in S.CONDITIONS:
        raise SystemExit(f"알 수 없는 조건: {condition}")
    base = Path(fold_dir) / rel
    return base / "ensemble" / "test_pred.npz" if S.CONDITIONS[condition].paired else base / "test_pred.npz"


def find_predictions(s6_dir):
    """fold마다 조건 폴더의 선택. 행: condition, fold, seed, rel, zero_selected, path, status."""
    rows = []
    for k in range(1, N_FOLDS + 1):
        fo = Path(s6_dir) / f"outer_fold{k}"
        if not fo.is_dir():
            continue
        for d in sorted(fo.iterdir()):
            if d.name == "plan" or not d.is_dir():
                continue
            if d.name not in S.CONDITIONS:
                raise SystemExit(f"{d}: 알 수 없는 조건 폴더")
            sel_path = d / "selected.json"
            if not sel_path.exists():
                rows.append(dict(condition=d.name, fold=k, seed=np.nan, rel=None, zero_selected=None, path=None, status="selected.json 없음"))
                continue
            sel = json.loads(sel_path.read_text())
            for seed, rel in sorted(sel["seeds"].items(), key=lambda t: int(t[0])):
                path = pred_file(fo, d.name, rel)
                rows.append(dict(condition=d.name, fold=k, seed=int(seed), rel=rel, zero_selected=bool(sel.get("zero_selected", False)), path=str(path), status="ok" if path.exists() else "예측 파일 없음"))
    return pd.DataFrame(rows, columns=["condition", "fold", "seed", "rel", "zero_selected", "path", "status"])


def coverage_table(found):
    """조건, seed마다 6 fold가 모두 있는지. 돌려주는 값: (조건 × seed × fold 표, 계산할 (조건, seed) 목록)."""
    rows, usable = [], []
    for cond in sorted(found.condition.unique()):
        f = found[found.condition == cond]
        seeds = sorted(int(s) for s in f.seed.dropna().unique())
        if not seeds:
            rows.append(dict(condition=cond, display=display(cond), seed=np.nan, fold=np.nan, rel=None, zero_selected=None, status="selected.json 없음", used=False))
            continue
        for s in seeds:
            ok = True
            for k in range(1, N_FOLDS + 1):
                hit = f[(f.fold == k) & (f.seed == s)]
                if hit.empty:
                    ok = False
                    rows.append(dict(condition=cond, display=display(cond), seed=s, fold=k, rel=None, zero_selected=None, status="이 fold에 선택 없음", used=False))
                    continue
                h = hit.iloc[0]
                ok = ok and h.status == "ok"
                rows.append(dict(condition=cond, display=display(cond), seed=s, fold=k, rel=h.rel, zero_selected=h.zero_selected, status=h.status, used=False))
            excluded = NOT_BRAIN.get(cond)
            if ok and excluded is None:
                usable.append((cond, s))
            for row in rows:
                if row["condition"] == cond and row["seed"] == s:
                    row["used"] = ok and excluded is None
                    if excluded is not None:
                        row["status"] = f"제외: {excluded}"
                    elif not ok and row["status"] == "ok":
                        row["status"] = "ok(다른 fold가 빠져 계산하지 않음)"
    return pd.DataFrame(rows), usable


def plan_test_rows(s6_dir, k):
    """S6 plan/rows.npz의 시험 행(참가자, 영상)."""
    path = Path(s6_dir) / f"outer_fold{k}" / "plan" / "rows.npz"
    if not path.exists():
        raise SystemExit(f"{path}가 없다. 시험 행을 대조할 수 없다")
    z = np.load(path)
    t = z["role"] == 2
    return set(zip(z["participant"][t].astype(str).tolist(), z["video_id"][t].astype(np.int64).tolist()))


def load_condition(paths, split, plan_rows, n_emotions):
    """(조건, seed) 하나의 6 fold 시험 예측. paths: fold -> 파일. 돌려주는 값: 참가자 -> (영상 번호 오름차순, p)."""
    fold_of = dict(zip(split.video_id.astype(int).tolist(), split.fold.astype(int).tolist()))
    parts = {}
    for k, path in sorted(paths.items()):
        z = np.load(path)
        lack = {"participant", "video_id", "p"} - set(z.files)
        if lack:
            raise ValueError(f"{path}: {sorted(lack)}가 없다")
        pid, vid, p = z["participant"].astype(str), z["video_id"].astype(np.int64), np.asarray(z["p"], np.float64)
        if p.shape != (len(vid), n_emotions) or len(pid) != len(vid):
            raise ValueError(f"{path}: 예측 크기 {p.shape}가 (행 {len(vid)}, 정서 {n_emotions})와 다르다")
        if not np.isfinite(p).all() or (p < 0).any() or (p > 1).any():
            raise ValueError(f"{path}: 예측 확률에 NaN이 있거나 0~1을 벗어났다")
        keys = list(zip(pid.tolist(), vid.tolist()))
        if len(set(keys)) != len(keys):
            raise ValueError(f"{path}: 한 참가자의 같은 영상 행이 둘 이상이다")
        wrong = [v for v in vid.tolist() if fold_of.get(v) != k]
        if wrong:
            raise ValueError(f"{path}: fold {k}의 시험 영상이 아닌 행이 있다 {wrong[:5]}")
        want = plan_rows[k]
        if set(keys) != want:
            raise ValueError(f"{path}: 예측 행이 S6 plan의 시험 행과 다르다(빠진 행 {len(want - set(keys))}, 남는 행 {len(set(keys) - want)})")
        for q in np.unique(pid):
            m = pid == q
            parts.setdefault(q, []).append((vid[m], p[m]))
    out = {}
    for q, items in parts.items():
        v = np.concatenate([a for a, _ in items])
        x = np.concatenate([b for _, b in items])
        order = np.argsort(v)
        out[q] = (v[order], x[order])
    return out


def same_rows(loaded):
    """모든 조건과 seed가 같은 참가자, 같은 영상 행인지 본다(N11). 돌려주는 값: 참가자 -> 영상 번호."""
    ref_key = next(iter(loaded))
    ref = {q: v for q, (v, _) in loaded[ref_key].items()}
    for key, by_pid in loaded.items():
        if set(by_pid) != set(ref) or any(not np.array_equal(by_pid[q][0], ref[q]) for q in ref):
            raise ValueError(f"{key}의 행이 {ref_key}와 다르다. 같은 행에서만 비교한다(N11)")
    return ref


def dk_reference(mode, split, y_split, videos):
    """O25의 m. 참가자 -> {fold: (정서,)}. mode는 --dk-mean."""
    if mode not in DK_MODES:
        raise ValueError(f"--dk-mean은 {DK_MODES} 가운데 하나다")
    ids = split.video_id.to_numpy()
    fold = split.fold.to_numpy()
    folds = range(1, N_FOLDS + 1)
    if mode == "videos":
        shared = st.dk_means(fold, y_split, np.ones(len(ids)), folds)
    elif mode == "rows":
        shared = st.dk_means(fold, y_split, sum(np.isin(ids, v).astype(np.float64) for v in videos.values()), folds)
    return {q: (st.dk_means(fold, y_split, np.isin(ids, v).astype(np.float64), folds) if mode == "participant" else shared) for q, v in videos.items()}


# 계산

def analyze(name, data, videos, split, y_split, dkref, emotions, *, n_boot, n_perm, boot_unit, split_pairs):
    """data: (조건, seed) -> 참가자 -> 예측(videos[참가자] 순서). videos: 참가자 -> 영상 번호(오름차순). 돌려주는 값: 표 이름 -> DataFrame, 기록."""
    pids = sorted(videos)
    keys = sorted(data)
    n_emo = len(emotions)
    U = np.array(sorted(set().union(*[set(v.tolist()) for v in videos.values()])), np.int64)
    sp = split.set_index("video_id").loc[U]
    split_pos = {v: i for i, v in enumerate(split.video_id.tolist())}
    yU = np.asarray(y_split, np.float64)[[split_pos[v] for v in U]]
    pos = {q: np.searchsorted(U, videos[q]) for q in pids}
    fold_U = sp.fold.to_numpy()
    info = dict(n_videos_union=len(U))

    # 관찰 지표
    metrics, keep, score = {}, {}, {}
    for key in keys:
        for q in pids:
            m = np.stack([dkref[q][f] for f in fold_U[pos[q]]])
            metrics[key, q] = st.emotion_metrics(yU[pos[q]], data[key][q], m)
            keep[key, q] = np.isfinite(metrics[key, q]["r"])
            score[key, q] = float(metrics[key, q]["r"][keep[key, q]].mean()) if keep[key, q].any() else np.nan

    # bootstrap(6-1, O4 (3)). 모든 조건, seed, 5명에 같은 뽑힌 횟수
    labels = sp.canonical_id.to_numpy() if boot_unit == "video" else sp.run_index.to_numpy()
    codes, n_units = st.unit_codes(labels)
    info.update(bootstrap_unit=boot_unit, n_bootstrap_units=n_units)
    W = st.bootstrap_counts(n_units, n_boot, np.random.default_rng(BOOT_SEED))
    boot = {}
    for q in pids:
        rb = st.boot_r(W[:, codes[pos[q]]], yU[pos[q]], {key: data[key][q] for key in keys})
        for key in keys:
            boot[key, q] = rb[key]
    del W
    score_boot = {kq: st.mean_over(boot[kq], keep[kq]) for kq in boot}
    mean5 = {key: float(np.mean([score[key, q] for q in pids])) for key in keys}
    mean5_boot = {key: np.mean(np.stack([score_boot[key, q] for q in pids]), 0) for key in keys}
    r5 = {key: nanmean0(np.stack([metrics[key, q]["r"] for q in pids])) for key in keys}  # 정서별 5명 평균. 계산할 수 없는 참가자는 빼고 그 수를 적는다
    r5_boot = {key: nanmean0(np.stack([boot[key, q] for q in pids])) for key in keys}

    tables = {}
    # 정서별 표(2-3, 2-6)
    rows = []
    for (cond, seed) in keys:
        key = (cond, seed)
        for q in pids:
            mt = metrics[key, q]
            lo, hi = st.basic_ci(mt["r"], boot[key, q])
            n_nan = np.isnan(boot[key, q]).sum(0)
            for e in range(n_emo):
                rows.append(dict(analysis=name, condition=cond, display=display(cond), fig_label=fig_label(cond), seed=seed, participant=q, emotion=emotions[e],
                                 r=mt["r"][e], ci_low=lo[e], ci_high=hi[e], n_boot_nan=int(n_nan[e]), r2=mt["r2"][e], mae=mt["mae"][e], mae_zero=mt["mae_zero"][e],
                                 mae_nonzero=mt["mae_nonzero"][e], error_reduction=mt["error_reduction"][e], n_videos=int(mt["n_videos"][e]), n_nonzero=int(mt["n_nonzero"][e]),
                                 rating_var=mt["rating_var"][e], prediction_var=mt["prediction_var"][e], computable=bool(keep[key, q][e]), reason=mt["reason"][e] or "", n_participants=1))
        lo, hi = st.basic_ci(r5[key], r5_boot[key])
        n_part = np.stack([keep[key, q] for q in pids]).sum(0)
        avg = lambda col: nanmean0(np.stack([metrics[key, q][col] for q in pids]))
        r2m, maem, maez, maen, erm = avg("r2"), avg("mae"), avg("mae_zero"), avg("mae_nonzero"), avg("error_reduction")
        for e in range(n_emo):
            rows.append(dict(analysis=name, condition=cond, display=display(cond), fig_label=fig_label(cond), seed=seed, participant="mean5", emotion=emotions[e],
                             r=r5[key][e], ci_low=lo[e], ci_high=hi[e], n_boot_nan=int(np.isnan(r5_boot[key][:, e]).sum()), r2=r2m[e], mae=maem[e], mae_zero=maez[e],
                             mae_nonzero=maen[e], error_reduction=erm[e], n_videos=np.nan, n_nonzero=np.nan, rating_var=np.nan, prediction_var=np.nan,
                             computable=bool(n_part[e] > 0), reason="" if n_part[e] == len(pids) else f"{len(pids) - n_part[e]}명 계산 불가", n_participants=int(n_part[e])))
    tables["per_emotion"] = pd.DataFrame(rows)

    # 참가자 점수(2-3, N19, O25)
    rows = []
    for key in keys:
        cond, seed = key
        for q in pids + ["mean5"]:
            if q == "mean5":
                th, b = mean5[key], mean5_boot[key]
                parts = [metrics[key, x] for x in pids]
                extra = dict(n_emotions_used=np.nan, n_noncomputable=int(sum((~keep[key, x]).sum() for x in pids)), n_boot_nan_draws=int(np.isnan(b).sum()),
                             r2_mean=float(np.mean([np.nanmean(mt["r2"]) for mt in parts])), mae_sum=float(np.mean([mt["mae"].sum() for mt in parts])),
                             mae_zero_sum=float(np.mean([np.nansum(mt["mae_zero"]) for mt in parts])), mae_nonzero_sum=float(np.mean([np.nansum(mt["mae_nonzero"]) for mt in parts])),
                             error_reduction_mean=float(np.mean([np.nanmean(mt["error_reduction"]) for mt in parts])), n_videos=np.nan)
            else:
                th, b = score[key, q], score_boot[key, q]
                mt = metrics[key, q]
                extra = dict(n_emotions_used=int(keep[key, q].sum()), n_noncomputable=int((~keep[key, q]).sum()), n_boot_nan_draws=int(np.isnan(boot[key, q][:, keep[key, q]]).any(1).sum()),
                             r2_mean=float(np.nanmean(mt["r2"])), mae_sum=float(mt["mae"].sum()), mae_zero_sum=float(np.nansum(mt["mae_zero"])), mae_nonzero_sum=float(np.nansum(mt["mae_nonzero"])),
                             error_reduction_mean=float(np.nanmean(mt["error_reduction"])), n_videos=int(mt["n_videos"][0]))
            lo, hi = st.basic_ci(th, b)
            rows.append(dict(analysis=name, condition=cond, display=display(cond), fig_label=fig_label(cond), seed=seed, participant=q, score_r=th, ci_low=float(lo), ci_high=float(hi), **extra))
    tables["participant_scores"] = pd.DataFrame(rows)
    tables["seed_summary"] = st.seed_summary(tables["participant_scores"], ["analysis", "condition", "display", "participant"], ["score_r", "r2_mean", "mae_sum", "error_reduction_mean"])

    # 계산할 수 없는 r의 수(2-6, N12)
    rows = []
    for key in keys:
        for q in pids:
            reason = metrics[key, q]["reason"]
            rows.append(dict(analysis=name, condition=key[0], display=display(key[0]), seed=key[1], participant=q, n_computable=int(keep[key, q].sum()),
                             n_rating_constant=int((reason == "rating_constant").sum()), n_prediction_constant=int((reason == "prediction_constant").sum()),
                             n_both_constant=int((reason == "rating_and_prediction_constant").sum()),
                             emotions_noncomputable=",".join(emotions[e] for e in np.flatnonzero(~keep[key, q]))))
    tables["noncomputable"] = pd.DataFrame(rows)

    # 조건 비교(6-1, O4 (3))
    comp_rows, emo_rows = [], []
    for kind, plan in (("prereg", PREREG_23), ("auxiliary", AUXILIARY)):
        for test_id, a, b, direction in plan:
            base = dict(analysis=name, kind=kind, test_id=test_id, condition_a=a, condition_b=b, display_a=display(a), display_b=display(b), direction=direction)
            seeds_a = {s for cnd, s in keys if cnd == a}
            seeds_b = {s for cnd, s in keys if cnd == b}
            lack = [x for x, s in ((a, seeds_a), (b, seeds_b)) if not s]
            if lack:
                comp_rows.append(dict(base, seed=np.nan, participant="", status=f"계산하지 않음: {', '.join(display(x) for x in lack)}의 6 fold 예측이 없다"))
                continue
            for s in sorted(seeds_a ^ seeds_b):
                comp_rows.append(dict(base, seed=s, participant="", status="계산하지 않음: 이 seed가 한 조건에만 있다"))
            for s in sorted(seeds_a & seeds_b):
                ka, kb = (a, s), (b, s)
                for q in pids:
                    if not np.array_equal(keep[ka, q], keep[kb, q]):
                        diff = [emotions[e] for e in np.flatnonzero(keep[ka, q] != keep[kb, q])]
                        raise ValueError(f"{test_id} seed {s} {q}: 두 조건에서 계산할 수 있는 정서가 다르다({diff}). 어느 정서로 평균할지 정해지지 않았다")
                for q in pids + ["mean5"]:
                    if q == "mean5":
                        d, db, sa, sb = mean5[ka] - mean5[kb], mean5_boot[ka] - mean5_boot[kb], mean5[ka], mean5[kb]
                        de, deb = r5[ka] - r5[kb], r5_boot[ka] - r5_boot[kb]
                        n_e = np.nan
                    else:
                        d, db, sa, sb = score[ka, q] - score[kb, q], score_boot[ka, q] - score_boot[kb, q], score[ka, q], score[kb, q]
                        de, deb = metrics[ka, q]["r"] - metrics[kb, q]["r"], boot[ka, q] - boot[kb, q]
                        n_e = int(keep[ka, q].sum())
                    lo, hi = st.basic_ci(d, db)
                    comp_rows.append(dict(base, seed=s, participant=q, status="ok", score_a=sa, score_b=sb, estimate=d, ci_low=float(lo), ci_high=float(hi),
                                          p_raw=float(st.centered_p(d, db)), n_emotions=n_e, n_boot_valid=int(np.isfinite(db).sum())))
                    elo, ehi = st.basic_ci(de, deb)
                    ep = st.centered_p(de, deb)
                    ebh = st.bh(ep)  # I9. 탐색. 참가자마다(5명 평균도 따로), 비교마다 34개 정서
                    for e in range(n_emo):
                        emo_rows.append(dict(analysis=name, kind=kind, test_id=test_id, condition_a=a, condition_b=b, display_a=display(a), display_b=display(b), seed=s, participant=q,
                                             emotion=emotions[e], estimate=de[e], ci_low=elo[e], ci_high=ehi[e], p_raw=ep[e], p_bh=ebh[e], family_size=int(np.isfinite(ep).sum()), label="탐색(BH-FDR)"))
    tables["comparisons"] = pd.DataFrame(comp_rows)
    tables["comparisons_per_emotion"] = pd.DataFrame(emo_rows)

    # 0행 전제 검정(O4 (1), (4), (6))
    prem_keys = [k for k in keys if k[0] in PREMISE]
    prem_rows, prem_emo = [], []
    info["premise_conditions_found"] = sorted({k[0] for k in prem_keys})
    if prem_keys and n_perm > 0:
        blocks = np.array([f"fold{f}_run{r}" for f, r in zip(sp.fold.to_numpy(), sp.run_index.to_numpy())])
        split_groups = st.check_content_units(blocks, sp.canonical_id.to_numpy(), split_pairs)
        info.update(n_exchange_blocks=int(len(np.unique(blocks))), content_groups_split_across_runs=split_groups.to_dict("records"))
        perm = st.block_permutations(blocks, n_perm, np.random.default_rng(PERM_SEED))
        null = {(key, q): np.empty((n_perm, n_emo)) for key in prem_keys for q in pids}
        for start in range(0, n_perm, PERM_CHUNK):
            chunk = perm[start:start + PERM_CHUNK]
            for q in pids:
                res = st.permuted_r(chunk, pos[q], yU, {key: data[key][q] for key in prem_keys})
                for key in prem_keys:
                    null[key, q][start:start + len(chunk)] = res[key]
        del perm
        for key in prem_keys:
            nulls = {q: st.mean_over(null[key, q], keep[key, q]) for q in pids}
            nulls["mean5"] = np.mean(np.stack([nulls[q] for q in pids]), 0)
            obs = {q: score[key, q] for q in pids} | {"mean5": mean5[key]}
            for q in pids + ["mean5"]:
                prem_rows.append(dict(analysis=name, condition=key[0], display=display(key[0]), seed=key[1], participant=q, observed=obs[q], null_mean=float(np.nanmean(nulls[q])),
                                      null_q95=float(np.nanquantile(nulls[q], 0.95)), p_raw=float(st.permutation_p(obs[q], nulls[q])), n_perm_valid=int(np.isfinite(nulls[q]).sum())))
            r_null5 = nanmean0(np.stack([null[key, q] for q in pids]))
            for q in pids + ["mean5"]:
                r_obs, nl = (r5[key], r_null5) if q == "mean5" else (metrics[key, q]["r"], null[key, q])
                ep = st.permutation_p(r_obs, nl)
                ebh = st.bh(ep)  # 탐색. 참가자마다(5명 평균도 따로) 34개 정서
                nm = nanmean0(nl)
                for e in range(n_emo):
                    prem_emo.append(dict(analysis=name, condition=key[0], display=display(key[0]), seed=key[1], participant=q, emotion=emotions[e], r=r_obs[e],
                                         null_mean=nm[e], p_raw=ep[e], p_bh=ebh[e], label="탐색(BH-FDR)"))
        prem = pd.DataFrame(prem_rows)
        prem["p_holm2"] = np.nan
        prem["holm_note"] = ""
        for (seed, q), g in prem.groupby(["seed", "participant"]):
            if set(g.condition) == set(PREMISE):
                prem.loc[g.index, "p_holm2"] = st.holm(g.p_raw.to_numpy())  # O4 (4). [사전] 15개와 따로 한 Holm 2개 묶음
            else:
                prem.loc[g.index, "holm_note"] = "두 조건이 다 있어야 Holm 2개 묶음을 낸다"
        tables["premise_tests"] = prem
    else:
        tables["premise_tests"] = pd.DataFrame([dict(analysis=name, status="계산하지 않음: A-1, C-1 예측이 없거나 --n-perm 0")])
    tables["premise_per_emotion"] = pd.DataFrame(prem_emo)
    return tables, info


def subset(data, videos, keep_ids):
    """keep_ids 영상만 남긴 data와 videos."""
    keep_ids = set(int(v) for v in keep_ids)
    masks = {q: np.array([int(v) in keep_ids for v in vids]) for q, vids in videos.items()}
    return {key: {q: p[masks[q]] for q, p in by.items()} for key, by in data.items()}, {q: vids[masks[q]] for q, vids in videos.items()}


def check_out(out):
    """결과는 git에 올라가지 않는 곳에만 쓴다(M3)."""
    out = Path(out).resolve()
    repo = c.REPO.resolve()
    if (out == repo or repo in out.parents) and c.git("check-ignore", "-q", str(out)).returncode != 0:
        raise SystemExit(f"{out}: 레포 안의 git에 올라가는 위치다. 결과는 레포 밖(output_root)에 쓴다")


def run(s6_dir, out, split, y_split, emotions, *, dk_mode, split_pairs, boot_unit="video", n_boot=st.N_RESAMPLE, n_perm=st.N_RESAMPLE, overwrite=False, extra_info=None):
    """S6 결과 폴더의 예측으로 표를 만든다. split: load_split의 표, y_split: split 순서의 사람 평정(영상 × 정서)."""
    started = time.time()
    s6_dir, out = Path(s6_dir).resolve(), Path(out)
    check_out(out)
    if out.exists() and not overwrite:
        raise SystemExit(f"{out}가 이미 있다. 다시 쓰려면 --overwrite를 준다")
    if dk_mode not in DK_MODES:
        raise ValueError(f"--dk-mean은 {DK_MODES} 가운데 하나다(O25의 D_k 평균. 문서가 정하지 않았다)")
    if boot_unit not in ("video", "run"):
        raise ValueError("bootstrap 단위는 video(주, 같은 내용 묶음) 또는 run(민감도)이다(6-1)")
    y_split = np.asarray(y_split, np.float64)
    if y_split.shape != (len(split), len(emotions)):
        raise ValueError("사람 평정의 크기가 split, 정서 수와 다르다")
    found = find_predictions(s6_dir)
    if found.empty:
        raise SystemExit(f"{s6_dir}: 읽을 선택이 없다")
    coverage, usable = coverage_table(found)
    if not usable:
        raise SystemExit("6 fold가 모두 있는 조건이 없다")
    plan_rows = {k: plan_test_rows(s6_dir, k) for k in range(1, N_FOLDS + 1)}
    loaded = {}
    for cond, seed in usable:
        f = found[(found.condition == cond) & (found.seed == seed)]
        loaded[cond, seed] = load_condition(dict(zip(f.fold.astype(int), f.path)), split, plan_rows, len(emotions))
    videos = same_rows(loaded)
    data = {key: {q: p for q, (_, p) in by.items()} for key, by in loaded.items()}
    pids = sorted(videos)
    common = sorted(set.intersection(*[set(v.tolist()) for v in videos.values()]))
    if "in_all_5" in split.columns and len(pids) == 5 and set(common) != set(split.video_id[split.in_all_5.astype(bool)].astype(int)):
        raise ValueError("예측 행에서 낸 5명 공통 영상이 split의 in_all_5와 다르다(B7)")
    dkref = dk_reference(dk_mode, split, y_split, videos)
    kw = dict(n_boot=n_boot, n_perm=n_perm, boot_unit=boot_unit, split_pairs=split_pairs)
    results = {"all": analyze("all", data, videos, split, y_split, dkref, emotions, **kw)}
    d5, v5 = subset(data, videos, common)
    results["common5"] = analyze("common5", d5, v5, split, y_split, dkref, emotions, **kw)

    rows = []
    for q in pids:
        f = split.set_index("video_id").loc[videos[q], "fold"]
        rows.append(dict(participant=q, n_videos=len(videos[q]), n_videos_common5=len(v5[q]), **{f"n_fold{k}": int((f == k).sum()) for k in range(1, N_FOLDS + 1)}))
    rows_table = pd.DataFrame(rows)
    comp = results["all"][0]["comparisons"]
    pre = comp[(comp.kind == "prereg") & (comp.status == "ok")]
    prereg = pd.DataFrame(dict(test_id=pre.test_id, family=pre.participant, seed=pre.seed.astype(int), estimate=pre.estimate, p_raw=pre.p_raw, statistic="34개 정서 평균 r의 차이(앞 − 뒤)", source="s10_performance", analysis="all"))
    hashes = {str(Path(p).relative_to(s6_dir)) if Path(p).is_relative_to(s6_dir) else str(p): c.sha256(p) for p in found.path.dropna() if Path(p).exists()}
    info = dict(stage="S10 performance", s6_dir=str(s6_dir), code_commit=c.START_HEAD, code_dirty=c.START_DIRTY, settings=dict(dk_mean=dk_mode, split_content_pairs=split_pairs, bootstrap_unit=boot_unit,
                n_boot=n_boot, n_perm=n_perm, boot_seed=BOOT_SEED, perm_seed=PERM_SEED, ci_level=st.CI_LEVEL), conditions_used=[f"{a} seed {s}" for a, s in usable],
                participants=pids, n_emotions=len(emotions), prediction_sha256=hashes, analyses={k: v[1] for k, v in results.items()}, **(extra_info or {}))
    if n_boot != st.N_RESAMPLE or n_perm != st.N_RESAMPLE:
        info["note"] = f"재표집 횟수가 I5의 {st.N_RESAMPLE}회와 다르다. 점검용 실행이다"
    with c.Atomic(out) as tmp:
        write_tsv(coverage, tmp / "coverage.tsv")
        write_tsv(rows_table, tmp / "rows.tsv")
        write_tsv(prereg, tmp / "prereg_pvalues.tsv")
        for name, (tables, _) in results.items():
            (tmp / name).mkdir()
            for tname, t in tables.items():
                write_tsv(t, tmp / name / f"{tname}.tsv")
        info["elapsed_seconds"] = round(time.time() - started, 1)
        (tmp / "run_info.json").write_text(json.dumps(info, indent=1, ensure_ascii=False, default=str))
    return info


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 주 지표, 보조 지표, 2-3 비교, 0행 전제 검정")
    ap.add_argument("--s6-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dk-mean", required=True, choices=DK_MODES, help="O25의 D_k 평균: 참가자의 D_k 영상, 5명의 D_k 행, D_k 영상. 문서가 정하지 않아 기본값이 없다")
    ap.add_argument("--design-freeze", required=True)
    ap.add_argument("--split-content-pairs", action="store_true", help="같은 내용 영상 쌍이 다른 run에 있으면 순열에서 각자 자기 run 안에서 섞는다(O4 (1)이 정하지 않은 경우)")
    ap.add_argument("--bootstrap-unit", choices=("video", "run"), default="video", help="video가 주(6-1, 같은 내용 묶음), run은 민감도")
    ap.add_argument("--n-boot", type=int, default=st.N_RESAMPLE)
    ap.add_argument("--n-perm", type=int, default=st.N_RESAMPLE)
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args(argv)
    c.guard(a.design_freeze)  # 실제 결과는 동결 커밋과 커밋된 코드로만 낸다(M5)
    split = c.load_split()
    y, cols = c.load_scores(split, "emotions")
    emotions = pd.read_csv(c.LABEL_MAP, sep="\t").set_index("score_col").loc[cols, "name"].tolist()
    inputs = {"split_hk_dev.tsv": c.sha256(c.SPLITS / "split_hk_dev.tsv"), "labels": c.sha256(c.LABELS), "label_map_34.tsv": c.sha256(c.LABEL_MAP)}
    info = run(a.s6_dir, a.out, split, y, emotions, dk_mode=a.dk_mean, split_pairs=a.split_content_pairs, boot_unit=a.bootstrap_unit, n_boot=a.n_boot, n_perm=a.n_perm,
               overwrite=a.overwrite, extra_info=dict(design_freeze=a.design_freeze, inputs=inputs))
    print(f"끝: {a.out} ({info['elapsed_seconds']}초, 조건 {len(info['conditions_used'])}개)")


if __name__ == "__main__":
    main()
