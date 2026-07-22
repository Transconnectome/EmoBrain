# Brain-JEPA Short-Window Validation

Standalone validation of adapting a Brain-JEPA checkpoint trained at 160 TR
(10 temporal patches) to 16 TR (one temporal patch).

## Isolation

The upstream repository at `../Brain-JEPA/` is imported read-only. This package does
not modify its source, configuration, or checkpoint. All code, logs, embeddings, and
results live in this sibling directory.

## Scientific distinction

The package tests two different claims:

1. **Short-window transfer validity:** corrected one-patch embeddings retain learned,
   stable, stimulus-relevant structure beyond scratch and preprocessing controls.
2. **Native temporal equivalence:** aggregated 16-TR embeddings preserve part of the
   geometry of native 160-TR Brain-JEPA embeddings.

The first can be tested now on Horikawa. The second requires a compatible long
rs-fMRI ROI array and is intentionally not inferred from Horikawa padding tests.

## Workflow

Run the required Horikawa workflow sequentially from an allocated GPU shell. This
runs only corrected pretrained, corrected scratch, and legacy temporal-mean for all
five subjects:

```bash
bash run_horikawa_validation.sh
```

Or run each stage separately:

1. Checkpoint audit:

   ```bash
   bash checkpoint_audit/run_checkpoint_audit.sh
   ```

2. Seven-condition, five-subject extraction matrix:

   ```bash
   bash horikawa_extraction/run_horikawa_extraction.sh
   ```

3. After all extraction tasks finish:

   ```bash
   bash short_window_benchmark/run_short_window_benchmark.sh
   ```

4. Optional native-length validation when a compatible array is available:

   ```bash
   bash native_length_validation/run_native_length_validation.sh /path/to/rest.npy
   ```

Codex prepares and smoke-tests these scripts but does not run the full workflow.

## Why Brain-JEPA-specific padding checks remain

SwiFT's padding robustness is useful evidence that the Horikawa result is not
generically driven by padding. It is not sufficient to validate Brain-JEPA's
10-to-1 temporal-token adaptation because the encoders have different patchification,
positional handling, and attention regimes. The minimal Brain-JEPA matrix therefore
uses only mean, zero, spatial-only, and time-shuffled inputs rather than repeating
every historical padding variant.

## Decision rules

- `pretrained native > scratch native`: resting-state pretraining transfers.
- native, legacy-mean, and center agree: positional adaptation does not drive the result.
- mean and zero agree: padding values do not drive the result.
- mean exceeds spatial-only: within-window temporal variation contributes.
- mean exceeds time-shuffle: temporal order contributes.
- corrected Brain-JEPA is stable against raw BOLD: the compressed representation is
  scientifically usable, even if raw BOLD remains the cortical localization standard.
- native-160 and aggregated-short geometry agree more for pretrained than scratch:
  strongest evidence for legitimate short-window transfer.
