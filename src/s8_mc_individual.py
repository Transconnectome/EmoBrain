#!/usr/bin/env python3
"""S8 MC 개인 모델과 네트워크 교란: 공통과 개인차 (11/17 석진 님 결정. 6-3 결과를 본 뒤 더한 탐색 분석).

질문(석진 님 11/17): 사람들이 공유하는 정서 관련 정보는 어떤 정보이고, 사람마다 다른 부분은 뇌 영역 어디에서 나오는가?
- 공통 모델: 6-3의 전이 모델(HK 5명의 공유 부분을 고정하고 MC 참가자의 ROI 입력층만 맞춤, s8_mc). 이미 있다.
- 개인 모델: 같은 구조(HK 최종 모델의 spec, d, rank, tokenizer, voxel 뽑기)를 MC 참가자 한 명의 자료(시청 학습 2,108개)만으로 처음부터 학습한다.
  설정(learning rate, 입력층 weight decay, λ)은 HK 최종 모델이 고른 값을 그대로 쓰고 참가자마다 다시 고르지 않는다(결과를 보고 고르지 않으려고).
  학습, 검증, 시험 행과 표준화는 6-3과 같다(s8_mc_transfer.mc_fold). 조건은 A-1(brain_only), C-1(brain_decoded), seed 0.
  01의 "참가자별 모델은 만들지 않는다"는 본 모델에 대한 결정이다. 여기서는 공통 모델과 비교하는 대조로만 쓴다(석진 님 11/17).
- 네트워크 교란(6-4b와 같은 방식, 학습 없음): MC 시험 영상 72개에서 한 네트워크(CAB-NP 13개)의 ROI 입력을 같은 참가자의 다른 시험 영상
  값으로 바꾸고(영상 순열, 20회, seed 고정, 자기 자신으로 가지 않는 순열), 34개 정서 평균 r의 하락을 낸다. 바꾸는 곳은 입력층 앞(voxel)이다.
  공통 모델(seed 0)과 개인 모델에 같은 순열을 쓴다.

미리 적는 예측과 판정(11/17, 계산 전. 결과를 보고 바꾸지 않는다)
- 질문 1(공통은 무엇인가): C-1 공통 모델의 decoded features(Vision, Caption)가 MC 시험 영상의 실제 feature와 맞는다(6-3의 mc_decoding, 이미 있음).
  여기서 새로 보는 것은 질문 2다.
- 질문 2(개인차는 어디서 나오나): 네트워크마다 "개인 모델의 교란 하락 − 공통 모델의 교란 하락"을 낸다. 양수면 그 네트워크의 정보를
  개인 모델이 더 쓰는 것이고, 공통 구조로 담기지 않는 그 사람만의 정보가 거기 있다는 뜻으로 읽는다.
  - 예측: 이 값의 연합 네트워크(Default, Frontoparietal, Cingulo-Opercular, Language) 평균이 시각 네트워크(Visual1, Visual2) 평균보다 크다.
    근거는 휴지기 연결의 개인차가 연합 피질에서 가장 크다는 보고(Mueller 외, 2013)다. 정서 부호에 대한 근거는 아니다.
  - 판정: A-1과 C-1 각각에서, 6명 가운데 5명 이상이 같은 방향이고 6명 평균의 bootstrap 구간(72개 영상, 10,000회)이 0 위면 맞는 것으로 본다.
    (11/25 S1을 빼면서 5명 가운데 4명 이상, 5명 평균으로 읽는다. 01 6-3)
- 전체 성능(개인 − 공통)은 방향을 정하지 않고 보고한다. 개인 모델은 입력층 weight decay를 고르지 않아 공통 모델보다 불리할 수 있다(공통은 6개 후보에서 고름).
- 쓰는 문장의 범위: 정답이 모든 사람에게 같은 규범 평정이므로, "사람마다 다르게 느낀다"가 아니라 "같은 장면 평정을 예측하는 뇌 정보가 사람마다
  다른 방식으로 담긴 곳"이다.

사용(run worktree의 src에서):
  python s8_mc_individual.py train --final <s6_brain_final_for_mc> --out <s8_mc_individual> --participants 02 --design-freeze <커밋> [--device cuda]
  python s8_mc_individual.py perturb --final <s6_brain_final_for_mc> --transfer <s8_mc> --individual <s8_mc_individual> --out <폴더> --design-freeze <커밋>
"""
import argparse
import dataclasses
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
import s8_mc_transfer as M8
import s10_stats as st

CONDITIONS = ("brain_only", "brain_decoded")
SEED = 0
N_PERM = 20
PERM_SEED = 20261117
BOOT_SEED = 20261115
ASSOC = ("Default", "Frontoparietal", "Cingulo-Opercular", "Language")
VISUAL = ("Visual1", "Visual2")


def fresh(hk_model, pid, counts):
    """HK 최종 모델과 같은 구조로 새로 초기화한 모델. 모든 가중치를 학습한다."""
    spec = {k: v for k, v in hk_model.spec.items() if k != "kind"}
    if hk_model.spec.get("kind") != "brain":
        raise ValueError("개인 모델은 뇌 모델(A-1, C-1)만 만든다")
    spec["voxel_counts"] = {pid: list(counts)}
    model = M.BrainModel(**spec)
    for p in model.parameters():
        p.requires_grad_(True)
    return model


def load_inputs(final, s):
    blocks, repeats, idmap = (pd.read_csv(p, sep="\t") for p in (M8.MC_BLOCKS, M8.MC_REPEATS, M8.ID_MAP))
    mc72_table = pd.read_csv(d5.MC72, sep="\t")
    mc72 = S.mc_video_ids()
    split = c.load_split()
    stats = dict(np.load(final / "plan" / "standardization.npz"))
    stats = {k: stats[k] for k in ("visual_mean", "visual_std", "caption_mean", "caption_std")}
    data = M8.load_mc(s, blocks, repeats, idmap, mc72)
    tg = M8.targets(data["video_tv"], data["video_te"], idmap, split, stats, mc72_table)
    return data, tg, stats


def train(final, out, parts, freeze, device):
    spec = S.Spec()
    for s in parts:
        pid = f"mc-{s}"
        data, tg, stats = load_inputs(final, s)
        fd = M8.mc_fold(pid, data, tg, stats, device)
        for cond in CONDITIONS:
            sel = json.loads((final / cond / "selected.json").read_text())
            ckpt = final / sel["seeds"][str(SEED)] / "model.pt"
            hk_model, hk_meta = M.load_checkpoint(ckpt, device="cpu")
            cand = dict(hk_meta["candidate"])
            out_dir = Path(out) / cond / f"seed{SEED}" / pid
            inputs = {"hk_checkpoint_spec": ckpt, "mc_blocks": M8.MC_BLOCKS, "mc_repeats": M8.MC_REPEATS, "id_map": M8.ID_MAP, "mc72": d5.MC72,
                      "response": M8.response_path(s), "roi": M8.roi_path(s), "code_s8i": Path(__file__).resolve()}
            run = S.Run(freeze, inputs, task="mc_individual", condition=cond, seed=SEED, participant=pid, candidate=cand, spec=dataclasses.asdict(spec))
            if c.done_or_new(out_dir, run.key):
                print(f"끝난 단위 건너뜀 {out_dir}", flush=True)
                continue
            started = time.time()
            with c.Atomic(out_dir) as tmp:
                T.seed_everything(SEED)
                model = fresh(hk_model, pid, fd.voxel_counts[pid]).to(fd.device)
                forward = T.brain_forward(fd)
                res = T.fit(model, fd, spec, lr=float(cand["lr"]), input_wd=float(cand["input_wd"]), feature_wd=cand.get("feature_wd"),
                            loss_fn=T.make_loss(cond, cand, fd), forward=forward, seed=SEED, restore_fn=T.total_val_loss(cond, cand, fd, forward, spec.batch))
                model.eval()
                names = ("z", "v_hat", "c_hat") if cond == "brain_decoded" else ("z",)
                test = fd.rows("test")
                with torch.no_grad():
                    o = T.collect(model, test, forward, spec.batch, names)
                np.savez(tmp / "test_pred.npz", video_id=fd.row_video[test], z=o["z"].numpy(), p=torch.sigmoid(o["z"]).numpy(),
                         **({"v_hat": o["v_hat"].numpy(), "c_hat": o["c_hat"].numpy()} if "v_hat" in o else {}))
                torch.save(dict(spec=dict(model.spec), state_dict=model.state_dict(), meta=dict(candidate=cand, condition=cond, participant=pid)), tmp / "model.pt")
                r = M8.pearson_cols(torch.sigmoid(o["z"]).numpy(), tg["y_te"])
                run.check()
                json.dump(dict(run.prov, condition=cond, seed=SEED, participant=pid, candidate=cand, val_score=res.val_score, best_epoch=res.best_epoch,
                               test_mean_r=float(np.nanmean(r)), seconds=time.time() - started), open(tmp / "done.json", "w"), indent=1, default=str)
            print(f"저장 {out_dir} 검증 r {res.val_score:.4f} 시험 r {np.nanmean(r):.4f} ({time.time() - started:.0f}초)", flush=True)


def network_columns(positions):
    """네트워크 이름 -> 입력 열(그 네트워크 ROI들의 voxel 열 합집합). MC의 positions는 ROI 표 순서다."""
    roi = pd.read_csv(c.S2 / "roi_table.tsv", sep="\t").sort_values("roi_index")
    if len(roi) != len(positions):
        raise ValueError("ROI 표의 ROI 수가 MC 자료와 다르다")
    return {g: np.unique(np.concatenate([positions[int(i)] for i in rows.roi_index])) for g, rows in roi.groupby("group", sort=False)}


def derangements(n, k, rng):
    out = []
    while len(out) < k:
        p = rng.permutation(n)
        if not (p == np.arange(n)).any():
            out.append(p)
    return np.stack(out)


def predict(model, fd, pid, test, forward, batch):
    model.eval()
    with torch.no_grad():
        return torch.sigmoid(T.collect(model, test, forward, batch, ("z",))["z"]).numpy().astype(np.float64)


def perturb(final, transfer, individual, out, parts, device):
    spec = S.Spec()
    rows = []
    preds = {}
    for s in parts:
        pid = f"mc-{s}"
        data, tg, stats = load_inputs(final, s)
        fd = M8.mc_fold(pid, data, tg, stats, device)
        test = fd.rows("test")
        y = tg["y_te"].astype(np.float64)
        nets = network_columns(data["positions"])
        perms = derangements(len(test), N_PERM, np.random.default_rng([PERM_SEED, int(s)]))
        x0 = fd.x[pid].clone()
        forward = T.brain_forward(fd)
        for cond in CONDITIONS:
            sel = json.loads((final / cond / "selected.json").read_text())
            hk_model, _ = M.load_checkpoint(final / sel["seeds"][str(SEED)] / "model.pt", device="cpu")
            shared = M8.adapt(hk_model, pid, fd.voxel_counts[pid])
            own = shared.state_dict()
            own.update(torch.load(Path(transfer) / cond / f"seed{SEED}" / pid / "input_layer.pt", map_location="cpu"))
            shared.load_state_dict(own)
            ind, _ = M.load_checkpoint(Path(individual) / cond / f"seed{SEED}" / pid / "model.pt", device="cpu")
            for kind, model in (("shared", shared.to(fd.device)), ("individual", ind.to(fd.device))):
                base = predict(model, fd, pid, test, forward, spec.batch)
                r0 = float(np.nanmean(M8.pearson_cols(base, y)))
                preds[f"{pid}|{cond}|{kind}|base"] = base
                for g, cols in nets.items():
                    drops = []
                    for b, perm in enumerate(perms):
                        x = x0.clone()
                        tr = torch.as_tensor(test, device=x.device)
                        ct = torch.as_tensor(cols, device=x.device)
                        x[tr[:, None], ct[None, :]] = x0[tr[torch.as_tensor(perm, device=x.device)][:, None], ct[None, :]]
                        fd.x[pid] = x
                        p = predict(model, fd, pid, test, forward, spec.batch)
                        drops.append(r0 - float(np.nanmean(M8.pearson_cols(p, y))))
                        if b == 0:
                            preds[f"{pid}|{cond}|{kind}|{g}"] = p
                    fd.x[pid] = x0
                    rows.append(dict(participant=pid, condition=cond, model=kind, network=g, n_columns=len(cols), r_base=r0, drop=float(np.mean(drops)), drop_sd=float(np.std(drops))))
                print(f"{pid} {cond} {kind}: r {r0:.3f}", flush=True)
    o = Path(out)
    o.mkdir(parents=True, exist_ok=True)
    D = pd.DataFrame(rows)
    D.to_csv(o / "perturb_drops.tsv", sep="\t", index=False)
    piv = D.pivot_table(index=["participant", "condition", "network"], columns="model", values="drop").reset_index()
    piv["individual_minus_shared"] = piv["individual"] - piv["shared"]
    piv.to_csv(o / "perturb_difference.tsv", sep="\t", index=False)
    summ = []
    for cond in CONDITIONS:
        q = piv[piv.condition == cond]
        per = q.groupby("participant").apply(lambda t: t.set_index("network").individual_minus_shared.reindex(ASSOC).mean()
                                             - t.set_index("network").individual_minus_shared.reindex(VISUAL).mean(), include_groups=False)
        summ.append(dict(condition=cond, assoc_minus_visual=float(per.mean()), n_positive=int((per > 0).sum()), n=len(per), per_participant=json.dumps(per.round(4).to_dict())))
    pd.DataFrame(summ).to_csv(o / "prediction.tsv", sep="\t", index=False)
    base = D.drop_duplicates(["participant", "condition", "model"])[["participant", "condition", "model", "r_base"]]
    base.to_csv(o / "scores.tsv", sep="\t", index=False)
    np.savez(o / "preds.npz", **preds)


def main():
    ap = argparse.ArgumentParser(description="MC 개인 모델과 네트워크 교란")
    ap.add_argument("step", choices=["train", "perturb"])
    ap.add_argument("--final", required=True, help="HK 최종 모델 결과 폴더(s6_brain_final_for_mc)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--transfer", help="6-3 전이 결과(s8_mc)")
    ap.add_argument("--individual", help="개인 모델 결과(이 스크립트 train의 --out)")
    ap.add_argument("--participants", default=",".join(M8.MC))
    ap.add_argument("--design-freeze", default="")
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    c.guard(a.design_freeze)
    parts = [x for x in a.participants.split(",") if x]
    if set(parts) - set(M8.MC):
        raise SystemExit("MC 참가자는 02~06이다(S1은 11/25 결정으로 뺌)")
    final = Path(a.final) / "final_for_mc"
    if a.step == "train":
        train(final, a.out, parts, a.design_freeze, a.device)
    else:
        perturb(final, a.transfer, a.individual, a.out, parts, a.device)


if __name__ == "__main__":
    main()
