# NetFeeliX Pilot Benchmark Design

## Purpose

The pilot benchmark should determine which existing model and data ingredients are worth turning into a full NetFeeliX model. It is not meant to prove the final architecture immediately.

## Benchmark Axes

### Axis 1: Input source

| Condition | Input | Example |
|---|---|---|
| Brain-only | fMRI | SwiFT/BrainLM/Brain-JEPA/NeuroSTORM frozen features |
| Stimulus-only | video/audio/text | V-JEPA2, Whisper/Wav2Vec, captions/LLM |
| Brain + stimulus | fMRI + aligned stimulus features | TRIBE-style alignment |
| Brain dynamics | dynamic FC/time-series | Ke-style arousal baseline |

### Axis 2: Pretraining

| Condition | Meaning |
|---|---|
| Scratch | Train only on downstream emotion dataset |
| Existing BFM | Use pretrained fMRI model |
| HCP movie-pretrained | Continue/pretrain on HCP movie fMRI |
| Stimulus-aligned | Use stimulus-brain alignment loss |
| Emotion-supervised adapter | Small adapter trained on emotion targets |

### Axis 3: Target

| Target | Expected difficulty | Why |
|---|---|---|
| Arousal | Low-medium | Prior cross-dataset evidence |
| Valence | Medium-high | More context-dependent |
| Discrete emotion | High | Category structure and label ambiguity |
| Emotion intensity trajectory | High | Requires temporal alignment |
| High-dimensional vector | Highest | Main rich representation target |

## Minimal Pilot Experiments

### Pilot 0: Dataset inventory

Goal: know what is actually usable.

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
- REELMO,
- Affective Videos,
- NeuroEmo,
- Koide-Majima if accessible,
- CNeuroMod/Algonauts if realistic.

### Pilot 1: Simple baselines

Goal: establish the minimum bar.

Models:

- ridge/elastic-net on mean activation or parcellated time windows,
- dynamic FC arousal model,
- stimulus-only V-JEPA2/CLIP/audio/text feature regression.

### Pilot 2: Existing BFM frozen probes

Goal: test whether existing BFMs transfer at all.

Models:

- SwiFT,
- BrainLM,
- Brain-JEPA,
- NeuroSTORM if weights are available,
- SwiFUN if task-activation bridge is feasible.

Protocol:

- freeze encoder,
- train linear/ridge or small MLP head,
- same splits and metrics as simple baselines.

### Pilot 3: TRIBE-style stimulus-emotion baseline

Goal: test how much emotion can be predicted from stimulus features alone.

Model:

```text
video/audio/text features -> temporal fusion -> emotion head
```

Interpretation:

- If this is strong, stimulus semantics dominate some emotion targets.
- If this is weak but brain-only is strong, fMRI contains additional affective state information.
- If both are complementary, alignment model is justified.

### Pilot 4: First alignment test

Goal: test whether brain-stimulus alignment helps.

Model:

```text
fMRI encoder -> z_brain
stimulus encoder -> z_stim
loss = emotion_loss + lambda * alignment_loss(z_brain, z_stim)
```

Alignment choices:

- regression,
- contrastive matching,
- CKA/RSA alignment,
- JEPA-style latent prediction.

## Decision Rules

| Result | Next Strategy |
|---|---|
| Existing BFMs beat scratch | pursue adapter/fine-tuning |
| Existing BFMs weak | prioritize HCP movie pretraining |
| Stimulus-only strong | pursue TRIBE-style emotion model |
| Brain-only strong | focus on fMRI encoder and subject adaptation |
| Alignment improves high-dimensional target | develop bidirectional NetFeeliX |
| Only arousal works | focus on dynamics/physiology |
| Cross-dataset transfer fails | harmonize targets and improve pretraining |

## First Deliverable

A single table:

| Dataset | Target | Brain-only | Stimulus-only | Existing BFM | Alignment | Notes |
|---|---|---|---|---|---|---|

This table is the practical foundation for the next model decision.

