# 추가 실험 스펙 — CCN 2-page claim 확보용

**목적**: "Brain-video alignment가 k≈27에서 수렴/최적화된다"는 claim을 검증  
**기반 파일**: 기존 k-sweep 결과 (`k_sweep_results.npz`, `raw_k_sweep_results.npz`)

---

## 배경 / 문제

기존 k-sweep (`05_k_sweep.py`)에서 측정한 것:
- R²_brain: brain_k → emotion score 예측력
- R²_vjepa: vjepa_k → emotion score 예측력
- Procrustes disparity(brain_k, vjepa_k)

**문제**: R²_vjepa, R²_clip은 k=100까지 계속 증가. k=27에서 특별한 지점이 없음.  
**필요한 것**: brain과 video model 사이의 **직접적인 alignment**가 k에 따라 어떻게 변하는지.

---

## 실험 1: CKA(brain_k, vjepa_k) vs k

### 핵심 질문
Brain embedding과 V-JEPA2 embedding 사이의 CKA가 k에 따라 어떻게 변하는가?  
k=27 근방에서 plateau 또는 elbow가 존재하는가?

### 방법

```python
k_values = [3, 5, 7, 10, 15, 20, 25, 27, 30, 34, 40, 50, 75, 100]

brain_mean = np.load("brain_jepa_embeddings.npy").mean(axis=0)  # (2196, 768)
vjepa = np.load("vjepa2_embeddings.npy")   # (2196, 1408)
clip  = np.load("clip_embeddings.npy")     # (2196, 512)

# CKA 정의 (linear kernel)
def linear_CKA(X, Y):
    # centered Gram matrices
    ...

cka_brain_vjepa = []
cka_brain_clip  = []

for k in k_values:
    brain_k = PCA(n_components=k).fit_transform(brain_mean)
    vjepa_k = PCA(n_components=k).fit_transform(vjepa)
    clip_k  = PCA(n_components=k).fit_transform(clip)
    
    cka_brain_vjepa.append(linear_CKA(brain_k, vjepa_k))
    cka_brain_clip.append(linear_CKA(brain_k, clip_k))
```

### 기대 output
- `cka_vs_k_results.npz`: k별 CKA(brain, vjepa), CKA(brain, clip)
- figure: CKA vs k 곡선 (x축: k, y축: CKA, 두 선: V-JEPA2 / CLIP, vertical line at k=27)

### 해석 기준
- k=27 근방에서 **elbow 또는 plateau** → "27차원이 brain-video alignment의 saturation point" claim 가능
- 계속 올라가면 → claim 불가, 다른 방향으로

---

## 실험 2: RSA(RSM_brain_k, RSM_vjepa_k) vs k

### 핵심 질문
각 k에서 PCA 축소한 embedding으로 RSM을 만들고, brain RSM과 vjepa RSM의 Spearman r이 k에 따라 어떻게 변하는가?

### 방법

```python
from scipy.stats import spearmanr
from sklearn.metrics.pairwise import cosine_similarity

rsa_brain_vjepa = []
rsa_brain_clip  = []

for k in k_values:
    brain_k = PCA(n_components=k).fit_transform(brain_mean)
    vjepa_k = PCA(n_components=k).fit_transform(vjepa)
    clip_k  = PCA(n_components=k).fit_transform(clip)
    
    rsm_b = cosine_similarity(brain_k)
    rsm_v = cosine_similarity(vjepa_k)
    rsm_c = cosine_similarity(clip_k)
    
    tri = np.triu_indices(2196, k=1)
    
    rsa_brain_vjepa.append(spearmanr(rsm_b[tri], rsm_v[tri]).statistic)
    rsa_brain_clip.append(spearmanr(rsm_b[tri], rsm_c[tri]).statistic)
```

### 기대 output
- `rsa_vs_k_results.npz`
- figure: RSA(brain, model) vs k 곡선

---

## 실험 3: Emotion decoding — brain-predictable dimensions

### 핵심 질문
V-JEPA2의 top-k PCA 차원 중에서 **brain이 예측 가능한 차원**이 어디에 집중되는가?  
Brain이 예측 가능한 차원 수가 k=27 근방에서 saturation되는가?

### 방법

```python
# V-JEPA2의 PCA 각 component를 brain embedding으로 예측
# brain → vjepa PC_i 예측 R² 를 i=1..100에 대해 계산

from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score

brain_mean = ...  # (2196, 768)
vjepa_pca = PCA(n_components=100).fit(vjepa)
vjepa_pcs = vjepa_pca.transform(vjepa)  # (2196, 100)

r2_per_dim = []
for i in range(100):
    target = vjepa_pcs[:, i]
    r2 = cross_val_score(Ridge(alpha=1.0), brain_mean, target, cv=5, scoring='r2').mean()
    r2_per_dim.append(max(r2, 0))

# 누적합: cumulative R² as function of how many dims included
cumulative_r2 = np.cumsum(r2_per_dim)
```

### 기대 output
- `brain_predictable_dims.npz`: r2_per_dim (100,), cumulative_r2 (100,)
- figure: cumulative R² vs PC index — saturation point가 몇 번째 PC인지

### 해석 기준
- cumulative curve가 k=27 근방에서 knee → "brain이 예측 가능한 video model의 structure는 ~27차원" claim 가능
- 이게 가장 강한 claim이 될 수 있음

---

## 우선순위

1. **실험 3 먼저** (가장 novel한 claim 가능성)
2. **실험 1** (빠르고 직접적)
3. **실험 2** (실험 1과 비슷하지만 RSM 기반)

---

## 파일 경로

```
brain:  /pscratch/sd/s/sjmoon/EmoFM/brain_embeddings/brain_jepa_embeddings.npy  (5,2196,768)
vjepa:  /pscratch/sd/s/sjmoon/EmoFM/video_embeddings/vjepa2_embeddings.npy      (2196,1408)
clip:   /pscratch/sd/s/sjmoon/EmoFM/video_embeddings/clip_embeddings.npy        (2196,512)
meta:   /pscratch/sd/s/sjmoon/EmoFM/metadata/horikawa_meta_data_with_dimension_binary.csv
output: /pscratch/sd/s/sjmoon/EmoFM/CCN/results/
figure: /pscratch/sd/s/sjmoon/EmoFM/CCN/figures/
```

---

## 결과 보고 형식

각 실험 완료 후 다음을 출력:

```
[실험 번호] 완료
- k별 수치 테이블 (k=3,5,7,10,15,20,25,27,30,34,40,50,75,100)
- elbow/plateau 여부 및 위치
- k=27에서의 값과 max값 대비 %
- figure 저장 경로
```
