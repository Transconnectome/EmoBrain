"""Assert that score_<j> in the label CSV corresponds to cowen34_order.txt[j].

Confirmed empirically 2026-09 (advisory review): 8 unambiguous caption probes
(romance/sadness/fear/amusement/disgust/surprise/joy/craving) were regressed
against every score column; 6/8 put the correct index first and the remaining
two (fear, surprise) put it 3rd of 34, behind 'amusement' -- the prank and
jump-scare clips in this corpus genuinely carry high amusement endorsement.

Import and call check_order() at the top of any script that touches per-emotion
results. A silent permutation here scrambles all 34-dimension findings.
"""
from pathlib import Path
import pandas as pd

SHARED = Path(__file__).resolve().parents[2] / "project" / "shared" / "data"


def load_order(order_file=None):
    p = Path(order_file) if order_file else SHARED / "cowen34_order.txt"
    names = [ln.strip() for ln in p.read_text().splitlines() if ln.strip()]
    assert len(names) == 34, f"expected 34 emotion names, got {len(names)}"
    return names


def check_order(labels_csv=None, emotion_query_json=None):
    """Raise AssertionError unless the label columns, the canonical order file
    and the emotion-query embedding file all agree on the same 34 names."""
    import json
    names = load_order()

    lp = Path(labels_csv) if labels_csv else SHARED / "cowen_horikawa_labels.csv"
    cols = [c for c in pd.read_csv(lp, nrows=1).columns if c.startswith("score_")]
    assert len(cols) == 34, f"expected 34 score_ columns, got {len(cols)}"
    expected = [f"score_{j}" for j in range(34)]
    assert cols == expected, f"score columns are not 0..33 in order: {cols[:5]}"

    qp = Path(emotion_query_json) if emotion_query_json else SHARED / "emotion_query" / "emotion_query_mpnet.json"
    q = json.loads(qp.read_text())
    assert q["emotions"] == names, "emotion_query_mpnet.json order != cowen34_order.txt"
    assert q["shape"][0] == 34, f"query matrix is not 34 rows: {q['shape']}"
    return names


if __name__ == "__main__":
    print("\n".join(f"score_{j}\t{n}" for j, n in enumerate(check_order())))
    print("OK: label columns, cowen34_order.txt and emotion_query_mpnet.json agree")
