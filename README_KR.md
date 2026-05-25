# FEELIN 한국어 가이드

**Emotion-aware Multimodal Foundation Model from Naturalistic fMRI + Video**


## 한 줄

fMRI 와 video 를 함께 활용해 emotion-aware multimodal foundation model 을 만든다. fMRI 를 어떤 architecture × 어떤 brain encoder (SwiFT / Brain-JEPA / NeuroSTORM / BrainLM) 로 통합해야 model 의 emotion 이해 능력이 가장 잘 형성되는지 비교한다.


## Big Question

fMRI 와 video 를 함께 활용해 emotion-aware multimodal foundation model 을 만들 수 있는가? 그리고 fMRI 를 어떻게 인코딩 / 통합해야 (어떤 architecture × 어떤 brain encoder) model 의 emotion 이해 능력이 가장 잘 형성되는가?


## 4 Sub-question

1. **fMRI 통합 방법 + brain encoder 선택 (main)** — 4 architecture (LLM token / cross-attention / contrastive / late fusion) × 4 brain encoder 중 어느 조합이 video-only baseline 을 넘는가?
2. **Emotion 표상의 evidence** — V/A regression + 27/34-cat 분류 + 14 affective dim + caption affect 모두에서 향상?
3. **Brain causal 기여** — 같은 video × 다른 brain 으로 conditioning 했을 때 output 차이가 systematic 한가? (counterfactual subject swap)
4. **Content grounding 보존** — Caption 으로 stimulus retrieval 시 Mind Captioning baseline 80% 유지?

### Probe 별 scientific question

| Probe | Question |
|---|---|
| BFM frozen probe | 각 brain foundation model 의 frozen embedding 이 emotion 의 어떤 측면을 capture 하나? |
| Video-only probe | 자극 feature 만으로 emotion 예측 ceiling 은? Brain 의 added value 의 reference baseline |
| Late fusion (Phase 2) | Brain + video 결합이 단독 대비 향상이 있는가? |
| Contrastive (Phase 2-3) | Brain-video shared latent 학습이 emotion 표상 향상시키나? |
| LLM-token (Phase 3) | fMRI 를 LLM token 으로 주입한 model 이 emotion caption 을 생성하나? |


## Architecture — design space

```
fMRI ─► brain encoder (4 종 swap-in) ─► z_brain
                                            │
                ▼ 4 통합 option (SQ1) ◄── video features (EmoViS reuse)
                  A: LLM token (BrainVLM)
                  B: Cross-attention
                  C: Contrastive alignment
                  D: Late fusion
                                            │
                                            ▼
                          Foundation model (LLM / transformer)
                                            │
                                            ▼
                  Multi-channel output:
                  - V/A continuous regression
                  - 27-cat classification
                  - Free-form emotion caption
                  - Latent embedding (counterfactual swap)
```

Option A 안에서 vision tower swap depth 3 수준 (L1 frozen → L2 swap+freeze → L3 LoRA), 각각 go/no-go.
Option B/C/D 는 Phase 2 의 A 결과 보고 결정.


## Brain encoder 4 종의 역할

SwiFT / Brain-JEPA / NeuroSTORM / BrainLM = **fMRI 를 model 입력으로 변환하는 인코더 후보**. SQ1 의 핵심 비교 축. 우리가 한 BFM extraction 작업이 이 비교의 build-up.


## EmoViS 와의 관계

- EmoViS = brain ↔ visual-semantic alignment (별도 repo)
- FEELIN = brain-conditioned caption generation
- **공유**: stimulus features. FEELIN 은 추출 안 함, `data/stimulus_features/` 에 EmoViS symlink. EmoViS 에 V-JEPA2, CLIP, DINOv2, VideoMAE, Qwen-VL caption 다 있음.
- W12, W18 결과 비교. Merge 가능성 열어둠.

CCN (사용자 발표) 의 결과는 인용 안 함. 아이디어만 reference.


## Phase Status

| Phase | Week | 다루는 sub-Q | Gate | 상태 |
|---|---|---|---|---|
| Phase 1: Foundation | W1-6 | (사전 검증) | W6 Option A transferable? | **진행 중** |
| Phase 2: 통합 학습 (Option A L1 → L2, 필요 시 B/C/D pilot) | W7-12 | SQ1, SQ2 | W12 baseline 넘는가 | 대기 |
| Phase 3: Deep integration (L3 LoRA) + causal | W13-18 | SQ2, SQ3, SQ4 | W18 brain swap + retrieval | 대기 |
| Phase 4: Submission | W19-24 | (통합) | W24 venue | 대기 |

자세한 plan: [`docs/masterplan_v2.md`](docs/masterplan_v2.md).


## Repository Map

| 경로 | 내용 |
|---|---|
| `docs/masterplan_v2.md` | Forward plan |
| `reports/phase1_foundation.md` | Phase 1 진행 보고 |
| `data/stimulus_features/` | EmoViS symlinks |
| `data/{horikawa_split, *_binary_subset, feelin_canonical_stimuli}.csv` | Splits + V/A binary + canonical stim |
| `code/bfm_embeddings/` | BFM extraction (lib + leaf + wrapper) |
| `code/probes/` | ROI feature + unified frozen probe |
| `code/analysis/` | Padding ablation, multi-BFM probe, figure 생성 |
| `code/brainvlm/` (Phase 1 W1 생성) | BrainVLM loader, transfer test, training |
| `output/embeddings/` | BFM .pt features |
| `results/{padding_ablation, main_grid_3bfm, phase1}/` | Probe 결과 |
| `baseline/` | BFM checkpoints |
| `external/Brain-JEPA/`, `external/NeuroSTORM/` | Vendored model code |
| `Paper/framework_*.md`, `methodology.md` | Canonical narrative + methodology |
| `notes/{benchmark_design, project_decisions}.md` | Dataset matrix + decision log |
| `reference/{datasets, task, papers, code_resources, training_strategy}.md` | Reference |


## Phase 1 즉시 작업

```bash
# 1. BrainVLM env setup (critical path)
#    /pscratch/sd/s/sjmoon/BrainVLM/UMBRELLA_qwen/ 의 env 활성화 + checkpoint

# 2. BFM proper mean 재추출 (병행)
bash /pscratch/sd/s/sjmoon/FEELIN/code/bfm_embeddings/run_full/proper_mean_all.sh

# 3. EmoViS feature 확인
ls /pscratch/sd/s/sjmoon/FEELIN/data/stimulus_features/

# 4. (optional) Tier 1 + Tier 2 unified probe
bash /pscratch/sd/s/sjmoon/FEELIN/code/probes/run_unified_probe.sh
```


## Cleanup history

2026-05-19 — v3 reframing 으로 "Emotion-aware Multimodal Foundation Model" 이 core. fMRI 통합 architecture 는 design space (LLM token / cross-attention / contrastive / late fusion). BrainVLM 은 Option A 의 baseline. 이전 v2 의 "context-aware foundation model" framing 폐기. ACTION_PLAN, research_overview, 2026-05-11 시점 자료는 `_archive/` 에.
