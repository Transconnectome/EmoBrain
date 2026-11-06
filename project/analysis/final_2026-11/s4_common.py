#!/usr/bin/env python3
"""S4 공통: 분할, 자료 읽기, 표준화, 실행 기록 (04 S4, 01 H2, H3, H4, N3, 4-3, 2026-11-06).

자료 경계
- 개발 영상 2,109개만 읽는다. MC 72개와 그 중복 영상의 특징과 정답은 어느 단계에도 넣지 않는다(check_dev).
- 뇌 반응은 읽지 않는다. 정서 정답과 14개 차원 정답은 특징 모델과 정서어 제거판에서만 읽는다.
- 실제 자료로 돌리려면 설계 동결 커밋을 주어야 한다(guard). 합성 자료 시험에서는 allow_test로 넘어간다.

표준화(N3, H4): 바깥 학습 자료 D_k에서 차원마다 평균과 표준편차를 한 번 맞추고, 그 안의 안쪽 fold도 같은 좌표를 쓴다. 시험 fold는 맞추는 데 쓰지 않는다.
"""
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[3]
CODE_DIR = REPO / "project/analysis/final_2026-11"
S2 = CODE_DIR / "manifests/s2"
LABEL_MAP = CODE_DIR / "manifests/label_map_34.tsv"
FEATURES = Path(os.environ.get("S4_FEATURES", REPO / "project/output/final_2026-11/s3_features"))
OUT = Path(os.environ.get("S4_OUT", REPO / "project/output/final_2026-11/s4_no_brain"))
LABELS = Path(os.environ.get("S4_LABELS", REPO / "project/shared/data/cowen_horikawa_labels.csv"))
DIMENSIONS = ["arousal", "dominance", "valence", "approach", "attention", "certainty", "commitment", "control", "effort", "fairness", "identity", "obstruction", "safety", "upswing"]
VISUAL_TARGET, CAPTION_TARGET, CAPTION_NO_EMOTION = "vjepa2/target", "deberta/target", "deberta_no_emotion_words/target"
LOWLEVEL = "lowlevel/lowlevel"
N_FOLDS = 6


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(2**22), b""):
            h.update(b)
    return h.hexdigest()


def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)


# 실행 출처는 코드를 불러온 그때 고정한다(S3와 같은 규칙, M2)
START_CODE = {f.name: sha256(f) for f in sorted(CODE_DIR.glob("s4_*.py"))}
START_HEAD = git("rev-parse", "HEAD").stdout.strip()
START_DIRTY = git("status", "--porcelain", "--", str(CODE_DIR)).stdout.strip() != ""


def guard(design_freeze, allow_test=False):
    """실제 결과는 설계 동결 뒤에만 낸다(M5). 코드가 커밋되지 않았거나 동결 커밋이 현재 코드의 조상이 아니면 멈춘다."""
    if allow_test:
        return
    if not design_freeze:
        raise SystemExit("설계 동결 커밋을 --design-freeze로 주어야 한다(04 S0, M5). 동결 전에는 실제 자료로 돌리지 않는다.")
    if START_DIRTY:
        raise SystemExit("커밋되지 않은 코드가 있다.")
    if git("merge-base", "--is-ancestor", design_freeze, "HEAD").returncode != 0:
        raise SystemExit(f"{design_freeze}가 현재 커밋의 조상이 아니다.")


def provenance(design_freeze=None, inputs=(), **settings):
    now = {f.name: sha256(f) for f in sorted(CODE_DIR.glob("s4_*.py"))}
    if now != START_CODE:
        raise SystemExit("시작 뒤 코드가 바뀌었다.")
    return dict(code_commit=START_HEAD, code_dirty=START_DIRTY, code_sha256=START_CODE, design_freeze=design_freeze, inputs={str(p): sha256(p) for p in inputs}, **settings)


def load_split():
    s = pd.read_csv(S2 / "split_hk_dev.tsv", sep="\t").sort_values("video_id").reset_index(drop=True)
    if len(s) != 2109 or not s.video_id.is_unique:
        raise ValueError("개발 영상이 2,109개가 아니다")
    return s


def roles(k):
    """바깥 fold k의 시험, 검증(H2. 다음 fold), 학습 fold. 표 fold_roles.tsv와 같아야 한다."""
    val = k % N_FOLDS + 1
    train = [f for f in range(1, N_FOLDS + 1) if f not in (k, val)]
    t = pd.read_csv(S2 / "fold_roles.tsv", sep="\t")
    row = t[(t.role == "outer") & (t.test_fold == k)].iloc[0]
    if int(row.val_fold) != val or [int(x) for x in str(row.train_folds).split(",")] != train:
        raise ValueError(f"fold {k}의 역할이 표와 다르다")
    return dict(test=k, val=val, train=train, dk=sorted(train + [val]))


def final_roles():
    """6-3의 HK 최종 모델(O7). fold 1이 검증이고 fold 2~6이 학습이다. 바깥 시험 fold가 없다."""
    t = pd.read_csv(S2 / "fold_roles.tsv", sep="\t")
    row = t[t.role == "final_for_mc_O7"].iloc[0]
    return dict(test=None, val=int(row.val_fold), train=[int(x) for x in str(row.train_folds).split(",")], dk=list(range(1, N_FOLDS + 1)))


def check_dev(ids, split):
    extra = set(np.asarray(ids).tolist()) - set(split.video_id.tolist())
    if extra:
        raise ValueError(f"개발 영상이 아닌 영상을 읽으려 했다: {sorted(extra)[:5]}")


def load_rows(name, ids, split):
    """특징 파일에서 허용한 행만 읽는다. 행 i는 video_id i + 1이다."""
    check_dev(ids, split)
    a = np.load(FEATURES / f"{name}.npy", mmap_mode="r")
    if a.shape[0] != 2196:
        raise ValueError(f"{name}: 영상이 2,196개가 아니다")
    return np.asarray(a[np.asarray(ids) - 1], np.float32)


def load_scores(split, kind):
    """정답. 행 i는 split의 행 i다. content_id로 붙인다(기록 칸 S0)."""
    y = pd.read_csv(LABELS).set_index("stim_num_int")
    cols = pd.read_csv(LABEL_MAP, sep="\t").score_col.tolist() if kind == "emotions" else [f"{d}_score" for d in DIMENSIONS]
    out = y.loc[split.content_id.to_numpy(), cols].to_numpy(np.float32)
    if not np.isfinite(out).all():
        raise ValueError("정답에 결측이 있다")
    return out, cols


def fit_standardizer(x):
    x = np.asarray(x, np.float64)  # 평균을 float32로 더하면 오차가 쌓인다
    m, s = x.mean(0), x.std(0)
    if (s <= 0).any():
        raise ValueError("표준편차가 0인 차원이 있다")
    return m, s


def zone_sets(split, block, k, kind, blocks=None, control=None):
    """6-2의 분할(4-3의 표). 돌려주는 값: 학습 자료(가중치 학습 + 검증) video_id, 시험 video_id."""
    blocks = pd.read_csv(S2 / "content_blocks_assignment.tsv", sep="\t") if blocks is None else blocks
    r = roles(k)
    in_block = set(blocks.video_id[blocks.block == block].tolist())
    fold_of = dict(zip(split.video_id, split.fold))
    test = sorted(v for v in in_block if fold_of[v] == k)
    excluded = sorted(v for v, f in fold_of.items() if f != k and v not in in_block)
    if kind == "excluded":
        return excluded, test
    if kind != "control":
        raise ValueError(kind)
    control = pd.read_csv(S2 / "content_block_control_samples.tsv", sep="\t") if control is None else control
    c = control[(control.block == block) & (control.fold == k)]
    tr, va = c.video_id[c.role == "train"].tolist(), c.video_id[c.role == "val"].tolist()
    if any(fold_of[v] not in r["train"] for v in tr) or any(fold_of[v] != r["val"] for v in va):
        raise ValueError("학습량 대조 표본이 학습 fold와 검증 fold를 벗어났다")
    ex_tr = sum(fold_of[v] in r["train"] for v in excluded)
    if len(tr) != ex_tr or len(va) != len(excluded) - ex_tr:
        raise ValueError("학습량 대조의 영상 수가 구역 제외와 다르다")
    return sorted(tr + va), test


def done_or_new(path, code):
    """끝난 결과는 같은 코드일 때만 건너뛴다. 다른 코드의 결과와 섞지 않고 멈춘다."""
    d = Path(path) / "done.json"
    if not d.exists():
        return False
    if json.loads(d.read_text()).get("code_sha256") != code:
        raise SystemExit(f"{path}: 다른 코드로 만든 결과가 있다. 지우고 다시 돌려야 한다.")
    return True


class Atomic:
    """결과 폴더를 임시 폴더에 다 쓴 뒤 옮긴다. 도중에 끊겨도 반쯤 쓴 결과가 남지 않는다."""

    def __init__(self, path):
        self.path = Path(path)

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.tmp = Path(tempfile.mkdtemp(dir=self.path.parent, prefix=f".{self.path.name}_"))
        return self.tmp

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:
            shutil.rmtree(self.tmp, ignore_errors=True)
            return False
        if self.path.exists():
            shutil.rmtree(self.path)
        os.chmod(self.tmp, 0o770)
        self.tmp.rename(self.path)
        return False


def pearson(a, b):
    """열마다 Pearson r. 두 값 중 하나가 상수이면 NaN이다(계산 불가, 2-6)."""
    a, b = np.asarray(a, np.float64), np.asarray(b, np.float64)
    a, b = a - a.mean(0), b - b.mean(0)
    den = np.sqrt((a**2).sum(0) * (b**2).sum(0))
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(den > 0, (a * b).sum(0) / den, np.nan)
