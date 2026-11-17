"""s10_perturb_models의 CKA와 판정 점검(합성 자료). 사용: python tests/s10_perturb_models_tests.py"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import s10_perturb_models as PM  # noqa: E402

rng = np.random.default_rng(0)
X = rng.normal(size=(200, 50))
Q, _ = np.linalg.qr(rng.normal(size=(50, 50)))
assert abs(PM.cka(X, X @ Q * 3.0 + 1.0) - 1) < 1e-10  # 직교 변환, 등방 배율, 평행 이동에 불변
assert PM.cka(X, rng.normal(size=(200, 30))) < 0.4
rows = []
for q in ["s1", "s2", "s3", "s4", "s5"]:
    for b, v in {"A-1 depth2": 0.8, "A-1 depth4": 0.75, "C-1": 0.9, "B-1": 0.78, "D-4": 0.5, "E-고정": 0.76 if q != "s3" else 0.7, "E-학습": 0.79}.items():
        rows.append(dict(participant=q, model_a="A-1", model_b=b, cka=v))
d = PM.cka_decide(pd.DataFrame(rows)).set_index("model")
assert d.loc["D-4", "decision"] == "A-1과 다른 표현" and d.loc["D-4", "prediction_held"]
assert d.loc["B-1", "decision"] == "A-1 변형 수준" and d.loc["E-고정", "decision"] == "보류" and d.loc["C-1", "decision"] == "A-1 변형 수준"
print("s10_perturb_models tests: 3 pass")
