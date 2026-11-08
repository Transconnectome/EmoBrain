#!/bin/bash
# Preprocessing census in dependency order. Read-only over all data.
#   q0   atlas on the fMRI grid                     (seconds)
#   q1   every step7 segment and filtered frame     (~7 min, 16 workers)
#   q2   CSV, .pt and fmri_raw against q1           (~2 min)
#   q3   label-blind response-window comparison     (~5 min)
#   q3b  presentation order versus content          (seconds)
set -euo pipefail
CODE=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/code
bash "$CODE/q0_atlas_grid.sh"
bash "$CODE/q1_voxel_census.sh" --workers 16
bash "$CODE/q2_derivation_chain.sh"
bash "$CODE/q3_response_window.sh"
bash "$CODE/q3b_order_design_audit.sh"
