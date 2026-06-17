# CCN_Emotion — Theoretical Framework (English)

**Last updated: 2026-05-26**
**Positioning: Brain validation of Conwell/Bao affectless machines hypothesis.**

> Self-supervised visual models develop emotion-relevant representations as an emergent property of natural visual statistics, without any emotion supervision. Whether the human brain's visual processing of emotional video uses these emergent representations is unknown.

---

## 1. Background — the story

### 1.1 A standing question in affective neuroscience

When the brain processes an emotional video, what does its visual representation organize? Two views compete.

**Reentry view (classical)**: Visual cortex extracts generic visual features (objects, scenes, motion). Emotion category is assigned downstream by limbic and prefrontal regions through reentrant feedback. Visual processing itself is affect-neutral.

**Intrinsic view (Kragel et al., 2019)**: Visual cortex already encodes emotion-relevant structure. Kragel and colleagues showed that a CNN trained on emotion category labels produces internal representations that align with visual cortex fMRI, with 15+ emotion categories decodable from visual cortex alone. Visual processing is intrinsically affect-relevant.

The Kragel evidence has a circularity problem: the CNN was trained with explicit emotion labels. Whether visual cortex aligns with emotion structure because natural visual statistics contain that structure, or only because supervised training imposed it on the model, is unresolved.

### 1.2 Recent evidence pointing to intrinsic emotion in visual representation

Two recent findings shift the debate, both pointing toward intrinsic emotion in visual statistics, both stopping short of brain validation.

**Bao et al. (2024, PLoS Computational Biology)** trained CNNs on object recognition only, with no emotion supervision, and found that internal neurons spontaneously develop emotion-selective responses. The visual hierarchy that emerges from natural statistics + object-recognition objectives contains emotion-relevant computation as a byproduct.

**Conwell et al. (2025, PNAS)** "The perceptual primacy of feeling: affectless visual machines explain a majority of variance in human visually evoked affect" tested 180 visual models trained without emotion supervision against human arousal and valence ratings. The affectless models explained the majority of variance in human affective behavior — as well as emotion-supervised models. The conclusion: visual representations developed from emotion-free training contain enough structure to explain how humans feel about images.

These two findings establish the **affectless machines hypothesis**: emergent emotion-relevant representations arise in visual learning systems without any emotion supervision.

### 1.3 Broader context: representational alignment as a research paradigm

The affectless machines findings sit within a larger and rapidly growing line of work on *representational alignment* — the systematic comparison and active matching of model representations against human cognitive structure (Sucholutsky et al., 2023). Muttenthaler et al. (2025, *Nature*) demonstrated that vision foundation models do not naturally capture the multi-level conceptual hierarchy that humans use (animal vs vehicle vs furniture, then within-animal dog vs bird, then within-dog poodle vs golden retriever), but this misalignment can be repaired by fine-tuning on human-similarity-distilled supervision (AligNet), with concurrent improvement in downstream machine learning performance. Their finding — that natural model representations are sparsely aligned with human-relevant structure without explicit intervention — frames our own sparse brain-alignment observation (3 of 100 V-JEPA2 PCs survive in the brain-aligned subspace) as part of a broader pattern.

The remaining question is whether the small brain-aligned subspace, despite its sparsity, nonetheless carries emotion-specific information. That is the question this project addresses.

### 1.4 The missing piece

Bao 2024 examined model internals. Conwell 2025 examined behavior. Neither examined brain. The crucial question — whether the emergent emotion representation in affectless models is actually used by the human brain during visual emotion processing — remains open.

If brain uses these emergent representations: the affectless machines hypothesis extends from model internals + behavior to neural representation. Visual cortex would not need dedicated emotion training, supervised or otherwise; it could rely on the same emergent emotion-relevant structure that affectless models develop.

If brain does not use these emergent representations: the affectless emotion structure is a property of models and behavior but not of neural representation. Visual cortex would process emotional video using different dimensions, and the emergent emotion structure observed by Bao and Conwell would be model-specific, not biologically grounded.

This question has not been answered. CCN_Emotion addresses it directly.

---

## 2. Research Question

> **Does the emergent emotion representation that arises in self-supervised and visual-text foundation models coincide with the visual representation that the human brain uses when processing emotional video, and does this differ between learning paradigms?**

We probe two primary models in parallel: V-JEPA2 (self-supervised video, no language) and CLIP (image-text contrastive). The comparison is motivated by empirical observation from the FEELIN project that CLIP outperforms V-JEPA2 in emotion prediction probes across all tasks (Valence regression Pearson r 0.683 vs 0.470, Cat34 top-1 balanced accuracy 0.383 vs 0.293). This raises the question: is the brain-aligned subspace and its overlap with emotion-encoding subspace different between these two learning paradigms, and does that difference reveal whether text supervision provides emotion-relevant structure that pure visual SSL does not?

Operationally, this becomes a question about the relationship between two subspaces of a single video model.

- **Brain-aligned subspace** of V-JEPA2: the principal components of V-JEPA2 representation that can be linearly predicted from Brain-JEPA fMRI representation (or directly from BOLD, in the secondary track).
- **Emotion-encoding subspace** of V-JEPA2: the principal components of V-JEPA2 representation that linearly predict emotion ratings (categorical labels and arousal-valence dimensions).

The empirical question is whether these two subspaces overlap. If they do, the brain validates the emergent emotion representation. If they do not, the affectless emotion structure remains a model-specific finding.

Stated as a single sentence the analysis can answer: **does brain's visual processing of emotional video organize videos along the dimensions that encode emotion, or along dimensions that are independent of emotion encoding?**

---

## 3. Hypotheses

Three primary hypotheses, formulated to be testable with the M1/M2/M3 framework.

**H1 (Brain selects sparsely from the model)**. A small subset of V-JEPA2 principal components is linearly predictable from brain representation. The full model representation contains 1,408 dimensions; brain-aligned dimensions are sparse.
*Operational measurement*: M1 — Brain-JEPA → V-JEPA2 PC ridge regression with permutation-based FDR.
*Current status*: established in the accepted CCN abstract (three of 100 PCs survive; R² clipping robustness check pending in Exp 29).

**H2 (Model encodes emotion in some dimensions)**. A subset of V-JEPA2 principal components encodes emotion information well, despite no emotion supervision in training. This is the within-V-JEPA2 instantiation of the affectless machines hypothesis (Conwell et al., 2025; Bao et al., 2024).
*Operational measurement*: M2 — V-JEPA2 PCs → emotion ratings ridge regression and decoding (continuous R², top-k accuracy, ROC-AUC).
*Current status*: not yet measured. Pending Exp 30.

**H3 (Brain-aligned subspace overlaps with emotion-encoding subspace)**. The principal components that brain reads from V-JEPA2 are the same components that encode emotion in V-JEPA2. The two subspaces overlap rather than being disjoint.
*Operational measurement*: M3 — set intersection, Jaccard coefficient, Spearman rank correlation between brain-aligned PC ranking and emotion-encoding PC ranking.
*Current status*: requires both M1 and M2. The core test of the project.

A supplementary hypothesis tests specificity to self-supervised video pretraining.

**H4 (Self-supervised contribution)**. The H3 overlap is specifically large for V-JEPA2 (self-supervised video model) and not for untrained ViT, ImageNet-supervised ViT-L, or VideoMAE. If the overlap is similar across all visual models, the emergent emotion structure is generic to visual learning rather than specific to self-supervised video learning.
*Current status*: requires architecture baseline embedding extraction. Pending Exp 31 series.

---

## 4. Outcome interpretation

The interpretation of M3 is the heart of the project. Three principal outcomes correspond to three distinct scientific conclusions.

**Outcome A — High overlap (brain-aligned ⊆ emotion-encoding, or large Jaccard)**.
*Statement*: Brain reads precisely the V-JEPA2 components that encode emotion. The dimensions along which brain differentiates emotional videos are the dimensions along which emotion can be decoded.
*Implication*: The affectless machines hypothesis extends to brain. Emergent emotion representation in self-supervised visual learning is biologically grounded; visual cortex uses this same kind of emergent structure when processing emotional video. Kragel et al. (2019) is strengthened with the supervision circularity removed.

**Outcome B — Disjoint subspaces (low Jaccard, low rank correlation)**.
*Statement*: Brain reads V-JEPA2 components that do not encode emotion well. Emotion-encoding components exist in V-JEPA2 but the brain attends to different dimensions.
*Implication*: The affectless machines hypothesis is bounded to model internals and behavior; it does not extend to brain. Visual cortex processes emotional video along dimensions distinct from emotion-relevant variation, consistent with the reentry view in which emotion is constructed downstream of visual processing.

**Outcome C — Partial overlap**.
*Statement*: Brain reads a mixture of emotion-encoding and emotion-orthogonal components.
*Implication*: Mixed support. Visual processing contributes partially to emotion processing but is not fully organized by it. Quantitative comparison with H4 baselines determines whether the partial overlap is specific to self-supervised video or generic to vision learning.

All three outcomes are scientifically informative. The project is designed to be informative under any outcome.

---

## 5. Method overview

### 5.1 Data

The Horikawa et al. (2020) dataset: 5 participants, **2,185 emotionally evocative video clips** (canonical Horikawa master index after excluding 11 repeated clips at stim_idx 2185–2195), continuous emotion ratings for 34 categories and 14 affective dimensions per video. Stimulus count is consistent with EmoViS and FEELIN projects in the same group.

### 5.2 Representations

**Dual primary video models** (both analyzed in full M1/M2/M3 pipeline):

- **V-JEPA2** (Assran et al., 2025): self-supervised video foundation model trained on 1M+ hours of video without emotion labels. ViT-G, 1,408-dimensional embedding per video, 16 uniformly sampled frames mean-pooled over spatial tokens. Affectless machines hypothesis instance.
- **CLIP** (Radford et al., 2021): visual-text contrastive pretraining. `openai/clip-vit-large-patch14`, image encoder only (text tower not used in this study), 1,024-dim, 3 frames at 25/50/75% of clip duration mean-pooled. Text-mediated emotion hypothesis instance.

Both embeddings sourced from EmoViS extraction pipeline (2185 stimuli, identical sampling and master index).

**Brain side**:
- **Brain-JEPA** (Dong et al., 2024): fMRI foundation model pretrained on UK Biobank, produces 768-dimensional subject-invariant representations per video. Primary track.
- **Raw BOLD (secondary track)**: 450-parcel Schaefer parcellation, used as alternative brain representation to test BFM-encoding robustness.

**Pillar 3 baselines** (also reusable from EmoViS): untrained V-JEPA2 (random init), untrained CLIP, DINOv2 (object SSL), VideoMAE (other video SSL). All at (2185, *) consistent with primary models.

### 5.3 Three measurements

**M1 — Brain-aligned subspace identification**. Reduce V-JEPA2 to 100 PCs. Ridge-regress each PC on subject-mean Brain-JEPA representation with 5-fold cross-validation. Permutation test (n=1,000) with FDR correction. Surviving PCs define the brain-aligned subspace.

**M2 — Emotion-encoding subspace identification**. For each V-JEPA2 PC, predict 34 emotion category ratings and 2 arousal-valence dimensions via ridge regression and decoding. Multiple metrics:
- Continuous regression: ridge R², Pearson r (against mean rater scores)
- Categorical decoding: top-1 accuracy, top-5 accuracy, ROC-AUC (against top-rated category per video)
Rank PCs by emotion-encoding performance.

**M3 — Subspace overlap**. Quantify the relationship between M1 and M2:
- Set intersection: |M1 PCs ∩ top-K M2 PCs|
- Jaccard coefficient
- Spearman rank correlation between PC orderings (brain-aligned R² vs emotion-encoding accuracy)
- Permutation null: compare observed overlap against random PC selection

### 5.4 Controls

**Visual baseline partial-out (Pillar 2)**: After partialling DINOv2 (object), Places365 (scene), optical flow (motion), and Sadeghi 139 (low-level statistics) out of V-JEPA2 PCs, recompute M1, M2, M3. Tests whether the overlap is reducible to generic visual category structure.

**Architecture baselines (Pillar 3)**: Repeat the entire M1/M2/M3 pipeline for untrained V-JEPA2 (random init), ImageNet-supervised ViT-L, and VideoMAE. Tests whether the overlap is specific to self-supervised video pretraining.

**Brain representation track (Pillar 4)**: Repeat with raw BOLD (450 parcels) as brain side. Tests whether the overlap is specific to BFM-encoded brain or generalizes to raw fMRI.

---

## 6. The leap problem in the accepted abstract

The accepted CCN abstract names the brain-aligned subspace an "affective subspace" and interprets it as "emotion schemas embedded within statistical regularities of the visual environment" (citing Kragel 2019, Conwell 2025). Both are interpretive moves that the data of the abstract alone do not support.

**Leap 1 (naming)**: V-JEPA2 PCs are visual feature axes by construction. Calling brain-aligned PCs "affective" requires showing that those PCs encode emotion-relevant information, not generic visual category statistics. The abstract does not test this directly. This is the gap M2 fills.

**Leap 2 (mechanism via citation)**: Kragel 2019 used supervised emotion classifier; Conwell 2025 used behavior only. Neither directly tests whether brain uses emergent emotion representation in a self-supervised model. Citing them as mechanism for our finding requires the M3 overlap analysis they did not have.

The current framework converts these leaps from interpretive assumptions into testable hypotheses. H2 tests Leap 1 (model emotion-encoding). H3 tests Leap 2 (brain-emotion overlap). H4 tests the additional specificity claim.

Until M1, M2, M3 are all measured and the overlap quantified, the brain-aligned subspace is most honestly described as a **brain-aligned visual subspace of V-JEPA2** without emotion attribution.

---

## 7. Differentiation from EmoViS

EmoViS, a separate project that uses the same Horikawa dataset, is a test of Barrett's constructionist framework. Its central claim is that brain's stimulus-level representational geometry follows the continuous sensory-semantic structure of stimuli rather than the discrete emotion ratings observers assign post hoc. The theoretical anchor is Barrett (2017) and Lindquist & Barrett (2012); the comparison is between a sensory-to-semantic model spectrum (VideoMAE → DINOv2 → V-JEPA2 → CLIP → Caption-LLM) and emotion ratings as competing accounts of brain geometry.

CCN_Emotion has a distinct theoretical anchor: the affectless machines hypothesis from Conwell et al. (2025) and Bao et al. (2024). Its central claim is that emergent emotion representation in self-supervised visual learning is biologically grounded — that brain actually uses these emergent representations during emotional video processing. The comparison is not across model families; it is within a single self-supervised video model (V-JEPA2), asking whether the brain-aligned and emotion-encoding subspaces coincide.

| | EmoViS | CCN_Emotion |
|---|---|---|
| Theoretical anchor | Barrett 2017 constructionism | Conwell 2025 + Bao 2024 affectless machines |
| Central debate | Is brain emotion-geometry organized by sensory-semantic ingredients or by linguistic categorization? | Does brain validate emergent emotion representation in affectless models? |
| Comparison structure | Across model family (visual-semantic spectrum vs ratings) | Within-model subspace overlap (brain-aligned vs emotion-encoding) |
| Brain side | Raw BOLD stimulus-level RDM | Brain-JEPA (track A) + raw BOLD (track B) |
| What different outcomes would tell us | Whether brain follows ingredients (H1) and how that varies across cortex (H2) | Whether affectless machines hypothesis extends to brain (H3) and whether SSL video is specifically responsible (H4) |

The two projects share the dataset and one model (V-JEPA2) as analytical resources, but answer questions in different theoretical traditions.

---

## 8. Contribution

### 8.1 Method-level contribution (independent of outcome)

A framework for testing the brain validation of emergent representations in self-supervised models. Brain-aligned subspace identification + emotion-encoding subspace identification + subspace overlap analysis is a general pattern, applicable to any model trained without supervision for a target capability, asking whether brain uses the emergent target representation.

This pattern is the natural within-model dual of Sartzetaki et al. (2025, ICLR), who decomposed brain alignment across 100 video models and identified which model properties drive alignment. CCN_Emotion decomposes alignment within a single model and asks whether the brain-aligned components carry the target capability (emotion).

### 8.2 Finding-level contribution (outcome dependent)

Three principal contributions, one per outcome:

**If Outcome A (high overlap)**: First brain-direct evidence that the affectless machines hypothesis (Conwell 2025, Bao 2024) extends to neural representation. Self-supervised video pretraining produces emotion-relevant visual structure that visual cortex uses. Kragel et al. (2019) intrinsic-emotion finding is replicated without supervision circularity.

**If Outcome B (disjoint)**: First demonstration that the affectless machines hypothesis is bounded to model internals and behavior. Brain processes emotional video along dimensions different from those that encode emotion in the model. Supports the reentry view that emotion is constructed downstream of visual processing.

**If Outcome C (partial)**: Quantitative characterization of the partial overlap. With H4 baselines, identification of which visual representations contribute more to brain's emotion processing than others.

All three outcomes are publishable, calibrated against the question framework.

---

## 9. Forbidden phrasings

To prevent the same drift that produced the leap problem in the accepted abstract.

- "Brain-aligned subspace is an affective subspace" — requires H2 + H3, not just M1.
- "Self-supervised learning spontaneously produces an affective representation" — requires H4 (specificity to SSL video) on top of H2+H3.
- "Brain reads out emotion structure from V-JEPA2" — replace with "brain-aligned PCs of V-JEPA2 carry/do-not-carry emotion-encoding signal," depending on M3 outcome.
- "The brain is categorical for emotion" — out of scope. The analysis concerns the visual-to-brain mapping, not brain organization at large.
- "Subjective emotional experience is categorical" — out of scope. No behavior or phenomenology in the analysis.
- "Brain follows X" / "Brain tracks X" — replace with precise terminology: "X is linearly predictable from brain representation" or "brain representation is linearly predictable from X."

---

## 10. Core References

| Paper | Role |
|---|---|
| Conwell et al. (2025, *PNAS*) | Central theoretical anchor — affectless visual machines explain affective behavior |
| Bao et al. (2024, *PLoS Comp Bio*) | Affectless emotion-selectivity emergence in object-recognition CNNs |
| Kragel et al. (2019, *Science Advances*) | Intrinsic emotion in visual cortex — supervised, our project removes the supervision circularity |
| Horikawa et al. (2020, *iScience*) | Dataset, brain categorical organization baseline |
| Cowen & Keltner (2017, *PNAS*) | Emotion taxonomy, stimulus pool |
| Assran et al. (2025) | V-JEPA 2 (the self-supervised video model under analysis) |
| Dong et al. (2024, NeurIPS) | Brain-JEPA fMRI foundation model |
| Sartzetaki et al. (2025, *ICLR*) | Methodological anchor — across-model alignment decomposition; we are its within-model dual |
| Doerig et al. (2025, *Nat Mach Intell*) | Caption-LLM brain alignment for generic scenes; precedent for ML-to-brain pipelines |
| Kornblith et al. (2019, *ICML*) | CKA representational similarity metric |
| Kriegeskorte et al. (2008, *Frontiers Sys Neurosci*) | RSA foundation |
| Lindquist & Barrett (2012) | Background reference — reentry view of emotion construction |
| Sadeghi et al. (2024) | Low-level visual feature baseline for Pillar 2 partial-out |
| Muttenthaler et al. (2025, *Nature*) | Representational alignment paradigm; models naturally miss multi-level human-relevant structure but can be repaired via fine-tuning; brain-tuning analog (Moussa et al., 2025) is a future direction |
| Sucholutsky et al. (2023, *arXiv*) | "Getting aligned on representational alignment" — defines the broader research program our project sits within |
| Moussa et al. (2025, *ICLR*) | Brain-tuning of speech models — methodological analog if M3 reveals disjoint subspaces, motivating future brain-side intervention |
