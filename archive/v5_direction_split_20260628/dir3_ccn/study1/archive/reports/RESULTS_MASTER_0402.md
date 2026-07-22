# CCN Results Master Document

**Date**: 2026-04-02  
**Project directory**: `/pscratch/sd/s/sjmoon/EmoFM/CCN`  
**Purpose**: 지금까지 나온 CCN 분석 결과를 한 문서에 모아서, 용어 설명부터 실험별 방법과 수치 결과, 해석 포인트, 저장 파일 위치까지 한 번에 볼 수 있게 정리한 통합 기록.

---

## 0. 이 문서를 읽는 방법

이 문서는 아래 순서로 읽으면 가장 이해가 쉽다.

1. **용어 설명**: RSM, RSA, CKA, Procrustes, PCA, Ridge CV 등이 무엇인지
2. **분석 파이프라인**: 01~13 분석이 서로 어떻게 연결되는지
3. **핵심 결과 요약**: 전체 스토리의 중심 숫자들
4. **실험별 상세 결과**: 각 스크립트/실험에서 실제로 무엇을 했고 무엇이 나왔는지
5. **Appendix**: Exp 12, Exp 13의 큰 표처럼 본문에 다 넣기엔 긴 결과값들

주의:
- 이 문서는 **보고용 scalar / vector / table 수준의 결과값**을 최대한 한데 모은 것이다.
- `(2196, 2196)` 같은 대형 행렬 전체를 문서에 그대로 싣는 것은 비효율적이어서, 그런 raw array는 `results/*.npz`, `results/*.npy`에 저장되어 있다.
- 따라서 “문서형 결과값”은 이 파일에 모았고, “원배열 전체”는 `results/`가 최종 원본이다.

---

## 1. 데이터와 전체 질문

### 데이터

- 데이터셋: **Horikawa et al. (2020)** emotion video dataset
- 피험자 수: **5명**
- 자극 수: **2196개 동영상**
- raw fMRI: `(5, 2196, 450)`
- Brain-JEPA embedding: `(5, 2196, 768)`
- V-JEPA2 embedding: `(2196, 1408)`
- CLIP embedding: `(2196, 512)`
- 감정 category score: **34개**
- affective dimension: **Arousal, Valence, Dominance**

### 프로젝트 핵심 질문

1. 뇌의 표상 공간과 video model의 표상 공간은 얼마나 정렬되어 있는가?
2. 그 정렬은 몇 차원 정도에서 사실상 포화되는가?
3. 뇌가 video model 전체를 읽는가, 아니면 소수의 핵심 차원만 읽는가?
4. 그 읽히는 차원은 감정적인가, 아니면 저차원적인 시각/의미 구조인가?
5. category-level emotion과 dimensional affect 중 무엇이 더 잘 설명되는가?

---

## 2. 방법론과 용어 설명

### Embedding

각 동영상을 하나의 고차원 벡터로 표현한 것.

- Brain-JEPA: 뇌 반응으로부터 학습된 신경 표상
- V-JEPA2: self-supervised video foundation model 표상
- CLIP: 이미지-텍스트 기반 vision-language model 표상

### PCA (Principal Component Analysis)

고차원 embedding을 더 작은 수의 축으로 요약하는 방법.

- PC1, PC2, PC3 ... 는 분산을 많이 설명하는 축부터 정렬된다.
- `k차원 PCA`는 “원래 공간의 핵심 구조를 k개의 축으로 압축한 버전”이라고 생각하면 된다.

### RSM (Representational Similarity Matrix)

각 자극 쌍 `(i, j)`가 얼마나 비슷하게 표현되는지 나타내는 `(N x N)` 행렬.

수식:

```text
RSM[i, j] = cosine_similarity(embedding_i, embedding_j)
```

왜 쓰는가:
- Brain-JEPA, raw fMRI, V-JEPA2, CLIP은 차원이 서로 다르다.
- 직접 좌표를 비교하기보다 “어떤 자극끼리 비슷한가”라는 **기하 구조**를 비교하려면 RSM이 유용하다.

### RSA (Representational Similarity Analysis)

특정 감정 구조가 RSM에 반영되는지 보는 분석.

감정 `i`에 대해:

```text
E_i[j, k] = score_i[j] * score_i[k]
RSA_i = Spearman r(RSM upper-tri, E_i upper-tri)
```

해석:
- RSA가 양수이면 그 감정을 많이 유발하는 자극들끼리 비슷하게 표상되는 경향이 있다는 뜻
- 34개 감정에 대한 mean RSA가 높을수록, 전체 공간이 감정 구조를 더 잘 반영

### CKA (Centered Kernel Alignment)

두 표현 구조가 얼마나 비슷한지를 보는 정렬 지표.

- 범위는 보통 `0 ~ 1`
- 값이 클수록 구조가 더 유사
- RSM에 직접 적용할 수도 있고, PCA-reduced embedding에 linear CKA로 적용할 수도 있다

직관:
- RSA는 특정 감정 구조와의 관련성을 본다
- CKA는 두 표현 공간 전체 구조가 얼마나 닮았는지를 본다

### Linear CKA

PCA 후의 feature matrix `X`, `Y`에 대해 Gram matrix `X @ X.T`, `Y @ Y.T`를 만든 뒤 centered alignment를 계산하는 방식.

이 프로젝트에서는:
- `CKA(brain_k, vjepa_k)`
- `CKA(brain_k, clip_k)`

같이 `k`차원 embedding을 직접 비교할 때 사용했다.

### Procrustes Alignment

두 좌표 공간을 회전/반전/스케일링해서 최대한 겹치게 만든 뒤 남는 오차를 보는 방법.

- disparity가 낮을수록 두 공간이 비슷
- “두 공간이 같은 모양인데 회전되어 있을 뿐인가?”를 확인하기 좋다

### Ridge Regression + Cross-Validation

한 공간의 좌표로 다른 변수(감정 점수, PC score)를 예측하는 분석.

이 프로젝트에서 자주 쓰는 형태:
- `brain -> model PC`
- `PC subspace -> emotion score`
- `k-dim PCA -> emotion score`

`R²` 해석:
- 높을수록 예측력이 높음
- 0이면 사실상 예측 못 함

### K-sweep

`k = [3, 5, 7, 10, 15, 20, 25, 27, 30, 34, 40, 50, 75, 100]` 등 여러 차원을 돌면서,

- CKA
- RSA
- Procrustes disparity
- Emotion decoding R²

가 어떻게 변하는지 보는 분석.

목적:
- “몇 차원 정도면 사실상 충분한가?”를 확인

### Brain-predictable PCs

video model PCA 축들 중에서, 뇌 embedding으로 예측 가능한 축.

기준:
- `brain -> PC_i` Ridge CV R² > 0.01

해석:
- 모델 전체 차원 중에서 **뇌가 실제로 접근하는 하위공간(subspace)**으로 볼 수 있다.

### FDR correction

여러 감정/축에 대해 상관을 많이 계산하면 우연히 유의해 보이는 값이 생길 수 있다.

- Benjamini-Hochberg FDR correction으로 다중비교를 조정
- `q < 0.05`이면 보정 후에도 유의

### Partial RSA / Partial R²

Exp 13의 핵심.

목적:
- “보이는 결과가 사실 감정이 아니라 low-level vision / semantic confound 때문 아닌가?”를 검증

방법:
- vision features와 semantic features를 confound로 두고
- RSA에서는 RSM에서 confound 구조를 회귀 제거
- R²에서는 PC와 감정 score에서 confound를 회귀 제거한 residual끼리 예측

---

## 3. 전체 분석 파이프라인

### 단계 1: 기본 neural geometry 확인
- Script 01: Brain-JEPA RSM
- Script 02: subject-level CKA

### 단계 2: 감정 구조와의 직접 대응
- Script 03-04: cross-space RSA

### 단계 3: 차원수 분석
- Script 05: Brain-JEPA k-sweep
- Script 08: Raw fMRI k-sweep
- Script 10: CKA/RSA vs k, brain-predictable dims

### 단계 4: 공간 정렬
- Script 06: Procrustes alignment
- Script 09: MDS / Procrustes overlay figure

### 단계 5: affective interpretation
- Exp 11: brain-predictable PC × emotion correlation
- Dimensional emotion analysis: A/V/D와의 관계
- Exp 12: category vs dimension 설명력 비교
- Exp 13: vision/semantic confound control

---

## 4. 핵심 결론만 먼저 보면

### 가장 강한 결과

1. **Brain-model alignment는 대략 27차원 근방에서 포화**
2. **뇌가 video model에서 읽는 차원은 전체가 아니라 극소수**
   - V-JEPA2: 3개 PC
   - CLIP: 4~6개 PC
3. **그 소수 PC는 감정과 강하게 관련**
4. **V-JEPA2 brain-predictable subspace는 A/V/D보다 category emotion을 더 잘 설명**
5. **하지만 vision/semantic confound를 통제하면 예측력은 크게 감소**
6. **V-JEPA2 vs CLIP 우열은 preprocessing 기준에 따라 뒤집혀서 primary claim으로 쓰기 어렵다**

### 현재 가장 안전한 claim

> Brain encodes only a small, affectively meaningful subspace of high-dimensional video representations, and the shared neural-computational geometry is effectively saturated by about 27 dimensions.

---

## 5. Script 01-02: Brain-JEPA RSM 및 피험자 간 일관성

### 무엇을 했는가

- 5명 피험자 각각의 Brain-JEPA embedding으로 per-subject RSM 계산
- 피험자 간 RSM 유사도(Spearman r) 계산
- Brain-JEPA RSM과 model RSM 사이의 subject-level CKA 계산

### Brain-JEPA cross-subject RSM consistency

```text
         Subj1   Subj2   Subj3   Subj4   Subj5
Subj1   [1.000   0.332   0.318   0.285   0.329]
Subj2   [0.332   1.000   0.381   0.359   0.412]
Subj3   [0.318   0.381   1.000   0.327   0.367]
Subj4   [0.285   0.359   0.327   1.000   0.360]
Subj5   [0.329   0.412   0.367   0.360   1.000]
```

- off-diagonal mean = **0.347 ± 0.034**

해석:
- Brain-JEPA는 raw fMRI보다 훨씬 높은 subject-invariant structure를 형성

### Per-subject CKA: Brain-JEPA vs V-JEPA2 / CLIP

| Subject | CKA(brain, V-JEPA2) | CKA(brain, CLIP) | Delta |
|---|---:|---:|---:|
| 1 | 0.054835 | 0.047351 | +0.007484 |
| 2 | 0.063292 | 0.060017 | +0.003274 |
| 3 | 0.055384 | 0.050774 | +0.004609 |
| 4 | 0.045845 | 0.051293 | -0.005448 |
| 5 | 0.072584 | 0.060269 | +0.012314 |
| **Mean** | **0.058388** | **0.053941** | **+0.004447** |

해석:
- 4/5 subject에서 Brain-JEPA는 V-JEPA2 쪽이 약간 높음
- 하지만 absolute effect size가 작고, subject 4에서는 CLIP이 더 높음

---

## 6. Script 03-04: Cross-space RSA

### 질문

Brain-JEPA, V-JEPA2, CLIP의 RSM이 각각 34개 감정 kernel과 얼마나 정렬되는가?

### RSA by emotion

| Emotion | Brain-JEPA | V-JEPA2 | CLIP |
|---|---:|---:|---:|
| Admiration | -0.019000 | 0.015000 | -0.014000 |
| Adoration | 0.006000 | 0.092000 | 0.082000 |
| Aesthetic appreciation | 0.023000 | -0.127000 | -0.003000 |
| Amusement | -0.083000 | 0.180000 | 0.134000 |
| Anger | -0.002000 | 0.028000 | 0.032000 |
| Anxiety | -0.037000 | 0.039000 | 0.130000 |
| Awe | -0.044000 | -0.007000 | 0.092000 |
| Awkwardness | 0.016000 | 0.045000 | 0.015000 |
| Boredom | -0.001000 | -0.043000 | -0.093000 |
| Calmness | 0.037000 | -0.082000 | -0.053000 |
| Confusion | -0.027000 | 0.028000 | 0.093000 |
| Contempt | -0.003000 | -0.001000 | -0.019000 |
| Craving | 0.031000 | 0.005000 | 0.017000 |
| Disgust | 0.000000 | 0.024000 | -0.001000 |
| Empathic pain | 0.027000 | 0.064000 | 0.045000 |
| Entrancement | -0.015000 | 0.048000 | 0.056000 |
| Excitement | -0.013000 | -0.103000 | 0.019000 |
| Fear | 0.010000 | -0.009000 | -0.015000 |
| Horror | -0.020000 | 0.020000 | 0.016000 |
| Interest | -0.028000 | 0.063000 | 0.151000 |
| Joy | 0.003000 | 0.017000 | 0.010000 |
| Nostalgia | -0.003000 | 0.068000 | 0.136000 |
| Relief | -0.068000 | -0.057000 | 0.048000 |
| Romance | -0.006000 | 0.098000 | 0.018000 |
| Sadness | 0.039000 | 0.009000 | -0.018000 |
| Satisfaction | -0.006000 | 0.013000 | -0.019000 |
| Sexual desire | -0.015000 | 0.034000 | 0.048000 |
| Surprise | 0.050000 | 0.019000 | 0.043000 |
| Sympathy | -0.018000 | 0.042000 | 0.040000 |
| Triumph | -0.040000 | 0.001000 | -0.011000 |
| Uncomfortable | 0.062000 | 0.030000 | 0.066000 |
| Annoyance | -0.109000 | 0.151000 | 0.220000 |
| Envy | -0.023000 | 0.073000 | 0.063000 |
| Guilt | -0.037000 | 0.038000 | 0.014000 |

### Mean RSA

- Brain-JEPA: **-0.009**
- V-JEPA2: **+0.024**
- CLIP: **+0.039**

해석:
- Brain-JEPA RSM은 감정 구조를 거의 직접 반영하지 않음
- CLIP과 V-JEPA2는 감정 kernel과 더 잘 맞음
- 하지만 이것만으로 “CLIP/V-JEPA2가 brain-like하다”라고 말하기는 어렵고, 오히려 Brain-JEPA 쪽에서 감정 정보가 압축됐을 가능성이 제기됨

---

## 7. Script 05: Brain-JEPA k-sweep

### 목적

Brain-JEPA 공간의 감정 정보가 몇 차원 정도면 사실상 포화되는가?

### Results

| k | Disp(brain,vjepa) | Disp(brain,clip) | R²(brain) | R²(vjepa) | R²(clip) |
|---|---:|---:|---:|---:|---:|
| 3 | 0.931579 | 0.933600 | 0.015627 | 0.054991 | 0.094106 |
| 5 | 0.938259 | 0.939800 | 0.022599 | 0.072626 | 0.136606 |
| 7 | 0.942706 | 0.936400 | 0.034557 | 0.079687 | 0.188361 |
| 10 | 0.940375 | 0.935100 | 0.042842 | 0.095500 | 0.211574 |
| 15 | 0.935514 | 0.936400 | 0.048828 | 0.113638 | 0.236082 |
| 20 | 0.937199 | 0.936900 | 0.053734 | 0.119836 | 0.253482 |
| 25 | 0.937570 | 0.938100 | 0.056145 | 0.129057 | 0.265433 |
| 27 | 0.938043 | 0.938500 | 0.056147 | 0.131729 | 0.269408 |
| 30 | 0.938735 | 0.938900 | 0.056797 | 0.133115 | 0.274387 |
| 34 | 0.938644 | 0.939300 | 0.058299 | 0.139859 | 0.281978 |
| 40 | 0.938995 | 0.939800 | 0.058972 | 0.146340 | 0.283630 |
| 50 | 0.939650 | 0.940600 | 0.060644 | 0.156382 | 0.289736 |
| 75 | 0.940351 | 0.941700 | 0.057418 | 0.167736 | 0.293137 |
| 100 | 0.940627 | 0.942600 | 0.054331 | 0.170615 | 0.290677 |

### 핵심 숫자

- Brain-JEPA emotion decoding은 `k=27`에서 이미 사실상 포화
- `R²_brain(k=27) = 0.056147`
- `R²_brain(k=100) = 0.054331`

해석:
- Brain-JEPA 안의 감정 geometry는 아주 고차원적이지 않다
- 27차원 근방이면 대부분의 감정 관련 구조가 다 나온다

---

## 8. Script 06: Procrustes Alignment (k=27)

### 전체 disparity

- disparity(brain, V-JEPA2) = **0.937986**
- disparity(brain, CLIP) = **0.938540**

### Per-emotion alignment error

| Emotion | Error(V-JEPA2) | Error(CLIP) | Delta |
|---|---:|---:|---:|
| Admiration | 0.020084 | 0.020236 | -0.000152 |
| Adoration | 0.018916 | 0.019001 | -0.000085 |
| Aesthetic appreciation | 0.018225 | 0.018312 | -0.000087 |
| Amusement | 0.020086 | 0.020166 | -0.000080 |
| Anger | 0.019125 | 0.019125 | -0.000000 |
| Anxiety | 0.019876 | 0.020023 | -0.000147 |
| Awe | 0.019601 | 0.019695 | -0.000094 |
| Awkwardness | 0.018354 | 0.018205 | +0.000149 |
| Boredom | 0.019237 | 0.019206 | +0.000031 |
| Calmness | 0.017465 | 0.017609 | -0.000144 |
| Confusion | 0.019389 | 0.019336 | +0.000052 |
| Contempt | 0.019461 | 0.019550 | -0.000089 |
| Craving | 0.016824 | 0.016865 | -0.000041 |
| Disgust | 0.019586 | 0.019538 | +0.000047 |
| Empathic pain | 0.018115 | 0.018081 | +0.000034 |
| Entrancement | 0.020051 | 0.019965 | +0.000085 |
| Excitement | 0.018794 | 0.018851 | -0.000057 |
| Fear | 0.018464 | 0.018547 | -0.000083 |
| Horror | 0.019392 | 0.019496 | -0.000104 |
| Interest | 0.019672 | 0.019791 | -0.000119 |
| Joy | 0.019072 | 0.019171 | -0.000099 |
| Nostalgia | 0.019787 | 0.019798 | -0.000011 |
| Relief | 0.020462 | 0.020508 | -0.000046 |
| Romance | 0.019233 | 0.019246 | -0.000013 |
| Sadness | 0.017436 | 0.017500 | -0.000064 |
| Satisfaction | 0.019902 | 0.020000 | -0.000097 |
| Sexual desire | 0.020005 | 0.020216 | -0.000210 |
| Surprise | 0.017055 | 0.016360 | +0.000696 |
| Sympathy | 0.019660 | 0.019678 | -0.000018 |
| Triumph | 0.020191 | 0.020269 | -0.000078 |
| Uncomfortable | 0.016571 | 0.016251 | +0.000321 |
| Annoyance | 0.020768 | 0.020811 | -0.000043 |
| Envy | 0.020062 | 0.020047 | +0.000015 |
| Guilt | 0.021500 | 0.021690 | -0.000189 |

### 요약

- mean error:
  - V-JEPA2 = **0.019189**
  - CLIP = **0.019210**
- V-JEPA2가 더 작은 error를 보인 감정 수: **25**
- CLIP이 더 작은 error를 보인 감정 수: **9**

해석:
- 아주 미세하게는 V-JEPA2가 더 잘 맞지만, 차이가 매우 작아서 strong claim으로 쓰기 어렵다

---

## 9. Script 07: Raw fMRI RSM / RSA / CKA

### 왜 중요한가

Brain-JEPA는 learned neural representation이라 감정 정보가 압축됐을 수 있다.  
그래서 raw fMRI로 같은 분석을 다시 돌려 비교했다.

### Raw fMRI cross-subject consistency

```text
         Subj1   Subj2   Subj3   Subj4   Subj5
Subj1   [1.000   0.089   0.078   0.061   0.061]
Subj2   [0.089   1.000   0.126   0.085   0.095]
Subj3   [0.078   0.126   1.000   0.083   0.088]
Subj4   [0.061   0.085   0.083   1.000   0.066]
Subj5   [0.061   0.095   0.088   0.066   1.000]
```

- off-diagonal mean = **0.083068 ± 0.018286**

해석:
- raw fMRI는 subject consistency가 낮다
- Brain-JEPA가 shared structure를 더 강하게 추출한 셈

### Raw fMRI RSA by emotion

| Emotion | Raw fMRI | V-JEPA2 | CLIP |
|---|---:|---:|---:|
| Admiration | 0.005737 | 0.014639 | -0.014047 |
| Adoration | 0.017860 | 0.091910 | 0.081541 |
| Aesthetic appreciation | 0.041952 | -0.127337 | -0.002714 |
| Amusement | 0.011574 | 0.180298 | 0.133543 |
| Anger | 0.013926 | 0.028315 | 0.031461 |
| Anxiety | 0.022440 | 0.039312 | 0.129950 |
| Awe | 0.010778 | -0.006655 | 0.091766 |
| Awkwardness | 0.009709 | 0.044620 | 0.014522 |
| Boredom | 0.009055 | -0.043090 | -0.093057 |
| Calmness | 0.025394 | -0.082173 | -0.052943 |
| Confusion | 0.013022 | 0.027720 | 0.093140 |
| Contempt | 0.001862 | -0.001139 | -0.019220 |
| Craving | 0.018954 | 0.004521 | 0.016612 |
| Disgust | 0.007469 | 0.023598 | -0.001239 |
| Empathic pain | 0.020703 | 0.063995 | 0.044687 |
| Entrancement | 0.026299 | 0.048049 | 0.056398 |
| Excitement | 0.027212 | -0.103104 | 0.019030 |
| Fear | 0.007147 | -0.008568 | -0.014886 |
| Horror | 0.011873 | 0.020271 | 0.016011 |
| Interest | 0.023179 | 0.062460 | 0.151003 |
| Joy | 0.002444 | 0.017052 | 0.009565 |
| Nostalgia | 0.024676 | 0.067809 | 0.135573 |
| Relief | 0.011727 | -0.057102 | 0.047859 |
| Romance | 0.014288 | 0.098440 | 0.017828 |
| Sadness | 0.018148 | 0.008528 | -0.017458 |
| Satisfaction | 0.004979 | 0.013013 | -0.018590 |
| Sexual desire | 0.017183 | 0.033627 | 0.047766 |
| Surprise | 0.023400 | 0.018697 | 0.042488 |
| Sympathy | 0.015734 | 0.041985 | 0.040263 |
| Triumph | 0.008021 | 0.001125 | -0.010456 |
| Uncomfortable | 0.030311 | 0.030325 | 0.065976 |
| Annoyance | 0.035088 | 0.150973 | 0.219993 |
| Envy | 0.020768 | 0.072970 | 0.063450 |
| Guilt | 0.017275 | 0.038032 | 0.013533 |

Mean RSA:
- Raw fMRI = **0.016770**
- V-JEPA2 = **0.023915**
- CLIP = **0.039393**

### Raw fMRI CKA

| Comparison | CKA | p-value | 95% CI |
|---|---:|---:|---|
| raw RSM vs V-JEPA2 | 0.151479 | 0.000 | [0.151, 0.173] |
| raw RSM vs CLIP | 0.170160 | 0.000 | [0.175, 0.194] |
| delta (vjepa - clip) | -0.018681 | 1.000 | [-0.032, -0.013] |

Per-subject CKA:

| Subject | CKA(raw, V-JEPA2) | CKA(raw, CLIP) | Delta |
|---|---:|---:|---:|
| 1 | 0.0698 | 0.0760 | -0.0063 |
| 2 | 0.0958 | 0.1101 | -0.0143 |
| 3 | 0.0919 | 0.0985 | -0.0066 |
| 4 | 0.0639 | 0.0784 | -0.0145 |
| 5 | 0.0761 | 0.0838 | -0.0077 |

해석:
- raw fMRI 기준으로는 CLIP이 consistently 더 높음
- Brain-JEPA 기준에서는 V-JEPA2가 약간 더 높았음
- 따라서 “V-JEPA2 > CLIP for brain alignment”는 preprocessing robust claim이 아니다

---

## 10. Script 08: Raw fMRI k-sweep

| k | Disp(raw,vjepa) | Disp(raw,clip) | R²(raw) | R²(vjepa) | R²(clip) |
|---|---:|---:|---:|---:|---:|
| 3 | 0.928750 | 0.936535 | 0.033044 | 0.054991 | 0.094106 |
| 5 | 0.918325 | 0.904319 | 0.052278 | 0.072626 | 0.136606 |
| 7 | 0.919001 | 0.895001 | 0.068315 | 0.079687 | 0.188361 |
| 10 | 0.913514 | 0.894108 | 0.086466 | 0.095500 | 0.211574 |
| 15 | 0.911136 | 0.898722 | 0.092066 | 0.113638 | 0.236082 |
| 20 | 0.913465 | 0.899652 | 0.101732 | 0.119836 | 0.253482 |
| 25 | 0.913292 | 0.902175 | 0.106129 | 0.129057 | 0.265433 |
| 27 | 0.914030 | 0.903096 | 0.107423 | 0.131729 | 0.269408 |
| 30 | 0.914686 | 0.903319 | 0.108785 | 0.133115 | 0.274387 |
| 34 | 0.914712 | 0.903618 | 0.110415 | 0.139859 | 0.281978 |
| 40 | 0.914229 | 0.904335 | 0.111238 | 0.146340 | 0.283630 |
| 50 | 0.913684 | 0.904608 | 0.113654 | 0.156382 | 0.289736 |
| 75 | 0.912409 | 0.905384 | 0.116914 | 0.167736 | 0.293137 |
| 100 | 0.911272 | 0.905453 | 0.114985 | 0.170615 | 0.290677 |

### 요약

- raw fMRI decoding R² @ k=27 = **0.107423**
- raw fMRI decoding R² @ k=100 = **0.114985**
- 즉 `k=27`은 max의 약 **93.4%**
- 자동 탐지:
  - elbow = **5**
  - plateau = **40**

비교:
- Brain-JEPA @ k=27 = **0.056147**
- Raw fMRI @ k=27 = **0.107423**

해석:
- raw fMRI가 Brain-JEPA보다 감정 정보는 더 많이 보존
- 그래도 포화되는 차원수 자체는 비슷한 범위에 있음

---

## 11. Script 09: 2D visualization

생성 figure:

- `figures/emotion_space_3panel.png`
- `figures/procrustes_overlay.png`
- `figures/raw_emotion_space_3panel.png`
- `figures/raw_procrustes_overlay.png`

이 figure들은 수치 테이블이라기보다 구조 시각화 자료다.  
핵심 수치는 이미 Procrustes disparity와 RSM/RSA/CKA 결과에 반영되어 있다.

---

## 12. Script 10: CKA/RSA vs k + Brain-predictable dimensions

### CKA / RSA vs k

| k | CKA(brain,vjepa) | CKA(brain,clip) | RSA(brain,vjepa) | RSA(brain,clip) |
|---|---:|---:|---:|---:|
| 3 | 0.117222 | 0.095519 | 0.096350 | 0.093218 |
| 5 | 0.117509 | 0.094917 | 0.103363 | 0.096922 |
| 7 | 0.119237 | 0.100535 | 0.106671 | 0.101136 |
| 10 | 0.121849 | 0.107214 | 0.112423 | 0.107721 |
| 15 | 0.125789 | 0.108687 | 0.118140 | 0.108203 |
| 20 | 0.126042 | 0.109331 | 0.118869 | 0.108106 |
| 25 | 0.126534 | 0.109425 | 0.119712 | 0.107871 |
| 27 | 0.126603 | 0.109412 | 0.119619 | 0.107628 |
| 30 | 0.126602 | 0.109566 | 0.119627 | 0.107788 |
| 34 | 0.126792 | 0.109775 | 0.119881 | 0.107940 |
| 40 | 0.126968 | 0.110057 | 0.119889 | 0.108137 |
| 50 | 0.127238 | 0.110084 | 0.120189 | 0.108256 |
| 75 | 0.127612 | 0.110412 | 0.120385 | 0.108031 |
| 100 | 0.127801 | 0.110565 | 0.120474 | 0.107963 |

### 포화 분석

- CKA(brain, vjepa) at k=27 = `0.126603 / 0.127801 = 99.06%`
- CKA(brain, clip) at k=27 = `0.109412 / 0.110565 = 98.96%`
- RSA(brain, vjepa) at k=27 = `0.119619 / 0.120474 = 99.29%`
- RSA(brain, clip) at k=27 = `0.107628 / 0.108256 = 99.42%`

해석:
- brain-model alignment는 CKA와 RSA 둘 다 `k≈27`에서 사실상 포화

### Brain-predictable dimensions

V-JEPA2:
- PC1 = **0.372842**
- PC2 = **0.074791**
- PC3 = **0.087770**
- PC4 = 0.000317
- 나머지 ≈ 0

CLIP:
- PC1 = **0.261256**
- PC2 = **0.155886**
- PC3 = **0.127107**
- PC4 = 0.000000
- PC5 = **0.115421**
- PC6 = **0.016697**
- PC7 = **0.012504**
- 나머지 ≈ 0

해석:
- Brain이 읽는 건 전체 representation이 아니라 소수 PC
- V-JEPA2는 사실상 3개 PC
- CLIP은 4~6개 PC

---

## 13. Experiment 11: Brain-predictable PC × Emotion Correlation

### 질문

Brain이 decode 가능한 PC들이 실제로 감정적인 축인가?

### 결론

**시나리오 A 확정**  

> Brain selectively reads the affective subspace of video representations.

### V-JEPA2 brain-predictable PCs

- PC1, PC2, PC3

#### PC1
- brain predictability R² = **0.3728**
- explained variance = **17.02%**
- max|r| = **0.3277**
- FDR-significant emotions = **26**
- top emotions:
  - Aesthetic appreciation = `-0.3277`
  - Annoyance = `+0.3253`
  - Calmness = `-0.2880`
- AVD:
  - Arousal = `+0.1408`
  - Valence = `-0.1259`
  - Dominance = `+0.0422`

#### PC2
- R² = **0.0748**
- explained variance = **5.53%**
- max|r| = **0.3544**
- FDR-significant emotions = **24**
- top emotions:
  - Aesthetic appreciation = `+0.3544`
  - Excitement = `+0.3276`
  - Adoration = `-0.2791`
- AVD:
  - Arousal = `+0.2254`
  - Valence = `-0.0823`
  - Dominance = `-0.0234`

#### PC3
- R² = **0.0878**
- explained variance = **5.07%**
- max|r| = **0.3034**
- FDR-significant emotions = **25**
- top emotions:
  - Uncomfortable = `-0.3034`
  - Empathic pain = `-0.2384`
  - Guilt = `+0.2369`
- AVD:
  - Arousal = `+0.0297`
  - Valence = `+0.0615`
  - Dominance = `+0.0426`

### Brain-pred vs unpred (V-JEPA2)

| Group | n PCs | mean max\|r\| across 34 emotions |
|---|---:|---:|
| Brain-predictable | 3 | 0.3285 |
| Brain-unpredictable | 97 | 0.0903 |
| Delta |  | +0.2382 |

### CLIP brain-predictable PCs

- PC1, PC2, PC3, PC5, PC6, PC7

대표값:
- PC1: Annoyance `-0.4512`, Uncomfortable `+0.4162`, Surprise `+0.3637`
- PC2: Aesthetic appreciation `-0.4726`, Excitement `-0.4029`, Uncomfortable `+0.3613`
- PC3: Guilt `-0.2269`, Awe `+0.2142`, Horror `-0.2088`
- PC5: Uncomfortable `+0.3497`, Sadness `-0.2740`, Horror `+0.2724`
- PC6: Nostalgia `+0.3131`, Interest `+0.3107`, Sympathy `+0.2923`
- PC7: Empathic pain `+0.4029`, Amusement `-0.2917`, Romance `-0.2856`

AVD correlation:
- PC1: `[-0.1337, +0.1983, +0.0293]`
- PC2: `[-0.1213, +0.0905, +0.0967]`
- PC3: `[+0.0237, +0.1238, -0.0755]`
- PC5: `[+0.1777, +0.0577, +0.0454]`
- PC6: `[-0.0132, -0.2768, -0.1779]`
- PC7: `[-0.0655, -0.3169, -0.0641]`

### Brain-pred vs unpred (CLIP)

| Group | n PCs | mean max\|r\| across 34 emotions |
|---|---:|---:|
| Brain-predictable | 6 | 0.3694 |
| Brain-unpredictable | 94 | 0.0818 |
| Delta |  | +0.2877 |

### 해석

- 뇌가 읽는 PC들은 감정과 강하게 correlate
- 따라서 brain-model alignment의 중심은 “임의의 perceptual 차원”이 아니라 affective subspace에 가깝다

---

## 14. Dimensional Emotion Analysis (Arousal / Valence / Dominance)

이 분석은 categorical emotion 34개와 별도로, A/V/D 차원에서 뇌와 모델이 어떤 패턴을 보이는지 본 supplementary analysis이다.

### Brain direct prediction of A/V/D

`r2_brain_avd = [0.000000, 0.065173, 0.000000]`

즉:
- Brain -> Arousal = **0.0000**
- Brain -> Valence = **0.0652**
- Brain -> Dominance = **0.0000**

### Model k=27 -> A/V/D

V-JEPA2 k=27:
- Arousal = **0.083343**
- Valence = **0.120334**
- Dominance = **0.016181**

CLIP k=27:
- Arousal = **0.105918**
- Valence = **0.439677**
- Dominance = **0.083408**

### Max R² across k

Brain:
- Arousal max = **0.042374**
- Valence max = **0.163023**
- Dominance max = **0.018872**

V-JEPA2:
- Arousal max = **0.101959**
- Valence max = **0.181673**
- Dominance max = **0.024133**

CLIP:
- Arousal max = **0.135484**
- Valence max = **0.478706**
- Dominance max = **0.087971**

### Brain-predictable PC × A/V/D correlation

V-JEPA2:
- PC1: `[+0.1408, -0.1259, +0.0422]`
- PC2: `[+0.2254, -0.0823, -0.0234]`
- PC3: `[+0.0297, +0.0615, +0.0426]`

CLIP:
- PC1: `[-0.1337, +0.1983, +0.0293]`
- PC2: `[-0.1213, +0.0905, +0.0967]`
- PC3: `[+0.0237, +0.1238, -0.0755]`
- PC5: `[+0.1777, +0.0577, +0.0454]`
- PC6: `[-0.0132, -0.2768, -0.1779]`
- PC7: `[-0.0655, -0.3169, -0.0641]`

### 해석

- CLIP은 특히 **Valence**를 강하게 담고 있다
- V-JEPA2는 category-related structure는 보이지만 A/V/D는 상대적으로 약하다
- Brain 자체도 A/V/D 중에서는 Valence만 어느 정도 직접 예측 가능

---

## 15. Experiment 12: Brain-Predictable Subspace — Category vs Dimension

### 질문

Brain-predictable subspace가 설명하는 것은
- 34개 emotion category인가?
- 아니면 A/V/D 같은 low-dimensional affective dimension인가?

### 핵심 결론

- **V-JEPA2**: category 쪽이 더 강함
- **CLIP**: category와 dimension이 둘 다 강하지만, 더 혼합적

### V-JEPA2 summary

- Brain-predictable PCs: `[1, 2, 3]`
- mean R²(34 cat), pred = **0.0550**
- mean R²(A/V/D), pred = **0.0254**
- cat/dim ratio = **2.162**

### CLIP summary

- Brain-predictable PCs: `[1, 2, 3, 5, 6, 7]`
- mean R²(34 cat), pred = **0.1659**
- mean R²(A/V/D), pred = **0.1297**
- cat/dim ratio = **1.279**

### A/V/D comparison table

| Dimension | V-JEPA2 pred | V-JEPA2 all | V-JEPA2 eff | CLIP pred | CLIP all | CLIP eff |
|---|---:|---:|---:|---:|---:|---:|
| Arousal | 0.0651 | 0.0889 | 0.732 | 0.0621 | 0.1355 | 0.459 |
| Valence | 0.0112 | 0.1817 | 0.062 | 0.2706 | 0.4787 | 0.565 |
| Dominance | 0.0000 | 0.0004 | 0.000 | 0.0565 | 0.0639 | 0.884 |
| Mean | 0.0254 | 0.0903 | 0.265 | 0.1297 | 0.2260 | 0.636 |

### 주요 감정

V-JEPA2 top:
- Aesthetic appreciation = 0.3231
- Excitement = 0.2001
- Uncomfortable = 0.1715
- Calmness = 0.1361
- Amusement = 0.1159

CLIP top:
- Uncomfortable = 0.5379
- Aesthetic appreciation = 0.4473
- Amusement = 0.3397
- Surprise = 0.3308
- Excitement = 0.2866

### Appendix A

Exp 12의 37-target 전체 표는 이 문서 맨 아래 Appendix A에 다시 붙여두었다.

---

## 16. Experiment 13: Vision / Semantic Confound Control

### 질문

지금까지 보인 affective alignment가 사실
- low-level visual feature
- semantic annotation feature

때문에 생긴 가짜 효과는 아닌가?

### Experiment A: Partial RSA

| Source | Model | Original RSA | Partial RSA | Delta | p-value |
|---|---:|---:|---:|---:|---:|
| Brain-JEPA | V-JEPA2 | -0.007063 | -0.004500 | +0.002562 | 2.812e-12 |
| Brain-JEPA | CLIP | -0.069710 | -0.068558 | +0.001153 | 0.000e+00 |
| Raw fMRI | V-JEPA2 | 0.095617 | 0.077626 | -0.017992 | 0.000e+00 |
| Raw fMRI | CLIP | 0.088632 | 0.071745 | -0.016888 | 0.000e+00 |

해석:
- Raw fMRI positive RSA는 confound control 후에도 남지만 감소
- Brain-JEPA negative RSA는 거의 그대로 유지

### Experiment B: Partial R²

핵심 summary:

V-JEPA2:
- mean R² emotions: `0.054990 -> 0.005117`
- mean R² A/V/D: `0.025439 -> 0.002932`
- retained:
  - emotion = **9.30%**
  - A/V/D = **11.52%**

CLIP:
- mean R² emotions: `0.165878 -> 0.013403`
- mean R² A/V/D: `0.129741 -> 0.008595`
- retained:
  - emotion = **8.08%**
  - A/V/D = **6.62%**

largest surviving partial values:
- V-JEPA2: Calmness `0.061010`, Aesthetic appreciation `0.051488`
- CLIP: Aesthetic appreciation `0.093505`, Calmness `0.056444`

### Appendix B

Exp 13의 full target-by-target table은 이 문서 맨 아래 Appendix B에 다시 붙여두었다.

---

## 17. 전체 종합 해석

### 17.1 지금까지 가장 안정적인 사실

1. **27차원 근방 포화**
   - Brain-JEPA k-sweep
   - raw fMRI k-sweep
   - CKA vs k
   - RSA vs k
   모두 대체로 `k≈27` 근방에서 중요한 구조가 대부분 나온다.

2. **Brain accesses only a small subspace**
   - V-JEPA2에서 3개 PC
   - CLIP에서 4~6개 PC

3. **그 subspace는 affective하다**
   - Exp 11에서 brain-predictable PC가 감정과 매우 강하게 correlate

4. **특히 V-JEPA2는 category-level organization 쪽으로 기울어 있음**
   - Exp 12 cat/dim ratio = 2.162

5. **하지만 confound control 후 residual signal은 작아진다**
   - Exp 13에서 partial R²가 크게 감소
   - 즉 affective signal이 있더라도, 시각/의미 confound와 완전히 분리된 pure signal은 상대적으로 작다

### 17.2 조심해야 할 claim

- “V-JEPA2가 CLIP보다 뇌와 더 잘 맞는다”
  - Brain-JEPA 기준: 약간 V-JEPA2 우세
  - raw fMRI 기준: CLIP 우세
  - 따라서 robust claim 아님

- “Brain-JEPA가 감정 geometry를 잘 보존한다”
  - Brain-JEPA RSA mean ≈ 0
  - raw fMRI가 감정 정보는 더 많이 남김

### 17.3 현재 가장 설득력 있는 서사

가장 자연스러운 스토리는 다음과 같다.

> Neural and computational emotion spaces share a geometry that is effectively low-dimensional, saturating around 27 dimensions, but the brain reads only a much smaller affective subspace of model representations. This readable subspace is emotion-related, especially for V-JEPA2, yet a substantial fraction of that signal overlaps with low-level visual and semantic structure.

---

## 18. 저장 파일 정리

### Core results

```text
results/
  brain_jepa_rsm_stats.npz
  subject_cka_results.npz
  crossspace_rsa_results.npz
  k_sweep_results.npz
  procrustes_results.npz
  raw_rsm_per_subject.npy
  raw_rsm_mean.npy
  raw_rsa_cka_results.npz
  raw_k_sweep_results.npz
  raw_embedding_2d.npz
  cka_rsa_vs_k.npz
  brain_predictable_dims.npz
  pc_emotion_correlation.npz
  dimensional_emotion_results.npz
  brain_pred_subspace_prediction.npz
  vision_semantic_partial_results.npz
```

### Result markdowns

```text
RESULTS_FULL_0402.md
RESULTS_EXP11_0402.md
RESULTS_EXP12_0402.md
RESULTS_EXP13_0402.md
RESULTS_MASTER_0402.md
```

---

## Appendix A. Experiment 12 Full Table Reference

아래 값은 `RESULTS_EXP12_0402.md`의 요약을 재배치한 것이다.

### V-JEPA2

| Target | pred R² | unpred R² | all R² | eff (pred/all) |
|---|---:|---:|---:|---:|
| Admiration | 0.0235 | 0.0000 | 0.0027 | 8.700 |
| Adoration | 0.0805 | 0.2677 | 0.3597 | 0.224 |
| Aesthetic appreciation | 0.3231 | 0.1687 | 0.5509 | 0.587 |
| Amusement | 0.1159 | 0.1805 | 0.3219 | 0.360 |
| Anger | 0.0118 | 0.0512 | 0.0671 | 0.176 |
| Anxiety | 0.0611 | 0.1660 | 0.2394 | 0.255 |
| Awe | 0.0222 | 0.2219 | 0.2538 | 0.088 |
| Awkwardness | 0.0308 | 0.0487 | 0.0839 | 0.367 |
| Boredom | 0.0196 | 0.0832 | 0.1228 | 0.160 |
| Calmness | 0.1361 | 0.1284 | 0.3176 | 0.429 |
| Confusion | 0.0000 | 0.0072 | 0.0095 | 0.000 |
| Contempt | 0.0000 | 0.0204 | 0.0208 | 0.000 |
| Craving | 0.0166 | 0.3386 | 0.3643 | 0.046 |
| Disgust | 0.0088 | 0.0000 | 0.0000 | — |
| Empathic pain | 0.0741 | 0.0953 | 0.1823 | 0.407 |
| Entrancement | 0.0024 | 0.0000 | 0.0066 | 0.362 |
| Excitement | 0.2001 | 0.1527 | 0.3955 | 0.506 |
| Fear | 0.0000 | 0.0000 | 0.0000 | — |
| Horror | 0.0570 | 0.0629 | 0.1447 | 0.394 |
| Interest | 0.0598 | 0.1963 | 0.2667 | 0.224 |
| Joy | 0.0028 | 0.0000 | 0.0000 | — |
| Nostalgia | 0.0167 | 0.1318 | 0.1561 | 0.107 |
| Relief | 0.0576 | 0.0720 | 0.1552 | 0.371 |
| Romance | 0.0793 | 0.1241 | 0.2235 | 0.355 |
| Sadness | 0.0094 | 0.1832 | 0.1975 | 0.048 |
| Satisfaction | 0.0071 | 0.0000 | 0.0000 | — |
| Sexual desire | 0.0313 | 0.0852 | 0.1221 | 0.257 |
| Surprise | 0.0450 | 0.2234 | 0.2763 | 0.163 |
| Sympathy | 0.0059 | 0.0322 | 0.0440 | 0.134 |
| Triumph | 0.0128 | 0.0306 | 0.0465 | 0.275 |
| Uncomfortable | 0.1715 | 0.3005 | 0.4990 | 0.344 |
| Annoyance | 0.1057 | 0.0678 | 0.1828 | 0.578 |
| Envy | 0.0293 | 0.0000 | 0.0241 | 1.219 |
| Guilt | 0.0518 | 0.0518 | 0.1517 | 0.341 |
| Arousal | 0.0651 | 0.0037 | 0.0889 | 0.732 |
| Valence | 0.0112 | 0.1562 | 0.1817 | 0.062 |
| Dominance | 0.0000 | 0.0000 | 0.0004 | 0.000 |

### CLIP

| Target | pred R² | unpred R² | all R² | eff (pred/all) |
|---|---:|---:|---:|---:|
| Admiration | 0.0266 | 0.0308 | 0.0695 | 0.383 |
| Adoration | 0.1424 | 0.3933 | 0.5462 | 0.261 |
| Aesthetic appreciation | 0.4473 | 0.1468 | 0.6505 | 0.688 |
| Amusement | 0.3397 | 0.0913 | 0.4711 | 0.721 |
| Anger | 0.1818 | 0.0325 | 0.2321 | 0.783 |
| Anxiety | 0.2036 | 0.1609 | 0.3920 | 0.520 |
| Awe | 0.2096 | 0.1493 | 0.3850 | 0.545 |
| Awkwardness | 0.0913 | 0.0242 | 0.1281 | 0.713 |
| Boredom | 0.1011 | 0.0512 | 0.1738 | 0.581 |
| Calmness | 0.1655 | 0.1442 | 0.3611 | 0.458 |
| Confusion | 0.0291 | 0.0545 | 0.0934 | 0.311 |
| Contempt | 0.0493 | 0.0000 | 0.0595 | 0.828 |
| Craving | 0.1482 | 0.4409 | 0.6394 | 0.232 |
| Disgust | 0.0847 | 0.0000 | 0.0542 | 1.564 |
| Empathic pain | 0.1964 | 0.1483 | 0.3671 | 0.535 |
| Entrancement | 0.0564 | 0.0112 | 0.0774 | 0.728 |
| Excitement | 0.2866 | 0.1364 | 0.4663 | 0.615 |
| Fear | 0.0385 | 0.0000 | 0.0123 | 3.123 |
| Horror | 0.1709 | 0.0085 | 0.2083 | 0.821 |
| Interest | 0.2536 | 0.1525 | 0.4300 | 0.590 |
| Joy | 0.0289 | 0.0000 | 0.0094 | 3.074 |
| Nostalgia | 0.2100 | 0.0699 | 0.2999 | 0.700 |
| Relief | 0.1818 | 0.0356 | 0.2616 | 0.695 |
| Romance | 0.1236 | 0.2418 | 0.3879 | 0.319 |
| Sadness | 0.1922 | 0.2808 | 0.5251 | 0.366 |
| Satisfaction | 0.0544 | 0.0405 | 0.1109 | 0.490 |
| Sexual desire | 0.1058 | 0.0099 | 0.1260 | 0.839 |
| Surprise | 0.3308 | 0.2437 | 0.6074 | 0.545 |
| Sympathy | 0.1959 | 0.0632 | 0.2795 | 0.701 |
| Triumph | 0.0436 | 0.0290 | 0.0767 | 0.569 |
| Uncomfortable | 0.5379 | 0.1367 | 0.7275 | 0.739 |
| Annoyance | 0.1882 | 0.0534 | 0.2600 | 0.724 |
| Envy | 0.1030 | 0.0609 | 0.1764 | 0.584 |
| Guilt | 0.1211 | 0.0148 | 0.2078 | 0.583 |
| Arousal | 0.0621 | 0.0585 | 0.1355 | 0.459 |
| Valence | 0.2706 | 0.1800 | 0.4787 | 0.565 |
| Dominance | 0.0565 | 0.0000 | 0.0639 | 0.884 |

---

## Appendix B. Experiment 13 Full Table Reference

### Partial RSA

| Source | Model | Original RSA | Partial RSA | Delta | p-value |
|---|---:|---:|---:|---:|---:|
| Brain-JEPA | V-JEPA2 | -0.007063 | -0.004500 | +0.002562 | 2.812e-12 |
| Brain-JEPA | CLIP | -0.069710 | -0.068558 | +0.001153 | 0.000e+00 |
| Raw fMRI | V-JEPA2 | 0.095617 | 0.077626 | -0.017992 | 0.000e+00 |
| Raw fMRI | CLIP | 0.088632 | 0.071745 | -0.016888 | 0.000e+00 |

### V-JEPA2 partial R² table

| Target | Original R² | Partial R² | Delta | Retained |
|---|---:|---:|---:|---:|
| Admiration | 0.023496 | 0.000000 | -0.023496 | 0.000000 |
| Adoration | 0.080494 | 0.007245 | -0.073249 | 0.090007 |
| Aesthetic appreciation | 0.323135 | 0.051488 | -0.271648 | 0.159338 |
| Amusement | 0.115904 | 0.004238 | -0.111666 | 0.036562 |
| Anger | 0.011802 | 0.000000 | -0.011802 | 0.000000 |
| Anxiety | 0.061135 | 0.000395 | -0.060740 | 0.006460 |
| Awe | 0.022231 | 0.000000 | -0.022231 | 0.000000 |
| Awkwardness | 0.030796 | 0.000000 | -0.030796 | 0.000000 |
| Boredom | 0.019606 | 0.000000 | -0.019606 | 0.000000 |
| Calmness | 0.136112 | 0.061010 | -0.075102 | 0.448232 |
| Confusion | 0.000000 | 0.000000 | +0.000000 | 0.000000 |
| Contempt | 0.000000 | 0.000000 | +0.000000 | 0.000000 |
| Craving | 0.016605 | 0.005333 | -0.011272 | 0.321142 |
| Disgust | 0.008802 | 0.000000 | -0.008802 | 0.000000 |
| Empathic pain | 0.074097 | 0.000000 | -0.074097 | 0.000000 |
| Entrancement | 0.002384 | 0.000000 | -0.002384 | 0.000000 |
| Excitement | 0.200124 | 0.009684 | -0.190441 | 0.048389 |
| Fear | 0.000000 | 0.000000 | +0.000000 | 0.000000 |
| Horror | 0.057006 | 0.006776 | -0.050231 | 0.118858 |
| Interest | 0.059754 | 0.001976 | -0.057778 | 0.033071 |
| Joy | 0.002780 | 0.000000 | -0.002780 | 0.000000 |
| Nostalgia | 0.016698 | 0.000000 | -0.016698 | 0.000000 |
| Relief | 0.057564 | 0.000000 | -0.057564 | 0.000000 |
| Romance | 0.079292 | 0.000000 | -0.079292 | 0.000000 |
| Sadness | 0.009389 | 0.002711 | -0.006678 | 0.288786 |
| Satisfaction | 0.007147 | 0.002982 | -0.004164 | 0.417309 |
| Sexual desire | 0.031337 | 0.000000 | -0.031337 | 0.000000 |
| Surprise | 0.044951 | 0.000000 | -0.044951 | 0.000000 |
| Sympathy | 0.005896 | 0.001858 | -0.004038 | 0.315090 |
| Triumph | 0.012807 | 0.005493 | -0.007314 | 0.428933 |
| Uncomfortable | 0.171491 | 0.002799 | -0.168692 | 0.016322 |
| Annoyance | 0.105711 | 0.007731 | -0.097980 | 0.073130 |
| Envy | 0.029347 | 0.002244 | -0.027103 | 0.076455 |
| Guilt | 0.051776 | 0.000000 | -0.051776 | 0.000000 |
| Arousal | 0.065094 | 0.008795 | -0.056299 | 0.135113 |
| Valence | 0.011222 | 0.000000 | -0.011222 | 0.000000 |
| Dominance | 0.000000 | 0.000000 | +0.000000 | 0.000000 |

### CLIP partial R² table

| Target | Original R² | Partial R² | Delta | Retained |
|---|---:|---:|---:|---:|
| Admiration | 0.026622 | 0.000000 | -0.026622 | 0.000000 |
| Adoration | 0.142386 | 0.000000 | -0.142386 | 0.000000 |
| Aesthetic appreciation | 0.447327 | 0.093505 | -0.353822 | 0.209031 |
| Amusement | 0.339656 | 0.049430 | -0.290227 | 0.145528 |
| Anger | 0.181774 | 0.014517 | -0.167257 | 0.079863 |
| Anxiety | 0.203644 | 0.014503 | -0.189142 | 0.071215 |
| Awe | 0.209649 | 0.000000 | -0.209649 | 0.000000 |
| Awkwardness | 0.091264 | 0.000000 | -0.091264 | 0.000000 |
| Boredom | 0.101085 | 0.000000 | -0.101085 | 0.000000 |
| Calmness | 0.165505 | 0.056444 | -0.109060 | 0.341043 |
| Confusion | 0.029090 | 0.000000 | -0.029090 | 0.000000 |
| Contempt | 0.049327 | 0.000000 | -0.049327 | 0.000000 |
| Craving | 0.148219 | 0.000000 | -0.148219 | 0.000000 |
| Disgust | 0.084713 | 0.000000 | -0.084713 | 0.000000 |
| Empathic pain | 0.196400 | 0.003818 | -0.192582 | 0.019441 |
| Entrancement | 0.056352 | 0.002025 | -0.054327 | 0.035938 |
| Excitement | 0.286630 | 0.025940 | -0.260690 | 0.090499 |
| Fear | 0.038490 | 0.005329 | -0.033161 | 0.138454 |
| Horror | 0.170896 | 0.032251 | -0.138645 | 0.188717 |
| Interest | 0.253596 | 0.023548 | -0.230048 | 0.092856 |
| Joy | 0.028893 | 0.000000 | -0.028893 | 0.000000 |
| Nostalgia | 0.210044 | 0.000000 | -0.210044 | 0.000000 |
| Relief | 0.181839 | 0.019169 | -0.162670 | 0.105418 |
| Romance | 0.123616 | 0.002769 | -0.120848 | 0.022399 |
| Sadness | 0.192205 | 0.016171 | -0.176034 | 0.084135 |
| Satisfaction | 0.054351 | 0.003109 | -0.051242 | 0.057205 |
| Sexual desire | 0.105767 | 0.000000 | -0.105767 | 0.000000 |
| Surprise | 0.330832 | 0.040950 | -0.289882 | 0.123779 |
| Sympathy | 0.195932 | 0.030591 | -0.165341 | 0.156130 |
| Triumph | 0.043598 | 0.000000 | -0.043598 | 0.000000 |
| Uncomfortable | 0.537881 | 0.009488 | -0.528393 | 0.017640 |
| Annoyance | 0.188162 | 0.008700 | -0.179461 | 0.046239 |
| Envy | 0.102990 | 0.003449 | -0.099541 | 0.033487 |
| Guilt | 0.121121 | 0.000000 | -0.121121 | 0.000000 |
| Arousal | 0.062126 | 0.000000 | -0.062126 | 0.000000 |
| Valence | 0.270625 | 0.025786 | -0.244839 | 0.095283 |
| Dominance | 0.056473 | 0.000000 | -0.056473 | 0.000000 |

