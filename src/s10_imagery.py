#!/usr/bin/env python3
"""S10 MC 회상(imagery) 분석 (01 6-3, 석진 님 결정 11/17. 탐색 분석. 질문과 판정은 회상 자료를 보기 전에 01에 적었다). GPU 없음.

모델: 6-3의 MC 전이 모델 A-1(brain_only), C-1(brain_decoded), seed 0~2. HK 공유 부분과 시청 자료로 맞춘 입력층(input_layer.pt)까지 모두 고정한다.
  입력 표준화는 6-3과 같다(그 참가자 시청 학습, 검증 2,108개의 voxel 통계, s8_mc_transfer.mc_fold).
  확인: 같은 모델에 시청 시험 입력을 넣은 예측이 s8_mc에 저장된 예측(chosen_input_wd)과 같아야 한다. 다르면 멈춘다.
회상 입력: MC 회상 run의 블록 반응(시청 v2와 같은 계산과 QC, 레포 밖 --imagery-dir/sub-XX/). 시청 QC 반응 배열과 열이 같다.
  영상마다 QC를 통과한 회상 블록(최대 5회)을 평균한다(MC 원문과 같음). 시험 영상 72개의 순서는 6-3과 같다.
단서 입력(보조): 같은 방식으로 단서 문장을 읽는 블록(trial_type −2)의 평균. 01 6-3의 단서 구간 대 회상 구간 점검용이고 판정에 쓰지 않는다.
채점: 6-3과 같다. 정서별 Pearson r(72개 영상), 72개에서 사람 평정이 상수인 정서와 예측이 상수인 정서는 그 단위의 평균에서 뺀다. 34개 평균이 참가자 점수.
  seed 3개의 r을 평균한 값이 참가자 값이고, 6명 평균이 집단 값이다.
판정(01 6-3의 문장 그대로)
- Q1 회상 반응에서 정서 평정을 읽는가(A-1, C-1 각각): 6명 평균이 순열 기준보다 높고(p < .05), 6명 가운데 4명 이상이 양수.
  순열은 6-3과 같다(72개 영상 안에서 사람 평정 벡터를 섞음, st.block_permutations, PERM_SEED 20261116, 10,000회, 6명과 seed에 같은 순열).
- Q2 회상에서도 C-1 > A-1인가: 6명 평균 차이의 구간이 0 위(72개 영상 bootstrap, BOOT_SEED 20261115, 10,000회, basic 95%), seed 3개 모두 6명 평균 차이 > 0,
  6명 가운데 5명 이상이 양수(seed 평균).
- Q3 어떤 정서가 남는가: 정서마다 V/C 지수(imagery_prereg)와 "시청 r − 회상 r"(6명 평균, seed 평균)의 Spearman ρ가 음수이고,
  34개 정서 이름표 순열(PERM_SEED, 10,000회) 한쪽 p < .05. 01이 모델을 정하지 않아, 회상 자료를 보기 전에(11/17) A-1을 판정에 쓰고 C-1은 같은 계산을 보고한다.
  판정에 쓰지 않고 함께 적는 것: 시청 r 순위를 통제한 편상관(시청에서 높았던 정서일수록 떨어질 폭이 크다는 것만으로 생기는 관계인지 보기 위함).
- Q4(보조) 어디에 남는가: 6-3의 MC 개인 모델 교란과 같은 네트워크 ablation(CAB-NP 13개 입력 열을 같은 참가자의 다른 시험 영상 값으로 바꿈, 20회,
  자기 자신으로 가지 않는 순열, seed 0)을 시청 입력과 회상 입력에 각각 걸어 하락을 비교한다. 판정 없음.
출력(레포 밖 --out): scores.tsv(단위마다 점수), q1.tsv, q2.tsv, q3.tsv, per_emotion.tsv, cue.tsv, ablation.tsv, repeats.tsv, verification.tsv, run_info.json
사용: s10_imagery.py --final <s6_brain_final_for_mc> --mc-dir <s8_mc> --imagery-dir <회상 반응 폴더> --vc-index <vision_over_caption_index.tsv> --out <폴더> --design-freeze <커밋>
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
import s6_train as T
import s8_mc_individual as I8
import s8_mc_transfer as M8
import s10_stats as st

CONDS = {"brain_only": "A-1", "brain_decoded": "C-1"}
SEEDS = (0, 1, 2)
BOOT_SEED, PERM_SEED, ABL_SEED = 20261115, 20261116, 20261117
N_ABL = 20
PARTS = ("01", "02", "03", "04", "05", "06")


def block_means(imagery_dir, s, kind, video_ids, unique):
    """그 종류(imagery, cue)의 블록 반응을 영상마다 QC 통과 블록으로 평균한다. 돌려주는 값: (72, 열), 영상마다 반복 수."""
    d = Path(imagery_dir) / f"sub-{s}"
    if not (d / "SUCCESS.json").exists():
        raise SystemExit(f"{d}: 회상 반응이 끝나지 않았다")
    b = pd.read_csv(d / f"sub-{s}_blocks.tsv", sep="\t")
    b = b[b.kind == kind].reset_index(drop=True)
    Z = np.load(d / f"sub-{s}_{kind}_runz.npy", mmap_mode="r")
    if len(Z) != len(b) or not np.array_equal(b.kind_row.to_numpy(), np.arange(len(b))):
        raise ValueError(f"sub-{s} {kind}: 블록 표와 배열이 맞지 않는다")
    X, n = [], []
    for v in video_ids:
        rows = np.flatnonzero((b.video_id == v).to_numpy() & b.usable.to_numpy())
        n.append(len(rows))
        X.append(np.asarray(Z[rows][:, unique], np.float64).mean(0) if len(rows) else np.full(len(unique), np.nan))
    X = np.stack(X).astype(np.float32)
    if np.isnan(X).all(1).any() or not np.isfinite(X[np.array(n) > 0]).all():
        raise ValueError(f"sub-{s} {kind}: 쓸 수 있는 블록이 없는 영상이 있거나 값에 NaN이 있다")
    return X, np.array(n)


def models_for(final, mc_dir, cond, seed, pid, counts):
    sel = json.loads((Path(final) / cond / "selected.json").read_text())
    hk, _ = M.load_checkpoint(Path(final) / sel["seeds"][str(seed)] / "model.pt", device="cpu")
    m = M8.adapt(hk, pid, counts)
    own = m.state_dict()
    d = Path(mc_dir) / cond / f"seed{seed}" / pid
    own.update(torch.load(d / "input_layer.pt", map_location="cpu"))
    m.load_state_dict(own)
    done = json.loads((d / "done.json").read_text())
    saved = np.load(d / f"test_pred_wd{float(done['chosen_input_wd']):g}.npz")
    return m.eval(), saved


def scores(y, p, rating_const):
    r = st.pearson_columns(y, p)
    keep = ~rating_const & np.isfinite(r)
    return r, keep


def run(final, mc_dir, imagery_dir, vc_path, out, n_boot, n_perm):
    torch.set_num_threads(16)
    final = Path(final) / "final_for_mc"  # s8_mc_individual.main과 같은 규칙(--final은 s6_brain_final_for_mc)
    spec_batch = 256
    names = pd.read_csv(c.LABEL_MAP, sep="\t").name.tolist()
    P, ver, rep_rows, abl_rows = {}, [], [], []
    y_ref = None
    for s in PARTS:
        pid = f"mc-{s}"
        data, tg, stats = I8.load_inputs(Path(final), s)
        z = np.load(M8.roi_path(s))
        unique = np.unique(z["columns"])
        X_img, n_img = block_means(imagery_dir, s, "imagery", data["video_te"], unique)
        X_cue, n_cue = block_means(imagery_dir, s, "cue", data["video_te"], unique)
        rep_rows += [dict(participant=pid, video_id=int(v), n_imagery=int(a), n_cue=int(b)) for v, a, b in zip(data["video_te"], n_img, n_cue)]
        y = tg["y_te"].astype(np.float64)
        if y_ref is None:
            y_ref, vid_ref = y, data["video_te"]
        elif not (np.array_equal(vid_ref, data["video_te"]) and np.allclose(y_ref, y)):
            raise ValueError("참가자마다 시험 영상 순서가 다르다")
        fds = {kind: M8.mc_fold(pid, dict(data, X_te=X), tg, stats, "cpu") for kind, X in (("perception", data["X_te"]), ("imagery", X_img), ("cue", X_cue))}
        test = fds["perception"].rows("test")
        nets = I8.network_columns(data["positions"])
        perms = I8.derangements(len(test), N_ABL, np.random.default_rng([ABL_SEED, int(s)]))
        for cond in CONDS:
            for seed in SEEDS:
                m, saved = models_for(final, mc_dir, cond, seed, pid, fds["perception"].voxel_counts[pid])
                for kind, fd in fds.items():
                    fw = T.brain_forward(fd)
                    p = I8.predict(m, fd, pid, test, fw, spec_batch)
                    P[kind, cond, seed, pid] = p
                    if kind == "perception":
                        if not np.array_equal(saved["video_id"], fd.row_video[test]):
                            raise ValueError(f"{pid} {cond} seed {seed}: 시험 영상 순서가 저장 예측과 다르다")
                        dmax = float(np.abs(p - saved["p"]).max())
                        ver.append(dict(participant=pid, condition=CONDS[cond], seed=seed, max_abs_vs_saved=dmax))
                        if dmax > 1e-4:
                            raise ValueError(f"{pid} {cond} seed {seed}: 시청 예측이 6-3 저장 예측과 다르다({dmax:.2e})")
                    if seed == 0 and kind in ("perception", "imagery"):
                        r0 = float(np.nanmean(st.pearson_columns(y, p)))
                        x0 = fd.x[pid].clone()
                        tr = torch.as_tensor(test)
                        for g, cols in nets.items():
                            ct = torch.as_tensor(cols)
                            drops = []
                            for perm in perms:
                                x = x0.clone()
                                x[tr[:, None], ct[None, :]] = x0[tr[torch.as_tensor(perm)][:, None], ct[None, :]]
                                fd.x[pid] = x
                                drops.append(r0 - float(np.nanmean(st.pearson_columns(y, I8.predict(m, fd, pid, test, fw, spec_batch)))))
                            fd.x[pid] = x0
                            abl_rows.append(dict(participant=pid, model=CONDS[cond], input=kind, network=g, r_base=r0, drop=float(np.mean(drops))))
        print(f"{pid} 끝", flush=True)
    pids = [f"mc-{s}" for s in PARTS]
    rating_const = st.constant_columns(y_ref)
    W = st.bootstrap_counts(72, n_boot, np.random.default_rng(BOOT_SEED)).astype(np.float64)
    perm = st.block_permutations(np.zeros(72, int), n_perm, np.random.default_rng(PERM_SEED))

    # 단위마다 점수, bootstrap, 순열
    sc, sb, sn, rr, ss, score_rows = {}, {}, {}, {}, {}, []
    for kind in ("perception", "imagery", "cue"):
        for cond in CONDS:
            for q in pids:
                rs, bs, ns = [], [], []
                for seed in SEEDS:
                    p = P[kind, cond, seed, q]
                    r, keep = scores(y_ref, p, rating_const)
                    rs.append(np.where(keep, r, np.nan))
                    bs.append(st.mean_over(st.boot_r(W, y_ref, {"p": p})["p"], keep))
                    ns.append(st.mean_over(st.permuted_r(perm, np.arange(72), y_ref, {"p": p})["p"], keep))
                    ss[kind, cond, seed, q] = float(np.nanmean(rs[-1]))
                    score_rows.append(dict(input=kind, model=CONDS[cond], seed=seed, participant=q, score_r=ss[kind, cond, seed, q], n_emotions=int(keep.sum())))
                rr[kind, cond, q] = np.nanmean(np.stack(rs), 0)  # seed 평균 정서별 r
                sc[kind, cond, q] = float(np.mean([np.nanmean(x) for x in rs]))
                sb[kind, cond, q] = np.mean(bs, 0)
                sn[kind, cond, q] = np.mean(ns, 0)
            sc[kind, cond, "mean"] = float(np.mean([sc[kind, cond, q] for q in pids]))
            sb[kind, cond, "mean"] = np.mean([sb[kind, cond, q] for q in pids], 0)
            sn[kind, cond, "mean"] = np.mean([sn[kind, cond, q] for q in pids], 0)
            rr[kind, cond, "mean"] = np.nanmean(np.stack([rr[kind, cond, q] for q in pids]), 0)

    def q1_table(kind, label):
        rows = []
        for cond, name in CONDS.items():
            for q in pids + ["mean"]:
                lo, hi = st.basic_ci(sc[kind, cond, q], sb[kind, cond, q])
                rows.append(dict(question=label, input=kind, model=name, participant=q, score_r=sc[kind, cond, q], ci_low=float(lo), ci_high=float(hi),
                                 null_mean=float(np.nanmean(sn[kind, cond, q])), p_perm=float(st.permutation_p(sc[kind, cond, q], sn[kind, cond, q]))))
            n_pos = sum(sc[kind, cond, q] > 0 for q in pids)
            m = rows[-1]
            m.update(n_positive=int(n_pos), decision=("읽음" if (m["p_perm"] < .05 and n_pos >= 4) else "옮겨 가지 않음") if kind == "imagery" else "")
        return rows

    q1 = pd.DataFrame(q1_table("imagery", "Q1") + q1_table("perception", "기준(시청)"))
    cue = pd.DataFrame(q1_table("cue", "단서 구간(보조)"))

    # Q2
    d_q = {q: sc["imagery", "brain_decoded", q] - sc["imagery", "brain_only", q] for q in pids + ["mean"]}
    db = sb["imagery", "brain_decoded", "mean"] - sb["imagery", "brain_only", "mean"]
    lo, hi = st.basic_ci(d_q["mean"], db)
    per_seed = {seed: float(np.mean([ss["imagery", "brain_decoded", seed, q] - ss["imagery", "brain_only", seed, q] for q in pids])) for seed in SEEDS}
    n_pos = sum(d_q[q] > 0 for q in pids)
    ok = lo > 0 and all(v > 0 for v in per_seed.values()) and n_pos >= 5
    q2 = pd.DataFrame([dict(question="Q2", comparison="C-1 − A-1 (회상)", estimate=d_q["mean"], ci_low=float(lo), ci_high=float(hi), p=float(st.centered_p(d_q["mean"], db)),
                            seed0=per_seed[0], seed1=per_seed[1], seed2=per_seed[2], n_positive=int(n_pos), per_participant=json.dumps({q: round(d_q[q], 4) for q in pids}),
                            decision="C-1 > A-1" if ok else "아님")])

    # Q3
    vc = pd.read_csv(vc_path, sep="\t").set_index("emotion").loc[names, "vision_over_caption"].to_numpy(np.float64)
    q3 = []
    for cond, name in CONDS.items():
        pr, im = rr["perception", cond, "mean"], rr["imagery", cond, "mean"]
        drop = pr - im
        m = np.isfinite(drop) & np.isfinite(vc)
        rv, rd = st_rank(vc[m]), st_rank(drop[m])
        rho = float(np.corrcoef(rv, rd)[0, 1])
        g = np.random.default_rng(PERM_SEED)
        null = np.array([np.corrcoef(rv, rd[g.permutation(len(rd))])[0, 1] for _ in range(n_perm)])
        p = float((1 + (null <= rho).sum()) / (1 + n_perm))
        part = float(np.corrcoef(resid_rank(vc[m], pr[m]), resid_rank(drop[m], pr[m]))[0, 1])
        q3.append(dict(question="Q3", model=name, used_for_decision=name == "A-1", n_emotions=int(m.sum()), rho=rho, p_one_sided_negative=p,
                       partial_rho_given_perception_r=part, decision=("남는 쪽은 상황(의미)으로 정해지는 정서" if (rho < 0 and p < .05) else "아님") if name == "A-1" else ""))
    per = pd.DataFrame([dict(emotion=names[e], vision_over_caption=vc[e], **{f"{k}_{CONDS[cd]}": rr[k, cd, "mean"][e] for k in ("perception", "imagery", "cue") for cd in CONDS}) for e in range(len(names))])

    o = Path(out)
    o.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(score_rows).to_csv(o / "scores.tsv", sep="\t", index=False)
    q1.to_csv(o / "q1.tsv", sep="\t", index=False)
    q2.to_csv(o / "q2.tsv", sep="\t", index=False)
    pd.DataFrame(q3).to_csv(o / "q3.tsv", sep="\t", index=False)
    per.to_csv(o / "per_emotion.tsv", sep="\t", index=False)
    cue.to_csv(o / "cue.tsv", sep="\t", index=False)
    pd.DataFrame(abl_rows).to_csv(o / "ablation.tsv", sep="\t", index=False)
    pd.DataFrame(rep_rows).to_csv(o / "repeats.tsv", sep="\t", index=False)
    pd.DataFrame(ver).to_csv(o / "verification.tsv", sep="\t", index=False)
    return dict(n_boot=n_boot, n_perm=n_perm, boot_seed=BOOT_SEED, perm_seed=PERM_SEED, ablation_seed=ABL_SEED, n_ablation=N_ABL, rating_constant=[names[e] for e in np.flatnonzero(rating_const)])


def st_rank(x):
    return pd.Series(x).rank().to_numpy()


def resid_rank(x, z):
    rx, rz = st_rank(x), st_rank(z)
    A = np.column_stack([np.ones_like(rz), rz])
    return rx - A @ np.linalg.lstsq(A, rx, rcond=None)[0]


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 MC 회상 분석")
    ap.add_argument("--final", required=True)
    ap.add_argument("--mc-dir", required=True)
    ap.add_argument("--imagery-dir", required=True)
    ap.add_argument("--vc-index", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", required=True)
    ap.add_argument("--n-boot", type=int, default=st.N_RESAMPLE)
    ap.add_argument("--n-perm", type=int, default=st.N_RESAMPLE)
    a = ap.parse_args(argv)
    c.guard(a.design_freeze)
    started = time.time()
    info = run(a.final, a.mc_dir, a.imagery_dir, a.vc_index, a.out, a.n_boot, a.n_perm)
    info.update(stage="S10 MC 회상", final=str(a.final), mc_dir=str(a.mc_dir), vc_index_sha256=c.sha256(Path(a.vc_index)), design_freeze=a.design_freeze,
                code_commit=c.START_HEAD, code_dirty=c.START_DIRTY, elapsed_seconds=round(time.time() - started, 1))
    (Path(a.out) / "run_info.json").write_text(json.dumps(info, indent=1, ensure_ascii=False))
    print(f"끝: {info['elapsed_seconds']}초", flush=True)


if __name__ == "__main__":
    main()
