# NetFeeliX Code Workspace

This directory is for shared code plans and utilities. Study-specific runnable scripts should normally live in `study{N}/code/`.

## Initial Coding Priorities

1. `study1/code/build_dataset_inventory.py`
   - Scan available local datasets.
   - Write a CSV/Markdown inventory to `study1/data/`.

2. `study1/code/build_emotion_targets.py`
   - Standardize Horikawa and Emo-FilM target matrices.
   - Write target metadata to `study1/data/`.

3. `study1/code/run_linear_baselines.py`
   - Ridge/elastic-net baselines for arousal, valence, and emotion vectors.
   - Write tables to `study1/results/`.

4. `study1/code/check_pretrained_models.py`
   - Verify which pretrained models can be imported and loaded locally.
   - Write availability report to `study1/results/`.

## Script Documentation Template

Each script should have a matching Markdown file:

```markdown
# script_name

## Purpose

## Inputs

## Outputs

## Assumptions

## Example

## Failure Modes
```

## Data Policy

- Do not store large raw datasets in this repository unless they are already local and intentionally linked.
- Store derived arrays under `study{N}/data/`.
- Store final metrics and figures under `study{N}/results/`.

