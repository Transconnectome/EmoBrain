# FEELIN Compact Context

This is the compact single source of truth for FEELIN. Agent-specific files
should point here rather than duplicating the full project narrative.

## Identity

FEELIN stands for:

```text
Brain Foundation Model for Emotion-aware Experience Learning In Naturalistic Data
```

FEELIN is a **model-development project for emotion/affect representation
learning from fMRI and naturalistic stimuli**. It is not an emotion theory
project, and it should not claim to be a completed emotion foundation model
before pretraining and transfer evidence exists.

## Core Direction

- The project is **SwiFT-first but not SwiFT-locked**.
- SwiFT is tested first because it is the local lab backbone and can be modified.
- The first concrete artifact is a `Dataset x BFM x Task` master matrix.
- Current benchmark BFMs are SwiFT, Brain-JEPA, NeuroSTORM, and BrainLM.
- Logistic/ridge/ROI/voxel models are statistical floors, not the main Model
  Axis.
- Stimulus-only video/audio/text models, TRIBE v2, multimodal fusion, and
  movie/story pretraining are later branches selected after the BFM matrix is
  populated.
- If matched benchmark cells show that another BFM beats SwiFT, document the
  result and pivot.
- The real goal is to find which model, neural representation, target, and
  training objective best support emotion prediction and transferable affective
  representation.

## Canonical Data Basis

- Horikawa/Cowen canonical stimulus count: `2185`.
- Canonical local fMRI rows: `2185 stimuli x 5 subjects = 10925`.
- Local extra stimulus ids `2186-2196` are not the project definition.
- Old 5TR caches are reference only.
- Current manifest builder: `setup/code/build_horikawa_window_manifest.py`.

## Primary Tracks

| Track | Question | First implementation |
|---|---|---|
| A0 Master benchmark | Which Dataset x BFM x Task cells are runnable and informative? | `RUN`/`CHECK`/`NA` master matrix |
| A1 Frozen BFM comparison | Which BFM carries emotion signal under matched splits? | SwiFT, Brain-JEPA, NeuroSTORM, BrainLM |
| A2 Statistical floors | Are BFM scores above simple decoding floors? | logistic/ridge/ROI/voxel floors |
| B BFM development | What should be adapted or pretrained after evidence exists? | adapter/fine-tuning/pretraining only after A0-A2 |
| C Stimulus controls | How much of the target is stimulus-explained? | video/audio/text/TRIBE after BFM benchmark |
| D Affective AI extension | Can brain responses regularize affective LLM/VLM embeddings? | small adapter/distillation only after evidence |

## Brain Representation Candidates

- Whole-brain 4D volume: SwiFT, NeuroSTORM-style models.
- Parcel/ROI time series: Schaefer 400/600, Tian subcortex, HCP-MMP.
- Network-restricted models: visual, auditory, salience, DMN, limbic/subcortical,
  frontoparietal/control, attention networks.
- Voxel-weighted models: ridge, elastic-net, sparse linear models, stability
  selection, searchlight where feasible.
- Dynamic connectivity: sliding-window FC, temporal graph features.
- Subject-adapted representations: subject adapters, hyperalignment, SRM.
- Stimulus-aligned latents: fMRI aligned to video/audio/text/TRIBE features.

## Core Documents

| File | Role |
|---|---|
| `README.md`, `README_KR.md` | human entry points |
| `notes/benchmark_design.md` | canonical `Dataset x BFM x Task` master matrix |
| `Paper/framework_EN.md`, `Paper/framework_KR.md` | canonical project narrative |
| `Paper/methodology.md` | canonical experimental design |
| `reference/datasets.md` | dataset details: what each dataset is, target, risks, sources |
| `reference/task.md` | task/target inventory |
| `reference/code_resources.md`, `reference/papers.md` | BFM/model details: what each model is, input, risks, sources |
| `reference/training_strategy.md` | post-benchmark model and training strategy |
| `ACTION_PLAN.md` | current Korean execution plan |
| `notes/project_decisions.md` | durable decision log |
| `workflows/README.md` | operating workflows |

## Current Rule

Do not add redundant root markdown files. Merge durable narrative into
`Paper/framework_KR.md` / `Paper/framework_EN.md`, methods into
`Paper/methodology.md`, and active execution details into `ACTION_PLAN.md`.

## Workflow Triggers

| Trigger | Meaning |
|---|---|
| `[deep search]` | search literature, code, and datasets; update reference docs |
| `[experiment card]` | turn an idea into a structured experiment card |
| `[red team]` | critique a model, dataset, claim, or experiment plan |
| `[weekly status]` | summarize decisions, changes, blockers, and next actions |
| `[verification]` | check citations, paths, completeness, and overclaims |
