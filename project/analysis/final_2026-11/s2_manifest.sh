#!/bin/bash
# S2: 분할, 내용 구역, 이름표 짝, ROI, CAB-NP 묶음, MC 표를 파일로 고정한다. 앞 단계부터 순서대로 돈다. CPU, login node, 약 10분. 실패하면 멈춘다.
set -euo pipefail
PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 /pscratch/sd/s/sjmoon/tribev2/.venv/bin/python /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11/s2_manifest.py --stage "${1:-all}"
