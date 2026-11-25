##### cueconflict
REPORT: cue-conflict and figure/background split, brought over from vision to emotion. All repos were cloned read-only into /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_*/. Nothing under /home/user was modified (one caption CSV was read).

Labels used below: VERIFIED = I read the primary source (repo README or code, PubMed abstract or full text). INDIRECT = search snippet only. UNVERIFIED = my estimate or not checked.
WebFetch could not reach arxiv.org or openreview.net (the host does not resolve in this session). Both need to be allowed in network settings to read the paper PDFs, so paper-internal details are INDIRECT at best.

=== 0. BOTTOM LINE ===
- **The method is not new in vision, and one video paper already does it end to end.** That paper is Chung, Wu & Russakovsky, "Enabling Detailed Action Recognition Evaluation Through Video Dataset Augmentation" (NeurIPS 2022 Datasets & Benchmarks track; the toolkit is called HAT). It segments people in video, removes and inpaints them, and pastes one video's person onto another video's inpainted background. It does this for action recognition.
- **No study did this in emotion research or with brain encoding models.** I found none in 13 PubMed searches, 21 web searches and 10 repository reads. Specifically, nothing used segmentation plus video inpainting on evoked-emotion videos to:
  (a) separate the main figure (person, animal or object) from the setting, or
  (b) swap figure and setting across videos,
  and then read out (i) a multi-dimensional evoked-emotion model or (ii) brain-region encoding-model predictions.
- **Emotion psychology already has face/body versus scene conflict studies in people.** Examples are Aviezer 2008, Righart & de Gelder 2006 and Chen & Whitney 2019. They are face-centred, about the perceived emotion of a depicted person, use few categories or valence/arousal only, and involve no model and no brain-encoding mapping.
- **So the methodological novelty is a transfer; the scientific novelty is the target.** The target is evoked 27-dimensional profiles, plus a cortical map of how much each region follows the figure versus the setting.
- **Strongest motivation from primary text.** Gao, Ajith & Peelen 2025 (Communications Biology) is correlational only. VERIFIED full text: "our results cannot exclusively be interpreted as supporting a causal relationship between object categorization (cause) and emotion (effect)." A figure/setting manipulation is the direct causal test of their object claim.
- **Main risk 1:** reviewers may call it "HAT for emotion." Answer: frame it as a measurement of which information drives evoked emotion and which brain regions follow, not as a robustness benchmark.
- **Main risk 2:** edited videos are out of distribution for encoding models trained on about 2,180 natural videos. The brain-side results are in-silico predictions, so validation must be preregistered.

=== 1. VISION CITATIONS ===
**Geirhos, Rubisch, Michaelis, Bethge, Wichmann & Brendel, "ImageNet-trained CNNs are biased towards texture; increasing shape bias improves accuracy and robustness"**
- Title, authors and OpenReview id Bygh9j09KX: VERIFIED (README of rgeirhos/texture-vs-shape).
- Venue ICLR 2019 (oral): INDIRECT (iclr.cc virtual 2019 oral page; arXiv 1811.12231 comments).
- Cue-conflict stimuli are made by style transfer (shape of one category with the texture of another). The repo has 16 category folders and 1,280 images in stimuli/style-transfer-preprocessed-512: VERIFIED (I counted the files).
- The README states the cue-conflict set is NOT Stylized-ImageNet: VERIFIED.
- Shape bias = shape decisions divided by (shape + texture decisions): INDIRECT. This is a top-1 decision measure, so it must not be ported literally under our rules. Use the continuous version in section 5.
- A 2025 critique (arXiv 2509.20234, "...are not biased towards texture") says the texture cue also carries colour and local shape: INDIRECT.

**Xiao, Engstrom, Ilyas & Madry, "Noise or Signal: The Role of Image Backgrounds in Object Recognition"**
- Title and authors: VERIFIED (MadryLab/backgrounds_challenge README BibTeX, which cites it as arXiv 2006.09994).
- Venue ICLR 2021: INDIRECT (iclr.cc virtual 2021 poster 2857; mlanthology).
- Correct variant names: Original, Only-FG, No-FG, Only-BG-B, Only-BG-T, Mixed-Same, Mixed-Rand, Mixed-Next (plus the IN-9L training set). VERIFIED, README. "only-BG" in the task text is really two variants, Only-BG-B and Only-BG-T.
- BG-Gap = Mixed-Same accuracy minus Mixed-Rand accuracy: VERIFIED (README).
- How foregrounds were extracted (bounding boxes plus a segmentation step): UNVERIFIED (paper not readable here).

**HAT, the closest video precedent (Chung, Wu & Russakovsky; princetonvisualai/HAT)**
- NeurIPS 2022 Datasets & Benchmarks track, 74 Kinetics models analysed: INDIRECT.
- From the README and code (VERIFIED):
  - Background Only: human segmentation removed and inpainted.
  - Human Only: the rest of the frame filled with the dataset average colour.
  - Action Swap: the original-RGB person plus mask pasted onto another video's inpainted background.
  - Tools used: SeMask segmentation and E2FGVI inpainting.
  - Swap frames are limited to 5–50% human coverage (doc/review_discussion.md).
  - The README plots accuracy against the percentage of synthetic pixels.
- Pair files are named close/far/rand/same: VERIFIED. Their exact meaning (probably class similarity, which we would replace with continuous profile distance): UNVERIFIED.
- Also INDIRECT: Li et al. (ICCV 2023), "Mitigating and Evaluating Static Bias of Action Representations in the Background and the Foreground" (backgrounds replaced in action videos).

=== 2. EMOTION-FIELD PRIOR ART (closest first) ===
Human behaviour and brain. According to PubMed (VERIFIED abstracts):
- **Aviezer et al. 2008**, Psychological Science 19(7):724–32, https://doi.org/10.1111/j.1467-9280.2008.02148.x
  - Identical facial configurations convey different emotions depending on the affective context they are embedded in.
  - The effect scales with how similar the face is to the face typical of that context. Eye movements were monitored.
- **Chen & Whitney 2019**, PNAS 116(15):7559–64, https://doi.org/10.1073/pnas.1812250116
  - Faces and bodies masked in silent videos; viewers tracked valence and arousal from context alone, with high agreement.
  - Context gave a unique contribution beyond face and body.
- **Chen & Whitney follow-ups:**
  - Chen & Whitney 2021, Cognition 208:104549, https://doi.org/10.1016/j.cognition.2020.104549 (speed of context-based perception).
  - Chen & Whitney 2022, Emotion 22(6):1185, https://doi.org/10.1037/emo0000934 ("visual context can override interpreted emotion categories from face and body").
  - Ortega, Murai & Whitney 2025, Nature Communications 17:786, https://doi.org/10.1038/s41467-025-67466-1 (face and context cue integration; Bayesian versus heuristic weighting; n=944).
- **Hao, Whitney & Bishop 2025**, Emotion 25(1):57–69, https://doi.org/10.1037/emo0001358
  - Natural crowd photos. They removed background context and swapped faces with faces from other images.
  - This is the closest human cue-swap with natural images, but it is face-centred, about group emotion, and uses valence/arousal/dominance only.
- **Righart & de Gelder 2006**, Cerebral Cortex 16(9):1249, https://doi.org/10.1093/cercor/bhj066
  - Fearful/neutral faces embedded in fearful/neutral scenes, with event-related potentials.
  - Included context-only and face-only control experiments.
- **Van den Stock et al. 2014**, SCAN 9(10):1481, https://doi.org/10.1093/scan/nst138
  - fMRI with fearful/neutral faces on threatening/neutral backgrounds.
- **Mobbs et al. 2006**, SCAN 1(2):95, https://doi.org/10.1093/scan/nsl014; **Cao et al. 2024**, PLoS One, https://doi.org/10.1371/journal.pone.0308295
  - The Kuleshov effect: face and scene juxtaposed in time, with fMRI.
- **Fan, Shen, Jiang, Koenig, Kankanhalli & Zhao 2017**, ACM Multimedia, "The Role of Visual Attention in Sentiment Prediction", doi 10.1145/3123266.3123445. INDIRECT.
  - They compared human perception of the isolated focal object with the whole image.
  - Negative sentiment came from the focal region; positive sentiment came from both focal region and context.
  - They also built CNNs with focal-object channels.
  - This is the closest object-versus-context test for evoked sentiment. It is limited to images and binary sentiment, with no brain data.

Models and brain, the "already known" list re-checked:
- **Gao, Ajith & Peelen 2025**, Communications Biology, https://doi.org/10.1038/s42003-025-08145-1. VERIFIED full text.
  - Stimuli were BOLD5000 images (Scenes, COCO and ImageNet subsets), with no stimulus manipulation.
  - Compared AlexNet fc8 with EmoNet; the lateral occipital complex (LOC) was most prominent.
  - The authors themselves state the causal limitation quoted in section 0.
- **Soderberg, Jang & Kragel 2026**, SCAN 21(1), https://doi.org/10.1093/scan/nsag028. VERIFIED full text.
  - Compares features from a face-emotion network (EmoFAN) and a scene network (EmoNet) for predicting pSTS and amygdala.
  - The text has 0 hits for mask, occlusion, removal, blur, segmentation, manipulation or in silico.
- **Context-aware recognition models.** These model the perceived emotion of a depicted person, as architecture or debiasing, not as a swap measurement:
  - EMOTIC (Kosti et al., CVPR 2017; TPAMI 2019): VERIFIED via the rkosti/emotic README. The two-stream body-box plus whole-image design is INDIRECT.
  - CAER-Net (Lee et al., ICCV 2019) hides faces in its context stream: INDIRECT.
  - EmotiCon (Mittal et al., 2020) masks the primary agent: INDIRECT.
  - CCIM (Yang et al., CVPR 2023, context de-confounding) and CLEF (Yang et al., CVPR 2024, a context-only branch to remove the direct context effect): INDIRECT.
  - CTERNet (IJCAI 2025) uses a counterfactual affective-region map: INDIRECT.
  - DSPO (arXiv 2609.36775) masks regions inside an emotion-reasoning multimodal model: INDIRECT.
- **Emotion-driven image editing** (EmoEdit, CVPR 2025; EmoEditor / "Make Me Happier", 2024) generates edits toward a target emotion. That is the reverse direction, not cue separation: INDIRECT.

Vision-neuroscience precedents for the brain side. According to PubMed (VERIFIED abstracts):
- **Loke et al. 2024**, Journal of Cognitive Neuroscience 36(3):551, https://doi.org/10.1162/jocn_a_02098
  - The same objects placed on different backgrounds, recorded with EEG and compared with deep convolutional networks.
  - Early EEG and early network layers represent the background.
- **Loke et al. 2026**, Current Biology 36(18):4827, https://doi.org/10.1016/j.cub.2026.08.008
  - Natural, texture-synthesized and object-only (background removed) images, with EEG.
  - Network–EEG alignment was strongest for texture-synthesized images.
- **Seijdel et al. 2020**, PLoS Computational Biology, https://doi.org/10.1371/journal.pcbi.1008022; **Seijdel et al. 2021**, Journal of Neuroscience, https://doi.org/10.1523/JNEUROSCI.2851-20.2021
- **Brain Dissection** (Sarch et al., NeurIPS 2023) and **BrainSAIL** (Luo et al., ICLR 2025) attribute image regions to encoding-model predictions: INDIRECT.

=== 3. SEARCH LOG FOR THE NOVELTY VERDICT ===
PubMed (13 searches; date filter where noted):
1. Aviezer 2008 title
2. Chen & Whitney "unseen"
3. emotional scenes figure-ground object context fMRI (0 hits)
4. DNN emotion context face composite Aviezer (0)
5. emotion/affective + scene context + object + fMRI + amygdala/visual cortex (7, none relevant)
6. Kuleshov / contextual framing (6)
7. de Gelder scene/context + body/face expression (11)
8. Whitney + inferential/affective tracking (8)
9. Kensinger negative object on neutral background (1)
10. Scholte object background + network/EEG (5)
11. emotion + inpainting/object removal/background removal/segmentation + network, 2018 onward (11, none relevant)
12. encoding model in silico emotion edited images (0)
13. figure-ground emotional pictures, IAPS (2, not relevant)

Web (21 searches; "ext." marks extended mode):
- object context cue conflict emotion deep network (ext.)
- emotion recognition background swap / inpainting / context-only (ext.)
- visual sentiment object removal / counterfactual (ext.)
- "cue conflict" emotion network (ext.)
- fMRI encoding in-silico emotion with removed/inpainted content (ext.)
- affective video content background/foreground counterfactual (ext.)
- backgrounds challenge / Mixed-Rand / Only-FG + emotion
- facial expression recognition texture/shape bias
- EMOTIC masked person
- VEATIC
- EmoEdit
- CAER-Net
- CCIM
- CLEF
- Fan 2017 (2 searches)
- Brain Dissection / BrainSAIL
- out-of-distribution encoding models
- HAT venue
- Xiao venue
- Geirhos venue

Repositories read (10): texture-vs-shape, backgrounds_challenge, HAT, sam2, sam3, Grounded-SAM-2, ProPainter, DiffuEraser, MiniMax-Remover, emotic.

Verdict: the specific combination was not found in these 34 searches. Say "not found in 34 searches," not "never done."

=== 4. TOOLS (VERIFIED from cloned repos unless marked) ===
**Segmentation**
- **SAM 2** (facebookresearch/sam2)
  - License: Apache-2.0.
  - Requires Python ≥3.10, PyTorch ≥2.5.1, CUDA toolkit.
  - SAM 2.1 checkpoints: tiny, small, base_plus, large (38.9M to 224.4M parameters).
  - The video predictor needs a point, box or mask prompt per object (add_new_points_or_box). Since December 2024, objects can be added after tracking starts.
  - Last commit 2024-12-15. Citation: Ravi et al. 2024, arXiv 2408.00714 (the conference venue is unverified).
- **SAM 3 / 3.1** (facebookresearch/sam3), the most recent option
  - Takes text prompts for "open-vocabulary concepts" and detects, segments and tracks every instance in video. No separate detector is needed.
  - Requires Python ≥3.12, PyTorch ≥2.7, CUDA ≥12.6.
  - Checkpoints are gated on Hugging Face; access must be requested.
  - License: custom "SAM License" (2025-11-19). Research use is allowed, and publications must acknowledge SAM Materials.
  - SAM 3.1 released 2026-03-27. Citation: Carion et al. 2025, arXiv 2511.16719. Last commit 2026-11-17.
  - Practical upside: text prompts can be noun phrases taken from each video's 20 human captions.
- **Grounded-SAM-2** (IDEA-Research)
  - Grounding DINO plus SAM 2, with text-prompted video tracking demos.
  - Apache-2.0, plus a separate Grounding DINO license file.
  - Fallback if SAM 3 access is not granted.

**Inpainting**
- **ProPainter** (sczhou/ProPainter; Zhou, Li, Chan & Loy, ICCV 2023; BibTeX in README)
  - License: S-Lab License 1.0, NON-COMMERCIAL only. Fine for academic work.
  - Python 3.8, PyTorch ≥1.7.1.
  - GPU memory, fp32/fp16, for 50 frames: 320x240 = 3G/2G; 640x480 = 10G/6G; 720x480 = 11G/7G; 1280x720 = 28G/19G.
  - Flags: --mask_dilation (default 4; helps catch edges and some shadow), --fp16, --subvideo_length (default 80), --resize_ratio, --height/--width.
  - Last commit 2026-10-27.
- **DiffuEraser** (lixiaowen-xw; Li et al. 2025, arXiv 2501.10018)
  - Diffusion inpainting that uses ProPainter as its prior.
  - Apache-2.0, but ProPainter's license still applies to the prior.
  - 640x360: 12G memory, 92 s per 250 frames on an L20 GPU.
- **MiniMax-Remover** (zibojia; arXiv 2505.24873)
  - Diffusion-transformer remover: 6 steps, no classifier-free guidance. Requires torch 2.7.1.
  - No LICENSE file in the repo, so licensing is unclear. Not recommended as the main tool.
- Removing shadows and reflections ("side effects") is not handled by ProPainter beyond mask dilation. Dedicated removers exist but I did not verify them (UNVERIFIED).

=== 5. FEASIBILITY ON ~2,180 VIDEOS ===
**Content estimate** (my computation; lexicon count over /home/user/EmoBrain/project/shared/data/caption_ck20.csv, 2,196 videos × 20 captions; rough, UNVERIFIED by humans):

| Content of the video | Videos | Share |
|---|---|---|
| Person mentioned in ≥50% of captions | 1,499 | 68.3% |
| Otherwise an animal in ≥50% | 290 | 13.2% |
| Body part only | 14 | 0.6% |
| Weak or mixed agent (20–50%) | 131 | 6.0% |
| No animate figure (food, explosions, mechanisms, landscapes, aurora) | 262 | 11.9% |

- About 82% of videos have an animate figure.
- About 12–18% need object prompts taken from caption nouns (for example "sushi", "key", "car"), or have no figure at all. For those, enter figure area = 0 as a continuous covariate; do not drop them silently.

**Figure size**
- Close-ups, where the face or body fills the frame, leave an empty setting.
- Precedent: HAT's 5–50% coverage rule. Preregister an area band and also report results along continuous mask area.

**Compute** (UNVERIFIED estimate)
- The lens model (VideoMAE) samples 16 frames at 224 px, so inpainting at 432x240 or 640x360 is enough.
- About 2,180 clips × ~200 frames (6.6 s at about 30 fps) needs roughly 2–10 GB of GPU memory with ProPainter, or about 45 GPU-hours with DiffuEraser at 640x360.
- Segmentation takes a few GPU-hours.
- Composites are a cheap alpha paste; HAT builds them on the fly in its data loader.
- Running the lens model and the encoding models on 10–20k variants is cheap.

**Conceptual caveats**
- Removing the agent also removes its action and motion. The split is really "agent with its action" versus "setting," and the write-up should say so.
- Composites can mismatch camera motion and lighting. Record camera-motion mismatch and a low-level-statistics difference as covariates.
- Optional third arm, to cover all three of the user's information levels: frames that keep colour and texture statistics but destroy objects. Precedents are Loke 2026 (texture-synthesized images) and Geirhos (style transfer). Video texture synthesis feasibility is UNVERIFIED.

=== 6. OUT-OF-DISTRIBUTION RISK AND MINIMAL CONTROLS ===
**Risk**
- Encoding models fit on about 2,180 natural videos, each shown once (Horikawa 2020), are extrapolating on edited videos.
- Vision evidence (INDIRECT): Madan et al., NeurIPS 2024, found simple image shifts can cut neural predictivity to as little as 20% of in-distribution levels. Gifford, Cichy, Naselaris & Kay (synthetic-image companion set to the Natural Scenes Dataset) found lower accuracy out of distribution.
- Therefore call brain-side results in-silico predictions. Preregister validation with human ratings now and fMRI later, following the logic of Ratan Murty 2021 and Gu 2023.

**Minimal control set** (each tied to a precedent)

| Code | Condition | What it controls or measures | Precedent |
|---|---|---|---|
| C0 | Original passed through the identical decode/resize/re-encode pipeline | Pipeline floor | — |
| C1 | Sham removal: inpaint a non-figure region with the same mask shape and area (mask borrowed from another video, placed so it does not overlap the figure) | Inpainting artifacts alone | User's suggestion; no direct precedent found. HAT plots accuracy against synthetic-pixel percentage |
| C2 | Self-recomposite: figure A pasted back onto A's own inpainted setting | Compositing artifacts: edge halos, lost shadows | Xiao's Mixed-Same, HAT's "same" pairs |
| C3 | Figure-only with neutral fill (dataset mean colour); optionally a second fill to check robustness | Figure alone | HAT Human Only, Xiao Only-FG |
| C4 | Setting-only: figure removed and inpainted | Setting alone | HAT Background Only, Xiao No-FG |
| C5 | Cross composites: figure A on setting B, with B sampled across the whole continuous range of profile distance d(A,B); no threshold, analysed as regression on d | The cue-conflict test itself | Mixed-Rand, Action Swap |

- Covariates: mask area, figure versus background motion energy, camera-motion mismatch, colour statistics.
- Out-of-distribution index per variant: distance of its lens-feature vector from the 2,180 originals (for example Mahalanobis distance in principal-component space). Report effects as a function of this index and restrict claims to the natural range.
- Preregistered human subset, for example about 300 composites: naturalness rating plus the same emotion scales. This gives the human figure-versus-setting weight for comparison.

**Analysis** (continuous only, consistent with the project rules)
- For each composite, fit p_C ≈ a·p_figure-only(A) + b·p_setting-only(B) with non-negative least squares, or use w = d(p_C,p_B) / (d(p_C,p_A) + d(p_C,p_B)). The figure weight is w = a/(a+b). This replaces Geirhos's top-1 shape bias.
- Fit per output dimension: which of the 27 emotion dimensions follow the figure and which follow the setting. No stimulus grouping is involved.
- Run the same index on each region's encoding-model predictions to get a cortical figure-weight map: early visual → body/face/object-selective lateral occipital → scene-selective areas → superior temporal → temporoparietal junction → medial prefrontal. This connects directly to H3 (the transmodal question).
- Link model and brain: across composites, does each region's figure weight track the lens model's figure weight?

=== 7. PLAIN-LANGUAGE NAME AND PLACE IN THE STORY (no acronyms) ===
- Suggested name: "figure–setting swap test" (Korean: 주인공·배경 맞바꾸기 실험).
- Act 1 addition: lift the agent out of one video and set it into another video's setting, then see which emotions in the frozen emotion model follow the agent and which follow the setting.
- Act 2 addition: run the same swapped videos through each brain region's encoding model and map, across cortex, whether a region "goes with the agent" or "goes with the setting."
- Act 4: preregister human ratings of a small swap set, and later an fMRI test.

=== KEY FILE PATHS ===
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_hat/HAT/README.md
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_hat/HAT/doc/review_discussion.md
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_hat/HAT/mmaction2/mmaction/datasets/actionswap_dataset.py
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_bgchal/backgrounds_challenge/README.md
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_geirhos/texture-vs-shape/README.md
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_sam3/sam3/README.md and LICENSE
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_sam2/sam2/README.md
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_propainter/ProPainter/README.md and LICENSE
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_diffueraser/DiffuEraser/README.md
- Caption file used for the content estimate (read-only): /home/user/EmoBrain/project/shared/data/caption_ck20.csv

Web sources (search snippets only):
- [ICLR 2021 Xiao](https://iclr.cc/virtual/2021/poster/2857)
- [ICLR 2019 Geirhos](https://iclr.cc/virtual/2019/oral/1165)
- [HAT NeurIPS 2022](https://neurips.cc/virtual/2022/poster/55773)
- [CCIM](https://openaccess.thecvf.com/content/CVPR2023/html/Yang_Context_De-Confounded_Emotion_Recognition_CVPR_2023_paper.html)
- [CLEF](https://openaccess.thecvf.com/content/CVPR2024/html/Yang_Robust_Emotion_Recognition_in_Context_Debiasing_CVPR_2024_paper.html)
- [CAER-Net](https://openaccess.thecvf.com/content_ICCV_2019/html/Lee_Context-Aware_Emotion_Recognition_Networks_ICCV_2019_paper.html)
- [Fan 2017 PDF](https://www-users.cse.umn.edu/~qzhao/publications/pdf/sentiment_acmmm17.pdf)
- [EmoEdit](https://openaccess.thecvf.com/content/CVPR2025/papers/Yang_EmoEdit_Evoking_Emotions_through_Image_Manipulation_CVPR_2025_paper.pdf)
- [VEATIC](https://openaccess.thecvf.com/content/WACV2024/html/Ren_VEATIC_Video-Based_Emotion_and_Affect_Tracking_in_Context_Dataset_WACV_2024_paper.html)
- [Brain Dissection](https://proceedings.neurips.cc/paper_files/paper/2023/hash/90e06fe49254204248cb12562528b952-Abstract.html)
- [BrainSAIL](https://iclr.cc/virtual/2025/poster/27735)
- [MacaqueITBench](https://cbmm.mit.edu/publications/benchmarking-out-distribution-generalization-capabilities-dnn-based-encoding-models)
- [Static bias, ICCV 2023](https://arxiv.org/pdf/2211.12883)

##### dissection
REPORT: Network Dissection (labelling each unit with a concept) brought into emotion research. Covers citation checks, prior work, code, feasibility and pitfalls.

## 0. Bottom line
- Labelling the units of an emotion-trained network with concepts is not new in general. It has been done at least 4 times, all on facial-expression networks with facial action units as the concepts (section 2, group A).
- Not found in about 31 prior-work searches (listed in section 3):
  (a) dissection of a model trained on emotion from scenes or situations (non-face) or from video;
  (b) a concept hierarchy (color, texture, material, part, object, scene) linked to a continuous emotion profile and to brain regions;
  (c) an emotion-objective model compared with an action-objective model from the same starting weights;
  (d) brain-region dissection ("Brain Dissection") applied to stimuli that evoke emotion, or to transmodal cortex.
- The novelty claim must therefore be narrow: the three-way link (concept level x emotion profile x brain region) plus the matched-twin comparison. "We label units with concepts" alone is not novel.
- Feasibility is good, with 4 required code changes (section 4). The project rule allows it if emotion links stay continuous (section 5).
- It also fits the project thesis without a competition frame. If the emotion model's units turn out to be mostly object and scene detectors, that directly says emotion structure rides on visual-semantic content.

## 1. Citation verification
VERIFIED means the source was read: repository README or code, or a PubMed record or full text.

- **Network Dissection** — Bau, Zhou, Khosla, Oliva, Torralba, CVPR 2017. VERIFIED from the citation blocks in the NetDissect and NetDissect-Lite READMEs.
  - The probe dataset Broden merges ADE20K, PASCAL, PASCAL-Part, PASCAL-Context, OpenSurfaces and DTD. VERIFIED (README).
  - The six concept categories are object, part, scene, material, texture, color. VERIFIED (NetDissect-Lite settings.py).
  - Thresholds: activation quantile 0.005 and IoU 0.04 for "interpretable". VERIFIED in code (settings.py; the Hierarchical Network Dissection README states the same rule).
  - The CVPR page and arXiv were blocked by the proxy, so page numbers were not checked.
- **Journal extension** — Zhou, Bau, Oliva, Torralba, IEEE TPAMI 2019;41(9):2131-45, doi 10.1109/TPAMI.2018.2858759. VERIFIED (PubMed abstract).
  - Key sentence: deep representations are "more interpretable than they would be under a random equivalently powerful basis". This is the rotation control.
  - The NetDissect code has a random-rotation option (rotation_seed, rotation_power in src/netprobe.py). VERIFIED.
- **Bau et al. 2020 PNAS** — the author list is Bau, Zhu, Strobelt, Lapedriza, Zhou, Torralba (not the CVPR list). PNAS 117(48):30071-8, doi 10.1073/pnas.1907375117. VERIFIED (PubMed).
  - Uses a segmentation network instead of hand labels: UnifiedParsingSegmenter gives object, part and material classes. VERIFIED (davidbau/dissect netdissect/segmenter.py).
  - Unit-ablation results: removing about 20 units destroys one class. VERIFIED (README).
- **CLIP-Dissect** — Oikarinen & Weng, ICLR 2023. The correct organization is Trustworthy-ML-Lab/CLIP-dissect. VERIFIED (README).
- **MILAN** — Hernandez, Schwettmann, Bau, Bagashvili, Torralba, Andreas, "Natural Language Descriptions of Deep Visual Features", ICLR 2022 oral. VERIFIED (README of evandez/neuron-descriptions).
- **BrainSCUBA** — Luo, Henderson, Tarr, Wehbe, ICLR 2024. Repository: aluo-x/BrainSCUBA. VERIFIED (README).
  - It is a linear CLIP ViT-B/32 to voxel encoder; weights are projected onto natural-image embeddings and then captioned with CLIPCap. The README abstract says "pre-trained large language model".
- **Brain analogue for concept selectivity**
  - Sarch, Tarr, Fragkiadaki, Wehbe, "Brain Dissection: fMRI-trained Networks Reveal Spatial Selectivity in the Processing of Natural Images". VERIFIED from the repository Gabesarch/brain-dissection; its README bibtex says bioRxiv 2023. The NeurIPS 2023 venue is INDIRECT (search results).
    - Method: trains networks optimized to predict region responses on the Natural Scenes Dataset (NSD), then dissects them on Places365 for depth, surface normals and curvature, and on GQA for objects and relations.
  - Huth, Nishimoto, Vu, Gallant 2012 Neuron 76:1210, doi 10.1016/j.neuron.2012.10.014. VERIFIED (PubMed).
  - Koide-Majima, Nakai, Nishimoto 2020 NeuroImage 222:117258, doi 10.1016/j.neuroimage.2020.117258. VERIFIED (PubMed). It maps 80 emotions onto cortex, running from unimodal to transmodal regions.
- **Video concept discovery** — Kowal et al., "Understanding Video Transformers via Universal Concept Discovery", CVPR 2024. VERIFIED (README of YorkUCVIL/VTCD). It runs on VideoMAE directly.

## 2. Prior work in emotion research, closest first

### A. Units of emotion or expression networks labelled with concepts (all faces)
1. **Teotia, Lapedriza, Ostadabbas, IJCV 2022**, "Interpreting Face Inference Models using Hierarchical Network Dissection". VERIFIED (repository ostadabbas/Hierarchical-Network-Dissection).
   - Dissects face models including a ResNet-50 smile vs non-smile classifier (loader/model_loader_smile.py).
   - Uses a "Face Dictionary" of parts, action units and attributes, with the same 0.005 quantile and 0.04 IoU rule.
2. **Inagaki, Ito, Shinozaki, Fujita 2022**, Front Psychol 13:988302, doi 10.3389/fpsyg.2022.988302. VERIFIED (PubMed abstract).
   - Measures how selective CNN units trained on expression databases are for facial action units, compared across cultures.
3. **Khorrami, Paine, Huang**, ICCV Workshops 2015. INDIRECT (search results).
   - Filters of an expression network matched facial action units.
4. **Cha, Choi, Lo, Luu 2024**, student capstone project mentored by Lily Weng, "Enhancing Emotion Recognition in AI: A CLIP-Dissect Approach" (github lacygus/Emotion_Recognition). VERIFIED (repository read). Not peer reviewed.
   - Applied CLIP-Dissect to a FER2013 VGG with a facial-expression concept set generated by GPT-4.

### B. Emotion-selective units without concept labels
5. **Liu, Bo, Ding, Fang 2024**, PLoS Comput Biol 20:e1011943, doi 10.1371/journal.pcbi.1011943. VERIFIED (full text). Note that "Fang" is Ruogu Fang.
   - Uses an ImageNet-trained VGG-16, not an emotion-trained model.
   - Images were sorted into pleasant, neutral and unpleasant by thresholds: this is exactly what the project rule forbids.
   - Selectivity index, lesion and gain experiments. No concept labels; only a "preliminary" two-way analysis of variance on object categories in the supplement.
6. **Zhou, Yang, Meng, Zhou 2022**, Sci Adv, doi 10.1126/sciadv.abj4383. VERIFIED (PubMed). Expression-selective units in VGG-Face.
7. **"Biologically Inspired Deep Neural Network Models for Visual Emotion Processing"**, bioRxiv 10.1101/2025.10.20.683439. INDIRECT. Emotion-selective units in a CLIP vision transformer with an amygdala module.
8. **Goh et al. 2021 Distill**, "Multimodal Neurons". INDIRECT. Emotion neurons in CLIP.

### C. Feature or concept links at the output level of models of emotional scenes (not hidden units)
9. **Kragel, Reddan, LaBar, Wager 2019**, Sci Adv 5:eaaw4358, doi 10.1126/sciadv.aaw4358. VERIFIED (full text).
   - Correlated the 20-dimensional fc8 output with color histograms, spatial power spectra, face counts and AlexNet object classes. These "largely failed" to discriminate on held-out data.
   - Only fc8 was retrained, so EmoNet's conv1 to fc7 layers are plain AlexNet. Dissecting EmoNet's hidden layers would simply reproduce Bau 2017's AlexNet result.
10. **Gao, Ajith, Peelen 2025**, Commun Biol 8:697, doi 10.1038/s42003-025-08145-1. VERIFIED (full text).
    - Weight matrix of AlexNet fc8 object labels x emotions, and representational similarity within vs between object clusters. They state the same AlexNet identity of EmoNet's lower layers.
11. **Jang & Kragel 2025**, J Neurosci 45(18), doi 10.1523/JNEUROSCI.1436-24.2025. VERIFIED (full text).
    - Amygdala encoding models built on EmoNet fc7, with image synthesis.
    - Low-level checks only: color, spatial frequency. No unit concepts.
12. **Newer from the same group (not in the given context)**
    - Soderberg, Jang, Kragel 2026 SCAN, doi 10.1093/scan/nsag028. VERIFIED (PubMed).
    - Jang, Riels, Aberman, Tao, Kragel, bioRxiv Oct 2026, "A representation of the visual environment in the human basolateral amygdala supports learning and choice", doi 10.64898/2026.10.07.757347. VERIFIED (PubMed abstract). Neither does concept labelling.
13. **Other related work, all INDIRECT**
    - EmoCAM (Doulfoukar, Mertens, Vennekens 2024, arXiv 2407.14314): heat maps plus object detection on EmoNet.
    - Asokan et al. 2022 (arXiv 2202.01072): concept activation vectors for multimodal emotion recognition, on a bidirectional contextual LSTM with IEMOCAP.
    - EmoSet (Yang et al., ICCV 2023): about 118k images labelled by humans with 6 attributes (brightness, colorfulness, scene, object, facial expression, action). Usable as an emotion-relevant concept dictionary, but labels are per image, not per pixel.
    - EmoMind (arXiv 2605.16739, 2026): decodes 34-category emotion-styled captions from fMRI. Not dissection.

## 3. Searches run, and the novelty verdict

**PubMed:**
- "network dissection emotion" (106 hits, all fields; dominated by gene and anatomy uses of the phrase, so the next query is the stricter screen)
- "network dissection"[Title/Abstract] (18 hits, none about emotion)
- emotion selective units deep neural network (3)
- PLoS Comput Biol emotion deep or convolutional network 2024 (1)
- convolutional network AND facial expression AND units/neurons AND selective (4)
- emotion AND network AND units/neurons AND selectivity AND images/videos (16)
- interpretability AND emotion AND units AND concept (0)
- dissection/concept labelling AND EmoNet/affective image (0)
- CLIP emotion neurons (6, irrelevant)
- plus searches targeted at specific authors

**Web search:**
- network dissection emotion recognition
- "CLIP-Dissect" with emotion, affect, sentiment or facial expression
- "network dissection" "facial expression recognition"
- "network dissection" with visual sentiment or image emotion
- Goh multimodal neurons emotion
- Khorrami action units
- concept activation vectors and emotion
- interpretable neurons, emotion, concept labelling 2024-25
- network dissection video 3D CNN
- EmoNet units interpretability
- voxel-wise concept selectivity, emotion, fMRI
- VideoMAE neuron descriptions
- emotion-selective neurons in vision transformers or CLIP, 2025-26
- MILAN or neuron descriptions with affect
- Cowen-Keltner videos, deep network units
- dissection with aesthetics, valence or memorability
- dissecting an emotion video model with brain encoding

**GitHub:**
- "hierarchical network dissection" (1 result)
- "network dissection emotion" (0)
- "netdissect video" (0)
- "dissect emotion units" (0)

**Verdict.** In about 31 searches, nothing was found that:
- dissects a non-face emotion model or a video emotion model;
- links concept-labelled units to a continuous 27-emotion profile and to brain regions;
- compares an emotion twin with an action twin;
- applies Brain Dissection to emotional stimuli.

Concept labelling of emotion-network units exists for faces (2015, 2022, 2022, 2024). Say "not found in 31 searches", never "never done". Coverage gaps: arXiv, OpenReview, CVF, Semantic Scholar and OpenAlex were all blocked by the proxy.

## 4. Code and data feasibility (repositories cloned and read)

**NetDissect-Lite** (CSAILVision; last commit 2019; PyTorch)
- The hook expects 4-dimensional convolution maps.
- VideoMAE ViT-B gives (batch, 1568, channels) tokens = 8 time steps x 14x14 patches with a 2-frame tubelet. VERIFIED in modeling_finetune.py.
- A wrapper must reshape to (batch, channels, 8, 14, 14) and average over time, or keep time.
- Broden download: http://netdissect.csail.mit.edu/data/broden1_224.zip. Blocked from this sandbox, so availability is UNVERIFIED.
  - Fallback: script/makebroden.sh in the NetDissect repository rebuilds it from the component datasets.
  - A possible Hugging Face mirror (ToBeGrad/data_224) is unconfirmed.

**dissect (Bau 2020)**
- Dissects with segmenter predictions, so the Cowen video frames can serve as the in-distribution probe set.
- Covers object, part and material only. Color would come from NetDissect src/colorname.py, and scene from a scene classifier.

**CLIP-Dissect**
- Needs no masks; accepts a custom probe set and concept list.
- Bug for this model: for 3-dimensional outputs the hook takes output[:,0], the class token. VideoMAE has no class token: it uses fc_norm(x.mean(1)) (VERIFIED). Taken as-is, it would silently read only the first patch. Replace with the mean or max over tokens.
- The shipped data/broden_labels_clean.txt (1,196 concepts) has no category tags. A concept-to-category map is needed.
- data/categories_places365.txt is included for scene concepts.

**Video concept discovery (VTCD)**
- Native VideoMAE support, plus "find_rosetta_concepts.py" for concepts shared across models.
- The only found route to temporal or motion concepts. It discovers concepts rather than labelling them against a fixed dictionary.

**Static frames into VideoMAE**
- Possible by repeating one frame 16 times, but this is out of distribution (no motion).
- Broden has no motion concepts, so the "low-level motion" level cannot be dissected with Broden.
- An optical-flow-derived motion concept would be new; no toolkit for it was found.
- Recommendation: dissect on real clips, using segmenter masks per frame.

**Matched twin is available** (VERIFIED)
- The emodiversity fine-tuning on the 61k emotion videos starts from the VideoMAE "Kinetics-400 ViT-B epoch-1600 pretrain" checkpoint, Google Drive file id 1tEhLy..., the same file listed in the MCG-NJU model zoo.
- That emotion fine-tuning uses BCEWithLogitsLoss over 27 intensities, full fine-tuning, layer decay 0.75 (fork JunShern/VideoMAE, scripts/emodiversity/finetune_vce.sh).
- The model zoo also publishes the Kinetics-400 supervised fine-tune of the same 1600-epoch pretrain.
- Result: emotion, action and pretrain-only models from identical starting weights. This mirrors Bau 2017's comparison of training objectives and fine-tuning (INDIRECT: from search results and the TPAMI abstract).

**Scale**
- 12 blocks x 3,072 MLP neurons = 36,864 units. The compute estimate is unverified.

## 5. Pitfalls and fit with the project rules

1. **Basis and polysemantic units.** The transformer's residual-stream dimensions are not a privileged basis (this is reasoning, not from a source read). Dissect the MLP neurons after GELU (blocks[i].mlp.act). Always run the random-rotation null (supported in the code; justified by the TPAMI abstract) and a randomly initialized twin.
2. **Probe-set and dictionary dependence.** Räz 2023 Patterns (doi 10.1016/j.patter.2023.100761, VERIFIED abstract) argues that concepts defined by sets of instances are underdetermined. Run on two probe sets (Broden and the Cowen frames) and report how well they agree. Counts of units per category are biased by dictionary size, so normalize against the nulls.
3. **Top-1 labels and the 0.04 threshold.** These categorize units and pixels, not stimuli, so they comply with the letter of the rule. Report the continuous intersection-over-union profile across the six levels for every unit as well as top-1.
4. **Linking units to emotions.**
   - Never use Liu 2024's binning of images into three valence classes.
   - Never assign each unit an argmax emotion.
   - Use a continuous 27-dimensional profile per unit: the change in the predicted profile after ablation (Bau 2020-style ablation, measured as profile distance rather than accuracy), or head weight x activation.
   - Then compare emotion structures by distance or representational similarity.
5. **Linking units to brain regions.**
   - Weights of single units in encoding models are not identifiable.
   - Option 1: group units by concept level into feature bands, then use banded regression with variance partitioning per region.
   - Option 2: Brain Dissection: train predictors of each region's response from frozen model features and dissect the predictor with the same dictionary. This gives a common concept currency for model units and brain regions.
   - The Horikawa 2020 data have one presentation per video and 5 people, so prefer region-level over voxel-level analysis.
6. **Avoid open-vocabulary or large-language-model labellers.**
   - BrainSCUBA (CLIPCap) and MILAN-style generative captions carry two problems: an LLM in the pipeline, and the open-vocabulary framing CLAUDE.md marks as abandoned.
   - Use a closed dictionary (Broden or a fixed list). CLIP-Dissect needs CLIP, which is not a large language model; disclose it as an annotation tool.
   - Do not generate concept sets with GPT-4, as the student project did.
7. **Do not dissect EmoNet as a contribution.** Its hidden layers are AlexNet (Kragel 2019 and Gao 2025, both VERIFIED).

## 6. Local paths (all clones under scratchpad, nothing under /home/user changed)
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_netdissect_lite/repo
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_netdissect/repo
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_dissect/repo
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_clipdissect/repo
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_milan/repo
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_brainscuba/repo
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_braindissect/repo
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_hnd/repo
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_vtcd/repo
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_emodiv/repo
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_videomae/repo
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_videomae_fork/repo
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_lacygus/repo
- Extracted full texts: /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/kragel2019.txt and /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/gao2025.txt

Hosts blocked here, to allow if needed: arxiv.org, openaccess.thecvf.com, proceedings.neurips.cc, netdissect.csail.mit.edu, www.cs.cmu.edu, papers.baulab.info, api.semanticscholar.org, api.openalex.org, huggingface.co.

Sources: PubMed records cited by DOI above.

Web search results relied on (INDIRECT):
- https://distill.pub/2021/multimodal-neurons/
- https://openaccess.thecvf.com/content_iccv_2015_workshops/w2/html/Khorrami_Do_Deep_Neural_ICCV_2015_paper.html
- https://link.springer.com/article/10.1007/s11263-022-01603-x
- https://proceedings.neurips.cc/paper_files/paper/2023/hash/90e06fe49254204248cb12562528b952-Abstract-Conference.html
- https://arxiv.org/abs/2202.01072
- https://arxiv.org/abs/2307.07961
- https://arxiv.org/abs/2407.14314
- https://www.biorxiv.org/content/10.1101/2025.10.20.683439v1.full
- https://arxiv.org/pdf/2605.16739
- https://lacygus.github.io/Emotion_Recognition/
- https://yorkucvil.github.io/VTCD/

##### bottleneck
CONCEPT BOTTLENECK (from vision interpretability) as the project's new method: research report

Evidence tags: VERIFIED means I read the source (a cloned repository, a PubMed abstract or full text, or a project file). INDIRECT means I saw it only in a search snippet. UNVERIFIED means I could not confirm it.
Access limits: arxiv.org and proceedings.mlr.press do not resolve from this session, so I could not fetch any paper pages. The GitHub API also refused requests. Cloning repositories with git worked, and PubMed worked.

====================================================================
1. BOTTOM LINE
====================================================================
- **Stimulus half: not new.** The chain "video → named concepts → sparse linear layer → emotions" has been done in affective computing for over ten years under other names (section 3a). It is a usable component, but it cannot be the paper's new claim.
- **Brain half: not found in 14 targeted searches.** The chain is "each brain region → decoded concept activations → the same frozen concept-to-emotion layer that was trained on stimuli." The closest prior work does brain → named concepts, but the target is words or images, never emotion (section 3b).
- **What vision brings that emotion research lacks, in 9 searches on concept bottlenecks for emotion:**
  - *Concept intervention* (Koh 2020): set one concept to its true value or to zero, then pass the change forward to the emotion output.
  - *Concept-route versus residual-route decomposition* (Post-hoc concept bottleneck "hybrid", Yuksekgonul 2023; the leakage side channel, Havasi 2022).
  
  These two pieces are what make the method novel. A plain table of region × concept × emotion is not novel.
- **Built-in risk.** The head is frozen and trained on stimuli. So every emotion label in the brain result comes from that stimulus-trained head, and the brain only decides which concepts can be decoded where. Without the residual test and the intervention test, a reviewer can fairly say this is a concept-decoding map relabelled through a lookup table (section 5).
- **"Existing model, small adjustment": yes.** Every part is a frozen published classifier, an existing elastic-net solver with permissive licenses, or a ridge decoder (section 4).

====================================================================
2. CITATION CHECK
====================================================================
- **Koh, Nguyen, Tang, Mussmann, Pierson, Kim, Liang. "Concept Bottleneck Models." ICML 2020.**
  - VERIFIED from the repository README and LICENSE.
  - Volume and pages, PMLR 119:5338–5348: INDIRECT.
  - The code implements three training modes: Independent, Sequential and Joint (CUB/README).
  - License: MIT (copyright 2021, the authors).
- **Oikarinen, Das, Nguyen (Lam M.), Weng. "Label-free Concept Bottleneck Models." ICLR 2023.**
  - VERIFIED from the BibTeX in the repository README; the repository is under the Trustworthy-ML-Lab organisation.
  - The code (VERIFIED) has three steps:
    - Concept lists come from GPT-3 (GPT_initial_concepts.ipynb calls openai), with a ConceptNet alternative.
    - The concept layer is a linear projection trained to match CLIP image–text similarity, using a cubed-cosine similarity in similarity.py.
    - Concepts are then filtered, and the final layer is fitted with GLM-SAGA (glm_saga, an elastic-net solver).
- **Yang, Panagopoulou, Zhou, Jin, Callison-Burch, Yatskar. "Language in a Bottle: Language Model Guided Concept Bottlenecks for Interpretable Image Classification." CVPR 2023, pp. 19187–19197.**
  - VERIFIED from the README BibTeX.
  - The title says the concepts are language-model guided. The project's rule against a language model as backbone makes it a gray area, so do not use it.
- **Wong, Santurkar, Madry. "Leveraging Sparse Linear Layers for Debuggable Deep Networks."**
  - VERIFIED from the glm_saga README, which cites it as arXiv 2105.04857. The ICML 2021 venue is UNVERIFIED.
- **Yuksekgonul, Wang, Zou. "Post-hoc Concept Bottleneck Models." ICLR 2023.**
  - VERIFIED from the README BibTeX.
  - Code is at github.com/mertyg/post-hoc-cbm, MIT license.
  - Its final layer is SGDClassifier with an elastic-net penalty (train_pcbm.py).
- **Srivastava, Yan, Weng. "VLG-CBM: Training Concept Bottleneck Models with Vision-Language Guidance." NeurIPS 2024.**
  - VERIFIED from the README.
  - Its README results table has a "Random" concept row that matches or beats published concept bottlenecks when the number of effective concepts is held at 5. Example on CUB: Random 68.91% against Label-free 53.51%. This is a VERIFIED pitfall for section 5.
- **Mahinpei, Clark, Lage, Doshi-Velez, Pan. "Promises and Pitfalls of Black-Box Concept Learning Models."** arXiv 2106.13314, ICML 2021 workshop on explainable AI. INDIRECT.
  - Finding: learned concept representations carry information beyond the named concepts (leakage), and natural fixes only partly work.
- **Margeloiu, Ashman, Bhatt, Chen, Jamnik, Weller. "Do Concept Bottleneck Models Learn as Intended?"** arXiv 2105.04289, ICLR 2021 Workshop on Responsible AI. INDIRECT.
  - Finding: concepts do not map to meaningful input regions, and independent training may be the only mode that meets the stated goals.
- **Havasi, Parbhoo, Doshi-Velez. "Addressing Leakage in Concept Bottleneck Models." NeurIPS 2022.** INDIRECT.
  - Remedy: a side channel for latent concepts plus an autoregressive concept predictor.
- **Roth, Kim, Koepke, Vinyals, Schmid, Akata. "Waffling around for Performance." ICCV 2023.** INDIRECT.
  - Finding: random words do about as well as GPT-generated descriptors in CLIP classification.

====================================================================
3. PRIOR ART
====================================================================

3a. Named concepts → emotion or sentiment, on the stimulus side. The idea itself is old.
- **Borth, Ji, Chen, Breuel, Chang, "SentiBank", ACM Multimedia 2013.** INDIRECT. 1,200 adjective–noun-pair detectors serve as a middle-level layer for visual sentiment.
- **Yuan, Mcdonough, You, Luo, "Sentribute", WISDOM 2013.** INDIRECT. 102 scene attributes from the SUN dataset predict image sentiment, with interpretability as the stated motive. The same 102 attributes are produced by the Places365 code; labels_sunattribute.txt has 102 lines (VERIFIED).
- **Jiang, Xu, Xue, "Predicting Emotions in User-Generated Videos", AAAI 2014, pp. 73–79.** INDIRECT. Semantic attribute features drive video emotion over 8 categories.
- **Xu, Fu, Jiang, Li, Sigal, "Heterogeneous Knowledge Transfer in Video Emotion Recognition, Attribution and Summarization", IEEE Transactions on Affective Computing.** INDIRECT. Auxiliary image concepts are used, and a task of "emotion attribution" is defined.
- **Chowdhury, Vall, Haunschmid, Widmer, "Towards Explainable Music Emotion Recognition: The Route via Mid-level Features", ISMIR 2019, pp. 237–243.** INDIRECT.
  - Music emotion is predicted through human-interpretable middle-level perceptual features, which is a concept bottleneck in all but name.
  - The authors report the cost of routing through these features is small. The exact number of features is UNVERIFIED.
- **Zhang & Hain, "From Speech to Editable Concepts: Probing Emotion Recognition with Concept Bottleneck Models", arXiv 2609.39453 (2026).** INDIRECT.
  - Concepts are transcript, acoustic, and speaker age and gender. Search snippets disagree on whether a language model is the predictor.
- **AU-GRACE (MDPI Computers 2026, 15(11):750).** INDIRECT. Facial expression is predicted through an explicit bottleneck of facial action units.
- **Sheep facial pain, arXiv 2609.20427.** INDIRECT. A concept bottleneck with a linear output layer.
- **PANDIA (PLOS Digital Health 2026).** VERIFIED from the PubMed abstract, https://doi.org/10.1371/journal.pdig.0001442. Neonatal pain assessment with symbolic concept-bottleneck explanations.
- **Concept activation vectors for multimodal emotion, arXiv 2202.01072.** INDIRECT. This is a post-hoc probe, not a bottleneck.
- **"VISTA" appraisal bottleneck, arXiv 2609.37324.** UNVERIFIED. One snippet described it; a search on the exact title found nothing.
- **Gao 2025** (from the caller's context, not checked by me; 1 search did not find it). ImageNet class outputs mapped linearly to emotion, then reporting the top-weighted labels, is structurally the stimulus half of a concept bottleneck.

**Not found:** a concept bottleneck that regresses continuous 27-emotion viewer profiles from video.

3b. Brain → named concepts → something else
- **Palatucci, Pomerleau, Hinton, Mitchell, "Zero-shot Learning with Semantic Output Codes", NIPS 2009, pp. 1410–1418.** INDIRECT. fMRI is decoded into semantic features and then into words never seen in training.
- **Horikawa & Kamitani, Nature Communications 2017, 8:15037.** VERIFIED from the abstract, https://doi.org/10.1038/ncomms15037. Deep-network features are decoded from fMRI and then used to identify object categories.
- **Cammarota, Ferrante, Toschi, "Bridging Brains and Concepts: Interpretable Visual Decoding from fMRI with Semantic Bottlenecks", NeurIPS 2025.** VERIFIED from the cloned README. This is the closest prior work:
  - The pipeline is fMRI → 214 binary questions → CLIP → Versatile Diffusion image reconstruction, on the Natural Scenes Dataset.
  - The questions were generated by GPT-4 from captions and answered by BLIP-2.
  - The voxel-to-question matrix gives voxel-level concept maps. The target is the image, not emotion. The repository has no license file.
- **Skerry & Saxe, Current Biology 2015, 25:1945–54.** VERIFIED from the abstract, https://doi.org/10.1016/j.cub.2015.06.009. A space of abstract event and appraisal features fits the neural similarity of emotions in mentalizing regions. This is a comparison of similarity structures, not a bottleneck decoder.
- **Horikawa, Cowen, Keltner, Kamitani, iScience 2020.** VERIFIED from the full text, https://doi.org/10.1016/j.isci.2020.101060.
  - They used crowdsourced semantic concept labels ("cats, indoor, sports") and VGG object outputs only as competing encoding covariates. They did not decode through concepts.
  - Project notes record 73 such concepts (docs/notes/methods_spec_2026-11-25/review/v1_verification_facts.md, around line 393). Du et al. 2023 also used them.
  - **So human-labelled concepts already exist for every Cowen video**, which allows a supervised bottleneck in the style of Koh 2020 with no language model.
- **Kragel 2019** (caller's context). fMRI is decoded into EmoNet outputs, with no named-concept layer in between.
- **EmoMind (Mohammed, Gu, Fang, arXiv 2605.16739, 2026).** INDIRECT. fMRI is decoded into a neutral scene description plus a 34-dimension Cowen–Keltner emotion vector, which then become an affective caption; it uses Emo-FilM. It is not a concept bottleneck, but it overlaps with our data and taxonomy, so it should be cited.
- **Sparse concept-atom encoding model, bioRxiv 2025 (10.64898/2025.11.29.691321).** INDIRECT. An encoding model, not a decoder through a bottleneck.

**Not found in 14 searches:** brain region → decoded concepts → frozen concept-to-emotion layer trained on stimuli. Also not found: concept intervention or concept/residual decomposition applied to emotion in the brain.

Searches run:
- **PubMed (all 0 relevant unless noted):**
  - "concept bottleneck": 28 hits, all medical imaging, activity recognition or pain; no emotion from stimuli, no brain decoding.
  - (concept bottleneck OR concept-based interpretable) AND (emotion OR affective OR facial expression): 9 hits, none relevant.
  - (semantic OR concept bottleneck) AND (fMRI OR EEG OR neural decoding): 73 hits; I inspected the first 20 titles and none were relevant.
  - fMRI emotion decoding semantic features zero-shot: 0.
  - emotion fMRI decoding interpretable concepts objects scenes video: 0.
  - (fMRI OR neural) decoding attribute/semantic feature emotion movie/video/film: 0.
  - (interpretable OR explainable) brain/fMRI decoding concept semantic (deep learning OR CLIP), 2022 onward: 3 hits, none relevant.
  - concept bottleneck/mid-level attributes AND emotion/sentiment AND image/video/music: 3 hits, none relevant.
- **Web search, about 32 queries,** covering concept bottleneck with: facial expression, action units, image or visual emotion, video emotion or sentiment, speech/text/multimodal emotion, art emotion or ArtEmis, EEG or brain signals, fMRI decoding, encoding models of visual cortex, emotion with fMRI 2025–26, a frozen readout for brain emotion; plus specific title checks for every paper above.

====================================================================
4. CODE, LICENSES, AND WHETHER THIS IS "EXISTING MODEL, SMALL ADJUSTMENT"
====================================================================
Cloned into /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_cbm_*/. All licenses are VERIFIED from the clone unless marked otherwise.
- **yewsiang/ConceptBottleneck:** MIT.
- **MadryLab/glm_saga:** MIT, installable with pip. It supports family='gaussian', which is 0.5·squared error plus elastic net, so it works with **continuous multi-output targets** (README and elasticnet.py).
  - `group=True` gives group lasso, where one concept is switched on or off for all 27 emotions together. `group=False` lets each emotion pick its own concepts.
  - Inputs must be standardised.
- **mertyg/post-hoc-cbm:** MIT. Its final layer is a classifier, so continuous profiles need a swap to a regressor or to glm_saga. This is a small change.
- **No license file (default: all rights reserved):** Trustworthy-ML-Lab/Label-free-CBM, YueYANG1996/LaBo, Trustworthy-ML-Lab/VLG-CBM, SaraCammarota/Bridging-Brains-and-Concepts. Read and cite them; do not copy their code.
- **Concept sources from existing classifiers:**
  - CSAILVision/places365 (MIT): 365 scenes, 102 SUN attributes, and indoor/outdoor.
  - MCG-NJU/VideoMAE (CC BY-NC 4.0): Kinetics-400 fine-tuned ViT-B checkpoints are in MODEL_ZOO.md, and there is also a Something-Something V2 section. These are the same backbone family as the emotion lens.
  - ImageNet-21k classifiers: license UNVERIFIED.
- **Verdict: satisfies "existing model, small adjustment."** The adjustments are swapping in concept sources and using the regression family.
- **Avoid language-model-generated concept lists** (Label-free, LaBo, Cammarota). Use instead:
  - the 73 crowdsourced concepts;
  - words from the 20 human captions per video (share of captions that mention a word);
  - Kinetics, Places and ImageNet vocabularies;
  - named low-level descriptors (motion energy, luminance, saturation).
  
  Together these cover the user's three levels (low-level, object, situation) inside one model.
- **Caution on concept scores:** Kinetics and Places softmax probabilities collapse toward one-hot on confident clips, which in effect sorts stimuli into categories on the concept side. Prefer logits or multi-label sigmoids.

====================================================================
5. IS A SPARSE CONCEPT-TO-EMOTION LAYER SOUND? PITFALLS AND REQUIRED CONTROLS
====================================================================
- **Sound and standard.** An elastic-net or GLM-SAGA layer over concepts is the final layer in Label-free, Post-hoc and VLG concept bottlenecks.
- **Leakage** (Mahinpei 2021; Margeloiu 2021; Havasi 2022).
  - Train the head only on concept values from the stimuli (Koh's "independent" mode). Never fine-tune it on brain-decoded concepts or jointly with them.
- **Random-concept null** (VGL-style "Random" row, VERIFIED; Roth 2023).
  - Run equal-size random concept sets, or concept sets with shuffled names, through the same pipeline.
  - Fix the number of effective concepts per emotion, as VLG-CBM does.
  - Report concept-level claims only where named concepts beat this null.
- **Composition is still linear.**
  - Ridge from voxels to concepts, followed by a linear head, is a rank-limited linear decoder from brain to emotion.
  - In the region × concept × emotion table, the emotion part is inherited from the stimulus head. The brain contributes only how well each concept can be decoded in each region.
  - Two tests make the brain result non-trivial:
    - **(a) Residual share per region.** Compare a direct decoder (brain → frozen lens outputs; never human ratings) with the concept-routed decoder, and plot the gap against vocabulary size: 73 human concepts, then plus Kinetics, then plus Places, then plus ImageNet. A residual that persists after vocabulary growth bears directly on the research question of whether emotion representation is "constructed from visual-semantic content or irreducible." This is a decomposition framing, which the project allows. Caveat: an incomplete vocabulary also inflates the residual, which is why the growth curve is required.
    - **(b) Intervention agreement.** In each region, replace a decoded concept with its true stimulus value, or with zero. Test whether the predicted 27-emotion profile moves in the same direction as the same intervention on the stimulus-side model, using continuous profile distances only.
- **Correlated concepts.** The elastic net picks arbitrarily among correlated concepts. Use bootstrap stability selection before naming any "top concept."
- **Unequal concept levels.** Vocabularies differ in size and classifier quality across levels, which confounds comparisons between levels. Equalise the number of effective concepts per level and use a separate random null for each level.
- **Domain shift.** The head is trained on the 61k social-media videos, and the classifiers on Kinetics and Places, but it is applied to the Cowen videos. Report how well the head's predictions transfer to the Cowen ratings before using it with brain data.
- **Noisy brain data.** The 2020 brain data has one presentation per video, so concept decoding will be weak for many concepts. The shrinkage this causes in the head's output must be modelled, not read as "no emotion information."
- **Alternative that keeps the lens central:** a post-hoc concept bottleneck on the frozen VideoMAE emotion lens.
  - Linear probes map lens embedding → concept activations → sparse head, plus a residual hybrid.
  - The share of the lens's emotion prediction that passes through named concepts at each level answers Act 1 with a single model.

Repository paths:
/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_cbm_koh/ConceptBottleneck
/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_cbm_lf/Label-free-CBM
/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_cbm_labo/LaBo
/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_cbm_glmsaga/glm_saga
/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_cbm_posthoc/post-hoc-cbm
/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_cbm_vlg/VLG-CBM
/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_cbm_bbc/Bridging-Brains-and-Concepts
/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_cbm_places/places365
/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_cbm_videomae/VideoMAE

Sources (PubMed-attributed items carry their DOI links above):
- https://proceedings.mlr.press/v119/koh20a.html
- https://arxiv.org/abs/2106.13314
- https://arxiv.org/abs/2105.04289
- https://proceedings.neurips.cc/paper_files/paper/2022/hash/944ecf65a46feb578a43abfd5cddd960-Abstract.html
- https://iclr.cc/virtual/2023/poster/11415
- https://zenodo.org/records/3527788
- https://www.ee.columbia.edu/ln/dvmm/publicationPage/Publi/MM13:sentibank_long.html
- https://www.sentic.net/wisdom2013luo.pdf
- https://ojs.aaai.org/index.php/AAAI/article/view/8724
- https://arxiv.org/abs/1511.04798
- https://arxiv.org/abs/2609.39453
- https://www.mdpi.com/2073-431X/15/11/750
- https://arxiv.org/pdf/2609.20427
- https://arxiv.org/pdf/2202.01072
- https://mlanthology.org/neurips/2025/cammarota2025neurips-bridging/
- https://openreview.net/forum?id=ONeBc93I9O
- https://papers.nips.cc/paper/3650-zero-shot-learning-with-semantic-output-codes
- https://arxiv.org/abs/2605.16739
- https://www.biorxiv.org/content/10.64898/2025.11.29.691321v2.full
- https://arxiv.org/abs/2306.07282

##### metamer_stitch
REPORT: Model metamers (A) and model stitching (B) as imported methods for the emotion project

Sources: PubMed records (attribution: "According to PubMed"), PubMed Central full texts, web search snippets, and GitHub repositories cloned into fresh directories. The proxy blocked arxiv.org, openreview, the NeurIPS proceedings hosts (papers.nips.cc, proceedings.neurips.cc, papers.neurips.cc) and openaccess.thecvf.com. I modified nothing under /home/user. I only read files there: docs/paper_logic_merged.md and docs/notes/methods_spec_2026-11-25/methods_spec_v2.md.

======================================================================
0. BOTTOM LINE
======================================================================
(A) Emotion metamers
- Synthesized metamers for an emotion model: not found in any of my searches (list in section 2). The method can run on our hardware, but checking whether people or brains treat the metamers as equivalent needs new data: a new human rating study. Neither the 5-person nor the 6-person brain data can test them. Verdict: NOVEL for the emotion domain, but it cannot be validated with the data we have.
- Natural metamers (pairs of real videos that the emotion lens maps to the same profile but whose content differs), tested region by region against brain pattern similarity. Verdict: PARTIALLY DONE. Our own hypothesis H2 already says the same thing. H2 in docs/paper_logic_merged.md line 78: "pairs with similar emotion profiles but different visual-semantic content -> brain patterns differ". Related prior work: emotion representations that hold across stimulus formats, defined by categories or valence (Peelen 2010; Skerry & Saxe 2014; Chikazoe 2014), and the "controversial natural pairs" logic (Golan et al. 2020, 2023). What is new:
  (i) "same emotion" is defined by the frozen model's invariance, not by human ratings;
  (ii) pairs can be matched at a specific model stage, for example pairs that differ only in directions the linear 768->27 head ignores;
  (iii) pairs can be split by which information level differs: low-level, object or situation.
  I found no study doing (i) to (iii).

(B) Brain stitching (map a region's response into a layer of a model, then run the rest of the model)
Verdict: DONE IN VISION, NOT FOUND IN EMOTION, PARTIALLY DONE overall.
- Sexton & Love 2022, Science Advances [VERIFIED, full text], did exactly this. They call it "direct interface", not "stitching". Setup: object-recognition network VGG-16; two human fMRI datasets in which each image was shown once (Generic Object Decoding, 1,200 training images; BOLD5000); macaque V4/IT recordings. They learned a linear map from brain to layer q, ran the remaining layers, and built a region x layer map.
- Their result: every region, V1 included, worked best when inserted into LATE layers. This is the main risk for our version.
- The last-layer variant is already done in emotion: Kragel 2019 decoded EmoNet's output layer (fc8) and every earlier layer from occipital cortex, as decodability only, without running the network forward. Our methods spec v2 also already contains the auxiliary "generic path": brain -> pooled 768 representation -> frozen head (methods_spec_v2.md line 222).
- What would be new: stitching into intermediate depths of an EMOTION video model, evaluated on its 27-dimensional emotion output, and compared with the depth profiles of stimulus features of each information level stitched the same way. Not found.
- Recommended framing: combine A and B into "invariance-aware brain stitching". Model-to-model papers motivate it: Smith et al. 2025 show that stitching can succeed even when two models carry different information; Athanasiadis et al. 2026 add an invariance check. I found no brain version (section 5).

======================================================================
1. CITATION CHECK
======================================================================
A1. Feather, Durango, Gonzalez, McDermott 2019. "Metamers of neural networks reveal divergence from human perceptual systems." NeurIPS 32 (2019).
- INDIRECT: authors and venue come from the GitHub README of jenellefeather/model_metamers, which links papers.nips.cc/paper/9198, plus search snippets from MIT DSpace and the neurips.cc virtual page. The proceedings host was blocked.
- Method (README + snippet): gradient descent on a noise input to match one network stage's responses to a natural image or speech signal. Humans recognize early-stage metamers; late-stage metamers are unrecognizable.

A2. Feather, Leclerc, Mądry, McDermott 2023. "Model metamers reveal divergent invariances between biological and artificial neural networks." Nat Neurosci 26(11):2017-2034.
- DOI https://doi.org/10.1038/s41593-023-01442-0, PMID 37845543, PMC10620097. VERIFIED from full text.
- Method facts read:
  - gradient descent on a noise input to minimize the normalized Euclidean distance to the natural signal's activations at one stage;
  - 24,000 steps per metamer; step size starts at 1 and halves every 3,000 iterations;
  - human recognition experiments; model-to-model recognition of each other's metamers;
  - metamer recognizability did not track brain benchmarks: Brain-Score for macaque V1/V2/V4/IT, and auditory-cortex fMRI on 165 natural sounds.
- Code: github.com/jenellefeather/model_metamers_pytorch (stated in the paper).

A0 (origin, PubMed). Freeman & Simoncelli 2011, "Metamers of the ventral stream", Nat Neurosci. DOI https://doi.org/10.1038/nn.2889. Title and journal VERIFIED from PubMed metadata only.

B1. Lenc & Vedaldi 2015, CVPR. "Understanding image representations by measuring their equivariance and equivalence."
- CVPR version: INDIRECT (search snippet: CVPR 2015, pages 991-999; the CVF host was blocked).
- Journal extension: IJCV 2019, DOI https://doi.org/10.1007/s11263-018-1098-y, PMC6510825. VERIFIED from full text.
- Method facts read:
  - stitching layers join the shallow layers of network A to the deep layers of network B ("Franken-CNNs");
  - the map E is learned on the task (classification) loss with the rest of the network fixed;
  - any pair of layers is tested, giving a matrix of results;
  - stitching works across depth offsets (E can "undo" layers), but stitching from input pixels failed (error above 94%).

B2. Bansal, Nakkiran, Barak 2021. "Revisiting Model Stitching to Compare Neural Representations." NeurIPS 34. arXiv 2106.07682.
- INDIRECT: search snippets only; all hosting pages were blocked.
- Snippet content: a trainable stitching layer joins the bottom of model A and the top of model B, both frozen; it reveals properties that similarity scores such as CKA miss.
- I found no official code in 2 searches.

Key prior for B: Sexton & Love 2022. "Reassessing hierarchical correspondences between brain and deep networks through direct interface." Sci Adv 8:eabm2219.
- DOI https://doi.org/10.1126/sciadv.abm2219, PMC9278854. VERIFIED from full text.
- Method:
  - g'_q(W·brain) = model output; W is a linear map fitted by minimizing squared error to layer-q activations (no bias);
  - alternative "end-to-end" variant: W trained by backpropagating the classification loss through the frozen network; qualitatively similar, lower accuracy (their fig. S4);
  - alternative variant mapping into the top 5,000 principal components of the layer; same pattern, lower accuracy (fig. S5);
  - control: pixel principal components inserted in place of brain data worked best at the EARLIEST layer (fig. S6);
  - perturbation analysis: later layers absorb added noise rather than amplify it (fig. S7).
- Data: "For both [fMRI] datasets, each image was presented once."
- Result: all regions best at later layers. They interpret this as long-range feedback.
- Code: not found (one search, no GitHub or OSF hit).

Other items checked:
- Horikawa et al. 2020 iScience. DOI https://doi.org/10.1016/j.isci.2020.101060. VERIFIED: 5 subjects, 2,181 unique videos, fMRI volumes over each presentation shifted 4 s and averaged, 6-fold cross-validation. The full text does not state "presented once"; that part is from the task context (UNVERIFIED).
- Horikawa 2025 Sci Adv "Mind captioning". DOI https://doi.org/10.1126/sciadv.adw1464. VERIFIED: "In the training session, 2180 unique videos were each presented once"; 72 test videos (from the last two training runs) shown 5 times; a recall-imagery session. Whether we can access that training data: UNVERIFIED.
- Kragel et al. 2019 Sci Adv. DOI https://doi.org/10.1126/sciadv.aaw4358. VERIFIED: partial least squares regression predicted EmoNet's 20 output units (fc8) from occipital fMRI. Decoding fc8 was more accurate than decoding conv1-5, fc6 and fc7 (their fig. S6). No forward run through the network.
- Golan, Raju, Kriegeskorte 2020 PNAS "Controversial stimuli". DOI https://doi.org/10.1073/pnas.1912334117. Abstract VERIFIED.
- Golan, Schütt, Kriegeskorte 2026, Nat Rev Neurosci review "Making models disagree to learn how brains compute". DOI https://doi.org/10.1038/s41583-026-01070-0. This is a review (a secondary source), so it is a pointer only and should not be used to describe methods.
- Golan, Siegelman, Kriegeskorte, Baldassano 2023, Nat Mach Intell 5:952-964: controversial sentence pairs, either selected from a natural corpus or synthesized. INDIRECT (snippet).
- Jang & Kragel 2025 J Neurosci. DOI https://doi.org/10.1523/JNEUROSCI.1436-24.2025. Abstract VERIFIED: image synthesis to drive amygdala encoding models. This maximizes predicted responses; it is not metamer matching.
- Jang, Riels, Aberman, Tao, Kragel 2026 bioRxiv. DOI https://doi.org/10.64898/2026.10.07.757347: closed-loop synthesis for the basolateral amygdala. Abstract VERIFIED.
- Soderberg, Jang & Kragel 2026 SCAN. DOI https://doi.org/10.1093/scan/nsag028: encoding analysis, not stitching. Abstract VERIFIED.
- Peelen, Atkinson, Vuilleumier 2010 J Neurosci (DOI https://doi.org/10.1523/JNEUROSCI.2161-10.2010); Skerry & Saxe 2014 J Neurosci (DOI https://doi.org/10.1523/JNEUROSCI.1676-14.2014); Chikazoe et al. 2014 Nat Neurosci (DOI https://doi.org/10.1038/nn.3749). Abstracts VERIFIED. All define "same emotion" by category or valence across formats or modalities, not by a model.
- Smith, Mannering, Marcu 2025 ICML (PMLR 267) "Functional Alignment Can Mislead: Examining Model Stitching". INDIRECT (snippet): models with very different biases, even ones trained on clustered random noise, can be stitched.
- Athanasiadis, Karmush, Felsberg 2026 ICML (PMLR 306) "Grounding Functional Similarity by Invariance-Aware Model Stitching". README VERIFIED (cloned): adds a backward or invariance requirement to forward stitching. Uses Nanda et al. "identically represented inputs", which are metamer-like.
- Nanda et al. 2023 AAAI "Do Invariances in Deep Neural Networks Align with Human Perception?": INDIRECT.
- MindEye (Scotti et al., arXiv 2305.18274): its README VERIFIES that fMRI is mapped to the token-level last hidden layer of the CLIP image model (257 x 768). This is precedent that fMRI can be mapped to a full token map. Venue and authors: INDIRECT.
- Wen et al. 2017 Cereb Cortex mapped voxels to AlexNet's last layer and passed the result through softmax: INDIRECT (search summary only).

======================================================================
2. SEARCHES RUN (novelty evidence)
======================================================================
PubMed (15 queries):
1. "metamer emotion": 0 hits.
2. "metamer AND (affective OR valence OR facial expression)": 1 hit (plant morphology; irrelevant).
3. "metamers[Title] AND (neural network OR brain)": 3 hits (Feather 2023; Freeman & Simoncelli 2011; Sohn & Jazayeri 2021 "prior-cost metamers"). None about emotion.
4. "metamers[Title/Abstract] AND (neurons OR fMRI OR cortex) AND (model OR network)", 2015 onward: 8 hits. None about emotion (contour, melanopsin light, color, texture, retina).
5. "model metamers fMRI": 0.
6. "metamer[TiAb] AND (visual cortex OR auditory cortex) AND (deep network OR neural network model)": 0.
7. "model stitching neural network representations": 15 hits, none brain-related.
8. "stitching AND fMRI AND deep neural network": 4 hits, none relevant.
9. "(emotion OR affective) AND fMRI AND (deep neural network layer) AND (decoded features OR feature decoding)": 1 hit, irrelevant.
10. "brain activity replace layer activations deep neural network drive model output": 0.
11. "(emotion OR affective) AND (invariance OR invariant) AND deep neural network AND fMRI AND representational similarity": 0.
12. "brain activity to deep neural network layer emotion decoding fMRI intermediate layer video", 2019 onward: 0.
13-15. Lookups for Sexton & Love, Golan, and Jang & Kragel (found as listed above).

Web (12 queries):
- "emotion/affective/emotional metamers": no relevant hits (only "meta-emotions").
- "natural metamers": no hit beyond Feather's work.
- "model metamers fMRI regions 2024-2026": none (one arXiv paper on graph-network metamers, 2510.17378).
- "emotion recognition network metamers": none.
- "metamers video models / video transformer": none; Feather covers image and audio models only.
- Adversarial attacks on facial expression recognition do exist in affective computing (for example a Sensors 2022 "Emotion Adversarial Attacks" paper and an IJPRAI paper). They aim at misclassification or privacy, not at matched representations tested against brains or people. INDIRECT.
- "emotion invariance pairs representational similarity": closest hits were an abstract-emotion RSA study (PMC6200969) and Korn et al. 2021, a workshop paper with an audio-visual network on 72 stimuli. Neither uses model-defined pairs.
- "model stitching fMRI": no completed study. arXiv 2503.19923 only PROPOSES stitching between an fMRI autoencoder and a vision transformer (INDIRECT).
- "brain stitching / neural stitching": none.
- "stitching neural recordings into deep network layer": Sexton & Love 2022.
- "decoded fMRI features fed into remaining layers": Wen 2017 (last layer -> softmax), Kamitani-lab feature decoding, BrainMCLIP (multi-layer CLIP fusion for reconstruction).
- Follow-ups citing Sexton & Love that use the method: none found (one search).

GitHub ("gh search repos 'model stitching'"): 15 repositories, none involving brain data.

Totals: not found in roughly 27 searches for an emotion metamer or for stitching brain data into an emotion model.

======================================================================
3. FEASIBILITY WITH OUR DATA
======================================================================
Model facts, VERIFIED from cloned code (JunShern/VideoMAE, the fork by the authors of the 61k-video dataset, modeling_finetune.py):
- forward_features: patch_embed -> + pos_embed (added only at the input) -> 12 pre-norm residual blocks -> norm (Identity when mean pooling is used) -> fc_norm(x.mean(1)) -> head Linear(768 -> 27).
- No class token.
- Tokens: (224/16)^2 x (16/2) = 1,568 tokens x 768 = 1,204,224 values per video per block.

B. Brain stitching

B-0. Stitching into the pooled representation just before the head
- The head is LayerNorm + Linear, so this is close to a linear decoder of the 27 outputs. It equals our existing generic path (Horikawa & Kamitani 2017 style) and Kragel's output decoding.
- Adds nothing new. Keep it only as the end point of the depth profile.

B-1. Full token-level stitching into block k
- Feasible. Ridge regression in its dual form gives the predicted token map as a weighted sum of the TRAINING videos' token maps:
  predicted map = K_test (K_train + λI)^-1 T_train
  so the voxel x 1.2M weight matrix is never stored.
- Storage: about 5.3 GB per block in fp16 for 2,181 videos; about 63 GB for 12 blocks.
- Downstream forward passes: about 42 regions x 12 depths x 2,181 videos x 5 subjects ≈ 5.5M partial runs of a ViT-B. Rough estimate: a few A100-hours. This uses my own UNVERIFIED cost assumption of about 180 GFLOPs per full forward.
- Precedent:
  - Sexton & Love stitched single-presentation fMRI (1,200 images) into large convolutional layers, one regression per unit;
  - MindEye maps fMRI to a 257 x 768 token map.
- End-to-end training (backpropagating the lens-output loss through frozen blocks) is only practical for the low-dimensional variants below.

B-2. Pooled variants for intermediate blocks (my proposals; no literature precedent except the principal-components variant)
- (a) Broadcast: all 1,568 tokens set to one predicted vector. Identical tokens make attention reduce to a per-token value projection, so the remaining network becomes a per-vector function. Out of distribution.
- (b) Dataset-mean token map + broadcast predicted deviation of the token mean.
- (c) Top-K principal-component reconstruction of the token map (Sexton & Love fig. S5 used 5,000 components).
- Required check before any brain data: apply (a), (b) and (c) to REAL videos' own token maps at each depth and measure how well the lens's 27-d output is preserved. A variant is legitimate only at depths where it preserves the output. This is cheap (one forward pass per variant and depth).

B-3. Expected outcome risk
- Sexton & Love found every region best at the latest layers. Pre-norm residual ViTs also carry information forward strongly, so our depth profile may be flat or only rise with depth.
- Required controls:
  - (i) an SNR-matched simulation null: true features -> synthetic voxels at each region's reliability -> the same pipeline (the project already plans this, methods spec section 3.3, control 2);
  - (ii) reference depth profiles from stitching stimulus features in place of brain data: low-level motion/color, object logits, caption embeddings. This is the analogue of Sexton & Love's pixel control, which peaked at the earliest layer.
- Interpret each region by which reference profile it resembles. This links information level, emotion and region in one map. Do not claim "region X equals block k" from a peak alone.

B-4. Evaluation
- Compare the stitched 27-d output with (1) the lens's own output for the same video (continuous profile agreement, as Sexton & Love used KL divergence to the image-driven output) and (2) human ratings, through the existing variance split against the Direct decoder.
- No top-1 labels and no thresholds.

B-5. Bonus (conditional)
- In the Mind captioning data, 2,180 training videos (single presentation) + 72 test videos x 5 repeats + recall imagery would allow:
  - higher-SNR testing on the 72 repeated videos;
  - "stitching recalled experience into the emotion model".
- Not found anywhere. Depends on whether we can access the training portion (UNVERIFIED).

A. Metamers

A-1. Natural pairs (existing data)
- 2,181 videos give about 2.38M pairs.
- Score each pair by lens distance (27-d output; also fc_norm 768-d) and content distance at each level (low-level, object, caption embedding).
- Avoid threshold groups (project rule): use a continuous "metamer score", for example content distance minus lens distance (both z-scored), as a weight, or report results across a sweep of percentiles.
- Head-null-space metamers: pairs whose fc_norm difference lies mostly in directions the 768->27 head discards, i.e. small ||W(f_i - f_j)|| / ||f_i - f_j||. This is exact and computable. It is the closest analogue of Feather's "same at the last stage, different inside".
- Also run the converse ("content metamers": same content, different lens output) to get a two-way test per region.
- Confounds:
  - single presentation plus slow drift: exclude same-run or temporally adjacent pairs;
  - lens distance and content distance are correlated (premise 2), so near-metamer pairs at early depths are essentially near-duplicate videos. Stage-specific natural metamers are therefore only available at late depths and at the output.

A-2. Synthesized metamers
- Compute is feasible: Feather's 24,000 steps on a 16x224x224x3 input. My UNVERIFIED estimate: about 10-30 A100-minutes per metamer, so 100 metamers ≈ 20-50 A100-hours.
- Validity requires new human emotion ratings of the metamer videos (a crowd study like Cowen's). The brain datasets cannot be used.
- Feeding metamers to DNN-based encoding models is circular: these noise-like inputs are adversarial for such models.
- Feather's model-to-model test is possible: does a second emotion lens (the V-JEPA lens B in spec v2) or a content model "recognize" the lens's metamers? It shows only model-to-model invariance.
- Ethical note: metamers synthesized from distressing reference videos.

======================================================================
4. CODE (git clone, all in the scratchpad)
======================================================================
- A: jenellefeather/model_metamers_pytorch.
  - Path: /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_metamers_pt/repo
  - README cites Feather 2023.
  - Has metamer generation, null distributions, "setup for your own model", Mechanical Turk experiment templates and the auditory fMRI regression.
  - Input pipeline is image/audio (NCHW): needs a video adapter for VideoMAE (a small adjustment).
  - The 2019 TensorFlow repo (unmaintained) is at /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_metamers_2019/repo
- Lens: JunShern/VideoMAE.
  - Path: /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_videomae_js/repo
  - Commit 35cf177 (2022-10-14); modeling_finetune.py lines 256-275 hold forward_features and the head.
  - For stitching, a forward hook on blocks[k] that replaces its output is enough.
- B, model-to-model stitching libraries (no brain code exists):
  - renyi-ai/drfrankenstein (Csiszárik et al., "Similarity and Matching of Neural Network Representations", arXiv 2110.14633): /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_drfrank/repo
  - athaioan/invariance-aware-stitching (ICML 2026; includes identically-represented-input generation plus stitching): /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_invstitch/repo
- Brain-side ridge: use the project's existing himalaya / FastL2LiR (methods spec v2).
- No official code found for Sexton & Love or for Bansal et al.
- MindEye repo (token-level mapping precedent): /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_mindeye/repo

======================================================================
5. SUGGESTED SYNTHESIS: "invariance-aware brain stitching" (not found)
======================================================================
A region is credited with corresponding to depth k of the emotion lens only if both hold:
- (forward, from Sexton & Love / Lenc & Vedaldi) its activity, mapped into depth k, drives the lens to that video's own emotion profile beyond the SNR-matched null and the feature-reference profiles;
- (backward, from Feather / Athanasiadis) pairs the lens treats as the same at depth k (natural metamers, available at late depths and the head null space) are also treated as the same by that region, while content metamers are not.

Rationale: Smith et al. 2025 show that forward stitching alone can mislead. That is exactly the skeptic's objection, "brain stitching is just decoding through the network".

This fits all four acts:
- Act 1: lens invariances split by information level.
- Act 3: brain -> lens.
- Act 2: region-wise comparison.
- It never groups stimuli into categories.

Honest framing: the metamer half extends our own H2. The stitching half is a direct import of Sexton & Love 2022 into emotion. The novelty claim should rest on the combination plus the emotion-video setting, not on either half alone.

Plain names for the write-up (the user asked for no acronyms):
- A: "모델이 같다고 보는 서로 다른 영상 쌍" (model metamers)
- B: "뇌 이어붙이기" (brain stitching)

The Science Advances 2022 paper calls B "direct interface"; cite it as the origin.

======================================================================
6. FILES
======================================================================
Extracted full texts I read, in /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/txt/:
- feather2023.txt
- lenc2019.txt
- kragel2019.txt
- horikawa2020.txt
- horikawa2025.txt

Sexton & Love 2022 was read inline from PubMed Central PMC9278854 (not saved).

Project files read (not modified):
- /home/user/EmoBrain/docs/paper_logic_merged.md (H2 at line 78)
- /home/user/EmoBrain/docs/notes/methods_spec_2026-11-25/methods_spec_v2.md (generic path at line 222; lens architecture at lines 17-18 and 100)

Blocked hosts, needed to move the INDIRECT items above to VERIFIED: arxiv.org, papers.nips.cc, proceedings.neurips.cc, papers.neurips.cc, openaccess.thecvf.com.

##### robust_time_attr
# 비전 방법 3종 검토: 인용 검증, 정서 분야 선행연구, 실현성, 판정

**표기 규칙.** VERIFIED는 원문 본문·초록·코드를 직접 읽은 경우, INDIRECT는 검색 결과 요약만 본 경우, UNVERIFIED는 확인하지 못한 경우다. PubMed 자료는 PubMed에서 가져왔고 DOI 링크를 붙였다.

**접근 제약.** 다음 사이트는 프록시가 막았다: openaccess.thecvf.com, export.arxiv.org, api.crossref.org, api.openalex.org, api.semanticscholar.org, dblp.org, sites.lafayette.edu. 그래서 CVF·arXiv 논문의 본문은 읽지 못했다.

---

## 0. 판정 요약

| 후보 | 판정 | 가장 가까운 선행연구 | 핵심 위험 |
|---|---|---|---|
| A. 손상 강건성 곡선 | 부분적으로 새로움 | Greco 외 2022 (얼굴표정 손상 벤치마크, 정확도 기준); De Cesarei & Codispoti 2008·2010 (사람 실험, 흐림·축소); Jang, McCormack & Tong 2021 (비전: 잡음 학습 모델 ↔ fMRI) | 모델 안에서만 비교하면 순환 논증이 된다. 영역 encoding 모델과 감정 head가 같은 특징을 읽는 두 개의 선형 출력이기 때문이다 |
| B. 시간 순서 | 부분적으로 새로움. 뇌 쪽 방법은 비전에 이미 있다 | Lahner 외 2024 Nat Commun (BOLD Moments: 프레임을 섞은 입력에서 영역별 예측 정확도가 떨어짐); Hasson 외 2008 J Neurosci (정방향·역방향·조각 섞은 영화로 본 시간 수용창 위계) | Cowen 영상은 약 5초, 모델 입력 창은 약 2초다. "상황의 순서"를 검정하기엔 짧다 |
| C. 귀속·가림 지도 | 부분적으로 새로움. 셋 중 가장 약하다 | EmotionROI (ICIP 2016); EMOd (CVPR 2018); Borriero 외 2024 (fMRI 감정 해독기 + 영상 모델 + 시선 추적에 귀속 기법 적용); Brain Dissection 2023; BrainSAIL 2025; St-Yves & Naselaris 2018 | 두 반쪽이 모두 이미 있고 새로운 건 조합뿐이다. 순환성 문제가 있고 계산량이 크다 |

**권고.** A와 B를 하나의 **"정보 제거 사다리"**로 합치는 쪽이 가장 강하다. 손상 정도를 단계별로 올리고, 각 단계에서 실제 데이터(손상되지 않은 영상에 대한 사람 평정과 뇌 반응)를 얼마나 설명하는지를 잰다. 그러면 감정 차원별·영역별 의존 프로파일을 저수준·객체·상황 세 층위에서 동시에 얻는다. C는 보조 그림 이상으로 쓰지 않는다.

---

## 1. 인용 검증

| 인용 | 상태 | 근거와 비고 |
|---|---|---|
| Hendrycks & Dietterich, "Benchmarking Neural Network Robustness to Common Corruptions and Perturbations", ICLR 2019 | **VERIFIED** | hendrycks/robustness README의 bibtex. `imagenet_c.corrupt()`는 손상 15종 + 검증용 4종, 강도 0–5단계 (코드 확인). 주의: 대표 지표 mCE는 top-1 오류율 기반이라 프로젝트 규칙상 그대로 쓸 수 없다 |
| Wei, Lim, Zisserman, Freeman, "Learning and Using the Arrow of Time", CVPR 2018, pp. 8052–8060, DOI 10.1109/CVPR.2018.00840 | INDIRECT | CVF 페이지, Harvard VCG bib, MIT DSpace의 검색 요약. 과제는 영상이 정방향인지 역방향인지 판별하는 것 |
| Sevilla-Lara, Zha, Yan, Goswami, Feiszli, Torresani, "Only Time Can Tell", WACV 2021, pp. 535–544 (arXiv 1907.08340) | INDIRECT | 사람에게 프레임을 섞은 영상을 보여주고 행동을 알아볼 수 있는지 판단하게 한다. 알아볼 수 없는 범주를 "시간 범주"로 분류한다. 우리 규칙상 범주로 나누는 부분은 빼고 연속적인 순서 의존도로 바꿔야 한다 |
| Zeiler & Fergus, "Visualizing and Understanding Convolutional Networks", ECCV 2014, LNCS 8689, pp. 818–833 | 학회 정보는 INDIRECT; 가림 기법의 출처는 VERIFIED | pytorch/captum 코드 `captum/attr/_core/occlusion.py` 38–40행이 가림 기법의 원 논문으로 arXiv 1311.2901을 가리킨다 |
| **Peng, Sadovnik, Gallagher, Chen, "Where Do Emotions Come From? Predicting the Emotion Stimuli Map"** | **학회 오류. CVPR이 아니라 ICIP 2016, pp. 614–618, DOI 10.1109/ICIP.2016.7532430 (INDIRECT)** | researchr, ORNL 기록, Sadovnik 연구실 공지("Paper accepted into ICIP 2016")의 검색 요약. GitHub Kahsolt/EmotionROI-ex README가 `ICIP16_EmotionROI.pdf`로 링크한다 (VERIFIED). 같은 그룹의 CVPR 논문은 2015년 "A Mixed Bag of Emotions" (Emotion6 데이터). EmotionROI는 이미지 1,980장, 6개 범주이고 정답 지도는 시선 추적이 아니라 사용자 연구에서 나왔다 (INDIRECT) |
| (관련) Fan 외, "Emotional Attention: A Study of Image Sentiment and Visual Attention", CVPR 2018 | INDIRECT | EMOd: 이미지 1,019장, 관찰자 16명의 시선 추적 |
| Mazeika 외, NeurIPS 2022 (VCE 데이터) | **VERIFIED** | hendrycks/emodiversity README: 영상 61,046개, 감정 27개, 학습 50,000 / 테스트 11,046. 마지막 저자가 Dan Hendrycks로 ImageNet-C 저자와 같다. 저장소와 VideoMAE 포크를 검색해 보니 손상·섞기 평가 코드는 없다 (VERIFIED). 포크 설정은 `num_frames 16`, `sampling_rate` 기본값 4, `tubelet_size` 기본값 2, `test_num_segment 2`, `test_num_crop 3` (VERIFIED) |

---

## 2. 선행연구

### 검색 기록

**PubMed 약 30회.** 실제 쓴 질의는 아래와 같다.
- "emotion recognition deep neural network robustness corruption blur noise" → 0건
- "De Cesarei Codispoti blurring emotional pictures"
- (scrambled OR shuffled) AND (movie OR film) AND emotion*
- Hasson[Author] AND temporal receptive windows
- (degraded OR blurred OR "spatial frequency") AND emotion* AND ("deep neural network" OR CNN)
- (perturbation OR corruption* OR degradation) AND (emotion* OR affective) AND "encoding model" → 0건
- (texform* OR "texture synthesis" OR "phase-scrambled") AND emotion → 20건. 모두 얼굴 ERP 실험의 통제 조건이라 무관
- grayscale/achromatic AND emotional pictures
- ("played backward" OR "reversed playback" OR "time-reversed") AND emotion AND video
- (temporal order OR scrambl*) AND emotion* AND naturalistic AND fMRI
- "encoding model" AND (saliency OR attribution OR occlusion OR "spatial selectivity" OR "receptive field") AND fMRI AND deep
- emotion AND (saliency map OR Grad-CAM OR occlusion) AND (fMRI OR visual cortex OR brain) AND (image OR video)
- 저자 검색: Kragel, Soderberg, Peelen, Conwell, Horikawa, Cowen, Vuilleumier, Delplanque, Emo-FilM 등

**WebSearch 약 18회.** 주제: 얼굴표정 인식 손상 벤치마크, 감정 이미지 손상 강건성, 영상 감정 인식의 프레임 섞기와 시간 순서, 시간의 화살과 감정, 영상 모델 encoding에서 시간 섞기, Cowen 영상 + 섭동, 감정 귀속 지도와 뇌 encoding 귀속 비교, Brain Dissection, BrainSAIL, Explainable Emotion Decoding, 손상 강건성과 fMRI 영역.

**본문 전체를 읽은 논문 (VERIFIED, 키워드 검색 포함).**
- Kragel 2019, Gao 2025, Conwell 2025: 손상·가림·프레임 섞기 조작이 **없다**.
- Liu 2024: 흑백 변환만 하고 lesion·gain 조작을 했다. 손상 조작은 없다.
- Jang & Kragel 2025: 손상이나 귀속 지도는 없다. encoding 예측값을 색·공간주파수 파워에 회귀했고, 이미지 합성을 했다.

### A. 손상 강건성

**감정 인식 모델의 손상 벤치마크는 이미 있다. 모두 얼굴표정이고 정확도 기준이다.**
- Greco, Strisciuglio, Vento, Vigilante 2022, Multimedia Tools Appl, DOI 10.1007/s11042-022-12790-7: RAF-DB-C / RAF-DB-P. MiviaLab/emotion-robustness README로 VERIFIED.
- FER-C: 손상 17종 × 강도 5단계, 보정(calibration) 중심. INDIRECT.
- ICUSI 2025: 영상 화질 저하와 감정 인식. INDIRECT.
- Li & Ying 2022, Front Comput Neurosci: 얼굴 감정 분류 CNN에 가림을 적용하고 CAM을 사람과 비교. VERIFIED, [DOI](https://doi.org/10.3389/fncom.2022.1054421).

**사람을 대상으로 한 감정 그림 손상 실험 (모두 VERIFIED 초록).**
- De Cesarei & Codispoti 2008, Emotion: 고공간주파수가 주관적 평가를 조절한다. [DOI](https://doi.org/10.1037/1528-3542.8.3.352)
- De Cesarei & Codispoti 2010, PLoS One: 피부전도 반응의 정서 조절은 줄지만 놀람 반사는 유지된다. [DOI](https://doi.org/10.1371/journal.pone.0013399)
- Bekhtereva & Müller 2017: 컬러와 흑백 비교. [DOI](https://doi.org/10.3758/s13415-017-0530-z)
- Vuilleumier 외 2003, Nat Neurosci: 저공간주파수 공포 얼굴과 편도체. [DOI](https://doi.org/10.1038/nn1057)
- Delplanque 외 2007: IAPS 사진의 공간주파수 분석. [DOI](https://doi.org/10.1016/j.jneumeth.2007.05.030)

**비전 분야에서 강건성과 뇌를 연결한 연구.**
- Jang, McCormack & Tong 2021, PLoS Biol: 잡음으로 학습한 모델이 행동과 fMRI 반응을 더 잘 맞춘다. VERIFIED, [DOI](https://doi.org/10.1371/journal.pbio.3001418)
- Dapello 외, McNeal 외 2024 (적대적 섭동과 encoding 모델). INDIRECT.

**같은 Cowen 영상의 저수준 운동 정보.**
- Thieu, Ayzenberg, Lourenco, Kragel 2024, iScience: 접근(looming) 감지 신경망을 Cowen & Keltner 2017 영상에 적용하면 주로 각성(arousal)을 거쳐 감정 평정을 예측한다. 본문 Key resources 표로 VERIFIED, [DOI](https://doi.org/10.1016/j.isci.2024.109886)
- Act 1의 "저수준 운동" 층위의 근거로 바로 쓸 수 있다.

**찾지 못한 것 (PubMed 30회 + 웹 18회 기준).**
- 감정을 *불러일으키는* 영상에 손상 강도를 단계적으로 올리면서 연속 감정 차원별 의존 곡선을 그린 연구.
- 그 곡선을 뇌 영역별 곡선과 대조한 연구.

**순환성 경고.** 영역 encoding 모델을 r = W_R f(x), 감정 head를 e = W_E f(x)라 하자 (같은 VideoMAE 특징 f). 그러면 손상에 따른 두 곡선의 유사도는 주로 W_R과 W_E 행 사이의 정렬로 정해진다. 이것은 손상 없는 데이터에서도 이미 측정할 수 있는 양이다.

**비순환적인 설계 (권장).** 각 손상 단계마다 특징을 다시 뽑고, 교차검증으로 다음 두 가지를 *실제 데이터*에 다시 맞춘다.
- 손상되지 않은 영상에 대한 사람 평정 또는 Act 1의 고정된 감정 렌즈의 깨끗한 출력.
- 손상되지 않은 영상에 대한 Horikawa 2020 뇌 반응.

그러면 곡선은 "설명 분산 대 손상 강도"가 된다. 지표는 top-1·mCE 대신 연속 프로파일 거리와 설명 분산을 쓴다.

### B. 시간 순서

**뇌 쪽은 이미 있다.**
- Hasson 외 2008, J Neurosci. VERIFIED 초록, [DOI](https://doi.org/10.1523/JNEUROSCI.5487-07.2008)
  - 소리 없는 영화를 정방향, 역방향, 조각 섞기로 보여줬다.
  - 초기 시각영역(V1, MT+)은 시간 구조를 깨도 반응이 안정적이었다.
  - STS와 precuneus는 약 12초, 외측고랑 후부·TPJ·FEF는 약 36초에 걸쳐 쌓인 정보에 의존했다.
  - 이것은 H3(transmodal 피질까지 이어짐)와 직결된다.
- Lerner 외 2011 [DOI](https://doi.org/10.1523/JNEUROSCI.3684-10.2011)와 Chang, Nastase, Hasson 2022 [DOI](https://doi.org/10.1073/pnas.2209307119): VERIFIED.
- **Lahner 외 2024, Nat Commun (BOLD Moments).** VERIFIED 본문, [DOI](https://doi.org/10.1038/s41467-024-50310-3)
  - 행동 인식 영상 모델(TSM)에 프레임을 섞은 영상을 넣었다.
  - 순서를 유지한 특징과 섞은 특징으로 *실제* fMRI를 각각 예측하고, 영역·블록별 정확도 차이를 FDR 보정으로 검정했다.
  - 섞으면 대부분 영역에서 정확도가 떨어졌다.
  - 영상당 3초 클립에 반응 추정치 하나라는 설계가 Horikawa 2020과 같다. **우리 B의 뇌 쪽 절반은 비전에서 이미 한 일이다.**

**감정 쪽.**
- 표현된 얼굴표정 인식에서의 프레임 섞기 실험: arXiv 2604.15280 (2026, 시각-언어 모델은 순서에 둔감), 2017년 EmotiW LSTM 연구. 둘 다 INDIRECT.
- Korolkova 2018, Vision Res: 시간을 뒤집은 동적 얼굴표정은 사람의 인식을 바꾼다. VERIFIED, [DOI](https://doi.org/10.1016/j.visres.2017.10.007)
- Dmochowski 외 2012: 장면을 섞으면 뇌파의 개인 간 상관이 줄어든다. VERIFIED, [DOI](https://doi.org/10.3389/fnhum.2012.00112)
- 장면·상황 영상이 *불러일으키는* 감정의 차원별 순서 의존도, 그리고 그것과 영역별 순서 의존도의 결합은 **찾지 못했다**.

**실현성 제약.**
- Cowen 영상 길이가 약 5초라는 근거는 INDIRECT다. arXiv 2505.12746 요약이 출처이고, Horikawa 2020 본문에는 길이가 없었다. Transparent Methods는 읽지 못했다.
- VideoMAE 입력은 16프레임 × 간격 4로, 30fps 가정 시 약 2.1초다. 시간 방향 토큰 묶음(tubelet)은 2프레임이다.
- 따라서 프레임 단위로 섞으면 "상황 순서"가 아니라 국소 운동이 깨진다. 실험 조건은 다음처럼 둔다.
  - 역재생: 운동량은 유지하고 방향만 바꾼다 (Wei 2018).
  - 클립 전체에 걸친 구간 단위 섞기: 구간 길이를 여러 단계로.
  - 정지 프레임 반복: 운동만 제거한다.
- Horikawa 데이터는 영상당 블록 평균 하나라서 영상 내 시간 변화를 볼 수 없다. Lahner 논리, 즉 "순서 특징이 영상 간 분산을 더 설명하는가"만 검정할 수 있다.
- **Emo-FilM**은 긴 시간 척도를 다룰 수 있다. 단편영화 14편(총 2.5시간 이상), 평정자 44명, 항목 50개, fMRI 참가자 30명. VERIFIED, [DOI](https://doi.org/10.1038/s41597-025-04803-5)
  - Hasson식으로 여러 시간 척도에서 섞은 특징을 컴퓨터 안에서 만들고, 실제 fMRI와 1Hz 평정을 각각 예측하게 한다.
  - 이렇게 하면 "감정 차원별 시간 수용창"을 추정할 수 있다. 이것도 찾지 못했다.

### C. 귀속·가림

**감정 귀속 지도는 이미 있다.**
- EmotionROI (ICIP 2016), EMOd (CVPR 2018), Li & Ying 2022 (CAM).
- EmotionROI-ex README에는 "ROI 주석이 감정별이 아니라 주의 초점에 가깝다"는 제3자 관찰이 있다 (README 내용만 VERIFIED, 동료 검토 없음).

**영역 encoding 모델의 공간 귀속도 비전에서는 이미 있다.**
- Sarch, Tarr, Fragkiadaki, Wehbe, Brain Dissection (NeurIPS 2023). GitHub의 bibtex는 bioRxiv 2023으로 되어 있다 (VERIFIED).
- Luo 외, BrainSAIL (ICLR 2025). INDIRECT.
- St-Yves & Naselaris 2018, NeuroImage, fwRF: 공간 "어디" 파라미터를 따로 추정한다. VERIFIED, [DOI](https://doi.org/10.1016/j.neuroimage.2017.06.035)

**감정 + 뇌 + 귀속 기법의 가장 가까운 사례.**
- Borriero 외 2024, xAI 2024 학회, arXiv 2408.00493 "Explainable Emotion Decoding for Human and Computer Vision". INDIRECT.
- 포레스트 검프 fMRI 감정 해독기와 영화 프레임 모델에 LIME·SHAP을 적용하고 시선 추적과 연결했다.
- 다만 뇌 쪽 귀속은 해독기의 "뇌 부위"에 대한 것이지, 영역 encoding 모델의 "화면 위치"에 대한 것이 아니다.
- Jang & Kragel 2025는 이미지 합성이고 귀속이 아니다 (VERIFIED).

**찾지 못한 것.** 같은 자극에서 감정 차원별 시공간 귀속 지도와 영역별 encoding 귀속 지도를 지도 대 지도로 비교한 연구.

**C의 약점.**
- A와 같은 순환성이 있다.
- 화면 전체에 펼쳐진 영상이고 시선 통제가 없어서 고차 영역의 공간 선택성이 약할 수 있다.
- 계산량이 크다. 토큰 8×14×14 = 1,568개이고, 2×2×2 묶음으로 가려도 약 196회 × 2,181개 영상 × 6개 view = 약 260만 회 전방 계산이다 (추정).
- Horikawa 2025의 테스트 영상 72개로 제한하면 현실적이다.

---

## 3. 우리 자원으로 실현 가능한가

**A의 계산량.**
- 2,181개 영상 (Horikawa 2020 본문의 "2,181 unique videos", VERIFIED) × (손상 종류 약 6 × 강도 5 + 원본) ≈ 6.8만 개 영상 × 6개 view ≈ 40만 회 ViT-B 전방 계산. GPU 한 장으로 수 시간이다 (추정).
- 병목은 CPU의 프레임별 손상 처리다. glass blur처럼 느린 종류는 뺀다.
- 손상 종류와 정보 층위의 대응(제안):

| 층위 | 손상 조작 | 근거 상태 |
|---|---|---|
| 저수준 | 대비, 채도 0(색 제거), 가우스 잡음, 흐림·픽셀화 | ImageNet-C에 있음 |
| 객체·배치 | 공간 패치 섞기 | ImageNet-C에 없음. 이번에 원 출처를 확인하지 못함 (UNVERIFIED) |
| 운동 | 정지 프레임 반복 | — |
| 상황·순서 | 구간 섞기, 역재생 | — |

**뇌 데이터 제약.**
- Horikawa 2020은 자극을 한 번만 보여줘서 노이즈 천장을 추정할 수 없다. 본문 VERIFIED: "because each stimulus was presented only once, we were unable to estimate…"
- 따라서 영역 간 비교는 "손상 단계 성능 / 원본 성능"처럼 상대 곡선으로 한다.
- Horikawa 2025의 72개 영상 × 5회 반복(맥락 정보, 이번에 검증하지 않음)으로 노이즈 천장 보정 확인을 할 수 있다.

**프로젝트 규칙 준수.**
- 자극을 감정 범주로 묶지 않는다. 묶는 것은 조작 종류다.
- top-1, 임계값, mCE를 쓰지 않는다.
- 렌즈 출력과 평정 두 기준을 모두 보고한다. 모델 중심 주장과 사람 기준 근거를 각각 세우기 위해서다.

---

## 4. 참고할 인접 연구 (새로움 주장에 영향을 준다)

- **Du, He 외, arXiv 2509.24298 (2025).** INDIRECT.
  - 같은 2,180개 영상과 5명의 뇌 데이터를 썼다.
  - 다중모달 대형언어모델에게 "셋 중 다른 하나 고르기" 판단을 수백만 번 시켰다. 다른 분야 방법을 이 데이터에 가져온 사례가 이미 있다는 뜻이다.
  - 대형언어모델 기반이므로 우리 모델 백본으로 쓰지는 않는다.
- **Jang, Riels, Aberman, Tao, Kragel 2026 bioRxiv.** VERIFIED 초록, [DOI](https://doi.org/10.64898/2026.10.07.757347)
  - 기저외측 편도체 encoding 모델로 이미지를 합성하고, 폐쇄 루프 fMRI로 검증했다.
  - Kragel 그룹이 "합성 → 새 데이터로 검증" 쪽으로 이미 나아갔다는 점을 유의해야 한다.
- **Soderberg, Jang & Kragel 2026, SCAN.** VERIFIED 초록, [DOI](https://doi.org/10.1093/scan/nsag028)
  - 얼굴표정 모델과 장면 모델 중 어느 쪽이 pSTS와 편도체 반응을 더 잘 예측하는지 비교했다.

---

## 5. 내려받은 저장소 (모두 scratchpad 아래)

- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_imagenetc/robustness
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_emodiv/emodiversity
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_vmaefork/VideoMAE
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_ferrobust/emotion-robustness
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_captum/captum
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_emoroi/EmotionROI-ex
- /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v4_braindissect/brain-dissection

/home/user 아래는 아무것도 수정하지 않았다.