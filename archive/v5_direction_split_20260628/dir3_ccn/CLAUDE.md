# CCN_Emotion Project Instructions

> **Validity gate (2026-07-21):** Legacy Brain-JEPA embeddings used a mean of 10
> fixed temporal sin/cos codes for a one-patch input. Treat all Brain-JEPA-dependent
> claims in this file as historical/provisional until the corrected frozen and
> cross-encoder analyses in `study1/code/brain_encoder_validation/` finish. Direct
> raw-BOLD content-affect partitioning is unaffected.

## Project Identity

CCN_Emotion is the project behind the **CCN 2026 accepted abstract**
"Fine-Grained Emotion Structure in the Brain-Predictable Subspace of a Self-Supervised Video Model" (Moon, 2026, poster).

It is **distinct from EmoViS** even though both projects use the Horikawa et al. (2020) dataset.

| | CCN_Emotion (this project) | EmoViS (`/pscratch/sd/s/sjmoon/EmoViS/`) |
|---|---|---|
| Brain side | Brain-JEPA encoded (foundation-model) representation | Raw BOLD (450 parcels) RDM |
| Model side | V-JEPA2 only (single self-supervised video model) | Multi-model spectrum (VideoMAE, DINOv2, V-JEPA2, CLIP_vis, Caption+LLM) |
| Question | What kind of visual structure does the brain read out from a self-supervised video model? | Which model family in the sensory-to-semantic spectrum best matches stimulus-level brain geometry? |
| Method | Brain-aligned subspace via Brain-JEPA → V-JEPA2 ridge; PC-level analysis | Cross-validated RSA per model; variance partitioning; layer-wise gradient |

The two projects are complementary, not redundant. CCN_Emotion narrows in on the V-JEPA2 alignment object; EmoViS broadens across model families.

---

## Folder Structure (reorganized 2026-07-21)

```
CCN_Emotion/
├── CLAUDE.md
├── README.md / README_KR.md
├── .gitignore
├── Paper/                           ← published abstract + drafts
│   ├── ccn2026_accepted.pdf
│   └── (camera_ready/, framework.md added as needed)
├── notes/                           ← decision logs, narrative memos
│   └── archive/                     ← old direction/spec docs (pre-2026-05-26)
├── data/
│   └── raw/                         ← raw inputs (.gitignored where appropriate)
│       ├── brain_embeddings/         (Brain-JEPA 768-dim, 5 subj × 2196)
│       ├── video_embeddings/         (V-JEPA2 1408-dim, CLIP 512-dim)
│       ├── videos/                   (Cowen-Keltner CowenEmotionVideos)
│       ├── feature/                  (Horikawa .mat features)
│       ├── raw_fmri/                 (fmri_raw.npy, 5 × 2196 × 450)
│       ├── semantic_features.csv
│       └── vision_features.csv
├── logs/                            ← project-wide SLURM logs
├── study1/                          ← MAIN POSTER/PAPER WORKSTREAM
│   ├── README.md
│   ├── code/
│   │   ├── shared_alignment/        ← supporting shared-channel screen
│   │   ├── affective_characterization/ ← 34D and A/V functional probes
│   │   ├── cortical_transformation/ ← primary LOSO cortical analysis
│   │   ├── content_affect_partition/ ← no-PCA content and affect controls
│   │   └── archive/                 ← legacy, robustness, figures, extraction
│   ├── data/
│   │   ├── shared_alignment/
│   │   ├── affective_characterization/
│   │   └── archive/
│   ├── archive/reports/             ← dated RESULTS_EXP notes
│   ├── logs/
│   └── results/
│       ├── accepted_abstract/
│       ├── cortical_transformation/
│       └── archive/legacy_figures/
└── study2_thesis/                   ← parallel thesis workstream
    ├── code/, data/, results/, logs/, storyline/, reference/, figures/
```

### Rules

- Scripts must live in `study{N}/code/`. No scripts at repo root.
- Every new `.py` must have a matching `{script_name}.md` next to it documenting purpose, inputs, outputs, parameters.
- Every new `.py` must have a matching `{script_name}.sh` SLURM submission script.
- Active scripts use scientific names, not experiment numbers. Do not add new `expXX` or numbered scripts.
- Active code must not import from `study1/code/archive/`.
- `data/raw/` = raw inputs only. Never write derived data here.
- `study{N}/data/` = intermediate processed data (RSMs, PCs, predictions).
- `study{N}/results/` = final analysis outputs (figures, tables, .npz with statistical tests).
- `notes/` = project-wide decision logs, narrative memos. Not script docs.
- `notes/archive/` = superseded direction/spec docs.

---

## Current Poster Narrative (updated 2026-07-21)

Primary question:

> **How does the cortical hierarchy transform video-foundation-model representations into affective brain representations?**

The shared V-JEPA2/Brain-JEPA subspace is now a method for estimating cross-domain information, not the final scientific endpoint. The primary analysis maps where this shared channel predicts raw BOLD and where continuous fine-grained affective profiles explain complementary variance beyond shared and full-video representations.

Target claim, only if supported by held-out subject and stimulus analyses:

> Shared video-brain information is expressed preferentially in perceptual systems, whereas video-unexplained fine-grained affective information increases toward transmodal cortex.

See `notes/poster_update_visual_semantic_subspace.md` for the poster specification and `notes/long_term_research_roadmap.md` for the research program.

## Accepted Abstract Narrative (historical baseline, 2026-05-26)

The core finding of the CCN paper is that **a compact subspace (3 PCs) of V-JEPA2 video representations is linearly predictable from Brain-JEPA fMRI representations, and this subspace carries categorical emotion structure better than dimensional (V-A) structure (ratio 1.44 vs 1.26 in the full V-JEPA2 space, stable across 5 subjects).**

### What the alignment necessarily IS

V-JEPA2 only sees video input. Therefore Brain-JEPA ↔ V-JEPA2 alignment **is by construction visual statistics**. The interesting question is not "is the alignment visual" (yes, trivially), but **what kind of visual structure is brain-readable**.

### Three-pillar narrative

1. **Existence.** A compact, brain-readable subspace exists in V-JEPA2 (3 PCs survive FDR after Brain-JEPA → V-JEPA2 ridge). Shown in the abstract.
2. **Specificity.** This subspace's categorical-vs-dimensional ratio survives controls for generic visual baselines (low-level statistics, object recognition, scene categorization, motion energy). To be added: confound regression with multiple baselines, not only VGG19 + 73-dim semantic.
3. **Self-supervised contribution.** Untrained ViT and supervised ViT baselines do NOT produce the same categorical-vs-dimensional pattern in their brain-aligned subspaces. To be added: untrained V-JEPA2, ImageNet-supervised ViT-L, VideoMAE comparison.

### Stimulus canonical = 2185 (locked 2026-05-27)

Horikawa repeat clips (stim_idx 2185-2195, 11 개) 메인 분석에서 제외. **모든 분석에 2185 stimuli 사용.** 이는 EmoViS / EmoBrain standard 와 일관.

- Master stimulus index: `stim_idx 0-2184` (2185 개)
- Brain-JEPA: `(5, 2196, 768)` → `[:, :2185, :]` 슬라이스
- Video embeddings: EmoViS final (이미 2185)

### Primary embedding paths (locked 2026-05-27)

EmoViS 가 모든 모델 embedding 을 (2185, *) 로 추출해놨음. CCN_Emotion 은 symlink 로 사용. 추가 추출 불필요.

```
data/raw/video_embeddings/
├── emovis_vjepa2_pretrained.npy   (2185, 1408)  Primary 1 (자기지도 비디오)
├── emovis_vjepa2_scratch.npy      (2185, 1408)  Pillar 3 baseline (untrained)
├── emovis_clip_pretrained.npy     (2185, 1024)  Primary 2 (visual-text)
├── emovis_clip_scratch.npy        (2185, 1024)  Pillar 3 baseline
├── emovis_dinov2_pretrained.npy   (2185, *)     Pillar 2/3 baseline (object SSL)
├── emovis_dinov2_scratch.npy      (2185, *)
├── emovis_videomae_pretrained.npy (2185, *)     Pillar 3 baseline (다른 SSL video)
├── emovis_videomae_scratch.npy    (2185, *)
└── emovis_stim_idx.npy                          stim_idx 0-2184
```

**CLIP variant**: `openai/clip-vit-large-patch14` (image encoder only, 3-frame at 25/50/75%).
**V-JEPA2**: `facebook/vjepa2-vitg-fpc64-256` (16-frame uniform).
**DINOv2**: ViT-G (3-frame at 25/50/75%).
**VideoMAE**: v2 (16-frame uniform).

기존 CCN_Emotion 의 `clip_embeddings.npy` (2196, 512) 와 `vjepa2_embeddings.npy` (2196, 1408) 는 deprecated. 분석에서 사용 금지. EmoViS 버전 사용.

### Dual primary model (locked 2026-05-27)

기존 V-JEPA2 only → V-JEPA2 + CLIP dual-primary.

**Background**: EmoBrain 프로젝트의 emotion prediction probe 결과, **CLIP > V-JEPA2 모든 task 에서** (Valence reg Pearson 0.683 vs 0.470, Cat34 bal_acc 0.383 vs 0.293).

따라서 두 모델을 primary 로 운영. M1, M2, M3 둘 다 계산. 두 모델 결과 비교가 새로운 finding 의 source.

- V-JEPA2: 자기지도 비디오, text 없음 (affectless 가설의 가장 깨끗한 instance)
- CLIP: visual-text contrastive, text-mediated emotion 가설

### Central positioning (locked 2026-05-26)

**Brain validation of the affectless machines hypothesis** (Conwell et al., 2025; Bao et al., 2024).

Operational question: **does the emergent emotion representation in a self-supervised video model coincide with the visual representation the brain uses when processing emotional video?**

Testable as M1 ∩ M2 overlap within V-JEPA2 (M3).
- M1 = brain-aligned subspace (Brain-JEPA → V-JEPA2 PC ridge)
- M2 = emotion-encoding subspace (V-JEPA2 PC → emotion ratings ridge + decoding)
- M3 = subspace overlap (Jaccard, Spearman rank correlation)

Differentiation from EmoViS: EmoViS tests Barrett constructionism (sensory-semantic ingredients vs linguistic categorization). CCN_Emotion tests affectless machines (does emergent emotion in DNN extend to brain). Different theoretical anchors.

Full framework: `Paper/framework_EN.md` / `Paper/framework_KR.md`.

### Multi-metric collection rule (2026-05-27)

Every analysis must compute and save **all applicable metrics**, not a single chosen one. Picking a metric post hoc is fine; rerunning to add a metric is wasted compute.

**Continuous regression target** — compute and save:
- R² (cross-validated)
- Pearson r (on CV predictions)
- Spearman r (on CV predictions)
- MAE, RMSE, MSE
- Explained variance score

**Categorical decoding target** — compute and save:
- Top-1 accuracy, Top-5 accuracy (if K >= 5)
- ROC-AUC (One-vs-Rest, One-vs-One)
- Macro F1, Weighted F1
- Cohen's kappa
- Matthews correlation coefficient
- Confusion matrix

**Ranking comparison (e.g., M3 overlap)** — compute and save:
- Jaccard coefficient (top-K)
- Spearman rank correlation (full ranking)
- Kendall tau
- Set intersection size (top-K, top-2K, top-half)
- Mutual information between rankings (discretized)

**Brain alignment specifically** — compute and save:
- Cross-validated R² (raw + max-clipped)
- Pearson r on CV predictions
- Spearman r (rank-based)
- Permutation p-value
- FDR-corrected q-value
- Noise-ceiling-normalized R² (when noise ceiling is measured)

Save all in a single `.npz` keyed by metric name. Downstream analyses pick whichever metric the question requires.

### Confirmed framing rules

- Do not write "self-supervised learning spontaneously produces a categorical subspace" without baselines. That claim requires Pillar 3 to be tested.
- Do not write "the brain is categorical" or "subjective emotion is categorical." The analysis is about the visual-to-brain mapping, not phenomenology, not brain organization at large.
- Do not equate "brain-predictable" with "emotion-specific" until Pillar 2 (visual baseline controls) is run.
- Do label the metric (`category mean R² / V-A mean R²`) as a ratio metric with known dimensionality-bias caveats.

### The leap problem in the accepted abstract (confirmed 2026-05-26)

The abstract names the brain-aligned subspace an "affective subspace" and interprets it via "emotion schemas embedded in visual statistics" (Kragel 2019; Conwell 2025). Both are interpretive leaps not earned by the current data.

- **Leap 1 (naming): category-friendly brain-aligned visual subspace → affective subspace.** Requires Pillar 2 (DINOv2, Places365, optical flow, low-level statistics partial out) to rule out trivial visual-category-coherence explanation.
- **Leap 2 (mechanism): affective subspace → emotion schemas in visual statistics.** Kragel 2019 used supervised emotion classifier; Conwell 2025 used behavior only. Citing them as supporting theory for our self-supervised + brain claim requires Pillar 3 (untrained ViT, supervised ViT-L, VideoMAE comparison).

Until both pillars are tested, the honest description of the brain-aligned subspace is **"category-friendly visual readout channel between V-JEPA2 and the subject-invariant brain response,"** not "affective subspace." See `Paper/framework_EN.md` "The leap problem in the accepted abstract" section for full reasoning.

### Anchor reference for "deep alignment meaning"

**Sartzetaki, Roig, Snoek, & Groen (2025). One Hundred Neural Networks and Brains Watching Videos: Lessons from Alignment. ICLR 2025.**

99 NNs × 10 brains × 17 ROIs on Bold Moments video dataset. Tests what model properties drive brain alignment. Key findings: temporal processing → early visual cortex; action classification training → late visual cortex; FLOPs negatively correlated with alignment; video models > image models overall. EmoViS already cites this for H2 (cortical gradient).

CCN_Emotion is the **within-model, affective extension** of Sartzetaki's question. Sartzetaki asks: which model properties make brain alignment? CCN_Emotion asks: within V-JEPA2, which components carry the brain-aligned signal, and is that signal reducible to generic visual baselines or specific to self-supervised video pretraining?

### Connection to EmoViS

EmoViS's H1 (brain follows continuous sensory-semantic structure rather than discretized emotion ratings) is at the project level. CCN_Emotion's Pillar 2 (controlling generic visual baselines) is the within-V-JEPA2 instantiation of the same logical move: is the visual structure that aligns with brain emotion-specific, or is it captured by generic vision tasks?

The three projects compose into one logical chain:

- **Sartzetaki 2025**: across 100 models, what makes video-brain alignment? (model-feature → alignment)
- **EmoViS**: across sensory-to-semantic model spectrum, what aligns with stimulus-level emotional brain geometry? (model-family → emotional brain geometry)
- **CCN_Emotion**: within V-JEPA2, what component of its representation does the brain read out, and is it reducible to generic visual category baselines? (within-model → emotional brain geometry)

---

## Data Facts

- **Dataset**: Horikawa et al. (2020), 5 subjects, 2196 silent video clips (Cowen & Keltner 2017).
  - **Note**: Stimuli 2186-2196 (11 clips) are repeated clips. Main analyses in EmoViS use 2185 unique clips; the current CCN paper analyses appear to use all 2196 (verify per script).
- **Emotion annotations**: 34 binary category labels + 14 continuous affective dimensions (arousal, valence, dominance + 11 others).
- **Brain-JEPA**: NeurIPS 2024. UK Biobank rest-fMRI pretraining; 768-dim subject-invariant embedding.
- **V-JEPA2**: `facebook/vjepa2-vitg-fpc64-256`, ViT-Giant, 40 transformer blocks, 1408-dim.
- **CLIP**: `openai/clip-vit-base-patch32`, 512-dim.

---

## CCN 2026 Camera-Ready (deadline 2026-06-11 AoE)

- **Constraint**: 2-page limit including title block; "not intended to be a significant revision; major changes require withdrawal and resubmission to CCN 2027."
- **Required**: deanonymization, LaTeX v2026.1+ template, Acknowledgments/Disclosure section with LLM-use disclosure, cite overlapping in-press work.
- **Reviews arrive ~2026-05-26**; no author response period.
- **Talk selection announced ~2026-06-12**.

Camera-ready work plan: see `notes/camera_ready_plan.md` (to be drafted after reviews).

---

## SLURM / NERSC

- Account: `m4641`. Queue: `cpu` (default; switch to `gpu` per script when needed).
- Python env: `/pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate`.
- User runs all scripts via `sbatch`, never directly.

---

## What was reorganized on 2026-05-26

- Root-level scripts (`01_~07_*.py`, `run_*.sh`) and superseded results (`RESULTS_FULL.md`, `RESULTS_SUMMARY.md`, `CCN_draft.md`, the older V-JEPA2-vs-CLIP CKA workstream and its figures): moved to `study1/code/archive/superseded_root/`.
- `CCN2026/` (active workstream B): redistributed into `study1/{code, data, results, logs}` and `notes/archive/` (for direction/spec memos).
- `main/` + `storyline/` (thesis workstream): moved into `study2_thesis/`.
- Raw inputs (`brain_embeddings/`, `video_embeddings/`, `videos/`, `feature/`, `raw_fmri/fmri_raw.npy`, `*.csv`): moved to `data/raw/`.
- Accepted PDF: moved to `Paper/ccn2026_accepted.pdf`.
- `CowenEmotionVideos.zip` (1.7GB redundant with unzipped `videos/`): moved to `data/raw/` and may be deleted after verification.

The old V-JEPA2-vs-CLIP CKA results are **not** the CCN 2026 paper. Historical numbered analyses now live under `study1/code/archive/`; active work is limited to the three named modules documented in `study1/README.md`.
