# EmoBrain Methodology

## Data

Five-subject Horikawa task-fMRI responses are aligned to 2,185 videos. Train,
validation, and test are disjoint at the stimulus level. Each target is a vector
of 34 independent Cowen emotion endorsement proportions. Targets are transformed
with `log1p` and standardized using training-stimulus statistics only.

## Encoders

- E1 ViT maps the 450-ROI response to a fixed 22x22 grid and adapts a pretrained
  ViT with LoRA.
- E2 BFM consumes frozen Brain-JEPA or SwiFT embeddings. Corrected Brain-JEPA
  uses the native one-patch fixed sinusoidal position code and is interpreted as
  short-window transfer.

Both return an embedding sequence projected into Qwen3-VL-4B token space. They
are evaluated as separate conditions, not concatenated branches.

## Direct Decoding

Brain tokens and a fixed question are processed by Qwen3-VL-4B. The base model
is frozen; LoRA, projector, segment markers, and linear 34D head are trained with
independent MSE. Validation profile Pearson selects a checkpoint, which is then
evaluated on the untouched test stimuli.

## Context Teacher and Distillation

The teacher receives brain tokens, V-JEPA2 video tokens, one human-written
MindCaptioning description, and the fixed question. Its raw 34D outputs are
cached for train/val with checkpoint and source provenance. A brain-only student
minimizes hard-label MSE plus MSE to the cached teacher outputs.

## Evaluation and Analysis

Primary metrics are per-stimulus 34D Pearson and CCC. Supporting metrics include
per-emotion correlation, MSE/R2, RSA, and sparse top-k agreement. Planned
analyses quantify pretrained-versus-scratch transfer, valid-window sensitivity,
cortical-network contributions, visual/semantic controls, cross-subject transfer,
and future cross-dataset generalization.
