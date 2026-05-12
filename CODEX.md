# FEELIN Codex Instructions

Read `CONTEXT_FEELIN.md` first. It is the compact project memory.

## File Policy

- Keep edits scoped.
- Do not create redundant root markdown files.
- Do not duplicate dataset/model/task details in root files. Point to the
  canonical reference file instead.
- When updating entry-point docs such as `README.md`, `README_KR.md`,
  `ONBOARDING.md`, or `ACTION_PLAN.md`, add short inline pointers near the
  relevant section, e.g. "For dataset details, see `reference/datasets.md`."
  Do not rely only on a separate lookup table.
- Put canonical narrative in `Paper/framework_EN.md` and `Paper/framework_KR.md`.
- Put methods in `Paper/methodology.md`.
- Put active Korean execution planning in `ACTION_PLAN.md`.
- Put project-operation automation in `scripts/`.
- Put runnable setup/experiment scripts in `setup/code/`.
- Do not touch raw data, checkpoints, embeddings, or generated outputs unless
  explicitly asked.

## Scientific Policy

- FEELIN is a model-development project.
- SwiFT is the first backbone, not a protected conclusion.
- The first benchmark artifact is the `Dataset x BFM x Task` master matrix in
  `notes/benchmark_design.md`.
- Current benchmark BFMs are SwiFT, Brain-JEPA, NeuroSTORM, and BrainLM.
- If another BFM beats SwiFT under matched dataset/task/split conditions,
  document and pivot.
- Logistic/ridge/ROI/voxel models are statistical floors, not the main Model
  Axis.
- Stimulus-only video/audio/text models and TRIBE v2 are later controls or
  extension branches, not part of the first BFM benchmark matrix.
- Old EmoDe caches are reference only.
- Canonical Horikawa/Cowen stimulus count is `2185`.

## First Benchmark Order

1. Confirm the `Dataset x BFM x Task` master matrix.
2. Mark cells as `RUN`, `CHECK`, or `NA`.
3. Define target, split, metric, and statistical floor for each runnable cell.
4. Run frozen BFM probes for SwiFT, Brain-JEPA, NeuroSTORM, and BrainLM where
   loadable.
5. Fill `Dataset | BFM | Task | Target | Split | Metric | Statistical floor |
   BFM score | Status | Decision`.
6. Only after the matrix is populated, decide on SwiFT adaptation,
   pretraining, stimulus-only controls, or TRIBE/stimulus alignment.

## Where To Look

| Need | Use |
|---|---|
| Compact project memory | `CONTEXT_FEELIN.md` |
| Current execution plan | `ACTION_PLAN.md` |
| Dataset x BFM x Task master matrix | `notes/benchmark_design.md` |
| Dataset details | `reference/datasets.md` |
| BFM/model details | `reference/code_resources.md`, `reference/papers.md` |
| Task and metric definitions | `reference/task.md` |
| Post-benchmark training/adaptation strategy | `reference/training_strategy.md` |
| Paper/proposal narrative | `Paper/framework_EN.md`, `Paper/framework_KR.md` |
| Methodology details | `Paper/methodology.md` |

## Checks

```bash
python3 scripts/check_md_completeness.py
python3 scripts/build_project_status.py
```
