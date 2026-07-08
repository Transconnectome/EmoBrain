"""Pre-download the Qwen backbone on a LOGIN node (internet) into a scratch HF
cache, so the OFFLINE compute node can load it during sbatch.

NERSC compute nodes have no internet. Run this once on a login node; the sbatch
sets HF_HOME to the same scratch cache and HF_HUB_OFFLINE=1 to load locally.

Run.
    bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/predownload_qwen.sh
    (optional) QWEN_MODEL=Qwen/Qwen2.5-1.5B-Instruct bash .../predownload_qwen.sh
"""
from __future__ import annotations

import os

os.environ.setdefault("HF_HOME", "/pscratch/sd/s/sjmoon/hf_cache")

from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

MODEL = os.environ.get("QWEN_MODEL", "Qwen/Qwen2.5-3B-Instruct")


def main():
    print(f"[predownload] model = {MODEL}")
    print(f"[predownload] HF_HOME = {os.environ['HF_HOME']}")
    AutoTokenizer.from_pretrained(MODEL)
    AutoModelForCausalLM.from_pretrained(MODEL)
    print("[predownload] cached OK. compute node can now load offline.")


if __name__ == "__main__":
    main()
