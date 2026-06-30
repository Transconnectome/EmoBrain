# EmoBrain Architecture Design

작성 2026-06-29. Single project framework novelty path 의 architectural spec. spine 결정 의 source 는 `project_decisions.md` 의 2026-06-29 entry, narrative 는 `Paper/framework_EN.md` + `framework_KR.md`.

본 문서 = 5 novelty (NV0-NV4) 의 architectural component, modular brain encoder spec, fusion strategy, 4 stage curriculum, evaluation framework, token budget, open implementation question 의 full spec.

---

## 1. Spine question (neuroscientific)

> Naturalistic video 가 일으키는 fine-grained emotion 의 분포 표상이, 단일 humanbrain 의 BOLD 신호 안에 multi-modal context (video + caption) 와 함께 decode 가능 한가? 그 decode 의 가능 여부 와 한계 가 emotion 표상의 *populational* vs *idiosyncratic* component 의 어떤 부분 에 attributable 한가?

이 질문은 EmoMind (Mohammed et al. 2026) 의 *per-subject* endpoint 와 EmoBrain 의 *5-subject pooled, multi-modal context-bridged* endpoint 의 spectrum 위에 위치. *fine-grained* = 34 categorical emotion (Cowen) 의 distribution. *brain activity* = Horikawa naturalistic video fMRI (5 subj × 2185 stim). *multi-modal context* = video clip + MindCaptioning human caption.

기존 단일 modality 접근 (frozen BFM, BrainVLM token-output, vanilla ridge) 가 baseline 못 넘은 결과 가 본 spine 의 motivation. 자세 한 evidence 는 `docs/reports/d1_brainvlm_va_negative_result_20260628.md` 와 `docs/reports/phase1_audit_20260604/`.

---

## 2. Architecture diagram

```
================================================================================
                              EmoBrain v6 Architecture
================================================================================

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                              MODALITY INPUT                              │
  └─────────────────────────────────────────────────────────────────────────┘

   fMRI BOLD                Video clip               Caption text
   (5 subj × 2185 stim)     (silent, 8 sec)         (MindCaptioning human
   shape (T, ROI)            T=8 frames@4Hz          + 우리 generated, 1-2 sent)
        │                          │                          │
        ▼                          ▼                          ▼
  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐
  │ Brain encoder│         │Vision encoder│         │Caption loader│
  │  (modular)   │         │  (selectable)│         │  (NV2 dual)  │
  │              │         │              │         │              │
  │ raw ROI      │         │ CLIP         │         │ MindCap human│
  │ Ridge embed  │         │ V-JEPA2      │         │ Our generated│
  │ BFM (6 변종) │         │ VideoMAE     │         │              │
  │ VLM hidden   │         │              │         │              │
  └──────┬───────┘         └──────┬───────┘         └──────┬───────┘
         │ brain token            │ video token            │ text token
         │ (Nb tokens)            │ (Nv tokens)            │ (Nc tokens)
         ▼                        ▼                        ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                         ADAPTER (NV0 + NV1 + NV2)                        │
  │                                                                          │
  │   brain → LLM token shape         video → LLM token shape                │
  │   text encoder (LLM tokenizer)    instruction (task + 34-cat inventory)  │
  │                                                                          │
  │   Token assembler. ordered concat with modality position embedding       │
  │   [<brain_start> Tb ... <brain_end> <video_start> Tv ... <video_end>     │
  │    <text_start>  Tc ... <text_end>  <inst_start>  Ti ... <inst_end>]     │
  └────────────────────────────────────┬─────────────────────────────────────┘
                                       │ unified token sequence (Nb+Nv+Nc+Ni)
                                       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                     FUSION LLM (NV0 + NV1 의 core)                       │
  │                                                                          │
  │     Qwen3-VL backbone (default 4B, ablation 2B/8B)                       │
  │     LoRA on {qkv attention, vision projector, output head}               │
  │     causal mask + modality cross-attention                               │
  │                                                                          │
  │     POYO 형 sequence model 은 ablation slot                              │
  └────────────────────────────────────┬─────────────────────────────────────┘
                                       │ fused hidden state (D=embed dim)
                                       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                       OUTPUT HEAD (NV4 curriculum)                       │
  │                                                                          │
  │     34-class linear (Stage 1-3 의 top-k CE)                              │
  │     34-D softmax (Stage 4 의 full distribution KL)                       │
  │     Class weight (Cowen top-1 frequency inverse)                         │
  │                                                                          │
  │     Optional auxiliary. hidden → ROI mean reconstruction (NV3 anchor)    │
  └─────────────────────────────────────────────────────────────────────────┘
```

Token order = brain → video → text → instruction. ablation slot 의 변경 가능. modality 별 position embedding 의 분리 학습.

---

## 3. 5 Novelty 의 architecture component 매핑

| Novelty | Component | 구체 위치 |
|---------|-----------|-----------|
| NV0. LLM-based brain emotion decoder | Fusion LLM + Output head 의 통합 | `project/code/fusion/llm_wrapper.py`, `project/code/training/trainer.py` |
| NV1. 3-modality LLM fusion | Adapter + Token assembler | `project/code/adapters/{brain_to_llm,video_to_llm}.py`, `project/code/fusion/token_assembler.py` |
| NV2. MindCaptioning bridge | Caption loader 의 dual source | `project/code/caption_loader/{mindcaptioning,generated}.py` |
| NV3. Modular brain encoder | Brain encoder 의 4 modular | `project/code/brain_encoder/{raw_roi,ridge_embedding,bfm,vlm}.py` |
| NV4. 34-distribution curriculum | Output head + Trainer 의 4 stage | `project/code/fusion/dist_head.py`, `project/code/training/trainer.py` |

NV0 는 spine 의 *framing* 이라 하나 의 component 가 아닌 *system 통합* 의 결과. 다른 4 NV 가 NV0 의 구성 요소.

---

## 4. Modular brain encoder spec (NV3)

같은 fusion stack 이 4 변종 모두 받음. 출력 shape 통일 (sequence of brain token, dimension 일관). 각 encoder 의 token sequence length Nb 가 다름 → token assembler 의 modality position embedding 이 정렬.

### 4.1 raw ROI

- **Input**. (T_brain, N_ROI) tensor. T_brain = Horikawa 자극별 BOLD length (median 5 TR), N_ROI = Schaefer-400 + Tian-50 = 450.
- **Token**. 각 TR 을 1 token 으로. linear projection (450 → D_token). Nb ≈ T_brain.
- **장점**. 가장 minimal, interpretation 쉬움.
- **단점**. ROI 시간적 정보 외 의 fine-grained pattern 손실.

### 4.2 Ridge embedding

- **Input**. Phase 1 의 ROI mean + Ridge 의 *prediction latent* (예측 직전 의 D=128 latent vector). emotion task 별 separate Ridge.
- **Token**. 각 task 의 latent 를 1 token 으로 concat. Nb = N_task (현재 4).
- **장점**. Phase 1 의 strong baseline 의 inductive bias 활용. 빠름.
- **단점**. Ridge 의 linear 가정 의 한계. task-bound.

### 4.3 BFM (Brain-JEPA / NeuroSTORM / SwiFT)

- **Input**. Phase 1 의 frozen BFM embedding. shape (T_brain, D_bfm).
- **Token**. BFM 의 token 을 그대로 또는 light linear projection (D_bfm → D_token). Nb = T_brain.
- **장점**. Pretrained representation 의 transfer.
- **단점**. Phase 1 결과 단독 으로는 baseline 못 넘음. multi-modal context 가 lift 의 source 가 되는지가 검증 대상.
- **변종**. BJ resting / BJ scratch / NS / SwiFT NewE96 / SwiFT 변종 6 종 의 selectable.

### 4.4 VLM-derived brain token

- **Input**. D1 BrainVLM 의 fine-tuned hidden state (V/A 또는 Cat34 task 의 LoRA-tuned backbone 의 brain patch 위치 의 last layer hidden).
- **Token**. hidden 의 token sequence 그대로. Nb = N_brain_patch (Qwen3-VL 의 patchify config 의존).
- **장점**. Token output 의 형식 한계 와 무관 한 hidden representation 만 활용.
- **단점**. D1 의 fine-tune 자체 가 한계 (역시 multi-modal context 가 lift 필요).

### 4.5 Encoder ablation grid

S11 evaluation 에서 4 encoder × 3 vision encoder × 2 caption source = 24 condition. sparse, *full multi-modal × encoder 4* + *encoder 1 best × vision 3* + *encoder 1 best × caption 2* 의 marginal sweep 만 학습.

---

## 5. Vision encoder choices

| Encoder | Output shape | 특징 |
|---------|--------------|------|
| CLIP ViT-L/14 | (Nv=N_frame, D=768) | semantic-rich, NSD 의 정착 baseline |
| V-JEPA2 ViT-L | (Nv=N_frame × N_patch_spatial, D=1024) | TRIBE (Algonauts 2025 1 위) 의 backbone. temporal dynamics 강. |
| VideoMAE-L | (Nv=N_frame × N_patch_spatial, D=1024) | self-supervised video pretrain. cheaper. |

Default = V-JEPA2 (TRIBE evidence). ablation = CLIP + VideoMAE.

Adapter `video_to_llm.py` 가 모두 동일 token shape (D=D_LLM) 으로 변환.

---

## 6. Caption sources (NV2)

### 6.1 MindCaptioning human caption (main)

- **Source**. Horikawa & Kamitani Mind Captioning paper (Science Advances 2025) 의 publicly released dataset. 2185 stim 의 human-written neutral caption.
- **형식**. 1-2 sentence English description. "neutral" = emotion label 직접 mention 없음.
- **역할**. brain-context bridge. brain 신호 와 emotion label 사이 의 semantic anchor. NV2 의 main argument.

### 6.2 우리 model-generated caption (비교)

- **Source**. Qwen-VL (또는 Qwen3-VL) 의 video clip → caption generation. 우리 batch 로 2185 stim 모두 cover.
- **형식**. 1-2 sentence English description. neutral filtering (emotion label mention 제거).
- **역할**. NV2 의 *human vs generated caption 의 효과 비교*. publishability 의 angle. publishable framing 의 한 contribution.

### 6.3 Caption generation pipeline (우리 generated)

- **Step 1**. Horikawa 자극 (mp4) 의 frame sample (8 frame uniform).
- **Step 2**. Qwen-VL prompt = "Describe this short video clip in 1-2 neutral sentences. Do not mention any emotion words.".
- **Step 3**. Output 의 emotion word filter (Cowen 34 + V/A 단어 list 의 substring match 제거 또는 rephrase).
- **Step 4**. Length 통일 (max 40 token).

`project/code/caption_loader/generate_captions.py` + `project/sample_scripts/generate_captions_qwen_vl.sh`.

---

## 7. Fusion. Prompt schema + token order + LoRA target

### 7.1 Prompt schema

Stage 별 task instruction 의 미세 차이 있지만 base template 통일.

```
<system>
You are an emotion analysis model trained on naturalistic video fMRI.
Use the brain signal, video, and caption together to identify the emotion distribution.
</system>

<brain_start>
{brain_tokens}
<brain_end>

<video_start>
{video_tokens}
<video_end>

<caption_start>
{caption_text}
<caption_end>

<inst_start>
Output the top-{k} emotion category(ies) from the 34-category inventory:
[admiration, adoration, ..., sadness, ..., triumph].
Format. JSON array of strings, sorted by likelihood.
<inst_end>

<output>
```

Stage 4 의 instruction 은 "Output the 34-dim probability distribution as JSON object" 으로 교체. Output 의 parse 는 grammar-constrained decoding (lm-format-enforcer) 또는 dedicated softmax head 의 forward (training 시 softmax head 만 사용, inference 시 token decode 도 grammar 강제).

### 7.2 Token order

`brain → video → caption → instruction` 이 default. Ablation 으로 `caption → brain → video → instruction` 도 시도 (context first 의 효과).

### 7.3 Modality position embedding

각 modality 의 start/end marker token (`<brain_start>` 등) 의 embedding 을 fresh learnable. backbone 의 BOS/EOS 와 분리.

### 7.4 LoRA target

| Layer | LoRA rank | Justification |
|-------|-----------|---------------|
| Q, K, V projection (모든 layer) | r=16 | standard |
| O (output projection, 모든 layer) | r=16 | EmoMind 의 LoRA target 참조 |
| Vision projector (Qwen3-VL 의 vision-to-text projection) | r=32 | brain modality 의 새 token type → vision projector 의 adaptation 더 필요 |
| Output head | full fine-tune | 34-D output 의 새 task |

LoRA target list 는 `project/config/lora_target.yaml`.

### 7.5 ICL or single-trial decision

D1 의 v1/v2 = ICL 3-round (cross-subject ref). 본 spine 에서는 **single-trial default**. ICL 은 ablation.

근거. ICL 의 *학습 시 의 SNR 약화* 가 D1 의 한 cause 후보 (negative result report §3.2 (b)). 새 spine 에서 brain + video + caption 의 3-modality 가 *trial-level context* 를 이미 충분히 제공. ICL 의 cross-subject reference 는 *transfer evaluation* (LOSO) 에서만 사용.

---

## 8. 4 stage curriculum (NV4)

| Stage | Output | Loss | Metric | Scheduler | Epoch (estimate) |
|-------|--------|------|--------|-----------|------------------|
| Stage 1 | top-1 categorical (34-class hard) | Cross-entropy + class weight | top-1 accuracy, balanced accuracy | cosine, warmup 5% | 20-30 |
| Stage 2 | top-2 multi-label | Multi-label BCE 또는 sigmoid + top-2 weighted CE | top-2 set match, Jaccard | cosine, warmup 3% | 15-20 |
| Stage 3 | top-k k-hot | Sparse multi-label CE with class weight | top-k F1, AUROC per class | cosine, warmup 3% | 15-20 |
| Stage 4 | full 34D soft distribution | KL(target || pred) + class weight | KL, mean Pearson r (per class), JS divergence | cosine, warmup 2% | 30-50 |

### 8.1 Stage 별 target 정의

- **top-1 target**. 자극 별 rater majority vote (highest frequency).
- **top-2 target**. 자극 별 highest 2 frequency category (tie 의 경우 union).
- **top-k target**. 자극 별 active (threshold 0.10 = 10% rater) category set.
- **full 34D target**. 자극 별 normalized rater frequency distribution (smoothing 옵션 = Dirichlet prior, OD-E).

### 8.2 Loss 의 class weighting

Cowen 34 의 frequency imbalance (top-1 frequency 의 max 5%, min < 1%). weight = inverse of marginal frequency, normalized.

### 8.3 Stage 간 transition

- 이전 stage 의 best checkpoint 에서 weight load.
- Output head 의 dimension 변경 안 함 (항상 34 logits, loss 만 변경).
- Adapter / fusion / backbone 의 LoRA 는 누적 학습.

### 8.4 Optional auxiliary loss

`L_total = L_main + λ_aux × L_recon`. L_recon = LLM hidden (brain segment) → ROI mean (Schaefer-400+Tian-50) 의 MSE. λ_aux = 0.1 (S9 smoke 후 결정).

이 auxiliary 가 NV3 의 brain modality 의 *representational anchor*. brain signal 의 정보 가 fusion 안에서 *희석* 되는 것 방지.

---

## 9. Evaluation framework

### 9.1 Baseline ladder

| Baseline | 설명 | 위치 |
|----------|------|------|
| Chance | Label permutation 의 평균 metric | `project/code/evaluation/chance_baseline.py` |
| ROI mean + Ridge | Phase 1 의 best baseline | 재활용 `project/shared/code/probes/run_unified_probe.py` |
| Phase 1 best BFM (BJ resting + Ridge) | Phase 1 의 BFM 의 best frozen probe | 재활용 |
| Video-only | Vision encoder + classifier head (brain 제외) | `project/code/evaluation/video_only.py` |
| Caption-only | LLM (text-only, brain + video 제외) | `project/code/evaluation/caption_only.py` |
| Brain-only (new spine encoder) | NV3 encoder + LLM (video + caption 제외) | trainer 의 modality mask |
| Brain + Video | brain + video, caption 제외 | trainer 의 modality mask |
| Brain + Caption | brain + caption, video 제외 | trainer 의 modality mask |
| Video + Caption | video + caption, brain 제외 | trainer 의 modality mask |
| **Full multi-modal** | brain + video + caption (NV1 main) | trainer 의 default |

### 9.2 Variance partitioning

7 modality combination 의 각 metric 차이 → unique vs shared vs joint variance 의 decomposition. 자극 (stim) level + subject level 2 방향.

N=5 의 subject d.f. 의 statistical power limit 을 method section + limitation 에 명시. claim 은 *trend-level* 로.

### 9.3 Ceiling anchor

- **Inter-rater ceiling**. Cowen 34 rater 의 half-split agreement. 자극 별 distribution 의 noise ceiling.
- **Inter-subject ceiling (brain side)**. 5 subj 의 brain RDM 의 mean cross-subject Spearman r.
- Model performance 의 ceiling 대비 비율 reporting.

### 9.4 Dissociation

- **Decoding accuracy vs RSA correlation**. EmoMind 의 결과 (decode 0.97 vs RSA 0.09) 와 의 비교. dissociation 의 우리 result 의 자체 측정.
- **Visual confound vs emotion-specific**. variance partitioning 의 부산물 + visual feature (CLIP feature) 의 control regression.

### 9.5 LOSO

5-fold by subject. 4 subj train → 1 subj zero-shot. ICL ref 를 *cross-subject* 로만 (transfer evaluation 의 ICL slot).

### 9.6 Cross-cohort

Horikawa → Emo-FilM. 자체 학습 후 zero-shot transfer + per-cohort fine-tune 의 두 condition.

Emo-FilM 의 다운로드 + preprocessing 의 prerequisite. S11 의 후반.

---

## 10. Token budget + attention cost + training time

### 10.1 Estimated prompt length (per trial)

| Component | Token count (estimate) |
|-----------|------------------------|
| System prompt | 80 |
| Brain start/end + brain tokens | 5 + Nb |
| Video start/end + video tokens | 5 + Nv |
| Caption start/end + caption text | 5 + Nc |
| Instruction start/end + instruction | 5 + Ni |
| Output | 10-50 |

Nb (raw ROI) ≈ 5-10 (T_brain median). Nb (BFM) ≈ 5-10. Nv (V-JEPA2, 8 frame × 16 patch) ≈ 128. Nc ≈ 40. Ni ≈ 200 (34-cat inventory).

**Per-trial total ≈ 80 + 10 + 130 + 50 + 210 + 30 ≈ 510 token**. ICL 사용 시 × ICL_rounds.

### 10.2 Attention cost

Qwen3-VL 4B 의 attention. seq 510 + batch 4 + 32 layer × 32 head × 128 head_dim. flash-attn 2 가정 시 step time ≈ 0.4 sec (A100). gradient checkpoint 권장 (memory 50%).

### 10.3 Training time estimate

| Stage | Trial 수 | Epoch | Batch | Step | Wall (A100, 1 GPU) |
|-------|----------|-------|-------|------|---------------------|
| Stage 1 | 10925 | 25 | 4 | 68281 | ~7.6 hour |
| Stage 2 | 10925 | 17 | 4 | 46431 | ~5.2 hour |
| Stage 3 | 10925 | 17 | 4 | 46431 | ~5.2 hour |
| Stage 4 | 10925 | 40 | 4 | 109250 | ~12 hour |

4 stage 의 sequential = ~30 hour per encoder × vision × caption combination. encoder 4 변종 × vision 1 default × caption 1 default = ~120 hour. ablation 추가 시 GPU month scale.

S11 의 ablation 은 *sparse marginal sweep* 으로만 실행.

---

## 11. Open implementation questions

각 question 은 S7-S11 의 specific gate 에서 decision point.

1. **Token assembler 의 modality position embedding 의 sharing 정책**. fresh learnable per modality 가 default. backbone 의 token embedding 의 weight tying 시도 여부.
2. **Brain token 의 dimensionality reduction.** raw ROI 의 450 → D_LLM (예. 3584 for Qwen3-VL 4B) 의 linear projection vs MLP. linear default, MLP 의 effect 측정 필요.
3. **Video frame 의 temporal alignment.** Horikawa 의 8 sec clip 의 frame uniform 8 sample vs HRF-aligned. brain 의 BOLD lag 와 의 alignment 의 effect.
4. **Caption length 의 cutoff.** MindCaptioning 의 length 분포 vs 우리 generated 의 length 분포 가 다름. cutoff 통일 의 effect.
5. **Stage transition 의 weight inheritance.** Stage 1 checkpoint 의 LoRA + adapter 의 100% inherit vs Stage 1 의 backbone + Stage 2 의 new LoRA 의 reset.
6. **Class weighting 의 stage 별 변화.** Stage 1-3 의 hard class weight vs Stage 4 의 KL 의 implicit weighting 의 균형.
7. **Auxiliary L_recon 의 λ 값.** 0.0 / 0.1 / 0.3 의 grid 의 S9 smoke 후 결정.
8. **ICL ablation 의 trigger 조건.** Single-trial default 의 성능 이 baseline 못 넘으면 ICL 시도. 또는 LOSO setting 에서만 ICL 사용.
9. **POYO ablation 의 priority.** S8 main 에 포함 vs supplementary appendix. publishability 의 marginal contribution 평가 필요.
10. **MindCaptioning vs 우리 generated 의 simultaneous use.** 한 trial 에 둘 다 input 으로 줄지 (text token 의 concat), 둘 중 하나만 줄지 (condition switch). 둘 다 = redundancy 증가 + token cost.
11. **Stage 4 의 KL target smoothing.** Dirichlet prior alpha=0.1 vs alpha=0.01 vs none. minority class 의 학습 안정성 vs target sharpness 의 trade-off.
12. **Cross-cohort 의 Emo-FilM 의 rating schema 정합성.** Cowen 34 의 schema 와 의 mapping 가능 여부. mapping 안 되면 cross-cohort 의 *transferable subset* 으로 축소.

각 question 의 decision 은 `project_decisions.md` 의 후속 entry 에 추가.

---

## 12. Cross-references

- Spine narrative. `Paper/framework_EN.md`, `Paper/framework_KR.md`.
- Decision log. `docs/notes/project_decisions.md`.
- Negative result evidence. `docs/reports/d1_brainvlm_va_negative_result_20260628.md`.
- Phase 1 audit. `docs/reports/phase1_audit_20260604/`.
- Action plan. `ACTION_PLAN.md`.
- Compact context. `CONTEXT_EMOBRAIN.md`.
