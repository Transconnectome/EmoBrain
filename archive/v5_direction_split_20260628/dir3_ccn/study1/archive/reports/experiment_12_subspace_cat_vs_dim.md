# Experiment 12: Brain-Predictable Subspace — Emotion Category vs Affective Dimension 설명력 비교

## 왜 필요한가

Exp 11에서 brain-predictable PC들이 감정과 correlate한다는 것을 확인했다. 그런데 두 가지 문제가 남아 있다:

1. **top emotion이 Aesthetic appreciation, Annoyance, Uncomfortable** — core emotion (Fear, Joy, Anger 등)이 아니라 해석이 약함
2. **A/V/D와의 상관을 개별 PC × 개별 dimension으로만 봄** — PC1 arousal=+0.14, PC2 arousal=+0.23이면 둘을 합치면 arousal 설명력이 높을 수 있는데, 이걸 안 봄

핵심 질문: **Brain-predictable subspace (3~6개 PC)가 설명하는 것은 고차원 감정 카테고리인가, 아니면 결국 A/V/D로 환원되는 저차원 affective dimension인가?**

이건 Horikawa et al. (2020)의 핵심 finding ("categories > dimensions")을 우리 프레임워크에서 재검증하는 것이기도 하다.

---

## 무엇을 해야 하는가

### 입력 데이터

```
# Exp 11에서 저장된 것
results/pc_emotion_correlation.npz
  → r2_vjepa (100,), r2_clip (100,)
  → brain_pred_mask_vjepa (100,), brain_pred_mask_clip (100,)

# PCA 결과 (Exp 11에서 이미 계산)
vjepa_pcs  (2196, 100)  — V-JEPA2 PCA
clip_pcs   (2196, 100)  — CLIP PCA

# Metadata
horikawa_meta_data_with_dimension_binary.csv
  → score_0 ~ score_33: 34개 감정 카테고리 (continuous 0~1)
  → arousal, valence, dominance: 3개 affective dimension
  → 14개 affective dimension 전부 있으면 전부 사용 (approach, arousal, attention, certainty, commitment, control, dominance, effort, fairness, identity, obstruction, safety, upswing, valence)
```

**주의**: metadata에 14개 affective dimension이 모두 있는지 확인할 것. 없으면 arousal, valence, dominance 3개만 사용.

---

### Analysis 1: Brain-predictable subspace → A/V/D 예측 (Multiple Regression)

개별 PC × 개별 dimension이 아니라, **brain-pred PC들을 합쳐서** A/V/D를 얼마나 설명하는지.

```python
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import numpy as np

# V-JEPA2
brain_pred_idx_vjepa = np.where(r2_vjepa > 0.01)[0]  # [0, 1, 2]
brain_unpred_idx_vjepa = np.where(r2_vjepa <= 0.01)[0]

X_pred_vjepa = vjepa_pcs[:, brain_pred_idx_vjepa]    # (2196, 3)
X_unpred_vjepa = vjepa_pcs[:, brain_unpred_idx_vjepa] # (2196, 97)
X_all_vjepa = vjepa_pcs[:, :100]                      # (2196, 100) baseline

pipe = Pipeline([('scaler', StandardScaler()), ('ridge', Ridge(alpha=1.0))])

# 각 target에 대해 5-fold CV R²
targets = {}
# A/V/D (또는 14개 affective dimensions 전부)
for dim_name in ['arousal', 'valence', 'dominance']:  # 14개 있으면 전부
    targets[dim_name] = meta[dim_name].values

# 34개 감정
for i in range(34):
    targets[emotion_labels[i]] = emotion_scores[:, i]

results_pred = {}
results_unpred = {}
results_all = {}

for name, y in targets.items():
    r2_pred = cross_val_score(pipe, X_pred_vjepa, y, cv=5, scoring='r2').mean()
    r2_unpred = cross_val_score(pipe, X_unpred_vjepa, y, cv=5, scoring='r2').mean()
    r2_all = cross_val_score(pipe, X_all_vjepa, y, cv=5, scoring='r2').mean()
    results_pred[name] = max(r2_pred, 0)
    results_unpred[name] = max(r2_unpred, 0)
    results_all[name] = max(r2_all, 0)

# CLIP도 동일하게
```

---

### Analysis 2: Category vs Dimension 설명력 직접 비교

Brain-pred subspace가 감정 카테고리 vs affective dimension 중 어느 쪽을 더 잘 설명하는지.

```python
# V-JEPA2 brain-pred subspace (3 PCs)로:
mean_r2_categories = np.mean([results_pred[e] for e in emotion_labels])     # 34개 평균
mean_r2_dimensions = np.mean([results_pred[d] for d in dimension_labels])   # A/V/D (또는 14개) 평균

# 개별 감정/차원 R² 전부 기록
```

---

### Analysis 3: 비교 baseline — Unpredictable subspace & Full subspace

Brain-pred만 쓸 때 vs 전체 100 PC 쓸 때 vs unpred만 쓸 때를 비교하면, brain-pred subspace의 "효율성"을 보여줄 수 있다.

```python
# 3개 PC만으로 arousal R² = X vs 100개 PC로 arousal R² = Y
# → 3개 PC가 전체의 몇 %를 설명하는가?
efficiency = results_pred[name] / max(results_all[name], 1e-10)
```

---

### Analysis 4: Emotion별 상세 — Brain-pred subspace의 감정 coverage

34개 감정 각각에 대해 brain-pred subspace의 R²를 보고, 어떤 감정이 잘 설명되고 어떤 감정이 안 되는지 확인.

```python
# 정렬: R²가 높은 감정 → 낮은 감정
sorted_emotions = sorted(results_pred.items(), key=lambda x: x[1], reverse=True)

# Top 10, Bottom 10 출력
```

이게 중요한 이유: Exp 11에서 top emotion이 Aesthetic appreciation, Annoyance 등이었는데, multiple regression에서는 다른 감정도 잘 설명될 수 있음 (여러 PC의 조합으로).

---

### 시각화

#### Figure A: Brain-pred subspace R² — 감정 34개 + A/V/D (또는 14 dim) 한 figure에

```python
import matplotlib.pyplot as plt
import numpy as np

# 모든 target을 하나의 bar chart로
# x축: 34개 감정 (파란색) + A/V/D (빨간색)
# y축: R² from brain-pred subspace
# 감정은 R² 내림차순 정렬, dimension은 별도 그룹으로

fig, ax = plt.subplots(figsize=(18, 5))

# 감정 정렬
emo_r2 = [(e, results_pred[e]) for e in emotion_labels]
emo_r2_sorted = sorted(emo_r2, key=lambda x: x[1], reverse=True)

dim_r2 = [(d, results_pred[d]) for d in dimension_labels]

names = [e[0] for e in emo_r2_sorted] + [''] + [d[0] for d in dim_r2]
values = [e[1] for e in emo_r2_sorted] + [0] + [d[1] for d in dim_r2]
colors = ['steelblue'] * 34 + ['white'] + ['tomato'] * len(dimension_labels)

ax.bar(range(len(names)), values, color=colors)
ax.set_xticks(range(len(names)))
ax.set_xticklabels(names, rotation=90, fontsize=8)
ax.set_ylabel('R² (brain-pred subspace → target, 5-fold CV)')
ax.set_title('V-JEPA2: Brain-predictable subspace (3 PCs) prediction of emotions vs dimensions')
ax.axhline(y=np.mean([e[1] for e in emo_r2_sorted]), color='steelblue', linestyle='--', alpha=0.5, label=f'mean cat R²')
ax.axhline(y=np.mean([d[1] for d in dim_r2]), color='tomato', linestyle='--', alpha=0.5, label=f'mean dim R²')
ax.legend()

plt.tight_layout()
plt.savefig('figures/brain_pred_subspace_r2_all.png', dpi=300, bbox_inches='tight')
```

#### Figure B: Pred vs Unpred vs All — 감정/차원별 비교

```python
fig, axes = plt.subplots(1, 2, figsize=(16, 5))

for ax, model_name in [(axes[0], 'V-JEPA2'), (axes[1], 'CLIP')]:
    # 적절한 results 사용
    # scatter: x = R²(all 100 PCs), y = R²(brain-pred only)
    # 감정은 파란 점, dimension은 빨간 점
    # diagonal line = identity
    pass
```

#### Figure C: Efficiency plot — Brain-pred R² / All R² (몇 %를 3~6개 PC만으로 설명하는가)

```python
# bar chart: 각 감정/차원에 대해 efficiency = R²_pred / R²_all
# 높으면 brain-pred subspace만으로 거의 다 설명
# 낮으면 brain이 안 읽는 차원에 추가 정보 있음
```

---

### 결과 저장

```python
np.savez('results/brain_pred_subspace_prediction.npz',
         # V-JEPA2
         r2_pred_vjepa=r2_pred_vjepa_dict,       # dict: target_name → R²
         r2_unpred_vjepa=r2_unpred_vjepa_dict,
         r2_all_vjepa=r2_all_vjepa_dict,
         # CLIP
         r2_pred_clip=r2_pred_clip_dict,
         r2_unpred_clip=r2_unpred_clip_dict,
         r2_all_clip=r2_all_clip_dict,
         # labels
         emotion_labels=emotion_labels,
         dimension_labels=dimension_labels)
```

### 텍스트 출력

```python
print("=== V-JEPA2 Brain-pred subspace (3 PCs) ===")
print(f"Mean R² for 34 emotions: {mean_r2_categories:.4f}")
print(f"Mean R² for dimensions:  {mean_r2_dimensions:.4f}")
print(f"Ratio (cat/dim): {mean_r2_categories/max(mean_r2_dimensions, 1e-10):.2f}")
print()
print("Top 10 emotions by R²:")
for name, r2 in sorted_emotions[:10]:
    print(f"  {name}: R²={r2:.4f} (efficiency={r2/max(results_all[name],1e-10):.1%})")
print()
print("Dimensions:")
for name in dimension_labels:
    print(f"  {name}: R²={results_pred[name]:.4f} (efficiency={results_pred[name]/max(results_all[name],1e-10):.1%})")

# CLIP도 동일
```

---

## 결과 해석 가이드

### 시나리오 A (best case for CCN)
- Brain-pred subspace의 mean R²(categories) > mean R²(dimensions)
- → "Brain reads category-level affective structure, not just valence/arousal"
- → Horikawa (2020) "categories > dimensions" 를 computational model 레벨에서 재확인

### 시나리오 B
- Brain-pred subspace가 A/V/D도 categories도 비슷하게 설명
- → "Brain-predictable subspace captures general affective information"
- → 여전히 valid하지만, category vs dimension 구분은 못 함

### 시나리오 C
- Brain-pred subspace의 mean R²(dimensions) > mean R²(categories)
- → "Brain-model alignment is driven by broad affective dimensions"
- → claim을 dimension 쪽으로 수정

### 어떤 시나리오든 paper에 쓸 수 있다
핵심은 "brain-pred subspace가 affective"라는 것은 Exp 11에서 이미 확정. 이 실험은 **그 affective information이 categorical인가 dimensional인가**를 추가로 밝히는 것.
