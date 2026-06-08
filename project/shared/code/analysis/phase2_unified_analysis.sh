#!/bin/bash
# Phase 2 결과 통합 분석. CPU 만, 1 분 안에 끝남.
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/analysis/phase2_unified_analysis.py
