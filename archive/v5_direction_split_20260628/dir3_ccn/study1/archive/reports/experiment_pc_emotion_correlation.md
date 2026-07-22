# Experiment: Brain-Predictable PC × Emotion Correlation

## 왜 필요한가

Script 10 (Exp 3)에서 brain이 V-JEPA2의 상위 3개 PC, CLIP의 상위 4~5개 PC만 decode할 수 있다는 결과가 나왔다. 그런데 이 PC들이 **무엇을 represent하는지** 모른다. 감정 관련 차원인지, low-level visual feature인지에 따라 paper의 main claim이 완전히 달라진다:

- 감정과 correlate → "Brain selectively reads the affective subspace of video representations"
- 감정과 무관 → "Brain-model alignment is driven by shared perceptual structure, not emotion"

이 실험 하나가 CCN paper의 핵심 claim을 결정한다.

---

## 무엇을 해야 하는가

### 입력 데이터

```
vjepa2_embeddings.npy          — (2196, 1408)
clip_embeddings.npy            — (2196, 512)
brain_jepa_embeddings.npy      — (5, 2196, 768)  → mean over subjects → (2196, 768)
horikawa_meta_data_with_dimension_binary.csv  — score_0 ~ score_33 (34개 감정 연속 score)
```

파일 경로: `/pscratch/sd/s/sjmoon/EmoFM/` 하위

### Step 1: PC 추출

```python
from sklearn.decomposition import PCA
import numpy as np

vjepa = np.load("video_embeddings/vjepa2_embeddings.npy")   # (2196, 1408)
clip = np.load("video_embeddings/clip_embeddings.npy")      # (2196, 512)

# 각 모델에 대해 상위 100개 PC 추출
vjepa_pca = PCA(n_components=100)
vjepa_pcs = vjepa_pca.fit_transform(vjepa)  # (2196, 100)

clip_pca = PCA(n_components=100)
clip_pcs = clip_pca.fit_transform(clip)     # (2196, 100)
```

### Step 2: 각 PC와 34개 감정 score 사이 Spearman correlation

```python
import pandas as pd
from scipy.stats import spearmanr

meta = pd.read_csv("metadata/horikawa_meta_data_with_dimension_binary.csv")
emotion_names = [col for col in meta.columns if col.startswith("score_")]
# score_0 ~ score_33, 총 34개
emotion_scores = meta[emotion_names].values  # (2196, 34)

# 감정 이름 매핑 (score_0 = Admiration, score_1 = Adoration, ... 순서는 metadata에서 확인)

# V-JEPA2
corr_vjepa = np.zeros((100, 34))   # (PC, emotion)
pval_vjepa = np.zeros((100, 34))
for i in range(100):
    for j in range(34):
        r, p = spearmanr(vjepa_pcs[:, i], emotion_scores[:, j])
        corr_vjepa[i, j] = r
        pval_vjepa[i, j] = p

# CLIP도 동일하게
corr_clip = np.zeros((100, 34))
pval_clip = np.zeros((100, 34))
for i in range(100):
    for j in range(34):
        r, p = spearmanr(clip_pcs[:, i], emotion_scores[:, j])
        corr_clip[i, j] = r
        pval_clip[i, j] = p
```

### Step 3: Brain-predictable 여부와 결합

Script 10 Exp 3에서 이미 계산한 `r2_per_dim` (brain → 각 PC의 R²)을 로드한다.

```python
# brain_predictable_dims.npz에서 로드
data = np.load("results/brain_predictable_dims.npz", allow_pickle=True)
# V-JEPA2: r2_per_dim_vjepa (100,)
# CLIP: r2_per_dim_clip (100,)
```

핵심 비교:
- **Brain-predictable PC** (R² > 0.01 등 threshold): 이 PC들의 emotion correlation profile
- **Brain-unpredictable PC** (R² ≈ 0): 이 PC들의 emotion correlation profile
- 둘의 차이 → brain이 선택적으로 affective 차원을 읽는지 확인

### Step 4: 시각화

#### Figure A: Heatmap (주요 PC × 34 emotions)

```python
import matplotlib.pyplot as plt
import seaborn as sns

fig, axes = plt.subplots(1, 2, figsize=(20, 6))

# V-JEPA2: 상위 10개 PC만
sns.heatmap(corr_vjepa[:10, :], ax=axes[0], cmap='RdBu_r', center=0,
            xticklabels=emotion_label_list, yticklabels=[f'PC{i+1}' for i in range(10)])
axes[0].set_title('V-JEPA2 PC × Emotion Spearman r')

# CLIP: 상위 10개 PC
sns.heatmap(corr_clip[:10, :], ax=axes[1], cmap='RdBu_r', center=0,
            xticklabels=emotion_label_list, yticklabels=[f'PC{i+1}' for i in range(10)])
axes[1].set_title('CLIP PC × Emotion Spearman r')

plt.tight_layout()
plt.savefig('figures/pc_emotion_heatmap.png', dpi=300, bbox_inches='tight')
```

#### Figure B: Brain-predictable vs unpredictable PC의 emotion correlation 비교

```python
# V-JEPA2 기준
brain_pred_mask = r2_per_dim_vjepa > 0.01   # brain-predictable PCs
brain_unpred_mask = r2_per_dim_vjepa <= 0.01

# 각 감정에 대해, brain-predictable PC들의 max |correlation|
max_corr_pred = np.max(np.abs(corr_vjepa[brain_pred_mask, :]), axis=0)     # (34,)
max_corr_unpred = np.max(np.abs(corr_vjepa[brain_unpred_mask, :]), axis=0) # (34,)

# bar plot 비교
fig, ax = plt.subplots(figsize=(14, 5))
x = np.arange(34)
ax.bar(x - 0.2, max_corr_pred, 0.4, label='Brain-predictable PCs', color='steelblue')
ax.bar(x + 0.2, max_corr_unpred, 0.4, label='Brain-unpredictable PCs', color='lightcoral')
ax.set_xticks(x)
ax.set_xticklabels(emotion_label_list, rotation=90)
ax.set_ylabel('Max |Spearman r| with emotion')
ax.legend()
plt.tight_layout()
plt.savefig('figures/pc_brain_pred_emotion.png', dpi=300, bbox_inches='tight')
```

#### Figure C: PC scatter — R²(brain) vs max emotion correlation

```python
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

for ax, name, r2, corr in [
    (axes[0], 'V-JEPA2', r2_per_dim_vjepa, corr_vjepa),
    (axes[1], 'CLIP', r2_per_dim_clip, corr_clip)
]:
    max_emo_corr = np.max(np.abs(corr), axis=1)  # (100,) 각 PC의 최대 감정 상관
    ax.scatter(r2, max_emo_corr, alpha=0.6)
    for i in range(5):  # 상위 5개 PC만 label
        ax.annotate(f'PC{i+1}', (r2[i], max_emo_corr[i]))
    ax.set_xlabel('R² (brain → PC)')
    ax.set_ylabel('Max |Spearman r| with any emotion')
    ax.set_title(name)

plt.tight_layout()
plt.savefig('figures/pc_r2_vs_emotion_scatter.png', dpi=300, bbox_inches='tight')
```

### Step 5: 결과 저장

```python
np.savez('results/pc_emotion_correlation.npz',
         corr_vjepa=corr_vjepa,      # (100, 34)
         pval_vjepa=pval_vjepa,
         corr_clip=corr_clip,
         pval_clip=pval_clip,
         emotion_names=emotion_label_list,
         r2_vjepa=r2_per_dim_vjepa,
         r2_clip=r2_per_dim_clip)
```

또한 결과를 텍스트로 출력:

```python
print("=== V-JEPA2: Brain-predictable PCs ===")
for i in range(10):
    if r2_per_dim_vjepa[i] > 0.01:
        top3_emo = np.argsort(np.abs(corr_vjepa[i]))[-3:][::-1]
        print(f"  PC{i+1} (R²={r2_per_dim_vjepa[i]:.4f}): "
              f"top emotions = {[(emotion_label_list[j], f'{corr_vjepa[i,j]:.3f}') for j in top3_emo]}")

print("\n=== CLIP: Brain-predictable PCs ===")
for i in range(10):
    if r2_per_dim_clip[i] > 0.01:
        top3_emo = np.argsort(np.abs(corr_clip[i]))[-3:][::-1]
        print(f"  PC{i+1} (R²={r2_per_dim_clip[i]:.4f}): "
              f"top emotions = {[(emotion_label_list[j], f'{corr_clip[i,j]:.3f}') for j in top3_emo]}")
```

---

## 결과 해석 가이드

### 시나리오 A (best case)
Brain-predictable PC들 (R² > 0.01)이 감정 score와 높은 상관 (|r| > 0.3)을 보이고, brain-unpredictable PC들은 낮은 상관을 보임.
→ **"Brain selectively reads the affective subspace of video models"**

### 시나리오 B (mixed)
Brain-predictable PC 중 일부만 감정과 correlate, 나머지는 아닌 경우.
→ **"Brain-model alignment captures both affective and perceptual dimensions"** — 여전히 쓸 수 있지만 claim이 약해짐

### 시나리오 C (negative)
Brain-predictable PC들이 감정과 별로 correlate하지 않음.
→ **"Brain-model alignment is driven by perceptual, not affective, structure"** — claim을 수정해야 함

---

## 주의사항

1. **감정 이름 매핑 확인**: score_0이 어떤 감정인지 metadata CSV의 컬럼 순서를 반드시 확인할 것. Horikawa 논문의 34개 카테고리 순서와 동일한지 체크.
2. **arousal/valence/dominance도 함께 확인**: metadata에 이 3개 차원도 있을 것. PC와의 상관을 같이 보면 해석에 도움.
3. **multiple comparison**: 100 PC × 34 emotion = 3400개 test. FDR correction 적용 필요. 하지만 우리의 관심은 brain-predictable PC (3~5개)에 집중되므로, 이 PC들만 따로 보고해도 됨.
4. **explained variance ratio**: 각 PC가 전체 분산에서 차지하는 비율도 함께 기록 (`pca.explained_variance_ratio_`).
