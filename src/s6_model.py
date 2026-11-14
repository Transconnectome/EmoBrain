#!/usr/bin/env python3
"""S6 뇌 모델의 구조 (04 S6, 01 5-A, 5-4, 5-5, C4, F3~F8, G8, G13, G16, O5, O26, 2026-11-07).

- 입력층 t(s, r) = W(s, r) x(s, r) + b(s, r) + e(r). W, b는 참가자와 ROI마다 따로 두고 e(r)만 참가자 공통이다.
- encoder: self-attention block 1개, pre-LN, head 4, FFN d → 2d → d(GELU), dropout 0.1, 마지막 LayerNorm(F3, O26).
- emotion query 34개와 feature query 2개는 docs/final/reference/audition_codex.py의 QueryReadout, FeatureHead를 그대로 쓴다(O26).
- 중심 모델의 Emotion: z = g(H) + a(v̂) + b(ĉ) + U[(Av̂) ⊙ (Bĉ)]. v̂, ĉ는 들어가기 전에 stop-gradient한다(G8).
- BrainModel.forward의 입력은 BrainBatch 하나뿐이다. 실제 Vision feature와 Caption feature가 들어갈 자리가 없다.
- MultimodalModel은 E-고정, E-학습이 쓰는 별도 모델이다. Brain, Vision, Caption을 받는다(O5). 시험 입력이 Brain뿐인 비교에는 들어가지 않는다.

weight decay 묶음(G13)은 parameter_group_name이 이름으로 정한다. 묶음을 정할 수 없는 파라미터가 있으면 멈춘다.

문서가 정하지 않은 초기값(구현 선택, 실행 기록에 남긴다)
- W, b: nn.Linear의 기본 초기값과 같은 범위(ROI마다 ±1 / sqrt(그 ROI의 voxel 수)).
- e(r): audition_codex의 query와 같은 규칙(정규분포, 표준편차 d^-0.5).
"""
import hashlib
import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from torch import Tensor, nn
import paths as P

AUDITION_PATH = P.REFERENCE / "audition_codex.py"


def _load_audition():
    name = "audition_codex"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, AUDITION_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclass가 자기 모듈을 찾으려면 먼저 등록해야 한다
    spec.loader.exec_module(module)
    return module


ac = _load_audition()
VISUAL_DIM, CAPTION_DIM, N_EMOTIONS = ac.VISUAL_DIM, ac.CAPTION_DIM, ac.N_EMOTIONS
OTHER_WEIGHT_DECAY = 0.01  # G13. 입력층 weight와 Multimodal 특징 선형층의 weight 밖의 weight, query, ROI embedding
INTERACTION_RANKS = (1, 2, 4, 8)  # 5-4


def _check_d(d):
    if isinstance(d, bool) or not isinstance(d, int) or d < 4 or d % 4:
        raise ValueError("d는 4의 배수여야 한다(F3)")


@dataclass(frozen=True)
class BrainBatch:
    """뇌 입력만 담는 묶음. xs: 참가자 -> (행 × ROI 순서로 이어 붙인 voxel 열). positions: 참가자 -> 묶음 안 위치."""
    xs: dict
    positions: dict
    n: int


@dataclass
class ModelOutput(ac.ReadoutOutput):
    o: Tensor = None  # emotion query의 출력(행 × 34 × d, O26의 LayerNorm 뒤). E-고정, E-학습의 중간 표현
    H: Tensor = None  # encoder 출력(행 × token × d)


@dataclass
class SeparateOutput(ModelOutput):
    """D-1, D-2. v_hat, c_hat은 encoder 1의 보조 feature head 출력(v̂₁, ĉ₁, 손실에만 씀)이고,
    v_used, c_used가 정서 계산에 들어간 encoder 2의 출력(v̂₂, ĉ₂)이다. 바꿔 끼우기는 v_used, c_used로 한다."""
    v_used: Tensor = None
    c_used: Tensor = None


class RoiInput(nn.Module):
    """C4. W는 참가자마다 ROI 순서로 이어 붙여 하나의 Parameter로 둔다. bounds가 ROI 경계이고, 곱은 ROI마다 따로 한다."""

    def __init__(self, voxel_counts, d, voxel_sampling=0.0):
        super().__init__()
        _check_d(d)
        if not 0.0 <= float(voxel_sampling) < 1.0:
            raise ValueError("voxel 뽑기 비율은 0 이상 1 미만이다(0이면 뽑지 않는다)")
        self.voxel_sampling = float(voxel_sampling)  # 11/12. 선형 입력층의 voxel 뽑기(Brain-IT 입력층과 같은 복원 추출). 원인 분리 점검용
        if len({len(v) for v in voxel_counts.values()}) != 1:
            raise ValueError("참가자마다 ROI 수가 같아야 한다(공통 ROI, C6)")
        self.d = d
        self.participants = sorted(voxel_counts)
        self.voxel_counts = {p: [int(x) for x in voxel_counts[p]] for p in self.participants}
        self.n_roi = len(self.voxel_counts[self.participants[0]])
        self.bounds = {}
        self.weights = nn.ParameterDict()
        self.input_bias = nn.ParameterDict()
        for pid in self.participants:
            counts = self.voxel_counts[pid]
            if min(counts) <= 0:
                raise ValueError(f"{pid}: voxel이 없는 ROI가 있다(공통 ROI가 아니다, C6)")
            bounds = [0]
            for n in counts:
                bounds.append(bounds[-1] + n)
            self.bounds[pid] = bounds
            w, b = torch.empty(bounds[-1], d), torch.empty(self.n_roi, d)
            for r, n in enumerate(counts):
                limit = n ** -0.5
                nn.init.uniform_(w[bounds[r]:bounds[r + 1]], -limit, limit)
                nn.init.uniform_(b[r], -limit, limit)
            self.weights[pid], self.input_bias[pid] = nn.Parameter(w), nn.Parameter(b)
        self.roi_embedding = nn.Parameter(torch.empty(self.n_roi, d))
        nn.init.normal_(self.roi_embedding, std=d ** -0.5)

    def sample(self, x):
        """학습 때만 voxel을 고른다. 평가 때는 모든 voxel을 쓴다.
        - 11/12(replace): Brain-IT 입력층과 같은 방식으로 예시마다 voxel을 복원 추출한다(전체의 voxel_sampling 비율만큼 뽑음). 선형 합이라
          뽑힌 횟수에 1/비율을 곱해 기댓값이 모든 voxel을 쓸 때와 같게 한다.
        - 11/14(bernoulli, 석진 님): voxel마다 voxel_sampling 확률로 빼고(0) 남은 값에 1/(1 − 확률)을 곱한다(입력 dropout, Srivastava 외 2014. 0.2면 80%를 남김)."""
        if not self.training or self.voxel_sampling <= 0:
            return x
        if getattr(self, "sampling_mode", "replace") == "bernoulli":
            keep = 1.0 - self.voxel_sampling
            return x * (torch.rand_like(x) < keep).to(x.dtype) / keep
        n_draw = max(1, round(self.voxel_sampling * x.shape[1]))
        draws = torch.randint(0, x.shape[1], (x.shape[0], n_draw), device=x.device)
        hits = torch.zeros_like(x).scatter_add_(1, draws, torch.ones_like(draws, dtype=x.dtype))
        return x * hits * (x.shape[1] / n_draw)

    def token(self, pid, x):
        """x: 행 × 그 참가자의 voxel 열. ROI token은 그 ROI의 voxel만으로 만든다(5-5). 칸 평균은 쓰지 않는다."""
        counts = self.voxel_counts[pid]
        if x.shape[1] != sum(counts):
            raise ValueError(f"{pid}: 입력 열 수가 입력층과 다르다")
        x = self.sample(x)
        # split을 쓴다. ROI마다 slice하면 역전파가 ROI마다 W 전체 크기의 텐서를 만들어 수백 배 느려진다
        out = [a @ b for a, b in zip(x.split(counts, 1), self.weights[pid].split(counts, 0))]
        return torch.stack(out, 1) + self.input_bias[pid] + self.roi_embedding

    def forward(self, batch):
        if not isinstance(batch, BrainBatch):
            raise TypeError("입력층은 BrainBatch만 받는다")
        parts, order = [], []
        for pid, x in batch.xs.items():
            parts.append(self.token(pid, x))
            order.append(batch.positions[pid])
        order = torch.cat(order)
        if sorted(order.tolist()) != list(range(batch.n)):
            raise ValueError("묶음의 행 위치가 맞지 않다")
        return torch.cat(parts)[order.argsort()]



class DenseVoxelInput(RoiInput):
    """11/14 석진 님. MindEye2 형식 입력층(Scotti 외 2024의 참가자별 선형층과 같은 형식). ROI로 묶지 않고 그 참가자의 모든 voxel 열을
    참가자별 선형층 하나로 d차원 token 하나에 보낸다. 가중치는 RoiInput과 같은 크기(열 수 × d)이고, RoiInput은 이 행렬에서 ROI 밖 가중치를 0으로 둔
    특수한 경우다. 그래서 가중치 수를 같게 둔 채 ROI 구조의 효과를 비교한다. voxel 뽑기는 RoiInput과 같다."""

    def __init__(self, voxel_counts, d, voxel_sampling=0.0):
        super().__init__(voxel_counts, d, voxel_sampling)
        self.input_bias = nn.ParameterDict({pid: nn.Parameter(b[:1].clone()) for pid, b in self.input_bias.items()})
        self.roi_embedding = nn.Parameter(self.roi_embedding[:1].detach().clone())
        for pid, counts in self.voxel_counts.items():  # 열 전체를 한 번에 받으므로 초기값 범위도 열 전체 수로 맞춘다
            limit = sum(counts) ** -0.5
            with torch.no_grad():
                self.weights[pid].uniform_(-limit, limit)
                self.input_bias[pid].uniform_(-limit, limit)

    def token(self, pid, x):
        if x.shape[1] != sum(self.voxel_counts[pid]):
            raise ValueError(f"{pid}: 입력 열 수가 입력층과 다르다")
        x = self.sample(x)
        return (x @ self.weights[pid])[:, None, :] + self.input_bias[pid] + self.roi_embedding


class BrainItRoiInput(RoiInput):
    """Brain-IT tokenizer(Beliy 외 2026, ICLR, 4절의 Brain Tokenizer와 부록 D.1)를 ROI 370개에 얹은 입력층. 11/9 석진 님 점검용이다.
    군집은 해부 ROI로 둔다(Brain-IT 부록 A.2의 해부 기반 묶음과 같은 구성). 원문과 같은 점:
    - voxel embedding e_v(참가자별, voxel마다 d차원)에 voxel 값 x_v를 곱한 m_v = x_v e_v가 key와 value다.
    - ROI embedding q_r(모든 참가자 공유)가 query다. head 1개 graph attention으로 ROI r 안의 voxel만 본다(TransformerConv, Shi 외 2021의 root 항 포함).
    - 학습 때 예시마다 voxel을 복원 추출로 뽑는다(원문은 약 4만 개 중 1.5만 개). 평가 때는 모든 voxel을 쓴다.
    계산: key가 x_v W_K e_v라 점수는 x_v s_v(s_v = (W_Q q_r)·(W_K e_v) / √d, voxel마다 숫자 하나)가 되고, key 편향은 ROI 안에서 상수라 softmax에서 빠진다.
    token_r = W_root q_r + Σ_v α_v (x_v W_V e_v) + b_V, α = softmax_v∈r(x_v s_v). 지금 RoiInput(token_r = Σ x_v w_v)에 입력마다 달라지는 비중 α를 곱한 꼴이다.
    가중치 이름 input_layer.weights.<참가자>는 RoiInput의 W와 같은 자리(e_v)라 같은 weight decay 묶음(input_weight)에 든다.
    저자 공개 코드(github.com/WeizmannVision/brainit-fmri, models/decoder_models.py의 Decoder, 11/9 대조)와 맞춘 것: 모은 token에 ReLU와 LayerNorm을 거치고,
    voxel embedding과 군집 embedding의 초기값은 0.1 / (2√d) × N(0, 1)이다. 계산은 PyG TransformerConv(head 1개, root 항, 편향 있음)와 같다."""

    def __init__(self, voxel_counts, d, voxel_sampling=0.0):
        super().__init__(voxel_counts, d)
        if not 0.0 <= float(voxel_sampling) < 1.0:
            raise ValueError("voxel 뽑기 비율은 0 이상 1 미만이다(0이면 뽑지 않는다)")
        self.voxel_sampling = float(voxel_sampling)
        del self.input_bias, self.roi_embedding  # Brain-IT에는 없다. ROI의 구분은 query q_r과 root 항이 맡는다
        scale = 0.1 / (2 * d ** 0.5)  # 저자 코드의 초기값
        for pid in self.participants:
            nn.init.normal_(self.weights[pid], std=scale)
        self.cluster_embedding = nn.Parameter(torch.empty(self.n_roi, d))
        nn.init.normal_(self.cluster_embedding, std=scale)
        self.query, self.key, self.value, self.root = (nn.Linear(d, d) for _ in range(4))
        self.norm = nn.LayerNorm(d)  # 저자 코드: ReLU 뒤 LayerNorm
        self.roi_index = {pid: torch.repeat_interleave(torch.arange(self.n_roi), torch.tensor(self.voxel_counts[pid])) for pid in self.participants}

    def token(self, pid, x):
        counts = self.voxel_counts[pid]
        if x.shape[1] != sum(counts):
            raise ValueError(f"{pid}: 입력 열 수가 입력층과 다르다")
        e = self.weights[pid]
        q = self.query(self.cluster_embedding)  # ROI × d
        s = (q[self.roi_index[pid].to(x.device)] * (e @ self.key.weight.T)).sum(1) / self.d ** 0.5  # voxel마다 숫자 하나. key 편향은 x_v에 곱해지지 않아 softmax에서 빠진다
        logit = x * s
        hits = None
        if self.training and self.voxel_sampling > 0:
            n_draw = max(1, round(self.voxel_sampling * x.shape[1]))
            draws = torch.randint(0, x.shape[1], (x.shape[0], n_draw), device=x.device)
            hits = torch.zeros_like(x).scatter_add_(1, draws, torch.ones_like(draws, dtype=x.dtype))
            logit = torch.where(hits > 0, logit + hits.clamp_min(1).log(), torch.full_like(logit, float("-inf")))  # 같은 voxel이 여러 번 뽑히면 그만큼 비중이 커진다
        u = e @ self.value.weight.T  # voxel마다 W_V e_v
        out = []
        hit_parts = hits.split(counts, 1) if hits is not None else [None] * len(counts)
        for lg, xv, uv, hv in zip(logit.split(counts, 1), x.split(counts, 1), u.split(counts, 0), hit_parts):
            if hv is None:
                out.append((torch.softmax(lg, 1) * xv) @ uv)
                continue
            seen = (hv > 0).any(1, keepdim=True)  # 한 ROI의 voxel이 하나도 뽑히지 않은 예시는 root 항만 남는다
            a = torch.softmax(torch.where(seen, lg, torch.zeros_like(lg)), 1) * seen
            out.append((a * xv) @ uv)
        return self.norm(torch.relu(torch.stack(out, 1) + self.value.bias + self.root(self.cluster_embedding)))

class RoiCellInput(RoiInput):
    """11/9 입력층 점검의 ROI 평균(칸 1개)과 칸 평균(칸 8개). 같은 Horikawa 2020 자료의 선행 모델이 쓴 ROI pooling(01 5-5의 "(가)")이다.
    ROI r의 칸 c에 든 voxel 값(학습 행으로 표준화한 값)을 평균해 m(r, c)를 내고, token_r = Σ_c m(r, c) w(s, r, c) + b(s, r) + e(r)로 d차원 token을 만든다.
    w(s, r, c)는 참가자, ROI, 칸마다 d차원이다(지금 입력층의 voxel마다 d차원 대신). voxel이 없는 칸은 평균 0으로 둔다.
    칸 번호는 s2_roi_cells.py가 만든 파일에서 받고(cells), 체크포인트에서는 buffer로 되살린다."""

    def __init__(self, voxel_counts, d, n_cells, cells=None):
        super().__init__(voxel_counts, d)
        self.n_cells = int(n_cells)
        for pid in self.participants:
            w = torch.empty(self.n_roi * self.n_cells, d)
            nn.init.uniform_(w, -self.n_cells ** -0.5, self.n_cells ** -0.5)
            self.weights[pid] = nn.Parameter(w)
            given = None if cells is None else torch.as_tensor(np.asarray(cells[pid]), dtype=torch.long)
            n = sum(self.voxel_counts[pid])
            if given is not None and (given.shape != (n,) or given.min() < 0 or given.max() >= self.n_cells):
                raise ValueError(f"{pid}: 칸 번호의 길이나 범위가 입력층과 다르다")
            if given is None and self.n_cells == 1:
                given = torch.zeros(n, dtype=torch.long)
            roi = torch.repeat_interleave(torch.arange(self.n_roi), torch.tensor(self.voxel_counts[pid]))
            seg = roi * self.n_cells + (given if given is not None else torch.zeros(n, dtype=torch.long))
            self.register_buffer(self._key(pid), seg)

    @staticmethod
    def _key(pid):
        return "segment_" + pid.replace("-", "_")

    def token(self, pid, x):
        counts = self.voxel_counts[pid]
        if x.shape[1] != sum(counts):
            raise ValueError(f"{pid}: 입력 열 수가 입력층과 다르다")
        seg = getattr(self, self._key(pid))
        k = self.n_roi * self.n_cells
        total = torch.zeros(x.shape[0], k, dtype=x.dtype, device=x.device).index_add_(1, seg, x)
        n = torch.bincount(seg, minlength=k).to(x.dtype).clamp_min(1)
        m = (total / n).view(x.shape[0], self.n_roi, self.n_cells)
        w = self.weights[pid].view(self.n_roi, self.n_cells, self.d)
        return torch.einsum("brc,rcd->brd", m, w) + self.input_bias[pid] + self.roi_embedding

CELL_TOKENIZERS = {"roi_mean": 1, "roi_cells": 8}  # 11/9 입력층 점검. 칸 수


def make_input_layer(voxel_counts, d, tokenizer="linear", voxel_sampling=0.0, cells=None):
    """linear는 5-5의 입력층(본 설계). 11/9 점검용: brainit(Brain-IT tokenizer), roi_mean(ROI 평균), roi_cells(ROI 8칸 평균)."""
    if voxel_sampling and tokenizer not in ("brainit", "linear", "linear_bernoulli", "dense"):
        raise ValueError("voxel 뽑기는 brainit, linear, linear_bernoulli, dense 입력층에만 있다")
    if tokenizer == "linear":
        return RoiInput(voxel_counts, d, voxel_sampling)  # 11/12. linear의 voxel 뽑기는 원인 분리 점검용
    if tokenizer == "linear_bernoulli":  # 11/14. voxel_sampling은 voxel마다 빼는 확률
        layer = RoiInput(voxel_counts, d, voxel_sampling)
        layer.sampling_mode = "bernoulli"
        return layer
    if tokenizer == "dense":  # 11/14. MindEye2 형식, token 하나
        return DenseVoxelInput(voxel_counts, d, voxel_sampling)
    if tokenizer == "brainit":
        return BrainItRoiInput(voxel_counts, d, voxel_sampling)
    if tokenizer in CELL_TOKENIZERS:
        return RoiCellInput(voxel_counts, d, CELL_TOKENIZERS[tokenizer], cells)
    raise ValueError(f"알 수 없는 tokenizer: {tokenizer}")


class Encoder(nn.Module):
    """F3, O26."""

    def __init__(self, d):
        super().__init__()
        _check_d(d)
        self.block = nn.TransformerEncoderLayer(d, 4, 2 * d, dropout=0.1, activation="gelu", batch_first=True, norm_first=True)
        self.final_norm = nn.LayerNorm(d)

    def forward(self, tokens):
        return self.final_norm(self.block(tokens))


class Readout(nn.Module):
    """H를 받아 Emotion을 낸다. feature_head: decoded features를 내는가. decoded: 그 값을 Emotion 계산에 쓰는가.
    rank는 decoded일 때만 있고 0이 더하기 head다. pooling: F7. query끼리 self-attention은 없다(F4)."""

    def __init__(self, d, *, feature_head=False, decoded=False, rank=None, pooling=False, stop_gradient=True):
        super().__init__()
        _check_d(d)
        if not stop_gradient and not decoded:
            raise ValueError("기울기 허용판은 decoded features를 쓰는 조건에만 있다")
        if decoded and not feature_head:
            raise ValueError("decoded features를 쓰려면 feature head가 있어야 한다")
        if decoded and (isinstance(rank, bool) or rank not in (0,) + INTERACTION_RANKS):
            raise ValueError("rank는 0(더하기 head), 1, 2, 4, 8이다")
        if not decoded and rank is not None:
            raise ValueError("decoded features를 쓰지 않는 조건에는 rank가 없다")
        self.d, self.rank, self.decoded, self.pooling, self.stop_gradient = d, rank, decoded, pooling, stop_gradient
        if pooling:
            self.pool_linear = nn.Linear(d, N_EMOTIONS)
        else:
            self.emotion_query = ac.QueryReadout(d, N_EMOTIONS)
            self.emotion_linears = nn.ModuleList(nn.Linear(d, 1) for _ in range(N_EMOTIONS))
        if feature_head:
            self.feature_head = ac.FeatureHead(d)
        if decoded:
            self.a = nn.Linear(VISUAL_DIM, N_EMOTIONS, bias=True)
            self.b = nn.Linear(CAPTION_DIM, N_EMOTIONS, bias=True)
            self.A = nn.Linear(VISUAL_DIM, rank, bias=False) if rank else None
            self.B = nn.Linear(CAPTION_DIM, rank, bias=False) if rank else None
            self.U = nn.Linear(rank, N_EMOTIONS, bias=False) if rank else None

    @property
    def has_feature_head(self):
        return hasattr(self, "feature_head")

    def combine(self, g, v_hat, c_hat):
        """G8. decoded features가 들어가는 모든 자리에서 기울기를 끊는다. 값은 그대로 전달된다.
        stop_gradient=False는 성능 비교용 기울기 허용판(G8의 허용판, 11/8 석진 님)이다. 정서 손실이 feature head와 encoder로 흐른다."""
        if not self.decoded:
            raise ValueError("이 조건은 decoded features를 Emotion 계산에 쓰지 않는다")
        ac._tensor(g, "g", (None, N_EMOTIONS))
        ac._tensor(v_hat, "v_hat", (g.shape[0], VISUAL_DIM))
        ac._tensor(c_hat, "c_hat", (g.shape[0], CAPTION_DIM))
        ac._same_coordinates(g, v_hat, c_hat)
        v, c = (v_hat.detach(), c_hat.detach()) if self.stop_gradient else (v_hat, c_hat)
        z = g + self.a(v) + self.b(c)
        if self.rank:
            z = z + self.U(self.A(v) * self.B(c))
        return z

    def forward(self, H):
        ac._tensor(H, "H", (None, None, self.d))
        if self.pooling:
            o, emotion_attention = None, None
            g = self.pool_linear(H.mean(1))
        else:
            o, emotion_attention = self.emotion_query(H)
            g = torch.cat([layer(o[:, e]) for e, layer in enumerate(self.emotion_linears)], dim=-1)
        v_hat, c_hat, feature_attention = None, None, None
        if self.has_feature_head:
            v_hat, c_hat, feature_attention = self.feature_head(H)
        z = self.combine(g, v_hat, c_hat) if self.decoded else g
        return ModelOutput(z, z.sigmoid(), g, v_hat, c_hat, emotion_attention, feature_attention, o, H)


class AuditionReadout(Readout):
    """audition_codex의 검증 함수를 이 구현에 그대로 돌리기 위한 얇은 생성자."""

    def __init__(self, d, rank):
        super().__init__(d, feature_head=True, decoded=True, rank=rank)


class BrainModel(nn.Module):
    """시험 입력이 Brain뿐인 모델(01 5-A의 A~C, E 묶음, 대조군, 평균 pooling판)."""

    def __init__(self, voxel_counts, d, *, feature_head=False, decoded=False, rank=None, pooling=False, stop_gradient=True, tokenizer="linear", voxel_sampling=0.0, cells=None):
        super().__init__()
        self.spec = dict(kind="brain", voxel_counts=voxel_counts, d=d, feature_head=feature_head, decoded=decoded, rank=rank, pooling=pooling, stop_gradient=stop_gradient, tokenizer=tokenizer, voxel_sampling=voxel_sampling)
        self.input_layer = make_input_layer(voxel_counts, d, tokenizer, voxel_sampling, cells)  # cells는 spec에 넣지 않는다. 체크포인트는 buffer로 되살린다
        self.encoder = Encoder(d)
        self.readout = Readout(d, feature_head=feature_head, decoded=decoded, rank=rank, pooling=pooling, stop_gradient=stop_gradient)

    def encode(self, brain):
        return self.encoder(self.input_layer(brain))

    def forward(self, brain):
        return self.readout(self.encode(brain))

    def load_head_from(self, source, *, frozen):
        """E-고정, E-학습. Multimodal Model의 정서별 선형층만 값으로 복사한다. 원본과 값을 공유하지 않는다.
        frozen이면 가중치를 고정한다. 기울기는 고정한 head를 통과해 encoder까지 간다(5-A)."""
        r = self.readout
        if r.pooling or r.decoded or r.has_feature_head:
            raise ValueError("E-고정, E-학습의 뇌 모델은 Brain → Emotion과 같은 구조여야 한다(O5)")
        if r.d != source.spec["d"]:
            raise ValueError("연결층이 없으므로 d가 같아야 한다(O5)")
        with torch.no_grad():
            for mine, theirs in zip(r.emotion_linears, source.emotion_linears):
                mine.weight.copy_(theirs.weight)
                mine.bias.copy_(theirs.bias)
        for p in r.emotion_linears.parameters():
            p.requires_grad_(not frozen)
        return self


class MultimodalModel(nn.Module):
    """E-고정, E-학습의 준비 모델(O5, 논문의 Multimodal Model). 뇌 모델과 같은 입력층, encoder, emotion query에 Vision, Caption token을 더한다.
    중간 표현은 emotion query 34개의 출력이고, head는 정서별 선형층이다."""

    def __init__(self, voxel_counts, d, tokenizer="linear", voxel_sampling=0.0):
        super().__init__()
        self.spec = dict(kind="multimodal", voxel_counts=voxel_counts, d=d, tokenizer=tokenizer, voxel_sampling=voxel_sampling)
        self.input_layer = make_input_layer(voxel_counts, d, tokenizer, voxel_sampling)  # 11/10. 뇌 모델과 같은 입력층(선형 또는 Brain-IT)
        self.vision_token = nn.Linear(VISUAL_DIM, d)
        self.caption_token = nn.Linear(CAPTION_DIM, d)
        self.encoder = Encoder(d)
        self.emotion_query = ac.QueryReadout(d, N_EMOTIONS)
        self.emotion_linears = nn.ModuleList(nn.Linear(d, 1) for _ in range(N_EMOTIONS))

    def forward(self, brain, vision, caption):
        tokens = self.input_layer(brain)
        ac._tensor(vision, "vision", (brain.n, VISUAL_DIM))
        ac._tensor(caption, "caption", (brain.n, CAPTION_DIM))
        extra = torch.stack((self.vision_token(vision), self.caption_token(caption)), 1)
        H = self.encoder(torch.cat((tokens, extra), 1))
        o, attention = self.emotion_query(H)
        g = torch.cat([layer(o[:, e]) for e, layer in enumerate(self.emotion_linears)], dim=-1)
        return ModelOutput(g, g.sigmoid(), g, None, None, attention, None, o, H)


class SeparateDecodedModel(nn.Module):
    """D-1, D-2(01 5-A, 11/9). main은 encoder 1(정서와 보조 feature head)과 정서 계산(a, b, A, B, U)을 가진 뇌 모델이다.
    feature_model은 feature 손실로만 따로 학습해 고정한 encoder 2이고 입력층까지 따로 있다. 정서 계산에는 encoder 2의 v̂₂, ĉ₂를 쓴다.
    정서 손실은 encoder 2로 가지 않는다(고정, no_grad). 입력은 뇌 반응뿐이다."""

    def __init__(self, main, feature_model):
        super().__init__()
        r = main.readout
        if not (r.decoded and r.has_feature_head) or r.pooling:
            raise ValueError("main은 decoded features를 쓰는 C-1 구조여야 한다")
        fr = feature_model.readout
        if fr.decoded or not fr.has_feature_head:
            raise ValueError("feature_model은 feature head만 쓰는 encoder 2여야 한다")
        if main.input_layer is feature_model.input_layer:
            raise ValueError("encoder 2는 입력층을 따로 가져야 한다")
        self.main = main
        self.feature_model = freeze(feature_model)
        self.spec = dict(kind="separate", main=dict(main.spec), feature_model=dict(feature_model.spec))

    def train(self, mode=True):
        super().train(mode)
        self.feature_model.eval()  # 고정한 encoder 2는 늘 평가 상태다(dropout 끔)
        return self

    def forward(self, brain, fixed=None):
        """fixed: (v̂₂, ĉ₂). 학습 행에서는 fold 밖(OOF) encoder 2가 낸 값을 받는다(11/9). 없으면 고정한 encoder 2를 돌린다(검증, 시험)."""
        H = self.main.encode(brain)
        r = self.main.readout
        o, emotion_attention = r.emotion_query(H)
        g = torch.cat([layer(o[:, e]) for e, layer in enumerate(r.emotion_linears)], dim=-1)
        v1, c1, feature_attention = r.feature_head(H)
        if fixed is None:
            with torch.no_grad():
                f = self.feature_model(brain)
            v2, c2 = f.v_hat, f.c_hat
        else:
            v2, c2 = fixed
        z = r.combine(g, v2, c2)  # combine도 기울기를 끊는다(G8)
        return SeparateOutput(z, z.sigmoid(), g, v1, c1, emotion_attention, feature_attention, o, H, v2, c2)


class FeatureHeadModel(nn.Module):
    """D-3(11/9, 옛 E-1). 고정한 encoder 2(feature 손실로만 학습, 입력층까지 따로)가 낸 v̂₂, ĉ₂ 위에 정서 head만 학습한다.
    정서 = a(v̂₂) + b(ĉ₂) + U[(Av̂₂) ⊙ (Bĉ₂)]. rank 0이면 더하기만 남는다. 뇌에서 바로 정서를 읽는 경로(g)는 없다.
    개념 bottleneck의 sequential 학습과 같은 꼴이다(Koh 외 2020)."""

    def __init__(self, feature_model, rank):
        super().__init__()
        fr = feature_model.readout
        if fr.decoded or not fr.has_feature_head:
            raise ValueError("feature_model은 feature head만 쓰는 encoder 2여야 한다")
        if isinstance(rank, bool) or rank not in (0,) + INTERACTION_RANKS:
            raise ValueError("rank는 0, 1, 2, 4, 8이다")
        self.rank = rank
        self.feature_model = freeze(feature_model)
        self.a = nn.Linear(VISUAL_DIM, N_EMOTIONS, bias=True)
        self.b = nn.Linear(CAPTION_DIM, N_EMOTIONS, bias=True)
        if rank:
            self.A = nn.Linear(VISUAL_DIM, rank, bias=False)
            self.B = nn.Linear(CAPTION_DIM, rank, bias=False)
            self.U = nn.Linear(rank, N_EMOTIONS, bias=False)
        self.spec = dict(kind="features_only", rank=rank, feature_model=dict(feature_model.spec))

    def train(self, mode=True):
        super().train(mode)
        self.feature_model.eval()
        return self

    def forward(self, brain, fixed=None):
        """fixed: (v̂₂, ĉ₂). 학습 행에서는 fold 밖(OOF) encoder 2가 낸 값을 받는다(11/9). 없으면 고정한 encoder 2를 돌린다."""
        if fixed is None:
            with torch.no_grad():
                f = self.feature_model(brain)
            v, c = f.v_hat, f.c_hat
        else:
            v, c = fixed
        z = self.a(v) + self.b(c)
        if self.rank:
            z = z + self.U(self.A(v) * self.B(c))
        return SeparateOutput(z, z.sigmoid(), z, v, c, None, None, None, None, v, c)


class FrozenEncoderModel(nn.Module):
    """D-4(11/9 석진 님). 장면 특징으로만 학습해 고정한 encoder 2의 token H 위에 A-1과 같은 정서 head(정서 query 34개와 정서별 선형층)만 학습한다.
    입력층과 encoder는 같은 바깥 fold, 같은 seed의 feature_encoder 체크포인트에서 불러와 고정한다(기울기 없음, dropout 끈 평가 상태). D-1의 feature_model 처리와 같다.
    encoder 2의 시각 head, 캡션 head와 정서 쪽 가중치는 쓰지 않는다. 정서 head는 새로 초기화한다. 사전학습한 표현에서 다른 과제를 읽는 꼴이다(Ortega Caro 외 2024)."""

    def __init__(self, feature_model):
        super().__init__()
        fr = feature_model.readout
        if fr.decoded or not fr.has_feature_head:
            raise ValueError("feature_model은 feature head만 쓰는 encoder 2여야 한다")
        self.feature_model = freeze(feature_model)
        self.d = feature_model.spec["d"]
        self.readout = Readout(self.d)
        self.spec = dict(kind="frozen_encoder", feature_model=dict(feature_model.spec))

    def train(self, mode=True):
        super().train(mode)
        self.feature_model.eval()  # 고정한 encoder 2는 늘 평가 상태다
        return self

    def forward(self, brain):
        with torch.no_grad():
            H = self.feature_model.encode(brain)
        return self.readout(H)

def freeze(model):
    """Multimodal 원본을 고정한다(G16). 가중치를 바꿀 수 없고 dropout도 꺼진다."""
    for p in model.parameters():
        p.requires_grad_(False)
    return model.eval()


def state_digest(model):
    """가중치 전체의 해시. 고정한 모델이 바뀌지 않았는지 시험하고 기록하는 데 쓴다."""
    h = hashlib.sha256()
    for name, t in sorted(model.state_dict().items()):
        h.update(name.encode())
        h.update(t.detach().cpu().numpy().tobytes())
    return h.hexdigest()


def parameter_group_name(name, is_layernorm):
    """G13의 묶음. 알 수 없는 이름은 멈춘다. 새 파라미터가 조용히 어느 묶음에 들어가지 않게 한다."""
    for prefix in ("main.", "feature_model."):  # D-1, D-2의 두 뇌 모델. 묶음 규칙은 같다
        if name.startswith(prefix):
            name = name[len(prefix):]
            break
    last = name.split(".")[-1]
    if is_layernorm:
        return "no_decay"  # LayerNorm
    if name.startswith("input_layer.weights."):
        return "input_weight"  # 입력층 W. d와 함께 후보에서 고른다
    if name.startswith("input_layer.input_bias."):
        return "no_decay"  # b(s, r)
    if name in ("input_layer.roi_embedding", "input_layer.cluster_embedding"):
        return "other"
    if name in ("vision_token.weight", "caption_token.weight"):
        return "feature_token"  # O5. Multimodal Model의 두 특징 선형층
    if last in ("bias", "in_proj_bias"):
        return "no_decay"
    if last in ("weight", "in_proj_weight", "query"):
        return "other"
    raise ValueError(f"weight decay 묶음을 정할 수 없는 파라미터: {name}")


def parameter_assignment(model):
    """이름 -> 묶음. 고정된 파라미터는 frozen이다."""
    norm_ids = {id(p) for m in model.modules() if isinstance(m, nn.LayerNorm) for p in m.parameters(recurse=False)}
    out = {}
    for name, p in model.named_parameters():
        group = parameter_group_name(name, id(p) in norm_ids)
        out[name] = "frozen" if not p.requires_grad else group
    return out


def parameter_groups(model, lr, input_weight_decay, feature_token_decay=None):
    """AdamW에 넘길 묶음(G13). 학습하는 파라미터가 빠지거나 겹치면 멈춘다."""
    if not isinstance(lr, float) or lr <= 0:
        raise ValueError("learning rate가 잘못됐다")
    if not isinstance(input_weight_decay, float) or input_weight_decay < 0:
        raise ValueError("입력층 weight decay가 잘못됐다")
    assignment = parameter_assignment(model)
    named = dict(model.named_parameters())
    decays = dict(input_weight=input_weight_decay, other=OTHER_WEIGHT_DECAY, no_decay=0.0, feature_token=feature_token_decay)
    groups = []
    for group, decay in decays.items():
        params = [named[n] for n, g in assignment.items() if g == group]
        if params:
            if decay is None:
                raise ValueError(f"{group} 묶음의 weight decay가 없다")
            groups.append(dict(params=params, weight_decay=decay, lr=lr, name=group))
    trainable = {id(p) for p in model.parameters() if p.requires_grad}
    placed = [id(p) for g in groups for p in g["params"]]
    if len(placed) != len(set(placed)) or set(placed) != trainable:
        raise ValueError("weight decay 묶음이 학습 파라미터와 일치하지 않는다")
    return groups


def count_parameters(model):
    """F8. 학습 가중치 수. 입력층을 따로 적는다. frozen은 학습하지 않는 수다."""
    rows = dict(input_weight=0, input_bias=0, roi_embedding=0, shared=0, frozen=0)
    for name, p in model.named_parameters():
        name = name.split("main.", 1)[1] if name.startswith("main.") else name
        if not p.requires_grad:
            rows["frozen"] += p.numel()
        elif name.startswith("input_layer.weights."):
            rows["input_weight"] += p.numel()
        elif name.startswith("input_layer.input_bias."):
            rows["input_bias"] += p.numel()
        elif name == "input_layer.roi_embedding":
            rows["roi_embedding"] += p.numel()
        else:
            rows["shared"] += p.numel()
    rows["trainable"] = sum(v for k, v in rows.items() if k != "frozen")
    return rows


def save_checkpoint(path, model, **meta):
    torch.save(dict(spec=model.spec, state_dict={k: v.cpu() for k, v in model.state_dict().items()}, meta=meta), path)


def build_from_spec(spec):
    spec = dict(spec)
    kind = spec.pop("kind")
    if kind == "separate":
        return SeparateDecodedModel(build_from_spec(spec["main"]), build_from_spec(spec["feature_model"]))
    if kind == "features_only":
        return FeatureHeadModel(build_from_spec(spec["feature_model"]), spec["rank"])
    if kind == "frozen_encoder":
        return FrozenEncoderModel(build_from_spec(spec["feature_model"]))
    voxel_counts, d = spec.pop("voxel_counts"), spec.pop("d")
    return MultimodalModel(voxel_counts, d, **spec) if kind == "multimodal" else BrainModel(voxel_counts, d, **spec)  # 11/10 전 체크포인트는 tokenizer 키가 없어 선형으로 되살린다


def load_checkpoint(path, device="cpu"):
    """저장한 모델을 평가 상태로 되살린다. S9는 이 함수로 읽는다. 추론용이다. requires_grad는 저장되지 않으므로,
    E-고정의 고정 head 같은 학습 상태는 되살리지 않는다. 학습을 이어 하려면 고정 상태를 따로 복원해야 한다."""
    saved = torch.load(path, map_location="cpu", weights_only=True)
    model = build_from_spec(dict(saved["spec"]))
    model.load_state_dict(saved["state_dict"])
    return model.to(device).eval(), saved["meta"]


def to_original_scale(z, mean, std):
    """표준화한 값을 원래 척도로 되돌린다(N3, O20)."""
    return z * std + mean


def to_head_scale(z, train_mean, train_std, head_mean, head_std):
    """N3. 학습 fold 4개의 눈금으로 낸 decoded features를 원래 척도로 되돌린 뒤 K1 head의 D_k 눈금으로 바꾼다."""
    return (to_original_scale(z, train_mean, train_std) - head_mean) / head_std
