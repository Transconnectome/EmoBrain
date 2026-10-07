# Agent coordination

_Asynchronous channel for the user, ChatGPT (coordinator), Claude Code and Codex · created 2026-10-07_

[English](#english) · [한국어](#한국어)

## English

### Purpose and scope

The agents cannot talk in real time; each runs only when the user invokes it. This folder is where they leave requests, evidence, reviews and decision requests for one another. It is a communication log, not study truth. The study design lives in [docs/current](../current/00_README.md); decisions are recorded in [04_DECISION_REGISTER](../current/04_DECISION_REGISTER.md). [AGENTS.md](../../AGENTS.md) governs everything here.

### Roles and ownership

| Who | Where | Owns | Does not |
| --- | --- | --- | --- |
| User | — | decisions, invoking agents | — |
| ChatGPT (coordinator) | GitHub | `docs/current/*`, `AGENTS.md`, task assignment in `BOARD.md` | run server jobs |
| Claude Code | Perlmutter | files listed under its tasks; `project/output/audits/claude/`; existing `prereg_v2/` | edit `docs/current/*` except `08_IMPLEMENTATION_STATUS.md` with evidence |
| Codex | Perlmutter | files listed under its tasks; `project/output/audits/codex/` | edit `docs/current/*` except `08_IMPLEMENTATION_STATUS.md` with evidence |

Comment on another agent's files in a thread; do not edit them.

### Shared checkout rules (Claude Code and Codex use the same Perlmutter checkout)

The checkout is `/pscratch/sd/s/sjmoon/EmoBrain` on `docs/unify-study-design-20261006`.

1. Never switch branches, `reset`, `stash`, `clean`, rebase or `checkout -- <file>` on files you do not own. Another agent may have uncommitted work.
2. Stage explicit paths only. No `git add -A`, `git add .` or `git commit -a`.
3. Before starting, set your task to `doing` in `BOARD.md` and list the files you will touch. Do not touch files listed under another agent's `doing` task.
4. Update from GitHub with `git pull --ff-only`. Never use `--autostash`; it would stash the other agent's work. If fast-forward fails, stop and post in a thread.
5. Prefix commit subjects with `[claude]`, `[codex]` or `[gpt]`. Never force-push.
6. If `.git/index.lock` exists, wait and retry. Remove it only when no git process is running.

### Threads

One topic per file: `threads/T###-short-slug.md`. The first line is the status: `OPEN`, `DECISION-NEEDED` or `CLOSED`. Append entries; do not rewrite earlier ones.

```
### YYYY-MM-DD HH:MM · <from> → <to> · <type>
Claim:
Evidence: <path / command / commit> (VERIFIED | REPORTED)
Request:
```

Entry types: `REQUEST`, `REVIEW-REQUEST`, `AGREE`, `DISAGREE` (evidence required), `NEEDS-INFO`, `DECISION-NEEDED` (to the user). Disagreements are settled by evidence, not by vote. Only the user decides; the coordinator then records the decision in the register and sets the thread to `CLOSED`.

### Session start checklist

1. Read `AGENTS.md`, then `BOARD.md`.
2. Read open threads addressed to you.
3. `git status` and `git log -5` to see others' uncommitted and recent work.

---

## 한국어

### 목적과 범위

세 AI 는 실시간으로 대화할 수 없고, 사용자가 부를 때만 실행된다. 이 폴더는 서로에게 요청, 근거, 검토, 결정 요청을 남기는 곳이다. 연구 기준 문서가 아니라 소통 기록이다. 연구 설계는 [docs/current](../current/00_README.md) 에, 결정은 [04_DECISION_REGISTER](../current/04_DECISION_REGISTER.md) 에 있다. 이 폴더도 [AGENTS.md](../../AGENTS.md) 를 따른다.

### 역할과 파일 소유

| 누구 | 위치 | 맡는 것 | 하지 않는 것 |
| --- | --- | --- | --- |
| 사용자 | — | 결정, AI 호출 | — |
| ChatGPT (총괄) | GitHub | `docs/current/*`, `AGENTS.md`, `BOARD.md` 작업 배정 | 서버 작업 실행 |
| Claude Code | Perlmutter | 자기 작업에 적힌 파일, `project/output/audits/claude/`, 기존 `prereg_v2/` | `docs/current/*` 수정 (`08_IMPLEMENTATION_STATUS.md` 만 근거를 붙여 예외) |
| Codex | Perlmutter | 자기 작업에 적힌 파일, `project/output/audits/codex/` | `docs/current/*` 수정 (`08_IMPLEMENTATION_STATUS.md` 만 근거를 붙여 예외) |

다른 AI 의 파일에 대한 의견은 스레드에 쓰고, 그 파일을 직접 고치지 않는다.

### 공유 사본 규칙 (Claude Code 와 Codex 는 Perlmutter 의 같은 사본을 쓴다)

사본은 `/pscratch/sd/s/sjmoon/EmoBrain`, 브랜치는 `docs/unify-study-design-20261006` 이다.

1. 브랜치 전환, `reset`, `stash`, `clean`, rebase, 자기 소유가 아닌 파일의 `checkout -- <file>` 을 하지 않는다. 다른 AI 의 커밋 안 된 작업이 있을 수 있다.
2. 경로를 명시해서만 stage 한다. `git add -A`, `git add .`, `git commit -a` 금지.
3. 시작 전에 `BOARD.md` 에서 자기 작업을 `doing` 으로 바꾸고 건드릴 파일을 적는다. 다른 AI 의 `doing` 작업에 적힌 파일은 건드리지 않는다.
4. GitHub 갱신은 `git pull --ff-only` 로 한다. `--autostash` 는 다른 AI 의 작업을 stash 하므로 쓰지 않는다. fast-forward 가 안 되면 멈추고 스레드에 쓴다.
5. 커밋 제목 앞에 `[claude]`, `[codex]`, `[gpt]` 를 붙인다. force push 금지.
6. `.git/index.lock` 이 있으면 기다렸다가 다시 시도한다. git 프로세스가 없을 때만 지운다.

### 스레드

주제 하나에 파일 하나, `threads/T###-짧은-이름.md`. 첫 줄은 상태(`OPEN`, `DECISION-NEEDED`, `CLOSED`)다. 글은 아래에 덧붙이기만 하고 이전 글을 고치지 않는다.

```
### YYYY-MM-DD HH:MM · <보낸 쪽> → <받는 쪽> · <종류>
주장:
근거: <경로 / 명령 / 커밋> (VERIFIED | REPORTED)
요청:
```

종류는 `REQUEST`, `REVIEW-REQUEST`, `AGREE`, `DISAGREE` (근거 필수), `NEEDS-INFO`, `DECISION-NEEDED` (사용자에게) 다. 의견이 갈리면 투표하지 않고 근거로 가린다. 결정은 사용자만 하고, 총괄이 결정 기록에 반영한 뒤 스레드를 `CLOSED` 로 바꾼다.

### 세션 시작 순서

1. `AGENTS.md`, 그다음 `BOARD.md` 를 읽는다.
2. 자기 앞으로 열린 스레드를 읽는다.
3. `git status`, `git log -5` 로 다른 AI 의 커밋 안 된 작업과 최근 작업을 확인한다.
