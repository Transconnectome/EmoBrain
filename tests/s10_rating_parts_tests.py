#!/usr/bin/env python3
"""s10_rating_parts 합성 자료 시험(11/16). 실제 자료를 읽지 않는다. src에서 실행한다.

보는 것: 시험 fold 영상의 부분 값이 시험 fold의 평정을 바꿔도 같다(시험 평정이 규칙에 들어가지 않음),
시험 fold 영상의 값이 s5_common.literature_version과 같다, D_k 영상의 값은 그 영상의 안쪽 겹을 뺀 규칙의 예측이다.
"""
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import s10_rating_parts as S  # noqa: E402
import s5_common as d5  # noqa: E402

fails = []


def check(name, ok):
    print(("통과 " if ok else "실패 ") + name)
    if not ok:
        fails.append(name)


torch.manual_seed(0)
n = 180
fold = np.repeat(np.arange(1, 7), n // 6)
x = torch.randn(n, 30, dtype=torch.float64)
y = x[:, :2] @ torch.randn(2, 3, dtype=torch.float64) + torch.randn(n, 3, dtype=torch.float64)
k = 2
a = S.crossfit(x, y, fold, k)
y2 = y.clone()
y2[fold == k] = torch.randn(int((fold == k).sum()), 3, dtype=torch.float64) * 5
b = S.crossfit(x, y2, fold, k)
check("시험 fold 값은 시험 평정과 무관", np.allclose(a[fold == k], b[fold == k]) and np.allclose(a[fold != k], b[fold != k]))
ref, _ = d5.literature_version(x, y, fold, [f for f in range(1, 7) if f != k], np.flatnonzero(fold == k))
check("시험 fold 값 = literature_version", np.allclose(a[fold == k], ref.numpy(), atol=1e-8))
j = 4
dk = np.flatnonzero(fold != k)
tr, va = dk[fold[dk] != j], dk[fold[dk] == j]
d = d5.DualRidge(x, tr, dict(val=va))
fitted = d.fit(y[tr])
cands = [d.predict("val", fitted, lam).numpy() for lam in d5.LAMBDAS]
check("D_k 값은 그 겹을 뺀 규칙의 예측", all(any(np.allclose(a[va][:, t], cc[:, t]) for cc in cands) for t in range(3)))
check("부분 이름 6 + 34 × 4개", len(S.part_names([f"e{i}" for i in range(34)])) == 6 + 34 * 4)
print(f"s10_rating_parts 시험 {'통과' if not fails else '실패 ' + str(len(fails)) + '개'}")
sys.exit(1 if fails else 0)
