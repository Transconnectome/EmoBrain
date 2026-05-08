# NetFeeliX Onboarding

This file is the first stop for a new collaborator or AI agent. NetFeeliX is a
SwiFT-first model-development project for emotion-specific fMRI representation
learning.

## Five-Minute Read Order

1. `README.md`
   - Project thesis, model families, two-month strategy, and repository map.
2. `README_KR.md`
   - Korean guide for the project structure and workflow.
3. `CONTEXT_NETFEELIX.md`
   - Single source of truth for project framing and operating rules.
4. `Paper/framework_EN.md`
   - Canonical narrative and proposal-level framework.
5. `Paper/methodology.md`
   - Experimental plan and benchmark matrix.
6. `reference/training_strategy.md`
   - SwiFT-first model-development strategy.
7. `reference/datasets.md`
   - Function-based dataset inventory.
8. `workflows/README.md`
   - How literature, experiment planning, review, and weekly updates should run.

## Project Identity

NetFeeliX stands for:

```text
Neural nETwork For Emotion rEpresentation Learning and Inference in NeuroX
```

The project should not be presented as an emotion theory paper. It is a model
development project asking how SwiFT can be adapted, pretrained, or aligned with
stimulus models to improve emotion representation learning from naturalistic
fMRI.

## What To Do Before Adding New Files

1. Check whether the content belongs in an existing canonical document.
2. Use a template in `templates/` when adding a paper, dataset, model,
   experiment, review, or decision.
3. Run:

```bash
python3 scripts/check_md_completeness.py
```

4. Update `reports/status/PROJECT_STATUS.md` through:

```bash
python3 scripts/build_project_status.py
```

## Default Workflows

| Intent | Workflow |
|---|---|
| Find new papers or datasets | `workflows/literature_sota_workflow.md` |
| Turn an idea into runnable experiments | `workflows/experiment_planning_workflow.md` |
| Stress-test a strategy or model claim | `workflows/red_blue_team_review.md` |
| Summarize project progress | `workflows/weekly_update_workflow.md` |

## Immediate Scientific Path

1. Horikawa: high-dimensional affect geometry.
2. Emo-FilM: naturalistic emotion/component/appraisal targets.
3. HCP 7T movie: continued pretraining for SwiFT.
4. Affective Videos and IAPS fMRI: fast valence/arousal/category checks.
5. TRIBE v2: stimulus-side teacher, baseline, and alignment component.
6. REELMO: long-context affect trajectories and rationale/cue targets.
7. NSD + OASIS: static-image affect transfer branch only if useful.
