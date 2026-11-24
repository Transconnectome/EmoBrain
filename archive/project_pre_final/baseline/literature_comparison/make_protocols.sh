#!/bin/bash
# 공정 비교 분할표 (몇 초). bash /pscratch/sd/s/sjmoon/EmoBrain/project/baseline/literature_comparison/make_protocols.sh
set -euo pipefail
PYTHONDONTWRITEBYTECODE=1 /pscratch/sd/s/sjmoon/tribev2/.venv/bin/python /pscratch/sd/s/sjmoon/EmoBrain/project/baseline/literature_comparison/make_protocols.py
