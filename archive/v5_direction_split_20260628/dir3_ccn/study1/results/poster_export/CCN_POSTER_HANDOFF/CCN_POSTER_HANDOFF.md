# CCN Poster Offline Handoff

Snapshot date: 2026-07-22

Project: CCN analysis only, under `EmoBrain/archive/v5_direction_split_20260628/dir3_ccn`

Repository commit at export: `fabeaff` plus uncommitted CCN poster-export changes

This folder is a self-contained handoff for poster production after the server becomes unavailable. It contains final figures, source tables, exact run configurations, the confirmed shared-alignment null distribution, corrected Brain-JEPA provenance, and the analysis scripts used to produce the results.

## 1. Download This Folder

Download the entire `CCN_POSTER_HANDOFF` folder or the adjacent ZIP archive. Do not download only screenshots because the PDF versions are preferable for poster layout.

Required poster assets:

| File | Role | Recommendation |
|---|---|---|
| `figure_1_framework.pdf` | Foundation-model framework | Use in Methods/Overview if space allows |
| `figure_2_corrected_shared_channel.pdf` | Confirmed video-brain shared dimensions | Main Result 1 |
| `figure_3_content_affect_partition.pdf` | Content-controlled affect result | Main Result 2, strongest control |
| `figure_4b_corrected_cortical_brain_maps.pdf` | Corrected cortical brain maps | Main neuroscience figure and visual centerpiece |
| `figure_4_corrected_cortical_networks.pdf` | Yeo-network summaries | Main Result 3 |
| `figure_3b_content_affect_brain_maps.pdf` | Content-controlled raw-BOLD brain maps | Optional or supplementary panel |

Every PDF has a 300-dpi PNG counterpart for software that handles PDF poorly. `figure_5` does not exist because the full multi-encoder consensus analysis was not completed. Never substitute the smoke-test encoder figure.

## 2. Recommended Poster Identity

### Recommended title

**Shared Video-Brain Representations Scaffold Fine-Grained Affective Coding Across Cortex**

### Alternative title with the earlier conceptual framing

**The Brain's Emotion Geometry Is Grounded in What Is Seen and Understood**

Recommended subtitle for the alternative title:

> Independent video and brain foundation models reveal a shared visuocognitive channel and complementary fine-grained affective variance.

### One-sentence conclusion

> Independently pretrained video and brain foundation models share a small set of reliably predictable video dimensions, while continuous fine-grained affective profiles explain additional cortical variance beyond both this shared channel and visual-semantic content.

### Korean conceptual summary

감정 영상에 대한 뇌 표상은 독립적으로 학습된 video/brain foundation model 사이의 공유된 visuocognitive channel을 포함하지만, 그것만으로 완전히 설명되지 않는다. 연속적인 34차원 fine-grained emotion profile은 shared channel뿐 아니라 V-JEPA2와 visual-semantic content를 통제한 뒤에도 추가적인 cortical variance를 설명하며, 이 추가 정보는 arousal-valence 2축보다 풍부하다.

## 3. Research Question

Primary question:

> **How is affective information organized within and beyond the representation shared by independently trained video and brain foundation models?**

Operational questions:

1. Which V-JEPA2 dimensions are reproducibly predictable from corrected Brain-JEPA embeddings on held-out stimuli?
2. Where is a cross-validated video-brain shared representation expressed in cortex?
3. Does a continuous 34-dimensional affective profile explain cortical activity beyond the shared representation?
4. Does the 34D profile add information beyond V-JEPA2 plus visual-semantic content, and beyond arousal-valence?

The shared subspace is a measurement tool, not the biological endpoint. The endpoint is the cortical organization of shared visuocognitive and complementary affective information.

## 4. Data and Representations

- Participants: 5 subjects.
- Stimuli: 2,185 canonical emotional video stimuli.
- Brain target: raw fMRI BOLD in the first 400 cortical Schaefer parcels.
- Video foundation model: pretrained V-JEPA2, 1,408-dimensional stimulus embeddings.
- Brain foundation model: corrected frozen Brain-JEPA, shape `(5, 2185, 768)`.
- Fine-grained affect: continuous 34-dimensional Cowen-Keltner profile from `categcontinuous.mat`.
- Low-dimensional affect: arousal and valence from `dimension.mat`.
- Content controls: visual features from `vision.mat` and 73D semantic features from `semantic.mat`.
- Functional systems: Yeo 7 networks.

The 34 values are continuous profiles. They are not hard labels, discovered neural categories, or 34 cortical modules.

## 5. Corrected Brain-JEPA Policy

Brain-JEPA was pretrained with a longer temporal grid. For the short-window data, the model has one temporal patch. The checkpoint's `emb_h` is fixed sinusoidal code rather than learned information, so the mismatched 10-patch `emb_h` was omitted at load time. The one-patch model's native sinusoidal code was retained. Learned compatible weights, including the spatial gradient-positioning projection, were loaded.

The resulting embedding is described as:

> **A corrected frozen Brain-JEPA spatial representation of short-window evoked responses.**

Do not claim that this analysis uses or validates long-range temporal dynamics. Mean padding ratio was approximately 0.627. Full provenance and SHA-256 hashes are in `source_tables/brain_jepa_native_1patch.json`.

## 6. Analysis A: Confirmed Shared Video-Brain Dimensions

Input:

- Group-mean corrected Brain-JEPA embedding: `(2185, 768)`.
- V-JEPA2 embedding reduced to 100 PCA components using all 2,185 stimuli.

Procedure:

1. Predict each V-JEPA2 PC from corrected Brain-JEPA with standardized ridge regression.
2. Evaluate held-out raw R-squared, Pearson correlation, and Spearman correlation using 5-fold stimulus CV.
3. Repeat with sequential and shuffled fold assignments.
4. Run 1,000 stimulus-label permutations on the top 20 observed PCs.
5. Apply Benjamini-Hochberg FDR across all 100 PCs.
6. Call a component shared only if held-out raw R-squared is positive and FDR q is below .05. Clipped-null and raw-null results must agree for positive components.

Confirmed shuffled-fold results:

| V-JEPA2 PC | Raw R-squared | Pearson r | Spearman r | Raw-null q | Clipped-null q |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.2938 | 0.5851 | 0.5974 | 0.0059 | 0.0250 |
| 2 | 0.1074 | 0.4336 | 0.4273 | 0.0059 | 0.0250 |
| 3 | 0.2139 | 0.5321 | 0.5469 | 0.0059 | 0.0250 |
| 4 | 0.0336 | 0.3694 | 0.3744 | 0.0059 | 0.0250 |

Sequential folds produced the same four positive, FDR-significant PCs. PCs 1-4 jointly account for 31.27% of V-JEPA2 variance. Several later PCs were statistically above the raw permutation null despite negative raw R-squared; these are not counted as predictive shared dimensions and their clipped-null q values were 1.

Interpretation:

> Cross-domain predictability is concentrated in the first four V-JEPA2 dimensions and is robust to fold construction.

Avoid calling four the intrinsic neural dimensionality. PCA was fitted before CV and rank was operationally selected from positive predictive performance rather than nested rank selection.

## 7. Analysis B: Content-Controlled Fine-Grained Affect

This analysis predicts raw cortical BOLD and is independent of Brain-JEPA for its encoding maps. The script loads a brain embedding only to save a separate descriptive CKA table; the nested BOLD models used in Figure 3 and Figure 3b contain no Brain-JEPA features. Therefore these panels are not affected by the earlier Brain-JEPA positional-code issue.

Procedure:

1. Fit kernel ridge encoding models using 5-fold shuffled stimulus CV.
2. Select ridge alpha inside each training fold.
3. Compare nested feature sets on identical held-out stimuli:
   - pretrained V-JEPA2 video features;
   - visual plus semantic content;
   - video plus content;
   - video plus content plus arousal-valence;
   - video plus content plus emotion profiles of rank 2, 3, 5, 10, 20, or 34.
4. Compute raw, unclipped parcel-wise R-squared and nested delta R-squared.
5. Use subjects, not parcels, as the inferential unit.
6. Apply FDR across the predefined map family separately for cortical mean, hierarchy contrast, and cortical-gradient association.

Primary results:

| Contrast | Mean held-out R-squared or delta | Cortical q | Transmodal minus visual | Hierarchy q |
|---|---:|---:|---:|---:|
| Video + visual-semantic content | 0.0590 | 0.0035 | -0.0207 | 0.1150 |
| Unique 34D beyond video + content | 0.001263 | 0.0048 | 0.000751 | 0.0310 |
| 34D advantage over arousal-valence | 0.000714 | 0.0053 | 0.000576 | 0.0310 |
| 34D advantage over matched emotion PCA-2D | 0.000898 | 0.0050 | 0.000584 | 0.0395 |
| Matched emotion PCA-2D versus arousal-valence | -0.000184 | 0.0559 | -0.000008 | 0.8779 |

Interpretation:

> Fine-grained affect contributes a small but consistent increment in held-out cortical prediction beyond extensive stimulus-computable video, visual, and semantic information. The 34D advantage is not reproduced by merely changing from arousal-valence to another two-dimensional affect basis, supporting representational resolution rather than coordinate choice.

This is the strongest evidence for relative transmodal enrichment in the current poster.

## 8. Analysis C: Corrected Shared-Channel Cortical Mapping

Procedure:

1. Hold out one subject from shared-axis discovery.
2. Within each of five stimulus folds, fit video PCA, brain PCA, and whitened cross-covariance SVD using training stimuli only.
3. Discover brain axes using the average corrected Brain-JEPA embedding of the other four subjects.
4. Use the first four video-side shared scores to predict the held-out subject's 400-parcel BOLD response with nested ridge regression.
5. Compare `shared`, `shared + 34D`, and `shared + arousal-valence` on identical held-out stimuli.

Primary corrected results:

| Map | Cortical mean | 95% CI | Subject-level p |
|---|---:|---:|---:|
| Shared-channel R-squared | 0.04817 | [0.03833, 0.05800] | 0.00017 |
| Unique 34D beyond shared | 0.01274 | [0.00599, 0.01950] | 0.00634 |
| 34D advantage over arousal-valence | 0.00693 | [0.00294, 0.01091] | 0.00847 |

Network/hierarchy results:

- Shared information was widespread and strongest on average in dorsal-attention parcels.
- The planned shared `visual - transmodal` contrast was unsupported: p = .894, BH q = .894.
- Unique 34D showed a positive `transmodal - visual` trend: p = .0513, BH q = .101.
- The 34D-over-arousal-valence hierarchy contrast also trended positive: p = .0758, BH q = .101.
- The maps were generated with shared rank 4 and `n_shuffles=0` because of the server deadline. Therefore the cortical rank diagnostic has no permutation-based p-values.

Interpretation:

> The shared channel is distributed rather than selectively visual. Fine-grained affect adds reliable cortical variance beyond this channel, but a strong shared-to-transmodal double dissociation is not established in the corrected cortical analysis.

## 9. Figure-by-Figure Use

### Figure 1: Framework

Place in the Methods/Overview section. It establishes that V-JEPA2 and Brain-JEPA were independently pretrained, paired only through the experimental stimuli, and connected through held-out cross-domain alignment. The two downstream branches represent shared cortical expression and complementary fine-grained affect.

Suggested caption:

> **Framework.** Independently pretrained video and brain foundation models were aligned using responses to the same emotional videos without emotion-label supervision. Cross-validated shared scores were localized in raw cortical BOLD, and nested encoding models tested fine-grained affective information beyond the shared video-brain channel.

### Figure 2: Corrected Shared Channel

Use as Main Result 1. The left panel is the inferential panel. The middle panel shows held-out correlations, including later components that correlate weakly but have negative raw R-squared. The right panel shows cumulative V-JEPA2 variance.

Suggested heading:

> **Four leading video dimensions are reliably recoverable from corrected Brain-JEPA.**

Suggested caption:

> Corrected frozen Brain-JEPA predicted V-JEPA2 PCs 1-4 with positive held-out raw R-squared under both sequential and shuffled five-fold CV. All four survived 1,000-permutation FDR correction across 100 PCs under both raw and clipped null definitions. Together they captured 31.3% of V-JEPA2 variance.

### Figure 3: Content-Affect Partition

Use as Main Result 2. This is the strongest specificity/control panel. Explain that all effects are increments in held-out raw-BOLD prediction, not decoding accuracy and not category classification.

Suggested heading:

> **Fine-grained affect explains cortical variance beyond video and visual-semantic content.**

Suggested caption:

> Across subjects, the continuous 34D affective profile improved held-out cortical prediction beyond pretrained V-JEPA2 plus visual-semantic features. Its gain exceeded both arousal-valence and a variance-matched two-dimensional emotion representation and was relatively enriched in control/default versus visual cortex.

### Figure 3b: Content-Controlled Brain Maps

Optional if poster space permits. It contains four unthresholded group-mean maps with row-specific color scales. Use it to show that the content-controlled effect is distributed and small in magnitude. Do not compare colors numerically across rows without reading each color bar.

### Figure 4b: Corrected Cortical Brain Maps

Use as the main neuroscience visual. The maps are unthresholded group means across five subjects and have separate symmetric color scales.

Suggested heading:

> **Shared visuocognitive and complementary fine-grained affective signals are distributed across cortex.**

Suggested caption:

> Cross-validated shared video-brain scores predicted widespread cortical activity. Adding the continuous 34D profile improved held-out prediction beyond the shared channel, and improved prediction beyond arousal-valence. Maps show unthresholded group means across five subjects; scales differ across rows.

### Figure 4: Corrected Cortical Networks

Place beside Figure 4b. Bars are subject means with SEM and dots are individual subjects. Use it to prevent overinterpreting the brain renderings.

Suggested caption:

> Shared-channel prediction was broad and strongest in dorsal-attention cortex. Fine-grained affective increments were globally positive, with numerically larger effects in control/default systems, but corrected transmodal-versus-visual contrasts did not survive FDR correction.

## 10. Recommended Poster Layout

Three-column layout:

1. **Left:** question, conceptual motivation, Figure 1, compact Methods.
2. **Center:** Figure 2 and Figure 3, emphasizing confirmed shared dimensions and the content-controlled affect result.
3. **Right:** Figure 4b as the largest visual, Figure 4 below it, then conclusion and limitations.

If space is tight, omit Figure 3b before omitting any main panel. Figure 4b is the primary brain figure. Figure 3 is the strongest control figure.

## 11. Poster-Ready Text

### Background

> Emotional videos jointly contain perceptual, semantic, and affective structure. This makes it difficult to determine whether cortical emotion geometry simply mirrors stimulus-computable content or contains additional fine-grained affective organization. We used independently pretrained video and brain foundation models to estimate a shared representational channel, then tested what cortical information remains beyond that channel.

### Methods

> Pretrained V-JEPA2 embeddings and corrected frozen Brain-JEPA embeddings were obtained for 2,185 videos and fMRI responses from five participants. Held-out ridge encoding and cross-view SVD estimated shared video-brain information without emotion-label supervision. Nested parcel-wise models tested whether a continuous 34D affective profile explained raw BOLD beyond shared scores, arousal-valence, and combined video/visual-semantic features.

### Results

> Corrected Brain-JEPA reliably predicted four leading V-JEPA2 PCs, which jointly captured 31.3% of video-model variance. Shared scores predicted widespread cortical activity. Fine-grained 34D affect improved held-out cortical prediction beyond the shared channel and beyond arousal-valence. The same profile added variance beyond V-JEPA2 plus visual-semantic content, with significant relative enrichment in control/default versus visual cortex in the strict content-control analysis.

### Conclusion

> Cortical responses to emotional videos contain a distributed representation shared with a video foundation model and complementary fine-grained affective information not exhausted by visual-semantic content or arousal-valence. Emotion categories are therefore better treated as continuous high-dimensional profiles of affectively meaningful content than as independent hard labels.

## 12. Claims That Are Supported

- Independently pretrained corrected Brain-JEPA and V-JEPA2 share reproducibly predictable stimulus structure.
- Four leading V-JEPA2 PCs have positive, permutation-confirmed held-out predictability from corrected Brain-JEPA.
- The shared channel predicts widespread held-out cortical BOLD.
- Continuous 34D affect adds cortical variance beyond the shared channel.
- The 34D profile adds variance beyond V-JEPA2 plus visual and semantic features.
- The 34D profile explains more than arousal-valence and more than a matched two-dimensional emotion representation.
- Relative transmodal enrichment is supported in the full video-plus-content control analysis.

## 13. Claims to Avoid

- Do not say that the study discovered 34 neural emotion categories.
- Do not describe the 34D ratings as hard category labels.
- Do not call all Brain-JEPA/V-JEPA2 overlap emotion-specific.
- Do not claim that video-unexplained activity is subjective feeling.
- Do not claim long-range temporal dynamics from one-patch Brain-JEPA.
- Do not claim a rank-3 subspace. The corrected operational result is four positive predictive PCs.
- Do not claim a clean visual-to-transmodal double dissociation. The corrected shared-channel hierarchy tests have q = .101 for affective increments.
- Do not claim replication across brain encoders. Full SwiFT/NeuroSTORM consensus was not completed.
- Do not treat 400 parcels as independent samples. Inferential tests use five subjects.
- Do not describe unthresholded brain maps as clusters of statistically significant activation.

## 14. Limitations and Outstanding Analyses

1. Only five subjects were available, so subject-level uncertainty is substantial.
2. Shared alignment uses a group-mean Brain-JEPA representation and PCA fitted before CV. A fully nested rank-selection analysis remains desirable.
3. Corrected cortical mapping used rank 4 but `n_shuffles=0`; shared-rank null inference was omitted under the server deadline.
4. Brain-JEPA encodes short-window responses with substantial padding and should be interpreted primarily as spatially organized.
5. The full pretrained-versus-scratch consensus across Brain-JEPA, SwiFT, and NeuroSTORM is missing.
6. Brain maps are unthresholded descriptive group means. Spatially informed nulls are needed for parcel-level localization claims.
7. The content-controlled affect increments are small in absolute R-squared but consistent across subjects and significant under the predefined FDR family.

## 15. Exact Reproduction Commands

Project root used on Perlmutter:

```bash
ROOT=/pscratch/sd/s/sjmoon/EmoBrain/archive/v5_direction_split_20260628/dir3_ccn
PYTHON=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python
```

Prepare the corrected five-subject Brain-JEPA stack from validated external embeddings:

```bash
$PYTHON -u $ROOT/study1/code/corrected_reanalysis/prepare_corrected_brain_embeddings.py
```

Confirmed shared alignment used for Figure 2:

```bash
OMP_NUM_THREADS=32 MKL_NUM_THREADS=32 OPENBLAS_NUM_THREADS=32 \
$PYTHON -u $ROOT/study1/code/shared_alignment/run_shared_alignment.py \
  --model vjepa2_pretrained \
  --brain-path $ROOT/study1/data/corrected_reanalysis/brain_jepa_native_1patch.npy \
  --output-dir $ROOT/study1/data/corrected_reanalysis/shared_alignment_confirm \
  --n-perm 1000 \
  --n-pc 100 \
  --n-test-pcs 20
```

Content-controlled raw-BOLD analysis used for Figure 3 and Figure 3b:

```bash
$PYTHON -u $ROOT/study1/code/content_affect_partition/run_content_affect_partition.py \
  --brain-path $ROOT/study1/data/corrected_reanalysis/brain_jepa_native_1patch.npy \
  --output-dir $ROOT/study1/results/content_affect_partition
```

Corrected cortical analysis used for Figure 4 and Figure 4b:

```bash
OMP_NUM_THREADS=32 MKL_NUM_THREADS=32 OPENBLAS_NUM_THREADS=32 \
$PYTHON -u $ROOT/study1/code/cortical_transformation/run_cortical_transformation.py \
  --brain-path $ROOT/study1/data/corrected_reanalysis/brain_jepa_native_1patch.npy \
  --output-dir $ROOT/study1/results/corrected_reanalysis/cortical_transformation \
  --shared-rank 4 \
  --n-pca 100 \
  --max-rank 20 \
  --n-folds 5 \
  --n-shuffles 0
```

For a post-poster full cortical rerun, change `--n-shuffles 0` to at least `--n-shuffles 100` and run on a compute node.

Regenerate poster figures:

```bash
$PYTHON -u $ROOT/study1/code/poster_figures/export_poster_figures.py \
  --output-dir $ROOT/study1/results/poster_export/CCN_POSTER_HANDOFF
```

## 16. Included Source Material

`source_tables/` contains:

- full shared-alignment NPZ with observed metrics, p/q values, and null distributions;
- corrected Brain-JEPA provenance and hashes;
- content-affect group, network, and parcel tables plus run config;
- corrected cortical group, network, parcel, rank-diagnostic tables plus run config;
- a human-readable CSV export of shared PC metrics.

`reproduction_code/` contains the exact Python modules used for:

- corrected Brain-JEPA stacking;
- shared alignment and permutation testing;
- content/affect variance partitioning;
- corrected cortical transformation;
- poster figure export.

## 17. Final Scientific Readout

The results do not support a simple story in which a purely visual shared channel is cleanly transformed into emotion only in transmodal cortex. They support a more defensible account:

> **A distributed visuocognitive representation is shared between independently trained video and brain foundation models. Fine-grained affective profiles add complementary cortical information beyond that shared representation and beyond extensive visual-semantic controls, and this content-controlled increment is relatively enriched in transmodal systems.**

This is the poster's scientific contribution. The foundation-model subspace identifies the shared information channel; nested raw-BOLD encoding establishes the complementary affective signal; brain maps show where both are expressed.
