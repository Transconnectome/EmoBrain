# EmoBrain Action Plan

## P0. Canonical Infrastructure

- [x] Qwen3-VL-4B-only backbone loader
- [x] Internal-padding compaction and safe readout token selection
- [x] E1 ViT / E2 BFM registry
- [x] Remove target-space encoder from the active pipeline
- [x] Correct `log1p_z` inverse metrics
- [x] Corrected Brain-JEPA provenance importer
- [x] Isolate Qwen2.5 implementation under `project/legacy/`

## P1. Direct Decoding

- [ ] Import corrected Brain-JEPA embeddings
- [ ] Run E1 ViT direct student
- [ ] Run E2 corrected Brain-JEPA direct student
- [ ] Run E2 SwiFT direct student
- [ ] Compare three seeds on stimulus-held-out test

## P2. Core Distillation

- [x] Teacher checkpointing and test reporting
- [x] Provenance-aware teacher soft-label cache
- [x] Brain-only student hard + distillation MSE
- [x] One-command teacher -> cache -> student launcher
- [ ] Run the E2 Brain-JEPA distillation workflow

## P3. Student-Side Ablations

- [ ] Hard-only vs distilled student with identical initialization and seed
- [ ] Context-only teacher and brain-shuffled student checks
- [ ] Video-only, caption-only, and video+caption teacher comparisons
- [ ] Caption affect-language sensitivity analysis
- [ ] Projector type and token-count sensitivity

## P4. Neuroscience

- [ ] Per-emotion transfer and distillation gain maps
- [ ] Cortical/network contribution analysis
- [ ] Visual/semantic controls and variance partitioning at the prediction level
- [ ] Short-window length and padding sensitivity
- [ ] Cross-subject and future cross-dataset generalization
