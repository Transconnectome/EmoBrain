# EmoBrain

**Decoding fine-grained emotion from human brain activity.**

(Repo path. `/pscratch/sd/s/sjmoon/EmoBrain/`.)

---

## Spine

Single LLM-based foundation model that decodes fine-grained emotion (Cowen-Keltner 34-category distribution + V/A continuous) from human brain activity. brain + naturalistic video + human-written caption 의 3 modality 를 한 LLM forward pass 에서 통합 fusion, modular brain encoder 로 backbone 의 fair ablation, 4-stage curriculum 으로 distribution-level output 의 학습.

## 5 Novelties

| ID | Name | One-line statement |
|----|------|--------------------|
| **NV0** | LLM-based brain emotion decoder | Emotion 분야 에서 LLM 을 brain activity 의 fine-grained decoder 로 통합 한 first instrument. |
| **NV1** | 3-modality LLM fusion | brain + video + caption 의 token sequence 가 single LLM forward pass 에서 통합. |
| **NV2** | MindCaptioning bridge | Human-written neutral caption (MindCaptioning, Horikawa) 이 brain-context bridge. 우리 model-generated caption (Qwen-VL) 도 비교 자원 으로 동시 활용. |
| **NV3** | Modular brain encoder | E1 raw ROI (control, no pretrain) / E2 Ridge latent (task-specific) / E3 BFM frozen (fMRI 대규모 pretrain) / E4 VLM hidden (image pretrain + fMRI fine-tune) 의 4 swappable adapter. 같은 fusion stack 이 4 encoder 모두 받음. 공통 patchify frontend 없음, 진짜 변수 는 사전 학습 유무 + fMRI 적응 설계. Encoder 순위 자체 는 spine result 아님, framework modularity 검증. |
| **NV4** | 34D independent emotion regression + practical curriculum | Cowen 34-category 를 서로 경쟁 하지 않는 독립 점수 로 output (bittersweet 처럼 여러 감정 동시 가능). Per-emotion MSE loss (curriculum stage 별 subset), z-score preprocessing 필수. Softmax / sum-to-1 / KL 사용 금지. Curriculum (top-1 → top-2 → top-k → full 34D) 은 stepwise validation tool 로 유지. 실행 = Track A (direct) → Track B (distillation) × curriculum sub-stage 1-4. |

NV0 가 spine 의 framing axis, NV1-NV4 가 NV0 를 구성 하는 architectural component.

## Architecture (concise)

```
INPUT
  fMRI (5 subj × 2185 stim pooled)
      → Brain encoder (modular. raw ROI / Ridge / BFM / VLM)         → brain tokens
  Video (Horikawa silent clip)
      → Vision encoder (CLIP / V-JEPA2 / VideoMAE selectable)        → video tokens
  Caption
      MindCaptioning human-written neutral caption (NV2 main)
      + our Qwen-VL generated caption (비교)
      → text encoder (LLM tokenizer)                                  → text tokens
  Prompt (task-specific instruction + 34-cat label inventory)
      → instruction tokens

FUSION
  [brain | video | text | instruction] tokens
      → Qwen3-VL LLM (LoRA fine-tune)
      또는 POYO 형 sequence model (ablation)
      → fused hidden state

OUTPUT (NV4. 34D independent emotion regression + curriculum)
  34-D linear regression head. NO softmax, NO sum-to-1, NO KL.
  각 감정 은 독립 점수 (bittersweet 처럼 여러 감정 동시 가능).
  학습 전 z-score per emotion (mean 0, std 1) 필수 전처리.

CURRICULUM (per-emotion MSE 원리 유지, subset target)
  1 (top-1)    A = {자극 별 rating 1위 감정}       sanity
  2 (top-2)    A = {상위 2}                        mixed emotion
  3 (top-k)    A = {rating > threshold, 가변 k}    sparse profile
  4 (full 34D) A = {1..34}                         전체 profile

LOSS
  Track A (direct)     L_main = sum_{k ∈ A} (pred_k - target_k)^2      (subset MSE)
  Track B (distill)    L_total = L_main + λ × L_distill                 (teacher 34D MSE 재현)
  Optional             brain-reconstruction auxiliary (LLM hidden → ROI mean MSE)
  금지                 Softmax, sum-to-1, KL divergence, cross-entropy, multi-label BCE
```

상세 spec 은 `docs/notes/architecture_design_20260629.md`.

## Directory structure

```
EmoBrain/
├── project/
│   ├── shared/                       (공통 data + baseline)
│   │   ├── code/{probes,bfm_embeddings,ssl_pretrain,analysis,tools}/
│   │   ├── data/                     (Horikawa splits, target matrices, ROI csv)
│   │   ├── output/                   (BFM embeddings, logs)
│   │   └── results/background/       (baseline CSV, figure)
│   ├── code/                         (main code)
│   │   ├── adapters/                 (brain ↔ LLM token adapter, video ↔ LLM token adapter)
│   │   ├── brain_encoder/            (raw ROI / Ridge / BFM / VLM 의 4 modular)
│   │   ├── vision_encoder/           (CLIP / V-JEPA2 / VideoMAE selectable)
│   │   ├── caption_loader/           (MindCaptioning human + 우리 generated)
│   │   ├── fusion/                   (multi-modal token assembler + LLM wrapper)
│   │   ├── training/                 (4 stage curriculum trainer)
│   │   └── evaluation/               (variance partitioning + ceiling + dissociation)
│   ├── config/                       (YAML hyperparams, model registry)
│   ├── sample_scripts/               (SLURM .sh)
│   └── output/                       (training logs, checkpoints, predictions)
├── archive/                          (이전 framing 의 보존. 현 작업 과 무관, 참조용)
├── external/                         (vendored repos + pretrained checkpoints)
├── docs/                             (notes + reports + reference)
├── Paper/                            (framework_EN/KR, methodology)
├── tools/
└── 7 root .md (README, README_KR, CONTEXT_EMOBRAIN, ACTION_PLAN, CLAUDE, CODEX, ONBOARDING)
```

## Framework 검증 축 (2026-07-03 확정)

두 축 명확히 구분.
- **Encoder 순위 확정** = Track A (E1-E4 각각 학습, brain + question only).
- **Context lift 정량 (framework primary)** = Track B (**Track A best encoder 1 개 만**, teacher + student distillation).

Track B 는 E1-E4 각각 진행 아님. Track A best 하나 만. Framework 검증 의 primary question 은 **"context 가 brain-only 예측 을 얼마나 끌어 올리는가"** 이지 "어느 encoder 가 distillation 과 잘 맞는가" 가 아님.

## Status

- 12-16 주 build phase. S7-S11 (`ACTION_PLAN.md`).
- Resolved decisions. Backbone Qwen3-VL 2B + 4B 둘 다 ablation. Caption source MindCaptioning only + MindCaptioning + 우리 generated dual 둘 다 ablation. Track B scope = Track A best encoder 1 개 (2026-07-03).

## Pointers

| 파일 | 역할 |
|------|------|
| `docs/notes/implementation_spec_20260702.md` | **Code 구현 명세** (Claude Code 대상, DECIDED / OPEN / CAUTION, Acceptance, 34개 감정 순서). Code 시작 시 canonical spec |
| `Paper/framework_EN.md` + `Paper/framework_KR.md` | Spine narrative (5 NV + architecture + evaluation framework + sub-claims) |
| `docs/notes/architecture_design_20260629.md` | Architecture design 의 상세 spec |
| `docs/notes/project_decisions.md` | Chronological decision log |
| `ACTION_PLAN.md` | S7-S11 의 ground-level weekly action |
| `CONTEXT_EMOBRAIN.md` | Agent / 협업자 의 compact context |
| `project/shared/data/cowen34_order.txt` | 34 감정 canonical 순서 (라벨 / 예측 / mu, std 강제) |
