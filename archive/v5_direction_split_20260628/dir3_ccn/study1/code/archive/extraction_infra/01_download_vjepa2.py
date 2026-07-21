"""
Step 1: Download V-JEPA2 model weights to HuggingFace cache.
Run this once. After success, model is cached locally.
"""

from transformers import VJEPA2Model, VJEPA2VideoProcessor

MODEL_NAME = "facebook/vjepa2-vitg-fpc64-256"

print(f"Downloading processor: {MODEL_NAME}")
processor = VJEPA2VideoProcessor.from_pretrained(MODEL_NAME)
print("Processor downloaded OK")

print(f"Downloading model: {MODEL_NAME}  (~4.1 GB, may take a while...)")
model = VJEPA2Model.from_pretrained(MODEL_NAME)
print("Model downloaded OK")
print(f"Hidden dim: {model.config.hidden_size}")
