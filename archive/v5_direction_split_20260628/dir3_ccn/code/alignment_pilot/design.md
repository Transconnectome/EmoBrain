# Direction 2. Multimodal Alignment — Design

EmoBrain Direction 2 의 구체적 설계. ACTION_PLAN.md 의 Direction 2 (Action 2.1 ~ 2.3) 의 ground-level 보강. 작업 시작 전 확정 문서.

## 0. Hypothesis

> Brain encoder + V-JEPA2 video encoder 의 contrastive alignment 학습 시, **brain 이 video baseline 위에 추가하는 emotion-relevant variance 가 paired bootstrap p < 0.05 이고 절대값 +0.05 Pearson r 이상으로 의미있게 존재한다**.

**Null**. p > 0.05 또는 절대값 < 0.05 → "video stim 만으로 emotion 의 universal axis 가 saturate, brain 의 unique contribution 무". negative result 도 publishable.

## 1. 데이터 흐름 (shape)

| Source | Shape | 위치 |
|--------|-------|------|
| **Brain (resting pretrained, frozen)** | (5 subj, 2185 stim, 768) | `project/shared/output/embeddings/brain_jepa_resting_pad-zero/sub-XX.pt` |
| **Brain (scratch random init, frozen)** | (5 subj, 2185 stim, 768) | `project/shared/output/embeddings/brain_jepa_scratch_pad-zero/sub-XX.pt` |
| Video (V-JEPA2 pretrained) | (2185 stim, 1408) | `project/shared/data/stimulus_features/vjepa2_pretrained.npy` |
| Stim-fold split | (2185 stim, fold ∈ {1..5}) | `project/shared/data/horikawa_5fold.csv` |

같은 stim → 같은 video. 5 subj 의 brain 이 모두 같은 video 와 매칭.

Pooled mode 의 sample. 5 subj × 2185 stim = 10925 (brain, video) pair. 같은 video 가 5 번 다른 brain 으로 등장.

### Brain encoder ablation (둘 다 시도)

| Variant | Pretrain | Frozen 여부 | 의미 |
|---------|----------|--------------|------|
| **BJ resting** | UKB / HCP-like resting fMRI pretrained | Frozen | "사전학습된 brain representation 위 alignment 가 emotion 잡는가" |
| **BJ scratch** | None (random init) | Frozen | "random init brain encoder + alignment 만으로 video 와 정렬 가능한가" |

두 variant 의 결과 비교가 Direction 2 의 핵심 ablation. Resting > Scratch 이면 "pretrained brain representation 의 emotion gain 존재", Resting ≈ Scratch 이면 "alignment 단계가 dominant 이고 brain encoder 의 pretrained quality 는 marginal".

Video 는 V-JEPA2 pretrained 만 사용 (scratch variant 는 Phase 1 video probe 에서 사실상 무의미한 결과로 확인되어 ablation 제외).

## 2. Architecture

```
Brain (B, 768)  → ProjBrain  → z_brain (B, 512)
Video (B, 1408) → ProjVideo  → z_video (B, 512)

ProjBrain  = Linear(768 → 1024) → GELU → Dropout(0.1) → Linear(1024 → 512) → LayerNorm(512)
ProjVideo  = Linear(1408 → 1024) → GELU → Dropout(0.1) → Linear(1024 → 512) → LayerNorm(512)
```

학습 parameter ~1.5M. Frozen Brain-JEPA + V-JEPA2 위의 가벼운 head 만.

## 3. Loss (fMRI-LM insight 반영)

이전 design 은 InfoNCE only 였으나 fMRI-LM 의 두 트릭을 추가해 robust 화.

### Pilot 학습 loss

$$
\mathcal{L} = \mathcal{L}_{\text{SigLIP}}(z_{\text{brain}}, z_{\text{video}}) + \lambda_{\text{adv}} \cdot \mathcal{L}_{\text{adv}}(z_{\text{brain}}, z_{\text{video}})
$$

### Sigmoid Loss for Language-Image Pretraining (SigLIP)

CLIP-style InfoNCE 의 softmax 정규화 대신 **pairwise sigmoid**.

$$
\mathcal{L}_{\text{SigLIP}} = -\frac{1}{B^2} \sum_{i,j} \log \frac{1}{1 + \exp(-z_{ij} (t \cdot s_{ij} + b))}
$$

- $s_{ij}$ = cosine similarity of $(z_{\text{brain},i}, z_{\text{video},j})$.
- $z_{ij} = +1$ if $i=j$, $-1$ otherwise.
- $t$ = learnable temperature (initialised log 10).
- $b$ = learnable bias (initialised -10).

**SigLIP 의 장점 (우리 setting 기준)**.
- batch 안 모든 negative pair 를 독립 sigmoid 로 처리 → batch size 의존성 낮음.
- InfoNCE 의 softmax 정규화로 인한 hard negative dominance 회피.
- 작은 batch (NERSC GPU 제약, 256 stim) 에서도 안정.
- fMRI-LM 의 Stage 1 SigLIP 결과 (Brain-JEPA, BrainNetCNN, SwiFT 대비 best/2nd) 가 우리 setting 과 호환.

### Domain-Adversarial Loss (Gradient Reversal)

$z_{\text{brain}}$ 과 $z_{\text{video}}$ 가 modality discriminator 로 구분 불가능하게 만드는 보조 loss.

- 별도 MLP `Discriminator(z → 2)` (modality classifier).
- Discriminator 는 (brain=0, video=1) 분류 학습 + projection head 는 discriminator 가 못 맞히도록 reverse gradient (GRL).
- $\lambda_{\text{adv}} = 0.1$ 시작 (warmup 후 점진적 증가, fMRI-LM 의 schedule 참조).

**효과**. brain embedding 이 video embedding 공간과 modality-agnostic 해짐 → variance partitioning 의 "modality-shared variance" 비율이 명시적으로 커짐 → joint vs video-only 의 차이가 명확.

### Subject-invariant 옵션 (ablation)

같은 stim 의 다른 subject 의 brain 끼리도 positive pair 로 추가 SigLIP. EmoBrain v4 의 universal emotion code 가설 검증.

$$
\mathcal{L}_{\text{subj-inv}} = \mathcal{L}_{\text{SigLIP}}(z_{\text{brain}_a, \text{stim} i}, z_{\text{brain}_b, \text{stim} i})
$$

$a, b$ = different subject pair. $\lambda_{\text{subj}} = 0.3$ (ablation 가능).

## 4. Training protocol

| 항목 | 값 |
|------|-----|
| Split | 5-fold stim-stratified (`horikawa_5fold.csv`) |
| Pilot | fold 1 만, 5 subj pooled, 1 seed, **Brain encoder 2 variant (resting + scratch) 병행** |
| Optimizer | AdamW, weight_decay 1e-4 |
| LR | 1e-4 (warmup 100 step, cosine decay) |
| Batch | 256 stim × 5 subj = 1280 sample |
| Epoch | 40, patience 10 on val SigLIP loss |
| Seed | pilot 0, final 0/1/2 |
| Temperature $t$ | learnable (init log 10) — SigLIP 의 표준 |
| Bias $b$ | learnable (init -10) — SigLIP 의 표준 |
| GRL $\lambda_{\text{adv}}$ | 0.0 (epoch 0-5) → 0.1 (linear warmup), epoch 5+ |
| HW | A100 40GB 충분 (frozen encoder + head only) |

## 5. Evaluation (variance partitioning)

학습 후 z_brain, z_video extract. 다음 3 model 의 emotion task 결과 비교.

| Model | Feature | Probe |
|-------|---------|-------|
| **Brain-only** | z_brain (512-dim) | Ridge / Logistic L2 (Phase 1 과 동일 grid) |
| **Video-only** | z_video (512-dim) | 동일 |
| **Joint** | [z_brain ; z_video] (1024-dim concat) | 동일 |

### Tasks 평가

- V_reg, A_reg → Pearson r, MAE
- Cat34 multilabel (threshold 0.10) → macro AUROC, macro F1
- Cat34 soft distribution → mean Pearson r, top1 accuracy
- (optional) Mixed valence 3-way → balanced accuracy

### Variance partitioning 정의

$$
\Delta_{\text{brain unique}} = \text{metric}_{\text{Joint}} - \text{metric}_{\text{Video-only}}
$$

$$
\Delta_{\text{video unique}} = \text{metric}_{\text{Joint}} - \text{metric}_{\text{Brain-only}}
$$

$$
\Delta_{\text{shared}} = \text{metric}_{\text{Brain-only}} + \text{metric}_{\text{Video-only}} - \text{metric}_{\text{Joint}}
$$

**Paired bootstrap 10K iter** 로 $\Delta_{\text{brain unique}}$ 의 95% CI + p-value.

## 6. Baseline 과의 비교 표

Brain encoder 2 variant 의 결과를 모두 reporting.

| Reference | V_reg r | A_reg r | Cat34_ml AUROC |
|-----------|---------|---------|------------------|
| Phase 1 ROI mean + Ridge | 0.396 | 0.233 | 0.699 |
| Phase 1 BJ resting frozen (no align) | 0.330 | 0.221 | 0.669 |
| Phase 1 BJ scratch frozen (no align) | (Phase 1 table 에서 추출) | | |
| Phase 1 V-JEPA2 pretrained (no align) | (Phase 1 table 에서 추출) | | |
| **본 학습. BJ resting + align. Brain-only** | ? | ? | ? |
| **본 학습. BJ resting + align. Video-only** | ? | ? | ? |
| **본 학습. BJ resting + align. Joint** | ? | ? | ? |
| **본 학습. BJ scratch + align. Brain-only** | ? | ? | ? |
| **본 학습. BJ scratch + align. Video-only** | ? | ? | ? |
| **본 학습. BJ scratch + align. Joint** | ? | ? | ? |

**핵심 KPI**.
1. $\Delta_{\text{brain unique}}$ (resting variant) 가 paired bootstrap p < 0.05 + 절대값 +0.05 이상.
2. Resting vs Scratch 의 비교. resting 이 의미있게 높으면 pretrained 의 emotion-relevant prior 검증.

## 7. Gate (Direction 2)

| 조건 | 결정 |
|------|------|
| $\Delta_{\text{brain unique}}$ p < 0.05 + 절대값 +0.05 이상 | Direction 2 main path 확정 → 5-fold full + 3 seed 확장 |
| p > 0.05 but trend 의미 있음 | Brain encoder 변경 (BJ → ROI → SwiFT NewE96) + GRL $\lambda_{\text{adv}}$ ablation |
| 완전 null | Negative result로 paper. Subject-invariant ablation 추가 시도. |

## 8. 코드 구조

```
project/dir2_multimodal/
├── code/
│   ├── README.md
│   ├── data/
│   │   └── dataset.py             (BrainVideoDataset, stim-paired loader)
│   ├── model/
│   │   ├── projection.py          (ProjBrain, ProjVideo)
│   │   └── discriminator.py       (Modality discriminator for GRL)
│   ├── loss/
│   │   ├── siglip.py              (SigLIP pairwise sigmoid)
│   │   └── grl.py                 (Gradient reversal layer + adversarial loss)
│   ├── train/
│   │   └── train_align.py         (entry point)
│   ├── eval/
│   │   └── eval_emotion.py        (3-way model 의 V/A + Cat34 평가)
│   ├── analysis/
│   │   └── variance_partition.py  (paired bootstrap 10K)
│   ├── scripts/
│   │   ├── train_pilot.sh         (SLURM, A100 40GB, fold 1)
│   │   └── eval_pilot.sh
│   └── legacy_phase2/             (v4 Brain+Video framework reference)
├── docs/
│   └── design.md                  (본 문서)
├── data/, output/, results/        (per-direction)
```

## 9. Smoke test (Day 1 first thing)

- Input. 10 stim brain (10, 768) + video (10, 1408).
- Projection → z_brain, z_video (10, 512).
- SigLIP loss 계산. 초기값 ≈ -log(sigmoid(-10)) ≈ 10 (bias -10 의 영향), 학습 후 감소.
- 1 epoch (100 step) 학습 후 loss decreasing, $t$ 와 $b$ 가 학습되는지 확인.
- z_brain @ z_video.T diagonal sharpening (i = j 가 i ≠ j 보다 큰지).

## 10. Day-by-day milestone

| Day | Goal | Deliverable |
|-----|------|-------------|
| 0 (now) | Design + scaffolding | design.md + 빈 module + smoke test ready |
| 1 | dataset + projection + SigLIP + GRL smoke test | loss decreasing, $t$/$b$ 학습 확인, diagonal sharpening |
| 2 | Fold 1 pilot 학습 2 회 (resting + scratch, 각 40 epoch, SigLIP + GRL) + variance partition | `pilot_metrics.csv` 의 6-way (resting × {B, V, J} + scratch × {B, V, J}) |
| 3 | 표 + visualization (UMAP, similarity matrix) + Phase 1 비교 + Resting vs Scratch 비교 | `figures/` 안의 plot, slide 1 page summary |

## 11. Risk + Mitigation

| Risk | Mitigation |
|------|------------|
| Brain unique variance ≈ 0 | Brain encoder 후보 변경 (BJ → ROI → SwiFT). 또는 GRL weight ablation. |
| Sample 부족 (1750 train stim) overfit | Dropout 0.1+, weight_decay 1e-4, early stop, projection dim 줄임 |
| Subject confound (subject-specific noise 가 contrastive 위) | Subject-invariant loss 추가, 또는 batch 안 subject balanced |
| SigLIP 의 learnable $t$, $b$ 가 발산 | warmup 100 step + grad clip 1.0 + initialise $t = \log 10, b = -10$ (fMRI-LM 표준) |
| GRL 의 weight 가 main loss 를 압도 | warmup ($\lambda_{\text{adv}} = 0$ epoch 0-5 → 0.1 linear) + abalation 0/0.05/0.1/0.2 |

## 12. fMRI-LM insight 의 직접 적용 정리

| fMRI-LM 트릭 | Direction 2 에서의 역할 |
|--------------|-------------------------|
| **SigLIP contrastive** | Pilot 의 main loss. CLIP InfoNCE 대신. |
| **Domain-adversarial (GRL)** | Pilot 의 보조 loss. modality gap 명시적으로 줄임. |
| Synthetic descriptor corpus | (해당 없음. Direction 2 는 brain ↔ video alignment 라 text 합성 불요.) |
| 3-objective F2F+F2T+T2T | (해당 없음. Direction 2 는 LLM 없음.) |
| ROI tokenizer | (해당 없음. Direction 2 는 frozen BFM embedding 위.) |

Direction 2 는 fMRI-LM 의 architecture 전체가 아닌 **loss 함수 2 개 (SigLIP, GRL)** 만 차용. nature 가 다른 task (brain ↔ video pair contrastive) 라서.

## 13. Reference (이 design 의 근거)

- fMRI-LM (Wei 2026, arXiv 2511.21760). SigLIP + GRL + 3-stage pipeline. **Loss 함수의 핵심 출처**.
- SigLIP (Zhai 2023, ICCV). Sigmoid Loss for Language-Image Pretraining.
- TRIBE (Meta FAIR 2025, arXiv 2507.22229). Algonauts 2025 1 위. V-JEPA2 + Llama 통합 framework.
- VIBE (2025). Video-only baseline 비교.
- BraVL (Du 2023, TPAMI). Brain-Visual-Linguistic tri-modal alignment.
- Doerig (2024). High-level visual cortex 의 visual representation 정렬 증거.
- CineBrain (2025). Naturalistic audiovisual narrative dataset.
- Phase 1 audit (`docs/reports/phase1_audit_20260604/`). Frozen BFM 한계의 motivation.
