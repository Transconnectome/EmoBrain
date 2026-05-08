# NetFeeliX Dataset Inventory

This is the canonical dataset document for NetFeeliX. Datasets are grouped by
their **experimental function**, not by an abstract priority ranking. The
central question is always:

```text
What can this dataset teach us about making SwiFT more emotion-specific?
```

The practical distinction is:

1. datasets with direct fMRI emotion targets,
2. movie-watching fMRI datasets for representation pretraining,
3. stimulus-to-brain encoding and alignment datasets,
4. image/static-stimulus resources for affective transfer,
5. physiology/context resources for later model expansion.

## Dataset Function Map

| Function | Dataset | Direct fMRI? | Direct emotion/affect target? | Primary NetFeeliX use |
|---|---|---:|---:|---|
| Emotion-labeled fMRI | Horikawa/Cowen emotional videos | yes | yes | high-dimensional affect geometry from brain activity |
| Emotion-labeled fMRI | Emo-FilM | yes | yes | naturalistic emotion/appraisal/component prediction |
| Emotion-labeled fMRI | Affective Videos ds000205 | yes | yes | valence/arousal benchmark on short audiovisual clips |
| Emotion-labeled fMRI | IAPS fMRI NeuroVault | beta maps | yes | image-valence category adaptation test |
| Emotion-labeled fMRI | NeuroEmo | yes | yes | cross-cultural emotion recognition from Bollywood clips |
| Emotion-labeled fMRI | Koide-Majima/Nishimoto | yes | yes | secondary high-dimensional emotional movie benchmark if accessible |
| Movie/story fMRI pretraining | HCP Young Adult 7T movie | yes | no | large-subject continued pretraining of SwiFT on stimulus-locked fMRI |
| Movie-watching fMRI pretraining | CNeuroMod / Algonauts 2025 | yes | no | multimodal movie encoding, TRIBE-style alignment engineering |
| Movie-watching fMRI pretraining | StudyForrest | yes | no | long film continuity and audiovisual narrative transfer |
| Story-listening fMRI pretraining | Narratives | yes | no | language/narrative context alignment without visual input |
| Movie-watching fMRI pretraining | 101 Dalmatians | yes | no | modality-control transfer across audiovisual/auditory/visual movie conditions |
| Context and affect trajectory | REELMO | fMRI subset | yes, mostly behavioral | long-context affect trajectories and MLLM/rationale targets |
| Static-image fMRI transfer | NSD | yes | no | large static-image fMRI representation with affective pseudo-labels |
| Stimulus affect labels | OASIS | no | yes | open image valence/arousal labels for NSD/image-model calibration |
| Visual-event auxiliary | BOLD Moments | yes | not primary | short-video visual event representation and stimulus-to-fMRI encoding |
| Physiology/context expansion | Spacetop | yes | partial affective ratings | physiology-aware and interoceptive/affective model extension |

## Immediate Dataset Logic

NetFeeliX should not choose datasets by popularity. It should choose datasets by
which model question they answer.

| Model question | Best dataset(s) | Reason |
|---|---|---|
| Can SwiFT decode rich emotion geometry from fMRI? | Horikawa/Cowen | direct fMRI responses to 2,185 emotion-evoking videos with high-dimensional ratings |
| Can SwiFT handle naturalistic appraisal/component targets? | Emo-FilM | fMRI, physiology, and 50 dynamic emotion/component annotations during film watching |
| Does naturalistic pretraining help emotion transfer? | HCP 7T movie, CNeuroMod, StudyForrest, Narratives | each tests a different hypothesis: large-subject transfer, multimodal alignment, long-film continuity, or language/narrative context |
| Is simple valence/arousal already recoverable? | Affective Videos, IAPS fMRI | smaller direct affect targets for fast sanity checks |
| Does stimulus context explain the label without brain data? | TRIBE v2 features, REELMO, Emo-FilM stimuli, Horikawa stimuli | stimulus-only comparison before claiming brain-specific emotion representation |
| Can we use large image fMRI for affective transfer? | NSD + OASIS / MLLM labels | NSD gives scale; OASIS and VLMs give affective pseudo-targets |
| Can TRIBE v2 be useful without replacing SwiFT? | CNeuroMod/Algonauts, HCP, Emo-FilM, Horikawa | use TRIBE v2 as stimulus-to-brain teacher, alignment module, and stimulus baseline |

## Direct Emotion-Labeled fMRI

These datasets are closest to the downstream task: fMRI is available and the
stimulus or trial has an emotion/affect target.

### Horikawa / Cowen Emotional Video fMRI

**Role in NetFeeliX**

Horikawa is the core **high-dimensional affect geometry** dataset. It should not
be framed as a reasoning dataset. Its value is that emotion labels are richer
than simple valence/arousal and are tied to fMRI responses evoked by many short
naturalistic videos.

**Dataset content**

- fMRI responses to 2,185 emotion-evoking videos.
- Behavioral target space from Cowen/Keltner-style high-dimensional emotion
  ratings.
- The original paper argues that emotion categories organize responses better
  than low-dimensional affective dimensions in several transmodal regions.
- OpenNeuro entry: `ds002425`.

**NetFeeliX task design**

- Primary task: predict high-dimensional emotion vectors from fMRI.
- Secondary task: compare category/vector prediction against valence/arousal
  reduction.
- Generalization task: train on videos or subjects and evaluate held-out
  videos/subjects.
- Representation analysis: CKA/RSA between SwiFT latent geometry and emotion
  rating geometry.

**SwiFT use**

- Frozen SwiFT + ridge/MLP emotion vector head.
- SwiFT adapter tuning or late-block fine-tuning.
- Affective query/token for pooling video-window fMRI features.
- Compare resting-state SwiFT weights vs HCP-movie continued-pretrained SwiFT.

**TRIBE v2 / stimulus use**

- Use stimulus-only video/audio features as an upper/lower comparison.
- Use TRIBE v2 predictions or intermediate multimodal latents as a teacher if
  video files and timing are easy to process.
- Evaluate whether brain representations add signal beyond stimulus embeddings.

**Risks**

- Videos are short; long-context reasoning claims do not fit.
- Need careful alignment of fMRI response windows with short video trials and
  hemodynamic lag.
- If target labels are averaged across raters rather than subject-specific, the
  task is closer to stimulus-evoked affect representation than individual
  emotion experience.

**Sources**

- https://www.sciencedirect.com/science/article/pii/S2589004220302455
- https://openneuro.org/datasets/ds002425
- https://data.mendeley.com/datasets/jbk2r73mzh

### Emo-FilM

**Role in NetFeeliX**

Emo-FilM is the strongest current fit for **naturalistic emotion dynamics**. It
contains fMRI, physiology, and detailed annotations during short film viewing.
This is where NetFeeliX can move beyond category prediction toward appraisal,
component, physiological, and context-sensitive targets.

**Dataset content**

- 30 fMRI participants watched 14 short films.
- Films total over 2.5 hours, with average film duration around 11 minutes.
- fMRI was acquired at 3T.
- Physiological recordings include heart rate, respiration, and electrodermal
  activity.
- Emotion annotations were collected from 44 raters.
- Final annotations include 50 items spanning discrete emotions and components:
  appraisal, motivation, motor expression, physiological response, and feeling.

**NetFeeliX task design**

- Multi-task emotion/component prediction from fMRI.
- Arousal/valence-like reduced targets for sanity checks.
- Component-specific heads: appraisal, motivation, expression, physiology,
  feeling.
- Context-window comparison: short local windows vs longer film context.
- Physiology-aware auxiliary targets where clean physiological time series are
  available.

**SwiFT use**

- Main fine-tuning dataset after Horikawa sanity checks.
- Adapter tuning with dataset-specific target heads.
- Subject adapter to separate shared film-locked responses from individual
  variation.
- Naturalistic-pretrained SwiFT should be tested here because the stimulus
  domain is naturalistic film.

**TRIBE v2 / stimulus use**

- Extract video/audio/text features from the 14 films.
- Compare stimulus-only prediction to fMRI-only prediction.
- Use stimulus features or TRIBE-predicted brain latents as alignment targets.
- Use annotations to evaluate whether alignment improves component-specific
  targets rather than only generic arousal.

**Risks**

- Timing and annotation smoothing must be handled carefully.
- Sample size is not large for full-model fine-tuning, so parameter-efficient
  tuning is important.
- Some items have lower reliability; target selection should use annotation
  reliability.

**Sources**

- https://www.nature.com/articles/s41597-025-04803-5
- https://openneuro.org/datasets/ds004892
- https://openneuro.org/datasets/ds004872

### Affective Videos / OpenfMRI ds000205

**Role in NetFeeliX**

Affective Videos is a compact direct affect benchmark. It is not the main
model-development dataset, but it is useful for quickly checking whether a
pipeline can recover valence/arousal from naturalistic audiovisual fMRI.

**Dataset content**

- 11 participants.
- 5-second dynamic audiovisual clips.
- Passive viewing task in scanner.
- Trial-level valence and arousal were analyzed from distributed fMRI patterns.
- OpenfMRI accession: `ds000205`.

**NetFeeliX task design**

- Arousal regression/classification.
- Valence regression/classification.
- fMRI-only vs stimulus-only comparison.
- Quick check for whether preprocessing, HRF windowing, and SwiFT readout are
  sane before scaling up.

**SwiFT use**

- Frozen SwiFT feature sanity check.
- Simple temporal pooling head.
- Compare against ROI/ridge/dynamic-FC baselines.

**TRIBE v2 / stimulus use**

- Use video/audio embeddings for stimulus-only valence/arousal prediction.
- If stimulus-only is strong and fMRI-only is weak, use this as evidence that
  alignment or richer brain targets are needed.

**Risks**

- Small subject count.
- Short clips constrain temporal modeling.
- Good for checking machinery, not for broad claims.

**Source**

- https://www.openfmri.org/dataset/ds000205/

### IAPS fMRI NeuroVault

**Role in NetFeeliX**

IAPS fMRI is a fast **static image valence-category** test. It is useful because
it gives preprocessed single-subject beta maps for positive, neutral, and
negative conditions. It is not useful for temporal dynamics.

**Dataset content**

- 56 participants.
- 90 IAPS emotional scenes.
- Positive, neutral, and negative block design.
- Each block contains six scenes from the same valence class.
- Each scene was shown for 2.5 seconds; each emotional block lasted 15 seconds.
- Each participant has beta images for positive, negative, and neutral
  conditions.
- 53 participants completed STAI questionnaires.

**NetFeeliX task design**

- Positive vs neutral vs negative classification from beta maps.
- Pairwise contrasts: negative-neutral, positive-neutral, positive-negative.
- Test whether SwiFT spatial features can transfer to static affective beta
  maps.

**SwiFT use**

- This is a model adaptation edge case because SwiFT expects 4D fMRI, while the
  dataset provides condition beta maps.
- Options:
  1. treat beta maps as a pseudo-time input with one or three frames,
  2. use only spatial stages/readout if the implementation allows it,
  3. train a beta-map adapter before using full temporal SwiFT.

**TRIBE v2 / stimulus use**

- TRIBE v2 is not the natural tool here.
- Use static image encoders, CLIP/VLM affect scores, or OASIS-style image norms
  for stimulus-side comparison.

**Risks**

- Not raw 4D time series.
- Block-level condition maps only.
- IAPS image access/licensing can be restrictive; NeuroVault beta maps are the
  practical entry point.

**Source**

- https://neurovault.org/collections/16284/

### NeuroEmo / OpenNeuro ds005700

**Role in NetFeeliX**

NeuroEmo is a cross-cultural emotion-recognition dataset using Indian Bollywood
movie clips. It is useful as a downstream generalization test and as a check
that NetFeeliX is not overfitting to Western stimulus sets.

**Dataset content**

- Raw BIDS fMRI from 40 healthy participants.
- Participants watched emotional Indian movie clips.
- Emotion-elicitation task plus resting-state data.
- Five emotion classes are used in the task design: calm, afraid, delighted,
  depressed, and excited.
- Clips are 30 seconds with white-noise intervals.

**NetFeeliX task design**

- Multi-class emotion recognition.
- Rest-to-task transfer: compare resting-state SwiFT features with task fMRI
  features.
- Dynamic-connectivity comparison against SwiFT temporal representations.

**SwiFT use**

- Downstream classification with subject-aware validation.
- Adapter/fine-tuning test after Horikawa/Emo-FilM.
- Cross-dataset test: train on one emotion dataset and evaluate on NeuroEmo
  where label mapping is compatible.

**TRIBE v2 / stimulus use**

- Extract features from Bollywood clips if stimulus files are available.
- Use stimulus-only classifier to estimate how much of the label is explained by
  clip identity/content.

**Risks**

- Need inspect event files and stimulus availability.
- Emotion labels are elicitation classes, not dense continuous ratings.
- Cultural/contextual specificity is a feature, but it complicates direct
  merging with other datasets.

**Source**

- https://github.com/OpenNeuroDatasets/ds005700

### Koide-Majima / Nishimoto Emotional Movie fMRI

**Role in NetFeeliX**

This is a strong secondary candidate for high-dimensional emotional movie fMRI,
but it should be treated as access-dependent until the data path is confirmed.

**Dataset content**

- fMRI responses during emotional audiovisual movies.
- Reported target space includes many emotion categories, often cited around 80
  emotion labels.
- More temporally extended than Horikawa short clips.

**NetFeeliX task design**

- High-dimensional emotional movie decoding.
- Compare short-video affect geometry from Horikawa with longer movie dynamics.
- Cross-dataset transfer from naturalistic-pretrained or Emo-FilM-tuned SwiFT.

**SwiFT use**

- Good target for testing whether emotion-specific SwiFT adaptations generalize
  beyond one dataset.

**TRIBE v2 / stimulus use**

- Natural candidate for multimodal stimulus feature extraction and latent
  alignment if stimuli are accessible.

**Risks**

- Access and exact files must be confirmed.
- Timing/label format may require substantial preprocessing.

**Source**

- https://pubmed.ncbi.nlm.nih.gov/32798681/

## Movie/Story fMRI For Pretraining

These datasets may not have emotion labels, but they are central for moving
SwiFT from resting-state/general fMRI toward naturalistic brain dynamics.

Naturalistic pretraining is not justified by the vague claim that "movie data is
more realistic than rest." The precise hypothesis is:

```text
Before emotion-specific fine-tuning, SwiFT may need to learn stimulus-locked
brain dynamics driven by visual, auditory, language, social, and narrative cues.
```

This matters because many emotion fMRI targets are small. Movie/story datasets
can provide self-supervised or alignment supervision before Horikawa, Emo-FilM,
or other emotion-labeled datasets are used. The success criterion is downstream
emotion transfer, not better movie reconstruction by itself.

#### Naturalistic pretraining rationale matrix

| Dataset/source | Best use | Why it is relevant for emotion representation | Main risk | Required control |
|---|---|---|---|---|
| HCP Young Adult 7T movie | first large-subject SwiFT continued pretraining | tests whether stimulus-locked movie fMRI improves transfer over resting/generic SwiFT | may learn only generic movie synchrony or low-level sensory response | compare against resting SwiFT and low-level stimulus controls |
| CNeuroMod / Algonauts 2025 | TRIBE-style stimulus-to-brain alignment | video, audio, and transcript features are organized for encoding models; useful for shared stimulus-brain latent learning | small subject count and parcel/volume mismatch | evaluate OOD movie encoding and then emotion transfer separately |
| StudyForrest | long-film continuity and audiovisual narrative | tests whether long coherent film structure helps temporal representation beyond short clips | copyright/stimulus access and dataset-specific story shortcuts | compare short-window vs long-window objectives |
| Narratives | language/story context without vision | isolates narrative/language context when visual emotion cues are absent | not directly visual emotion; no emotion labels | use as auxiliary context alignment, not core emotion benchmark |
| 101 Dalmatians | modality-control naturalistic movie fMRI | visual-only, auditory-only, and audiovisual conditions can test whether emotion transfer is vision-dominated | may distract from core datasets | run only after HCP/Horikawa/Emo-FilM pipelines are stable |
| Emo-FilM / REELMO | downstream affect validation | provides emotion/component/trajectory targets that test whether naturalistic pretraining actually transfers | smaller fMRI scale than pretraining datasets | always report transfer to direct emotion targets |

Sources for the additional naturalistic candidates:

- HCP 7T protocol: https://www.humanconnectome.org/hcp-protocols-ya-7t-imaging
- CNeuroMod dataset gallery: https://www.cneuromod.ca/gallery/datasets/
- Algonauts 2025 brain data: https://algonautsproject.com/2025/braindata.html
- StudyForrest: https://openfmri.org/dataset/ds000113
- Narratives: https://openneuro.org/datasets/ds002345

### HCP Young Adult 7T Movie Watching

**Role in NetFeeliX**

HCP 7T movie is the first **continued pretraining** candidate for SwiFT, not
because it is an emotion dataset, but because it is a standardized large-subject
movie-watching fMRI resource. It tests whether moving SwiFT from resting/general
fMRI toward stimulus-locked naturalistic dynamics improves transfer to direct
emotion targets.

**Dataset content**

- HCP Young Adult 7T acquisition.
- 184 subjects listed in the 7T MRI session summaries.
- Sessions include resting-state fMRI, movie-watching fMRI, retinotopy, and dMRI.
- Movie-watching runs are part of the 7T protocol.
- High-resolution 7T fMRI with naturalistic movie excerpts.

**NetFeeliX task design**

- Masked fMRI segment modeling.
- Temporal contrastive learning.
- JEPA-style future latent prediction.
- Subject-invariant learning.
- Optional stimulus-conditioned fMRI prediction if stimulus timing/features are
  aligned.
- Transfer-only success criterion: improvement on Horikawa, Emo-FilM,
  Affective Videos, or another direct emotion target.

**SwiFT use**

- Continue pretraining from existing SwiFT weights.
- Compare:
  1. original SwiFT,
  2. HCP movie-pretrained SwiFT,
  3. HCP movie + subject-invariant objective,
  4. HCP movie + stimulus-conditioned objective,
  5. CNeuroMod/StudyForrest/Narratives variants if they answer a concrete
     alignment, continuity, or context question.
- Evaluate transfer on Horikawa and Emo-FilM.

**TRIBE v2 / stimulus use**

- If movie stimuli can be processed, use TRIBE v2 or component encoders to
  produce stimulus latents.
- Use these latents for stimulus-conditioned pretraining or post-hoc alignment.

**Risks**

- No direct emotion labels.
- Pretraining can consume compute without transfer benefit; transfer benchmarks
  must be scheduled early.
- Movie pretraining may learn low-level visual motion, luminance, auditory
  energy, speech onset, or generic arousal rather than emotion-relevant
  representation.
- If improvement appears only on visually driven targets and not on
  high-dimensional emotion/component targets, the result should be interpreted
  as visual naturalistic adaptation, not emotion-specific learning.
- Stimulus timing and feature extraction may be nontrivial.

**Source**

- https://www.humanconnectome.org/hcp-protocols-ya-7t-imaging

### CNeuroMod / Algonauts 2025

**Role in NetFeeliX**

CNeuroMod and Algonauts 2025 are not emotion datasets, but they are highly
relevant for **stimulus-to-brain encoding and multimodal alignment**. They are
the most practical reference for TRIBE-style engineering.

**Dataset content**

- CNeuroMod includes densely sampled naturalistic fMRI.
- Movie resources include multiple seasons of Friends and Movie10.
- Algonauts 2025 uses CNeuroMod-derived movie stimuli and fMRI responses.
- Challenge data include visual frames, audio, and transcripts.
- Brain responses are provided for four subjects in 1,000 parcels.
- Training distribution includes Friends seasons 1-6 and Movie10-style stimuli;
  evaluation includes held-out Friends and OOD movies.

**NetFeeliX task design**

- Stimulus-to-fMRI encoding benchmark.
- TRIBE v2 reproduction/reference comparison.
- Shared latent learning between stimulus encoders and SwiFT fMRI encoder.
- Out-of-distribution movie generalization check for alignment models.

**SwiFT use**

- Use as auxiliary naturalistic pretraining or alignment validation.
- Test whether SwiFT latents align with multimodal stimulus features.
- If parcel data are easier than volumetric data, use parcel-level readout as a
  bridge before full 4D SwiFT.

**TRIBE v2 / stimulus use**

- Directly relevant: TRIBE v2 predicts fMRI responses to video/audio/text and
  outputs fsaverage5 cortical responses.
- Use TRIBE v2 as teacher, comparison model, or feature generator.

**Risks**

- Not emotion-specific.
- Parcel/surface/volume mismatch with SwiFT must be handled explicitly.
- The best use is alignment engineering, not downstream emotion claims.

**Sources**

- https://www.cneuromod.ca/gallery/datasets/
- https://algonautsproject.com/2025/challenge.html
- https://algonautsproject.com/2025/braindata.html

### StudyForrest

**Role in NetFeeliX**

StudyForrest is a naturalistic film dataset family centered on Forrest Gump. It
is useful when NetFeeliX needs to test whether coherent long-film structure
helps fMRI temporal representation beyond short emotional clips. It should be
treated as a secondary naturalistic pretraining/alignment source after the core
HCP/Horikawa/Emo-FilM path is running.

**Dataset content**

- Naturalistic fMRI resources built around prolonged Forrest Gump stimulation.
- The OpenfMRI `ds000113` entry provides high-resolution 7T fMRI during an
  auditory feature-film presentation, with auxiliary anatomical and noise
  measurements.
- Related studyforrest resources include audio-visual movie-watching data and
  denoised derivatives.
- Exact modality, preprocessing level, and stimulus access depend on the
  specific studyforrest release being used.

**NetFeeliX task design**

- Long-window vs short-window representation learning.
- JEPA/future-latent objective over coherent story segments.
- Compare whether long-film pretraining transfers better to Emo-FilM than
  short-clip-only learning.
- Use as an auxiliary narrative-continuity dataset, not as direct emotion
  supervision.

**SwiFT use**

- Parcel/ROI temporal pretraining first, then 4D SwiFT only if format and
  compute are practical.
- Test whether long-segment temporal pooling or future-latent prediction helps
  emotion downstream transfer.
- Useful for diagnosing whether SwiFT's temporal path is learning beyond local
  sensory events.

**TRIBE v2 / stimulus use**

- Extract video/audio/text features only after confirming which stimulus variant
  is available.
- Use stimulus latents for synchronized retrieval or cross-view prediction with
  fMRI windows.
- Do not use TRIBE-style results as emotion evidence unless transfer to
  Horikawa/Emo-FilM is shown.

**Risks**

- Not directly emotion-labeled.
- StudyForrest has multiple related releases; the exact usable release must be
  pinned before experiment design.
- Long coherent film can introduce story-specific shortcuts.
- Stimulus access and copyright constraints may affect feature extraction.

**Sources**

- https://openfmri.org/dataset/ds000113
- https://www.nature.com/articles/s41597-019-0303-3
- https://www.studyforrest.org/

### Narratives

**Role in NetFeeliX**

Narratives is not a movie-vision dataset and not an emotion dataset. Its value
is isolating language and story context. It can test whether affective context
alignment requires visual/audiovisual cues or whether narrative language alone
can regularize fMRI representations.

**Dataset content**

- Naturalistic story-listening fMRI collection.
- The Scientific Data descriptor reports 345 subjects, 891 functional scans, 27
  stories, and about 4.6 hours of unique spoken stimuli.
- Provides spoken story stimuli with time-stamped phoneme- and word-level
  transcripts.
- OpenNeuro entry: `ds002345`.

**NetFeeliX task design**

- Auxiliary context representation learning.
- Align fMRI windows with transcript/LLM embeddings.
- Compare language-only context representations with audiovisual movie
  representations.
- Later use for affective-rationale or context embedding transfer if language
  models produce reliable affective annotations.

**SwiFT use**

- Use only if the main emotion-fMRI pipeline needs a language/context
  pretraining branch.
- Parcel-level temporal encoder is likely the first practical route.
- Do not replace Horikawa/Emo-FilM with Narratives for emotion claims.

**TRIBE v2 / stimulus use**

- TRIBE v2 itself is multimodal movie-oriented; for Narratives, language/audio
  encoders are more natural.
- Use sentence/LLM embeddings, transcript timing, and audio features for
  fMRI-context alignment.

**Risks**

- No direct emotion labels.
- It can help context/language alignment, but it does not validate visual
  emotion representation.
- Affective pseudo-labeling from text may reflect language-model bias rather
  than participants' affective brain states.

**Sources**

- https://www.nature.com/articles/s41597-021-01033-3
- https://openneuro.org/datasets/ds002345

### 101 Dalmatians

**Role in NetFeeliX**

101 Dalmatians is useful for multimodal movie generalization and modality
control, especially if we want to test how visual-only, auditory-only, and
audiovisual conditions affect fMRI representations.

**Dataset content**

- fMRI during movie stimulus variants.
- Includes audiovisual, auditory, and visual conditions.
- Naturalistic movie structure is useful for multimodal encoding questions.

**NetFeeliX task design**

- Modality ablation for movie fMRI.
- Test whether SwiFT representations differ by sensory access.
- Compare stimulus-only audio/video embeddings against brain responses.

**SwiFT use**

- Auxiliary naturalistic fMRI transfer.
- Useful after core HCP/Horikawa/Emo-FilM experiments are running.

**TRIBE v2 / stimulus use**

- Good fit for TRIBE-style multimodal stimulus decomposition.

**Risks**

- Not emotion-labeled as a primary resource.
- Should not distract from core emotion tasks.

**Source**

- https://www.nature.com/articles/s41597-025-06077-3

## Context, Affect Trajectories, and Physiology

These resources are important for the later "context understanding" direction,
but they should not replace direct fMRI emotion benchmarks.

### REELMO

**Role in NetFeeliX**

REELMO is valuable for long-context affect trajectories. It provides much richer
movie-level affect reports than typical fMRI emotion datasets. Its fMRI subset
could be useful, but the immediate value is also as a stimulus-side target
source for context-aware models.

**Dataset content**

- 1,060 hours of moment-by-moment affective reports.
- 20 affective states.
- 60 full-length movies.
- 161 behavioral participants.
- Additional personality traits, empathy, movie synopses, and overall liking.
- fMRI subset: 20 volunteers watching Jojo Rabbit.

**NetFeeliX task design**

- Long-context affect trajectory prediction from movie features.
- MLLM/rationale/cue target generation and validation.
- Test whether short context vs long context improves affect prediction.
- If fMRI subset is accessible, compare context-aware stimulus latents to fMRI
  latents.

**SwiFT use**

- Only use the fMRI subset if access and format are practical.
- More likely to be a target/source for context-aware stimulus supervision than
  a core SwiFT fine-tuning dataset.

**TRIBE v2 / stimulus use**

- Strong fit for movie-level video/audio/text embeddings.
- Can provide stimulus-side affect trajectories that later align with fMRI
  latents in Emo-FilM or HCP.

**Risks**

- fMRI subset is much smaller than the behavioral dataset.
- Movie copyright/access issues may complicate feature extraction.
- Behavioral affect trajectories are not equivalent to subject-specific fMRI
  emotion experience.

**Sources**

- https://www.nature.com/articles/s41597-025-05159-6
- https://springernature.figshare.com/articles/dataset/Lights_Camera_Emotion_REELMO_s_1060_Hours_of_Affective_Reports_to_Explore_Emotions_in_Naturalistic_Contexts/28255745

### Spacetop

**Role in NetFeeliX**

Spacetop is a broad multimodal fMRI dataset. Its value for NetFeeliX is not
first-pass emotion decoding, but physiology-aware and interoceptive/affective
model expansion.

**Dataset content**

- 101 participants.
- Around 6 hours of scanning per participant.
- Includes naturalistic movie viewing, cognitive/affective/social/somatic tasks,
  structural MRI, diffusion MRI, and autonomic physiological data.
- Naturalistic video task includes ratings across affective domains such as
  happy, sad, afraid, disgusted, warm/tender, engaged, and personal relevance.

**NetFeeliX task design**

- Physiology-aware representation learning.
- Cross-task transfer between movie, social affect, pain/interoception, and
  narrative tasks.
- Auxiliary validation for whether emotion-specific SwiFT captures affective and
  bodily-state structure.

**SwiFT use**

- Later-stage multi-task or physiology-aware fine-tuning.
- Subject-level generalization and multi-condition robustness.

**TRIBE v2 / stimulus use**

- Use stimulus encoders for naturalistic video tasks where stimuli are available.

**Risks**

- Very broad scope.
- Can easily distract from the main two-month NetFeeliX goal.
- Target harmonization is nontrivial.

**Source**

- https://www.nature.com/articles/s41597-025-05154-x

## Static Image fMRI and Affective Image Labels

These are not the core movie-emotion path, but they can be useful if static
image affect transfer becomes strategically important.

### Natural Scenes Dataset

**Role in NetFeeliX**

NSD is not an emotion dataset. Its value is scale: it is a large, high-quality
7T fMRI dataset for natural image perception. NetFeeliX can use it for
static-image brain representation learning and then attach affective pseudo-
targets from OASIS, CLIP/VLM affect scoring, or image emotion models.

**Dataset content**

- 8 participants.
- 7T fMRI.
- 9,000-10,000 distinct color natural scenes per subject.
- 22,500-30,000 trials per subject.
- 30-40 weekly scan sessions.
- Whole-brain 1.8 mm resolution, 1.6 s TR.
- Additional resting-state, retinotopy, localizer, anatomical, physiological,
  eye-tracking, and behavioral data.

**NetFeeliX task design**

- Static-image fMRI representation learning.
- Image affect pseudo-label prediction.
- Compare brain-image latent geometry with CLIP/VLM affect dimensions.
- Use only as a branch if image-based affect transfer becomes useful.

**SwiFT use**

- Test whether 4D fMRI backbone can adapt to static-image trials.
- Use trial-level responses or beta estimates depending on available
  preprocessing.
- Potential bridge from visual representation to affective image response.

**TRIBE v2 / stimulus use**

- TRIBE v2 is video/audio/text-oriented; for NSD use image encoders instead.
- Possible pipeline: image -> CLIP/VLM affect embedding -> fMRI latent alignment.

**Risks**

- No native emotion labels.
- Visual cortex-heavy task may not transfer to affective brain systems.
- Pseudo-label quality determines usefulness.

**Sources**

- https://registry.opendata.aws/nsd/
- https://www.nature.com/articles/s41593-021-00962-x

### OASIS

**Role in NetFeeliX**

OASIS is not an fMRI dataset. It is an open affective image stimulus set that
can calibrate or validate image affect labels for NSD-like static image work.

**Dataset content**

- 900 open-access color images.
- Normative valence and arousal ratings.
- Ratings from 822 online participants.
- Images cover humans, animals, objects, and scenes.
- Useful because it avoids some copyright restrictions associated with IAPS.

**NetFeeliX task design**

- Calibrate image affect scoring models.
- Create affect pseudo-labels for NSD images or other image fMRI datasets.
- Validate whether VLM-derived valence/arousal scores match human norms.

**SwiFT use**

- Indirect only. OASIS has no brain data.

**TRIBE v2 / stimulus use**

- Not a TRIBE v2 use case; use static image encoders or VLMs.

**Risks**

- No fMRI.
- Two-dimensional affect labels are useful but limited.

**Source**

- https://link.springer.com/article/10.3758/s13428-016-0715-3

## Visual-Event Auxiliary Encoding

### BOLD Moments

**Role in NetFeeliX**

BOLD Moments is useful for dynamic visual-event representation, not primary
emotion learning. It can help test short-video fMRI encoding and stimulus
feature extraction.

**Dataset content**

- fMRI responses from 10 adults.
- 1,102 naturalistic 3-second videos.
- Videos include object, scene, action, sentence, and memorability annotations.

**NetFeeliX task design**

- Short-video stimulus-to-fMRI encoding.
- Compare event/action semantics with affective labels in Horikawa.
- Auxiliary pretraining for video-evoked fMRI representations if needed.

**SwiFT use**

- Dynamic visual-event representation test.
- Could help debug short-clip temporal pooling before Horikawa.

**TRIBE v2 / stimulus use**

- Good for short-video encoding comparison.

**Risks**

- Not emotion-specific.
- Should remain auxiliary.

**Source**

- https://www.nature.com/articles/s41467-024-50310-3

## Automation-Ready Dataset Fields

To avoid repeatedly rewriting this document by hand, every dataset should be
tracked with the same fields:

| Field | Meaning |
|---|---|
| `function` | emotion-labeled fMRI, movie pretraining, encoding/alignment, image affect, physiology/context |
| `brain_data` | raw 4D fMRI, beta maps, parcel time series, surface responses, or none |
| `stimulus` | videos, films, full movies, static images, narratives, multimodal clips |
| `emotion_target` | direct labels, continuous ratings, pseudo-labels, or none |
| `target_resolution` | trial, block, TR-level, second-level, film-level, subject-level |
| `swiFT_entry` | frozen probe, adapter, continued pretraining, beta-map adaptation, or indirect |
| `tribe_entry` | stimulus baseline, teacher, alignment, or not applicable |
| `first_experiment` | the first runnable experiment for this dataset |
| `main_risk` | access, preprocessing, label quality, sample size, or scope |
| `source` | paper/data/code URL |

The next automation step should be a small machine-readable registry that
renders this Markdown table and checks missing fields. That would prevent the
dataset inventory from becoming another manually maintained wall of text.

## Current Recommended Dataset Path

1. **Horikawa**: first high-dimensional affect geometry task.
2. **Emo-FilM**: first naturalistic component/appraisal task.
3. **HCP 7T movie**: first continued-pretraining source for SwiFT.
4. **Affective Videos + IAPS fMRI**: fast valence/arousal/category checks.
5. **TRIBE v2 with Horikawa/Emo-FilM/HCP stimuli**: stimulus baseline and
   teacher/alignment path.
6. **REELMO**: context/rationale/long-movie affect target source.
7. **NSD + OASIS**: static-image affect transfer branch only if useful.
