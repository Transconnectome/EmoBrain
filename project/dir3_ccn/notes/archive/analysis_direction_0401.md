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
