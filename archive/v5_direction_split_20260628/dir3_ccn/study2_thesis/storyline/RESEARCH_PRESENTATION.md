# 연구 발표 스토리라인

---

## 1. Introduction

### 1.1 감정의 구조: Cowen & Keltner (2017)

- 2,185개 감정 유발 비디오에 대한 대규모 행동 연구
- 감정은 VA(valence/arousal) 2차원이 아니라 **27개 구별되는 범주**로 조직
- Split-half CCA로 재현 가능한 차원 수 확인
- 범주들은 연속적 gradient로 연결 (discrete이면서 continuous)
- 34개 감정 범주 + 14개 affective dimensions 측정
- **핵심 메시지: 감정 공간은 고차원이고, 범주가 차원보다 설명력이 높다**

### 1.2 뇌의 감정 표상: Horikawa et al. (2020)

- 같은 자극(2,196 비디오), 5명 fMRI
- 뇌에서 감정 디코딩: 수십 개 감정이 정확히 디코딩됨
- **Category > Dimension**: 범주가 차원보다 뇌 반응을 더 잘 예측
- **Distributed**: 특정 영역이 아닌 transmodal brain regions에 분산
- Visual/semantic confound 통제 후에도 유의
- Margulies principal gradient 활용: transmodal regions에서 감정 encoding 강함
- **핵심 메시지: 뇌의 감정 표상은 고차원, 범주적, 전뇌 분산적**

### 1.3 AI와 뇌의 감정 표상: Du et al. (2023, 2025)

**Du et al. (2023)** — 같은 데이터로 더 깊은 분석
- Voxel-wise encoding model → PCA → "fundamental affective space" 발견
- 뇌의 감정 공간이 14 affective dimensions의 hybrid 구조
- 뇌의 affective space ≠ 행동의 affective space (다른 구조)
- 감정이 cortex에 smooth gradients로 분포

**Du et al. (2025)** — AI를 cognitive agent로 활용
- MLLM(Qwen2-VL)로 700만+ triplet similarity judgment
- MLLM의 30차원 embedding이 인간 self-report보다 뇌 활동을 더 잘 예측
- MLLM > Human > LLM → sensory grounding 중요
- **핵심 메시지: AI가 뇌의 감정 기하 구조를 인간 행동보다 잘 포착**

### 1.4 남아있는 질문

```
지금까지 알려진 것:
  - 감정은 27개 범주, 고차원 (Cowen)
  - 뇌에서 범주적으로 디코딩 가능 (Horikawa)
  - 뇌에 fundamental affective space 존재 (Du 2023)
  - AI가 뇌의 감정 구조를 잘 포착 (Du 2025)
  - 감정 학습 안 한 비전 모델도 감정의 67% 설명 (Conwell 2025)

모르는 것:
  → AI가 설명하는 67%와 설명 못하는 33%의 정체는?
  → 뇌에서 감정으로 가는 과정에서 AI가 놓치는 것은 무엇인가?
  → 그 "놓치는 것"을 AI에 전달할 수 있는가?
```

### 1.5 관련 연구 배경 (추가 인용)

- **Conwell (2025)** "Perceptual primacy": 180개 비전 모델, 감정 학습 없이 VA의 67% 설명 → 감정은 지각에 기반
- **VCA (2025)**: CLIP-ViT + amygdala 모듈 → VA 예측 (r≈0.9) + 편도체 fMRI alignment → 하지만 image only, VA only, 편도체만
- **Moussa (2025)** Brain-tuning: speech model을 fMRI로 fine-tune → alignment 50% 향상, downstream 유지 → emotion 도메인에서는 안 됨
- **ICLR (2025)** 100 models: 99개 video model의 뇌 alignment 비교 → temporal modeling, classification task의 역할 → 하지만 emotion 안 봄
- **Margulies (2016)**: Principal gradient — unimodal(감각) ↔ transmodal(DMN) 축
- **Kragel (2015)**: 감정 신경 biomarker가 범주적으로 구별됨
- **(2019)** Emotion schemas: 감정이 시각 피질에 내장
- **Ma & Kragel (2026)**: 해마에 감정 지식의 map-like 표상

---

## 2. Research Question, Goal, Hypothesis

### Research Question

> **뇌가 시각 자극을 감정으로 변환하는 과정에서, AI 모델이 포착하지 못하는 뇌 고유의 감정 정보는 무엇인가?**

### Goal

**Primary:** Brain → ??? → Behavior에서 ???를 밝히는 것
- 뇌의 감정 표상을 AI 모델 "렌즈"로 분해
- AI가 설명하는 성분(지각적 감정)과 설명 못하는 성분(뇌 고유 감정)을 분리
- 뇌 고유 성분(???)의 정체 규명: 어떤 감정, 어떤 영역, 어떤 차원

**Sub:** Brain-tuning으로 ???를 AI에 전달
- ???의 existence proof
- Emotion Foundation Model 방향 제시

### Hypotheses

```
H1: 뇌의 감정 표상은 AI model이 설명하는 성분(지각적)과
    설명 못하는 성분(뇌 고유)으로 분해된다.
    → AI-unique 잔차에서 감정 디코딩이 유의하면 지지

H2: 뇌 고유 성분(???)은 범주적 감정에서 더 크다.
    → AV regress out 후에도 유지되는 범주 정보 (CCN에서 97.6% 확인)
    → 지각으로 충분한 감정 (e.g., looming→fear) vs 뇌 처리 필요한 감정

H3: ???는 transmodal brain regions (TPJ, mPFC, DMN)에서 주로 온다.
    → Horikawa: transmodal에서 감정 encoding 강함
    → Margulies PG: transmodal = 가장 추상적 처리
    → 예측: unimodal에서는 AI-shared 크고, transmodal에서는 AI-unique 큼

H4: Language 없는 self-supervised video model (V-JEPA2)에서도
    감정의 지각적 성분이 emerge한다.
    → V-JEPA2 ≈ CLIP이면: language 불필요 (perceptual primacy)
    → V-JEPA2 < CLIP이면: language가 감정 표상에 기여

H5: Brain-tuning으로 ???를 AI에 전달하면 감정 예측이 향상된다.
    → 특히 ???가 큰 감정에서 향상이 크면: 메커니즘적 검증
```

---

## 3. Methods

### 3.1 데이터

```
자극: 2,196개 감정 유발 비디오 (~3초)
참여자: 5명, fMRI (3T)
감정 레이블: 34 emotion categories + 14 affective dimensions = 48 targets
  (crowd-sourced, Cowen & Keltner 2017)
```

### 3.2 표상 (Representations)

```
Behavior: 48 emotion targets (output)
Brain:    Raw fMRI (Glasser 370 + Schaefer 450)
Stimulus: V-JEPA2 (1408-dim, self-supervised video)
          CLIP (512-dim, vision+language)
          DINOv2 (1536-dim, self-supervised image)
```

### 3.3 분석 파이프라인

```
Analysis 1: Brain → Behavior 디코딩 (baseline)
  fMRI → Ridge regression → 48 targets
  전뇌 + ROI별 (theory-driven: amygdala, insula, ACC, mPFC, TPJ, OFC, STS)
  Horikawa (2020) 재현 + 14 dim 확장

Analysis 2: AI 렌즈로 뇌 분해
  fMRI를 AI model feature와 emotion feature로 동시에 분해
  → Banded Ridge Regression (Horikawa 2020, Du 2023 방식)
  → 각 feature set의 unique variance를 엄밀하게 추정
  → 단순 residual(빼기)이 아닌 통계적 variance partitioning
  
  A: fMRI 전체 → Emotion                (뇌 전체 디코딩)
  B: AI-shared variance → Emotion       (지각적 감정)
  C: AI-unique variance → Emotion       (뇌 고유 감정 = ???)
  
  → 48 targets × 여러 AI 렌즈 × ROI별

Analysis 3: ??? 정체 규명
  감정별: 어떤 감정에서 C가 큰가?
  영역별: 어떤 ROI에서 C가 큰가? (transmodal vs unimodal)
  차원별: 14 dim 중 C와 관련 깊은 것?
  구조별: C의 Cat/VA ratio?

Analysis 4: Brain-tuning (sub goal)
  V-JEPA2 → adapter → predict fMRI → L2 loss (label-free)
  brain-tuned embedding → linear probe → 48 targets
  비교: vanilla vs brain-tuned vs behavior-tuned vs VA-tuned
```

### 3.4 통계

```
디코딩: Ridge regression, 5-fold CV + Leave-one-subject-out CV
메트릭: R², Pearson r, AUC-ROC (classification)
유의성: Permutation test (n=1000), FDR correction (BH, q<0.05)
스케일링: Z-score + Rank transform (robustness check)
Confound control: Banded ridge (emotion vs visual vs semantic)
```

---

## 4. Preliminary Results (CCN 2026 + 추가 분석)

### 4.1 Brain → V-JEPA2 alignment (CCN)

```
Forward (Brain-JEPA → V-JEPA2 PC):
  PC1: R²=0.373, PC2: R²=0.075, PC3: R²=0.088 (3개 유의)
  나머지 97개: R²=0.000

Forward (Raw fMRI → V-JEPA2 PC):
  PC1-6 유의 (6개), Raw가 Brain-JEPA보다 풍부

Reverse (V-JEPA2 → Brain PC):
  모든 100개 PC: R²=0.000 (완전한 비대칭)
  Raw fMRI에서도 동일 → Brain-JEPA artifact 아님

해석:
  뇌는 V-JEPA2의 소수 축을 선택적으로 읽지만,
  V-JEPA2는 뇌의 주요 분산을 전혀 읽지 못한다.
  → 비대칭 = 뇌의 주요 활동이 AI와 근본적으로 다름
```

### 4.2 범주성 (CCN)

```
Brain-pred subspace (3 PCs) → 감정 디코딩:
  Cat/VA ratio = 1.44 (Brain-JEPA), 1.68 (Raw fMRI)
  → 범주 > VA

AV regress out:
  VA 제거 후 범주 디코딩 97.6% 유지
  → 범주 정보는 VA와 독립 → Cowen (2017) 지지

CCA:
  100개 CC, 88개 유의, 27개 substantial (r>0.3)
  → Cowen의 27 범주와 수치적 일치
  → CC들이 구체적 범주 감정과 연결 (Annoyance, Aesthetic apprec., ...)
```

### 4.3 Brain-JEPA vs Raw fMRI

```
Brain-JEPA (resting-state pretrained): 3 brain-pred PCs
Raw fMRI (task, no model): 6 brain-pred PCs

→ Resting-state brain foundation model이 task-specific 감정 신호 절반 손실
→ Raw fMRI를 메인으로 사용하는 근거
```

### 4.4 해석 분석 (Exp 26-27)

```
Rating 분포 artifact:
  R² vs Std: r=0.480 (부분적 confound, 하지만 77%는 진짜 신호)
  Rank normalize 후 순서 거의 불변 (r=0.971)

6 Basic Emotion 실패:
  Joy Strong%=0.0%, Fear=0.0% → 데이터에 태깅 안 됨
  → 모델 문제 아닌 데이터 문제

Variance Partitioning (preliminary, Brain-JEPA 기반):
  Stimulus unique=0.014, Brain unique=0.003, Shared=0.041
  → Brain-JEPA에서는 brain unique 작음
  → Raw fMRI로 재실행 필요 (본 분석에서)

V-JEPA2 vs CLIP:
  Brain-pred PCs: V-JEPA2 3개, CLIP 6개
  → CLIP이 더 많은 뇌 축과 align
  → 추가 모델 비교 필요
```

---

## 5. 앞으로 할 분석 (발표 시점에 결과 있을 것들)

```
(발표까지 시간에 따라 조절)

1. Glasser 370 parcellation 완료 → Horikawa 직접 비교
2. 48 targets (14 dim 포함) 전체 디코딩
3. AI 렌즈 분해: AI-shared vs AI-unique (???) → 핵심 새 결과
4. ROI별 분석 (theory-driven)
5. DINOv2/VideoMAE 임베딩 추출 + 비교
6. Varimax rotation + Cowen 재현
```

---

## 6. Future Plan

### 6.1 본 분석 완성

```
??? 정체 규명:
  감정별 × 영역별 × 차원별 brain necessity map
  다중 AI 렌즈 비교 (V-JEPA2 vs CLIP vs DINOv2)
  Du (2023) 방식 fundamental affective space와 비교
```

### 6.2 Brain-Tuning (Sub Goal)

```
V-JEPA2를 fMRI로 fine-tune → 감정 예측 향상 검증
???가 큰 감정에서 더 향상되면 → ???의 existence proof
Moussa (2025) speech → emotion 도메인 최초 확장
```

### 6.3 추가 데이터셋 확장

```
Emo-FilM (30명, 14 films, 50 emotion): 재현 + n 확장
ReelMo (20명, 풀타임 영화, moment-by-moment): 시간 역학
```

### 6.4 방법론 발전 가능성

```
fMRI-LM 방식: fMRI → LLM token → brain-tuning in LLM space
Brain-inspired module: VCA 확장 (전뇌 + 범주)
Cross-cultural validation: 다른 문화권 데이터
```

---

## 발표 슬라이드 구성 (예상)

```
Slide 1:   Title
Slide 2-4: Introduction (Cowen → Horikawa → Du → 남은 질문)
Slide 5:   Research Question + Goal + Hypotheses
Slide 6-7: Methods (데이터, 표상, 분석 파이프라인)
Slide 8-10: Preliminary Results (CCN 결과 + 추가 분석)
Slide 11:  새 결과 (AI 렌즈 분해, ??? 발견)
Slide 12:  Future Plan (brain-tuning, 추가 데이터)
Slide 13:  Summary + Take-home message
```

---

## Take-home Message

> AI 비전 모델은 감정의 지각적 성분을 잘 포착하지만,
> 뇌에는 AI가 놓치는 고유한 감정 정보가 있다.
> 이 고유 정보는 주로 transmodal brain regions에서 오며 범주적으로 조직된다.
> Brain-tuning을 통해 이 정보를 AI에 전달하면 감정 예측이 향상될 수 있다.
