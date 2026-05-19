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

### Phase 1 Settings — Confirmed

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
- Normalization: **Robust scaling** (median/IQR per ROI) — outlier에 강함, Brain-JEPA pretrain 동일 방식
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

### Subject Block — Separate Axis (deferred)

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
