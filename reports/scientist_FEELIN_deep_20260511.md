# Scientist Analysis: FEELIN (Deep)
분석일: 2026-05-11
범위: 전체 프로젝트 (research_overview, ACTION_PLAN, training_strategy, datasets, task, methodology, framework_EN, CONTEXT, benchmark_design, project_decisions)

---

## 0. 한줄 요약

연구 방향성, dataset 명세, model selection, master matrix, statistical floor까지 잘 짜여 있다. **남아 있는 blind spot은 "scope와 우선순위"의 문제로 옮겨갔다.** 즉 어떤 실험을 먼저 자르고, 어디서 의사결정을 stop할지가 정의되어 있지 않다. 2달이라는 제약에서 이게 가장 큰 위험이다.

---

## 1. SCOPE-KILLING Blind Spots

이것들은 **scope 자체를 무너뜨릴 수 있는** 것들이다. 첫 실험 시작 전에 결정해야 한다.

### 1.1 Compute budget이 없다

Master matrix에 28개 non-NA cell. 각 cell × 4 BFM × 4 window 조건 × multiple targets × multiple seeds.

```
보수적 추정:
28 cells × 4 BFMs × 2 window strategy × 2 seeds = 448 experiments (frozen probe만)
+ adapter tuning: ×2 = 896
+ scratch SL5/10/20/40 (SwiFT만): +16 cells × 4 SL = 64
+ pretraining: HCP movie continued pretraining 자체가 일주일 단위
```

NERSC GPU 할당량(`m4641`)에서 2달 안에 가능한 GPU-hour 추정이 어디에도 없다. **이게 안 정해지면 master matrix 채우는 도중에 시간이 끝난다.**

**결정 필요:** 2달 GPU-hour total, 실험당 평균 예산, "fill 50% matrix" vs "fill 100% matrix" 선택.

---

### 1.2 Data access 상태가 binary로 표시되지 않았다

Master matrix는 RUN/CHECK/NA로 되어 있는데, CHECK는 "format check 필요"인지 "access 자체가 없는지" 구분 안 된다.

현 상태:
- **Horikawa/Cowen**: 있음 (확인됨)
- **HCP 7T movie**: HCP Data Use Agreement 필요. NERSC에 다운로드되어 있는지 미확인
- **Emo-FilM**: OpenNeuro ds004892. 로컬 다운로드 상태 미확인
- **Affective Videos ds000205**: OpenfMRI. 로컬 상태 미확인
- **IAPS fMRI**: NeuroVault collection 16284. beta map 다운로드 가능
- **NeuroEmo ds005700**: OpenNeuro. 미확인
- **Koide-Majima**: access dependent. 거의 불가능
- **REELMO**: Figshare. 미확인
- **CNeuroMod/Algonauts**: 등록 필요

**Master matrix의 7개 dataset × 4 BFM = 28 cell 중 실제 즉시 RUN 가능한 cell은 Horikawa × 4 BFM = 4 cell.** 나머지는 전부 access 대기. 이 사실이 어디에도 명시되어 있지 않다.

**결정 필요:** 지금 당장 ssh로 각 dataset 로컬 경로 확인. binary status table을 만들어서 ACTION_PLAN Step 0로 추가.

---

### 1.3 Input shape 호환성 매트릭스가 없다

각 BFM은 다른 입력 형식을 요구한다.

| BFM | 요구 입력 |
|---|---|
| SwiFT | 96×96×96×SL volumetric |
| NeuroSTORM | 96×96×96×SL volumetric |
| Brain-JEPA | 450 ROI time series |
| BrainLM | A424 atlas time series, 490 timepoints fixed |

Dataset 별로 변환이 필요하다:

| Dataset | Raw shape | → SwiFT/NeuroSTORM | → Brain-JEPA | → BrainLM |
|---|---|---|---|---|
| Horikawa | 74×91×81×variable | resample to 96³ | Schaefer400+Tian50 (done) | A424 미생성 |
| Emo-FilM | 2.5mm isotropic | resample + crop | re-parcellate | re-parcellate |
| Affective Videos | 3mm isotropic | resample + crop | re-parcellate | re-parcellate |
| IAPS | beta maps only | not native | beta-only | beta-only |
| NeuroEmo | 1.8×1.8×4 anisotropic | major resample | re-parcellate | re-parcellate |

**EmoDe README에서 BrainLM 제외 이유 = "num_timepoints=490 고정 → Horikawa 5TR 비호환".** 이건 BrainLM이 다른 모든 dataset에서도 동일하게 부딪힐 문제다. 그런데 benchmark_design.md는 BrainLM을 모든 cell에 포함시켰다.

**결정 필요:** BrainLM을 master matrix에서 제거하거나, BrainLM에 맞는 preprocessing pipeline (490 timepoint manifest)을 명시적으로 정의.

---

## 2. EXPERIMENTAL DECISION Blind Spots

실험 시작은 가능하지만, **결과가 나와도 해석할 수 없는** 항목들이다.

### 2.1 Pass/fail 임계값이 어디에도 없다

methodology.md에는 모든 결정 규칙이 "X가 Y보다 좋으면" 형식이다. 하지만 "좋다"의 임계가 없다.

예시:
- "If frozen SwiFT beats simple baseline" — 0.01 차이도 "beats"인가, 0.10 차이가 필요한가?
- "If naturalistic pretraining helps" — 어떤 effect size가 "help"인가?
- "If alignment improves high-dimensional targets" — 무엇이 "improvement"인가?

**5 subject × 1748 train / 218 test의 setup에서 noise floor 위 어떤 r 차이가 통계적으로 유의한지조차 계산이 안 되어 있다.**

**결정 필요:** dataset별 noise ceiling을 ISC로 측정하고, 그 위에서 effect size threshold를 사전 정의 (예: Δr > 0.02, p < 0.05 with permutation test). 이게 없으면 "decision rule"이 사후 cherry-picking이 된다.

---

### 2.2 Window 전략과 BFM × dataset 조합의 product 폭발

training_strategy.md에는 5개 window 조건이 있다.

```
all observed | SL5 | SL10 | SL20 | SL40
```

× 28 non-NA cells × 4 BFMs = **560 experiment configurations**

각 configuration이 frozen + adapter + scratch 세 변형이라면 = **1680 runs**

**결정 필요:** 1라운드는 **single window only**로 시작. 모든 BFM의 native input length 또는 SL20 하나로 고정. 결과 보고 window sensitivity는 selective하게 확장.

---

### 2.3 5 subject에서 subject-wise 통계는 df=4

methodology.md: "subject-wise metrics with bootstrap confidence intervals"

5명만으로 bootstrap CI는 의미가 약하다. 5명의 mean ± SE에서 SE = SD/√5 = SD×0.45, 95% CI = ±t(4,0.95)×SE = ±2.78×SE. 즉 SD가 작아도 CI가 매우 넓다.

대안:
- **Stimulus-level CI** (n=1748 train stimuli, n=437 test stimuli per subject) — 통계적 검정력 훨씬 높음
- **Permutation test** (label shuffle) — distribution-free, n=5 OK
- **Pooled model with stimulus-stratified split** — subject를 covariate로

**결정 필요:** subject-wise reporting은 보조용. primary inference는 stimulus-level permutation test 또는 pooled model 결과로.

---

### 2.4 Horikawa의 "high-dim emotion vector" 정의 모호

benchmark_design.md에 두 컬럼이 있다.

- Multi-label prediction
- High-dimensional vector prediction (RSA/CKA)

EmoDe metadata 보면 `score_0` ~ `score_33`은 0-1 연속값. Multi-label binary(`label_0` ~ `label_33`)도 따로 있음. 14 affective dimensions도 또 다른 set.

**같은 dataset에 세 가지 다른 target structure가 있는데 master matrix는 하나의 cell로 표시한다.**

| Target 구조 | 차원 | 평가 metric |
|---|---|---|
| 34 binary labels | 34 | macro F1, AUROC |
| 34 continuous scores | 34 | Pearson r per emotion, RSA |
| 14 affective dimensions | 14 | Pearson r per dim |
| Top category | 1 | balanced accuracy |
| Joint 48 (34+14) | 48 | RSA |

**결정 필요:** EmoViS 결정 (2026-05-07)을 FEELIN에 명시적으로 import. "34-category only", "14-dimension only" 두 variant를 별도 cell로 분리. 또는 단일 target 하나로 freeze.

---

### 2.5 "Naturalistic pretraining" Track B의 데이터-시간 mismatch

HCP movie continued pretraining = 184 subjects × 4 movies × ~15min = 약 184시간 fMRI.

NERSC `m4641` cpu queue로는 GPU pretraining이 불가능. GPU queue는 `m4641_g` 또는 별도 할당이 필요. 2달 안에 SwiFT 모델 사이즈에서 HCP 184시간 데이터로 pretraining을 끝낼 수 있는지가 미검증.

**결정 필요:** 
- HCP movie 로컬 path 확인
- SwiFT pretraining 1 epoch wall-clock time 사전 측정 (smoke test)
- 만약 1 epoch이 24시간 이상이면 Track B는 2달 안에 불가, partial epoch만 가능

---

### 2.6 Cross-dataset transfer 정의

methodology.md: "Horikawa → Emo-FilM transfer"

이게 의미하는 게 무엇인가?

해석 A: Horikawa로 학습 → Emo-FilM에서 frozen embedding의 emotion target 예측 성능
해석 B: Horikawa의 emotion category label space를 Emo-FilM의 component label space로 매핑
해석 C: 두 dataset의 representation geometry를 RSA로 비교

세 가지 모두 가능하지만 각각 다른 실험 설계와 다른 결과 해석이 필요하다.

**결정 필요:** Track B 결정 규칙의 "transfer"가 위 세 중 어느 것인지 명시.

---

## 3. DELIVERABLE Blind Spots

결과가 나왔을 때 어디에 쓸 건지에 관한 것들이다.

### 3.1 2달 후 deliverable이 정의되어 있지 않다

framework_EN.md "Expected Contribution"에 5가지가 나열되어 있지만, "이 5가지를 다 만든다"가 아니라 "결과에 따라 골라낸다"인가?

가능한 결과:
- (a) Screening benchmark paper — master matrix를 채운 결과 자체가 contribution
- (b) Model development paper — SwiFT emotion adaptation으로 SoTA
- (c) Negative result paper — "BFM은 emotion에 잘 안 된다"
- (d) Workshop preprint — 진행 보고

**결정 필요:** 8주차에 무엇이 정확히 산출물로 나가는가. workshop paper인지, arXiv preprint인지, conference submission인지. **target venue와 abstract가 사전에 작성되어 있어야** scope creep을 막을 수 있다.

---

### 3.2 EmoViS와의 분리/연결 정의 없음

FEELIN의 stimulus-only baseline은 V-JEPA2, VideoMAE 등을 쓴다. 이건 EmoViS의 stimulus model spectrum과 동일한 도구다.

질문:
- FEELIN의 video model 분석을 EmoViS에서 그대로 재사용할 것인가
- 두 프로젝트의 stimulus feature 추출 코드를 공유할 것인가
- EmoViS의 V-JEPA2 layer-wise feature를 FEELIN의 stimulus baseline으로 쓸 것인가

**결정 필요:** EmoViS `study1/code/`의 V-JEPA2/VideoMAE 추출 결과를 FEELIN `setup/data/`로 symlink. 두 번 추출하지 말 것.

---

## 4. 우선순위 액션 (2주 안)

```
Week 1, Day 1-2:
[즉시] Data access binary check
  - HCP movie, Emo-FilM, Affective Videos, IAPS, NeuroEmo, REELMO 로컬 경로 ls
  - 각 dataset에 대해 access=YES/NO/PARTIAL 표 작성
  - reports/status/dataset_access_2026-05-11.md

Week 1, Day 2-3:
[즉시] Compute budget 측정
  - NERSC m4641 GPU 할당 잔여량 확인
  - SwiFT frozen probe 1 run wall-clock (Horikawa, 1 subject)
  - 추정: total available GPU-hours / per-experiment hour = max experiments

Week 1, Day 3-4:
[즉시] Noise ceiling (ISC) 계산
  - 5명 subject 간 fmri_raw.npy (Horikawa) ISC 추정
  - 결과로 effect size threshold 설정

Week 1, Day 4-5:
[즉시] Input shape conversion matrix 정의
  - dataset × BFM 별 resampling 또는 parcellation 변환 pipeline 명시
  - 변환 코드가 이미 있는지 확인 (Horikawa→Schaefer400 done)

Week 2:
[1라운드] Master matrix에서 RUN-able 4 cell부터 시작
  - Horikawa × {SwiFT, Brain-JEPA, NeuroSTORM} (BrainLM 제외)
  - frozen probe + ridge head only
  - single window (SL5 또는 SwiFT native)
  - 결과 표 작성
```

---

## 5. 연구 계획 업데이트 권고

### A. CONTEXT_FEELIN.md에 추가
- **Compute Budget** 섹션: 2달 GPU-hour total, per-experiment budget, prioritization rule
- **Data Access Status** 섹션: binary YES/NO/PENDING table

### B. notes/benchmark_design.md 수정
- BrainLM 행 전체 제거 또는 BrainLM 전용 pipeline 정의
- 각 cell에 `RUN` 옆에 access 상태 추가 (예: `RUN[OK]` vs `RUN[ACCESS-PENDING]`)
- Phase 0 cells (즉시 가능) vs Phase 1 cells (access 후) 분리

### C. methodology.md "Metrics"에 추가
- Effect size threshold (Δr > 0.02, p < 0.05 permutation)
- Noise ceiling (ISC) 의무화: optional이 아니라 required

### D. ACTION_PLAN.md Step 0 신설
- Data access 확인
- Compute budget 측정
- Noise ceiling 계산
- Input shape conversion 정의
- (현재 Step 1 = Horikawa manifest 확정은 Step 0가 끝난 후)

### E. 2달 deliverable 사전 정의
- 8주차 산출물: workshop preprint? conference paper?
- target venue 명시 (예: NeurIPS workshop submission 2026-07-15 if hitting)
- 미달성 시 fallback (technical report on GitHub)

---

## 6. 한 줄 요약 (다시)

연구 계획은 깊이 있고 충분히 ambitious다. 하지만 **"무엇을 안 할 것인가"가 정의되어 있지 않다.** 2달 안에 8개 modeling question을 모두 답하려는 시도는 아무것도 답하지 못한 채로 끝날 위험이 있다. 가장 시급한 액션은 **scope을 줄이는 결정**이다.
