# Raw fMRI Cross-Subject Analysis

---

## 목적

Brain-JEPA final embedding이 완전히 subject-invariant (r≈0.986)하다는 것이 확인됐다. 이것이 실제로 감정 표상에 개인화된 구조가 없어서인지, 아니면 Brain foundation model이 개인 정보를 압축해서 날린 것인지를 구분해야 한다.

Raw fMRI parcel feature로 같은 분석을 하면 이 둘을 분리할 수 있다.

---

## 데이터 구조

```
fmri[subject, stimulus] = (400,)   # Schaefer 400 parcel activation
전체 shape: (5, 2196, 400)
```

---

## 분석 방법

### Step 1: 피험자별 RSM 계산

각 피험자 s에 대해 2196x2196 RSM을 만든다.

```python
RSM_s[j,k] = cosine_similarity(fmri[s,j], fmri[s,k])
# "피험자 s의 뇌에서 비디오 j와 k가 얼마나 비슷한가"
```

결과: 5개의 RSM, 각각 (2196, 2196)

### Step 2: Cross-subject RSA

모든 피험자 쌍에 대해 RSM 간 Spearman 상관을 계산한다.

```python
RSA(RSM_A, RSM_B) = spearman(RSM_A.upper_triangle, RSM_B.upper_triangle)
```

결과: 5x5 similarity matrix

### Step 3: Diagonal vs Off-diagonal 비교

Diagonal (within-subject): 같은 피험자의 RSM 신뢰도 추정. 데이터를 절반씩 나눠 split-half reliability로 추정.

Off-diagonal (cross-subject): 다른 피험자 RSM 간 상관.

Permutation test로 두 분포의 차이를 검증한다.

### Step 4: Brain-JEPA 결과와 비교

동일한 분석을 Brain-JEPA embedding으로도 수행해서 나란히 비교한다.

```
Raw fMRI:    diagonal vs off-diagonal 차이
Brain-JEPA:  diagonal vs off-diagonal 차이 (≈ 0, 이미 확인)
```

---

## 기대 결과 시나리오

### 시나리오 A (가장 강한 결과)

```
Raw fMRI:    diagonal (0.7~0.8) >> off-diagonal (0.3~0.4)
Brain-JEPA:  diagonal ≈ off-diagonal (≈ 0.986)
```

해석: 개인화된 감정 구조가 raw fMRI에는 존재하지만, Brain foundation model의 final embedding 과정에서 압축/소실된다.

이 경우 스토리:

> Brain foundation models preserve shared affective geometry but suppress individual-specific structure. Individual-specific emotional representations exist in raw neural data but are compressed away at the final representation level.

### 시나리오 B

```
Raw fMRI:    diagonal > off-diagonal (약한 차이)
Brain-JEPA:  diagonal ≈ off-diagonal (≈ 0.986)
```

해석: 감정 표상이 pain과 달리 상당 부분 공유된 구조를 가진다. Brain foundation model이 공유 구조를 잘 포착하는 것은 실제 신경 데이터의 특성을 반영한다.

이 경우 스토리:

> Unlike pain, emotional representations are largely shared across individuals. Brain foundation models faithfully preserve this shared affective geometry.

### 시나리오 C

```
Raw fMRI:    diagonal >> off-diagonal (매우 강한 차이, pain과 유사)
Brain-JEPA:  diagonal ≈ off-diagonal (≈ 0.986)
```

해석: 감정도 pain처럼 개인화가 강하지만, Brain foundation model이 이를 완전히 날린다.

이 경우 스토리:

> Emotional representations are highly individual-specific, similar to pain. Current brain foundation models fail to capture this personalization, limiting their utility for individual-level affective neuroscience.

---

## 왜 이 분석이 중요한가

Brain-JEPA 결과만 있으면 두 가지 해석이 가능하다.

해석 1: 감정 표상에 개인화된 구조가 없다.

해석 2: 개인화된 구조는 있는데, Brain-JEPA가 날린다.

Raw fMRI 분석이 이 둘을 구분해준다.

또한 풀 페이퍼의 핵심 RQ인 "뇌의 감정 표상은 개인화된 구조와 공유된 구조를 동시에 가지는가"에 직접적으로 답한다.

---

## CCN에서의 역할

Raw fMRI 결과 + Brain-JEPA 결과를 나란히 보여주는 것만으로도 강한 Figure 1이 된다.

```
Figure 1: 5x5 RSA matrix 두 개 나란히
    왼쪽: Raw fMRI (개인화 구조 있음)
    오른쪽: Brain-JEPA (subject-invariant)

→ "개인화 구조는 존재하지만 Brain foundation model이 압축한다"
```

이게 Brain Tuning motivation으로 자연스럽게 연결된다.

> 개인화 구조가 날아간 공유 geometry만 가지고는 감정 예측에 한계가 있다. Brain Tuning으로 이 gap을 줄일 수 있는가?

---

## 코드 구조

```python
import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics.pairwise import cosine_similarity

# 1. Load raw fMRI
fmri = np.load("fmri_schaefer400.npy")  # (5, 2196, 400)

# 2. Compute per-subject RSM
rsm_raw = np.zeros((5, 2196, 2196))
for s in range(5):
    rsm_raw[s] = cosine_similarity(fmri[s])  # (2196, 2196)

# 3. Cross-subject RSA
n_sub = 5
rsa_matrix = np.zeros((n_sub, n_sub))
for i in range(n_sub):
    for j in range(n_sub):
        tri_i = rsm_raw[i][np.triu_indices(2196, k=1)]
        tri_j = rsm_raw[j][np.triu_indices(2196, k=1)]
        rsa_matrix[i,j] = spearmanr(tri_i, tri_j).statistic

# 4. Compare diagonal vs off-diagonal
diagonal = rsa_matrix[np.eye(n_sub, dtype=bool)]
off_diagonal = rsa_matrix[~np.eye(n_sub, dtype=bool)]

print(f"Within-subject (diagonal): {diagonal.mean():.4f}")
print(f"Cross-subject (off-diagonal): {off_diagonal.mean():.4f}")
```

---

## 파일 경로 (확인 필요)

```
/pscratch/sd/s/sjmoon/EmoFM/
└── fmri_raw/
    └── fmri_schaefer400.npy    # (5, 2196, 400) — 경로 확인 필요
```
