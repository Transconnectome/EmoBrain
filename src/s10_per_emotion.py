#!/usr/bin/env python3
"""S10 정서별 모델 비교 (11/17 석진 님 요청. 34개 평균 성능이 비슷한 모델들이 정서별로는 서로 다른 정서를 잘 맞히는가). GPU 없음.

이미 저장된 시험 예측만 쓴다. 모델을 다시 학습하거나 다시 돌리지 않는다.
모델: A-1(기준), B-1, C-1, D-1, D-3, D-4, E-고정, E-학습. distillation 조건(A-2, C-2, D-2)은 11/17 결정(01 5-A)으로 넣지 않는다.
  D-3 짝은 학습이 끝나지 않아 뺀다.
자료
- HK: S6 최종 결과의 seed 0 시험 예측(6 fold를 모음, 5명). 읽기와 행 대조는 s10_performance와 같다(find_predictions, load_condition, same_rows).
  bootstrap은 s10_performance와 같다. 내용 묶음(canonical_id) 단위, BOOT_SEED 20261115, 10,000회, 모든 모델과 5명에 같은 재표집.
- MC: 6-3 전이(A-1, C-1만 있다). 읽기는 s10_mc.load_units. seed 3개의 r을 평균하고 6명을 평균한다(6-3과 같다).
  bootstrap은 72개 영상, 같은 BOOT_SEED, 6명과 seed에 같은 재표집.
계산
- 정서마다 r(참가자마다, 그다음 참가자 평균), Δ = 모델 − A-1, basic 95% 구간, 중심 맞춘 양측 p, BH-FDR(비교마다 34개). 정서별 차이는 탐색이다.
- 표마다 Cowen & Keltner 2017에서 별도 차원으로 남지 않은 7개(01 0절, 27개판에서 빼는 정서)를 표시한다(ck27 열). 우리 결과로 고른 정서가 아니다.
사전 질문과 판정 (11/17, 결과를 보기 전에 적음)
- Q1. 정서별 차이가 사람과 영상이 바뀌어도 재현되는가. C-1 − A-1만 HK와 MC 둘 다 있어 이것으로 한다.
  통계: 두 자료 모두 계산되는 정서에서, HK의 Δ와 MC의 Δ의 Spearman ρ.
  귀무분포: 정서 이름표를 섞는 순열 10,000회(PERM_SEED 20261116). 단측(ρ > 0). p = (1 + #(ρ* ≥ ρ)) / (1 + 10,000).
  판정: ρ > 0이고 p < .05면 "C-1과 A-1의 차이가 큰 정서는 사람과 영상이 바뀌어도 같은 정서다".
  아니면 "정서별 차이의 양상은 자료가 바뀌면 재현되지 않는다. 34개 평균 차이 밖의 정서별 차이는 주장하지 않는다".
  판정에 쓰지 않고 함께 적는 것: 자료마다 Δ와 A-1 r의 Spearman ρ, A-1 r을 통제한 편상관(순위로 바꾼 뒤 A-1 r 순위를 회귀로 뺀 잔차끼리의 상관).
  "A-1이 잘 맞히는 정서일수록 차이가 크다"만으로 재현되는 것인지 보려는 것이다.
- Q2. 모델마다 어느 정서에서 다른가(HK, MC는 C-1만). BH q < .05인 정서의 수와 방향을 보고한다. 판정 규칙은 두지 않는다(탐색).
- Q3. 정서마다의 Vision 대 Caption 지수(imagery_prereg/vision_over_caption_index.tsv, HK 개발 영상에서 뇌 자료 없이 계산해 고정한 값)와
  Δ의 Spearman ρ. 양측 순열 p(같은 순열). 방향은 정하지 않는다(01 2-3, 11/3: 처음 보는 자료에서 어느 경로와 연결된 정서가 유지될지 방향을 정하지 않음).
  모델마다, 자료마다 보고하고 보정하지 않는다(탐색).
한계: 정서들은 서로 상관되어 있어 정서 이름표를 섞는 순열은 정서를 바꿔 쓸 수 있다고 가정한다. HK는 seed 0, MC는 seed 3개 평균이다.
출력(레포 밖 --out): per_emotion.tsv, differences.tsv, counts.tsv, replication.tsv(Q1), vc_index.tsv(Q3), run_info.json
사용: s10_per_emotion.py --s6-dir <S6 최종 결과 폴더> --mc-dir <s8_mc 폴더> --vc-index <vision_over_caption_index.tsv> --out <폴더> --design-freeze <커밋>
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

import s4_common as c
import s10_mc as MC
import s10_performance as PF
import s10_stats as st

BOOT_SEED, PERM_SEED = 20261115, 20261116
MODELS = {"brain_only": "A-1", "brain_only_featdec": "B-1", "brain_decoded": "C-1", "brain_decoded_sep": "D-1",
          "brain_features_only": "D-3", "brain_frozen_feature_encoder": "D-4", "brain_only_repr_frozen": "E-고정", "brain_only_repr_trained": "E-학습"}
REF = "brain_only"
CK_SEVEN = ("pride", "triumph", "contempt", "disappointment", "sympathy", "guilt", "envy")  # 01 0절. 27개판에서 빼는 7개
HK_SEED = 0


def rank(x):
    return pd.Series(x).rank().to_numpy()


def spearman(a, b):
    return float(np.corrcoef(rank(a), rank(b))[0, 1])


def residual_rank(x, z):
    rx, rz = rank(x), rank(z)
    A = np.column_stack([np.ones_like(rz), rz])
    return rx - A @ np.linalg.lstsq(A, rx, rcond=None)[0]


def perm_spearman(a, b, n, seed, two_sided):
    """정서 이름표를 섞는 순열. a, b는 같은 정서 순서. 돌려주는 값: (ρ, p)."""
    ra, rb = rank(a), rank(b)
    rho = float(np.corrcoef(ra, rb)[0, 1])
    rng = np.random.default_rng(seed)
    null = np.array([np.corrcoef(ra, rb[rng.permutation(len(rb))])[0, 1] for _ in range(n)])
    hit = np.abs(null) >= abs(rho) if two_sided else null >= rho
    return rho, float((1 + hit.sum()) / (1 + n))


def hk_part(s6_dir, split, y, n_boot):
    """HK seed 0 예측. 돌려주는 값: 모델 -> (점 추정 34, bootstrap (B, 34)) 5명 평균, 참가자별 r 표."""
    found = PF.find_predictions(s6_dir)
    plan_rows = {k: PF.plan_test_rows(s6_dir, k) for k in range(1, PF.N_FOLDS + 1)}
    data = {}
    for cond in MODELS:
        f = found[(found.condition == cond) & (found.seed == HK_SEED) & (found.status == "ok")]
        if sorted(f.fold.tolist()) != list(range(1, PF.N_FOLDS + 1)):
            raise SystemExit(f"{cond}: seed {HK_SEED}의 6 fold 예측이 다 있지 않다")
        data[cond] = PF.load_condition(dict(zip(f.fold.astype(int), f.path)), split, plan_rows, y.shape[1])
    videos = PF.same_rows(data)
    pids = sorted(videos)
    U = np.array(sorted(set().union(*[set(v.tolist()) for v in videos.values()])), np.int64)
    sp = split.set_index("video_id").loc[U]
    split_pos = {v: i for i, v in enumerate(split.video_id.tolist())}
    yU = np.asarray(y, np.float64)[[split_pos[v] for v in U]]
    pos = {q: np.searchsorted(U, videos[q]) for q in pids}
    codes, n_units = st.unit_codes(sp.canonical_id.to_numpy())
    W = st.bootstrap_counts(n_units, n_boot, np.random.default_rng(BOOT_SEED))
    point, boot, rows = {}, {}, []
    for q in pids:
        yq = yU[pos[q]]
        rb = st.boot_r(W[:, codes[pos[q]]], yq, {cond: data[cond][q][1] for cond in MODELS})
        for cond in MODELS:
            r = st.pearson_columns(yq, data[cond][q][1])
            point.setdefault(cond, []).append(r)
            boot.setdefault(cond, []).append(rb[cond])
            rows += [dict(dataset="HK", participant=q, model=MODELS[cond], emotion_index=e, r=float(r[e])) for e in range(len(r))]
    out = {cond: (PF.nanmean0(np.stack(point[cond])), PF.nanmean0(np.stack(boot[cond]))) for cond in MODELS}
    return out, rows, dict(participants=pids, n_videos_union=len(U), n_bootstrap_units=n_units)


def mc_part(mc_dir, n_boot):
    """MC 6-3 예측. 돌려주는 값: 모델 -> (점 추정 34, bootstrap (B, 34)) 6명 평균(seed 3개의 r 평균), 참가자별 r 표."""
    units, _, missing = MC.load_units(mc_dir, False)
    if missing:
        raise SystemExit(f"MC 예측이 빠졌다: {missing}")
    W = st.bootstrap_counts(72, n_boot, np.random.default_rng(BOOT_SEED))
    point, boot, rows = {}, {}, []
    vid0 = None
    for cond in MC.MODELS:
        for q in MC.MC_PIDS:
            rs, bs = [], []
            for seed in MC.SEEDS:
                u = units[cond, seed, q]
                if vid0 is None:
                    vid0 = u["video_id"]
                if not np.array_equal(u["video_id"], vid0):
                    raise ValueError("MC 시험 영상 순서가 다르다")
                rs.append(st.pearson_columns(u["y"], u["p"]))
                bs.append(st.boot_r(W, u["y"], {"p": u["p"]})["p"])
            r = PF.nanmean0(np.stack(rs))
            point.setdefault(cond, []).append(r)
            boot.setdefault(cond, []).append(PF.nanmean0(np.stack(bs)))
            rows += [dict(dataset="MC", participant=q, model=MODELS[cond], emotion_index=e, r=float(r[e])) for e in range(len(r))]
    return {cond: (PF.nanmean0(np.stack(point[cond])), PF.nanmean0(np.stack(boot[cond]))) for cond in MC.MODELS}, rows


def differences(dataset, res, emotions, ck):
    rows = []
    r0, b0 = res[REF]
    for cond, (r, b) in res.items():
        if cond == REF:
            continue
        d, db = r - r0, b - b0
        lo, hi = st.basic_ci(d, db)
        p = st.centered_p(d, db)
        q = st.bh(p)
        rows += [dict(dataset=dataset, comparison=f"{MODELS[cond]} − A-1", model=MODELS[cond], emotion=emotions[e], ck27=bool(ck[e]), r_model=float(r[e]), r_A1=float(r0[e]),
                      diff=float(d[e]), ci_low=float(lo[e]), ci_high=float(hi[e]), p=float(p[e]), q_bh=float(q[e]), label="탐색(BH-FDR, 비교마다 34개)") for e in range(len(emotions))]
    return rows


def run(s6_dir, mc_dir, vc_path, out, n_boot, n_perm):
    split = c.load_split()
    y, cols = c.load_scores(split, "emotions")
    lm = pd.read_csv(c.LABEL_MAP, sep="\t")
    emotions = lm.set_index("score_col").loc[cols, "name"].tolist()
    if emotions != lm.name.tolist():
        raise ValueError("정서 순서가 label map과 다르다(MC 예측은 label map 순서다)")
    missing_ck = set(CK_SEVEN) - set(emotions)
    if missing_ck:
        raise ValueError(f"정서 이름에 없는 7개 항목: {missing_ck}")
    ck = np.array([e in CK_SEVEN for e in emotions])
    hk, hk_rows, hk_info = hk_part(s6_dir, split, y, n_boot)
    mc, mc_rows = mc_part(mc_dir, n_boot)
    diff = pd.DataFrame(differences("HK", hk, emotions, ck) + differences("MC", mc, emotions, ck))

    per = pd.DataFrame(hk_rows + mc_rows)
    per["emotion"] = [emotions[i] for i in per.emotion_index]
    mean_rows = [dict(dataset=ds, participant="mean", model=MODELS[cond], emotion_index=e, r=float(res[cond][0][e]), emotion=emotions[e])
                 for ds, res in (("HK", hk), ("MC", mc)) for cond in res for e in range(len(emotions))]
    per = pd.concat([per, pd.DataFrame(mean_rows)], ignore_index=True)
    per["ck27"] = per.emotion.isin(CK_SEVEN)

    counts = (diff.assign(up=(diff.q_bh < .05) & (diff["diff"] > 0), down=(diff.q_bh < .05) & (diff["diff"] < 0))
              .groupby(["dataset", "comparison"], as_index=False)
              .agg(n_emotions=("diff", lambda s: int(np.isfinite(s).sum())), mean_diff=("diff", "mean"), n_up_q05=("up", "sum"), n_down_q05=("down", "sum")))
    counts["up_emotions"] = [", ".join(diff[(diff.dataset == r.dataset) & (diff.comparison == r.comparison) & (diff.q_bh < .05) & (diff["diff"] > 0)].emotion) for r in counts.itertuples()]
    counts["down_emotions"] = [", ".join(diff[(diff.dataset == r.dataset) & (diff.comparison == r.comparison) & (diff.q_bh < .05) & (diff["diff"] < 0)].emotion) for r in counts.itertuples()]

    # Q1. C-1 − A-1의 정서별 양상이 HK와 MC에서 재현되는가
    dh = hk["brain_decoded"][0] - hk[REF][0]
    dm = mc["brain_decoded"][0] - mc[REF][0]
    ok = np.isfinite(dh) & np.isfinite(dm)
    rho, p = perm_spearman(dh[ok], dm[ok], n_perm, PERM_SEED, two_sided=False)
    rep = [dict(question="Q1", statistic="Spearman ρ(HK Δ, MC Δ), C-1 − A-1", n_emotions=int(ok.sum()), rho=rho, p_one_sided=p,
                decision="재현됨" if (rho > 0 and p < .05) else "재현되지 않음", rule="ρ > 0이고 순열 p < .05")]
    for ds, d, r0 in (("HK", dh, hk[REF][0]), ("MC", dm, mc[REF][0])):
        rep.append(dict(question="Q1 기록", statistic=f"{ds}: Spearman ρ(Δ, A-1 r)", n_emotions=int(ok.sum()), rho=spearman(d[ok], r0[ok]), p_one_sided=np.nan, decision="", rule="판정에 쓰지 않음"))
    pr = float(np.corrcoef(residual_rank(dh[ok], hk[REF][0][ok]), residual_rank(dm[ok], mc[REF][0][ok]))[0, 1])
    rep.append(dict(question="Q1 기록", statistic="A-1 r 순위를 통제한 편상관(HK Δ, MC Δ)", n_emotions=int(ok.sum()), rho=pr, p_one_sided=np.nan, decision="", rule="판정에 쓰지 않음"))

    # Q3. Vision 대 Caption 지수와 Δ
    vc = pd.read_csv(vc_path, sep="\t").set_index("emotion").loc[emotions, "vision_over_caption"].to_numpy(np.float64)
    vrows = []
    for ds, res in (("HK", hk), ("MC", mc)):
        for cond in res:
            if cond == REF:
                continue
            d = res[cond][0] - res[REF][0]
            m = np.isfinite(d) & np.isfinite(vc)
            rho_v, p_v = perm_spearman(vc[m], d[m], n_perm, PERM_SEED, two_sided=True)
            vrows.append(dict(question="Q3", dataset=ds, comparison=f"{MODELS[cond]} − A-1", n_emotions=int(m.sum()), rho=rho_v, p_two_sided=p_v, label="탐색, 보정 없음, 방향 없음"))

    o = Path(out)
    o.mkdir(parents=True, exist_ok=True)
    per.drop(columns="emotion_index").to_csv(o / "per_emotion.tsv", sep="\t", index=False)
    diff.to_csv(o / "differences.tsv", sep="\t", index=False)
    counts.to_csv(o / "counts.tsv", sep="\t", index=False)
    pd.DataFrame(rep).to_csv(o / "replication.tsv", sep="\t", index=False)
    pd.DataFrame(vrows).to_csv(o / "vc_index.tsv", sep="\t", index=False)
    return dict(hk=hk_info, n_boot=n_boot, n_perm=n_perm, boot_seed=BOOT_SEED, perm_seed=PERM_SEED, models=MODELS, hk_seed=HK_SEED, mc_seeds=list(MC.SEEDS))


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 정서별 모델 비교")
    ap.add_argument("--s6-dir", required=True)
    ap.add_argument("--mc-dir", required=True)
    ap.add_argument("--vc-index", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", required=True)
    ap.add_argument("--n-boot", type=int, default=st.N_RESAMPLE)
    ap.add_argument("--n-perm", type=int, default=st.N_RESAMPLE)
    a = ap.parse_args(argv)
    c.guard(a.design_freeze)
    started = time.time()
    info = run(a.s6_dir, a.mc_dir, a.vc_index, a.out, a.n_boot, a.n_perm)
    info.update(stage="S10 정서별 모델 비교", s6_dir=str(a.s6_dir), mc_dir=str(a.mc_dir), vc_index=str(a.vc_index), vc_index_sha256=c.sha256(Path(a.vc_index)),
                design_freeze=a.design_freeze, code_commit=c.START_HEAD, code_dirty=c.START_DIRTY, elapsed_seconds=round(time.time() - started, 1))
    (Path(a.out) / "run_info.json").write_text(json.dumps(info, indent=1, ensure_ascii=False))
    print(f"끝: {info['elapsed_seconds']}초", flush=True)


if __name__ == "__main__":
    main()
