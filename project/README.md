# EmoBrain Project

`project/code/` is the only active modeling pipeline.

## Components

```text
project/code/
  brain_encoder/   E1 ViT, E2 BFM
  adapters/        MLP or Q-Former token projector
  fusion/          Qwen3-VL-4B multimodal assembly and 34D head
  training/        direct, teacher, cache, distilled student
  configs/         canonical Qwen3-VL-4B runs
project/data/      labels, fMRI, caption, BFM sources
project/evaluation metrics and noise-ceiling utilities
project/tests/     focused canonical pipeline tests
project/legacy/    unsupported historical implementations
```

## Encoder Contract

Every encoder returns `(batch, tokens, dimension)`.

- E1 `type: vit`: ROI vector -> 22x22 grid -> pretrained ViT -> token
- E2 `type: bfm`: precomputed Brain-JEPA or SwiFT embedding -> token

There is no target-supervised encoder and no raw+BFM dual branch.

## Training

Direct brain-only training:

```bash
bash /pscratch/sd/s/sjmoon/EmoBrain/project/code/training/trainer.sh /absolute/path/to/config.yaml
```

Corrected Brain-JEPA import:

```bash
bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/import_corrected_brain_jepa.sh
```

Full core distillation:

```bash
bash /pscratch/sd/s/sjmoon/EmoBrain/project/code/training/run_e2_brain_jepa_distillation.sh
```

Every full run selects on val and evaluates the untouched stimulus-held-out test
from the best checkpoint.
