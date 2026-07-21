# Research Direction — 최종 확정

**Last updated:** 2026-04-12

---

## Primary Goal

> **Brain → ??? → Behavior: 뇌가 시각 입력을 감정으로 변환하는 과정(???)을 밝히는 것.**
> AI model을 "렌즈"로 사용하여, 뇌의 감정 표상에서 지각적 성분과 뇌 고유 성분을 분리한다.

## Sub Goal

> **Video → Emotion 예측 모델 개선: brain-tuning을 통해 AI 모델의 감정 예측을 향상시키는 것.**
> Primary goal에서 발견한 ???(뇌 고유 정보)를 AI에 전달하여, 감정 예측 성능을 높인다.
> 이는 ???의 existence proof이자 실용적 응용이다.

---

## 프레임워크

```
        Stimulus (AI model = 렌즈)
        V-JEPA2, CLIP, DINOv2 등
       /                         \
      /                           \
Brain (fMRI) ────────────── Behavior (emotion rating)
  = Input                     = Output (34 cat + 14 dim)
              ??? = 이걸 밝힌다
```

**Behavior = output. Brain = input. AI model = 뇌를 분해하는 도구.**

---

## 핵심 과학적 질문

```
Q1. 뇌에서 감정으로의 디코딩은 어떻게 되는가?
    Brain → Behavior (Horikawa 재현 + 14 dim 확장)

Q2. 뇌의 감정 표상에서 AI가 설명하는 부분과 못하는 부분은?
    fMRI = AI-shared 성분 + AI-unique 성분(???)
    AI-shared → Emotion: 지각적 감정
    AI-unique → Emotion: 뇌 고유 감정 = ???

Q3. ???의 정체는?
    어떤 감정에서 큰가?
    어떤 뇌 영역에서 오는가?
    어떤 affective dimension과 관련?
    범주적인가 차원적인가?

Q4. ???를 AI에 전달할 수 있는가? (brain-tuning = sub goal)
    brain-tuned model이 vanilla보다 감정 예측 향상?
    특히 ???가 큰 감정에서 더 향상? → ???의 existence proof
```

---

## 실험 구조

### Chapter 1: Brain → Behavior 디코딩 (baseline)

```
Input:  fMRI (Raw Glasser 370 / Schaefer 450)
Output: 48 targets (34 cat + 14 dim)
Method: Ridge regression, 5-fold CV + LOSO CV

Horikawa (2020) 재현 + 14 dim 확장
ROI별 분석 (theory-driven)
Cat vs Dim 비교
```

### Chapter 2: AI 렌즈로 뇌 분해

```
fMRI에서 AI model이 설명하는 성분 추출:
  V-JEPA2 embedding으로 fMRI를 regression → predicted fMRI
  Residual = fMRI - predicted fMRI = AI가 설명 못하는 성분

분석:
  A: fMRI 전체 → Emotion                    (뇌 전체)
  B: AI-shared fMRI 성분 → Emotion           (지각적 감정)
  C: AI-unique fMRI 성분(잔차) → Emotion     (뇌 고유 감정 = ???)
  
  C > 0 이면: "뇌에 AI가 모르는 감정 정보가 있다"

방법론 — Shared/Unique 분리:
  단순 residual (fMRI - predicted)이 아닌,
  Banded Ridge Regression / Variance Partitioning 사용.
  (Horikawa 2020, Du 2023에서 사용한 방법)
  여러 feature set(AI embedding, emotion, visual, semantic)의
  독립 기여도를 동시에 추정 → 통계적으로 엄밀한 분리.

다중 렌즈:
  V-JEPA2 렌즈 (self-supervised, video, no language)
  CLIP 렌즈 (language-supervised)
  DINOv2 렌즈 (self-supervised, image)
  → 각 렌즈로 분해했을 때 ???가 다른가?
  → V-JEPA2로 안 보이는데 CLIP으로 보이면: language가 그 감정에 필요
  → 어떤 렌즈로도 안 보이면: 진짜 뇌 고유
```

### Chapter 3: ??? 의 정체 규명

```
??? = AI-unique fMRI 잔차에서 디코딩되는 감정 정보

분석:
  감정별: 어떤 감정에서 ???가 큰가?
    → 지각으로 충분한 감정 (Aesthetic appreciation?) vs 뇌가 필요한 감정 (?)
  영역별: 어떤 ROI에서 ???가 오는가?
    → transmodal (TPJ, mPFC, DMN) vs unimodal (V1, auditory)
    → Horikawa의 PG 발견과 연결
  차원별: 14 dim 중 ???와 관련 깊은 것?
    → valence? approach? control? identity?
  구조별: ???는 범주적인가 차원적인가?
    → Cat/VA ratio in residual space
    → Cowen vs Barrett 논쟁에 기여
```

### Chapter 4: ??? 를 AI에 전달 (brain-tuning = sub goal)

```
방법: V-JEPA2를 fMRI로 fine-tune (Moussa 방식)
  → brain-tuned embedding 생성
  → 이 embedding으로 감정 예측

비교:
  (a) Vanilla V-JEPA2 → Emotion
  (b) Brain-tuned V-JEPA2 → Emotion
  (c) Behavior-tuned V-JEPA2 → Emotion
  (d) VA-tuned V-JEPA2 → Emotion

검증:
  (b) > (a): brain-tuning 효과 있음
  (b) > (c): 뇌가 행동 label보다 더 풍부한 supervision
  ???가 큰 감정에서 (b)-(a) 차이가 크면: ???가 전달됐다는 증거

brain-tuning은 감정 label 없이 순수하게 뇌 반응만으로 학습.
그런데 감정 예측이 올라가면:
  → "뇌 반응 자체가 implicit emotion supervision"
  → "우리가 발견한 ???가 진짜 의미있는 정보"
```

---

## 기존 논문과의 관계

```
Horikawa (2020): Brain → Behavior 직접 디코딩
  → 우리 Chapter 1의 baseline

Du (2023): Brain의 fundamental affective space 발견
  → 우리 Chapter 2-3에서 이걸 AI 렌즈로 분해

Du (2025): AI → Brain encoding, MLLM > Human
  → 우리는 반대 방향: Brain → Behavior decoding에서 AI를 렌즈로

Conwell (2025): Vision model이 감정의 67% 설명
  → 우리: 나머지 33%가 ???이고, 그게 뇌에 있다

VCA (2025): 편도체 모듈로 VA 예측
  → 우리: 전뇌 + 범주 감정 + decoding 방향

Moussa (2025): Brain-tuning (speech)
  → 우리 Chapter 4에서 emotion 도메인으로 확장

Cowen (2017): 27 범주, cat > dim, SH-CCA
  → 우리 분석 방법론 차용 + ???의 범주성 검증

Margulies (2016): Principal gradient
  → ???가 transmodal에서 오는지 확인
```

---

## 차별점 요약

```
1. Decoding 방향: Du (2025)는 encoding (AI→Brain), 우리는 decoding (Brain→Behavior)
2. AI를 렌즈로: 뇌를 AI-shared vs AI-unique로 분해하는 프레임워크 (아무도 안 함)
3. ???의 정체 규명: 감정별 × 영역별 × 차원별 (아무도 안 함)
4. Brain-tuning for emotion: ???의 existence proof (최초)
5. 34 cat + 14 dim 전부: 대부분 VA만 보거나 34 cat만 봄
6. Self-supervised video model: Du는 MLLM(language 있음), 우리는 V-JEPA2(language 없음)
7. Multiple AI lenses: 여러 모델로 분해 → 렌즈에 따라 ???가 다른가
```
