# NetFeeliX Training Strategy

This document defines the model-development strategy. The default direction is **SwiFT-first**: SwiFT is the primary brain backbone because it is the local lab model and can be modified, pretrained, fine-tuned, and inserted into multimodal systems.

## Core Position

NetFeeliX should not overclaim a complete emotion foundation model at the current stage. Use one of these phrases instead:

- emotion-specific brain representation model,
- emotion-aware fMRI foundation-model strategy,
- SwiFT-based emotion representation learning framework,
- brain-stimulus alignment model for affective representation learning.

The core question:

```text
How can SwiFT be adapted, pretrained, or combined with multimodal stimulus models
to improve emotion representation learning and inference from fMRI?
```

## Why Naturalistic Movie/Story Pretraining Belongs Here

Naturalistic pretraining is not included because movie-watching is automatically
better than resting-state. The reason is a model-development hypothesis:

```text
Emotion downstream datasets are small, but many affective targets are driven by
time-varying visual, auditory, language, social, and narrative cues. SwiFT may
need stimulus-locked fMRI pretraining before emotion-specific fine-tuning.
```

This hypothesis must be tested, not assumed. A naturalistic-pretrained SwiFT is
useful only if it improves transfer to direct emotion targets such as Horikawa,
Emo-FilM, Affective Videos, IAPS fMRI, or NeuroEmo.

The main failure modes are also explicit:

- the model may learn low-level motion, luminance, scene cuts, audio energy, or
  speech onset;
- it may learn generic arousal/attention rather than rich emotion geometry;
- it may improve stimulus reconstruction without improving brain-to-emotion
  inference;
- it may overfit a dataset-specific movie distribution.

Therefore every naturalistic pretraining run should have controls:

| Control | Purpose |
|---|---|
| resting/generic SwiFT vs naturalistic-pretrained SwiFT | test whether naturalistic fMRI adds transfer value |
| low-level stimulus feature controls | detect visual/audio shortcuts |
| vision-only/audio-only/text-only ablations | identify which modality carries transfer |
| stimulus-only baseline | test whether labels are explained without brain data |
| high-dimensional/component targets | avoid claiming success from arousal alone |

## SwiFT-First Strategy

| Strategy | What changes | Dataset | Target | Why it matters |
|---|---|---|---|---|
| Frozen SwiFT probe | freeze SwiFT, train linear/ridge/MLP head | Horikawa, Emo-FilM, Affective Videos, IAPS fMRI | emotion target | minimum BFM transfer baseline |
| Adapter tuning | freeze most SwiFT blocks, train small adapters | Horikawa, Emo-FilM | emotion/appraisal targets | sample-efficient emotion specialization |
| Partial fine-tuning | unfreeze late SwiFT stages or temporal blocks | Horikawa, Emo-FilM | high-dimensional emotion vector | tests where emotion-specific changes are needed |
| Naturalistic continued pretraining | continue SSL on movie/story fMRI | HCP 7T movie, CNeuroMod, StudyForrest, Narratives | masked/contrastive/JEPA objective | tests whether stimulus-locked dynamics improve emotion transfer |
| Emotion-specific head | replace generic classifier with multi-task affect head | all emotion datasets | arousal, valence, category, vector, appraisal | handles heterogeneous targets |
| Affective token | add learned affect query/token for pooled representation | Horikawa, Emo-FilM | emotion vector/component | tests explicit affect readout from 4D features |
| Subject adapter | subject embedding or subject-specific adapter | multi-subject datasets | same target | separates shared affect structure from individual variation |
| Multimodal brain module | use SwiFT as fMRI encoder inside dual encoder | Emo-FilM, HCP, Horikawa | alignment + emotion | connects fMRI dynamics with stimulus context |

## SwiFT Architecture Modification Options

### A. Readout-Level Changes

Use these first because they are lowest risk.

- Linear/ridge head on frozen features.
- MLP emotion head.
- Multi-task head with separate outputs for arousal, valence, categories, high-dimensional vectors, and appraisal/component ratings.
- Attention pooling over time and/or spatial windows.
- Dataset-specific output heads with shared SwiFT backbone.

### B. Parameter-Efficient Emotion Adaptation

Use when frozen features are nontrivial but insufficient.

- Adapters after selected SwiFT blocks.
- LoRA-style updates on attention projections where implementation is feasible.
- Subject embeddings added to pooled features.
- Small domain adapters for dataset identity or stimulus type.

### C. Pretraining Objective Changes

Use HCP movie first, then other naturalistic movie/story fMRI data only when the
dataset choice follows the hypothesis:

- HCP 7T movie: large-subject stimulus-locked pretraining.
- CNeuroMod/Algonauts: multimodal stimulus-to-brain alignment.
- StudyForrest: long-film continuity and audiovisual narrative.
- Narratives: language/story context without visual cues.
- 101 Dalmatians: visual/auditory/audiovisual modality control.

- Masked fMRI segment modeling.
- Temporal contrastive learning across augmented windows.
- JEPA-style future latent prediction.
- Subject-invariant contrastive learning.
- Stimulus-conditioned prediction if stimulus features are aligned.

### D. Emotion-Specific Latent Structure

Use after a stable benchmark exists.

- Emotion prototype contrastive loss.
- CKA/RSA loss to emotion rating geometry.
- Cross-dataset affect geometry matching.
- Affective-token attention analysis.
- Auxiliary physiology prediction for Emo-FilM/Spacetop if available.

## TRIBE v2 Usage Strategy

TRIBE v2 is not a replacement for SwiFT. It is a multimodal stimulus-to-brain component that can provide stimulus features, predicted brain responses, and teacher signals.

| Use mode | Input | Output | NetFeeliX role |
|---|---|---|---|
| Frozen teacher | video/audio/text | predicted fsaverage5 cortical response | compare predicted brain response with observed fMRI/emotion |
| Stimulus-only baseline | video/audio/text features | emotion target | test how much emotion is stimulus-explained |
| Teacher distillation | TRIBE-predicted brain map/latent | SwiFT latent or response target | transfer stimulus-brain structure into fMRI encoder |
| Dual encoder | TRIBE stimulus latent + SwiFT fMRI latent | shared latent | build brain-stimulus-emotion representation |
| Auxiliary encoding loss | stimulus features | fMRI response | regularize emotion training with brain response prediction |

TRIBE v2 implementation facts to remember:

- It combines LLaMA 3.2 text, V-JEPA2 video, and Wav2Vec-BERT audio features.
- It predicts fMRI responses to naturalistic video/audio/text.
- Predictions are on fsaverage5 cortical mesh, roughly 20k vertices.
- It uses hemodynamic lag handling; documentation notes a 5-second offset.
- Code/weights are available through GitHub/HuggingFace.
- License is CC-BY-NC-4.0, so reuse must respect non-commercial constraints.

Source: https://github.com/facebookresearch/tribev2

## Surface/Volume Alignment Problem

SwiFT is naturally a 4D volume model, while TRIBE v2 predicts cortical-surface responses. This mismatch should be handled explicitly.

Options:

1. **Common parcellation**
   - Project both observed fMRI and TRIBE predictions into a shared parcel space.
   - Best first choice for fast experiments.

2. **Surface projection**
   - Project fMRI volumes to fsaverage/fsaverage5 where preprocessing supports it.
   - Best for direct TRIBE v2 comparison.

3. **Volume approximation**
   - Map TRIBE surface predictions back to volume only if projection tools are reliable.
   - Higher risk, not first choice.

4. **Latent-only alignment**
   - Avoid direct voxel/vertex matching.
   - Align pooled SwiFT latents with pooled TRIBE/stimulus latents using contrastive or regression losses.

Default: start with common parcellation or latent-only alignment.

## Training Stages

### Stage 0: Feasibility Benchmark

Goal: establish runnable data, labels, and baseline metrics.

Run:

1. dataset inventory,
2. fMRI target construction,
3. ridge/dynamic FC baseline,
4. frozen SwiFT probe,
5. stimulus-only baseline if features are easy.

### Stage 1: SwiFT Emotion Adaptation

Goal: make SwiFT emotion-specific without changing the whole architecture.

Run:

1. frozen SwiFT + linear/MLP head,
2. emotion-specific multi-task head,
3. subject adapter,
4. adapter tuning or late-block fine-tuning.

Decision:

- If frozen SwiFT works, prioritize adapters and task-specific heads.
- If frozen SwiFT fails but simple baselines work, revisit preprocessing/target construction.
- If all fMRI models are weak but stimulus models are strong, prioritize alignment.

### Stage 2: Naturalistic Movie/Story Continued Pretraining

Goal: test whether shifting SwiFT toward stimulus-locked naturalistic fMRI
dynamics improves transfer to direct emotion targets.

Run:

1. masked fMRI modeling,
2. temporal contrastive learning,
3. JEPA/future latent prediction,
4. subject-invariant learning,
5. optional stimulus-conditioned prediction with visual/audio/text features.

Evaluate:

- transfer to Horikawa,
- transfer to Emo-FilM,
- arousal/valence sanity checks,
- high-dimensional/component target transfer,
- low-level feature controls,
- feature geometry with emotion ratings.

Decision:

- If HCP-style pretraining helps across Horikawa and Emo-FilM, scale 4D SwiFT
  continued pretraining.
- If it helps only visually dominated targets, treat it as visual naturalistic
  adaptation and add modality ablations.
- If CNeuroMod/Algonauts alignment helps more than brain-only pretraining,
  prioritize TRIBE-SwiFT shared latent work.
- If no naturalistic pretraining helps, prioritize emotion-specific heads,
  subject adapters, and target construction.

### Stage 3: TRIBE v2 + SwiFT Alignment

Goal: connect stimulus dynamics and fMRI dynamics.

Run:

```text
stimulus -> TRIBE v2 / stimulus encoder -> z_stim
fMRI     -> SwiFT brain encoder        -> z_brain

loss = emotion_loss(z_brain)
     + optional emotion_loss(z_stim)
     + alignment_loss(z_brain, z_stim)
     + optional fMRI_encoding_loss(z_stim)
```

Candidate alignment losses:

- regression,
- contrastive matching,
- CKA/RSA geometry alignment,
- JEPA-style cross-view prediction,
- retrieval loss between synchronized stimulus and brain windows.

### Stage 4: Context and Reasoning Extension

Goal: use affective LLM/VLM outputs as richer stimulus-side targets.

Run:

1. generate or collect emotion captions/rationales/cue labels,
2. embed rationales with sentence/LLM encoder,
3. align fMRI latents with label embeddings and rationale embeddings separately,
4. compare short-window vs long-window context.

Claim carefully:

- acceptable: context/rationale embeddings organize brain-stimulus-emotion representations,
- not acceptable yet: fMRI directly performs natural-language emotional reasoning.

## Default Model Comparison

| Condition | Brain input | Stimulus input | Backbone | Objective |
|---|---|---|---|---|
| Simple baseline | parcel/ROI | none | ridge/dynamic FC | emotion |
| SwiFT frozen | 4D fMRI | none | SwiFT | emotion |
| SwiFT adapted | 4D fMRI | none | SwiFT + adapter/head | emotion |
| SwiFT naturalistic-pretrained | movie/story-pretrained fMRI | none | SwiFT | SSL + emotion |
| Stimulus-only | none | video/audio/text/image | TRIBE v2 or encoders | emotion |
| TRIBE teacher | none | video/audio/text | TRIBE v2 | predicted fMRI + emotion |
| Dual encoder | 4D fMRI | video/audio/text | SwiFT + TRIBE/stimulus encoder | emotion + alignment |

## Immediate Recommendation

1. Use **SwiFT** as the default brain backbone.
2. Use **Horikawa** to test high-dimensional emotion geometry.
3. Use **Emo-FilM** to test naturalistic appraisal/component targets.
4. Use **HCP 7T movie first**, but treat CNeuroMod, StudyForrest, Narratives,
   and modality-control movie data as hypothesis-specific naturalistic sources.
5. Use **TRIBE v2** as stimulus-side teacher/alignment module, not as a replacement for the brain encoder.
6. Use **IAPS fMRI** or **Affective Videos** for fast valence/arousal/category checks.
7. Treat **NSD + OASIS/MLLM labels** as a strategic static-image extension, not the core story.
