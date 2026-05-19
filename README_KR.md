# FEELIN 한국어 가이드

**Brain-conditioned Emotion-Vision-Language Model on Naturalistic fMRI**


## 한 줄

fMRI 와 video 를 함께 입력으로 받아 그 사람이 영상에서 느낀 emotion 을 자연어로 묘사하는 model 을 만든다. fMRI 인코더로 어떤 brain foundation model (SwiFT, Brain-JEPA, NeuroSTORM, BrainLM) 을 쓰면 가장 좋은지 비교한다.


## Big Question

fMRI 와 video 를 함께 받는 model 이 그 사람이 영상에서 느낀 emotion 을 자연어로 묘사할 수 있는가? 그리고 fMRI 를 어떻게 인코딩해야 (어떤 brain foundation model 을 쓰면) 묘사가 가장 잘 되는가?


## 3 Sub-question

1. **Caption affect 정확도** — Brain-conditioned caption 에서 추출한 V/A 가 self-rating 과 within-subject Pearson r ≥ 0.4 이고 video-only 보다 높은가?
2. **Brain swap caption 변화** — 같은 영상에 다른 사람 brain 으로 conditioning 하면 caption affect tone 이 달라지는가?
3. **Stimulus retrieval** — 생성된 caption 으로 자극 retrieval 시 Mind Captioning baseline 의 80% 이상 정확도 유지?


## Architecture

```
fMRI ─► fMRI encoder (BFM 후보: SwiFT / Brain-JEPA / NeuroSTORM / BrainLM)
                                                │
                              ▼ prefix / cross-attn ◄── video frames
                  Brain-VLM (UMBRELLA_qwen, Qwen3-VL backbone)
                                                │
                                                ▼
                                  free-form emotion caption
```

Vision tower swap 3 수준:
- L1 frozen embedding 주입 (Phase 2)
- L2 vision tower 교체 freeze (Phase 3)
- L3 LoRA fine-tune (Phase 3 후반)

각 수준마다 go/no-go.


## BFM 의 역할

4 종 brain foundation model 은 BrainVLM 의 fMRI 인코더 후보. 우리가 한 BFM extraction 작업이 vision tower swap 비교의 build-up.


## EmoViS 와의 관계

- EmoViS = brain ↔ visual-semantic alignment (별도 repo)
- FEELIN = brain-conditioned caption generation
- **공유**: stimulus features. FEELIN 은 추출 안 함, `data/stimulus_features/` 에 EmoViS symlink. EmoViS 에 V-JEPA2, CLIP, DINOv2, VideoMAE, Qwen-VL caption 다 있음.
- W12, W18 결과 비교. Merge 가능성 열어둠.

CCN (사용자 발표) 의 결과는 인용 안 함. 아이디어만 reference.


## Phase Status

| Phase | Week | 다루는 sub-Q | Gate | 상태 |
|---|---|---|---|---|
| Phase 1: Foundation | W1-6 | (사전 검증) | W6 BrainVLM transferable? | **진행 중** |
| Phase 2: L1 학습 | W7-12 | SQ1 | W12 L1 result | 대기 |
| Phase 3: L2 + L3 | W13-18 | SQ1, SQ2, SQ3 | W18 | 대기 |
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

2026-05-19 — v3 reframing 으로 "Brain-conditioned Emotion-VLM" 이 core. 이전 v2 의 "context-aware foundation model" framing 폐기. ACTION_PLAN, research_overview, 2026-05-11 시점 자료는 `_archive/` 에.
