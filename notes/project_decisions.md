# FEELIN Project Decisions

## 2026-05-08

### Project Name

Confirmed working name: **FEELIN**.

Formal subtitle:

**SwiFT-first Emotion Representation Learning and Inference in Naturalistic fMRI**

### Core Direction

FEELIN will compare:

1. SwiFT-first emotion adaptation.
2. HCP movie-watching pretraining.
3. TRIBE v2-style stimulus-brain-emotion alignment.

### Important Clarification

TRIBE is an encoding model: stimulus to fMRI response. It should not be described as the same kind of model as SwiFT, BrainLM, Brain-JEPA, or NeuroSTORM.

TRIBE v2 is useful as a multimodal teacher/alignment component. It should not replace SwiFT as the default brain backbone.

### Two-Month Constraint

The project has roughly two months. Therefore:

- Start with baselines and frozen probes.
- Use parcellated or compact time-series data before raw 4D volume training.
- Treat expensive end-to-end 4D training as optional, not the first milestone.
- Keep all results comparable through shared splits and metrics.

### Setup Workspace

`setup` should focus on:

- dataset inventory,
- target construction,
- simple baselines,
- pretrained model availability,
- deciding which downstream target is most stable.

---

## 2026-05-16

### Phase 1 Settings (Confirmed)

**Stratification & Split**
- Split: stimulus-stratified across all 5 subjects (같은 stimulus는 모든 subject에서 같은 split)
- Stratification basis: **V quartile × A quartile multilabel stratified split** (8 label, iterative-stratification)
- Train / Val / Test = 80 / 10 / 10 by stimulus
- Stimulus 0 (resting fMRI, 16 TR) 은 metadata 없음, canonical 2,185 에서 자동 제외

**Binary Task Definition (L0)**
- V binary: V Q4 (top 25%) vs V Q1 (bottom 25%), middle Q2+Q3 50% 제외 → ~1,092 stimuli
- A binary: A Q4 vs A Q1, middle 50% 제외 → ~1,092 stimuli
- 이유: median split의 boundary noise 문제 + 뇌 반응이 valence에 quadratic (extreme 더 강한 신호)
- Stratification (모든 자극 포함) 과 binary task (extreme group only) 는 다른 목적이므로 분리

**Training Mode (Phase 1 모두 진행)**
- Pooled: 1 model, 5 subjects 8,740 samples 통합 → universal emotion code 측정
- Per-subject: 5 models, 각자 1,748 samples → subject별 성능 평균±std
- 두 비교 자체가 결과

**Input & Normalization**
- Brain-JEPA ROI atlas: Schaefer 400 17-network + Tian S3 50 = 450 (pretrained model 제약)
- NeuroSTORM: 4D volume 96×96×96 (model expectation)
- dtype: float32 (정확도 우선, embedding 저장 크기 33MB로 부담 없음)
- Normalization: **Robust scaling** (median/IQR per ROI). outlier에 강함, Brain-JEPA pretrain 동일 방식
- Normalization 순서: pad → normalize (코드 단순, 영향 거의 동일)
- Normalization source: `normalization_params.npz` (전체 데이터 기반 사전 계산)

**Stimulus Inclusion**
- 전체 2,185 사용 (T별 robustness check 별도)
- 누락 없음 확인됨 (ROI 5 subjects 전부, volumetric 2,196 stimuli 전부)

**Padding (3 conditions 모두 추출하여 비교)**
- A. Replicate last frame (자극 마지막 신호 유지)
- B. Zero pad (baseline 0 가정)
- C. Mean → replicate (5 TR 평균 1 vector → 20 복제, spatial-only control)
- 이유: 우리 dataset에서 71.6% 자극이 T=5 (75% padding). DL fMRI 분야에 standard padding 전략 없음.
  Brain transformer 모델들이 attention mask 사용 안 함 → padding 방식이 결과에 직접 영향.
  3 조건 비교로 padding 영향 측정하고 어느 게 emotion decoding에 적합한지 결정.
- Spatial padding (NeuroSTORM): background-zero 유지 (74,91,81 → 96,96,96)

**Head (Linear + MLP 둘 다)**
- Linear probe: ridge / logistic / multinomial / multi-output ridge (task type별)
- MLP: 2-layer, hidden 256, ReLU, dropout 0.3
- 이유: Linear는 frozen BFM 평가 표준 (representation quality 직접 측정).
  MLP는 capacity 비교 (linear로 안 보이는 signal이 MLP로 잡히면 representation은 있지만 non-linearly separable)

**Phase 1 전체 scope**
- 3 BFM × 2 init × 3 padding = 18 embedding sets
- × 5 task level × 2 head × 2 mode = 360 head training runs
- + Statistical floor 4종 × 5 task

### Subject Block as Separate Axis (deferred)

Subject-conditional projection (TRIBE v2 식 subject block, Défossez et al. 2023 inspired) 은 매력적이지만 **emotion biomarker discovery와 잠재적 충돌**이 있어 별도 축으로 분리한다.

**우려:**
Subject block이 강할수록 shared trunk가 "어떤 brain feature가 emotion-relevant"를 학습하지 않고, 단순히 subject identity → emotion target 매핑을 학습할 위험. 5 subjects 같은 작은 N에서 특히 위험. Universal emotion neural signature (Wager 식 biomarker) 발견이 목표라면 부적절.

**Phase 1 결정:**
Subject block 사용하지 않음. Pooled training (BFM embedding만 입력, subject identity는 입력에서 제외).

**별도 축으로 보류:**
Subject block은 "personalized emotion decoding" 트랙으로 분리. Phase 2 후반에 별도 ablation:
- Subject block ON vs OFF 비교
- Shared trunk만 떼서 frozen probe → cross-task transfer
- Subject block weight entropy 분석 (nuisance vs signal 분리도)

**기록 위치:**
이 결정은 `Paper/methodology.md` Phase 2 Track A0 (architecture exploration) 으로도 반영.

---

## 2026-06-01 (revised, v4 final)

### Scientific Question 재정의 (v4 framing, labserver-base + critic-informed)

교수님 면담 후 "scientific question 이 뭐냐, multi-dim representation 학습 후 independent dataset 평가 전략은 무엇인가" 라는 질문에서 출발. Web search (Emo-FilM, OV-MER, fMRI FM survey) + emovi-method-critic 적대적 검토 + labserver branch (`reference/v4_history_labserver_framing.md`) 의 더 정확한 framing 통합. 사용자가 "SQ1 의 'video baseline 을 통계적으로 넘는가' framing 이 잘못, sub-question 들이 너무 dataset-specific" 이라고 지적 → labserver framing 채택, v3 의 individual difference 방향과 v4 (initial draft) 의 SQ1-5 폐기. 새 framing 은 모두 dataset-agnostic representation question.

### Big Question (final)

> Naturalistic fMRI 로부터 학습한 multi-dimensional emotion brain representation 이, 단일 dataset 과 label taxonomy 에 종속되지 않고 새로운 subject, 자극, emotion 어휘로 transfer 되는 emotion brain foundation model 이 될 수 있는가?

### 5 Sub-questions (전부 dataset-agnostic representation question)

1. **SQ1 Transfer (main)**. Horikawa 에서 학습한 brain emotion representation 이 retrain 없이 새 dataset / subject / taxonomy 로 일반화되는가? (zero-shot + few-shot scaling, acquisition-controlled)
2. **SQ2 Supervision richness**. Scalar V/A vs Cowen 34-cat vs 14-dim vs OV description 중 어느 supervision 이 더 transferable 한 representation 을 만드는가?
3. **SQ3 Representation geometry**. 학습된 brain emotion space 가 Horikawa 2020 의 구조 (high-dim, category > dimension, transmodal 분산) 를 복원하는가? RSA / CKA / W refit.
4. **SQ4 Data efficiency**. Pretrained brain emotion FM 이 새 dataset 에서 from-scratch 대비 몇 배 적은 label 로 같은 성능에 도달하는가?
5. **SQ5 Where (label-free)**. Emotion 정보가 brain 의 어디에 있는가? Network-restricted probe + ISC ceiling + caption baseline 대비 brain-only added variance.

### Target hierarchy (multi-dim 승격, V/A 강등)

- **Primary** = Cowen 34-category (multilabel + soft) + Cowen 14-dimension + OV emotion-text embedding
- **Reference (floor / sanity)** = V/A binary + regression (Phase 1-2 에서 video 가 saturate 한 axis 임이 확정. Floor only.)

### Build recipe (foundation 의 정직한 출처)

5 subj × 2185 stim 으로는 emotion brain FM 을 from-scratch pretrain 불가. **대규모 pretrained brain backbone + 대규모 pretrained emotion-language space 의 emotion-transferable adaptation**.

```
fMRI ─► 450-ROI parcel (Schaefer-400 + Tian-50)
        │
        ▼ Brain-JEPA backbone + LoRA (resting → emotion reshape)
        │
        ▼ projection
        z_emo ─► frozen emotion-text embedding space (sentence-transformer / CLIP-text)
                  target = embed(Cowen 34-cat + 14-dim 문장화 또는 OV description)
                  loss  = contrastive InfoNCE + 보조 regression + caption baseline delta
        │
        ▼ multi-dataset pooling (Horikawa + Emo-FilM + Koide-Majima + Affective Videos)
        ▼ 평가 (freeze 후): SQ1-5
```

### Cross-dataset evaluation 4 전략

1. **Shared text-embedding zero-shot (main)**. brain → emotion-text space, native label 이름만으로 zero-shot retrieval
2. **Label-space intersection (안전)**. target dataset 의 축만 잘라
3. **MLLM universal annotator**. OV-MER pipeline 의 local LLM (Qwen2.5-72B / Llama-3.3-70B) frozen artifact
4. **Representational alignment (label-free)**. RSA / ISC ceiling

### Phase 1-2 measurement 가 framing 의 근거

- Phase 1 frozen probe. ROI mean V_binary AUROC 0.7889 > all BFM (best 0.7402) ≫ Video CLIP 0.9708
- Phase 2 trained integration. D late fusion V_binary 0.9718, CLIP-only 0.9708 → Δ = +0.001 (noise). 4 fusion architecture 모두 video baseline 못 넘음. Brain group-level emotion label 추가 contribution = 0
- Phase 3a BrainVLM. Fold 1 완료, inference V_reg r = NaN, MAE 2.55. Supplementary 로 demote.
- **의의**. Brain unique signal 은 multi-dim geometry, transmodal localization, subject-conditioned variability, cross-dataset transfer 의 4 축에서만 가능. v4 SQ1-5 가 이 4 축 측정.

### 옛 frame 명시적 탈피

- ❌ "Brain + video fusion 으로 video 를 넘는다" (Phase 2 결과로 falsified)
- ❌ BrainVLM token integration 을 main path 로
- ❌ 4 fusion architecture (A/B/C/D joint) 비교가 main contribution
- ❌ "Brain 이 video 를 이긴다" framing 자체

대신.

- ✅ Brain backbone (Brain-JEPA + LoRA) 의 emotion-specialized adaptation
- ✅ Multi-dim emotion-text space (sentence-transformer / CLIP-text) 와 contrastive alignment
- ✅ Cross-dataset / cross-taxonomy zero-shot transfer
- ✅ Caption baseline 대비 brain unique variance

Video 는 옵션 teacher (contrastive partner, caption baseline, RSA reference) 로만.

### v4 final 이 v3 (2026-05-19) 와 v4-initial-draft (2026-06-01 morning) 를 어떻게 대체하는가

| 측면 | v3 (2026-05-19) | v4-initial-draft (오전) | v4 final (저녁, labserver-base) |
|---|---|---|---|
| Big Q | 4 architecture × 3 encoder 중 best 비교 | "video baseline 을 통계적으로 넘는가" + "transfer 되는가" 두 part | "transfer 되는 emotion brain FM 이 될 수 있는가" (single core) |
| SQ1 framing | Architecture × encoder selection | "video baseline 을 통계적으로 넘는가" (잘못된 framing) | "transfer 되는가" (zero-shot + few-shot scaling) |
| Target hierarchy | 모든 task 동등 | V/A + Cowen 34-cat 동등 | V/A 강등 to floor/sanity, Cowen 34-cat / 14-dim / OV-text 승격 |
| Build recipe | 4 architecture option (LLM token / cross-attn / contrastive / late fusion) | 4 architecture × 3 encoder + ComBat | brain backbone (Brain-JEPA + LoRA) + emotion-text space (sentence-transformer / CLIP-text) + adaptation |
| Cross-dataset 전략 | (없음) | S1 Cowen W projection + S2 ComBat probe + S5 zero-shot | (1) shared text-embedding zero-shot main + (2) intersection + (3) MLLM annotator + (4) RSA |
| BrainVLM 위상 | Phase 3a main path | Phase 3a main path (유지) | "옛 frame, video teacher 로 demote, supplementary" |

### Critic 7-hit 과 v4 final 의 대응

| Critic hit | v4 final 의 대응 위치 |
|---|---|
| 1. Q2 tautological | SQ3 W refit + mediator regression |
| 2. Acquisition confound (Sripada 2020) | SQ1 ComBat + acquisition null baseline + 2σ prespecify |
| 3. 5 subj power | Open-vocab 강등 (case study). Subject-level bootstrap CI 명시 |
| 4. FM naming bias (Bommasani 2021) | Paper retreat ("Transferable Emotion Brain Foundation Model" / "Cross-dataset Emotion Brain Encoder"), internal FEELIN 유지 |
| 5. Caption baseline 부재 (Doerig 2025) | SQ5 variance partitioning |
| 6. OV-MER GPT-3.5 dependency | 전략 3 local LLM (Qwen2.5-72B / Llama-3.3-70B) frozen artifact |
| 7. Cowen 34-cat transmodal 한정 (Cowen 2020) | SQ1 ROI-wise transfer matrix |

### Independent dataset evaluation stack (final)

- **Main**. 전략 1 shared text-embedding zero-shot + 전략 2 label-space intersection (ComBat 적용) on Emo-FilM, StudyForrest
- **Confound control**. 전략 4 RSA + SQ5 caption baseline variance partitioning
- **Supplementary**. 전략 3 OV-MER bridge (local LLM frozen) on Horikawa + Emo-FilM + StudyForrest

### Naming dual-track (final)

- **내부 / project / repo / slack** = "FEELIN" 유지 (Brain Foundation Model for Emotion-aware Experience Learning In Naturalistic Data, 교수님과 연구실 정체성)
- **Paper title / abstract** = "foundation model" 명사 직접 사용 자제. 후보.
  - "Transferable Emotion Brain Foundation Model from Naturalistic fMRI"
  - "Cross-dataset Emotion-aware Brain Encoder via Emotion-Text Alignment"
  - "Adapting Brain Foundation Models to Multi-dimensional Emotion Representation"

### 변경된 후속 작업 (v4 final)

- ✅ `docs/masterplan_v2.md` v4 final 전면 재작성 완료 (Big Q + 5 SQ + build recipe + 4 cross-dataset 전략 + go-no-go + agent review + risk register + critic 7-hit self-check)
- ✅ `Paper/framework_KR.md` / `framework_EN.md` v4 final framing prepend 완료
- ✅ `CONTEXT_FEELIN.md` / `README.md` / `README_KR.md` v4 final 동기화 완료
- ✅ `notes/project_decisions.md` 이 entry 가 final 결정
- ⏳ 다음 step (사용자 결정 필요).
  - (a) `code/cross_dataset/` 의 Brain-JEPA + LoRA adaptation 학습 코드 작성
  - (b) Emo-FilM OpenNeuro 다운로드 + BIDS 검증
  - (c) `Paper/methodology.md` 도 v4 build recipe 에 맞춰 update
  - (d) ONBOARDING.md, CODEX.md 동기화 검토

---

## 2026-06-02 (v4 final, universal emotion code)

### Branch
`v4_20260602_perlmutter`. 모든 v4 final 작업이 여기서. Main 으로의 merge 는 paper 단계.

### Driver
- 2026-06-01 의 v4-revised (transfer-centric) draft 를 사용자가 reject. "Video baseline 을 통계적으로 넘는가" framing 이 잘못됐다 (engineering question, scientific 아님). "Dataset-specific SQ" 도 잘못됐다 (모든 SQ 는 dataset-agnostic representation question 이어야 함).
- 사용자의 "FM 과 연결되는 깊은 science question" 요구.
- 사용자의 "BFM + Brain+Video + BrainVLM 세 측면 모두 진행" 결정.
- 사용자의 "소수 데이터로 pretrain 해서 성능 높이는 방법" 검토 요구.
- 사용자의 "BrainVLM feasibility 의심" 의 정직한 평가.
- 사용자의 "branch 기반 git workflow" 결정.

### Big Question (final)

> Brain 에 paradigm, label taxonomy, subject 의 surface variation 을 가로지르는 universal emotion code 가 존재하는가? Multi-source naturalistic emotion fMRI 의 adaptation 으로 그 universal code 를 학습하고 검증할 수 있는가?

핵심 scientific bet. Wager-style universal pain signature 시도의 emotion 판. Affective neuroscience 의 미해결 질문 (universal vs idiosyncratic emotion representation) 에 falsifiable evidence.

### Sub-claims (falsifiable)

1. Multi-source pretrain invariance. Universal code 가 있다면 multi-source > single-source 의 cross-dataset invariance.
2. ROI localization. Universal code 는 특정 ROI / network 에 localize (Cowen 2020 transmodal 가설 비교).
3. Subject-invariant alignment. Subject-invariant SSL 후 같은 stim 의 다른 subject 의 representation alignment.
4. Null. 위 모두 acquisition floor 안 → negative result paper.

### 2 Main Track + 1 Supplementary

- **Track A (main). BFM SSL pretrain + LoRA adaptation**. Universal code 의 measurement machinery.
- **Track B (main). Brain+Video framework (Phase 2 reuse) + task 재설계**. Brain unique 의 cross-dataset preservation.
- **Track C (supplementary). BrainVLM**. Phase 3a fold 1 + parsing fix 만. 본격 진행 안 함.

### Track A SSL pretrain 후보 (5, priority)

**Priority 1 (둘 다 main, 반드시)**
- (1) Subject-invariant SSL. 같은 video 의 5 subject brain response 의 contrastive alignment. Universal code 의 subject invariance evidence.
- (2) Multi-source SSL (masked autoencoder). 4 dataset 의 fMRI 의 30% ROI mask 후 MSE 예측. Paradigm invariance evidence.

**Priority 2 (main, 가능하면)**
- (3) Brain-stimulus contrastive (TRIBE-style). Brain ↔ video alignment. Universal code 의 stimulus-driven 측면.

**Priority 3 (optional)**
- (4) Curriculum pretrain (resting → naturalistic → emotion 3-stage)
- (5) Distillation

### BrainVLM 의 정직한 평가 (Track C supplementary 로 demote)

(a) LLM 의 visual semantic bias 가 brain invariance 측정 가림 (Phase 2 video saturate 와 같은 함정).
(b) Generation noise 가 reliability 낮춤.
(c) Phase 3a inference 자체 약함 (V_reg r = NaN, MAE 2.55, scale mismatch).
(d) Multi-source 확장 자원 부담 큼.

본격 Track 으로 진행은 risk 대비 evidence 약함. Supplementary 로.

### Build recipe

```
fMRI → 450-ROI parcel
     → Brain-JEPA backbone (pretrained ABCD resting)
     → Track A SSL pretrain ((1) subject-invariant + (2) multi-source masked + (3) brain-stimulus alignment)
     → LoRA adaptation
     → projection → frozen emotion-text embedding space
     → multi-source pooling
     → 평가
```

Foundation 의 출처 = brain backbone (수만 subject pretrained) × emotion-text space (수천 emotion 개념) × multi-source SSL pretrain. FEELIN 기여 = universal code 의 measurement methodology.

### Cross-dataset evaluation 4 전략

1. Shared text-embedding zero-shot (main)
2. Label-space intersection (안전)
3. MLLM universal annotator (OV-MER local LLM frozen artifact)
4. RSA / ISC ceiling (label-free)

### Phase 1-2 measurement 가 framing 의 근거

- Phase 1. ROI mean V_binary AUROC 0.7889 > all BFM (0.7402) ≫ Video CLIP 0.9708
- Phase 2. D late fusion 0.9718, CLIP 0.9708 → Δ +0.001 (noise). 4 fusion architecture 모두 video baseline 못 넘음
- Phase 3a. Fold 1 완료, V_reg r = NaN, MAE 2.55. Track C supplementary
- 결론. Group-level V/A 는 video saturate. Brain unique signal 은 invariance 의 4 축에서만 가능. Universal code 가 그 invariance 의 scientific 표현.

### 옛 frame 명시적 탈피

- ❌ "Brain + video fusion 으로 video 를 넘는다"
- ❌ BrainVLM token integration 을 main path 로
- ❌ 4 fusion architecture 비교가 main contribution
- ❌ "Brain 이 video 를 이긴다" framing 자체
- ❌ Dataset-specific SQ (transfer-centric draft)

대신 universal emotion code 의 존재 검증.

### Naming dual-track (final)

- 내부 / repo / 연구실 = FEELIN (Brain Foundation Model for Emotion-aware Experience Learning In Naturalistic Data)
- Paper title 후보. "Universal Emotion Code in Naturalistic Brain Data via Multi-source Self-supervised Adaptation" / "Transferable Multi-dimensional Emotion Representation from Naturalistic fMRI" / "Cross-dataset Emotion-aware Brain Encoder via Emotion-Text Alignment"

### v4-revised (2026-06-01 오후) → v4 final (2026-06-02) 비교

| 측면 | v4-revised (2026-06-01) | v4 final (2026-06-02) |
|---|---|---|
| Big Q | "Transfer 되는가" (engineering) | "Universal emotion code 가 존재하는가" (scientific) |
| SQ structure | 5 SQ (Transfer / Supervision / Geometry / Data efficiency / Where), dataset-specific | 2 main track + 1 supp + 4 falsifiable sub-claim, dataset-agnostic |
| BrainVLM 위상 | 본격 main path 후보 | Supplementary, Phase 3a parsing fix 만 |
| SSL pretrain | 명시 없음 | 5 후보 명시, priority 1 (subject-invariant + multi-source masked) 반드시 진행 |
| Cross-dataset 전략 | Cowen W projection + ComBat probe | Shared text-embedding zero-shot main + 4 전략 |
| FM naming | retreat 유지 | retreat 유지 + "Universal Emotion Code" 추가 후보 |
| Git workflow | main 에 직접 update | Branch `v4_20260602_perlmutter` 에서 작업 |

### 후속 작업

- ✅ `docs/masterplan_v2.md` v4 final 전면 재작성
- ✅ `Paper/framework_KR.md` / `framework_EN.md` v4 final framing prepend
- ✅ `CONTEXT_FEELIN.md` / `README.md` / `README_KR.md` v4 final 동기화
- ✅ Branch `v4_20260602_perlmutter` 생성
- ⏳ 다음 step.
  - (a) Phase 3b Track A 의 `code/ssl_pretrain/` 구현 시작 (subject_invariant.py + multi_source_masked.py)
  - (b) Phase 3c Track B 의 `code/phase2/task_universal_code.py` 구현
  - (c) Independent dataset 다운로드 (Emo-FilM, StudyForrest, NNDb, Affective Videos)
  - (d) ComBat wrapper + acquisition null baseline (`code/cross_dataset/`)
  - (e) `Paper/methodology.md` 도 v4 build recipe 에 맞춰 update
