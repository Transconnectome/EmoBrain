"""
Path B (Hybrid) skeleton: video modality dispatch.

Goal:
  - fMRI 는 BrainVLM 의 PatchEmbedQwen.fMRI_proj (lab ABCD pretrained) 거쳐 vision token
  - video 는 Qwen3-VL 의 native vision tower (web pretrained 그대로) 거쳐 vision token
  - 두 stream 의 token 이 LLM context 안에 함께 inject

What this file does (skeleton, not yet running):
  1. Loads Qwen3VLForConditionalGeneration
  2. Backs up the original visual.patch_embed (= Qwen3-VL native image patcher)
  3. Replaces it with BrainVLM PatchEmbedQwen (for fMRI)
  4. Implements a modality-conditional dispatch:
       - if modality == 'fMRI'  → use BrainVLM PatchEmbedQwen
       - if modality == 'video' → use the backed-up Qwen3-VL native patcher
  5. Both streams flow through the same vision tower body, then the merger
     (BrainVLM NoPoolingTriPlanarMerger for fMRI, native Qwen merger for video — TODO)

Open issues / TODOs marked inline. This is NOT yet a runnable training pipeline.
"""
import sys
import torch

sys.path.insert(0, "/pscratch/sd/s/sjmoon/EmoBrain/project/shared/code/brainvlm")
sys.path.insert(0, "/pscratch/sd/s/sjmoon/BrainVLM/UMBRELLA_qwen")

from _lib import make_patch_embed


def build_hybrid_brainvlm(hf_name: str = "Qwen/Qwen3-VL-2B-Instruct",
                          fmri_size=(96, 96, 96, 20),
                          fmri_patch_size=(16, 16, 16, 5)):
    """Build the Path-B hybrid model: BrainVLM fMRI patchifier + Qwen3-VL native video patchifier.

    Returns a Qwen3VLForConditionalGeneration with a modality dispatch attached.
    """
    from transformers import Qwen3VLForConditionalGeneration
    from project.model.patch_embed_qwen_NoPool import CustomNoPoolingTriPlanarMerger

    print(f"[Path B] Loading {hf_name} (this downloads full weights, ~5GB)...")
    model = Qwen3VLForConditionalGeneration.from_pretrained(
        hf_name, torch_dtype=torch.float32, device_map="cpu",
    )
    vit_dim = model.config.vision_config.hidden_size
    llm_dim = model.config.text_config.hidden_size
    print(f"     vit_dim={vit_dim}, llm_dim={llm_dim}")

    # 1) Back up Qwen3-VL native patcher (for video path)
    qwen_native_patch_embed = model.model.visual.patch_embed
    qwen_native_merger = model.model.visual.merger
    print(f"     backed up native patch_embed (type={type(qwen_native_patch_embed).__name__})")
    print(f"     backed up native merger (type={type(qwen_native_merger).__name__})")

    # 2) Build BrainVLM fMRI patchifier + NoPool merger (for fMRI path)
    brainvlm_patch_embed = make_patch_embed(
        embed_dim=vit_dim, fMRI_size=fmri_size, fMRI_patch_size=fmri_patch_size,
        dtype=torch.float32,
    )
    brainvlm_merger = CustomNoPoolingTriPlanarMerger(vit_dim, llm_dim, torch.float32)
    print(f"     built BrainVLM PatchEmbedQwen ({sum(p.numel() for p in brainvlm_patch_embed.parameters())/1e6:.1f}M params)")

    # 3) Modality dispatch container
    # TODO: integrate with HF visual.forward via monkey-patch or subclass.
    #   On each forward call, check which modality the current input is (set externally)
    #   and call the appropriate patch_embed + merger pair.
    model._fmri_patch_embed = brainvlm_patch_embed
    model._fmri_merger = brainvlm_merger
    model._video_patch_embed = qwen_native_patch_embed
    model._video_merger = qwen_native_merger
    # By default leave native in place. Trainer flips by writing to .current_modality (BrainVLM convention)
    # or by manually swapping these slots before forward.

    return model


# TODO: implement dispatcher
# class HybridVisionDispatcher(torch.nn.Module):
#     def __init__(self, model):
#         super().__init__()
#         self.model = model
#     def forward(self, hidden_states, grid_thw, modality):
#         if modality == 'fMRI':
#             model.model.visual.patch_embed = self.model._fmri_patch_embed
#             model.model.visual.merger = self.model._fmri_merger
#         elif modality == 'video':
#             model.model.visual.patch_embed = self.model._video_patch_embed
#             model.model.visual.merger = self.model._video_merger
#         return self.model.model.visual(hidden_states=hidden_states, grid_thw=grid_thw)


if __name__ == "__main__":
    print("\n=== Path B hybrid model skeleton ===\n")
    print("This will download Qwen3-VL-2B-Instruct full weights on first run.")
    print("To proceed, uncomment the line below.\n")
    # model = build_hybrid_brainvlm()
    # print(f"\n[done] Hybrid model assembled. Trainer integration TODO.")
    print("(Skeleton only — see TODOs inline)")
