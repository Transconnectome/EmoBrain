# CCN_Emotion

> **2026-07-21 validity note:** The legacy Brain-JEPA extraction averaged 10 fixed
> temporal sin/cos codes into one for a 16-TR input. Brain-JEPA-dependent findings
> below are historical/provisional until corrected frozen extraction and
> SwiFT/NeuroSTORM replication are complete. Raw-BOLD analyses conditioned directly
> on V-JEPA2 and visual-semantic features are unaffected. See `STATUS.md` and
> `study1/code/brain_encoder_validation/`.

**Fine-grained emotion structure in the brain-predictable subspace of a self-supervised video model.**

CCN 2026 accepted poster (Moon, August 2026, New York). Camera-ready deadline 2026-06-11 AoE.

---

## Current poster direction (2026-07-21)

> **How does the cortical hierarchy transform video-foundation-model representations into affective brain representations?**

The shared V-JEPA2/Brain-JEPA subspace is an estimator of cross-domain information. The primary poster analysis localizes that shared channel in raw BOLD and tests where continuous fine-grained affective profiles add variance beyond shared and full-video representations. See `notes/poster_update_visual_semantic_subspace.md` and `notes/long_term_research_roadmap.md`.

## Accepted-abstract positioning (historical, 2026-05-26)

**Brain validation of the affectless machines hypothesis** (Conwell et al., 2025; Bao et al., 2024).

Two recent findings establish that self-supervised visual models develop emotion-relevant representations as an emergent property of natural visual statistics, without any emotion supervision. Bao et al. (2024) showed this inside the model (object-recognition CNNs develop emotion-selective internal neurons). Conwell et al. (2025) showed it in behavior (affectless visual models explain a majority of variance in human affective ratings). Neither showed it in brain.

CCN_Emotion fills that gap. The operational question:

> **Does the emergent emotion representation that arises in a self-supervised video model coincide with the visual representation that the human brain uses when processing emotional video?**

This is testable as a subspace-overlap question within V-JEPA2. The brain-aligned subspace (M1, V-JEPA2 PCs predictable from Brain-JEPA) and the emotion-encoding subspace (M2, V-JEPA2 PCs that predict emotion ratings) are quantified separately; their overlap (M3) is the central finding. High overlap supports the affectless machines hypothesis at the neural level. Disjoint subspaces bound the hypothesis to model internals and behavior, supporting a reentry view of emotion construction.

Full framework: [Paper/framework_EN.md](Paper/framework_EN.md) / [Paper/framework_KR.md](Paper/framework_KR.md).

---

## Project narrative (the story in 8 steps)

**1. What we observed.** V-JEPA2 is a self-supervised video model that has never seen an emotion label. We took its 100 leading principal components on 2,196 emotional video clips and asked which of them are linearly predictable from people's brain responses, encoded by Brain-JEPA. Only three components survived statistical correction. Inside those three, videos cluster more sharply by 34 discrete emotion category labels than they spread along arousal-valence dimensions (ratio 1.44 vs 1.26 in the full V-JEPA2 space). The pattern is stable across all five subjects.

**2. What the abstract claimed, and why that was a leap.** The abstract named this 3-PC region an "affective subspace" and interpreted it as evidence that emotion schemas are embedded in visual statistics. Re-reading it carefully, two interpretive leaps sit between the measurement and the claim. **Leap 1**: the three PCs are V-JEPA2 visual feature axes by construction. Calling them "affective" presumes the categorical clustering reflects affect-relevant structure rather than visual category statistics (faces, scenes, motion patterns) that happen to co-vary with emotion category labels in the Cowen-Keltner stimulus set. **Leap 2**: the cited support (Kragel 2019, Conwell 2025) does not establish the mechanism for a self-supervised video model. Kragel used a supervised emotion classifier; Conwell used behavior with no brain data.

**3. What is honestly there.** Without those leaps, what the data establish is a **category-friendly visual readout channel between V-JEPA2 and the subject-invariant brain response**. Three visual feature axes in V-JEPA2 are tracked by the brain, and along those axes the videos in this stimulus set separate by emotion category label more than they vary by continuous affect. That is the empirical finding.

**4. What we actually want to know.** Given the honest finding, the central question is whether the brain-readable visual information is:
(a) generic visual recognition (objects, scenes, faces, motion) that happens to co-vary with emotion category labels,
(b) something beyond generic visual recognition that is still present in any vision model, or
(c) something that self-supervised video pretraining specifically produces as an emergent representation.

**5. How we answer.** Two control experiments, in nested order. **Control 1 (Pillar 2)**: partial out generic visual baselines (DINOv2 for objects, Places365 for scenes, optical flow for motion, Sadeghi 2024 low-level statistics) and see whether the categorical-vs-dimensional ratio survives. If it disappears, scenario (a) is confirmed. **Control 2 (Pillar 3)**: run the full pipeline on untrained V-JEPA2 (random initialization), ImageNet-supervised ViT-L, and VideoMAE. If V-JEPA2 stands alone, scenario (c) is supported. If all baselines produce similar ratios, scenario (b) is the right reading.

**6. Three possible endings, all honest.** Scenario (c) gives a NeurIPS or Nature Communications level finding (self-supervised video pretraining produces brain-readable affect-relevant visual structure as an emergent property). Scenario (b) gives the brain version of Conwell 2025 (any visual representation contains category-organized affect structure beyond standard tasks). Scenario (a) closes the project at CCN poster level and forces a camera-ready softening. The point is not to land on a preferred ending. The point is to actually find out.

**7. Why this matters, to three audiences.** For **affective neuroscience**, this updates Kragel et al. (2019)'s "emotion schemas in visual cortex" result with a self-supervised model, removing the circularity that comes from emotion-supervised classifiers and providing direct evidence on the constructionist debate over whether visual representation is a neutral ingredient (Barrett 2017) or already affect-relevant. For **AI and machine learning**, it asks whether self-supervised video pretraining is "general visual learning" or whether natural-video statistics implicitly carry emergent affect-relevant structure. For **methodology**, it introduces brain-predictable subspace identification as a within-model interpretability tool, the natural within-model dual of Sartzetaki et al. (2025, ICLR)'s across-model alignment decomposition.

**8. How this sits in the literature.** The direct empirical benchmark is **Horikawa et al. (2020)** because we use the same dataset and the same fundamental question, with their primitive 2020-era visual baseline upgraded to a foundation-model lens. The methodological benchmark is **Sartzetaki et al. (2025, ICLR)** because they decomposed video-to-brain alignment across 100 models and we decompose alignment within one model. EmoViS (a separate project on the same dataset) handles the across-model emotion question; CCN_Emotion handles the within-model decomposition. The two projects are complementary, not redundant.

### One-line summary

A self-supervised video model that never saw an emotion label nonetheless has a small piece of its representation that the brain tracks, and inside that piece videos cluster along discrete emotion categories more than along continuous affect. Whether that is a trivial reflection of how emotion videos are visually clustered, or evidence that self-supervised video learning produces an emergent affect-relevant visual representation, is what the follow-up controls are designed to decide.

---

## What this project asks

A self-supervised video model (V-JEPA2) learns visual representations from billions of frames with no emotion supervision. When we ridge-regress those representations onto whole-brain fMRI embeddings (Brain-JEPA) of people watching emotional video clips, a small set of directions in V-JEPA2 turns out to be linearly predictable from the brain.

**What does this brain-predictable subspace of V-JEPA2 actually represent?**

The empirical finding in the CCN abstract is that this subspace, despite being compact (3 PCs survive FDR after Brain-JEPA → V-JEPA2 ridge), is more categorically organized than dimensionally organized: categorical (34 Cowen-Keltner emotion categories) mean R² is 1.44× higher than dimensional (arousal-valence) mean R², compared to 1.26× in the full V-JEPA2 100-PC space. The pattern is stable across all 5 subjects in Horikawa et al. (2020) and attenuated but preserved after partialling out VGG19 visual features and a 73-dim semantic feature set.

The abstract framed this as "self-supervised learning spontaneously produces a categorically organized affective subspace." That framing requires baseline controls the abstract does not include. The follow-up project is to test the claim rigorously.

---

## The honest framing (2026-05-26)

V-JEPA2 only sees video. Therefore Brain-JEPA ↔ V-JEPA2 alignment is, by construction, visual statistics. The interesting question is not "is the alignment visual?" (yes, trivially) but **what kind of visual structure is brain-readable?**

This is the within-model dual of the question Sartzetaki et al. (2025, ICLR) "One Hundred Neural Networks and Brains Watching Videos: Lessons from Alignment" asked across models. Sartzetaki asked which model properties (temporal processing, action classification, FLOPs) determine video-to-brain alignment. CCN_Emotion asks which components within V-JEPA2 carry the brain-aligned signal, and whether that signal is reducible to generic visual baselines or specific to self-supervised video pretraining.

### Three pillars

1. **Existence.** A compact, brain-readable subspace of V-JEPA2 exists (3 PCs survive FDR). Already shown in the abstract.

2. **Specificity.** The categorical organization of this subspace survives controls for generic visual baselines (low-level statistics, object recognition, scene categorization, motion energy). The abstract has only a partial test (VGG19 + 73-dim semantic). The follow-up needs DINOv2 (object), Places365 (scene), and optical flow (motion) as additional confound terms.

3. **Self-supervised contribution.** Untrained ViT and ImageNet-supervised ViT baselines do not produce the same categorical-vs-dimensional pattern in their brain-aligned subspaces. The abstract does not test this. The follow-up needs untrained V-JEPA2 (random init), ImageNet-supervised ViT-L, and ideally VideoMAE comparison.

If Pillars 2 and 3 hold, the brain-readable subspace of V-JEPA2 carries category-organized visual structure that is neither captured by standard visual recognition tasks nor produced by random or supervised baselines. That is a defensible "self-supervised video pretraining contains an affective visual signal" claim. Without Pillars 2 and 3, the abstract overclaims.

### Forbidden phrasings

- "Self-supervised learning spontaneously produces a categorical subspace" (without Pillar 3 baselines)
- "The brain is categorical" (the analysis is about the visual-to-brain mapping, not the brain itself)
- "Subjective emotion is categorical" (no behavioral measurement here)
- "V-JEPA2 learned emotion" (V-JEPA2 has no emotion supervision)
- "Brain reads out emotion structure from V-JEPA2" without precise definition of "emotion structure"

See `notes/narrative_v2.md` for full reasoning.

---

## Relation to EmoViS

[EmoViS](../EmoViS/) is a separate project (not derivative of this one) that uses the same Horikawa dataset to ask a broader question: across a sensory-to-semantic model spectrum (VideoMAE, DINOv2, V-JEPA2, CLIP, Caption+LLM), which family best matches stimulus-level brain geometry built directly from raw BOLD?

The three projects compose into one logical chain:

- **Sartzetaki 2025 (ICLR)** — across 100 models, what makes video-to-brain alignment? *Anchor for "what does alignment mean."*
- **EmoViS** — across sensory-to-semantic model spectrum, what aligns with stimulus-level emotional brain geometry? *Across-model emotion alignment.*
- **CCN_Emotion (this project)** — within V-JEPA2, what component does the brain read out, and is it reducible to generic visual baselines? *Within-model emotion alignment.*

CCN_Emotion and EmoViS share data (Horikawa fMRI, V-JEPA2 features) but answer different questions.

---

## Repository layout

```
CCN_Emotion/
├── CLAUDE.md                    project-level instructions (folder rules, narrative, data facts)
├── README.md / README_KR.md     this file
├── .gitignore
├── Paper/                       accepted abstract + (forthcoming) camera-ready materials
│   └── ccn2026_accepted.pdf
├── notes/                       narrative memos, camera-ready plan
│   ├── narrative_v2.md          full three-pillar narrative + Sartzetaki anchor
│   ├── camera_ready_plan.md     6/11 mechanical + text fixes
│   └── archive/                 superseded direction docs, old result summaries
├── data/
│   └── raw/                     raw inputs (.gitignored where appropriate)
│       ├── brain_embeddings/      Brain-JEPA 768-dim, 5 subj × 2196
│       ├── video_embeddings/      V-JEPA2 1408-dim + CLIP 512-dim
│       ├── videos/                CowenEmotionVideos (2196 mp4)
│       ├── feature/               Horikawa .mat features (category, dimension, vision, semantic)
│       ├── raw_fmri/fmri_raw.npy  5 × 2196 × 450 parcels
│       ├── semantic_features.csv
│       └── vision_features.csv
├── logs/                        project-wide SLURM logs
├── study1/                      main poster/paper workstream
│   ├── README.md                active pipeline overview
│   ├── code/
│   │   ├── shared_alignment/
│   │   ├── affective_characterization/
│   │   ├── cortical_transformation/
│   │   └── archive/             legacy, robustness, figures, extraction
│   ├── data/                    module outputs + archived intermediates
│   ├── archive/reports/         historical result reports
│   ├── logs/
│   └── results/                 accepted abstract, cortical analysis, archive
└── study2_thesis/               parallel thesis chapter workstream (separate scope)
    ├── code/                    ch1, ch2 analyses (Glasser parcellation, ROI decoding, gradient, VP)
    ├── data/, results/, figures/, logs/, reference/, storyline/
```

---

## Cleanup history (2026-05-26)

Before this date the directory had three workstreams tangled at the root:

- Workstream A (root-level `01_~07_*.py`, `RESULTS_FULL.md`, `RESULTS_SUMMARY.md`, `CCN_draft.md`): the older V-JEPA2-vs-CLIP overall + per-emotion CKA analysis. The accepted abstract pivoted away from this framing.
- Workstream B (`CCN2026/`): the brain-predictable subspace analysis that became the CCN paper.
- Workstream C (`main/`, `storyline/`): thesis chapter analyses (ROI decoding, principal gradient, variance partitioning).

Reorganization:
- Workstream B → `study1/` (this is the CCN paper).
- Workstream C → `study2_thesis/`.
- Workstream A analysis scripts and ~226 MB of derived outputs (`cka_results/`, `subject_blocks/`, `raw_fmri_outputs/`, old `figures/`) were deleted on user instruction. Reusable extraction utilities are retained under `study1/code/archive/extraction/`.
- Raw inputs consolidated under `data/raw/`.
- Accepted PDF → `Paper/ccn2026_accepted.pdf`.
- One-time metadata helpers and the `CowenEmotionVideos.zip` (1.7 GB redundant copy of the unzipped `videos/`) → deleted.

Total size: 4.0 GB → 2.1 GB.

For details of what is in each archive subdirectory and why it was kept or removed, see `study1/code/archive/README.md`.

---

## Where the project is going

### Tier 0 — Camera-ready (deadline 2026-06-11)
Text-level revisions only ("not intended to be a significant revision"). Soften the "spontaneously produces" claim, add concrete statistics for ratio comparison and partial R², add 1-sentence limitation acknowledging baseline gap. Mechanical work: new LaTeX template, deanonymization, LLM-use disclosure. See `notes/camera_ready_plan.md`.

### Tier 1 — Pillar 2 baseline controls (2026-05-26 to 2026-06-02)
Extract DINOv2 (object), Places365 (scene), and optical flow (motion) features. Compute partial R² of V-JEPA2 brain-predictable subspace after partialling out each baseline. Goal: show that the categorical organization is not absorbed by any single standard visual recognition task. Results go in the August poster as supplementary panels.

### Tier 2 — Pillar 3 model baselines (2026-06-03 to 2026-06-16)
Extract embeddings from untrained V-JEPA2 (random init, same architecture), ImageNet-supervised ViT-L, and VideoMAE. Run the full pipeline (100 PCs → ridge → categorical/dimensional ratio) on each. Goal: show that the brain-aligned categorical organization is specific to self-supervised video pretraining, not architecture or any pretraining at all. Results go in the August poster.

### Tier 3 — Mechanistic depth (2026-06-17 to 2026-08-03)
Layer-wise V-JEPA2 (blocks 4, 8, ..., 40) brain-aligned ratio. Brain-region-wise breakdown (Schaefer parcels, networks). PC1 stimulus interpretation (top-k similar/dissimilar videos). Noise ceiling from split-half reliability of Horikawa fMRI. These mature the story for the August poster presentation.

### Tier 4 — Full paper (post-poster)
Cross-validation re-design, cross-dataset replication (Kragel emotion fMRI if accessible), decoding accuracy, theoretical framing alignment with Barrett constructionism vs Sartzetaki cross-model alignment results. Target venue TBD (NeurIPS, Nature Communications, or similar).

---

## Core references

- **Horikawa et al. (2020)** — fMRI dataset; 5 subj × 2196 emotional video clips.
- **Cowen & Keltner (2017, *PNAS*)** — 27-category emotion taxonomy and the video stimulus pool.
- **Assran et al. (2025)** — V-JEPA 2 (the self-supervised video model under analysis).
- **Kim et al. (2024, *NeurIPS*)** — Brain-JEPA brain foundation model.
- **Sartzetaki et al. (2025, *ICLR*)** — anchor reference for "what does brain alignment mean": 100 video models × brain, what determines alignment.
- **Conwell et al. (2025, *PNAS*)** — affectless visual machines explain visually evoked affective behavior (behavioral precedent for "alignment is visual").
- **Doerig et al. (2025, *Nature Machine Intelligence*)** — LLM caption embeddings align with high-level visual brain (semantic side neural precedent).
- **Kornblith et al. (2019, *ICML*)** — CKA representational similarity metric.
- **Kriegeskorte et al. (2008)** — RSA foundational paper.
