"""Canonical Qwen3-VL-4B backbone.

Loaded only when the config selects it. hidden_dim comes from the model config so
the projector and head adapt automatically. Student uses a frozen LM with LoRA
(spec §6-6 DECIDED); teacher LoRA vs full is OPEN (config).

Text (caption, question) enters via the tokenizer + embed_tokens here, never the
projector. Pooling reads the last valid token, including batches with internal
padding between multimodal segments.
"""

from __future__ import annotations

import torch

from project.code.fusion.backbone import last_valid_indices, register_backbone


@register_backbone("qwen")
class QwenBackbone(torch.nn.Module):
    def __init__(self, hf_model: str = "Qwen/Qwen3-VL-4B-Instruct",
                 lora: dict | None = None, dtype: str = "bfloat16",
                 frozen: bool = True):
        super().__init__()
        from transformers import AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(hf_model)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        if hf_model != "Qwen/Qwen3-VL-4B-Instruct":
            raise ValueError(
                "EmoBrain canonical backbone is Qwen/Qwen3-VL-4B-Instruct; "
                f"got {hf_model!r}"
            )
        self.lm = self._load_lm(hf_model, dtype)
        self.hidden_dim = int(self.lm.config.text_config.hidden_size)
        if frozen and not lora:
            for p in self.lm.parameters():
                p.requires_grad_(False)
        if lora:
            from peft import LoraConfig, get_peft_model
            cfg = {"r": 16, "lora_alpha": 32, "lora_dropout": 0.05,
                   "target_modules": ["q_proj", "v_proj"]}
            cfg.update(lora)
            self.lm = get_peft_model(self.lm, LoraConfig(task_type="CAUSAL_LM", **cfg))

    @staticmethod
    def _load_lm(hf_model, dtype):
        """Load the text decoder. Qwen3-VL is a VL model; we drive its language
        model with inputs_embeds and read hidden states, so load the full model
        and use its text stack."""
        import torch as _t
        from transformers import Qwen3VLForConditionalGeneration
        return Qwen3VLForConditionalGeneration.from_pretrained(
            hf_model, torch_dtype=getattr(_t, dtype)
        )

    def tokenize(self, texts):
        enc = self.tokenizer(list(texts), padding=True, return_tensors="pt")
        return enc["input_ids"], enc["attention_mask"]

    def embed_text(self, token_ids):
        return self.lm.get_input_embeddings()(token_ids)

    def forward(self, inputs_embeds, attention_mask):
        out = self.lm(inputs_embeds=inputs_embeds, attention_mask=attention_mask,
                      output_hidden_states=True, use_cache=False,
                      logits_to_keep=1)
        h = out.hidden_states[-1]
        last = last_valid_indices(attention_mask)
        return h[torch.arange(h.size(0), device=h.device), last]
