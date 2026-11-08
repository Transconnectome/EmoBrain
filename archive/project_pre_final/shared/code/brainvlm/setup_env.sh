#!/bin/bash
# BrainVLM_qwen env setup for EmoBrain.
#
# 한 번 paste 해서 실행. ~10-20 min 걸림.
# 결과: /pscratch/sd/s/sjmoon/brainvlm_qwen_env/ conda env 생성

set -e

ENV_PATH=/pscratch/sd/s/sjmoon/brainvlm_qwen_env

echo "=== 0. NERSC module load (conda 사용 가능하게) ==="
module load python
module load cpe/23.03 2>/dev/null || true
which conda || { echo "ERROR: conda not found even after module load python"; exit 1; }

echo ""
echo "=== 1. Conda env 생성 (Python 3.11) ==="
conda create -y -p "$ENV_PATH" python=3.11 pip

echo ""
echo "=== 2. env 활성화 ==="
# conda activate 가 script 안에서는 source 필요
source $(conda info --base)/etc/profile.d/conda.sh
conda activate "$ENV_PATH"
which python
python --version

echo ""
echo "=== 3. PyTorch 2.11 + CUDA 12.4 설치 ==="
# 주의: environment.yml 의 torchvision==0.25 은 torch 2.10 과 페어. 우리는 torch 2.11 이므로 torchvision 0.26 사용.
pip install torch==2.11.0 torchvision==0.26.0 triton==3.6.0

echo ""
echo "=== 4. transformers DEV BUILD (Qwen3-VL 지원) ==="
# 5.3.0.dev0 은 PyPI 에 없음, github main branch 에서 install
pip install git+https://github.com/huggingface/transformers.git@main
pip install tokenizers==0.22.2 accelerate==1.13.0 datasets==2.19.0 \
            safetensors==0.4.5 huggingface-hub==0.25.1 sentencepiece==0.1.99 peft==0.18.1

echo ""
echo "=== 5. DeepSpeed ==="
pip install deepspeed==0.12.3

echo ""
echo "=== 6. Neuroimaging + scientific ==="
pip install monai==1.5.2 nibabel==5.4.2
pip install numpy==1.25.2 pandas==2.2.3 scipy==1.15.2 scikit-learn==1.7.1 einops==0.8.0

echo ""
echo "=== 7. Config / logging / IO ==="
pip install PyYAML==6.0.1 omegaconf==2.3.0 tqdm==4.67.3 wandb==0.25.1 pillow==10.4.0

echo ""
echo "=== 8. Verify install ==="
python <<'PY'
import torch, transformers, peft, monai, deepspeed
print(f"  torch        : {torch.__version__}")
print(f"  transformers : {transformers.__version__}")
print(f"  peft         : {peft.__version__}")
print(f"  monai        : {monai.__version__}")
print(f"  deepspeed    : {deepspeed.__version__}")
print(f"  CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"  device count : {torch.cuda.device_count()}")
    print(f"  device name  : {torch.cuda.get_device_name(0)}")
# Try import a Qwen3-VL config (test transformers version)
try:
    from transformers import Qwen3VLConfig
    print(f"  Qwen3VLConfig: OK (transformers supports Qwen3-VL)")
except Exception as e:
    print(f"  Qwen3VLConfig: FAIL ({type(e).__name__}: {e})")
PY

echo ""
echo "=== 9. Env vars (다음 사용 시 source activate 후 적용) ==="
echo "다음을 ~/.bashrc 또는 sbatch script 상단에 추가:"
echo "  source activate $ENV_PATH"
echo "  export TORCH_EXTENSIONS_DIR=/pscratch/sd/s/sjmoon/torch_extensions"
echo "  export HF_HOME=/pscratch/sd/s/sjmoon/huggingface"
echo "  export TORCH_HOME=/pscratch/sd/s/sjmoon/torch_cache"

echo ""
echo "=== Done. Env at: $ENV_PATH ==="
