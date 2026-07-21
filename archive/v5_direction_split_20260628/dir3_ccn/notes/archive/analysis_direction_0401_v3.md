# Analysis Direction: Neural-Video Emotion Space Alignment
## Beyond Horikawa — Direct Comparison of Neural and Computational Emotion Spaces

---

## 핵심 질문

> **뇌의 감정 표상 공간과 video model의 감정 표상 공간은 얼마나 직접적으로 대응하는가?**
> **어떤 감정에서 수렴하고 어떤 감정에서 diverge하는가?**
> **두 공간이 가장 잘 수렴하는 차원수는 몇인가?**

---

## 데이터 및 모델

```
Brain (공유 구조):
    Brain-JEPA embedding:  (5, 2196, 768)
    → 5명 subject-averaged → (2196, 768)
    → Subject-invariant neural emotion geometry

Video:
    V-JEPA2:  (2196, 1408)
    CLIP:     (2196, 512)

Metadata:
    score_0 ~ score_33:  (2196,) × 34   # 감정 연속 score (0~1)
    arousal / valence / dominance:  (2196,)
```

---

## 분석 0: Brain-JEPA Subject-Invariance 확인

### 목적
Brain-JEPA가 subject-invariant한 것이 모델의 특성인가, 아니면 데이터 자체의 특성인가를 구분한다. 이것이 Brain-JEPA를 공유된 neural emotion geometry의 대표로 사용하는 것을 정당화한다.

### 방법

```python
# Brain-JEPA: 5×5 cross-subject prediction
# V-JEPA2 embedding → subject별 Brain-JEPA embedding 예측
# 이미 완료: diagonal ≈ off-diagonal ≈ 0.986
# → Brain-JEPA가 subject-invariant

# Raw fMRI: 5×5 cross-subject RSA
# 이미 완료: off-diagonal mean = 0.083
# → Raw fMRI는 subject마다 다름
```

### 해석

```
Raw fMRI cross-subject RSA:    0.083  (개인마다 다름)
Brain-JEPA cross-subject RSA:  0.347  (subject-invariant)

결론:
    개인화 구조는 raw fMRI에 존재하지만
    Brain-JEPA는 이를 압축하고 공유 구조만 추출함
    → Brain-JEPA = 뇌의 공유된 감정 geometry의 대표
    → 이후 모든 분석은 Brain-JEPA subject-averaged embedding 사용
```

---

## 분석 1: Subject별 Brain-JEPA RSM 구성

### 목적
Brain-JEPA embedding으로 subject별 RSM을 만들고, 5명 결과를 하나의 figure에 보여준다. Horikawa 방식과 동일하게 subject별 일관성을 확인한다.

### 방법

```python
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

brain_jepa = np.load("brain_jepa_embeddings.npy")  # (5, 2196, 768)

# Subject별 RSM
rsm_brain_per_subject = {}
for s in range(5):
    rsm_brain_per_subject[s] = cosine_similarity(brain_jepa[s])  # (2196, 2196)

# Subject-averaged RSM
rsm_brain_mean = np.mean(
    [rsm_brain_per_subject[s] for s in range(5)], axis=0
)  # (2196, 2196)
```

### 출력
- `rsm_brain_per_subject`: 5개의 (2196, 2196) RSM
- `rsm_brain_mean`: (2196, 2196) — 이후 모든 분석의 기준

---

## 분석 2: Overall CKA — Brain vs Video Models

### 목적
Brain-JEPA의 공유된 neural emotion geometry와 video model embedding이 전체적으로 얼마나 align되는가.

### 방법

```python
# 이미 완료
# V-JEPA2 CKA = 0.1282 (p<0.0001)
# CLIP CKA     = 0.1115 (p<0.0001)
# Δ = +0.0167  (p=0.017)

# Subject별로도 확인
for s in range(5):
    cka_vjepa_s = cka(rsm_brain_per_subject[s], rsm_vjepa2)
    cka_clip_s  = cka(rsm_brain_per_subject[s], rsm_clip)
```

### 해석
두 모델 모두 뇌의 감정 geometry와 유의미하게 align되지만 절대값이 낮다 (0.11~0.13). 이 gap이 Brain Tuning의 motivation이 된다.

---

## 분석 3: Procrustes Alignment — 두 공간을 같은 좌표계로

### 목적
RSM 기반 CKA는 간접 비교다. Procrustes로 두 공간을 같은 좌표계에 올려서 직접 비교한다. 어떤 비디오에서, 어떤 감정에서 두 공간이 멀리 있는지를 정량화한다.

### 방법

```python
from scipy.spatial import procrustes
from sklearn.decomposition import PCA

k = 27  # 초기값, 분석 5에서 최적 k 탐색

# Step 1: PCA로 차원 축소
pca_brain = PCA(n_components=k)
pca_vjepa = PCA(n_components=k)
pca_clip  = PCA(n_components=k)

brain_k = pca_brain.fit_transform(brain_jepa_mean)      # (2196, k)
vjepa_k = pca_vjepa.fit_transform(vjepa2_embeddings)    # (2196, k)
clip_k  = pca_clip.fit_transform(clip_embeddings)       # (2196, k)

# Step 2: Procrustes alignment
# brain을 기준으로 video model을 최적 회전/스케일링
brain_std, vjepa_aligned, disparity_vjepa = procrustes(brain_k, vjepa_k)
brain_std, clip_aligned,  disparity_clip  = procrustes(brain_k, clip_k)

print(f"Procrustes disparity — Brain vs V-JEPA2: {disparity_vjepa:.4f}")
print(f"Procrustes disparity — Brain vs CLIP:    {disparity_clip:.4f}")

# Step 3: 비디오별 alignment error
# 각 비디오가 두 공간에서 얼마나 떨어져 있는가
error_vjepa = np.linalg.norm(brain_std - vjepa_aligned, axis=1)  # (2196,)
error_clip  = np.linalg.norm(brain_std - clip_aligned,  axis=1)  # (2196,)
```

### 감정별 alignment error 계산

```python
# 각 감정 i에서 두 공간의 거리가 얼마나 큰가
emotion_error_vjepa = {}
emotion_error_clip  = {}

for i in range(34):
    score_i = metadata[f"score_{i}"].values  # (2196,)
    
    # score가 높은 비디오들의 alignment error
    # weighted average: score를 가중치로 사용
    emotion_error_vjepa[i] = np.average(error_vjepa, weights=score_i)
    emotion_error_clip[i]  = np.average(error_clip,  weights=score_i)

# 결과: 어떤 감정에서 두 공간이 가장 멀리 있는가
# → Brain Tuning의 target
```

---

## 분석 4: Cross-space RSA — 감정별 alignment

### 목적
각 감정에 대해 뇌 공간과 video 공간의 구조가 얼마나 일치하는지를 측정한다. 어떤 감정에서 두 공간이 수렴하고 어디서 diverge하는지 정량화한다.

### 방법

```python
from scipy.stats import spearmanr

results = {}

for i in range(34):
    score_i = metadata[f"score_{i}"].values  # (2196,)
    
    # Emotion kernel: 두 자극이 모두 감정 i를 강하게 유발할 때 similarity 높음
    E_i = np.outer(score_i, score_i)  # (2196, 2196)
    
    tri = np.triu_indices(2196, k=1)
    e_flat = E_i[tri]
    
    # 각 공간이 감정 i의 구조를 얼마나 반영하는가
    rsa_brain  = spearmanr(rsm_brain_mean[tri], e_flat).statistic
    rsa_vjepa  = spearmanr(rsm_vjepa2[tri],     e_flat).statistic
    rsa_clip   = spearmanr(rsm_clip[tri],        e_flat).statistic
    
    results[i] = {
        'brain':      rsa_brain,
        'vjepa2':     rsa_vjepa,
        'clip':       rsa_clip,
        'divergence': abs(rsa_brain - rsa_vjepa),  # 두 공간의 차이
        'alignment':  min(rsa_brain, rsa_vjepa)    # 두 공간이 모두 잘 표현할 때 높음
    }
```

### 출력: 감정별 profile

```
감정            Brain RSA    V-JEPA2 RSA    CLIP RSA    Divergence
Relief          0.045        0.032          0.086       0.013  ← 낮음: 수렴
Annoyance       0.044        0.084          0.113       0.040
Uncomfortable   0.035        0.089          0.223       0.054  ← 높음: diverge
...

Divergence 높음 → Brain Tuning의 target
Divergence 낮음 → 두 공간이 이미 수렴
```

---

## 분석 5: k Sweep — 최적 차원수 탐색

### 핵심 아이디어

Cowen & Keltner (2017): 행동 데이터에서 감정 공간은 27차원이 최적

Horikawa et al. (2020): 뇌에서도 27개 카테고리 구조 확인

우리: 뇌와 video model이 가장 잘 수렴하는 차원수는 몇인가?

> **만약 k=27 근방에서 최적이 나온다면, 행동(Cowen) + 뇌(Horikawa) + 모델(우리) 세 레벨에서 감정 표상의 최적 차원수가 수렴한다.**

### 왜 두 가지 기준이 필요한가

Procrustes disparity만 보면 k가 커질수록 자연히 낮아지는 경향이 있어서 최적 k를 찾기 어렵다. 따라서 두 가지 기준을 함께 사용한다.

```
기준 1 — Procrustes disparity elbow:
    disparity가 급격히 감소하다가 완만해지는 지점
    두 공간이 충분히 align되기 시작하는 k

기준 2 — Emotion decoding accuracy plateau:
    accuracy가 더 이상 크게 증가하지 않는 지점
    감정 표상에 필요한 충분한 차원수

최적 k = 두 기준이 수렴하는 지점
```

### 방법

```python
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler

k_values = [3, 5, 7, 10, 15, 20, 25, 27, 30, 34, 40, 50, 75, 100]

disparity_vjepa       = []
disparity_clip        = []
decoding_acc_brain    = []
decoding_acc_vjepa    = []
decoding_acc_clip     = []

emotion_scores = metadata[[f"score_{i}" for i in range(34)]].values  # (2196, 34)

for k in k_values:
    # PCA
    brain_k = PCA(n_components=k).fit_transform(brain_jepa_mean)
    vjepa_k = PCA(n_components=k).fit_transform(vjepa2_embeddings)
    clip_k  = PCA(n_components=k).fit_transform(clip_embeddings)
    
    # Procrustes disparity
    _, _, d_vjepa = procrustes(brain_k, vjepa_k)
    _, _, d_clip  = procrustes(brain_k, clip_k)
    disparity_vjepa.append(d_vjepa)
    disparity_clip.append(d_clip)
    
    # Emotion decoding accuracy (Ridge + 5-fold CV)
    scaler = StandardScaler()
    
    for name, emb_k in [('brain', brain_k), ('vjepa', vjepa_k), ('clip', clip_k)]:
        emb_scaled = scaler.fit_transform(emb_k)
        acc_per_emotion = []
        for j in range(34):
            r2 = cross_val_score(
                Ridge(alpha=1.0), emb_scaled, emotion_scores[:, j],
                cv=5, scoring='r2'
            ).mean()
            acc_per_emotion.append(max(r2, 0))  # negative R² → 0
        
        if name == 'brain':
            decoding_acc_brain.append(np.mean(acc_per_emotion))
        elif name == 'vjepa':
            decoding_acc_vjepa.append(np.mean(acc_per_emotion))
        else:
            decoding_acc_clip.append(np.mean(acc_per_emotion))
```

### 시각화

```python
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 왼쪽: Procrustes disparity vs k
axes[0].plot(k_values, disparity_vjepa, 'b-o', label='Brain vs V-JEPA2')
axes[0].plot(k_values, disparity_clip,  'r-o', label='Brain vs CLIP')
axes[0].axvline(x=27, color='gray', linestyle='--', alpha=0.7, label='k=27 (Cowen)')
axes[0].set_xlabel('Number of dimensions (k)')
axes[0].set_ylabel('Procrustes disparity (lower = better)')
axes[0].set_title('Alignment quality vs dimensionality')
axes[0].legend()

# 오른쪽: Emotion decoding accuracy vs k
axes[1].plot(k_values, decoding_acc_brain, 'g-o', label='Brain-JEPA')
axes[1].plot(k_values, decoding_acc_vjepa, 'b-o', label='V-JEPA2')
axes[1].plot(k_values, decoding_acc_clip,  'r-o', label='CLIP')
axes[1].axvline(x=27, color='gray', linestyle='--', alpha=0.7, label='k=27 (Cowen)')
axes[1].set_xlabel('Number of dimensions (k)')
axes[1].set_ylabel('Emotion decoding R²')
axes[1].set_title('Emotion predictability vs dimensionality')
axes[1].legend()

plt.tight_layout()
plt.savefig('figures/k_sweep_analysis.png', dpi=300, bbox_inches='tight')
```

### 기대 결과 시나리오

| 시나리오 | 결과 | 해석 |
|---------|------|------|
| A (강한) | k=27에서 elbow + plateau 동시 | 27차원은 감정의 보편적 구조 |
| B (현실적) | k=20~35에서 안정화 | ~27차원, Cowen과 일치 |
| C (반례) | 최적 k가 27과 명확히 다름 | 레벨 간 차원성 차이 → 새로운 질문 |

---

## 분석 6: UMAP 시각화 — 두 공간의 감정 구조 비교

### 목적
Brain-JEPA 공간과 V-JEPA2 공간의 감정 구조를 같은 컬러 스키마로 시각화해서 직접 비교한다. Horikawa의 UMAP을 확장하여 두 공간이 어떻게 다른지를 보여준다.

### 방법

```python
import umap

# Option A: 각각 따로 UMAP (Horikawa 방식 확장)
rsm_brain_dist = 1 - rsm_brain_mean   # distance matrix
rsm_vjepa_dist = 1 - rsm_vjepa2
rsm_clip_dist  = 1 - rsm_clip

reducer = umap.UMAP(metric='precomputed', random_state=42, n_neighbors=15)

emb_brain = reducer.fit_transform(rsm_brain_dist)   # (2196, 2)
emb_vjepa = reducer.fit_transform(rsm_vjepa_dist)   # (2196, 2)
emb_clip  = reducer.fit_transform(rsm_clip_dist)    # (2196, 2)

# Option B: Procrustes aligned 공간을 함께 UMAP
joint = np.hstack([brain_std, vjepa_aligned])        # (2196, 2k)
emb_joint = umap.UMAP(random_state=42).fit_transform(joint)  # (2196, 2)
```

### 시각화

```python
# 각 비디오를 가장 높은 감정 score로 색칠
top_emotion = np.argmax(
    metadata[[f"score_{i}" for i in range(34)]].values, axis=1
)  # (2196,)

# Figure 구성:
# 왼쪽: Brain-JEPA UMAP
# 가운데: V-JEPA2 UMAP
# 오른쪽: CLIP UMAP
# 동일한 컬러 스키마로 34개 감정 표시
# → 같은 비디오가 두 공간에서 어디에 위치하는가 비교 가능
```

---

## Brain Tuning으로의 연결

```
분석 3, 4의 Divergence가 큰 감정
    → Video model이 뇌의 감정 구조를 잘 못 잡는 감정
    → Brain Tuning의 target
        ↓
Brain Tuning 후:
    Procrustes disparity 감소 → 정량적 개선 지표
    UMAP에서 두 공간이 더 가까워짐 → 시각적 확인
    Divergence가 큰 감정에서 CKA 증가 → 감정별 개선 확인
```

---

## 전체 실행 순서

```
오늘 (3/31):
    분석 0: 이미 완료 (Brain-JEPA subject-invariance 확인)
    분석 1: Brain-JEPA subject별 RSM 계산
    분석 2: Subject별 CKA 확인
    분석 3: Procrustes alignment + 감정별 error
    분석 4: Cross-space RSA (34개 감정)
    분석 5: k sweep 실행

내일 (4/1):
    분석 6: UMAP 시각화
    Figure 제작
    CCN draft 작성

4/2:
    제출
```

---

## 파일 경로

```
/pscratch/sd/s/sjmoon/EmoFM/
├── brain_embeddings/
│   └── brain_jepa_embeddings.npy        (5, 2196, 768)
├── video_embeddings/
│   ├── vjepa2_embeddings.npy            (2196, 1408)
│   └── clip_embeddings.npy             (2196, 512)
├── cka_results/
│   ├── rsm_brain.npy                   (2196, 2196) — Brain-JEPA mean
│   ├── rsm_vjepa2.npy                  (2196, 2196)
│   └── rsm_clip.npy                    (2196, 2196)
└── metadata/
    └── horikawa_meta_data_with_dimension_binary.csv
```
