#!/bin/bash
set -euo pipefail

REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
TEACHER_CFG="${REPO_ROOT}/project/code/configs/e2_brain_jepa_teacher_qwen3vl4b.yaml"
STUDENT_CFG="${REPO_ROOT}/project/code/configs/e2_brain_jepa_distill_qwen3vl4b.yaml"

bash "${REPO_ROOT}/project/code/training/train_teacher.sh" "${TEACHER_CFG}"
bash "${REPO_ROOT}/project/code/training/cache_soft_labels.sh" "${TEACHER_CFG}"
bash "${REPO_ROOT}/project/code/training/train_student_distill.sh" "${STUDENT_CFG}"
