# NetFeeliX Compact Context

This is the compact single source of truth for NetFeeliX. Agent-specific files
should point here rather than duplicating the full project narrative.

## Identity

NetFeeliX stands for:

```text
Neural nETwork For Emotion rEpresentation Learning and Inference in NeuroX
```

NetFeeliX is a **model-development project for emotion/affect representation
learning from fMRI and naturalistic stimuli**. It is not an emotion theory
project, and it should not claim to be a completed emotion foundation model
before pretraining and transfer evidence exists.

## Core Direction

- The project is **SwiFT-first but not SwiFT-locked**.
- SwiFT is tested first because it is the local lab backbone and can be modified.
- If matched benchmarks show that ROI/voxel/network baselines, another BFM, or
  stimulus-aligned models are better, document the negative result and pivot.
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
| A0 Neural representation search | Which brain representation matters? | ROI/parcel, voxel-weighted, network-restricted, dynamic FC |
| A1 SwiFT transfer/adaptation | Does SwiFT help emotion targets? | frozen/adapted/pretrained SwiFT under matched splits |
| A2 Temporal length | Which fMRI window length works? | all observed, SL5, SL10, SL20, SL40 |
| B Pretraining source | What should the model learn first? | naturalistic SSL vs emotion-labeled vs two-stage |
| C Stimulus-brain alignment | Does stimulus context improve brain emotion representation? | TRIBE/V-JEPA/audio/text + fMRI latent alignment |
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
| `Paper/framework_EN.md`, `Paper/framework_KR.md` | canonical project narrative |
| `Paper/methodology.md` | canonical experimental design |
| `reference/datasets.md` | dataset inventory |
| `reference/task.md` | task/target inventory |
| `reference/training_strategy.md` | model and training strategy |
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
