# FEELIN Framework

## Canonical Direction

FEELIN is a **model-development project for emotion-aware brain representation learning**. It is not an emotion theory paper. Emotion theory should appear only as a short constraint on target design: emotion labels are noisy, dynamic, stimulus-dependent, and multi-component, so the model should be evaluated on arousal, valence, discrete categories, and high-dimensional emotion vectors rather than on one fixed label.

One-line framing:

**FEELIN treats emotion representation as a model-development problem over brain dynamics, naturalistic stimulus dynamics, and affective annotations. Initial benchmarks decide which architecture and training objectives are worth developing.**

External-facing pitch:

> FEELIN will not start by claiming a complete emotion foundation model. It will first build an initial benchmark around SwiFT, naturalistic movie/story fMRI datasets, TRIBE v2-style stimulus-to-brain models, and affective LLM/VLM representations. The benchmark asks which information source helps which emotion target. The model-development track is then chosen from four directions: SwiFT emotion adaptation, naturalistic fMRI continued pretraining, TRIBE-SwiFT stimulus-brain alignment, and brain-tuned affective LLM/VLM adapters.

## v4 Reframing (2026-06-02)

The canonical direction above is preserved. The Big Question axis moves from the v3 framing ("does fMRI + video fusion beat the video-only baseline") to **transfer**. All measured results are preserved (`reports/phase1_wrapup/`, `docs/masterplan_v2.md` section 7.0).

**Two distinct questions.** Question A (does the brain beat video features on the same stimulus) was answered by the Phase 1 frozen probe and Phase 2 joint inference: it does not. The crowd-sourced valence and arousal labels are by construction a property of the stimulus video, so a video encoder such as CLIP wins trivially. Question B (does a brain emotion representation learned on Horikawa transfer to new subjects, datasets, and taxonomies) is the real foundation-model question. Video is not a competitor in Question B but a supervision oracle, since video cannot be applied to a new fMRI dataset's brain data.

**Scientific grounding (Horikawa, Cowen, Keltner, Kamitani 2020, iScience).** Emotion category representations predicted cortical and subcortical responses better than affective dimensions such as valence, and outperformed visual and semantic covariates (that is, video features) in transmodal regions. High-dimensional categorical and appraisal targets, not scalar valence and arousal, are the battleground where brain-specific signal lives.

**Five v4 sub-questions.** SQ1 transfer (main), SQ2 supervision richness, SQ3 representation geometry, SQ4 data efficiency, SQ5 where (label-free). All are representation questions and none assume the brain must beat video.

**Target hierarchy.** Cowen 34-category, Cowen 14-dimension, and open-vocabulary emotion-text embedding are promoted to primary targets. Valence and arousal are demoted to a reference axis.

**Cross-dataset evaluation.** (1) shared text-embedding zero-shot (main), (2) label-space intersection (safe baseline), (3) MLLM (OV-MER / AffectGPT) universal annotator, (4) representational alignment (label-free). Metadata-poor independent datasets remain evaluable. Horikawa is trained on Cowen gold norms, while OV-MER / AffectGPT serve only as a label-harmonization tool for target datasets without such norms.

Forward plan: `docs/masterplan_v2.md` (v4).

## Model-Development Problem

The main question is not "what is emotion?" The main question is:

```text
Which model architecture and learning objective produce the most transferable
brain-based representation of emotion under small downstream fMRI datasets?
```

FEELIN decomposes this into eight testable modeling questions.

| Question | Modeling interpretation | First test |
|---|---|---|
| Do generic BFMs transfer to emotion? | Emotion may already be encoded in broad fMRI representations. | Frozen BFM probe and adapter tuning. |
| Which neural representation matters? | Whole-brain 4D modeling may not be optimal; specific voxels, parcels, ROIs, networks, or dynamic connectivity may carry stronger emotion signal. | Whole-brain SwiFT/NeuroSTORM vs ROI/parcel ridge vs voxel-weighted sparse models vs network-restricted models. |
| What temporal window length should SwiFT use? | Emotion may depend on short evoked responses, delayed hemodynamics, or longer context. Pretrained SwiFT also has checkpoint-native sequence-length constraints. | All observed Horikawa windows, standardized SL5/SL10/SL20/SL40, pretrained-native SL20/SL40, and scratch SL5/SL10/SL20/SL40. |
| Does naturalistic fMRI pretraining help? | Emotion targets arise as vision, audio, language, social cues, and narrative context unfold over time. | Resting/generic SwiFT vs HCP/CNeuroMod/StudyForrest-style pretraining. |
| Is emotion-labeled pretraining needed? | Naturalistic SSL may not directly learn emotion target structure. | Horikawa/Emo-FilM/Affective Videos/IAPS/NeuroEmo multi-task pretraining and held-out transfer. |
| Which pretraining curriculum is best? | We need to decide whether to learn stimulus dynamics first, emotion label structure first, or both in sequence. | Naturalistic-only vs emotion-labeled-only vs naturalistic-to-emotion two-stage comparison. |
| Does stimulus-brain alignment help? | Emotion depends on the shared structure between stimulus dynamics and brain dynamics. | TRIBE-style stimulus features aligned with fMRI latents. |
| Can affective AI be brain-tuned? | LLM/VLM emotion features may improve when regularized by neural responses. | Small adapter or distillation from brain-aligned latent spaces. |

The project should stay comparative. Arousal, valence, discrete emotion, and high-dimensional category vectors may prefer different architectures and brain representations. A useful result can be a pattern of failures, not only one winning model. SwiFT-first is a starting strategy, not a fixed conclusion. If SwiFT is not the right backbone, FEELIN should pivot to the neural representation or architecture that works.

## Literature Landscape for Model Development

### fMRI Brain Foundation Models

SwiFT, BrainLM, Brain-JEPA, NeuroSTORM, Omni-fMRI, Brain-DiT, and related models define the brain-side foundation-model space. FEELIN is **SwiFT-first** because SwiFT is the local lab backbone that can be modified, pretrained, and inserted into multimodal architectures. The other BFMs define comparison points.

- **SwiFT**: direct 4D fMRI spatiotemporal window attention.
- **BrainLM**: masked prediction over brain activity recordings.
- **Brain-JEPA**: joint-embedding predictive learning with spatiotemporal masking.
- **NeuroSTORM**: large-scale raw 4D fMRI pretraining with lightweight adaptation.
- **Omni-fMRI / Brain-DiT**: future references for atlas-free or multi-state pretraining.
- **SwiFUN**: resting-state to task-activation bridge, useful because emotion-related task contrasts are included in its evaluation.

For FEELIN, these are not final solutions. They are screening baselines that test whether generic brain representations already carry emotion-relevant information.

### Stimulus-to-Brain Encoding and Alignment

TRIBE and TRIBE v2 are not fMRI encoders in the same native sense as SwiFT or BrainLM. They are **stimulus-to-brain encoding models**: video, audio, and language features are used to predict fMRI responses. This distinction matters, but it does not make comparison impossible.

FEELIN should compare TRIBE-style and SwiFT-style models through a shared interface:

| Interface | Input | Model form | Objective |
|---|---|---|---|
| Brain-only decoding | fMRI | SwiFT/BFM encoder + emotion head | emotion prediction |
| Stimulus-only decoding | video/audio/text | TRIBE-style fusion + emotion head | emotion prediction |
| Encoding-regularized brain model | fMRI + stimulus during training | fMRI encoder + stimulus auxiliary loss | emotion + alignment |
| Bidirectional aligned model | fMRI and/or stimulus | shared brain-stimulus latent | emotion + fMRI prediction + contrastive/JEPA loss |

Thus the correct framing is not "TRIBE cannot be compared with SwiFT." The correct framing is: **their native input-output directions differ, so FEELIN compares modified variants with harmonized targets, splits, and heads.**

Concrete model-surgery variants:

1. **SwiFT-decoder baseline**: fMRI to emotion.
2. **TRIBE-emotion baseline**: video/audio/text to emotion.
3. **TRIBE-to-SwiFT distillation**: fMRI encoder learns stimulus-derived latent structure.
4. **SwiFT-to-TRIBE alignment**: fMRI latents align with TRIBE-style stimulus latents.
5. **Bidirectional FEELIN**: shared latent learns stimulus-to-brain encoding and brain-to-emotion decoding together.

### Affective Computing Foundation Models

Affective computing is moving toward foundation models: LLM/VLM/MLLM emotion recognition, emotion reasoning, multimodal affective benchmarks, and affective generation. Schuller et al. describe this as a foundation-model disruption in affective computing; MMAFFBen and related work show that affective reasoning is now evaluated across text, image, video, and languages.

This creates an opening for FEELIN. Affective AI has large external models but little brain grounding. fMRI BFMs have brain representations but rarely organize pretraining around emotion. FEELIN can bridge them by asking whether brain responses to emotional/naturalistic stimuli can regularize affective AI representations.

Recent MLLM benchmarks such as MME-Emotion, EmoBench-M, Beyond Emotion Recognition, and EIBench also show that affective computing is shifting from "which emotion label?" to emotional understanding, trigger inference, and contextual reasoning. FEELIN should not simply copy these benchmarks, but they are useful for designing richer stimulus-side affective embeddings and auxiliary targets.

Affective-computing task design is therefore broader than classification versus
regression. A useful ladder is:

| Task type | Output | FEELIN use |
|---|---|---|
| Sentiment/valence classification | positive/neutral/negative or ordinal class | low-dimensional IAPS/Affective Videos check |
| Discrete emotion classification | single label such as anger, fear, joy | baseline, but may over-simplify mixed affect |
| Multi-label / distribution prediction | multiple labels or emotion probability vector | closest to Horikawa-style high-dimensional emotion targets |
| Dimensional regression | arousal, valence, dominance, intensity | first sanity ladder for fMRI transfer |
| Continuous-time affect tracking | frame/window-level affect trajectory | relevant for Emo-FilM, REELMO, and movie-window design |
| Cue/cause/reasoning | trigger, intent, appraisal, rationale | stimulus-side auxiliary target or alignment target |
| Affective captioning / QA | natural-language emotion description or answer | convert to embedding/retrieval targets before making brain-generation claims |

Thus FEELIN should not choose only one of classification or regression. It
should start with stable arousal/valence/category targets, move toward
multi-label/high-dimensional emotion geometry and component trajectories, and
use reasoning/caption targets mainly to enrich stimulus-side representations.

Top-conference work makes this especially clear. ICML 2025 AffectGPT reframes multimodal emotion recognition as descriptive emotion understanding with large-scale fine-grained captions and a unified benchmark. NeurIPS 2025 VidEmo uses affective-tree reasoning guidance for emotion-centric video foundation modeling. ICLR 2026 AVERE, MME-Emotion, EmotionHallucer, and HitEmotion target audiovisual cue grounding, emotion hallucination, emotional-intelligence evaluation, and Theory-of-Mind-guided multimodal emotion reasoning. The practical lesson for FEELIN is that emotion models should explain or ground affective judgments in temporal context, not only predict labels.

### Brain-Tuning and Brain-Aligned AI

Brain-Score Vision, Brain-Score Language, EEG representational alignment, brain-tuning speech/language models, multi-participant brain-tuning, and fMRI language-encoding scaling laws show that neural data can be used not only to evaluate AI models but also to tune or regularize them. For FEELIN, this supports a cautious but concrete extension:

```text
affective LLM/VLM representation + fMRI response during emotional stimuli
    -> brain-aligned affective adapter or distilled affective embedding
```

Because fMRI data are small, this should use adapters, contrastive alignment, or distillation rather than full LLM/VLM fine-tuning.

SED-GPT is a useful nearby precedent because it combines fMRI, long-sequence semantic decoding, and emotion distributions with LLM-style priors. It should be cited as early evidence that semantic/emotional fMRI decoding is possible, not as evidence that an fMRI emotion foundation model already exists.

### Gap Statement

There is no mature fMRI emotion foundation model direction yet. Existing fMRI BFMs are usually generic; neural-signal FMs may include emotion as one downstream benchmark; affective computing FMs usually lack brain grounding; stimulus-to-brain models usually optimize fMRI encoding rather than emotion representation. FEELIN fills this gap by making **screening-benchmark-driven model development for emotion-aware brain/stimulus representation** the central objective.

## Initial Benchmark Strategy

The first phase should avoid expensive end-to-end architecture claims. It should build a comparable benchmark surface across datasets, models, and targets.

Benchmark questions:

1. Which datasets and targets are usable after access, preprocessing, and temporal alignment checks?
2. What do non-deep brain baselines achieve?
3. Do frozen BFM representations predict arousal, valence, discrete categories, or high-dimensional emotion vectors?
4. Are stimulus-only features stronger than brain-only features for some targets?
5. Does brain-stimulus alignment improve high-dimensional or cross-dataset transfer?
6. Which direction justifies two-month model development?

Minimum benchmark table:

| Dataset | Target | Brain-only baseline | Stimulus-only baseline | Existing BFM | Alignment model | Notes |
|---|---|---|---|---|---|---|
| Horikawa | high-dimensional emotion vector | planned | planned | planned | planned | core downstream |
| Emo-FilM | emotion/appraisal/component ratings | planned | planned | planned | planned | modern naturalistic benchmark |
| Affective Videos | valence/arousal | planned | optional | planned | optional | lightweight sanity check |
| REELMO | time-resolved affect reports; fMRI participants watched Jojo Rabbit | optional | planned | limited one-movie fMRI | optional | strong stimulus-side supervision |
| HCP 7T movie | pretraining objective | planned | planned features | planned | planned | naturalistic pretraining source |

## Horikawa vs. Reasoning/Context Understanding

Horikawa should not be forced to carry the whole reasoning/context story. Its strength is different: it provides a high-dimensional, visually evoked emotion space with fMRI responses to many short videos. In FEELIN, Horikawa is best used as a **brain-side affect geometry probe**.

Reasoning and context understanding require longer temporal context, cue grounding, narrative structure, and sometimes natural-language rationales. These should come from other sources:

- **Emo-FilM**: component/appraisal-style annotations and naturalistic film context.
- **REELMO**: long movie trajectories, 20 emotion labels, stimulus features, subtitles, and fMRI in which participants watched Jojo Rabbit.
- **HCP/CNeuroMod/StudyForrest/Narratives movie-story data**: naturalistic fMRI pretraining, modality/context ablations, and stimulus-brain alignment experiments.
- **Affective MLLM benchmarks/models**: descriptive emotion captions, cue-emotion QA, rationale embeddings, and hallucination diagnostics.

The bridge is therefore staged:

1. Use Horikawa to test whether brain encoders learn high-dimensional affective geometry.
2. Use Emo-FilM/REELMO to test whether temporal context and appraisal/component targets improve representation.
3. Use MLLM-derived rationale or cue embeddings as stimulus-side auxiliary targets.
4. Align fMRI latents with emotion label embeddings first, then with context/rationale embeddings.
5. Evaluate context by comparing short-window, long-window, and ablated-stimulus models.

This keeps the project coherent: Horikawa answers "does the brain representation capture rich emotion geometry?", while the reasoning/context track asks "can naturalistic stimulus-brain alignment explain why an affective state emerges over time?"

## Model Development Tracks

### Track A: SwiFT-First BFM Transfer

Goal: test whether SwiFT and related pretrained brain models already contain emotion-relevant structure.

Order:

1. Frozen encoder + ridge/linear/MLP head.
2. Adapter or LoRA-style tuning where supported.
3. Partial or full fine-tuning only after stable probes.

Primary model: SwiFT. Comparison models: BrainLM, Brain-JEPA, SwiFUN, NeuroSTORM if code/weights are accessible.

Decision rule: if frozen/adapted BFM representations outperform simple baselines on more than arousal, prioritize adapter and fine-tuning experiments. If ROI/parcel ridge, voxel-weighted linear models, network-restricted models, another BFM, or stimulus-aligned models are more stable under matched splits and targets, deprioritize or discard SwiFT-centered development. The goal is not to defend SwiFT; the goal is to find the model and neural representation that best support emotion representation.

### Track A0: Neural Representation Search

Goal: identify which brain representation is actually useful for emotion prediction and affective geometry. Whole-brain 4D input may preserve the most information, but small fMRI datasets can favor lower-noise, better-harmonized, or more interpretable representations.

| Representation | Example | Why test it |
|---|---|---|
| Whole-brain 4D volume | SwiFT, NeuroSTORM | preserves distributed spatiotemporal patterns |
| Parcel/ROI time series | Schaefer/Tian, HCP-MMP, emotion/salience/visual ROIs | faster, more stable, easier to harmonize across datasets |
| Voxel-weighted model | ridge, elastic-net, sparse linear model, stability selection | identifies which voxels contribute to each emotion target |
| Network-restricted model | visual, auditory, salience, DMN, limbic/control networks | tests whether emotion prediction depends on specific systems |
| Dynamic connectivity | sliding-window FC, temporal graph features | tests whether arousal/context dynamics are better captured by FC |
| Subject-adapted representation | subject adapter, hyperalignment, shared response model | separates individual response geometry from shared affect structure |
| Stimulus-aligned latent | fMRI aligned with TRIBE/V-JEPA/audio/text latents | tests whether emotion is better represented as shared brain-stimulus structure |

This track should produce both performance and interpretability tables: which
target is predicted by which region, network, time window, and stimulus modality.

### Track A1: SwiFT Temporal-Length and Padding Comparison

Goal: decide whether emotion representation needs short event-level response,
longer temporal context, or checkpoint-native SwiFT sequence length.

This track is necessary because Horikawa should not be treated as exactly-5TR
only. The local preprocessing contains variable-length response windows. The old
5TR setup was a legacy subset created by the loader/split design, not the full
dataset definition.

Compare:

| Condition | Lengths | Why |
|---|---|---|
| all observed windows | 5-47 observed frames | use all available data when the model can support it |
| standardized windows | SL5, SL10, SL20, SL40 | controlled temporal-context comparison |
| pretrained-native SwiFT | SL20, SL40 if matching checkpoints exist | clean checkpoint-compatible fine-tuning |
| pretrained SwiFT with short observed windows | 5/10/20 observed frames padded or cropped to native SL | explicit adaptation and padding sensitivity test |
| scratch SwiFT | SL5, SL10, SL20, SL40 | test sequence-length effect without pretrained-weight constraints |

Rule: pretrained SwiFT fine-tuning should normally keep the checkpoint-native
sequence length. Mismatched downstream windows are allowed only as explicit
adaptation experiments with padding/mask/crop behavior logged.

### Track B: Pretraining Source and Curriculum

Goal: test which pretraining source and curriculum improves emotion transfer. This is not the vague claim that movie data is automatically better than rest, and it is also not the claim that adding emotion labels is sufficient. The precise hypothesis is that, before or alongside learning from small emotion-labeled fMRI datasets, SwiFT may need either stimulus-locked brain dynamics driven by visual, auditory, language, social, and narrative cues, or target-aware affect structure from Horikawa/Emo-FilM/Affective Videos/IAPS/NeuroEmo.

Compare three pretraining families:

1. naturalistic SSL pretraining: learn stimulus-locked dynamics from movie/story fMRI;
2. emotion-labeled pretraining: use emotion labels, high-dimensional vectors, and component/appraisal targets in supervised or weakly supervised multi-task learning;
3. two-stage pretraining: learn naturalistic dynamics first, then specialize on emotion-labeled datasets.

Start with parcel-level time series. Add raw 4D volumes only after simple pipelines work.

Dataset choice should follow the hypothesis:

| Source | Role | Testable question |
|---|---|---|
| HCP 7T movie | large-subject continued pretraining | does stimulus-locked pretraining improve Horikawa/Emo-FilM transfer? |
| CNeuroMod / Algonauts | multimodal encoding/alignment | does video/audio/transcript-to-fMRI alignment help emotion targets? |
| StudyForrest | long-film continuity | does coherent audiovisual narrative improve temporal representation? |
| Narratives | language/story context | can narrative context help without visual cues? |
| 101 Dalmatians | modality control | do visual-only, auditory-only, and audiovisual conditions differ for emotion transfer? |
| Horikawa / Emo-FilM / Affective Videos / IAPS / NeuroEmo | emotion-labeled pretraining | does supervised affective pretraining improve held-out emotion transfer? |

Candidate objectives:

- masked fMRI segment modeling,
- temporal contrastive learning,
- JEPA-style latent prediction,
- subject-invariant contrastive learning,
- future brain-state prediction,
- optional stimulus-conditioned prediction,
- multi-task emotion label/vector/component prediction,
- emotion geometry alignment across datasets.

Decision rule: if naturalistic-pretrained encoders beat generic BFM transfer on Horikawa/Emo-FilM and improve high-dimensional/component targets beyond arousal or low-level visual/audio shortcuts, scale movie/story pretraining. If emotion-labeled pretraining improves held-out emotion dataset transfer, scale multi-dataset affective pretraining and task-specific heads. If two-stage pretraining is best, prioritize a curriculum of naturalistic dynamics first and emotion specialization second. If gains are absent or shortcut-driven, prioritize emotion-specific heads, subject adapters, TRIBE-style alignment, and target redesign.

### Track C: Stimulus-Brain-Emotion Alignment

Goal: learn emotion as a shared latent between naturalistic stimuli and brain dynamics.

Candidate architecture:

```text
Stimulus path:
    video/audio/text -> TRIBE-style temporal fusion -> z_stim

Brain path:
    fMRI window -> SwiFT/BFM/temporal encoder -> z_brain

Shared latent:
    align(z_stim, z_brain)

Heads:
    z_brain -> emotion
    z_stim -> emotion
    z_stim -> predicted fMRI
    z_brain -> future/reconstructed fMRI
```

Candidate features:

- video: V-JEPA2, VideoMAE, CLIP frame features,
- audio: Wav2Vec2/Wav2Vec-BERT, Whisper, spectrogram baselines,
- text: subtitles/captions with sentence-transformer or LLM embeddings.

Decision rule: if stimulus-only features or alignment losses help high-dimensional targets, prioritize TRIBE-style model surgery over brain-only pretraining.

### Track D: Brain-Tuned Affective LLM/VLM

Goal: use brain responses as a biological alignment signal for external affective models.

Feasible first variants:

1. Train a small adapter so affective VLM/LLM embeddings predict fMRI latents.
2. Add a brain-geometry regularizer to an emotion classifier.
3. Distill a shared stimulus-brain latent into a lightweight affective embedding.
4. Use fMRI-derived arousal or high-dimensional estimates as auxiliary pseudo-labels for movie segments.

Decision rule: activate this track if stimulus-side affective embeddings are strong or if brain-stimulus alignment is measurable.

## Data Strategy

| Role | Datasets | Purpose |
|---|---|---|
| Naturalistic pretraining | HCP 7T movie, CNeuroMod/Algonauts, StudyForrest, Narratives, 101 Dalmatians | test stimulus-locked fMRI dynamics, modality/context ablations, and alignment hypotheses |
| Core emotion downstream | Horikawa, Emo-FilM | evaluate high-dimensional and naturalistic emotion transfer |
| Lightweight emotion downstream | Affective Videos, IAPS fMRI, NeuroEmo, Koide-Majima if accessible | valence/arousal/category screening benchmark |
| Static-image affect extension | NSD, OASIS labels, image affect models | large static-image fMRI representation and affective pseudo-labeling |
| Stimulus-side affective supervision | REELMO, MMAFFBen/MMAFFIn, affective LLM/VLMs | build or validate stimulus emotion trajectories |
| Auxiliary encoding | BOLD Moments, CNeuroMod, Algonauts 2025, Spacetop as future expansion | test video/audio/text-to-fMRI alignment and physiology-rich transfer |

Naturalistic pretraining and Horikawa/Emo-FilM downstream evaluation remain central. HCP is the first candidate, not the only candidate. Other datasets should be added when they reduce uncertainty about modality, narrative context, alignment, or low-level shortcut risks.

## Evaluation Ladder

Report targets as an increasing-difficulty ladder:

1. **Arousal regression**: early sanity check; likely most transferable.
2. **Valence regression**: harder affective dimension.
3. **Discrete emotion prediction**: category-like structure.
4. **High-dimensional emotion vector prediction**: main rich-representation test.
5. **Cross-dataset transfer**: strongest evidence against dataset-specific shortcuts.

Metrics:

- regression: Pearson r, Spearman r, MAE/MSE, subject-wise confidence intervals,
- classification/multi-label: macro F1, AUROC, balanced accuracy, top-k accuracy,
- representation: RSA/CKA, retrieval, explained variance,
- fMRI encoding: parcel/voxel correlation and noise-ceiling-normalized score when available.

## Expected Contribution

- A structured benchmark comparing generic BFM transfer, naturalistic movie/story fMRI pretraining, and stimulus-brain alignment for emotion prediction.
- A practical two-month roadmap that can produce useful results even if the ambitious model is not yet ready.
- A taxonomy separating fMRI encoders, stimulus-to-brain encoding models, and emotion-aware aligned representation models.
- A model-development bridge between affective computing foundation models and affective neuroscience.
- A clear decision framework for when to pursue adapters, naturalistic pretraining, TRIBE-style alignment, or brain-tuned affective VLM/LLM.

## Key References

| Area | References | Role |
|---|---|---|
| fMRI BFMs | SwiFT, SwiFUN, BrainLM, Brain-JEPA, NeuroSTORM, Omni-fMRI, Brain-OF | brain-side baselines and pretraining precedents |
| Stimulus-to-brain | TRIBE, TRIBE v2, VIBE, Algonauts 2025, Hu and Mohsenzadeh | multimodal alignment and fMRI response prediction |
| Naturalistic fMRI | HCP 7T movie, CNeuroMod, StudyForrest, Narratives, 101 Dalmatians, BOLD Moments | movie/story pretraining, modality/context ablations, and naturalistic dynamics |
| Emotion fMRI | Horikawa, Koide-Majima, Emo-FilM, Ke et al., Affective Videos, NeuroEmo, REELMO | downstream targets and target difficulty |
| Affective FM | Schuller et al., LLM affect survey, MLLM emotion reasoning survey, MMAFFBen, MME-Emotion, EmoBench-M, EIBench | external affective AI and emotion-reasoning trend |
| Top-conference affective reasoning | ICML 2025 AffectGPT; NeurIPS 2025 VidEmo; ICLR 2026 AVERE, EmotionHallucer, HitEmotion/MME-Emotion | label prediction is shifting toward cue grounding, rationale, context, and hallucination control |
| Brain tuning | Brain-Score Vision/Language, EEG representational alignment, brain-tuning speech LMs, scaling laws, SED-GPT | brain-aligned AI and fMRI semantic/emotion decoding precedent |
