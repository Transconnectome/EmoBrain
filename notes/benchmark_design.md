# NetFeeliX Benchmark Design

This note defines the first benchmark master matrix.

The first deliverable is not a sequence of experiments. It is one large table
that enumerates:

```text
Emotion fMRI Dataset x Brain Foundation Model x Emotion Task
```

Then we run through the table and fill in status, metrics, failures, and
decisions.

## Scope

Current benchmark:

- emotion/affect fMRI datasets,
- brain foundation models,
- emotion/affect prediction tasks,
- minimal statistical floors for comparison.

Not current benchmark:

- video-only, audio-only, text-only, or stimulus-only emotion prediction,
- TRIBE/stimulus-brain alignment,
- HCP/CNeuroMod/StudyForrest/Narratives as pretraining sources,
- adapter/fine-tuning/pretraining/fusion strategies.

Those come after the BFM benchmark table tells us which dataset, BFM, and task
combinations are worth expanding.

## Where Details Live

This file is the benchmark control table. It should be readable by itself, but
the full descriptions live elsewhere:

| Thing | Quick view here | Full detail |
|---|---|---|
| Dataset meaning, subjects, stimuli, targets, risks | Dataset cheat sheet below | `reference/datasets.md` |
| BFM meaning, input format, output, risks, source links | BFM cheat sheet below | `reference/code_resources.md`, `reference/papers.md` |
| Task definitions and metrics | Task Axis below | `reference/task.md` |
| Training/adaptation/pretraining after benchmark | After The Master Matrix below | `reference/training_strategy.md` |

## Axes

### Dataset Axis

| Dataset | Benchmark role | Tier |
|---|---|---|
| Horikawa/Cowen | core short-video affect geometry benchmark | P0 |
| Emo-FilM | naturalistic emotion/component/appraisal benchmark | P0 |
| Affective Videos | fast valence/arousal sanity benchmark | P1 |
| IAPS fMRI | static image valence/category beta-map benchmark | P1 |
| NeuroEmo | secondary categorical emotion benchmark | P2 |
| Koide-Majima/Nishimoto | secondary high-dimensional emotion benchmark | P2 |
| REELMO / Jojo Rabbit fMRI | one-movie dynamic/context benchmark; 60-movie part is behavioral/stimulus-side | P2 |

### Dataset Cheat Sheet

| Dataset | What it is | Why it is in the matrix | First detail to check | Full detail |
|---|---|---|---|---|
| Horikawa/Cowen | fMRI responses to 2,185 short emotion-evoking videos; n=5, TR=2s, 61 runs | core high-dimensional affect geometry benchmark | canonical 2,185 stimuli, exact BIDS run volumes, HRF/window policy | `reference/datasets.md` |
| Emo-FilM | 30 participants watching 14 short films; TR=1.3s; local MRIQC mean about 9,563 film volumes/subject | naturalistic emotion, component, appraisal, dynamic target benchmark | access, annotation timing, dummy volumes, target reliability | `reference/datasets.md` |
| Affective Videos | Kim et al. 2016 PLOS ONE / OpenfMRI ds000205; 11 participants, 32 five-second audiovisual clips, TR=2.2s, 128 main trials | fast low-dimensional valence/arousal sanity benchmark | paper/task design, OpenfMRI format, exact run volumes, TR/event timing | `reference/datasets.md` |
| IAPS fMRI | NeuroVault beta maps from 56 participants; original TR=2.5s but current input is condition beta maps | static image valence/category benchmark | beta-map format and how to adapt BFM input | `reference/datasets.md` |
| NeuroEmo | BIDS fMRI from 40 participants watching emotional Bollywood clips; task TR=3s, about 200 task volumes | secondary multiclass/cross-cultural emotion benchmark | event files, exact NIfTI shape, stimulus access, label mapping | `reference/datasets.md` |
| Koide-Majima/Nishimoto | emotional audiovisual movie fMRI; n=8, TR=2s, 18 runs, 5,490 volumes/subject | secondary high-dimensional movie-emotion benchmark | data access and timing/label format | `reference/datasets.md` |
| REELMO / Jojo Rabbit fMRI | 60-movie affect-report dataset plus Jojo Rabbit-only fMRI subset; fMRI n=20, TR=2s, 3,087 volumes/participant | dynamic/context benchmark for the one fMRI movie; later stimulus-side trajectory source | download/access, BIDS layout, 8-run timing, dummy/overlap handling, group-label alignment | `reference/datasets.md` |

Excluded from the benchmark dataset axis:

| Resource | Reason |
|---|---|
| HCP 7T movie | pretraining source, not emotion-labeled downstream |
| CNeuroMod / Algonauts | pretraining/alignment source |
| StudyForrest | pretraining/context source |
| Narratives | pretraining/language-context source |
| 101 Dalmatians | modality-control pretraining source |

### Brain Foundation Model Axis

| BFM | Input style | Current use |
|---|---|---|
| SwiFT | 4D fMRI volume windows | primary BFM |
| Brain-JEPA | fMRI/ROI time series, depending on implementation | alternative BFM |
| NeuroSTORM | raw 4D fMRI windows | alternative 4D BFM |
| BrainLM | ROI/time-series fMRI | alternative time-series BFM |

`SwiFUN` is not included in the benchmark matrix because it is not a direct
emotion-fMRI BFM candidate for this table.

### BFM Cheat Sheet

| BFM | What it is | Why it is in the matrix | First detail to check | Full detail |
|---|---|---|---|---|
| SwiFT | Swin-style 4D fMRI transformer from the local Transconnectome ecosystem | primary modifiable fMRI backbone | checkpoint native sequence length, input shape, pooling | `reference/code_resources.md`, `reference/training_strategy.md` |
| Brain-JEPA | JEPA-style brain representation model using predictive latent learning/spatiotemporal masking | alternative BFM and objective precedent | ROI/time-series format, mask actually used, weights/code availability | `reference/code_resources.md`, `reference/papers.md` |
| NeuroSTORM | large-scale raw 4D fMRI foundation model | alternative 4D BFM against SwiFT | code/weight availability, padding/pooling, input volume format | `reference/code_resources.md`, `reference/papers.md` |
| BrainLM | ROI/time-series fMRI foundation model based on masked prediction | alternative time-series BFM | atlas/ROI format, checkpoint availability, downstream feature shape | `reference/code_resources.md`, `reference/papers.md` |

### Task Axis

| Task | Target examples | Metrics |
|---|---|---|
| Binary classification | high/low valence, high/low arousal, positive vs negative | AUROC, balanced accuracy, macro F1 |
| Regression | valence, arousal, dominance, intensity | Pearson r, Spearman r, MAE/MSE |
| Multiclass classification | positive/neutral/negative, discrete emotion | balanced accuracy, macro F1 |
| Multi-label prediction | multiple emotion labels or probabilities | macro/micro F1, macro AUROC |
| High-dimensional vector prediction | 34D or 80D emotion vector | mean Pearson/Spearman, RSA/CKA |
| Dynamic/binning regression | time-windowed affect bin or trajectory | CCC, lagged correlation, binned accuracy |
| Component/appraisal prediction | appraisal, motivation, expression, physiology, feeling | correlation, MAE/MSE |

## Master Matrix Codes

Each cell in the master matrix is a benchmark combination.

| Code | Meaning |
|---|---|
| `RUN` | run this combination in the benchmark if the model loads |
| `CHECK` | possible, but requires format/timing/access check first |
| `NA` | not a valid task for this dataset |

## Dataset x BFM x Task Master Matrix

| Dataset | BFM | Binary | Regression | Multiclass | Multi-label | High-dim vector | Dynamic/binning | Component/appraisal |
|---|---|---|---|---|---|---|---|---|
| Horikawa/Cowen | SwiFT | RUN | RUN | CHECK | RUN | RUN | NA | NA |
| Horikawa/Cowen | Brain-JEPA | RUN | RUN | CHECK | RUN | RUN | NA | NA |
| Horikawa/Cowen | NeuroSTORM | RUN | RUN | CHECK | RUN | RUN | NA | NA |
| Horikawa/Cowen | BrainLM | RUN | RUN | CHECK | RUN | RUN | NA | NA |
| Emo-FilM | SwiFT | CHECK | RUN | CHECK | RUN | CHECK | RUN | RUN |
| Emo-FilM | Brain-JEPA | CHECK | RUN | CHECK | RUN | CHECK | RUN | RUN |
| Emo-FilM | NeuroSTORM | CHECK | RUN | CHECK | RUN | CHECK | RUN | RUN |
| Emo-FilM | BrainLM | CHECK | RUN | CHECK | RUN | CHECK | RUN | RUN |
| Affective Videos | SwiFT | RUN | RUN | CHECK | NA | NA | NA | NA |
| Affective Videos | Brain-JEPA | RUN | RUN | CHECK | NA | NA | NA | NA |
| Affective Videos | NeuroSTORM | RUN | RUN | CHECK | NA | NA | NA | NA |
| Affective Videos | BrainLM | RUN | RUN | CHECK | NA | NA | NA | NA |
| IAPS fMRI | SwiFT | RUN | CHECK | RUN | NA | NA | NA | NA |
| IAPS fMRI | Brain-JEPA | RUN | CHECK | RUN | NA | NA | NA | NA |
| IAPS fMRI | NeuroSTORM | RUN | CHECK | RUN | NA | NA | NA | NA |
| IAPS fMRI | BrainLM | RUN | CHECK | RUN | NA | NA | NA | NA |
| NeuroEmo | SwiFT | RUN | CHECK | RUN | CHECK | NA | CHECK | NA |
| NeuroEmo | Brain-JEPA | RUN | CHECK | RUN | CHECK | NA | CHECK | NA |
| NeuroEmo | NeuroSTORM | RUN | CHECK | RUN | CHECK | NA | CHECK | NA |
| NeuroEmo | BrainLM | RUN | CHECK | RUN | CHECK | NA | CHECK | NA |
| Koide-Majima/Nishimoto | SwiFT | CHECK | CHECK | CHECK | RUN | RUN | CHECK | NA |
| Koide-Majima/Nishimoto | Brain-JEPA | CHECK | CHECK | CHECK | RUN | RUN | CHECK | NA |
| Koide-Majima/Nishimoto | NeuroSTORM | CHECK | CHECK | CHECK | RUN | RUN | CHECK | NA |
| Koide-Majima/Nishimoto | BrainLM | CHECK | CHECK | CHECK | RUN | RUN | CHECK | NA |
| REELMO / Jojo Rabbit fMRI | SwiFT | CHECK | CHECK | CHECK | CHECK | CHECK | RUN | CHECK |
| REELMO / Jojo Rabbit fMRI | Brain-JEPA | CHECK | CHECK | CHECK | CHECK | CHECK | RUN | CHECK |
| REELMO / Jojo Rabbit fMRI | NeuroSTORM | CHECK | CHECK | CHECK | CHECK | CHECK | RUN | CHECK |
| REELMO / Jojo Rabbit fMRI | BrainLM | CHECK | CHECK | CHECK | CHECK | CHECK | RUN | CHECK |

This table is the object we conquer. Each non-`NA` cell should eventually get:

- target definition,
- split,
- input format,
- statistical floor,
- BFM score,
- notes/failure reason,
- decision.

## Statistical Floors

These are not BFMs. They are run beside each dataset-task combination so the
BFM scores have a minimum reference point.

| Task | Floor model |
|---|---|
| Binary classification | logistic regression |
| Multiclass classification | multinomial logistic regression |
| Regression | ridge regression |
| Multi-label prediction | one-vs-rest logistic or ridge, depending on target |
| High-dimensional vector prediction | multi-output ridge |
| Dynamic/binning regression | ridge or logistic on binned windows |
| Component/appraisal prediction | multi-output ridge |

## Result Table Schema

Every filled cell from the master matrix should produce rows like this:

| Dataset | BFM | Task | Target | Split | Metric | Statistical floor | BFM score | Status | Decision |
|---|---|---|---|---|---|---:|---:|---|---|

Status:

| Status | Meaning |
|---|---|
| `todo` | listed but not started |
| `running` | currently being run |
| `done` | metric produced |
| `blocked` | data/model/format issue |
| `invalid` | removed after inspection |

Decision:

| Decision | Meaning |
|---|---|
| `keep` | worth expanding |
| `drop` | weak or not worth more compute |
| `revisit` | useful later after a dependency is solved |

## After The Master Matrix

Only after the Dataset x BFM x Task table is populated do we choose later
branches:

| Benchmark finding | Later branch |
|---|---|
| SwiFT is best or competitive | SwiFT readout/adapter/fine-tuning |
| Another BFM is better | pivot away from strict SwiFT-first |
| All BFMs are weak but floors work | revisit input representation, HRF/windowing, pooling |
| Naturalistic datasets need context | task/movie-fMRI pretraining |
| Brain-only results need controls | stimulus-only video/audio/text baselines |
| Stimulus controls are strong | modality addition or TRIBE/stimulus-brain alignment |
