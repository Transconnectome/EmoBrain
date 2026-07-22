# Final Results

| Directory | Status |
|---|---|
| `accepted_abstract/` | Figures associated with the accepted CCN abstract and camera-ready version |
| `cortical_transformation/` | Current poster-development maps, tables, and rank diagnostics |
| `cortical_transformation/smoke/` | Pipeline validation only; never use for scientific inference |
| `content_affect_partition/` | No-PCA raw-video, visual-semantic, and affective variance partition |
| `content_affect_partition/smoke/` | Pipeline validation only; never use for scientific inference |
| `brain_encoder_validation/` | Corrected-position and cross-encoder consensus results |
| `archive/legacy_figures/` | Exploratory and superseded figures |

The results root stays free of loose files. Every active module writes to one named directory containing its configuration, machine-readable results, tables, and figures.

Until `brain_encoder_validation/consensus/` is complete, all results that depend on
the legacy Brain-JEPA/V-JEPA2 shared scores are provisional. Raw-BOLD models that
condition directly on V-JEPA2 and visual-semantic features are unaffected.
