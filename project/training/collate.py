"""Collate. HorikawaDataset items + fixed Question -> model-ready batch.

Turns a list of dataset dicts (fmri, label, meta, optional caption) into a batch
the model forward accepts (fmri, text_ids, text_mask, label). The Question is
tokenized by the backbone (swappable: stub trivial, qwen real), so the collate
stays backbone-agnostic. Caption stays a separate list (teacher, later) and is
never merged into the question.

Usage.
    from project.training.collate import make_collate
    collate = make_collate(TRACK_A_QUESTION, model.backbone)
    loader = DataLoader(ds, batch_size=..., collate_fn=collate)
"""
from __future__ import annotations

import torch


def make_collate(question: str, backbone):
    """Return a collate_fn binding a fixed Question and the backbone tokenizer."""

    def collate(items: list[dict]) -> dict:
        fmri = torch.stack(
            [torch.as_tensor(it["fmri"], dtype=torch.float32) for it in items]
        )
        label = torch.stack(
            [torch.as_tensor(it["label"], dtype=torch.float32) for it in items]
        )
        text_ids, text_mask = backbone.tokenize([question] * len(items))
        batch = {
            "fmri": fmri,
            "text_ids": text_ids,
            "text_mask": text_mask,
            "label": label,
            "subject_id": [it["subject_id"] for it in items],
            "stim_num": [it["stim_num"] for it in items],
        }
        if "caption" in items[0]:  # teacher path (later); kept separate
            batch["caption"] = [it["caption"] for it in items]
        return batch

    return collate
