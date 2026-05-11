# NetFeeliX

**Neural nETwork For Emotion rEpresentation Learning and Inference in NeuroX**

> Emotion representation learning with brain foundation models and naturalistic fMRI.

Korean guide: [`README_KR.md`](README_KR.md)
Research overview: [`research_overview.md`](research_overview.md)
Action plan: [`ACTION_PLAN.md`](ACTION_PLAN.md)

NetFeeliX studies how to make SwiFT and related brain models more emotion-specific, with a focus on naturalistic fMRI, emotion representation learning, and stimulus-brain-emotion alignment.

---

## Project Thesis

Emotion representation is unlikely to be solved by attaching a small emotion head to a generic resting-state brain foundation model. Emotion during naturalistic experience depends on the interaction between multimodal stimulus dynamics, subject-specific brain dynamics, and affective labels or ratings. NetFeeliX therefore treats emotion representation learning as a three-way alignment problem:

```text
naturalistic stimulus dynamics + fMRI brain dynamics + emotion annotations
```

The project is **SwiFT-first but not SwiFT-locked** and compares four families of approaches:

1. **SwiFT emotion specialization.** Adapt SwiFT with emotion heads, adapters, subject modules, continued pretraining, and targeted fine-tuning.
2. **Neural representation search.** Test ROI/parcel, voxel-weighted, network-restricted, dynamic-FC, and whole-brain representations.
3. **Naturalistic and emotion-labeled pretraining.** Compare naturalistic SSL, emotion-labeled training, and two-stage curricula.
4. **Stimulus-brain-emotion alignment.** Use TRIBE v2 and other multimodal stimulus models as teachers or alignment components.

## Core Research Question

**What model architecture and learning objective best support transferable emotion representation learning from naturalistic fMRI?**

Subquestions:

- Do resting-state fMRI foundation models transfer to emotion prediction, or do they miss naturalistic affective dynamics?
- Does stimulus-locked movie/story fMRI pretraining improve sample efficiency and generalization on small emotion fMRI datasets?
- Are emotion labels better predicted from brain-only representations, stimulus-only representations, or jointly aligned stimulus-brain representations?
- Which downstream targets are more transferable: arousal, valence, discrete emotion categories, or high-dimensional emotion embeddings?

## Working Hypotheses

**H1. Resting-state BFM transfer is useful but incomplete.** Existing brain foundation models should provide nontrivial baselines, but their pretraining distribution may underrepresent stimulus-locked affective dynamics.

**H2. Naturalistic pretraining may improve emotion transfer.** The hypothesis is not simply that movie beats rest. HCP movie-watching fMRI tests whether stimulus-locked visual/audio/social dynamics help emotion transfer; CNeuroMod, StudyForrest, Narratives, and modality-control movie data test alignment, long-context, language-context, and modality-specific variants of the same question.

**H3. Arousal will generalize more robustly than valence.** This follows recent movie-watching fMRI evidence that dynamic connectivity predicts arousal across datasets more reliably than valence.

**H4. Stimulus-brain alignment should be necessary for high-dimensional emotion.** TRIBE-style multimodal encoders can capture semantic, audio, and visual context that brain-only BFM objectives may not learn from small downstream datasets.

## Key Model Families

| Family | Examples | Input | Output | Role in NetFeeliX |
|---|---|---|---|---|
| 4D fMRI backbone | SwiFT | fMRI volumes | task label or representation | Baseline fMRI encoder |
| Resting-to-task prediction | SwiFUN | resting-state fMRI | task activation map | Bridge from intrinsic dynamics to emotion reactivity |
| fMRI foundation model | BrainLM, Brain-JEPA, NeuroSTORM, Omni-fMRI | fMRI time series or 4D fMRI | transferable brain representation | Existing pretrained BFM baseline |
| Brain encoding model | TRIBE, TRIBE v2 | video/audio/text stimulus | predicted fMRI response | Stimulus-to-brain comparison and alignment target |
| NetFeeliX | proposed | fMRI + optional stimulus features | emotion-aware brain representation | Project target |

## Immediate Decision-Driven Strategy

1. **Data and target readiness**
   - Build canonical Horikawa 2185-stimulus manifest.
   - Confirm Emo-FilM, Affective Videos, IAPS fMRI, HCP, and alignment datasets.
   - Define target matrices, splits, and metrics.

2. **Neural representation search**
   - Compare ROI/parcel, voxel-weighted, network-restricted, dynamic-FC, and
     whole-brain representations.
   - Identify which regions/networks/time windows carry emotion signal.

3. **SwiFT and BFM evaluation**
   - Test frozen/adapted/pretrained SwiFT under matched conditions.
   - Compare Brain-JEPA, NeuroSTORM, BrainLM/SwiFUN if feasible.
   - Pivot if simple or alternative representations outperform SwiFT.

4. **Pretraining and alignment**
   - Compare naturalistic SSL, emotion-labeled pretraining, and two-stage
     curricula.
   - Compare brain-only, stimulus-only, and stimulus-brain aligned models.

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
- `notes/benchmark_design.md`: initial benchmark axes, experiments, and decision rules.
- `templates/`: reusable note/card templates for papers, datasets, models, experiments, reviews, and decisions.
- `workflows/`: operating protocols for literature search, experiment planning, red-team review, and weekly updates.
- `scripts/`: project-operation automation only.
- `setup/code/`: runnable setup/experiment scripts.

Project completeness and status can be checked with:

```bash
python3 scripts/check_md_completeness.py
python3 scripts/build_project_status.py
```
