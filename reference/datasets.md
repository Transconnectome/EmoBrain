# NetFeeliX Dataset Decision Table

This document is the canonical dataset inventory for NetFeeliX. It prioritizes datasets by how directly they support **SwiFT-first emotion-specific brain representation development**, not by general popularity.

## Decision Summary

| Tier | Dataset | Role | Brain data | Stimulus/context | Target | SwiFT use | TRIBE v2 use | Priority | Main risk |
|---|---|---|---|---|---|---|---|---|---|
| 0 | Horikawa/Cowen emotional videos | Core downstream | fMRI | 2,185 short emotional videos | high-dimensional emotion category ratings | emotion head, affect geometry probe, fine-tuning benchmark | stimulus-only and stimulus-to-brain teacher for short videos if features are extractable | Start first | short clips limit context/reasoning claims |
| 0 | Emo-FilM | Core naturalistic downstream | fMRI + physiology | 14 short films | 50 emotion/appraisal/component annotations | emotion-specific fine-tuning, component/appraisal heads | multimodal stimulus features, context-alignment targets | Start first | access, annotation timing, preprocessing burden |
| 0 | HCP 7T movie | Naturalistic pretraining | 7T fMRI, 184 subjects | movie clips, TR 1 s | no direct emotion labels | continued pretraining for SwiFT, masked/contrastive/JEPA objectives | stimulus-conditioned pretraining if movie features are aligned | Start first | no emotion labels; target comes from transfer |
| 1 | Affective Videos ds000205 | Lightweight emotion benchmark | fMRI | 5 s audiovisual clips | valence/arousal | quick emotion regression/classification benchmark | optional stimulus-only baseline | Add early if easy | small sample size |
| 1 | REELMO | Context/reasoning and affect trajectories | behavioral reports + fMRI subset | 60 full movies; fMRI subset on Jojo Rabbit | 20 affective states at 1 s resolution | context-aware transfer if fMRI subset is usable | strong source of affective stimulus trajectories | Add for context | fMRI subset access/format |
| 1 | NeuroEmo | Cross-cultural emotion downstream | fMRI | Bollywood emotion clips | emotion labels | downstream generalization and dynamic-connectivity comparison | optional stimulus-only/cultural context features | Add after core datasets | metadata/stimulus-label details |
| 1 | IAPS fMRI NeuroVault | Fast valence-category benchmark | preprocessed beta maps | 90 IAPS emotional scenes | positive/neutral/negative blocks | beta-map adaptation, image-level valence category head | static image feature comparison, no temporal fusion needed | Add early if beta-map format fits | not raw 4D time series; block-level only |
| 1 | NSD | Large static-image fMRI representation | 7T fMRI, 8 subjects, 9k-10k images per subject | COCO natural scenes | no native emotion labels | static-image brain representation pretraining/adaptation; visual cortex-heavy test | image features and pseudo-affective labels from CLIP/MLLM/image affect models | Add strategically | not emotion-labeled; not naturalistic movie |
| 1 | OASIS stimulus set | Open affective stimulus labels | none | 900 affective images | normative valence/arousal | no direct fMRI use unless paired with other data | stimulus-side affective supervision and pseudo-label calibration | Add as label source | stimulus set, not fMRI dataset |
| 2 | Koide-Majima/Nishimoto | Secondary high-dimensional benchmark | fMRI | 3 h emotional audiovisual movies | 80 emotion labels | high-dimensional emotion transfer if accessible | audiovisual alignment and temporal labels | Add if accessible | data access uncertainty |
| 2 | CNeuroMod/Algonauts 2025 | Multimodal encoding reference | dense fMRI, 1,000 parcels in challenge | Friends, films, documentary; video/audio/transcripts | no primary emotion labels | auxiliary naturalistic pretraining or alignment validation | direct TRIBE/TRIBE v2 engineering reference | Add for alignment engineering | not emotion-specific |
| 2 | BOLD Moments | Short-video auxiliary encoding | fMRI | 1,102 3 s videos | object/scene/action/sentence/memorability | dynamic visual-event representation test | short-video stimulus-to-fMRI comparison | Future support | not emotion-specific |
| 2 | Spacetop | Physiology-rich expansion | fMRI + autonomic physiology | naturalistic movie + tasks | not primarily emotion labels | physiology-aware adaptation and multi-state transfer | context and physiology-rich auxiliary features | Future support | broad scope; may distract from core |
| 2 | 101 Dalmatians | Multimodal generalization | fMRI | audiovisual/auditory/visual movie variants | semantic/event descriptors | modality-specific naturalistic transfer | multimodal context features | Future support | not emotion-specific |

## Tier 0 Core

### Horikawa / Cowen Emotional Video fMRI

- **Role**: core brain-side affect geometry benchmark.
- **Brain data**: fMRI responses to 2,185 emotion-evoking videos.
- **Target**: high-dimensional emotion category ratings from Cowen/Keltner-style emotion space.
- **SwiFT use**:
  - attach emotion vector head to SwiFT features,
  - compare frozen, adapter, partial fine-tuning, and continued-pretrained SwiFT,
  - use as the main high-dimensional affect geometry task.
- **TRIBE v2 use**:
  - extract video/audio/text stimulus features where possible,
  - compare stimulus-only emotion prediction against SwiFT brain-only prediction,
  - optionally align TRIBE-style stimulus latents with SwiFT fMRI latents.
- **Sources**:
  - https://www.sciencedirect.com/science/article/pii/S2589004220302455
  - https://openneuro.org/datasets/ds002425
  - https://data.mendeley.com/datasets/jbk2r73mzh

### Emo-FilM

- **Role**: core naturalistic emotion downstream dataset.
- **Brain data**: fMRI from 30 participants, plus physiology.
- **Stimulus**: 14 short films, over 2.5 hours combined.
- **Target**: 50 annotations including discrete emotions, appraisals, motivation, motor expression, physiological response, and feeling.
- **SwiFT use**:
  - fine-tune/adapter-tune SwiFT on naturalistic affect targets,
  - add multi-task heads for emotion, appraisal, and physiology,
  - test whether HCP movie continued pretraining improves naturalistic emotion transfer.
- **TRIBE v2 use**:
  - generate video/audio/text features for film segments,
  - compare stimulus-only and brain-stimulus aligned models,
  - use appraisal/component annotations to bridge toward context reasoning.
- **Source**: https://www.nature.com/articles/s41597-025-04803-5

### HCP Young Adult 7T Movie Watching

- **Role**: primary naturalistic fMRI pretraining dataset.
- **Brain data**: 184 7T subjects, four movie runs, TR 1 s, 1.6 mm isotropic.
- **Stimulus**: independent film and Hollywood movie excerpts.
- **Target**: no direct emotion labels.
- **SwiFT use**:
  - continued pretraining of SwiFT on movie fMRI,
  - masked fMRI modeling, temporal contrastive learning, JEPA/future latent prediction,
  - subject-invariant representation learning before emotion fine-tuning.
- **TRIBE v2 use**:
  - optional stimulus-conditioned pretraining if movie features and timing are aligned,
  - compare TRIBE-predicted brain activity against observed HCP movie fMRI.
- **Source**: https://www.humanconnectome.org/hcp-protocols-ya-7t-imaging

## Tier 1 High-Value Additions

### Affective Videos / OpenfMRI ds000205

- **Role**: quick valence/arousal feasibility benchmark.
- **Brain data**: fMRI from 11 subjects.
- **Stimulus**: 5-second dynamic audiovisual clips.
- **Target**: valence and arousal.
- **SwiFT use**: fast regression sanity check for emotion-specific heads.
- **TRIBE v2 use**: optional stimulus-only audiovisual baseline.
- **Source**: https://www.openfmri.org/dataset/ds000205/

### REELMO

- **Role**: long-context affect trajectories and reasoning/context source.
- **Brain data**: fMRI subset from 20 volunteers.
- **Stimulus**: 60 full movies for behavioral ratings; fMRI subset watched Jojo Rabbit across two one-hour sessions.
- **Target**: 20 affective states at 1-second resolution, plus personality traits, empathy, synopses, and liking.
- **SwiFT use**: if fMRI subset is accessible, test context-window emotion prediction.
- **TRIBE v2 use**: generate movie-level stimulus trajectories and compare with human affect reports.
- **Sources**:
  - https://www.nature.com/articles/s41597-025-05159-6
  - https://springernature.figshare.com/articles/dataset/Lights_Camera_Emotion_REELMO_s_1060_Hours_of_Affective_Reports_to_Explore_Emotions_in_Naturalistic_Contexts/28255745

### NeuroEmo / OpenNeuro ds005700

- **Role**: culturally grounded emotion fMRI downstream dataset.
- **Brain data**: raw BIDS fMRI from 40 healthy participants.
- **Stimulus**: Indian Bollywood emotional clips.
- **Target**: emotion-elicitation labels and resting-state/task structure.
- **SwiFT use**: cross-cultural emotion generalization and dynamic-connectivity comparison.
- **TRIBE v2 use**: optional stimulus feature extraction from movie clips.
- **Source**: https://github.com/OpenNeuroDatasets/ds005700

### IAPS fMRI NeuroVault

- **Role**: fast image-valence category benchmark.
- **Brain data**: preprocessed beta maps for 56 participants; 53 have STAI questionnaires.
- **Stimulus**: 90 IAPS scenes in positive, neutral, and negative valence blocks.
- **Target**: positive/neutral/negative condition beta images.
- **SwiFT use**:
  - beta-map adaptation test,
  - emotion valence-category head,
  - sanity check for whether SwiFT spatial features carry affective contrast information.
- **TRIBE v2 use**: not primary; use static image encoders instead.
- **Risk**: not raw 4D fMRI, block design, beta maps only.
- **Source**: https://neurovault.org/collections/16284/

### Natural Scenes Dataset

- **Role**: large static-image fMRI representation resource.
- **Brain data**: 7T fMRI, 8 subjects, 9,000-10,000 natural scenes per subject, 22,500-30,000 trials.
- **Stimulus**: COCO natural scenes.
- **Target**: no native emotion labels; rich visual and recognition structure.
- **SwiFT use**:
  - static-image fMRI representation pretraining/adaptation,
  - visual-emotion transfer test with pseudo-affective labels,
  - compare fMRI visual representations with emotion/affect image embeddings.
- **TRIBE v2 use**:
  - not a direct video/audio/text use case,
  - use image encoders or image-to-caption pipelines for stimulus-side affect pseudo-targets.
- **Sources**:
  - https://registry.opendata.aws/nsd/
  - https://www.nature.com/articles/s41593-021-00962-x

### OASIS

- **Role**: open affective image stimulus and label source.
- **Brain data**: none.
- **Stimulus**: 900 color images.
- **Target**: normative valence and arousal ratings.
- **SwiFT use**: indirect only, by calibrating image affect pseudo-labels for NSD or other image fMRI datasets.
- **TRIBE v2 use**: not primary; use static image encoders or VLMs.
- **Risk**: not an fMRI dataset.
- **Source**: https://link.springer.com/article/10.3758/s13428-016-0715-3

## Tier 2 Expansion

- **Koide-Majima/Nishimoto**: high-dimensional emotional movie fMRI, useful if data access is feasible. Source: https://pubmed.ncbi.nlm.nih.gov/32798681/
- **CNeuroMod/Algonauts 2025**: strong engineering reference for TRIBE-style encoding and long naturalistic stimuli. Sources: https://algonautsproject.com/2025/braindata.html and https://www.cneuromod.ca/gallery/datasets/
- **BOLD Moments**: auxiliary short-video fMRI for dynamic visual-event representation. Source: https://www.nature.com/articles/s41467-024-50310-3
- **Spacetop**: physiology-rich naturalistic/task fMRI expansion. Source: https://www.nature.com/articles/s41597-025-05154-x
- **101 Dalmatians**: multimodal movie fMRI generalization, not first-priority. Source: https://www.nature.com/articles/s41597-025-06077-3

## Immediate Dataset Decision

Start with:

1. **Horikawa** for high-dimensional affect geometry.
2. **Emo-FilM** for naturalistic appraisal/component emotion targets.
3. **HCP 7T movie** for SwiFT continued pretraining.
4. **IAPS fMRI** or **Affective Videos** for fast valence/arousal/category sanity checks.
5. **NSD + OASIS/MLLM pseudo-labels** only if image-based affective transfer becomes strategically useful.
