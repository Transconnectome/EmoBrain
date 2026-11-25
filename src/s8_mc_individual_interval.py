#!/usr/bin/env python3
"""S8 MC 개인 모델의 예측(01 6-4e (라): 연합 − 시각의 "개인 − 공유" 하락)에 붙이는 bootstrap 구간 (2026-11-25). GPU 없음.

s8_mc_individual.perturb는 네트워크마다 하락(순열 20회 평균)만 저장하고 판정 규칙의 구간을 내지 않았다. 같은 모델, 같은 순열(PERM_SEED)로 교란을 다시 걸고
72개 영상 bootstrap 10,000회(BOOT_SEED)로 참가자 평균의 basic 95% 구간을 낸다. 하락은 순열 20회의 평균이므로 재표집에서도 20회를 평균한다.
확인: 다시 낸 하락이 저장된 perturb_drops.tsv와 같아야 한다(CPU와 GPU의 차이만 허용, 1e-3을 넘으면 멈춘다).
출력: <out>/prediction_interval.tsv
사용(src에서): s8_mc_individual_interval.py --final <s6_brain_final_for_mc> --transfer <s8_mc> --individual <s8_mc_individual> --out <perturb 폴더> [--threads 16]
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

import s6_common as S
import s6_model as M
import s6_train as T
import s8_mc_individual as I8
import s8_mc_transfer as M8
import s10_stats as st


def main():
    ap = argparse.ArgumentParser(description="MC 개인 모델 예측의 bootstrap 구간")
    ap.add_argument("--final", required=True)
    ap.add_argument("--transfer", required=True)
    ap.add_argument("--individual", required=True)
    ap.add_argument("--out", required=True, help="perturb_drops.tsv가 있는 폴더")
    ap.add_argument("--threads", type=int, default=16)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    final, out = Path(a.final) / "final_for_mc", Path(a.out)
    W = st.bootstrap_counts(72, st.N_RESAMPLE, np.random.default_rng(I8.BOOT_SEED)).astype(float)
    spec, nets_used = S.Spec(), I8.ASSOC + I8.VISUAL
    saved = pd.read_csv(out / "perturb_drops.tsv", sep="\t").set_index(["participant", "condition", "model", "network"])["drop"]
    est, boot, diff, t0 = {}, {}, 0.0, time.time()
    for s in M8.MC:
        pid = f"mc-{s}"
        data, tg, stats = I8.load_inputs(final, s)
        fd = M8.mc_fold(pid, data, tg, stats, "cpu")
        test, y = fd.rows("test"), tg["y_te"].astype(float)
        nets = I8.network_columns(data["positions"])
        perms = I8.derangements(len(test), I8.N_PERM, np.random.default_rng([I8.PERM_SEED, int(s)]))
        x0, fw, tr = fd.x[pid].clone(), T.brain_forward(fd), torch.as_tensor(test)
        for cond in I8.CONDITIONS:
            sel = json.loads((final / cond / "selected.json").read_text())
            hk, _ = M.load_checkpoint(final / sel["seeds"][str(I8.SEED)] / "model.pt", device="cpu")
            shared = M8.adapt(hk, pid, fd.voxel_counts[pid])
            own = shared.state_dict()
            own.update(torch.load(Path(a.transfer) / cond / f"seed{I8.SEED}" / pid / "input_layer.pt", map_location="cpu"))
            shared.load_state_dict(own)
            ind, _ = M.load_checkpoint(Path(a.individual) / cond / f"seed{I8.SEED}" / pid / "model.pt", device="cpu")
            val = {}
            for kind, model in (("shared", shared), ("individual", ind)):
                base = I8.predict(model, fd, pid, test, fw, spec.batch)
                r0, b0 = st.pearson_columns(y, base).mean(), st.boot_r(W, y, {"p": base})["p"].mean(1)
                for g in nets_used:
                    ct, d, bd = torch.as_tensor(nets[g]), [], []
                    for perm in perms:
                        x = x0.clone()
                        x[tr[:, None], ct[None, :]] = x0[tr[torch.as_tensor(perm)][:, None], ct[None, :]]
                        fd.x[pid] = x
                        p = I8.predict(model, fd, pid, test, fw, spec.batch)
                        d.append(r0 - st.pearson_columns(y, p).mean())
                        bd.append(b0 - st.boot_r(W, y, {"p": p})["p"].mean(1))
                    fd.x[pid] = x0
                    val[kind, g] = (float(np.mean(d)), np.mean(bd, 0))
                    diff = max(diff, abs(val[kind, g][0] - float(saved[pid, cond, kind, g])))

            def contrast(k):
                part = {n: np.mean([val["individual", g][k] - val["shared", g][k] for g in group], 0) for n, group in (("assoc", I8.ASSOC), ("visual", I8.VISUAL))}
                return part["assoc"] - part["visual"]
            est[cond, pid], boot[cond, pid] = float(contrast(0)), contrast(1)
            print(pid, cond, round(est[cond, pid], 4), f"{time.time() - t0:.0f}초", flush=True)
    if diff > 1e-3:
        raise SystemExit(f"저장된 하락 값과 다르다(최대 {diff:.2e})")
    rows = []
    for cond in I8.CONDITIONS:
        e = [est[cond, f"mc-{s}"] for s in M8.MC]
        lo, hi = st.basic_ci(float(np.mean(e)), np.mean([boot[cond, f"mc-{s}"] for s in M8.MC], 0))
        rows.append(dict(condition=cond, assoc_minus_visual=float(np.mean(e)), ci_low=float(lo), ci_high=float(hi), n_positive=int((np.array(e) > 0).sum()), n=len(e)))
    pd.DataFrame(rows).to_csv(out / "prediction_interval.tsv", sep="\t", index=False)
    print(pd.DataFrame(rows).to_string(index=False), f"\n저장 값과의 최대 차이 {diff:.2e}")


if __name__ == "__main__":
    main()
