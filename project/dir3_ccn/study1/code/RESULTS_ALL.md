# CCN 2026 — Full Analysis Results

**Date**: 2026-03-31  
**Scripts**: 01–06 in `/pscratch/sd/s/sjmoon/EmoFM/CCN/`  
**Data**: Horikawa et al. (2020), Brain-JEPA embeddings (5 subjects × 2196 videos × 768 dims)  
**Models**: V-JEPA2 (`facebook/vjepa2-vitg-fpc64-256`, 1408-dim), CLIP (`openai/clip-vit-base-patch32`, 512-dim)

---

## 01 — Brain-JEPA RSM (`01_brain_jepa_rsm.py`)

**Input**: `brain_jepa_embeddings.npy` (5, 2196, 768)  
**Method**: Per-subject cosine similarity RSM → 5×5 cross-subject Spearman r matrix  

### Cross-subject Spearman r matrix (5×5)

|        | S1     | S2     | S3     | S4     | S5     |
|--------|--------|--------|--------|--------|--------|
| **S1** | 1.0000 | 0.3320 | 0.3185 | 0.2853 | 0.3293 |
| **S2** | 0.3320 | 1.0000 | 0.3809 | 0.3589 | 0.4122 |
| **S3** | 0.3185 | 0.3809 | 1.0000 | 0.3270 | 0.3672 |
| **S4** | 0.2853 | 0.3589 | 0.3270 | 1.0000 | 0.3603 |
| **S5** | 0.3293 | 0.4122 | 0.3672 | 0.3603 | 1.0000 |

- **off_diag_mean**: 0.3472  
- **off_diag_std**: 0.0342

### Brain-JEPA RSM (mean across subjects) stats

- shape: (2196, 2196)
- min: 0.9062
- max: 1.0000
- mean: 0.9803
- std: 0.0090

**Outputs**: `results/brain_jepa_rsm_per_subject.npy`, `results/brain_jepa_rsm_mean.npy`, `results/brain_jepa_rsm_stats.npz`

---

## 02 — Per-subject CKA (`02_subject_cka.py`)

**Input**: `brain_jepa_rsm_per_subject.npy`, `rsm_vjepa2.npy`, `rsm_clip.npy`  
**Method**: CKA(brain_RSM_i, model_RSM) per subject, using pre-centered model RSMs

### Per-subject CKA

| Subject | V-JEPA2  | CLIP     | Δ (V-J − CLIP) |
|---------|----------|----------|----------------|
| S1      | 0.054835 | 0.047351 | +0.007484      |
| S2      | 0.063292 | 0.060017 | +0.003274      |
| S3      | 0.055383 | 0.050774 | +0.004609      |
| S4      | 0.045845 | 0.051293 | −0.005448      |
| S5      | 0.072584 | 0.060269 | +0.012314      |

### Summary

- **mean CKA V-JEPA2**: 0.058388
- **mean CKA CLIP**: 0.053941
- **mean Δ**: +0.004447
- **V-JEPA2 > CLIP**: 4/5 subjects

**Outputs**: `results/subject_cka_results.npz`

---

## 03 — Procrustes Alignment (`03_procrustes.py`)

**Input**: `brain_jepa_embeddings.npy`, `vjepa2_embeddings.npy`, `clip_embeddings.npy`  
**Method**: brain_mean=(2196,768); PCA(k=27) on brain_mean, vjepa2, clip → `scipy.spatial.procrustes` → disparity + per-video alignment error; per-emotion score-weighted mean error

### Global Results

- **k_used**: 27
- **brain_k shape**: (2196, 27)
- **vjepa_k shape**: (2196, 27)
- **clip_k shape**: (2196, 27)
- **disparity_vjepa**: 0.93798642
- **disparity_clip**: 0.93853992
- **Δ disparity (vjepa−clip)**: −0.00055350 (V-JEPA2 lower = better)
- **mean per-video error vjepa**: 0.019153 (std: 0.007764)
- **mean per-video error clip**: 0.019159 (std: 0.007766)
- **V-JEPA2 lower error**: 25/34 emotions

### Per-emotion Procrustes alignment error (score-weighted mean)

| Emotion                   | V-JEPA2  | CLIP     | Δ (v−c)    |
|---------------------------|----------|----------|------------|
| Admiration                | 0.020084 | 0.020236 | −0.000152  |
| Adoration                 | 0.018916 | 0.019001 | −0.000085  |
| Aesthetic appreciation    | 0.018225 | 0.018312 | −0.000087  |
| Amusement                 | 0.020086 | 0.020166 | −0.000080  |
| Anger                     | 0.019125 | 0.019125 | −0.000000  |
| Anxiety                   | 0.019876 | 0.020023 | −0.000147  |
| Awe                       | 0.019601 | 0.019695 | −0.000094  |
| Awkwardness               | 0.018354 | 0.018205 | +0.000149  |
| Boredom                   | 0.019237 | 0.019206 | +0.000031  |
| Calmness                  | 0.017465 | 0.017609 | −0.000144  |
| Confusion                 | 0.019389 | 0.019336 | +0.000052  |
| Contempt                  | 0.019461 | 0.019550 | −0.000089  |
| Craving                   | 0.016824 | 0.016865 | −0.000041  |
| Disgust                   | 0.019586 | 0.019538 | +0.000047  |
| Empathic pain             | 0.018115 | 0.018081 | +0.000034  |
| Entrancement              | 0.020051 | 0.019965 | +0.000085  |
| Excitement                | 0.018794 | 0.018851 | −0.000057  |
| Fear                      | 0.018464 | 0.018547 | −0.000083  |
| Horror                    | 0.019392 | 0.019496 | −0.000104  |
| Interest                  | 0.019672 | 0.019791 | −0.000119  |
| Joy                       | 0.019072 | 0.019171 | −0.000099  |
| Nostalgia                 | 0.019787 | 0.019798 | −0.000011  |
| Relief                    | 0.020462 | 0.020508 | −0.000046  |
| Romance                   | 0.019233 | 0.019246 | −0.000013  |
| Sadness                   | 0.017436 | 0.017500 | −0.000064  |
| Satisfaction              | 0.019902 | 0.020000 | −0.000097  |
| Sexual desire             | 0.020005 | 0.020216 | −0.000210  |
| Surprise                  | 0.017055 | 0.016360 | +0.000696  |
| Sympathy                  | 0.019660 | 0.019678 | −0.000018  |
| Triumph                   | 0.020191 | 0.020269 | −0.000078  |
| Uncomfortable             | 0.016571 | 0.016251 | +0.000321  |
| Annoyance                 | 0.020768 | 0.020811 | −0.000043  |
| Envy                      | 0.020062 | 0.020047 | +0.000015  |
| Guilt                     | 0.021500 | 0.021690 | −0.000189  |

**Outputs**: `results/procrustes_results.npz`

---

## 04 — Cross-space RSA (`04_crossspace_rsa.py`)

**Input**: `rsm_brain.npy` (RSM of mean Brain-JEPA embedding), `rsm_vjepa2.npy`, `rsm_clip.npy`  
**Method**: Spearman r between upper-triangle of RSM and emotion kernel E_i[j,k]=score_i[j]×score_i[k] for each of 34 emotions  
**alignment_i** = min(rsa_brain_i, rsa_vjepa2_i)  
**divergence_i** = |rsa_brain_i − rsa_vjepa2_i|

### Per-emotion RSA (Spearman r)

| Emotion                   |   Brain  | V-JEPA2  |   CLIP   | Alignment | Divergence |
|---------------------------|----------|----------|----------|-----------|------------|
| Admiration                | −0.018824| +0.014639| −0.014047| −0.018824 |  0.033464  |
| Adoration                 | +0.005688| +0.091910| +0.081541| +0.005688 |  0.086222  |
| Aesthetic appreciation    | +0.022610| −0.127337| −0.002714| −0.127337 |  0.149947  |
| Amusement                 | −0.082621| +0.180298| +0.133543| −0.082621 |  0.262919  |
| Anger                     | −0.002080| +0.028315| +0.031461| −0.002080 |  0.030395  |
| Anxiety                   | −0.036861| +0.039312| +0.129950| −0.036861 |  0.076172  |
| Awe                       | −0.043583| −0.006655| +0.091766| −0.043583 |  0.036928  |
| Awkwardness               | +0.015989| +0.044620| +0.014522| +0.015989 |  0.028631  |
| Boredom                   | −0.001145| −0.043090| −0.093057| −0.043090 |  0.041945  |
| Calmness                  | +0.037007| −0.082173| −0.052943| −0.082173 |  0.119181  |
| Confusion                 | −0.026636| +0.027720| +0.093140| −0.026636 |  0.054357  |
| Contempt                  | −0.003291| −0.001139| −0.019220| −0.003291 |  0.002152  |
| Craving                   | +0.030783| +0.004521| +0.016612| +0.004521 |  0.026262  |
| Disgust                   | −0.000074| +0.023598| −0.001239| −0.000074 |  0.023673  |
| Empathic pain             | +0.026774| +0.063995| +0.044687| +0.026774 |  0.037220  |
| Entrancement              | −0.014773| +0.048049| +0.056398| −0.014773 |  0.062822  |
| Excitement                | −0.012570| −0.103104| +0.019030| −0.103104 |  0.090534  |
| Fear                      | +0.009640| −0.008568| −0.014886| −0.008568 |  0.018207  |
| Horror                    | −0.019927| +0.020271| +0.016011| −0.019927 |  0.040198  |
| Interest                  | −0.027501| +0.062460| +0.151003| −0.027501 |  0.089962  |
| Joy                       | +0.003393| +0.017052| +0.009565| +0.003393 |  0.013659  |
| Nostalgia                 | −0.002599| +0.067809| +0.135573| −0.002599 |  0.070408  |
| Relief                    | −0.068246| −0.057102| +0.047859| −0.068246 |  0.011144  |
| Romance                   | −0.006084| +0.098440| +0.017828| −0.006084 |  0.104523  |
| Sadness                   | +0.038634| +0.008528| −0.017458| +0.008528 |  0.030106  |
| Satisfaction              | −0.006079| +0.013013| −0.018590| −0.006079 |  0.019092  |
| Sexual desire             | −0.015026| +0.033627| +0.047766| −0.015026 |  0.048653  |
| Surprise                  | +0.050138| +0.018697| +0.042488| +0.018697 |  0.031441  |
| Sympathy                  | −0.018333| +0.041985| +0.040263| −0.018333 |  0.060318  |
| Triumph                   | −0.040270| +0.001125| −0.010456| −0.040270 |  0.041395  |
| Uncomfortable             | +0.062026| +0.030325| +0.065976| +0.030325 |  0.031701  |
| Annoyance                 | −0.108467| +0.150973| +0.219993| −0.108467 |  0.259441  |
| Envy                      | −0.022637| +0.072970| +0.063450| −0.022637 |  0.095606  |
| Guilt                     | −0.037373| +0.038032| +0.013533| −0.037373 |  0.075405  |

### Global means

| Metric     | Value     |
|------------|-----------|
| Brain mean | −0.009186 |
| V-JEPA2 mean | +0.023915 |
| CLIP mean  | +0.039393 |
| Alignment mean | −0.025048 |
| Divergence mean | +0.064826 |

### Pairwise comparisons

- Brain > V-JEPA2: 9/34
- Brain > CLIP: 11/34
- V-JEPA2 > CLIP: 18/34

### Top 5 Brain–Model Divergence

| Emotion                 | Brain    | V-JEPA2  | CLIP     | Divergence |
|-------------------------|----------|----------|----------|------------|
| Amusement               | −0.0826  | +0.1803  | +0.1335  | 0.2629     |
| Annoyance               | −0.1085  | +0.1510  | +0.2200  | 0.2594     |
| Aesthetic appreciation  | +0.0226  | −0.1273  | −0.0027  | 0.1499     |
| Calmness                | +0.0370  | −0.0822  | −0.0529  | 0.1192     |
| Romance                 | −0.0061  | +0.0984  | +0.0178  | 0.1045     |

### Top 5 Brain RSA (highest brain emotion encoding)

| Emotion        | Brain    | V-JEPA2  | CLIP     |
|----------------|----------|----------|----------|
| Uncomfortable  | +0.0620  | +0.0303  | +0.0660  |
| Surprise       | +0.0501  | +0.0187  | +0.0425  |
| Sadness        | +0.0386  | +0.0085  | −0.0175  |
| Calmness       | +0.0370  | −0.0822  | −0.0529  |
| Craving        | +0.0308  | +0.0045  | +0.0166  |

**Outputs**: `results/crossspace_rsa_results.npz`

---

## 05 — k-sweep (`05_k_sweep.py`)

**Input**: `brain_jepa_embeddings.npy`, `vjepa2_embeddings.npy`, `clip_embeddings.npy`  
**Method**: For each k: PCA(k) → Procrustes disparity (brain vs model); Pipeline(StandardScaler, Ridge α=1.0) 5-fold CV → emotion decoding R² from k-dim PCA subspace  
**k_values**: [3, 5, 7, 10, 15, 20, 25, 27, 30, 34, 40, 50, 75, 100]

### k-sweep table

```
Running k sweep: [3, 5, 7, 10, 15, 20, 25, 27, 30, 34, 40, 50, 75, 100]
  k=  3  disp_v=0.9316  disp_c=0.9336  R²_brain=0.0156  R²_vjepa=0.0550  R²_clip=0.0941  [2s]
  k=  5  disp_v=0.9383  disp_c=0.9398  R²_brain=0.0226  R²_vjepa=0.0726  R²_clip=0.1366  [2s]
  k=  7  disp_v=0.9427  disp_c=0.9364  R²_brain=0.0346  R²_vjepa=0.0797  R²_clip=0.1884  [2s]
  k= 10  disp_v=0.9404  disp_c=0.9351  R²_brain=0.0428  R²_vjepa=0.0955  R²_clip=0.2115  [2s]
  k= 15  disp_v=0.9355  disp_c=0.9364  R²_brain=0.0488  R²_vjepa=0.1136  R²_clip=0.2361  [2s]
  k= 20  disp_v=0.9372  disp_c=0.9369  R²_brain=0.0537  R²_vjepa=0.1196  R²_clip=0.2534  [2s]
  k= 25  disp_v=0.9376  disp_c=0.9381  R²_brain=0.0561  R²_vjepa=0.1292  R²_clip=0.2653  [2s]
  k= 27  disp_v=0.9380  disp_c=0.9385  R²_brain=0.0561  R²_vjepa=0.1317  R²_clip=0.2696  [2s]
  k= 30  disp_v=0.9387  disp_c=0.9389  R²_brain=0.0568  R²_vjepa=0.1334  R²_clip=0.2743  [2s]
  k= 34  disp_v=0.9386  disp_c=0.9393  R²_brain=0.0583  R²_vjepa=0.1397  R²_clip=0.2816  [2s]
  k= 40  disp_v=0.9390  disp_c=0.9398  R²_brain=0.0590  R²_vjepa=0.1463  R²_clip=0.2841  [3s]
  k= 50  disp_v=0.9397  disp_c=0.9406  R²_brain=0.0606  R²_vjepa=0.1554  R²_clip=0.2906  [3s]
  k= 75  disp_v=0.9404  disp_c=0.9417  R²_brain=0.0574  R²_vjepa=0.1678  R²_clip=0.2940  [4s]
  k=100  disp_v=0.9406  disp_c=0.9426  R²_brain=0.0543  R²_vjepa=0.1704  R²_clip=0.2907  [4s]
```

### Full precision table

| k   | disp_vjepa | disp_clip  | Δdisp(v−c) | R²_brain | R²_vjepa | R²_clip  |
|-----|------------|------------|------------|----------|----------|----------|
| 3   | 0.931579   | 0.933554   | −0.001975  | 0.015627 | 0.054990 | 0.094106 |
| 5   | 0.938259   | 0.939770   | −0.001510  | 0.022599 | 0.072629 | 0.136606 |
| 7   | 0.942706   | 0.936396   | +0.006309  | 0.034557 | 0.079684 | 0.188368 |
| 10  | 0.940375   | 0.935088   | +0.005287  | 0.042842 | 0.095550 | 0.211525 |
| 15  | 0.935514   | 0.936417   | −0.000903  | 0.048828 | 0.113620 | 0.236077 |
| 20  | 0.937199   | 0.936934   | +0.000265  | 0.053734 | 0.119607 | 0.253445 |
| 25  | 0.937570   | 0.938097   | −0.000527  | 0.056145 | 0.129166 | 0.265345 |
| 27  | 0.938043   | 0.938532   | −0.000489  | 0.056147 | 0.131655 | 0.269617 |
| 30  | 0.938735   | 0.938871   | −0.000135  | 0.056797 | 0.133377 | 0.274277 |
| 34  | 0.938644   | 0.939274   | −0.000630  | 0.058299 | 0.139738 | 0.281579 |
| 40  | 0.938995   | 0.939833   | −0.000838  | 0.058972 | 0.146310 | 0.284052 |
| 50  | 0.939650   | 0.940577   | −0.000927  | 0.060644 | 0.155396 | 0.290639 |
| 75  | 0.940351   | 0.941703   | −0.001352  | 0.057418 | 0.167841 | 0.294026 |
| 100 | 0.940627   | 0.942573   | −0.001945  | 0.054331 | 0.170436 | 0.290744 |

### Key derived values

- **k_elbow** (largest Procrustes disparity drop): **15**
- **k_plateau** (first k where R²_brain ≥ 95% of max): **34**
- **max R²_brain**: 0.060644 (at k=50)
- **R²_brain at k=27**: 0.056147 = **92.6%** of max
- **95% threshold**: 0.057612
- **R²_brain at k=25 vs k=27**: 0.056145 vs 0.056147 (effectively identical)
- **V-JEPA2 disparity < CLIP for**: 10/14 k values (k=3,5,15,25,27,30,34,40,50,75,100 — all except k=7,10,20)

**Outputs**: `results/k_sweep_results.npz`, `figures/k_sweep.png`

---

## 06 — Visualization (`06_umap.py`)

**Method**:
- RSM panels: MDS (`sklearn.manifold.MDS`, metric=precomputed, dissimilarity=precomputed)
- Procrustes overlay: PCA(n_components=2) on joint (brain_std + vjepa_aligned), shape (4392, 27) → 2D

### Procrustes overlay (PCA 2D)

- **pca_var_explained**: 48.78%
- **per-video overlay error**: min=0.000139, max=0.049166, mean=0.012405, std=0.007363

### Embedding shapes

| Array               | Shape     | dtype   |
|---------------------|-----------|---------|
| emb_brain           | (2196, 2) | float32 |
| emb_vjepa2          | (2196, 2) | float32 |
| emb_clip            | (2196, 2) | float32 |
| emb_overlay_brain   | (2196, 2) | float64 |
| emb_overlay_vjepa   | (2196, 2) | float64 |

**Outputs**: `results/embedding_2d.npz`, `figures/emotion_space_3panel.png`, `figures/procrustes_overlay.png`

---

## Summary table (all analyses)

| Analysis | Metric | V-JEPA2 | CLIP | Winner |
|----------|--------|---------|------|--------|
| 02 CKA (mean across 5 subjects) | CKA | 0.058388 | 0.053941 | V-JEPA2 |
| 02 CKA (subject count) | # subjects V-J > CLIP | 4/5 | — | V-JEPA2 |
| 03 Procrustes (k=27) | disparity | 0.937986 | 0.938540 | V-JEPA2 |
| 03 Procrustes per-emotion | # emotions lower error | 25/34 | 9/34 | V-JEPA2 |
| 04 RSA mean Spearman r | r | +0.0239 | +0.0394 | CLIP |
| 04 RSA emotion count | # emotions higher r | 18/34 | 16/34 | CLIP |
| 05 k-sweep disparity | # k values V-J lower | 10/14 | — | V-JEPA2 |
| 05 k-sweep R²_brain | max (k=50) | — | — | 0.0606 |
| 01 Subject invariance | off-diag Spearman r | 0.347 ± 0.034 | — | — |
