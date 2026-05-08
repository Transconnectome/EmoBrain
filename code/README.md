# NetFeeliX Code Workspace

This directory is for shared modeling utilities and code plans. Initial runnable
scripts should normally live in `setup/code/`.

Project-operation automation lives in `scripts/`, not here.

- `scripts/check_md_completeness.py`: project-level documentation and workflow checks.
- `scripts/build_project_status.py`: generates `reports/status/PROJECT_STATUS.md`.
- `scripts/generate_experiment_cards.py`: creates structured experiment cards.

## Initial Coding Priorities

1. `setup/code/build_dataset_inventory.py`
   - Scan available local datasets.
   - Write a CSV/Markdown inventory to `setup/data/`.

2. `setup/code/build_emotion_targets.py`
   - Standardize Horikawa and Emo-FilM target matrices.
   - Write target metadata to `setup/data/`.

3. `setup/code/run_linear_baselines.py`
   - Ridge/elastic-net baselines for arousal, valence, and emotion vectors.
   - Write tables to `setup/results/`.

4. `setup/code/check_pretrained_models.py`
   - Verify which pretrained models can be imported and loaded locally.
   - Write availability report to `setup/results/`.

## Script Documentation Rule

Do not create extra Markdown files for every small script. Use a clear module docstring, `--help` output, and concise comments unless the script becomes a major reusable workflow.

## Data Policy

- Do not store large raw datasets in this repository unless they are already local and intentionally linked.
- Store derived arrays under `setup/data/` for initial work.
- Store final metrics and figures under `setup/results/` for initial work.
