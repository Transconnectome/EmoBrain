# NetFeeliX

**Neural nETwork For Emotion rEpresentation Learning and Inference in NeuroX**

> Emotion representation learning with brain foundation models and naturalistic fMRI.

NetFeeliX studies how to learn emotion-aware brain representations from naturalistic fMRI, with a focus on movie-watching data, brain foundation models, and stimulus-brain-emotion alignment.

---

## Project Thesis

Emotion representation is unlikely to be solved by attaching a small emotion head to a generic resting-state brain foundation model. Emotion during naturalistic experience depends on the interaction between multimodal stimulus dynamics, subject-specific brain dynamics, and affective labels or ratings. NetFeeliX therefore treats emotion representation learning as a three-way alignment problem:

```text
naturalistic stimulus dynamics + fMRI brain dynamics + emotion annotations
```

The project compares three families of approaches:

1. **Existing fMRI foundation models.** Fine-tune or probe pretrained models such as SwiFT, BrainLM, Brain-JEPA, and NeuroSTORM on emotion prediction.
2. **Naturalistic movie pretraining.** Pretrain from HCP 7T movie-watching fMRI, then fine-tune on Horikawa, Emo-FilM, and related affective movie datasets.
3. **Stimulus-brain-emotion alignment.** Extend the TRIBE-style encoding idea into an emotion-aware representation model by aligning video/audio/text encoders with fMRI responses and emotion labels.

## Core Research Question

**What model architecture and learning objective best support transferable emotion representation learning from naturalistic fMRI?**

Subquestions:

- Do resting-state fMRI foundation models transfer to emotion prediction, or do they miss naturalistic affective dynamics?
- Does HCP movie-watching pretraining improve sample efficiency and generalization on small emotion fMRI datasets?
- Are emotion labels better predicted from brain-only representations, stimulus-only representations, or jointly aligned stimulus-brain representations?
- Which downstream targets are more transferable: arousal, valence, discrete emotion categories, or high-dimensional emotion embeddings?

## Working Hypotheses

**H1. Resting-state BFM transfer is useful but incomplete.** Existing brain foundation models should provide nontrivial baselines, but their pretraining distribution may underrepresent stimulus-locked affective dynamics.

**H2. Naturalistic movie pretraining should improve emotion transfer.** HCP movie-watching fMRI should provide a better pretraining domain for Horikawa and Emo-FilM than resting-state-only pretraining.

**H3. Arousal will generalize more robustly than valence.** This follows recent movie-watching fMRI evidence that dynamic connectivity predicts arousal across datasets more reliably than valence.

**H4. Stimulus-brain alignment should be necessary for high-dimensional emotion.** TRIBE-style multimodal encoders can capture semantic, audio, and visual context that brain-only BFM objectives may not learn from small downstream datasets.

## Key Model Families

| Family | Examples | Input | Output | Role in NetFeeliX |
|---|---|---|---|---|
| 4D fMRI backbone | SwiFT | fMRI volumes | task label or representation | Baseline fMRI encoder |
| Resting-to-task prediction | SwiFUN | resting-state fMRI | task activation map | Bridge from intrinsic dynamics to emotion reactivity |
| fMRI foundation model | BrainLM, Brain-JEPA, NeuroSTORM, Omni-fMRI | fMRI time series or 4D fMRI | transferable brain representation | Existing pretrained BFM baseline |
| Brain encoding model | TRIBE, TRIBE v2 | video/audio/text stimulus | predicted fMRI response | Stimulus-to-brain comparison and alignment target |
| NetFeeliX | proposed | fMRI + optional stimulus features | emotion-aware brain representation | Project target |

## Immediate Two-Month Strategy

1. **Weeks 1-2: Baselines and data readiness**
   - Confirm access and preprocessing for HCP 7T movie, Horikawa, Emo-FilM, and available local fMRI assets.
   - Run simple baselines: ridge/MLP on ROI time series, dynamic FC arousal baseline, frozen BFM linear probes.
   - Record exact splits, target definitions, and metrics.

2. **Weeks 3-4: HCP movie pretraining**
   - Start with a small ROI or parcel-level temporal transformer.
   - Compare masked modeling, temporal contrastive learning, and JEPA-style latent prediction.
   - Track compute, convergence, and transfer quality.

3. **Weeks 5-6: Emotion fine-tuning**
   - Fine-tune or probe on Horikawa and Emo-FilM.
   - Compare arousal, valence, discrete emotions, and embedding targets.
   - Add subject adapters and HRF-aware temporal lag modules if baselines justify them.

4. **Weeks 7-8: Alignment and ablation**
   - Add V-JEPA2, Wav2Vec-BERT or Whisper, and text/caption features where possible.
   - Compare brain-only, stimulus-only, and stimulus-brain aligned models.
   - Prepare paper-style tables, failure analysis, and next-step proposal.

## Repository Structure

```text
NetFeeliX/
├── README.md
├── CLAUDE.md
├── CODEX.md
├── Paper/
│   ├── framework_EN.md
│   ├── framework_KR.md
│   └── methodology.md
├── reference/
│   ├── systematic_reference_map.md
│   ├── papers.md
│   ├── datasets.md
│   ├── code_resources.md
│   └── search_log_2026-05-08.md
├── notes/
│   ├── project_decisions.md
│   └── two_month_plan.md
├── code/
│   └── README.md
└── study1/
    ├── code/
    ├── data/
    ├── logs/
    └── results/
```

## Current Planning Documents

- `Paper/framework_EN.md` and `Paper/framework_KR.md`: canonical project framework, narrative, and proposal-level framing.
- `Paper/methodology.md`: detailed experimental plan.
- `reference/systematic_reference_map.md`: organized reference map by conceptual role.
- `notes/pilot_benchmark_design.md`: pilot benchmark axes, experiments, and decision rules.
