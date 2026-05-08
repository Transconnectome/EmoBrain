# NetFeeliX Paper Reference Index

This file records the currently relevant papers and how each should be used in the project.

## Core fMRI Foundation Models

### SwiFT: Swin 4D fMRI Transformer

- **Type**: 4D fMRI encoder.
- **Claim**: Efficient end-to-end spatiotemporal fMRI learning with 4D shifted-window attention and contrastive self-supervised pretraining.
- **NetFeeliX role**: direct fMRI backbone baseline.
- **Source**: https://huggingface.co/papers/2307.05916

### SwiFUN: Predicting task-related brain activity from resting-state dynamics

- **Type**: resting-state fMRI to task activation map prediction.
- **Claim**: Swin fMRI UNet Transformer predicts 3D task activation maps from resting-state fMRI, including emotion-related contrasts in UK Biobank and ABCD.
- **NetFeeliX role**: bridge baseline for resting-state to emotion-related task reactivity.
- **Source**: https://direct.mit.edu/imag/article/doi/10.1162/imag_a_00440/126557/Predicting-task-related-brain-activity-from
- **Code**: https://github.com/Transconnectome/SwiFUN

### BrainLM: A foundation model for brain activity recordings

- **Type**: fMRI foundation model, ROI/time-series masked prediction.
- **Claim**: Trained on 6,700 hours of fMRI with self-supervised masked prediction, supports fine-tuning and zero-shot analyses.
- **NetFeeliX role**: pretrained BFM transfer baseline.
- **Source**: https://sciety.org/articles/activity/10.1101/2023.09.12.557460

### Brain-JEPA

- **Type**: fMRI foundation model using joint-embedding predictive architecture.
- **Claim**: Uses Brain Gradient Positioning and spatiotemporal masking for brain dynamics representation learning.
- **NetFeeliX role**: strong methodological precedent for JEPA-style HCP movie pretraining.
- **Source**: https://neurips.cc/virtual/2024/poster/94113
- **HF paper page**: https://huggingface.co/papers/2409.19407

### NeuroSTORM

- **Type**: large-scale 4D fMRI foundation model.
- **Claim**: Learns directly from 4D fMRI volumes at scale, with 28.65 million fMRI frames from over 50,000 participants.
- **NetFeeliX role**: state-of-the-art BFM baseline if code/weights are available.
- **Source**: https://www.nature.com/articles/s41551-026-01666-y

### Omni-fMRI

- **Type**: atlas-free voxel-level fMRI foundation model.
- **Claim**: Avoids parcellation bias through dynamic patching and voxel-level pretraining across 49,497 sessions.
- **NetFeeliX role**: useful reference for atlas-free direction, likely not first two-month implementation unless code is easy.
- **Source**: https://www.researchgate.net/publication/400339978_Omni-fMRI_A_Universal_Atlas-Free_fMRI_Foundation_Model

### Brain-DiT

- **Type**: multi-state fMRI foundation model with diffusion transformer pretraining.
- **Claim**: Metadata-conditioned diffusion pretraining across resting, task, naturalistic, disease, and sleep states.
- **NetFeeliX role**: future-method reference, especially for multi-state pretraining.
- **Source**: https://papers.cool/arxiv/2604.12683

## Brain Encoding Models and Stimulus Alignment

### TRIBE: TRImodal Brain Encoder

- **Type**: stimulus-to-brain encoding model.
- **Claim**: Combines pretrained text, audio, and video models with temporal transformers to predict whole-brain fMRI responses to naturalistic video.
- **NetFeeliX role**: compare against BFM; inspiration for stimulus-brain alignment.
- **Important distinction**: TRIBE is not the same kind of model as SwiFT or BrainLM. It predicts fMRI from stimuli.
- **Source**: https://huggingface.co/papers/2507.22229
- **Code**: https://github.com/facebookresearch/algonauts-2025

### TRIBE v2

- **Type**: multimodal foundation model for in-silico neuroscience.
- **Claim**: Predicts high-resolution fMRI responses from video, audio, and language across naturalistic and experimental conditions.
- **NetFeeliX role**: newest stimulus-brain alignment reference.
- **Meta search listing**: https://ai.meta.com/global_search/
- **Code**: https://github.com/facebookresearch/tribev2

### V-JEPA 2

- **Type**: self-supervised video world model.
- **Claim**: Pretrained on large-scale video, strong motion understanding, action anticipation, and video reasoning.
- **NetFeeliX role**: video feature extractor for stimulus-brain-emotion alignment.
- **Source**: https://ai.meta.com/research/publications/v-jepa-2-self-supervised-video-models-enable-understanding-prediction-and-planning/

### VIBE: Video-Input Brain Encoder for fMRI Response Modeling

- **Type**: multimodal stimulus-to-brain encoding model.
- **Claim**: Uses video, audio, and text features with fusion and prediction transformers to predict fMRI activity from movie data.
- **NetFeeliX role**: practical architecture reference for stimulus feature fusion and temporal prediction in movie fMRI.
- **Source**: https://huggingface.co/papers/2507.17958

### Comprehensive Neural Representations of Naturalistic Stimuli through Multimodal Deep Learning

- **Type**: multimodal naturalistic fMRI encoding model.
- **Claim**: Video-text aligned deep learning features improve whole-brain encoding of naturalistic stimuli relative to unimodal or static baselines.
- **NetFeeliX role**: supports the claim that dynamic multimodal integration should help stimulus-brain-emotion alignment.
- **Source**: https://sciety.org/articles/activity/10.1101/2025.04.15.646250

## Emotion and Naturalistic fMRI

### Horikawa et al. 2020: High-dimensional visually evoked emotion

- **Type**: emotional video fMRI and high-dimensional category representation.
- **Claim**: Dozens of video-evoked emotions are predictable from fMRI; categorical emotion structure outperforms lower-dimensional affective dimensions in parts of the brain.
- **NetFeeliX role**: core downstream benchmark.
- **Source**: https://www.sciencedirect.com/science/article/pii/S2589004220302455
- **Dataset link noted in search**: https://openneuro.org/datasets/ds002425
- **Mendeley data mirror**: https://data.mendeley.com/datasets/jbk2r73mzh

### Koide-Majima, Nakai, Nishimoto 2020

- **Type**: emotion-inducing audiovisual movie fMRI.
- **Claim**: About 25 distinct emotion dimensions contribute to cortical emotion representation from 80 emotion ratings over 3 hours of movies.
- **NetFeeliX role**: high-dimensional emotion benchmark if data access is feasible.
- **Source**: https://pubmed.ncbi.nlm.nih.gov/32798681/

### Emo-FilM 2025

- **Type**: multimodal affective neuroscience dataset.
- **Claim**: 30 participants, 14 short films, over 2.5 hours, fMRI, physiology, and 50 affective annotations.
- **NetFeeliX role**: modern downstream dataset for naturalistic emotion prediction.
- **Source**: https://www.nature.com/articles/s41597-025-04803-5

### Ke et al. 2025: Dynamic connectivity predicts emotional arousal

- **Type**: movie-watching fMRI dynamic FC prediction.
- **Claim**: Arousal generalizes across movie datasets more robustly than valence.
- **NetFeeliX role**: baseline method and hypothesis support that arousal may be easier than valence.
- **Source**: https://pubmed.ncbi.nlm.nih.gov/40215238/
- **Code/data noted in paper**: https://github.com/jinke828/AffectPrediction

### Naturalistic stimuli in affective neuroimaging review

- **Type**: review.
- **Claim**: Naturalistic affective stimuli mix perceptual, physiological, semantic, and experiential components.
- **NetFeeliX role**: theoretical justification for not treating emotion as a simple label.
- **Source**: https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.675068/full

### Morgenroth et al. 2023: Hitchhiker's guide to film fMRI

- **Type**: review/practitioner's guide.
- **Claim**: Film fMRI can bridge the mismatch between emotion theory and traditional fMRI paradigms, and needs systematic theory-grounded analysis.
- **NetFeeliX role**: methodological justification for using film fMRI as the central affective neuroscience paradigm.
- **Source**: https://pmc.ncbi.nlm.nih.gov/articles/PMC10656947/

### Barrett 2017: Theory of constructed emotion

- **Type**: theoretical/computational account of emotion.
- **Claim**: Emotion is constructed through prediction, interoception, categorization, and situated conceptualization rather than fixed neural fingerprints.
- **NetFeeliX role**: theoretical basis for treating emotion as dynamic, context-dependent representation rather than a static category label.
- **Source**: https://pmc.ncbi.nlm.nih.gov/articles/PMC5390700/

## Naturalistic Movie fMRI and Brain Dynamics

### van der Meer et al. 2020: Movie viewing elicits rich and reliable brain state dynamics

- **Type**: naturalistic movie fMRI brain-state dynamics.
- **Claim**: Movie viewing reshapes resting-state-like dynamics into richer, more reliable brain-state transitions that align with movie events, physiology, and subjective engagement.
- **NetFeeliX role**: key justification for movie-fMRI pretraining instead of resting-state-only pretraining.
- **Source**: https://www.nature.com/articles/s41467-020-18717-w

### Petrican, Graham, Lawrence 2021: Brain-environment alignment during movie watching

- **Type**: dynamic FC and brain-environment alignment during movie watching.
- **Claim**: Uses Cam-CAN and HCP movie-watching data to link FC variability and brain-environment alignment with fluid intelligence and affective functioning.
- **NetFeeliX role**: supports the claim that movie-driven brain dynamics carry behaviorally and affectively meaningful signal.
- **Source**: https://www.sciencedirect.com/science/article/pii/S1053811921004547

### Gruskin and Patel 2022: Resting connectivity predicts movie activity

- **Type**: rest-to-movie individual-difference mapping.
- **Claim**: HCP resting-state connectivity predicts individual differences in normative movie-watching activity.
- **NetFeeliX role**: bridge reference for testing how much resting-state representations can predict naturalistic responses.
- **Source**: https://pmc.ncbi.nlm.nih.gov/articles/PMC9491116/

### View, engage, predict 2025

- **Type**: preprint on movie-watching FC for brain-behavior mapping.
- **Claim**: Movie-watching FC can outperform resting-state FC for predicting cognitive scores and sex, with effects related to inter-subject synchrony and movie content.
- **NetFeeliX role**: supports the practical value of movie fMRI for representation learning.
- **Source**: https://sciety.org/articles/activity/10.1101/2025.07.28.666907

## Naturalistic Multisensory Neuroscience

### Hu and Mohsenzadeh 2025: Neural processing of naturalistic audiovisual events

- **Type**: fMRI and EEG study of naturalistic audiovisual processing.
- **Claim**: Acoustic, visual, categorical, and semantic information emerge with distinct spatial and temporal profiles; high-level semantic information appears in multisensory association areas.
- **NetFeeliX role**: supports explicit video/audio/semantic temporal modeling instead of unimodal fMRI-only targets.
- **Source**: https://www.nature.com/articles/s42003-024-07434-5

### BOLD Moments Dataset paper

- **Type**: dynamic visual-event fMRI dataset and modeling benchmark.
- **Claim**: Provides fMRI responses to 1,102 short naturalistic video clips across ten subjects with rich metadata including object, scene, action, sentence, and memorability labels.
- **NetFeeliX role**: auxiliary dataset for short-video stimulus-brain modeling and possible non-emotion pretraining.
- **Source**: https://www.nature.com/articles/s41467-024-50310-3

### Spacetop

- **Type**: multimodal fMRI dataset with naturalistic and task data.
- **Claim**: Provides 101 participants with about 6 hours of scanning per participant, including naturalistic movie viewing, multiple tasks, structural/diffusion imaging, and autonomic physiology.
- **NetFeeliX role**: future expansion dataset for naturalistic/physiology-rich pretraining or transfer, not a first two-month priority unless access is easy.
- **Source**: https://www.nature.com/articles/s41597-025-05154-x

## Affective Computing Foundation-Model Literature

### AffectGPT

- **Venue**: ICML 2025 oral.
- **Type**: dataset, model, and benchmark for MLLM-based emotion understanding.
- **Claim**: Moves multimodal emotion recognition from discriminative labels toward descriptive emotion understanding with fine-grained emotion captions, over 2,000 emotion categories, 115K samples, and MER-UniBench.
- **NetFeeliX role**: top-conference evidence that stimulus-side affective modeling is moving toward caption/rationale/context-rich supervision.
- **Source**: https://icml.cc/virtual/2025/oral/47171
- **Code/data**: https://github.com/zeroQiaoba/AffectGPT

### VidEmo

- **Venue**: NeurIPS 2025.
- **Type**: emotion-centric video foundation model.
- **Claim**: Uses affective-tree reasoning guidance with fine-grained captions and rationales to model open-set, dynamic, and context-dependent emotions in video.
- **NetFeeliX role**: top-conference precedent for treating video emotion as context/rationale-based representation learning, not only classification.
- **Source**: https://openreview.net/forum?id=x8lg9aihwl

### AVERE / EmoReAlM

- **Venue**: ICLR 2026.
- **Type**: audiovisual emotion reasoning benchmark and preference-optimization method.
- **Claim**: Introduces EmoReAlM for cue-emotion associations, hallucinations, and modality agreement; uses AVEm-DPO to reduce spurious associations and text-prior hallucinations.
- **NetFeeliX role**: direct methodological template for cue grounding, hallucination control, and preference-style alignment in brain-tuned affective VLM/LLM track.
- **Source**: https://openreview.net/forum?id=td682AAuPr
- **Project**: https://avere-iclr.github.io/

### EmotionHallucer

- **Venue**: ICLR 2026.
- **Type**: benchmark for emotion hallucinations in MLLMs.
- **Claim**: Evaluates emotion-specific hallucinations in multimodal large language models.
- **NetFeeliX role**: diagnostic reference for checking whether stimulus-side affective models invent emotional cues unsupported by audiovisual evidence.
- **Source**: https://openreview.net/forum?id=ahWmeQG3K2

### HitEmotion / ToM-Guided Multimodal Emotion Reasoning

- **Venue**: ICLR 2026.
- **Type**: Theory-of-Mind-grounded benchmark and reinforcement-learning approach for multimodal emotion reasoning.
- **Claim**: Diagnoses emotional reasoning by increasing cognitive depth and uses intermediate mental-state supervision to improve reasoning.
- **NetFeeliX role**: supports using context/rationale embeddings as auxiliary targets, while keeping brain claims grounded in fMRI alignment rather than pure ToM theory.
- **Source**: https://openreview.net/forum?id=8VSrk2CaBr

### Schuller et al. 2026: Affective computing has changed

- **Type**: perspective/review on foundation models in affective computing.
- **Claim**: Foundation models are disrupting affective computing across vision, language, and speech, while raising evaluation concerns for affective validity.
- **NetFeeliX role**: establishes that "foundation models for affect" is an active AI direction, but also highlights that neuroscience-grounded affective FMs remain underdeveloped.
- **Source**: https://www.nature.com/articles/s44387-025-00061-3

### Affective Computing in the Era of Large Language Models

- **Type**: NLP-centric survey.
- **Claim**: LLMs reshape affective understanding and affective generation through prompting, instruction tuning, RL-style alignment, and broader world knowledge.
- **NetFeeliX role**: reference for external affective language models that may support stimulus annotation or text-side affect embeddings.
- **Source**: https://huggingface.co/papers/2408.04638

### Multimodal Large Language Models Meet Multimodal Emotion Recognition and Reasoning

- **Type**: survey.
- **Claim**: Reviews MLLM-based emotion recognition and reasoning across architectures, datasets, and benchmarks.
- **NetFeeliX role**: reference for stimulus-side multimodal affective reasoning, not a replacement for brain modeling.
- **Source**: https://huggingface.co/papers/2509.24322

### MMAFFBen

- **Type**: multilingual multimodal affective benchmark.
- **Claim**: Evaluates LLMs/VLMs on sentiment and emotion tasks across text, image, and video in 35 languages; introduces affective fine-tuning data and MMAFFLM models.
- **NetFeeliX role**: benchmark-design inspiration for affective evaluation, especially target diversity and intensity prediction.
- **Source**: https://huggingface.co/papers/2505.24423
- **Code/project**: https://github.com/lzw108/MMAFFBen

### MME-Emotion

- **Type**: MLLM emotional-intelligence benchmark.
- **Claim**: Evaluates multimodal emotional understanding and reasoning across diverse video scenarios with task-specific QA.
- **NetFeeliX role**: reference for moving stimulus-side affective supervision beyond label prediction toward reasoning about triggers/context.
- **Source**: https://mme-emotion.github.io/

### EmoBench-M

- **Type**: benchmark for emotional intelligence in MLLMs.
- **Claim**: Evaluates foundational emotion recognition, conversational emotion understanding, and socially complex emotion analysis.
- **NetFeeliX role**: stimulus-side affective evaluation reference; useful for defining richer external affective embeddings.
- **Source**: https://huggingface.co/papers/2502.04424

### Beyond Emotion Recognition

- **Type**: multi-turn multimodal emotion understanding and reasoning benchmark.
- **Claim**: Targets emotion reasoning rather than only emotion classification.
- **NetFeeliX role**: supports the brain-tuned affective LLM/VLM track as a reasoning/representation problem, not just label matching.
- **Source**: https://huggingface.co/papers/2508.16859

### Why We Feel / EIBench

- **Type**: emotion interpretation benchmark for MLLMs.
- **Claim**: Emphasizes causal factors and rationale-based emotional reasoning rather than only "which emotion" labels.
- **NetFeeliX role**: potential source of stimulus-side causal/contextual affective targets, kept separate from brain-grounded evaluation.
- **Source**: https://cvpr.thecvf.com/virtual/2025/35814

### 2026 Multimodal Emotion Recognition Survey

- **Type**: survey and taxonomy.
- **Claim**: Reviews MER advances from 2020-2025, emphasizing transformer models, fusion strategies, missing data, imbalance, and user generalization.
- **NetFeeliX role**: practical reference for stimulus-only baselines, missing-modality handling, and temporal fusion.
- **Source**: https://www.sciencedirect.com/science/article/pii/S2667305326000177

## Neural-Signal Foundation Models with Emotion Downstream

### REVE

- **Type**: EEG foundation model.
- **Claim**: Pretrained on over 60,000 hours of EEG from 92 datasets and 25,000 subjects; achieves strong transfer across tasks including emotion recognition.
- **NetFeeliX role**: methodological reference for heterogeneous neural-signal pretraining and emotion downstream transfer.
- **Source**: https://brain-bzh.github.io/reve/

### Brain-OF

- **Type**: fMRI/EEG/MEG omnifunctional foundation model.
- **Claim**: Jointly pretrains across functional neuroimaging modalities using any-resolution sampling, sparse MoE, and masked temporal-frequency modeling; evaluates affective computing among downstream tasks.
- **NetFeeliX role**: broad neural-signal FM precedent, especially for multimodal neural data and time-frequency objectives.
- **Source**: https://www.researchgate.net/publication/401418431_Brain-OF_An_Omnifunctional_Foundation_Model_for_fMRI_EEG_and_MEG

### REVE and LaBraM-style EEG FM line

- **Type**: EEG foundation-model family.
- **Claim**: Large-scale EEG pretraining can generalize to emotion recognition, stress detection, BCI, sleep, seizure, and other downstream tasks.
- **NetFeeliX role**: useful for architecture and pretraining-objective ideas if physiology or EEG is added later.
- **Source**: https://www.emergentmind.com/topics/eeg-foundation-models-eeg-fms

## Brain-Tuning and Brain-Aligned AI

### Brain-Score Vision

- **Type**: benchmark platform for model-brain-behavior alignment in vision.
- **Claim**: Artificial neural networks can be quantitatively evaluated by how well they match primate neural and behavioral measurements.
- **NetFeeliX role**: conceptual template for an affective brain-score style evaluation of VLM/LLM emotion models.
- **Source**: https://github.com/brain-score/vision

### Brain-Score Language

- **Type**: benchmark platform for language model alignment with neural and behavioral measurements.
- **Claim**: Operationalizes language model comparison against brain and behavioral data using a standard interface.
- **NetFeeliX role**: template for evaluating affective language models against naturalistic emotion fMRI.
- **Source**: https://github.com/brain-score/language

### Lu, Wang, Golomb 2026: Human EEG representational alignment

- **Type**: brain-aligned computer vision model.
- **Claim**: EEG-based representational alignment can make visual models more brain-like, improving alignment with EEG, fMRI, and behavior.
- **NetFeeliX role**: direct precedent for brain-tuning external VLM representations with human neural data.
- **Source**: https://www.nature.com/articles/s42003-026-09685-w

### Moussa, Klakow, Toneva 2024: Brain-tuning speech language models

- **Type**: fMRI-tuned speech/language model.
- **Claim**: Fine-tuning speech language models with fMRI responses to natural stories improves brain alignment and semantic understanding.
- **NetFeeliX role**: direct methodological precedent for brain-tuned affective LLM/VLM adapters.
- **Source**: https://huggingface.co/papers/2410.09230

### Moussa and Toneva 2025: Multi-participant brain-tuning

- **Type**: scalable brain-tuning for speech models.
- **Claim**: Jointly predicting fMRI from multiple participants improves generalization, data efficiency, and downstream semantic performance.
- **NetFeeliX role**: supports multi-subject brain-tuning rather than subject-specific overfitting.
- **Source**: https://papers.cool/arxiv/2510.21520

### Antonello, Vaidya, Huth 2023: Scaling laws for language encoding models in fMRI

- **Type**: language-model-to-fMRI encoding study.
- **Claim**: Larger language models show log-linear improvements in predicting fMRI responses to natural language, with similar scaling for fMRI training data.
- **NetFeeliX role**: supports using modern LLM representations and considering model/data scaling in brain alignment.
- **Source**: https://pmc.ncbi.nlm.nih.gov/articles/PMC11258918/

### Narratives fMRI dataset

- **Type**: naturalistic spoken story fMRI benchmark.
- **Claim**: Provides 345 subjects, 891 functional scans, and 27 stories as a benchmark for naturalistic language comprehension models.
- **NetFeeliX role**: analogy for how naturalistic neuroimaging datasets can become model-evaluation infrastructure.
- **Source**: https://www.nature.com/articles/s41597-021-01033-3

### SED-GPT

- **Type**: long-sequence semantic and emotion decoding from fMRI.
- **Claim**: Uses a GPT-style semantic decoding framework and GoEmotions-derived emotional distributions to decode fine-grained semantics and emotions from fMRI in an exploratory study.
- **NetFeeliX role**: direct cautionary precedent for brain-to-emotion decoding with LLM priors; useful for the brain-tuned affective LLM/VLM track, but not evidence that an fMRI emotion foundation model already exists.
- **Source**: https://www.mdpi.com/2076-3417/15/20/11100

## Dataset/Challenge References

### Algonauts Project 2025

- **Type**: multimodal movie-fMRI encoding challenge.
- **Claim**: Uses CNeuroMod movie data with visual frames, audio samples, transcripts, and 1,000-parcel fMRI responses from four subjects.
- **NetFeeliX role**: benchmark and data/model reference for TRIBE-style multimodal fMRI response prediction.
- **Source**: https://algonautsproject.com/2025/braindata.html

### CNeuroMod

- **Type**: dense single-subject naturalistic fMRI resource.
- **Claim**: Provides roughly ten hours per subject for multiple movie datasets including Friends seasons and movie10.
- **NetFeeliX role**: high-value expansion dataset if access and preprocessing are feasible.
- **Source**: https://www.cneuromod.ca/gallery/datasets/
