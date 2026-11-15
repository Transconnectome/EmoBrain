#!/usr/bin/env python3
"""S10 통계 함수 (04 S10, 01 2-3, 2-4, 2-6, 6-0, 6-1, I5, N11, N12, N19, G14, B7, O4, O25, 2026-11-15).

자료를 읽거나 쓰지 않고 numpy와 pandas만 쓴다. 실제 자료는 s10_performance.py가 읽는다.

주 지표(2-3, N12)
- 참가자마다, 정서마다 6 fold의 시험 예측을 모아 Pearson r을 한 번 낸다. fold별 r을 평균하지 않는다.
- 사람 평정이나 예측이 상수라 계산할 수 없는 r은 NaN이다. 0으로 채우지 않고 그 수를 센다(2-6).
- 참가자 점수는 계산할 수 있는 정서의 r 평균, 5명 평균은 참가자 점수의 평균이다.
보조 지표(2-4, 6-0, N19, O25)
- 영상별 프로필 상관(2-4): 영상마다 34개 예측과 사람 평정의 r. 영상들에 걸쳐 평균한다(11/15 석진 님). 학습 자료의 평균 프로필(D_k 평균)을 늘 내는 기준선을 함께 낸다.
- R² = 1 − Σ(y − p)² / Σ(y − ȳ)². ȳ는 그 참가자가 모은 시험 영상의 평균이다(6-0 "실제 평정의 분산").
- 평균 예측 대비 오차 감소 = 1 − Σ(y − p)² / Σ(y − m)². m은 그 영상이 시험된 fold의 D_k 정서별 평균이다(O25).
- MAE는 전체, 사람 평정이 0인 영상, 0보다 큰 영상으로 나눠 낸다(N19).
재표집(6-1, I5, O4)
- bootstrap: 단위(같은 내용 영상 묶음)를 복원 추출하고, 영상마다 그 단위가 뽑힌 횟수를 가중치로 쓴다. 두 조건과 5명에 같은 가중치를 쓴다.
- 구간은 basic bootstrap 95% [2θ − q(0.975), 2θ − q(0.025)], 차이의 p는 중심을 맞춘 양측 검정 (1 + #(|Δ* − Δ| ≥ |Δ|)) / (B + 1)(O4 (3)).
- 순열: exchangeability block(같은 시험 fold, 같은 원래 run) 안에서만 영상과 사람 평정 34개 벡터의 대응을 섞는다.
  예측은 그대로 두고 5명에 같은 순열을 쓴다. 한쪽 p = (1 + #(귀무 값 ≥ 관찰 값)) / (순열 수 + 1)(O4 (1), (6)).
2부(2-1, 2-2)에서 더한 것
- boot_r_paired: 여러 열이 같은 y 열과 짝인 가중 r(바꿔 끼우기의 실제 교체와 대조 100회가 같은 Δy를 씀).
- permuted_feature_r: 2-1 순열. 실제 특징 벡터를 block 안에서 옮기고 decoded features는 그대로 둔다.
다중비교(6-1): Holm, BH-FDR. 값이 NaN인 검정은 묶음에서 빼고 남은 수로 보정한다.
seed(G14): 점수를 seed마다 내고 평균과 표준편차를 낸다. 예측을 seed끼리 평균하지 않는다.
"""
import warnings

import numpy as np
import pandas as pd

N_RESAMPLE = 10_000  # I5. bootstrap과 순열의 횟수
CI_LEVEL = 0.95  # 6-1. 95% 구간
REL_TOL = 1e-11  # 재표집 한 번에서 상수 열을 알아보는 수치 허용치(제곱합 대비). 결과 값이 아니라 뺄셈 오차를 걸러 내는 값이다

# 6-1 표의 [사전] 15개(04 S10 표). Holm 묶음의 구성원이고, 단계마다 이 이름으로 p를 쓴다
PREREG_15 = (
    "2-1 Vision feature", "2-1 Caption feature",
    "2-2 시각만", "2-2 캡션만", "2-2 둘 다",
    "2-3(가)", "2-3(나)", "2-3(다)", "2-3(라)", "2-3(마)", "2-3(바)",
    "처음 보는 장면",
    "1-3 Visual1", "1-3 Visual2", "1-3 Default",
)
FAMILIES = ("mean5", "sub-01", "sub-02", "sub-03", "sub-04", "sub-05")  # 6-1. 5명 평균의 묶음과 참가자마다의 묶음


def _arr(x, name):
    a = np.asarray(x, np.float64)
    if a.ndim == 1:
        a = a[:, None]
    if a.ndim != 2:
        raise ValueError(f"{name}: 2차원(영상 × 정서)이어야 한다")
    if not np.isfinite(a).all():
        raise ValueError(f"{name}: NaN 또는 Inf가 있다. 상수가 아니라 계산 실패다")
    return a


def constant_columns(a):
    """열마다 값이 모두 같은가. 영상이 1개 이하이면 상수로 본다."""
    a = np.asarray(a)
    if len(a) == 0:
        return np.ones(a.shape[1], bool)
    return a.max(0) == a.min(0)


def pearson_columns(y, p):
    """열마다 Pearson r. 사람 평정이나 예측이 상수인 열은 NaN이다(2-6, N12)."""
    y, p = _arr(y, "사람 평정"), _arr(p, "예측")
    if y.shape != p.shape:
        raise ValueError(f"사람 평정 {y.shape}과 예측 {p.shape}의 크기가 다르다")
    const = constant_columns(y) | constant_columns(p)
    yc, pc = y - y.mean(0), p - p.mean(0)
    den = np.sqrt((yc**2).sum(0) * (pc**2).sum(0))
    with np.errstate(invalid="ignore", divide="ignore"):
        r = (yc * pc).sum(0) / den
    return np.where(const | ~(den > 0), np.nan, r)


def noncomputable_reason(y, p):
    """정서마다 r을 계산할 수 없는 이유. 빈 문자열이면 계산할 수 있다. 사람 평정이 상수인 경우와 예측이 상수인 경우를 따로 센다(2-6, 6-2와 같은 구분)."""
    cy, cp = constant_columns(np.asarray(y)), constant_columns(np.asarray(p))
    out = np.full(len(cy), "", dtype=object)
    out[cy & ~cp] = "rating_constant"
    out[cp & ~cy] = "prediction_constant"
    out[cy & cp] = "rating_and_prediction_constant"
    return out


def _masked_mean(a, mask):
    n = mask.sum(0)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(n > 0, (a * mask).sum(0) / np.maximum(n, 1), np.nan)


def emotion_metrics(y, p, m=None):
    """정서마다의 지표. y, p: (영상, 정서). m: (영상, 정서) O25의 D_k 평균(없으면 오차 감소를 내지 않는다).
    돌려주는 값: 열 이름 -> (정서,) 배열. r, r2(6-0), mae, mae_zero, mae_nonzero(N19), error_reduction(O25), n_videos, n_nonzero, rating_var, prediction_var, reason."""
    y, p = _arr(y, "사람 평정"), _arr(p, "예측")
    if y.shape != p.shape:
        raise ValueError("사람 평정과 예측의 크기가 다르다")
    err = p - y
    sse = (err**2).sum(0)
    cy = constant_columns(y)
    sst = ((y - y.mean(0))**2).sum(0)
    zero = y == 0
    with np.errstate(invalid="ignore", divide="ignore"):
        r2 = np.where(cy, np.nan, 1.0 - sse / sst)
    out = dict(r=pearson_columns(y, p), r2=r2, mae=np.abs(err).mean(0), mae_zero=_masked_mean(np.abs(err), zero), mae_nonzero=_masked_mean(np.abs(err), ~zero),
               n_videos=np.full(y.shape[1], len(y)), n_nonzero=(~zero).sum(0), rating_var=y.var(0), prediction_var=p.var(0), reason=noncomputable_reason(y, p))
    if m is not None:
        m = _arr(m, "D_k 평균")
        if m.shape != y.shape:
            raise ValueError("D_k 평균의 크기가 사람 평정과 다르다")
        ssm = ((y - m)**2).sum(0)
        with np.errstate(invalid="ignore", divide="ignore"):
            out["error_reduction"] = np.where(ssm > 0, 1.0 - sse / ssm, np.nan)
    return out


def profile_r(y, p):
    """영상별 프로필 상관(2-4): 한 영상 안에서 34개 예측과 34개 사람 평정의 Pearson r. y, p: (영상, 정서). 돌려주는 값: (영상,).
    그 영상의 사람 평정이나 예측이 34개 모두 같으면 NaN이다. 요약은 영상들에 걸친 평균이다(11/15 석진 님)."""
    y, p = _arr(y, "사람 평정"), _arr(p, "예측")
    if y.shape != p.shape:
        raise ValueError("사람 평정과 예측의 크기가 다르다")
    return pearson_columns(y.T, p.T)


def weighted_mean_boot(w, values):
    """재표집마다 값의 가중 평균. w: (B, 영상) 뽑힌 횟수, values: (영상,). NaN인 영상은 빼고 평균한다."""
    v = np.asarray(values, np.float64)
    ok = np.isfinite(v)
    w = np.asarray(w, np.float64)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (w @ np.where(ok, v, 0.0)) / (w @ ok.astype(np.float64))


def dk_means(video_fold, y, weights, folds):
    """O25의 m. fold k마다 D_k(k가 아닌 fold)의 정서별 가중 평균. video_fold: (N,), y: (N, 정서), weights: (N,) 영상마다의 무게.
    무게가 1이면 영상 단위, 그 영상을 가진 참가자 수이면 행 단위다(어느 것을 쓸지는 s10_performance --dk-mean). 돌려주는 값: fold -> (정서,)."""
    video_fold, w = np.asarray(video_fold), np.asarray(weights, np.float64)
    y = _arr(y, "사람 평정")
    if (w < 0).any():
        raise ValueError("무게가 음수다")
    out = {}
    for k in folds:
        dk = video_fold != k
        total = w[dk].sum()
        if total <= 0:
            raise ValueError(f"fold {k}의 D_k가 비었다")
        out[k] = (w[dk] @ y[dk]) / total
    return out


def mean_over(values, keep):
    """keep 정서의 값 평균. values: (..., 정서). 재표집 한 번에서 NaN이 나온 정서는 그 재표집에서만 빼고 센다."""
    v = np.asarray(values, np.float64)[..., np.asarray(keep, bool)]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)  # 모두 NaN인 행은 NaN으로 둔다
        return np.nanmean(v, axis=-1)


# bootstrap

def unit_codes(labels):
    """같은 단위(같은 내용 영상 묶음, 또는 run)의 영상에 같은 번호를 준다. 돌려주는 값: (번호, 단위 수)."""
    codes, uniques = pd.factorize(pd.Series(np.asarray(labels)), sort=True)
    if (codes < 0).any():
        raise ValueError("단위 이름에 빈 값이 있다")
    return codes, len(uniques)


def bootstrap_counts(n_units, n_boot, rng, chunk=1000):
    """단위 n_units개를 n_units번 복원 추출할 때 단위마다 뽑힌 횟수. (n_boot, n_units) 정수 배열."""
    out = np.empty((n_boot, n_units), np.int32)
    for start in range(0, n_boot, chunk):
        b = min(chunk, n_boot - start)
        idx = rng.integers(0, n_units, size=(b, n_units)) + (np.arange(b)[:, None] * n_units)
        out[start:start + b] = np.bincount(idx.ravel(), minlength=b * n_units).reshape(b, n_units)
    return out


def boot_r(w, y, preds):
    """재표집마다 정서별 r. w: (B, 영상) 뽑힌 횟수, y: (영상, 정서), preds: 이름 -> (영상, 정서).
    돌려주는 값: 이름 -> (B, 정서). 재표집 안에서 사람 평정이나 예측이 상수인 열은 NaN이다."""
    y = _arr(y, "사람 평정")
    w = np.asarray(w, np.float64)
    if w.shape[1] != len(y):
        raise ValueError("가중치의 영상 수가 사람 평정과 다르다")
    y = y - y.mean(0)  # 평균을 옮겨도 r은 같고 뺄셈 오차가 줄어든다
    sw = w.sum(1, keepdims=True)
    sy, syy = w @ y, w @ (y * y)
    vy = syy - sy * sy / sw
    cy = vy <= REL_TOL * syy
    out = {}
    for name, p in preds.items():
        p = _arr(p, f"예측 {name}")
        if p.shape != y.shape:
            raise ValueError(f"예측 {name}의 크기가 사람 평정과 다르다")
        p = p - p.mean(0)
        sp, spp, syp = w @ p, w @ (p * p), w @ (y * p)
        vp = spp - sp * sp / sw
        const = cy | (vp <= REL_TOL * spp)
        with np.errstate(invalid="ignore", divide="ignore"):
            r = (syp - sy * sp / sw) / np.sqrt(np.where(const, 1.0, vy * vp))
        r[const] = np.nan
        out[name] = r
    return out


def basic_ci(theta, boot, level=CI_LEVEL):
    """basic bootstrap 구간 [2θ − q(1 − a/2), 2θ − q(a/2)](O4 (3)). boot: (B, ...). 재표집의 NaN은 빼고 분위수를 낸다."""
    a = 1.0 - level
    boot = np.asarray(boot, np.float64)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        q_lo, q_hi = np.nanquantile(boot, [a / 2, 1 - a / 2], axis=0)
    theta = np.asarray(theta, np.float64)
    return 2 * theta - q_hi, 2 * theta - q_lo


def centered_p(delta, boot_delta):
    """중심을 맞춘 양측 bootstrap p(Hall & Wilson, 1991; O4 (3)). (1 + #(|Δ* − Δ| ≥ |Δ|)) / (B + 1). B는 NaN이 아닌 재표집 수다."""
    delta = np.asarray(delta, np.float64)
    boot = np.asarray(boot_delta, np.float64)
    valid = np.isfinite(boot)
    with np.errstate(invalid="ignore"):
        hit = (np.abs(boot - delta) >= np.abs(delta)) & valid
    p = (1.0 + hit.sum(0)) / (valid.sum(0) + 1.0)
    return np.where(np.isfinite(delta), p, np.nan)


# 순열

def check_content_units(blocks, content, split_allowed):
    """O4 (1)의 "같은 내용 쌍은 한 단위로". 같은 내용 영상이 둘 이상인 묶음을 찾는다.
    한 block 안에 있으면 한 단위로 옮기는 방법을 문서가 정하지 않았으므로 멈춘다. 다른 block에 나뉘어 있으면 block 안 순열로는 함께 옮길 수 없다.
    이때 split_allowed가 참일 때만 각 영상을 자기 block 안에서 따로 섞는다(s10_performance --split-content-pairs). 돌려주는 값: 나뉜 묶음의 표."""
    t = pd.DataFrame(dict(block=np.asarray(blocks), content=np.asarray(content)))
    multi = t[t.content.duplicated(keep=False)]
    rows = []
    for name, g in multi.groupby("content"):
        if g.block.nunique() == 1:
            raise ValueError(f"같은 내용 영상 {name}이 한 block 안에 둘 이상 있다. 한 단위로 섞는 방법이 정해지지 않았다(O4 (1))")
        rows.append(dict(content=name, n_videos=len(g), blocks=",".join(str(b) for b in sorted(g.block.unique()))))
    if rows and not split_allowed:
        raise ValueError(f"같은 내용 영상 묶음이 다른 run에 나뉘어 있다({[r['content'] for r in rows]}). run 안 순열로는 한 단위로 옮길 수 없다. "
                         "각자 섞을지는 문서가 정하지 않았다. 그렇게 하려면 --split-content-pairs를 준다")
    return pd.DataFrame(rows, columns=["content", "n_videos", "blocks"])


def block_permutations(blocks, n_perm, rng):
    """block 안에서만 섞는 순열 (n_perm, N). perm[b, i]는 i번째 영상이 받는 사람 평정 벡터의 원래 위치다. 34개 정서는 한 벡터로 함께 옮긴다."""
    blocks = np.asarray(blocks)
    out = np.empty((n_perm, len(blocks)), np.int32)
    for b in pd.unique(blocks):
        idx = np.flatnonzero(blocks == b)
        order = np.argsort(rng.random((n_perm, len(idx))), axis=1)
        out[:, idx] = idx[order]
    return out


def permuted_r(perm, pos, y_all, preds):
    """순열마다 정서별 r. perm: (B, N) 전체 영상의 순열(5명 공통), pos: 이 참가자 영상의 전체 위치,
    y_all: (N, 정서) 전체 영상의 사람 평정, preds: 이름 -> (이 참가자 영상, 정서) 예측(그대로 둔다). 돌려주는 값: 이름 -> (B, 정서)."""
    y_all = _arr(y_all, "사람 평정")
    y_all = y_all - y_all.mean(0)
    pos = np.asarray(pos)
    ys = y_all[np.asarray(perm)[:, pos]]  # (B, 영상, 정서). 영상마다 34개 벡터를 통째로 받는다
    n = len(pos)
    sy = ys.sum(1)
    syy = np.einsum("bnk,bnk->bk", ys, ys)
    vy = syy - sy * sy / n
    cy = vy <= REL_TOL * syy
    out = {}
    for name, p in preds.items():
        p = _arr(p, f"예측 {name}")
        if p.shape != (n, y_all.shape[1]):
            raise ValueError(f"예측 {name}의 크기가 참가자 영상 수와 다르다")
        pc = p - p.mean(0)
        spp = (pc * pc).sum(0)
        const = cy | constant_columns(p)[None, :]
        with np.errstate(invalid="ignore", divide="ignore"):
            r = np.einsum("bnk,nk->bk", ys, pc) / np.sqrt(np.where(const, 1.0, vy * spp))
        r[const] = np.nan
        out[name] = r
    return out


def permutation_p(observed, null):
    """한쪽 순열 p(O4 (6)). (1 + #(귀무 값 ≥ 관찰 값)) / (순열 수 + 1). 예상 방향은 순열 기준보다 높다(6-1). 귀무의 NaN은 빼고 센다."""
    observed = np.asarray(observed, np.float64)
    null = np.asarray(null, np.float64)
    valid = np.isfinite(null)
    with np.errstate(invalid="ignore"):
        hit = (null >= observed) & valid
    p = (1.0 + hit.sum(0)) / (valid.sum(0) + 1.0)
    return np.where(np.isfinite(observed), p, np.nan)


# S10 2부(2-1, 2-2, 6-2, 6-3, 6-4)에서 더한 함수

def boot_r_paired(w, x, y, col_of):
    """재표집마다 열 r. x의 열 j는 y의 열 col_of[j]와 짝이다(ex) 바꿔 끼우기의 실제 교체와 대조 100회가 같은 Δy를 쓴다).
    w: (B, 행) 뽑힌 횟수, x: (행, M), y: (행, K). 돌려주는 값: (B, M). 재표집 안에서 상수인 열은 NaN이다(boot_r과 같은 허용치)."""
    x, y = _arr(x, "x"), _arr(y, "y")
    w = np.asarray(w, np.float64)
    col_of = np.asarray(col_of)
    if len(x) != len(y) or w.shape[1] != len(x) or len(col_of) != x.shape[1]:
        raise ValueError("행 수나 짝 열의 수가 맞지 않는다")
    x, y = x - x.mean(0), y - y.mean(0)
    sw = w.sum(1, keepdims=True)
    sy, syy = w @ y, w @ (y * y)
    vy = syy - sy * sy / sw
    cy = vy <= REL_TOL * syy
    sx, sxx, sxy = w @ x, w @ (x * x), w @ (x * y[:, col_of])
    vx = sxx - sx * sx / sw
    const = cy[:, col_of] | (vx <= REL_TOL * sxx)
    with np.errstate(invalid="ignore", divide="ignore"):
        r = (sxy - sx * sy[:, col_of] / sw) / np.sqrt(np.where(const, 1.0, vx * vy[:, col_of]))
    r[const] = np.nan
    return r


def permuted_feature_r(perm, pos, f_all, p):
    """2-1 순열(04 S10 순열, O4 (1)). 실제 Vision feature, Caption feature 벡터를 영상 사이에 다시 배정하고 decoded features는 그대로 둔다.
    perm: (B, N) 전체 영상의 순열(5명 공통), pos: 이 참가자 영상의 전체 위치, f_all: (N, 차원) 전체 영상의 실제 특징, p: (이 참가자 영상, 차원) decoded features.
    돌려주는 값: (B, 차원) 차원별 r. 참가자에게 없는 영상의 특징도 순열로 들어올 수 있어 분산은 순열마다 다시 낸다(permuted_r과 같은 방식). 상수 차원은 NaN이다.
    곱의 합은 float32로 모으고(영상 수천 개의 합이라 상대 오차 1e-6 안팎), 나머지는 float64다."""
    f_all = _arr(f_all, "실제 특징")
    p = _arr(p, "decoded features")
    pos = np.asarray(pos)
    perm = np.asarray(perm)
    n = len(pos)
    if p.shape != (n, f_all.shape[1]):
        raise ValueError("decoded features의 크기가 참가자 영상 수, 특징 차원과 다르다")
    fc = f_all - f_all.mean(0)
    f32 = fc.astype(np.float32)
    pc = p - p.mean(0)
    p32 = pc.astype(np.float32)
    spp = (pc * pc).sum(0)
    const_p = constant_columns(p)
    take = perm[:, pos]
    ind = np.zeros((len(perm), len(f_all)))
    ind[np.arange(len(perm))[:, None], take] = 1.0  # 이 참가자 자리에 들어온 영상
    sy, syy = ind @ fc, ind @ (fc * fc)
    vy = syy - sy * sy / n
    const = (vy <= REL_TOL * syy) | const_p[None, :]
    num = np.stack([np.einsum("nd,nd->d", f32[t], p32).astype(np.float64) for t in take])
    with np.errstate(invalid="ignore", divide="ignore"):
        r = num / np.sqrt(np.where(const, 1.0, vy * spp[None, :]))
    r[const] = np.nan
    return r


# 다중비교

def holm(p):
    """Holm(1979) 보정 p. NaN은 묶음에서 빼고 남은 수 m으로 보정한다."""
    p = np.asarray(p, np.float64)
    out = np.full(p.shape, np.nan)
    ok = np.isfinite(p)
    q = p[ok]
    m = len(q)
    if m:
        order = np.argsort(q, kind="stable")
        adj = np.minimum(np.maximum.accumulate((m - np.arange(m)) * q[order]), 1.0)
        res = np.empty(m)
        res[order] = adj
        out[ok] = res
    return out


def bh(p):
    """Benjamini-Hochberg FDR 보정 p. NaN은 묶음에서 빼고 남은 수 m으로 보정한다."""
    p = np.asarray(p, np.float64)
    out = np.full(p.shape, np.nan)
    ok = np.isfinite(p)
    q = p[ok]
    m = len(q)
    if m:
        order = np.argsort(q, kind="stable")
        ranked = q[order] * m / np.arange(1, m + 1)
        adj = np.minimum(np.minimum.accumulate(ranked[::-1])[::-1], 1.0)
        res = np.empty(m)
        res[order] = adj
        out[ok] = res
    return out


# seed(G14)

def seed_summary(df, keys, values):
    """seed마다 낸 값의 평균과 표준편차(G14). 표준편차는 ddof=1이고 seed가 하나면 NaN이다. 예측을 seed끼리 평균하지 않는다."""
    if "seed" not in df.columns:
        raise ValueError("seed 열이 없다")
    g = df.groupby(list(keys), sort=True, dropna=False)
    out = g["seed"].agg(n_seeds="nunique", seeds=lambda s: ",".join(str(x) for x in sorted(s.unique())))
    for v in values:
        out[f"{v}_mean"] = g[v].mean()
        out[f"{v}_sd"] = g[v].std(ddof=1)
    return out.reset_index()
