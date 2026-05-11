#!/usr/bin/env python3
"""Prepare fresh Horikawa BFM extraction commands.

This writes command files under `setup/jobs/` that point outputs to NetFeeliX
fresh directories. It does not use old embedding caches.
"""

import argparse
import json
from pathlib import Path


ROOT = Path("/pscratch/sd/s/sjmoon")
NETFEELIX = ROOT / "NetFeeliX"
JOB_DIR = NETFEELIX / "setup/jobs"
FRESH_ROOT = NETFEELIX / "setup/results/fresh_embeddings/horikawa"


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)


def brain_jepa_script():
    out_dir = FRESH_ROOT / "brain_jepa"
    return f"""#!/bin/bash
set -euo pipefail

source /pscratch/sd/s/sjmoon/brain-jepa-env/bin/activate
cd /pscratch/sd/s/sjmoon/EmoDe/Foundation_baseline/Brain-JEPA

python run_embedding_extraction_horikawa.py \\
  --data_root_dir /pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_preprocess_JEPA_ROI \\
  --output_dir {out_dir} \\
  --mni_data_root /pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/img \\
  --finetune /pscratch/sd/s/sjmoon/EmoDe/Foundation_baseline/Brain-JEPA/pretrained_models/jepa-ep300.pth \\
  --model_name vit_base \\
  --crop_size 450,20 \\
  --patch_size 16 \\
  --attn_mode normal \\
  --add_w mapping \\
  --batch_size 64 \\
  --num_workers 8 \\
  --device cuda
"""


def neurostorm_script():
    out_dir = FRESH_ROOT / "neurostorm"
    return f"""#!/bin/bash
set -euo pipefail

source /pscratch/sd/s/sjmoon/neurostorm_env/bin/activate
cd /pscratch/sd/s/sjmoon/EmoDe/Foundation_baseline/NeuroSTORM

python run_embedding_extraction_horikawa.py \\
  --data_root /pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs \\
  --output_dir {out_dir} \\
  --ckpt_path /pscratch/sd/s/sjmoon/EmoDe/Foundation_baseline/NeuroSTORM/output/neurostorm/pt_neurostorm_mae_ratio0.5.ckpt \\
  --embed_dim 36 \\
  --batch_size 16 \\
  --num_workers 8 \\
  --device cuda
"""


def swift_script():
    raw_dir = FRESH_ROOT / "swift_v2/raw"
    pooled_dir = FRESH_ROOT / "swift_v2/pooled"
    return f"""#!/bin/bash
set -euo pipefail

cd /pscratch/sd/s/sjmoon/SwiFT_v2

module load python
module load cpe/23.03
conda activate /global/common/software/m4750/swift_PTL2

export MASTER_ADDR=$(/bin/hostname -s)
export MASTER_PORT=29600

CKPT_PATH=/pscratch/sd/j/jubchoi/Newdata_Phase3_MR0p6/UAH_P2_51M_MR_0p6_L1e-4/best.pt
IMAGE_PATH=/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs
SPLIT_FILE=/pscratch/sd/s/sjmoon/EmoDe/Foundation_baseline/SwiFT_v2/data/splits/Horikawa/pretraining/split_fixed_0_all.txt

python project/main_embedding_extraction.py \\
  --accelerator gpu --max_epochs 60 --precision 32 --num_nodes 1 --devices 1 --strategy deepspeed_stage_1 \\
  --loggername neptune --classifier_module v6 --dataset_name Horikawa --image_path ${{IMAGE_PATH}} --num_workers 8 \\
  --project_name seokjin14/SwiFT-EMBEDDING \\
  --c_multiplier 2 --last_layer_full_MSA True --clf_head_version v1 --downstream_task arousal --train_split 0.7 --val_split 0.15 --grad_clip --use_scheduler --gamma 0.5 --cycle 0.5 --use_MuTransfer \\
  --extract_embeddings --test_only --test_ckpt_path ${{CKPT_PATH}} --load_ds_ckpt_manually --eval_batch_size 1 --embedding_save_dir {raw_dir} --split_file_path ${{SPLIT_FILE}} \\
  --batch_size 16 --dataset_split_num 0 --seed 1 --learning_rate 7e-5 --model simmim_swin4d_ver9 --depth 2 2 18 2 --num_heads 6 12 24 48 \\
  --embed_dim 96 --first_window_size 4 4 4 4 --window_size 4 4 4 20 --sequence_length 20 --img_size 96 96 96 20 --use_mim --patch_size 6 6 6 2 --mask_patch_size 6 6 6 2 --mask_ratio 0.8 --input_scaling_method znorm_minback

/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python /pscratch/sd/s/sjmoon/SwiFT_v2/downstream_optuna/pooling_extracted_embeddings.py \\
  --input_dir {raw_dir} \\
  --output_dir {pooled_dir} \\
  --flat_structure \\
  --max_jobs 8
"""


def brain_lm_note():
    return """BrainLM fresh Horikawa extraction is not prepared yet.

Reason:
- The available local BrainLM repo exposes generic toolkit/inference notebooks.
- A Horikawa-specific extractor that converts the fresh fMRI windows into BrainLM's parcel/time-series format still needs to be implemented or verified.

Do not use `/pscratch/sd/t/tylee/BrainLM` as a benchmark cache.
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobs-dir", default=str(JOB_DIR))
    args = parser.parse_args()

    jobs_dir = Path(args.jobs_dir)
    scripts = {
        "run_fresh_brain_jepa_horikawa.sh": brain_jepa_script(),
        "run_fresh_neurostorm_horikawa.sh": neurostorm_script(),
        "run_fresh_swift_v2_horikawa.sh": swift_script(),
    }
    written = []
    for name, text in scripts.items():
        path = jobs_dir / name
        write(path, text)
        written.append(str(path))

    brain_lm_path = jobs_dir / "BrainLM_fresh_extraction_TODO.md"
    brain_lm_path.parent.mkdir(parents=True, exist_ok=True)
    brain_lm_path.write_text(brain_lm_note(), encoding="utf-8")
    written.append(str(brain_lm_path))

    manifest = {
        "fresh_root": str(FRESH_ROOT),
        "jobs": written,
        "benchmark_after_extraction": str(NETFEELIX / "setup/code/run_horikawa_bfm_benchmark.py"),
    }
    manifest_path = jobs_dir / "fresh_horikawa_bfm_extraction_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
