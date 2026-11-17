"""
EmoBrain BrainVLM fold 1 V/A training.

Strategy: import upstream UMBRELLA Qwen3-VL training pipeline, monkey-patch the
dataset's brain-scan loader so it reads our .pt files (shape (1,1,96,96,96,T))
instead of relying on MONAI's nibabel-based loader.

Trainable parameters: PatchEmbedQwen + CustomNoPoolingTriPlanarMerger (~42M).
Frozen: Qwen3-VL ViT + LLM backbone.

Usage:
    python train_brainvlm.py --fold 1 --config <yaml> --epochs 1 [--smoke]

Default smoke = limit to 50 train + 10 val samples for sanity (~10 min).
Full = no limit (~6 hr per epoch for 5 subj × 1742 stim, batch=1).
"""
import argparse
import logging
import sys
from pathlib import Path

import numpy as np
import torch

# Stubs to let deepspeed import succeed on this env (incompatible torch+numpy versions).
# accelerate.unwrap_model imports deepspeed unconditionally; we don't need DeepSpeed for
# single-GPU training, but the import chain must not crash.
import torch.distributed.elastic.agent.server.api as _elastic_api
if not hasattr(_elastic_api, "log"):
    _elastic_api.log = _elastic_api.logger
if not hasattr(_elastic_api, "_get_socket_with_port"):
    def _stub_get_socket_with_port(*a, **kw):
        raise RuntimeError("_get_socket_with_port stub")
    _elastic_api._get_socket_with_port = _stub_get_socket_with_port
import numpy as _np
if not hasattr(_np, "BUFSIZE"):
    _np.BUFSIZE = 8192

EmoBrain = Path("/pscratch/sd/s/sjmoon/EmoBrain")
BRAINVLM = Path("/pscratch/sd/s/sjmoon/BrainVLM/UMBRELLA_qwen")

for p in (BRAINVLM, BRAINVLM / "project"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s :: %(message)s")
log = logging.getLogger("feelin.brainvlm")


def patch_dataset_for_pt_files():
    """Override UMBRELLADatasetQwen._load_brain_scans to load EmoBrain .pt files directly.

    Our .pt files are (1, 1, 96, 96, 96, T) tensors saved by convert_horikawa_fmri.py.
    The upstream loader expects nibabel-readable (.nii.gz) files and applies MONAI
    transforms. We bypass that and return the .pt tensor as-is, squeezing the leading
    batch dim so downstream collation works (expects per-sample shape).
    """
    from dataset.umbrella_dataset_qwen import UMBRELLADatasetQwen

    def _load_brain_scans_pt(self, scan_paths):
        scans = []
        target_paths = scan_paths[: self.max_images_per_sample]
        for scan_path in target_paths:
            try:
                t = torch.load(scan_path, weights_only=False, map_location="cpu")
                if hasattr(t, "as_tensor"):
                    t = t.as_tensor()
                if not isinstance(t, torch.Tensor):
                    t = torch.tensor(t)
                # Our .pt has shape (1, 1, 96, 96, 96, T). Strip the outer batch dim
                # so each per-sample tensor is (1, 96, 96, 96, T) = (C, D, H, W, T).
                while t.dim() > 5 and t.shape[0] == 1:
                    t = t[0]
                scans.append(t.float())
            except Exception as e:
                log.warning(f"Failed to load brain scan {scan_path}: {e}")
                fallback = torch.zeros((1, 96, 96, 96, 20))
                scans.append(fallback)
        if not scans:
            return torch.zeros((1, 1, 96, 96, 96, 20))
        return torch.stack(scans, dim=0)

    UMBRELLADatasetQwen._load_brain_scans = _load_brain_scans_pt
    log.info("Patched UMBRELLADatasetQwen._load_brain_scans for .pt files")


def maybe_subset_dataset(dataset, n_keep: int, label: str):
    """For smoke: truncate to first n_keep samples."""
    if n_keep is None or n_keep >= len(dataset):
        return dataset
    log.info(f"  smoke: {label} dataset {len(dataset)} -> {n_keep}")
    return torch.utils.data.Subset(dataset, list(range(n_keep)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fold", type=int, default=1)
    ap.add_argument("--config", default=str(EmoBrain / "project/shared/code/brainvlm/config_feelin_fold1_VA.yaml"))
    ap.add_argument("--conv_root", default=str(EmoBrain / "project/shared/output/brainvlm_conversations/pad-zero_VA"))
    ap.add_argument("--output_dir", default=None)
    ap.add_argument("--epochs", type=int, default=None,
                    help="override yaml max_epochs")
    ap.add_argument("--smoke", action="store_true",
                    help="limit to 50 train + 10 val samples; 1 epoch")
    ap.add_argument("--batch_size", type=int, default=None)
    ap.add_argument("--skip_eval", action="store_true",
                    help="skip in-trainer evaluation (upstream eval has pooler_output bug); "
                         "set this for training-only runs.")
    args = ap.parse_args()

    np.random.seed(1234); torch.manual_seed(1234)

    fold_dir = Path(args.conv_root) / f"fold{args.fold}"
    train_jsonls = sorted(fold_dir.glob("train/*.jsonl"))
    val_jsonls   = sorted(fold_dir.glob("val/*.jsonl"))
    assert train_jsonls, f"no train JSONL under {fold_dir}/train"
    if args.skip_eval:
        val_jsonls = []
        log.info(f"fold {args.fold}: {len(train_jsonls)} train JSONLs, val skipped (--skip_eval)")
    else:
        log.info(f"fold {args.fold}: {len(train_jsonls)} train JSONLs, {len(val_jsonls)} val")

    patch_dataset_for_pt_files()

    # In transformers >=4.57, Qwen3VLVisionModel.forward returns a plain
    # (hidden_states, deepstack_feature_lists) tuple. Upstream BrainVLM accesses
    # `.pooler_output` and `.deepstack_features`. Wrap the tuple return so both
    # tuple-unpacking and attribute access work.
    from transformers.models.qwen3_vl.modeling_qwen3_vl import Qwen3VLVisionModel
    class _VisualOutput(tuple):
        def __new__(cls, hidden_states, deepstack_features):
            obj = super().__new__(cls, (hidden_states, deepstack_features))
            return obj
        @property
        def pooler_output(self):
            return self[0]
        @property
        def last_hidden_state(self):
            return self[0]
        @property
        def deepstack_features(self):
            return self[1]
    _orig_visual_forward = Qwen3VLVisionModel.forward
    def _patched_visual_forward(self, *a, **kw):
        out = _orig_visual_forward(self, *a, **kw)
        if isinstance(out, tuple) and len(out) == 2 and not isinstance(out, _VisualOutput):
            return _VisualOutput(out[0], out[1])
        return out
    Qwen3VLVisionModel.forward = _patched_visual_forward
    log.info("Patched Qwen3VLVisionModel.forward to expose pooler_output/deepstack_features attrs")

    # Upstream PatchEmbedQwen __init__ does NOT store fMRI_patch_size as an instance
    # attribute, but forward_embeddings reads `self.fMRI_patch_size`. Patch the class so
    # every instance created downstream by the training pipeline has the attribute.
    # Upstream imports it as `model.patch_embed_qwen_NoPool` (not `project.model.*`);
    # we must patch via the same path so the class object matches in sys.modules.
    from model.patch_embed_qwen_NoPool import PatchEmbedQwen
    _orig_pe_init = PatchEmbedQwen.__init__
    def _patched_pe_init(self, *a, **kw):
        _orig_pe_init(self, *a, **kw)
        for key in ("fMRI_patch_size", "sMRI_patch_size", "dMRI_patch_size"):
            if key in kw:
                object.__setattr__(self, key, tuple(kw[key]))
    PatchEmbedQwen.__init__ = _patched_pe_init
    log.info("Patched PatchEmbedQwen.__init__ to expose patch_size attributes")

    # Upstream training script patches Qwen3VLModel.get_vision_position_ids at
    # module-import time, but that attribute does not exist in transformers >=4.57.
    # Install a placeholder so the upstream backup-and-replace succeeds.
    import transformers.models.qwen3_vl.modeling_qwen3_vl as _mq
    if not hasattr(_mq.Qwen3VLModel, "get_vision_position_ids"):
        def _placeholder_get_vision_position_ids(self, *a, **kw):
            raise RuntimeError("placeholder; upstream replaces this")
        _mq.Qwen3VLModel.get_vision_position_ids = _placeholder_get_vision_position_ids
        log.info("Installed placeholder Qwen3VLModel.get_vision_position_ids for upstream patch")

    from training.main_umbrella_training_qwen_NoPool import (
        UMBRELLATrainingConfigQwen, UMBRELLATrainingPipelineQwen,
    )

    # Upstream hardcodes eval_on_start=True; when --skip_eval drops eval_dataset, HF Trainer
    # still tries to evaluate at step 0 and crashes. Patch to_training_args to honour the
    # eval_dataset_available flag for eval_on_start too.
    if args.skip_eval:
        _orig_to_args = UMBRELLATrainingConfigQwen.to_training_args
        def _patched_to_args(self, eval_dataset_available: bool = False):
            ta = _orig_to_args(self, eval_dataset_available=eval_dataset_available)
            if not eval_dataset_available:
                ta.eval_on_start = False
                ta.eval_strategy = "no"
                ta.eval_steps = None
            return ta
        UMBRELLATrainingConfigQwen.to_training_args = _patched_to_args
        log.info("Patched UMBRELLATrainingConfigQwen.to_training_args to disable eval_on_start when no eval dataset")

    config = UMBRELLATrainingConfigQwen.from_yaml(args.config)
    config.train_json_path = [str(p) for p in train_jsonls]
    if val_jsonls:
        config.eval_json_path = [str(p) for p in val_jsonls]
    config.use_wandb = False

    out_default = EmoBrain / "project/shared/output/brainvlm_ckpt" / f"fold{args.fold}_VA_smoke"
    config.output_dir = args.output_dir or str(out_default)
    Path(config.output_dir).mkdir(parents=True, exist_ok=True)

    if args.epochs is not None:
        config.num_epochs = args.epochs
    if args.batch_size is not None:
        config.batch_size = args.batch_size

    if args.smoke:
        config.num_epochs = 1
        config.logging_steps = 1
        config.save_steps = 25
        config.eval_steps = 25
        # We do the truncation by monkey-patching the dataset constructor after build.
        _truncate_n = {"train": 50, "val": 10}
    else:
        _truncate_n = None

    log.info(f"output_dir = {config.output_dir}")
    log.info(f"epochs = {config.num_epochs}, batch = {config.batch_size}, "
             f"grad_accum = {config.gradient_accumulation_steps}, lr = {config.learning_rate}")

    # If smoke: hook UMBRELLATrainingPipelineQwen.train to truncate datasets
    pipeline = UMBRELLATrainingPipelineQwen(config)
    if _truncate_n is not None:
        original_train = pipeline.train

        def train_with_truncate(self=pipeline):
            from dataset.umbrella_dataset_qwen import UMBRELLADatasetQwen
            from dataset.umbrella_collator_qwen import UMBRELLACollatorQwen
            from training.umbrella_trainer_qwen_NoPool import UMBRELLATrainerQwen

            model, processor = self.setup_model_and_processor()
            train_datasets = [UMBRELLADatasetQwen(
                data_path=p, tokenizer=processor, mode="train",
                sMRI_img_size=self.config.sMRI_img_size,
                dMRI_img_size=self.config.dMRI_img_size,
                fMRI_img_size=self.config.fMRI_img_size,
                max_seq_length=self.config.max_seq_length,
                max_images_per_sample=self.config.max_images_per_sample,
            ) for p in self.config.train_json_path]
            train_ds = torch.utils.data.ConcatDataset(train_datasets) if len(train_datasets) > 1 else train_datasets[0]
            train_ds = maybe_subset_dataset(train_ds, _truncate_n["train"], "train")

            eval_ds = None
            if self.config.eval_json_path:
                eval_paths = self.config.eval_json_path if isinstance(self.config.eval_json_path, list) else [self.config.eval_json_path]
                eval_ds = {}
                for i, p in enumerate(eval_paths):
                    d = UMBRELLADatasetQwen(
                        data_path=p, tokenizer=processor, mode="eval",
                        sMRI_img_size=self.config.sMRI_img_size,
                        dMRI_img_size=self.config.dMRI_img_size,
                        fMRI_img_size=self.config.fMRI_img_size,
                        max_seq_length=self.config.max_seq_length,
                        max_images_per_sample=self.config.max_images_per_sample,
                    )
                    eval_ds[f"task_{i}"] = maybe_subset_dataset(d, _truncate_n["val"], f"val_{i}")

            collator = UMBRELLACollatorQwen(processor=processor, max_length=self.config.max_seq_length)
            training_args = self.config.to_training_args(eval_dataset_available=(eval_ds is not None))
            trainer = UMBRELLATrainerQwen(
                model=model, args=training_args,
                train_dataset=train_ds, eval_dataset=eval_ds,
                data_collator=collator, processor=processor,
            )
            log.info("Starting smoke training...")
            trainer.train()
            final_dir = Path(self.config.output_dir) / "final_model"
            trainer.save_model(str(final_dir))
            processor.save_pretrained(str(final_dir))
            log.info(f"Smoke training complete. ckpt={final_dir}")

        pipeline.train = train_with_truncate

    pipeline.train()


if __name__ == "__main__":
    main()
