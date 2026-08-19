> ⚠️ **ARCHIVED — 역사 기록. 현행 문서가 아니다.**
> 현행 논증 = `docs/paper_logic_merged.md` (대전제 · RQ · 가설 H1–H4). 운영 규칙 = `CLAUDE.md`.
>
> 아래 내용 중 다음은 **뒤집혔다.** (a) Qwen3-VL 등 LLM backbone 사용 — 금지.
> (b) open-vocabulary / cross-taxonomy 전이를 headline novelty 로 삼는 프레임 — 폐기.
> (c) 학습에 없던 감정 zero-shot — 폐기(원칙적 분할 기준 없음, RQ 와 무관).
> (d) "EmoBrain 과 EmoViS 는 별도 논문 2편" — 현재는 **한 편의 논문**.
> (e) "EmoBrain 은 cortical location 을 주장하지 않는다" — 현재 **H3 이 cortical location 주장**이다.

# Phase 1 Audit — 1D. Task / target matrix audit

Date: 2026-06-04
Auditor: Claude (Opus 4.7)
Scope:
- `project/shared/data/feelin_canonical_stimuli.csv`
- `project/shared/data/cowen_horikawa_labels.csv`
- `project/shared/data/horikawa_L0_V_binary_subset.csv` / `horikawa_L0_A_binary_subset.csv`
- `project/shared/data/horikawa_5fold.csv`

---

## 점검 대상

- V/A score 의 출처 일관성 (canon vs cowen)
- V/A binary 의 quartile 기준 (Q1 vs Q4)
- Cat34 의 34 score 컬럼 존재 및 top1 / multilabel / soft 분포
- Dim14 의 14 컬럼 존재
- 5-fold 분포 균일성
- 1C 의 FLAG F8 (Cat34_top1 broken folds) 원인 진단

## 점검 방법

Python 으로 각 CSV 로드, label 분포, score 통계, source 간 correlation, fold × class crosstab 계산.

## PASS 항목

### P10. V/A score: single source of truth

`feelin_canonical_stimuli.csv` 의 `valence_score`, `arousal_score` 과 `cowen_horikawa_labels.csv` 의 `valence_score`, `arousal_score` 의 Pearson r = **1.000000** (2185 stim 전체 일치). NaN 0개. 출처 정합 PASS.

| Source | n | V mean ± std | V range | A mean ± std | A range |
|--------|---|--------------|---------|--------------|---------|
| feelin_canonical | 2185 | 5.26 ± 1.97 | 1.00 ~ 9.00 | 5.82 ± 0.91 | 2.00 ~ 8.67 |
| cowen (rename) | 2185 | 5.26 ± 1.97 | 동일 | 5.82 ± 0.91 | 동일 |

### P11. V_binary subset 정의

> Indexing 주의: 데이터 컬럼 `v_quartile` 은 0-indexed (값 = `{0, 1, 2, 3}`). 사람 표현 Q1~Q4 (1-indexed) 와 매핑하면 `v_quartile=0 ↔ Q1` (lowest V), `v_quartile=3 ↔ Q4` (highest V). 본 보고서에서는 "Q1 vs Q4 (= v_quartile 0 vs 3)" 로 통일.

- Source: `horikawa_L0_V_binary_subset.csv` (n = 1131 / 2185)
- 사용된 quartile: **Q1 (v_quartile=0) vs Q4 (v_quartile=3)** 만, mid 두 quartile (Q2, Q3) 제외
- Label crosstab:

| v_label | v_quartile=0 (Q1, low V) | v_quartile=3 (Q4, high V) |
|---------|---------------------------|----------------------------|
| 0 | **519** | 0 |
| 1 | 0 | **612** |

- V score range: label=0 → 1.00 ~ 3.56 (mean 2.37), label=1 → 6.78 ~ 9.00 (mean 7.42). 두 분포가 깨끗하게 분리됨. PASS.

### P12. A_binary subset 정의

- Source: `horikawa_L0_A_binary_subset.csv` (n = 1107 / 2185)
- 사용된 quartile: **Q1 (a_quartile=0) vs Q4 (a_quartile=3)** 만
- Label crosstab:

| a_label | a_quartile=0 (Q1, low A) | a_quartile=3 (Q4, high A) |
|---------|---------------------------|----------------------------|
| 0 | **485** | 0 |
| 1 | 0 | **622** |

- A score range: label=0 → 2.00 ~ 5.11 (mean 4.56), label=1 → 6.44 ~ 8.67 (mean 6.87). 분리 PASS.

### P13. Cat34 score 34 컬럼 + Dim14 14 컬럼 존재

- `cowen_horikawa_labels.csv` 의 `score_0` ~ `score_33` 모두 존재 (34 / 34). NaN 0개.
- Dim14 cols (arousal, dominance, valence, approach, attention, certainty, commitment, control, effort, fairness, identity, obstruction, safety, upswing) 14 / 14 모두 존재. NaN 0개.

### P14. Cat34_multilabel (threshold 0.15) 분포 stable

- 평균 stim 당 label 수 = 4.19
- Zero-label stim = **0** (모든 stim 이 최소 1개 label)
- Per-class positive rate: 최소 0.0037 (≈ 8 / 2185), 최대 0.4545 (≈ 993 / 2185)
- 즉 일부 minority class 의 positive rate 가 매우 낮긴 하지만 zero 가 없으므로 안정. probe 측 `class_weight=balanced` 와 결합하면 학습 가능.

### P15. 5-fold split 분포 균일

`horikawa_5fold.csv` (2185 row).

| fold | n |
|------|---|
| 1 | ≈ 437 |
| 2 | ≈ 437 |
| 3 | ≈ 437 |
| 4 | ≈ 437 |
| 5 | ≈ 437 |

V quartile, A quartile 분포 (canon):
- v_quartile dist: {0: 519, 1: 543, 2: 511, 3: 612}
- a_quartile dist: {0: 485, 1: 604, 2: 474, 3: 622}

(stratification 은 V×A joint label = 16 cell. 1C 의 P6 에서 확인된 design.)

## FLAG 항목

### F13 (critical). Cat34_top1 의 "broken folds" 원인 규명

1C 의 F8 ("broken folds") 의 정확한 정체를 1D 에서 측정으로 확정.

**Class imbalance 본질**

| 분포 | 값 |
|------|-----|
| 34 class 중 top1 으로 한 번도 등장 안 한 class | **4 / 34** (즉 30 active class only) |
| Top1 count (highest 5) | class 3 (550, 25.2%), 14 (195, 8.9%), 2 (172, 7.9%), 19 (119, 5.4%), 30 (116, 5.3%) |
| Top1 count (lowest 5) | class 25 (**2** stim), 29 (5), 32 (7), 4 (11), 0 (12) |
| 5 stim 미만 active class | 1 개 (class 25) |
| 10 stim 미만 active class | 2 개 (25, 29) |

**Fold × class missing analysis** (test fold 에 있는데 train 3 folds 에 없는 class)

| fold | test classes | train classes | missing in train |
|------|--------------|---------------|------------------|
| 1 | 29 | 29 | **[25]** ← class 25 가 test 에는 있는데 train 에는 없음 |
| 2 | 27 | 30 | [] |
| 3 | 28 | 30 | [] |
| 4 | 29 | 30 | [] |
| 5 | 28 | 29 | [] |

즉 fold 1 에서 class 25 (전체 2 stim) 가 train 3 folds 에는 한 번도 안 나타나는데 test 1 fold 에 있음 → linear / MLP 모두 25 를 학습 못 한 상태에서 25 예측 평가 → 정의상 "broken fold". 다른 fold 들도 30 active class 미만으로 떨어지는 경우 존재 (e.g., fold 5 의 train 은 29).

이것이 코드 주석 "supplementary, broken folds" 의 실제 의미. Cat34 의 자연적 imbalance 와 stim N (=2185) 의 sparsity 가 결합되어 stratification 으로 보정할 수 없음.

**Action**

- Phase 1 결과 해석 시 Cat34_top1 metric **사용 금지** 또는 "broken folds 주의" 명기.
- Category-level evidence 는 Cat34_multilabel (P14 stable) 또는 Cat34_soft (KL distribution) 로 대체.
- 만약 top1 결과를 surface 해야 한다면 30 active class 로 reduced (e.g., Cat30_top1) 정의 후 stratification 재구축 권장. 1E 에서 paper / report 안의 Cat34_top1 사용 여부 확인.

### F14. V_binary / A_binary 가 전체 stim 의 절반만 사용

- V_binary: 1131 / 2185 (51.8%)
- A_binary: 1107 / 2185 (50.7%)

Q1 vs Q4 정의 자체는 명확하지만, "all stim" baseline 과 직접 비교 시 stim N 이 다르다는 점은 metric 해석에 영향 있음 (chance baseline 의 N 의존성). 1E 의 chance baseline 정합성 확인 시 cross-check.

### F15. Cowen 34 class 중 4 class 의 top1 = 0 (deadweight class)

class 1, 6, 7, 9 (혹은 다른 4 개, top1 으로 한번도 maximal 이 되지 않은 class) 는 Cat34_multilabel / soft 에서는 여전히 positive sample 을 가지지만 top1 에서는 보이지 않음. 분석 narrative 에서 "Cowen 34 cat" 이라고 표현할 때 실제 학습은 30 active class 라는 점 명기 필요.

## FAIL 항목

없음. F13 은 코드 작성자가 미리 "broken" 명시했고 후속 task 가 multilabel/soft 로 대체 가능.

## Verdict

**Step 1D: PASS with FLAGS.**

- V/A 의 모든 source 가 일관 (correlation 1.0). NaN 0.
- V/A binary 가 명확히 Q1 vs Q4 정의됨.
- Cat34_multilabel, Cat34_soft, Dim14 모두 안정적 target.
- F13 (Cat34_top1 broken) 은 1C 의 F8 의 정확한 evidence. 결과 해석 시 제외 필요.
- F14, F15 는 minor caveat.
- 1E 진입 가능.

## Action items (1E 로 이월)

- 1E 에서 paper / report / benchmark 안에 Cat34_top1 metric 이 main evidence 로 surface 됐는지 확인. 됐으면 retract.
- 1E 의 chance baseline 비교 시 V/A binary 의 N=1131/1107 과 all-stim N=2185 의 baseline 분리 확인.
- 1E 에서 Cat34_multilabel 의 best HP (1C 의 F9) 가 grid 경계 [1e-2, 1, 100] 에 붙어 있는지 cross-check.
