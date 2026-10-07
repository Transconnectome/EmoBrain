---
title: "EmoBrain: End-to-end Action Items"
subtitle: "지금부터 논문 제출·재현성 패키지까지 — 목적, 절차, 산출물, 판정 기준을 포함한 상세 실행계획 v1"
date: "2026-09-23"
---

# 문서 목적과 사용법

이 문서는 아이디어 목록이 아니라 실제 연구 실행의 단일 기준 문서다. 각 항목은 무엇을 할지뿐 아니라 왜 필요한지, 어떤 대안 설명을 제거하는지, 어떤 입력과 절차가 필요한지, 무엇을 산출물로 남길지, 어떤 결과에서 다음 단계로 진행하거나 주장을 낮출지를 기록한다. 완료 표시는 산출물 파일과 검증 로그가 존재할 때만 한다.

상태 표시는 다음과 같이 사용한다.

- [ ] 미시작: 입력, 코드 또는 결정이 아직 준비되지 않음
- [ ] 진행 중: 담당자, 시작일, 현재 blocker를 항목 아래 기록
- [ ] 검증 대기: 계산은 끝났으나 독립 QA 또는 재실행이 남음
- [ ] 완료: 산출물, hash, config와 검증 로그가 모두 존재
- [ ] 중단 또는 격하: 중단 이유와 논문에서의 새 지위를 기록

모든 결정 기록에는 `결정`, `과학적 이유`, `대안`, `근거`, `동결 시각`, `변경 이력`, `결과를 보기 전/후 여부`를 남긴다. 결과를 본 뒤 바꾼 결정은 confirmatory로 되돌리지 않고 exploratory 변경으로 표시한다.

# 연구의 고정 중심축

## Thesis

정서를 유발하는 자연 장면에 대한 공유된 stimulus-locked brain response는 장면의 spatiotemporal visual 및 situation-semantic content와 체계적인 관계 구조를 보이며, brain-grounded model은 이 관계를 학습하고 brain-only representation에 보존하며 high-dimensional normative affect readout에 기능적으로 사용할 수 있다.

## 모델의 목적

모델의 일차 목적은 최고 decoding 성능이 아니다. 모델은 brain–visual–semantic 관계가 형성되는지, 그중 무엇이 brain-only student에 남는지, 그리고 남은 정보가 normative affect output에 실제로 사용되는지를 검정하는 실험 장치다. 성능은 이 해석을 가능하게 하는 gate이자 기능적 endpoint다.

## 주장하지 않을 것

- 감정은 sensory plus semantic의 합이다.
- 34-D category ontology가 14-D 또는 dimensional theory보다 참이다.
- Normative annotation이 fMRI 참가자의 주관적 감정이다.
- V-JEPA 2와 caption embedding이 인간의 visual 또는 semantic representation과 동일하다.
- Activation patching 또는 model perturbation이 인간 뇌의 인과성을 입증한다.
- 동일 자극 participant replication이 새로운 stimulus distribution generalization을 입증한다.

# 전체 의존성 지도와 단계별 Gate

Phase 0부터 5까지는 분석을 가능하게 하는 provenance와 leakage 방지 단계다. Phase 6은 shared neural organization을 검정한다. Phase 7과 8은 teacher 및 student를 학습한다. Phase 9부터 12까지는 관계의 형성, 보존, 기능적 사용을 검정한다. Phase 13과 14는 affect target 및 독립 ontology를 평가한다. Phase 15는 replication, Phase 16은 추론, Phase 17부터 21은 robustness, figure, 원고, 공개와 제출이다.

- Gate 0 — 데이터 식별성: participant, stimulus, annotation, brain response가 one-to-one 또는 명시적인 one-to-many key로 연결되고 2,180/2,181 차이가 설명되어야 한다.
- Gate 1 — 측정 신뢰도: brain response와 target이 분석 가능한 품질이며 repeated-test reliability 및 결측 구조가 문서화되어야 한다.
- Gate 2 — content organization: visual minus low-level 및 full minus visual contrast를 계산할 수 있어야 한다. 효과가 없으면 downstream model은 진행할 수 있지만 “content가 shared response를 조직한다”는 주장은 철회한다.
- Gate 3 — teacher validity: BVS teacher가 최소 baseline을 넘고 OOF cache의 leakage test를 통과해야 student guidance를 생성할 수 있다.
- Gate 4 — student readout: brain-only clean performance가 mean-profile 및 mandatory linear baseline을 넘어야 primary mechanistic interpretation을 유지한다.
- Gate 5 — relation evidence: retrieval이 permutation null을 넘고 mismatch, inheritance와 intervention 중 최소 사전 규정된 evidence chain이 수렴해야 functional-use 주장을 유지한다.
- Gate 6 — replication: frozen rule의 participant-level effect 방향과 uncertainty를 보고한다. 실패 시 generality를 주장하지 않는다.

# 즉시 실행할 첫 12개 Action Items

- [ ] A00-01. Primary 및 replication dataset의 공식 root, version, download source, license와 checksum을 기록한다.
- [ ] A00-02. Participant ID crosswalk와 stimulus hash crosswalk를 만들고 2,180/2,181 차이를 해소한다.
- [ ] A00-03. 34-D 및 14-D 원자료 codebook을 대조해 열 이름, 척도, 방향, 결측, rater 수와 raw count 가용성을 확인한다.
- [ ] A00-04. Run, presentation, repetition, TR, stimulus onset/duration과 fMRI preprocessing provenance를 manifest로 만든다.
- [ ] A00-05. 모든 stimulus를 participant 공통 outer fold에 배정하고 split intersection이 0인지 unit test를 만든다.
- [ ] A00-06. 기존 response estimate와 GLMsingle 가능성을 점검하고 label-blind reliability 비교 계획을 동결한다.
- [ ] A00-07. Schaefer/Tian ROI 정의, ROI-wise PCA, participant adapter와 ROI provenance 보존 rule을 동결한다.
- [ ] A00-08. Low-level, V-JEPA 2, caption encoder의 checkpoint, layer, pooling, 입력 전처리와 output shape을 dry run한다.
- [ ] A00-09. Analysis 1의 kernel, inner-CV, metric과 세 confirmatory contrast를 synthetic data로 검증한다.
- [ ] A00-10. B/BV/BS/BVS/shuffled teacher의 parameter parity와 stimulus-wise OOF pipeline을 synthetic data에서 검사한다.
- [ ] A00-11. Direct/Full/Shuffled student의 동일 initialization schedule과 loss 계산을 unit test한다.
- [ ] A00-12. Outcome을 보기 전에 preregistration freeze manifest를 생성하고 primary cohort analysis를 시작한다.

# Phase 0. 프로젝트 구조, provenance와 동결 체계

## A0-1. 분석 저장소와 디렉터리 계약

- [ ] 목적: 원자료, 파생자료, config, model, result와 manuscript가 섞여 재현이 불가능해지는 것을 막는다.
- [ ] 왜 필요한가: 동일 이름의 feature 또는 model이 다른 split이나 checkpoint에서 생성되면 leakage와 결과 바꿔치기를 탐지할 수 없다.
- [ ] 절차: `data_raw`, `data_manifest`, `derivatives/brain`, `derivatives/features`, `splits`, `configs`, `models`, `oof_cache`, `results`, `figures`, `logs`, `manuscript`, `release`의 논리적 구조를 정의한다. 원자료는 read-only로 취급한다.
- [ ] 산출물: `project_structure.md`, directory validation script, artifact naming convention.
- [ ] 통과 기준: 모든 파생 artifact 이름 또는 sidecar에 dataset version, cohort, participant, stimulus hash, fold, seed, config hash가 포함된다.
- [ ] 제거 또는 변경 기준: 기존 laboratory pipeline이 동등한 provenance를 자동 기록하면 새 구조를 중복 생성하지 않고 mapping만 문서화한다.
- [ ] 주장 한계: 정돈된 구조 자체는 분석의 타당성을 보증하지 않는다.

## A0-2. 환경과 dependency lock

- [ ] 목적: feature와 model 결과가 library 또는 CUDA version 차이로 달라지는 것을 추적한다.
- [ ] 절차: Python, PyTorch, CUDA, nilearn/nibabel, scikit-learn, transformer/video model library와 atlas version을 lock file에 기록한다. CPU/GPU deterministic option과 허용되는 nondeterminism을 기록한다.
- [ ] 산출물: `environment.lock`, container 또는 reproducible environment specification, hardware report.
- [ ] QA: 새 환경에서 작은 end-to-end smoke test를 재현하고 tolerance를 넘는 차이가 없는지 확인한다.
- [ ] 통과 기준: 동일 test fixture에서 output shape, hash 또는 수치 tolerance가 사전 범위 안이다.

## A0-3. Config와 결과 변경 이력

- [ ] 목적: 결과를 본 뒤 hyperparameter나 contrast가 암묵적으로 바뀌는 것을 방지한다.
- [ ] 절차: 모든 run은 immutable config와 git commit, data-manifest hash를 참조한다. Confirmatory config는 freeze 뒤 수정할 수 없고, 수정 run은 exploratory namespace에 저장한다.
- [ ] 산출물: `freeze_manifest.json`, `decision_log.md`, run registry.
- [ ] 통과 기준: 결과 표의 모든 숫자에서 원 run, config, fold와 seed를 역추적할 수 있다.

# Phase 1. 데이터 provenance와 key audit

## A1-1. Dataset inventory

- [ ] 과학적 질문: 실제 사용할 cohort, stimulus, annotation과 fMRI response의 범위는 무엇인가?
- [ ] 대안 설명: 문헌의 표본 수와 local release의 표본 수가 다르면 분석 대상 자체가 달라질 수 있다.
- [ ] 절차: 공식 source와 local directory를 대조하고 파일별 size, modified time, cryptographic hash, format과 license를 기록한다. 논문 본문 수치와 local manifest 수치를 별도 열로 둔다.
- [ ] 산출물: `datasets.tsv`, `file_checksums.tsv`, `license_notes.md`.
- [ ] 통과 기준: 분석에 들어가는 모든 파일이 하나의 versioned dataset entry에 속한다.
- [ ] 미확인 사항: 현재 기록의 primary n=6, replication n=5, stimulus 2,180/2,181은 공식 manifest 대조 전까지 검증 대기다.

## A1-2. Participant crosswalk

- [ ] 목적: fMRI, behavior, run metadata와 cohort label이 동일 participant를 가리키는지 확인한다.
- [ ] 절차: 원 ID를 외부 공개용 pseudonym과 연결하되 개인식별정보는 포함하지 않는다. Missing run, exclusion, motion/QC flag와 repeated-test 가용성을 기록한다.
- [ ] 산출물: `participants.tsv`, `participant_crosswalk_private.tsv` 또는 접근 제한 mapping.
- [ ] 통과 기준: 각 fMRI file이 정확히 한 participant와 한 cohort에 연결된다.
- [ ] 중단 기준: ID 충돌을 해소할 수 없는 participant는 사전 exclusion rule로 처리하고 이유를 기록한다.

## A1-3. Stimulus hash crosswalk

- [ ] 목적: 서로 다른 파일명이나 encoding을 가진 동일 video를 식별하고 두 cohort의 중첩을 정확히 계산한다.
- [ ] 절차: raw file hash, decoded-frame perceptual hash, duration, frame rate, resolution, audio presence를 기록한다. 동일 content의 re-encoding은 별도 raw hash와 공통 canonical stimulus ID를 갖게 한다.
- [ ] 산출물: `stimuli.tsv`, `stimulus_crosswalk.tsv`, duplicate report.
- [ ] QA: filename이 아니라 content hash 기준 중복률을 계산한다. Random sample을 시각 확인한다.
- [ ] 통과 기준: 모든 brain event와 annotation row가 canonical stimulus ID에 연결되고 2,180/2,181 차이가 missing, duplicate, excluded 중 하나로 설명된다.
- [ ] 실패 시: 미해결 stimulus는 primary에서 제외하고 sensitivity set으로 보존한다. 결과를 본 뒤 선택하지 않는다.

## A1-4. Event and run audit

- [ ] 목적: 어떤 brain response가 어떤 stimulus presentation에 대응하는지 확정한다.
- [ ] 절차: run ID, onset, duration, TR index, repetition, session, censoring과 preprocessing output을 long-form table로 만든다. Overlap, duplicate onset, stimulus outside scan과 missing response를 탐지한다.
- [ ] 산출물: `events_audited.tsv`, validation report.
- [ ] 통과 기준: 모든 usable presentation에 participant, run, canonical stimulus와 response location이 유일하게 연결된다.

# Phase 2. Annotation audit와 독립 target 정의

## A2-1. 34-D category-proportion audit

- [ ] 과학적 질문: 34-D vector가 정확히 무엇을 측정하며 어떤 scale을 갖는가?
- [ ] 왜 필요한가: proportion을 one-hot, continuous rating 또는 count로 잘못 취급하면 loss와 metric이 달라진다.
- [ ] 절차: category name, order, raw range, precision, missing, row sum, marginal prevalence, pairwise dependence를 검사한다. 각 category의 선택 count k와 rater count n을 복원할 수 있는지 확인한다.
- [ ] 산출물: `target34_codebook.tsv`, distribution report, target hash.
- [ ] 통과 기준: 모든 usable stimulus에 길이 34의 유효 vector가 있고 category order가 pipeline 전반에서 hash로 고정된다.
- [ ] 결정: raw [0,1] proportion을 유지하고 one-hot 또는 dominant label로 바꾸지 않는다.
- [ ] loss 결정: k,n이 없으면 unweighted SoftBCE를 primary로 사용한다. k,n이 확인되면 binomial NLL은 robustness로만 추가한다.
- [ ] 한계: category proportion은 participant self-report가 아니다.

## A2-2. 14-D appraisal audit

- [ ] 과학적 질문: 14개 dimension의 이름, 방향과 scale은 무엇인가?
- [ ] 절차: 공식 codebook에서 열 이름, 질문 문구, rating direction, possible range, missing code와 aggregation을 확인한다. Train-fold 표준화 전후 분포를 시각화한다.
- [ ] 산출물: `target14_codebook.tsv`, transform specification.
- [ ] 통과 기준: dimension order와 direction이 문헌 및 원자료와 일치하고 reverse coding이 unit test로 검증된다.
- [ ] 실패 시: 정의가 불분명한 dimension은 임의 해석하지 않고 primary 14-D target에서 제외 여부를 결과 전에 결정한다.

## A2-3. VA-2와 VAD-3 mapping

- [ ] 목적: low-dimensional affect core에 대한 nested control을 독립적으로 검정한다.
- [ ] 절차: 14-D codebook에서 valence, arousal, dominance에 해당하는 정확한 열을 문헌과 함께 확인한다. Dominance에 직접 대응하는 열이 없으면 유사 열을 임의로 대체하지 않는다.
- [ ] 산출물: `target_lowdim_mapping.yaml`, rationale note.
- [ ] 통과 기준: 각 dimension이 명시적인 source column과 방향을 가진다.
- [ ] 제거 기준: dominance mapping이 불충분하면 VAD-3를 제거하고 VA-2만 유지한다.

## A2-4. Target independence assertion

- [ ] 목적: 34-D, 14-D, VA-2, VAD-3가 서로를 regularize해 이론 비교가 오염되는 것을 막는다.
- [ ] 절차: target별 별도 model initialization, teacher, student, head, optimizer state, standardizer, OOF directory와 run ID를 강제한다.
- [ ] 산출물: parameter-sharing audit log.
- [ ] 통과 기준: trainable parameter object, checkpoint, cache path가 target 간 공유되지 않는다는 automated assertion이 통과한다.
- [ ] 공통으로 허용: stimulus split, architecture-selection rule, seed list와 λ candidate grid.

# Phase 3. Split, leakage 방지와 통계 단위

## A3-1. Stimulus-wise outer split

- [ ] 목적: 동일 stimulus가 participant나 modality를 통해 train과 test에 동시에 나타나는 leakage를 막는다.
- [ ] 절차: canonical stimulus ID를 기준으로 모든 participant와 modality에 공통 fold를 배정한다. Repeated presentation은 같은 fold에 묶는다. Stratification이 필요하면 target을 직접 균형화하지 않고 사전 정의 summary만 사용한다.
- [ ] 산출물: `outer_folds.tsv`, split seed와 hash.
- [ ] 통과 기준: train, validation, test stimulus intersection이 0이며 모든 cache가 같은 fold ID를 갖는다.

## A3-2. Inner validation split

- [ ] 목적: hyperparameter, PCA dimension, λ와 early stopping을 test data 없이 선택한다.
- [ ] 절차: outer-training stimulus 안에서 inner folds를 만든다. Participant는 유지하되 stimulus가 inner train/validation에 중복되지 않게 한다.
- [ ] 산출물: `inner_folds.tsv`.
- [ ] 통과 기준: 모든 tuning decision이 inner validation만 참조하고 test metric을 읽는 코드 path가 차단된다.

## A3-3. Replication freeze split

- [ ] 목적: replication cohort를 primary result에 맞춰 재설계하는 것을 막는다.
- [ ] 절차: primary outcome을 열기 전에 replication manifest, eligible participants, stimulus crosswalk와 adapter-fit rule을 생성한다.
- [ ] 산출물: `replication_manifest_preoutcome.json`.
- [ ] 통과 기준: timestamp와 hash가 primary result generation보다 빠르다.

## A3-4. Statistical unit contract

- [ ] 목적: 많은 stimulus 또는 stimulus pair를 독립 sample처럼 세어 p-value를 과대평가하지 않는다.
- [ ] 결정: participant가 primary inferential unit이다. Stimulus는 held-out generalization unit이며 seed는 inferential sample이 아니다.
- [ ] 산출물: `inference_contract.md`와 test.
- [ ] QA: bootstrap이 participant cluster를 보존하고 pairwise matrix entry를 독립 row로 전달하지 않는지 검사한다.

# Phase 4. fMRI response estimation, reliability와 brain tokens

## A4-1. Existing response baseline 재현

- [ ] 목적: 기존 dataset 또는 이전 분석의 response estimate를 재현 가능한 출발점으로 확보한다.
- [ ] 절차: 제공된 preprocessing과 beta/block-response 생성 절차를 문서화하고 일부 participant에서 reported summary를 재현한다.
- [ ] 산출물: `brain_response_baseline` cache, reproduction report.
- [ ] 통과 기준: shape, stimulus order, ROI 또는 voxel count와 summary statistic이 source record와 일치한다.

## A4-2. GLMsingle feasibility와 label-blind comparison

- [ ] 과학적 질문: raw timing과 repeated presentation이 GLMsingle single-trial beta를 신뢰성 있게 추정하기에 충분한가?
- [ ] 왜 필요한가: 더 최신이라는 이유로 response estimator를 바꾸면 안 되며 실제 reliability 개선이 있어야 한다.
- [ ] 절차: raw BOLD, design, onset, duration, confound가 완전한지 확인한다. 가능한 participant subset에서 기존 estimate와 GLMsingle을 비교하되 affect label은 보지 않는다.
- [ ] metric: repeated-test pattern correlation, split-half reliability, temporal residual diagnostics.
- [ ] 산출물: feasibility report, estimator decision record.
- [ ] 선택 기준: 사전 tolerance 이상의 reliability gain이 안정적으로 나타나고 coverage 손실이 허용 범위일 때만 GLMsingle을 primary로 선택한다.
- [ ] 반례: gain이 participant마다 뒤집히거나 많은 stimulus를 잃으면 기존 estimate를 primary로 유지한다.

## A4-3. Atlas mapping

- [ ] 목적: participant-native fMRI를 ROI provenance를 유지하는 token으로 만든다.
- [ ] 절차: Schaefer cortical atlas와 Tian subcortical atlas의 resolution/version을 고정하고 participant native space로 변환한다. Coverage, empty ROI와 voxel count를 검사한다.
- [ ] 산출물: participant별 ROI mask, coverage table, atlas transform log.
- [ ] 통과 기준: 분석 대상 ROI의 최소 voxel 수와 coverage criterion이 사전 기준을 만족한다.
- [ ] 한계: atlas ROI는 기능적으로 순수한 visual, semantic 또는 affective module이 아니다.

## A4-4. Fold-wise standardization과 ROI-PCA

- [ ] 과학적 질문: high-dimensional voxel pattern을 leakage 없이 안정적인 ROI token으로 축약할 수 있는가?
- [ ] 이유: sample 수에 비해 voxel 수가 크며 raw voxel concatenation은 과적합과 participant alignment 문제를 키운다.
- [ ] 절차: outer-training fold에서 ROI별 voxel mean/scale과 PCA를 fit하고 validation/test에 고정 적용한다. Component 수 또는 explained-variance threshold는 inner validation과 reliability를 기준으로 선택한다.
- [ ] 산출물: fold별 scaler/PCA object, token arrays, reconstruction/reliability report.
- [ ] 통과 기준: test data가 PCA fit에 들어가지 않고 ROI token identity가 유지된다.
- [ ] 대안: shrinkage projection 또는 supervised PLS는 primary outcome을 보지 않은 benchmark에서 명확히 우수할 때만 고려한다. Supervised reduction은 target leakage 위험 때문에 기본 선택이 아니다.

## A4-5. Participant-specific adapter

- [ ] 목적: participant별 measurement basis와 component orientation 차이를 공통 model width로 변환한다.
- [ ] 절차: 각 participant와 ROI의 token을 작은 linear 또는 low-rank map으로 변환한다. Adapter 뒤에도 ROI ID embedding 또는 index를 유지한다. Parameter budget을 보고한다.
- [ ] control: shared adapter, no-adapter, participant-specific adapter를 inner validation 또는 small pilot에서 비교한다.
- [ ] 통과 기준: adapter가 shared content generalization을 개선하거나 최소한 불안정성을 줄이며 participant identity shortcut을 만들지 않는다.
- [ ] 제거 기준: no-adapter가 동등하고 specific adapter가 과적합하면 primary에서 제거한다.
- [ ] 한계: 이 adapter는 개인적 감정 또는 subjectivity component가 아니다. 향후 brain token에 subject-specific affect component를 별도로 추가할 수 있다.

# Phase 5. Frozen content feature 구축

## A5-1. Low-level visual controls

- [ ] 과학적 질문: brain/content effect가 단순 luminance, color, orientation/spatial frequency 또는 motion energy로 설명되는가?
- [ ] 절차: frame-wise luminance와 color statistics, multiscale orientation/spatial-frequency energy, optical-flow 또는 motion-energy summary를 video duration에 걸쳐 사전 rule로 aggregate한다.
- [ ] 산출물: low-level feature matrix, extraction config, per-feature QC plots.
- [ ] QA: constant, near-zero variance, NaN과 duration confound를 검사한다. Feature extraction은 affect label을 사용하지 않는다.
- [ ] depth 결정: pretrained monocular depth는 semantic prior와 분리하기 어려워 primary low-level block에서 제외한다. Classical geometry로 신뢰할 수 있는 depth proxy가 있으면 exploratory로만 추가한다.
- [ ] 한계: low-level control이 모든 early visual computation을 완전히 포괄하지 않는다.

## A5-2. V-JEPA 2 spatiotemporal feature

- [ ] 목적: object, appearance, motion과 event dynamics를 하나의 affect-label-free video coordinate로 제공한다.
- [ ] 선택 이유: 정적 object encoder를 primary로 두면 짧은 video의 dynamics와 state change를 놓친다. V-JEPA 2는 video-native self-supervised representation을 제공한다.
- [ ] 절차: checkpoint, input sampling, frame rate, crop, layer, token pooling과 temporal aggregation 후보를 결과 전에 제한한다. Small batch로 output shape와 memory를 확인한다.
- [ ] 산출물: versioned feature cache, model card, compute log.
- [ ] 통과 기준: 모든 canonical stimulus에 deterministic feature가 생성되고 fold-independent frozen extraction임을 확인한다.
- [ ] 대안: 다른 video foundation model은 primary가 실패하거나 기술적으로 불가능할 때만 sensitivity로 사용한다.
- [ ] 한계: V-JEPA 2 feature는 semantic information도 포함할 수 있으며 순수 visual module로 해석하지 않는다.

## A5-3. Caption-semantic feature

- [ ] 목적: video appearance/dynamics와 부분적으로 겹치지만 human-described event, actor relation과 situation context를 제공한다.
- [ ] 절차: caption provenance와 language를 확인하고 frozen sentence encoder, checkpoint, pooling과 multiple-caption aggregation을 고정한다. Caption length와 number를 기록한다.
- [ ] 산출물: caption text manifest, sentence embedding cache, caption QC report.
- [ ] 통과 기준: stimulus별 최소 하나의 유효 caption이 있거나 missing rule이 사전 정의되어 있다.
- [ ] 대안: LLM-generated caption은 human caption과 annotation leakage 가능성이 있으므로 primary에 섞지 않는다. 필요하면 별도 exploratory branch다.
- [ ] 한계: caption은 semantic truth가 아니라 observer-generated description이다.

## A5-4. Visual–semantic overlap 진단

- [ ] 과학적 질문: V-JEPA 2와 caption representation은 어느 정도 정보를 공유하며 독립 contribution을 추정할 수 있는가?
- [ ] 절차: held-out stimulus에서 cross-validated linear predictability, feature CKA와 retrieval overlap을 descriptive diagnostic으로 계산한다. Low-level에서 예측 가능한 부분도 함께 요약한다.
- [ ] 산출물: overlap matrix와 report.
- [ ] 판정: overlap이 높아도 한 branch를 자동 제거하지 않는다. 대신 Analysis 1 nested contrast와 teacher BV/BS/BVS ladder에서 conditional contribution을 해석한다.
- [ ] 제거 기준: 한 source가 다른 source에서 거의 완전 예측되고 추가 held-out contribution이 없으며 teacher에서도 효과가 없으면 primary branch를 단순화하고 이유를 보고한다.
- [ ] 한계: statistical residual이 순수 심리 구성개념을 의미하지 않는다.

## A5-5. AlexNet historical anchor

- [ ] 목적: Kragel/Gao 계열 static-appearance 결과와 연결되는 supplementary comparison을 제공한다.
- [ ] 절차: published convention과 최대한 일치하는 pretrained AlexNet fc7 extraction을 사용한다.
- [ ] 위치: Analysis 1 supplementary only. Teacher input과 student loss에는 넣지 않는다.
- [ ] 제거 기준: 계산 부담이나 stimulus preprocessing mismatch가 크면 manuscript rationale만 남기고 분석을 제거할 수 있다.

## A5-6. Feature cache leakage audit

- [ ] 목적: feature row misalignment과 잘못된 stimulus join을 막는다.
- [ ] 절차: cache마다 canonical stimulus hash, checkpoint, layer, preprocessing hash와 feature shape를 sidecar에 저장한다.
- [ ] 통과 기준: brain, visual, caption, target row key가 exact match이고 shuffled smoke test에서 expected performance collapse가 나타난다.

# Phase 6. Analysis 1 — shared neural organization

## A6-1. Multi-kernel encoding 구현

- [ ] 과학적 질문: low-level, spatiotemporal visual, caption-semantic coordinates가 held-out brain response를 얼마나 예측하는가?
- [ ] 모델: 각 feature block의 centered normalized kernel과 nested cross-validated regularization을 사용하는 multi-kernel ridge 또는 banded-ridge-equivalent encoding.
- [ ] 선택 이유: source별 scale과 dimension이 달라도 additive conditional contribution을 평가하며 small-n fMRI에 과도한 nonlinear capacity를 넣지 않는다.
- [ ] 대안: end-to-end deep encoding은 sample size에 비해 capacity가 크고 feature attribution이 어려워 primary가 아니다. PCM/RSA는 geometry comparison에는 유용하지만 held-out response prediction과 nested conditional contribution을 동시에 주기 어렵다.
- [ ] 절차: training fold에서 kernel normalization, hyperparameter 선택과 response standardization을 fit한다. Test response는 마지막 한 번만 예측한다.
- [ ] 산출물: participant × ROI × model performance table, fold prediction cache.
- [ ] QA: synthetic additive signal 회복, no-signal permutation, duplicate-kernel behavior와 scale invariance를 test한다.

## A6-2. Nested model set과 contrasts

- [ ] M0: low-level only.
- [ ] M1: spatiotemporal visual only 또는 low-level plus visual. 정확한 nested definition을 freeze 문서에 명시한다.
- [ ] M2: spatiotemporal visual plus caption semantics, 필요하면 low-level kernel을 함께 유지한다.
- [ ] Primary contrast 1: visual minus low-level.
- [ ] Primary contrast 2: full minus visual.
- [ ] Primary contrast 3: full minus low-level.
- [ ] 목적: visual/caption의 절대 성능이 아니라 조건부 추가 설명력을 평가한다.
- [ ] 통과 기준: contrast, metric, ROI aggregation과 inference family가 결과 전에 동결된다.

## A6-3. Analysis 1 metrics

- [ ] Primary: held-out ROI response-pattern correlation 또는 사전 정의 pattern prediction correlation.
- [ ] Secondary: explained variance, voxel/ROI-wise correlation, reliability-normalized score.
- [ ] Noise ceiling: repeated-test reliability로 추정하되 불안정한 denominator에 대한 exclusion/tolerance를 정의한다.
- [ ] 보고: absolute performance와 paired difference를 모두 제시한다.
- [ ] 한계: encoding success는 model-computational use나 affect mechanism을 뜻하지 않는다.

## A6-4. Analysis 1 decision

- [ ] Visual minus low-level이 안정적으로 양수면 visual representation이 단순 통계 이상을 제공한다고 보고한다.
- [ ] Full minus visual이 양수면 caption-derived coordinate가 visual representation에 조건부 정보를 더한다고 보고한다.
- [ ] Full minus visual이 0이면 semantics가 무관하다고 단정하지 않고 chosen caption representation에서 추가 predictive value가 없다고 제한한다.
- [ ] Full model이 baseline을 넘지 못하면 thesis의 neural-organization 부분을 철회하고 downstream model 결과를 exploratory 또는 engineering result로 격하한다.

# Phase 7. Primary 34-D multimodal teacher

## A7-1. Teacher architecture 최소화

- [ ] 목적: brain–visual–semantic relation을 학습할 충분한 capacity를 가지되 작은 dataset에서 과적합과 해석 불가능성을 줄인다.
- [ ] 입력: participant-specific ROI brain tokens, frozen V-JEPA 2 vector/tokens, frozen caption vector/tokens.
- [ ] 구조: modality projector, compact fusion module, fused brain-token state, joint latent, 34 sigmoid head.
- [ ] 선택 이유: modality provenance와 ROI identity를 fusion 전후 stage에서 추적하고 activation patching 가능한 지점을 제공한다.
- [ ] 대안: 거대 LLM fusion은 sample size와 causal interpretation에 부적합하므로 primary에서 제외한다. Simple concatenation plus MLP는 mandatory ablation 또는 fallback이다.
- [ ] 산출물: architecture spec, parameter count, tensor-shape diagram, forward-pass test.

## A7-2. Matched teacher ladder

- [ ] B: brain only.
- [ ] BV: brain plus visual.
- [ ] BS: brain plus caption semantics.
- [ ] BVS: brain plus visual plus caption semantics.
- [ ] Shuffled BVS: 같은 input distribution과 capacity를 유지하되 training-fold stimulus correspondence를 끊는다.
- [ ] 목적: modality 추가에 따른 capacity 증가, soft-label difficulty와 올바른 alignment의 효과를 구분한다.
- [ ] 절차: missing modality는 mask token으로 대체하고 가능한 한 동일 brain encoder, fusion depth, head와 parameter budget을 유지한다.
- [ ] QA: parameter count, optimizer, schedule, batch composition, seed가 matched인지 자동 비교한다.
- [ ] 한계: BV minus B와 BS minus B는 architecture와 optimization이 완전히 동일하지 않을 수 있으므로 conditional evidence이지 pure component decomposition이 아니다.

## A7-3. Teacher target loss

- [ ] Primary loss: dimension-averaged SoftBCE on 34-D proportions.
- [ ] 왜 필요한가: 각 output은 binary category selection probability의 soft target으로 해석할 수 있고 one-hot classification을 강제하지 않는다.
- [ ] Secondary metric: stimulus-wise profile correlation, Brier, RMSE, calibration.
- [ ] Robustness: k,n 확인 시 binomial NLL.
- [ ] 사용하지 않을 것: primary correlation loss 단독 사용. Correlation은 profile shape에 민감하지만 absolute calibration과 base rate를 무시하므로 evaluation metric으로 두고 supervised primary loss로 쓰지 않는다.
- [ ] QA: all-zero/constant target, extreme probability와 numerical stability test.

## A7-4. Stimulus-wise OOF teacher generation

- [ ] 목적: student가 학습할 stimulus의 true label을 이미 본 teacher로부터 guidance를 받는 leakage를 방지한다.
- [ ] 절차: outer fold i의 모든 participant에서 stimulus i-set을 제외하고 teacher를 fit한다. Teacher를 freeze한 뒤 excluded stimulus를 예측한다. 모든 fold prediction을 원 stimulus order로 합친다.
- [ ] 산출물: `teacher_oof_target34` cache, fold checkpoint, provenance sidecar.
- [ ] QA: 각 prediction의 generating teacher training set에 해당 canonical stimulus가 없는지 assertion한다.
- [ ] 통과 기준: 전체 eligible stimulus에 exactly one OOF prediction이 있고 duplicate/missing이 0이다.
- [ ] OOF의 의미: 별도 loss나 metric이 아니라 prediction generation procedure다.

## A7-5. Teacher validity gate

- [ ] BVS teacher의 held-out 34-D performance가 mean-profile baseline을 넘어야 한다.
- [ ] BVS minus shuffled가 양수인지 확인한다.
- [ ] BVS가 BV와 BS 모두를 반드시 이겨야 한다는 절대 조건은 두지 않되, 이기지 못하면 joint synergy 주장을 하지 않는다.
- [ ] 실패 시: student distillation은 generic teacher experiment로는 진행 가능하지만 brain–visual–semantic joint relation 주장은 격하한다.

# Phase 8. Brain-only student와 learning conditions

## A8-1. Mandatory linear baseline

- [ ] 목적: deep student가 실제로 필요한지 검정한다.
- [ ] 모델: 동일 ROI-PCA input의 multi-output ridge와, 필요하면 reduced-rank regression.
- [ ] 선택: inner validation에서 안정성과 held-out metric을 기준으로 하나를 mandatory comparator로 고정한다.
- [ ] 통과 기준: nonlinear student가 여러 seed와 participant에서 baseline을 일관되게 넘지 못하면 단순 model을 primary로 승격한다.

## A8-2. Student architecture

- [ ] 입력: brain ROI tokens only.
- [ ] 구조: participant adapter, small shared token encoder, final latent, 34-D joint head.
- [ ] 목적: teacher의 privileged content가 시험 시 없이도 brain representation에 남는지 검정한다.
- [ ] 제약: visual/caption token은 student forward에 들어가지 않는다. Caption dropout이 아니라 완전 brain-only inference다.
- [ ] 산출물: architecture spec, parameter count, inference contract.

## A8-3. Direct, Full-guided, Shuffled-guided

- [ ] Direct: SoftBCE label loss only.
- [ ] Full-guided: SoftBCE plus λ probability-MSE to aligned BVS OOF teacher.
- [ ] Shuffled-guided: SoftBCE plus 동일 λ와 동일 OOF vector를 사용하되 stimulus pairing만 train fold 안에서 permutation.
- [ ] 과학적 질문: aligned multimodal guidance가 단순 추가 loss, smoothing 또는 output covariance보다 더 유용한가?
- [ ] QA: 세 조건의 architecture, initialization schedule, seed, optimizer, early stopping과 batch order를 맞춘다.
- [ ] Shuffled rule: output vector 내부 34-D covariance와 marginal distribution을 보존하고 stimulus correspondence만 끊는다.

## A8-4. Student objective와 λ selection

- [ ] Loss: `L=SoftBCE(y,pS)+λ mean_d(pT_OOF−pS)^2`.
- [ ] 이유: label accuracy와 teacher probability structure를 분리해 최적화하며 probability-MSE는 calibrated vector의 절대 차이를 보존한다.
- [ ] λ grid: 사전 제한된 `{0.1, 0.3, 1.0}` 또는 compute pilot 후 결과 전에 확정한 grid.
- [ ] 선택: target별 inner validation only.
- [ ] 보고: 두 loss term의 raw magnitude와 normalized magnitude를 기록한다.
- [ ] 사용하지 않을 것: teacher latent/CKA/retrieval alignment loss. 이것들을 loss에 넣으면 사후 inheritance analysis가 자명해진다.

## A8-5. Training QA

- [ ] Train/validation curve, gradient norm, output saturation, per-dimension prediction variance를 저장한다.
- [ ] Seed 최소 수를 freeze하고 세 condition에 동일 seed list를 사용한다.
- [ ] Early stopping은 validation metric만 사용한다.
- [ ] Test는 모든 selection이 끝난 뒤 한 번 평가한다.
- [ ] Degenerate solution: mean profile만 출력하거나 variance가 사라지는 run을 detect하고 exclusion rule을 결과 전에 정의한다.

# Phase 9. Analysis 2A — teacher가 관계를 어떻게 형성했는가

## A9-1. Held-out correct and mismatch triplets

- [ ] 과학적 질문: 올바른 brain–video–caption correspondence가 fusion-stage representation과 output을 변화시키는가?
- [ ] Conditions: correct `(Bi,Vi,Si)`, video swap `(Bi,Vj,Si)`, caption swap `(Bi,Vi,Sj)`, both swap `(Bi,Vj,Sj)`.
- [ ] Both-swap 이유: V–S content coherence는 유지하면서 brain과 content의 correspondence를 끊는다.
- [ ] Single-swap 해석: 한 modality correspondence뿐 아니라 V–S coherence도 바뀌므로 unique visual 또는 semantic causal effect로 부르지 않는다.
- [ ] 절차: held-out set 안 derangement를 사전 seed로 여러 번 생성하고 평균한다.
- [ ] 산출물: mismatch index files, stage activation cache, output table.

## A9-2. Matched mismatch robustness

- [ ] 목적: mismatch effect가 단순 luminance, motion, caption length 또는 target distance 때문인지 줄인다.
- [ ] 절차: low-level video statistics, duration, caption length와 가능한 target-independent descriptor가 비슷한 후보 안에서 j를 선택한다.
- [ ] 지위: robustness, primary mismatch를 대체하지 않는다.
- [ ] 한계: 완전 matching은 불가능하며 conditioning variable에 따라 새로운 bias가 생길 수 있다.

## A9-3. Stagewise measures

- [ ] Projected brain, visual, semantic token.
- [ ] Fusion block별 post-fusion brain-token state.
- [ ] Joint latent.
- [ ] 34-D teacher output.
- [ ] Measure 1: paired correct–mismatch representation distance.
- [ ] Measure 2: correct teacher-joint/video/caption retrieval rank.
- [ ] Measure 3: output profile correlation, Brier 또는 change from clean.
- [ ] 목적: relation이 input similarity가 아니라 fusion 과정의 어느 stage에서 나타나는지 추적한다.
- [ ] 판정: early stage부터 나타나도 architecture shortcut 가능성을 검토하며, stage localization을 human brain processing stage와 동일시하지 않는다.

## A9-4. Teacher relation-formation decision

- [ ] Correct가 both-swap보다 joint retrieval과 affect output에서 안정적으로 우수하면 aligned brain–content correspondence evidence로 본다.
- [ ] Video-swap과 caption-swap 차이는 source-specific sensitivity로 기술하되 pure modality essence로 해석하지 않는다.
- [ ] Correct–mismatch가 output에서만 나타나고 latent/retrieval에서 없으면 relation formation보다 head-level calibration effect 가능성을 우선한다.
- [ ] 모든 mismatch가 clean과 같으면 teacher가 content alignment를 사용하지 않았다고 보고 downstream mechanistic thesis를 낮춘다.

# Phase 10. Analysis 2B — student가 무엇을 보존했는가

## A10-1. Frozen stage extraction

- [ ] 목적: 학습 후 representation을 training objective와 분리해 분석한다.
- [ ] Stage: participant adapter, encoder block 1, block 2 또는 실제 architecture의 사전 지정 block, final latent.
- [ ] 절차: model을 evaluation mode로 freeze하고 held-out stimulus activation을 반복 presentation 규칙에 따라 평균한다.
- [ ] 산출물: condition × participant × fold × stage activation cache.
- [ ] QA: activation extraction이 gradient와 batch statistic update를 발생시키지 않는다.

## A10-2. Teacher-joint low-capacity probe와 retrieval

- [ ] 과학적 질문: brain-only student stage에서 training-only teacher joint content가 읽히는가?
- [ ] 절차: training fold에서 linear 또는 reduced-rank map을 teacher joint latent로 fit하고 held-out brain query에서 candidate joint latent를 rank한다.
- [ ] Metrics: top-1, top-5 또는 사전 k, median rank, mean reciprocal rank.
- [ ] Control: shuffled-label probe, random projection, matched parameter capacity.
- [ ] 통과 기준: retrieval이 permutation null을 넘고 Full minus Direct 및 Full minus Shuffled가 같은 방향이다.
- [ ] 한계: decodability는 output use를 보이지 않는다.

## A10-3. Visual and semantic held-out probes

- [ ] 목적: student가 teacher output만 안내받았음에도 어떤 content view를 보존했는지 구분한다.
- [ ] Visual target: training-fold PCA로 축약한 frozen V-JEPA 2 feature.
- [ ] Semantic target: frozen caption embedding 또는 training-fold PCA 축약본.
- [ ] 절차: 각 stage에서 동일 capacity의 linear/reduced-rank probe를 fit하고 correct-video/caption retrieval을 계산한다.
- [ ] 중요한 위치: 이들은 post-training evaluation이며 student training loss가 아니다.
- [ ] 한계: V-JEPA 2와 caption의 겹치는 content 때문에 visual-only 또는 semantic-only neural code로 해석하지 않는다.

## A10-4. Linear CKA geometry map

- [ ] 과학적 질문: student stage의 전체 stimulus geometry가 teacher joint, visual, semantic, affect reference 중 무엇과 유사한가?
- [ ] 절차: 동일 held-out stimulus order에서 centered linear CKA를 계산한다. Stage × reference heatmap으로 absolute CKA와 Full minus Direct, Full minus Shuffled를 제시한다.
- [ ] 선택 이유: orthogonal transform과 isotropic scaling에 비교적 안정적인 global geometry summary다.
- [ ] 지위: secondary. CKA는 probe/retrieval, patching 또는 perturbation을 대체하지 않는다.
- [ ] Null: stimulus label 공동 permutation.
- [ ] 한계: CKA 유사성은 정보의 사용, directionality 또는 causal mechanism을 뜻하지 않는다.

## A10-5. Neighborhood와 exemplar

- [ ] 목적: aggregate score를 사람이 이해할 수 있는 held-out content 관계로 보여준다.
- [ ] Quantitative: k-nearest-neighbor overlap, correct rank, error-category summary.
- [ ] Exemplar selection: 사전 정의 quantile에서 typical success, typical failure, condition-disagreement를 선택한다.
- [ ] Cherry-picking 방지: manual 선별 전 complete rank table과 selection script를 고정한다.
- [ ] 한계: exemplar는 통계 결과의 예시이며 독립 증거가 아니다.

## A10-6. Inheritance decision

- [ ] Full minus Direct > 0이고 Full minus Shuffled > 0이면 aligned guidance-specific recovery를 지지한다.
- [ ] Full > Direct이지만 Full ≈ Shuffled이면 generic extra-loss 또는 soft-target regularization으로 제한한다.
- [ ] CKA만 증가하고 retrieval이 null이면 geometry-level descriptive effect로만 보고한다.
- [ ] Retrieval은 증가하지만 affect performance가 없으면 preserved content가 task output에 유용하다는 결론을 내리지 않는다.

# Phase 11. Analysis 2C — teacher activation patching

## A11-1. Patch site와 scope 동결

- [ ] 목적: mismatch로 손상된 computation의 어떤 stage가 content와 affect output 회복에 충분한지 검정한다.
- [ ] 후보: post-fusion brain-token group, joint latent. 모든 unit을 탐색한 뒤 좋은 site만 보고하지 않는다.
- [ ] 절차: 사전 정의 stage와 token scope를 freeze하고 clean, mismatch, patched forward를 동일 sample에서 실행한다.
- [ ] 산출물: patch plan, site index, activation cache.

## A11-2. Recovery metrics

- [ ] Raw recovery: `metric(patched)−metric(mismatch)`.
- [ ] Normalized recovery: `[metric(patched)−metric(mismatch)]/[metric(clean)−metric(mismatch)]`.
- [ ] Readouts: correct-video retrieval, correct-caption retrieval, teacher-joint retrieval, 34-D output metric.
- [ ] Denominator rule: clean minus mismatch가 사전 tolerance 이하이면 normalized recovery를 missing 처리하고 raw recovery만 보고한다.
- [ ] 목적: retrieval만 또는 output만 회복되는 경우를 구분한다.

## A11-3. Matched patch nulls

- [ ] Wrong-stimulus clean activation.
- [ ] Random stage 또는 random token의 같은 크기 patch.
- [ ] Same-norm noise 또는 permutation patch가 기술적으로 가능한 경우.
- [ ] 통과 기준: correct clean patch가 matched null보다 content와 affect readout을 함께 더 회복한다.
- [ ] 한계: model activation intervention이며 뇌 activation 개입이 아니다.

## A11-4. Patching decision

- [ ] Content retrieval과 affect output이 함께 회복되면 해당 frozen teacher computation에서 functional use evidence로 본다.
- [ ] Retrieval만 회복되면 content representation은 있으나 affect head가 사용한다는 증거가 부족하다.
- [ ] Affect만 회복되면 nonspecific activation magnitude 또는 head shortcut을 우선 검토한다.
- [ ] Null과 구별되지 않으면 patching-based mechanism 주장을 철회한다.

# Phase 12. Analysis 2D — student anatomical-network reliance

## A12-1. Network grouping 사전 정의

- [ ] 목적: student가 어떤 anatomical brain-token group에 의존해 content와 affect를 읽는지 검정한다.
- [ ] 절차: Schaefer network label과 Tian subcortical grouping을 outcome 전에 고정한다. 결과에 따라 ROI를 visual, semantic, affective로 재명명하지 않는다.
- [ ] 산출물: `network_groups.tsv`, atlas version과 ROI list.
- [ ] 통과 조건: ROI-PCA 및 participant adapter가 ROI identity를 보존한다.
- [ ] 중단 조건: token mixing으로 provenance를 추적할 수 없으면 primary network perturbation을 실행하지 않는다.

## A12-2. Primary perturbation

- [ ] 절차: held-out set에서 한 network의 ROI token을 participant 안 다른 stimulus의 같은 ROI token과 공동 permutation한다.
- [ ] 이유: marginal distribution과 ROI identity를 유지하면서 stimulus-specific information을 끊는다.
- [ ] Readouts: teacher-joint, video, caption retrieval과 34-D affect performance drop.
- [ ] 산출물: network × participant × condition × seed effect table.
- [ ] Null: 동일 token 수의 random ROI grouping 또는 identity-preserving random perturbation.

## A12-3. Robustness perturbations

- [ ] Training-fold mean-token replacement.
- [ ] Leave-one-network-out refit.
- [ ] Perturbation magnitude matching.
- [ ] 목적: 한 replacement artifact에만 의존하는 결과를 걸러낸다.
- [ ] 해석: primary와 robustness 방향이 뒤집히면 reliance conclusion을 철회한다.

## A12-4. Reliance decision

- [ ] Full-guided에서 특정 network perturbation이 content와 affect readout을 함께 떨어뜨리고 matched null을 넘으면 model reliance로 보고한다.
- [ ] Direct와 Full 차이는 guidance가 reliance pattern을 바꿨는지 보여주는 secondary contrast다.
- [ ] 결과를 인간 뇌의 causal contribution 또는 functional specialization으로 표현하지 않는다.

# Phase 13. Analysis 3 — 34-D functional affect readout

## A13-1. Primary metric

- [ ] 과학적 질문: recovered brain-only representation이 각 stimulus의 34-D profile shape를 예측하는가?
- [ ] Metric: stimulus-wise predicted/observed profile Pearson r, Fisher z 후 participant summary.
- [ ] 이유: 34개 값의 전체 조합과 상대 shape를 평가하며 단일 category accuracy로 환원하지 않는다.
- [ ] 반드시 함께 보고: mean-profile baseline, Brier, RMSE, calibration, dimension-wise macro-Fisher-z.
- [ ] 한계: correlation은 level/calibration을 무시하므로 단독 성공 기준이 아니다.

## A13-2. Baselines

- [ ] Training-fold mean-profile을 모든 test stimulus에 예측.
- [ ] Multi-output ridge 또는 reduced-rank brain-only baseline.
- [ ] Direct student.
- [ ] Shuffled-guided student.
- [ ] Optional brain-only teacher distillation control은 supplementary.
- [ ] 목적: base rate, simple linear mapping, nonlinear architecture, extra guidance loss와 meaningful alignment를 분리한다.

## A13-3. Primary contrasts

- [ ] Full minus Direct: multimodal guidance의 총 효과.
- [ ] Full minus Shuffled: 올바른 brain–stimulus alignment에 특이적인 효과.
- [ ] 두 contrast가 같은 방향이어야 aligned guidance claim을 유지한다.
- [ ] Report: participant별 paired dot, group estimate, CI, corrected p와 seed variability.

## A13-4. Calibration and residual profile checks

- [ ] Category별 calibration curve와 Brier decomposition이 가능한지 확인한다.
- [ ] Training-fold base rate를 제거한 residual profile correlation을 robustness로 계산한다.
- [ ] Rare category가 metric을 지배하는지 dimension prevalence와 error relation을 본다.
- [ ] k,n이 확인되지 않으면 binomial uncertainty를 과장해 모델링하지 않는다.

## A13-5. Mechanistic interpretation gate

- [ ] Gate A: Full-guided clean performance가 mean-profile baseline을 넘는다.
- [ ] Gate B: mandatory linear/reduced-rank baseline을 넘거나 최소한 비열등하면서 relation evidence가 추가된다.
- [ ] Gate C: teacher-joint, visual 또는 semantic retrieval 중 사전 지정 readout이 permutation null을 넘는다.
- [ ] Gate D: activation patching 또는 network perturbation이 content와 affect output에서 수렴한다.
- [ ] Gate 실패 시: prediction은 보고하되 mechanism wording을 exploratory diagnostic으로 낮춘다.

# Phase 14. Independent 14-D, VA-2, VAD-3 analyses

## A14-1. 별도 model training

- [ ] 14-D, VA-2, VAD-3 각각 새 random initialization, teacher, OOF cache, student, head와 standardizer를 사용한다.
- [ ] BVS teacher와 Direct/Full/Shuffled student의 final functional contrast에 집중한다.
- [ ] Paper size와 multiple comparison을 통제하기 위해 full layerwise mismatch/patching/CKA를 모두 반복하지 않는다.

## A14-2. Continuous-target objectives

- [ ] Teacher: dimension-normalized MSE on training-fold standardized target.
- [ ] Student: target MSE plus λ OOF-teacher MSE.
- [ ] Evaluation: dimension-wise across-stimulus correlation의 macro-Fisher-z.
- [ ] Secondary: original-scale RMSE, concordance correlation coefficient, valence/arousal/dominance individual metrics.
- [ ] QA: standardizer가 outer-training data에만 fit되는지 검사한다.

## A14-3. Within-target contrasts only

- [ ] 각 target 안에서 Full minus Direct와 Full minus Shuffled를 계산한다.
- [ ] Raw 34-D correlation과 14-D correlation을 직접 순위화하지 않는다.
- [ ] 필요하면 within-target standardized gain과 participant별 effect direction만 비교한다.
- [ ] 이유: output dimension, scale, reliability와 metric difficulty가 달라 absolute score가 이론의 승패가 될 수 없다.

## A14-4. Theory interpretation matrix

- [ ] 모든 target 성공: aligned guidance가 low-dimensional core부터 fine-grained profile까지 일반화될 가능성.
- [ ] VA/VAD만 성공: broad valence, activation, dominance 관련 signal로 제한.
- [ ] 14-D와 34-D 성공, VA/VAD 실패: low-dimensional core만으로 환원되지 않는 broader organization 가능성.
- [ ] 34-D만 성공: category-profile-specific result.
- [ ] 14-D만 성공: appraisal-space-specific result.
- [ ] 어떤 pattern도 한 ontology가 진실임을 증명하지 않는다.

# Phase 15. Independent participant replication

## A15-1. Freeze transfer

- [ ] Primary cohort에서 checkpoint, layer, preprocessing, atlas, ROI-PCA rule, architecture, λ grid, seed, metric, contrast와 inference를 동결한다.
- [ ] Replication cohort에서는 participant adapter만 사전 규칙대로 새로 fit한다.
- [ ] Hyperparameter를 replication outcome에 맞춰 retune하지 않는다. 필요한 adaptation은 별도 exploratory result다.

## A15-2. Stimulus overlap accounting

- [ ] 두 cohort의 exact shared, unique, missing stimulus 수를 hash crosswalk로 보고한다.
- [ ] Shared-stimulus analysis와 cohort-specific held-out analysis의 목적을 분리한다.
- [ ] 같은 stimulus이므로 replication을 stimulus-generalization이라고 부르지 않는다.

## A15-3. Replication outcomes

- [ ] Analysis 1 primary contrast direction.
- [ ] 34-D Full minus Direct와 Full minus Shuffled direction.
- [ ] 최소 사전 지정 retrieval/reliance signature.
- [ ] 14-D/VA/VAD final functional contrast.
- [ ] Report: replication effect, CI, primary-replication heterogeneity, participant-level plot.
- [ ] 판정: p-value 일치보다 effect direction, interval overlap과 preregistered replication criterion을 사용한다.

# Phase 16. Statistical inference와 multiple comparisons

## A16-1. Effect table specification

- [ ] 모든 confirmatory effect에 contrast, metric, sign convention, aggregation, participant unit, null generation, bootstrap, family와 correction method를 기록한다.
- [ ] 산출물: `confirmatory_effects.tsv`.
- [ ] 통과 기준: 결과 계산 전에 행 목록과 hash가 동결된다.

## A16-2. Bootstrap

- [ ] Participant-clustered bootstrap을 primary CI에 사용한다.
- [ ] Stimulus resampling이 추가되면 participant 구조를 보존한 hierarchical bootstrap으로 명시한다.
- [ ] Seed를 bootstrap sample로 세지 않는다. Seed는 model uncertainty summary로 별도 표시한다.
- [ ] QA: known synthetic effect와 null에서 coverage를 simulation으로 확인한다.

## A16-3. Permutation

- [ ] Analysis 1: stimulus labels를 participant pairing을 보존한 채 permutation.
- [ ] Retrieval/CKA: reference stimulus order를 공동 permutation.
- [ ] Student shuffled guidance: training fold 안 permutation이며 statistical null permutation과 구분한다.
- [ ] Network perturbation: matched random network/token grouping null.
- [ ] QA: exchangeability 조건과 fixed effects를 문서화한다.

## A16-4. Multiple-comparison families

- [ ] Family 1: Analysis 1의 세 nested contrasts.
- [ ] Family 2: teacher B/BV/BS/BVS/shuffled contrasts.
- [ ] Family 3: mismatch × stage.
- [ ] Family 4: patch × readout.
- [ ] Family 5: student condition × retrieval reference.
- [ ] Family 6: network × readout.
- [ ] Family 7: target별 Full minus Direct/Full minus Shuffled.
- [ ] Correction method를 각 family의 hypothesis structure와 함께 동결한다.

## A16-5. Missing and exclusion handling

- [ ] Participant, stimulus, ROI, category와 run exclusion rule을 outcome 전에 정한다.
- [ ] Missing result를 0 effect로 대체하지 않는다.
- [ ] Denominator tolerance, undefined correlation, constant output handling을 명시한다.
- [ ] Exclusion 전후 sensitivity를 보고한다.

# Phase 17. Robustness와 falsification analyses

## A17-1. Feature robustness

- [ ] V-JEPA 2 layer/pooling의 제한된 alternative.
- [ ] Caption aggregation alternative.
- [ ] AlexNet historical anchor.
- [ ] Low-level control definition alternative.
- [ ] 지위: primary decision을 바꾸지 않는 supplementary sensitivity.

## A17-2. Response robustness

- [ ] Existing beta versus GLMsingle if both feasible.
- [ ] ROI-PCA dimension alternative.
- [ ] Reliability-normalized versus raw performance.
- [ ] Participant adapter versus shared/no adapter.

## A17-3. Model robustness

- [ ] Concatenation plus MLP teacher fallback.
- [ ] Linear/reduced-rank student.
- [ ] λ sensitivity.
- [ ] Seed variability.
- [ ] Parameter-count matched controls.

## A17-4. Interpretation robustness

- [ ] Matched mismatch.
- [ ] Patch null variants.
- [ ] Network replacement variants.
- [ ] Base-rate-residualized 34-D correlation.
- [ ] Retrieval candidate-set size sensitivity.

## A17-5. Falsification log

- [ ] 각 primary claim에 반례를 사전 기록한다.
- [ ] Claim 1 반례: full content가 visual 또는 low-level을 넘지 못함.
- [ ] Claim 2 반례: correct와 mismatch가 구별되지 않거나 Full과 Shuffled가 같음.
- [ ] Claim 3 반례: retrieval은 가능하지만 patch/perturbation이 affect output을 바꾸지 않음.
- [ ] Claim 4 반례: replication effect가 반대이거나 interval이 사전 criterion을 충족하지 못함.
- [ ] 결과에 따라 해당 claim을 삭제, 축소 또는 exploratory로 이동한다.

# Phase 18. Failure-path decision tree

## A18-1. Analysis 1 실패

- [ ] Feature extraction, key alignment, noise ceiling과 response reliability를 먼저 확인한다.
- [ ] 기술적 오류가 없으면 content-organization claim을 철회한다.
- [ ] Teacher/student 결과는 predictive model study로 남길 수 있으나 sensory-semantic neural organization의 근거로 연결하지 않는다.

## A18-2. Teacher 성공, student 실패

- [ ] Brain-only signal-to-noise, capacity와 OOF teacher quality를 점검한다.
- [ ] Student architecture를 무제한 확장하지 않는다.
- [ ] 결과는 privileged multimodal teacher가 relation을 형성하지만 brain-only transfer는 제한적이라고 보고한다.

## A18-3. Prediction 성공, relation evidence 실패

- [ ] Full versus Shuffled, retrieval null, patching null을 확인한다.
- [ ] 결론을 improved decoder 또는 generic distillation으로 제한한다.
- [ ] Mechanistic wording과 brain–content learning claim을 삭제한다.

## A18-4. Relation evidence 성공, affect prediction 실패

- [ ] Student가 content를 보존하지만 normative affect mapping에 충분하지 않다고 보고한다.
- [ ] 34-D task difficulty와 target reliability를 논의하되 실패를 숨기지 않는다.
- [ ] Foundation-model 성능 claim을 하지 않는다.

## A18-5. Primary 성공, replication 실패

- [ ] Cohort preprocessing, reliability, participant adapter와 shared-stimulus coverage 차이를 기술한다.
- [ ] Primary result는 cohort-specific으로 제한한다.
- [ ] Replication-specific retuning은 exploratory appendix로만 제시한다.

# Phase 19. Figure와 table 생산

## A19-1. Figure 1 — Study overview

- [ ] 메시지: organization → relation formation/inheritance/use → affect readout → replication.
- [ ] 포함: primary/replication cohort, frozen content views, analysis gates, independent targets.
- [ ] 제외: 결과 숫자와 과도한 model detail.
- [ ] QA: figure만 보고도 decoding이 갑자기 등장하지 않고 Analysis 1에서 3으로 이어지는 이유가 보여야 한다.

## A19-2. Figure 2 — Model architecture and tests

- [ ] Panel A: paired brain+video+caption training, participant map, teacher, 34-D normative target, OOF guidance와 losses.
- [ ] Panel B: brain-only inference, no video/caption/teacher/label.
- [ ] Panel C: after-training teacher mismatch, student probes/retrieval, CKA, activation patching와 anatomical reliance.
- [ ] 표기: visual/semantic probes are held-out evaluation, not training losses.
- [ ] Target box: 34-D primary, 14-D/VA-2/VAD-3 independent runs.
- [ ] Design: v24의 직관적 panel 구조를 보존하고 형광색을 줄인 academic palette를 사용한다.

## A19-3. Figure 3 — Analysis 1

- [ ] Participant-level paired effect plot.
- [ ] Nested model absolute performance.
- [ ] Visual minus low-level, full minus visual, full minus low-level.
- [ ] Exploratory ROI map은 main confirmatory plot과 분리한다.

## A19-4. Figure 4 — Analysis 2

- [ ] Teacher ladder와 correct–mismatch stage plot.
- [ ] Full/Direct/Shuffled stagewise retrieval.
- [ ] Linear CKA heatmap은 secondary label을 명확히 한다.
- [ ] Activation-patching recovery와 network perturbation drop.
- [ ] Content와 affect readout의 수렴 또는 불일치를 같은 scale/legend로 보여준다.

## A19-5. Figure 5 — Analysis 3 and replication

- [ ] 34-D profile examples는 사전 exemplar rule로 선택한다.
- [ ] Full minus Direct, Full minus Shuffled participant effects.
- [ ] 14-D, VA-2, VAD-3는 raw score가 아니라 within-target effect 중심으로 표시한다.
- [ ] Primary와 replication effect를 나란히 배치한다.

## A19-6. Tables

- [ ] Table 1: verified dataset/cohort/stimulus/annotation/response summary.
- [ ] Table 2: model component, scientific question, rationale, alternative, limitation.
- [ ] Table 3: confirmatory contrast, metric, statistical unit, null, correction, falsifying result.
- [ ] Table 4: ablated/removed/supplementary analysis와 scope rationale.
- [ ] Supplementary table: all participant/seed results and exact hyperparameters.

# Phase 20. Manuscript 작성과 claim audit

## A20-1. Methods finalization

- [ ] Phase 0–5의 verified 값으로 bracket와 provisional wording을 교체한다.
- [ ] Dataset version, sample size, exclusion, split, checkpoint, layer, pooling, atlas, loss, λ, seeds와 statistics를 모두 명시한다.
- [ ] 결과를 재현하는 데 필요한 선택을 supplementary가 아닌 Methods 또는 open config에 둔다.

## A20-2. Results 작성

- [ ] 분석 순서를 바꾸지 않는다: Analysis 1 organization, Analysis 2 relation formation/inheritance/use, Analysis 3 affect readout, independent targets, replication.
- [ ] 각 절에서 absolute performance, paired contrast, CI, corrected inference와 participant consistency를 보고한다.
- [ ] Null result와 failed gate를 동일한 가시성으로 보고한다.
- [ ] Model performance adjective 대신 실제 effect와 interval을 쓴다.

## A20-3. Discussion 작성

- [ ] 첫 문단은 실제로 지지된 thesis 범위만 요약한다.
- [ ] Kragel 2019와의 연결: visual schema에서 natural-video brain–content relation과 brain-only functional use로의 확장 여부.
- [ ] Du et al. 관련 연결: model이 무엇을 배웠는지 해석하되 method 복제 자체가 novelty가 아님을 명시한다.
- [ ] Normative annotation, content overlap, model intervention와 participant-level replication의 한계를 명시한다.
- [ ] Future foundation model은 discussion implication이며 현재 contribution으로 과장하지 않는다.

## A20-4. Claim-to-evidence matrix

- [ ] 모든 abstract, introduction hypothesis, results statement와 discussion claim을 evidence row에 연결한다.
- [ ] 각 claim에 supporting figure/table, analysis gate, alternative explanation과 forbidden wording을 기록한다.
- [ ] 산출물: `claim_evidence_matrix.tsv`.
- [ ] 통과 기준: 근거가 없는 문장은 삭제하거나 hypothesis/future work로 바뀐다.

## A20-5. Citation audit

- [ ] 모든 model, dataset, atlas, loss, interpretation method와 theory claim에 primary source를 연결한다.
- [ ] Reference metadata, DOI/URL, publication status를 확인한다.
- [ ] Preprint는 preprint로 표시하고 이후 peer-reviewed version 존재 여부를 확인한다.
- [ ] 문헌이 선택 이유를 실제로 지지하는지, 단순 유명 논문 인용인지 검토한다.

# Phase 21. Reproducibility, 공개와 제출

## A21-1. End-to-end pipeline

- [ ] 한 command 또는 documented workflow로 manifest audit부터 final tables/figures까지 재생성한다.
- [ ] Raw data가 공개 불가하면 synthetic fixture와 expected outputs를 제공한다.
- [ ] 각 stage는 input/output contract와 resume point를 갖는다.
- [ ] 통과 기준: clean environment에서 smoke test와 공개 가능한 subset run이 성공한다.

## A21-2. Automated tests

- [ ] Key uniqueness와 crosswalk completeness.
- [ ] Train/validation/test overlap 0.
- [ ] Target order/hash consistency.
- [ ] Fold-wise scaler/PCA leakage 0.
- [ ] OOF teacher training-set exclusion.
- [ ] Parameter sharing 0 across target spaces.
- [ ] Condition parameter/schedule parity.
- [ ] Visual/semantic probes absent from training loss.
- [ ] Statistical unit and bootstrap cluster preservation.
- [ ] Figure table values match result artifacts.

## A21-3. Model and data cards

- [ ] Teacher/student intended use와 non-use.
- [ ] Dataset provenance, normative label limitation, participant privacy.
- [ ] Pretrained feature source와 license.
- [ ] Known failure modes, cohort limits, compute footprint.
- [ ] Brain-only inference contract와 unavailable modalities.

## A21-4. Release package

- [ ] Code, configs, environment lock, manifests, splits, synthetic fixture, trained weights 또는 weight access rule, result tables와 figure source.
- [ ] 공개가 불가능한 artifact는 생성 recipe와 checksum을 제공한다.
- [ ] README에 exact reproduction order와 expected runtime/resource를 기록한다.
- [ ] DOI 가능한 archive에 versioned release를 만든다.

## A21-5. Internal review before submission

- [ ] 한 reviewer는 neuroscience claim과 causal wording만 검토한다.
- [ ] 한 reviewer는 ML leakage, control과 capacity parity를 검토한다.
- [ ] 한 reviewer는 statistics와 multiplicity를 검토한다.
- [ ] 한 reviewer는 figure만 보고 study logic을 설명해 본다.
- [ ] 저자 전원이 claim-to-evidence matrix와 failed gates를 확인한다.

## A21-6. Submission package

- [ ] Journal/venue scope에 맞춰 title, abstract length, main figure/table 수와 supplement를 조정한다.
- [ ] Cover letter에는 성능 benchmark가 아니라 brain–content relation의 learned formation, inheritance와 functional use를 contribution으로 명시한다.
- [ ] Reporting checklist, ethics/data-use statement, code/data availability와 conflicts를 준비한다.
- [ ] 최종 PDF의 모든 figure label, font, color contrast, caption과 cross-reference를 검수한다.

# Reviewer 질문 대비 목록

## 왜 34-D가 primary인가?

- [ ] 답변 근거: one-hot이 아닌 graded category-proportion profile이며 fine-grained stimulus relation을 보존한다.
- [ ] 방어 장치: 14-D, VA-2, VAD-3를 independent runs로 포함한다.
- [ ] 금지 답변: category theory가 dimensional theory보다 참이기 때문이다.

## 왜 brain-only inference인가?

- [ ] 답변 근거: training-time content가 brain representation에 무엇을 남기는지 검정하고 실제 test에서 privileged modality shortcut을 막기 위해서다.
- [ ] 예상 반례: brain-only 성능이 baseline을 넘지 못하면 mechanistic interpretation gate를 통과하지 못한다.

## 왜 V-JEPA 2와 caption을 모두 쓰는가?

- [ ] 답변 근거: natural video의 spatiotemporal content와 observer-described event/context라는 부분적으로 겹치는 두 view를 제공한다.
- [ ] Control: overlap diagnostic, nested Analysis 1, BV/BS/BVS ladder, mismatch.
- [ ] 금지 답변: 하나는 순수 visual, 하나는 순수 semantic이기 때문이다.

## 왜 AlexNet을 primary로 쓰지 않는가?

- [ ] 답변 근거: static object/appearance의 historical anchor는 되지만 video dynamics와 event structure를 충분히 담지 못한다.
- [ ] 위치: supplementary comparison.

## 왜 elementary visual feature를 넣는가?

- [ ] 답변 근거: complex content effect가 luminance/color/orientation/spatial-frequency/motion energy로 환원되는 대안 설명을 통제한다.
- [ ] depth 제외 이유: pretrained monocular depth의 semantic prior를 low-level로 해석하기 어렵다.

## 왜 ridge, PCA 또는 low-capacity probe처럼 단순한 방법을 쓰는가?

- [ ] 답변 근거: sample size가 제한된 fMRI에서 leakage와 overfitting을 줄이고 conditional contribution과 decodability를 반증 가능하게 만든다.
- [ ] 최신성 자체는 선택 기준이 아니다. 더 복잡한 model은 사전 기준에서 재현성 있는 out-of-sample gain과 해석상 필요를 보여야 한다.

## CKA가 mechanism을 보여주는가?

- [ ] 답변: 아니다. CKA는 동일 stimulus에 대한 global geometry summary다. Retrieval, mismatch, activation patching와 perturbation이 mechanism-related evidence를 제공한다.

## Activation patching이 neural causality인가?

- [ ] 답변: 아니다. Frozen trained model 내부의 computational dependence만 보여준다.

## Normative annotation으로 emotion decoding이라고 부를 수 있는가?

- [ ] 답변: participant emotion decoding이라고 부르지 않는다. Normative affect-profile readout이라고 명시한다.

# 완료 정의

연구는 다음 조건을 모두 만족할 때만 “완료”다.

- [ ] Data, participant, stimulus와 annotation provenance가 hash와 함께 확정되었다.
- [ ] Split, preprocessing, feature, target, architecture, loss와 inference가 outcome 전에 동결되었다.
- [ ] Analysis 1–3과 independent target 및 replication의 모든 preregistered result가 성공 여부와 관계없이 생성되었다.
- [ ] 모든 main claim이 claim-to-evidence matrix에서 실제 result와 gate에 연결되었다.
- [ ] 실패한 gate에 맞춰 wording과 conclusion이 낮춰졌다.
- [ ] Figure/table 숫자가 machine-readable result와 일치한다.
- [ ] End-to-end 또는 공개 가능한 reproduction pipeline이 clean environment에서 통과했다.
- [ ] Manuscript, supplement, code/data statement, model/data cards와 submission checklist가 완성되었다.
- [ ] 내부 neuroscience, ML, statistics와 visual-logic review가 완료되었다.

# 실행 기록 템플릿

새 action을 추가하거나 기존 action을 완료할 때 아래 필드를 복사한다.

- Action ID:
- 상태:
- 담당자:
- 시작일 / 완료일:
- 과학적 질문:
- 포함 이유:
- 배제하려는 대안 설명:
- 입력 artifact와 hash:
- 정확한 절차와 config:
- 예상 산출물:
- QA와 unit test:
- 통과 기준:
- 중단/격하 기준:
- 이 결과로 주장할 수 없는 것:
- 실제 결과 artifact:
- 판단:
- 결정 변경 여부와 새 근거:
