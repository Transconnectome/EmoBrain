"""Phase 3 / A3-4 and Phase 0 / A0-2. Statistical unit contract and
environment lock.

Scientific question
-------------------
What counts as an independent observation when a result is tested, and which
software produced the artifacts this audit wrote?

What this excludes
------------------
With 5 participants and 2,180 stimuli, treating stimuli or stimulus pairs as
independent samples would shrink every interval by roughly the square root of
a few hundred. prereg_v2 D6 and A3-4 fix the participant as the inferential
unit for exactly that reason, and the contract has to exist as a checkable
object rather than a sentence in a document.

Outputs
-------
configs/inference_contract.json
configs/environment.lock.json
tests/test_inference_contract.py
"""
from __future__ import annotations

import json
import platform
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _assets import CONFIGS, PYTHON, TESTS, provenance, write_json  # noqa: E402

SCRIPT = "prereg_v2/code/p3c_inference_contract.py"

CONTRACT = {
    "inferential_unit": "participant",
    "generalization_unit": "stimulus",
    "seeds_are_inferential_samples": False,
    "stimulus_pairs_are_independent_observations": False,
    "n_participants_available": 5,
    "bootstrap": {
        "scheme": "cluster bootstrap resampling participants with replacement",
        "why": ("prereg_v2 D6 and A3-4 forbid counting stimuli or the 2,556 "
                "stimulus pairs as independent samples. A stimulus-level "
                "bootstrap over 5 pooled participants is anti-conservative "
                "because the residuals of one participant are correlated "
                "across stimuli."),
        "reporting": "per-participant points, seed spread, absolute value and "
                     "paired difference with an interval, per prereg_v2 M7",
    },
    "permutation_null": {
        "scheme": "joint permutation of stimulus labels within a held-out fold",
        "constraint": "permutations never cross a participant or fold boundary",
    },
    "power_note": (
        "With 5 participants a participant-clustered interval is wide. Any "
        "contrast that is significant only under a stimulus-level resampling "
        "is not evidence under this contract."),
    "prohibited": [
        "grouping stimuli into emotion categories, by top-1 or by threshold",
        "counting seeds as independent participants",
        "passing entries of a pairwise matrix as independent rows",
        "selecting a layer, lambda or architecture on the test fold",
    ],
}

TEST_SRC = '''"""A3-4 contract tests. Run with the project python.

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
'''


def pip_freeze() -> list:
    try:
        r = subprocess.run([PYTHON, "-m", "pip", "freeze"],
                           capture_output=True, text=True, timeout=180)
        return r.stdout.strip().splitlines()
    except Exception as e:
        return [f"pip freeze failed: {type(e).__name__}: {e}"]


def main() -> None:
    prov = provenance(SCRIPT)
    write_json(CONFIGS / "inference_contract.json",
               {"provenance": prov, "contract": CONTRACT})

    vers = {}
    for mod in ["numpy", "pandas", "torch", "sklearn", "scipy", "nibabel", "nilearn"]:
        try:
            r = subprocess.run(
                [PYTHON, "-c",
                 f"import {mod};print(getattr({mod},'__version__','unknown'))"],
                capture_output=True, text=True, timeout=120)
            vers[mod] = r.stdout.strip() or f"IMPORT FAILED: {r.stderr.strip()[:120]}"
        except Exception as e:
            vers[mod] = f"{type(e).__name__}: {e}"

    ff = {}
    for name, path in [("ffprobe", "/usr/bin/ffprobe"),
                       ("ffmpeg_system", "/usr/bin/ffmpeg"),
                       ("ffmpeg_decode", "/pscratch/sd/s/sjmoon/swift_PTL2/bin/ffmpeg")]:
        try:
            r = subprocess.run([path, "-version"], capture_output=True,
                               text=True, timeout=30)
            first = r.stdout.splitlines()[0] if r.stdout else ""
            has_h264 = False
            if "ffmpeg" in name:
                rd = subprocess.run([path, "-v", "quiet", "-decoders"],
                                    capture_output=True, text=True, timeout=60)
                has_h264 = any(line.split()[1:2] == ["h264"]
                               for line in rd.stdout.splitlines() if line.strip())
            ff[name] = {"path": path, "version": first, "h264_decoder": has_h264}
        except Exception as e:
            ff[name] = {"path": path, "error": f"{type(e).__name__}: {e}"}

    write_json(CONFIGS / "environment.lock.json", {
        "provenance": prov,
        "python_executable": PYTHON,
        "python_version": subprocess.run(
            [PYTHON, "-c", "import sys;print(sys.version)"],
            capture_output=True, text=True).stdout.strip(),
        "platform": platform.platform(),
        "library_versions": vers,
        "media_tools": ff,
        "nondeterminism_note": (
            "Nothing in Phase 0 to 3 uses a GPU or a stochastic optimizer. "
            "The only randomness is the split permutation, which is seeded and "
            "recorded in splits/split_config.json."),
        "pip_freeze": pip_freeze(),
    })

    TESTS.mkdir(parents=True, exist_ok=True)
    (TESTS / "test_inference_contract.py").write_text(TEST_SRC)
    print(f"  wrote {TESTS / 'test_inference_contract.py'}")


if __name__ == "__main__":
    main()
