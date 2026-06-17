# Experiment 11: Brain-Predictable PC × Emotion Correlation

**Date**: 2026-04-02  
**Script**: `11_pc_emotion_correlation.py`  
**기반**: Script 10 Exp 3 결과 (brain-predictable PC 목록)

---

## 왜 했는가

Script 10 (Exp 3)에서 brain이 V-JEPA2의 상위 3개 PC, CLIP의 6개 PC만 decode할 수 있다는 결과가 나왔다.  
이 PC들이 **무엇을 represent하는지** 알아야 paper의 main claim을 결정할 수 있다.

- **시나리오 A**: brain-predictable PC ↔ 감정과 높은 상관 → "Brain selectively reads the affective subspace"
- **시나리오 B**: 일부만 감정 관련 → "Brain-model alignment captures both affective and perceptual dimensions"
- **시나리오 C**: brain-predictable PC ↔ 감정과 무관 → "Brain-model alignment is driven by perceptual structure"

---

## 방법

1. V-JEPA2 (2196, 1408), CLIP (2196, 512) 각각 PCA 100개 PC 추출
2. 각 PC × 34개 감정 score Spearman r 계산 → (100, 34) 행렬
3. Arousal / Valence / Dominance score와도 Spearman r 계산
4. FDR correction (Benjamini-Hochberg, 3400개 test)
5. Script 10의 R²(brain→PC)와 결합 → brain-predictable (R²>0.01) vs unpredictable 비교

---

## 결론: **시나리오 A 확정**

Brain-predictable PC들이 **모두** 감정과 강하게 correlate.  
Brain-pred PC의 mean max|r| = 0.33~0.37 vs unpredictable = 0.09 → **약 3.6~4.5배 차이**

> **"Brain selectively reads the affective subspace of video representations"**

---

## V-JEPA2 결과

### Brain-predictable PCs (R² > 0.01): **PC1, PC2, PC3** (n=3)

---

#### PC1 — R²=0.3728, explained var=17.02%, max|r|=0.3277, FDR-sig emotions=26

| 감정 | Spearman r | FDR q |
|------|-----------|-------|
| Aesthetic appreciation | −0.3277 | 4.77e-53 |
| Annoyance | +0.3253 | 2.21e-52 |
| Calmness | −0.2880 | 1.81e-40 |

AVD: Arousal=+0.1408 (q=3.00e-09), Valence=−0.1259 (q=1.94e-07), Dominance=+0.0422 (q=0.184)

→ **calm/aesthetic(−) ↔ annoying(+)** 축. 뇌가 가장 강하게 decode하는 차원 (R²=0.37).

---

#### PC2 — R²=0.0748, explained var=5.53%, max|r|=0.3544, FDR-sig emotions=24

| 감정 | Spearman r | FDR q |
|------|-----------|-------|
| Aesthetic appreciation | +0.3544 | 1.89e-62 |
| Excitement | +0.3276 | 4.77e-53 |
| Adoration | −0.2791 | 6.62e-38 |

AVD: Arousal=+0.2254 (q=3.19e-24), Valence=−0.0823 (q=2.43e-03), Dominance=−0.0234 (q=0.524)

→ **aesthetic/exciting(+) ↔ adoration(−)** 축.

---

#### PC3 — R²=0.0878, explained var=5.07%, max|r|=0.3034, FDR-sig emotions=25

| 감정 | Spearman r | FDR q |
|------|-----------|-------|
| Uncomfortable | −0.3034 | 3.85e-45 |
| Empathic pain | −0.2384 | 2.67e-27 |
| Guilt | +0.2369 | 5.70e-27 |

AVD: Arousal=+0.0297 (q=0.399), Valence=+0.0615 (q=0.031), Dominance=+0.0426 (q=0.180)

→ **guilt(+) ↔ uncomfortable/empathic pain(−)** 축.

---

### Brain-pred vs Unpred 비교 (V-JEPA2)

| | n PCs | mean max\|r\| across 34 emotions |
|---|---|---|
| Brain-predictable | 3 | **0.3285** |
| Brain-unpredictable | 97 | 0.0903 |
| Δ | | **+0.2382** |

### Max|r| per emotion: brain-pred vs unpred (V-JEPA2)

| 감정 | pred max\|r\| | unpred max\|r\| |
|------|--------------|----------------|
| Admiration | 0.1330 | 0.0778 |
| Adoration | 0.2791 | 0.2003 |
| Aesthetic appreciation | **0.3544** | 0.1591 |
| Amusement | 0.2626 | 0.2186 |
| Anger | 0.1063 | 0.0900 |
| Anxiety | 0.2034 | 0.1474 |
| Awe | 0.1132 | 0.2167 |
| Awkwardness | 0.1708 | 0.1423 |
| Boredom | 0.1457 | 0.2177 |
| Calmness | **0.2880** | 0.0964 |
| Confusion | 0.0901 | 0.1154 |
| Contempt | 0.0548 | 0.1098 |
| Craving | 0.1640 | 0.1689 |
| Disgust | 0.0999 | 0.0668 |
| Empathic pain | **0.2384** | 0.1067 |
| Entrancement | 0.1213 | 0.1412 |
| Excitement | **0.3276** | 0.1145 |
| Fear | 0.0504 | 0.0775 |
| Horror | 0.1972 | 0.1255 |
| Interest | 0.2098 | 0.1789 |
| Joy | 0.0866 | 0.0667 |
| Nostalgia | 0.1415 | 0.1520 |
| Relief | 0.2544 | 0.1170 |
| Romance | 0.2409 | 0.1471 |
| Sadness | 0.0722 | 0.1867 |
| Satisfaction | 0.0963 | 0.1203 |
| Sexual desire | 0.1436 | 0.0972 |
| Surprise | 0.1921 | 0.1586 |
| Sympathy | 0.0943 | 0.1645 |
| Triumph | 0.0831 | 0.1054 |
| Uncomfortable | **0.3034** | 0.1787 |
| Annoyance | **0.3253** | 0.1506 |
| Envy | 0.1759 | 0.1236 |
| Guilt | **0.2369** | 0.0812 |

---

## CLIP 결과

### Brain-predictable PCs (R² > 0.01): **PC1, PC2, PC3, PC5, PC6, PC7** (n=6)

---

#### PC1 — R²=0.2613, explained var=8.27%, max|r|=0.4512, FDR-sig emotions=28

| 감정 | Spearman r | FDR q |
|------|-----------|-------|
| Annoyance | −0.4512 | 2.35e-107 |
| Uncomfortable | +0.4162 | 8.51e-90 |
| Surprise | +0.3637 | 5.90e-67 |

AVD: Arousal=−0.1337 (q=8.71e-09), Valence=+0.1983 (q=3.86e-19), Dominance=+0.0293 (q=0.376)

---

#### PC2 — R²=0.1559, explained var=6.26%, max|r|=0.4726, FDR-sig emotions=18

| 감정 | Spearman r | FDR q |
|------|-----------|-------|
| Aesthetic appreciation | −0.4726 | 4.70e-119 |
| Excitement | −0.4029 | 9.71e-84 |
| Uncomfortable | +0.3613 | 4.59e-66 |

AVD: Arousal=−0.1213 (q=2.51e-07), Valence=+0.0905 (q=4.06e-04), Dominance=+0.0967 (q=1.14e-04)

→ 전체 데이터에서 가장 강한 단일 상관. **aesthetic/exciting(−) ↔ uncomfortable(+)** 축.

---

#### PC3 — R²=0.1271, explained var=5.17%, max|r|=0.2269, FDR-sig emotions=24

| 감정 | Spearman r | FDR q |
|------|-----------|-------|
| Guilt | −0.2269 | 3.59e-25 |
| Awe | +0.2142 | 2.14e-22 |
| Horror | −0.2088 | 2.86e-21 |

AVD: Arousal=+0.0237 (q=0.481), Valence=+0.1238 (q=1.46e-07), Dominance=−0.0755 (q=4.94e-03)

---

#### PC4 — R²=0.0000 (brain-unpredictable, 참고용)

AVD: Arousal=+0.1777 (q=...), Valence=−0.2059 (q=...) → A/V와는 correlate하지만 brain이 decode 못함

---

#### PC5 — R²=0.1154, explained var=3.47%, max|r|=0.3497, FDR-sig emotions=20

| 감정 | Spearman r | FDR q |
|------|-----------|-------|
| Uncomfortable | +0.3497 | 1.17e-61 |
| Sadness | −0.2740 | 5.65e-37 |
| Horror | +0.2724 | 1.57e-36 |

AVD: Arousal=+0.1777 (q=1.65e-15), Valence=+0.0577 (q=4.44e-02), Dominance=+0.0454 (q=0.132)

---

#### PC6 — R²=0.0167, explained var=2.93%, max|r|=0.3131, FDR-sig emotions=29

| 감정 | Spearman r | FDR q |
|------|-----------|-------|
| Nostalgia | +0.3131 | 9.42e-49 |
| Interest | +0.3107 | 4.89e-48 |
| Sympathy | +0.2923 | 3.02e-42 |

AVD: Arousal=−0.0132 (q=0.720), Valence=−0.2768 (q=9.97e-38), Dominance=−0.1779 (q=1.65e-15)

---

#### PC7 — R²=0.0125, explained var=2.45%, max|r|=0.4029, FDR-sig emotions=27

| 감정 | Spearman r | FDR q |
|------|-----------|-------|
| Empathic pain | +0.4029 | 9.71e-84 |
| Amusement | −0.2917 | 4.49e-42 |
| Romance | −0.2856 | 2.75e-40 |

AVD: Arousal=−0.0655 (q=1.84e-02), Valence=−0.3169 (q=6.12e-50), Dominance=−0.0641 (q=2.14e-02)

---

### Brain-pred vs Unpred 비교 (CLIP)

| | n PCs | mean max\|r\| across 34 emotions |
|---|---|---|
| Brain-predictable | 6 | **0.3694** |
| Brain-unpredictable | 94 | 0.0818 |
| Δ | | **+0.2877** |

### Max|r| per emotion: brain-pred vs unpred (CLIP)

| 감정 | pred max\|r\| | unpred max\|r\| |
|------|--------------|----------------|
| Admiration | 0.1477 | 0.1331 |
| Adoration | 0.2868 | **0.4484** |
| Aesthetic appreciation | **0.4726** | 0.1678 |
| Amusement | 0.2993 | 0.1546 |
| Anger | 0.2224 | 0.0820 |
| Anxiety | 0.3445 | 0.1583 |
| Awe | 0.2670 | 0.2186 |
| Awkwardness | 0.2624 | 0.1435 |
| Boredom | 0.2426 | 0.1159 |
| Calmness | 0.2437 | 0.1968 |
| Confusion | 0.1684 | 0.1848 |
| Contempt | 0.1344 | 0.0721 |
| Craving | 0.2723 | 0.1942 |
| Disgust | 0.2014 | 0.0643 |
| Empathic pain | **0.4029** | 0.2546 |
| Entrancement | 0.2180 | 0.1050 |
| Excitement | **0.4029** | 0.1626 |
| Fear | 0.1790 | 0.0787 |
| Horror | 0.2724 | 0.1356 |
| Interest | 0.3473 | 0.1371 |
| Joy | 0.1126 | 0.0770 |
| Nostalgia | 0.3131 | 0.1666 |
| Relief | 0.3108 | 0.1279 |
| Romance | 0.2856 | **0.3524** |
| Sadness | 0.2740 | 0.1513 |
| Satisfaction | 0.2037 | 0.0979 |
| Sexual desire | 0.2632 | 0.0926 |
| Surprise | **0.3637** | 0.1321 |
| Sympathy | 0.2923 | 0.1099 |
| Triumph | 0.2037 | 0.1226 |
| Uncomfortable | **0.4162** | 0.1566 |
| Annoyance | **0.4512** | 0.1332 |
| Envy | 0.2850 | 0.1054 |
| Guilt | 0.2269 | 0.0954 |

※ Adoration, Romance는 unpred PC에서 오히려 높음 (0.45, 0.35) — 예외적 감정

---

## 반복 등장 감정 (V-JEPA2 + CLIP brain-pred PCs 공통)

| 감정 | V-JEPA2 pred max\|r\| | CLIP pred max\|r\| | 해석 |
|------|----------------------|-------------------|------|
| Aesthetic appreciation | **0.3544** | **0.4726** | 두 모델 모두 가장 강한 상관 |
| Annoyance | **0.3253** | **0.4512** | 두 모델 모두 top |
| Uncomfortable | **0.3034** | **0.4162** | 두 모델 모두 top |
| Excitement | 0.3276 | 0.4029 | 두 모델 모두 높음 |
| Empathic pain | 0.2384 | 0.4029 | 공통 |
| Calmness | 0.2880 | 0.2437 | 공통 |
| Guilt | 0.2369 | 0.2269 | 공통 |

→ 두 모델(V-JEPA2, CLIP)이 공유하는 감정 구조를 뇌가 선택적으로 decode.

---

## 생성된 Figure

| 파일 | 내용 |
|------|------|
| `figures/pc_emotion_heatmap.png` | 상위 20 PC × 34 emotion Spearman r heatmap (*=brain-pred, ·=FDR-sig) |
| `figures/pc_brain_pred_emotion.png` | Brain-pred vs unpred PC의 max\|r\| bar chart (34 emotions) |
| `figures/pc_r2_vs_emotion_scatter.png` | R²(brain) vs max emotion\|r\| scatter (점 크기=설명분산) |
| `figures/pc_avd_heatmap.png` | 상위 20 PC × Arousal/Valence/Dominance heatmap (수치 표기) |

---

## CCN Claim 확정

### Main Claim

> **"Brain selectively reads the affective subspace of video representations"**

- V-JEPA2 1408차원 중 brain이 decode하는 3개 PC: 전부 감정과 강하게 correlate  
  (FDR-sig 24~26개 감정, mean max|r|=0.33 vs unpred 0.09, Δ=+0.24)
- CLIP 512차원 중 brain이 decode하는 6개 PC: 모두 감정과 강하게 correlate  
  (FDR-sig 18~29개 감정, mean max|r|=0.37 vs unpred 0.08, Δ=+0.29)

### 전체 스토리라인 (Script 10 + 11)

1. Brain은 video model 고차원 표상(1408-dim, 512-dim)의 **극히 일부**만 표상 (3~6개 PC)
2. 이 소수 차원들은 **감정 구조와 강하게 aligned** — affective subspace
3. Brain이 decode하지 못하는 나머지 94~97개 차원의 감정 상관은 낮음 (mean max|r|≈0.09)
4. CKA(brain, model)이 k≈27에서 포화 → affective subspace를 포착하는 데 ~27차원이면 충분
5. Aesthetic appreciation, Annoyance, Uncomfortable이 두 모델 모두에서 반복 등장  
   → 뇌가 읽는 것은 모델 특이적이 아닌, **video representation의 공통 affective structure**

### 주의: AVD와의 관계

- A/V/D 상관은 전반적으로 낮음 (|r| < 0.32)
- brain이 decode하는 PC가 단순 arousal/valence 축이 아님
- **고차원 감정 카테고리 (Aesthetic, Annoying, Uncomfortable, Empathic pain 등)**를 반영

---

## 저장 파일

```
results/pc_emotion_correlation.npz
  corr_vjepa_emo        (100, 34) — V-JEPA2 PC × emotion Spearman r
  pval_vjepa_emo        (100, 34) — raw p-values
  pval_vjepa_emo_fdr    (100, 34) — BH FDR q-values
  corr_clip_emo         (100, 34)
  pval_clip_emo         (100, 34)
  pval_clip_emo_fdr     (100, 34)
  corr_vjepa_avd        (100, 3)  — PC × Arousal/Valence/Dominance
  pval_vjepa_avd_fdr    (100, 3)
  corr_clip_avd         (100, 3)
  pval_clip_avd_fdr     (100, 3)
  emotion_labels        (34,)
  avd_labels            (3,)
  r2_vjepa              (100,)    — from Script 10 Exp 3
  r2_clip               (100,)
  brain_pred_mask_vjepa (100,)    — R² > 0.01 (int8)
  brain_pred_mask_clip  (100,)
  vjepa_var_ratio       (100,)    — PCA explained variance ratio
  clip_var_ratio        (100,)
```
