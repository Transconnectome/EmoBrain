# Experiment 18 Results: Subject-wise Claim Check

Date: 0402  
Script: [18_subjectwise_claim_check.py](/pscratch/sd/s/sjmoon/EmoFM/CCN/18_subjectwise_claim_check.py)  
Result file: [exp18_subjectwise_claim_check.npz](/pscratch/sd/s/sjmoon/EmoFM/CCN/results/exp18_subjectwise_claim_check.npz)

## 1. What This Experiment Tested

The goal of Exp 18 was simple:

- define brain-predictable video-model PCs separately for the group-mean Brain-JEPA representation and for each of the 5 individual subjects
- re-run the Exp 12 style category-vs-dimension comparison at the subject level
- check whether the core group-level claim is preserved per subject

The experiment covered three target ontologies:

- `3D`: 34 emotions + `Arousal`, `Valence`, `Dominance`
- `14D`: 34 emotions + 14 affective dimensions
- `2D`: 34 emotions + `Arousal`, `Valence`

## 2. Brain-predictable PC Counts

The group-mean representation produced a larger readable subspace than any individual subject.

| Neural representation | V-JEPA2 predictable PCs | CLIP predictable PCs |
|---|---:|---:|
| Mean | 3 | 6 |
| Subject 1 | 1 | 1 |
| Subject 2 | 2 | 2 |
| Subject 3 | 2 | 2 |
| Subject 4 | 1 | 1 |
| Subject 5 | 1 | 1 |

Predictable PC identities:

- V-JEPA2 mean: `PC1, PC2, PC3`
- V-JEPA2 subjects:
  - Subject 1: `PC1`
  - Subject 2: `PC1, PC3`
  - Subject 3: `PC1, PC3`
  - Subject 4: `PC1`
  - Subject 5: `PC1`
- CLIP mean: `PC1, PC2, PC3, PC5, PC6, PC7`
- CLIP subjects:
  - Subject 1: `PC1`
  - Subject 2: `PC1, PC2`
  - Subject 3: `PC1, PC2`
  - Subject 4: `PC1`
  - Subject 5: `PC1`

Interpretation:

- the group-mean Brain-JEPA representation exposes a larger brain-predictable subspace than any single subject
- the most stable core remains very small
- `PC1` is the dominant shared readable axis for both V-JEPA2 and CLIP

## 3. Subject-wise Category-vs-Dimension Balance

### 3.1 3D Targets: 34 Emotions + A/V/D

#### V-JEPA2

| Neural representation | Mean category `R²` | Mean A/V/D `R²` | Ratio |
|---|---:|---:|---:|
| Mean | 0.0550 | 0.0254 | 2.162 |
| Subject 1 | 0.0197 | 0.0067 | 2.937 |
| Subject 2 | 0.0328 | 0.0083 | 3.969 |
| Subject 3 | 0.0328 | 0.0083 | 3.969 |
| Subject 4 | 0.0197 | 0.0067 | 2.937 |
| Subject 5 | 0.0197 | 0.0067 | 2.937 |

#### CLIP

| Neural representation | Mean category `R²` | Mean A/V/D `R²` | Ratio |
|---|---:|---:|---:|
| Mean | 0.1659 | 0.1297 | 1.279 |
| Subject 1 | 0.0391 | 0.0151 | 2.591 |
| Subject 2 | 0.0775 | 0.0206 | 3.768 |
| Subject 3 | 0.0775 | 0.0206 | 3.768 |
| Subject 4 | 0.0391 | 0.0151 | 2.591 |
| Subject 5 | 0.0391 | 0.0151 | 2.591 |

Agreement with the group-mean claim:

- V-JEPA2: `5/5` subjects matched the mean-level `category > dimension` orientation
- CLIP: `5/5` subjects matched the mean-level `category > dimension` orientation

Interpretation:

- the 3D result is highly stable at the subject level
- if the ontology is restricted to A/V/D, both models remain category-leaning in every subject

### 3.2 14D Targets: 34 Emotions + 14 Dimensions

#### V-JEPA2

| Neural representation | Mean category `R²` | Mean 14D `R²` | Ratio |
|---|---:|---:|---:|
| Mean | 0.0550 | 0.0306 | 1.794 |
| Subject 1 | 0.0197 | 0.0115 | 1.715 |
| Subject 2 | 0.0328 | 0.0139 | 2.361 |
| Subject 3 | 0.0328 | 0.0139 | 2.361 |
| Subject 4 | 0.0197 | 0.0115 | 1.715 |
| Subject 5 | 0.0197 | 0.0115 | 1.715 |

#### CLIP

| Neural representation | Mean category `R²` | Mean 14D `R²` | Ratio |
|---|---:|---:|---:|
| Mean | 0.1659 | 0.1802 | 0.921 |
| Subject 1 | 0.0391 | 0.0395 | 0.991 |
| Subject 2 | 0.0775 | 0.0563 | 1.375 |
| Subject 3 | 0.0775 | 0.0563 | 1.375 |
| Subject 4 | 0.0391 | 0.0395 | 0.991 |
| Subject 5 | 0.0391 | 0.0395 | 0.991 |

Agreement with the group-mean claim:

- V-JEPA2: `5/5` subjects matched the mean-level `category > dimension` orientation
- CLIP: `3/5` subjects matched the mean-level `dimension >= category` orientation

Interpretation:

- V-JEPA2 remains robustly category-leaning even at the subject level in the richer 14D target space
- CLIP is less stable than V-JEPA2 in 14D
- the group-level `CLIP -> dimension-heavy` result is present, but not uniformly strong across subjects

### 3.3 2D Targets: 34 Emotions + A/V

#### V-JEPA2

| Neural representation | Mean category `R²` | Mean A/V `R²` | Ratio |
|---|---:|---:|---:|
| Mean | 0.0550 | 0.0382 | 1.441 |
| Subject 1 | 0.0197 | 0.0101 | 1.958 |
| Subject 2 | 0.0328 | 0.0124 | 2.646 |
| Subject 3 | 0.0328 | 0.0124 | 2.646 |
| Subject 4 | 0.0197 | 0.0101 | 1.958 |
| Subject 5 | 0.0197 | 0.0101 | 1.958 |

#### CLIP

| Neural representation | Mean category `R²` | Mean A/V `R²` | Ratio |
|---|---:|---:|---:|
| Mean | 0.1659 | 0.1664 | 0.997 |
| Subject 1 | 0.0391 | 0.0227 | 1.727 |
| Subject 2 | 0.0775 | 0.0304 | 2.549 |
| Subject 3 | 0.0775 | 0.0304 | 2.549 |
| Subject 4 | 0.0391 | 0.0227 | 1.727 |
| Subject 5 | 0.0391 | 0.0227 | 1.727 |

Agreement with the group-mean claim:

- V-JEPA2: `5/5` subjects matched the mean-level `category > dimension` orientation
- CLIP: `0/5` subjects matched the mean-level near-balanced / dimension-leaning orientation

Interpretation:

- V-JEPA2 is again stable
- CLIP’s mean-level near-balance in 2D is not reproduced at the individual-subject level
- the CLIP 2D result appears to be more dependent on subject averaging than the V-JEPA2 result

## 4. Main Takeaways

The most important result of Exp 18 is that the group-level story is not uniformly fragile, but it is not uniformly equally stable either.

What looks robust:

- V-JEPA2 remains category-leaning in `3D`, `14D`, and `2D` for all 5 subjects
- the readable subspace remains very small at both group and subject levels
- `PC1` is the dominant shared readable axis

What now needs more caution:

- CLIP’s `14D` dimension-heavy tendency is only partially stable at the subject level
- CLIP’s `2D` near-balanced result is not reproduced in any single subject
- the CLIP mean-level result should therefore be framed as a group-level tendency rather than a uniformly subject-level effect

## 5. Implication for the Main Claim

Exp 18 strengthens the following claim:

> The readable part of video-model space is very small, and V-JEPA2’s readable subspace is consistently category-leaning across subjects and target ontologies.

Exp 18 weakens or at least qualifies the following stronger claim:

> CLIP is uniformly dimension-heavy or uniformly balanced at the individual-subject level.

So after Exp 18, the safest interpretation is:

- V-JEPA2 shows stable subject-level category dominance
- CLIP shows a stronger dependence on group averaging, especially in `2D` and partly in `14D`
- therefore, the category-vs-dimension balance is representation-dependent and aggregation-dependent

## 6. Output Files

- Result array: [exp18_subjectwise_claim_check.npz](/pscratch/sd/s/sjmoon/EmoFM/CCN/results/exp18_subjectwise_claim_check.npz)
- Ratio figure: [exp18_subjectwise_ratios.png](/pscratch/sd/s/sjmoon/EmoFM/CCN/figures/exp18_subjectwise_ratios.png)
- PC-count figure: [exp18_subjectwise_pc_counts.png](/pscratch/sd/s/sjmoon/EmoFM/CCN/figures/exp18_subjectwise_pc_counts.png)
