#!/bin/bash
# SwiFT_UAH_51M frozen probe: Arousal extreme binary. Padding=zero (variants extracted with zero).
# 2 init × 1 task × 2 mode × 2 head × 5 fold × 1 seed.  ~20-30min.
# Usage: bash <this>.sh [padding]  (default: zero)
set -e
PADDING="${1:-zero}"
cd /pscratch/sd/s/sjmoon/FEELIN
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/probes/run_unified_probe.py \
    --config_set swift_variants \
    --swift_variants_padding "${PADDING}" \
    --features SwiFT_UAH_51M \
    --tasks A_binary \
    --out_csv "results/phase1/bfm_probe_SwiFT_UAH_51M_${PADDING}_A_binary.csv" \
    --summary_csv "results/phase1/bfm_probe_SwiFT_UAH_51M_${PADDING}_A_binary_summary.csv"
