# Task board / 작업판

_GPT assigns; agents update their own rows with exclusive shared-file access. Updated 2026-10-08._

---

## 📋 English

Use the [coordination rules](README.md). Existing task states below are preserved; this update does not launch jobs or approve scientific choices. Before moving to `doing`, name an owner, reviewer and exact writable paths. `unassigned` means not ready for execution. The board is not a lock.

Status: `todo` · `doing` · `review` · `blocked` · `done`

| ID | Task / 할 일 | Owner / 담당 | Status / 상태 | Reviewer / 검토 | Files touched / 건드리는 파일 | Thread |
| --- | --- | --- | --- | --- | --- | --- |
| T001 | OFC voxel loss: intersection-mask rule versus absent signal (09 §4.1) / 안와전두 voxel 손실 원인 분리 | unassigned | todo | — | — | [T001](threads/T001-ofc-mask.md) |
| T002 | Canonical content ID across cohorts, including 1349/1363 / 두 cohort 공통 content ID, 1349/1363 포함 | Claude Code | review | Codex | — (proposal only) | [T002](threads/T002-content-id-1363.md) |
| T003 | Annotation join by content ID for both cohorts / annotation 을 content ID 로 연결 | unassigned | todo | — | — | [T003](threads/T003-annotation-join.md) |
| T004 | Pilot data adapter and development audit / pilot 데이터 어댑터·개발 감사 | Claude Code | review | Codex | `project/data/pilot_adapter.py`; `project/data/pilot_adapter.sh`; `project/tests/test_pilot_adapter.py`; `project/output/audits/pilot_data/`; `project/baseline/` (user request, ownership pending GPT) | [T004](threads/T004-pilot-data-adapter.md) · [Handoff](../current/10_PILOT_IMPLEMENTATION_HANDOFF.md) |
| T005 | Pilot pipeline, contracts and tests / pilot 구현·계약·테스트 | Codex | todo | Claude Code | `project/code/pilot_contracts.py`; `project/code/pilot/`; `project/scripts/run_pilot.py`; `project/tests/test_pilot_contracts.py`; `project/tests/test_pilot_pipeline.py`; `project/configs/pilot/`; `project/output/audits/pilot_code/` | [Handoff](../current/10_PILOT_IMPLEMENTATION_HANDOFF.md) |

### Deliverables and completion criteria

- **T004/T005:** Follow the handoff's P0–P3 sequence and exact ownership. Existing equivalent implementations take priority over duplicate new modules; claim any changed paths before edits. T004 returns an audited batch/manifest contract and bounded development subset. T005 first returns synthetic tests and a CPU baseline plan, then implements the bounded model/probe path. Code readiness, real-data execution and scientific validation are separate statuses. The supplied guard passes 11 local synthetic tests; no server training is claimed. T004 may inventory T003 issues but does not approve its target policy. Report back on the board with evidence paths; serialize board edits.

- **T001:** First locate v2 run-level masks and unfiltered signal/QC sources; the thread reports missing run masks on Perlmutter. Return paired coverage and added-voxel quality evidence under matched atlas/mask denominators, with code commit and run provenance, following 09 §4.1–4.2. Separate acquisition low signal from intersection exclusion; do not substitute old MNI audit numbers for v2. Exact output paths and independent reviewer must be assigned before execution. No mask threshold change is approved here.
- **T002:** Codex reviews Claude Code's existing proposal and evidence in the linked thread. Return a reproducible check of 1349/1363 identity, crosswalk differences and split grouping with source versions. Distinguish a verified content match from the author's reason for exclusion, which requires separate evidence. Whether to retain both Horikawa presentations remains a user decision; do not change splits or drop samples during review.
- **T003:** After the canonical mapping review, inventory missing/multiple annotation joins and compare candidate target policies without overwriting labels. Return affected content IDs, annotation provenance and policy consequences in the existing thread. Do not assume two annotation rows are independent rating samples. Owner, reviewer and exact output paths remain to be assigned; aggregation policy requires user decision after GPT's synthesis.

Evidence goes in existing topic threads or an assigned audit output, not a new competing design document. Mark `done` only after linked evidence and reviewer disposition satisfy the criteria; unresolved research choices remain explicitly pending. Existing threads' `VERIFIED` tags describe their authors' checks, not GPT's independent verification.

---

## 📋 한국어

GPT가 배정하고 각 AI는 공유 파일을 독점 편집할 수 있을 때 자기 행만 갱신한다. [협업 규칙](README.md)을 따른다. 위 표의 기존 작업 상태를 보존했으며 이번 갱신은 job 실행이나 과학적 선택 승인이 아니다. `doing` 전 담당자·검토자·정확한 수정 경로를 정한다. `unassigned`는 실행 준비가 안 된 상태다. 작업판은 잠금이 아니다.

상태는 `todo` 대기 · `doing` 진행 · `review` 검토 · `blocked` 차단 · `done` 완료다. 위 영한 작업표가 단일 상태 원본이다. T001과 T003은 미배정이며 T002는 Claude Code 제안을 Codex가 검토하는 상태다.

### 산출물과 완료 기준

- **T004/T005:** 전달문의 P0–P3 순서와 수정 경로를 따른다. 동등한 기존 구현이 있으면 중복 모듈보다 재사용을 우선하며 경로 변경 전 소유권을 정한다. T004는 검토된 batch/manifest 계약과 제한된 개발 subset을, T005는 synthetic 검사와 CPU 기준모델 계획부터 반환하고 모델/probe 경로를 구현한다. 코드 준비·실제 실행·과학적 검증의 상태를 구분한다. 제공된 guard는 로컬 synthetic 검사 11개가 통과했으며 서버 학습은 아직 주장하지 않는다. T004가 T003 문제를 조사하더라도 target 정책 승인 권한은 없다. 근거 경로와 함께 작업판에 반환하며 작업판 편집도 직렬화한다.

- **T001:** 먼저 v2 run별 마스크와 필터링 전 신호·QC 자료 위치를 확인한다. 스레드는 Perlmutter에 run 마스크가 없다고 보고한다. 09 §4.1–4.2에 따라 atlas·마스크 분모를 맞춘 coverage 및 추가 voxel 품질 비교를 코드 커밋·run 출처와 함께 반환한다. 촬영 저신호와 교집합 제외를 분리하며 예전 MNI 감사 수치를 v2 근거로 대체하지 않는다. 실행 전 정확한 출력 경로와 독립 검토자를 배정해야 한다. 여기서 마스크 threshold 변경을 승인하지 않는다.
- **T002:** Codex가 연결된 스레드의 Claude Code 제안·근거를 검토한다. 1349/1363 동일성, crosswalk 차이와 split 그룹을 재현 가능하게 확인하고 자료 버전을 반환한다. 내용 동일성 확인과 저자가 제외한 이유는 구분하며 후자는 별도 근거가 필요하다. Horikawa의 두 제시를 모두 유지할지는 사용자 결정으로 남긴다. 검토 중 split 변경이나 sample 제외를 하지 않는다.
- **T003:** canonical mapping 검토 후 annotation의 누락·다중 연결을 조사하고 label을 덮어쓰지 않은 채 target 정책 후보를 비교한다. 영향받는 content ID·annotation 출처·정책별 결과를 기존 스레드에 반환한다. 두 annotation 행이 독립 평정 표본이라고 가정하지 않는다. 담당자·검토자·정확한 출력 경로는 아직 미배정이며 통합 정책은 GPT 종합 후 사용자가 결정한다.

근거는 기존 주제 스레드나 배정된 감사 산출물에 두며 경쟁하는 설계 문서를 만들지 않는다. 연결된 근거와 검토 결과가 기준을 충족해야 `done`으로 바꾸고 미결 연구 선택은 별도로 남긴다. 기존 스레드의 `VERIFIED`는 작성자의 검사이며 GPT의 독립 검증을 뜻하지 않는다.
