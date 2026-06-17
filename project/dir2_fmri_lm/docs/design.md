# Direction 2. fMRI-LM — Design

EmoBrain Direction 2. **Wei 2026 fMRI-LM official repo 를 그대로 사용.** EmoBrain 안에 git submodule 로 등록 (`external/repos/fMRI-LM` → `https://github.com/yuxiangwei0808/fMRI-LM`). 협업자는 `git clone --recursive` 또는 `git submodule update --init` 로 가져온다.

이 direction 은 fMRI-LM 의 architecture / loss / quantizer / LLM / LoRA 설정을 변경하지 않고, 다음 두 가지만 더한다.

1. **새 dataset adapter**. 협업자가 자기 dataset (Horikawa, Emo-FilM, 또는 그 외) 의 raw fMRI → fMRI-LM 의 HDF5 schema 로 변환하는 entry point.
2. **NERSC SLURM wrapper**. fMRI-LM 의 `scripts/launch_train_*.sh` 의 default 인자를 그대로 가져온 NERSC m4641 / gpu queue 용 sbatch script.

## 0. 원칙 (변경 금지)

| 항목 | 위치 |
|------|------|
| ViT (Brain-JEPA 의 ViT 구현 차용) | `brain_encoder/vision_transformer.py` |
| Patch embed | `brain_encoder/patch_embed.py` |
| Quantizer | `quantizers/{vq,fsq}.py` |
| 3-stage trainer | `train_quantizer*.py`, `train_pretrain_paired.py`, `train_instruction*.py` |
| Model wrapper | `model_fmrilm.py`, `model_gpt.py` |
| Loss / objectives | `utils_loss.py` |
| Dataset loader | `dataset.py` |
| Config | `configs/*.yaml` |

위 파일은 *수정하지 않는다*. 우리 변경/추가는 모두 `project/dir2_fmri_lm/code/` 또는 `scripts/` 안에 머문다. fMRI-LM 의 upstream 동기화를 깨지 않기 위함.

## 1. fMRI-LM 의 3-stage (변경 없음, reference)

기존 official 의 3 stage 그대로.

- Stage 1. `train_quantizer_contr.py`. Tokenizer + contrastive (`--contr_loss=soft_siglip`, `--desc_type=fc,ica`).
- Stage 2. `train_pretrain_paired.py`. LLM paired pretraining (Qwen3-0.6B + LoRA r=1 alpha=2 q_proj/k_proj, DeepSpeed zero stage 2).
- Stage 3. `train_instruction.py`. Instruction tuning (`--add_src_info`, `--use_random_prompt`, `--use_allowed_tokens`, `--add_desc`).

config 와 인자 default 는 user 본인의 `scripts/launch_train_*.sh` 와 동일. 우리 wrapper 는 동일 인자 + NERSC SLURM directive + env var override 가능 형태로만.

## 2. 데이터 schema (변경 없음, reference)

```
data/<DATASET>/fmri/<ATLAS>/
├── data_resampled.h5
│     time_series/sample_{i}: (N_rois, N_timepoints) float32
│     metadata/subjects:      (N_samples,) bytes
│     metadata/sessions:      (N_samples,) bytes
├── normalization_params.npz
│     medians (N_rois,) iqrs (N_rois,)    # if --norm robust
│     mean    (N_rois,) std  (N_rois,)    # if --norm std
└── descriptors_rewritten/
      fc_descriptors.csv
      ica_descriptors.csv
      gradient_descriptors.csv
      graph_descriptors.csv
      (또는 emotion 등 새 desc_type 추가 가능)
```

dataset 별 cohort 한 줄 설명은 fMRI-LM 의 `dataset.py` 의 `DATASET_INFO` dict 에 1 line 추가가 필요할 수 있다. 본 repo 의 코드 변경 없이 협업자가 자기 fork 에서 추가하거나, EmoBrain 측 maintenance fork 에 한꺼번에 패치.

## 3. EmoBrain 의 추가물 (`project/dir2_fmri_lm/code/`)

| Path | 역할 |
|------|------|
| `adapters/_template.py` | 새 dataset 의 raw → fMRI-LM HDF5 변환 template. `write_h5`, `write_normalization_params` helper 포함 |
| `adapters/generate_descriptors.py` | emotion label (V/A continuous + multilabel/soft K-cat) 을 descriptor CSV (`va_descriptors.csv`, `cat_top1_descriptors.csv`, `cat_topk_descriptors.csv`) 로 변환 |
| `configs/dataset_config_patch.yaml` | fMRI-LM 의 `configs/dataset_config.yaml` 에 emotion dataset entry 추가용 (협업자가 merge 하거나 참고) |
| `eval_emotion/metrics.py` | V/A regression, K-class multilabel (threshold 0.10), soft distribution metric. fMRI-LM 의 metrics/ 는 임상 분류 위주라 별도 |

## 4. NERSC wrapper (`scripts/`)

| Script | 대응되는 official |
|--------|---------------------|
| `setup_external.sh` | (없음) — symlink + checkpoint 안내 |
| `train_stage1.sh` | `launch_train_quantizer_contr.sh` |
| `train_stage2.sh` | `launch_train_pretrain_paired_deepspeed.sh` |
| `train_stage3.sh` | `launch_train_instruction.sh` |

default 인자는 user 본인 launch script 와 동일.
- Stage 1. quantizer=vq, contr_loss=soft_siglip, cfg=vit_small_gpt2_p160, desc_type=fc,ica, domain_confuse_weight=0.5
- Stage 2. quantizer=vq, cfg=vit_base_p160, lm=Qwen/Qwen3-0.6B, lora_target=q_proj,k_proj, lora_r=1, lora_alpha=2, dropout=0.1, deepspeed zero_stage=2
- Stage 3. quantizer=vq, cfg=vit_base_p160, lm=Qwen/Qwen3-0.6B, add_src_info, use_random_prompt, use_allowed_tokens, add_desc

환경변수 override 패턴 (`DATASET_DIR`, `DESC_TYPE`, `CFG_PATH`, `LM_NAME`, `QUANTIZER`, `TOKENIZER_PATH`, `PRETRAINED_CKPT`, `TRAIN_SCRIPT`) 으로 dataset / config 만 바꿔서 재사용.

## 5. 협업자 onboarding (다른 dataset 가져갈 때)

`getting_started.md` 의 "Adding a new dataset" 참고. 핵심.

- (a) raw fMRI 를 atlas 적용 후 `(N_rois, N_timepoints)` time series 로 만들고, `adapters/<your_dataset>.py` 작성 (template 복사).
- (b) `code/adapters/generate_descriptors.py` 로 paired text supervision 생성.
- (c) fMRI-LM 의 `dataset.py` 의 `DATASET_INFO` 에 cohort 1 line, `configs/dataset_config.yaml` 에 dataset entry 추가.
- (d) `scripts/train_stage*.sh` 의 `DATASET_DIR` env var 만 새 path 로 바꿔서 sbatch.

위 4 step 외에는 fMRI-LM upstream 코드를 건드릴 일이 없다.

## 6. Reference

- fMRI-LM (Wei 2026, arXiv 2511.21760). official architecture.
- 본 EmoBrain Direction 2 는 fMRI-LM 의 emotion-specific 적용 path. 모델 변경 없음.
