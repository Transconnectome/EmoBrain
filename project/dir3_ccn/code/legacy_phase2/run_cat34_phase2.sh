#!/bin/bash
# Phase 2 Cat34 launch — runs all 8 paradigms × 2 Cat34 tasks sequentially.
#
# 8 paradigms:
#   Brain-only: I_supervised  II_distillation  III_multitask  IV_subject_aware
#   Joint:      D_late_fusion  A_token_attn    B_cross_attn   C_contrastive
#
# 2 tasks: Cat34_multilabel, Cat34_soft
#
# Wall time estimate: ~3-5 hr total on a single GPU.
# Brain-only ~10 min/task, joint A/B ~30 min/task, D ~5 min/task,
# C alignment is task-agnostic (already trained from V/A run), so we just re-probe.
#
# Usage:
#   bash project/dir2_multimodal/code/legacy_phase2/run_cat34_phase2.sh                # all 16 cells sequentially
#   bash project/dir2_multimodal/code/legacy_phase2/run_cat34_phase2.sh joint          # only joint 4 methods
#   bash project/dir2_multimodal/code/legacy_phase2/run_cat34_phase2.sh brain_only     # only brain-only 4 methods
set -e
cd /pscratch/sd/s/sjmoon/EmoBrain

PY_PHASE1=/pscratch/sd/s/sjmoon/swift_PTL2/bin/python                 # phase 2 joint scripts use this env
PY_BRAIN=/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python           # brain-only scripts use this env
TASKS=(Cat34_multilabel Cat34_soft)
TARGET=${1:-all}                                                       # all / brain_only / joint

mkdir -p /pscratch/sd/s/sjmoon/EmoBrain/project/shared/output/slurm

run_brain_only() {
  for task in "${TASKS[@]}"; do
    echo "===== Brain-only I_supervised / $task ====="
    $PY_BRAIN project/dir2_multimodal/code/legacy_phase2/brain_only/train_brain_supervised.py --task $task

    echo "===== Brain-only II_distillation / $task ====="
    $PY_BRAIN project/dir2_multimodal/code/legacy_phase2/brain_only/train_brain_distillation.py --task $task

    echo "===== Brain-only III_multitask / $task ====="
    $PY_BRAIN project/dir2_multimodal/code/legacy_phase2/brain_only/train_brain_multitask.py --task $task

    echo "===== Brain-only IV_subject_aware / $task ====="
    $PY_BRAIN project/dir2_multimodal/code/legacy_phase2/brain_only/train_brain_subject_aware.py --task $task
  done
}

run_joint() {
  for task in "${TASKS[@]}"; do
    echo "===== Joint D late_fusion / $task ====="
    $PY_PHASE1 project/dir2_multimodal/code/legacy_phase2/train_supervised.py --arch D --task $task

    echo "===== Joint A token_transformer / $task ====="
    $PY_PHASE1 project/dir2_multimodal/code/legacy_phase2/train_supervised.py --arch A --task $task

    echo "===== Joint B cross_attention / $task ====="
    $PY_PHASE1 project/dir2_multimodal/code/legacy_phase2/train_supervised.py --arch B --task $task

    # C contrastive: alignment is task-agnostic, reuse existing aligners.
    # If aligner ckpts already exist (results/phase2/C/aligner_fold*_seed*.pt), skip Stage 1.
    if ! ls results/phase2/C/aligner_fold*_seed*.pt > /dev/null 2>&1; then
      echo "===== Joint C Stage 1 (alignment) ====="
      $PY_PHASE1 project/dir2_multimodal/code/legacy_phase2/train_contrastive.py
    else
      echo "===== Joint C Stage 1 aligners present, skipping training ====="
    fi
    echo "===== Joint C probe_brain_only / $task ====="
    $PY_PHASE1 project/dir2_multimodal/code/legacy_phase2/probe_contrastive.py --task $task --probe_input brain_only
    echo "===== Joint C probe_joint / $task ====="
    $PY_PHASE1 project/dir2_multimodal/code/legacy_phase2/probe_contrastive.py --task $task --probe_input joint
  done
}

case $TARGET in
  brain_only) run_brain_only ;;
  joint)      run_joint ;;
  all)        run_brain_only; run_joint ;;
  *)          echo "Unknown target: $TARGET. Use: brain_only / joint / all"; exit 1 ;;
esac

echo ""
echo "===== ALL DONE ($TARGET) ====="
echo "Results:"
ls -1 results/phase2/brain_only/*/Cat34_*.csv 2>/dev/null | sort
ls -1 results/phase2/{A,B,D}/Cat34_*.csv      2>/dev/null | sort
ls -1 results/phase2/C/probe_*Cat34*.csv      2>/dev/null | sort
