#!/usr/bin/env python3
"""EmoBrain 선행 점검 (2026-10-22). 주 데이터 = Horikawa 2020, 재현 = MindCaptioning.

--labels : 라벨(34개 감정 비율 + 14개 정서 척도)이 감정과 무관한 요인과 얽혀 있는지 (표만 읽음, 몇 초)
           요인: 영상 길이, run 안 순서(몇 번째 블록), run 안 시작 시각, 세션, 블록 머리 움직임(FD 최대), DVARS 최대
--brain  : QC 후 블록 반응에 이상한 값이 없는지 (피험자 하나, 블록 파일 전체를 한 번 읽음)
           블록별 평균·표준편차·최대 절댓값, run 별 요약, 튀는 블록 표시, 블록 전체 신호 크기와 움직임·길이·라벨의 관계
입력: response_t1w/sub-XX/{v3_qc (Horikawa), v2_qc (MindCaptioning)}
라벨: /scratch/connectome/seokjin14/EmoBrain/project/shared/data/ (cowen34_order.txt, cowen_horikawa_labels.csv)
      34개 점수는 Horikawa metadata 파일(2,196개 모두)에서, 14개 척도는 cowen_horikawa_labels.csv(2,185개)에서.
      14개 척도가 없는 영상 11개(2186~2196)는 같은 내용 영상(content_id)의 값을 쓴다.
출력: /storage/bigdata/EmoBrain_response/prelim/
사용: python confound_and_block_check.py --labels
      python confound_and_block_check.py --brain --dataset horikawa --sub 01
      python confound_and_block_check.py --brain-summary
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

OUT = Path("/storage/bigdata/EmoBrain_response/prelim")
LAB = Path("/scratch/connectome/seokjin14/EmoBrain/project/shared/data")
META = Path("/storage/bigdata/Horikawa/metadata/horikawa_meta_data_with_dimension_binary.csv")
DS = {"horikawa": ("Horikawa", "v3_qc", ["01", "02", "03", "04", "05"]),
      "mindcaptioning": ("MindCaptioning", "v2_qc", ["01", "02", "03", "04", "05", "06"])}
DIMS14 = ["valence", "arousal", "dominance", "approach", "attention", "certainty", "commitment", "control",
          "effort", "fairness", "identity", "obstruction", "safety", "upswing"]
FLAG_R = 0.1   # 이 이상이면 표에 표시 (n≈2,000 에서 p<1e-5 수준)


def mad(x):
    """정규분포 기준 표준편차 단위의 중앙절대편차 (scipy 1.3 에는 median_abs_deviation 이 없음)."""
    x = np.asarray(x, float); return 1.4826 * np.median(np.abs(x - np.median(x)))


def samples(ds, sub):
    root, ver, _ = DS[ds]
    p = Path(f"/storage/bigdata/{root}/response_t1w/sub-{sub}/{ver}/sub-{sub}_samples_qc_usable.tsv")
    return pd.read_csv(p, sep="\t")


def load_labels():
    """영상 번호(1~2196) → 34개 감정 비율 + 14개 척도. 열 이름은 감정 이름."""
    names = [l.strip() for l in open(LAB / "cowen34_order.txt") if l.strip()]
    assert len(names) == 34
    D = pd.read_csv(META); D.index = D.stimulus_num.str.replace("stimulus_", "").astype(int)
    Y = D[[f"score_{i}" for i in range(34)]].copy(); Y.columns = names
    C = pd.read_csv(LAB / "cowen_horikawa_labels.csv"); C.index = C.stim_num_int
    assert np.allclose(C[[f"score_{i}" for i in range(34)]].values, D.loc[C.index, [f"score_{i}" for i in range(34)]].values)
    Z = C[[f"{d}_score" for d in DIMS14]].copy(); Z.columns = DIMS14
    return Y, Z


def fill_by_content(Z, content):
    """14개 척도가 없는 영상은 같은 content_id 영상의 값으로 채운다."""
    Z = Z.reindex(range(1, 2197))
    for vid in Z.index[Z.isna().any(axis=1)]:
        c = content.get(vid)
        mates = [v for v, cc in content.items() if cc == c and v != vid and not Z.loc[v].isna().any()]
        if mates:
            Z.loc[vid] = Z.loc[mates[0]].values
    return Z


def spearman_table(L, F):
    """라벨 열 × 요인 열의 Spearman 상관."""
    rows = []
    for f in F.columns:
        x = F[f].to_numpy(float)
        for l in L.columns:
            y = L[l].to_numpy(float); ok = np.isfinite(x) & np.isfinite(y)
            r, p = stats.spearmanr(x[ok], y[ok]) if ok.sum() > 10 and np.std(x[ok]) > 0 and np.std(y[ok]) > 0 else (np.nan, np.nan)
            rows.append(dict(요인=f, 라벨=l, spearman_r=r, p=p, n=int(ok.sum())))
    return pd.DataFrame(rows)


def eta_sq(y, g):
    """범주형 요인(세션)이 라벨 분산을 설명하는 비율 (ANOVA η²)."""
    y = np.asarray(y, float); ok = np.isfinite(y); y, g = y[ok], np.asarray(g)[ok]
    ss_t = ((y - y.mean()) ** 2).sum()
    ss_b = sum(((y[g == k].mean() - y.mean()) ** 2) * (g == k).sum() for k in np.unique(g))
    return ss_b / ss_t if ss_t > 0 else np.nan


def run_labels():
    OUT.mkdir(parents=True, exist_ok=True)
    Y, Z = load_labels()
    out = []
    summary = {}
    for ds, (root, ver, subs) in DS.items():
        Zf = Z.reindex(range(1, 2197))   # 2026-10-24: 14개 척도 결측은 채우지 않고 관측값만 사용 (GPT 패키지 원칙)
        L = pd.concat([Y.add_prefix("감정:"), Zf.add_prefix("척도:")], axis=1)
        per_sub = []
        for s in subs:
            T = samples(ds, s)
            if "exclude_duplicate" in T:
                T = T[~T.exclude_duplicate.astype(bool)]
            if "test_video_in_train_session" in T:   # MindCaptioning: 설계상 제외 행과 시험 세션은 뺀다
                T = T[~T.test_video_in_train_session.astype(bool) & (T.part != "test")]
            T = T.copy()
            T["run_key"] = T.session.astype(str) + "_" + T.run.astype(str)
            T = T.sort_values(["run_key", "onset_sec"])
            T["run안_순서"] = T.groupby("run_key").cumcount() + 1
            F = pd.DataFrame({"영상길이_초": T.duration_sec.values, "run안_순서": T.run안_순서.values,
                              "run안_시작시각_초": T.onset_sec.values, "FD최대_블록": T.fd_max_window.values,
                              "DVARS최대_블록": T.std_dvars_max_window.values})
            Ls = L.loc[T.video_id.values].reset_index(drop=True)
            tab = spearman_table(Ls, F); tab.insert(0, "피험자", f"sub-{s}"); tab.insert(0, "데이터", root)
            # 세션: η²
            for l in Ls.columns:
                tab = pd.concat([tab, pd.DataFrame([dict(데이터=root, 피험자=f"sub-{s}", 요인="세션(η²)", 라벨=l,
                                                          spearman_r=np.nan, p=np.nan, n=len(T), eta_sq=eta_sq(Ls[l], T.session.values))])])
            per_sub.append(tab)
            # 요인끼리의 관계 (길이 ↔ 움직임 등)
            summary.setdefault(root, {})[f"sub-{s}"] = {
                "블록수": int(len(T)),
                "영상길이↔FD최대": float(stats.spearmanr(F.영상길이_초, F.FD최대_블록)[0]),
                "영상길이↔DVARS최대": float(stats.spearmanr(F.영상길이_초, F.DVARS최대_블록)[0]),
                "run안순서↔FD최대": float(stats.spearmanr(F.run안_순서, F.FD최대_블록)[0])}
        out.append(pd.concat(per_sub))
    R = pd.concat(out, ignore_index=True)
    R.to_csv(OUT / "label_confounds_long.tsv", sep="\t", index=False, float_format="%.4f")
    # 피험자 평균 (영상 단위 요인은 Horikawa 피험자 간 같음)
    g = R.groupby(["데이터", "요인", "라벨"], sort=False)
    S = g.agg(r_평균=("spearman_r", "mean"), r_최소=("spearman_r", "min"), r_최대=("spearman_r", "max"),
              eta_sq_평균=("eta_sq", "mean"), 피험자수=("피험자", "nunique")).reset_index()
    S["주의"] = np.where((S.r_평균.abs() >= FLAG_R) | (S.eta_sq_평균 >= 0.02), "확인", "")
    S.to_csv(OUT / "label_confounds_summary.tsv", sep="\t", index=False, float_format="%.4f")
    (OUT / "factor_relations.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1))
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 400)
    for root in S.데이터.unique():
        print(f"\n===== {root}: 요인별 라벨 관계 요약 (|r|≥{FLAG_R} 또는 η²≥0.02 개수 / 최대)")
        for f in S.요인.unique():
            sub = S[(S.데이터 == root) & (S.요인 == f)]
            if f.startswith("세션"):
                top = sub.sort_values("eta_sq_평균", ascending=False).head(5)
                print(f"  {f}: 확인 {int((sub.주의 == '확인').sum())}개 | 상위: " + ", ".join(f"{a}({b:.3f})" for a, b in zip(top.라벨, top.eta_sq_평균)))
            else:
                top = sub.reindex(sub.r_평균.abs().sort_values(ascending=False).index).head(6)
                print(f"  {f}: 확인 {int((sub.주의 == '확인').sum())}개 | 상위: " + ", ".join(f"{a}({b:+.2f})" for a, b in zip(top.라벨, top.r_평균)))
    print("\n요인끼리:", json.dumps(summary, ensure_ascii=False))
    print(f"저장: {OUT}")


def run_brain(ds, sub, test_rows=0):
    t0 = time.time(); OUT.mkdir(parents=True, exist_ok=True)
    out = OUT if not test_rows else OUT / "_test"; out.mkdir(parents=True, exist_ok=True)
    root, ver, _ = DS[ds]
    d = Path(f"/storage/bigdata/{root}/response_t1w/sub-{sub}/{ver}")
    T = samples(ds, sub)
    raw = np.load(d / f"sub-{sub}_blocks_common36_qc.npy", mmap_mode="r")
    rz = np.load(d / f"sub-{sub}_blocks_common36_qc_runz.npy", mmap_mode="r")
    assert raw.shape == rz.shape and raw.shape[0] == len(T), f"행 수 불일치: {raw.shape} vs {len(T)}"
    n, v = raw.shape
    if test_rows:   # 코드 경로 시험용: 앞 몇 블록만
        n = test_rows; T = T.iloc[:n].reset_index(drop=True)
    st = {k: np.zeros(n) for k in ["raw_평균", "raw_표준편차", "raw_최대절댓값", "runz_표준편차", "runz_최대절댓값", "runz_4넘는비율", "runz_8넘는비율"]}
    nan_cnt = 0
    rng = np.random.RandomState(0); samp_cols = np.sort(rng.choice(v, min(5000, v), replace=False)); samp = []
    for i0 in range(0, n, 64):
        sl = slice(i0, min(i0 + 64, n))
        a = np.asarray(raw[sl], np.float64); b = np.asarray(rz[sl], np.float64)
        nan_cnt += int((~np.isfinite(a)).sum() + (~np.isfinite(b)).sum())
        st["raw_평균"][sl] = a.mean(1); st["raw_표준편차"][sl] = a.std(1); st["raw_최대절댓값"][sl] = np.abs(a).max(1)
        st["runz_표준편차"][sl] = b.std(1); st["runz_최대절댓값"][sl] = np.abs(b).max(1)
        st["runz_4넘는비율"][sl] = (np.abs(b) > 4).mean(1); st["runz_8넘는비율"][sl] = (np.abs(b) > 8).mean(1)
        samp.append(b[:, samp_cols])
    B = T[["qc_row", "row", "video_id", "session", "run", "run_index", "duration_sec", "fd_max_window", "std_dvars_max_window"]].copy()
    for k, x in st.items():
        B[k] = x
    med = B.raw_표준편차.median(); m = mad(B.raw_표준편차)
    B["raw_표준편차_강건z"] = (B.raw_표준편차 - med) / (m if m > 0 else 1)
    B["튀는블록"] = (B.raw_표준편차_강건z.abs() > 5) | (B.runz_최대절댓값 > 15)
    B.to_csv(out / f"block_stats_{root}_sub-{sub}.tsv", sep="\t", index=False, float_format="%.5g")
    Rn = B.groupby("run_index").agg(run=("run", "first"), 블록수=("row", "size"), raw_표준편차_중앙값=("raw_표준편차", "median"),
                                    raw_평균_평균=("raw_평균", "mean"), runz_최대=("runz_최대절댓값", "max"),
                                    튀는블록수=("튀는블록", "sum"), FD최대_중앙값=("fd_max_window", "median")).reset_index()
    rmed = Rn.raw_표준편차_중앙값.median(); rmad = mad(Rn.raw_표준편차_중앙값)
    Rn["run_강건z"] = (Rn.raw_표준편차_중앙값 - rmed) / (rmad if rmad > 0 else 1)
    Rn.to_csv(out / f"run_stats_{root}_sub-{sub}.tsv", sep="\t", index=False, float_format="%.5g")
    S = np.concatenate(samp)
    summ = dict(데이터=root, 피험자=f"sub-{sub}", 블록수=n, voxel수=v, NaN_Inf=nan_cnt,
                runz_분위수={q: float(np.percentile(S, q)) for q in [0.1, 1, 50, 99, 99.9]}, runz_첨도=float(stats.kurtosis(S.ravel())),
                raw_표준편차_중앙값=float(med), 튀는블록수=int(B.튀는블록.sum()), 튀는run수=int((Rn.run_강건z.abs() > 4).sum()),
                블록신호크기_대_FD=float(stats.spearmanr(B.raw_표준편차, B.fd_max_window)[0]),
                블록신호크기_대_DVARS=float(stats.spearmanr(B.raw_표준편차, B.std_dvars_max_window)[0]),
                블록신호크기_대_영상길이=float(stats.spearmanr(B.raw_표준편차, B.duration_sec)[0]),
                블록전체평균_대_영상길이=float(stats.spearmanr(B.raw_평균, B.duration_sec)[0]),
                초=round(time.time() - t0))
    # 블록 전체 신호 크기와 라벨 (감정이 전체 신호 크기와 얽혀 있는지)
    Y, Z = load_labels(); Zf = Z.reindex(range(1, 2197))   # 2026-10-24: 결측은 채우지 않음 (이전 실행 결과는 채운 판)
    L = pd.concat([Y.add_prefix("감정:"), Zf.add_prefix("척도:")], axis=1).loc[B.video_id.values].reset_index(drop=True)
    F = pd.DataFrame({"블록신호크기(raw 표준편차)": B.raw_표준편차.values, "블록전체평균(raw)": B.raw_평균.values})
    tab = spearman_table(L, F); tab.insert(0, "피험자", f"sub-{sub}"); tab.insert(0, "데이터", root)
    tab.to_csv(out / f"block_signal_vs_labels_{root}_sub-{sub}.tsv", sep="\t", index=False, float_format="%.4f")
    top = tab.reindex(tab.spearman_r.abs().sort_values(ascending=False).index).head(5)
    summ["신호크기·라벨_상위"] = [f"{a} × {b}: {c:+.3f}" for a, b, c in zip(top.요인, top.라벨, top.spearman_r)]
    (out / f"brain_summary_{root}_sub-{sub}.json").write_text(json.dumps(summ, ensure_ascii=False, indent=1))
    print(json.dumps(summ, ensure_ascii=False, indent=1))
    print("튀는 블록:", B[B.튀는블록][["run", "video_id", "raw_표준편차_강건z", "runz_최대절댓값", "fd_max_window"]].head(20).to_string(index=False))
    print("튀는 run:", Rn[Rn.run_강건z.abs() > 4][["run", "raw_표준편차_중앙값", "run_강건z", "FD최대_중앙값"]].to_string(index=False))


def brain_summary():
    js = sorted(OUT.glob("brain_summary_*.json"))
    rows = [json.loads(p.read_text()) for p in js]
    df = pd.DataFrame([{k: (v if not isinstance(v, (dict, list)) else json.dumps(v, ensure_ascii=False)) for k, v in r.items()} for r in rows])
    df.to_csv(OUT / "brain_summary_all.tsv", sep="\t", index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    print(df.drop(columns=["runz_분위수", "신호크기·라벨_상위"]).to_string(index=False))
    for r in rows:
        print(r["데이터"], r["피험자"], "runz 분위수", {k: round(v, 2) for k, v in r["runz_분위수"].items()}, "| 신호크기·라벨 상위:", r["신호크기·라벨_상위"][:3])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", action="store_true"); ap.add_argument("--brain", action="store_true")
    ap.add_argument("--brain-summary", action="store_true"); ap.add_argument("--dataset"); ap.add_argument("--sub"); ap.add_argument("--test-rows", type=int, default=0)
    a = ap.parse_args()
    if a.labels:
        run_labels()
    elif a.brain:
        run_brain(a.dataset, a.sub, a.test_rows)
    elif a.brain_summary:
        brain_summary()
