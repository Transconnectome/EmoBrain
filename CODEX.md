# NetFeeliX Codex Instructions

Read `CONTEXT_NETFEELIX.md` first. It is the compact project memory.

## File Policy

- Keep edits scoped.
- Do not create redundant root markdown files.
- Put canonical narrative in `Paper/framework_EN.md` and `Paper/framework_KR.md`.
- Put methods in `Paper/methodology.md`.
- Put active Korean execution planning in `ACTION_PLAN.md`.
- Put project-operation automation in `scripts/`.
- Put runnable setup/experiment scripts in `setup/code/`.
- Do not touch raw data, checkpoints, embeddings, or generated outputs unless
  explicitly asked.

## Scientific Policy

- NetFeeliX is a model-development project.
- SwiFT is the first backbone, not a protected conclusion.
- If ROI/voxel/network baselines, another BFM, or stimulus-aligned models beat
  SwiFT under matched conditions, document and pivot.
- Old EmoDe caches are reference only.
- Canonical Horikawa/Cowen stimulus count is `2185`.

## Minimal Baseline Order

1. ROI/parcel ridge or elastic-net.
2. Voxel-weighted and network-restricted sparse/linear models.
3. Dynamic FC and temporal baselines.
4. Frozen BFM probes.
5. SwiFT adaptation and SL5/10/20/40 comparisons.
6. Naturalistic vs emotion-labeled vs two-stage pretraining.
7. Stimulus-only and stimulus-brain alignment.

## Checks

```bash
python3 scripts/check_md_completeness.py
python3 scripts/build_project_status.py
```
