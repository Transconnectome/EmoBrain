# Analysis Direction: fMRI-Video Embedding Space Alignment
## Beyond Horikawa — Direct Comparison of Neural and Computational Emotion Spaces

---

## 핵심 아이디어

Horikawa et al. (2020)은 fMRI에서 감정을 decode할 수 있다는 것을 보였다. 우리는 한 단계 나아가서 **뇌의 감정 표상 공간과 video model의 감정 표상 공간이 얼마나 직접적으로 대응하는가**를 묻는다.

단순한 RSM 간 상관이 아니라, 두 공간을 같은 좌표계에 올려서 **어떤 감정에서 수렴하고 어떤 감정에서 diverge하는가**를 측정한다. 이 divergence가 Brain Tuning의 target이 된다.

---

## 데이터 현황

```
fMRI:
    raw_fmri:  (5, 2196, 450)   # 5 subjects × 2196 videos × 450 parcels
    brain_jepa: (5, 2196, 768)  # 5 subjects × 2196 videos × 768 dim

Video:
    vjepa2:    (2196, 1408)     # 2196 videos × 1408 dim
    clip:      (2196, 512)      # 2196 videos × 512 dim

Metadata:
    score_0 ~ score_33:  (2196,)  # 34개 감정 연속 score (0~1, rater proportion)
    arousal_score:       (2196,)
    valence_score:       (2196,)
    dominance_score:     (2196,)
```

---

## 분석 1: Subject별 fMRI RSM 구성

### 목적
Horikawa 방식대로 subject별로 따로 분석해서 5명 결과를 하나의 figure에 보여준다.

### 방법

```python
# per-subject RSM
fmri_rsm = {}
for s in range(5):
    fmri_rsm[s] = cosine_similarity(raw_fmri[s])  # (2196, 2196)

# subject-averaged RSM
fmri_rsm_mean = np.mean([fmri_rsm[s] for s in range(5)], axis=0)  # (2196, 2196)
```

### 출력
- `fmri_rsm_per_subject`: dict, 5개의 (2196, 2196) RSM
- `fmri_rsm_mean`: (2196, 2196)

---

## 분석 2: Procrustes Alignment — 두 공간을 같은 좌표계로

### 목적
fMRI 공간과 V-JEPA2 공간을 직접 비교하기 위해 같은 좌표계에 올린다.

### 방법

```python
from scipy.spatial import procrustes
from sklearn.decomposition import PCA

# Step 1: PCA로 차원 축소 (같은 차원으로)
k = 50  # 비교할 차원 수 (조정 가능)

pca_fmri = PCA(n_components=k)
pca_vjepa = PCA(n_components=k)

fmri_k = pca_fmri.fit_transform(raw_fmri_mean)   # (2196, k), subject-averaged
vjepa_k = pca_vjepa.fit_transform(vjepa2)         # (2196, k)

# Step 2: Procrustes alignment
# fMRI를 기준으로 V-JEPA2를 최적 회전/스케일링
fmri_std, vjepa_aligned, disparity = procrustes(fmri_k, vjepa_k)

# disparity: 전체 공간 alignment 점수 (낮을수록 잘 align)
print(f"Procrustes disparity (fMRI vs V-JEPA2): {disparity:.4f}")
print(f"Procrustes disparity (fMRI vs CLIP): ...")  # CLIP도 동일하게
```

### 핵심 분석: 비디오별 alignment error

```python
# 각 비디오에 대해 두 공간에서의 위치 차이
alignment_error = np.linalg.norm(fmri_std - vjepa_aligned, axis=1)  # (2196,)

# 감정별 평균 alignment error
for i in range(34):
    score_i = metadata[f"score_{i}"].values  # (2196,)
    # high score 비디오들의 alignment error
    high_score_mask = score_i > score_i.mean()
    emotion_error[i] = alignment_error[high_score_mask].mean()
```

### 출력
- Procrustes disparity: 전체 공간 alignment 수치
- Per-video alignment error: 어떤 비디오에서 두 공간이 멀리 있는가
- Per-emotion alignment error: 어떤 감정에서 두 공간이 diverge하는가

---

## 분석 3: Shared UMAP — 같은 2D 공간에 두 표상 투영

### 목적
fMRI 공간과 V-JEPA2 공간을 같은 2D UMAP에 투영해서 시각적으로 비교한다. Horikawa의 UMAP을 확장해서 두 공간을 직접 overlay한다.

### 방법

```python
import umap

# Option A: RSM 기반 UMAP (Horikawa 방식)
# 각각 따로 UMAP → 같은 컬러 스키마로 비교
reducer_fmri = umap.UMAP(metric='precomputed')
reducer_vjepa = umap.UMAP(metric='precomputed')

# RSM을 distance matrix로 변환
fmri_dist = 1 - fmri_rsm_mean
vjepa_dist = 1 - vjepa_rsm

embedding_fmri = reducer_fmri.fit_transform(fmri_dist)   # (2196, 2)
embedding_vjepa = reducer_vjepa.fit_transform(vjepa_dist) # (2196, 2)

# Option B: Joint UMAP (두 공간을 하나로)
# Procrustes aligned 벡터를 concatenate
joint = np.hstack([fmri_std, vjepa_aligned])  # (2196, 2k)
embedding_joint = umap.UMAP().fit_transform(joint)  # (2196, 2)
```

### 시각화

```python
# 각 비디오를 34개 감정 score로 색칠
# Horikawa 논문과 동일한 방식
# 각 비디오의 색상 = 가장 높은 score를 가진 감정의 색상

# Figure 구성:
# 왼쪽: fMRI UMAP (subject 1~5 + mean)
# 오른쪽: V-JEPA2 UMAP
# 비교: 같은 비디오가 두 공간에서 어디에 위치하는가
```

---

## 분석 4: Cross-space RSA — 감정별 alignment

### 목적
각 감정에 대해 fMRI 공간과 video 공간의 구조가 얼마나 일치하는지를 측정한다. 어떤 감정에서 두 공간이 수렴하고 어디서 diverge하는지 정량화한다.

### 방법

```python
# 각 감정 i에 대해
for i in range(34):
    score_i = metadata[f"score_{i}"].values  # (2196,)
    
    # Emotion kernel (rank-1)
    E_i = np.outer(score_i, score_i)  # (2196, 2196)
    
    # 각 공간이 감정 i 구조를 얼마나 반영하는가
    rsa_fmri_i = spearmanr(
        fmri_rsm_mean[np.triu_indices(2196, k=1)],
        E_i[np.triu_indices(2196, k=1)]
    ).statistic
    
    rsa_vjepa_i = spearmanr(
        vjepa_rsm[np.triu_indices(2196, k=1)],
        E_i[np.triu_indices(2196, k=1)]
    ).statistic
    
    rsa_clip_i = spearmanr(
        clip_rsm[np.triu_indices(2196, k=1)],
        E_i[np.triu_indices(2196, k=1)]
    ).statistic
    
    # alignment: fMRI와 V-JEPA2가 같은 감정 구조를 공유하는가
    alignment_i = min(rsa_fmri_i, rsa_vjepa_i)  # 두 공간이 모두 잘 표현할 때 높음
    divergence_i = abs(rsa_fmri_i - rsa_vjepa_i)  # 두 공간의 차이
```

### 출력: 감정별 alignment/divergence 프로파일

```
감정              fMRI RSA    V-JEPA2 RSA    CLIP RSA    Divergence
Relief            0.045       0.032          0.086       0.013
Annoyance         0.044       0.084          0.113       0.040
Uncomfortable     0.035       0.089          0.223       0.054
...

→ Divergence가 큰 감정 = Brain Tuning의 target
→ Alignment가 높은 감정 = 두 공간이 이미 수렴
```

---

## 분석 5: Subject별 결과 (Horikawa 방식 확장)

### 목적
5명 피험자 각각에 대해 분석을 돌려서 결과의 일관성을 보인다.

### 방법

```python
results_per_subject = {}

for s in range(5):
    fmri_s = raw_fmri[s]  # (2196, 450)
    rsm_s = cosine_similarity(fmri_s)  # (2196, 2196)
    
    # CKA: fMRI_s vs V-JEPA2
    cka_vjepa_s = cka(rsm_s, vjepa_rsm)
    
    # CKA: fMRI_s vs CLIP
    cka_clip_s = cka(rsm_s, clip_rsm)
    
    # Per-emotion RSA
    for i in range(34):
        score_i = metadata[f"score_{i}"].values
        E_i = np.outer(score_i, score_i)
        rsa_fmri_s_i = spearmanr(
            rsm_s[np.triu_indices(2196, k=1)],
            E_i[np.triu_indices(2196, k=1)]
        ).statistic
        
    results_per_subject[s] = {
        'cka_vjepa': cka_vjepa_s,
        'cka_clip': cka_clip_s,
        'per_emotion_rsa': ...
    }

# Figure: 5명 결과 + mean, Horikawa 스타일
```

---

## Figure 구성 (CCN용)

### Figure 1: Neural vs Computational Emotion Space

```
[A] fMRI UMAP (5 subjects + mean)
    각 비디오를 34개 감정으로 색칠
    → 뇌의 감정 공간 구조

[B] V-JEPA2 UMAP
    동일한 컬러 스키마
    → 모델의 감정 공간 구조

[C] Procrustes disparity
    fMRI vs V-JEPA2, fMRI vs CLIP
    subject별 + mean
    → 전체 공간 alignment
```

### Figure 2: Emotion-specific Alignment

```
[A] 34개 감정별 fMRI RSA vs V-JEPA2 RSA scatter plot
    대각선 위: 두 공간이 수렴하는 감정
    대각선 아래: diverge하는 감정
    → Brain Tuning target 시각화

[B] Divergence 상위 감정 vs 하위 감정 예시
    → 어떤 감정이 왜 diverge하는가 해석
```

---

## 분석 6: Optimal Dimensionality — k Sweep

### 핵심 아이디어

Cowen & Keltner (2017)은 인간의 행동 데이터(self-report)에서 감정 공간이 27차원으로 최적 설명된다는 것을 발견했다. Horikawa et al. (2020)은 뇌에서도 27개 카테고리 구조가 확인된다는 것을 보였다.

우리는 세 번째 레벨에서 같은 질문을 한다:

> **fMRI 공간과 video model 공간이 가장 잘 수렴하는 차원수는 몇인가? 그것이 27과 일치하는가?**

만약 k=27 근방에서 두 공간의 alignment가 최적이 된다면, 이는 행동(Cowen), 뇌(Horikawa), 모델(우리) 세 레벨에서 감정 표상의 최적 차원수가 수렴한다는 강력한 주장이 된다.

---

### 왜 k를 바꿔가며 분석해야 하는가

PCA로 fMRI와 V-JEPA2를 각각 k차원으로 줄인 후 Procrustes alignment를 하면, k에 따라 alignment 품질이 달라진다.

k가 너무 작으면: 정보가 부족해서 두 공간을 제대로 비교하지 못함

k가 너무 크면: noise가 포함되어 alignment가 오히려 나빠질 수 있음

k가 최적일 때: 두 공간의 핵심 감정 구조가 가장 잘 align됨

이 최적 k가 감정 표상의 내재적 차원수를 반영한다.

---

### 방법

#### Step 1: k sweep으로 Procrustes disparity 측정

```python
from scipy.spatial import procrustes
from sklearn.decomposition import PCA
import numpy as np

k_values = [3, 5, 7, 10, 15, 20, 25, 27, 30, 34, 40, 50, 75, 100]

disparity_vjepa = []  # fMRI vs V-JEPA2
disparity_clip = []   # fMRI vs CLIP

for k in k_values:
    # fMRI: subject-averaged, (2196, 450) → (2196, k)
    pca_fmri = PCA(n_components=k)
    fmri_k = pca_fmri.fit_transform(raw_fmri_mean)  # (2196, k)
    
    # V-JEPA2: (2196, 1408) → (2196, k)
    pca_vjepa = PCA(n_components=k)
    vjepa_k = pca_vjepa.fit_transform(vjepa2_embeddings)  # (2196, k)
    
    # CLIP: (2196, 512) → (2196, k)
    pca_clip = PCA(n_components=k)
    clip_k = pca_clip.fit_transform(clip_embeddings)  # (2196, k)
    
    # Procrustes: fMRI를 기준으로 각 모델을 최적 정렬
    # disparity: 정렬 후 남은 거리 (낮을수록 잘 align됨)
    _, _, d_vjepa = procrustes(fmri_k, vjepa_k)
    _, _, d_clip = procrustes(fmri_k, clip_k)
    
    disparity_vjepa.append(d_vjepa)
    disparity_clip.append(d_clip)

# 주의: disparity는 k가 커질수록 자연히 감소하는 경향이 있음
# 따라서 disparity만 보면 안 되고, 아래 Step 2와 함께 봐야 함
```

#### Step 2: 각 k에서 emotion decoding accuracy 측정

Procrustes disparity만 보면 k가 커질수록 낮아지는 경향이 있어서 단독으로는 최적 k를 찾기 어렵다. 따라서 각 k에서 실제로 감정을 얼마나 잘 예측하는지를 함께 측정한다.

```python
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler

decoding_accuracy_vjepa = []  # 각 k에서 V-JEPA2로 감정 예측 정확도
decoding_accuracy_fmri = []   # 각 k에서 fMRI로 감정 예측 정확도

for k in k_values:
    pca_fmri = PCA(n_components=k)
    pca_vjepa = PCA(n_components=k)
    
    fmri_k = pca_fmri.fit_transform(raw_fmri_mean)   # (2196, k)
    vjepa_k = pca_vjepa.fit_transform(vjepa2_embeddings)  # (2196, k)
    
    # 각 k차원 표상으로 34개 감정 score 예측
    # target: 34개 감정 score matrix (2196, 34)
    emotion_scores = metadata[[f"score_{i}" for i in range(34)]].values  # (2196, 34)
    
    # Ridge regression + 5-fold cross-validation
    scaler = StandardScaler()
    
    # fMRI k차원으로 감정 예측
    fmri_k_scaled = scaler.fit_transform(fmri_k)
    scores_fmri = []
    for j in range(34):
        cv_score = cross_val_score(
            Ridge(alpha=1.0), fmri_k_scaled, emotion_scores[:, j],
            cv=5, scoring='r2'
        ).mean()
        scores_fmri.append(cv_score)
    decoding_accuracy_fmri.append(np.mean(scores_fmri))
    
    # V-JEPA2 k차원으로 감정 예측
    vjepa_k_scaled = scaler.fit_transform(vjepa_k)
    scores_vjepa = []
    for j in range(34):
        cv_score = cross_val_score(
            Ridge(alpha=1.0), vjepa_k_scaled, emotion_scores[:, j],
            cv=5, scoring='r2'
        ).mean()
        scores_vjepa.append(cv_score)
    decoding_accuracy_vjepa.append(np.mean(scores_vjepa))
```

#### Step 3: 최적 k 판단

두 가지 기준을 함께 사용한다.

```
기준 1 — Procrustes disparity elbow:
    disparity가 급격히 감소하다가 완만해지는 지점 (elbow)
    이 지점이 두 공간이 충분히 align되기 시작하는 k

기준 2 — Emotion decoding accuracy plateau:
    accuracy가 더 이상 크게 증가하지 않는 지점
    이 지점이 감정 표상에 필요한 충분한 차원수

최적 k = 두 기준이 수렴하는 지점
```

#### Step 4: 결과 시각화

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 왼쪽: Procrustes disparity vs k
axes[0].plot(k_values, disparity_vjepa, 'b-o', label='fMRI vs V-JEPA2')
axes[0].plot(k_values, disparity_clip, 'r-o', label='fMRI vs CLIP')
axes[0].axvline(x=27, color='gray', linestyle='--', label='k=27 (Cowen)')
axes[0].set_xlabel('Number of dimensions (k)')
axes[0].set_ylabel('Procrustes disparity (lower = better alignment)')
axes[0].set_title('Alignment quality vs dimensionality')
axes[0].legend()

# 오른쪽: Emotion decoding accuracy vs k
axes[1].plot(k_values, decoding_accuracy_fmri, 'b-o', label='fMRI')
axes[1].plot(k_values, decoding_accuracy_vjepa, 'r-o', label='V-JEPA2')
axes[1].axvline(x=27, color='gray', linestyle='--', label='k=27 (Cowen)')
axes[1].set_xlabel('Number of dimensions (k)')
axes[1].set_ylabel('Emotion decoding accuracy (R²)')
axes[1].set_title('Emotion predictability vs dimensionality')
axes[1].legend()

plt.tight_layout()
plt.savefig('figures/k_sweep_analysis.png', dpi=300)
```

---

### 기대 결과 시나리오

#### 시나리오 A (가장 강한 결과)
```
k=27 근방에서:
    Procrustes disparity: elbow point
    Emotion decoding accuracy: plateau 시작

해석:
    뇌와 모델이 가장 잘 수렴하는 차원수 = 27
    행동(Cowen) + 뇌(Horikawa) + 모델(우리) 세 레벨 수렴
    "27차원은 감정 표상의 보편적 구조다"
```

#### 시나리오 B (현실적)
```
k=20~35 구간에서 plateau:
    명확한 elbow는 없지만 ~27 근방에서 안정화

해석:
    "~27차원 구조가 감정 표상에 충분하다"
    Cowen의 발견과 일치하는 범위
```

#### 시나리오 C (흥미로운 반례)
```
최적 k가 27과 명확히 다름:
    예: k=10에서 plateau, 또는 k=50에서도 계속 증가

해석:
    행동/뇌/모델의 최적 차원수가 다름
    "왜 다른가?"가 새로운 연구 질문이 됨
    이것도 중요한 finding
```

---

### 풀 페이퍼와의 연결

이 분석은 풀 페이퍼 Figure 3 (공유 구조의 차원성) 의 핵심 실험이다.

```
CCN:
    k sweep 결과 보여주기
    "k=27 근방에서 수렴한다" preliminary finding

풀 페이퍼:
    + Mantel test: k=27에서 행동/뇌/모델 세 RSM 간 상관
    + Intrinsic dimensionality estimation (TwoNN 등)
    + Subject별로 최적 k가 일관되는가
    → "27차원은 감정의 보편적 계산적 구조"라는 강한 주장
```

---

## Brain Tuning으로의 연결

```
분석 4의 Divergence가 큰 감정들
    → Video model이 뇌의 감정 구조를 잘 못 잡는 감정
    → Brain Tuning의 target

분석 3의 UMAP 비교
    → Tuning 전후 두 공간이 얼마나 가까워지는가 시각화 가능

분석 2의 Procrustes disparity
    → Brain Tuning 전후 disparity 감소 → 정량적 평가 지표
```

---

## 실행 순서

```
오늘:
    1. Subject별 raw fMRI RSM 계산 → fmri_rsm_per_subject
    2. Subject-averaged RSM → fmri_rsm_mean
    3. Procrustes alignment (fMRI vs V-JEPA2, fMRI vs CLIP)
    4. Per-emotion RSA (분석 4) — subject별 + mean

내일:
    5. UMAP 시각화 (분석 3)
    6. Figure 제작
    7. CCN draft 작성
```

---

## 파일 경로

```
/pscratch/sd/s/sjmoon/EmoFM/
├── raw_fmri_results/
│   ├── fmri_raw.npy                    (5, 2196, 450)
│   └── raw_fmri_rsa_results.npz        cross-subject RSA
├── video_embeddings/
│   ├── vjepa2_embeddings.npy           (2196, 1408)
│   └── clip_embeddings.npy             (2196, 512)
├── cka_results/
│   ├── rsm_brain.npy                   (2196, 2196) — Brain-JEPA mean
│   ├── rsm_vjepa2.npy                  (2196, 2196)
│   └── rsm_clip.npy                    (2196, 2196)
└── metadata/
    └── horikawa_meta_data_with_dimension_binary.csv
```
