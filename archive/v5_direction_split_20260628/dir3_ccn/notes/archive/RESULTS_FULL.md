# EmoFM Full Results Summary
**Last updated: 2026-03-31**
**Dataset: Horikawa et al. (2020) — 5 subjects, 2196 emotional video stimuli, 34 emotion categories**

---

## 0. 분석 개요

| 모델 | 타입 | Dim | 설명 |
|---|---|---|---|
| **Brain-JEPA** | Neural foundation model | 768 | fMRI(450 parcel) → subject-invariant embedding |
| **V-JEPA2** | Temporal video model | 1408 | facebook/vjepa2-vitg-fpc64-256 |
| **CLIP** | Static visual model | 512 | openai/clip-vit-base-patch32, mean-pool 8 frames |

**핵심 분석 파이프라인:**
1. 각 모델로 2196개 자극에 대한 embedding 추출
2. 2196×2196 cosine RSM(Representational Similarity Matrix) 구성
3. CKA(Centered Kernel Alignment)로 모델 간 geometry 비교
4. Permutation test (1,000회) + Bootstrap CI (1,000회)로 통계 검증

---

## 1. Subject-Invariant Encoding (Brain-JEPA 검증)

**분석**: V-JEPA2 → Brain-JEPA embedding 예측 MLP 학습 (SubjectBlock)
- 입력: V-JEPA2 embedding (1408-dim)
- 출력: Brain-JEPA embedding (768-dim)
- Train/test split: 80/20 (train=1756, test=440)

**5×5 Pearson r matrix (row=train subject, col=test subject):**

```
        sub-01  sub-02  sub-03  sub-04  sub-05
sub-01:  0.9882  0.9876  0.9872  0.9865  0.9864
sub-02:  0.9878  0.9875  0.9875  0.9865  0.9867
sub-03:  0.9876  0.9875  0.9872  0.9860  0.9861
sub-04:  0.9869  0.9867  0.9860  0.9861  0.9856
sub-05:  0.9869  0.9870  0.9864  0.9857  0.9862
```

**해석:**
- 대각(within-subject)과 비대각(cross-subject) 모두 r≈0.986
- 즉, subject A의 MLP로 subject B의 뇌를 예측해도 성능 동일
- Brain-JEPA가 이미 subject-invariant representation 공간에 있다는 강력한 증거
- → 5명 subject 평균 Brain-JEPA RSM을 공통 neural geometry로 사용하는 것이 정당화됨

---

## 2. Raw fMRI Cross-Subject RSA (450 parcels)

**분석**: 피질(Schaefer 400) + 피질하(Tian S3 50) = 450 parcel raw fMRI
- Per-subject cosine RSM (2196×2196) → 5×5 Spearman r cross-subject RSA matrix

**Raw fMRI (5×5 Spearman r):**
```
        sub-01  sub-02  sub-03  sub-04  sub-05
sub-01:  1.0000  0.0886  0.0776  0.0606  0.0612
sub-02:  0.0886  1.0000  0.1260  0.0852  0.0949
sub-03:  0.0776  0.1260  1.0000  0.0831  0.0876
sub-04:  0.0606  0.0852  0.0831  1.0000  0.0660
sub-05:  0.0612  0.0949  0.0876  0.0660  1.0000
off-diagonal mean: r = 0.083
```

**Brain-JEPA (5×5 Spearman r):**
```
        sub-01  sub-02  sub-03  sub-04  sub-05
sub-01:  1.0000  0.3320  0.3185  0.2853  0.3293
sub-02:  0.3320  1.0000  0.3809  0.3589  0.4122
sub-03:  0.3185  0.3809  1.0000  0.3270  0.3672
sub-04:  0.2853  0.3589  0.3270  1.0000  0.3603
sub-05:  0.3293  0.4122  0.3672  0.3603  1.0000
off-diagonal mean: r = 0.347
```

**해석:**
- Raw fMRI: cross-subject r=0.083 → subject마다 뇌 activation 패턴이 다름 (individual variability 큼)
- Brain-JEPA: cross-subject r=0.347 → **4.2배 높음** → subject-invariant space로 정렬됨
- Raw fMRI에서 subject 간 공유되는 emotion geometry가 약하다는 것 자체가
  Brain-JEPA의 subject-invariant 압축이 의미있음을 반증

---

## 3. Overall CKA: Brain-JEPA RSM vs. Model RSMs

**분석**: 2196×2196 RSM 간 CKA
- V-JEPA2/CLIP RSM을 Brain-JEPA RSM(5명 평균)과 비교
- Permutation test: 10,000회 (Mantel-style)
- Bootstrap CI: 10,000회 (95%)

| 모델 | CKA | p-value | 95% CI |
|---|---|---|---|
| **V-JEPA2** | **0.1282** | p<0.0001 | [0.1172, 0.1486] |
| **CLIP** | **0.1115** | p<0.0001 | [0.1071, 0.1284] |
| Δ (V-JEPA2 − CLIP) | **+0.0167** | p=0.0168 | [0.0012, 0.0295] |

**해석:**
- V-JEPA2와 CLIP 모두 Brain-JEPA neural geometry와 유의미하게 정렬 (both p<0.0001)
- V-JEPA2 > CLIP (Δ=+0.017, p=0.017): **temporal video model이 static model보다 neural emotion geometry를 더 잘 포착**
- V-JEPA2↔CLIP RSM 유사도: CKA=0.391 → 두 모델 자체는 상당히 유사한 표현 공간

---

## 4. Per-Emotion CKA (Emotion Score RSM)

**분석**: 각 감정 i에 대해 rank-1 kernel E_i[j,k] = score_i[j] × score_i[k]
- 연속 rater score (0~1) 사용, 2196개 자극 전체
- Permutation test: 1,000회, Bootstrap: 1,000회

**전체 34개 감정 결과:**

| # | Emotion | Brain | V-JEPA2 | CLIP | Δ(V-JEPA2−CLIP) |
|---|---|---|---|---|---|
| 0 | Admiration | 0.0115* | 0.0207* | 0.0207* | −0.0001 |
| 1 | Adoration | 0.0067* | 0.0396* | 0.1357* | −0.0961 |
| 2 | Aesthetic appreciation | 0.0139* | 0.1769* | 0.2196* | −0.0427 |
| 3 | Amusement | 0.0216* | 0.0871* | 0.1428* | −0.0558 |
| 4 | Anger | 0.0072* | 0.0177* | 0.0605* | −0.0427 |
| 5 | Anxiety | 0.0226* | 0.0590* | 0.1126* | −0.0536 |
| 6 | Awe | 0.0179* | 0.0276* | 0.0942* | −0.0666 |
| 7 | Awkwardness | 0.0112* | 0.0192* | 0.0491* | −0.0299 |
| 8 | Boredom | 0.0158* | 0.0431* | 0.0559* | −0.0128 |
| 9 | **Calmness** | 0.0162* | **0.1147*** | 0.0987* | **+0.0160** |
| 10 | Confusion | 0.0103* | 0.0083* | 0.0251* | −0.0169 |
| 11 | Contempt | 0.0056* | 0.0083* | 0.0225* | −0.0142 |
| 12 | Craving | 0.0058* | 0.0379* | 0.0877* | −0.0497 |
| 13 | Disgust | 0.0043* | 0.0094* | 0.0354* | −0.0260 |
| 14 | Empathic pain | 0.0200* | 0.0258* | 0.0571* | −0.0312 |
| 15 | Entrancement | 0.0176* | 0.0143* | 0.0323* | −0.0180 |
| 16 | Excitement | 0.0146* | 0.1085* | 0.1493* | −0.0408 |
| 17 | Fear | 0.0049* | 0.0062* | 0.0258* | −0.0196 |
| 18 | Horror | 0.0153* | 0.0532* | 0.0659* | −0.0127 |
| 19 | Interest | 0.0225* | 0.0587* | 0.1217* | −0.0630 |
| 20 | Joy | 0.0024* | 0.0065* | 0.0158* | −0.0093 |
| 21 | Nostalgia | 0.0181* | 0.0273* | 0.0703* | −0.0430 |
| 22 | **Relief** | **0.0447*** | 0.0316* | 0.0861* | −0.0546 |
| 23 | Romance | 0.0063* | 0.0452* | 0.0958* | −0.0506 |
| 24 | Sadness | 0.0144* | 0.0271* | 0.0828* | −0.0557 |
| 25 | Satisfaction | 0.0042* | 0.0105* | 0.0311* | −0.0206 |
| 26 | Sexual desire | 0.0164* | 0.0261* | 0.0592* | −0.0331 |
| 27 | Surprise | 0.0253* | 0.0410* | 0.1497* | −0.1087 |
| 28 | Sympathy | 0.0087* | 0.0162* | 0.0678* | −0.0516 |
| 29 | **Triumph** | 0.0225* | **0.0139*** | 0.0193* | −0.0054 |
| 30 | **Uncomfortable** | **0.0350*** | 0.0887* | **0.2228*** | −0.1342 |
| 31 | **Annoyance** | **0.0442*** | 0.0838* | 0.1134* | −0.0297 |
| 32 | Envy | 0.0120* | 0.0278* | 0.0551* | −0.0273 |
| 33 | Guilt | 0.0215* | 0.0519* | 0.0701* | −0.0182 |

(*p<0.05)

**요약 통계:**
- 유의한 감정 수: Brain 34/34, V-JEPA2 34/34, CLIP 34/34 (전부 유의)
- V-JEPA2 > CLIP: **1/34** (Calmness만)
- CLIP > V-JEPA2: **33/34**

**Brain CKA 상위 5개 감정:**
1. Relief (0.0447)
2. Annoyance (0.0442)
3. Uncomfortable (0.0350)
4. Surprise (0.0253)
5. Triumph / Anxiety (0.0225~0.0226)

**V-JEPA2에서 특히 높은 감정 (temporal dynamics 중요):**
- Aesthetic appreciation (0.177), Calmness (0.115), Excitement (0.109), Annoyance (0.084)

**CLIP이 압도적으로 높은 감정 (static visual feature로 충분):**
- Uncomfortable (CLIP=0.223 vs V-JEPA2=0.089, Δ=−0.134)
- Surprise (CLIP=0.150 vs V-JEPA2=0.041, Δ=−0.109)
- Adoration (CLIP=0.136 vs V-JEPA2=0.040, Δ=−0.096)

**해석:**
- Per-emotion 수준에서는 CLIP이 대부분의 감정에서 V-JEPA2를 앞섬
- 단, overall CKA에서는 V-JEPA2가 유의하게 높음 (Δ=+0.017, p=0.017)
- 이는 **V-JEPA2가 개별 감정 semantic보다 전반적인 neural geometry 구조를 더 잘 포착**함을 시사
- Calmness는 유일하게 V-JEPA2>CLIP → 시간적 흐름(slow dynamics, sustained scenes)이 중요한 감정

---

## 5. Affective Dimension CKA (Arousal / Valence / Dominance)

**분석**: 연속 rater score (1~9 scale, z-scored) → rank-1 kernel CKA
- Arousal, Valence, Dominance 각각 2196개 자극 전체 사용

| Dimension | Brain CKA | V-JEPA2 CKA | CLIP CKA | Winner |
|---|---|---|---|---|
| **Arousal** | 0.0208 [0.014, 0.031] | 0.0379 [0.030, 0.052] | 0.0388 [0.033, 0.051] | ≈ tie |
| **Valence** | 0.0242 [0.019, 0.032] | 0.0281 [0.022, 0.039] | **0.0995 [0.089, 0.114]** | **CLIP** |
| **Dominance** | 0.0049 [0.003, 0.010] | 0.0081 [0.007, 0.014] | **0.0233 [0.020, 0.033]** | **CLIP** |

(모든 결과 p<0.005)

**해석:**
- **Arousal**: V-JEPA2 ≈ CLIP (0.038 vs 0.039) → 각성 수준은 두 모델이 비슷하게 포착
- **Valence**: CLIP이 V-JEPA2 대비 **3.5배** 높음 (0.100 vs 0.028) → **쾌/불쾌는 static visual feature가 핵심**
- **Dominance**: CLIP이 V-JEPA2 대비 **2.9배** 높음 (0.023 vs 0.008) → 지배감도 static feature 우세
- Brain CKA는 모든 차원에서 낮음 (0.005~0.024) — 특히 Dominance(0.005)는 거의 표현 안 됨

---

## 6. 결과 통합 해석

### A. Overall geometry: V-JEPA2 > CLIP
- Brain-JEPA neural emotion geometry 전체 구조는 V-JEPA2와 더 잘 정렬 (Δ=+0.017, p=0.017)
- **Temporal video representation이 static image representation보다 뇌의 감정 표현 공간을 더 잘 설명**

### B. Per-emotion / dimension: CLIP > V-JEPA2
- 개별 감정 카테고리 및 valence/dominance 차원에서는 CLIP이 우세
- CLIP이 잡는 것: semantic category (Adoration, Surprise, Uncomfortable 등), valence, visual content
- V-JEPA2가 잡는 것: temporal dynamics, scene unfolding, slow/sustained emotional scenes (Calmness, Aesthetic appreciation)

### C. Dissociation (핵심 발견)
```
Overall neural geometry → V-JEPA2 wins (temporal structure matters for the whole space)
Per-emotion content     → CLIP wins (static semantic cues sufficient for most categories)
Exception: Calmness     → only emotion where V-JEPA2 > CLIP (requires temporal context)
```

### D. Raw fMRI vs Brain-JEPA
- Raw fMRI cross-subject r=0.083 → 개인 간 뇌 활동 패턴 차이 큼
- Brain-JEPA cross-subject r=0.347 → **4.2배 높은 subject consistency**
- Brain-JEPA가 개인 특이성을 제거하고 공유된 neural emotion geometry만 추출

### E. Affective dimensions
- Valence/Dominance는 static visual feature(CLIP)로 포착됨
- Arousal은 V-JEPA2 ≈ CLIP → dynamic/static 모두 비슷한 정보 보유
- Dominance는 Brain에서 거의 표현 안 됨 (Brain CKA=0.005)

---

## 7. 파일 목록

| 파일 | 내용 |
|---|---|
| `cka_results/cka_overall.npz` | Overall CKA (V-JEPA2, CLIP, V-JEPA2↔CLIP) |
| `cka_results/significance_overall.npz` | Permutation test + Bootstrap CI (10,000회) |
| `cka_results/emotion_rsm_results.npz` | Per-emotion CKA (34 emotions, 1,000 perm/boot) |
| `cka_results/affective_dim_results.npz` | Affective dim CKA (Arousal/Valence/Dominance, 10,000 perm/boot) |
| `cka_results/rsm_brain.npy` | Brain-JEPA RSM (2196×2196) |
| `cka_results/rsm_vjepa2.npy` | V-JEPA2 RSM (2196×2196) |
| `cka_results/rsm_clip.npy` | CLIP RSM (2196×2196) |
| `raw_fmri_results/fmri_raw.npy` | Raw fMRI (5, 2196, 450) |
| `raw_fmri_results/raw_fmri_rsa_results.npz` | Cross-subject RSA 결과 |
| `brain_embeddings/brain_jepa_embeddings.npy` | Brain-JEPA (5, 2196, 768) |
| `video_embeddings/vjepa2_embeddings.npy` | V-JEPA2 (2196, 1408) |
| `video_embeddings/clip_embeddings.npy` | CLIP (2196, 512) |
| `subject_blocks/predictions.npz` | SubjectBlock MLP 예측 + 5×5 r matrix |
