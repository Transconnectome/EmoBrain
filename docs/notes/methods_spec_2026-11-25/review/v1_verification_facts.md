##### R1_stimulus_code
# Stimulus-side model code: verified facts

**Path roots** (all absolute; `SP=/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad`)
- JS = `SP/verify_A_lens/JunShern_VideoMAE` (HEAD 35cf177, 2022-10-14)
- JSPIN = `SP/v2_stimcode/junshern_pin`. This is the emodiversity submodule pin 893228f4, fetched with depth 1. Its VCE code (`vce.py`, `vce_dense.py`, `datasets.py`, `run_class_finetuning.py`, `finetune_vce.sh`) is identical to JS. Only the V2V files differ (verified with `diff -rq`).
- ED = `SP/verify_A_lens/hendrycks_emodiversity` (4deaea3)
- VM2 = `SP/verify_A_lens/OpenGVLab_VideoMAEv2` (29eab1e)
- VJ = `SP/repos/vjepa2` (204698b, 2026-03-23)
- PE = `SP/verify_A_lens/facebookresearch_perception_models` (3e352cc)
- PM = `SP/repos/pymoten` (a641c8a)
- TIMM = `SP/v2_stimcode/timm` (new clone, b4f423c, 2026-11-19)
- CNX2 = `SP/v2_stimcode/convnextv2` (new clone, 2553895)

**What I could not reach.** Hugging Face and dl.fbaipublicfiles.com are blocked by the proxy (403). So no weight file's download or byte size could be checked. "Released" below means it is listed in the repo or its code.

---

## 1. JunShern/VideoMAE: the VCE fine-tune

**Command** (VERIFIED, JS/scripts/emodiversity/finetune_vce.sh:18-41)
```
python -u run_class_finetuning.py --model vit_base_patch16_224 --data_set VCE --nb_classes 27 \
  --finetune ${REPO}/models/kinetics400-ViTB-1600-16x5x3-pretrain.pth --batch_size 8 --num_sample 1 \
  --input_size 224 --short_side_size 224 --save_ckpt_freq 10 --num_frames 16 --opt adamw --lr 5e-4 \
  --opt_betas 0.9 0.999 --weight_decay 0.05 --epochs 50 --dist_eval --test_num_segment 2 --test_num_crop 3 \
  --num_workers 10   # --enable_deepspeed commented out
```
- The evaluation script (JS/scripts/emodiversity/evaluate_vce.sh:12-35) uses the same arguments plus `--eval --enable_deepspeed`. Its model is `MODEL_PATH='PATH/TO/TRAINED_MODEL.pt'`.
- The sbatch file sets `GPUS=${GPUS:-1}` (finetune_vce.sbatch:15).

**Values not on the command line, taken from argparse defaults** (VERIFIED, JS/run_class_finetuning.py)

| Setting | Value | Line |
|---|---|---|
| sampling_rate | 4 | 145 |
| tubelet_size | 2 | 37 |
| drop_path | 0.1 | 45 |
| layer_decay | 0.75 | 72 |
| warmup_epochs | 5 | 79 |
| warmup_lr | 1e-6 | 74 |
| min_lr | 1e-6 | 76 |
| opt_eps | 1e-8 | 56 |
| clip_grad | None | 60 |
| update_freq | 1 | 31 |
| weight_decay_end | = weight_decay | 450-451 |
| auto-augment | `rand-m7-n4-mstd0.5-inc1` | 89 |
| reprob (random erasing) | 0.25 | 103 |
| head | mean pooling (`use_mean_pooling=True`) | 130-131 |
| init_scale | 0.001 | 130 |
| imagenet mean/std | yes | 142 |

- **LR scaling** (lines 398-402): `lr = lr × total_batch / 256`. With 1 GPU × 8 this gives 1.5625e-5; with 4 GPUs it gives 6.25e-5. These numbers are my arithmetic from the code.
- **Schedule:** cosine with warmup, stepped per iteration (lines 445-447).

**Mixup, CutMix and label smoothing are effectively OFF.**
- The defaults are mixup 0.8, cutmix 1.0 and smoothing 0.1 (lines 91, 113, 115), and a `Mixup` object is built (lines 290-297).
- But the call `mixup_fn(samples, targets)` is commented out in JS/engine_for_finetuning.py:59-60.
- Smoothing is only used inside `Mixup`, so it never applies.

**Loss:** `torch.nn.BCEWithLogitsLoss()` on 27 soft targets in [0,1] (VERIFIED, run_class_finetuning.py:455).

**Training sampling** (VERIFIED, JS/datasets.py:190-204; JS/vce_dense.py:113-118, 353-377)
- Uses `vce_dense.TrainDataset(VCEDataset(split='train', frames_per_clip=16, step_between_clips=1, frame_rate=args.sampling_rate))`.
- Each `__getitem__` returns one random clip from one video, so one epoch is one pass over the videos.
- `frame_rate=4` goes to torchvision `VideoClips`. That makes a training clip 16 frames at 4 fps, about 4 s. The resampling meaning comes from torchvision API knowledge, not code I read here (INDIRECT).
- Augmentation: RandAug, then random-resized-crop to 224 (scale 0.08–1, ratio 0.75–1.333), horizontal flip, random erasing (JS/vce_dense.py:198-257).

**Test sampling** (VERIFIED, JS/vce.py:142-174 and 263-269)
- decord keeps every 4th native frame. That is 7.5 fps for 30 fps video, so a clip is about 2.1 s.
- 2 temporal clips × 3 spatial crops (short side 224, crops along the long side) = 6 views.
- Logits are averaged over views (`compute_video` / `np.mean`, JS/engine_for_finetuning.py:274-281).
- **The training and test temporal scales differ** (4 fps vs every 4th frame). This is my inference from the two code paths.

**Evaluation metric:** top-1 and top-3 accuracy against the **argmax** of the 27-d label (VERIFIED, engine_for_finetuning.py:164, 197-212, 279-280). There is no correlation or regression metric in the code. Per-view raw 27-d logits are written to `{rank}.txt` (lines 199-205), so 27-d predictions are recoverable.

**The validation split is not held out.** (VERIFIED)
- Validation = the last 10% of `train_labels.json` (datasets.py:212-214; vce.py:51-55).
- The training set loads all of `train_labels.json` (vce_dense.py:95).

**Pretrained checkpoint** (VERIFIED)
- It is the K400 ViT-B, 1600-epoch self-supervised **pre-train** checkpoint, not the K400-fine-tuned one.
- The ED/README.md:149-154 gdown ID `1tEhLyskjb755TJ65ptsrafUG2llSwQE1` equals the "Pre-train checkpoint" link in JS/MODEL_ZOO.md:9.
- How the checkpoint keys are loaded: `encoder.` and `backbone.` prefixes are stripped, and `head.*` is dropped if its shape differs (run_class_finetuning.py:334-349).

**Is a VCE-fine-tuned checkpoint released?**
- No link in ED/README.md, ED/examples/README.md, JS/README.md or JS/MODEL_ZOO.md (VERIFIED: these were read in full).
- A web search found no HF repo for VCE or emodiversity (INDIRECT, search snippet only).
- The Google Drive data folder (ED/README.md:5) could not be inspected (UNVERIFIED).

**How the 27 labels are loaded** (VERIFIED, vce.py:58-63; vce_dense.py:191-196)
- Source: `{split}_labels.json`, field `obj["emotions"]` (a dict of name → score).
- Order: `sorted(...items())`, i.e. alphabetical.
- Format: a list of 27 floats, cast to a FloatTensor.
- Video path: `data_path / obj['file']`.
- `metadata.json` is also loaded and indexed by key (vce_dense.py:89-101).

## 2. hendrycks/emodiversity: label formats (all VERIFIED, ED/README.md)

**VCE** (lines 12-89)
- 61,046 videos: train 50,000, test 11,046.
- Files: `metadata.json`, `train_labels.json`, `test_labels.json`, `videos/NNNNN.mp4`.
- Each label entry is keyed by a 5-digit ID: `{"emotions": {27 names: mean rated intensity 0-1}, "file": "videos/00000.mp4", "topK": [3 highest, descending]}`.
- The 27 names exactly as written: Admiration, Adoration, Aesthetic Appreciation, Amusement, Anger, Anxiety, "Awe (or Wonder)", Awkwardness, Boredom, Calmness, Confusion, Craving, Disgust, Empathic Pain, Entrancement, Excitement, Fear, Horror, Interest, Joy, Nostalgia, Relief, Romance, Sadness, Satisfaction, Sexual Desire, Surprise.

**metadata.json fields** (lines 74-89): `codec_name`, `duration` (string, e.g. "12.000000"), `file`, `frame_rate` (e.g. "30/1"), `height`, `number_of_frames` (string), `width`. The example shows height 320, width 256.

**V2V** (lines 92-136)
- 26,670 videos, a subset of the VCE videos.
- train: 11,038 pairwise comparisons over 16,125 videos.
- test: 3,189 pairwise comparisons over 6,223 videos.
- listwise: 1,758 lists over 4,322 videos, up to 4 videos per list.
- The three splits share no videos.
- Format: `{"comparisons": [[id_a, id_b], ...]}`, where the **second** video is preferred. Listwise lists are ordered least → most preferred.
- Its `metadata.json` is the same as VCE's.

**Licence**
- ED/LICENSE is MIT, "Copyright (c) 2022 Dan Hendrycks". This covers the code repo (VERIFIED).
- No dataset or video licence text appears anywhere in the README (VERIFIED absent). The Drive folder was not inspected.

**Other code in the repo**
- ED/examples/wellbeing_datasets.py has a `UniformVideos` loader. It resamples fps per video so a clip is spread uniformly over the whole video (lines 103-113). It also has a `train_and_test` split for STAM (lines 75-89).
- ED/STAM contains a modified STAM model and needs the Alibaba-MIIL STAM_8/16 K400 weights (STAM/README.md:3).

## 3. VideoMAE V2 (OpenGVLab)

**Fine-tuning code exists** (VERIFIED)
- `VM2/run_class_finetuning.py` plus `VM2/scripts/finetune/` with scripts for vit_b k400/k710/ssv2, vit_l k400/ssv2, vit_h k400/k600/k710/ssv2, and vit_g with several datasets.
- Loss (run_class_finetuning.py:773-777): SoftTargetCE when mixup is on, else LabelSmoothingCE when smoothing > 0, else CE.

**Example: the ViT-B K710 script** (VERIFIED, vit_b_k710_ft.sh:31-56)
- `--finetune .../vit_b_hybrid_pt_800e.pth --batch_size 16 --num_frames 16 --sampling_rate 4 --num_sample 2 --lr 7e-4 --drop_path 0.1 --head_drop_rate 0.0 --layer_decay 0.75 --warmup_epochs 5 --epochs 90 --test_num_segment 5 --test_num_crop 3`
- Default 32 GPUs.

**Checkpoints in VM2/docs/MODEL_ZOO.md** (VERIFIED)
- Pre-train (line 12): only ViT-g `vit_g_hybrid_pt_1200e` (UnlabeledHybrid, 16 frames).
- ViT-g fine-tunes (lines 20-26), all 224²:

| Dataset | Views (frames×clips×crops) | Top-1 |
|---|---|---|
| K710 | 16x5x3 | 83.8 |
| K400 | 16x5x3 | 87.2 |
| K710→K400 | 16x5x3 | 88.4 |
| K710→K600 | 16x5x3 | 88.8 |
| SSv2 | 16x2x3 | 77.0 |
| K710→UCF101 | 16x5x3 | 99.6 |
| K710→HMDB51 | 16x5x3 | 88.1 |

- These weights sit behind a Google request form (line 4). README.md:21 says they were migrated to `huggingface.co/OpenGVLab/VideoMAE2`.
- **Distilled from vit_g_hybrid_pt_1200e_k710_ft, with direct HF links** (lines 35-38), K710 head:
  - ViT-S `distill/vit_s_k710_dl_from_giant.pth`: K710 77.6 / K400 83.7 / K600 83.1
  - ViT-B `distill/vit_b_k710_dl_from_giant.pth`: K710 81.5 / K400 86.6 / K600 85.9
- The ViT-B 800e pretrain referenced by the script is not in MODEL_ZOO (VERIFIED absent). The HF repo has `mae-b/` and `mae-g/` folders; `vit_g_hybrid_pt_1200e.pth` is listed there at 4.11 GB (INDIRECT, search snippet).

**Architectures** (VERIFIED, models/modeling_finetune.py:457-531)

| Model | Width / depth / heads |
|---|---|
| ViT-S/16 | 384 / 12 / 6 |
| ViT-B/16 | 768 / 12 / 12 |
| ViT-L/16 | 1024 / 24 / 16 |
| ViT-H/16 | 1280 / 32 / 16 |
| ViT-g/14 | 1408 / 40 / 16, mlp_ratio 48/11 |

- `forward_features` returns `fc_norm(x.mean(1))` (mean pooling) or the CLS token (lines 429-448).

**Named output classes** (VERIFIED)
- `VM2/misc/label_map_k710.txt` has 710 action names (`wc` = 709 newlines, no trailing newline; first line "riding a bike").
- Also present: `label_710to400.json`, `…to600`, `…to700`, and k400/k600/k700 label maps. So a K710-head model has named outputs.

**Feature extraction example:** `VM2/extract_tad_feature.py:120-156` uses `model.forward_features` on 16-frame windows (docs/TAD.md:9-18).

**Licence:** MIT (VM2/LICENSE).

## 4. V-JEPA 2 / 2.1 (`VJ`, MIT licence)

**Released encoders** (VERIFIED, VJ/README.md:158-240)

| Version | Model | Params | Resolution | File (dl.fbaipublicfiles.com/vjepa2/…) |
|---|---|---|---|---|
| 2 | ViT-L/16 | 300M | 256 | `vitl.pt` |
| 2 | ViT-H/16 | 600M | 256 | `vith.pt` |
| 2 | ViT-g/16 | 1B | 256 | `vitg.pt` |
| 2 | ViT-g/16 | 1B | 384 | `vitg-384.pt` |
| 2.1 | ViT-B/16 | 80M | 384 | `vjepa2_1_vitb_dist_vitG_384.pt` (distilled from G) |
| 2.1 | ViT-L/16 | 300M | 384 | `vjepa2_1_vitl_dist_vitG_384.pt` (distilled from G) |
| 2.1 | ViT-g/16 | 1B | 384 | `vjepa2_1_vitg_384.pt` |
| 2.1 | ViT-G/16 | 2B | 384 | `vjepa2_1_vitG_384.pt` |

- File byte sizes: UNVERIFIED (blocked).
- HF IDs: `facebook/vjepa2-vit{l,h,g}-fpc64-256` and `vitg-fpc64-384` (lines 273-277).
- Embedding widths (src/models/vision_transformer.py): B 768 (l.362), L 1024 (l.275), H 1280 (l.289), g 1408 (l.303), G 1664 (l.464).

**Frames used in pretraining** (VERIFIED)
- configs/train/vitl16/pretrain-256px-16f.yaml:20-25 — 16 frames at 4 fps.
- configs/train/vitl16/cooldown-256px-64f.yaml:19-23 — 64 frames at 4 fps.
- The hub builders default to `num_frames=64` (src/hub/backbones.py:98, 217).

**Torch hub bug.** (VERIFIED) VJ/src/hub/backbones.py:8-11 has the real URL commented out and `VJEPA_BASE_URL = "http://localhost:8300"` live. So `torch.hub.load(..., pretrained=True)` will fail unless this is patched or weights are loaded manually.

**Attentive probe** (VERIFIED, VJ/src/models/attentive_pooler.py:16-137)
- `AttentiveClassifier` wraps `AttentivePooler(num_queries=1)`, then `nn.Linear(embed_dim, num_classes)`.
- With `depth=d`: (d−1) self-attention `Block`s over the encoder tokens, then one `CrossAttentionBlock` with 1 learnable query; mlp_ratio 4, init_std 0.02.
- All configs use `num_probe_blocks: 4` and `num_heads: 16`, i.e. 3 self-attention blocks + 1 cross-attention block with 1 query. Code defaults are 1 and 16 (evals/video_classification_frozen/eval.py:76-77, 152-158).

**Multi-clip handling** (VERIFIED, evals/video_classification_frozen/modelcustom/vit_encoder_multiclip.py, `ClipAggregation`)
- Each temporal segment is encoded separately, and their tokens are **concatenated along time** before the probe.
- Spatial views get separate outputs. Their softmaxes are averaged (eval.py:327).
- Loss is CE (eval.py:299).
- Optimiser: AdamW + WarmupCosine LR + cosine WD (eval.py:482-485).

**Video classification probe configs** (VERIFIED, VJ/configs/eval/vitl/k400.yaml)
- Data: 16 frames, `frame_step: 4` (stride in native frames, src/datasets/video_dataset.py:307-319), 8 segments × 3 views, resolution 256.
- Training: batch 4, 20 epochs, bf16, `use_pos_embed: false`.
- 20 probe heads trained in parallel: lr ∈ {5e-3, 3e-3, 1e-3, 3e-4, 1e-4} × wd ∈ {0.01, 0.1, 0.4, 0.8}, warmup 0, final_lr 0.
- Encoder loaded from `checkpoint_key: target_encoder`.
- Other configs:
  - ssv2: 16 frames × 2 segments × 3 views, 20 epochs.
  - diving48 / jester: 32 frames, frame_step 2, 4 segments × 3 views, 100 epochs, 9 heads. They use the multilevel encoder with `out_layers: [17, 19, 21, 23]` for ViT-L.
  - vitg-384 ssv2: 64 frames, frame_step 2.
- **V-JEPA 2.1 has its own configs** (VERIFIED, VJ/configs/eval_2_1/{vitb,vitl,vitg,vitG}-384/{k400,ssv2,…}.yaml). Same probe design: K400 16f × 8 segments × 3 views at 384, 20 epochs, same 20-head grid. Encoder `checkpoint_key: ema_encoder`, `img_temporal_dim_size: 1`.
- Released probes (README:283-320): SSv2, Diving48 and EK100 for ViT-L and ViT-g-384, e.g. `evals/ssv2-vitg-384-64x2x3.pt` at 77.3%.

**Full fine-tuning script:** none. `grep -ril "finetun|fine-tun"` returns nothing (VERIFIED absent). Only frozen probes exist (evals/), plus pretraining and cooldown (app/).

**Frozen-feature example** (VERIFIED, VJ/notebooks/vjepa2_demo.py)
- `vit_giant_xformers_rope(img_size=(384,384), num_frames=64)`, load `torch.load(pt)["encoder"]` after stripping `module.` and `backbone.`.
- Transform: Resize(int(256/224·img)) → CenterCrop → ImageNet normalisation.
- `model_pt(x)` returns patch tokens [B, N, D]. Frames are sampled as `np.arange(0,128,2)`.
- Hugging Face alternative: `AutoModel.from_pretrained(...).get_vision_features(x)`.
- Classifier: `AttentiveClassifier(embed_dim, num_heads=16, depth=4, num_classes=174)` loading `["classifiers"][0]`.

## 5. Perception Encoder (VERIFIED unless marked)

**PE-Core CLIP models with text towers** (PE/core/vision_encoder/config.py:81-169; PE/apps/pe/README.md:63-71, 180)

| Model | Vision (width / layers / heads), pool | Output dim | Text tower |
|---|---|---|---|
| G14-448 | 1536 / 50 / 16, attn pool, no CLS | 1280 | ctx 72, w1280, 24 layers |
| L14-336 | 1024 / 24 / 16 | 1024 | ctx 32, w1024 |
| B16-224 | 768 / 12 / 12 | 1024 | same text config as L |
| S16-384 | 384 / 12 / 6 | 512 | ctx 32, w512 |
| T16-384 | 192 / 12 / 3 | 512 | same text config as S |

- Zero-shot K400 / MSR-VTT T2V scores: G 76.9 / 51.2, L 73.4 / 50.3, B 65.6 / 47.6 (README:67-71).
- Text encoder available: `CLIP(TextTransformer)` with `encode_text` (pe.py:700-727). Tokenizer: `transforms.get_text_tokenizer(model.context_length)`.

**`encode_video` (pe.py:717-723) is plain frame averaging.** It reshapes [b,n,c,h,w] into frames, runs `encode_image` on each frame (L2-normalised only if `normalize=True`), and takes `.mean(dim=1)`. There is no temporal modelling.
- Benchmark default `--num-frames 8` (apps/pe/clip_benchmark/cli.py:266-267), sampled uniformly (datasets/video_classification_dataset.py:94-98).
- The demo notebook also uses 8 uniformly spaced frames.

**Other details**
- Weights come from `hf://facebook/{name}:{name}.pt` (config.py:16-24).
- Intermediate layers: `VisionTransformer.forward_features(x, layer_idx=…, strip_cls_token=…)` (pe.py:499-525).
- PE-Lang and PE-Spatial are vision-only configs (README:218).
- Checkpoints are Apache-2.0 (README:302; LICENSE.PE).

## 6. pymoten (VERIFIED)

**Defaults**
- `get_default_pyramid(vhsize=(144,256), fps=24)` (PM/moten/__init__.py:21-51).
- `MotionEnergyPyramid` defaults (PM/moten/pyramids.py:93-106): `temporal_frequencies=[0,2,4]`, `spatial_frequencies=[0,2,4,8,16]` (cycles per image), `spatial_directions=[0,45,…,315]` (8 directions), `sf_gauss_ratio=0.6`, `max_spatial_env=0.3`, `filter_spacing=3.5`, `tf_gauss_ratio=10.`, `max_temp_env=0.3`, `include_edges=False`, `spatial_phase_offset=0`.
- `filter_temporal_width='auto'` resolves to `int(fps·2/3)` (lines 132-134): 16 frames at 24 fps, 10 at 15 fps.
- `project_stimulus` returns (nimages × nfilters), float32, combining quadrature pairs with `sqrt_sum_squares` and then `log_compress` (lines 386-391).

**Feature count** (computed by running the repo code with `python3 -I`). It depends on **aspect ratio only**, not on pixel count or fps:

| Frame size (v×h) | Aspect | nfilters |
|---|---|---|
| 144×256 or 72×128 | 16:9 | 2530 (same at 15, 24 and 30 fps) |
| 96×160 | 5:3 | 2208 |
| 96×128 | 4:3 | 1840 |
| 96×96 | 1:1 | 1380 |
| 90×180 | 2:1 | 2990 |

**Recommended usage**
- The README gives no explicit fps or downsampling recommendation; its examples use fps=24.
- `moten.io.video2luminance(file, size=(v,h))` converts to CIE-L luminance and downsamples (demo_example.py:24). `resize_image` defaults to `size=(96,96)` (io.py:237).
- demo_batching.py downsamples to (72,128) at 24 fps with `filter_temporal_width=16`. For batched or chunked processing it pads by `ceil(tw/2)` frames.
- GPU backends: `set_backend("torch_cuda")` with `project_stimulus_batched` (README:76-99).

## 7. Recent, git-clonable ImageNet-21k/22k classifier with named classes (VERIFIED, timm)

**Repo:** `github.com/huggingface/pytorch-image-models`, cloned to `SP/v2_stimcode/timm`.

**Where class names come from:** files shipped inside the package at `TIMM/timm/data/_info/`
- `imagenet_synsets.txt` (1000 lines), `imagenet22k_synsets.txt` (21,841), `imagenet21k_goog_synsets.txt` (21,843), `imagenet12k_synsets.txt` (11,821).
- `imagenet_synset_to_lemma.txt` (21,844 lines, tab-separated, e.g. `n01440764\ttench, Tinca tinca`) and `imagenet_synset_to_definition.txt`.

**API** (`TIMM/timm/data/imagenet_info.py:12-95`)
- `ImageNetInfo('imagenet-22k').label_names()` gives WordNet synset IDs.
- `.label_descriptions(detailed=…)` gives lemmas, optionally with definitions.
- `infer_imagenet_subset(model)` maps output size to subset: 21841 → imagenet-22k, 21843 → imagenet-21k-goog, 11821 → imagenet-12k.
- Reference usage: TIMM/inference.py:265-292.

**Models with full 22k heads**
- `eva02_large_patch14_448.mim_m38m_ft_in22k` and `.mim_in22k_ft_in22k`: `num_classes=21841`, 448 px, hf_hub_id `timm/` (TIMM/timm/models/eva.py:1669-1678; licence 'mit', l.1486).
- `convnext_{tiny,small,base,large,xlarge}.fb_in22k`: `num_classes=21841`, with URL `dl.fbaipublicfiles.com/convnext/convnext_*_22k_224.pth` plus hf_hub_id `timm/`, licence apache-2.0 (TIMM/timm/models/convnext.py:893-912, 731).
- Also present: `beitv2_*.in1k_ft_in22k`, `swinv2_*_window12_192.ms_in22k`, `vit_*_224.augreg_in21k` (21843), `caformer_*.sail_in22k`, `tiny_vit_*.dist_in22k`, `maxvit_*_tf_224.in21k` (grep of `num_classes=2184[123]`).
- Whether the weight files download could not be tested (HF and fbaipublicfiles blocked).

**ConvNeXt-V2 has no released 22k-head checkpoint.**
- CNX2/README.md:45-58 lists "ImageNet-22K fine-tuned models" (N/T/B/L/H, `im22k/convnextv2_*_22k_{224,384,512}_ema.pt`) with ImageNet-1K acc@1. timm tags them `convnextv2_*.fcmae_ft_in22k_in1k` with the default 1000 classes (convnext.py:914-950), licence cc-by-nc-4.0 (l.742).
- So these are 22k→1k models with 1000-class heads (my inference from the table and the tags).

**Video alternative with named outputs:** VideoMAE V2 K710 heads, with names in `VM2/misc/label_map_k710.txt` (see §3).

---

**Sources from search** (INDIRECT only):
- [HF VideoMAE2 tree](https://huggingface.co/OpenGVLab/VideoMAE2/tree/main)
- [HF VideoMAE2 mae-g](https://huggingface.co/OpenGVLab/VideoMAE2/tree/main/mae-g)
- [HF VideoMAE2 mae-b](https://huggingface.co/OpenGVLab/VideoMAE2/tree/main/mae-b)
- [VideoMAEv2 MODEL_ZOO](https://github.com/OpenGVLab/VideoMAEv2/blob/master/docs/MODEL_ZOO.md)
- The VCE-checkpoint search returned only unrelated HF repos, e.g. [cy0307/c-videomae-finetune](https://huggingface.co/cy0307/c-videomae-finetune) and [LinboTTT/videomae-base-finetuned-emonet-subset](https://huggingface.co/LinboTTT/videomae-base-finetuned-emonet-subset).

##### R2_brain_code
# Brain-side facts: code and data (verification pass)

**Tags:** [V] = I read the primary file (path:line given). [I] = indirect evidence. [U] = unverified.

**Repo roots** (all read-only; `SP` = `/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad`)

| Key | Absolute path | Commit |
|---|---|---|
| HKpy | `/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/verify_B_decode/KamitaniLab_EmotionVideoNeuralRepresentationPython` | 451236c |
| FD (new clone) | `/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v2_brain/feature-decoding` | ef0f1cc |
| FE (new clone) | `/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v2_brain/feature-encoding` | |
| FL (new clone) | `/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v2_brain/PyFastL2LiR` | 4b7c794 |
| MC | `/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/verify_A_lens/horikawa-t_MindCaptioning` | 4c39764 |
| GOD | `/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/repos/GenericObjectDecoding` | b0cecdc |
| BIT | `/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/verify_B_decode/WeizmannVision_brainit-fmri` | a7663eb |
| HIM | `/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/repos/himalaya` | v0.4.11, 0d3ed4c |

**Paper texts:**
- H20: `/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/horikawa2020.txt`. This is the main text only. Its Methods line 133 says "All methods can be found in the accompanying Transparent Methods supplemental file", and that supplement is not available locally (PMC7191651, DOI 10.1016/j.isci.2020.101060, via PubMed).
- MCP: `/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/mindcap.txt`
- GODP: `/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/god.txt`

---

## 1. Horikawa 2020 (HK) Python code

**Data format**
- [V] The fMRI comes in bdpy BData h5 files, one per subject: `./data/fmri/paper2020/fmri_Subject{1..5}.h5`, dataset name `EmotionMovie_fmriprep_volume_native`, `label_key: stimulus_name` (HKpy `config/decoding_emotion_score_cv_paper2020.yaml` L15–33).
  - The metadata columns used are `Run`, `stimulus_name`, ROI flags, and `voxel_i/j/k` (Tutorials.ipynb, pycortex cell).
  - There is also a tutorial file `fmri_Subject1_for_tutorial.h5` (`data/files.json`).
- [V] One sample is one video: "fMRI volumes measured over the course of each video presentation were shifted by 4 s and averaged" (H20 L19).
- [V] There are 61 runs. The 6-fold CV splits by run: runs 1–10, 11–20, 21–30, 31–40, 41–50, 51–61 (yaml L64–98).
  - `exclusive_key: stimulus_name` (L105) drops training samples that share a stimulus with the test fold.
  - `average_sample: true` averages test samples that have the same label (FD `cv_predict_feature_fastl2lir.py` L153–157).
  - [I] Together these imply that a few stimulus names occur more than once in the h5.
- [U] Voxel counts per subject and per ROI: the h5 files are not available locally.
- [U] fMRIPrep and preprocessing details are in the Transparent Methods supplement only.

**ROIs**
- [V] `config/roi_set/wholebrain.yaml` has 370 ROIs:
  - 10 subcortical regions (L5–14): thalamus, hyppocampus [sic], hypothalamus, pallidum, brainstem, caudate, putamen, nuc_accum, amygdala, cerebellum.
  - 180 `hcp180_r_lh.L_*_ROI` plus 180 `hcp180_r_rh.R_*_ROI` (HCP-MMP; I counted them with grep).
  - Every ROI has `num: 500`.
- [V] The paper says the same: 360 HCP cortical regions plus 10 subcortical, giving 370 region-wise decoders per emotion (H20 L23).
- [V] The tutorial uses `wholebrain_demo.yaml` instead: 22 grouped Glasser ROIs, hemispheres merged: PVC, EVC, DSVC, VSVC, MTcVA, SMC, PCL_MCC, PMC, POC, EAC, AAC, IFOC, MTC, LTC, TPOJ, SPC, IPC, PCC, ACC_mPFC, OPFC, IFC, DLPFC (L5–26).
- [V] Encoding uses the `WholeBrain = 1` mask; the tutorial uses `Cortex = 1` (encoding yaml L28).

**How "transmodal" is defined**
- [V] It is defined functionally, not by a list of ROIs. Transmodal regions are the voxels with high values on the first principal gradient (PG1) of Margulies et al. (2016). Voxels were placed in 10 equal-count PG1 bins (H20 L83–85, Fig. 5H caption).
- [V] Yeo 17-network results are also reported (H20 L77).
- [V] The HKpy repo contains no gradient or PG files.

**Regression model**
- [V] FastL2LiR, which is ridge with feature selection.
  - Decoder: `alpha: 100`, `select_voxel_num: 500` (decoding yaml L10–11).
  - Encoder: `alpha: 100`, all voxels as outputs, features category, dimension, semantic and vision, each with `num: 0` (encoding yaml L7, L36–39).
- [V] Training (FD `cv_train_decoder_fastl2lir.py` L194–199, L220–225):
  - X and Y are z-scored with the training mean and std (ddof=1).
  - `FastL2LiR(alpha, n_feat=num_voxel[roi])`.
- [V] Voxel selection (FL `src/fastl2lir/fastl2lir.py` L256–295):
  - For each output separately, voxels are ranked by |Pearson r| with that output on the training data, and the top `n_feat` are kept.
  - The model then solves `(XᵀX + αI)` restricted to those voxels plus a bias column. The bias is also penalised.
  - With no selection it uses the closed form (primal or dual) (L240–254).
- [V] The Python version uses a fixed alpha. Nested CV for hyperparameter tuning is "omitted from reproduction code" (HKpy `README.md` L32–34; notebook cell 28).
  - The paper used nested CV and ensemble decoders built from region-wise decoders "selected based on decoding accuracy via a nested cross-validation procedure" (H20 L29).
  - [U] The alpha grid and the number of regions in each ensemble are in the Transparent Methods only.
- [V] Evaluation: `profile_correlation` only, averaged across folds (HKpy `src/cv_evaluate_predicted_features.py` L83–88, L182–183).
  - Video identification is pairwise against all 2,180 other videos (H20 L43).
  - Significance thresholds: decoding r > 0.095 (L25); encoding r > 0.111 (L65).

**Rating files**
- [V] `data/features/amt/mean_score_concat/{category,dimension}/0001.mat, 0002.mat, …`: one file per clip (HKpy `data/README.md` L48–104).
  - The 34 category columns are in alphabetical order, admiration … triumph.
  - The 14 dimension columns: Approach, Arousal, Attention, Certainty, Commitment, Control, Dominance, Effort, Fairness, Identity, Obstruction, Safety, Upswing, Valence.
- [V] Category score = proportion of raters who gave a non-zero score. The analysis uses mean scores across raters (H20 L11).
- [V] The encoding feature sets are 34 categories, 14 dimensions, 73 semantic features and 1000 vision features (notebook cell 28).
  - The vision model is VGG (Simonyan & Zisserman). The semantic features are crowdsourced concept labels (H20 L75).
- [U] The shape inside each .mat file: `features.zip` was not downloaded.
- [V] Video counts in the paper: 2,181 unique videos were analysed (H20 L9, L19, L23); Cowen–Keltner annotated 2,185 videos (L5).

## 2. MindCaptioning (MC)

**Caption features**
- [V] For each layer, take `hidden_states[litr+1]` for `litr` in `range(num_hidden_layers)`, so the embedding-layer output is skipped. Average over all non-special tokens. Optionally z-score with `norm_param` (MC `code/python/util/mcap_utils_demo.py` L1034–1059).
- [V] DeBERTa-large features are stored as `feature/video/deberta-large/layer01..layer24.mat` (nVideos × nUnits). TimeSformer has `layer01..12`. `norm_param` holds the mean and SD per layer (MC `data/README.md` L19–34).
- [V] Each video's feature is the average of the features of its 20 captions. DeBERTa-large was chosen out of 42 language models by cross-validated encoding performance (MCP L204, L208).
  - The shuffled-caption control averages up to 1000 word-order shuffles per caption (L210).
- [V] Captions are in `data/caption/caption_ck20.csv` with header `video_id,description`: 20 captions × 2196 videos = 43,920 (`data/README.md` L37).
- [U] The 1024-dimensional width per layer was not read from a model config.

**Decoder**
- [V] L2 ridge, one decoder per feature unit, per layer and per model.
  - `p.aparam.l2` = logspace(1, 6, 10), i.e. 10 alphas from 10¹ to 10⁶. The code comment says "[10,1,6] are the actual paramters used in our manuscript" (MC `code/matlab/util/mcap_setParams.m` L37–39).
  - **Conflict:** the paper says "10 … log spaced between 10 and 10,000" (MCP L224).
- [V] Voxel selection: `nSelectVoxels = 50000` (mcap_setParams L50). These are the top 50,000 voxels by encoding accuracy:
  - nested-CV encoding accuracy for each fold during the inner CV,
  - full CV accuracy for the final generalisation model (`mcap_gen_decoding.m` L148–163).
- [V] Lambda selection: inner 6-fold CV over runs (`run2FoldAssignIdx = [1,11,21,31,41,51; 10,20,30,40,50,58]`, mcap_setParams L33). The best lambda maximises the mean profile correlation across all units (gen_decoding L186–218). The final model is then refit on all training data (L223).
- [V] X and Y are z-scored with training statistics, then a bias column is added and `flinreg_l2` is applied, which penalises the bias too (`gen_regression_anlaysis.m` L35–57; `flinreg_l2.m` L50).
- [V] ROI variants: WB, WBnoLang, WBnoSem, WBnoVis, Lang (mcap_setParams L53).
  - WBnoVis removes voxels predicted better by TimeSformer than by DeBERTa (gen_decoding L120–138).
  - Language areas come from a localizer (MCP L170–174).
- [V] Encoding:
  - per voxel and per layer, with nested CV (`mcap_cv_encoding.m` L92–118);
  - best layer chosen per voxel (L209–211; MCP L226).

**Evaluation**
- [V] Metrics computed (`evaluate_accuracy.m` L24–27):
  - profile r: per unit, across samples;
  - pattern r: per sample, across units;
  - pairwise identification (`fmcidentification`).
- [V] Repetition handling: predictions are averaged over 1–5 repetitions (gen_decoding L245–254).
- [V] Identification with the full candidate set uses the 72 test videos plus the 2108 training videos (L272–282).
- [V] Text-level metrics:
  - feature correlation, BLEU-4, METEOR, ROUGE-L, CIDEr, BERTScore (RoBERTa-large, layer 17, rescaled), each taking the best match out of the 20 references;
  - text-based identification against 2179 other videos (MCP L262–300).

**Data storage and preprocessing**
- [V] Files:
  - `trainPerception_S*.mat`: `braindat` 2108 × nVoxels;
  - `testPerception_S*.mat` and `testImagery_S*.mat`: [72 × 5 repetitions] × nVoxels;
  - plus `spaceDefine_S*.nii` (`data/README.md` L12–14).
- [V] **Inconsistency:** `data/fmri/README.md` L7 says 2180 training samples. 2108 is the consistent number: the paper discards the last two training runs, which contain the test videos (MCP L188), and `mcap_analysis.py` L136–138 uses `range(0,2108)`.
- [V] Preprocessing (MCP L178, L184–186):
  - TR 1 s, 2 mm voxels, fMRIPrep 20.2.7;
  - discard the first 8 s;
  - per-run nuisance regression: constant, linear trend, 24 motion, 12 global signals;
  - 4 s shift, despike at ±3 SD, block average;
  - **z-score each voxel within each run**.
- [V] Design: 60 training runs plus 10 test runs (MCP L130). 2196 videos minus 16 duplicates gives 2180 unique (L122). The 72 test videos come from the last two training runs and were each shown 5 times (L138).

**72-video test list**
- [V] There is no standalone list file in the repo. Test IDs come from `metainf.Label` under label_type `'Condition'` inside the `.mat` files (`load_data_wrapper.m` L33–35).
- [I] Locally, AffectLab uses `manifests/s2/hk_mc_id_map.tsv` with an `is_mc_test_72` column (`/home/user/AffectLab/tests/test_head_sweep.py` L29; `/home/user/AffectLab/src/crossmodal_emotion/fold_plan.py` L59).

## 3. GenericObjectDecoding (GOD)

- [V] Decoder: sparse linear regression (SLR) with an automatic relevance determination prior, fit by variational Bayes, one model per feature unit (GODP L159–163; `code/matlab/analysis_FeaturePrediction.m` L235–247, `linear_map_sparse_cov`).
  - The MATLAB demo uses `nTrain=200`; the paper used 2000 iterations (L40–44).
- [V] The Python demo is not the paper's model:
  - it fits plain `LinearRegression`, with `SparseLinearRegression(n_iter=200, prune_mode=1)` commented out (`code/python/analysis_FeaturePrediction.py` L264–265);
  - it truncates to 100 units (L120).
- [V] Voxel selection: for each unit, voxels are ranked by |corr| with that unit on the training data, after z-scoring X and Y with training statistics (py L224–256; matlab L196–221).
  - Up to 500 voxels for V1–V4, LOC, FFA and PPA; 1000 for LVC, HVC and VC (GODP L123; `god_config.py` L27–36).
- [V] Feature units: 1000 randomly selected units for each of CNN1–7, and all 1000 units of CNN8. There are 13 feature types: CNN1–8, HMAX1–3, GIST, SIFT+BoF (GODP L131, L21; `god_config.py` L39).
- [V] Identification:
  - The decoded vector is compared by Pearson r with category-average feature vectors drawn from 15,372 ImageNet categories.
  - The candidate set is the test categories plus N random categories. Pairwise accuracy is the rank-based correct rate; top-1 is also reported (GODP L51, L173; `analysis_CategoryIdentification.py` L60–66, L92–116; `matlab/lib/pwidentification.m`).
- [V] Predictions are averaged within each category/label before identification (py L290–298).

## 4. Brain-IT (brainit-fmri)

- [V] The repo implements two papers: the Universal Brain Encoder (arXiv 2406.12179) and Brain-IT (ICLR 2026, arXiv 2510.25976) (BIT `README.md` L1–11). Both are trained on NSD, 8 subjects, **images only** (README L73).

**Encoder**
- [V] Frozen DINOv2 ViT-L/14-reg (`model_size=2`), layers [1, 6, 12, 18, 24], plus LoRA (rank 3), a learnable embedding per voxel and voxel-wise attention maps (`train/train_encoder.py` L8, L166–169; `models/encoder_models.py` L11–71).

**Clustering**
- [V] A Gaussian mixture with 128 components is fit on the encoder's voxel embeddings, giving the mapping `v2c_128_mapping_gmm_v2.npy` (`data/scripts/decoder_prep/get_clusters.py` L17, L30–34).

**Decoder (Brain Interaction Transformer)**
- [V] Forward pass (`models/decoder_models.py` L35–113):
  1. Voxel value × learnable voxel embedding.
  2. Graph convolution from voxels to their cluster nodes (torch_geometric `TransformerConv`) over learnable cluster centres.
  3. ReLU and LayerNorm.
  4. Self-attention blocks over the cluster tokens.
  5. Cross-attention updates of learnable output tokens.
  6. Linear projection.
- [V] Training defaults (`train/train_decoder.py`):
  - 128 centres (L44); 15k voxels sampled per step (L45, L243); dim 512 (L46); 5 blocks (L48); 8 heads; batch 128 (L49); lr 5e-4 with AdamW and warmup (L51–55); 75 epochs (L167).
  - `dec_param` class defaults differ (256 centres, 2 blocks, L14–17) but are overridden by these arguments.
- [V] Outputs:
  - `--CLIPG`: 256 tokens × 1664, the CLIP image patch tokens in `nsd_images_clip.npy` (L162–164, L195).
  - `--VGG`: 2029 multi-scale tokens × 512 (L159–160).
  - Stage 2 is diffusion with SDXL / unCLIP from MindEye2 (`src/MindEyeV2`).
- [V] Input: fsaverage surface vertices. Betas are z-scored per vertex within each session; the code comment says "across voxels", but it normalises along `axis=0`, i.e. across trials. Up to 3 repeats are averaged (`data/scripts/data_processing/prepare_fmri.py` L28–29, L47–49, L82–124).
- [V] Image-only: yes. There is no temporal or video module.
- [V] Transfer: base model trained on 7 subjects, then fine-tuned on single-session data from the held-out subject. New voxels are mapped to existing clusters by nearest neighbour in embedding space (`train_transfer/README.md` L5–12, L80).
- [V] Compute: Stage 2 needs 2×H200 or 4×H100 (README L134–135).
- [V] Local HK run: one Brain-IT fold took about 31 min (`/home/user/AffectLab/01_AffectModels/1-1_Vision2Affect/README.md` L109).

## 5. himalaya API (v0.4.11)

**Banded ridge**
- [V] `from himalaya.ridge import BandedRidgeCV`, which is an alias of `GroupRidgeCV` (HIM `himalaya/ridge/__init__.py` L13).
- [V] Signature: `GroupRidgeCV(groups=None|"input"|array, solver="random_search", solver_params=None, fit_intercept=False, cv=5, random_state=None, Y_in_cpu=False, force_cpu=False)` (`ridge/_sklearn_api.py` L346, L438–441).
  - Attributes: `deltas_` (n_groups × n_targets, log band scalings), `cv_scores_`, `best_alphas_ = 1/exp(deltas_).sum(0)`.
- [V] Per-band outputs:
  - `predict(X, split=True)` returns shape (n_groups, n_samples, n_targets) (L531–575).
  - `score(X, y, split=True)` uses `r2_score_split` (L600–630).
  - Use `groups="input"` with `ColumnTransformerNoStack` or `make_column_transformer_no_stack` (`ridge/_column.py` L5).
- [V] Solver parameters (`solve_group_ridge_random_search`, `ridge/_random_search.py` L16–23):
  - `n_iter=100`, either Dirichlet samples or an explicit (n_iter, n_bands) weight array;
  - `concentration=[0.1, 1.0]`, `alphas`, `score_func=l2_neg_loss`, `cv`, `local_alpha=True`, `n_targets_batch`, `n_alphas_batch`, `diagonalize_method="svd"`.

**Kernel version**
- [V] `himalaya.kernel_ridge.MultipleKernelRidgeCV(kernels=["linear","polynomial"], kernels_params, solver="random_search"|"hyper_gradient", solver_params, fit_intercept=False, cv=5, random_state, Y_in_cpu, force_cpu)` (`kernel_ridge/_sklearn_api.py` L753, L867).
  - It also supports `predict` / `score` with `split=True` (L569, L627).
- [V] Related classes: `ColumnKernelizer` (`kernel_ridge/_kernelizer.py` L166), `Kernelizer` (L17), `WeightedKernelRidge` (L984), `KernelRidgeCV` (L366).

**Scoring**
- [V] `himalaya.scoring` (`scoring.py`):
  - `r2_score_split(y_true, y_pred, include_correlation=True)`, product measure; assumes zero-mean y (L99);
  - `r2_score_split_svd`, relative weights (L178);
  - `correlation_score_split` (L270);
  - `correlation_score` (L70).

**GPU**
- [V] `from himalaya.backend import set_backend; set_backend("torch_cuda", on_error="raise")`.
- [V] Available backends: numpy, cupy, torch, torch_cuda, torch_mps (`backend/_utils.py` L6–12, L25).

## 6. HK data available locally, per the docs

None of the arrays exist in this sandbox. A `find` for `fmri_Subject*.h5`, `*common36_qc_runz*` and `split_hk_dev.tsv` returned nothing, so the data live on the NERSC server.

**EmoBrain**
- [V] `/home/user/EmoBrain/project/README.md` L51 lists `brain.roi_mean` as Schaefer-400 + Tian-S3 50 = 450 ROI-mean BOLD, "5명 평균" (averaged over 5 subjects), shape (2185, 450). L52–53 list `brain.brain_jepa` and `brain.swift` at 768 dims.
- [V] **The loader contradicts "5명 평균".** `/home/user/EmoBrain/project/data/fmri_adapter.py` L1–11 and L41–44 load one file per subject, `project/shared/data/roi_timeseries/sub-XX.pt`, containing:
  - `roi_timeseries` (2185, 47, 450), `roi_mean` (2185, 450), `mask`, `original_T`, `stim_num`.
- [V] `/home/user/EmoBrain/project/data/datasets.py` L9–11 and L60–63 pool (subject, stimulus) pairs: 8740 / 1085 / 1100 samples, from `horikawa_split.csv`, `cowen_horikawa_labels.csv` and `norm_stats/cowen34_train.pt`.
- [V] `/home/user/EmoBrain/CONTEXT_EMOBRAIN.md` L16–18: 2196 presented = 2185 unique + 11 repeats; stimulus split 1748 / 217 / 220.
  - [V] Baselines quoted there: ridge 0.294, kernel ridge 0.313 (L23–25).

**AffectLab**
- [V] `/home/user/AffectLab/docs/data_compatibility.md`:
  - L17: the stimulus table and crosswalk have 2,196 rows; the labels have 2,185 `stim_num_int`; there are 2,180 canonical IDs.
  - L19: usable sample rows per subject are 2,191 / 2,195 / 2,187 / 2,175 / 2,085. The doc says these are not training-sample counts, and the QC column order is unverified.
- [V] `/home/user/AffectLab/src/crossmodal_emotion/fold_plan.py` L55–61 gives the exact split and data file paths:
  - `splits/hk_dev_v4/split_hk_dev.tsv`, `splits/hk_dev_v4/fold_roles.tsv`
  - `manifests/s2/participant_blocks_hk.tsv`, `data/stimulus_crosswalk.tsv`, `manifests/s2/hk_mc_id_map.tsv`
  - `{hk_roi_voxels}/hk_{subject}.npz`
  - `{horikawa_root}/{subject}/v3_qc/{subject}_blocks_common36_qc_runz.npy`
- [V] Fold rules (fold_plan.py L10–20, L45–47): 6 folds, 4 train / 1 val / 1 test; no run may span two roles.
- [V] `/home/user/AffectLab/01_AffectModels/1-1_Vision2Affect/EXPLORATORY_SWEEP_2026-11-14.md` L38–40:
  - `hk_dev_v4` comes from `EmoBrain_run_1110`, and its 5 files are byte-identical to EmoBrain's;
  - splits are per participant, not participant hold-out;
  - content matching the MC 72 test videos is excluded;
  - fold 1 has already been seen.
- [V] Voxel-level input for Brain-IT and MindEye2 (`/home/user/AffectLab/docs/BRAINIT_PILOT.md` L30–36):
  - sub-01 has 149,080 voxels, run-z-scored;
  - fold 1 has 1,388 train / 380 val / 337 test videos;
  - Brain-IT transfer used the first 750 shuffled training rows;
  - the target is CLIP 256×1664, token-averaged.
- [V] The brain input is a block-average vector per video over the union of QC'd ROI voxels, and the visual target is a single middle frame (Vision2Affect `README.md` L23–25).

## 7. Is a noise ceiling impossible for HK?

- [V] **Yes for a repeat-based voxelwise ceiling.** The paper states: "because each stimulus was presented only once, we were unable to estimate the proportion of systematic variance in voxel responses that was left unexplained by our models … we performed our analyses on data from single trials" (H20 L117).
- [V] Partial caveat. The paper analyses 2,181 unique videos (L19), while 2196 videos were presented (MC data and AffectLab). The HK CV code drops shared `stimulus_name`s and averages same-label test samples (see item 1).
  - [I] So a small number of duplicate items (about 11–15) were probably presented twice.
  - [U] Whether these were intended as repeats. This is too few for a voxelwise ceiling.
- [V] MindCaptioning has a real repeat design: 72 test videos × 5 repetitions in 6 *different* subjects watching the same stimulus pool (MCP L138). A noise ceiling is possible there for those 72 videos only.
  - [V] AffectLab reserves MC as the final external test (Vision2Affect README L121), so using it for a ceiling would conflict with that.
- [U] Ceiling proxies that do not need repeats (my inference, not from any source):
  - inter-subject consistency across the 5 HK subjects;
  - split-half reliability of the rating-side 34-D profiles, if rater-level data exist. `datasets.py` mentions "rater rotation" at L147, which is [I] evidence that they do.

## Discrepancies to resolve

1. Unique video count differs by source: HK paper 2,181; Cowen–Keltner 2,185; MC 2,180 (2196 − 16 duplicates); EmoBrain CONTEXT says "2185 + 11 repeats".
2. MC alpha grid: code 10¹–10⁶ versus paper 10–10⁴.
3. MC training sample count: 2108 versus 2180 in the two READMEs.
4. EmoBrain `roi_mean`: README says it is averaged over 5 subjects; the loader keeps it per subject and pools.
5. The HK Python code uses a fixed alpha of 100 and 500 voxels per ROI, not the paper's nested-CV tuning or its ensemble decoders.
6. The GOD Python demo uses `LinearRegression` and 100 units, not SLR.


##### R3_lit_methods
# Methods-literature verification (v2)

Status labels: **VERIFIED** means I read the primary text or code at the location given. **INDIRECT** means it rests on a search snippet or secondary source only. **UNVERIFIED** means I could not find it in any source I could reach.
Citation metadata comes from PubMed.
Paths in the table below are shorthand. Each one expands to an absolute path as follows:
- `SP/` = `/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/`
- `V2/` = `SP/v2_methods/`

**Sources I could not reach** (all blocked by the network): science.org/advances supplements (Kragel fig. S2 and the trailer supplement), PMC/EuropePMC web pages, sciencedirect, the TU Berlin Haufe PDF, par.nsf.gov, and the iScience "Transparent Methods" supplement. Anything that exists only in a supplement is therefore marked UNVERIFIED.

---

## 1. Kragel, Reddan, LaBar & Wager 2019, *Sci Adv* 5(7):eaaw4358, "Emotion schemas are embedded in the human visual system" ([DOI](https://doi.org/10.1126/sciadv.aaw4358); PMID 31355334; PMC6656543)

**Low-level and object features (post hoc feature tests)**
- What they computed (VERIFIED, `SP/kragel.txt` L103):
  - R, G and B color histograms
  - "the 2D power spectral density"
  - number of faces, via the Viola–Jones algorithm
  - object identities, by running AlexNet (1000-class) on each image
- How associations were tested (VERIFIED, L25 and L103):
  - Bivariate correlations between each feature set and EmoNet's 20-dimensional fc8 output, in the **training** set. They report r up to 0.8 (this is fig. S2).
  - Each feature set (between 1 and about 150,000 predictors) was then used to classify images into 20 categories with **PLS discriminant analysis**.
  - On the holdout set, the bivariate associations "largely failed". The exception was object classes, with top-1 accuracy of 11.4%.
- UNVERIFIED (supplement only): histogram bin counts, how the PSD was binned or summarized, the fig. S2 caption, and the PLS-DA component count.
- Related layer-wise test (VERIFIED, L99): one PLS regression per EmoNet layer, predicting the 20 categories. Trained on training images and evaluated on holdout images (Fig. 1D).

**Movie-trailer genre demonstration** (VERIFIED, L41–47 and L107; Fig. 3 caption at L43)
- Stimuli: 28 trailers (9 romantic comedy, 9 action, 10 horror). Chosen using imdb.com/feature/genre and availability on hd-trailers.net. The exact sampling criteria are in the supplement (UNVERIFIED).
- Frames: the text says "EmoNet made emotion predictions for each movie frame". The Fig. 3A caption says the time courses show "every fifth frame", with the per-trailer summary "averaging predictions across all analyzed frames". **Which frames fed the classifier is ambiguous.**
- Per-trailer feature: the average activation over time of the 20 fc8 units.
- Classifier: PLS regression, one-vs-all classification (their ref 37), 10-fold CV. Weights were bootstrapped 1000 times (Fig. 3B violins).
- Reported results:
  - 3-way accuracy 71.43%, permutation P < 0.0001, chance stated as 35.7%. My own arithmetic: 35.7% equals 10/28, the majority class.
  - Mean AUC 0.855 (d = 1.497), with ROC curves.
  - Confusion matrix: errors were mostly action vs horror (26.32%); romantic comedies were never misclassified.
  - t-SNE of the trailer-mean vectors.
  - β with 95% CIs per genre, e.g. romcom: romance 1.499, amusement 1.167, sadness 0.743.
- UNVERIFIED: number of PLS components, and how the one-vs-all scores became a single 3-way decision (argmax is presumed, not stated).

**IAPS valence/arousal demonstration** (VERIFIED, L33–37 and L105)
- Model: PLS regression of normative valence and of normative arousal on the 20 EmoNet fc8 units.
- Validation: 10 repetitions of 10-fold CV, with folds stratified on normative ratings. Weights (β_PLS) were bootstrapped.
- Fig. 2B is a "circumplex" figure built from those weights: each category is plotted at (β_valence, β_arousal).
- Results:
  - Valence: r = 0.88, RMSE 0.9849. Arousal: r = 0.85, RMSE 0.5843. Both by permutation test.
  - Applied without retraining to a second database (their ref 36): valence r = 0.83, arousal r = 0.84.
- Fig. 2C plots the mean of 25 rating quantiles and uses a corrected resampled t test. The title of Fig. 2 marks significance with *P<.05 and **P_FWE<.05.
- PLS component count: UNVERIFIED.

**Weight interpretation:** the paper reads raw PLS β directly. There is no Haufe or activation-pattern transform (grep for "Haufe" finds 0 hits; VERIFIED for the main text only).

**Conflicts with our rules (CLAUDE.md bans top-1 and grouping):** Fig. 2A colors the t-SNE by the max category, and the confusion matrices are argmax-based.

## 2. Gao, Ajith & Peelen 2025, *Commun Biol* 8:697, "Object representations drive emotion schemas across a large and diverse set of daily-life scenes" ([DOI](https://doi.org/10.1038/s42003-025-08145-1); PMID 40325234)

**Targets** (VERIFIED, `SP/gao.txt` L151): for each of 4913 BOLD5000 images, the proportion of 10 raters who selected each of 20 categories (multi-select allowed).

**Fig. 3 procedure** (VERIFIED, L33–35, L169, L179)
- Predictor: AlexNet fc8 (1000 ImageNet class units). PLSR via MATLAB `plsregress`.
- Folds: leave-one-session-out, which gives 15 folds.
- The figure uses the "transformation matrix (1000 object labels x 20 emotions) between AlexNet's fc8 layer and emotion ratings", **averaged across 15 cross-validation folds**.
- It shows **the top 10 positive and top 10 negative weights out of 1000 object labels**, for 6 example emotions.
- The text names 5 of the 6 emotions: esthetic appreciation (mountains, flowers, houses), craving (pizza, dishes), horror (cockroaches, tiger beetles), sadness (bulletproof vests, military uniforms), sexual desire (faces, sunglasses, lipstick).
- UNVERIFIED:
  - the 6th emotion;
  - whether the "transformation matrix" is the `plsregress` BETA (the paper does not say);
  - whether the figure shows label words or example images (the text says "top example images");
  - whether fc8 was taken before or after softmax;
  - the component count for this particular fc8 model. The paper states "PLSR models with 20 dimensions to prevent overfitting" only in the layer-wise section (L179).

**Weight-interpretation issues:** not addressed. There is no Haufe, activation-pattern or suppressor discussion (grep returns 0). The limitations paragraph (L95) covers only the task mismatch and causality.

**Layer-wise analysis** (VERIFIED, L45–49, L167, L179)
- Layers conv1–conv5, fc6, fc7, fc8.
- Conv layers were spatially averaged, giving 96, 256, 384, 384 and 256 dimensions. fc6/fc7 have 4096; fc8 has 1000.
- PLSR with 20 dimensions, leave-one-session-out; score is Pearson r between observed and cross-validated predictions.
- Permutation test: 1000 shuffles of the ratings, with FDR correction.
- Repeated-measures ANOVA across folds with Greenhouse–Geisser correction: F(2.93, 41.04) = 999.42. Successive-layer contrasts used permutation tests with FDR.
- Related analyses:
  - AlexNet fc8 vs EmoNet fc8: Δr = 0.115 (permutation test).
  - On 6555 Cowen17 frames (taken at 25/50/75% of each video), 15-fold: EmoNet > AlexNet, t(14) = 24.55.
  - BOLD5000 subsets: 5-fold.

**ROI decoding** (VERIFIED, L71–77, L140, L189–197)
- Data: BOLD5000 Release 2.0 GLMsingle betas (TYPED-FITHRF-GLMDENOISE-RR).
- ROIs (from localizers):
  - EarlyVis: scrambled > baseline
  - LOC: objects > scrambled
  - PPA, RSC and OPA: scenes > objects and scrambled
  - Heschl's gyrus (AAL3) as the control
- Voxels and the 20 targets were z-scored across trials, per participant.
- PLSR per participant and per ROI, leave-one-session-out: 15 folds for CSI1–3, 9 for CSI4.
- Score: Pearson r. 1000-permutation test, FDR, repeated-measures ANOVA across folds.
- LOC confusion matrix: correlate the predicted 20-dimensional vectors with the actual rating vectors (a 20×20 matrix per fold), take the argmax, aggregate, normalize, and build a Ward dendrogram.
- The ROI component count is UNVERIFIED.
- The confusion matrix is argmax/top-1, which conflicts with our rules.

## 3. Haufe et al. 2014, *NeuroImage* 87:96–110, "On the interpretation of weight vectors of linear models in multivariate neuroimaging" (authors: Haufe, Meinecke, Görgen, Dähne, Haynes, Blankertz, Bießmann; [DOI](https://doi.org/10.1016/j.neuroimage.2013.10.067); PMID 24239590; not in PMC)

- **Citation: VERIFIED** (PubMed).
- **Claim: VERIFIED** (abstract):
  - Backward-model (decoder) weights can be nonzero at channels that are statistically independent of the process of interest.
  - The paper proposes transforming linear backward models into forward models (activation patterns).
- **Formula**
  - INDIRECT for the paper's own notation (search snippets only; I could not open the PDF): A = Σ_x W Σ_ŝ⁻¹, where **Σ_ŝ is the covariance of the estimated sources/outputs ŝ = Wᵀx**, not of the true targets.
  - VERIFIED in MNE's implementation (`V2/dl/mne_base.py` L556–562): `patterns_ = cov(X) · W · pinv(cov(y))`, commented "Haufe's trick: A = Cov_X . W . Precision_Y". MNE uses the covariance of the **true targets y**.
  - So "A = Cov(X) W Cov(Y)⁻¹" matches MNE. The paper (per secondary sources) uses Cov(ŷ). For a single output this only rescales A; for 34 correlated outputs the two differ.
  - Spec should state which one it uses.

## 4. Supporting methods citations (all citations VERIFIED via PubMed metadata)

| Ref | Citation | Relevant claim | Status |
|---|---|---|---|
| Lescroart, Stansbury & Gallant 2015 | *Front Comput Neurosci* 9:135, "Fourier power, subjective distance, and object categories all provide plausible models of BOLD responses in scene-selective visual areas" ([DOI](https://doi.org/10.3389/fncom.2015.00135)) | Fit A, B and the concatenated A∪B. Unique(A) = r²(A∪B) − r²(B), from the 3-way example "full minus 2-part" (`V2/txt/lescroart.txt` L85–87). r² = signed squared prediction r. OLS (L55). Result: Fourier, distance and category models explain largely **shared** variance in PPA/RSC/OPA. Low-level recipe (L39): CIELAB luminance → 2D FFT amplitude → 8 bins (4 orientations × high/low split at 5 cyc/deg), each divided by the L2 norm, plus the norm itself = 9 channels, z-scored. | VERIFIED. The shared-variance equation sits in Fig. 3C's image, so the standard set formula Z = r²A + r²B − r²A∪B is INDIRECT. |
| Dupré la Tour, Eickenberg, Nunez-Elizalde & Gallant 2022 | *NeuroImage* 264:119728, "Feature-space selection with banded ridge regression" ([DOI](https://doi.org/10.1016/j.neuroimage.2022.119728)) | Banded ridge (one λ per feature space) plus decomposition of the joint R² over feature spaces. Product measure from Himalaya `r2_score_split` (`V2/dl/himalaya_scoring.py` L99–175): R²_i = Σ_samples(2·y·ŷ_i − ŷ_i·Σ_j ŷ_j)/Σy², which sums exactly to the joint R². Requires zero-mean y. My derivation: a component can be negative. | VERIFIED (abstract + code) |
| Westfall & Yarkoni 2016 | *PLoS ONE* 11(3):e0152719, "Statistically controlling for confounding constructs is harder than you think" ([DOI](https://doi.org/10.1371/journal.pone.0152719)) | "Incremental validity" claims via multiple regression with imperfectly reliable covariates have very high Type I error. The error is highest with large N and moderate reliability. They recommend SEM. | VERIFIED (abstract) |
| Lakens 2017 | *Soc Psychol Personal Sci* 8(4):355–362, "Equivalence tests: a practical primer for t tests, correlations, and meta-analyses" ([DOI](https://doi.org/10.1177/1948550617697177)) | TOST: set the bounds at the smallest effect size of interest, ideally prespecified. This can statistically reject effects large enough to matter, so a non-significant result alone is not evidence of absence. | VERIFIED (abstract) |
| Schütt, Kipnis, Diedrichsen & Kriegeskorte 2023 | *eLife* 12:e82566, "Statistical inference on representational geometries" ([DOI](https://doi.org/10.7554/eLife.82566)) | 2-factor cross-validation and bootstrap, generalizing simultaneously to new subjects and new conditions (rsatoolbox). Code `eval_dual_bootstrap` (`V2/dl/rsa_evaluate.py` L28–205): bootstraps over subjects (rdm), conditions (pattern) and both. Corrected variance in `_dual_bootstrap` (`V2/dl/rsa_util_inference.py` L665–695): σ² = 2(σ²_subj + σ²_cond) − σ²_both, or a small-sample form with n/(n−1) factors. The result is clipped to [max(σ²_subj, σ²_cond), σ²_both]. A CV-variance correction applies with n_cv = 2. | VERIFIED (abstract + code) |
| Mehrer, Spoerer, Kriegeskorte & Kietzmann 2020 | *Nat Commun* 11:5725, "Individual differences among deep neural network models" ([DOI](https://doi.org/10.1038/s41467-020-19632-w)) | Changing only the random initialization gives substantial differences in intermediate and high-level representations at similar accuracy. Inferences should rest on groups of network instances. | VERIFIED (abstract) |
| Kriegeskorte, Mur & Bandettini 2008 | *Front Syst Neurosci* 2:4, "Representational similarity analysis – connecting the branches of systems neuroscience" ([DOI](https://doi.org/10.3389/neuro.06.004.2008)) | RDMs abstract away from channel correspondence, so brain, model and behavior can be compared. Tested with randomization and bootstrap. | VERIFIED (abstract) |
| Nili et al. 2014 | *PLoS Comput Biol* 10(4):e1003553, "A toolbox for representational similarity analysis" ([DOI](https://doi.org/10.1371/journal.pcbi.1003553)) | MATLAB RSA toolbox: nonparametric model tests and comparisons, searchlight RSA, and the linear-discriminant t (LD-t) distance. | VERIFIED (abstract) |

## 5. Horikawa, Cowen, Keltner & Kamitani 2020, *iScience* 23(5):101060 ([DOI](https://doi.org/10.1016/j.isci.2020.101060); PMID 32353765)

Main text is from `SP/h20.txt`. The Transparent Methods supplement was not reachable; I filled parameters from the authors' code, cloned to `V2/evnr_m` (KamitaniLab/EmotionVideoNeuralRepresentation).

**Setup** (VERIFIED, L58–75)
- 5 subjects, 2,181 videos, 34 categories plus 14 dimensions.
- Responses: shift 4 s, then average over the video.
- 6-fold CV with regularized linear regression.
- Region-wise decoders on HCP360 plus 10 subcortical regions.

**UMAP** (VERIFIED main text L145–151 and L256–260; parameters VERIFIED in code)
- On emotion scores (`code/umap_on_emotion_scores.ipynb`): fit on the true 34-category scores, then `.transform` the decoded scores. Parameters: metric='correlation', n_neighbors=10, min_dist=1.0, spread=3, seed=1. Agreement: r = .46 (x) and .53 (y).
- On brain patterns (`code/umap_on_brain_activity_distance.ipynb`): a precomputed correlation-distance matrix among the 2,181 patterns from **selected voxels only**. Voxels were selected as significantly and best predicted by the category or dimension encoding models. Parameters: n_neighbors=20, min_dist=0.5, spread=10, seed=1.

**Clustering** (VERIFIED, L271–281; code `code/sub/perform_clustering_analysis.m` L12, L164, L185–186)
- k-means on the voxel patterns, k = 27 (code also runs 15 and 50); 'Distance','correlation'; 10 replicates.
- For each emotion, they took the top 5% of videos (109), built the histogram over clusters, then compared sorted histograms and entropy (ANOVA).
- This is grouping and thresholding, which conflicts with our rules.

**Principal gradient and "transmodal"** (VERIFIED, L217–239)
- They used Margulies et al. 2016's principal gradients:
  - PG1 runs from unimodal to transmodal.
  - PG2 runs visual → auditory/somatomotor; its sign is flipped "following the convention of Margulies et al.", matching `-map{2}` in `code/sub/draw_figure5GH.m` L59.
- **"Transmodal" is not a defined ROI.** It means the high end of the continuous PG1 axis.
- Voxels were split into **10 bins of roughly equal voxel count along PG1** (Fig. 5H caption, L220).
- Each voxel's best model (visual object / semantic / emotion) was located in PG space (Fig. 5G). Object, semantic and emotion voxels peak at low, mid and high PG1 respectively, with an ANOVA frequency × level interaction.
- UNVERIFIED (Transparent Methods): how the per-subject PG maps were derived. The code loads precomputed `<sbj>_pringrad_values.mat`.

**Covariate models** (VERIFIED, L200–208)
- Visual object model: a pretrained object network (Simonyan & Zisserman 2014). Which layers is UNVERIFIED.
- Semantic model: crowdsourced concept labels.
- The emotion model won in IPL, TE, DLPFC, DMPFC, VMPFC, OFC and Yeo networks 8/10/13/16/17.
- They did **no variance partitioning**. They used best-model-per-voxel, slope angles, and a joint category+dimension model (+1.8% vs +75.9% significant voxels).
- RSA in Figs. S5C/D was a robustness check only.

**Identification** (VERIFIED, L108–126, L188–189)
- Video identification is pairwise: the true video vs each of the other 2,180, by correlation; chance 50%.
- Emotion identification across subjects uses the region-wise accuracy patterns; example: 5-way 71.4% (categories).

## 6. Horikawa 2025, *Sci Adv* 11(45):eadw1464, "Mind captioning: Evolving descriptive text of mental content from human brain activity" ([DOI](https://doi.org/10.1126/sciadv.adw1464); PMID 41191769)

Main text from `SP/mindcap.txt`; code from `V2/mindcap_repo`.

**Data** (VERIFIED, L24, L122–136, L186–188)
- 6 subjects (Japanese, non-native English speakers).
- 2180 unique videos (2196 minus 16 duplicates), shown silent, free viewing.
- Blocks are ≥10 s: short videos repeat, long ones play once.
- Training: 58 usable runs. Test: 72 videos × 5 repetitions, averaged.
- Preprocessing: shift 4 s, despike, average within block, z-score within run.
- The source study is cited as "(36)", but the local text also numbers RoBERTa as (36), so the stimulus source is UNVERIFIED.

**Features and decoders** (VERIFIED, L204–208, L222–234)
- 42 language models were screened by CV encoding; **DeBERTa-large** was chosen.
- Semantic feature per layer: token mean excluding special tokens; **all layers** used; averaged over 20 captions per video.
- Code (`code/python/util/mcap_utils_demo.py` L1044–1050) uses `hidden_states[1..N]`, which excludes the embedding layer. The layer count N is UNVERIFIED.
- Decoders:
  - one ridge model per feature unit;
  - whole brain, with up to 50,000 voxels pre-selected by encoding accuracy inside the training data;
  - 6-fold outer CV with 5-fold inner CV;
  - λ chosen per layer, model and subject.
- The 10-value λ grid (log-spaced 10–10,000) is stated in the encoding section. The decoding section only says "optimized on training data".
- Other feature models:
  - Vision: TimeSformer (ImageNet + Kinetics-400). Frames sampled every 32 (at least 8), spatial average, 3 crops, then temporal average.
  - Visuo-semantic: CLIP ViT-B/16, final layer, 197 tokens × 768 = 151,296 dimensions, frame-averaged.

**Text generation** (VERIFIED, L238–248; code `code/python/mcap_analysis.py` L73, L76, L106–111)
- Loop of mask → RoBERTa-large MLM unmask → keep the top 5 candidates.
- Candidates are scored by Pearson r with the target features averaged over layers, with a length penalty s = r / l^α, α = 0.1.
- Search width 130, 100 iterations, 5 restarts, starting from `<unk>`.

**Identification** (VERIFIED, L38, L72, L78, L290–300)
- Text-based:
  - Similarity of the generated description to the reference captions of all 2180 videos: 20 correct captions vs 43,580 incorrect captions (2,179 videos).
  - Feature correlation and BERTScore use the mean over captions; BLEU, METEOR, ROUGE-L and CIDEr use the max.
  - Candidate sets range from 2 (chance 50%) to 100 (chance 1%). For more than 2 candidates, incorrect videos are drawn at random over 100 repetitions. The 2-way case uses all pairs.
  - Results: about 50% at 100-way for perception; "nearly 40%" at 100-way for recall in proficient subjects.
- Feature-based pairwise:
  - Pearson r of the decoded vector with each candidate's model features; correct vs each of 2,179 incorrect; chance 50%.
  - Done per model (TimeSformer / CLIP / DeBERTa) and per layer.
  - Perception→imagery generalization measured as the angle to the parity line.

**Imagery block timing** (VERIFIED, L142–152)
- 30 runs × 12 trials, totaling 72 videos × 5.
- Each trial:
  1. Preparation: a verbal cue (one of the 20 captions, fixed), self-paced; button press, then a beep and less than 1 s of rest.
  2. Imagery, eyes closed: same duration as the stimulus block, **+2 s**; a beep ends it.
  3. The actual video.
  4. Two 3-s ratings (accuracy, vividness; 5-point scale).
- Every block is followed by 2 s of rest; each run has 32 s of rest at the start and 8 s at the end.
- Brain data from the preparation period gave near-chance accuracy in most subjects (S2 was the exception).


##### R4_external_data
# External datasets for Kragel-style demos: verified facts

Tags: **V** = VERIFIED (I read the primary file, path or URL given). **I** = INDIRECT (search snippet only). **U** = UNVERIFIED. PubMed-sourced items include their DOIs.

**Blocked hosts in this session.** These were blocked by the proxy or failed DNS: proceedings.neurips.cc, zenodo.org, huggingface.co, movienet.github.io, richardtml.github.io, cs.virginia.edu, gin.g-node.org, files.grouplens.org, openneuro.org (API) and lsa.pucrs.br. OpenNeuro data was reachable through the S3 mirror (s3.amazonaws.com/openneuro.org) and through GitHub git mirrors.

Clones and downloads are in `/tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v2_datasets/`.

---

## 1. Movie-trailer and genre datasets

| Dataset | Citation | Size, labels | Media available | License | Tag |
|---|---|---|---|---|---|
| **Trailers12k** | Montalvo-Lezama R, Montalvo-Lezama B, Fuentes-Pineda G. "Improving Transfer Learning for Movie Trailer Genre Classification using a Dual Image and Video Transformer." *Information Processing & Management* 60(3):103343, 2023 | 12,000 titles. 10 multi-label binary genres: action, adventure, comedy, crime, drama, fantasy, horror, romance, sci-fi, thriller. Trailers manually verified. `mtgc.csv` has columns `mid` plus the 10 genres, and 3 stratified folds (`split0-2`: 0 = train, 1 = val, 2 = test) | `metadata.json` holds **IMDb metadata and YouTube ids**. Precomputed features in zarr format: frame-level ImageNet ShuffleNet/ResNet50/Swin and clip-level Kinetics ShuffleNet3D/R(2+1)D/Swin3D, 24 frames per clip. Poster Swin features. **No raw mp4.** Hosted on Zenodo, doi 10.5281/zenodo.5716409 | CC BY-NC-SA 4.0 | **V**: `t12k_site/docs/index.md` (lines 12-145, branch `site` of github.com/richardtml/trailers12k); `richardtml_DIViTA/files.py` and `utils.py:11-14` |
| **LMTD / LMTD-9** | Simões GS, Wehrmann J, Barros RC, Ruiz DD. "Movie genre classification with convolutional neural networks." IJCNN 2016, pp. 259-266. Also Wehrmann & Barros, *Applied Soft Computing* 2017 | About 10K trailers in total. LMTD-9: **4,021 trailers**, 9 multi-label genres. In the DB the split codes are 0/1/2 with counts 2874/374/773. The SQLite DB has 9,408 trailers, 5,721 movies (IMDb ids) and 24 genres | README says raw mp4 (~90 GB), keyframes (~32 GB) and features (~4.5 GB) can be fetched from lsa.pucrs.br. **That host did not resolve here.** The Trailers12k comparison table (March 2023) marks LMTD as having no downloadable data. **The YouTube id is recoverable from the filename for 8,958 of 9,408 trailers** (e.g. `...-4CWkZ0CUOdM.mp4`) | none stated | **V**: `lmtd/README.md`, `lmtd/lmtd9/data/database.db` (queried), `lmtd/scripts/*.sh`, `t12k_site/docs/images/table.png` |
| **Moviescope** | Cascante-Bonilla P, Sitaraman K, Luo M, Ordonez V. "Moviescope: Large-scale Analysis of Movies using Multiple Modalities." arXiv 1908.03180, 2019 | 5,027 movies, 13 multi-label genres. Average trailer length about 2 min | **Trailer URLs only** (Trailers12k table). The MovieCLIP paper reports that 3,900 of 4,927 videos were still on YouTube | U | sample count, genre count and URL-only status are **V** from Trailers12k `table.png`; everything else **I**. No official repo was found. github.com/maximus009/MovieScope is an unrelated project |
| **MovieNet** (trailers) | Huang Q et al., ECCV 2020 | 1,100 movies and **33K unique trailers**. Metadata for 375K movies, with 805K genre tags over **28 genres** (multi-label, e.g. Titanic = Drama, Romance) | "we can only release the key frames but not the original movies". Trailers likewise come as keyframes and STFT audio. **No raw video.** Trailers12k's table marks trailers as not downloadable. Whether YouTube ids are released: **U** | U | **V**: `movienet_movienet-tools/docs/wiki/data.md` lines 12-81. The 60K vs 33K footnote is **V** from `table.png` |
| **MMTrail** | Chi X et al. "MMTrail: A Multimodal Trailer Video Dataset with Language and Music Descriptions." arXiv 2407.20962, 2024 | 20M clips with frame captions and 2.1M clips with multimodal captions, 27.1K hours. **No genre or emotion labels.** The first sample's source video lasts 9,301 s, so the sources are not only roughly 2-min trailers | `video_id` (YouTube-style) plus caption metadata. "We provide only the caption files" | RUDA1.0 | **V**: `litwellchi_MMTrail/README.md`, `MMTrail2M_sample1w.json` (9,980 entries) |
| **MovieLens-20M YouTube Trailers** | GroupLens | 25,623 YouTube ids for MovieLens movies, not all manually verified. MovieLens genres are multi-label | YouTube ids only | CC BY 4.0 | **I** (files.grouplens.org blocked). The MovieLens "tag genome" (continuous tag-relevance scores such as "dark" or "feel-good") could serve as continuous mood targets: **U** |
| **Video2Reaction** (2025-26) | Nguyen T, Zhang S, Shankar S, Jagatap G, Chandran D, Fanelli A, Fiterau M (UMass Amherst & Dolby). arXiv 2607.06875 (**I**) | ">10,000 videos" of movie clips. Each clip has a **distribution over 21 audience-reaction classes**: sadness, disgust, grief, fear, disapproval, disappointment, embarrassment, nervousness, annoyance, anger, confusion, realization, caring, curiosity, relief, approval, surprise, excitement, amusement, admiration, joy. Plus a dominant reaction and **IMDb genre multi-hot over 23 genres**, `movie_name` and `clip_description`. Labels come from **an LLM annotating YouTube comments**, with 86% correctness under blind human check | Features and metadata on HF (`video2reac/Video2Reaction`). Raw clips must be fetched from YouTube with yt-dlp. The project page says "Dataset and annotation code will be released upon acceptance" | repo CC BY 4.0 | **V**: `Information-Fusion-Lab-Umass_video2reaction/src/dataset.py:20-55,345-401`, `README.md`, and `...-bench.github.io/index.html` |

**Fit for item 1.**
- **Trailers12k is the best trailer-to-genre target.** It is manually curated, multi-label and has fixed folds. YouTube ids are needed to get raw video; link rot will be non-zero.
- **Video2Reaction is the only set found that pairs clip-level emotion distributions with genre.** It directly enables "34-d profile → audience reaction distribution and genre" analyses. Caveat: its labels are derived from text (comments) by an LLM, so the semantic channel is built in. That is useful for the decomposition story but must be stated.

---

## 2. Video affect datasets independent of VCE and Cowen

| Dataset | Citation | Size, labels | Media | License, access | Overlap risk | Tag |
|---|---|---|---|---|---|---|
| **LIRIS-ACCEDE** | Baveye Y, Dellandréa E, Chamaret C, Chen L. IEEE Trans. Affective Computing 2015, doi 10.1109/TAFFC.2015.2396531 | Discrete set: 9,800 excerpts of 8-12 s from 160 Creative Commons films. Valence and arousal **ranks** from crowdsourced pairwise comparisons, later mapped to scores. Continuous set: 30 films with per-second valence/arousal, 16 annotators (joystick, 10 s window with 1 s shift, range -1 to 1). Used in MediaEval | Actual video files (CC films) | BY-NC-SA, academic; liris-accede.ec-lyon.fr (form terms **U**) | None with VCE or Cowen. **Emo-FilM's films come from the LIRIS database (V)** | **I** (except the Emo-FilM link) |
| **VideoEmotion-8** | Jiang YG, Xu B, Xue X. AAAI 2014 | 1,101 user-generated videos from YouTube and Flickr, average 107 s. **Single-label** Plutchik-8 (Ekman 6 plus anticipation and trust) | U (Fudan page) | U | Platform overlap with Cowen's web-sourced clips is possible: **U** | **I** |
| **Ekman-6** | Xu B et al., IEEE TAC 2018 | 1,637 videos from YouTube and Flickr, average 112 s. 6 single-label classes. Split 819/818 | U | U | as above | **I** |
| **GIFGIF / GIFGIF+** | Chen W, Rudovic O, Picard R (MIT Media Lab) | Pairwise "which GIF better expresses X" votes over 17 emotions. GIFGIF+: 23,544 GIFs. A later paper says GIFGIF+ is "not released". Columbia DVMM used about 3,800 GIFs with 17-emotion scores | U | U | low | **I** |
| **EmoSet** | Yang J, Huang Q, Ding T, Lischinski D, Cohen-Or D, Huang H. ICCV 2023 | **Images.** 3.3M images, of which 118,102 are human-labelled. **Single-label** Mikels 8: amusement, awe, contentment, excitement, anger, disgust, fear, sadness. Attributes: brightness, colorfulness, scene, object, facial expression, human action | Dropbox zip | code MIT; data license not stated | low | **V**: `JingyuanYY_EmoSet/README.md`, `info.json` |
| **FilmStim** | Schaefer A, Nils F, Sanchez X, Philippot P. *Cognition & Emotion* 2010 | 70 film excerpts rated on several dimensions by 364 participants | FilmStim.zip, 1.23 GB (French; English versions added 2016) | free, sites.uclouvain.be/ipsp/FilmStim | low | **I** |
| **Samson 2016 film library** | Samson AC, Kreibig SD, Soderstrom B, Wade AA, Gross JJ. *Cogn Emot* 30(5):827-56. [doi](https://doi.org/10.1080/02699931.2015.1031089) | 300 amateur clips of 20-33 s were screened, then 199 kept (51 positive, 39 negative, 59 mixed, 50 neutral). Continuous amusement and repulsion ratings; 411 online raters | U | U | low (web-sourced amateur clips) | **V** (PubMed abstract) |
| **EEV** | Sun JJ, Liu T, **Cowen AS**, Schroff F, Adam H, Prasad G. 2020-21 | 23,574 YouTube videos. 15 *viewer facial-expression* scores at 6 Hz, produced by an automatic FER model. Test labels withheld | YouTube ids (csv) | U | **The taxonomy is Cowen's, and Cowen is a co-author** | **I** |
| **eMotions** | Wu X et al. 2025, arXiv 2508.06902 | 27,996 Douyin/Kuaishou/TikTok videos. 6 categorical labels: Excitation, Fear, Neutral, Relaxation, Sadness, Tension | release unclear | U | low | **I** |
| **Video2Reaction** | see item 1 | 21-class distributions | YouTube | CC BY 4.0 | low | **V** |

**Overlap notes.**
- VCE videos were sourced from **Reddit and Instagram** (**I**, quoted from the NeurIPS supplement via search). VCE's 27 categories are modelled on Cowen & Keltner (2017).
- **V2V videos are a subset of VCE videos.** README line 112: "this is a subset of the VCE dataset videos that have V2V labels" (**V**). So V2V gives independent *labels* (pleasantness) but **not** independent *stimuli* if VCE is used in training.
- For any web-sourced set (VideoEmotion-8, Ekman-6, Samson), run near-duplicate hashing against the Cowen and VCE pools. No overlap analysis was found (**U**).

**Fit for item 2.** Continuous labels plus downloadable media: LIRIS-ACCEDE (valence/arousal), Emo-FilM (50 items at 1 Hz) and Samson (amusement/repulsion). VideoEmotion-8, Ekman-6 and EmoSet are single-label. Under the project rule against grouping stimuli into categories, they could only serve as an external read-out, never as a grouping.

---

## 3. Emo-FilM (Morgenroth et al., *Sci Data* 12:684, 2025)

Source: PMC12019557, read in full. [doi](https://doi.org/10.1038/s41597-025-04803-5).

**Datasets.** The paper's Data Records section says annotation is OpenNeuro **ds004872** and fMRI is **ds004892** (**V**). Both are licensed **CC0** (**V**, from each `dataset_description.json`).

**Films.**
- 16 films were annotated; 14 were used for fMRI. Damaged Kung Fu and Riding the Rails were dropped for low agreement.
- All are Creative Commons films "taken from the films included in the LIRIS database", with beginning and end credits cut (**V**).
- Paper Table 1 (**V**), as title, cut duration, genre:
  - After The Rain, 8:16, Drama
  - Between Viewings, 13:28, Comedy/Drama
  - Big Buck Bunny, 8:10, Animation/Comedy
  - Chatter, 6:45, Thriller
  - First Bite, 9:59, Romance
  - Lesson Learned, 11:07, Drama
  - Payload, 16:48, Drama/Sci-Fi
  - Sintel, 12:02, Animation/Fantasy
  - Spaceman, 13:25, Romance/Drama
  - Superhero, 17:08, Drama
  - Tears Of Steel, 9:48, Action/Sci-Fi
  - The Secret Number, 13:04, Drama
  - To Claire From Sonny, 6:42, Drama
  - You Again, 13:18, Romance/Drama
- Scan lengths include a 90 s washout at each end (e.g. Sintel 710 TRs at TR 1.3 s).

**Obtaining the stimuli.** Videos are **not in the datasets**. The sources are listed in `ds004892/code/FilmInfo.txt` (downloaded from S3, **V**):
- Vimeo ids: After The Rain 40104084, Between Viewings 43763789, First Bite 23980578, Lesson Learned 40539260, Payload 50509389, Superhero 23423341, The Secret Number 43732205, You Again 33454078.
- vodo.net: Chatter, Spaceman.
- Official sites: bigbuckbunny.org, sintel.org, tearsofsteel.org.
- YouTube 8rKW-VRFczA: To Claire From Sonny.
- Each film's CC variant (BY, BY-NC, BY-SA, BY-NC-SA) is listed in the same file.

**Exact cut points** come from `ds004892/code/BBL_experiment_Movies_without_credits_exp_files.xlsx`, parsed by me (**V**). Every cut length matches Table 1. Start and end in seconds:

| Film | Start | End | Film | Start | End |
|---|---|---|---|---|---|
| AfterTheRain | 32 | 528 | Spaceman | 50 | 855 |
| BigBuckBunny | 0 | 490 | FirstBite | 5 | 604 |
| Chatter | 30 | 435 | LessonLearned | 0 | 667 |
| TearsOfSteel | 0 | 588 | Superhero | 50 | 1078 |
| YouAgain | 7 | 805 | TheSecretNumber | 20 | 804 |
| BetweenViewings | 14 | 822 | Payload | 0 | 1008 |
| Sintel | 23 | 745 | ToClaireFromSonny | 0 | 402 |

**Annotations.**
- CARMA software, sampled at **1 Hz**, scale 0-100. 44 raters; each item rated by 4 raters (sometimes 3).
- The consensus is computed after per-rater z-scoring across films (**V**, paper).
- After reliability filtering there are **50 items**. Removed items: Breathing, Consequences, Movement, EyesOpen, Jaw (**V**).
- Files (**V**):
  - `derivatives/Annot_<Film>_stim.tsv.gz`, one per film, 50 columns. The Sintel file has 722 rows, which equals 722 s.
  - `C_Annot_FILMS_stim.tsv.gz`, all 14 films concatenated: **9,600 rows**, which equals the summed durations.
  - Per-rater raw series in `sub-<word>/beh/sub-*_task-<Film>_recording-<Item>_stim.tsv.gz` (44 raters).
- The column order comes from `Annot_Sintel_stim.json` (**V**). The last 13 columns are the **13 discrete emotions**: **Anger, Guilt, WarmHeartedness, Disgust, Happiness, Fear, Regard, Anxiety, Satisfaction, Pride, Surprise, Love, Sad**. Assigning these 13 as "discrete" rests on column order plus the paper's count; the paper's Supplementary Table 1 was not accessible (**I** for that assignment).
- The other 37 retained items are GRID components: Standards, PleasantSelf, SocialNorms, PleasantOther, GoalsOther, Controlled, Predictable, Suddenly, Agent, Urgency, Lips, Tears, Eyebrows, Smile, Frown, Stop, Undo, Repeat, Oppose, Attention, Tackle, Command, Support, Move, Care, Bad, Good, Calm, Strong, IntenseEmotion, Alert, AtEase, Muscle, Heartrate, Throat, Stomach, Warm.

**fMRI.**
- 30 subjects (S01-S32, excluding S12 and S18). 4 sessions each. Siemens 3T, TR 1.3 s, 2.5 mm isotropic, multiband 3.
- **Every subject watched all 14 films.** sub-S01 has 15 BOLD runs (14 films plus rest) (**V**).
- Physiology (PPG, respiration, EDA) recorded at 1 kHz.
- After scanning, subjects re-rated about 292 clips of about 7 s each. These are in `beh/*_events.tsv` (columns onset, duration, 5 items, trial) (**V**).

**Preprocessing.** **Not fMRIPrep.** The pipeline is FSL FEAT: MCFLIRT, BET, 6 mm smoothing, high-pass sigma 50 s, then WM, CSF and 6 motion regressors removed (**V**, paper and the sidecar `..._space-MNI_desc-ppres_bold.json`). Derivatives in `derivatives/preprocessing/` (**V**):
- `space-MNI_desc-ppres`: 450 files
- `space-subject_desc-ppres`: 930 files
- `space-orig_desc-prepro`: 450 files
- also `mriqc/`, `physioqc/`, `onset_validation/`, `annotation_validation/ValItems.mat`, `ValTimes.mat`

**Sizes** (summed from git-annex keys, **V**):
- ds004892: **790.6 GB** in total. Raw sub-* is 141.4 GB. Preprocessing is 646.4 GB, of which MNI is 358.7 GB, subject space 164.0 GB and orig 122.3 GB. MRIQC is 2.7 GB.
- ds004872: about 0.01 GB.

---

## 4. VCE: V2V (Video to Valence)

Source: `clones/emodiversity/README.md` lines 92-136 (**V**). The copy at `verify_A_lens/hendrycks_emodiversity/README.md` is identical (repo commit 4deaea3, October 2022, MIT code license).

**Counts.**
- 26,670 videos in total, **a subset of VCE videos**.
- `train`: 11,038 **pairwise** comparisons on 16,125 unique videos.
- `test`: 3,189 pairwise comparisons on 6,223 unique videos.
- `listwise`: 1,758 ranked lists on 4,322 unique videos, at most 4 videos per list.
- The video sets of the three splits are **mutually exclusive** (16,125 + 6,223 + 4,322 = 26,670).

**Format.**
- `train_labels.json` and `test_labels.json` hold `{"comparisons": [[id_a, id_b], ...]}`, and **the second id is the preferred one**.
- `listwise_labels.json` lists are ordered **from least to most preferred**.
- Videos are `videos/NNNNN.mp4`, the same ids as VCE. `metadata.json` is identical to VCE's (e.g. 12 s, 30 fps, 256×320).
- Distributed via Google Drive.

**Reference training and evaluation code** (**V**, `verify_D_demo/JunShern_VideoMAE/run_v2v_finetuning.py:25-88`):
- The model emits a scalar per video. Loss is `BCEWithLogits(logit(v_pref) − logit(v_other), 1)`, i.e. Bradley-Terry-style.
- Pairwise accuracy is the fraction of pairs with a positive difference.
- **Listwise accuracy requires the whole list to be in correct order.**
- The STAM loaders are in `clones/emodiversity/STAM/wellbeing_datasets.py` (from line 481).

**Annotation protocol** (**I**, NeurIPS supplement B.2 via search snippet):
- Amazon Mechanical Turk workers were asked which video *other workers* would find most pleasant, falling back to their own judgement, judging each video holistically.
- 9 annotations per pair; only pairs with ≥8/9 agreement were kept.
- "Pleasantness" is framed as a proxy for wellbeing.

---

## 5. Public fMRI with trailers or genre-diverse films

| Dataset | Genres | fMRI | Stimuli | Tag |
|---|---|---|---|---|
| **NNDb v1.0** (Aliko S, Huang J, Gheorghiu F, Meliss S, Skipper JI. *Sci Data* 7:347, 2020; [doi](https://doi.org/10.1038/s41597-020-00680-2)) | **10 full films, one genre each** (paper Table 2): 500 Days of Summer (Romance, 5,470 s), Citizenfour (Documentary, 6,804), 12 Years a Slave (Historical, 7,715), Back to the Future (Sci-fi, 6,674), Little Miss Sunshine (Comedy, 5,900), The Prestige (Thriller, 7,515), Pulp Fiction (Action, 8,882), The Shawshank Redemption (Drama, 8,181), Split (Horror, 6,739), The Usual Suspects (Crime, 6,102) | 86 subjects. **Each watched one film**: n=20 for 500 Days, 18 for Citizenfour, 6 for each of the others. TR 1 s. OpenNeuro ds002837, CC0. Derivatives are AFNI-preprocessed in MNI space (blur/no-blur, censor, ICA variants) plus face and word annotation `.1D` files. Sizes: raw 95.6 GB, total **1,281.7 GB** (annex keys) | **Not distributed.** DVDs can be bought by ASIN/EAN (Table 2) | **V**: `scratchpad/nndb.txt` lines 72-89, 237, 263; `v2_datasets/ds002837` (README, derivatives listing) |
| **Emo-FilM** | 14 short films with Table 1 genre tags (Drama-heavy; also Thriller, Romance, Animation, Sci-Fi, Action, Comedy) | 30 subjects, all 14 films each, plus continuous 50-item annotations | free CC films (see item 3) | **V** |
| **CNeuroMod / Algonauts 2025** | Friends S1-7. Movie10: bourne, figures, life, wolf. Out-of-distribution (OOD) set: chaplin, mononoke, passepartout, planetearth, pulpfiction, wot | 4 subjects (01, 02, 03, 05). Parcellated Schaefer-1000 h5 files, CC0. **OOD fMRI is withheld** (Codabench benchmark) | `.mkv` via datalad submodules | **V**: `v2_datasets/algo25/README.md` lines 25-26, 95-142, 209; directory listing |
| **vim-2 / Gallant shortclips** (Nishimoto et al., *Curr Biol* 2011, [doi](https://doi.org/10.1016/j.cub.2011.08.031); Huth et al. 2012/2022) | Clips "drawn from the Apple QuickTime HD gallery … and YouTube", cut to 10-20 s. **Trailer origin is implied, not stated. No titles or genre labels** | vim-2: 3 subjects, 4T, occipital only, 7,200 s train and 540 s test. Shortclips: 5 subjects, 3T whole brain, CC0, GIN (**I**) | frames in hdf files (`stimuli/train_00.hdf`) | stimulus source **V** (PMC3326357); shortclips facts **I**; hdf layout **V** (`vwt/tutorials/notebooks/shortclips/07_extract_motion_energy.ipynb`) |
| **Koide-Majima et al. 2020** (*NeuroImage* 222:117258, [doi](https://doi.org/10.1016/j.neuroimage.2020.117258)) | movies with **80 emotion ratings per 1-s scene**, about 3 h of fMRI | data availability **U** (no PMC full text) | U | abstract **V** (PubMed) |
| HCP 7T movie, Koide-Majima data release | — | — | — | U, not checked |

**Fit for item 5.**
- **No public fMRI was found that uses trailers with genre labels.**
- NNDb is the only "10 genres × fMRI" set. Genre is confounded with film and with subject group (n=1 film per genre), so genre decoding there reduces to film identity. A defensible design is within-film time courses: model-predicted 34-d profile vs brain-decoded profile, compared across films.
- Emo-FilM is the best brain-side resource: within-subject, all films seen by every subject, 1 Hz continuous labels, coarse multi-genre tags. It supports a demo of genre tag ← brain-decoded profile time-course, but only across 14 films.

**Practical shortlist for Kragel/Gao-style demos.**
1. Trailers12k (YouTube ids, 10 genres): a Kragel-style trailer-to-genre readout from frozen 34-d profiles, with per-genre top-weight emotions in the style of Gao 2025.
2. Video2Reaction: 21-class audience distributions plus 23 genres, compared with the 34-d profile by RSA or regression.
3. Emo-FilM: brain plus 1 Hz labels plus genre.
4. LIRIS-ACCEDE: continuous valence/arousal, independent stimuli.

V2V gives independent pleasantness labels but on VCE stimuli.


##### R5_demo_ideas
# Kragel- and Gao-style demonstrations for EmoBrain: 10 candidates, stress-tested

Evidence tags: **[V]** = I read the primary text or code (source list at the end gives full paths). **[I]** = search snippet only. **[U]** = unverified.

Settings marked "prop." are my proposals, not values taken from a paper. Kragel, Gao and Haufe numbers are cited where I read them.

---

## 0. Anchors (what the user liked, as verified)

**Kragel et al. 2019, Sci Adv, PMID 31355334, DOI 10.1126/sciadv.aaw4358 [V]**
- Stimuli: 28 trailers (rom-com 9, action 9, horror 10) [kragel.txt:41].
- Features: EmoNet final 20-category layer, averaged over frames [kragel.txt:41,43].
- Classifier: PLS one-vs-all with 10-fold CV [kragel.txt:41,107].
- Coefficients: 1,000-iteration bootstrap [kragel.txt:43].
- Result: 71.43% (chance 35.7%), mean AUC 0.855. Errors were mostly action vs horror; rom-coms were never misclassified [kragel.txt:45].
- Coefficients by genre [kragel.txt:47]:
  - rom-com: romance, amusement, sadness
  - horror: interest, horror, aesthetic appreciation
  - action: anxiety, awe, fear
- Figures used CC0 stand-in images instead of actual trailer frames [kragel.txt:43].
- The number of PLS components is not stated in the text I read [U].

**Gao, Ajith & Peelen 2025, Commun Biol, PMID 40325234, DOI 10.1038/s42003-025-08145-1 [V]**
- Transformation matrix: AlexNet fc8 (1,000 labels) × 20 emotions, averaged over 15 CV folds. Fig. 3 shows top-10 positive and top-10 negative labels for 6 emotions [gao.txt:35].
- PLSR with 20 components [gao.txt:179]. Leave-one-session-out CV [gao.txt:169].
- For Cowen videos: 3 frames at 25/50/75% of the clip, 15-fold CV [gao.txt:175].
- On Cowen17, EmoNet beat AlexNet; object labels were weaker for explicitly evocative scenes [gao.txt:89].
- The text never mentions Haufe or activation patterns [grep of gao.txt].

**Haufe et al. 2014, NeuroImage 87:96–110, PMID 24239590 [V abstract]**
- Weights of a backward (decoding) model can be non-zero on channels that are unrelated to the signal. They must be converted to a forward pattern before interpretation.
- The forward pattern is A = Σ_X W Σ_ŷ⁻¹. I am stating this from memory; I did not re-read the equation [U].

---

## D1. Trailer → genre through the emotion lens (with a brain-route version)

**(a) Question.** Do genres, which are external non-emotion labels, separate along the 27 axes of a lens trained on independent clips and independent raters? Which emotions define each genre?

**(b) Setup**
- **Stimuli, stage 1:** a Kragel-matched replication with 28–30 trailers in 3 genres.
- **Stimuli, stage 2:** LMTD-9.
  - 4,021 trailers, 9 multi-label genres, official split 2,874/374/773 [V lmtd database.db query; README].
  - The raw-video host lsa.pucrs.br gave no response from this sandbox [U].
  - Trailers12k publishes only precomputed features and labels on Zenodo, not raw video [V DIViTA/files.py]. It is unusable for the lens.
- **Lens:** frozen VCE-trained video model producing 27 continuous intensities. The VCE authors' VideoMAE fork uses a K400 ViT-B 16-frame pretrain [V emodiversity README:149].
  - Applied every 1 s (prop.), giving a 27×T arc.
  - Summary = time-mean, as Kragel did. Time-SD is secondary.
- **Analysis:**
  - PLS-DA one-vs-rest.
  - k chosen by inner CV (prop.).
  - Outer CV: 10-fold for the 28 trailers; official test split for LMTD.
  - Genre×emotion coefficients from 1,000 bootstraps, plus Haufe patterns (corr(emotion_i, genre score)).
- **Decomposition (framed as decomposition, not competition):** genre information from
  - the 27-d output,
  - the lens penultimate embedding,
  - low-level features (motion energy, color, luminance),
  - the 27-d output after partialling out low-level features.

  This gives the share of genre information that survives the 27-emotion bottleneck.
- **Brain-route version (in silico):** ŷ_R = D_R(E_R(f(x))).
  - E_R = HK encoding model for region R (features → ROI pattern).
  - D_R = HK decoder (ROI pattern → 34-d profile).
  - Run genre PLS on ŷ_R for early visual, LOC/OTC, STS/TPJ and PCC/mPFC.
  - Nulls: encoder fit to permuted stimulus labels with its own α, and a rank-matched random subspace [V synthesis.md:13,179].
  - Claims are limited to differences between regions [V synthesis.md:180].
  - For a real-brain genre test, see D10.
- **Figure:**
  - A: arc of a CC-BY trailer (Sintel and Tears of Steel are CC-BY [V FilmInfo.txt]).
  - B: genre×emotion coefficient violins.
  - C: ROC curves.
  - D: bottleneck-share bars.
  - E: region×genre coefficient heatmaps for the brain route.

**(c) Why it is about emotion, not performance.** Genre is an industry label for intended affect. The coefficients are statements about emotion concepts. Accuracy is reported only as a construct check.

**(d) Rule compliance.**
- Genre is an external, non-emotion label.
- The lens output is continuous, with no softmax and no top-1. This deviates from EmoNet's 20-way classifier, and the paper must say so.
- No LLM.

**(e) Prior art.**
- Kragel 2019 [V].
- Affective features are already used for genre classification in computer science: Sulun et al. 2024 used face_emotion features; also Vishwakarma 2021 and Ben-Ahmed & Huet [I].
- Genre has been decoded from MEG (Ghaemmaghami) [I].
- One search found no fMRI genre decoding [I].
- So the concept is not new. What is new is the continuous 27-d independent-rater lens and the region route.

**(f) Risks and controls.**
- Horror trailers are darker → low-level-only baseline and partialled coefficients.
- Possible VCE–trailer overlap [U] → near-duplicate screen (embedding cosine plus perceptual hash), drop matches.
- Title cards and text overlays → mask or drop those frames.
- Drama dominates the multi-label set → per-genre AP against prevalence; use the balanced 3-genre subset for the headline.
- Audio and music carry much genre information and the lens is video-only → this is conservative.
- The brain route is a model property, not new fMRI [V synthesis.md:21].

---

## D2. Gao on video: object/action/scene → emotion top-weight atlas (stimulus side)

**(a) Question.** Which nameable objects, actions and scenes carry each emotion's variance across 61k videos rated by independent raters?

**(b) Setup**
- **Data:** VCE, 61,046 videos (train 50,000 / test 11,046), 27-d mean intensity on a 0–1 scale [V README:16-20,36].
- **Features (logits with named classes):**
  - AlexNet fc8, 1,000 ImageNet classes, for Gao continuity [V gao.txt:167].
  - A modern ImageNet classifier; ConvNeXt-V2 and timm code are present locally.
  - Kinetics-400 actions.
  - Places365 scenes.
  - Frame sampling: 25/50/75%, as Gao did for Cowen.
- **Analysis:**
  - PLSR with 20 components to replicate Gao; inner-CV k as a sensitivity check.
  - 15-fold CV on VCE-train, fold-averaged coefficient matrix.
  - Out-of-sample r on VCE-test.
  - Applied without refit to Cowen 2,185 on the overlapping emotion names.
- **Figure:** Gao Fig. 3 layout (6 emotions × top-10 positive / top-10 negative labels), with two columns per emotion:
  - rank by raw weight vs rank by Haufe pattern;
  - a stability bar = fraction of bootstraps in which the label is in the top-10.

  Example frames: CC stand-ins, following Kragel's practice.

**(c) Why it is about emotion.** It maps emotion schemas onto the object vocabulary. It tests Gao's object-mediation claim on evocative video, where Gao's own Cowen17 result went against it [gao.txt:89].

**(d) Rule compliance.** Pass.

**(e) Prior art.**
- Gao 2025 [V].
- Kragel 2019 already found the 20 object categories that best predict the 20 emotions [kragel.txt:97].
- A video-scale version was not found [I].
- Novelty is low. Its value is as the foundation for D4.

**(f) Risks and controls.**
- PLS coefficients form a backward model. With 1,000 collinear logits (for example, many dog breeds), weights can point to unrelated labels [Haufe].
  - Report the forward pattern a_e = Cov(X, ŷ_e)/Var(ŷ_e).
  - Pool labels by WordNet hypernym.
  - Apply a frequency floor.
  - Report top-10 overlap between AlexNet and the modern classifier.
- Licensing of VCE frames [U].

---

## D3. Situation-level word atlas from human captions, with an affect-word ablation ladder

**(a) Question.** Which described situations, as opposed to described feelings, carry each emotion?

**(b) Setup**
- **Data:**
  - Cowen videos with 20 human-written descriptive captions each: 43,920 captions over 2,196 IDs, including repeat-presentation IDs [V capstats.py on caption_ck20.csv].
  - VCE has no captions [V README], so this level exists only on Cowen.
- **Features:** fraction of a video's 20 captions containing each lemma. The vocabulary floor is fixed before analysis (prop.).
- **Target:** 34-d log1p_z, z-scored with train statistics only [V project/README.md].
- **Split:** canonical 1748/217/220 [V CONTEXT]. PLS k chosen on val; report test.
- **Pre-registered ladder:**
  - L0: all words.
  - L1: minus an affect lexicon (34 category names and their variants, plus expression verbs such as smile, laugh, cry, scream, scared).
  - L2: nouns only.
  - L3: nouns and verbs, minus face/expression words.
- **Why the ladder is needed (my counts, as tokens / videos):** smiling 402/156, scared 197/84, laughing 174/64, kissing 613/106, crying 84/22, beautiful 244/156 [V].
- **Exact decomposition:** Cov(ŷ_e, y_e) = Σ_j w_{j,e} Cov(x_j, y_e) gives the share of each emotion carried by affect words. This is an arithmetic identity, not a lesion test.
- **Figure:** Gao-style word bars per emotion, L0 and L1 side by side. L1 is the headline.

**(c) Why it is about emotion.** It tests premise (2) at the level of vocabulary. The ladder separates described affect from described situation.

**(d) Rule compliance.** Pass.

**(e) Prior art.**
- No direct prior work found [I].
- Adjacent: the EmoMind 2026 arXiv preprint decodes a 34-d vector and affective captions from HK fMRI [I].
- The Doerig 2025 NMI shuffled-sentence control applies to sentence embeddings, not to bag-of-words [V paper_logic §5].

**(f) Risks and controls.**
- Implicit affect in adjectives ("cute", "beautiful", "scary") → include them in the lexicon and report the whole L0–L3 curve.
- Use the term "human-written descriptive caption", not "affect-neutral" [V paper_logic §5].
- The caption writers are the MindCaptioning crowd, not Cowen's raters, so the two sources are independent.

---

## D4. Brain route: which objects or words are decodable from which region, and which emotion they feed

**(a) Question.** Per region, which nameable contents can be read out, and through which of them does the region carry each emotion?

**(b) Setup**
- **Stage 1 (label-blind):**
  - Regions: atlas groups over the 450 ROIs (Schaefer-400 + Tian-S3) [V project/README].
  - Voxel-wise L2 linear decoders, Horikawa-style (PyFastL2LiR is present locally), from HK brain to D2 logits and to D3 word-presence vectors. Train split only.
  - Per-label decodability r_j^R on the stimulus-held-out test split, with subject-clustered bootstrap CIs [V paper_logic §5].
- **Stage 2 (fixed maps):** object→emotion map W from D2 (fit on VCE, independent of HK) and word→emotion map from D3 (Cowen train).
- **Route:**
  - ŷ^R = Wᵀ d̂^R, compared with the test 34-d profile.
  - The decomposition Cov(ŷ_e^R, y_e) = Σ_j w_{j,e} Cov(d̂_j^R, y_e) gives each decoded label's contribution to each emotion in each region.
- **Figure:**
  - region × emotion small multiples of the top labels, colored by decodability;
  - a Sankey diagram (region → label → emotion) restricted to contributions whose CI excludes 0.

**(c) Why it is about the brain.** It answers Cowen & Keltner's outstanding question ("which brain regions contribute to the conversion of sensory input…") in nameable content [V paper_logic §1].

**(d) Rule compliance.**
- The brain side never sees emotion labels.
- No lesion of the linear readout; that would be tautological [V synthesis.md:20,64]. The decomposition is reported as arithmetic.

**(e) Prior art.**
- Horikawa 2020 iScience region-wise emotion decoding, PMID 32353765 [V].
- Gao 2025: LOC best among visual ROIs [gao.txt:73].
- This combination was not found [I].

**(f) Risks and controls.**
- Decodability tracks label frequency and ROI size → equalize voxel counts; normalize by target reliability.
- Decoded features shrink toward the mean → use correlation-based measures.
- Zero decodability in transmodal cortex ≠ no emotion there → show as blank.
- Show both factors (decodability and weight) separately, not only their product.

---

## D5. In silico "what each region would pick" from 61k VCE videos

**(a) Question.** If a model of each region picks its preferred clips from 61k unscanned videos, are those clips emotionally distinctive according to independent raters?

**(b) Setup**
- **Encoding models:** HK region models (ridge; himalaya is present locally) on V-JEPA2, VideoMAE or PE-Core features.
  - Keep only regions whose test r exceeds both an a-priori floor and their permutation null.
- **Primary analysis (continuous):** predict all 61,046 VCE videos; Spearman correlation between predicted response and each of the 27 intensities → region × emotion map.
- **Illustration:** top-24 / bottom-24 montage per region, compared with:
  - random sets;
  - top-24 along random feature directions with matched predicted variance;
  - a permuted-label encoder with its own α [V synthesis.md:179].
- **Pre-registration:** record the montage lists now for a later prospective fMRI test [V synthesis.md:181].
- **Figure:** one row per region: a 4×6 frame montage plus a 27-bar profile with the null band.

**(c) Why it is about the brain and emotion.** It expresses a region's encoding function as an emotional signature, measured with other people's ratings.

**(d) Rule compliance.** Selection is by predicted brain response, not by emotion. The continuous map is primary.

**(e) Prior art.**
- Ratan Murty 2021, Nat Commun, PMID 34545079: screening and synthesis, validated with new fMRI [V].
- Jang & Kragel 2025, J Neurosci, PMID 40086868: amygdala encoding models plus synthesized images, valence [V].
- A video pool with multi-emotion ratings was not found [I].

**(f) Risks and controls.**
- Extrapolation to the VCE domain; feature-extreme artifacts (darkness, text) → matched-direction null.
- Transmodal encoders are weak → show regional ceilings.
- This is a model property, so it stays out of the headline [V synthesis.md:21].

---

## D6. Emotion arc of a film: content-computable vs context-dependent (Emo-FilM, 1 Hz)

**(a) Question.** Second by second, how much of what viewers feel is computable from what is on screen, and where in the brain does the rest live?

**(b) Setup**
- **Films:** 14 films, 6:42 to 17:08 long [V PMC12019557 Table 1].
- **Annotations:**
  - 50 items at 1 Hz: 13 discrete emotions plus CoreGRID items [V Annot_Sintel_stim.json].
  - Consensus = mean of at least 3 raters' series, each z-scored within rater. Mean agreement r = 0.39 (0.29–0.54 by film) [V PMC12019557].
  - The concatenated file has 9,600 rows, equal to the sum of the film durations [V C_Annot_FILMS_stim.tsv.gz].
  - Per-annotator files exist, so raters can be split [V ds004872/sub-*/beh].
- **Lens:** frozen VCE lens every 1 s → 27×T arc.
- **Mapping to the 13 Emo-FilM emotions** (my comparison of the two verified lists):
  - No fit needed for 7 names: Anger, Disgust, Fear, Anxiety, Satisfaction, Surprise, Sad↔Sadness.
  - Flagged near-synonyms, pre-registered: Happiness↔Joy, Love↔Romance, WarmHeartedness↔Adoration, Regard↔Admiration.
  - No counterpart: Guilt, Pride.
  - Secondary: leave-one-film-out linear map from 27 dims to all 50 items.
- **Statistics:**
  - Pearson r per film and emotion.
  - Annotation lag chosen on held-out films within a pre-set range.
  - Circular-shift null (preserves autocorrelation).
  - Ceiling = leave-one-rater-out agreement.
- **Brain part (needs the ds004892 download, about 132 GB [V paper_logic §8]):**
  - 30 subjects, TR 1.3 s, 90-s washouts, films watched with sound [V PMC12019557].
  - Parcel time series regressed on the HRF-convolved lens arc and on a residual arc = annotation orthogonalized to the lens arc, the audio envelope and low-level features, plus nuisance regressors.
  - Output: maps of the content part vs the residual part.
- **Figure:** a Sintel strip (CC-BY, so real frames can be shown). Annotated Fear vs lens Fear, with the residual shaded; inset: residual and content brain maps.

**(c) Why it is about emotion and the brain.** It splits experienced emotion into a content-computable part and a context-dependent part. The residual map is the "unexplained-part map" that H3 calls for [V paper_logic §3].

**(d) Rule compliance.** Pass.

**(e) Prior art.**
- Continuous LIRIS-ACCEDE (per-second valence/arousal for 30 films) and the MediaEval 2016–18 content-based prediction tasks [I].
- Emo-FilM's films are taken from the LIRIS database and were previously annotated for valence/arousal [V PMC12019557].
- Koide-Majima 2020, PMID 32798681: 1-s annotations of 80 emotions plus fMRI [V].
- REELMO, PMID 40374710: 60 movies, real-time reports on 20 affective states; fMRI for Jojo Rabbit [V].
- What is new: discrete-emotion arcs from a lens never fit to Emo-FilM, and the residual brain map.

**(f) Risks and controls.**
- Films were heard with sound; the lens is video-only; whether VCE raters heard audio is unknown [U] → audio nuisance regressors.
- Mouse-annotation lag → set on held-out films.
- Agreement is only about 0.39, so the residual is mostly noise unless the residual map reproduces across a 2-vs-2 rater split (4 raters per item) [V].
- Animated films (Sintel, Big Buck Bunny) shift the domain → report per film.

---

## D7. Pleasantness from pairwise choices, routed through emotions and brains (V2V)

**(a) Question.** If pleasantness is defined only by people choosing between two videos, which of the 27 emotions does it weigh? Can a region's content code carry that axis and predict a different group's valence ratings?

**(b) Setup**
- **V2V data [V README:92-112]:**
  - train: 11,038 pairs over 16,125 videos;
  - test: 3,189 pairs over 6,223 videos;
  - listwise: 1,758 lists over 4,322 videos;
  - the three sets of videos are mutually exclusive, and all V2V videos are a subset of VCE.
  - Collection [I, NeurIPS supplement snippet]: 9 judgments per pair; only pairs with 8–9 of 9 agreeing were kept. The question asked which video other workers would find most pleasant.
- **Step 1:** Bradley–Terry model (logistic on f(a) − f(b), no intercept, L2 tuned by inner CV; prop.).
  - f ∈ {lens 27-d, object logits, low-level features, PE-Core}.
  - Headline: 27 BT weights with bootstrap CIs = "how much each emotion's intensity buys pleasantness" (a Kragel Fig. 3B-style bar chart).
  - Checks: pairwise accuracy on the V2V test set and Kendall τ on the listwise set.
- **Step 2 (no refit):** w·f(Cowen video) vs Cowen's "valence" affective dimension [V h20.txt:15].
- **Step 3 (brain route):**
  - Label-blind decoders D_R from HK region to f. With f = the lens output on Cowen videos, no Cowen rating is used.
  - pleasantness_R = w·D_R(brain) on the test split, correlated with Cowen valence.
  - Region map with subject-clustered CIs.
- **Figure:** A = weight bars; B = region map; C = scatter for the best region.

**(c) Why it is about emotion and the brain.** The affect variable uses no emotion vocabulary at all. The chain uses four disjoint sources: VCE raters (lens), V2V choosers (axis), HK brains (route), Cowen raters (criterion).

**(d) Rule compliance.** Pass. Pairwise judgments are external labels.

**(e) Prior art.**
- Mazeika et al., NeurIPS 2022: benchmark and models only.
- No brain use of V2V found [I].
- Valence decoding from brain is common, e.g. Horikawa 2020.
- What is new is the chain.

**(f) Risks and controls.**
- V2V is a subset of VCE, so the lens must exclude V2V test and listwise videos from training. How VCE and V2V splits align is unknown [U].
- Keeping only high-agreement pairs inflates accuracy [I] → headline the weights and the transfer, not accuracy.
- Construct mismatch: "pleasant to others" vs Cowen's valence item.
- Possible MTurk rater overlap between VCE and V2V [U].
- Report results after partialling out arousal.

---

## D8. New brains, no refit: an HK-trained decoder read out in MindCaptioning's 6 subjects, during perception and eyes-closed recall

**(a) Question.** Does an emotion readout learned from 5 brains work unchanged in 6 other people, including when they only imagine the video?

**(b) Setup**
- **Decoder:** HK ROI-mean (450) → 34-d ridge (R0 = 0.294 [V CONTEXT]).
  - Retrain it on HK excluding the 72 MindCaptioning test videos. Their IDs are on figshare, not local [U].
- **MindCaptioning data:**
  - Preprocessed per subject in native space (spaceDefine files).
  - Test perception: 72 videos × 5 repetitions; test imagery: 72 × 5 [V repo data/fmri/README].
  - Raw T1 images on OpenNeuro ds005191.
- **Procedure:**
  - Warp Schaefer + Tian to each subject's native space through the T1.
  - Compute ROI means; z-score within subject and condition. Whether the authors' run-wise z-scoring may be used is a decision the PI still has to make [V synthesis.md:176].
  - Apply the decoder unchanged.
- **Readouts:**
  - per-clip 34-d Pearson vs Cowen ratings;
  - RSA over the 72 videos;
  - per-subject direction consistency [V paper_logic §5];
  - imagery/perception ratio by region.
- **Fallback:** fixed-metric RSA [V synthesis.md:174-175].
- **Figure:** subjects × (perception, imagery) dot plots, plus one imagery trial's decoded 34 bars against the Cowen profile.

**(c) Why it is about the brain.** It tests emotion organization as a shared property of cortex, robust to new brains and to the absence of retinal input.

**(d) Rule compliance.** Nothing is fit on MindCaptioning responses [V synthesis.md:22]. Per the project doc, this is subject replication, not cross-dataset generalization [V paper_logic §8].

**(e) Prior art.**
- Horikawa 2025, Sci Adv, PMID 41191769: perception-trained semantic decoders generalize to recall [V mc.txt:184-211].
- arXiv 2410.00047: imagery decoding on an extended HK dataset with emotion-label prompts [I].
- No zero-refit cross-subject emotion decoding found [I].

**(f) Risks and controls.**
- The cue is one fixed caption out of the 20 [V mc.txt:357-358], and captions contain affect words (D3 counts).
  - Score the cue with the D3 word map and partial out the cue-predicted profile.
  - Compare the preparation period with the imagery period; MindCaptioning found preparation-period semantic decoding was lower, near chance for most subjects [V mc.txt:207-208].
- The real video is re-shown right after imagery, with only 2 s of rest [V mc.txt:363-370] → trim the imagery window or model the next block. Exact HRF overlap [U].
- Anatomical misfit → use coarse parcels.
- Test videos are short (mean 3.94 s) [V mc.txt:322]; n = 72 → low power.

---

## D9. "Same feeling, different content": the pair gallery (H2 in one figure)

**(a) Question.** When two videos feel alike but show different things (snake strike vs car crash), do brain regions treat them alike?

**(b) Setup**
- **Data:** Cowen 2,185 (or the test split).
- **Distances:**
  - Emotion: distance between 34-d log1p_z profiles.
  - Content: two independent descriptors, human-caption SBERT (mean over 20 captions) and PE-Core or V-JEPA2.
  - Declare a canonical metric and report both Euclidean and cosine; this choice is an open item [V CONTEXT].
- **Pair selection:** top N% of |rank(content) − rank(emotion)|, with N = 5/10/20 [V paper_logic §2; CONTEXT].
- **Brain distances:** cross-validated across subjects, per region.
- **Model over all pairs, per region:** brain_dist ~ β_c·content + β_e·emotion.
- **Gallery:** emotion-twin/content-stranger pairs, and the mirror case (content-twin/emotion-stranger).
- **Figure:**
  - 2×5 pair cards: thumbnails, overlaid 34-d profiles, a per-region brain-similarity bar with null band;
  - a map of β_e and β_c.

**(c) Why it is about emotion and the brain.** This is the only place where content and emotion structures disagree, so the brain decides between them.

**(d) Rule compliance.** Selection uses continuous ranks, exactly as the project doc prescribes. No emotion categories.

**(e) Prior art.**
- H2 was not claimed in the project's 37-paper check [V paper_logic §3].
- Nothing contrary turned up in my searches [I].

**(f) Risks and controls.**
- 73.8% of label values are zero [V CONTEXT], so "emotion twins" may just be two near-neutral clips.
  - Report the profile norms of selected pairs.
  - Repeat within the higher-norm half, as a sensitivity check.
- The pair set depends on metric and content model → keep pairs selected under both descriptors.
- Noise from single presentations → subject-cross-validated distances and subject-clustered bootstrap.

---

## D10. Genre from real brains, zero refit (NNDb 10 films/10 genres; Emo-FilM 14 films)

**(a) Question.** Does the 34-d profile decoded with the unchanged HK decoder from a viewer's brain, over a whole film, carry the film's genre-defining emotions?

**(b) Setup**
- **NNDb (Aliko et al. 2020, Sci Data, PMID 33051448):**
  - 86 people, each watching one of 10 full-length films from 10 genres [V nndb.txt:27,76-89].
  - The 10 films: 500 Days of Summer (romance), Citizenfour (documentary), 12 Years a Slave (historical), Back to the Future (sci-fi), Little Miss Sunshine (comedy), The Prestige (thriller), Pulp Fiction (action), Shawshank Redemption (drama), Split (horror), The Usual Suspects (crime).
  - 1.5 T, TR 1 s, aligned to MNI [V nndb.txt:171,183].
  - Planned viewers per film were unequal (18, 18, then 6 × 8) [V nndb.txt:37].
- **Decoding:**
  - Decode the 34-d profile in sliding windows; the window length and HRF shift are fixed a priori (prop.).
  - Average over time to get one profile per subject.
- **Analyses:**
  - (i) Pre-registered directional predictions, e.g. horror → horror/fear/anxiety, comedy → amusement, romance → romance/adoration. Test by permuting film labels across subjects.
  - (ii) Kragel-style PLS-DA, leave-subject-out, with bootstrapped genre×emotion coefficients.
  - (iii) Compare with the lens applied to the films themselves (DVD ASINs are listed in NNDb). For 500 Days of Summer and Little Miss Sunshine, also compare with REELMO's real-time human reports [V reelmo.txt:33,61; REELMO viewings were Italian-dubbed, reelmo.txt:27].
- **Emo-FilM variant:** 30 subjects × 14 films, genre labels from its Table 1 [V].
- **Figure:** Kragel Fig. 3B analog from brains, with lens-derived coefficients for the same films inset.

**(c) Why it is about the brain.** Real brains, an unchanged decoder, and an external label.

**(d) Rule compliance.** Pass.

**(e) Prior art.** No fMRI genre decoding found [I]; MEG genre decoding exists [I].

**(f) Risks and controls.**
- In NNDb each genre is a single film, so genre and film are confounded. The claim must be "a film-level signature readable in genre terms", not genre generalization.
- Large domain shift (silent short clips → long films with sound; 3 T vs 1.5 T) → per-run z-scoring; keep only ROIs that are reliable in HK; exclude auditory ROIs as a sensitivity check.
- Data are not local [U size].

---

## Ranking (novelty × simplicity × robustness, each scored 1–3)

| Rank | Demo | N | S | R | Score | Why |
|---|---|---|---|---|---|---|
| 1 | D9 pair gallery (H2) | 3 | 3 | 2 | 18 | Central to the RQ; one striking figure; no model needed; the metric caveat is manageable |
| 2 | D7 V2V pleasantness | 3 | 2 | 3 | 18 | Four disjoint sources; the 27-weight bar chart is Kragel-simple; 11k pairs |
| 3 | D3 caption-word atlas + ladder | 2 | 3 | 3 | 18 | Gao figure at situation level; 20 captions per video gives stable estimates; the ladder kills the leakage critique |
| 4 | D1 trailer → genre | 2 | 3 | 2 | 12 | The user's favorite format; framed as a bottleneck share; the brain route is in silico (use D10 for real brains) |
| 5 | D8 MindCaptioning zero-refit (perception + imagery) | 3 | 2 | 2 | 12 | Strong "new brains, no picture" message; risks are the cue and low power |
| – | D2 objects | 1 | 3 | 3 | 9 | Do it anyway; it is a prerequisite for D4 |
| – | D6 film arc | 2 | 2 | 2 | 8 | Best visual (CC-BY Sintel), but annotation reliability is about 0.39 and the brain part needs 132 GB |
| – | D4, D5, D10 | – | – | – | 6 each | D4: high novelty but complex. D5: in silico, so a model property only. D10: genre and film confounded; data not local |

**Suggested combination.**
- D2 + D3 (stimulus words/objects) next to D4 (the brain version) as a two-panel Gao-style figure.
- The D1 lens figure next to the D10 brain coefficients for the "Kragel, then real brains" story.

---

## Shared rules for all 10

- Interpret top-weight figures with Haufe patterns or structure coefficients, not raw weights.
- Bootstraps must be subject-clustered [V paper_logic §5].
- The lens is frozen and never sees Cowen, HK, MindCaptioning or Emo-FilM labels.
- Copyrighted frames → CC stand-ins (Kragel's practice). Emo-FilM films are CC, so their real frames can be used.
- Still unverified:
  - whether VCE raters heard audio;
  - overlap between VCE/Cowen clips and trailers. Asanuma et al. 2025 (Sci Rep, PMID 40890212) show trailer clips in Koide-Majima's 550-clip set, not in Cowen [V asanuma.txt:69,79-80,227];
  - the IDs of the 72 MindCaptioning test videos;
  - LMTD raw-video availability.

---

## Source files (full paths)

- Kragel text: /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/kragel.txt
- Gao text: /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/gao.txt
- MindCaptioning text: /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/mc.txt
- NNDb text: /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/nndb.txt
- REELMO text: /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/reelmo.txt
- Asanuma text: /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/asanuma.txt
- HK 2020 text: /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/h20.txt
- Earlier panel synthesis: /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/synthesis.md
- VCE/V2V README: /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/clones/emodiversity/README.md
- Human captions: /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/clones/MindCaptioning/data/caption/caption_ck20.csv
- MindCaptioning fMRI data README: /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/clones/MindCaptioning/data/fmri/README.md
- My caption-count script: /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v2_demos/capstats.py
- Emo-FilM item list: /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v2_datasets/ds004872/derivatives/Annot_Sintel_stim.json
- Emo-FilM concatenated annotations: /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v2_datasets/C_Annot_FILMS_stim.tsv.gz
- Emo-FilM film licenses: /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v2_datasets/dl_emofilm/FilmInfo.txt
- LMTD database: /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v2_datasets/lmtd/lmtd9/data/database.db
- Trailers12k file list: /tmp/claude-0/-home-user/c293907b-0ab4-53eb-a274-20cf029c1cf8/scratchpad/v2_datasets/richardtml_DIViTA/files.py
- Project files: /home/user/EmoBrain/docs/paper_logic_merged.md, /home/user/EmoBrain/CONTEXT_EMOBRAIN.md, /home/user/EmoBrain/project/README.md, /home/user/EmoBrain/project/shared/data/horikawa_split.csv
- Emo-FilM full text: PMC12019557 (PMID 40268934, DOI 10.1038/s41597-025-04803-5)
- Other PMIDs, according to PubMed:
  - Koide-Majima 2020: 32798681, DOI 10.1016/j.neuroimage.2020.117258
  - Ratan Murty 2021: 34545079, DOI 10.1038/s41467-021-25409-6
  - Jang & Kragel 2025: 40086868, DOI 10.1523/JNEUROSCI.1436-24.2025
  - Horikawa 2020: 32353765, DOI 10.1016/j.isci.2020.101060
  - Horikawa 2025: 41191769, DOI 10.1126/sciadv.adw1464
  - REELMO: 40374710, DOI 10.1038/s41597-025-05159-6
  - NNDb: 33051448, DOI 10.1038/s41597-020-00680-2
  - Asanuma 2025: 40890212, DOI 10.1038/s41598-025-14961-6
- Search-snippet-only [I] sources:
  - https://proceedings.nips.cc/paper_files/paper/2022/file/75ff01252ab45ce278cb060effce4ca1-Supplemental-Datasets_and_Benchmarks.pdf
  - https://liris.cnrs.fr/Documents/Liris-7059.pdf
  - https://arxiv.org/abs/2410.19760
  - https://arxiv.org/abs/2410.00047
  - https://arxiv.org/html/2605.16739v1
  - https://typeset.io/pdf/movie-genre-classification-by-exploiting-meg-brain-signals-2j9q0zjecl.pdf
