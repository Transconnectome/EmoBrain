# NetFeeliX Scripts

Scripts here support project operations across the repository. Initial runnable
experiments should live under `setup/code/`.

## Current Scripts

| Script | Purpose |
|---|---|
| `check_md_completeness.py` | checks required docs, old broken references, dataset entry fields, and trigger/workflow presence |
| `build_project_status.py` | writes `reports/status/PROJECT_STATUS.md` from git/docs state |
| `generate_experiment_cards.py` | creates experiment-card skeletons from templates |

Runnable setup/experiment scripts live in `setup/code/`, not here.

## Common Commands

```bash
python3 scripts/check_md_completeness.py
python3 scripts/build_project_status.py
python3 scripts/generate_experiment_cards.py --id NFx-001 --title "Frozen SwiFT Horikawa probe"
```

## Rule

Do not store large data outputs here. Use `setup/data`, `setup/logs`, and
`setup/results` for initial experiments.
