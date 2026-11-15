#!/usr/bin/env python3
"""S10 2부 합성 자료 시험 (2026-11-15). 실제 정답, 실제 예측, 실제 특징, GPU를 쓰지 않는다. 결과 폴더는 임시 폴더에 만든다.
시험: 특징 순열 r(참가자에게 없는 영상이 들어오는 경우 포함)과 짝 열 가중 r의 손 계산, 2-1(이어 붙이기, 차원 r 평균, 순열 p, 식별, 빠진 fold),
2-2(audition_codex와 같은 관찰 효과, 짝 연결 묶음 재표집이 반복 표본과 같음, Δy와 짝 대조, 빠진 fold), 6-4b(fold 합으로 낸 r과 하락, 빠진 fold),
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

def build_perturb(root, drop_fold=None, units=("Default", "Visual1"), rep=3):
    rng = np.random.default_rng(3)
    truth = {}
    for k in range(1, 7):
        rows = [(q, v) for q in PIDS for v in PVIDEOS[q] if SPLIT.fold[SPLIT.video_id == v].iloc[0] == k]
        pid = np.array([q for q, _ in rows])
        vid = np.array([v for _, v in rows])
        y = Y[vid - 1]
        onehot = np.stack([pid == q for q in PIDS], 1).astype(float)
        sums = lambda p: np.stack([onehot.T @ p, onehot.T @ (p * p), onehot.T @ (p * y)])
        arr = dict(video_id=vid, participant=pid, donors=np.zeros((rep, len(vid)), int), donor_seed=np.array(1), unit_kind=np.array(["group"] * len(units) + ["roi"]),
                   unit_name=np.array(list(units) + ["L_V1"]), sum_y=onehot.T @ y, sum_yy=onehot.T @ (y * y), n=onehot.sum(0))
        for m in pt.MODELS:
            base = np.clip(y + rng.normal(0, 0.3, y.shape), 0, 1)
            pert = np.clip(base[None, None] + rng.normal(0, 0.2, (len(units) + 1, rep) + y.shape), 0, 1)
            truth[m, k] = (pid, vid, base, pert)
            arr[f"{m}_base"] = sums(base)
            arr[f"{m}_perturbed"] = np.stack([np.stack([sums(pert[u, t]) for t in range(rep)]) for u in range(len(units) + 1)])
        if k == drop_fold:
            continue
        d = root / f"outer_fold{k}_seed0"
        d.mkdir(parents=True)
        np.savez(d / "perturb_sums.npz", **arr)
        (d / "done.json").write_text("{}")
    return truth


def t_perturb():
    root = TMP / "pert"
    truth = build_perturb(root)
    ag = pd.DataFrame(dict(group=["Default", "Visual1"], group_ko=["d", "v"], median=[0.1, 0.2], min=[0, 0], max=[1, 1], count=[3, 2]))
    pt.run(root, TMP / "pert_out", SPLIT, Y, EMOTIONS, agreement=ag)
    t = pd.read_csv(TMP / "pert_out" / "network_drops.tsv", sep="\t")
    pid = np.concatenate([truth["brain_only", k][0] for k in range(1, 7)])
    vid = np.concatenate([truth["brain_only", k][1] for k in range(1, 7)])
    m = pid == "sub-02"
    base = np.concatenate([truth["brain_only", k][2] for k in range(1, 7)])[m]
    pert = np.concatenate([truth["brain_only", k][3] for k in range(1, 7)], 2)[:, :, m]
    yq = Y[vid[m] - 1]
    rb = st.pearson_columns(yq, base)
    keep = np.isfinite(rb)
    drops = [rb[keep].mean() - st.pearson_columns(yq, pert[0, t_])[keep].mean() for t_ in range(pert.shape[1])]
    row = t[(t.unit == "Default") & (t.participant == "sub-02")].iloc[0]
    check("6-4b 하락 = fold 합으로 모은 r의 (원래 − 교란) 점수를 반복마다 내 평균", np.isclose(row.drop_A1, np.mean(drops)) and np.isclose(row.base_score_A1, rb[keep].mean()))
    check("6-4b 하락폭 차이 = C-1 − A-1, 일치도를 붙이고 구간이 없다는 사실을 적는다", np.isclose(row.drop_difference, row.drop_C1 - row.drop_A1) and row.agreement_median == 0.1 and row.uncertainty == pt.NO_UNCERTAINTY)
    root_b = TMP / "pert_b"
    build_perturb(root_b, drop_fold=4)
    check("6-4b 빠진 fold가 있으면 최종 표를 내지 않는다", raises(lambda: pt.run(root_b, TMP / "pert_out_b", SPLIT, Y, EMOTIONS, agreement=ag), text="빠진 입력"))
    pt.run(root_b, TMP / "pert_out_c", SPLIT, Y, EMOTIONS, agreement=ag, partial_check=True)
    check("6-4b --partial-check는 점검용", (pd.read_csv(TMP / "pert_out_c" / "network_drops.tsv", sep="\t").n_folds == 5).all())
    Y2 = Y.copy()
    Y2[0, 0] += 0.5
    check("6-4b 저장된 사람 평정 합이 다르면 멈춘다", raises(lambda: pt.run(root, TMP / "pert_out_d", SPLIT, Y2, EMOTIONS, agreement=ag), text="사람 평정 합"))


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
