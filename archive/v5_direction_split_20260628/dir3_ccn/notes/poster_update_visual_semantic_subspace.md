# CCN Poster Development - An Affective Bottleneck Between Foundation Models

**Scope.** This document applies only to the CCN analysis in `dir3_ccn`. EmoViS and the other EmoBrain projects remain separate.

**Status.** New poster-development direction. The accepted CCN camera-ready analysis is retained as the starting observation, but the poster story may incorporate new analyses within the existing video-foundation-model / brain-foundation-model framework.

---

## Fixed Framework

The following elements remain fixed:

1. V-JEPA2 provides video foundation model embeddings for emotional videos.
2. Brain-JEPA provides brain foundation model embeddings for the corresponding fMRI responses.
3. The two foundation models were trained independently and without emotion-label supervision.
4. The scientific object is the relationship between the two embedding spaces, not a competition between EmoViS model families.

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

> When independently trained video and brain foundation models represent the same emotional videos, is their shared information diffuse across the full representations, or concentrated in a compact and functionally selective bottleneck?

The stronger follow-up question is:

> Is this shared bottleneck specifically necessary and sufficient for affectively meaningful information, and what complementary information remains outside it?

---

## Working Thesis

Primary version:

> Brain alignment identifies a compact affective bottleneck within a video foundation model: this bottleneck selectively preserves stimulus-grounded emotion structure, while video-unexplained brain components retain complementary affective information.

More conservative version:

> A compact subspace shared by video and brain foundation models is selectively enriched for continuous, fine-grained affective profiles relative to matched model components.

The primary version requires new necessity, sufficiency, and shared-versus-unique analyses. Until those analyses are complete, use the conservative version.

---

## Updated Storyline

### 1. Two Independently Trained Foundation Models

V-JEPA2 learns from videos and Brain-JEPA learns from brain dynamics. They are not jointly trained and neither receives emotion-label supervision. The same emotional videos nevertheless provide paired observations in the two embedding spaces.

Question:

> What representational structure is shared across these independently learned domains?

### 2. Cross-Domain Correspondence Is Compact

The accepted analysis provides initial evidence:

- Brain-JEPA predicts only a small subset of the leading V-JEPA2 components.
- Group-level PC1-PC3 survive the accepted selection procedure.
- PC1 is the most stable component across individual subjects.

The updated analysis should estimate shared dimensionality directly with a cross-validated multiview method rather than assuming that the final object is exactly PC1-PC3.

Preferred interpretation:

> Video-brain correspondence is concentrated in a low-rank shared representation.

### 3. Emotion Ratings Are Functional Probes

The 34 Cowen-Keltner scores should be described as a continuous 34-dimensional emotion profile. They characterize the information retained in the shared representation; they do not define the representation.

Preferred wording:

> The shared representation is enriched for information about continuous fine-grained affective profiles.

Avoid:

> The shared subspace follows 34 discrete emotion categories.

The arousal-valence comparison is retained as a resolution test:

> Is the shared affective information adequately summarized by two broad dimensions, or does it retain a richer multivariate profile?

### 4. Test Representational Necessity and Sufficiency

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

### 5. Decompose Shared and Complementary Information

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

### 6. Interpret the Division of Labor

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

### Analysis 3. Shared-Unique Variance Partitioning

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

### Analysis 4. Visual-Semantic Matched-Pair Test

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

### Analysis 5. Optional Network Localization

Goal:

> Determine whether shared and video-unexplained affective components have different anatomical distributions.

Use the available 450-parcel raw BOLD data grouped into functional networks. For each network, estimate:

- predictability of the shared video component
- residual affective prediction after removing video-predictable activity
- relative sensitivity to 34D profiles, A/V, and 14D dimensions

This analysis is optional for the first updated poster draft. It should be added only after Analyses 1-4 are stable.

---

## Analysis Priority

### Must Complete

1. Cross-validated shared-rank estimation
2. Necessity-sufficiency ablation
3. Shared-unique variance partitioning
4. Visual-semantic matched-pair test

### Important Controls

1. leave-one-subject-out validation
2. raw BOLD replication
3. random and variance-matched subspaces
4. shuffled correspondence null
5. PC1-only versus PC1-PC3
6. unclipped metrics and bootstrap intervals

### Defer Unless Needed

- broad model-zoo comparison
- additional UMAP visualizations
- hard-label emotion classification
- additional category/A-V ratios
- external datasets
- layer-wise V-JEPA2 analysis

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

### Figure 3. Necessity and Sufficiency

Compare full, shared-only, shared-removed, PCA, random, and shuffled controls across target families.

Message:

> The shared representation is disproportionately important for fine-grained affective profiles.

### Figure 4. Shared and Unique Information

Show shared, video-unique, and reliable brain-unique contributions for visual, semantic, 34D profile, A/V, and 14D target families.

Message:

> Different aspects of affect occupy shared and complementary representational components.

### Figure 5. Critical Video Pairs

Show representative visual-semantic-matched and emotion-matched triplets with aggregate subject-wise statistics.

Message:

> Affective organization can be tested while explicitly matching stimulus content.

---

## Title Options

Primary, if necessity and sufficiency succeed:

1. **An Affective Bottleneck Between Video and Brain Foundation Models**

Conservative alternatives:

2. **A Compact Shared Representation Between Video and Brain Foundation Models**
3. **Decomposing Shared and Brain-Specific Affective Representations Across Foundation Models**
4. **What Do Video and Brain Foundation Models Share When Watching Emotional Videos?**
5. **A Low-Rank Bridge Between Video and Brain Representations of Emotional Events**

---

## Claim Ladder

### Safe With Existing Results

> Brain-JEPA predicts a compact subset of V-JEPA2 components, and these components carry information about continuous fine-grained affective profiles.

### Requires Shared-Rank and Control Analyses

> Independently trained video and brain foundation models share a reproducible low-rank representation of emotional videos.

### Poster Target Claim

> The shared representation is selectively necessary and sufficient for stimulus-grounded affective information relative to matched visual-model components.

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

> 두 독립적인 video/brain foundation model의 교집합은 단순히 작기만 한 것이 아니라, 감정적으로 의미 있는 정보를 선택적으로 보존하는 affective bottleneck일 수 있으며, 새로운 분석은 그 bottleneck의 필요성, 충분성, 그리고 brain 쪽의 보완적 정보를 직접 검증한다.
