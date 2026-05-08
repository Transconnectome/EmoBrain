# NetFeeliX Task Inventory

This document defines the task space for NetFeeliX. The main goal is not to maximize one emotion prediction score, but to identify which tasks reveal useful **emotion-specific brain representation learning**.

## Task Groups

| Group | Task | Input | Target/output | Primary dataset | Main model use |
|---|---|---|---|---|---|
| Emotion prediction | Arousal regression | fMRI, stimulus, or aligned latent | continuous arousal | Affective Videos, Emo-FilM, REELMO, Ke datasets | fast sanity check |
| Emotion prediction | Valence regression | fMRI, stimulus, or aligned latent | continuous valence | Affective Videos, IAPS fMRI, Emo-FilM | harder affect dimension |
| Emotion prediction | Valence category | fMRI beta map or time window | positive/neutral/negative | IAPS fMRI | quick category benchmark |
| Emotion prediction | Discrete emotion prediction | fMRI or stimulus window | emotion category/multi-label vector | Horikawa, Emo-FilM, NeuroEmo | category-like affect structure |
| Emotion prediction | High-dimensional emotion vector | fMRI or stimulus window | emotion rating vector | Horikawa, Koide-Majima | affect geometry benchmark |
| Emotion prediction | Appraisal/component prediction | fMRI + stimulus context | component ratings | Emo-FilM | bridge to context understanding |
| Representation learning | Masked fMRI modeling | HCP movie fMRI | reconstructed masked segments | HCP 7T movie | SwiFT continued pretraining |
| Representation learning | Contrastive fMRI learning | augmented fMRI windows | matched latent views | HCP, Horikawa, Emo-FilM | robust fMRI representation |
| Representation learning | JEPA/future latent prediction | fMRI history window | future or held-out latent | HCP 7T movie | predictive brain dynamics |
| Representation learning | Subject-invariant learning | multi-subject fMRI | subject-shared latent | HCP, Emo-FilM | transfer across participants |
| Alignment/encoding | fMRI-to-emotion decoding | fMRI | emotion target | Horikawa, Emo-FilM, Affective Videos | SwiFT emotion head |
| Alignment/encoding | stimulus-to-emotion prediction | video/audio/text/image | emotion target | Horikawa, Emo-FilM, REELMO | TRIBE v2/stimulus baseline |
| Alignment/encoding | stimulus-to-fMRI encoding | video/audio/text | fMRI response | CNeuroMod, HCP, Emo-FilM if aligned | TRIBE v2 auxiliary objective |
| Alignment/encoding | brain-stimulus latent matching | fMRI + stimulus | matched latent/retrieval | HCP, Emo-FilM, Horikawa | shared representation |
| Alignment/encoding | TRIBE-teacher distillation | TRIBE-predicted brain response | SwiFT latent or fMRI target | CNeuroMod/HCP-style data | transfer stimulus-brain structure into SwiFT |
| Reasoning/context | short vs long context | local and extended stimulus windows | emotion target | Emo-FilM, REELMO | context sensitivity |
| Reasoning/context | rationale embedding alignment | stimulus + MLLM rationale | rationale/cue embedding | Emo-FilM, REELMO | explanation-aware latent |
| Reasoning/context | cue grounding | audiovisual/text cues | cue-emotion association | REELMO, MLLM-generated targets | avoid label-only shortcut |
| Reasoning/context | MLLM-derived affect targets | movie/image stimulus | caption, appraisal, cause, intensity | REELMO, Emo-FilM, NSD/OASIS | stimulus-side supervision |
| Transfer | cross-subject transfer | train subjects -> held-out subject | same target | all fMRI datasets | population generalization |
| Transfer | cross-stimulus/movie transfer | train clips/movies -> held-out clips/movies | same target | Horikawa, Emo-FilM, REELMO | content generalization |
| Transfer | cross-dataset transfer | source dataset -> target dataset | compatible affect target | Affective Videos, Emo-FilM, Horikawa | representation robustness |

## Recommended Stage Order

### Stage 0: Feasibility Benchmark

Purpose: determine which datasets and targets are runnable.

Tasks:

1. dataset access and metadata check,
2. fMRI shape and timing check,
3. target construction check,
4. minimal ridge/linear baseline.

Outputs:

- dataset availability table,
- target construction table,
- first baseline metric table,
- blocked-resource list.

### Stage 1: SwiFT Emotion Specificity

Purpose: test whether SwiFT can be made more emotion-specific.

Tasks:

1. SwiFT frozen features + linear/ridge/MLP emotion head,
2. SwiFT adapter or partial fine-tuning,
3. SwiFT continued pretraining on HCP movie,
4. emotion-specific head comparison: arousal/valence, discrete emotion, high-dimensional vector, appraisal/component.

Primary targets:

- Horikawa high-dimensional vector,
- Emo-FilM component/appraisal ratings,
- Affective Videos or IAPS fMRI valence/arousal/category.

### Stage 2: TRIBE v2 and Stimulus-Side Comparison

Purpose: test how much emotion is explained by stimulus context.

Tasks:

1. TRIBE v2 stimulus features -> emotion head,
2. TRIBE v2 predicted brain response -> emotion head,
3. V-JEPA2/CLIP/Whisper/LLM features -> emotion head,
4. stimulus-only vs fMRI-only vs aligned comparison.

Key question:

```text
Does fMRI add emotion-relevant information beyond stimulus features,
or does stimulus context explain most observed emotion labels?
```

### Stage 3: Shared Latent and Context

Purpose: build the NetFeeliX model direction.

Tasks:

1. fMRI and stimulus latent matching,
2. contrastive retrieval between brain windows and stimulus windows,
3. shared latent with emotion and fMRI-response heads,
4. short-window vs long-window context,
5. rationale/cue embedding alignment.

## Task-to-Dataset Mapping

| Dataset | Best first task | Secondary task | Avoid overclaiming |
|---|---|---|---|
| Horikawa | high-dimensional affect geometry | stimulus-only vs fMRI-only comparison | natural-language reasoning |
| Emo-FilM | component/appraisal emotion prediction | context/rationale alignment | large-scale foundation model claims |
| HCP 7T movie | SwiFT continued pretraining | stimulus-conditioned fMRI prediction | direct emotion prediction without labels |
| Affective Videos | valence/arousal sanity check | simple fMRI/stimulus comparison | broad transfer claims |
| IAPS fMRI | valence-category beta-map benchmark | static image affect comparison | temporal dynamics |
| REELMO | context/rationale trajectory targets | fMRI subset transfer if accessible | assuming fMRI scale is large |
| NSD | static-image fMRI representation | affective pseudo-label transfer | native emotion labels |
| OASIS | affect label calibration | image affect pseudo-labeling | fMRI analysis |

## Horikawa Rule

Horikawa should be written as a **high-dimensional affect geometry benchmark**, not as a reasoning/context dataset. It is ideal for testing whether SwiFT or a modified fMRI encoder captures rich emotion-category structure from brain activity. Reasoning/context tasks should be tested with Emo-FilM, REELMO, movie datasets, and MLLM-derived cue/rationale embeddings.
