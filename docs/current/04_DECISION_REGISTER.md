# EmoBrain 결정·정정 기록

_2026-10-06 · 기존 설계의 복원과 이번 검토의 제안을 분리한 기록 · 이 문서 자체가 preregistration 승인은 아님_

---

## 🔄 0. 2026-10-06 승인된 보강

Analysis 1b의 실제 뇌 content–affect 설명력 비교와 Analysis 2d의 독립 neural validation을 연구 방향에 반영한다. 기존 세 분석은 유지하며 큰 Analysis 4·5를 추가하지 않는다. 구현 권고, 보조 후보, 본실험 동결은 구분한다. [06 보강 문서](06_NEURAL_VALIDATION_AMENDMENT.md)에 각 항목의 여섯 질문 rationale, 산식, split, 반례·한계가 있다.

Affect-neighborhood retrieval은 후속 사용자 요청으로 Analysis 2의 정식 보조 분석에 채택됐다. 결정 변경의 근거는 사용자의 명시적 포함 요청이다. 효과가 검증되었거나 primary가 승인되었다는 뜻은 아니다. 원본 overview PNG v1은 보강 전 상태로 보존한다. 본 업데이트가 이미 등록된 prereg 또는 노출된 test를 소급 변경하지 않는다.

## 📋 1. 유지하는 핵심 원칙

후속 합의: Joint 학습을 기본으로 유지하고 Brain-first → Joint를 필요에 따라 비교하는 방향을 승인했다. 공유 Affect Head 보조 loss는 여전히 제안이다. D20/D21, C10/C11과 R16에 학습 전략·해석·탐색 범위를 기록한다.

1. 뇌 중심 neuroscience 연구이며 prediction 성능만으로 끝내지 않는다.
2. 감각·의미가 감정에 기여한다는 문제의식은 유지하되 감정 전체의 환원적 등식을 검정했다고 주장하지 않는다.
3. Teacher에는 brain, video, caption을 모두 넣는다. Student는 brain-only다.
4. Visual과 semantic task는 기본적으로 frozen post-training probe/retrieval이며 student 학습 loss에 추가하지 않는다.
5. 34-D와 14-D는 독립 학습한다. VA-2와 VAD-3도 실제 codebook이 허용하면 독립 비교한다.
6. Normative annotation은 fMRI 참가자의 자기보고가 아니다.
7. 미래 subject-specific component는 brain token 확장으로 기록하되 현재 adapter와 구분한다.
8. Imagery, 즉시 emotion foundation model 구축, 불필요한 object/event 전용 branch는 현재 범위 밖이다.
9. 분석을 새로 포함할 때 이유·대안·반례·해석 한계를 먼저 적는다.

## 🔄 2. 이번 정리에서 바로잡은 부분

### C01. OOF는 student의 nested split 안에서 생성

기존 문서의 ‘outer training 내부 OOF’ 원칙을 더 명확히 했다. Student inner validation을 고를 때 그 validation label을 본 teacher가 inner-training guidance를 만들면 간접 누출이 된다. 따라서 매 scope에서 recipient와 validation/test를 모두 제외한다. Continuous OOF prediction은 fold별 z-score를 섞지 않고 원척도로 복원한 뒤 student scaler로 옮긴다.

**판단 변경의 이유:** Teacher/student 두 단계의 정보 흐름을 따라가면 단순 OOF 표기만으로 모든 validation 경계가 보호되지 않는다. 기존 cache는 provenance를 확인하기 전에는 유효하다고 가정하지 않는다.

### C02. Whole-state restoration gate 폐기

기존의 ‘brain 전체를 clean state로 복원하고 성능 회복 → 독립 기전 증거’는 강한 주장이다. 유일하게 바꾼 전체 입력을 원상복구하면 clean output이 돌아오는 것은 계산 구조상 예상된다. 따라서 전체 복원은 QA로 두고 일부 token/ROI/path patch만 mechanistic candidate로 평가한다.

**판단 변경의 이유:** 입력 복구와 부분 계산 경로 검증을 구분해야 한다. Downstream은 재계산해야 하므로 ‘다른 activation 모두 고정’이라는 구현 문구도 정정한다.

### C03. OOF teacher latent 좌표의 혼합 금지

각 fold teacher가 만든 latent는 학습된 좌표계가 서로 다를 수 있다. Output vector는 공통 target 좌표라 합칠 수 있지만 latent는 같지 않다. Teacher-joint probe는 fold별 하나의 reference teacher로 정의한다.

**판단 변경의 이유:** Output distillation이 latent coordinate alignment까지 보장하지 않는다. Student–teacher joint recovery는 shared brain input에 의한 유사성도 포함하므로 V/S reference보다 강한 증거로 취급하지 않는다.

### C04. 소수 참가자 추론은 미해결 상태로 명시

Participant bootstrap 또는 계층 모형이 자동으로 신뢰할 수 있는 confirmatory 판정을 제공한다고 쓰지 않는다. n=5/6에서는 참가자 일반화가 제한된다. 정확 부호 뒤집기 계산과 사용자 지적은 타당하지만, 어떤 여러 family 보정에서도 절대 불가능하다는 보편 명제로 확장하지 않는다.

**판단 변경의 이유:** 검정 종류·방향·family 구조·estimand에 따라 규칙이 달라진다. Hierarchical model과 direction gate는 calibration·승인 전까지 후보일 뿐이다.

### C05. Replication 방식 두 가지를 분리

기존 ‘새 participant adapter만 fit’은 strict-transfer protocol이다. ‘다른 참가자에서 연구 효과 재현’과 완전히 같은 질문이 아니다. Pipeline refit을 primary replication으로 하는 방안을 권고하되 사용자 승인을 기다린다.

**판단 변경의 이유:** 작은 자료에서 transfer 실패와 원래 과학적 효과의 재현 실패를 혼동하지 않기 위해서다. 현재 두 방식 중 하나가 승인됐다고 주장하지 않는다.

### C06. B-only 실패와 brain weight에 대한 한계 명확화

B-only baseline 실패는 뇌 정보가 전혀 없다는 증명이 아니다. Multimodal synergy가 가능하고 측정·representation·optimization 실패일 수도 있다. 단순 scale 증폭은 정보 생성 수단이 아니지만 최적화에 영향을 줄 가능성까지 부정하지 않는다.

**판단 변경의 이유:** ‘정보의 존재’, ‘주어진 모델의 추출 가능성’, ‘훈련 중 실제 사용’을 구분해야 한다. Multimodal pilot을 무조건 금지하는 gate는 두지 않는다.

### C07. Encoding 비교의 low-level baseline 유지

`L`, `V`, `V+S`를 중첩 모델이라고 부르기보다 `L`, `L+V`, `L+V+S`로 비교한다. V 단독은 별도 기술적 모델로 남길 수 있다.

**판단 변경의 이유:** 서로 다른 feature set의 차이와 L을 통제한 추가 기여가 혼동되지 않도록 하기 위해서다.

### C08. 원문 확인과 서버 확인 분리

2020/2025 참가자 수와 unique clip 수는 원문에서 확인했지만, 현재 derivative의 수·좌표공간·clip mapping은 미확인이다. ‘2020 MNI’라는 기존 진술은 원문만으로 확인되지 않는다. Caption 비율과 인접 반응 상관은 사용자 제공 수치로 남긴다.

### C09. 블록 평균 고정이라는 설명 정정

원본 prereg B1은 block response를 재현 baseline으로 보존하고 대체 beta 추정을 검토하도록 되어 있어 ‘단순 블록 평균이 이미 확정’이라는 설명과 다르다. 최신 전달본도 estimator를 D04 미동결로 둔다. 짧은 원본 영상은 실험 중 반복 재생되므로 clip duration과 block duration을 혼동하지 않는다. 현재 `blocks_mcap`의 생성 코드·window·정규화는 미확인이다. 상세 근거와 권고는 [07 검토](07_RESPONSE_ESTIMATION_REVIEW.md)에 있다. 이 정정으로 서버 데이터나 등록된 계획을 자동 변경하지 않는다.

### C10. Joint latent와 학습 순서, affect supervision의 해석

Joint latent는 결합 표상이고 Brain-first는 초기 학습 순서다. 둘을 반대 연구로 구분하지 않는다. 사용자는 joint 학습을 기본으로, 필요시 Brain-first → Joint를 비교하는 방향을 선택했다. 공유 brain 경로뿐 아니라 affect head까지 공유하는 보조 objective는 설명한 후보이지 자동 채택된 기본 loss가 아니다.

Training affect를 쓰는 것 자체는 cheating이 아니다. Warm-up부터 OOF 범위를 지켜야 하며, supervised latent의 affect geometry를 가공하지 않은 뇌의 자연적 geometry라고 해석할 수 없다. 현재 연구는 affect-supervised joint 모델이 무엇을 학습·사용하는지 묻는다. Affect-free emergence 연구를 별도로 의무 추가하지 않는다.

**판단 변경의 이유:** Assistant가 brain 활용 강화를 우선해 warm-up을 기본 추천했으나, 사용자가 joint representation의 학습·해석이라는 중심 목적을 재확인했다. 이에 warm-up을 선택적 비교 경로로 낮췄다. 방법의 효과가 실험으로 검증된 것은 아니다.

### C11. 결과 기반 실험 수정은 허용, 독립 검증과 구분

‘최종 결과를 보고 학습법을 바꾸거나 최종 모델을 교체하면 안 된다’는 포괄적 금지를 철회한다. 결과를 보고 새 방법을 탐색하고 최종 선택을 수정할 수 있다. 기존 run·변경 이유·선택에 사용한 평가 자료·시점을 기록하고, 선택에 사용된 test를 같은 모델의 독립 검증으로 표현하지 않는다. 과거 결과나 실제 preregistration을 덮어쓰거나 사후 선택을 사전 primary로 소급 표시하지 않는다. 새 split 명칭이나 freeze 날짜만으로 독립성이 생기지 않는다.

**판단 변경의 이유:** 사용자가 실험적 탐색과 방법 개선 자체를 금지하는 설명에 이의를 제기했다. 필요한 제한은 방법 수정 자체가 아니라 누출 방지와 선택·검증의 구분이다. 고정된 실패 gate는 추가 전략 검토의 필수 전제가 아니며 GPU 실행·비용의 별도 승인 원칙은 유지한다.

## 📌 3. 본실험 전에 결정할 항목

| ID | 결정 | 현재 상태 | 필요한 근거 |
|---|---|---|---|
| D01 | Canonical video/duplicate 정의 | 미확정 | 실제 manifest·hash |
| D02 | Run grouping과 outer/inner/OOF K | 권고 6/5, OOF 별도 | 연결 성분·계산량 |
| D03 | Reserved 72와 개발 자료 경계 | 미확정 | Presentation mapping |
| D04 | Response estimator·공간·atlas | 미동결; lagged block mean 출발점 권고 | 07 문서의 window/TR/nuisance/normalization audit·개발 QA |
| D05 | ROI rank·width·student depth | 개발 선택 | 제한된 validation |
| D06 | V/S checkpoint·layer·pooling | 미확정 | 재현성·입력 적합성 |
| D07 | 14-D codebook·VA/VAD 열 | 미확정 | 원 annotation |
| D08 | λ·η·dropout·seed·warm-up 설정 | 미확정 | Fit scope·선택 이력·비용 |
| D09 | Primary contrasts·multiplicity | 재검토 | Claim별 family |
| D10 | Interval·계층 모형·direction gate | 미확정 | Small-n calibration |
| D11 | Permutation·swap donor 규칙 | 미확정 | Exchangeability·run QC |
| D12 | Selective patch subset·null | 미확정 | 질문·QA·matched damage |
| D13 | Pipeline replication 또는 transfer | 승인 필요 | 연구 질문과 비용 |
| D14 | VS-guided student 추가 | 주장 의존적 | Brain teacher의 필요성 주장 여부 |
| D15 | Caption narrow lexicon | 미확정 | Manual audit·의미 손상 |
| D16 | 1b score·ROI aggregation·primary family | 방향 승인, 세부 동결 필요 | Common-denominator QA·capacity·small-n 계획 |
| D17 | 2d bridge·stage·calibration 경계 | 방향 승인, 구현 권고 | Bridge fidelity·공통 H·비용·controls |
| D18 | Affect-neighborhood retrieval 평가 규칙 | 보조 분석 채택 승인; 세부 미동결 | Profile coverage·내용 차이·metric/m/null |
| D19 | Visual cortex 대비 추가 ROI의 예측 증분 | 사용자 질문에 대한 검토 후보; 실행/primary 미승인 | 독립 ROI 정의·coverage·차원/capacity·reliability·split·contrast |
| D20 | Joint 기본 / Brain-first → Joint 추가 비교 | 방향 승인; warm-up 필수 아님; 실행 미보고 | 초기화 provenance·학습량·OOF·선택/검증 구분 |
| D21 | 공유 Affect Head의 joint + B-only objective | 제안; primary 채택 미확정 | 경로/head 공유·η·표현 호환·예산·학습 효과 |

해당 결정이 다른 결과를 보기 전에 실제로 동결됐는지 기록한다. 과거 test에 이미 접근했다면 새로운 freeze 날짜를 붙여 과거를 사전등록처럼 보이게 하지 않는다.

## 🎯 4. 주요 구성요소의 여섯 질문 rationale

### R01. Frozen video와 caption을 함께 사용

1. **질문:** 서로 겹치는 두 content view가 뇌 반응과 affect readout에 어떤 조건부 정보를 주는가?
2. **대안 설명:** 한 source만으로 충분하거나 modality capacity 차이일 수 있다.
3. **근거:** V-JEPA 2의 video representation과 Mind captioning의 caption-derived neural readout은 후보 선택 근거다. 우리 데이터에서의 증분 효과는 아직 미확인이다.
4. **선택 이유:** 임의 object/event branch보다 관측 source가 명확하다. 다중 backbone sweep을 피한다.
5. **반례·변경:** S 추가 효과가 불확실하면 semantic의 독립 기여를 주장하지 않는다.
6. **한계:** V/S를 인간의 순수 visual/semantic 과정으로 분리하지 못한다.

### R02. ROI-PCA와 participant map

1. **질문:** 위치 추적성과 작은 모델 크기를 유지하면서 참가자별 측정 좌표를 연결할 수 있는가?
2. **대안 설명:** 큰 voxel 수와 parameter 수가 overfitting을 만들 수 있다.
3. **근거:** 현재 n과 fMRI 차원, atlas-based grouping이라는 설계상의 제약. 실제 이득은 pilot으로 확인한다.
4. **선택 이유:** End-to-end 대형 brain encoder보다 비용과 자유도가 작다. Regularized projection을 대안으로 둔다.
5. **반례·변경:** PCA가 안정적 predictive signal을 잃으면 개발 단계에서 대체하고 이유를 기록한다.
6. **한계:** 고분산 PC가 감정 또는 개인 경험 성분이라는 뜻은 아니다.

### R03. Regularized encoding과 low-level controls

1. **질문:** L 위에 V/S가 held-out brain prediction을 추가하는가?
2. **대안 설명:** 밝기·색·단순 움직임 또는 모델 자유도만으로 설명될 수 있다.
3. **근거:** Encoding/decoding 및 structured regularization 문헌, 실제 feature dimension.
4. **선택 이유:** Source별 비교와 cross-validation이 명확하며 새로운 fancy estimator가 질문 해결에 필수는 아니다.
5. **반례·변경:** 추가 효과가 없으면 해당 content의 설명력을 제한한다.
6. **한계:** Kernel weight는 뇌의 modality 비중이나 causal share가 아니다.

### R04. Brain-query teacher와 VS control

1. **질문:** Teacher가 측정된 brain을 사용하면서 content 관계를 형성하는가?
2. **대안 설명:** Text/video만으로 target을 맞추는 shortcut.
3. **근거:** Multimodal optimization 문헌과 normative labels의 stimulus-level 공유 구조.
4. **선택 이유:** Brain pathway를 추적하기 쉽고 VS·swap으로 반증 가능하다. Architecture만의 보증은 하지 않는다.
5. **반례·변경:** BVS가 VS보다 낫지 않고 swap에도 둔감하면 brain-grounded 주장을 보류한다.
6. **한계:** 유의한 증분이나 swap 효과도 정서 고유 code 또는 neural causality가 아니다.

### R05. Output-only distillation

1. **질문:** Training-only content guidance가 brain-only learner에 어떤 변화를 남기는가?
2. **대안 설명:** 추가 loss의 일반 regularization 또는 직접 content reconstruction 목표의 자명한 효과.
3. **근거:** Distillation/privileged-information 틀. 현재 효과는 실험으로 검정한다.
4. **선택 이유:** Student inference를 B-only로 유지하고 content probe를 독립 평가로 둘 수 있다.
5. **반례·변경:** 성능만 향상되면 감독 이득으로 제한한다. Direct와 차이가 없으면 유용성을 인정하지 않는다.
6. **한계:** Teacher geometry의 전달을 보장하지 않는다. Shuffled control 하나로 모든 regularization 대안을 제거하지 못한다.

### R06. Target별 별도 학습과 loss

1. **질문:** 결론이 category profile 한 ontology 또는 VA/VAD만으로 제한되는가?
2. **대안 설명:** 34-D 선택 자체 또는 공동학습의 cross-target transfer가 효과를 만들 수 있다.
3. **근거:** Annotation 형태·codebook과 사용자 결정. BCE는 selection proportion, MSE는 연속 척도에 대응한다.
4. **선택 이유:** 서로 배척하지 않으면서 trainable cross-target 공유를 피한다. Categorical KL 정규화를 강제하지 않는다.
5. **반례·변경:** 14-D에서 재현되지 않으면 target-specific 결과로 제한한다. 열이 없으면 VAD를 제외한다.
6. **한계:** Raw decoding metric만으로 categorical 또는 dimensional emotion theory의 진위를 판정하지 않는다.

### R07. Held-out content probes와 joint reference

1. **질문:** Brain-only latent에 어떤 자극 내용이 읽히는가?
2. **대안 설명:** Probe 자체의 학습능력, stimulus memorization, teacher와의 shared brain input.
3. **근거:** Controlled probing 문헌과 모델 좌표계의 비식별성.
4. **선택 이유:** 제한된 linear/ridge probe와 V/S retrieval이 joint-space 그림만 보는 것보다 content가 명확하다.
5. **반례·변경:** Direct/adapter baseline과 차이가 없으면 새로운 내용 학습의 증거라고 부르지 않는다.
6. **한계:** 정보 접근성이지 affect head의 기능적 사용 증거는 아니다.

### R08. CKA

1. **질문:** 단계별 전체 stimulus geometry가 어떤 reference와 비슷한가?
2. **대안 설명:** 몇 개 exemplar만으로 전체 구조를 추정할 수 있다.
3. **근거:** Kornblith et al.의 representation similarity 방법.
4. **선택 이유:** Stage × reference를 작게 요약할 수 있다. Primary mechanism이 아닌 보조 분석으로 제한한다.
5. **반례·변경:** Retrieval/개입과 일치하지 않으면 geometry summary로만 보고한다.
6. **한계:** 특정 의미 관계나 feature 사용, 인간 뇌와의 동등성을 보이지 않는다.

### R09. Selective patching·ROI reliance

1. **질문:** 특정 부분 계산의 변화가 content 및 affect readout에 영향을 주는가?
2. **대안 설명:** Decodable하지만 사용하지 않는 정보, 일반적인 모델 손상, 전체 상태 복원의 자명함.
3. **근거:** Activation patching의 방법론과 계산 그래프 분석. LLM 결과를 fMRI 모델의 검증 결과로 대체하지 않는다.
4. **선택 이유:** 부분 개입과 matched null은 전체 activation 시각화보다 사용 여부에 가까운 질문을 준다.
5. **반례·변경:** Null과 차이가 없거나 OOD 손상으로 설명되면 mechanistic claim을 보류한다.
6. **한계:** Model-computational intervention이며 인간의 neural causal intervention이 아니다.

### R10. Caption masking과 brain rescue

1. **질문:** 직접 감정어 또는 안정적인 content만 이용하는 shortcut인가?
2. **대안 설명:** 상황 의미가 아니라 label word, modality optimization 차이가 효과를 만든다.
3. **근거:** 실제 caption audit 및 multimodal optimization 문헌. 사용자 수치는 아직 검증 대기다.
4. **선택 이유:** 원문 primary를 유지한 sensitivity와 제한된 dropout/동일-target auxiliary를 사용한다.
5. **반례·변경:** Masking 자체의 의미 손상이나 rescue의 과적합이면 효과를 shortcut 해소로 해석하지 않는다.
6. **한계:** Brain scalar, dropout, auxiliary loss가 뇌 정보를 새로 만들거나 실제 사용을 보장하지 않는다.

### R11. Small-n inference와 cohort replication

1. **질문:** 효과가 어느 참가자·자극 모집단까지 일반화되는가?
2. **대안 설명:** 특정 개인, 자극 순서, 작은 cluster 수, preprocessing 차이에 특이할 수 있다.
3. **근거:** 실제 participant/run 구조와 two-factor representational inference 문헌.
4. **선택 이유:** 참가자별 효과와 estimation을 중심으로 calibrated 방법을 정한다. 큰 자극 수로 n을 부풀리지 않는다.
5. **반례·변경:** Interval이 넓거나 cohort에서 재현되지 않으면 일반화 범위를 줄인다.
6. **한계:** Hierarchical model도 작은 participant n을 해소하지 못하며 공유 영상은 새 자극 일반화가 아니다.

### R12–R14. 보강 방향과 채택된 보조 분석

- R12: 1b는 content와 affect annotation이 동일 뇌 반응에서 공유/조건부로 설명하는 부분을 묻는다. Lescroart/Horikawa 선례를 근거로 기존 encoding을 재사용하며, signed contrast의 불안정 시 공유·분리 주장을 보류한다. 감정 인과 분해는 아니다.
- R13: 2d는 동일 입력 B와 f(B)의 공통성 대안을 막고 발견된 내용 관련 표현을 독립 fMRI로 검증한다. Content-side projection을 권고하되 bridge fidelity와 control이 실패하면 모델 내부 해석으로 제한한다. Zero-shot 또는 neural causality는 아니다.
- R14: Affect-neighborhood retrieval은 affect-profile 재표현 대안에 대한 채택된 보조 분석이다. Continuous-profile 기반의 기존 retrieval 재사용을 권고하며 coverage/구별력이 없으면 보류한다. 감정별 threshold 분할이나 완전한 affect 통제가 아니다.

각 rationale의 여섯 질문 전체와 문헌은 [06 보강 문서](06_NEURAL_VALIDATION_AMENDMENT.md)에 명시했다. R12/R13의 보강 방향과 R14의 보조 분석 포함은 승인되었다. D16–D18의 실행 설정 동결 및 primary 통계 승인과는 구분한다.

### R16. Joint 기본 방향과 선택적 brain 학습 보완

1. **질문:** Affect-supervised joint 모델에서 brain–visual–semantic 관계가 어떻게 학습되며, brain 경로의 학습 순서·직접 supervision이 이를 바꾸는가?
2. **대안 설명:** Content 경로의 최적화 우위, 단순한 추가 update/label exposure, 학습 목표가 유도한 geometry를 뇌 고유 구조로 오인할 수 있다.
3. **근거:** Joint 모델을 중심으로 유지하겠다는 사용자 결정, Wang et al. (2020)의 modality별 일반화 차이, Peng et al. (2022)의 학습 불균형 조절 연구, 독립 평가 원칙. 이 문헌들은 현재 fMRI warm-up·공유 head 조합의 효과를 검증하지 않는다.
4. **선택 이유:** Joint를 직접 학습하는 기존 연구 질문을 유지하고, warm-up은 같은 최종 joint 구조로 이어지는 추가 전략으로 비교한다. D21은 별도 head보다 본 readout에 brain 학습 신호를 주기 위한 후보이며, 단순 brain scale 증폭보다 objective 경로가 명시적이다. 모든 장치를 동시에 채택하지 않는다.
5. **반례·변경:** Warm-up 과적합, 추가 학습량으로 설명되는 효과, 공유 head의 표현 충돌, 보조 loss가 joint 학습을 저해하는 경우 해당 전략·해석을 수정하거나 제외한다. 효과 없음은 뇌 정보 부재의 증거가 아니다.
6. **한계:** Brain 학습 신호 부여는 full-input 사용이나 신규 정보 생성의 보증이 아니다. Affect 지도 latent를 자연적 뇌 geometry 또는 affect-free discovery라고 부르지 않는다. 선택에 노출된 평가 자료는 독립 최종 검증을 대신하지 않는다.

## 🚫 5. 현재 primary에 넣지 않을 항목

- Imagery, audio branch, generative caption output, end-to-end LLM
- 별도 object/event network를 이유 없이 병렬 추가
- SPoSE·PCM·RSA·CKA를 모두 주 분석으로 나열
- Latent alignment/reconstruction loss를 추가한 뒤 recovery를 독립 결과라고 부르기
- Single emotion threshold로 자극을 나누는 ‘감정 안의 이질성’ 분석
- 모든 target에 모든 model ablation과 patching을 자동 반복
- Foundation model 구축, 개인 감정 component의 현재 학습 주장

향후 추가는 금지가 아니라 별도 rationale와 범위 승인 문제다. 이 목록은 실험 수를 줄이기 위한 것이며 음성 결과를 숨기기 위한 제거 규칙이 아니다.

## 🔍 6. D19 검토 후보: ROI의 조건부 예측 정보

사용자 질문은 ‘visual cortex만으로 normative affect profile을 예측한 뒤 amygdala 또는 hypothalamus를 추가하면 무엇이 달라지는가?’다. 이는 검토 요청이며 이 문서에 기록했다고 primary 편입·실행·별도 논문이 승인된 것은 아니다.

### R15. 여섯 질문 rationale

1. **질문:** 시각피질 패턴으로 접근 가능한 정보에 더해 특정 비시각 영역이 held-out normative affect prediction에 조건부 정보를 제공하는가?
2. **대안 설명:** Whole-brain decoder만 있으면 성공이 시각피질 정보로 충분한지 알 수 없다. 반대로 ROI를 추가한 성능 향상은 위치 특이성이 아니라 추가 차원·측정 신뢰도·모델 자유도 효과일 수 있다.
3. **근거:** Kragel et al. (2019)은 시각피질 패턴과 emotion-related output/decoding의 관련성을 보고했다. Horikawa et al. (2020)은 여러 뇌 영역의 고차원 emotion decoding을 연구했다. 이들은 이번 amygdala/hypothalamus 증분의 존재나 새로움을 입증하지 않는다. Hypothalamus의 작은 크기·분할 어려움은 Billot et al. (2020)이 설명한다. 현 데이터의 일부 hypothalamus coverage 저하는 사용자 제공 보고이며 직접 재검증하지 않았다. 문헌은 [05 §8](05_REFERENCES.md)에 기록한다.
4. **선택 이유:** 전체 ROI 조합 탐색 대신 사전 정의한 소수의 중첩 입력 비교로 anatomical increment를 묻는다. 첫 권고는 regularized linear decoder의 B_vis 대 B_vis+B_amygdala이며, 정확한 head/loss는 target 계약을 유지한다. Hypothalamus는 데이터 적합성을 확인한 후 별도 승인한다.
5. **반례·변경:** 증분이 불안정하거나 차원·coverage·신뢰도를 고려한 대조에서 사라지면 영역 특이 해석을 낮춘다. 충분한 신호나 coverage가 없으면 null을 기능 부재로 해석하지 않는다. ROI의 유효 coverage 기준을 성능을 본 뒤 바꾸지 않는다.
6. **한계:** 예측 증분은 정서 전용 code, 감정 생성의 인과 순서, amygdala의 필수성, hypothalamic/interoceptive mechanism 또는 개인 감정 복원을 증명하지 않는다. Visual cortex로 설명되지 않은 모든 정보를 ‘emotion-specific’이라 부르지 않는다.

### 조작과 통제의 최소안 — 아직 미동결

- B_vis는 해부학적으로 독립 정의한 시각피질 fMRI이고 video feature V와 다르다. Amygdala/hypothalamus는 별도 구조이며 thalamus를 hypothalamus로 대체하지 않는다. Atlas label과 native-space 정합·유효 voxel 수를 참가자별 확인한다.
- 같은 자극/run split, 평가 행, target와 tuning budget으로 각 입력 조건을 **처음부터 따로 학습**한다. 어떤 ROI가 유효한지 test decoding으로 선택하지 않는다. 증분은 동일 참가자·자극에서 paired comparison한다.
- 입력 voxel 수·PCA rank·trainable parameter·regularization 효과를 기록한다. Train-only dimension-matched sensitivity와 사전에 정한 비교 ROI를 검토한다. 임의 white noise 추가만으로 현실의 ROI 추가를 충분히 통제했다고 하지 않는다. 신뢰도로 성능을 단순 나누지 않는다.
- 34-D/14-D는 별도 target이며 공동학습하지 않는다. ROI별 성능 순위 전체를 두 ontology의 우열로 해석하지 않는다. 정확한 score와 multiplicity는 D09/D10과 함께 정한다.
- 해부학적 증분을 먼저 보기 위해 teacher 없는 B-only 비교를 권고한다. Guided student의 증분은 별도 질문이며 모든 ROI 조건의 teacher까지 재학습하는 대규모 factorial sweep을 자동 추가하지 않는다.
- 기존 frozen-model ROI perturbation은 ‘이미 학습한 모델이 무엇에 의존하는가’를 묻는다. 입력 subset별 재학습은 ‘어떤 정보가 다른 영역에 더해 예측 가능한가’를 묻는다. 서로를 대체하지 않는다.
- 채택하면 Analysis 3의 제한된 보조 분석으로 배치하고, Analysis 2의 content retrieval/ROI reliance와 연결한다. Affect 증분만으로 ‘내용을 넘어선 감정’을 결론 내리지 않는다. 새 Analysis 4나 별도 논문으로 자동 확대하지 않는다.

본실험 전 결정: 시각피질 범위, 독립 ROI 정의, coverage gate, 참가자 포함 규칙, 차원/capacity sensitivity, target·metric·contrasts·추론 단위·보정·계산 예산. 현재는 데이터 적합성 및 과학적 가치 검토 단계다.
