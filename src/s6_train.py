#!/usr/bin/env python3
"""S6 뇌 모델 학습 (04 S6, 01 5-A, G7~G16, H2, L9, M1, N3, N24, O1, O5, O6, O31, O32, 2026-11-07).

바깥 fold k가 시험, 다음 fold가 H2 검증, 나머지 4개가 학습이다. 후보는 seed 0으로 고르고 고른 설정으로 seed 1, 2를 더 학습한다(L9). 고른 모델을 그대로 시험한다.
조기 종료는 검증 자료의 실제 y에 대한 정서 soft BCE(patience 30, 가장 낮은 epoch로 되돌림), 선택은 실제 y에 대한 정서별 r 평균이다(0-2, O6).
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
    history.tsv: epoch, train_loss, val_loss
    val_pred.npz: participant, video_id, logit(sigmoid 전), p. 고른 epoch의 값
    test_pred.npz: 같은 꼴(시험이 있는 분할만). 후보마다 저장한다(N24)
    shuffle.json: 대조군의 순열과 그 seed(O1)
    representation_stats.npz, teacher.json: F-고정, F-학습. 중간 표현의 평균과 표준편차, 짝지은 Multimodal Model의 체크포인트 해시
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
        if cfg.feature_only:  # D-1, D-2, E-1의 encoder 2. 정서를 학습하지 않는다
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


def fit(model, fd, spec, *, lr, input_wd, feature_wd, loss_fn, forward, seed, on_epoch=None, val_fn=None):
    """G13, O6. AdamW, batch 64, 최대 300 epoch, patience 30, warmup 없음. 가장 낮은 epoch의 가중치로 되돌린다. 같은 값이면 앞선 epoch다."""
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
        if val_fn is not None:  # encoder 2는 feature MSE로 멈춘다
            val_loss = numeric(lambda: val_fn(model), f"epoch {epoch} 검증")
        else:
            z = numeric(lambda: collect(model, val, forward, spec.batch)["z"], f"epoch {epoch} 검증")
            val_loss = validation_loss(z, y_val)
        if not np.isfinite(val_loss):
            raise Diverged(f"epoch {epoch}: 검증 손실이 NaN 또는 Inf다")
        history.append(dict(epoch=epoch, train_loss=total / len(order), val_loss=val_loss))
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
    """F-고정, F-학습의 Multimodal Model 하나(G16). 고정하고, 학습 행의 중간 표현과 그 표준화 통계를 미리 낸다.
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
        """D-1, D-2, E-1의 encoder 2. 같은 seed의 feature_encoder 선택을 읽어 고정한다. 학습 한 번마다 복사해 쓴다."""
        if seed not in self.feature_encoders:
            sel = self.selected("feature_encoder")
            path = self.root / sel["seeds"][str(seed)] / "model.pt"
            model, _ = M.load_checkpoint(path, self.fd.device)
            M.freeze(model)
            self.feature_encoders[seed] = dict(model=model, sha256=c.sha256(path), digest=M.state_digest(model))
        return self.feature_encoders[seed]

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
        model = S.build_model(condition, cand, fd.voxel_counts, self.config.tokenizer, self.config.voxel_sampling)
        if teacher is not None:
            model.load_head_from(teacher.model, frozen=cfg.representation == "frozen")
        fenc = self.feature_encoder(seed) if (cfg.separate or cfg.head_only) else None
        if fenc is not None and cfg.separate:
            model = M.SeparateDecodedModel(model, copy.deepcopy(fenc["model"]))
        if fenc is not None and cfg.head_only:  # E-1. 같은 seed의 encoder 2 가중치를 넣고 고정한다
            model.feature_model.load_state_dict(fenc["model"].state_dict())
            M.freeze(model.feature_model)
        model = model.to(fd.device)
        shuffle = self.shuffle(seed) if condition in S.NEEDS_SHUFFLE else None
        forward = multimodal_forward(fd) if cfg.multimodal else brain_forward(fd)
        try:
            result = fit(model, fd, self.spec, lr=cand["lr"], input_wd=cand["input_wd"], feature_wd=cand["feature_wd"], loss_fn=make_loss(condition, cand, fd, shuffle, teacher), forward=forward, seed=seed, val_fn=feature_val_loss(fd, self.spec.batch) if cfg.feature_only else None)
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
                    raise ValueError("encoder 2가 학습 중에 바뀌었다(D-1, D-2)")
                extra["feature_encoder"] = dict(checkpoint_sha256=fenc["sha256"], seed=seed)
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
        if cfg.head_only:  # E-1. 정서 출력만 저장한다. 쓴 v̂₂, ĉ₂는 같은 seed의 feature_encoder 출력과 같다
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
    run = S.Run(a.design_freeze, {**S.input_paths(plan, stimulus=use_stimulus), "config": a.config}, stimulus_run_key=stimulus_run, plan=plan.name, config=asdict(config), spec=asdict(spec), torch=torch.__version__, deterministic=torch.are_deterministic_algorithms_enabled(), nondeterministic_ops=[])  # 읽기 전에 해시를 낸다
    include_test = "multimodal" in wanted and bool(plan.test)
    y, v, cap = load_known(split, plan, include_test)
    brains = S.load_brains(split, list(plan.train) + list(plan.val) + list(plan.test))  # 이번 실행에 쓰는 영상의 행만 읽는다. 파일럿은 시험 영상이 없다
    stimulus = dict(np.load(S.stimulus_path(plan.outer_fold))) if use_stimulus else None
    fd = S.prepare_fold(brains, split, y, v, cap, plan, stimulus=stimulus, include_test_features=include_test, device=a.device)
    del brains, y, v, cap
    run.check()  # 읽은 내용이 기록한 해시와 같음을 확인한다
    runner = FoldRunner(fd, split, run, spec, config, S.OUT / plan.name)
    for name in S.ORDER:
        if name in wanted:
            runner.run_condition(name)


if __name__ == "__main__":
    main()
