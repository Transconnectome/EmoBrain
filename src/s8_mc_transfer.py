#!/usr/bin/env python3
"""S8 6-3. HK에서 학습한 공유 모델을 MC 시청 자료에 옮긴다 (01 6-3, 04 S8, O29, O30, 11/15 석진 님).

- HK 최종 모델(final_for_mc 분할, 개발 영상 전체, seed 3개)의 공유 가중치(encoder, query, feature head, emotion head, e(r))를 모두 고정하고,
  MC 참가자마다 ROI 입력층 W(s, r), b(s, r)만 새로 학습한다. 참가자 이름은 HK와 겹치지 않게 mc-01 ~ mc-06으로 둔다.
- 입력층 학습 자료: MC 시청 학습 세션 2,108개(manifests/s2/mc_blocks.tsv의 input_train, input_val). 검증 run은 O29(5, 10, ... 번째 run, 표의 input_val).
  시험 영상 72개와 그 중복 영상은 학습과 선택에 들어가지 않는다(시작할 때 확인한다). excluded_test_runs 행은 읽지 않는다.
- 표준화: MC voxel은 그 참가자의 학습, 검증 block 통계(O29, C5). feature 목표는 HK 최종 모델의 D9 통계(O30, plan/standardization.npz).
- 손실과 학습 규칙: 조건의 원래 손실(A-1 soft BCE, C-1 soft BCE + λ(시각 MSE + 캡션 MSE)/2, λ와 r은 HK 최종 모델의 값).
  learning rate는 HK 최종 모델의 값, voxel 뽑기와 batch, epoch, patience는 HK와 같다(G13). 조기 종료는 검증 총손실, 선택은 검증 정서 r 평균(0-2, O6).
- 후보: 입력층 weight decay는 HK 입력층 후보(S7)와 같은 INPUT_WDS 가운데 lr × weight decay < 1인 것(O29, s6_common.candidates와 같은 제외 규칙).
  후보별 시험 예측은 저장만 하고 선택에 쓰지 않는다(N24).
- 시험: 72개 영상의 반복 block을 평균한 반응만 넣는다(정할 것 9). 평균한 반복 수가 manifests/s2/mc_test_repeats.tsv와 다르면 멈춘다.
  사람 평정은 채점에만, 실제 feature는 decoded features 채점에만 쓴다. 시험 때 모델 입력은 뇌 반응뿐이다.
- 고정한 encoder의 dropout은 학습 중 켜 둔다(HK에서 학습할 때와 같은 상태). 이 선택은 done.json에 남긴다.
- B-1, D-1, D-3, D-4(11/17 석진 님. "입력층은 HK에서 배울 때와 같은 것을 맞히게 한다"를 A-1~D-4에 똑같이 적용)
  - B-1: A-1, C-1과 같다(입력층 하나, B-1의 원래 손실 soft BCE + λ feature MSE, 검증 정서 r로 weight decay 선택).
  - encoder 2의 입력층: HK에서 encoder 2를 학습한 목표(Vision, Caption feature MSE)와 선택 기준(검증 feature MSE)을 그대로 쓴다. MC 정서 평정은 쓰지 않는다.
    D-1, D-3이 쓰는 encoder 2(전체)는 참가자마다 한 번 맞춰 둘이 함께 쓰고(<out>/encoder2/seed<k>/mc-0X), D-4의 짝 encoder 2 다섯은 짝마다 맞춘다(<out>/encoder2_pair<j>/...).
  - D-3, D-4: 뇌 입력은 encoder 2로만 들어간다. 정서 head는 HK 값 그대로 고정한다. 그래서 MC 입력층을 맞출 때 정서 평정을 쓰지 않는다. D-4의 예측은 짝 다섯의 예측 평정 평균이다.
  - D-1: 입력층이 둘이다. encoder 2 쪽은 위와 같고, 정서 encoder 쪽은 그 encoder 2를 고정한 채 D-1의 원래 손실로 맞추고 검증 정서 r로 weight decay를 고른다.
    HK에서는 학습 행의 v̂₂, ĉ₂를 fold 밖 encoder 2에서 받았지만 MC 입력층 학습에서는 같은 참가자 자료로 맞춘 encoder 2의 값을 그대로 쓴다(한계로 기록).
  - D 조건의 예측 파일은 test_pred_final.npz이고 done.json의 pred_file에 적는다.
출력: <out>/<조건>/seed<k>/mc-0X/{selection.tsv, test_pred_<후보>.npz, input_layer.pt, done.json}
확인용 실행(11/15): --plan outer_fold1로 바깥 fold 모델을 옮겨 오류, 메모리, 시간만 본다. 출력 폴더를 따로 두고 결과로 쓰지 않는다.
사용(run worktree의 src에서): python s8_mc_transfer.py --final <s6_brain_final_for_mc> --out <s8_mc> --conditions brain_only,brain_decoded --seeds 0,1,2
                               --participants 01,02,03,04,05,06 --design-freeze <커밋> [--device cuda]
"""
import argparse
import dataclasses
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

import s4_common as c
import s5_common as d5
import s6_common as S
import s6_model as M
import s6_train as T

MC = ("01", "02", "03", "04", "05", "06")
BRAIN_CONDITIONS = ("brain_only", "brain_decoded", "brain_only_featdec")  # 6-3의 A-1, C-1(상호작용 head)과 11/17에 더한 B-1. 입력층 하나, 조건의 원래 손실
D_CONDITIONS = ("brain_decoded_sep", "brain_features_only", "brain_frozen_feature_encoder")  # 11/17 석진 님. D-1, D-3, D-4
CONDITIONS = BRAIN_CONDITIONS + D_CONDITIONS
INPUT_WDS = (0.01, 0.1, 1.0, 10.0, 100.0, 1000.0)  # O29. HK 입력층 weight decay 후보(11/13 grid)와 같다
MC_BLOCKS = c.S2 / "mc_blocks.tsv"
MC_REPEATS = c.S2 / "mc_test_repeats.tsv"
ID_MAP = c.S2 / "hk_mc_id_map.tsv"
TRAIN_ROLES = {"input_train": 0, "input_val": 1}


def response_path(s):
    return d5.PM / f"MindCaptioning/sub-{s}/v2_qc/sub-{s}_blocks_common36_qc_runz.npy"


def roi_path(s):
    return d5.ROI_VOXELS / f"mc_sub-{s}.npz"


def wds_for(lr):
    return [w for w in INPUT_WDS if lr * w < 1.0]


# ---------- MC 자료 ----------

def mc_rows(s, blocks, repeats, idmap, mc72):
    """그 참가자의 학습, 검증 block과 시험 block. 읽기 전에 표만으로 경계를 확인한다."""
    t = blocks[blocks.participant == f"sub-{s}"]
    tv = t[t.role.isin(list(TRAIN_ROLES))].sort_values("qc_row").reset_index(drop=True)
    te = t[t.role == "test_72"].sort_values("qc_row").reset_index(drop=True)
    if not len(tv) or not len(te):
        raise ValueError(f"sub-{s}: 학습 또는 시험 block이 없다")
    if not tv.video_id.is_unique:
        raise ValueError(f"sub-{s}: 학습 세션에서 한 영상이 두 번 나온다")
    m = idmap.set_index("mc_video_id")
    if m.loc[tv.video_id].is_mc_test_72.any() or set(tv.canonical_id) & set(mc72):
        raise ValueError(f"sub-{s}: 학습, 검증 영상에 MC 시험 72개나 그 중복이 있다")
    test_ids = sorted(te.video_id.unique())
    if len(test_ids) != 72 or not m.loc[test_ids].is_mc_test_72.all():
        raise ValueError(f"sub-{s}: 시험 영상이 MC 72개가 아니다")
    n = te.groupby("video_id").size()
    want = repeats[repeats.participant == f"sub-{s}"].set_index("video_id").n_repeats
    if not n.sort_index().equals(want.sort_index().astype(n.dtype)):
        raise ValueError(f"sub-{s}: 시험 반복 수가 mc_test_repeats.tsv와 다르다")
    return tv, te, test_ids


def load_mc(s, blocks, repeats, idmap, mc72, raw=None, roi=None):
    """반응 배열에서 허용한 행만 읽는다. 돌려주는 값: 학습, 검증 X(block별), 시험 X(영상별 반복 평균), 영상 번호, ROI 위치."""
    tv, te, test_ids = mc_rows(s, blocks, repeats, idmap, mc72)
    z = np.load(roi_path(s) if roi is None else roi)
    columns, offsets = z["columns"], z["offsets"]
    unique = np.unique(columns)
    raw = np.load(response_path(s), mmap_mode="r") if raw is None else raw
    if raw.shape[1] != int(z["n_columns"]):
        raise ValueError(f"sub-{s}: 반응 배열의 열 수가 ROI 표와 다르다")
    allowed = np.concatenate([tv.qc_row.to_numpy(), te.qc_row.to_numpy()])
    read = lambda rows: np.concatenate([d5.read_rows(raw, rows[i:i + 64], allowed)[:, unique] for i in range(0, len(rows), 64)]).astype(np.float32)
    X_tv = c.finite(read(tv.qc_row.to_numpy()), f"MC sub-{s} 학습 반응")
    X_te_blocks = c.finite(read(te.qc_row.to_numpy()), f"MC sub-{s} 시험 반응")
    X_te = np.stack([X_te_blocks[(te.video_id == v).to_numpy()].mean(0) for v in test_ids]).astype(np.float32)  # 정할 것 9. 남은 반복의 평균
    pos = [np.searchsorted(unique, columns[offsets[i]:offsets[i + 1]]) for i in range(len(offsets) - 1)]
    return dict(X_tv=X_tv, video_tv=tv.video_id.to_numpy(), role_tv=tv.role.map(TRAIN_ROLES).to_numpy(), X_te=X_te, video_te=np.array(test_ids),
                n_repeats=te.groupby("video_id").size().loc[test_ids].to_numpy(), positions=pos, n_columns=len(columns))


def targets(video_tv, video_te, idmap, split, stats, mc72_table):
    """사람 평정과 feature. 학습, 검증 영상은 HK 개발 영상 번호로 기존 함수로 읽고, 시험 72개는 채점용으로만 따로 읽는다.
    feature는 HK 최종 모델의 D9 통계로 표준화한다(O30)."""
    m = idmap.set_index("mc_video_id")
    hk_ids = m.loc[video_tv].hk_dev_video_id.astype(int).to_numpy()
    rows = split.set_index("video_id").loc[hk_ids].reset_index()
    y_tv = c.load_scores(rows, "emotions")[0]
    v_tv = c.load_rows(c.VISUAL_TARGET, hk_ids, split)
    c_tv = c.load_rows(c.CAPTION_TARGET, hk_ids, split)
    t72 = mc72_table.set_index("mc_video_id")
    canon = t72.loc[video_te].canonical_stimulus_id.to_numpy()
    labels = pd.read_csv(c.LABELS).set_index("stim_num_int")
    cols = pd.read_csv(c.LABEL_MAP, sep="\t").score_col.tolist()
    y_te = c.finite(labels.loc[canon, cols].to_numpy(np.float32), "MC 시험 사람 평정")
    first = np.array([int(str(x).split(",")[0]) for x in t72.loc[video_te].hk_analysis_videos])
    feats = {}
    for name in (c.VISUAL_TARGET, c.CAPTION_TARGET):
        a = np.load(c.FEATURES / f"{name}.npy", mmap_mode="r")
        if a.shape[0] != 2196:
            raise ValueError(f"{name}: 영상이 2,196개가 아니다")
        feats[name] = c.finite(np.asarray(a[first - 1], np.float32), f"MC 시험 {name}")
    zv = lambda x: (x - stats["visual_mean"]) / stats["visual_std"]
    zc = lambda x: (x - stats["caption_mean"]) / stats["caption_std"]
    return dict(y_tv=y_tv, v_tv=zv(v_tv).astype(np.float32), c_tv=zc(c_tv).astype(np.float32), y_te=y_te,
                v_te=feats[c.VISUAL_TARGET], c_te=feats[c.CAPTION_TARGET])


def mc_fold(pid, data, tg, stats, device):
    """MC 참가자 한 명의 FoldData. 행 순서는 학습, 검증 block 다음 시험 영상이다. 시험 행은 bank 밖(-1)이라 정답이 학습 경로로 들어가지 않는다."""
    m, sd, constant = S.voxel_standardizer(data["X_tv"])  # O29, C5. 2,108개(학습, 검증) 통계

    def norm(X):  # prepare_fold와 같은 순서. 값이 변하지 않는 voxel은 0이다
        z = (np.asarray(X, np.float64) - m) / sd
        z[:, constant] = 0.0
        return z.astype(np.float32)
    x = np.concatenate([norm(data["X_tv"]), norm(data["X_te"])])
    n_tv, n_te = len(data["X_tv"]), len(data["X_te"])
    role = np.concatenate([data["role_tv"], np.full(n_te, 2)])
    video = np.concatenate([data["video_tv"], data["video_te"]])
    train_ids = data["video_tv"][data["role_tv"] == 0].tolist()
    val_ids = data["video_tv"][data["role_tv"] == 1].tolist()
    plan = S.Plan(f"mc_{pid}", 0, train_ids, val_ids, data["video_te"].tolist())
    t = lambda a: torch.as_tensor(np.asarray(a, np.float32), device=device)
    bank = data["video_tv"].tolist()
    row_bank = np.concatenate([np.arange(n_tv), np.full(n_te, -1)])
    y_train_mean = tg["y_tv"][data["role_tv"] == 0].mean(0)
    return S.FoldData(plan, [pid], {pid: t(x)}, {pid: torch.as_tensor(np.concatenate(data["positions"]), dtype=torch.long, device=device)},
                      {pid: [len(p) for p in data["positions"]]}, {pid: dict(mean=m, std=sd, constant=constant)},
                      np.zeros(len(x), int), np.arange(len(x)), video, role, bank, row_bank, t(tg["y_tv"]), t(tg["v_tv"]), t(tg["c_tv"]),
                      dict(stats), t(y_train_mean), None, device)


# ---------- 모델 ----------

SHARED_SKIP = ("input_layer.weights.", "input_layer.input_bias.")


def adapt(hk_model, pid, counts):
    """HK 최종 모델의 구조로 MC 참가자 한 명의 모델을 만든다. 입력층 W, b만 학습하고 나머지는 HK 값을 넣어 고정한다."""
    spec = {k: v for k, v in hk_model.spec.items() if k != "kind"}
    if hk_model.spec.get("kind") != "brain":
        raise ValueError("MC 전이는 뇌 모델(A-1, C-1)만 받는다")
    spec["voxel_counts"] = {pid: list(counts)}
    model = M.BrainModel(**spec)
    hk, own = hk_model.state_dict(), model.state_dict()
    extra = {k for k in hk if not k.startswith(SHARED_SKIP)} ^ {k for k in own if not k.startswith(SHARED_SKIP)}
    if extra:
        raise ValueError(f"HK 모델과 MC 모델의 공유 가중치 이름이 다르다: {sorted(extra)[:5]}")
    for k in own:
        if not k.startswith(SHARED_SKIP):
            if hk[k].shape != own[k].shape:
                raise ValueError(f"{k}: 크기가 다르다")
            own[k] = hk[k].clone()
    model.load_state_dict(own)
    trainable = {f"input_layer.weights.{pid}", f"input_layer.input_bias.{pid}"}
    for n, p in model.named_parameters():
        p.requires_grad_(n in trainable)
    return model


def frozen_digest(model):
    """학습하지 않는 가중치 전체의 해시(requires_grad가 꺼진 파라미터와 buffer). 학습 전후로 같아야 한다."""
    trainable = {n for n, q in model.named_parameters() if q.requires_grad}
    h = hashlib.sha256()
    for name, x in sorted(model.state_dict().items()):
        if name not in trainable:
            h.update(name.encode())
            h.update(x.detach().cpu().numpy().tobytes())
    return h.hexdigest()


def input_state(model):
    return {k: v.detach().cpu().clone() for k, v in model.state_dict().items() if k.startswith(SHARED_SKIP)}


def fit_encoder2(hk_fe, fe_cand, seed, pid, fd, spec, out_dir, log=print):
    """encoder 2(HK에서 feature 손실로만 학습)의 MC 입력층. 같은 손실, 검증 feature MSE로 weight decay를 고른다. 돌려주는 값: (입력층을 넣은 모델, 고른 weight decay)."""
    lr = float(fe_cand["lr"])
    rows, best = [], None
    for wd in wds_for(lr):
        cw = dict(fe_cand, input_wd=float(wd))
        T.seed_everything(seed)
        model = adapt(hk_fe, pid, fd.voxel_counts[pid]).to(fd.device)
        before = frozen_digest(model)
        started = time.time()
        try:
            res = T.fit(model, fd, spec, lr=lr, input_wd=float(wd), feature_wd=None, loss_fn=T.make_loss("feature_encoder", cw, fd), forward=T.brain_forward(fd), seed=seed,
                        val_fn=T.feature_val_loss(fd, spec.batch))
        except T.Diverged as e:
            rows.append(dict(input_wd=wd, val_score=np.nan, val_loss=np.nan, best_epoch=None, diverged=True, reason=str(e), seconds=time.time() - started))
            continue
        if frozen_digest(model) != before:
            raise SystemExit("고정한 HK encoder 2 가중치가 학습 중에 바뀌었다")
        rows.append(dict(input_wd=wd, val_score=res.val_score, val_loss=res.val_loss, best_epoch=res.best_epoch, diverged=False, reason="", seconds=time.time() - started))
        log(f"  encoder 2 seed{seed} {pid} wd {wd}: 검증 feature MSE {res.val_loss:.4f}, epoch {res.best_epoch}")
        if best is None or (res.val_score, -wd) > (best[0], -best[1]):
            best = (res.val_score, wd, input_state(model))
    if best is None:
        raise SystemExit(f"encoder 2 seed{seed} {pid}: 모든 후보가 발산했다")
    out_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out_dir / "selection.tsv", sep="\t", index=False)
    torch.save(best[2], out_dir / "input_layer.pt")
    return load_encoder2(hk_fe, pid, fd, out_dir), best[1]


def load_encoder2(hk_fe, pid, fd, folder):
    model = adapt(hk_fe, pid, fd.voxel_counts[pid])
    own = model.state_dict()
    own.update(torch.load(Path(folder) / "input_layer.pt", map_location="cpu"))
    model.load_state_dict(own)
    return M.freeze(model).to(fd.device)


def encoder2_cached(hk_fe, fe_cand, seed, pid, fd, spec, folder, run_key, log=print):
    """참가자마다 한 번만 맞춘다. 같은 실행 번호의 결과가 있으면 읽는다."""
    folder = Path(folder)
    if c.done_or_new(folder, run_key):
        done = json.loads((folder / "done.json").read_text())
        return load_encoder2(hk_fe, pid, fd, folder), float(done["chosen_input_wd"])
    with c.Atomic(folder) as tmp:
        model, wd = fit_encoder2(hk_fe, fe_cand, seed, pid, fd, spec, tmp, log)
        json.dump(dict(run_key=run_key, participant=pid, seed=seed, encoder2_candidate=fe_cand, chosen_input_wd=wd), open(tmp / "done.json", "w"), indent=1, default=str)
    return load_encoder2(hk_fe, pid, fd, folder), wd


def copy_head(new, hk, skip_prefix):
    """HK 모델에서 skip_prefix로 시작하지 않는 가중치(정서 head 등)를 그대로 옮긴다. 이름과 크기가 다르면 멈춘다."""
    own, src = new.state_dict(), hk.state_dict()
    if {k for k in own if not k.startswith(skip_prefix)} != {k for k in src if not k.startswith(skip_prefix)}:
        raise ValueError("HK 모델과 새 모델의 head 가중치 이름이 다르다")
    for k in own:
        if not k.startswith(skip_prefix):
            if own[k].shape != src[k].shape:
                raise ValueError(f"{k}: 크기가 다르다")
            own[k] = src[k].clone()
    new.load_state_dict(own)
    return new


def run_unit_d1(hk_model, hk_meta, fe, seed, pid, fd, spec, out_dir, log=print):
    """D-1의 정서 encoder 입력층. encoder 2(MC 입력층까지 맞춘 것)는 고정하고 D-1의 원래 손실로 맞추며 검증 정서 r로 고른다."""
    cand = dict(hk_meta["candidate"])
    lr = float(cand["lr"])
    forward = T.brain_forward(fd)
    rows, best = [], None
    for wd in wds_for(lr):
        cw = dict(cand, input_wd=float(wd))
        T.seed_everything(seed)
        model = M.SeparateDecodedModel(adapt(hk_model.main, pid, fd.voxel_counts[pid]), fe).to(fd.device)
        before = frozen_digest(model)
        started = time.time()
        try:
            res = T.fit(model, fd, spec, lr=lr, input_wd=float(wd), feature_wd=None, loss_fn=T.make_loss("brain_decoded_sep", cw, fd), forward=forward, seed=seed,
                        restore_fn=T.total_val_loss("brain_decoded_sep", cw, fd, forward, spec.batch))
        except T.Diverged as e:
            rows.append(dict(input_wd=wd, val_score=np.nan, val_loss=np.nan, best_epoch=None, diverged=True, reason=str(e), seconds=time.time() - started))
            continue
        if frozen_digest(model) != before:
            raise SystemExit("고정한 가중치가 학습 중에 바뀌었다")
        rows.append(dict(input_wd=wd, val_score=res.val_score, val_loss=res.val_loss, best_epoch=res.best_epoch, diverged=False, reason="", seconds=time.time() - started))
        log(f"  D-1 seed{seed} {pid} wd {wd}: 검증 r {res.val_score:.4f}, epoch {res.best_epoch}")
        if best is None or (res.val_score, -wd) > (best[0], -best[1]):
            model.eval()
            with torch.no_grad():
                z = T.collect(model, fd.rows("test"), forward, spec.batch, ("z",))["z"]
            best = (res.val_score, wd, {k: v.detach().cpu().clone() for k, v in model.state_dict().items() if k.startswith("main." + SHARED_SKIP[0]) or k.startswith("main." + SHARED_SKIP[1])}, z)
    if best is None:
        raise SystemExit(f"D-1 seed{seed} {pid}: 모든 후보가 발산했다")
    pd.DataFrame(rows).to_csv(out_dir / "selection.tsv", sep="\t", index=False)
    torch.save(best[2], out_dir / "input_layer_main.pt")
    return best[1], best[3]


@torch.no_grad()
def predict_z(model, fd, spec):
    model.eval()
    return T.collect(model, fd.rows("test"), T.brain_forward(fd), spec.batch, ("z",))["z"]


def shared_digest(model):
    """고정한 가중치만의 해시. 학습 전후로 같아야 한다."""
    h = hashlib.sha256()
    for name, t in sorted(model.state_dict().items()):
        if not name.startswith(SHARED_SKIP):
            h.update(name.encode())
            h.update(t.detach().cpu().numpy().tobytes())
    return h.hexdigest()


def pearson_cols(p, y):
    pc, yc = p - p.mean(0), y - y.mean(0)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (pc * yc).sum(0) / np.sqrt((pc ** 2).sum(0) * (yc ** 2).sum(0))


def run_unit(hk_model, hk_meta, condition, seed, pid, fd, spec, out_dir, log=print):
    """한 조건, 한 seed, 한 참가자. 후보마다 입력층을 학습하고 검증 r로 고른다."""
    cand = dict(hk_meta["candidate"])
    lr = float(cand["lr"])
    forward = T.brain_forward(fd)
    names = ("z", "v_hat", "c_hat") if condition in ("brain_decoded", "brain_only_featdec") else ("z",)
    rows, best = [], None
    test = fd.rows("test")
    for wd in wds_for(lr):
        cw = dict(cand, input_wd=float(wd))
        T.seed_everything(seed)
        model = adapt(hk_model, pid, fd.voxel_counts[pid]).to(fd.device)
        before = shared_digest(model)
        started = time.time()
        try:
            res = T.fit(model, fd, spec, lr=lr, input_wd=float(wd), feature_wd=None, loss_fn=T.make_loss(condition, cw, fd), forward=forward, seed=seed,
                        restore_fn=T.total_val_loss(condition, cw, fd, forward, spec.batch))
        except T.Diverged as e:
            rows.append(dict(input_wd=wd, val_score=np.nan, val_loss=np.nan, best_epoch=None, diverged=True, reason=str(e), seconds=time.time() - started))
            log(f"  {condition} seed{seed} {pid} wd {wd}: 발산")
            continue
        if shared_digest(model) != before:
            raise SystemExit("고정한 HK 가중치가 학습 중에 바뀌었다")
        model.eval()
        with torch.no_grad():
            o = T.collect(model, test, forward, spec.batch, names)
        np.savez(out_dir / f"test_pred_wd{wd:g}.npz", video_id=fd.row_video[test], z=o["z"].numpy(), p=torch.sigmoid(o["z"]).numpy(),
                 **({"v_hat": o["v_hat"].numpy(), "c_hat": o["c_hat"].numpy()} if "v_hat" in o else {}))
        rows.append(dict(input_wd=wd, val_score=res.val_score, val_loss=res.val_loss, best_epoch=res.best_epoch, diverged=False, reason="", seconds=time.time() - started))
        log(f"  {condition} seed{seed} {pid} wd {wd}: 검증 r {res.val_score:.4f}, epoch {res.best_epoch}")
        if best is None or (res.val_score, -wd) > (best[0], -best[1]):  # O6. 같으면 작은 값
            best = (res.val_score, wd, {k: v.detach().cpu().clone() for k, v in model.state_dict().items() if k.startswith(SHARED_SKIP)})
    if best is None:
        raise SystemExit(f"{condition} seed{seed} {pid}: 모든 후보가 발산했다")
    pd.DataFrame(rows).to_csv(out_dir / "selection.tsv", sep="\t", index=False)
    torch.save(best[2], out_dir / "input_layer.pt")
    return best[1], rows


def state_hash(model):
    h = hashlib.sha256()
    for name, x in sorted(model.state_dict().items()):
        h.update(name.encode())
        h.update(x.detach().cpu().numpy().tobytes())
    return h.hexdigest()[:16]


def run_unit_dgroup(cond, hk_models, hk_meta, fe_cand, seed, pid, fd, spec, out_dir, root, design_freeze, enc_inputs, log=print):
    """D-1, D-3, D-4 한 단위. encoder 2 입력층은 참가자마다 캐시해 함께 쓴다. 돌려주는 값: (기록할 weight decay, done.json에 더할 값). out_dir에 test_pred_final.npz를 쓴다."""
    def enc(hk_fe, name):
        folder = Path(root) / name / f"seed{seed}" / pid
        run = S.Run(design_freeze, enc_inputs, task="mc_encoder2", fe_digest=state_hash(hk_fe), fe_candidate=fe_cand, participant=pid, seed=seed, input_wds=list(INPUT_WDS), spec=dataclasses.asdict(spec))
        return encoder2_cached(hk_fe, fe_cand, seed, pid, fd, spec, folder, run.key, log)
    if cond == "brain_features_only":
        (hk,) = hk_models
        fe, wd = enc(hk.feature_model, "encoder2")
        z = predict_z(copy_head(M.FeatureHeadModel(fe, hk.rank), hk, "feature_model."), fd, spec)
        chosen, extra = wd, dict(encoder2_input_wd=wd)
    elif cond == "brain_frozen_feature_encoder":
        ps, wds = [], {}
        for j, hk in hk_models:
            fe, wd = enc(hk.feature_model, f"encoder2_pair{j}")
            ps.append(torch.sigmoid(predict_z(copy_head(M.FrozenEncoderModel(fe), hk, "feature_model."), fd, spec)))
            wds[f"pair{j}"] = wd
        p = torch.stack(ps).mean(0)
        z = torch.log(p) - torch.log1p(-p)
        chosen, extra = None, dict(encoder2_input_wd=wds, n_pairs=len(ps))
    elif cond == "brain_decoded_sep":
        (hk,) = hk_models
        fe, wd = enc(hk.feature_model, "encoder2")
        chosen, z = run_unit_d1(hk, hk_meta, fe, seed, pid, fd, spec, out_dir, log)
        extra = dict(encoder2_input_wd=wd)
    else:
        raise ValueError(cond)
    test = fd.rows("test")
    np.savez(out_dir / "test_pred_final.npz", video_id=fd.row_video[test], z=z.numpy(), p=torch.sigmoid(z).numpy())
    return chosen, extra


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--final", required=True, help="HK 최종 모델 결과 폴더(S6_OUT=s6_brain_final_for_mc)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--conditions", default=",".join(CONDITIONS))
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--participants", default=",".join(MC))
    ap.add_argument("--plan", default="final_for_mc", help="옮길 HK 모델의 분할. 본 실행은 final_for_mc. 확인용 실행만 outer_fold<k>를 준다(결과로 쓰지 않음)")
    ap.add_argument("--design-freeze", default="")
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    c.guard(a.design_freeze)
    conditions = [x for x in a.conditions.split(",") if x]
    if set(conditions) - set(CONDITIONS):
        raise SystemExit(f"MC 전이 조건은 {CONDITIONS}다")
    seeds = [int(x) for x in a.seeds.split(",")]
    parts = [x for x in a.participants.split(",") if x]
    if set(parts) - set(MC):
        raise SystemExit("MC 참가자는 01~06이다")
    if a.plan != "final_for_mc" and not a.plan.startswith("outer_fold"):
        raise SystemExit("--plan은 final_for_mc나 outer_fold<k>다")
    final = Path(a.final) / a.plan
    stats = dict(np.load(final / "plan" / "standardization.npz"))
    stats = {k: stats[k] for k in ("visual_mean", "visual_std", "caption_mean", "caption_std")}
    blocks, repeats, idmap = (pd.read_csv(p, sep="\t") for p in (MC_BLOCKS, MC_REPEATS, ID_MAP))
    mc72_table = pd.read_csv(d5.MC72, sep="\t")
    mc72 = S.mc_video_ids()
    split = c.load_split()
    spec = S.Spec()
    hk = {}
    for cond in conditions:
        sel = json.loads((final / cond / "selected.json").read_text())
        for seed in seeds:
            rel = sel["seeds"].get(str(seed))
            if rel is None:
                raise SystemExit(f"{cond}: seed {seed}의 HK 최종 모델이 없다")
            if S.CONDITIONS[cond].paired:  # D-4. 짝 모델마다(pair<j>/model.pt)
                pairs = sorted((final / rel).glob("pair*/model.pt"))
                if len(pairs) != S.N_PAIRS_FINAL:
                    raise SystemExit(f"{cond}: 짝 모델이 {S.N_PAIRS_FINAL}개가 아니다({len(pairs)})")
                loaded = [(int(q.parent.name.removeprefix("pair")), *M.load_checkpoint(q, device="cpu")) for q in pairs]
                hk[(cond, seed)] = (final / rel, [(j, m) for j, m, _ in loaded], loaded[0][2])
            else:
                ckpt = final / rel / "model.pt"
                m, meta = M.load_checkpoint(ckpt, device="cpu")
                hk[(cond, seed)] = (ckpt, m if cond in BRAIN_CONDITIONS else [m], meta)
    fe_cand = None
    if set(conditions) & set(D_CONDITIONS):
        fe_cand = json.loads((final / "feature_encoder" / "selected.json").read_text())["candidate"]
    for s in parts:
        pid = f"mc-{s}"
        fd = data = tg = None
        for cond in conditions:
            for seed in seeds:
                ckpt, hk_model, hk_meta = hk[(cond, seed)]
                out_dir = Path(a.out) / cond / f"seed{seed}" / pid
                hk_paths = {f"hk_pair{j}": ckpt / f"pair{j}" / "model.pt" for j, _ in hk_model} if S.CONDITIONS[cond].paired else {"hk_checkpoint": ckpt}
                inputs = {**hk_paths, "hk_standardization": final / "plan" / "standardization.npz", "mc_blocks": MC_BLOCKS, "mc_repeats": MC_REPEATS,
                          "id_map": ID_MAP, "mc72": d5.MC72, "response": response_path(s), "roi": roi_path(s), "code_s8": Path(__file__).resolve()}
                run = S.Run(a.design_freeze, inputs, task="mc_transfer", hk_plan=a.plan, condition=cond, seed=seed, participant=pid, input_wds=list(INPUT_WDS), spec=dataclasses.asdict(spec))
                if c.done_or_new(out_dir, run.key):
                    print(f"끝난 단위 건너뜀 {out_dir}", flush=True)
                    continue
                started = time.time()
                if fd is None:  # 참가자마다 한 번만 읽는다
                    data = load_mc(s, blocks, repeats, idmap, mc72)
                    tg = targets(data["video_tv"], data["video_te"], idmap, split, stats, mc72_table)
                    fd = mc_fold(pid, data, tg, stats, a.device)
                with c.Atomic(out_dir) as tmp:
                    if cond in BRAIN_CONDITIONS:
                        chosen, rows = run_unit(hk_model, hk_meta, cond, seed, pid, fd, spec, tmp, log=lambda m: print(m, flush=True))
                        pred_file, extra = f"test_pred_wd{chosen:g}.npz", {}
                    else:
                        enc_inputs = {k: v for k, v in inputs.items() if not k.startswith(("hk_checkpoint", "hk_pair"))}
                        chosen, extra = run_unit_dgroup(cond, hk_model, hk_meta, fe_cand, seed, pid, fd, spec, tmp, a.out, a.design_freeze, enc_inputs, log=lambda m: print(m, flush=True))
                        pred_file = "test_pred_final.npz"
                    np.savez(tmp / "scoring.npz", video_id=data["video_te"], y=tg["y_te"], vision=tg["v_te"], caption=tg["c_te"], n_repeats=data["n_repeats"],
                             visual_mean=stats["visual_mean"], visual_std=stats["visual_std"], caption_mean=stats["caption_mean"], caption_std=stats["caption_std"])
                    p = np.load(tmp / pred_file)["p"]
                    r = pearson_cols(p, tg["y_te"])
                    run.check()
                    json.dump(dict(run.prov, condition=cond, seed=seed, participant=pid, hk_candidate=hk_meta["candidate"], chosen_input_wd=chosen, pred_file=pred_file, **extra,
                                   n_train=int((data["role_tv"] == 0).sum()), n_val=int((data["role_tv"] == 1).sum()), n_test=len(data["video_te"]),
                                   test_mean_r=float(np.nanmean(r)), n_constant=int(np.isnan(r).sum()), frozen_dropout="train", seconds=time.time() - started),
                              open(tmp / "done.json", "w"), indent=1, default=str)
                print(f"저장 {out_dir} 고른 weight decay {chosen}", flush=True)

if __name__ == "__main__":
    main()
