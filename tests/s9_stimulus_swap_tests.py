#!/usr/bin/env python3
"""s9_stimulus_swap 합성 자료 시험(11/16). 실제 자료와 뇌 반응을 읽지 않는다. src에서 실행한다.

보는 것: 더하기 head(r = 0)에서는 I가 0이다, 대조의 교체 길이가 실제 교체 길이와 같다, 대조 영상 C는 A, B가 아니고 같은 seed면 같다,
Δy = y_B − y_A다, 저장 형식이 audition_codex.FoldInterventions로 되살아나고 summarize_interventions가 돈다.
"""
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import s9_stimulus_swap as S  # noqa: E402
from s4_feature_model import FeatureModel  # noqa: E402

fails = []


def check(name, ok):
    print(("통과 " if ok else "실패 ") + name)
    if not ok:
        fails.append(name)


torch.manual_seed(0)
n, DC = 9, S.PE.DC
x = torch.randn(n, S.DV + DC, dtype=torch.float64)
ratings = torch.rand(n, 34, dtype=torch.float64)
pairs = torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7]], dtype=torch.long)
add, inter = FeatureModel(S.DV, DC, 34, 0).eval(), FeatureModel(S.DV, DC, 34, 2).eval()
ra = S.intervene(add, x, ratings, pairs, video_ids=range(n), participant="sub-01", fold=1, control_seed=123, checkpoint_id="t")
ri = S.intervene(inter, x, ratings, pairs, video_ids=range(n), participant="sub-01", fold=1, control_seed=123, checkpoint_id="t")
check("더하기 head는 I가 0", float(ra.I.abs().max()) < 1e-4 and float(ra.control_I.abs().max()) < 1e-4)
check("상호작용 head는 I가 0이 아님", float(ri.I.abs().max()) > 1e-6)
check("대조의 교체 길이가 실제와 같음", torch.allclose(ra.control_lengths, ra.actual_lengths.expand(S.CONTROL_REPEATS, -1, -1), atol=1e-4))
ci = ra.control_indices
check("대조 영상 C는 A, B가 아님", bool(((ci != pairs[:, 0]) & (ci != pairs[:, 1])).all()))
check("같은 seed면 같은 C", torch.equal(ci, S.control_indices(n, pairs, 123)) and not torch.equal(ci, S.control_indices(n, pairs, 124)))
check("Δy = y_B − y_A", torch.allclose(ra.delta_y.double(), ratings[pairs[:, 1]] - ratings[pairs[:, 0]], atol=1e-6))
check("시각만 바꾼 Δp는 캡션을 A로 둔 값", torch.allclose(ra.delta_p[:, 0], ra.p[:, 1, 0] - ra.p[:, 0, 0]))
back = S.ac.FoldInterventions(**vars(ri))
summ = S.ac.summarize_interventions([back])
check("FoldInterventions로 되살아나고 요약이 돈다", "effect" in summ or len(summ) > 0)
print(f"s9_stimulus_swap 시험 {'통과' if not fails else '실패 ' + str(len(fails)) + '개'}")
sys.exit(1 if fails else 0)
