# FEELIN Code Workspace

This directory is for shared modeling utilities and code plans. Initial runnable
scripts should normally live in `setup/code/`.

Project-operation automation lives in `scripts/`. Runnable setup/experiment
scripts live in `setup/code/`.

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

5. `setup/code/check_bfm_readiness.py`
   - Verify fresh benchmark readiness for SwiFT-v2, Brain-JEPA, NeuroSTORM, and
     BrainLM.
   - This checks source code/checkpoint availability and fresh FEELIN output
     directories only; old embedding caches are deliberately ignored.

6. `setup/code/prepare_horikawa_bfm_fresh_extraction.py`
   - Generate fresh Horikawa extraction command files under `setup/jobs/`.
   - Outputs are written under
     `setup/results/fresh_embeddings/horikawa/`.

7. `setup/code/run_horikawa_bfm_benchmark.py`
   - Run the current Horikawa `Dataset x BFM x Task` benchmark slice using
     freshly extracted embeddings only.
   - Legacy cache roots are refused.

8. `setup/code/summarize_tribe_progress.py`
   - Count existing TRIBE v2 Horikawa stimulus outputs and write a progress
     report. This is a later stimulus-side branch, not part of the BFM model
     axis.

9. `setup/code/summarize_horikawa_bfm_results.py`
   - Collapse fresh Horikawa BFM result JSONs into one comparison CSV/Markdown
     table for the current `Dataset x BFM x Task` matrix slice.

## Script Documentation Rule

Do not create extra Markdown files for every small script. Use a clear module docstring, `--help` output, and concise comments unless the script becomes a major reusable workflow.

## Data Policy

- Do not store large raw datasets in this repository unless they are already local and intentionally linked.
- Store derived arrays under `setup/data/` for initial work.
- Store final metrics and figures under `setup/results/` for initial work.
