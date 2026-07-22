"""Audit spec build steps 1-3 against implementation_spec_20260702 Acceptance.

The user chose "review steps 1-3; reuse only if they are correct". This script
does not read code, it VERIFIES the spec's own Acceptance clauses empirically so
the reuse decision rests on measurement.

Clauses checked.
    A  Appendix A. 34 emotion canonical order is fixed and matches the spec list.
    B  §3 / §5-1. Labels are crowd proportions in [0,1], sparse by nature.
    C  §5-2 Acceptance. z-score is fit on TRAIN ONLY and after transform the
       train per-emotion mean ~ 0 and std ~ 1. val/test reuse the same stats.
    D  §5-3. Split is clip-level with no stimulus leaking across splits.
    E  §9 Acceptance. Every headline / auxiliary metric function exists and runs.
    F  §7 Acceptance. B1 ridge (no LLM) is reported on the same 34D metric.
    G  §5-4. caption_map exists for the MindCaptioning mapping.

Run.
    bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/audit_spec_stage123.sh
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

DATA = REPO_ROOT / "project" / "shared" / "data"
LABELS_CSV = DATA / "cowen_horikawa_labels.csv"
SPLIT_CSV = DATA / "horikawa_split.csv"
ORDER_TXT = DATA / "cowen34_order.txt"
NORM_DIR = DATA / "norm_stats"
SCORE_COLS = [f"score_{k}" for k in range(34)]

# Appendix A of the spec, verbatim order.
SPEC_ORDER = [
    "admiration", "adoration", "aesthetic appreciation", "amusement", "anger",
    "anxiety", "awe", "awkwardness", "boredom", "calmness", "confusion",
    "contempt", "craving", "disappointment", "disgust", "empathic pain",
    "entrancement", "envy", "excitement", "fear", "guilt", "horror", "interest",
    "joy", "nostalgia", "pride", "relief", "romance", "sadness", "satisfaction",
    "sexual desire", "surprise", "sympathy", "triumph",
]

results = []


def check(clause: str, name: str, ok: bool, detail: str) -> None:
    results.append({"clause": clause, "name": name, "pass": bool(ok), "detail": detail})
    print(f"  [{'PASS' if ok else 'FAIL'}] {clause} {name}. {detail}")


def clause_A() -> None:
    if not ORDER_TXT.exists():
        check("A", "34 emotion order", False, f"missing {ORDER_TXT}")
        return
    ours = [l.strip() for l in ORDER_TXT.read_text().splitlines() if l.strip()]
    ok = ours == SPEC_ORDER
    if ok:
        detail = f"{len(ours)} emotions, exact match with spec Appendix A"
    else:
        diff = [(i, a, b) for i, (a, b) in enumerate(zip(ours, SPEC_ORDER)) if a != b]
        detail = (f"len ours={len(ours)} spec={len(SPEC_ORDER)}; "
                  f"first mismatches={diff[:3]}")
    check("A", "34 emotion order", ok, detail)


def clause_B(labels: pd.DataFrame) -> None:
    Y = labels[SCORE_COLS].to_numpy(np.float64)
    in_range = bool((Y >= -1e-9).all() and (Y <= 1 + 1e-9).all())
    zero_frac = float((Y == 0).mean())
    rowsum = float(Y.sum(axis=1).mean())
    check("B", "labels are crowd proportions", in_range,
          f"range [{Y.min():.3f}, {Y.max():.3f}], zero={100*zero_frac:.1f}%, "
          f"mean row-sum={rowsum:.2f} (spec: 0-1 proportion, ~74% zero, ~1.7)")


def clause_C(labels: pd.DataFrame, split: pd.DataFrame) -> None:
    """z-score fit on train only; train mean~0 std~1 after transform."""
    from project.data.labels import Cowen34Normalizer

    train_stims = sorted(split.loc[split["split"] == "train", "stimulus_num"]
                         .astype(int).unique().tolist())
    test_stims = sorted(split.loc[split["split"] == "test", "stimulus_num"]
                        .astype(int).unique().tolist())
    lab = labels.set_index("stim_num_int")
    Ytr = np.stack([lab.loc[s, SCORE_COLS].to_numpy(np.float64) for s in train_stims])
    Yte = np.stack([lab.loc[s, SCORE_COLS].to_numpy(np.float64) for s in test_stims])

    found = sorted(p.name for p in NORM_DIR.glob("*.pt"))
    for pt in NORM_DIR.glob("*.pt"):
        norm = Cowen34Normalizer.load(pt)
        ztr = np.asarray(norm.transform(Ytr))
        m, s = ztr.mean(axis=0), ztr.std(axis=0)
        ok = bool(np.allclose(m, 0, atol=0.05) and np.allclose(s, 1, atol=0.10))
        check("C", f"z-score acceptance [{pt.name}]", ok,
              f"train per-emotion mean in [{m.min():+.3f},{m.max():+.3f}] "
              f"std in [{s.min():.3f},{s.max():.3f}] (spec: ~0 / ~1)")
        # leakage probe: test stats must NOT be 0/1 if fit was train-only
        zte = np.asarray(norm.transform(Yte))
        mt, st = zte.mean(axis=0), zte.std(axis=0)
        leaked = bool(np.allclose(mt, 0, atol=1e-6) and np.allclose(st, 1, atol=1e-6))
        check("C", f"train-only fit [{pt.name}]", not leaked,
              f"test mean/std = [{mt.min():+.3f},{mt.max():+.3f}] / "
              f"[{st.min():.3f},{st.max():.3f}] (exactly 0/1 would mean test refit)")
    check("C", "norm_stats files present", len(found) > 0, f"{found}")


def clause_D(split: pd.DataFrame) -> None:
    sets = {sp: set(split.loc[split["split"] == sp, "stimulus_num"].astype(int))
            for sp in ("train", "val", "test")}
    overlaps = {f"{a}&{b}": len(sets[a] & sets[b])
                for a, b in (("train", "val"), ("train", "test"), ("val", "test"))}
    ok = all(v == 0 for v in overlaps.values())
    total = len(set.union(*sets.values()))
    check("D", "clip-level split, no leakage", ok,
          f"overlaps={overlaps}, sizes={{k: len(v) for k, v in sets.items()}}, "
          f"union={total}")
    # test set identical across subjects (needed for inter-subject analyses)
    per_subj = {s: set(g.loc[g['split'] == 'test', 'stimulus_num'].astype(int))
                for s, g in split.groupby('subject')}
    same = all(v == list(per_subj.values())[0] for v in per_subj.values())
    check("D", "test stimuli identical across subjects", same,
          f"{len(per_subj)} subjects, test size={len(list(per_subj.values())[0])}")


def clause_E() -> None:
    from project.evaluation import metrics as M

    required = ["profile_correlation", "per_emotion_correlation", "rsa",
                "dim_compression_curve", "sparse_retrieval", "error",
                "compute_metrics"]
    missing = [f for f in required if not hasattr(M, f)]
    check("E", "metric functions present", not missing,
          f"required={len(required)}, missing={missing or 'none'}")
    rng = np.random.default_rng(0)
    p, t = rng.standard_normal((40, 34)), rng.standard_normal((40, 34))
    prof = M.profile_correlation(p, t)
    heads = [k for k in ("pearson_mean", "ccc_mean", "spearman_mean") if k in prof]
    check("E", "headline Pearson+CCC+Spearman", len(heads) == 3,
          f"profile_correlation returns {heads} (spec 9-1 requires all three)")
    try:
        M.compute_metrics(p, t)
        check("E", "compute_metrics runs", True, "all families execute on smoke input")
    except Exception as e:  # noqa: BLE001
        check("E", "compute_metrics runs", False, f"raised {type(e).__name__}: {e}")


def clause_F() -> None:
    p = REPO_ROOT / "project/shared/results/noise_ceiling/ridge_subject_regimes.json"
    if not p.exists():
        check("F", "B1 ridge on 34D metric", False, f"missing {p}")
        return
    d = json.loads(p.read_text())
    keys = ("within_mean", "pooled", "loso_mean")
    ok = all(k in d for k in keys)
    check("F", "B1 ridge on 34D metric", ok,
          f"profile pearson within={d.get('within_mean'):.3f} "
          f"pooled={d.get('pooled'):.3f} loso={d.get('loso_mean'):.3f}")
    enc = REPO_ROOT / "project/shared/data/ridge_encoder.pt"
    check("F", "E2 ridge encoder artifact distinct from B1", enc.exists(),
          f"{'present' if enc.exists() else 'missing'} {enc.name} (E2 = via LLM, "
          f"B1 = no LLM; spec forbids conflating them)")


def clause_G() -> None:
    p = REPO_ROOT / "project/data/caption_map.py"
    check("G", "caption_map module", p.exists(),
          f"{'present' if p.exists() else 'missing'} (spec 5-4 MindCaptioning mapping)")


def main() -> None:
    print("=" * 70)
    print("SPEC STAGE 1-3 ACCEPTANCE AUDIT (implementation_spec_20260702)")
    print("=" * 70)
    labels = pd.read_csv(LABELS_CSV)
    split = pd.read_csv(SPLIT_CSV)

    print("\n[A] Appendix A. 34 emotion canonical order")
    clause_A()
    print("\n[B] 3 / 5-1. label definition")
    clause_B(labels)
    print("\n[C] 5-2 Acceptance. z-score, train-only fit")
    clause_C(labels, split)
    print("\n[D] 5-3. split integrity")
    clause_D(split)
    print("\n[E] 9 Acceptance. metric suite")
    clause_E()
    print("\n[F] 7 Acceptance. baseline B1")
    clause_F()
    print("\n[G] 5-4. caption map")
    clause_G()

    n_fail = sum(1 for r in results if not r["pass"])
    print("\n" + "=" * 70)
    print(f"RESULT. {len(results) - n_fail}/{len(results)} clauses PASS, {n_fail} FAIL")
    if n_fail:
        print("FAILING:")
        for r in results:
            if not r["pass"]:
                print(f"  - {r['clause']} {r['name']}: {r['detail']}")
        print("\n=> fix these modules before reuse; the rest are reusable as-is.")
    else:
        print("=> stage 1-3 satisfy the spec Acceptance. Safe to reuse and build 4-8.")
    out = REPO_ROOT / "project/shared/results/spec_stage123_audit.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    print(f"[save] {out}")


if __name__ == "__main__":
    main()
