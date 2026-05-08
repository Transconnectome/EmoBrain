# NetFeeliX Initial Benchmark Design

This note defines the benchmark axes and first decision table. Detailed dataset, task, and training strategy inventories live in:

- `reference/datasets.md`
- `reference/task.md`
- `reference/training_strategy.md`

## Purpose

The initial benchmark should determine which model and data ingredients are worth turning into a full NetFeeliX model. It is not meant to prove the final architecture immediately.

## Benchmark Axes

### Axis 1: Input Source

| Condition | Input | Example |
|---|---|---|
| Brain-only | fMRI | SwiFT frozen/adapted features |
| Stimulus-only | video/audio/text/image | TRIBE v2, V-JEPA2, CLIP, Whisper/Wav2Vec, captions/LLM |
| Brain + stimulus | fMRI + aligned stimulus features | SwiFT + TRIBE v2/stimulus encoder |
| Brain dynamics | dynamic FC/time-series | Ke-style arousal baseline |

### Axis 2: Pretraining and Adaptation

| Condition | Meaning |
|---|---|
| Scratch | train only on downstream emotion dataset |
| Frozen SwiFT | use pretrained SwiFT representation with small head |
| SwiFT adapted | add emotion head, adapter, subject embedding, or partial fine-tuning |
| HCP movie continued pretraining | continue SwiFT training on HCP movie fMRI |
| Stimulus-aligned | add TRIBE v2/stimulus-brain alignment loss |
| Emotion-supervised adapter | train a small emotion-specific module |

### Axis 3: Target

| Target | Expected difficulty | Why |
|---|---|---|
| Arousal | low-medium | often more robust across naturalistic datasets |
| Valence | medium-high | more context-dependent |
| Positive/neutral/negative | low-medium | useful for IAPS fMRI beta-map check |
| Discrete emotion | high | label ambiguity and category structure |
| Appraisal/component | high | bridges emotion labels and context |
| High-dimensional vector | highest | main Horikawa-style affect geometry task |

## Minimum Experiments

### Stage 0: Dataset and Target Readiness

Outputs:

- dataset availability table,
- subject count,
- stimulus count/duration,
- target type,
- temporal resolution,
- preprocessing status,
- access burden,
- first-priority ranking.

Datasets:

- Horikawa,
- Emo-FilM,
- HCP 7T movie,
- Affective Videos,
- IAPS fMRI,
- REELMO,
- NeuroEmo,
- NSD/OASIS if static-image extension is useful,
- CNeuroMod/Algonauts if TRIBE-style engineering is needed.

### Stage 1: Simple Baselines

Goal: establish the minimum bar.

Models:

- ridge/elastic-net on mean activation or parcellated time windows,
- dynamic FC arousal/valence model,
- stimulus-only V-JEPA2/CLIP/audio/text/image feature regression.

### Stage 2: SwiFT Emotion-Specific Benchmarks

Goal: test whether SwiFT can become emotion-specific.

Models:

- frozen SwiFT + linear/ridge/MLP head,
- SwiFT + emotion-specific multi-task head,
- SwiFT + subject adapter,
- SwiFT + adapter or late-block fine-tuning.

### Stage 3: HCP Movie Continued Pretraining

Goal: test whether naturalistic fMRI pretraining improves emotion transfer.

Objectives:

- masked fMRI modeling,
- temporal contrastive learning,
- JEPA/future latent prediction,
- subject-invariant learning.

### Stage 4: TRIBE v2 / Stimulus Alignment

Goal: test whether stimulus-brain alignment helps emotion representation.

Model:

```text
fMRI    -> SwiFT encoder          -> z_brain
stimuli -> TRIBE v2/stim encoder -> z_stim

loss = emotion_loss
     + alignment_loss(z_brain, z_stim)
     + optional fMRI_encoding_loss
```

Alignment choices:

- regression,
- contrastive matching,
- CKA/RSA alignment,
- JEPA-style cross-view prediction,
- retrieval between synchronized windows.

## First Decision Matrix

| Candidate experiment | Dataset | Model | Task | Decision it answers |
|---|---|---|---|---|
| Setup-A | IAPS fMRI or Affective Videos | ridge/dynamic FC/SwiFT head | valence/arousal/category | what is the fastest emotion baseline? |
| Setup-B | Horikawa | SwiFT frozen/adapted head | high-dimensional emotion vector | can SwiFT capture affect geometry? |
| Setup-C | HCP 7T movie -> Horikawa/Emo-FilM | SwiFT continued pretraining | pretrain then probe | does naturalistic fMRI pretraining help? |
| Setup-D | Emo-FilM | SwiFT vs stimulus-only | component/appraisal/emotion ratings | which source explains naturalistic affect? |
| Setup-E | REELMO or Emo-FilM | stimulus-only + MLLM rationale embeddings | context/rationale target | is context useful as auxiliary supervision? |
| Setup-F | Horikawa or Emo-FilM | SwiFT + TRIBE v2 dual encoder | contrastive/regression alignment | does alignment improve emotion representation? |

## Decision Rules

| Result | Next strategy |
|---|---|
| SwiFT frozen/adapted beats simple baselines | prioritize SwiFT emotion heads and adapters |
| SwiFT weak but HCP continued pretraining helps | scale naturalistic fMRI pretraining |
| stimulus-only strong | use TRIBE v2/stimulus encoders as teacher or auxiliary path |
| brain-only strong | focus on SwiFT architecture and subject adaptation |
| alignment improves high-dimensional target | develop dual-encoder NetFeeliX |
| only arousal/category works | focus on dynamics and simple affective targets first |
| cross-dataset transfer fails | harmonize targets and improve pretraining/adaptation |

## First Deliverable

A single result table:

| Dataset | Target | Simple baseline | SwiFT frozen | SwiFT adapted | Stimulus-only | Alignment | Notes |
|---|---|---|---|---|---|---|---|

This table is the practical foundation for deciding the first NetFeeliX model.
