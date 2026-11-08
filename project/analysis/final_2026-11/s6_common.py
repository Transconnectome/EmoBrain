#!/usr/bin/env python3
"""S6 공통: 조건과 후보, 자료 경계, 선택 규칙, 실행 기록 (04 S6, 01 5-A, G9, G13, H2, N3, O1, O5, O6, 2026-11-07).

자료 경계는 prepare_fold와 FoldData 안에서 강제한다.
- 학습, 검증, 시험 영상은 겹치지 않고 모두 개발 영상이다. MC 72개와 그 중복이 있으면 멈춘다. 한 영상의 행은 항상 같은 쪽이다(H6).
- voxel은 참가자별로, feature 목표는 차원마다 그 실행의 학습 자료로만 표준화한다(N3, C5, D9). 통계는 저장한다.
- 시험 영상의 사람 평정과 feature는 FoldData에 없다. 시험 행의 정답을 달라고 하면 멈춘다. 시험 성능은 S10이 저장한 예측으로 낸다(N24).
- Stimulus 예측 평정은 학습 영상에만 붙는다(E4). 평균 목표와 섞기도 학습 자료 안에서만 만든다(G6, O1).
- 뇌 입력은 s5_common.load_brain의 허용 행으로만 읽는다.

선택(O6, 0-2): 검증 자료의 정서별 Pearson r을 참가자마다 내고 34개 정서와 참가자에 걸쳐 평균한다. y가 상수인 정서는 뺀다. 예측이 상수이면 선택 계산에서만 0으로 센다.
점수가 같으면 작은 d, λ, α, r, weight decay, learning rate 순으로 고른다. 조기 종료는 검증 자료의 정서 soft BCE다. 모두 실제 y로 계산하고 섞은 목표나 feature loss로 고르지 않는다.
"""
import hashlib
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
import torch

import s4_common as c
import s5_common as d5
import s6_model as M
from s6_model import AUDITION_PATH, ac

LEARNING_RATES = (1e-4, 1e-3, 1e-2)  # G13(11/7). 후보 목록은 이 한 곳에서 받는다
ALPHAS = (0.25, 0.5)  # G9. 0은 앞 조건과 같아 새로 학습하지 않는다
LAMBDAS_FEATURE = (0.1, 1.0)  # G9
RANKS = M.INTERACTION_RANKS  # 5-4
MULTIMODAL_DECAYS = (1e-4, 1e-3, 1e-2)  # O5
SEEDS = (0, 1, 2)  # G14, L9
BATCH, MAX_EPOCHS, PATIENCE = 64, 300, 30  # G13
OUT = Path(os.environ.get("S6_OUT", c.REPO / "project/output/final_2026-11/s6_brain"))
MANIFEST = c.CODE_DIR / "manifests/s6"
START_CODE = {f.name: c.sha256(f) for f in sorted(c.CODE_DIR.glob("s[456]_*.py"))}
START_CODE[AUDITION_PATH.name] = c.sha256(AUDITION_PATH)


@dataclass(frozen=True)
class Condition:
    thesis: str  # 1-1의 이름
    feature_head: bool = False
    decoded: bool = False
    target: str = "human"  # human, stimulus, stimulus_shuffled, mean
    features: str = "none"  # none, actual, shuffled
    representation: str = ""  # frozen, trained
    pooling: bool = False
    multimodal: bool = False
    additive: bool = False


CONDITIONS = {
    "brain_only": Condition("Direct training"),  # 조건 1
    "brain_only_featdec": Condition("Auxiliary feature decoding", feature_head=True, features="actual"),  # 조건 2
    "brain_decoded": Condition("Decoded-feature readout", feature_head=True, decoded=True, features="actual"),  # 조건 3, 상호작용 head
    "brain_decoded_additive": Condition("Decoded-feature readout (additive head)", feature_head=True, decoded=True, features="actual", additive=True),  # 조건 3, 더하기 head
    "brain_only_distill": Condition("Response-based distillation", target="stimulus"),  # 조건 4
    "brain_decoded_distill": Condition("Decoded-feature readout + response-based distillation", feature_head=True, decoded=True, features="actual", target="stimulus"),  # 조건 5
    "multimodal": Condition("Multimodal Model", multimodal=True),  # 조건 6, 7의 준비
    "brain_only_repr_frozen": Condition("Representation, frozen head", representation="frozen"),  # 조건 6
    "brain_only_repr_trained": Condition("Representation, trained head", representation="trained"),  # 조건 7
    "control_label_smoothing": Condition("Control: label smoothing", target="mean"),  # G11
    "control_stimulus_shuffle": Condition("Control: shuffled Stimulus predictions", target="stimulus_shuffled"),  # G12
    "control_feature_shuffle": Condition("Control: shuffled feature pairs", feature_head=True, features="shuffled"),  # G12
    "brain_only_pool": Condition("Direct training (mean pooling)", pooling=True),  # F7
    "brain_decoded_pool": Condition("Decoded-feature readout (mean pooling)", feature_head=True, decoded=True, features="actual", pooling=True),  # F7
}
ORDER = list(CONDITIONS)  # 앞 조건의 선택을 뒤 조건이 쓴다(5-5, G9, O5, O31)
ZONE_CONDITIONS = {"brain_only", "brain_decoded"}  # 6-2(4-3). 다른 조건으로 넓히지 않는다
NEEDS_STIMULUS = {"brain_only_distill", "brain_decoded_distill", "control_stimulus_shuffle"}
NEEDS_SHUFFLE = {"control_stimulus_shuffle", "control_feature_shuffle"}
POOLED = {"brain_only_pool": "brain_only", "brain_decoded_pool": "brain_decoded"}  # O31. 표준 실행의 설정을 그대로 쓴다
ZERO_SOURCE = {"brain_only_distill": ("brain_only", "alpha"), "brain_only_featdec": ("brain_only", "lam"), "brain_decoded_distill": ("brain_decoded", "alpha")}  # G9. 0 후보는 앞 조건의 학습이다


@dataclass(frozen=True)
class Spec:
    """학습 규칙. G13의 값이고 시험에서만 줄인다."""
    batch: int = BATCH
    max_epochs: int = MAX_EPOCHS
    patience: int = PATIENCE
    seeds: tuple = SEEDS


@dataclass(frozen=True)
class Config:
    """실행 설정. k_candidates는 S7에서 정한다(5-5). 값이 없으면 실제 실행을 시작하지 않는다.
    lr_follows_brain_only: S7의 실행 시간이 예산을 넘을 때만 켠다(G13). 나머지 조건이 Brain → Emotion에서 고른 값을 따른다."""
    k_candidates: tuple
    learning_rates: tuple = LEARNING_RATES
    lr_follows_brain_only: bool = False
    keep_candidate_checkpoints: bool = False


def load_config(path):
    """manifests/s6의 JSON을 읽는다. 알 수 없는 키, S7 전의 빈 후보, G13 밖의 learning rate는 멈춘다."""
    raw = json.loads(Path(path).read_text())
    extra = set(raw) - {"k_candidates", "learning_rates", "lr_follows_brain_only", "keep_candidate_checkpoints", "note"}
    if extra:
        raise ValueError(f"설정에 알 수 없는 키가 있다: {sorted(extra)}")
    if not raw.get("k_candidates"):
        raise ValueError("d와 입력층 weight decay 후보(k_candidates)는 S7에서 정한다(5-5). 값이 없으면 돌리지 않는다")
    return Config(tuple((int(d), float(w)) for d, w in raw["k_candidates"]), tuple(float(x) for x in raw.get("learning_rates", LEARNING_RATES)), bool(raw.get("lr_follows_brain_only", False)), bool(raw.get("keep_candidate_checkpoints", False)))


def _cand(**kw):
    return dict(d=None, input_wd=None, lr=None, lam=None, alpha=None, rank=None, feature_wd=None) | kw


def _check_k(k_candidates):
    if not k_candidates:
        raise ValueError("d와 입력층 weight decay 후보는 S7에서 정해 주어야 한다(5-5)")
    out = []
    for d, wd in k_candidates:
        if isinstance(d, bool) or not isinstance(d, int) or d < 4 or d % 4:
            raise ValueError("d는 4의 배수여야 한다(F3)")
        if not isinstance(wd, float) or wd < 0:
            raise ValueError("입력층 weight decay가 잘못됐다")
        out.append((d, wd))
    if len(set(out)) != len(out):
        raise ValueError("후보가 겹친다")
    return out


def _check_lrs(learning_rates):
    lrs = [float(x) for x in learning_rates]
    if not lrs or len(set(lrs)) != len(lrs) or not set(lrs) <= set(LEARNING_RATES):
        raise ValueError("learning rate 후보는 G13의 값 안에서만 정할 수 있다")
    return lrs


def candidates(condition, *, k_candidates=None, base=None, decoded=None, learning_rates=LEARNING_RATES, lr_follows_brain_only=False):
    """G9와 G13의 후보. base는 그 fold의 brain_only에서 고른 값, decoded는 brain_decoded에서 고른 값이다.
    0 후보는 앞 조건과 같아 새로 학습하지 않으므로 여기 없다(zero_rows). 함수 밖에서 후보를 바꿀 수 없다."""
    if condition not in CONDITIONS:
        raise ValueError(condition)
    lrs = _check_lrs(learning_rates)
    if condition == "brain_only":
        return [_cand(d=d, input_wd=wd, lr=lr) for d, wd in _check_k(k_candidates) for lr in lrs]
    if base is None:
        raise ValueError(f"{condition}: 그 fold의 brain_only 선택이 먼저 있어야 한다(5-5)")
    if lr_follows_brain_only:
        lrs = [base["lr"]]
    shared = dict(d=base["d"], input_wd=base["input_wd"])  # 5-5. 고른 값을 그 바깥 fold의 모든 내부 조건에 쓴다
    if condition in ("brain_only_distill", "control_label_smoothing", "control_stimulus_shuffle"):
        return [_cand(**shared, alpha=a, lr=lr) for a in ALPHAS for lr in lrs]
    if condition in ("brain_only_featdec", "control_feature_shuffle"):
        return [_cand(**shared, lam=x, lr=lr) for x in LAMBDAS_FEATURE for lr in lrs]
    if condition == "brain_decoded":
        return [_cand(**shared, lam=x, rank=r, lr=lr) for x in LAMBDAS_FEATURE for r in RANKS for lr in lrs]
    if condition == "brain_decoded_additive":
        return [_cand(**shared, lam=x, rank=0, lr=lr) for x in LAMBDAS_FEATURE for lr in lrs]
    if condition == "brain_decoded_distill":
        if decoded is None:
            raise ValueError("brain_decoded의 선택이 먼저 있어야 한다(G9)")
        return [_cand(**shared, lam=decoded["lam"], rank=decoded["rank"], alpha=a, lr=lr) for a in ALPHAS for lr in lrs]
    if condition in ("brain_only_repr_frozen", "brain_only_repr_trained"):
        return [_cand(**shared, lam=x, lr=lr) for x in LAMBDAS_FEATURE for lr in lrs]
    if condition == "multimodal":
        return [_cand(**shared, feature_wd=w, lr=lr) for w in MULTIMODAL_DECAYS for lr in lrs]
    raise ValueError(f"{condition}: 후보를 고르지 않는 조건이다(O31)")


def check_candidate(condition, cand):
    """학습 직전 마지막 확인. 후보표 밖의 값이면 멈춘다. α = 0과 λ = 0은 새로 학습하지 않는다."""
    cfg = CONDITIONS[condition]
    if cand["lr"] not in LEARNING_RATES:
        raise ValueError("learning rate가 G13의 후보 밖이다")
    wants_alpha = cfg.target != "human"
    if wants_alpha != (cand["alpha"] is not None) or (wants_alpha and cand["alpha"] not in ALPHAS):
        raise ValueError(f"{condition}: α가 G9와 다르다")
    wants_lam = cfg.features != "none" or bool(cfg.representation)
    if wants_lam != (cand["lam"] is not None) or (wants_lam and cand["lam"] not in LAMBDAS_FEATURE):
        raise ValueError(f"{condition}: λ가 G9와 다르다")
    if cfg.decoded != (cand["rank"] is not None):
        raise ValueError(f"{condition}: rank가 구조와 다르다")
    if cfg.decoded and (cand["rank"] not in (0,) + tuple(RANKS) or (cfg.additive and cand["rank"] != 0) or (not cfg.additive and cand["rank"] == 0)):
        raise ValueError(f"{condition}: rank가 G9와 다르다")
    if cfg.multimodal != (cand["feature_wd"] is not None) or (cfg.multimodal and cand["feature_wd"] not in MULTIMODAL_DECAYS):
        raise ValueError(f"{condition}: 특징 선형층 weight decay가 O5와 다르다")


def planned_runs(k, n_lr=3, n_seeds=3):
    """한 fold의 학습 횟수(7-L의 식). 시험에서 후보 함수의 결과와 대조한다."""
    extra = n_seeds - 1
    return dict(brain_only=k * n_lr + extra, brain_only_featdec=2 * n_lr + extra, brain_decoded=8 * n_lr + extra, brain_decoded_additive=2 * n_lr + extra, brain_only_distill=2 * n_lr + extra, brain_decoded_distill=2 * n_lr + extra, control_label_smoothing=2 * n_lr + extra, control_stimulus_shuffle=2 * n_lr + extra, control_feature_shuffle=2 * n_lr + extra, multimodal=3 * n_lr + extra, brain_only_repr_frozen=2 * n_lr + extra, brain_only_repr_trained=2 * n_lr + extra, brain_only_pool=n_seeds, brain_decoded_pool=n_seeds)


def candidate_id(cand):
    return hashlib.sha256(json.dumps(cand, sort_keys=True).encode()).hexdigest()[:12]


def _key(row):
    none = -1.0
    return tuple(none if row.get(x) is None else float(row[x]) for x in ("d", "lam", "alpha", "rank", "input_wd", "feature_wd", "lr"))


def select_best(rows):
    """O6. rows: 후보 값과 val_score. 시험 fold 값은 받지 않는다. 0 후보(앞 조건)는 함께 넘긴다."""
    if not rows:
        raise ValueError("후보가 없다")
    for row in rows:
        if any(str(k).startswith("test") for k in row):
            raise ValueError("선택에 시험 fold 값을 쓰지 않는다(H5)")
        if not np.isfinite(row["val_score"]):
            raise ValueError("유효한 선택 점수가 없다. 첫 후보로 넘어가지 않고 멈춘다")
    best = max(row["val_score"] for row in rows)
    return min((r for r in rows if r["val_score"] == best), key=_key)


def zero_rows(condition, source_rows, source_selected):
    """G9. α = 0, λ = 0 후보를 앞 조건의 학습 결과로 채운다. 같은 d, 입력층 weight decay와 (조건 5는) λ, r인 행만 쓴다."""
    if condition not in ZERO_SOURCE:
        return []
    source, name = ZERO_SOURCE[condition]
    fixed = ("d", "input_wd", "lam", "rank") if condition == "brain_decoded_distill" else ("d", "input_wd")
    out = []
    for row in source_rows:
        if all(row[k] == source_selected[k] for k in fixed):
            out.append(dict(row) | {name: 0.0, "source_condition": source, "source_id": row["candidate_id"]})
    if not out:
        raise ValueError(f"{condition}: 0 후보로 쓸 앞 조건의 행이 없다")
    return out


def validation_score(p, y, participants):
    """O6, 0-2. 참가자마다 정서별 r을 내고 34개 정서와 참가자에 걸쳐 평균한다."""
    p, y = np.asarray(p, np.float64), np.asarray(y, np.float64)
    if not np.isfinite(p).all():
        raise ValueError("예측에 NaN 또는 Inf가 있다. 상수 예측이 아니라 계산 실패다")
    values = []
    participants = np.asarray(participants)
    for pid in sorted(set(participants.tolist())):
        rows = participants == pid
        yp, pp = y[rows], p[rows]
        keep = yp.max(0) > yp.min(0)
        if not keep.any():
            raise ValueError(f"{pid}: 검증 자료의 정답이 모두 상수라 선택 점수를 낼 수 없다")
        a, b = yp[:, keep] - yp[:, keep].mean(0), pp[:, keep] - pp[:, keep].mean(0)
        den = np.sqrt((a**2).sum(0) * (b**2).sum(0))
        r = np.divide((a * b).sum(0), den, out=np.zeros_like(den), where=den > 0)
        values.append(r.mean())
    return float(np.mean(values))


def mc_video_ids(table=None):
    """MC 최종 시험 72개와 그 중복 영상의 번호(0-2, B2). 어느 개발 단계에도 들어가면 안 된다."""
    table = pd.read_csv(d5.MC72, sep="\t") if table is None else table
    return sorted({int(x) for row in table.same_content_videos for x in str(row).split(",")})


@dataclass
class Plan:
    """영상 단위 분할. train은 가중치 학습, val은 선택과 조기 종료, test는 평가다."""
    name: str
    outer_fold: int
    train: list
    val: list
    test: list


def plan_outer(split, k):
    """H2. 바깥 fold k가 시험, 다음 fold가 검증, 나머지 4개가 학습이다(c.roles)."""
    r = c.roles(k)
    return Plan(f"outer_fold{k}", k, split.video_id[split.fold.isin(r["train"])].tolist(), split.video_id[split.fold == r["val"]].tolist(), split.video_id[split.fold == k].tolist())


def plan_pilot(split, k):
    """S7(N34). 시험 영상의 뇌 반응도 메모리에 올리지 않는다."""
    p = plan_outer(split, k)
    return Plan(f"pilot_fold{k}", k, p.train, p.val, [])


def plan_zone(split, block, k, kind, blocks=None, control=None):
    """4-3의 표. 학습 자료를 H2로 나눈다."""
    train_val, test = c.zone_sets(split, block, k, kind, blocks, control)
    fold_of = dict(zip(split.video_id, split.fold))
    r = c.roles(k)
    return Plan(f"zone_block{block}_fold{k}_{kind}", k, [v for v in train_val if fold_of[v] in r["train"]], [v for v in train_val if fold_of[v] == r["val"]], test)


def plan_final(split):
    """6-3의 HK 최종 모델(O7). 시험이 없다."""
    r = c.final_roles()
    return Plan("final_for_mc", 0, split.video_id[split.fold.isin(r["train"])].tolist(), split.video_id[split.fold == r["val"]].tolist(), [])


def parse_plan(name, split):
    if name.startswith("outer_fold"):
        return plan_outer(split, int(name[len("outer_fold"):]))
    if name.startswith("pilot_fold"):
        return plan_pilot(split, int(name[len("pilot_fold"):]))
    if name == "final_for_mc":
        return plan_final(split)
    if name.startswith("zone_block"):
        block, fold, kind = name[len("zone_block"):].split("_")
        return plan_zone(split, int(block), int(fold[len("fold"):]), kind)
    raise SystemExit(f"알 수 없는 분할: {name}")


def check_plan(plan, split, mc_ids=None):
    sets = [set(plan.train), set(plan.val), set(plan.test)]
    if sets[0] & sets[1] or sets[0] & sets[2] or sets[1] & sets[2]:
        raise ValueError("학습, 검증, 시험 영상이 겹친다")
    if not sets[0] or not sets[1]:
        raise ValueError("학습 또는 검증 영상이 없다")
    every = sets[0] | sets[1] | sets[2]
    c.check_dev(sorted(every), split)
    if every & set(mc_video_ids() if mc_ids is None else mc_ids):
        raise ValueError("MC 최종 시험 72개와 그 중복 영상은 HK 개발에 쓰지 않는다(0-2)")


def check_conditions(plan_name, conditions):
    for name in conditions:
        if name not in CONDITIONS:
            raise SystemExit(f"알 수 없는 조건: {name}")
        if not plan_name.startswith(("outer_fold", "pilot_fold")) and name not in ZONE_CONDITIONS:
            raise SystemExit(f"{name}: 기본 run 분할에서만 돌리는 조건이다(G6, G16, O31)")


@dataclass
class FoldData:
    """한 실행의 자료. 행은 참가자 한 명의 영상 하나다(G15). 텐서는 device에 둔다."""
    plan: Plan
    participants: list
    x: dict  # 참가자 -> 표준화한 행 × 고유 voxel
    columns: dict  # 참가자 -> ROI 순서로 이어 붙인 고유 voxel 위치
    voxel_counts: dict
    voxel_stats: dict  # 참가자 -> 평균, 표준편차(학습 행)
    row_participant: np.ndarray
    row_local: np.ndarray
    row_video: np.ndarray
    row_role: np.ndarray  # 0 학습, 1 검증, 2 시험
    bank_ids: list  # 정답과 feature가 있는 영상(학습과 검증)
    row_bank: np.ndarray  # 행 -> bank 위치. 시험 행은 -1이다
    y_bank: torch.Tensor  # 사람 평정. 학습과 검증 영상만 있다
    vision_bank: torch.Tensor  # D9로 표준화한 목표
    caption_bank: torch.Tensor
    feature_stats: dict
    y_train_mean: torch.Tensor  # G11. 학습 행의 평균
    t_bank: torch.Tensor = None  # Stimulus 예측 평정. 학습 영상 밖은 NaN이다
    device: str = "cpu"
    test_vision: torch.Tensor = None  # Multimodal Model의 참고 성능에만 쓴다(G16)
    test_caption: torch.Tensor = None
    test_ids: list = field(default_factory=list)
    _donor_cache: dict = field(default_factory=dict)

    def rows(self, role):
        return np.flatnonzero(self.row_role == {"train": 0, "val": 1, "test": 2}[role])

    def participant_names(self, rows):
        return np.array(self.participants)[self.row_participant[rows]]

    def batch(self, rows):
        """뇌 입력만 담은 묶음을 만든다. 정답과 feature는 들어가지 않는다."""
        xs, positions = {}, {}
        for i, pid in enumerate(self.participants):
            at = np.flatnonzero(self.row_participant[rows] == i)
            if len(at):
                local = torch.as_tensor(self.row_local[rows[at]], device=self.device)
                xs[pid] = self.x[pid].index_select(0, local).index_select(1, self.columns[pid])
                positions[pid] = torch.as_tensor(at, device=self.device)
        return M.BrainBatch(xs, positions, len(rows))

    def _bank_index(self, rows):
        index = self.row_bank[rows]
        if (index < 0).any():
            raise ValueError("시험 행의 정답과 feature는 이 경로로 꺼낼 수 없다(H5)")
        return torch.as_tensor(index, device=self.device)

    def y(self, rows):
        """실제 사람 평정. 학습과 검증 행만 있다."""
        return self.y_bank[self._bank_index(rows)]

    def feature_targets(self, rows):
        """실제 Vision feature와 Caption feature(D9). 학습과 검증 행만 있다."""
        index = self._bank_index(rows)
        return self.vision_bank[index], self.caption_bank[index]

    def _check_train(self, rows):
        if (self.row_role[rows] != 0).any():
            raise ValueError("학습 목표는 학습 행에만 만든다. 검증과 시험 행은 섞은 목표나 Stimulus 예측 평정을 받지 않는다")

    def donor_index(self, shuffle):
        """O1의 순열을 bank 위치로 옮긴다. 학습 영상 밖은 자기 위치 그대로다."""
        key = (shuffle.outer_fold, shuffle.seed)
        if key not in self._donor_cache:
            pos = {v: i for i, v in enumerate(self.bank_ids)}
            mapping = dict(shuffle.mapping)
            if set(mapping) != set(self.plan.train):
                raise ValueError("순열이 학습 영상과 다르다(O1)")
            index = np.arange(len(self.bank_ids))
            for v, donor in mapping.items():
                index[pos[v]] = pos[donor]
            self._donor_cache[key] = torch.as_tensor(index, device=self.device)
        return self._donor_cache[key]

    def train_target(self, rows, kind, alpha=None, shuffle=None):
        """그 조건의 정서 학습 목표(G7, G11, G12). 학습 행에서만 만든다. 조기 종료와 선택은 이 값을 쓰지 않는다(0-2)."""
        self._check_train(rows)
        y = self.y(rows)
        if kind == "human":
            return y
        if alpha is None or not 0 < alpha < 1:
            raise ValueError("α가 필요하다")
        if kind == "mean":
            other = self.y_train_mean.expand_as(y)
        elif kind in ("stimulus", "stimulus_shuffled"):
            if self.t_bank is None:
                raise ValueError("Stimulus 예측 평정이 준비되지 않았다")
            index = self._bank_index(rows)
            if kind == "stimulus_shuffled":
                if shuffle is None:
                    raise ValueError("섞은 Stimulus 예측 평정에는 O1의 순열이 필요하다")
                index = self.donor_index(shuffle)[index]
            other = self.t_bank[index]
        else:
            raise ValueError(kind)
        return (1 - alpha) * y + alpha * other

    def multimodal_inputs(self, rows):
        """Multimodal Model의 입력. 시험 행은 참고 성능을 낼 때만 있다(G16). 뇌 모델의 계산에는 쓰지 않는다."""
        index = self.row_bank[rows]
        if (index >= 0).all():
            return self.feature_targets(rows)
        if (index >= 0).any():
            raise ValueError("시험 행과 다른 행을 한 묶음에 섞지 않는다")
        if self.test_vision is None:
            raise ValueError("시험 영상의 feature는 Multimodal Model의 참고 성능을 낼 때만 준비한다")
        pos = {v: i for i, v in enumerate(self.test_ids)}
        at = torch.as_tensor([pos[int(v)] for v in self.row_video[rows]], device=self.device)
        return self.test_vision[at], self.test_caption[at]


def prepare_fold(brains, split, y, vision, caption, plan, *, stimulus=None, include_test_features=False, device="cpu", mc_ids=None):
    """brains: 참가자 -> s5_common.BrainSet. y, vision, caption은 split 순서이고 원래 값이다. 실제 실행은 시험 행을 읽지 않고 NaN으로 넘긴다(s6_train.load_known).
    표준화는 학습 자료로만 한다(N3). 돌려주는 자료에는 시험 영상의 정답과(기본값에서) feature가 없다."""
    check_plan(plan, split, mc_ids)
    pos = {v: i for i, v in enumerate(split.video_id.tolist())}
    roles = {**{v: 0 for v in plan.train}, **{v: 1 for v in plan.val}, **{v: 2 for v in plan.test}}
    participants = sorted(brains)
    x, columns, counts, stats = {}, {}, {}, {}
    rp, rl, rv, rr = [], [], [], []
    for i, pid in enumerate(participants):
        b = brains[pid]
        if len(set(b.video_id.tolist())) != len(b.video_id):
            raise ValueError(f"{pid}: 한 영상의 행이 둘 이상이다")
        c.check_dev(b.video_id, split)
        role = np.array([roles.get(int(v), -1) for v in b.video_id])
        train_rows = np.flatnonzero(role == 0)
        if not len(train_rows):
            raise ValueError(f"{pid}: 학습 행이 없다")
        used = np.flatnonzero(role >= 0)  # 시험도 학습도 검증도 아닌 행(빠진 구역 등)은 메모리에 올리지 않는다
        m, s = c.fit_standardizer(np.asarray(b.X[train_rows]))  # C5, N3. 학습 행만
        x[pid] = torch.as_tensor(((np.asarray(b.X[used], np.float64) - m) / s).astype(np.float32), device=device)
        columns[pid] = torch.as_tensor(np.concatenate(b.roi_positions), dtype=torch.long, device=device)
        counts[pid] = [len(p) for p in b.roi_positions]
        stats[pid] = dict(mean=m, std=s)
        rp.append(np.full(len(used), i)), rl.append(np.arange(len(used))), rv.append(b.video_id[used]), rr.append(role[used])
    row_video, row_role = np.concatenate(rv), np.concatenate(rr)
    known = list(plan.train) + list(plan.val)
    at, train_at = [pos[v] for v in known], [pos[v] for v in plan.train]
    vm, vs = c.fit_standardizer(np.asarray(vision)[train_at])  # D9, N3. 학습 영상만
    cm, cs = c.fit_standardizer(np.asarray(caption)[train_at])
    as_t = lambda a: torch.as_tensor(c.finite(np.asarray(a, np.float32), "학습 또는 검증 자료"), device=device)
    y_arr = c.finite(np.asarray(y, np.float32)[at], "사람 평정")
    bank_pos = {v: i for i, v in enumerate(known)}
    row_bank = np.array([bank_pos.get(int(v), -1) for v in row_video])
    train_mean = y_arr[row_bank[row_role == 0]].mean(0)  # G11. 학습 행의 평균
    t_bank = None
    if stimulus is not None:
        t_bank = torch.as_tensor(stimulus_bank(stimulus, plan.train, bank_pos, y_arr.shape), device=device)  # 학습 영상 밖은 NaN이다. 잘못 쓰면 손실이 NaN이 되어 멈춘다
    fd = FoldData(plan, participants, x, columns, counts, stats, np.concatenate(rp), np.concatenate(rl), row_video, row_role, known, row_bank, as_t(y_arr), as_t((np.asarray(vision)[at] - vm) / vs), as_t((np.asarray(caption)[at] - cm) / cs), dict(visual_mean=vm, visual_std=vs, caption_mean=cm, caption_std=cs), as_t(train_mean), t_bank, device)
    if include_test_features and plan.test:
        te = [pos[v] for v in plan.test]
        fd.test_vision, fd.test_caption = as_t((np.asarray(vision)[te] - vm) / vs), as_t((np.asarray(caption)[te] - cm) / cs)
        fd.test_ids = [int(v) for v in plan.test]
    return fd


def stimulus_bank(stimulus, train_ids, bank_pos, shape):
    """S4의 Stimulus 예측 평정을 학습 영상 자리에 붙인다(E4). 영상 ID와 배열 크기가 정확히 맞아야 한다. 한 열이나 한 행이 여러 정서나 영상으로 복제되지 않게 막는다."""
    ids = np.asarray(stimulus["video_id"])
    if ids.ndim != 1 or not np.issubdtype(ids.dtype, np.integer) or len(set(ids.tolist())) != len(ids):
        raise ValueError("Stimulus 예측 평정의 영상 ID가 1차원 정수가 아니거나 중복이 있다")
    if sorted(ids.tolist()) != sorted(int(v) for v in train_ids):
        raise ValueError("Stimulus 예측 평정은 학습 영상에만 붙어야 한다(E4)")
    values = c.finite(np.asarray(stimulus["p_clipped"], np.float32), "Stimulus 예측 평정")
    if values.shape != (len(ids), shape[1]):
        raise ValueError(f"Stimulus 예측 평정의 크기 {values.shape}가 (영상 {len(ids)}, 정서 {shape[1]})와 다르다")
    if ((values < 0) | (values > 1)).any():
        raise ValueError("Stimulus 예측 평정이 0~1을 벗어났다")
    out = np.full(shape, np.nan, np.float32)
    out[[bank_pos[int(v)] for v in ids]] = values
    return out


def check_stimulus_source(done_path, k, current_hashes):
    """S4가 이 Stimulus 예측 평정을 지금과 같은 입력으로 만들었는지 본다(E4, M1). S4의 완료 기록이 없거나, 과제와 바깥 fold가 다르거나,
    S4가 쓴 입력(Vision feature, Caption feature, 사람 평정, S2 표) 가운데 하나라도 지금 내용과 다르면 학습 전에 멈춘다. 돌려주는 값은 S4 실행 번호다."""
    p = Path(done_path)
    if not p.exists():
        raise SystemExit(f"{p}: S4 완료 기록이 없다. 출처를 확인할 수 없는 Stimulus 예측 평정은 쓰지 않는다")
    d = json.loads(p.read_text())
    task = d.get("task", {})
    if task.get("task") != "stimulus" or int(task.get("k", -1)) != int(k):
        raise SystemExit(f"{p}: S4 과제나 바깥 fold가 다르다({task})")
    for role, h in d.get("inputs", {}).items():
        if role not in current_hashes:
            raise SystemExit(f"{p}: S4 입력 {role}을 지금 실행에서 확인할 수 없다")
        if current_hashes[role] != h:
            raise SystemExit(f"{p}: S4 입력 {role}의 내용이 지금과 다르다. S4를 다시 돌려야 한다")
    if "run_key" not in d:
        raise SystemExit(f"{p}: S4 실행 번호가 없다")
    return d["run_key"]


def shuffle_plan(split, plan, seed, mc_ids=None):
    """O1. 학습 영상 안의 영상 단위 순열 하나. 바깥 fold와 seed만으로 정해져 후보가 달라도 같다. audition_codex의 함수를 그대로 쓴다."""
    if not plan.name.startswith(("outer_fold", "pilot_fold")):
        raise ValueError("대조군은 기본 run 분할에서만 돌린다(G6)")
    s = ac.make_scene_pair_shuffle(dict(zip(split.video_id.tolist(), split.fold.tolist())), outer_fold=plan.outer_fold, seed=seed, mc_test_ids=mc_video_ids() if mc_ids is None else mc_ids)
    if set(dict(s.mapping)) != set(plan.train):
        raise ValueError("순열이 학습 영상과 다르다(O1)")
    return s


def build_model(condition, cand, voxel_counts):
    """조건의 구조를 만든다. 구조는 조건 이름으로만 정해지고 부르는 쪽이 바꿀 수 없다."""
    cfg = CONDITIONS[condition]
    if cfg.multimodal:
        return M.MultimodalModel(voxel_counts, cand["d"])
    return M.BrainModel(voxel_counts, cand["d"], feature_head=cfg.feature_head, decoded=cfg.decoded, rank=cand["rank"] if cfg.decoded else None, pooling=cfg.pooling)


def to_k1_head(v_hat, c_hat, feature_stats, coordinates):
    """N3. 뇌 모델이 학습 fold 4개의 눈금으로 낸 decoded features를 원래 척도로 되돌린 뒤 K1 head의 D_k 눈금으로 바꾼다.
    coordinates: S4 stimulus 결과의 coordinates.npz. S9의 K1이 이 함수를 쓴다."""
    for name in ("visual_std", "caption_std"):
        if (np.asarray(feature_stats[name]) <= 0).any() or (np.asarray(coordinates[name]) <= 0).any():
            raise ValueError("표준편차가 0 이하인 차원이 있다")
    v = M.to_head_scale(np.asarray(v_hat, np.float64), feature_stats["visual_mean"], feature_stats["visual_std"], coordinates["visual_mean"], coordinates["visual_std"])
    cap = M.to_head_scale(np.asarray(c_hat, np.float64), feature_stats["caption_mean"], feature_stats["caption_std"], coordinates["caption_mean"], coordinates["caption_std"])
    return c.finite(v, "K1 눈금의 v̂"), c.finite(cap, "K1 눈금의 ĉ")


def load_brain_subset(s, split, keep_ids, raw_path=None, roi_file=None, table=None, crosswalk=None, mc72=None, raw=None):
    """d5.load_brain과 같지만, 원본 배열을 인덱싱하기 전에 이번 실행에 쓰는 영상(keep_ids)의 행으로 줄인다.
    파일럿처럼 시험 fold를 쓰지 않는 실행은 시험 영상의 뇌 반응을 아예 읽지 않는다(N34). 허용 행 검사와 MC 검사는 d5의 함수를 그대로 쓴다."""
    t = d5.allowed_rows(s, table, crosswalk, mc72)  # 표 전체로 MC와 행 번호를 검사한다
    c.check_dev(t.video_id.to_numpy(), split)
    keep = set(int(v) for v in keep_ids)
    t = t[t.video_id.isin(keep)].reset_index(drop=True)
    if not t.video_id.is_unique:
        raise ValueError("한 영상의 block이 둘 이상이다")
    z = np.load(d5.roi_path(s) if roi_file is None else roi_file)
    columns, offsets = z["columns"], z["offsets"]
    unique = np.unique(columns)
    raw = np.load(d5.response_path(s) if raw_path is None else raw_path, mmap_mode="r") if raw is None else raw
    if raw.shape[1] != int(z["n_columns"]):
        raise ValueError("반응 배열의 열 수가 ROI 표와 다르다")
    rows = t.qc_row.to_numpy()
    X = np.empty((len(rows), len(unique)), np.float32)
    for i in range(0, len(rows), 64):
        X[i:i + 64] = d5.read_rows(raw, rows[i:i + 64], rows)[:, unique]
    c.finite(X, f"sub-{s} 반응")
    fold_of = dict(zip(split.video_id, split.fold))
    pos = [np.searchsorted(unique, columns[offsets[i]:offsets[i + 1]]) for i in range(len(offsets) - 1)]
    return d5.BrainSet(f"sub-{s}", X, t.video_id.to_numpy(), np.array([fold_of[v] for v in t.video_id]), pos, len(columns))


def load_brains(split, keep_ids, participants=d5.HK, **kw):
    """뇌 반응은 허용 행 가운데 이번 실행에 쓰는 영상의 행만 읽는다. e(r)이 참가자 공통이므로 ROI 순서가 같은지 ROI 표로 확인한다."""
    order = None
    out = {}
    for s in participants:
        roi_file = kw.get("roi_file") or d5.roi_path(s)
        with np.load(roi_file) as z:
            names = z["roi"].tolist() if "roi" in z.files else None
        if order is not None and names != order:
            raise ValueError(f"sub-{s}: ROI 순서가 다른 참가자와 다르다")
        order = names
        b = load_brain_subset(s, split, keep_ids, **kw)
        out[b.participant] = b
    return out


def stimulus_path(k):
    """S4의 nested OOF(E4). 그 fold의 H2 학습 영상에만 있다."""
    return c.OUT / "stimulus" / f"fold{k}" / "oof.npz"


def input_paths(plan, participants=d5.HK):
    """역할 -> 파일. 읽기 전에 해시를 낸다."""
    paths = {"visual_target": c.FEATURES / f"{c.VISUAL_TARGET}.npy", "caption_target": c.FEATURES / f"{c.CAPTION_TARGET}.npy", "labels": c.LABELS}
    for s in participants:
        paths[f"response:sub-{s}"], paths[f"roi:sub-{s}"] = d5.response_path(s), d5.roi_path(s)
    if plan.name.startswith(("outer_fold", "pilot_fold")):
        paths["stimulus_oof"] = stimulus_path(plan.outer_fold)
        paths["stimulus_done"] = stimulus_path(plan.outer_fold).parent / "done.json"
    return paths


class Run:
    """s5_common.Run과 같은 뜻이고 S6 코드와 audition_codex까지 해시한다."""

    def __init__(self, design_freeze, inputs, **settings):
        tables = list(d5.S2_TABLES)
        self.paths = {**{f"s2:{p.name}": Path(p) for p in tables}, **{k: Path(p) for k, p in inputs.items()}}
        self.hashes = {k: c.sha256(p) for k, p in self.paths.items()}
        self.prov = dict(code_commit=c.START_HEAD, code_dirty=c.START_DIRTY, code_sha256=START_CODE, design_freeze=design_freeze, inputs=self.hashes, input_paths={k: str(p) for k, p in self.paths.items()}, settings=settings)
        self._check_code()
        key = json.dumps(dict(code=START_CODE, inputs=self.hashes, settings=settings, design_freeze=design_freeze), sort_keys=True, default=str)
        self.prov["run_key"] = hashlib.sha256(key.encode()).hexdigest()

    def _check_code(self):
        now = {f.name: c.sha256(f) for f in sorted(c.CODE_DIR.glob("s[456]_*.py"))}
        now[AUDITION_PATH.name] = c.sha256(AUDITION_PATH)
        if now != START_CODE:
            raise SystemExit("시작 뒤 코드가 바뀌었다.")

    def check(self):
        self._check_code()
        for k, p in self.paths.items():
            if c.sha256(p) != self.hashes[k]:
                raise SystemExit(f"시작 뒤 입력이 바뀌었다: {k} ({p})")

    @property
    def key(self):
        return self.prov["run_key"]
