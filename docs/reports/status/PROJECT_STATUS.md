# EmoBrain Project Status

Generated: 2026-07-07 00:54 UTC

## Git

- Branch: `main`
- Last commit: `266240c [REFACTOR] Adopt implementation_spec + physical archive of v5 Three Directions`
- Working tree: `M ACTION_PLAN.md
 M CONTEXT_EMOBRAIN.md
 M ONBOARDING.md
 M Paper/framework_EN.md
 M Paper/framework_KR.md
 M README.md
 M README_KR.md
 M docs/notes/architecture_design_20260629.md
 M docs/notes/implementation_spec_20260702.md
 M docs/notes/project_decisions.md
 M project/README.md
 T project/shared/data/cowen_horikawa_labels.csv
?? project/__init__.py
?? project/data/
?? project/evaluation/
?? project/models/
?? project/scripts/
?? project/shared/data/caption_ck20.csv
?? project/training/
?? project/utils/`

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
266240c [REFACTOR] Adopt implementation_spec + physical archive of v5 Three Directions
4054164 [SPEC] Adopt implementation_spec_20260702 as canonical code spec
6c51fd3 Pivot to single-project framework novelty path
1d2749d [CONTEXT] Rename CONTEXT_FEEL.md → CONTEXT_EMOBRAIN.md, rewrite ONBOARDING.md, fix CODEX.md
e205135 [SETUP] Rename FEELIN→EmoBrain, submodule BrainVLM/fMRI-LM, D1/D2 scaffolding
```

## Next Operating Checks

```bash
python3 tools/check_md_completeness.py
python3 tools/build_project_status.py
```
