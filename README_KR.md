# FEEL 한국어 가이드

**Universal Emotion Code in Naturalistic Brain Data**

(내부 / repo / 연구실 정체성 이름은 Foundation Model for Emotion Embedding Learning 로 유지. Paper title 에서는 "Universal Emotion Code in Naturalistic Brain Data" 또는 "Transferable Emotion Brain Foundation Model" 로 표현. 2026-06-02 naming dual-track.)


## 한 줄

Brain 에 paradigm / label / subject 의 surface variation 을 가로지르는 universal emotion code 가 존재하는지를 multi-source naturalistic emotion fMRI 의 SSL pretrain + adaptation 으로 학습하고 검증한다.


## Big Question (v4 final, 2026-06-02)

> Brain 에 paradigm, label taxonomy, subject 의 surface variation 을 가로지르는 *universal emotion code* 가 존재하는가? Multi-source naturalistic emotion fMRI 의 adaptation 으로 그 universal code 를 학습하고 검증할 수 있는가?

핵심 scientific bet. Wager-style universal pain signature 시도의 emotion 판. Affective neuroscience 의 미해결 질문 (universal vs idiosyncratic emotion representation) 에 falsifiable evidence.

"Brain 이 video 를 이겨야" 전제 없음. Phase 1-2 measurement 가 group-level V/A 의 video saturation 을 확정.


## Sub-claims (falsifiable)

1. Universal code 가 있으면 multi-source pretrain representation 이 single-source 보다 cross-dataset transfer 에서 더 invariant
2. Universal code 는 brain 의 특정 ROI / network 에 localize (Cowen 2020 transmodal 가설 비교)
3. Universal code 는 subject-invariant SSL 후 같은 stim 의 다른 subject representation 의 alignment
4. (Null) 위 모두 acquisition floor 안 → "universal code 없음" 결론, negative result paper


## 2 Main Track + 1 Supplementary

| Track | 답하는 sub-Q | Universal code 측정 |
|---|---|---|
| **Track A (main). BFM SSL pretrain + LoRA** | Multi-source SSL 이 invariance emerge 시키는가? | Pretrain 후 cross-dataset invariance metric |
| **Track B (main). Brain+Video framework + task 재설계** | Brain unique 의 universal component? | Joint - video baseline = brain unique. Cross-dataset RSA |
| **Track C (supplementary). BrainVLM** | Universal code 의 generative 표현? | Phase 3a parsing fix. Supplementary figure |

**BrainVLM 이 supplementary 인 이유**. (a) LLM 의 visual bias 가 invariance 측정 가림, (b) generation noise, (c) Phase 3a 약함 (r=NaN, MAE 2.55), (d) 자원 부담.

Track A + Track B 의 converging evidence 가 paper 강점.


## Track A SSL pretrain (priority 순)

### Priority 1 (main, 반드시)

**(1) Subject-invariant SSL**. 같은 video 를 본 5 subject 의 brain response 가 비슷해지도록 contrastive.
- Stim k 의 subject A brain ↔ subject B brain 의 cosine ↑. 다른 stim 은 ↓. InfoNCE.
- Universal code 연결. Subject invariance = universal code 정의. 학습 후 subject alignment 가 직접 evidence.
- 자원 GPU 며칠.

**(2) Multi-source SSL (masked autoencoder, BrainLM-style)**. Horikawa + Emo-FilM + StudyForrest + Affective Videos 의 fMRI 모음. ROI 일부 가리고 예측.
- 450 ROI 중 30% mask → 70% 로 예측. MSE.
- 4 dataset 같은 model, dataset 별 헤더.
- Universal code 연결. Paradigm invariance evidence. Single vs multi-source pretrain 의 invariance 차이.
- 자원 GPU 1-2 주.

### Priority 2 (main, 가능하면)

**(3) Brain-stimulus contrastive (TRIBE-style)**. Brain ↔ video (V-JEPA2 / CLIP) alignment.
- Brain_k ↔ Video_k cosine ↑. 다른 stim ↓.
- Universal code 연결. Universal code 가 stimulus-driven 이면 alignment emerge. Brain unique 분리 시 안 됨.
- 자원 GPU 며칠.

### Priority 3 (optional)

**(4) Curriculum**. Resting → naturalistic movie → emotion-aware 3-stage. Stage 별 prior contribution ablation.
**(5) Distillation**. 큰 BFM → 작은 model. 부수적.


## Target hierarchy

| Tier | Target | 비고 |
|---|---|---|
| Primary | Cross-dataset emotion-text alignment + Cowen 34-cat multilabel + 14-dim + OV description | Universal code invariance 측정 |
| Reference (floor) | V/A binary + regression | Phase 1-2 video saturate 확정. Floor only |


## Cross-dataset evaluation 4 전략

1. Shared text-embedding zero-shot (main)
2. Label-space intersection (안전)
3. MLLM universal annotator (OV-MER local LLM frozen)
4. RSA / ISC ceiling (label-free)


## Build recipe

```
fMRI ─► 450-ROI parcel (Schaefer-400 + Tian-50)
        ▼ Brain-JEPA backbone (pretrained ABCD resting)
        ▼ Track A SSL pretrain (subject-invariant + multi-source masked + brain-stimulus alignment)
        ▼ LoRA adaptation
        ▼ projection
        z_emo ─► frozen emotion-text embedding space (sentence-transformer / CLIP-text)
                  target = embed(Cowen 34-cat + 14-dim or OV description)
                  loss  = InfoNCE + 보조 regression + caption baseline delta
        ▼ multi-source pooling
        ▼ 평가 (freeze 후)
            Track A invariance (subject + paradigm align)
            Track B brain unique cross-dataset RSA
            Track C BrainVLM parsing fix (supplementary)
```


## Brain encoder 후보

| Backbone | 역할 | 상태 |
|---|---|---|
| Brain-JEPA | ROI default | 추출 완료 |
| SwiFT (NewE96 + 5 변종) | 4D volume | NewE96 완료 |
| NeuroSTORM | 4D volume | 추출 완료 |
| BrainLM | 제외 | 490 TR × A424 atlas 고정 → Horikawa 비호환 |


## Independent dataset

| Dataset | Subj × Stim | Label | Role |
|---|---|---|---|
| Horikawa | 5 × 2185 (1 min) | Cowen 34-cat consensus | Base, Track A pretrain, Track B testbed |
| Emo-FilM (Cordoni 2025) | 30 × 14 films | 13 discrete + 42 CPM, 1 Hz | Track A multi-source + cross-dataset test |
| StudyForrest | 20 × Forrest Gump 2h | 8 portrayed + V/A | Track A multi-source + cross-dataset test |
| NNDb (Aliko 2020) | 86 × 10 movies | 없음 | 전략 4 RSA (Appendix) |
| Affective Videos | 11 × 32×4 | V/A | Track A multi-source |


## 측정 결과 (Phase 1 + Phase 2, evidence 보존)

### Phase 1 (frozen probe)

- ROI Schaefer400+Tian50 mean (linear). V_binary AUROC 0.7889 ± 0.0119
- Best BFM (Brain-JEPA resting). V_binary 0.7402 ± 0.0365
- Best video (CLIP). V_binary 0.9708
- 결론. ROI mean > all BFM. Brain 정교화 effect 없음.

### Phase 2 (trained integration)

- D late fusion V_binary 0.9718, CLIP-only 0.9708 → Δ +0.001 (noise)
- A token 0.9670, B cross-attn 0.9663, C contrastive 0.9606
- Brain-only best (multitask) 0.7235
- V_reg A token 0.7628 vs CLIP 0.7645 = -0.002
- A_binary D 0.8025 vs CLIP 0.8003 = +0.002

**결론**. 4 fusion 모두 video baseline 못 넘음. Brain group-level 추가 contribution = 0.

### Phase 3a (BrainVLM)

Fold 1 학습 완료 (loss 0.151). Inference V_reg r = NaN, MAE 2.55. Track C supplementary.

### 의의

Group-level V/A 는 video saturate. Brain unique signal 은 invariance / cross-dataset preservation 의 4 축. Universal code 가 그 invariance 의 scientific 표현. v4 의 Track A/B 가 이 4 축 측정.


## Evaluation protocol

- 5-fold stim-stratified CV
- 6 task × 2 head × (BFM 2 mode) × 1 seed (screening) / 3 seed (final)
- Cross-dataset 은 ComBat + acquisition null
- Track A SSL pretrain 의 invariance metric (subject + paradigm alignment)

### Critic-informed control

- Acquisition control. ComBat + phase-scrambled null + trivial ROI mean null. Transfer Δ > 2σ × max(null).
- Caption baseline (Doerig 2025). B_caption vs B_brain vs B_joint. Brain unique = B_joint - B_caption + paired bootstrap.
- Naming retreat. Paper title 에서 "foundation model" 자제.


## Phase Status

| Phase | Week | Track | 상태 |
|---|---|---|---|
| Phase 1 Foundation (frozen probe + padding ablation + SwiFT variants) | W1-6 | (사전 검증) | **✅ 완료** |
| Phase 2 통합 학습 (4 architecture + brain-only 4 method + Cat34) | W7-12 | (사전 검증) | **✅ 측정 완료**. Universal code framing 으로 pivot |
| Phase 3a BrainVLM | W13-15 | Track C supp | **🔄 Fold 1 완료, parsing fix** |
| Phase 3b Track A (SSL pretrain 1+2+3 + LoRA adaptation) | W15-20 | Track A main | **🆕 main path** |
| Phase 3c Track B (Brain+Video framework + task 재설계, cross-dataset) | W15-18 | Track B main | **🆕 main path** (병행) |
| Phase 4 Synthesis + submission | W19-24 | (통합) | 대기 |
| Phase 5 **Future Extensions** (Context-aware text modulation + Individual differences) | post-submission | v5 candidates | 🔮 추후 |


## Git workflow

- Branch `v4_20260602_perlmutter` (active)
- 새 framing 으로 pivot 시 새 branch
- Paper 단계에서 main merge


## Repository Map

| 경로 | 내용 |
|---|---|
| `docs/masterplan_v2.md` | Forward plan v4 final |
| `reports/phase{1,2}_wrapup/`, `reports/phase1_foundation.md` | Phase 1/2 progress |
| `data/stimulus_features/` | EmoViS symlinks |
| `data/independent/` (NEW) | Emo-FilM / StudyForrest / NNDb / Affective Videos |
| `data/{horikawa_split, *_binary_subset, feelin_canonical_stimuli}.csv` | Splits |
| `code/bfm_embeddings/` | BFM extraction |
| `code/probes/` | Tier 1 + frozen probe |
| `code/phase2/` | Phase 2 4 architecture + brain-only (Track B reuse) |
| `code/brainvlm/` | Phase 3a (Track C supp) |
| `code/ssl_pretrain/` (NEW, Track A) | Subject-invariant + multi-source masked + brain-stimulus contrastive |
| `code/cross_dataset/` (NEW) | LoRA, emotion-text space, ComBat, evaluators, OV-MER local LLM |
| `code/analysis/` | Padding ablation, multi-BFM probe, figure |
| `output/embeddings/` | BFM .pt |
| `results/{padding_ablation, main_grid_3bfm, phase1, phase2, brainvlm}/` | 결과 |
| `results/phase3_universal_code/` (NEW) | Track A + B 결과 |
| `Paper/framework_*.md`, `methodology.md` | Narrative + methodology |
| `notes/{benchmark_design, project_decisions}.md` | Matrix + decision log |
| `reference/{datasets, task, papers, code_resources, training_strategy}.md` | Reference |
