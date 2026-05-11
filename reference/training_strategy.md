# NetFeeliX Training Strategy

This document defines the model-development strategy. The default direction is **SwiFT-first but not SwiFT-locked**: SwiFT is the first brain backbone because it is the local lab model and can be modified, pretrained, fine-tuned, and inserted into multimodal systems. If evidence shows that SwiFT is not the right backbone for emotion representation, NetFeeliX should pivot rather than protect the initial choice.

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

The broader project question:

```text
Which neural representation, brain region weighting, model architecture, and
learning objective best support emotion prediction and transferable affective
representation from brain/stimulus data?
```

An additional core research question is now explicit:

```text
Which fMRI temporal window length should SwiFT use for emotion representation:
short event windows, longer context windows, pretrained sequence lengths, or
scratch-trained sequence lengths?
```

This matters because Horikawa is not a fixed 5TR-only problem. The current
local preprocessing contains variable-length stimulus-response windows, and the
old 5TR subset came from a legacy loader/split constraint. NetFeeliX should use
all valid windows when possible, and treat sequence length as a model variable
rather than a preprocessing accident.

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
| Emotion-labeled pretraining | supervised or weakly supervised multi-task learning on emotion fMRI | Horikawa, Emo-FilM, Affective Videos, IAPS fMRI, NeuroEmo | emotion labels, vectors, components, arousal/valence | tests whether target-aware pretraining improves held-out emotion transfer |
| Two-stage pretraining | naturalistic SSL followed by emotion-labeled multi-task pretraining | movie/story fMRI then emotion fMRI | SSL + supervised affect objectives | tests whether dynamics-first then emotion specialization is better |
| Emotion-specific head | replace generic classifier with multi-task affect head | all emotion datasets | arousal, valence, category, vector, appraisal | handles heterogeneous targets |
| Affective token | add learned affect query/token for pooled representation | Horikawa, Emo-FilM | emotion vector/component | tests explicit affect readout from 4D features |
| Subject adapter | subject embedding or subject-specific adapter | multi-subject datasets | same target | separates shared affect structure from individual variation |
| Multimodal brain module | use SwiFT as fMRI encoder inside dual encoder | Emo-FilM, HCP, Horikawa | alignment + emotion | connects fMRI dynamics with stimulus context |

## SwiFT Exit and Pivot Strategy

SwiFT should be tested seriously, but it should not be protected from negative
results. The project goal is emotion representation learning, not proving that
one backbone is always best.

### Continue SwiFT If

- frozen/adapted/pretrained SwiFT improves beyond simple brain baselines on
  valence, high-dimensional emotion vectors, or component/appraisal targets;
- sequence-length or padding fixes produce stable gains beyond arousal only;
- SwiFT latents show meaningful RSA/CKA alignment with emotion-rating geometry;
- SwiFT becomes useful as a brain module in alignment or multimodal models even
  if it is not the best standalone decoder.

### Deprioritize or Discard SwiFT If

- ROI/parcel ridge, voxel-weighted linear models, or dynamic FC baselines beat
  SwiFT under matched splits and targets;
- SwiFT gains are limited to arousal, motion/visual shortcuts, or subject/dataset
  leakage;
- padding/sequence-length sensitivity dominates the result and cannot be fixed
  cleanly;
- scratch temporal models, Brain-JEPA/NeuroSTORM/BrainLM, or stimulus-aligned
  models give stronger and more stable emotion representations;
- compute cost is high while transfer to held-out emotion datasets is weak.

If this happens, the SwiFT track becomes a documented negative result and the
main project pivots to the representation family that works: voxel/ROI/network
models, alternative BFMs, stimulus-brain alignment, or multimodal affective
models.

## Brain Representation Search Space

NetFeeliX should test which neural representation is useful for emotion rather
than assuming whole-brain 4D modeling is always optimal.

| Representation choice | Example method | Why test it |
|---|---|---|
| Whole-brain 4D volume | SwiFT, NeuroSTORM-style raw fMRI | preserves distributed spatiotemporal structure |
| Parcel/ROI time series | Schaefer/Tian, HCP-MMP, emotion/network ROIs | faster, less noisy, easier cross-dataset harmonization |
| Voxel-weighted decoding | ridge/elastic-net, sparse linear model, stability selection | identifies which voxels carry emotion target signal |
| Network-weighted decoding | visual, auditory, salience, DMN, limbic, control networks | tests whether emotion prediction is dominated by specific systems |
| Subject-adapted representation | subject embedding, hyperalignment, shared response model | separates shared affect structure from individual response geometry |
| Dynamic connectivity | sliding-window FC, temporal graph features | tests arousal/context dynamics not captured by local volume features |
| Stimulus-aligned latent | TRIBE/V-JEPA/audio/text aligned with fMRI | tests whether emotion is better represented as brain-stimulus shared structure |

Minimum comparison:

1. whole-brain SwiFT/NeuroSTORM;
2. parcel/ROI ridge or small temporal model;
3. voxel-weighted linear/sparse model;
4. network-restricted models;
5. stimulus-only and brain-stimulus aligned models.

The output should include both prediction performance and interpretability:
which regions, networks, time windows, and stimulus modalities explain the
emotion target.

## Sequence Length and Padding Strategy

SwiFT sequence length is not a minor implementation detail. It should be tested
as a first-class model-development variable.

### Main Question

```text
Does emotion representation improve with longer fMRI temporal context, and does
that benefit depend on whether SwiFT is pretrained, fine-tuned, or trained from
scratch at the same sequence length?
```

### Pretrained SwiFT Rule

If a SwiFT checkpoint was pretrained with sequence length 20 or 40, the safest
fine-tuning setup is to keep the same native sequence length. This avoids
changing temporal positional structure, patch-grid shape, window attention
geometry, and checkpoint-compatible tensor assumptions.

Shorter downstream windows can still be evaluated, but they should be framed as
explicit input-adaptation conditions:

| Condition | Meaning | Interpretation |
|---|---|---|
| pretrained SL20 -> downstream SL20 | native checkpoint-compatible fine-tuning | primary pretrained transfer condition |
| pretrained SL40 -> downstream SL40 | native checkpoint-compatible fine-tuning | primary long-context transfer condition if SL40 checkpoint exists |
| pretrained SL20 with 5/10TR observed windows | pad/mask/crop into SL20 | tests short-event adaptation, but padding strategy must be reported |
| pretrained SL40 with 5/10/20TR observed windows | pad/mask/crop into SL40 | tests whether long-context pretrained weights tolerate short events |
| pretrained checkpoint with resized/interpolated temporal parameters | architecture surgery | only valid if interpolation and output shapes are explicitly verified |

So the answer is: for clean pretrained fine-tuning, yes, sequence length should
normally match the pretraining sequence length. But mismatched downstream
windows can be tested as an adaptation question, not silently treated as the
same experiment.

### Scratch SwiFT Length Comparison

Scratch or from-random-initialization SwiFT gives a clean way to ask whether the
emotion task itself wants 5, 10, 20, or 40 TR context.

| Scratch condition | Why run it | What it can decide |
|---|---|---|
| SL5 | short event response, closest to old Horikawa subset | whether immediate evoked response is enough |
| SL10 | modest temporal context | whether extra post-stimulus dynamics help |
| SL20 | matches common SwiFT pretrained setup | fair comparison to pretrained SL20 |
| SL40 | long context / delayed dynamics | whether emotion benefits from extended temporal integration |

This comparison should be run with identical target construction, split logic,
metrics, and decoder head. Otherwise sequence length will be confounded with
preprocessing and optimization.

### Padding and Masking Rules

Padding is allowed only if it is logged as an experimental condition.

| Issue | Required treatment |
|---|---|
| observed window shorter than model SL | compare zero padding, repeat/edge padding, and valid-frame-aware pooling if supported |
| observed window longer than model SL | compare first-window, HRF-aligned window, center/window crop, and full-context model when possible |
| no attention mask support | report that padded frames participate in attention/pooling; add padding sensitivity control |
| model supports masks | pass the valid-frame mask through attention/pooling and verify it is actually used |
| pretrained temporal patch/window mismatch | do not claim native transfer unless checkpoint tensor compatibility is verified |

### Immediate Model-Setting Matrix

Before large extraction, run the same small smoke set for every model:

| Model | Required smoke tests |
|---|---|
| SwiFT pretrained | SL20 native, SL40 native if available, short-window padded into native SL, output shape and padding sensitivity |
| SwiFT scratch | SL5, SL10, SL20, SL40 from the same target/split setup |
| Brain-JEPA | actual ROI window length, crop/pad length, whether attention mask is passed and used |
| NeuroSTORM | actual 4D window length, crop/pad length, whether pooled embedding includes padded frames |
| TRIBE v2 | stimulus duration/segment coverage, HRF lag, predicted cortical response length, alignment with fMRI windows |

The first NetFeeliX decoding result should therefore be a length-aware screening
benchmark, not a single frozen-embedding rerun.

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

Pretraining is a data-choice question, not only an HCP movie question. Compare
three families:

1. naturalistic self-supervised pretraining,
2. emotion-labeled supervised or weakly supervised pretraining,
3. two-stage naturalistic-to-emotion pretraining.

Use HCP movie first for naturalistic self-supervision, then other movie/story
fMRI data only when the dataset choice follows the hypothesis:

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

For emotion-labeled pretraining, use direct affective targets as supervised or
weakly supervised objectives:

- Horikawa: high-dimensional emotion vector and affect geometry.
- Emo-FilM: component/appraisal, arousal/valence, physiology-linked targets.
- Affective Videos: arousal/valence sanity target.
- IAPS fMRI: valence category and beta-map adaptation.
- NeuroEmo: discrete/category or dimensional emotion target, depending on access.

Important control: do not pretrain and evaluate on the same samples as the main
claim. Emotion-labeled pretraining matters only if it improves held-out dataset
transfer, such as Horikawa to Emo-FilM, Emo-FilM to Horikawa, or mixed
emotion-dataset pretraining to a held-out target.

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
- If simple voxel/ROI/network baselines consistently beat SwiFT under matched
  conditions, deprioritize SwiFT and make neural-representation discovery the
  main track.

### Stage 2: Pretraining Source Comparison

Goal: decide whether SwiFT should first learn stimulus-locked naturalistic fMRI
dynamics, emotion-label-aware affect structure, or a two-stage curriculum.

Run:

1. naturalistic SSL pretraining with masked fMRI modeling,
2. naturalistic temporal contrastive or JEPA/future latent prediction,
3. emotion-labeled multi-task pretraining on affective fMRI datasets,
4. two-stage naturalistic SSL followed by emotion-labeled multi-task pretraining,
5. optional stimulus-conditioned prediction with visual/audio/text features.

Evaluate:

- transfer to Horikawa,
- transfer to Emo-FilM,
- transfer to held-out emotion datasets when feasible,
- arousal/valence sanity checks,
- high-dimensional/component target transfer,
- low-level feature controls,
- feature geometry with emotion ratings.

Decision:

- If HCP-style pretraining helps across Horikawa and Emo-FilM, scale 4D SwiFT
  continued pretraining.
- If emotion-labeled pretraining improves held-out emotion transfer, scale
  multi-dataset affective pretraining and task-specific heads.
- If two-stage pretraining beats either source alone, prioritize curriculum
  learning: naturalistic dynamics first, emotion-specific specialization second.
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
