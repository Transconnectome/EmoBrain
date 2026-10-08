# Baseline experiments

_Development baselines for the pilot (handoff 10, P1). Not final results._

Each baseline gets one subfolder holding everything needed to rerun it: config, target codebook contracts, launcher, summary script, and an ignored `runs/` folder. Shared library code stays where it is (`project/data/pilot_adapter.py`, `project/code/pilot/`, `project/scripts/run_pilot.py`).

```text
project/baseline/
  README.md
  brain_decoding/            B -> affect, ridge vs training-mean predictor
    config.json              participant, subset roles, alpha grid, budgets
    codebook/cat34.json      target contract checked by run_pilot before fitting
    codebook/affect14.json
    codebook/template.json   empty template (intentionally rejected)
    run.sh                   SBATCH launcher: fit, then summarize
    summarize.py, .sh        per-dimension r and MSE reduction from predictions.tsv
    runs/                    git-ignored: <preprocessing-hash>/<experiment-id>/, logs/
```

## brain_decoding

- **Question.** Does the v2 `common36` block response of one participant predict held-out normative affect better than the training mean, under run-group separated splits? This is a check of loader, split and scaling with real data, not a scientific claim.
- **Data.** MindCaptioning sub-01, `runz` brain variant, development subset from `project/output/audits/pilot_data/audit_20261008T044941Z` (fit 8 / tune 2 / evaluate 2 run components; 289 / 72 / 74 rows after the pilot-only annotation quarantine). Reserved final-test content is never used.
- **Method.** Training-only voxel standardization, dual ridge per target space, alpha chosen on tune from a grid declared before fitting, refit on fit+tune, one evaluation on evaluate. 34-D and 14-D run as separate jobs.
- **Run.** `sbatch /pscratch/sd/s/sjmoon/EmoBrain/project/baseline/brain_decoding/run.sh cat34 <new-experiment-id>` (and `affect14`). Each experiment ID can be used once.
- **Limits.** One participant and one fixed split, so no inference. The codebook contracts record that the original Cowen & Keltner codebook is not on the server (34-D order taken from `cowen34_order.txt`, 14-D polarity unverified). A weak result does not show absent brain information; a good one does not select preprocessing.

## Results index

| Experiment ID | Target | Status | Summary |
| --- | --- | --- | --- |
| (none yet) | | | |
