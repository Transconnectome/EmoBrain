"""Qwen backbone (real). Lazy-imports transformers; needs GPU for real sizes.

NOT exercised by the CPU wiring smoke (imported only when selected in config).
hidden_dim is read from the loaded model config, so the projector and head
adapt automatically. LoRA is applied to the language model when cfg.lora is
given (default target = the decoder, task_type CAUSAL_LM).

Contract. Backbone. Same as backbones/stub.py.

Caution (implementation_spec / red-team).
    - Text (question, caption) goes through the tokenizer + embed_tokens here,
      never through the projector.
    - Pooling reads the LAST non-pad token (causal LM). If we later switch to a
      dedicated readout token, change only this file.
    - Default is a small Qwen; 4B is a config swap (hf_model).
"""
from __future__ import annotations

import torch

from project.models.base import Backbone
from project.models.registry import register


@register("backbone", "qwen")
class QwenBackbone(Backbone):
    def __init__(self, hf_model: str = "Qwen/Qwen2-1.5B",
                 lora: dict | None = None, dtype: str = "bfloat16"):
        super().__init__()
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(hf_model)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.lm = AutoModelForCausalLM.from_pretrained(
            hf_model, torch_dtype=getattr(torch, dtype)
        )
        self.hidden_dim = self.lm.config.hidden_size
        if lora:
            from peft import LoraConfig, get_peft_model

            self.lm = get_peft_model(
                self.lm, LoraConfig(task_type="CAUSAL_LM", **lora)
            )

    def tokenize(self, texts):  # list[str] -> (ids [B, L], mask [B, L])
        enc = self.tokenizer(list(texts), padding=True, return_tensors="pt")
        return enc["input_ids"], enc["attention_mask"]

    def embed_text(self, token_ids):  # [B, L] -> [B, L, H]
        return self.lm.get_input_embeddings()(token_ids)

    def forward(self, inputs_embeds, attention_mask):
        out = self.lm(
            inputs_embeds=inputs_embeds,
            attention_mask=attention_mask,
            output_hidden_states=True,
        )
        h = out.hidden_states[-1]                       # [B, L, H]
        last = attention_mask.long().sum(dim=1) - 1     # [B] last non-pad idx
        return h[torch.arange(h.size(0), device=h.device), last]  # [B, H]
