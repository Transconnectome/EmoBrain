#!/usr/bin/env python3
"""S2: 모든 실행이 같은 자료 경계를 쓰도록 분할, 내용 구역, 이름표 짝, ROI, 묶음, MC 표를 파일로 고정한다 (04 S2, 2026-11-04).

단계(--stage)
  split   : HK 개발 영상 분할(v1 fold를 그대로 쓰고 1363의 run 묶음만 1349의 fold로 옮김, fold는 통합문서처럼 1~6), 세션 검사(O8), 세션별 정서 평균, 참가자별 block 표, fold 역할(H2, O7)
  blocks  : 내용 구역 k-means 5개(4-3, J2), 구역 기록, 거리 점검, 학습량 대조 표본, 정서별 0이 아닌 학습 영상 수
  pairs   : 이름표 짝(4-2, O9), 짝 연결 묶음과 순서 없는 쌍(O4), 참가자별 빠진 쌍 수
  roi     : 370개 ROI의 참가자별 voxel 열 번호(저자 피질 + 새 피질하, 정할 것 5~7), ROI 표, CAB-NP 13묶음(6-4)
  mc      : MC 시청 자료의 입력층 학습과 검증 run(O29), 시험 72개, HK와 MC의 영상 ID 대응(6-3). 표만 읽고 반응은 읽지 않는다
  brain   : 새 지도의 영역 평균(개발 block과 반복 쌍만), HK 참가자 간 일치도(K7, 13묶음), HK 반복 신뢰도(14쌍). 정서 정답은 읽지 않는다. 이 결과로 지도나 묶음을 바꾸지 않는다
  order   : 배열의 열 순서 후보(NumPy, Fortran)의 공간 연속성을 11명에서 본다(HK 개발 block, MC 입력층 학습 block만)
  check   : 04 S2의 확인 기준 검사와 provenance 기록

정서 정답은 세션별 평균(2-0)과 구역별 0이 아닌 학습 영상 수(4-3)를 적을 때만 읽고, 분할, 구역, 짝을 정하는 데 쓰지 않는다.
MC 시험 반응은 읽지 않는다. 최종 때까지 쓰지 않기로 했으므로(11/3 석진 님) MC 반복 신뢰도는 지금 내지 않는다. 반응 배열은 allowed_response_rows와 read_rows를 거쳐서만 읽는다.
11/4에 order 단계가 MC 6명의 시험 block 40개씩을 읽은 일이 있다. 고쳤고 사실은 04 기록 칸에 있다.
출력: 작은 표 manifests/s2/, 큰 파일 project/output/final_2026-11/s2_manifest/
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
import scipy.sparse as sp
import sklearn
from sklearn.cluster import KMeans

PM = Path("/pscratch/sd/s/sjmoon")
REPO = PM / "EmoBrain"
HERE = REPO / "project/analysis/final_2026-11"
OUT = HERE / "manifests/s2"
BIG = REPO / "project/output/final_2026-11/s2_manifest"
V1 = REPO / "docs/reports/prelim_2026-10/splits/horikawa_rungroup6_v1.tsv"
CROSSWALK = REPO / "prereg_v2/manifests/stimulus_crosswalk.tsv"
MC72 = HERE / "manifests/mc_test72.tsv"
LABEL_MAP = HERE / "manifests/label_map_34.tsv"
LABELS = REPO / "project/shared/data/cowen_horikawa_labels.csv"
SEMANTIC = PM / "Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/semantic_features.csv"
ABNORMAL = HERE / "manifests/abnormal_blocks_hk.tsv"
MC_RUNS = HERE / "manifests/mc_train_runs.tsv"
CABNP = PM / "atlas_sources/cab_np/CortexSubcortex_ColeAnticevic_NetPartition_wSubcorGSR_parcels_LR_LabelKey.txt"
PUB = REPO / "project/output/final_2026-11/s1_original_rois"
NEW = REPO / "project/output/final_2026-11/s1_subcortex_rebuild"
HK = ["01", "02", "03", "04", "05"]
MC = ["01", "02", "03", "04", "05", "06"]
K = 6
N_BLOCKS = 5
SPLIT_ID = "hk_dev_rungroup6_v2"
SEED_CONTROL_SAMPLE = 20261104  # 6-2에 쓸 학습량 대조 표본
SEED_DISTANCE_CHECK = 20261105  # 거리 점검의 20번 반복
NETWORK_KO = {"Visual1": "1차 시각", "Visual2": "2차 시각", "Auditory": "청각", "Somatomotor": "체성감각운동", "Cingulo-Opercular": "cingulo-opercular", "Dorsal-Attention": "dorsal attention", "Frontoparietal": "frontoparietal", "Default": "Default", "Language": "언어", "Posterior-Multimodal": "posterior multimodal", "Ventral-Multimodal": "ventral multimodal", "Orbito-Affective": "orbito-affective"}
SUBCORTEX_DISPLAY = {"nuc_accum": "BA34 ROI", "hyppocampus": "hippocampus"}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def allowed_response_rows(cohort, s):
    """반응 배열에서 읽어도 되는 행을 metadata로 먼저 정한다. 행 번호를 고정 슬라이스로 잡지 않는다.
    HK는 개발 block, MC는 입력층 학습 block(input_train)뿐이다. MC 배열은 시험 세션이 맨 앞에 있으므로 앞쪽 행을 읽으면 시험 반응이 된다."""
    mc = set(pd.read_csv(MC72, sep="\t").canonical_stimulus_id)
    if cohort == "hk":
        cw = pd.read_csv(CROSSWALK, sep="\t", comment="#").set_index("video_number").canonical_stimulus_id
        t = pd.read_csv(OUT / "participant_blocks_hk.tsv", sep="\t")
        t = t[t.participant == f"sub-{s}"]
        canon = t.video_id.map(cw)
    else:
        t = pd.read_csv(OUT / "mc_blocks.tsv", sep="\t")
        t = t[(t.participant == f"sub-{s}") & (t.role == "input_train")]
        canon = t.canonical_id
    if len(t) == 0 or canon.isna().any() or canon.isin(mc).any():
        raise ValueError(f"{cohort} sub-{s}: 허용 행에 MC 시험 72개와 같은 내용이 있거나 표가 비었다")
    return np.sort(t.qc_row.to_numpy())


def read_rows(raw, rows, allowed):
    """반응 배열을 읽는 유일한 입구. 허용되지 않은 행을 요청하면 읽기 전에 멈춘다."""
    rows = np.asarray(rows)
    if not np.isin(rows, allowed).all():
        raise ValueError(f"허용되지 않은 반응 행 요청: {rows[~np.isin(rows, allowed)][:5]}")
    return np.asarray(raw[rows], np.float64)


def tsv(df, name):
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / name, sep="\t", index=False, float_format="%.6g")


def hk_samples(s, usable=True):
    f = "samples_qc_usable" if usable else "samples_qc"
    return pd.read_csv(PM / f"Horikawa/sub-{s}/v3_qc/sub-{s}_{f}.tsv", sep="\t")


def semantic():
    c = pd.read_csv(SEMANTIC)
    ids = c.iloc[:, 0].str.replace("stimulus_", "").astype(int).to_numpy()
    assert (ids == np.arange(1, 2197)).all()
    return c.columns[1:].tolist(), c.iloc[:, 1:].to_numpy(float)  # 행 i = video_id i + 1


def labels34():
    m = pd.read_csv(LABEL_MAP, sep="\t")
    y = pd.read_csv(LABELS).set_index("stim_num_int")
    assert (y.index.to_numpy() == np.arange(1, 2186)).all()
    return m.name.tolist(), y[m.score_col.tolist()].to_numpy(float)  # 행 i = content_id i + 1


def label_distance(a, b):
    """이름표 거리(4-2) = √(73개 이름표마다 두 영상의 값 차이를 제곱해 평균한 값). a: n×73, b: m×73 → n×m."""
    return np.sqrt(((a[:, None, :] - b[None, :, :]) ** 2).mean(2))


def load_split():
    return pd.read_csv(OUT / "split_hk_dev.tsv", sep="\t")


# ---------- split
def stage_split():
    v1 = pd.read_csv(V1, sep="\t")
    cw = pd.read_csv(CROSSWALK, sep="\t", comment="#").set_index("video_number").canonical_stimulus_id
    mc = set(pd.read_csv(MC72, sep="\t").canonical_stimulus_id)
    assert len(mc) == 72
    T = v1[["video_id", "content_id", "run_index", "exclude_duplicate", "analysis_row"]].copy()
    T["canonical_id"] = T.video_id.map(cw)
    assert T.canonical_id.notna().all() and len(T) == 2196
    T["dev"] = T.analysis_row & ~T.canonical_id.isin(mc)
    assert int(T.analysis_row.sum()) == 2181 and int(T.dev.sum()) == 2109, (int(T.analysis_row.sum()), int(T.dev.sum()))
    # 같은 내용(canonical, 1349와 1363 포함)이 든 run을 묶는다. v1과 같은 규칙에 B2의 묶음을 더한 것이다.
    parent = {r: r for r in T.run_index.unique()}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for _, g in T.groupby("canonical_id"):
        rs = g.run_index.unique()
        for r in rs[1:]:
            parent[find(r)] = find(rs[0])
    T["run_group"] = T.run_index.map(find)
    # v1의 fold를 그대로 쓴다(04 S2). 파일 fold 0~5 = 통합문서 fold 1~6(불일치 4).
    # 바꾸는 것은 하나뿐이다. B2에 따라 1363이 든 v1 run 묶음을 1349가 든 fold로 옮긴다. 라벨과 뇌 자료는 쓰지 않는다.
    T["fold"] = v1.fold.to_numpy() + 1
    rows_1349, rows_1363 = v1[v1.video_id == 1349].iloc[0], v1[v1.video_id == 1363].iloc[0]
    moved_group = rows_1363.run_group
    T.loc[v1.run_group == moved_group, "fold"] = int(rows_1349.fold) + 1
    moved_runs = sorted(v1[v1.run_group == moved_group].run_index.unique().tolist())
    print(f"v1에서 옮긴 run 묶음 {moved_group}(run_index {moved_runs}): fold {int(rows_1363.fold) + 1} → {int(rows_1349.fold) + 1}")
    assert T.groupby("run_group").fold.nunique().max() == 1
    assert T.groupby("run_index").fold.nunique().max() == 1
    assert T.groupby("canonical_id").fold.nunique().max() == 1
    D = T[T.dev].copy()
    print("fold별 개발 영상", D.groupby("fold").size().to_dict(), "run", T.groupby("fold").run_index.nunique().to_dict())
    print("v1 fold별 개발 영상(파일 번호 + 1)", (v1[v1.video_id.isin(D.video_id)].fold + 1).value_counts().sort_index().to_dict())
    print("1349, 1363:", D[D.video_id.isin([1349, 1363])][["video_id", "run_index", "fold"]].to_dict("records"))
    # 참가자별 block 표
    rows, common = [], None
    ab = pd.read_csv(ABNORMAL, sep="\t")
    flagged = {(r.participant, r.video_id) for r in ab[ab.abnormal_block.astype(bool)].itertuples()}
    flagged_runs = {(r.participant, r.run_index) for r in ab[ab.abnormal_run.astype(bool)].itertuples()}
    session = {}
    for s in HK:
        u = hk_samples(s)
        session[s] = hk_samples(s, usable=False).drop_duplicates("run_index").set_index("run_index").session
        u = u[u.video_id.isin(D.video_id)]
        common = set(u.video_id) if common is None else common & set(u.video_id)
        for r in u.itertuples():
            rows.append(dict(participant=f"sub-{s}", video_id=int(r.video_id), content_id=int(r.content_id), qc_row=int(r.qc_row), run_index=int(r.run_index), session=r.session, abnormal_block_note=(f"sub-{s}", int(r.video_id)) in flagged, abnormal_run_note=(f"sub-{s}", int(r.run_index)) in flagged_runs))
    P = pd.DataFrame(rows)
    D["in_all_5"] = D.video_id.isin(common)
    D["n_participants"] = D.video_id.map(P.groupby("video_id").size()).fillna(0).astype(int)
    D["split_id"] = SPLIT_ID
    D = D.sort_values("video_id")
    tsv(D[["split_id", "video_id", "content_id", "canonical_id", "run_index", "run_group", "fold", "in_all_5", "n_participants"]], "split_hk_dev.tsv")
    tsv(P.sort_values(["participant", "qc_row"]), "participant_blocks_hk.tsv")
    print("참가자별 개발 block", P.groupby("participant").size().to_dict(), "5명 공통 영상", len(common), "표시만 하는 이상 block", int(P.abnormal_block_note.sum()), "이상 run block", int(P.abnormal_run_note.sum()))
    # fold 역할
    roles = [dict(role="outer", test_fold=k, val_fold=k % K + 1, train_folds=",".join(str(j) for j in range(1, K + 1) if j not in (k, k % K + 1))) for k in range(1, K + 1)]
    roles.append(dict(role="final_for_mc_O7", test_fold="", val_fold=1, train_folds="2,3,4,5,6"))
    tsv(pd.DataFrame(roles), "fold_roles.tsv")
    # 세션 검사(O8)
    rows, viol = [], []
    test_runs = D.groupby("fold").run_index.unique()
    all_runs = T.groupby("fold").run_index.unique()
    for s in HK:
        for k in range(1, K + 1):
            for what, runs in [("dev_runs", test_runs[k]), ("all_runs", all_runs[k])]:
                c = session[s].reindex(runs).value_counts()
                rows.append(dict(participant=f"sub-{s}", fold=k, runs_counted=what, n_test_runs=len(runs), n_sessions=int(c.size), max_runs_from_one_session=int(c.max())))
                if c.size == 1:
                    viol.append((s, k, what))
    tsv(pd.DataFrame(rows), "session_check.tsv")
    S = pd.DataFrame(rows)
    print("세션 검사(개발 run)", S[S.runs_counted == "dev_runs"].groupby("fold")[["n_test_runs", "n_sessions", "max_runs_from_one_session"]].agg(["min", "max"]).to_string())
    if viol:
        raise SystemExit(f"O8 위반: {viol}. 분할을 바꾸지 않고 멈춘다.")
    # 세션별 정서 평균(2-0). 분할에 쓰지 않고 확인만 한다
    names, Y = labels34()
    rows, summ = [], []
    for s in HK:
        u = P[P.participant == f"sub-{s}"]
        y = pd.DataFrame(Y[u.content_id.values - 1], columns=names)
        y["session"] = u.session.values
        m = y.groupby("session").mean()
        for sess, r in m.iterrows():
            rows += [dict(participant=f"sub-{s}", session=sess, emotion=e, mean=float(r[e])) for e in names]
        sd = y[names].std()
        z = ((m - y[names].mean()) / sd).abs()
        summ.append(dict(participant=f"sub-{s}", n_sessions=len(m), median_abs_diff_in_sd=float(np.median(z.values)), max_abs_diff_in_sd=float(z.values.max()), emotion_at_max=z.max().idxmax()))
    tsv(pd.DataFrame(rows), "session_emotion_means.tsv")
    tsv(pd.DataFrame(summ), "session_emotion_summary.tsv")
    print(pd.DataFrame(summ).round(3).to_string(index=False))


# ---------- blocks
def stage_blocks():
    D = load_split()
    label_names, X_all = semantic()
    emo, Y = labels34()
    vids = D.video_id.to_numpy()
    X = X_all[vids - 1]
    fit = lambda: KMeans(n_clusters=N_BLOCKS, n_init=10, random_state=0).fit_predict(X)
    lab = fit()
    assert np.array_equal(lab, fit()), "같은 설정으로 다시 돌린 구역 배정이 다르다"
    # 번호만 크기 순으로 바꾼다(배정은 그대로)
    order = pd.Series(lab).value_counts().index.tolist()
    block = np.array([order.index(x) + 1 for x in lab])
    D["block"] = block
    tsv(D[["video_id", "fold", "block"]], "content_blocks_assignment.tsv")
    rows, dist, nz, ctrl = [], [], [], []
    for z in range(1, N_BLOCKS + 1):
        m = block == z
        centroid = X[m].mean(0)
        top = np.argsort(-centroid)[:3]
        near = vids[m][np.argsort(((X[m] - centroid) ** 2).sum(1))[:5]]
        rows.append(dict(block=z, n_videos=int(m.sum()), top_labels=", ".join(label_names[i] for i in top), top_label_means=", ".join(f"{centroid[i]:.3f}" for i in top), sample_videos=",".join(map(str, near))))
    tsv(pd.DataFrame(rows), "content_blocks.tsv")
    print(pd.DataFrame(rows).to_string(index=False))
    content = D.content_id.to_numpy()
    fold = D.fold.to_numpy()
    for z in range(1, N_BLOCKS + 1):
        for k in range(1, K + 1):
            te = (fold == k) & (block == z)
            pool = fold != k
            tr_ex = pool & (block != z)
            n = int(tr_ex.sum())
            idx_pool = np.flatnonzero(pool)
            d_ex = label_distance(X[te], X[tr_ex]).min(1)
            reps = []
            rng = np.random.default_rng([SEED_DISTANCE_CHECK, z, k])
            for _ in range(20):
                pick = rng.choice(idx_pool, n, replace=False)
                reps.append(label_distance(X[te], X[pick]).min(1))
            d_ct = np.mean(reps, 0)
            dist.append(dict(block=z, fold=k, n_test=int(te.sum()), n_train_excluded=n, median_excluded=float(np.median(d_ex)), median_control=float(np.median(d_ct)), ratio=float(np.median(d_ex) / np.median(d_ct)), frac_test_farther=float((d_ex > d_ct).mean())))
            # 6-2에 쓸 학습량 대조 표본(구역과 fold마다 하나)
            pick = np.sort(np.random.default_rng([SEED_CONTROL_SAMPLE, z, k]).choice(idx_pool, n, replace=False))
            ctrl += [dict(block=z, fold=k, video_id=int(v)) for v in vids[pick]]
            y_ex, y_ct = Y[content[tr_ex] - 1], Y[content[pick] - 1]
            nz += [dict(block=z, fold=k, emotion=e, n_nonzero_excluded=int((y_ex[:, i] > 0).sum()), n_nonzero_control=int((y_ct[:, i] > 0).sum())) for i, e in enumerate(emo)]
    Dt = pd.DataFrame(dist)
    tsv(Dt, "content_block_distance.tsv")
    tsv(pd.DataFrame(ctrl), "content_block_control_samples.tsv")
    tsv(pd.DataFrame(nz), "content_block_nonzero.tsv")
    print(Dt.groupby("block").agg(n_test_min=("n_test", "min"), n_test_max=("n_test", "max"), train_min=("n_train_excluded", "min"), train_max=("n_train_excluded", "max"), median_excluded=("median_excluded", "median"), median_control=("median_control", "median"), ratio_min=("ratio", "min"), ratio_med=("ratio", "median"), farther=("frac_test_farther", "mean")).round(3).to_string())
    print("거리가 대조보다 늘지 않은 (구역, fold):", Dt[Dt.ratio <= 1][["block", "fold", "ratio"]].to_dict("records"))
    N = pd.DataFrame(nz)
    print("정서별 0이 아닌 학습 영상 수 최솟값(구역 제외):", N.groupby("block").n_nonzero_excluded.min().to_dict(), "(대조):", N.groupby("block").n_nonzero_control.min().to_dict())


# ---------- pairs
def stage_pairs():
    D = load_split()
    _, X_all = semantic()
    P = pd.read_csv(OUT / "participant_blocks_hk.tsv", sep="\t")
    rows, groups, unordered = [], [], []
    for k in range(1, K + 1):
        v = np.sort(D[D.fold == k].video_id.to_numpy())
        d = label_distance(X_all[v - 1], X_all[v - 1])
        np.fill_diagonal(d, np.inf)
        nearest = d.min(1)
        tied = np.isclose(d, nearest[:, None], rtol=0, atol=1e-12)
        pick = tied.argmax(1)  # v가 오름차순이므로 동점이면 영상 ID가 작은 쪽(O9)
        parent = {int(x): int(x) for x in v}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        for i, a in enumerate(v):
            b = v[pick[i]]
            rows.append(dict(fold=k, video_a=int(a), video_b=int(b), distance=float(nearest[i]), n_tied=int(tied[i].sum()), mutual=bool(v[pick[pick[i]]] == a)))
            parent[find(int(a))] = find(int(b))
        roots = {}
        for a in v:
            r = find(int(a))
            roots.setdefault(r, len(roots) + 1)
            groups.append(dict(fold=k, video_id=int(a), pair_group=f"f{k}g{roots[r]}"))
    R = pd.DataFrame(rows)
    G = pd.DataFrame(groups)
    seen = set()
    for r in R.itertuples():
        key = (min(r.video_a, r.video_b), max(r.video_a, r.video_b))
        if key not in seen:
            seen.add(key)
            unordered.append(dict(fold=r.fold, video_a=key[0], video_b=key[1], distance=r.distance, mutual=r.mutual))
    U = pd.DataFrame(unordered)
    G["group_size"] = G.pair_group.map(G.groupby("pair_group").size())
    tsv(R, "pairs_directed.tsv")
    tsv(G, "pair_groups.tsv")
    tsv(U, "pairs_unordered.tsv")
    have = {s: set(P[P.participant == f"sub-{s}"].video_id) for s in HK}
    miss = [dict(participant=f"sub-{s}", n_directed_all=len(R), n_directed_missing=int((~(R.video_a.isin(have[s]) & R.video_b.isin(have[s]))).sum()), n_unordered_all=len(U), n_unordered_missing=int((~(U.video_a.isin(have[s]) & U.video_b.isin(have[s]))).sum())) for s in HK]
    tsv(pd.DataFrame(miss), "pair_missing_counts.tsv")
    gs = G.drop_duplicates("pair_group").group_size.value_counts().sort_index().to_dict()
    print("짝", len(R), "거리 중앙값", round(R.distance.median(), 4), "최댓값", round(R.distance.max(), 4), "동점 있는 영상", int((R.n_tied > 1).sum()), "서로 최근접 영상", int(R.mutual.sum()), "순서 없는 쌍", len(U), "서로 최근접 쌍", int(U.mutual.sum()))
    print("연결 묶음 수", G.pair_group.nunique(), "크기 분포", gs)
    print(pd.DataFrame(miss).to_string(index=False))
    print("1349의 짝:", R[R.video_a.isin([1349, 1363])][["video_a", "video_b", "distance"]].to_dict("records"))


# ---------- roi
def roi_table():
    z = np.load(PUB / "hk_sub-01_rois.npz")
    names = [str(x) for x in z["roi"]]
    key = pd.read_csv(CABNP, sep="\t")
    net = {r.GLASSERLABELNAME: r.NETWORK for r in key.itertuples() if isinstance(r.GLASSERLABELNAME, str)}
    rows = []
    for i, n in enumerate(names):
        if n.startswith("hcp180_"):
            g = net[n.replace("hcp180_", "") + "_ROI"]
            rows.append(dict(roi_index=i, roi=n, display=n.replace("hcp180_", ""), kind="cortex", source="저자 공개 ROI", group=g, group_ko=NETWORK_KO[g]))
        else:
            rows.append(dict(roi_index=i, roi=n, display=SUBCORTEX_DISPLAY.get(n, n), kind="subcortex", source="새 mask(PickAtlas, 1 mm 중심 방식)", group="Subcortex", group_ko="피질하 해부학적 묶음"))
    T = pd.DataFrame(rows)
    assert len(T) == 370 and T.group.nunique() == 13, T.group.nunique()
    return T


def stage_roi():
    T = roi_table()
    tsv(T, "roi_table.tsv")
    g = T.groupby(["group", "group_ko"]).size().reset_index(name="n_roi").sort_values("n_roi", ascending=False)
    tsv(g, "cabnp_groups.tsv")
    print(g.to_string(index=False))
    (BIG / "roi_voxels").mkdir(parents=True, exist_ok=True)
    rows = []
    for cohort, root, ver, subs in [("hk", "Horikawa", "v3", HK), ("mc", "MindCaptioning", "v2", MC)]:
        for s in subs:
            tag = f"{cohort}_sub-{s}"
            m = nib.load(PM / root / f"sub-{s}/{ver}_qc/sub-{s}_mask_qc.nii.gz")
            mask = np.asarray(m.dataobj) > 0
            n_col = np.load(PM / root / f"sub-{s}/{ver}_qc/sub-{s}_blocks_common36_qc_runz.npy", mmap_mode="r").shape[1]
            assert int(mask.sum()) == n_col
            col = np.full(mask.shape, -1, np.int64)
            col[mask] = np.arange(n_col)  # 전처리 기록: 배열의 열은 QC mask의 NumPy 기본 순서
            z = np.load(PUB / f"{tag}_rois.npz")
            ijk, M, names = z["ijk"].astype(int), z["member"], [str(x) for x in z["roi"]]
            assert names == T.roi.tolist()
            keep = ((ijk >= 0) & (ijk < np.array(mask.shape))).all(1)
            nz = np.load(NEW / f"{tag}_new_masks.npz")
            assert tuple(nz["shape"]) == mask.shape and np.array_equal(nz["affine"], m.affine)
            new = {str(r): nz["overlap_2mm"][i] for i, r in enumerate(nz["roi"])}
            offsets, columns = [0], []
            for c, n in enumerate(names):
                if n in new:
                    v = new[n]
                else:
                    v = np.zeros(mask.shape, bool)
                    v[tuple(ijk[keep & M[:, c]].T)] = True
                cols = np.sort(col[v & mask])
                assert len(cols) > 0, (tag, n)
                columns.append(cols)
                offsets.append(offsets[-1] + len(cols))
                rows.append(dict(cohort=cohort, participant=f"sub-{s}", roi=n, n_in_grid=int(v.sum()), n_voxels=len(cols)))
            np.savez_compressed(BIG / "roi_voxels" / f"{tag}.npz", roi=np.array(names), offsets=np.array(offsets, np.int64), columns=np.concatenate(columns).astype(np.int32), n_columns=n_col, affine=m.affine, shape=np.array(mask.shape), mask_sha256=sha(PM / root / f"sub-{s}/{ver}_qc/sub-{s}_mask_qc.nii.gz"))
            print(tag, "ROI voxel 합", offsets[-1], flush=True)
    V = pd.DataFrame(rows)
    tsv(V, "roi_voxel_counts.tsv")
    good = V[V.n_voxels > 0].groupby("roi").size()
    print("11명 모두 voxel이 있는 ROI", int((good == 11).sum()), "최소", int(V.n_voxels.min()))


# ---------- mc
def stage_mc():
    cw = pd.read_csv(CROSSWALK, sep="\t", comment="#").set_index("video_number").canonical_stimulus_id
    mc72 = set(pd.read_csv(MC72, sep="\t").canonical_stimulus_id)
    runs = pd.read_csv(MC_RUNS, sep="\t")
    rows = []
    for s in MC:
        u = pd.read_csv(PM / f"MindCaptioning/sub-{s}/v2_qc/sub-{s}_samples_qc_usable.tsv", sep="\t")
        r = runs[(runs.participant == f"sub-{s}") & runs.used_for_input_layer.astype(bool)].sort_values("run_index")
        assert len(r) == 58, len(r)
        val = set(r.run_index.to_numpy()[4::5])  # 58개 run의 5, 10, ..., 55번째(O29)
        assert len(val) == 11
        use = set(r.run_index)
        for x in u.itertuples():
            if x.part == "test":
                role = "test_72"
            elif x.run_index in use:
                role = "input_val" if x.run_index in val else "input_train"
            else:
                role = "excluded_test_runs"
            rows.append(dict(participant=f"sub-{s}", video_id=int(x.video_id), canonical_id=int(cw[x.video_id]), qc_row=int(x.qc_row), session=x.session, run_index=int(x.run_index), part=x.part, rep=int(x.rep), role=role))
    M = pd.DataFrame(rows)
    assert M[M.role.isin(["input_train", "input_val"])].canonical_id.isin(mc72).sum() == 0, "입력층 학습에 시험 영상이 있다"
    assert M[M.role == "test_72"].canonical_id.isin(mc72).all()
    tsv(M, "mc_blocks.tsv")
    print(M.groupby(["participant", "role"]).size().unstack().to_string())
    print("input 고유 영상", M[M.role.isin(["input_train", "input_val"])].groupby("participant").video_id.nunique().to_dict())
    T = M[M.role == "test_72"]
    print("시험 영상 수", T.groupby("participant").video_id.nunique().to_dict(), "반복 수 범위", T.groupby(["participant", "video_id"]).size().agg(["min", "max"]).to_dict())
    D = load_split()
    idmap = pd.DataFrame({"mc_video_id": sorted(set(M.video_id))})
    idmap["canonical_id"] = idmap.mc_video_id.map(cw)
    first = D.drop_duplicates("canonical_id").set_index("canonical_id").video_id
    idmap["hk_dev_video_id"] = idmap.canonical_id.map(first)
    v1 = pd.read_csv(V1, sep="\t")
    v1["canonical_id"] = v1.video_id.map(cw)
    ana = v1[v1.analysis_row].groupby("canonical_id").video_id.apply(lambda x: ",".join(map(str, sorted(x))))
    idmap["hk_analysis_video_ids"] = idmap.canonical_id.map(ana)
    idmap["is_mc_test_72"] = idmap.canonical_id.isin(mc72)
    tsv(idmap, "hk_mc_id_map.tsv")
    print("MC 영상", len(idmap), "HK 개발에 없는 MC 영상", int(idmap.hk_dev_video_id.isna().sum()), "그중 시험 72개", int((idmap.hk_dev_video_id.isna() & idmap.is_mc_test_72).sum()))


# ---------- brain
def roi_matrix(tag):
    z = np.load(BIG / "roi_voxels" / f"{tag}.npz")
    off, col = z["offsets"], z["columns"]
    n = np.diff(off)
    rows = np.repeat(np.arange(len(n)), n)
    return sp.csr_matrix((np.ones(len(col), np.float32) / n[rows], (rows, col)), shape=(len(n), int(z["n_columns"])))


def corr_rows(a, b):
    a = a - a.mean(1, keepdims=True)
    b = b - b.mean(1, keepdims=True)
    a = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-12)
    b = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-12)
    return a @ b.T


def ident(S):
    d = np.diag(S)
    return float(np.mean([(d[i] > np.delete(S[i], i)).mean() for i in range(len(S))]))


def stage_brain():
    T = pd.read_csv(OUT / "roi_table.tsv", sep="\t")
    P = pd.read_csv(OUT / "participant_blocks_hk.tsv", sep="\t")
    D = load_split()
    mats, rep_rows = {}, []
    (BIG / "roi_means").mkdir(parents=True, exist_ok=True)
    cw = pd.read_csv(CROSSWALK, sep="\t", comment="#").set_index("video_number").canonical_stimulus_id
    mc72 = set(pd.read_csv(MC72, sep="\t").canonical_stimulus_id)
    for s in HK:
        tag = f"hk_sub-{s}"
        A = roi_matrix(tag)
        Y = np.load(PM / f"Horikawa/sub-{s}/v3_qc/sub-{s}_blocks_common36_qc_runz.npy", mmap_mode="r")
        # 반복 신뢰도: 같은 내용이 두 번 제시된 쌍(MC 72개와 같은 내용 제외)
        u = hk_samples(s)
        u["canonical_id"] = u.video_id.map(cw)
        g = u[u.groupby("content_id").video_id.transform("size") == 2]
        g = g[~g.canonical_id.isin(mc72)].sort_values(["content_id", "onset_sec"])
        first = g[~g.exclude_duplicate.astype(bool)].set_index("content_id")
        second = g[g.exclude_duplicate.astype(bool)].set_index("content_id")
        ids = first.index.intersection(second.index)
        a, b = first.loc[ids].qc_row.to_numpy(), second.loc[ids].qc_row.to_numpy()
        # 읽는 행은 개발 block과 반복 쌍뿐이다. MC 시험 72개와 같은 내용의 block은 읽지 않는다. 읽지 않은 행은 NaN으로 둔다
        allowed = np.union1d(allowed_response_rows("hk", s), np.r_[a, b])
        assert not u[u.qc_row.isin(allowed)].canonical_id.isin(mc72).any()
        R = np.full((Y.shape[0], A.shape[0]), np.nan, np.float32)
        for chunk in np.array_split(allowed, max(1, len(allowed) // 64)):
            R[chunk] = (A @ read_rows(Y, chunk, allowed).astype(np.float32).T).T
        np.save(BIG / "roi_means" / f"{tag}_roi370_runz.npy", R)
        S = corr_rows(R[a], R[b])
        rep_rows.append(dict(participant=f"sub-{s}", group="all_370_roi_means", n_pairs=len(ids), same_pair_r=float(np.diag(S).mean()), diff_pair_r=float(S[~np.eye(len(S), dtype=bool)].mean()), identification=ident(S)))
        z = np.load(BIG / "roi_voxels" / f"{tag}.npz")
        Xa, Xb = read_rows(Y, a, allowed), read_rows(Y, b, allowed)
        for grp, sub in T.groupby("group"):
            cols = np.unique(np.concatenate([z["columns"][z["offsets"][i]:z["offsets"][i + 1]] for i in sub.roi_index]))
            Sg = corr_rows(Xa[:, cols], Xb[:, cols])
            rep_rows.append(dict(participant=f"sub-{s}", group=grp, n_pairs=len(ids), same_pair_r=float(np.diag(Sg).mean()), diff_pair_r=float(Sg[~np.eye(len(Sg), dtype=bool)].mean()), identification=ident(Sg), n_voxels=len(cols)))
        p = P[P.participant == f"sub-{s}"]
        mats[s] = pd.DataFrame(R[p.qc_row.to_numpy()], index=p.video_id.to_numpy())
        print(tag, "ok", len(ids), "쌍", flush=True)
    tsv(pd.DataFrame(rep_rows), "reliability_hk_repeat_pairs.tsv")
    common = sorted(D[D.in_all_5].video_id)
    Astack = np.stack([mats[s].loc[common].to_numpy(np.float64) for s in HK])
    isc = np.zeros((5, Astack.shape[2]))
    for i in range(5):
        o = np.delete(Astack, i, 0).mean(0)
        x = Astack[i] - Astack[i].mean(0)
        y = o - o.mean(0)
        isc[i] = (x * y).sum(0) / np.sqrt((x * x).sum(0) * (y * y).sum(0))
    I = T[["roi_index", "roi", "display", "group", "group_ko"]].copy()
    for i, s in enumerate(HK):
        I[f"sub-{s}"] = isc[i]
    I["mean"] = isc.mean(0)
    tsv(I, "agreement_hk_roi.tsv")
    G = I.groupby(["group", "group_ko"])["mean"].agg(["median", "min", "max", "count"]).reset_index().sort_values("median", ascending=False)
    tsv(G, "agreement_hk_13groups.tsv")
    print("공통 영상", len(common), "ROI 일치도 중앙값", round(float(I["mean"].median()), 3))
    print(G.round(3).to_string(index=False))
    print(pd.DataFrame(rep_rows).groupby("group")[["same_pair_r", "diff_pair_r", "identification"]].mean().round(3).sort_values("same_pair_r", ascending=False).to_string())


# ---------- order
def stage_order():
    """배열의 열 순서 후보(NumPy, Fortran) 가운데 어느 쪽이 공간적으로 연속인지 보는 진단이다. 모든 열 순서를 배제하는 증명이 아니다.
    직접 근거는 생성 코드의 volume[mask].T(HK response_v3.py 414행, MC response_v2.py 383행)와 QC 열 보존 기록이다.
    HK는 개발 block, MC는 입력층 학습 block 앞 40개의 정규화 전 평균 패턴을 쓴다. 정서 정답은 읽지 않는다."""
    rows = []
    for cohort, root, ver, subs in [("hk", "Horikawa", "v3", HK), ("mc", "MindCaptioning", "v2", MC)]:
        for s in subs:
            mask = np.asarray(nib.load(PM / root / f"sub-{s}/{ver}_qc/sub-{s}_mask_qc.nii.gz").dataobj) > 0
            raw = np.load(PM / root / f"sub-{s}/{ver}_qc/sub-{s}_blocks_common36_qc.npy", mmap_mode="r")
            allowed = allowed_response_rows(cohort, s)
            pat = read_rows(raw, allowed[:40], allowed).mean(0)
            idx = np.argwhere(mask)
            orders = {"numpy": idx, "fortran": idx[np.lexsort((idx[:, 0], idx[:, 1], idx[:, 2]))]}
            for name, ijk in orders.items():
                vol = np.zeros(mask.shape)
                vol[tuple(ijk.T)] = pat
                rec = dict(cohort=cohort, participant=f"sub-{s}", order=name)
                for ax in range(3):
                    a, b = [slice(None)] * 3, [slice(None)] * 3
                    a[ax], b[ax] = slice(None, -1), slice(1, None)
                    both = mask[tuple(a)] & mask[tuple(b)]
                    rec[f"neighbor_r_axis{ax}"] = float(np.corrcoef(vol[tuple(a)][both], vol[tuple(b)][both])[0, 1])
                rows.append(rec)
    t = pd.DataFrame(rows)
    tsv(t, "column_order_check.tsv")
    print(t.groupby("order")[["neighbor_r_axis0", "neighbor_r_axis1", "neighbor_r_axis2"]].agg(["min", "max"]).round(3).to_string())
    n = t[t.order == "numpy"].filter(like="neighbor").min(axis=1).min()
    f = t[t.order == "fortran"].filter(like="neighbor").min(axis=1).max()
    assert n > f, (n, f)
    print("NumPy 순서의 세 축 최솟값", round(n, 3), "Fortran 순서의 세 축 최솟값 중 최댓값", round(f, 3))


# ---------- check
def stage_check():
    D = load_split()
    cw = pd.read_csv(CROSSWALK, sep="\t", comment="#").set_index("video_number").canonical_stimulus_id
    mc = set(pd.read_csv(MC72, sep="\t").canonical_stimulus_id)
    assert D.video_id.is_unique and len(D) == 2109
    assert D.groupby("run_index").fold.nunique().max() == 1
    assert D.groupby("canonical_id").fold.nunique().max() == 1, "같은 내용 영상 쌍이 다른 fold"
    assert D[D.video_id == 1349].fold.iloc[0] == D[D.video_id == 1363].fold.iloc[0]
    P = pd.read_csv(OUT / "participant_blocks_hk.tsv", sep="\t")
    # 영상 단위 표이므로 한 영상의 5명 행은 fold가 하나뿐이다. 참가자 행이 분할 밖이 아닌지 본다
    assert P.video_id.isin(D.video_id).all()
    fold_by_video = D.set_index("video_id").fold
    assert P.groupby("video_id").video_id.first().map(fold_by_video).notna().all()
    assert P.groupby(["participant", "video_id"]).size().max() == 1
    tables = {"split_hk_dev.tsv": ["video_id"], "participant_blocks_hk.tsv": ["video_id"], "content_blocks_assignment.tsv": ["video_id"], "content_block_control_samples.tsv": ["video_id"], "pairs_directed.tsv": ["video_a", "video_b"], "pairs_unordered.tsv": ["video_a", "video_b"], "pair_groups.tsv": ["video_id"]}
    for name, cols in tables.items():
        t = pd.read_csv(OUT / name, sep="\t")
        for c in cols:
            assert not t[c].map(cw).isin(mc).any(), (name, c)
    R = pd.read_csv(OUT / "pairs_directed.tsv", sep="\t")
    assert (R.video_a != R.video_b).all()
    assert (R.video_a.map(fold_by_video) == R.video_b.map(fold_by_video)).all(), "짝이 다른 fold"
    A = pd.read_csv(OUT / "content_blocks_assignment.tsv", sep="\t")
    assert A.video_id.tolist() == D.video_id.tolist() and A.block.nunique() == N_BLOCKS
    C = pd.read_csv(OUT / "content_block_control_samples.tsv", sep="\t").merge(D[["video_id", "fold"]], on="video_id", suffixes=("", "_video"))
    assert (C.fold != C.fold_video).all(), "학습량 대조 표본에 시험 fold 영상이 있다"
    S = pd.read_csv(OUT / "session_check.tsv", sep="\t")
    assert (S.n_sessions > 1).all()
    Mt = pd.read_csv(OUT / "mc_blocks.tsv", sep="\t")
    assert not Mt[Mt.role.isin(["input_train", "input_val"])].canonical_id.isin(mc).any()
    assert set(Mt[Mt.role == "test_72"].canonical_id) == mc and Mt[Mt.role == "test_72"].groupby("participant").video_id.nunique().eq(72).all()
    # 회귀 검사: MC 배열은 시험 세션이 맨 앞에 있다. 반응을 읽는 입구가 시험 행과 입력 검증 행을 막는지 가짜 배열로 본다(실제 반응은 읽지 않는다)

    class FakeRaw:
        def __init__(self):
            self.keys = []

        def __getitem__(self, k):
            self.keys.append(np.asarray(k))
            return np.zeros((len(k), 3), np.float32)
    for s in MC:
        t = Mt[Mt.participant == f"sub-{s}"]
        allowed = allowed_response_rows("mc", s)
        assert set(allowed) == set(t[t.role == "input_train"].qc_row)
        front = t.sort_values("qc_row").qc_row.to_numpy()[:40]
        assert t.set_index("qc_row").loc[front].role.eq("test_72").all(), "MC 배열 앞쪽이 시험 행이 아니다. 검사 전제를 다시 볼 것"
        fake = FakeRaw()
        read_rows(fake, allowed[:40], allowed)
        assert np.isin(fake.keys[0], t[t.role == "input_train"].qc_row).all()
        for bad in (front, t[t.role == "input_val"].qc_row.to_numpy()[:5], t[t.role == "excluded_test_runs"].qc_row.to_numpy()[:5]):
            fake = FakeRaw()
            try:
                read_rows(fake, bad, allowed)
            except ValueError:
                assert not fake.keys
            else:
                raise AssertionError(f"sub-{s}: 허용되지 않은 MC 행을 읽었다")
    for s in HK:
        a = allowed_response_rows("hk", s)
        assert set(a) == set(P[P.participant == f"sub-{s}"].qc_row)
    V = pd.read_csv(OUT / "roi_voxel_counts.tsv", sep="\t")
    assert V.groupby(["cohort", "participant"]).roi.nunique().eq(370).all() and (V.n_voxels > 0).all()
    roi_files = sorted((BIG / "roi_voxels").glob("*.npz"))
    assert len(roi_files) == 11
    for f in roi_files:
        z = np.load(f)
        assert len(z["roi"]) == 370 and z["offsets"][-1] == len(z["columns"]) and z["columns"].max() < int(z["n_columns"]) and z["columns"].min() >= 0
    commit = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    inputs = [V1, CROSSWALK, MC72, LABEL_MAP, LABELS, SEMANTIC, ABNORMAL, MC_RUNS, CABNP] + roi_files
    for cohort, root, ver, subs in [("hk", "Horikawa", "v3", HK), ("mc", "MindCaptioning", "v2", MC)]:
        for x in subs:
            inputs += [PM / root / f"sub-{x}/{ver}_qc/sub-{x}_mask_qc.nii.gz", PM / root / f"sub-{x}/{ver}_qc/sub-{x}_samples_qc_usable.tsv"]
    info = dict(split_id=SPLIT_ID, code=str(Path(__file__).relative_to(REPO)), code_sha256=sha(__file__), git_head_when_checked=commit, sklearn=sklearn.__version__, kmeans=dict(n_clusters=N_BLOCKS, n_init=10, random_state=0), seed_control_sample=SEED_CONTROL_SAMPLE, seed_distance_check=SEED_DISTANCE_CHECK, input_sha256={str(p): sha(p) for p in inputs}, output_sha256={f.name: sha(f) for f in sorted(OUT.glob("*.tsv"))})
    (OUT / "provenance.json").write_text(json.dumps(info, indent=1, ensure_ascii=False))
    print("확인 기준 통과. sklearn", sklearn.__version__)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["split", "blocks", "pairs", "roi", "mc", "brain", "order", "check", "all"])
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    BIG.mkdir(parents=True, exist_ok=True)
    stages = dict(split=stage_split, blocks=stage_blocks, pairs=stage_pairs, roi=stage_roi, mc=stage_mc, brain=stage_brain, order=stage_order, check=stage_check)
    for name in (list(stages) if a.stage == "all" else [a.stage]):
        print(f"===== {name}", flush=True)
        stages[name]()


if __name__ == "__main__":
    main()
