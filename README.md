# FEELIN

**Emotion-aware Multimodal Foundation Model from Naturalistic fMRI + Video**


## 한 줄 요약

fMRI 와 video 를 함께 활용해 emotion-aware multimodal foundation model 을 만든다. fMRI 를 어떤 architecture × 어떤 brain encoder 로 통합해야 model 의 emotion 이해 능력이 가장 잘 형성되는지 비교한다.


## Big Question

> fMRI 와 video 를 함께 활용해 emotion-aware multimodal foundation model 을 만들 수 있는가? 그리고 fMRI 를 어떻게 인코딩 / 통합해야 (어떤 architecture × 어떤 brain encoder) model 의 emotion 이해 능력이 가장 잘 형성되는가?


## 4 Sub-question

1. **fMRI 통합 방법 + brain encoder 선택 (main)** — 4 architecture (LLM token / cross-attention / contrastive / late fusion) × 4 brain encoder (SwiFT / Brain-JEPA / NeuroSTORM / BrainLM) 중 어느 조합이 emotion task 에서 video-only baseline 을 넘는가?
2. **Emotion 표상의 evidence** — V/A regression + 27/34-cat 분류 + 14 affective dim + caption affect 모두에서 model 이 baseline 을 넘는가?
3. **Brain 의 causal 기여** — 같은 video × 다른 brain → output 차이가 systematic 한가? (counterfactual subject swap)
4. **Content grounding 보존** — Caption 으로 stimulus retrieval 시 Horikawa Mind Captioning baseline 의 80% 정확도 유지?

### Probe pipeline 별 scientific question

| Probe | Scientific question | 답하는 것 |
|---|---|---|
| **BFM frozen probe** | 각 brain foundation model 의 frozen embedding 이 emotion 의 어떤 측면을 capture 하나? Architecture × init × subject mode 의 어느 조합이 어느 task 에 강한가? | Tier 2 ceiling 측정 (SQ1 brain side) |
| **Video-only probe** | 자극 (영상) 자체의 feature 만으로 emotion 이 어디까지 예측되나? Brain 없이 video model 만의 ceiling 은? | "Brain 이 video 위에 추가하는 value" 의 reference. **Reviewer 의 가장 큰 challenge 에 대한 직접 답** |
| (Phase 2) Late fusion | Brain + video 결합이 단독 대비 향상이 있는가? | Architecture D 결과, brain unique contribution evidence |
| (Phase 2-3) Contrastive | Brain-video shared latent 학습이 emotion 표상 capture 향상? | Architecture C 결과 |
| (Phase 3) LLM-token | fMRI 를 LLM token 으로 주입한 model 이 emotion caption 생성하나? | Architecture A 의 generative novelty |


## Architecture — design space

```
fMRI ─► brain encoder (4 종 swap-in) ─► z_brain
                                            │
                ▼ 4 통합 option (SQ1) ◄── video features (EmoViS 추출본 reuse)
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
                  - Free-form emotion caption (retrieval evaluation)
                  - Latent embedding (counterfactual swap)
```

Option A (LLM token, BrainVLM) 안에서 vision tower swap depth 3 수준:
- L1: Frozen embedding → linear projection 으로 주입
- L2: Vision tower 교체 + freeze
- L3: LoRA fine-tune

Option B/C/D 는 Phase 2 의 A 결과 보고 결정.


## Brain encoder 4 종의 역할

SwiFT / Brain-JEPA / NeuroSTORM / BrainLM = **fMRI 를 model 입력으로 변환하는 인코더 후보**. SQ1 의 핵심 비교 축. 우리가 한 BFM padding ablation / extraction / probe 작업이 이 비교의 build-up.


## Evaluation protocol (모든 probe 공통)

- **5-fold stim-stratified CV** (`data/horikawa_5fold.csv`, V × A quartile joint stratification)
- 각 outer fold k 마다: test = fold k, val = (k%5)+1, train = 나머지 3 fold
- 6 task: V_binary, A_binary, V_reg, A_reg, Cat34_top1, Dim14_multi
- Head 2 종: Linear (deterministic, 1 seed) + MLP (default 1 seed screening, final paper 시 3 seed)
- BFM probe 는 추가로 `pooled` vs `per_subject` 2 mode
- 모든 결과: per-fold per-seed row → CSV (`results/phase1/`)


## EmoViS 와의 관계

- EmoViS = brain ↔ visual-semantic alignment 분석 (별도 repo)
- FEELIN = brain-conditioned caption generation (이 repo)
- **공유**: stimulus features (V-JEPA2, CLIP, DINOv2, VideoMAE, Qwen-VL caption). FEELIN 에서는 추출 안 함, `data/stimulus_features/` 에 EmoViS symlink
- W12 / W18 에 결과 비교 meeting. Merge 가능성 열어둠.


## Phase Status (6 month plan)

| Phase | Week | 다루는 sub-Q | Gate | 상태 |
|---|---|---|---|---|
| Phase 1: Foundation (architecture A transfer + brain encoder 추출 완성 + EmoViS feature 통합) | W1-6 | (사전 검증) | W6 Option A transferable? | **진행 중** |
| Phase 2: 통합 학습 (Option A L1 → L2, 필요 시 B/C/D pilot) | W7-12 | SQ1, SQ2 | W12 video-only baseline 넘는가 | 대기 |
| Phase 3: Deep integration (L3 LoRA) + causal evidence | W13-18 | SQ2, SQ3, SQ4 | W18 brain swap effect + retrieval | 대기 |
| Phase 4: Synthesis + submission | W19-24 | (통합) | W24 venue 결정 | 대기 |

자세한 phase 별 task / go-no-go / agent review 는 [`docs/masterplan_v2.md`](docs/masterplan_v2.md).


## Repository Map

| 경로 | 내용 |
|---|---|
| `docs/masterplan_v2.md` | Forward plan (Big Q, 3 sub-Q, phase, go-no-go) |
| `reports/phase1_foundation.md` | Phase 1 progress |
| `data/stimulus_features/` | EmoViS symlinks (V-JEPA2, CLIP, DINOv2, VideoMAE, Qwen-VL caption) |
| `data/{horikawa_split, *_binary_subset, feelin_canonical_stimuli}.csv` | Splits + V/A binary subset + 2185 canonical stim |
| `code/bfm_embeddings/{_lib, extract_embedding, run_full}/` | BFM extraction (SwiFT / Brain-JEPA / NeuroSTORM lib + leaf scripts + per-subject wrappers) |
| `code/probes/` | Tier 1 ROI feature + unified frozen probe |
| `code/analysis/` | Padding ablation, multi-BFM probe, figure 생성 |
| `code/brainvlm/` (Phase 1 에 생성 예정) | BrainVLM loader, transfer test, training |
| `output/embeddings/` | 추출된 BFM .pt features (proper mean padding) |
| `results/{padding_ablation, main_grid_3bfm, phase1}/` | Probe 결과 CSV + figure |
| `baseline/` | BFM checkpoints |
| `external/Brain-JEPA/`, `external/NeuroSTORM/` | Vendored model code |
| `Paper/framework_*.md`, `Paper/methodology.md` | Canonical narrative + methodology |
| `notes/{benchmark_design, project_decisions}.md` | Dataset matrix + decision log |
| `reference/{datasets, task, papers, code_resources, training_strategy}.md` | Reference docs |


## Phase 1 즉시 실행

```bash
# 1. BrainVLM env setup (Phase 1 W1, critical path)
#    UMBRELLA_qwen env 활성화 + ABCD checkpoint 확보
#    위치: /pscratch/sd/s/sjmoon/BrainVLM/UMBRELLA_qwen/

# 2. BFM proper mean 재추출 (병행 진행 중, 단일 wrapper)
bash /pscratch/sd/s/sjmoon/FEELIN/code/bfm_embeddings/run_full/proper_mean_all.sh

# 3. EmoViS feature 로딩 sanity check (이미 symlink 완료)
ls /pscratch/sd/s/sjmoon/FEELIN/data/stimulus_features/

# 4. Phase 1 W5-6 의 unified frozen probe (Tier 1 ROI + Tier 2 BFM, optional, 이미 만들어둠)
bash /pscratch/sd/s/sjmoon/FEELIN/code/probes/run_unified_probe.sh
```


## Cleanup history

2026-05-19 — v3 reframing: "Emotion-aware Multimodal Foundation Model" 이 core. fMRI 통합 architecture 는 design space (LLM token / cross-attention / contrastive / late fusion 4 option). BrainVLM 은 Option A 의 baseline architecture. 이전 v2 의 "context-aware foundation model" framing 폐기. ACTION_PLAN, research_overview, 2026-05-11 시점 자료는 `_archive/` 에. Top-level .md 6개 유지.
