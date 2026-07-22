# Validation Protocol

## Primary claim under test

The 16-TR representation is a valid short-window transfer of resting-pretrained
Brain-JEPA knowledge. It is not assumed to reproduce native long-range dynamics.

## Required evidence

1. Exact 16-TR patch weights are loaded without interpolation.
2. Corrected pretrained/native embeddings outperform scratch/native embeddings on
   held-out stimuli.
3. Core effects do not depend on legacy-mean versus native position handling.
4. Core effects do not depend strongly on mean versus zero padding.
5. Spatial-only and time-shuffle controls determine whether the transferred signal
   is spatial, temporally varying, or order-sensitive.
6. Raw BOLD provides a non-foundation benchmark.

## Strong optional evidence

On compatible long rs-fMRI, aggregated 16-TR embeddings preserve native 160-TR
geometry and predict native embedding PCs better for pretrained than scratch models.

## Interpretation matrix

| Result | Interpretation |
|---|---|
| Pretrained > scratch; position/padding stable | Learned short-window transfer is defensible |
| Pretrained > scratch; mean ~= spatial-only | Primarily resting-pretrained spatial network-state representation |
| Pretrained > scratch; mean > spatial-only but mean ~= shuffle | Temporal variation matters, order does not |
| Pretrained > scratch; mean > shuffle | Within-window temporal order contributes |
| Native and legacy position disagree | Legacy shared-subspace results are adaptation-sensitive |
| Scratch ~= pretrained | Do not attribute results to Brain-JEPA pretraining |
| Raw BOLD >= Brain-JEPA | Keep Brain-JEPA as compact/supporting measurement, not a superior encoder |
| Full-to-short consistency is weak | Use "short-window transfer" only; avoid native-dynamics language |

## Statistical guardrails

- Extraction never uses emotion labels.
- Model selection occurs within training folds.
- Subject-level effect directions are primary with only five subjects.
- Report exploratory p-values as such and avoid claims based only on CKA magnitude.
