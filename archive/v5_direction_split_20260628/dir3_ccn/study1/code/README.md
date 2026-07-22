# Active Code

Only these directories are active:

| Module | Entry point | Scientific role |
|---|---|---|
| Shared alignment | `shared_alignment/run_shared_alignment.py` | Brain-JEPA predictability of video-model dimensions |
| Affective characterization | `affective_characterization/run_affective_characterization.py` | Continuous 34D and A/V functional probes |
| Cortical transformation | `cortical_transformation/run_cortical_transformation.py` | LOSO parcel encoding, unique variance, networks, and gradient |
| Content-affect partition | `content_affect_partition/run_content_affect_partition.py` | No-video-PCA content controls and dimension-matched affective variance |
| Brain-encoder validation | `brain_encoder_validation/` | Corrected frozen Brain-JEPA extraction and cross-encoder consensus |

Each entry point has a same-name `.md` and `.sh`. Details, inputs, outputs, and interpretation guardrails are documented next to the script.

Everything in `archive/` is historical. Active code must not depend on it.

Brain-JEPA-dependent outputs from the original extraction are provisional because
the legacy loader averaged 10 fixed temporal position codes into one. Use
`brain_encoder_validation/extract_brain_jepa_frozen.py` for the corrected frozen
condition. Raw-BOLD content-affect partitioning is not affected by this issue.
