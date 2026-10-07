# EmoBrain project instructions

_Current working rules · updated 2026-10-07_

---

## 📍 English

### Authority and scope

Start with [docs/current/00_README.md](docs/current/00_README.md). Current explicit user decisions take precedence over an approved freeze manifest, then the accepted principles in docs/current. Proposals and unresolved entries are not automatically approved. Record changes to an actual preregistration as amendments, not retroactive freezes.

The former root rules, paper_logic_merged, project contracts and September review are historical. Their archived instructions do not govern new work. Reference literature and existing code do not independently define the current protocol.

Read [implementation status](docs/current/08_IMPLEMENTATION_STATUS.md) before execution. A documentation update is not evidence of implementation or successful validation. Inspect the server's actual commit and uncommitted changes before changing it. Preserve other contributors' work.

`prereg_v2/design_docs/` contains audit-era design snapshots, not a competing current protocol. Preserve those snapshots; audit code, manifests and results in `prereg_v2/` remain evidence to review, not automatically accepted design decisions.

### Coordination and roles

- **GPT** is the user's research-idea and study-design coordinator: discuss the story, models and analyses with the user; synthesize independent checks; maintain `docs/current`, decision records and work assignments.
- **Claude Code** and **Codex** are server verification, implementation and experiment agents. Both may challenge ideas with evidence. Neither independently replaces the agreed study design.
- **The user** makes final decisions on core research direction and material changes. Routine verification and implementation within already authorized scope do not require a new user decision for every step.
- These names identify project roles, not the application hosting a conversation. Use GPT for this coordinating conversation and Codex for the dedicated coding agent, as requested by the user.
- Read [coordination rules](docs/coordination/README.md), [the board](docs/coordination/BOARD.md) and relevant open threads at session start. Threads are proposals and evidence, not automatic approvals or job-launch authorization.
- Work only on assigned paths. Shared files, including the board and implementation status, need a single writer at a time. In the shared Perlmutter checkout, serialize the whole update/stage/commit/push sequence; explicit staging alone does not isolate the shared index. Do not run concurrent Git-writing operations or force-push.

### Rationale before inclusion

Before adding or changing a model, feature, target, loss, control, analysis, statistical test, visualization or interpretation, answer:

1. What scientific question does it answer?
2. What alternative explanation remains without it?
3. Which literature or verified data supports it?
4. Why choose it over plausible alternatives?
5. Which result would change its inclusion or interpretation?
6. What cannot be claimed from it?

Without these answers, do not add it to the primary design. Novelty, popularity, capacity or performance alone is not a rationale. Distinguish architecture, objective, training data and capacity differences from psychological constructs. Evaluate claims neutrally; distinguish verified facts, user reports, proposals and uncertainty. State the evidence that changes a judgment.

### Execution boundaries

- Protect canonical stimulus/run boundaries, nested teacher OOF and train-only transforms.
- Do not substitute normative labels for scanned participants' self-reports.
- Do not infer learned content or neural causality from prediction/attention alone.
- No imagery, new LLM backbone or foundation-model construction without a new scope decision.
- GPU jobs are user-run unless explicitly authorized. No full training, test-driven selection, new downloads or raw-data uploads as part of documentation maintenance.
- Do not overwrite server changes, delete original data/results or silently reuse old caches under new protocol names.

### Repository hygiene

- Maintain one source of study truth in docs/current with stable filenames.
- Put superseded design material in docs/archive; use Git history for ordinary revisions.
- Do not create dated current-document copies, duplicated all-in-one files, ZIPs, backup files or reports in the repository root.
- Store server audit outputs together under project/output/audits; link evidence rather than duplicating data.
- Keep root README, CLAUDE and CONTEXT as navigation, not competing specifications.
- Keep replies and README prose concise. Omit obvious visual descriptions, editing commentary and repetitive caveats; keep methodological qualifications in the relevant design documents.
- Write newly created or revised README-style contributor documentation in English first, followed by a clearly separated Korean version in the same file. Use matching section order, preserve equivalent technical meaning, and update both languages together; the Korean version must not omit caveats or unresolved status. Do not create separate translation files or rewrite archived originals just for translation.
- This work uses a temporary local checkout; do not create a persistent Mac project checkout or rearrange the user's local research folder.
- Continue documentation, code and experiment-related work on `docs/unify-study-design-20261006`. Keep main unchanged until experiments have been run, major design decisions and results have been reviewed, and the user explicitly approves a merge. Do not create a PR without authorization.

---

## 📍 한국어

### 기준과 범위

[docs/current/00_README.md](docs/current/00_README.md)부터 읽는다. 현재 사용자의 명시적 결정, 승인된 freeze manifest, docs/current의 확정 원칙 순으로 우선한다. 제안과 미확정 항목은 자동 승인되지 않는다. 실제 사전등록 변경은 소급 동결이 아니라 amendment로 기록한다.

이전 루트 규칙, paper_logic_merged, project 계약과 9월 검토는 역사 기록이며 새 작업을 지배하지 않는다. 참고문헌과 기존 코드만으로 현재 프로토콜을 정하지 않는다.

실행 전 [구현 상태](docs/current/08_IMPLEMENTATION_STATUS.md)를 읽는다. 문서 갱신이 구현·검증 완료의 증거는 아니다. 서버를 수정하기 전에 실제 커밋과 미커밋 변경을 확인하고 다른 작업자의 변경을 보존한다.

`prereg_v2/design_docs/`는 감사 당시 설계 사본이며 별도의 최신 프로토콜이 아니다. 사본을 보존한다. `prereg_v2/`의 감사 코드·manifest·결과는 검토할 근거이지 자동 승인된 설계 결정이 아니다.

### 협업과 역할

- **GPT**는 사용자와 연구 아이디어·설계를 논의하는 총괄이다. 스토리·모델·분석을 논의하고 독립 검증을 종합하며 `docs/current`, 결정 기록과 작업 배정을 관리한다.
- **Claude Code**와 **Codex**는 서버 검증·구현·실험 담당이다. 둘 다 근거를 들어 아이디어에 이견을 낼 수 있지만 합의된 연구 설계를 독자적으로 대체하지 않는다.
- **사용자**가 핵심 연구 방향과 중요한 변경을 최종 결정한다. 이미 승인된 범위의 일상적인 검증·구현은 단계마다 새 결정을 받지 않는다.
- 명칭은 대화를 실행하는 앱이 아니라 프로젝트 역할을 구분한다. 사용자 요청에 따라 이 총괄 대화는 GPT, 코드 전용 에이전트는 Codex로 표기한다.
- 세션 시작 시 [협업 규칙](docs/coordination/README.md), [작업판](docs/coordination/BOARD.md), 관련 열린 스레드를 읽는다. 스레드는 제안·근거이며 자동 승인이나 job 실행 허가가 아니다.
- 배정된 경로만 수정한다. 작업판·구현 상태 등 공유 파일은 한 번에 한 작성자만 수정한다. Perlmutter 공유 사본에서는 갱신·stage·commit·push 전체를 직렬 실행한다. 경로를 명시해 stage하는 것만으로 공유 index가 분리되지는 않는다. Git 쓰기 동시 실행과 force push는 금지한다.

### 포함 전 근거

모델·feature·target·loss·control·분석·통계 검정·시각화·해석을 추가하거나 변경하기 전에 다음에 답한다.

1. 답하는 과학적 질문은 무엇인가?
2. 없으면 어떤 대안 설명을 배제할 수 없는가?
3. 어떤 문헌 또는 검증된 데이터가 뒷받침하는가?
4. 가능한 대안 중 왜 이것을 선택하는가?
5. 어떤 결과가 포함 여부나 해석을 바꾸는가?
6. 이것으로 주장할 수 없는 것은 무엇인가?

답이 없으면 primary design에 넣지 않는다. 최신성·유명세·용량·성능만으로는 근거가 되지 않는다. 구조·목적함수·학습 데이터·용량 차이를 심리적 구성개념 차이와 구별한다. 중립적으로 판단하고 확인한 사실·사용자 보고·제안·불확실성을 구분하며 판단을 바꾼 근거를 밝힌다.

### 실행 경계

- canonical stimulus/run 경계, nested teacher OOF와 train-only 변환을 보호한다.
- normative label을 촬영 참가자의 자기보고로 대체하지 않는다.
- 예측·attention만으로 학습된 내용이나 신경 인과성을 추론하지 않는다.
- 새 범위 결정 없이 imagery, 새 LLM backbone, foundation model 구축을 추가하지 않는다.
- 명시적으로 승인받지 않은 GPU job은 사용자가 실행한다. 문서 정리 작업에 전체 학습, test 기반 선택, 새 다운로드나 원자료 업로드를 포함하지 않는다.
- 서버 변경을 덮어쓰거나 원자료·결과를 삭제하거나 바뀐 프로토콜 이름으로 과거 cache를 몰래 재사용하지 않는다.

### 저장소 정리

- 안정적인 파일명으로 docs/current에 연구 기준을 하나만 유지한다.
- 폐기된 설계는 docs/archive에 두고 일반 수정 이력은 Git으로 남긴다.
- 날짜별 current 사본·중복 통합본·ZIP·백업 파일·루트 보고서를 만들지 않는다.
- 새 서버 감사 산출물은 project/output/audits 아래에 모으고 데이터 복제 대신 근거를 연결한다.
- 루트 README·CLAUDE·CONTEXT는 안내문이지 경쟁하는 명세가 아니다.
- 답변과 README는 간결하게 쓴다. 자명한 도식 설명·편집 중계·반복 경고는 생략하고 방법론적 한계는 해당 설계 문서에 둔다.
- 새로 쓰거나 수정하는 README형 협업 문서는 같은 파일 안에 영문 다음 한글로 구분한다. 절 순서와 기술적 의미·주의점·미확정 상태를 일치시키고 함께 갱신한다. 별도 번역 파일이나 번역만을 위한 과거 원본 재작성을 만들지 않는다.
- 로컬은 임시 checkout만 사용한다. Mac에 영구 사본을 만들거나 사용자의 로컬 연구 폴더를 재배치하지 않는다.
- 문서·코드·실험 관련 작업은 `docs/unify-study-design-20261006`에서 계속한다. 실험과 주요 설계·결과 검토 후 사용자가 명시적으로 merge를 승인하기 전까지 main은 변경하지 않는다. 승인 없이 PR을 만들지 않는다.
