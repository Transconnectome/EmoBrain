# FEELIN 한국어 가이드

**Transferable Emotion Brain Foundation Model from Naturalistic fMRI**


## 한 줄

Horikawa naturalistic fMRI 로 transfer 가능한 multi-dimensional emotion brain representation 을 학습하고, metadata 가 빈약한 independent dataset / 새 subject / 다른 taxonomy 로 일반화되는지 측정한다. 어떤 supervision 과 어떤 brain encoder (SwiFT / Brain-JEPA / NeuroSTORM) 가 가장 transferable 한 표상을 만드는지 비교한다.


## Big Question

Naturalistic fMRI 로부터 학습한 multi-dimensional emotion brain representation 이, 단일 dataset 과 label taxonomy 에 종속되지 않고 새로운 subject, 자극, emotion 어휘로 transfer 되는 emotion brain foundation model 이 될 수 있는가?

<sub>운영 정의 (operationalization, FEELIN testbed): Horikawa naturalistic fMRI 로 학습한 multi-dimensional emotion brain representation 이, metadata 가 풍부하지 않은 independent dataset / 새 subject / 다른 emotion taxonomy 로 transfer 되는 emotion brain foundation model 이 될 수 있는가? 그리고 어떤 supervision (scalar V/A vs Cowen 34-category vs 14-dimension vs open-vocabulary description) 과 어떤 brain encoder 가 가장 transferable 한 표상을 만드는가? supervision 과 encoder 비교는 SQ2 와 encoder-swap 축에서 다룬다.</sub>

v3 의 질문 ("fMRI + video fusion 이 video baseline 을 넘는가") 은 Phase 1 + Phase 2 joint 가 "넘지 못한다" 로 답했고 (crowd V/A label = stimulus 속성이라 trivial), 측정 결과는 보존된다. 근거 (Horikawa 2020): emotion category 가 affective dimension 보다, transmodal region 에서 video feature 를 능가.


## 5 Sub-question (전부 representation 질문)

1. **SQ1 Transfer (main)**, Horikawa 학습 표상이 새 dataset / subject / taxonomy 로 일반화되는가? (zero-shot + few-shot)
2. **SQ2 Supervision richness**, scalar V/A vs Cowen 34 / 14 / open-vocabulary 중 어느 supervision 이 더 transferable 한가?
3. **SQ3 Representation geometry**, 학습된 emotion space 가 Horikawa 2020 구조를 복원하나? (RSA / CKA)
4. **SQ4 Data efficiency**, pretrained FM 이 from-scratch 대비 몇 배 적은 label 로 같은 성능?
5. **SQ5 Where (label-free)**, emotion 정보가 brain 의 어디에? network-restricted, ISC ceiling.

### Cross-dataset evaluation (metadata 빈곤 해결)

1 Shared text-embedding zero-shot (main), 2 Label-space intersection (안전), 3 MLLM (OV-MER / AffectGPT) universal annotator, 4 Representational alignment (label-free). 자세한 내용 `docs/masterplan_v2.md` 4 절.

### Probe 별 scientific question

| Probe | Question |
|---|---|
| BFM frozen probe | 각 brain foundation model 의 frozen embedding 이 emotion 의 어떤 측면을 capture 하나? |
| Video-only probe | 자극 feature 만으로 emotion 예측 ceiling 은? Brain 의 added value 의 reference baseline |
| Late fusion (Phase 2) | Brain + video 결합이 단독 대비 향상이 있는가? |
| Contrastive (Phase 2-3) | Brain-video shared latent 학습이 emotion 표상 향상시키나? |
| LLM-token (Phase 3) | fMRI 를 LLM token 으로 주입한 model 이 emotion caption 을 생성하나? |


## 어떻게 만드는가 (build recipe)

5 subject × 2185 stimulus 로는 FM 을 from-scratch pretrain 할 수 없다. 그래서 **대규모 pretrained brain backbone + 대규모 pretrained emotion-language space 를 emotion-transferable 하게 잇는 adaptation** 이 핵심이다. 상세는 [`docs/masterplan_v2.md`](docs/masterplan_v2.md) 5 절.

```
fMRI ─► [A] 450-ROI parcel 입력 (Schaefer-400 + Tian-50, scanner / dataset 무관 substrate)
        │
        ▼ [B] Brain-JEPA backbone + LoRA   (frozen 금지, resting prior → emotion 으로 reshape)
        │
        ▼ projection
        z_emo ─► [C] frozen emotion-text embedding space (sentence-transformer / CLIP-text)
                  target = embed( Cowen 34-cat + 14-dim 문장화 또는 AffectGPT OV description )
                  loss  = contrastive InfoNCE (brain ↔ matched emotion-text) + 보조 regression
        │
        ▼ [D] subject + multi-dataset pooling (Horikawa + Emo-FilM + Koide-Majima + Affective Videos)
                shared text space 가 이질적 taxonomy harmonize → foundation 규모 데이터
        ▼ 평가 (freeze 후)
        - zero-shot cross-dataset retrieval (native label 을 같은 text space 로 encode)
        - few-shot scaling (SQ4) / RSA geometry (SQ3) / region-restricted (SQ5)
```

- **foundation 의 출처**: backbone (수만 subject pretrained) + emotion-text space (수천 emotion 개념 geometry). FEELIN 기여 = 둘을 잇는 adaptation recipe.
- **brain encoder 후보 (Block B swap 축)**: Brain-JEPA (ROI, default) / SwiFT (NewE96 + 변종) / NeuroSTORM. BrainLM 은 490 TR × A424 고정으로 Horikawa 비호환, 제외.
- **옛 frame 탈피**: brain + video fusion, BrainVLM token, late fusion 은 main path 아님. video 는 옵션 teacher 로만. 정직한 framing = from-scratch pretrain 이 아니라 brain FM 의 emotion-specialized adaptation.


## Evaluation protocol

- **5-fold stim-stratified CV** (`data/horikawa_5fold.csv`)
- 각 fold k: test=k, val=(k%5)+1, train=나머지 3
- 6 task × 2 head (Linear + MLP) × (BFM 의 경우 2 mode) × 1 seed (screening) / 3 seed (final paper)


## Phase Status

| Phase | Week | 다루는 sub-Q | 상태 |
|---|---|---|---|
| Phase 1: Foundation (frozen probe benchmark + SwiFT padding ablation + 6 SwiFT variants) | W1-6 | (사전 검증) | **✅ 완료** (15p main + 11p supplementary PDF) |
| Phase 2: 통합 학습 (4 architecture A/B/C/D + brain-only 4 methods I/II/III/IV) | W7-12 | SQ1, SQ2 | **🔄 진행 중** |
| Phase 3: Deep integration + subject-conditioned variability | W13-18 | SQ2, SQ3, SQ4 | 대기 |
| Phase 4: Submission | W19-24 | (통합) | 대기 |

자세한 plan: [`docs/masterplan_v2.md`](docs/masterplan_v2.md).
Phase 1 보고서: [`reports/phase1_wrapup/main.pdf`](reports/phase1_wrapup/main.pdf).
Phase 2 진행: [`code/phase2/README.md`](code/phase2/README.md).

### Phase 1 핵심 finding

Frozen BFM 모두 video baseline 못 넘음 (CLIP 0.97 ≫ BFM best 0.74). 이건 V/A label 이
crowd-sourced video attribute 라 trivial. SwiFT 5M~264M size 효과 무. Padding ablation 4
mode 거의 비슷 (시간 정보 frozen 으로 안 씀). Phase 2 trained integration 으로 진행.

### Phase 2 finding (진행 중)

4 fusion arch (D/A/B/C joint) 가 V_binary 0.97 (CLIP 단독 = 그대로 saturate). Brain 추가
효과 noise 수준 → 질문 A 종료. Brain-only 4 method 학습 중.

측정값 전부 보존 (`reports/phase1_wrapup/`, `docs/masterplan_v2.md` 7.0).


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

2026-06-02, v4 reframing: Big Question 축을 transfer 로 이동 (질문 A = video fusion, 측정 완료 / 질문 B = transfer 가 본 plan). target 을 Cowen 34 / 14 / OV emotion-text embedding 으로 승격, V/A 강등. cross-dataset 평가 4 전략 + build recipe (Brain-JEPA backbone + LoRA → emotion-text space) 도입. 측정 결과 전부 보존 (`docs/masterplan_v2.md` 7.0). 상세 결정 로그는 `notes/project_decisions.md`.

2026-05-19 — v3 reframing 으로 "Emotion-aware Multimodal Foundation Model" 이 core. fMRI 통합 architecture 는 design space (LLM token / cross-attention / contrastive / late fusion). BrainVLM 은 Option A 의 baseline. 이전 v2 의 "context-aware foundation model" framing 폐기. ACTION_PLAN, research_overview, 2026-05-11 시점 자료는 `_archive/` 에.
