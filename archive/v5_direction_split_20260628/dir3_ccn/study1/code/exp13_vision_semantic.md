# # Experiment: Controlling Low-Level Features (Partial RSA & Partial $R^2$)

# ## 1. 분석의 목적과 구조

# 리뷰어의 핵심 공격 루트인 "모델이 포착한 것은 감정이 아니라 단순한 시각적 속성(low-level visual feature)이나 의미적 속성(semantic feature)일 뿐이다"라는 주장을 두 가지 층위에서 방어합니다.

# * **실험 A (Global Level): Partial RSA**
#   * 전체 비디오 표상 공간(RSM)에서 vision feature와 semantic feature의 기여도를 수학적으로 제거(regress out)합니다.
#   * **목적:** 전역적인 latent space 차원에서도 뇌와 모델 간의 순수한 감정적 정렬(affective alignment)이 존재하는지 확인합니다.

# * **실험 B (Local Level): Partial $R^2$ of Brain-Predictable Subspace**
#   * Exp 12에서 발굴한 brain-predictable PC(예: V-JEPA2 PC1~3)와 감정 점수(Emotion scores) 양쪽 모두에서 vision feature와 semantic feature의 효과를 제거합니다.
#   * 남은 잔차(Residuals)들끼리 5-fold CV Ridge regression을 돌려 Partial $R^2$를 계산합니다.
#   * **목적:** "뇌가 선택한 3~6개의 PC는 시각/의미 정보를 완전히 통제한 후에도 독립적으로 감정 카테고리를 설명하는 진짜 감정 축이다"라는 논문의 핵심 주장을 직접적으로 증명합니다.

# ## 2. Python Script (`experiment_confound_control.py`)

# ```python
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# ==========================================
# Data Loading
# ==========================================
# 1. Confound Features
vision_df = pd.read_csv('vision_features 1 (1).csv')
semantic_df = pd.read_csv('semantic_features 1 (1).csv')
vision_features = vision_df.iloc[:, 1:].values
semantic_features = semantic_df.iloc[:, 1:].values
X_confounds = np.column_stack((vision_features, semantic_features))

# 2. RSMs for Experiment A
rsm_brain = np.load('cka_results/rsm_brain.npy')
rsm_vjepa = np.load('cka_results/rsm_vjepa2.npy')

n_videos = rsm_brain.shape[0]
tri_idx = np.triu_indices(n_videos, k=1)
brain_vec = rsm_brain[tri_idx]
vjepa_vec = rsm_vjepa[tri_idx]

rsm_vision = cosine_similarity(vision_features)
rsm_semantic = cosine_similarity(semantic_features)
vision_vec = rsm_vision[tri_idx]
semantic_vec = rsm_semantic[tri_idx]
X_confounds_rsm = np.column_stack((vision_vec, semantic_vec))

# 3. Data for Experiment B
# Exp 11, 12에서 사용한 데이터 경로에 맞게 수정 필요
vjepa_pcs = np.load('vjepa2_pcs.npy')
r2_vjepa = np.load('results/pc_emotion_correlation.npz')['r2_vjepa']
brain_pred_pcs = vjepa_pcs[:, r2_vjepa > 0.01] # (2196, 3)

meta = pd.read_csv('metadata/horikawa_meta_data_with_dimension_binary.csv')
emotion_names = [col for col in meta.columns if col.startswith('score_')]
emotion_scores = meta[emotion_names].values # (2196, 34)

# ==========================================
# Experiment A: Partial RSA (Global Level)
# ==========================================
reg_brain = LinearRegression().fit(X_confounds_rsm, brain_vec)
brain_resid = brain_vec - reg_brain.predict(X_confounds_rsm)

reg_vjepa = LinearRegression().fit(X_confounds_rsm, vjepa_vec)
vjepa_resid = vjepa_vec - reg_vjepa.predict(X_confounds_rsm)

partial_rsa, p_val_rsa = spearmanr(brain_resid, vjepa_resid)
original_rsa, _ = spearmanr(brain_vec, vjepa_vec)

print("=== Experiment A: Partial RSA ===")
print(f"Original RSA: {original_rsa:.4f}")
print(f"Partial RSA (Vision/Semantic 통제): {partial_rsa:.4f} (p={p_val_rsa})")
print("\n")

# ==========================================
# Experiment B: Partial R^2 (Subspace Level)
# ==========================================
# 1. 감정 점수에서 Vision/Semantic 기여도 제거
reg_emotion = LinearRegression().fit(X_confounds, emotion_scores)
emotion_resid = emotion_scores - reg_emotion.predict(X_confounds)

# 2. Brain-predictable PCs에서 Vision/Semantic 기여도 제거
reg_pcs = LinearRegression().fit(X_confounds, brain_pred_pcs)
pcs_resid = brain_pred_pcs - reg_pcs.predict(X_confounds)

# 3. 잔차 간의 예측력 평가 (Ridge + 5-fold CV)
pipe = Pipeline([('scaler', StandardScaler()), ('ridge', Ridge(alpha=1.0))])

print("=== Experiment B: Partial R^2 for Brain-Predictable Subspace ===")
partial_r2_list = []
original_r2_list = []

for i, emo_name in enumerate(emotion_names):
    # Original R^2 (통제 전)
    orig_r2 = cross_val_score(pipe, brain_pred_pcs, emotion_scores[:, i], cv=5, scoring='r2').mean()
    original_r2_list.append(max(orig_r2, 0))
    
    # Partial R^2 (통제 후)
    part_r2 = cross_val_score(pipe, pcs_resid, emotion_resid[:, i], cv=5, scoring='r2').mean()
    partial_r2_list.append(max(part_r2, 0))

# 상위 5개 감정 결과 출력 예시 (기존 Exp 12 결과 바탕)
top_idx = np.argsort(original_r2_list)[-5:][::-1]
for idx in top_idx:
    print(f"{emotion_names[idx]}:")
    print(f"  Original R^2: {original_r2_list[idx]:.4f}")
    print(f"  Partial R^2 : {partial_r2_list[idx]:.4f}")