#!/usr/bin/env python3
"""s10_mc_ridge 합성 자료 시험(11/17). 실제 자료를 읽지 않는다. src에서 실행한다.
보는 것: ROI 평균이 위치별 voxel 평균이다, 표준화가 지정한 행의 통계를 쓴다(분산 0인 열은 1로 나눔), ridge 예측이 main_version과 같다."""
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import s10_mc_ridge as R  # noqa: E402
import s5_common as d5  # noqa: E402

fails = []


def check(name, ok):
    print(("통과 " if ok else "실패 ") + name)
    if not ok:
        fails.append(name)


rng = np.random.default_rng(0)
X = rng.normal(size=(50, 12))
pos = [np.array([0, 1, 2]), np.array([5, 9])]
m = R.roi_means(X, pos)
check("ROI 평균", np.allclose(m[:, 0], X[:, :3].mean(1)) and np.allclose(m[:, 1], X[:, [5, 9]].mean(1)))
x = np.c_[rng.normal(size=50), np.ones(50)]
z = R.zscore(x, np.arange(30))
check("지정한 행으로 표준화", np.isclose(z[:30, 0].mean(), 0) and np.isclose(z[:30, 0].std(), 1) and np.allclose(z[:, 1], 0))
y = X[:, :2] + rng.normal(size=(50, 2))
tr, va, te = np.arange(30), np.arange(30, 40), np.arange(40, 50)
ref, _ = d5.main_version(torch.as_tensor(X), torch.as_tensor(y), tr, va, te)
check("ridge = main_version", np.allclose(R.ridge_fit_predict(X, y, tr, va, te), ref.numpy()))
print(f"s10_mc_ridge 시험 {'통과' if not fails else '실패 ' + str(len(fails)) + '개'}")
sys.exit(1 if fails else 0)
