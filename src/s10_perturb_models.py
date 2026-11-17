#!/usr/bin/env python3
"""S10 네트워크 교란의 모델 확장과 정서 head 입력 표현 유사도 (01 6-4e (나), (다), 11/17). GPU 없음. 입력은 s9_perturb_models.py의 저장 결과.

질문(석진 님 11/17): 34개 평균 성능이 비슷한 모델들이 같은 뇌 영역을 같은 방식으로 쓰는가, 같은 표현을 배웠는가.

(나) 네트워크 교란
- 모델: A-1(기준), C-1, B-1, D-4, E-고정, E-학습(seed 0). 계산은 6-4b(s10_perturb)와 같다.
  참가자마다 6 fold의 영상을 모아 정서별 r을 내고, 점수는 모든 모델에서 원래 예측의 r을 계산할 수 있는 정서의 평균이다.
  하락 = 원래 점수 − 교란 점수를 반복마다 내고 20회를 평균한다. 하락폭 차이 = 모델의 하락 − A-1의 하락.
- 재표집: 6-4b와 같은 영상 단위 bootstrap(canonical_id 묶음, BOOT_SEED 20261115, 10,000회, 모든 모델, 묶음, 5명에 같은 뽑힌 횟수). 배정표는 고정(6-4b의 fixed).
  basic 95% 구간, 중심 맞춘 양측 p. Holm은 모델마다 13묶음(5명 평균), 참가자마다도 같은 묶음으로 센다.
- 예측과 판정(실행 전, 11/17)
  - D-4: A-1보다 Visual2 교란에 더 크게 떨어지고(하락폭 차이 > 0), Default 교란에는 덜 떨어진다(< 0).
    둘 다 예측한 방향이고 Holm p < .05면 "맞음", 둘 가운데 하나라도 반대 방향으로 Holm p < .05면 "반대", 나머지는 "보류".
    Visual1(> 0)과 Cingulo-Opercular(< 0)는 같은 방향의 예측이고 판정에는 쓰지 않고 함께 보고한다.
  - B-1, E-고정, E-학습: 방향 예측이 없다. Holm p < .05인 묶음을 보고한다. C-1은 6-4b에서 이미 했고 같은 값이 나오는지 확인용이다.
(다) 정서 head 입력 표현의 유사도
- 표현: 정서 query의 출력 o(행 × 34·d). 같은 fold(같은 모델), 같은 참가자의 시험 영상에서 두 모델의 linear CKA(Kornblith 외 2019, 행 평균을 뺀 Gram 행렬의 정규화 내적).
  참가자마다 6 fold 평균, 그다음 5명 평균. D-4는 짝 모델 4개 각각과의 CKA를 평균한다(D-4 대각은 짝 사이 CKA 평균).
- 기준: A-1과 A-1 depth2, A-1 depth4(같은 후보 설정에서 encoder block 수만 다름)의 CKA. 정서를 직접 맞히도록 학습한 같은 종류의 모델끼리 얼마나 같은지의 값이다.
- 판정(모델마다, A-1과의 CKA): 5명 모두 CKA(A-1, 모델) < 그 참가자의 min(CKA(A-1, depth2), CKA(A-1, depth4))이면 "A-1과 다른 표현",
  5명 모두 그 이상이면 "A-1 변형 수준", 나머지는 "보류".
- 예측(실행 전, 11/17): D-4는 "A-1과 다른 표현". B-1, E-고정, E-학습은 "A-1 변형 수준". C-1은 예측 없음.
- 한계: seed가 하나라 같은 설정의 seed 사이 CKA는 없다. depth 기준은 구조도 다르다(기준이 낮게 나올 수 있는 쪽).
확인: A-1, C-1의 원래 예측과 13묶음 교란 예측이 6-4b(S9 perturb, --s9-dir)의 저장 값과 같아야 한다(같은 배정표). 다르면 멈춘다.
출력(레포 밖 --out): network_drops.tsv, prediction.tsv, cka.tsv(모델 쌍, 참가자마다), cka_decision.tsv, verification.tsv, run_info.json
사용: s10_perturb_models.py --perturb-dir <s9_perturb_models 출력> --s9-dir <6-4b S9 perturb 폴더> --out <폴더> --design-freeze <커밋> [--workers 5]
"""
import argparse
import json
import multiprocessing as mp
import time
from pathlib import Path

import numpy as np
import pandas as pd

import s4_common as c
import s10_stats as st

BOOT_SEED = 20261115
MODELS = {"brain_only": "A-1", "brain_decoded": "C-1", "brain_only_featdec": "B-1", "brain_frozen_feature_encoder": "D-4",
          "brain_only_repr_frozen": "E-고정", "brain_only_repr_trained": "E-학습"}
REF = "brain_only"
CKA_NAMES = ["A-1", "C-1", "B-1", "D-4", "E-고정", "E-학습", "A-1 depth2", "A-1 depth4"]
REPR_KEY = {v: k for k, v in MODELS.items()} | {"A-1 depth2": "depth2", "A-1 depth4": "depth4"}
PRED_UNITS = {"Visual2": 1, "Default": -1}  # 판정
ALSO = {"Visual1": 1, "Cingulo-Opercular": -1}  # 함께 보고


def load(perturb_dir, s9_dir, split):
    """fold마다의 저장 결과를 읽고 6-4b와 대조한다. 돌려주는 값: 참가자 -> dict(video_id, y, base{조건}, pert{조건}), 단위 이름, 표현(fold, 참가자 -> 이름 -> 배열), 확인 표."""
    import s9_saved_models as S9
    by_q, reprs, ver, units = {}, {}, [], None
    for k in range(1, 7):
        d = Path(perturb_dir) / f"outer_fold{k}_seed0"
        if not (d / "done.json").exists():
            raise SystemExit(f"{d}: 결과가 없다")
        z = np.load(d / "pred.npz")
        pid, vid = z["participant"].astype(str), z["video_id"].astype(np.int64)
        if units is None:
            units = z["unit_name"].astype(str)
        elif not np.array_equal(units, z["unit_name"].astype(str)):
            raise ValueError("fold마다 묶음 순서가 다르다")
        y = S9.test_ratings(split, vid)
        pert = {cond: np.load(d / f"perturbed_{cond}.npy", mmap_mode="r") for cond in MODELS}
        # 6-4b와 대조
        s9 = Path(s9_dir) / f"outer_fold{k}_seed0"
        old = np.load(s9 / "perturb_pred.npz")
        same_rows = np.array_equal(old["participant"].astype(str), pid) and np.array_equal(old["video_id"].astype(np.int64), vid)
        same_units = np.array_equal(old["unit_name"].astype(str)[:13], units)
        for cond in ("brain_only", "brain_decoded"):
            ob = np.asarray(old[f"{cond}_base"], np.float64)
            op = np.load(s9 / f"perturb_pred_{cond}.npy", mmap_mode="r")[:13]
            db = float(np.abs(ob - z[f"{cond}_base"]).max())
            dp = float(np.abs(np.asarray(op, np.float64) - np.asarray(pert[cond], np.float64)).max())
            ver.append(dict(fold=k, condition=MODELS[cond], same_rows=same_rows, same_units=same_units, max_abs_base=db, max_abs_perturbed=dp))
            if not (same_rows and same_units and db < 1e-5 and dp < 1e-5):
                raise ValueError(f"fold {k} {cond}: 6-4b 저장 값과 다르다 (행 {same_rows}, 단위 {same_units}, {db:.2e}, {dp:.2e})")
        r = np.load(d / "repr.npz")
        for q in np.unique(pid):
            m = pid == q
            e = by_q.setdefault(q, dict(video_id=[], y=[], base={x: [] for x in MODELS}, pert={x: [] for x in MODELS}))
            e["video_id"].append(vid[m])
            e["y"].append(y[m])
            for cond in MODELS:
                e["base"][cond].append(np.asarray(z[f"{cond}_base"], np.float64)[m])
                e["pert"][cond].append(np.asarray(pert[cond][:, :, m], np.float32))
            rep = {n: np.asarray(r[REPR_KEY[n]], np.float64)[m] for n in CKA_NAMES if n != "D-4"}
            pair_keys = [x for x in r.files if x.startswith("brain_frozen_feature_encoder|")]
            if len(pair_keys) != 4:
                raise ValueError(f"fold {k}: D-4 짝 표현이 4개가 아니다 ({r.files})")
            rep.update({"D-4|" + x.split("|")[1]: np.asarray(r[x], np.float64)[m] for x in pair_keys})
            reprs[k, q] = rep
    out = {}
    for q, e in by_q.items():
        v = np.concatenate(e["video_id"])
        o = np.argsort(v)
        out[q] = dict(video_id=v[o], y=np.concatenate(e["y"])[o],
                      base={x: np.concatenate(e["base"][x])[o] for x in MODELS},
                      pert={x: np.concatenate(e["pert"][x], axis=2)[:, :, o] for x in MODELS})
    return out, units, reprs, pd.DataFrame(ver)


JOBS = []  # fork로 넘기는 참가자별 입력(복사하지 않음)


def participant_boot(i):
    """참가자 하나: 모델마다 묶음별 하락의 점추정과 bootstrap. 돌려주는 값: (점 하락 {조건: 13}, 재표집 하락 {조건: (13, B)}, 쓴 정서 수)."""
    e, W = JOBS[i]
    y = e["y"]
    keep = np.ones(y.shape[1], bool)
    for cond in MODELS:
        keep &= np.isfinite(st.pearson_columns(y, e["base"][cond]))
    point, boot = {}, {}
    for cond in MODELS:
        base_r = st.pearson_columns(y, e["base"][cond])
        base_b = st.mean_over(st.boot_r(W, y, {"b": e["base"][cond]})["b"], keep)
        P = e["pert"][cond]
        n_u, n_t = P.shape[:2]
        pt = np.empty((n_u, n_t))
        pb = np.empty((n_u, n_t, W.shape[0]))
        for u in range(n_u):
            for t in range(n_t):
                p = np.asarray(P[u, t], np.float64)
                pt[u, t] = st.mean_over(st.pearson_columns(y, p), keep)
                pb[u, t] = st.mean_over(st.boot_r(W, y, {"p": p})["p"], keep)
        point[cond] = st.mean_over(base_r, keep) - pt.mean(1)
        boot[cond] = base_b[None] - pb.mean(1)
    return point, boot, int(keep.sum())


def cka(X, Y):
    X = X - X.mean(0)
    Y = Y - Y.mean(0)
    K, L = X @ X.T, Y @ Y.T
    return float((K * L).sum() / np.sqrt((K * K).sum() * (L * L).sum()))


def cka_tables(reprs):
    rows = []
    for (k, q), R in reprs.items():
        get = lambda n: [R[x] for x in sorted(R) if x.startswith("D-4|")] if n == "D-4" else [R[n]]
        for i, a in enumerate(CKA_NAMES):
            for b in CKA_NAMES[i:]:
                if a == b == "D-4":
                    xs = get("D-4")
                    v = np.mean([cka(xs[s], xs[t]) for s in range(4) for t in range(s + 1, 4)])
                elif a == b:
                    continue
                else:
                    v = np.mean([cka(x, w) for x in get(a) for w in get(b)])
                rows.append(dict(fold=k, participant=q, model_a=a, model_b=b, cka=v))
    t = pd.DataFrame(rows)
    per = t.groupby(["participant", "model_a", "model_b"], as_index=False).cka.mean()
    mean5 = per.groupby(["model_a", "model_b"], as_index=False).cka.mean().assign(participant="mean5")
    return pd.concat([per, mean5], ignore_index=True)


def cka_decide(cka_t):
    per = cka_t[cka_t.participant != "mean5"]
    vsA = per[per.model_a == "A-1"].pivot_table(index="participant", columns="model_b", values="cka")
    ref = vsA[["A-1 depth2", "A-1 depth4"]].min(1)
    rows = []
    pred = {"D-4": "A-1과 다른 표현", "B-1": "A-1 변형 수준", "E-고정": "A-1 변형 수준", "E-학습": "A-1 변형 수준"}
    for m in ("C-1", "B-1", "D-4", "E-고정", "E-학습"):
        below = (vsA[m] < ref)
        dec = "A-1과 다른 표현" if below.all() else ("A-1 변형 수준" if (~below).all() else "보류")
        rows.append(dict(model=m, cka_mean5=float(vsA[m].mean()), reference_min_mean5=float(ref.mean()), n_participants_below_reference=int(below.sum()),
                         decision=dec, prediction=pred.get(m, "예측 없음"), prediction_held=("" if m not in pred else dec == pred[m])))
    return pd.DataFrame(rows)


def run(perturb_dir, s9_dir, out, workers, n_boot):
    split = c.load_split()
    data, units, reprs, ver = load(perturb_dir, s9_dir, split)
    pids = sorted(data)
    U = np.array(sorted(set().union(*[set(data[q]["video_id"].tolist()) for q in pids])), np.int64)
    sp = split.set_index("video_id").loc[U]
    codes, n_units = st.unit_codes(sp.canonical_id.to_numpy())
    W = st.bootstrap_counts(n_units, n_boot, np.random.default_rng(BOOT_SEED)).astype(np.float64)
    JOBS[:] = [(data[q], W[:, codes[np.searchsorted(U, data[q]["video_id"])]]) for q in pids]
    with mp.get_context("fork").Pool(workers) as pool:
        res = dict(zip(pids, pool.map(participant_boot, range(len(pids)))))
    rows = []
    for who in pids + ["mean5"]:
        if who == "mean5":
            pt = {m: np.mean([res[q][0][m] for q in pids], 0) for m in MODELS}
            bt = {m: np.mean([res[q][1][m] for q in pids], 0) for m in MODELS}
            n_emo = np.nan
        else:
            pt, bt, n_emo = res[who]
        for m in MODELS:
            lo, hi = st.basic_ci(pt[m], bt[m].T)
            p = st.centered_p(pt[m], bt[m].T)
            if m == REF:
                dlo = dhi = dp = dph = np.full(len(units), np.nan)
                d = np.full(len(units), np.nan)
            else:
                d, db = pt[m] - pt[REF], (bt[m] - bt[REF]).T
                dlo, dhi = st.basic_ci(d, db)
                dp = st.centered_p(d, db)
                dph = st.holm(dp)
            for u, name in enumerate(units):
                rows.append(dict(participant=who, model=MODELS[m], unit=name, drop=pt[m][u], drop_ci_low=lo[u], drop_ci_high=hi[u], drop_p=p[u],
                                 diff_vs_A1=d[u], diff_ci_low=dlo[u], diff_ci_high=dhi[u], diff_p=dp[u], diff_p_holm13=dph[u], n_emotions=n_emo))
    drops = pd.DataFrame(rows)
    m5 = drops[(drops.participant == "mean5") & (drops.model == "D-4")].set_index("unit")
    sig = lambda u, s: (np.sign(m5.loc[u, "diff_vs_A1"]) == s) and (m5.loc[u, "diff_p_holm13"] < .05)
    opp = lambda u, s: (np.sign(m5.loc[u, "diff_vs_A1"]) == -s) and (m5.loc[u, "diff_p_holm13"] < .05)
    dec = "맞음" if all(sig(u, s) for u, s in PRED_UNITS.items()) else ("반대" if any(opp(u, s) for u, s in PRED_UNITS.items()) else "보류")
    pred = []
    for u, s in (PRED_UNITS | ALSO).items():
        n_q = 0
        for q in pids:
            x = drops[(drops.participant == q) & (drops.model == "D-4") & (drops.unit == u)].iloc[0]
            n_q += int(np.sign(x.diff_vs_A1) == s and x.diff_p_holm13 < .05)
        pred.append(dict(model="D-4", unit=u, predicted_sign=s, used_for_decision=u in PRED_UNITS, diff_vs_A1=m5.loc[u, "diff_vs_A1"], ci_low=m5.loc[u, "diff_ci_low"],
                         ci_high=m5.loc[u, "diff_ci_high"], p_holm13=m5.loc[u, "diff_p_holm13"], n_participants_predicted_sign_holm=n_q, decision=dec))
    cka_t = cka_tables(reprs)
    o = Path(out)
    o.mkdir(parents=True, exist_ok=True)
    drops.to_csv(o / "network_drops.tsv", sep="\t", index=False)
    pd.DataFrame(pred).to_csv(o / "prediction.tsv", sep="\t", index=False)
    cka_t.to_csv(o / "cka.tsv", sep="\t", index=False)
    cka_decide(cka_t).to_csv(o / "cka_decision.tsv", sep="\t", index=False)
    ver.to_csv(o / "verification.tsv", sep="\t", index=False)
    return dict(participants=pids, n_bootstrap_units=n_units, n_boot=n_boot, boot_seed=BOOT_SEED, units=units.tolist())


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 네트워크 교란 모델 확장과 표현 유사도")
    ap.add_argument("--perturb-dir", required=True)
    ap.add_argument("--s9-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", required=True)
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--n-boot", type=int, default=st.N_RESAMPLE)
    a = ap.parse_args(argv)
    c.guard(a.design_freeze)
    started = time.time()
    info = run(a.perturb_dir, a.s9_dir, a.out, a.workers, a.n_boot)
    info.update(stage="S10 네트워크 교란 모델 확장과 표현 유사도", perturb_dir=str(a.perturb_dir), s9_dir=str(a.s9_dir), design_freeze=a.design_freeze,
                code_commit=c.START_HEAD, code_dirty=c.START_DIRTY, elapsed_seconds=round(time.time() - started, 1))
    (Path(a.out) / "run_info.json").write_text(json.dumps(info, indent=1, ensure_ascii=False))
    print(f"끝: {info['elapsed_seconds']}초", flush=True)


if __name__ == "__main__":
    main()
