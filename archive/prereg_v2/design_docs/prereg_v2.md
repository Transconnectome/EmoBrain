---
title: "EmoBrain 사전 확정 문서"
subtitle: "v2 revised — prespecified teacher relation formation and model-computational interventions"
date: "2026-09-12"
---

# 1. 목적과 사용법

이 문서는 결과를 보기 전에 분석 선택을 동결하기 위한 단일 진실 원천이다. `확정`은 문헌·원자료 구조로 확인되어 더 이상 결과에 맞춰 선택하지 않는다는 뜻이고, `동결 전 확인`은 **정서 label과 뇌 반응의 대응을 보지 않는** 데이터 무결성·신뢰도·계산 가능성 검사 뒤 확정한다는 뜻이다. 동결 후 변경은 변경 전 사양, 변경 이유, 영향을 받는 가설과 분석을 `process_v14.md`에 기록한다.

# 2. 연구질문과 반증 조건

## 2.1 중심 연구질문

**How are shared neural responses to emotionally evocative situations organized by affect-unsupervised sensory–semantic representations, and how does a brain-grounded model learn and functionally use those relations for high-dimensional affective readout?**

이 질문에서 model은 단순한 성능 도구가 아니라, `relation formation → brain-only inheritance → functional use`를 검정하기 위한 조작 가능한 분석 대상이다. 다만 model intervention에서 관찰된 dependence를 인간 뇌의 인과기제로 확장하지 않는다.

여기서 `affect-unsupervised`는 해당 representation이 이 연구에서 정서 label 또는 정서 판별 목적으로 학습·선택되지 않았다는 뜻이다. 사전학습 corpus가 정서적 내용을 전혀 포함하지 않았다는 뜻은 아니다.

## 2.2 주장이 지지되기 위한 최소 조건

1. 감각–의미 feature가 held-out 자극의 뇌 반응을 low-level control보다 안정적으로 더 예측한다.
2. primary 34-D matched teacher ladder에서 aligned BVS model이 B, BV, BS와 shuffled-alignment teacher와 구별되고, correct triplet이 modality-mismatched triplet보다 일관된 fused brain-token state, retrieval과 output을 만든다.
3. BVS teacher의 OOF guidance가 brain-only student의 held-out joint/video/caption readability를 Direct와 Shuffled보다 선택적으로 바꾼다. Linear CKA는 secondary geometry summary로 사용한다.
4. Teacher activation patching이 mismatch로 손상된 content retrieval과 affect output을 회복하고, 사전 정의 anatomical network perturbation이 student의 같은 readout을 선택적으로 저하시켜 단순 decodability가 아닌 trained-model dependence가 확인된다.
5. Full-guided student의 primary 34-D normative profile readout이 사전 정의 baseline을 넘고 Direct 및 Shuffled-guided보다 개선된다.
6. 별도 학습한 14-D, VA-2, VAD-3에서 `Full−Direct`와 `Full−Shuffled`의 방향이 어떤 affect coordinate까지 일반화되는지 판정할 수 있다.
7. 효과의 방향이 독립 참가자 cohort에서 재현된다.

## 2.3 반례

- Analysis 1에서 content kernel이 low-level control을 넘지 못한다.
- BVS teacher가 B/BV/BS 또는 shuffled-alignment teacher를 안정적으로 넘지 못하거나 correct triplet이 modality mismatch와 구별되지 않는다.
- full guidance와 shuffled guidance가 같은 geometry 변화와 같은 성능 이득을 낸다.
- retrieval은 변하지만 clean activation patching 또는 anatomical-network perturbation이 content와 affect output을 함께 바꾸지 않거나 matched null과 구별되지 않는다.
- Full-guided affect readout이 training-fold mean profile 또는 mandatory linear/reduced-rank baseline을 넘지 못해 mechanistic interpretation gate를 통과하지 못한다.
- learned-representation 변화는 있으나 34-D readout은 개선되지 않는다.
- readout은 개선되지만 geometry 변화가 content reference와 무관하다.
- primary cohort의 효과가 replication cohort에서 방향까지 재현되지 않는다.

어느 한 반례도 “감정이 감각–의미 처리와 무관하다”를 뜻하지 않는다. 본 연구의 표상, 자극, fMRI SNR, 학습 절차로 제안된 organizing mechanism을 지지하지 못했다는 뜻이다.

# 3. 데이터와 분석 단위

| ID | 항목 | 사전 확정 | 상태 |
|---|---|---|---|
| D1 | primary cohort | Mind Captioning/Horikawa 2025 계열 perception fMRI, 6 participants | 원문 확인; events 재검증 필요 |
| D2 | replication cohort | Horikawa et al. 2020, 5 participants | 원문 확인 |
| D3 | cohort 역할 | 같은/중첩된 자극을 본 다른 참가자에 대한 participant-level replication. stimulus-level external generalization으로 부르지 않음 | 확정 |
| D4 | 참가자 독립성 | 참가자 ID 비중복이어야 replication이라는 표현을 유지 | 동결 전 ID crosswalk |
| D5 | 자극 수 | primary: unique 2,180; modeling train 2,108; repeated test 72. replication: 2,181 | 제공 문서·원문 확인; 파일 매핑 재검증 |
| D6 | 통계 단위 | 자극과 참가자. 자극쌍 2,556개를 독립 표본으로 취급하지 않음 | 확정 |
| D7 | repeated test | 72개 자극의 반복은 reliability/noise ceiling 및 final held-out evaluation에 사용 | 확정 |
| D8 | imagery | 사용하지 않음 | 확정 |

# 4. normative annotation

| ID | 항목 | 사전 확정 | 상태 |
|---|---|---|---|
| L1 | 34-D space | 주 target. 복수 category를 선택한 평정자 비율로 이루어진 자극별 graded profile. one-hot classification이 아님 | 확정 |
| L2 | 14-D space | broad affective appraisal을 나타내는 독립 alternative-ontology secondary target | 확정 |
| L3 | VA-2/VAD-3 | `VA-2 ⊂ VAD-3 ⊂ appraisal-14`인 dimensional family의 nested low-dimensional controls | 열 정의 audit 후 동결 |
| L4 | 독립 학습 | 34-D, 14-D, VA-2, VAD-3를 각각 별도 teacher/student로 학습. trainable parameter, head, loss, standardizer, OOF cache를 공유하지 않음 | 확정 |
| L5 | 결합 금지 | target들을 concatenate하거나 multi-task/joint loss로 공동학습하지 않음 | 확정 |
| L6 | self-report 해석 | 모든 annotation은 fMRI participant self-report로 부르지 않음 | 확정 |
| L7 | thresholding | 단일 dominant emotion이나 특정 감정의 고/저 집단을 만드는 threshold 분석을 하지 않음 | 확정 |
| L8 | 34-D 변환 | raw `[0,1]` proportion을 그대로 사용하고 z-score·log1p·임의 frequency weight를 적용하지 않음 | 확정 |
| L9 | dimensional 변환 | 14-D·VA-2·VAD-3는 outer-training fold에서 차원별 표준화하고 평가 시 원척도로 역변환 | 확정; column/scale audit 필요 |
| L10 | raw counts | category별 선택 인원수 `k`와 전체 평정자 수 `n`을 확인할 수 있을 때만 binomial NLL robustness 수행 | 동결 전 data audit |
| L11 | 결측 | 자극–annotation crosswalk를 고정하고 결측 자극은 해당 target의 모든 조건에서 동일하게 제외 | 동결 전 확인 |

# 5. fMRI 표현과 분할

| ID | 항목 | 사전 확정 | 상태 |
|---|---|---|---|
| B1 | response estimate | 제공된 block response를 재현 baseline으로 보존. raw data가 완전하고 계산 가능하면 GLMsingle single-trial beta를 주 입력으로 채택하되 repeated-test reliability로 선택 | 동결 전, label-blind |
| B2 | 공간 | participant-native response를 기본으로 하고 atlas ROI로 요약 | 확정 |
| B3 | atlas | Schaefer cortical parcels + Tian subcortical parcels. 해상도는 usable voxel 수와 adapter parameter 수를 보고한 뒤 한 번 고정 | 동결 전, label-blind |
| B4 | ROI token | ROI 안의 voxel pattern을 fold-training PCA로 축약. 모든 standardization/PCA는 train fold에서만 fit | 확정 |
| B5 | PCA 차원 | 설명분산 80%를 기본값으로 하되 고정 차원 8을 robustness로 사용. ROI별 최소/최대 차원과 총 token 차원을 보고 | 동결 전 계산 가능성 확인 |
| B6 | participant adapter | ROI token을 공통 latent width로 사상하는 participant-specific linear adapter | 확정 |
| B7 | shared encoder | 소형 shared encoder; depth/width는 고정된 작은 후보 집합에서 nested validation으로 선택 | 확정 |
| B8 | split | stimulus/run held-out. 동일 stimulus는 어떤 participant에서도 동시에 train과 validation/test에 걸치지 않음 | 확정 |
| B9 | repeated test leakage | 72개 repeated test stimuli는 architecture, layer, λ, k 선택에 사용하지 않음 | 확정 |
| B10 | session/duration | session과 presented duration을 기록하고 주요 metric에 대한 민감도 분석을 수행 | 확정 |

# 6. 감각–의미 feature

| ID | source | 조작적 역할 | 선택 이유 | 동결 항목 |
|---|---|---|---|---|
| F0 | low-level | luminance/color/spatial-frequency/motion control | content model의 이득이 기본 영상 통계만으로 설명되는지 검사 | 구현·차원 |
| F1 | V-JEPA 2 visual encoder | spatiotemporal visual content | appearance와 dynamics를 한 video model에서 표현해 object/event의 임의적 분리를 피함 | checkpoint, layer, temporal pooling |
| F2 | frozen sentence encoder | caption semantics | 사람이 기술한 행위·상황 의미가 visual dynamics를 넘어 추가하는 정보를 검정 | checkpoint, layer, token/caption pooling 및 선택 근거 |
| F3 | AlexNet fc7 | supplementary static-appearance anchor | Kragel/Gao 계열과 역사적으로 연결하되 model-family 차이를 object–event 차이로 오해하지 않도록 주 teacher에서는 제외 | frame sampling, pooling |

모든 source는 frozen이며 study-specific affect label로 fine-tuning하지 않는다. layer를 test 성능에 맞춰 사후 선택하지 않는다. 후보 layer가 둘 이상이면 training folds에서만 선택하거나 사전 정의한 layer profile 전체를 보조 결과로 보고한다.

# 7. Analysis 1 — Organization

## 7.1 질문

감각–의미 representation은 held-out stimulus에 대한 공유된 ROI-wise brain response를 어떻게 조직하는가?

## 7.2 모델

각 source를 kernel로 변환하고 nested cross-validation으로 regularization을 정하는 **multi-kernel ridge encoding**을 사용한다. 구현은 primal banded ridge 또는 동등한 dual multi-kernel ridge가 될 수 있으나 prediction과 kernel weight가 수치적으로 일치해야 한다.

주 모델:

1. low-level only
2. spatiotemporal visual only
3. spatiotemporal visual + caption semantics (full)

AlexNet fc7 static-appearance encoding은 supplementary historical-anchor 분석으로만 수행하며 주 nested contrast에 포함하지 않는다.

## 7.3 평가

- primary metric: held-out ROI-pattern prediction correlation, participant별 계산
- secondary: cross-validated explained variance, reliability-normalized correlation
- 주 대비: visual − low-level, full − visual, full − low-level
- inference: stimulus permutation을 participant 내에서 수행하고, participant-clustered bootstrap으로 CI 계산

## 7.4 해석 제한

encoding 성공은 해당 feature가 brain response를 예측한다는 뜻이지, brain이 그 feature를 동일한 알고리즘으로 계산한다거나 그 feature가 affect readout에 사용된다는 뜻이 아니다.

# 8. Teacher–student learning

## 8.1 multimodal neural teacher

- 입력: participant-specific fMRI ROI tokens, frozen V-JEPA 2 spatiotemporal visual feature, frozen caption-semantic feature
- 출력: target별 normative prediction. Primary는 34-D category-proportion profile이며 14-D, VA-2, VAD-3는 별도 model run
- 구조: 각 modality를 작은 projector로 공통 width에 맞추고, modality와 ROI token identity를 보존한 compact fusion module이 fused brain-token state와 joint latent `u_BVS`를 생성한 뒤 target-specific joint head로 예측
- primary 34-D teacher ladder: `B`, `BV`, `BS`, `BVS`, `B+shuffled(V,S)`; brain encoder와 fusion capacity를 가능한 한 일치시키고 missing modality는 mask token으로 대체
- scope: full teacher ladder와 mechanistic relation analysis는 category34에서 수행. appraisal14, VA-2, VAD-3는 BVS teacher와 Direct/Full/Shuffled student의 final functional contrast만 confirmatory로 반복
- 필수 조건: 동일 stimulus가 어느 participant에서도 teacher training과 해당 OOF prediction에 동시에 나타나지 않는 stimulus-wise fold
- student에는 fold-specific teacher가 만든 OOF soft profile만 제공
- teacher의 역할: brain response를 aligned content와 함께 해석하는 training-only privileged model. visual/caption input은 시험 시 사용하지 않음
- 34-D teacher objective: sigmoid output에 `L_T^34 = mean_d SoftBCE(y_d, p_d^T)`. raw `k,n`이 확인될 때만 binomial NLL을 robustness로 사용
- 14-D·VA-2·VAD-3 teacher objective: training-fold standardized continuous target에 `L_T^q = mean_d MSE(y_{z,d}, ŷ^T_{z,d})`
- 모든 objective는 output dimension으로 나누며 임의 class/dimension weighting을 사용하지 않음
- OOF는 추가 loss가 아니라 `K−1` stimulus folds에서 teacher를 fit하고 동결한 뒤 제외된 stimulus를 예측하는 procedure

## 8.2 brain-only student

`ROI-PCA tokens → participant-specific adapters → small shared encoder → target-specific joint head`

한 target 안의 출력을 차원별 독립 model로 나누지 않는다. joint head는 target 내부 공분산을 학습하되, 특정 category가 하나의 고정 brain pattern이라는 가정을 두지 않는다. 서로 다른 target space 사이에는 shared encoder를 포함한 trainable parameter를 공유하지 않는다.

## 8.3 목적함수

34-D: `L_S^34 = SoftBCE(y, p_student) + λ MSE(p_teacher^OOF, p_student)`

14-D·VA-2·VAD-3: `L_S^q = MSE(y_z, ŷ_{S,z}) + λ MSE(ŷ_{T,z}^{OOF}, ŷ_{S,z})`

34-D의 distillation MSE는 sigmoid 뒤 probability scale에서 계산하는 Brier-type error다. `λ ∈ {0.1, 0.3, 1.0}`에서 target별 nested validation으로 선택하고, 두 항은 각각 output dimension으로 정규화한다. teacher representation, visual feature, caption embedding, CKA 또는 pairwise relation을 직접 맞추는 student loss와 attention distillation은 사용하지 않는다. 따라서 사후 joint/visual/semantic recovery는 직접 최적화되지 않은 검정 결과다.

## 8.4 student 조건

| 조건 | label loss | guidance | 의미 |
|---|---:|---|---|
| Direct | 사용 | 없음 | 동일 brain architecture의 brain-only 기준 |
| Full-guided | 사용 | aligned BVS teacher의 OOF 출력 | joint brain–visual–semantic guidance |
| Shuffled-guided | 사용 | BVS OOF 출력의 stimulus pairing을 training fold 안에서 permutation | supervision 양·smoothness·추가 loss 효과 통제 |

세 조건은 한 target 안에서 initialization schedule, parameter count, optimizer, early-stopping rule, split, seed를 공유한다. shuffled condition은 target vector의 내부 공분산과 marginal distribution을 보존하고 stimulus pairing만 끊는다. Brain-only teacher distillation은 generic teacher-capacity control로 supplementary에 둔다.

# 9. Analysis 2 — Learned relations

## 9.1 질문

Teacher는 correct brain–video–caption correspondence를 어디에서 형성하며, output-level guidance 뒤 brain-only student는 그 관계 중 무엇을 회복하고, teacher와 student는 그 정보를 affect output에 실제로 사용하는가?

## 9.2 추출

각 teacher의 projected modality tokens, post-fusion brain tokens와 joint latent, 그리고 각 student의 participant adapter, encoder block 1, block 2, 최종 예측 직전 latent를 **완전히 held-out stimulus**에서 추출한다. 반복 test는 먼저 반복을 평균한 자극 수준 activation을 주 분석에 사용하고, 반복별 activation은 reliability 분석에만 사용한다.

## 9.3 primary teacher relation formation

Frozen primary BVS teacher에 다음 held-out triplet을 입력한다.

- correct: `(B_i,V_i,S_i)`
- video swap: `(B_i,V_j,S_i)`
- caption swap: `(B_i,V_i,S_j)`
- both swap: `(B_i,V_j,S_j)`

`j`는 같은 participant와 held-out fold 안에서 `i`와 겹치지 않는 derangement로 선택한다. Primary는 여러 사전 생성 permutation의 평균이며, 정확한 수는 계산 가능성 검사 뒤 outcome을 보기 전에 동결한다. Both swap은 V–S pair를 함께 이동해 content 간 coherence를 보존하면서 brain alignment를 끊는다. Single swap은 한 modality의 correspondence와 V–S coherence를 함께 깨므로 unique visual 또는 unique semantic mechanism으로 해석하지 않는다. 각 stage에서 correct–mismatch representation distance, correct-stimulus retrieval, teacher-joint neighborhood와 affect-output shift를 계산한다. Low-level video statistics 또는 caption length가 비슷한 후보 안의 matched mismatch는 robustness다.

## 9.4 primary student inheritance

각 student stage activation에서 cross-validated linear 또는 reduced-rank readout을 fit한다. Probe capacity와 regularization은 training fold 안에서만 선택하며 shuffled-label 및 matched-capacity null을 함께 계산한다.

- teacher BVS joint latent: correct-stimulus retrieval
- V-JEPA 2 visual: training-fold PCA로 축약한 feature prediction과 correct-video retrieval
- caption semantics: sentence-embedding prediction과 correct-caption retrieval
- 34-D category profile: Analysis 3와 같은 held-out metric

Retrieval의 주 요약은 top-k accuracy와 median rank이고, neighborhood overlap은 secondary다. Held-out exemplar montage는 retrieval rank의 사전 정의 분위수와 성공/실패 규칙으로 선택하며 수동 cherry-picking을 금지한다. 주 대비는 primary 34-D model의 `Full − Direct`, `Full − Shuffled` stage × reference별 readout 변화다. Visual/semantic readout은 diagnostic task이며 student loss나 model selection에 들어가지 않는다. 높은 readout은 representation에 정보가 decodable하다는 뜻이지 student가 그 정보를 output에 사용했다는 뜻은 아니다. 14-D·VA-2·VAD-3는 paper size와 중복을 통제하기 위해 full layerwise geometry/content analysis를 반복하지 않고 final functional contrast를 중심으로 보고한다.

## 9.5 secondary geometry map: layer×reference linear CKA

동일한 held-out stimulus order에서 student의 `[adapter, block1, block2, final latent]`와 네 reference `[teacher BVS joint latent, V-JEPA 2 visual, caption semantics, 34-D affect profile]` 사이 centered linear CKA를 계산한다. 각 condition의 absolute CKA와 `Full−Direct`, `Full−Shuffled`를 `layer × reference` heatmap으로 보고한다. CKA는 student loss나 model selection에 넣지 않으며 primary success criterion으로 사용하지 않는다. CKA는 전체 stimulus geometry의 similarity를 뜻할 뿐 decodability, information use 또는 neural causality를 뜻하지 않는다.

## 9.6 primary teacher activation patching

Video-swap 및 caption-swap run에서 선택된 post-fusion brain-token 또는 joint activation을 같은 stimulus의 clean activation으로 교체하고 나머지 activation은 mismatch 상태로 유지한다. 각 stage와 readout에 대해 `R=[m(patched)−m(mismatch)]/[m(clean)−m(mismatch)]`를 계산한다. `m`은 correct-video retrieval, correct-caption retrieval, teacher-joint retrieval 또는 target-space output metric이다. 분모가 사전 tolerance 이하이면 해당 sample-stage의 normalized recovery를 결측 처리하고 raw difference를 별도 보고한다. Wrong-stimulus activation, random stage/token과 동일 크기 patch를 matched null로 사용한다. Video/caption retrieval과 affect output이 함께 회복되고 matched null을 넘을 때만 functional use를 주장한다.

## 9.7 primary student model-reliance test: predefined anatomical network perturbation

ROI-wise PCA와 participant-specific adapter가 ROI token identity를 보존한 경우에만 이 분석을 실행한다. Schaefer/Tian atlas에서 결과를 보기 전에 정의한 소수의 anatomical network group을 대상으로 하며, 결과에 따라 `visual`, `semantic`, `affective` 같은 functional 이름을 사후 부여하지 않는다.

Primary perturbation은 held-out set에서 해당 network의 ROI token을 participant 안에서 다른 stimulus의 token으로 공동 permutation해 marginal distribution을 보존하면서 stimulus-specific information을 끊는 것이다. 각 perturbation 전후의 다음 변화를 계산한다.

- teacher-joint retrieval의 저하
- video retrieval의 저하
- caption retrieval의 저하
- 34-D affect-profile readout의 저하

Training-fold mean-token replacement와 leave-one-network-out refit은 robustness다. Drop의 절대값과 `Full−Direct`, `Full−Shuffled` 차이를 participant/seed별로 보고한다. 효과가 replacement 방식이나 seed에 따라 방향이 뒤집히거나 matched null perturbation과 구별되지 않으면 reliance 해석을 철회한다. 이 분석은 trained model의 input reliance를 검정하며 해당 network의 인간 정서에 대한 신경 인과성을 주장하지 않는다. 개별 ROI 전수 지도와 모든 network 조합의 Shapley 분석은 confirmatory 범위에 포함하지 않는다.

## 9.8 interpretation gate and inference

Mechanistic interpretation은 다음 두 gate를 모두 통과할 때만 confirmatory로 유지한다.

1. Full-guided 34-D clean readout이 training-fold mean-profile baseline과 mandatory linear/reduced-rank baseline을 넘는다.
2. 관련 video, caption 또는 teacher-joint retrieval이 stimulus-permutation null을 넘는다.

Gate가 실패해도 모든 결과는 보고하지만 teacher patching과 student ROI/network perturbation을 exploratory model diagnostics로 분류한다. Affect performance만 개선되고 relation formation, retrieval과 intervention evidence가 수렴하지 않으면 더 나은 decoder 또는 generic privileged-supervision effect로 제한한다.

Stimulus labels를 공동 permutation해 retrieval/CKA null을 만들고, participant를 cluster로 bootstrap한다. 자극쌍을 독립 observation으로 세지 않는다. Teacher conditional-source contrast, mismatch × stage, activation-patch × readout, student condition contrast와 network × readout을 사전 정의한 family로 나누어 multiple-comparison correction을 적용한다. Reference 간 CKA 차이는 같은 held-out stimuli에 대한 paired statistic으로 검정하며 CKA만으로 success를 판정하지 않는다. Seed는 inferential sample로 세지 않는다.

# 10. Analysis 3 — Functional readout

## 10.1 질문

Analysis 2에서 회복된 관계 구조가 brain-only 34-D normative profile prediction을 실제로 개선하는가?

## 10.2 target별 지표

- 34-D primary: 각 held-out stimulus에서 true/predicted profile의 Pearson correlation을 Fisher z 변환해 participant별 평균
- 34-D mandatory baseline: outer-training mean profile을 모든 held-out stimulus에 예측
- 34-D secondary: Brier score, RMSE, calibration, dimension-wise across-stimulus correlation의 macro-Fisher-z. training-fold base-rate를 제거한 residual profile correlation은 robustness
- 14-D·VA-2·VAD-3 primary: 차원별 across-stimulus correlation의 macro-Fisher-z
- 14-D·VA-2·VAD-3 secondary: 원척도 RMSE, concordance correlation coefficient; valence, arousal, dominance 개별 결과
- noise ceiling: repeated-test reliability로 계산하며 ceiling-normalized score는 보조로 보고

## 10.3 주 대비

1. Full-guided vs Direct
2. Full-guided vs Shuffled-guided

두 대비가 같은 방향이고 teacher ladder의 modality 대비 및 Analysis 2의 joint/visual/semantic recovery와 수렴해야 aligned multimodal guidance의 기능적 역할을 주장한다. Full vs Shuffled가 지지되지 않으면 privileged supervision 또는 label smoothing 이득으로 해석하고 content-specific organization으로 주장하지 않는다.

## 10.4 geometry–function 연결

participant별·seed별 readout 향상과 held-out geometry 변화의 대응을 기술한다. 표본 수가 작으므로 단순 상관 하나를 증거로 삼지 않고, pre-specified mediation이나 인과 해석을 하지 않는다. 방향 일관성과 bootstrap CI를 보고한다.

## 10.5 independent target-space analysis

34-D와 별도의 random initialization, teacher, student, head, target transform과 OOF cache를 사용해 14-D를 학습한다. VA-2와 VAD-3도 서로 및 14-D와 parameter를 공유하지 않는 별도 model이다. split, architecture candidate, Direct/Full/Shuffled condition과 λ 후보 grid만 공통으로 유지한다. target 사이의 raw performance는 비교하지 않고, 각 target 안의 `Full−Direct`, `Full−Shuffled`, within-target standardized gain과 참가자별 방향만 비교한다. 14-D는 alternative ontology에 대한 prespecified secondary analysis이고, VA-2/VAD-3는 nested low-dimensional controls다. 어느 target의 성공도 34-D 실패를 대체하지 않는다.

해석 규칙은 다음과 같다. 모든 target에서 두 대비가 지지되면 guidance가 core affect에서 fine-grained profile까지 일반화될 가능성을 지지한다. VA/VAD에서만 지지되면 효과를 broad polarity·activation·control로 제한한다. 14-D와 34-D에서만 지지되면 broad appraisal과 fine-grained profile에 공통되지만 저차원 core만으로 환원되지 않는 효과로 해석한다. 34-D에서만 지지되면 category-profile-specific effect, 14-D에서만 지지되면 broad appraisal에 특이적인 효과로 제한한다. `2D<3D<14D<34D` 같은 raw 성능 순서는 theory evidence로 사용하지 않는다.

## 10.6 replication

primary cohort에서 architecture, feature checkpoint, layer, λ, k, metric을 동결한 뒤 replication cohort에 적용한다. 참가자별 adapter만 사전 규칙으로 적합한다. 동일/중첩 자극을 사용하므로 결론은 participant-level replication으로 제한한다.

# 11. baseline, optimization, reproducibility

| ID | 항목 | 사전 확정 |
|---|---|---|
| M1 | linear baseline | 동일 ROI-PCA 입력의 multi-output ridge 또는 reduced-rank regression |
| M2 | architecture gate | small encoder가 nested held-out validation에서 linear baseline을 안정적으로 넘지 못하면 단순 모델을 주 결과로 승격 |
| M3 | seeds | 최소 5개. 모든 주 조건에 동일 seed 집합 사용 |
| M4 | early stopping | validation metric만 사용; test를 보며 중단하지 않음 |
| M5 | parameter budget | 세 student 조건 동일. Primary 34-D B/BV/BS/BVS/shuffled teacher는 동일 brain encoder/head와 matched fusion capacity를 사용하고 parameter 수를 별도 보고 |
| M6 | leakage audit | stimulus hash와 fold ID를 모든 feature/brain/label cache에 저장하고 split 교집합 0을 자동 검사 |
| M7 | reporting | 참가자별 점, seed 분산, absolute performance, paired difference, CI를 함께 보고 |

# 12. confirmatory와 exploratory의 경계

## Confirmatory

- Analysis 1의 세 nested content models와 세 주 대비
- Analysis 2의 primary 34-D B/BV/BS/BVS/shuffled teacher ladder, correct–mismatched relation-formation contrast, student held-out joint/video/caption retrieval, teacher activation patching, 사전 정의 anatomical-network perturbation
- Analysis 3의 34-D primary metric과 Full−Direct/Full−Shuffled 대비
- 별도 학습한 14-D의 Full−Direct/Full−Shuffled alternative-ontology 대비
- 별도 학습한 VA-2와 VAD-3의 compact nested-control 대비
- independent participant replication

## Exploratory 또는 supplementary

- neighborhood preservation과 exemplar montage의 세부 분류
- 개별 ROI별 전수 지도 및 post hoc functional naming
- nonlinear/RBF CKA
- linear CKA의 단독 mechanism 해석
- archetypal analysis
- alternative video/language model
- visual/semantic auxiliary loss를 직접 사용하는 multi-task student
- 14-D·VA-2·VAD-3의 layerwise geometry/content 전체 반복 분석
- target 간 absolute performance ranking
- trial-level temporal dynamics

Exploratory 결과는 confirmatory 가설의 성공/실패 판정을 바꾸지 않는다.

# 13. 해석 규칙

| 관측 | 허용되는 해석 | 금지되는 해석 |
|---|---|---|
| Analysis 1만 성공 | tested content spaces가 shared neural response를 예측 | emotion이 sensory+semantic으로 환원됨 |
| Analysis 2의 relation formation과 inheritance만 성공 | guidance가 model latent relations를 바꿈 | 그 관계가 output에 사용됨 또는 brain의 native geometry 자체임 |
| Retrieval과 intervention이 함께 성공 | tested information이 고정된 model computation에 사용됨 | 인간 뇌에서 같은 경로가 인과적으로 작동함 |
| Analysis 3만 성공 | privileged guidance가 brain-only prediction을 개선 | paired content relation이 원인임 |
| Full > Direct이고 Full ≈ Shuffled | generic regularization/soft target 가능성 | content-specific distillation |
| 세 분석과 replication이 모두 성공 | tested sensory–semantic relations가 shared response를 조직하고 model이 그 관계를 회복해 normative affect readout에 사용한다는 수렴 증거 | 참가자 주관 감정의 복원, 뇌에 대한 인과 개입, emotion의 완전한 정의 |

# 14. 동결 전 체크리스트

- [ ] participant ID crosswalk 확인
- [ ] stimulus file hash crosswalk와 2,180/2,181 차이 문서화
- [ ] primary run/fold 및 repeated-test 구조 확인
- [ ] 34-D/14-D 결측·분포 확인 후 변환 동결
- [ ] 34-D raw proportion의 정의와 category별 `k,n` 가용성 확인
- [ ] 14-D column name, rating direction, scale, VA-2/VAD-3 열 대응을 codebook에서 확인
- [ ] target별 teacher/student/head/standardizer/OOF cache의 parameter-sharing 0 assert
- [ ] fMRI response estimate와 ROI-PCA reliability 확인
- [ ] ROI-wise PCA와 participant adapter가 ROI token identity를 보존하는지 확인
- [ ] anatomical network grouping, perturbation null, replacement rule을 outcome 확인 전에 동결
- [ ] correct/video-swap/caption-swap/both-swap 생성 규칙과 permutation 수 동결
- [ ] activation-patching stage, token scope, recovery metric, denominator tolerance와 matched null 동결
- [ ] mechanistic interpretation gate의 baseline 및 null 계산 pipeline 확인
- [ ] feature checkpoint/layer/pooling 동결
- [ ] teacher OOF cache leakage unit test 통과
- [ ] teacher B/BV/BS/BVS/shuffled의 encoder·fusion capacity parity 확인
- [ ] 세 student 조건의 parameter/schedule parity 확인
- [ ] visual/semantic readout이 student training loss에 포함되지 않았음을 config로 확인
- [ ] held-out exemplar 선택 규칙과 retrieval metric을 outcome 확인 전에 동결
- [ ] inference code가 stimulus pair를 독립 표본으로 세지 않는지 확인
- [ ] primary cohort 결과 확인 전에 replication pipeline manifest 생성
