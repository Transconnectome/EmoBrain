# NetFeeliX Code Resource Index

## Core Repositories

### SwiFUN

- **URL**: https://github.com/Transconnectome/SwiFUN
- **Use**: resting-state fMRI to task activation prediction, with SwiFT/Swin UNETR code patterns.
- **First action**: inspect data loader assumptions and pretrained checkpoint availability.

### TRIBE / Algonauts 2025

- **URL**: https://github.com/facebookresearch/algonauts-2025
- **Use**: stimulus-to-brain encoding model training and evaluation.
- **First action**: inspect feature extraction pipeline, temporal transformer, and HRF/time-alignment assumptions.

### TRIBE v2

- **URL**: https://github.com/facebookresearch/tribev2
- **Use**: latest multimodal stimulus-to-brain alignment reference.
- **First action**: verify whether weights, inference examples, and academic license constraints are usable.

### Brain-DiT

- **URL**: https://github.com/REDMAO4869/Brain-DiT
- **Use**: metadata-conditioned diffusion-transformer fMRI foundation-model reference.
- **First action**: inspect whether released parameters and preprocessing scripts are usable as a future BFM baseline.

### AffectPrediction

- **URL**: https://github.com/jinke828/AffectPrediction
- **Use**: dynamic FC arousal/valence prediction baseline from Ke et al. 2025.
- **First action**: check expected input format and reproduce on provided data before adapting.

## Candidate Model Dependencies

### Video features

- V-JEPA2 for video representation.
  - Source: https://ai.meta.com/research/publications/v-jepa-2-self-supervised-video-models-enable-understanding-prediction-and-planning/
- VideoMAE for alternative video SSL baseline.
- CLIP visual encoder for static frame semantic baseline.

### Audio features

- Wav2Vec-BERT or Wav2Vec2.
- Whisper embeddings if easier locally.
- Spectrogram baseline for low-level audio.

### Text features

- LLaMA-style contextual embeddings where available.
- Sentence-transformer caption embeddings for lightweight baseline.

## Brain-Aligned AI and Affective FM Resources

### Brain-Score Vision

- **URL**: https://github.com/brain-score/vision
- **Use**: conceptual and software reference for scoring model-brain-behavior alignment.
- **First action**: inspect benchmark interface patterns before designing affective brain-score style evaluation.

### Brain-Score Language

- **URL**: https://github.com/brain-score/language
- **Use**: reference for comparing language models with neural/behavioral data.
- **First action**: inspect how model activations and neural benchmarks are wrapped.

### REVE

- **URL**: https://brain-bzh.github.io/reve/
- **Use**: EEG foundation-model precedent with emotion downstream tasks.
- **First action**: check whether code/weights are public and whether any design ideas transfer to fMRI/physiology extensions.

### Affective LLM/VLM Benchmarks

- **AffectGPT**: https://github.com/zeroQiaoba/AffectGPT
- **AVERE / EmoReAlM**: https://avere-iclr.github.io/
- **MMAFFBen**: https://huggingface.co/papers/2505.24423
- **MMAFFBen code**: https://github.com/lzw108/MMAFFBen
- **MME-Emotion**: https://mme-emotion.github.io/
- **VidEmo**: https://openreview.net/forum?id=x8lg9aihwl
- **EmotionHallucer**: https://openreview.net/forum?id=ahWmeQG3K2
- **HitEmotion / ToM-guided reasoning**: https://openreview.net/forum?id=8VSrk2CaBr
- **EmoBench-M**: https://huggingface.co/papers/2502.04424
- **Beyond Emotion Recognition**: https://huggingface.co/papers/2508.16859
- **EIBench / Why We Feel**: https://cvpr.thecvf.com/virtual/2025/35814
- **LLM affect survey**: https://huggingface.co/papers/2408.04638
- **MLLM emotion reasoning survey**: https://huggingface.co/papers/2509.24322
- **Use**: external affective representation sources and evaluation inspiration.
- **First action**: identify lightweight embeddings, caption/rationale generators, or API-free models that can be used as frozen stimulus-side features; separately track hallucination/cue-grounding diagnostics.

## Local Code Policy

All NetFeeliX scripts should follow:

```text
studyN/code/script_name.py
studyN/code/script_name.sh
studyN/code/script_name.md
studyN/logs/
studyN/data/
studyN/results/
```

Use `code/README.md` for shared utility plans, not for experiment output.
