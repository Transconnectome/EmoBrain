# Referee report: EmoBrain methods spec v1 (2026-11-25)

## Verdict

The spec is detailed and well sourced. Several choices are sound: the lens is frozen before any Cowen data is seen, D_R never sees ratings, MC is run once after a commit-hash freeze, MC-72 is excluded everywhere, and HK is honestly labelled exploratory. But it is not ready to run.

- **Three problems are fatal.** (F1) Two incompatible Cowen splits leak rating information into the HK test folds. (F2) The L/O/S level decomposition repeats, with more collinear features, the analysis that already failed in this project. (F3) In 2막 one comparison is structurally rigged, and the arms are not matched on anything except head and loss.
- **Seventeen problems are major.** They cover statistics with 5 subjects, ratio metrics, controls for the brain route, Haufe/top-weight inference, MC and Emo-FilM confounds, data-product inconsistencies, and gaps against H1–H4 in `docs/paper_logic_merged.md`.

Tags: (V) = I verified this in this pass; (est) = my own arithmetic or inference.

---

## FATAL

### F1. Two partitions of the same Cowen stimuli let rating-trained components see HK test stimuli

**Where:** §1.2, §1.3, §2b (g_Scap), §3.3 (R-S-cap path and ρ_rec ceiling), §4.2 G2/G3 (W_word, W_obj), §3.4 4d (PLS), §6.2 ("두 분할을 하나로 통일할지 여부" left open).

**Problem**
- Every Cowen-rating-fitted component is trained on the 1748 train set of the 1748/217/220 split (minus MC-72). These are g_Scap, W_word, the 4d PLS, the S-cap layer choice and the lexicon-floor tuning.
- Brain results are evaluated on hk_dev_v4 test folds, which partition the same stimuli differently.
- If the two partitions are independent, about 1748/2185 ≈ 80% of each HK test fold sits inside the readout's training set (est).
- So R-S-cap, the G3 word route and the S-cap ceiling are in-sample for ratings. These are the exact routes the transmodal/situation story depends on.

**Evidence**
- hk_dev_v4 assigns one fold per video_id, shared across subjects (V: `/home/user/AffectLab/src/crossmodal_emotion/fold_plan.py` L31-48, `split = {video_id: row}` with a 'fold' field). Nesting is therefore possible.
- The spec says the 220 test set "이번 분해 질문으로는 열린 적이 없다". That is not defensible:
  - stimulus→emotion test numbers already exist (CLIP bigG 0.505, V-JEPA 2 0.425);
  - the per-emotion sensory:semantic composition question was already run and failed (V: `/home/user/EmoBrain/CONTEXT_EMOBRAIN.md` L39; `/home/user/EmoBrain/docs/notes/project_decisions.md` L30).

**Fix**
1. Use one partition for everything Cowen-side: hk_dev_v4, MC-72 excluded, 6 folds.
2. Refit every component that touches Cowen ratings inside each outer rotation: 4 train folds, select on its val fold. This covers g_Scap, W_word, the G1 transfer check, 4d PLS, S-cap layer, lexicon floor and the affine-correction choice.
3. Report Cowen-side Act 1 results as 6-fold out-of-fold (OOF) over all ~2.1k non-MC stimuli. That gives about 10× the test N. Label it exploratory.
4. Make VCE-test the confirmatory stimulus-side set.
5. Keep 1748/217/220 only for the R0 continuity check.
6. Add a unit test asserting that no test-fold stimulus ID appears in any training set of any rating-fitted object. Reuse the MC-protected-ID assertion pattern in fold_plan.py L39-40.

### F2. The L/O/S decomposition is not identifiable as specified

**Where:** §3.1 steps 3–5 (Fig 1C/1D); §3.2 step 4 ("voxel별 우세 band", Fig 2C); §3.2 step 5.

**Problem**
- This is the analysis that already died here: 0/34 Bonferroni, split-half reliability −0.95 to −1.00 (CONTEXT L39).
- A reliability near −1 is the signature of collinear bands. Shared variance goes to band A in one half and to band B in the other.
- v1 makes the collinearity worse:
  - O-obj (EVA02-L), O-act (VideoMAE V2-B) and S-vis (PE-Core G) are all large ViTs run on the same frames.
  - "Object / situation" is a name taken from each model's training objective, not a measured information level. CLIP-type embeddings carry object identity; in22k logits carry scene.
- Banded-ridge random-search deltas and the product-measure split R² assign shared variance through fitted weights. The split R² can also go negative (R3 §4). Both are unstable under collinearity.
- Per-emotion estimates on about 200 Cowen test stimuli with 73.8% zeros add noise.
- A per-voxel "dominant band" is an argmax over noisy, collinear estimates.

**Fix:** a prespecified gate, run before any interpretation. It can start now on CPU with existing features.
- (a) **Collinearity report.** Cross-prediction R² between bands, CCA/CKA spectra, and effective rank, on Cowen and on VCE.
- (b) **Parameter recovery.** Build synthetic targets as known mixtures (pure L, pure O, pure S, 50/50 pairs) from the real feature matrices, with noise set to the observed R². Run the exact pipeline at Cowen per-fold N and at VCE N, and report the recovery confusion matrix. If dominant-band recovery falls below a prespecified level, declare per-emotion or per-voxel attribution non-identifiable at that N and do not report it.
- (c) **Split-half reliability gate.** Split stimuli in halves (and subjects, for brain). Require the reliability CI for each band's share to exclude 0 before any per-emotion or per-ROI claim.
- (d) **Grain.** Per-emotion decomposition only on VCE (~11k test). Cowen and brain only at pooled grain: profile/RDM level, 22 groups or PG1 deciles, never voxels.
- (e) **Primary analysis = hierarchical sequential ΔR², order L → O → S fixed in advance.** It answers "what S adds beyond L and O". The 7-way commonality analysis is descriptive only. Drop "dominant band per voxel" as an inferential map.
- (f) **Dimensionality sensitivity.** Equalize band dimensions (PCA to k chosen in train). The sizes 2530, 1024/21841 and 1280 change the ridge prior.
- (g) **Validate the level labels (convergent/discriminant).**
  - L must predict low-level image statistics better than S does.
  - S-vis must predict S-cap (the human-caption embedding) beyond O.
  - O must predict object annotations beyond L.

  Without this, "situation level" is a label, not a measurement.

### F3. The 2막 objective contrast is confounded, and step 5 is structurally rigged

**Where:** §2c, §3.2.

**Problems**
- **(a) Built-in zero.** The N-act teacher is VideoMAE V2-B K710-distilled, which is also the O-act band extractor (§2b). N-act fc_norm is trained to reproduce that teacher. In step 5 ({L,O,S} + {N-act fc_norm}), N-act's unique R² over the bands is therefore about 0 by construction, while E's is not. N-obj vs O-obj (both EVA02) has the same flaw.
- **(b) Targets differ in many ways besides "emotion or not":**
  - dimensionality: 27 vs 710 vs 21841;
  - entropy;
  - loss: BCE vs soft CE;
  - noise: crowd means vs a deterministic teacher;
  - head size: about 20.7k vs 0.55M vs 16.8M parameters (est).

  So the amount of representational change differs between arms.
- **(c) Layer decay concentrates change at the top.** With layer_decay 0.75 over 12 blocks, the first block gets about 0.75^12 ≈ 3% of the head learning rate (est). Any fine-tune changes mostly the late blocks, and late blocks best predict higher-order cortex. So E vs base and E vs E-perm will show "transmodal" Δ whatever the objective.
- **(d) E-perm degenerates.** E-perm is selected by its own val-loss minimum. Permuted targets can only be memorized and val loss rises, so the chosen epoch will be early and E-perm ≈ base. It does not control for "27-d multilabel training". The spec also does not say whether val labels are permuted for E-perm.
- **(e) Selection rules differ.** The main lens ("E seed 0") is selected by mean val r (§2a); the arms are selected by val loss (§2c). The main lens is therefore not the E-arm checkpoint.
- **(f) Learning rate depends on GPU count.** lr = 5e-4 × total_batch/256 (§2a). Runs on different GPU counts get a different effective lr and batch.
- **(g) Seeds.** With 3 seeds the SD has df = 2. Its 95% CI is about 0.52s to 6.3s (est).

**Fix**
- **Primary contrast: E vs a new N-27 arm.**
  - Target: the top 27 PCs of the K710 teacher logits on lens-train videos.
  - Mix them with the Cholesky factor of the emotion-label correlation matrix.
  - Quantile-map each dimension to the marginal of the corresponding E label.
  - Same BCE loss and same 768→27 head.

  This matches dimensionality, loss, head, marginals, correlation structure and diet; only the content differs. N-act and N-obj become secondary.
- **Step 5:** compute unique R² over L+S only, or use teachers that are not in the band set.
- **Training budget:** fixed for all arms (final checkpoint at epoch 50) with the same total batch enforced via `update_freq`. No per-arm early stopping. The main lens is a separately r-selected checkpoint of E seed 0, and the spec should say so.
- **Change magnitude:** report linear CKA to base per block on Cowen videos, and test Δ_R beyond change magnitude.
- **Soft targets:** state the distillation temperature, and whether frame averaging comes before or after softmax.
- **Seeds:** set the seed count from the K-seed pilot's power. Aim for ≥5 per arm on the primary contrast, or downgrade the claim.

---

## MAJOR

### M1. No confirmatory test of the 3막 region × level claims

**Problem**
- All HK results are exploratory (§1.3).
- The confirmatory MC test (§4.5) uses ROI-mean-450 decoders. 3막's findings come from per-subject voxel FastL2LiR on HCP-MMP ROIs (§2e). The model tested on MC is not the model that produced the claims.
- MC-72 are new people, not new stimuli.

**Fix**
- Build 3막 also at the ROI-mean level, with the same 42 units defined in MNI. Freeze it on HK.
- Pre-register directional predictions, for example the sign of the ρ difference between the top and bottom PG1 deciles, or the rank order over the 22 groups.
- Test them once on MC-72 perception.
- Add leave-one-subject-out (LOSO) within HK (train on 4 subjects' ROI-means, test on the held-out subject's held-out stimuli). This gives a "new people" test that does not consume MC, and calibrates the expected transfer loss.

### M2. Inference with 5 subjects

**Problem**
- An exact sign-flip test over 5 subjects has 2^5 = 32 permutations. The minimum p is .031 one-sided and .0625 two-sided (est). No subject-level test can survive q = .05 FDR.
- A size-5 bootstrap from 5 subjects has only 126 distinct resamples (est). σ²_subj is unstable, so the Schütt correction will often clip.
- This project already has a red-team verdict to the same effect: "N=5 d.f.=4 underpowered … dominance 주장 통계적 불가" (V: `/home/user/EmoBrain/docs/notes/project_decisions.md` L701).

**Fix**
- Run inference within each subject, at stimulus level (about 2.1k stimuli).
- Treat each subject as a replication. Report k/5 and Bayesian population prevalence (Ince et al. 2021, "Bayesian inference of population prevalence", eLife, [DOI](https://doi.org/10.7554/eLife.62461), PubMed).
- Use the dual bootstrap for descriptive CIs only.
- Make population-mean claims only on Emo-FilM (n = 30).
- For MC, prespecify 6/6: the binomial p is .016 for 6/6 and .109 for 5/6 (est).

### M3. Permutation resolution is too coarse for the FDR families

**Problem**
- 1000 permutations give a p floor of about .001.
- Under BH, tests sitting at the floor are rejected only if at least 2% of the family is there (est):
  - ≥23 of 1134 tests (42 ROIs × 27 emotions);
  - ≥137 of 6804 tests (42 × 6 levels × 27).
- Sparse true effects therefore become unrejectable by construction.

**Fix**
- Use ≥10^4 permutations, or a generalized Pareto tail approximation (Winkler et al. 2016, "Faster permutation inference in brain imaging", NeuroImage, [DOI](https://doi.org/10.1016/j.neuroimage.2016.05.068), PubMed).
- Test hierarchically: an omnibus test per ROI on profile r, then emotions only within significant ROIs.
- Fix the family for each figure in advance.

### M4. The TOST equivalence margin is estimated from the data it judges

**Problem**
- §3.0 sets SESOI = seed SD; §3.2 uses this margin for the "동등" colour in Fig 2B.
- With 3 seeds the margin is uncertain by a factor of about 12 (est).
- Noisier seeds give a wider margin, which makes equivalence easier to declare.
- Lakens 2017 requires a prespecified smallest effect size of interest.

**Fix**
- Prespecify an absolute Δr margin per ROI before training, for example a fixed fraction of the ROI's LOSO ceiling proxy.
- Use seed variance only for power.

### M5. ρ_med and ρ_rec are ratio statistics with unstable denominators

**Problem**
- In transmodal ROIs, Direct r is near the floor. HK's region significance threshold is r > 0.095 (H20 L25).
- A ratio of two noisy correlations is heavy-tailed, so bootstrap CIs are invalid.
- ρ_med > 1 is expected wherever feature routes denoise.
- H4 is stated as a difference: route vs label-only decoder (paper_logic L100-102).

**Fix**
- Primary: Δr = r(R-ℓ) − r(Direct), with a paired stimulus bootstrap within subject.
- Secondary: report ratios only where Direct's lower CI exceeds a prespecified floor, using Fieller intervals.
- Add the partial correlation r(y, Direct | R-ℓ) as "emotion not routed through ℓ".

### M6. The brain route measures decodability, not emotion-specific organization

**Problem**
- Emotion r of R-ℓ is roughly (decodability of ℓ in R) × (stimulus-side ceiling).
- It exceeds that only if the region preferentially keeps the emotion-relevant feature dimensions.
- Fig 3D shows decodability, but nothing predicts emotion r from decodability.
- paper_logic §B (L182-188) requires a control that subtracts gains unrelated to the brain. This is its analogue.

**Fix:** a noise-matched simulation null per (subject, R, ℓ).
- Generate pseudo-decoded features: true test features → synthetic voxels (random mixing plus noise at the region's SNR) → the same FastL2LiR.
- Match per-unit decodability and the shrinkage spectrum to the region's real decoding.
- Pass the result through g_ℓ or the head and compute the expected emotion r.
- Claim = observed − expected, i.e. the emotion selectivity of the region's decodable subspace.
- Apply the same null to G3.

### M7. The decoder choice contradicts its own justification

**Problem**
- §2e reason 2 says a linear decoder preserves feature geometry, so a frozen head can read the decoded features. But FastL2LiR:
  - picks a different 500-voxel set for each output unit (FL L256-295);
  - uses one global alpha chosen by mean profile r.
- Decoded 768/1024/2530-d vectors are shrunk and have the wrong covariance for the head. A per-unit affine correction cannot restore covariance between units.
- Reason 3 (31 min per fold) is not a methodological argument.

**Fix**
- **Primary R-lens:** decode the lens's 27-d outputs directly from brain. Likewise decode g_ℓ(x) 27-d outputs directly.
  - This is still blind to human ratings.
  - It is Kragel 2019's own design: EmoNet outputs decoded by PLS from 7,214 occipital voxels.
  - Route and Direct then have identical output dimensionality and selection budget.
- **Secondary:** fc_norm → head, i.e. Horikawa-style generic decoding.
- **Sensitivity:** ridge without voxel selection (shared voxel set, per-target alpha via himalaya).
- **§3.3 step 3:** the affine-correction choice must use feature-reconstruction profile r, not emotion ratings.

### M8. Haufe and double-dipping problems in the top-weight figures

**Problems**
- **(a) G2's word attribution is unstable.** Cov(ŷ_e, y_e) = Σ_j w_je Cov(x_j, y_e) is an identity, but each term multiplies a backward weight by a covariance. Co-occurring words (smiling / laughing / happy) produce suppressor sign flips, so per-word "affect share" is unstable. This is Haufe 2014's argument applied to w.
- **(b) G3 is double dipping.** The top 5 words per cell are chosen on test stimuli, then CIs are shown on the same test. This is the circularity in Kriegeskorte et al. 2009, "Circular analysis in systems neuroscience: the dangers of double dipping", Nat Neurosci ([DOI](https://doi.org/10.1038/nn.2303), PubMed).
- **(c) §4.1 Fig B uses raw PLS-DA β.** With 27 correlated emotions (fear / horror / anxiety), β signs can be suppressor artifacts. Kragel's horror β included aesthetic appreciation.
- **(d) 21841 in22k logits.** With z-scored X, the pattern is proportional to corr(x_j, ŷ_e) and will be dominated by clusters of near-synonyms.

**Fix**
- Rank by held-out patterns, averaged over folds. Show univariate corr(x_j, y_e) beside them, to separate the data relation from the model relation.
- Report contributions at group level (lexicon, hypernym) with split-half reliability.
- Headline the refit ladder ΔR² rather than the identity.
- In G3, select words on train/val or on one half of the stimuli, and display them on the other half.
- In the genre figure, make patterns primary and β secondary.
- Fix the hypernym grouping and frequency floor (D6.13) before running.

### M9. The ablation ladder (S-cap-noaff, G2 L1) confounds "affect removed" with "tokens removed"

**Problem**
- Deleting any tokens degrades DeBERTa inputs.
- Videos whose captions carry many affect words are also the most affect-laden videos.

**Fix**
- Add a matched random-deletion control: delete the same number of non-lexicon tokens per caption, matched on part of speech (POS) and frequency.
- Affect-specific share = (full − noaff) − (full − random deletion).
- Report the fraction of tokens removed per video.

### M10. "Irreducible emotion" inferences fall into the Westfall–Yarkoni trap

**Where:** §3.1 "unique 잔차 → 환원되지 않는 정서 고유 구조"; §3.3 "ρ_med 낮고 Direct 높다".

**Problem**
- The feature sets are incomplete measures of content. noaff deliberately removes some content.
- The residual therefore contains unmeasured content plus rating noise (Westfall & Yarkoni 2016).

**Fix**
- Express the residual against a rating-reliability ceiling: split raters if rater-level data exist; otherwise say the upper bound is unknown.
- Show a saturation curve: the residual as more and bigger content models are added.
- Claim irreducibility only if the residual plateaus clearly above 0 and is reliable across halves.
- Wording: "not captured by these content measures".

### M11. Near-duplicates inside VCE, and a positional lens-val split

**Problem**
- lens-val = the last 10% of train_labels.json, by position (§1.1). The order of that file is unchecked.
- VCE comes from Reddit and Instagram (INDIRECT), so reposts are likely. They would inflate lens selection, the "confirmatory" VCE-test, and V2V listwise results.
- §1.6 dedups only Cowen and trailers against VCE.

**Fix**
- Run the same pHash + embedding pipeline within VCE: train vs val vs test vs V2V test/listwise.
- Cluster near-duplicates and keep each cluster inside one split.
- If the JSON order is not random, use a seeded random 10% for lens-val.

### M12. The lens and the O-act band share a model family

**Problem**
- The lens is VideoMAE-B on K400; O-act is VideoMAE V2-B on K710.
- In T2 (what the lens learned) and in R-lens vs R-O-act, O-act will absorb lens variance through shared inductive bias, not through an "action level".

**Fix**
- Make lens B (V-JEPA 2.1) co-primary for the T2 decomposition.
- Require conclusions to hold for both lenses.
- Report CKA between the lens and each band.

### M13. MC: data provenance, scale, subject identity, and the cue

**(a) Three HK data products are mixed.**
- §4.5 says the HK ROI-mean decoder comes from AffectLab `*_blocks_common36_qc_runz.npy` and therefore matches MC preprocessing. That file is voxel-level: AffectLab computes 370 anatomical-ROI means from it (V: `/home/user/AffectLab/docs/FIRST_PILOTS.md` L66).
- §1.3's ROI-mean is EmoBrain's Schaefer400 + Tian50, built from per-stimulus CSVs with undocumented normalization (V: `/home/user/EmoBrain/project/scripts/build_roi_timeseries.py` L5, L58-59).
- The voxel analyses use the Kamitani h5 (fMRIPrep, native space), while hk_dev_v4 indexes AffectLab qc_rows.
- **Fix:** compute Schaefer/Tian means from the runz voxel file with MC's exact pipeline (4 s shift, despike, block average, run-z). Write and unit-test the crosswalk between h5 run/sample and qc_row.

**(b) Per-ROI scale is not shared across people.**
- The variance of a run-z ROI-mean depends on how coherent the voxels inside the ROI are, which varies by subject.
- Z-scoring MC's ROI means would be normalization with MC responses, which the rules forbid.
- **Fix:** measure the effect with HK LOSO under the identical no-renormalization rule. Escalate to the PI before the single MC run.

**(c) "New people" is unverified.**
- Both cohorts are Kamitani-lab Japanese subjects.
- I found no statement in MC's main text that its subjects differ from HK's.
- **Fix:** verify subject identity first.

**(d) The cue contaminates imagery.**
- The preparation cue is a fixed caption that contains affect words.
- BOLD from reading it lands at the start of the 4-s-shifted imagery window.
- Partialling out a G2-predicted profile is a weak proxy, so it under-corrects.
- **Fix:**
  - Decode the preparation period with the same frozen decoder as an empirical cue control. MC reports preparation-period decoding near chance except for S2.
  - Add time-resolved (per-TR) decoding.
  - Prespecify an imagery window that starts ≥6 s after cue offset.

**(e) Run-z on test runs is transductive.**
- It is label-free but uses the test data themselves.
- Record it as a pre-registered PI exception.

### M14. Emo-FilM is watched with sound; the HK decoder was trained on silent viewing

**Problem**
- Auditory and language ROI inputs are out of distribution for the decoder and project arbitrarily onto the 27 outputs.
- Preprocessing also differs: FSL FEAT with 6 mm smoothing in MNI space.

**Fix**
- Primary: a decoder restricted to non-auditory ROIs, with the excluded list fixed a priori. The full decoder is secondary.
- Add the audio envelope as a nuisance regressor in the brain-vs-annotation comparison.
- Compare per emotion over time. Cross-emotion profile comparisons share the head's bias.
- Population inference is legitimate here: per-subject Fisher z across 30 subjects.

### M15. §4.3 in silico screening

**Problems**
- **(a) Selection on test.** ROI inclusion uses "test r > null & FDR" (Kriegeskorte 2009). Use val folds.
- **(b) The random-direction null is biased low.** Ridge solutions concentrate on high-variance PCs, and those carry most of the emotion variance. Random isotropic directions under-correlate with emotion, which inflates region effects.
  - Null directions should come from ridge fits with the same spectrum: other subjects' or other ROIs' responses, or phase-randomized responses.
- **(c) Extrapolation.** Restrict to VCE videos inside the Cowen feature support, e.g. PCA-Mahalanobis distance below Cowen's 99th percentile.

### M16. Coverage gaps against the authoritative hypotheses

Checked against `docs/paper_logic_merged.md` L72-104 and L175-191 and against CLAUDE.md.

**Gaps**
- **H1** requires parity between content bands and an emotion-rating band in brain encoding. 2막 has no rating band.
- **H2** (emotion-similar, content-different pairs; D9, ranked #1 among demos) is absent.
- **H3**'s specific prediction is not tested explicitly: vision-only models fail in transmodal cortex, while vision + language models partly succeed. The O vs S-vis ingredients are there.
- The **unexplained-variance map** that paper_logic §3 requires exists only for Emo-FilM, not for HK.
- **H4** is operationalized by 3막 route-vs-Direct, but two required pieces are missing:
  - the mismatched-brain control on the size of the improvement (M6 supplies it);
  - the ROI-removal convergence test against H3 regions.
- The CLAUDE.md model (a label-query decoder over a brain + video + caption memory, 34 queries) does not appear at all. The spec uses 27 dimensions and FastL2LiR.

**Fix**
- Add a table mapping each analysis to H1–H4.
- Add a fold-internal Cowen-27 rating band to the HK banded encoding, with TOST parity.
- Add the H2 pair test.
- Add the HK unexplained-variance map.
- Add the ROI-removal test.
- Flag to the PI: either update CLAUDE.md and paper_logic (model section, 34 → 27), or keep the joint model as the H4 vehicle.

### M17. Label constructs differ, and zeros dominate per-emotion r

**Problem**
- VCE labels are mean intensity (select-then-rate). Cowen labels are the proportion of raters choosing the category, with 73.8% zeros.
- log1p on [0,1] is nearly the identity (est), so log1p_z is effectively a z-scored proportion.
- Pearson r per emotion is driven by the few non-zero stimuli.
- Cross-emotion rankings (Fig 1A, 1D) are confounded with per-emotion reliability.

**Fix**
- Report the count of non-zero stimuli per emotion per fold, and set a minimum count for per-emotion inference.
- Add Spearman r as a robustness check.
- Normalize by a reliability ceiling if rater-level data exist. Otherwise do not rank emotions against each other.

---

## MINOR

- **m1. Pooled OOF predictions.** Fold-specific scaling and alpha make concatenated predictions misleading. Compute r within each fold and average with Fisher z, or standardize within fold. Prespecify which.
- **m2. K-enc uses test r.** Use val folds.
- **m3. The K-dec gate compares different models.**
  - R0 = 0.294 is a single ridge on subject-pooled ROI-mean data, 34-d, with 8740 / 1085 / 1100 pooled samples (EmoBrain datasets.py).
  - The spec's Direct decoder is per-subject voxel FastL2LiR, 27-d.
  - Reproduce R0 with the original code as a data-integrity check, and gate K-dec on EVC L decodability only.
- **m4. S-cap layer criterion is unspecified.** If the layer is chosen by Cowen emotion val, it injects emotion selection into the brain bands. Average over layers, or choose by brain val.
- **m5. corr_R(Δ, S ratio) is computed over 42 overlapping, spatially autocorrelated ROIs.** Use a spin-test null: Alexander-Bloch et al. 2018, "On testing for spatial correspondence between maps of human brain structure and function", NeuroImage ([DOI](https://doi.org/10.1016/j.neuroimage.2018.05.070), PubMed). Or present it descriptively.
- **m6. Fig 1D compares unlike bands.** Cowen uses S-cap while VCE uses S-vis. Use S-vis on both sides for that panel.
- **m7. "Label-blind" overstates.** fc_norm is optimized for VCE emotion. Say "never sees Cowen/HK/MC ratings".
- **m8. MC 72×72 RSA.** Use cross-validated distances across the 5 repetitions: Walther et al. 2016, "Reliability of dissimilarity measures for multi-voxel pattern analysis", NeuroImage ([DOI](https://doi.org/10.1016/j.neuroimage.2015.12.012), PubMed).
- **m9. Δ_R notation.** "mean_subj(r_E,R) − r_N,R" averages one side only. Define it as the mean of paired (subject, seed) differences.
- **m10. lens-val is reused for six selections** (epoch, inference mode a/b, logit z-stats, g alphas, V-JEPA head, arm checkpoints). Acceptable because VCE-test is untouched, but list them, and report nothing on lens-val.
- **m11. Trailers.**
  - With n = 28, bootstrapped β is unstable; treat the replication arm as illustrative.
  - YouTube download terms and link rot need reporting.
  - Detect text overlays by OCR, not by hand.
  - AUC is a construct check only.
- **m12. V2V.** Only pairs with ≥8/9 agreement were kept, so the BT weights reflect extreme pairs. State this.
- **m13. Emo-FilM ceiling.** Leave-one-rater-out with 3–4 raters is noisy. Use Spearman–Brown on split halves.
- **m14. Competition framing.** The 3막 "Direct vs R-lens vs Ceiling" dot plot reads as competition. Label it as a share or decomposition, per the project rules.

---

## Do before any GPU job, in order

1. Unify on one partition and add the leakage unit test (F1).
2. Run the identifiability gate (F2: collinearity report, recovery simulation, split-half gate) on existing features. This is CPU-only and can start now.
3. Redesign 2막: add the N-27 arm, fixed epoch budget, fixed total batch, CKA covariate; fix step 5 (F3).
4. Unify the HK data product and verify HK–MC subject identity (M13a, M13c).
5. Rewrite the statistics plan: within-subject inference plus prevalence, permutation resolution, absolute SESOI, Δr instead of ρ (M2–M5).
6. Run within-VCE dedup and re-derive lens-val (M11).
7. Add the H1 rating band, H2 pair test, decodability-matched null and ROI-removal test (M6, M16).

## What already holds up

- The lens is frozen before any Cowen, HK, MC or Emo-FilM label is seen.
- The D_R target contains features only, no ratings.
- MC-72 is excluded everywhere, and MC runs once after a commit-hash freeze.
- HK results are explicitly labelled exploratory.
- All outputs are continuous; there is no top-1.
- The Haufe pattern formula is stated.
- Kragel and Gao settings are traced to the source text.
- Alternatives to Brain-IT and MindEye2 are argued from code facts.
- Kill-tests are fixed before results are seen.

**Local evidence files cited:**
- `/home/user/EmoBrain/CONTEXT_EMOBRAIN.md`
- `/home/user/EmoBrain/docs/paper_logic_merged.md`
- `/home/user/EmoBrain/docs/notes/project_decisions.md`
- `/home/user/EmoBrain/project/scripts/build_roi_timeseries.py`
- `/home/user/EmoBrain/project/data/fmri_adapter.py`
- `/home/user/AffectLab/src/crossmodal_emotion/fold_plan.py`
- `/home/user/AffectLab/docs/FIRST_PILOTS.md`

PubMed was the source for the five newly verified citations: Kriegeskorte 2009, Alexander-Bloch 2018, Ince 2021, Walther 2016, Winkler 2016. DOIs are linked above.