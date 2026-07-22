#!/bin/bash
# Run the complete Brain-JEPA Horikawa validation sequentially.
# Usage: bash run_horikawa_validation.sh

set -euo pipefail

ROOT="/pscratch/sd/s/sjmoon/EmoBrain/external/Brain-JEPA_short_window_validation"

echo "[1/3] Checkpoint audit"
bash "$ROOT/checkpoint_audit/run_checkpoint_audit.sh"

echo "[2/3] Required Horikawa extraction (3 conditions x 5 subjects)"
for TASK_ID in $(seq 0 14); do
  bash "$ROOT/horikawa_extraction/run_horikawa_extraction.sh" "$TASK_ID"
done

echo "[3/3] Short-window benchmark"
bash "$ROOT/short_window_benchmark/run_short_window_benchmark.sh" \
  --conditions pre_native_mean scratch_native_mean pre_legacy_mean

echo "Validation complete: $ROOT/outputs"
