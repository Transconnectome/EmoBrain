"""
FEELIN BrainVLM inference. Test fold V/A regression evaluation.

Loads trained checkpoint, generates assistant turn for each test (subj, stim),
parses <Valence>/<Arousal> XML, computes Pearson r vs ground truth V/A.

Usage:
    python inference_brainvlm.py --fold 1 \
        --ckpt /pscratch/sd/s/sjmoon/FEELIN/project/dir1_brainvlm/output/brainvlm_ckpt/fold1_VA_full/final_model \
        --out_csv /pscratch/sd/s/sjmoon/FEELIN/project/dir1_brainvlm/results/brainvlm/fold1_test_preds.csv
"""
import argparse
import json
import logging
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

# ============================================================
# Env compat patches (must run BEFORE any upstream import)
# ============================================================
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

FEELIN = Path("/pscratch/sd/s/sjmoon/FEELIN")
BRAINVLM = Path("/pscratch/sd/s/sjmoon/BrainVLM/UMBRELLA_qwen")
for p in (BRAINVLM, BRAINVLM / "project"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s :: %(message)s")
log = logging.getLogger("feelin.brainvlm.infer")


def install_visual_output_wrap():
    """Wrap Qwen3VLVisionModel.forward to expose pooler_output / deepstack_features attrs."""
    from transformers.models.qwen3_vl.modeling_qwen3_vl import Qwen3VLVisionModel
    class _VisualOutput(tuple):
        def __new__(cls, hidden, ds):
            return super().__new__(cls, (hidden, ds))
        @property
        def pooler_output(self): return self[0]
        @property
        def last_hidden_state(self): return self[0]
        @property
        def deepstack_features(self): return self[1]
    if not hasattr(Qwen3VLVisionModel, "_feelin_wrapped"):
        _orig = Qwen3VLVisionModel.forward
        def _patched(self, *a, **kw):
            out = _orig(self, *a, **kw)
            if isinstance(out, tuple) and len(out) == 2 and not isinstance(out, _VisualOutput):
                return _VisualOutput(out[0], out[1])
            return out
        Qwen3VLVisionModel.forward = _patched
        Qwen3VLVisionModel._feelin_wrapped = True


def install_patchembed_init_patch():
    """Same as training: expose fMRI_patch_size as instance attr."""
    from model.patch_embed_qwen_NoPool import PatchEmbedQwen
    if hasattr(PatchEmbedQwen, "_feelin_init_patched"):
        return
    _orig_init = PatchEmbedQwen.__init__
    def _patched_init(self, *a, **kw):
        _orig_init(self, *a, **kw)
        for key in ("fMRI_patch_size", "sMRI_patch_size", "dMRI_patch_size"):
            if key in kw:
                object.__setattr__(self, key, tuple(kw[key]))
    PatchEmbedQwen.__init__ = _patched_init
    PatchEmbedQwen._feelin_init_patched = True


def install_get_vpid_placeholder():
    """Same as training: Qwen3VLModel.get_vision_position_ids placeholder so upstream patch backs up."""
    import transformers.models.qwen3_vl.modeling_qwen3_vl as mq
    if not hasattr(mq.Qwen3VLModel, "get_vision_position_ids"):
        def _ph(self, *a, **kw):
            raise RuntimeError("placeholder")
        mq.Qwen3VLModel.get_vision_position_ids = _ph


# ============================================================
# Helpers
# ============================================================

GT_VAL_RE = re.compile(r"<Valence>([-\d.]+)</Valence>")
GT_ARO_RE = re.compile(r"<Arousal>([-\d.]+)</Arousal>")


def parse_va(text: str):
    """Extract (valence, arousal) floats from XML-like text. Returns (nan, nan) on failure."""
    if not text:
        return (float("nan"), float("nan"))
    m_v = GT_VAL_RE.search(text)
    m_a = GT_ARO_RE.search(text)
    try:
        v = float(m_v.group(1)) if m_v else float("nan")
    except ValueError:
        v = float("nan")
    try:
        a = float(m_a.group(1)) if m_a else float("nan")
    except ValueError:
        a = float("nan")
    return v, a


def get_gt_from_sample(sample: dict):
    """Pull GT V/A from the assistant turn of a conversation sample."""
    for turn in sample.get("conversations", []):
        if turn.get("role") != "assistant":
            continue
        content = turn.get("content", "")
        if isinstance(content, list):
            text = " ".join(c.get("text", "") for c in content if c.get("type") == "text")
        else:
            text = str(content)
        return parse_va(text)
    return (float("nan"), float("nan"))


def get_user_messages_only(sample: dict):
    """Return a deep-copy of the conversation with assistant turn stripped (prompt only)."""
    msgs = []
    for turn in sample.get("conversations", []):
        if turn.get("role") == "assistant":
            continue
        msgs.append(turn)
    return msgs


# ============================================================
# Main
# ============================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fold", type=int, default=1)
    ap.add_argument("--ckpt", required=True,
                    help="Path to the final_model checkpoint directory")
    ap.add_argument("--conv_root",
                    default=str(FEELIN / "output/brainvlm_conversations/pad-zero_VA"))
    ap.add_argument("--out_csv", required=True)
    ap.add_argument("--limit", type=int, default=None,
                    help="If set, only run first N samples per subject (for quick smoke).")
    ap.add_argument("--max_new_tokens", type=int, default=128)
    ap.add_argument("--temperature", type=float, default=0.0,
                    help="0.0 = greedy. >0 enables sampling.")
    args = ap.parse_args()

    Path(args.out_csv).parent.mkdir(parents=True, exist_ok=True)

    install_get_vpid_placeholder()

    # Now safe to import upstream stuff
    install_patchembed_init_patch()
    install_visual_output_wrap()

    log.info(f"Loading model from {args.ckpt}")
    from transformers import AutoProcessor, Qwen3VLForConditionalGeneration

    processor = AutoProcessor.from_pretrained(args.ckpt, trust_remote_code=True)
    model = Qwen3VLForConditionalGeneration.from_pretrained(
        args.ckpt, dtype=torch.bfloat16, device_map="cuda", trust_remote_code=True,
    )
    model.eval()
    device = next(model.parameters()).device
    log.info(f"Model loaded on {device}")

    # Need to also restore PatchEmbedQwen + Merger replacement that was done during training.
    # Upstream create_qwen_model_with_custom_patch_embed swaps them. After save_model these
    # land inside model.safetensors. So loading from_pretrained should restore them via
    # the same key names. We DO need to set patch_embed.current_modality = 'fMRI' at inference.
    try:
        visual = model.model.visual
        visual.patch_embed.current_modality = "fMRI"
    except Exception as e:
        log.warning(f"Could not set current_modality on patch_embed: {e}")

    # Iterate over test JSONLs
    test_dir = Path(args.conv_root) / f"fold{args.fold}" / "test"
    jsonls = sorted(test_dir.glob("*.jsonl"))
    log.info(f"fold {args.fold} test: {len(jsonls)} subjects")

    rows = []
    for jsonl in jsonls:
        subj_name = jsonl.stem.replace("_conversations", "")
        with open(jsonl) as f:
            samples = [json.loads(line) for line in f]
        if args.limit is not None:
            samples = samples[: args.limit]
        log.info(f"  {subj_name}: {len(samples)} samples")

        for i, sample in enumerate(samples):
            t0 = time.time()
            stim_id = sample.get("task_id", f"sample_{i}")
            gt_v, gt_a = get_gt_from_sample(sample)

            # Build prompt (user turn only)
            user_msgs = get_user_messages_only(sample)
            # Use processor's chat template
            try:
                inputs = processor.apply_chat_template(
                    user_msgs, add_generation_prompt=True, tokenize=True,
                    return_dict=True, return_tensors="pt",
                ).to(device)
            except Exception as e:
                log.warning(f"  [{stim_id}] chat template failed: {e}")
                rows.append({"subject": subj_name, "task_id": stim_id,
                             "gt_v": gt_v, "gt_a": gt_a,
                             "pred_v": float("nan"), "pred_a": float("nan"),
                             "pred_text": "", "error": str(e)[:200]})
                continue

            with torch.no_grad():
                gen_kwargs = dict(max_new_tokens=args.max_new_tokens, do_sample=(args.temperature > 0))
                if args.temperature > 0:
                    gen_kwargs["temperature"] = args.temperature
                out_ids = model.generate(**inputs, **gen_kwargs)
            text = processor.tokenizer.decode(out_ids[0][inputs["input_ids"].shape[1]:],
                                              skip_special_tokens=True)
            pred_v, pred_a = parse_va(text)

            rows.append({"subject": subj_name, "task_id": stim_id,
                         "gt_v": gt_v, "gt_a": gt_a,
                         "pred_v": pred_v, "pred_a": pred_a,
                         "pred_text": text.strip()[:300],
                         "elapsed_s": round(time.time() - t0, 2),
                         "error": ""})
            if (i + 1) % 20 == 0:
                ok = sum(1 for r in rows if not np.isnan(r["pred_v"]))
                log.info(f"  {subj_name}: {i+1}/{len(samples)}  parsed_ok={ok}")

    df = pd.DataFrame(rows)
    df.to_csv(args.out_csv, index=False)
    log.info(f"wrote {args.out_csv}  ({len(df)} rows)")

    # Metrics
    from scipy.stats import pearsonr
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    valid = df.dropna(subset=["gt_v", "gt_a", "pred_v", "pred_a"])
    log.info(f"valid rows for metric: {len(valid)} / {len(df)} ({100*len(valid)/len(df):.1f}%)")
    if len(valid) >= 10:
        v_r, _ = pearsonr(valid["gt_v"], valid["pred_v"])
        a_r, _ = pearsonr(valid["gt_a"], valid["pred_a"])
        log.info(f"  V_reg Pearson r = {v_r:.4f}")
        log.info(f"  A_reg Pearson r = {a_r:.4f}")
        log.info(f"  V_reg MAE       = {mean_absolute_error(valid['gt_v'], valid['pred_v']):.4f}")
        log.info(f"  A_reg MAE       = {mean_absolute_error(valid['gt_a'], valid['pred_a']):.4f}")

        summary_csv = str(Path(args.out_csv).with_name(Path(args.out_csv).stem + "_metrics.csv"))
        pd.DataFrame([{"fold": args.fold, "n_total": len(df), "n_valid": len(valid),
                       "V_reg_pearson_r": v_r, "A_reg_pearson_r": a_r,
                       "V_reg_mae": float(mean_absolute_error(valid["gt_v"], valid["pred_v"])),
                       "A_reg_mae": float(mean_absolute_error(valid["gt_a"], valid["pred_a"]))
                       }]).to_csv(summary_csv, index=False)
        log.info(f"summary -> {summary_csv}")


if __name__ == "__main__":
    main()
