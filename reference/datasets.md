# NetFeeliX Dataset Reference

## HCP Young Adult 7T Movie Watching

- **Role**: primary naturalistic fMRI pretraining candidate.
- **Subjects**: 184 7T subjects in the release.
- **Runs**: four movie-watching runs, each about 15 minutes.
- **TR**: 1,000 ms.
- **Resolution**: 1.6 mm isotropic voxels for 7T fMRI.
- **Stimuli**: independent film and Hollywood movie excerpts concatenated into mp4 files.
- **Source**: https://www.humanconnectome.org/hcp-protocols-ya-7t-imaging

### Planned Use

- Start with parcellated time series to reduce compute.
- Pretrain small temporal transformer or JEPA-style encoder.
- Fine-tune on Horikawa and Emo-FilM.

## Horikawa / Cowen Emotional Video fMRI

- **Role**: core emotion downstream dataset.
- **Stimuli**: 2,185 emotion-evoking videos.
- **Annotations**: high-dimensional emotion category ratings from Cowen/Keltner-style emotion space.
- **Source**: https://www.sciencedirect.com/science/article/pii/S2589004220302455
- **Dataset noted in search**: https://openneuro.org/datasets/ds002425
- **Mendeley data mirror**: https://data.mendeley.com/datasets/jbk2r73mzh

### Planned Use

- Predict high-dimensional emotion vectors.
- Compare category vs valence/arousal targets if available.
- Use as main benchmark for whether HCP movie pretraining helps.

## Koide-Majima / Nakai / Nishimoto Emotional Movie fMRI

- **Role**: high-dimensional emotion representation benchmark.
- **Stimuli**: about 3 hours of emotion-inducing audiovisual movies.
- **Annotations**: 80 emotion labels at one-second scene level.
- **Finding**: around 25 distinct dimensions contributed to brain emotion representation.
- **Source**: https://pubmed.ncbi.nlm.nih.gov/32798681/

### Planned Use

- Secondary downstream dataset if data access is feasible.
- Useful for testing continuous high-dimensional emotion representation.

## Emo-FilM

- **Role**: modern naturalistic affective fMRI downstream dataset.
- **Subjects**: 30.
- **Stimuli**: 14 short films, combined duration over 2.5 hours.
- **Annotations**: 50 items, including discrete emotions, appraisals, motivation, motor expression, physiological response, and feeling.
- **Physiology**: heart rate, respiration, electrodermal activity.
- **Source**: https://www.nature.com/articles/s41597-025-04803-5

### Planned Use

- Moment-to-moment emotion prediction.
- Test whether physiological auxiliary targets help representation learning.

## REELMO

- **Role**: large-scale naturalistic affect annotation resource with fMRI subset.
- **Full name**: REal-time EmotionaL responses to MOvies.
- **Scale**: 1,060 hours of moment-by-moment emotional reports.
- **Participants**: 161 behavioral participants; fMRI data from 20 volunteers.
- **Stimuli**: 60 full-length movies for behavioral ratings; fMRI subset watched Jojo Rabbit over two one-hour sessions.
- **Annotations**: 20 affective states at 1-second resolution, plus personality traits, empathy, movie synopses, and overall liking.
- **Sources**:
  - https://www.nature.com/articles/s41597-025-05159-6
  - https://springernature.figshare.com/articles/dataset/Lights_Camera_Emotion_REELMO_s_1060_Hours_of_Affective_Reports_to_Explore_Emotions_in_Naturalistic_Contexts/28255745

### Planned Use

- High-value source for stimulus-side emotion trajectories.
- Potentially useful for pretraining or validating movie emotion targets.
- fMRI subset may support downstream testing, but access and format must be checked.

## Movie Datasets from Ke et al. 2025

- **Role**: dynamic FC baseline and cross-dataset arousal generalization reference.
- **Datasets**: Sherlock, Friday Night Lights, Merlin, North by Northwest.
- **Finding**: arousal generalized across datasets; valence did not show comparable generalizability.
- **Source**: https://pubmed.ncbi.nlm.nih.gov/40215238/
- **Code/data**: https://github.com/jinke828/AffectPrediction

### Planned Use

- Reproduce or adapt arousal CPM baseline.
- Use as a sanity check for arousal prediction before deep models.

## CNeuroMod / Algonauts 2025 Movie fMRI

- **Role**: auxiliary naturalistic encoding and multimodal alignment dataset.
- **Stimuli**: Friends sitcom seasons, feature films, documentary material.
- **Modalities**: movie visual frames, audio samples, and time-stamped language transcripts.
- **Brain data**: whole-brain fMRI responses from four CNeuroMod subjects for Algonauts 2025, represented as 1,000 functionally defined parcels.
- **Scale**: Algonauts 2025 uses almost 80 hours of multimodal movie stimuli and fMRI responses; training includes Friends seasons 1-6 plus films/documentary, with held-out Friends season 7 and OOD movies.
- **Sources**:
  - https://algonautsproject.com/2025/braindata.html
  - https://www.cneuromod.ca/gallery/datasets/

### Planned Use

- Reference implementation for TRIBE-style encoding.
- Possible auxiliary pretraining or validation dataset if access and compute are realistic.
- Useful for testing multimodal feature alignment before emotion-specific fine-tuning.

## BOLD Moments Dataset

- **Role**: auxiliary short-video fMRI dataset.
- **Subjects**: 10.
- **Stimuli**: 1,102 short 3-second naturalistic videos.
- **Annotations**: object, scene, action, sentence, and memorability metadata.
- **Source**: https://www.nature.com/articles/s41467-024-50310-3

### Planned Use

- Optional pretraining or sanity-check dataset for dynamic visual-event representation.
- Useful bridge between controlled short-video fMRI and longer movie fMRI.
- Not an emotion dataset, so it should not replace Horikawa or Emo-FilM.

## 101 Dalmatians Naturalistic fMRI

- **Role**: possible future multimodal naturalistic dataset.
- **Subjects**: 50 participants with typical development and congenital sensory loss.
- **Stimuli**: audiovisual, auditory, or visual versions of the live-action movie 101 Dalmatians.
- **Annotations/features**: auditory and visual descriptors, GPT-4 semantic embeddings, human-tagged movie events and content.
- **Source**: https://www.nature.com/articles/s41597-025-06077-3

### Planned Use

- Future generalization test for multimodal naturalistic representation learning.
- Not a first two-month priority.

## Spacetop

- **Role**: future naturalistic/physiology-rich expansion dataset.
- **Subjects**: 101.
- **Scale**: about 6 hours of scanning per participant.
- **Data**: 6 functional tasks, about 2 hours of naturalistic movie viewing, structural T1, diffusion imaging, and autonomic physiology.
- **Source**: https://www.nature.com/articles/s41597-025-05154-x

### Planned Use

- Future generalization or physiology-aware representation learning.
- Potential bridge between naturalistic processes and controlled task states.
- Not a first two-month priority unless data access and preprocessing are already straightforward.

## Affective Videos / OpenfMRI ds000205

- **Role**: older but directly affective fMRI dataset.
- **Subjects**: 11.
- **Stimuli**: 5-second dynamic naturalistic audiovisual clips.
- **Targets**: valence and arousal.
- **Source**: https://www.openfmri.org/dataset/ds000205/

### Planned Use

- Lightweight pilot dataset for valence/arousal decoding.
- Useful sanity check for old-school affective fMRI baselines.

## NeuroEmo / OpenNeuro ds005700

- **Role**: culturally grounded fMRI emotion-recognition dataset.
- **Subjects**: 40 healthy participants.
- **Stimuli**: Indian Bollywood movie clips.
- **Tasks**: resting-state and emotion-elicitation tasks.
- **Source**: https://github.com/OpenNeuroDatasets/ds005700

### Planned Use

- Potential downstream dataset for cross-cultural or culturally specific emotion generalization.
- Check OpenNeuro metadata, stimulus labels, and preprocessing burden before prioritizing.
