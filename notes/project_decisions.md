# NetFeeliX Project Decisions

## 2026-05-08

### Project Name

Confirmed working name: **NetFeeliX**.

Formal subtitle:

**A Naturalistic fMRI Foundation Model for Emotion Representation Learning**

### Core Direction

NetFeeliX will compare:

1. Existing BFM transfer.
2. HCP movie-watching pretraining.
3. TRIBE-style stimulus-brain-emotion alignment.

### Important Clarification

TRIBE is an encoding model: stimulus to fMRI response. It should not be described as the same kind of model as SwiFT, BrainLM, Brain-JEPA, or NeuroSTORM.

### Two-Month Constraint

The project has roughly two months. Therefore:

- Start with baselines and frozen probes.
- Use parcellated or compact time-series data before raw 4D volume training.
- Treat expensive end-to-end 4D training as optional, not the first milestone.
- Keep all results comparable through shared splits and metrics.

### First Study

`study1` should focus on:

- dataset inventory,
- target construction,
- simple baselines,
- pretrained model availability,
- deciding which downstream target is most stable.

