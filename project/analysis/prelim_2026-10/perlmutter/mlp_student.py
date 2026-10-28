#!/usr/bin/env python3
"""작은 MLP student: 내용 teacher 예측을 보조 target 으로 쓰는 뇌 단독 정서 디코더 (2026-10-28).

구조: 469개 영역 (학습 fold 기준 표준화) → 은닉 128 (GELU, dropout 0.3) → 정서. AdamW (lr 3e-3, weight decay 1e-2), full batch, 최대 300 epoch.
손실: (1 - w)·L(실제 평정) + w·L(teacher 예측). 34개 범주는 soft BCE (sigmoid), 14개 차원은 학습 평균·표준편차로 z 한 MSE.
  soft BCE 와 MSE 는 target 에 대해 선형(또는 상수 차이)이라, 섞은 target 하나로 학습하는 것과 같다.
teacher
  content  : 내용 (V-JEPA 2 + 사람 캡션) → 정서 ridge 의 교차검증 밖 예측 (teacher_cache.py)
  labelpca : 내용 없는 대조. 학습 라벨의 주성분 4개 smoothing
선택: 안쪽 5묶음 검증에서 실제 평정 손실(출력 합)이 가장 작은 (w, k, epoch) 를 공간마다 하나 고른다. w = 0 도 후보.
  검증 손실은 매 epoch 기록한다 (2026-10-28 수정: 10 epoch 간격이면 14개 차원의 뇌 단독이 첫 평가점 10 에 몰려 범위가 최적을 감싸지 못했다).
최종: 바깥 학습 fold 전체로 고른 설정을 seed 3개로 학습해 예측 평균. 평가 영상에는 뇌만 넣는다.
조건: mlp_w0 (뇌 단독 MLP), mlp_content_wsel, mlp_labelpca_wsel
사용: python mlp_student.py --sub 01 | --summarize   (torch 가 있는 brainvlm_qwen_env)
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn

sys.path.insert(0, str(Path(__file__).parent))
import teacher_cache as tc  # noqa: E402

ld, bb, cl = tc.ld, tc.bb, tc.rs.cl
OUT = tc.rs.OUT / "07_students/mlp"
HID, DROP, WD, LR, EPOCHS, EVAL = 128, 0.3, 1e-2, 3e-3, 300, 1
WS = [0.0, 0.5, 0.75, 1.0]
KS = [4]
SEEDS = [0, 1, 2]
torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "4")))


def fit(X, T, space, seed, epochs, Xv=None, Yv=None):
    """target T 로 학습. Xv·Yv 가 있으면 EVAL epoch 마다 실제 평정 기준 검증 손실(출력 합)을 기록한다."""
    torch.manual_seed(seed)
    X_, T_ = torch.as_tensor(X, dtype=torch.float32), torch.as_tensor(T, dtype=torch.float32)
    if space == "A34":
        m0 = np.clip(T.mean(0), 1e-4, 1 - 1e-4); bias = np.log(m0 / (1 - m0))
        L = lambda o, y: nn.functional.binary_cross_entropy_with_logits(o, y, reduction="none")  # noqa: E731
    else:
        bias = T.mean(0)
        L = lambda o, y: (o - y) ** 2  # noqa: E731
    model = nn.Sequential(nn.Linear(X.shape[1], HID), nn.GELU(), nn.Dropout(DROP), nn.Linear(HID, T.shape[1]))
    with torch.no_grad():
        model[-1].bias.copy_(torch.as_tensor(bias, dtype=torch.float32))
    opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WD)
    if Xv is not None:
        Xv_, Yv_ = torch.as_tensor(Xv, dtype=torch.float32), torch.as_tensor(Yv, dtype=torch.float32)
    curve = []
    for ep in range(1, epochs + 1):
        model.train(); opt.zero_grad(); L(model(X_), T_).mean().backward(); opt.step()
        if Xv is not None and ep % EVAL == 0:
            model.eval()
            with torch.no_grad():
                curve.append(L(model(Xv_), Yv_).sum().item())
    model.eval()
    return model, np.array(curve)


def predict(model, X, space):
    with torch.no_grad():
        o = model(torch.as_tensor(X, dtype=torch.float32)).numpy().astype(np.float64)
    return 1 / (1 + np.exp(-o)) if space == "A34" else o


def run_subject(sub):
    t0 = time.time(); OUT.mkdir(parents=True, exist_ok=True)
    d = np.load(tc.CACHE / f"sub-{sub}.npz")
    B, fold, vids = d["B"].astype(np.float64), d["fold"], d["vids"]
    pid = f"sub-{sub}"; preds, sel = [], []
    obs14 = np.isfinite(d["Y14"]).all(1)
    configs = [("w0", 0, 0.0)] + [("content", 0, w) for w in WS[1:]] + [("labelpca", k, w) for k in KS for w in WS[1:]]
    families = {"mlp_w0": ["w0"], "mlp_content_wsel": ["w0", "content"], "mlp_labelpca_wsel": ["w0", "labelpca"]}
    for f in np.unique(fold):
        for space, Y, mask, dims in [("A34", d["Y34"], np.ones(len(fold), bool), list(d["names"])),
                                     ("A14", d["Y14"], obs14, list(d["dims14"]))]:
            trm, tem = (fold != f) & mask, (fold == f) & mask
            g = fold[trm]; Ytr = Y[trm]; idx = np.flatnonzero(tem)
            if space == "A14":
                ym, ys = Ytr.mean(0), Ytr.std(0); ys[ys == 0] = 1
            else:
                ym, ys = np.zeros(Ytr.shape[1]), np.ones(Ytr.shape[1])
            z = lambda A: (A - ym) / ys  # noqa: E731

            def teacher(kind, k, rows_a, key):
                if kind == "content":
                    T = d[key]
                else:
                    T = ld.label_smooth(Ytr[rows_a], k)
                return np.clip(T, 1e-4, 1 - 1e-4) if space == "A34" else T

            curves = {c: 0 for c in configs}
            for h in np.unique(g):
                a, b = g != h, g == h
                Ba, Bb = cl.std_fit(B[trm][a], B[trm][b])
                for c in configs:
                    kind, k, w = c
                    T = z(Ytr[a]) if kind == "w0" else (1 - w) * z(Ytr[a]) + w * z(teacher(kind, k, a, f"T_{space}_f{f}_h{h}"))
                    curves[c] = curves[c] + fit(Ba, T, space, 0, EPOCHS, Bb, z(Ytr[b]))[1]
            Btr, Bte = cl.std_fit(B[trm], B[tem])
            mu = Ytr.mean(0); all_rows = np.ones(len(Ytr), bool)
            for fam, kinds in families.items():
                cand = [(curves[c].min(), c, int((curves[c].argmin() + 1) * EVAL)) for c in configs if c[0] in kinds]
                _, (kind, k, w), ep = min(cand, key=lambda x: x[0])
                T = z(Ytr) if kind == "w0" else (1 - w) * z(Ytr) + w * z(teacher(kind, k, all_rows, f"T_{space}_f{f}"))
                P = np.mean([predict(fit(Btr, T, space, s, ep)[0], Bte, space) for s in SEEDS], axis=0) * ys + ym
                for j, dim in enumerate(dims):
                    preds.append(pd.DataFrame(dict(participant_id=pid, video_id=vids[idx], outer_fold=int(f), input_condition=fam,
                                                   target_space=space, dimension=dim, y_true=Y[idx, j], y_pred=P[:, j], train_mean=mu[j])))
                sel.append(dict(participant_id=pid, outer_fold=int(f), target_space=space, condition=fam,
                                teacher=kind, k=k, w=w, epochs=ep))
        print(f"  {pid} fold {f} 완료 ({time.time() - t0:.0f}초)", flush=True)
    pred = pd.concat(preds, ignore_index=True)
    pred.to_csv(OUT / f"predictions_{pid}.tsv.gz", sep="\t", index=False, float_format="%.6g")
    pd.DataFrame(sel).to_csv(OUT / f"selected_{pid}.tsv", sep="\t", index=False)
    dim, _ = bb.evaluate(pred, sub)
    dim.to_csv(OUT / f"dimension_metrics_{pid}.tsv", sep="\t", index=False, float_format="%.5f")
    (OUT / f"run_info_{pid}.json").write_text(json.dumps(dict(hidden=HID, dropout=DROP, weight_decay=WD, lr=LR, max_epochs=EPOCHS,
                                                             ws=WS, ks=KS, seeds=SEEDS, seconds=round(time.time() - t0)), indent=1))
    print(dim.groupby(["target_space", "input_condition"], sort=False).r_oof.mean().round(4).to_string())
    print(f"{pid} 완료 ({time.time() - t0:.0f}초)")


def summarize():
    D = pd.concat([pd.read_csv(f, sep="\t") for f in sorted(OUT.glob("dimension_metrics_sub-*.tsv"))])
    S = pd.concat([pd.read_csv(f, sep="\t") for f in sorted(OUT.glob("selected_sub-*.tsv"))])
    lab = pd.read_csv(tc.rs.LAB_REPORT / "02_brain/dimension_metrics.tsv", sep="\t")
    lab = lab[lab.input_condition == "brain_roi469"]
    for space, g in D.groupby("target_space", sort=False):
        h = g.pivot_table(index=["participant_id", "dimension"], columns="input_condition", values="r_oof")
        per = h.groupby("participant_id").mean()
        base = lab[lab.target_space == space].groupby("participant_id").r_oof.mean()
        print(f"== {space} (선형 기준선 {base.mean():.4f})"); print(per.round(4).to_string())
        for a, b in [("mlp_content_wsel", "mlp_w0"), ("mlp_labelpca_wsel", "mlp_w0"), ("mlp_content_wsel", "mlp_labelpca_wsel")]:
            dl = per[a] - per[b]; dd = (h[a] - h[b]).groupby("dimension").mean()
            print(f"  {a} − {b}: 평균 {dl.mean():+.4f} (피험자 {dl.min():+.4f}~{dl.max():+.4f}, 증가 {(dl > 0).sum()}/5, 5명 평균 증가 차원 {(dd > 0).sum()}/{len(dd)})")
        dl = per["mlp_content_wsel"] - base
        print(f"  mlp_content_wsel − 선형 기준선: 평균 {dl.mean():+.4f} (피험자 {dl.min():+.4f}~{dl.max():+.4f}, 증가 {(dl > 0).sum()}/5)")
    print(S.groupby(["target_space", "condition"])[["w", "epochs"]].mean().round(2).to_string())
    edge = S.groupby(["target_space", "condition"]).epochs.apply(lambda x: ((x <= EVAL) | (x >= EPOCHS)).mean()).rename("epoch 범위 끝 비율")
    print(edge.round(2).to_string())
    print(S[S.condition != "mlp_w0"].groupby(["target_space", "condition"]).w.apply(lambda x: (x > 0).mean()).round(2).rename("w>0 비율").to_string())


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--sub"); ap.add_argument("--summarize", action="store_true")
    a = ap.parse_args()
    summarize() if a.summarize else run_subject(a.sub)
