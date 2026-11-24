#!/usr/bin/env python3
"""S10 2-2 바꿔 끼우기, 1-1 정서별 경로 효과, 1-2 (나) 결합 지표 (04 S9, S10, 01 1-3, 4-2, 6-1, O2, O3, O4 (2), (3), O9, 2026-11-15). GPU 없음.

입력: S9 swap 결과(<S9 swap 폴더>/outer_fold<k>_seed<s>/interventions.pt, s9_saved_models.py). 참가자마다 audition_codex.FoldInterventions의 값이다.
- 6 fold가 모두 있어야 seed의 최종 표를 낸다. 빠지면 멈춘다(--partial-check는 점검용).
- 확인: 쌍(A, B)은 S2 pairs_directed.tsv의 그 fold 짝이고, 그 참가자에게 두 영상이 모두 있는 짝은 모두 들어 있다(O9). Δy는 사람 평정의 y_B − y_A와 같다.
  A와 B는 S2 pair_groups.tsv의 같은 짝 연결 묶음에 있다. 관찰 효과는 audition_codex.summarize_interventions와 같아야 한다.
계산(O2, O3)
- 참가자, 정서, 교체 조건(시각만, 캡션만, 둘 다)마다 6 fold의 모든 쌍에 걸친 r(Δp, Δy). 대조 100회는 회마다 r을 낸 뒤 평균한다(예측을 먼저 평균하지 않음). 효과 = 실제 r − 대조 평균 r.
- Δy가 모든 쌍에서 같은 정서(사실상 모두 0)는 빼고 그 수를 센다. 실제나 대조 한 회라도 Δp가 상수인 정서는 효과를 계산할 수 없어 빼고 따로 센다(2-6).
- 2-2([사전] 3개): 경로마다 계산할 수 있는 정서의 효과 평균. 1-1(탐색): 정서마다 시각 효과 − 캡션 효과. 1-2 (나)(탐색): 정서마다 쌍에 걸친 평균 |I| − 대조 100회 평균 |I|.
  I는 logit으로 계산하고(I = z(B, B) − z(A, B) − z(B, A) + z(A, A), 괄호는 (시각 출처, 캡션 출처)), 최종 확률의 같은 값도 따로 낸다(5-0).
- 1-1 보조 비교: Kragel 외(2019)에서 정지 프레임 분류 성능이 높았던 정서(craving, sexual desire, entrancement, horror)와 낮았던 정서(confusion, awe, surprise)의
  두 경로 효과를 묶음마다 평균해 나란히 낸다. 두 묶음 사이의 검정은 문서가 정하지 않아 내지 않는다.
재표집(O4 (2), (3))
- 단위는 최근접 짝으로 이어진 영상 묶음(S2 pair_groups.tsv)이다. 묶음을 복원 추출하고 그 안의 쌍과 쌍마다의 대조 100회를 함께 가져온다. 5명과 모든 seed에 같은 뽑힌 횟수를 쓴다.
- 재표집마다 실제 r과 대조 100회 r의 평균을 다시 내 효과를 낸다. 구간은 basic 95%, p는 중심을 맞춘 양측 검정 (1 + #(|Δ* − Δ| ≥ |Δ|)) / (B + 1).
- 묶음 크기 분포(영상 수, 참가자별 쌍 수)를 clusters.tsv와 run_info.json에 적는다(04 기록 칸 S9).
다중비교: 2-2의 p는 prereg_pvalues.tsv로 s10_holm15.py에 넘긴다. 정서별 결과는 탐색이고 BH-FDR(참가자마다, 비교마다 34개 정서, 6-1).
출력(레포 밖 --out): swap_scores.tsv, prereg_pvalues.tsv, swap_per_emotion.tsv, path_difference_per_emotion.tsv, interaction_per_emotion.tsv, kragel_groups.tsv, clusters.tsv, coverage.tsv, run_info.json
사용: s10_swap.py --swap-dir <S9 swap 폴더> --out <출력 폴더> --design-freeze <커밋> [--n-boot 10000] [--partial-check] [--overwrite]
"""
import argparse
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

import s4_common as c
import s10_inputs as I
import s10_performance as perf
import s10_stats as st

PATHS = ("visual", "caption", "both")  # audition_codex.PATH_ORDER
TESTS = {"visual": "2-2 시각만", "caption": "2-2 캡션만", "both": "2-2 둘 다"}
KRAGEL = {"높았던 정서": ("craving", "sexual desire", "entrancement", "horror"), "낮았던 정서": ("confusion", "awe", "surprise")}  # 04 S9, 01 1-3의 1-1
N_CONTROL = 100  # O3
BOOT_CHUNK = 500


def find_runs(swap_dir):
    """폴더 이름의 (seed, fold). 돌려주는 값: 표(seed, fold, path, status), 빠진 목록."""
    rows = []
    for d in sorted(Path(swap_dir).iterdir()):
        m = re.fullmatch(r"outer_fold(\d+)_seed(\d+)", d.name)
        if not m or not d.is_dir():
            continue
        ok = (d / "interventions.pt").exists() and (d / "done.json").exists()
        rows.append(dict(seed=int(m.group(2)), fold=int(m.group(1)), path=str(d), status="ok" if ok else "끝나지 않음"))
    t = pd.DataFrame(rows, columns=["seed", "fold", "path", "status"])
    if t.empty:
        raise SystemExit(f"{swap_dir}: outer_fold<k>_seed<s> 폴더가 없다")
    missing = []
    for s in sorted(t.seed.unique()):
        have = set(t.fold[(t.seed == s) & (t.status == "ok")])
        missing += [dict(seed=s, fold=k) for k in range(1, I.N_FOLDS + 1) if k not in have]
    return t, missing


def load_seed(paths, split, y, pairs, groups):
    """seed 하나의 fold들. 돌려주는 값: 참가자 -> 모은 배열, 짝 확인 기록."""
    ypos = {v: i for i, v in enumerate(split.video_id.astype(int).tolist())}
    fold_of = dict(zip(split.video_id.astype(int), split.fold.astype(int)))
    group_of = dict(zip(groups.video_id.astype(int), groups.pair_group))
    raw, log = {}, []
    for k, path in sorted(paths.items()):
        data = torch.load(Path(path) / "interventions.pt", map_location="cpu", weights_only=False)
        pk = pairs[pairs.fold == k]
        for q, x in data.items():
            vids = np.asarray(x["video_ids"], np.int64)
            if x["fold"] != k or any(fold_of[int(v)] != k for v in vids):
                raise ValueError(f"{path} {q}: fold {k}가 아닌 영상이 있다")
            pr = x["pairs"].numpy()
            a, b = vids[pr[:, 0]], vids[pr[:, 1]]
            have = set(vids.tolist())
            want = {(int(u), int(v)) for u, v in zip(pk.video_a, pk.video_b) if u in have and v in have}
            if set(zip(a.tolist(), b.tolist())) != want or len(a) != len(want):
                raise ValueError(f"{path} {q}: 쌍이 pairs_directed.tsv의 그 fold 짝(두 영상이 모두 있는 것)과 다르다(O9)")
            dy = y[[ypos[int(v)] for v in b]] - y[[ypos[int(v)] for v in a]]
            if not np.allclose(x["delta_y"].numpy(), dy, atol=1e-5):
                raise ValueError(f"{path} {q}: 저장된 Δy가 사람 평정의 y_B − y_A와 다르다")
            ga, gb = [group_of[int(v)] for v in a], [group_of[int(v)] for v in b]
            if ga != gb:
                raise ValueError(f"{path} {q}: 쌍의 두 영상이 다른 짝 연결 묶음에 있다")
            if x["control_delta_p"].shape[0] != N_CONTROL:
                raise ValueError(f"{path} {q}: 대조가 {N_CONTROL}회가 아니다(O3)")
            raw.setdefault(q, []).append((k, x, np.array(ga)))
            log.append(dict(participant=q, fold=k, n_pairs=len(a), n_pairs_missing=int((~(pk.video_a.isin(have) & pk.video_b.isin(have))).sum())))
    out = {}
    for q, items in raw.items():
        items.sort(key=lambda t: t[0])
        cat = lambda key, axis=0: np.concatenate([np.asarray(it[1][key].numpy(), np.float64) for it in items], axis)
        p, cp = cat("p"), cat("control_p", 1)
        out[q] = dict(folds=[it[0] for it in items], items=[it[1] for it in items], dp=cat("delta_p"), dy=cat("delta_y"), cdp=cat("control_delta_p", 1),
                      I=cat("I"), cI=cat("control_I", 1), Ip=p[:, 1, 1] - p[:, 1, 0] - p[:, 0, 1] + p[:, 0, 0],
                      cIp=cp[:, :, 1, 1] - cp[:, :, 1, 0] - cp[:, :, 0, 1] + cp[:, :, 0, 0], group=np.concatenate([it[2] for it in items]))
    return out, pd.DataFrame(log)


def effects_from_r(real, ctrl):
    """real: (…, 3, 34), ctrl: (…, 100, 3, 34). 대조 r의 평균은 한 회라도 NaN이면 NaN이다(audition_codex와 같음)."""
    cm = ctrl.mean(-3)
    return cm, real - cm


def observed(d):
    """관찰 값. 상수 판정은 정확히 같은 값(pearson_columns, audition_codex.change_alignment와 같은 규칙)."""
    P = len(d["dy"])
    real = st.pearson_columns(np.tile(d["dy"], 3), d["dp"].reshape(P, -1)).reshape(3, 34)  # 열 순서: 경로, 정서
    cdp = np.moveaxis(d["cdp"], 0, 1).reshape(P, -1)
    ctrl = st.pearson_columns(np.tile(d["dy"], N_CONTROL * 3), cdp).reshape(N_CONTROL, 3, 34)
    cm, eff = effects_from_r(real, ctrl)
    absI = {"logit": np.abs(d["I"]).mean(0), "probability": np.abs(d["Ip"]).mean(0)}
    cabsI = {"logit": np.abs(d["cI"]).mean(1).mean(0), "probability": np.abs(d["cIp"]).mean(1).mean(0)}
    return dict(real=real, ctrl=cm, effect=eff, real_const_p=st.constant_columns(d["dp"].reshape(P, -1)).reshape(3, 34),
                ctrl_nan=np.isnan(ctrl).any(0), target_const=st.constant_columns(d["dy"]), absI=absI, cabsI=cabsI)


def boot(d, Wpair):
    """묶음 재표집. Wpair: (B, 쌍) 쌍마다 뽑힌 횟수. 돌려주는 값: effect (B, 3, 34), real (B, 3, 34), I 효과 {척도: (B, 34)}."""
    P = len(d["dy"])
    X = np.concatenate([d["dp"].reshape(P, -1), np.moveaxis(d["cdp"], 0, 1).reshape(P, -1)], 1)
    col_of = np.arange(X.shape[1]) % 34
    mI = {"logit": (np.abs(d["I"]), np.abs(d["cI"]).mean(0)), "probability": (np.abs(d["Ip"]), np.abs(d["cIp"]).mean(0))}
    effs, reals, Ieff = [], [], {k: [] for k in mI}
    for i in range(0, len(Wpair), BOOT_CHUNK):
        w = Wpair[i:i + BOOT_CHUNK].astype(np.float64)
        r = st.boot_r_paired(w, X, d["dy"], col_of)
        real, ctrl = r[:, :102].reshape(-1, 3, 34), r[:, 102:].reshape(-1, N_CONTROL, 3, 34)
        _, e = effects_from_r(real, ctrl)
        effs.append(e), reals.append(real)
        sw = w.sum(1, keepdims=True)
        for k, (a, b) in mI.items():
            with np.errstate(invalid="ignore", divide="ignore"):
                Ieff[k].append((w @ a - w @ b) / sw)
    return np.concatenate(effs), np.concatenate(reals), {k: np.concatenate(v) for k, v in Ieff.items()}


def check_against_audition(d, ob):
    """관찰 효과가 S9가 쓰는 audition_codex.summarize_interventions와 같은지 본다."""
    import s6_model as M
    s = M.ac.summarize_interventions([M.ac.FoldInterventions(**x) for x in d["items"]])
    if not np.allclose(s["effect"].numpy(), ob["effect"], atol=1e-6, equal_nan=True):
        raise ValueError("관찰 효과가 audition_codex.summarize_interventions와 다르다")
    if not np.allclose(s["mean_abs_I_effect"].numpy(), ob["absI"]["logit"] - ob["cabsI"]["logit"], atol=1e-6):
        raise ValueError("관찰 |I| 효과가 audition_codex와 다르다")


def per_emotion_rows(kind, seed, q, emotions, est, b, extra=None):
    """정서별 탐색 표. BH는 이 행 묶음(참가자 하나, 비교 하나, 34개 정서) 안에서 한다."""
    lo, hi = st.basic_ci(est, b)
    p = st.centered_p(est, b)
    pb = st.bh(p)
    return [dict(seed=seed, participant=q, comparison=kind, emotion=emotions[e], estimate=est[e], ci_low=lo[e], ci_high=hi[e], p_raw=p[e], p_bh=pb[e],
                 family_size=int(np.isfinite(p).sum()), label="탐색(BH-FDR)", **{k: v[e] for k, v in (extra or {}).items()}) for e in range(len(est))]


def analyze_seed(seed, data, Wunits, gcode, emotions, check_audition=True):
    pids = sorted(data)
    ob, bt = {}, {}
    for q in pids:
        d = data[q]
        ob[q] = observed(d)
        if check_audition:
            check_against_audition(d, ob[q])
        bt[q] = boot(d, Wunits[:, gcode[q]])
    eligible = {q: ~ob[q]["target_const"] for q in pids}
    score, sboot, nused = {}, {}, {}
    for q in pids:
        for j, path in enumerate(PATHS):
            keep = eligible[q] & np.isfinite(ob[q]["effect"][j])
            score[q, path] = float(ob[q]["effect"][j][keep].mean()) if keep.any() else np.nan
            sboot[q, path] = st.mean_over(bt[q][0][:, j], keep)
            nused[q, path] = int(keep.sum())
    rows, pre, emo, diff, inter, kr = [], [], [], [], [], []
    for j, path in enumerate(PATHS):
        score["mean5", path] = float(np.mean([score[q, path] for q in pids]))
        sboot["mean5", path] = np.mean(np.stack([sboot[q, path] for q in pids]), 0)
        for q in pids + ["mean5"]:
            est, b = score[q, path], sboot[q, path]
            lo, hi = I.ci_row(est, b)
            p = float(st.centered_p(est, b))
            base = dict(seed=seed, participant=q, path=path, test_id=TESTS[path], effect=est, ci_low=lo, ci_high=hi, p_raw=p, n_boot_valid=int(np.isfinite(b).sum()))
            if q != "mean5":
                o = ob[q]
                keep = eligible[q]
                base.update(actual_r_mean=float(np.nanmean(o["real"][j][keep])), control_r_mean=float(np.nanmean(o["ctrl"][j][keep])), n_emotions_used=nused[q, path],
                            n_target_constant=int(o["target_const"].sum()), n_prediction_constant=int((o["real_const_p"][j] & keep).sum()),
                            n_control_noncomputable=int((o["ctrl_nan"][j] & keep).sum()), n_pairs=len(data[q]["dy"]))
            rows.append(base)
            pre.append(dict(test_id=TESTS[path], family=q, seed=seed, estimate=est, p_raw=p, statistic="34개 정서 평균의 (실제 r − 대조 100회 평균 r), 짝 연결 묶음 bootstrap의 중심 맞춘 양측 p",
                            source="s10_swap", analysis="all"))
    for q in pids + ["mean5"]:
        if q == "mean5":
            stack = lambda f: np.nanmean(np.stack([f(x) for x in pids]), 0)
            eff = stack(lambda x: np.where(eligible[x][None], ob[x]["effect"], np.nan))
            effb = np.nanmean(np.stack([np.where(eligible[x][None, None], bt[x][0], np.nan) for x in pids]), 0)
            Iest = {k: stack(lambda x: np.where(eligible[x], ob[x]["absI"][k] - ob[x]["cabsI"][k], np.nan)) for k in ("logit", "probability")}
            Iboot = {k: np.nanmean(np.stack([bt[x][2][k] for x in pids]), 0) for k in ("logit", "probability")}
        else:
            eff = np.where(eligible[q][None], ob[q]["effect"], np.nan)
            effb = np.where(eligible[q][None, None], bt[q][0], np.nan)
            Iest = {k: np.where(eligible[q], ob[q]["absI"][k] - ob[q]["cabsI"][k], np.nan) for k in ("logit", "probability")}
            Iboot = {k: bt[q][2][k] for k in ("logit", "probability")}
        for j, path in enumerate(PATHS):
            ex = dict(actual_r=ob[q]["real"][j], control_r_mean=ob[q]["ctrl"][j]) if q != "mean5" else None
            emo += per_emotion_rows(f"2-2 정서별 효과({path})", seed, q, emotions, eff[j], effb[:, j], ex)
        diff += per_emotion_rows("1-1 시각 효과 − 캡션 효과", seed, q, emotions, eff[0] - eff[1], effb[:, 0] - effb[:, 1], dict(visual_effect=eff[0], caption_effect=eff[1]))
        for k in ("logit", "probability"):
            ex = dict(mean_abs_I=ob[q]["absI"][k], control_mean_abs_I=ob[q]["cabsI"][k]) if q != "mean5" else None
            inter += per_emotion_rows(f"1-2 (나) 평균 |I| − 대조 평균 |I| ({k})", seed, q, emotions, Iest[k], Iboot[k], ex)
        for gname, names in KRAGEL.items():
            idx = [emotions.index(n) for n in names]
            for label, est, b in (("시각 효과", eff[0], effb[:, 0]), ("캡션 효과", eff[1], effb[:, 1]), ("시각 효과 − 캡션 효과", eff[0] - eff[1], effb[:, 0] - effb[:, 1])):
                keep = np.zeros(len(emotions), bool)
                keep[idx] = True
                keep &= np.isfinite(est)
                th = float(est[keep].mean()) if keep.any() else np.nan
                bb = st.mean_over(b, keep)
                lo, hi = I.ci_row(th, bb)
                kr.append(dict(seed=seed, participant=q, group=f"EmoNet에서 정지 프레임 분류 성능이 {gname}", emotions=",".join(names), n_emotions_used=int(keep.sum()), quantity=label,
                               estimate=th, ci_low=lo, ci_high=hi, p_raw=float(st.centered_p(th, bb)), label="보조(검정 묶음 밖)"))
    return dict(swap_scores=pd.DataFrame(rows), prereg_pvalues=pd.DataFrame(pre), swap_per_emotion=pd.DataFrame(emo), path_difference_per_emotion=pd.DataFrame(diff),
                interaction_per_emotion=pd.DataFrame(inter), kragel_groups=pd.DataFrame(kr))


def run(swap_dir, out, split, y, emotions, *, n_boot=st.N_RESAMPLE, partial_check=False, overwrite=False, extra_info=None, pairs=None, groups=None, check_audition=True):
    started = time.time()
    out = I.prepare_out(out, overwrite)
    runs, missing = find_runs(swap_dir)
    I.require_complete(missing, partial_check, "2-2")
    pairs = pd.read_csv(c.S2 / "pairs_directed.tsv", sep="\t") if pairs is None else pairs
    groups = pd.read_csv(c.S2 / "pair_groups.tsv", sep="\t") if groups is None else groups
    names = sorted(groups.pair_group.unique())
    gidx = {g: i for i, g in enumerate(names)}
    W = st.bootstrap_counts(len(names), n_boot, np.random.default_rng(perf.BOOT_SEED))  # 묶음 단위. 5명, seed 모두 같다
    tables, logs, csize = {}, [], []
    for seed in sorted(runs.seed.unique()):
        ok = runs[(runs.seed == seed) & (runs.status == "ok")]
        data, log = load_seed(dict(zip(ok.fold.astype(int), ok.path)), split, y, pairs, groups)
        log["seed"] = seed
        logs.append(log)
        gcode = {q: np.array([gidx[g] for g in d["group"]]) for q, d in data.items()}
        res = analyze_seed(int(seed), data, W, gcode, emotions, check_audition)
        for k, t in res.items():
            tables[k] = pd.concat([tables[k], t], ignore_index=True) if k in tables else t
        for q, d in data.items():
            cnt = pd.Series(d["group"]).value_counts()
            csize.append(pd.DataFrame(dict(seed=seed, participant=q, pair_group=cnt.index, n_pairs=cnt.values)))
        print(f"2-2 seed {seed} 끝 ({time.time() - started:.0f}초)", flush=True)
    cl = groups.drop_duplicates("pair_group")[["fold", "pair_group", "group_size"]].rename(columns={"group_size": "n_videos"})
    pairs_per = pd.concat(csize).pivot_table(index="pair_group", columns=["seed", "participant"], values="n_pairs", fill_value=0)
    pairs_per.columns = [f"n_pairs_seed{s}_{q}" for s, q in pairs_per.columns]
    tables["clusters"] = cl.merge(pairs_per, left_on="pair_group", right_index=True, how="left").fillna(0)
    tables["coverage"] = runs.merge(pd.concat(logs), on=["seed", "fold"], how="left")
    if missing:
        tables["missing"] = pd.DataFrame(missing)
    info = dict(stage="S10 2-2 swap", swap_dir=str(swap_dir), settings=dict(n_boot=n_boot, boot_seed=perf.BOOT_SEED, bootstrap_unit="짝 연결 묶음(pair_groups.tsv)", n_control=N_CONTROL),
                n_clusters=len(names), cluster_size_distribution={int(k): int(v) for k, v in cl.n_videos.value_counts().sort_index().items()},
                partial_check=bool(missing), **(extra_info or {}))
    if missing:
        info["note"] = I.PARTIAL_NOTE
    if n_boot != st.N_RESAMPLE:
        info["note_resample"] = f"재표집 횟수가 I5의 {st.N_RESAMPLE}회와 다르다. 점검용 실행이다"
    return I.write_out(out, tables, info, started)


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 2-2 바꿔 끼우기, 1-1, 1-2 (나)")
    ap.add_argument("--swap-dir", required=True, help="<output_root>/s9_saved_models/swap/<S6 결과 폴더 이름>")
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", required=True)
    ap.add_argument("--n-boot", type=int, default=st.N_RESAMPLE)
    ap.add_argument("--partial-check", action="store_true")
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args(argv)
    c.guard(a.design_freeze)
    split = c.load_split()
    y, cols = c.load_scores(split, "emotions")
    info = run(a.swap_dir, a.out, split, np.asarray(y, np.float64), I.emotion_names(cols), n_boot=a.n_boot, partial_check=a.partial_check, overwrite=a.overwrite,
               extra_info=dict(design_freeze=a.design_freeze))
    print(f"끝: {a.out} ({info['elapsed_seconds']}초)")


if __name__ == "__main__":
    main()
