# Short-Window Benchmark

## Questions

1. Does corrected one-patch Brain-JEPA retain a pretrained advantage over scratch?
2. Is the conclusion stable to native, legacy-mean, and center position policies?
3. Is it stable to mean and zero padding?
4. Does the representation use within-window temporal values or temporal order?
5. Does Brain-JEPA improve on an event-level raw-BOLD benchmark?

## Outputs

- `embedding_stability.csv`: CKA, RSA, and nearest-neighbor overlap between variants
- `direct_geometry_cka.csv`: descriptive alignment with V-JEPA2/content/affect
- `fold_encoding_scores.csv`: nested held-out ridge scores
- `planned_contrasts.csv`: subject-wise pretrained, position, padding, and temporal effects
- `length_stratified_cka.csv`: dependence on original stimulus duration

Target PCA and ridge selection are fit within training data. The five-subject t tests
are exploratory; effect direction and subject consistency are primary.

Run after all 35 extraction tasks finish:

```bash
bash run_short_window_benchmark.sh
```

This analysis uses Brain-JEPA plus raw BOLD only. SwiFT and NeuroSTORM are not
required to validate the Brain-JEPA adapter itself; they answer the separate question
of cross-architecture generality.
