# Implementation status and migration boundary

_Static repository audit · 2026-10-06 · not an execution report_

---

## 📍 Scope and authority

The current design is defined by [00_README](00_README.md), not by inherited code defaults. The audit examined main commit `a5285044ce417945685e0eb044ac77f68d487af0`, following the documented training entry point, loaders, decoder, loss, legacy teacher/cache/student and tests. It did not execute training or tests, inspect server-only modifications, or establish new scientific results. A missing implementation in this inspected path does not prove it is absent from the server.

This branch unifies documentation only. No inherited experiment becomes a current-design result by this change.

The subsequent D20 decision keeps Joint training as the default and allows an optional Brain-first → Joint comparison. D21 shared-head auxiliary training remains a proposal. P11b now specifies scope-safe warm-up provenance and experiment-selection records. These are documentation changes, not implemented or executed training results.

후속 D20 결정은 Joint 학습을 기본으로 유지하고 Brain-first → Joint 비교를 선택적으로 허용한다. D21 공유 head 보조 학습은 제안 상태다. P11b에 warm-up의 학습 범위·provenance와 실험 선택 기록을 추가했으며, 이는 구현·학습 실행 완료 보고가 아니다.

## 🔍 Verified implementation gaps

2026-10-08 documentation update: D22–D24 add detailed Participant Map/encoder contracts, optional ROI-masked JEPA design and multi-layer vision extraction proposals. P07b/P08b/P11c specify tests. These are specifications, not claims that the server has implemented or passed them. Existing server code, audit outputs and coordination states are unchanged by this update.

2026-10-08 문서 갱신: D22–D24에 Participant Map/encoder 계약, 선택적 ROI-masked JEPA 설계, 다층 vision 추출 개발안을 추가했다. P07b/P08b/P11c는 필요한 검사 목록이며 서버 구현·통과 보고가 아니다. 이번 갱신은 기존 서버 코드·감사 산출물·작업 상태를 변경하지 않는다.

| Area | Repository evidence at audited commit | Migration requirement |
| --- | --- | --- |
| Model | `project/code/decoder/label_query_decoder.py`: emotion queries read combined memory | Implement the current brain-query teacher and small brain-only student |
| Brain input | `project/data/fmri_adapter.py`: one mean value per ROI per participant | Connect voxel block responses; fit ROI compression/maps only within training scopes |
| Labels/loss | `project/data/datasets.py`, `labels.py`, `scripts/train_label_query.py`: 34-D log1p-z plus MSE | Separate target contracts; 34-D soft BCE plus probability-MSE guidance |
| Split | `project/shared/code/build_canonical_split.py`: 2185 fixed IDs, stimulus stratification | Audit canonical content/repeats/runs/cohorts; build shared scope manifests |
| Teacher guidance | `project/code/training/cache_soft_labels.py`: one teacher predicts train/val | Replace with nested recipient-excluded OOF; do not relabel old caches |
| Caption | `scripts/train_label_query.py` loads caption_embed.npy; old README identifies generated captions | Verify provenance and use the intended human-caption features |
| Analysis | No current 1b/2d/content-probe/patching pipeline found in the inspected active path | Compare server work first, then implement required analyses and tests |
| Persistence | Main label-query script returns summary metrics without persisting its best checkpoint | Save checkpoints, fold transforms, stage outputs and stimulus-level predictions for analysis |

## ⚠️ Concrete reuse hazards

1. The documented `train_label_query.py` call omits `query_init` while the model defaults to residual semantic queries and explicitly rejects missing initialization. Static call-path inspection establishes a constructor error if execution reaches it; no runtime reproduction was performed. Fixing it would only repair an old baseline.
2. `gate1_sanity.py` chooses its winning arm from test metrics. Its bootstrap operates on pooled participant-by-stimulus rows, not independent participants. Do not reuse this as a current confirmatory gate.
3. `evaluation/metrics.py` calculates conventional R² using the evaluation-target mean. It is not the proposed Analysis 1b Q with a shared training-intercept denominator. The conventional metric is not intrinsically wrong, but it is a different quantity.
4. Old ROI-mean features discard within-ROI spatial patterns. Temporal block averaging does not require that spatial averaging or participant averaging.
5. Existing core tests cover old encoder/padding/normalization behavior; they do not establish current nested OOF, target isolation or brain-only content-access guarantees.

## ✍️ Server migration order

1. Record the server commit, dirty files, running jobs, data/cache provenance and test exposure without resetting anything.
2. Review this documentation branch on its own. Fetching it does not authorize switching a busy/dirty training checkout or merging main.
3. Reconcile actual preprocessing artifacts and stable canonical IDs before changing model code. Candidate generation/comparison is not itself evidence that a final estimator was selected.
4. Resolve D01–D04 split/input questions, then implement data contracts and leakage QA.
5. Build a small B-only baseline and encoding pilot; then brain-grounded teacher controls, nested OOF and student guidance.
6. Add current Analysis 1–3 outputs and verification. Freeze unresolved choices explicitly before confirmatory runs.

## 📌 Unresolved items remain unresolved

Importing the handoff does not approve outer/inner K, ROI rank, small-n inference, replication mode, the proposed 2d bridge details or D18 candidate rules. VS-guided student remains D14 claim-dependent, not automatically mandatory. The proposed ROI increment study is D19; no new experiment has been approved or launched by recording it. No frame scrambling, imagery or new model backbone was added.

## 💾 Provenance and clean layout

The maintained files were imported from `Server_Handoff_2026-10-06`, with repository navigation, clarified report status and the D19 proposal added. Local dated handoff folders/ZIPs and original manuscript/preregistration files remain untouched outside this repository and are historical exports, not parallel editable authorities. Do not create another all-in-one copy or ZIP in this branch.

Earlier GitHub entry points and reviews are under [docs/archive](../archive/README.md). Literature reference files remain in docs/reference, but do not override current decisions. When server evidence changes an audit finding, update this file and the relevant decision with commit/path/test evidence.
