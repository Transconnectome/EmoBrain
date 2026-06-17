#!/bin/bash
# Phase 1 benchmark table 생성. CPU 만, 수 초.
set -e
cd /pscratch/sd/s/sjmoon/EmoBrain
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/analysis/phase1_benchmark_table.py
