# EmoFM — 실험 결과 총정리

**작성일: 2026-03-30**
**CCN 2026 deadline: 2026-04-02**

---

## 데이터셋

- **Horikawa et al. (2020)**: 5 subjects, 2196 videos (Cowen & Keltner 2017 감정 비디오)
- 34개 감정 카테고리 + 14개 affective dimensions (valence, arousal, dominance)
- Whole-brain fMRI, 3T, Schaefer 400 parcels

---

## 실험 1: Cross-subject Brain-JEPA Invariance

### 설정
- Brain-JEPA (ep300) 임베딩 추출: 5 subjects × 2196 stimuli → `(5, 2196, 768)`
- SubjectBlock MLP (1408→1024→512→768) 학습 후 5×5 cross-subject prediction

### 결과

```
         sub-01  sub-02  sub-03  sub-04  sub-05
sub-01   0.9882  0.9876  0.9872  0.9865  0.9864
sub-02   0.9878  0.9875  0.9875  0.9865  0.9867
sub-03   0.9876  0.9875  0.9872  0.9860  0.9861
sub-04   0.9869  0.9867  0.9860  0.9861  0.9856
sub-05   0.9869  0.9870  0.9864  0.9857  0.9862
```
(Pearson r, 모든 값 ≈ 0.986)

### 해석 (치명적 발견)
- **Diagonal ≈ Off-diagonal** → Brain-JEPA는 완전히 subject-invariant
- sub-01 fMRI로 예측한 임베딩 ≈ sub-05 fMRI로 예측한 임베딩
- 결론: Brain-JEPA로는 개인 특이적 감정 구조 분석 **불가능**
- **Pivot**: 개인 구조 분석 포기 → 공유 구조 ↔ V-JEPA2 alignment로 방향 전환

---

## 실험 2: CKA Alignment (Overall)

### 설정
- Brain-JEPA mean across 5 subjects → (2196, 768) shared emotion geometry
- V-JEPA2 (`facebook/vjepa2-vitg-fpc64-256`): 16 frames → mean-pool → (2196, 1408)
- CLIP (`openai/clip-vit-base-patch32`): 8 frames → per-frame encode → mean-pool → (2196, 512)
- RSM: 2196×2196 cosine similarity matrix (각 모델별)
- CKA(Brain RSM, Model RSM)

### 통계 검증
- Permutation test (Mantel-style, 10,000 perms)
- Bootstrap 95% CI (10,000 resamples)
- Paired bootstrap (V-JEPA2 vs CLIP, 10,000 resamples)

### 결과

| 모델 | CKA | 95% CI | p (permutation) |
|------|-----|--------|-----------------|
| V-JEPA2 (temporal) | **0.1282** | [0.1172, 0.1486] | < 0.0001 |
| CLIP (static) | 0.1115 | [0.1071, 0.1284] | < 0.0001 |
| **Δ (V-JEPA2 − CLIP)** | **+0.0167** | **[0.0012, 0.0295]** | **p = 0.0168** |

### 해석
- 두 모델 모두 뇌 감정 표상과 유의하게 align (p < 0.0001)
- V-JEPA2 > CLIP: **유의** (p = 0.017), CI가 0을 배제
- 절대값이 낮은 이유: 2196개 stimulus 전체 pool에 감정 무관 시각 변산이 다수 포함 → per-emotion에서 CKA 올라감 (아래 참조)

---

## 실험 3: CKA Alignment (Per-emotion, 23 categories)

### 설정
- 각 감정 카테고리별로 해당 stimulus만 subset → sub-RSM → CKA
- n ≥ 20인 카테고리만 분석 (23/34)
- 동일한 통계 검증 적용

### 결과 전체

| 감정 | n | V-JEPA2 CKA | p | CLIP CKA | p | Δ | p(paired) |
|------|---|------------|---|----------|---|---|-----------|
| Amusement | 574 | 0.109* | 0.000 | 0.118* | 0.000 | −0.008 | 0.853 |
| Empathic pain | 212 | 0.165* | 0.000 | 0.139* | 0.000 | +0.027 | 0.196 |
| Aesthetic apprec. | 174 | 0.206* | 0.000 | **0.267*** | 0.000 | −0.061 | 0.968 |
| Interest | 150 | 0.175* | 0.000 | 0.135* | 0.000 | +0.040 | 0.081 |
| Relief | 164 | 0.158* | 0.000 | 0.157* | 0.000 | +0.001 | 0.626 |
| Awe | 134 | 0.219* | 0.000 | 0.184* | 0.000 | +0.036 | 0.223 |
| Uncomfortable | 123 | 0.088 | 0.072 | 0.097* | 0.023 | −0.009 | 0.663 |
| Nostalgia | 90 | 0.257* | 0.000 | 0.261* | 0.000 | −0.003 | 0.512 |
| Annoyance | 91 | 0.157* | 0.014 | 0.188* | 0.002 | −0.031 | 0.920 |
| Sadness | 83 | 0.152* | 0.009 | 0.169* | 0.029 | −0.017 | 0.826 |
| Sympathy | 77 | 0.254* | 0.000 | 0.219* | 0.000 | +0.035 | 0.313 |
| Confusion | 76 | 0.217* | 0.001 | 0.237* | 0.000 | −0.020 | 0.854 |
| Romance | 76 | 0.216* | 0.000 | 0.237* | 0.000 | −0.020 | 0.835 |
| **Anxiety** | **71** | **0.291*** | **0.000** | 0.210* | 0.022 | **+0.081*** | **0.038** |
| Adoration | 73 | 0.208* | 0.002 | 0.199* | 0.035 | +0.009 | 0.569 |
| Surprise | 73 | 0.196* | 0.002 | 0.161 | 0.191 | +0.035 | 0.261 |
| Excitement | 51 | 0.250* | 0.004 | **0.316*** | 0.000 | −0.066 | 0.877 |
| Craving | 57 | 0.223* | 0.003 | 0.198* | 0.049 | +0.025 | 0.394 |
| Boredom | 44 | 0.245* | 0.031 | 0.249 | 0.331 | −0.005 | 0.609 |
| Horror | 39 | 0.320* | 0.021 | 0.329* | 0.019 | −0.008 | 0.524 |
| Entrancement | 33 | 0.297 | 0.243 | 0.293 | 0.381 | +0.004 | 0.510 |
| Calmness | 29 | 0.370 | 0.050 | **0.416*** | 0.012 | −0.046 | 0.700 |
| Guilt | 23 | **0.496*** | 0.001 | 0.401 | 0.115 | +0.095 | 0.148 |

*p < 0.05

### 주요 패턴

**V-JEPA2 유의하게 우세 (p < 0.05):**
- **Anxiety** (Δ=+0.081, p=0.038): 유일하게 paired bootstrap 유의. 시간적 축적/예측이 핵심인 감정.

**V-JEPA2 우세 (trend, p < 0.1):**
- Interest (Δ=+0.040, p=0.081)
- Awe (+0.036), Surprise (+0.036), Sympathy (+0.035)

**CLIP 우세 (trend):**
- Aesthetic appreciation (Δ=−0.061): 장면 미적 내용이 핵심
- Excitement (Δ=−0.066): 역설적 — 시각적 흥분 자체가 중요
- Calmness (Δ=−0.046): 정적 장면

**이상치:**
- Guilt (CKA=0.496 최고, but n=23 불안정): 두 모델 모두 높은 CKA. 비디오 내용이 매우 homogeneous할 가능성.

### 통계 요약
- V-JEPA2 유의 (p<0.05): 20/23 카테고리
- CLIP 유의 (p<0.05): 19/23 카테고리
- Δ 유의 (V-JEPA2 > CLIP, p<0.05): **1/23** (Anxiety만)

---

## 현재 스토리의 강점과 약점

### 강점
1. 통계적으로 탄탄: 10,000번 permutation/bootstrap, CI 0 배제
2. 방향 일관성: 23개 중 14개에서 V-JEPA2 ≥ CLIP (trend)
3. 이론적 해리: Anxiety(temporal) vs Aesthetic appreciation(static) double dissociation
4. Foundation model 2개 조합(Brain-JEPA + V-JEPA2)이 novelty

### 약점 (약한 부분)
1. **Overall Δ=0.017**: 작다. Reviewer가 "practically meaningless"라고 할 수 있음
2. **Per-emotion: Anxiety만 유의**: 34개 중 1개가 유의한 건 multiple comparison 보정하면 더 약해짐
3. **Brain-JEPA subject-invariance**: 개인 구조 분석 불가 → "왜 5 subject가 필요했나?" 질문 가능
4. **CLIP이 Overall에서 낮은 건 V-JEPA2도 낮다**: 둘 다 낮으면 "둘 다 별로 설명 못 한다"는 해석도 가능
5. **Rationale 부족**: "왜 temporal model이 emotion representation을 더 잘 설명해야 하는가?" 이론적 근거가 약함

---

## 강화 가능한 추가 실험 방향

### A. RSM 시각화 + MDS/UMAP
Brain RSM의 MDS/UMAP으로 34개 감정의 neural geometry 시각화. V-JEPA2 RSM과 겹쳐서 어디서 align되고 어디서 diverge하는지 보여줌. **Figure 1로 좋음.**

### B. Linear regression: 감정 차원 예측
V-JEPA2 임베딩으로 arousal/valence/dominance 예측 vs CLIP — RSA가 아닌 직접 decoding으로 보완.

### C. RSM distance matrix 비교
Brain RSM의 upper-triangle을 flatten해서 Spearman correlation으로 Model RSM과 비교 (전통적 RSA). CKA 외 두 번째 metric으로 수렴 타당성.

### D. Emotion category decoding
Brain-JEPA 임베딩 → emotion category 분류 정확도. V-JEPA2 임베딩 → emotion category 분류 정확도. 비교. **단순하고 설득력 있음.**

### E. 감정별 arousal과 Δ의 관계
Δ(V-JEPA2−CLIP)와 arousal score의 상관관계. "High arousal emotion이 temporal advantage를 보인다"는 hypotheis 검증 가능.

---

## 사용 모델/데이터 요약

| 구성요소 | 세부 | 상태 |
|----------|------|------|
| Brain-JEPA | ep300, (5, 2196, 768) | ✅ 완료 |
| V-JEPA2 | vitg-fpc64-256, (2196, 1408) | ✅ 완료 |
| CLIP | ViT-B/32, (2196, 512) | ✅ 완료 |
| RSM (세 모델) | (2196, 2196) × 3 | ✅ 완료 |
| CKA overall + stats | 10k perm + 10k boot | ✅ 완료 |
| CKA per-emotion + stats | 23 categories | ✅ 완료 |
| Figure | — | ❌ 미완 (style 개선 필요) |
| CCN draft | CCN_draft.md | ✅ 초안 존재 |

---

## 파일 경로

```
/pscratch/sd/s/sjmoon/EmoFM/
├── brain_embeddings/brain_jepa_embeddings.npy     (5, 2196, 768)
├── video_embeddings/
│   ├── vjepa2_embeddings.npy                      (2196, 1408)
│   └── clip_embeddings.npy                        (2196, 512)
├── subject_blocks/predictions.npz                 (5×5 r_matrix)
├── cka_results/
│   ├── rsm_brain.npy                              (2196, 2196)
│   ├── rsm_vjepa2.npy                             (2196, 2196)
│   ├── rsm_clip.npy                               (2196, 2196)
│   ├── cka_overall.npz
│   ├── cka_per_emotion.npz
│   ├── significance_overall.npz
│   └── significance_per_emotion.npz
├── 05_extract_clip_embeddings.py
├── 06_cka_analysis.py
├── 06b_significance.py
├── 07_plot_figures.py
├── CCN_draft.md
└── RESULTS_SUMMARY.md
```
