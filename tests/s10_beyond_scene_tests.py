#!/usr/bin/env python3
"""s10_beyond_scene 합성 자료 시험(11/17). 실제 자료를 읽지 않는다. src에서 실행한다.

보는 것: band 하나의 kernel 교차 예측이 s10_rating_parts.crossfit(s5_common.DualRidge)과 같다, band 무게가 trace를 band마다 같게 맞춘다,
학습 행에서 상수인 열이 있어도 멈추지 않는다, 시험 fold의 값은 시험 fold의 평정과 무관하다, 판정 규칙(남음, 흡수, 보류)이 머리말과 같다.
"""
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import s10_beyond_scene as S  # noqa: E402
import s10_rating_parts as RP  # noqa: E402

fails = []


def check(name, ok):
    print(("통과 " if ok else "실패 ") + name)
    if not ok:
        fails.append(name)


rng = np.random.default_rng(0)
n = 180
fold = np.repeat(np.arange(1, 7), n // 6)
x = rng.normal(size=(n, 30))
y = x[:, :2] @ rng.normal(size=(2, 3)) + rng.normal(size=(n, 3))
k = 2
a = S.crossfit_banded([x], y, fold, k)
b = RP.crossfit(torch.as_tensor(x), torch.as_tensor(y), fold, k)
check("band 하나 = s10_rating_parts.crossfit", np.allclose(a, b, atol=1e-8))

x1, x2 = rng.normal(size=(n, 10)), rng.normal(size=(n, 200))
tr = np.arange(100)
K, _ = S.band_kernel([x1, x2], tr, [np.arange(100, 120)])
K1, _ = S.band_kernel([x1], tr, [np.arange(100, 120)])
K2, _ = S.band_kernel([x2], tr, [np.arange(100, 120)])
w1, w2 = 210 / (2 * 10), 210 / (2 * 200)
check("band 무게로 trace가 같다", np.isclose(float(torch.trace(w1 * K1)), float(torch.trace(w2 * K2)), rtol=1e-6)
      and np.allclose(K.numpy(), (w1 * K1 + w2 * K2).numpy()))
check("전체 trace = 표준화한 feature를 붙였을 때", np.isclose(float(torch.trace(K)), 210 * len(tr), rtol=1e-6))

xc = x.copy()
xc[fold != k, 0] = 1.0  # 학습 행에서 상수
try:
    S.crossfit_banded([xc, x2], y, fold, k)
    ok = True
except Exception:
    ok = False
check("학습 행에서 상수인 열이 있어도 돈다", ok)

y2 = y.copy()
y2[fold == k] = rng.normal(size=((fold == k).sum(), 3)) * 5
check("시험 fold 값은 시험 평정과 무관", np.allclose(S.crossfit_banded([x, x2], y, fold, k), S.crossfit_banded([x, x2], y2, fold, k)))

check("판정 남음", S.classify(0.08, 0.01, 0.15, True) == "survives")
check("부호가 5명 같지 않으면 남음이 아님", S.classify(0.08, 0.01, 0.15, False) == "inconclusive")
check("판정 흡수", S.classify(0.01, -0.03, 0.04, True) == "absorbed")
check("r < 0.05면 남음이 아님", S.classify(0.04, 0.01, 0.07, True) == "inconclusive")
check("읽는 판 5개, 장면 판 4개", S.READ == ("T", "Sw", "V", "C", "Sall") and set(S.SETS) == {"Sw", "V", "C", "Sall"})
print(f"s10_beyond_scene 시험 {'통과' if not fails else '실패 ' + str(len(fails)) + '개'}")
sys.exit(1 if fails else 0)
