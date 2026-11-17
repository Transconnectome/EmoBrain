#!/usr/bin/env python3
"""S9 네트워크 교란의 모델 확장과 정서 head 입력 표현 저장 (01 6-4e (나), (다), 11/17 석진 님 승인). 다시 학습하지 않는다. GPU 추론.

모델(seed 0, 바깥 fold 6개): A-1, C-1, B-1, D-4(짝 모델 4개의 예측 평균), E-고정, E-학습.
  표현 비교의 기준으로 A-1 depth2, depth4(A-1과 같은 후보 설정, encoder block 수만 2, 4)의 표현도 저장한다.
교란: 6-4b와 같다. CAB-NP 13묶음의 입력을 같은 참가자, 같은 시험 fold의 다른 시험 영상 값으로 바꾼다. 20회.
  배정표는 s9_saved_models.donor_table(같은 seed 규칙)이라 6-4b의 A-1, C-1과 같은 배정이다. ROI 370개판은 하지 않는다.
  선형 입력층에서는 입력을 바꾼 것과 ROI token을 바꾼 것이 같다(s9_saved_models 머리말). 모델마다 첫 묶음, 첫 반복에서 입력을 직접 바꾼 결과와 같은지 확인한다.
  D-4는 짝 모델마다 그 모델의 token을 바꾸고 네 예측을 평균한다(S6 ensemble과 같은 평균).
  D-4 짝 j의 입력은 S6 짝 학습과 같게 encoder 2 j의 학습 영상으로 표준화한 자료(S.prepare_fold의 stats_videos, s6_train._inner_fold_head)에서 만든다.
  행은 바깥 fold 시험 행과 같은 (참가자, 영상)이고 같은 순서로 맞춘다. 그래서 배정표가 모든 모델에 같다.
확인: 다시 낸 원래 예측이 S6이 저장한 test_pred.npz와 같다(D-4는 짝마다, 그리고 네 짝 평균이 ensemble과 같다).
표현: 정서 query의 출력 o(행 × 34 × d, 정서마다의 선형층에 들어가는 값. E-고정, E-학습이 Multimodal Model에 맞춘 그 표현)를 행 × (34·d)로 저장한다.
저장(--out/outer_fold<k>_seed0/)
- pred.npz: participant, video_id(행 열쇠), unit_name(13묶음), donors(반복 × 행, 행 안 위치), <조건>_base(행 × 34 원래 예측)
- perturbed_<조건>.npy: 묶음 13 × 반복 20 × 행 × 34, float32 확률
- repr.npz: <이름>(행 × 34·d, float32). 이름은 조건, D-4는 조건|pair<k>, 기준은 depth2, depth4
사용: s9_perturb_models.py --s6-dir <S6 최종> --depth2-dir <s6_brain_depth2> --depth4-dir <s6_brain_depth4> --out <폴더> --design-freeze <커밋> [--folds 1,2] [--device cuda]
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch

import s4_common as c
import s6_common as S
import s6_model as M
import s6_train as T
import s9_saved_models as S9

CONDS = ("brain_only", "brain_decoded", "brain_only_featdec", "brain_frozen_feature_encoder", "brain_only_repr_frozen", "brain_only_repr_trained")
REPEATS = S9.PERTURB_REPEATS
CHUNK = 512


def submodels(root, k, cond, device):
    """돌려주는 값: [(폴더, 모델)], 비교할 저장 예측 파일. 짝 학습 조건은 짝 모델 4개와 ensemble."""
    fo = Path(root) / f"outer_fold{k}"
    sel = json.loads((fo / cond / "selected.json").read_text())
    d = fo / sel["seeds"]["0"]
    if S.CONDITIONS[cond].paired:
        paths, saved = sorted(d.glob("pair*/model.pt")), d / "ensemble" / "test_pred.npz"
        if len(paths) != 4:
            raise ValueError(f"{d}: 짝 모델이 4개가 아니다")
    else:
        paths, saved = [d / "model.pt"], d / "test_pred.npz"
    out = []
    for p in paths:
        m, meta = M.load_checkpoint(p, device)
        if meta["condition"] != cond or int(meta["seed"]) != 0:
            raise ValueError(f"{p}: 체크포인트의 조건이나 seed가 다르다")
        out.append((p.parent, m))
    return out, saved


def parts(m):
    if isinstance(m, M.FrozenEncoderModel):
        il, enc = m.feature_model.input_layer, m.feature_model.encoder
    elif type(m) is M.BrainModel:
        il, enc = m.input_layer, m.encoder
    else:
        raise ValueError(f"{type(m).__name__}: 이 분석이 다루지 않는 모델")
    if type(il) is not M.RoiInput:
        raise ValueError("token 교체는 선형 입력층에서만 입력 교체와 같다")
    return il, enc, m.readout


@torch.no_grad()
def tokens(m, fd, rows):
    il = parts(m)[0]
    return torch.cat([il(fd.batch(rows[j:j + CHUNK])) for j in range(0, len(rows), CHUNK)])


@torch.no_grad()
def head(m, Tk, want_o=False):
    _, enc, rd = parts(m)
    ps, os_ = [], []
    for j in range(0, len(Tk), CHUNK):
        out = rd(enc(Tk[j:j + CHUNK]))
        ps.append(out.z.sigmoid())
        if want_o:
            os_.append(out.o.flatten(1))
    return torch.cat(ps), (torch.cat(os_) if want_o else None)


def saved_p(path, fd, rows):
    z = np.load(path)
    key = {(p, int(v)): i for i, (p, v) in enumerate(zip(z["participant"].astype(str), z["video_id"]))}
    return np.asarray(z["p"], np.float64)[[key[(p, int(v))] for p, v in zip(fd.participant_names(rows), fd.row_video[rows])]]


@torch.no_grad()
def check_direct(m, fd, rows, donors, Tk, idx):
    """첫 참가자의 시험 행에서, 입력을 직접 바꾼 예측과 token을 바꾼 예측이 같은지."""
    part = fd.row_participant[rows]
    p0 = np.flatnonzero(part == 0)
    local = {g: i for i, g in enumerate(p0)}
    direct = m(S9.raw_perturbed_batch(fd, rows[p0], np.array([local[g] for g in donors[0][p0]]), idx)).z.sigmoid().double()
    Tp = Tk[p0].clone()
    Tp[:, idx] = Tk[torch.as_tensor(donors[0][p0], device=Tk.device)][:, idx]
    if not torch.allclose(direct, head(m, Tp)[0].double(), atol=1e-4):
        raise ValueError("token 교체가 입력 교체와 다르다")


def load_all(k, s6_dir, device):
    """s9_saved_models.load_fold와 같은 준비. 짝 모델의 자료를 다시 만들 원자료도 돌려준다."""
    split = c.load_split()
    plan = S.load_plan(f"outer_fold{k}", split)
    y, v, cap = T.load_known(split, plan)
    brains = S.load_brains(split, list(plan.train) + list(plan.val) + list(plan.test))
    fd = S.prepare_fold(brains, split, y, v, cap, plan, device=device)
    saved = np.load(Path(s6_dir) / f"outer_fold{k}" / "plan" / "standardization.npz")
    for pid, s in fd.voxel_stats.items():
        if not (np.array_equal(saved[f"voxel_mean:{pid}"], s["mean"]) and np.array_equal(saved[f"voxel_std:{pid}"], s["std"])):
            raise ValueError(f"fold {k} {pid}: 다시 만든 voxel 표준화가 S6에 저장한 것과 다르다")
    return split, plan, (brains, y, v, cap), fd


def pair_data(split, plan, raw, j, device, fd, rows):
    """D-4 짝 j의 자료(S6 _inner_fold_head와 같음)와, 바깥 시험 행 순서에 맞춘 그 자료의 행 번호."""
    brains, y, v, cap = raw
    hit = [(enc, head, rest) for jj, enc, head, rest in S.inner_plans(plan, split) if jj == j]
    if len(hit) != 1:
        raise ValueError(f"짝 {j}의 계획이 없다")
    _, head_plan, rest = hit[0]
    fdj = S.prepare_fold(brains, split, y, v, cap, head_plan, device=device, stats_videos=rest)
    rj = fdj.rows("test")
    pos = {key: i for i, key in enumerate(zip(fdj.participant_names(rj), fdj.row_video[rj].tolist()))}
    order = [pos[key] for key in zip(fd.participant_names(rows), fd.row_video[rows].tolist())]
    return fdj, rj[order]


@torch.no_grad()
def run_fold(k, s6_dir, ref_dirs, device, tmp):
    split, plan, raw, fd = load_all(k, s6_dir, device)
    rows = fd.rows("test")
    donors = S9.donor_table(fd, rows, k, REPEATS)
    units = [u for u in S9.units_table() if u[0] == "group"]
    if len(units) != 13:
        raise ValueError("묶음이 13개가 아니다")
    arrays = dict(participant=fd.participant_names(rows), video_id=fd.row_video[rows], unit_name=np.array([u[1] for u in units]), donors=donors)
    reprs, inputs = {}, {}
    for cond in CONDS:
        subs, saved = submodels(s6_dir, k, cond, device)
        toks, base = [], []
        for d, m in subs:
            inputs[f"{cond}|{d.name}"] = c.sha256(d / "model.pt")
            if S.CONDITIONS[cond].paired:
                fdu, ru = pair_data(split, plan, raw, int(d.name.removeprefix("pair")), device, fd, rows)
            else:
                fdu, ru = fd, rows
            Tk = tokens(m, fdu, ru)
            p, o = head(m, Tk, want_o=True)
            if len(subs) > 1 and not np.allclose(p.double().cpu().numpy(), saved_p(d / "test_pred.npz", fdu, ru), atol=1e-4):
                raise ValueError(f"{d}: 다시 낸 예측이 저장한 짝 예측과 다르다")
            check_direct(m, fdu, ru, donors, Tk, units[0][2])
            if fdu is not fd:
                del fdu
                torch.cuda.empty_cache()
            reprs[cond if len(subs) == 1 else f"{cond}|{d.name}"] = o.float().cpu().numpy()
            toks.append(Tk)
            base.append(p)
        b = torch.stack(base).mean(0)
        if not np.allclose(b.double().cpu().numpy(), saved_p(saved, fd, rows), atol=1e-4):
            raise ValueError(f"{cond} fold {k}: 다시 낸 예측이 S6 저장 예측과 다르다")
        arrays[f"{cond}_base"] = b.float().cpu().numpy()
        pv = np.empty((len(units), REPEATS, len(rows), b.shape[1]), np.float32)
        for t in range(REPEATS):
            dt = torch.as_tensor(donors[t], device=toks[0].device)
            donor_toks = [Tk[dt] for Tk in toks]
            for u, (_, _, idx) in enumerate(units):
                preds = []
                for (_, m), Tk, Td in zip(subs, toks, donor_toks):
                    keep = Tk[:, idx].clone()
                    Tk[:, idx] = Td[:, idx]
                    preds.append(head(m, Tk)[0])
                    Tk[:, idx] = keep
                pv[u, t] = torch.stack(preds).mean(0).float().cpu().numpy()
        np.save(tmp / f"perturbed_{cond}.npy", pv)
        print(f"fold {k} {cond} 끝", flush=True)
        del toks, subs
        torch.cuda.empty_cache()
    for name, root in ref_dirs.items():
        subs, saved = submodels(root, k, "brain_only", device)
        (d, m), = subs
        inputs[name] = c.sha256(d / "model.pt")
        p, o = head(m, tokens(m, fd, rows), want_o=True)
        if not np.allclose(p.double().cpu().numpy(), saved_p(saved, fd, rows), atol=1e-4):
            raise ValueError(f"{name} fold {k}: 다시 낸 예측이 저장 예측과 다르다")
        reprs[name] = o.float().cpu().numpy()
    np.savez(tmp / "pred.npz", **arrays)
    np.savez(tmp / "repr.npz", **reprs)
    return inputs


def main(argv=None):
    ap = argparse.ArgumentParser(description="S9 네트워크 교란 모델 확장과 정서 head 입력 표현")
    ap.add_argument("--s6-dir", required=True)
    ap.add_argument("--depth2-dir", required=True)
    ap.add_argument("--depth4-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", required=True)
    ap.add_argument("--folds", default="")
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args(argv)
    c.guard(a.design_freeze)
    folds = [int(x) for x in a.folds.split(",")] if a.folds else list(range(1, 7))
    refs = {"depth2": a.depth2_dir, "depth4": a.depth4_dir}
    for k in folds:
        out = Path(a.out) / f"outer_fold{k}_seed0"
        if (out / "done.json").exists():
            print("이미 있음", out, flush=True)
            continue
        started = time.time()
        with c.Atomic(out) as tmp:
            inputs = run_fold(k, a.s6_dir, refs, a.device, tmp)
            info = dict(stage="S9 네트워크 교란 모델 확장과 표현", fold=k, seed=0, conditions=list(CONDS), references=refs, repeats=REPEATS, s6_dir=str(a.s6_dir),
                        model_sha256=inputs, design_freeze=a.design_freeze, code_commit=c.START_HEAD, code_dirty=c.START_DIRTY, elapsed_seconds=round(time.time() - started, 1))
            (tmp / "done.json").write_text(json.dumps(info, indent=1, ensure_ascii=False))
        print("저장", out, f"{time.time() - started:.0f}초", flush=True)
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
