> ⚠️ **ARCHIVED — 역사 기록. 현행 문서가 아니다.**
> 현행 논증 = `docs/paper_logic_merged.md` (대전제 · RQ · 가설 H1–H4). 운영 규칙 = `CLAUDE.md`.
>
> 아래 내용 중 다음은 **뒤집혔다.** (a) Qwen3-VL 등 LLM backbone 사용 — 금지.
> (b) open-vocabulary / cross-taxonomy 전이를 headline novelty 로 삼는 프레임 — 폐기.
> (c) 학습에 없던 감정 zero-shot — 폐기(원칙적 분할 기준 없음, RQ 와 무관).
> (d) "EmoBrain 과 EmoViS 는 별도 논문 2편" — 현재는 **한 편의 논문**.
> (e) "EmoBrain 은 cortical location 을 주장하지 않는다" — 현재 **H3 이 cortical location 주장**이다.

# Weekly Update Workflow

Purpose: produce a compact weekly project status without re-reading every
Markdown file.

## Inputs

- `git log --oneline --since="7 days ago"`
- `git status --short`
- canonical docs:
  - `CONTEXT_EMOBRAIN.md`
  - `notes/project_decisions.md`
  - `reference/datasets.md`
  - `reference/training_strategy.md`
  - `reports/status/PROJECT_STATUS.md`

## Steps

1. Run:

```bash
python3 scripts/check_md_completeness.py
python3 scripts/build_project_status.py
```

2. Summarize:
   - new references,
   - new dataset/model decisions,
   - experiment cards created,
   - blockers,
   - next three actions.
3. Save the weekly note under `reports/weekly/YYYY-MM-DD_weekly_update.md` only
   when the user asks for a durable weekly report.

## Output Format

```markdown
## This Week

## Decisions

## New Evidence

## Blockers

## Next 3 Actions

## Files Changed
```
