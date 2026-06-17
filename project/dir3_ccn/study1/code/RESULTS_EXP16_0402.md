# Results: Experiment 16 (Incremental Baseline Benchmark)

Date: 0402  
Source file: `results/exp16_incremental_baseline_results.npz`  
Figures:
- `figures/exp16_incremental_benchmark.png`
- `figures/exp16_incremental_scatter.png`

## Goal

Experiment 16 tested a reviewer-facing question directly:

> If vision and semantic features are already available, do brain-predictable video-model PCs still add anything?

To answer this, five models were compared:

1. `Vision + Semantic`
2. `V-JEPA2 brain-predictable PCs only`
3. `CLIP brain-predictable PCs only`
4. `Vision + Semantic + V-JEPA2 PCs`
5. `Vision + Semantic + CLIP PCs`

The key quantity was incremental `R^2`:

- `Delta_vjepa = R^2(baseline + V-JEPA2 PCs) - R^2(baseline)`
- `Delta_clip = R^2(baseline + CLIP PCs) - R^2(baseline)`

## Main Takeaways

### Overall summary

- The `Vision + Semantic` baseline already predicts a meaningful portion of variance.
- Adding brain-predictable V-JEPA2 PCs gives a small positive gain overall:
  - mean category gain `= +0.0022`
  - mean A/V/D gain `= +0.0001`
- Adding brain-predictable CLIP PCs gives a clearer gain:
  - mean category gain `= +0.0065`
  - mean A/V/D gain `= +0.0079`

### What this means

- The answer is not "vision+semantic is enough."
- Brain-predictable model PCs do add information beyond explicit vision/semantic features.
- But the extra contribution is modest, not huge.
- CLIP adds more incremental variance than V-JEPA2 under this benchmark.

This makes Exp 16 a useful supplementary control:

- it defends the use of model PCs,
- but it also shows that much of the explainable structure is already shared with explicit vision/semantic features.

## Brain-Predictable PC Counts

Using the same threshold as Exp 12 (`R^2 > 0.01`):

- V-JEPA2 selected PCs: `1, 2, 3` (`n = 3`)
- CLIP selected PCs: `1, 2, 3, 5, 6, 7` (`n = 6`)

## Summary of Model Families

| Model | Mean category `R^2` | Mean A/V/D `R^2` | Category/dimension ratio |
|---|---:|---:|---:|
| Vision + Semantic baseline | 0.0796 | 0.0991 | 0.8027 |
| V-JEPA2 PCs only | 0.0550 | 0.0254 | 2.1615 |
| CLIP PCs only | 0.1659 | 0.1297 | 1.2785 |
| Baseline + V-JEPA2 PCs | 0.0818 | 0.0993 | 0.8238 |
| Baseline + CLIP PCs | 0.0861 | 0.1071 | 0.8042 |

## Incremental Gain Over Baseline

| Added feature set | Mean category delta `R^2` | Mean A/V/D delta `R^2` |
|---|---:|---:|
| V-JEPA2 PCs | +0.0022 | +0.0001 |
| CLIP PCs | +0.0065 | +0.0079 |

## Top Incremental Emotions

### Baseline + V-JEPA2 PCs vs Baseline

| Rank | Emotion | Baseline `R^2` | Combined `R^2` | Delta |
|---:|---|---:|---:|---:|
| 1 | Aesthetic appreciation | 0.3549 | 0.3936 | +0.0387 |
| 2 | Excitement | 0.0907 | 0.1049 | +0.0141 |
| 3 | Adoration | 0.1427 | 0.1546 | +0.0118 |
| 4 | Amusement | 0.0114 | 0.0178 | +0.0063 |
| 5 | Interest | 0.0632 | 0.0691 | +0.0059 |
| 6 | Craving | 0.3873 | 0.3911 | +0.0038 |
| 7 | Uncomfortable | 0.6769 | 0.6773 | +0.0004 |
| 8 | Calmness | 0.0000 | 0.0000 | +0.0000 |
| 9 | Contempt | 0.0000 | 0.0000 | +0.0000 |
| 10 | Confusion | 0.0000 | 0.0000 | +0.0000 |

### Baseline + CLIP PCs vs Baseline

| Rank | Emotion | Baseline `R^2` | Combined `R^2` | Delta |
|---:|---|---:|---:|---:|
| 1 | Aesthetic appreciation | 0.3549 | 0.4115 | +0.0567 |
| 2 | Amusement | 0.0114 | 0.0654 | +0.0540 |
| 3 | Excitement | 0.0907 | 0.1165 | +0.0258 |
| 4 | Valence | 0.2974 | 0.3212 | +0.0238 |
| 5 | Interest | 0.0632 | 0.0850 | +0.0218 |
| 6 | Surprise | 0.4791 | 0.4976 | +0.0185 |
| 7 | Empathic pain | 0.2008 | 0.2176 | +0.0168 |
| 8 | Sadness | 0.0000 | 0.0166 | +0.0166 |
| 9 | Adoration | 0.1427 | 0.1518 | +0.0090 |
| 10 | Uncomfortable | 0.6769 | 0.6796 | +0.0027 |

## Full Target-Wise Results

Columns:

- `Baseline`: Vision + Semantic
- `V-JEPA2 only`: brain-predictable V-JEPA2 PCs only
- `CLIP only`: brain-predictable CLIP PCs only
- `Base+VJ`: Vision + Semantic + V-JEPA2 PCs
- `Base+CLIP`: Vision + Semantic + CLIP PCs
- `Delta VJ`: `Base+VJ - Baseline`
- `Delta CLIP`: `Base+CLIP - Baseline`

| Target | Baseline | V-JEPA2 only | CLIP only | Base+VJ | Base+CLIP | Delta VJ | Delta CLIP |
|---|---:|---:|---:|---:|---:|---:|---:|
| Admiration | 0.0000 | 0.0235 | 0.0266 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Adoration | 0.1427 | 0.0805 | 0.1424 | 0.1546 | 0.1518 | +0.0118 | +0.0090 |
| Aesthetic appreciation | 0.3549 | 0.3231 | 0.4473 | 0.3936 | 0.4115 | +0.0387 | +0.0567 |
| Amusement | 0.0114 | 0.1159 | 0.3397 | 0.0178 | 0.0654 | +0.0063 | +0.0540 |
| Anger | 0.0000 | 0.0118 | 0.1818 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Anxiety | 0.0000 | 0.0611 | 0.2036 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Awe | 0.0000 | 0.0222 | 0.2096 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Awkwardness | 0.0000 | 0.0308 | 0.0913 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Boredom | 0.0000 | 0.0196 | 0.1011 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Calmness | 0.0000 | 0.1361 | 0.1655 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Confusion | 0.0000 | 0.0000 | 0.0291 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Contempt | 0.0000 | 0.0000 | 0.0493 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Craving | 0.3873 | 0.0166 | 0.1482 | 0.3911 | 0.3881 | +0.0038 | +0.0008 |
| Disgust | 0.0000 | 0.0088 | 0.0847 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Empathic pain | 0.2008 | 0.0741 | 0.1964 | 0.2000 | 0.2176 | -0.0008 | +0.0168 |
| Entrancement | 0.0000 | 0.0024 | 0.0564 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Excitement | 0.0907 | 0.2001 | 0.2866 | 0.1049 | 0.1165 | +0.0141 | +0.0258 |
| Fear | 0.0000 | 0.0000 | 0.0385 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Horror | 0.0000 | 0.0570 | 0.1709 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Interest | 0.0632 | 0.0598 | 0.2536 | 0.0691 | 0.0850 | +0.0059 | +0.0218 |
| Joy | 0.0000 | 0.0028 | 0.0289 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Nostalgia | 0.2984 | 0.0167 | 0.2100 | 0.2951 | 0.2976 | -0.0033 | -0.0007 |
| Relief | 0.0000 | 0.0576 | 0.1818 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Romance | 0.0000 | 0.0793 | 0.1236 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Sadness | 0.0000 | 0.0094 | 0.1922 | 0.0000 | 0.0166 | +0.0000 | +0.0166 |
| Satisfaction | 0.0000 | 0.0071 | 0.0544 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Sexual desire | 0.0000 | 0.0313 | 0.1058 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Surprise | 0.4791 | 0.0450 | 0.3308 | 0.4776 | 0.4976 | -0.0015 | +0.0185 |
| Sympathy | 0.0000 | 0.0059 | 0.1959 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Triumph | 0.0000 | 0.0128 | 0.0436 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Uncomfortable | 0.6769 | 0.1715 | 0.5379 | 0.6773 | 0.6796 | +0.0004 | +0.0027 |
| Annoyance | 0.0000 | 0.1057 | 0.1882 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Envy | 0.0000 | 0.0293 | 0.1030 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Guilt | 0.0000 | 0.0518 | 0.1211 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Arousal | 0.0000 | 0.0651 | 0.0621 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |
| Valence | 0.2974 | 0.0112 | 0.2706 | 0.2979 | 0.3212 | +0.0004 | +0.0238 |
| Dominance | 0.0000 | 0.0000 | 0.0565 | 0.0000 | 0.0000 | +0.0000 | +0.0000 |

## Interpretation

The cleanest reading of Exp 16 is:

1. Explicit vision and semantic features already explain a substantial amount of affective variance.
2. Brain-predictable model PCs are not redundant, because they still improve prediction beyond that baseline.
3. The incremental contribution is larger for CLIP than for V-JEPA2 in this setting.
4. The added value is selective rather than uniform, with the clearest gains for:
   - Aesthetic appreciation
   - Amusement
   - Excitement
   - Interest
   - Valence

So Exp 16 supports a moderate claim, not an extreme one:

- model PCs do contain information that is not fully recoverable from simple vision+semantic features,
- but much of the total explainable structure is still shared with those explicit features.
