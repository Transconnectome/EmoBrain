#!/usr/bin/env python3
"""S10 2부 합성 자료 시험 (2026-11-15). 실제 정답, 실제 예측, 실제 특징, GPU를 쓰지 않는다. 결과 폴더는 임시 폴더에 만든다.
시험: 특징 순열 r(참가자에게 없는 영상이 들어오는 경우 포함)과 짝 열 가중 r의 손 계산, 2-1(이어 붙이기, 차원 r 평균, 순열 p, 식별, 빠진 fold),
2-2(audition_codex와 같은 관찰 효과, 짝 연결 묶음 재표집이 반복 표본과 같음, Δy와 짝 대조, 빠진 fold),
6-4b(영상별 예측으로 낸 하락, 영상 단위 재표집이 반복 표본과 같음, Holm 13과 BH 묶음, 반복 처리 선택, workers 무관, 옛 형식과 합 불일치 거절, 빠진 fold),
6-2(평가 정서 목록, 상수 예측 범위 옵션, 다섯 구역 평균, 하락폭, [사전] 차이, 빠진 분할), 6-4a(작업 목록, [사전] 세 행, BH 묶음 옵션, decoded features),
6-3(평정 상수 정서, 상수 예측 범위 옵션, 확인용 실행 거절, seed 요약, 빠진 단위).
사용(레포 최상위): python tests/s10b_tests.py
"""
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1] / "src"))  # 코드는 src에 있다
_sys.dont_write_bytecode = True
import json
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "4")
import numpy as np
import pandas as pd
import torch

import s10_stats as st
import s10_inputs as I
import s10_performance as perf
import s10_feature_decoding as fdec
import s10_swap as sw
import s10_perturb as pt
import s10_zone as zn
import s10_network as nw
import s10_mc as mc
from s5_collect import identification_scores

RESULTS = []
N_EMO = 34
EMOTIONS = ["craving", "sexual desire", "entrancement", "horror", "confusion", "awe", "surprise"] + [f"emo{e}" for e in range(7, N_EMO)]  # 앞 7개는 1-1 보조 비교(Kragel 외, 2019)의 정서
PIDS = ["sub-01", "sub-02"]
DV, DC = I.DIMS["vision"], I.DIMS["caption"]


def check(name, ok):
    RESULTS.append((name, bool(ok)))
    print("통과" if ok else "실패", name, flush=True)


def raises(fn, exc=(ValueError, SystemExit), text=None):
    try:
        fn()
    except exc as e:
        return text is None or text in str(e)
    return False


def fake_split():
    """fold 6개, fold마다 run 2개, run마다 영상 6개(72개). fold 4의 다른 run에 같은 내용 쌍이 하나 있다."""
    rows, vid = [], 1
    for k in range(1, 7):
        for j in range(2):
            run = (k - 1) * 2 + j + 1
            for _ in range(6):
                rows.append(dict(split_id="fake", video_id=vid, content_id=vid, canonical_id=vid, run_index=run, run_group=run, fold=k))
                vid += 1
    s = pd.DataFrame(rows)
    a, b = s.video_id[(s.fold == 4) & (s.run_index == 7)].iloc[0], s.video_id[(s.fold == 4) & (s.run_index == 8)].iloc[0]
    s.loc[s.video_id == b, "canonical_id"] = a
    return s


SPLIT = fake_split()
MISSING_02 = [3, 20, 50]  # sub-02에 없는 영상
PVIDEOS = {"sub-01": SPLIT.video_id.to_numpy(), "sub-02": np.array([v for v in SPLIT.video_id if v not in MISSING_02])}
RNG = np.random.default_rng(11)
Y = RNG.random((len(SPLIT), N_EMO)) * (RNG.random((len(SPLIT), N_EMO)) < 0.6)
Y[:, -1] = 0.0
FEAT = RNG.standard_normal((len(SPLIT), DV + DC)).astype(np.float32)


def fake_features(split, ids):
    at = np.asarray(ids) - 1
    return {"vision": FEAT[at, :DV], "caption": FEAT[at, DV:]}


I.actual_features = fake_features  # 실제 S3 파일을 읽지 않는다
TMP = Path(tempfile.mkdtemp(prefix="s10b_tests_"))


# 통계 함수

def t_stats():
    rng = np.random.default_rng(1)
    N, D = 30, 12
    f = rng.standard_normal((N, D))
    f[:, 2] = 0.5
    blocks = np.repeat(np.arange(5), 6)
    perm = st.block_permutations(blocks, 40, np.random.default_rng(2))
    pos = np.array([i for i in range(N) if i not in (4, 17)])  # 이 참가자에게 없는 영상 둘
    p = f[pos] + rng.standard_normal((len(pos), D))
    r = st.permuted_feature_r(perm, pos, f, p)
    man = np.stack([st.pearson_columns(f[perm[b, pos]], p) for b in range(len(perm))])
    check("특징 순열 r = 실제 특징 벡터를 옮긴 손 계산(없는 영상이 들어오는 경우 포함)", np.allclose(r, man, atol=1e-5, equal_nan=True) and np.isnan(r[:, 2]).all())
    x = rng.standard_normal((N, 5))
    yy = rng.standard_normal((N, 2))
    col = np.array([0, 1, 0, 1, 1])
    w = rng.integers(0, 3, (6, N))
    w[:, 0] = 1
    got = st.boot_r_paired(w, x, yy, col)
    man = np.stack([st.pearson_columns(np.repeat(yy[:, col], wi, 0), np.repeat(x, wi, 0)) for wi in w])
    check("짝 열 가중 r = 뽑힌 횟수만큼 반복한 표본의 r", np.allclose(got, man))


# 2-1

def write_s5(root, preds, drop=None):
    fold_of = dict(zip(SPLIT.video_id, SPLIT.fold))
    for q, (v, x) in preds.items():
        for k in range(1, 7):
            if drop == (q, k):
                continue
            d = root / f"{q}_fold{k}"
            d.mkdir(parents=True)
            m = np.array([fold_of[int(t)] == k for t in v])
            arrs = {}
            for i, n in enumerate(fdec.VISION_LAYERS):
                arrs[n] = x[m][:, i * 1408:(i + 1) * 1408]
            for i, n in enumerate(fdec.CAPTION_LAYERS):
                arrs[n] = x[m][:, DV + i * 1024:DV + (i + 1) * 1024]
            np.savez(d / "test_pred.npz", video_id=v[m], **arrs)
            (d / "done.json").write_text("{}")


def t_decoding():
    preds = {q: (PVIDEOS[q], FEAT[PVIDEOS[q] - 1].astype(np.float64) + RNG.standard_normal((len(PVIDEOS[q]), DV + DC)) * (2 + i)) for i, q in enumerate(PIDS)}
    s5 = TMP / "s5"
    write_s5(s5, preds)
    seen = {}
    orig = st.block_permutations

    def spy(blocks, n, rng):
        seen["perm"] = orig(blocks, n, rng)
        return seen["perm"]
    st.block_permutations = spy
    try:
        fdec.run(s5, TMP / "dec_out", SPLIT, n_perm=30, n_boot=40, threads=2, pvideos=PVIDEOS)
    finally:
        st.block_permutations = orig
    t = pd.read_csv(TMP / "dec_out" / "decoding_scores.tsv", sep="\t")
    v, x = preds["sub-02"]
    r = st.pearson_columns(FEAT[v - 1].astype(np.float64), x)
    row = t[(t.participant == "sub-02") & (t.feature == "vision")].iloc[0]
    check("2-1 통계량 = 이어 붙인 예측의 차원별 r 평균", np.isclose(row.mean_dim_r, np.nanmean(r[:DV])) and row.n_dims_noncomputable == 0)
    U = np.array(sorted(set(PVIDEOS["sub-01"])))
    pos = np.searchsorted(U, v)
    null = np.array([np.nanmean(st.pearson_columns(FEAT[U - 1][seen["perm"][b, pos]].astype(np.float64), x)[DV:]) for b in range(30)])
    rc = t[(t.participant == "sub-02") & (t.feature == "caption")].iloc[0]
    check("2-1 순열 p = 실제 특징 벡터를 block 안에서 옮긴 손 계산의 한쪽 p", np.isclose(rc.p_perm, st.permutation_p(rc.mean_dim_r, null), atol=1e-6) and np.isclose(rc.null_mean, null.mean(), atol=1e-5))
    k = 3
    fold_of = dict(zip(SPLIT.video_id, SPLIT.fold))
    at = np.array([fold_of[int(t_)] == k for t_ in v])
    dk = FEAT[[t_ - 1 for t_ in PVIDEOS["sub-02"] if fold_of[int(t_)] != k], DV:].astype(np.float64)
    m_, s_ = dk.mean(0), dk.std(0)
    check("2-1 영상 식별은 D_k 눈금, 같은 fold 안(O19)", np.isfinite(rc.identification) and 0 <= rc.identification <= 1
          and np.isfinite(identification_scores((x[at][:, DV:] - m_) / s_, (FEAT[v[at] - 1, DV:] - m_) / s_).mean()))
    pre = pd.read_csv(TMP / "dec_out" / "prereg_pvalues.tsv", sep="\t", dtype={"seed": "string"})
    check("2-1 [사전] p 파일: 두 이름, 묶음마다, seed 칸 빈칸", set(pre.test_id) == {"2-1 Vision feature", "2-1 Caption feature"} and set(pre.family) == set(PIDS + ["mean5"]) and pre.seed.isna().all())
    s5b = TMP / "s5b"
    write_s5(s5b, preds, drop=("sub-01", 4))
    check("2-1 빠진 fold가 있으면 최종 표를 내지 않는다", raises(lambda: fdec.run(s5b, TMP / "dec_b", SPLIT, n_perm=5, n_boot=5, pvideos=PVIDEOS), text="빠진 입력"))
    fdec.run(s5b, TMP / "dec_c", SPLIT, n_perm=5, n_boot=5, pvideos=PVIDEOS, partial_check=True)
    check("2-1 --partial-check는 점검용으로 쓰고 표시한다", json.loads((TMP / "dec_c" / "run_info.json").read_text())["note"] == I.PARTIAL_NOTE)


# 2-2

def swap_tables():
    """fold마다 짝: i -> i^1, 다만 2 -> 0, 3 -> 2(크기 4 묶음 하나와 크기 2 묶음 넷)."""
    rows, groups = [], []
    for k in range(1, 7):
        v = SPLIT.video_id[SPLIT.fold == k].tolist()
        partner = {i: i ^ 1 for i in range(len(v))}
        partner[2], partner[3] = 0, 2
        for i, j in partner.items():
            rows.append(dict(fold=k, video_a=v[i], video_b=v[j], distance=0.1, n_tied=1, mutual=partner[j] == i))
        comp = {0: 0, 1: 0, 2: 0, 3: 0}
        for i in range(4, len(v)):
            comp[i] = i // 2
        for i in range(len(v)):
            groups.append(dict(fold=k, video_id=v[i], pair_group=f"f{k}g{comp[i]}"))
    g = pd.DataFrame(groups)
    g["group_size"] = g.pair_group.map(g.groupby("pair_group").size())
    return pd.DataFrame(rows), g


def build_swap(root, pairs, drop_fold=None, bad_dy=False):
    from s6_model import ac
    torch.manual_seed(0)
    model = ac.DecodedFeatureReadout(8, 2).eval()
    ypos = {v: i for i, v in enumerate(SPLIT.video_id)}
    for k in range(1, 7):
        if k == drop_fold:
            continue
        d = root / f"outer_fold{k}_seed0"
        d.mkdir(parents=True)
        out = {}
        for i, q in enumerate(PIDS):
            vids = [v for v in PVIDEOS[q] if SPLIT.fold[SPLIT.video_id == v].iloc[0] == k]
            local = {v: j for j, v in enumerate(vids)}
            pk = pairs[(pairs.fold == k) & pairs.video_a.isin(local) & pairs.video_b.isin(local)]
            pr = torch.tensor([[local[a], local[b]] for a, b in zip(pk.video_a, pk.video_b)], dtype=torch.long)
            H = torch.randn(len(vids), 5, 8, generator=torch.Generator().manual_seed(100 * k + i))
            ratings = torch.as_tensor(Y[[ypos[v] for v in vids]], dtype=torch.float32)
            res = ac.interchange_intervention(model, H, ratings, pr, video_ids=vids, participant=q, fold=k, seed=0, checkpoint_id="x", control_seed=k * 10 + i)
            dd = vars(res)
            if bad_dy and k == 2 and i == 0:
                dd["delta_y"] = dd["delta_y"] + 0.1
            out[q] = dd
        torch.save(out, d / "interventions.pt")
        (d / "done.json").write_text("{}")


def t_swap():
    from s6_model import ac
    pairs, groups = swap_tables()
    root = TMP / "swap"
    build_swap(root, pairs)
    sw.run(root, TMP / "swap_out", SPLIT, Y, EMOTIONS, n_boot=60, pairs=pairs, groups=groups)
    s = pd.read_csv(TMP / "swap_out" / "swap_scores.tsv", sep="\t")
    data = torch.load(root / "outer_fold1_seed0" / "interventions.pt", weights_only=False)
    items = [ac.FoldInterventions(**torch.load(root / f"outer_fold{k}_seed0" / "interventions.pt", weights_only=False)["sub-02"]) for k in range(1, 7)]
    ref = ac.summarize_interventions(items)
    got = s[s.participant == "sub-02"].set_index("path").effect
    check("2-2 경로별 효과 = audition_codex.summarize_interventions의 34개 평균", np.allclose(got[list(sw.PATHS)].to_numpy(), ref["effect_mean"].numpy(), atol=1e-6))
    pre = pd.read_csv(TMP / "swap_out" / "prereg_pvalues.tsv", sep="\t")
    check("2-2 [사전] 세 이름과 묶음", set(pre.test_id) == set(sw.TESTS.values()) and set(pre.family) == set(PIDS + ["mean5"]))
    seed_data, _ = sw.load_seed({k: root / f"outer_fold{k}_seed0" for k in range(1, 7)}, SPLIT, Y, pairs, groups)
    d = seed_data["sub-02"]
    names = sorted(groups.pair_group.unique())
    gi = np.array([names.index(g) for g in d["group"]])
    wu = np.random.default_rng(5).integers(0, 3, (3, len(names)))
    wpair = wu[:, gi]
    eff, _, Ie = sw.boot(d, wpair)
    ok = True
    for b in range(3):
        rep = np.repeat(np.arange(len(gi)), wpair[b])
        dd = dict(dp=d["dp"][rep], dy=d["dy"][rep], cdp=d["cdp"][:, rep], I=d["I"][rep], cI=d["cI"][:, rep], Ip=d["Ip"][rep], cIp=d["cIp"][:, rep])
        o = sw.observed(dd)
        ok &= np.allclose(eff[b], o["effect"], atol=1e-8, equal_nan=True) and np.allclose(Ie["logit"][b], o["absI"]["logit"] - o["cabsI"]["logit"], atol=1e-10)
    check("2-2 짝 연결 묶음 재표집 = 묶음을 뽑힌 횟수만큼 반복한 쌍과 대조로 다시 낸 효과", ok)
    cl = pd.read_csv(TMP / "swap_out" / "clusters.tsv", sep="\t")
    check("2-2 묶음 크기 분포를 적는다", set(cl.n_videos) == {2, 4} and json.loads((TMP / "swap_out" / "run_info.json").read_text())["cluster_size_distribution"] == {"2": 24, "4": 6})
    pe = pd.read_csv(TMP / "swap_out" / "path_difference_per_emotion.tsv", sep="\t")
    g = pe[pe.participant == "sub-01"]
    check("1-1 정서별 차이는 탐색, BH는 참가자마다 34개", np.allclose(g.p_bh, st.bh(g.p_raw.to_numpy()), equal_nan=True) and g.label.eq("탐색(BH-FDR)").all())
    check("Δy가 모두 0인 정서는 빼고 센다", (s[s.participant != "mean5"].n_target_constant == 1).all() and (s[s.participant != "mean5"].n_emotions_used == N_EMO - 1).all())
    kr = pd.read_csv(TMP / "swap_out" / "kragel_groups.tsv", sep="\t")
    g = kr[(kr.participant == "sub-02") & (kr.quantity == "시각 효과 − 캡션 효과") & kr.group.str.contains("높았던")].iloc[0]
    d2 = pe[(pe.participant == "sub-02") & pe.emotion.isin(sw.KRAGEL["높았던 정서"])].estimate.mean()
    check("1-1 보조: Kragel 두 묶음의 경로 효과 평균", set(kr.quantity) == {"시각 효과", "캡션 효과", "시각 효과 − 캡션 효과"} and kr.group.nunique() == 2 and np.isclose(g.estimate, d2))
    root_b = TMP / "swap_b"
    build_swap(root_b, pairs, drop_fold=5)
    check("2-2 빠진 fold가 있으면 멈춘다", raises(lambda: sw.run(root_b, TMP / "swap_out_b", SPLIT, Y, EMOTIONS, n_boot=5, pairs=pairs, groups=groups), text="빠진 입력"))
    root_c = TMP / "swap_c"
    build_swap(root_c, pairs, bad_dy=True)
    check("2-2 저장된 Δy가 사람 평정과 다르면 멈춘다", raises(lambda: sw.run(root_c, TMP / "swap_out_c", SPLIT, Y, EMOTIONS, n_boot=5, pairs=pairs, groups=groups), text="Δy"))
    bad = pairs.copy()
    bad.loc[0, "video_b"] = bad.loc[5, "video_b"]
    check("2-2 쌍이 S2 짝과 다르면 멈춘다", raises(lambda: sw.run(root, TMP / "swap_out_d", SPLIT, Y, EMOTIONS, n_boot=5, pairs=bad, groups=groups), text="O9"))


# 6-4b

PERT_UNITS, PERT_ROIS = ("Default", "Visual1"), ("L_V1", "L_V2", "L_V3")
PERT_AG = pd.DataFrame(dict(group=list(PERT_UNITS), group_ko=["d", "v"], median=[0.1, 0.2], min=[0, 0], max=[1, 1], count=[3, 2]))
PERT_NB = 40  # 시험용 재표집 수
PERT_OPTS = dict(repeat_handling="fixed", drop_bh_family="by_model", n_boot=PERT_NB, agreement=PERT_AG)


def build_perturb(root, drop_fold=None, rep=3, old_format=None, bad_sum=None, bad_keys=None):
    """S9 perturb 꼴의 합성 결과. 영상별 예측은 float32이고 합은 그 값을 float64로 더한 것이다(s9_saved_models와 같음).
    old_format: 영상별 예측을 쓰지 않는 fold. bad_sum: 영상별 교란 예측 하나를 바꾼 fold. bad_keys: 영상별 행 순서를 바꾼 fold."""
    rng = np.random.default_rng(3)
    names = list(PERT_UNITS) + list(PERT_ROIS)
    kinds = ["group"] * len(PERT_UNITS) + ["roi"] * len(PERT_ROIS)
    truth = {}
    for k in range(1, 7):
        rows = [(q, v) for q in PIDS for v in PVIDEOS[q] if SPLIT.fold[SPLIT.video_id == v].iloc[0] == k]
        pid = np.array([q for q, _ in rows])
        vid = np.array([v for _, v in rows])
        y = Y[vid - 1]
        onehot = np.stack([pid == q for q in PIDS], 1).astype(float)
        sums = lambda p: np.stack([onehot.T @ p, onehot.T @ (p * p), onehot.T @ (p * y)])
        arr = dict(video_id=vid, participant=pid, donors=np.zeros((rep, len(vid)), int), donor_seed=np.array(1), unit_kind=np.array(kinds),
                   unit_name=np.array(names), sum_y=onehot.T @ y, sum_yy=onehot.T @ (y * y), n=onehot.sum(0))
        pv = dict(video_id=vid, participant=pid, unit_kind=np.array(kinds), unit_name=np.array(names))
        big = {}
        for m in pt.MODELS:
            base = np.clip(y + rng.normal(0, 0.3, y.shape), 0, 1).astype(np.float32)
            pert = np.clip(base[None, None] + rng.normal(0, 0.2, (len(names), rep) + y.shape), 0, 1).astype(np.float32)
            b64, p64 = base.astype(np.float64), pert.astype(np.float64)
            truth[m, k] = (pid, vid, b64, p64)
            arr[f"{m}_base"] = sums(b64)
            arr[f"{m}_perturbed"] = np.stack([np.stack([sums(p64[u, t]) for t in range(rep)]) for u in range(len(names))])
            pv[f"{m}_base"], big[m] = base, pert
        if k == drop_fold:
            continue
        d = root / f"outer_fold{k}_seed0"
        d.mkdir(parents=True)
        np.savez(d / "perturb_sums.npz", **arr)
        (d / "done.json").write_text("{}")
        if k == old_format:
            continue
        if k == bad_keys:
            pv["video_id"] = pv["video_id"][::-1].copy()
        np.savez(d / pt.PRED_FILE, **pv)
        for m in pt.MODELS:
            a = big[m].copy()
            if k == bad_sum and m == "brain_decoded":
                a[3, 1, 2, 5] = np.float32(0.5) if a[3, 1, 2, 5] != 0.5 else np.float32(0.25)
            np.save(d / pt.PRED_ARRAY.format(m), a)
    return truth


def perturb_truth(truth, m, q):
    """참가자 q의 6 fold 행을 fold 순서로 모은 (사람 평정, 원래 예측, 교란 예측 단위 × 반복 × 영상 × 34, 영상 번호)."""
    pid = np.concatenate([truth[m, k][0] for k in range(1, 7)])
    vid = np.concatenate([truth[m, k][1] for k in range(1, 7)])
    base = np.concatenate([truth[m, k][2] for k in range(1, 7)])
    pert = np.concatenate([truth[m, k][3] for k in range(1, 7)], 2)
    s = pid == q
    return Y[vid[s] - 1], base[s], pert[:, :, s], vid[s]


def hand_drop_boot(truth, m, q, u, counts=None):
    """뽑힌 횟수만큼 영상을 반복한 표본에서 r을 다시 내 낸 하락(재표집마다). 1부와 같은 단위(canonical_id)와 seed를 쓴다."""
    U = np.array(sorted(set().union(*[set(v.tolist()) for v in PVIDEOS.values()])))
    codes, n_units = st.unit_codes(SPLIT.set_index("video_id").loc[U].canonical_id.to_numpy())
    W = st.bootstrap_counts(n_units, PERT_NB, np.random.default_rng(perf.BOOT_SEED))
    yq, base, pert, vq = perturb_truth(truth, m, q)
    keep = np.isfinite(st.pearson_columns(yq, base))
    out = []
    for b in range(PERT_NB):
        rep = np.repeat(np.arange(len(vq)), W[b, codes[np.searchsorted(U, vq)]])
        bs = np.nanmean(st.pearson_columns(yq[rep], base[rep])[keep])
        d = np.array([bs - np.nanmean(st.pearson_columns(yq[rep], pert[u, t][rep])[keep]) for t in range(pert.shape[1])])
        out.append(d.mean() if counts is None else (counts[b] * d).sum() / counts[b].sum())
    return np.array(out)


def t_perturb():
    root = TMP / "pert"
    truth = build_perturb(root)
    pt.run(root, TMP / "pert_out", SPLIT, Y, EMOTIONS, **PERT_OPTS)
    t = pd.read_csv(TMP / "pert_out" / "network_drops.tsv", sep="\t")
    yq, base, pert, _ = perturb_truth(truth, "brain_only", "sub-02")
    rb = st.pearson_columns(yq, base)
    keep = np.isfinite(rb)
    drops = [rb[keep].mean() - st.pearson_columns(yq, pert[0, t_])[keep].mean() for t_ in range(pert.shape[1])]
    row = t[(t.unit == "Default") & (t.participant == "sub-02")].iloc[0]
    check("6-4b 하락 = 6 fold를 모은 r의 (원래 − 교란) 점수를 반복마다 내 평균(11/15 전 점추정과 같음)", np.isclose(row.drop_A1, np.mean(drops)) and np.isclose(row.base_score_A1, rb[keep].mean()))
    check("6-4b 하락폭 차이 = C-1 − A-1, 일치도를 붙인다", np.isclose(row.drop_difference, row.drop_C1 - row.drop_A1) and row.agreement_median == 0.1)
    # 재표집: 뽑힌 횟수만큼 반복한 표본으로 손 계산
    ok = True
    for u, unit in ((0, "Default"), (3, "L_V2")):
        hb = {m: hand_drop_boot(truth, m, "sub-02", u) for m in pt.MODELS}
        tab = t if u < 2 else pd.read_csv(TMP / "pert_out" / "roi_drops.tsv", sep="\t")
        r_ = tab[(tab.unit == unit) & (tab.participant == "sub-02")].iloc[0]
        for pre, est, b in (("drop_A1", r_.drop_A1, hb["brain_only"]), ("drop_C1", r_.drop_C1, hb["brain_decoded"]), ("difference", r_.drop_difference, hb["brain_decoded"] - hb["brain_only"])):
            lo, hi = st.basic_ci(est, b)
            ok &= np.isclose(r_[f"{pre}_ci_low"], lo, atol=1e-9) and np.isclose(r_[f"{pre}_ci_high"], hi, atol=1e-9) and np.isclose(r_[f"{pre}_p_raw"], st.centered_p(est, b))
    check("6-4b 영상 단위 재표집(1부와 같은 단위와 seed) = 뽑힌 횟수만큼 영상을 반복한 표본에서 반복마다 하락을 다시 내 평균한 값의 basic 구간과 중심 맞춘 p(묶음과 ROI)", ok)
    m5 = t[(t.unit == "Default") & (t.participant == "mean5")].iloc[0]
    sub = t[(t.unit == "Default") & (t.participant != "mean5")]
    check("6-4b 5명 평균 하락은 참가자 하락의 평균", np.isclose(m5.drop_A1, sub.drop_A1.mean()) and np.isclose(m5.drop_difference, sub.drop_difference.mean()))
    ok = True
    for (s, q), g in t.groupby(["seed", "participant"]):
        ok &= np.allclose(g.difference_p_holm, st.holm(g.difference_p_raw.to_numpy())) and np.allclose(g.drop_A1_p_bh, st.bh(g.drop_A1_p_raw.to_numpy()))
        ok &= (g.difference_family_size == len(PERT_UNITS)).all() and g.difference_family.str.contains("Holm").all() and g.drop_family.str.contains("by_model").all()
    check("6-4b 하락폭 차이는 seed와 참가자(5명 평균 따로)마다 묶음 전체로 Holm, 각 모델 하락은 by_model BH", ok and set(t.participant) == set(PIDS + ["mean5"]))
    rd = pd.read_csv(TMP / "pert_out" / "roi_drops.tsv", sep="\t")
    ok = len(rd) == len(PERT_ROIS) * 3
    for _, g in rd.groupby(["seed", "participant"]):
        for pre in ("drop_A1", "drop_C1", "difference"):
            ok &= np.allclose(g[f"{pre}_p_bh"], st.bh(g[f"{pre}_p_raw"].to_numpy())) and (g[f"{pre}_family_size"] == len(PERT_ROIS)).all()
    check("6-4b ROI판은 탐색이고 BH는 seed, 참가자, 값마다 ROI 전체", ok and "difference_p_holm" not in rd.columns)
    pe = pd.read_csv(TMP / "pert_out" / "network_drops_per_emotion.tsv", sep="\t")
    g = pe[(pe.unit == "Visual1") & (pe.participant == "sub-01") & (pe.quantity == pt.QUANTITIES["difference"])]
    check("6-4b 묶음 안 정서별은 탐색이고 BH는 참가자, 묶음, 값마다 34개 정서(계산할 수 없는 정서는 뺌)",
          len(g) == N_EMO and np.allclose(g.p_bh, st.bh(g.p_raw.to_numpy()), equal_nan=True) and (g.family_size == N_EMO - 1).all() and g.label.eq("탐색(BH-FDR)").all())
    cf = pd.read_csv(TMP / "pert_out" / "network_confirmed.tsv", sep="\t")
    check("6-4b 묶음마다 확인된 참가자 수(보정 전과 후)", len(cf) == len(PERT_UNITS) and (cf.n_participants == len(PIDS)).all()
          and (cf.n_confirmed_after_holm <= cf.n_confirmed_before_holm).all())
    info = json.loads((TMP / "pert_out" / "run_info.json").read_text())
    check("6-4b run_info에 반복 처리, BH 묶음, 보정 묶음 설명, 재표집 seed를 적는다", info["repeat_handling"] == "fixed" and info["drop_bh_family"] == "by_model"
          and "[사전] Holm 13" in info["correction_families"] and info["resampling"]["boot_seed"] == perf.BOOT_SEED)
    # 다른 선택
    pt.run(root, TMP / "pert_pool", SPLIT, Y, EMOTIONS, **dict(PERT_OPTS, drop_bh_family="pooled", repeat_handling="resample"))
    tp = pd.read_csv(TMP / "pert_pool" / "network_drops.tsv", sep="\t")
    ok = True
    for _, g in tp.groupby(["seed", "participant"]):
        adj = st.bh(np.concatenate([g.drop_A1_p_raw.to_numpy(), g.drop_C1_p_raw.to_numpy()]))
        ok &= np.allclose(np.concatenate([g.drop_A1_p_bh.to_numpy(), g.drop_C1_p_bh.to_numpy()]), adj) and (g.drop_A1_family_size == 2 * len(PERT_UNITS)).all()
    check("6-4b --drop-bh-family pooled: 두 모델의 하락을 한 BH 묶음으로", ok)
    R = pert.shape[1]
    pick = np.random.default_rng(pt.REPEAT_SEED).integers(0, R, size=(PERT_NB, R))
    counts = np.stack([np.bincount(x, minlength=R) for x in pick])
    hb = hand_drop_boot(truth, "brain_only", "sub-02", 0, counts)
    r_ = tp[(tp.unit == "Default") & (tp.participant == "sub-02")].iloc[0]
    lo, hi = st.basic_ci(r_.drop_A1, hb)
    check("6-4b --repeat-handling resample: 재표집마다 반복도 복원 추출해 뽑힌 횟수로 평균(관찰 값은 같음)", np.isclose(r_.drop_A1, row.drop_A1) and np.isclose(r_.drop_A1_ci_low, lo, atol=1e-9)
          and np.isclose(r_.drop_A1_ci_high, hi, atol=1e-9) and not np.isclose(r_.drop_A1_ci_low, row.drop_A1_ci_low))
    pt.run(root, TMP / "pert_w2", SPLIT, Y, EMOTIONS, workers=2, **PERT_OPTS)
    same = all(pd.read_csv(TMP / "pert_w2" / f, sep="\t").equals(pd.read_csv(TMP / "pert_out" / f, sep="\t")) for f in ("network_drops.tsv", "roi_drops.tsv", "network_drops_per_emotion.tsv"))
    check("6-4b --workers 2의 결과가 1과 같다", same)
    # 거절
    check("6-4b 문서가 정하지 않은 두 선택이 없으면 최종 표를 내지 않는다", raises(lambda: pt.run(root, TMP / "pert_x", SPLIT, Y, EMOTIONS, n_boot=PERT_NB, agreement=PERT_AG), text="기본값 없음"))
    root_b = TMP / "pert_b"
    build_perturb(root_b, drop_fold=4)
    check("6-4b 빠진 fold가 있으면 최종 표를 내지 않는다", raises(lambda: pt.run(root_b, TMP / "pert_out_b", SPLIT, Y, EMOTIONS, **PERT_OPTS), text="빠진 입력"))
    pt.run(root_b, TMP / "pert_out_c", SPLIT, Y, EMOTIONS, agreement=PERT_AG, partial_check=True)
    tc = pd.read_csv(TMP / "pert_out_c" / "network_drops.tsv", sep="\t")
    check("6-4b --partial-check는 점검용(선택이 없으면 재표집 없이 점추정만)", (tc.n_folds == 5).all() and tc.difference_ci_low.isna().all()
          and "점검용" in json.loads((TMP / "pert_out_c" / "run_info.json").read_text())["note"])
    root_o = TMP / "pert_old"
    build_perturb(root_o, old_format=2)
    check("6-4b 영상별 예측이 없는 옛 S9 형식 fold는 빠진 입력으로 센다", raises(lambda: pt.run(root_o, TMP / "pert_out_o", SPLIT, Y, EMOTIONS, **PERT_OPTS), text="영상별 예측 없음"))
    root_s = TMP / "pert_sum"
    build_perturb(root_s, bad_sum=5)
    check("6-4b 영상별 교란 예측의 합이 저장된 합과 다르면 멈춘다", raises(lambda: pt.run(root_s, TMP / "pert_out_s", SPLIT, Y, EMOTIONS, **PERT_OPTS), text="합이 perturb_sums.npz와 다르다"))
    root_k = TMP / "pert_keys"
    build_perturb(root_k, bad_keys=3)
    check("6-4b 영상별 예측의 행 열쇠가 다르면 멈춘다", raises(lambda: pt.run(root_k, TMP / "pert_out_k", SPLIT, Y, EMOTIONS, **PERT_OPTS), text="행 열쇠"))
    Y2 = Y.copy()
    Y2[0, 0] += 0.5
    check("6-4b 저장된 사람 평정 합이 다르면 멈춘다", raises(lambda: pt.run(root, TMP / "pert_out_d", SPLIT, Y2, EMOTIONS, **PERT_OPTS), text="사람 평정 합"))
    check("6-4b 묶음 단위가 S2 일치도 표의 묶음과 다르면 멈춘다(Holm 13의 묶음)", raises(lambda: pt.run(root, TMP / "pert_out_g", SPLIT, Y, EMOTIONS, **dict(PERT_OPTS, agreement=PERT_AG.iloc[:1])), text="Holm 13"))


# 6-2

ZBLOCKS = pd.DataFrame(dict(video_id=SPLIT.video_id, fold=SPLIT.fold, block=np.where(SPLIT.video_id % 2 == 0, 1, 2)))


def zone_control():
    import s4_common as c
    rows = []
    fold_of = dict(zip(SPLIT.video_id, SPLIT.fold))
    for b in (1, 2):
        for k in range(1, 7):
            r = c.roles(k)
            ex, _ = c.zone_sets(SPLIT, b, k, "excluded", ZBLOCKS, pd.DataFrame(columns=["block", "fold", "role", "video_id"]))
            n_tr = sum(fold_of[v] in r["train"] for v in ex)
            tr = [v for v in SPLIT.video_id if fold_of[v] in r["train"]][:n_tr]
            va = [v for v in SPLIT.video_id if fold_of[v] == r["val"]][:len(ex) - n_tr]
            rows += [dict(block=b, fold=k, role="train", video_id=v) for v in tr] + [dict(block=b, fold=k, role="val", video_id=v) for v in va]
    return pd.DataFrame(rows)


ZCONTROL = zone_control()
YZ = Y.copy()
YZ[(ZBLOCKS.block == 1).to_numpy(), 5] = 0.0  # 구역 1에서만 평정이 상수인 정서


def build_zone(root, drop=None, const=None):
    import s4_common as c
    rng = np.random.default_rng(4)
    fold_of = dict(zip(SPLIT.video_id, SPLIT.fold))
    truth = {}
    for b in (1, 2):
        for k in range(1, 7):
            for kind in zn.KINDS:
                d = root / zn.plan_name(b, k, kind)
                (d / "plan").mkdir(parents=True)
                tv, test = c.zone_sets(SPLIT, b, k, kind, ZBLOCKS, ZCONTROL)
                r = c.roles(k)
                (d / "plan" / "plan.json").write_text(json.dumps(dict(name=d.name, outer_fold=k, train=[v for v in tv if fold_of[v] in r["train"]], val=[v for v in tv if fold_of[v] == r["val"]], test=test)))
                rows = [(q, v) for q in PIDS for v in test if v in set(PVIDEOS[q].tolist())]
                pid, vid = np.array([q for q, _ in rows]), np.array([v for _, v in rows])
                np.savez(d / "plan" / "rows.npz", participant=pid, video_id=vid, role=np.full(len(vid), 2))
                np.savez(d / "plan" / "standardization.npz", visual_mean=np.zeros(DV), visual_std=np.ones(DV), caption_mean=np.zeros(DC), caption_std=np.ones(DC))
                for m in zn.MODELS:
                    if drop == (b, k, kind, m):
                        continue
                    sd = d / m / "c_seed0"
                    (sd / "outputs").mkdir(parents=True)
                    (d / m / "selected.json").write_text(json.dumps(dict(seeds={"0": f"{m}/c_seed0"})))
                    p = np.clip(YZ[vid - 1] + rng.normal(0, 0.25 if m == "brain_only" else 0.2, (len(vid), N_EMO)) + (0.1 if kind == "excluded" else 0), 0.001, 0.999)
                    if const and (b, kind, m) == const[:3]:
                        p[pid == const[3], 3] = 0.4
                    np.savez(sd / "test_pred.npz", participant=pid, video_id=vid, p=p)
                    truth[b, k, kind, m] = (pid, vid, p)
                    if m == "brain_decoded":
                        np.savez(sd / "outputs" / "decoded_test.npz", participant=pid, video_id=vid, v_hat=FEAT[vid - 1, :DV] + 0.5, c_hat=FEAT[vid - 1, DV:] * 2)
    return truth


def zone_r(truth, b, kind, m, q):
    pid = np.concatenate([truth[b, k, kind, m][0] for k in range(1, 7)])
    vid = np.concatenate([truth[b, k, kind, m][1] for k in range(1, 7)])
    p = np.concatenate([truth[b, k, kind, m][2] for k in range(1, 7)])
    s = pid == q
    return st.pearson_columns(YZ[vid[s] - 1], p[s])


def t_zone():
    root = TMP / "zone"
    truth = build_zone(root)
    kw = dict(blocks_table=ZBLOCKS, control_table=ZCONTROL, n_boot=40)
    zn.run(root, TMP / "zone_out", SPLIT, YZ, EMOTIONS, **kw)
    zs = pd.read_csv(TMP / "zone_out" / "zone_summary.tsv", sep="\t")
    ze = pd.read_csv(TMP / "zone_out" / "zone_emotions.tsv", sep="\t")
    check("6-2 평가 정서: 구역에서 평정이 상수인 정서만 뺀다", ze.set_index("block").n_evaluated.to_dict() == {1: N_EMO - 2, 2: N_EMO - 1})
    z = {}
    for b in (1, 2):
        ev = ~st.constant_columns(YZ[(ZBLOCKS.block == b).to_numpy()])
        for m in zn.MODELS:
            for kind in zn.KINDS:
                z[b, m, kind] = zone_r(truth, b, kind, m, "sub-02")[ev].mean()
    five = {(m, kind): np.mean([z[b, m, kind] for b in (1, 2)]) for m in zn.MODELS for kind in zn.KINDS}
    g = zs[(zs.participant == "sub-02") & (zs.scope == "다섯 구역 평균")].set_index(["model", "quantity"]).estimate
    check("6-2 구역 평균 = 구역마다 평가 정서 r 평균을 같은 무게로", np.isclose(g["A-1", "구역 제외 성능(절대)"], five["brain_only", "excluded"]) and np.isclose(g["C-1", "학습량 대조 성능"], five["brain_decoded", "control"]))
    dd = (five["brain_decoded", "control"] - five["brain_decoded", "excluded"]) - (five["brain_only", "control"] - five["brain_only", "excluded"])
    check("6-2 더 높다(구역 제외 성능 차이)와 덜 떨어진다(하락폭 차이)를 따로 낸다",
          np.isclose(g["C-1 − A-1", "구역 제외 성능의 차이(더 높다)"], five["brain_decoded", "excluded"] - five["brain_only", "excluded"]) and np.isclose(g["C-1 − A-1", "하락폭의 차이(덜 떨어진다)"], dd))
    pre = pd.read_csv(TMP / "zone_out" / "prereg_pvalues.tsv", sep="\t")
    check("6-2 [사전] 처음 보는 장면의 p", set(pre.test_id) == {"처음 보는 장면"} and set(pre.family) == set(PIDS + ["mean5"]) and pre.p_raw.between(0, 1).all())
    dec = pd.read_csv(TMP / "zone_out" / "c1_zone_decoding.tsv", sep="\t")
    check("6-2 C-1 decoded features의 2-1 지표를 원래 척도로 낸다", len(dec) and np.isclose(dec[(dec.feature == "caption") & (dec.participant == "sub-01")].mean_dim_r, 1.0).all())
    yp = YZ.copy()
    miss = [v for v in MISSING_02 if ZBLOCKS.set_index("video_id").block[v] == 2]
    blk2 = (ZBLOCKS.block == 2).to_numpy()
    yp[blk2, 8] = 0.0
    yp[SPLIT.video_id.to_numpy() == miss[0], 8] = 0.5  # 구역 2에서 sub-02에 없는 영상 하나만 0이 아님
    zn.run(root, TMP / "zone_p", SPLIT, yp, EMOTIONS, **kw)
    zp = pd.read_csv(TMP / "zone_p" / "zone_emotions.tsv", sep="\t").set_index("block")
    ep = pd.read_csv(TMP / "zone_p" / "zone_per_emotion.tsv", sep="\t")
    s8 = ep[(ep.block == 2) & (ep.emotion == EMOTIONS[8])]
    check("6-2 한 참가자에서만 평정이 상수인 정서는 모든 참가자에서 뺀다(11/17)", zp.loc[2, "rating_constant_in_participant"] == EMOTIONS[8]
          and (~s8.used_in_mean).all() and (s8.reason == "rating_constant_in_participant").all() and zp.loc[2, "n_used_sub-01"] == zp.loc[2, "n_used_sub-02"])
    root_c = TMP / "zone_c"
    build_zone(root_c, const=(2, "excluded", "brain_decoded", "sub-01"))
    check("6-2 상수 예측이 있으면 범위 옵션 없이 멈춘다", raises(lambda: zn.run(root_c, TMP / "zone_c1", SPLIT, YZ, EMOTIONS, **kw), text="--constant-prediction-scope"))
    zn.run(root_c, TMP / "zone_c2", SPLIT, YZ, EMOTIONS, scope="participant", **kw)
    e2 = pd.read_csv(TMP / "zone_c2" / "zone_per_emotion.tsv", sep="\t")
    sel = e2[(e2.block == 2) & (e2.emotion == EMOTIONS[3])]
    check("6-2 상수 예측 정서는 그 참가자의 네 설정 모두에서 뺀다(participant)", (~sel[sel.participant == "sub-01"].used_in_mean).all() and sel[sel.participant == "sub-02"].used_in_mean.all())
    zn.run(root_c, TMP / "zone_c3", SPLIT, YZ, EMOTIONS, scope="all", **kw)
    e3 = pd.read_csv(TMP / "zone_c3" / "zone_per_emotion.tsv", sep="\t")
    check("6-2 상수 예측 정서를 모든 참가자에서 뺀다(all)", (~e3[(e3.block == 2) & (e3.emotion == EMOTIONS[3])].used_in_mean).all() and len(pd.read_csv(TMP / "zone_c3" / "constant_predictions.tsv", sep="\t")) == 1)
    root_d = TMP / "zone_d"
    build_zone(root_d, drop=(1, 3, "control", "brain_decoded"))
    check("6-2 빠진 분할이 있으면 최종 표를 내지 않는다", raises(lambda: zn.run(root_d, TMP / "zone_d1", SPLIT, YZ, EMOTIONS, **kw), text="빠진 입력"))
    zn.run(root_d, TMP / "zone_d2", SPLIT, YZ, EMOTIONS, partial_check=True, **kw)
    zs2 = pd.read_csv(TMP / "zone_d2" / "zone_summary.tsv", sep="\t")
    check("6-2 --partial-check는 있는 설정만 내고 [사전] 차이는 낼 수 있을 때만", not ((zs2.scope == "구역 1") & (zs2.quantity == "하락폭의 차이(덜 떨어진다)")).any())


# 6-4a

NETS = ["Visual1", "Visual2", "Default", "Auditory"]


def build_networks(root, missing_net=None):
    rng = np.random.default_rng(6)
    jobs = []
    for g in NETS:
        out = root / f"s6_brain_net_{g}"
        for k in range(1, 7):
            jobs.append(dict(name=f"net_{g}_f{k}", plan=f"outer_fold{k}", conditions="brain_only,brain_decoded", config="/x.json", s6_out=str(out), est_hours=2))
            if g == missing_net:
                continue
            d = out / f"outer_fold{k}"
            (d / "plan").mkdir(parents=True)
            test = SPLIT.video_id[SPLIT.fold == k].tolist()
            rows = [(q, v) for q in PIDS for v in test if v in set(PVIDEOS[q].tolist())]
            pid, vid = np.array([q for q, _ in rows]), np.array([v for _, v in rows])
            np.savez(d / "plan" / "rows.npz", participant=pid, video_id=vid, role=np.full(len(vid), 2))
            np.savez(d / "plan" / "standardization.npz", visual_mean=np.full(DV, 1.0), visual_std=np.full(DV, 2.0), caption_mean=np.zeros(DC), caption_std=np.ones(DC))
            for m in nw.MODELS:
                sd = d / m / "c_seed0"
                (sd / "outputs").mkdir(parents=True)
                (d / m / "selected.json").write_text(json.dumps(dict(seeds={"0": f"{m}/c_seed0"}, zero_selected=False)))
                p = np.clip(Y[vid - 1] + rng.normal(0, 0.3, (len(vid), N_EMO)), 0.001, 0.999)
                np.savez(sd / "test_pred.npz", participant=pid, video_id=vid, p=p)
                if m == "brain_decoded":
                    np.savez(sd / "outputs" / "decoded_test.npz", participant=pid, video_id=vid, v_hat=(FEAT[vid - 1, :DV] - 1.0) / 2.0, c_hat=FEAT[vid - 1, DV:])
    path = root / "jobs.tsv"
    pd.DataFrame(jobs).to_csv(path, sep="\t", index=False)
    return path


def t_network():
    root = TMP / "net"
    jobs = build_networks(root)
    ag = pd.DataFrame(dict(group=NETS, group_ko=NETS, median=[0.5, 0.4, 0.2, 0.1], min=0, max=1, count=[6, 54, 77, 15]))
    kw = dict(groups=NETS, agreement=ag, n_boot=40, n_perm=30)
    check("6-4a BH 묶음 옵션 없이는 멈춘다", raises(lambda: nw.run(jobs, TMP / "net_x", SPLIT, Y, EMOTIONS, **kw), text="--network-bh-family"))
    nw.run(jobs, TMP / "net_out", SPLIT, Y, EMOTIONS, bh_family="by_model", **kw)
    s = pd.read_csv(TMP / "net_out" / "network_scores.tsv", sep="\t")
    pre = pd.read_csv(TMP / "net_out" / "prereg_pvalues.tsv", sep="\t")
    check("6-4a [사전] 1-3은 A-1의 Visual1, Visual2, Default 세 행(묶음마다)", set(pre.test_id) == {"1-3 Visual1", "1-3 Visual2", "1-3 Default"} and len(pre) == 3 * 3)
    ex = s[(s.test_kind == "탐색") & (s.participant == "sub-01")]
    a = ex[ex.model == "A-1"]
    check("6-4a 탐색 BH(by_model): A-1 나머지 묶음과 C-1 묶음을 따로", len(a) == 1 and np.isclose(a.p_bh.iloc[0], a.p_perm.iloc[0]) and np.allclose(ex[ex.model == "C-1"].sort_values("network").p_bh, st.bh(ex[ex.model == "C-1"].sort_values("network").p_perm.to_numpy())))
    d = pd.read_csv(TMP / "net_out" / "network_decoding.tsv", sep="\t")
    check("6-4a C-1 decoded features를 D9 통계로 되돌려 채점(r = 1)", np.isclose(d[(d.participant != "mean5")].mean_dim_r, 1.0).all() and set(d.network) == set(NETS))
    nw.run(jobs, TMP / "net_out2", SPLIT, Y, EMOTIONS, bh_family="pooled", **kw)
    s2 = pd.read_csv(TMP / "net_out2" / "network_scores.tsv", sep="\t")
    e2 = s2[(s2.test_kind == "탐색") & (s2.participant == "sub-01")].sort_values(["model", "network"])
    check("6-4a 탐색 BH(pooled): 나머지 모두 한 묶음", np.allclose(e2.p_bh, st.bh(e2.p_perm.to_numpy())))
    fdec.run(TMP / "s5", TMP / "dec_c1", SPLIT, s6_dir=root / "s6_brain_net_Visual1", n_perm=0, n_boot=20, pvideos=PVIDEOS)
    c1 = pd.read_csv(TMP / "dec_c1" / "c1_decoding_scores.tsv", sep="\t")
    check("2-1 C-1 decoded features(--s6-dir)를 D9 통계로 되돌려 같은 지표로 낸다(순열 p 없음)", np.isclose(c1.mean_dim_r, 1.0).all() and "p_perm" not in c1.columns and set(c1.participant) == set(PIDS + ["mean5"]))
    root_b = TMP / "net_b"
    jobs_b = build_networks(root_b, missing_net="Default")
    check("6-4a 빠진 묶음이 있으면 멈춘다", raises(lambda: nw.run(jobs_b, TMP / "net_b1", SPLIT, Y, EMOTIONS, bh_family="by_model", **kw), text="빠진 입력"))
    nw.run(jobs_b, TMP / "net_b2", SPLIT, Y, EMOTIONS, partial_check=True, **kw)
    check("6-4a --partial-check는 빠진 목록을 쓴다", (TMP / "net_b2" / "missing.tsv").exists())


# 6-3

def build_mc(root, drop=None, const=None, hk_plan="final_for_mc"):
    rng = np.random.default_rng(8)
    vids = np.arange(101, 173)
    y = rng.random((72, N_EMO)) * (rng.random((72, N_EMO)) < 0.5)
    y[:, 5] = 0.0
    for m in mc.MODELS:
        for seed in mc.SEEDS:
            for q in mc.MC_PIDS:
                if drop == (m, seed, q):
                    continue
                d = root / m / f"seed{seed}" / q
                d.mkdir(parents=True)
                order = rng.permutation(72)
                p = np.clip(y + rng.normal(0, 0.3, y.shape), 0.001, 0.999)
                if const == (m, seed, q):
                    p[:, 7] = 0.3
                extra = dict(v_hat=np.ones((72, 6)) + rng.normal(0, 1, (72, 6)), c_hat=rng.normal(0, 1, (72, 4))) if m == "brain_decoded" else {}
                np.savez(d / "test_pred_wd10.npz", video_id=vids[order], p=p[order], **{k: v[order] for k, v in extra.items()})
                np.savez(d / "scoring.npz", video_id=vids[order], y=y[order], vision=rng.normal(0, 1, (72, 6)), caption=rng.normal(0, 1, (72, 4)), n_repeats=np.full(72, 5),
                         visual_mean=np.zeros(6), visual_std=np.ones(6), caption_mean=np.zeros(4), caption_std=np.ones(4))
                (d / "done.json").write_text(json.dumps(dict(condition=m, seed=seed, participant=q, chosen_input_wd=10.0, settings=dict(hk_plan=hk_plan))))
    return y


def t_mc():
    root = TMP / "mc"
    y = build_mc(root)
    kw = dict(n_boot=40, n_perm=30, emotions=EMOTIONS)
    mc.run(root, TMP / "mc_out", **kw)
    s = pd.read_csv(TMP / "mc_out" / "mc_scores.tsv", sep="\t")
    check("6-3 72개에서 평정이 상수인 정서는 두 조건 모두에서 빼고 센다", (s.n_rating_constant == 1).all() and (s[s.participant != "mean_mc"].n_emotions_used == N_EMO - 1).all())
    cp = pd.read_csv(TMP / "mc_out" / "mc_comparison.tsv", sep="\t")
    a = s.set_index(["seed", "participant", "model"]).score_r
    check("6-3 두 모델 차이 = C-1 − A-1(seed마다)", np.isclose(cp[(cp.seed == 1) & (cp.participant == "mc-03")].estimate.iloc[0], a[1, "mc-03", "C-1"] - a[1, "mc-03", "A-1"]))
    ss = pd.read_csv(TMP / "mc_out" / "mc_seed_summary.tsv", sep="\t")
    check("6-3 seed는 평균과 표준편차로만 묶는다", (ss.n_seeds == 3).all() and set(ss.participant) == set(mc.MC_PIDS) | {"mean_mc"})
    root_c = TMP / "mc_c"
    build_mc(root_c, const=("brain_only", 1, "mc-02"))
    check("6-3 예측이 일정한 정서가 있으면 범위 옵션 없이 멈춘다", raises(lambda: mc.run(root_c, TMP / "mc_c1", **kw), text="--constant-prediction-scope"))
    mc.run(root_c, TMP / "mc_c2", scope="unit", **kw)
    e = pd.read_csv(TMP / "mc_c2" / "mc_per_emotion.tsv", sep="\t")
    u = e[(e.emotion == "emo7")]
    check("6-3 상수 예측 정서는 그 참가자와 seed의 두 모델 모두에서 뺀다(unit)", (~u[(u.seed == 1) & (u.participant == "mc-02")].used_in_mean).all() and u[(u.seed == 0)].used_in_mean.all())
    root_d = TMP / "mc_d"
    build_mc(root_d, hk_plan="outer_fold1")
    check("6-3 S8 확인용 실행은 거절한다", raises(lambda: mc.run(root_d, TMP / "mc_d1", **kw), text="확인용"))
    root_e = TMP / "mc_e"
    build_mc(root_e, drop=("brain_decoded", 2, "mc-06"))
    check("6-3 빠진 단위가 있으면 최종 표를 내지 않는다", raises(lambda: mc.run(root_e, TMP / "mc_e1", **kw), text="빠진 입력"))


def main():
    for f in (t_stats, t_decoding, t_swap, t_perturb, t_zone, t_network, t_mc):
        f()
    bad = [n for n, ok in RESULTS if not ok]
    print("통과", len(RESULTS) - len(bad), "실패", len(bad), bad)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
