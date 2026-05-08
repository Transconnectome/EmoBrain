# NetFeeliX Two-Month Plan

## Goal

Produce a credible research package showing whether emotion-aware brain representations benefit from naturalistic movie pretraining and stimulus-brain alignment beyond generic resting-state BFM transfer.

## Week 1

- Confirm local data availability.
- Build dataset inventory table.
- Define target variables for Horikawa and Emo-FilM.
- Confirm evaluation splits.
- Reproduce one simple baseline.

## Week 2

- Run ridge/MLP baselines.
- Run dynamic FC arousal baseline if possible.
- Check pretrained model availability for BrainLM, Brain-JEPA, SwiFT, NeuroSTORM.
- Produce baseline table v0.

## Week 3

- Build HCP movie pretraining dataloader.
- Start parcel-level temporal transformer.
- Implement masked modeling objective.
- Save first pretraining checkpoints.

## Week 4

- Add temporal contrastive or JEPA-style latent prediction.
- Compare pretraining objectives on downstream frozen probe.
- Select best pretraining variant for deeper fine-tuning.

## Week 5

- Fine-tune on Horikawa.
- Compare arousal/valence/category/high-dimensional targets.
- Add subject embedding or adapter if needed.

## Week 6

- Fine-tune on Emo-FilM.
- Evaluate cross-dataset generalization where possible.
- Prepare model comparison table.

## Week 7

- Add stimulus features: video first, then audio/text if feasible.
- Implement simple aligned latent baseline.
- Compare brain-only vs stimulus-only vs aligned.

## Week 8

- Run ablations.
- Write results summary.
- Prepare paper/proposal framing.
- Identify failure modes and next experiments.

## Minimum Successful Outcome

- A clean literature map.
- A reproducible baseline table.
- At least one pretrained BFM probe.
- One HCP movie pretraining run.
- One emotion downstream comparison.

## Strong Outcome

- HCP movie-pretrained model beats generic BFM frozen probe on at least one emotion target.
- Arousal generalizes better than valence, matching prior literature.
- Stimulus-brain alignment improves high-dimensional emotion representation or provides a clear failure analysis.

