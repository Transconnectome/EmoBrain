# 방법론 상세 설명

**Last updated:** 2026-04-09

---

## 0. 데이터 상황

```
2,196개 비디오 각각에 대해 세 가지 벡터가 있다:

  V-JEPA2 embedding:    (2196, 1408)  — 비디오 모델이 본 것
  Brain-JEPA embedding:  (2196, 768)  — 뇌가 반응한 것 (5명 평균)
  Behavior ratings:      (2196, 36)   — 사람이 보고한 감정 (34 범주 + Arousal + Valence)
```

질문: 이 세 표상 사이에 어떤 관계가 있는가?

---

## 1. 방법 1: PCA + Ridge Regression

### 1.1 Step 1 — PCA: V-JEPA2의 "주요 방향"을 정리

V-JEPA2의 1408차원은 너무 많다. PCA는 이 1408차원을 **분산이 큰 순서대로** 정렬하는 것이다.

```
원본: 1408개 축이 뒤죽박죽
PCA 후:
  PC1 = V-JEPA2에서 분산이 가장 큰 방향
  PC2 = PC1과 직교하면서 분산이 두 번째로 큰 방향
  ...
  PC100 = 분산 100번째
```

**핵심: PCA는 V-JEPA2 데이터만 본다. 뇌 데이터는 전혀 안 봄.**
순전히 "V-JEPA2 안에서 어떤 방향에 분산이 크냐"만 보는 것이다.

PCA 후 각 비디오는 100개의 PC 값을 가진다:
```
비디오 #1:    PC1=2.3, PC2=-0.5, PC3=1.1, ..., PC100=0.02
비디오 #2:    PC1=-1.1, PC2=3.2, PC3=0.4, ..., PC100=-0.08
...
비디오 #2196: ...
```

### 1.2 Step 2 — Ridge Regression: 뇌가 각 PC를 "맞출 수 있는지" 시험

각 PC 하나하나에 대해 **독립적으로** 묻는다:

```
문제: 뇌 반응(768차원)만 보고, 이 비디오의 PC1 값을 맞혀봐.

X (입력):  Brain-JEPA embedding (2196 × 768)
y (정답):  V-JEPA2 PC1 값 (2196 × 1)

Ridge regression으로 학습 → 5-fold CV → R² 측정

R² = 0.37 → 뇌 반응으로 PC1 값의 37%를 설명 → "뇌가 이 축을 읽을 수 있다"
R² = 0.00 → 전혀 못 맞춤 → "뇌가 이 축을 못 읽는다"
```

이걸 PC1, PC2, ..., PC100 총 100번 반복:

```
PC1:   Brain(768) → Ridge → PC1 예측 → R²=0.373 ✓
PC2:   Brain(768) → Ridge → PC2 예측 → R²=0.075 ✓
PC3:   Brain(768) → Ridge → PC3 예측 → R²=0.088 ✓
PC4:   Brain(768) → Ridge → PC4 예측 → R²=0.000 ✗
...
PC100: Brain(768) → Ridge → PC100 예측 → R²=0.000 ✗
```

### 1.3 Step 3 — Permutation Test: 이 R²가 우연이 아닌지 검증

R²=0.373이 우연히 나온 건 아닌지 확인해야 한다.

**아이디어:** 만약 뇌와 PC1 사이에 진짜 관계가 없다면, 비디오 순서를 무작위로 섞어도 비슷한 R²가 나와야 한다.

```
원래 데이터:
  비디오 #1: Brain 반응 → PC1=2.3   (실제 대응)
  비디오 #2: Brain 반응 → PC1=-1.1  (실제 대응)

Permutation (섞기):
  비디오 #1: Brain 반응 → PC1=-1.1  (엉뚱한 대응)
  비디오 #2: Brain 반응 → PC1=2.3   (엉뚱한 대응)
  → 이 상태에서 Ridge regression → null R²
```

이걸 1000번 반복하면 null distribution이 만들어진다:

```
null R² 1000개: [0.000, 0.001, 0.000, 0.002, 0.000, ...]

관측된 R² = 0.373
→ 1000개 null 중 0.373 이상인 것이 0개
→ p = 0/1000 = 0.000
→ 이건 우연이 아니다
```

**FDR correction (Benjamini-Hochberg):**
100개 PC에 대해 동시에 검정하므로, 다중 비교 보정이 필요하다.
BH 방법으로 q-value를 계산하고, q < 0.05인 PC만 "brain-predictable"로 정의한다.

결과: PC1, 2, 3만 FDR q < 0.05 → **brain-predictable subspace = 3차원**

### 1.3b 관련 Figure

| Figure | 파일명 | 내용 |
|--------|--------|------|
| **Figure 1A** | `figure1_brain_predictable_subspace` | R² per V-JEPA2 PC (1~40). 파란=brain-pred(3개), 회색=unpred. *=유의 |
| **Figure 1B** | (같은 파일) | Brain-pred vs unpred의 mean max\|r\| with 34 emotions |

### 1.4 왜 R²인가? MSE도 봐야 하는가?

**R² (결정 계수):**
- 0~1 범위, 스케일에 무관
- "예측이 평균보다 얼마나 나은가"의 비율
- PC1과 PC50의 R²를 직접 비교 가능 (스케일 다르지만 상관없음)

**MSE (평균 제곱 오차):**
- 스케일에 의존
- PC1의 MSE와 PC50의 MSE는 직접 비교 불가 (PC1의 값 범위가 더 크니까)
- "예측 오차의 절대 크기"를 보여줌

**답:** 현재 분석에서는 **R²가 적절하다.** 100개 PC의 예측 가능성을 비교하는 것이 목적인데, 각 PC의 스케일이 다르기 때문이다. PC1은 분산이 크고 PC100은 분산이 작아서, MSE로 비교하면 PC1이 무조건 MSE가 크다. R²는 이 스케일 차이를 제거해준다.

단, MSE를 **추가로** 보고하면 리뷰어의 질문을 예방할 수 있다:
- R²가 높은데 MSE도 큰 경우 = 예측은 잘하지만 절대 오차가 큼
- 이런 경우는 거의 없지만 확인 차원에서 보고할 가치 있음

### 1.5 반대 방향: V-JEPA2 → Brain PC

**현재 방향:**
```
Brain(768) → Ridge → V-JEPA2 PC_i 예측
질문: "뇌가 V-JEPA2의 어떤 축을 읽을 수 있는가?"
```

**반대 방향:**
```
V-JEPA2(1408) → Ridge → Brain-JEPA PC_j 예측
질문: "V-JEPA2가 뇌의 어떤 축을 설명할 수 있는가?"
```

이 두 방향이 **다른 질문**이다:

| 방향 | X → y | 질문 |
|------|-------|------|
| Brain → Video PC | 뇌 → V-JEPA2 PC | 뇌가 비디오 모델의 어떤 축을 읽는가? |
| Video → Brain PC | V-JEPA2 → Brain PC | 비디오 모델이 뇌의 어떤 축을 설명하는가? |

**반대 방향도 해봐야 한다.** 이유:

1. **비대칭일 수 있다:** 뇌가 V-JEPA2 PC1을 잘 읽지만, V-JEPA2가 Brain PC1을 못 설명할 수도 있다. 뇌의 주요 분산 방향이 감정이 아니라 저수준 시각 처리일 수 있기 때문이다.

2. **논문 claim이 달라진다:**
   - Brain → Video PC: "뇌에서 감정을 뽑아서 비디오 모델의 축을 예측" → 뇌가 능동적 역할
   - Video → Brain PC: "비디오 모델이 뇌의 축을 설명" → 모델이 능동적 역할

3. **두 방향의 결과가 일관되면** → claim이 훨씬 강해진다
   - "뇌와 V-JEPA2가 양방향으로 서로를 예측하는 축이 동일하고, 그게 감정이다"

### 1.6 이 방법의 핵심 구조 정리

```
1. V-JEPA2가 혼자 축을 정한다 (PCA, 분산 기준)
2. 뇌는 그 축을 읽을 수 있는지 시험받는다 (Ridge, R²)
3. 우연이 아닌지 확인한다 (Permutation test, 1000회, FDR correction)
4. 질문: "V-JEPA2가 중요하다고 한 방향들 중에서, 뇌도 아는 건 몇 개?"
5. 답: 3개 (PC1, 2, 3)
```

**비유:** 수학 선생님(V-JEPA2)이 100문제짜리 시험을 출제. 학생(뇌)이 풀었더니 3문제만 맞힘.

**한계:** 선생님이 출제 안 한 영역(V-JEPA2 분산이 작은 방향)에서는 학생이 천재일 수도 있는데 그건 모름.

### 1.7 감정 디코딩 관련 Figure

| Figure | 파일명 | 내용 |
|--------|--------|------|
| **Figure 2A** | `figure2_categorical_organization` | 34 emotion + A/V decoding R² (brain-pred subspace). 파란=범주, 빨간=VA |
| **Figure 2B** | (같은 파일) | Cat/VA ratio: brain-pred(1.44) vs full space(1.26) |

---

## 2. 방법 2: CCA (Canonical Correlation Analysis)

### 2.1 PCA+Ridge의 한계를 CCA가 어떻게 해결하는가

PCA+Ridge의 문제: V-JEPA2의 PC47이 뇌와 관련 있어도, PC47은 V-JEPA2 분산이 작으니까 PCA에서 뒷순위로 밀린다. 뇌는 이 방향을 잘 읽을 수 있는데, PCA 기준으로 "별로 중요하지 않은 축"이라 놓칠 수 있다.

CCA는 이 문제를 해결한다: **V-JEPA2 분산 기준이 아니라, 뇌-비디오 상관 기준으로 축을 찾는다.**

### 2.2 CCA가 하는 것 (상세)

```
입력:
  V = V-JEPA2 쪽 (2196 × 100, PCA 전처리 후)
  B = Brain 쪽   (2196 × 100, PCA 전처리 후)

CCA가 찾는 것:
  V 쪽 100차원에서 방향 벡터 w_v를 하나 고른다
  B 쪽 100차원에서 방향 벡터 w_b를 하나 고른다
  
  각 비디오를 이 방향으로 projection:
    video_score_i = V_i · w_v  (scalar, 비디오 i의 점수)
    brain_score_i = B_i · w_b  (scalar, 비디오 i의 점수)
  
  corr(video_score, brain_score) 가 최대가 되도록 w_v, w_b를 동시에 최적화
  
  → 이게 CC1 (첫 번째 canonical component)
  → canonical correlation r₁ = 그 최대 상관값
```

CC2는:
```
CC1의 방향과 직교하는 조건 하에서
다시 corr(video_score, brain_score)가 최대가 되는 방향 쌍을 찾음
→ CC2, canonical correlation r₂
```

이걸 반복해서 CC1, CC2, ..., CC100까지 뽑는다.

### 2.3 CCA 전 PCA 전처리 — 왜 필요한가

CCA를 V-JEPA2(1408차원) × Brain(768차원)에 바로 적용하면 안 된다.

**이유: 과적합 (overfitting)**
- CCA는 양쪽에서 자유롭게 방향을 찾기 때문에, 차원 수가 샘플 수(2196)에 비해 너무 크면 noise까지 잡아버린다.
- V-JEPA2 1408 + Brain 768 = 2176 파라미터 vs N=2196 샘플 → 거의 1:1 → 과적합 위험

**해결: PCA로 양쪽을 먼저 축소**
```
V-JEPA2 (2196, 1408) → StandardScaler → PCA(100) → (2196, 100)
Brain   (2196, 768)  → StandardScaler → PCA(100) → (2196, 100)
```
이 PCA는 CCA의 일부가 아니라 **전처리**이다. 노이즈를 줄이고 CCA를 안정화하는 역할만 한다.

### 2.4 "왜 PCA 100인가?" — Justification

PCA n_components 선택은 **원본 분산을 얼마나 보존하느냐**로 정당화한다.

| n_components | V-JEPA2 분산 보존 | Brain-JEPA 분산 보존 |
|------|---------|---------|
| 10 | 24.3% | 82.7% |
| 20 | 34.5% | 92.7% |
| 50 | 53.0% | 98.2% |
| **100** | **69.3%** | **99.5%** |
| 200 | 84.0% | 99.9% |
| 500 | 96.4% | 100.0% |

**n=100의 근거:**
- Brain-JEPA: 99.5% 보존 → 거의 완벽, 정보 손실 없음
- V-JEPA2: 69.3% 보존 → 약 70%. 100개보다 더 쓰면 분산 보존은 올라가지만, 이 추가 축들은 분산이 매우 작아서 노이즈에 가깝다
- PCA+Ridge 분석과 동일한 100차원 → **두 방법 간 직접 비교 가능**
- N/p ratio = 2196/100 = 22 → CCA 안정성 충분 (일반적으로 N/p > 10 권장)

**추가 robustness check:** n=50, 100, 200으로 CCA를 반복하여 결과가 안정적인지 확인하면 더 강해진다.

### 2.5 CCA에서의 Permutation Test

CCA의 canonical correlation이 우연이 아닌지 확인해야 한다.

```
Step 1: 원본 데이터로 CCA → 관측된 r₁, r₂, ..., r₁₀₀

Step 2: Permutation (1000번 반복)
  뇌 데이터의 행(비디오)을 무작위로 섞는다.
  → 비디오-뇌 대응이 깨진다
  → 섞은 상태에서 CCA를 다시 돌린다
  → null r₁, r₂, ..., r₁₀₀ 을 얻는다

  이걸 1000번 반복 → 각 CC에 대해 null distribution (1000개 값)

Step 3: p-value 계산
  CC_i의 p-value = (null r ≥ 관측된 r인 횟수) / 1000

  예: CC1 관측 r = 0.733
      1000번 permutation 중 null r ≥ 0.733인 횟수 = 0
      → p = 0/1000 = 0.000

Step 4: FDR correction (Benjamini-Hochberg)
  100개 CC에 대해 동시에 검정 → 다중 비교 보정
  q < 0.05인 CC만 "significant"
```

**왜 permutation을 쓰는가 (parametric test 안 쓰는 이유):**
- CCA의 canonical correlation에 대한 표준 검정(Wilks' lambda 등)은 다변량 정규성을 가정
- 뇌 데이터 + 비디오 임베딩이 정규분포를 따르는지 모름
- Permutation test는 분포 가정 없이 정확한 p-value 제공

**주의: N이 큰 경우 모든 CC가 유의할 수 있다**
- N=2196일 때, 아주 작은 canonical r (예: 0.05)도 통계적으로 유의
- 유의성(significance) ≠ 의미(meaningfulness)
- 따라서 유의성과 별도로 **effect size 기준** 적용 필요:
  - r > 0.3을 "substantial shared variance"로 정의하는 것이 합리적
  - 또는 scree plot에서 elbow 지점 이용

### 2.6 PCA+Ridge와의 핵심 차이

```
PCA+Ridge:
  1. V-JEPA2 혼자 축을 정한다 (PCA, 분산 기준)
  2. 뇌는 그 축을 읽을 수 있는지 시험받는다 (Ridge)
  → V-JEPA2가 출제, 뇌가 응시

CCA:
  1. V-JEPA2와 뇌가 동시에 축을 정한다 (상관 최대화 기준)
  2. "둘이 가장 잘 통하는 방향"을 직접 찾는다
  → 둘이 함께 출제하고 함께 응시
```

**왜 결과가 다른가:**

PCA+Ridge에서 PC47이 뇌와 관련 있어도 발견 못하는 이유:
- PCA는 V-JEPA2 분산 기준으로 축을 정하니까 PC47은 "V-JEPA2에서 분산이 작은 방향"
- Brain → PC47 Ridge를 해봤자, PC47 자체의 변동성이 작아서 R²가 낮게 나옴

CCA는:
- V-JEPA2의 여러 축을 **선형 조합**해서 새로운 방향 w_v를 만듦
- 이 조합이 뇌와 상관이 높으면 잡아냄
- PC47 단독은 약하지만, PC23 + PC47 + PC89를 적절히 조합하면 뇌와 잘 맞을 수 있음
- CCA는 이 조합을 자동으로 찾는다

**정리:**

| | PCA + Ridge | CCA |
|---|---|---|
| 축을 정하는 주체 | V-JEPA2 혼자 | 양쪽이 함께 |
| 축 정의 기준 | V-JEPA2 분산 | 뇌-비디오 상관 |
| 뇌의 역할 | 시험 응시자 | 공동 참여자 |
| 방향 조합 | 안 함 (각 PC 개별 평가) | 함 (여러 PC를 조합) |
| 발견되는 축 수 | 적음 (엄격) | 많음 (관대) |
| 놓치는 것 | V-JEPA2 분산 작은 공유 축 | — |
| 강점 | 선택성 명확 | 숨겨진 공유도 발견 |
| 약점 | 편향적 (V-JEPA2 기준) | N 크면 뭐든 유의 |

### 2.7 CCA 관련 Figure

| Figure | 파일명 | 내용 |
|--------|--------|------|
| **Figure 3A** | `figure3_cca_shared_space` | Canonical correlations (CC1-30) + null 95th %ile 빨간 점선 |
| **Figure 3B** | (같은 파일) | CC1-5 × 감정 heatmap (Spearman r, 빨강/파랑) |
| **Figure 5** | `figure5_subject_cca_stability` | Subject-level CCA r (5명 개별 회색 + mean 파랑) |
| **Figure 6** | `figure6_cca_full_heatmap` | 모든 CC × 34 emotions 전체 heatmap |
| **NEW** | `figure_cca100_spectrum` | CCA 100 CC 전체 spectrum (초록/연두/회색 3단계, r>0.3 / r>0.1 / r<0.1) |

---

## 3. 두 방법이 보완 관계인 이유

### PCA+Ridge만 하면

> "V-JEPA2의 100개 주성분 중 3개만 뇌가 읽는다" (강한 선택성)

하지만 리뷰어: "V-JEPA2 PCA 기준이잖아. 뇌에 맞는 축을 못 찾은 건 아닌가?"

### CCA만 하면

> "뇌와 V-JEPA2가 공유하는 축이 100개나 있다" (풍부한 공유)

하지만 리뷰어: "N=2196이면 뭐든 유의하잖아. 의미 있는 게 뭔가?"

### 둘 다 하면

> "CCA로 보면 공유 구조는 풍부하다 (다차원적).
> 하지만 PCA+Ridge로 보면 V-JEPA2의 주요 분산 축 중에서는 딱 3개만 뇌가 선택적으로 읽고,
> 그 3개가 특히 범주 감정에 편향되어 있다."

→ CCA = 큰 그림 (숲), PCA+Ridge = 날카로운 주장 (나무). 서로의 약점을 보완한다.

### 3.1 비교 관련 Figure

| Figure | 파일명 | 내용 |
|--------|--------|------|
| **Figure 4A** | `figure4_method_comparison` | Decoding R² 비교: PCA(3), PCA(10), PCA(100), CCA — 파란(cat)/빨간(VA) grouped bar |
| **Figure 4B** | (같은 파일) | Cat/VA ratio 비교: 4가지 방법 |
| **Figure 7A** | `figure7_pca_vs_cca_comparison` | PCA R² spectrum (PC1-15) |
| **Figure 7B** | (같은 파일) | CCA r spectrum (CC1-15) + null |
| **Figure 7C** | (같은 파일) | Cat/VA ratio 4가지 비교 |

---

## 4. 방법 3: Reverse PCA+Ridge (V-JEPA2 → Brain PC)

### 4.1 왜 반대 방향이 필요한가

Forward는 "뇌가 V-JEPA2의 축을 읽을 수 있는가"를 봤다. 반대로 "V-JEPA2가 뇌의 축을 설명할 수 있는가"도 확인해야 한다. 두 방향의 결과가 같으면 대칭적 alignment, 다르면 비대칭 → 해석이 풍부해진다.

### 4.2 방법

```
Step 1: Brain-JEPA mean (2196, 768) → PCA → 100개 Brain PC
        Brain PC1 = 뇌 반응에서 분산이 가장 큰 방향 (32.7%)
        Brain PC2 = 두 번째 (16.3%)
        ...

Step 2: 각 Brain PC에 대해:
        X = V-JEPA2 (2196, 1408)
        y = Brain PC_j 값 (2196,)
        Ridge regression (5-fold CV) → R², MSE

Step 3: Permutation test (n=1000) + FDR correction
```

### 4.3 결과

**핵심: 완전한 비대칭**

```
Forward:  Brain → V-JEPA2 PC → 3개 유의 (R²=0.373, 0.088, 0.075)
Reverse:  V-JEPA2 → Brain PC → 0개 유의 (모든 R²=0.000)
```

V-JEPA2는 뇌의 **어떤 주요 분산 축도 예측할 수 없다.**

Brain PCA 분산 구조:

| Brain PC | 분산% | V-JEPA2→R² | max\|r\| emotion | Top emotion |
|----------|-------|-----------|-----------------|------------|
| BPC1 | 32.7% | 0.000 | 0.223 | Annoyance (-0.22) |
| BPC2 | 16.3% | 0.000 | 0.147 | Guilt (+0.15) |
| BPC3 | 12.0% | 0.000 | 0.204 | Interest (-0.20) |
| BPC4 | 6.7% | 0.000 | 0.183 | Amusement (+0.18) |
| BPC5 | 6.2% | 0.000 | 0.105 | Relief (-0.11) |

Brain PC들의 감정 상관이 V-JEPA2 brain-pred PC들보다 **약함** (max|r| ≈ 0.1–0.2 vs 0.3–0.4).

### 4.4 Cat/VA ratio가 뒤집힘

| 방향 | Cat R² | AV R² | Cat/VA Ratio |
|------|--------|-------|--------------|
| Forward brain-pred (PC1-3) | 0.055 | 0.038 | **1.44** |
| Reverse Brain PC1-3 | 0.016 | 0.026 | **0.61** |
| Reverse Brain PC1-10 | 0.043 | 0.071 | **0.60** |
| Reverse Brain all 100 | 0.055 | 0.091 | **0.60** |

Forward: 범주 > VA (ratio 1.44)
Reverse: VA > 범주 (ratio 0.60)

### 4.5 해석

**뇌의 주요 분산(Brain PCs)은 감정이 아니다:**
- Brain PC1 (32.7%)은 저수준 시각 처리, 주의 등에 가까울 가능성
- V-JEPA2가 이걸 예측 못함 = V-JEPA2가 인코딩하는 시각 특성과 뇌의 주요 활동이 근본적으로 다름

**뇌의 감정 정보는 분산이 작은 하위 차원에 숨어 있다:**
- Brain PCs 전체를 써도 Cat/VA = 0.60 → 뇌 분산의 주요 방향은 VA 편향
- 그러나 Forward에서 뇌가 V-JEPA2를 읽을 때는 범주를 선택적으로 추출 (Cat/VA = 1.44)

**결론:**
> 뇌는 전반적으로는 VA를 많이 표상하지만,
> V-JEPA2를 읽을 때는 범주 정보를 선택적으로 뽑아낸다.
> → 뇌가 V-JEPA2 안의 숨겨진 affective subspace를 능동적으로 선택하는 것이다.

### 4.6 Reverse 관련 Figure

| Figure | 파일명 | 내용 |
|--------|--------|------|
| **NEW-A** | `figure_three_methods_comparison` | Forward R² / Reverse R²(=0) / CCA r — 3-panel 나란히 비교 |
| **NEW-B** | `figure_forward_vs_reverse_ratio` | Cat/VA ratio: Forward(1.44) vs Reverse(0.60) |

---

## 5. 전체 결과 요약

### Forward PCA+Ridge (Brain → V-JEPA2 PC)

| PC | R² | FDR q | Brain-predictable? |
|----|-----|-------|--------------------|
| PC1 | 0.373 | < 0.001 | Yes |
| PC2 | 0.075 | < 0.001 | Yes |
| PC3 | 0.088 | < 0.001 | Yes |
| PC4-100 | 0.000 | ≥ 1.000 | No |

### Reverse PCA+Ridge (V-JEPA2 → Brain PC)

| Brain PC | R² | Significant? |
|----------|-----|-------------|
| BPC1-100 | **0.000 (전부)** | **No (0개)** |

### CCA (PCA 100 → CCA 100)

| CC | Canonical r |
|----|-------------|
| CC1 | **0.774** |
| CC2 | 0.679 |
| CC3 | 0.649 |
| CC4 | 0.608 |
| CC5 | 0.572 |
| CC6-27 | 0.52 ~ 0.31 (substantial, r > 0.3) |
| CC28-75 | 0.30 ~ 0.10 (weak) |
| CC76-100 | 0.09 ~ 0.00 (negligible) |

CCs with r > 0.3: **27개**
CCs with r > 0.1: 75개

### CCA 감정 프로필 (PCA50 → CCA30, 이전 실행)

| CC | r | Top emotion | A | V |
|----|---|-----------|---|---|
| CC1 | 0.733 | Annoyance (+0.44) | +0.23 | -0.14 |
| CC2 | 0.609 | Aesthetic apprec. (+0.46) | +0.13 | ~0 |
| CC3 | 0.563 | Interest (-0.18) | +0.05 | +0.07 |
| CC4 | 0.521 | Uncomfortable (-0.29) | -0.12 | +0.07 |
| CC5 | 0.472 | Amusement (+0.23) | -0.06 | +0.05 |

Subject-level CC1: 0.671 ± 0.013 (5명)

### 감정 디코딩 전체 비교

| Method | Direction | Dims | Cat R² | AV R² | Cat/VA |
|--------|-----------|------|--------|-------|--------|
| Forward PCA PC1-3 | Brain→Video | 3 | 0.055 | 0.038 | **1.44** |
| Forward PCA PC1-10 | Brain→Video | 10 | 0.109 | 0.070 | **1.55** |
| Forward PCA all 100 | Brain→Video | 100 | 0.170 | 0.135 | 1.26 |
| CCA (30, PCA50) | Brain↔Video | 30 | 0.154 | 0.121 | 1.28 |
| Reverse Brain PC1-3 | Video→Brain | 3 | 0.016 | 0.026 | **0.61** |
| Reverse Brain PC1-10 | Video→Brain | 10 | 0.043 | 0.071 | **0.60** |
| Reverse Brain all 100 | Video→Brain | 100 | 0.055 | 0.091 | **0.60** |

---

## 6. 아직 안 한 것 (To-Do)

### 6.1 CCA 100 emotion correlation + decoding
CCA 100 결과로 감정 프로필 업데이트 필요 (현재 CCA 30 기준)

### 6.2 CCA PCA sweep robustness
n_pca = 50, 100, 200으로 CCA 반복 → 결과 안정성 확인

### 6.3 Variance Partitioning
Behavior = f(Stimulus) + f(Brain) + shared + residual

### 6.4 Brain Residual Analysis
V-JEPA2로 설명 못하는 뇌의 고유 감정 정보

### 6.5 Partial Mantel test
r(brain, behavior | stimulus) > 0?
