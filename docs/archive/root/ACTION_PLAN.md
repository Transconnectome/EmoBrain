> ⚠️ **ARCHIVED — 역사 기록. 현행 문서가 아니다.**
> 현행 논증 = `docs/paper_logic_merged.md` (대전제 · RQ · 가설 H1–H4). 운영 규칙 = `CLAUDE.md`.
>
> 아래 내용 중 다음은 **뒤집혔다.** (a) Qwen3-VL 등 LLM backbone 사용 — 금지.
> (b) open-vocabulary / cross-taxonomy 전이를 headline novelty 로 삼는 프레임 — 폐기.
> (c) 학습에 없던 감정 zero-shot — 폐기(원칙적 분할 기준 없음, RQ 와 무관).
> (d) "EmoBrain 과 EmoViS 는 별도 논문 2편" — 현재는 **한 편의 논문**.
> (e) "EmoBrain 은 cortical location 을 주장하지 않는다" — 현재 **H3 이 cortical location 주장**이다.

# EmoBrain Action Plan

> **SUPERSEDED 2026-08-17 — LLM backbone removed.** Current plan is the roadmap in
> `docs/direction_v6_labelquery_20260817.md` (§10). The Qwen3-VL-4B P0/P1 checklist
> below is historical.

## P0. Canonical Infrastructure

- [x] Qwen3-VL-4B-only backbone loader
- [x] Internal-padding compaction and safe readout token selection
- [x] E1 ViT / E2 BFM registry
- [x] Remove target-space encoder from the active pipeline
- [x] Correct `log1p_z` inverse metrics
- [x] Corrected Brain-JEPA provenance importer
- [x] Isolate Qwen2.5 implementation under `project/legacy/`

## P1. Direct Decoding

- [ ] Import corrected Brain-JEPA embeddings
- [ ] Run E1 ViT direct student
- [ ] Run E2 corrected Brain-JEPA direct student
- [ ] Run E2 SwiFT direct student
- [ ] Compare three seeds on stimulus-held-out test

## P2. Core Distillation

- [x] Teacher checkpointing and test reporting
- [x] Provenance-aware teacher soft-label cache
- [x] Brain-only student hard + distillation MSE
- [x] One-command teacher -> cache -> student launcher
- [ ] Run the E2 Brain-JEPA distillation workflow

## P3. Student-Side Ablations

- [ ] Hard-only vs distilled student with identical initialization and seed
- [ ] Context-only teacher and brain-shuffled student checks
- [ ] Video-only, caption-only, and video+caption teacher comparisons
- [ ] Caption affect-language sensitivity analysis
- [ ] Projector type and token-count sensitivity

## P4. Neuroscience

- [ ] Per-emotion transfer and distillation gain maps
- [ ] Cortical/network contribution analysis
- [ ] Visual/semantic controls and variance partitioning at the prediction level
- [ ] Short-window length and padding sensitivity
- [ ] Cross-subject and future cross-dataset generalization
