# CCN Poster Development - Cortical Transformation of Foundation-Model Representations

**Scope.** This document applies only to the CCN analysis in `dir3_ccn`. EmoViS and the other EmoBrain projects remain separate.

**Status.** New poster-development direction. The accepted CCN camera-ready analysis is retained as the starting observation, but the poster story may incorporate new analyses within the existing video-foundation-model / brain-foundation-model framework. Legacy Brain-JEPA-dependent results are provisional pending the temporal-position audit below.

## Brain-Encoder Validity Gate (2026-07-21)

Brain-JEPA was pretrained with 160 TR (10 temporal patches), while the CCN input has
16 TR (one temporal patch). The legacy extraction averaged the checkpoint's 10
temporal position codes. Code inspection shows that this tensor is fixed sin/cos
code (`requires_grad=False`), not a learned positional table. The patch kernel is
already matched at 16 TR.

The corrected frozen condition therefore does not require task finetuning: omit the
mismatched checkpoint position tensor and retain the native one-patch sin/cos code
created by the model. This removes arbitrary averaging while preserving independent
pretraining. It does not erase the broader one-patch versus 10-patch architecture
shift, which remains a limitation.

Poster claims must pass three gates:

1. corrected frozen Brain-JEPA does not reverse the shared-geometry result;
2. the result replicates in matched-window SwiFT SL20 and NeuroSTORM;
3. pretrained encoders exceed their scratch controls on held-out stimuli.

The raw-BOLD content-affect partition is independent of this gate. The shared-rank
estimate, shared cortical map, and `E34 | shared` result are not.

---

## Fixed Framework

The following elements remain fixed:

1. V-JEPA2 provides video foundation model embeddings for emotional videos.
2. Independently pretrained brain foundation models provide embeddings for the corresponding fMRI responses; corrected frozen Brain-JEPA, SwiFT SL20, and NeuroSTORM test encoder generality.
3. The two foundation models were trained independently and without emotion-label supervision.
4. The scientific object is the brain-general intersection with V-JEPA2, not a competition between EmoViS model families or dependence on one brain encoder.

The accepted PC1-PC3 result remains useful as preliminary evidence, but the updated poster does not need to treat PCA-defined components as the final shared representation.

---

## Why the Previous Story Is Too Weak

The previous story can be summarized as:

```text
Brain-JEPA predicts three V-JEPA2 PCs
    -> those PCs decode 34 emotion categories better than arousal-valence
    -> therefore V-JEPA2 contains an affective subspace
```

This framing has three problems:

1. A video model predicting emotion ratings is not by itself surprising because emotional videos contain correlated faces, actions, scenes, and motion.
2. The 34 emotion scores are continuous profiles, not hard category labels. Calling the result categorical overstates the measurement.
3. A category/A-V ratio characterizes the selected components but does not establish that they are specifically selected for affective information.

Therefore, the updated poster should not make "34 emotion categories" the discovery. Emotion annotations should be external functional probes used to characterize a shared foundation-model representation.

---

## New Central Question

Primary research question:

> **How does the cortical hierarchy transform video-foundation-model representations into affective brain representations?**

Operational questions:

1. Is the intersection of independently trained video and brain foundation models reproducible across held-out stimuli, subjects, and brain encoders?
2. Where in cortex is this shared video-brain information expressed?
3. Where does fine-grained affective information explain brain activity beyond the shared video representation?
4. Does this video-unexplained affective contribution increase from perceptual to transmodal cortex, and is it richer than arousal-valence alone?

The subspace is therefore an estimator of cross-domain information, not the scientific endpoint. The endpoint is the cortical organization of shared and transformed information.

---

## Working Thesis

Target finding, conditional on the new analyses:

> **The cortex does not uniformly mirror a video foundation model. Shared video-brain information is expressed predominantly in perceptual systems, whereas fine-grained affective information not explained by that shared representation increases toward transmodal cortex.**

Conservative version:

> A compact representation shared by video and brain foundation models has a non-uniform cortical distribution, and fine-grained affective profiles explain complementary variance in association cortex.

This claim does not require the cortex to contain 34 discrete emotion modules. The 34 ratings are a continuous high-dimensional profile used to test representational resolution beyond two broad arousal-valence dimensions.

### Preliminary Full-Run Update

The first 2185-stimulus run does not support the simplest perceptual-to-transmodal double dissociation as written above.

- Shared prediction is widespread and is strongest in dorsal-attention cortex at the Yeo-network level; visual cortex is not greater than control/default cortex.
- Unique 34D variance is positive beyond both the prespecified rank-3 shared representation and the full 100-PC V-JEPA2 control.
- Unique 34D variance is relatively enriched in control/default versus visual cortex in the current subject-level contrasts.
- The 34D advantage over A/V is globally positive, while its transmodal enrichment remains weaker.
- Components 1 through 20 all show positive held-out cross-view correlation under the current estimator, so compact rank 3 is not established.

The updated result-driven working thesis is therefore:

> **A broad visuocognitive channel is shared between video and brain foundation models, while complementary fine-grained affective information is relatively enriched in transmodal cortex.**

This remains provisional until dimensionality selection, repeated splits, multiple-comparison handling, and spatially informed inference are completed.

---

## Updated Storyline

### 1. Two Independently Trained Foundation Models

V-JEPA2 learns from videos and Brain-JEPA learns from brain dynamics. They are not jointly trained and neither receives emotion-label supervision. The same emotional videos nevertheless provide paired observations in the two embedding spaces.

Question:

> What representational structure is shared across these independently learned domains?

### 2. Estimate a Compact Cross-Domain Bottleneck

The accepted analysis provides initial evidence:

- Brain-JEPA predicts only a small subset of the leading V-JEPA2 components.
- Group-level PC1-PC3 survive the accepted selection procedure.
- PC1 is the most stable component across individual subjects.

The updated analysis should estimate shared dimensionality directly with a cross-validated multiview method rather than assuming that the final object is exactly PC1-PC3.

Preferred interpretation:

> Video-brain correspondence is concentrated in a low-rank shared representation.

This result establishes the information channel to be localized. It is not the poster's final biological finding.

### 3. Emotion Ratings Are Functional Probes

The 34 Cowen-Keltner scores should be described as a continuous 34-dimensional emotion profile. They characterize the information retained in the shared representation; they do not define the representation.

Preferred wording:

> The shared representation is enriched for information about continuous fine-grained affective profiles.

Avoid:

> The shared subspace follows 34 discrete emotion categories.

The arousal-valence comparison is retained as a resolution test:

> Is the shared affective information adequately summarized by two broad dimensions, or does it retain a richer multivariate profile?

### 4. Localize the Shared Channel in Cortex

Use the video-side shared scores, learned without the held-out subject, to predict each parcel's raw BOLD response on held-out stimuli.

```text
V-JEPA2 + Brain-JEPA from four subjects
        -> shared latent scores
        -> held-out subject's 400 cortical parcels
```

The resulting parcel-wise held-out `R2` map answers where cortex expresses the shared video-brain information. The expected pattern is an empirical question; it must not be described as perceptual before the map is observed.

### 5. Identify Cortical Transformation Beyond the Shared Channel

For every parcel, compare nested encoding models on identical held-out stimuli:

```text
Shared video-brain scores
Shared scores + 34D continuous emotion profile
Shared scores + arousal/valence
```

Define:

```text
Unique fine-grained affect = R2(shared + emotion34) - R2(shared)
Unique A/V affect          = R2(shared + A/V) - R2(shared)
Fine-grained advantage     = Unique emotion34 - Unique A/V
```

The first contrast asks where affective information remains after accounting for the shared video channel. The second contrast asks whether that contribution requires a richer profile than arousal-valence. These are encoding-model variance increments, not evidence for discrete emotion categories.

As a stricter control, repeat the unique-affect test beyond the full cross-validated V-JEPA2 PCA representation rather than only beyond the compact shared scores.

### 6. Test the Cortical Hierarchy

Summarize all parcel maps in two independent anatomical coordinate systems:

1. Yeo 7 functional networks
2. the independently estimated principal functional gradient

The transformation hypothesis predicts a double dissociation:

- shared-channel `R2` is larger toward visual/perceptual cortex
- unique fine-grained affect and its advantage over A/V increase toward control/default/transmodal cortex

Network and gradient tests turn a collection of parcel maps into a cortical mechanism. Subject-level effects, not parcels treated as independent observations, are the inferential unit.

### 7. Test Representational Necessity and Sufficiency

Compactness and enrichment are descriptive. The stronger claim requires component ablation.

```text
Shared-only
Shared-removed
Full V-JEPA2
Rank- and variance-matched controls
```

The shared component is affectively selective only if:

1. A low-dimensional shared-only representation preserves disproportionate affective information.
2. Removing the shared component reduces affective prediction more than removing matched random components.
3. The effect exceeds what can be explained by generic visual and semantic information.

### 8. Decompose Shared and Complementary Information

The foundation-model framework allows three operational components:

```text
Video-private
    Information in V-JEPA2 not shared reliably with Brain-JEPA

Video-brain shared
    Cross-validated low-rank information recoverable across both models

Video-unexplained brain component
    Reliable Brain-JEPA information not predicted from V-JEPA2
```

Do not call the last component subjective emotion. With the current dataset, it can only be called a reliable video-unexplained brain component. It becomes affectively meaningful only if it predicts affective targets across held-out stimuli and subjects.

### 9. Interpret the Division of Labor

A theoretically informative outcome would be:

- shared component: visual-semantic and fine-grained stimulus-grounded affective profiles
- video-private component: visual details that are not consistently reflected in the brain representation
- reliable video-unexplained brain component: complementary affective dimensions or transmodal structure

This would reframe category profiles and affective dimensions as descriptions of different representational components rather than competing universal emotion theories.

---

## Required New Analyses

### Analysis 1. Cross-Validated Shared-Rank Estimation

Goal:

> Establish that the video-brain intersection is genuinely low-rank and not an artifact of selecting leading V-JEPA2 PCs.

Recommended method:

1. Reduce V-JEPA2 and Brain-JEPA within each training fold.
2. Fit regularized CCA, PLS, or reduced-rank regression on training stimuli only.
3. Select rank `k = 1...20` with nested cross-validation.
4. Evaluate cross-model prediction or canonical correlation on held-out stimuli.
5. Repeat subject-wise and with leave-one-subject-out discovery.

Controls:

- shuffled brain-stimulus correspondence
- rank-matched random projections
- top-k PCA baseline
- PC1-only and accepted PC1-PC3 analysis
- raw BOLD replication

Primary output:

- held-out alignment as a function of shared rank
- confidence interval for the optimal rank
- subject-level reproducibility

### Analysis 2. Necessity-Sufficiency Ablation

Goal:

> Test whether the shared component is selectively important for affective information.

Representations:

1. full V-JEPA2
2. shared-only
3. shared-removed
4. random rank-matched subspace
5. variance-matched PCA control
6. shuffled-brain-derived subspace

Target families:

- continuous 34D emotion profile
- arousal-valence
- all 14 affective dimensions
- VGG19 visual features
- 73D semantic features

Primary statistics:

- sufficiency: performance retained by shared-only relative to full V-JEPA2
- necessity: performance loss after shared removal
- selectivity: affective loss minus visual/semantic loss
- empirical percentile against random-subspace nulls

Use raw cross-validated `R2`, Pearson `r`, and difference scores. Do not use clipped `R2` or the category/A-V ratio as the primary inferential statistic.

### Analysis 3. Parcel-Wise Shared-Channel Encoding

Goal:

> Localize where the cross-domain bottleneck is expressed in cortex.

Procedure:

1. Leave one subject out of shared-subspace discovery.
2. Within that loop, fit every PCA and cross-view mapping on training stimuli only.
3. Use video-side shared scores to predict the held-out subject's raw BOLD response in each of the first 400 cortical parcels.
4. Concatenate out-of-fold predictions and compute parcel-wise raw `R2`, Pearson `r`, and Spearman `r`.
5. Retain subject maps separately before calculating a group summary.

Controls:

- shuffled video-brain stimulus correspondence during subspace discovery
- full V-JEPA2 PCA encoding map
- top-k V-JEPA2 PCA map with the same rank as the shared representation
- accepted PC1 and PC1-PC3 maps

Primary output:

- one 400-parcel map per subject and a group-average map
- Yeo-network summaries with subject-level confidence intervals
- correspondence with the independent principal cortical gradient

### Analysis 4. Parcel-Wise Unique Affective Variance

Goal:

> Identify where cortex contains affective structure not explained by the shared video representation.

Fit nested encoding models with identical outer folds and regularization selection:

```text
S       = shared video-brain scores
S+E34   = shared scores + continuous 34D emotion profile
S+AV    = shared scores + arousal and valence
V       = cross-validated full V-JEPA2 PCA scores
V+E34   = full video scores + continuous 34D emotion profile
```

Primary contrasts:

```text
Delta_E34|S  = R2(S+E34) - R2(S)
Delta_AV|S   = R2(S+AV) - R2(S)
FG_advantage = Delta_E34|S - Delta_AV|S
Delta_E34|V  = R2(V+E34) - R2(V)
```

Interpretation:

- `Delta_E34|S > 0`: the compact shared channel is insufficient to explain all affect-related BOLD variance
- `FG_advantage > 0`: the complementary effect is better captured by a fine-grained profile than by A/V alone
- `Delta_E34|V > 0`: the effect survives the stricter full-video control

Use held-out raw `R2` without clipping. Quantify uncertainty across subjects and folds. A positive group map without subject-level consistency is descriptive only.

### Analysis 5. Cortical Gradient and Network Tests

Goal:

> Test whether shared and complementary affective signals follow a perceptual-to-transmodal transformation.

Required summaries:

1. subject-wise Spearman correlation between each parcel map and principal gradient 1
2. subject-wise Yeo 7 network means
3. perceptual-versus-transmodal planned contrast
4. bootstrap confidence intervals over subjects

Spatial autocorrelation must be respected for parcel-level inference. Until a surface spin/null implementation is available, gradient statistics are effect-size summaries and subject-wise tests carry the primary inference.

### Analysis 6. Shared-Unique Variance Partitioning in Embedding Space

Goal:

> Quantify which affective information is shared, video-unique, or brain-unique.

For each target family, compare nested cross-validated models:

```text
Video FM only
Brain FM only
Video FM + Brain FM
```

Compute:

```text
Unique brain = R2(video + brain) - R2(video)
Unique video = R2(video + brain) - R2(brain)
Shared contribution = total explained structure not uniquely assigned to either side
```

Because commonality estimates can be unstable under correlated predictors, report bootstrap intervals and the underlying model performances in addition to the partitioned values.

Reliability requirement for any brain-unique claim:

- repeat per subject
- discover on four subjects and evaluate on the held-out subject
- repeat with raw BOLD
- require held-out stimulus generalization

### Analysis 7. Visual-Semantic Matched-Pair Test

Goal:

> Test affective organization under direct stimulus matching rather than relying only on linear residualization.

Select critical pairs without using brain data:

1. visual-semantic matched but emotion-profile divergent
2. emotion-profile matched but visual-semantic divergent

Use VGG19 and 73D semantic features for matching and the continuous 34D profile for affective distance. Evaluate whether Brain-JEPA and the learned shared representation distinguish the first pair type and generalize across the second.

Required controls:

- caliper matching on visual-semantic distance
- repeated matching rather than one nearest neighbor
- subject-wise evaluation
- permutation of pair labels
- no brain information during pair selection

This analysis should produce a small set of interpretable video triplets for the poster as well as an aggregate statistical result.

---

## Analysis Priority

### Must Complete

1. Cross-validated shared-rank estimation
2. Parcel-wise shared-channel encoding
3. Parcel-wise unique 34D and A/V variance maps
4. Yeo-network and principal-gradient tests
5. Necessity-sufficiency ablation

### Important Controls

1. leave-one-subject-out validation
2. raw BOLD replication
3. random and variance-matched subspaces
4. shuffled correspondence null
5. PC1-only versus PC1-PC3
6. unclipped metrics and bootstrap intervals
7. full-video control for unique affective variance

### Defer Unless Needed

- broad model-zoo comparison
- additional UMAP visualizations
- hard-label emotion classification
- additional category/A-V ratios
- external datasets
- layer-wise V-JEPA2 analysis
- visual-semantic matched-pair analysis, unless the cortical results require an additional stimulus-level control

---

## Existing Evidence Retained

The accepted camera-ready results remain the starting observation:

- V-JEPA2 embedding dimension: 1,408
- analyzed PCA space: top 100 PCs
- accepted brain-aligned components: PC1-PC3
- PC1 `R2 = 0.373`
- PC2 `R2 = 0.075`
- PC3 `R2 = 0.088`
- 34D profile mean `R2 = 0.055`
- arousal-valence mean `R2 = 0.038`
- accepted category/A-V ratio: 1.44
- full V-JEPA2 ratio: 1.26

These numbers should be presented as preliminary characterization, not as the final proof of an affective bottleneck.

Existing visual-semantic controls also remain relevant:

- visual and semantic residualization strongly reduces absolute predictive signal
- a small residual remains under the tested VGG19 and 73D semantic baselines
- current controls justify "not fully explained by the tested baselines," not "independent of visual-semantic content"

---

## Decision Rules

| Result | Poster conclusion |
|---|---|
| Shared-only retains affective information and shared removal selectively harms it | Brain alignment identifies an affective bottleneck |
| Shared space is low-rank but ablation is not affect-selective | Compact cross-domain visual-semantic bottleneck |
| Brain-unique affective contribution generalizes across subjects and raw BOLD | Complementary video-unexplained brain affective structure |
| Brain-unique contribution fails cross-subject validation | Do not interpret brain residual as affective |
| Top-k PCA performs like the learned shared space | Brain alignment is not demonstrably selective |
| Only PC1 is stable | Describe a dominant shared axis, not a three-dimensional subspace |
| Visual-semantic matched-pair effect survives | Shared or brain-specific affective structure is not reducible to simple content matching |

---

## Poster Figure Plan

### Figure 1. Foundation-Model Framework

```text
Emotional video -> V-JEPA2 embedding
Same video      -> fMRI -> Brain-JEPA embedding
                         |
                         v
              shared / complementary decomposition
```

Message:

> Two independently trained foundation models provide paired views of the same emotional event.

### Figure 2. Shared Rank

Show held-out cross-model prediction across candidate ranks, with subject-level points and shuffled null.

Message:

> Cross-domain correspondence is concentrated in a compact latent space.

### Figure 3. Main Brain Figure - Cortical Transformation

Four coordinated panels:

```text
A. Shared-channel held-out R2 cortical map
B. Unique 34D affect beyond shared-channel cortical map
C. Fine-grained advantage over A/V cortical map
D. Yeo-network bars + principal-gradient relationships
```

Each panel displays subject-wise uncertainty. Surface maps are descriptive; network and gradient summaries carry the cross-subject statistics.

Message, if supported:

> Shared video-brain information is strongest in perceptual systems, while complementary fine-grained affective information increases toward transmodal cortex.

### Figure 4. Specificity and Controls

Compare compact shared, full video, 34D, A/V, shuffled-correspondence, and rank-matched controls. Include the stricter `Delta_E34|V` result.

Message:

> The cortical effect reflects information beyond the shared or full video representation and is not reproduced by A/V alone.

### Figure 5. Optional Stimulus-Level Interpretation

Use necessity-sufficiency results or visual-semantic matched pairs to interpret what stimulus content drives the cortical transformation. This figure is secondary to the brain map.

---

## Title Options

Primary, if the cortical hierarchy result succeeds:

1. **From Shared Video Features to Affective Brain Geometry Across the Cortical Hierarchy**

Alternatives:

2. **Cortical Transformation of Emotional Video Representations Across Foundation Models**
3. **Where Video and Brain Foundation Models Converge and Diverge in Cortex**
4. **A Compact Video-Brain Bottleneck Reveals Hierarchical Affective Transformation**
5. **The Brain's Emotion Geometry Is Grounded in What Is Seen and Transformed Across Cortex**

---

## Claim Ladder

### Safe With Existing Results

> Brain-JEPA predicts a compact subset of V-JEPA2 components, and these components carry information about continuous fine-grained affective profiles.

### Requires Shared-Rank and Control Analyses

> Independently trained video and brain foundation models share a reproducible low-rank representation of emotional videos.

### Poster Target Claim

> Shared video-brain information and complementary fine-grained affective information have distinct distributions along the cortical hierarchy.

### Requires Reliable Unique-Variance Results

> Shared and video-unexplained brain components carry complementary aspects of affective structure.

### Avoid

- The brain is categorically organized.
- V-JEPA2 learned emotion categories.
- The shared subspace is a pure emotion module.
- Brain-private structure represents subjective feeling.
- Visual-semantic content has been completely controlled.
- Arousal-valence is an incorrect theory of emotion.

---

## One-Sentence Takeaway

> 두 독립적인 video/brain foundation model의 compact한 교집합은 cortex 전체에 균일하게 복제되지 않으며, perceptual system의 shared video information에서 transmodal cortex의 video-unexplained fine-grained affective information으로 이어지는 계층적 변환을 검증한다.
