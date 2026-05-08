# Search Log, 2026-05-08

This file records the initial web search used to scaffold NetFeeliX.

## Search Topics

- SwiFT fMRI foundation model spatiotemporal transformer.
- TRIBE fMRI encoding model.
- SwiFUN fMRI Transformer.
- NeuroSTORM Brain Foundation Model.
- BrainLM, Brain-JEPA, Omni-fMRI, Brain-DiT.
- HCP 7T movie watching fMRI.
- Emotion prediction from movie-watching fMRI.
- Horikawa, Emo-FilM, Koide-Majima, dynamic arousal prediction.

## Key Findings

1. TRIBE should be treated as a stimulus-to-brain encoding model, not as the same category as fMRI encoders such as SwiFT.
2. SwiFUN is directly relevant because it predicts task activation maps from resting-state fMRI and includes emotion-related contrasts in UK Biobank and ABCD.
3. NeuroSTORM is a major current BFM reference, with large-scale raw 4D fMRI pretraining.
4. HCP 7T movie-watching provides a practical pretraining dataset: 184 subjects, four movie runs, about one hour per subject, TR 1 s.
5. Ke et al. 2025 provides a useful baseline and suggests arousal generalizes better than valence in movie-watching fMRI.
6. Horikawa and Emo-FilM are direct emotion downstream datasets.

## URLs Consulted

- SwiFT: https://huggingface.co/papers/2307.05916
- SwiFUN paper: https://direct.mit.edu/imag/article/doi/10.1162/imag_a_00440/126557/Predicting-task-related-brain-activity-from
- SwiFUN code: https://github.com/Transconnectome/SwiFUN
- TRIBE: https://huggingface.co/papers/2507.22229
- TRIBE code: https://github.com/facebookresearch/algonauts-2025
- TRIBE v2 listing: https://ai.meta.com/global_search/
- TRIBE v2 code: https://github.com/facebookresearch/tribev2
- V-JEPA2: https://ai.meta.com/research/publications/v-jepa-2-self-supervised-video-models-enable-understanding-prediction-and-planning/
- NeuroSTORM: https://www.nature.com/articles/s41551-026-01666-y
- BrainLM: https://sciety.org/articles/activity/10.1101/2023.09.12.557460
- Brain-JEPA: https://neurips.cc/virtual/2024/poster/94113
- Brain-JEPA HF page: https://huggingface.co/papers/2409.19407
- Omni-fMRI: https://www.researchgate.net/publication/400339978_Omni-fMRI_A_Universal_Atlas-Free_fMRI_Foundation_Model
- Brain-DiT: https://papers.cool/arxiv/2604.12683
- HCP 7T protocol: https://www.humanconnectome.org/hcp-protocols-ya-7t-imaging
- Horikawa 2020: https://www.sciencedirect.com/science/article/pii/S2589004220302455
- Koide-Majima 2020: https://pubmed.ncbi.nlm.nih.gov/32798681/
- Emo-FilM: https://www.nature.com/articles/s41597-025-04803-5
- Ke et al. 2025: https://pubmed.ncbi.nlm.nih.gov/40215238/
- AffectPrediction code: https://github.com/jinke828/AffectPrediction

## Follow-Up Searches Needed

- Verify availability of pretrained weights for NeuroSTORM, Brain-JEPA, BrainLM, and Omni-fMRI.
- Check exact data access pathway for Emo-FilM and Horikawa.
- Search for HCP movie emotion annotation resources, if any exist.
- Search for recent work using HCP movie fMRI pretraining followed by affective downstream tasks.

## Additional Search Pass

Added after deeper refinement:

- Naturalistic movie fMRI and brain-state dynamics.
- Brain-environment alignment and affective function.
- CNeuroMod and Algonauts 2025 movie-fMRI resources.
- BOLD Moments short-video fMRI.
- Multimodal naturalistic audiovisual encoding.
- VIBE and video/audio/text fMRI response modeling.

Additional sources:

- van der Meer et al. 2020: https://www.nature.com/articles/s41467-020-18717-w
- Petrican et al. 2021: https://www.sciencedirect.com/science/article/pii/S1053811921004547
- Gruskin and Patel 2022: https://pmc.ncbi.nlm.nih.gov/articles/PMC9491116/
- View, engage, predict 2025: https://sciety.org/articles/activity/10.1101/2025.07.28.666907
- Hu and Mohsenzadeh 2025: https://www.nature.com/articles/s42003-024-07434-5
- BOLD Moments: https://www.nature.com/articles/s41467-024-50310-3
- Algonauts 2025 brain data: https://algonautsproject.com/2025/braindata.html
- CNeuroMod datasets: https://www.cneuromod.ca/gallery/datasets/
- VIBE: https://huggingface.co/papers/2507.17958

## Emotion-Aware Foundation-Model Search Pass

Queries:

- "emotion foundation model" affective neuroscience fMRI
- "affective foundation model" emotion representation learning neuroscience
- "foundation model" "affective neuroscience"
- "foundation models affective computing emotion recognition review"
- "physiological foundation model emotion recognition EEG ECG affective computing"
- "fMRI emotion dataset naturalistic film valence arousal OpenNeuro"

Findings:

- The phrase "emotion foundation model" is much more developed in affective computing than in affective neuroscience.
- Affective computing now has foundation-model discussions, LLM/VLM affective benchmarks, and multimodal emotion-recognition surveys.
- Neural-signal FMs increasingly include emotion recognition as a downstream task, especially EEG FMs such as REVE and LaBraM-style models, but do not center emotion as the organizing scientific target.
- New affective film resources exist beyond Horikawa and Emo-FilM, especially REELMO, Affective Videos, and NeuroEmo.

Additional sources:

- Affective computing foundation-model disruption: https://www.nature.com/articles/s44387-025-00061-3
- Affective computing in the LLM era: https://huggingface.co/papers/2408.04638
- MLLMs and emotion reasoning survey: https://huggingface.co/papers/2509.24322
- MMAFFBen: https://huggingface.co/papers/2505.24423
- REVE EEG foundation model: https://brain-bzh.github.io/reve/
- Brain-OF: https://www.researchgate.net/publication/401418431_Brain-OF_An_Omnifunctional_Foundation_Model_for_fMRI_EEG_and_MEG
- REELMO: https://www.nature.com/articles/s41597-025-05159-6
- REELMO data: https://springernature.figshare.com/articles/dataset/Lights_Camera_Emotion_REELMO_s_1060_Hours_of_Affective_Reports_to_Explore_Emotions_in_Naturalistic_Contexts/28255745
- Affective Videos: https://www.openfmri.org/dataset/ds000205/
- NeuroEmo: https://github.com/OpenNeuroDatasets/ds005700

## Brain-Tuning / Brain-Aligned AI Search Pass

Queries:

- "brain tuning" fMRI language model foundation model
- "brain aligned" vision language model fMRI EEG emotion
- "Brain-Score" vision language model neural benchmark
- "representational alignment" EEG visual model fMRI behavior

Findings:

- Brain-tuning and brain-aligned AI are better established in language, speech, vision, and EEG than in fMRI emotion.
- Existing work supports the idea that neural responses can act as an alignment or regularization signal for external AI models.
- For NetFeeliX, this should be framed as an adapter/distillation track rather than full LLM/VLM fine-tuning.
- This track is conditional: activate it if screening results show strong stimulus-side affective features or measurable brain-stimulus alignment.

Additional sources:

- Brain-Score Vision: https://github.com/brain-score/vision
- Brain-Score Language: https://github.com/brain-score/language
- EEG representational alignment: https://www.nature.com/articles/s42003-026-09685-w
- Brain-tuning speech language models: https://huggingface.co/papers/2410.09230
- Multi-participant brain-tuning: https://papers.cool/arxiv/2510.21520
- Scaling laws for fMRI language encoding: https://pmc.ncbi.nlm.nih.gov/articles/PMC11258918/
- Narratives dataset: https://www.nature.com/articles/s41597-021-01033-3

## Follow-Up Web Search Pass, 2026-05-08

Queries:

- "2026 affective computing foundation models emotion recognition survey multimodal LLM VLM"
- "fMRI emotion decoding foundation model 2025 GPT emotion decoding fMRI SED-GPT"
- "NeuroSTORM fMRI foundation model 2026 Nature Biomedical Engineering"
- "multimodal affective foundation model benchmark 2026 emotion reasoning"

Findings:

- NeuroSTORM now has a 2026 Nature Biomedical Engineering article and should be treated as a major current fMRI BFM baseline if access permits.
- Recent affective-computing benchmarks are moving beyond emotion classification toward emotional intelligence, trigger inference, and multimodal reasoning.
- SED-GPT is a direct but exploratory precedent for long-sequence fMRI semantic and emotion decoding with LLM priors.
- Spacetop adds a physiology-rich naturalistic fMRI option, but should remain a future expansion path rather than distracting the two-month initial benchmark.
- Horikawa now has an easily citable Mendeley data mirror in addition to OpenNeuro.

Additional sources:

- NeuroSTORM / general-purpose fMRI foundation model: https://www.nature.com/articles/s41551-026-01666-y
- Omni-fMRI: https://www.researchgate.net/publication/400339978_Omni-fMRI_A_Universal_Atlas-Free_fMRI_Foundation_Model
- Brain-DiT: https://papers.cool/arxiv/2604.12683
- Brain-DiT code: https://github.com/REDMAO4869/Brain-DiT
- SED-GPT: https://www.mdpi.com/2076-3417/15/20/11100
- MME-Emotion: https://mme-emotion.github.io/
- EmoBench-M: https://huggingface.co/papers/2502.04424
- Beyond Emotion Recognition: https://huggingface.co/papers/2508.16859
- EIBench / Why We Feel: https://cvpr.thecvf.com/virtual/2025/35814
- 2026 MER survey: https://www.sciencedirect.com/science/article/pii/S2667305326000177
- Spacetop: https://www.nature.com/articles/s41597-025-05154-x
- Horikawa Mendeley data mirror: https://data.mendeley.com/datasets/jbk2r73mzh

## Top-Conference Affective Reasoning Search Pass

Queries:

- "site:openreview.net ICLR 2026 emotion reasoning multimodal large language models"
- "OpenReview ICML 2025 multimodal emotion reasoning affective computing"
- "OpenReview NeurIPS 2025 emotion reasoning affective computing multimodal"
- "OpenReview ICLR 2026 AVERE emotion reasoning preference optimization"

Findings:

- Top-conference affective computing is shifting from category prediction to descriptive emotion understanding, cue grounding, hallucination control, Theory-of-Mind/appraisal-style reasoning, and preference optimization.
- Horikawa should not be framed as a reasoning/context dataset. It is better used as a high-dimensional brain-side affect geometry probe.
- The reasoning/context track should use naturalistic film/movie datasets and stimulus-side MLLM outputs: captions, cue-emotion QA, rationales, appraisal-like variables, and hallucination diagnostics.
- For NetFeeliX, the key model idea is not "decode natural-language reasoning directly from fMRI" in the first study. A safer claim is to align brain latents with richer stimulus-side context/rationale embeddings and test whether this improves emotion transfer.

Additional sources:

- ICML 2025 AffectGPT: https://icml.cc/virtual/2025/oral/47171
- AffectGPT code/data: https://github.com/zeroQiaoba/AffectGPT
- NeurIPS 2025 VidEmo: https://openreview.net/forum?id=x8lg9aihwl
- ICLR 2026 AVERE / EmoReAlM: https://openreview.net/forum?id=td682AAuPr
- AVERE project: https://avere-iclr.github.io/
- ICLR 2026 MME-Emotion: https://openreview.net/forum?id=oSX9aenbea
- ICLR 2026 EmotionHallucer: https://openreview.net/forum?id=ahWmeQG3K2
- ICLR 2026 HitEmotion / ToM-guided reasoning: https://openreview.net/forum?id=8VSrk2CaBr
- ICML 2025 EduInsightLLM: https://icml.cc/virtual/2025/50443
- NeurIPS 2025 diagnostic multimodal reasoning: https://openreview.net/forum?id=2S7VgHrx20
- NeurIPS 2025 representation-first emotion decoding from 7T fMRI workshop: https://neurips.cc/virtual/2025/132676
- NeurIPS 2025 emotional EEG joint pretraining: https://openreview.net/forum?id=xaxuzubN31
