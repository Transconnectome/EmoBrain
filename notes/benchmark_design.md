# FEELIN Benchmark Design (v2)

Last updated: 2026-05-11

## Goal

`(Dataset) × (BFM × Init) × (Task)` 그리드를 채워서 **어디에 emotion signal이 있고 어디에 없는지** 지도를 만든다.

이 매트릭스 자체가 첫 deliverable이다. 매트릭스를 채운 결과에 따라:
- 어떤 BFM이 baseline 위에 있는가
- resting-state pretraining이 scratch보다 나은가
- 어떤 task가 안정적으로 학습되는가
- 어떤 dataset이 robust한 signal을 제공하는가

를 결정한 후, **두 가지 search track (pretraining/adaptation, multimodal)** 중 어디로 갈지 정한다.

---

## Axes

### A. Dataset Axis

| Dataset | Status | Subjects | Stimuli | TR | Role |
|---|---|---:|---|---:|---|
| Horikawa/Cowen | **HAVE** | 5 | 2,185 short videos | 2.0s | core high-dim affect geometry |
| Emo-FilM | DOWNLOAD | 30 | 14 short films | 1.3s | naturalistic component/appraisal/dynamic |
| Affective Videos (ds000205) | DOWNLOAD | 11 | 32 × 4 = 128 trials | 2.2s | fast V/A sanity |
| IAPS fMRI (NeuroVault) | DOWNLOAD | 56 | 90 IAPS images (beta maps) | 2.5s | static valence category |
| NeuroEmo (ds005700) | DOWNLOAD | 40 | block design, 5 classes | 3.0s | cross-cultural multi-class |

**Excluded:**
- Koide-Majima/Nishimoto: access dependent, defer
- REELMO: one-movie fMRI (Jojo Rabbit), defer to Phase 2

### B. Model × Init Axis (6 conditions)

3 BFM × 2 initialization = 6 model conditions per (dataset, task) cell.

| BFM | Resting-state pretrained init | Scratch init |
|---|---|---|
| SwiFT | existing checkpoint (Transconnectome lab) | random init, same architecture |
| Brain-JEPA | `jepa-ep300.pth` (ABCD resting) | random init |
| NeuroSTORM | `pt_neurostorm_mae_ratio0.5.ckpt` | random init |

**핵심 비교**: 같은 architecture에서 weight initialization만 차이. 이게 H1을 직접 테스트한다 ("resting-state BFM transfer is useful but incomplete").

**BrainLM 제외**: 490 timepoint fixed, A424 atlas 고정 → Horikawa(5 TR) 비호환. EmoDe에서 검증됨 (Pearson r ≈ 0.012, chance 수준).

### C. Task Axis (5 levels)

| Level | Name | Output | Primary metric | Secondary metric |
|---|---|---|---|---|
| L0 | High/Low V/A binary | binary class | AUROC | balanced accuracy |
| L1 | V/A regression | continuous (1D) | Pearson r | MAE |
| L2 | One-hot classification | top-1 emotion label | balanced accuracy | macro F1 |
| L3 | Multi-label classification | multi-emotion prob vector | macro F1 | AUROC |
| L4 | Continuous dynamics | time-windowed trajectory | CCC | lagged correlation |

---

## Master Matrix: Dataset × Task Compatibility

각 cell의 가능 여부를 표시. 각 valid cell마다 6 model conditions를 돌린다.

| Dataset | L0 binary V/A | L1 V/A reg | L2 one-hot | L3 multi-label | L4 dynamics |
|---|---|---|---|---|---|
| Horikawa | RUN | RUN | RUN (top cat from 34) | RUN (34 cont scores) | NA (short clips) |
| Emo-FilM | RUN | RUN | CHECK | RUN (50 items) | RUN (TR-level) |
| Affective Videos | RUN (4 quadrants → V/A) | RUN | RUN (4 quadrants) | NA | NA |
| IAPS | RUN (pos/neg) | NA (beta only) | RUN (pos/neu/neg) | NA | NA |
| NeuroEmo | CHECK (V/A from labels) | NA | RUN (5 class) | CHECK (overlap) | NA |

**Valid (dataset × task) pairs: 17**

```
Horikawa:         L0, L1, L2, L3        = 4
Emo-FilM:         L0, L1, L3, L4         = 4 (L2 check)
Affective Videos: L0, L1, L2             = 3
IAPS:             L0, L2                 = 2
NeuroEmo:         L2                     = 1 (L0/L3 check)
+ CHECK cells:                            = 3
Total valid: 14 confirmed + 3 CHECK = 17
```

**Total cells = 17 valid pairs × 6 model conditions = 102 cells.**

---

## Statistical Floor

각 task에 대해 BFM 없이 돌리는 baseline. BFM이 이걸 못 이기면 BFM 가치 없음.

| Task | Floor model | Input |
|---|---|---|
| L0 binary | Logistic regression | ROI/parcel mean features |
| L1 regression | Ridge regression | ROI/parcel mean features |
| L2 one-hot | Multinomial logistic | ROI/parcel mean features |
| L3 multi-label | per-class logistic / multi-output ridge | ROI/parcel mean features |
| L4 dynamics | Ridge on sliding-window FC | dynamic FC features |

Floor model input은 dataset별로 정의된 표준 parcellation 사용 (Horikawa는 Schaefer 400 + Tian 50 = 450 features).

---

## Pass/Fail Threshold (사전 정의)

각 cell에서 BFM이 "win"으로 분류되려면 세 가지를 모두 만족해야 한다:

```
1. Δ(BFM - floor) > 2 × pooled SE         (statistical significance)
2. Δ(BFM - floor) > 0.02 (absolute)        (practical effect size)
3. Permutation test p < 0.05               (label-shuffle null)
```

분류 라벨:
- `WIN` — 세 조건 모두 만족
- `MARGINAL` — 1 또는 2만 만족
- `PAR` — BFM ≈ floor
- `LOSE` — BFM < floor
- `FAIL` — 학습 자체 실패 (NaN, divergence)

추가 비교 (BFM 간):
- 같은 architecture의 resting vs scratch 비교 — Δ > 2 × SE이면 resting pretraining이 도움
- BFM 간 비교 — 같은 (dataset, task)에서 가장 높은 BFM 식별

---

## Noise Ceiling (의무)

각 dataset에 대해 inter-subject correlation (ISC)을 사전 계산.

```
Horikawa: ISC across 5 subjects on emotion ratings → ceiling per task
Emo-FilM: ISC across 30 subjects on annotations → ceiling per item
Affective Videos: across 11 subjects → ceiling
IAPS: across 56 subjects → ceiling
NeuroEmo: across 40 subjects → ceiling
```

모든 BFM 성능은 ceiling 대비 % 로 보조 표시.

---

## Result Table Schema

각 cell이 채워지면 다음 row를 생성:

| Dataset | BFM | Init | Task | Floor score | BFM score | Δ | SE | Permut p | Ceiling | Class | Decision |
|---|---|---|---|---|---|---|---|---|---|---|---|

- `Init` ∈ {scratch, resting-pretrained}
- `Class` ∈ {WIN, MARGINAL, PAR, LOSE, FAIL}
- `Decision` ∈ {keep, drop, revisit}

---

## Split Policy

모든 cell에 동일 split 적용. dataset별:

| Dataset | Split | n_train | n_test |
|---|---|---|---|
| Horikawa | stimulus-stratified (모든 5 subjects 공통) | 1748 × 5 = 8740 | 437 × 5 = 2185 |
| Emo-FilM | film-stratified (held-out films) | TBD | TBD |
| Affective Videos | trial-level (4 repetitions 같은 split에) | TBD | TBD |
| IAPS | subject-stratified | TBD | TBD |
| NeuroEmo | subject-stratified | TBD | TBD |

Cross-dataset transfer는 Phase 2 (benchmark 채운 후).

---

## Execution Roadmap (8 weeks)

```
Week 1: Data download + access verification
  - HCP credential 확인 (Phase 2 대비)
  - Emo-FilM (OpenNeuro ds004892) download
  - Affective Videos (OpenfMRI ds000205) download
  - IAPS NeuroVault collection 16284 download
  - NeuroEmo (OpenNeuro ds005700) download
  - 각 dataset access status table 작성

Week 2: Preprocessing harmonization
  - Schaefer 400 + Tian 50 parcellation 모든 dataset에 적용
  - SwiFT/NeuroSTORM 입력 형식 (96×96×96) 변환
  - Brain-JEPA ROI 입력 변환
  - ISC noise ceiling 계산

Week 3-4: Horikawa 전체 cell 채우기
  - Horikawa × 6 models × 4 tasks = 24 cells
  - frozen probe + linear/ridge head
  - 각 cell × 5 seeds → mean ± SE 산출

Week 5-6: 나머지 dataset cell
  - Emo-FilM × 6 × 4 = 24 cells
  - Affective Videos × 6 × 3 = 18 cells
  - IAPS × 6 × 2 = 12 cells
  - NeuroEmo × 6 × 1 = 6 cells

Week 7: Decision table
  - WIN/MARGINAL/PAR/LOSE 분류
  - Pattern 분석: scratch vs resting, BFM 간 차이, task별 안정성
  - Two-track decision: pretraining/adaptation vs multimodal 어디로 갈지

Week 8: Writeup
  - 결과에 따른 paper framing 결정
  - workshop preprint 또는 arXiv
```

---

## After The Master Matrix

| Benchmark finding | Direction |
|---|---|
| Resting-pretrained > scratch consistently | resting pretraining is partial transfer; pursue movie/task pretraining (Track B Pretraining) |
| Scratch ≈ resting-pretrained | resting pretraining adds nothing for emotion; investigate target-aware pretraining |
| BFMs ≈ floors | input representation / window / pooling 문제; revisit preprocessing |
| Some BFMs WIN on L1/L2 but LOSE on L3/L4 | rich emotion targets need stimulus context; pursue multimodal (Track C) |
| All BFMs LOSE on Emo-FilM | naturalistic context modeling 부족; movie pretraining 필수 |
| Specific BFM dominates | scale that BFM; pursue adapter/fine-tuning |

---

## Excluded Considerations (Phase 2 이후)

다음은 Phase 1 benchmark에 포함하지 않음:
- TRIBE v2 stimulus-only baseline
- HCP/CNeuroMod/StudyForrest 등 naturalistic pretraining
- Adapter, LoRA, fine-tuning variants (frozen probe만)
- Stimulus-brain alignment
- Affective LLM/VLM brain-tuning
- Window length sweep (SL5/10/20/40) — single window only

이것들은 Phase 1 결과 따라 Phase 2에서 선택적으로 활성화.

---

## Phase 1 Deliverable

8주차 산출물:
1. **Filled master matrix** (102 cells with class labels)
2. **Decision table** (BFM × task × init별 WIN/LOSE 패턴)
3. **Track choice document** (Phase 2 방향 결정 근거)
4. **Workshop preprint draft** (target: NeurIPS workshop 또는 ICLR workshop)
