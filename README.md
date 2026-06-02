# FEELIN

**Universal Emotion Code in Naturalistic Brain Data**

(내부 / repo / 연구실 정체성 이름은 Brain Foundation Model for Emotion-aware Experience Learning In Naturalistic Data 로 유지. Paper title 에서는 "Universal Emotion Code in Naturalistic Brain Data" 또는 "Transferable Emotion Brain Foundation Model" 로 표현. 2026-06-02 naming dual-track.)


## 한 줄 요약

Brain 에 paradigm, label taxonomy, subject 의 surface variation 을 가로지르는 universal emotion code 가 존재하는지를 multi-source naturalistic emotion fMRI 의 SSL pretrain + adaptation 으로 학습하고 검증한다.


## Big Question (v4 final, 2026-06-02)

> Brain 에 paradigm, label taxonomy, subject 의 surface variation 을 가로지르는 *universal emotion code* 가 존재하는가? Multi-source naturalistic emotion fMRI 의 adaptation 으로 그 universal code 를 학습하고 검증할 수 있는가?

핵심 scientific bet. Wager-style universal pain signature 시도의 emotion 판. Affective neuroscience 의 미해결 질문 (universal vs idiosyncratic emotion representation) 에 falsifiable evidence 제공.

"Brain 이 video 를 이겨야" 전제 없음. Phase 1-2 의 measurement 가 group-level V/A 는 video 가 saturate 함을 확정했음 (자세히 아래 [측정 결과]). Universal code 가 존재한다면 group-level emotion attribute 가 아니라 invariance / cross-dataset preservation 의 axis 에 있어야 함.


## Sub-claims (falsifiable)

1. Universal code 가 존재한다면 multi-source pretrain 의 representation 이 single-source pretrain 보다 cross-dataset transfer 에서 더 invariant.
2. Universal code 는 brain 의 특정 ROI / network 에 localize 됨 (Cowen 2020 transmodal 가설과 align 또는 disagree).
3. Universal code 는 subject-invariant SSL 후 같은 stim 의 다른 subject representation 이 alignment.
4. (Null) 위 세 metric 모두 acquisition floor 안 → "universal code 없음" 결론, negative result paper.


## 2 Main Track + 1 Supplementary

| Track | 답하는 sub-Q | Universal code 측정 |
|---|---|---|
| **Track A (main). BFM SSL pretrain + LoRA adaptation** | Multi-source SSL 이 emotion-relevant invariance 를 emerge 시키는가? Subject-invariant / multi-source / stimulus-contrastive SSL 의 marginal contribution? | Pretrain 후 representation 의 cross-dataset invariance metric (RSA, ROI-wise transfer) |
| **Track B (main). Brain+Video framework + task 재설계** | Brain unique contribution 의 universal component? Video 가 못 잡는 brain emotion variance 의 cross-dataset preservation? | Joint - video baseline = brain unique. 그 brain unique 의 cross-dataset RSA / alignment |
| **Track C (supplementary). BrainVLM generative path** | Universal code 가 generative 표현 가능한가? | Phase 3a fold 1 결과 + inference parsing fix. Supplementary figure 만 |

**왜 BrainVLM 이 supplementary 인가**. (a) LLM 의 visual semantic bias 가 brain invariance 측정을 가림, (b) Generation noise 가 reliability 낮춤, (c) Phase 3a inference 자체 약함 (V_reg r = NaN, MAE 2.55, scale mismatch), (d) Multi-source 확장에 자원 부담 큼. Risk 대비 evidence 약해서 supplementary.

Track A + Track B 의 **converging evidence** 가 paper 의 강점.


## Track A SSL pretrain 후보 (priority 순)

자원 manageable. 우선순위 1 (둘 다 main, 반드시) + 우선순위 2 (main, 가능하면) + 우선순위 3 (optional).

### Priority 1 (main)

**(1) Subject-invariant SSL**. 같은 video 를 본 5 subject 의 brain response 가 서로 비슷해지도록 contrastive 학습.
- Stim k 의 subject A brain (brain_Ak) ↔ subject B brain (brain_Bk) 의 cosine ↑
- 다른 stim m 의 brain_Am ↔ brain_Ak 의 cosine ↓
- InfoNCE contrastive
- Universal code 연결. Subject 간 invariance = universal code 의 정의. 학습 후 representation 의 subject alignment 가 직접 evidence.
- 자원 GPU 며칠.

**(2) Multi-source SSL (masked autoencoder, BrainLM-style)**. Horikawa + Emo-FilM + StudyForrest + Affective Videos 의 fMRI 모두 사용. Brain 의 일부 ROI / time 가리고 예측.
- 450 ROI 중 30% mask → 나머지 70% 로 가린 부분 예측. MSE loss
- 4 dataset 같은 model. Dataset 별 헤더
- Universal code 연결. Paradigm 간 invariance evidence. Single-source vs multi-source 의 invariance 차이가 multi-paradigm 존재 증거
- 자원 GPU 1-2 주.

### Priority 2 (main, 가능하면)

**(3) Brain-stimulus contrastive (TRIBE-style)**. Brain representation 과 video representation (V-JEPA2 / CLIP) 의 alignment.
- Brain_k encoder output ↔ Video_k V-JEPA2 feature 의 cosine ↑. 다른 stim ↓
- Universal code 연결. Universal code 가 stimulus-driven 이면 alignment emerge. Stimulus 와 분리된 brain unique 면 alignment 안 됨. 두 경우의 분리 측정
- 자원 GPU 며칠.

### Priority 3 (optional)

**(4) Curriculum pretrain**. Resting (Brain-JEPA prior) → naturalistic movie (HCP 7T) → emotion-aware (Horikawa Cowen) 의 3-stage. Stage 별 prior contribution ablation.

**(5) Distillation**. 큰 BFM 의 representation 을 작은 specialized model 로. 부수적.


## Target hierarchy (V/A 강등, multi-dim 승격)

| Tier | Target | 비고 |
|---|---|---|
| **Primary** | Cross-dataset emotion-text alignment + Cowen 34-cat multilabel + 14-dim regression + OV description retrieval | Universal code 의 invariance 측정 |
| **Reference (floor)** | V/A binary + regression | Phase 1-2 에서 video saturate 확정. Floor only |


## Cross-dataset evaluation 4 전략

1. **Shared text-embedding zero-shot (main)**. brain → emotion-text space, native label 이름만으로 zero-shot retrieval
2. **Label-space intersection (안전)**. target dataset 의 축만 잘라
3. **MLLM universal annotator**. OV-MER pipeline 의 local LLM (Qwen2.5-72B / Llama-3.3-70B) frozen artifact
4. **Representational alignment (label-free)**. RSA / ISC ceiling


## Build recipe

5 subj × 2185 stim 으론 from-scratch FM 불가. **Pretrained brain backbone + 소수 multi-source SSL pretrain + emotion-text space adaptation** 이 honest scope.

```
fMRI ─► 450-ROI parcel (Schaefer-400 + Tian-50)
        │
        ▼ Brain-JEPA backbone (pretrained on ABCD resting)
        │
        ▼ Track A SSL pretrain
            (1) subject-invariant contrastive
            (2) multi-source masked AE
            (3) brain-stimulus alignment (optional)
        │
        ▼ LoRA adaptation
        │
        ▼ projection
        z_emo ─► frozen emotion-text embedding space (sentence-transformer / CLIP-text)
                  target = embed(Cowen 34-cat + 14-dim or OV description)
                  loss  = contrastive InfoNCE + 보조 regression + caption baseline delta
        │
        ▼ multi-source pooling
        ▼ 평가 (freeze 후)
            Track A invariance metric (subject align, paradigm align)
            Track B brain unique cross-dataset RSA (Brain+Video framework reuse)
            Track C BrainVLM parsing fix (supplementary)
```


## Brain encoder 후보

| Backbone | 역할 | 상태 |
|---|---|---|
| Brain-JEPA | ROI default | 추출 완료 |
| SwiFT (NewE96 + 5 변종) | 4D volume | NewE96 완료, 변종 진행 중 |
| NeuroSTORM | 4D volume | 추출 완료 |
| BrainLM | 제외 | 490 TR × A424 atlas 고정 → Horikawa 비호환 |


## Independent dataset

| Dataset | Subj × Stim | Label | Role |
|---|---|---|---|
| Horikawa | 5 × 2185 (1 min clips) | Cowen 34-cat behavioral consensus | Base, Track A pretrain, Track B testbed |
| Emo-FilM (Cordoni 2025) | 30 × 14 films | 13 discrete + 42 CPM, 1 Hz | Track A multi-source + cross-dataset test |
| StudyForrest | 20 × Forrest Gump 2h | 8 portrayed + V/A | Track A multi-source + cross-dataset test |
| NNDb (Aliko 2020) | 86 × 10 movies | 없음 | 전략 4 RSA (Appendix) |
| Affective Videos (ds000205) | 11 × 32×4 | V/A | Track A multi-source |


## 측정 결과 (Phase 1 + Phase 2, evidence 보존)

### Phase 1 (frozen probe)

- ROI Schaefer400+Tian50 mean (linear, pooled). V_binary AUROC 0.7889 ± 0.0119
- Best BFM (Brain-JEPA resting zero). V_binary 0.7402 ± 0.0365
- Best video (CLIP_pretrained). V_binary 0.9708
- 결론. ROI mean > all BFM. Brain 정교화가 group-level emotion 에 effect 없음.

### Phase 2 (trained integration)

V_binary AUROC.
- D late fusion 0.9718, A token transformer 0.9670, B cross-attention 0.9663, C contrastive joint 0.9606
- Phase 1 CLIP 0.9708 → D joint Δ vs CLIP = +0.001 (noise)
- Brain-only best (multitask) 0.7235

V_reg Pearson r. A token transformer 0.7628 → CLIP 0.7645 = -0.002.
A_binary AUROC. D late fusion 0.8025 → CLIP 0.8003 = +0.002.

**결론**. 4 fusion architecture 모두 video baseline 위 향상 없음. Brain group-level emotion label 추가 contribution = 0.

### Phase 3a (BrainVLM)

Fold 1 학습 완료 (loss 0.151). Inference V_reg r = NaN, MAE 2.55. Scale mismatch. Track C supplementary 로 demote.

### 의의 (왜 universal code framing 으로 갔는가)

Group-level V/A 는 video 가 saturate. Brain unique signal 은 (a) multi-dim geometry, (b) transmodal localization, (c) subject-conditioned variability, (d) cross-dataset transfer 의 4 축에서만 가능. 그 중 (a)(b)(d) 의 공통 motif = invariance. **Universal emotion code 가 그 invariance 의 scientific 표현.**


## Evaluation protocol

- 5-fold stim-stratified CV (`data/horikawa_5fold.csv`)
- 각 fold k: test=k, val=(k%5)+1, train=나머지 3
- 6 task × 2 head × (BFM 2 mode) × 1 seed (screening) / 3 seed (final)
- Cross-dataset probe 는 ComBat harmonization (Fortin 2018) + acquisition null baseline 필수
- Track A SSL pretrain 의 invariance metric (subject alignment + paradigm alignment) 도 같은 fold 위에

### Critic-informed control

- Acquisition control. ComBat + phase-scrambled null + trivial ROI mean null. Transfer Δ > 2σ × max(null) 만 의미.
- Caption baseline (Doerig 2025 위협 대응). Qwen-VL caption → text embedding probe. Brain unique variance = B_joint - B_caption + paired bootstrap p.
- Naming retreat. Paper title 에서 "foundation model" 명사 자제, 내부 이름 FEELIN 유지.


## Phase Status (6 month plan)

| Phase | Week | Track | 상태 |
|---|---|---|---|
| Phase 1 Foundation (frozen probe + padding ablation + SwiFT variants) | W1-6 | (사전 검증) | **✅ 완료** |
| Phase 2 통합 학습 (4 architecture A/B/C/D + brain-only 4 method) + Cat34 | W7-12 | (사전 검증) | **✅ 측정 완료**. joint 가 video saturate, brain added value 0. Universal code framing 으로 pivot |
| Phase 3a BrainVLM (Option A L1/L2/L3) | W13-15 | Track C supplementary | **🔄 Fold 1 완료, parsing fix 만 추가** |
| Phase 3b Track A (SSL pretrain 1+2+3 + LoRA adaptation) | W15-20 | Track A main | **🆕 v4 main path** |
| Phase 3c Track B (Brain+Video framework + task 재설계, cross-dataset transfer) | W15-18 | Track B main | **🆕 v4 main path** (병행) |
| Phase 4 Synthesis + submission | W19-24 | (통합) | 대기 |

자세한 phase 별 task / go-no-go / agent review 는 [`docs/masterplan_v2.md`](docs/masterplan_v2.md).
Phase 1 보고서. [`reports/phase1_wrapup/main.pdf`](reports/phase1_wrapup/main.pdf).
Phase 2 보고서. [`reports/phase2_wrapup/main.pdf`](reports/phase2_wrapup/main.pdf).
Decision log. [`notes/project_decisions.md`](notes/project_decisions.md) 2026-06-02.


## Git workflow

- Branch `v4_20260602_perlmutter` (active)
- 새 framing 으로 pivot 필요하면 새 branch
- Paper 단계에서 main 으로 merge


## Repository Map

| 경로 | 내용 |
|---|---|
| `docs/masterplan_v2.md` | Forward plan v4 final |
| `reports/phase{1,2}_wrapup/`, `reports/phase1_foundation.md` | Phase 1/2 progress + PDF |
| `data/stimulus_features/` | EmoViS symlinks |
| `data/independent/` (NEW, Phase 3b) | Emo-FilM / StudyForrest / NNDb / Affective Videos (OpenNeuro) |
| `data/{horikawa_split, *_binary_subset, feelin_canonical_stimuli}.csv` | Splits + V/A binary + canonical stim |
| `code/bfm_embeddings/` | BFM extraction |
| `code/probes/` | Tier 1 ROI feature + unified frozen probe |
| `code/phase2/` | Phase 2 4 architecture + 4 brain-only method (Track B framework reuse) |
| `code/brainvlm/` | Phase 3a BrainVLM (Track C supplementary) |
| `code/ssl_pretrain/` (NEW, Phase 3b Track A) | Subject-invariant SSL + multi-source masked AE + brain-stimulus contrastive |
| `code/cross_dataset/` (NEW, Phase 3b/3c) | LoRA adaptation, emotion-text space, ComBat, W refit, caption baseline, OV-MER local LLM, 4 evaluators |
| `code/analysis/` | Padding ablation, multi-BFM probe, figure |
| `output/embeddings/` | BFM .pt (proper mean) |
| `results/{padding_ablation, main_grid_3bfm, phase1, phase2, brainvlm}/` | Probe / training 결과 |
| `results/phase3_universal_code/` (NEW) | Track A invariance + Track B cross-dataset 결과 |
| `baseline/` | BFM checkpoints |
| `external/Brain-JEPA/`, `external/NeuroSTORM/` | Vendored model code |
| `Paper/framework_*.md`, `methodology.md` | Canonical narrative + methodology |
| `notes/{benchmark_design, project_decisions}.md` | Dataset matrix + decision log |
| `reference/{datasets, task, papers, code_resources, training_strategy}.md` | Reference |
