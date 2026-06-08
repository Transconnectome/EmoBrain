# FEEL Phase 2. Trained fusion benchmark

4 fusion architectures × 4 V/A tasks, trained on frozen brain + frozen video features.
Same 5-fold stim-stratified CV protocol as Phase 1.

## Architectures

| ID | Name | Structure | Trainable | Seeds |
|---|---|---|---|---|
| **D** | Late fusion | concat(brain, video) → sklearn Logistic/Ridge | ~K params | 1 (deterministic) |
| **A** | Token transformer | [brain, video] tokens → 2-layer Transformer encoder → CLS → linear | ~600K | 3 |
| **B** | Cross-attention | bidirectional cross-attn (brain↔video) → pool → linear | ~400K | 3 |
| **C** | Contrastive (2-stage) | Stage 1: brain_proj + video_proj with InfoNCE. Stage 2: linear probe on (i) brain_proj only or (ii) concat(brain_proj, video_proj). | ~400K | 3 |

D uses sklearn (LogisticRegression / Ridge) directly to match Phase 1 frozen-probe convention.
A/B/C use PyTorch + AdamW + early stopping (val-fold-based).

## Default input

- Brain: **Brain-JEPA** (`brain_jepa_resting_pad-zero`, Phase 1 frozen probe best BFM)
- Video: **CLIP_pretrained** (Phase 1 video best)

Override via `--brain_model`, `--brain_init`, `--brain_padding`, `--video` args.

## Tasks (V/A only; Dim14 omitted per scope)

- V_binary, A_binary (logistic regression, AUROC main metric)
- V_reg, A_reg (ridge regression, Pearson r main metric)

Pooled mode (5 subjects merged). Phase 1 default. Per-subject not used in Phase 2 v1.

## Critical fix: video feature alignment

The original `project/shared/data/stimulus_features/stim_idx.npy` is **0-indexed (0..2184)**, but label CSVs
use stimulus_num **1-indexed (1..2185)**. Phase 2 `_lib.load_video_feature` IGNORES stim_idx.npy
and uses `np.arange(1, N+1)` to match Phase 1 video probe convention (off-by-one fix applied
2026-05-30).

## File map

```
project/dir2_multimodal/code/legacy_phase2/
├── README.md
├── _lib.py                          ← Brain/video loader, fold split, metrics
├── architectures/
│   ├── arch_D_late_fusion.py
│   ├── arch_A_token_transformer.py
│   ├── arch_B_cross_attention.py
│   └── arch_C_contrastive.py
├── train_supervised.py              ← D/A/B trainer (sklearn for D, PyTorch for A/B)
├── train_contrastive.py             ← C Stage 1
├── probe_contrastive.py             ← C Stage 2
├── encoding_brain_to_video.py       ← Direction 2 (brain → video feature prediction)
├── subject_variability.py           ← Direction 4 (skeleton, post-hoc)
├── _diag_D.py                       ← bug-finding script (kept for reference)
└── wrappers/
    ├── D/<task>.sh                  ← D-V_binary, D-A_binary, D-V_reg, D-A_reg
    ├── A/<task>.sh
    ├── B/<task>.sh
    ├── C/stage1_align.sh
    ├── C/probe_brain_only/<task>.sh
    ├── C/probe_joint/<task>.sh
    └── encoding/<video>.sh
```

## Run order

### 1. Supervised architectures (D, A, B). parallel across tasks

```bash
# D (sklearn, ~5s/fold, 5 folds × 1 seed = 5 runs)
bash project/dir2_multimodal/code/legacy_phase2/wrappers/D/V_binary.sh
bash project/dir2_multimodal/code/legacy_phase2/wrappers/D/A_binary.sh
bash project/dir2_multimodal/code/legacy_phase2/wrappers/D/V_reg.sh
bash project/dir2_multimodal/code/legacy_phase2/wrappers/D/A_reg.sh

# A (PyTorch, ~20-50s/fold/seed, 5 folds × 3 seeds = 15 runs)
bash project/dir2_multimodal/code/legacy_phase2/wrappers/A/V_binary.sh
bash project/dir2_multimodal/code/legacy_phase2/wrappers/A/A_binary.sh
bash project/dir2_multimodal/code/legacy_phase2/wrappers/A/V_reg.sh
bash project/dir2_multimodal/code/legacy_phase2/wrappers/A/A_reg.sh

# B (PyTorch, ~15-30s/fold/seed)
bash project/dir2_multimodal/code/legacy_phase2/wrappers/B/V_binary.sh
bash project/dir2_multimodal/code/legacy_phase2/wrappers/B/A_binary.sh
bash project/dir2_multimodal/code/legacy_phase2/wrappers/B/V_reg.sh
bash project/dir2_multimodal/code/legacy_phase2/wrappers/B/A_reg.sh
```

### 2. Architecture C (contrastive). 2 stages

```bash
# Stage 1: align (5 folds × 3 seeds = 15 aligner ckpts, ~8s each)
bash project/dir2_multimodal/code/legacy_phase2/wrappers/C/stage1_align.sh

# Stage 2: linear probe (after Stage 1 ckpts exist)
bash project/dir2_multimodal/code/legacy_phase2/wrappers/C/probe_brain_only/V_binary.sh
bash project/dir2_multimodal/code/legacy_phase2/wrappers/C/probe_brain_only/A_binary.sh
bash project/dir2_multimodal/code/legacy_phase2/wrappers/C/probe_brain_only/V_reg.sh
bash project/dir2_multimodal/code/legacy_phase2/wrappers/C/probe_brain_only/A_reg.sh
bash project/dir2_multimodal/code/legacy_phase2/wrappers/C/probe_joint/V_binary.sh
bash project/dir2_multimodal/code/legacy_phase2/wrappers/C/probe_joint/A_binary.sh
bash project/dir2_multimodal/code/legacy_phase2/wrappers/C/probe_joint/V_reg.sh
bash project/dir2_multimodal/code/legacy_phase2/wrappers/C/probe_joint/A_reg.sh
```

### 3. Direction 2 (encoding)

```bash
bash project/dir2_multimodal/code/legacy_phase2/wrappers/encoding/clip_pretrained.sh
bash project/dir2_multimodal/code/legacy_phase2/wrappers/encoding/vjepa2_pretrained.sh
bash project/dir2_multimodal/code/legacy_phase2/wrappers/encoding/dinov2_pretrained.sh
```

### 4. Total

- D: 4 cmds (1 seed × 5 folds × 4 task = 20 fits, total <1 min CPU)
- A: 4 cmds (3 seed × 5 folds × 4 task = 60 fits, total ~30 min GPU)
- B: 4 cmds (60 fits, total ~20 min GPU)
- C: 1 stage1 cmd + 8 probe cmds (~5 min GPU + ~30s probe)
- Encoding: 3 cmds (5 folds × 3 video = 15 fits, ~5 min)

**Estimated total: 1 hour on 1 GPU node** (or much less if all parallel).

## Smoke test results (V_binary fold 1, seed 0)

| Arch | AUROC | Reference |
|---|---|---|
| D late fusion (BJ+CLIP) | 0.9829 | CLIP alone Phase 1 = 0.9816 |
| A token transformer | 0.9817 | (essentially same as D) |
| B cross-attention | 0.9683 | (slightly lower; small N for attention) |
| C-stage1 + brain-only probe | 0.6905 | (brain alone via contrastive proj) |
| C-stage1 + joint probe | 0.9616 | (close to CLIP alone) |

**Observation**: On V_binary, video signal dominates and brain adds essentially nothing
on top (D BJ+CLIP 0.9829 vs CLIP-alone Phase 1 0.9816. within seed noise). This is
consistent with the Phase 1 hypothesis that crowd-sourced V/A labels are video-attributable
and the brain's added value should be measured on subject-specific targets, not group
labels.

Full V/A benchmark will quantify this across all 4 tasks × 4 architectures.

## Output

- `project/shared/results/phase2/D/<task>.csv`. D late fusion per-fold rows
- `project/shared/results/phase2/A/<task>.csv`. A token transformer
- `project/shared/results/phase2/B/<task>.csv`. B cross-attention
- `project/shared/results/phase2/C/aligner_fold<K>_seed<S>.pt`. C Stage 1 ckpts
- `project/shared/results/phase2/C/probe_brain_only_<task>.csv`. C Stage 2 (brain-only probe)
- `project/shared/results/phase2/C/probe_joint_<task>.csv`. C Stage 2 (joint probe)
- `project/shared/results/phase2/encoding/<video>__<brain>.csv`. Direction 2 encoding

Schema matches Phase 1 frozen probe CSV → existing `_summary_helper.py` and analysis
scripts work directly.
