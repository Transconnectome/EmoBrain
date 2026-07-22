# Corrected Brain-JEPA Reanalysis

This module is the only entry point for CCN analyses that depend on the corrected
frozen Brain-JEPA embeddings. It does not modify the legacy raw input or legacy
results.

## Data Contract

- Source: five `sub-XX.npz` files from the external short-window validation.
- Position policy: native one-patch sin/cos code; the mismatched checkpoint
  `emb_h` is omitted.
- Shape: `(5 subjects, 2185 canonical stimuli, 768 features)`.
- CCN input: `study1/data/corrected_reanalysis/brain_jepa_native_1patch.npy`.
- Provenance: the adjacent JSON records source hashes and checkpoint audit fields.

## Fast Order

Run one stage at a time and inspect its result before starting the next stage.

```bash
bash run_corrected_reanalysis.sh prepare
bash run_corrected_reanalysis.sh shared-screen
bash run_corrected_reanalysis.sh geometry
```

`shared-screen` computes observed cross-validated alignment without permutations.
It is a directional screen, not inferential evidence.

After selecting a defensible rank from the corrected shared result and the cortical
rank diagnostic, run:

```bash
bash run_corrected_reanalysis.sh cortical 3
```

Replace `3` only if the corrected shared analysis supports a different rank. The
full cortical run saves brain maps and held-out rank diagnostics under
`study1/results/corrected_reanalysis/cortical_transformation/`.

Permutation confirmation and the Brain-JEPA-independent content analysis remain
separate stages:

```bash
bash run_corrected_reanalysis.sh shared-confirm
bash run_corrected_reanalysis.sh content
```

Use `CCN_N_PERM` or `CCN_N_SHUFFLES` to change the corresponding null count. Full
analyses are run by the user; Codex performs only syntax and lightweight contract
checks.

## Interpretation Order

1. Establish whether corrected pretrained Brain-JEPA has reproducible V-JEPA2
   alignment across subjects.
2. Estimate compactness without assuming the accepted rank of three.
3. Characterize affective enrichment relative to arousal-valence and matched
   video-space controls.
4. Localize shared and complementary affective variance in held-out cortical BOLD.

The one-patch encoder is described as a spatially organized encoder of short-window
evoked responses. It does not establish long-range temporal dynamics.
