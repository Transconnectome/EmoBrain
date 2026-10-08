# EmoBrain pilot implementation handoff

_2026-10-08 · Server Claude Code and Codex · Implementation and exploratory development, not final results_

---

## 🎯 English — scope and purpose

The user reports that data are staged on Perlmutter and Horikawa distortion-correction comparison is in progress. **Build and test the analysis pipeline now; run small exploratory analyses on versioned development data.** Do not wait for all preprocessing to finish before writing code. This handoff does not launch jobs, choose the final preprocessing pipeline, or authorize a full study sweep.

The scientific question is what brain–visual–semantic relationships models learn and use, not simply which decoder scores highest. Analysis 1 tests correspondence with measured brain responses; Analysis 2 trains and examines the teacher/student; Analysis 3 evaluates affective readout and participant replication. Analyses 2 and 3 share trained models, rather than requiring separate architectures.

Authority: [00](00_README.md), [02 implementation specification](02_IMPLEMENTATION_SPEC.md), [04 decisions](04_DECISION_REGISTER.md), [06 neural validation](06_NEURAL_VALIDATION_AMENDMENT.md), [09 preprocessing](09_PREPROCESSING_HANDOFF.md), and current user decisions. This is an execution sequence, not a replacement scientific protocol. Joint B/V/S training remains the default; Brain-first → Joint is an optional later experiment. No new auxiliary latent-alignment loss is approved here.

Verified locally: branch documents and tracked code; the old entry points have documented incompatibilities in [08](08_IMPLEMENTATION_STATUS.md). Not verified here: current Perlmutter files, usable observations, feature availability, preprocessing quality, or successful real-data runs. Recheck server state rather than treating the old static audit as an up-to-date runtime report.

## 📋 English — assignments and first actions

Work only on `docs/unify-study-design-20261006`. Preserve active jobs, local changes, and all previous results. No main merge, force push, automatic stash, broad cleanup, new dated handoff folder, or large-data commit. Serialize git operations and shared-file edits under [coordination rules](../coordination/README.md).

### Ownership

These are proposed new implementation paths. Before writing, check for existing equivalent modules and active owners. Reuse existing code where appropriate; if this changes ownership paths, update the board with exclusive access first. Neither agent may revert the other's work.

- **Claude Code — data interface and audit:** `project/data/pilot_adapter.py`, `project/tests/test_pilot_adapter.py`, `project/output/audits/pilot_data/`. Codex reviews. Continue T002/T003 in their existing threads; do not silently settle duplicate/annotation policies.
- **Codex — pilot pipeline and tests:** `project/code/pilot_contracts.py`, `project/code/pilot/`, `project/scripts/run_pilot.py`, `project/tests/test_pilot_contracts.py`, `project/tests/test_pilot_pipeline.py`, `project/configs/pilot/`, `project/output/audits/pilot_code/`. Claude Code reviews.
- **GPT — design and integration:** this document and current design decisions. Report scientific choices instead of changing them as implementation conveniences.
- **Generated runs:** `project/output/pilot/<preprocessing-hash>/<experiment-id>/`. Agent-specific run IDs; never overwrite an earlier run. These outputs are ignored by git. Summarize reviewed findings and evidence references on the coordination board; do not assume ignored reports are accessible on other machines.

### First return, before real-data training

1. Record `git status`, branch, commit, active jobs, environment and existing implementations. Inspect first; update a clean checkout with `pull --ff-only` only during exclusive repository access.
2. Locate actual response arrays, row manifests, masks/voxel coordinates, atlas labels, captions, video features, affect codebook and reserved test IDs. Record paths, shapes, dtypes, versions/checksums, and missing dependencies. Never infer a row's stimulus identity from its array index.
3. Resolve observation → canonical content → annotation joins. Report unmatched and ambiguous rows; quarantine unresolved content groups for this pilot only, with an explicit exclusion manifest. This is not a permanent study exclusion or approval to average conflicting labels.
4. Audit the full manifest before selecting a small subset: connected run/content groups, cross-participant repeats, test clips repeated in training sessions, and near duplicates. If grouping leaves too few independent components, report the actual component sizes; do not quietly switch to random trial splitting.
5. Propose one bounded CPU pilot configuration with a wall-time/memory estimate. Real-data computation runs inside an appropriate scheduler allocation, not as a heavy login-node process. Show the command before any GPU or expanded job; full-scale training remains out of scope.

## 🔧 English — implementation sequence

### P0. Contracts and synthetic tests — start immediately

The supplied `project/code/pilot_contracts.py` is a small standard-library guard, not a working trainer. Run from the repository root:

```bash
python -m unittest project.tests.test_pilot_contracts -v
```

Map the audited full observation manifest to `Observation(row_id, content_id, run_id, run_group, preprocessing_id, reserved)`. `run_id` must include cohort/participant/session/run; `run_group` is a connected component computed upstream. The guard checks IDs, reserved-content propagation, cross-scope content/run overlap, and artifact fingerprints. It does not build the crosswalk, discover near duplicates, verify files, or prove that a trainer obeyed its declared dependencies.

Before each fit, call `validate_scopes` with every data-dependent fit/selection dependency. For an OOF teacher, its recipient observations are `evaluate_ids`; current inner-validation and outer-test observations are forbidden. Include scaler/PCA fitting, warm-up, early stopping and hyperparameter selection in the dependency ledger, not only gradient-training rows. Keep the full manifest available so an unselected reserved repeat cannot disappear from the audit.

Additional tests to implement: shuffled row-order joins; missing labels/masks; all-masked content; teacher stop-gradient; brain-only inference without content files; save/reload equality; final-test-label poisoning; separate target and preprocessing caches. Test 1b formulas on synthetic predictions with a common denominator, including negative signed components.

### P1. Data adapter and small linear baselines

Return an explicit batch with `observation_ids`, `content_ids`, `participant_ids`, brain voxel patterns/validity masks, targets/target masks, and optional V/S features. Keep teacher and student input interfaces separate. A block response is one spatial pattern per stimulus observation, not one scalar per ROI. Do not require Brain-JEPA, an LLM, or new foundation-model downloads.

For the first real-data run, use one available primary-cohort participant and a small, deterministically selected set of development run-components. Select by metadata, not scores. Use at least three independent components for fit/tuning/evaluation; if unavailable, run synthetic/loader tests only. One seed and one fixed outer pilot split are enough for engineering verification; they are not the final CV or inference design. Record counts after exclusions. Add a second participant/cohort only after this path works.

Implement training-only scaling and a regularized linear baseline, with tuning confined to pilot training groups. Compare with a training-mean predictor. No global PCA, ROI selection or target normalization before splitting. If ROI compression is needed, fit it within the training scope and preserve the voxel mapping. Match held-out rows and brain targets across model comparisons.

- **Analysis 1a pilot:** `L → B`, `[L,V] → B`, `[L,V,S] → B`, if all features are actually available. Without L, a V/S-only pilot tests plumbing but cannot claim an increment beyond low-level vision. Do not fabricate missing features or substitute model-generated captions.
- **Analysis 1b pilot:** `G`, `G+C`, `G+E`, `G+C+E → B`, with C=[V,S] and E=measured normative annotations. Save SSE and the common training-mean-reference denominator. Use the signed contrasts in [06 §3](06_NEURAL_VALIDATION_AMENDMENT.md); do not clip negative terms or call correlation differences explained variance.
- **Brain-only decoding pilot:** `B → affect` with a linear baseline and training-mean baseline. Run 34-D and 14-D independently when codebooks/joins are verified. A linear MSE benchmark is not the primary 34-D teacher/student objective. Report it as a benchmark, with output scale and any clipping explicitly recorded.

Keep initial outputs small: row-aligned predictions, per-participant/ROI descriptive scores, coverage/missingness, time and memory. No significance claim or anatomical conclusion from a single-participant pilot. If features are unavailable, complete the data adapter and brain-only path and report the missing feature artifact.

### P2. Small joint teacher and brain-only student

Encoder detail is now specified in [02 §3a–3c](02_IMPLEMENTATION_SPEC.md): train-only compression → Participant Map → Brain Encoder in both teacher and student, with separately fitted parameters. Compare a small MLP and ROI-token Transformer without externally pretrained brain weights. ROI-masked JEPA-style learning is an optional objective on the same Transformer, not the original Brain-JEPA or a required loss (D23). Frozen pretrained video/text encoders remain allowed. Multi-layer V-JEPA extraction and explicit low-level features follow D24/P08b; proposed numerical settings require pilot QA, not a full sweep.

Implement a configurable small model following [02 §4](02_IMPLEMENTATION_SPEC.md). Brain tokens query video/caption keys and values; a brain residual feeds the fused state and affect head. Participant maps are fitted transformations, not measured subjectivity. Video and sentence encoders stay frozen. Student forward input is brain only, during both training and inference. Expose named intermediate stages for later probes.

Start with a synthetic forward/backward pass, then a bounded real-data fit. The first target run can be CAT-34 for debugging convenience, not a scientific preference over 14-D. Confirm the independent 14-D path before claiming implementation complete. VA/VAD require verified dimensions and coding; do not invent a dominance label.

```text
34-D teacher: masked soft BCEWithLogits(teacher_logits, normative_proportions)
OOF guidance: sigmoid(teacher_logits), detached and scoped to recipient-excluded fits
34-D student: masked soft BCEWithLogits(student_logits, normative_proportions)
              + lambda * masked MSE(sigmoid(student_logits), OOF_probabilities)

14-D teacher/student: training-standardized MSE; independent models/transforms
14-D OOF: inverse each teacher's own scaling into original units,
          then apply the recipient student's training-only target scaling
```

Reduce losses over valid entries; log label and distillation terms separately. Missing labels are not zero targets. Fit/tune lambda using inner-development data only. These are the existing specification's objectives, not a new correlation-loss decision. Do not use softmax/KL on independent category proportions without a separately justified change.

Implement nested scopes explicitly:

```text
outer A/E = development-training / development-evaluation groups
for inner I/V within A:
    generate teacher OOF targets for I using only I
    for each recipient group R in I:
        fit/tune all teacher dependencies within I minus R
        predict R with the frozen teacher; never use V or E in fitting/selection
    train candidate student on I; select on brain-only V predictions
regenerate teacher OOF targets within A after selection
fit final pilot student on A; evaluate once on E
```

Teacher hyperparameter selection must itself exclude the OOF recipient. For a cheap smoke test, fixed declared hyperparameters can avoid an additional tuning loop; do not select them on recipient outcomes. Choose feasible pilot fold counts from component sizes, not a hard-coded final K. If nested fitting is infeasible, complete a synthetic OOF smoke test rather than relabeling in-sample predictions OOF.

Implement Direct and Full-guided first, then Shuffled-guided with V/S paired together and content pairings shuffled only within permitted training scopes. Teacher BVS/VS and brain-swap checks are required before attributing an effect to brain use. The complete matched controls remain in 02; this first run is not evidence they are unnecessary. A VS-guided student remains a claim-dependent decision, not silently added here.

### P3. Minimal After Training path, then expansion

Implement and smoke-test one frozen student stage, one visual probe and one semantic probe, fitted only on training groups. Evaluate retrieval against canonical-content-deduplicated held-out candidates; report candidate count, chance level, top-k and median rank. Calculate CKA only for matched held-out observations within a common reference fit; do not pool arbitrary OOF teacher coordinates. Probe success means recoverable information, not necessarily information used by the affect head.

Add a matched ROI/token perturbation and null perturbation to check changes in retrieval and affect readout. Record perturbation magnitude and missingness; this is model dependence, not biological causality. Test metadata alignment and selectivity before expanding ROI/layer sweeps.

Retain interfaces for affect-neighborhood retrieval (including affect-output-only control) and 2d content-side independent neural validation. Their D17/D18 evaluation choices are unresolved: implement synthetic boundary tests now, but do not rush them into this first real-data pilot. Keep the three-analysis study intact; staged implementation is not deletion of later analyses.

## 📦 English — rationale, outputs and data replacement

### Why these steps, rather than a full model sweep?

These are engineering checks implementing existing choices in 02/06, not new primary hypotheses.

1. **Question:** can the declared pipeline preserve stimulus identity and learn/evaluate on genuinely separated data? **Alternative:** apparent success is an ID join or split/cache error. **Basis:** current T002/T003 and 08 identify unresolved mappings and legacy-code differences. **Choice:** explicit contracts and synthetic failures are cheaper to diagnose than full training. **Change condition:** if an existing module passes the same checks, reuse it. **Limit:** passing does not validate neuroscientific claims.
2. **Question:** does the present brain/feature interface support any useful held-out prediction? **Alternative:** a complex model hides a broken loader, ineffective inputs or scaling problems. **Basis:** the linear benchmarks already specified in 02. **Choice:** a small linear pilot exposes these issues with limited compute. **Change condition:** inadequate independent groups or unverified joins block real-data scores, not synthetic development. **Limit:** a weak pilot does not prove absent brain information; a good pilot does not select final preprocessing.
3. **Question:** can output guidance, content probing and input-dependence tests be executed without leakage? **Alternative:** reported multimodal benefit is in-sample teacher fitting or direct content access by the student. **Basis:** existing 02/06 contracts. **Choice:** one-stage, bounded tests precede a full sweep. **Change condition:** repair failed contracts; consider Brain-first only as a recorded additional strategy. **Limit:** output distillation does not guarantee transfer of joint geometry.

### Required artifacts

Each pilot run saves config, code commit/dirty-state record, data/annotation/caption/feature hashes, preprocessing and mask versions, observation IDs and scope roles, split hash, fitted transforms, model checkpoint, predictions, losses/metrics, runtime and seed. OOF caches additionally record each recipient's teacher fit/selection IDs, checkpoint and transform hashes. Reject mismatched caches. Raw data and large arrays stay on the server.

Use `artifact_key` as a metadata fingerprint helper only; adapters must compute actual file hashes. Immutable preprocessing IDs must distinguish SDC variants and response estimator, spatial grid, atlas and mask changes. An unknown preprocessing version is a blocker for interpretable real-data output, not a reason to invent `v2`.

When corrected data arrive: preserve old pilot outputs; audit IDs/shapes/space again; rebuild affected brain arrays, masks, participant maps/PCA/scalers, encoding fits, all brain-dependent teacher/OOF/student artifacts, probes and brain-dependent scores. Reuse frozen V/S features and original annotations only if their content identities and extraction/annotation hashes are unchanged. Keep the same valid splits where possible; log unavoidable membership changes and use matched observations for any preprocessing comparison. Do not describe provisional uncorrected-versus-corrected differences as cohort replication.

Return one concise report with: verified data facts; implemented versus not implemented paths; tests with exact commands; descriptive pilot results; unresolved decisions; and the next bounded action. Do not fill absent results with expected outcomes.

## 🎯 한국어 — 범위와 목적

사용자 보고상 Perlmutter에 데이터가 준비됐고 Horikawa 왜곡 보정 비교가 진행 중이다. **지금 코드를 구현·검사하고, 버전을 명시한 개발 데이터로 작은 예비 분석을 진행한다.** 전처리 완료까지 구현을 미루지 않는다. 이 전달문은 job을 실행하거나 최종 전처리를 선택하거나 전체 실험을 승인하는 문서가 아니다.

목적은 최고 decoding 성능이 아니라 모델이 뇌–시각–상황 의미 관계를 무엇으로 학습하고 사용하는지 확인하는 것이다. 분석 1은 실제 뇌 대응, 분석 2는 teacher/student 학습 및 내부 표상·사용, 분석 3은 동일 모델의 정서 readout과 참가자 재현이다. 분석 2·3 때문에 서로 다른 architecture를 만들지 않는다.

최신 사용자 결정과 00·02·04·06·09 문서를 따른다. 본 문서는 실행 순서이며 연구 기준을 대체하지 않는다. Joint B/V/S가 기본, Brain-first → Joint는 선택적 추가 실험이고 latent alignment 보조 loss는 승인되지 않았다. 여기서 확인한 것은 저장소 문서·코드이며 서버의 파일·품질·사용 가능한 표본·실행 성공은 아직 직접 확인하지 않았다. 08의 예전 정적 감사와 현재 서버 상태를 대조한다.

## 📋 한국어 — 역할과 먼저 할 일

`docs/unify-study-design-20261006`에서만 작업한다. 실행 중 job·미커밋 변경·기존 결과를 보존한다. main 병합, force push, 자동 stash, 광범위 정리, 날짜별 전달본 복제, 큰 데이터 커밋은 하지 않는다. 공유 파일 편집과 git 조작은 직렬화한다.

### 담당과 수정 경로

영문 Ownership의 경로 목록을 공통 소유권 원본으로 사용한다. Claude Code는 `pilot_adapter.py`와 해당 검사·데이터 감사, Codex는 계약 코드·pilot 모델/실행기/설정/테스트·코드 감사를 맡고 서로 검토한다. GPT는 설계·통합을 맡는다. 새 파일을 만들기 전 동등한 기존 구현과 활성 담당자를 확인하고, 재사용으로 경로가 달라지면 작업판을 먼저 갱신한다. 서로의 변경을 되돌리지 않는다.

산출물은 `project/output/pilot/<preprocessing-hash>/<experiment-id>/`, 감사는 담당별 `project/output/audits/pilot_data/`와 `pilot_code/`에 둔다. 이전 run을 덮어쓰지 않는다. ignored 산출물이 다른 컴퓨터에 자동 공유된다고 가정하지 말고 검토 요약·근거 경로를 작업판에 남긴다. T002/T003은 기존 스레드에서 이어간다.

### 실제 학습 전 첫 반환물

1. 브랜치·커밋·dirty 상태·job·환경·기존 구현을 확인한다. clean하고 독점 접근할 때만 `pull --ff-only`로 갱신한다.
2. 실제 brain 배열·행 manifest·mask/voxel 좌표·atlas·caption·영상 feature·정서 codebook·예약 test ID의 경로, shape, dtype, 버전/hash와 누락을 기록한다. 배열 순번으로 자극을 추측하지 않는다.
3. observation → canonical content → annotation 연결을 검사한다. 충돌/누락 그룹은 이유를 기록해 pilot에서만 격리하고 영구 제외나 평정 평균 정책을 임의 결정하지 않는다.
4. 작은 subset을 고르기 전에 전체 manifest의 run/content 연결 성분, 참가자 간 반복, training session에 들어 있는 test clip, near duplicate를 검사한다. 독립 성분이 부족하면 크기를 보고하고 무작위 trial split으로 바꾸지 않는다.
5. CPU 소규모 설정 하나와 시간·메모리 예상량을 반환한다. 실제 계산은 적절한 scheduler allocation에서 하며 login node에 무거운 작업을 올리지 않는다. GPU·확대 job 전 실행 명령을 제시한다. 전체 학습은 아직 범위 밖이다.

## 🔧 한국어 — 구현 순서

### P0. 계약과 synthetic test: 바로 시작

제공된 `project/code/pilot_contracts.py`는 표준 라이브러리로 작동하는 안전 검사이며 trainer가 아니다. 저장소 루트에서 `python -m unittest project.tests.test_pilot_contracts -v`로 검사한다.

전체 observation manifest를 `Observation`의 여섯 필드로 연결한다. `run_id`는 cohort/participant/session/run을 모두 포함하고, `run_group`은 사전에 계산·검토한 연결 성분이다. 코드는 ID 중복, 예약 자극의 다른 회차 포함, scope 사이 content/run 누출, 산출물 fingerprint를 검사한다. Crosswalk 생성, near duplicate 발견, 실제 파일 검증, 학습 코드가 선언한 scope를 지켰는지는 별도 검사해야 한다.

`validate_scopes`에 scaler·PCA·warm-up·early stopping·hyperparameter 선택까지 포함한 fit 의존성을 넣는다. OOF teacher의 예측 대상은 evaluate, 현재 inner-validation과 outer-test는 forbidden이다. 선택하지 않은 예약 회차가 검사에서 사라지지 않도록 전체 manifest를 유지한다.

추가 테스트: 행 순서 변경 후 join 보존, 누락 label/mask, content 전체 masking, teacher gradient 차단, content 파일 없는 brain-only 추론, checkpoint 재로딩 일치, 최종 test label 변경이 학습에 영향을 주지 않는지, target/전처리별 cache 분리. 1b 공통 분모·음수 대비도 synthetic prediction으로 검사한다.

### P1. 데이터 어댑터와 작은 선형 기준모델

Batch는 observation/content/participant ID, brain voxel pattern과 유효 mask, target과 mask, 선택적 V/S feature를 명시적으로 반환한다. Teacher와 student 입력 interface를 분리한다. 자극당 block 반응은 공간 패턴이며 ROI당 scalar 평균으로 대체하지 않는다. Brain-JEPA·LLM·새 foundation model 다운로드는 필요 없다.

첫 실제 실행은 주 cohort에서 가능한 참가자 1명, metadata로 결정한 소수의 개발 run-component, seed 1개, 고정 pilot outer split 1개로 시작한다. 이는 본실험 CV 확정이 아니다. 학습/튜닝/평가에 최소 3개의 독립 성분이 없으면 synthetic/loader 검사까지만 한다. 제외 후 표본 수를 기록하고 작동 확인 후 다른 참가자·cohort로 넓힌다.

Training-only scaling과 regularized linear baseline, training-mean baseline을 구현한다. Tuning은 pilot 학습 그룹 안에서 한다. 전체 데이터 PCA·ROI 선택·target 정규화는 하지 않는다. ROI 압축이 필요하면 training 안에서 fit하고 voxel mapping을 보존한다. 비교 모델의 평가 행·뇌 target을 맞춘다.

- **1a:** feature가 있으면 L, [L,V], [L,V,S] → B. L이 없으면 V/S pilot은 코드 연결 검사일 뿐 저수준 시각 정보 이상의 설명력 검정이 아니다. 없는 feature를 꾸미거나 생성 caption으로 대체하지 않는다.
- **1b:** G, G+C, G+E, G+C+E → B. C=[V,S], E는 실제 normative annotation이다. SSE·training-mean 공통 분모와 06의 signed contrast를 저장한다. 음수를 자르거나 상관 차이를 설명 분산이라고 부르지 않는다.
- **Brain-only:** B → affect 선형 모델과 평균 예측. Codebook/join 확인 후 34-D와 14-D를 독립 실행한다. 선형 MSE 기준모델은 34-D teacher/student의 주 loss와 다른 benchmark이며 scale/clipping을 기록한다.

최초 산출물은 행별 prediction, 참가자/ROI별 기술 점수, coverage/missingness, 시간·메모리다. 참가자 1명 pilot으로 유의성·해부학 결론을 내리지 않는다. Feature가 없으면 어댑터와 brain-only부터 끝내고 부족한 artifact를 보고한다.

### P2. 작은 joint teacher와 brain-only student

Encoder 상세는 [02 §3a–3c](02_IMPLEMENTATION_SPEC.md)에 있다. Teacher와 student 모두 train-only compression → Participant Map → Brain Encoder를 사용하고 parameter는 따로 학습한다. 외부 사전학습 brain weight 없이 작은 MLP와 ROI-token Transformer를 비교한다. ROI-masked JEPA-style은 같은 Transformer에 붙이는 선택적 목적함수이며 원형 Brain-JEPA나 필수 loss가 아니다(D23). Frozen pretrained video/text encoder는 유지한다. 다층 V-JEPA 추출·명시적 저수준 특징은 D24/P08b를 따르고, 제안한 숫자는 pilot QA를 거친다. 전체 sweep을 요구하지 않는다.

02 §4에 따라 brain query와 video/caption key/value, brain residual, fused state와 affect head를 구현한다. Participant map은 학습되는 변환이지 측정된 개인 주관성이 아니다. Video/sentence encoder는 frozen, student는 학습·추론 모두 brain-only다. 후속 probe를 위해 stage별 표상을 반환한다.

Synthetic forward/backward 후 제한된 실제 fit을 한다. 디버깅을 CAT-34부터 시작할 수 있지만 이는 이론적 우선순위가 아니며 14-D 독립 경로까지 확인해야 구현 완료다. VA/VAD는 실제 차원·coding을 확인하고 dominance label을 만들어 넣지 않는다.

34-D teacher는 masked soft BCEWithLogits, student는 동일 label loss + λ×OOF probability MSE다. Teacher sigmoid 출력은 detach하고 label·distillation loss를 각각 기록한다. 유효 entry만 평균하며 missing을 0 target으로 처리하지 않는다. 14-D는 training-standardized MSE로 별도 학습한다. OOF teacher마다 자신의 scaler로 원척도로 복원한 후 student training scaler로 변환한다. λ는 inner-development에서 고른다. 기존 명세를 유지하며 correlation loss나 softmax/KL로 임의 교체하지 않는다.

Nested OOF는 영문 pseudocode를 따른다. Outer A/E 안의 inner I/V에서 I의 OOF를 만들 때 V와 E는 teacher fit/선택에 쓰지 않는다. I의 recipient R을 제외한 I\R 안에서만 teacher 및 모든 transform·hyperparameter를 fit한다. Student를 I에서 학습해 V로 선택하고, 선택 후 A 안에서 OOF를 다시 만들어 A로 최종 pilot student를 fit하고 E에서 평가한다. 저비용 smoke에서는 사전에 선언한 고정 hyperparameter로 tuning loop를 줄일 수 있지만 recipient 결과로 고르지 않는다. Fold 수는 실제 성분 수에 맞춘 pilot 설정이며 최종 K가 아니다. 불가능하면 synthetic OOF까지만 하고 in-sample 출력을 OOF라고 부르지 않는다.

Direct·Full-guided를 먼저 연결한 뒤 허용 training scope 안에서 V/S를 함께 잘못 짝짓는 Shuffled-guided를 추가한다. 뇌 사용에 이득을 귀속하기 전 BVS/VS·brain-swap 검사를 한다. 전체 matched controls는 02에 유지된다. VS-guided student는 주장 의존적 결정으로 남기며 여기서 자동 추가하지 않는다.

### P3. 최소 After Training 경로와 후속 확장

Frozen student stage 하나에서 training-only visual/semantic probe를 학습한다. Canonical content 중복을 제거한 held-out 후보에서 retrieval의 후보 수·chance·top-k·median rank를 보고한다. CKA는 같은 held-out 관측과 같은 reference fit 안에서 계산하고 서로 다른 OOF teacher 좌표를 합치지 않는다. Probe 성공은 읽을 수 있다는 뜻이며 affect head가 사용했다는 뜻은 아니다.

ROI/token perturbation과 크기를 맞춘 null을 넣어 retrieval·affect readout 변화, perturbation 크기와 missingness를 기록한다. 모델 의존성이지 생물학적 인과성은 아니다. Metadata 정렬·선택성 검사를 먼저 하고 ROI/layer 대규모 sweep은 미룬다.

Affect-neighborhood retrieval(+affect-output-only control)과 2d 독립 뇌 검증 interface는 남긴다. D17/D18의 평가 세부가 미정이므로 지금은 synthetic 경계 검사를 준비하고 첫 실제 pilot에 서둘러 넣지 않는다. 단계적 구현이지 세 분석이나 후속 분석을 삭제하는 것이 아니다.

## 📦 한국어 — 근거, 산출물, 데이터 교체

### 이 순서의 이유

새 primary 가설이 아니라 02/06의 기존 설계를 구현하는 공학적 검사다.

1. **질문:** 자극 정체성과 학습/평가 분리가 유지되는가? **대안 설명:** join·split·cache 오류가 성능을 만든다. **근거:** T002/T003과 08의 미결 매핑·구현 차이. **선택 이유:** 전체 학습보다 계약·synthetic 실패를 진단하기 쉽다. **변경 조건:** 기존 코드가 같은 검사를 통과하면 재사용한다. **한계:** 통과가 neuroscience 주장을 검증하지 않는다.
2. **질문:** 현재 brain/feature interface로 held-out 예측이 가능한가? **대안 설명:** 복잡한 모델이 loader·입력·scale 문제를 가린다. **근거:** 02의 선형 기준모델. **선택 이유:** 작은 계산으로 문제를 드러낸다. **변경 조건:** 독립 성분·join이 불충분하면 실제 점수는 보류하고 synthetic 작업을 진행한다. **한계:** 낮은 성능이 뇌 정보 부재를, 높은 성능이 최종 전처리 선택을 뜻하지 않는다.
3. **질문:** output guidance·내용 probe·입력 의존성 검사를 누출 없이 수행하는가? **대안 설명:** in-sample teacher나 student의 직접 content 접근이 이득을 만든다. **근거:** 02/06의 계약. **선택 이유:** 전체 sweep 전 최소 경로를 검증한다. **변경 조건:** 계약 실패를 고치고 Brain-first는 기록된 추가 전략으로 검토한다. **한계:** output distillation이 joint geometry 전달을 보장하지 않는다.

### 저장과 교체

Run마다 config, 코드 commit/dirty 상태, 데이터·annotation·caption·feature hash, preprocessing/mask 버전, observation ID와 scope, split hash, fitted transform, checkpoint, predictions, losses/metrics, 실행 시간과 seed를 저장한다. OOF는 recipient별 teacher fit/선택 ID·checkpoint·transform hash까지 기록한다. 불일치 cache는 거부한다. 원자료·큰 배열은 서버에 남긴다.

`artifact_key`는 metadata fingerprint일 뿐 파일 checksum을 직접 계산하지 않는다. 어댑터에서 실제 hash를 계산한다. 전처리 ID는 SDC·response estimator·공간 grid·atlas·mask 변경을 구별해야 한다. 버전이 불명확하면 실제 결과 해석을 멈추고 확인하며 `v2`를 임의로 붙이지 않는다.

보정 데이터 도착 후 이전 결과를 보존하고 ID/shape/space를 재검사한다. 영향받은 brain 배열·mask·PCA/map/scaler·encoding·brain-dependent teacher/OOF/student·probe·점수를 재생성한다. Frozen V/S와 원 annotation은 content 정체성 및 추출/annotation hash가 같을 때만 재사용한다. 가능한 split을 유지하고 표본 변경은 기록한다. 전처리 비교에는 공통 관측을 사용하며 보정 전후 차이를 cohort 재현으로 부르지 않는다.

반환 보고서는 확인한 데이터 사실, 구현/미구현 경로, 검사 명령·결과, 기술적 pilot 결과, 미결 결정, 다음 제한된 작업 순서로 작성한다. 실행하지 않은 결과를 예상값으로 채우지 않는다.

## ✍️ Copy-paste prompts / 전달용 프롬프트

### Claude Code

```text
EmoBrain의 소규모 개발 단계부터 진행해줘. AGENTS.md → docs/coordination/BOARD.md
→ docs/current/10_PILOT_IMPLEMENTATION_HANDOFF.md를 읽고 연결된 현재 명세를 확인해.
너는 데이터 어댑터·manifest·ID/annotation join·개발 subset 감사 담당이야.
먼저 서버 현황과 기존 코드를 확인하고, 문서의 소유 경로에서만 작업해.
T002/T003의 미결 정책을 임의 확정하지 말고 모호한 그룹을 보고해.
현재 데이터 버전을 명시하고 reserved content를 전체 manifest에서 확인해.
P0와 P1 데이터 interface부터 구현·검사하고 Codex가 쓸 batch 계약을 반환해.
새 전처리 실행이나 전체 GPU 학습은 시작하지 마. Codex 구현은 별도로 검토하되
같은 파일을 동시에 고치지 마. 근거 경로·테스트·다음 작업을 짧게 보고해.
```

### Codex

```text
AGENTS.md → docs/coordination/BOARD.md → docs/current/10_PILOT_IMPLEMENTATION_HANDOFF.md
순서로 읽고 현재 명세에 맞는 pilot pipeline을 구현해줘.
너는 split/OOF 계약, 기준모델, 작은 teacher/student, 사후 분석 interface와 테스트 담당이야.
기존 구현을 먼저 확인하고, 제공된 test_pilot_contracts부터 실행해.
Claude Code의 데이터 어댑터를 기다리는 동안 synthetic batch로 P0/P2 경계를 구현해.
데이터 join·split 검사를 통과하면 P1의 bounded CPU baseline부터 진행할 설정을 제시해.
Teacher/student 전체 sweep이 아니라 한 경로의 정확성·재현성과 저장을 확인하는 게 목표야.
Student는 학습·추론 모두 brain-only, guidance는 nested OOF, Joint 학습이 기본이야.
14-D와 34-D는 별도 모델·cache로 지원하고 현재 loss 계약을 임의 교체하지 마.
전처리 교체 시 뇌 관련 fitted artifact가 재생성되게 해줘. 실행하지 않은 결과는 쓰지 마.
공유 git 조작은 직렬화하고 main·진행 중 전처리·타인 파일은 건드리지 마.
```
