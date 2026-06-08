#!/bin/bash
#SBATCH --account=m4641
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=00:30:00
#SBATCH --job-name=feelin_scientist
#SBATCH --output=/pscratch/sd/s/sjmoon/FEELIN/reports/scientist_%j.log

# 사용법: sbatch scientist_ai.sh /path/to/model_dir [/path/to/context.md]

MODEL_DIR=${1:?"모델 디렉토리 경로를 첫 번째 인자로 지정하세요"}
CONTEXT=${2:-""}

source /global/homes/s/sjmoon/.bashrc
source /pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

pip show anthropic > /dev/null 2>&1 || pip install anthropic -q

cd /pscratch/sd/s/sjmoon/FEELIN

if [ -n "$CONTEXT" ]; then
    python scripts/scientist_ai.py --model-dir "$MODEL_DIR" --context "$CONTEXT"
else
    python scripts/scientist_ai.py --model-dir "$MODEL_DIR"
fi
