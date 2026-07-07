# EmoBrain Build Log

각 코드 사이클 완료 (파일 구현 + sanity 통과) 시 상단 append.
결정 사항 은 `project_decisions.md` 별도.

Spec §12 build order 기준.
1. data 모듈 (labels, datasets, caption_map, fmri_adapter)
2. models/losses + evaluation/metrics
3. baseline (B1 ridge, B2 modality solo)
4. models (encoders, projector, prompt, llm_backbone)
5. student (hard only)
6. teacher + video_encoder
7. distillation
8. eval 확장

---

## 2026-07-03. Cycle 7. Evaluation metrics (Step 2 완성)

**What.** 채점용 metric 4 개. Loss 는 학습 연료, metric 은 성적표. Headline = per-clip 34D profile Pearson + Spearman. 부가 = per-emotion Pearson, RSA, dim compression curve. Config-selectable dispatcher `compute_metrics`.

**설계.**
- `profile_correlation(pred, target)`. HEADLINE. Clip 마다 34D vector 간 Pearson + Spearman → clip 평균. "이 영상 의 감정 profile 이 정답 profile 과 닮았나".
- `per_emotion_correlation(pred, target, rare_idx)`. 감정 마다 clip 을 가로질러 Pearson → 34 값 + 전체 mean + rare subset mean.
- `rsa(pred, target)`. Predicted 34×34 corr matrix upper-triangle vs target upper-triangle Pearson. Structure preservation.
- `dim_compression_curve(pred, target, ks)`. Target PCA top-k 축 에 사영 후 profile correlation 유지율. 고차원 구조 실재 검증.
- `compute_metrics(pred, target, which)`. Dispatcher.

**결정.** Constant vector (std=0) clip 은 correlation undefined → skip + skip 수 report (NaN 오염 방지). 표준.

**Files.**
- `project/evaluation/metrics.py`
- `project/scripts/metrics_smoke.py`, `.sh`

**Sanity.**
- profile. Perfect → Pearson 1.0, Spearman 1.0. Random → ±0.006 (≈ 0). Constant clip 1 개 → skipped=1, 나머지 199 used (NaN 안 섞임).
- per_emotion. Perfect → mean 1.0, rare_mean 1.0.
- rsa. Perfect → 1.0 (561 pair = C(34,2)). Emotion order shuffle → 0.04 (구조 깨짐).
- dim_compression. Perfect → 모든 k 에서 1.0. k=1 은 single dim 이라 sign agreement proxy.
- dispatcher. `which=["profile","rsa"]` → 정확 히 두 키.

**의존성.** scipy 1.17.1 (Spearman), sklearn 1.8.0 (PCA). tribev2 venv 에 존재 확인.

**Meaning.** Step 2 완성. Baseline B1 부터 최종 model 까지 모든 결과 를 이 metric 으로 채점. Headline = per-clip profile Pearson 확정. 다음 = Step 3 baseline (`train_baseline_ridge.py` = 첫 실질 실험). Distillation loss (`models/losses/distillation.py`) 는 teacher 있을 때 (Step 6-7) 추가.

---

## 2026-07-03. Cycle 6. Loss 함수 (Step 2 시작)

**What.** 두 loss function. `supervised.py` (per-emotion MSE, main, 항상 ON) + `structure.py` (34×34 correlation matrix matching, optional, 기본 OFF). Stateless function 으로 구현 (class 불필요).

**설계.**
- `supervised_loss(pred, target, active, per_emotion_weight, huber_delta)`. Per-sample 34 감정 sum → batch mean. Softmax / KL / CE 없음. `active` mask 로 curriculum subset (top-1/2/k) 지원. `per_emotion_weight` optional. `huber_delta` optional (Huber 대안).
- `structure_loss(pred, target, min_batch)`. Batch 안 predicted 34×34 correlation matrix vs target correlation matrix 의 MSE. Batch < 4 reject (correlation 불안정).
- Total loss 는 trainer 에서 `λ_hard × L_main + λ_struct × L_struct`. Default `λ_struct = 0.0` (관계 학습 OFF).

**결정.** 감정 간 관계 학습 은 기본 OFF (structure loss). Loss 는 각 감정 독립 회귀 만. 관계 는 (a) model shared representation 이 implicit 학습, (b) metric (per-clip Pearson, RSA) 으로 사후 관찰. Structure loss 는 config 로 켜는 실험 축 (`lambda_struct` sweep) 으로 남김.

**Files.**
- `project/models/losses/supervised.py`
- `project/models/losses/structure.py`
- `project/scripts/losses_smoke.py`, `.sh`

**Sanity.**
- Supervised. pred==target → 0. z-space scale 검증 (모든 감정 +1 std off → loss 정확 히 34). Active top-1 mask → loss 정확 히 1.0. Per-emotion weight (emo0 ×2) → 35.0. Wrong emotion dim reject.
- Structure. pred==target → 0. Shared-factor target (감정 간 실제 correlation 존재) 에서 감정 절반 sign flip → loss 0.651 (0 대비 크게 증가, sensitivity 확인). Tiny batch (2) reject.
- Smoke test 초안 은 random Gaussian target 으로 structure 를 test 했 는데, i.i.d. Gaussian 은 감정 축 이 무상관 이라 sign flip 해도 loss 변화 미미. Shared-factor target 으로 수정 하여 correlation 구조 가 실재 하도록 fix.

**Meaning.** Neural network training (Step 4+) 의 loss 접점. 이후 어떤 model (E1-E4, teacher, student) 을 붙여도 loss 는 여기 서 import. Baseline B1 (closed-form ridge) 은 loss function 을 직접 안 쓰지만 같은 metric 으로 비교. 다음 사이클 = `evaluation/metrics.py` (per-clip Pearson + Spearman headline).

---

## 2026-07-03. Cycle 5. CaptionMap + Dataset 연결 (Step 1 완성)

**What.** MindCaptioning 스타일 human caption (`caption_ck20.csv`, 43920 row = 2196 stim × 20 rater) 을 stim_num → caption string 으로 매핑 하는 `CaptionMap` class. Rater 정책 = 옵션 3 (train 은 epoch 별 random, val/test 는 stim 별 fixed seed). `HorikawaDataset` 에 `caption_mode="human"` 파라미터 로 연결.

**결정.** Rater 정책 = 옵션 3 (deterministic random). 근거. 옵션 2 (train random, eval rater=0) 는 data leakage 는 아니지만 evaluation bias (rater 0 특성 에 종속). 옵션 3 은 eval 도 20 rater 를 balanced 하게 사용 하되 fixed seed 로 재현 성 유지.

**Files.**
- `project/data/caption_map.py` (`CaptionMap`, `_rater_idx`)
- `project/data/datasets.py` (수정. `caption_mode` + `set_epoch()` 추가)
- `project/scripts/datasets_smoke.py` (수정. Caption sanity 추가)

**Mapping 검증.**
- 우리 `stim_num_int` = Cowen 원본 filename (`0001.mp4`..`2185.mp4`).
- Human `video_id` 도 Cowen 원본 순서 (1-based). 매핑 = **stim_num == video_id** 확정.
- Qwen-VL caption 은 sample 검증 결과 stim 마다 부정확 하게 다른 자극 을 서술 하는 경우 발견 (예. stim 457 인 gun 자극 을 seashells 로 서술). Qwen 자체 부정확 (매핑 은 정상). `captions.json` 은 지금 skip, 별도 사이클 에서 재검증 or 재생성 후 사용.

**Sanity.**
- Coverage. 2196 stim 모두 정확 히 20 rater. 우리 canonical 2185 stim 을 모두 커버.
- Sample 에 `caption` 필드 attach. Non-empty string.
- Train deterministic within epoch. 같은 (stim_num, epoch) → 같은 rater_idx.
- Train cross-epoch variation. Train[0] 을 epoch {0,1,2} 에서 호출 → 3 distinct captions ("A woman walking on catwalk falls" / "A model slips and falls on runway" / "A woman walks on catwalk but slips"). 20 rater 를 augmentation 으로 활용.
- Val / test epoch-invariant. `set_epoch(99)` 무시. Val[0] 은 항상 같은 rater.

**Meaning.** Step 1 data 모듈 완성. 앞으로 teacher (Step 6) 가 caption 을 input 으로 씀. 지금 Baseline B1 (LLM 없는 ridge) 은 caption 안 씀. Trainer 는 `dataset.set_epoch(epoch)` 를 epoch 시작 마다 호출 해야 rater rotation 이 정상 작동. Qwen-VL caption 재생성 / 재검증 은 별도 사이클 (Step 6 진입 전).

---

## 2026-07-03. Cycle 4. FmriAdapter + Dataset 연결 (Step 1 마무리 앞 사이클)

**What.** Cycle 3 에서 만든 `roi_timeseries/sub-XX.pt` 를 memory 에 load 하는 얇은 `FmriAdapter` class. `HorikawaDataset` 이 이 adapter 를 참조 하여 placeholder zeros 를 실제 fMRI 로 교체. 두 mode 지원. `mean` = `(450,)`, `timeseries` = `(T_max=47, 450)` + `(T_max,)` bool mask + `original_T`.

**Files.**
- `project/data/fmri_adapter.py` (`FmriAdapter` class)
- `project/data/datasets.py` (수정. `fmri_mode` 파라미터 추가, adapter 호출)
- `project/scripts/datasets_smoke.py` (전체 재작성. Real fmri sanity + 두 mode 검증 + padding-invariance)

**Sanity.**
- Split 개수 유지. train 8740, val 1085, test 1100.
- Mean mode. sample fmri shape `(450,)`. Zeros 아님, range `[-0.311, +0.754]` (실제 BOLD).
- Cross-subject 검증. 같은 stim (stim 3) 에서 5 subject 의 fMRI std (ROI 평균) `+0.1795`. Label 은 identical (subject-invariant) 이지만 fMRI 는 subject 별 다름. Pool 방식 실증.
- Timeseries mode. sample fmri shape `(47, 450)`, mask shape `(47,)` bool, `original_T=8` (stim 3 의 실제 T). Padding zone `[T=8..46]` 이 exact zero.
- Padding-invariance under mask. Padding 자리 를 scale-1e3 random noise 로 바꾸고 masked mean 을 재계산 해도 원본 과 max abs diff `0.00e+00` (bit-for-bit identical). Mask 가 padding 을 완벽 히 차단.

**Meaning.** Step 1 data 모듈 의 마지막 core 파일. 이 사이클 후 부터 baseline / model 이 즉시 `HorikawaDataset` 을 사용 가능. Sample 구조 는 앞으로 모든 encoder / model 이 받는 계약. 다음 사이클 (caption_map) 은 Baseline B1 에는 필요 없지만 data 모듈 완성 을 위해.

---

## 2026-07-03. Cycle 3. ROI time-series build (Step 1 지속)

**What.** Raw ROI CSV (Schaefer 400 + Tian 50) 를 subject 별 통합 pt 로 변환. Right-padded T_max=47 + mask + metadata. Baseline / E1 / E2 (roi_mean) 과 E3 BFM (roi_timeseries + mask) 이 공유 할 fMRI 원본 form.

**Files.**
- `project/scripts/build_roi_timeseries.py`
- `project/scripts/build_roi_timeseries.sh`

**Output.**
- `project/shared/data/roi_timeseries/sub-{01..05}.pt` (5 파일, 각 184 MB, 합 920 MB)
- Per pt. `roi_timeseries (2185, 47, 450)` + `roi_mean (2185, 450)` + `mask (2185, 47)` + `original_T` + `stim_num` + `T_max=47` + `n_roi=450` + `missing_stim`

**Sanity.**
- Missing 0 stim / subject. Canonical 2185 완벽.
- Valid ratio 12.9 % (T_max=47, median T=5 이라 storage 87 % zero padding).
- Regenerated `roi_mean` vs 기존 reference `roi_schaefer400tian50_mean/sub-XX.pt` embeddings. Max abs diff `~10⁻⁷`, mean abs diff `~10⁻⁹` (float32 precision 한계). 우리 pipeline 이 기존 mean 을 numerically 재생성 함.
- Padding-invariance. Padding 자리 를 scale-1e3 random noise 로 대체 해도 mask 적용 mean 이 원본 과 identical (max abs diff `~10⁻⁷`). Padding zero 가 downstream 에 leak 안 됨 검증.

**Meaning.** Baseline B1 이 이 pt 의 roi_mean 을 받아 34D 예측 예정. "엄격 controlled baseline" 원칙 (baseline 과 우리 model 이 동일 source, 동일 preprocess) 이 여기 서 성립. Bit-for-bit 재생성 이 아닌 float32 tolerance 안 identical 이라 실질 결과 identical. Padding 정책 (right-pad + mask + 3 규칙) 은 앞으로 encoder / model 이 반드시 강제.

---

## 2026-07-03. Cycle 2. HorikawaDataset pool 로더 (Step 1 지속)

**What.** PyTorch `Dataset` 하나. Pool 5-subject × 2185-stim 을 (subject, stim) 개별 sample 로 batch 접근. 지금 은 fMRI 필드 를 zeros placeholder 로 두고 label + metadata 만 실제 값.

**Files.**
- `project/data/datasets.py` (`HorikawaDataset`)
- `project/scripts/datasets_smoke.py`, `.sh`

**Sanity.**
- Split sample 수 정확. train 8740 (5 subj × 1748 stim), val 1085 (5 × 217), test 1100 (5 × 220). 합 10925.
- 같은 stim 에서 5 subject 의 label 이 identical (subject-invariant label). Pool 방식 검증.
- Sample dict = `{subject_id, stim_idx, stim_num, label (34,), fmri (16, 450) placeholder}`.
- Z-scored label 전체 range [-0.881, +20.353], mean ~ 0, std 1. Long-tail 은 원 데이터 가 대부분 0 fraction 이라 정상.

**Meaning.** 앞으로 baseline / model 이 다 이 dataset 을 `DataLoader` 로 감싸 학습. 데이터 로딩 접점 하나 로 통일. fMRI 는 다음 사이클 (fmri_adapter) 에서 실제 값 으로 교체 예정.

---

## 2026-07-02. Cycle 1. Cowen 34D label z-score preprocessing (Step 1 시작)

**What.** 34D emotion rating 을 train-fit z-score 로 rescale 하는 `Cowen34Normalizer` class. Sklearn `StandardScaler` 관례 (fit / transform / save / load) 를 torch native 로 구현. 실제 로 train 통계 fit + mu / std pt 저장.

**Files.**
- `project/data/labels.py` (`Cowen34Normalizer` class)
- `project/scripts/labels_fit.py`, `.sh`

**Data prep.**
- `project/shared/data/cowen_horikawa_labels.csv` 를 symlink 에서 실제 file 로 copy (사용자 규칙, symlink 금지).
- 34D score 는 0-1 fraction (rater agreement). Row sum mean 1.71 → distribution 아님, 독립 score 형태.
- V/A 는 1-9 Likert (별도).

**Output.**
- `project/shared/data/norm_stats/cowen34_train.pt` (mu 34D + std 34D + emotion_dim=34).

**Sanity.**
- Train unique stimuli 1748, val 217, test 220 (총 2185).
- Post-transform train mean range `[-1.24e-7, +1.01e-7]` (거의 0), std range `[+1.0000, +1.0000]` (거의 1).
- CAUTION 준수. Train 만 fit, val/test 는 이후 transform 만.

**Meaning.** 앞으로 모든 loss / metric / model 은 이 z-score 공간 에서 동작. 표시 용 raw scale 은 별도 inverse_transform. 이 파일 이 spec §12 build order 의 첫 진입점.
