# Final Check Notes for the Revised CCN 2026 Extended Abstract

Target manuscript: **“Fine-Grained Emotion Structure in the Brain-Aligned Subspace of a Self-Supervised Video Model”**

Purpose of this document:  
This is a **final pre-submission check**, not a full review. The manuscript is much improved. The main remaining issues are small but important clarifications that could reduce reviewer pushback.

---

## Overall judgment

The revised manuscript is close to submission-ready.

Major improvements already made:

- The Methods now specify **2,196 stimulus presentations** rather than vaguely referring to unique videos.
- The Brain-JEPA embedding extraction procedure is more explicit.
- The manuscript now explains that **valence and arousal** are used as the canonical two-dimensional affective baseline.
- The Results now report the absolute difference, **ΔR² = 0.017**, in addition to the category/V-A ratio.
- The Abstract and Discussion are more cautious about the claim that dimensional affective information lies outside the visually shared brain-model subspace.

The main remaining concerns are about methodological clarity and wording strength.

---

## 1. Check the page limit immediately

### Issue

The current PDF is **3 pages**.

The main text and figures appear to fit within 2 pages, while the third page contains acknowledgments and references.

### Required check

Confirm the CCN 2026 extended abstract rule:

- If the limit is **2 pages excluding references/acknowledgments**, the current layout is likely fine.
- If the limit is **2 pages including references/acknowledgments**, the manuscript may violate the page limit.

### Action

Check the official submission guideline before final upload.

---

## 2. Clarify independence between PC selection and emotion decoding

### Issue

The manuscript now explains that V-JEPA2 PCs were predicted from Brain-JEPA using 5-fold cross-validated ridge, and that FDR-surviving PCs were defined as brain-aligned.

However, it is still unclear whether:

- brain-aligned PCs were selected using the same stimuli later used for emotion decoding, or
- PC selection was performed independently within training folds and evaluated on held-out stimuli.

A reviewer may ask whether the downstream emotion decoding is biased by subspace selection.

### Recommended fix

If the analysis was done with proper fold-wise or nested independence, add this sentence to Methods:

> Brain-aligned PCs were selected within the training folds only, and emotion decoding was evaluated on held-out stimuli to avoid optimistic bias from subspace selection.

### Important

Only add this sentence if it accurately reflects the actual analysis.

If the analysis did not use independent PC selection and evaluation, do not claim it did. In that case, leave the Methods as they are and keep the Discussion claims cautious.

---

## 3. Specify the emotion decoding model and cross-validation scheme

### Issue

The Methods currently state:

> From this subspace we decoded 34 emotion categories and, among the 14 affective dimensions, focused on valence and arousal...

This does not specify:

- the decoding model
- whether decoding used cross-validation
- whether the same 5-fold scheme was used as the PC prediction analysis

### Recommended fix

Add a short sentence to Methods.

If ridge regression was used:

> Emotion categories and valence-arousal scores were decoded from the selected V-JEPA2 PCs using ridge regression with the same 5-fold cross-validation scheme.

If another model was used, replace “ridge regression” with the correct model.

### Why this matters

The key quantitative result depends on decoding performance, so the decoding procedure should be explicit even in a short extended abstract.

---

## 4. Clarify whether residualization was fold-wise

### Issue

The manuscript says:

> To test whether categorical alignment was reducible to low-level visual or annotated semantic content, we residualized model embeddings with respect to VGG19 (1,000-dim) and human-annotated semantic features (73-dim).

This is better than the previous version, but still slightly underspecified.

A reviewer may ask whether the residualization was done:

- on the full dataset before cross-validation, or
- within training folds and then applied to held-out stimuli.

### Recommended fix

If residualization was performed within the cross-validation procedure, write:

> To test whether categorical alignment was reducible to low-level visual or annotated semantic content, we residualized model embeddings with respect to VGG19 features and human-annotated semantic features within each training fold.

### Important

Only use this wording if it matches the actual pipeline.

If residualization was done on the full dataset, do not write “within each training fold.” In that case, consider either re-running fold-wise residualization or keeping the claim cautious.

---

## 5. Replace “categorical dominance” with softer wording

### Issue

The manuscript still uses the phrase **categorical dominance** in the Abstract, Results, and Discussion.

This phrase is rhetorically strong. The data support a categorical advantage, but “dominance” may sound too forceful given that:

- the absolute ΔR² is modest
- the main comparison is against valence-arousal rather than all possible dimensional structures
- the subspace is selected through brain-model alignment

### Recommended replacement

Use:

- **categorical advantage**
- **category-preferential structure**
- **category-over-valence-arousal advantage**
- **preferential alignment with categorical emotion structure**

### Specific replacements

#### Abstract

Current-style phrase:

> with categorical dominance exceeding that of the full video model space

Recommended:

> with a larger category-over-valence-arousal advantage than in the full video model space

#### Results

Current-style phrase:

> the categorical dominance of the shared subspace was attenuated rather than eliminated

Recommended:

> the categorical advantage of the shared subspace was attenuated rather than eliminated

#### Discussion

Current-style phrase:

> paralleling the categorical dominance Horikawa et al. reported

Recommended:

> paralleling the category-preferential structure reported by Horikawa et al.

---

## 6. Keep the Abstract conclusion as currently softened

### Status

The revised Abstract conclusion is much better:

> These findings suggest that visually shared brain-model representations preferentially preserve category-like emotion structure, whereas dimensional affective information may rely more strongly on brain components not captured by this visual model-aligned subspace.

This is appropriately cautious.

### Recommendation

Keep this general framing. It is stronger and safer than the earlier claim that dimensional structure “resides predominantly outside” the visually shared channel.

---

## 7. Keep the Figure 1B interpretation cautious

### Status

The current Results sentence is improved:

> suggesting that the brain-aligned PCs are enriched for affectively relevant variation

This is a good revision.

### Recommendation

Keep this cautious wording.

Avoid saying that the max |r| analysis “confirms” categorical organization, because taking the maximum over 34 emotion categories can favor category-based structure descriptively.

---

## 8. Current strengths of the revised manuscript

The following elements now look solid:

- The central research question is clear.
- The Abstract has a strong but defensible narrative.
- The Methods are much clearer than before.
- The dataset count is phrased more safely as **stimulus presentations**.
- The use of V-A as a canonical dimensional baseline is now justified.
- The Results now include both the ratio and absolute ΔR².
- The Discussion’s constructionist interpretation is now framed as “one interpretation,” which is appropriately cautious.
- The phrase “may rely more strongly” appropriately softens the dimensional-structure claim.

---

## Final must-do checklist

Before final submission, confirm or fix the following:

- [ ] Page limit: confirm whether references/acknowledgments count toward the 2-page limit.
- [ ] Add decoding model and CV details.
- [ ] Clarify whether PC selection and emotion decoding were independent.
- [ ] Clarify whether residualization was fold-wise.
- [ ] Replace “categorical dominance” with “categorical advantage” or similar softer phrasing.
- [ ] Keep the softened Abstract conclusion.
- [ ] Keep the cautious Figure 1B interpretation.

---

## Minimal final edit recommendation

If only a few edits are possible, prioritize these three:

1. Add one sentence specifying the **emotion decoding model and CV scheme**.
2. Add one sentence clarifying **PC selection vs decoding independence**, but only if true.
3. Replace **categorical dominance** with **categorical advantage** throughout.

After these edits, the manuscript should be in good shape for submission.
