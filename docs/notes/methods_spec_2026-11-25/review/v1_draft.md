# EmoBrain 방법론 상세 사양 v1 (2026-11-25)

## 표기 규칙

**수치 출처 표기.** 모든 하이퍼파라미터에는 아래 네 표기 중 하나가 붙는다. 데이터셋 크기처럼 표기가 없는 수치는 데이터 사실이다.
- **[R: 경로]** repo 기본값
- **[P: 인용]** 선행연구 값
- **[V: grid]** val에서 선택
- **[D6.n]** 근거 있는 값이 없어 사용자 결정이 필요한 항목. §6 목록의 n번이다. 이 경우 "제안"이라고 적은 값은 근거가 없다는 뜻이다.

**사실 검증 표기.** (V) 1차 자료 확인 / (I) 간접 / (U) 미확인.

**경로 약어.** `SP` = `/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad`

| 약어 | 절대경로 | commit |
|---|---|---|
| JS | SP/verify_A_lens/JunShern_VideoMAE | 35cf177 |
| ED | SP/verify_A_lens/hendrycks_emodiversity | 4deaea3 |
| VM2 | SP/verify_A_lens/OpenGVLab_VideoMAEv2 | 29eab1e |
| VJ | SP/repos/vjepa2 | 204698b |
| PE | SP/verify_A_lens/facebookresearch_perception_models | 3e352cc |
| PM | SP/repos/pymoten | a641c8a |
| TIMM | SP/v2_stimcode/timm | b4f423c |
| HKpy | SP/verify_B_decode/KamitaniLab_EmotionVideoNeuralRepresentationPython | 451236c |
| FD / FL | SP/v2_brain/feature-decoding / SP/v2_brain/PyFastL2LiR | ef0f1cc / 4b7c794 |
| MCR | SP/verify_A_lens/horikawa-t_MindCaptioning | 4c39764 |
| HIM | SP/repos/himalaya | v0.4.11 |
| AL | /home/user/AffectLab | |

---

## 0. 전체 구조

```
 [VCE 61,046 영상, 27-d 평균 강도, 독립 평정자 (Mazeika et al. 2022)]
        | 1회 학습 후 동결 (Cowen 평정, 뇌 데이터 열람 전)
        v
 영상 x --> 정서 렌즈 f : VideoMAE ViT-B/16 (K400 self-sup pretrain)
            -> 12 blocks -> token mean -> fc_norm (768) -> head Linear(768->27) -> 27 logits
 영상 x --> 정보 수준 특징 (모두 기존 공개 모델, 동결)
            L  저수준 : pymoten 운동에너지 2530 (+ 색 히스토그램)
            O  대상   : O-obj EVA02-L in22k (pre-logit, 21841 named logits)
                        O-act VideoMAE V2-B K710 distilled (768, 710 named logits)
            S  상황   : S-cap  Cowen 전용, 인간 캡션 20개 -> DeBERTa-large 층별 토큰평균
                        S-vis  전 데이터, PE-Core G14-448 영상 임베딩 1280 ("language-aligned vision")
 readout g_level : 특징 -> 27 (VCE에서 ridge 학습 후 동결; S-cap만 Cowen train fold)

 HK 뇌 (5명; voxel 수준은 HK h5, ROI-mean은 Schaefer400+Tian50)
   Encoding  E_R : [L | O-obj | O-act | S] --banded ridge (himalaya)--> voxel     (2막, 4막 in silico)
   Decoding  D_R : ROI voxel --L2 ridge, 특징 단위별, voxel 선택 (FastL2LiR)--> 특징^ (3막, 감정 라벨 없음)
   직접 decoder  : ROI voxel --같은 방식--> 27 평정                               (3막 비교 기준)
   3막 경로      : 뇌 -> D_R -> 특징^ -> (동결 렌즈 head 또는 g_level) -> 27
 MC 6명 / Emo-FilM 30명 : HK ROI-mean decoder를 재적합 없이 적용                 (4막)
```

| 막 | 고정 (동결) | 학습 | 평가 데이터 |
|---|---|---|---|
| 1막 자극->정서 | 렌즈 f, 특징 추출기 전부 | 분해용 banded ridge (L/O/S -> 27), 자극 train fold에서만 | VCE-test, Cowen stimulus test |
| 2막 자극모델<->뇌 | 특징 추출기, HK 데이터 | 목표만 다른 VideoMAE arm (E, E-perm, N-act, N-obj) x seeds; arm별 encoding ridge | HK hk_dev_v4 test folds |
| 3막 뇌->정서 | 렌즈 head, g_level, 특징 | ROI별 특징 decoder D_R (라벨 없음), 직접 decoder (비교용) | HK test folds |
| 4막 예측 | 3막의 모든 decoder, 렌즈, g, encoding 모델 | 없음. 단 V2V Bradley-Terry 가중치, Cowen 14차원 PLS, 장르 PLS-DA readout은 각 외부 라벨에서 CV로 학습 | MC 72 (지각/심상), Emo-FilM, VCE 61k, V2V listwise, Trailers |

**원칙 4개**
1. 렌즈는 Cowen, HK, MC, Emo-FilM의 어떤 라벨도 보지 않는다.
2. 뇌 측 decoder D_R는 감정 라벨을 보지 않는다.
3. MC 반응은 학습, 선택, 정규화, 정렬, 보정 어디에도 쓰지 않는다.
4. 모든 출력은 연속 27-d다. top-1, 임계값, 범주 묶기는 하지 않는다.

---

## 1. 데이터와 분할

### 1.1 VCE (Mazeika et al. 2022, NeurIPS Datasets and Benchmarks)

**구성**
- 61,046 영상: train 50,000, test 11,046 [ED README L12-89] (V).
- 라벨: `emotions` dict, 27개 이름별 평균 강도 0-1 [ED README] (V).
- 로딩 순서: `sorted()`, 즉 알파벳순 [R: JS vce.py L58-63] (V).

**렌즈 풀(lens-pool)** = VCE-train 50,000에서 다음을 뺀 것.
- (a) V2V test 6,223개와 listwise 4,322개. 4막 V2V 검정을 표본 외로 만들기 위해서다. VCE train/test와 V2V 분할이 어떻게 겹치는지는 미확인이라(U), 해당 영상 ID를 모두 뺀다.
- (b) §1.6 중복 검사에서 Cowen이나 trailer와 같은 원본으로 확정된 영상.

**lens-val**
- `train_labels.json`의 마지막 10%다. 위치 규칙은 repo 그대로 [R: JS datasets.py L212-214].
- **수정:** repo는 이 10%를 학습에도 포함한다 [JS vce_dense.py L95] (V). 우리는 학습에서 제외한다.
- lens-train = lens-pool에서 lens-val을 뺀 것.

**VCE-test 11,046:** 렌즈 동결 전에는 열지 않는다. 렌즈 보고와 1막 VCE 측 분해에 쓴다.

### 1.2 Cowen 영상 (Cowen & Keltner 2017 자극; HK와 MC가 본 영상)

**개수:** 2,185 고유 [EmoBrain CONTEXT]. HK 논문은 2,181, MC는 2,180이다. crosswalk는 `AL/data/stimulus_crosswalk.tsv`, `AL/manifests/s2/hk_mc_id_map.tsv` (V).

**MC-72:** MC 시험 영상 72개(`is_mc_test_72`)는 **모든 적합에서 제외**한다. 1막 분해, 2막 encoding, 3막 decoder, g_Scap 모두 포함이다. MC-72는 4막 최종 외부 검정에만 쓴다.

**자극 측 분할 (뇌 없음, 1막)**
- EmoBrain 정본 1748/217/220에서 MC-72를 뺀 것을 쓴다 [R: project/shared/data/horikawa_split.csv].
- 이 test는 과거 뇌 디코딩 수치에만 쓰였고, 이번 분해 질문으로는 열린 적이 없다.
- 강건성으로 train+val 안에서 10-fold CV를 추가 보고한다 [P: Kragel et al. 2019 10-fold].

### 1.3 HK (Horikawa, Cowen, Keltner & Kamitani 2020, iScience)

**voxel 수준 (2막, 3막 주분석)**
- 파일: `fmri_Subject{1..5}.h5`, `EmotionMovie_fmriprep_volume_native` [R: HKpy config yaml L15-33] (V). 위치는 NERSC다.
- 표본 정의: 4 s shift 후 영상 구간 평균 [P: H20 L19].
- ROI: HCP-MMP 360 + 피질하 10 [R: HKpy roi_set/wholebrain.yaml].

**ROI-mean 수준 (4막 피험자 간 전이)**
- Schaefer-400 + Tian-S3 50 = 450, 피험자별 [R: EmoBrain project/data/fmri_adapter.py L1-11, L41-44].
- README에는 "5명 평균"이라고 적혀 있지만 loader는 피험자별이다. 피험자별을 쓴다.

**분할: AffectLab `hk_dev_v4`**
- 6 fold, 각 회전에서 4 train / 1 val / 1 test, run 단위, MC-72 내용 제외 [R: AL/src/crossmodal_emotion/fold_plan.py L10-20, L45-47, L55-61].
- 같은 stimulus_name을 공유하는 train 표본은 버린다 [R: HKpy yaml `exclusive_key: stimulus_name`].
- 같은 라벨의 test 표본은 평균한다 [R: FD cv_predict_feature_fastl2lir.py L153-157].

**기존 1748/217/220 분할과의 관계**
- 기존 분할은 R0 = 0.294 (34-d) 재현에만 쓴다. 연속성 확인용이다.
- 새 HK 분석은 전부 hk_dev_v4 6-fold 회전으로 한다. 자극마다 피험자별 out-of-fold 예측이 정확히 1개씩 생긴다.

**확증 지위**
- HK test 데이터는 이미 다른 분석에서 열람됐다. fold 1도 이미 보였다 [AL EXPLORATORY_SWEEP L38-40].
- 따라서 HK 결과는 "사전등록된 탐색"으로 표기한다.
- 확증 주장은 VCE-test, V2V listwise, MC-72, Emo-FilM에 둔다.

### 1.4 MC (Horikawa 2025, Sci Adv, "Mind captioning")

- 6명. 학습 지각 2,108 표본은 **사용 금지**(AffectLab 규칙).
- test 지각 72 x 5, test 심상 72 x 5 [MCR data/README L12-14] (V).
- 저자 전처리를 그대로 쓴다: 4 s shift, despike, 블록평균, run 내 z [P: Horikawa 2025 L178-186]. 추가 정규화는 하지 않는다.
- 공간: `spaceDefine_S*.nii`(native). T1은 OpenNeuro ds005191 (I).

### 1.5 Emo-FilM (Morgenroth et al. 2025, Sci Data)

**주석:** ds004872, 로컬에 있음 (V).
- 14편 x 1 Hz, 50 항목. 그중 마지막 13 열이 이산 감정이다 (I, 열 순서 기반).
- `C_Annot_FILMS_stim.tsv.gz`, 9,600 행 (V).

**fMRI:** ds004892, 30명, TR 1.3 s, 소리와 함께 시청 (V).
- 필요한 것: `derivatives/preprocessing/space-MNI_desc-ppres` 450 파일, 358.7 GB (V).
- 전처리: FSL FEAT, 6 mm 평활, WM/CSF/motion 회귀 (V).

**영상:** `ds004892/code/FilmInfo.txt`의 출처(Vimeo id, 공식 사이트)에서 받는다. `BBL_experiment_Movies_without_credits_exp_files.xlsx`의 시작/끝 초로 자른다 (V, §R4 표).

### 1.6 중복 검사 (Cowen vs VCE, Cowen vs trailers, VCE vs trailers)

**목적:** 렌즈가 Cowen 영상을 학습에서 본 적이 없음을 보장한다. 중복이 확인되면 VCE 쪽 영상을 lens-pool에서 뺀다.

1. **프레임 추출.** 모든 영상에서 1 fps와 첫/중간/끝 프레임을 뽑는다 [D6.1, 제안 1 fps]. 검은 레터박스는 행/열 평균 휘도가 0에 가까운 테두리를 잘라 제거한다.
2. **pHash.**
   - `imagehash.phash`, hash_size 8 (64-bit DCT) [R: imagehash 기본값, clone 후 확인 필요 (U)].
   - 좌우반전 프레임도 hash해서 둘 중 작은 Hamming 거리를 쓴다.
   - 영상 쌍 점수 = 프레임 쌍 최소 Hamming 거리.
3. **임베딩 최근접.**
   - S-vis 계산에 쓰는 PE-Core G14-448 `encode_image` 프레임 임베딩(L2 정규화)의 cosine.
   - 영상 쌍 점수 = 프레임 쌍 최대 cosine. Cowen 약 1.5만 프레임 x VCE 약 70만 프레임은 GPU 행렬곱 한 번이다.
4. **임계값 보정 (데이터로 결정).**
   - 양성 대조: Cowen 영상 500개 [D6.2]를 VCE 형식으로 재인코딩한다(H.264, 256x320 [VCE metadata 예시 (V)]). 여기에 무작위 crop(면적 10% 이내 [D6.2]), 밝기 변화, 좌우반전을 준다.
   - 음성 대조: 무작위 Cowen x VCE 쌍.
   - τ_H(pHash), τ_E(cosine) = 양성 대조의 99%를 잡는 값으로 정한다 [D6.2, 제안 99% 재현율].
   - 후보 = 두 기준 중 하나라도 넘는 쌍의 합집합. 관대하게 잡고 정밀도는 사람 확인으로 확보한다.
5. **수작업 확인.**
   - 평정자 2명이 각 후보 쌍을 4프레임 스트립 두 줄로 나란히 본다.
   - 판정: {같은 원본 영상 / 같은 사건, 다른 촬영 / 무관}. 불일치는 합의로 정하고 Cohen's kappa를 보고한다.
   - 후보가 2,000개를 넘으면 점수순으로 확인하고, 연속 200개가 "무관"이면 멈춘다 [D6.3].
6. **조치.** "같은 원본"이면 VCE 영상을 lens-pool에서 제외한다. 제외 수와 Cowen 측 해당 자극 목록을 보고한다. 1막 Cowen 결과는 해당 자극을 제외한 민감도 분석도 함께 낸다.

### 1.7 34 -> 27 규칙과 라벨 변환

**34 -> 27:** Cowen 34에서 contempt, disappointment, envy, guilt, pride, sympathy, triumph를 뺀다 [VCE 27 정의 (V)].
- 이름 대응: awe <-> "Awe (or Wonder)". 나머지 26개는 대소문자만 다르다.
- 순서는 양쪽 모두 알파벳순이다 [R: JS vce.py; HKpy data/README L48-104].
- 34-d는 Horikawa 2020 재현에만 쓴다.

**라벨 변환**

| 대상 | 변환 | 출처 |
|---|---|---|
| Cowen 27 평정 | log1p 후 train fold 통계로 z | [R: EmoBrain project/README log1p_z] |
| Cowen 14 차원 | train fold 통계로 z | 같은 규칙 |
| VCE 라벨, 렌즈 학습 | 원값 0-1 그대로, BCE target | [R: JS run_class_finetuning.py L455] |
| VCE 라벨, 분석 | VCE lens-train 통계로 감정별 z | 같은 규칙 |
| 렌즈 출력 | sigmoid 이전 logit, lens-val logit 통계로 감정별 z | 고정 상수. Cowen 정보 미사용 |

**자극 간 거리 지표**는 열린 사항이다(CONTEXT). §6 D6.4에서 원리로 정하고, 본문에는 두 지표를 모두 보고한다.

---

## 2. 모델 사양

### 2a. 정서 렌즈 (주 모델): VCE 저자 fork, JunShern/VideoMAE

| 항목 | 값 | 출처 |
|---|---|---|
| backbone | ViT-B/16 (768 / 12 / 12), tubelet 2, token mean pooling + fc_norm | [R: JS finetune_vce.sh `--model vit_base_patch16_224`; run_class_finetuning.py L37, L130-131] |
| 초기화 | K400 ViT-B 1600 epoch self-supervised **pretrain** (gdown 1tEhLyskjb755TJ65ptsrafUG2llSwQE1). K400 fine-tune 판이 아님 | [R: ED README L149-154; JS MODEL_ZOO L9] |
| head | Linear 768->27, init_scale 0.001 | [R: L130] |
| 학습 입력 | 16 frames, 224x224, VideoClips frame_rate 4 (약 4 s 창), 영상당 무작위 clip 1개 | [R: datasets.py L190-204; vce_dense.py L113-118] |
| 증강 | RandAug `rand-m7-n4-mstd0.5-inc1`, RandomResizedCrop scale 0.08-1 / ratio 0.75-1.333, hflip, random erasing 0.25 | [R: L89, L103; vce_dense.py L198-257] |
| mixup / cutmix / smoothing | 실효 off (호출 주석 처리). 그대로 둔다 | [R: engine_for_finetuning.py L59-60] |
| loss | BCEWithLogits, 27 soft target | [R: L455] |
| optimizer | AdamW, betas 0.9/0.999, eps 1e-8, wd 0.05 고정, layer decay 0.75, drop_path 0.1, grad clip 없음 | [R: L45, L56, L60, L72; finetune_vce.sh] |
| lr | base 5e-4 x (total batch / 256). 1 GPU x 8이면 1.5625e-5 | [R: L398-402; finetune_vce.sbatch GPUS=1] |
| schedule | iteration 단위 cosine, warmup 5 epoch (1e-6에서 시작), min 1e-6 | [R: L74-79, L445-447] |
| epochs / batch | 50 / 8 per GPU. GPU를 늘리면 repo의 선형 스케일 규칙이 자동 적용된다 | [R: finetune_vce.sh] |
| early stopping | 매 epoch lens-val 평가. 27 감정별 Pearson r(영상 간)의 평균이 최대인 epoch를 고른다. 50 epoch는 다 돈다 | **수정.** repo는 argmax top-1로 평가하는데, top-1은 프로젝트 규칙상 금지다. 선택 대상: [V: epoch 1-50] |
| VCE-test 평가 | 2 temporal segments x 3 spatial crops, logit 평균 | [R: test_num_segment 2, test_num_crop 3; engine L274-281] |
| 외부 영상 추론 | (a) repo test 경로(native frame 4개마다 1개, 2 seg x 3 crop) 또는 (b) 학습과 같은 4 fps 16-frame 창을 1 s 간격으로 밀고 3 crop, 시간 평균 | [V: lens-val에서 a/b 선택]. 학습과 test의 시간 척도가 다르다(4 fps vs 7.5 fps)는 점은 코드에서 추론했다. 1 Hz 곡선(trailer, Emo-FilM)은 항상 (b) [P: Emo-FilM 1 Hz 주석 해상도] |
| 출력 | 27 logits (분석용), fc_norm 768 (3막 decode 대상), 12 block token-mean (2막) | 구조 사실 |
| seed | 주 렌즈 = 2막 E arm의 seed 0 | 추가 seed 수: [D6.5] |

**repo 대비 수정 (작은 조정 4개, 구조 변경 없음)**
1. lens-val을 학습에서 분리한다.
2. 선택 지표를 연속 r로 바꾼다.
3. V2V와 중복 영상을 제외한다.
4. 27-d logit을 저장한다. repo도 `{rank}.txt`에 저장한다 [engine L199-205].

**민감도 렌즈 B: V-JEPA 2.1 ViT-L/16 384 (`vjepa2_1_vitl_dist_vitG_384.pt`), encoder 동결**
- 용도: 1막 결과가 backbone에 의존하지 않는지 확인.
- 이 repo에는 full fine-tune 스크립트가 없다 (V). 그래서 frozen probe를 쓴다.
- probe: AttentiveClassifier depth 4, heads 16 (self-attention 3 + cross-attention 1, query 1) [R: VJ configs/eval_2_1/vitl-384/k400.yaml; src/models/attentive_pooler.py].
- 데이터: 16 frames, frame_step 4, 8 segments x 3 views, 384 [R: 같은 yaml].
- 학습: 20 epochs, bf16, batch 4. 20 head를 병렬로 학습한다: lr {5e-3, 3e-3, 1e-3, 3e-4, 1e-4} x wd {0.01, 0.1, 0.4, 0.8}, warmup 0, final lr 0 [R: 같은 yaml]. 20개 중 1개는 [V: lens-val 평균 r].
- 수정: loss를 CE에서 BCEWithLogits(27)로 바꾸고, view 집계를 softmax 평균에서 logit 평균으로 바꾼다.
- 주의: torch hub URL이 localhost로 되어 있다 [VJ src/hub/backbones.py L8-11]. 가중치는 `torch.load(...)["ema_encoder"]`로 직접 읽는다 [R: eval_2_1 `checkpoint_key: ema_encoder`].

### 2b. 정보 수준 특징 (전부 공개 모델, 동결, git clone)

| 수준 | 추출기 | 층 / 출력 | 프레임과 시간 pooling | 차원 | 출처 |
|---|---|---|---|---|---|
| **L-me** | pymoten `get_default_pyramid` | `project_stimulus`, quadrature `sqrt_sum_squares` 후 `log_compress` | 휘도: `video2luminance`, size (72,128) [R: PM demo_batching.py]. fps 24로 재표집 [R: PM __init__ L21-51]. `filter_temporal_width` auto = 16 [R: pyramids.py L132-134]. 경계 패딩 ceil(tw/2) [R: demo_batching]. 영상 내 프레임 평균 [P: H20 블록평균 반응에 대응] | 2530 (16:9) [R: 실행 확인] | 종횡비가 다른 영상의 처리(왜곡 resize vs 16:9 center crop): [D6.6] |
| **L-col** | RGB 색 히스토그램 | 채널별 | 1 fps 프레임 평균 [D6.1] | bin 수 [D6.7] | [P: Kragel et al. 2019 L103]. bin 수는 supplement에만 있다 (U) |
| **O-obj** | timm `eva02_large_patch14_448.mim_m38m_ft_in22k` | pre-logit pooled feature와 21841 logits (softmax 이전) | 25/50/75% 지점 3 프레임 [P: Gao et al. 2025 L175], 3 프레임 평균 [P: Kragel 2019 시간 평균]. 전처리는 timm data config | 1024 (U, config 확인 필요) / 21841 | [R: TIMM eva.py L1669-1678]; 이름 [R: TIMM imagenet_info.py, imagenet22k_synsets.txt] |
| O-obj-Gao | torchvision AlexNet fc8 | 1000 logits | 위와 같음 | 1000 | [P: Gao 2025] 연속성 보조 |
| **O-act** | VideoMAE V2 ViT-B `distill/vit_b_k710_dl_from_giant.pth` | `forward_features` (mean + fc_norm)와 710 logits | 16 frames, sampling_rate 4, 224; test 5 seg x 3 crop 평균 | 768 / 710 | [R: VM2 MODEL_ZOO L35-38; scripts/finetune/vit_b_k710_ft.sh; misc/label_map_k710.txt] |
| **S-cap** (Cowen만) | DeBERTa-large | `hidden_states[1..24]`, 특수 토큰을 뺀 토큰 평균, 캡션별 계산 후 20 캡션 평균 | (텍스트) | 1024 x 24 층 (U) | [R: MCR code/python/util/mcap_utils_demo.py L1034-1059; P: Horikawa 2025]. 층: [V: 24층] |
| S-cap 변형 | 위와 같음 | (i) **noaff**: 정서 어휘집을 캡션에서 지운 뒤 임베딩. (ii) **shuf**: 단어 순서 섞기, 캡션당 최대 1000회 평균. (iii) **bow**: lemma 출현 비율 | | | (ii) [P: Horikawa 2025 L210; Doerig et al. 2025 NMI]. 어휘집: [D6.8] |
| **S-vis** (전 데이터) | PE-Core G14-448 | `encode_video(normalize=False)` = 프레임 `encode_image`의 평균 | 균일 8 프레임 | 1280 | [R: PE pe.py L717-723; apps/pe/clip_benchmark/cli.py L266-267; config.py] |

**S-cap 주의 (D3 계수)**
- 인간 캡션에 감정 단어가 들어 있다: smiling 402, scared 197, laughing 174 등 (V).
- 그래서 1막 headline과 2막 band에는 **S-cap-noaff**를 쓴다. full은 보조로 보고한다.

**S-vis와 S-cap의 관계**
- VCE에는 캡션이 없어서 VCE 측 상황 수준은 S-vis로 대신한다.
- Cowen에서 S-vis와 S-cap-noaff를 RSA와 상호 예측 r로 비교해, 대체의 정도를 숫자로 보고한다.

**모든 특징의 정규화:** 분석 단위의 train fold 통계로 z-score한다 [R: FD cv_train_decoder_fastl2lir.py L194-199].

**readout g_level (3막 경로용, 동결)**
- 각 특징에서 27로 가는 ridge를 VCE lens-train에서 VCE 27 라벨(z)로 학습한다.
- alpha: [V: lens-val, grid logspace(1,6,10); R: MCR code/matlab/util/mcap_setParams.m L37-39 grid].
- 예외: g_Scap은 VCE에 캡션이 없으므로 Cowen train fold 평정으로 학습하고, alpha는 Cowen val로 고른다. 이 경로는 "평정 출처가 다름"으로 따로 표기한다.

### 2c. 학습 목표 대조 모델 (2막)

**공통 조건 (arm 간 동일)**
- 초기화: §2a의 K400 pretrain.
- 데이터: lens-train과 같은 영상, 같은 순서 seed.
- 증강, optimizer, schedule, epochs 50, batch는 모두 §2a와 같다 [R: §2a 표].
- arm 간 차이는 **head 출력 차원과 loss뿐**이다.

| arm | target | head / loss | 근거 |
|---|---|---|---|
| **E** | VCE 27 진짜 라벨 | 768->27, BCEWithLogits | [R: JS] |
| **E-perm** | 27 라벨 벡터를 영상 간에 섞음. seed마다 1회 섞기 | 같음 | 라벨의 주변분포와 공동출현 구조는 유지하고, 자극-라벨 대응만 끊는다. "27-d 다중라벨 학습 자체"의 효과를 통제 |
| **N-act** | 같은 VCE 영상에 대한 VideoMAE V2-B K710 teacher의 710-way softmax | 768->710, soft-target CE | loss: [R: VM2 run_class_finetuning.py L773-777 SoftTargetCE]. 같은 영상(diet)에서 목표만 바꾼다 [P: Conwell et al. 2024 Nat Commun, diet가 지배적이라 diet를 고정] |
| **N-obj** (예산 허용 시) | EVA02-L in22k teacher의 21841-way softmax (3 프레임 평균) | 768->21841, soft-target CE | 위와 같음 |
| base | K400 pretrain, fine-tune 없음 | | 참조점 |

- **checkpoint 선택:** 각 arm이 자기 lens-val loss 최소 epoch를 고른다 [V: epoch 1-50]. 같은 규칙을 모든 arm에 적용한다.
- **seed:** arm마다 같은 seed 집합을 쓴다. 집단 수준 추론의 근거는 [P: Mehrer et al. 2020 Nat Commun]. seed 수는 [D6.5]. SD 추정에 최소 3이 필요하다는 것은 산술이다.
- **분석 특징:** 12 block token mean과 fc_norm, 모두 768. Cowen 영상에서 §2a 추론 규칙으로 뽑는다.

### 2d. 뇌 encoding 모델 (himalaya v0.4.11)

**단일 특징 공간 (2막 arm별 층별)**
- `himalaya.kernel_ridge.KernelRidgeCV(kernel="linear", alphas=np.logspace(1,6,10), cv=<run-grouped 5-fold>)`.
- alpha grid: [R: MCR mcap_setParams.m L37-39]. grid 경계에서 해가 고르면 grid를 확장한다.
- cv 5: [R: HIM 기본값 cv=5]. run 그룹 묶음은 [P: Horikawa 2025 inner CV over runs].

**banded ridge (2막 수준->영역, 4막 in silico)**
- `himalaya.ridge.GroupRidgeCV(groups="input", solver="random_search", solver_params=dict(n_iter=100, concentration=[0.1,1.0], alphas=np.logspace(1,6,10)), cv=<run-grouped 5-fold>)`.
- band 입력은 `ColumnTransformerNoStack`으로 넣는다 [R: HIM ridge/_sklearn_api.py L346, L438-441; _random_search.py L16-23; _column.py L5].
- n_iter와 concentration은 [R: 기본값].

**band 구성**
- 주분석: {L-me, O-obj(pre-logit), O-act(768), S-cap-noaff(층 [V])}.
- VCE 적용용: {L-me, O-obj, O-act, S-vis}.

**표적과 지표**
- 표적: 피험자별 voxel (WholeBrain mask [R: HKpy encoding yaml L28]), train fold 통계로 z.
- 지표: test r(voxel별). band별 분해는 `r2_score_split` (product measure, 합이 joint R²) [R: HIM scoring.py L99].
- 교차확인: Lescroart식 집합 분할(7개 모델 별도 적합, unique와 shared) [P: Lescroart, Stansbury & Gallant 2015 Front Comput Neurosci].
- 해석상 주의: unique 분산의 Type I 오류 [P: Westfall & Yarkoni 2016 PLoS ONE]. 그래서 **shared 성분을 주 결과**로 둔다.

**GPU:** `set_backend("torch_cuda", on_error="raise")` [R: HIM backend].

**집계 단위**
- HCP-MMP 370 영역, 22개 그룹 [R: HKpy wholebrain_demo.yaml L5-26].
- PG1 10분위 [P: H20 Fig. 5H, Margulies et al. 2016 PNAS].
- PG1 지도 출처는 [D6.9]. HK는 피험자별로 미리 계산한 파일을 썼고, repo에는 없다 (V).

**noise ceiling:** HK는 단일 제시라 반복 기반 ceiling이 불가능하다 [P: H20 L117].
- 대용치: ROI-mean 수준 leave-one-subject-out 피험자 간 상관. "ceiling 대용치"로만 표기한다.

### 2e. 뇌 decoder

**종류:** 특징 단위별, ROI별 L2 ridge에 voxel 선택을 결합한 FastL2LiR.
- 근거: [P: Horikawa & Kamitani 2017 Nat Commun "Generic decoding of seen and imagined objects using hierarchical visual features"의 단위별 특징 decoding; Horikawa 2020; Horikawa 2025].

| 항목 | 값 | 출처 |
|---|---|---|
| 구현 | `FastL2LiR(alpha, n_feat)`. 출력 단위마다 train에서 \|Pearson r\| 상위 voxel을 고르고 bias 포함 ridge | [R: FL src/fastl2lir/fastl2lir.py L256-295] |
| X, Y 정규화 | train fold 평균과 SD(ddof=1)로 z | [R: FD cv_train_decoder_fastl2lir.py L194-199] |
| n_feat | ROI당 500 voxel. 500보다 작은 ROI는 전부 | [R: HKpy wholebrain.yaml `num: 500`] |
| alpha | [V: hk_dev val fold, grid logspace(1,6,10)]. 기준: 단위 전체의 평균 profile r | grid [R: MCR mcap_setParams.m L37-39]; 기준 [R: MCR mcap_gen_decoding.m L186-218]. HKpy의 고정 alpha 100은 쓰지 않는다. 원논문도 nested CV를 썼다 [P: H20 L29] |
| 최종 적합 | 선택된 alpha로 train fold에 적합 후 test 예측 | 회전마다 반복 |
| ROI (3막) | 22개 그룹 + 피질하 10 + PG1 10분위 = 42 ROI. 렌즈 fc_norm 경로만 370 영역 전체 | 그룹 [R: wholebrain_demo.yaml]. 분위 [P: H20] |
| 전뇌 decoder | 훈련 내 encoding 정확도 상위 50,000 voxel | [R: MCR mcap_setParams.m L50; mcap_gen_decoding.m L148-163] |
| 피험자 간 전이용 (4막) | ROI-mean 450 -> 특징 또는 27, ridge, voxel 선택 없음, alpha [V: val, 같은 grid] | MC와 Emo-FilM은 voxel 대응이 없어서 ROI 수준이 필수 |

**decode 대상 (3막)**
- 렌즈 fc_norm 768.
- L-me 2530.
- O-obj pre-logit. 복원한 뒤 동결된 EVA head로 21841 logits를 만든다. 4막 Gao 뇌 그림에도 쓴다.
- O-act 768.
- S-vis 1280.
- S-cap-noaff (선택된 층).
- 비교용: 27 평정 직접 decoder.

**MindEye2나 Brain-IT를 주 decoder로 쓰지 않는 이유**
1. Brain-IT(arXiv 2510.25976, ICLR 2026)와 MindEye2(Scotti et al. 2024 ICML)는 NSD **정지 영상**용이다. Brain-IT에는 시간/영상 모듈이 없다 (V, BIT README L73; decoder_models.py).
2. 출력이 CLIP 토큰(256 x 1664)이고 확산 모델로 재구성하는 것이 목적이다. 반면 우리는 **특징 공간 그대로 복원해서 동결 head에 넣는 합성**이 목적이다. 선형 decoder여야 복원 특징의 기하가 원 공간에 남고, 영역별 귀속도 해석할 수 있다.
3. HK는 fold당 약 1.4k 단일 제시 표본이다. 비선형 decoder는 영역 비교 단위(42 ROI x 6 fold x 5명)를 감당하기 어렵다. 로컬에서도 Brain-IT 1 fold에 약 31분이 걸렸다 [AL 1-1_Vision2Affect/README L109].
4. 같은 HK 데이터의 선행 분석이 모두 L2 선형을 썼다 [P: H20; Horikawa 2025]. 비교 가능성이 유지된다.
5. 그래도 둘은 **전뇌 민감도 분석**으로만 보고한다. 로컬 AffectLab에 HK 파일럿이 있다.

---

## 3. 막별 방법

### 3.0 공통 통계

| 항목 | 규칙 | 출처 |
|---|---|---|
| 분석 단위 | 자극(test), 피험자(HK 5 / MC 6 / Emo-FilM 30), seed(2막) | |
| 자극별 예측 | hk_dev_v4 6개 test fold의 out-of-fold 예측을 이어 붙인다. 피험자마다 자극당 1개 | |
| 신뢰구간 | 피험자 x 자극 2요인 bootstrap. 분산 보정식 σ² = 2(σ²_subj + σ²_cond) − σ²_both, 클리핑 포함 | [P: Schütt, Kipnis, Diedrichsen & Kriegeskorte 2023 eLife; R: rsatoolbox `eval_dual_bootstrap`] |
| bootstrap 횟수 | 1000 | [P: Kragel et al. 2019 계수 bootstrap 1000] |
| 영가설 | test 예측의 자극 라벨 순열 1000회 | [P: Gao, Ajith & Peelen 2025 순열 1000] |
| 시계열 영가설 | 원형 이동 (자기상관 보존) | 4막 Emo-FilM. 횟수는 위와 같음 |
| 다중비교 | BH-FDR q = .05. 군은 ROI x 감정 | [P: Gao 2025 FDR] |
| "차이 없음" 주장 | TOST. SESOI = 같은 조건 seed 간 SD로 사전 고정 | [P: Lakens 2017 SPPS]. SESOI 규칙은 [P: Mehrer 2020]의 seed 변동을 척도로 쓴 것 |
| 가중치 해석 | Haufe 활성 패턴, 감정별 단일 출력형 a_e = Cov(X, ŷ_e) / Var(ŷ_e) | [P: Haufe et al. 2014 NeuroImage]. 원문 표기 Σ_ŷ는 (I). 단일 출력이면 척도만 달라 순위는 같다 |
| 정확도 숫자 | 구성 타당도 확인으로만 쓴다. headline은 분해 결과 | 프로젝트 규칙 |

### 3.1 1막: 자극 -> 정서 (AffectProcess 축)

**질문.** 독립된 영상과 독립된 평정자로 학습한 렌즈가 Cowen 영상의 감정 프로파일 구조를 재현하는가? 그 구조를 실어 나르는 것은 저수준, 대상, 상황 중 어느 수준인가?

**입력 -> 출력.** 영상 -> {렌즈 27, L/O/S 특징}. 평가 기준은 Cowen 27 평정과 VCE-test 27 라벨이다.

**절차**
1. **렌즈 보고 (VCE-test).** 감정별 r(영상 간)과 영상별 profile r(감정 간). 둘 다 감정별 z 이후에 계산한다.
2. **동결 전이 (Cowen, MC-72 제외).** 렌즈 27 vs Cowen 27을 본다.
   - 감정별 r 27개. FDR을 적용한다.
   - 영상별 profile r.
   - RDM 대 RDM의 Spearman. 거리 지표는 [D6.4].
3. **수준 분해 (Cowen).** banded ridge, bands {L-me+L-col, O-obj+O-act, S-cap-noaff}.
   - 표적 T1 = Cowen 27 평정. T2 = 렌즈 27 출력(렌즈가 무엇을 배웠는지).
   - 1748/217/220(MC-72 제외)에서 train으로 적합, val로 층과 변형 선택, test로 보고.
   - 출력: band별 split R²(product measure). 7개 모델 집합 분할로 unique와 shared를 구한다.
4. **수준 분해 (VCE).** 같은 분석을 VCE에서 한다. bands {L, O, S-vis}. lens-train으로 적합, lens-val로 선택, VCE-test로 보고. N이 11k라 추정이 안정적이다.
5. **상황 수준 사다리.** S-cap full, noaff, shuf, bow 순서로 같은 분해를 한다. 감정 단어, 어순, 단어 구성 각각의 몫을 보기 위해서다 [P: Doerig et al. 2025 NMI 통제 사다리].
6. **렌즈 강건성.** 렌즈 B(V-JEPA 2.1)로 2-3단계를 반복한다.

**통제**
- 표적 순열.
- 저수준만 쓴 모델.
- 감정 어휘 제거(noaff).
- Cowen-VCE 중복 제외 민감도.
- 무음 조건: Cowen은 스캐너에서 무음이었고 렌즈도 영상만 쓴다.

**통계:** 단위는 test 자극. CI는 자극 bootstrap 1000, 영가설은 순열 1000, FDR은 27 감정 군.

**그림**
- A: 감정별 r 막대. 렌즈 -> Cowen과 렌즈 -> VCE-test를 나란히, 순열 영대 포함.
- B: 렌즈 RDM과 평정 RDM. test 자극을 평정 RDM의 계층군집 순서로 정렬해 시각화만 한다. 묶음을 분석에 쓰지는 않는다.
- C: T1, T2별 L/O/S 분할 막대(unique 3, shared 4).
- D: Cowen 대 VCE의 분할 비율 산점도. 감정별 점 27개.
- E: S 사다리(full, noaff, shuf, bow)의 R² 곡선.

**양방향 해석**
- shared(L∩O∩S)와 O, S가 크다: 대전제 (2)를 지지한다.
- 감정별 unique 잔차가 크다: "환원되지 않는 정서 고유 구조"를 지지한다. 이것도 발표 가능한 결과다.
- 렌즈 전이가 영에 가깝다: VCE와 Cowen의 정서 구조가 자료 특이적이라는 뜻이다. 그러면 3막 경로를 g_level 중심으로 돌린다.

### 3.2 2막: 자극 모델 <-> 뇌 ("brain-like")

**질문.** 같은 모델, 같은 영상에서 목표만 감정으로 바꾸면 어느 영역과 더 닮아지는가? 그 영역은 L/O/S 수준 지도에서 어디에 있는가?

**입력 -> 출력.** arm x seed x 층 특징 -> HK voxel 반응 예측 r.

**절차**
1. §2c의 arm을 학습한다.
2. 피험자별 voxel encoding을 한다(§2d 단일 특징). 층 13개(block 12 + fc_norm) 중 ROI별 최적 층은 [V: val fold] [P: Horikawa 2025 voxel별 최적 층]. test r을 보고한다.
3. 영역 차이 Δ_R = mean_subj(r_E,R) − r_N,R, N ∈ {N-act, N-obj, E-perm, base}. seed는 짝지어 비교한다.
4. **수준->영역 지도.** banded ridge {L, O-obj, O-act, S-cap-noaff}. voxel별 split R²를 PG1 분위별 분포로 표시한다 [P: H20 Fig. 5G/H 형식].
5. **목표 고유분.** band {L, O, S} + {E fc_norm} 대 {L, O, S} + {N-act fc_norm}. 각 arm이 L/O/S 위에 더하는 unique R²를 영역별로 본다.
6. **결합 지표.** ROI 간 상관 corr_R(Δ_E−N-act, S의 split R² 비율). 감정 목표의 이득이 상황 수준이 강한 영역에서 생기는지 본다.

**통제**
- E-perm: 27-d 다중라벨 형식 자체의 효과.
- base: fine-tune의 효과.
- N-act, N-obj: 감정이 아닌 목표.
- 같은 diet, 같은 단계 수.

**통계**
- 단위는 seed, 피험자, 자극이다.
- ROI별 Δ의 CI: seed 재표집과 피험자 x 자극 2요인 bootstrap을 중첩한다.
- FDR은 ROI 군에 적용한다.
- Δ가 작은 영역은 TOST로 "동등"을 검정한다(SESOI = seed 간 SD).

**그림**
- A: arm별 층 x PG1 분위 encoding r 곡선. seed 띠 포함.
- B: Δ_E−N-act 피질 지도. FDR과 TOST 결과를 세 색(E 우위 / 동등 / N 우위)으로.
- C: 수준->영역 지도. voxel별 우세 band를 PG1-PG2 공간에 표시 [P: H20 Fig. 5G].
- D: 목표 고유분 막대(영역 그룹 22개).
- E: Δ 대 S 비율 산점도.

**양방향 해석**
- Δ가 transmodal 쪽에서 양수: 감정 목표가 상위 영역과의 정렬을 만든다(H3 방향).
- 모든 영역에서 동등: 목표가 아니라 diet와 구조가 정렬을 결정한다는 결과다 [P: Conwell 2024]. 이 경우 "감정 학습이 뇌와 닮게 만든다"는 주장을 접고 분해 결과로 보고한다.

### 3.3 3막: 뇌 -> 정서 (EmoBrain 축)

**질문.** 감정 라벨 없이 각 영역에서 복원한 내용 특징(L/O/S)이 동결 렌즈를 거치면 얼마나 감정을 낳는가? 그 양은 감정 라벨로 직접 학습한 decoder와 자극 측 상한에 비해 어디쯤인가?

**경로 (영역 R, 수준 ℓ)**
- **R-lens:** 뇌 -> D_R -> fc_norm^(768) -> 동결 렌즈 head -> 27 logit.
- **R-ℓ:** 뇌 -> D_R -> 특징^_ℓ -> 동결 g_ℓ -> 27. ℓ ∈ {L, O-obj, O-act, S-vis, S-cap-noaff}.
- **Direct:** 뇌 -> 27 평정. 같은 FastL2LiR 규칙.
- **Ceiling:** 같은 test 자극의 진짜 특징을 g_ℓ에 넣은 것, 그리고 렌즈(영상).

**지표**
- 감정별 r(test 자극 간)과 profile r.
- 비율 ρ_med = r(R-ℓ) / r(Direct): 영역의 감정 정보 중 ℓ 내용으로 갈 수 있는 몫.
- 비율 ρ_rec = r(R-ℓ) / r(Ceiling_ℓ): 자극 측 정보 중 그 영역에서 복원되는 몫.
- 출력 텐서: 영역 42 x 수준 6 x 감정 27.

**절차**
1. 피험자별, fold별로 D_R을 적합한다. alpha는 val에서 고른다.
2. decodability(특징 단위별 test r)를 따로 보고한다. 감정과 무관한 양성 대조다.
3. 복원 특징을 head나 g에 통과시킨다.
   - 선형 decoder의 축소 편향은 val fold 복원값으로 추정한 단위별 affine 보정(평균, SD)으로 맞춘다 [V: 보정 유무를 val profile r로 선택].
   - 지표는 상관 기반이라 척도에 덜 민감하다.
4. 34-d Direct를 1748/217/220에서 재현해 R0 = 0.294와 맞는지 확인한다. 연속성 확인용이다.

**통제**
- 순열 decoder: 자극-뇌 대응을 섞어 재적합한다.
- voxel 수 균등(n_feat 500).
- ROI 크기 공변량.
- R-lens 대 R-L의 차이로 "저수준만으로 설명되는 감정"을 분리한다.
- D_R이 감정 라벨을 보지 않았음은 코드 수준에서 보증한다. Y에는 특징만 넣는다.

**통계:** ρ의 CI는 피험자 x 자극 2요인 bootstrap. FDR은 영역 x 감정 군.

**그림**
- A: 영역(PG1 순서) x 수준 열지도 ρ_med.
- B: 같은 형식의 ρ_rec.
- C: 감정 6개 [D6.10]의 영역별 R-lens, Direct, Ceiling 점그림.
- D: decodability 열지도. 감정과 무관한 축이다.
- E: 한 test 영상의 27 막대. 평정, Direct, R-lens, R-S-vis, R-L을 겹쳐 그린다.

**양방향 해석**
- transmodal에서 ρ_med가 높다: 상위 영역의 감정 정보가 상황 내용을 통해 매개된다(H3, H4 방향).
- ρ_med가 낮고 Direct가 높다: 내용 특징으로 환원되지 않는 감정 성분이 그 영역에 있다. 이것도 RQ의 한쪽 답이다.

### 3.4 4막: Kragel식 예측

각 항목의 정확한 설정은 §4에 있다. 여기서는 막 차원의 요약만 둔다.

| 예측 | 새로운 것 | 고정 | readout 학습 | 시연 |
|---|---|---|---|---|
| 4a 새 사람 | MC 6명, 지각과 눈 감은 심상 | HK ROI-mean decoder 전부 | 없음 | §4.5 |
| 4b 새 자극과 새 사람 | Emo-FilM 14편 x 30명, 소리 있음 | 렌즈, HK decoder | 없음. 이름 7개는 직접 대응, 근의어 4개는 사전 표기 | §4.4 |
| 4c 영역 선호 영상 | VCE 61k, 독립 평정 | HK encoding 모델 | 없음 | §4.3 |
| 4d 렌즈 대 Cowen 14 차원 | Cowen 감정 차원 | 렌즈 | PLS 27->14, Cowen 자극 split | 아래 |
| 4e 렌즈 대 V2V 쾌 | 쌍대 선택 | 렌즈 | Bradley-Terry, V2V test 쌍 | §4.6 |

**4d 설정**
- X = 렌즈 27 (Cowen, z). Y = 14 차원, 개별 PLS 1개와 전체 PLS 1개.
- 성분 수 [V: val, grid 1-20]. 상한 20은 [P: Gao 2025 PLSR 20 dims]이다.
- 1748/217/220(MC-72 제외)으로 학습/선택/보고한다. 강건성으로 10회 반복 10-fold를 추가한다 [P: Kragel 2019 IAPS 10 x 10-fold].
- β bootstrap 1000.
- 그림: 감정 27개를 (β_valence, β_arousal) 평면에 찍는다 [P: Kragel 2019 Fig. 2B circumplex 형식].

---

## 4. Kragel / Gao식 시연 세트

### 4.1 Trailer -> 장르 (Kragel 2019 Fig. 3 재현과 확장)

**자극**
- Trailers12k 메타데이터(IMDb와 YouTube id, 장르 10개 다중라벨, 고정 3 fold) (V, CC BY-NC-SA). 원본 mp4는 없다 (V). yt-dlp로 받고 링크 소실 수를 보고한다.
- 장르 정의 (Kragel 3장르, 순수 장르 규칙) [D6.11]:
  - romcom = romance ∧ comedy ∧ ¬(action ∨ horror ∨ thriller)
  - horror = horror ∧ ¬(comedy ∨ romance)
  - action = action ∧ ¬(horror ∨ romance ∨ comedy)
- 단계 1(복제): 장르당 9-10편 [P: Kragel 28편]. 단계 2(확장): 조건을 만족하는 전부. 규모는 [D6.11].
- 오디오 제거. 렌즈는 영상만 쓴다.
- 제목 카드와 자막 프레임은 포함판과 제외판을 모두 낸다 [D6.12].

**특징**
- 렌즈 (b) 경로, 1 s 간격 -> 27 x T.
- trailer당 시간 평균 27 [P: Kragel 시간 평균]. 시간 SD는 보조.

**분석**
- PLS-DA one-vs-all [P: Kragel]. 성분 수 [V: inner CV, grid 1-20].
- outer 10-fold, 장르 층화 [P: Kragel].
- β bootstrap 1000 [P: Kragel]. 순열 10,000 [P: Kragel이 P < 0.0001을 보고했으므로 최소 10^4].
- **주 지표는 장르별 one-vs-rest AUC** [P: Kragel AUC]. 3-way 정확도는 argmax에 기반하므로 보조로만 둔다.
- **분해:** 같은 분석을 렌즈 768, L, O, S-vis로 반복한다. 또 렌즈 27을 L로 잔차화한 것(fold 내 적합)으로도 반복한다. "장르 정보 중 27 감정 병목을 통과하는 몫"을 보기 위해서다.

**통제**
- 중복 검사(§1.6).
- 장르별 평균 휘도.
- 무음이므로 보수적인 검정이다.

**그림**
- A: CC-BY 단편(Sintel, Tears of Steel) [V: FilmInfo]의 27 감정 시간곡선과 프레임 띠.
- B: 장르별 27 β 바이올린 [P: Kragel Fig. 3B].
- C: ROC.
- D: 병목 몫 막대.
- E: 장르 x 감정 Haufe 패턴 열지도.

### 4.2 정서별 top-weight 단어 그림 3종 (Gao 2025 Fig. 3 형식)

**G1. 대상 (VCE)**
- X = EVA02 21841 logits. 보조 X = AlexNet fc8 1000.
- Y = VCE 27 (z). 데이터는 VCE lens-train과 lens-val.
- PLSR 20 성분 [P: Gao], 15-fold [P: Gao 15 fold]. 계수는 fold 평균 [P: Gao].
- 해석 지표는 held-out fold의 Haufe 패턴. 단어 순위도 패턴으로 매긴다. 원 계수 순위는 나란히 보조로 둔다.
- 감정별 상위 10과 하위 10 [P: Gao].
- 안정성: bootstrap 1000에서 상위 10에 든 비율.
- 표본 외: VCE-test r, 그리고 Cowen 27에 재적합 없이 적용.
- 21841 클래스의 근의어 처리(WordNet 상위어로 묶기, 출현 빈도 하한) [D6.13].
- 본문 감정 6개: Gao가 명시한 5개(aesthetic appreciation, craving, horror, sadness, sexual desire)와 1개 [D6.10]. 27개 전부는 보충자료로.
- 예시 프레임: 저작권이 불명이면 CC 대체 이미지를 쓴다 [P: Kragel 관행].

**G2. 상황 단어 (Cowen 인간 캡션)**
- X = 영상별 20 캡션의 lemma 출현 비율. 어휘 하한은 [D6.8]. lemmatizer는 spaCy (버전 U).
- Y = Cowen 27 log1p_z. 분할 1748/217/220(MC-72 제외).
- PLSR 성분 [V: val, grid 1-20]. 계수 안정성은 train bootstrap 1000.
- 사전 등록 사다리:
  - L0 전체
  - L1 정서 어휘집 제거 (**headline**)
  - L2 명사만
  - L3 명사와 동사에서 표정 단어 제외
- 정확한 분해 Cov(ŷ_e, y_e) = Σ_j w_je Cov(x_j, y_e)로 감정별 "정서 단어 몫"을 낸다. 산술 항등식이고 lesion 검정이 아니다.

**G3. 뇌 (영역별 단어 경로)**
- D_R로 EVA pre-logit을 복원하고, 동결 head로 21841 logits를 만든 뒤 G1 지도 W_obj를 적용한다.
- 단어 출현 벡터(G2 어휘)를 FastL2LiR로 직접 복원하고 W_word를 적용한다.
- 영역 R의 단어 j가 감정 e에 기여하는 몫: c_je^R = w_je Cov(d̂_j^R, y_e). test 자극 기준.
- decodability와 가중치를 따로 표시한다.
- 그림: 행 = 영역 그룹(EVC, VSVC, MTC/LTC, TPOJ, IPC, PCC, ACC_mPFC, OPFC), 열 = 감정 6개. 칸마다 기여 상위 5 단어, 색은 decodability. CI가 0을 포함하는 기여는 회색.

### 4.3 영역 선호 VCE 영상 (in silico; Ratan Murty et al. 2021, Jang & Kragel 2025 형식)

**encoding 모델**
- HK에서 band {L, O-obj, O-act, S-vis}로 학습한다. VCE에서 계산 가능한 특징만 쓰고, 렌즈는 넣지 않는다.
- voxel 예측을 ROI(42)별로 평균하고 피험자 평균을 낸다.
- 대상 영역: test r이 순열 영가설보다 크고 FDR을 통과한 ROI.

**예측 집합:** VCE 61,046에서 Cowen 중복을 뺀 전부. 평정은 HK와 독립이다.

**주분석 (연속)**
- ROI 예측 반응과 VCE 27 강도의 Spearman -> 영역 x 감정 지도.
- 영가설:
  - (i) 자극-반응 대응을 섞어 재적합한 encoder. alpha는 따로 선택.
  - (ii) 예측 분산이 같은 무작위 특징 방향.

**몽타주 (예시)**
- ROI별 상위 24 / 하위 24 영상 [D6.14]. 24개 집합의 평균 27 프로파일과, 무작위 24 집합 1000개의 영대를 함께 그린다.
- 목록을 사전등록해서 향후 새 fMRI 검증에 쓴다 [P: Gu et al. 2023 Commun Biol은 새 fMRI로 검증. Ratan Murty 2021은 육안 검증].

**그림:** ROI당 한 줄. 4 x 6 프레임 몽타주(저작권 불명이면 CC 대체), 27 막대와 영대.

**해석:** 모델의 속성이므로 headline에는 쓰지 않는다.

### 4.4 Emo-FilM 감정 곡선 (자극 측, 뇌 측)

**자극 측**
- 렌즈 (b), 1 s 간격 -> 27 x 9,600 s.
- 대응:
  - 직접 7개: Anger, Disgust, Fear, Anxiety, Satisfaction, Surprise, Sad<->Sadness.
  - 근의어 4개(사전 표기): Happiness<->Joy, Love<->Romance, WarmHeartedness<->Adoration, Regard<->Admiration.
  - 대응 없음: Guilt, Pride.
- 주석 지연(lag)은 [V: leave-one-film-out, 범위 D6.15].
- 지표: 영화 x 감정별 r. 영가설은 원형 이동 1000. 상한은 leave-one-rater-out 일치도 (V: 항목당 평정자 3-4명).
- 보조: 27 -> 50 항목 선형지도, leave-one-film-out.

**뇌 측**
- MNI ppres에서 Schaefer400 + Tian50 ROI 평균 시계열을 뽑고, run 내 z를 한다 [P: HK와 MC의 run-z 처리와 같음].
- HK와 같은 표본 정의: 4 s shift [P: H20], 창 길이 5 TR = 6.5 s. 창 길이는 HK 평균 자극 길이 6.61 s에서 유도했다 [P: CONTEXT 6.61 s].
- 1 TR 간격 슬라이딩 창 -> HK ROI-mean decoder(Direct, R-lens, R-ℓ)를 재적합 없이 적용 -> 27 x T.
- 비교: 뇌 곡선 대 주석 곡선, 뇌 곡선 대 렌즈 곡선. 단위는 피험자 30명, 영화 14편.
- 보조 encoding: ROI 시계열 ~ HRF 합성곱한 렌즈 곡선 + "잔차 곡선". 잔차 곡선 = 주석을 렌즈 곡선, 오디오 포락선, L에 직교화한 것. 이렇게 내용분 지도와 잔차분 지도를 그린다. 잔차분 지도의 재현성은 평정자 2 대 2 분할로 확인한다.

**그림**
- A: Sintel 프레임 띠(CC-BY).
- B: 주석 Fear, 렌즈 Fear, 뇌 decoded Fear 세 곡선. 잔차를 음영으로.
- C: 영화 x 감정 r 열지도.
- D: 내용분 / 잔차분 뇌 지도.

### 4.5 MC 재적합 없음 (지각과 심상)

**decoder**
- HK ROI-mean 450 -> {27 Direct, 특징 경로}. MC-72를 제외하고 학습한 것 그대로 쓴다.
- HK ROI-mean은 run-z 파일 [R: AL fold_plan.py `*_blocks_common36_qc_runz.npy`]이라 MC 저자 전처리와 같은 규약이다.

**MC ROI 평균**
- Schaefer와 Tian(MNI)을 각 피험자 native로 옮긴다(ds005191 T1 경유).
- 등록 도구는 [D6.16]. 등록 파라미터는 MC 반응을 보지 않고 해부 영상만으로 정한다.

**표본:** 저자 블록 정의 그대로(test 지각 72 x 5, 심상 72 x 5). 반복은 평균한다 [R: MCR mcap_gen_decoding.m L245-254].

**지표**
- 감정별 r(72 영상), profile r, 72 x 72 RSA.
- 피험자별 방향 일관성(6명 중 몇 명이 양수인가).
- 영역별 심상/지각 비율.

**통제**
- 단서 캡션(고정 1개)의 lemma 벡터에 G2 지도를 적용해 "단서 예측 프로파일"을 만든다. 이것을 부분상관으로 뺀다.
- 감정과 무관한 양성 대조: EVC에서 L 특징 decodability. 파이프라인은 MC를 보기 전에 동결하고, 대조 결과를 보고 수정하지 않는다.

**통계:** 단위는 피험자 6명. 영상 bootstrap 1000, 순열 1000.

**그림**
- A: 피험자 x {지각, 심상} 점그림.
- B: 심상 1회의 decoded 27 막대와 Cowen 프로파일.
- C: 영역별 심상/지각 비율.

### 4.6 V2V 쾌 (보조 시연)

- Bradley-Terry: logistic(f(b) − f(a)), 절편 없음, L2 [V: inner 5-fold, grid logspace(-3,3,13)] [D6.17: grid 근거 없음].
- 적합은 **V2V test 쌍 3,189개**로 한다. 이 영상들은 렌즈 학습에서 빠져 있다.
- 평가는 listwise 1,758 목록(Kendall τ)으로 한다. 손실 형식은 [R: JS run_v2v_finetuning.py L25-88] (V).
- f ∈ {렌즈 27, O, L, S-vis}.
- headline: 27 BT 가중치 막대와 CI. 쾌 축을 Cowen 영상에 재적합 없이 적용해 Cowen valence 차원과 상관을 본다.
- 뇌 경로: R-lens로 복원한 27에 BT 가중치를 적용하고 Cowen valence와 상관을 본다. 영역 지도로 그린다.

---

## 5. 계산 예산과 실행 순서

| 순서 | 작업 | 자원 | 의존 | kill-test (결과를 보기 전에 고정) |
|---|---|---|---|---|
| 1 | 매니페스트: VCE / V2V / MC-72 제외, 34->27, 분할 파일 | CPU | | |
| 2 | 프레임 추출, pHash, PE-Core 프레임 임베딩, 보정, 수작업 확인 | CPU + GPU 1 | 1 | 중복 수를 보고한다(중단 조건 아님) |
| 3 | 렌즈 pilot: E seed 0, 1 epoch 시간 측정 | GPU | 2 | 손실 감소와 lens-val r > E-perm 1 epoch. 실패하면 학습 설정 점검 |
| 4 | 렌즈 E seed 0 전체 50 epoch, 동결 | GPU | 3 | **K-lens:** VCE-test 27 감정 중 FDR 통과가 0이면 렌즈를 폐기하고 원인을 진단한다 |
| 5 | 특징 추출: Cowen, VCE 61k, Emo-FilM, trailer (L-me, O-obj, O-act, S-vis, S-cap) | GPU (pymoten은 `torch_cuda` 가능) | 1 | |
| 6 | 1막 분석 | CPU / GPU 소량 | 4, 5 | **K-transfer:** 렌즈 -> Cowen 감정별 r이 FDR 0개이면 3막을 g_level 중심 경로로 바꾼다 |
| 7 | HK encoding (banded), 수준->영역 지도 | GPU (himalaya) | 5 | **K-enc:** EVC에서 L band test r이 영가설 이하이면 데이터 정렬 버그로 보고 멈춘다 |
| 8 | 3막 decoder (FastL2LiR, 42 ROI x 단위 x 6 fold x 5명), Direct | CPU 대량 | 4, 5 | **K-dec:** EVC L decodability와 R0 재현(0.294 근처)을 확인한 뒤 감정 경로를 연다 |
| 9 | 2막 arm: pilot 2 seed, 이후 확장 | GPU 최대 | 4 | **K-seed:** pilot에서 모든 ROI의 \|Δ\| < seed SD이면 seed를 늘리거나 TOST 동등 보고로 전환한다 |
| 10 | Emo-FilM 다운로드(358.7 GB) 시작 | 디스크 / 네트워크 | 지금 바로 | |
| 11 | 4막: MC (마지막, 1회만), Emo-FilM, 4.3 in silico, 4.1 trailer, 4.6 V2V | CPU / GPU | 8 | MC는 파이프라인 동결 증빙(commit hash)을 남긴 뒤 1회 실행 |

**GPU 소요 순서:** 2막 arm(arm 4개 x seed x 50 epoch) > 렌즈 > EVA02-L 448로 VCE 18.3만 프레임 > PE-Core G > 나머지.
- 시간은 3단계에서 1 epoch를 실측해 정한다. 근거 없는 추정치는 적지 않는다.

**사용자 실행 명령 형식 (스크립트는 작성 예정)**
- `bash /home/user/EmoBrain/project/scripts/lens/train_lens_vce_seed0.sh`
- `bash /home/user/EmoBrain/project/scripts/features/extract_all_features.sh`
- `bash /home/user/EmoBrain/project/scripts/act2/train_arm_E_seed1.sh` (arm, seed별 단일 파일)
- `bash /home/user/EmoBrain/project/scripts/encoding/run_banded_hk.sh`

---

## 6. 미확인 항목과 사용자 결정

### 6.1 이 사양이 의존하는 미확인 사실

- VCE 평정자가 소리를 들었는지; VCE와 Cowen 영상의 실제 중복 (§1.6에서 실측).
- V2V 분할과 VCE train/test가 어떻게 겹치는지. 그래서 V2V test와 listwise 전체를 렌즈에서 뺀다.
- VCE 데이터와 영상의 라이선스 (Drive 폴더 미확인). VCE 학습 체크포인트가 공개됐는지 (없다고 가정하고 직접 학습).
- 모든 가중치 파일의 다운로드 가능 여부. HF와 fbaipublicfiles가 차단되어 있었다.
- 차원값: EVA02-L pre-logit 1024, DeBERTa-large 1024 x 24층.
- imagehash 기본값(hash_size 8). clone 후 확인이 필요하다.
- Kragel의 색 히스토그램 bin 수, PLS 성분 수, 3-way 결정 규칙 (supplement).
- Gao의 fc8 softmax 전/후, 6번째 감정, 그림이 단어인지 이미지인지.
- Haufe 원문의 다중 출력 표기(Σ_ŷ). 이 사양은 감정별 단일 출력형을 쓴다.
- HK Transparent Methods: alpha grid, 앙상블 영역 수, PG 지도 산출법, voxel 수. 데이터는 NERSC에 있다.
- MC alpha grid 충돌(코드 10^1-10^6 vs 논문 10-10^4). 코드 grid를 쓴다. MC 72 ID는 로컬 map에만 있다.
- Emo-FilM 13 이산 감정 열 지정은 열 순서에 근거한다 (I).
- Trailers12k YouTube 링크 소실률. LMTD 원본 호스트는 응답하지 않았다.
- V-JEPA 2.1 hub 버그. 수동 로딩으로 우회한다.
- 인용 중 이번 라운드에서 원문을 재확인하지 않은 것: Scotti et al. 2024 (MindEye2), Margulies et al. 2016, Schaefer 2018 / Tian 2020 / Glasser 2016 아틀라스, VideoMAE (Tong et al. 2022) / VideoMAE V2 (Wang et al. 2023), EVA-02, DeBERTa, Bradley & Terry 1952, Benjamini & Hochberg 1995. 원고에 넣기 전에 확인한다.

### 6.2 사용자 결정 (D 번호)

1. **D6.1** 프레임 표집률 (중복 검사, 색 특징). 제안: 1 fps.
2. **D6.2** 양성 대조 수, 변형 강도, 재현율 기준. 제안: 500개, crop 10%, 99%.
3. **D6.3** 수작업 확인 중단 규칙. 제안: 2,000개 초과 시 연속 200개 음성이면 중단.
4. **D6.4** 감정 거리 지표의 정본. 원리 후보는 둘이다.
   - Euclidean (log1p_z): 강도 정보를 보존한다. 0이 73.8%인 근중립 영상에서 상관 거리가 불안정하다는 점을 고려한 후보다.
   - cosine: 패턴만 본다.
   - 데이터를 보기 전에 정한다.
5. **D6.5** seed 수 (렌즈 추가분, 2막 arm별).
6. **D6.6** pymoten 종횡비 처리 (왜곡 resize 또는 crop).
7. **D6.7** 색 히스토그램 bin 수.
8. **D6.8** 정서 어휘집 목록과 어휘 하한 (S-cap-noaff, G2). 사전등록이 필요하다.
9. **D6.9** PG1 지도 출처와 피험자 공간으로 옮기는 방법.
10. **D6.10** 본문에 올릴 감정 6개 (Gao 5개 + 1, 3막 그림 C).
11. **D6.11** trailer 장르 정의와 규모.
12. **D6.12** 제목/자막 프레임 처리 (주분석은 포함, 제외는 민감도).
13. **D6.13** 21841 클래스 근의어 묶기 규칙.
14. **D6.14** 몽타주 크기. 제안: 24.
15. **D6.15** Emo-FilM 주석 지연 탐색 범위.
16. **D6.16** MC 아틀라스 등록 도구 (ANTs 등).
17. **D6.17** BT L2 grid.

**구조 결정 (기본값을 제안해 둔 것)**
- 3막 ROI 단위: 42 ROI (그룹 22, 피질하 10, PG1 분위 10).
- 2막 N-obj arm 포함 여부 (예산에 따라).
- 자극 측(1막) 분할: 정본 1748/217/220(MC-72 제외). 뇌 분석은 hk_dev_v4. 두 분할을 하나로 통일할지 여부.
- MC 저자 run-z 전처리를 그대로 쓰는 것이 AffectLab 규칙("MC로 정규화 금지")에 맞는지 PI 확인.

### 6.3 인용 (본문 사용분, PubMed 또는 1차 자료 확인)

- Kragel, Reddan, LaBar & Wager 2019, "Emotion schemas are embedded in the human visual system", Sci Adv.
- Gao, Ajith & Peelen 2025, "Object representations drive emotion schemas across a large and diverse set of daily-life scenes", Commun Biol.
- Horikawa, Cowen, Keltner & Kamitani 2020, iScience.
- Horikawa 2025, "Mind captioning", Sci Adv.
- Horikawa & Kamitani 2017, Nat Commun.
- Mazeika et al. 2022, NeurIPS Datasets and Benchmarks (VCE/V2V).
- Morgenroth et al. 2025, Sci Data (Emo-FilM).
- Haufe et al. 2014, NeuroImage.
- Dupré la Tour et al. 2022, NeuroImage.
- Lescroart, Stansbury & Gallant 2015, Front Comput Neurosci.
- Westfall & Yarkoni 2016, PLoS ONE.
- Lakens 2017, SPPS.
- Schütt et al. 2023, eLife.
- Mehrer et al. 2020, Nat Commun.
- Conwell et al. 2024, Nat Commun.
- Doerig et al. 2025, NMI.
- Ratan Murty et al. 2021, Nat Commun.
- Gu et al. 2023, Commun Biol.
- Jang & Kragel 2025, J Neurosci.
- Kriegeskorte, Mur & Bandettini 2008, Front Syst Neurosci.
