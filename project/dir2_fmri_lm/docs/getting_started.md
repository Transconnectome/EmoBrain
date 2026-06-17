# D2 fMRI-LM Getting Started

EmoBrain Direction 2. **Wei 2026 fMRI-LM official repo 그대로 사용.** EmoBrain 안에 git submodule (`external/repos/fMRI-LM` → `https://github.com/yuxiangwei0808/fMRI-LM`) 로 등록되어 있다. 협업자는 EmoBrain clone 시 자동으로 함께 받는다.

이 가이드는 협업자가 자기 dataset (Horikawa, Emo-FilM, 또는 그 외) 으로 fMRI-LM 을 가져다 쓰는 방법을 정리한다. **fMRI-LM 의 모델/loss/quantizer/LLM 설정은 변경하지 않는다.**

## 0. TL;DR

```bash
# (one-time) symlink + checkpoint 안내
bash /pscratch/sd/s/sjmoon/EmoBrain/project/dir2_fmri_lm/scripts/setup_external.sh

# 새 dataset 추가 (Section 4 참고)
#   1. raw fMRI -> HDF5 변환 (adapters/<your_dataset>.py)
#   2. descriptors CSV 생성 (adapters/generate_descriptors.py)
#   3. fMRI-LM 의 dataset.py + dataset_config.yaml 에 entry 추가
#   4. scripts/train_stage*.sh 의 DATASET_DIR override

# Stage 별 학습 (사용자 사전 승인 후)
sbatch /pscratch/sd/s/sjmoon/EmoBrain/project/dir2_fmri_lm/scripts/train_stage1.sh
sbatch /pscratch/sd/s/sjmoon/EmoBrain/project/dir2_fmri_lm/scripts/train_stage2.sh
sbatch /pscratch/sd/s/sjmoon/EmoBrain/project/dir2_fmri_lm/scripts/train_stage3.sh
```

## 1. 환경

| 항목 | 경로 |
|------|------|
| Python env | `/pscratch/sd/s/sjmoon/brainvlm_qwen_env` (torch 2.11.0+cu130, transformers 4.57.0, peft 0.19.2.dev0) |
| fMRI-LM 본체 (submodule) | `external/repos/fMRI-LM` |
| EmoBrain 안 symlink | `/pscratch/sd/s/sjmoon/EmoBrain/external/repos/fmri-lm` |
| Stage 1/2 checkpoint (Google Drive) | `external/checkpoints/fmri_lm_stage12/` 로 다운로드 |
| NERSC account | `m4641` |
| GPU queue | `regular -C gpu --gpus-per-node=4` (A100 80GB) |

## 2. 디렉토리 구조

```
project/dir2_fmri_lm/
├── code/
│   ├── README.md
│   ├── adapters/
│   │   ├── _template.py                새 dataset 의 raw -> HDF5 변환 template
│   │   └── generate_descriptors.py     emotion label -> descriptor CSV
│   ├── configs/
│   │   └── dataset_config_patch.yaml   fMRI-LM dataset_config.yaml 에 추가용 entry
│   └── eval_emotion/
│       └── metrics.py                  V/A reg, K-cat multilabel/soft
├── scripts/
│   ├── setup_external.sh
│   ├── train_stage1.sh                 train_quantizer_contr.py wrapper
│   ├── train_stage2.sh                 train_pretrain_paired.py wrapper
│   └── train_stage3.sh                 train_instruction.py wrapper
├── docs/{design.md, getting_started.md}
├── data/, output/, results/
```

## 3. fMRI-LM 본체의 데이터 schema

```
data/<DATASET>/fmri/<ATLAS>/
├── data_resampled.h5
│     time_series/sample_{i}: (N_rois, N_timepoints) float32
│     metadata/subjects:      (N_samples,) bytes
│     metadata/sessions:      (N_samples,) bytes
├── normalization_params.npz
│     medians, iqrs   (--norm robust)
│     mean, std       (--norm std)
└── descriptors_rewritten/
      fc_descriptors.csv
      ica_descriptors.csv
      gradient_descriptors.csv
      graph_descriptors.csv
      (emotion 등 새 desc_type 추가 가능)
```

ROI 수 / atlas / norm 방식은 fMRI-LM 의 `configs/vit_*.yaml` + `dataset.py` 의 default 와 일치해야 한다. 기본은 Schaefer-400 + Tian-S3 50 = 450 ROI (TianS3 디렉토리 명).

## 4. Adding a new dataset (협업자 가이드)

### Step 1. raw fMRI -> HDF5

`code/adapters/_template.py` 를 `code/adapters/<your_dataset>.py` 로 복사 후 다음을 구현.

- raw fMRI 를 atlas (default Schaefer-400 + Tian-S3 50) 로 ROI time series 추출. 결과 shape `(N_rois, N_timepoints)`.
- `write_h5(out_path, time_series_list, subjects, sessions)` 호출.
- `write_normalization_params(out_path, time_series_list, norm='robust')` 호출.

산출.
```
data/<YOUR_DATASET>/fmri/TianS3/data_resampled.h5
data/<YOUR_DATASET>/fmri/TianS3/normalization_params.npz
```

### Step 2. descriptors CSV

paired text supervision. 두 가지 경로.

- 기존 fMRI-LM 의 `nbs_data/get_fmri_discriptor.py` 로 fc/ica/gradient/graph descriptor 생성 (functional connectivity 기반 자연어, 임상 dataset 표준).
- 또는 emotion task 라면 본 repo 의 `code/adapters/generate_descriptors.py` 로 emotion label 기반 descriptor 생성.

```bash
PYTHONPATH=/pscratch/sd/s/sjmoon/EmoBrain python -m project.dir2_fmri_lm.code.adapters.generate_descriptors \
    --va-csv     <your va csv: sample_id, valence, arousal> \
    --cat-csv    <your K-class soft distribution csv: sample_id, <K label cols>> \
    --label-cols-file <one label name per line> \
    --out-dir    data/<YOUR_DATASET>/fmri/TianS3/descriptors_rewritten/
```

산출. `va_descriptors.csv`, `cat_top1_descriptors.csv`, `cat_topk_descriptors.csv`.

### Step 3. fMRI-LM 코드에 dataset 등록

upstream 변경이 한 곳에 모인다.

- `external/repos/fMRI-LM/dataset.py` 의 `DATASET_INFO` dict 에 cohort 한 줄 추가. 예시.
  ```python
  'Horikawa': 'This subject is from Horikawa et al. naturalistic video fMRI dataset (5 subjects, 2185 video stimuli).',
  ```
- `external/repos/fMRI-LM/configs/dataset_config.yaml` 에 entry 추가. 예시는 `code/configs/dataset_config_patch.yaml` 의 Horikawa block 참고.

이 두 줄 외에는 fMRI-LM 코드를 건드릴 필요 없다.

### Step 4. launch

```bash
# 환경변수로 dataset / desc / config 만 override. 모델 설정은 default 그대로.
DATASET_DIR=data/<YOUR_DATASET>/fmri/TianS3/ \
DESC_TYPE=va,cat_topk \
sbatch /pscratch/sd/s/sjmoon/EmoBrain/project/dir2_fmri_lm/scripts/train_stage1.sh
```

## 5. Stage 별 launch 인자 (변경 없음)

각 wrapper 는 user 본인의 `scripts/launch_train_*.sh` 의 default 를 그대로 가져온다.

### Stage 1. `train_stage1.sh`

```
quantizer=vq
cfg=configs/vit_small_gpt2_p160.yaml
contr_loss=soft_siglip
fmri_pool_method=cls, text_pool_method=last
contr_weight=1.0, domain_confuse_weight=0.5
desc_type=fc,ica   (env var DESC_TYPE 로 override)
batch_size=12, epochs=50
```

### Stage 2. `train_stage2.sh`

```
quantizer=vq
cfg=configs/vit_base_p160.yaml
lm_name=Qwen/Qwen3-0.6B
lora_target=q_proj,k_proj, lora_r=1, lora_alpha=2, lora_dropout=0.1
deepspeed zero_stage=2
text_only_weight=0.1
fmri_batch_size=4, gradient_accumulation_steps=8, epochs=30
tokenizer_path=checkpoints/tokenizer/UKB_robust/VQ_Align-ViT_base-p160/ckpt-best.pt  (TOKENIZER_PATH 로 override)
```

DeepSpeed checkpoint 는 학습 후 `merge_deepspeed_checkpoint.py` 로 merge 필요. 자세한 내용은 fMRI-LM 본체의 README 참고.

### Stage 3. `train_stage3.sh`

```
quantizer=vq
cfg=configs/vit_base_p160.yaml
lm_name=Qwen/Qwen3-0.6B
add_src_info, use_random_prompt, use_allowed_tokens, add_desc, save_ckpt
gradient_accumulation_steps=8, epochs=30
pretrained_ckpt=<Stage 2 merged ckpt>   (PRETRAINED_CKPT 로 override)
TRAIN_SCRIPT=train_instruction.py  (single-Q/A 기본, train_instruction_mq.py 또는 train_instruction_open_ended.py 로 변경 가능)
```

## 6. Emotion 평가

fMRI-LM 의 `eval_zeroshot.py` 는 임상 binary classification 위주. emotion task (V/A regression, K-cat multilabel/soft) 는 본 repo 의 `code/eval_emotion/metrics.py` 의 3 함수.

```python
from project.dir2_fmri_lm.code.eval_emotion.metrics import (
    va_regression_metrics, cat_multilabel_metrics, cat_soft_metrics,
)
```

## 7. 다음 단계 ordering

1. `setup_external.sh` 로 symlink + checkpoint 확보.
2. 첫 협업 dataset 선택 (Horikawa 또는 Emo-FilM).
3. adapter `code/adapters/<dataset>.py` 작성 + HDF5 생성.
4. descriptors CSV 생성.
5. fMRI-LM 의 `dataset.py` + `configs/dataset_config.yaml` 에 entry 추가.
6. Stage 1 → 2 → 3 학습 (사용자 사전 승인 후 sbatch).
7. `code/eval_emotion/metrics.py` 의 metric 으로 emotion 평가.
