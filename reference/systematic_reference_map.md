# FEEL Systematic Reference Map

This file organizes references by the role they play in the FEEL argument. It is the single canonical literature map. Do not create separate proposal, narrative, or emotion-foundation-model landscape files unless explicitly requested.

## 1. Minimal Theoretical Constraints for Target Design

Emotion theory is not the center of FEEL. It only constrains how targets are defined and evaluated.

| Reference | Core Point | Use in FEEL |
|---|---|---|
| Barrett 2017, Theory of Constructed Emotion | Emotion labels are constructed from prediction, interoception, categorization, and situated context rather than fixed neural fingerprints. | Justifies evaluating multiple target types instead of one fixed label. |
| Saarimäki 2021, Naturalistic Stimuli in Affective Neuroimaging | Naturalistic affective research must consider stimulus features, observer features, and experience reports. | Supports brain-stimulus-affect alignment as a modeling problem. |
| Film fMRI Hitchhiker's Guide | Film fMRI can bridge conventional task designs and naturalistic affective experience. | Justifies movie fMRI as a method for representation learning. |

Sources:

- Barrett: https://pmc.ncbi.nlm.nih.gov/articles/PMC5390700/
- Saarimäki: https://pmc.ncbi.nlm.nih.gov/articles/PMC8245682/
- Film fMRI guide: https://pmc.ncbi.nlm.nih.gov/articles/PMC10656947/

## 2. Affective fMRI Targets

| Reference | Data/Method | Core Point | Use |
|---|---|---|---|
| Horikawa et al. 2020 | 2,185 emotional videos + fMRI | High-dimensional categorical emotion explains brain activity better than low-dimensional affect in parts of cortex. | Main downstream benchmark. |
| Koide-Majima et al. 2020 | Audiovisual emotional movies + 80 emotion labels | Many emotion dimensions contribute to cortical emotion representation. | Secondary high-dimensional benchmark if accessible. |
| Emo-FilM 2025 | 14 films, 30 participants, fMRI/physiology/50 annotations | Modern naturalistic affective fMRI dataset. | Main modern downstream benchmark. |
| Ke et al. 2025 | Movie fMRI dynamic FC | Arousal generalizes better than valence across movie datasets. | Target ladder and dynamic-FC baseline. |
| Affective Videos ds000205 / Kim et al. 2016 | 11 participants viewed 32 five-second audiovisual clips in four valence-arousal quadrants | Direct core-affect fMRI dataset for valence/arousal decoding. | Lightweight screening benchmark before richer emotion targets. |
| IAPS fMRI NeuroVault | IAPS positive/neutral/negative beta maps from 56 participants | Fast valence-category fMRI benchmark. | Quick beta-map adaptation test for SwiFT. |
| NSD + OASIS | NSD large 7T image fMRI; OASIS open valence/arousal image norms | Static-image fMRI can be paired with affective pseudo-labels. | Strategic image-based extension, not core movie-emotion dataset. |
| NeuroEmo ds005700 | Bollywood emotional clips, 40 participants | Emotion fMRI with culturally grounded stimuli. | Possible cross-cultural downstream. |
| REELMO 2025 | fMRI n=20 watching Jojo Rabbit, TR=2s, 3,087 volumes/participant; movie affect annotations | Direct movie-fMRI benchmark with affect trajectories. | Dynamic fMRI test and later stimulus-side affect supervision. |
| SED-GPT 2025 | long-sequence fMRI semantic and emotion decoding | Uses an LLM-style decoding framework to reconstruct semantic and emotional distributions from fMRI. | Useful cautionary precedent for brain-to-emotion decoding with language models; exploratory, not a foundation model. |

Sources:

- Horikawa: https://www.sciencedirect.com/science/article/pii/S2589004220302455
- Koide-Majima: https://pubmed.ncbi.nlm.nih.gov/32798681/
- Emo-FilM: https://www.nature.com/articles/s41597-025-04803-5
- Ke: https://pubmed.ncbi.nlm.nih.gov/40215238/
- Affective Videos paper: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0161589
- Affective Videos data: https://www.openfmri.org/dataset/ds000205/
- NeuroEmo: https://github.com/OpenNeuroDatasets/ds005700
- REELMO: https://www.nature.com/articles/s41597-025-05159-6
- Horikawa Mendeley data mirror: https://data.mendeley.com/datasets/jbk2r73mzh
- SED-GPT: https://www.mdpi.com/2076-3417/15/20/11100

## 3. Naturalistic Movie fMRI for Pretraining

| Reference | Core Point | Use |
|---|---|---|
| HCP 7T Movie | 184 subjects, four movie runs, TR 1 s. | First large-subject naturalistic pretraining candidate. |
| van der Meer et al. 2020 | Movie viewing produces rich and reliable brain-state dynamics aligned with events and engagement. | Supports testing stimulus-locked dynamics, not assuming movie automatically solves emotion transfer. |
| Petrican et al. 2021 | Brain-environment alignment during movie watching relates to cognitive and affective function. | Supports affective relevance of movie-driven dynamics. |
| Gruskin and Patel 2022 | Resting connectivity predicts individual differences in movie activity. | Bridge between resting BFM and movie dynamics. |
| CNeuroMod / Algonauts 2025 | Dense movie fMRI with video, audio, and transcript streams. | Stimulus-brain alignment and TRIBE-style resource. |
| StudyForrest | Naturalistic Forrest Gump fMRI resources and long-film stimulation. | Tests long-film continuity and audiovisual narrative effects. |
| Narratives | Large story-listening fMRI collection with time-stamped transcripts. | Tests language/story context without visual emotion cues. |
| BOLD Moments | 1,102 short videos with repeated fMRI and metadata. | Auxiliary short-video encoding/pretraining dataset. |
| Spacetop 2025 | 101 participants, 6 hours scanning per participant, including naturalistic movie viewing and autonomic physiology. | Possible future naturalistic/physiology-rich expansion dataset; not first-priority unless access is easy. |

Sources:

- HCP 7T: https://www.humanconnectome.org/hcp-protocols-ya-7t-imaging
- van der Meer: https://www.nature.com/articles/s41467-020-18717-w
- Petrican: https://www.sciencedirect.com/science/article/pii/S1053811921004547
- Gruskin/Patel: https://pmc.ncbi.nlm.nih.gov/articles/PMC9491116/
- Algonauts: https://algonautsproject.com/2025/braindata.html
- CNeuroMod: https://www.cneuromod.ca/gallery/datasets/
- StudyForrest: https://openfmri.org/dataset/ds000113
- Narratives: https://www.nature.com/articles/s41597-021-01033-3
- BOLD Moments: https://www.nature.com/articles/s41467-024-50310-3
- Spacetop: https://www.nature.com/articles/s41597-025-05154-x

## 4. Existing Brain Foundation Models

| Model | Native direction | Role in FEEL |
|---|---|---|
| SwiFT | fMRI -> representation | 4D fMRI encoder baseline. |
| SwiFUN | rsfMRI -> task activation | Resting-to-task/emotion bridge. |
| BrainLM | fMRI time series -> representation | Generic BFM transfer baseline. |
| Brain-JEPA | fMRI -> latent predictive representation | JEPA-style pretraining precedent. |
| NeuroSTORM | raw 4D fMRI -> representation | State-of-the-art BFM baseline if accessible. |
| Omni-fMRI | atlas-free voxel-level BFM | Future atlas-free reference. |
| Brain-DiT | multi-state diffusion-transformer fMRI FM | Future multi-state pretraining reference. |
| Brain-OF | fMRI/EEG/MEG omnifunctional FM | Cross-modality neural FM precedent. |
| REVE / LaBraM EEG line | EEG -> transferable representation | Emotion downstream and heterogeneous neural-data precedent. |

Sources:

- SwiFT: https://huggingface.co/papers/2307.05916
- SwiFUN: https://direct.mit.edu/imag/article/doi/10.1162/imag_a_00440/126557/Predicting-task-related-brain-activity-from
- BrainLM: https://sciety.org/articles/activity/10.1101/2023.09.12.557460
- Brain-JEPA: https://neurips.cc/virtual/2024/poster/94113
- NeuroSTORM: https://www.nature.com/articles/s41551-026-01666-y
- Omni-fMRI: https://www.researchgate.net/publication/400339978_Omni-fMRI_A_Universal_Atlas-Free_fMRI_Foundation_Model
- Brain-DiT: https://papers.cool/arxiv/2604.12683
- REVE: https://brain-bzh.github.io/reve/
- Brain-OF: https://www.researchgate.net/publication/401418431_Brain-OF_An_Omnifunctional_Foundation_Model_for_fMRI_EEG_and_MEG

## 5. Stimulus-to-Brain Encoding and Alignment

| Reference | Native direction | Core Point | Use |
|---|---|---|---|
| TRIBE | video/audio/text -> fMRI | Multimodal transformer predicts fMRI responses to naturalistic video. | Architecture source for alignment and stimulus-only baselines. |
| TRIBE v2 | video/audio/language -> high-resolution fMRI | Multimodal foundation model for in-silico neuroscience. | Latest stimulus-brain encoding reference. |
| VIBE | video/audio/text -> fMRI | Practical fusion architecture for movie fMRI response modeling. | Implementation precedent for temporal fusion. |
| Hu and Mohsenzadeh 2025 | audiovisual features -> fMRI/EEG profiles | Acoustic, visual, categorical, and semantic information appear with distinct spatial/temporal profiles. | Justifies explicit multimodal temporal modeling. |
| V-JEPA2 | video -> representation | Self-supervised video features capture dynamics and prediction. | Candidate stimulus encoder for emotion and alignment. |

Sources:

- TRIBE: https://huggingface.co/papers/2507.22229
- TRIBE code: https://github.com/facebookresearch/algonauts-2025
- TRIBE v2: https://github.com/facebookresearch/tribev2
- VIBE: https://huggingface.co/papers/2507.17958
- Hu/Mohsenzadeh: https://www.nature.com/articles/s42003-024-07434-5
- V-JEPA2: https://ai.meta.com/research/publications/v-jepa-2-self-supervised-video-models-enable-understanding-prediction-and-planning/

## 6. Foundation Model + Emotion Landscape

This is the main narrative bridge for FEEL. Emotion foundation-model work is growing in affective computing, but fMRI emotion foundation models are not yet established.

### Affective Computing Task Taxonomy

| Task type | References | Target form | FEEL use |
|---|---|---|---|
| Sentiment/valence classification and regression | SemEval Affect in Tweets | ordinal class or continuous valence/intensity | low-dimensional sanity tasks |
| Continuous affect tracking | AVEC | frame/word-level arousal, valence, power/dominance, expectancy | Emo-FilM/movie-window trajectory design |
| Discrete and multi-label emotion classification | GoEmotions, MAFW, MME-Emotion | single label, multi-label vector, emotion distribution | Horikawa-style high-dimensional targets |
| Multimodal emotion recognition | MER/MuSe, AffectGPT | audio/video/text emotion prediction and free-form outputs | stimulus-only and multimodal alignment baselines |
| Emotion reasoning / interpretation | EIBench, MME-Emotion, EmoBench-M | cause, trigger, intent, rationale, QA | stimulus-side auxiliary target or embedding alignment |
| Descriptive affective captioning | AffectGPT / MER-Caption | natural-language emotion description | convert to embeddings/retrieval targets before brain-generation claims |

Implication: FEEL should not reduce affective computing to "emotion label
classification." Classification and regression are necessary first checks, but
the stronger model-development story uses multi-label/high-dimensional targets,
continuous trajectories, and stimulus-side cue/cause/caption embeddings.

| Area | References | Current pattern | FEEL implication |
|---|---|---|---|
| Affective computing FMs | Schuller et al. 2026; Affective Computing in the LLM Era; MLLMs and Emotion Reasoning; MMAFFBen | LLM/VLM/MLLM systems are being used for affective recognition, reasoning, and evaluation. | Use affective AI as stimulus-side features, annotation support, and possible brain-tuning targets. |
| Top-conference affective reasoning | ICML 2025 AffectGPT; NeurIPS 2025 VidEmo; ICLR 2026 AVERE, MME-Emotion, EmotionHallucer, HitEmotion | Top venues are moving from label prediction toward descriptive emotion understanding, cue grounding, hallucination control, ToM/appraisal-style reasoning, and preference optimization. | FEEL should use reasoning/context as stimulus-side supervision and alignment targets, not force Horikawa to become a reasoning dataset. |
| Emotional-intelligence benchmarks | MME-Emotion; EmoBench-M; Beyond Emotion Recognition; EIBench/Why We Feel | Benchmarks are moving from label prediction toward emotion reasoning, trigger inference, and socially contextual explanation. | Stimulus-side affective models can provide richer targets than category labels, but FEEL should keep brain-grounded evaluation separate from pure VLM scoring. |
| Multimodal emotion recognition surveys | 2026 MER surveys on missing modality, fusion, and transformer-based MER | Current affective computing emphasizes modality reliability, temporal synchronization, missing data, and cross-modal fusion. | Directly supports FEEL's benchmark matrix with brain-only, stimulus-only, and alignment conditions. |
| Neural-signal FMs | REVE; Brain-OF; LaBraM-style EEG FMs | Emotion recognition appears as one downstream task among many. | Borrow heterogeneous neural pretraining ideas, but keep fMRI emotion representation as the FEEL target. |
| fMRI BFMs | SwiFT; BrainLM; Brain-JEPA; NeuroSTORM; Omni-fMRI | Pretraining is usually generic, resting/task-general, or not emotion-organized. | Test transfer first; then decide whether naturalistic movie/story pretraining or emotion-specific adaptation is justified. |
| Stimulus-to-brain models | TRIBE; TRIBE v2; VIBE; Algonauts | Models predict fMRI from naturalistic stimuli, usually not emotion representation. | Convert encoding models into emotion and alignment components. |

Sources:

- Schuller: https://www.nature.com/articles/s44387-025-00061-3
- LLM affect survey: https://huggingface.co/papers/2408.04638
- MLLM emotion survey: https://huggingface.co/papers/2509.24322
- MMAFFBen: https://huggingface.co/papers/2505.24423
- AffectGPT: https://icml.cc/virtual/2025/oral/47171
- AffectGPT code/data: https://github.com/zeroQiaoba/AffectGPT
- VidEmo: https://openreview.net/forum?id=x8lg9aihwl
- AVERE / EmoReAlM: https://openreview.net/forum?id=td682AAuPr
- AVERE project: https://avere-iclr.github.io/
- EmotionHallucer: https://openreview.net/forum?id=ahWmeQG3K2
- HitEmotion / ToM-guided emotion reasoning: https://openreview.net/forum?id=8VSrk2CaBr
- MME-Emotion: https://mme-emotion.github.io/
- EmoBench-M: https://huggingface.co/papers/2502.04424
- Beyond Emotion Recognition: https://huggingface.co/papers/2508.16859
- EIBench / Why We Feel: https://cvpr.thecvf.com/virtual/2025/35814
- 2026 MER survey: https://www.sciencedirect.com/science/article/pii/S2667305326000177
- REVE: https://brain-bzh.github.io/reve/
- Brain-OF: https://www.researchgate.net/publication/401418431_Brain-OF_An_Omnifunctional_Foundation_Model_for_fMRI_EEG_and_MEG

## 7. Brain-Tuning and Brain-Aligned AI

| Reference | Core Point | Use |
|---|---|---|
| Brain-Score Vision | ANN vision models can be scored against primate neural and behavioral measurements. | Template for affective brain-score style evaluation. |
| Brain-Score Language | Language models can be benchmarked against neural and behavioral data. | Template for affective language-model evaluation. |
| Human EEG representational alignment | EEG alignment can make visual models more brain-like and behaviorally aligned. | Direct precedent for brain-tuned VLM direction. |
| Brain-tuning speech language models | fMRI fine-tuning improves semantic alignment and downstream semantic tasks. | Direct precedent for brain-tuned affective LLM/VLM adapters. |
| Multi-participant brain-tuning | Jointly predicting fMRI from multiple participants improves generalization and data efficiency. | Supports multi-subject brain tuning rather than single-subject overfit. |
| Scaling laws for fMRI language encoding | Larger LMs and more fMRI data improve language-to-brain prediction. | Justifies modern LLM features and model/data scaling checks. |
| Narratives dataset | Large naturalistic story fMRI benchmark. | Analogy for model-evaluation infrastructure. |

Sources:

- Brain-Score Vision: https://github.com/brain-score/vision
- Brain-Score Language: https://github.com/brain-score/language
- EEG representational alignment: https://www.nature.com/articles/s42003-026-09685-w
- Brain-tuning speech LMs: https://huggingface.co/papers/2410.09230
- Multi-participant brain-tuning: https://papers.cool/arxiv/2510.21520
- Scaling laws: https://pmc.ncbi.nlm.nih.gov/articles/PMC11258918/
- Narratives: https://www.nature.com/articles/s41597-021-01033-3

## Gap Statement

FEEL should state the gap as a model-development gap, not a theory gap.

1. Affective computing has foundation-model momentum, but usually lacks neural grounding.
2. fMRI foundation models exist, but emotion is rarely the organizing target of pretraining or evaluation.
3. Stimulus-to-brain encoding models provide powerful naturalistic alignment machinery, but their native objective is fMRI response prediction.
4. Affective fMRI datasets provide emotion targets, but are too small and heterogeneous for naive scratch training.
5. Therefore, FEEL should first benchmark transfer, pretraining, and alignment routes, then develop the model family indicated by screening results.

## Narrative Use

Use this sequence in proposals and meetings:

1. The project is about model development for emotion-aware brain representation, not emotion theory.
2. Naturalistic affective fMRI gives the right downstream targets, but the datasets are small.
3. Existing BFMs test whether generic brain representations transfer to emotion.
4. Naturalistic movie/story fMRI tests whether stimulus-locked pretraining improves emotion transfer beyond resting/task-general transfer; HCP is the first candidate, not the whole strategy.
5. TRIBE-style models show how to align video/audio/text with fMRI; FEEL modifies them for emotion representation.
6. Affective LLM/VLM work provides external affective representations that can be brain-tuned with adapters or distillation.
7. MLLM emotion benchmarks show a shift from simple recognition to reasoning about causes and context; FEEL can borrow this stimulus-side richness while keeping the central claim brain-grounded.
8. Horikawa remains the high-dimensional brain-side emotion geometry probe; reasoning/context should be tested with Emo-FilM, REELMO, HCP/CNeuroMod/StudyForrest/Narratives movie-story data, and MLLM-derived cue/rationale targets.
9. The initial benchmark decides whether to prioritize SwiFT adapters, naturalistic pretraining, TRIBE-SwiFT alignment, or brain-tuned affective AI.
