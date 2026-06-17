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
