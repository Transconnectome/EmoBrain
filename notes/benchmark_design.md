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
| REELMO fMRI subset | dynamic/context benchmark if fMRI subset is usable | P2 |

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
| REELMO fMRI subset | SwiFT | CHECK | RUN | CHECK | CHECK | CHECK | RUN | CHECK |
| REELMO fMRI subset | Brain-JEPA | CHECK | RUN | CHECK | CHECK | CHECK | RUN | CHECK |
| REELMO fMRI subset | NeuroSTORM | CHECK | RUN | CHECK | CHECK | CHECK | RUN | CHECK |
| REELMO fMRI subset | BrainLM | CHECK | RUN | CHECK | CHECK | CHECK | RUN | CHECK |

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
