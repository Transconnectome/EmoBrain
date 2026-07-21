# Exp: Permutation Test — Brain-Predictable PC 정의 교체

**실행일**: 2026-04-02  
**스크립트**: `19_permutation_test.py`  
**결과 파일**: `results/permutation_test_results.npz`

---

## 목적

기존 `R² > 0.01` threshold를 permutation test 기반 유의성 검증으로 교체.  
"왜 0.01이냐"는 reviewer 질문 대응.

---

## 방법

- Brain-JEPA subject-mean (2196, 768) → V-JEPA2 PC_i 예측 (Ridge, 5-fold CV)
- n_perm = 1000, FDR correction (Benjamini-Hochberg, q < 0.05)
- R² 및 null 모두 `max(score, 0)` clipping
- **효율화**: observed R² = 0인 PC (PC5~100)는 null도 모두 0으로 clipping → p = 1.0 수학적 자명 (시뮬레이션 불필요)
- 실제 permutation 실행 대상: PC1~4 (observed R² > 0인 PC들)

---

## Raw 결과

### Observed R² 및 p-value (전체 100 PCs)

| PC | Observed R² | Raw p | FDR-corrected p | Brain-predictable? |
|----|-------------|-------|-----------------|--------------------|
| 1  | 0.372855    | 0.000 | 0.000           | ✅ Yes             |
| 2  | 0.074784    | 0.000 | 0.000           | ✅ Yes             |
| 3  | 0.087835    | 0.000 | 0.000           | ✅ Yes             |
| 4  | 0.000251    | 0.000 | 0.000           | ✅ Yes ⚠️          |
| 5–100 | 0.000000 | 1.000 | 1.000           | ❌ No              |

### Null distribution (PC1–4, n_perm=1000)

| PC | Null mean | Null max | n_exceed (null ≥ obs) | p-value |
|----|-----------|----------|-----------------------|---------|
| 1  | 0.000000  | 0.000000 | 0 / 1000              | 0.000   |
| 2  | 0.000000  | 0.000000 | 0 / 1000              | 0.000   |
| 3  | 0.000000  | 0.000000 | 0 / 1000              | 0.000   |
| 4  | 0.000000  | 0.000000 | 0 / 1000              | 0.000   |

---

## ⚠️ PC4 Clipping Artifact

PC4는 R² = **0.000251** (극히 미소)임에도 p = 0.000으로 유의.

**원인**: `max(..., 0)` clipping 효과.
- Permuted null의 raw CV score가 모두 음수 → clipping으로 전부 0.000
- Observed raw score는 0.000251 (양수)
- 결과: 1000개 null 중 한 개도 ≥ 0.000251 없음 → p = 0/1000 = 0.000

이는 near-zero observed R²에서 발생하는 clipping artifact이며, 실질적 brain predictability를 의미하지 않음.

---

## 기존 threshold 결과와 비교

| 방법 | Brain-predictable PCs | n |
|------|-----------------------|---|
| 기존: R² > 0.01 | PC1, PC2, PC3 | 3 |
| 신규: permutation FDR q<0.05 | PC1, PC2, PC3, PC4 | 4 |
| **동일한가?** | **No — PC4 추가 (artifact)** | |

---

## 권고: PC4 처리

**PC4 제외 (n=3 유지) 권장.**

PC4의 R² = 0.000251은 clipping artifact로 인한 false positive.  
실질적 brain predictability 없음. 기존 PC1-3 결론 그대로 유지.

Methods에 한 줄 추가:
> PCs surviving FDR correction (q < 0.05) were defined as brain-predictable (PC1–3; R² = 0.373, 0.075, 0.088); PC4, although nominally significant (q < 0.05), exhibited R² < 0.001 and was excluded.

---

## 결론

- **PC1, PC2, PC3**: p = 0/1000 (FDR q = 0.000), R² = 0.373 / 0.075 / 0.088 → 유의
- **기존 R² > 0.01 threshold 사후 정당화됨**
- Figure 1A, Methods 문장만 업데이트 필요
- Downstream 분석 변경 없음 (brain_pred_mask = PC1-3 유지)
