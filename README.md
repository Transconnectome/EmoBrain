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
| **NV3** | Modular brain encoder | raw ROI / Ridge embedding / BFM (Brain-JEPA, NeuroSTORM, SwiFT) / VLM-derived brain token 의 swappable adapter. 같은 fusion stack 이 4 encoder 모두 받음. |
| **NV4** | 34-distribution curriculum | Cowen 34-category distribution 출력 을 top-1 → top-2 → top-k → full 34D KL 의 4 stage curriculum 으로 학습. |

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

OUTPUT (4 stage curriculum, NV4)
  Stage 1   top-1     34-class CE
  Stage 2   top-2     multi-label CE (top 2 per stimulus)
  Stage 3   top-k     k-hot sparse CE
  Stage 4   full 34D  soft distribution KL (rater empirical distribution as target)

LOSS
  Stage 1-3  cross-entropy + class weighting
  Stage 4    KL divergence with soft target + class weighting
  Optional   brain-reconstruction auxiliary (LLM hidden → ROI mean 복원)
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

## Status

- 12-16 주 build phase. S7-S11 (`ACTION_PLAN.md`).
- Resolved decisions. Backbone Qwen3-VL 2B + 4B 둘 다 ablation. Caption source MindCaptioning only + MindCaptioning + 우리 generated dual 둘 다 ablation.

## Pointers

| 파일 | 역할 |
|------|------|
| `Paper/framework_EN.md` + `Paper/framework_KR.md` | Spine narrative (5 NV + architecture + evaluation framework + sub-claims) |
| `docs/notes/architecture_design_20260629.md` | Architecture design 의 상세 spec |
| `docs/notes/project_decisions.md` | Chronological decision log |
| `ACTION_PLAN.md` | S7-S11 의 ground-level weekly action |
| `CONTEXT_EMOBRAIN.md` | Agent / 협업자 의 compact context |
