#!/usr/bin/env python3
"""S4 특징 모델: 실제 시각 특징과 캡션 특징으로 정서를 맞히는 모델(T_VS, K1a, 정서어 제거판, 구역 제외) (04 S4, 01 E1~E6, H3, O6, O16, O17, K1a, 2026-11-06).

뇌 반응은 읽지 않는다. 결과는 사전 분석이고 뇌에 대한 결론으로 쓰지 않는다(E6, N43).

꼴(E2, O5): logit = a(v) + b(c) + U[(Av) ⊙ (Bc)]. a, b는 편향이 있는 선형이고 A, B, U는 편향 없는 선형이다. r = 0이면 더하기만 남는다.
선택(O16)
- 후보마다 epoch별 안쪽 검증 손실의 겹 평균 곡선이 가장 낮은 epoch(최대 300)를 그 후보의 epoch 수로 정한다.
- 그 epoch에서 안쪽 검증의 출력별 r을 평균하고 겹 평균이 가장 큰 후보를 고른다. y가 상수인 출력은 그 겹에서 모든 후보에서 빼고, 예측이 상수인 출력은 r = 0으로 센다(O6).
- 점수가 같으면 더 작은 r, 더 작은 weight decay를 고른다(O6). 조기 종료로 겹마다 멈추지 않는다.

과제
- tvs: 바깥 fold k. D_k 안쪽 5겹으로 고른 모델로 시험 fold 예측, K1 head 두 개(더하기판, 상호작용판), H2 학습 fold 4개 안쪽 4겹의 nested OOF 출력(E4).
- k1a: 14개 차원. 손실 MSE, sigmoid 없음, 정답은 D_k로 표준화. 더하기판과 상호작용판(K1a).
- noemo: 정서어 제거 캡션으로 같은 T_VS 선택과 시험 예측(D8, SI).
- zone: 구역 제외와 학습량 대조마다 그 학습 자료로 표준화와 선택을 다시 하고 구역 시험 영상을 예측(J3, 4-3).
- hkfinal: 6-3의 HK 최종 모델용 OOF 출력(E4, O7). fold 2~6 안쪽 5겹.

사용: s4_feature_model.py --task tvs --design-freeze <커밋> [--part 0/4] [--device cuda]
"""
import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")  # O32. 결정적 모드에 필요하다

import numpy as np
import pandas as pd
import torch
from torch import nn

import s4_common as c

RANKS = (0, 1, 2, 4, 8)  # E2
WEIGHT_DECAYS = (1e-4, 1e-3, 1e-2)  # E3
LR, BATCH, MAX_EPOCHS, SEED = 1e-3, 64, 300, 0  # O16, G13
CANDIDATES = [(r, wd) for r in RANKS for wd in WEIGHT_DECAYS]  # 이 순서가 O6의 동점 규칙이다
torch.use_deterministic_algorithms(True)


class FeatureModel(nn.Module):
    def __init__(self, dv, dc, n_out, r):
        super().__init__()
        self.r = r
        self.a, self.b = nn.Linear(dv, n_out), nn.Linear(dc, n_out)
        if r:
            self.A, self.B, self.U = nn.Linear(dv, r, bias=False), nn.Linear(dc, r, bias=False), nn.Linear(r, n_out, bias=False)

    def forward(self, v, cap):
        z = self.a(v) + self.b(cap)
        return z + self.U(self.A(v) * self.B(cap)) if self.r else z


@dataclass
class Spec:
    """학습 규칙. 시험에서만 값을 줄인다."""
    kind: str = "emotions"  # emotions: soft BCE, sigmoid. dimensions: MSE, 출력 그대로
    max_epochs: int = MAX_EPOCHS
    batch: int = BATCH
    lr: float = LR
    candidates: tuple = tuple(CANDIDATES)
    seed: int = SEED

    def loss(self, out, y):
        if self.kind == "emotions":
            return nn.functional.binary_cross_entropy_with_logits(out, y)
        return nn.functional.mse_loss(out, y)

    def predict(self, out):
        return torch.sigmoid(out) if self.kind == "emotions" else out


def _r_selection(pred, y, keep):
    """선택 계산용 출력별 r. keep은 y가 상수가 아닌 출력이다. 예측이 상수이면 0으로 센다(O6)."""
    if not torch.isfinite(pred).all():
        raise ValueError("예측에 NaN 또는 Inf가 있다. 상수 예측이 아니라 계산 실패다")
    if not keep.any():
        raise ValueError("검증 자료의 정답이 모두 상수라 선택 점수를 낼 수 없다")
    p, t = pred[:, keep] - pred[:, keep].mean(0), y[:, keep] - y[:, keep].mean(0)
    den = torch.sqrt((p**2).sum(0) * (t**2).sum(0))
    r = torch.where(den > 0, (p * t).sum(0) / den.clamp_min(1e-30), torch.zeros_like(den))
    return r.mean()


def train(spec, r, wd, tr, va=None, keep_preds=False, epochs=None, device="cpu"):
    """tr, va: (v, c, y) 텐서. 돌려주는 값: 모델, epoch별 검증 손실, epoch별 r 평균, epoch별 검증 출력(원하면)."""
    torch.manual_seed(spec.seed)
    g = torch.Generator().manual_seed(spec.seed)
    v, cap, y = tr
    model = FeatureModel(v.shape[1], cap.shape[1], y.shape[1], r).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=spec.lr, weight_decay=wd)
    n_epochs = epochs if epochs is not None else spec.max_epochs
    curve, score, preds = [], [], []
    keep = None if va is None else (va[2].amax(0) > va[2].amin(0))
    for _ in range(n_epochs):
        model.train()
        order = torch.randperm(len(v), generator=g).to(device)
        for i in range(0, len(v), spec.batch):
            b = order[i:i + spec.batch]
            opt.zero_grad(set_to_none=True)
            spec.loss(model(v[b], cap[b]), y[b]).backward()
            opt.step()
        if va is not None:
            model.eval()
            with torch.no_grad():
                out = model(va[0], va[1])
                if not torch.isfinite(out).all():
                    raise ValueError("검증 출력에 NaN 또는 Inf가 있다")
                curve.append(spec.loss(out, va[2]).item())
                score.append(_r_selection(spec.predict(out), va[2], keep).item())
                if keep_preds:
                    preds.append(out.cpu().numpy().astype(np.float32))
    if not all(torch.isfinite(x).all() for x in model.parameters()):
        raise ValueError("가중치에 NaN 또는 Inf가 있다")
    return model, np.array(curve), np.array(score), (np.stack(preds) if keep_preds else None)


def search(spec, data, device, keep_preds=False):
    """data: 겹 번호 -> (tr, va). 후보마다 곡선과 점수를 겹 평균해 표로 돌려준다."""
    folds = sorted(data)
    curves, scores, preds = [], [], {}
    for ci, (r, wd) in enumerate(spec.candidates):
        cu, sc = [], []
        for j in folds:
            _, cur, s, p = train(spec, r, wd, *data[j], keep_preds=keep_preds, device=device)
            cu.append(cur), sc.append(s)
            if keep_preds:
                preds[(ci, j)] = p
        curves.append(np.stack(cu)), scores.append(np.stack(sc))
    curves, scores = c.finite(np.stack(curves), "검증 손실"), c.finite(np.stack(scores), "선택 점수")  # 후보 × 겹 × epoch
    mean_curve = curves.mean(1)
    best = mean_curve.argmin(1)  # 같으면 앞선 epoch
    table = pd.DataFrame(spec.candidates, columns=["r", "weight_decay"])
    table["epochs"] = best + 1
    table["val_loss"] = mean_curve[np.arange(len(best)), best]
    table["val_r"] = scores[np.arange(len(best)), :, best].mean(1)
    return table, mean_curve, preds


def choose(table, ranks=None):
    """가장 큰 r 평균. 같으면 표의 앞쪽(작은 r, 작은 weight decay)이다(O6). ranks로 판을 나눈다(O17)."""
    t = table if ranks is None else table[table.r.isin(ranks)]
    if t.empty or not np.isfinite(t.val_r.to_numpy()).all():
        raise ValueError("유효한 선택 점수가 없다. 첫 후보로 넘어가지 않고 멈춘다")
    i = int(t.val_r.to_numpy().argmax())
    return t.iloc[i]


class Coordinates:
    """바깥 학습 자료로 맞춘 표준화(N3, H4)."""

    def __init__(self, v, cap, y=None):
        self.vm, self.vs = c.fit_standardizer(v)
        self.cm, self.cs = c.fit_standardizer(cap)
        self.ym, self.ys = (None, None) if y is None else c.fit_standardizer(y)

    def tensors(self, v, cap, y, device):
        yy = y if self.ym is None else (y - self.ym) / self.ys
        return tuple(torch.as_tensor(c.finite(x, "모델 입력"), dtype=torch.float32, device=device) for x in ((v - self.vm) / self.vs, (cap - self.cm) / self.cs, yy))

    def arrays(self):
        d = dict(visual_mean=self.vm, visual_std=self.vs, caption_mean=self.cm, caption_std=self.cs)
        if self.ym is not None:
            d.update(target_mean=self.ym, target_std=self.ys)
        return d


@dataclass
class Data:
    """split 순서의 개발 영상 자료."""
    ids: np.ndarray
    folds: np.ndarray
    v: np.ndarray
    cap: np.ndarray
    y: np.ndarray

    def mask(self, folds):
        return np.isin(self.folds, list(folds))


def inner_data(d, coord, rows, device):
    """rows(bool) 안에서 run fold마다 하나를 검증으로 두는 안쪽 겹."""
    out = {}
    for j in sorted(set(d.folds[rows].tolist())):
        tr, va = rows & (d.folds != j), rows & (d.folds == j)
        out[j] = (coord.tensors(d.v[tr], d.cap[tr], d.y[tr], device), coord.tensors(d.v[va], d.cap[va], d.y[va], device))
    return out


def refit(spec, row, d, coord, rows, device):
    tr = coord.tensors(d.v[rows], d.cap[rows], d.y[rows], device)
    model, *_ = train(spec, int(row.r), float(row.weight_decay), tr, epochs=int(row.epochs), device=device)
    return model


def predict(spec, model, d, coord, rows, device):
    vt, ct, _ = coord.tensors(d.v[rows], d.cap[rows], d.y[rows], device)
    model.eval()
    with torch.no_grad():
        out = model(vt, ct)
        return c.finite(out.cpu().numpy().astype(np.float32), "시험 출력"), c.finite(spec.predict(out).cpu().numpy().astype(np.float32), "시험 예측")


def nested_oof(spec, d, coord, rows, device):
    """E4, O16. 후보와 epoch 수를 안쪽 겹 평균으로 정하고, 고른 후보의 안쪽 모델이 각자 빠진 fold에 낸 예측을 모은다."""
    data = inner_data(d, coord, rows, device)
    table, curve, preds = search(spec, data, device, keep_preds=True)
    row = choose(table)
    ci, e = int(row.name), int(row.epochs) - 1
    ids, logit = [], []
    for j in sorted(data):
        ids.append(d.ids[rows & (d.folds == j)]), logit.append(preds[(ci, j)][e])
    ids, logit = np.concatenate(ids), np.concatenate(logit)
    order = np.argsort(ids)
    ids, logit = ids[order], logit[order]
    p_raw = 1 / (1 + np.exp(-logit.astype(np.float64)))  # 자르기 전 값(E4). 이 꼴은 sigmoid라 이미 0~1이다
    return dict(video_id=ids, logit=logit, p_raw=p_raw.astype(np.float32), p_clipped=np.clip(p_raw, 0, 1).astype(np.float32)), table, curve, row


def save_state(path, model, row, coord):
    torch.save(dict(state_dict={k: t.cpu() for k, t in model.state_dict().items()}, r=int(row.r), weight_decay=float(row.weight_decay), epochs=int(row.epochs), **{k: torch.as_tensor(v) for k, v in coord.arrays().items()}), path)


def task_tvs(spec, d, k, device, out):
    r = c.roles(k)
    dk = d.mask(r["dk"])
    coord = Coordinates(d.v[dk], d.cap[dk])  # 정답은 표준화하지 않는다(B3)
    table, curve, _ = search(spec, inner_data(d, coord, dk, device), device)
    table.to_csv(out / "selection_dk.tsv", sep="\t", index=False)
    np.save(out / "curves_dk.npy", curve)
    np.savez(out / "coordinates.npz", **coord.arrays())
    rows = dict(teacher_family=choose(table), additive=choose(table, [0]), interaction=choose(table, [x for x in RANKS if x]))
    json.dump({n: {x: float(v[x]) for x in ("r", "weight_decay", "epochs", "val_r")} for n, v in rows.items()}, open(out / "chosen.json", "w"), indent=1)
    models = {}
    for n in ("additive", "interaction"):
        models[n] = refit(spec, rows[n], d, coord, dk, device)
        save_state(out / f"head_{n}.pt", models[n], rows[n], coord)
    best = models["additive"] if int(rows["teacher_family"].r) == 0 else models["interaction"]
    te = d.mask([k])
    logit, p = predict(spec, best, d, coord, te, device)
    np.savez(out / "test_pred.npz", video_id=d.ids[te], logit=logit, p=p)
    oof, t4, c4, row4 = nested_oof(spec, d, coord, d.mask(r["train"]), device)
    np.savez(out / "oof.npz", **oof)
    t4.to_csv(out / "selection_oof.tsv", sep="\t", index=False)
    np.save(out / "curves_oof.npy", c4)
    return dict(oof_chosen={x: float(row4[x]) for x in ("r", "weight_decay", "epochs", "val_r")})


def task_k1a(spec, d, k, device, out):
    r = c.roles(k)
    dk = d.mask(r["dk"])
    coord = Coordinates(d.v[dk], d.cap[dk], d.y[dk])
    table, curve, _ = search(spec, inner_data(d, coord, dk, device), device)
    table.to_csv(out / "selection_dk.tsv", sep="\t", index=False)
    np.save(out / "curves_dk.npy", curve)
    np.savez(out / "coordinates.npz", **coord.arrays())
    te = d.mask([k])
    chosen, pred = {}, {"video_id": d.ids[te]}
    for n, ranks in (("additive", [0]), ("interaction", [x for x in RANKS if x])):
        row = choose(table, ranks)
        chosen[n] = {x: float(row[x]) for x in ("r", "weight_decay", "epochs", "val_r")}
        model = refit(spec, row, d, coord, dk, device)
        save_state(out / f"head_{n}.pt", model, row, coord)
        z, _ = predict(spec, model, d, coord, te, device)
        pred[f"{n}_z"], pred[f"{n}_score"] = z, z * coord.ys + coord.ym  # 정답 표준화를 되돌린 값(K1a)
    np.savez(out / "test_pred.npz", **pred)
    json.dump(chosen, open(out / "chosen.json", "w"), indent=1)
    return {}


def task_select_predict(spec, d, rows, test_rows, device, out):
    """구역 제외와 정서어 제거판. 그 학습 자료로 표준화와 선택을 다시 하고 시험 영상을 예측한다."""
    coord = Coordinates(d.v[rows], d.cap[rows])
    table, curve, _ = search(spec, inner_data(d, coord, rows, device), device)
    table.to_csv(out / "selection.tsv", sep="\t", index=False)
    np.save(out / "curves.npy", curve)
    row = choose(table)
    json.dump({x: float(row[x]) for x in ("r", "weight_decay", "epochs", "val_r")}, open(out / "chosen.json", "w"), indent=1)
    model = refit(spec, row, d, coord, rows, device)
    save_state(out / "model.pt", model, row, coord)
    logit, p = predict(spec, model, d, coord, test_rows, device)
    np.savez(out / "test_pred.npz", video_id=d.ids[test_rows], logit=logit, p=p)
    return {}


def task_hkfinal(spec, d, device, out):
    r = c.final_roles()
    coord = Coordinates(d.v, d.cap)  # 개발 영상 전체. 바깥 시험 fold가 없다
    oof, table, curve, row = nested_oof(spec, d, coord, d.mask(r["train"]), device)
    np.savez(out / "oof.npz", **oof)
    np.savez(out / "coordinates.npz", **coord.arrays())
    table.to_csv(out / "selection_oof.tsv", sep="\t", index=False)
    np.save(out / "curves_oof.npy", curve)
    return dict(oof_chosen={x: float(row[x]) for x in ("r", "weight_decay", "epochs", "val_r")})


def enumerate_tasks(task, split=None):
    if task in ("tvs", "k1a", "noemo"):
        return [dict(task=task, k=k, name=f"fold{k}") for k in range(1, c.N_FOLDS + 1)]
    if task == "hkfinal":
        return [dict(task=task, name="all")]
    if task == "zone":
        return [dict(task=task, block=b, k=k, kind=kind, name=f"block{b}_fold{k}_{kind}") for b in range(1, 6) for k in range(1, c.N_FOLDS + 1) for kind in ("excluded", "control")]
    raise SystemExit(task)


def input_paths(task):
    cap = {"caption_no_emotion": c.FEATURES / f"{c.CAPTION_NO_EMOTION}.npy"} if task == "noemo" else {"caption_target": c.FEATURES / f"{c.CAPTION_TARGET}.npy"}
    return {"visual_target": c.FEATURES / f"{c.VISUAL_TARGET}.npy", **cap, "labels": c.LABELS}


def load_data(task, split):
    ids = split.video_id.to_numpy()
    cap = c.CAPTION_NO_EMOTION if task == "noemo" else c.CAPTION_TARGET
    y, _ = c.load_scores(split, "dimensions" if task == "k1a" else "emotions")
    return Data(ids, split.fold.to_numpy(), c.load_rows(c.VISUAL_TARGET, ids, split), c.load_rows(cap, ids, split), y)


def run_one(t, spec, d, split, device, out, run):
    if c.done_or_new(out, run.key):
        print("건너뜀", out, flush=True)
        return
    with c.Atomic(out) as tmp:
        if t["task"] == "tvs":
            extra = task_tvs(spec, d, t["k"], device, tmp)
        elif t["task"] == "k1a":
            extra = task_k1a(spec, d, t["k"], device, tmp)
        elif t["task"] == "noemo":
            r = c.roles(t["k"])
            extra = task_select_predict(spec, d, d.mask(r["dk"]), d.mask([t["k"]]), device, tmp)
        elif t["task"] == "zone":
            train_ids, test_ids = c.zone_sets(split, t["block"], t["k"], t["kind"])
            extra = task_select_predict(spec, d, np.isin(d.ids, train_ids), np.isin(d.ids, test_ids), device, tmp)
        else:
            extra = task_hkfinal(spec, d, device, tmp)
        run.check()  # 저장 전에 코드와 입력이 시작 때와 같은지 다시 본다
        json.dump(dict(run.prov, task=t, **extra), open(tmp / "done.json", "w"), indent=1)
    print("저장", out, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, choices=["tvs", "k1a", "noemo", "zone", "hkfinal"])
    ap.add_argument("--design-freeze", default="")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--part", default="0/1", help="나눠 돌릴 때 i/n. 끝난 과제는 건너뛴다")
    a = ap.parse_args()
    c.guard(a.design_freeze)
    spec = Spec(kind="dimensions" if a.task == "k1a" else "emotions")
    run = c.Run(a.design_freeze, input_paths(a.task), task=a.task, lr=spec.lr, batch=spec.batch, max_epochs=spec.max_epochs, seed=spec.seed, candidates=spec.candidates, torch=torch.__version__)  # 읽기 전에 해시를 낸다
    split = c.load_split()
    d = load_data(a.task, split)
    run.check()  # 읽은 내용이 기록한 해시와 같음을 확인한다
    i, n = (int(x) for x in a.part.split("/"))
    tasks = enumerate_tasks(a.task, split)
    for t in tasks[i::n]:
        run_one(t, spec, d, split, a.device, c.OUT / a.task / t["name"], run)


if __name__ == "__main__":
    main()
