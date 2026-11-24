"""s10_per_emotion의 순위 상관, 순열, 편상관 점검(합성 자료). 사용: python tests/s10_per_emotion_tests.py"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import s10_per_emotion as PE  # noqa: E402

rng = np.random.default_rng(0)
a = rng.normal(size=34)
rho, p = PE.perm_spearman(a, a + 0.1 * rng.normal(size=34), 2000, 1, two_sided=False)
assert rho > 0.9 and p < 0.01, (rho, p)
rho, p = PE.perm_spearman(a, rng.normal(size=34), 2000, 1, two_sided=True)
assert p > 0.01, (rho, p)
rho, p = PE.perm_spearman(a, -a, 2000, 1, two_sided=False)
assert rho < -0.99 and p > 0.99, (rho, p)
z = rng.normal(size=34)
r = PE.residual_rank(a + 5 * z, z)
assert abs(np.corrcoef(r, PE.rank(z))[0, 1]) < 1e-8
assert abs(PE.spearman(np.arange(10), np.arange(10) ** 3) - 1) < 1e-12
print("s10_per_emotion tests: 5 pass")
