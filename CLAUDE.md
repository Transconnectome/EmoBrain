# NetFeeliX Claude Instructions

Read `CONTEXT_NETFEELIX.md` first. It is the compact project memory and should
not be duplicated here.

## Operating Rules

- Keep root files minimal. Do not create new brief/proposal/narrative markdown
  files unless explicitly requested.
- Do not duplicate dataset/model/task details in root files. Point to the
  canonical reference file instead.
- When updating entry-point docs such as `README.md`, `README_KR.md`,
  `ONBOARDING.md`, or `ACTION_PLAN.md`, add short inline pointers near the
  relevant section, e.g. "For dataset details, see `reference/datasets.md`."
  Do not rely only on a separate lookup table.
- Canonical narrative lives in `Paper/framework_EN.md` and
  `Paper/framework_KR.md`.
- Canonical methodology lives in `Paper/methodology.md`.
- Active Korean execution plan lives in `ACTION_PLAN.md`.
- Project-operation scripts live in `scripts/`.
- Runnable setup/experiment scripts live in `setup/code/`.
- Generated data/logs/results live in `setup/data/`, `setup/logs/`, and
  `setup/results/`.
- Do not overwrite raw data, model checkpoints, embeddings, or experiment
  outputs.

## Scientific Rules

- NetFeeliX is model-development, not emotion theory.
- The first benchmark deliverable is a `Dataset x BFM x Task` master matrix.
- Current benchmark models are brain foundation models: SwiFT, Brain-JEPA,
  NeuroSTORM, and BrainLM.
- Use SwiFT first, but pivot if matched `Dataset x BFM x Task` results favor
  another BFM.
- Treat logistic/ridge/ROI/voxel models as statistical floors, not as the main
  Model Axis.
- Treat video/audio/text stimulus-only models and TRIBE v2 as later
  control/extension branches, not part of the first BFM benchmark.
- Treat old EmoDe caches as reference only.
- Use `2185` as the canonical Horikawa/Cowen stimulus count.
- Keep claims separated from measured results.

## Where To Look

| Need | Use |
|---|---|
| Compact project memory | `CONTEXT_NETFEELIX.md` |
| Current execution plan | `ACTION_PLAN.md` |
| Dataset x BFM x Task master matrix | `notes/benchmark_design.md` |
| Dataset details | `reference/datasets.md` |
| BFM/model details | `reference/code_resources.md`, `reference/papers.md` |
| Task and metric definitions | `reference/task.md` |
| Post-benchmark training/adaptation strategy | `reference/training_strategy.md` |
| Paper/proposal narrative | `Paper/framework_EN.md`, `Paper/framework_KR.md` |
| Methodology details | `Paper/methodology.md` |

## Required Checks

After structural documentation edits:

```bash
python3 scripts/check_md_completeness.py
```

To refresh generated status:

```bash
python3 scripts/build_project_status.py
```
