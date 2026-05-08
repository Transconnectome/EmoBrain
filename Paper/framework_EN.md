# NetFeeliX Framework

## Canonical Direction

NetFeeliX is a **model-development project for emotion-aware brain representation learning**. It is not an emotion theory paper. Emotion theory should appear only as a short constraint on target design: emotion labels are noisy, dynamic, stimulus-dependent, and multi-component, so the model should be evaluated on arousal, valence, discrete categories, and high-dimensional emotion vectors rather than on one fixed label.

One-line framing:

**NetFeeliX treats emotion representation as a model-development problem over brain dynamics, naturalistic stimulus dynamics, and affective annotations. Pilot benchmarks decide which architecture and training objectives are worth developing.**

Professor-facing pitch:

> NetFeeliX will not start by claiming a complete Emotion Foundation Model. It will first benchmark existing Brain Foundation Models, TRIBE-style stimulus-to-brain encoding models, naturalistic movie fMRI datasets, and affective LLM/VLM representations in one pilot framework. The pilot asks which information source helps which emotion target. The model-development track is then chosen from four directions: existing BFM transfer, HCP movie pretraining, TRIBE-SwiFT stimulus-brain alignment, and brain-tuned affective LLM/VLM adapters.

## Model-Development Problem

The main question is not "what is emotion?" The main question is:

```text
Which model architecture and learning objective produce the most transferable
brain-based representation of emotion under small downstream fMRI datasets?
```

NetFeeliX decomposes this into four testable modeling questions.

| Question | Modeling interpretation | First test |
|---|---|---|
| Do generic BFMs transfer to emotion? | Emotion may already be encoded in broad fMRI representations. | Frozen BFM probe and adapter tuning. |
| Does movie fMRI pretraining help? | Emotion during films is stimulus-locked and temporally structured. | HCP movie-pretrained encoder vs resting-state/generic BFM. |
| Does stimulus-brain alignment help? | Emotion depends on the shared structure between stimulus dynamics and brain dynamics. | TRIBE-style stimulus features aligned with fMRI latents. |
| Can affective AI be brain-tuned? | LLM/VLM emotion features may improve when regularized by neural responses. | Small adapter or distillation from brain-aligned latent spaces. |

The project should stay comparative. Arousal, valence, discrete emotion, and high-dimensional category vectors may prefer different architectures. A useful result can be a pattern of failures, not only one winning model.

## Literature Landscape for Model Development

### fMRI Brain Foundation Models

SwiFT, BrainLM, Brain-JEPA, NeuroSTORM, Omni-fMRI, Brain-DiT, and related models define the brain-side foundation-model space. They differ in input representation, objective, and compute cost:

- **SwiFT**: direct 4D fMRI spatiotemporal window attention.
- **BrainLM**: masked prediction over brain activity recordings.
- **Brain-JEPA**: joint-embedding predictive learning with spatiotemporal masking.
- **NeuroSTORM**: large-scale raw 4D fMRI pretraining with lightweight adaptation.
- **Omni-fMRI / Brain-DiT**: future references for atlas-free or multi-state pretraining.
- **SwiFUN**: resting-state to task-activation bridge, useful because emotion-related task contrasts are included in its evaluation.

For NetFeeliX, these are not final solutions. They are pilot baselines that test whether generic brain representations already carry emotion-relevant information.

### Stimulus-to-Brain Encoding and Alignment

TRIBE and TRIBE v2 are not fMRI encoders in the same native sense as SwiFT or BrainLM. They are **stimulus-to-brain encoding models**: video, audio, and language features are used to predict fMRI responses. This distinction matters, but it does not make comparison impossible.

NetFeeliX should compare TRIBE-style and SwiFT-style models through a shared interface:

| Interface | Input | Model form | Objective |
|---|---|---|---|
| Brain-only decoding | fMRI | SwiFT/BFM encoder + emotion head | emotion prediction |
| Stimulus-only decoding | video/audio/text | TRIBE-style fusion + emotion head | emotion prediction |
| Encoding-regularized brain model | fMRI + stimulus during training | fMRI encoder + stimulus auxiliary loss | emotion + alignment |
| Bidirectional aligned model | fMRI and/or stimulus | shared brain-stimulus latent | emotion + fMRI prediction + contrastive/JEPA loss |

Thus the correct framing is not "TRIBE cannot be compared with SwiFT." The correct framing is: **their native input-output directions differ, so NetFeeliX compares modified variants with harmonized targets, splits, and heads.**

Concrete model-surgery variants:

1. **SwiFT-decoder baseline**: fMRI to emotion.
2. **TRIBE-emotion baseline**: video/audio/text to emotion.
3. **TRIBE-to-SwiFT distillation**: fMRI encoder learns stimulus-derived latent structure.
4. **SwiFT-to-TRIBE alignment**: fMRI latents align with TRIBE-style stimulus latents.
5. **Bidirectional NetFeeliX**: shared latent learns stimulus-to-brain encoding and brain-to-emotion decoding together.

### Affective Computing Foundation Models

Affective computing is moving toward foundation models: LLM/VLM/MLLM emotion recognition, emotion reasoning, multimodal affective benchmarks, and affective generation. Schuller et al. describe this as a foundation-model disruption in affective computing; MMAFFBen and related work show that affective reasoning is now evaluated across text, image, video, and languages.

This creates an opening for NetFeeliX. Affective AI has large external models but little brain grounding. fMRI BFMs have brain representations but rarely organize pretraining around emotion. NetFeeliX can bridge them by asking whether brain responses to emotional/naturalistic stimuli can regularize affective AI representations.

Recent MLLM benchmarks such as MME-Emotion, EmoBench-M, Beyond Emotion Recognition, and EIBench also show that affective computing is shifting from "which emotion label?" to emotional understanding, trigger inference, and contextual reasoning. NetFeeliX should not simply copy these benchmarks, but they are useful for designing richer stimulus-side affective embeddings and auxiliary targets.

Top-conference work makes this especially clear. ICML 2025 AffectGPT reframes multimodal emotion recognition as descriptive emotion understanding with large-scale fine-grained captions and a unified benchmark. NeurIPS 2025 VidEmo uses affective-tree reasoning guidance for emotion-centric video foundation modeling. ICLR 2026 AVERE, MME-Emotion, EmotionHallucer, and HitEmotion target audiovisual cue grounding, emotion hallucination, emotional-intelligence evaluation, and Theory-of-Mind-guided multimodal emotion reasoning. The practical lesson for NetFeeliX is that emotion models should explain or ground affective judgments in temporal context, not only predict labels.

### Brain-Tuning and Brain-Aligned AI

Brain-Score Vision, Brain-Score Language, EEG representational alignment, brain-tuning speech/language models, multi-participant brain-tuning, and fMRI language-encoding scaling laws show that neural data can be used not only to evaluate AI models but also to tune or regularize them. For NetFeeliX, this supports a cautious but concrete extension:

```text
affective LLM/VLM representation + fMRI response during emotional stimuli
    -> brain-aligned affective adapter or distilled affective embedding
```

Because fMRI data are small, this should use adapters, contrastive alignment, or distillation rather than full LLM/VLM fine-tuning.

SED-GPT is a useful nearby precedent because it combines fMRI, long-sequence semantic decoding, and emotion distributions with LLM-style priors. It should be cited as pilot-level evidence that semantic/emotional fMRI decoding is possible, not as evidence that an fMRI emotion foundation model already exists.

### Gap Statement

There is no mature fMRI emotion foundation model direction yet. Existing fMRI BFMs are usually generic; neural-signal FMs may include emotion as one downstream benchmark; affective computing FMs usually lack brain grounding; stimulus-to-brain models usually optimize fMRI encoding rather than emotion representation. NetFeeliX fills this gap by making **pilot-driven model development for emotion-aware brain/stimulus representation** the central objective.

## Pilot-First Strategy

The first phase should avoid expensive end-to-end architecture claims. It should build a comparable benchmark surface across datasets, models, and targets.

Pilot questions:

1. Which datasets and targets are usable after access, preprocessing, and temporal alignment checks?
2. What do non-deep brain baselines achieve?
3. Do frozen BFM representations predict arousal, valence, discrete categories, or high-dimensional emotion vectors?
4. Are stimulus-only features stronger than brain-only features for some targets?
5. Does brain-stimulus alignment improve high-dimensional or cross-dataset transfer?
6. Which direction justifies two-month model development?

Minimum pilot table:

| Dataset | Target | Brain-only baseline | Stimulus-only baseline | Existing BFM | Alignment model | Notes |
|---|---|---|---|---|---|---|
| Horikawa | high-dimensional emotion vector | planned | planned | planned | planned | core downstream |
| Emo-FilM | emotion/appraisal/component ratings | planned | planned | planned | planned | modern naturalistic benchmark |
| Affective Videos | valence/arousal | planned | optional | planned | optional | lightweight sanity check |
| REELMO | time-resolved affect reports | optional | planned | optional fMRI subset | optional | strong stimulus-side supervision |
| HCP 7T movie | pretraining objective | planned | planned features | planned | planned | naturalistic pretraining source |

## Horikawa vs. Reasoning/Context Understanding

Horikawa should not be forced to carry the whole reasoning/context story. Its strength is different: it provides a high-dimensional, visually evoked emotion space with fMRI responses to many short videos. In NetFeeliX, Horikawa is best used as a **brain-side affect geometry probe**.

Reasoning and context understanding require longer temporal context, cue grounding, narrative structure, and sometimes natural-language rationales. These should come from other sources:

- **Emo-FilM**: component/appraisal-style annotations and naturalistic film context.
- **REELMO**: long movie trajectories, 20 emotion labels, stimulus features, subtitles, and fMRI subset.
- **HCP/CNeuroMod/Spacetop movie data**: naturalistic fMRI pretraining and context-window experiments.
- **Affective MLLM benchmarks/models**: descriptive emotion captions, cue-emotion QA, rationale embeddings, and hallucination diagnostics.

The bridge is therefore staged:

1. Use Horikawa to test whether brain encoders learn high-dimensional affective geometry.
2. Use Emo-FilM/REELMO to test whether temporal context and appraisal/component targets improve representation.
3. Use MLLM-derived rationale or cue embeddings as stimulus-side auxiliary targets.
4. Align fMRI latents with emotion label embeddings first, then with context/rationale embeddings.
5. Evaluate context by comparing short-window, long-window, and ablated-stimulus models.

This keeps the project coherent: Horikawa answers "does the brain representation capture rich emotion geometry?", while the reasoning/context track asks "can naturalistic stimulus-brain alignment explain why an affective state emerges over time?"

## Model Development Tracks

### Track A: Existing BFM Transfer

Goal: test whether pretrained brain models already contain emotion-relevant structure.

Order:

1. Frozen encoder + ridge/linear/MLP head.
2. Adapter or LoRA-style tuning where supported.
3. Partial or full fine-tuning only after stable probes.

Primary models: SwiFT, BrainLM, Brain-JEPA, SwiFUN, NeuroSTORM if code/weights are accessible.

Decision rule: if frozen/adapted BFM representations outperform simple baselines on more than arousal, prioritize adapter and fine-tuning experiments.

### Track B: HCP Movie Pretraining

Goal: test whether naturalistic stimulus-driven fMRI pretraining improves emotion transfer.

Start with parcel-level time series. Add raw 4D volumes only after simple pipelines work.

Candidate objectives:

- masked fMRI segment modeling,
- temporal contrastive learning,
- JEPA-style latent prediction,
- subject-invariant contrastive learning,
- future brain-state prediction.

Decision rule: if HCP-pretrained encoders beat generic BFM transfer on Horikawa/Emo-FilM, scale movie pretraining.

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
| Naturalistic pretraining | HCP 7T movie, CNeuroMod/Algonauts if accessible | learn stimulus-driven fMRI dynamics |
| Core emotion downstream | Horikawa, Emo-FilM | evaluate high-dimensional and naturalistic emotion transfer |
| Lightweight emotion downstream | Affective Videos, NeuroEmo, Koide-Majima if accessible | pilot valence/arousal/category generalization |
| Stimulus-side affective supervision | REELMO, MMAFFBen/MMAFFIn, affective LLM/VLMs | build or validate stimulus emotion trajectories |
| Auxiliary encoding | BOLD Moments, CNeuroMod, Algonauts 2025, Spacetop as future expansion | test video/audio/text-to-fMRI alignment and physiology-rich transfer |

HCP movie pretraining and Horikawa/Emo-FilM downstream evaluation remain the central story. Other datasets should be added only when they reduce uncertainty in the pilot matrix.

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

- A structured benchmark comparing generic BFM transfer, movie-fMRI pretraining, and stimulus-brain alignment for emotion prediction.
- A practical two-month roadmap that can produce useful results even if the ambitious model is not yet ready.
- A taxonomy separating fMRI encoders, stimulus-to-brain encoding models, and emotion-aware aligned representation models.
- A model-development bridge between affective computing foundation models and affective neuroscience.
- A clear decision framework for when to pursue adapters, HCP pretraining, TRIBE-style alignment, or brain-tuned affective VLM/LLM.

## Key References

| Area | References | Role |
|---|---|---|
| fMRI BFMs | SwiFT, SwiFUN, BrainLM, Brain-JEPA, NeuroSTORM, Omni-fMRI, Brain-OF | brain-side baselines and pretraining precedents |
| Stimulus-to-brain | TRIBE, TRIBE v2, VIBE, Algonauts 2025, Hu and Mohsenzadeh | multimodal alignment and fMRI response prediction |
| Naturalistic fMRI | HCP 7T movie, CNeuroMod, BOLD Moments, van der Meer, Petrican | movie pretraining and naturalistic dynamics |
| Emotion fMRI | Horikawa, Koide-Majima, Emo-FilM, Ke et al., Affective Videos, NeuroEmo, REELMO | downstream targets and target difficulty |
| Affective FM | Schuller et al., LLM affect survey, MLLM emotion reasoning survey, MMAFFBen, MME-Emotion, EmoBench-M, EIBench | external affective AI and emotion-reasoning trend |
| Top-conference affective reasoning | ICML 2025 AffectGPT; NeurIPS 2025 VidEmo; ICLR 2026 AVERE, EmotionHallucer, HitEmotion/MME-Emotion | label prediction is shifting toward cue grounding, rationale, context, and hallucination control |
| Brain tuning | Brain-Score Vision/Language, EEG representational alignment, brain-tuning speech LMs, scaling laws, SED-GPT | brain-aligned AI and fMRI semantic/emotion decoding precedent |
