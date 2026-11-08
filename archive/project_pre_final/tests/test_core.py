from __future__ import annotations

import unittest

import numpy as np
import torch

from project.code.brain_encoder.registry import available
from project.code.fusion.backbone import last_valid_indices
from project.code.fusion.model import compact_valid_tokens
from project.data.labels import Cowen34Normalizer
from project.evaluation.metrics import error


class CorePipelineTests(unittest.TestCase):
    def test_encoder_registry_has_only_canonical_families(self):
        self.assertEqual(available(), ["bfm", "vit"])

    def test_last_valid_index_handles_internal_caption_padding(self):
        mask = torch.tensor([
            [1, 1, 0, 0, 1, 1],
            [1, 1, 1, 1, 1, 1],
        ])
        self.assertEqual(last_valid_indices(mask).tolist(), [5, 5])

    def test_compaction_moves_padding_to_sequence_end(self):
        embeds = torch.arange(12, dtype=torch.float32).reshape(2, 6, 1)
        mask = torch.tensor([
            [1, 1, 0, 0, 1, 1],
            [1, 0, 1, 0, 0, 0],
        ])
        packed, packed_mask = compact_valid_tokens(embeds, mask)
        self.assertEqual(packed_mask.tolist(), [[1, 1, 1, 1], [1, 1, 0, 0]])
        self.assertEqual(packed[0, :, 0].tolist(), [0.0, 1.0, 4.0, 5.0])
        self.assertEqual(packed[1, :2, 0].tolist(), [6.0, 8.0])

    def test_raw_metrics_use_log1p_inverse(self):
        normalizer = Cowen34Normalizer(
            mode="log1p_z", mu=torch.zeros(34), std=torch.ones(34)
        )
        target_raw = np.stack([
            np.linspace(0.5, 1.5, 34),
            np.linspace(1.0, 2.0, 34),
        ]).astype(np.float32)
        pred_raw = target_raw + 1.0
        target_z = np.log1p(target_raw)
        pred_z = np.log1p(pred_raw)
        metrics = error(pred_z, target_z, normalizer=normalizer)
        self.assertAlmostEqual(metrics["mse_raw"], 1.0, places=6)
        self.assertAlmostEqual(metrics["mae_raw"], 1.0, places=6)


if __name__ == "__main__":
    unittest.main()
