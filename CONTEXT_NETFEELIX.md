# NetFeeliX Project Context

This is the compact single source of truth for NetFeeliX. Agent memory files
should point here so the project framing survives context compaction.

## Canonical Framing

NetFeeliX is a **SwiFT-first emotion-specific fMRI representation learning
project**.

It asks:

```text
How can SwiFT be adapted, pretrained, or aligned with multimodal stimulus models
to improve emotion representation learning and inference from fMRI?
```

Do not overclaim a completed "emotion foundation model" until pretraining and
transfer evidence exists. Prefer:

- emotion-specific brain representation model,
- emotion-aware fMRI foundation-model strategy,
- SwiFT-based emotion representation learning framework.

## Non-Negotiable Direction

- SwiFT is the default brain backbone.
- TRIBE v2 is not a replacement for SwiFT. It is a multimodal
  stimulus-to-brain teacher, stimulus baseline, and alignment module.
- HCP 7T movie is the main naturalistic fMRI continued-pretraining source.
- Horikawa is a high-dimensional affect geometry task, not a reasoning dataset.
- Emo-FilM is the strongest naturalistic emotion/component/appraisal dataset.
- Emotion theory should only justify target design; model development is the
  center of gravity.

## Core Model Tracks

| Track | Question | First implementation |
|---|---|---|
| SwiFT transfer | Do generic fMRI features already help emotion targets? | frozen SwiFT + linear/ridge/MLP head |
| SwiFT adaptation | Which small model changes improve emotion specificity? | adapter, subject adapter, affective token, multi-task head |
| HCP movie pretraining | Does naturalistic fMRI pretraining improve transfer? | masked fMRI, contrastive, JEPA/future latent objectives |
| TRIBE-SwiFT alignment | Does stimulus context improve or regularize brain emotion representation? | dual encoder or teacher distillation |
| Affective LLM/VLM extension | Can richer affective semantics supervise brain latents? | rationale/cue/appraisal embeddings as auxiliary targets |

## Core Documents

| File | Role |
|---|---|
| `Paper/framework_EN.md` | canonical English framework and narrative |
| `Paper/framework_KR.md` | canonical Korean framework and narrative |
| `Paper/methodology.md` | experimental design and method details |
| `reference/datasets.md` | function-based dataset inventory |
| `reference/task.md` | task and target inventory |
| `reference/training_strategy.md` | SwiFT-first training strategy |
| `reference/systematic_reference_map.md` | literature map by conceptual role |
| `workflows/README.md` | operating system for AI-assisted research work |

## Trigger Phrases

Use these project-level triggers in natural language:

| Trigger | Meaning |
|---|---|
| `[deep search]` | search recent literature, code, and datasets; update reference docs |
| `[experiment card]` | turn an idea into a structured experiment card |
| `[red team]` | critique a model/dataset/claim from multiple reviewer perspectives |
| `[weekly status]` | summarize decisions, changes, blockers, and next actions |
| `[verification]` | check citations, paths, completeness, and overclaims |

## Reviewer Personas

Use these personas for red-team/blue-team review:

- fMRI methods reviewer,
- affective neuroscience reviewer,
- ML foundation-model reviewer,
- data/compute feasibility reviewer,
- skeptical PI deciding what can be done in two months.

## Current Two-Month Target

The immediate target is not a finished model paper. It is a decision-ready
research system:

1. runnable datasets and target definitions,
2. first baseline and SwiFT-probe results,
3. clear decision rules for SwiFT adaptation vs HCP pretraining vs TRIBE-SwiFT
   alignment,
4. documented failure modes and next model-development steps.
