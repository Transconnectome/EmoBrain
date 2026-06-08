#!/bin/bash
#SBATCH --job-name=p2_brainonly
#SBATCH --output=/pscratch/sd/s/sjmoon/FEELIN/output/slurm/p2_brainonly_%x_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/FEELIN/output/slurm/p2_brainonly_%x_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gpus=1
#SBATCH --time=03:00:00
#SBATCH --account=m4750_g
#SBATCH --qos=regular
#SBATCH --constraint=gpu
#
# Usage: sbatch --job-name=I_supervised _submit_method.sh I_supervised
#        sbatch --job-name=II_distillation _submit_method.sh II_distillation
#        sbatch --job-name=III_multitask _submit_method.sh III_multitask
#        sbatch --job-name=IV_subject_aware _submit_method.sh IV_subject_aware
# Runs all 4 tasks (V_binary, A_binary, V_reg, A_reg) sequentially for one method.

set -e
METHOD=${1:?"method name required (I_supervised, II_distillation, III_multitask, IV_subject_aware)"}
WRAP_DIR=/pscratch/sd/s/sjmoon/FEELIN/project/dir2_multimodal/code/legacy_phase2/brain_only/wrappers/${METHOD}

mkdir -p /pscratch/sd/s/sjmoon/FEELIN/output/slurm

for task in V_binary A_binary V_reg A_reg; do
    echo "===== ${METHOD} / ${task} ====="
    bash ${WRAP_DIR}/${task}.sh
    echo "===== done ${METHOD} / ${task} ====="
done
