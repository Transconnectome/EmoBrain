# NetFeeliX Pilot Benchmark Design

## Purpose

The pilot benchmark should determine which existing model and data ingredients are worth turning into a full NetFeeliX model. It is not meant to prove the final architecture immediately.

## Candidate Inventory

This section lists the current dataset, model, and task space before final prioritization. The goal is to make the decision surface explicit.

### Dataset Candidates

| Priority | Dataset | Brain data | Stimulus/context | Emotion/affect target | Best use |
|---|---|---|---|---|---|
| Tier 0 | Horikawa/Cowen emotional videos | fMRI | 2,185 short emotional videos | high-dimensional emotion category ratings | core brain-side affect geometry probe |
| Tier 0 | Emo-FilM | fMRI + physiology | 14 naturalistic short films | 50 emotion/appraisal/component annotations | core naturalistic downstream benchmark |
| Tier 0 | HCP 7T movie | 7T fMRI, 184 subjects | movie clips, TR 1 s | no direct emotion labels | naturalistic fMRI pretraining |
| Tier 1 | Affective Videos ds000205 | fMRI | 5 s audiovisual clips | valence/arousal | lightweight sanity-check dataset |
| Tier 1 | REELMO | behavioral reports + fMRI subset | 60 full movies; fMRI subset on Jojo Rabbit | 20 affective states at 1 s resolution | stimulus-side emotion trajectories and context |
| Tier 1 | NeuroEmo | fMRI | Bollywood emotion clips | emotion labels | cross-cultural emotion downstream if metadata is usable |
| Tier 1 | Ke et al. movie datasets | fMRI/dynamic FC resources | Sherlock, Friday Night Lights, Merlin, North by Northwest | arousal/valence reference | dynamic FC arousal baseline |
| Tier 2 | Koide-Majima/Nishimoto | fMRI | 3 h emotional audiovisual movies | 80 emotion labels | high-dimensional secondary benchmark if accessible |
| Tier 2 | CNeuroMod/Algonauts 2025 | dense fMRI, 1,000 parcels in challenge | video/audio/transcripts, long movie/sitcom stimuli | no primary emotion labels | TRIBE-style encoding and alignment reference |
| Tier 2 | BOLD Moments | fMRI | 1,102 short naturalistic videos | object/scene/action/sentence metadata | auxiliary dynamic visual-event encoding |
| Tier 2 | Spacetop | fMRI + autonomic physiology | naturalistic movie + tasks | not primarily emotion labels | future physiology-rich expansion |
| Tier 3 | 101 Dalmatians | fMRI | audiovisual/auditory/visual movie variants | semantic/event descriptors | future multimodal generalization |

Working prioritization:

1. **Start with Horikawa + Emo-FilM + HCP 7T movie.**
2. Add **Affective Videos** if a fast arousal/valence sanity check is needed.
3. Add **REELMO** for context/reasoning and stimulus-side affect trajectories.
4. Treat **CNeuroMod/Algonauts** as the TRIBE/alignment engineering reference, not the first emotion downstream dataset.

### Model Candidates

| Priority | Model family | Examples | Native input/output | First NetFeeliX use |
|---|---|---|---|---|
| Tier 0 | Simple brain baselines | ridge, elastic-net, PCA/ICA, ROI windows | fMRI -> target | minimum bar for every dataset |
| Tier 0 | Dynamic brain baselines | dynamic FC, CPM-style arousal model | fMRI dynamics -> arousal/valence | test whether simple dynamics already work |
| Tier 0 | Existing BFM probes | SwiFT, BrainLM, Brain-JEPA | fMRI -> representation | frozen probe and small head |
| Tier 0 | Small in-house temporal encoder | parcel MLP/TCN/Transformer | fMRI window -> representation | scratch baseline and HCP pretraining backbone |
| Tier 1 | Resting-to-task bridge | SwiFUN | rsfMRI -> task activation | emotion-related contrast bridge if checkpoint/data fit |
| Tier 1 | HCP movie-pretrained encoder | NetFeeliX parcel encoder | HCP movie fMRI -> representation | compare movie pretraining vs generic BFM transfer |
| Tier 1 | Stimulus-only encoders | V-JEPA2, CLIP, VideoMAE, Whisper, Wav2Vec, sentence transformer, LLM embeddings | video/audio/text -> representation | test how much emotion is stimulus-explained |
| Tier 1 | TRIBE-style fusion | TRIBE, TRIBE v2, Algonauts pipeline | video/audio/text -> predicted fMRI | stimulus-brain alignment and model surgery |
| Tier 1 | Alignment models | dual encoder, contrastive, regression, CKA/RSA, JEPA-style | fMRI + stimulus -> shared latent | main NetFeeliX development track if pilot supports it |
| Tier 2 | Brain-tuned affective VLM/LLM | AffectGPT-style embeddings, MLLM rationale embeddings, small adapters | stimulus affect embedding + fMRI latent | reasoning/context extension |
| Tier 2 | Large raw 4D BFMs | NeuroSTORM, Omni-fMRI, Brain-DiT | raw 4D fMRI -> representation | high-value baseline if code/weights are usable |
| Tier 3 | Cross-modality neural FMs | REVE, Brain-OF, LaBraM-style EEG FMs | EEG/fMRI/MEG -> representation | future physiology or neural-signal expansion |

First model order:

1. Non-deep fMRI baseline.
2. Frozen existing BFM probe.
3. Small in-house parcel temporal encoder.
4. HCP movie-pretrained parcel encoder.
5. Stimulus-only emotion model.
6. First brain-stimulus alignment model.
7. Brain-tuned affective VLM/LLM adapter only if stimulus/context pilots are promising.

### Task Candidates

| Task group | Task | Input | Target/output | Why it matters |
|---|---|---|---|---|
| Dataset readiness | inventory/access check | dataset metadata | usable/not usable; first target | prevents overplanning around inaccessible data |
| Preprocessing | fMRI window construction | fMRI runs | parcel/window tensors | common input for simple and deep baselines |
| Pretraining | masked fMRI modeling | HCP movie fMRI | reconstructed masked segments | tests generic naturalistic fMRI representation |
| Pretraining | JEPA/future latent prediction | HCP movie fMRI | future/held-out latent | tests predictive brain dynamics |
| Pretraining | subject-invariant learning | multi-subject fMRI | subject-shared latent | tests transfer across participants |
| Downstream regression | arousal | fMRI or stimulus features | continuous arousal | easiest sanity-check target |
| Downstream regression | valence | fMRI or stimulus features | continuous valence | harder affective dimension |
| Downstream classification | discrete emotion | fMRI or stimulus features | category or multi-label emotion | tests category-like structure |
| Downstream embedding | high-dimensional emotion vector | fMRI or stimulus features | emotion rating vector | main Horikawa-style affect geometry task |
| Component modeling | appraisal/component prediction | fMRI + stimulus | Emo-FilM component ratings | bridge toward reasoning/context |
| Context modeling | short vs long window prediction | stimulus/fMRI windows | emotion target | tests whether temporal context helps |
| Stimulus-side reasoning | caption/rationale embedding prediction | video/audio/text | MLLM-derived rationale/cue embedding | brings affective reasoning without overclaiming fMRI language decoding |
| Alignment | brain-stimulus latent matching | fMRI + video/audio/text | matched latent or retrieval | tests shared representation |
| Encoding auxiliary | stimulus-to-fMRI prediction | video/audio/text | parcel/voxel response | TRIBE-style auxiliary objective |
| Transfer | cross-subject transfer | train subjects -> held-out subject | emotion metrics | tests subject generalization |
| Transfer | cross-stimulus/movie transfer | train clips/movies -> held-out clips/movies | emotion metrics | tests content generalization |
| Transfer | cross-dataset transfer | one dataset -> another compatible dataset | emotion metrics | strongest representation test |

### First Decision Matrix

| Candidate study | Dataset | Model | Task | Decision it answers |
|---|---|---|---|---|
| Study 1A | Affective Videos or Horikawa | ridge/dynamic FC | arousal/valence or emotion vector | what is the minimum baseline? |
| Study 1B | Horikawa | frozen BFM + linear head | high-dimensional emotion vector | do existing BFMs transfer to rich emotion geometry? |
| Study 1C | HCP 7T movie -> Horikawa | parcel temporal encoder | pretrain then probe | does movie pretraining help downstream emotion? |
| Study 1D | Emo-FilM | brain-only vs stimulus-only | component/appraisal/emotion ratings | which source explains naturalistic affect? |
| Study 1E | REELMO or Emo-FilM | stimulus-only + MLLM rationale embeddings | context/rationale target | is reasoning/context useful as auxiliary supervision? |
| Study 1F | Horikawa or Emo-FilM | dual brain-stimulus encoder | contrastive/regression alignment | does alignment improve emotion representation? |

Recommended first cut:

1. **Dataset**: Horikawa, Emo-FilM, HCP 7T movie, plus Affective Videos as a sanity check.
2. **Model**: ridge/dynamic FC, frozen BFM probe, small parcel encoder, stimulus-only baseline.
3. **Task**: arousal/valence sanity check, high-dimensional emotion vector prediction, component/appraisal prediction, and first alignment retrieval/regression.

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
