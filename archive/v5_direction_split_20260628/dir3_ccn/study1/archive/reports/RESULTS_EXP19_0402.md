# Results: Experiment 19 (Subject-wise Direct Decoding)

Date: 0402  
Source file: `results/exp19_subjectwise_direct_decoding.npz`  
Script: `19_subjectwise_direct_decoding.py`  
Figures:
- `figures/exp19_subjectwise_direct_decoding_ratios.png`
- `figures/exp19_subjectwise_direct_decoding_means.png`

## Goal

Experiment 19 was designed to answer the stronger subject-level question that Exp 18 did not answer directly.

Question:

> If we decode affective targets directly from each subject's Brain-JEPA embedding, does the category-vs-dimension pattern still hold?

This is different from Exp 18:

- Exp 18: subject-specific readable model-subspace check
- Exp 19: direct subject-wise decoding from neural embeddings themselves

Two neural feature settings were compared:

1. `k=27` PCA-reduced Brain-JEPA embedding
2. `full 768D` Brain-JEPA embedding

Three target ontologies were tested:

- `3D`: 34 emotions + `Arousal`, `Valence`, `Dominance`
- `14D`: 34 emotions + 14 affective dimensions
- `2D`: 34 emotions + `Arousal`, `Valence`

## Main Takeaways

1. `k=27` is clearly more informative than `full 768D` for direct subject-wise decoding.
2. At the group-mean level, direct Brain-JEPA decoding is dimension-heavy in all three ontologies:
   - `3D`: ratio `0.9404`
   - `14D`: ratio `0.6511`
   - `2D`: ratio `0.6932`
3. At the subject level, the direct-decoding story is less uniform than the readable-subspace story from Exp 18.
4. `14D` is the most stable: all 5 subjects remain dimension-heavy at `k=27`.
5. `3D` is mixed at `k=27`: 4/5 subjects are category-heavy even though the group mean is slightly dimension-heavy.
6. `full 768D` decoding mostly collapses toward near-zero `R^2`, so orientation ratios there should be treated as unstable and not over-interpreted.

## k=27 Results

### 3D Targets: 34 Emotions + A/V/D

| Neural representation | Mean category `R^2` | Mean A/V/D `R^2` | Category/dimension ratio | Orientation |
|---|---:|---:|---:|---|
| mean | 0.0561 | 0.0597 | 0.9404 | Dimension |
| subj1 | 0.0304 | 0.0273 | 1.1129 | Category |
| subj2 | 0.0277 | 0.0183 | 1.5109 | Category |
| subj3 | 0.0229 | 0.0267 | 0.8597 | Dimension |
| subj4 | 0.0259 | 0.0238 | 1.0871 | Category |
| subj5 | 0.0216 | 0.0205 | 1.0552 | Category |

Agreement with group-mean orientation:
- `k27 3D`: 1/5 (20.0%)

Interpretation:
- The group-mean direct-decoding result is slightly dimension-heavy (`0.9404`), but most individual subjects are category-heavy.
- This means the `3D` direct-decoding result is not very stable across aggregation levels.

### 14D Targets: 34 Emotions + 14 Dimensions

| Neural representation | Mean category `R^2` | Mean 14D `R^2` | Category/dimension ratio | Orientation |
|---|---:|---:|---:|---|
| mean | 0.0561 | 0.0862 | 0.6511 | Dimension |
| subj1 | 0.0304 | 0.0479 | 0.6343 | Dimension |
| subj2 | 0.0277 | 0.0287 | 0.9671 | Dimension |
| subj3 | 0.0229 | 0.0373 | 0.6138 | Dimension |
| subj4 | 0.0259 | 0.0381 | 0.6798 | Dimension |
| subj5 | 0.0216 | 0.0379 | 0.5707 | Dimension |

Agreement with group-mean orientation:
- `k27 14D`: 5/5 (100.0%)

Interpretation:
- This is the cleanest subject-level result in Exp 19.
- Both group mean and all 5 subjects are dimension-heavy in the richer 14D target space.

### 2D Targets: 34 Emotions + A/V

| Neural representation | Mean category `R^2` | Mean A/V `R^2` | Category/dimension ratio | Orientation |
|---|---:|---:|---:|---|
| mean | 0.0561 | 0.0810 | 0.6932 | Dimension |
| subj1 | 0.0304 | 0.0409 | 0.7419 | Dimension |
| subj2 | 0.0277 | 0.0275 | 1.0073 | Category |
| subj3 | 0.0229 | 0.0400 | 0.5731 | Dimension |
| subj4 | 0.0259 | 0.0329 | 0.7883 | Dimension |
| subj5 | 0.0216 | 0.0308 | 0.7035 | Dimension |

Agreement with group-mean orientation:
- `k27 2D`: 4/5 (80.0%)

Interpretation:
- The group mean is dimension-heavy, and 4/5 subjects match that direction.
- Subject 2 is nearly balanced but just slightly category-heavy (`1.0073`).

## Full 768D Results

### 3D Targets: 34 Emotions + A/V/D

| Neural representation | Mean category `R^2` | Mean A/V/D `R^2` | Category/dimension ratio | Orientation |
|---|---:|---:|---:|---|
| mean | 0.0103 | 0.0217 | 0.4737 | Dimension |
| subj1 | 0.0019 | 0.0000 | 19139728.5262 | Category |
| subj2 | 0.0000 | 0.0000 | 0.0000 | Dimension |
| subj3 | 0.0001 | 0.0000 | 1326300.3066 | Category |
| subj4 | 0.0000 | 0.0000 | 0.0000 | Dimension |
| subj5 | 0.0000 | 0.0000 | 0.0000 | Dimension |

Agreement with group-mean orientation:
- `full 3D`: 3/5 (60.0%)

### 14D Targets: 34 Emotions + 14 Dimensions

| Neural representation | Mean category `R^2` | Mean 14D `R^2` | Category/dimension ratio | Orientation |
|---|---:|---:|---:|---|
| mean | 0.0103 | 0.0252 | 0.4091 | Dimension |
| subj1 | 0.0019 | 0.0000 | 19139728.5262 | Category |
| subj2 | 0.0000 | 0.0000 | 0.0000 | Dimension |
| subj3 | 0.0001 | 0.0000 | 1326300.3066 | Category |
| subj4 | 0.0000 | 0.0000 | 0.0000 | Dimension |
| subj5 | 0.0000 | 0.0000 | 0.0000 | Dimension |

Agreement with group-mean orientation:
- `full 14D`: 3/5 (60.0%)

### 2D Targets: 34 Emotions + A/V

| Neural representation | Mean category `R^2` | Mean A/V `R^2` | Category/dimension ratio | Orientation |
|---|---:|---:|---:|---|
| mean | 0.0103 | 0.0326 | 0.3158 | Dimension |
| subj1 | 0.0019 | 0.0000 | 19139728.5262 | Category |
| subj2 | 0.0000 | 0.0000 | 0.0000 | Dimension |
| subj3 | 0.0001 | 0.0000 | 1326300.3066 | Category |
| subj4 | 0.0000 | 0.0000 | 0.0000 | Dimension |
| subj5 | 0.0000 | 0.0000 | 0.0000 | Dimension |

Agreement with group-mean orientation:
- `full 2D`: 3/5 (60.0%)

Important caution for `full 768D`:

- Several subject-level mean dimension `R^2` values are effectively zero in the full-space setting.
- As a result, category/dimension ratios can explode or become numerically unstable.
- The main interpretable point is simply that direct decoding with full `768D` Brain-JEPA is much worse than with `k=27`.

## Comparison with Exp 18

The contrast with Exp 18 is scientifically important.

- Exp 18 asked: `What kind of video-model subspace is readable from each subject's neural representation?`
- Exp 19 asks: `What kind of affective target can be decoded directly from each subject's neural embedding itself?`

These are not the same question, and they do not give the same answer.

Most important contrast:

- Exp 18: V-JEPA2 readable subspace was stably category-leaning across subjects.
- Exp 19: direct Brain-JEPA decoding is not uniformly category-leaning; in fact, the group mean is dimension-heavy, especially in `14D` and `2D`.

This suggests that:

- the readable model subspace story and the direct neural decoding story are complementary rather than identical
- category dominance is strongest in the model-subspace readout framing
- broader dimensional structure becomes more evident when decoding directly from neural embeddings, especially in richer target spaces

## Main Interpretation

The safest interpretation after Exp 19 is:

- direct subject-wise neural decoding supports the low-dimensional (`k=27`) story
- direct subject-wise neural decoding does **not** support a simple universal category-dominance claim
- the richer the affective target space, the more clearly the direct neural decoding result becomes dimension-heavy
- therefore, category-vs-dimension balance depends not only on the target ontology, but also on whether we analyze:
  - direct neural decoding
  - or neural-to-model readable subspaces

## Output Files

- Result array: [exp19_subjectwise_direct_decoding.npz](/pscratch/sd/s/sjmoon/EmoFM/CCN/results/exp19_subjectwise_direct_decoding.npz)
- Ratio figure: [exp19_subjectwise_direct_decoding_ratios.png](/pscratch/sd/s/sjmoon/EmoFM/CCN/figures/exp19_subjectwise_direct_decoding_ratios.png)
- Mean figure: [exp19_subjectwise_direct_decoding_means.png](/pscratch/sd/s/sjmoon/EmoFM/CCN/figures/exp19_subjectwise_direct_decoding_means.png)
