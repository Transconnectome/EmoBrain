"""Sanity check for evaluation metrics.

Verifies.
    profile_correlation.
        - pred == target -> pearson 1.0, spearman 1.0.
        - random pred -> near 0.
        - constant clip skipped (not NaN in the mean).
    per_emotion_correlation.
        - pred == target -> all ~ 1.0.
        - rare subset mean computed.
    rsa.
        - pred == target -> ~ 1.0.
        - shuffled structure -> lower.
    dim_compression_curve.
        - pred == target -> ~ 1.0 at all k.
        - monotone-ish, saturates.

Run.
    bash project/scripts/metrics_smoke.sh
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np  # noqa: E402
import torch  # noqa: E402
from project.evaluation.metrics import (  # noqa: E402
    profile_correlation,
    per_emotion_correlation,
    rsa,
    dim_compression_curve,
    compute_metrics,
    C,
)


def check_profile() -> None:
    print("[profile_correlation]")
    torch.manual_seed(0)
    N = 200
    # Structured target (shared factors) so profiles are non-degenerate.
    factor = torch.randn(N, 3)
    loading = torch.randn(3, C)
    target = factor @ loading + 0.1 * torch.randn(N, C)

    m = profile_correlation(target.clone(), target)
    print(f"  perfect: pearson={m['pearson_mean']:.4f} spearman={m['spearman_mean']:.4f} "
          f"used={m['n_used']} skipped={m['n_skipped']}")
    assert m["pearson_mean"] > 0.999
    assert m["spearman_mean"] > 0.999

    rand = torch.randn(N, C)
    mr = profile_correlation(rand, target)
    print(f"  random : pearson={mr['pearson_mean']:+.4f} spearman={mr['spearman_mean']:+.4f}")
    assert abs(mr["pearson_mean"]) < 0.2

    # constant clip -> skipped
    target2 = target.clone()
    pred2 = target.clone()
    pred2[0, :] = 5.0  # constant vector -> undefined corr
    mc = profile_correlation(pred2, target2)
    print(f"  1 constant clip: used={mc['n_used']} skipped={mc['n_skipped']}")
    assert mc["n_skipped"] == 1


def check_per_emotion() -> None:
    print("")
    print("[per_emotion_correlation]")
    torch.manual_seed(1)
    N = 300
    factor = torch.randn(N, 4)
    loading = torch.randn(4, C)
    target = factor @ loading + 0.1 * torch.randn(N, C)

    rare_idx = [11, 13, 17, 20, 24, 25, 27, 32, 33, 30]
    m = per_emotion_correlation(target.clone(), target, rare_idx=rare_idx)
    print(f"  perfect: mean={m['mean']:.4f} rare_mean={m['rare_mean']:.4f} skipped={m['n_skipped']}")
    assert m["mean"] > 0.999
    assert m["rare_mean"] > 0.999


def check_rsa() -> None:
    print("")
    print("[rsa]")
    torch.manual_seed(2)
    N = 300
    factor = torch.randn(N, 3)
    loading = torch.randn(3, C)
    target = factor @ loading + 0.1 * torch.randn(N, C)

    m0 = rsa(target.clone(), target)
    print(f"  perfect: rsa={m0['rsa_pearson']:.4f} pairs={m0['n_pairs']}")
    assert m0["rsa_pearson"] > 0.999

    shuffled = target[:, torch.randperm(C)]
    m1 = rsa(shuffled, target)
    print(f"  shuffled emotion order: rsa={m1['rsa_pearson']:+.4f}")
    assert m1["rsa_pearson"] < m0["rsa_pearson"] - 0.1


def check_dim_compression() -> None:
    print("")
    print("[dim_compression_curve]")
    torch.manual_seed(3)
    N = 300
    factor = torch.randn(N, 3)
    loading = torch.randn(3, C)
    target = factor @ loading + 0.1 * torch.randn(N, C)

    m = dim_compression_curve(target.clone(), target)
    print(f"  ks           = {m['ks']}")
    print(f"  pearson_at_k = {[round(x, 3) for x in m['pearson_at_k']]}")
    # Perfect prediction should retain ~1.0 at all k >= 2.
    for k, v in zip(m["ks"], m["pearson_at_k"]):
        if k >= 2:
            assert v > 0.99, f"k={k} pearson={v}"


def check_dispatcher() -> None:
    print("")
    print("[compute_metrics dispatcher]")
    torch.manual_seed(4)
    N = 128
    factor = torch.randn(N, 3)
    loading = torch.randn(3, C)
    target = factor @ loading + 0.1 * torch.randn(N, C)
    out = compute_metrics(target.clone(), target, which=["profile", "rsa"])
    print(f"  keys returned: {sorted(out.keys())}")
    assert set(out.keys()) == {"profile", "rsa"}


def main() -> None:
    check_profile()
    check_per_emotion()
    check_rsa()
    check_dim_compression()
    check_dispatcher()
    print("")
    print("all checks OK")


if __name__ == "__main__":
    main()
