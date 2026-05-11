# NetFeeliX

**Neural nETwork For Emotion rEpresentation Learning and Inference in NeuroX**

> Building an emotion-specific brain foundation model through benchmark-driven search.

Korean guide: [`README_KR.md`](README_KR.md)
Research overview: [`research_overview.md`](research_overview.md)
Action plan: [`ACTION_PLAN.md`](ACTION_PLAN.md)

NetFeeliX is an attempt to build a brain model that captures emotion
representations: not just "predict an emotion label," but learn fMRI
representations that track affect, appraisal, context, and multimodal
naturalistic experience.

The first deliverable is a large `Dataset x BFM x Task` benchmark matrix. That
matrix is not the final goal. It is the search-space narrowing stage that tells
us which datasets, BFMs, targets, windows, and baselines contain usable signal
before we commit to larger model-development tracks.

---

## Project Thesis

The final goal is an **emotion-specific brain foundation model**: a brain model
whose representations preserve emotion-relevant structure across datasets,
stimuli, subjects, and target types.

Emotion representation is unlikely to be solved by attaching a small emotion
head to a generic resting-state brain foundation model. Emotion during
naturalistic experience depends on the interaction between multimodal stimulus
dynamics, subject-specific brain dynamics, task context, and affective labels
or ratings. NetFeeliX therefore treats emotion representation learning as a
brain-model search problem over:

```text
brain foundation model + task/movie fMRI learning signal + multimodal stimulus context + emotion targets
```

The project is **SwiFT-first but not SwiFT-locked**. The immediate benchmark
compares emotion-fMRI datasets, brain foundation models, and emotion tasks:

```text
Emotion fMRI Dataset x Brain Foundation Model x Emotion Task
```

The current BFM axis is:

- SwiFT,
- Brain-JEPA,
- NeuroSTORM,
- BrainLM.

For model details, input formats, first checks, risks, and source links, see
`reference/code_resources.md` and `reference/papers.md`.

Logistic/ridge/ROI/voxel models are statistical floors, not the main Model
Axis. Video/audio/text stimulus-only models, TRIBE v2, multimodal fusion, and
movie/story pretraining are later branches.

After the benchmark, the roadmap splits into two major search tracks:

1. **Pretraining and adaptation strategy**
   - Use task-related or movie fMRI rather than only resting fMRI.
   - Test loss terms such as masked fMRI modeling, future/JEPA-style latent
     prediction, contrastive objectives, target-aware emotion supervision, and
     subject-invariant learning.
   - Compare frozen probes, adapters, late-block fine-tuning, affective pooling,
     and multi-task emotion heads.

2. **Multimodal brain-stimulus framework**
   - Use video/audio/text models as controls, teachers, or context providers.
   - Test TRIBE-like stimulus-to-brain alignment, late fusion between video and
     brain models, and injection of video/text/audio embeddings into brain
     foundation models.
   - Ask whether multimodal context improves emotion representation beyond
     brain-only BFM features and beyond stimulus-only shortcuts.

The benchmark stage exists so these branches are not chosen by taste. We run
the broad grid first, then narrow the search space with evidence.

## Core Research Question

**How can we develop a brain foundation model that best captures
emotion-relevant representation across naturalistic fMRI datasets and emotion
tasks?**

Subquestions:

- Benchmark phase: which Dataset x BFM x Task cells are runnable, blocked, or
  invalid?
- Baseline phase: which BFMs beat logistic/ridge/ROI/voxel statistical floors
  under matched splits and metrics?
- Target phase: which emotion targets are stable enough to drive model
  development: arousal, valence, category, multi-label, high-dimensional
  vector, dynamic/binning, or component/appraisal?
- Pretraining phase: does task/movie fMRI pretraining improve emotion transfer
  beyond generic resting/general BFM transfer?
- Multimodal phase: does video/audio/text context or TRIBE-like alignment
  improve brain emotion representations beyond brain-only and stimulus-only
  shortcuts?

## Working Hypotheses

**H1. Resting-state BFM transfer is useful but incomplete.** Existing brain foundation models should provide nontrivial baselines, but their pretraining distribution may underrepresent stimulus-locked affective dynamics.

**H2. The first decision should be empirical, not architectural.** Fill the
Dataset x BFM x Task matrix before choosing adapters, pretraining, fusion, or
alignment.

**H3. Arousal may generalize more robustly than valence.** This must be checked
across BFM and dataset cells before building a larger model around it.

**H4. Task/movie fMRI pretraining is a central candidate.** If frozen BFMs are
weak or narrow, NetFeeliX should test whether task-related or naturalistic movie
fMRI objectives create more emotion-sensitive brain representations.

**H5. Multimodal context may be necessary but must be controlled.** Video,
audio, and text features may help emotion representation, but stimulus-only
shortcuts must be measured before claiming brain-specific emotion modeling.

## Key Model Families

| Family | Examples | Input | Role in NetFeeliX |
|---|---|---|---|
| Current BFM benchmark | SwiFT | fMRI volumes | Primary BFM |
| Current BFM benchmark | Brain-JEPA | fMRI or ROI time series | Alternative BFM |
| Current BFM benchmark | NeuroSTORM | raw 4D fMRI | Alternative 4D BFM |
| Current BFM benchmark | BrainLM | ROI/time-series fMRI | Alternative time-series BFM |
| Statistical floors | logistic/ridge/ROI/voxel models | pooled BFM or simple brain features | Minimum comparison |
| Pretraining/adaptation branch | task/movie fMRI objectives, adapters, affective heads | fMRI volumes or time series | Search track after benchmark |
| Multimodal branch | TRIBE v2, V-JEPA2, CLIP, Whisper, text encoders | video/audio/text + fMRI | Stimulus controls, fusion, alignment, and feature injection |

## Immediate Decision-Driven Strategy

1. **Master benchmark matrix**
   - Build the `Dataset x BFM x Task` table in `notes/benchmark_design.md`.
   - Mark cells as `RUN`, `CHECK`, or `NA`.
   - Use emotion-fMRI benchmark datasets only.
   - For the dataset/model/task cheat sheets inside the matrix, see
     `notes/benchmark_design.md`.

2. **Dataset and target readiness**
   - Build canonical Horikawa 2185-stimulus manifest.
   - Confirm Emo-FilM, Affective Videos, IAPS fMRI, NeuroEmo, Koide-Majima, and
     REELMO / Jojo Rabbit fMRI where usable.
   - Define target matrices, splits, metrics, and statistical floors.
   - For dataset content, targets, risks, and source links, see
     `reference/datasets.md`.
   - For task definitions and metrics, see `reference/task.md`.

3. **BFM evaluation**
   - Compare SwiFT, Brain-JEPA, NeuroSTORM, and BrainLM under matched conditions.
   - Fill `Dataset | BFM | Task | Target | Split | Metric | Statistical floor |
     BFM score | Status | Decision`.
   - For BFM/model details, see `reference/code_resources.md` and
     `reference/papers.md`.

4. **Post-benchmark model search**
   - Choose between two main branches:
     1. pretraining/adaptation strategy for the brain model,
     2. multimodal brain-stimulus framework.
   - Keep both branches evidence-driven: benchmark result first, model
     modification second.
   - For post-benchmark adaptation/pretraining strategy, see
     `reference/training_strategy.md`.

## Where To Find Details

The README is only the entry point. Details live in these files:

| Need | File |
|---|---|
| What each benchmark dataset is | `reference/datasets.md` |
| What each BFM/model is | `reference/code_resources.md`, `reference/papers.md` |
| What each task/metric means | `reference/task.md` |
| Current `Dataset x BFM x Task` table | `notes/benchmark_design.md` |
| What to do after the matrix is filled | `reference/training_strategy.md`, `ACTION_PLAN.md` |

## Repository Structure

```text
NetFeeliX/
├── README.md
├── README_KR.md
├── ACTION_PLAN.md
├── ONBOARDING.md
├── CONTEXT_NETFEELIX.md
├── CLAUDE.md
├── CODEX.md
├── Paper/
│   ├── framework_EN.md
│   ├── framework_KR.md
│   └── methodology.md
├── reference/
│   ├── datasets.md
│   ├── task.md
│   ├── training_strategy.md
│   ├── systematic_reference_map.md
│   ├── papers.md
│   ├── code_resources.md
│   └── search_log_2026-05-08.md
├── notes/
│   ├── benchmark_design.md
│   └── project_decisions.md
├── templates/
│   ├── paper_note.md
│   ├── dataset_card.md
│   ├── experiment_card.md
│   ├── model_card.md
│   ├── review_card.md
│   └── decision_log.md
├── workflows/
│   ├── README.md
│   ├── literature_sota_workflow.md
│   ├── experiment_planning_workflow.md
│   ├── red_blue_team_review.md
│   └── weekly_update_workflow.md
├── scripts/
│   ├── README.md
│   ├── check_md_completeness.py
│   ├── build_project_status.py
│   └── generate_experiment_cards.py
├── reports/
│   ├── weekly/
│   ├── reviews/
│   └── status/
├── code/
│   ├── README.md
│   └── tools/
│       └── check_dataset_inventory.py
└── setup/
    ├── README.md
    ├── code/
    │   ├── build_horikawa_window_manifest.py
    │   ├── run_tribe_horikawa.py
    │   └── run_tribe_horikawa.sh
    ├── data/
    ├── logs/
    └── results/
```

## Current Planning Documents

- `ONBOARDING.md`: first-read guide for new collaborators and AI agents.
- `CONTEXT_NETFEELIX.md`: compact single source of truth for project framing.
- `ACTION_PLAN.md`: current execution plan and phase-level next actions.
- `Paper/framework_EN.md` and `Paper/framework_KR.md`: canonical project framework, narrative, and proposal-level framing.
- `Paper/methodology.md`: detailed experimental plan.
- `reference/datasets.md`: function-based dataset inventory.
- `reference/task.md`: task inventory and target definitions.
- `reference/training_strategy.md`: SwiFT-first training and model-development strategy.
- `reference/systematic_reference_map.md`: organized reference map by conceptual role.
- `notes/benchmark_design.md`: `Dataset x BFM x Task` master matrix.
- `templates/`: reusable note/card templates for papers, datasets, models, experiments, reviews, and decisions.
- `workflows/`: operating protocols for literature search, experiment planning, red-team review, and weekly updates.
- `scripts/`: project-operation automation only.
- `setup/code/`: runnable setup/experiment scripts.

Project completeness and status can be checked with:

```bash
python3 scripts/check_md_completeness.py
python3 scripts/build_project_status.py
```
