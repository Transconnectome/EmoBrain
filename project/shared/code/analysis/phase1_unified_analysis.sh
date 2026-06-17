#!/bin/bash
# Phase 1 결과 통합 분석. CPU 만, 1분 안에 끝남.
set -e
cd /pscratch/sd/s/sjmoon/EmoBrain
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/analysis/phase1_unified_analysis.py
