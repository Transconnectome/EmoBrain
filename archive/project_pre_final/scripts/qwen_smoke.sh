#!/bin/bash
# One-shot smoke: does the real Qwen3-VL-4B backbone load + forward end-to-end?
# Writes the result to project/output/qwen_smoke.txt so it can be inspected
# without copy-pasting stdout. Run on a GPU node.
#
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/qwen_smoke.sh
set -uo pipefail

REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
export HF_HOME=/pscratch/sd/s/sjmoon/hf_cache
mkdir -p "${REPO_ROOT}/project/output"
OUT="${REPO_ROOT}/project/output/qwen_smoke.txt"

cd "${REPO_ROOT}"
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python - > "${OUT}" 2>&1 <<'PY'
import torch, sys, traceback
sys.path.insert(0, ".")
print("cuda_available:", torch.cuda.is_available())
try:
    from project.code.fusion.build import build_model
    cfg = {
        "encoder":  {"type": "bfm", "model": "brain_jepa", "adapt": "frozen", "emb_dim": 768},
        "projector": {"type": "mlp", "n_tokens": 8},
        "backbone": {"type": "qwen", "hf_model": "Qwen/Qwen3-VL-4B-Instruct",
                     "dtype": "bfloat16", "frozen": True,
                     "lora": {"r": 16, "lora_alpha": 32, "lora_dropout": 0.05,
                              "target_modules": ["q_proj", "v_proj"]}},
        "modalities": {"brain": True},
    }
    m = build_model(cfg).to("cuda")
    out = m(torch.randn(2, 768).to("cuda"))
    print("FORWARD_OK", tuple(out.shape), out.dtype)
except Exception:
    print("FORWARD_FAILED")
    traceback.print_exc()
PY
echo "wrote ${OUT}"
cat "${OUT}"
