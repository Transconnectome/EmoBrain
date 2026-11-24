#!/usr/bin/env python3
"""s10_geometry_checks 합성 자료 시험(11/16). 실제 자료를 읽지 않는다. src에서 실행한다.

보는 것: 무게를 준 AUC가 scikit-learn과 같다(같은 점수 포함), kernel ridge가 s5_common.main_version과 같다,
dichotomy가 126개이고 차원 dichotomy는 낮음 대 높음이다, 조건 쌍마다 그 둘을 나누는 dichotomy가 70개다,
전역 신호 회귀 뒤 학습 행에서 voxel과 공변량의 상관이 0이다, size 변형이 가장 작은 네트워크 크기로 뽑고 seed가 같으면 같다.
"""
import sys
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import s10_geometry_checks as S  # noqa: E402
import s5_common as d5  # noqa: E402

fails = []


def check(name, ok):
    print(("통과 " if ok else "실패 ") + name)
    if not ok:
        fails.append(name)


rng = np.random.default_rng(0)
n = 300
score = rng.normal(size=n)
score[:40] = np.round(score[:40], 1)  # 같은 점수
pos = rng.random(n) < 0.4
w = rng.integers(0, 3, size=(5, n)).astype(np.float32)
got = S.wauc(score, pos, torch.as_tensor(w))
ref = np.array([roc_auc_score(pos, score, sample_weight=w[b]) for b in range(5)])
check("무게 AUC = scikit-learn", np.allclose(got, ref, atol=1e-6))
check("무게 없는 AUC = scikit-learn", abs(S.wauc(score, pos, torch.ones((1, n)))[0] - roc_auc_score(pos, score)) < 1e-9)

torch.manual_seed(0)
x = torch.randn(120, 40, dtype=torch.float64)
y = torch.randn(120, 3, dtype=torch.float64) + x[:, :3]
tr, va, te = np.arange(0, 80), np.arange(80, 100), np.arange(100, 120)
ref, _ = d5.main_version(x, y, tr, va, te)
z, _, _ = d5.standardize(x, torch.as_tensor(tr))
got = S.gram_ridge(z @ z.T, y, tr, va, te)
check("kernel ridge = main_version", torch.allclose(got, ref, atol=1e-8))

check("dichotomy 126개", len(S.DICHOTOMIES) == 126 and S.SIDE.shape == (126, 10))
check("차원 dichotomy는 낮음(짝수) 대 높음(홀수)", S.DICHOTOMIES[S.DIM_DICHOTOMY] == frozenset({0, 2, 4, 6, 8}))
check("조건 쌍마다 나누는 dichotomy 70개", all(int((S.SIDE[:, a] != S.SIDE[:, b]).sum()) == 70 for a, b in S.PAIRS))
check("dichotomy마다 (c1, c2) 조합 25개", all(sum(S.SIDE[t, a] != S.SIDE[t, b] for a, b in S.PAIRS) == 25 for t in range(126)))

C = np.c_[np.ones(120), rng.normal(size=(120, 2))]
xg = x + torch.as_tensor(C[:, 1:2]) * 3
r = S.residualize(xg, C, tr)
cc = np.corrcoef(np.c_[C[tr, 1:], r[tr].numpy()].T)[:2, 2:]
check("전역 신호 회귀 뒤 학습 행 상관 0", np.abs(cc).max() < 1e-10)

nets = {"a": np.arange(0, 50), "b": np.arange(50, 70), "c": np.arange(70, 200)}
s0, s0b, s1 = S.network_inputs(nets, "size0", "01"), S.network_inputs(nets, "size0", "01"), S.network_inputs(nets, "size1", "01")
check("size는 가장 작은 크기로 뽑음", all(len(p) == 20 for p in s0.values()) and all(np.isin(s0[g], nets[g]).all() for g in nets))
check("같은 seed면 같고 다른 뽑기면 다름", all(np.array_equal(s0[g], s0b[g]) for g in nets) and not np.array_equal(s0["c"], s1["c"]))
check("raw는 그대로", all(np.array_equal(S.network_inputs(nets, "raw", "01")[g], nets[g]) for g in nets))
print(f"s10_geometry_checks 시험 {'통과' if not fails else '실패 ' + str(len(fails)) + '개'}")
sys.exit(1 if fails else 0)
