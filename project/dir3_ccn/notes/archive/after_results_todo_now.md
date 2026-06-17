# 지금 해야 할 것
## 현재 상황 및 즉시 실행 분석 목록
**Date: 2026-03-31**

---

## 현재 상황 요약

### 확보된 결과

| 분석 | 결과 | 신뢰도 |
|------|------|--------|
| Brain-JEPA subject-invariance | off-diagonal r=0.347 vs raw fMRI r=0.083 | 높음 |
| Overall CKA (Brain-JEPA RSM 기반) | V-JEPA2=0.058, CLIP=0.054, V-JEPA2>CLIP 4/5 subjects | 보통 |
| Procrustes (k=27) | V-JEPA2 disparity 낮음, 25/34 감정에서 우세 | 보통 |
| Cross-space RSA (Brain-JEPA RSM 기반) | Brain RSA mean=-0.009, 거의 0 | 낮음 |
| k sweep | R²_brain max=0.06, k=27 특별한 elbow 없음 | 낮음 |

### 핵심 문제

**Brain-JEPA RSM이 감정 구조를 거의 담고 있지 않다.**

Brain-JEPA RSM의 std=0.009로 거의 균일하다. 즉 2196개 비디오가 Brain-JEPA 공간에서 모두 거의 같은 거리에 있다. 이 때문에 Cross-space RSA에서 Brain RSA mean이 -0.009로 사실상 0이 나왔다.

이것이 모델의 문제인지 (Brain-JEPA가 감정 정보를 압축해버림) 분석 방법의 문제인지 (cosine RSM이 적절하지 않음) 를 구분해야 한다.

### 가장 유력한 원인

Brain-JEPA는 fMRI 전반을 예측하도록 학습됐다. 감정은 fMRI 전체 분산에서 작은 부분만 차지할 수 있다. 결과적으로 Brain-JEPA embedding이 감정보다 visual/semantic 공통 구조를 더 강하게 인코딩했을 가능성이 높다.

---

## 즉시 해야 할 분석

### 우선순위 1: Raw fMRI RSM으로 Cross-space RSA 재실행

**왜 필요한가**

Brain-JEPA RSM이 감정 구조를 반영하지 못하는 것이 Brain-JEPA의 문제일 가능성이 높다. Raw fMRI는 직접적인 신경 신호이기 때문에 감정 구조를 더 잘 담고 있을 가능성이 높다. 이를 확인해야 Cross-space RSA 결과를 신뢰할 수 있다.

**입력**

```
raw_fmri_results/fmri_raw.npy  →  shape: (5, 2196, 450)
rsm_vjepa2.npy                 →  shape: (2196, 2196)
rsm_clip.npy                   →  shape: (2196, 2196)
metadata (score_0 ~ score_33)  →  shape: (2196,) × 34
```

**해야 할 것**

1. 5명 피험자 각각의 raw fMRI로 RSM 계산: cosine similarity → (2196, 2196) × 5개
2. 5명 평균 RSM 계산: (2196, 2196)
3. 각 감정 i에 대해 emotion kernel 계산: E_i[j,k] = score_i[j] × score_i[k]
4. Spearman r 계산:
   - rsa_rawfmri_i = spearman(raw_fmri_rsm_mean upper-tri, E_i upper-tri)
   - rsa_vjepa_i = spearman(rsm_vjepa2 upper-tri, E_i upper-tri)
   - rsa_clip_i = spearman(rsm_clip upper-tri, E_i upper-tri)
5. divergence_i = |rsa_rawfmri_i - rsa_vjepa_i|
6. 34개 감정 전체에 대해 결과 테이블 출력

**기대 결과**

Raw fMRI RSA mean이 Brain-JEPA (-0.009)보다 의미있게 높으면 → Brain-JEPA가 감정 정보를 압축했다는 증거. 이 경우 이후 분석은 raw fMRI RSM 기반으로 전환.

Raw fMRI RSA도 낮으면 → 감정 kernel 방식 자체의 문제이거나, 뇌의 감정 표상이 이 방식으로는 포착되지 않는 것.

---

### 우선순위 2: Raw fMRI RSM 기반 Overall CKA 계산

**왜 필요한가**

현재 Overall CKA는 Brain-JEPA RSM 기반이다. Raw fMRI RSM으로 다시 계산하면 더 직접적인 neural signal과 video model의 alignment를 측정할 수 있다.

**입력**

```
raw fMRI RSM (우선순위 1에서 계산)  →  (2196, 2196)
rsm_vjepa2.npy                      →  (2196, 2196)
rsm_clip.npy                        →  (2196, 2196)
```

**해야 할 것**

1. CKA(raw_fmri_rsm_mean, rsm_vjepa2) 계산
2. CKA(raw_fmri_rsm_mean, rsm_clip) 계산
3. Subject별로도 계산: CKA(raw_fmri_rsm_s, rsm_vjepa2) for s in 1..5
4. Permutation test (1,000회) + Bootstrap CI (1,000회) for significance
5. Brain-JEPA RSM 기반 CKA 결과와 나란히 비교

**기대 결과**

Raw fMRI 기반 CKA가 Brain-JEPA 기반 CKA보다 높거나 낮을 수 있다. 중요한 건 방향성 (V-JEPA2 > CLIP 여부)이 일관되는지 확인하는 것.

---

### 우선순위 3: Raw fMRI RSM 기반 k sweep 재실행

**왜 필요한가**

현재 k sweep에서 R²_brain이 max 0.06으로 매우 낮았다. 이는 Brain-JEPA embedding 자체가 감정 정보를 거의 담지 않기 때문일 가능성이 높다. Raw fMRI로 같은 분석을 하면 R²가 더 높게 나올 수 있고, k=27 근방에서 의미있는 패턴이 나올 수 있다.

**입력**

```
raw_fmri_results/fmri_raw.npy   →  (5, 2196, 450)
vjepa2_embeddings.npy           →  (2196, 1408)
clip_embeddings.npy             →  (2196, 512)
metadata (score_0 ~ score_33)   →  (2196,) × 34
```

**해야 할 것**

1. raw fMRI subject-averaged: (2196, 450)
2. k_values = [3, 5, 7, 10, 15, 20, 25, 27, 30, 34, 40, 50, 75, 100]
3. 각 k에서:
   - PCA(k)로 raw fMRI (2196, k), V-JEPA2 (2196, k), CLIP (2196, k) 축소
   - Procrustes disparity: raw fMRI vs V-JEPA2, raw fMRI vs CLIP
   - Emotion decoding R²: Ridge regression + 5-fold CV, 34개 감정 평균
     - raw fMRI k차원으로 감정 예측
     - V-JEPA2 k차원으로 감정 예측
     - CLIP k차원으로 감정 예측
4. k=27에서 elbow 또는 plateau 여부 확인
5. Brain-JEPA k sweep 결과와 나란히 비교 테이블 출력

**기대 결과**

R²_rawfmri가 R²_brain (0.06)보다 높으면 → raw fMRI가 감정 정보를 더 잘 담고 있음 확인.

k=27 근방에서 plateau가 나오면 → "27차원이 감정 표상의 최적 차원수" claim 가능.

---

### 우선순위 4: UMAP 시각화 업데이트

**왜 필요한가**

현재 UMAP은 Brain-JEPA RSM 기반이다. Raw fMRI RSM으로 다시 시각화하면 뇌의 감정 공간 구조가 더 명확하게 보일 수 있다.

**입력**

```
raw fMRI RSM (우선순위 1에서 계산)  →  (2196, 2196)
rsm_vjepa2.npy                      →  (2196, 2196)
rsm_clip.npy                        →  (2196, 2196)
metadata (score_0 ~ score_33)       →  (2196,) × 34
```

**해야 할 것**

1. raw fMRI RSM → distance matrix (1 - RSM) → UMAP 2D embedding
2. V-JEPA2 RSM → distance matrix → UMAP 2D embedding
3. 두 embedding을 같은 컬러 스키마로 시각화
   - 각 비디오를 가장 높은 감정 score로 색칠
   - 또는 상위 3개 감정의 혼합 색상
4. Procrustes overlay: raw fMRI와 V-JEPA2를 같은 2D 공간에 overlay
   - Brain Tuning target 시각화: divergence 높은 비디오를 강조

---

## 결과에 따른 분기

### 케이스 A: Raw fMRI RSA mean이 의미있게 양수 (>0.02)

Brain-JEPA가 감정 정보를 압축했다는 것이 확인됨. 이후 모든 분석은 raw fMRI RSM 기반으로 전환. CCN 스토리:

> Brain foundation models encode shared neural geometry but compress emotion-specific information. Using raw fMRI reveals a clearer alignment between neural and computational emotion spaces, with V-JEPA2 better capturing the shared affective structure than CLIP.

### 케이스 B: Raw fMRI RSA도 여전히 낮음 (<0.01)

Emotion kernel 방식 자체의 문제이거나, 뇌의 감정 표상이 pairwise similarity 방식으로 포착되지 않는 것. 이 경우:

- Emotion kernel 대신 다른 방식의 RSM 시도 (예: correlation distance 기반)
- 또는 CKA overall 결과만 살리는 방향으로 스토리 축소

### 케이스 C: k sweep에서 k=27 근방에서 plateau

"27차원이 감정 표상의 최적 차원수" claim 가능. 풀 페이퍼로 연결되는 강한 preliminary finding.

---

## 오늘 타임라인

```
지금 ~ 저녁:
    우선순위 1, 2 실행 (raw fMRI RSM 계산 + Cross-space RSA + CKA)
    결과 확인 후 케이스 분기 결정

저녁 ~ 밤:
    우선순위 3 실행 (k sweep)
    우선순위 4 실행 (UMAP)
    결과 보고 CCN 스토리 확정

내일 (4/1):
    Figure 완성
    CCN draft 작성

4/2:
    제출
```

---

## 파일 경로

```
/pscratch/sd/s/sjmoon/EmoFM/CCN/
├── raw_fmri_results/
│   └── fmri_raw.npy                     (5, 2196, 450)
├── video_embeddings/
│   ├── vjepa2_embeddings.npy            (2196, 1408)
│   └── clip_embeddings.npy              (2196, 512)
├── cka_results/
│   ├── rsm_vjepa2.npy                   (2196, 2196)
│   └── rsm_clip.npy                     (2196, 2196)
├── results/
│   ├── brain_jepa_rsm_mean.npy          (2196, 2196) — Brain-JEPA 기반
│   └── crossspace_rsa_results.npz       — Brain-JEPA 기반 (재실행 필요)
└── metadata/
    └── horikawa_meta_data_with_dimension_binary.csv
```
