#!/usr/bin/env python3
"""S5 외부 baseline ML-BVAE(Fu 외, 2024, IEEE TNNLS)를 우리 과제로 다시 학습한다(01 5-2 외부 baseline, O27, O28, 11/9 석진 님).

공개 코드(github.com/KaichengFu1997/ML-BVAE, commit 9cb9884)는 라이선스가 없어 복사하지 않고, 논문(arXiv 2211.02629, 3절, 4.C절)과 코드의 계산을 이 파일에 다시 짰다.
원 논문과 코드를 따른 것
- 입력: HCP360 피질 360개 영역마다 voxel 좌표 상자를 n³칸으로 나눈 칸 평균(ROI pooling). 왼쪽 반구 180개(x_l), 오른쪽 180개(x_r), 그 차이(x_d = x_l − x_r).
  칸 평균은 공개되지 않은 전처리라 GED 공식 코드의 area_pooling으로 만든다. 따로 표준화하지 않는다(공개 코드와 같음).
- BVAE: 보기마다 encoder(입력 → 512 → 512 → μ, log σ², ReLU), decoder(64 → 512 → 512 → 512 → 입력), 표준 정규 prior와 Product of Experts, 잠재 차원 64.
  ELBO = 세 보기의 복원 MSE(λl = λr = λd = 1) + β × KL. β는 batch마다 (j + (i − 1)M + 1) / (100M)로 키운다(100 epoch에 1).
  학습 때 네 가지 입력(세 보기 함께, 왼쪽만, 오른쪽만, 차이만)마다 ELBO와 분류 손실을 더한다.
- 분류망: z에 정서별 선형 가중을 곱한 정서별 표현(label-aware), 학습 라벨이 함께 나온 비율 H를 mask로 더한 self-attention(head 1), 두 출력의 합.
  H는 학습 영상의 평정을 0.1에서 이진화해 낸다(원 논문의 라벨 만들기와 같음). 학습 영상에서 한 번도 나오지 않은 정서의 행은 0.
- 손실 = λ1 × ELBO 합 + λ2 × 분류 손실 합. 공개 코드의 λ1 = 1.5, λ2 = 0.1이므로 λ2 = 0.1로 두고 λ1 = (λ1/λ2) × 0.1.
- Adam(learning rate 1e-4, weight decay 0.1, 공개 코드의 기본 β), batch 100, 30 epoch(공개 코드 기본값), float64.
원 논문과 코드에서 바꾼 것(O27, 01 외부 baseline (가), (다), (라), SI에 기록)
- 목표: 27개 이진 라벨 대신 34개 평정 비율. 손실: asymmetric focal loss 대신 soft BCE(이진 라벨용이라).
- 분할: 무작위 10겹 대신 우리 run 6 fold. 칸 수 n³ ∈ {8, 27, 64, 125, 216, 343}과 λ1/λ2 ∈ {0.001, 0.01, 0.1, 1, 2, 5, 10, 15, 20}을 검증 fold의 정서별 r 평균(공통 기준)으로
  seed 0에서 고르고(원 논문의 탐색 범위 그대로, O28), 그 설정으로 seed 1, 2를 더한다. 학습 길이는 공개 코드대로 30 epoch로 두고 조기 종료하지 않는다.
- 예측: 평가 상태에서 세 보기를 함께 넣고 z = μ로 낸 logit의 sigmoid.
"""
import numpy as np
import pandas as pd
import torch
from torch import nn

import s4_common as c
import s5_common as d5
from s5_ged import area_pooling

N_HEMI = 180  # 01 ROI 순서: 0~179 왼쪽, 180~359 오른쪽(이름으로 짝 확인), 360~369 피질하(쓰지 않음)
NROIF = (8, 27, 64, 125, 216, 343)  # 원 논문 4.C절
RATIOS = (0.001, 0.01, 0.1, 1.0, 2.0, 5.0, 10.0, 15.0, 20.0)  # λ1/λ2, 원 논문 4.C절
MLBVAE = dict(latent=64, hidden=512, lr=1e-4, weight_decay=0.1, batch=100, epochs=30, annealing_epochs=100, lambda2=0.1, label_threshold=0.1)
SEEDS = (0, 1, 2)


class Encoder(nn.Module):
    def __init__(self, n_in, hidden, latent):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(n_in, hidden), nn.ReLU(), nn.Linear(hidden, hidden), nn.ReLU())
        self.mu, self.logvar = nn.Linear(hidden, latent), nn.Linear(hidden, latent)

    def forward(self, x):
        h = self.net(x)
        return self.mu(h), self.logvar(h)


class Decoder(nn.Module):
    def __init__(self, n_out, hidden, latent):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(latent, hidden), nn.ReLU(), nn.Linear(hidden, hidden), nn.ReLU(), nn.Linear(hidden, hidden), nn.Linear(hidden, n_out))

    def forward(self, z):
        return self.net(z)


class LabelAttention(nn.Module):
    """정서별 표현 사이 self-attention. mask H를 attention 점수에 더한다(head 1)."""

    def __init__(self, dim, mask):
        super().__init__()
        self.qkv = nn.Linear(dim, 3 * dim, bias=False)
        self.proj = nn.Linear(dim, dim)
        self.register_buffer("mask", mask)
        self.scale = dim ** -0.5

    def forward(self, x):
        q, k, v = self.qkv(x).chunk(3, dim=-1)
        a = ((q @ k.transpose(-2, -1)) * self.scale + self.mask).softmax(-1)
        return self.proj(a @ v)


class Classifier(nn.Module):
    def __init__(self, latent, n_labels, mask):
        super().__init__()
        self.c1 = nn.Linear(latent, n_labels)
        self.c2 = nn.Linear(latent, 1)
        self.att = LabelAttention(latent, mask)

    def forward(self, z):
        ya = self.c1(z)
        emb = z.unsqueeze(1) * self.c1.weight.unsqueeze(0)  # 행 × 정서 × 잠재
        return ya + self.c2(self.att(emb)).squeeze(-1)


class MultiViewVAE(nn.Module):
    def __init__(self, n_in, n_labels, mask, latent=64, hidden=512):
        super().__init__()
        self.enc = nn.ModuleList(Encoder(n_in, hidden, latent) for _ in range(3))  # 왼쪽, 오른쪽, 차이
        self.dec = nn.ModuleList(Decoder(n_in, hidden, latent) for _ in range(3))
        self.cls = Classifier(latent, n_labels, mask)
        self.latent = latent

    def infer(self, views):
        n = next(v for v in views if v is not None).shape[0]
        ref = next(v for v in views if v is not None)
        mus, logvars = [ref.new_zeros(n, self.latent)], [ref.new_zeros(n, self.latent)]  # 표준 정규 prior
        for e, x in zip(self.enc, views):
            if x is not None:
                m, lv = e(x)
                mus.append(m), logvars.append(lv)
        mu, lv = torch.stack(mus), torch.stack(logvars)
        prec = 1.0 / (lv.exp() + 1e-8 + 1e-8)
        pmu = (mu * prec).sum(0) / prec.sum(0)
        return pmu, torch.log(1.0 / prec.sum(0) + 1e-8)  # Product of Experts

    def forward(self, left=None, right=None, diff=None):
        mu, logvar = self.infer((left, right, diff))
        z = mu + torch.randn_like(mu) * (0.5 * logvar).exp() if self.training else mu
        return [d(z) for d in self.dec], mu, logvar, self.cls(z)


def elbo(recons, views, mu, logvar, beta):
    rec = sum(nn.functional.mse_loss(r, x) for r, x in zip(recons, views))
    kld = (-0.5 * (1 + logvar - mu.pow(2) - logvar.exp()).sum(1)).mean()
    return rec + beta * kld


def cooccurrence(y_train, threshold):
    """학습 영상의 평정을 threshold에서 이진화해 정서 j가 나온 영상 가운데 k도 나온 비율 H[j, k]."""
    b = (np.asarray(y_train) >= threshold).astype(np.float64)
    n = b.sum(0)
    H = np.zeros((b.shape[1], b.shape[1]))
    for j in range(b.shape[1]):
        if n[j] > 0:
            H[j] = b[b[:, j] == 1].sum(0) / n[j]
    return H


def views(X, roi_positions, coords, n_parts):
    """ROI pooling. 반환: 왼쪽(행 × 180·n³), 오른쪽, 차이. 피질 360개만 쓴다."""
    feats = [area_pooling(n_parts, coords[r], np.asarray(X[:, roi_positions[r]], np.float64)) for r in range(2 * N_HEMI)]
    left, right = np.concatenate(feats[:N_HEMI], 1), np.concatenate(feats[N_HEMI:], 1)
    return left, right, left - right


def train_one(V, y, tr, va, mask, ratio, seed, settings, device):
    """한 설정, 한 seed. 공개 코드처럼 정해진 epoch만큼 학습하고 마지막 모델을 쓴다. 반환: 모델, 검증 r 평균."""
    torch.manual_seed(seed)
    g = torch.Generator().manual_seed(seed)
    dt = torch.float64
    L, R, D = (torch.as_tensor(v, dtype=dt, device=device) for v in V)
    Y = torch.as_tensor(y, dtype=dt, device=device)
    model = MultiViewVAE(L.shape[1], y.shape[1], torch.as_tensor(mask, dtype=dt), settings["latent"], settings["hidden"]).to(device=device, dtype=dt)
    opt = torch.optim.Adam(model.parameters(), lr=settings["lr"], weight_decay=settings["weight_decay"])
    lam2 = settings["lambda2"]
    lam1 = ratio * lam2
    n_batches = int(np.ceil(len(tr) / settings["batch"]))
    bce = nn.functional.binary_cross_entropy_with_logits
    for epoch in range(1, settings["epochs"] + 1):
        model.train()
        order = tr[torch.randperm(len(tr), generator=g).numpy()]
        for j, i in enumerate(range(0, len(order), settings["batch"])):
            b = torch.as_tensor(order[i:i + settings["batch"]], device=device)
            beta = (j + (epoch - 1) * n_batches + 1) / (settings["annealing_epochs"] * n_batches) if epoch < settings["annealing_epochs"] else 1.0
            l, r, d, t = L[b], R[b], D[b], Y[b]
            full = (l, r, d)
            loss_elbo, loss_cls = 0.0, 0.0
            for inputs in ((l, r, d), (l, None, None), (None, r, None), (None, None, d)):
                recons, mu, logvar, logit = model(*inputs)
                loss_elbo = loss_elbo + elbo(recons, full, mu, logvar, beta)
                loss_cls = loss_cls + bce(logit, t)  # 01 (가): asymmetric focal loss 대신 soft BCE
            loss = lam1 * loss_elbo + lam2 * loss_cls
            opt.zero_grad()
            loss.backward()
            opt.step()
    p = predict(model, (L, R, D), va, settings["batch"])
    score = d5.r_selection(torch.as_tensor(y[va]), torch.as_tensor(p)).nanmean().item()
    return model, score


@torch.no_grad()
def predict(model, LRD, rows, batch):
    model.eval()
    L, R, D = LRD
    out = []
    for i in range(0, len(rows), batch):
        b = torch.as_tensor(rows[i:i + batch], device=L.device)
        out.append(torch.sigmoid(model(L[b], R[b], D[b])[3]).cpu())
    return torch.cat(out).numpy()


def mlbvae_task(brain, y_em, coords, k, device, nroif=NROIF, ratios=RATIOS, settings=MLBVAE, seeds=SEEDS):
    """참가자 하나, 바깥 fold 하나. 칸 수와 λ1/λ2를 검증 fold로 고르고(seed 0, 같으면 작은 칸 수, 작은 λ1/λ2), seed 1, 2를 더한다."""
    if not set(nroif) <= set(NROIF) or not set(ratios) <= set(RATIOS) or not nroif or not ratios:
        raise ValueError(f"후보는 칸 수 {NROIF}, λ1/λ2 {RATIOS} 안에서만 준다(원 논문, O28)")
    if not seeds or seeds[0] != 0:
        raise ValueError("후보는 seed 0으로 고른다(L9)")
    if len(coords) < 2 * N_HEMI:
        raise ValueError("피질 360개 영역의 좌표가 필요하다")
    r = c.roles(k)
    tr = np.flatnonzero(np.isin(brain.fold, r["train"]))
    va, te = np.flatnonzero(brain.fold == r["val"]), np.flatnonzero(brain.fold == k)
    y = np.asarray(y_em, np.float64)
    mask = cooccurrence(y[tr], settings["label_threshold"])  # 학습 영상만
    rows, best = [], None  # best: (점수, 칸 수, λ1/λ2, 입력, seed 0 모델)
    for n3 in sorted(nroif):
        n = round(n3 ** (1 / 3))
        if n ** 3 != n3:
            raise ValueError("칸 수는 n³이다")
        V = views(brain.X, brain.roi_positions, coords, n)
        for ratio in sorted(ratios):
            model, score = train_one(V, y, tr, va, mask, ratio, seeds[0], settings, device)
            rows.append(dict(nroif=n3, ratio=ratio, seed=seeds[0], val_r=score))
            if best is None or score > best[0]:  # 같으면 앞의 것(작은 칸 수, 작은 λ1/λ2)
                best = (score, n3, ratio, V, model.cpu())
            del model
    _, n3, ratio, V, model0 = best
    LRD = tuple(torch.as_tensor(v, dtype=torch.float64, device=device) for v in V)
    preds = [predict(model0.to(device), LRD, te, settings["batch"])]
    for sd in seeds[1:]:
        model, score = train_one(V, y, tr, va, mask, ratio, sd, settings, device)
        rows.append(dict(nroif=n3, ratio=ratio, seed=sd, val_r=score))
        preds.append(predict(model, LRD, te, settings["batch"]))
    return dict(video_id=brain.video_id[te], emotion_seeds=c.finite(np.stack(preds), "ML-BVAE 예측"), seeds=np.array(seeds), cooccurrence=mask), pd.DataFrame(rows), dict(nroif=n3, ratio=ratio)
