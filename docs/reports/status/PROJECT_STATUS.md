# FEEL Project Status

Generated: 2026-05-11 12:16 UTC

## Git

- Branch: `main`
- Last commit: `a7434aa Translate research overview to Korean`
- Working tree: `M .gitignore
 M ACTION_PLAN.md
 M CLAUDE.md
 M CODEX.md
 M CONTEXT_FEEL.md
 D NARRATIVE_KR.md
 M ONBOARDING.md
 M Paper/framework_EN.md
 M Paper/framework_KR.md
 M Paper/methodology.md
 M README.md
 M README_KR.md
 M code/README.md
 D notes/two_month_plan.md
 M reference/task.md
 M reference/training_strategy.md
 M research_overview.md
 M scripts/README.md
 M scripts/check_md_completeness.py
?? "FEEL Research Overview.txt"
?? reports/scientist_FEEL_20260511.md
?? scripts/scientist_ai.py
?? scripts/scientist_ai.sh
?? code/build_horikawa_window_manifest.py
?? code/run_tribe_horikawa.py
?? code/run_tribe_horikawa.sh`

## Canonical Direction

- SwiFT is the default brain backbone.
- TRIBE v2 is a stimulus-to-brain teacher/baseline/alignment component.
- HCP 7T movie is the main naturalistic fMRI continued-pretraining source.
- Horikawa and Emo-FilM are the primary downstream emotion datasets.

## Inventory Counts

- Dataset entries in `reference/datasets.md`: 16
- Approximate paper table rows in `reference/papers.md`: 0
- Approximate code-resource table rows in `reference/code_resources.md`: 0

## Recent Commits

```text
a7434aa Translate research overview to Korean
5b30b47 Add detailed research overview
24657ba Add affective computing task taxonomy
3b42391 Clarify naturalistic pretraining rationale
99fdab9 Add Korean project narrative
```

## Next Operating Checks

```bash
python3 scripts/check_md_completeness.py
python3 scripts/build_project_status.py
```
