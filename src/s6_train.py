#!/usr/bin/env python3
"""S6 뇌 모델 학습 (04 S6, 01 5-A, G7~G16, H2, L9, M1, N3, N24, O1, O5, O6, O31, O32, 2026-11-07).

바깥 fold k가 시험, 다음 fold가 H2 검증, 나머지 4개가 학습이다. 후보는 seed 0으로 고르고 고른 설정으로 seed 1, 2를 더 학습한다(L9). 고른 모델을 그대로 시험한다.
조기 종료와 되돌릴 epoch는 검증 total loss(학습 손실과 같은 식, 정서 항의 목표는 실제 y, patience 30)로 정하고, 선택은 실제 y에 대한 정서별 r 평균이다(0-2, O6, 11/10 total_val_loss).
시험 영상의 사람 평정과 feature는 읽지 않는다(load_known). 시험 성능은 S10이 저장한 예측으로 낸다. 후보별 시험 예측도 저장하지만 선택에는 쓰지 않는다(N24).

사용: s6_train.py --plan outer_fold1 --conditions brain_only,brain_decoded --config manifests/s6/run_config.json --design-freeze <커밋> [--device cuda]
      s6_train.py --weight-counts 32,64,128  (F8의 표. 뇌 반응을 읽지 않고 ROI 표만 읽는다)

저장 형식 (S9, S10이 읽는다). 모두 OUT = <output_root>/s6_brain 아래다.
<plan>/plan/
    done.json: 실행 번호(run_key), 코드 커밋, 입력 해시, 설정(M1)
    plan.json: train, val, test 영상 번호
    rows.npz: participant, video_id, role(0 학습, 1 검증, 2 시험). 행 순서
    standardization.npz: voxel_mean:<참가자>, voxel_std:<참가자>, visual_mean, visual_std, caption_mean, caption_std. H2 학습 fold 4개의 통계(N3)
<plan>/<조건>/selection.tsv: 후보마다 d, input_wd, lr, lam, alpha, rank, feature_wd, candidate_id, val_score, val_loss, best_epoch, source_condition(0 후보의 출처)
<plan>/<조건>/selected.json: candidate(고른 값), zero_selected(G10), source_condition, seeds(seed -> 결과 폴더의 상대 경로), rows(선택표), run_key
<plan>/<조건>/<candidate_id>_seed<s>/
    done.json: M1의 기록 + condition, candidate, seed, best_epoch, val_loss, val_score, n_epochs, parameter_counts, 시간, GPU 메모리
    model.pt: s6_model.load_checkpoint로 읽는다. 선택되지 않은 후보는 지운다(설정 keep_candidate_checkpoints로 남길 수 있다)
    parameter_groups.json: 파라미터마다 weight decay 묶음(G13)
    history.tsv: epoch, train_loss, val_emotion_bce(검증 정서 soft BCE), val_loss(조기 종료 기준. 정서 항만 있는 조건은 val_emotion_bce와 같다)
    val_pred.npz: participant, video_id, logit(sigmoid 전), p. 고른 epoch의 값
    test_pred.npz: 같은 꼴(시험이 있는 분할만). 후보마다 저장한다(N24)
    shuffle.json: 대조군의 순열과 그 seed(O1)
    representation_stats.npz, teacher.json: E-고정, E-학습. 중간 표현의 평균과 표준편차, 짝지은 Multimodal Model의 체크포인트 해시
    outputs/ (고른 설정의 seed마다, seed 폴더는 selected.json의 seeds를 따른다)
        done.json
        test_outputs.npz: participant, video_id, logit, p, g(ROI 경로의 점수)
        decoded_test.npz, decoded_val.npz: participant, video_id, v_hat, c_hat. 학습 fold 4개의 D9 눈금. K1은 s6_common.to_k1_head로 옮긴다(N3)
        attention_emotion_test.npy: 시험 행 × head 4 × 정서 34 × token. attention_feature_test.npy: 시험 행 × head 4 × 2(시각, 캡션) × token. 행 순서는 test_outputs와 같다
        decoding_accuracy.tsv: participant, split(train, val), target(vision, caption), mse, mean_dim_r, n_constant_dims (B, C, D 묶음과 encoder 2, 5-0의 남는 주의)

재현성(O32): Python, NumPy, PyTorch의 seed와 자료 순서를 실행 seed로 고정한다. 결정적 모드에서 지원되지 않는 연산은 오류로 멈추므로 비결정 연산 목록은 비어 있다. GPU에서는 아직 돌려 보지 않았다.
"""
import argparse
import copy
import json
import os
import random
import time
from dataclasses import asdict, dataclass
from pathlib import Path

os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")  # O32. 결정적 모드에 필요하다

import numpy as np
import pandas as pd
import torch
from torch.nn import functional as F

import s4_common as c
import s5_common as d5
import s6_common as S
import s6_model as M
from s6_model import ac


def seed_everything(seed):
    """O32."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def soft_bce(z, target):
    """G7, N4. 행과 정서에 같은 가중치를 둔다."""
    return F.binary_cross_entropy_with_logits(z, target)


def validation_loss(z, y):
    """조기 종료 기준(G13, O6). y는 항상 검증 자료의 실제 사람 평정이다."""
    return soft_bce(z, y).item()


def brain_forward(fd):
    """뇌 모델의 forward. 입력은 뇌 반응뿐이다(0절)."""
    return lambda model, rows: model(fd.batch(rows))


def oof_forward(fd, oof):
    """11/9. 학습 행에는 fold 밖(OOF) encoder 2의 v̂₂, ĉ₂를 넣고, 검증과 시험 행은 고정한 encoder 2를 그대로 돌린다. 한 묶음에 둘이 섞이면 멈춘다."""
    v_all, c_all, is_train = oof["v"], oof["c"], oof["is_train"]

    def f(model, rows):
        idx = torch.as_tensor(np.asarray(rows), dtype=torch.long)
        t = is_train[idx]
        if bool(t.all()):
            return model(fd.batch(rows), fixed=(v_all[idx.to(v_all.device)], c_all[idx.to(c_all.device)]))
        if not bool(t.any()):
            return model(fd.batch(rows))
        raise ValueError("학습 행과 다른 행이 한 묶음에 섞였다")
    return f


def multimodal_forward(fd):
    return lambda model, rows: model(fd.batch(rows), *fd.multimodal_inputs(rows))


@torch.no_grad()
def collect(model, rows, forward, batch, names=("z",)):
    """행 순서대로 출력을 모은다. 호출하는 쪽이 eval 상태를 책임진다."""
    if model.training:
        raise ValueError("평가 값은 eval 상태에서만 낸다")
    out = {n: [] for n in names}
    for i in range(0, len(rows), batch):
        o = forward(model, rows[i:i + batch])
        for n in names:
            out[n].append(getattr(o, n).cpu())
    return {n: torch.cat(v) for n, v in out.items()}


def make_loss(condition, cand, fd, shuffle=None, teacher=None):
    """01 5-A의 손실. 학습 행에서만 부른다(FoldData.train_target이 확인한다)."""
    cfg = S.CONDITIONS[condition]
    alpha, lam = cand["alpha"], cand["lam"]
    if cfg.target == "stimulus_shuffled" and shuffle is None or cfg.features == "shuffled" and shuffle is None:
        raise ValueError("대조군에는 O1의 순열이 필요하다")

    def loss(out, rows):
        if cfg.feature_only:  # D-1~D-4의 encoder 2. 정서를 학습하지 않는다
            v, cap = fd.feature_targets(rows)
            return (F.mse_loss(out.v_hat, v) + F.mse_loss(out.c_hat, cap)) / 2
        target = fd.train_target(rows, cfg.target, alpha, shuffle)
        if cfg.representation:
            o_t = teacher.o[torch.as_tensor(teacher.position[rows], device=teacher.o.device)]
            return soft_bce(out.z, target) + lam * F.mse_loss((out.o - teacher.mean) / teacher.std, (o_t - teacher.mean) / teacher.std)
        if cfg.features == "none":
            return soft_bce(out.z, target)
        if cfg.features == "shuffled":
            return ac.shuffled_scene_pair_loss(out, target, shuffle, fd.row_video[rows].tolist(), fd.bank_ids, fd.vision_bank, fd.caption_bank, lambda_feat=lam)[0].L
        v, cap = fd.feature_targets(rows)
        return ac.decoding_loss(out, target, v, cap, lambda_feat=lam, condition="decoded_feature_readout" if cfg.decoded else "auxiliary_feature_decoding").L
    return loss


@dataclass
class FitResult:
    best_epoch: int
    val_loss: float
    val_score: float
    n_epochs: int
    history: pd.DataFrame


class Diverged(ValueError):
    """학습이 발산했다(손실이 NaN 또는 Inf). G13(11/8): 설정 후보 고르기(seed 0)에서는 그 후보만 기록하고 건너뛴다.
    고른 설정의 seed 1, 2에서 나면 seed를 빼지 않고 멈춘다."""


NONFINITE = ("must be nonempty and finite", "NaN 또는 Inf")  # 수치 실패를 알리는 검사 문구. shape, 자료 경계 오류와 구별한다


def numeric(step, what):
    """학습 중 계산 하나. 출력이나 중간값이 NaN, Inf가 되어 난 오류만 Diverged로 바꾼다(Codex 0a36925 필수 1). 다른 오류는 그대로 낸다."""
    try:
        return step()
    except Diverged:
        raise
    except ValueError as e:
        if any(m in str(e) for m in NONFINITE):
            raise Diverged(f"{what}: {e}") from e
        raise


def check_finite_state(model, what):
    for name, p in model.named_parameters():
        if not torch.isfinite(p).all():
            raise Diverged(f"{what}: 가중치 {name}에 NaN 또는 Inf가 있다")
        if p.grad is not None and not torch.isfinite(p.grad).all():
            raise Diverged(f"{what}: 기울기 {name}에 NaN 또는 Inf가 있다")


def feature_val_loss(fd, batch):
    """encoder 2의 조기 종료와 선택 기준. 검증 영상의 feature MSE((Vision MSE + Caption MSE) / 2)다."""
    val = fd.rows("val")
    v, cap = (t.cpu() for t in fd.feature_targets(val))

    def score(model):
        o = collect(model, val, brain_forward(fd), batch, ("v_hat", "c_hat"))
        return float(((o["v_hat"] - v) ** 2).mean() + ((o["c_hat"] - cap) ** 2).mean()) / 2
    return score


def total_val_loss(condition, cand, fd, forward, batch, teacher=None):
    """11/10 구현(석진 님 결정: 되돌리는 기준을 학습 손실과 같게). 검증 행에 학습 손실과 같은 식을 적용한 값으로 조기 종료하고 되돌린다.
    정서 항의 목표는 실제 사람 평정이다. distillation과 대조군의 섞은 목표는 학습 행에서만 만든다(0-2, train_target). 그래서 그 항은 빠진다.
    feature 항(B, C, D-1, D-2)과 representation 항(E)은 같은 λ로 더한다. feature 짝 섞기 대조군은 검증 영상의 원래 feature를 쓴다(audition_codex
    apply_shuffled_scene_pairs: 검증과 시험은 원래 목표). 정서 항만 있는 조건(A-1, A-2, D-3, D-4 등)과 encoder 2는 None을 돌려준다(기존 기준과 같은 식).
    선택 점수(검증 정서별 r 평균)는 바꾸지 않는다."""
    cfg = S.CONDITIONS[condition]
    if cfg.feature_only or (cfg.features == "none" and not cfg.representation):
        return None
    if cfg.representation and (teacher is None or teacher.o_val is None):
        raise ValueError("representation 조건의 검증 손실에는 검증 행의 Multimodal Model 중간 표현이 필요하다")
    val = fd.rows("val")
    y = fd.y(val)
    lam = cand["lam"]
    v_all, c_all = fd.feature_targets(val) if cfg.features != "none" else (None, None)
    mode = "decoded_feature_readout" if cfg.decoded and cfg.features == "actual" else "auxiliary_feature_decoding"

    def score(model):
        total = 0.0
        with torch.no_grad():
            for i in range(0, len(val), batch):
                rows, t = val[i:i + batch], y[i:i + batch]
                out = forward(model, rows)
                if cfg.representation:
                    o_t = teacher.o_val[i:i + batch]
                    loss = soft_bce(out.z, t) + lam * F.mse_loss((out.o - teacher.mean) / teacher.std, (o_t - teacher.mean) / teacher.std)
                else:
                    loss = ac.decoding_loss(out, t, v_all[i:i + batch], c_all[i:i + batch], lambda_feat=lam, condition=mode).L
                total += loss.item() * len(rows)
        return total / len(val)
    return score


def fit(model, fd, spec, *, lr, input_wd, feature_wd, loss_fn, forward, seed, on_epoch=None, val_fn=None, restore_fn=None):
    """G13, O6. AdamW, batch 64, 최대 300 epoch, patience 30, warmup 없음. 가장 낮은 epoch의 가중치로 되돌린다. 같은 값이면 앞선 epoch다.
    val_fn: encoder 2의 feature MSE(조기 종료와 선택 모두). restore_fn: 정서 조건의 검증 total loss(조기 종료만, 11/10). 없으면 검증 정서 soft BCE."""
    if val_fn is not None and restore_fn is not None:
        raise ValueError("val_fn과 restore_fn은 함께 주지 않는다")
    train, val = fd.rows("train"), fd.rows("val")
    y_val = fd.y(val).cpu()
    optimizer = torch.optim.AdamW(M.parameter_groups(model, lr, input_wd, feature_wd))
    generator = torch.Generator().manual_seed(seed)  # 자료 순서(O32)
    best_loss, best_epoch, best_state = float("inf"), 0, None
    history = []
    for epoch in range(1, spec.max_epochs + 1):
        model.train()
        order = train[torch.randperm(len(train), generator=generator).numpy()]
        total = 0.0
        for i in range(0, len(order), spec.batch):
            rows = order[i:i + spec.batch]
            optimizer.zero_grad(set_to_none=True)
            loss = numeric(lambda: loss_fn(forward(model, rows), rows), f"epoch {epoch} 학습")
            if not torch.isfinite(loss):
                raise Diverged(f"epoch {epoch}: 학습 손실이 NaN 또는 Inf다")
            loss.backward()
            check_finite_state(model, f"epoch {epoch} backward")  # 기울기가 비유한이면 가중치를 바꾸기 전에 멈춘다
            optimizer.step()
            check_finite_state(model, f"epoch {epoch} update")
            total += loss.item() * len(rows)
        model.eval()
        row = dict(epoch=epoch, train_loss=total / len(order))
        if val_fn is not None:  # encoder 2는 feature MSE로 멈춘다
            val_loss = numeric(lambda: val_fn(model), f"epoch {epoch} 검증")
        else:
            z = numeric(lambda: collect(model, val, forward, spec.batch)["z"], f"epoch {epoch} 검증")
            row["val_emotion_bce"] = validation_loss(z, y_val)
            val_loss = numeric(lambda: restore_fn(model), f"epoch {epoch} 검증") if restore_fn is not None else row["val_emotion_bce"]
        if not np.isfinite(val_loss):
            raise Diverged(f"epoch {epoch}: 검증 손실이 NaN 또는 Inf다")
        history.append(dict(row, val_loss=val_loss))
        if on_epoch is not None:
            on_epoch(epoch, model, val_loss)
        if val_loss < best_loss:
            best_loss, best_epoch = val_loss, epoch
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
        elif epoch - best_epoch >= spec.patience:
            break
    model.load_state_dict(best_state)
    model.eval()
    if val_fn is not None:  # 점수가 클수록 좋도록 MSE의 부호를 바꾼다(select_best)
        return FitResult(best_epoch, best_loss, -best_loss, len(history), pd.DataFrame(history))
    z = collect(model, val, forward, spec.batch)["z"]
    score = S.validation_score(z.sigmoid().numpy(), y_val.numpy(), fd.participant_names(val))
    return FitResult(best_epoch, best_loss, score, len(history), pd.DataFrame(history))


class Teacher:
    """E-고정, E-학습의 Multimodal Model 하나(G16). 고정하고, 학습 행의 중간 표현과 그 표준화 통계를 미리 낸다.
    통계는 Multimodal Model이 학습한 4개 fold의 행에서 내고 MSE 계산에만 쓴다(O5)."""

    def __init__(self, path, fd, batch):
        self.sha256 = c.sha256(path)
        self.model, _ = M.load_checkpoint(path, fd.device)
        M.freeze(self.model)
        self.digest = M.state_digest(self.model)
        rows = fd.rows("train")
        o = collect(self.model, rows, multimodal_forward(fd), batch, ("o",))["o"]
        mean, std = c.fit_standardizer(o.numpy().reshape(len(o), -1))
        shape = o.shape[1:]
        self.o = o.to(fd.device)
        self.mean = torch.as_tensor(mean.reshape(shape), dtype=torch.float32, device=fd.device)
        self.std = torch.as_tensor(std.reshape(shape), dtype=torch.float32, device=fd.device)
        self.position = np.full(len(fd.row_role), -1)
        self.position[rows] = np.arange(len(rows))
        val = fd.rows("val")  # 11/10. 검증 total loss의 representation 항. 통계는 위의 학습 행 통계를 그대로 쓴다
        self.o_val = collect(self.model, val, multimodal_forward(fd), batch, ("o",))["o"].to(fd.device)


def _json(obj, path):
    Path(path).write_text(json.dumps(obj, indent=1, ensure_ascii=False, default=float))


class FoldRunner:
    """한 분할의 조건들을 순서대로 돌린다. 끝난 결과는 같은 실행 번호일 때만 건너뛴다(s4_common.done_or_new)."""

    def __init__(self, fd, split, run, spec, config, root, mc_ids=None):
        if spec.seeds[0] != 0:
            raise ValueError("후보는 seed 0으로 고른다(L9)")
        self.fd, self.split, self.run, self.spec, self.config, self.root = fd, split, run, spec, config, Path(root)
        self.mc_ids = mc_ids
        self.teachers, self.shuffles, self.feature_encoders = {}, {}, {}
        self.cells = S.load_roi_cells(fd.voxel_counts) if config.tokenizer == "roi_cells" else None  # 11/9 입력층 점검의 칸 번호
        self.raw = None  # 11/9. (brains, y, vision, caption). fold 밖 encoder 2와 짝 학습의 자료를 다시 준비할 때 쓴다. main이 채운다
        self.oofs = {}  # seed -> fold 밖 encoder 2의 출력과 체크포인트
        self.trained = []  # 이번 실행에서 실제로 학습한 (조건, 후보, seed). 시험에서 횟수를 대조한다
        self.write_plan()

    def write_plan(self):
        path = self.root / "plan"
        if c.done_or_new(path, self.run.key):
            return
        fd = self.fd
        with c.Atomic(path) as tmp:
            _json(asdict(fd.plan), tmp / "plan.json")
            np.savez(tmp / "rows.npz", participant=fd.participant_names(np.arange(len(fd.row_role))), video_id=fd.row_video, role=fd.row_role)
            np.savez(tmp / "standardization.npz", **fd.feature_stats, **{f"voxel_mean:{p}": s["mean"] for p, s in fd.voxel_stats.items()}, **{f"voxel_std:{p}": s["std"] for p, s in fd.voxel_stats.items()}, **{f"voxel_constant:{p}": s["constant"] for p, s in fd.voxel_stats.items()})
            _json(self.run.prov, tmp / "done.json")

    def shuffle(self, seed):
        """O1. 바깥 fold와 seed마다 하나다. 후보가 달라도 같다."""
        if seed not in self.shuffles:
            self.shuffles[seed] = S.shuffle_plan(self.split, self.fd.plan, seed, self.mc_ids)
        return self.shuffles[seed]

    def teacher(self, seed):
        if seed not in self.teachers:
            sel = self.selected("multimodal")
            self.teachers[seed] = Teacher(self.root / sel["seeds"][str(seed)] / "model.pt", self.fd, self.spec.batch)
        return self.teachers[seed]

    def feature_encoder(self, seed):
        """D-1~D-4의 encoder 2. 같은 seed의 feature_encoder 선택을 읽어 고정한다. 학습 한 번마다 복사해 쓴다."""
        if seed not in self.feature_encoders:
            sel = self.selected("feature_encoder")
            path = self.root / sel["seeds"][str(seed)] / "model.pt"
            model, _ = M.load_checkpoint(path, self.fd.device)
            M.freeze(model)
            self.feature_encoders[seed] = dict(model=model, sha256=c.sha256(path), digest=M.state_digest(model))
        return self.feature_encoders[seed]

    def _inner_fold(self, plan):
        if self.raw is None:
            raise ValueError("fold 밖 encoder 2를 만들 원자료가 없다(FoldRunner.raw)")
        brains, y, v, cap = self.raw
        return S.prepare_fold(brains, self.split, y, v, cap, plan, device=self.fd.device, mc_ids=self.mc_ids)

    def oof(self, seed):
        """11/9 석진 님. 학습 fold 4개를 하나씩 뺀 encoder 2 네 개(같은 seed, 전체 encoder 2가 고른 learning rate, 검증 feature MSE로 조기 종료).
        j번째가 뺀 fold의 v̂₂, ĉ₂를 원래 단위로 되돌린 뒤 바깥 fold의 통계로 다시 표준화해 학습 행 순서로 모은다(Stimulus Model의 nested OOF와 같은 구조)."""
        if seed in self.oofs:
            return self.oofs[seed]
        fd = self.fd
        cand = self.selected("feature_encoder")["candidate"]
        key = {k: i for i, k in enumerate(zip(fd.participant_names(np.arange(len(fd.row_video))), fd.row_video.tolist()))}
        train_rows = fd.rows("train")
        V = torch.full((len(fd.row_video), M.VISUAL_DIM), float("nan"))
        C = torch.full((len(fd.row_video), M.CAPTION_DIM), float("nan"))
        encoders = []
        for j, enc_plan, head_plan, rest in S.inner_plans(fd.plan, self.split):
            path = self.root / "feature_encoder_oof" / f"seed{seed}" / f"inner{j}"
            if not c.done_or_new(path, self.run.key):
                fdj = self._inner_fold(enc_plan)
                started = time.time()
                seed_everything(seed)
                model = S.build_model("feature_encoder", cand, fdj.voxel_counts, self.config.tokenizer, self.config.voxel_sampling).to(fd.device)  # 11/10. 전체 encoder 2와 같은 입력층
                result = fit(model, fdj, self.spec, lr=cand["lr"], input_wd=cand["input_wd"], feature_wd=None, loss_fn=make_loss("feature_encoder", cand, fdj), forward=brain_forward(fdj), seed=seed, val_fn=feature_val_loss(fdj, self.spec.batch))
                held = fdj.rows("test")
                o = collect(model, held, brain_forward(fdj), self.spec.batch, ("v_hat", "c_hat"))
                st, ft = fdj.feature_stats, fd.feature_stats
                v = M.to_head_scale(o["v_hat"].numpy().astype(np.float64), st["visual_mean"], st["visual_std"], ft["visual_mean"], ft["visual_std"])
                cc = M.to_head_scale(o["c_hat"].numpy().astype(np.float64), st["caption_mean"], st["caption_std"], ft["caption_mean"], ft["caption_std"])
                with c.Atomic(path) as tmp:
                    M.save_checkpoint(tmp / "model.pt", model, condition="feature_encoder", candidate=cand, seed=seed, best_epoch=result.best_epoch, held_fold=int(j))
                    np.savez(tmp / "held.npz", participant=fdj.participant_names(held), video_id=fdj.row_video[held], v_hat=v.astype(np.float32), c_hat=cc.astype(np.float32))
                    result.history.to_csv(tmp / "history.tsv", sep="\t", index=False)
                    self.run._check_code()
                    _json(dict(self.run.prov, condition="feature_encoder_oof", candidate=cand, seed=seed, held_fold=int(j), n_train_videos=len(rest), n_held_videos=len(head_plan.train), best_epoch=result.best_epoch, val_loss=result.val_loss, **c.timing(started)), tmp / "done.json")
                self.trained.append(("feature_encoder_oof", f"inner{j}", seed))
                print("저장", path, f"epoch {result.best_epoch}/{result.n_epochs}", flush=True)
                del fdj, model
            z = np.load(path / "held.npz")
            for name, vid, vv, cv in zip(z["participant"], z["video_id"], z["v_hat"], z["c_hat"]):
                i = key[(str(name), int(vid))]
                V[i], C[i] = torch.as_tensor(vv), torch.as_tensor(cv)
            model, _ = M.load_checkpoint(path / "model.pt", fd.device)
            encoders.append(dict(fold=int(j), model=M.freeze(model), sha256=c.sha256(path / "model.pt"), digest=M.state_digest(model), head_plan=head_plan, stats_videos=rest))
        is_train = torch.zeros(len(fd.row_video), dtype=torch.bool)
        is_train[torch.as_tensor(train_rows)] = True
        if torch.isnan(V[is_train]).any() or torch.isnan(C[is_train]).any():
            raise ValueError("fold 밖 v̂₂, ĉ₂가 없는 학습 행이 있다")
        self.oofs[seed] = dict(v=V.to(fd.device), c=C.to(fd.device), is_train=is_train, encoders=encoders, shas=[e["sha256"] for e in encoders])
        return self.oofs[seed]

    def run_dir(self, condition, cand, seed):
        return self.root / condition / f"{S.candidate_id(cand)}_seed{seed}"

    def _save_pred(self, path, rows, z):
        fd = self.fd
        np.savez(path, participant=fd.participant_names(rows), video_id=fd.row_video[rows], logit=z.numpy(), p=z.sigmoid().numpy())

    def train_one(self, condition, cand, seed, search=False):
        """학습 한 번. 돌려주는 값은 done.json의 내용이다. search: 설정 후보 고르기(seed 0)이면 발산을 기록하고 넘어간다."""
        S.check_candidate(condition, cand)
        cfg = S.CONDITIONS[condition]
        path = self.run_dir(condition, cand, seed)
        if c.done_or_new(path, self.run.key):
            return json.loads((path / "done.json").read_text())
        fd = self.fd
        started = time.time()
        if str(fd.device).startswith("cuda"):
            torch.cuda.reset_peak_memory_stats()
        teacher = self.teacher(seed) if cfg.representation else None
        seed_everything(seed)
        model = S.build_model(condition, cand, fd.voxel_counts, self.config.tokenizer, self.config.voxel_sampling, self.cells)
        if teacher is not None:
            model.load_head_from(teacher.model, frozen=cfg.representation == "frozen")
        fenc = self.feature_encoder(seed) if (cfg.separate or cfg.head_only or cfg.frozen_encoder) else None
        if fenc is not None and cfg.separate:
            model = M.SeparateDecodedModel(model, copy.deepcopy(fenc["model"]))
        if fenc is not None and (cfg.head_only or cfg.frozen_encoder):  # D-3, D-4. 같은 seed의 encoder 2 가중치를 넣고 고정한다
            model.feature_model.load_state_dict(fenc["model"].state_dict())
            M.freeze(model.feature_model)
        model = model.to(fd.device)
        shuffle = self.shuffle(seed) if condition in S.NEEDS_SHUFFLE else None
        forward = multimodal_forward(fd) if cfg.multimodal else brain_forward(fd)
        oof = self.oof(seed) if (cfg.separate or cfg.head_only) and not cfg.paired else None  # 11/9. D-1, D-2, D-3의 학습 행은 fold 밖 v̂₂, ĉ₂
        if oof is not None:
            forward = oof_forward(fd, oof)
        try:
            result = fit(model, fd, self.spec, lr=cand["lr"], input_wd=cand["input_wd"], feature_wd=cand["feature_wd"], loss_fn=make_loss(condition, cand, fd, shuffle, teacher), forward=forward, seed=seed,
                         val_fn=feature_val_loss(fd, self.spec.batch) if cfg.feature_only else None,
                         restore_fn=None if cfg.feature_only else total_val_loss(condition, cand, fd, forward, self.spec.batch, teacher))
        except Diverged as e:
            if not search:
                raise
            with c.Atomic(path) as tmp:  # 발산 기록. 모델은 저장하지 않는다
                self.run._check_code()
                done = dict(self.run.prov, plan=fd.plan.name, condition=condition, thesis_name=cfg.thesis, candidate=cand, candidate_id=S.candidate_id(cand), seed=seed, diverged=True, diverged_reason=str(e), best_epoch=None, val_loss=None, val_score=None, **c.timing(started))
                _json(done, tmp / "done.json")
            print("발산", path, e, flush=True)
            return done
        with c.Atomic(path) as tmp:
            M.save_checkpoint(tmp / "model.pt", model, condition=condition, candidate=cand, seed=seed, best_epoch=result.best_epoch)
            _json(M.parameter_assignment(model), tmp / "parameter_groups.json")
            result.history.to_csv(tmp / "history.tsv", sep="\t", index=False)
            val = fd.rows("val")
            if not cfg.feature_only:  # encoder 2는 정서를 내지 않는다
                self._save_pred(tmp / "val_pred.npz", val, collect(model, val, forward, self.spec.batch)["z"])
                if fd.plan.test:
                    test = fd.rows("test")
                    self._save_pred(tmp / "test_pred.npz", test, collect(model, test, forward, self.spec.batch)["z"])
            extra = {}
            if fenc is not None:
                if M.state_digest(model.feature_model) != fenc["digest"]:
                    raise ValueError("encoder 2가 학습 중에 바뀌었다(D-1~D-4)")
                extra["feature_encoder"] = dict(checkpoint_sha256=fenc["sha256"], seed=seed)
            if oof is not None:
                extra["feature_encoder_oof"] = dict(checkpoint_sha256=oof["shas"], seed=seed)
            if shuffle is not None:
                _json(dict(outer_fold=shuffle.outer_fold, seed=shuffle.seed, random_seed=shuffle.random_seed, mapping=shuffle.mapping), tmp / "shuffle.json")
            if teacher is not None:
                if M.state_digest(teacher.model) != teacher.digest:
                    raise ValueError("Multimodal Model이 학습 중에 바뀌었다(G16)")
                np.savez(tmp / "representation_stats.npz", mean=teacher.mean.cpu().numpy(), std=teacher.std.cpu().numpy())
                _json(dict(checkpoint_sha256=teacher.sha256, seed=seed), tmp / "teacher.json")
            self.run._check_code()  # 저장 전에 코드가 시작 때와 같은지 본다. 입력 전체의 해시는 조건마다 본다
            memory = int(torch.cuda.max_memory_allocated()) if str(fd.device).startswith("cuda") else None
            done = dict(self.run.prov, plan=fd.plan.name, condition=condition, thesis_name=cfg.thesis, candidate=cand, candidate_id=S.candidate_id(cand), seed=seed, best_epoch=result.best_epoch, val_loss=result.val_loss, val_score=result.val_score, n_epochs=result.n_epochs, parameter_counts=M.count_parameters(model), max_gpu_memory_bytes=memory, **extra, **c.timing(started))
            _json(done, tmp / "done.json")
        self.trained.append((condition, S.candidate_id(cand), seed))
        print("저장", path, f"epoch {result.best_epoch}/{result.n_epochs}", flush=True)
        return done

    def _row(self, cand, done):
        diverged = bool(done.get("diverged", False))
        return dict(cand, candidate_id=done["candidate_id"], val_score=float("nan") if diverged else done["val_score"], val_loss=float("nan") if diverged else done["val_loss"], best_epoch=done["best_epoch"], diverged=diverged, source_condition=None, source_id=None)

    def selected(self, condition):
        path = self.root / condition / "selected.json"
        if not path.exists():
            raise SystemExit(f"{condition}의 선택이 아직 없다. 앞 조건을 먼저 돌려야 한다(5-5, G9, O5)")
        sel = json.loads(path.read_text())
        if sel["run_key"] != self.run.key:
            raise SystemExit(f"{path}: 코드, 입력, 분할 또는 설정이 다른 선택이다. 지우고 다시 돌려야 한다.")
        return sel

    def run_condition(self, condition):
        if condition in S.POOLED:
            return self._run_pooled(condition)
        if S.CONDITIONS[condition].paired:
            return self._run_paired(condition)
        cfg, config = S.CONDITIONS[condition], self.config
        base = None if condition == "brain_only" else self.selected("brain_only")["candidate"]
        decoded = self.selected(S.DECODED_SOURCE[condition])["candidate"] if condition in S.DECODED_SOURCE else None
        cands = S.candidates(condition, k_candidates=config.k_candidates, base=base, decoded=decoded, learning_rates=config.learning_rates, lr_follows_brain_only=config.lr_follows_brain_only)
        rows = [self._row(cand, self.train_one(condition, cand, self.spec.seeds[0], search=True)) for cand in cands]
        source = None
        if condition in S.ZERO_SOURCE:
            source = self.selected(S.ZERO_SOURCE[condition][0])
            rows = rows + S.zero_rows(condition, source["rows"], source["candidate"])
        best = S.select_best(rows)
        cand = {k: best[k] for k in ("d", "input_wd", "lr", "lam", "alpha", "rank", "feature_wd")}
        if best["source_condition"] is not None:
            if best["source_id"] != S.candidate_id({k: source["candidate"][k] for k in cand}):  # 앞 조건에서 고른 모델이어야 한다. 아니면 규칙이 어긋난 것이다
                raise ValueError(f"{condition}: 0 후보가 앞 조건에서 고른 모델과 다르다(G10)")
            seeds = dict(source["seeds"])  # G10. 그 fold의 결과는 앞 조건의 모델이다
        else:
            seeds = {str(self.spec.seeds[0]): str(self.run_dir(condition, cand, self.spec.seeds[0]).relative_to(self.root))}
            for s in self.spec.seeds[1:]:
                self.train_one(condition, cand, s)
                seeds[str(s)] = str(self.run_dir(condition, cand, s).relative_to(self.root))
        self._write_selection(condition, rows, cand, best["source_condition"], seeds)
        if not config.keep_candidate_checkpoints:
            self._prune(condition, seeds)
        for rel in seeds.values():
            self.save_outputs(self.root / rel)
        self.run.check()

    def train_pair(self, condition, cand, seed, enc, fdj):
        """짝 하나(11/9). encoder j를 고정하고 그 encoder가 보지 않은 j번째 fold 영상으로만 head를 학습한다. 입력은 encoder j와 같은 기준으로 표준화한 자료(fdj)다."""
        S.check_candidate(condition, cand)
        path = self.run_dir(condition, cand, seed) / f"pair{enc['fold']}"
        if c.done_or_new(path, self.run.key):
            return json.loads((path / "done.json").read_text())
        started = time.time()
        seed_everything(seed)
        model = S.build_model(condition, cand, fdj.voxel_counts, self.config.tokenizer, self.config.voxel_sampling)  # 11/10. 짝 조건도 같은 입력층
        model.feature_model.load_state_dict(enc["model"].state_dict())
        M.freeze(model.feature_model)
        model = model.to(fdj.device)
        forward = brain_forward(fdj)
        result = fit(model, fdj, self.spec, lr=cand["lr"], input_wd=cand["input_wd"], feature_wd=None, loss_fn=make_loss(condition, cand, fdj), forward=forward, seed=seed)
        if M.state_digest(model.feature_model) != enc["digest"]:
            raise ValueError("짝의 encoder 2가 학습 중에 바뀌었다")
        with c.Atomic(path) as tmp:
            M.save_checkpoint(tmp / "model.pt", model, condition=condition, candidate=cand, seed=seed, best_epoch=result.best_epoch, held_fold=enc["fold"])
            result.history.to_csv(tmp / "history.tsv", sep="\t", index=False)
            for name, rows in (("val_pred.npz", fdj.rows("val")), ("test_pred.npz", fdj.rows("test") if fdj.plan.test else None)):
                if rows is not None:
                    z = collect(model, rows, forward, self.spec.batch)["z"]
                    np.savez(tmp / name, participant=fdj.participant_names(rows), video_id=fdj.row_video[rows], logit=z.numpy(), p=z.sigmoid().numpy())
            self.run._check_code()
            done = dict(self.run.prov, plan=fdj.plan.name, condition=condition, candidate=cand, candidate_id=S.candidate_id(cand), seed=seed, held_fold=enc["fold"], n_head_rows=len(fdj.rows("train")), feature_encoder_oof=dict(checkpoint_sha256=enc["sha256"], seed=seed), best_epoch=result.best_epoch, val_loss=result.val_loss, val_score=result.val_score, n_epochs=result.n_epochs, **c.timing(started))
            _json(done, tmp / "done.json")
        self.trained.append((condition, S.candidate_id(cand) + f"_pair{enc['fold']}", seed))
        print("저장", path, f"epoch {result.best_epoch}/{result.n_epochs}", flush=True)
        return done

    def _pairs(self, condition, cands, seed):
        """seed 하나에서 후보마다 네 짝을 학습한다. 짝 j의 자료(fdj)는 한 번만 준비한다."""
        oof = self.oof(seed)
        done = {S.candidate_id(x): [] for x in cands}
        for enc in oof["encoders"]:
            paths = [self.run_dir(condition, cand, seed) / f"pair{enc['fold']}" for cand in cands]
            fdj = None if all(c.done_or_new(x, self.run.key) for x in paths) else self._inner_fold_head(enc)  # 끝난 짝은 자료를 다시 준비하지 않는다
            for cand in cands:
                done[S.candidate_id(cand)].append(self.train_pair(condition, cand, seed, enc, fdj))
            del fdj
        return done

    def _inner_fold_head(self, enc):
        if self.raw is None:
            raise ValueError("짝 학습의 자료를 만들 원자료가 없다(FoldRunner.raw)")
        brains, y, v, cap = self.raw
        return S.prepare_fold(brains, self.split, y, v, cap, enc["head_plan"], device=self.fd.device, mc_ids=self.mc_ids, stats_videos=enc["stats_videos"])

    def _ensemble(self, condition, cand, seed, pairs):
        """시험(과 검증) 예측은 네 짝의 예측 평정을 평균한다. 짝마다의 예측도 남겨 짝 하나의 성능을 따로 낼 수 있게 한다(11/9)."""
        folder = self.run_dir(condition, cand, seed)
        out = folder / "ensemble"
        if c.done_or_new(out, self.run.key):
            return
        with c.Atomic(out) as tmp:
            for name in ("val_pred.npz", "test_pred.npz"):
                parts = [np.load(folder / f"pair{d['held_fold']}" / name) for d in pairs if (folder / f"pair{d['held_fold']}" / name).exists()]
                if not parts:
                    continue
                keys = [list(zip(z["participant"].tolist(), z["video_id"].tolist())) for z in parts]
                if any(k != keys[0] for k in keys):
                    raise ValueError("짝마다 예측한 행이 다르다")
                pp = np.stack([z["p"] for z in parts])
                pm = pp.mean(0)
                np.savez(tmp / name, participant=parts[0]["participant"], video_id=parts[0]["video_id"], p=pm, logit=np.log(pm) - np.log1p(-pm), p_pairs=pp, held_folds=np.array([d["held_fold"] for d in pairs]))
            self.run._check_code()
            _json(dict(self.run.prov, condition=condition, candidate=cand, seed=seed, pairs=[dict(held_fold=d["held_fold"], val_score=d["val_score"], feature_encoder_oof=d["feature_encoder_oof"]) for d in pairs]), tmp / "done.json")

    def _run_paired(self, condition):
        """11/9 석진 님. D-4와 D-3 짝. 후보마다 네 짝을 학습하고, 네 짝의 검증 점수 평균으로 고른다(learning rate는 네 짝에 같은 값). 시험은 네 짝의 평균."""
        config = self.config
        base = self.selected("brain_only")["candidate"]
        cands = S.candidates(condition, k_candidates=config.k_candidates, base=base, learning_rates=config.learning_rates, lr_follows_brain_only=config.lr_follows_brain_only)
        s0 = self.spec.seeds[0]
        done = self._pairs(condition, cands, s0)
        rows = []
        for cand in cands:
            ds = done[S.candidate_id(cand)]
            rows.append(dict(cand, candidate_id=S.candidate_id(cand), val_score=float(np.mean([d["val_score"] for d in ds])), val_loss=float(np.mean([d["val_loss"] for d in ds])), best_epoch=[d["best_epoch"] for d in ds], diverged=False, source_condition=None, source_id=None))
        best = S.select_best(rows)
        cand = {k: best[k] for k in ("d", "input_wd", "lr", "lam", "alpha", "rank", "feature_wd")}
        seeds = {}
        for s in self.spec.seeds:
            ds = done[S.candidate_id(cand)] if s == s0 else self._pairs(condition, [cand], s)[S.candidate_id(cand)]
            self._ensemble(condition, cand, s, ds)
            seeds[str(s)] = str(self.run_dir(condition, cand, s).relative_to(self.root))
        self._write_selection(condition, rows, cand, None, seeds)
        if not config.keep_candidate_checkpoints:
            keep = {self.root / rel for rel in seeds.values()}
            for path in (self.root / condition).glob("*_seed*/pair*/model.pt"):
                if path.parent.parent not in keep:
                    path.unlink()
        self.run.check()

    def _run_pooled(self, condition):
        """F7, O31. 그 fold의 표준 실행에서 고른 값을 그대로 쓴다. 새 후보 탐색은 없다."""
        src = self.selected(S.POOLED[condition])["candidate"]
        seeds = {}
        for s in self.spec.seeds:
            self.train_one(condition, src, s)
            seeds[str(s)] = str(self.run_dir(condition, src, s).relative_to(self.root))
        self._write_selection(condition, [], src, None, seeds)
        for rel in seeds.values():
            self.save_outputs(self.root / rel)
        self.run.check()

    def _write_selection(self, condition, rows, cand, source_condition, seeds):
        folder = self.root / condition
        folder.mkdir(parents=True, exist_ok=True)
        if rows:
            pd.DataFrame(rows).to_csv(folder / "selection.tsv", sep="\t", index=False)
        zero = source_condition is not None
        _json(dict(run_key=self.run.key, condition=condition, candidate=cand, zero_selected=zero, source_condition=source_condition, seeds=seeds, rows=rows), folder / "selected.json")

    def _prune(self, condition, seeds):
        """선택되지 않은 후보의 체크포인트를 지운다. 시험 예측과 기록은 남긴다(N24)."""
        keep = {self.root / rel for rel in seeds.values()}
        for path in (self.root / condition).glob("*_seed*"):
            if path not in keep and (path / "model.pt").exists():
                (path / "model.pt").unlink()

    def save_outputs(self, path):
        """고른 모델의 M1 저장. 체크포인트를 다시 읽어 낸다. 시험과 검증 행의 decoded features, attention, decoding 정확도."""
        out = path / "outputs"
        if c.done_or_new(out, self.run.key):
            return
        fd = self.fd
        model, meta = M.load_checkpoint(path / "model.pt", fd.device)
        cfg = S.CONDITIONS[meta["condition"]]
        forward = multimodal_forward(fd) if cfg.multimodal else brain_forward(fd)
        batch = self.spec.batch
        if cfg.head_only:  # D-3. 정서 출력만 저장한다. 쓴 v̂₂, ĉ₂는 같은 seed의 feature_encoder 출력과 같다
            with c.Atomic(out) as tmp:
                if fd.plan.test:
                    test = fd.rows("test")
                    o = collect(model, test, forward, batch, ("z",))
                    np.savez(tmp / "test_outputs.npz", participant=fd.participant_names(test), video_id=fd.row_video[test], logit=o["z"].numpy(), p=o["z"].sigmoid().numpy())
                self.run._check_code()
                _json(dict(self.run.prov, model_dir=str(path.relative_to(self.root))), tmp / "done.json")
            return
        inner = model.main if cfg.separate else model
        has_feature = not cfg.multimodal and inner.readout.has_feature_head
        has_query = not cfg.pooling
        with c.Atomic(out) as tmp:
            if cfg.feature_only:  # encoder 2. decoded features와 그 정확도만 저장한다(K1의 "특징만 학습한 모델")
                for split_name in (("test", "val") if fd.plan.test else ("val",)):
                    rows = fd.rows(split_name)
                    o = collect(model, rows, forward, batch, ("v_hat", "c_hat"))
                    np.savez(tmp / f"decoded_{split_name}.npz", participant=fd.participant_names(rows), video_id=fd.row_video[rows], v_hat=o["v_hat"].numpy(), c_hat=o["c_hat"].numpy())
                decoding_accuracy(model, fd, batch).to_csv(tmp / "decoding_accuracy.tsv", sep="\t", index=False)
                self.run._check_code()
                _json(dict(self.run.prov, model_dir=str(path.relative_to(self.root))), tmp / "done.json")
                return
            if cfg.separate:  # D-1, D-2. 정서 계산에 쓴 encoder 2의 v̂₂, ĉ₂를 decoded features로, encoder 1의 보조 출력은 aux로 저장한다
                for split_name in (("test", "val") if fd.plan.test else ("val",)):
                    rows = fd.rows(split_name)
                    o = collect(model, rows, forward, batch, ("v_used", "c_used", "v_hat", "c_hat"))
                    np.savez(tmp / f"decoded_{split_name}.npz", participant=fd.participant_names(rows), video_id=fd.row_video[rows], v_hat=o["v_used"].numpy(), c_hat=o["c_used"].numpy())
                    np.savez(tmp / f"aux_decoded_{split_name}.npz", participant=fd.participant_names(rows), video_id=fd.row_video[rows], v_hat=o["v_hat"].numpy(), c_hat=o["c_hat"].numpy())
                if fd.plan.test:
                    test = fd.rows("test")
                    o = collect(model, test, forward, batch, ("z", "g", "emotion_attention"))
                    np.savez(tmp / "test_outputs.npz", participant=fd.participant_names(test), video_id=fd.row_video[test], logit=o["z"].numpy(), p=o["z"].sigmoid().numpy(), g=o["g"].numpy())
                    np.save(tmp / "attention_emotion_test.npy", o["emotion_attention"].numpy())
                decoding_accuracy(model, fd, batch).to_csv(tmp / "decoding_accuracy_aux.tsv", sep="\t", index=False)
                self.run._check_code()
                _json(dict(self.run.prov, model_dir=str(path.relative_to(self.root))), tmp / "done.json")
                return
            if fd.plan.test:
                test = fd.rows("test")
                names = ("z", "g") + (("emotion_attention",) if has_query else ()) + (("v_hat", "c_hat", "feature_attention") if has_feature else ())
                o = collect(model, test, forward, batch, names)
                np.savez(tmp / "test_outputs.npz", participant=fd.participant_names(test), video_id=fd.row_video[test], logit=o["z"].numpy(), p=o["z"].sigmoid().numpy(), g=o["g"].numpy())
                if has_query:
                    np.save(tmp / "attention_emotion_test.npy", o["emotion_attention"].numpy())
                if has_feature:
                    np.save(tmp / "attention_feature_test.npy", o["feature_attention"].numpy())
                    np.savez(tmp / "decoded_test.npz", participant=fd.participant_names(test), video_id=fd.row_video[test], v_hat=o["v_hat"].numpy(), c_hat=o["c_hat"].numpy())
            if has_feature:
                val = fd.rows("val")
                o = collect(model, val, forward, batch, ("v_hat", "c_hat"))
                np.savez(tmp / "decoded_val.npz", participant=fd.participant_names(val), video_id=fd.row_video[val], v_hat=o["v_hat"].numpy(), c_hat=o["c_hat"].numpy())
                if cfg.features == "actual":
                    decoding_accuracy(model, fd, batch).to_csv(tmp / "decoding_accuracy.tsv", sep="\t", index=False)
            self.run._check_code()
            _json(dict(self.run.prov, model_dir=str(path.relative_to(self.root))), tmp / "done.json")


def decoding_accuracy(model, fd, batch):
    """5-0의 남는 주의. 학습 영상과 검증 영상에서 decoded features가 실제 feature와 얼마나 맞는지 기록한다. 시험 영상은 S9, S10이 채점한다."""
    out = []
    forward = brain_forward(fd)
    for split_name in ("train", "val"):
        rows = fd.rows(split_name)
        o = collect(model, rows, forward, batch, ("v_hat", "c_hat"))
        v, cap = (t.cpu().numpy() for t in fd.feature_targets(rows))
        names = fd.participant_names(rows)
        for pid in fd.participants:
            at = names == pid
            for target, pred, true in (("vision", o["v_hat"].numpy()[at], v[at]), ("caption", o["c_hat"].numpy()[at], cap[at])):
                r = c.pearson(pred, true)
                out.append(dict(participant=pid, split=split_name, target=target, mse=float(((pred - true) ** 2).mean()), mean_dim_r=float(np.nanmean(r)) if np.isfinite(r).any() else float("nan"), n_constant_dims=int(np.isnan(r).sum())))
    return pd.DataFrame(out)


def load_known(split, plan, include_test_features=False):
    """split 순서의 y, v, c. 학습과 검증 영상의 행만 읽고 나머지는 NaN이다. 시험 영상의 사람 평정은 읽지 않는다.
    시험 영상의 feature는 Multimodal Model의 참고 성능을 낼 때만 읽는다(G16)."""
    known = set(plan.train) | set(plan.val)
    mask = split.video_id.isin(known).to_numpy()
    y = np.full((len(split), M.N_EMOTIONS), np.nan, np.float32)
    y[mask] = c.load_scores(split[mask], "emotions")[0]
    if include_test_features:
        mask = mask | split.video_id.isin(set(plan.test)).to_numpy()
    ids = split.video_id.to_numpy()[mask]
    v = np.full((len(split), M.VISUAL_DIM), np.nan, np.float32)
    cap = np.full((len(split), M.CAPTION_DIM), np.nan, np.float32)
    v[mask], cap[mask] = c.load_rows(c.VISUAL_TARGET, ids, split), c.load_rows(c.CAPTION_TARGET, ids, split)
    return y, v, cap


def weight_table(ds, participants=d5.HK, voxel_counts=None):
    """F8. 조건마다 학습 가중치 수. 실제 ROI 표의 voxel 수를 쓴다(ROI별 voxel 수의 합, 04 기록 칸 S1). 뇌 반응을 읽지 않는다."""
    if voxel_counts is None:
        voxel_counts = {}
        for s in participants:
            with np.load(d5.roi_path(s)) as z:
                voxel_counts[f"sub-{s}"] = np.diff(z["offsets"]).tolist()
    out = []
    for d in ds:
        for name, cfg in S.CONDITIONS.items():
            ranks = ((0,) if cfg.additive else S.RANKS) if cfg.decoded else (None,)
            for rank in ranks:
                model = S.build_model(name, dict(d=d, rank=rank), voxel_counts)
                if cfg.representation == "frozen":
                    for p in model.readout.emotion_linears.parameters():
                        p.requires_grad_(False)
                out.append(dict(condition=name, d=d, rank=rank, **M.count_parameters(model)))
                del model
    table = pd.DataFrame(out)
    table["rank"] = table["rank"].astype("Int64")
    return table


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", help="outer_fold1~6, pilot_fold1, zone_block<b>_fold<k>_<excluded|control>, final_for_mc")
    ap.add_argument("--conditions", help="쉼표로 나눈 조건 이름. 앞 조건의 선택이 있어야 한다")
    ap.add_argument("--config", help="configs/s6의 설정 JSON. k_candidates는 S7에서 정한다")
    ap.add_argument("--design-freeze", default="")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--weight-counts", help="d 값을 쉼표로 나눠 주면 F8의 표만 쓰고 끝난다")
    a = ap.parse_args(argv)
    if a.weight_counts:
        S.MANIFEST.mkdir(parents=True, exist_ok=True)
        table = weight_table([int(x) for x in a.weight_counts.split(",")])
        table.to_csv(S.MANIFEST / "weight_counts.tsv", sep="\t", index=False)
        print(table.to_string())
        return
    c.guard(a.design_freeze)  # 동결 커밋이 없거나 커밋되지 않은 코드가 있으면 아무것도 읽기 전에 멈춘다(M5)
    if not (a.plan and a.conditions and a.config):
        raise SystemExit("--plan, --conditions, --config를 주어야 한다")
    config = S.load_config(a.config)
    split = c.load_split()
    plan = S.load_plan(a.plan, split)  # manifests/s2/splits의 목록 파일을 쓰고 분할 표와 대조한다
    wanted = a.conditions.split(",")
    S.check_conditions(plan.name, wanted)
    spec = S.Spec(seeds=config.seeds)
    stimulus_run = None
    use_stimulus = plan.name.startswith(("outer_fold", "pilot_fold")) and S.needs_stimulus(wanted)  # Stimulus 예측 평정을 쓰는 조건이 없으면 읽지 않는다(11/9)
    if use_stimulus:  # S4 출처를 학습 전에 대조한다. 입력 해시는 이 실행과 같은 방식으로 낸다
        probe = S.Run(a.design_freeze, {**S.input_paths(plan), "config": a.config})
        stimulus_run = S.check_stimulus_source(S.stimulus_path(plan.outer_fold).parent / "done.json", plan.outer_fold, probe.hashes)
    run = S.Run(a.design_freeze, {**S.input_paths(plan, stimulus=use_stimulus, cells=config.tokenizer == "roi_cells"), "config": a.config}, stimulus_run_key=stimulus_run, plan=plan.name, config=asdict(config), spec=asdict(spec), torch=torch.__version__, deterministic=torch.are_deterministic_algorithms_enabled(), nondeterministic_ops=[])  # 읽기 전에 해시를 낸다
    include_test = "multimodal" in wanted and bool(plan.test)
    y, v, cap = load_known(split, plan, include_test)
    brains = S.load_brains(split, list(plan.train) + list(plan.val) + list(plan.test))  # 이번 실행에 쓰는 영상의 행만 읽는다. 파일럿은 시험 영상이 없다
    stimulus = dict(np.load(S.stimulus_path(plan.outer_fold))) if use_stimulus else None
    fd = S.prepare_fold(brains, split, y, v, cap, plan, stimulus=stimulus, include_test_features=include_test, device=a.device)
    needs_inner = any(S.CONDITIONS[n].separate or S.CONDITIONS[n].head_only or S.CONDITIONS[n].paired for n in wanted)  # 11/9. fold 밖 encoder 2와 짝 학습은 원자료로 자료를 다시 준비한다
    raw = (brains, y, v, cap) if needs_inner else None
    del brains, y, v, cap
    run.check()  # 읽은 내용이 기록한 해시와 같음을 확인한다
    runner = FoldRunner(fd, split, run, spec, config, S.OUT / plan.name)
    runner.raw = raw
    for name in S.ORDER:
        if name in wanted:
            runner.run_condition(name)


if __name__ == "__main__":
    main()
