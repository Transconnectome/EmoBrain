# EmoBrain `project/` Quick Reference

EmoBrain 의 active 분석 work 가 모두 모이는 폴더. Three Directions 의 entry point 와 공통 자원의 한눈 정리.
자세한 forward plan 은 `../docs/masterplan_v3_emobrain.md`, ground-level action 은 `../ACTION_PLAN.md`.

## 1. Directions at a glance

| Dir | Method | Architecture base | 위치 | 결정 (모델/코드 변경) |
|------|---------|--------------------|------|------------------------|
| **D1** | BrainVLM | Qwen3-VL backbone + ROI patchify + LoRA + multi-task heads | `dir1_brainvlm/` | UMBRELLA_qwen (`external/repos/BrainVLM/UMBRELLA_qwen/`) reference, 우리 emotion task 에 맞춰 신규 |
| **D2** | fMRI-LM | Wei 2026 fMRI-LM 3-stage (tokenizer + paired LLM + instruction tuning) | `dir2_fmri_lm/` | **upstream 그대로 사용**. `external/repos/fMRI-LM/` submodule. wrapper 만 추가 |
| **D3** | CCN | Brain-Video alignment (SigLIP + GRL) + context clustering | `dir3_ccn/` | study1/2 의 본문 연구 + alignment_pilot scaffolding |
| **shared** | 공통 자원 | Phase 1 baseline, BFM embedding, splits, target matrices | `shared/` | 두 main direction 이 공유 |

D1 + D2 는 main paper 의 2 axis (2 × 2 grid with Horikawa + Emo-FilM). D3 는 별도 workshop path.

## 2. Direction 별 핵심 정보

### D1. BrainVLM (`dir1_brainvlm/`)

| 항목 | 값 |
|------|-----|
| Input shape | (3, 224, 224) — Schaefer-400 + Tian-S3 50 ROI 의 2D grid (L1 layout, 23×20=460 cells 중 10 pad) |
| Sequence length | 단일 image (time-axis mean). L3 ablation 으로 (450, T) matrix 가능 |
| ROI atlas | Schaefer-400 + Tian-S3 50 = 450 ROI |
| Backbone | Qwen3-VL-2B-Instruct, vision tower frozen, LLM body LoRA r=16 alpha=32 |
| Output | (a) caption 자연어 (b) V/A 2-D scalar (c) K-cat soft distribution |
| Loss | CE (caption) + λ1 MSE (V/A) + λ2 KL (cat soft), λ1=1.0 λ2=0.5 |
| Env | `/pscratch/sd/s/sjmoon/brainvlm_qwen_env` (torch 2.11.0, transformers 4.57.0, peft 0.19.2.dev0) |
| Pilot HW | NERSC m4641 gpu queue, A100 80GB 1 장 |
| Smoke | `bash scripts/smoke_test.sh` (skeleton-only, file/backbone 부재 OK) |
| Pilot | `sbatch scripts/train_pilot_path_a.sh` (사용자 사전 승인 필수) |

### D2. fMRI-LM (`dir2_fmri_lm/`)

| 항목 | 값 |
|------|-----|
| Input shape | (N_rois, N_timepoints) per sample, HDF5 `time_series/sample_{i}` |
| Sequence length | 기본 cfg `vit_base_p160.yaml` 의 patch size 160 (clip_timepoints=160), short-T dataset 의 경우 interpolate 처리 (`fMRI-LM/dataset.py:interpolate_time_dimension`) |
| ROI atlas | Schaefer-400 + Tian-S3 50 = 450 ROI (TianS3 디렉토리 명) |
| Backbone | Stage 2/3 의 LLM 은 Qwen3-0.6B (user 본인 default), LoRA r=1 alpha=2 dropout=0.1 on q_proj/k_proj |
| Quantizer | VQ (user 본인 default) — 변경 금지 |
| Output (Stage 3) | instruction-following 자연어 (single-Q/A default, multi-Q/A + open-ended variant) |
| Env | `/pscratch/sd/s/sjmoon/brainvlm_qwen_env` |
| Pilot HW | NERSC m4641 gpu queue, A100 80GB 4 장 (DeepSpeed zero stage 2) |
| Repository | `external/repos/fMRI-LM/` (submodule). 모델/loss/quantizer/LLM 변경 없음 |

### D3. CCN (`dir3_ccn/`)

| 항목 | 값 |
|------|-----|
| Brain encoder input | BFM hidden state (Brain-JEPA, NeuroSTORM, SwiFT) 또는 ROI mean. (5 subj, 2185 stim) |
| Video encoder | V-JEPA2 pretrained (default) |
| Projection | ProjBrain (768→1024→512), ProjVideo (1408→1024→512) |
| Alignment loss | SigLIP (learnable log_t, b) + GRL (modality discriminator) |
| Smoke | `bash code/alignment_pilot/scripts/smoke_test.sh` (PASS) |
| Pilot | `sbatch code/alignment_pilot/scripts/train_pilot_{resting,scratch}.sh` (사용자 사전 승인 필수) |

### shared (`shared/`)

| 항목 | 위치 |
|------|------|
| ROI time series (필요 시 추출) | `shared/data/roi_timeseries_schaefer400tian50/` |
| Splits | `shared/data/horikawa_5fold.csv`, `horikawa_split.csv` |
| Stimulus feature embeddings | `shared/data/stimulus_features/` (Qwen-VL caption, V-JEPA2/CLIP/DINOv2/VideoMAE pretrained + scratch) |
| BFM hidden state embeddings | `shared/output/embeddings/` (Brain-JEPA 5 subj × 10 cell, NeuroSTORM, SwiFT 6 변종) |
| Phase 1 background result | `shared/results/background/phase1/` |
| 공통 probe/baseline code | `shared/code/{probes,bfm_embeddings,ssl_pretrain,analysis,tools}/` |

## 3. 데이터 schema 비교

### D2 의 schema (fMRI-LM 표준)

```
data/<DATASET>/fmri/<ATLAS>/
├── data_resampled.h5
│     time_series/sample_{i}: (N_rois, N_timepoints) float32
│     metadata/subjects:      (N_samples,) bytes
│     metadata/sessions:      (N_samples,) bytes
├── normalization_params.npz
│     medians (N_rois,) iqrs (N_rois,)    # --norm robust
│     mean    (N_rois,) std  (N_rois,)    # --norm std
└── descriptors_rewritten/
      fc_descriptors.csv
      ica_descriptors.csv
      gradient_descriptors.csv
      graph_descriptors.csv
```

### D1 의 schema

`shared/data/` 에 모인 standardized matrix.
- `horikawa_5fold.csv` (per-stim fold split).
- `roi_timeseries_schaefer400tian50/sub-XX_<stim>.npy` (각 (T, 450)).
- `stimulus_features/qwen_vl_captions.jsonl` (per-stim 자연어).
- `va_continuous_z.csv` (per-stim valence_z, arousal_z).
- `cat34_soft_distribution.csv` (per-stim 34-cat soft, Horikawa 의 Cowen rating).

(주의. 위 파일 일부는 아직 추출 대기. `shared/code/probes/` 의 wrapper 로 생성.)

## 4. 환경

| 자원 | 위치 | 용도 |
|------|------|------|
| Python (general) | `/pscratch/sd/s/sjmoon/tribev2/.venv` | probe, baseline, D3 alignment, dataset adapter smoke |
| Python (LLM) | `/pscratch/sd/s/sjmoon/brainvlm_qwen_env` | D1 LoRA, D2 LLM tuning |
| Submodule (D1 reference) | `external/repos/BrainVLM/` | UMBRELLA_qwen 의 patch_embed + merger + trainer |
| Submodule (D2 본체) | `external/repos/fMRI-LM/` | Stage 1/2/3 trainer 그대로 사용 |
| Compute | NERSC m4641 (cpu/gpu queue) | A100 80GB |

## 5. 협업자 onboarding (다른 사람도 가져갈 수 있게)

clone.
```bash
git clone --recursive git@github.com:Transconnectome/EmoBrain.git
# 이미 clone 했다면
git submodule update --init --recursive
```

각 direction 의 `docs/getting_started.md` 가 사용법 entry.

새 dataset (Horikawa, Emo-FilM 외) 을 D2 에 가져갈 때.
1. raw fMRI → HDF5 변환 (`dir2_fmri_lm/code/adapters/_template.py` 복사).
2. paired descriptor CSV (`dir2_fmri_lm/code/adapters/generate_descriptors.py`).
3. `external/repos/fMRI-LM/dataset.py` 의 `DATASET_INFO` + `configs/dataset_config.yaml` 에 1 줄 추가.
4. `dir2_fmri_lm/scripts/train_stage1.sh` 의 `DATASET_DIR` env var override 만으로 launch.

## 6. 결과 + 운영 규칙

- 모든 .py 는 .sh 동반 (NERSC 의 sbatch 진입점).
- Bash 명령은 절대경로. cd + relative 금지.
- sbatch 는 사용자 사전 승인 필수.
- 결과 / output / checkpoint 는 per-direction 의 `output/`, `results/` 에 저장. shared 자원은 `shared/` 에.
- D1, D2 의 main paper 결과는 standard baseline suite (chance / ROI Ridge / BFM frozen reference / video baseline) 와 함께 reporting.

## 7. Forward plan

- Background. Phase 1 frozen BFM 한계 확정 완료 (`../docs/reports/phase1_audit_20260604/`).
- D1 / D2. Horikawa pilot → Emo-FilM 확장 → 2 × 2 grid.
- D3. alignment pilot → context clustering 학습 → cross-dataset transfer → CCN workshop.

자세한 forward plan 은 `../docs/masterplan_v3_emobrain.md`.
