# FEEL Paper Reference Index

This file records the currently relevant papers and how each should be used in the project.

## Core fMRI Foundation Models

### SwiFT: Swin 4D fMRI Transformer

- **Type**: 4D fMRI encoder.
- **Claim**: Efficient end-to-end spatiotemporal fMRI learning with 4D shifted-window attention and contrastive self-supervised pretraining.
- **FEEL role**: direct fMRI backbone baseline.
- **Source**: https://huggingface.co/papers/2307.05916

### SwiFUN: Predicting task-related brain activity from resting-state dynamics

- **Type**: resting-state fMRI to task activation map prediction.
- **Claim**: Swin fMRI UNet Transformer predicts 3D task activation maps from resting-state fMRI, including emotion-related contrasts in UK Biobank and ABCD.
- **FEEL role**: bridge baseline for resting-state to emotion-related task reactivity.
- **Source**: https://direct.mit.edu/imag/article/doi/10.1162/imag_a_00440/126557/Predicting-task-related-brain-activity-from
- **Code**: https://github.com/Transconnectome/SwiFUN

### BrainLM: A foundation model for brain activity recordings

- **Type**: fMRI foundation model, ROI/time-series masked prediction.
- **Claim**: Trained on 6,700 hours of fMRI with self-supervised masked prediction, supports fine-tuning and zero-shot analyses.
- **FEEL role**: pretrained BFM transfer baseline.
- **Source**: https://sciety.org/articles/activity/10.1101/2023.09.12.557460

### Brain-JEPA

- **Type**: fMRI foundation model using joint-embedding predictive architecture.
- **Claim**: Uses Brain Gradient Positioning and spatiotemporal masking for brain dynamics representation learning.
- **FEEL role**: strong methodological precedent for JEPA-style naturalistic fMRI pretraining.
- **Source**: https://neurips.cc/virtual/2024/poster/94113
- **HF paper page**: https://huggingface.co/papers/2409.19407

### NeuroSTORM

- **Type**: large-scale 4D fMRI foundation model.
- **Claim**: Learns directly from 4D fMRI volumes at scale, with 28.65 million fMRI frames from over 50,000 participants.
- **FEEL role**: state-of-the-art BFM baseline if code/weights are available.
- **Source**: https://www.nature.com/articles/s41551-026-01666-y

### Omni-fMRI

- **Type**: atlas-free voxel-level fMRI foundation model.
- **Claim**: Avoids parcellation bias through dynamic patching and voxel-level pretraining across 49,497 sessions.
- **FEEL role**: useful reference for atlas-free direction, likely not first two-month implementation unless code is easy.
- **Source**: https://www.researchgate.net/publication/400339978_Omni-fMRI_A_Universal_Atlas-Free_fMRI_Foundation_Model

### Brain-DiT

- **Type**: multi-state fMRI foundation model with diffusion transformer pretraining.
- **Claim**: Metadata-conditioned diffusion pretraining across resting, task, naturalistic, disease, and sleep states.
- **FEEL role**: future-method reference, especially for multi-state pretraining.
- **Source**: https://papers.cool/arxiv/2604.12683

## Brain Encoding Models and Stimulus Alignment

### TRIBE: TRImodal Brain Encoder

- **Type**: stimulus-to-brain encoding model.
- **Claim**: Combines pretrained text, audio, and video models with temporal transformers to predict whole-brain fMRI responses to naturalistic video.
- **FEEL role**: compare against BFM; inspiration for stimulus-brain alignment.
- **Important distinction**: TRIBE is not the same kind of model as SwiFT or BrainLM. It predicts fMRI from stimuli.
- **Source**: https://huggingface.co/papers/2507.22229
- **Code**: https://github.com/facebookresearch/algonauts-2025

### TRIBE v2

- **Type**: multimodal foundation model for in-silico neuroscience.
- **Claim**: Predicts high-resolution fMRI responses from video, audio, and language across naturalistic and experimental conditions.
- **FEEL role**: newest stimulus-brain alignment reference.
- **Meta search listing**: https://ai.meta.com/global_search/
- **Code**: https://github.com/facebookresearch/tribev2

### V-JEPA 2

- **Type**: self-supervised video world model.
- **Claim**: Pretrained on large-scale video, strong motion understanding, action anticipation, and video reasoning.
- **FEEL role**: video feature extractor for stimulus-brain-emotion alignment.
- **Source**: https://ai.meta.com/research/publications/v-jepa-2-self-supervised-video-models-enable-understanding-prediction-and-planning/

### VIBE: Video-Input Brain Encoder for fMRI Response Modeling

- **Type**: multimodal stimulus-to-brain encoding model.
- **Claim**: Uses video, audio, and text features with fusion and prediction transformers to predict fMRI activity from movie data.
- **FEEL role**: practical architecture reference for stimulus feature fusion and temporal prediction in movie fMRI.
- **Source**: https://huggingface.co/papers/2507.17958

### Comprehensive Neural Representations of Naturalistic Stimuli through Multimodal Deep Learning

- **Type**: multimodal naturalistic fMRI encoding model.
- **Claim**: Video-text aligned deep learning features improve whole-brain encoding of naturalistic stimuli relative to unimodal or static baselines.
- **FEEL role**: supports the claim that dynamic multimodal integration should help stimulus-brain-emotion alignment.
- **Source**: https://sciety.org/articles/activity/10.1101/2025.04.15.646250

## Emotion and Naturalistic fMRI

### Horikawa et al. 2020: High-dimensional visually evoked emotion

- **Type**: emotional video fMRI and high-dimensional category representation.
- **Claim**: Dozens of video-evoked emotions are predictable from fMRI; categorical emotion structure outperforms lower-dimensional affective dimensions in parts of the brain.
- **FEEL role**: core downstream benchmark.
- **Source**: https://www.sciencedirect.com/science/article/pii/S2589004220302455
- **Dataset link noted in search**: https://openneuro.org/datasets/ds002425
- **Mendeley data mirror**: https://data.mendeley.com/datasets/jbk2r73mzh

### Koide-Majima, Nakai, Nishimoto 2020

- **Type**: emotion-inducing audiovisual movie fMRI.
- **Claim**: About 25 distinct emotion dimensions contribute to cortical emotion representation from 80 emotion ratings over 3 hours of movies.
- **FEEL role**: high-dimensional emotion benchmark if data access is feasible.
- **Source**: https://pubmed.ncbi.nlm.nih.gov/32798681/

### Emo-FilM 2025

- **Type**: multimodal affective neuroscience dataset.
- **Claim**: 30 participants, 14 short films, over 2.5 hours, fMRI, physiology, and 50 affective annotations.
- **FEEL role**: modern downstream dataset for naturalistic emotion prediction.
- **Source**: https://www.nature.com/articles/s41597-025-04803-5

### Ke et al. 2025: Dynamic connectivity predicts emotional arousal

- **Type**: movie-watching fMRI dynamic FC prediction.
- **Claim**: Arousal generalizes across movie datasets more robustly than valence.
- **FEEL role**: baseline method and hypothesis support that arousal may be easier than valence.
- **Source**: https://pubmed.ncbi.nlm.nih.gov/40215238/
- **Code/data noted in paper**: https://github.com/jinke828/AffectPrediction

### Naturalistic stimuli in affective neuroimaging review

- **Type**: review.
- **Claim**: Naturalistic affective stimuli mix perceptual, physiological, semantic, and experiential components.
- **FEEL role**: theoretical justification for not treating emotion as a simple label.
- **Source**: https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.675068/full

### Morgenroth et al. 2023: Hitchhiker's guide to film fMRI

- **Type**: review/practitioner's guide.
- **Claim**: Film fMRI can bridge the mismatch between emotion theory and traditional fMRI paradigms, and needs systematic theory-grounded analysis.
- **FEEL role**: methodological justification for using film fMRI as the central affective neuroscience paradigm.
- **Source**: https://pmc.ncbi.nlm.nih.gov/articles/PMC10656947/

### Barrett 2017: Theory of constructed emotion

- **Type**: theoretical/computational account of emotion.
- **Claim**: Emotion is constructed through prediction, interoception, categorization, and situated conceptualization rather than fixed neural fingerprints.
- **FEEL role**: theoretical basis for treating emotion as dynamic, context-dependent representation rather than a static category label.
- **Source**: https://pmc.ncbi.nlm.nih.gov/articles/PMC5390700/

## Naturalistic Movie fMRI and Brain Dynamics

### van der Meer et al. 2020: Movie viewing elicits rich and reliable brain state dynamics

- **Type**: naturalistic movie fMRI brain-state dynamics.
- **Claim**: Movie viewing reshapes resting-state-like dynamics into richer, more reliable brain-state transitions that align with movie events, physiology, and subjective engagement.
- **FEEL role**: supports testing stimulus-locked movie fMRI pretraining against resting-state-only transfer, while still requiring emotion downstream validation.
- **Source**: https://www.nature.com/articles/s41467-020-18717-w

### Petrican, Graham, Lawrence 2021: Brain-environment alignment during movie watching

- **Type**: dynamic FC and brain-environment alignment during movie watching.
- **Claim**: Uses Cam-CAN and HCP movie-watching data to link FC variability and brain-environment alignment with fluid intelligence and affective functioning.
- **FEEL role**: supports the claim that movie-driven brain dynamics carry behaviorally and affectively meaningful signal.
- **Source**: https://www.sciencedirect.com/science/article/pii/S1053811921004547

### Gruskin and Patel 2022: Resting connectivity predicts movie activity

- **Type**: rest-to-movie individual-difference mapping.
- **Claim**: HCP resting-state connectivity predicts individual differences in normative movie-watching activity.
- **FEEL role**: bridge reference for testing how much resting-state representations can predict naturalistic responses.
- **Source**: https://pmc.ncbi.nlm.nih.gov/articles/PMC9491116/

### View, engage, predict 2025

- **Type**: preprint on movie-watching FC for brain-behavior mapping.
- **Claim**: Movie-watching FC can outperform resting-state FC for predicting cognitive scores and sex, with effects related to inter-subject synchrony and movie content.
- **FEEL role**: supports the practical value of movie fMRI for representation learning.
- **Source**: https://sciety.org/articles/activity/10.1101/2025.07.28.666907

## Naturalistic Multisensory Neuroscience

### Hu and Mohsenzadeh 2025: Neural processing of naturalistic audiovisual events

- **Type**: fMRI and EEG study of naturalistic audiovisual processing.
- **Claim**: Acoustic, visual, categorical, and semantic information emerge with distinct spatial and temporal profiles; high-level semantic information appears in multisensory association areas.
- **FEEL role**: supports explicit video/audio/semantic temporal modeling instead of unimodal fMRI-only targets.
- **Source**: https://www.nature.com/articles/s42003-024-07434-5

### BOLD Moments Dataset paper

- **Type**: dynamic visual-event fMRI dataset and modeling benchmark.
- **Claim**: Provides fMRI responses to 1,102 short naturalistic video clips across ten subjects with rich metadata including object, scene, action, sentence, and memorability labels.
- **FEEL role**: auxiliary dataset for short-video stimulus-brain modeling and possible non-emotion pretraining.
- **Source**: https://www.nature.com/articles/s41467-024-50310-3

### Sartzetaki et al. 2025: One Hundred Neural Networks and Brains Watching Videos

- **Authors**: Christina Sartzetaki, Gemma Roig, Cees G.M. Snoek, Iris I.A. Groen.
- **Venue**: ICLR 2025.
- **Type**: large-scale benchmarking of 99 deep video and image models against human brain responses on the BOLD Moments dataset using Representational Similarity Analysis (RSA) across 17 brain regions.
- **Claim**: Disentangles four factors of variation (temporal modeling, classification task, architecture, training dataset). **Temporal modeling is the key driver of alignment with early visual regions (V1, V2, V3)**, while **action-recognition classification task drives alignment with late higher-level regions (LOC, FFA, OFA)**. CNN and Transformer architectures show distinct layer-depth alignment patterns (Transformers align early in the network, CNNs gradually). Reports a negative correlation between model FLOPs and alignment in higher-level regions.
- **FEEL role**: methodological prior for FEEL. Our Phase 1 frozen-probe finding that SwiFT does not use temporal information is consistent with Sartzetaki's observation that temporal modeling matters only when the video model is end-to-end trained on a task that requires it. Motivates Phase 2 trained-integration architectures over frozen-probe extraction. Also motivates layer-wise alignment scans and FLOPs scaling analyses across SwiFT variants (UAH 5M to 202M; NewE36 to NewE192) as direct emotion-domain replications of their visual-domain analyses.
- **Source**: https://openreview.net/forum?id=LM4PYXBId5 (paper PDF: https://openreview.net/pdf?id=LM4PYXBId5)

### Spacetop

- **Type**: multimodal fMRI dataset with naturalistic and task data.
- **Claim**: Provides 101 participants with about 6 hours of scanning per participant, including naturalistic movie viewing, multiple tasks, structural/diffusion imaging, and autonomic physiology.
- **FEEL role**: future expansion dataset for naturalistic/physiology-rich pretraining or transfer, not a first two-month priority unless access is easy.
- **Source**: https://www.nature.com/articles/s41597-025-05154-x

## Affective Computing Foundation-Model Literature

### AffectGPT

- **Venue**: ICML 2025 oral.
- **Type**: dataset, model, and benchmark for MLLM-based emotion understanding.
- **Claim**: Moves multimodal emotion recognition from discriminative labels toward descriptive emotion understanding with fine-grained emotion captions, over 2,000 emotion categories, 115K samples, and MER-UniBench.
- **FEEL role**: top-conference evidence that stimulus-side affective modeling is moving toward caption/rationale/context-rich supervision.
- **Source**: https://icml.cc/virtual/2025/oral/47171
- **Code/data**: https://github.com/zeroQiaoba/AffectGPT

### VidEmo

- **Venue**: NeurIPS 2025.
- **Type**: emotion-centric video foundation model.
- **Claim**: Uses affective-tree reasoning guidance with fine-grained captions and rationales to model open-set, dynamic, and context-dependent emotions in video.
- **FEEL role**: top-conference precedent for treating video emotion as context/rationale-based representation learning, not only classification.
- **Source**: https://openreview.net/forum?id=x8lg9aihwl

### AVERE / EmoReAlM

- **Venue**: ICLR 2026.
- **Type**: audiovisual emotion reasoning benchmark and preference-optimization method.
- **Claim**: Introduces EmoReAlM for cue-emotion associations, hallucinations, and modality agreement; uses AVEm-DPO to reduce spurious associations and text-prior hallucinations.
- **FEEL role**: direct methodological template for cue grounding, hallucination control, and preference-style alignment in brain-tuned affective VLM/LLM track.
- **Source**: https://openreview.net/forum?id=td682AAuPr
- **Project**: https://avere-iclr.github.io/

### EmotionHallucer

- **Venue**: ICLR 2026.
- **Type**: benchmark for emotion hallucinations in MLLMs.
- **Claim**: Evaluates emotion-specific hallucinations in multimodal large language models.
- **FEEL role**: diagnostic reference for checking whether stimulus-side affective models invent emotional cues unsupported by audiovisual evidence.
- **Source**: https://openreview.net/forum?id=ahWmeQG3K2

### HitEmotion / ToM-Guided Multimodal Emotion Reasoning

- **Venue**: ICLR 2026.
- **Type**: Theory-of-Mind-grounded benchmark and reinforcement-learning approach for multimodal emotion reasoning.
- **Claim**: Diagnoses emotional reasoning by increasing cognitive depth and uses intermediate mental-state supervision to improve reasoning.
- **FEEL role**: supports using context/rationale embeddings as auxiliary targets, while keeping brain claims grounded in fMRI alignment rather than pure ToM theory.
- **Source**: https://openreview.net/forum?id=8VSrk2CaBr

### Schuller et al. 2026: Affective computing has changed

- **Type**: perspective/review on foundation models in affective computing.
- **Claim**: Foundation models are disrupting affective computing across vision, language, and speech, while raising evaluation concerns for affective validity.
- **FEEL role**: establishes that "foundation models for affect" is an active AI direction, but also highlights that neuroscience-grounded affective FMs remain underdeveloped.
- **Source**: https://www.nature.com/articles/s44387-025-00061-3

### Affective Computing in the Era of Large Language Models

- **Type**: NLP-centric survey.
- **Claim**: LLMs reshape affective understanding and affective generation through prompting, instruction tuning, RL-style alignment, and broader world knowledge.
- **FEEL role**: reference for external affective language models that may support stimulus annotation or text-side affect embeddings.
- **Source**: https://huggingface.co/papers/2408.04638

### Multimodal Large Language Models Meet Multimodal Emotion Recognition and Reasoning

- **Type**: survey.
- **Claim**: Reviews MLLM-based emotion recognition and reasoning across architectures, datasets, and benchmarks.
- **FEEL role**: reference for stimulus-side multimodal affective reasoning, not a replacement for brain modeling.
- **Source**: https://huggingface.co/papers/2509.24322

### MMAFFBen

- **Type**: multilingual multimodal affective benchmark.
- **Claim**: Evaluates LLMs/VLMs on sentiment and emotion tasks across text, image, and video in 35 languages; introduces affective fine-tuning data and MMAFFLM models.
- **FEEL role**: benchmark-design inspiration for affective evaluation, especially target diversity and intensity prediction.
- **Source**: https://huggingface.co/papers/2505.24423
- **Code/project**: https://github.com/lzw108/MMAFFBen

### MME-Emotion

- **Type**: MLLM emotional-intelligence benchmark.
- **Claim**: Evaluates multimodal emotional understanding and reasoning across diverse video scenarios with task-specific QA.
- **FEEL role**: reference for moving stimulus-side affective supervision beyond label prediction toward reasoning about triggers/context.
- **Source**: https://mme-emotion.github.io/

### EmoBench-M

- **Type**: benchmark for emotional intelligence in MLLMs.
- **Claim**: Evaluates foundational emotion recognition, conversational emotion understanding, and socially complex emotion analysis.
- **FEEL role**: stimulus-side affective evaluation reference; useful for defining richer external affective embeddings.
- **Source**: https://huggingface.co/papers/2502.04424

### Beyond Emotion Recognition

- **Type**: multi-turn multimodal emotion understanding and reasoning benchmark.
- **Claim**: Targets emotion reasoning rather than only emotion classification.
- **FEEL role**: supports the brain-tuned affective LLM/VLM track as a reasoning/representation problem, not just label matching.
- **Source**: https://huggingface.co/papers/2508.16859

### Why We Feel / EIBench

- **Type**: emotion interpretation benchmark for MLLMs.
- **Claim**: Emphasizes causal factors and rationale-based emotional reasoning rather than only "which emotion" labels.
- **FEEL role**: potential source of stimulus-side causal/contextual affective targets, kept separate from brain-grounded evaluation.
- **Source**: https://cvpr.thecvf.com/virtual/2025/35814

### 2026 Multimodal Emotion Recognition Survey

- **Type**: survey and taxonomy.
- **Claim**: Reviews MER advances from 2020-2025, emphasizing transformer models, fusion strategies, missing data, imbalance, and user generalization.
- **FEEL role**: practical reference for stimulus-only baselines, missing-modality handling, and temporal fusion.
- **Source**: https://www.sciencedirect.com/science/article/pii/S2667305326000177

## Neural-Signal Foundation Models with Emotion Downstream

### REVE

- **Type**: EEG foundation model.
- **Claim**: Pretrained on over 60,000 hours of EEG from 92 datasets and 25,000 subjects; achieves strong transfer across tasks including emotion recognition.
- **FEEL role**: methodological reference for heterogeneous neural-signal pretraining and emotion downstream transfer.
- **Source**: https://brain-bzh.github.io/reve/

### Brain-OF

- **Type**: fMRI/EEG/MEG omnifunctional foundation model.
- **Claim**: Jointly pretrains across functional neuroimaging modalities using any-resolution sampling, sparse MoE, and masked temporal-frequency modeling; evaluates affective computing among downstream tasks.
- **FEEL role**: broad neural-signal FM precedent, especially for multimodal neural data and time-frequency objectives.
- **Source**: https://www.researchgate.net/publication/401418431_Brain-OF_An_Omnifunctional_Foundation_Model_for_fMRI_EEG_and_MEG

### REVE and LaBraM-style EEG FM line

- **Type**: EEG foundation-model family.
- **Claim**: Large-scale EEG pretraining can generalize to emotion recognition, stress detection, BCI, sleep, seizure, and other downstream tasks.
- **FEEL role**: useful for architecture and pretraining-objective ideas if physiology or EEG is added later.
- **Source**: https://www.emergentmind.com/topics/eeg-foundation-models-eeg-fms

## Brain-Tuning and Brain-Aligned AI

### Brain-Score Vision

- **Type**: benchmark platform for model-brain-behavior alignment in vision.
- **Claim**: Artificial neural networks can be quantitatively evaluated by how well they match primate neural and behavioral measurements.
- **FEEL role**: conceptual template for an affective brain-score style evaluation of VLM/LLM emotion models.
- **Source**: https://github.com/brain-score/vision

### Brain-Score Language

- **Type**: benchmark platform for language model alignment with neural and behavioral measurements.
- **Claim**: Operationalizes language model comparison against brain and behavioral data using a standard interface.
- **FEEL role**: template for evaluating affective language models against naturalistic emotion fMRI.
- **Source**: https://github.com/brain-score/language

### Lu, Wang, Golomb 2026: Human EEG representational alignment

- **Type**: brain-aligned computer vision model.
- **Claim**: EEG-based representational alignment can make visual models more brain-like, improving alignment with EEG, fMRI, and behavior.
- **FEEL role**: direct precedent for brain-tuning external VLM representations with human neural data.
- **Source**: https://www.nature.com/articles/s42003-026-09685-w

### Moussa, Klakow, Toneva 2024: Brain-tuning speech language models

- **Type**: fMRI-tuned speech/language model.
- **Claim**: Fine-tuning speech language models with fMRI responses to natural stories improves brain alignment and semantic understanding.
- **FEEL role**: direct methodological precedent for brain-tuned affective LLM/VLM adapters.
- **Source**: https://huggingface.co/papers/2410.09230

### Moussa and Toneva 2025: Multi-participant brain-tuning

- **Type**: scalable brain-tuning for speech models.
- **Claim**: Jointly predicting fMRI from multiple participants improves generalization, data efficiency, and downstream semantic performance.
- **FEEL role**: supports multi-subject brain-tuning rather than subject-specific overfitting.
- **Source**: https://papers.cool/arxiv/2510.21520

### Antonello, Vaidya, Huth 2023: Scaling laws for language encoding models in fMRI

- **Type**: language-model-to-fMRI encoding study.
- **Claim**: Larger language models show log-linear improvements in predicting fMRI responses to natural language, with similar scaling for fMRI training data.
- **FEEL role**: supports using modern LLM representations and considering model/data scaling in brain alignment.
- **Source**: https://pmc.ncbi.nlm.nih.gov/articles/PMC11258918/

### Narratives fMRI dataset

- **Type**: naturalistic spoken story fMRI benchmark.
- **Claim**: Provides 345 subjects, 891 functional scans, and 27 stories as a benchmark for naturalistic language comprehension models.
- **FEEL role**: analogy for how naturalistic neuroimaging datasets can become model-evaluation infrastructure.
- **Source**: https://www.nature.com/articles/s41597-021-01033-3

### SED-GPT

- **Type**: long-sequence semantic and emotion decoding from fMRI.
- **Claim**: Uses a GPT-style semantic decoding framework and GoEmotions-derived emotional distributions to decode fine-grained semantics and emotions from fMRI in an exploratory study.
- **FEEL role**: direct cautionary precedent for brain-to-emotion decoding with LLM priors; useful for the brain-tuned affective LLM/VLM track, but not evidence that an fMRI emotion foundation model already exists.
- **Source**: https://www.mdpi.com/2076-3417/15/20/11100

### EmoMind: Decoding Affective Captions from Human Brain fMRI (Mohammed, Gu, Fang 2026)

- **Type**: brain-to-text affective caption *generation* pipeline (decoding).
- **Claim**: Per-subject fMRI decoded into a neutral semantic caption (DeBERTa-large 24-layer retrieval) plus a continuous 34-D Cowen & Keltner emotion vector (per-subject ridge), then rewritten by an axis-token BART with classifier-free guidance. Beats label-prompted GPT-4 on subject-specificity, RSA structure, and SWAP causal control across MindCaptioning + Horikawa 2020. Key probe: TRIBE v2 synthetic-brain substitution preserves point-wise affect (SWAP own-leakage 2.8%->5.2%) but loses ~74% of between-clip RSA structure (rho +0.635 -> +0.166).
- **EmoBrain/EmoViS role**: nearest competitor on the decoding side (D1/D2) — full delineation in `docs/notes/emomind_team_post_20260622.txt`. For EmoViS (sensory-semantic representational study) it is a *foil*: it separates affect from a single monolithic semantic caption and shows model-predicted brain loses most emotion relational geometry, but never decomposes that structure along the sensory->semantic axis or localizes it in cortex, which is exactly our white space. Exploitation plan in `docs/notes/emomind_exploitation_20260622.md`.
- **Status**: arXiv:2605.16739v2 [cs.LG], 2026-06-11. Preprint (NeurIPS submission, not yet accepted) — cite as preprint.
- **Source**: arXiv:2605.16739

## Du / Fu / He 그룹 (CAS) — 같은 Horikawa 데이터 선행/경쟁군

Changde Du, Kaicheng Fu, Zhongyu Huang, Huiguang He (Institute of Automation, CAS) 그룹 이 **우리 와 같은 Horikawa 2020 정서 영상 fMRI (5 subject, CK34)** 로 fine-grained emotion decoding 을 개척. EmoBrain 의 가장 직접적 선행/경쟁. 7편 상세 review + 우리 positioning 은 `docs/reference/du_fu_group_review_0707.md`.

### GED — Graph Emotion Decoding (MICCAI 2022 → TMI 2023) ★ 가장 직접 비교

- **Type**: brain→34D emotion regression, emotion-brain bipartite graph + GNN. (PDF 원문 확인.)
- **Data**: Horikawa 5 subject, **2196 pair = 2181 unique + 15 duplicate**, 34 category continuous (우리 cowen34_order 동일), 370 region (360 HCP + 10 subcortical). Per-subject 10-fold (1976/220) + cross-subject LOSO (TMI).
- **Target**: rater binary → 평균 [0,1] proportion. **우리 crowd-proportion target 과 동일.**
- **Metric**: **MAE 만** (34 감정 합산, Pearson 아님 — web 조사 오류 정정). Within-subject GED best 1.64-1.67, LOSO GED 1.689±0.015 (BrainGNN 1.727, GCN 1.826, FNN 2.384). 우리 pooled ridge raw MAE 0.054×34 ≈ 1.84 (환산) ≈ GCN 수준. **target·metric 동일 하므로 우리 예측 에 GED 식 MAE 재계산 시 직접 대조.**
- **EmoBrain role**: continuous-regression + 같은 target 의 nearest external anchor. bipartite (emotion×ROI) graph 는 우리 34×34 structure loss 의 generalization. Relation prior 가 decoding 을 돕는 존재 증명 (structure loss default OFF 재고 근거).
- **Source**: TMI DOI 10.1109/TMI.2023.3246220 (PMID 37027550), MICCAI DOI 10.1007/978-3-031-16452-1_38. Code https://github.com/zhongyu1998/GED. PDF = Du2/Du3.

### ML-BVAE — Multi-view Multi-label Fine-grained Emotion Decoding (TNNLS 2022)

- **Type**: multi-label binary 분류 (27-cat, 0.1 threshold). Multi-view VAE (L/R/L−R PoE) + label co-occurrence masked self-attention + asymmetric focal loss. (PDF 원문 확인.)
- **Data**: MEMO27 = Horikawa 5 subject, HCP360. Metric (5-subj avg) miF1 0.505 / maF1 0.398 / mAP 0.448 / e-AP 0.619 (Pearson 없음). LR(Horikawa 선형 baseline) mAP 0.246.
- **EmoBrain role**: 가장 강한 fine-grained decoding 선행. 숫자 비교 불가 (binarize 분류). 우리 regression-vs-classification + 27→34 확장 을 contribution 으로. 그들 co-occurrence 모델링 vs 우리 independent MSE.
- **Source**: arXiv 2211.02629. Code https://github.com/KaichengFu1997/ML-BVAE. PDF = Du1.

### EmoGrowth — Incremental Multi-label Emotion Decoding (ICML 2025)

- **Type**: class-incremental multi-label 분류. Augmented Emotional Relation Graph (co-occurrence P(i|j)) + GIN GAE + affective-dim RSM distillation. (PDF 원문 확인.)
- **Data**: Brain27 = Horikawa 5 subject, 27-cat + 14 affective dim, 0.1 threshold, 2880-dim ROI-pooling (360×8), train 1800/test 396. Brain27 subject1 mAP 44.2/43.8/41.9/39.5.
- **EmoBrain role**: continual 기계장치 는 우리 problem 아님. 단 structure loss 에 borrowable — arctanh reparam (Eq. 12), affective-dim RSM as second teacher, oracle-vs-learned ERG Pearson (RKD r=0.86 vs 0.75). **NV0 경고**: LLaMA 3.1-8B sentence embedding 을 label 로 naive 사용 시 오히려 성능 하락 (ablation) → LLM 은 구조 안 에서 써야 함.
- **Source**: PMLR v267 (ICML 2025). arXiv 2405.20600. Code https://github.com/ChangdeDu/EmoGrowth. PDF = Du_4.

### iScience 2023 — Topographic Representation (encoding, 표상)

- **Type**: voxel-wise encoding (34 emotion→brain), topographic map, banded ridge.
- **Data**: Horikawa 5 subject, 34-cat + 14-dim.
- **EmoBrain role**: ROI 우선순위 근거 (TPJ ~62% / IPL ~50% / LO 51-67% significant voxel, V1 최저) → modular encoder up-weight. "emotion high-D + distributed" (cortex 21% significant, locationism 기각). Behavioral-brain dissociation (neural 0.56 vs behavioral 0.20-0.25) → 우리 sub-question (d). Valence not primary neural axis.
- **Source**: DOI 10.1016/j.isci.2023.107571. OSF https://osf.io/9uyn2/. (encoding-only, per-emotion decoding accuracy 없음.)

### TAFFC 2023 — CNN-Brain Alignment (우리 CCN 라인)

- **Type**: brain RSM 을 video CNN 에 inductive bias 주입 (brain→CNN 단방향). RSA loss + learnable per-layer weight + Fisher-z.
- **Data**: Brain = Horikawa 5 subject. Video task = VideoEmotion-8 / Ekman-6 (별개 자극).
- **EmoBrain role**: CCN video-brain alignment 라인 의 방향-반대 foil. Borrowable = softmax-gamma layer weight + Fisher-z RSA matching. Tension 해소 — "brain improves lightweight CNN" vs 우리 "strong CLIP 0.60 > brain 0.30" 는 model capacity regime 이 달라 모순 아님.
- **Source**: DOI 10.1109/TAFFC.2023.3316173. Code https://osf.io/ucx57.

### Information Fusion 2025 — Hierarchical Emotional Areas (Horikawa 아님)

- **Type**: FC 트리 정보전파 깊이 로 hierarchical emotional area 식별. HEmoN (LSTM per level).
- **Data**: **Horikawa 아님.** StudyForrest (15 subj, 6 basic) + Vimeo (8 subj, 80). Power 264 ROI.
- **EmoBrain role**: "distributed + hierarchical (sensory→psychological→cognitive)" 근거, psychological constructionist 지지. **주의**: visual 이 Level 1/2/3 재등장 (visual=저차 전용 서사 완화), 그들 위계(FC 트리) ≠ 우리 ISC. "상위 명제 수렴" 수준 만.
- **Source**: arXiv 2408.00525. PII S1566253524003919. (DOI 미확인.)

## Dataset/Challenge References

### Algonauts Project 2025

- **Type**: multimodal movie-fMRI encoding challenge.
- **Claim**: Uses CNeuroMod movie data with visual frames, audio samples, transcripts, and 1,000-parcel fMRI responses from four subjects.
- **FEEL role**: benchmark and data/model reference for TRIBE-style multimodal fMRI response prediction.
- **Source**: https://algonautsproject.com/2025/braindata.html

### CNeuroMod

- **Type**: dense single-subject naturalistic fMRI resource.
- **Claim**: Provides roughly ten hours per subject for multiple movie datasets including Friends seasons and movie10.
- **FEEL role**: high-value expansion dataset if access and preprocessing are feasible.
- **Source**: https://www.cneuromod.ca/gallery/datasets/
