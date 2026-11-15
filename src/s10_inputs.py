#!/usr/bin/env python3
"""S10 2부의 공통 읽기 함수 (04 S10, 01 2-1, 6-2, 6-3, 6-4, N11, O19, O20, 2026-11-15). 계산은 s10_stats가 한다.

- S6 꼴의 결과 폴더(<분할 폴더>/plan, <분할 폴더>/<조건>/selected.json)에서 시험 예측과 decoded features를 읽는다. 바깥 fold 폴더(outer_fold<k>), 6-2의 구역 분할 폴더(zone_block<b>_fold<k>_<방식>), 6-4a 묶음 결과 폴더가 같은 꼴이다.
- 행 대조(N11): 예측 행(참가자, 영상)은 그 분할 폴더 plan/rows.npz의 시험 행과 같아야 한다. 다르면 멈춘다.
- decoded features는 학습 fold 4개의 D9 눈금으로 저장되어 있다(s6_train 머리말). 그 분할의 plan/standardization.npz로 되돌려 원래 척도로 바꾼다(O20).
- 실제 Vision feature, Caption feature는 S3의 target 파일(V-JEPA 2 block 10, 20, 30, 40 이어 붙임 5,632차원, DeBERTa 층 6, 12, 18, 24 이어 붙임 4,096차원, D9, O21)이다. 개발 영상만 읽는다.
- 빠진 입력은 표로 적고, 최종 표는 입력이 모두 있을 때만 낸다(require_complete). --partial-check는 읽기와 행 대조를 보는 점검용이고 그 표를 결과로 쓰지 않는다.
"""
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

import s4_common as c
import s10_stats as st

N_FOLDS = 6
HK_PIDS = [f"sub-0{i}" for i in range(1, 6)]
FEATURES = {"vision": (c.VISUAL_TARGET, "visual"), "caption": (c.CAPTION_TARGET, "caption")}  # 이름 -> (S3 target, standardization.npz의 접두어)
DIMS = {"vision": 5632, "caption": 4096}  # D9, O21
PARTIAL_NOTE = "점검용 실행(--partial-check): 빠진 입력이 있어 결과로 쓰지 않는다"


def emotion_names(cols=None):
    """사람 평정 열 순서(s4_common.load_scores)의 정서 이름."""
    m = pd.read_csv(c.LABEL_MAP, sep="\t").set_index("score_col")
    if cols is None:
        cols = pd.read_csv(c.LABEL_MAP, sep="\t").score_col.tolist()
    return m.loc[cols, "name"].tolist()


def participant_videos(split, table=None):
    """참가자마다 block이 있는 개발 영상(S2 participant_blocks_hk.tsv). 돌려주는 값: 참가자 -> 영상 번호 오름차순."""
    t = pd.read_csv(c.S2 / "participant_blocks_hk.tsv", sep="\t") if table is None else table
    dev = set(split.video_id.astype(int).tolist())
    return {q: np.array(sorted(set(g.video_id.astype(int)) & dev)) for q, g in t.groupby("participant")}


def actual_features(split, ids):
    """영상 ids(개발 영상)의 실제 Vision feature와 Caption feature. 원래 척도, float32."""
    ids = np.asarray(ids, np.int64)
    return {name: c.load_rows(path, ids, split) for name, (path, _) in FEATURES.items()}


def plan_test_rows(plan_dir):
    """plan/rows.npz의 시험 행(참가자, 영상)."""
    path = Path(plan_dir) / "plan" / "rows.npz"
    if not path.exists():
        raise SystemExit(f"{path}가 없다. 시험 행을 대조할 수 없다")
    z = np.load(path)
    t = z["role"] == 2
    return set(zip(z["participant"][t].astype(str).tolist(), z["video_id"][t].astype(np.int64).tolist()))


def selected_seeds(plan_dir, condition):
    """selected.json의 seed -> 결과 폴더. 없으면 None."""
    path = Path(plan_dir) / condition / "selected.json"
    if not path.exists():
        return None
    sel = json.loads(path.read_text())
    return {int(s): Path(plan_dir) / rel for s, rel in sel["seeds"].items()}


def _by_participant(pid, vid, arrays):
    out = {}
    for q in np.unique(pid):
        m = pid == q
        order = np.argsort(vid[m])
        out[str(q)] = (vid[m][order], *[a[m][order] for a in arrays])
    return out


def _check_rows(path, pid, vid, want):
    keys = list(zip(pid.tolist(), vid.tolist()))
    if len(set(keys)) != len(keys):
        raise ValueError(f"{path}: 한 참가자의 같은 영상 행이 둘 이상이다")
    if set(keys) != want:
        raise ValueError(f"{path}: 예측 행이 plan의 시험 행과 다르다(빠진 행 {len(want - set(keys))}, 남는 행 {len(set(keys) - want)}). N11")


def load_test_pred(path, want, n_emotions):
    """시험 예측 파일(test_pred.npz, test_outputs.npz의 p). want: plan의 시험 행. 돌려주는 값: 참가자 -> (영상 번호, p)."""
    z = np.load(path)
    pid, vid, p = z["participant"].astype(str), z["video_id"].astype(np.int64), np.asarray(z["p"], np.float64)
    if p.shape != (len(vid), n_emotions):
        raise ValueError(f"{path}: 예측 크기 {p.shape}")
    if not np.isfinite(p).all() or (p < 0).any() or (p > 1).any():
        raise ValueError(f"{path}: 예측 확률에 NaN이 있거나 0~1을 벗어났다")
    _check_rows(path, pid, vid, want)
    return _by_participant(pid, vid, [p])


def load_decoded(seed_dir, plan_dir, want):
    """C-1의 decoded features(outputs/decoded_test.npz)를 그 분할의 D9 통계로 되돌린 원래 척도 값(O20). 돌려주는 값: 참가자 -> (영상 번호, vision, caption)."""
    path = Path(seed_dir) / "outputs" / "decoded_test.npz"
    z = np.load(path)
    s = np.load(Path(plan_dir) / "plan" / "standardization.npz")
    pid, vid = z["participant"].astype(str), z["video_id"].astype(np.int64)
    _check_rows(path, pid, vid, want)
    out = []
    for name, key in (("vision", "v_hat"), ("caption", "c_hat")):
        pre = FEATURES[name][1]
        x = np.asarray(z[key], np.float64)
        if x.shape != (len(vid), DIMS[name]) or not np.isfinite(x).all():
            raise ValueError(f"{path}: {key}의 크기 {x.shape}가 다르거나 NaN이 있다")
        out.append(x * s[f"{pre}_std"] + s[f"{pre}_mean"])
    return _by_participant(pid, vid, out)


def decoding_scores(true, pred):
    """2-1의 지표(O19, O20): 모은 시험 영상에서 차원별 Pearson r의 평균. 상수 차원은 빼고 수를 센다. 돌려주는 값: (평균, 계산 불가 차원 수, 차원별 r)."""
    r = st.pearson_columns(true, pred)
    ok = np.isfinite(r)
    return (float(r[ok].mean()) if ok.any() else np.nan), int((~ok).sum()), r


def require_complete(missing, partial_check, what):
    """빠진 입력이 있으면 최종 표를 내지 않는다. --partial-check일 때만 점검용으로 이어 간다."""
    if len(missing) and not partial_check:
        raise SystemExit(f"{what}: 빠진 입력이 {len(missing)}개 있어 최종 표를 내지 않는다. 목록은 missing.tsv와 같은 형식이다:\n"
                         + pd.DataFrame(missing).head(30).to_string(index=False) + "\n점검만 하려면 --partial-check를 준다")


def write_tsv(t, path):
    """seed와 n_으로 시작하는 개수 열은 정수로 쓴다(빈 칸은 비워 둔다)."""
    t = t.copy()
    for col in t.columns:
        if col == "seed" or (col.startswith("n_") and pd.api.types.is_numeric_dtype(t[col])):
            v = pd.to_numeric(t[col], errors="coerce")
            if (v.dropna() % 1 == 0).all():
                t[col] = v.astype("Int64")
    t.to_csv(path, sep="\t", index=False)


def prepare_out(out, overwrite):
    """계산 전에 출력 위치를 본다. 레포 안 git 위치에는 쓰지 않고(M3), 이미 있으면 --overwrite 없이 덮지 않는다."""
    import s10_performance as perf
    out = Path(out)
    perf.check_out(out)
    if out.exists() and not overwrite:
        raise SystemExit(f"{out}가 이미 있다. 다시 쓰려면 --overwrite를 준다")
    return out


def write_out(out, tables, info, started, arrays=None):
    """표, 배열(arrays.npz), run_info.json을 한 번에 쓴다(Atomic)."""
    info = dict(info, code_commit=c.START_HEAD, code_dirty=c.START_DIRTY)
    with c.Atomic(Path(out)) as tmp:
        for name, t in tables.items():
            write_tsv(t, tmp / f"{name}.tsv")
        if arrays:
            np.savez(tmp / "arrays.npz", **arrays)
        info["elapsed_seconds"] = round(time.time() - started, 1)
        (tmp / "run_info.json").write_text(json.dumps(info, indent=1, ensure_ascii=False, default=str))
    return info


def ci_row(theta, boot):
    lo, hi = st.basic_ci(theta, boot)
    return float(lo), float(hi)
