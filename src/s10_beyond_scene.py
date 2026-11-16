#!/usr/bin/env python3
"""S10 장면 표현으로 선형으로 얻어지지 않는 정서 평정 정보 (11/17 석진 님이 질문을 정함, 같은 날 비판 agent 검토 반영. 결과를 본 뒤 더한 탐색 분석). GPU 없음.

질문(석진 님 11/17): "뇌의 정서 정보는 장면 정보와 같은 것인가, 그 이상인가?"
이 자료로 답할 수 있는 꼴: "다른 사람들의 정서 평정을 예측하는 뇌 정보가, 풍부한 장면 표현에서 선형으로 얻어지는가?"
- 정답은 영상의 규범 평정이다. 평정자 잡음은 스캔 참가자의 뇌를 예측할 수 없으므로, 뇌로 읽히는 잔차는 "이 feature 집합이 선형으로 담지 못한
  장면 정보(빠진 feature, 비선형 조합)"다. 정서 경험과 장면 affordance를 구별하지 못한다.
- Horikawa 외(2020)와 Du 외(2023)의 transmodal 우위가, 그들이 쓴 통제(물체 DNN이나 motion energy, 이름표 73개)보다 풍부한 통제
  (V-JEPA 2의 Vision feature, 캡션 DeBERTa의 Caption feature)에서도 남는지를 본다.
- 01 1-3(11/1)은 "뇌의 정서 정보가 시각 정보와 의미 정보로 얼마나 설명되나"를 질문으로 두지 않기로 했다(이유 2 feature 집합의 성질, 이유 3 규범 평정).
  이 분석은 그 결정과 충돌하므로 탐색으로만 쓰고, 01에 석진 님 확인 필요로 적는다.
- encoding 방향의 ΔR²(장면 + 정서 − 장면)는 쓰지 않는다. 정서 평정이 장면 feature의 저차원 투영에 가까워, 34차원 band가 큰 band보다 덜 줄어드는
  것만으로 ΔR²가 생길 수 있다(비판 agent 11/17). 그래서 장면 feature로 교차 예측한 부분을 뺀 평정(잔차)을 뇌로 직접 읽는다.

장면 표현(S)
- Sw: motion energy(S3 lowlevel/motion_energy, 6,555) + 이름표 73개(Horikawa 공개 semantic_features). Du 외 2023의 통제와 같은 종류다.
- V: Vision feature(S3 vjepa2 target, 5,632). C: Caption feature(정서어 181개를 지운 deberta target, 4,096).
- Sall: Sw + V + C(band 4개). 한 번에 둘을 바꾸지 않도록 Sw를 포함한다(비판 agent 11/17).
- band마다 학습 행으로 표준화한다(학습 행에서 상수인 열은 0). kernel에서 band마다 trace가 같도록 band 무게를 p_전체 / (band 수 × p_band)로 둔다.
  전체 trace가 표준화한 feature를 그냥 붙였을 때와 같아서 λ 후보(O18)를 그대로 쓴다. band 하나면 s5_common.DualRidge와 같다.

목표(T): 정서 범주 34개 + valence + arousal.
1단계 targets(뇌 없음): 바깥 fold k마다 S → T ridge를 D_k로만 맞춘다(s10_rating_parts.crossfit과 같은 규칙. 안쪽 5겹 r 평균으로 목표마다 λ,
  D_k 행은 안쪽 겹의 바깥 예측, 시험 fold 행은 D_k 전체 규칙의 예측). 잔차 R_S = T − T̂_S. 시험 fold의 평정은 어느 규칙에도 들어가지 않는다.
- 조작 점검: 시험 fold를 모은 r(Sall → T) ≥ r(Sw → T)여야 한다. 아닌 목표는 Sw 대 Sall 대비가 무효다.
- 잔차 점검: Sall → R_Sall을 같은 규칙으로 다시 맞춰, 시험 r이 0.05를 넘는 목표는 Sall 주장에서 뺀다(축소 때문에 선형 정보가 남은 경우).
2단계 fit(참가자마다): 네트워크 13개(s10_geometry.network_positions)와 뇌 전체(모든 ROI의 voxel)로 T, R_Sw, R_V, R_C, R_Sall을
  ridge(s5_common.main_version, H2: 학습 fold 4개로 학습, 검증 fold로 목표마다 λ)로 읽는다. 6 fold 시험 예측을 모아 r을 한 번 낸다.
3단계 summarize: 5명 평균 r, bootstrap 95% 구간(같은 내용 영상 묶음 canonical_id, BOOT_SEED, 10,000회, 5명 같은 무게),
  한쪽 순열 p(시험 fold와 원래 run 안에서 영상과 목표 벡터의 대응을 섞음, 10,000회(I5), PERM_SEED, 5명 같은 순열, 예측은 그대로), 5명 부호 일치.
  11/17 첫 실행은 순열 1,000회로 적어 Holm 보정 p의 최솟값이 0.108이었다. 판정 규칙(구간, r, 부호)과 예측은 바꾸지 않고 횟수만 프로젝트 기준으로 고쳐 다시 돌렸다.
- 확인 묶음: Visual1, Visual2, Default × 목표 36개를 목표 판(T, R_Sw, R_V, R_C, R_Sall)마다 Holm. 나머지 네트워크와 뇌 전체는 탐색(BH).

미리 적는 판정 규칙과 예측(11/17, 계산 전. 결과를 보고 바꾸지 않는다)
- 목표, 네트워크, 잔차 판마다: 남음 = 5명 평균 r의 구간 하한 > 0, r ≥ 0.05, 5명 모두 양수. 흡수 = 구간 상한 < 0.05(Horikawa 영역 문턱
  r > 0.095의 약 절반). 그 밖은 판정 보류.
- 예측 1: R_Sw에서 Default는 정서 범주 34개의 절반 넘게가 남는다.
- 예측 2: R_Sall에서 Default는 판정할 수 있는 정서 범주(조작 점검과 잔차 점검을 통과한 것)의 3분의 1 미만이 남는다. 3분의 1 이상 남으면 틀린 예측이다.
- 예측 3: valence와 arousal의 잔차 decoding은 Visual1, Visual2, Default 모두에서 R_Sw보다 R_Sall에서 낮다(짝 bootstrap 구간이 0 위).
  rating_parts(01 6-4c)를 이미 봤으므로 눈가림이 아니다.
- 미리 적는 문장. 흡수되면 "이 네트워크에서 정서 평정과 관련된 정보는 장면 표현에서 선형으로 얻어진다. 이 자료로는 경험과 affordance를 구별할 수 없다."
  남으면 "이 네트워크는 이 feature로 선형으로 얻어지지 않는 평정 관련 정보를 담는다(빠진 feature, 비선형 조합, 공유 appraisal)."
- 질문 2(모델)의 null과의 관계는 "맞는다(consistent with)"까지만 쓰고 "설명한다"고 쓰지 않는다.

사용: s10_beyond_scene.py targets --out <폴더> --design-freeze <커밋> [--threads 16]
      s10_beyond_scene.py fit --participant 01 --out <폴더> --design-freeze <커밋> [--threads 16]
      s10_beyond_scene.py summarize --out <폴더> --design-freeze <커밋>
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

import paths as P
import s4_common as c
import s5_common as d5
import s10_geometry as geo
import s10_geometry_checks as gc
import s10_stats as st

NE = 34
DIMS = ("valence", "arousal")
SEMANTIC = P.DATA_ROOT / "Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/semantic_features.csv"
SETS = {"Sw": ("motion", "labels"), "V": ("vision",), "C": ("caption",), "Sall": ("motion", "labels", "vision", "caption")}
READ = ("T", "Sw", "V", "C", "Sall")  # 뇌로 읽는 목표 판. T는 평정 그대로, 나머지는 그 장면 표현의 잔차
CONFIRM = ("Visual1", "Visual2", "Default")
WHOLE = "whole_brain"
SURVIVE_R = 0.05
SANITY_R = 0.05
PERM_SEED = 20261116  # s10_performance.PERM_SEED와 같은 값
N_PERM = st.N_RESAMPLE  # I5. 11/17 첫 실행은 1,000회였다. Holm 108개에서 보정 p가 0.108 아래로 내려갈 수 없어, 판정 규칙은 그대로 두고 프로젝트 기준으로 고쳤다
PERM_CHUNK = 100


def target_names(split):
    T, names, dnames = geo.targets(split, split.video_id.to_numpy())
    return names + list(DIMS)


def load_targets(split, vid):
    T, names, dnames = geo.targets(split, vid)
    return np.c_[T[:, :NE], T[:, [NE + dnames.index(d) for d in DIMS]]]


def load_bands(split):
    """장면 band. 행은 split 순서."""
    vid = split.video_id.to_numpy()
    s = pd.read_csv(SEMANTIC)
    ids = s.iloc[:, 0].str.replace("stimulus_", "").astype(int).to_numpy()
    if not (ids == np.arange(1, 2197)).all():
        raise ValueError("이름표 73개 표의 행이 video_id 1~2196이 아니다")
    labels = s.iloc[:, 1:].to_numpy(np.float64)[vid - 1]
    if labels.shape[1] != 73 or not np.isfinite(labels).all():
        raise ValueError("이름표가 73개가 아니거나 NaN이 있다")
    return dict(motion=np.asarray(c.load_rows("lowlevel/motion_energy", vid, split), np.float64), labels=labels,
                vision=np.asarray(c.load_rows(c.VISUAL_TARGET, vid, split), np.float64),
                caption=np.asarray(c.load_rows(c.CAPTION_NO_EMOTION, vid, split), np.float64))


def band_kernel(bands, train, rows_list):
    """band마다 train 행으로 표준화(상수 열 0)하고, trace가 같도록 무게를 준 kernel. 돌려주는 값: K(train, train), [K(rows, train) ...]."""
    total, nb = sum(b.shape[1] for b in bands), len(bands)
    tr = torch.as_tensor(train)
    Ktr, cross = None, [None] * len(rows_list)
    for b in bands:
        x = torch.as_tensor(b, dtype=torch.float64)
        m, s = x[tr].mean(0), x[tr].std(0, unbiased=False)
        keep = s > 0
        z = torch.zeros_like(x)
        z[:, keep] = (x[:, keep] - m[keep]) / s[keep]
        w = total / (nb * b.shape[1])
        ztr = z[tr]
        k = w * (ztr @ ztr.T)
        Ktr = k if Ktr is None else Ktr + k
        for i, r in enumerate(rows_list):
            kr = w * (z[torch.as_tensor(r)] @ ztr.T)
            cross[i] = kr if cross[i] is None else cross[i] + kr
    return Ktr, cross


def kernel_paths(Ktr, crosses, y_tr):
    """λ 후보마다 예측. 돌려주는 값: [ (λ 수, 행, 목표) for each cross ]."""
    vals, vecs = torch.linalg.eigh(Ktr)
    vals = vals.clamp_min(0)
    ym = y_tr.mean(0)
    uty = vecs.T @ (y_tr - ym)
    out = []
    for cr in crosses:
        cv = cr @ vecs
        out.append(torch.stack([ym + cv @ ((1 / (vals + float(lam)))[:, None] * uty) for lam in d5.LAMBDAS]))
    return out


def crossfit_banded(bands, y, fold, k):
    """s10_rating_parts.crossfit과 같은 규칙을 band kernel로. y는 numpy(영상 × 목표). 돌려주는 값: numpy(영상 × 목표)."""
    y = torch.as_tensor(np.asarray(y, np.float64))
    dk_folds = [f for f in range(1, c.N_FOLDS + 1) if f != k]
    dk, te = np.flatnonzero(np.isin(fold, dk_folds)), np.flatnonzero(fold == k)
    L = len(d5.LAMBDAS)
    oof = torch.zeros((L, len(fold), y.shape[1]), dtype=torch.float64)
    scores = []
    for j in dk_folds:
        tr, va = dk[fold[dk] != j], dk[fold[dk] == j]
        Ktr, (cva,) = band_kernel(bands, tr, [va])
        (paths,) = kernel_paths(Ktr, [cva], y[tr])
        oof[:, va] = paths
        scores.append(torch.stack([d5.r_selection(y[va], paths[i]) for i in range(L)]))
    pick = d5.pick_per_target(torch.stack(scores).nanmean(0))
    out = oof.gather(0, pick[None, None, :].expand(1, len(fold), y.shape[1]))[0]
    Ktr, (cte,) = band_kernel(bands, dk, [te])
    (paths,) = kernel_paths(Ktr, [cte], y[dk])
    out[te] = paths.gather(0, pick[None, None, :].expand(1, len(te), y.shape[1]))[0]
    return out.numpy()


def pooled_r(a, b):
    return np.array([np.corrcoef(a[:, i], b[:, i])[0, 1] for i in range(a.shape[1])])


def targets(out, split, threads):
    """targets.npz: hat/resid(장면 판 × fold 6 × 영상 × 목표), truth(읽는 판 × 영상 × 목표, 영상이 시험된 fold의 값), split 순서."""
    torch.set_num_threads(threads)
    vid, fold = split.video_id.to_numpy(), split.fold.to_numpy()
    T = load_targets(split, vid)
    names = target_names(split)
    bands = load_bands(split)
    hat = {S: np.zeros((c.N_FOLDS, len(vid), T.shape[1])) for S in SETS}
    for S, keys in SETS.items():
        for k in range(1, c.N_FOLDS + 1):
            hat[S][k - 1] = crossfit_banded([bands[b] for b in keys], T, fold, k)
            print(f"{S} fold {k} 끝", flush=True)
    resid = {S: T[None] - hat[S] for S in SETS}
    te_of = lambda A: np.stack([A[f - 1, i] for i, f in enumerate(fold)])  # noqa: E731
    truth = {"T": T, **{S: te_of(resid[S]) for S in SETS}}
    rows = []
    feat_r = {S: pooled_r(te_of(hat[S]), T) for S in SETS}
    sanity = np.zeros((len(vid), T.shape[1]))
    for k in range(1, c.N_FOLDS + 1):
        sanity[fold == k] = crossfit_banded([bands[b] for b in SETS["Sall"]], resid["Sall"][k - 1], fold, k)[fold == k]
        print(f"잔차 점검 fold {k} 끝", flush=True)
    san_r = pooled_r(sanity, truth["Sall"])
    for i, n in enumerate(names):
        rows.append(dict(target=n, **{f"r_{S}_to_T": feat_r[S][i] for S in SETS}, r_Sall_to_resid_Sall=san_r[i],
                         manipulation_ok=bool(feat_r["Sall"][i] >= feat_r["Sw"][i]), sanity_ok=bool(san_r[i] <= SANITY_R)))
    o = Path(out)
    o.mkdir(parents=True, exist_ok=True)
    np.savez(o / "targets.npz", video_id=vid, target=np.array(names), read=np.array(READ),
             **{f"hat_{S}": hat[S] for S in SETS}, **{f"resid_{S}": resid[S] for S in SETS}, truth=np.stack([truth[r] for r in READ]))
    pd.DataFrame(rows).to_csv(o / "features_only.tsv", sep="\t", index=False)


def fit(s, out, split, threads, n_boot):
    torch.set_num_threads(threads)
    z = np.load(Path(out) / "targets.npz", allow_pickle=True)
    tvid, names = z["video_id"], z["target"].tolist()
    resid = {S: z[f"resid_{S}"] for S in SETS}
    T_all = z["truth"][0]
    brain = d5.load_brain(s, split)
    vid, fold = np.asarray(brain.video_id), np.asarray(brain.fold)
    pos = {v: i for i, v in enumerate(tvid.tolist())}
    rows = np.array([pos[v] for v in vid.tolist()])
    K = len(names)
    Yk = [np.concatenate([T_all[rows]] + [resid[S][k - 1, rows] for S in SETS], 1) for k in range(1, c.N_FOLDS + 1)]
    truth = np.concatenate([z["truth"][i][rows] for i in range(len(READ))], 1)  # (영상, 판 × 목표)
    nets = geo.network_positions(brain)
    nets[WHOLE] = np.arange(np.asarray(brain.X).shape[1])
    W = gc.boot_weights(split, vid, n_boot).double().numpy()
    X = torch.as_tensor(np.asarray(brain.X))
    nn, KK = len(nets), truth.shape[1]
    pred = np.full((nn, len(vid), KK), np.nan, np.float32)
    point = np.full((nn, KK), np.nan)
    boot = np.full((n_boot, nn, KK), np.nan, np.float32)
    for j, (g, p) in enumerate(nets.items()):
        started = time.time()
        x = X[:, torch.as_tensor(p)].double()
        for k in range(1, c.N_FOLDS + 1):
            r = c.roles(k)
            tr, va, te = np.flatnonzero(np.isin(fold, r["train"])), np.flatnonzero(fold == r["val"]), np.flatnonzero(fold == k)
            pr, bad = geo.ridge(x, Yk[k - 1], tr, va, te)
            if bad:
                raise ValueError(f"{g} fold {k}: 정답이 상수인 목표가 있다")
            pred[j, te] = pr
        del x
        Pj = pred[j].astype(np.float64)
        point[j] = st.boot_r(np.ones((1, len(vid))), truth, dict(p=Pj))["p"][0]
        boot[:, j] = st.boot_r(W, truth, dict(p=Pj))["p"]
        print(f"sub-{s} {g} ({len(p)} voxel) {time.time() - started:.0f}초", flush=True)
    # 순열: split 전체에서 block(시험 fold, 원래 run) 안의 순열을 5명 공통으로 만든다
    sp = split.reset_index(drop=True)
    blocks = np.array([f"fold{f}_run{r}" for f, r in zip(sp.fold.to_numpy(), sp.run_index.to_numpy())])
    perm = st.block_permutations(blocks, N_PERM, np.random.default_rng(PERM_SEED))
    y_all = np.concatenate([z["truth"][i] for i in range(len(READ))], 1)
    null = np.full((N_PERM, nn, KK), np.nan, np.float32)
    preds = {j: pred[j].astype(np.float64) for j in range(nn)}
    for start in range(0, N_PERM, PERM_CHUNK):
        res = st.permuted_r(perm[start:start + PERM_CHUNK], rows, y_all, preds)
        for j in range(nn):
            null[start:start + PERM_CHUNK, j] = res[j]
    o = Path(out) / "fit"
    o.mkdir(parents=True, exist_ok=True)
    tmp = o / f"sub-{s}.tmp.npz"
    np.savez(tmp, video_id=vid, networks=np.array(list(nets)), n_voxels=np.array([len(p) for p in nets.values()]), target=np.array(names),
             read=np.array(READ), pred=pred, point=point, boot=boot, null=null)
    tmp.rename(o / f"sub-{s}.npz")


def classify(r, lo, hi, sign5):
    if lo > 0 and r >= SURVIVE_R and sign5:
        return "survives"
    if hi < SURVIVE_R:
        return "absorbed"
    return "inconclusive"


def summarize(out):
    """scores.tsv(네트워크 × 판 × 목표), counts.tsv(네트워크 × 판마다 정서 범주 34개의 판정 수), predictions.tsv(미리 적은 예측 3개의 판정)."""
    out = Path(out)
    F = [np.load(out / "fit" / f"sub-{s}.npz", allow_pickle=True) for s in d5.HK]
    feat = pd.read_csv(out / "features_only.tsv", sep="\t").set_index("target")
    nets, names = F[0]["networks"].tolist(), F[0]["target"].tolist()
    K = len(names)
    pt = np.stack([f["point"] for f in F])  # 5 × 망 × (판 × 목표)
    bt = np.stack([f["boot"] for f in F]).mean(0)
    nl = np.stack([f["null"] for f in F]).mean(0)
    m = pt.mean(0)
    lo, hi = st.basic_ci(m, bt)
    pp = st.permutation_p(m, nl)
    sign5 = (pt > 0).all(0)
    rows = []
    for j, g in enumerate(nets):
        for ri, rd in enumerate(READ):
            for t, n in enumerate(names):
                i = ri * K + t
                usable = True
                if rd == "Sall":
                    usable = bool(feat.loc[n, "manipulation_ok"] and feat.loc[n, "sanity_ok"])
                rows.append(dict(network=g, read=rd, target=n, is_category=t < NE, r=m[j, i], lo=lo[j, i], hi=hi[j, i], p_perm=pp[j, i],
                                 sign5=bool(sign5[j, i]), usable=usable, verdict=classify(m[j, i], lo[j, i], hi[j, i], sign5[j, i]) if usable else "excluded",
                                 confirmatory=g in CONFIRM, **{f"r_sub-{s}": pt[q, j, i] for q, s in enumerate(d5.HK)}))
    S = pd.DataFrame(rows)
    S["p_adj"] = np.nan
    for rd in READ:
        for conf in (True, False):
            idx = S.index[(S.read == rd) & (S.confirmatory == conf)]
            S.loc[idx, "p_adj"] = (st.holm if conf else st.bh)(S.loc[idx, "p_perm"].to_numpy())
    S["correction"] = np.where(S.confirmatory, "Holm(Visual1, Visual2, Default × 36)", "BH(나머지 × 36)")
    S.to_csv(out / "scores.tsv", sep="\t", index=False)
    cat = S[S.is_category]
    cnt = cat.groupby(["network", "read"]).verdict.value_counts().unstack(fill_value=0).reset_index()
    cnt.to_csv(out / "counts.tsv", sep="\t", index=False)
    pred_rows = []
    d = cat[(cat.network == "Default") & (cat.read == "Sw")]
    frac = (d.verdict == "survives").mean()
    pred_rows.append(dict(prediction="1. R_Sw에서 Default는 정서 범주의 절반 넘게가 남는다", value=frac, n=len(d), holds=bool(frac > 0.5)))
    d = cat[(cat.network == "Default") & (cat.read == "Sall") & cat.usable]
    frac = (d.verdict == "survives").mean() if len(d) else np.nan
    pred_rows.append(dict(prediction="2. R_Sall에서 Default는 판정 가능한 정서 범주의 3분의 1 미만이 남는다", value=frac, n=len(d), holds=bool(frac < 1 / 3)))
    ia, ib = READ.index("Sw"), READ.index("Sall")
    ok = []
    for g in CONFIRM:
        j = nets.index(g)
        for dname in DIMS:
            t = names.index(dname)
            dp = m[j, ia * K + t] - m[j, ib * K + t]
            db = bt[:, j, ia * K + t] - bt[:, j, ib * K + t]
            a, b = st.basic_ci(dp, db)
            ok.append(float(a) > 0)
            pred_rows.append(dict(prediction=f"3. {g} {dname}: r(R_Sw) − r(R_Sall)", value=dp, lo=float(a), hi=float(b), holds=bool(float(a) > 0)))
    pred_rows.append(dict(prediction="3. 위 6개 모두 0 위", value=float(np.mean(ok)), holds=bool(all(ok))))
    pd.DataFrame(pred_rows).to_csv(out / "predictions.tsv", sep="\t", index=False)
    return S


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 장면 표현으로 선형으로 얻어지지 않는 정서 평정 정보")
    ap.add_argument("step", choices=["targets", "fit", "summarize"])
    ap.add_argument("--participant", choices=d5.HK)
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", required=True)
    ap.add_argument("--threads", type=int, default=16)
    ap.add_argument("--n-boot", type=int, default=st.N_RESAMPLE)
    a = ap.parse_args(argv)
    c.guard(a.design_freeze)
    split = c.load_split()
    started = time.time()
    if a.step == "targets":
        targets(a.out, split, a.threads)
        tag = "targets"
    elif a.step == "fit":
        if a.participant is None:
            raise SystemExit("fit은 --participant가 필요하다")
        fit(a.participant, a.out, split, a.threads, a.n_boot)
        tag = f"fit_sub-{a.participant}"
    else:
        summarize(a.out)
        tag = "summarize"
    info = dict(step=a.step, participant=a.participant, n_boot=a.n_boot, boot_seed=gc.BOOT_SEED, perm_seed=PERM_SEED, n_perm=N_PERM,
                design_freeze=a.design_freeze, code_commit=c.START_HEAD, code_dirty=c.START_DIRTY, elapsed_seconds=round(time.time() - started, 1))
    Path(a.out).mkdir(parents=True, exist_ok=True)
    (Path(a.out) / f"run_info_{tag}.json").write_text(json.dumps(info, indent=1, ensure_ascii=False))
    print(f"끝: {tag} {info['elapsed_seconds']}초", flush=True)


if __name__ == "__main__":
    main()
