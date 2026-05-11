# NetFeeliX Onboarding

This file is the first stop for a new collaborator or AI agent. NetFeeliX is a
SwiFT-first but not SwiFT-locked model-development project aiming for an
emotion-specific brain foundation model. The immediate artifact is the
`Dataset x BFM x Task` master benchmark matrix, but that matrix is the first
search-space narrowing step rather than the final project scope.

## Five-Minute Read Order

1. `README.md`
   - Project thesis, model families, active strategy, and repository map.
2. `README_KR.md`
   - Korean guide for the project structure and workflow.
3. `CONTEXT_NETFEELIX.md`
   - Single source of truth for project framing and operating rules.
4. `ACTION_PLAN.md`
   - Current execution plan and near-term research actions.
5. `notes/benchmark_design.md`
   - Current `Dataset x BFM x Task` master matrix.
6. `Paper/framework_EN.md`
   - Canonical narrative and proposal-level framework.
7. `Paper/methodology.md`
   - Experimental plan and benchmark matrix.
8. `reference/training_strategy.md`
   - SwiFT-first model-development strategy.
9. `reference/datasets.md`
   - Function-based dataset inventory and dataset details.
10. `reference/code_resources.md`
   - BFM/model details and implementation resources.
11. `workflows/README.md`
   - How literature, experiment planning, review, and weekly updates should run.

## Project Identity

NetFeeliX stands for:

```text
Neural nETwork For Emotion rEpresentation Learning and Inference in NeuroX
```

The project should not be presented as an emotion theory paper or as a benchmark
paper only. It is a model-development project that first compares brain
foundation models across emotion-fMRI datasets and tasks, then uses that
evidence to choose between two larger tracks:

1. task/movie-fMRI pretraining and brain-model adaptation, and
2. multimodal brain-stimulus frameworks such as TRIBE-like alignment, late
   fusion, or stimulus-feature injection.

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

1. Build the `Dataset x BFM x Task` master matrix.
2. Use emotion-fMRI datasets: Horikawa, Emo-FilM, Affective Videos, IAPS,
   NeuroEmo, Koide-Majima/Nishimoto, and REELMO / Jojo Rabbit fMRI if usable.
3. Compare BFMs: SwiFT, Brain-JEPA, NeuroSTORM, and BrainLM.
4. Cover tasks: binary, regression, multiclass, multi-label, high-dimensional
   vector, dynamic/binning, and component/appraisal where valid.
5. Add logistic/ridge/ROI/voxel statistical floors for each runnable cell.
6. Use the matrix to narrow the search space, then branch into:
   pretraining/adaptation strategy or multimodal brain-stimulus framework.
