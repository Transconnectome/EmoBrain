# Long-Term Research Roadmap

## Program Identity

The durable CCN topic is not whether 34 emotion categories can be decoded from a selected subspace. It is:

> **How does the cortical hierarchy transform visual representations of emotional events into affectively organized brain representations?**

Video and brain foundation models provide a scalable measurement framework for this question. The shared subspace estimates information available across the two domains; raw BOLD localization identifies where that information is expressed and where additional affective structure emerges.

This remains distinct from EmoViS:

- EmoViS asks which model families best match emotional brain geometry across a sensory-to-semantic spectrum.
- CCN asks how information shared with a video foundation model is transformed across cortex within a paired video/brain foundation-model framework.

## Research Arc

### Phase 1: Establish the cortical transformation

Primary claims to test with the current dataset:

1. Estimate the effective dimensionality of the V-JEPA2/Brain-JEPA intersection under held-out stimuli and subjects.
2. Shared-channel information has a non-uniform cortical distribution.
3. Fine-grained affective profiles explain BOLD variance beyond the shared channel and beyond full V-JEPA2 features.
4. Shared and complementary signals occupy different positions along functional networks and the principal cortical gradient.

This is the poster-scale project. Its endpoint is a brain map and a cortical hierarchy test, not another category/A-V ratio.

### Current Full-Run Readout

The first 2185-stimulus run provides a useful but exploratory decision point:

- All tested shared components `1..20` had positive held-out cross-view correlation above the current shuffled null. This does **not** support a uniquely compact rank-3 intersection. Rank 3 remains an accepted-abstract reference and a sensitivity setting, not a discovered dimensionality.
- Shared-channel BOLD prediction was widespread and largest in dorsal-attention cortex at the network level. The planned visual-greater-than-transmodal contrast was not supported.
- The continuous 34D profile added BOLD variance beyond the rank-3 shared channel in all five subjects.
- The 34D profile also added variance beyond the full 100-PC V-JEPA2 control in all five subjects, with a transmodal-greater-than-visual contrast in the current subject-level test.
- The 34D advantage over arousal-valence was globally positive in every subject. Its additional transmodal enrichment was a trend rather than a stable result in the current five-subject test.

These results favor a revised working account:

> A broad visuocognitive video-brain channel is accompanied by complementary fine-grained affective information that is relatively enriched in transmodal cortex.

They do not yet support:

> A compact perceptual shared channel is transformed monotonically into transmodal emotion.

All p-values from this first run are exploratory, uncorrected across related contrasts, and based on five subjects. The next analysis should prioritize effect definition and stability over adding more maps.

### Phase 2: Identify the transformation mechanism

Move from spatial description to mechanism:

1. **Layer-to-cortex mapping:** test whether early and late V-JEPA2 layers preferentially explain perceptual and transmodal parcels.
2. **Mediation:** quantify whether semantic features mediate the path from video representation to transmodal affective variance.
3. **Representational flow:** compare shared, video-private, and video-unexplained brain components across networks.
4. **Temporal scale:** use clip segments or model tokens to test whether affective transformation depends on temporal integration rather than static content.

A strong result would connect model depth, temporal context, and cortical hierarchy in one analysis.

### Phase 3: Test specificity and generalization

Within the existing dataset first:

1. Hold out visual-semantic stimulus clusters rather than random stimuli.
2. Generalize across emotion-profile regions, not only across individual clips.
3. Compare pretrained, scratch, image, and video objectives with the same cortical transformation metric.
4. Estimate subject reliability and noise ceilings before interpreting individual differences.
5. Test whether effects survive motion, face, object, scene, and semantic controls jointly.

External datasets become useful only after the estimand and primary contrasts are stable. Replication should test the cortical transformation, not merely whether emotion labels are decodable again.

### Phase 4: Connect representation to experience and behavior

The current dataset supports stimulus-grounded affective representation, not subjective feeling. A later study can add trial-wise experience ratings, physiology, or behavior to ask whether video-unexplained transmodal activity predicts what a person actually feels.

This phase changes the claim from:

> affectively meaningful cortical information beyond a video model

to the stronger and separately testable claim:

> subject-specific affective experience constructed beyond stimulus-computable content

## Paper Ladder

### CCN Poster

- compact held-out shared rank
- shared-channel cortical map
- unique 34D and A/V maps
- network and cortical-gradient double dissociation
- full-video and shuffled-correspondence controls

### Short Full Paper

- nested rank selection
- spatial-autocorrelation-aware inference
- visual-semantic controls
- model/pretraining controls
- reliability and noise-ceiling analysis

### Larger Mechanistic Paper

- layer-to-cortex and temporal analyses
- mediation or variance-flow model
- independent dataset or new behavioral acquisition
- explicit account of what is stimulus-computable versus experience-dependent

## Decision Points

| Outcome | Development path |
|---|---|
| Shared map is perceptual and unique affect is transmodal | Develop hierarchical transformation account |
| Shared map is broad/attentional and unique affect is transmodal | Develop a visuocognitive-scaffold plus affective-enrichment account |
| Shared and unique maps overlap | Reframe as affectively enriched shared channel, without a transformation claim |
| 34D advantage disappears beyond full video | Conclude that fine-grained affect is largely stimulus-computable |
| Unique affect survives but has no hierarchy | Focus on distributed complementary representation |
| Only the first shared axis is stable | Use a dominant shared axis, not a multi-dimensional subspace claim |
| Effects fail across subjects | Treat group-average findings as exploratory and prioritize reliability |

## Guardrails

- The 34D ratings are continuous profiles, not 34 neural modules.
- Brain-JEPA/video-model overlap is not automatically emotion-specific.
- Video-unexplained activity is not automatically subjective feeling.
- Parcel count is not the inferential sample size; subjects are.
- Spatial gradient statistics require spatially informed nulls for parcel-level inference.
- Theoretical language follows the strongest surviving control, not the preferred story.
