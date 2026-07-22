# Horikawa Extraction Matrix

The SLURM array extracts seven conditions for five subjects (35 tasks):

| Condition | Purpose |
|---|---|
| pretrained, native, mean | Corrected primary |
| scratch, native, mean | Pretraining contribution |
| pretrained, temporal-mean, mean | Exact legacy positional sensitivity |
| pretrained, temporal-center, mean | Alternative positional sensitivity |
| pretrained, native, zero | Padding sensitivity |
| pretrained, native, spatial-only | Remove within-window temporal information |
| pretrained, native, time-shuffle | Destroy temporal order while retaining samples |

Run the full matrix sequentially from an allocated GPU shell:

```bash
bash run_horikawa_extraction.sh
```

Run one task only with `bash run_horikawa_extraction.sh TASK_ID`, where task IDs are
0-34. The script still accepts `SLURM_ARRAY_TASK_ID` when explicitly used as an array,
but it does not require SLURM.

The package does not submit jobs automatically. Results are isolated under
`outputs/horikawa_embeddings/` and the original Brain-JEPA repository is read-only.

Swift padding robustness is useful supporting evidence, but it does not replace this
minimal Brain-JEPA-specific test because SwiFT does not undergo the 10-to-1 temporal
token adaptation.
