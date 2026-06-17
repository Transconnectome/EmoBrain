# Permutation Test — Brain-Predictable PC 정의 교체

## 목적

기존 r² > 0.01 threshold를 permutation test 기반 유의성 검증으로 교체.
"왜 0.01이냐"는 reviewer 질문에 대응.

---

## 방법

### 기존 방법 (교체 대상)
```python
# 각 PC에 대해 Brain-JEPA → PC_i ridge regression R² 계산
# R² > 0.01 이면 brain-predictable로 정의
```

### 새 방법: Permutation test

```python
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
import numpy as np

brain = np.load("brain_jepa_embeddings.npy").mean(axis=0)  # (2196, 768)
vjepa_pcs = PCA(100).fit_transform(vjepa)  # (2196, 100)

n_perm = 1000
alpha = 0.05
model = Pipeline([('scaler', StandardScaler()), ('ridge', Ridge(alpha=1.0))])

r2_obs = np.zeros(100)
r2_null = np.zeros((100, n_perm))

for i in range(100):
    target = vjepa_pcs[:, i]
    
    # Observed R²
    r2_obs[i] = max(cross_val_score(model, brain, target, cv=5, scoring='r2').mean(), 0)
    
    # Null distribution: permute target labels
    for p in range(n_perm):
        target_perm = np.random.permutation(target)
        r2_null[i, p] = max(cross_val_score(model, brain, target_perm, cv=5, scoring='r2').mean(), 0)

# p-value: proportion of null R² >= observed R²
p_values = np.mean(r2_null >= r2_obs[:, None], axis=1)

# FDR correction (Benjamini-Hochberg)
from statsmodels.stats.multitest import multipletests
rejected, p_corrected, _, _ = multipletests(p_values, alpha=0.05, method='fdr_bh')

# brain-predictable PCs: FDR-corrected p < 0.05
brain_pred_mask = rejected
brain_pred_pcs = np.where(brain_pred_mask)[0]

print(f"Brain-predictable PCs: {brain_pred_pcs + 1}")  # 1-indexed
print(f"Observed R²: {r2_obs[brain_pred_mask]}")
print(f"p-values (corrected): {p_corrected[brain_pred_mask]}")
```

---

## 기대 결과

- PC1, PC2, PC3가 유의하게 나오면 → 기존 결과 그대로 유지, threshold 문제 해결
- PC 수가 달라지면 → 그에 맞게 결과 업데이트 필요

---

## Methods 문장 교체

기존:
> PCs with r² > 0.01 were defined as brain-predictable.

교체:
> The statistical significance of each PC's brain-predictability was assessed via permutation testing (n = 1,000 permutations of target labels), and PCs surviving FDR correction (Benjamini-Hochberg, q < 0.05) were defined as brain-predictable.

---

## 파일 경로

```
brain:  /pscratch/sd/s/sjmoon/EmoFM/brain_embeddings/brain_jepa_embeddings.npy
vjepa:  /pscratch/sd/s/sjmoon/EmoFM/video_embeddings/vjepa2_embeddings.npy
output: /pscratch/sd/s/sjmoon/EmoFM/CCN/results/permutation_test_results.npz
  - r2_obs: (100,)
  - r2_null: (100, 1000)
  - p_values: (100,)
  - p_corrected: (100,)
  - brain_pred_mask: (100,)
```

---

## 결과 보고 형식

```
완료 후 출력:
- Brain-predictable PCs (1-indexed): [?, ?, ...]
- Observed R²: [?, ?, ...]
- FDR-corrected p-values: [?, ?, ...]
- 기존 threshold 결과와 동일한가? Yes/No
```
