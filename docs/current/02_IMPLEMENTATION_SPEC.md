# EmoBrain 구현·분석 명세

_2026-10-06 · 서버 경로와 실행 결과는 현장 audit 후 채운다 · 미확정 값은 임의로 확정하지 않는다_

---

## 📋 1. 데이터 계약과 확인 범위

### Cohort와 관측 단위

계획상의 primary는 Mind captioning/Horikawa 2025의 video-viewing cohort, replication은 Horikawa 2020 cohort다. 원문은 각각 6명과 5명을 기술한다. 개인 식별자와 cohort 간 참가자 중복 여부는 서버 manifest 및 원자료 설명으로 다시 확인한다. Imagery data는 사용하지 않는다.[^1][^2]

원문 수준에서 확인한 사항은 다음과 같다. 서버에 있는 derivative가 원문과 동일하다는 뜻은 아니다.

| 항목 | 2025 원문 | 2020 원문 |
|---|---|---|
| Unique video | 2,180 | 2,181 |
| 원래 video 목록 | 2,196 | 2,196 |
| Presentation 구성 | Training 60 runs, test 10 runs | 61 runs |
| 반복 test | 72 clips, 각 5회 | 중복 파일 제외 후 독립 반복 없음 |
| 원문 decoder 학습 | Test clips 제외 2,108 | 2,181 unique samples |
| 원문 CV | Run 묶음 outer 6, inner 5 | Run 묶음 outer 6, inner 5 |

2025의 72 test clips는 training session에도 등장하므로 그 presentation을 학습에 섞으면 안 된다. 실제 mapping을 검증한다. ‘2020은 한 번 제시’는 unique clip의 분석 sample이 한 개라는 뜻이며, 짧은 clip을 한 stimulus block 안에서 반복 재생하지 않았다는 뜻은 아니다.

2020 원문은 T1 co-registration 후 original 2-mm space로 resampling했다고 기술한다. 따라서 로컬 파일을 직접 확인하지 않고 ‘Horikawa 데이터는 MNI’라고 확정하지 않는다. 두 cohort의 실제 NIfTI header, affine, preprocessing report, atlas transform chain을 조사한다.

### Manifest 필수 필드

`stimulus_manifest`:

```text
cohort_id, raw_video_id, canonical_stimulus_id, file_hash,
duplicate_group, video_path, duration, fps, has_audio,
caption_source, caption_count, caption_hash,
normative_target_source, label_row_id, exclusion_reason
```

`observation_manifest`:

```text
cohort_id, participant_id, session_id, run_id, trial_id,
canonical_stimulus_id, onset, block_duration, repeat_index,
response_path, response_estimation_version, coordinate_space,
motion_qc, usable_flag, exclusion_reason
```

`split_manifest`:

```text
protocol_version, canonical_stimulus_id, connected_run_group,
outer_fold, inner_fold_scope, teacher_oof_fold_scope,
development_or_confirmatory, reserved_test_flag
```

Stimulus manifest의 한 행과 observation manifest의 한 행은 서로 다른 단위다. 하나의 stimulus-level label을 여러 participant 관측에 연결하는 구조를 명시한다.

Annotation은 stimulus-level normative target이다. 같은 자극의 여러 참가자에게 동일 label이 붙어도 독립적인 평정 횟수가 늘어난 것은 아니다. 동일 영상·caption·annotation의 정렬을 hash와 ID로 검사한다. 배열의 행 순서만 믿고 결합하지 않는다.

### Target codebook

34-D의 각 열 이름, selection proportion의 분모, 결측 의미, 표본별 rater 수를 기록한다. 모든 값의 합이 1인지 여부도 측정하되 합이 1이 아니라고 오류 처리하지 않는다. 14-D의 척도·방향·범위를 확인한다. VA와 dominance의 정확한 열을 표기하고, 대응 열이 없으면 외부 모델이 생성한 값으로 대체하지 않는다.

## 🔐 2. Split과 nested OOF

### Split의 원칙

Split은 run 구조와 canonical stimulus identity를 동시에 지킨다. 같은 clip의 다른 참가자 관측과 반복 presentation은 같은 stimulus split에 놓는다. 중복 clip이 여러 run에 걸치면 관련 run들을 연결 성분으로 묶거나 그 중복을 다루는 사전 규칙을 정한다. 연결 성분이 너무 커지면 조용히 stimulus random split으로 되돌리지 말고 feasibility를 보고한다.

**권고안:** 원문과 비교 가능한 run-grouped outer 6, inner 5를 우선 검토한다. 이는 최종 승인값이 아니다. 기존에 논의된 5/10-fold도 후보이므로 실제 연결 성분 수·표본 균형·계산량을 보고 결정한다. Teacher OOF fold 수는 outer K와 별개의 설정이다.

각 학습 scope의 모든 PCA, standardizer, feature selection, target scaling, probe, hyperparameter selection은 그 scope의 training data만 사용한다. Label 없이 fit하는 PCA도 전체 데이터 fit은 허용하지 않는다. Frozen pretrained encoder의 자극별 독립 feature 추출은 공통 cache로 허용한다.

Run grouping은 run 내부 인접 자극이 train/test로 나뉘는 문제를 줄인다. Run 경계의 잔여 HRF, nuisance 처리, 동일 순서의 공유 성분까지 자동 제거하지는 않는다. 순서 상관 및 boundary 영향은 QC로 검사한다. 알려진 `r≈−0.13`은 사용자 제공 수치이며 이번 전달본에서 재계산하지 않았다.

### OOF를 어디까지 중첩해야 하는가

Student의 outer test label을 teacher가 간접적으로라도 학습하면 안 된다. Inner validation으로 student 설정을 고를 때도, 해당 inner validation label이 inner training guidance에 섞이면 안 된다.

```text
for outer_fold:
    A = outer_training_groups
    E = outer_test_groups          # 최종 평가 전 접근 제한

    for student_candidate:
        for inner_fold within A:
            I = inner_training_groups
            V = inner_validation_groups

            # I 내부에서 teacher cross-fitting을 다시 수행
            guidance_I = make_teacher_oof(
                recipient_groups=I,
                allowed_training_groups=I,
                teacher_tuning_scope=I_only
            )
            fit every student transform on I
            fit student_candidate on I with guidance_I
            evaluate candidate on V using brain only

    select candidate using inner validation only
    guidance_A = make_teacher_oof(A, allowed_training_groups=A)
    fit selected student transforms and student on A
    evaluate once on E using brain only

    # Teacher 자체의 held-out 분석용 reference
    fit reference_teacher on A only
    analyze reference_teacher on E without fitting to E
```

`make_teacher_oof` 내부에서도 recipient fold를 teacher 학습·전처리·hyperparameter selection에서 제외한다. Teacher hyperparameter를 전체 A의 recipient label까지 사용해 골랐다면 엄격한 OOF가 아니므로, recipient 제외 범위 안에서 tuning하거나 별도 개발 자료에서 동결한 설정을 사용한다.

계산 절약을 위한 cache 재사용은 training-ID 집합, fold scope, target, transforms, checkpoint hash가 동일할 때만 허용한다. CPU/GPU 비용을 줄이려고 outer 경계를 합치지 않는다.

### 누출 자동 검사

- Recipient canonical ID와 teacher fit/tuning ID 교집합 = 0
- Outer test ID와 모든 training/OOF/probe fit ID 교집합 = 0
- Inner validation ID와 해당 inner-training teacher fit/tuning ID 교집합 = 0
- 같은 자극을 다른 참가자를 통해 학습하지 않았음
- Caption aggregation·target scaler·PCA fit scope가 일치함
- Test labels를 바꿔도 training artifact hash가 바뀌지 않는 synthetic 검사
- Repeated test clips의 training-session 관측도 최종 학습에서 제외됨

## ⚙️ 3. fMRI와 feature pipeline

### Response 추정과 ROI

먼저 기존 derivative의 response 정의를 재현한다. 자극당 한 벡터라는 인터페이스는 단순 평균을 강제하지 않는다. 현재 권고는 HRF 지연을 반영한 원문 방식 평균을 출발점으로 유지하되, 정확한 estimator는 D04 audit 후 동결하는 것이다. 연속 run 시계열·events·confounds는 보존한다. 평균 구간, TR, 휴지기 포함, nuisance, 정규화 scope와 GLM 대안의 조건은 [전처리 검토](07_RESPONSE_ESTIMATION_REVIEW.md)에 기록한다. Raw timing이 충분할 때 GLMsingle 등 대체 추정법을 검토하되 이를 필수 교체로 간주하지 않는다.[^3] 최종 test 반복 자료를 보고 preprocessing을 선택하면 label-blind라도 평가 대상의 특성에 맞춘 선택이 된다. 별도 개발 자료로 고르거나 사전에 단일 규칙을 동결한다.

ROI는 해부학적 위치 추적과 제한된 token 수를 위해 사용한다. Schaefer cortical + Tian subcortical은 기존 후보이며 정확한 resolution, version, native mapping은 미확정이다.[^4][^5] Label 효과를 보고 ROI를 선별하지 않는다. Missing ROI mask, 최소 voxel 수, PCA rank 제한을 train scope에서 정한다.

권장 인터페이스:

```text
B[s,i,r,:] = response for subject s, stimulus i, ROI r
train-only voxel standardization
train-only ROI PCA or approved regularized projection
participant-specific ROI map P[s,r]
ROI token + anatomical ROI identifier + valid-mask
```

Participant-specific map은 학습 참가자에게만 fit된다. 새 참가자에 그 map이 자동으로 생기지는 않는다. 새 참가자 adapter fitting에 필요한 자료·label 사용 범위는 replication protocol에 명시한다. 단순 participant ID token이나 stimulus ID를 정답 shortcut으로 넣지 않는다.

### Content feature

`L`: luminance/color, spatial-frequency/orientation-energy, motion-energy의 사전 지정 작은 집합. Depth는 pretrained semantics와 얽힐 수 있어 exploratory만 허용한다. 어떤 low-level feature가 무엇을 통제하는지 기록한다.

`V`: frozen V-JEPA 2 checkpoint, input resolution, frame sampling, crop, layer, temporal pooling, original dimension을 manifest에 기록한다. 원래 audio가 있어도 무음 시청 조건이면 audio branch를 만들지 않는다.

`S`: 원본 human caption을 frozen sentence encoder로 변환한다. 자극별 모든 유효 caption을 사전 정한 규칙으로 집계한다. 단순 embedding mean은 후보 기본안이며, 실제 caption 수·길이·언어를 확인한 뒤 동결한다. Affect label로 ‘좋은 caption’을 고르지 않는다.

Checkpoint·software version·license·feature hash를 저장한다. Encoders가 이 연구의 affect label로 fine-tune되지 않았다는 뜻이지 pretraining 자체에 정서 의미가 없다는 뜻은 아니다.

### Caption shortcut controls

Primary는 원문 caption을 유지한다. Robustness는 동결한 좁은 affect lexicon을 masking한 caption이다. 감정어 presence/count만 사용하는 low-capacity baseline도 둔다. `cute/funny`처럼 애매한 항목은 narrow와 broad lexicon을 구분한다. Masking은 문장 의미와 embedding 분포를 바꿀 수 있어 결과 감소 전체를 lexical leakage로 해석하지 않는다.

사용자 제공 7.1%/46%/10%는 검증 대기 수치다. Caption-level 비율과 video-level 비율, tokenizer, lexicon, 수작업 확인 표본을 모두 다시 기록한다.

## 🧠 4. Teacher와 student

### Teacher 기본안

```text
brain ROI tokens -- trainable participant map --> brain queries
video features  -- trainable projector --------> visual keys/values
caption features -- trainable projector -------> semantic keys/values

fused brain state = brain residual + content-conditioned update
target head reads pooled fused brain state
```

Head로 가는 content-only direct skip은 기본안에서 제외한다. 그러나 brain query 구조 자체가 brain 사용의 증거는 아니다. B-only에서 content attention이 비어도 유효한 residual brain pathway가 남아야 한다. All-masked attention의 NaN을 unit test로 막는다.

Projector width, token 수, normalization, trainable parameter 수를 기록한다. 서로 같은 norm 또는 token 수가 곧 같은 정보량/심리적 비중을 의미하지는 않는다. Primary 후보 `brain_scale=1`은 임의 증폭을 피하기 위한 프로젝트 운영 선택이다.

기존 명세의 gated token pooling architecture ablation도 pilot 후보로 기록한다. 이를 전체 본실험에서 mandatory로 유지할지, 개발 단계의 단일 대체 fusion 비교로 제한할지는 D05에서 결정한다. 본 전달본이 해당 비교를 실행 완료하거나 사용자 승인 없이 삭제한 것으로 해석하지 않는다.

### 필수 teacher controls와 선택적 확장

34-D의 기본 control set:

| 이름 | 입력 | 묻는 질문 |
|---|---|---|
| `T_B` | Brain | 뇌 단독 readout |
| `T_BV` | Brain + video | Caption 없는 안내 |
| `T_BS` | Brain + caption | Video 없는 안내 |
| `T_BVS` | Brain + video + caption | 전체 multimodal 안내 |
| `T_VS` | Video + caption | Brain shortcut 대안 |
| `T_BVS_SHUF` | Brain + 잘못 짝지은 content | Pairing 대안 |

가능한 한 width, head, budget, tuning 기회를 맞춘다. `T_VS`는 brain이 없는 일정 query/token을 사용하고 participant/stimulus ID를 제공하지 않는다. 같은 stimulus의 label을 참가자 수만큼 반복하여 VS에 다른 weighting을 부여하지 않는다. Input 차이에 따른 capacity 차이는 완전히 제거되지 않을 수 있으므로 보고한다.

Teacher shuffled control은 training 범위 안에서 video와 caption을 같은 permutation으로 이동한다. 이는 무작위 content가 정답에 정렬되지 않는 대조이지 모든 종류의 regularization을 동일하게 맞춘 대조가 아니다.

14-D/VA/VAD에는 BVS teacher와 세 student 조건을 우선 적용한다. Full teacher ladder와 patching을 모든 target으로 복제하지 않는다. 이 target에서도 brain-grounded teacher를 주장하려면 그에 필요한 VS/brain-swap 검증을 추가하거나 주장을 제한한다.

### Student 세 조건

Student architecture 후보는 regularized linear/reduced-rank baseline, 1-block token mixer, 2-block token mixer로 제한한다. 큰 pretrained brain model이나 LLM을 기본 포함하지 않는다. 비선형 모델은 개발 validation의 이득과 안정성이 있을 때만 채택한다.

- `Direct`: normative label만 학습
- `Full-guided`: label + aligned BVS teacher OOF output
- `Shuffled-guided`: label + 잘못 짝지은 BVS teacher OOF output

모든 student는 brain-only다. 같은 split, seed, optimizer budget과 candidate grid를 사용한다. Primary 비교용 shuffled guidance는 full-guided에서 고른 λ를 그대로 적용하여 guidance 세기를 맞추는 방안을 권고한다. 조건별 최적화를 추가하면 별도 sensitivity로 표시한다.

‘Teacher에 brain을 넣었기 때문에 student가 좋아졌다’까지 주장하려면 `VS-guided student`와의 비교가 추가로 필요하다. 이는 이번 패키지의 **주장 의존적 권고**이며 자동으로 모든 target의 필수 실험을 늘리는 결정은 아니다.

### Loss 계약

34-D, dimension 수 `D=34`:

```text
p_T = sigmoid(logits_T)
p_S = sigmoid(logits_S)
L_label = mean_{i,s,d} [ -y_id log(p_isd) - (1-y_id) log(1-p_isd) ]
L_KD = mean_{i,s,d} (stopgrad(p_T_oof_isd) - p_S_isd)^2
L_student_full = L_label + lambda * L_KD
```

수치적으로는 logits 기반 안정적인 BCE 구현을 쓴다. Missing label mask를 적용하고 유효 dimension 수로 정규화한다. 참가자·자극별 불균형 sampling weight를 기록한다. Count 기반 binomial NLL은 rater count가 확인되었을 때만 sensitivity 후보로 둔다.

원래 normative proportion도 이미 graded/soft target이다. 따라서 이 설계의 차이를 ‘hard label을 soft label로 바꾼다’고 설명하지 않는다. 추가되는 것은 OOF teacher가 추정한 profile에 대한 안내다.

연속 target:

```text
y_z = (y - mean_train) / sd_train
L_label = mean_valid_dimensions (y_z - prediction)^2
L_KD = mean_valid_dimensions (teacher_oof_in_common_scale - prediction)^2
```

각 OOF teacher는 자기 training set으로 target scaler를 fit한다. OOF prediction을 먼저 원척도로 inverse-transform하여 저장하고, student 학습 scope의 scaler로 다시 변환한다. 서로 다른 fold의 z-score를 그대로 섞지 않는다. 원척도 OOF 값과 scaler hash를 둘 다 남긴다.

λ grid, learning rate, epoch, early stopping, rank, token width, seed 수는 개발 audit 후 freeze할 설정이다. 개발 결과를 보지 않고 임의의 ‘최적값’을 이 문서에서 지정하지 않는다.

### 학습 전략 계약 — Joint 기본, 추가 비교 허용

- **Joint 기본 방향 승인 (D20):** 처음부터 B/V/S를 결합해 affect prediction으로 teacher를 학습한다. Brain-first를 모든 run의 필수 준비 단계로 넣지 않는다.
- **Brain-first → Joint 추가 경로 승인 (D20):** 해당 teacher fit scope 안에서 brain 경로와 affect head를 먼저 학습하고 그 가중치를 이어받아 joint fitting한다. Warm-up epoch·학습률·초기화·freeze/unfreeze·총 update 수는 기록하며 구체 설정은 D08에서 결정한다. Frozen V/S encoder 원칙은 유지한다. 항상 별도 실험 두 벌을 수행해야 한다는 뜻은 아니다.
- **공유 Head 보조 loss (D21, 제안):** 동일 brain 경로와 동일 affect head를 사용하는 두 forward 경로다. 별도 B-only baseline 모델이나 student와 가중치를 공유한다는 뜻이 아니다.

```text
H_B = teacher_brain_path(B)
U_BVS = fusion(H_B, V, S)
p_B = output_activation(h(pool(H_B)))
p_BVS = output_activation(h(pool(U_BVS)))  # same h
L_T_candidate = L_affect(y, p_BVS) + eta * L_affect(y, p_B)
```

34-D는 sigmoid/soft BCE, 연속 target은 linear output/해당 fit scope의 standardized MSE다. 두 항은 **같은 target**이며 34-D와 14-D 공동학습이 아니다. 공유 head가 두 표현을 읽을 수 있도록 차원·pooling 계약을 맞춘다. eta, 공유 head 채택, dropout과의 병용은 미확정이며 새 primary loss로 자동 추가하지 않는다. Content dropout은 별도 후보로 남기고 모든 보완책을 한꺼번에 넣지 않는다. Brain-first와 보조 loss는 독립적인 설계 축이다.

**Warm-up 누출 방지:** 모든 teacher fit에서 warm-up·전처리·target scaler·checkpoint 선택부터 recipient canonical stimulus group의 모든 참가자 관측을 제외한다. Student inner validation과 outer test 등 해당 scope의 기존 제외 경계도 그대로 적용한다. 해당 프로젝트의 더 넓은 label scope로 학습한 checkpoint에서 시작하면 recipient-excluded OOF가 아니다. 공통 checkpoint를 재사용하려면 그 전체 학습 provenance가 현재 fit scope와 양립해야 한다. Scope ID, training-ID hash, warm-up checkpoint와 parent fit ID, scaler hash를 OOF cache provenance에 남긴다. 전략 변경 후 이전 cache를 이름만 바꿔 재사용하지 않는다.

**비교·탐색 기록:** 학습 순서 효과를 비교할 때 architecture·target·평가 행을 맞추고 warm-up까지 포함한 총 update/label exposure/tuning 기회를 보고한다. 계산량을 맞춘 joint 비교를 검토하고, 맞추지 못하면 추가 학습량이라는 대안 설명을 남긴다. 서로 다른 objective까지 바꾼 결과를 순서만의 효과로 귀속하지 않는다.

결과를 본 뒤 새 학습법을 시도하거나 최종 선택 모델을 바꿀 수 있다. 각 run은 별도 ID로 보존하고 parent run, 변경 이유, schedule/objective, 선택에 사용한 데이터·metric·시점, exploratory/independent-validation 지위를 남긴다. 개발 자료를 통한 선택을 우선하되 이미 열람한 test를 탐색에 사용했다면 선택 자료로 표시한다. 같은 test의 재평가나 선택 이후의 단순 재분할은 그 선택에 대한 독립 검증이 아니다. 기존 preregistration은 amendment로 남기며 사후 모델을 소급 primary로 표시하지 않는다. 이것은 실험 수정 금지가 아니라 선택·검증 분리와 정직한 보고의 계약이다.

## 🔍 5. Analysis 1·2의 실행 계약

### Analysis 1a: content encoding

Multi-kernel ridge/regularized linear encoding은 source별 복잡도를 조절하면서 중첩 model의 held-out prediction을 비교하기 위한 방법이다. PCM/RSA/CKA를 모두 primary로 추가하지 않는다. Kernel weights가 visual/semantic의 신경학적 ‘비중’이라고 해석하지 않는다.[^6]

Analysis 1a의 기존 핵심 대비는 `L+V − L`, `L+V+S − (L+V)`다. 1b 보강에 따라 이를 포함한 primary/secondary와 family는 D09/D16에서 재동결한다. `Full − L`과 대칭 조건부 `Full − (L+S)`는 보조다. ROI response target과 component aggregation은 freeze한다. Fold마다 PCA basis가 다르므로 component 좌표를 그대로 이어붙이지 않는다. Fold 내부 score 집계 또는 native voxel로 역변환한 prediction의 집계 중 한 규칙을 정한다.

### Analysis 1b: content–affect predictive overlap

2026-10-06 보강 방향 승인. C=[V,S], E=실제 normative profile, 공통 G=low-level L와 동결한 nuisance 처리로 네 모델 G, G+C, G+E, G+C+E가 동일 B를 예측한다. 34-D/14-D를 별도 실행하고 teacher prediction을 E로 쓰지 않는다.

[보강 문서](06_NEURAL_VALIDATION_AMENDMENT.md)의 공통 held-out SSE 기반 Q와 산식을 사용한다. Content_given_affect, affect_given_content, shared_predictive_component를 저장한다. 음수 contrast를 잘라내거나 correlation 차이를 설명 분산이라 부르지 않는다. 동일 평가 행·voxel·분모·가중치와 train-only scaling, inner tuning을 보장한다. ROI/rank/score aggregation은 D16에서 동결한다.

분산 분할은 예측적 중첩이며 인과적 매개가 아니다. Caption masking, original feature capacity, order nuisance는 기존 sensitivity/QC와 연결한다. 기존의 작은-n inference 미확정 상태를 보강 승인으로 해결된 것으로 취급하지 않는다.

### Teacher brain/content dependence

동일 held-out 자극에서 clean BVS, brain swap, video swap, caption swap을 비교한다. Brain swap은 같은 참가자 내 다른 canonical stimulus의 brain을 쓰고 V/S를 유지한다. Content swap도 다른 canonical ID를 사용한다. 동일 clip의 반복 관측을 donor로 고르지 않는다.

Run 내 derangement 또는 matching은 순서·norm 차이를 줄이기 위한 후보 규칙이다. ‘V/S에 통계적으로 조건부인 뇌 분포에서 뽑은 표본’이라고 부르지 않는다. Marginal signal을 보존해도 joint distribution은 깨질 수 있다. Mean replacement, 크기를 맞춘 random-token 교란 등으로 일반 손상 설명을 점검한다.

34-D primary reliance metric 후보는 `ΔSoftBCE = loss_corrupt − loss_clean`이다. 연속 target은 `ΔMSE`. 양수는 악화를 뜻한다. Within-profile correlation과 content retrieval은 보조적 수렴 지표다. `BVS vs VS` 비교는 held-out 예측의 조건부 증분을 묻고 swap은 고정된 모델의 의존성을 묻는다. 서로 다른 estimand다.

### Frozen probes와 retrieval

Student의 adapter, block 1, block 2(존재할 때), final latent를 export한다. Train/validation에서 low-capacity linear/ridge probe를 fit하여 `z → V`, `z → S`를 예측하고 고정된 held-out candidate set에서 retrieval한다. Test brain의 여러 관측은 같은 canonical target에 대응하며 duplicates를 별도 후보로 늘리지 않는다.

Video retrieval: 예측 feature와 frozen V candidate의 similarity로 순위를 계산한다. Semantic retrieval: 예측 feature와 caption aggregate S candidate로 순위를 계산한다. Top-k, median rank 또는 normalized rank, 후보 수 N과 null 규칙을 함께 저장한다. 후보가 M개면 single-target top-1 chance가 1/M이라는 단순 계산만으로 복잡한 permutation inference를 대체하지 않는다.

동일 probe capacity·regularization grid·candidate set을 조건마다 적용한다. 최종 representation뿐 아니라 raw/adapter brain baseline과 비교한다. Affect-output만을 입력으로 한 probe는 ‘내용이 단지 예측 affect profile의 재표현인가?’를 묻는 claim-dependent control 후보다. Probe 성능만으로 학습 과정 전체를 식별했다고 말하지 않는다.

Teacher-joint retrieval은 보조다. 각 outer fold에서 하나의 고정 reference teacher를 정의하여 train/test 모두 같은 좌표로 만든다. 여러 OOF teacher의 latent를 같은 좌표인 것처럼 concatenate하지 않는다. Reference teacher의 train latent는 in-sample임을 명시한다. Joint latent에는 brain 자체가 들어가므로 단순 recovery는 공유 입력 때문에 높을 수 있다. Visual/semantic 독립 reference를 중심 근거로 삼는다.

### Affect-neighborhood content retrieval: 채택된 보조 분석

사용자가 Analysis 2의 보조 분석으로 채택했다. D18에서 평가 규칙을 동결한 뒤 수행하며 자동 primary 승격은 하지 않는다. Held-out query마다 전체 34-D 또는 14-D E에서 가까운 다른 canonical 자극 m개와 정답으로 candidate set을 구성한다. Scaling/거리/m/tie/결측 규칙은 training/development에서 동결한다. Test E는 고정된 평가 candidate 생성기에만 쓰고 prediction/probe fitting에 전달하지 않는다. 이는 완전한 affect matching 또는 조건부 독립 검정이 아니다.

같은 후보로 Direct/Full/Shuffled, raw/adapter baseline 및 affect-output-only probe를 필수 비교로 평가한다. Candidate coverage와 content 차이를 먼저 확인한다. Pair 재사용을 독립 n으로 세지 않고 후보 graph·run 구조를 고려한 null을 검토한다. 전체 후보 retrieval은 유지한다. 목적·실패 기준은 06 문서에 있다.

### CKA와 선택적 개입

Linear CKA는 동일 held-out stimulus 행을 정렬한 `stage × reference` matrix로 계산한다. Stimulus subset, centering, participant 집계, estimator를 동결한다. Reference는 V, S, affect annotation, teacher-joint이며 joint 해석 한계를 병기한다. Different checkpoint latent를 먼저 이어붙인 CKA는 금지한다. Fold별 CKA를 집계하고 fold를 독립 참가자로 세지 않는다.[^7]

Teacher selective patching은 일부 brain ROI/token 또는 사전에 특정한 경로만 바꾸고 downstream을 재계산한다. Whole brain state나 final latent 전체 복원은 QA다. ‘다른 activation을 모두 고정’하여 downstream 갱신까지 차단하면 유효한 복원 실험이 아니므로 개입 위치와 재계산 경계를 명시한다.

Student ROI reliance는 사전 정의 해부학적 network token을 교란했을 때 content retrieval 및 affect readout 변화다. Target으로 골라낸 ‘affective ROI’ 이름을 사후 부여하지 않는다. 같은 token 수, 가능한 signal 규모가 맞는 random sets를 반복하며 clean loss가 높아 생기는 해석 문제를 보고한다.

Primary는 raw paired difference를 권고한다. Normalized recovery는 clean–corrupt 차이가 작을 때 불안정하므로 denominator threshold와 부호 규칙을 사전 정의한 보조 지표다. Clean/sham/null/all-state QA를 함께 저장한다.[^8]

### Analysis 2d: independent neural validation

2d의 독립 검증 원칙은 승인, content-side bridge 구현은 D17 개발/동결 대상이다. 최소 계약은 다음과 같다.

```text
T = training/development stimulus groups; H = held-out groups shared across cohorts
fit teacher/student and content probes on discovery-cohort T only
freeze selected student stage/rank using development evidence only
fit small bridge g: C_T -> z_T within T; validate fidelity inside T
q_i = g(C_i)  # content-recoverable projection, NOT actual student latent
fit neural readout W_R: q_T -> validation-cohort B_R,T
predict W_R(g(C_H)); compare only now with B_R,H
```

H의 brain/affect는 discovery model, bridge, neural map, selection 어디에도 사용하지 않는다. 평가 경로는 content만으로 계산하며 target B_H를 입력받지 않는다. W_R calibration에 R,T를 사용했다고 명시하고 zero-shot transfer라 부르지 않는다. C-derived q와 original C, Direct-derived q를 공통 nuisance/ROI/split/rank·budget 조건에서 비교한다. 모든 layer·ROI·target의 새 sweep은 금지한다.

Bridge fidelity가 불충분하면 ‘모델 표현의 뇌 검증’ 해석을 중단하고 실패를 보고한다. q는 C의 함수이므로 새로운 정보량을 입증하지 않으며, C 대비 이득도 inductive bias/regularization 차이일 수 있다. 같은 B로 만든 z와 B의 대응은 독립 증거로 세지 않는다. 2d와 Analysis 3의 cohort pipeline replication은 별도 estimand다.

## 📊 6. Readout, 통계, replication

### Affect metrics

34-D: stimulus 내 34개 값의 Pearson correlation을 Fisher-z 집계하는 기존 primary readout을 유지하되, training mean-profile baseline과 비교한다. Constant vector 또는 분산이 매우 작은 profile의 처리 규칙을 freeze한다. Brier/MSE, RMSE, calibration, category별 across-stimulus correlation도 보고한다. Base-rate-residualized correlation은 training mean만 사용한다.

14-D: dimension별 across-stimulus correlation과 macro-Fisher-z, original-scale RMSE를 보고한다. VA-2/VAD-3도 각 dimension metric을 사용한다. 특히 2-D vector 안의 Pearson correlation은 비퇴화한 경우 사실상 ±1이므로 유용한 primary metric으로 쓰지 않는다. 서로 다른 target의 raw score만으로 emotion theory 우열을 판정하지 않는다.

### 통계적으로 아직 동결되지 않은 것

참가자 일반화를 주장할 때 독립 참가자는 6명/5명 수준이다. Seed, fold, ROI, 자극 수가 참가자 수를 늘려주지 않는다. 대칭적인 부호 뒤집기 양측 exact test의 최소 p는 n=5에서 `2/32=0.0625`, n=6에서 `2/64=0.03125`다. 이는 직접 조합 계산이며 어떤 test를 사용해도 절대 유의할 수 없다는 뜻은 아니다.

Participant × stimulus 변동을 분리한 계층 모형은 검토 후보이나 작은 참가자 수의 한계를 없애지 않는다. Prior sensitivity, null simulation, interval coverage, 효과 추정 대상이 필요하다. CKA나 across-stimulus correlation 같은 집계량을 stimulus 독립 관측처럼 mixed model에 넣지 않는다. Representation inference에는 participant와 condition 일반화를 구분하는 방법론을 참고한다.[^9]

현재 숫자로 된 direction gate와 multiple-testing rule은 **미확정**이다. 이전 `5/6`, `4/5` 또는 ‘bootstrap CI가 0을 넘으면 confirmatory’ 같은 제안을 확정 규칙으로 복사하지 않는다. 어떤 family를 어떤 주장으로 묶는지 정한 뒤 보정한다. 사전 방향 가설 없이 작은 n을 우회하려고 사후 one-sided test로 바꾸지 않는다.

자극 순열은 해당 참가자들에서의 stimulus association을 검정할 수 있지만 참가자 모집단 일반화와 같지 않다. Exchangeability를 run/order structure에 맞춰 검토한다. Re-fitting이 필요한 null과 fixed-model retrieval row shuffle을 구분한다.

### Replication과 reliability

권고 primary replication은 다른 cohort에서 동결한 분석 절차·모델 선택 규칙을 별도 fit하여 핵심 효과를 재현하는 것이다. Strict transfer는 backbone 고정 후 새 participant adapter만 학습하는 별도 질문이다. 두 방식은 혼용하지 않고 승인받는다. 어떤 방식도 공유 영상이면 unseen-stimulus-distribution replication이 아니다.

2025 반복 관측은 freeze 후 reliability와 single-trial/averaged 성능을 별도 보고하는 데 쓴다. 2020에 없는 반복 기반 noise ceiling을 2025 값으로 대신하지 않는다. Cross-participant agreement는 공유 반응의 일관성이지 within-participant test–retest ceiling이 아니다.

## 📦 7. 산출물·검증 계약

모든 run은 `cohort / target / outer_fold / condition / seed / protocol_version` namespace를 갖는다. 저장 대상은 config, training ID hash, preprocessing hash, fitted transforms, checkpoint, metrics, held-out predictions, latent export, probe, intervention donor IDs, figure source data다.

필수 unit/integration tests:

```text
test_canonical_id_alignment
test_duplicate_and_repeat_grouping
test_nested_oof_excludes_outer_and_inner_validation
test_train_only_transforms
test_continuous_oof_scaler_roundtrip
test_brain_only_inference_no_content_access
test_missing_modality_attention_is_finite
test_target_parameter_and_cache_isolation
test_probe_fit_excludes_test
test_single_reference_teacher_coordinates
test_selective_patch_recomputes_descendants
test_full_state_restore_is_qa_only
test_retrieval_candidate_deduplication
test_no_pseudoreplication_of_seeds_or_folds
test_analysis1b_common_rows_denominator_and_score
test_analysis1b_signed_components_not_clipped
test_analysis2d_common_test_ids_excluded_from_all_fits
test_analysis2d_evaluation_predictor_has_no_test_brain_or_affect
test_affect_neighborhood_labels_are_evaluation_only
```

최종 test 성능을 로그로 출력한 실험은 이미 evaluation exposure가 발생한 것으로 기록한다. 해당 결과를 보고 새 방법을 고르면 exploratory로 표시하거나 별도의 untouched evaluation 자료를 사용한다. ‘파일을 열지 않았다’와 ‘metric을 이미 봤다’를 혼동하지 않는다.

## 🔗 8. 근거

[^1]: Horikawa (2025). Mind captioning: Evolving descriptive text of mental content from human brain activity. Methods. https://doi.org/10.1126/sciadv.adw1464
[^2]: Horikawa et al. (2020). The neural representation of visually evoked emotion is high-dimensional, categorical, and distributed across transmodal brain regions. Transparent methods. https://doi.org/10.1016/j.isci.2020.101060
[^3]: Prince et al. (2022). Improving the accuracy of single-trial fMRI response estimates using GLMsingle. https://elifesciences.org/articles/77599
[^4]: Schaefer et al. (2018). Local-global parcellation of the human cerebral cortex from intrinsic functional connectivity MRI. https://doi.org/10.1093/cercor/bhx179
[^5]: Tian et al. (2020). Topographic organization of the human subcortex unveiled with functional connectivity gradients. https://doi.org/10.1038/s41593-020-00711-6
[^6]: Nunez-Elizalde et al. (2019). Voxelwise encoding models with non-spherical multivariate normal priors. https://doi.org/10.1016/j.neuroimage.2019.04.012
[^7]: Kornblith et al. (2019). Similarity of neural network representations revisited. https://proceedings.mlr.press/v97/kornblith19a.html
[^8]: Heimersheim and Nanda (2024). How to use and interpret activation patching. https://arxiv.org/abs/2404.15255
[^9]: Schütt et al. (2023). Statistical inference on representational geometries. https://doi.org/10.7554/eLife.82566
