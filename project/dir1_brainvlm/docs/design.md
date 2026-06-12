# Direction 1. BrainVLM — Design

EmoBrain Direction 1 의 구체적 설계. ACTION_PLAN.md 의 Direction 1 (Action 1.1 ~ 1.3) 의 ground-level 보강. 작업 시작 전 확정 문서.

## 0. Hypothesis

> Qwen3-VL backbone 위에 Horikawa fMRI 를 token 으로 주입하고 LoRA fine-tune 하면, frozen BFM (Phase 1 의 best, BJ resting Pearson r 0.330 / Cat34_multilabel 0.669) 대비 V/A regression Pearson r 과 Cat34 multilabel macro AUROC 가 유의미하게 향상한다.

**Null**. ROI baseline (Phase 1 의 V_reg r 0.396, A_reg r 0.233, Cat34_multilabel 0.699) 을 넘지 못함 → "frozen VLM 의 vision tower 가 fMRI modality 와 너무 다른 modality gap 이라 active VLM 으로도 못 잡음" 의 negative result.

## 1. 두 Path 의 framing

Direction 1 은 BrainVLM 의 가능 architecture 두 가지를 시도한다.

| Path | Encoder | LLM | Bridge | 자원 부담 |
|------|---------|-----|--------|------------|
| **A (main)**. VLM 기반 BrainVLM | Qwen3-VL 의 image encoder (frozen, natural image pretrained) | Qwen3-VL 의 LLM body (LoRA) | Linear projection (LLaVA-style) 또는 Q-Former (BLIP-2-style) | A100 80GB 1 장, LoRA 만 학습 |
| **B (ablation test)**. fMRI-LM 기반 BrainLM | Brain-JEPA-like ViT tokenizer (UKB-style brain pretrained) | GPT-2 / Qwen3-0.6B 가벼운 LLM | Vector quantizer + projection + SigLIP + GRL adversarial | encoder 부터 학습 또는 fMRI-LM checkpoint 활용 |

**우리 결정**. Path A 를 main pilot. Path B 의 핵심 트릭 (synthetic descriptor corpus, SigLIP, domain-adversarial regularizer) 만 Path A 에 차용해서 hybrid 시도.

VLM 의 일반 architecture (image encoder = main 표상, LLM = integration / output) 를 Path A 가 그대로 따른다. fMRI 가 새 modality 라 image encoder 부분에 적응이 필요하지만 (MedBLIP 의 3D → 2D slice trick), 전체 paradigm 은 표준 VLM.

## 2. Path A. 데이터 흐름 (shape)

| Source | Shape | 위치 |
|--------|-------|------|
| Horikawa fMRI raw volume | (5 subj, 2185 stim, T variable, 96, 96, 96, 1) | (이전 추출) |
| Schaefer-400 + Tian-50 ROI time series | (5 subj, 2185 stim, T variable, 450) | `project/shared/data/` 또는 추출 필요 |
| 2D ROI map (Schaefer grid layout) | (5 subj, 2185 stim, H_roi, W_roi) | 변환 후 |
| Qwen-VL caption (자극의 video description) | (2185, ) string + (2185, 768) embedding | `project/shared/data/stimulus_features/` |
| Stim-fold split | `horikawa_5fold.csv` | `project/shared/data/` |

## 3. Path A. fMRI patchify 방법

fMRI 를 Qwen3-VL 의 image encoder (ViT, 224×224 입력 가정) 가 받을 수 있는 형식으로 변환.

### 후보 3 가지 (Action 1.1 의 ablation)

| Layout | 변환 방법 | 장점 | 단점 |
|--------|-----------|------|------|
| **L1. Schaefer 2D grid** | 450 ROI 의 BOLD 값을 25×18 또는 23×20 grid 로 배열, time 축 mean | 단순, fast, Phase 1 의 time mean baseline 과 직접 비교 가능 | ROI 의 spatial neighbor 관계 손실 |
| **L2. Cortical surface flatmap** | 450 ROI 를 cortical surface flatmap 으로 project, ROI 인접성 보존 | Brain anatomy 와 일치 | 변환 코드 추가 (PyCortex / freesurfer 활용) |
| **L3. ROI × time matrix** | (450, T) matrix 를 image 로 (T 축 padding/truncate to 16) | Time dynamics 보존 | image encoder 가 일반 image 가정과 다름 |

**Pilot 결정**. L1 (Schaefer 2D grid) 먼저. 가장 간단하고 정합성 검증 쉬움. L2, L3 는 ablation.

### 2D 변환 후 처리

- Resize to 224×224 (Qwen3-VL ViT 의 input size).
- Per-ROI z-score normalization (Phase 1 의 robust scaling 과 동일).
- 3 channel 로 broadcast (single-channel 2D → 3-channel image-like).

## 4. Path A. Architecture

```
fMRI volume → ROI extraction → 2D grid (224×224×3)
              ↓
        [frozen] Qwen3-VL image encoder (ViT-L/14 or backbone equiv)
              ↓ (B, N_patch, D_vis)
        [trainable] Linear projection or Q-Former (D_vis → D_llm)
              ↓ (B, N_patch, D_llm)
        Concat with text prompt embedding
              ↓
        [LoRA] Qwen3-VL LLM body
              ↓
        Output. 자연어 + V/A score (numeric head) + Cat34 distribution (numeric head)
```

**학습 parameter**.
- LoRA on LLM body (rank 8 ~ 16, alpha 16 ~ 32). 약 5 ~ 30M params.
- Linear projection 또는 Q-Former. Linear 면 ~0.5M, Q-Former 면 ~30M (BLIP-2 표준).
- V/A regression head (small MLP, ~0.1M).
- Cat34 distribution head (small MLP, ~0.3M).

**Frozen 부분**.
- Image encoder (vision tower) 전체.
- LLM 의 base weight.

## 5. Path A. Multi-task prompt + loss

### Prompt template

```
<image: fMRI ROI map>
<text>
You are an expert in affective neuroscience. Based on the fMRI activity
pattern, predict the emotional response.
Question: What is the valence, arousal, and emotion distribution?
</text>
<output>
Valence: <V_score>
Arousal: <A_score>
Cat34: <distribution_token>
Caption: <free-form description>
</output>
```

**Output 형식**.
- V/A score: 자연어 ("Valence: 6.5") 또는 special token ([V=6.5]). pilot 은 자연어.
- Cat34 distribution: 별도 numeric head 의 직접 출력 (34-dim softmax). LLM 의 자연어 generation 과는 별도.
- Caption: free-form 자연어.

### Loss

$$
\mathcal{L} = \mathcal{L}_{\text{CE caption}} + \lambda_1 \mathcal{L}_{\text{MSE V/A}} + \lambda_2 \mathcal{L}_{\text{KL Cat34}}
$$

- $\lambda_1 = 1.0$, $\lambda_2 = 0.5$ (pilot 초기값, ablation 가능).
- CE caption. LLM 의 standard cross-entropy on caption tokens.
- MSE V/A. V, A 각각 standardize 후 (y - $\mu$) / $\sigma$, scalar regression head 에서 MSE.
- KL Cat34. log_softmax(head_logit) vs target distribution (sum 1), KLDivLoss(reduction='batchmean').

### fMRI-LM 의 insight 차용 (Path A 안에서)

| fMRI-LM 의 트릭 | Path A 에 어떻게 적용 | Pilot vs Ablation |
|----------------|------------------------|---------------------|
| **Synthetic descriptor corpus** | Horikawa 자극의 V/A + Cat34 distribution + Qwen-VL caption 을 합성 instruction data 로. "이 fMRI 의 valence=6.5, arousal=4.2, dominant emotion 은 amusement, video 는 a child playing..." 같은 paired training data. | **Pilot 포함**. paired data 없는 fMRI 의 자연 한계 우회. |
| **SigLIP contrastive (bridge stage)** | Stage 1 으로 fMRI ↔ caption embedding 의 SigLIP 사전 정렬. 그 다음 LLM 에 주입. | **Ablation**. pilot 은 simple linear projection. SigLIP 추가는 후속. |
| **Domain-adversarial (GRL)** | Brain projection 과 text embedding 이 modality discriminator 로 구분 불가능하게 추가 loss. | **Ablation**. pilot 결과 보고 결정. |
| **3-objective F2F+F2T+T2T** | F2F (fMRI next-step) 는 fMRI-LM 의 brain-specific 학습. Path A 는 LLM 의 language 능력 유지가 main 이라 T2T 만 차용 (random text LM, catastrophic forgetting 방지). | **Pilot 포함** (T2T 만, F2F 는 제외). |

## 6. Path A. Training protocol

| 항목 | 값 |
|------|-----|
| Split | 5-fold stim-stratified (`horikawa_5fold.csv`) |
| Pilot | fold 1 만, 5 subj pooled, 1 seed |
| Optimizer | AdamW, lr 1e-4 (warmup 100 step, cosine to 1e-5) |
| Batch | 8 stim (memory-limited by Qwen3-VL on A100 80GB) |
| Epoch | 5 (pilot), 10 ~ 20 (final) |
| Seed | 0 |
| LoRA | rank 16, alpha 32, dropout 0.05, on LLM body의 q_proj/k_proj/v_proj/o_proj |
| HW | A100 80GB 1 장, NERSC m4641 gpu queue |

## 7. Path A. Evaluation

### 평가 task

- V/A regression (Pearson r, MAE)
- Cat34 multilabel (macro AUROC, macro F1)
- Cat34 soft distribution (mean Pearson r, top1 accuracy)
- Free-form caption emotion accuracy (SEED-style multi-component: CLIP score + Cap-Sim + EffNet)

### 비교 baseline

| Reference | Source |
|-----------|--------|
| Phase 1 ROI mean + Ridge | `project/shared/results/background/phase1/` |
| Phase 1 BJ resting frozen | 동일 |
| Phase 1 Qwen-VL caption embedding probe | 동일 |
| Phase 1 V-JEPA2 pretrained probe | 동일 |

## 8. Path A. Gate (Direction 1)

- V/A Pearson r 가 Phase 1 ROI baseline (V 0.40, A 0.23) **+0.03 이상** 이면 main path 확정. paired bootstrap p < 0.05 도 함께.
- 낮으면. (a) Patchify layout 변경 (L1 → L2 또는 L3) (b) LoRA target 확장 (vision tower 도 부분 학습) (c) Path B 보조 trick (SigLIP 추가, GRL) ablation.

## 9. Path B. fMRI-LM ablation test (보조 시도)

Path A 의 pilot 학습 후, 동일 fold 위에서 fMRI-LM 의 pretrained checkpoint 가 사용 가능하면 ablation 으로 시도.

- Brain-JEPA-like tokenizer + Qwen3-0.6B 의 가벼운 LLM + LoRA.
- 동일 prompt template + multi-task head.
- 같은 emotion task 평가 → Path A 와 직접 비교.

**Hypothesis**. Path B 가 brain-specific encoder 라 modality gap 적어서 V/A 가 더 잘 잡힐 수도 있음. 단, fMRI-LM checkpoint 의 우리 환경 호환성 + Horikawa 의 짧은 T 분포 (median 5 vs fMRI-LM 의 T=160) 호환성이 critical.

## 10. 코드 구조

```
project/dir1_brainvlm/
├── code/
│   ├── README.md
│   ├── data/
│   │   ├── dataset.py             (BrainVQADataset, fMRI ROI + caption + V/A + Cat34 distribution)
│   │   └── patchify.py            (Schaefer 2D grid / surface flatmap / ROI×time matrix)
│   ├── model/
│   │   ├── brainvlm_path_a.py     (Path A. Qwen3-VL + projection + LoRA)
│   │   └── brainvlm_path_b.py     (Path B. fMRI-LM tokenizer + LLM)
│   ├── loss/
│   │   └── multitask.py           (CE + MSE + KL combination)
│   ├── train/
│   │   └── train_pilot.py         (Path A pilot entry)
│   ├── eval/
│   │   └── eval_emotion.py        (V/A + Cat34 + SEED-style caption metric)
│   ├── analysis/
│   │   └── token_distribution.py  (ABCD pretrained vs Horikawa token KL divergence)
│   └── scripts/
│       ├── train_pilot_path_a.sh  (SLURM)
│       └── eval_pilot.sh
├── docs/
│   └── design.md                  (본 문서)
├── data/, output/, results/        (per-direction)
```

## 11. Day-by-day milestone

| Day | Goal | Deliverable |
|-----|------|-------------|
| 0 (now) | Design + scaffolding | design.md + 빈 module + smoke test ready |
| 1 | Dataset + patchify (L1 Schaefer grid) + smoke test | (10 stim) input → projection → LLM forward → loss decreasing |
| 2 | Fold 1 pilot 학습 (Path A, 5 epoch) | LoRA weight + intermediate metrics |
| 3 | Evaluation + Phase 1 baseline 비교 + caption sample 확인 | `pilot_metrics.csv` + figure |
| 4 | (조건부) Path B ablation 시도, 또는 Path A 의 prompt / LoRA target ablation | 추가 결과 |

## 12. Risk + Mitigation

| Risk | Mitigation |
|------|------------|
| Qwen3-VL image encoder 의 modality gap (natural image 와 fMRI 가 너무 다름) | Patchify layout 3 종 ablation. 또는 vision tower 도 일부 학습 가능하게. |
| LoRA fine-tune 후 catastrophic forgetting (LLM 의 language 능력 손실) | T2T objective 추가 (random text LM batch 섞기). fMRI-LM 의 트릭. |
| Caption generation 품질 낮음 (SEED-style 평가에서) | Phase 1 의 Qwen-VL caption 을 ground-truth 로 distillation. 또는 LoRA rank 증가. |
| GPU memory 초과 (Qwen3-VL 큰 모델) | gradient checkpointing + batch 4 로 축소. 또는 Qwen3-VL-S 같은 가벼운 모델 활용. |
| Paired data (fMRI ↔ emotion text) 부족 | Synthetic descriptor corpus (V/A + Cat34 → template + DeepSeek/GPT rewrite). fMRI-LM 의 트릭. |

## 13. Reference (이 design 의 근거)

- BLIP-2 (Li 2023, ICML). Frozen ViT + frozen LLM bridge by Q-Former.
- LLaVA (Liu 2023, NeurIPS). Linear projection + instruction tuning.
- MedBLIP (Chen 2023). 3D MRI → 2D ViT patch trick + MedQFormer + LoRA.
- USC Brain MRI VLM (Dhinagar 2025). Demographics token + contrastive joint.
- fMRI-LM (Wei 2026, arXiv 2511.21760). Synthetic corpus + SigLIP + GRL + 3-objective tuning + 3-stage pipeline.
- SEED (Park 2026, ICLR). Multi-component caption evaluation.
- Phase 1 audit (`docs/reports/phase1_audit_20260604/`). Frozen BFM 한계의 motivation.
