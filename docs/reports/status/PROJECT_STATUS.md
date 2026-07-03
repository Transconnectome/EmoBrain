# EmoBrain Project Status

Generated: 2026-07-01 06:47 UTC

## Git

- Branch: `main`
- Last commit: `6c51fd3 Pivot to single-project framework novelty path`
- Working tree: `M ACTION_PLAN.md
 M CLAUDE.md
 M CODEX.md
 M CONTEXT_EMOBRAIN.md
 M ONBOARDING.md
 M Paper/framework_EN.md
 M Paper/framework_KR.md
 M README.md
 M README_KR.md
 M docs/masterplan_v3_emobrain.md
 M docs/notes/architecture_design_20260629.md
 M docs/notes/project_decisions.md
 M docs/reports/status/PROJECT_STATUS.md
 M project/README.md
 M tools/build_project_status.py
 M tools/check_md_completeness.py
?? docs/notes/ppt_outline_20260630.md
?? docs/notes/redteam_review_20260630.md`

## Canonical Direction

- SwiFT is the default brain backbone.
- TRIBE v2 is a stimulus-to-brain teacher/baseline/alignment component.
- HCP 7T movie is the main naturalistic fMRI continued-pretraining source.
- Horikawa and Emo-FilM are the primary downstream emotion datasets.

## Inventory Counts

- Dataset entries in `docs/reference/datasets.md`: 17
- Approximate paper table rows in `docs/reference/papers.md`: 0
- Approximate code-resource table rows in `docs/reference/code_resources.md`: 0

## Recent Commits

```text
6c51fd3 Pivot to single-project framework novelty path
1d2749d [CONTEXT] Rename CONTEXT_FEEL.md → CONTEXT_EMOBRAIN.md, rewrite ONBOARDING.md, fix CODEX.md
e205135 [SETUP] Rename FEELIN→EmoBrain, submodule BrainVLM/fMRI-LM, D1/D2 scaffolding
d4537a3 [FRAMING] 3-direction pivot. D1 BrainVLM + D2 fMRI-LM (main) + D3 CCN (separate)
9f6ec33 [DESIGN] Direction 1 + Direction 2 design.md with fMRI-LM reference
```

## Next Operating Checks

```bash
python3 tools/check_md_completeness.py
python3 tools/build_project_status.py
```
