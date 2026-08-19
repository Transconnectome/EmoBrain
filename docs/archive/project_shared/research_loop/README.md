> ⚠️ **ARCHIVED — 역사 기록. 현행 문서가 아니다.**
> 현행 논증 = `docs/paper_logic_merged.md` (대전제 · RQ · 가설 H1–H4). 운영 규칙 = `CLAUDE.md`.
>
> 아래 내용 중 다음은 **뒤집혔다.** (a) Qwen3-VL 등 LLM backbone 사용 — 금지.
> (b) open-vocabulary / cross-taxonomy 전이를 headline novelty 로 삼는 프레임 — 폐기.
> (c) 학습에 없던 감정 zero-shot — 폐기(원칙적 분할 기준 없음, RQ 와 무관).
> (d) "EmoBrain 과 EmoViS 는 별도 논문 2편" — 현재는 **한 편의 논문**.
> (e) "EmoBrain 은 cortical location 을 주장하지 않는다" — 현재 **H3 이 cortical location 주장**이다.

# research_loop — EmoBrain near-autonomous research loop

GPT-5.4 ↔ Maria 구조의 in-silico 버전 운영 폴더. 가설을 상태로 관리하고, 매 라운드
실험 결과를 evidence 로 연결해 over-claim 을 구조적으로 막는다.

## 구성

| 파일 | 역할 |
|------|------|
| `hypothesis_ledger.md` | 모든 가설의 상태 backbone. 라운드별 가설·점수·critic 판정·job-id·결과. |
| (명령어) `/emobrain-loop` | 오케스트레이터. `~/.claude/commands/emobrain-loop.md`. |

## 루프 한 바퀴

```
목표(Gate)
  → [나] 가설 6~10개 생성
  → [나] 루브릭 점수 → [critic] 적대적 검증 → ranked shortlist
  → [GATE 1: 사용자] 1라운드 가설 선택
  → [emovi-coder/-code-reviewer] .py + .sh 실험 grid
  → [GATE 2: 사용자] sbatch 승인
  → NERSC 실행 (= Maria)
  → [나] "무엇을 의미하는가" 해석 → ledger 갱신 → 후속 가설
  → (다음 라운드)
```

사용자 결정권은 **가설 선택**과 **sbatch 승인** 두 곳. 나머지는 자율 (smoke test 까지).

## status 흐름

`proposed → shortlisted → running(job-id) → done → confirmed | refuted | parked`

- `confirmed` 는 반드시 run output 경로(evidence)를 가진다. evidence 없는 confirmed 금지.
- `parked` = 지금은 안 돌리지만 폐기 아님 (후속 라운드 후보).

## 시작

```
/emobrain-loop "<반증 가능한 Gate 문장>" dir=D1
```
