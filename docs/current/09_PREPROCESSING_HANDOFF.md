# EmoBrain preprocessing review and server-AI handoff

_2026-10-07 · Review of reported evidence; not a server execution report or final preprocessing freeze_

[English](#english) · [한국어](#한국어)

## English

### 1. Read this first: purpose, authority and immediate recommendation

This is a self-contained preprocessing handoff for the AIs working on the EmoBrain server. It supplements [07_RESPONSE_ESTIMATION_REVIEW.md](07_RESPONSE_ESTIMATION_REVIEW.md), not a replacement study protocol. Read [00_README.md](00_README.md) and [AGENTS.md](../../AGENTS.md) for authority and execution rules. Current user decisions and an approved freeze take precedence; recommendations below are not automatically approved settings. D04 and the ROI-specific details of D19 remain unresolved.

**Recommendation: preserve v2, complete the targeted audits, and reprocess only the affected stages once the evidence and decision rules justify it. Do not discard v2 or launch a guessed-PE whole-cohort rerun by default.** Existing authorized jobs are not cancelled or expanded by this document. Inspect their status before acting. New costly jobs and any destructive replacement require the applicable user approval.

Work on `docs/unify-study-design-20261006`; do not merge main or create a PR. Preserve server changes, previous outputs and failed runs. Use Git history for document revisions, not dated copies of current documents. Server audit artifacts belong together under `project/output/audits/`; existing data/audit folders may remain where they are and be linked rather than copied.

#### Research context that must guide preprocessing

- EmoBrain is a neuroscience study of brain–visual–semantic relationships, not only an affect-decoding benchmark.
- Primary: MindCaptioning/Horikawa 2025 video-viewing fMRI, original videos and human captions. Replication: Horikawa 2020. Imagery is out of scope. Shared stimuli across cohorts do not establish generalization to a new stimulus distribution.
- Analysis 1: sensory–semantic encoding of brain responses and shared/conditional predictive relationships with normative affect profiles.
- Analysis 2: joint Brain + Video + Caption teacher, output-guided brain-only student, followed by geometry, content probes, ROI/token dependence and independent neural validation. Geometry similarity or prediction success alone does not establish learned content use.
- Analysis 3: affect readout and cohort replication. 34-D, 14-D and available VA/VAD targets use independent model runs, not joint target learning. Targets are stimulus-level crowdsourced annotations, not scanned participants' self-reports.
- Primary input interface: **one voxel-pattern vector per presentation per participant**. Temporal block averaging is not ROI spatial averaging. Retain within-ROI voxel patterns, individual observations and repeats; ROI PCA/projectors are fitted in the appropriate training scope.
- ROI quality matters for interpretation: weak OFC decoding cannot be translated into weak biological involvement. Participant maps and larger brain weights cannot recover unmeasured BOLD information.

### 2. Evidence status and the two AI reports

**What this review actually inspected:** two user-supplied reports, subsequent Claude Code/Codex replies, current repository design documents and the methodological sources in §10. It did not independently open server NIfTI files, TSVs, QC panels, code or Slurm logs. Server-report numbers below are reported observations, not independently reproduced measurements by the coordinating assistant.

Source labels:

- **R1:** “EmoBrain OFC 집중 품질검사 — 2026-10-07.” Reports T1w availability for all 11 participants, 725 runs, 8,700 run × OFC-parcel measurements, and temporal QC on 33 runs. Twelve parcels with `_OFC_` in their names; not the complete anatomical OFC/vmPFC.
- **R2:** “EmoBrain 전처리 전체 정리 (검토 요청용, 2026-10-07).” Reports fMRIPrep/postprocessing configuration and proposed mask/SDC checks. Its OFC summary uses 11 Limbic OFC parcels, unlike R1's 12-parcel set including one Control parcel.
- **R3:** Subsequent Claude Code reply. Contains useful separation of low signal and mask restriction, but overstates spatial certainty and extrapolates MindCaptioning displacement to Horikawa.
- **R4:** Subsequent Codex reply. Correctly separates low signal, mask restriction and localization uncertainty. Newly mentions remaining motion concerns including Horikawa 05; supporting run/block metrics have not been supplied here.

| Claim | Evidence status and required interpretation |
| --- | --- |
| 6 × 70 MindCaptioning runs + 5 × 61 Horikawa runs = 725 | Internally consistent reported totals. Verify manifest and viewing-task restriction on server. |
| T1w exists for all 11 participants | Reported in R1 with paths. T1w availability is not proof of successful SDC or local alignment. |
| OFC coverage is about 41–67% MC and 48–82% HK | R2's **11-parcel** ranges. R1's **12-parcel** ranges are 44.4–68.8% and 49.7–82.9%. Do not combine without parcel IDs and denominators. |
| HK02 individual-run OFC coverage 68.3–93.3%, common coverage 49.7% | R1; supports additional intersection-mask restriction, not proof that all excluded voxels are usable. |
| Relaxing the mask adds 5–9 percentage points | Summary claim requiring participant-wise paired recomputation. Range endpoints do not establish paired gains. |
| Newly included voxels have half the SNR | R2 preliminary **tSNR** result from HK01, one run (e.g. OFC 20.9 versus 9.9). Not an 11-participant conclusion and not half the neural information. |
| Horikawa Limbic regions are displaced by approximately 5 mm, visual regions by approximately 1 mm | **Not established.** R2's displacement measurements are from MindCaptioning; they cannot supply Horikawa displacement estimates. Distinguish median, percentile and mean. |
| Fieldmap correction is present, therefore MindCaptioning has no spatial problem | Unsupported. Reported SDC application does not certify the fieldmap association, correction quality or low-signal local registration. |
| Everything outside OFC/temporal pole is fine | Unsupported. Computational reproducibility is not complete motion, spatial, tissue or task-signal validation. |
| New v2 independent recomputation matches saved arrays | Reported strong arithmetic QA. It verifies computation under the chosen definition, not that the definition is optimal or scientifically sufficient. |

Where the reports differ, request the underlying table and calculation, not a vote between AIs. Replace “no issues” with the specific test, scope and pass criterion.

### 3. Reported current pipeline: preserve as baseline, do not silently redefine

| Stage | Reported configuration |
| --- | --- |
| Acquisition | MC TR 1 s, TE 30 ms; HK TR 2 s, TE 43 ms; both 2 mm. Acquisition differences remain even with common code. |
| fMRIPrep | 25.0.0, participant T1w-space output. MC has session phase-difference fieldmaps, reportedly applied to 420/420 runs. HK has no SDC in the present derivatives and lacks reported PE metadata. |
| HK reuse | Second T1w-output execution reuses derivatives from first MNI-output execution. Matching motion parameters is necessary evidence but insufficient to verify the complete applied transform chain. |
| Initial volumes | MC removes first 8 s before regression; reported NSS volumes fall inside it. HK retains initial volumes and adds NSS spike regressors where present. Different handling is not automatically an error; audit rationale and time origin. |
| `common36` | Motion 24 + CSF/WM/GM mean signals with four expansions each; plus intercept, linear trend and applicable NSS columns. GM mean uses GM probability ≥0.5 intersected with analysis mask. |
| Response | Reported 4 s lag; iterative ±3 SD clipping, up to 10 iterations; mean over actual presentation block including the specified following rest. Participant-specific event-duration conventions are handled explicitly. |
| Normalization | Voxel-wise z-score across block responses within each run; pre-runz block values also saved. Block-wise and volume-wise run z-scoring are not interchangeable. |
| Mask | Participant-specific intersection of all run brain masks and variable-voxel checks; this is not an intersection across all participants. |
| Atlas | Reported 469-label composite: Schaefer400 + Tian S3 + hypothalamus/BNST + cerebellum + brainstem. Actual label accounting, transforms and conflicts require verification. |
| Auxiliary time series | Nuisance-processed/lagged stream with 0.01–0.1 Hz filtering, temporal Gaussian FWHM 4 s, run z-score and slicing. Not the sole time-series preservation format. |

R2 reports 2,540 MC observations per participant (2,180 + 72 × 5) and 2,196 HK observations per participant, totaling 26,220. These are observations, not necessarily unique training stimuli. MC training-session observations of final-test stimuli and HK duplicate-content pairs require canonical-ID split handling.

### 4. Four requested decisions

#### 4.1 Intersection mask versus 90% coverage

**Provisional recommendation:** preserve the current intersection as the reference derivative; do not promote a 90% mask to primary from the one-run tSNR result or voxel count alone.

1. Identify whether exclusions are driven by a few failed masks/runs, stable low signal, field-of-view boundaries, registration or variable-voxel rules. Correct identified upstream failures before blanket relaxation.
2. Complete the planned multi-participant/multi-run QC. Sample sessions and quality ranges transparently; distinguish systematic sampling from deliberately selected worst cases.
3. For each added voxel/ROI, report spatial location, run-validity fraction, raw steady-state mean signal, tSNR definition, motion context and the participant/run distribution. Do not import a universal tSNR pass threshold across acquisitions.
4. Define how a 90%-eligible voxel is handled in its invalid runs. An fMRIPrep-mask-external nonzero value is not proof of useful brain measurement. Do not silently zero-fill and treat the value as observed activity.
5. A fixed ROI token identity does not solve changing within-ROI voxel support. Missingness must be explicit; assess whether it becomes a run/session shortcut. Train-only PCA must have a coherent feature space.
6. **Separate two effects:** changing the analysis mask also changes the GM mean used in regression. First compare masks with nuisance definition held fixed where feasible, then document the end-to-end candidate. Otherwise attribute differences to the combined preprocessing change, not mask expansion alone.
7. Record which runs define the mask, including evaluation runs. Anatomical acquisition QC is not automatically label leakage, but all-run adaptation must be disclosed and must not be represented as an unseen-run, training-defined transform. Any data-dependent threshold selection needs a defined development scope.

Adopt relaxation only if supported voxels are genuinely usable, invalid-run handling is coherent and relevant downstream conclusions are stable under the documented comparison. Neither maximal coverage nor maximal tSNR is the scientific objective.

#### 4.2 Small OFC parcels: missingness versus pooling

- Keep original parcel identities and coverage/validity masks. Empty parcels are missing observations, not zero neural responses.
- `<10 voxels OR <20% coverage` is a draft technical flag, not a biological validity threshold. A passing parcel may still have poor alignment or signal. Define counts before/after masking, PCA rank feasibility and spatial support.
- Do not merge different surviving parcels per participant just to pass a count threshold.
- An anatomically fixed, same-hemisphere OFC super-ROI may be a supplementary alternative after the pooling map is specified identically across participants. Pooling changes the question and cannot reconstruct absent subregions. Keep voxel patterns when the question concerns multivoxel representation.
- Schaefer “Limbic” is a cortical network label, not every limbic structure. Audit amygdala, hypothalamus, BNST and other small subcortical targets separately. The 12 `_OFC_` labels do not exhaust anatomical OFC/vmPFC.

#### 4.3 Horikawa SDC and unknown phase encoding

**Neither “ignore it with one sentence” nor “guess PE and rerun all five” is an adequate default.**

1. Recover acquisition evidence first: DICOM/conversion records, inherited BIDS metadata, protocol files, original preprocessing configuration and, if necessary, a user-authorized author inquiry. Do not send external messages without approval.
2. Distinguish image-axis designation, physical orientation and PE polarity; document NIfTI orientation. “Try two directions” is underspecified if even the axis is unknown.
3. Check the exact container and SDCFlows requirements, including any readout-time requirements. `--use-syn-sdc warn` can permit execution without performing SDC when metadata is missing; completion is not proof of correction. Do not invent measured metadata in raw BIDS. An inferred candidate belongs in a separate, documented derivative/configuration.
4. If evidence supports a candidate, propose a limited pilot such as HK01/02 with explicitly identified development runs and computational cost. Whole-cohort rerun waits for review of that evidence.
5. Evaluate anatomical boundaries in usable-signal regions, constrained warp plausibility/Jacobians, regional displacement, other-region degradation, coverage and changes in response patterns. Improved T1 similarity alone is insufficient because it is part of the registration objective. Separate signal absence from displacement.
6. Audit whether reuse actually recomputes SDC-dependent BOLD reference, BOLD-to-T1 alignment, resampling, masks and confounds; do not inadvertently reuse stale uncorrected functional products. Reusable anatomy need not automatically be recomputed.

The ongoing MC SDC-on/off comparison is useful as a **within-MC sensitivity experiment**. It cannot estimate HK displacement or validate an assumed HK PE direction. Fieldmap-based MC is a measured-field reference, not error-free ground truth. Verify fieldmap/run association and whether reported millimeters represent the nonlinear SDC component rather than a total transform. Compare on a common evaluation support as well as native candidate masks; otherwise changed sampling and changed signal are mixed.

If PE cannot be established and a candidate cannot be justified, retain the uncorrected baseline with explicit regional localization limits rather than manufacture certainty. If a supported pilot shows reliable benefit without unacceptable distortion elsewhere, propose reprocessing the affected HK functional stages and downstream products; retain both versions and invalidate incompatible caches.

#### 4.4 Interpretation across cohorts

- Low signal, additional masking and localization uncertainty are separate mechanisms with separate remedies.
- Do not currently anchor the headline on fine-grained OFC/temporal-pole localization, their relative importance versus visual cortex, or between-cohort regional ranking.
- Valid regional data can still contribute to models, with coverage/reliability limitations reported. Blanket deletion of the entire OFC or all “Limbic” structures is not required by these reports.
- A low/absent effect in poorly measured tissue is not evidence of biological irrelevance. A positive result also requires localization and artifact checks.
- Acquisition/SDC differences remain potential confounds; common downstream code does not remove them. A regional failure does not automatically invalidate the whole three-analysis study.

### 5. Additional EmoBrain-specific issues beyond OFC

#### 5.1 GM mean regression and ROI interpretation

The MC paper explicitly reports motion 24 and CSF/WM/GM expansions [1]. `common36` therefore has a published rationale; do not call it an implementation mistake simply because it includes GM regression. It is not, however, an exact reproduction of HK2020 or proof of optimality for EmoBrain.

Broad GM signal can contain both nuisance and neural/task-related components. Removing it changes the available response patterns. Furthermore, an ROI residual calculated using a whole-GM time series depends computationally on measurements outside that ROI. This is **not itself target leakage**, but it limits a strict “visual cortex measurements alone suffice” interpretation and affects ROI-increment/reliance claims.

**Recommended development sensitivity, not a newly frozen primary:** compare `common36` with the same pipeline omitting only the four GM-derived columns (24 motion + 8 CSF/WM expansions, plus intercept/trend/NSS as applicable). Preserve masks, timing and other processing to isolate this choice. Start with limited linear encoding/readout and preprocessing diagnostics rather than duplicating all teacher/student runs. Non-GM regression is not automatically ground truth or guaranteed improvement. Do not re-regress already residualized outputs; restart from the appropriate pre-regression BOLD. Freeze the exact GM definition and report how much variance it removes and its relation to run/task/nuisance structure.

For model ROI perturbations, hold preprocessing fixed and describe dependence on the processed ROI input. Recomputing global regression after every ROI perturbation changes many regions at once and answers a different question.

#### 5.2 Time-series preservation

Preserve fMRIPrep continuous BOLD, events, confounds, actual time coordinates, censor/NSS information and the ability to regenerate an unsmoothed/non-bandpassed downstream series. Existing filtered slices may remain as optional derivatives. They should not be the only preserved source for future duration-aware GLMs or temporal analyses. Noncausal filtering/temporal smoothing mix neighboring times; do not present such slices as independent temporal observations or evidence of psychological processing order. No new temporal model is authorized here.

#### 5.3 Motion, clipping and timing QA

- Mean FD 0.10–0.20 mm does not certify all volumes/blocks. Report FD/DVARS distributions, peaks, affected-volume fractions under stated candidate rules, and block-wise summaries, particularly the new HK05 concern. Its magnitude remains unverified in this handoff.
- Iterative ±3 SD clipping is not motion censoring. Record modified voxel-volume fractions, affected blocks/ROIs, iteration counts and convergence. A clipping sensitivity is a diagnostic candidate if changes are extensive, not a mandatory full experiment grid.
- Verify time origins after deletion and slice-time correction, 4 s lag direction, rest inclusion, actual presentation versus original clip duration and run-end truncation. fMRIPrep 25.0.0 describes middle-TR slice alignment [2]; audit the actual configuration rather than automatically adding another offset. Full-run volume count and broad occipital latency checks do not alone certify each response window.
- For regression, record design column names, scaling, numerical rank/tolerance, residual degrees of freedom and projection checks. Retaining column names does not imply linear independence; valid rank reduction is not the same as the earlier scaling bug. Save independent-reference comparison evidence.
- Reconcile the one constant-voxel/zero-fill exception with the stated all-runs-variable mask rule, including its final inclusion and validity flag. Do not infer that one boundary voxel invalidates the whole dataset.

#### 5.4 Atlas, normalization and leakage boundaries

- Verify composite label IDs, overlaps/priority, transforms, surface-to-volume mapping and appropriate categorical resampling; avoid treating interpolated label numbers as labels. Confirm all intended ROIs and outside-atlas voxels are accounted for.
- MC training-session observations of final-test clips must be excluded from fitting wherever the final-test canonical ID is held out, not merely annotated. HK duplicate-content observations stay in the same canonical group; later presentation is not automatically worthless or an independent test.
- Preserve run-group/canonical-group compatibility across both cohorts and nested teacher OOF. A connected run group cannot be split merely to balance fold sizes.
- Run-wise nuisance fitting/runz is an offline complete-run transformation. Do not claim single-trial/no-calibration inference. Avoid treating adjacent within-run samples with shared preprocessing statistics as fully independent train/test observations. Downstream PCA/scalers/selection remain training-scope fitted.
- QC inspection is allowed and should discover corrupted data. Comparing alternatives is allowed. Document any final-test exposure used for selection; do not silently relabel an adaptively selected result as independent validation. Test repeated-stimulus reliability is not an unrestricted preprocessing tuning target.

### 6. Why these checks are needed: six-question rationale

These are proposed QA/sensitivity decisions, not new primary neuroscience analyses.

| Item | Scientific question | Alternative explanation | Evidence | Why this limited approach | Change/stop criterion | Cannot establish |
| --- | --- | --- | --- | --- | --- | --- |
| Mask audit | Is usable spatial information unnecessarily excluded? | Coverage gains are noise or changing missingness | R1/R2 and voxel-pattern input contract | Compare existing mask candidates before blanket expansion | No usable added support, incoherent invalid-run handling, or harmful upstream masking | Recovery of lost tissue signal |
| OFC validity/pooling | What anatomical support can the regional estimate represent? | Surviving fragments are mistaken for whole OFC | Reported parcel loss and rank constraints | Preserve fine labels; fixed pooling only as justified supplement | Spatial support/rank inadequate or pooling conceals heterogeneity | Absence of neural involvement |
| SDC metadata/pilot | Is localization improved by a defensible correction? | Guessed PE forces an attractive but wrong warp | R1/R2 and official fMRIPrep/SDC methods | Recover metadata then targeted pilot | Unresolved metadata, implausible warp, poor localization or harm elsewhere | HK displacement from MC data; dropout restoration |
| GM sensitivity | Do brain–content/ROI conclusions depend on broad-GM regression? | Removal of shared neural signal or cross-ROI preprocessing dependence | MC methods, global-regression literature and regression definition | Change four columns, start with small models | Poorly controlled comparison or unreliable effects; retain qualification if conclusions change | A uniquely correct denoising pipeline |
| Motion/time-series QA | Are block patterns interpretable and future estimators reproducible? | Motion, clipping, timing or temporal mixing drives effects | Reported pipeline and actual events/confounds to inspect | Diagnostics and source preservation before new estimators | Window errors, excessive artifact influence or missing reproducible sources | Within-video causal dynamics from block means |
| Split/provenance audit | Is evaluation genuinely outside the fitting/selection scope? | Duplicates, shared run statistics or stale artifacts explain generalization | Existing nested-OOF and canonical-ID contract | Manifest assertions and hashes, not new models | Any scope mismatch or incompatible cache | Independent validation after undisclosed adaptive selection |

### 7. Execution order and acceptance evidence

| Priority | Work | Required return | Completion criterion |
| --- | --- | --- | --- |
| P0 | Snapshot server commit, dirty changes, active jobs, v2 configuration and hashes | `status_and_provenance` section; actual artifact links | No overwritten output; code differences for MC05 explained; active-job authority clear |
| P1 | Reconcile R1–R4 figures and ROI definitions; inspect motion concern | Evidence table with source path, units, denominator, participants/runs and method | Unsupported HK displacement removed; 11/12-parcel and one-run/full-sample distinctions explicit |
| P2 | Complete already authorized mask and MC SDC checks | Participant × run × ROI table; matched before/after spatial panels; candidate-mask provenance | Mechanisms separated; no tSNR-only decision; MC findings not transferred quantitatively to HK |
| P3 | Recover HK PE metadata and prepare pilot proposal | Metadata provenance, candidate config, run IDs, expected cost and proposed pass/fail criteria | No invented acquisition facts; review before new rerun |
| P4 | Audit timing, regression, clipping, atlas, missingness and splits | Reproducible checks and failures with exact IDs | Arithmetic and scientific-quality assertions distinguished; canonical test exclusion verified |
| P5 | Propose limited no-GM sensitivity if not already authorized | Matched configuration diff, development scope, metrics and cost | Rationale accepted before execution; no automatic full-model duplication |
| P6 | Present final preprocessing recommendation | Candidate comparison, decision reasons, selected scope and exposure history | User/authorized freeze process resolves D04; affected caches identified before reprocessing |

Already completed checks should be linked and reused, not recomputed merely because a checklist is new. Failed or infeasible checks are valid outputs. Do not use the final emotion-model score as the only measure of preprocessing validity.

### 8. Return format for the server AIs

Use one focused report under the existing audit tree, for example `project/output/audits/preprocessing_review/report.md`, with supporting TSVs/images/code in that same subtree or links to existing locations. Do not create duplicate current-design documents or root-level report piles.

The report must contain:

1. **Verified on server:** exact paths, code/config hash, scope and calculations.
2. **Not verified / conflicting:** missing evidence and the precise unresolved claim.
3. **Three distinct spatial mechanisms:** low signal, mask exclusion and localization uncertainty.
4. **Candidate comparisons:** matched parameters, development/evaluation exposure and any changed GM mask or spatial support.
5. **Decisions requested:** recommendation, scientific rationale, alternative, cost, reversal criterion and claim limit.
6. **Next three actions:** owner/responsibility, existing approval, artifact and completion test. If multiple AIs work, assign non-overlapping files and do not overwrite each other's changes.

Minimum table fields: cohort, participant, session/run, ROI ID and definition, atlas/mask versions, original/retained voxel counts, coverage denominator, per-run validity, signal/tSNR calculation scope, motion summaries, SDC status/evidence, code/config hash, split group and decision status. Do not fill unknown values with invented numbers or zeros that mean observed signal.

### 9. Known server locations (reported, not accessed in this review)

- Response derivatives: `/storage/bigdata/{MindCaptioning,Horikawa}/response_t1w/sub-XX/v2/`.
- Postprocessing code: `/scratch/connectome/seokjin14/emobrain_response_v2/`; MC05 reportedly uses `/scratch/connectome/seokjin14/emobrain_response_v2_fix/`.
- MC fMRIPrep script: `/storage/bigdata/MindCaptioning/fmriprep/run_fmriprep.sbatch`.
- HK first-pass scripts: `/storage/bigdata/Horikawa/fmriprep/horikawa_preprocess_subXX/run_fmriprep_docker_subXX.sh`.
- HK T1w-output script: `/storage/bigdata/Horikawa/fmriprep_t1w/run_fmriprep_t1w.sbatch`.
- Existing summary: `/storage/bigdata/EmoBrain_response/PREPROCESSING_FINAL.md`; the filename does not establish a scientific freeze.
- R2 references `code/audit/`, `code/sdc_check/`, `code/mask_check/`; resolve their actual root before use.
- R1 names `combined_summary.tsv`, `all_roi.tsv`, `all_runs.tsv`, `all_roi_runs.tsv`, `temporal_33runs.tsv`, `hemisphere_coverage.tsv`, `draft_rule_flagged_ofc.tsv` and spatial QC figures. Their containing audit directory must be located on server. R1's figure tSNR row uses an older first-run calculation, whereas its numerical summary uses the revised 33-run calculation; do not compare them as identical estimators.

---

## 한국어

### 1. 먼저 읽을 것: 목적·권한·즉시 권고

이 문서는 EmoBrain을 잘 모르는 서버 AI도 이어서 검토할 수 있도록 작성한 **전처리 전용 인수인계**다. [07_RESPONSE_ESTIMATION_REVIEW.md](07_RESPONSE_ESTIMATION_REVIEW.md)를 보강하며 전체 연구 사양을 대체하지 않는다. 권한·실행 규칙은 [00_README.md](00_README.md)와 [AGENTS.md](../../AGENTS.md)를 따른다. 사용자 결정과 승인된 freeze가 우선이고, 아래 권고는 자동 확정값이 아니다. D04 및 D19의 ROI 세부 규칙은 미확정이다.

**총괄 권고: 현재 v2를 보존하고 필요한 표적 검사를 마친 뒤, 근거와 결정 규칙에 따라 영향을 받는 단계만 재처리한다. v2를 폐기하거나 추정 PE를 넣어 전체 cohort를 바로 다시 돌리지 않는다.** 이 문서는 기존 승인 작업을 취소하거나 확장하지 않는다. 먼저 실행 상태를 확인한다. 새로운 고비용 작업과 파괴적 대체는 해당 사용자 승인이 필요하다.

`docs/unify-study-design-20261006`에서 작업한다. Main 병합·PR 생성은 하지 않는다. 서버 미커밋 변경·기존 산출물·실패 run을 보존한다. 문서는 Git 이력으로 관리하고 날짜별 current 복사본을 만들지 않는다. 서버 감사 산출물은 `project/output/audits/`에 모으되, 이미 있는 데이터·감사 폴더는 옮기거나 복제하지 말고 연결한다.

#### 전처리 판단에 필요한 연구 배경

- EmoBrain은 affect decoding 성능 경쟁만 하는 연구가 아니라, **뇌–시각–상황 의미의 관계를 모델이 무엇으로 학습하고 예측에 어떻게 사용하는지** 보는 neuroscience 연구다.
- 주 데이터는 MindCaptioning/Horikawa 2025의 영상 시청 fMRI·원본 영상·원본 human caption, 재현은 Horikawa 2020이다. Imagery는 제외한다. 같은 영상의 다른 참가자 cohort는 새로운 자극 분포 일반화와 다르다.
- Analysis 1: 감각–의미 표상이 뇌 반응을 얼마나 설명하는지, 정서 프로필과 공유·조건부 설명력이 어떤지 본다.
- Analysis 2: Brain + Video + Caption joint teacher와 출력 지도를 받는 brain-only student를 학습하고, geometry·content probe·ROI/token 의존성·독립 뇌 검증을 수행한다. 표상 유사성이나 성능만으로 내용 사용을 입증하지 않는다.
- Analysis 3: 정서 프로필 readout과 cohort 재현이다. 34-D·14-D·가용 VA/VAD는 target별 독립 학습이며 공동학습하지 않는다. Crowdsourcing target은 fMRI 참가자의 자기보고가 아니다.
- 주 입력 계약은 **참가자별·제시 회차별 voxel 공간 패턴 한 벡터**다. 블록 시간 평균은 ROI 공간 평균이 아니다. ROI 안 voxel 패턴·참가자·반복 회차를 보존하고 PCA/projector는 해당 training 범위에서 fit한다.
- 낮은 OFC decoding을 낮은 생물학적 중요도로 바꾸어 해석하지 않는다. Participant Map이나 brain weight 증폭이 측정되지 않은 BOLD 정보를 복원하지는 않는다.

### 2. 근거 상태와 두 AI 답변의 조정

**이번 총괄 검토가 직접 본 것:** 사용자가 제공한 두 보고서, 후속 Claude Code/Codex 답변, 현재 저장소 설계, §10의 방법론 자료다. 서버 NIfTI·TSV·QC 그림·코드·Slurm 로그를 직접 열거나 재계산하지 않았다. 아래 수치는 서버 AI의 보고값이며 총괄 AI의 독립 실측값이 아니다.

근거 문서:

- **R1:** 「EmoBrain OFC 집중 품질검사 — 2026-10-07」. 11명 T1w, 725 run, 8,700 run×OFC parcel 기록, 33개 run의 시간적 QC를 보고한다. 이름에 `_OFC_`가 있는 12개 parcel이며 해부학적 OFC/vmPFC 전체가 아니다.
- **R2:** 「EmoBrain 전처리 전체 정리 (검토 요청용, 2026-10-07)」. 전처리 설정과 마스크·SDC 검토 계획을 보고한다. OFC 범위는 Limbic parcel 11개로, Control parcel을 포함한 R1의 12개와 다르다.
- **R3:** 후속 Claude Code 답변. 저신호와 마스크 제외를 나눈 점은 유용하지만, 공간 품질을 과도하게 확정하고 MindCaptioning 변위를 Horikawa로 외삽한다.
- **R4:** 후속 Codex 답변. 저신호·마스크 제한·위치 불확실성을 올바르게 구분한다. Horikawa 05 등의 움직임 우려를 추가로 언급했으나, 해당 run/block 근거 수치는 이번 전달 자료에 없다.

| 주장 | 근거 상태와 올바른 해석 |
| --- | --- |
| MC 6명×70 run + HK 5명×61 run = 725 | 보고 숫자의 산술은 일치한다. 서버 manifest와 viewing-only 선택은 확인한다. |
| T1w가 11명 모두 존재 | R1에 경로와 함께 보고됨. SDC 성공이나 국소 정합 통과를 뜻하지 않는다. |
| OFC 범위 MC 약 41–67%, HK 48–82% | R2의 **11-parcel** 값이다. R1의 **12-parcel** 값은 44.4–68.8%, 49.7–82.9%다. ROI ID·분모 없이 섞지 않는다. |
| HK02 개별 run OFC 68.3–93.3%, 공통 49.7% | R1 보고. 교집합의 추가 제외를 보여주지만 제외된 모든 voxel이 쓸 만하다는 증거는 아니다. |
| 90% 마스크로 5–9%p 증가 | 참가자별 paired 차이를 재계산해야 한다. 범위 양 끝의 차이만으로 개인별 증가량을 확정하지 않는다. |
| 새 voxel SNR이 절반 | R2의 HK01 **한 run tSNR** 예비 결과다(예: OFC 20.9 대 9.9). 11명 전체 결과도, 신경정보가 절반이라는 뜻도 아니다. |
| HK Limbic 약 5 mm, 시각 약 1 mm 왜곡 | **확인되지 않음.** R2의 변위 실측은 MC에서 나왔다. HK의 변위 수치로 옮기지 않는다. 평균·중앙값·백분위도 구분한다. |
| MC는 fieldmap 보정했으니 공간 문제없음 | 근거 부족. 적용 여부와 fieldmap 연결·보정 품질·저신호 국소 정합은 별도다. |
| OFC·측두극 밖은 모두 문제없음 | 근거 부족. 계산 재현 검수와 움직임·정합·조직·과제 신호 품질은 다르다. |
| 독립 재계산이 v2 저장값과 일치 | 보고서상 강한 산술 QA다. 선택한 계산 정의의 재현성을 검증하며 최적성·과학적 충분성을 입증하지 않는다. |

AI 간 의견이 다르면 투표하지 말고 근거 표와 계산을 확인한다. ‘문제 없음’ 대신 **어떤 범위에서 어떤 검사가 어떤 기준으로 통과했는지** 쓴다.

### 3. 현재 보고된 파이프라인: 기준판으로 보존

| 단계 | 보고된 설정 |
| --- | --- |
| 촬영 | MC TR 1초·TE 30 ms, HK TR 2초·TE 43 ms, 둘 다 2 mm. 같은 후처리 코드로 촬영 차이가 없어지지 않는다. |
| fMRIPrep | 25.0.0, 개인 T1w 공간 출력. MC는 세션별 phase-difference fieldmap, 420/420 run 적용 보고. HK 현재 derivative는 SDC 없음, PE metadata 누락 보고. |
| HK 재사용 | MNI 출력 1차 결과를 T1w 출력 2차 실행에서 재사용. 움직임 값 일치만으로 전체 적용 transform chain을 검증하지 못한다. |
| 초기 volume | MC 회귀 전 8초 삭제, NSS가 그 안에 있다고 보고. HK는 초기 volume 유지 및 해당 NSS spike regressor 추가. 차이 자체를 오류라 단정하지 말고 이유와 시간 원점 확인. |
| `common36` | Motion 24 + CSF/WM/GM 각 4확장, 별도로 상수·선형 추세·해당 NSS 열. GM 평균은 확률 ≥0.5 ∩ 분석 마스크. |
| 반응 추정 | 4초 지연, ±3 SD 반복 clipping 최대 10회, 실제 제시 block과 명시된 후속 rest 평균. 참가자별 events duration 표기 차이를 처리한다고 보고. |
| 정규화 | Run 내부 block response들로 voxel별 z-score. Runz 전 block도 저장. Volume 기준 z-score와 block 기준 z-score는 같은 연산이 아니다. |
| 마스크 | 참가자별 모든 run 뇌 마스크 교집합 및 변동 voxel 검사. 모든 참가자의 교집합이라는 뜻은 아니다. |
| Atlas | Schaefer400·Tian S3·시상하부/BNST·소뇌·뇌간 복합 469개 보고. Label 합계·transform·겹침 처리는 확인 필요. |
| 보조 시계열 | 회귀·지연 처리 후 0.01–0.1 Hz filter, 시간 Gaussian FWHM 4초, run z-score 및 조각 추출. 이것만 원자료 보존본으로 삼지 않는다. |

R2의 MC 참가자당 2,540행(2,180+72×5), HK 2,196행은 전체 26,220행과 산술적으로 일치한다. 이는 **관측 행**이지 모두 고유 학습 자극이라는 뜻은 아니다. MC 학습 세션의 test 영상 회차와 HK 동일 내용 영상은 canonical ID 분할이 필요하다.

### 4. 요청된 네 가지 결정

#### 4.1 모든 run 교집합인가, 90% 마스크인가?

**잠정 권고:** 현재 교집합을 기준 derivative로 보존한다. 한 run의 tSNR이나 voxel 증가량만으로 90% 마스크를 primary로 바꾸지 않는다.

1. 소수 실패 run/mask, 지속적 저신호, FOV 경계, 정합, 변동 voxel 규칙 중 무엇이 제외를 만드는지 분리한다. 상위 단계 오류가 발견되면 무조건 완화하기 전에 오류를 해결한다.
2. 계획된 여러 참가자·run 검사를 마친다. 세션·품질 범위 선정 방법과 의도적으로 고른 최악 run을 구분한다.
3. 추가 voxel/ROI의 위치·유효 run 비율·steady-state 평균 신호·tSNR 정의·움직임·개인/run 분포를 보고한다. 촬영 조건을 무시한 보편 tSNR 합격선을 만들지 않는다.
4. 90% 기준으로 포함한 voxel이 나머지 무효 run에서 어떻게 처리되는지 정한다. fMRIPrep 마스크 밖에도 수치가 있다는 것만으로 유효 뇌 측정이 되지는 않는다. 무표시 0 채우기를 정상 반응으로 취급하지 않는다.
5. ROI token ID 고정만으로 ROI 내부 voxel 구성이 달라지는 문제가 해결되지 않는다. 결측을 명시하고 run/session shortcut 가능성을 확인한다. Train-only PCA의 feature 공간도 일관되어야 한다.
6. **두 효과를 분리한다:** 분석 마스크를 바꾸면 GM 평균 회귀 신호도 바뀐다. 가능하면 nuisance 정의를 고정한 마스크 비교를 먼저 하고, 이후 전체 후보 파이프라인의 차이를 기록한다. 그렇지 못하면 결과는 마스크 단독 효과가 아니라 결합된 변경 효과다.
7. 마스크 산출에 어떤 run, 특히 평가 run이 포함되는지 기록한다. 해부학적 acquisition QC가 자동 label leakage는 아니지만, all-run 적응을 training-only unseen-run 변환으로 서술하지 않는다. 데이터로 threshold를 고르는 범위는 별도 development로 정의한다.

완화 채택 조건은 추가 위치의 실제 사용 가능성, 무효 run 처리의 일관성, 관련 결론의 안정성이다. 최대 coverage나 최대 tSNR 자체가 연구 목표는 아니다.

#### 4.2 작은 OFC parcel은 결측인가, 합칠 것인가?

- 원래 parcel ID와 coverage/validity mask를 유지한다. 빈 parcel은 결측이며 0 신경 반응이 아니다.
- `<10 voxel 또는 coverage<20%`는 기술적 초안 flag다. 통과해도 신호·정합이 나쁠 수 있다. Mask 전후 수, PCA rank 가능성, 공간 위치까지 정의한다.
- 최소 개수를 통과시키려고 참가자마다 남은 parcel을 다르게 합치지 않는다.
- 같은 반구의 해부학적 상위 OFC는 모든 참가자에 같은 pooling map을 정한 뒤 보조안으로 검토할 수 있다. 합치면 질문이 달라지고, 사라진 부위가 복원되지 않는다. Multivoxel 질문이면 voxel 패턴을 유지한다.
- Schaefer ‘Limbic’은 피질 network 이름이지 모든 변연계 구조가 아니다. Amygdala·hypothalamus·BNST 등 작은 피질하 영역은 별도 QC한다. `_OFC_` 12개도 해부학적 OFC/vmPFC 전체가 아니다.

#### 4.3 Horikawa 왜곡 보정과 PE 정보 누락

**‘한 문장으로 제한점을 쓰고 종료’도, ‘방향을 짐작해 5명 전체 재실행’도 기본안으로 충분하지 않다.**

1. DICOM/변환 기록, BIDS 상위 metadata, protocol, 원저자 전처리 설정을 먼저 찾는다. 필요한 저자 문의는 사용자 승인을 받은 후에만 보낸다.
2. 영상 축·실제 해부학적 방향·PE polarity를 구분하고 NIfTI orientation을 기록한다. 축도 모르면 ‘두 방향을 해본다’는 설명 자체가 불충분하다.
3. 실제 container/SDCFlows 버전의 readout time 등 입력 요건을 확인한다. PE가 없을 때 `--use-syn-sdc warn`으로 실행만 끝나고 SDC는 안 될 수 있다. Raw BIDS에 추정값을 실측처럼 쓰지 않는다. 추정 후보는 별도 derivative/config와 근거로 관리한다.
4. 근거 있는 후보가 마련되면 HK01/02 등의 제한된 development run pilot과 계산량을 제안한다. 전체 재실행은 pilot 검토 이후다.
5. 신호가 남은 위치의 해부학 경계, warp/Jacobian의 타당성, 국소 변위, 다른 영역 악화, coverage, 반응 패턴 변화를 함께 평가한다. T1과 더 잘 맞는지만으로 판정하지 않는다. 이는 최적화 목표 자체이기 때문이다. 신호 소실과 위치 변형도 구분한다.
6. 재사용 시 SDC의 영향을 받는 BOLD reference·BOLD-to-T1 정합·resampling·mask·confounds가 실제 재계산되는지 확인한다. 이전 미보정 기능영상 결과를 잘못 재사용하지 않는다. 재사용 가능한 해부학 결과까지 자동 재실행할 필요는 없다.

진행 중인 MC 보정 ON/OFF는 **MC 내부의 민감도 실험**으로 유용하다. HK 왜곡 크기를 추정하거나 가정한 HK PE를 검증하지는 못한다. MC fieldmap 보정판은 측정 field 기반의 기준판이지 무오류 정답이 아니다. Fieldmap/run 연결과 보고한 mm가 전체 transform이 아닌 SDC 비선형 변위인지 확인한다. 후보별 고유 mask뿐 아니라 공통 평가 support에서도 비교해 포함 위치 변화와 신호 변화를 구분한다.

PE를 확인하지 못하고 후보 정당성도 확보되지 않으면, 확신을 만들어내기보다 현 미보정판을 국소 위치 해석 제한과 함께 유지한다. 근거 있는 pilot에서 다른 영역을 과도하게 손상시키지 않으며 안정적 이득이 확인되면, 해당 HK 기능영상 단계와 후속 산출물 재처리를 제안한다. 이전 판을 보존하고 호환되지 않는 cache를 명시한다.

#### 4.4 두 cohort의 결과 해석

- 저신호·마스크 추가 제외·위치 불확실성은 원인과 대응이 서로 다르다.
- 현재는 세밀한 OFC/측두극 위치, 시각피질 대비 중요도, cohort 간 영역 순위를 핵심 결론으로 삼지 않는다.
- 유효한 해당 영역 자료까지 모두 삭제할 필요는 없다. Coverage·신뢰도 제한과 함께 모델에 사용할 수 있다. OFC 전체 또는 모든 ‘Limbic’ 구조의 일괄 제외는 이 보고서로 정당화되지 않는다.
- 측정이 나쁜 곳의 낮은/없는 효과는 생물학적 무관함의 증거가 아니다. 양성 결과도 정합·artifact 검토가 필요하다.
- 촬영·SDC 차이는 여전히 confound 후보이며 공통 후처리 코드로 없어지지 않는다. 국소 한계가 세 분석 전체의 무효를 자동 의미하지도 않는다.

### 5. OFC 외에 EmoBrain에서 중요한 추가 항목

#### 5.1 GM 평균 회귀와 ROI 해석

MC 원문은 motion 24와 CSF/WM/GM 확장을 실제 기술한다[1]. 따라서 `common36`은 문헌 근거가 있고 GM 회귀 자체를 구현 오류라고 부르면 안 된다. 그러나 HK2020의 정확한 재현도, EmoBrain에서의 최적성 입증도 아니다.

광범위 GM 신호에는 잡음과 신경/과제 관련 성분이 함께 있을 수 있다. 이를 제거하면 분석 가능한 공간 패턴이 달라진다. 또한 전체 GM 시계열로 전처리한 특정 ROI residual은 계산상 ROI 밖 측정에도 의존한다. **이 자체를 정답 누출이라고 부르지는 않지만**, ‘시각피질 측정만으로 충분하다’는 강한 주장과 ROI 증분/의존성 해석에는 제약이 생긴다.

**개발용 sensitivity 권고이며 새 primary 확정 아님:** `common36`과 GM 관련 4개 열만 뺀 동일 파이프라인을 비교한다(움직임 24+CSF/WM 8, 별도 상수·추세·해당 NSS). Mask·timing·다른 설정을 맞춰 해당 선택만 분리한다. 모든 teacher/student를 두 벌 돌리기 전에 제한된 선형 encoding/readout과 전처리 진단부터 검토한다. No-GM이 무조건 정답이거나 성능을 높인다는 뜻은 아니다. 이미 회귀한 residual을 다시 회귀해 대체하지 말고 적절한 회귀 전 BOLD에서 시작한다. GM 정의, 제거 분산량, run/task/nuisance 구조와의 관계를 기록한다.

모델 ROI 교란에서는 전처리를 고정하고 **처리된 ROI 입력에 대한 모델 의존성**으로 해석한다. ROI 교란마다 global regression을 다시 하면 여러 영역이 함께 바뀌어 질문이 달라진다.

#### 5.2 시계열 보존

fMRIPrep 연속 BOLD·events·confounds·실제 시간 좌표·censor/NSS 정보와, 추가 band-pass/시간 smoothing 없는 후처리 시계열을 재생성할 수 있는 자료를 보존한다. 현재 필터된 조각은 선택적 derivative로 유지할 수 있다. 향후 duration-aware GLM이나 시간 분석의 유일한 원천으로 삼지 않는다. 양방향 filter와 시간 smoothing은 인접 시점을 섞으므로, 조각을 독립 관측이나 심리적 처리 순서의 증거로 취급하지 않는다. 새 temporal model 실행은 승인하지 않는다.

#### 5.3 움직임·clipping·시간 정렬

- 평균 FD 0.10–0.20 mm가 모든 volume/block 통과를 뜻하지 않는다. FD/DVARS 분포·최댓값·명시한 후보 기준에서의 영향 volume 비율·block 요약을 보고한다. 특히 새로 언급된 HK05 우려의 근거를 확인한다. 이번 문서에서 그 크기는 미확인이다.
- ±3 SD 반복 clipping은 motion censoring이 아니다. 바뀐 voxel-volume 비율·block/ROI·반복 횟수·수렴을 기록한다. 변경이 광범위하면 clipping sensitivity를 진단 후보로 검토하되 전체 조합 실험을 자동 추가하지 않는다.
- Volume 삭제 후 시간 원점, slice-time 기준, 4초 지연 방향, rest 포함, 원본 clip과 제시 block 길이, run 말단 잘림을 확인한다. fMRIPrep 25.0.0 문서는 middle-TR 정렬을 기술한다[2]. 실제 설정을 확인하고 추가 offset을 자동 적용하지 않는다. 총 길이와 대략적인 후두엽 latency만으로 모든 평균 window가 확인되지는 않는다.
- 회귀 design 열 이름·scaling·수치 rank/tolerance·잔여 자유도·projection 검사를 기록한다. 열 이름이 남았다고 선형 독립인 것은 아니며, 정당한 rank reduction과 이전 scaling 오류를 구분한다. 독립 계산 비교 근거를 남긴다.
- 상수 voxel 1개를 0으로 처리한 예외가 ‘모든 run에서 변동하는 voxel’ 규칙과 어떻게 양립하는지, 최종 포함 여부·validity flag를 확인한다. 이 한 voxel 때문에 전체 데이터가 무효라고 단정하지 않는다.

#### 5.4 Atlas·정규화·분할 경계

- 복합 atlas ID·겹침/우선순위·transform·surface-to-volume 매핑·범주형 보간을 확인한다. 보간된 label 숫자를 그대로 해부학 label로 취급하지 않는다. 의도한 ROI와 atlas 밖 voxel을 모두 설명한다.
- MC 학습 세션에 있는 최종 test 영상은 표시만 하지 말고, 해당 canonical ID가 held-out인 모든 fit에서 제외한다. HK 동일 내용 관측은 같은 canonical group에 둔다. 나중 회차가 자동 무가치한 것도 독립 test인 것도 아니다.
- 두 cohort와 nested teacher OOF에서 run-group/canonical-group 경계를 맞춘다. Fold 균형을 위해 연결된 run 그룹을 임의로 자르지 않는다.
- Run별 nuisance fit/runz는 offline complete-run 변환이다. 단일 trial·무보정 추론으로 부르지 않는다. 공유 전처리 통계가 있는 인접 같은-run 자극을 완전히 독립 train/test로 취급하지 않는다. Downstream PCA/scaler/selection은 training 범위 안에서 수행한다.
- QC 관찰과 후보 비교 자체는 허용하며 손상 자료를 찾아야 한다. 최종 test를 선택에 사용한 이력은 기록하고, 적응적으로 고른 결과를 독립 검증으로 이름만 바꾸지 않는다. 반복 test 신뢰도를 무제한 전처리 tuning 기준으로 사용하지 않는다.

### 6. 왜 필요한 검사인가: 여섯 질문 근거

아래는 제안된 QA/sensitivity 판단이며 새로운 primary neuroscience 분석이 아니다.

| 항목 | 과학적 질문 | 대안 설명 | 근거 | 제한된 방법의 선택 이유 | 변경/중단 기준 | 주장할 수 없는 것 |
| --- | --- | --- | --- | --- | --- | --- |
| 마스크 감사 | 쓸 만한 공간 정보를 불필요하게 제외하는가? | 증가한 범위가 잡음·결측 변화일 수 있음 | R1/R2와 voxel-pattern 입력 계약 | 전면 확대 전 기존 후보를 비교 | 추가 support 부적합·무효 run 처리 불일치·상위 masking 오류 | 소실 신호 복원 |
| OFC validity/pooling | 영역 추정치가 어떤 해부학 범위를 대표하는가? | 남은 일부를 OFC 전체로 오인 | 보고된 손실·rank 제약 | 원 label 보존, 고정 pooling은 보조 | Support/rank 부족·pooling이 이질성 은폐 | 신경학적 무관함 |
| SDC metadata/pilot | 근거 있는 보정으로 위치 정확성이 개선되는가? | 추정 PE가 그럴듯하지만 틀린 warp를 만듦 | R1/R2·공식 SDC 방법 | Metadata 복구 후 표적 pilot | 근거 미해결·비현실 warp·위치 부정확·타 영역 악화 | MC 수치로 HK 변위 확정·dropout 복원 |
| GM sensitivity | 뇌–내용/ROI 결론이 GM 회귀에 의존하는가? | 공유 신경 성분 제거·ROI 밖 전처리 의존 | MC methods·global 회귀 문헌·연산 정의 | 4개 열만 변경, 작은 모델부터 | 통제 실패·불안정 결과; 결론 달라지면 제한 명시 | 유일하게 옳은 denoising |
| Motion/시계열 QA | Block 패턴 해석과 재추정이 가능한가? | Motion·clipping·시간 오류·혼합이 효과를 만듦 | 보고 pipeline·확인할 events/confounds | 새 estimator 전 진단·보존 | Window 오류·큰 artifact 영향·재현 원천 없음 | Block 평균으로 영상 내 인과 dynamics |
| Split/provenance | 평가가 fit/selection 범위 밖인가? | 중복·공유 run 통계·오래된 cache | 기존 OOF·canonical 계약 | Manifest assertions·hash | Scope 위반·cache 비호환 | 미공개 선택 후 독립 검증 |

### 7. 작업 순서와 완료 증거

| 우선순위 | 작업 | 반환물 | 완료 기준 |
| --- | --- | --- | --- |
| P0 | 서버 commit·미커밋 변경·실행 job·v2 설정/hash 확인 | `status_and_provenance` 절과 실제 링크 | 덮어쓰기 없음, MC05 코드 차이 설명, 기존 job 권한 확인 |
| P1 | R1–R4 수치·ROI 정의 조정, 움직임 우려 확인 | 출처 경로·단위·분모·참가자/run·계산법 표 | HK 미실측 변위 제거, 11/12-parcel·한 run/전체 구분 |
| P2 | 기존 승인된 mask/MC SDC 검사 완료 | 참가자×run×ROI 표, 대응 전후 그림, mask provenance | 세 원인 분리, tSNR 단독 결정 금지, MC→HK 정량 외삽 금지 |
| P3 | HK PE 정보 복구 및 pilot 제안 | Metadata 근거·후보 설정·run ID·계산량·판정 기준 | 촬영 사실 창작 없음, 신규 재실행 전 검토 |
| P4 | 시간·회귀·clipping·atlas·결측·split 감사 | 재현 검사와 실패 ID | 산술 검수/과학적 품질 구분, canonical test 제외 확인 |
| P5 | 미승인 상태면 제한된 no-GM sensitivity 제안 | 대응 설정 diff·development 범위·metric·비용 | 이유 승인 후 실행, 전체 모델 두 벌 자동 실행 금지 |
| P6 | 최종 전처리 권고 | 후보 비교·선택 이유·scope·노출 기록 | 사용자/승인 freeze 절차로 D04 해결, 재처리 전 cache 영향 확인 |

이미 완료한 검사는 링크로 재사용하고 새 체크리스트라는 이유만으로 반복하지 않는다. 실패·실행 불가도 산출물이다. 최종 감정 예측 성능만을 전처리 타당성의 유일한 기준으로 삼지 않는다.

### 8. 서버 AI 반환 형식

기존 audit 구조 안에 집중 보고서 하나를 둔다. 예: `project/output/audits/preprocessing_review/report.md`. TSV·그림·코드는 같은 하위 폴더에 모으거나 기존 위치를 연결한다. Current 설계 사본이나 루트 보고서 묶음을 만들지 않는다.

반드시 포함할 것:

1. **서버에서 확인한 것:** 실제 경로·code/config hash·범위·계산.
2. **미확인/충돌:** 없는 근거와 정확히 어떤 주장이 미해결인지.
3. **공간 문제 세 가지:** 저신호·마스크 제외·위치 불확실성.
4. **후보 비교:** 맞춘 설정, 개발/평가 노출, GM mask나 공간 support 변경 여부.
5. **결정 요청:** 권고·과학적 이유·대안·비용·판단 변경 기준·주장 한계.
6. **다음 세 작업:** 책임 범위·기존 승인·산출물·완료 검사. 여러 AI가 작업하면 파일 소유 범위를 나누고 서로의 변경을 덮어쓰지 않는다.

최소 표 필드: cohort, participant, session/run, ROI ID/정의, atlas/mask version, 원래/남은 voxel 수, coverage 분모, run별 validity, 신호/tSNR 산출 범위, motion 요약, SDC 상태/근거, code/config hash, split group, decision status. 미확인을 가짜 숫자나 정상 신호를 뜻하는 0으로 채우지 않는다.

### 9. 보고된 서버 위치 — 이번 검토에서 직접 접근하지 않음

- 반응 derivative: `/storage/bigdata/{MindCaptioning,Horikawa}/response_t1w/sub-XX/v2/`.
- 후처리 코드: `/scratch/connectome/seokjin14/emobrain_response_v2/`; MC05는 `/scratch/connectome/seokjin14/emobrain_response_v2_fix/` 사용 보고.
- MC fMRIPrep: `/storage/bigdata/MindCaptioning/fmriprep/run_fmriprep.sbatch`.
- HK 1차: `/storage/bigdata/Horikawa/fmriprep/horikawa_preprocess_subXX/run_fmriprep_docker_subXX.sh`.
- HK T1w 출력: `/storage/bigdata/Horikawa/fmriprep_t1w/run_fmriprep_t1w.sbatch`.
- 기존 요약: `/storage/bigdata/EmoBrain_response/PREPROCESSING_FINAL.md`. 파일명이 FINAL이라고 연구 설정이 동결된 것은 아니다.
- R2의 `code/audit/`, `code/sdc_check/`, `code/mask_check/`는 실제 root를 확인한 뒤 사용한다.
- R1의 `combined_summary.tsv`, `all_roi.tsv`, `all_runs.tsv`, `all_roi_runs.tsv`, `temporal_33runs.tsv`, `hemisphere_coverage.tsv`, `draft_rule_flagged_ofc.tsv` 및 QC 그림은 서버에서 포함 폴더를 찾는다. 그림의 tSNR 행은 이전 첫-run 계산이고 수치 요약은 갱신된 33-run 계산이므로 동일 estimator처럼 비교하지 않는다.

---

## 10. References and verification scope / 참고문헌과 확인 범위

1. Horikawa, T. (2025). *Mind captioning: Evolving descriptive text of mental content from human brain activity*. Science Advances, 11, eadw1464. [Article](https://pmc.ncbi.nlm.nih.gov/articles/PMC12588295/). The retrieved methods explicitly describe motion-24 and CSF/WM/GM expansions. This does not independently verify the server's exact GM mask, implementation or all processing details. / 검색된 원문 methods에서 해당 회귀항을 확인했으며 서버 구현 전체를 검증한 것은 아니다.
2. fMRIPrep 25.0.0. [Processing pipeline](https://fmriprep.org/en/25.0.0/workflows.html), [usage](https://fmriprep.org/en/25.0.0/usage.html). Supports documented temporal/spatial processing and configuration checks, not actual execution on these runs. / 공식 처리 정의와 옵션 근거이며 해당 run 실행의 증거는 아니다.
3. fMRIPrep. [Change history, including missing-PE SyN behavior](https://fmriprep.org/en/24.1.0/changes.html), [25.x derivative reuse changes](https://fmriprep.org/en/25.2.0/changes.html). Check the installed container/logs rather than infer execution from flags. / 실제 실행은 container/log로 확인한다.
4. Esteban, O., et al. (2019). *fMRIPrep: a robust preprocessing pipeline for functional MRI*. Nature Methods. [Article](https://pmc.ncbi.nlm.nih.gov/articles/PMC6319393/). Describes anatomical-reference, constrained fieldmap-less SDC; does not validate guessed acquisition metadata for Horikawa. / 해부학 기반 SDC 원리이며 HK 추정 metadata의 검증 근거가 아니다.
5. Murphy, K., et al. (2009). *The impact of global signal regression on resting state correlations: Are anti-correlated networks introduced?* NeuroImage. [Article](https://pmc.ncbi.nlm.nih.gov/articles/PMC2750906/). Provides methodological evidence that global regression changes signal relationships, not proof that the current task pipeline is invalid. / 신호 관계 변화의 근거이지 현재 task pipeline 무효 판정은 아니다.

R1–R4 are user-supplied project evidence, not external peer-reviewed sources. The limited no-GM comparison and operational decision gates are project-specific recommendations. No server job, new experiment, final threshold, scientific result or primary-design freeze is created by publishing this document.

R1–R4는 사용자가 제공한 프로젝트 근거이며 외부 검증 논문이 아니다. 제한된 no-GM 비교와 운영 판정 규칙은 이 프로젝트에 대한 권고다. 이 문서 발행 자체로 서버 job·새 실험·최종 threshold·연구 결과·primary 설계 동결이 발생하지 않는다.
