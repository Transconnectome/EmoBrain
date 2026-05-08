# Experiment Planning Workflow

Purpose: convert broad model ideas into runnable experiments with clear decision
rules.

## Inputs

- Model idea or dataset question.
- `reference/datasets.md`
- `reference/task.md`
- `reference/training_strategy.md`
- `Paper/methodology.md`

## Steps

1. Choose the dataset function.
   - direct emotion-labeled fMRI,
   - movie-watching pretraining,
   - stimulus-to-brain alignment,
   - static-image affect transfer,
   - physiology/context extension.
2. Choose the target.
   - arousal, valence, discrete category, high-dimensional vector,
     appraisal/component, retrieval/alignment.
3. Define comparable model conditions.
   - simple baseline,
   - frozen SwiFT,
   - adapted SwiFT,
   - stimulus-only,
   - TRIBE-teacher or aligned model.
4. Define the split and metric before running.
5. Create an experiment card from `templates/experiment_card.md`.
6. Store planned cards under `reports/status/` until a study-specific folder is
   created.
7. When code exists, move runnable scripts into `study{N}/code/` and outputs to
   `study{N}/results/`.

## Required Decision Rule

Every experiment must answer one of:

- continue SwiFT frozen/adapted transfer,
- invest in HCP movie continued pretraining,
- prioritize TRIBE-SwiFT alignment,
- use stimulus-side affective LLM/VLM supervision,
- stop because dataset/target is not useful.

## Output

- one experiment card,
- one short decision entry in `notes/project_decisions.md` when the experiment
  changes priorities.
