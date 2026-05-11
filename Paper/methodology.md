# NetFeeliX Methodology Plan

## Overview

The methodology is organized around **SwiFT-first but not SwiFT-locked, screening-benchmark-driven model development**. Before claiming a mature emotion-aware foundation model, NetFeeliX should build a harmonized benchmark surface across datasets, targets, brain representations, and model families. Every model should be evaluated with comparable splits, target definitions, and metrics.

The practical goal for the first two months is:

```text
dataset/model inventory -> lightweight baselines -> frozen/adapted SwiFT probes
    -> stimulus-only and alignment baselines -> decision on model-development track
```

## Phase 0: Dataset and Model Inventory

Phase 0 answers what can actually be run. It should produce one table with dataset access, fMRI format, stimulus availability, annotation type, preprocessing burden, and first target.

| Dataset | Role | First target | First action |
|---|---|---|---|
| HCP 7T movie | naturalistic pretraining | masked/future fMRI objective | confirm local files, parcellation, run metadata |
| Horikawa/Cowen | core downstream | high-dimensional emotion vector | confirm OpenNeuro format, labels, video timing |
| Emo-FilM | modern downstream | emotion/appraisal/component ratings | check access, temporal annotations, physiology |
| Affective Videos ds000205 | lightweight downstream | valence/arousal | run simple ROI/ridge/SwiFT-head baseline |
| IAPS fMRI NeuroVault | lightweight downstream | positive/neutral/negative beta maps | test beta-map valence category adaptation |
| NSD | static-image fMRI extension | pseudo-affective image labels | evaluate image-based fMRI affect transfer |
| OASIS | stimulus label source | valence/arousal norms | calibrate image affect pseudo-labels |
| REELMO | stimulus-side affect supervision, fMRI subset | time-resolved affect reports | check fMRI subset access and annotation format |
| NeuroEmo | downstream/cross-cultural | emotion labels | inspect OpenNeuro metadata and task labels |
| Koide-Majima | high-dimensional benchmark | 80 emotion labels | check data access feasibility |
| CNeuroMod/Algonauts | auxiliary encoding/alignment | fMRI response prediction | inspect TRIBE/Algonauts pipeline |
| BOLD Moments | auxiliary short-video encoding | video event response | check fit for stimulus-brain alignment |

Model inventory should similarly record:

| Model/resource | Native direction | First NetFeeliX use |
|---|---|---|
| SwiFT | fMRI -> representation | frozen/adapted emotion head |
| SwiFUN | rsfMRI -> task activation | resting-to-task/emotion bridge |
| BrainLM | fMRI time series -> representation | frozen probe if weights load |
| Brain-JEPA | fMRI -> latent prediction | objective reference and probe if available |
| NeuroSTORM | raw 4D fMRI -> representation | high-value BFM baseline if accessible |
| TRIBE/TRIBE v2 | stimulus -> fMRI | stimulus feature fusion, fMRI encoding, alignment |
| V-JEPA2/CLIP/VideoMAE | video -> representation | stimulus-only emotion baseline |
| Whisper/Wav2Vec | audio -> representation | audio-side stimulus baseline |
| LLM/sentence transformer | text -> representation | subtitle/caption affective baseline |

## Phase 1: Screening Benchmark Matrix

The screening benchmark should compare model interfaces and temporal-window
conditions rather than one native architecture against another.

| Interface | Input | Example model | Output | Main question |
|---|---|---|---|---|
| Brain-only baseline | fMRI | ROI/ridge, dynamic FC, temporal MLP | emotion | How much emotion signal is in simple brain features? |
| SwiFT-first BFM probe | fMRI | SwiFT, then BrainLM/Brain-JEPA/NeuroSTORM if usable | emotion | Can SwiFT be made emotion-specific? |
| Stimulus-only baseline | video/audio/text | V-JEPA2, CLIP, Whisper, LLM, TRIBE fusion | emotion | How much emotion is explained by stimulus features alone? |
| Alignment model | fMRI + stimulus during training | fMRI encoder + stimulus encoder | emotion + alignment | Does brain-stimulus alignment improve representation? |

Temporal-window conditions are part of the benchmark, not a preprocessing
footnote:

| Condition | Main use | Required logging |
|---|---|---|
| all observed windows | use all valid Horikawa/Emo-FilM windows when supported | observed frame count, HRF alignment, target timing |
| SL5 | short event-level response | padding/crop method if model expects longer input |
| SL10 | modest post-stimulus context | same split and target as SL5/20/40 |
| SL20 | checkpoint-native condition for common SwiFT setups | checkpoint name, temporal patch/window config |
| SL40 | long-context condition and possible native condition for SL40 SwiFT | checkpoint name or scratch initialization |

For pretrained SwiFT, the checkpoint-native SL is the clean transfer condition.
For mismatched downstream windows, padding/cropping/masking must be treated as
an explicit adaptation experiment. For scratch SwiFT, SL5/SL10/SL20/SL40 should
be compared directly under matched splits and objectives.

Minimum result table:

| Dataset | Target | Brain-only | Stimulus-only | Existing BFM | Alignment | Notes |
|---|---|---|---|---|---|---|
| Horikawa | high-dimensional emotion vector | planned | planned | planned | planned | primary benchmark |
| Emo-FilM | component/appraisal/emotion ratings | planned | planned | planned | planned | naturalistic downstream |
| Affective Videos | valence/arousal | planned | optional | planned | optional | fast sanity check |
| REELMO | time-resolved affect reports | optional | planned | fMRI subset optional | optional | stimulus-side supervision |
| HCP 7T movie | pretraining objective | planned | planned features | planned | planned | pretraining source |

## Phase 1B: Reasoning and Context Benchmark

Horikawa should be used as a high-dimensional affect geometry benchmark, not as the main reasoning/context dataset. The reasoning/context benchmark should use naturalistic datasets and stimulus-side MLLM outputs.

Inputs:

- short-window stimulus features: frame/audio/subtitle features around the current TR,
- long-window stimulus features: preceding scene or narrative context,
- MLLM-derived affective outputs: emotion caption, cue-emotion QA, rationale, appraisal-like dimensions, hallucination flags,
- brain features: fMRI windows aligned to the same segment.

Benchmark comparisons:

| Comparison | Purpose |
|---|---|
| short-window vs long-window stimulus-only | Does temporal context improve affective prediction? |
| label-only vs rationale-embedding supervision | Do richer affective targets improve representation? |
| brain-only vs stimulus-only vs aligned | Does fMRI add information beyond stimulus context? |
| MLLM rationale alignment vs emotion-label alignment | Does brain latent align with "why" representations or only labels? |
| context ablation | Which modalities or preceding context drive the prediction? |

First feasible implementation:

1. Run Horikawa as the high-dimensional emotion-vector probe.
2. Run Emo-FilM or REELMO as the context-aware naturalistic benchmark.
3. Generate or collect stimulus-side emotion captions/rationales with a frozen affective VLM/LLM where feasible.
4. Embed rationales with a sentence/LLM encoder and train lightweight alignment heads.
5. Report whether context/rationale embeddings improve emotion prediction or only stimulus-side explanation quality.

Do not claim fMRI can produce reliable natural-language emotional reasoning in the first study. The first claim should be weaker and testable: context/rationale embeddings may improve or organize brain-stimulus-emotion representations.

## Brain-Only Baselines

Purpose: establish the minimum bar before expensive models and identify which
neural representation carries emotion-relevant signal.

Models:

- ridge/elastic-net from parcel or ROI summary features,
- voxel-wise ridge/elastic-net with stability selection,
- network-restricted models for visual, auditory, salience, DMN, limbic, and
  control networks,
- PCA/ICA features with linear heads,
- dynamic functional connectivity CPM-style arousal/valence prediction,
- small temporal MLP/TCN/Transformer trained from scratch.

Targets:

- arousal and valence when available,
- discrete or multi-label emotion category,
- high-dimensional emotion rating vector.

Evaluation:

- leave-subject-out where possible,
- leave-stimulus or leave-movie-out when stimulus generalization matters,
- subject-wise metrics with bootstrap confidence intervals.
- region/network importance and stability across folds.

## Existing BFM Transfer

Purpose: test whether generic pretrained fMRI representations already contain emotion-relevant information.

Protocol:

1. **Frozen probe**
   - Freeze encoder.
   - Train ridge, linear, or shallow MLP head.
   - Use as the first fair comparison.

2. **Adapter tuning**
   - Freeze most of the encoder.
   - Train small adapters, subject embeddings, LoRA-style modules if supported.
   - Prefer this over full fine-tuning on small datasets.

3. **Partial/full fine-tuning**
   - Use only after frozen probes and adapters are stable.
   - Require strict validation, early stopping, and subject/stimulus split documentation.

Decision rule:

- If BFM probes beat non-deep baselines on arousal only, keep BFM as a sanity baseline.
- If BFM probes beat baselines on valence or high-dimensional targets, prioritize adapter/fine-tuning.
- If BFM probes fail broadly, prioritize naturalistic movie/story pretraining or stimulus-brain alignment.
- If voxel/ROI/network baselines beat SwiFT under matched splits, deprioritize
  SwiFT and focus on neural-representation search or alternative architectures.

## Naturalistic Movie/Story Pretraining

Purpose: test whether stimulus-locked naturalistic fMRI pretraining helps
emotion transfer beyond resting-state or generic BFM transfer.

This is not based on the loose claim that movie-watching is simply better than
rest. The concrete rationale is that affective responses in Horikawa, Emo-FilM,
and related tasks are driven by visual, auditory, language, social, and
narrative cues that unfold over time. Naturalistic pretraining is useful only if
it improves transfer to direct emotion targets.

Initial representation:

- Start with parcellated or downsampled time series for speed.
- Move to raw 4D volume only after a stable parcel-level pipeline exists.

Dataset choice:

| Source | Role | Required check |
|---|---|---|
| HCP 7T movie | first large-subject continued pretraining source | transfer to Horikawa/Emo-FilM |
| CNeuroMod / Algonauts | multimodal video/audio/transcript alignment | stimulus-to-fMRI and OOD movie encoding |
| StudyForrest | long-film continuity | short-window vs long-window transfer |
| Narratives | language/story context without vision | context alignment without visual shortcuts |
| 101 Dalmatians | modality-control movie fMRI | vision-only/audio-only/audiovisual ablation |

Candidate objectives:

- masked segment reconstruction,
- temporal contrastive learning,
- JEPA-style latent prediction,
- future brain-state prediction,
- subject-invariant contrastive learning,
- optional stimulus-conditioned prediction when movie features are available.

Pretraining outputs:

- encoder checkpoint,
- frozen embeddings for downstream probes,
- training/validation loss curves,
- metadata table with subject, run, TR, movie, acquisition direction, and split.

Decision rule:

- If naturalistic pretraining improves Horikawa or Emo-FilM transfer over generic BFMs, scale Track B.
- If gains are limited to low-level visual/audio features or arousal, add
  modality and shortcut controls before claiming emotion representation.
- If it only improves fMRI reconstruction but not emotion transfer, treat it as an auxiliary representation source.
- If it overfits or fails at parcel level, do not move to raw 4D volume yet.

## Stimulus-Only and Alignment Models

Purpose: test whether emotion representation improves when fMRI is aligned with video/audio/text stimulus dynamics.

Stimulus-only baselines:

- video: V-JEPA2, VideoMAE, CLIP frame features,
- audio: Wav2Vec2/Wav2Vec-BERT, Whisper, spectrogram baseline,
- text: subtitles/captions with sentence-transformer or LLM embeddings,
- fusion: TRIBE-style temporal transformer over video/audio/text features.

Alignment models:

```text
z_brain = fMRI_encoder(fMRI window)
z_stim  = stimulus_encoder(video/audio/text window)

loss = emotion_loss(z_brain)
     + optional emotion_loss(z_stim)
     + alignment_loss(z_brain, z_stim)
     + optional fMRI_prediction_loss(z_stim)
```

Candidate alignment losses:

- regression from stimulus latent to brain latent,
- contrastive matching between synchronized brain and stimulus windows,
- CKA/RSA geometry matching,
- JEPA-style latent prediction across brain and stimulus views,
- fMRI response prediction with HRF-aware lag.

Decision rule:

- If stimulus-only is strong but brain-only is weak, prioritize brain-tuned affective VLM/LLM or stimulus-brain alignment.
- If alignment improves high-dimensional emotion targets, prioritize Track C.
- If alignment improves only fMRI encoding but not emotion, keep it as auxiliary pretraining rather than the main emotion model.

## Brain-Tuned Affective LLM/VLM Track

Purpose: connect affective computing foundation models with brain-grounded emotion representation.

This is not the first expensive experiment. It becomes active when screening benchmarks show either strong stimulus-side affective features or measurable brain-stimulus alignment.

Feasible variants:

1. **Brain-aligned affective adapter**
   - Freeze VLM/LLM.
   - Train small adapter from affective embedding to fMRI latent or emotion target.

2. **Brain-regularized emotion classifier**
   - Train emotion classifier with label loss plus brain-geometry alignment loss.

3. **Shared latent distillation**
   - Train a joint stimulus-brain latent.
   - Distill it into a lightweight affective embedding usable without fMRI at inference.

4. **Brain-informed pseudo-labeling**
   - Use fMRI-derived arousal or high-dimensional emotion estimates as auxiliary supervision for ambiguous movie segments.

Risk control:

- Do not full fine-tune an LLM/VLM on small fMRI data.
- Keep adapters small.
- Evaluate whether brain alignment improves affective targets, not just fMRI prediction.

## Fine-Tuning and Split Policy

Splits must be documented before running model comparisons.

Recommended split hierarchy:

1. leave-subject-out for subject generalization,
2. leave-stimulus or leave-movie-out for content generalization,
3. within-subject repeated-stimulus split only for diagnostic analyses,
4. cross-dataset transfer when compatible targets exist.

Fine-tuning order:

1. frozen probe,
2. adapter tuning,
3. partial fine-tuning,
4. full fine-tuning only when justified.

Subject adaptation should be explicit:

- no subject adapter,
- subject embedding,
- small subject-specific adapter,
- population model plus subject calibration.

## Metrics

### Regression Targets

- Pearson r,
- Spearman r,
- MAE/MSE,
- explained variance,
- noise-ceiling-normalized correlation when available.

### Classification or Multi-Label Targets

- macro F1,
- AUROC,
- balanced accuracy,
- top-k accuracy,
- calibration metrics if probabilistic outputs are used.

### Representation Targets

- RSA correlation between predicted and observed emotion spaces,
- CKA between model representations and emotion rating embeddings,
- clip/time-window retrieval accuracy,
- cross-dataset representation transfer.

### fMRI Encoding Targets

- parcel-wise or voxel-wise correlation,
- subject-wise average score,
- noise-ceiling-normalized score where possible,
- HRF-lag sensitivity.

## Ablations

- resting/generic BFM transfer vs naturalistic movie/story pretraining,
- masked modeling vs JEPA vs contrastive pretraining,
- brain-only vs stimulus-only vs aligned model,
- no HRF lag vs fixed lag vs learned lag,
- subject-agnostic vs subject-adapted model,
- arousal/valence vs discrete categories vs high-dimensional emotion vectors,
- frozen stimulus features vs trainable fusion module.

## Initial Setup Experiments

The initial setup experiments should avoid expensive training and answer four questions:

1. Which datasets and targets are actually usable?
2. What do simple brain-only and stimulus-only baselines achieve?
3. Which pretrained BFMs can be loaded and probed?
4. Which target is most stable: arousal, valence, discrete categories, or high-dimensional emotion vectors?

Expected setup outputs:

- dataset inventory table,
- target construction notes,
- baseline metric table,
- failed/blocked resource list,
- recommendation for Track A, B, C, or D.
