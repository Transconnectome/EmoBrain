#!/usr/bin/env python3
"""S9 저장된 모델로 하는 분석 (04 S9, 01 2-2, 1-1, 1-2, 6-4b, 6-4의 ROI판, O2, O3. 2026-11-13).

다시 학습하지 않는다. S6이 고른 모델(selected.json의 seed 폴더 model.pt)을 읽고, 학습 때와 같은 표준화로 시험 영상의 뇌 입력을 다시 만든다.

task swap (바꿔 끼우기, 2-2, 1-1, 1-2의 (나))
- 모델: C-1 Brain + Decoded Feature → Emotion(상호작용 head). 바깥 fold, seed, 참가자마다 한다.
- 짝: S2의 pairs_directed.tsv(같은 시험 fold, 이름표 73개 거리가 가장 가까운 영상). 그 참가자에게 두 영상의 block이 모두 있는 짝만 쓰고 뺀 수를 남긴다.
- 계산: audition_codex.interchange_intervention을 그대로 부른다. ROI token은 A로 고정하고(g(H_A)), 시각만, 캡션만, 둘 다를 B의 값으로 바꾼다.
  같은 크기의 무작위 변경 대조 100회(O3), 결합 지표 I(logit). 요약은 audition_codex.summarize_interventions(6 fold의 쌍을 모은 r, 대조 100회의 r 평균을 뺀 효과).
- 사람 평정 차이 Δy = y_B − y_A는 시험 영상의 사람 평정이다. 이 분석의 채점에만 쓰고 모델과 짝은 고정되어 있다.

task perturb (네트워크 단위와 ROI 단위 입력 교란, 6-4b와 그 ROI판)
- 모델: A-1 Brain → Emotion과 C-1. 둘 다 고정한다.
- 교체: 묶음(CAB-NP 13개) 또는 ROI 하나의 입력 x(s, r)를 같은 참가자, 같은 시험 fold의 다른 시험 영상 값으로 바꾼다. 0으로 지우지 않는다.
  선형 입력층에서 ROI token은 그 ROI의 voxel만으로 만들어지고 평가 때는 voxel 뽑기를 하지 않으므로, 입력을 바꾼 것은 그 ROI token을 다른 영상의 token으로 바꾼 것과 같다.
  그래서 token을 한 번 만들고 바꿔 넣는다. 실행마다 첫 묶음에서 입력을 직접 바꾼 결과와 같은지 확인하고 다르면 멈춘다.
- 다른 영상 배정: 시험 영상마다 같은 참가자의 다른 시험 영상 하나를 무작위로 고른다. 20회 반복(04 S9). 두 모델과 모든 묶음, ROI에 같은 배정표를 쓴다. 배정표와 seed를 저장한다.
- 저장: 참가자마다 6 fold를 모은 r(O19와 같은 방식)을 낼 수 있게, 원래 예측과 교란 예측의 합, 제곱합, 사람 평정과의 곱의 합을 fold마다 저장한다.
  성능 하락은 반복마다 (원래 r − 교란 r)을 낸 뒤 20회를 평균한다(04 S9). 검정은 S10이다.
사용: s9_saved_models.py --task swap|perturb --s6-dir <S6 결과 폴더> --design-freeze <커밋> [--folds 1,2] [--seed 0] [--device cuda]
"""
import argparse
import hashlib
import json
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

import paths as P
import s4_common as c
import s5_common as d5
import s6_common as S
import s6_model as M
import s6_train as T

ac = M.ac
OUT = Path(os.environ.get("S9_OUT", P.OUT / "s9_saved_models"))
SWAP_CONDITION = "brain_decoded"  # C-1. 04 S9의 상호작용 head
PERTURB_CONDITIONS = ("brain_only", "brain_decoded")  # A-1, C-1
PERTURB_REPEATS = 20  # 04 S9, O3
CHUNK = 512
START_CODE = dict(S.START_CODE, **{Path(__file__).name: c.sha256(Path(__file__))})


class Run(S.Run):
    """S6의 Run과 같고 이 파일까지 해시한다."""

    def _check_code(self):
        now = {f.name: c.sha256(f) for f in sorted(c.CODE_DIR.glob("s[456]_*.py"))}
        now[M.AUDITION_PATH.name] = c.sha256(M.AUDITION_PATH)
        now[Path(__file__).name] = c.sha256(Path(__file__))
        if now != START_CODE:
            raise SystemExit("시작 뒤 코드가 바뀌었다.")

    def __init__(self, design_freeze, inputs, **settings):
        tables = list(d5.S2_TABLES)
        self.paths = {**{f"s2:{p.name}": Path(p) for p in tables}, **{k: Path(p) for k, p in inputs.items()}}
        self.hashes = {k: c.sha256(p) for k, p in self.paths.items()}
        self.prov = dict(code_commit=c.START_HEAD, code_dirty=c.START_DIRTY, code_sha256=START_CODE, design_freeze=design_freeze, inputs=self.hashes, input_paths={k: str(p) for k, p in self.paths.items()}, settings=settings)
        self._check_code()
        key = json.dumps(dict(code=START_CODE, inputs=self.hashes, settings=settings, design_freeze=design_freeze), sort_keys=True, default=str)
        self.prov["run_key"] = hashlib.sha256(key.encode()).hexdigest()


def fixed_seed(*parts):
    """배정과 대조의 seed. 이름과 번호에서 정하고 결과를 보지 않는다."""
    return int(hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:8], 16)


def model_dir(s6_dir, k, condition, seed):
    sel = json.load(open(Path(s6_dir) / f"outer_fold{k}" / condition / "selected.json"))
    rel = sel["seeds"].get(str(seed))
    if rel is None:
        raise ValueError(f"fold {k} {condition}: seed {seed}의 고른 모델이 없다")
    path = Path(s6_dir) / f"outer_fold{k}" / rel
    if not (path / "model.pt").exists() or not (path / "outputs" / "done.json").exists():
        raise ValueError(f"{path}: model.pt 또는 outputs가 없다(S6이 끝나지 않음)")
    return path, sel["run_key"]


def load_fold(k, s6_dir, device):
    """학습 때와 같은 자료 준비(S6 main과 같은 함수). 저장된 표준화 통계와 다르면 멈춘다."""
    split = c.load_split()
    plan = S.load_plan(f"outer_fold{k}", split)
    y, v, cap = T.load_known(split, plan)
    brains = S.load_brains(split, list(plan.train) + list(plan.val) + list(plan.test))
    fd = S.prepare_fold(brains, split, y, v, cap, plan, device=device)
    saved = np.load(Path(s6_dir) / f"outer_fold{k}" / "plan" / "standardization.npz")
    for pid, st in fd.voxel_stats.items():
        if not (np.array_equal(saved[f"voxel_mean:{pid}"], st["mean"]) and np.array_equal(saved[f"voxel_std:{pid}"], st["std"])):
            raise ValueError(f"fold {k} {pid}: 다시 만든 voxel 표준화가 S6에 저장한 것과 다르다")
    return split, fd


def test_ratings(split, video_ids):
    y, _ = c.load_scores(split, "emotions")
    pos = {v: i for i, v in enumerate(split.video_id.tolist())}
    return y[[pos[int(v)] for v in video_ids]]


def check_against_saved(path, fd, rows, out, names):
    """다시 계산한 시험 출력이 S6이 저장한 출력과 같은지 본다(같은 모델, 같은 행)."""
    t = np.load(path / "outputs" / "test_outputs.npz")
    key = {(p, int(v)): i for i, (p, v) in enumerate(zip(t["participant"], t["video_id"]))}
    at = [key[(p, int(v))] for p, v in zip(fd.participant_names(rows), fd.row_video[rows])]
    if not np.allclose(t["g"][at], out["g"], atol=1e-3, rtol=1e-3):
        raise ValueError(f"{path}: 다시 계산한 g가 저장한 값과 다르다")
    if "v_hat" in names:
        d = np.load(path / "outputs" / "decoded_test.npz")
        if not np.allclose(d["v_hat"][at], out["v_hat"], atol=1e-3, rtol=1e-3) or not np.allclose(d["c_hat"][at], out["c_hat"], atol=1e-3, rtol=1e-3):
            raise ValueError(f"{path}: 다시 계산한 decoded features가 저장한 값과 다르다")


@torch.no_grad()
def swap_fold(model, fd, split, k, seed, checkpoint_id, pairs_table):
    """바깥 fold k의 참가자마다 interchange_intervention. 돌려주는 것: 참가자 -> FoldInterventions, 짝 기록."""
    if model.training:
        raise ValueError("평가 상태에서만 한다")
    r = model.readout
    if not (r.decoded and r.rank):
        raise ValueError("바꿔 끼우기는 상호작용 head의 Brain + Decoded Feature → Emotion에서 한다(04 S9)")
    rows_all = fd.rows("test")
    pt = pairs_table[pairs_table.fold == k]
    out, log = {}, []
    for i, pid in enumerate(fd.participants):
        rows = rows_all[fd.row_participant[rows_all] == i]
        vids = [int(v) for v in fd.row_video[rows]]
        H = torch.cat([model.encode(fd.batch(rows[j:j + CHUNK])) for j in range(0, len(rows), CHUNK)])
        local = {v: j for j, v in enumerate(vids)}
        keep = pt[pt.video_a.isin(local) & pt.video_b.isin(local)]
        pairs = torch.tensor([[local[a], local[b]] for a, b in zip(keep.video_a, keep.video_b)], dtype=torch.long)
        ratings = torch.as_tensor(test_ratings(split, vids), dtype=torch.float32, device=H.device)
        res = ac.interchange_intervention(r, H, ratings, pairs, video_ids=vids, participant=pid, fold=k, seed=seed, checkpoint_id=checkpoint_id, control_seed=fixed_seed("swap", pid, k, seed))
        out[pid] = res
        log.append(dict(participant=pid, fold=k, seed=seed, n_test=len(vids), n_pairs=len(keep), n_pairs_missing=len(pt) - len(keep), control_seed=res.control_seed))
    return out, log


def donor_table(fd, rows, k, repeats=PERTURB_REPEATS):
    """시험 행마다 같은 참가자의 다른 시험 행(전역 행 번호가 아니라 rows 안 위치). 반복 × 행."""
    g = np.random.default_rng(fixed_seed("perturb", k))
    part = fd.row_participant[rows]
    table = np.empty((repeats, len(rows)), np.int64)
    for p in np.unique(part):
        at = np.flatnonzero(part == p)
        if len(at) < 2:
            raise ValueError("다른 시험 영상이 없는 참가자가 있다")
        for t in range(repeats):
            pick = g.integers(0, len(at) - 1, size=len(at))
            pick = pick + (pick >= np.arange(len(at)))  # 자기 자신을 빼고 고른다
            table[t, at] = at[pick]
    if (table == np.arange(len(rows))[None]).any() or (part[table] != part[None]).any():
        raise ValueError("배정표가 규칙과 다르다")
    return table


def units_table():
    """교란 단위. CAB-NP 13묶음과 ROI 370개. ROI 순서는 S2 roi_table(입력층의 ROI 순서)이다."""
    roi = pd.read_csv(c.S2 / "roi_table.tsv", sep="\t")
    units = [("group", g, np.flatnonzero(roi.group.to_numpy() == g)) for g in pd.read_csv(c.S2 / "cabnp_groups.tsv", sep="\t").group]
    units += [("roi", name, np.array([i])) for i, name in enumerate(roi.display)]
    if sum(len(u[2]) for u in units if u[0] == "group") != len(roi):
        raise ValueError("13묶음이 ROI 370개를 한 번씩 덮지 않는다")
    return units


def raw_perturbed_batch(fd, rows, donors, roi_index):
    """입력 x(s, r)를 직접 바꾼 묶음(확인용). donors: rows 안 위치."""
    batch = fd.batch(rows)
    xs = {}
    for pid, x in batch.xs.items():
        i = fd.participants.index(pid)
        at = np.flatnonzero(fd.row_participant[rows] == i)
        donor_x = fd.batch(rows[donors[at]]).xs[pid]
        bounds = np.concatenate([[0], np.cumsum(fd.voxel_counts[pid])])
        x = x.clone()
        for r in roi_index:
            x[:, bounds[r]:bounds[r + 1]] = donor_x[:, bounds[r]:bounds[r + 1]]
        xs[pid] = x
    return M.BrainBatch(xs, batch.positions, batch.n)


@torch.no_grad()
def tokens(model, fd, rows):
    if not isinstance(model.input_layer, M.RoiInput) or type(model.input_layer) is not M.RoiInput:
        raise ValueError("token 교체는 선형 입력층에서만 입력 교체와 같다")
    return torch.cat([model.input_layer(fd.batch(rows[j:j + CHUNK])) for j in range(0, len(rows), CHUNK)])


@torch.no_grad()
def predict_from_tokens(model, Tk):
    return torch.cat([model.readout(model.encoder(Tk[j:j + CHUNK])).z.sigmoid() for j in range(0, len(Tk), CHUNK)])


@torch.no_grad()
def perturb_fold(models, fd, split, k, repeats=PERTURB_REPEATS):
    """models: 조건 -> 고정한 모델. 돌려주는 것: 저장할 배열. repeats는 시험에서만 줄인다(실행은 04 S9의 20회)."""
    rows = fd.rows("test")
    y = torch.as_tensor(test_ratings(split, fd.row_video[rows]), dtype=torch.float64, device=fd.device)
    part = fd.row_participant[rows]
    n_part = len(fd.participants)
    onehot = torch.zeros(len(rows), n_part, dtype=torch.float64, device=fd.device)
    onehot[np.arange(len(rows)), part] = 1
    donors = donor_table(fd, rows, k, repeats)
    units = units_table()
    sums = lambda p: torch.stack([onehot.T @ p, onehot.T @ (p * p), onehot.T @ (p * y)])  # 3 × 참가자 × 34
    arrays = dict(video_id=fd.row_video[rows], participant=fd.participant_names(rows), donors=donors, donor_seed=np.array(fixed_seed("perturb", k)),
                  unit_kind=np.array([u[0] for u in units]), unit_name=np.array([u[1] for u in units]),
                  sum_y=(onehot.T @ y).cpu().numpy(), sum_yy=(onehot.T @ (y * y)).cpu().numpy(), n=onehot.sum(0).cpu().numpy())
    for name, model in models.items():
        if model.training:
            raise ValueError("평가 상태에서만 한다")
        Tk = tokens(model, fd, rows)
        base = predict_from_tokens(model, Tk).double()
        # 확인: 첫 참가자의 시험 행에서, 첫 묶음 단위의 입력을 직접 바꾼 결과와 token을 바꾼 결과가 같다
        p0 = np.flatnonzero(part == 0)
        local = {g: i for i, g in enumerate(p0)}
        idx = units[0][2]
        direct = model(raw_perturbed_batch(fd, rows[p0], np.array([local[g] for g in donors[0][p0]]), idx)).z.sigmoid().double()
        Tp = Tk[p0].clone()
        Tp[:, idx] = Tk[torch.as_tensor(donors[0][p0], device=Tk.device)][:, idx]
        if not torch.allclose(direct, predict_from_tokens(model, Tp).double(), atol=1e-4):
            raise ValueError(f"{name}: token 교체가 입력 교체와 다르다")
        arrays[f"{name}_base"] = sums(base).cpu().numpy()
        out = np.empty((len(units), repeats, 3, n_part, base.shape[1]))
        for t in range(repeats):
            donor_tokens = Tk[torch.as_tensor(donors[t], device=Tk.device)]
            for u, (_, _, idx) in enumerate(units):
                keep = Tk[:, idx].clone()
                Tk[:, idx] = donor_tokens[:, idx]
                out[u, t] = sums(predict_from_tokens(model, Tk).double()).cpu().numpy()
                Tk[:, idx] = keep
        arrays[f"{name}_perturbed"] = out
    return arrays


def pooled_r(base_sums, sum_y, sum_yy, n):
    """fold별 합을 모은 참가자 × 34의 r. base_sums: [..., 3, 참가자, 34]."""
    sp, spp, spy = base_sums[..., 0, :, :], base_sums[..., 1, :, :], base_sums[..., 2, :, :]
    n = n[:, None]
    cov = spy - sp * sum_y / n
    with np.errstate(invalid="ignore", divide="ignore"):
        return cov / np.sqrt((spp - sp ** 2 / n) * (sum_yy - sum_y ** 2 / n))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, choices=["swap", "perturb"])
    ap.add_argument("--s6-dir", required=True, help="S6 결과 폴더(ex) <output_root>/s6_brain_sampling_main)")
    ap.add_argument("--design-freeze", default="")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--folds", default="")
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    c.guard(a.design_freeze)
    folds = [int(x) for x in a.folds.split(",")] if a.folds else list(range(1, c.N_FOLDS + 1))
    conditions = (SWAP_CONDITION,) if a.task == "swap" else PERTURB_CONDITIONS
    dirs = {(k, cond): model_dir(a.s6_dir, k, cond, a.seed) for k in folds for cond in conditions}
    inputs = {f"model:fold{k}:{cond}": d / "model.pt" for (k, cond), (d, _) in dirs.items()}
    inputs.update({"pairs": c.S2 / "pairs_directed.tsv", "roi_table": c.S2 / "roi_table.tsv", "cabnp": c.S2 / "cabnp_groups.tsv", "labels": c.LABELS})
    run = Run(a.design_freeze, inputs, task=a.task, s6_dir=str(a.s6_dir), seed=a.seed, control_repeats=ac.CONTROL_REPEATS, perturb_repeats=PERTURB_REPEATS, s6_run_keys={f"{k}:{cond}": rk for (k, cond), (_, rk) in dirs.items()})
    variant = Path(a.s6_dir).name
    pairs_table = pd.read_csv(c.S2 / "pairs_directed.tsv", sep="\t")
    for k in folds:
        out = OUT / a.task / variant / f"outer_fold{k}_seed{a.seed}"
        if c.done_or_new(out, run.key):
            continue
        started = time.time()
        split, fd = load_fold(k, a.s6_dir, a.device)
        rows = fd.rows("test")
        models = {}
        for cond in conditions:
            path, _ = dirs[(k, cond)]
            model, meta = M.load_checkpoint(path / "model.pt", a.device)
            if meta["condition"] != cond or meta["seed"] != a.seed:
                raise ValueError(f"{path}: 체크포인트의 조건이나 seed가 다르다")
            names = ("z", "g", "v_hat", "c_hat") if model.readout.has_feature_head else ("z", "g")
            check_against_saved(path, fd, rows, {n: v.numpy() for n, v in T.collect(model, rows, T.brain_forward(fd), CHUNK, names).items()}, names)
            models[cond] = model
        with c.Atomic(out) as tmp:
            if a.task == "swap":
                path, _ = dirs[(k, SWAP_CONDITION)]
                res, log = swap_fold(models[SWAP_CONDITION], fd, split, k, a.seed, c.sha256(path / "model.pt")[:16], pairs_table)
                torch.save({pid: vars(r) for pid, r in res.items()}, tmp / "interventions.pt")
                pd.DataFrame(log).to_csv(tmp / "pairs_used.tsv", sep="\t", index=False)
            else:
                np.savez(tmp / "perturb_sums.npz", **perturb_fold(models, fd, split, k))
            run.check()
            json.dump(dict(run.prov, **c.timing(started), fold=k), open(tmp / "done.json", "w"), indent=1)
        print("저장", out, f"{time.time() - started:.0f}초", flush=True)
        del fd, models
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
