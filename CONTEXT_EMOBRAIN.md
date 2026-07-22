# EmoBrain Current Context

EmoBrain is not an encoder leaderboard and is not defined by beating every raw
decoder. It asks how pretrained representation and multimodal context can support
fine-grained emotion decoding when task-fMRI windows and sample sizes are small.

Current locked choices:

- Qwen3-VL-4B backbone
- E1 ViT and E2 BFM only
- Brain-JEPA/SwiFT as E2 variants
- no dual raw+BFM branch
- 34D independent regression in `log1p_z` space
- teacher uses brain/video/human description; student is brain-only
- future extension: cross-dataset transfer and cortical interpretability

MindCaptioning captions are human-written detailed visual descriptions. The
paper does not establish that they are affect-neutral by construction, so that
phrase must not be used. Their contribution is controlled empirically through
context-only and student-side ablations after core distillation is established.
