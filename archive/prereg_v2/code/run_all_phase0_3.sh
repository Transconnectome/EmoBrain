#!/bin/bash
# Phase 0 to 3 in dependency order. Read-only over all data; every artifact
# lands under prereg_v2/ and a previous artifact is moved to
# manifests/superseded/ rather than overwritten.
#
#   p0   A1-1  inventory and checksums          (~3 min, walks 270 GB of trees)
#   p1   A1-2  A1-3 stimulus and participant crosswalk  (~5 min, decodes 2196 clips)
#   p1b  A1-4  event and run audit              (~2 min)
#   p1c        repeat structure magnitude       (~1 min)
#   p2   A2-*  annotation audit                 (<1 min)
#   p3   A3-1  A3-2 splits and leakage tests    (~1 min)
#   p3b        leakage negative control         (<1 min)
#   p3c  A3-4  inference contract, A0-2 env lock(<1 min)
set -euo pipefail
CODE=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/code
for s in p0_inventory p1_stimulus_crosswalk p1b_event_run_audit p1c_repeat_reliability \
         p2_annotation_audit p3_splits_leakage p3b_leakage_negative_control \
         p3c_inference_contract; do
  echo "================ $s ================"
  bash "$CODE/$s.sh"
done
echo "================ contract tests ================"
/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python \
  /pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/tests/test_inference_contract.py
