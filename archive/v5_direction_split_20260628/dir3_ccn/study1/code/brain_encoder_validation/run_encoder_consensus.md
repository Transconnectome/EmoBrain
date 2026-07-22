# Brain-Encoder Consensus

## Question

Does the V-JEPA2/brain intersection replicate across independently pretrained brain
encoders, or is it specific to the legacy Brain-JEPA temporal-position adaptation?

## Inputs

- corrected frozen Brain-JEPA (`native` one-patch sin/cos)
- legacy Brain-JEPA (`temporal_mean`) as a sensitivity condition
- matched-window SwiFT SL20, pretrained and scratch
- matched-window NeuroSTORM, pretrained and scratch
- raw cortical BOLD as a non-foundation benchmark
- V-JEPA2, visual+semantic features, 34D emotion profiles, and arousal-valence

All inputs come from the same Horikawa stimuli. No external dataset is required.

## Analyses

1. Direct linear CKA describes geometry without matching feature dimensions.
2. Stimulus-fold cross-validation predicts V-JEPA2-PC100 and
   visual-semantic-PC100 targets from each subject's brain representation.
3. The same folds compare emotion-PCA2 against arousal-valence at matched target
   dimensionality.
4. Full 34D emotion prediction tests additional fine-grained resolution.
5. Pretrained-minus-scratch differences test whether pretrained weights contribute
   beyond architecture and preprocessing.

Target PCA is fit inside each outer training fold. Ridge alpha is selected inside the
outer training set. Direct CKA is descriptive and must not be compared as if it were
an inferential, dimension-matched effect.

## Decision rule

- Replication across corrected Brain-JEPA, SwiFT, and NeuroSTORM supports a
  brain-foundation-model-general shared channel.
- Replication only in legacy Brain-JEPA indicates a positional-adaptation artifact.
- Similar pretrained and scratch results indicate architecture/input statistics, not
  learned foundation-model knowledge.
- Raw-BOLD content-affect partitioning remains the primary cortical analysis in all
  cases.

## Run order

```bash
sbatch --array=1-5 extract_brain_jepa_frozen.sh native mean
sbatch run_encoder_consensus.sh
```

Optional corrected Brain-JEPA scratch extraction:

```bash
for subject in 01 02 03 04 05; do
  /pscratch/sd/s/sjmoon/brain-jepa-env/bin/python extract_brain_jepa_frozen.py \
    --subject "sub-${subject}" --init scratch --position-policy native --padding mean
done
```

The full jobs are run by the user. Codex only performs syntax and smoke checks.
