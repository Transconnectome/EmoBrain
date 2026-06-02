# FEELIN

**Transferable Emotion Brain Foundation Model from Naturalistic fMRI**


## 한 줄 요약

Horikawa naturalistic fMRI 로 transfer 가능한 multi-dimensional emotion brain representation 을 학습하고, metadata 가 빈약한 independent dataset / 새 subject / 다른 label taxonomy 로 일반화되는지 측정한다. 어떤 supervision 과 어떤 brain encoder 가 가장 transferable 한 표상을 만드는지 비교한다.


## Big Question

> Naturalistic fMRI 로부터 학습한 multi-dimensional emotion brain representation 이, 단일 dataset 과 label taxonomy 에 종속되지 않고 새로운 subject, 자극, emotion 어휘로 transfer 되는 emotion brain foundation model 이 될 수 있는가?

<sub>운영 정의 (operationalization, FEELIN testbed): Horikawa naturalistic fMRI 로 학습한 multi-dimensional emotion brain representation 이, metadata 가 풍부하지 않은 independent dataset / 새 subject / 다른 emotion taxonomy 로 transfer 되는 emotion brain foundation model 이 될 수 있는가? 그리고 어떤 supervision (scalar V/A vs Cowen 34-category vs 14-dimension vs open-vocabulary description) 과 어떤 brain encoder 가 가장 transferable 한 표상을 만드는가? supervision 과 encoder 비교는 SQ2 와 encoder-swap 축에서 다룬다.</sub>

### v3 → v4 (두 개의 다른 질문 분리)

v3 의 질문 ("fMRI + video fusion 이 video-only baseline 을 넘는가") 은 Phase 1 + Phase 2 joint 가 "넘지 못한다" 로 답했다. crowd-sourced V/A label 은 stimulus 속성이라 CLIP 같은 video encoder 가 이기는 게 trivial 하기 때문이다. v4 는 질문을 transfer 로 옮긴다. foundation model 의 contribution 은 "brain 이 video 를 이기나" 가 아니라 representation 의 transfer / generalization / data-efficiency / universality 다. 근거는 Horikawa et al. 2020 (iScience): emotion category 표상이 affective dimension 보다, transmodal region 에서 visual / semantic covariate (video feature) 를 능가한다.


## 5 Sub-question (전부 representation 질문, "brain 이 video 를 이겨야" 전제 없음)

1. **SQ1 Transfer (main)**, Horikawa 에서 학습한 brain emotion representation 이 retrain 없이 새 dataset / subject / taxonomy 로 일반화되는가? (zero-shot + few-shot scaling)
2. **SQ2 Supervision richness**, scalar V/A vs Cowen 34-category / 14-dimension / open-vocabulary description 중 어느 supervision 이 더 transferable 한 표상을 만드는가?
3. **SQ3 Representation geometry**, 학습된 brain emotion space 가 Horikawa 2020 구조 (high-dim, category > dimension, transmodal 분산) 를 복원하는가? (RSA / CKA)
4. **SQ4 Data efficiency**, pretrained brain emotion FM 이 새 dataset 에서 from-scratch 대비 몇 배 적은 label 로 같은 성능에 도달하는가?
5. **SQ5 Where (label-free)**, emotion 정보가 brain 의 어디에 있는가? network-restricted probe, ISC ceiling. label 빈약한 dataset 의 fallback.

### Target hierarchy (multi-dim 승격, V/A 강등)

| Tier | Target | 비고 |
|---|---|---|
| Primary | Cowen 34-category, Cowen 14-dimension, OV emotion-text embedding | brain 고유 신호 + cross-dataset 호환 |
| Reference | V/A binary / regression | video 가 이기는 게 알려진 axis, floor / sanity 로만 |

### Cross-dataset evaluation protocol (metadata 빈곤 해결)

| 전략 | 방법 | 위치 |
|---|---|---|
| 1. Shared text-embedding zero-shot (main) | brain → emotion-text space 사영, native label 이름만으로 zero-shot retrieval | masterplan 4.1 |
| 2. Label-space intersection (안전) | target dataset 이 가진 축만 잘라 평가 | 4.2 |
| 3. MLLM universal annotator | OV-MER / AffectGPT 로 모든 stimulus 에 OV 라벨. Horikawa 는 Cowen gold, OV 는 norm 없는 target 에만 | 4.3 |
| 4. Representational alignment (label-free) | RSA / ISC ceiling | 4.4 |


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

SwiFT (NewE96 + 변종) / Brain-JEPA / NeuroSTORM = **fMRI 를 model 입력으로 변환하는 인코더 후보**. SQ1 의 핵심 비교 축. 우리가 한 BFM padding ablation / extraction / probe 작업이 이 비교의 build-up. BrainLM 은 490 timepoint × A424 atlas 가 고정이라 Horikawa 비호환으로 scope 제외.


## Evaluation protocol (모든 probe 공통)

- **5-fold stim-stratified CV** (`data/horikawa_5fold.csv`, V × A quartile joint stratification)
- 각 outer fold k 마다: test = fold k, val = (k%5)+1, train = 나머지 3 fold
- 6 task: V_binary, A_binary, V_reg, A_reg, Cat34_top1, Dim14_multi
- Head 2 종: Linear (deterministic, 1 seed) + MLP (default 1 seed screening, final paper 시 3 seed)
- BFM probe 는 추가로 `pooled` vs `per_subject` 2 mode
- 모든 결과: per-fold per-seed row → CSV (`results/phase1/`)


## Phase Status (6 month plan)

| Phase | Week | 다루는 sub-Q | 상태 |
|---|---|---|---|
| Phase 1: Foundation (frozen probe benchmark + SwiFT padding ablation + 6 SwiFT variants) | W1-6 | (사전 검증) | **✅ 완료** (15p main + 11p supplementary PDF report) |
| Phase 2: 통합 학습 (4 architecture A/B/C/D + brain-only 4 methods I/II/III/IV) | W7-12 | SQ1, SQ2 | **🔄 진행 중** (D/A/B/C joint 끝, brain-only 학습 중) |
| Phase 3: Deep integration + subject-conditioned variability | W13-18 | SQ2, SQ3, SQ4 | 대기 |
| Phase 4: Synthesis + submission | W19-24 | (통합) | 대기 |

자세한 phase 별 task / go-no-go / agent review 는 [`docs/masterplan_v2.md`](docs/masterplan_v2.md).
Phase 1 결과 정리: [`reports/phase1_wrapup/main.pdf`](reports/phase1_wrapup/main.pdf).
Phase 2 진행 상황: [`code/phase2/README.md`](code/phase2/README.md).

### Phase 1 핵심 finding (한 줄)

Frozen brain foundation model probe 어떤 변종도 video pretrained baseline 을 못 넘음
(CLIP V_binary 0.97 ≫ best frozen BFM 0.74). Crowd-sourced V/A label 이 video attribute
라 video 가 우세한 게 trivial. SwiFT 5M~264M size 효과 무. 시간 정보도 frozen probe 에선
거의 사용 안 됨 (padding ablation 4 mode 비슷). Phase 2 trained integration 으로 진행.

### Phase 2 진행 중 finding

- 4 fusion arch (D/A/B/C joint inference) 결과 V_binary AUROC ~0.97 (= CLIP 단독)
- Joint 가 video baseline 위로 추가 향상 만들지 못함 → 질문 A 종료. video 가 stimulus-property
  label 을 saturate 하는 게 trivial 임이 확정
- 진행 중: brain-only 4 method (supervised MLP / CLIP distill / multitask / subject-aware)

### v4 pivot (2026-06-02)

질문을 transfer 로 옮긴다 (위 5 Sub-question). target 을 Cat34 / Dim14 / OV-text-embedding 으로
승격하고 (multi-dim), brain → emotion-text projector 로 cross-dataset zero-shot / few-shot transfer
를 측정한다. OV-MER / AffectGPT 는 metadata 빈약한 target dataset 의 라벨 harmonization 도구로
도입 (Horikawa 자체는 Cowen gold norm 사용). 자세한 내용은 [`docs/masterplan_v2.md`](docs/masterplan_v2.md).


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
