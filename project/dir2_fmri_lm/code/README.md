# D2 fMRI-LM code

EmoBrain Direction 2. **Wei 2026 fMRI-LM official repo (https://github.com/yuxiangwei0808/fMRI-LM) 그대로 사용.**
재구현 없음. clone 위치 `/pscratch/sd/s/sjmoon/EmoBrain/external/repos/fmri-lm/`.

이 `code/` 하위는 official 에 *추가* 만 한다.

- `adapters/`        새 dataset 의 raw → fMRI-LM HDF5 schema 변환 (`data/<DATASET>/fmri/TianS3/data_resampled.h5` 형식). 협업자가 다른 dataset 추가할 때 entry point.
- `configs/`         `dataset_config.yaml` 의 우리 추가 패치 + NERSC 환경용 `vit_*.yaml` override (필요 시).
- `eval_emotion/`    emotion-specific evaluation (V/A r, Cat34 multilabel, soft). official 이 임상 (sex, AD 등) 분류 위주라 emotion 평가는 별도.

## 원칙

- **fMRI-LM 의 train_quantizer*, train_pretrain_paired, train_instruction, model_fmrilm, model_gpt, dataset, brain_encoder, language_models, quantizers, utils 는 절대 수정하지 않음.** Upstream patch 가 필요하면 fork 또는 별도 PR.
- 우리 추가는 모두 `project/dir2_fmri_lm/code/` 또는 `scripts/` 안에.
- Dataset 별 hardcode 는 official 의 dataset_config.yaml + dataset.py 의 DATASET_INFO 패턴 따른다.

## 사용 흐름

1. `scripts/setup_external.sh`. official repo clone (이미 완료) + Stage 1/2 checkpoint 다운로드.
2. `code/adapters/<DATASET>.py` 로 raw fMRI → `data/<DATASET>/fmri/TianS3/data_resampled.h5` 생성.
3. `code/adapters/generate_descriptors.py` 로 descriptor CSV 생성 (협업자가 보유한 emotion label 또는 video caption 으로).
4. `code/configs/dataset_config_patch.yaml` 로 dataset 추가, official `configs/dataset_config.yaml` 와 merge.
5. `scripts/train_stage{1,2,3}_<dataset>.sh` 의 NERSC SLURM wrapper 로 학습 (사용자 사전 승인 후 sbatch).
6. `code/eval_emotion/` 의 metric 으로 emotion-specific 결과 평가.

`docs/design.md`, `docs/getting_started.md` 의 ground-level 상세.

## 협업자 가이드 (다른 dataset 가져갈 때)

`docs/getting_started.md` Section "Adding a new dataset" 참고. 핵심 4 step.
- (a) raw fMRI → HDF5 변환 (atlas 결정, normalization param 계산)
- (b) descriptor CSV 생성 (paired text supervision)
- (c) `configs/dataset_config.yaml` 에 entry 추가
- (d) launch script 의 `--dataset_dir` 에 새 path 추가
