# Horikawa D2 fMRI-LM Adapter

Converts Horikawa naturalistic-video ROI time-series csvs into the official
fMRI-LM HDF5 schema so that D2 stage 1/2/3 training scripts (to be written
separately) can consume the dataset without modification to the fMRI-LM repo.

## Inputs

| Item | Path |
|------|------|
| ROI csvs (per subject, per stimulus) | `/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_preprocess_JEPA_ROI/time_series/sub-XX/stimulus_N/{fMRI.Schaefer17n400p.csv.gz, fMRI.Tian_Subcortex_S3_3T.csv.gz}` |
| Stimulus labels (V/A + Cowen-Keltner 34D) | `/pscratch/sd/s/sjmoon/EmoBrain/project/shared/data/cowen_horikawa_labels.csv` (2185 rows) |
| Per-trial split + V/A quartile | `/pscratch/sd/s/sjmoon/EmoBrain/project/shared/data/horikawa_split.csv` (10925 rows) |

Coverage. 5 subjects (`sub-01` .. `sub-05`) x 2185 stimuli = **10925 trials, subject-pooled**.

## Pipeline

For every (subject, stimulus_N) trial:

1. Load Schaefer-400 csv and Tian-S3 50 csv, concatenate along ROI axis to
   `(450, T)` float32.
2. Zero-pad or truncate to `T_fixed = 16` (median T in Horikawa is 5; longer
   trials are truncated to keep tensor shapes uniform).
3. Per-subject per-ROI robust z-score. For each subject, stack that subject's
   2185 trials along time, compute `median` and `IQR` per ROI, then z-score
   every trial. Matches the D1 BrainVLM
   `recording="Horikawa_ROI_zscore"` convention so D1/D2 inputs are comparable.
4. Cohort-level robust normalization params (over all 10925 trials) are also
   written to `normalization_params.npz` for compatibility with the official
   fMRI-LM loader.

## Outputs

Default `--out-dir`:
`/pscratch/sd/s/sjmoon/EmoBrain/project/dir2_fmri_lm/data/horikawa_emotion/ROI_Schaefer400Tian50/`

```
data_resampled.h5
  time_series/sample_{i}     (450, 16) float32             # i = 0 .. 10924
  metadata/subjects          (10925,) bytes  e.g. b"sub-03"
  metadata/sessions          (10925,) bytes  e.g. b"stimulus_42"
  metadata/sample_ids        (10925,) bytes  e.g. b"sub-03::stimulus_42"

normalization_params.npz
  medians (450,)  iqrs (450,)        # cohort-level, robust

per_subject_norm.npz
  subjects (5,) bytes
  medians  (5, 450)  iqrs (5, 450)   # the per-subject stats actually applied to the trials

splits/
  train.txt   val.txt   test.txt     # one sample_id per line

descriptors_rewritten/
  va_descriptors.csv          sample_id, text
  va_binary_descriptors.csv   sample_id, text   (Q1 + Q4 only; rows from middle quartiles dropped)
  cat_top1_descriptors.csv    sample_id, text   (top-1 Cowen-Keltner emotion)
  cat_topk_descriptors.csv    sample_id, text   (threshold 0.10)
  mixed_descriptors.csv       sample_id, text   (VA + topk combined)
```

Sample-id format throughout: `"{subject}::stimulus_{N}"`, e.g. `sub-03::stimulus_42`.

## Expected file sizes

- `data_resampled.h5`: ~10925 trials x 450 x 16 x 4 B = ~315 MB
  (10925 individual datasets impose some HDF5 overhead; expect roughly 350-400 MB on disk).
- `normalization_params.npz`: ~7 kB.
- `per_subject_norm.npz`: ~20 kB.
- Each descriptor csv: 100 kB - 1 MB.
- Split txts: ~250 kB total.

## Expected runtime

Sequential, single process, NERSC Perlmutter scratch.

- SMOKE (2 subj x 50 stim = 100 trials): ~30-60 s including HDF5 write.
- Full (5 subj x 2185 stim = 10925 trials): ~10-25 min, dominated by
  `pd.read_csv` on 21850 gzipped csv files. Most of the wall time is IO, not CPU.

If wall time matters, the trial loader is trivially parallelizable across
subjects (5-way) since per-subject normalization stats need only that subject's
trials. Not parallelized in this version to keep determinism simple; add a
`joblib.Parallel` wrapper on `_load_one_trial` if needed.

## Run

```bash
bash /pscratch/sd/s/sjmoon/EmoBrain/project/dir2_fmri_lm/adapters/horikawa_RUN.sh
```

The launcher runs SMOKE first, aborts on non-zero exit, then runs the full
conversion. Logs are written under
`project/shared/output/logs/dir2_fmri_lm/adapter_horikawa/`.

Direct invocation (without the launcher):
```bash
source /pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate
cd /pscratch/sd/s/sjmoon/EmoBrain
python -m project.dir2_fmri_lm.adapters.horikawa --smoke
python -m project.dir2_fmri_lm.adapters.horikawa
```

## Downstream consumers (to be written separately)

The HDF5 + descriptors produced here feed the following D2 training scripts
(not yet written; they will live under `project/dir2_fmri_lm/code/`):

- `train_stage1_pretrain.py`. SSL pre-training of the fMRI-LM encoder on
  Horikawa time-series alone (no descriptor supervision). Reads
  `data_resampled.h5` + `normalization_params.npz`.
- `train_stage2_descriptor.py`. Paired-text contrastive training using
  `descriptors_rewritten/{va,cat_top1,cat_topk,mixed}_descriptors.csv` and the
  Stage 1 encoder weights.
- `train_stage3_finetune.py`. Task-specific heads on the emotion targets
  declared in `configs/horikawa_emotion_dataset_config_patch.yaml`
  (valence_continuous, arousal_continuous, valence_binary, arousal_binary,
  cat34_multilabel, cat34_soft). Splits come from `splits/{train,val,test}.txt`.

## Discrepancies vs. the brief

- The labels csv (`cowen_horikawa_labels.csv`) does NOT contain
  `valence_quartile` / `arousal_quartile` columns. The quartiles (encoded as
  integers `0..3`) live in `horikawa_split.csv` per (subject, stimulus). The
  adapter joins on `(subject, stimulus_name)` and remaps `0..3` -> `Q1..Q4`
  before invoking `make_va_binary` (which expects "Q1"/"Q4" strings).
- The Cowen-Keltner score columns are named `score_0` .. `score_33`. Their
  human-readable names are defined inline in `horikawa.py` (`CAT34_NAMES`,
  Cowen & Keltner 2017 order). If the canonical EmoViS ordering differs,
  update `CAT34_NAMES` in `horikawa.py` (single source of truth) and rerun.
- The Horikawa `time_series` directory contains `stimulus_0` in addition to
  `stimulus_1 .. stimulus_2185` (2186 dirs observed in `sub-01`, plus a few
  extra higher-numbered ones giving 2197 total). The adapter only iterates
  `stimulus_1 .. stimulus_2185` (the canonical EmoBrain count), which exactly
  matches the 2185 rows in the labels csv and the 2185 per-subject rows in the
  split csv.
