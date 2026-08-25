"""Phase 0 / Gate 1 — same-dataset sanity.

Question. Does the brain-only label-query decoder reach the bar set by plain linear
ridge on the SAME roi_mean input (test per-clip 34D profile Pearson = 0.294)?

Why this gates everything. If a 3.5M-parameter decoder cannot match a linear model
on the same brain input, then the bottleneck is the brain representation we feed it,
not the label space, and any held-out-emotion result would be uninterpretable. The
fallback lever in that case is spatial resolution: R0 (~0.31) was established on
ROI means, and voxel-level data exists locally (EmoViS/data/raw/step7_voxel).

It also runs the query ablation in one pass, because the three arms share
everything except how the queries are parameterised:
    semantic_residual  frozen emotion-name embedding + learnable delta  (our design)
    semantic_frozen    frozen emotion-name embedding only
    free               fully learnable queries, no semantic anchor       (control)
This is the disciplined test of EmoGrowth's (ICML 2025) warning that naive frozen
label embeddings can hurt: we can see whether the semantic anchor helps, hurts, or
is neutral WITHIN the same architecture.

Run.
    bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/gate1_sanity.sh
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent / "_lib"))
from labelquery import (  # noqa: E402
    REFERENCE, Standardizer, bootstrap_diff, build_decoder, emotion_names,
    load_query_init, load_split, per_clip_pearson, predict, profile_metrics,
    train_decoder, REPO_ROOT,
)

OUT = REPO_ROOT / "project" / "output" / "gate1_sanity.json"
ARMS = ("semantic_residual", "semantic_frozen", "free")
MODE_OF = {"semantic_residual": "residual", "semantic_frozen": "frozen", "free": "free"}


def main():
    tr, va, te = load_split("train"), load_split("val"), load_split("test")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    scaler = Standardizer(tr["brain"])
    qi = load_query_init()
    names = emotion_names()
    print(f"[data] train {len(tr['Y'])} val {len(va['Y'])} test {len(te['Y'])} "
          f"| device={device} | queries {tuple(qi.shape)}")

    results, pcv = {}, {}
    for arm in ARMS:
        print(f"\n=== arm: {arm} ===")
        net = build_decoder(qi, MODE_OF[arm], seed=0)
        net, info = train_decoder(net, tr, va, scaler, device, active_idx=None,
                                  epochs=150, seed=0, verbose_every=30)
        pred = predict(net, te["brain"], scaler, device)
        m = profile_metrics(pred, te["Y"])
        results[arm] = {**m, **info}
        pcv[arm] = per_clip_pearson(pred, te["Y"])
        print(f"  -> TEST profile pearson={m['pearson_mean']:.4f} ccc={m['ccc_mean']:.4f} "
              f"(best val {info['best_val']:.4f} @ep{info['best_epoch']})")

    best_arm = max(ARMS, key=lambda a: results[a]["pearson_mean"])
    best = results[best_arm]["pearson_mean"]

    # Query ablation: does the semantic anchor buy anything, within-architecture?
    cis = {
        "semantic_residual_vs_free": bootstrap_diff(pcv["semantic_residual"], pcv["free"]),
        "semantic_frozen_vs_free": bootstrap_diff(pcv["semantic_frozen"], pcv["free"]),
        "semantic_residual_vs_frozen": bootstrap_diff(pcv["semantic_residual"],
                                                      pcv["semantic_frozen"]),
    }

    print("\n===== GATE 1 =====")
    print(f"{'arm':22s} {'test pearson':>13s} {'vs ridge 0.294':>16s}")
    for a in ARMS:
        d = results[a]["pearson_mean"] - REFERENCE["ridge_brain"]
        print(f"{a:22s} {results[a]['pearson_mean']:>13.4f} {d:>+16.4f}")
    print("\nquery ablation (bootstrap 95% CI on per-clip difference):")
    for k, (d, lo, hi) in cis.items():
        print(f"  {k:32s} d={d:+.4f} CI[{lo:+.4f},{hi:+.4f}] "
              f"{'sig' if (lo > 0 or hi < 0) else 'ns'}")

    passed = bool(best >= REFERENCE["ridge_brain"])
    print(f"\nbest arm = {best_arm} ({best:.4f})")
    print("VERDICT:", "PASS - proceed to Gate 2 (held-out emotion)" if passed else
          "FAIL - brain representation is the bottleneck, not the label space.\n"
          "        Do NOT interpret held-out-emotion results until this clears.\n"
          "        Next lever: voxel-level input (EmoViS/data/raw/step7_voxel).")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "results": results, "query_ablation_ci": cis, "reference": REFERENCE,
        "best_arm": best_arm, "best_pearson": best, "gate_passed": passed,
        "device": device, "n_emotions": len(names),
    }, indent=2))
    print(f"\n[done] -> {OUT}")


if __name__ == "__main__":
    main()
