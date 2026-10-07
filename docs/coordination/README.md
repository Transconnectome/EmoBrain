# Agent coordination

_GPT coordinates research; Claude Code and Codex verify and implement · updated 2026-10-07_

---

## 📋 English

### Purpose and document authority

This folder holds asynchronous requests, evidence and reviews. Updating a file does not wake another agent; do not assume live communication or delivery without a separate authorized mechanism. Follow [root AGENTS.md](../../AGENTS.md).

| Location | Role |
| --- | --- |
| `docs/current/` | Current study design: accepted, proposed and unresolved items remain distinct |
| `docs/coordination/` | Work assignments, discussion and evidence review |
| `prereg_v2/design_docs/` | Preserved audit-era design snapshots, not the current protocol |
| `prereg_v2/` audit code/results | Existing evidence; importing it does not approve old settings |

### Roles and ownership

| Role | Responsibility | Write scope |
| --- | --- | --- |
| User | Core research direction and material changes | Final approval when required |
| GPT | Discuss ideas with the user; synthesize reviews; coordinate study design | Current documents, root rules, coordination rules and assignments |
| Claude Code | Verification, implementation and authorized experiments | Explicitly assigned code and audit outputs |
| Codex | Verification, implementation and authorized experiments | Explicitly assigned code and audit outputs |

GPT is the coordinator's project name regardless of its host application; Codex names the dedicated coding agent. Neither server agent owns an entire directory by default. Preserve existing authorship, but specify paths for each new task. Comment on another owner's files in a thread instead of editing them; GPT may explicitly reassign ownership.

The board, threads and `08_IMPLEMENTATION_STATUS.md` are shared surfaces: one writer at a time. Server agents may record evidence-backed implementation status within assigned scope, but cannot use a status update to change the study design.

### From proposal to accepted design

1. The user and GPT discuss the idea. GPT records the proposal and specific verification questions in a topic thread.
2. Claude Code and/or Codex return evidence, limitations and reproducible outputs. Resolve disagreement through evidence, not votes or role seniority.
3. GPT synthesizes findings. Routine verification, bug fixes and implementation of already authorized specifications may proceed within scope without another user decision for every step.
4. Escalate core research questions, primary analyses, target/split/exclusion rules, material protocol changes, substantial new compute, destructive actions and unresolved consequential choices to the user. Assignment does not override execution permissions.
5. GPT records accepted research decisions in [04_DECISION_REGISTER.md](../current/04_DECISION_REGISTER.md), updates affected current documents and links the disposition in the thread. A proposal or review alone is not protocol approval.

### Shared checkout and Git safety

The reported shared Perlmutter checkout is `/pscratch/sd/s/sjmoon/EmoBrain`. Work only on `docs/unify-study-design-20261006`; no main changes, PRs or merges to main without explicit user approval.

1. Inspect `git status`, recent commits and the board before editing. Declare exact paths and preserve unrelated work. Do not switch branches, reset, stash, clean or rewrite history in the shared checkout.
2. Serialize the entire update → stage → commit → push sequence. Confirm by explicit handoff that the other session is not writing Git or shared files. A `doing` row is not a lock. If exclusive access cannot be established, defer the write operation.
3. During that exclusive window, update with `git pull --ff-only` only when active edits will not be disturbed. No automatic rebase or autostash. If fast-forward or push fails, fetch and review divergence; never force-push or overwrite others' work.
4. Stage explicit paths only; no `git add -A`, `git add .` or `git commit -a`. Inspect the staged diff. If someone else's changes are staged, stop; do not commit or unstage them.
5. Serialize shared-file edits even for different board rows or appended replies. Prefix commits with `[gpt]`, `[claude]` or `[codex]` and include the resulting commit in the handoff.
6. `.git/index.lock` is Git's lock, not the collaboration protocol. Do not delete it automatically. Establish that a persistent lock is stale and obtain explicit approval before removing it.

This is a manual protocol, not an installed lock or scheduler. Do not create extra worktrees, lock scripts or branches as part of this documentation update.

### Threads and evidence

Keep the existing `threads/T###-topic.md` files. Append corrections and reviews without rewriting previous entries. The status marker may change to `OPEN`, `DECISION-NEEDED` or `CLOSED` with a linked disposition.

```text
### YYYY-MM-DD HH:MM TZ · GPT / Claude Code / Codex → recipient · TYPE
Claim or question:
Evidence: repository-relative path + commit; run ID/config/data version where applicable
Verification: VERIFIED by whom and how / REPORTED by whom / PROPOSED / UNKNOWN
Result and limits:
Request or next action:
```

Types: `REQUEST`, `REVIEW-REQUEST`, `AGREE`, `DISAGREE`, `NEEDS-INFO`, `DECISION-NEEDED`, `RESOLVED`. Another author's `VERIFIED` tag does not mean the reader independently verified it. Include a timezone; do not invent missing run IDs. Concise review entries may be Korean; contributor rules remain English then Korean.

Close routine tasks after acceptance criteria and review are met. Close decision-dependent tasks only after the required decision is recorded. Silence is not approval.

### Session start and handoff

Read root AGENTS → this README → [BOARD](BOARD.md) → relevant open threads → linked current specifications. Check the actual checkout state before writing and re-read updated instructions after syncing. Return the task ID, commit, inspected evidence, unresolved issues and next action. Pushing a message does not establish that its recipient has read it.

---

## 📋 한국어

### 목적과 문서 우선순위

이 폴더는 비동기 요청·근거·검토를 남기는 곳이다. 파일 갱신만으로 다른 AI가 실행되지는 않는다. 별도로 승인된 수단 없이 실시간 소통이나 전달 완료를 가정하지 않는다. [루트 AGENTS.md](../../AGENTS.md)를 따른다.

| 위치 | 역할 |
| --- | --- |
| `docs/current/` | 현재 연구 설계. 확정·제안·미확정을 구분 |
| `docs/coordination/` | 작업 배정·논의·근거 검토 |
| `prereg_v2/design_docs/` | 감사 당시 설계 사본. 현재 프로토콜이 아님 |
| `prereg_v2/` 감사 코드·결과 | 기존 근거. 가져왔다고 과거 설정을 승인한 것은 아님 |

### 역할과 파일 소유

| 역할 | 책임 | 수정 범위 |
| --- | --- | --- |
| 사용자 | 핵심 연구 방향과 중요한 변경 | 필요한 사항의 최종 승인 |
| GPT | 사용자와 아이디어 논의·검토 종합·연구 설계 총괄 | 최신 문서·루트 지침·협업 규칙·작업 배정 |
| Claude Code | 검증·구현·승인된 실험 | 명시적으로 배정된 코드·감사 산출물 |
| Codex | 검증·구현·승인된 실험 | 명시적으로 배정된 코드·감사 산출물 |

GPT는 실행 앱과 무관한 총괄 역할명이고 Codex는 코드 전용 AI다. 서버 AI 어느 쪽에도 디렉토리 전체 소유권을 자동 부여하지 않는다. 기존 작성 기록을 보존하되 새 작업별 경로를 지정한다. 다른 담당자의 파일은 직접 수정 대신 스레드로 검토하며 GPT가 소유권을 명시적으로 재배정할 수 있다.

작업판·스레드·`08_IMPLEMENTATION_STATUS.md`는 공유 문서이므로 한 번에 한 작성자만 수정한다. 서버 AI는 배정 범위 안에서 근거가 있는 구현 상태를 기록할 수 있지만 상태 갱신으로 연구 설계를 바꿀 수 없다.

### 제안에서 확정 설계까지

1. 사용자와 GPT가 아이디어를 논의한다. GPT가 제안과 구체적 검증 질문을 해당 스레드에 남긴다.
2. Claude Code 또는 Codex가 근거·한계·재현 가능한 산출물을 반환한다. 이견은 투표나 역할 서열이 아니라 근거로 판단한다.
3. GPT가 결과를 종합한다. 이미 승인된 명세의 일반 검증·버그 수정·구현은 범위 안에서 단계마다 새 사용자 결정을 받을 필요가 없다.
4. 핵심 연구 질문, 주 분석, target·split·제외 규칙, 중요한 프로토콜 변경, 큰 추가 계산, 파괴적 작업, 해결되지 않은 중대한 선택은 사용자에게 올린다. 배정이 실행 권한을 넘어서지는 않는다.
5. GPT가 승인된 연구 결정을 [04_DECISION_REGISTER.md](../current/04_DECISION_REGISTER.md)에 기록하고 관련 current 문서를 갱신하며 처리 결과를 스레드에 연결한다. 제안이나 검토만으로 프로토콜이 승인되지 않는다.

### 공유 사본과 Git 안전

보고된 Perlmutter 공유 사본은 `/pscratch/sd/s/sjmoon/EmoBrain`이다. `docs/unify-study-design-20261006`에서만 작업한다. 명시적 사용자 승인 없이 main 변경·PR 생성·main 병합을 하지 않는다.

1. 편집 전 `git status`·최근 커밋·작업판을 확인한다. 담당 경로를 명시하고 무관한 작업을 보존한다. 공유 사본에서 브랜치 전환·reset·stash·clean·이력 재작성을 하지 않는다.
2. 갱신 → stage → commit → push 전체를 직렬 실행한다. 명시적인 인계로 다른 세션이 Git·공유 파일을 쓰지 않는지 확인한다. `doing` 표시는 잠금이 아니다. 독점 사용을 확인할 수 없으면 쓰기를 미룬다.
3. 독점 작업 시간에 진행 중인 편집을 방해하지 않는 상태에서 `git pull --ff-only`로 갱신한다. 자동 rebase·autostash는 금지한다. fast-forward나 push 실패 시 fetch 후 차이를 검토하며 force push나 덮어쓰기로 해결하지 않는다.
4. 경로를 명시해서만 stage한다. `git add -A`, `git add .`, `git commit -a`는 금지한다. staged diff를 확인한다. 다른 AI의 변경이 이미 stage되어 있으면 멈추고 함께 커밋하거나 stage에서 빼지 않는다.
5. 다른 행 수정·답글 추가도 공유 파일이면 직렬 편집한다. 커밋 접두사는 `[gpt]`, `[claude]`, `[codex]`를 쓰고 인계 시 커밋을 포함한다.
6. `.git/index.lock`은 Git 잠금이지 협업 프로토콜이 아니다. 자동 삭제하지 않는다. 계속 남아 있으면 사용 중이 아닌 잠금인지 확인하고 명시적 승인을 받아 삭제한다.

이는 수동 규칙이며 잠금 장치나 스케줄러를 설치한 것이 아니다. 이번 문서 갱신으로 추가 worktree·잠금 스크립트·브랜치를 만들지 않는다.

### 스레드와 근거

기존 `threads/T###-topic.md`를 유지한다. 정정·검토는 덧붙이고 이전 글을 다시 쓰지 않는다. 상태 표시는 처리 결과를 연결하며 `OPEN`, `DECISION-NEEDED`, `CLOSED`로 바꿀 수 있다.

```text
### YYYY-MM-DD HH:MM TZ · GPT / Claude Code / Codex → 수신자 · TYPE
주장 또는 질문:
근거: 저장소 상대 경로 + 커밋; 해당하면 run ID/config/데이터 버전
확인 상태: VERIFIED 누가 어떻게 확인 / REPORTED 누구의 보고 / PROPOSED / UNKNOWN
결과와 한계:
요청 또는 다음 작업:
```

종류는 `REQUEST`, `REVIEW-REQUEST`, `AGREE`, `DISAGREE`, `NEEDS-INFO`, `DECISION-NEEDED`, `RESOLVED`다. 다른 작성자의 `VERIFIED`가 독자의 독립 검증을 뜻하지는 않는다. 시간대를 기록하고 없는 run ID를 만들지 않는다. 짧은 검토 글은 한글로 써도 되며 협업 지침은 영문 다음 한글로 쓴다.

일반 작업은 완료 기준과 검토 충족 후 종료한다. 결정 의존 작업은 필요한 결정을 기록한 뒤 종료한다. 침묵은 승인이 아니다.

### 세션 시작과 인계

루트 AGENTS → 이 README → [BOARD](BOARD.md) → 관련 열린 스레드 → 연결된 최신 명세 순으로 읽는다. 수정 전 실제 사본 상태를 확인하고 동기화 후 바뀐 지침을 다시 읽는다. 작업 ID·커밋·검토한 근거·미해결 사항·다음 작업을 반환한다. 메시지를 push했다고 상대 AI가 읽었다고 보고하지 않는다.
