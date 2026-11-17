#!/usr/bin/env python3
"""S10 2-1 feature decoding 대 순열 기준 (04 S10의 [사전] 2개, 01 6-1 2-1행, O4 (1), (6), O19, O20, O21, I5, 2026-11-15). GPU 없음.

입력
- S5 ridge decoding(s5_decoding.py): <S5 폴더>/sub-0X_fold<k>/test_pred.npz. 층별 예측(원래 척도)을 이어 붙여 Vision feature(V-JEPA 2 block 10, 20, 30, 40, 5,632차원)와
  Caption feature(DeBERTa 층 6, 12, 18, 24, 4,096차원)를 만든다(O21. 04 기록 칸 S5가 이어 붙이기를 S9에 맡겼으나 S9에 없어 여기서 한다).
  예측 영상은 참가자의 개발 block 영상(S2 participant_blocks_hk.tsv) 가운데 그 fold의 영상과 같아야 한다.
- 실제 특징은 S3 target 파일(s10_inputs.actual_features). 개발 영상만 읽는다.
- (선택) --s6-dir: C-1 Brain + Decoded Feature → Emotion의 decoded features(outputs/decoded_test.npz). 6-1 2-1행의 "같은 지표로 보고"이고 [사전]이 아니라 순열 p를 내지 않는다.
계산(s10_stats)
- 검정 통계량(O19): 참가자마다 6 fold를 모은 시험 영상에서 차원별 Pearson r의 평균. 특징마다 하나다. 5명 평균은 참가자 값의 평균이다.
- 순열(O4 (1), (6), 04 S10 순열): 실제 특징 벡터를 다른 영상에 다시 배정하고 예측은 그대로 둔다. 같은 시험 fold, 같은 원래 run 안에서만 섞고(1부와 같은 block, 같은 난수 seed),
  5명에 같은 순열을 쓴다. 같은 내용 쌍이 다른 run에 나뉘면 각자 자기 run 안에서 섞는다(--split-content-pairs, 11/15 석진 님). 한쪽 p = (1 + #(귀무 ≥ 관찰)) / (순열 수 + 1).
- 구간: 영상 단위 bootstrap 10,000회(같은 내용 묶음은 함께, 1부와 같은 seed), basic 95%(O4 (3)).
- 영상 식별(O19, 보고만, Holm에 넣지 않음): 같은 fold 안에서 A의 예측과 A의 실제의 r이 다른 영상 B의 실제와의 r보다 크면 1. 눈금은 그 decoder의 학습 자료와 같다.
  ridge는 그 참가자의 D_k 영상(S5 standardize), C-1은 저장된 D9 통계(학습 fold 4개)다. 계산은 s5_collect.identification_scores를 쓴다.
출력(레포 밖 --out): decoding_scores.tsv, prereg_pvalues.tsv([사전] 2개 × 묶음 6개, seed 칸 빈칸), c1_decoding_scores.tsv(--s6-dir), coverage.tsv, arrays.npz(차원별 r), run_info.json
사용: s10_feature_decoding.py --s5-dir <S5 decoding 폴더> --out <출력 폴더> --design-freeze <커밋> [--s6-dir <S6 결과 폴더>] [--n-perm 10000] [--n-boot 10000] [--threads 8] [--partial-check] [--overwrite]
"""
import argparse
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

import s4_common as c
import s10_inputs as I
import s10_performance as perf
import s10_stats as st
from s5_collect import identification_scores

VISION_LAYERS = ("vjepa2_10", "vjepa2_20", "vjepa2_30", "vjepa2_40")  # O21
CAPTION_LAYERS = ("deberta_06", "deberta_12", "deberta_18", "deberta_24")
TESTS = {"vision": "2-1 Vision feature", "caption": "2-1 Caption feature"}  # s10_stats.PREREG_15의 이름
BOOT_CHUNK, PERM_CHUNK = 500, 100
N_FOLDS = I.N_FOLDS


def feature_slices():
    a = I.DIMS["vision"]
    return {"vision": slice(0, a), "caption": slice(a, a + I.DIMS["caption"])}


def load_s5(s5_dir, split, pvideos, pids):
    """참가자마다 6 fold의 ridge 예측. 돌려주는 값: 참가자 -> (영상 번호, 이어 붙인 예측 (영상, 9,728)), 기록 표, 빠진 목록."""
    fold_of = dict(zip(split.video_id.astype(int), split.fold.astype(int)))
    out, rows, missing = {}, [], []
    for q in pids:
        parts = []
        for k in range(1, N_FOLDS + 1):
            d = Path(s5_dir) / f"{q}_fold{k}"
            path = d / "test_pred.npz"
            if not (path.exists() and (d / "done.json").exists()):
                missing.append(dict(participant=q, fold=k, path=str(path)))
                rows.append(dict(participant=q, fold=k, path=str(path), status="없음", n_videos=0))
                continue
            z = np.load(path)
            vid = z["video_id"].astype(np.int64)
            want = sorted(v for v in pvideos[q] if fold_of[int(v)] == k)
            if len(set(vid.tolist())) != len(vid) or sorted(vid.tolist()) != want:
                raise ValueError(f"{path}: 시험 영상이 그 참가자의 fold {k} block 영상과 다르다")
            x = np.concatenate([np.asarray(z[n], np.float64) for n in VISION_LAYERS + CAPTION_LAYERS], 1)
            if x.shape != (len(vid), I.DIMS["vision"] + I.DIMS["caption"]) or not np.isfinite(x).all():
                raise ValueError(f"{path}: 이어 붙인 예측의 크기 {x.shape}가 다르거나 NaN이 있다")
            parts.append((vid, x))
            rows.append(dict(participant=q, fold=k, path=str(path), status="ok", n_videos=len(vid)))
        if parts:
            v = np.concatenate([a for a, _ in parts])
            x = np.concatenate([b for _, b in parts])
            o = np.argsort(v)
            out[q] = (v[o], x[o])
    return out, pd.DataFrame(rows), missing


def group_means(r, slices):
    """(…, 9,728) 차원별 r -> 특징마다 평균. 재표집 한 번의 NaN 차원은 그 재표집에서만 뺀다."""
    return {name: st.mean_over(r[..., sl], np.ones(sl.stop - sl.start, bool)) for name, sl in slices.items()}


def boot_means(W, codes_q, f_q, p_q, slices):
    """영상 단위 bootstrap의 특징별 차원 r 평균. 돌려주는 값: 특징 -> (B,)."""
    out = {name: [] for name in slices}
    for i in range(0, len(W), BOOT_CHUNK):
        r = st.boot_r(W[i:i + BOOT_CHUNK][:, codes_q], f_q, {"p": p_q})["p"]
        for name, v in group_means(r, slices).items():
            out[name].append(v)
    return {name: np.concatenate(v) for name, v in out.items()}


def perm_means(perm, pos, f_all, p_q, slices, threads):
    """순열 귀무의 특징별 차원 r 평균. 순열 묶음을 thread로 나눠 낸다(einsum은 GIL을 풀어 준다). 돌려주는 값: 특징 -> (순열 수,)."""
    chunks = [perm[i:i + PERM_CHUNK] for i in range(0, len(perm), PERM_CHUNK)]
    with ThreadPoolExecutor(max(1, threads)) as ex:
        res = list(ex.map(lambda ch: group_means(st.permuted_feature_r(ch, pos, f_all, p_q), slices), chunks))
    return {name: np.concatenate([r[name] for r in res]) for name in slices}


def identification_ridge(q, vids, pred, fcat, upos, split, pvideos, slices):
    """ridge 영상 식별(O19). 눈금은 그 참가자의 D_k 영상의 실제 특징 평균과 표준편차(S5 standardize와 같다). 돌려주는 값: 특징 -> 정확도."""
    fold_of = dict(zip(split.video_id.astype(int), split.fold.astype(int)))
    fv = np.array([fold_of[int(v)] for v in vids])
    allv = np.asarray(pvideos[q])
    allf = np.array([fold_of[int(v)] for v in allv])
    scores = {name: [] for name in slices}
    for k in np.unique(fv):
        dk = fcat[[upos[int(v)] for v in allv[allf != k]]]
        at = fv == k
        true = fcat[[upos[int(v)] for v in vids[at]]]
        for name, sl in slices.items():
            m, s = dk[:, sl].mean(0), dk[:, sl].std(0)
            if (s <= 0).any():
                raise ValueError(f"{q} fold {k}: D_k에서 표준편차가 0인 {name} 차원이 있어 식별 눈금을 낼 수 없다")
            scores[name].append(identification_scores((pred[at][:, sl] - m) / s, (true[:, sl] - m) / s))
    return {name: float(np.concatenate(v).mean()) for name, v in scores.items()}


def load_c1(s6_dir, pids):
    """C-1 decoded features(seed마다 6 fold). 돌려주는 값: seed -> 참가자 -> (영상 번호, 이어 붙인 원래 척도 값, fold 번호, D9 평균, D9 표준편차), 빠진 목록."""
    by_seed, missing = {}, []
    stats = {}
    for k in range(1, N_FOLDS + 1):
        plan = Path(s6_dir) / f"outer_fold{k}"
        seeds = I.selected_seeds(plan, "brain_decoded") if plan.is_dir() else None
        if not seeds:
            missing.append(dict(source="C-1", fold=k, seed="", path=str(plan / "brain_decoded" / "selected.json")))
            continue
        want = I.plan_test_rows(plan)
        s = np.load(plan / "plan" / "standardization.npz")
        stats[k] = (np.concatenate([s["visual_mean"], s["caption_mean"]]), np.concatenate([s["visual_std"], s["caption_std"]]))
        for seed, d in seeds.items():
            if not (d / "outputs" / "decoded_test.npz").exists():
                missing.append(dict(source="C-1", fold=k, seed=seed, path=str(d / "outputs" / "decoded_test.npz")))
                continue
            for q, (v, vis, cap) in I.load_decoded(d, plan, want).items():
                by_seed.setdefault(seed, {}).setdefault(q, []).append((v, np.concatenate([vis, cap], 1), np.full(len(v), k)))
    out = {}
    for seed, by_q in by_seed.items():
        for q, items in by_q.items():
            if len(items) != N_FOLDS:
                missing.append(dict(source="C-1", fold="", seed=seed, path=f"{q}: fold {len(items)}개"))
                continue
            v = np.concatenate([a for a, _, _ in items])
            o = np.argsort(v)
            out.setdefault(seed, {})[q] = (v[o], np.concatenate([b for _, b, _ in items])[o], np.concatenate([f for _, _, f in items])[o])
    return out, stats, missing


def run(s5_dir, out, split, *, s6_dir=None, n_perm=st.N_RESAMPLE, n_boot=st.N_RESAMPLE, split_pairs=True, threads=8, partial_check=False, overwrite=False, extra_info=None, pvideos=None):
    started = time.time()
    out = I.prepare_out(out, overwrite)
    pvideos = I.participant_videos(split) if pvideos is None else pvideos
    pids = [q for q in I.HK_PIDS if q in pvideos]
    preds, coverage, missing = load_s5(s5_dir, split, pvideos, pids)
    c1, c1_stats, c1_missing = load_c1(s6_dir, pids) if s6_dir else ({}, {}, [])
    I.require_complete(missing + c1_missing, partial_check, "2-1")
    if not preds:
        raise SystemExit("읽은 S5 예측이 없다")
    pids = sorted(preds)
    slices = feature_slices()
    U = np.array(sorted(set().union(*[set(v.tolist()) for v, _ in preds.values()], *[set(v.tolist()) for by in c1.values() for v, _, _ in by.values()])), np.int64)
    feats = I.actual_features(split, U)
    fcat = np.concatenate([feats["vision"], feats["caption"]], 1).astype(np.float64)
    upos = {int(v): i for i, v in enumerate(U)}
    sp = split.set_index("video_id").loc[U]
    codes, n_units = st.unit_codes(sp.canonical_id.to_numpy())
    W = st.bootstrap_counts(n_units, n_boot, np.random.default_rng(perf.BOOT_SEED))  # 1부와 같은 seed
    blocks = np.array([f"fold{f}_run{r}" for f, r in zip(sp.fold.to_numpy(), sp.run_index.to_numpy())])
    split_groups = st.check_content_units(blocks, sp.canonical_id.to_numpy(), split_pairs)
    perm = st.block_permutations(blocks, n_perm, np.random.default_rng(perf.PERM_SEED)) if n_perm > 0 else np.empty((0, len(U)), np.int32)

    obs, boot, null, ident, ndim_nan, arrays = {}, {}, {}, {}, {}, {}
    for q in pids:
        v, p = preds[q]
        pos = np.array([upos[int(x)] for x in v])
        f_q = fcat[pos]
        r = st.pearson_columns(f_q, p)
        arrays[f"ridge_r:{q}"] = r.astype(np.float32)
        for name, sl in slices.items():
            ok = np.isfinite(r[sl])
            obs[q, name] = float(r[sl][ok].mean())
            ndim_nan[q, name] = int((~ok).sum())
        bm = boot_means(W, codes[pos], f_q, p, slices)
        nm = perm_means(perm, pos, fcat, p, slices, threads) if n_perm > 0 else {name: np.full(0, np.nan) for name in slices}
        for name in slices:
            boot[q, name], null[q, name] = bm[name], nm[name]
        ident[q] = identification_ridge(q, v, p, fcat, upos, split, pvideos, slices)
        print(f"2-1 ridge {q} 끝 ({time.time() - started:.0f}초)", flush=True)

    rows, pre = [], []
    for name in slices:
        obs["mean5", name] = float(np.mean([obs[q, name] for q in pids]))
        boot["mean5", name] = np.mean(np.stack([boot[q, name] for q in pids]), 0)
        null["mean5", name] = np.mean(np.stack([null[q, name] for q in pids]), 0) if n_perm > 0 else np.full(0, np.nan)
        for q in pids + ["mean5"]:
            lo, hi = I.ci_row(obs[q, name], boot[q, name])
            nl = null[q, name]
            p = float(st.permutation_p(obs[q, name], nl)) if n_perm > 0 else np.nan
            rows.append(dict(source="ridge(S5)", feature=name, participant=q, mean_dim_r=obs[q, name], ci_low=lo, ci_high=hi,
                             n_dims=slices[name].stop - slices[name].start, n_dims_noncomputable=ndim_nan.get((q, name), np.nan),
                             null_mean=float(np.nanmean(nl)) if len(nl) else np.nan, null_q95=float(np.nanquantile(nl, 0.95)) if len(nl) else np.nan,
                             p_perm=p, n_perm_valid=int(np.isfinite(nl).sum()), n_boot_valid=int(np.isfinite(boot[q, name]).sum()),
                             identification=ident[q][name] if q != "mean5" else float(np.mean([ident[x][name] for x in pids])),
                             n_videos=len(preds[q][0]) if q != "mean5" else np.nan))
            if n_perm > 0:
                pre.append(dict(test_id=TESTS[name], family=q, seed="", estimate=obs[q, name], p_raw=p, statistic="차원별 r 평균(O19), 순열 기준과 비교한 한쪽 p", source="s10_feature_decoding", analysis="all"))
    tables = {"decoding_scores": pd.DataFrame(rows), "prereg_pvalues": pd.DataFrame(pre, columns=["test_id", "family", "seed", "estimate", "p_raw", "statistic", "source", "analysis"]),
              "coverage": coverage}

    if c1:  # 6-1 2-1행. C-1 decoded features를 같은 지표로 보고한다(순열 p 없음)
        crow = []
        for seed, by_q in sorted(c1.items()):
            cobs, cboot = {}, {}
            for q, (v, x, fk) in sorted(by_q.items()):
                pos = np.array([upos[int(t)] for t in v])
                f_q = fcat[pos]
                r = st.pearson_columns(f_q, x)
                arrays[f"c1_r:seed{seed}:{q}"] = r.astype(np.float32)
                bm = boot_means(W, codes[pos], f_q, x, slices)
                idn = {name: [] for name in slices}
                for k in np.unique(fk):
                    m, s = c1_stats[int(k)]
                    at = fk == k
                    for name, sl in slices.items():
                        idn[name].append(identification_scores((x[at][:, sl] - m[sl]) / s[sl], (f_q[at][:, sl] - m[sl]) / s[sl]))
                for name, sl in slices.items():
                    ok = np.isfinite(r[sl])
                    cobs[q, name], cboot[q, name] = float(r[sl][ok].mean()), bm[name]
                    lo, hi = I.ci_row(cobs[q, name], bm[name])
                    crow.append(dict(source="C-1 decoded features", seed=seed, feature=name, participant=q, mean_dim_r=cobs[q, name], ci_low=lo, ci_high=hi,
                                     n_dims_noncomputable=int((~ok).sum()), identification=float(np.concatenate(idn[name]).mean()), n_videos=len(v)))
            qs = sorted(by_q)
            for name in slices:
                m5, b5 = float(np.mean([cobs[q, name] for q in qs])), np.mean(np.stack([cboot[q, name] for q in qs]), 0)
                lo, hi = I.ci_row(m5, b5)
                crow.append(dict(source="C-1 decoded features", seed=seed, feature=name, participant="mean5", mean_dim_r=m5, ci_low=lo, ci_high=hi,
                                 identification=float(np.mean([r["identification"] for r in crow if r["seed"] == seed and r["feature"] == name and r["participant"] != "mean5"]))))
        ct = pd.DataFrame(crow)
        tables["c1_decoding_scores"] = ct
        tables["c1_seed_summary"] = st.seed_summary(ct, ["feature", "participant"], ["mean_dim_r", "identification"])
    if missing or c1_missing:
        tables["missing"] = pd.DataFrame(missing + c1_missing)
    info = dict(stage="S10 2-1 feature decoding", s5_dir=str(s5_dir), s6_dir=str(s6_dir) if s6_dir else None, participants=pids, n_videos_union=len(U),
                settings=dict(n_perm=n_perm, n_boot=n_boot, boot_seed=perf.BOOT_SEED, perm_seed=perf.PERM_SEED, split_content_pairs=split_pairs, bootstrap_unit="video",
                              vision_layers=VISION_LAYERS, caption_layers=CAPTION_LAYERS), n_exchange_blocks=int(len(np.unique(blocks))),
                content_groups_split_across_runs=split_groups.to_dict("records"), partial_check=bool(missing or c1_missing), **(extra_info or {}))
    if missing or c1_missing:
        info["note"] = I.PARTIAL_NOTE
    if n_perm != st.N_RESAMPLE or n_boot != st.N_RESAMPLE:
        info["note_resample"] = f"재표집 횟수가 I5의 {st.N_RESAMPLE}회와 다르다. 점검용 실행이다"
    return I.write_out(out, tables, info, started, arrays)


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 2-1 feature decoding 대 순열 기준")
    ap.add_argument("--s5-dir", required=True, help="S5 decoding 폴더(<output_root>/s5_ridge/decoding)")
    ap.add_argument("--s6-dir", default=None, help="C-1 decoded features를 함께 낼 S6 결과 폴더(선택)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", required=True)
    ap.add_argument("--split-content-pairs", action=argparse.BooleanOptionalAction, default=True, help="같은 내용 쌍이 다른 run에 있으면 각자 자기 run 안에서 섞는다(11/15 석진 님)")
    ap.add_argument("--n-perm", type=int, default=st.N_RESAMPLE)
    ap.add_argument("--n-boot", type=int, default=st.N_RESAMPLE)
    ap.add_argument("--threads", type=int, default=8, help="순열 계산 thread 수(결과는 같다)")
    ap.add_argument("--partial-check", action="store_true", help="빠진 입력이 있어도 읽기와 행 대조만 점검한다. 결과로 쓰지 않는다")
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args(argv)
    c.guard(a.design_freeze)
    split = c.load_split()
    info = run(a.s5_dir, a.out, split, s6_dir=a.s6_dir, n_perm=a.n_perm, n_boot=a.n_boot, split_pairs=a.split_content_pairs, threads=a.threads,
               partial_check=a.partial_check, overwrite=a.overwrite, extra_info=dict(design_freeze=a.design_freeze))
    print(f"끝: {a.out} ({info['elapsed_seconds']}초)")


if __name__ == "__main__":
    main()
