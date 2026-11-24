#!/bin/bash
# SwiFT_NewE36 frozen probe: Arousal continuous regression. Padding=zero (variants extracted with zero).
# 2 init × 1 task × 2 mode × 2 head × 5 fold × 1 seed.  ~20-30min.
# Usage: bash <this>.sh [padding]  (default: zero)
set -e
PADDING="${1:-zero}"
cd /pscratch/sd/s/sjmoon/EmoBrain
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/probes/run_unified_probe.py \
    --config_set swift_variants \
    --swift_variants_padding "${PADDING}" \
    --features SwiFT_NewE36 \
    --tasks A_reg \
    --out_csv "results/phase1/bfm_probe_SwiFT_NewE36_${PADDING}_A_reg.csv" \
    --summary_csv "results/phase1/bfm_probe_SwiFT_NewE36_${PADDING}_A_reg_summary.csv"
