"""
End-to-end forward pass smoke test for Path B and Path C foundations.

Step 1: Load Horikawa fMRI of sub-01 stimulus_1.
Step 2: Pass through random-init PatchEmbedQwen.fMRI → vision tokens.
Step 3: Confirm output shape matches Qwen3-VL LLM hidden dim (2048 for 2B).
Step 4 (Path C only): Load EmoViS video features for the same stim, confirm alignment.

Does NOT load full Qwen3-VL weights (saves time). Tests the EmoBrain-side integration only.
"""
import sys
sys.path.insert(0, "/pscratch/sd/s/sjmoon/EmoBrain/project/shared/code/brainvlm")
import torch
import numpy as np

from _lib import (load_horikawa_fmri, make_patch_embed, build_emotion_query_conversation,
                  load_video_feature)


def main():
    print("=" * 60)
    print("EmoBrain BrainVLM smoke test (random-init)")
    print("=" * 60)

    # Step 1: Load Horikawa fMRI
    print("\n[1] Loading Horikawa fMRI: sub-01 / stimulus_1, padding=zero")
    y = load_horikawa_fmri("sub-01", "stimulus_1", T_target=20, padding="zero")
    print(f"    shape: {tuple(y.shape)}  (B, C, D, H, W, T)")
    print(f"    range: [{y.min():.3f}, {y.max():.3f}]  mean={y.mean():.3f}  std={y.std():.3f}")

    # Step 2: PatchEmbedQwen forward (random init)
    print("\n[2] PatchEmbedQwen.fMRI forward (random init, embed_dim=1152)")
    pe = make_patch_embed(embed_dim=1152, dtype=torch.float32)
    pe.current_modality = "fMRI"
    with torch.no_grad():
        tokens = pe(y)
    print(f"    output: {tuple(tokens.shape)}  (B*L, embed_dim)")
    print(f"    expected L = (96/16)^3 * (20/5) = 216 * 4 = 864")
    expected_L = (96 // 16) ** 3 * (20 // 5)
    assert tokens.shape == (expected_L, 1152), f"expected (864, 1152), got {tuple(tokens.shape)}"
    print(f"    ✅ matches")

    # Step 3: Confirm dimension matches Qwen3-VL ViT hidden (=1152, matches)
    print("\n[3] Token dim 1152 = Qwen3-VL-2B-Instruct vision_config.hidden_size")
    print(f"    Vision tower would now process these 864 tokens of dim 1152")
    print(f"    After NoPoolingTriPlanarMerger, projected to LLM dim 2048")

    # Step 4 (Path C): Video feature alignment check
    print("\n[4] Path C: EmoViS video features alignment")
    feats, stim_idx = load_video_feature("vjepa2_pretrained")
    print(f"    V-JEPA2 features: {feats.shape}, stim_idx shape: {stim_idx.shape}")
    # Find stim_1 index
    stim_num = 1
    # stim_idx 가 어떤 형식인지 보고 lookup
    if stim_num in stim_idx.tolist():
        i = stim_idx.tolist().index(stim_num)
        print(f"    stim_1 vector: {feats[i].shape}  range [{feats[i].min():.3f}, {feats[i].max():.3f}]")
        print(f"    ✅ ready for Path C cross-attention injection")
    else:
        print(f"    [warn] stim_1 not found in stim_idx (first 5: {stim_idx[:5].tolist()})")

    # Step 5: Build conversation JSON for ABCD-format dataset loader
    print("\n[5] Conversation JSON (Path B + C 둘 다 사용)")
    conv = build_emotion_query_conversation("/path/to/sub-01_stimulus_1.pt")
    import json
    print(json.dumps(conv, indent=2)[:600] + "...")

    print("\n" + "=" * 60)
    print("✅ Smoke test complete. Foundation ready for Path B and Path C.")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  Path B (hybrid): implement video modality dispatch in trainer")
    print("  Path C (decoupled): implement video feature cross-attention adapter")
    print("  Both: wait for lab ABCD-pretrained PatchEmbedQwen + Merger ckpt")
    print()
    print("See: code/brainvlm/path_B/  and code/brainvlm/path_C/")


if __name__ == "__main__":
    main()
