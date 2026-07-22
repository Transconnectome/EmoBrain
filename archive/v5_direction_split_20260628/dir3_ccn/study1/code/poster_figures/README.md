# CCN Poster Figure Export

This module is figure-only. It does not fit models or modify analysis outputs.

## Panels

1. Framework schematic.
2. Corrected Brain-JEPA shared-channel screen or permutation-confirmed result.
3. Brain-JEPA-independent raw-BOLD content/affect partition.
4. Corrected cortical maps and Yeo-network summaries when complete.
5. Full brain-encoder pretrained-minus-scratch consensus when complete.

Legacy Brain-JEPA cortical results are never used as a fallback. Every export
writes `poster_figure_manifest.json` and `.md` under
`study1/results/poster_export/`.

## Run Once

```bash
bash /pscratch/sd/s/sjmoon/EmoBrain/archive/v5_direction_split_20260628/dir3_ccn/study1/code/poster_figures/export_poster_figures.sh
```

## Watch Running Jobs

The command below exports immediately, then refreshes whenever corrected outputs
appear. It stops after 270 minutes or once every panel is complete.

```bash
bash /pscratch/sd/s/sjmoon/EmoBrain/archive/v5_direction_split_20260628/dir3_ccn/study1/code/poster_figures/export_poster_figures.sh \
  --watch-minutes 270 \
  --interval-seconds 120
```
