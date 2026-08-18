# EmoBrain Multimodal Alignment — Three Research Directions

## 0. Purpose of this note

This document consolidates three candidate research directions for improving the current **EmoBrainModel** beyond simple multimodal concatenation.

The current teacher/student design is:

```text
Teacher:
video + caption + brain + question
                ↓
              LLM
                ↓
             34-D z

Student / inference:
brain + question
       ↓
      LLM
       ↓
    34-D z
```

The present implementation converts each modality into the LLM hidden dimension and then concatenates the token segments:

```python
embeds = torch.cat(segs, dim=1)
pooled = self.backbone(embeds, mask)
prediction = self.head(pooled)
```

This is a valid baseline, but it contains almost no explicit inductive bias about **what information should be shared across brain, video, and language**. The LLM is expected to discover the relevant cross-modal structure almost entirely by itself.

The goal of the proposed work is therefore **not simply to add another multimodal fusion block**, but to design an alignment principle that is motivated by the structure of affective neuroscience and by the asymmetry of this training setup:

- **video and caption are privileged information available only during training**;
- **brain is the only informative modality available at final inference**;
- the final task is prediction of a **34-dimensional affective profile**;
- video and caption describe the external stimulus, whereas fMRI reflects the evoked neural response;
- therefore, the useful scientific question is not merely how to fuse modalities, but:

> **What cross-modal information should be transferred into the brain representation so that it remains useful when the privileged modalities disappear at inference?**

This note retains only three ideas that appear defensible after considering implementation compatibility, novelty, and positioning relative to existing multimodal alignment / emotion recognition / brain-decoding literature.

---

# 1. Current model and the central limitation

## 1.1 Current token pipeline

The current code produces four possible segments:

### Brain

```text
fMRI
 ↓
encoder
 ↓
brain_projector
 ↓
brain tokens
```

### Video

```text
video feature
 ↓
video_projector
 ↓
video tokens
```

### Caption

```text
caption
 ↓
tokenizer
 ↓
LLM text embedding
 ↓
caption tokens
```

### Question

```text
fixed question prompt
 ↓
tokenizer
 ↓
LLM text embedding
 ↓
question tokens
```

Teacher token order:

```text
video → caption → brain → question
```

Student token order:

```text
brain → question
```

Learnable segment start/end markers are already used, which solves the relatively local problem of telling the LLM **where each modality segment begins and ends**.

However, markers do not solve the deeper problem:

> They tell the model **which modality a token came from**, but they do not tell the model **which cross-modal correspondence is desirable for emotion decoding**.

For example, nothing explicitly encourages the representation of a threatening visual pattern to align with the part of the brain representation that reflects fear-related affect rather than with generic stimulus identity.

---

## 1.2 Why plain global alignment is also not enough

A naive next step would be to add a CLIP-style objective:

\[
b_i \approx v_i
\]

or:

\[
\mathrm{sim}(b_i, v_i) >
\mathrm{sim}(b_i, v_j).
\]

But this can align the wrong information.

Two stimuli can be:

- visually or semantically similar but affectively different, or
- visually very different but affectively similar.

Examples:

```text
Semantic similarity high, affective similarity low:
- a man running in triumph
- a man running away in fear
```

```text
Semantic similarity low, affective similarity high:
- a puppy playing
- a comedy scene
```

Therefore:

> **Cross-modal correspondence is not identical to affective correspondence.**

The proposed methods below are all attempts to make this distinction explicit.

---

# 2. Design principle for all three ideas

The most important constraint is the teacher/student asymmetry.

A method is useful only if privileged video/caption information modifies the representation learned by:

```text
fMRI → encoder → brain_projector
```

because the final test condition is:

```text
brain + question only
```

Therefore, a visually sophisticated teacher-only fusion block is not automatically useful.

The alignment objective should backpropagate into the brain encoder/projector so that the student representation itself changes.

This leads to the following general form:

\[
L =
L_{\mathrm{task}}
+
\lambda L_{\mathrm{alignment}},
\]

where the alignment term is active during multimodal teacher training but is designed specifically to improve the brain representation used by the student.

---

# 3. Candidate 1 — Residual Affective Structure Alignment

## 3.1 One-sentence idea

> **Do not align brain and privileged modalities according to their raw similarity; align only the part of their relational structure that cannot be explained by generic visual or linguistic stimulus similarity.**

This is currently the most conservative and practically promising candidate.

---

# 3.2 Motivation

The original problem with direct multimodal alignment is that it can reward the model for learning **stimulus identity** instead of **affective structure**.

Suppose stimulus \(i\) and stimulus \(j\) contain similar actors, objects, or scenes.

Then:

\[
\mathrm{sim}(v_i, v_j)
\]

can be high even if the affective states are very different.

A brain representation trained to mimic this geometry may therefore become a better stimulus-semantic representation without becoming a better affect representation.

This issue is particularly relevant to naturalistic video-fMRI.

The neuroscience motivation is that emotion-related neural structure is typically analyzed while considering potential visual and semantic covariates. In other words, one attempts to identify neural representational structure that cannot be trivially reduced to low-level stimulus similarity or generic semantic content.

The proposed method turns that analysis principle into a **training objective**.

---

# 3.3 Core hypothesis

Let:

- \(b_i\): brain representation for stimulus \(i\)
- \(a_i\): affective teacher representation
- \(v_i\): visual stimulus representation
- \(c_i\): caption / semantic representation

The hypothesis is:

> The useful signal to transfer from the privileged multimodal teacher to the brain student is the **affective relational structure that remains after accounting for generic visual and linguistic similarity**.

Therefore, rather than maximizing:

\[
\mathrm{corr}(D_B, D_A),
\]

we maximize a **partial / residual representational correspondence**.

---

# 3.4 Representational geometry

For a batch of \(B\) stimuli, define pairwise distance matrices:

\[
D_B(i,j) = 1 - \cos(b_i, b_j)
\]

\[
D_A(i,j) = 1 - \cos(a_i, a_j)
\]

\[
D_V(i,j) = 1 - \cos(v_i, v_j)
\]

\[
D_C(i,j) = 1 - \cos(c_i, c_j).
\]

Vectorize the upper triangular parts:

\[
d_B,\quad d_A,\quad d_V,\quad d_C.
\]

Define nuisance relational structure:

\[
N =
\begin{bmatrix}
d_V & d_C
\end{bmatrix}.
\]

Estimate the part of brain and affective-teacher geometry predictable from nuisance structure:

\[
\hat d_B = f_B(N)
\]

\[
\hat d_A = f_A(N).
\]

Then calculate residual geometry:

\[
r_B = d_B - \hat d_B
\]

\[
r_A = d_A - \hat d_A.
\]

The alignment loss becomes:

\[
L_{\mathrm{RASA}}
=
1 -
\mathrm{corr}(r_B, r_A).
\]

A simple linear residualization is sufficient for the first implementation.

---

# 3.5 Why not simply use RSA?

A major literature-positioning issue is that plain RSA-style brain-model alignment is **not sufficient novelty**.

Prior work has already aligned neural representational similarity matrices and visual-model representations for emotion-related video processing. More generally, recent multimodal emotion recognition literature has also introduced consistency constraints over sample-level geometry.

Therefore the claim must **not** be:

> We align the similarity structure of brain and video representations.

That is too close to existing work.

The proposed novelty is instead:

> **We explicitly separate affective correspondence from generic cross-modal stimulus correspondence and align only the residual affective structure.**

In short:

```text
Existing:
brain geometry ↔ model geometry
```

versus:

```text
Proposed:
                       visual similarity ─┐
                                         ├─ remove
brain geometry --------------------------┤
                                         │
teacher affective geometry --------------┤
                                         ├─ residual affective alignment
                       language similarity┘
```

The object being aligned is different.

---

# 3.6 Partial rather than complete residualization

A reviewer can reasonably object:

> Visual and semantic information is not merely nuisance; these features are themselves part of what produces emotion.

That is correct.

Therefore complete removal should not be assumed to be optimal.

A more flexible formulation is:

\[
r = d - \alpha \hat d,
\]

with:

\[
\alpha \in [0,1].
\]

Interpretation:

```text
alpha = 0
    ordinary relational alignment

alpha ≈ 0.25–0.75
    suppress stimulus-semantic structure while retaining some grounding

alpha = 1
    full residual alignment
```

This converts a potential criticism into an informative ablation.

If intermediate \(\alpha\) performs best, the scientific interpretation becomes:

> Emotion representations remain grounded in stimulus semantics, but cross-modal supervision benefits when non-affective semantic similarity is partially suppressed.

That is a stronger story than simply claiming semantics are nuisance.

---

# 3.7 How to implement this in the current code

This method requires almost no change to the current inference architecture.

The current segment embeddings already exist before concatenation:

```python
brain_emb
video_emb
caption_emb
question_emb
```

Add pooled representations:

```python
brain_repr = masked_pool(brain_emb, brain_mask)
video_repr = masked_pool(video_emb, video_mask)
caption_repr = masked_pool(caption_emb, caption_mask)
```

The teacher affect representation can be defined as either:

### Option A — teacher backbone representation

```text
video + caption + brain + question
              ↓
             LLM
              ↓
       teacher hidden state
              ↓
       affective projector
```

### Option B — privileged-only affect representation

```text
video + caption + question
          ↓
         LLM
          ↓
   affective projector
```

Option B is conceptually cleaner because the teacher target is not contaminated by the same brain representation that it supervises.

Recommended initial implementation:

```text
teacher affect = privileged video + caption representation
```

or a lightweight projector on the teacher hidden state.

Then compute `L_RASA` only during training.

The final student forward remains unchanged:

```text
brain → brain_projector → question → LLM → head
```

---

# 3.8 Minimal training architecture

```text
                           ┌──────── task loss ───────→ 34-D z
                           │
brain → encoder → projector┼→ concat → LLM
            │              │
            │              └──────────────────────────
            │
            ↓
        brain_repr
            │
            │ residual affect geometry loss
            ↕
       teacher_affect_repr
            ↑
            │
       video + caption

video_repr   ───────┐
                    ├── nuisance relational geometry
caption_repr ───────┘
```

---

# 3.9 Recommended loss

First prototype:

\[
L =
L_{\mathrm{z-regression}}
+
\lambda_{\mathrm{RASA}}
L_{\mathrm{RASA}}.
\]

Avoid adding many auxiliary losses initially.

The point of the first experiment is to determine whether **affect-selective geometry supervision itself** improves brain-only inference.

---

# 3.10 Important implementation details

## Pooling

For each modality, begin with simple masked mean pooling:

\[
h =
\frac{\sum_t m_t x_t}
{\sum_t m_t}.
\]

A more complicated attention pooling layer can be explored later, but it should not be introduced in the first experiment because it confounds the contribution.

---

## Distance function

Start with cosine distance.

Possible ablations later:

- cosine distance
- Euclidean distance after normalization
- correlation distance

---

## Residualization

A linear ridge regression is probably sufficient.

Within each batch:

```text
[d_V, d_C] → predict d_B
[d_V, d_C] → predict d_A
```

Potential concern: estimating a regression per batch can be noisy.

Alternative implementation:

- projection-matrix residualization;
- running covariance estimates;
- memory bank of representations.

For the first experiment, a differentiable projection residualization can be used.

---

## Batch-size issue

Pairwise geometry yields approximately:

\[
B(B-1)/2
\]

pairs.

Small batches therefore provide noisy estimates.

Possible solutions:

1. larger effective batch through gradient accumulation;
2. representation memory queue;
3. EMA teacher feature bank;
4. pair sampling across recent batches.

The first implementation should preferably test whether the existing batch size is already adequate before introducing a memory bank.

---

# 3.11 Key ablations

A convincing experiment should include:

### A. No alignment

```text
current concat baseline
```

### B. Direct feature alignment

```text
brain ↔ video
```

### C. Generic relational alignment

\[
1-\mathrm{corr}(d_B,d_A)
\]

### D. Residual affective structure alignment

\[
1-\mathrm{corr}(r_B,r_A)
\]

### E. Residualization strength

\[
\alpha = 0,\;0.25,\;0.5,\;0.75,\;1.0
\]

### F. Nuisance source

```text
visual only
caption only
visual + caption
```

These ablations directly test the central scientific claim rather than merely showing that another loss improves performance.

---

# 3.12 What can be claimed if it works?

A defensible claim:

> **Generic cross-modal alignment is not necessarily optimal for brain emotion decoding because it conflates affective correspondence with stimulus-semantic correspondence. Explicitly controlling for visual and linguistic similarity produces a more affect-selective alignment signal and improves brain-only decoding.**

A shorter paper-style formulation:

> **We align modalities by affective structure rather than by raw cross-modal similarity.**

Potential contribution statement:

> We introduce a residual representational alignment objective that isolates affect-relevant cross-modal structure from generic visual and linguistic stimulus similarity.

---

# 3.13 Main reviewer attacks

## Attack 1 — “Semantics are part of affect”

Valid.

Response:

- use partial residualization rather than assuming complete removal;
- show \(\alpha\) ablation;
- interpret the optimum rather than assuming nuisance independence.

---

## Attack 2 — “This is just RSA with extra regression”

The response must focus on the **problem formulation**, not the mathematical novelty of correlation.

The novelty is:

```text
cross-modal similarity
        ≠
affective similarity
```

and therefore privileged supervision should be **affect-selective**.

The relevant comparison is not just a different loss implementation but whether controlling stimulus semantics changes brain-only decoding.

---

## Attack 3 — “Why not use the 34-D labels themselves as the target geometry?”

Using:

\[
D_A(i,j)=d(z_i,z_j)
\]

would be easy, but weakens the contribution.

It risks reducing the method to label-aware metric learning.

Prefer an affective **teacher representation** learned from privileged modalities and use the 34-D labels only for the main task.

---

# 3.14 Overall assessment

```text
Implementation difficulty:      Low
Scientific motivation:          Strong
Novelty potential:              Medium–High
Literature separation:          Good if residualization is central
Empirical risk:                 Low–Medium
Compatibility with current code: Excellent
```

This is the recommended **first experiment**.

---

# 4. Candidate 2 — Sensory-Grounded Affective Residual

## 4.1 One-sentence idea

> **Use caption as a semantic baseline, isolate what video contributes beyond language, retain only the affect-predictive part of that visual residual, and distill that information into the brain representation.**

This is more ambitious than Candidate 1 and potentially provides the strongest scientific story.

---

# 4.2 Motivation

The current teacher treats video and caption largely as parallel privileged modalities:

```text
video + caption + brain + question
```

But video and caption are not independent sensors.

They describe the **same external stimulus** and can be highly redundant.

For example:

```text
Caption:
"A man approaches another man."
```

The video may additionally contain:

```text
- dark lighting
- facial tension
- rapid motion
- aggressive posture
- timing
- prosody / audiovisual context
```

These details can carry affective information not explicitly encoded in the caption.

The key idea is therefore not:

> “Video is another modality, align it with brain.”

Instead:

> **What affectively relevant information does direct sensory access to the video provide beyond what can already be inferred from language?**

This gives the privileged teacher a much more precise role.

---

# 4.3 Neuroscience / affective-computation motivation

Recent work on the same broad class of emotional-video resources reported an important observation:

- language-only representations built from textual descriptions show meaningful affective structure;
- multimodal/video-grounded language-model representations show stronger correspondence with neural affective representations.

The interpretation is that direct sensory grounding contributes information beyond language-derived conceptual affect.

This motivates converting an observational result into a learning principle:

> If video supplies affective information beyond language that is especially brain-relevant, isolate this information and use it as the privileged signal for brain training.

---

# 4.4 Why plain `video - caption` is not enough

A naive residual:

\[
r_V = v - g(c)
\]

does **not** automatically represent sensory affect.

It contains everything omitted from the caption:

```text
camera motion
background texture
object details
lighting
color
irrelevant visual content
etc.
```

Therefore the method requires two stages.

---

# 4.5 Stage 1 — Remove language-predictable video information

Let:

- \(v_i\): video embedding
- \(c_i\): caption embedding

Train a predictor:

\[
\hat v_i = g(c_i).
\]

Then:

\[
r_i^{V|C} =
v_i - \hat v_i.
\]

Interpretation:

> visual information not predictable from the caption representation.

This is a **conditional visual residual**, not yet an affective residual.

---

# 4.6 Stage 2 — Select only affect-predictive residual information

Pass the residual through a low-rank affect bottleneck:

\[
q_i =
A(r_i^{V|C})
\]

where:

\[
q_i \in \mathbb{R}^k,
\quad k \ll D.
\]

Require this representation to predict the 34-D affective target:

\[
\hat z_i =
W q_i
\]

\[
L_{\mathrm{aff-res}}
=
\|\hat z_i-z_i\|^2.
\]

This forces the low-dimensional residual representation to preserve information useful for affect prediction rather than arbitrary visual detail.

The result is intended to approximate:

\[
q_i
\approx
\text{affect-predictive information in video not predictable from caption}.
\]

This quantity is the **sensory-grounded affective residual**.

---

# 4.7 Distill this residual into brain

Obtain a corresponding brain representation:

\[
q_i^B =
A_B(b_i).
\]

Then align:

\[
q_i^B
\leftrightarrow
\mathrm{sg}(q_i).
\]

Possible loss:

\[
L_{\mathrm{SGAR}}
=
1-
\cos(q_i^B,q_i)
\]

or MSE after normalization.

A relational version is also possible:

\[
L_{\mathrm{SGAR-rel}}
=
1-
\mathrm{corr}
(D(q^B), D(q)).
\]

The first prototype should likely use simple feature alignment because Candidate 1 already tests the relational hypothesis separately.

---

# 4.8 Architecture

```text
 Caption
    │
    ▼
caption embedding
    │
    └──────→ predict video embedding
                  │
Video ────────────┤
embedding          ▼
               residual
          V - E[V | Caption]
                  │
                  ▼
          affective bottleneck
                  │
                  ├── predict 34-D z
                  │
                  ▼
        sensory affect teacher
                  │
                  │ privileged distillation
                  ↕
             brain bottleneck
                  ↑
Brain → encoder → projector
```

The original teacher fusion path can remain:

```text
video + caption + brain + question → LLM → 34-D
```

Thus the new module is primarily a **training-time privileged regularizer**.

---

# 4.9 How it fits the current code

Before:

```python
elif seg == "video":
    emb = self.video_projector(video)
```

and:

```python
elif seg == "caption":
    emb, m = self._text_segment(...)
```

Add separate pooled versions:

```python
video_repr = masked_pool(video_emb)
caption_repr = masked_pool(caption_emb)
brain_repr = masked_pool(brain_emb)
```

Then modules:

```python
caption_to_video
sensory_residual_projector
sensory_affect_head
brain_affect_projector
```

Conceptually:

```python
pred_video = caption_to_video(caption_repr)
visual_residual = video_repr - pred_video

teacher_aff = sensory_residual_projector(visual_residual)
teacher_aff_z = sensory_affect_head(teacher_aff)

brain_aff = brain_affect_projector(brain_repr)

loss_residual_pred = mse(teacher_aff_z, z_target)
loss_distill = cosine_loss(brain_aff, teacher_aff.detach())
```

The student inference path does **not** require video or caption.

---

# 4.10 Important training detail — prevent trivial solutions

If `caption_to_video` and the residual branch are trained naively together, the system can potentially manipulate the decomposition.

Possible stabilization:

### Phase A

Train / initialize `caption_to_video` to predict video embeddings.

Then freeze it or use a much smaller learning rate.

### Phase B

Train the affect residual branch and brain distillation.

Alternative:

use stop-gradient carefully:

\[
r_V = \mathrm{sg}(v) - g(c)
\]

for the predictor objective, but retain the correct gradient path for the affective branch.

The exact gradient routing should be tested carefully.

---

# 4.11 Why this is not generic shared/private decomposition

Existing multimodal emotion work already decomposes representations into:

```text
shared component
private component
```

Therefore that cannot be the claim.

The proposed quantity is much more specific:

\[
V_{\mathrm{sensory-affective}}
=
\operatorname{AffectRelevant}
\left[
V - E(V|C)
\right].
\]

The private component is defined by two conditional criteria:

1. **not predictable from language**, and
2. **predictive of affect**.

This is not simply “video-private information.”

It is:

> **affectively useful sensory information beyond language**.

That distinction is crucial to the novelty.

---

# 4.12 Caption leakage / shortcut problem

This method forces us to confront an important dataset issue.

The current code explicitly notes:

> Affect neutrality is not assumed.

If captions contain words such as:

```text
terrified
joyful
angry
sad
romantic
```

then caption representations can directly reveal the target affect.

This could create a shortcut in the teacher.

Therefore the following analyses are important:

### Caption-only baseline

```text
caption → 34-D
```

### Emotion-word-masked caption

Remove / mask explicit affective vocabulary.

### Original caption

Compare both.

If original captions are extremely predictive but masked captions remain useful, this can distinguish generic semantic grounding from direct emotion-word leakage.

This analysis is important for the whole project, not only Candidate 2.

---

# 4.13 Strong validation test

To support the interpretation that the residual is affective rather than generic omitted visual content:

Test whether the learned sensory residual:

```text
retains:
    emotion prediction

but loses:
    generic visual semantics / object identity
```

For example, compare linear probes on:

- 34-D affect;
- scene category;
- object / CLIP semantic embedding;
- generic caption retrieval.

The stronger the dissociation, the stronger the scientific interpretation.

---

# 4.14 Critical ablations

### A. Direct video alignment

\[
b \leftrightarrow v
\]

### B. Video residual only

\[
b \leftrightarrow [v-g(c)]
\]

### C. Affect-selected video residual

\[
b \leftrightarrow A[v-g(c)]
\]

### D. Caption-only privileged teacher

### E. Full video + caption teacher

### F. Original caption vs emotion-word-masked caption

The key expected result is:

```text
direct video alignment       < affect-selected sensory residual
```

not merely:

```text
some auxiliary loss > baseline
```

---

# 4.15 What can be claimed if it works?

A strong claim:

> **Privileged vision is most useful for brain emotion decoding not when its full representation is aligned to fMRI, but when we isolate the affectively predictive sensory information that language fails to explain.**

Shorter:

> **What vision adds beyond words is the useful privileged signal.**

Potential contribution language:

> We introduce a conditional sensory-affective distillation objective that extracts affect-predictive visual information beyond language and transfers it into the brain representation.

This is substantially more specific than saying “we use video-text-brain multimodal distillation.”

---

# 4.16 Main reviewer attacks

## Attack 1 — “Why is `video - caption` sensory affect?”

It is not.

The affect bottleneck and affect prediction objective are essential.

Without them, the method should not be presented as sensory-affective residual learning.

---

## Attack 2 — “The residual may simply contain omitted scene semantics”

Address through:

- semantic probes;
- low-rank bottleneck;
- affect prediction constraint;
- comparison to direct residual.

---

## Attack 3 — “Caption contains emotion words and therefore makes the residual artificial”

Must analyze caption shortcut explicitly.

This is a real methodological issue rather than a cosmetic ablation.

---

## Attack 4 — “This is just privileged-modality distillation”

Generic privileged KD is already well studied.

The novelty is **not that video is a teacher**.

The novelty must be framed as:

> **what is distilled** = affect-predictive sensory information conditionally independent of language.

---

# 4.17 Overall assessment

```text
Implementation difficulty:       Medium
Scientific motivation:           Very strong
Novelty potential:               Medium–High / High if validated well
Literature separation:           Good if conditional affect residual is central
Empirical risk:                  Medium–High
Compatibility with current code: Very good
```

This is the **high-risk / high-reward** candidate.

If it produces a strong result, it may provide the best paper story of the three.

---

# 5. Candidate 3 — Cross-Subject Consensus-Gated Alignment

## 5.1 One-sentence idea

> **Privileged stimulus modalities should supervise only the component of brain representation reproducibly evoked across subjects, rather than forcing the entire individual brain representation to align with video and text.**

This candidate exploits the fact that video/caption are stimulus-level information whereas fMRI is subject-specific.

---

# 5.2 Motivation

For stimulus \(i\), suppose several subjects watched the same clip:

\[
b_{i,1},
b_{i,2},
\dots,
b_{i,S}.
\]

But there is only one:

\[
v_i
\]

and one:

\[
c_i.
\]

Therefore aligning every individual representation directly:

\[
b_{i,s} \leftrightarrow v_i
\]

implicitly assumes that **all variation in the individual brain representation should correspond to stimulus information**.

This is not reasonable.

The individual brain representation contains:

```text
stimulus-locked response
+
subject anatomy
+
idiosyncratic neural response
+
measurement noise
+
possibly subject-specific affective variation
```

Video and caption cannot explain the subject-specific components.

Therefore, they should not be allowed to supervise those components indiscriminately.

---

# 5.3 Core hypothesis

Decompose:

\[
b_{i,s}
=
s_i + r_{i,s},
\]

where:

- \(s_i\): stimulus-reproducible / cross-subject consensus component
- \(r_{i,s}\): individual residual component

Privileged modalities should align primarily with:

\[
s_i,
\]

not with the full:

\[
b_{i,s}.
\]

---

# 5.4 Leave-one-subject-out consensus

A simple estimate:

\[
\mu_i =
\frac{1}{S}
\sum_s b_{i,s}.
\]

However, aligning \(b_{i,s}\) to a consensus that contains itself can create leakage / triviality.

Better:

\[
\mu_{i,-s}
=
\frac{1}{S-1}
\sum_{s' \neq s} b_{i,s'}.
\]

This is the leave-one-subject-out consensus.

Conceptually:

```text
subject 1 brain ─┐
subject 2 brain ─┼────→ stimulus consensus
subject 3 brain ─┤             │
subject 4 brain ─┘             │
                               ↕
                        video / caption
```

For subject \(s\):

```text
other subjects
      ↓
consensus representation
      ↓
defines the neural component privileged stimulus information is allowed to supervise
```

---

# 5.5 Why “consensus-gated” rather than ordinary subject alignment?

Cross-subject fMRI alignment itself is not novel.

There is extensive work on:

- shared latent spaces;
- hyperalignment;
- multi-subject visual decoding;
- subject adapters;
- stimulus-level semantic alignment.

Therefore the contribution cannot be:

> We learn subject-invariant brain representations.

Instead:

> **Cross-subject consensus is used only as a gate defining which part of the neural representation is eligible for privileged cross-modal alignment.**

The individual representation can still retain private information for prediction.

That distinction is crucial.

---

# 5.6 Possible implementation A — explicit shared/private decomposition

Project brain representation into:

\[
s_{i,s} = P_s(b_{i,s})
\]

\[
r_{i,s} = P_r(b_{i,s}).
\]

Train \(s_{i,s}\) toward leave-one-subject consensus:

\[
L_{\mathrm{cons}}
=
1-\cos(
s_{i,s},
\mathrm{sg}(\mu_{i,-s})
).
\]

Then multimodal alignment only uses \(s_{i,s}\):

\[
L_{\mathrm{align}}
=
L(
s_{i,s},
a_i
).
\]

The final prediction can still use:

\[
[s_{i,s};r_{i,s}]
\]

or the original brain token representation.

---

# 5.7 Possible implementation B — reliability weight instead of decomposition

A lighter version estimates how reproducible the sample is across subjects.

For each clip:

\[
\rho_i
=
\mathrm{sim}
(
b_{i,s},
\mu_{i,-s}
).
\]

Then weight privileged alignment:

\[
L_{\mathrm{align}}
=
\sum_i
\rho_i
L(b_i,a_i).
\]

Interpretation:

> Clips with reproducible neural responses receive stronger stimulus-based alignment; low-consensus samples are not forced strongly toward the privileged modality.

This version is easier to implement but probably weaker as a standalone methodological contribution.

---

# 5.8 Required data-loader changes

Unlike Candidates 1 and 2, this idea cannot be implemented solely inside `EmoBrainModel`.

The dataloader must expose:

```python
clip_id
subject_id
```

and preferably construct batches containing repeated clips across subjects.

Possible strategies:

### Strategy A — grouped batching

```text
batch =
multiple clips × multiple subjects per clip
```

Best conceptually, but may reduce sampling flexibility.

### Strategy B — memory bank

Maintain:

```text
clip_id → EMA consensus brain representation
```

Then each subject sample can retrieve the current consensus.

### Strategy C — offline consensus

If the brain encoder is frozen, consensus can be precomputed.

But if the encoder is trainable, offline consensus becomes stale and is less desirable.

---

# 5.9 Why target provenance matters

This idea has an important conceptual caveat.

If the 34-D target is a **stimulus-level group rating** rather than each participant's self-reported emotion, then suppressing individual variation may naturally improve performance.

A reviewer can reasonably say:

> The target itself is stimulus-level, so a cross-subject consensus representation is simply better matched to the label definition.

That is not necessarily a flaw, but it changes the claim.

Avoid:

> individualized emotion decoding.

Prefer:

> **stimulus-evoked affect decoding under cross-subject neural variability.**

The method is most defensible if the project explicitly studies generalization across subjects.

---

# 5.10 Important ablations

### A. Standard direct multimodal alignment

\[
b_{i,s} \leftrightarrow a_i
\]

### B. Subject-invariant brain representation only

No multimodal gate.

### C. Consensus-weighted alignment

### D. Explicit consensus/private decomposition

### E. Leave-one-subject-out vs including current subject

### F. Within-subject vs cross-subject evaluation

The key evidence should be that consensus-gated alignment improves **cross-subject generalization**, not merely average training performance.

---

# 5.11 What can be claimed if it works?

A careful claim:

> **Stimulus-level privileged modalities should supervise the reproducible stimulus-locked component of fMRI, rather than collapsing subject-specific neural variation into a common multimodal space.**

Possible contribution language:

> We introduce consensus-gated privileged alignment, where cross-subject neural reproducibility determines which components of individual fMRI representations are aligned to stimulus modalities.

---

# 5.12 Main reviewer attacks

## Attack 1 — “Cross-subject shared representations are old”

Correct.

Therefore never claim subject-invariant representation learning itself as the novelty.

The novelty is the **role of consensus as a privileged-alignment gate**.

---

## Attack 2 — “The label is stimulus-level, so your result is expected”

Also valid.

This method should be framed around cross-subject decoding and stimulus-evoked affect.

If subject-specific affect labels are unavailable, avoid overclaiming individuality.

---

## Attack 3 — “Consensus may erase meaningful individual affect”

Yes.

Therefore:

- do not replace the entire brain representation with the consensus;
- only gate privileged alignment;
- retain a private path if necessary.

---

# 5.13 Overall assessment

```text
Implementation difficulty:        Medium–High
Scientific motivation:            Strong
Novelty potential:                Medium
Literature separation:            Conditional but defensible
Empirical risk:                   High
Compatibility with current code:  Requires data-pipeline changes
```

This candidate is most useful if **cross-subject generalization becomes a core paper axis**.

Otherwise it may add unnecessary complexity.

---

# 6. Comparison of the three ideas

| Criterion | Residual Affective Structure Alignment | Sensory-Grounded Affective Residual | Cross-Subject Consensus-Gated Alignment |
|---|---|---|---|
| Main question | What relational structure should modalities share? | What useful information does video add beyond language? | Which part of individual fMRI should privileged modalities supervise? |
| Main nuisance addressed | Generic visual / semantic similarity | Video-caption redundancy | Subject-specific neural variability |
| Requires LLM architecture change | No | No | No |
| Requires dataloader change | Minimal | Minimal | Yes |
| Changes inference path | No | No | No |
| Directly improves brain representation | Yes | Yes | Yes |
| Scientific specificity | High | Very high | High |
| Novelty risk | Moderate | Moderate but potentially strong | Moderate |
| Engineering risk | Low | Medium | High |
| Best use | First method to test | Strong final story if successful | Cross-subject extension |

---

# 7. Recommended research sequence

## Phase 1 — Establish the simplest meaningful baseline

Keep the current architecture exactly as-is:

```text
teacher:
video + caption + brain + question → LLM → 34-D

student:
brain + question → LLM → 34-D
```

Evaluate:

- teacher performance;
- brain-only student performance;
- caption-only predictability;
- video-only predictability;
- brain-only performance by subject;
- cross-subject generalization if applicable.

This determines how much privileged information exists to transfer.

---

## Phase 2 — Implement Candidate 1 first

Reason:

- minimal architecture change;
- cleanest ablation;
- directly tests the central idea that affective alignment differs from generic multimodal alignment;
- low engineering cost.

Recommended comparison:

```text
1. concat baseline
2. + direct feature alignment
3. + generic relational alignment
4. + residual affective structure alignment
```

If Candidate 1 fails to outperform generic alignment, the more complicated proposals should be reconsidered before expanding the architecture.

---

## Phase 3 — Add Candidate 2 if Candidate 1 shows a signal

Test:

```text
video
vs
video residual beyond caption
vs
affect-selected video residual beyond caption
```

The decisive question:

> Does the affect-selected sensory residual provide a better privileged teacher for brain than the full video embedding?

If yes, this becomes a strong main contribution.

---

## Phase 4 — Consider Candidate 3 only if cross-subject generalization is central

Candidate 3 should not be added merely to increase method complexity.

Use it if:

- multiple subjects viewed the same clips;
- cross-subject generalization is important;
- current direct alignment appears to collapse subject variability;
- the paper wants to make a neuroscience claim about stimulus-reproducible versus individual neural components.

---

# 8. Potential combined method

The strongest eventual method may combine Candidates 1 and 2 rather than use all three.

## Sensory-Residual Affective Alignment

First isolate:

\[
V_{\mathrm{sens-aff}}
=
\operatorname{AffectRelevant}
\left[
V - E(V|C)
\right].
\]

This identifies:

> affectively predictive sensory information provided by video beyond language.

Then align the brain to its **affective relational structure**, while controlling generic stimulus semantics:

\[
L =
1 -
\mathrm{corr}
\left(
D_B \mid D_{\mathrm{semantic}},
D_{V_{\mathrm{sens-aff}}}
\mid D_{\mathrm{semantic}}
\right).
\]

Conceptually:

```text
Caption ───────────────┐
                       │ explain predictable visual semantics
Video ─────────────────┤
                       ↓
             visual residual beyond language
                       ↓
              affective bottleneck
                       ↓
       sensory-grounded affective teacher
                       │
                       │ remove generic stimulus geometry
                       ↓
          affect-selective relational signal
                       │
                       ↕
              brain representation
                       ↓
                  brain-only LLM
                       ↓
                    34-D z
```

The resulting paper claim becomes coherent:

> **Not all cross-modal information is useful for brain emotion decoding. We isolate the sensory-grounded affective information contributed by privileged video beyond language and align brain representations to affective structure rather than generic stimulus similarity.**

This is substantially more specific than:

```text
multimodal concatenation
cross-attention
contrastive alignment
generic Q-Former
generic knowledge distillation
```

---

# 9. Ideas deliberately NOT used as the primary novelty

Several initially plausible directions should be treated as baselines or auxiliary components rather than main contributions.

---

## 9.1 Emotion-query / Q-Former bottleneck

Possible:

```text
34 emotion queries
      ↓
brain / video / caption cross-attention
```

This is potentially useful architecturally.

However:

- Q-Former-style modality querying is established;
- class/prototype queries are common;
- label-specific multimodal emotion representations already exist.

Therefore:

> useful module, weak standalone novelty.

It may be added later if required for optimization or interpretability, but should not be the core paper claim unless a substantially stronger emotion-specific principle is developed.

---

## 9.2 Generic contrastive alignment

```text
brain ↔ video
brain ↔ caption
```

Already heavily explored in multimodal learning and brain-language/image alignment.

Use as a baseline only.

---

## 9.3 Generic representational geometry alignment

```text
RSM_brain ↔ RSM_model
```

Too close to prior RSA-based neural-model alignment and recent multimodal structure-consistency methods.

Candidate 1 survives specifically because it aligns **residual affective structure**, not raw geometry.

---

## 9.4 Generic shared/private representation

```text
shared
+
modality-private
```

Well established in multimodal sentiment / emotion modeling.

Candidate 2 survives because the private quantity is not arbitrary:

\[
\operatorname{AffectRelevant}
[V-E(V|C)].
\]

---

## 9.5 Plain teacher→student distillation

```text
multimodal teacher → brain-only student
```

Privileged-information distillation is already a large literature.

The contribution must therefore specify **what privileged information is distilled and why**.

---

## 9.6 Plain teacher-minus-student residual distillation

Distilling the prediction correction contributed by privileged modalities is an attractive idea, but closely related forms of privileged residual / corrective distillation have already appeared.

Use only as a baseline or auxiliary loss unless a more domain-specific formulation is developed.

---

# 10. Suggested initial code organization

A clean implementation could keep `EmoBrainModel` simple and move alignment objectives to separate modules.

For example:

```text
project/code/fusion/
    model.py
    prompt.py

    alignment/
        pooling.py
        rasa.py
        sensory_residual.py
        consensus.py
```

---

## 10.1 Suggested model outputs during training

Instead of returning only prediction:

```python
return self.head(pooled)
```

allow optional feature return:

```python
return {
    "pred": pred,
    "brain_tokens": brain_emb,
    "video_tokens": video_emb,
    "caption_tokens": caption_emb,
    "brain_repr": brain_repr,
    "video_repr": video_repr,
    "caption_repr": caption_repr,
    "teacher_repr": teacher_repr,
}
```

At inference:

```python
return pred
```

or preserve API compatibility with an option:

```python
forward(..., return_features=False)
```

---

# 11. Example first implementation plan for Candidate 1

## Step 1

Add masked pooling utility:

```python
def masked_mean(x, mask):
    w = mask.unsqueeze(-1).to(x.dtype)
    return (x * w).sum(1) / w.sum(1).clamp_min(1.0)
```

---

## Step 2

Expose:

```python
brain_repr
video_repr
caption_repr
teacher_repr
```

during teacher training.

---

## Step 3

Build pairwise cosine distance:

```python
def pairwise_cosine_distance(x):
    x = torch.nn.functional.normalize(x, dim=-1)
    return 1 - x @ x.T
```

---

## Step 4

Extract upper triangle.

```python
idx = torch.triu_indices(B, B, offset=1, device=x.device)
d = D[idx[0], idx[1]]
```

---

## Step 5

Residualize against video/caption geometry.

Begin with a differentiable ridge solution or projection formulation.

---

## Step 6

Compute correlation loss.

```python
loss = 1 - pearson_corr(r_brain, r_teacher)
```

---

## Step 7

Total objective.

```python
loss_total = loss_task + lambda_rasa * loss_rasa
```

No other architectural change in the first experiment.

---

# 12. What evidence would make the workshop paper convincing?

A workshop paper does not need to solve all multimodal emotion decoding.

But it does need one clean, falsifiable result.

The strongest evidence pattern would look like:

```text
Concat baseline
    ↓
Direct multimodal alignment         small or inconsistent gain
    ↓
Generic geometry alignment          some gain
    ↓
Affect-selective residual alignment clear gain
```

and ideally:

```text
brain-only student improvement
+
teacher performance not the only source of gain
+
cross-subject or held-out-video robustness
+
representation analysis showing greater affect structure
```

For Candidate 2:

```text
full video teacher
    <
video-beyond-caption residual
    <
affect-selected sensory residual
```

would provide a very strong mechanistic result.

---

# 13. Representation analyses worth including

Because the proposal is about **what representation is learned**, downstream accuracy alone is not enough.

Useful analyses include:

## 13.1 RSA with 34-D affect geometry

Measure whether brain representation geometry becomes more consistent with affective structure.

---

## 13.2 RSA with generic visual semantics

Check whether improved affect decoding is not simply explained by better visual-stimulus reconstruction.

---

## 13.3 Caption semantic geometry

Measure whether the representation is becoming merely language-like.

---

## 13.4 Partial RSA

A particularly useful analysis for Candidate 1:

```text
brain ↔ affect
controlling:
    video semantics
    caption semantics
```

The training objective and evaluation analysis then use the same conceptual language.

---

## 13.5 Subject generalization

For Candidate 3 or any cross-subject claim:

```text
within-subject
cross-subject
held-out subject
```

must be separated.

---

# 14. Claim discipline

Avoid broad claims such as:

> Our model learns human emotion from brain activity.

This is likely too strong, especially if the target is a stimulus-level averaged 34-D affective profile.

Prefer:

> Our model decodes stimulus-evoked affective representations from fMRI.

or:

> We improve brain-only prediction of a 34-dimensional video-evoked affective profile using training-time privileged multimodal information.

For Candidate 1:

> We show that affect-selective cross-modal alignment is more useful than generic multimodal correspondence for brain emotion decoding.

For Candidate 2:

> We show that the privileged visual information most useful for brain decoding is the affect-predictive sensory component not explained by language.

For Candidate 3:

> We show that stimulus-level privileged modalities should supervise reproducible stimulus-locked neural structure rather than collapse all subject-specific variability.

---

# 15. Final recommendation

At the current stage:

## First choice

### **Residual Affective Structure Alignment**

Why:

- easiest to implement;
- cleanest comparison against current concat model;
- directly tests an important scientific distinction;
- does not require architecture redesign;
- does not change inference;
- can be falsified with a small set of controlled experiments.

---

## Second choice

### **Sensory-Grounded Affective Residual**

Why:

- stronger conceptual novelty;
- directly exploits the non-equivalence of video and caption;
- gives privileged multimodal training a very specific purpose;
- potentially creates the best workshop-paper story.

But:

- requires stronger validation;
- easier to misinterpret;
- must deal with caption leakage and residual semantics carefully.

---

## Third choice

### **Cross-Subject Consensus-Gated Alignment**

Use only if cross-subject generalization is central.

Why:

- neuroscience-motivated;
- respects stimulus/subject asymmetry;
- potentially useful.

But:

- requires data-pipeline changes;
- related cross-subject alignment literature is mature;
- target provenance weakens individualized-emotion claims.

---

# 16. Most promising eventual paper formulation

The strongest full method is likely not all three.

A clean final paper could be built around:

## **Sensory-Residual Affective Alignment**

with two principles:

### Principle 1

Identify what privileged vision contributes to affect beyond language:

\[
V_{\mathrm{sens-aff}}
=
\operatorname{AffectRelevant}
[V-E(V|C)].
\]

### Principle 2

Transfer affective structure rather than generic stimulus similarity:

\[
\text{brain}
\leftrightarrow
V_{\mathrm{sens-aff}}
\quad
\text{after controlling generic semantic geometry}.
\]

This yields a coherent central message:

> **Multimodal supervision for brain emotion decoding should be selective rather than indiscriminate. Instead of collapsing brain, vision, and language into a common space, we isolate privileged sensory information that is specifically relevant to affect and align only the affective relational structure that remains beyond generic stimulus semantics.**

That is currently the most promising direction for turning the existing concatenation-based EmoBrainModel into a method with a defensible NeurIPS-workshop-level contribution.
