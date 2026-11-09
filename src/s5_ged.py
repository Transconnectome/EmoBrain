#!/usr/bin/env python3
"""S5 외부 baseline GED(Huang 외, 2022, MICCAI)를 우리 과제로 다시 학습한다(01 5-2 외부 baseline, O27, 11/9 석진 님).

원 코드(github.com/zhongyu1998/GED, commit 3ea8492, MIT)를 따른 것
- 입력: 영역마다 voxel 좌표의 상자를 축마다 4등분한 64칸의 평균(area_pooling, 원 코드 그대로)을 영역 node의 특징으로, 정서 node 34개는 학습하는 embedding.
  영역은 우리 지도의 370개(HCP360 피질 360 + 피질하 10, 원 논문과 같은 구성). voxel 값은 우리 block 반응(run 안 표준화)이고 따로 표준화하지 않는다(원 코드와 같음).
- 정서-영역 이분 그래프: 학습 영상의 정규화한 평정과 영역 평균 활동으로 만든다(load_adj, l = 150, m = 50).
- 모델과 학습: GraphCNN(층 5, MLP 층 2, 은닉 64, 마지막 dropout 0.5, 이웃 평균), MSE(합), Adam lr 0.01, StepLR(50, 0.5), batch 16, 최대 300 epoch.
원 코드에서 바꾼 것(O27, 01 외부 baseline (나), SI에 기록)
- 분할: 원 코드의 무작위 10겹 대신 우리 run 6 fold. 학습 fold 4개로 학습, 검증 fold로 epoch를 고르고, 시험 fold로 평가.
- 정규화: 원 코드는 정서마다 전체 자극(시험 포함)의 최소~최대로 평정을 정규화한다. 여기서는 학습 영상의 최소~최대로만 정규화하고 평가 때 원래 비율로 되돌린다.
- epoch 선택: 원 코드는 고르는 절차 없이 매 epoch 시험 성능을 출력한다. 여기서는 검증 fold의 공통 조기 종료(patience 30)로 고르고 가장 낮았던 epoch의 가중치로 되돌린다.
  검증 손실은 원래 비율로 되돌린 예측을 [1e-6, 1 − 1e-6]로 자른 값과 사람 평정의 soft BCE다(O27).
- seed 0, 1, 2(L9). 원 코드는 seed 하나.
"""
import sys

import numpy as np
import pandas as pd
import torch

import paths as P
import s4_common as c
import s5_common as d5

sys.path.insert(0, str(P.REPO / "third_party/ged"))
from graphcnn import GraphCNN  # noqa: E402

GED = dict(num_parts=4, num_activations=150, num_interactions=50, num_layers=5, num_mlp_layers=2, hidden_dim=64, final_dropout=0.5, pooling="average", lr=0.01, step=50, gamma=0.5, batch=16, max_epochs=300, patience=30, clip=1e-6)  # 원 코드 기본값, patience와 clip은 O27
GED_SEEDS = (0, 1, 2)


def area_pooling(n, area_cors, area_voxels):
    """GED utils.area_pooling 그대로(MIT). area_cors: 3 × voxel, area_voxels: 행 × voxel. 빈 칸은 0이다."""
    x_min, y_min, z_min = np.min(area_cors, axis=1)
    x_max, y_max, z_max = np.max(area_cors, axis=1)
    x_bound = np.linspace(x_min, x_max, n + 1)
    y_bound = np.linspace(y_min, y_max, n + 1)
    z_bound = np.linspace(z_min, z_max, n + 1)
    count = 0
    area_features = np.zeros((area_voxels.shape[0], n * n * n))
    for i in range(n):
        for j in range(n):
            for k in range(n):
                lower_bound = np.array([x_bound[i], y_bound[j], z_bound[k]]).reshape(-1, 1)
                upper_bound = np.array([x_bound[i + 1], y_bound[j + 1], z_bound[k + 1]]).reshape(-1, 1)
                if i == n - 1 or j == n - 1 or k == n - 1:  # consider the voxels at the upper boundary
                    indicator_bool = np.all((lower_bound <= area_cors) * (area_cors <= upper_bound), axis=0)
                else:
                    indicator_bool = np.all((lower_bound <= area_cors) * (area_cors < upper_bound), axis=0)
                indicator = np.nonzero(indicator_bool)[0]
                block_features = area_voxels[:, indicator]
                if block_features.shape[1]:
                    area_features[:, count] = np.mean(block_features, axis=1)
                count = count + 1
    return area_features


def load_adj(category_feat, area_avgs, num_activations, num_interactions):
    """GED utils.load_adj 그대로(MIT). 학습 영상의 정규화한 평정과 영역 평균 활동만 넣는다."""
    num_emotions = category_feat.shape[1]
    category_feat = np.asarray(category_feat)
    area_avgs = np.asarray(area_avgs)
    index_list = []
    category_temp = category_feat.copy()
    category_comp = np.tile(np.max(category_feat, axis=1), (num_emotions, 1)).T
    for i in range(num_emotions):
        index = np.nonzero(np.argmax(category_temp, axis=1) == i)[0]
        multi_index = np.nonzero(np.sum(category_temp == category_comp, axis=1) > 1)[0]
        zero_index = np.intersect1d(index, multi_index)
        if zero_index.shape[0]:
            category_temp[zero_index, i] = 0
        if index.shape[0] < 5:
            index = np.argsort(-category_feat[:, i])[0:10]
        index_list.append(index)
    interaction_list = []
    for i in range(num_emotions):
        rep_feat = area_avgs[index_list[i]]
        area_index = np.argsort(-rep_feat, axis=1)[:, 0:num_activations]
        interaction = np.argsort(-np.bincount(area_index.reshape(-1)))[0:num_interactions]
        interaction_list.append(interaction)
    source = []
    for i in range(num_emotions):
        source.extend([i] * num_interactions)
    destination = np.concatenate(interaction_list) + num_emotions
    edges = [[s, d] for s, d in zip(source, destination)]
    edges.extend([[i, j] for j, i in edges])
    return edges


def roi_coords(s, brain):
    """ROI마다 voxel 좌표(3 × voxel). brain.X의 열(고유 voxel)은 QC mask의 NumPy 기본 순서의 열 번호를 정렬한 것이다(s2_manifest, s5_common.load_brain)."""
    import nibabel as nib
    import s2_roi_cells as rc
    z = np.load(d5.roi_path(s))
    if rc.sha(rc.mask_path(s)) != str(z["mask_sha256"]):
        raise SystemExit(f"sub-{s}: QC mask가 ROI 표를 만들 때와 다르다")
    mask = np.asarray(nib.load(rc.mask_path(s)).dataobj) > 0
    ijk = np.argwhere(mask)[np.unique(z["columns"])]
    if len(ijk) != brain.X.shape[1]:
        raise SystemExit(f"sub-{s}: 좌표 수가 voxel 열 수와 다르다")
    return [ijk[p].T for p in brain.roi_positions]


def build_inputs(X, roi_positions, coords, n_emotions, num_parts):
    """원 코드 load_data의 영역 node 특징(64칸 평균)과 영역 평균 활동. 정서 node 자리는 0이고 모델이 embedding으로 채운다. 학습하는 값이 없어 모든 행을 한 번에 낸다."""
    feats = np.zeros((X.shape[0], n_emotions + len(roi_positions), num_parts ** 3), np.float32)
    avgs = np.zeros((X.shape[0], len(roi_positions)), np.float32)
    for r, (pos, cor) in enumerate(zip(roi_positions, coords)):
        vox = np.asarray(X[:, pos], np.float64)
        feats[:, n_emotions + r] = area_pooling(num_parts, cor, vox)
        avgs[:, r] = vox.mean(1)
    return feats, avgs


def train_ged(feats, y_norm, edges, tr, va, y_val, lo, span, seed, settings, device):
    """한 seed의 학습. 반환: 고른 epoch의 모델, 검증 손실 기록."""
    torch.manual_seed(seed)
    g = torch.Generator().manual_seed(seed)
    n_em = y_norm.shape[1]
    edge_mat = torch.LongTensor(edges).transpose(0, 1)
    model = GraphCNN(settings["num_layers"], settings["num_mlp_layers"], feats.shape[2], settings["hidden_dim"], n_em, settings["final_dropout"], feats.shape[1], edge_mat, settings["pooling"], device).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=settings["lr"])
    sched = torch.optim.lr_scheduler.StepLR(opt, step_size=settings["step"], gamma=settings["gamma"])
    F_all = torch.as_tensor(feats)
    Y = torch.as_tensor(y_norm, dtype=torch.float32)
    yv = torch.as_tensor(y_val, dtype=torch.float32)
    lo_t, span_t = torch.as_tensor(lo, dtype=torch.float32), torch.as_tensor(span, dtype=torch.float32)
    best, best_state, best_epoch, wait, history = float("inf"), None, 0, 0, []
    for epoch in range(1, settings["max_epochs"] + 1):
        model.train()
        order = tr[torch.randperm(len(tr), generator=g).numpy()]
        total = 0.0
        for i in range(0, len(order), settings["batch"]):
            b = order[i:i + settings["batch"]]
            out = model(F_all[b].clone().to(device))
            loss = torch.nn.functional.mse_loss(out, Y[b].to(device), reduction="sum")  # 원 코드 nn.MSELoss(reduction='sum')
            opt.zero_grad()
            loss.backward()
            opt.step()
            total += loss.item()
        sched.step()
        p = predict(model, F_all, va, settings["batch"], device)
        p_orig = (p * span_t + lo_t).clamp(settings["clip"], 1 - settings["clip"])
        vloss = torch.nn.functional.binary_cross_entropy(p_orig, yv).item()  # O27. 원래 비율로 되돌려 자른 값의 soft BCE
        if not np.isfinite(vloss):
            raise ValueError("GED 검증 손실이 NaN 또는 Inf다")
        history.append(dict(epoch=epoch, train_loss=total / len(order), val_loss=vloss))
        if vloss < best:
            best, best_epoch, wait = vloss, epoch, 0
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
        else:
            wait += 1
            if wait >= settings["patience"]:
                break
    model.load_state_dict(best_state)
    return model, best, best_epoch, history


@torch.no_grad()
def predict(model, F_all, rows, batch, device):
    model.eval()
    out = [model(F_all[rows[i:i + batch]].clone().to(device)).cpu() for i in range(0, len(rows), batch)]
    return torch.cat(out)


def ged_task(brain, y_em, coords, k, device, settings=GED, seeds=GED_SEEDS):
    """참가자 하나, 바깥 fold 하나. 반환: 시험 예측(seed마다, 원래 비율), 학습 기록, 기록용 값."""
    if not seeds or seeds[0] != 0:
        raise ValueError("seed는 0부터다(L9)")
    r = c.roles(k)
    tr = np.flatnonzero(np.isin(brain.fold, r["train"]))
    va, te = np.flatnonzero(brain.fold == r["val"]), np.flatnonzero(brain.fold == k)
    y = np.asarray(y_em, np.float64)
    lo, hi = y[tr].min(0), y[tr].max(0)
    if (hi <= lo).any():
        raise ValueError("학습 영상에서 값이 변하지 않는 정서가 있어 최소~최대로 정규화할 수 없다")
    span = hi - lo
    y_norm = np.full_like(y, np.nan)
    y_norm[tr] = (y[tr] - lo) / span  # 학습 영상만 정규화한다. 검증, 시험 영상의 평정은 정규화에 쓰지 않는다
    feats, avgs = build_inputs(brain.X, brain.roi_positions, coords, y.shape[1], settings["num_parts"])
    edges = load_adj(y_norm[tr], avgs[tr], settings["num_activations"], settings["num_interactions"])
    preds, rows = [], []
    for sd in seeds:
        model, vloss, epoch, history = train_ged(feats, np.nan_to_num(y_norm), edges, tr, va, y[va], lo, span, sd, settings, device)
        p = predict(model, torch.as_tensor(feats), te, settings["batch"], device).numpy() * span + lo
        preds.append(p)
        rows += [dict(seed=sd, **h) for h in history]
    return dict(video_id=brain.video_id[te], emotion_seeds=c.finite(np.stack(preds), "GED 예측"), seeds=np.array(seeds), train_min=lo, train_max=hi, n_edges=np.array(len(edges))), pd.DataFrame(rows)
