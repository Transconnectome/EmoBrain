#!/usr/bin/env python3
"""S10 6-4a 묶음만으로 학습한 모델과 1-3 [사전] 세 검정 (04 S10 영역, 01 6-4a, 1-3, 6-1 1-3행, O4 (1), (6), 2026-11-15). GPU 없음.

입력: S6 작업 목록(scripts/s6_queue.py의 TSV, 열 name, plan, conditions, config, s6_out, est_hours)의 net_<묶음>_f<k> 작업. 묶음마다 결과 폴더(s6_out)가 하나이고
  S6 꼴(outer_fold<k>/<조건>/selected.json, outer_fold<k>/plan)이다. 묶음 이름은 S2 cabnp_groups.tsv의 13개와 같아야 한다.
- 묶음마다 A-1, C-1의 seed 0이 6 fold 모두 있어야 최종 표를 낸다(01 11/15: 6-4a는 seed 0만). 빠지면 목록을 적고 멈춘다(--partial-check는 점검용).
- 읽기와 행 대조는 s10_performance의 함수(find_predictions, coverage_table, plan_test_rows, load_condition, same_rows)를 쓴다(N11).
계산
- 평가 정서는 34개 모두이고, 시험 영상 전체에서 사람 평정이나 예측이 상수라 r을 계산할 수 없는 정서만 빼고 그 수를 센다(6-4a, 2-6).
- 묶음마다, 모델마다 참가자별 정서별 r(6 fold를 모음), 참가자 점수(계산할 수 있는 정서의 r 평균), 5명 평균. 영상 단위 bootstrap 구간(1부와 같은 seed와 단위).
- 순열 기준(O4 (1), (6)): 1부와 같은 block(같은 시험 fold, 같은 원래 run), 같은 순열 seed, 5명 공통. 한쪽 p.
  1-3 [사전]: A-1의 Visual1, Visual2, Default 점수 대 순열 기준(prereg_pvalues.tsv, s10_holm15.py로 넘김).
  나머지(A-1의 다른 10묶음, C-1의 13묶음)는 탐색이고 BH-FDR이다. 그 묶음 구성은 문서가 정하지 않아(01 6-4 "참가자, 묶음, 비교마다 34개 정서 등")
  --network-bh-family로 받고 기본값이 없다. by_model: 모델마다(A-1 10개, C-1 13개), pooled: 23개 함께. 둘 다 참가자마다(5명 평균 따로), seed마다.
  묶음 안 정서별 순열 p는 탐색이고 BH 묶음은 참가자, 묶음, 모델마다 34개 정서다.
- C-1의 decoded features(Vision, Caption)는 2-1의 지표(차원별 r 평균, 원래 척도로 되돌려 6 fold를 모음, O20)로 낸다. 관찰 값만 낸다.
- 13묶음의 참가자 간 일치도(S2 agreement_hk_13groups.tsv)를 붙인다.
출력(레포 밖 --out): network_scores.tsv, network_per_emotion.tsv, network_decoding.tsv, prereg_pvalues.tsv, coverage.tsv, run_info.json
사용: s10_network.py --jobs <작업 TSV> --out <출력 폴더> --design-freeze <커밋> --network-bh-family by_model|pooled [--n-boot 10000] [--n-perm 10000] [--partial-check] [--overwrite]
"""
import argparse
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd

import s4_common as c
import s10_inputs as I
import s10_performance as perf
import s10_stats as st

MODELS = ("brain_only", "brain_decoded")
SHORT = {"brain_only": "A-1", "brain_decoded": "C-1"}
PREREG = {"Visual1": "1-3 Visual1", "Visual2": "1-3 Visual2", "Default": "1-3 Default"}  # 01 1-3. A-1만
BH_FAMILIES = ("by_model", "pooled")
REQUIRED_SEED = 0  # 01 11/15. 6-4a는 seed 0만


def network_dirs(jobs_path, groups):
    """작업 목록에서 묶음 -> 결과 폴더."""
    t = pd.read_csv(jobs_path, sep="\t", dtype=str)
    t = t[t.name.str.startswith("net_")]
    out = {}
    for r in t.itertuples(index=False):
        m = re.fullmatch(r"net_(.+)_f(\d+)", r.name)
        if not m or r.plan != f"outer_fold{m.group(2)}":
            raise SystemExit(f"{r.name}: 작업 이름과 분할이 net_<묶음>_f<k>, outer_fold<k>가 아니다")
        if set(r.conditions.split(",")) != set(MODELS):
            raise SystemExit(f"{r.name}: 조건이 A-1, C-1이 아니다")
        if out.setdefault(m.group(1), r.s6_out) != r.s6_out:
            raise SystemExit(f"{m.group(1)}: 결과 폴더가 둘 이상이다")
    if set(out) != set(groups):
        raise SystemExit(f"작업 목록의 묶음 {sorted(out)}이 S2 cabnp_groups.tsv의 13개와 다르다")
    return out


def load_network(d, split, n_emo):
    """한 묶음 폴더. 돌려주는 값: data((조건, seed) -> 참가자 -> p), videos, coverage, 빠진 목록, (조건, seed) -> fold -> seed 폴더."""
    found = perf.find_predictions(d) if Path(d).is_dir() else pd.DataFrame(columns=["condition", "fold", "seed", "rel", "zero_selected", "path", "status"])
    cov, usable = perf.coverage_table(found) if len(found) else (pd.DataFrame(), [])
    usable = [(a, s) for a, s in usable if a in MODELS]
    missing = [dict(condition=m, seed=REQUIRED_SEED) for m in MODELS if (m, REQUIRED_SEED) not in usable]
    if not usable:
        return None, None, cov, missing, {}
    plan_rows = {k: perf.plan_test_rows(d, k) for k in range(1, I.N_FOLDS + 1)}
    loaded, seed_dirs = {}, {}
    for cond, seed in usable:
        f = found[(found.condition == cond) & (found.seed == seed)]
        loaded[cond, seed] = perf.load_condition(dict(zip(f.fold.astype(int), f.path)), split, plan_rows, n_emo)
        seed_dirs[cond, seed] = {int(k): Path(d) / f"outer_fold{int(k)}" / rel for k, rel in zip(f.fold, f.rel)}
    videos = perf.same_rows(loaded)
    data = {key: {q: p for q, (_, p) in by.items()} for key, by in loaded.items()}
    return data, videos, cov, missing, seed_dirs


def analyze(name, data, videos, split, y_split, emotions, W, codes_all, perm, upos_all):
    """한 묶음. 돌려주는 값: 점수 행, 정서별 행."""
    pids = sorted(videos)
    ypos = {v: i for i, v in enumerate(split.video_id.astype(int).tolist())}
    U = np.array(sorted(upos_all), np.int64)
    yU = np.asarray(y_split, np.float64)[[ypos[int(v)] for v in U]]
    pos = {q: np.array([upos_all[int(v)] for v in videos[q]]) for q in pids}
    keys = sorted(data)
    score, sboot, snull, rr, rnull, keep = {}, {}, {}, {}, {}, {}
    for q in pids:
        yq = yU[pos[q]]
        rb = st.boot_r(W[:, codes_all[pos[q]]], yq, {k: data[k][q] for k in keys})
        rn = {k: [] for k in keys}
        for i in range(0, len(perm), perf.PERM_CHUNK):
            res = st.permuted_r(perm[i:i + perf.PERM_CHUNK], pos[q], yU, {k: data[k][q] for k in keys})
            for k in keys:
                rn[k].append(res[k])
        for k in keys:
            r = st.pearson_columns(yq, data[k][q])
            kp = np.isfinite(r)
            rr[k, q], keep[k, q] = r, kp
            score[k, q] = float(r[kp].mean()) if kp.any() else np.nan
            sboot[k, q] = st.mean_over(rb[k], kp)
            rnull[k, q] = np.concatenate(rn[k]) if rn[k] else np.empty((0, len(emotions)))
            snull[k, q] = st.mean_over(rnull[k, q], kp)
    rows, emo = [], []
    for k in keys:
        cond, seed = k
        score[k, "mean5"] = float(np.mean([score[k, q] for q in pids]))
        sboot[k, "mean5"] = np.mean(np.stack([sboot[k, q] for q in pids]), 0)
        snull[k, "mean5"] = np.mean(np.stack([snull[k, q] for q in pids]), 0)
        for q in pids + ["mean5"]:
            lo, hi = I.ci_row(score[k, q], sboot[k, q])
            nl = snull[k, q]
            rows.append(dict(network=name, model=SHORT[cond], condition=cond, seed=seed, participant=q, score_r=score[k, q], ci_low=lo, ci_high=hi,
                             null_mean=float(np.nanmean(nl)) if len(nl) else np.nan, null_q95=float(np.nanquantile(nl, 0.95)) if len(nl) else np.nan,
                             p_perm=float(st.permutation_p(score[k, q], nl)) if len(nl) else np.nan, n_perm_valid=int(np.isfinite(nl).sum()),
                             n_emotions_used=int(keep[k, q].sum()) if q != "mean5" else np.nan, n_noncomputable=int((~keep[k, q]).sum()) if q != "mean5" else int(sum((~keep[k, x]).sum() for x in pids)),
                             n_videos=len(videos[q]) if q != "mean5" else np.nan))
            r_obs = rr[k, q] if q != "mean5" else perf.nanmean0(np.stack([rr[k, x] for x in pids]))
            nl = rnull[k, q] if q != "mean5" else perf.nanmean0(np.stack([rnull[k, x] for x in pids]))
            ep = st.permutation_p(r_obs, nl) if len(nl) else np.full(len(emotions), np.nan)
            eb = st.bh(ep)
            for e in range(len(emotions)):
                emo.append(dict(network=name, model=SHORT[cond], seed=seed, participant=q, emotion=emotions[e], r=r_obs[e], p_perm=ep[e], p_bh=eb[e], family_size=int(np.isfinite(ep).sum()),
                                label="탐색(BH-FDR, 참가자, 묶음, 모델마다 34개 정서)"))
    return rows, emo


def decoding(name, seed_dirs, split):
    """C-1 decoded features의 2-1 지표(관찰 값)."""
    rows = []
    for (cond, seed), by_fold in sorted(seed_dirs.items()):
        if cond != "brain_decoded":
            continue
        parts = {}
        for k, sd in sorted(by_fold.items()):
            plan = sd.parent.parent
            if not (sd / "outputs" / "decoded_test.npz").exists():
                raise SystemExit(f"{sd}: outputs/decoded_test.npz가 없다")
            for q, item in I.load_decoded(sd, plan, I.plan_test_rows(plan)).items():
                parts.setdefault(q, []).append(item)
        for q, items in sorted(parts.items()):
            v = np.concatenate([a[0] for a in items])
            feats = I.actual_features(split, v)
            for j, fname in enumerate(("vision", "caption")):
                m, nn, _ = I.decoding_scores(feats[fname].astype(np.float64), np.concatenate([a[1 + j] for a in items]))
                rows.append(dict(network=name, model="C-1", seed=seed, participant=q, feature=fname, mean_dim_r=m, n_dims_noncomputable=nn, n_videos=len(v)))
    t = pd.DataFrame(rows)
    if len(t):
        t = pd.concat([t, t.groupby(["network", "model", "seed", "feature"], as_index=False).mean_dim_r.mean().assign(participant="mean5")], ignore_index=True)
    return t


def add_bh(scores, family):
    """탐색 묶음의 BH. 1-3 [사전] 세 행은 넣지 않는다."""
    s = scores.copy()
    s["test_kind"] = np.where((s.model == "A-1") & s.network.isin(list(PREREG)), "[사전] 1-3(Holm 15개)", "탐색")
    s["p_bh"] = np.nan
    s["bh_family"] = ""
    expl = s[s.test_kind == "탐색"]
    if family is None:
        s.loc[expl.index, "bh_family"] = "정하지 않음(--network-bh-family 없음, 점검용)"
        return s
    by = ["seed", "participant"] + (["model"] if family == "by_model" else [])
    for _, g in expl.groupby(by):
        s.loc[g.index, "p_bh"] = st.bh(g.p_perm.to_numpy())
        s.loc[g.index, "bh_family"] = f"{family}: " + ", ".join(f"{b}" for b in by) + f"마다 {len(g)}개"
    return s


def run(jobs, out, split, y, emotions, *, bh_family=None, n_boot=st.N_RESAMPLE, n_perm=st.N_RESAMPLE, split_pairs=True, partial_check=False, overwrite=False, extra_info=None, groups=None, agreement=None):
    started = time.time()
    out = I.prepare_out(out, overwrite)
    if bh_family is not None and bh_family not in BH_FAMILIES:
        raise ValueError(f"--network-bh-family는 {BH_FAMILIES} 가운데 하나다")
    if bh_family is None and not partial_check:
        raise SystemExit(f"탐색 검정의 BH 묶음을 --network-bh-family {BH_FAMILIES}로 정해야 한다(문서가 정하지 않음)")
    groups = pd.read_csv(c.S2 / "cabnp_groups.tsv", sep="\t").group.tolist() if groups is None else groups
    agreement = pd.read_csv(c.S2 / "agreement_hk_13groups.tsv", sep="\t") if agreement is None else agreement
    dirs = network_dirs(jobs, groups)
    loaded, covs, missing = {}, [], []
    for g in groups:
        data, videos, cov, miss, seed_dirs = load_network(dirs[g], split, len(emotions))
        if len(cov):
            covs.append(cov.assign(network=g, s6_out=dirs[g]))
        missing += [dict(network=g, s6_out=dirs[g], **m) for m in miss]
        if data is not None:
            loaded[g] = (data, videos, seed_dirs)
    I.require_complete(missing, partial_check, "6-4a")
    tables = dict(coverage=pd.concat(covs, ignore_index=True) if covs else pd.DataFrame(columns=["network"]))
    if missing:
        tables["missing"] = pd.DataFrame(missing)
    info = dict(stage="S10 6-4a network", jobs=str(jobs), network_dirs=dirs, settings=dict(n_boot=n_boot, n_perm=n_perm, boot_seed=perf.BOOT_SEED, perm_seed=perf.PERM_SEED,
                split_content_pairs=split_pairs, network_bh_family=bh_family), partial_check=bool(missing), n_networks_loaded=len(loaded), **(extra_info or {}))
    if missing:
        info["note"] = I.PARTIAL_NOTE
    if not loaded:
        info["note_empty"] = "읽은 묶음 결과가 없다. 빠진 목록만 쓴다"
        return I.write_out(out, tables, info, started)
    U = np.array(sorted(set().union(*[set(v.tolist()) for _, videos, _ in loaded.values() for v in videos.values()])), np.int64)
    upos = {int(v): i for i, v in enumerate(U)}
    sp = split.set_index("video_id").loc[U]
    codes, n_units = st.unit_codes(sp.canonical_id.to_numpy())
    W = st.bootstrap_counts(n_units, n_boot, np.random.default_rng(perf.BOOT_SEED)).astype(np.float64)
    blocks = np.array([f"fold{f}_run{r}" for f, r in zip(sp.fold.to_numpy(), sp.run_index.to_numpy())])
    split_groups = st.check_content_units(blocks, sp.canonical_id.to_numpy(), split_pairs)
    perm = st.block_permutations(blocks, n_perm, np.random.default_rng(perf.PERM_SEED)) if n_perm > 0 else np.empty((0, len(U)), np.int32)
    rows, emo, dec = [], [], []
    for g, (data, videos, seed_dirs) in loaded.items():
        r, e = analyze(g, data, videos, split, y, emotions, W, codes, perm, upos)
        rows += r
        emo += e
        dec.append(decoding(g, seed_dirs, split))
        print(f"6-4a {g} 끝 ({time.time() - started:.0f}초)", flush=True)
    scores = add_bh(pd.DataFrame(rows), bh_family)
    ag = agreement.rename(columns={"group": "network", "median": "agreement_median", "min": "agreement_min", "max": "agreement_max", "count": "agreement_n_roi"})
    tables["network_scores"] = scores.merge(ag, on="network", how="left")
    tables["network_per_emotion"] = pd.DataFrame(emo)
    tables["network_decoding"] = pd.concat(dec, ignore_index=True) if dec else pd.DataFrame()
    pre = scores[scores.test_kind.str.startswith("[사전]")]
    tables["prereg_pvalues"] = pd.DataFrame(dict(test_id=pre.network.map(PREREG), family=pre.participant, seed=pre.seed, estimate=pre.score_r, p_raw=pre.p_perm,
                                                 statistic="그 묶음만으로 학습한 A-1의 34개 정서 평균 r, 순열 기준과 비교한 한쪽 p", source="s10_network", analysis="all"))
    info.update(n_videos_union=len(U), content_groups_split_across_runs=split_groups.to_dict("records"))
    if n_perm != st.N_RESAMPLE or n_boot != st.N_RESAMPLE:
        info["note_resample"] = f"재표집 횟수가 I5의 {st.N_RESAMPLE}회와 다르다. 점검용 실행이다"
    return I.write_out(out, tables, info, started)


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 6-4a 묶음만으로 학습, 1-3 [사전]")
    ap.add_argument("--jobs", required=True, help="S6 작업 목록 TSV(<output_root>/logs/s6_queue_jobs_<tag>.tsv)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", required=True)
    ap.add_argument("--network-bh-family", choices=BH_FAMILIES, default=None, help="탐색 묶음 검정의 BH 묶음. 문서가 정하지 않아 기본값이 없다")
    ap.add_argument("--split-content-pairs", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument("--n-boot", type=int, default=st.N_RESAMPLE)
    ap.add_argument("--n-perm", type=int, default=st.N_RESAMPLE)
    ap.add_argument("--partial-check", action="store_true")
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args(argv)
    c.guard(a.design_freeze)
    split = c.load_split()
    y, cols = c.load_scores(split, "emotions")
    info = run(a.jobs, a.out, split, np.asarray(y, np.float64), I.emotion_names(cols), bh_family=a.network_bh_family, n_boot=a.n_boot, n_perm=a.n_perm, split_pairs=a.split_content_pairs,
               partial_check=a.partial_check, overwrite=a.overwrite, extra_info=dict(design_freeze=a.design_freeze))
    print(f"끝: {a.out} ({info['elapsed_seconds']}초)")


if __name__ == "__main__":
    main()
