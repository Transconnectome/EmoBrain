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
    run.sh                   bash (login node) or sbatch launcher: fit, then summarize
    summarize.py, .sh        per-dimension r and MSE reduction from predictions.tsv
    runs/                    git-ignored: <preprocessing-hash>/<experiment-id>/, logs/
```

## brain_decoding

- **Question.** Does the v2 `common36` block response of one participant predict held-out normative affect better than the training mean, under run-group separated splits? This is a check of loader, split and scaling with real data, not a scientific claim.
- **Data.** MindCaptioning sub-01, `runz` brain variant, development subset from `project/output/audits/pilot_data/audit_20261008T044941Z` (fit 8 / tune 2 / evaluate 2 run components; 289 / 72 / 74 rows after the pilot-only annotation quarantine). Reserved final-test content is never used.
- **Method.** Training-only voxel standardization, dual ridge per target space, alpha chosen on tune from a grid declared before fitting, refit on fit+tune, one evaluation on evaluate. 34-D and 14-D run as separate jobs.
- **Run.** On the login node: `bash /pscratch/sd/s/sjmoon/EmoBrain/project/baseline/brain_decoding/run.sh cat34 <new-experiment-id>` (and `affect14`); `sbatch` with the same arguments also works. Outside SLURM the script passes `--login-node` and the host is recorded in `metadata.json`. Log goes to `runs/logs/<experiment-id>.log`. Each experiment ID can be used once.
- **Limits.** One participant and one fixed split, so no inference. The codebook contracts record that the original Cowen & Keltner codebook is not on the server (34-D order taken from `cowen34_order.txt`, 14-D polarity unverified). A weak result does not show absent brain information; a good one does not select preprocessing.

## Results index

| Experiment ID | Target | Status | Summary |
| --- | --- | --- | --- |
| claude-cat34-sub01-r1 | cat34 | done 2026-10-07, login node, code 116ddd7 + uncommitted T005 | MSE reduction 0.107 (row bootstrap 0.065 to 0.148); mean r 0.273 (0.210 to 0.322) vs row-shuffle 95th pct 0.050; 28/34 dims above training mean; alpha 1e5 (interior) |
| claude-affect14-sub01-r1 | affect14 | done 2026-10-07, login node, code 116ddd7 + uncommitted T005 | MSE reduction 0.152 (0.045 to 0.243); mean r 0.301 (0.170 to 0.412) vs shuffle 95th pct 0.113; 10/14 dims; alpha 1e5 (interior) |

Runs are under `brain_decoding/runs/be0eee6e.../<experiment-id>/` (`summary.md`). Across the 14 affect dimensions, decoding r tracks each dimension's correlation with valence in the label table (r = 0.90 over dimensions) and not arousal (arousal r 0.03, attention -0.02, dominance -0.11). Descriptive only: one participant, 74 evaluate rows from two runs.
