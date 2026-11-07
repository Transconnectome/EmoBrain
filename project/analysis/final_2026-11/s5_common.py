#!/usr/bin/env python3
"""S5 공통: 허용 행만 읽는 뇌 입력과 dual ridge (04 S5, 01 N3, O18, O20, H5, 2026-11-06).

자료 경계
- 뇌 반응은 allowed_rows가 정한 개발 block만 읽는다(s2_manifest와 같은 규칙). MC 72개와 같은 내용이 표에 있으면 멈춘다.
- 입력은 공통 ROI의 voxel을 이어 붙인 것이고, ROI가 겹치는 voxel은 한 번만 쓴다(I10, 고유 voxel).
- 실제 자료로 돌리려면 설계 동결 커밋을 주어야 한다(s4_common.guard).

표준화(N3): 모델마다 그 모델의 실제 학습 자료로만 맞추고, 검증과 시험 자료에는 그 값을 적용한다.
ridge: n × n kernel을 분해하므로 목표가 늘어도 분해를 다시 쓴다(3-2). 절편은 학습 평균으로 처리한다.
"""
import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")  # O32. 결정적 모드에 필요하다

import numpy as np
import pandas as pd
import torch

import s4_common as c

torch.use_deterministic_algorithms(True)  # O32

PM = Path(os.environ.get("S5_PM", "/pscratch/sd/s/sjmoon"))
OUT = Path(os.environ.get("S5_OUT", c.REPO / "project/output/final_2026-11/s5_ridge"))
ROI_VOXELS = c.REPO / "project/output/final_2026-11/s2_manifest/roi_voxels"
BLOCKS = c.S2 / "participant_blocks_hk.tsv"
CROSSWALK = c.REPO / "prereg_v2/manifests/stimulus_crosswalk.tsv"
MC72 = c.CODE_DIR / "manifests/mc_test72.tsv"
STIMULI = c.REPO / "prereg_v2/manifests/stimuli.tsv"
HK = ["01", "02", "03", "04", "05"]
LAMBDAS = np.logspace(1, 6, 10)  # O18
H2020_LAMBDAS = np.logspace(1, 4, 20)  # O18, I7. Horikawa 외(2020) 공개 코드
H2020_VOXELS = 500  # I7
H2020_ENSEMBLE_THRESHOLD = 0.095  # 공개 코드 summary_decoding_results.m 9행. 안쪽 r이 이 값 이상인 ROI의 예측을 평균한다
SOFT_BCE_DECAYS = (1e-4, 1e-3, 1e-2)  # O24, E3
SOFT_BCE_LRS = (1e-4, 1e-3, 1e-2)  # O24, G13. 뇌 모델과 같이 learning rate도 후보로 고른다(11/7)
SOFT_BCE = dict(batch=64, max_epochs=300, patience=30, seed=0)  # O24, G13
VISUAL_LAYERS = list(range(1, 41))
CAPTION_LAYERS = list(range(1, 25))
LAYERS = [("vjepa2", b) for b in VISUAL_LAYERS] + [("deberta", l) for l in CAPTION_LAYERS]
TARGET_LAYERS = [("vjepa2", b) for b in (10, 20, 30, 40)] + [("deberta", l) for l in (6, 12, 18, 24)]  # O21
S2_TABLES = [c.S2 / "split_hk_dev.tsv", c.S2 / "fold_roles.tsv", c.S2 / "content_blocks_assignment.tsv", c.S2 / "content_block_control_samples.tsv", c.LABEL_MAP, BLOCKS, CROSSWALK, MC72]
START_CODE = {f.name: c.sha256(f) for f in sorted(c.CODE_DIR.glob("s[45]_*.py"))}


class Run:
    """한 실행의 출처. s4_common.Run과 같은 뜻이고, S5 코드까지 해시한다."""

    def __init__(self, design_freeze, inputs, **settings):
        self.paths = {**{f"s2:{p.name}": Path(p) for p in S2_TABLES}, **{k: Path(p) for k, p in inputs.items()}}
        self.hashes = {k: c.sha256(p) for k, p in self.paths.items()}
        self.prov = dict(code_commit=c.START_HEAD, code_dirty=c.START_DIRTY, code_sha256=START_CODE, design_freeze=design_freeze, inputs=self.hashes, input_paths={k: str(p) for k, p in self.paths.items()}, settings=settings)
        self._check_code()
        key = json.dumps(dict(code=START_CODE, inputs=self.hashes, settings=settings, design_freeze=design_freeze), sort_keys=True, default=str)
        self.prov["run_key"] = hashlib.sha256(key.encode()).hexdigest()

    def _check_code(self):
        if {f.name: c.sha256(f) for f in sorted(c.CODE_DIR.glob("s[45]_*.py"))} != START_CODE:
            raise SystemExit("시작 뒤 코드가 바뀌었다.")

    def check(self):
        self._check_code()
        for k, p in self.paths.items():
            if c.sha256(p) != self.hashes[k]:
                raise SystemExit(f"시작 뒤 입력이 바뀌었다: {k} ({p})")

    @property
    def key(self):
        return self.prov["run_key"]


def response_path(s, normalized=True):
    name = "blocks_common36_qc_runz" if normalized else "blocks_common36_qc"
    return PM / f"Horikawa/sub-{s}/v3_qc/sub-{s}_{name}.npy"


def roi_path(s):
    return ROI_VOXELS / f"hk_sub-{s}.npz"


def check_qc_rows(rows, n_rows=None):
    """반응 행 번호는 음수가 아닌 정수이고 겹치지 않아야 한다. -1은 마지막 행을 읽고, 겹치면 같은 반응이 다른 영상에 붙는다."""
    rows = np.asarray(rows)
    if not np.issubdtype(rows.dtype, np.integer):
        raise ValueError("반응 행 번호가 정수가 아니다")
    if (rows < 0).any() or len(set(rows.tolist())) != len(rows):
        raise ValueError("반응 행 번호에 음수나 중복이 있다")
    if n_rows is not None and (rows >= n_rows).any():
        raise ValueError("반응 행 번호가 배열 범위를 벗어났다")
    return rows


def allowed_rows(s, table=None, crosswalk=None, mc72=None):
    """반응 배열에서 읽어도 되는 행을 metadata로 먼저 정한다. MC 72개와 같은 내용이 있으면 멈춘다(s2_manifest.allowed_response_rows와 같은 규칙)."""
    table = pd.read_csv(BLOCKS, sep="\t") if table is None else table
    cw = pd.read_csv(CROSSWALK, sep="\t", comment="#").set_index("video_number").canonical_stimulus_id if crosswalk is None else crosswalk
    mc = set(pd.read_csv(MC72, sep="\t").canonical_stimulus_id) if mc72 is None else set(mc72)
    t = table[table.participant == f"sub-{s}"]
    canon = t.video_id.map(cw)
    if len(t) == 0 or canon.isna().any() or canon.isin(mc).any():
        raise ValueError(f"sub-{s}: 허용 행에 MC 시험 72개와 같은 내용이 있거나 표가 비었다")
    check_qc_rows(t.qc_row.to_numpy())
    return t.sort_values("qc_row").reset_index(drop=True)


def read_rows(raw, rows, allowed):
    """반응 배열을 읽는 유일한 입구. 허용되지 않은 행을 요청하면 읽기 전에 멈춘다."""
    rows = check_qc_rows(rows, raw.shape[0])
    check_qc_rows(allowed, raw.shape[0])
    if not np.isin(rows, allowed).all():
        raise ValueError(f"허용되지 않은 반응 행 요청: {rows[~np.isin(rows, allowed)][:5]}")
    return np.asarray(raw[rows], np.float32)


@dataclass
class BrainSet:
    """참가자 한 명의 개발 block. 행 순서는 qc_row다."""
    participant: str
    X: np.ndarray  # block × 고유 voxel
    video_id: np.ndarray
    fold: np.ndarray
    roi_positions: list  # ROI마다 X의 열 위치
    n_voxels_with_overlap: int = 0

    def rows(self, ids):
        return np.flatnonzero(np.isin(self.video_id, list(ids)))


def load_brain(s, split, raw_path=None, roi_file=None, table=None, crosswalk=None, mc72=None):
    t = allowed_rows(s, table, crosswalk, mc72)
    c.check_dev(t.video_id.to_numpy(), split)
    if not t.video_id.is_unique:
        raise ValueError("한 영상의 block이 둘 이상이다")
    z = np.load(roi_path(s) if roi_file is None else roi_file)
    columns, offsets = z["columns"], z["offsets"]
    unique = np.unique(columns)
    raw = np.load(response_path(s) if raw_path is None else raw_path, mmap_mode="r")
    if raw.shape[1] != int(z["n_columns"]):
        raise ValueError("반응 배열의 열 수가 ROI 표와 다르다")
    rows = t.qc_row.to_numpy()
    X = np.empty((len(rows), len(unique)), np.float32)
    for i in range(0, len(rows), 64):
        X[i:i + 64] = read_rows(raw, rows[i:i + 64], rows)[:, unique]
    c.finite(X, f"sub-{s} 반응")
    fold_of = dict(zip(split.video_id, split.fold))
    pos = [np.searchsorted(unique, columns[offsets[i]:offsets[i + 1]]) for i in range(len(offsets) - 1)]
    return BrainSet(f"sub-{s}", X, t.video_id.to_numpy(), np.array([fold_of[v] for v in t.video_id]), pos, len(columns))


def signal_baseline_input(s, split, raw_path=None, table=None, crosswalk=None, mc72=None):
    """뇌 전체 평균과 block 신호 크기(I7). 정규화 전 block 반응의 block마다 voxel 평균과 voxel 간 표준편차다.
    정의는 prelim_2026-10/prelim/confound_and_block_check.py 169행(04 기록 칸 S1)이고, 그 코드처럼 QC mask의 모든 voxel을 쓴다."""
    t = allowed_rows(s, table, crosswalk, mc72)
    c.check_dev(t.video_id.to_numpy(), split)
    raw = np.load(response_path(s, normalized=False) if raw_path is None else raw_path, mmap_mode="r")
    rows = t.qc_row.to_numpy()
    out = np.empty((len(rows), 2))
    for i in range(0, len(rows), 64):
        a = np.asarray(read_rows(raw, rows[i:i + 64], rows), np.float64)
        out[i:i + 64, 0], out[i:i + 64, 1] = a.mean(1), a.std(1)
    return c.finite(out, f"sub-{s} block 통계"), t.video_id.to_numpy()


def align(values, split, ids):
    """split 순서의 값에서 ids 행을 뽑는다."""
    pos = {v: i for i, v in enumerate(split.video_id.tolist())}
    return values[[pos[v] for v in np.asarray(ids).tolist()]]


def as_tensor(x, device):
    return torch.as_tensor(np.asarray(x, np.float64), device=device)


def standardize(x, rows):
    m, s = x[rows].mean(0), x[rows].std(0, unbiased=False)
    if (s <= 0).any():
        raise ValueError("학습 자료에서 표준편차가 0인 차원이 있다")
    return (x - m) / s, m, s


class DualRidge:
    """표준화한 입력의 n × n kernel을 분해해 둔다. others: 이름 -> 예측할 행. 입력은 train으로만 표준화한다(N3)."""

    def __init__(self, x, train, others):
        z, _, _ = standardize(x, train)
        ztr = z[train]
        k = ztr @ ztr.T
        self.values, self.vectors = torch.linalg.eigh(k)
        self.values = self.values.clamp_min(0)
        self.cross = {n: (z[r] @ ztr.T) @ self.vectors for n, r in others.items()}

    def fit(self, y_train):
        ym = y_train.mean(0)
        return ym, self.vectors.T @ (y_train - ym)

    def predict(self, name, fitted, lam):
        ym, uty = fitted
        out = ym + self.cross[name] @ ((1 / (self.values + float(lam)))[:, None] * uty)
        if not torch.isfinite(out).all():
            raise ValueError("ridge 예측에 NaN 또는 Inf가 있다")
        return out


def r_selection(y, p):
    """열마다 선택용 r. y가 상수인 열은 NaN이고, 예측이 상수이면 0이다(O6). 예측의 NaN은 오류다."""
    if not torch.isfinite(p).all():
        raise ValueError("예측에 NaN 또는 Inf가 있다")
    yc, pc = y - y.mean(0), p - p.mean(0)
    den = torch.sqrt((yc**2).sum(0) * (pc**2).sum(0))
    r = torch.where(den > 0, (yc * pc).sum(0) / den.clamp_min(1e-30), torch.zeros_like(den))
    return torch.where((yc**2).sum(0) > 0, r, torch.full_like(r, float("nan")))


def pick_per_target(scores):
    """scores: λ × 목표. 목표마다 큰 값의 λ. 같으면 작은 λ다(O6). 정답이 상수라 고를 수 없으면 멈춘다."""
    if scores.isnan().any():
        raise ValueError("정답이 상수라 λ를 고를 수 없는 목표가 있다")
    return scores.argmax(0)


def main_version(x, y, train, val, test, lambdas=LAMBDAS):
    """주 비교판(N15, O18). 검증 fold로 목표마다 λ를 고르고, train으로 학습한 모델을 그대로 시험한다."""
    d = DualRidge(x, train, dict(val=val, test=test))
    fitted = d.fit(y[train])
    scores = torch.stack([r_selection(y[val], d.predict("val", fitted, lam)) for lam in lambdas])
    pick = pick_per_target(scores)
    paths = torch.stack([d.predict("test", fitted, lam) for lam in lambdas])
    return paths.gather(0, pick[None, None, :].expand(1, len(test), y.shape[1]))[0], pick


def literature_version(x, y, fold, dk_folds, test, lambdas=LAMBDAS):
    """문헌판(H3, O18). D_k 안쪽 5겹의 r 평균으로 목표마다 λ를 고르고 D_k 전체로 학습한다."""
    dk = np.flatnonzero(np.isin(fold, dk_folds))
    scores = []
    for j in dk_folds:
        tr, va = dk[fold[dk] != j], dk[fold[dk] == j]
        d = DualRidge(x, tr, dict(val=va))
        fitted = d.fit(y[tr])
        scores.append(torch.stack([r_selection(y[va], d.predict("val", fitted, lam)) for lam in lambdas]))
    pick = pick_per_target(torch.stack(scores).nanmean(0))
    d = DualRidge(x, dk, dict(test=test))
    fitted = d.fit(y[dk])
    paths = torch.stack([d.predict("test", fitted, lam) for lam in lambdas])
    return paths.gather(0, pick[None, None, :].expand(1, len(test), y.shape[1]))[0], pick
