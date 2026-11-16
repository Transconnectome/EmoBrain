#!/usr/bin/env python3
"""S9 바꿔 끼우기의 Stimulus Model 기준선 (11/16 석진 님. 01 2-2, 1-1의 해석 한계 보완). GPU 없음, 학습 없음.

왜 하나: 뇌 모델(C-1)의 2-2에서 캡션 쪽 교체 효과가 시각 쪽보다 컸다. 그런데 Caption feature는 1차 시각 ROI에서도 Vision feature보다 잘 읽혀,
  이 차이가 뇌의 성질인지 두 특징 표현의 성질인지 나눌 수 없다. 그래서 같은 교체를 실제 특징으로 학습한 Stimulus Model(S4)에 해서,
  특징에 decoding 오차가 없을 때 시각과 캡션 교체가 정서 예측을 얼마나 움직이는지를 기준으로 둔다.
무엇을 같게 두나(뇌 모델 2-2와 바로 비교하려고)
- 짝: S2 pairs_directed.tsv의 그 fold 짝 가운데 그 참가자에게 두 영상이 모두 있는 것. 순서도 같다.
- 영상 순서: 합친 S6 폴더의 plan/rows.npz 시험 행 순서(뇌 모델 2-2가 쓴 순서).
- 무작위 대조: audition_codex.interchange_intervention과 같은 방식과 같은 seed(s9_saved_models.fixed_seed("swap", 참가자, fold, seed))로
  다른 시험 영상 C를 뽑고, C의 실제 특징 쪽으로 실제 교체와 같은 길이만큼 옮긴다(O3, length_matched_change).
  --brain-swap-dir를 주면 뽑힌 C가 뇌 모델 2-2의 저장 값(control_indices)과 같은지 확인하고, 다르면 멈춘다.
- 저장 형식: audition_codex.FoldInterventions와 같은 키. 그래서 통계는 s10_swap.py를 그대로 쓴다.
무엇이 다르나
- 입력은 뇌에서 decoding한 v̂, ĉ가 아니라 실제 Vision feature와 Caption feature이고, K1 head 눈금(S4 coordinates.npz, D_k 통계)으로 바꾼 값이다.
- 뇌 경로 g가 없다. 정서 = Stimulus Model head(v, c). I는 logit으로 낸다(I = z(B, B) − z(B, A) − z(A, B) + z(A, A), 괄호는 (시각 출처, 캡션 출처)).
- fold k의 head는 D_k(시험 fold k를 뺀 개발 영상)로 학습한 것이다(S4 stimulus/fold<k>). 읽은 head는 S4가 저장한 시험 예측과 같은지 확인한다(s9_path_eval.check_heads).
- head 두 판(더하기판 r = 0, 상호작용판 r ∈ {1, 2, 4, 8})을 따로 낸다. S4가 고른 판(chosen.json의 all_ranks)을 run_info에 적는다.
출력(레포 밖 --out): <head>/outer_fold<k>_seed0/{interventions.pt, done.json}. s10_swap.py --swap-dir <out>/<head>로 통계를 낸다.
사용: s9_stimulus_swap.py --s6-dir <합친 S6 폴더> --out <출력 폴더> --design-freeze <커밋> [--s4-dir <S4 결과 폴더>] [--brain-swap-dir <S9 swap 폴더>] [--overwrite]
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

import s4_common as c
import s6_model as M
import s10_inputs as I
import s9_path_eval as PE
from s9_saved_models import fixed_seed

ac = M.ac
SEED = 0  # 뇌 모델 2-2가 쓴 seed(seed 1, 2는 11/15에 미룸)
HEADS = PE.HEADS
CONTROL_REPEATS = 100  # O3
DV = PE.DV
CODE_FILES = ("s9_stimulus_swap.py", "s9_path_eval.py", "s9_saved_models.py", "s10_inputs.py", "s4_feature_model.py", "s4_common.py")


def code_hashes():
    return {n: c.sha256(c.CODE_DIR / n) for n in CODE_FILES}


def control_indices(n, pairs, control_seed):
    """audition_codex.interchange_intervention과 같은 규칙으로 대조 영상 C를 뽑는다(같은 seed면 같은 C)."""
    generator = torch.Generator(device="cpu").manual_seed(control_seed)
    out = torch.empty(CONTROL_REPEATS, len(pairs), dtype=torch.long)
    for j, (ai, bi) in enumerate(pairs.tolist()):
        eligible = torch.tensor([i for i in range(n) if i not in (ai, bi)])
        out[:, j] = eligible[torch.randint(len(eligible), (CONTROL_REPEATS,), generator=generator)]
    return out


def head_logit(model, v, c):
    """K1 head 눈금의 시각, 캡션 입력 -> logit(float32 계산, S4 predict와 같음)."""
    with torch.no_grad():
        return model(v.float(), c.float()).double()


def swap_2x2(model, va, ca, vb, cb):
    """audition_codex.swap_2x2와 같은 배열(쌍, 시각 출처 A/B, 캡션 출처 A/B, 정서). 뇌 경로 g는 없다."""
    z_aa, z_ab = head_logit(model, va, ca), head_logit(model, va, cb)
    z_ba, z_bb = head_logit(model, vb, ca), head_logit(model, vb, cb)
    z = torch.stack((torch.stack((z_aa, z_ab), 1), torch.stack((z_ba, z_bb), 1)), 1)
    return z, z.sigmoid(), (z_bb - z_ba) - (z_ab - z_aa)


def intervene(model, x, ratings, pairs, *, video_ids, participant, fold, control_seed, checkpoint_id):
    """x: K1 head 눈금의 (영상, 9,728) 실제 특징. 돌려주는 값: FoldInterventions."""
    n = x.shape[0]
    if n < 3:
        raise ValueError("O3는 서로 다른 A, B, C가 필요하다(영상 3개 이상)")
    a, b = pairs[:, 0], pairs[:, 1]
    v, cc = x[:, :DV], x[:, DV:]
    c_idx = control_indices(n, pairs, control_seed)
    va, ca, vb, cb = v[a], cc[a], v[b], cc[b]
    z, p, I_ = swap_2x2(model, va, ca, vb, cb)
    lengths = torch.stack((torch.linalg.vector_norm(vb - va, dim=-1), torch.linalg.vector_norm(cb - ca, dim=-1)), -1)
    cz, cp, cI, cl = [], [], [], []
    for cs in c_idx:
        v_r, _ = ac.length_matched_change(va, vb, v[cs])
        c_r, _ = ac.length_matched_change(ca, cb, cc[cs])
        rz, rp, ri = swap_2x2(model, va, ca, v_r, c_r)
        cz.append(rz)
        cp.append(rp)
        cI.append(ri)
        cl.append(torch.stack((torch.linalg.vector_norm(v_r - va, dim=-1), torch.linalg.vector_norm(c_r - ca, dim=-1)), -1))
    cp = torch.stack(cp)
    return ac.FoldInterventions(participant, fold, SEED, checkpoint_id, tuple(int(i) for i in video_ids), pairs, c_idx,
                                z.float(), p.float(), I_.float(), ac._delta_p(p).float(), (ratings[b] - ratings[a]).float(),
                                lengths.float(), torch.stack(cz).float(), cp.float(), torch.stack(cI).float(), ac._delta_p(cp).float(),
                                torch.stack(cl).float(), control_seed)


def test_rows_in_order(s6_dir, k):
    """합친 S6 폴더 plan/rows.npz의 시험 행을 참가자마다 그 순서대로(뇌 모델 2-2가 쓴 순서)."""
    path = Path(s6_dir) / f"outer_fold{k}" / "plan" / "rows.npz"
    r = np.load(path, allow_pickle=True)
    keep = np.asarray(r["role"]) == I.PLAN_ROLES["test"]
    pids, vids = np.asarray(r["participant"])[keep], np.asarray(r["video_id"], np.int64)[keep]
    order = []
    for q in pids:
        if q not in order:
            order.append(q)
    return {q: vids[pids == q].tolist() for q in order}, path


def run(s4_dir, s6_dir, out, split, *, brain_swap_dir=None, overwrite=False, design_freeze=None):
    started = time.time()
    out = Path(out)
    if out.exists() and any(out.iterdir()) and not overwrite:
        raise SystemExit(f"{out}가 비어 있지 않다. --overwrite를 주면 덮어쓴다")
    inputs = PE.Inputs()
    pairs_path = inputs.add(c.S2 / "pairs_directed.tsv")
    pairs_table = pd.read_csv(pairs_path, sep="\t")
    y, _ = c.load_scores(split, "emotions")
    y = np.asarray(y, np.float64)
    ypos = {v: i for i, v in enumerate(split.video_id.astype(int).tolist())}
    fold_of = dict(zip(split.video_id.astype(int), split.fold.astype(int)))
    chosen, log, checked = {}, [], 0
    for k in range(1, I.N_FOLDS + 1):
        fh = PE.load_fold_heads(s4_dir, k, inputs)
        fold_videos = sorted(v for v, f in fold_of.items() if f == k)
        PE.check_heads(fh, k, split, fold_videos)
        ch = json.loads(inputs.add(Path(s4_dir) / "stimulus" / f"fold{k}" / "chosen.json").read_text())
        chosen[k] = "additive" if float(ch["all_ranks"]["r"]) == 0 else "interaction"
        coord = fh["stimulus"]["coord"]
        by_q, rows_path = test_rows_in_order(s6_dir, k)
        inputs.add(rows_path)
        brain = None
        if brain_swap_dir is not None:
            brain = torch.load(inputs.add(Path(brain_swap_dir) / f"outer_fold{k}_seed{SEED}" / "interventions.pt"), map_location="cpu", weights_only=False)
        pt = pairs_table[pairs_table.fold == k]
        results = {h: {} for h in HEADS}
        for q, vids in by_q.items():
            if any(fold_of[v] != k for v in vids):
                raise ValueError(f"fold {k} {q}: 시험 행에 fold {k}가 아닌 영상이 있다")
            local = {v: j for j, v in enumerate(vids)}
            keep = pt[pt.video_a.isin(local) & pt.video_b.isin(local)]
            pairs = torch.tensor([[local[u], local[w]] for u, w in zip(keep.video_a, keep.video_b)], dtype=torch.long)
            feats = I.actual_features(split, vids)
            x = torch.as_tensor(PE.to_head(np.concatenate([feats["vision"], feats["caption"]], 1), coord), dtype=torch.float64)
            ratings = torch.as_tensor(y[[ypos[v] for v in vids]], dtype=torch.float64)
            seed_c = fixed_seed("swap", q, k, SEED)
            for h in HEADS:
                res = intervene(fh["stimulus"]["heads"][h]["model"], x, ratings, pairs, video_ids=vids, participant=q, fold=k,
                                control_seed=seed_c, checkpoint_id=f"stimulus_{h}_fold{k}")
                results[h][q] = res
            if brain is not None:
                bx = brain[q]
                if tuple(int(v) for v in bx["video_ids"]) != tuple(vids) or not torch.equal(bx["pairs"], pairs) or not torch.equal(bx["control_indices"], res.control_indices):
                    raise ValueError(f"fold {k} {q}: 영상 순서, 짝, 대조 영상이 뇌 모델 2-2와 다르다")
                checked += 1
            log.append(dict(participant=q, fold=k, n_test=len(vids), n_pairs=len(keep), n_pairs_missing=len(pt) - len(keep), control_seed=seed_c))
        for h in HEADS:
            d = out / h / f"outer_fold{k}_seed{SEED}"
            d.mkdir(parents=True, exist_ok=True)
            torch.save({q: vars(r) for q, r in results[h].items()}, d / "interventions.pt")
            inputs.check()
            json.dump(dict(stage="S9 Stimulus Model 바꿔 끼우기 기준선", head=h, fold=k, seed=SEED, design_freeze=design_freeze, code_commit=c.START_HEAD,
                           code_dirty=c.START_DIRTY, code=code_hashes(), inputs=inputs.hashes, s4_dir=str(s4_dir), s6_dir=str(s6_dir)),
                      open(d / "done.json", "w"), indent=1, ensure_ascii=False)
    info = dict(stage="S9 Stimulus Model 바꿔 끼우기 기준선", s4_selected_head_by_fold=chosen, brain_swap_checked=checked,
                brain_swap_dir=str(brain_swap_dir) if brain_swap_dir else None, pairs_log=log, elapsed_seconds=round(time.time() - started, 1))
    (out / "run_info.json").write_text(json.dumps(info, indent=1, ensure_ascii=False, default=str))
    return info


def main(argv=None):
    ap = argparse.ArgumentParser(description="S9 바꿔 끼우기의 Stimulus Model 기준선")
    ap.add_argument("--s4-dir", default=str(PE.S4_DEFAULT))
    ap.add_argument("--s6-dir", required=True)
    ap.add_argument("--brain-swap-dir")
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", required=True)
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args(argv)
    c.guard(a.design_freeze)
    split = c.load_split()
    info = run(a.s4_dir, a.s6_dir, a.out, split, brain_swap_dir=a.brain_swap_dir, overwrite=a.overwrite, design_freeze=a.design_freeze)
    print(f"끝: {a.out} ({info['elapsed_seconds']}초, 뇌 모델 2-2와 대조한 참가자 × fold {info['brain_swap_checked']}개, S4가 고른 판 {info['s4_selected_head_by_fold']})")


if __name__ == "__main__":
    main()
