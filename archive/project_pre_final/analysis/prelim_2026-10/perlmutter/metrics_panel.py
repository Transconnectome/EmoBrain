#!/usr/bin/env python3
"""저장된 예측(긴 형식)에서 지표를 가능한 한 많이 계산한다 (2026-10-28). 나중에 고를 수 있게 모두 기록한다.

차원별 (34개 범주·14개 차원 각각 계산 후 평균)
  pearson, spearman, r2 (1 − SSE/SST, 기준 = 학습 fold 평균), mse, mae, ccc (Lin 일치 상관), calib_slope (실제를 예측에 회귀한 기울기),
  soft_bce (34개만), r_noise_norm (r / √라벨 신뢰도, 34개만), auc_ge01·ap_ge01·auc_ge05 (평정 비율 0.1·0.5 이상을 양성으로, 34개만)
영상별 (한 영상의 프로필)
  profile_r, profile_spearman, cosine, top1_acc, top3_overlap (실제 상위 3개 중 예측 상위 3개에 든 비율), pair_id (같은 fold 안 영상 짝 구별, 우연 0.5)
문헌 지표 (34개 범주, 0.1 이상 = 양성)
  mae_sum34 (GED: 34개 합산 MAE 의 영상 평균), map27 (27개 범주 label 별 AP 평균; ML-BVAE·AESL), map34,
  micro_f1·macro_f1 (예측 ≥ 0.1), one_error, ranking_loss, example_ap (영상별 label 순위 AP)
출력: project/output/prelim_2026-10/10_metrics/metrics_by_subject.tsv, metrics_summary.tsv
사용: python metrics_panel.py   (아래 SOURCES 의 모든 예측 파일)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import average_precision_score, f1_score, label_ranking_average_precision_score, label_ranking_loss, roc_auc_score

sys.path.insert(0, str(Path(__file__).parent))
import run_stage1 as rs  # noqa: E402

O = rs.OUT
OUT = O / "10_metrics"
NOT7 = rs.bb.NOT_DISTINCT7
SOURCES = {  # 이름: (예측 파일 패턴, 남길 조건 접두어 None = 전부)
    "softbce": ("07_students/softbce/predictions_sub-*.tsv.gz", None),
    "mlp": ("07_students/mlp/predictions_sub-*.tsv.gz", None),
    "ridge_pilot": ("06_linear_distill/vjepa2_vitg_final+caption_human_mpnet/predictions_sub-*.tsv.gz", ["student_w0", "student_wsel", "teacher_content"]),
    "ridge_labelpca": ("06_linear_distill/labelpca/predictions_sub-*.tsv.gz", None),
}
REL = pd.read_csv(rs.REPO / "docs/reports/prelim_2026-10/stage0/tables/label_structure_reliability.tsv", sep="\t").set_index("감정")["라벨신뢰도"]


def ccc(y, p):
    my, mp = y.mean(), p.mean(); return 2 * np.cov(y, p, bias=True)[0, 1] / (y.var() + p.var() + (my - mp) ** 2)


def safe(f, *a):
    try:
        return f(*a)
    except ValueError:
        return np.nan


def dim_metrics(g, space):
    y, p, m = g.y_true.values, g.y_pred.values, g.train_mean.values
    ok = p.std() > 0 and y.std() > 0
    out = dict(pearson=np.corrcoef(y, p)[0, 1] if ok else np.nan, spearman=spearmanr(y, p).correlation if ok else np.nan,
               r2=1 - ((y - p) ** 2).sum() / ((y - m) ** 2).sum(), mse=((y - p) ** 2).mean(), mae=np.abs(y - p).mean(),
               ccc=ccc(y, p), calib_slope=np.polyfit(p, y, 1)[0] if ok else np.nan)
    if space == "A34":
        pc = np.clip(p, 1e-7, 1 - 1e-7)
        out.update(soft_bce=float(-(y * np.log(pc) + (1 - y) * np.log(1 - pc)).mean()),
                   r_noise_norm=out["pearson"] / np.sqrt(REL.get(g.dimension.iloc[0], np.nan)),
                   auc_ge01=safe(roc_auc_score, y >= .1, p), ap_ge01=safe(average_precision_score, y >= .1, p),
                   auc_ge05=safe(roc_auc_score, y >= .5, p) if (y >= .5).sum() >= 5 else np.nan)
    return out


def profile_metrics(g, space):
    Yt = g.pivot_table(index="video_id", columns="dimension", values="y_true"); Yp = g.pivot_table(index="video_id", columns="dimension", values="y_pred")
    Yp = Yp[Yt.columns]; T, P = Yt.values, Yp.values
    fo = g.groupby("video_id").outer_fold.first().loc[Yt.index].values
    z = lambda A: (A - A.mean(1, keepdims=True)) / (A.std(1, keepdims=True) + 1e-12)  # noqa: E731
    pr = (z(T) * z(P)).mean(1)
    acc = []
    for f in np.unique(fo):
        A, B = z(P[fo == f]), z(T[fo == f]); C = A @ B.T / A.shape[1]; d = np.diag(C)
        acc.append(np.mean([(d[i] > np.delete(C[i], i)).mean() for i in range(len(C))]))
    out = dict(profile_r=np.nanmean(pr), profile_spearman=np.nanmean([spearmanr(a, b).correlation for a, b in zip(T, P)]),
               cosine=np.mean((T * P).sum(1) / (np.linalg.norm(T, axis=1) * np.linalg.norm(P, axis=1) + 1e-12)),
               top1_acc=np.mean(T.argmax(1) == P.argmax(1)),
               top3_overlap=np.mean([len(set(np.argsort(-a)[:3]) & set(np.argsort(-b)[:3])) / 3 for a, b in zip(T, P)]),
               pair_id=np.mean(acc))
    if space == "A34":
        Lb = T >= .1; c27 = [i for i, c in enumerate(Yt.columns) if c not in NOT7]
        aps = lambda idx: np.nanmean([safe(average_precision_score, Lb[:, i], P[:, i]) for i in idx if Lb[:, i].any()])  # noqa: E731
        keep = Lb[:, c27].any(1)
        out.update(mae_sum34=np.abs(T - P).sum(1).mean(), map27=aps(c27), map34=aps(range(T.shape[1])),
                   micro_f1=f1_score(Lb[:, c27], P[:, c27] >= .1, average="micro", zero_division=0),
                   macro_f1=f1_score(Lb[:, c27], P[:, c27] >= .1, average="macro", zero_division=0),
                   one_error=np.mean(~Lb[keep][:, c27][np.arange(keep.sum()), P[keep][:, c27].argmax(1)]),
                   ranking_loss=label_ranking_loss(Lb[keep][:, c27], P[keep][:, c27]),
                   example_ap=label_ranking_average_precision_score(Lb[keep][:, c27], P[keep][:, c27]))
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True); rows = []
    for src, (pat, keep) in SOURCES.items():
        fs = sorted(O.glob(pat))
        if not fs:
            continue
        P = pd.concat([pd.read_csv(f, sep="\t") for f in fs])
        if keep:
            P = P[P.input_condition.isin(keep)]
        for (pid, cond, space), g in P.groupby(["participant_id", "input_condition", "target_space"]):
            dm = pd.DataFrame([dim_metrics(h, space) for _, h in g.groupby("dimension")]).mean()
            rows.append(dict(source=src, condition=cond, target_space=space, participant_id=pid, **dm.to_dict(), **profile_metrics(g, space)))
        print(f"{src}: {P.input_condition.nunique()}개 조건", flush=True)
    R = pd.DataFrame(rows); R.to_csv(OUT / "metrics_by_subject.tsv", sep="\t", index=False, float_format="%.5f")
    S = R.groupby(["target_space", "source", "condition"]).mean(numeric_only=True)
    S.to_csv(OUT / "metrics_summary.tsv", sep="\t", float_format="%.4f")
    pd.set_option("display.width", 300); pd.set_option("display.max_columns", 40)
    for sp in ["A34", "A14"]:
        print(f"== {sp}"); print(S.loc[sp].dropna(axis=1, how="all").round(3).T.to_string())


if __name__ == "__main__":
    main()
