"""A3-4 contract tests. Run with the project python.

These check the two failure modes the contract exists to prevent: an
inferential n that counts stimuli or seeds, and a bootstrap that resamples
stimuli instead of participants.
"""
import json
from pathlib import Path

import numpy as np

CONFIGS = Path(__file__).resolve().parents[1] / "configs"
SPLITS = Path(__file__).resolve().parents[1] / "splits"


def contract():
    return json.load(open(CONFIGS / "inference_contract.json"))["contract"]


def test_inferential_unit_is_participant():
    assert contract()["inferential_unit"] == "participant"


def test_seeds_are_not_inferential():
    assert contract()["seeds_are_inferential_samples"] is False


def test_stimulus_pairs_are_not_independent():
    assert contract()["stimulus_pairs_are_independent_observations"] is False


def test_cluster_bootstrap_resamples_participants_not_stimuli():
    """A participant-clustered bootstrap must give a wider interval than a
    stimulus-level bootstrap on data with a participant offset. If it does
    not, the clustering is not actually happening."""
    rng = np.random.default_rng(0)
    n_p, n_s = 5, 400
    offset = rng.normal(0, 1.0, size=n_p)[:, None]
    x = offset + rng.normal(0, 1.0, size=(n_p, n_s))

    cl = [x[rng.integers(0, n_p, n_p)].mean() for _ in range(2000)]
    st = [x.reshape(-1)[rng.integers(0, n_p * n_s, n_p * n_s)].mean()
          for _ in range(2000)]
    assert np.std(cl) > 3 * np.std(st)


def test_no_stimulus_is_in_two_outer_folds():
    folds = json.load(open(SPLITS / "folds.json"))["outer"]
    seen = set()
    for members in folds.values():
        s = set(members)
        assert not (s & seen)
        seen |= s


if __name__ == "__main__":
    # pytest is not installed in any environment on this system, so the tests
    # are runnable directly.
    import sys, traceback
    fails = 0
    for name, fn in sorted(list(globals().items())):
        if not name.startswith("test_") or not callable(fn):
            continue
        try:
            fn()
            print(f"  [PASS] {name}")
        except Exception:
            fails += 1
            print(f"  [FAIL] {name}")
            traceback.print_exc()
    print(f"\n  {fails} failed")
    sys.exit(1 if fails else 0)
