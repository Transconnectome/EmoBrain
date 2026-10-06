# EmoBrain 상세 실행 목록

_2026-10-06 · 서버 현황 확인에서 최종 원고·재현 패키지까지 · 체크박스는 실제 증거를 확인한 뒤 갱신_

---

## 📍 1. 실행 순서와 완료의 의미

각 항목은 목적, 수행 내용, 산출물, 수용 기준, 실패 시 조치를 포함한다. 미체크는 미실행의 확정이 아니라 이번 인수인계에서 확인되지 않았다는 뜻이다. 기존 작업이 기준을 만족하면 재사용하고 근거를 연결한다.

진행 단계는 `서버 현황 → 데이터·누출 QA → 개발 pilot → 설계 동결 → 본실험 → 해석·재현 → 원고`다. Primary 효과의 양성 여부는 작업 완료와 다르다. 음성 결과도 계획대로 검증하고 보고하면 분석은 완료다.

각 task 기록은 다음 필드를 갖는다.

```text
task_id, status, evidence_path, code_version, config_hash,
input_scope, output_paths, acceptance_tests,
deviation_from_plan, next_dependency, decision_needed
```

`status`는 `not_audited / reusable / needs_repair / ready / running / done / blocked` 중 하나다. 결과를 보기 전에 필요한 승인과 단순 구현 선택을 구분한다. 승인 대기 중에도 synthetic test와 read-only audit은 진행할 수 있다.

## 🔍 2. Phase 0 — 현황과 데이터 감사

### P00. 기존 서버 작업 인수

- [ ] 프로젝트 코드, 환경, 데이터, cache, checkpoint, result directory를 찾는다.
- **목적:** 이미 한 작업을 버리거나 누출된 결과를 무심코 재사용하는 것을 막는다.
- **수행:** Git 상태와 변경 파일, 실행 중인 job, 문서 버전, 재현 가능한 실행 명령을 조사한다. 원자료나 기존 결과를 삭제하지 않는다.
- **산출물:** `server_status.md`, `artifact_inventory.tsv`, `environment.lock` 또는 실제 환경 export.
- **수용:** 모든 ‘완료’ 주장이 코드·config·로그·output으로 뒷받침되고, 확인 못한 것은 별도 표시된다.
- **실패 시:** 경로·권한·데이터 부재를 보고하되 존재 여부를 추측하지 않는다. 결과가 있으면 training IDs와 test 노출 여부부터 조사한다.

### P01. Canonical stimulus와 cohort 매핑

- [ ] 두 cohort의 raw ID, unique video, duplicate, caption, affect annotation을 하나의 canonical table로 연결한다.
- **목적:** 2,180/2,181 차이와 중복으로 생길 train/test 누출을 막는다.
- **수행:** File hash, metadata 및 필요 시 perceptual duplicate 점검을 병행한다. 같은 내용의 재인코딩은 byte hash만으로 못 잡을 수 있음을 고려한다. 불확실한 duplicate는 사람이 검토할 목록으로 만든다.
- **산출물:** `stimulus_manifest`, `duplicate_report.md`, `cohort_overlap.tsv`.
- **수용:** 각 유효 fMRI observation이 정확히 하나의 canonical stimulus와 target에 연결되고 unmatched 항목 및 제외 사유가 모두 기록된다.
- **실패 시:** 행 순서를 가정해 강제 결합하지 않는다. 해당 자극을 보류하고 전체 손실 수를 보고한다.

### P02. Presentation·repeat·run audit

- [ ] 참가자별 presentation order, onset, run, repeat를 복원한다.
- **목적:** 동일 순서, 시간 의존, 반복 test 재사용이라는 대안 설명을 통제한다.
- **수행:** 모든 참가자 간 순서 일치 여부와 이탈 run을 실제로 비교한다. 2025 test 72개가 training session 어디에 있었는지 표시한다. 2020의 block 내 재생 반복과 독립 repeat를 구분한다.
- **산출물:** `observation_manifest`, `presentation_audit.md`, `reserved_test_ids.tsv`.
- **수용:** 각 repeat의 위치와 학습 제외 여부가 명시되고 trial 개수와 unique stimulus 수가 분리되어 보고된다.
- **실패 시:** Timing 없이는 새 beta estimator를 강행하지 않고 기존 derivative의 한계를 기록한다.

### P03. Target와 caption 감사

- [ ] 34-D/14-D raw table, scale, missingness, rater count, VA/VAD mapping을 확인한다.
- **목적:** Loss와 target ontology를 데이터 생성 방식에 맞춘다.
- **수행:** 분포·base rate·constant dimension·동일/중복 열을 점검한다. Caption affect-word count를 frozen candidate lexicon별로 재계산하고 소규모 manual audit을 한다.
- **산출물:** `target_codebook.md`, `target_qc.tsv`, `caption_audit.md`, `lexicon_candidates.json`.
- **수용:** 모든 target 열이 원천으로 추적되며 사용자 제공 7.1%/46%/10%와 실제 재계산 값이 분리된다. Missing은 zero로 바꾸지 않는다.
- **실패 시:** Dominance 열이 없으면 VAD-3를 중단하고 대체 target을 임의 생성하지 않는다.

### P04. fMRI 공간·품질 audit

- [ ] NIfTI header, native/MNI, template, voxel size, affine, preprocessing version, motion, run별 QC를 확인한다.
- **목적:** Cohort 차이가 preprocessing mismatch로 설명될 가능성을 확인한다.
- **수행:** 원문 기술과 서버 derivative를 대조한다. Atlas transform을 실제 image overlay로 검사한다. fMRI 정보를 activation screenshot RGB로 대체하지 않는다.
- **산출물:** `fmri_audit.md`, `spatial_provenance.tsv`, `roi_registration_qc/`.
- **수용:** 좌표 변환 방향·보간·atlas version이 명시되고 ROI coverage가 확인된다.
- **실패 시:** MNI로 무조건 맞추기보다 native ROI mapping 또는 정당화된 변환안을 제시한다. 방법 변경은 기록한다.

### P04b. Response window·정규화 audit

- [ ] [07 전처리 검토](07_RESPONSE_ESTIMATION_REVIEW.md)의 timing·보존·scope 항목을 확인한다.
- **목적:** 단순 평균, 지연 보정 평균, trial beta를 구분하고 서로 다른 길이·이웃 자극·정규화의 혼동을 막는다.
- **수행:** blocks_mcap 생성 코드와 window, TR, rest, dummy scan, censor, nuisance, runz 적용 순서·범위를 추적한다. 원본 clip/block/BOLD window 길이를 별도 계산한다. Continuous run과 events/confounds를 보존한다.
- **산출물:** response_estimator_audit.md, response_window_manifest.tsv, normalization_provenance.tsv, timing_qc, D04 권고.
- **수용:** 기존 derivative를 재현하며 분석용 estimator가 최종 test를 보고 선택되지 않는다. 시계열·GLMsingle·Brain-JEPA를 자동 추가하지 않는다.
- **실패 시:** Primary 입력 확정을 보류하고 개발 자료에서만 제한된 추정법 대안을 검토한다. 평균 완료를 전체 전처리 완료로 쓰지 않는다.

## 🔐 3. Phase 1 — Split·누출·기초 pipeline

### P05. Run-grouped split feasibility

- [ ] 중복 stimulus로 연결된 run graph를 만들고 후보 split의 표본 수와 연결 성분을 비교한다.
- **목적:** 자극 identity와 시간 구조를 함께 보호한다.
- **수행:** Outer 6/inner 5 권고안과 계산 가능한 대안을 비교한다. Label 성능으로 좋은 split을 고르지 않는다. 같은 자극의 모든 참가자 관측을 같은 fold에 둔다.
- **산출물:** `split_candidates.md`, `split_manifest_candidate`, fold별 run/stimulus 표.
- **수용:** 중복·repeat·참가자 간 leakage가 0이고 fold size와 temporal boundary 규칙이 설명된다.
- **실패 시:** 연결 성분 때문에 K가 불가능하면 근거를 제출하고 K 또는 duplicate 처리 규칙을 승인받는다.

### P06. 누출 방지 테스트 구현

- [ ] Outer/inner/teacher OOF 경계와 transform scope를 자동 검사한다.
- **목적:** 가장 위험한 간접 teacher-label 누출을 학습 전에 차단한다.
- **수행:** Synthetic IDs로 잘못된 cache가 반드시 실패하도록 negative test를 만든다. Continuous OOF target의 scaler round-trip도 검사한다.
- **산출물:** 자동 test suite, `leakage_test_report.md`, cache provenance schema.
- **수용:** 정상 사례는 통과하고 의도적으로 주입한 중복·outer test·inner validation 누출은 각각 실패한다.
- **실패 시:** 학습보다 cache 계약을 먼저 고친다. 누출된 기존 결과는 삭제하지 않고 invalidated로 표시한다.

### P07. Response·ROI token pipeline

- [ ] 승인된 response estimator와 ROI preprocessing을 재현한다.
- **목적:** 작은 표본에서 안정적인 brain token과 해부학적 추적성을 확보한다.
- **수행:** Train-only standardization/PCA, participant map, missing-ROI mask를 구현한다. Rank는 training sample 수와 voxel 수를 넘지 않는다. 다른 scope의 PCA를 재사용하지 않는다.
- **산출물:** `brain_cache`, `transform_manifest`, `roi_token_qc.md`.
- **수용:** Shape·finite·variance 검사가 통과하고 임의 test observation을 변경해도 fitted training transform이 바뀌지 않는다.
- **실패 시:** No-PCA regularized projection 등 제한된 대안을 개발 범위에서 비교하고 선택 이유를 남긴다.

### P08. Frozen content cache

- [ ] L/V/S를 추출하고 checkpoint·sampling·aggregation을 기록한다.
- **목적:** 모든 비교가 같은 자극과 같은 feature 좌표를 사용하게 한다.
- **수행:** Encoders는 eval/frozen 상태를 확인한다. V-JEPA 2 frame/time coverage, captions 수, masking pipeline을 검사한다. Sample video의 시각적 내용과 frame indexing을 수작업 확인한다.
- **산출물:** `lowlevel_cache`, `video_cache`, `caption_cache`, `feature_manifest`.
- **수용:** 모든 usable canonical ID에 feature가 있고 hash·dimension이 재현된다. Affect labels가 feature 추출/선택에 입력되지 않는다.
- **실패 시:** Missing feature 원인을 보고하고 조용히 zero-filled modality로 학습하지 않는다.

## 🧪 4. Phase 2 — 작은 pilot과 사전 동결

### P09. Brain-only·mean baseline pilot

- [ ] 개발 fold 안에서 mean-profile, regularized linear B-only, 작은 Direct student를 비교한다.
- **목적:** 데이터 연결·target·scale·학습이 실제로 작동하는지 확인한다.
- **수행:** Train/validation gap, per-subject metric, class base rate, seed variation을 조사한다. 단일 성능 수치만 보지 않는다.
- **산출물:** `baseline_pilot.md`, held-out development predictions, runtime/memory estimate.
- **수용:** 누출 검사와 수치적 QA를 통과하고 train/validation 개선 또는 실패 원인이 설명된다. 양성 성능 자체는 QA 통과 조건이 아니다.
- **실패 시:** Alignment, response SNR, scaling, target reliability를 점검한다. ‘뇌 정보 없음’ 결론을 내리거나 임의 brain weight를 키우지 않는다.

### P10. Encoding pilot

- [ ] 소수의 사전 정한 ROI로 L, L+V, L+V+S pipeline을 시험한다.
- **목적:** 본실험 전에 다중 kernel 적합·집계·시간 비용을 검증한다.
- **수행:** Train-only reduction과 inner hyperparameter search, native/PC score 집계 규칙을 비교 가능하게 구현한다.
- **산출물:** `encoding_pilot.md`, resource estimate, test suite.
- **수용:** 행 정렬·kernel centering·prediction shape가 맞고 negative control에서 비정상적 완벽 예측이 발생하지 않는다.
- **실패 시:** 코드나 data leakage를 조사한다. Pilot ROI의 유리한 결과로 최종 ROI 범위를 선택하지 않는다.

### P11. 최소 teacher/student pilot

- [ ] 개발 자료에서 B, VS, BVS와 작은 student의 학습을 확인한다.
- **목적:** Full ladder 전에 brain shortcut 위험과 비용을 확인한다.
- **수행:** BVS−VS, brain-swap, 학습 안정성, modality norm·gradient QA를 조사한다. Attention/gradient plot을 과학적 explanation으로 사용하지 않는다.
- **산출물:** `teacher_pilot.md`, architecture comparison, nested OOF runtime estimate.
- **수용:** Brain-only inference가 V/S 파일에 접근하지 않아도 작동하고 OOF provenance test가 통과한다.
- **후속 탐색:** Brain pathway 학습·optimization·측정 신호 문제를 구분하고 Brain-first → Joint 등 이유 있는 추가 전략을 비교할 수 있다. 정해진 실패 gate를 통과해야만 탐색할 수 있는 것은 아니다. 실행 자원 승인 범위는 유지한다.

### P11b. 학습 전략 비교와 provenance — 필요에 따라 수행

- **목적:** Joint latent 학습을 유지하면서 brain 경로의 학습 순서·supervision이 미치는 영향을 구분한다. 새 Analysis 4나 두 연구의 의무 실행을 뜻하지 않는다.
- [ ] 기본 joint run의 설정·checkpoint·결과를 보존한다.
- [ ] 필요하면 Brain-first → Joint를 비교한다. Warm-up brain 경로·affect head의 가중치가 실제 joint 초기화에 연결됐는지 확인한다.
- [ ] 공유 Affect Head의 `L_joint + η L_brain`은 D21 제안으로 구분하고 채택 여부를 명시한다. 채택 시 동일 경로/head 공유, 두 loss의 gradient 도달, 34-D/연속 target의 출력·loss 계약을 검사한다. Warm-up과 동시에 바꾸면 효과를 학습 순서 하나로 귀속하지 않는다.
- [ ] Recipient와 inner validation/outer test가 warm-up부터 제외되는 자동 QA를 추가한다. 더 넓은 프로젝트 label scope의 checkpoint 재사용은 엄격한 OOF에서 거부한다.
- [ ] 총 update·label exposure·seed·tuning budget과 필요한 계산량 matched joint 대조를 기록한다.
- [ ] Run별 변경 이유·parent run·관찰한 평가 자료·선택 metric·시점·최종 선택 여부를 기존 실험 기록에 저장한다. 결과 기반 추가 실험을 금지하지 않는다.
- [ ] 모델 선택에 이용한 test 결과와 독립 validation 결과를 구분한다. 후자가 없으면 없다고 보고하고 freeze 날짜를 소급하지 않는다.
- **산출물:** 기존 `teacher_pilot.md`의 전략 비교 절, 실험 output 영역의 run manifest/OOF provenance/QA 결과. 새 루트 보고서나 중복 handoff를 만들지 않는다.
- **완료 기준:** 전략별 재현 가능한 학습 범위·초기화·loss 기록과 누출 QA. 성능 향상을 완료 조건으로 강제하지 않는다. 문서 갱신은 학습 실행 완료가 아니다.

### P12. Inferential plan과 freeze

- [ ] 작은 참가자 수, primary contrasts, family, metric, interval, permutation, direction reporting을 확정한다.
- **목적:** 결과에 맞춘 유의성 판정을 방지한다.
- **수행:** 계층 모형 후보는 추정 대상·prior·수렴·null simulation·coverage를 검토한다. 집계 metric과 stimulus-wise metric에 같은 likelihood를 기계적으로 적용하지 않는다. 방향 일치 수는 효과와 함께 보고하되 자동 p<.05 판정으로 쓰지 않는다.
- **산출물:** `inference_plan.md`, `simulation_validation.md`, `freeze_manifest.json`, 변경 이력.
- **수용:** [결정 기록](04_DECISION_REGISTER.md)의 본실험 필수 미확정 항목이 resolved이고 사용자/연구책임자의 승인 기록이 있다. D16/D17은 새 핵심 보강의 실행 전 조건이며 D18은 채택된 보조 분석의 거리·후보 수·null 등 평가 규칙이다. 새로운 family와 기존 family를 함께 검토한다.
- **실패 시:** 분석을 estimation-focused/exploratory로 제한할지 결정한다. 더 많은 seed나 stimulus로 participant n 부족을 숨기지 않는다.

## 🧠 5. Phase 3 — 세 분석의 본실험

### P13. Analysis 1 전체 실행

- [ ] 승인된 모든 참가자·ROI에서 nested encoding을 실행한다.
- **목적:** 모델 학습 이전에 실제 뇌–내용 대응을 검정한다.
- **수행:** 기존 1a의 두 핵심 contrast, per-participant 효과, ROI별 prediction과 보조 effect를 저장한다. Primary/secondary 지위는 P13b까지 포함한 D09/D16 freeze를 따른다. Permutation은 사전 지정한 scope에 맞춰 필요한 재적합까지 수행한다.
- **산출물:** `analysis1_predictions`, `analysis1_effects`, figure source table, Methods 기록.
- **수용:** 모든 예상 fold/subject가 있거나 제외 사유가 있고 통계 단위와 CI 범위가 명확하다.
- **실패 시:** 음성 결과를 보고하고 content correspondence의 강한 주장을 줄인다. Target과 ROI를 사후 골라 양성으로 바꾸지 않는다.

### P13b. Analysis 1b 내용–정서 설명력

- [ ] 34-D/14-D 각각 G, G+C, G+E, G+C+E의 held-out encoding을 실행한다.
- **목적:** 일반적인 content encoding과 affect-associated brain response 사이의 공유·조건부 예측 성분을 직접 확인한다.
- **수행:** P10에서 synthetic/개발 pilot 후 공통 SSE score·분모·평가 행을 고정한다. 기존 1a 대비까지 포함한 D09/D16의 family를 P12에서 승인받는다.
- **산출물:** `analysis1b_model_manifest`, `analysis1b_oos_predictions`, `analysis1b_signed_contrasts`, participant별 uncertainty와 figure source.
- **수용:** 입력 E가 실제 annotation이며 네 모델의 target 행·ROI·분모가 같고 음수 성분이 보존된다. 독립 tuning과 전처리 scope가 추적 가능하다.
- **실패 시:** Shared 불안정·비유의를 완전 분리/환원으로 해석하지 않는다. Model mismatch·noise·power를 분리해 보고한다. 결과의 양성 여부가 완료 기준은 아니다.

### P14. 34-D teacher ladder와 OOF outputs

- [ ] B/BV/BS/BVS/VS/shuffled teacher를 matched 조건으로 fit한다.
- **목적:** 각 content source와 brain의 조건부 기여를 평가한다.
- **수행:** Outer test용 teacher와 student guidance용 cross-fit teacher를 분리한다. Teacher OOF recipient의 모든 참가자·repeat를 제외한다. 모든 caption/masking 설정을 기록한다.
- **산출물:** `teacher_checkpoints`, `teacher_oof_outputs`, `teacher_contrasts`, cache manifests.
- **수용:** OOF 누출 0, target/condition/fold별 cache namespace 분리, capacity·tuning budget 보고가 완전하다.
- **실패 시:** Teacher가 VS와 구별되지 않아도 결과를 보존한다. Brain-grounded 주장은 보류하고 조건부 이득과 frozen reliance를 따로 보고한다.

### P15. Teacher brain/content mismatch

- [ ] Held-out clean, brain-swap, video-swap, caption-swap을 생성한다.
- **목적:** 정렬 관계가 학습된 computation에 영향을 주는지 평가한다.
- **수행:** Donor 규칙·seed·run restrictions·duplicate exclusion을 저장한다. Loss와 content readout을 같이 기록한다. 일반 손상 또는 OOD 설명을 위한 matched control을 적용한다.
- **산출물:** `mismatch_manifest`, paired trial-level metrics, layer outputs.
- **수용:** Donor가 같은 canonical stimulus가 아니며 intervention 방향과 metric 부호가 명확하다.
- **실패 시:** Swap 손상만으로 의미적 통합을 주장하지 않는다. In-distribution ablation 및 VS 비교와 함께 한계를 쓴다.

### P16. 세 student 학습

- [ ] Direct, Full-guided, Shuffled-guided를 같은 brain input과 비교 가능한 budget으로 학습한다.
- **목적:** Aligned teacher supervision의 이득을 label-only와 잘못된 guidance와 비교한다.
- **수행:** Target별 λ 선택 규칙을 적용하고 전체 hyperparameter 탐색 횟수를 기록한다. Test 시 teacher/content 접근을 차단하는 integration test를 수행한다.
- **산출물:** `student_checkpoints`, `student_predictions`, `training_logs`, provenance.
- **수용:** Test-time brain-only가 입증되고 모든 조건에 동일 평가 자극이 사용된다.
- **실패 시:** Full이 좋아지지 않아도 직접 baseline을 삭제하지 않는다. Distillation 효과가 없거나 불확실하다고 보고한다.

### P17. Student stage export와 content probes

- [ ] Adapter부터 final latent까지 frozen representation을 추출한다.
- **목적:** 단지 맞춘 정답이 아니라 무엇을 읽을 수 있는지 조사한다.
- **수행:** 동일 linear/ridge probe로 V/S retrieval을 학습·평가한다. Candidate ID를 deduplicate한다. Teacher-joint는 fold별 단일 reference를 사용하는 보조 분석으로 둔다.
- **산출물:** `latent_manifest`, `probe_checkpoints`, `retrieval_scores`, held-out neighbor tables.
- **수용:** Probe test 누출 0, 모든 조건의 candidate set 동일, raw/adapter baseline 포함, projection/latent coordinate scope 명시.
- **실패 시:** Affect만 개선되고 content가 안 읽히면 regularization/privileged supervision 해석으로 제한한다.

### P17b. Affect-neighborhood content retrieval — 채택된 보조 분석

- [ ] 실제 전체 profile 이웃에서 유효 후보 수·거리·content 차이·coverage를 조사한다.
- **목적:** 정서 프로필이 가까운 후보들 사이에서도 내용 구별이 가능한지 검사하고, retrieval이 단순 affect-profile 재표현이라는 대안 설명을 점검한다.
- **수행:** 개발 자료에서 candidate 거리/m/scaling/tie/coverage와 null 규칙을 D18에 동결한다. 기존 frozen probe와 동일 후보로 Direct/Full/Shuffled, raw/adapter 및 affect-output-only control을 평가한다. 전체 후보 retrieval도 유지한다. 단일 감정 threshold를 쓰지 않는다.
- **산출물:** `affect_neighborhood_feasibility`, `candidate_manifest`, `affect_neighborhood_retrieval_scores`, output-only 대비, 참가자별 결과와 불확실성; 불가능하면 이유와 coverage를 보고한다.
- **수용:** Test E는 평가 후보 생성에만 사용하며 학습과 분리되고 모든 모델에 같은 후보가 적용된다. Pair reuse를 독립 표본으로 세지 않는다.
- **실패 시:** 불충분한 coverage·내용 차이이면 보류한다. 실패가 내용 정보 부재를 입증한다고 쓰지 않는다.

### P18. CKA와 exemplar montage

- [ ] Stage × V/S/affect/reference-joint CKA와 대표 retrieval 예시를 만든다.
- **목적:** 정량 결과를 직관적으로 보여주되 시각적 인상으로 결론을 대체하지 않는다.
- **수행:** Fold·참가자별 CKA를 저장한다. 예시는 사전 seed로 뽑은 사례, median 사례, failure 사례를 포함한다. 조건 차이가 큰 것만 골라 전체를 대표하게 하지 않는다.
- **산출물:** `cka_tables`, `exemplar_selection_manifest`, 실제 영상·caption·prediction이 연결된 montage.
- **수용:** 각 예시의 held-out 여부와 선택 규칙을 추적할 수 있다. 이미지 사용·배포 권한도 점검한다.
- **실패 시:** 2-D cluster나 CKA만으로 ‘joint space 회복’을 주장하지 않는다.

### P19. Selective patching과 ROI reliance

- [ ] 동결한 ROI/token subset의 perturbation 및 부분 복원을 수행한다.
- **목적:** 읽을 수 있는 정보와 실제 affect computation의 의존성을 연결한다.
- **수행:** Descendant 재계산, sham, wrong-donor, equal-size token null을 구현한다. Teacher와 student에서 어느 경로에 개입했는지 분리한다. Whole-state restoration은 QA로만 기록한다.
- **산출물:** `intervention_manifest`, raw paired differences, null distributions, reliability gate/해석 상태.
- **수용:** 지정한 tensor subset 외 upstream state가 섞이지 않고 downstream은 재계산된다. Clean model의 예측·retrieval 수준과 uncertainty가 함께 보고된다.
- **실패 시:** Model damage와 content-specific dependence를 구분할 수 없으면 mechanistic conclusion을 보류한다. Null보다 크다는 이유만으로 인간 뇌 causal claim을 하지 않는다.

### P19b. Analysis 2d 독립 뇌 검증

- [ ] 모델에서 선택한 content-related representation을 평가 뇌 입력 없이 독립 fMRI와 연결한다.
- **목적:** 모델 입력의 재기술과 실제 독립 뇌 대응을 구분한다.
- **수행:** P11 개발 단계에서 content-side bridge fidelity와 비용을 확인한다. Discovery T에서만 stage/rank/bridge를 선택한다. 공통 H를 모든 fit에서 제외한다. R,T에서 neural readout만 calibration하고 H에서 평가한다. Original-content/Direct-derived controls를 함께 둔다.
- **산출물:** `analysis2d_scope_manifest`, `analysis2d_bridge_fidelity`, `analysis2d_neural_validation`, calibration 명세.
- **수용:** D17과 family가 동결되고 평가 predictor에 B_H/E_H가 없으며 어떤 모델이 어느 참가자·자극을 봤는지 확인된다. Projection을 실제 latent와 구분한다.
- **실패 시:** Bridge 불충분·독립 뇌 효과 미재현을 보고하고 neuroscience 주장을 줄인다. Ordinary content encoding을 2d 성공으로 대신 보고하지 않는다.

## 📊 6. Phase 4 — Target 확장·robustness·replication

### P20. Analysis 3의 34-D readout

- [ ] Mean-profile, linear, Direct, Full, Shuffled의 held-out profile prediction을 평가한다.
- **목적:** Brain–content 분석을 고차원 affective annotation과 연결한다.
- **수행:** Within-profile correlation뿐 아니라 Brier/MSE, RMSE, category별 예측, base-rate 보정 지표를 보고한다. Constant profile 규칙을 적용한다.
- **산출물:** `affect34_results`, `geometry_content_function_summary`, participant effect plot.
- **수용:** 학습 loss와 평가 correlation이 혼동되지 않고 normative target임이 모든 figure에 표시된다.
- **실패 시:** Readout 실패가 앞선 encoding 결과까지 없애지는 않는다. 어떤 분석 단계까지 근거가 있는지 분리해 쓴다.

### P21. 14-D 및 VA/VAD 독립 실행

- [ ] Codebook이 허용하는 target별로 별도 teacher/student run을 수행한다.
- **목적:** 결과가 category-based annotation 한 종류에만 의존하는지 조사한다.
- **수행:** Trainable parameter·optimizer·OOF·target scaler를 분리한다. Frozen features와 split만 공유한다. Full mechanistic ladder는 자동 확장하지 않는다.
- **산출물:** `affect14_results`, `va2_results`, `vad3_results` 또는 VAD 보류 사유.
- **수용:** 모든 독립성 검사를 통과하고 dimension별 original-scale metric이 있다.
- **실패 시:** Target 간 metric 차이를 categorical/dimensional theory의 승패로 해석하지 않는다. Noise/reliability/차원 수 차이를 먼저 다룬다.

### P22. 제한된 robustness

- [ ] Narrow affect-word masking, affect-word-only baseline, 필요한 brain rescue를 실행한다.
- **목적:** Primary 결론에 남은 구체적 대안 설명만 점검한다.
- **수행:** 사전 정의한 항목부터 실행한다. AlexNet, depth, 대형 brain encoder, 다양한 loss는 독립적인 rationale이 없으면 추가하지 않는다.
- **산출물:** `robustness_registry`, sensitivity effect table, deviations.
- **수용:** 어떤 대안 설명을 다뤘는지와 추가 계산량이 명시된다. Primary와 robustness 결과를 섞지 않는다.
- **실패 시:** Masking 손실을 전부 shortcut 증거로, dropout 회복을 brain 정보 생성으로 해석하지 않는다.

### P23. 다른 cohort에서 재현

- [ ] 승인된 pipeline-refit 또는 strict-transfer protocol을 실행한다.
- **목적:** 동일/중첩 자극에서 다른 참가자 집단의 재현성을 평가한다.
- **수행:** Primary 결과에 맞춰 cohort-specific 규칙을 추가하지 않는다. 불가피한 preprocessing 차이는 기술한다. 공통 stimulus mapping과 test 제외 규칙을 유지한다.
- **산출물:** `replication_manifest`, `replication_results`, cohort comparison figure.
- **수용:** 새로 fit한 것과 고정한 것이 구분되고 participant independence와 shared-stimulus 한계가 표기된다.
- **실패 시:** 원인을 탐색할 수 있으나 그 탐색을 confirmatory replication으로 바꾸지 않는다.

### P24. 통계와 claim audit

- [ ] Freeze된 inference rule을 모든 계획 대비에 적용한다.
- **목적:** 여러 양성 조각을 이어 과도한 전체 주장을 만들지 않는다.
- **수행:** 참가자별 효과·interval·direction·multiple testing·seed stability를 함께 제시한다. 빠진 실험과 음성 결과를 포함한다. Reuse된 label/stimulus의 dependence를 명시한다.
- **산출물:** `claim_evidence_table.md`, `confirmatory_exploratory_register`, 완전한 effect table.
- **수용:** 각 conclusion이 해당 metric/control/불확실성으로 추적된다. ‘비유의 = 같음’ 표현이 없다.
- **실패 시:** 주장을 데이터 범위까지 축소하고 변경 이유를 기록한다.

## ✍️ 7. Phase 5 — 그림·논문·재현 패키지

### P25. 최종 figure와 table

- [ ] Figure 1: 세 분석의 study overview, Figure 2: training/inference/post-training architecture.
- [ ] Figure 3: 1a content encoding과 1b content–affect 공유/조건부 signed contrast 및 개인별 효과.
- [ ] Figure 4: teacher shortcut, student content retrieval, 선택적 개입 및 2d 독립 뇌 검증의 증거 연결. 필요한 경우 세부 패널은 supplement로 분리한다.
- [ ] Figure 5: 34-D와 독립 dimensional readout 및 cohort replication.
- **목적:** 모델 박스를 늘어놓기보다 질문–대조–결과의 관계를 보여준다.
- **수행:** 이전에 선호한 직관적 도안을 보존하며 실제 구현에 맞춰 수정한다. 색은 절제하고 input, loss, test-time exclusion, evaluation-only probe를 명시한다. 미구현 module을 완성된 것처럼 그리지 않는다.
- **산출물:** 편집 가능한 figure 원본, 고해상도 export, caption, source data.
- **수용:** 그림 화살표가 실제 데이터 흐름과 일치하고 no-overlap, cropping, 글자 가독성 검사가 끝난다. ‘Independent targets’는 training 쪽 작은 표기로 유지할 수 있다.

### P26. 논문형 원고 완성

- [ ] Introduction → 세 분석 Methods → 실제 Results → 제한된 Discussion 순서로 쓴다.
- **목적:** Performance paper가 아닌 neuroscience 논리를 유지한다.
- **수행:** `paper_v15.md`의 결과 placeholder를 검증된 값으로만 채운다. Whole-state restoration, OOF, inference 정정을 반영한다. 모든 모델 선택에 여섯 질문 rationale를 붙인다. 실제 등록 여부에 따라 preregistered라는 표현을 사용한다.
- **산출물:** manuscript, supplement, figure captions, references, deviations table.
- **수용:** 숫자가 source table로 역추적되고 normative/subjective, model/brain causality가 구분된다. 감정=감각+의미라는 과잉 환원 문장이 없다.
- **실패 시:** 결과가 부분적이면 그 범위의 논문으로 재구성한다. 미래 foundation model은 Discussion 가능성으로만 둔다.

### P27. 재현과 인계 완료

- [ ] Clean environment 또는 별도 재현 경로에서 작은 end-to-end smoke test를 실행한다.
- **목적:** 논문 결과를 만든 입력과 코드를 다시 연결할 수 있게 한다.
- **수행:** Config·version·dependency·seed·hash·license·data access 설명을 정리한다. 원본 데이터 공개가 허용되지 않으면 metadata와 재현 명령만 제공한다.
- **산출물:** release candidate, reproducibility README, manifest checksums, final handoff report.
- **수용:** 대표 fold의 예측/metric이 허용 오차 내 재현되고 누출 테스트가 통과한다. 삭제·덮어쓰기 없이 이전 상태가 보존된다.
- **완료 보고:** 무엇이 재현됐는지, 못 한 것은 무엇인지, 최종 주장과 남은 한계를 명시한다.

## 📌 8. 지금 당장 할 최소 묶음

서버 AI의 첫 실행 범위는 P00–P08의 audit·QA다. 2026-10-06 보강으로 기존 결과 노출 이력, 1b의 공통 score, 2d의 cohort/stimulus 경계도 함께 감사한다. 데이터가 이미 정리되어 있으면 증거로 확인한 뒤 중복 작업을 건너뛴다. 다음으로 P09–P11의 제한된 개발 pilot을 제안하고, P12의 미확정 결정을 정리한다. P10/P11 개발 pilot에는 P13b/P19b의 작은 feasibility를 포함할 수 있다. P13 이후 본실험은 승인된 freeze가 있어야 한다. P17b는 채택된 보조 분석이다. 평가 규칙 동결과 coverage 확인 후 수행한다. P00–P08에는 07 문서의 block window·HRF·run normalization audit를 포함한다.

처음부터 full ladder × 모든 target × 모든 seed × 모든 cohort를 한꺼번에 돌리지 않는다. 첫 보고서의 핵심은 ‘무엇을 확인했고, 무엇을 재사용할 수 있으며, 다음에 어떤 판단이 필요한가’다.
