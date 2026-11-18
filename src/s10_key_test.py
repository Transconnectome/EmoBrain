#!/usr/bin/env python3
"""S10 핵심 시험의 첫 판(11/18 석진 님 "필요한 분석 빠르게"; 06 통합 스토리라인 4절의 핵심 시험). CPU, 수 초. 결과를 본 뒤 더한 탐색 분석이다.

질문: 정서마다, 평정을 맞히는 데 상황 정보가 물체 정보보다 더 필요한 정도(뇌 없음)와, 뇌에서 그 정서 평정이 상황 정보에 기대는 정도가 함께 가는가.
이 판은 6-4d(src/s10_beyond_scene.py)의 저장값만 쓴다. 물체 수준은 Sw(motion energy + 이름표 73개), 상황 수준은 C(Caption feature 정서어 제거판)로 대신한다.
  물체 단어, 속성과 관계 단어로 나눈 캡션은 아직 없다(06 14절 4번). 그래서 Sw에는 저수준 움직임과 장소 이름표도 섞여 있다는 한계가 있다.
- 가로축 x_e = r(C → 평정) − r(Sw → 평정): 뇌 없이 교차 예측한 r(6-4d features_only.tsv).
- 세로축 y_e = r_brain(Sw 잔차) − r_brain(C 잔차): 같은 영역에서 두 잔차를 뇌가 읽은 r(6-4d scores.tsv, 5명 평균)의 차이.
- 기준선(06 4절 제안): 뇌에서 읽히는 정보가 평정 전체에 고르게 퍼져 있다면 잔차 r의 기대값은 r_brain(T) × √(1 − R²), R² = r(특징 → 평정)²(0 아래는 0).
  b_e = r_brain(T) × (√(1 − R²_Sw) − √(1 − R²_C)). 기준선을 뺀 y_e − b_e도 낸다.
- 판정 없이 보고하는 값: 정서 27개(01 0절, Cowen & Keltner 7개 제외)에서 Spearman ρ(x, y), ρ(x, y − b), 정서 이름표 순열 10,000회의 양측 p.
  06의 예측은 "점들이 오른쪽 위로"(ρ > 0)다. 영역은 뇌 전체와 네트워크 13개.
출력(--out): points.tsv(영역 × 정서의 x, y, b, y − b), summary.tsv(영역마다 ρ와 p), run_info.json
- 11/18 둘째 판: --object N --stats <beyond_scene_levels>로 물체 수준을 물체 단어만 남긴 캡션(N)으로 바꾼다. 물체와 전체 캡션이 같은 언어 모델(DeBERTa-large, 같은 층)이라
  특징 차원과 모델이 같다(비판 agent 11/17의 "B와 C는 같은 언어 모델로"). NA(물체 + 속성)도 --object NA로 낼 수 있다.
사용: s10_key_test.py --stats <s10_stats/beyond_scene 또는 beyond_scene_levels> --out <폴더> [--object Sw|N|NA] [--situation C]
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

import s4_common as c

CK7 = ("pride", "triumph", "contempt", "disappointment", "sympathy", "guilt", "envy")
N_PERM = 10_000
PERM_SEED = 20261118


def spearman(a, b):
    ra, rb = pd.Series(a).rank().to_numpy(), pd.Series(b).rank().to_numpy()
    return float(np.corrcoef(ra, rb)[0, 1])


def perm_p(x, y, rng):
    obs = spearman(x, y)
    null = np.array([spearman(x, rng.permutation(y)) for _ in range(N_PERM)])
    return obs, float((1 + (np.abs(null) >= abs(obs)).sum()) / (N_PERM + 1))


def run(stats, out, obj="Sw", sit="C"):
    f = pd.read_csv(Path(stats) / "features_only.tsv", sep="\t").set_index("target")
    s = pd.read_csv(Path(stats) / "scores.tsv", sep="\t")
    s = s[s.is_category & ~s.target.isin(CK7)]
    emos = sorted(s.target.unique())
    if len(emos) != 27:
        raise SystemExit(f"정서가 27개가 아니다: {len(emos)}")
    r_sw, r_c = f.loc[emos, f"r_{obj}_to_T"].to_numpy(), f.loc[emos, f"r_{sit}_to_T"].to_numpy()
    r2_sw, r2_c = np.clip(r_sw, 0, None) ** 2, np.clip(r_c, 0, None) ** 2
    x = r_c - r_sw
    rows, summ = [], []
    rng = np.random.default_rng(PERM_SEED)
    for net, g in s.groupby("network"):
        piv = g.pivot_table(index="target", columns="read", values="r").loc[emos]
        t, sw, cc = piv["T"].to_numpy(), piv[obj].to_numpy(), piv[sit].to_numpy()
        y = sw - cc
        b = t * (np.sqrt(1 - r2_sw) - np.sqrt(1 - r2_c))
        for i, e in enumerate(emos):
            rows.append(dict(network=net, emotion=e, x=x[i], r_Sw_to_T=r_sw[i], r_C_to_T=r_c[i], brain_T=t[i], brain_Sw_resid=sw[i], brain_C_resid=cc[i], y=y[i], baseline=b[i], y_minus_baseline=y[i] - b[i]))
        rho, p = perm_p(x, y, rng)
        rho2, p2 = perm_p(x, y - b, rng)
        summ.append(dict(network=net, rho_x_y=rho, p_x_y=p, rho_x_y_minus_baseline=rho2, p_x_y_minus_baseline=p2, mean_y=float(y.mean()), mean_baseline=float(b.mean())))
    o = Path(out)
    o.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(o / "points.tsv", sep="\t", index=False)
    pd.DataFrame(summ).to_csv(o / "summary.tsv", sep="\t", index=False)
    return dict(n_emotions=len(emos), n_perm=N_PERM, perm_seed=PERM_SEED, object_read=obj, situation_read=sit)


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 핵심 시험 첫 판(6-4d 저장값)")
    ap.add_argument("--stats", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--object", default="Sw", choices=("Sw", "N", "NA"))
    ap.add_argument("--situation", default="C", choices=("C", "NA"))
    a = ap.parse_args(argv)
    info = run(a.stats, a.out, a.object, a.situation)
    info.update(stage="S10 핵심 시험 첫 판", stats=str(a.stats), code_commit=c.START_HEAD, code_dirty=c.START_DIRTY)
    (Path(a.out) / "run_info.json").write_text(json.dumps(info, indent=1, ensure_ascii=False))
    print(json.dumps(info, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
