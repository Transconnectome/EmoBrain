# Must-Fix Revision Notes for the CCN 2026 Extended Abstract

Target manuscript: **“Fine-Grained Emotion Structure in the Brain-Aligned Subspace of a Self-Supervised Video Model”**

Purpose of this document:  
This is **not a full review**. It lists only the **must-fix issues** that should be addressed before submission or further review.

---

## 1. Clarify the comparison between emotion categories and affective dimensions

### Problem

The manuscript states that the dataset includes:

- 34 emotion categories
- 14 affective dimensions

However, the main Results compare the 34 categories only against **valence and arousal (V-A)**.

This creates a potential inconsistency. A reviewer may ask:

> If the dataset includes 14 affective dimensions, why is the main dimensional baseline only valence-arousal?

### Required fix

Add a clear justification for using only valence and arousal as the main dimensional baseline.

Recommended sentence:

> Although the dataset includes 14 affective dimensions, we focused on valence and arousal as the canonical two-dimensional affective model. We additionally verified whether the categorical advantage persisted when using all 14 affective dimensions.

### Stronger fix if possible

Run and report an additional analysis comparing:

- 34 emotion categories
- all 14 affective dimensions
- valence-arousal only

If the 34-category advantage remains, this will substantially strengthen the manuscript.

---

## 2. Report absolute differences, not only category/V-A ratios

### Problem

The current Results emphasize the category/V-A ratio:

- category mean R² = 0.055
- V-A mean R² = 0.038
- category/V-A ratio = 1.44

The ratio sounds strong, but the absolute difference is relatively small:

- ΔR² = 0.017

A reviewer may worry that the ratio exaggerates the effect size.

### Required fix

Report both:

1. the ratio
2. the absolute difference

Recommended reporting format:

> Decoding from the brain-aligned subspace yielded higher prediction for emotion categories than for valence-arousal (mean category R² = 0.055, mean V-A R² = 0.038, ΔR² = 0.017, category/V-A ratio = 1.44).

### Stronger fix if possible

Add uncertainty estimates:

- bootstrap confidence intervals for category R²
- bootstrap confidence intervals for V-A R²
- bootstrap confidence interval for ΔR²
- permutation p-value for category > V-A

This will make the category advantage much more defensible.

---

## 3. Address possible selection bias in the brain-aligned PC analysis

### Problem

The pipeline appears to be:

1. Decompose V-JEPA2 embeddings into 100 PCs.
2. Predict each PC from Brain-JEPA.
3. Select PCs that survive permutation FDR.
4. Use the selected PCs for emotion category / V-A decoding.

This raises a possible concern:

> Were the same stimuli used both to select the brain-aligned PCs and to evaluate emotion decoding?

Even though PC selection does not use emotion labels directly, a reviewer may still see this as a possible source of optimistic bias.

### Required fix

Clarify whether PC selection and downstream emotion evaluation were independent.

If they were independent, explicitly state this in Methods.

Recommended sentence:

> Brain-aligned PCs were selected within the training folds only, and downstream emotion decoding was evaluated on held-out stimuli to avoid optimistic bias from subspace selection.

### If not currently independent

The stronger solution is to use a nested cross-validation or stimulus-split procedure:

- Outer fold: held-out stimuli for final emotion evaluation
- Inner fold: select brain-aligned PCs
- Evaluate category/V-A decoding only on the outer held-out stimuli

If this cannot be done before submission, acknowledge it as a limitation and soften the claim.

---

## 4. Make Brain-JEPA embedding extraction explicit

### Problem

The Methods say:

> Brain-JEPA embeddings, averaged across subjects, were paired with V-JEPA2 video embeddings.

This is too compressed.

A reviewer may ask:

- What exactly is the Brain-JEPA embedding?
- Is it extracted per video?
- Is it extracted from stimulus-evoked fMRI responses?
- Was subject averaging done before or after embedding extraction?
- How are subject-level stability analyses related to the averaged representation?

### Required fix

Add 1–2 sentences explaining the exact embedding extraction process.

Template to adapt:

> For each subject and each video, we extracted a video-level Brain-JEPA embedding from the stimulus-evoked fMRI response. Subject-invariant brain embeddings were obtained by averaging these video-level embeddings across the five subjects. Subject-level analyses repeated the same decoding procedure separately for each subject.

Only use this wording if it matches the actual pipeline. Otherwise, modify it to match the actual analysis.

---

## 5. Clarify the partialling-out / confound-control analysis

### Problem

The manuscript says:

> We partialled out VGG19 and human-annotated semantic features for confound control.

This is underspecified.

A reviewer may ask:

- What variable was residualized?
- Were VGG19 and semantic features removed from V-JEPA2, Brain-JEPA, or emotion labels?
- Was residualization done within cross-validation folds?
- Are semantic features really “confounds,” or are they part of the meaningful visual-semantic structure of emotion?

### Required fix

Specify the residualization procedure.

Recommended wording:

> To test whether categorical alignment was reducible to low-level visual or annotated semantic content, we residualized model embeddings with respect to VGG19 features and human-annotated semantic features within each training fold, then evaluated decoding on held-out stimuli.

If residualization was not done within folds, do not use this exact wording. Instead, state the actual procedure and consider adding fold-wise residualization.

### Tone adjustment

Avoid framing semantics simply as a “confound.” A safer phrase is:

> reducible to visual or semantic content

rather than:

> controlled for confounds

---

## 6. Soften the strongest interpretive claim in the Abstract and Discussion

### Problem

The Abstract currently claims that:

> the brain's dimensional structure for emotional video resides predominantly outside this visually shared channel.

This is an interesting claim, but it may be too strong for the current evidence.

The data more directly show that:

- the V-JEPA2-aligned brain/model subspace is relatively more categorical than V-A
- the full brain space may preserve dimensional information more strongly
- therefore, dimensional affective information may depend on brain components not captured by the visual model-aligned subspace

### Required fix

Replace strong localization-style claims with more cautious wording.

Recommended replacement:

> These findings suggest that visually shared brain-model representations preferentially preserve category-like emotion structure, whereas dimensional affective information may rely more strongly on brain components not captured by this visual model-aligned subspace.

Also soften similar language in the Discussion.

Recommended replacement:

> One possible interpretation, consistent with constructionist accounts, is that visually grounded features contribute more strongly to category-like emotion structure, whereas dimensional affective structure may depend more on non-visual or higher-order brain components.

---

## 7. Avoid overclaiming from the “max |r| across 34 categories” analysis

### Problem

Figure 1B uses mean maximum absolute Spearman correlation with the 34 emotion categories.

Because it takes the maximum across 34 categories, this measure can favor the category side by construction.

This is acceptable as a descriptive visualization, but it should not carry the main evidential burden.

### Required fix

Rephrase the relevant Results sentence.

Current-style claim to avoid:

> confirming that the shared subspace is affectively organized

Safer version:

> suggesting that the brain-aligned PCs are enriched for affectively relevant variation

or:

> indicating that the shared subspace carries affectively relevant structure

### Stronger fix if possible

Use cross-validated decoding or RSA as the main evidence for categorical structure, and keep max |r| as a supplementary/descriptive analysis.

---

## 8. Check and standardize the video count

### Problem

The manuscript states:

> 2,196 emotional videos

Depending on the dataset convention, Horikawa/Cowen-Keltner materials may refer to slightly different counts, such as:

- stimulus entries
- unique clips
- analyzed clips after exclusions

If the number is not carefully specified, a reviewer familiar with the dataset may notice the discrepancy.

### Required fix

Use precise wording.

Possible wording:

> We analyzed 2,196 stimulus entries corresponding to [N] unique emotion-evocative video clips.

Replace `[N]` with the actual number used in the current preprocessing.

If the analysis truly used 2,196 unique videos, state that explicitly.

---

## 9. Tighten the main claim

### Problem

The manuscript currently uses strong language such as:

- categorical dominance
- dimensional structure resides outside the visually shared channel
- shared channel isolates the visual, category-organized contribution

These phrases are compelling but may sound stronger than the current analyses warrant.

### Required fix

Use a more defensible central claim.

Recommended central claim:

> The brain-model shared visual subspace preferentially preserves category-like structure of emotional videos relative to canonical valence-arousal dimensions.

Alternative:

> Self-supervised visual representations capture a category-relevant component of visually evoked emotion that is shared with brain responses.

These claims are still strong, but less vulnerable to reviewer criticism.

---

## 10. Add one sentence explicitly stating what is novel

### Problem

The novelty is present but slightly implicit.

The manuscript should make it unmistakable that the contribution is not simply “Horikawa replicated with a new model.”

### Required fix

Add a sentence in the Introduction or Discussion.

Recommended wording:

> Unlike prior work that examined emotion structure directly in neural responses or supervised affective models, this study asks whether categorical emotion geometry emerges specifically in the subspace shared between human brain responses and a self-supervised video model trained without emotion labels.

This sentence clarifies the unique contribution.

---

# Minimal revision checklist

Before submission, make sure the manuscript answers these questions:

- [ ] Why is valence-arousal the main dimensional baseline if 14 affective dimensions are available?
- [ ] Does the categorical advantage remain when using all 14 affective dimensions?
- [ ] Are category/V-A results reported as both ratio and absolute ΔR²?
- [ ] Are confidence intervals or permutation tests reported for the category advantage?
- [ ] Were brain-aligned PCs selected independently from the final emotion evaluation?
- [ ] Is the Brain-JEPA embedding extraction procedure clear?
- [ ] Is subject averaging clearly explained?
- [ ] Is the residualization / partialling-out procedure specified?
- [ ] Are strong claims about dimensional structure outside the visual channel softened?
- [ ] Is the video count precise and consistent?
- [ ] Is the novelty stated explicitly?

---

# Suggested revised core message

Use this as the guiding message for the revised abstract/discussion:

> We identify a compact V-JEPA2 subspace that is predictable from Brain-JEPA representations of emotional video responses. This brain-model shared visual subspace preferentially preserves fine-grained categorical emotion structure relative to canonical valence-arousal dimensions, suggesting that self-supervised visual representations capture a category-relevant component of visually evoked emotion shared with the human brain.
