# FEEL Research Operating Workflows

This folder defines how FEEL should run as an AI-assisted research
project. These workflows are not extra narrative documents; they are operating
protocols.

## Workflow Map

| Intent | Use |
|---|---|
| Literature or dataset expansion | `literature_sota_workflow.md` |
| Turning an idea into runnable experiments | `experiment_planning_workflow.md` |
| Stress-testing a claim or strategy | `red_blue_team_review.md` |
| Weekly synthesis and project management | `weekly_update_workflow.md` |

## Natural-Language Triggers

| Trigger | Action |
|---|---|
| `[deep search]` | search external literature/code/data and update reference docs |
| `[experiment card]` | create a structured experiment card from a model idea |
| `[red team]` | generate multi-reviewer critique and blue-team response |
| `[weekly status]` | build a status report from git changes and canonical docs |
| `[verification]` | run path, completeness, and overclaim checks |

## Required Checks

Run before committing research-operations changes:

```bash
python3 scripts/check_md_completeness.py
python3 scripts/build_project_status.py
git status --short
```
