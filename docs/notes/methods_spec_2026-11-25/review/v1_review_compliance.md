# Compliance and feasibility review: EmoBrain methods spec v1 (2026-11-25)

**Verdict.** The 4-act design mostly complies with the project rules.

- **Must fix before any script is written or GPU job runs:** three items (C1–C3).
- **Must fix before the affected act runs:** eight high-severity items.
- **Biggest risks:**
  - The spec conflicts with the canonical documents (H4 and the LabelQueryDecoder).
  - The HK ROI-mean input used for the MC and Emo-FilM transfer is not what the spec says it is.
  - The VCE authors' training script opens VCE-test on its own and saves checkpoints by top-1 accuracy.

Path root: `SP=/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad`

---

## A. Issues by severity

### CRITICAL (fix before writing scripts)

**C1. The spec conflicts with the canonical project documents (CLAUDE.md v7 and paper_logic_merged.md).**
- What the canonical documents say:
  - The model's place in the paper rests on H4.
  - The model is a LabelQueryDecoder that puts brain, video and caption into one memory and reads it with 34 queries, trained teacher → cache → student.
  - H4 requires a brain-only student trained on labels only, with the same initialization and seed.
  - H4 also requires a control where brain data are paired with the wrong stimuli.
  - Sources: /home/user/EmoBrain/docs/paper_logic_merged.md L100-104 and L148-198; /home/user/EmoBrain/project/README.md L18-21; /home/user/EmoBrain/CONTEXT_EMOBRAIN.md L5-10.
- What the spec does:
  - It never mentions H4, the LabelQueryDecoder, the teacher/student setup, or a joint brain+video+caption model.
  - It switches to 27 dimensions.
  - It never tests H2 (see M1).
- Under CLAUDE.md, other agents (Codex and others) would be following contradictory rules.
- **Fix:** before writing scripts, add a dated entry to /home/user/EmoBrain/docs/notes/project_decisions.md and bump CLAUDE.md to v8. The entry should:
  - (a) map each act to H1–H4. Act 3 (the R-ℓ content route vs the Direct decoder) and 4b (Emo-FilM) become the H4 test and its cross-dataset part.
  - (b) decide the fate of the LabelQueryDecoder. The cleanest option is to keep it as the H4 student. Use the frozen lens / g_level outputs as the "stimulus-only teacher". paper_logic L196 already lists that teacher as an open control. Keep the brain-only label student and the mismatched-pair control required at L177-188, with 27 queries. paper_logic L163-167 says query sets are designed to be swapped.
  - (c) record the 34 → 27 decision.

  Write H4's "decoder is more accurate" as a difference with a CI, as paper_logic does, not as a win.

**C2. Run as-is, the VCE authors' fork opens VCE-test and selects checkpoints by top-1.**
- Evidence:
  - `SP/verify_A_lens/JunShern_VideoMAE/run_class_finetuning.py` L529-530 calls `final_test(data_loader_test, ...)` on VCE-test with the last-epoch model at the end of every training run.
  - L500-507 saves the "best" checkpoint by val `acc1`, which is argmax top-1.
  - So every lens run, Act 2 arm and seed would open VCE-test before the checkpoint is chosen, and would use a top-1 selection rule.
- **Fix:** a small patch, committed and with its hash recorded:
  1. During training, set `dataset_test=None` (or add a `--no_final_test` flag).
  2. Replace acc1-best saving with a per-epoch val computation of mean per-emotion r, and save that checkpoint (or use a fixed epoch; see M3).
  3. Run VCE-test only from a separate eval script (`evaluate_vce.sh --eval`) after the lens is frozen.

**C3. The HK ROI-mean input for the MC and Emo-FilM transfer (4a/4b) is described wrongly and preprocessed differently.**
- §4.5 says the HK ROI-mean is the run-z AffectLab file "and therefore follows the MC convention". That is not so:
  - EmoBrain `roi_mean` comes from the in-house `horikawa_preprocess_JEPA_ROI` time series. The parcellation script is not in the repo (/home/user/EmoBrain/docs/REPRODUCE.md L38).
  - It is the time-mean over all valid TRs per stimulus (/home/user/EmoBrain/project/scripts/build_roi_timeseries.py L3-5, L46, L90).
  - Normalization uses `normalization_params.npz` computed over the whole dataset (/home/user/EmoBrain/project/shared/code/bfm_embeddings/_lib/SETTINGS_brain_jepa.md L60-64).
  - Whether a 4 s shift was applied is unknown.
- The other datasets are processed differently:
  - MC: 4 s shift, despike, block mean, run-z.
  - Emo-FilM: FSL, 6 mm smoothing.
- **Fix:**
  1. Rebuild the HK ROI-level inputs from the AffectLab blocks (`*_blocks_common36_qc_runz.npy`, or the pre-normalization `blocks_common36_qc` that already gives 370 anatomical ROI means; /home/user/AffectLab/docs/FIRST_PILOTS.md L66).
  2. Use one atlas that can be placed in all three datasets, and the identical order of operations in all three: 4 s shift → despike → block mean → run-z → ROI mean.
  3. Write that order into the spec.
  4. Keep the old roi_mean only for the R0 = 0.294 continuity check.

### HIGH

**H1. MC: normalization rule and subject overlap.**
- (a) **Run-z.** MC run-z uses statistics of the MC responses. The spec leaves this to the PI (§6.2), but 4a cannot be coded until it is decided. Record the ruling: the authors' released preprocessing counts as "data as released", not as fitting by us. Use the same order of operations for HK (see C3).
- (b) **Subject overlap is unverified.** MC S1 "was exposed to the same stimuli multiple times" in a preliminary experiment (`SP/mindcap.txt` L118). HK and MC come from the same lab and stimulus set.
- **Fix for (b):** compare `participants.tsv` in OpenNeuro ds005191 with the HK subject demographics, or ask the authors. Any overlapping subject is reported as "same person, different session" and removed from the "new people" claim. CONTEXT L48 already says MC is subject replication, not generalization.

**H2. The Act 2 arms differ in more than the objective.**
- §2c says only the head and the loss differ. In fact the arms also differ in:
  - target source: human ratings vs teacher soft labels;
  - output dimension: 27 / 710 / 21841;
  - loss family: BCE vs soft CE;
  - selection criterion: per-arm val loss.
- According to PubMed, Conwell et al. 2024 (*Nat Commun* 15:9383, [DOI](https://doi.org/10.1038/s41467-024-53147-y)) report:
  - task objectives give near-equivalent brain predictivity when diet is held constant;
  - linking methods "may be too flexible".
  So a null result is likely, and the arms must be clean.
- **Fix:**
  1. Add an **N-act-27** arm. Take the K710 teacher probabilities, reduce them to 27 PCs fit on lens-train, squash to [0,1], and train the same 768→27 head with BCEWithLogits. Keep N-act-710 as secondary.
  2. Use one epoch rule for all arms (see M3).
  3. Fix the GPU count (see M4).
  4. Add a fit-free linking metric, RSA (Kriegeskorte et al. 2008, already verified), next to encoding r.
  5. Cite Dobs, Martinez, Kell & Kanwisher 2022 as a precedent for training the same architecture on different tasks: "Brain-like functional specialization emerges spontaneously in deep neural networks", *Sci Adv* 8:eabl8913 (according to PubMed, abstract verified; [DOI](https://doi.org/10.1126/sciadv.abl8913)).

**H3. Act 3 ratio metrics are unstable, have no precedent, and read as competition.**
- The metrics are ρ_med = r(R-ℓ)/r(Direct) and ρ_rec.
- In transmodal ROIs the Direct r is near 0, so the ratio can blow up or flip sign.
- Comparing "route vs direct" reads as a contest.
- R-lens = W_head·D_R is itself linear, so R-lens vs Direct really compares a constrained linear readout (VCE's 27-d subspace) with an unconstrained one. Say so.
- **Fix:** make the headline a variance partition of y_e on the two prediction vectors: unique(R-ℓ), unique(Direct), shared. Fit on the val fold and score on test; this is the same set logic as Lescroart. Report ρ only as secondary, and only where the CI of the denominator excludes 0.

**H4. 1,000 permutations cannot pass BH-FDR in the large test families.**
- The smallest possible p with 1,000 permutations is about 1e-3.
- For ROI × emotion (42 × 27 = 1,134 tests), BH needs p ≤ 4.4e-5 for the first-ranked test. Nothing passes unless at least 23 tests sit at the floor.
- The 370-region family has the same problem.
- **Fix:** for these families use at least 1e5 permutations, or analytic / t-based p values checked against permutation, or a cited tail approximation.

**H5. The robustness lens (V-JEPA 2.1 ViT-L/384 frozen probe) may be the largest single GPU job, and §5 leaves it out.**
- Per the config: 8 segments, 20 epochs, and the encoder is re-run every epoch.
- That is about 4.9 TFLOP per 16-frame, 384² segment (my arithmetic), roughly 10× a lens run. See section B.
- **Fix:** use V-JEPA 2.1 ViT-B/384 (80M), or 2 segments as in the repo's ssv2 config, or V-JEPA 2 ViT-L at 256. Time one pilot epoch, and add the job to §5.

**H6. Short videos are handled silently.**
- `SP/verify_A_lens/JunShern_VideoMAE/vce_dense.py` L362-366 drops every VCE video shorter than one 16-frame clip at 4 fps (about 4 s). The lens is never trained on them.
- Cowen clips have median 4.51 s and MC test clips mean 3.94 s. Inference path (b) cannot form a window for many of them.
- The test path pads by repeating the last frame index (`vce.py` L262-263).
- **Fix:**
  1. Log how many VCE videos are dropped.
  2. Use the repo test-path padding as the short-clip rule for both paths (a) and (b).
  3. Run a sensitivity analysis that excludes Cowen clips under 4 s.

**H7. Emo-FilM film sources are risky.**
- Chatter and Spaceman are hosted on vodo.net. I believe the site is offline (from memory, unverified). vodo.net, vimeo.com and youtube.com all returned 403 from this sandbox.
- Five films are NC-licensed (After The Rain, Chatter, Spaceman, The Secret Number, To Claire From Sonny) (`SP/v2_datasets/dl_emofilm/FilmInfo.txt`).
- **Fix:**
  1. Fetch and check all 14 films before the 358.7 GB fMRI download: match each film's duration and fps to the cut points in the xlsx.
  2. Fallbacks: the LIRIS-ACCEDE continuous set (academic form), or a request to the Emo-FilM authors. If films cannot be obtained, pre-declare a 12-film analysis.
  3. In figures, show frames only from CC-BY films: Big Buck Bunny, Sintel, Tears of Steel, Between Viewings, First Bite, Payload, Superhero.

**H8. Act 1 Cowen test status is overstated.**
- The canonical 1748/217/220 split is valence/arousal-quartile stratified, so ratings were used to bin stimuli when the split was built (/home/user/EmoBrain/project/shared/code/build_canonical_split.py L3, L59-92; the `horikawa_split.csv` header has `v_quartile`, `a_quartile`).
- EmoViS stimulus-side analyses probably covered all stimuli (unverified).
- **Fix:**
  - Label the Act 1 Cowen results exploratory and put confirmatory weight on VCE-test.
  - State that the split is emotion-stratified. AffectLab /home/user/AffectLab/AGENTS.md L17 has the analogous rule.
  - Or run Act 1 on the label-free hk_dev_v4 folds as well. This also settles the open "unify the two splits" item in §6.2.

### MEDIUM

**M1. H2 is untested; one Act 2 analysis duplicates EmoViS.**
- The spec has no conflict-pair analysis. Either state that EmoViS owns H2 (CONTEXT L5), or add the D9 pair gallery with continuous rank-difference selection at 5/10/20%, as paper_logic prescribes.
- Act 2 step 4 (level → region banded ridge) duplicates EmoViS's open "clean 3-band banded ridge" with different bands. Agree on one version.

**M2. The 27 vs 34 change is unrecorded, and label semantics differ between datasets.**
- VCE labels are mean intensity (select-then-rate). Cowen labels are the proportion of raters endorsing the category. State this.
- Map the 27 names by a name table that is asserted in code, not by position. "Awe (or Wonder)" vs "awe" is the one name that differs beyond case.

**M3. Inconsistent checkpoint rules.**
- The main lens is chosen by max val r, while Act 2 arms are chosen by min val loss, yet the spec says "main lens = E seed 0".
- Repo checkpoints are saved only every 10 epochs (`--save_ckpt_freq 10`).
- **Fix:** use the fixed final epoch 50 for every run. The cosine schedule ends at min_lr. Log the val-r curve as a sanity check only.

**M4. GPU count changes the learning rate; the clip index is rebuilt at every launch.**
- Effective lr = 5e-4 × total_batch / 256 (run_class_finetuning.py L398-402), so results depend on the GPU count. Fix the GPU count for all arms and seeds.
- `datasets.py` L194-204 does not pass `cached_video_clips`, and VideoClips builds with `num_workers=1` (`vce_dense.py` L72, L107-120). So the timestamp index over roughly 45k videos is rebuilt on every launch. Pickle it once.

**M5. FastL2LiR memory and time; the whole-brain decoder needs a different solver.**
- FastL2LiR builds XᵀX over all ROI voxels in float64, then loops per output with single-thread BLAS (`SP/v2_brain/PyFastL2LiR/src/fastl2lir/fastl2lir.py` L258-279).
- The whole-brain 50k-voxel decoder with per-unit selection would need a 20 GB W0 per alpha.
- **Fix:**
  - Whole-brain decoder: ridge on all 50k voxels in dual form (`use_all_features`), as MC did.
  - Parallelize over ROI × fold × subject.
  - Order of cost: section B.

**M6. PG1 deciles in native space are not feasible as written.**
- HK's per-subject PG maps are not in the repo, and the h5 files have no transforms to standard space.
- **Fix:** assign each HCP-MMP parcel its mean Margulies PG1 value in standard space (for example via neuromaps; verify the source), then bin parcels into deciles. Label this a deviation from H20's voxel deciles.

**M7. Wrong partition count in §2d.** With 4 bands, the Lescroart set partition needs 15 models, not 7. Act 1 has 3 groups, so 7 is right there.

**M8. TOST SESOI rule.**
- "SESOI = seed SD" is not stated by Lakens or Mehrer, and an SD from 2–3 seeds is unstable.
- **Fix:** fix the SESOI value before the Act 2 analysis: log it from the pilot seeds and freeze it. Label it D-.

**M9. Only 5 subjects for the 2-factor bootstrap.**
- There are only 126 distinct subject resamples.
- Report per-subject estimates and sign consistency (n/5) alongside, and use rsatoolbox's small-sample correction (`_dual_bootstrap` n/(n−1)).

**M10. Emo-FilM window length is invented.**
- "5 TR = 6.5 s" is derived from the mean Cowen clip length.
- But each HK sample averaged over its own video's duration, and MC blocks are at least 10 s. Label it D-, pre-declare a sensitivity set, and specify the 4 s shift at TR 1.3 s.

**M11. Sound is a confound in the Emo-FilM brain transfer.** Exclude the EAC/AAC groups as a sensitivity analysis and add an audio-envelope nuisance regressor to the decoding path as well.

**M12. S-cap features: use the authors' release.** MC already releases `feature/video/deberta-large/layer01..24.mat`. Use these as-is for S-cap-full, check a subset against a recomputation, and recompute only the noaff / shuf / bow variants.

**M13. File formats and IDs.**
- MC `.mat` files may be v7.3 / HDF5 (unverified); use h5py or mat73.
- HK h5 files are bdpy.
- Emo-FilM is NIfTI plus tsv.gz.
- Re-encode yt-dlp trailers to H.264 at a fixed fps before any extractor.
- VCE `metadata.json` stores duration and frame_rate as strings.
- Build one ID crosswalk manifest: VCE 5-digit ID ↔ Cowen stim_num 1–2185 ↔ HK stimulus_name ↔ MC video_id (including the 16 duplicates).

**M14. VCE is a single point of failure.**
- The Google Drive folder was never inspected, and the size, quota and licence are unknown.
- Make the first job: download, checksum, count, and compute total duration (this also fixes the ~700k-frame estimate). Until the licence is known, show no VCE frames.

**M15. Recency constraint.**
- The main lens is a 2022 VideoMAE K400 pretrain.
- State explicitly that recency is traded for grounding in the VCE authors' recipe, and that lens B (V-JEPA 2.1) is the recency check.

**M16. Code via git clone.**
- Several pieces come from pip or single downloaded files, not clones: torchvision AlexNet, spaCy (model and version unstated), transformers, and rsatoolbox (single files in `SP/v2_methods/dl`).
- Clone and pin commits.

**M17. Methods still described from secondary sources.**
- Haufe's formula comes from MNE code plus search snippets.
- Doerig's ladder comes from paper_logic §5. According to PubMed, the Doerig et al. 2025 abstract supports only "controlled comparisons … beyond individual words" (*Nat Mach Intell* 7:1220-1234, [DOI](https://doi.org/10.1038/s42256-025-01072-0); full text PMC12364710).
- Margulies 2016, MindEye2, Gao's fc8 component count and Kragel's permutation count are also not from primary text.
- Read the primaries before the manuscript.

**M18. Trailers.**
- Trailers12k has only YouTube IDs. NERSC downloads may be blocked, and YouTube ToS and copyright apply. Kragel's own 28-trailer list sits in a supplement I could not reach.
- **Fix:**
  - Download about 30 IDs first and check that they arrive.
  - Make stage 2 optional.
  - Never redistribute; use CC stand-ins in figures.
  - Drop the argmax 3-way accuracy entirely; keep AUC and coefficients.

### LOW

- **L1.** Act 1 Fig. B orders stimuli by hierarchical clustering, which groups them by emotion profile. Order by RDM PC1 / seriation or by UMAP angle (H20) instead.
- **L2.** Act 2 Fig. B uses "E advantage / N advantage" colours. Relabel as the sign of objective-specific unique variance.
- **L3.** The Δ formula is asymmetric (mean over subjects on one side only). Average both sides over subjects.
- **L4.** Ratan Murty 2021. According to PubMed, the abstract describes screening and synthesis checked by category membership, with no new fMRI ([DOI](https://doi.org/10.1038/s41467-021-25409-6)). The spec's wording is correct; R5's "new fMRI [V]" is wrong. Gu et al. 2023 is confirmed to validate with new fMRI ([DOI](https://doi.org/10.1038/s42003-023-05440-7)).
- **L5.** §6.3 lacks titles for Horikawa 2020, Mazeika 2022, Morgenroth 2025 and others. CLAUDE.md requires author, title and venue.
- **L6.** Script paths: the spec gives `/home/user/EmoBrain/...`. The project convention is `bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/...` (project/README.md L69-71).
- **L7.** Emo-FilM: which 13 columns are the discrete emotions is still inferred (I). Read Supplementary Table 1 before analysis.
- **L8.** K-dec "near 0.294" has no tolerance. Pre-specify one (for example, within the bootstrap CI of 0.294 on the same split).

---

## B. Scale of each GPU and CPU job

**How these were computed.**
- Token counts, epochs and sample counts come from the verified configs.
- The rest is my arithmetic. Forward FLOPs ≈ 2·params·tokens + 4·N²·d·L, with params ≈ 12·d²·L.
- Training ≈ 3× forward.
- I assumed a sustained 100 TFLOP/s on one A100 in fp16. The repo uses autocast: engine_for_finetuning.py L67/159/199.
- Video decoding with 10 CPU workers may dominate the lens runs. Measure with the step-3 pilot.

| Job | Verified quantities | Estimate |
|---|---|---|
| Lens E, 1 run (1 GPU × batch 8, 50 epochs) | lens-train ≈ 34.5k–45k videos; 1,568 tokens per clip; ViT-B ≈ 85M params | ~0.36 TF forward, ~1.1 TF train per sample; 1.9–2.4 EFLOP; ~5–7 h of compute, ~5–15 A100-h in practice |
| Act 2 arms | 8 runs (S=3: E +2, E-perm 3, N-act 3) up to 14 runs (+N-act-27, +N-obj) | ~40–210 A100-h. Largest block |
| Lens B: V-JEPA 2.1 ViT-L/384 probe | 4,608 tokens per segment; 8 segments; 20 epochs; frozen encoder | ~4.9 TF per segment; ~27–35 EFLOP; **~75–100+ A100-h**. ViT-B/384 ≈ 25–32 h; 2 segments ≈ 20–25 h |
| PE-Core G14-448 frames (duplicate screen + S-vis) | width 1536, 50 layers, 1,024 tokens | ≥3.2 TF per frame (MLP ratio unverified). ~745k frames at 1 fps (VCE durations unverified) + ~506k S-vis frames → ~10–25 A100-h. PE-Core L14-336 is ~8× cheaper for the duplicate screen |
| EVA02-L 448 (O-obj + N-obj teacher) | ~190k frames | ~0.7 TF each; <1 A100-h |
| VideoMAE V2-B K710 (O-act + N-act teacher) | 15 views × ~63k videos | ~0.34 EFLOP; ~1 A100-h |
| Lens inference (VCE-test, Cowen, Emo-FilM 9,600 windows × 3 crops, trailers) | | <1–2 A100-h; decoding-bound |
| pymoten on GPU | VCE ~17.6M frames at 24 fps, if mean ≈12 s (unverified) | Compute is small; I/O-bound |
| HK encoding with himalaya | ~150k voxels per subject (AffectLab sub-01: 149,080); Act 2: ~5.9k KernelRidgeCV fits | ~10–20 GPU-h |
| FastL2LiR decoders (CPU) | ~7.4k outputs × 10 alphas × 42 ROIs × 30 subject-folds ≈ 93M solves of 501×501, plus the lens 370-region path ≈ 85M | ~10–20 ms each → **~500–1,000 CPU-h**, roughly 5–8 Perlmutter CPU node-hours |
| Emo-FilM fMRI download | 358.7 GB (MNI ppres) over S3 | CONTEXT L45 says ~132 GB; the annex-key total is authoritative |

---

## C. Hyperparameters lacking a source or mis-sourced

Each item gives the section, the parameter, and what is needed.

**§1.6 duplicate screen**
- Letterbox threshold ("near-0 luminance"): no value, no source. Label D-.
- Positive controls: brightness-change size, and the H.264 re-encode CRF/bitrate. Neither is specified. The 256×320 size comes from a single README example.
- pHash: **now sourced** as [R: imagehash 9322be5, `__init__.py` L259, `hash_size=8, highfreq_factor=4`], from a clone at `SP/v3_review/imagehash_repo`.

**§2a lens inference**
- The 3 crops for sliding-window path (b) should be labelled [R: test_num_crop 3].
- The short-clip padding rule is missing (see H6).
- GPU count is missing (see M4).

**§2b features**
- **pymoten frame-mean pooling.** [P: H20 block average] is a mis-source: H20 averaged BOLD, not features. Label D-, or cite a primary motion-energy-on-HK pooling rule (Du et al. 2023; check its text).
- **O-obj 3-frame aggregation.** Averaging logits, probabilities or pre-logits is not stated. Kragel averaged outputs over time.
- **S-cap-bow.** The definition, the lemmatizer (spaCy model and version) and the vocabulary floor are all missing.
- **S-vis `normalize=False`.** Unlabelled choice.
- **g_level alpha grid `logspace(1,6,10)`.** Borrowed from MC brain decoders (n ≈ 2k, voxel inputs) and applied to n ≈ 45k stimulus features. Mark it as borrowed and add a rule to extend the grid when the optimum hits its boundary.

**§2c Act 2 arms**
- E-perm with one shuffle per seed: unlabelled design choice.
- Teacher softmax temperature for N-act and N-obj: missing.
- Whether EVA 3-frame outputs are averaged as probabilities or logits: missing.
- Val-loss checkpoint rule: no source, and inconsistent with the lens rule.

**§2d encoding**
- The noise-ceiling proxy (leave-one-subject-out inter-subject r) has no source.
- The MC alpha grid conflicts between code (10¹–10⁶) and paper (10–10⁴). The spec should say it follows the code.

**§2e decoding**
- The affine (mean/SD) correction of decoded features has no source. Label D-, or find a Kamitani-lab primary.

**§3.0 statistics**
- SESOI = seed SD: invented, and mis-attributed to Lakens and Mehrer.
- 1,000 permutations: borrowed from Gao's small families and inadequate here (see H4).
- 1,000 circular shifts: borrowed. The minimum shift (exclusion zone) is missing.
- The TOST alpha is missing.

**§3.3:** ρ_med and ρ_rec have no precedent (see H3).

**§3.4 (4d)**
- The PLS component grid 1–20 comes from Gao's fixed count of 20, which is not a grid bound.
- The PLS implementation is unspecified. Gao used MATLAB `plsregress` (SIMPLS); sklearn uses NIPALS with `scale=True`.

**§4.1 trailers**
- 10,000 permutations is inferred from "P < 0.0001"; Kragel's actual count is unverified.
- The number of inner-CV folds is missing.
- Residualizing the lens-27 on L has no source.

**§4.2 Gao-style figures**
- G1 uses 15 folds. In Gao, 15 is the number of BOLD5000 sessions (data structure), so here it is an arbitrary k. Label it borrowed.
- G1 PLSR with 20 components: Gao states 20 only in the layer-wise section; the count for the fc8 model is unverified.
- G1 stability measure (top-10 frequency over 1,000 bootstraps): no source.
- G2 component grid: borrowed.
- G3 top-5 words per cell: display choice, unlabelled.

**§4.3 in silico**
- The "matched predicted variance" random-direction null and the 1,000 random 24-video sets have no source.
- The criterion for which encoders count as significant should be pre-specified.

**§4.4 Emo-FilM**
- Window of 5 TR: invented.
- 1-TR stride: unlabelled.
- HRF model, audio-envelope method and nuisance set: all missing.

**§4.6 V2V:** the inner 5-fold CV is unlabelled (the grid is D6.17).

**§5 kill tests**
- K-seed "|Δ| < seed SD": invented.
- K-dec tolerance: missing.

---

## D. Checked in this pass (primary files and code)

**JS fork** (`SP/verify_A_lens/JunShern_VideoMAE`)
- `run_class_finetuning.py` L500-507: best checkpoint by acc1. L529-530: final test on VCE-test.
- `engine_for_finetuning.py` L67/159/199: fp16 autocast.
- `datasets.py` L194-204: no VideoClips cache passed.
- `vce_dense.py` L362-366: short videos dropped. `vce.py` L262-263: test-path padding.

**Brain-side code**
- `SP/v2_brain/PyFastL2LiR/src/fastl2lir/fastl2lir.py` L258-279.
- himalaya: `KernelRidgeCV(alphas, kernel="linear", ...)` at `kernel_ridge/_sklearn_api.py` L447; random-search defaults `n_iter=100`, `concentration=[0.1,1.0]` at `ridge/_random_search.py` L17-18.

**EmoBrain and AffectLab provenance**
- `/home/user/EmoBrain/project/scripts/build_roi_timeseries.py`
- `/home/user/EmoBrain/project/shared/code/bfm_embeddings/_lib/SETTINGS_brain_jepa.md`
- `/home/user/EmoBrain/project/shared/code/build_canonical_split.py`
- `/home/user/AffectLab/docs/FIRST_PILOTS.md` L66
- `/home/user/AffectLab/01_AffectModels/1-1_Vision2Affect/README.md` L131: the 0.505 result was on the HK split.

**Papers and data notes**
- `SP/mindcap.txt` L118 (S1 preliminary exposure), L122 (videos shown silent).
- `SP/v2_datasets/dl_emofilm/FilmInfo.txt`: film licences.

**PubMed** metadata and abstracts: Conwell 2024, Doerig 2025, Dobs 2022, Gu 2023, Ratan Murty 2021 (DOIs above).

**Not verifiable here:** vodo.net, vimeo.com and youtube.com all returned proxy 403.
