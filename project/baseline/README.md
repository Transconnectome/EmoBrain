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

- **Question.** Does the `common36` block response of one participant predict held-out normative affect better than the training mean, under run-group separated splits? This is a check of loader, split and scaling with real data, not a scientific claim.
- **Cohort roles (decision 2026-10-20, `docs/current/04_DECISION_REGISTER.md` D28).** Horikawa 2020 is the training and development cohort; MindCaptioning is the later validation cohort. Models and settings are fixed on Horikawa 2020; MindCaptioning fMRI is not used for training or tuning, and `run_pilot` refuses MindCaptioning participants. MindCaptioning final-test videos (72) stay excluded from every development scope.
- **Data.** Horikawa 2020 sub-01, `runz` brain variant, final v3 responses (fieldmap-less SyN-SDC, 202,183 voxels), development subset from `project/output/audits/pilot_data/audit_20261020T052441Z`: fit 8 / tune 2 / evaluate 2 run components (324 / 72 / 72 rows), components with MindCaptioning final-test content excluded.
- **Method.** Training-only voxel standardization, dual ridge per target space, alpha chosen on tune from a grid declared before fitting, refit on fit+tune, one evaluation on evaluate. 34-D and 14-D run as separate jobs.
- **Run.** On the login node: `bash /pscratch/sd/s/sjmoon/EmoBrain/project/baseline/brain_decoding/run.sh cat34 <new-experiment-id>` (and `affect14`; default participant `horikawa/sub-01`); `sbatch` with the same arguments also works. Outside SLURM the script passes `--login-node` and the host is recorded in `metadata.json`. Log goes to `runs/logs/<experiment-id>.log`. Each experiment ID can be used once.
- **Limits.** One participant and one fixed split, so no inference. The codebook contracts record that the original Cowen & Keltner codebook is not on the server (34-D order taken from `cowen34_order.txt`, 14-D polarity unverified). A weak result does not show absent brain information; a good one does not select preprocessing.

## Results index

| Experiment ID | Target | Status | Summary |
| --- | --- | --- | --- |
| claude-cat34-hk01-r1 | cat34 | done 2026-10-20, login node, code 8ecd58e + uncommitted T005 | MSE reduction 0.117 (row bootstrap 0.080 to 0.151); mean r 0.268 (0.215 to 0.312) vs row-shuffle 95th pct 0.047; 27/34 dims above training mean; alpha 1e5 (interior) |
| claude-affect14-hk01-r1 | affect14 | done 2026-10-20, login node, code 8ecd58e + uncommitted T005 | MSE reduction 0.013 (0.007 to 0.021); mean r 0.259 (0.151 to 0.357) vs shuffle 95th pct 0.108; 14/14 dims; **alpha 1e7 = grid upper edge** (tuning MSE still falling), predictions shrunk to 2.5% of target SD |

Horikawa runs are under `brain_decoding/runs/4b94193e.../<experiment-id>/`; both pass the strict recomputation in `summarize.py` (W04). For affect14 the selected alpha sits at the declared grid edge, so the small MSE reduction reflects heavy shrinkage rather than absent signal (correlation is above the shuffle reference in all 14 dimensions); a wider grid must be declared before any rerun. One participant with 72 evaluate rows: descriptive only.

### Executed before the cohort decision: MindCaptioning sub-01

Run record only. On 2026-10-07, before the cohort roles were decided, the same baseline ran once per target on MindCaptioning sub-01 (training-session runs ses-trainPerception01 run-01 to run-06 and ses-trainPerception02 run-01 to run-06, 436 rows; audit 044941Z, now in `superseded/`; code 116ddd7 plus the uncommitted T005 files). These runs were not used to select any model or setting, and MindCaptioning is not used for training or tuning. Outputs are kept unchanged on the server under `brain_decoding/runs/be0eee6e.../`.

| Experiment ID | Target | Executed |
| --- | --- | --- |
| claude-cat34-sub01-r1 | cat34 | 2026-10-07, login node |
| claude-affect14-sub01-r1 | affect14 | 2026-10-07, login node |
