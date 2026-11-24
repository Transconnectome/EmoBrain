#!/usr/bin/env python3
"""공정 비교 baseline: 같은 자료·같은 분할·같은 지표로 문헌 방법과 우리 방법을 비교 (2026-10-28).

프로토콜: ours (run 묶음 6겹, 중복 제외), lit (피험자별 무작위 10겹, 중복 포함; GED·ML-BVAE·AESL 방식). make_protocols.py 가 만든다.
입력 (--features)
  roi469  : 469개 영역 평균 (피험자별 유효 영역)
  subroi4 : GED 식 영역 하위 구역 평균 (469 × 4³; build_subroi_features.py). ridge·MLP 는 펼쳐서 쓰고 GED 는 영역 노드 특징으로 쓴다.
모델 (--model)
  ridge : 차원별 ridge (34개 비율·14개 평균 평정). 규제 강도는 학습 자료 안의 5묶음 검증으로 선택
  mlp   : 은닉 128 MLP (perlmutter/mlp_student.fit 과 같음). epoch 는 학습 자료 안 검증 묶음 하나로 고르고 seed 3개 평균
  ged   : GED 공식 모델 (third_party/GED/models/graphcnn.py, MIT). 감정 34 + 영역 469 이분 그래프, MSE, Adam lr 0.01,
          StepLR(50, 0.5), batch 16, 300 epoch. 검증 세트(학습 자료의 10%)로 epoch 를 고른다.
          문헌처럼 평가 세트에서 가장 좋은 epoch 를 고른 값도 따로 기록한다 (ged_curves_*.tsv; 결과로는 쓰지 않음).
target: 34개 범주 평정자 비율(0~1, 정규화 없음), 14개 차원 평균 평정 (GED 는 34개만).
출력: runs/<protocol>/<features>_<model>/predictions_sub-XX.tsv.gz (perlmutter 분석과 같은 긴 형식)
사용: python run_baselines.py --protocol lit --features subroi4 --model ged --sub 01 [--folds 0,1] [--epochs 300] [--max-rows N] [--device cuda]
"""
import argparse
import copy
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = Path("/pscratch/sd/s/sjmoon/EmoBrain")
sys.path.insert(0, str(REPO / "project/analysis/prelim_2026-10/perlmutter"))
import run_stage1 as rs  # noqa: E402

bb, cl = rs.bb, rs.cl
ROI = REPO / "project/output/prelim_2026-10/roi_blocks"


def load(sub, protocol, features, max_rows=None):
    P = pd.read_csv(HERE / f"runs/protocols/{protocol}_sub-{sub}.tsv", sep="\t")
    if max_rows:
        P = P.groupby("fold", group_keys=False).head(max_rows // P.fold.nunique())
    R = np.load(ROI / f"Horikawa_sub-{sub}_roi469_runz.npy")[P.row.values]
    info = pd.read_csv(ROI / f"Horikawa_sub-{sub}_roi469_info.tsv", sep="\t")
    valid = info.roi_valid.values & np.isfinite(R).all(0)
    names, Y34, Y14 = cl.labels_for(P.video_id.values)
    area = np.nan_to_num(R).astype(np.float64)                                   # GED 그래프용 영역 평균 (전체 469)
    if features == "roi469":
        X = R[:, valid].astype(np.float64); node = None
    else:
        node = np.load(HERE / f"runs/features/sub-{sub}_subroi4.npy", mmap_mode="r")[P.row.values].astype(np.float64)
        X = node[:, valid].reshape(len(P), -1)
    return P, X, node, area, names, Y34, Y14


def inner_groups(n, protocol, fold_tr, seed=0, k=5):
    """학습 자료 안 검증 묶음. ours 는 남은 바깥 fold 5개, ours10·ours46 은 남은 바깥 fold 를 5묶음으로 합침 (run 묶음 유지),
    lit 는 무작위 5묶음."""
    if protocol == "ours":
        return fold_tr
    if protocol.startswith("ours"):
        u = np.unique(fold_tr); return pd.Series(fold_tr).map(dict(zip(u, np.arange(len(u)) % k))).values
    return np.random.RandomState(seed).randint(0, k, n)


def run_ridge(Xtr, Ytr, Xte, groups):
    Xs, Xt = cl.std_fit(Xtr, Xte)
    return bb.fit_predict_a14(Xs, Ytr, Xt, groups)[0]


def run_mlp(Xtr, Ytr, Xte, groups, space):
    import mlp_student as ms
    ms.EVAL = 1
    if space == "A14":
        ym, ys = Ytr.mean(0), Ytr.std(0); ys[ys == 0] = 1
    else:
        ym, ys = np.zeros(Ytr.shape[1]), np.ones(Ytr.shape[1])
    h = np.unique(groups)[0]; a, b = groups != h, groups == h
    Xa, Xb = cl.std_fit(Xtr[a], Xtr[b])
    _, curve = ms.fit(Xa, (Ytr[a] - ym) / ys, space, 0, ms.EPOCHS, Xb, (Ytr[b] - ym) / ys)
    ep = int(curve.argmin() + 1)
    Xs, Xt = cl.std_fit(Xtr, Xte)
    return np.mean([ms.predict(ms.fit(Xs, (Ytr - ym) / ys, space, s, ep)[0], Xt, space) for s in ms.SEEDS], axis=0) * ys + ym, ep


def ged_edges(category_feat, area_avgs, num_activations=150, num_interactions=50):
    """GED utils.load_adj 를 그대로 옮김 (Huang et al. 2022, MIT). 학습 자료의 라벨과 영역 평균으로 감정–영역 이분 그래프의 간선을 만든다."""
    num_emotions = category_feat.shape[1]
    category_temp = category_feat.copy(); category_comp = np.tile(np.max(category_feat, axis=1), (num_emotions, 1)).T
    index_list = []
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
        area_index = np.argsort(-area_avgs[index_list[i]], axis=1)[:, 0:num_activations]
        interaction_list.append(np.argsort(-np.bincount(area_index.reshape(-1)))[0:num_interactions])
    source = [i for i in range(num_emotions) for _ in range(num_interactions)]
    destination = np.concatenate(interaction_list) + num_emotions
    edges = [[s, d] for s, d in zip(source, destination)]
    edges.extend([[i, j] for j, i in edges])
    return edges


def run_ged(node_tr, area_tr, Ytr, node_te, Yte, epochs, seed=0, device="cpu"):
    import torch
    import torch.nn as nn
    import torch.utils.data as Data
    sys.path.insert(0, str(HERE / "third_party/GED/models"))
    from graphcnn import GraphCNN
    torch.manual_seed(seed); rng = np.random.RandomState(seed)
    dev = torch.device(device)
    mu, sd = node_tr.mean(0), node_tr.std(0); sd[sd == 0] = 1                       # 영역·하위 구역별 표준화 (학습 자료 기준)
    nz = lambda A: (A - mu) / sd  # noqa: E731
    K, Rn, Pd = Ytr.shape[1], node_tr.shape[1], node_tr.shape[2]
    va = np.zeros(len(Ytr), bool); va[rng.permutation(len(Ytr))[: max(1, len(Ytr) // 10)]] = True   # 학습 자료의 10% 검증
    def pack(node, Y):
        F = np.zeros((len(node), K + Rn, Pd), np.float32); F[:, K:] = nz(node)
        return Data.TensorDataset(torch.from_numpy(F), torch.from_numpy(Y.astype(np.float32)))
    edges = torch.LongTensor(ged_edges(Ytr[~va], area_tr[~va])).transpose(0, 1)
    model = GraphCNN(5, 2, Pd, 64, K, 0.5, K + Rn, edges, "average", dev).to(dev)
    tr_loader = Data.DataLoader(pack(node_tr[~va], Ytr[~va]), batch_size=16, shuffle=True)
    sets = {"val": pack(node_tr[va], Ytr[va]), "test": pack(node_te, Yte)}
    opt = torch.optim.Adam(model.parameters(), lr=0.01); sch = torch.optim.lr_scheduler.StepLR(opt, step_size=50, gamma=0.5)
    def predict(ds):
        model.eval(); out = []
        with torch.no_grad():
            for xb, _ in Data.DataLoader(ds, batch_size=64, shuffle=False):
                out.append(model(xb.clone()).cpu().numpy())
        return np.vstack(out)
    best, best_state, curves = np.inf, None, []
    for ep in range(1, epochs + 1):
        model.train()
        for xb, yb in tr_loader:
            opt.zero_grad(); loss = nn.MSELoss(reduction="sum")(model(xb.clone()), yb.to(dev)); loss.backward(); opt.step()
        sch.step()
        pv, pt = predict(sets["val"]), predict(sets["test"])
        mv, mt = np.abs(pv - Ytr[va]).sum(1).mean(), np.abs(pt - Yte).sum(1).mean()          # GED 식 MAE (34개 합산, 영상 평균)
        curves.append(dict(epoch=ep, val_mae_sum=mv, test_mae_sum=mt))
        if mv < best:
            best, best_state = mv, copy.deepcopy(model.state_dict())
    model.load_state_dict(best_state)
    return predict(sets["test"]), pd.DataFrame(curves)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--protocol", choices=["ours", "ours10", "ours46", "lit"], required=True); ap.add_argument("--features", choices=["roi469", "subroi4"], required=True)
    ap.add_argument("--model", choices=["ridge", "mlp", "ged"], required=True); ap.add_argument("--sub", required=True)
    ap.add_argument("--folds"); ap.add_argument("--epochs", type=int, default=300); ap.add_argument("--max-rows", type=int)
    ap.add_argument("--out-root", type=Path, default=HERE / "runs")
    ap.add_argument("--device", default="cpu", help="GED 학습 장치 (cpu 또는 cuda). GPU 는 사용자가 지정해 실행")
    a = ap.parse_args(); t0 = time.time()
    P, X, node, area, names, Y34, Y14 = load(a.sub, a.protocol, a.features, a.max_rows)
    if a.model == "ged" and node is None:
        raise SystemExit("GED 는 subroi4 입력이 필요하다")
    od = a.out_root / a.protocol / f"{a.features}_{a.model}"; od.mkdir(parents=True, exist_ok=True)
    fold = P.fold.values; folds = [int(x) for x in a.folds.split(",")] if a.folds else sorted(np.unique(fold))
    obs14 = np.isfinite(Y14).all(1); preds, curves, eps = [], [], []
    spaces = [("A34", Y34, np.ones(len(fold), bool), names)] + ([] if a.model == "ged" else [("A14", Y14, obs14, bb.DIMS14)])
    for f in folds:
        for space, Y, mask, dims in spaces:
            trm, tem = (fold != f) & mask, (fold == f) & mask; idx = np.flatnonzero(tem)
            g = inner_groups(trm.sum(), a.protocol, fold[trm], seed=f)
            if a.model == "ridge":
                Pp = run_ridge(X[trm], Y[trm], X[tem], g)
            elif a.model == "mlp":
                Pp, ep = run_mlp(X[trm], Y[trm], X[tem], g, space); eps.append(dict(fold=f, space=space, epochs=ep))
            else:
                Pp, cv = run_ged(node[trm], area[trm], Y[trm], node[tem], Y[tem], a.epochs, seed=f, device=a.device); curves.append(cv.assign(fold=f))
            mu = Y[trm].mean(0)
            for j, d in enumerate(dims):
                preds.append(pd.DataFrame(dict(participant_id=f"sub-{a.sub}", video_id=P.video_id.values[idx], outer_fold=int(f),
                                               input_condition=f"{a.features}_{a.model}", target_space=space, dimension=d,
                                               y_true=Y[idx, j], y_pred=Pp[:, j], train_mean=mu[j])))
        print(f"  sub-{a.sub} {a.protocol} {a.features}_{a.model} fold {f} 완료 ({time.time() - t0:.0f}초)", flush=True)
    tag = f"sub-{a.sub}" + (f"_folds{a.folds.replace(',', '-')}" if a.folds else "")
    pd.concat(preds, ignore_index=True).to_csv(od / f"predictions_{tag}.tsv.gz", sep="\t", index=False, float_format="%.6g")
    if curves:
        pd.concat(curves).to_csv(od / f"ged_curves_{tag}.tsv", sep="\t", index=False, float_format="%.5f")
    if eps:
        pd.DataFrame(eps).to_csv(od / f"mlp_epochs_{tag}.tsv", sep="\t", index=False)
    print(f"sub-{a.sub} 완료 ({time.time() - t0:.0f}초)")


if __name__ == "__main__":
    main()
