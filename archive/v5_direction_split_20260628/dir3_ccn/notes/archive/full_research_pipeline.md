# Full Research Pipeline
## Do neural representations of emotion contain shared and individual-specific structures, and can transferring the shared geometry to an AI model improve emotion prediction?

---

## Data

- 2,181 emotionally evocative videos (Horikawa et al., 2020)
- Whole-brain fMRI, 5 subjects, preprocessed
- Emotion ratings: 34 emotion categories + 14 affective dimensions per video (Cowen & Keltner, 2017)

---

## Models

- Video encoder: V-JEPA2 (via TRIBE v2 backbone), CLIP as baseline
- Brain encoder: Brain-JEPA
- Brain-to-video alignment: TRIBE v2 Transformer (frozen) + subject block (trainable per subject)

---

## Figure 1: Individual-specific structure

**Question:** Are neural emotional representations fully individual-specific, as in pain (Lee et al., 2026)?

**Method:**

Train one subject block per subject using Brain-JEPA embeddings as target. For each subject, the TRIBE v2 Transformer remains frozen and only the subject block learns to map video input to that subject's fMRI response pattern.

**Analysis:**

Within-subject prediction accuracy is evaluated via leave-one-out cross-validation across videos. Cross-subject prediction is then performed for all pairwise combinations of the 5 subjects: the subject block trained on subject A is used to predict the fMRI responses of subject B. Pairwise RSA is computed between all subject block representations to quantify inter-subject similarity.

**Expected result:**

Cross-subject prediction is significantly worse than within-subject prediction, confirming individual specificity. However, unlike pain (Lee et al., 2026), prediction does not fail completely, suggesting that a shared structure exists alongside individual-specific variation.

---

## Figure 2: Shared structure

**Question:** Does a shared subspace exist across individual-specific representations, and does it capture emotion category structure?

**Method:**

PCA or CCA is applied across the 5 trained subject blocks to extract a shared subspace. The remaining variance after projecting out the shared subspace constitutes the individual residual for each subject.

Within the shared subspace, an RSM is computed across all 2,181 videos. The same is done within the individual residual. Both RSMs are organized by emotion category scores and by affective dimension scores (valence, arousal) separately.

CKA is computed between the shared subspace RSM and the video embedding RSM (V-JEPA2), and separately between the individual residual RSM and the video embedding RSM.

UMAP visualization is applied to both the shared subspace and the individual residual, with points colored by emotion category.

**Analysis:**

RSA between shared subspace RSM and emotion category labels vs affective dimension labels. RSA between individual residual RSM and the same labels. CKA between shared subspace and video embedding. CKA between individual residual and video embedding.

**Expected result:**

The shared subspace shows clear emotion category structure, replicating Horikawa et al. in a shared representational space across subjects. The individual residual is less structured and more person-specific. Video embeddings align more with the shared subspace than with the individual residual. Emotion categories explain more variance than valence/arousal in the shared subspace.

---

## Figure 3: Dimensionality of shared structure

**Question:** How many dimensions does the shared structure have, and does it converge to ~27?

**Experiment 1: Intrinsic dimensionality**

The intrinsic dimensionality of the shared subspace is estimated using explained variance curve elbow detection, participation ratio, and a nearest-neighbor-based intrinsic dimensionality estimator (e.g., TwoNN). This provides a data-driven answer to how many dimensions naturally emerge from the shared neural emotional geometry.

**Experiment 2: Dimension sweep**

The shared subspace is projected to k dimensions for k = 5, 10, 15, 20, 27, 34, 50, 100. For each k, three metrics are computed: downstream emotion task performance (valence/arousal regression, emotion category classification), CKA with the full brain RSM, and RSA correspondence with Cowen's 27 emotion label structure (behavior-based RSM from Cowen & Keltner, 2017).

**Experiment 3: Cross-level Mantel test**

With k fixed at 27, RSMs are computed for three levels: the behavioral space (Cowen's emotion ratings across 2,181 videos), the neural space (Horikawa fMRI shared subspace RSM), and the model space (V-JEPA2 video embedding RSM). Mantel tests are run between all pairs of RSMs to determine whether the three levels share the same geometric structure at k = 27.

**Expected result scenarios:**

| Scenario | Result | Interpretation |
|----------|--------|----------------|
| A (strong) | k=27 optimal across all metrics | 27 dimensions are the universal structure of emotion |
| B (realistic) | Plateau at k=20~30 | ~27-dim structure, consistent with Cowen & Keltner |
| C (informative null) | Optimal k differs from 27 | Behavioral and neural dimensionality diverge, raising further questions |

---

## Figure 4: Brain-guided transfer to AI model (Brain Tuning)

**Question:** Does transferring the shared neural geometry to an AI model improve emotion prediction, and are shared and individual structures functionally separable?

**Step 1: Shared Brain Tuning**

V-JEPA2 is fine-tuned using the shared subspace RSM as the target structure. Two losses are applied jointly. The RSM loss minimizes the Frobenius distance between the video embedding RSM and the brain shared subspace RSM across all video pairs. The contrastive loss pulls together videos from the same emotion category and pushes apart videos from different categories, using category labels derived from the shared subspace structure.

**Step 2: Personalized Brain Tuning**

On top of the Shared Brain-Tuned model, a lightweight subject-specific adapter is added per subject. Each adapter is trained using the individual subject block from Figure 1 as the target, with few parameters, capturing the individual-specific residual structure.

**Analysis:**

Four conditions are compared: baseline V-JEPA2, Shared Brain-Tuned model, Personalized Brain-Tuned model, and CLIP as a reference baseline. Evaluation metrics include CKA with the shared subspace RSM, CKA with individual subject block RSMs, cross-subject prediction accuracy (revisiting Figure 1 to test whether shared tuning improves generalization), and downstream emotion task performance including valence/arousal regression, emotion category classification, and affective video retrieval measured by Recall@K.

Qualitative analysis includes UMAP visualization of the emotion space before and after tuning, and identification of which emotion categories undergo the largest representational shift.

**Key hypotheses:**

Shared Brain Tuning improves alignment with the shared subspace and improves downstream emotion task performance. Personalized adapters further improve alignment with individual subject blocks. Cross-subject prediction remains poor even after Shared Brain Tuning, demonstrating that individual structure is preserved and not overwritten. This dissociation provides functional evidence that shared and individual structures are separable within neural emotional representations.

---

## Connecting narrative

Figure 1 establishes that neural emotional representations are partially individual-specific, unlike pain which is fully individual-specific (Lee et al., 2026). This partial specificity implies the existence of a shared structure.

Figure 2 identifies and characterizes this shared subspace, showing that emotion categories organize the shared structure while the individual residual is less structured.

Figure 3 asks how many dimensions this shared structure has, testing whether it converges to the ~27 dimensions found in behavioral data (Cowen & Keltner, 2017) and neural data (Horikawa et al., 2020).

Figure 4 tests whether this geometry can be transferred to an AI model to improve emotion prediction, and whether shared and individual structures remain functionally separable after the transfer.

---

## Overall claim

Neural emotional representations contain both shared and individual-specific structures. The shared structure converges to ~27 dimensions, consistent across behavioral, neural, and computational levels. Transferring this geometry to an AI model via Brain Tuning improves emotion prediction, while individual-specific structure remains intact. This suggests that ~27 dimensions reflect not a biological constraint but a computational necessity of emotional information processing.
