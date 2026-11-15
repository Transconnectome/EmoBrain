#!/usr/bin/env python3
"""S10 합성 자료 시험 (2026-11-15). 실제 정답, 실제 예측, GPU를 쓰지 않는다. 결과 폴더는 임시 폴더에 만든다.
시험: 모은 r과 손 계산, fold r 평균과 다름, 계산 불가(NaN)와 그 수, R²와 MAE와 오차 감소의 정의(01 6-0 예시), D_k 평균, 가중 r과 반복 표본,
basic 구간과 중심 맞춘 p의 식, 순열이 block 안에 머물고 34개 벡터를 함께 옮기며 5명에 같은 순열을 씀, 같은 내용 쌍 규칙, Holm과 BH 손 계산, seed 요약,
합친 S6 폴더 끝에서 끝까지(0 후보 fold, D-4 ensemble, 빠진 fold, 5명 공통 영상, 행 대조, 계산 가능한 정서가 다른 비교, 레포 안 출력 거절), [사전] 15개 Holm.
사용(레포 최상위): python tests/s10_tests.py. EMOBRAIN_PYTHON_CPU(matplotlib이 있는 Python)가 있으면 그림도 그려 본다.
"""
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1] / "src"))  # 코드는 src에 있다
_sys.dont_write_bytecode = True
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "4")  # login node를 다 쓰지 않는다
import numpy as np
import pandas as pd

import s10_stats as st
import s10_performance as perf
import s10_holm15 as h15

RESULTS = []
N_EMO = 34
PIDS = [f"sub-0{i}" for i in range(1, 6)]


def check(name, ok):
    RESULTS.append((name, bool(ok)))
    print("통과" if ok else "실패", name, flush=True)


def raises(fn, exc=(ValueError, SystemExit), text=None):
    try:
        fn()
    except exc as e:
        return text is None or text in str(e)
    return False


# 통계 함수

def t_pooled_r():
    rng = np.random.default_rng(0)
    y = rng.random((40, 3))
    p = y + rng.normal(0, 0.3, (40, 3))
    p[:20] += 1.0  # fold 1의 예측만 크게 옮긴다. fold 안 r은 그대로이고 모은 r은 달라진다
    r = st.pearson_columns(y, p)
    manual = np.array([np.corrcoef(y[:, j], p[:, j])[0, 1] for j in range(3)])
    check("모은 r = np.corrcoef", np.allclose(r, manual))
    fold_mean = (st.pearson_columns(y[:20], p[:20]) + st.pearson_columns(y[20:], p[20:])) / 2
    check("모은 r은 fold r 평균과 다르다(2-3)", not np.allclose(r, fold_mean))


def t_nan():
    rng = np.random.default_rng(1)
    y, p = rng.random((30, 4)), rng.random((30, 4))
    y[:, 1] = 0.0
    p[:, 2] = 0.3
    y[:, 3], p[:, 3] = 0.2, 0.4
    r = st.pearson_columns(y, p)
    check("상수 평정, 상수 예측의 r은 NaN이고 0이 아니다", np.isnan(r[1:]).all() and np.isfinite(r[0]))
    reason = st.noncomputable_reason(y, p).tolist()
    check("계산 불가 이유를 나눠 센다", reason == ["", "rating_constant", "prediction_constant", "rating_and_prediction_constant"])
    m = st.emotion_metrics(y, p)
    check("R²는 평정이 상수이면 NaN", np.isnan(m["r2"][[1, 3]]).all() and np.isfinite(m["r2"][[0, 2]]).all())
    keep = np.isfinite(m["r"])
    check("참가자 점수는 계산할 수 있는 정서만 평균", np.isclose(st.mean_over(m["r"], keep), r[0]))
    check("NaN 예측은 계산 실패로 멈춘다", raises(lambda: st.pearson_columns(y, np.where(p > 0.5, np.nan, p))))


def t_metrics_definition():
    # 01 6-0의 disgust 예시
    y = np.array([0.5, 0.2, 0.1, 0.0, 0.0])
    p = np.array([0.3, 0.15, 0.08, 0.05, 0.02])
    m = st.emotion_metrics(y, p, np.full(5, 0.1))
    check("6-0 예시 MAE 0.068", np.isclose(m["mae"][0], 0.068))
    check("6-0 예시 R² = 1 − MSE / 평정 분산 = 0.73", np.isclose(m["r2"][0], 1 - ((p - y)**2).mean() / y.var()) and np.isclose(m["r2"][0], 0.73, atol=0.005))
    check("6-0 예시 r 0.99", np.isclose(m["r"][0], 0.99, atol=0.005))
    check("평정 0인 영상의 MAE(N19)", np.isclose(m["mae_zero"][0], (0.05 + 0.02) / 2))
    check("평정이 0보다 큰 영상의 MAE(N19)", np.isclose(m["mae_nonzero"][0], (0.2 + 0.05 + 0.02) / 3))
    check("0이 아닌 영상 수와 평정 분산", m["n_nonzero"][0] == 3 and np.isclose(m["rating_var"][0], y.var()))
    sse = ((p - y)**2).sum()
    check("오차 감소(O25) = 1 − Σ(y − p)² / Σ(y − m)²", np.isclose(m["error_reduction"][0], 1 - sse / ((y - 0.1)**2).sum()))
    fold = np.array([1, 1, 2, 2, 3])
    yy = np.array([[0.0], [0.2], [0.4], [0.6], [1.0]])
    w = np.array([1.0, 1.0, 2.0, 1.0, 1.0])
    dk = st.dk_means(fold, yy, w, [1, 2, 3])
    check("D_k 평균은 그 fold를 뺀 가중 평균", np.isclose(dk[1][0], (0.8 + 0.6 + 1.0) / 4) and np.isclose(dk[3][0], (0 + 0.2 + 0.8 + 0.6) / 5))


def t_bootstrap():
    rng = np.random.default_rng(2)
    y, p = rng.random((25, 3)), rng.random((25, 3))
    counts = rng.integers(0, 3, size=(4, 25))
    counts[:, 0] = 1
    r = st.boot_r(counts, y, {"a": p})["a"]
    manual = np.stack([st.pearson_columns(np.repeat(y, w, 0), np.repeat(p, w, 0)) for w in counts])
    check("가중 r = 뽑힌 횟수만큼 반복한 표본의 r", np.allclose(r, manual))
    w = np.zeros((1, 25), int)
    w[0, :3] = 1
    yc = y.copy()
    yc[:3, 1] = 0.25
    check("재표집 안에서 상수인 열은 NaN", np.isnan(st.boot_r(w, yc, {"a": p})["a"][0, 1]))
    codes, n = st.unit_codes([10, 10, 11, 12, 12, 13])
    cnt = st.bootstrap_counts(n, 500, np.random.default_rng(3))
    wv = cnt[:, codes]
    check("뽑힌 횟수의 합은 단위 수", (cnt.sum(1) == n).all())
    check("같은 내용 묶음은 함께 뽑힌다", (wv[:, 0] == wv[:, 1]).all() and (wv[:, 3] == wv[:, 4]).all())
    boot = np.arange(1001) / 1000
    lo, hi = st.basic_ci(1.0, boot)
    check("basic 구간 [2θ − q(0.975), 2θ − q(0.025)]", np.isclose(lo, 2 - 0.975) and np.isclose(hi, 2 - 0.025))
    p_c = st.centered_p(0.5, np.array([0.5, 0.6, 1.1, 1.0, -0.1, 0.0, np.nan]))
    check("중심 맞춘 p = (1 + #(|Δ* − Δ| ≥ |Δ|)) / (B + 1), NaN은 뺌", np.isclose(p_c, 5 / 7))


def t_permutation():
    blocks = np.array(["a"] * 5 + ["b"] * 4 + ["c"] * 6)
    perm = st.block_permutations(blocks, 300, np.random.default_rng(4))
    within = all((blocks[perm[i]] == blocks).all() for i in range(len(perm)))
    check("순열은 block 안에 머문다", within)
    check("행마다 전체 순열이다", all(np.array_equal(np.sort(row), np.arange(len(blocks))) for row in perm))
    check("순열이 실제로 섞는다", (perm != np.arange(len(blocks))).any())
    rng = np.random.default_rng(5)
    y = rng.random((15, N_EMO))
    pos_a, pos_b = np.arange(15), np.array([0, 2, 3, 5, 6, 9, 10, 12, 14])
    pa, pb = rng.random((15, N_EMO)), rng.random((9, N_EMO))
    ra = st.permuted_r(perm[:50], pos_a, y, {"x": pa})["x"]
    rb = st.permuted_r(perm[:50], pos_b, y, {"x": pb})["x"]
    man_a = np.stack([st.pearson_columns(y[perm[i, pos_a]], pa) for i in range(50)])
    man_b = np.stack([st.pearson_columns(y[perm[i, pos_b]], pb) for i in range(50)])
    check("순열 r = 34개 벡터를 통째로 옮긴 사람 평정의 r(참가자 A)", np.allclose(ra, man_a))
    check("같은 순열을 영상이 다른 참가자 B에도 쓴다", np.allclose(rb, man_b))
    yy = np.arange(15)[:, None] * 100.0 + np.arange(N_EMO)[None, :]
    moved = yy[perm[7]]
    check("한 영상의 34개 값은 함께 옮겨진다", np.allclose(moved - moved[:, :1], np.arange(N_EMO)[None, :]))
    check("한쪽 순열 p = (1 + #(귀무 ≥ 관찰)) / (n + 1)", np.isclose(st.permutation_p(0.3, np.array([0.1, 0.3, 0.5, 0.2])), 3 / 5))
    content = np.arange(15).astype(str)
    content[6] = content[1]  # 다른 block(a, b)의 같은 내용 쌍
    check("다른 run에 나뉜 같은 내용 쌍은 옵션 없이 멈춘다", raises(lambda: st.check_content_units(blocks, content, False), text="--split-content-pairs"))
    check("옵션이 있으면 나뉜 쌍을 기록하고 진행한다", len(st.check_content_units(blocks, content, True)) == 1)
    content2 = np.arange(15).astype(str)
    content2[2] = content2[1]  # 같은 block a
    check("한 block 안의 같은 내용 쌍은 멈춘다", raises(lambda: st.check_content_units(blocks, content2, True)))


def t_multiple():
    p = np.array([0.01, 0.04, 0.03, 0.005])
    check("Holm 손 계산", np.allclose(st.holm(p), [0.03, 0.06, 0.06, 0.02]))
    check("BH 손 계산", np.allclose(st.bh(p), [0.02, 0.04, 0.04, 0.02]))
    q = np.array([0.01, np.nan, 0.04])
    check("NaN은 묶음에서 빼고 보정", np.allclose(st.holm(q), [0.02, np.nan, 0.04], equal_nan=True) and np.allclose(st.bh(q), [0.02, np.nan, 0.04], equal_nan=True))
    check("보정 p는 1을 넘지 않는다", st.holm(np.array([0.6, 0.7]))[1] == 1.0 and st.bh(np.array([0.9, 0.95])).max() <= 1.0)
    t = pd.DataFrame(dict(condition=["a", "a", "b"], seed=[0, 1, 0], score=[0.2, 0.4, 0.3]))
    s = st.seed_summary(t, ["condition"], ["score"]).set_index("condition")
    check("seed 요약: 평균과 표준편차(ddof=1), seed 하나면 NaN", np.isclose(s.loc["a", "score_mean"], 0.3) and np.isclose(s.loc["a", "score_sd"], np.std([0.2, 0.4], ddof=1)) and np.isnan(s.loc["b", "score_sd"]))


# 끝에서 끝까지

def fake_split():
    rows, vid = [], 1
    for k in range(1, 7):
        for j in range(2):
            run = (k - 1) * 2 + j + 1
            for _ in range(6):
                rows.append(dict(split_id="fake", video_id=vid, content_id=vid, canonical_id=vid, run_index=run, run_group=run, fold=k))
                vid += 1
    s = pd.DataFrame(rows)
    a, b = s.video_id[(s.fold == 4) & (s.run_index == 7)].iloc[0], s.video_id[(s.fold == 4) & (s.run_index == 8)].iloc[0]
    s.loc[s.video_id == b, "canonical_id"] = a  # 1349, 1363처럼 같은 fold 다른 run의 같은 내용 쌍
    return s


MISSING_05 = [3, 20, 33, 50, 61]  # sub-05에 없는 영상(B7)


def participant_videos(split):
    ids = split.video_id.tolist()
    return {q: np.array([v for v in ids if not (q == "sub-05" and v in MISSING_05)]) for q in PIDS}


def build_s6(root, split, y, *, drop_row=False, constant_emotion=None):
    """합친 S6 폴더. 조건마다 예측 = 사람 평정 + 조건별 잡음. 돌려주는 값: (조건, seed) -> 참가자 -> fold -> 예측."""
    videos = participant_videos(split)
    fold_of = dict(zip(split.video_id, split.fold))
    ypos = {v: i for i, v in enumerate(split.video_id)}
    conds = {"brain_only": [0, 1], "brain_only_featdec": [0, 1], "brain_only_distill": [0], "control_label_smoothing": [0], "brain_decoded": [0], "brain_decoded_distill": [0],
             "brain_frozen_feature_encoder": [0], "brain_decoded_additive": [0]}
    truth = {}
    for k in range(1, 7):
        fo = root / f"outer_fold{k}"
        (fo / "plan").mkdir(parents=True)
        parts, vids, roles = [], [], []
        for q in PIDS:
            for v in videos[q]:
                parts.append(q), vids.append(v), roles.append(2 if fold_of[v] == k else 0)
        np.savez(fo / "plan" / "rows.npz", participant=np.array(parts), video_id=np.array(vids), role=np.array(roles))
        for ci, (cond, seeds) in enumerate(conds.items()):
            if cond == "brain_decoded_additive" and k == 3:
                continue  # 빠진 fold
            sel = dict(seeds={}, zero_selected=False)
            for s in seeds:
                zero = cond == "brain_only_distill" and k == 2
                rel = f"brain_only/c0_seed{s}" if zero else f"{cond}/c{ci}_seed{s}"
                sel["seeds"][str(s)] = rel
                sel["zero_selected"] = zero
                if zero:
                    for q in PIDS:
                        truth.setdefault((cond, s), {}).setdefault(q, {})[k] = truth[("brain_only", s)][q][k]
                    continue
                rng = np.random.default_rng(1000 * k + 10 * ci + s)
                P, V, Q = [], [], []
                for q in PIDS:
                    vv = np.array([v for v in videos[q] if fold_of[v] == k])
                    pr = np.clip(y[[ypos[v] for v in vv]] + rng.normal(0, 0.2 + 0.05 * ci, (len(vv), N_EMO)), 0.001, 0.999)
                    if constant_emotion is not None and cond == "brain_only_featdec":
                        pr[:, constant_emotion] = 0.5
                    truth.setdefault((cond, s), {}).setdefault(q, {})[k] = (vv, pr)
                    P.append(pr), V.append(vv), Q.append(np.full(len(vv), q))
                P, V, Q = np.concatenate(P), np.concatenate(V), np.concatenate(Q)
                if drop_row and cond == "brain_only" and k == 1:
                    P, V, Q = P[1:], V[1:], Q[1:]
                d = fo / rel
                if S_paired(cond):
                    (d / "ensemble").mkdir(parents=True)
                    np.savez(d / "ensemble" / "test_pred.npz", participant=Q, video_id=V, p=P, logit=np.log(P / (1 - P)), p_pairs=np.stack([P] * 4))
                else:
                    d.mkdir(parents=True)
                    np.savez(d / "test_pred.npz", participant=Q, video_id=V, p=P, logit=np.log(P / (1 - P)))
            (fo / cond).mkdir(exist_ok=True)
            (fo / cond / "selected.json").write_text(json.dumps(sel))
    return truth


def S_paired(cond):
    return perf.S.CONDITIONS[cond].paired


def pooled(truth, key, q, y, split):
    ypos = {v: i for i, v in enumerate(split.video_id)}
    items = [truth[key][q][k] for k in range(1, 7)]
    v = np.concatenate([a for a, _ in items])
    p = np.concatenate([b for _, b in items])
    o = np.argsort(v)
    return y[[ypos[x] for x in v[o]]], p[o]


def fake_y(split):
    rng = np.random.default_rng(7)
    y = rng.random((len(split), N_EMO)) * (rng.random((len(split), N_EMO)) < 0.5)
    y[:, -1] = 0.0  # 모든 영상에서 0인 정서(계산 불가)
    return y


def t_end_to_end():
    split = fake_split()
    videos = participant_videos(split)
    common = set.intersection(*[set(v.tolist()) for v in videos.values()])
    split["in_all_5"] = split.video_id.isin(common)
    y = fake_y(split)
    emotions = [f"emo{e}" for e in range(N_EMO)]
    tmp = Path(tempfile.mkdtemp(prefix="s10_tests_"))
    s6 = tmp / "s6"
    truth = build_s6(s6, split, y)
    kw = dict(dk_mode="participant", n_boot=300, n_perm=300)
    check("같은 내용 쌍이 다른 run에 있으면 옵션 없이 멈춘다", raises(lambda: perf.run(s6, tmp / "out_x", split, y, emotions, split_pairs=False, **kw), text="--split-content-pairs"))
    check("D_k 평균 방식을 정하지 않으면 멈춘다", raises(lambda: perf.run(s6, tmp / "out_y", split, y, emotions, split_pairs=True, **{**kw, "dk_mode": "auto"})))
    seen = {}
    orig = st.block_permutations

    def spy(blocks, n, rng):
        seen.setdefault("blocks", []).append(np.asarray(blocks))
        return orig(blocks, n, rng)
    st.block_permutations = spy
    try:
        info = perf.run(s6, tmp / "out", split, y, emotions, split_pairs=True, **kw)
    finally:
        st.block_permutations = orig
    out = tmp / "out"
    want_blocks = np.array([f"fold{f}_run{r}" for f, r in zip(split.fold, split.run_index)])
    check("순열 block = 같은 시험 fold, 같은 원래 run(O4 (1))", np.array_equal(seen["blocks"][0], want_blocks))
    pe = pd.read_csv(out / "all" / "per_emotion.tsv", sep="\t")
    ps = pd.read_csv(out / "all" / "participant_scores.tsv", sep="\t")
    cov = pd.read_csv(out / "coverage.tsv", sep="\t")
    rows = pd.read_csv(out / "rows.tsv", sep="\t").set_index("participant")

    yq, pq = pooled(truth, ("brain_only", 0), "sub-01", y, split)
    got = pe[(pe.condition == "brain_only") & (pe.seed == 0) & (pe.participant == "sub-01")].r.to_numpy()
    check("표의 r = 6 fold를 모은 손 계산 r", np.allclose(got, st.pearson_columns(yq, pq), equal_nan=True))
    check("모든 영상이 0인 정서는 계산 불가로 표시", np.isnan(got[-1]) and pe[(pe.participant == "sub-01") & (pe.emotion == "emo33")].reason.eq("rating_constant").all())
    nc = pd.read_csv(out / "all" / "noncomputable.tsv", sep="\t")
    check("계산 불가 수를 센다", (nc.n_rating_constant == 1).all() and (nc.n_computable == N_EMO - 1).all())
    sc = ps[(ps.condition == "brain_only") & (ps.seed == 0) & (ps.participant == "sub-01")].iloc[0]
    check("참가자 점수 = 계산 가능한 33개 정서의 r 평균", np.isclose(sc.score_r, np.nanmean(st.pearson_columns(yq, pq))) and sc.n_emotions_used == N_EMO - 1)
    m5 = ps[(ps.condition == "brain_only") & (ps.seed == 0) & (ps.participant == "mean5")].score_r.iloc[0]
    check("5명 평균 = 참가자 점수의 평균", np.isclose(m5, ps[(ps.condition == "brain_only") & (ps.seed == 0) & (ps.participant != "mean5")].score_r.mean()))
    yd, pd_ = pooled(truth, ("brain_only_distill", 0), "sub-02", y, split)
    got = pe[(pe.condition == "brain_only_distill") & (pe.participant == "sub-02")].r.to_numpy()
    check("0 후보 fold는 앞 조건(A-1)의 예측을 읽는다(G10)", np.allclose(got, st.pearson_columns(yd, pd_), equal_nan=True))
    zrow = cov[(cov.condition == "brain_only_distill") & (cov.fold == 2)].iloc[0]
    check("coverage에 0 후보 fold와 그 경로를 적는다", bool(zrow.zero_selected) and zrow.rel.startswith("brain_only/"))
    y4, p4 = pooled(truth, ("brain_frozen_feature_encoder", 0), "sub-03", y, split)
    got = pe[(pe.condition == "brain_frozen_feature_encoder") & (pe.participant == "sub-03")].r.to_numpy()
    check("D-4는 ensemble/test_pred.npz를 읽는다", np.allclose(got, st.pearson_columns(y4, p4), equal_nan=True))
    miss = cov[(cov.condition == "brain_decoded_additive")]
    check("빠진 fold는 coverage에 적고 계산하지 않는다", (miss.used == False).all() and (miss[miss.fold == 3].status == "이 fold에 선택 없음").all())
    comp = pd.read_csv(out / "all" / "comparisons.tsv", sep="\t")
    check("빠진 조건이 든 비교는 빠졌다고 적는다", comp[comp.test_id.str.startswith("1-2(가)")].status.str.startswith("계산하지 않음").all())
    check("seed가 한 조건에만 있으면 적는다", ((comp.test_id == "2-3(다)") & (comp.seed == 1) & comp.status.str.contains("한 조건에만")).any())
    c_da = comp[(comp.test_id == "2-3(다)") & (comp.seed == 0) & (comp.participant == "mean5")].iloc[0]
    sd = ps[(ps.seed == 0) & (ps.participant == "mean5")].set_index("condition").score_r
    check("2-3(다) 5명 평균 차이 = A-2 − A-1", np.isclose(c_da.estimate, sd["brain_only_distill"] - sd["brain_only"]))
    check("차이의 구간과 p가 있다", np.isfinite([c_da.ci_low, c_da.ci_high]).all() and 0 < c_da.p_raw <= 1)
    pre = pd.read_csv(out / "prereg_pvalues.tsv", sep="\t")
    check("[사전] p 파일: 2-3 여섯, 묶음 6개", set(pre.test_id) == {x[0] for x in perf.PREREG_23} and set(pre.family) == set(st.FAMILIES))
    check("[사전] p 파일은 seed마다 쓴다", set(pre[pre.test_id == "2-3(가)"].seed) == {0, 1})
    ce = pd.read_csv(out / "all" / "comparisons_per_emotion.tsv", sep="\t")
    g = ce[(ce.test_id == "2-3(가)") & (ce.seed == 0) & (ce.participant == "sub-01")]
    check("정서별 차이는 탐색이고 BH는 참가자마다, 비교마다", np.allclose(g.p_bh, st.bh(g.p_raw.to_numpy()), equal_nan=True) and g.label.eq("탐색(BH-FDR)").all() and g.family_size.iloc[0] == N_EMO - 1)
    prem = pd.read_csv(out / "all" / "premise_tests.tsv", sep="\t")
    pm = prem[prem.seed == 0]
    check("전제 검정: A-1과 C-1, Holm 2개 묶음", set(pm.condition) == set(perf.PREMISE) and pm.p_holm2.notna().all()
          and all(np.allclose(g.sort_values("condition").p_holm2, st.holm(g.sort_values("condition").p_raw.to_numpy())) for _, g in pm.groupby("participant")))
    check("seed 1만 있는 A-1은 Holm 2개 묶음을 내지 않는다", prem[prem.seed == 1].p_holm2.isna().all())
    check("rows: sub-05는 빠진 영상만큼 적다", rows.loc["sub-05", "n_videos"] == 72 - len(MISSING_05) and rows.loc["sub-01", "n_videos"] == 72)
    pe5 = pd.read_csv(out / "common5" / "per_emotion.tsv", sep="\t")
    check("5명 공통 영상판(B7)은 모두 같은 영상 수", set(pe5[pe5.participant != "mean5"].n_videos) == {72 - len(MISSING_05)})
    ss = pd.read_csv(out / "all" / "seed_summary.tsv", sep="\t")
    r0 = ss[(ss.condition == "brain_only") & (ss.participant == "sub-01")].iloc[0]
    v = ps[(ps.condition == "brain_only") & (ps.participant == "sub-01")].sort_values("seed").score_r
    check("seed 요약은 seed 점수의 평균과 표준편차(예측 평균 아님)", r0.n_seeds == 2 and np.isclose(r0.score_r_mean, v.mean()) and np.isclose(r0.score_r_sd, v.std(ddof=1)))
    ri = json.loads((out / "run_info.json").read_text())
    check("run_info에 설정과 나뉜 같은 내용 쌍 기록", ri["settings"]["dk_mean"] == "participant" and len(ri["analyses"]["all"]["content_groups_split_across_runs"]) == 1)
    check("이미 있는 출력은 --overwrite 없이 덮지 않는다", raises(lambda: perf.run(s6, out, split, y, emotions, split_pairs=True, **kw), text="--overwrite"))
    check("레포 안 git 위치에는 쓰지 않는다", raises(lambda: perf.run(s6, perf.c.REPO / "tests" / "s10_out_should_fail", split, y, emotions, split_pairs=True, **kw), text="레포 안"))

    s6b = tmp / "s6_drop"
    build_s6(s6b, split, y, drop_row=True)
    check("예측 행이 plan 시험 행과 다르면 멈춘다(N11)", raises(lambda: perf.run(s6b, tmp / "out_b", split, y, emotions, split_pairs=True, **kw), text="plan의 시험 행"))
    s6c = tmp / "s6_const"
    build_s6(s6c, split, y, constant_emotion=5)
    check("두 조건의 계산 가능한 정서가 다르면 비교를 멈춘다", raises(lambda: perf.run(s6c, tmp / "out_c", split, y, emotions, split_pairs=True, **kw), text="계산할 수 있는 정서가 다르다"))

    t_holm15(out, tmp)
    cpu = os.environ.get("EMOBRAIN_PYTHON_CPU")
    if cpu:
        r = subprocess.run([cpu, str(perf.c.CODE_DIR / "s10_figures.py"), "--out", str(out)], capture_output=True, text=True)
        check("그림을 그린다(s10_figures)", r.returncode == 0 and (out / "all" / "per_emotion_r_seed0.png").exists() and (out / "common5" / "participant_scores_seed1.png").exists())
    else:
        print("건너뜀 그림 시험: EMOBRAIN_PYTHON_CPU가 없다(scripts/s10_tests.sh로 돌리면 configs/env.sh에서 읽는다)", flush=True)


def t_holm15(out, tmp):
    pre = out / "prereg_pvalues.tsv"
    check("seed가 여럿이면 --seed 없이 멈춘다", raises(lambda: h15.main(["--inputs", str(pre), "--out", str(tmp / "h.tsv")]), text="--seed"))
    code = h15.main(["--inputs", str(pre), "--out", str(tmp / "h.tsv"), "--seed", "0"])
    miss = pd.read_csv(tmp / "h_missing.tsv", sep="\t")
    check("15개가 다 없으면 보정하지 않고 없는 것을 적는다", code == 1 and not (tmp / "h.tsv").exists() and len(miss) == 9 * 6)
    rng = np.random.default_rng(9)
    rows = [dict(test_id=t, family=f, seed="" if t.startswith("2-1") else 0, estimate=rng.normal(), p_raw=float(rng.uniform(0.0001, 0.2))) for t in st.PREREG_15 for f in st.FAMILIES]
    full = pd.DataFrame(rows)
    full.to_csv(tmp / "full.tsv", sep="\t", index=False)
    code = h15.main(["--inputs", str(tmp / "full.tsv"), "--out", str(tmp / "full_holm.tsv"), "--alpha", "0.05"])
    res = pd.read_csv(tmp / "full_holm.tsv", sep="\t")
    ok = code == 0 and all(np.allclose(g.set_index("test_id").loc[list(st.PREREG_15)].p_holm, st.holm(full[full.family == f].set_index("test_id").loc[list(st.PREREG_15)].p_raw.to_numpy())) for f, g in res.groupby("family"))
    check("15개가 다 있으면 묶음마다 Holm(seed 없는 2-1과 함께)", ok)
    cnt = pd.read_csv(tmp / "full_holm_counts.tsv", sep="\t").set_index("test_id")
    part = res[res.family != "mean5"]
    check("--alpha를 주면 보정 전과 후의 확인 수를 센다", int(cnt.n_confirmed_after_holm.sum()) == int((part.p_holm < 0.05).sum()) and int(cnt.n_confirmed_before_holm.sum()) == int((part.p_raw < 0.05).sum()))
    pd.concat([full, full.iloc[:1]]).to_csv(tmp / "dup.tsv", sep="\t", index=False)
    check("같은 검정이 둘이면 멈춘다", raises(lambda: h15.main(["--inputs", str(tmp / "dup.tsv"), "--out", str(tmp / "d.tsv")])))
    bad = full.copy()
    bad.loc[0, "test_id"] = "2-3(사)"
    bad.to_csv(tmp / "bad.tsv", sep="\t", index=False)
    check("15개 밖의 이름은 멈춘다", raises(lambda: h15.main(["--inputs", str(tmp / "bad.tsv"), "--out", str(tmp / "b.tsv")])))


def main():
    for f in (t_pooled_r, t_nan, t_metrics_definition, t_bootstrap, t_permutation, t_multiple, t_end_to_end):
        f()
    bad = [n for n, ok in RESULTS if not ok]
    print("통과", len(RESULTS) - len(bad), "실패", len(bad), bad)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
