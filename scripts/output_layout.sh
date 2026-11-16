#!/bin/bash
# 결과 폴더(output_root) 정리와 폴더별 README. GPU 없음, 몇 초. 규칙은 scripts/output_layout.py 머리말.
# 사용(레포 최상위): bash scripts/output_layout.sh [--dry-run] [--skip-moves]
#   학습이나 합치기가 끝날 때마다 다시 돌리면 새 결과의 링크와 README가 붙는다(옮기기는 이미 끝났으면 건너뜀).
set -euo pipefail
source "$(dirname "$0")/_env.sh"
"$PY_CPU" "$ROOT/scripts/output_layout.py" "$@"
