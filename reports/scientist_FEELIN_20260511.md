# Scientist Analysis: FEELIN
분석일: 2026-05-11

## 0. 한줄 요약

연구 계획의 방향성과 실험 조건 목록은 잘 짜여 있지만, **실제로 코드를 돌리는 순간 막히는 구체적인 결정**들이 빠져 있다. 특히 HRF lag, window 구성 방식, pooling 전략, split 정의, noise ceiling이 전혀 없어서 첫 실험 결과가 나와도 해석이 불가능하다.

---

## 1. 즉시 결정 필요 항목

### [즉시 결정 1] HRF lag 가정

연구 계획 어디에도 없다.

Horikawa TR이 얼마인지 확인 필요 (2초? 2.5초?). HRF는 자극 시작 후 약 4~6초에서 피크. TR=2.5s이면 2TR delay가 기준. 5TR짜리 stimulus window에서 TR 0~4를 쓰면 HRF 피크가 TR 2~3이고, 이후 TR 4는 이미 내려오는 구간이다.

결정 필요한 것:
- TR이 얼마인가
- fMRI window를 자극 onset 기준으로 정렬하는가, 아니면 peak-HRF 기준으로 shift하는가
- variable-length stimulus에서 peak는 어디인가 (duration 5TR짜리와 20TR짜리의 peak TR이 다르다)
- 결정하지 않으면: 모든 모델이 HRF peak 이전/이후를 뒤섞어 학습하게 되고, "temporal이 재미없다"는 결론이 HRF alignment 문제인지 모델 문제인지 구분 불가

### [즉시 결정 2] Variable duration → fixed SL window 구성 전략

Horikawa는 stimulus duration이 5~47 TR로 가변이다. SL=20으로 맞추려면 다음 중 하나를 선택해야 한다.

| 전략 | 의미 | 문제 |
|---|---|---|
| A: duration ≤ SL만 사용 | clean set, 결측 없음 | 5TR짜리만 사용하면 2185개 중 일부만 남음 |
| B: 전체 padding | 모든 자극 포함 | padding 비율이 모델마다 달라서 비교 공정성 문제 |
| C: stride/crop | 긴 자극에서 여러 window 추출 | 같은 자극의 여러 window가 train/test 동시 존재 → leakage |
| D: valid-frame masking | attention mask 사용 | SwiFT가 실제로 mask를 attention에 반영하는지 검증 필요 |

전략에 따라 sample 수가 달라지고, 그 숫자가 SL별로 다 다르다.

### [즉시 결정 3] SwiFT 출력 pooling 방식

EmoDe에서 SwiFT layer_3 shape = `(768, 2, 2, 2, 10)`. Mean pool → 768-dim. 이 결정이 공간과 시간 정보를 모두 날려버린다.

대안:
- 공간만 pool → 시간 축 유지 → (768, 10) → temporal decoder 가능
- 마지막 frame만 사용 → (768,) → HRF 감안한 late-window feature
- attention pooling → learned readout

"temporal이 재미없다"는 결론이 이 pooling 때문일 수 있다. Mean pool은 시간 정보를 완전히 없애므로 temporal model이 random feature와 다를 이유가 없다.

### [즉시 결정 4] Subject split 정의

5명인데 train/val/test를 어떻게 나누는지 정의가 없다.

Horikawa의 2185 자극은 5명 피험자 모두에게 동일하게 제시된다. stimulus-level split을 하면 sub-01의 stimulus_1이 train에, sub-02의 stimulus_1이 test에 들어갈 수 있다. emotion target이 stimulus에 anchored되어 있으므로 심각한 leakage.

결정: **subject-level LOSO를 primary split으로 먼저 정의하라.**

### [즉시 결정 5] Noise ceiling 정의

EmoDe 결과 Pearson r = 0.165 (Brain-JEPA)가 좋은 건지 나쁜 건지 알 수 없다. Inter-subject correlation (ISC)을 noise ceiling으로 쓸 수 있다. 계획에 noise ceiling이 없으면 모든 결과가 해석 불가 숫자다.

---

## 2. 1라운드 결정 항목

### Subject normalization 방식

EmoDe 전처리는 min-max normalization per-volume. within-subject z-score가 더 안정적일 수 있다. 선택에 따라 모든 결과가 달라진다.

### Multi-subject 학습 방식

pooled model vs per-subject model. pooled 사용 시 subject identity shortcut 가능성. Subject adapter가 필요한지 먼저 결정해야 함.

### Stimulus-only baseline feature 정의

Horikawa는 silent video. V-JEPA2가 첫 번째 선택. 이걸 정하지 않으면 brain model contribution 해석 불가.

### Cross-dataset transfer 조건 사전 확인

Emo-FilM access TBD. 지금 당장 access 가능 여부 확인 필요. 없으면 emotion-labeled pretraining 전체 평가 불가.

### TRIBE fsaverage5 → Schaefer 매핑

TRIBE v2 출력(fsaverage5, ~20k vertices) → Schaefer 450 (MNI) 매핑 toolchain 정의 필요.

---

## 3. 실험 트리

```
Week 1-2: [즉시 결정] 5개 결정 완료 + manifest 확정
├── HRF lag 확인 (TR 값, onset vs peak 정렬)
├── Window 구성 전략 선택 (A/B/C/D)
├── Pooling 방식 선택 (mean vs late-frame vs temporal)
├── Split 정의 (LOSO 확정)
└── Noise ceiling 계산 (ISC)

Week 2-3: [1라운드] Simple brain baselines
├── ROI ridge baseline (Schaefer 400 + Tian)
├── Stimulus-only baseline (V-JEPA2)
└── Noise ceiling 대비 성능 확인

Week 3-4: [1라운드] SwiFT smoke test
├── Frozen SwiFT + linear head (SL20 native, pooling 방식 3종 비교)
├── SwiFT scratch SL5 vs SL20
└── [pivot point] ROI baseline 대비 delta < 0이면 SwiFT deprioritize

Week 4-5: [2라운드] Alternative BFM (Brain-JEPA, NeuroSTORM 재실행, 동일 split/pooling)

Week 5-6: [2라운드] Naturalistic pretraining (HCP movie, Emo-FilM transfer)

Week 6-8: [보류→2라운드] TRIBE alignment
```

---

## 4. Blind Spots 요약

| 항목 | 심각도 | 현재 상태 |
|---|---|---|
| HRF lag 가정 | 치명적 | 어디에도 없음 |
| variable duration → SL 변환 전략 | 치명적 | "use all valid windows"만 언급 |
| SwiFT output pooling 방식 | 치명적 | EmoDe mean pool만, 비교 없음 |
| Noise ceiling (ISC) | 높음 | 없음 |
| Subject LOSO vs stimulus split | 높음 | 정의 없음 |
| Emo-FilM access 확인 | 높음 | TBD |
| Subject normalization 방식 | 중간 | EmoDe minmax, 계획에 없음 |
| Stimulus-only baseline feature | 중간 | 목록만 있고 우선순위 없음 |
| TRIBE fsaverage5 → Schaefer 매핑 | 중간 | toolchain 없음 |
| 2달 주차별 timeline | 중간 | 없음 |

---

## 5. 연구 계획 업데이트 권고

`reference/training_strategy.md`에 다음 섹션 추가 필요:
- "HRF Lag and Window Alignment Policy" (TR 값, onset/peak 결정, variable duration 처리)
- "Output Pooling Strategy" (SwiFT feature pooling 방식 정의)
- "Split and Evaluation Protocol" (LOSO 정의, noise ceiling 계산 방법)

`ACTION_PLAN.md` Step 1 앞에 추가:
- Step 0: TR/HRF 확인, pooling 방식 결정, noise ceiling 계산, Emo-FilM access 확인
