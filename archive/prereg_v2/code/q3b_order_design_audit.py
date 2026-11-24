"""Preprocessing census q3b. Is the presentation order random with respect to
content and annotation?

Scientific question
-------------------
Are clips that were shown back to back more alike, in visual content or in
normative annotation, than clips shown far apart in the same run?

What this excludes
------------------
q3 measures how much of a clip's window belongs to the preceding clip. If the
order were random, that leak is noise. If neighbours were alike, the leak
would carry content and annotation of the neighbour into the clip's own
pattern, and a decoder could exploit it. This uses no brain data, so it is a
property of the design, not an outcome.

Outputs
-------
qc/order_design_audit.json
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from _assets import ASSETS, MANIFESTS, provenance, read_tsv, write_json  # noqa: E402
from _qc import QC  # noqa: E402

SCRIPT = "prereg_v2/code/q3b_order_design_audit.py"


def main() -> None:
    prov = provenance(SCRIPT)
    ev = read_tsv(MANIFESTS / "events_audited.tsv")
    ev = ev[(ev.participant_id == "sub-01") & (~ev.is_baseline)]
    sig = np.load(MANIFESTS / "clip_signatures.npy")
    sig_nums = np.load(MANIFESTS / "clip_signature_video_numbers.npy")
    S = {int(n): sig[i] for i, n in enumerate(sig_nums)}
    lab = pd.read_csv(ASSETS["labels_emobrain"]["path"]).set_index("stim_num_int")
    c34 = [c for c in lab.columns if c.startswith("score_")]
    c14 = [c for c in lab.columns if c.endswith("_score") and not c.startswith("score_")]
    A34 = {int(k): v for k, v in zip(lab.index, lab[c34].to_numpy(float))}
    A14 = {int(k): v for k, v in zip(lab.index, lab[c14].to_numpy(float))}

    rng = np.random.default_rng(20260927)
    out = {"provenance": prov}
    for name, F, corr in [("clip_signature", S, "dot"), ("annotation34", A34, "pearson"),
                          ("annotation14", A14, "pearson")]:
        adj, far = [], []
        for _, g in ev.groupby(["session", "run"]):
            order = g.sort_values("onset_sec").stimulus_number.astype(int).tolist()
            for i in range(1, len(order)):
                a, b = order[i], order[i - 1]
                cand = [order[j] for j in range(len(order)) if abs(j - i) >= 5]
                c = cand[rng.integers(len(cand))]
                if a in F and b in F and c in F:
                    f = (lambda x, y: float(x @ y)) if corr == "dot" else (lambda x, y: float(np.corrcoef(x, y)[0, 1]))
                    adj.append(f(F[a], F[b])); far.append(f(F[a], F[c]))
        adj, far = np.array(adj), np.array(far)
        d = adj - far
        boot = [rng.choice(d, d.size).mean() for _ in range(2000)]
        out[name] = {"n_pairs": int(d.size), "adjacent_mean": float(adj.mean()),
                     "far_mean": float(far.mean()), "difference": float(d.mean()),
                     "difference_ci95": [float(np.quantile(boot, .025)), float(np.quantile(boot, .975))]}
        print(f"  {name}: adjacent {adj.mean():.4f}  far {far.mean():.4f}  diff {d.mean():.4f} "
              f"CI {out[name]['difference_ci95']}")
    write_json(QC / "order_design_audit.json", out)


if __name__ == "__main__":
    main()
