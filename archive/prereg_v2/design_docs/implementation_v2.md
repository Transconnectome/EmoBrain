---
title: "EmoBrain 구현 사양"
subtitle: "v2 revised — teacher relation formation and model-computational intervention pipeline"
date: "2026-09-12"
---

# 1. 구현 원칙

- 설계의 단일 진실 원천은 `prereg_v2.md`다.
- 모든 fit, 변환, feature selection, PCA, hyperparameter 선택은 training fold 안에서만 수행한다.
- repeated test 72 stimuli는 최종 평가와 reliability/noise ceiling에만 사용한다.
- 동일 stimulus는 모든 participant에서 같은 outer fold에 속한다.
- 모든 cache에 `dataset_id`, `participant_id`, `stimulus_id`, `run_id`, `fold_id`, source-file hash, preprocessing-config hash를 저장한다.
- 세 student 조건은 brain architecture, parameter count, optimizer, fold, seed, early stopping을 공유한다.
- 34-D, 14-D, VA-2, VAD-3는 split과 architecture-selection rule만 공유하며 teacher/student parameter, head, label transform, loss와 OOF cache를 공유하지 않는다.
- 결과 코드는 absolute metric과 paired difference를 동시에 생성한다.
- CKA는 secondary geometry summary로 저장하고 primary success flag를 생성하지 않는다.
- Mechanistic result는 affect readout baseline gate와 retrieval-null gate를 통과한 경우에만 confirmatory flag를 갖는다.
- imagery/recall, SPoSE, PCM, Shapley, gradient boundary, two-stage decoding은 구현하지 않는다.

# 2. 권장 디렉터리 계약

```text
configs/
  data.yaml
  features.yaml
  encoding.yaml
  student.yaml
  geometry.yaml
  inference.yaml
manifests/
  participants.tsv
  stimuli.tsv
  stimulus_crosswalk.tsv
  folds.json
  freeze_manifest.json
features/
  low_level/
  alexnet_fc7/
  vjepa2/
  sentence_caption/
brain/
  responses/
  roi_pca/
teachers/
  category34/{brain_only,brain_visual,brain_visual_semantic,shuffled_content}/
  appraisal14/{brain_only,brain_visual,brain_visual_semantic,shuffled_content}/
  va2/{brain_only,brain_visual,brain_visual_semantic,shuffled_content}/
  vad3/{brain_only,brain_visual,brain_visual_semantic,shuffled_content}/
students/
  category34/{direct,full_guided,shuffled_guidance}/
  appraisal14/{direct,full_guided,shuffled_guidance}/
  va2/{direct,full_guided,shuffled_guidance}/
  vad3/{direct,full_guided,shuffled_guidance}/
results/
  analysis1_encoding/
  analysis2_integration_recovery/{geometry,retrieval,roi_reliance}/
  analysis3_readout/
  replication/
tests/
reports/{figures,heldout_exemplars}/
```

# 3. Phase 0 — provenance와 동결

## 3.1 participant/stimulus manifest

### 작업

1. primary와 replication dataset의 participant ID 목록 작성
2. video 파일의 content hash와 normalized stimulus ID 생성
3. 두 dataset의 stimulus 교집합/차집합 산출
4. normative 34-D/14-D annotation key와 video key의 one-to-one/one-to-many 상태 점검
5. 34-D 값의 raw proportion 정의와 category별 선택 count `k`, rater count `n` 가용성 점검
6. 14-D column name, scale direction, range와 VA-2/VAD-3 column mapping을 codebook에서 확정
7. run, session, onset, presented duration, repetition index 기록

### 수용 기준

- participant ID 중복 여부가 명시됨
- `stimulus_crosswalk.tsv`에 2,180/2,181 차이가 설명됨
- annotation이 없는 stimulus와 중복 annotation이 모두 보고됨
- 34-D raw values가 `[0,1]` proportion인지 검증되고 `k,n` 가용성 상태가 기록됨
- VA-2/VAD-3 mapping과 각 14-D rating 방향이 manifest에 기록됨
- file hash가 같은 stimulus의 fold가 participant 간 일치함

## 3.2 freeze manifest

다음 값이 기록되고 primary outcome 실행 전 read-only snapshot으로 저장되어야 한다.

- dataset/version
- response-estimation method
- atlas/version
- PCA rule
- feature checkpoints, layers, pooling
- outer/inner folds
- teacher structure
- student candidate set
- λ candidate set
- seed list
- metrics와 inference rule
- target별 loss, output activation, standardizer, OOF-cache namespace

# 4. Phase 1 — fMRI response pipeline

## 4.1 response estimate

두 경로를 만든다.

- reproducibility path: 제공/기존 block response
- candidate primary path: raw fMRI에서 GLMsingle single-trial beta

둘의 repeated-test split-half reliability를 label-blind하게 비교하고 한 경로를 동결한다. 긴 영상은 실제 presentation duration을 boxcar에 반영한다.

### 수용 기준

- participant/run별 trial 수가 events와 일치
- repeated stimulus의 response reliability 표
- 결측 run과 censoring rule 문서화
- response estimate 선택이 34-D/14-D label 성능을 보지 않고 이루어짐

## 4.2 atlas와 ROI tokenization

1. Schaefer cortical atlas와 Tian subcortical atlas를 participant 공간에 사상
2. 각 outer training fold에서 voxel standardization fit
3. ROI별 PCA fit
4. train/validation/test에 동일 transform 적용
5. `[stimulus, roi, component]`와 valid-component mask 저장

### 수용 기준

- test data로 fit된 scaler/PCA가 0개
- ROI별 voxel 수, retained component 수, explained variance 보고
- empty/small ROI 처리 규칙 고정
- 모든 participant가 shared encoder의 동일 ROI index order를 사용

# 5. Phase 2 — frozen content features

## 5.1 common interface

모든 feature extractor는 다음 record를 출력한다.

```text
stimulus_id
source_name
checkpoint
layer
sampling_config_hash
raw_shape
pooled_shape
feature_vector
```

PCA가 필요하면 outer training stimuli에서만 fit하고, source별 original dimension과 retained dimension을 manifest에 저장한다.

## 5.2 low-level control

- frame luminance/color summary
- spatial-frequency summary
- motion-energy summary

### 수용 기준

- 동일 frame sampling 사용
- constant/NaN dimension 제거가 train fold에만 의존
- feature dimension과 분포 보고

## 5.3 V-JEPA 2 spatiotemporal visual

- language alignment 이전 frozen visual encoder
- checkpoint는 freeze manifest에 정확히 기록
- 8초 미만 loop 여부와 8초 이상 window rule은 실제 presentation protocol을 확인한 뒤 고정
- layer와 temporal pooling은 training fold 또는 사전 정의한 단일 설정으로만 선택

### 수용 기준

- video decode failure 0 또는 명시된 제외표
- frame timestamp와 presentation window의 일치
- looped stimulus 표시
- test performance로 layer를 선택하지 않았음을 로그로 보장

## 5.4 sentence-level caption semantics

- human captions를 개별 문장으로 encode
- stimulus-level sentence embedding을 생성하고 caption 간 평균
- caption 간 평균으로 stimulus representation 생성
- affect-word masking, role reversal, word-order scrambling 없음

### 수용 기준

- stimulus별 caption 수와 결측 분포 보고
- model/version/tokenizer hash 저장
- caption text가 split에 따라 변하지 않음
- translation 또는 generated caption이 섞였으면 source column으로 구분

정확한 sentence-encoder checkpoint, layer와 pooling은 sentence-level 적합성, 재현성, 계산 가능성의 근거를 기록한 뒤 preregistration 전에 동결한다. 특정 checkpoint를 관행만으로 선택하지 않는다.

## 5.5 AlexNet fc7 supplementary anchor

- pretrained object-recognition AlexNet
- 고정 frame sampling
- frame별 fc7 후 시간 평균
- parameter update 없음
- primary teacher와 주 nested contrast에는 사용하지 않음

### 수용 기준

- checksum으로 pretrained weights 고정
- batch/order 변화에 대한 deterministic output tolerance 통과
- output shape와 frame coverage 보고
- 결과를 object 전용 또는 event 부재의 증거로 해석하지 않음

# 6. Phase 3 — Analysis 1 encoding

## 6.1 입력과 target

- X kernels: low-level, V-JEPA 2 spatiotemporal visual, caption semantics
- Y: participant별 ROI-PCA response pattern
- outer split: stimulus/run held-out
- inner split: regularization과 kernel weight 선택

## 6.2 모델 집합

```text
M0 = low_level
M1 = spatiotemporal_visual
M2 = spatiotemporal_visual + caption_semantics
```

multi-kernel ridge를 사용한다. primal banded-ridge와 dual kernel 구현 중 계산 자원에 맞는 것을 선택하되 작은 synthetic dataset에서 prediction equivalence test를 통과해야 한다.

## 6.3 출력

- participant × ROI × model의 held-out correlation
- participant × ROI × model의 explained variance
- M1−M0, M2−M1, M2−M0 paired differences
- repeated-test reliability와 normalized metric
- permutation null과 bootstrap CI

## 6.4 수용 기준

- held-out prediction만 결과 파일에 사용
- feature kernel normalization이 fold-local
- identical fold mask가 모든 nested model에 적용
- ROI map 외에 participant-level dot plot 생성

# 7. Phase 4 — OOF multimodal neural teachers

## 7.1 shared teacher architecture

```text
fMRI ROI-PCA tokens → participant adapter → compact brain encoder ─┐
V-JEPA 2 visual tokens → frozen encoder → visual projector ────────┼→ compact token fusion → fused brain-token state → joint latent u → target-specific head
caption → frozen sentence encoder → semantic projector ────────────┘
```

brain, visual, semantic token identity는 fusion 전까지 보존한다. fusion 후보는 gated token pooling과 1-block cross-attention 두 개로 제한하고, OOF validation이 비슷하면 parameter가 적은 모델을 선택한다. attention weight는 explanation으로 사용하지 않는다.

Primary 34-D teacher objective는 다음과 같다.

```text
p_teacher = sigmoid(logits_teacher)
L_teacher_34 = mean_d soft_BCE(y_proportion[d], p_teacher[d])
```

- raw 34-D `[0,1]` category proportion을 한 sigmoid joint head에서 동시에 예측
- z-score, log1p, arbitrary class-frequency/dimension weight를 사용하지 않음
- raw category count `k,n`이 확인될 때만 binomial NLL을 robustness로 계산

Dimensional teacher objective는 다음과 같다.

```text
y_z = standardize_per_dimension(y; fit_on_outer_train_only)
L_teacher_q = mean_d MSE(y_z[d], yhat_teacher_z[d]), q in {appraisal14, va2, vad3}
```

- appraisal14, va2, vad3는 각각 별도 teacher를 학습하고 standardizer와 checkpoint를 공유하지 않음
- inference report에서는 prediction을 원척도로 역변환
- 모든 loss는 output dimension으로 나누어 target dimension 수에 따른 scale 차이를 제거

## 7.2 matched teacher ladder

```text
T_B        = brain + masked visual + masked semantic
T_BV       = brain + visual + masked semantic
T_BS       = brain + masked visual + semantic
T_BVS      = brain + visual + semantic
T_BVS_SHUF = brain + shuffled visual + shuffled semantic
```

Primary category34의 다섯 teacher는 brain encoder, projector width, fusion module, target head와 parameter budget을 맞춘다. `T_BVS_SHUF`는 training fold 안에서 visual과 semantic을 같은 permutation으로 재배열해 두 content modality의 상호관계는 유지하고 brain/stimulus alignment만 끊는다. Full teacher ladder와 relation-formation/patching pipeline은 category34에서만 실행한다. appraisal14, va2, vad3는 `T_BVS`만 학습해 target별 OOF guidance와 final functional contrast를 생성한다. target 간에는 checkpoint와 trainable parameter를 공유하지 않는다.

## 7.3 OOF cache 생성

outer training set 안의 각 sample에 대해, sample이 속한 fold를 제외하고 teacher를 fit한 뒤 prediction을 저장한다.

```text
teacher_kind
outer_fold
oof_fold
stimulus_id
participant_id
true_profile_hash
target_space
prediction[target_dim]
joint_latent
model_config_hash
training_stimulus_hashes
```

### 필수 assert

- `stimulus_id`가 `training_stimulus_hashes`에 있으면 실패
- test stimulus의 label이 teacher fit에 들어가면 실패
- teacher OOF cache의 `(participant_id, stimulus_id)` key와 brain cache가 일치하지 않으면 실패
- 동일 stimulus hash가 다른 participant를 통해 OOF teacher training에 들어가면 실패

## 7.4 shuffled student guidance

각 target의 outer training fold 안에서 full-teacher OOF prediction의 stimulus row를 하나의 permutation으로 재배열한다. target-vector 내부 관계와 marginal distribution은 보존하고 stimulus pairing만 끊는다. seed별 permutation을 저장한다.

# 8. Phase 5 — brain-only students

## 8.1 architecture

```text
ROI-PCA components
  → participant-specific linear adapter per ROI
  → masked ROI tokens
  → small shared encoder
  → pooled held-out latent z
  → target-specific joint head
```

small shared encoder 후보는 최대 세 개로 제한한다.

- linear/reduced-rank baseline
- 1-block token mixer or transformer
- 2-block token mixer or transformer

큰 모델을 기본으로 두지 않는다. validation에서 단순 baseline 대비 평균 향상과 seed 안정성이 모두 있을 때만 비선형 encoder를 주 모델로 채택한다.

## 8.2 conditions

```text
category34 direct:            soft_BCE(y, p_student)
category34 full_guided:       soft_BCE(y, p_student) + λ * mean_d MSE(p_T_BVS_oof, p_student)
category34 shuffled_guidance: soft_BCE(y, p_student) + λ * mean_d MSE(permuted_p_T_BVS_oof, p_student)

q direct:            mean_d MSE(y_z, yhat_student_z)
q full_guided:       mean_d MSE(y_z, yhat_student_z) + λ * mean_d MSE(yhat_T_BVS_oof_z, yhat_student_z)
q shuffled_guidance: mean_d MSE(y_z, yhat_student_z) + λ * mean_d MSE(permuted_yhat_T_BVS_oof_z, yhat_student_z)
q in {appraisal14, va2, vad3}
```

## 8.3 training parity

- 동일 seed로 weight initialization
- 동일 batch order
- 동일 optimizer/scheduler
- 동일 early-stopping rule
- 동일 parameter count
- 동일 label transform
- 동일 target 안에서만 parameter/schedule parity를 강제하고, target 간 checkpoint 재사용 금지
- λ=0 direct run도 같은 training code path 사용

## 8.4 수용 기준

- test-time forward signature에 content input이 없음
- condition별 parameter count 일치
- OOF target provenance test 통과
- seed별 validation/test metric과 checkpoint hash 저장
- NaN/constant prediction check 통과
- target-space ID가 모든 checkpoint, prediction, metric file에 포함됨
- `category34`, `appraisal14`, `va2`, `vad3` 사이 trainable parameter object 공유 0

# 9. Phase 6 — Analysis 2 relation formation, inheritance, and functional use

## 9.1 activation export

Primary category34 teacher ladder의 projected modality tokens, fused brain-token state와 joint latent `u_B`, `u_BV`, `u_BS`, `u_BVS`, `u_BVS_SHUF`, 그리고 student의 participant adapter, encoder block 1, block 2, 최종 head 직전 `z`를 held-out stimuli에서 export한다. 반복 test는 먼저 repetition-mean stimulus activation을 만들고, repetition-wise activation은 reliability table로 분리한다.

## 9.2 held-out teacher mismatch generation

```text
clean         = B_i + V_i + S_i
video_swap    = B_i + V_j + S_i
caption_swap  = B_i + V_i + S_j
both_swap     = B_i + V_j + S_j
```

- `j != i`인 derangement index를 participant와 held-out fold 안에서 생성
- 같은 permutation set을 모든 teacher checkpoint와 metric에 재사용
- primary random derangement 수와 seed를 `freeze_manifest.json`에 저장
- both-swap에서는 같은 `j`의 V–S pair를 사용해 content coherence를 보존
- robustness용 video match는 low-level feature distance, caption match는 caption length와 surface-statistic distance만 사용하고 affect label은 사용하지 않음
- projected tokens, fused brain tokens, joint latent, output profile을 condition별로 저장

### 수용 기준

- clean과 swap condition의 brain tensor가 동일
- video-swap에서는 caption tensor가, caption-swap에서는 video tensor가 동일
- both-swap의 video/caption stimulus ID가 동일하고 brain ID와 다름
- permutation이 held-out fold와 participant 경계를 넘지 않음
- mismatch 생성에 affect outcome을 사용하지 않음

## 9.3 low-capacity held-out readout과 retrieval

각 condition × participant × seed × stage에서 다음 held-out readout을 계산한다. readout model은 training stimuli에서만 fit하고 student encoder는 고정한다.

```text
stages     = [adapter, block1, block2, z]
references = [teacher_joint_BVS, vjepa2_visual, caption_semantic, profile_34d]
contrasts  = [full-direct, full-shuffled]
```

### teacher-joint retrieval

- training-fold linear 또는 reduced-rank mapping으로 BVS joint latent를 예측
- held-out candidate set에서 correct-stimulus top-k accuracy와 median rank 계산
- neighborhood overlap은 secondary로 저장

### visual auxiliary task

- training-fold PCA로 V-JEPA 2 target을 축약한 뒤 multi-output ridge로 예측
- metric: held-out feature correlation, correct-video top-k accuracy, median rank

### semantic auxiliary task

- frozen sentence embedding을 multi-output ridge로 예측
- metric: held-out embedding correlation, correct-caption top-k accuracy, median rank

모든 readout은 linear 또는 reduced-rank로 제한하고 regularization은 probe-training fold 안에서 선택한다. Shuffled-label과 matched-capacity null을 같은 split에 계산한다. 두 auxiliary task는 student optimizer loss와 model selection metric에 포함하지 않는다. Free-form caption generation은 별도 생성 연구가 되므로 사용하지 않는다.

전체 stage-wise joint/visual/semantic probe와 CKA는 primary `category34` pipeline에서 수행한다. `appraisal14`, `va2`, `vad3`에서는 final functional contrast만 confirmatory로 계산하고 같은 geometry/content 분석을 반복하지 않는다.

### 수용 기준

- 동일 stimulus order
- probe split이 student outer-test stimulus를 training에 사용하지 않음
- synthetic linear-signal recovery와 null-label test 통과
- row permutation 후 null behavior 확인
- probe가 student training loss에 사용되지 않았음을 config assert
- retrieval candidate set과 distance metric이 condition 간 동일

## 9.4 secondary layer×reference linear CKA

```text
student_stages = [adapter, block1, block2, z]
references     = [teacher_joint_BVS, vjepa2_visual, caption_semantic, profile_34d]
conditions     = [direct, full_guided, shuffled_guidance]
```

- 동일 held-out stimulus ID와 순서에서 centered linear CKA 계산
- condition별 absolute heatmap과 `full-direct`, `full-shuffled` difference heatmap 생성
- CKA는 optimizer loss, checkpoint 선택 또는 probe fitting에 사용하지 않음
- neighborhood는 secondary: correlation distance primary, cosine robustness
- secondary k: 5, 10, 20, 40; k=10 summary
- participant/seed별 CKA와 neighborhood 결과를 분리 저장

### 수용 기준

- self-neighbor 제외
- ties rule 고정
- k가 n_stimulus보다 작음
- shuffled row synthetic test에서 chance 수준 확인
- constant/near-zero reference column 처리 규칙 고정

## 9.5 teacher activation patching

For each clean/mismatch pair, run the frozen category34 BVS teacher once and cache the following eligible patch locations.

```text
patch_locations = [
  post_fusion_brain_tokens,
  joint_latent
]
readouts = [
  teacher_joint_retrieval,
  video_retrieval,
  caption_retrieval,
  affect_profile_metric
]
```

At one location at a time, replace the mismatch activation with the clean activation from the same `(participant_id, stimulus_id)`; leave every other activation from the mismatch run unchanged. Store clean, mismatch, patched and null-patched metrics. Compute raw recovery and normalized recovery.

```text
raw_recovery = metric_patched - metric_mismatch
denominator  = metric_clean - metric_mismatch
normalized_recovery = raw_recovery / denominator
```

The denominator tolerance, aggregation rule and direction convention for loss-based metrics are frozen before outcomes. Nulls are wrong-stimulus clean activation, random eligible location and equal-size random token sets. A patch is interpreted only when video or caption retrieval and affect output recover in the predicted direction and exceed matched nulls.

### 수용 기준

- patched tensor shape와 mask가 source/target run에서 동일
- 한 번에 한 location만 교체되고 나머지 cached activation은 tolerance 내 동일
- clean source stimulus ID가 query stimulus와 일치
- null patch가 같은 tensor 크기와 횟수를 사용
- denominator near zero 처리 규칙이 condition-independent
- model-computational intervention으로만 report

## 9.6 predefined anatomical network perturbation

### prerequisite와 grouping

- ROI별 PCA가 atlas ROI 경계를 넘지 않고 fit되었는지 확인
- participant adapter가 ROI token을 섞지 않고 ROI별 공통 width로만 사상하는지 확인
- Schaefer/Tian atlas-derived network group 목록과 ROI membership을 `freeze_manifest.json`에 outcome-blind하게 기록
- network에는 결과 확인 전 `visual`, `semantic`, `affective` 같은 functional label을 붙이지 않음

### primary perturbation

Held-out participant 안에서 선택 network의 모든 ROI token에 같은 stimulus permutation을 적용한다. 나머지 ROI token, valid-component mask와 model parameter는 고정한다. 이는 token의 marginal distribution을 유지하면서 해당 network의 stimulus-specific pairing만 끊는다.

```text
delta_joint_retrieval   = metric(clean) - metric(permuted_network)
delta_video_retrieval   = metric(clean) - metric(permuted_network)
delta_caption_retrieval = metric(clean) - metric(permuted_network)
delta_affect_readout    = metric(clean) - metric(permuted_network)
```

### robustness와 null

- training-fold network mean-token replacement
- leave-one-network-out refit with identical training schedule
- 같은 크기의 ROI token을 무작위로 선택한 matched null perturbation
- condition별 absolute drop과 `full-direct`, `full-shuffled` drop difference

### 수용 기준

- permutation은 participant와 held-out fold 경계를 넘지 않음
- 같은 permutation seed를 모든 student condition과 readout에 재사용
- untouched network token이 bitwise 또는 tolerance 내 동일
- perturbation 전 clean metric이 저장된 Analysis 2/3 결과와 일치
- model-reliance로만 report하고 neural causality 문장을 자동 template에서 금지

## 9.7 held-out exemplar montage

- retrieval 성공/실패와 rank 분위수에 기반한 exemplar 선택 규칙을 outcome 확인 전에 고정
- 모든 condition에 같은 stimulus ID를 표시
- video frame, neutral caption, nearest-neighbor ID와 rank만 표시하고 latent unit에 사후 이름을 붙이지 않음
- saliency 또는 attention overlay를 주 설명으로 사용하지 않음

## 9.8 mechanistic interpretation gate

```text
gate_affect = full_guided_category34 > mean_profile_baseline
              and full_guided_category34 > mandatory_linear_or_rrr_baseline
gate_content = relevant_retrieval > stimulus_permutation_null
confirmatory_mechanism = gate_affect and gate_content
```

The exact paired statistic and interval rule are read from `freeze_manifest.json`. Gate failure does not suppress results; it changes the status of patching and ROI/network perturbation from confirmatory mechanism evidence to exploratory diagnostics.

# 10. Phase 7 — Analysis 3 readout

## 10.1 34-D metrics

- stimulus-wise profile Pearson r (primary)
- training-fold mean-profile prediction baseline (mandatory)
- Brier score와 RMSE
- category-wise calibration curve/intercept/slope
- dimension-wise across-stimulus r, macro-Fisher-z
- training-fold category base-rate를 제거한 residual profile r (robustness)
- ceiling-normalized metric (supplementary)

모든 metric은 condition별 absolute value와 `Full−Direct`, `Full−Shuffled` paired contrast를 출력한다.

## 10.2 geometry–function table

participant × seed 단위로 다음을 한 row에 저장한다.

```text
delta_readout_full_direct
delta_readout_full_shuffled
delta_readout_visual_by_stage
delta_readout_semantic_by_stage
delta_joint_recovery_by_stage
delta_cka_by_stage_and_reference
delta_teacher_mismatch_by_stage_and_modality
delta_activation_patch_recovery_by_stage_and_readout
delta_roi_reliance_by_network_and_readout
```

상관은 기술적 결과로만 보고하고 participant 수를 부풀리기 위해 seed를 독립 참가자로 취급하지 않는다.

## 10.3 independent dimensional-target analyses

`appraisal14`, `va2`, `vad3`를 각각 완전히 별도 teacher/student pipeline으로 실행한다. 34-D 및 서로 간에 label standardizer, head, encoder weights, OOF cache, optimizer state와 metric cache를 공유하지 않는다. architecture candidate, outer/inner split, condition 정의와 λ candidate grid만 공유한다.

각 dimensional target의 metric은 다음과 같다.

- primary: dimension-wise across-stimulus Pearson r의 macro-Fisher-z
- secondary: original-scale RMSE와 concordance correlation coefficient
- VA-2/VAD-3: valence, arousal, dominance dimension별 결과를 반드시 별도 출력
- target 내부 contrast: `Full−Direct`, `Full−Shuffled`
- target 간 허용 비교: effect direction과 within-target standardized gain
- target 간 금지 비교: raw r/RMSE의 절대 순위와 `2D<3D<14D<34D`를 theory evidence로 사용하는 것

# 11. Phase 8 — replication cohort

1. primary freeze manifest를 복사해 변경 불가 상태로 둔다.
2. replication participant의 response/ROI-PCA와 adapter만 적합한다.
3. 같은 stimulus ID가 primary와 replication에서 같은 feature vector를 참조하는지 hash로 확인한다.
4. primary와 동일 metric/contrast를 계산한다.
5. effect direction, participant distribution, CI를 보고한다.

새 자극 일반화라고 표기하지 않는다. 참가자 ID가 겹치거나 stimulus crosswalk가 예상과 다르면 replication label을 수정하고 보고한다.

# 12. 추론

- stimulus permutation: condition pairing을 유지한 공동 permutation
- participant-clustered bootstrap: participant를 cluster로, cluster 안 stimulus를 재표집하는 계층 bootstrap
- small-n 보고: p-value보다 participant별 effect, bootstrap CI, direction consistency를 우선
- multiple comparison: primary 34-D teacher의 사전 정의 conditional-source/alignment 대비, mismatch × stage family, activation-patch × readout family, student 두 주 대비와 network × readout family 안에서 각각 보정
- individual ROI maps: exploratory 또는 supplementary로 명시하고 FDR 적용
- stimulus pairs: 독립 observation으로 사용 금지
- seeds: uncertainty source로 요약하되 inferential n으로 사용 금지

# 13. 필수 자동 검사

| test | 실패 조건 |
|---|---|
| `test_no_stimulus_leakage` | 같은 stimulus hash가 train과 held-out에 존재 |
| `test_fold_shared_across_participants` | participant마다 동일 stimulus의 fold가 다름 |
| `test_pca_train_only` | PCA fit sample에 held-out ID 존재 |
| `test_teacher_oof` | OOF target 생성 model이 해당 stimulus를 학습 |
| `test_teacher_global_stimulus_holdout` | 동일 stimulus가 다른 participant를 통해 teacher training에 유입 |
| `test_teacher_capacity_parity` | B/BV/BS/BVS/shuffled teacher의 shared component·parameter budget 불일치 |
| `test_teacher_mismatch_integrity` | modality swap이 지정하지 않은 brain/content tensor까지 변경하거나 fold 경계를 넘음 |
| `test_activation_patch_isolation` | 지정한 activation 외 tensor가 clean 값으로 바뀌거나 null patch 크기가 불일치 |
| `test_mechanistic_gate` | baseline/null gate 실패인데 confirmatory mechanism flag가 true |
| `test_condition_parameter_parity` | 세 student의 trainable parameter 수 불일치 |
| `test_target_parameter_isolation` | category34/appraisal14/va2/vad3 사이 trainable parameter, optimizer state 또는 OOF cache 공유 |
| `test_target_columns` | VA/VAD 열, rating 방향 또는 scale이 freeze manifest와 불일치 |
| `test_loss_target_match` | 34-D에 continuous MSE label loss를 쓰거나 dimensional target에 soft BCE를 사용 |
| `test_brain_only_inference` | test forward가 content tensor를 요구 |
| `test_probe_not_in_loss` | linear-probe/CKA term이 optimizer loss에 존재 |
| `test_auxiliary_tasks_posthoc_only` | visual/semantic target 또는 metric이 student training/model selection에 사용 |
| `test_stimulus_order` | latent와 reference kernel의 ID 순서 불일치 |
| `test_roi_token_provenance` | ROI PCA 또는 participant adapter가 atlas ROI identity를 섞음 |
| `test_network_perturbation_scope` | 선택 network 밖 token이 변하거나 participant/fold 경계를 넘어 permutation |
| `test_perturbation_pairing` | condition 간 다른 permutation seed 또는 candidate set을 사용 |
| `test_exemplar_selection_frozen` | outcome 확인 뒤 exemplar 규칙 또는 stimulus ID를 변경 |
| `test_pairwise_independence_guard` | inferential dataframe row가 stimulus-pair 단위 |
| `test_replication_freeze` | replication 실행에서 primary config hash 변경 |

# 14. 핵심 figure 산출

1. Study overview: neural organization → relation formation/inheritance → functional affect readout
2. Model architecture: training-only brain+video+caption teacher, OOF output guidance, brain-only inference, teacher relation formation, student inheritance, activation patching and ROI/network perturbation
3. Analysis 1: nested encoding 성능과 incremental contrast
4. Analysis 2: primary 34-D B/BV/BS/BVS/shuffled teacher ladder, held-out modality mismatch, fused brain-token shifts, student content retrieval, secondary CKA, activation patching and predefined anatomical-network perturbation
5. Analysis 3: 34-D profile readout의 Full−Direct/Full−Shuffled contrast와 replication
6. Prespecified secondary: 별도 학습한 14-D alternative-ontology contrast
7. Compact controls: 별도 학습한 VA-2와 VAD-3 contrast
8. Supplement: reliability/noise ceiling, ROI maps, architecture baseline

# 15. 완료 정의

- freeze manifest와 crosswalk가 존재한다.
- 모든 primary 결과가 held-out prediction에서 생성된다.
- Direct/Full/Shuffled student가 동일 조건으로 학습된다.
- teacher B/BV/BS/BVS/shuffled의 capacity와 fold provenance가 일치한다.
- visual/semantic task는 frozen-student held-out readout으로만 실행된다.
- teacher mismatch, student retrieval, secondary CKA, activation patching과 predefined network perturbation이 relation formation, inheritance, geometry summary와 model-computational use로 구분되어 저장된다.
- mechanistic interpretation gate가 baseline/null status에 따라 confirmatory/exploratory flag를 올바르게 생성한다.
- ROI token provenance와 perturbation scope 자동 검사가 통과한다.
- Analysis 1→2→3의 각 결과 파일이 같은 stimulus/participant provenance를 가진다.
- 34-D, 14-D, VA-2, VAD-3가 parameter를 공유하지 않는 별도 pipeline으로 보고된다.
- target별 loss와 metric이 measurement scale에 맞게 적용되고 cross-target absolute ranking이 생성되지 않는다.
- primary와 replication cohort 결과가 같은 report schema로 생성된다.
- 문서에서 금지한 과대해석을 자동 report template이 사용하지 않는다.
