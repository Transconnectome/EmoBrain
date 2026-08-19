> ⚠️ **ARCHIVED — 역사 기록. 현행 문서가 아니다.**
> 현행 논증 = `docs/paper_logic_merged.md` (대전제 · RQ · 가설 H1–H4). 운영 규칙 = `CLAUDE.md`.
>
> 아래 내용 중 다음은 **뒤집혔다.** (a) Qwen3-VL 등 LLM backbone 사용 — 금지.
> (b) open-vocabulary / cross-taxonomy 전이를 headline novelty 로 삼는 프레임 — 폐기.
> (c) 학습에 없던 감정 zero-shot — 폐기(원칙적 분할 기준 없음, RQ 와 무관).
> (d) "EmoBrain 과 EmoViS 는 별도 논문 2편" — 현재는 **한 편의 논문**.
> (e) "EmoBrain 은 cortical location 을 주장하지 않는다" — 현재 **H3 이 cortical location 주장**이다.

# FEEL Code Resource Index

This is the canonical place for model/code details. For paper-level claims and
citations, see `reference/papers.md`. For dataset details, see
`reference/datasets.md`.

## Current BFM Benchmark Models

These are the only brain foundation models in the first `Dataset x BFM x Task`
benchmark matrix.

### SwiFT

- **Type**: Swin-style 4D fMRI transformer / fMRI encoder.
- **Input**: volumetric 4D fMRI windows.
- **Benchmark role**: primary BFM because it is the local Transconnectome
  backbone and can be modified after the benchmark.
- **First use**: frozen feature extraction followed by logistic/ridge/MLP heads
  for the Dataset x BFM x Task cells.
- **First checks**:
  - checkpoint native sequence length, e.g. SL20/SL40 if applicable,
  - input volume shape and preprocessing assumptions,
  - pooling choice: mean, late-frame, temporal/attention pooling,
  - padding/masking sensitivity.
- **Risks**:
  - mean pooling can erase temporal information,
  - short emotion trials may mismatch pretrained sequence length,
  - strong performance on arousal alone should not be overclaimed as rich
    emotion representation.
- **Source**: https://huggingface.co/papers/2307.05916

### Brain-JEPA

- **Type**: fMRI brain representation model using JEPA-style predictive latent
  learning.
- **Input**: fMRI/ROI time series, depending on the released implementation and
  preprocessing.
- **Benchmark role**: alternative BFM and objective precedent for latent
  prediction/spatiotemporal masking.
- **First use**: frozen feature probe under the same dataset/task/split cells as
  SwiFT where the input format can be matched.
- **First checks**:
  - exact expected ROI/time-series input,
  - whether the mask path is actually used in the implementation,
  - checkpoint and code availability,
  - feature shape and pooling.
- **Risks**:
  - may require a different preprocessing representation than 4D SwiFT,
  - matched split/target is mandatory before comparing with SwiFT.
- **Sources**:
  - https://neurips.cc/virtual/2024/poster/94113
  - https://huggingface.co/papers/2409.19407

### NeuroSTORM

- **Type**: large-scale raw 4D fMRI foundation model.
- **Input**: raw or preprocessed 4D fMRI volumes, depending on released code.
- **Benchmark role**: alternative 4D BFM for checking whether a larger/general
  4D model beats SwiFT under matched emotion tasks.
- **First use**: frozen feature probe if code/weights and preprocessing can be
  loaded locally.
- **First checks**:
  - code and checkpoint availability,
  - required spatial normalization and voxel grid,
  - window length and padding/pooling behavior,
  - GPU/memory feasibility.
- **Risks**:
  - may be too heavy or inaccessible for the first pass,
  - if input preprocessing differs too much, comparison with SwiFT may be
    confounded.
- **Source**: https://www.nature.com/articles/s41551-026-01666-y

### BrainLM

- **Type**: fMRI time-series foundation model with masked prediction.
- **Input**: ROI/time-series fMRI rather than raw 4D volumes.
- **Benchmark role**: alternative time-series BFM to test whether compact
  parcellated representations outperform 4D-volume encoders on emotion tasks.
- **First use**: frozen ROI/time-series feature probe with logistic/ridge/MLP
  heads.
- **First checks**:
  - expected atlas/parcellation,
  - checkpoint availability,
  - feature extraction API,
  - compatibility with Horikawa/Emo-FilM/Affective Videos time windows.
- **Risks**:
  - ROI representation may not be directly comparable to 4D volume models,
  - atlas mismatch can dominate model differences.
- **Source**: https://sciety.org/articles/activity/10.1101/2023.09.12.557460

## Not In First BFM Benchmark

### SwiFUN

- **Type**: resting-state fMRI to task activation prediction model.
- **Use later**: possible rest-to-task reference or architecture/code pattern.
- **Why excluded now**: it is not a direct Dataset x BFM x Emotion Task model for
  the first benchmark matrix.
- **URL**: https://github.com/Transconnectome/SwiFUN

### TRIBE v2

- **Type**: stimulus-to-brain model.
- **Use later**: video/audio/text stimulus control, predicted-brain teacher, or
  alignment component after the BFM benchmark.
- **Why excluded now**: it is not an fMRI-input brain foundation model.
- **URL**: https://github.com/facebookresearch/tribev2

## Additional / Later Repositories

### TRIBE / Algonauts 2025

- **URL**: https://github.com/facebookresearch/algonauts-2025
- **Use**: stimulus-to-brain encoding model training and evaluation.
- **First action**: inspect feature extraction pipeline, temporal transformer, and HRF/time-alignment assumptions.

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

All FEEL scripts should follow:

```text
studyN/code/script_name.py
studyN/code/script_name.sh
studyN/code/script_name.md
studyN/logs/
studyN/data/
studyN/results/
```

Use `project/shared/code/README.md` for shared utility plans, not for experiment output.
