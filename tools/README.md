# EmoBrain Scripts

Scripts here support project operations across the repository. Initial runnable
experiments should live under `project/shared/code/`.

## Current Scripts

| Script | Purpose |
|---|---|
| `check_md_completeness.py` | checks required docs, old broken references, dataset entry fields, and trigger/workflow presence |
| `build_project_status.py` | (미사용) 옛 `docs/reports/status/PROJECT_STATUS.md` 생성기. 그 산출물은 2026-08-19 정리에서 삭제됨 |
| `generate_experiment_cards.py` | creates experiment-card skeletons from templates |

Runnable setup/experiment scripts live in `project/shared/code/`, not here.

## Common Commands

```bash
python3 scripts/check_md_completeness.py
python3 scripts/build_project_status.py
python3 scripts/generate_experiment_cards.py --id NFx-001 --title "Frozen SwiFT Horikawa probe"
```

## Rule

Do not store large data outputs here. Use `data`, `project/shared/output/logs`, and
`results` for initial experiments.
