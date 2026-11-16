#!/usr/bin/env python3
"""S5 외부 baseline EmoGrowth(Fu 외, 2025, ICML. 방법 이름 AESL)의 모델 구조를 우리 과제로 학습한다(01 5-2 외부 baseline, O27, 11/9 석진 님).

공개 코드(github.com/ChangdeDu/EmoGrowth, commit b98109d)는 라이선스가 없어 복사하지 않고, 논문(PMLR 267, 3절, 부록 B.4)과 코드(convs/CLIFModel.py,
convs/layers.py, utils/inc_net_ml.py, models/clif_ml.py의 첫 단계 학습)의 계산을 이 파일에 다시 짰다.
가져오는 것(01 결정, 11/2): 정서 관계 그래프와 graph autoencoder의 정서 embedding, 정서별 특징 분리, 정서별 분류기, 그래프 복원 손실.
빼는 것: 증분 학습 절차(라벨 모호성 해소, 이전 단계 모델 teacher), 정서 차원 정렬 손실(RKD). 그래서 λ1, λ2 항이 없다.
원 논문과 코드를 따른 것
- 입력: HCP360 피질 360개 영역의 8칸 평균(2,880차원, 부록의 Brain27과 같음). 칸 평균은 GED의 area_pooling. 따로 표준화하지 않는다(공개 코드와 같음).
- 정서 관계 그래프: 학습 영상의 라벨로 낸 대칭 조건부 확률(sym_conditional_prob, 대각 0). 라벨은 평정을 0.1에서 이진화(원 논문의 라벨과 같음).
- 정서 embedding: 고정한 무작위 정서 표현(정서 수 × 정서 수, 정규분포) → GIN 1층(은닉 128, 출력 256, batch norm, leaky ReLU 0.1, ε 학습).
- 특징 분리: 뇌 입력 → 512 → 64(ReLU), 정서 embedding → 64(sigmoid), 둘의 곱 → 64 → 64(ReLU). 정서별 분류기는 정서마다 64 → 1(groups 합성곱).
- 손실: MultiLabelSoftMarginLoss(원문 식 14의 BCE) + λ3 × 그래프 복원 손실(cosine, 정답은 그래프 + 단위행렬).
- Adam(learning rate 1e-4, weight decay 0.005, 공개 코드의 기본 β), batch 128, 40 epoch(공개 코드의 첫 단계).
원 논문과 코드에서 바꾼 것(O27, SI에 기록)
- 목표: 27개 대신 34개 정서를 한 번에 학습한다(단계 하나). 학습 라벨은 원 논문처럼 평정 비율을 0.1에서 이진화한다(11/10. 평정 비율 그대로는 학습되지 않았다). 선택과 평가는 평정 비율과의 r이다.
- 분할: 우리 run 6 fold. λ3 ∈ {0.001, 0.01, 0.1, 1, 2, 5, 10}(원 논문 부록 B.4의 탐색 범위)을 검증 fold의 정서별 r 평균으로 seed 0에서 고르고 seed 1, 2를 더한다.
  학습 길이는 공개 코드대로 40 epoch로 두고 조기 종료하지 않는다.
"""

import numpy as np
import pandas as pd
import torch
from torch import nn

import s4_common as c
import s5_common as d5
from s5_ged import area_pooling
from s5_mlbvae import N_HEMI

LAMBDA3 = (0.001, 0.01, 0.1, 1.0, 2.0, 5.0, 10.0)  # 원 논문 부록 B.4
EMOGROWTH = dict(n_parts=2, gin_hidden=128, gin_out=256, hidden=512, latent=64, lr=1e-4, weight_decay=0.005, batch=128, epochs=40, label_threshold=0.1, slope=0.1)
SEEDS = (0, 1, 2)


def _init(lin, nonlinearity, slope):
    nn.init.kaiming_uniform_(lin.weight, a=slope, nonlinearity=nonlinearity)
    nn.init.uniform_(lin.bias, 0, 0.1)


class GINLayer(nn.Module):
    """x' = MLP((1 + ε)x + A x). MLP는 선형 → batch norm → leaky ReLU를 두 번(은닉 128, 출력 256). 입력과 출력 차원이 달라 residual 없음."""

    def __init__(self, n_in, hidden, n_out, slope):
        super().__init__()
        self.eps = nn.Parameter(torch.zeros(1))
        self.l1, self.b1, self.l2, self.b2 = nn.Linear(n_in, hidden), nn.BatchNorm1d(hidden), nn.Linear(hidden, n_out), nn.BatchNorm1d(n_out)
        self.slope = slope
        for l in (self.l1, self.l2):
            _init(l, "leaky_relu", slope)

    def forward(self, x, adj):
        h = (1 + self.eps) * x + adj @ x
        h = nn.functional.leaky_relu(self.b1(self.l1(h)), self.slope)
        return nn.functional.leaky_relu(self.b2(self.l2(h)), self.slope)


class EmoGrowthNet(nn.Module):
    def __init__(self, n_in, n_labels, s=EMOGROWTH):
        super().__init__()
        self.register_buffer("label_input", torch.randn(n_labels, n_labels))  # 고정한 무작위 정서 표현(공개 코드: requires_grad=False, normal_)
        self.gin = GINLayer(n_labels, s["gin_hidden"], s["gin_out"], s["slope"])
        self.nn1a, self.nn1b = nn.Linear(n_in, s["hidden"]), nn.Linear(s["hidden"], s["latent"])
        self.nn2 = nn.Linear(s["gin_out"], s["latent"])
        self.nn3 = nn.Linear(s["latent"], s["latent"])
        for l in (self.nn1a, self.nn1b, self.nn3):
            _init(l, "relu", s["slope"])
        nn.init.kaiming_uniform_(self.nn2.weight, nonlinearity="sigmoid")
        nn.init.constant_(self.nn2.bias, 0.0)
        self.fc = nn.Conv1d(n_labels, n_labels, s["latent"], groups=n_labels)  # 정서별 분류기

    def forward(self, x, adj):
        emb = self.gin(self.label_input, adj)  # 정서 embedding(정서 × 256)
        f = torch.relu(self.nn1b(torch.relu(self.nn1a(x))))  # 행 × 64
        g = torch.sigmoid(self.nn2(emb))  # 정서 × 64
        dis = torch.relu(self.nn3(f.unsqueeze(1) * g.unsqueeze(0)))  # 행 × 정서 × 64
        return self.fc(dis).squeeze(2), emb


def label_graph(y_train, threshold):
    """공개 코드 sym_conditional_prob. 학습 영상의 라벨(평정을 threshold에서 이진화)로 대칭 조건부 확률, 대각 0."""
    y = torch.as_tensor((np.asarray(y_train) >= threshold).astype(np.float32))
    adj = y.t() @ y
    s = y.t().sum(1, keepdim=True).clamp_min(1e-6)
    adj = adj / s
    adj.fill_diagonal_(0.0)
    return (adj + adj.t()) * 0.5


def train_targets(y, threshold):
    """11/10 석진 님 결정((가)). 원 논문의 학습 라벨처럼 평정 비율을 threshold(0.1)에서 이진화한다. 평정 비율을 그대로 주면 학습 영상에서도
    정서별 평균만 맞히는 상태로 수렴했다(04 11/10 기록). 검증 선택과 시험 평가는 평정 비율과의 r 그대로다."""
    return (np.asarray(y, np.float64) >= threshold).astype(np.float32)


def link_loss(emb, adj):
    """공개 코드 LinkPredictionLoss_cosine: 정서 embedding의 cosine 유사도 행렬과 그래프의 평균 제곱 차이."""
    e = emb / (emb.norm(dim=1, keepdim=True) + 1e-6)
    return ((adj - e @ e.t()) ** 2).mean()


def inputs(X, roi_positions, coords, n_parts):
    """피질 360개 영역의 n³칸 평균을 이어 붙인다(n = 2면 2,880차원)."""
    return np.concatenate([area_pooling(n_parts, coords[r], np.asarray(X[:, roi_positions[r]], np.float64)) for r in range(2 * N_HEMI)], 1).astype(np.float32)


def train_one(x, y, tr, va, adj, lam3, seed, s, device):
    torch.manual_seed(seed)
    g = torch.Generator().manual_seed(seed)
    X = torch.as_tensor(x, device=device)
    Y = torch.as_tensor(train_targets(y, s["label_threshold"]), device=device)  # 11/10. 원 논문처럼 0.1에서 이진화한 라벨로 학습(평가는 평정 비율과의 r)
    A = adj.to(device)
    A_loss = A + torch.eye(A.shape[0], device=device)
    model = EmoGrowthNet(X.shape[1], Y.shape[1], s).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=s["lr"], weight_decay=s["weight_decay"])
    cost = nn.MultiLabelSoftMarginLoss()
    for _ in range(s["epochs"]):
        model.train()
        order = tr[torch.randperm(len(tr), generator=g).numpy()]
        for i in range(0, len(order), s["batch"]):
            b = torch.as_tensor(order[i:i + s["batch"]], device=device)
            logits, emb = model(X[b], A)
            loss = cost(logits, Y[b]) + lam3 * link_loss(emb, A_loss)
            opt.zero_grad()
            loss.backward()
            opt.step()
    p = predict(model, X, A, va, s["batch"])
    return model, d5.r_selection(torch.as_tensor(np.asarray(y)[va], dtype=torch.float32), torch.as_tensor(p)).nanmean().item()


@torch.no_grad()
def predict(model, X, A, rows, batch):
    model.eval()
    return torch.cat([torch.sigmoid(model(X[torch.as_tensor(rows[i:i + batch], device=X.device)], A)[0]).cpu() for i in range(0, len(rows), batch)]).numpy()


def emogrowth_task(brain, y_em, coords, k, device, lambdas=LAMBDA3, settings=EMOGROWTH, seeds=SEEDS):
    """참가자 하나, 바깥 fold 하나. λ3를 검증 fold로 고르고(seed 0, 같으면 작은 λ3) seed 1, 2를 더한다."""
    if not lambdas or not set(lambdas) <= set(LAMBDA3):
        raise ValueError(f"λ3 후보는 {LAMBDA3} 안에서만 준다(원 논문 부록 B.4)")
    if not seeds or seeds[0] != 0:
        raise ValueError("후보는 seed 0으로 고른다(L9)")
    if len(coords) < 2 * N_HEMI:
        raise ValueError("피질 360개 영역의 좌표가 필요하다")
    r = c.roles(k)
    tr = np.flatnonzero(np.isin(brain.fold, r["train"]))
    va, te = np.flatnonzero(brain.fold == r["val"]), np.flatnonzero(brain.fold == k)
    y = np.asarray(y_em, np.float64)
    adj = label_graph(y[tr], settings["label_threshold"])  # 학습 영상만
    x = inputs(brain.X, brain.roi_positions, coords, settings["n_parts"])
    rows, best = [], None
    for lam in sorted(lambdas):
        model, score = train_one(x, y, tr, va, adj, lam, seeds[0], settings, device)
        rows.append(dict(lambda3=lam, seed=seeds[0], val_r=score))
        if best is None or score > best[0]:
            best = (score, lam, model)
    _, lam, model0 = best
    X = torch.as_tensor(x, device=device)
    A = adj.to(device)
    preds = [predict(model0, X, A, te, settings["batch"])]
    for sd in seeds[1:]:
        model, score = train_one(x, y, tr, va, adj, lam, sd, settings, device)
        rows.append(dict(lambda3=lam, seed=sd, val_r=score))
        preds.append(predict(model, X, A, te, settings["batch"]))
    return dict(video_id=brain.video_id[te], emotion_seeds=c.finite(np.stack(preds), "EmoGrowth 예측"), seeds=np.array(seeds), label_graph=adj.numpy()), pd.DataFrame(rows), dict(lambda3=lam)
