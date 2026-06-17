# Neural Emotion Representations Align with Temporal Video Foundation Models

**CCN 2026 — 2-page abstract**
**Deadline: April 2, 2026**

---

## Introduction

Emotions are inherently temporal: fear builds, awe unfolds, anxiety accumulates across time. Yet computational models of emotional neural representations have largely relied on static visual features — single-frame image embeddings or semantic vectors — to explain brain responses to affective stimuli (Horikawa et al., 2020; Conwell et al., 2025; Güçlütürk et al., 2017). This raises a fundamental question: does the temporal structure of emotional content matter for how the brain represents emotion?

Recent self-supervised video foundation models offer a new lens for this question. V-JEPA2 (Assran et al., 2025) learns rich spatiotemporal representations from video without language supervision, encoding the unfolding dynamics of visual scenes across time. Unlike image-based models such as CLIP (Radford et al., 2021), which process individual frames independently, V-JEPA2 captures motion, temporal flow, and scene evolution — the very dimensions that define how many emotions are experienced. At the same time, Brain-JEPA (Kim et al., 2024) enables the extraction of subject-invariant whole-brain fMRI embeddings that capture shared neural geometry across individuals.

Here we ask: **(RQ A)** Does V-JEPA2's representational geometry align with the neural geometry of emotional experience? **(RQ B)** Does a temporal video foundation model explain neural emotion representations better than a static model, and for which emotion categories?

---

## Methods

**Dataset.** We used the Horikawa et al. (2020) dataset: 5 participants each viewed 2,196 short video clips selected to evoke diverse emotional experiences spanning 34 categories (Cowen & Keltner, 2017). Whole-brain fMRI responses were recorded at 3T (TR = 2s).

**Brain embeddings.** We extracted fMRI representations using Brain-JEPA (Kim et al., 2024), a whole-brain masked autoencoder pretrained on large-scale fMRI data that produces 768-dimensional subject-invariant embeddings. Cross-subject Pearson correlation of embeddings was *r* = 0.986 (mean across all subject pairs), confirming that Brain-JEPA captures strongly shared neural structure. We used the mean embedding across 5 subjects as our primary brain representation.

**Video model embeddings.**
- **V-JEPA2** (`facebook/vjepa2-vitg-fpc64-256`, ViT-Giant, 1408-dim): 16 uniformly sampled frames per video → mean-pooled over spatial tokens → single embedding per video.
- **CLIP** (`openai/clip-vit-base-patch32`, 512-dim): 8 uniformly sampled frames per video → per-frame visual projection → mean-pooled across frames → single embedding per video. CLIP processes each frame independently, with no temporal integration.

**RSA + CKA.** For each embedding set we computed a 2196×2196 representational similarity matrix (RSM) using pairwise cosine similarity (Kriegeskorte et al., 2008). Alignment between brain and model RSMs was measured using Centered Kernel Alignment (CKA; Kornblith et al., 2019), which is invariant to linear transformations and scales well to large stimulus sets.

For per-emotion analysis, we subsetted each RSM to stimuli labeled as belonging to each emotion category (binary labels; Horikawa et al., 2020) and recomputed CKA within each subset (23 categories with n ≥ 20 stimuli).

**Statistics.**
1. *Permutation test* (Mantel-style): 10,000 permutations of brain RSM rows/columns simultaneously → null distribution → p-value per model.
2. *Bootstrap 95% CI*: 10,000 stimulus resamplings with replacement.
3. *Paired bootstrap* for Δ(V-JEPA2 − CLIP): same bootstrap sample applied to both models → one-tailed p-value for H₀: Δ ≤ 0.

---

## Results

### Both models significantly align with neural emotion geometry

Both V-JEPA2 and CLIP showed significant alignment with Brain-JEPA's neural emotion geometry across all 2,196 stimuli (both p < 0.0001, permutation test; Figure 1). V-JEPA2 achieved higher CKA than CLIP:

| Model | CKA | 95% CI | p (permutation) |
|-------|-----|--------|-----------------|
| V-JEPA2 (temporal) | 0.128 | [0.117, 0.149] | < 0.0001 |
| CLIP (static) | 0.112 | [0.107, 0.128] | < 0.0001 |
| **Δ (V-JEPA2 − CLIP)** | **+0.017** | **[0.001, 0.030]** | **p = 0.017** |

The paired bootstrap test confirmed that V-JEPA2's advantage over CLIP is statistically significant (p = 0.017), despite the modest absolute difference. The 95% CI for Δ excludes zero, indicating that temporal video representations explain neural emotion geometry reliably beyond what static frame representations capture.

### Per-emotion alignment: Anxiety shows strongest temporal advantage

Per-emotion CKA analysis revealed substantial variation across emotion categories (Figure 2). V-JEPA2 alignment was significant in 20 of 23 analyzable categories (p < 0.05, permutation test), while CLIP was significant in 19/23. The temporal advantage of V-JEPA2 over CLIP was significant for **Anxiety** (Δ = +0.081, p = 0.038), with consistent positive trends for Awe (Δ = +0.036), Surprise (Δ = +0.036), Sympathy (Δ = +0.035), and Interest (Δ = +0.040; p = 0.081).

In contrast, static CLIP representations better explained neural geometry for **Aesthetic appreciation** (Δ = −0.061), **Excitement** (Δ = −0.066), and **Calmness** (Δ = −0.046) — emotions whose neural signatures may be more strongly tied to the content of individual visual frames than to temporal dynamics.

The highest absolute alignment for V-JEPA2 was observed for **Guilt** (CKA = 0.496), though the V-JEPA2 vs CLIP difference did not reach significance for this category (n = 23, p = 0.148).

---

## Discussion

We demonstrate that a temporal video foundation model (V-JEPA2) aligns significantly with the neural geometry of emotion as captured by a whole-brain fMRI foundation model (Brain-JEPA), and that this alignment exceeds that of a matched static model (CLIP). This is, to our knowledge, the first demonstration that temporal video representations explain neural emotion geometry better than static image representations at the whole-brain level.

The category-specific pattern is theoretically informative. The strongest temporal advantage appears for **Anxiety** — an emotion whose phenomenology is defined precisely by anticipation and temporal accumulation rather than instantaneous appraisal (Öhman, 2008; Bar, 2009). In contrast, emotions tied to visual scene content (Aesthetic appreciation, Excitement) are better explained by static representations. This double dissociation suggests that the temporal structure of emotional content is differentially encoded across emotion categories — a finding that is invisible to static models.

A key constraint of the current work is that Brain-JEPA is strongly subject-invariant (*r* = 0.986 cross-subject), meaning it captures shared neural geometry. Individual differences in emotional response — which prior work suggests exist especially for complex social emotions (Barrett, 2017; Finn et al., 2020) — are not accessible through this approach and remain an important direction for future work.

**Implications for Brain Tuning.** These results motivate a *Brain Tuning* approach (Scotti et al., 2024; Lu et al., 2024): fine-tuning V-JEPA2 using Brain-JEPA emotion geometry as a supervisory signal. The category-specific alignment profile provides a concrete hypothesis: fine-tuning should improve alignment most for emotions where temporal dynamics are neural-representationally significant (Anxiety, Awe, Surprise), while having smaller effects for frame-content-dominated emotions. The modest but reliable overall Δ also suggests that current temporal video models capture only a fraction of the variance in neural emotion geometry — leaving substantial room for alignment-based fine-tuning to improve.

---

## Figures

**Figure 1.** *Overall CKA alignment between video model RSMs and Brain-JEPA RSM.*
Bar chart: CKA ± 95% bootstrap CI for V-JEPA2 (temporal, blue) and CLIP (static, orange), both significantly above chance (permutation p < 0.0001). Δ = +0.017, 95% CI [0.001, 0.030], paired bootstrap p = 0.017.

**Figure 2.** *Per-emotion CKA profile across 23 emotion categories.*
Diverging bar chart showing Δ(V-JEPA2 − CLIP) for each emotion category, sorted from most positive (temporal advantage) to most negative (static advantage). Stars mark categories significant at p < 0.05 (paired bootstrap). Anxiety is the only category with significant temporal advantage.

---

## References

- Assran, M., et al. (2025). V-JEPA 2: Self-supervised video models enable understanding, prediction and planning. *arXiv preprint*.
- Bar, M. (2009). The proactive brain: memory for predictions. *Philosophical Transactions of the Royal Society B*, 364, 1235–1243.
- Barrett, L. F. (2017). *How Emotions Are Made: The Secret Life of the Brain.* Houghton Mifflin Harcourt.
- Conwell, C., et al. (2025). Affectless machines: visual models explain behavioral affect without emotional induction. *arXiv preprint*.
- Cowen, A. S., & Keltner, D. (2017). Self-report captures 27 distinct categories of emotion. *PNAS*, 114(38), E7900–E7909.
- Finn, E. S., et al. (2020). Idiosynchrony: From shared responses to individual differences during naturalistic neuroimaging. *NeuroImage*, 215, 116828.
- Güçlütürk, Y., et al. (2017). Reconstructing perceived faces from brain activations with deep adversarial neural decoding. *NeurIPS*, 30.
- Hasson, U., et al. (2010). Reliability of cortical activity during natural stimulation. *Trends in Cognitive Sciences*, 14(1), 40–48.
- Horikawa, T., et al. (2020). Characterization of neural representations of temporal structures in emotional experiences. *bioRxiv preprint*.
- Huth, A. G., et al. (2016). Natural speech reveals the semantic maps that tile human cerebral cortex. *Nature*, 532, 453–458.
- Kim, J., et al. (2024). Brain-JEPA: Brain foundation model with gradient-mask modeling for brain signals. *NeurIPS*, 37.
- Kornblith, S., et al. (2019). Similarity of neural network representations revisited. *ICML*.
- Kriegeskorte, N., et al. (2008). Representational similarity analysis — connecting the branches of systems neuroscience. *Frontiers in Systems Neuroscience*, 2, 4.
- Lindquist, K. A., et al. (2012). The brain basis of emotion: A meta-analytic review. *Behavioral and Brain Sciences*, 35(3), 121–143.
- Lu, Y., et al. (2024). MindBridge: A cross-subject brain decoding framework. *CVPR*.
- Öhman, A. (2008). Fear and anxiety: overlaps and dissociations. In *Handbook of Emotions* (3rd ed.).
- Radford, A., et al. (2021). Learning transferable visual models from natural language supervision. *ICML*.
- Scotti, P. S., et al. (2024). MindEye2: Shared-subject models enable fMRI-to-image with 1 hour of data. *ICML*.
- Tong, Z., et al. (2022). VideoMAE: Masked autoencoders are data-efficient learners for self-supervised video pre-training. *NeurIPS*, 35.
