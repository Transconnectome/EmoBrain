# 방법 명세 v2 (초안, 2026-11-25)

상태: 초안. 사용자 승인 전이며 커밋하지 않았다. CLAUDE.md v7 과 충돌하는 부분(27차원, 모델의 자리)은 §7 결정 후 `project_decisions.md` 에 기록하고 CLAUDE.md 를 v8 로 올린다.

이력: v1 초안(`review/v1_draft.md`)을 독립 검토 2건(`review/v1_review_rigor.md`, `review/v1_review_compliance.md`)이 공격했고, 그 지적을 반영한 것이 이 문서다. 사실 근거는 `review/v1_verification_facts.md` 에 경로와 줄 번호로 있다. v1 과 충돌하면 v2 가 우선한다. 하이퍼파라미터 출처 표(v1 §2)는 v2 에서 바뀐 항목만 다시 적었다.

표기: [R: 경로] repo 기본값, [P: 인용] 선행연구 값, [V: grid] val 에서 선택, [D-n] 근거 값이 없어 사용자 결정 필요(§7). (V) 1차 확인 / (I) 간접 / (U) 미확인.

---

## 0. 전체 구조

```
[VCE 61,046 영상, 27-d 평균 강도, 독립 평정자]  (Mazeika et al. 2022)
     | 학습 1회, 고정 (Cowen 평정, 뇌를 보기 전)
     v
 정서 렌즈 f = VideoMAE ViT-B/16 (VCE 저자 fork, 구조 그대로)
     영상 16 frames x 224 -> 12 blocks -> token mean -> fc_norm 768 -> Linear 768->27
 정보 수준 특징 (전부 공개 모델, 고정)
     L  pymoten 운동에너지 + 색 히스토그램 + 공간 power spectrum (Kragel 2019 저수준 통제)
     O  O-obj EVA02-L in22k 21,841 named logits / O-obj-Gao AlexNet fc8 1,000 / O-act VideoMAE V2-B K710
     S  S-cap: MC 인간 캡션 DeBERTa-large (Cowen 만) / S-vis: PE-Core G 영상 임베딩 (전 데이터, "언어정렬 시각")
 수준별 렌즈 g_l : 특징_l -> 27, VCE 에서 ridge 학습 후 고정

HK 뇌 (5명, 피험자별)
 encoding : 특징 --(himalaya banded / kernel ridge)--> voxel           (2막, 4막 in silico)
 decoder  : ROI voxel --(FastL2LiR, 출력별 voxel 500 + L2)--> 27-d 목표  (3막)
            목표 = (a) 렌즈 출력 f(x) (b) 수준별 렌즈 g_l(x) (c) Cowen 평정 (Direct)
 4막      : HK 에서 고정한 decoder / encoding 을 MC, Emo-FilM, VCE, 예고편에 재적합 없이 적용
```

| 막 | 고정 | 학습 | 확증 / 탐색 |
|---|---|---|---|
| 1 자극->정서 | 렌즈, 특징 추출기, g_l | 수준 분해 ridge, 14차원 PLS (hk_dev_v4 회전 안) | VCE-test 확증, Cowen 탐색 |
| 2 자극모델<->뇌 | 특징, HK | 목표만 다른 arm x seed, arm별 encoding | HK 탐색 |
| 3 뇌->정서 (H4) | 렌즈, g_l | ROI별 decoder (사람 평정 안 봄) + Direct | HK 탐색, MC/Emo-FilM 확증 |
| 4 예측 | 3막 decoder, 렌즈, encoding | 외부 라벨 readout 만 (장르 PLS-DA, BT, 14차원 PLS) | 외부 자료 |

원칙
1. 렌즈와 g_l 은 Cowen, HK, MC, Emo-FilM 의 어떤 라벨도 보지 않는다.
2. 3막 경로 decoder 는 사람 평정을 보지 않는다 (목표가 모델 출력). "VCE 정서로 학습된 모델 출력"을 목표로 한다는 점은 명시한다.
3. MC 반응은 학습, 선택, 정규화, 정렬, 보정에 쓰지 않는다. 파이프라인 commit hash 고정 후 1회 실행.
4. 출력은 모두 연속 27-d. top-1, 임계값, 범주 묶기 없음. 외부 비정서 라벨(장르, 선호 쌍)은 readout 대상일 뿐이다.

---

## 1. 데이터와 분할

### 1.1 단일 분할 (v1 치명 F1 수정)
- Cowen 쪽 모든 분석과 HK 분석은 AffectLab `hk_dev_v4` 하나만 쓴다. video_id 단위 6 fold, 피험자 공통, MC-72 내용 제외 [R: AffectLab/src/crossmodal_emotion/fold_plan.py L31-48] (V).
- 회전마다 4 fold 학습 / 1 val / 1 test. Cowen 평정을 쓰는 모든 객체(14차원 PLS, G2 단어 지도, S-cap 층 선택, 어휘 하한, affine 보정 선택, Direct decoder)는 회전 안에서 다시 적합한다.
- 보고: test fold out-of-fold 예측. 상관은 fold 안에서 계산 후 Fisher z 평균 (v1 m1).
- EmoBrain 1748/217/220 은 valence/arousal 4분위 층화 분할이라 평정이 분할 생성에 쓰였다 [R: project/shared/code/build_canonical_split.py L59-92] (V). R0 = 0.294 재현(데이터 무결성 확인)에만 쓴다.
- 누수 단위 시험: 어떤 평정 적합 객체의 학습 ID 집합에도 해당 회전 test ID 가 없음을 assert (fold_plan.py L39-40 의 MC 보호 assert 패턴 재사용).

### 1.2 VCE
- 61,046 (train 50,000 / test 11,046), 27 강도 0-1, `emotions` dict, 알파벳순 로딩 [R: ED README; JS vce.py L58-63] (V).
- 첫 작업: Drive 다운로드, checksum, 개수, 총 길이, 라이선스 확인. 라이선스 확인 전에는 VCE 프레임을 그림에 쓰지 않는다.
- 렌즈 풀 = VCE-train 에서 (a) V2V test 6,223 과 listwise 4,322 영상 (b) 중복 군집 정리 결과 제외.
- lens-val = 중복 군집 정리 후 seed 고정 무작위 10% (v1 M11). repo 는 마지막 10% 를 val 로 쓰면서 학습에도 넣는다 [R: JS datasets.py L212-214; vce_dense.py L95] (V). 둘 다 수정.
- VCE-test 는 렌즈 고정 전에는 열지 않는다. repo 는 학습 끝에 VCE-test 를 자동 평가한다 [R: JS run_class_finetuning.py L529-530] (V): 비활성화 패치.

### 1.3 중복 검사 (VCE 내부, VCE-Cowen, VCE-예고편, Cowen-예고편)
1. 1 fps 프레임 + 첫/중간/끝 [D-1]. 레터박스 제거.
2. pHash: imagehash `phash`, hash_size 8 [R: imagehash `__init__.py` L259] (V). 좌우반전 포함 최소 Hamming.
3. 임베딩: PE-Core L14-336 프레임 임베딩 cosine 최대값 (G 보다 약 8배 저렴, 검토 추정).
4. 임계값: Cowen 500개 [D-2] 를 VCE 형식으로 재인코딩 + crop/밝기/반전 변형 = 양성 대조, 무작위 쌍 = 음성 대조. 양성 재현율 99% [D-2] 지점.
5. 후보는 평정자 2명이 {같은 원본 / 같은 사건 다른 촬영 / 무관} 으로 판정, kappa 보고.
6. VCE 내부 중복은 군집으로 묶어 한 분할에만 둔다. Cowen 과 같은 원본인 VCE 영상은 렌즈 풀에서 제외.

### 1.4 34 -> 27, 라벨
- Cowen 34 에서 contempt, disappointment, envy, guilt, pride, sympathy, triumph 제외. 이름표로 대응 (awe <-> "Awe (or Wonder)") 하고 코드에서 assert.
- 34-d 는 Horikawa 2020 재현에만 쓴다.
- 구성개념 차이 명시: VCE = 고른 정서의 평균 강도, Cowen = 그 정서를 고른 평정자 비율.
- Cowen 27: 회전 train 통계로 z. 감정별 비영(非零) 자극 수를 fold 마다 보고하고, 최소 개수 미만 감정은 감정별 추론에서 뺀다 [D-3]. Pearson 과 Spearman 병기.

### 1.5 HK 입력 통일 (v1 C3 수정)
- voxel 수준: Kamitani h5 (`fmri_Subject{1..5}.h5`) [R: HKpy config] (V) 와 AffectLab qc_rows 사이 crosswalk 를 만들고 단위 시험한다.
- ROI 수준(4막 전이용): AffectLab `*_blocks_common36_qc` 에서 MC 와 같은 순서(4 s shift -> despike -> block 평균 -> run-z -> ROI 평균)로 다시 만든다. EmoBrain roi_mean(시간 평균, 전체 데이터 정규화)은 전이에 쓰지 않는다.
- ROI 단위: HCP-MMP 22 그룹 + 피질하 10 + PG1 10분위(구획 평균 PG1 값으로 구획을 분위에 배정, Margulies et al. 2016 지도 출처 확인 필요 [D-4]) = 42.

### 1.6 MC
- test 지각 72 x 5, 심상 72 x 5 (V). 학습 지각 자료는 쓰지 않는다.
- 저자 배포 전처리(run-z 포함)를 "배포된 자료"로 쓰는 것은 PI 판정 [D-5].
- HK 와 MC 피험자 동일인 여부 확인 (ds005191 participants.tsv 대조 또는 저자 문의). 동일인이 있으면 "새 사람" 주장에서 뺀다.

### 1.7 Emo-FilM
- 주석 ds004872 (로컬), fMRI ds004892 30명, TR 1.3 s, 소리 있음 (V). 필요한 MNI 전처리 파생본은 358.7 GB (검토 집계). CONTEXT 의 약 132 GB 와 다르다.
- 영화 14편 확보 가능성을 먼저 확인한다. 일부는 NC 라이선스, 일부 호스트 응답 없음 (검토). 확보 실패 시 확보된 편수로 분석을 사전 선언한다.
- 13 이산 정서 열 이름은 Supplementary Table 1 로 확인한 뒤 쓴다 (현재 열 순서 추론, I).

---

## 2. 모델

### 2a. 정서 렌즈: JunShern/VideoMAE (VCE 저자 fork), 구조 변경 없음

| 항목 | 값 | 출처 |
|---|---|---|
| backbone | ViT-B/16, tubelet 2, token mean + fc_norm, head Linear 768->27 (init_scale 0.001) | [R: JS finetune_vce.sh; run_class_finetuning.py L37, L130-131] |
| 초기화 | K400 ViT-B 1600 epoch 자기지도 pretrain | [R: ED README L149-154; JS MODEL_ZOO L9] |
| 학습 입력 | 16 frames, 224, VideoClips frame_rate 4 (약 4 s), 영상당 무작위 clip 1개 | [R: JS datasets.py L190-204; vce_dense.py L113-118] |
| 증강 | RandAug rand-m7-n4-mstd0.5-inc1, RandomResizedCrop 0.08-1, hflip, random erasing 0.25. mixup/cutmix 실효 off 그대로 | [R: L89, L103; engine_for_finetuning.py L59-60] |
| loss | BCEWithLogits, 27 soft target | [R: L455] |
| optimizer | AdamW (0.9, 0.999), wd 0.05, layer decay 0.75, drop_path 0.1 | [R: L45, L56, L72] |
| lr | 5e-4 x total_batch/256. **GPU 수를 모든 run 에서 고정**하고 update_freq 로 total batch 를 맞춘다 | [R: L398-402] |
| schedule | iteration 단위 cosine, warmup 5 epoch, min 1e-6 | [R: L74-79, L445-447] |
| epochs | 50, **최종 epoch 체크포인트 고정** (모든 run 동일 규칙). lens-val 의 감정별 r 곡선은 점검용 기록만 | v1 M3/F3e 수정 |
| 짧은 영상 | 학습: repo 규칙(4 s 미만 제외)대로 두고 제외 수 기록 [R: vce_dense.py L362-366]. 추론: repo test 경로의 마지막 프레임 반복 패딩 [R: vce.py L262-263]. Cowen 4 s 미만 제외 민감도 | 검토 H6 |
| VCE-test 평가 | 2 temporal x 3 spatial, logit 평균. 별도 평가 스크립트로 1회 | [R: evaluate_vce.sh; engine L274-281] |
| 외부 영상 | 학습과 같은 4 fps 16-frame 창을 1 s 간격으로 밀고 3 crop, logit 시간 평균 (1 Hz 곡선 필요 시 시간 평균 생략) | 학습 시간 척도와 일치 |
| 출력 | 27 logits, fc_norm 768, 12 block token-mean | |
| 패치 (작은 조정) | (1) 학습 중 VCE-test 평가 끔 (2) acc1 기반 best 저장 제거 (3) lens-val 분리 (4) 27 logit 저장 | 검토 C2 |

렌즈 B (최신성 확인용): V-JEPA 2.1 고정 encoder + repo AttentiveClassifier (depth 4, heads 16, query 1) [R: vjepa2 configs/eval_2_1; src/models/attentive_pooler.py] (V). loss 만 CE -> BCEWithLogits(27), view 집계 logit 평균. 비용 때문에 ViT-L/384 를 2 segment 로 쓰거나 ViT-B/384 로 바꾼다 (8 segment ViT-L 은 단일 최대 GPU 작업, 검토 추정 75-100+ A100-h). 1막 결론은 두 렌즈에서 모두 성립할 때만 주장한다 (v1 M12).

### 2b. 정보 수준 특징

| 수준 | 추출기 | 출력 / pooling | 출처 |
|---|---|---|---|
| L-me | pymoten default pyramid, luminance (72,128), 24 fps 재표집, sqrt_sum_squares + log_compress, 영상 내 평균 | 2,530 | [R: pymoten demo_batching, pyramids.py] |
| L-col / L-sps | RGB 색 강도 히스토그램, 공간 power spectrum | bin [D-6] | [P: Kragel et al. 2019 저수준 특징] |
| O-obj | timm `eva02_large_patch14_448.mim_m38m_ft_in22k`, pre-logit + 21,841 logits(softmax 전) | 25/50/75% 지점 3 프레임 평균 | [R: timm eva.py L1669-1678]; 프레임 규칙 [P: Gao et al. 2025] |
| O-obj-Gao | AlexNet fc8 1,000 logits (Gao 연속성 확인용) | 같은 3 프레임 | [P: Gao et al. 2025] |
| O-act | VideoMAE V2-B `vit_b_k710_dl_from_giant.pth`, fc_norm 768 + 710 logits | 16 frames, sampling 4 | [R: VideoMAEv2 MODEL_ZOO L35-38] |
| S-cap | MC 저자 배포 DeBERTa-large 특징 (layer01..24) 사용, 일부를 재계산해 대조. 변형(noaff, 무작위 삭제, shuf, bow)만 새로 계산 | 20 캡션 평균 | [R: MindCaptioning 배포 특징; P: Horikawa 2025] |
| S-vis | PE-Core G14-448 `encode_video` (프레임 임베딩 평균), 균일 8 프레임 | 1,280 | [R: perception_models pe.py L717-723] |

- 이름은 측정이 아니다 (v1 F2g). 수준 이름의 수렴/변별 타당도를 먼저 보고한다: L 은 영상 저수준 통계를 S 보다 잘 예측, O-obj 는 캡션 명사 출현을 L 보다 잘 예측, S-vis 는 S-cap 을 O 이상으로 예측.
- S-cap-noaff 의 통제: 같은 개수의 비정서 토큰을 품사, 빈도 맞춰 지운 무작위 삭제판. 정서 고유 몫 = (full - noaff) - (full - 무작위 삭제) (v1 M9). 정서 어휘집 [D-7].
- g_l: 각 특징 -> VCE 27 (z) ridge, lens-train 적합, alpha 는 lens-val grid logspace(1,6,10) [V; grid R: MindCaptioning mcap_setParams.m L37-39]. g_Scap 은 VCE 에 캡션이 없어 만들지 않는다 (v1 의 Cowen 학습 g_Scap 폐기: 누수 경로).

### 2c. 2막 학습 목표 대조 (v1 F3 재설계)

공통: 초기화, 영상, 증강, optimizer, GPU 수와 total batch, 50 epoch, 최종 체크포인트가 모든 arm 에서 같다.

| arm | 목표 | head / loss | 역할 |
|---|---|---|---|
| **E** | VCE 27 진짜 라벨 | 768->27 BCE | 주 대조 |
| **N-27** | VideoMAE V2-B K710 teacher logits 를 lens-train 에서 27 PC 로 축소 -> 정서 라벨 상관행렬의 Cholesky 인자로 섞음 -> 각 차원을 E 라벨 주변분포로 quantile 변환 | 768->27 BCE | 주 대조. 차원, loss, head, 주변분포, 상관구조, 영상이 같고 내용만 다름 |
| E-perm | 27 라벨 벡터를 영상 간 순열 (seed 별 1회, val 도 같은 순열) | 768->27 BCE | 열화 참조 |
| N-act-710 | teacher 710-way soft target | 768->710 soft CE [R: VideoMAEv2 run_class_finetuning.py L773-777] | 보조 |
| base | fine-tune 없음 | | 변화량 기준 |

- seed: E 와 N-27 각 5 이상 (주 대조), 나머지 3. 먼저 2 seed 파일럿으로 효과 크기와 seed 분산을 본 뒤 확정 (K-seed). 근거: 같은 구조 다른 seed 의 표상 차이 [P: Mehrer et al. 2020 Nat Commun], 같은 구조 다른 과제 학습 비교의 선례 [P: Dobs et al. 2022 Sci Adv].
- 변화량 공변량: Cowen 영상에서 block 별 base 대비 linear CKA. layer decay 0.75 때문에 변화가 상위 block 에 몰리므로(0.75^12 약 3%), Δ 를 변화량으로 설명되는 부분 이상에서 검정한다.

### 2d. 뇌 encoding (himalaya v0.4.11)
- 단일 특징: `KernelRidgeCV(kernel="linear", alphas=logspace(1,6,10), cv=run 묶음 5-fold)` [R: himalaya; grid R: MindCaptioning].
- banded: `GroupRidgeCV(groups="input", solver="random_search", n_iter=100, concentration=[0.1,1.0])` + `ColumnTransformerNoStack` [R: himalaya _sklearn_api.py, _random_search.py].
- 표적: 피험자별 전뇌 voxel, 회전 train 통계로 z. 지표: test r, band 분해는 `r2_score_split` (product measure) [R: himalaya scoring.py L99].
- 해석 단위: 42 ROI. voxel 별 "우세 band" 지도는 추론에 쓰지 않는다 (v1 F2).
- ceiling: HK 는 영상당 1회 제시라 반복 기반 ceiling 불가. 대용치로 HK LOSO(피험자 간) ROI 상관.

### 2e. 뇌 decoder
- 구현: KamitaniLab PyFastL2LiR `FastL2LiR(alpha, n_feat)`: 출력 단위마다 train 에서 |r| 상위 voxel 을 고르고 bias 포함 L2 ridge [R: PyFastL2LiR fastl2lir.py L256-295] (V). X, Y 는 회전 train 평균/SD 로 z [R: KamitaniLab feature-decoding].
- ROI 당 n_feat 500 (작은 ROI 는 전부) [R: HKpy wholebrain.yaml `num: 500`]. voxel 수가 같아 ROI 간 비교가 공정하다.
- alpha: val fold, grid logspace(1,6,10), 기준 = 목표 27-d profile r [V].
- 전뇌: dual ridge, 전 voxel 또는 학습 encoding 상위 50,000 [R: MindCaptioning mcap_setParams.m L50].
- 민감도: himalaya ridge (voxel 선택 없음, 목표별 alpha).
- 목표가 모두 27-d 라서 경로 간 출력 차원과 선택 예산이 같고, v1 의 수천 차원 특징 decoding 보다 계산이 크게 줄어든다.

선형 decoder 를 쓰는 이유
1. Kragel 2019 는 EmoNet 20 출력을 후두엽 7,214 voxel 에서 PLS 로 decoding 했다 (뇌 -> 모델 출력). 3막 주 경로가 같은 설계다. Gao 2025 도 ROI 별 PLSR 이다.
2. 같은 HK/MC 자료의 선행 분석(Horikawa 2020, Horikawa 2025, Du et al. 2023)이 모두 L2 선형이라 비교 가능하다.
3. Conwell et al. 2024: 유연한 연결은 모델 차이를 가린다. 선형이 해석 가능한 최소 연결이다.
4. MindEye2 (Scotti et al. 2024 ICML), Brain-IT (Beliy et al., ICLR 2026) 는 정지 영상 복원 모델이고 출력이 CLIP 토큰이다. Brain-IT 에는 시간 모듈이 없다 (V). 전뇌 민감도 분석으로만 쓴다 (AffectLab 에 HK 파일럿 있음).
5. EmoBrain LabelQueryDecoder 는 Query2Label 방식을 직접 구현한 것이라 사용자 조건 1(git clone)과 충돌한다. 거취는 §7 D-8.

---

## 3. 막별 방법

### 3.0 공통 통계 (v1 M2-M5 수정)
- 추론 단위: 피험자 안에서 자극 수준 (약 2.1k). 피험자는 반복 재현으로 다루고 k/5 와 Bayesian prevalence 를 보고 [P: Ince et al. 2021 eLife "Bayesian inference of population prevalence"].
- 피험자 x 자극 2요인 bootstrap [P: Schütt et al. 2023 eLife] 은 기술적 CI 로만.
- 순열: 10^4 이상, 또는 일반화 Pareto 꼬리 근사 [P: Winkler et al. 2016 NeuroImage]. 1,000 회로는 큰 FDR 군을 통과할 수 없다.
- 계층 검정: ROI 별 profile 수준 omnibus -> 유의한 ROI 안에서만 감정별. FDR 군은 그림마다 사전 고정.
- "차이 없음": TOST, SESOI 는 절대값으로 분석 전에 고정 [P: Lakens 2017; D-9]. seed 분산은 검정력 계산에만.
- 비율 통계(ρ)는 주 지표로 쓰지 않는다. 주 지표는 분산 분할과 차이(Δr).
- 지도 간 공간 상관은 spin test [P: Alexander-Bloch et al. 2018 NeuroImage] 또는 기술 통계로만.
- 가중치 해석: held-out fold 의 Haufe 패턴(backward -> forward 변환) [P: Haufe et al. 2014 NeuroImage] 을 주로, 원 계수는 보조. 단변량 corr(x_j, y_e) 를 나란히 표시.

### 3.1 1막: 자극 -> 정서
질문: 독립 영상과 독립 평정자로 학습한 렌즈가 Cowen 영상의 정서 프로파일 구조를 재현하는가? 저수준, 물체, 상황 정보는 각각 무엇을 더하는가?

1. 렌즈 보고 (VCE-test, 확증): 감정별 r, 영상별 profile r.
2. 고정 전이 (Cowen, MC-72 제외 전부, 적합 없음): 렌즈 27 vs Cowen 27. 감정별 Pearson/Spearman, profile r, RDM 상관 (거리 지표 [D-10]).
3. Kragel IAPS 대응: 렌즈 27 -> Cowen 14 차원 PLS, 회전 안 적합. 그림: 27 정서를 (valence, arousal) 패턴 하중 평면에 배치 [P: Kragel 2019 Fig. 2 형식].
4. **식별 가능성 관문 (CPU, 지금 가능)**: band 간 교차예측 R², CCA/CKA 스펙트럼, 유효 rank; 알려진 혼합(순수 L, 순수 O, 순수 S, 50/50)으로 만든 합성 목표의 회수 시뮬레이션; split-half 신뢰도. 관문을 통과한 해상도에서만 보고 (v1 F2).
5. 수준 분해 주분석 = **순차 ΔR², 순서 L -> O -> S 사전 고정**: "상황은 저수준과 물체를 넘어 무엇을 더하는가". 역순은 민감도, 7분할 commonality 는 기술용 [P: Lescroart et al. 2015].
   - 감정별 해상도: VCE 에서만 (test 11,046). bands {L, O-obj, O-act, S-vis}.
   - Cowen: profile/RDM 수준만. S 는 S-vis 와 S-cap 사다리(full, noaff, 무작위 삭제, shuf, bow) [P: Doerig et al. 2025 NMI 의 통제 형식].
   - 차원 민감도: band 를 train 에서 고른 k 로 PCA 해 같은 차원으로.
6. 렌즈 B 로 2, 5 반복.

그림: A 렌즈 -> VCE-test / Cowen 감정별 r (순열 영대). B 렌즈 RDM vs 평정 RDM (RDM PC1 순서로 정렬, 군집 순서 금지). C 순차 ΔR² 막대 (VCE 감정별). D S 사다리. E valence-arousal 평면.

양방향: 전이가 크고 공유분이 크면 대전제 (2) 지지. 전이가 0 에 가까우면 구성개념, 도메인, 소리 차이가 겹친 상태에서 안 옮겨진다는 결과이며 3막은 g_l 경로 중심으로 바꾼다. S 가 L, O 위에 더하는 몫이 0 이면 "상황 정보는 시각 내용에 이미 들어 있다".

### 3.2 2막: 자극모델 <-> 뇌
질문: 같은 모델, 같은 영상에서 목표만 정서로 바꾸면 어느 영역과 더 닮아지는가?

1. §2c arm 학습.
2. Cowen 영상에서 arm x seed x block(13) 특징 -> 피험자별 voxel encoding (§2d). ROI 별 최적 층은 val [P: Horikawa 2025 층 선택].
3. 적합 없는 연결도 병행: ROI 별 cRSA [P: Kriegeskorte et al. 2008]. encoding 과 RSA 에서 부호가 같을 때만 "기하적 정렬", encoding 만이면 "선형 접근 가능".
4. Δ_R = (피험자, seed) 짝 차이 평균, E - N-27. CKA 변화량을 공변량으로. 영역 주장은 arm x ROI 상호작용이 있을 때만.
5. 수준 -> 영역 지도 (H1): banded {L, O-obj, O-act, S-cap-noaff, Cowen 27 평정 band(회전 안)} -> 42 ROI. 내용 band 대 평정 band 의 설명력 동등성 TOST.
6. 목표 고유분: {L, O-obj, S-cap-noaff} 위에 E fc_norm 이 더하는 unique R² vs N-27 fc_norm 의 그것. O-act 는 N-27 teacher 와 같은 모델이라 이 분석에서 뺀다 (v1 F3a).

그림: A arm 별 block x PG1 분위 encoding r 곡선 (seed 띠). B Δ_{E-N27} 피질 지도: "목표 고유 분산의 부호" 세 색(+, 동등, -). C 수준 -> 영역 band 분해 (42 ROI). D H1 내용 vs 평정 band.

양방향: transmodal 에서 Δ>0 이면 정서 목표가 상위 영역과의 정렬을 만든다(H3 방향). 전 영역 동등이면 정렬은 diet 와 구조가 결정한다 [P: Conwell et al. 2024] 는 결과로 보고.

### 3.3 3막: 뇌 -> 정서 (H4 검정)
질문: 사람 평정을 한 번도 보지 않은 decoder 로 영역별 뇌에서 정서를 읽을 수 있는가? 어느 영역에서 어느 수준의 정보가 그것을 지탱하는가?

경로 (영역 R, 피험자별, 회전 안)
- R-lens: 뇌 -> f(x) 27 (렌즈 출력을 목표로 학습).
- R-l: 뇌 -> g_l(x) 27, l in {L, O-obj, O-act, S-vis}.
- Direct: 뇌 -> Cowen 27 평정 (평정만 학습한 decoder, H4 의 필수 비교).
- 보조 generic 경로: 뇌 -> fc_norm 768 -> 고정 렌즈 head [P: Horikawa & Kamitani 2017].

평가: 모든 경로의 test 예측을 **Cowen 사람 평정**과 비교.
- 주 지표: 평정 y_e 를 [경로 예측, Direct 예측] 에 대해 분산 분할 (val 에서 가중치, test 에서 점수): unique(경로), unique(Direct), shared.
- 보조: Δr = r(경로) - r(Direct), 피험자 안 짝 자극 bootstrap.
- 출력: 42 ROI x 5 경로 x 27 정서. 감정별 셀은 split-half 관문 통과 시만.

통제
1. 짝 어긋난 뇌: 뇌를 다른 자극의 것과 짝지어 같은 절차. 향상 폭의 차이에 CI (paper_logic §4-B 요구).
2. decodability 대응 시뮬레이션 영가설: 진짜 test 특징 -> 영역 SNR 의 합성 voxel -> 같은 FastL2LiR -> 기대 정서 r. 주장 = 관측 - 기대 (영역이 정서 관련 차원을 선택적으로 보존하는 정도) (v1 M6).
3. ROI 제거 수렴 검정: 전뇌 decoder 에서 ROI 그룹을 하나씩 빼고 하락 측정 -> 2막 지도와 대조 (paper_logic H4 수렴 검정).
4. HK LOSO: 4명 ROI 수준 학습 -> 1명 시험. MC 전이 손실의 기대치 보정.

그림: A 영역(PG1 순) x 경로 분산 분할 열지도. B 감정 6개 [D-11] 의 영역별 unique/shared 막대. C decodability-정서 산점도와 시뮬레이션 영가설. D ROI 제거 하락 지도 vs 2막 지도. E 한 test 영상의 27 막대(평정, Direct, R-lens, R-S-vis, R-L).

양방향: transmodal 에서 R-S-vis 의 unique+shared 가 크면 상위 영역의 정서 정보가 언어정렬 시각 내용으로 운반된다 (H3, H4). Direct unique 가 크면 이 특징 집합으로 잡히지 않는 성분이 그 영역에 있다 ("환원 불가능" 아님).

---

## 4. 시연 (Kragel, Gao 형식)

### D1. 예고편 장르 (Kragel 2019 Fig. 3 의 재현과 확장)
- 자료: Trailers12k 메타데이터 (IMDb id, YouTube id, 10 장르 다중 라벨, 고정 3 fold; CC BY-NC-SA) (V). 영상은 YouTube 에서 받는다. 30개 먼저 받아 확인. 재배포 없음, 그림은 CC 대체 이미지.
- 장르: Kragel 의 3개를 순수 규칙으로 [D-12]. romcom = romance & comedy & not(action, horror, thriller); horror = horror & not(comedy, romance); action = action & not(horror, romance, comedy).
- 규모: 단계 1 Kragel 규모(장르당 9-10, 예시용), 단계 2 조건을 만족하는 전부.
- 소리 제거. 렌즈 1 s 창 -> 27 x T. 요약 = 시간 평균 [P: Kragel] + 시간 SD.
- 분류: PLS-DA one-vs-all [P: Kragel], 성분 수 inner CV, outer 10-fold 장르 층화 [P: Kragel]. 지표 = 장르별 AUC (argmax 3-way 정확도는 보고 안 함). 순열 10^4. 계수: held-out Haufe 패턴 주, bootstrap 1000 β 보조 [P: Kragel].
- 확장 (Kragel 이 하지 않은 것): (1) 같은 분석을 L, O-obj, S-vis, 렌즈 768 로 반복하고, 렌즈 27 을 L 로 잔차화(fold 안)해 "장르 정보 중 27 정서를 통과하는 몫" 분리. (2) 예고편 진행(0-100%)에 정렬한 장르별 평균 정서 곡선. (3) 제목/자막 프레임은 OCR 로 검출해 포함판/제외판.
- 그림: A Sintel(CC-BY) 27 정서 시간 곡선 + 프레임 띠. B 장르 x 정서 패턴 열지도 (CI). C ROC. D 수준별 장르 정보 막대. E 장르별 정서 곡선.

### D2. 정서별 상위 가중치 단어 그림 3종 (Gao 2025 Fig. 3 형식)
G1 물체 (VCE)
- X = EVA02-L in22k 21,841 logits (25/50/75% 3 프레임 평균) [P: Gao 프레임 규칙]; 보조 X = AlexNet fc8 1,000 (Gao 와 같은 공간).
- Y = VCE 27 (z). 자료 lens-train + lens-val.
- PLSR 20 성분 [P: Gao], 15-fold, 계수 fold 평균 [P: Gao].
- 순위: fold 평균 held-out Haufe 패턴. 원 계수와 단변량 상관 병기.
- 정서별 상위 10 / 하위 10 [P: Gao]. 안정성: bootstrap 1000 에서 상위 10 에 든 비율.
- 근의어: WordNet 상위어 묶기와 출현 하한을 사전 고정 [D-13].
- 표본 외: VCE-test r, Cowen 재적합 없는 적용 r.
- 그림: 정서 6개 [D-11] 패널, 각 +10 / -10 단어, 막대 = 패턴, 색 = 안정성. 27개 전부는 보충.

G2 상황 단어 (Cowen 인간 캡션)
- X = 영상별 20 캡션의 lemma 출현 비율 (명사, 동사, 형용사; spaCy 버전 고정; 출현 하한 [D-7]). 헤드라인은 정서 어휘 제거판, 무작위 삭제 대조 병기.
- Y = Cowen 27. hk_dev_v4 회전 안에서 PLSR, 패턴 순위, 상위 단어.
- 그림: G1 과 같은 배치. "같은 정서를 부르는 물체 단어 vs 상황 단어" 를 나란히.

G3 뇌 단어 지도
- 영역 R 에서 단어 출현 벡터를 FastL2LiR 로 decoding (회전 안).
- 단어 선택은 train/val 절반에서, 표시는 나머지 절반에서 (v1 M8 이중 사용 수정).
- 기여 = decodability x G2 패턴 가중치, decodability 대응 영가설과 비교.
- 그림: 행 = 영역 그룹 8개 (EVC, 복측 시각, MT/LTC, TPOJ, IPC, PCC/precuneus, mPFC/ACC, OFC), 열 = 정서 6개, 칸 = 기여 상위 5 단어, 색 = decodability, CI 가 0 포함이면 회색.

### D3. 영역이 좋아할 VCE 영상 (in silico; Ratan Murty et al. 2021, Jang & Kragel 2025 형식)
- HK encoding (bands {L, O-obj, O-act, S-vis}, VCE 에서 계산 가능한 것만, 렌즈 제외). 대상 ROI 는 val 에서 선택.
- VCE 61k 중 Cowen 특징 지지역 안(PCA-Mahalanobis < Cowen 99 백분위)인 영상만.
- ROI 예측 반응 vs VCE 독립 평정 27 의 Spearman -> 영역 x 정서 지도.
- 영가설: 자극 순열 반응으로 적합한 encoder (같은 스펙트럼).
- 몽타주: ROI 별 상위 24 / 하위 24 [D-14] 프레임 + 평균 27 프로파일 vs 무작위 24 집합 1,000 개.
- 목록 사전등록 -> 향후 새 fMRI 검증 [P: Gu et al. 2023 Commun Biol]. 헤드라인 주장에는 쓰지 않는다 (모델의 속성).

### D4. Emo-FilM 정서 곡선 (자극 측, 뇌 측)
- 자극: 렌즈 1 s 창 -> 27 x 약 9,600 s. Emo-FilM 13 이산 정서와 대응: 직접 7 (Anger, Disgust, Fear, Anxiety, Satisfaction, Surprise, Sad->Sadness), 근의어 4 사전 표기 (Happiness->Joy, Love->Romance, WarmHeartedness->Adoration, Regard->Admiration), 대응 없음 2 (Guilt, Pride). 열 이름 확인 후 확정.
- 주석 지연: leave-one-film-out 로 선택 [D-15]. 지표: 영화 x 정서 r, 원형 이동 영가설. 상한: 평정자 split-half Spearman-Brown.
- 뇌: MNI 전처리 파생본에서 ROI 시계열 -> run-z -> 4 s shift -> 슬라이딩 창 [D-16] -> HK 에서 고정한 ROI 수준 decoder. **주 decoder 는 청각 ROI 를 사전 제외한 것**, 오디오 포락선 nuisance. 단위 30명, 집단 추론 가능.
- 그림: A Sintel 프레임 띠. B 주석 Fear, 렌즈 Fear, 뇌 decoded Fear 세 곡선. C 영화 x 정서 r 열지도.

### D5. MC 재적합 없음 (지각, 심상)
- HK 에서 고정한 ROI 수준 decoder (§1.5 통일 입력) 를 MC 72 에 그대로.
- 지표: 감정별 r, profile r, 72 x 72 RSA (5 반복 교차검증 거리 [P: Walther et al. 2016 NeuroImage]).
- 단서 통제: 준비 구간(캡션 단서 읽는 시간)을 같은 decoder 로 decoding 해 경험적 단서 기준선으로. 심상 창은 단서 종료 후 시작점 사전 고정.
- 판정: 6/6 방향 일관성 사전 선언 (6/6 이항 p = .016, 5/6 = .109). HK LOSO 를 기대 손실로.

### D6. V2V 선호 (보조)
- Bradley-Terry: logistic(f(b) - f(a)), V2V test 쌍 3,189 로 적합 (렌즈 학습에서 제외된 영상), listwise 1,758 에서 Kendall τ 평가 [R: JS run_v2v_finetuning.py 손실 형식].
- 헤드라인: 27 BT 가중치 막대 = "어떤 정서가 영상을 더 선호되게 하는가". 이 축을 Cowen 에 재적합 없이 적용해 Cowen valence 차원과 상관. 뇌 경로: R-lens 출력에 BT 가중치 적용 -> 영역별 "decoded 선호" 지도.

### D7. "같은 정서, 다른 내용" 쌍 (H2, paper_logic 필수)
- Cowen 비-MC 자극 모든 쌍에서 정서 거리(27)와 내용 거리(S-vis, 보조 L+O) 계산, |rank(내용) - rank(정서)| 상위 5/10/20% (임계값 없음, paper_logic 규칙).
- 그림: 정서는 비슷하고 내용은 다른 쌍의 프레임 갤러리.
- 검정: 그런 쌍의 영역별 뇌 패턴 거리 vs 정서-내용이 모두 비슷한 대응 쌍. H2 예측 = 뇌는 다르게 반응.

---

## 5. 실행 순서와 비용

| 순서 | 작업 | 자원 | 관문 (결과 보기 전에 고정) |
|---|---|---|---|
| 1 | 매니페스트, ID crosswalk (VCE id, Cowen stim_num, HK stimulus_name, MC video_id), 단일 분할, 누수 assert | CPU | |
| 2 | VCE 다운로드, checksum, 라이선스; HK-MC 피험자 동일인 확인; Emo-FilM 영화 확보 확인 | 네트워크 | VCE 실패 시 전체 재검토 |
| 3 | 식별 가능성 관문 (기존 CLIP bigG, V-JEPA 2 특징 + pymoten) | CPU, 지금 | 회수 실패 해상도는 보고 안 함 |
| 4 | 중복 검사 (VCE 내부, VCE-Cowen) | CPU + GPU 소량 | 중복 다수면 독립성 프레임 재검토 |
| 5 | 렌즈 파일럿 1 epoch 시간 측정 -> 렌즈 E seed 0, 50 epoch | GPU (검토 추정 1 run 약 5-15 A100-h) | K-lens: VCE-test FDR 통과 0 이면 원인 진단 |
| 6 | 특징 추출 (Cowen, VCE, 예고편, Emo-FilM) | GPU (검토 추정 약 10-25 A100-h, PE-Core G 가 대부분) | |
| 7 | 1막 | CPU | K-transfer: 렌즈 -> Cowen 이 영가설과 구분 안 되면 3막 경로 재설계 |
| 8 | 3막 decoder (27-d 목표) | CPU | K-dec: EVC 에서 L 경로 decodability 양성 확인 후 정서 경로 개방 |
| 9 | 2막 파일럿 2 seed -> 확장 | GPU 최대 (검토 추정 arm 전체 약 40-210 A100-h) | K-seed: 효과 < seed SD 면 seed 늘리거나 동등 보고 |
| 10 | Emo-FilM fMRI (358.7 GB) | 디스크 | 영화 확보 후 |
| 11 | 4막. MC 는 마지막, commit hash 고정 후 1회 | CPU/GPU | |

GPU 명령은 단일 절대경로 `bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/...sh` 형식으로 제공 (스크립트 미작성). 시간은 5단계 실측 후 확정하며, 위 수치는 검토자의 FLOP 산술이다.

---

## 6. 미확인 사항
- VCE 라이선스, 크기, 소리 유무, Cowen 과 실제 중복.
- 가중치 다운로드 가능 여부 (이 세션에서 HF, fbaipublicfiles 차단).
- EVA02-L pre-logit 차원, DeBERTa-large 층 차원 (U).
- Kragel 색 bin 수, PLS 성분 수 (supplement 미열람).
- Emo-FilM 13 정서 열 이름, 영화 확보.
- HK-MC 피험자 동일인 여부.
- Margulies PG1 지도 출처 (neuromaps 등).
- 원고 전 원문 재확인 필요: Scotti 2024, Margulies 2016, 아틀라스 논문들, VideoMAE / VideoMAE V2 / EVA-02 / DeBERTa 원논문, Bradley & Terry 1952, Benjamini & Hochberg 1995.

## 7. 결정 사항
- D-1 중복 검사 프레임율 (제안 1 fps). D-2 양성 대조 수와 재현율 (제안 500, 99%).
- D-3 감정별 추론 최소 비영 자극 수.
- D-4 PG1 지도 출처.
- D-5 MC 저자 run-z 를 "배포 자료"로 인정할지 (PI).
- D-6 색 히스토그램 bin. D-7 정서 어휘집과 출현 하한 (사전등록).
- **D-8 모델의 자리**: (a) 3막 선형 경로를 H4 검정으로 삼고 LabelQueryDecoder 는 은퇴 또는 민감도 (추천, 조건 1 충족) / (b) LabelQueryDecoder 를 H4 student 로 유지하고 렌즈를 stimulus-only teacher 로. 어느 쪽이든 CLAUDE.md v8 과 34->27 기록.
- D-9 TOST SESOI 절대값.
- D-10 정서 거리 지표 정본 (원리로).
- D-11 본문 정서 6개 (Gao 5개: aesthetic appreciation, craving, horror, sadness, sexual desire + 1).
- D-12 예고편 장르 정의와 YouTube 다운로드 허용.
- D-13 21,841 클래스 근의어 규칙. D-14 몽타주 크기. D-15 Emo-FilM 지연 범위. D-16 Emo-FilM 창 길이.
- 2막 seed 예산 (E, N-27 각 5 이상).

## 부록: v1 검토 지적의 처리
| 지적 | 처리 |
|---|---|
| F1 분할 두 개로 누수 | hk_dev_v4 단일, 회전 안 재적합, assert (§1.1) |
| F2 수준 분해 식별 불가 | 관문, 순차 ΔR², 감정별은 VCE 만, 이름 타당도 (§3.1) |
| F3 2막 불공정 | N-27 arm, 고정 예산, CKA, O-act 제외 (§2c, §3.2) |
| C1 정본 문서 충돌 | D-8, CLAUDE.md v8 |
| C2 repo 가 VCE-test 자동 평가, top-1 저장 | 패치 (§2a) |
| C3 HK ROI 입력 불일치 | MC 와 같은 순서로 재구성 (§1.5) |
| M2-M5 통계 | 피험자 안 추론, prevalence, 10^4 순열, 절대 SESOI, 비율 폐기 (§3.0) |
| M6 decodability 와 정서 혼동 | 시뮬레이션 영가설 (§3.3) |
| M7 decoder 정당화 모순 | 27-d 목표 직접 decoding 을 주 경로로 (§2e, §3.3) |
| M8 가중치 해석, 이중 사용 | Haufe 패턴, 절반 분할 (§4 D2) |
| M9 정서어 삭제 혼동 | 무작위 삭제 대조 (§2b) |
| M11 VCE 내부 중복, 위치 기반 val | 군집, 무작위 val (§1.2-1.3) |
| M12 렌즈와 O-act 같은 계열 | 렌즈 B 공동 조건 (§2a) |
| M13 MC 출처, 단서 | 동일인 확인, 준비 구간 기준선 (§1.6, D5) |
| M14 Emo-FilM 소리 | 청각 ROI 제외 주 decoder, 포락선 (D4) |
| M15 in silico 선택, 외삽 | val 선택, 지지역 제한 (D3) |
| M16 H1-H4 누락 | H1 band (§3.2-5), H2 (D7), H4 (§3.3), 수렴 검정 |
| H5 렌즈 B 비용 | ViT-L 2 segment 또는 ViT-B |
| H6 짧은 영상 | 패딩 규칙, 민감도 (§2a) |
