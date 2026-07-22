# Reproducing EmoBrain from raw fMRI

End-to-end path from Horikawa raw BOLD to a trained emotion decoder. Each step
says whether the code is **in this repo** or an **external prerequisite**, with
its provenance, so someone cloning the repo can retrace it.

Convention. `[REPO]` = runnable from this repository. `[EXTERNAL]` = lives
outside the repo (another codebase, checkpoint download, or a preprocessing tree
kept locally because of size). External artifacts are gitignored on purpose
(`*.pt`, `*.npy`, `*.nii*`, `external/`, `project/shared/output/`).

```
raw BOLD ─[EXTERNAL parcellation]─▶ ROI csv ─[REPO]─▶ roi_timeseries.pt ─┐
        └─[EXTERNAL MNI prep]──────▶ MNI volumes ─────────────────────────┤
                                                                          ├─[REPO extraction + EXTERNAL model]─▶ BFM embeddings
labels + splits + norm stats ─[REPO]──────────────────────────────────────┘
                                                                          ▼
                                              [REPO] Track A / Track B training ─▶ 34D emotion decoder
```

---

## 0. External prerequisites (obtain first)

| Item | What | Provenance | Note |
|------|------|-----------|------|
| Raw fMRI | Horikawa 2020 naturalistic-video emotion fMRI, 5 subjects | Horikawa & Kamitani release | 2185 unique stimuli + 11 repeats = 2196 presentations |
| Parcellation output | Per-stimulus Schaefer-400 + Tian-S3-50 ROI time-series `csv.gz` | `horikawa_parcellation.py` (in `Horikawa_embedding/horikawa_preprocess_JEPA_ROI/`, **not in this repo**) | uses Schaefer2018 400p 17-net + Tian S3 atlases (the `.nii.gz` atlases are under `external/Brain-JEPA/atlas/`) |
| MNI volumes | 96^3 x 20 TR MNI-space volumes for volume BFMs | `Horikawa_embedding/horikawa_filtered_MNI_to_TRs/` (**not in this repo**) | z-scored variant also at `/pscratch/sd/t/tylee/Horikawa_Haka/img/` (standard NIfTI) |
| BFM model code | Brain-JEPA / NeuroSTORM / SwiFT-v2 | see below | vendored under `external/` locally but **gitignored** (third-party licenses); link as submodules to reproduce |
| BFM checkpoints | pretrained weights | `external/checkpoints/{brain_jepa,neurostorm}/`; SwiFT weights via SwiFT-v2 | gitignored (size). Record the exact download source when adding a model |

**Model repositories (link as git submodules; do not vendor, license).**
- SwiFT-v2 = `https://github.com/Transconnectome/SwiFT_v2` (known)
- Brain-JEPA = upstream URL TODO (local copy has no git metadata; confirm the fork before submoduling)
- NeuroSTORM = upstream URL TODO (same)

Already submoduled (`.gitmodules`): BrainVLM, fMRI-LM.

---

## 1. Preprocessing to ROI time-series `[REPO]`

Reads the external parcellation `csv.gz` and packs per-subject tensors.

```bash
bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/build_roi_timeseries.sh
# in: Horikawa_embedding/.../time_series/sub-XX/stimulus_N/{Schaefer17n400p,Tian_S3}.csv.gz
# out: project/shared/data/roi_timeseries/sub-XX.pt
#      { roi_timeseries (2185,T,450), roi_mean (2185,450), mask, original_T, stim_num }
```

Optional volume format for BrainVLM-style input `[REPO]`.
```bash
python3 project/shared/code/brainvlm/convert_horikawa_fmri.py --padding zero --T_target 20
# out: output/brainvlm_fmri/<padding>/sub-XX/stimulus_N.pt  (1,1,96,96,96,20)
```

## 2. Labels, splits, normalization `[REPO]`

```bash
# canonical 2185 stimulus split (clip-level, no leakage)
python3 project/shared/code/build_canonical_split.py     # -> horikawa_split.csv, horikawa_5fold.csv
# 34D crowd-proportion labels + per-emotion log1p_z stats (TRAIN only)
#   labels live in project/shared/data/cowen_horikawa_labels.csv (34 = Appendix A order)
#   normalizer stats: project/shared/data/norm_stats/cowen34_train.pt  (mode=log1p_z, canonical)
# ridge encoder for the E2/baseline slot
python3 project/scripts/fit_ridge_encoder.py             # -> project/shared/data/ridge_encoder.pt
```

## 3. BFM embedding extraction `[REPO code + EXTERNAL model]`

Each `_lib/*.py` injects the model repo on `sys.path`, loads the checkpoint, runs
the forward, and writes `output/embeddings/<variant>/sub-XX.pt` = `{embeddings
(2185,dim), stim_num}`. Requires the model repo + checkpoint from step 0.

```bash
# single (init x padding x subject)
python3 project/shared/code/bfm_embeddings/_lib/brain_jepa.py \
    --init resting --padding zero --subject sub-01 --device cuda
# -> output/embeddings/brain_jepa_resting_pad-zero/sub-01.pt

# full sweep (all init x padding x subject) per model
bash project/shared/code/bfm_embeddings/run_full/brain_jepa.sh
bash project/shared/code/bfm_embeddings/run_full/swift_NewE96_SL20.sh
bash project/shared/code/bfm_embeddings/run_full/neurostorm.sh
```

Brain-JEPA is ROI-based (450 parcels, reads step-1 output). SwiFT / NeuroSTORM
are whole-brain volume (96^3, read step-0 MNI volumes). Settings per model are in
`_lib/SETTINGS_*.md`.

ROI-mean baseline feature (no model needed) `[REPO]`.
```bash
bash project/shared/code/probes/extract_roi_features.sh
# -> output/embeddings/roi_schaefer400tian50_mean/sub-XX.pt
```

## 4. Training `[REPO]`

Config-driven; swapping the brain encoder is one config line. GPU (Qwen3-VL-4B).

```bash
export HF_HOME=/pscratch/sd/s/sjmoon/hf_cache      # predownload Qwen3-VL / ViT on a login node

# Track A (direct supervised, brain-only student)
bash project/code/training/trainer.sh project/code/configs/ridge_student_qwen.yaml
bash project/code/training/trainer.sh project/code/configs/vit_lora_student_qwen.yaml
bash project/code/training/trainer.sh project/code/configs/bfm_jepa_student_qwen.yaml

# Track B (offline distillation): teacher -> cache soft labels -> student
bash project/code/training/train_teacher.sh        project/code/configs/ridge_teacher_qwen.yaml
bash project/code/training/cache_soft_labels.sh    project/code/configs/ridge_teacher_qwen.yaml
bash project/code/training/train_student_distill.sh project/code/configs/ridge_student_distill_qwen.yaml
```

Encoder axis (`encoder.type`) = `ridge` | `vit` | `bfm` (`model: brain_jepa|swift`).
Adapt axis (`encoder.adapt`) = `frozen` (linear probe on precomputed embedding) |
`lora` | `full`. BFM `lora/full` (in-loop fine-tune) is not wired yet; frozen works.
Loss (`loss.hard_kind`) = `mse` | `huber` | `ccc` | `mse+ccc`.

## 5. Evaluation and analyses `[REPO]`

```bash
# Stage 0 decoding noise ceiling (R0 gate)
bash project/scripts/stage0_decoding_ceiling.sh
# representation comparison (why a BFM vs ridge)
bash project/scripts/loso_matched_retention.sh all
# spatial resolution ladder (needs the tylee NIfTI volumes)
bash project/scripts/spatial_resolution_ladder.sh sub-01
# data QC
bash project/scripts/qc_horikawa_data.sh
```

Headline metric = per-clip 34D profile Pearson + CCC (`project/evaluation/metrics.py`).
Baselines: chance, ROI-mean + ridge (pooled ~0.294), frozen-BFM reference.

---

## Known gaps (reproducibility TODO)

1. **Raw -> ROI parcellation** (`horikawa_parcellation.py`) and **raw -> MNI
   volume** prep live in `Horikawa_embedding/`, outside this repo. Bring copies
   (or a thin driver) into `project/shared/code/preprocess/` to close the chain
   from raw BOLD.
2. **Model repos** Brain-JEPA / NeuroSTORM upstream URLs to confirm, then add as
   submodules (SwiFT-v2 URL is known).
3. **Checkpoint sources** to record per model (currently local only).
4. **BFM in-loop fine-tune** not implemented (frozen extraction only).
5. **Brain-JEPA is used far below its design temporal length.** It was
   pretrained on ~160 TR (10 time patches); our stimuli are ~6 TR (1 patch), so
   `_lib/brain_jepa.py::load_pretrained` averages the checkpoint's temporal
   position embedding across the 10 patches. Measured: `emb_h` (4500,384) is a
   period-10 temporal embedding replicated across all 450 ROIs (no ROI info), so
   the averaging is a small shared-bias effect, NOT destruction of the gradient
   positioning. The real limitation is that 6 TR wastes Brain-JEPA's long-sequence
   design; its frozen underperformance is mostly the ROI ceiling + resting-vs-task
   domain gap, not this surgery (see project_decisions 2026-07-21 (2), severity
   downgraded). SwiFT / NeuroSTORM match their SL20 pretraining and need no such
   surgery. Also the hardcoded `CHECKPOINT` path is stale (`baseline/...` vs
   actual `external/checkpoints/...`).
