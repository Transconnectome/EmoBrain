# NetFeeliX: Research Overview for Team Discussion, Abstract, and Presentation

> **Purpose**: team-facing research overview for NetFeeliX.  
> **Use**: Teams post, abstract drafting, presentation outline, experiment planning.  
> **GitHub**: https://github.com/Transconnectome/NetFeeliX  
> **Last synced**: 2026-05-08  
> **Canonical docs**: `Paper/framework_KR.md`, `Paper/framework_EN.md`, `reference/datasets.md`, `reference/task.md`, `reference/training_strategy.md`

---

## 0. Executive Summary

**NetFeeliX** stands for:

```text
Neural nETwork For Emotion rEpresentation Learning and Inference in NeuroX
```

NetFeeliX is a **SwiFT-first model-development project** for emotion-aware fMRI
representation learning. The goal is not to immediately claim a completed
"Emotion Foundation Model." The goal is to build a rigorous experimental
framework that tells us how to make SwiFT and related fMRI models more
emotion-specific.

The central question is:

```text
How can we adapt, pretrain, or align SwiFT to learn better emotion-relevant
brain representations from fMRI?
```

The project starts from four linked observations:

1. **Affective computing is moving beyond simple emotion classification.**
   Modern emotion tasks include arousal/valence regression, multi-label emotion
   distributions, continuous affect trajectories, cue grounding, cause
   reasoning, and affective captioning.
2. **Existing brain foundation models are mostly generic.** Models such as
   SwiFT, BrainLM, Brain-JEPA, NeuroSTORM, and Omni-fMRI provide useful fMRI
   representations, but they are not usually optimized around emotion-specific
   representation learning.
3. **Emotion fMRI datasets are small and heterogeneous.** Horikawa, Emo-FilM,
   Affective Videos, IAPS fMRI, NeuroEmo, and related datasets differ in
   stimulus, target, temporal structure, and preprocessing. A single dataset
   score is not enough.
4. **Emotion during naturalistic experience is stimulus-linked and temporal.**
   Visual scenes, faces, body motion, voice, music, language, social cues, and
   narrative context unfold over time. Therefore, naturalistic movie/story fMRI
   and stimulus-to-brain alignment may be useful for emotion representation,
   but only if they transfer to direct emotion targets.

The working strategy is:

```text
initial benchmark -> SwiFT adaptation -> naturalistic pretraining ->
TRIBE/SwiFT alignment -> brain-tuned affective LLM/VLM extension
```

The immediate two-month target is a **decision-ready model-development roadmap**:

- Which datasets are actually runnable?
- Which emotion targets are stable?
- Does frozen SwiFT already transfer?
- Does naturalistic pretraining help beyond resting/generic SwiFT?
- Does stimulus-only prediction explain most emotion labels?
- Does brain-stimulus alignment improve high-dimensional emotion targets?
- Which model-development track should receive serious compute?

---

## 1. Background and Significance

### 1.1 Why Emotion Is Not Just One Label

In many machine-learning settings, emotion is treated as a classification task:

```text
image/video/audio/text -> anger / fear / joy / sadness / neutral / ...
```

This is useful as a starting point, but it is too narrow for fMRI emotion
representation learning. Real affective responses can be:

- dimensional: arousal, valence, dominance, intensity,
- categorical: fear, joy, sadness, disgust, anger, awe, etc.,
- multi-label: multiple emotions can co-occur,
- dynamic: affect changes over time during a film or narrative,
- componential: appraisal, motivation, expression, bodily response, feeling,
- contextual: a facial expression or scene can mean different things depending
  on story context,
- stimulus-dependent: visual, auditory, language, and social cues contribute
  differently.

Therefore, NetFeeliX should not ask only:

```text
Can fMRI classify emotion labels?
```

It should ask:

```text
Which model architecture and learning objective produce transferable
emotion-relevant brain representations across multiple target types?
```

### 1.2 Affective Computing Task Landscape

Affective computing has expanded beyond basic emotion recognition. The field now
uses a ladder of tasks:

| Task family | Typical output | Typical metric | NetFeeliX use |
|---|---|---|---|
| Sentiment / valence classification | positive, neutral, negative | accuracy, macro F1 | quick low-dimensional check |
| Discrete emotion classification | one emotion label | accuracy, balanced accuracy | basic baseline |
| Multi-label emotion prediction | multiple labels or probability vector | macro/micro F1, AUROC, KL/correlation | closest to high-dimensional emotion geometry |
| Dimensional affect regression | arousal, valence, dominance, intensity | Pearson r, Spearman r, CCC, MAE/MSE | first fMRI sanity ladder |
| Continuous-time affect tracking | frame/window-level affect trace | CCC, time-lagged correlation | relevant for Emo-FilM and REELMO |
| Emotion in conversation | utterance-level emotion with speaker/context | macro F1, accuracy | conceptual precedent for context models |
| Multimodal emotion recognition | video/audio/text/physiology -> emotion | task-specific F1/correlation | motivates stimulus-only and alignment baselines |
| Emotion cause / trigger reasoning | cause, cue, intent, appraisal, rationale | QA, retrieval, human/LLM judge | stimulus-side auxiliary target |
| Affective captioning / QA | free-form emotion description | caption metrics, LLM judge, retrieval | convert to embedding targets |
| Affective interaction/generation | empathetic response, emotional speech/action | preference, task success | later extension, not core fMRI target |

NetFeeliX should borrow this ladder but translate it into fMRI-compatible
targets. The first experiments should remain measurable: regression,
classification, multi-label prediction, and representation geometry. Later
tracks can use MLLM-derived captions or rationales as **stimulus-side alignment
targets**, not as direct claims that fMRI generates explanations.

### 1.3 Brain Foundation Models Are Useful but Not Enough

Recent fMRI and neural-signal foundation models provide a strong starting point.

| Model family | Examples | Native direction | NetFeeliX role |
|---|---|---|---|
| 4D fMRI backbone | SwiFT | fMRI -> representation/task label | primary brain backbone |
| fMRI masked modeling | BrainLM | fMRI time series -> masked prediction | BFM transfer baseline |
| JEPA-style BFM | Brain-JEPA | fMRI -> predictive latent | objective precedent |
| Large 4D fMRI FM | NeuroSTORM | 4D fMRI -> transferable representation | comparison point if available |
| Omnifunctional / atlas-free FM | Omni-fMRI, Brain-OF, Brain-DiT | multi-state neural representation | future comparison |
| Rest-to-task bridge | SwiFUN | resting fMRI -> task activation | relevant because emotion-related task contrasts exist |

These models are important, but they do not solve the NetFeeliX problem by
themselves. Many BFMs are trained on resting-state or broad fMRI distributions.
Emotion-specific structure may not be explicitly learned unless we test and
adapt the models.

### 1.4 Why SwiFT-First

NetFeeliX is **SwiFT-first** for practical and scientific reasons.

Practical reason:

- SwiFT is the local lab backbone.
- We can inspect, modify, pretrain, fine-tune, and insert it into multimodal
  systems more realistically than external black-box models.

Scientific reason:

- SwiFT directly models 4D fMRI with spatiotemporal attention.
- Emotion in naturalistic fMRI is not purely spatial. It depends on temporal
  context, stimulus timing, and subject-level variation.
- A useful project question is not "does a pretrained checkpoint work?" but
  "how should a 4D fMRI encoder be modified for emotion representation?"

SwiFT-first does **not** mean only using frozen SwiFT. It means:

- start with frozen SwiFT probes,
- then test emotion heads,
- then adapters and subject modules,
- then naturalistic continued pretraining,
- then stimulus-brain alignment,
- then brain-tuned affective LLM/VLM extensions if justified.

---

## 2. Rationale

### 2.1 Emotion Prediction vs Emotion Representation Learning

If we train a model on one small emotion fMRI dataset and report one score, the
result can be misleading. High performance may reflect:

- stimulus identity,
- subject identity,
- low-level visual or auditory features,
- generic arousal,
- preprocessing artifacts,
- label imbalance,
- hemodynamic timing shortcuts.

Therefore, NetFeeliX should treat performance as only one layer of evidence.
The stronger evidence is:

1. performance across multiple target types,
2. transfer across subjects and stimuli,
3. transfer across datasets,
4. representation geometry aligned with emotion rating geometry,
5. improvement beyond stimulus-only models,
6. improvement beyond simple ROI/ridge baselines,
7. robustness after low-level stimulus controls.

### 2.2 Why Naturalistic Movie/Story fMRI

Naturalistic pretraining is **not** justified by the vague claim that
movie-watching is better than resting-state. The more precise hypothesis is:

```text
Before fine-tuning on small emotion-labeled fMRI datasets, SwiFT may need to
learn stimulus-locked brain dynamics driven by visual, auditory, language,
social, and narrative cues.
```

Resting-state fMRI can teach intrinsic connectivity, subject traits, and network
structure. Movie/story fMRI adds time-locked stimulus structure:

- faces and bodies,
- scene transitions,
- visual motion,
- speech and voice,
- music and auditory salience,
- language and semantic context,
- social interaction,
- narrative buildup and resolution.

This matters because many emotion targets are stimulus-driven. If visual or
audiovisual features are important for emotion prediction, as suggested by the
EmoViS direction, then NetFeeliX should test whether the **brain response to
those features** can improve emotion-specific fMRI representations.

But naturalistic pretraining can also fail. It may learn:

- low-level motion/luminance,
- audio energy or speech onset,
- scene-cut timing,
- face/object category,
- stimulus identity,
- generic arousal or attention,
- subject synchronization unrelated to emotion.

Therefore, naturalistic pretraining is useful only if it improves downstream
emotion transfer beyond these shortcuts.

### 2.3 HCP Is First Candidate, Not the Whole Strategy

HCP Young Adult 7T movie is the first naturalistic pretraining candidate because
it is standardized and relatively large. But HCP is not the only relevant
dataset. Different naturalistic datasets test different model hypotheses.

| Dataset/source | Main hypothesis | NetFeeliX role |
|---|---|---|
| HCP 7T movie | large-subject movie pretraining improves transfer | first continued-pretraining source |
| CNeuroMod / Algonauts 2025 | multimodal video/audio/transcript alignment improves fMRI representation | TRIBE-style alignment engineering |
| StudyForrest | long coherent film structure matters | long-film continuity and temporal representation |
| Narratives | language/story context matters without vision | language-context alignment |
| 101 Dalmatians | modality matters | visual-only/audio-only/audiovisual control |
| Emo-FilM | naturalistic emotion/component target | downstream validation |
| REELMO | long affect trajectories and rationale targets | stimulus-side supervision |

The correct statement is not:

```text
We will use HCP because it is a big movie dataset.
```

The correct statement is:

```text
We will use naturalistic fMRI sources to test whether stimulus-locked
pretraining and alignment improve emotion transfer. HCP is the first source;
other datasets are added when they answer a specific uncertainty.
```

### 2.4 Why TRIBE v2

TRIBE v2 is not a replacement for SwiFT.

Native directions:

```text
SwiFT:
    fMRI -> brain representation -> emotion head

TRIBE v2:
    video/audio/language stimulus -> predicted brain response
```

This difference is important. TRIBE v2 is a **stimulus-to-brain encoding
model**, not a direct fMRI encoder. But that does not make it irrelevant.

TRIBE v2 helps answer a critical question:

```text
How much of the emotion target is explained by stimulus context alone, and how
much requires observed brain activity?
```

NetFeeliX can use TRIBE v2 in four ways:

1. **Stimulus-only baseline**
   - video/audio/text -> emotion target.
   - Tests whether the label is mostly stimulus-explained.

2. **Stimulus-to-brain teacher**
   - stimulus -> predicted brain response.
   - Provides a teacher signal for fMRI representation learning.

3. **Latent alignment target**
   - align SwiFT latent with TRIBE/stimulus latent.
   - Tests whether shared stimulus-brain space helps emotion.

4. **Bidirectional architecture component**
   - learn emotion + fMRI encoding + alignment jointly.
   - Candidate NetFeeliX model family.

### 2.5 Why Affective LLM/VLMs

Modern affective computing is moving toward richer affective understanding:

- descriptive emotion captions,
- cue grounding,
- cause/trigger reasoning,
- appraisal-like explanations,
- multimodal emotional intelligence benchmarks.

NetFeeliX should not copy these tasks naively. fMRI data are too small and too
indirect for strong claims that the brain model "reasons" in natural language.

Instead, affective LLM/VLMs can be used as:

- stimulus-side feature extractors,
- weak label generators,
- caption/rationale embedding sources,
- auxiliary alignment targets,
- brain-tuned adapter targets.

Practical first version:

```text
stimulus -> affective VLM/LLM embedding -> z_affect
fMRI     -> SwiFT encoder                -> z_brain

align(z_brain, z_affect)
```

The claim should be cautious:

```text
Brain responses can regularize or evaluate affective stimulus representations.
```

Avoid overclaiming:

```text
fMRI directly performs natural-language emotional reasoning.
```

---

## 3. Gap in the Literature

### Gap 1. fMRI BFMs Are Not Emotion-Organized

Existing fMRI BFMs learn general brain representations. They may include emotion
tasks as downstream evaluations, but emotion is rarely the organizing principle
for pretraining objective, architecture, or benchmark design.

NetFeeliX gap:

```text
There is no mature SwiFT-style fMRI model-development framework focused on
emotion-specific representation learning.
```

### Gap 2. Affective Computing Foundation Models Lack Brain Grounding

Affective computing has strong LLM/VLM/MLLM momentum, but these models are
usually trained and evaluated on external labels, human judgments, and
multimodal stimuli. They are rarely grounded in fMRI responses to emotional or
naturalistic stimuli.

NetFeeliX gap:

```text
Can brain responses provide a biological alignment signal for affective AI
representations?
```

### Gap 3. Stimulus-to-Brain Models Optimize Encoding, Not Emotion Representation

TRIBE, TRIBE v2, VIBE, and related models predict fMRI responses from
naturalistic stimuli. Their native goal is encoding accuracy, not necessarily
emotion representation.

NetFeeliX gap:

```text
Can stimulus-to-brain models be modified into emotion representation components?
```

### Gap 4. Emotion fMRI Datasets Are Too Small for Naive End-to-End Training

Core emotion fMRI datasets are valuable but limited:

- Horikawa has rich high-dimensional targets but short videos and few subjects.
- Emo-FilM has naturalistic films and component annotations but limited fMRI N.
- Affective Videos and IAPS fMRI are useful checks but not enough for broad
  model claims.
- NeuroEmo and Koide-Majima-like datasets may help generalization but require
  access and harmonization.

NetFeeliX gap:

```text
We need a benchmark-to-model-development strategy before expensive full
pretraining or architecture claims.
```

### Gap 5. Task Design Is Often Too Narrow

If emotion is evaluated only as single-label classification, the model may miss:

- intensity,
- mixed emotions,
- high-dimensional affect geometry,
- appraisal/component structure,
- temporal affect trajectory,
- context and cue grounding.

NetFeeliX gap:

```text
Emotion fMRI modeling needs a task ladder, not one target.
```

---

## 4. Research Questions and Hypotheses

### 4.1 Main Research Question

```text
Which model architecture and learning objective best support transferable
emotion representation learning from fMRI?
```

### 4.2 Sub-Questions

1. **BFM transfer**
   - Do existing SwiFT/BFM representations predict emotion targets better than
     simple ROI/parcel baselines?

2. **Emotion specificity**
   - If frozen SwiFT works only for arousal, what architecture changes are
     needed for valence, multi-label emotion, high-dimensional vectors, or
     component targets?

3. **Naturalistic pretraining**
   - Does movie/story fMRI pretraining improve transfer to direct emotion
     targets beyond generic or resting-state pretraining?

4. **Stimulus-only explanation**
   - Are emotion labels mostly explained by stimulus features alone?

5. **Stimulus-brain alignment**
   - Does aligning SwiFT latents with video/audio/text/TRIBE latents improve
     high-dimensional emotion targets or cross-dataset transfer?

6. **Brain-tuned affective AI**
   - Can fMRI responses regularize affective LLM/VLM embeddings through
     adapters, contrastive learning, or distillation?

### 4.3 Working Hypotheses

| Hypothesis | Expected support | Falsification / warning |
|---|---|---|
| H1. Frozen SwiFT contains some emotion-relevant signal. | Frozen SwiFT beats ROI/ridge on at least arousal or category targets. | If simple ROI/ridge beats SwiFT broadly, check preprocessing and target timing first. |
| H2. Emotion-specific adaptation is needed for rich targets. | Adapters, subject modules, or multi-task heads improve valence/high-dimensional/component targets. | If frozen features already dominate, avoid unnecessary architecture complexity. |
| H3. Naturalistic pretraining helps only if it transfers beyond shortcuts. | HCP/CNeuroMod-style pretraining improves Horikawa/Emo-FilM high-dimensional or component targets. | If only arousal or visual tasks improve, treat it as sensory adaptation, not emotion representation. |
| H4. Stimulus-only models will be strong for some targets. | V-JEPA/CLIP/audio/text/TRIBE features predict labels well. | If stimulus-only explains everything, brain-specific claims must be conservative. |
| H5. Alignment is most useful for high-dimensional emotion. | Brain-stimulus alignment improves RSA/CKA, retrieval, or multi-label vectors. | If alignment only improves encoding but not emotion transfer, keep it auxiliary. |
| H6. Affective LLM/VLM targets are useful as embeddings, not direct claims. | Caption/rationale embeddings improve latent organization or retrieval. | Avoid claiming direct neural reasoning without explicit evidence. |

---

## 5. Conceptual Framework

### 5.1 Four-Axis NetFeeliX Framework

NetFeeliX can be viewed as a four-axis design space.

```text
Axis 1: Input source
    fMRI-only
    stimulus-only
    fMRI + stimulus
    fMRI + affective LLM/VLM target

Axis 2: Task target
    arousal/valence
    category
    multi-label / distribution
    high-dimensional emotion vector
    appraisal/component
    trajectory
    cue/rationale embedding

Axis 3: Model intervention
    frozen probe
    adapter / head
    subject module
    naturalistic continued pretraining
    stimulus-brain alignment
    brain-tuned affective adapter

Axis 4: Evidence standard
    performance
    transfer
    representation geometry
    low-level control
    stimulus-only comparison
    cross-dataset generalization
```

### 5.2 Minimum Comparable Interface

To compare SwiFT, TRIBE v2, stimulus encoders, and affective LLM/VLMs fairly,
NetFeeliX should define a harmonized interface.

| Condition | Input | Encoder | Head/loss | Question |
|---|---|---|---|---|
| Brain-only baseline | fMRI | ROI/ridge, dynamic FC | emotion loss | Is there brain signal at all? |
| Frozen SwiFT | fMRI | frozen SwiFT | linear/ridge/MLP | Does generic SwiFT transfer? |
| Adapted SwiFT | fMRI | SwiFT + adapter/head | emotion loss | Can SwiFT be emotion-specific? |
| Naturalistic-pretrained SwiFT | fMRI | SwiFT after movie/story SSL | emotion loss | Does stimulus-locked pretraining help? |
| Stimulus-only | video/audio/text | V-JEPA, CLIP, Whisper, LLM, TRIBE features | emotion loss | Is the target explained by stimulus alone? |
| TRIBE teacher | stimulus | TRIBE v2 | predicted fMRI / latent | Can predicted brain response teach SwiFT? |
| Aligned model | fMRI + stimulus | SwiFT + stimulus encoder | emotion + alignment | Does shared latent help? |
| Brain-tuned affective model | fMRI + affective embedding | SwiFT + adapter | contrastive/distillation | Can brain responses tune affective embeddings? |

### 5.3 Evidence Ladder

NetFeeliX should report results as an evidence ladder:

1. **Runnable data**
   - paths, shape, timing, target matrix, split.

2. **Non-deep baselines**
   - ROI/ridge, dynamic FC, simple temporal pooling.

3. **Frozen BFM transfer**
   - frozen SwiFT and other available BFMs.

4. **Parameter-efficient adaptation**
   - adapters, subject modules, multi-task heads.

5. **Naturalistic pretraining transfer**
   - HCP/CNeuroMod/StudyForrest-style pretraining -> emotion target.

6. **Stimulus-only comparison**
   - video/audio/text features -> emotion target.

7. **Alignment benefit**
   - brain-stimulus shared latent improves target/geometry/transfer.

8. **Cross-dataset robustness**
   - not just one dataset shortcut.

---

## 6. Task Design

### 6.1 NetFeeliX Task Ladder

| Level | Task | Dataset candidates | Why it matters |
|---|---|---|---|
| L0 | data/timing/target sanity | all datasets | no modeling claim before timing is correct |
| L1 | arousal regression | Affective Videos, Emo-FilM, REELMO-like targets | easiest transferable affect dimension |
| L2 | valence regression/category | Affective Videos, IAPS fMRI, Emo-FilM | harder than arousal; useful check |
| L3 | discrete/multi-label emotion | Horikawa, Emo-FilM, NeuroEmo | category-like emotion structure |
| L4 | high-dimensional emotion vector | Horikawa, Koide-Majima if accessible | core representation target |
| L5 | appraisal/component prediction | Emo-FilM | moves beyond simple category |
| L6 | continuous affect trajectory | Emo-FilM, REELMO | naturalistic time-varying emotion |
| L7 | cue/rationale/caption embedding | REELMO, MLLM targets, affective VLMs | stimulus-side context/reasoning alignment |

### 6.2 Metrics

| Target type | Metrics |
|---|---|
| Regression | Pearson r, Spearman r, CCC, MAE/MSE |
| Classification | balanced accuracy, macro F1, AUROC, top-k accuracy |
| Multi-label | macro/micro F1, AUROC, label-wise correlation |
| Distribution/vector | Pearson/Spearman per dimension, KL, cosine, RSA |
| Representation | RSA, CKA, retrieval accuracy, explained variance |
| fMRI encoding | parcel/voxel correlation, noise-ceiling-normalized score |
| Temporal trajectory | time-lagged correlation, CCC, dynamic error |
| Caption/rationale embedding | retrieval, contrastive accuracy, embedding similarity |

### 6.3 Critical Controls

| Control | What it detects |
|---|---|
| subject split | subject leakage |
| stimulus split | stimulus identity shortcut |
| temporal lag sweep | wrong HRF alignment |
| low-level visual/audio control | motion/luminance/audio shortcut |
| arousal-only analysis | generic attention/arousal shortcut |
| stimulus-only baseline | whether brain data adds information |
| simple ROI/ridge baseline | whether deep model adds value |
| frozen vs adapted SwiFT | whether architecture changes matter |
| naturalistic-pretrained vs generic SwiFT | whether movie/story SSL transfers |
| cross-dataset test | whether representation generalizes |

---

## 7. Dataset Strategy

### 7.1 Dataset Roles

NetFeeliX should not rank datasets as "Tier 0/1/2." Datasets should be grouped
by the question they answer.

| Role | Datasets | Primary question |
|---|---|---|
| Core emotion-labeled fMRI | Horikawa/Cowen, Emo-FilM | can fMRI encode rich emotion targets? |
| Lightweight affect checks | Affective Videos, IAPS fMRI | can the pipeline recover arousal/valence/category? |
| Generalization emotion fMRI | NeuroEmo, Koide-Majima if accessible | does the representation transfer beyond one dataset? |
| Naturalistic pretraining | HCP 7T movie, CNeuroMod, StudyForrest, Narratives, 101 Dalmatians | does stimulus-locked pretraining help? |
| Stimulus-side affect/context | REELMO, OASIS, MLLM targets | can richer affect targets supervise stimulus representations? |
| Static-image fMRI extension | NSD + OASIS/MLLM pseudo-labels | can large image fMRI support affective transfer? |
| Encoding/alignment resources | TRIBE v2, CNeuroMod/Algonauts, BOLD Moments | can stimulus-to-brain models regularize SwiFT? |

### 7.2 Direct Emotion-Labeled fMRI

#### Horikawa / Cowen Emotional Video fMRI

Role:

- core high-dimensional affect geometry dataset.
- not a reasoning dataset.
- useful for testing whether brain representation captures rich emotion
  structure beyond arousal/valence.

Main tasks:

- high-dimensional emotion vector prediction,
- category/multi-label prediction,
- RSA/CKA between SwiFT latent geometry and emotion rating geometry,
- brain-only vs stimulus-only comparison.

SwiFT use:

- frozen SwiFT + ridge/MLP head,
- adapter tuning,
- affective token/query pooling,
- compare generic SwiFT vs naturalistic-pretrained SwiFT.

Risk:

- short videos,
- small subject count,
- target is often group-level stimulus rating rather than individual subjective
  experience.

#### Emo-FilM

Role:

- strongest naturalistic emotion/component dataset.
- useful for appraisal, component, physiology, and film-context targets.

Main tasks:

- arousal/valence-like reduced targets,
- component-specific prediction,
- appraisal/motivation/expression/physiology/feeling heads,
- context-window comparison,
- physiology-aware auxiliary prediction.

SwiFT use:

- adapter tuning,
- subject adapter,
- multi-task head,
- naturalistic-pretrained SwiFT transfer evaluation.

Risk:

- timing and annotation smoothing are important,
- fMRI sample size is limited,
- annotation reliability may differ across items.

#### Affective Videos

Role:

- compact arousal/valence check.
- useful before expensive pretraining.

Main tasks:

- arousal regression/classification,
- valence regression/classification,
- fMRI-only vs stimulus-only comparison.

Risk:

- small subject count,
- short clips,
- not enough for broad model claims.

#### IAPS fMRI NeuroVault

Role:

- static image valence-category test.
- useful for spatial/beta-map adaptation.

Main tasks:

- positive/neutral/negative classification,
- pairwise valence contrasts,
- beta-map adapter testing.

Risk:

- beta maps, not raw 4D fMRI,
- no temporal dynamics,
- IAPS stimulus licensing can matter.

#### NeuroEmo

Role:

- cross-cultural emotion-recognition dataset.
- useful for generalization and label mapping.

Main tasks:

- multi-class emotion recognition,
- rest-to-task comparison,
- cross-dataset compatibility check.

Risk:

- stimulus availability and event files need inspection,
- emotion labels are elicitation classes,
- cultural context complicates merging with other datasets.

### 7.3 Naturalistic Movie/Story fMRI

#### HCP Young Adult 7T Movie

Role:

- first large-subject continued-pretraining candidate.
- tests whether stimulus-locked movie fMRI improves emotion transfer.

Main objectives:

- masked fMRI segment modeling,
- temporal contrastive learning,
- JEPA/future latent prediction,
- subject-invariant learning,
- optional stimulus-conditioned prediction.

Success criterion:

- improvement on Horikawa/Emo-FilM/Affective Videos/IAPS/NeuroEmo,
  especially beyond arousal.

Risk:

- no direct emotion labels,
- may learn low-level sensory features or generic synchrony,
- compute cost can be large.

#### CNeuroMod / Algonauts 2025

Role:

- multimodal encoding and alignment engineering.
- natural bridge to TRIBE v2-style work.

Main tasks:

- video/audio/transcript-to-fMRI encoding,
- stimulus-brain latent matching,
- OOD movie generalization,
- parcel-level alignment before full 4D volume work.

Risk:

- small number of dense subjects,
- surface/parcel/volume mismatch with SwiFT,
- not emotion-specific unless transfer is shown.

#### StudyForrest

Role:

- long-film continuity and audiovisual narrative.

Main tasks:

- long-window vs short-window representation learning,
- future-latent prediction over coherent story segments,
- transfer to Emo-FilM.

Risk:

- multiple releases,
- stimulus access and copyright constraints,
- story-specific shortcut.

#### Narratives

Role:

- language/story context without visual cues.

Main tasks:

- align fMRI with transcript/LLM embeddings,
- test language-only context representation,
- optional affective-rationale embedding transfer.

Risk:

- no direct emotion labels,
- language-model pseudo-label bias,
- not a visual emotion dataset.

#### 101 Dalmatians

Role:

- modality-control naturalistic movie fMRI.

Main tasks:

- visual-only vs auditory-only vs audiovisual comparison,
- modality ablation for emotion transfer.

Risk:

- not primary emotion-labeled dataset,
- should be used after core pipelines are stable.

### 7.4 Stimulus-Side and Static-Image Extensions

#### REELMO

Role:

- long movie affect trajectories and context-rich affect supervision.

Main use:

- stimulus-side affect trajectory target,
- cue/rationale/caption embedding generation,
- possible fMRI subset exploration.

Risk:

- fMRI subset is much smaller than behavioral affect reports,
- movie copyright/access issues,
- behavioral reports are not identical to subject-specific fMRI experience.

#### NSD + OASIS

Role:

- static image fMRI scale + affective pseudo-label calibration.

Main use:

- image fMRI representation learning,
- OASIS valence/arousal labels or VLM affect scoring,
- static-image affect extension.

Risk:

- NSD is not natively an emotion dataset,
- pseudo-labels must be treated carefully,
- static images do not test temporal dynamics.

---

## 8. Model and Training Strategy

### 8.1 Baseline Order

The first experiments should avoid expensive architecture changes.

1. ROI/parcel ridge baseline.
2. Dynamic FC baseline for arousal/valence.
3. Frozen SwiFT feature + linear/ridge/MLP head.
4. Stimulus-only baseline if features are available.
5. Adapter or subject-module tuning.
6. Naturalistic pretraining only after target/readout pipeline is stable.
7. TRIBE-SwiFT alignment after stimulus and brain baselines are interpretable.

### 8.2 SwiFT Adaptation Options

| Option | What changes | When to use |
|---|---|---|
| linear/ridge head | only readout | first baseline |
| MLP emotion head | shallow nonlinear readout | if frozen features show signal |
| multi-task head | separate arousal/valence/category/vector/component outputs | heterogeneous targets |
| subject adapter | subject embedding or adapter | multi-subject variation |
| dataset adapter | small dataset/domain module | cross-dataset training |
| affective token/query | learned pooling target | test explicit affect readout |
| late-block tuning | unfreeze late stages | if adapters underfit |
| LoRA-style attention update | parameter-efficient attention tuning | if implementation feasible |

### 8.3 Naturalistic Pretraining Objectives

| Objective | Input | Target | Why it matters |
|---|---|---|---|
| masked fMRI modeling | fMRI window with masked segments | reconstruct masked fMRI | basic self-supervised learning |
| temporal contrastive learning | augmented windows | matched latent | robust temporal representation |
| JEPA/future latent prediction | past/current window | future or held-out latent | predictive brain dynamics |
| subject-invariant contrastive | same stimulus, different subjects | shared latent | reduce subject-specific noise |
| stimulus-conditioned prediction | fMRI + stimulus features | fMRI/latent prediction | connect stimulus and brain dynamics |
| cross-view retrieval | fMRI window + stimulus window | matched pair | alignment-ready representation |

### 8.4 TRIBE v2 + SwiFT Alignment

Candidate architecture:

```text
Stimulus path:
    video/audio/text -> TRIBE v2 or component encoders -> z_stim

Brain path:
    fMRI window -> SwiFT -> z_brain

Shared latent:
    align(z_brain, z_stim)

Heads:
    z_brain -> emotion
    z_stim  -> emotion
    z_stim  -> predicted fMRI
    z_brain -> future/reconstructed fMRI
```

Candidate losses:

```text
L = L_emotion(z_brain, y_emotion)
  + lambda_1 * L_emotion(z_stim, y_emotion)
  + lambda_2 * L_align(z_brain, z_stim)
  + lambda_3 * L_encoding(z_stim, fMRI)
  + lambda_4 * L_ssl(z_brain)
```

Alignment loss options:

- regression,
- contrastive InfoNCE,
- CKA/RSA geometry alignment,
- cross-view JEPA prediction,
- synchronized retrieval.

### 8.5 Surface/Volume Mismatch

TRIBE v2 outputs cortical surface responses, while SwiFT is a volumetric 4D fMRI
model. This must be handled explicitly.

Options:

1. common parcellation,
2. surface projection,
3. volume approximation,
4. latent-only alignment.

Default first choice:

```text
common parcellation or latent-only alignment
```

because it reduces engineering risk.

---

## 9. Experimental Phases

### Phase 0. Setup and Feasibility

**Goal**: determine what can be run immediately.

Inputs:

- local dataset paths,
- BIDS/event files,
- fMRI shape/TR/timing metadata,
- target annotations,
- SwiFT checkpoint/code availability,
- stimulus availability.

Tasks:

1. create dataset availability table,
2. inspect fMRI shape and TR,
3. inspect event timing and HRF lag assumptions,
4. build initial target matrices,
5. define train/validation/test split,
6. list blocked datasets/resources,
7. document compute requirements.

Outputs:

- `setup/results/dataset_availability.md`,
- target construction report,
- split metadata,
- blocked resource list,
- first experiment cards.

Decision rule:

- If Horikawa target is ready, start NFx-001 and NFx-002.
- If Emo-FilM timing is manageable, prepare component/appraisal targets.
- If HCP data are accessible, prepare pretraining-readiness report.
- If data access is blocked, switch to Affective Videos/IAPS for pipeline sanity.

### Phase 1. Initial Benchmark

**Goal**: establish the minimum comparable benchmark surface.

Models:

- ROI/parcel ridge,
- dynamic FC,
- frozen SwiFT + linear/ridge/MLP head,
- stimulus-only model if easy.

Initial experiments:

| ID | Dataset | Model | Target | Purpose |
|---|---|---|---|---|
| NFx-001 | Horikawa | frozen SwiFT + head | high-dimensional vector | test BFM transfer |
| NFx-002 | Horikawa | ROI/parcel ridge | high-dimensional vector | simple baseline |
| NFx-003 | Affective Videos | ridge / frozen SwiFT | arousal, valence | sanity check |
| NFx-004 | IAPS fMRI | beta-map adapter | positive/neutral/negative | spatial affect check |
| NFx-005 | Emo-FilM | ridge / frozen SwiFT | component/appraisal | naturalistic target readiness |

Outputs:

- baseline table,
- per-target metrics,
- error/failure report,
- preprocessing notes.

Decision rule:

- If frozen SwiFT beats simple baselines, proceed to adapters and heads.
- If simple baselines beat SwiFT, inspect preprocessing, HRF timing, and readout.
- If stimulus-only is very strong, prioritize alignment and interpret brain
  claims carefully.

### Phase 2. SwiFT Emotion Adaptation

**Goal**: make SwiFT more emotion-specific without overfitting.

Model changes:

- multi-task emotion head,
- subject adapter,
- dataset/domain adapter,
- affective token/query pooling,
- temporal pooling head,
- partial late-block fine-tuning.

Primary datasets:

- Horikawa,
- Emo-FilM,
- Affective Videos/IAPS for sanity checks.

Outputs:

- adapted SwiFT checkpoints,
- adapter/head comparison,
- target-wise improvement table,
- subject/stimulus generalization analysis.

Decision rule:

- If adapters improve high-dimensional/component targets, continue SwiFT
  specialization.
- If only arousal improves, add physiology/dynamic objectives.
- If adaptation overfits, reduce trainable parameters and strengthen split
  validation.

### Phase 3. Naturalistic Movie/Story Pretraining

**Goal**: test whether stimulus-locked fMRI pretraining improves emotion
transfer.

First source:

- HCP Young Adult 7T movie.

Hypothesis-specific extensions:

- CNeuroMod/Algonauts for multimodal alignment,
- StudyForrest for long-film continuity,
- Narratives for language/story context,
- 101 Dalmatians for modality control.

Objectives:

- masked fMRI modeling,
- temporal contrastive learning,
- JEPA/future latent prediction,
- subject-invariant learning,
- stimulus-conditioned fMRI prediction.

Controls:

- generic/resting SwiFT vs naturalistic-pretrained SwiFT,
- low-level visual/audio controls,
- vision-only/audio-only/text-only ablation,
- stimulus-only baseline,
- arousal-only vs high-dimensional target.

Outputs:

- pretraining loss curves,
- frozen embeddings,
- transfer table to Horikawa/Emo-FilM,
- shortcut-control analysis.

Decision rule:

- If transfer improves on high-dimensional/component targets, scale
  naturalistic pretraining.
- If only low-level or arousal targets improve, treat it as sensory adaptation.
- If no transfer benefit appears, prioritize adapters, target design, and
  alignment instead.

### Phase 4. TRIBE v2 + SwiFT Alignment

**Goal**: learn shared brain-stimulus-emotion representation.

Conditions:

| Condition | Brain input | Stimulus input | Purpose |
|---|---|---|---|
| brain-only | observed fMRI | none | fMRI emotion decoding |
| stimulus-only | none | video/audio/text | label explained by stimulus |
| TRIBE teacher | none | TRIBE-predicted brain | stimulus-to-brain prior |
| latent aligned | observed fMRI | stimulus latent | shared representation |
| joint model | observed fMRI | stimulus latent | emotion + encoding + alignment |

Outputs:

- alignment metrics,
- emotion metrics,
- fMRI encoding metrics,
- representation geometry analysis,
- brain-only vs stimulus-only vs aligned comparison.

Decision rule:

- If alignment improves high-dimensional emotion or cross-dataset transfer,
  prioritize TRIBE-SwiFT model surgery.
- If stimulus-only dominates and brain adds little, focus on brain-specific
  residuals or reinterpret claims.
- If alignment helps encoding but not emotion, keep it as auxiliary.

### Phase 5. Brain-Tuned Affective LLM/VLM Extension

**Goal**: use brain responses to regularize affective stimulus representations.

Inputs:

- affective captions,
- cue/rationale labels,
- appraisal embeddings,
- VLM/LLM stimulus embeddings,
- fMRI latents.

Candidate approach:

```text
stimulus -> affective LLM/VLM -> z_affect
fMRI     -> SwiFT             -> z_brain

loss = contrastive(z_brain, z_affect)
     + emotion_loss
     + optional retrieval / RSA loss
```

Outputs:

- brain-aligned affective embeddings,
- retrieval/alignment score,
- target improvement over pure stimulus embeddings,
- qualitative cue/rationale analysis if valid.

Decision rule:

- Activate this track only if stimulus-side features or alignment are promising.
- Do not make natural-language reasoning claims without explicit evidence.

### Phase 6. Consolidation and Paper Direction

**Goal**: convert benchmark results into a coherent model-development story.

Possible outcomes:

| Outcome | Interpretation | Next model direction |
|---|---|---|
| frozen SwiFT works well | generic BFM already contains emotion signal | adapter/head refinement |
| adapters help | emotion-specific changes are needed | parameter-efficient SwiFT adaptation |
| naturalistic pretraining helps | stimulus-locked fMRI dynamics matter | scale movie/story pretraining |
| stimulus-only dominates | labels are mostly stimulus-explained | alignment and residual brain analysis |
| alignment helps | emotion is shared brain-stimulus structure | dual encoder / TRIBE-SwiFT model |
| only arousal works | representation is low-dimensional | physiology/dynamic objective |
| no method works | target/preprocessing mismatch or dataset limitation | revise target construction |

---

## 10. Two-Month Roadmap

### Weeks 1-2: Data and Target Readiness

Priorities:

- Horikawa path, fMRI shape, event timing, target matrix.
- Emo-FilM access, annotation format, timing.
- Affective Videos / IAPS sanity dataset readiness.
- HCP 7T movie accessibility and preprocessing status.
- Initial experiment cards.

Deliverables:

- dataset availability report,
- target construction report,
- NFx-001 and NFx-002 cards,
- first simple baseline script outline.

### Weeks 3-4: Baselines and Frozen SwiFT

Priorities:

- ROI/ridge baseline,
- dynamic FC baseline if target supports it,
- frozen SwiFT feature extraction,
- stimulus-only features for Horikawa/Emo-FilM if available.

Deliverables:

- first metrics table,
- brain-only vs stimulus-only comparison,
- readout/head selection.

### Weeks 5-6: SwiFT Adaptation and Naturalistic Readiness

Priorities:

- multi-task head,
- subject adapter,
- affective token/query pooling if feasible,
- HCP/CNeuroMod/StudyForrest/Narratives readiness report.

Deliverables:

- adapted SwiFT comparison,
- naturalistic pretraining plan,
- compute estimate,
- shortcut-control plan.

### Weeks 7-8: Alignment Prototype and Decision Report

Priorities:

- TRIBE v2 feasibility check,
- common parcellation or latent-only alignment design,
- stimulus-only vs aligned prototype,
- decision table for next model-development stage.

Deliverables:

- Phase 0/1/2 result summary,
- go/no-go decision for naturalistic pretraining,
- go/no-go decision for TRIBE-SwiFT alignment,
- draft abstract/presentation outline.

---

## 11. Expected Contributions

NetFeeliX can contribute at several levels even before claiming a final model.

### 11.1 Benchmark Contribution

- A structured benchmark comparing brain-only, stimulus-only, BFM transfer,
  naturalistic pretraining, and stimulus-brain alignment for emotion fMRI.

### 11.2 Model-Development Contribution

- A SwiFT-first roadmap for emotion-specific fMRI representation learning.
- Parameter-efficient adaptation strategies for small emotion fMRI datasets.
- Decision rules for when to pretrain, adapt, align, or stop.

### 11.3 Conceptual Contribution

- A taxonomy separating:
  - fMRI encoders,
  - stimulus-to-brain encoding models,
  - emotion decoding heads,
  - brain-stimulus aligned representations,
  - brain-tuned affective AI adapters.

### 11.4 Empirical Contribution

- Evidence about which emotion targets are recoverable from fMRI.
- Evidence about whether naturalistic movie/story fMRI pretraining transfers to
  emotion tasks.
- Evidence about when stimulus context explains emotion labels without brain
  data.

### 11.5 Practical Contribution

- A reusable project scaffold:
  - dataset cards,
  - experiment cards,
  - decision logs,
  - verification scripts,
  - status reports.

---

## 12. Action Items

### 12.1 Immediate Dataset Actions

- [ ] Confirm Horikawa local data path.
- [ ] Confirm Horikawa fMRI shape, TR, event timing, and target matrix format.
- [ ] Confirm Emo-FilM access and annotation files.
- [ ] Inspect Emo-FilM timing and annotation smoothing requirements.
- [ ] Confirm Affective Videos access and target labels.
- [ ] Confirm IAPS fMRI NeuroVault beta-map availability.
- [ ] Confirm HCP 7T movie availability and preprocessing format.
- [ ] List CNeuroMod/Algonauts, StudyForrest, Narratives, and 101 Dalmatians
      access requirements.
- [ ] Create `setup/results/dataset_availability.md`.
- [ ] Create `setup/results/target_construction.md`.

### 12.2 Immediate Baseline Actions

- [ ] Define train/validation/test split for Horikawa.
- [ ] Implement ROI/parcel ridge baseline.
- [ ] Implement frozen SwiFT feature extraction check.
- [ ] Implement frozen SwiFT + linear/ridge/MLP head.
- [ ] Create NFx-001 experiment card: Frozen SwiFT Horikawa probe.
- [ ] Create NFx-002 experiment card: ROI/ridge Horikawa baseline.
- [ ] Create NFx-003 experiment card: Affective Videos arousal/valence check.
- [ ] Create NFx-004 experiment card: IAPS beta-map category check.

### 12.3 Model Actions

- [ ] Design emotion-specific multi-task head.
- [ ] Design subject adapter option.
- [ ] Design affective token/query pooling option.
- [ ] Decide whether to use parcel-level or 4D input for first adaptation.
- [ ] Define adapter vs late-block fine-tuning comparison.
- [ ] Define naturalistic pretraining minimum viable objective.
- [ ] Define TRIBE v2 integration point: feature extractor, teacher, or alignment
      target.

### 12.4 Stimulus and Alignment Actions

- [ ] Check availability of video/audio/text stimuli for Horikawa and Emo-FilM.
- [ ] Define candidate stimulus encoders: V-JEPA2, CLIP, Wav2Vec-BERT, Whisper,
      LLM/sentence embeddings.
- [ ] Define stimulus-only baseline target table.
- [ ] Decide first alignment space: common parcellation vs latent-only.
- [ ] Define low-level visual/audio controls.

### 12.5 Documentation and Operations

- [ ] Keep framework updates in `Paper/framework_KR.md` and
      `Paper/framework_EN.md`.
- [ ] Keep dataset decisions in `reference/datasets.md`.
- [ ] Keep task design in `reference/task.md`.
- [ ] Keep training plans in `reference/training_strategy.md`.
- [ ] Use experiment cards before running major experiments.
- [ ] Use decision logs after each benchmark result.
- [ ] Run `python3 scripts/check_md_completeness.py` after structural edits.

---

## 13. Open Questions

1. Which Horikawa target format is most practical for first experiments:
   raw high-dimensional ratings, reduced category vectors, or PCA/embedding
   targets?

2. Should the first SwiFT probe operate on full 4D volumes, parcels, or
   extracted intermediate features?

3. For Emo-FilM, which component targets are reliable enough for first
   modeling?

4. What is the minimum HCP movie pretraining experiment that can be run without
   consuming too much compute?

5. Is TRIBE v2 easiest to use as:
   - a stimulus feature extractor,
   - a predicted-brain teacher,
   - or a latent alignment module?

6. What split should be primary:
   - subject split,
   - stimulus split,
   - or both?

7. How should fMRI hemodynamic lag be handled consistently across datasets?

8. How should stimulus-only strength be interpreted when the emotion target is
   based on group-level stimulus annotations rather than participant-specific
   emotion reports?

9. Which action is more valuable after the first benchmark:
   - SwiFT adapter,
   - naturalistic pretraining,
   - TRIBE-SwiFT alignment,
   - or target redesign?

---

## 14. Short Team Post Version

NetFeeliX is a SwiFT-first model-development project for emotion-aware fMRI
representation learning. The goal is not to immediately claim a complete
"Emotion Foundation Model," but to determine how SwiFT should be adapted,
pretrained, or aligned with multimodal stimulus models to better learn
emotion-relevant brain representations.

The project starts with Horikawa and Emo-FilM as core emotion fMRI targets,
uses Affective Videos/IAPS as lightweight checks, tests HCP/CNeuroMod/StudyForrest
style naturalistic fMRI pretraining only if it transfers to emotion targets, and
uses TRIBE v2 as a stimulus-to-brain teacher/alignment component rather than a
replacement for SwiFT.

The immediate action is to build a runnable benchmark: dataset access, target
matrices, simple ROI baselines, frozen SwiFT probes, stimulus-only baselines,
and experiment cards. These results will decide whether we invest next in
SwiFT adapters, naturalistic pretraining, TRIBE-SwiFT alignment, or
brain-tuned affective LLM/VLM extensions.

---

## 15. Key References and Resources

### Project

- NetFeeliX GitHub: https://github.com/Transconnectome/NetFeeliX
- SwiFT: https://github.com/Transconnectome/SwiFT
- TRIBE v2: https://github.com/facebookresearch/tribev2

### Core Emotion fMRI

- Horikawa/Cowen emotional video fMRI: https://openneuro.org/datasets/ds002425
- Horikawa/Cowen paper: https://www.sciencedirect.com/science/article/pii/S2589004220302455
- Horikawa data mirror: https://data.mendeley.com/datasets/jbk2r73mzh
- Emo-FilM paper: https://www.nature.com/articles/s41597-025-04803-5
- Emo-FilM OpenNeuro: https://openneuro.org/datasets/ds004892
- Affective Videos: https://www.openfmri.org/dataset/ds000205/
- IAPS fMRI NeuroVault: https://neurovault.org/collections/16284/
- NeuroEmo: https://github.com/OpenNeuroDatasets/ds005700

### Naturalistic fMRI and Alignment

- HCP 7T protocol: https://www.humanconnectome.org/hcp-protocols-ya-7t-imaging
- CNeuroMod datasets: https://www.cneuromod.ca/gallery/datasets/
- Algonauts 2025 brain data: https://algonautsproject.com/2025/braindata.html
- StudyForrest: https://www.studyforrest.org/
- StudyForrest OpenfMRI: https://openfmri.org/dataset/ds000113
- Narratives: https://openneuro.org/datasets/ds002345
- BOLD Moments: https://www.nature.com/articles/s41467-024-50310-3

### Affective Computing and Task Design

- GoEmotions: https://aclanthology.org/2020.acl-main.372/
- AVEC continuous affect: https://portal.fis.tum.de/en/publications/avec-2012-the-continuous-audiovisual-emotion-challenge
- SemEval Affect in Tweets: https://publications-cnrc.canada.ca/eng/view/object/?id=560b602a-37a5-47be-b306-4b80277382ea
- MME-Emotion: https://mme-emotion.github.io/
- EmoBench-M: https://github.com/Emo-gml/EmoBench-M
- AffectGPT: https://github.com/zeroQiaoba/AffectGPT
- MuSe Challenge: https://www.muse-challenge.org/

### Brain Foundation Models and Brain-Aligned AI

- BrainLM: https://sciety.org/articles/activity/10.1101/2023.09.12.557460
- Brain-JEPA: https://huggingface.co/papers/2409.19407
- NeuroSTORM: https://www.nature.com/articles/s41551-026-01666-y
- Brain-Score Vision: https://github.com/brain-score/vision
- Brain-Score Language: https://github.com/brain-score/language

