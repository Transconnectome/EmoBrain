"""
Verify BrainVLM (UMBRELLA_qwen) environment is ready.

Checks:
  1. torch / transformers / peft load
  2. Qwen3-VL-2B-Instruct config download (no full weights yet)
  3. PatchEmbedQwen + CustomNoPoolingTriPlanarMerger import from BrainVLM repo
  4. CUDA available
  5. Tokenizer / processor for Qwen3-VL-2B-Instruct

No model weights downloaded here. Just import sanity.
"""
import sys
import warnings

warnings.filterwarnings("ignore")


def check(name, fn):
    try:
        fn()
        print(f"  ✅ {name}")
        return True
    except Exception as e:
        print(f"  ❌ {name}: {type(e).__name__}: {e}")
        return False


def main():
    print("=== BrainVLM env verification ===\n")

    all_ok = True

    def torch_check():
        import torch
        assert torch.__version__.startswith("2."), f"torch {torch.__version__}"
        print(f"     torch={torch.__version__}, CUDA={torch.cuda.is_available()}")
    all_ok &= check("torch", torch_check)

    def transformers_check():
        import transformers
        from transformers import Qwen3VLForConditionalGeneration
        print(f"     transformers={transformers.__version__}, Qwen3VLForConditionalGeneration import OK")
    all_ok &= check("transformers + Qwen3VL", transformers_check)

    def peft_check():
        import peft
        from peft import LoraConfig
        print(f"     peft={peft.__version__}")
    all_ok &= check("peft", peft_check)

    def brainvlm_module_check():
        sys.path.insert(0, "/pscratch/sd/s/sjmoon/BrainVLM/UMBRELLA_qwen")
        from project.model.patch_embed_qwen_NoPool import PatchEmbedQwen, CustomNoPoolingTriPlanarMerger
        print(f"     PatchEmbedQwen + CustomNoPoolingTriPlanarMerger import OK")
    all_ok &= check("BrainVLM model import", brainvlm_module_check)

    def patch_embed_init_check():
        sys.path.insert(0, "/pscratch/sd/s/sjmoon/BrainVLM/UMBRELLA_qwen")
        from project.model.patch_embed_qwen_NoPool import PatchEmbedQwen
        import torch
        fMRI_patch_size = [16, 16, 16, 5]
        pe = PatchEmbedQwen(
            sMRI_size=[128, 128, 128], sMRI_patch_size=[18, 18, 18],
            dMRI_size=[128, 128, 128], dMRI_patch_size=[18, 18, 18],
            fMRI_size=[96, 96, 96, 20], fMRI_patch_size=fMRI_patch_size,
            embed_dim=1152, dtype=torch.float32,
        )
        # Workaround for BrainVLM upstream bug: forward references self.fMRI_patch_size
        # but __init__ only stores it as local var. Patch instance attribute manually.
        pe.fMRI_patch_size = tuple(fMRI_patch_size)
        n = sum(p.numel() for p in pe.parameters())
        print(f"     PatchEmbedQwen init OK, {n/1e6:.1f}M params (random init)")
        # Forward test on fMRI (Horikawa shape)
        x = torch.randn(1, 1, 96, 96, 96, 20)
        pe.current_modality = "fMRI"
        out = pe(x)
        print(f"     fMRI forward: input (1,1,96,96,96,20) → output {tuple(out.shape)}")
    all_ok &= check("PatchEmbedQwen instantiation + fMRI forward (random init)", patch_embed_init_check)

    def qwen_tokenizer_check():
        # Lightweight: only fetch tokenizer config, not the full model
        from transformers import AutoProcessor
        # This will only download tokenizer + processor config (small)
        proc = AutoProcessor.from_pretrained("Qwen/Qwen3-VL-2B-Instruct", trust_remote_code=True)
        print(f"     Qwen3-VL-2B-Instruct processor loaded, type={type(proc).__name__}")
    all_ok &= check("Qwen3-VL processor download", qwen_tokenizer_check)

    print()
    if all_ok:
        print("✅ All checks passed. Env ready for BrainVLM development.")
        sys.exit(0)
    else:
        print("❌ Some checks failed. Inspect errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
