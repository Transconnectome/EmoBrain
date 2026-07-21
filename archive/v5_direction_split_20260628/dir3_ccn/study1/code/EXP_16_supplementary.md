# Supplemental Experiment & Research Framework Update

## 1. 추가 실험: Baseline Benchmark (Vision/Semantic Only vs. Model PC)

### 왜 필요한가 (The Benchmark)
현재의 Partial $R^2$ 실험은 "모델의 PC가 시각 정보를 제외하고도 감정을 설명한다"는 점을 보여주지만, **"왜 굳이 비디오 모델(V-JEPA2)의 embedding을 써야 하는가?"**에 대한 대답으로는 부족합니다. 리뷰어의 "단순 시각/의미 피처의 선형 조합보다 모델 PC가 나은 점이 무엇인가?"라는 공격을 방어해야 합니다.

### 실험 방법: Incremental $R^2$ Test
다음 세 가지 모델의 예측력($R^2$)을 동일한 조건(5-fold Ridge CV)에서 비교합니다.
1. **Model A (Baseline):** Vision (1000-dim) + Semantic (73-dim) $\rightarrow$ Emotion
2. **Model B (Proposed):** V-JEPA2 Brain-predictable PCs (3-dim) $\rightarrow$ Emotion
3. **Model C (Combined):** Vision + Semantic + V-JEPA2 PCs $\rightarrow$ Emotion

### 기대 효과 및 해석
- **Unique Contribution:** Model A보다 Model C의 성능이 유의미하게 높다면, 비디오 모델이 단순 피처들의 합을 넘어서는 '맥락적 감정 정보'를 추가로 제공함을 증명합니다.
- **Redundancy Reduction:** 모델의 PC가 시각 정보와 80%를 공유하더라도, 남은 20%가 뇌의 표상과 정렬되는 '핵심 정보'임을 강조할 수 있습니다.

---

## 2. 업데이트된 연구 프레임워크 (RQ, Hypothesis, Claim)

### Research Question (연구 질문)
> **"비디오 AI 모델의 latent space는 인간의 뇌가 감정을 처리하는 고차원적 구조를 시각적 속성과 독립적으로 공유하고 있는가?"**

* **세부 질문:** 뇌는 모델의 방대한 정보 중 감정 특이적인 부분 공간(Affective Subspace)을 선택적으로 해독하는가? 이 정렬은 단순한 시각적 통계로 환원되는가, 아니면 독자적인 감정 구조인가?

### Hypothesis (가설)
1. **Selective Affective Alignment:** 뇌는 모델의 전체 차원이 아닌, 감정 정보가 응축된 특정 PC(V-JEPA2의 경우 상위 3개)와 집중적으로 정렬될 것이다.
2. **Emotion-Specific Primacy:** 이 공유 공간은 단순한 Arousal/Valence 차원보다 복합적인 감정 카테고리를 설명하는 데 더 최적화되어 있을 것이다.
3. **Robustness to Visual Confounds:** 시각적/의미적 속성을 수학적으로 통제한 후에도 뇌와 모델 간의 정렬은 유의미하게 유지될 것이며, 이는 AI 내부에 '순수한 감정적 축'이 존재함을 시사한다.

### Main Claim (핵심 주장)
> **"인간의 뇌와 비디오 AI 모델은 시각적 속성에 강하게 결합된(visually-grounded) 공통의 감정 축을 공유한다. 비록 이 정렬의 상당 부분이 시각적 통계에 의존하나, 모델 내부에는 시각 정보를 초과하여 뇌의 표상과 직접 대응하는 독자적인 감정 구조가 존재한다."**

---

## 3. 결과 해석 및 방어 전략 (Discussion Points)

* **숫자의 유의성:** Partial $R^2$가 0.05~0.09 수준인 것은 노이즈가 극심한 fMRI 데이터와 엄격한 통제 환경(Confounds removal)을 고려할 때 통계적으로 매우 강력한 신호(True signal)입니다.
* **Brain-JEPA의 역할:** 뇌 foundation model은 피험자 간 공통된 감정 기하학(Shared Geometry)을 추출하는 데 탁월하지만, 세밀한 감정 해상도는 일부 희생됨을 인정하며 '공유 구조' 연구의 정당성을 확보합니다.
* **Brain Tuning의 명분:** 현재 AI 모델이 가진 '시각적 편향성(80% 의존)'을 숫자로 증명했으므로, 이를 극복하기 위해 뇌의 순수한 감정 구조를 주입하는 Brain Tuning이 필수적임을 역설합니다.