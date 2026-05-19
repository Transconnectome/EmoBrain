# FEELIN

**Brain-conditioned Emotion-Vision-Language Model on Naturalistic fMRI**


## 한 줄 요약

fMRI 와 video 를 함께 입력으로 받아 그 사람이 영상에서 느낀 emotion 을 자연어로 묘사하는 model 을 만든다. 그리고 fMRI 인코더로 어떤 brain foundation model 을 쓰면 가장 좋은지 비교한다.


## Big Question

> fMRI 와 video 를 함께 받는 model 이 그 사람이 영상에서 느낀 emotion 을 자연어로 묘사할 수 있는가? 그리고 fMRI 를 어떻게 인코딩해야 (어떤 brain foundation model 을 쓰면) 묘사가 가장 잘 되는가?


## 3 Sub-question

1. **Caption 의 affect 정확도** — Brain-conditioned caption 에서 추출한 V/A 가 그 subject 의 self-rating 과 within-subject Pearson r ≥ 0.4, video-only baseline 보다 유의하게 높은가?
2. **Brain swap 의 caption 변화** — 같은 영상에 다른 사람 brain 을 conditioning 하면 caption affect tone 이 systematically 다른가? (brain 이 caption 의 driver 인가)
3. **Stimulus retrieval** — 생성된 caption 으로 자극을 retrieval 할 때 Mind Captioning baseline 의 80% 이상 정확도 유지 (affect 에 집중하면서도 content grounding 보존)?


## Architecture

```
fMRI ─► [fMRI encoder = swap-in BFM 후보] ─► z_brain
                                                │
                          ▼ as prefix / cross-attn ◄── video frames
                  Brain-VLM (UMBRELLA_qwen, Qwen3-VL)
                                                │
                                                ▼
                                  free-form emotion caption
                                                │
                       ┌────────────────────────┼────────────────────────┐
                       ▼                        ▼                        ▼
                  SQ1: affect accuracy   SQ2: brain swap         SQ3: retrieval
```

Vision tower swap 3 수준 (각각 go/no-go gate):
- **L1**: Frozen BFM embedding → linear projection 으로 주입 (안전, Phase 2)
- **L2**: BrainVLM 의 vision tower 를 BFM 으로 교체, freeze (Phase 3)
- **L3**: LoRA fine-tune (deep, Phase 3 후반)


## BFM 의 역할

BFM 4 종 (SwiFT, Brain-JEPA, NeuroSTORM, BrainLM) 은 **BrainVLM 의 fMRI 인코더 후보**. SQ2 의 핵심 비교 축. 우리가 한 BFM padding ablation / extraction / probe 작업이 이 비교의 build-up.


## EmoViS 와의 관계

- EmoViS = brain ↔ visual-semantic alignment 분석 (별도 repo)
- FEELIN = brain-conditioned caption generation (이 repo)
- **공유**: stimulus features (V-JEPA2, CLIP, DINOv2, VideoMAE, Qwen-VL caption). FEELIN 에서는 추출 안 함, `data/stimulus_features/` 에 EmoViS symlink
- W12 / W18 에 결과 비교 meeting. Merge 가능성 열어둠.


## Phase Status (6 month plan)

| Phase | Week | 다루는 sub-Q | Gate | 상태 |
|---|---|---|---|---|
| Phase 1: Foundation (BrainVLM transfer + BFM 추출 완성 + EmoViS feature 통합) | W1-6 | (사전 검증) | W6 BrainVLM transferable? | **진행 중** |
| Phase 2: Brain-conditioned VLM 학습 (L1: frozen BFM embedding) | W7-12 | SQ1 | W12 L1 result | 대기 |
| Phase 3: Vision tower 교체 (L2) + LoRA (L3) | W13-18 | SQ1, SQ2, SQ3 | W18 L1/L2/L3 비교 | 대기 |
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

2026-05-19 — v3 reframing: "Brain-conditioned Emotion-VLM" 이 core. 이전 v2 의 "context-aware foundation model" framing 폐기. ACTION_PLAN, research_overview, 2026-05-11 시점 자료는 `_archive/` 에. Top-level .md 6개 유지.
