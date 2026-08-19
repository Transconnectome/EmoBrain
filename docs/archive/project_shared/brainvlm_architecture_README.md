> ⚠️ **ARCHIVED — 역사 기록. 현행 문서가 아니다.**
> 현행 논증 = `docs/paper_logic_merged.md` (대전제 · RQ · 가설 H1–H4). 운영 규칙 = `CLAUDE.md`.
>
> 아래 내용 중 다음은 **뒤집혔다.** (a) Qwen3-VL 등 LLM backbone 사용 — 금지.
> (b) open-vocabulary / cross-taxonomy 전이를 headline novelty 로 삼는 프레임 — 폐기.
> (c) 학습에 없던 감정 zero-shot — 폐기(원칙적 분할 기준 없음, RQ 와 무관).
> (d) "EmoBrain 과 EmoViS 는 별도 논문 2편" — 현재는 **한 편의 논문**.
> (e) "EmoBrain 은 cortical location 을 주장하지 않는다" — 현재 **H3 이 cortical location 주장**이다.

# FEEL BrainVLM integration

Two parallel integration paths under FEEL Phase 2 for combining Horikawa naturalistic
emotion fMRI with video into a Qwen3-VL-2B-Instruct backbone via the BrainVLM
(UMBRELLA_qwen) `PatchEmbedQwen` fMRI patchifier.

## Architecture choices

### Path B: Hybrid (fMRI via BrainVLM + video via Qwen3-VL native)

```
fMRI volume (1, 1, 96, 96, 96, 20)
   ↓ BrainVLM PatchEmbedQwen.fMRI_proj   ← lab ABCD pretrain weight (when received)
fMRI patch tokens (864, 1152)
   ↓ Qwen3-VL ViT body                    ← Qwen3-VL public weights, frozen
   ↓ BrainVLM CustomNoPoolingTriPlanarMerger (1152 → 2048)
fMRI vision tokens (N_fmri, 2048)
                                           +
video frames                                ↓ Qwen3-VL native patch_embed   ← public, frozen
                                            ↓ Qwen3-VL ViT body              ← shared body
                                            ↓ Qwen3-VL native merger
video vision tokens (N_video, 2048)
                                           ↓
LLM context: [text query tokens] + [fMRI vision tokens] + [video vision tokens]
   ↓ Qwen3-VL LLM
generated emotion-aware caption + V/A
```

Strengths: both vision streams use their respective pretrained weights. Video uses
Qwen3-VL's web-pretrained vision tower (strong CLIP-style alignment). fMRI uses BrainVLM's
ABCD-pretrained patchifier. Only LoRA on LLM + patchifier fine-tune is needed.

Limitation: requires lab to release ABCD-pretrained `PatchEmbedQwen` + `NoPoolingTriPlanarMerger`
weights. Until then, fMRI patchifier is random-init.

### Path C: Decoupled (fMRI via BrainVLM + video as pre-extracted EmoViS feature)

```
fMRI volume → BrainVLM PatchEmbedQwen.fMRI → Qwen3-VL ViT → merger → fMRI vision tokens

video → (pre-extracted V-JEPA2 / CLIP / DINOv2 / VideoMAE / Qwen-VL caption features)
        in data/stimulus_features/<model>.npy
                              ↓
                              VideoFeatureInjector (cross-attention adapter)
                              ↓
LLM hidden states (with video info injected via cross-attention into last N layers)
   ↓ Qwen3-VL LLM
generated emotion-aware caption + V/A
```

Strengths: video extraction cost is zero (EmoViS features already extracted and symlinked
into FEEL). Injector is small (~24M params with V-JEPA2 dim=1408). Trainable parts are
minimal. LLM input length is short (no video patch tokens in context).

Limitation: video representation depends on EmoViS feature quality. Loses spatial
structure of video patches.

## File map

```
code/brainvlm/
├── README.md                                ← this file
├── setup_env.sh                             ← conda env setup (existing)
├── verify_env.{py,sh}                       ← env sanity check (no GPU needed)
├── smoke_test_forward.{py,sh}               ← random-init Horikawa fMRI → BrainVLM forward
├── convert_horikawa_fmri.{py,sh}            ← per-stim frames → 4D (1,1,96,96,96,20) .pt
├── build_horikawa_conversations.{py,sh}     ← (subj, stim) → BrainVLM JSONL with emotion query
├── _lib.py                                  ← shared utilities (fMRI loader, PatchEmbed factory,
│                                              conversation builder, video feature loader)
├── path_B/
│   └── wrapper_video_dispatch.py            ← skeleton: modality-conditional vision tower
└── path_C/
    └── video_feature_injection.py           ← skeleton: VideoFeatureInjector cross-attention
```

## Run order (current state)

### 1. Environment verification (~1-2 min, no GPU)
```bash
bash /pscratch/sd/s/sjmoon/FEEL/code/brainvlm/verify_env.sh
```
Confirms torch / transformers / peft / Qwen3-VL processor / BrainVLM module imports work.

### 2. Smoke test (~30s, no GPU)
```bash
bash /pscratch/sd/s/sjmoon/FEEL/code/brainvlm/smoke_test_forward.sh
```
End-to-end Horikawa fMRI → BrainVLM PatchEmbedQwen.fMRI → vision tokens shape check.
Also loads EmoViS video features (Path C side) and confirms shape alignment.

### 3. Path C injector forward (no GPU)
```bash
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python \
    /pscratch/sd/s/sjmoon/FEEL/code/brainvlm/path_C/video_feature_injection.py
```
Confirms `VideoFeatureInjector` forward shape, gate-residual behaviour.

### 4. Convert Horikawa fMRI into BrainVLM input format (~30-60 min CPU)
```bash
bash /pscratch/sd/s/sjmoon/FEEL/code/brainvlm/convert_horikawa_fmri.sh
```
Produces `project/shared/output/brainvlm_fmri/pad-zero/sub-XX/stimulus_N.pt` for 5 subj × 2185 stim.
Each `.pt` is a `(1, 1, 96, 96, 96, 20)` tensor ready for BrainVLM `PatchEmbedQwen.fMRI`.
Resume-safe (existing files skipped).

### 5. Build emotion VQA conversation JSONL (~30s CPU)
```bash
bash /pscratch/sd/s/sjmoon/FEEL/code/brainvlm/build_horikawa_conversations.sh
```
Produces 5-fold splits of conversation JSONL files under
`project/shared/output/brainvlm_conversations/pad-zero_VA/foldK/{train,val,test}/sub-XX_conversations.jsonl`.

Each line is one conversation record (mirrors `BrainVLM/UMBRELLA_qwen/sample_data`
ABCD-style ChatML format) with:
  - user turn: `<Clinical_Task>` system prompt + fMRI image entry + emotion question
  - assistant turn: ground-truth valence/arousal answer (placeholder caption)

Requires step 4 to have produced the fMRI `.pt` files first.

## Pending (require additional work)

### Both paths
- **Lab ABCD-pretrained ckpt** for `PatchEmbedQwen` + `NoPoolingTriPlanarMerger`. Until
  received, fMRI patchifier runs as random-init and provides no transferred prior.
- **Conversation generator for Horikawa**: `sample_data/generate_*_conversations_*.py`
  를 fork to produce JSONL with `(fmri_path, emotion_query)` pairs.
- **Horikawa fMRI BrainVLM-format converter**: convert per-stimulus `.pt` frames into a
  single 4D `.nii.gz` or `.pt` that the BrainVLM dataset loader can read.
- **Loss / training loop**: emotion VQA targets (V/A regression + free-form caption with
  affect proxy via RoBERTa-emotion).

### Path B specific
- Modality dispatch integration into Qwen3-VL `visual.forward`. Currently `wrapper_video_dispatch.py`
  builds the model but does not yet attach a forward hook to flip between fMRI and video
  patchifiers per input.
- Video frame extraction pipeline for Horikawa (Qwen3-VL native patcher expects sampled
  frames at fixed resolution).

### Path C specific
- Layer-wise cross-attention injection: register forward hooks on chosen LLM decoder
  layers that route `video_feat` from `model.forward(..., video_feat=...)` to each
  `VideoFeatureInjector`.
- Multi-feature ensembling: optionally inject more than one video feature (V-JEPA2 + CLIP)
  in parallel injectors and learn their relative weights.

## Notes on upstream BrainVLM bug

`patch_embed_qwen_NoPool.py` line 75 references `self.fMRI_patch_size` but `__init__`
never stores it as an instance attribute (only `self.fMRI_grid_size`). Our `_lib.py`
factory `make_patch_embed` monkey-patches the attribute after construction. The lab's
training script appears to work around this differently (likely via a custom config
loader); we should reconcile when integrating with their pretrained ckpt.

## Phase 2 roadmap

| Stage | Path B | Path C |
|---|---|---|
| W7  | conversation generator + fmri converter | same |
| W8  | random-init forward pass at LLM end | injector hook integration |
| W9  | (wait for ckpt) | adapter-only training, video=V-JEPA2 |
| W10 | LoRA on LLM + fmri patchifier fine-tune | adapter + LLM LoRA fine-tune |
| W11 | emotion VQA evaluation | emotion VQA evaluation |
| W12 | cross-path comparison: Path B vs Path C on V/A regression, free-form caption affect |  |
