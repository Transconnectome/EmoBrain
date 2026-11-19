#!/bin/bash
# S10 핵심 시험 첫 판(06 4절). 6-4d 저장값만 쓴다. CPU, 로그인 노드, 1분 안쪽. 레포 최상위에서 실행한다.
# 사용: bash scripts/s10_key_test.sh
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
"$PY_CPU" s10_key_test.py --stats "$OUT_ROOT/s10_stats/beyond_scene" --out "$OUT_ROOT/s10_stats/key_test_v1"
# 11/18 둘째 판: 물체 = 물체 단어 캡션(N), 그리고 물체 + 속성(NA)과 전체 캡션(C)
if [ -f "$OUT_ROOT/s10_stats/beyond_scene_levels/scores.tsv" ]; then
  "$PY_CPU" s10_key_test.py --stats "$OUT_ROOT/s10_stats/beyond_scene_levels" --out "$OUT_ROOT/s10_stats/key_test_v2_N_C" --object N --situation C
  "$PY_CPU" s10_key_test.py --stats "$OUT_ROOT/s10_stats/beyond_scene_levels" --out "$OUT_ROOT/s10_stats/key_test_v2_N_NA" --object N --situation NA
  "$PY_CPU" s10_key_test.py --stats "$OUT_ROOT/s10_stats/beyond_scene_levels" --out "$OUT_ROOT/s10_stats/key_test_v2_NA_C" --object NA --situation C
fi
# 11/18 셋째 판: parser 판. GO 대 GR(물체 대 object relations까지), GA 대 GR(관계만의 단계), GR 대 C(부사와 문장 구조의 단계), GO 대 C
if [ -f "$OUT_ROOT/s10_stats/beyond_scene_levels_graph/scores.tsv" ]; then
  G="$OUT_ROOT/s10_stats/beyond_scene_levels_graph"
  "$PY_CPU" s10_key_test.py --stats "$G" --out "$OUT_ROOT/s10_stats/key_test_v3_GO_GR" --object GO --situation GR
  "$PY_CPU" s10_key_test.py --stats "$G" --out "$OUT_ROOT/s10_stats/key_test_v3_GA_GR" --object GA --situation GR
  "$PY_CPU" s10_key_test.py --stats "$G" --out "$OUT_ROOT/s10_stats/key_test_v3_GR_C" --object GR --situation C
  "$PY_CPU" s10_key_test.py --stats "$G" --out "$OUT_ROOT/s10_stats/key_test_v3_GO_C" --object GO --situation C
fi
