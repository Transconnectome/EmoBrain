# NetFeeliX 한국어 가이드

**NetFeeliX**는 감정 이론 프로젝트가 아니라, **emotion representation을 잘
포착하는 emotion-specific brain foundation model / brain model을 만들기 위한
모델 개발 프로젝트**입니다.

정식 이름은 다음과 같습니다.

```text
Neural nETwork For Emotion rEpresentation Learning and Inference in NeuroX
```

한 줄로 말하면:

> NetFeeliX는 emotion/affect fMRI에서 가능한 기본 실험을 먼저 넓게 펼쳐
> `Dataset x BFM x Task` master matrix를 채운 뒤, 그 결과로 search space를
> 좁혀가며 emotion-specific brain foundation model을 개발하는 프로젝트입니다.

---

## 제일 먼저 보면 되는 파일

처음 들어왔을 때는 아래 순서대로 보면 됩니다.

1. `README_KR.md`
   - 지금 읽는 파일입니다. 전체 구조를 한국어로 설명합니다.
2. `ONBOARDING.md`
   - 새 연구자나 AI agent가 어떤 문서를 읽어야 하는지 정리한 파일입니다.
3. `CONTEXT_NETFEELIX.md`
   - NetFeeliX의 핵심 방향만 압축한 single source of truth입니다.
4. `research_overview.md`
   - Teams 공유, abstract, presentation 준비용 상세 research overview입니다.
5. `ACTION_PLAN.md`
   - 지금 무엇을 해야 하는지 단계별로 정리한 실행 계획입니다.
6. `Paper/framework_KR.md`
   - 외부 공유와 연구 논의를 위한 전체 연구 프레임워크 한국어 버전입니다.
7. `reference/datasets.md`
   - 사용할 수 있는 dataset을 기능별로 정리한 문서입니다.
8. `reference/training_strategy.md`
   - SwiFT를 어떻게 pretrain, finetune, modify, align할지 정리한 문서입니다.
9. `workflows/README.md`
   - 앞으로 AI와 함께 문헌 조사, 실험 계획, 리뷰, 주간 보고를 어떻게 운영할지 설명합니다.

---

## NetFeeliX의 핵심 방향

NetFeeliX의 중심 질문은 이것입니다.

```text
어떻게 하면 emotion-relevant representation을 가장 잘 담아내는
brain foundation model / emotion-specific brain model을 만들 수 있는가?
```

여기서 중요한 점은 세 가지입니다.

### 0. Benchmark는 최종 목적이 아니라 첫 게이트

현재 `Dataset x BFM x Task` benchmark는 프로젝트의 최종 thesis가 아닙니다.
목적은 가능한 기본 실험을 모두 펼쳐서 어떤 dataset, BFM, task, target, window,
baseline에서 신호가 있는지 확인하고 search space를 줄이는 것입니다.

그 이후 큰 길은 두 갈래입니다.

| Branch | 질문 | 예시 strategy |
|---|---|---|
| Pretraining / adaptation | generic resting/general BFM을 emotion-specific하게 만들려면 어떤 fMRI learning signal과 loss가 필요한가? | task-fMRI/movie-fMRI pretraining, masked/future latent prediction, JEPA-style objective, contrastive loss, emotion-supervised multi-task loss, adapter/late-block tuning |
| Multimodal framework | emotion은 stimulus context와 brain dynamics가 함께 있어야 잡히는가? | TRIBE-like stimulus-to-brain alignment, video model + brain model late fusion, video/audio/text embedding injection, stimulus-only control, brain-stimulus joint latent |

즉 benchmark는 “작게 끝내는 프로젝트”가 아니라, 큰 emotion-specific BFM search를
헛발질 없이 시작하기 위한 첫 단계입니다.

### 1. SwiFT-first but not SwiFT-locked

SwiFT는 먼저 검증할 brain backbone입니다. 하지만 최종 목적은 SwiFT를 지키는 것이 아니라 emotion prediction과 affective representation에 유용한 neural representation을 찾는 것입니다.

첫 benchmark의 모델 축은 Brain Foundation Model입니다.

| BFM | 역할 |
|---|---|
| SwiFT | primary BFM |
| Brain-JEPA | alternative BFM |
| NeuroSTORM | alternative 4D BFM |
| BrainLM | alternative time-series BFM |

logistic/ridge/ROI/voxel 모델은 비교용 statistical floor입니다. Model Axis의
중심은 아닙니다.

각 BFM이 어떤 모델인지, 입력 형식이 무엇인지, 먼저 확인할 위험 요소가 무엇인지는
`reference/code_resources.md`와 `reference/papers.md`를 봅니다.

### 2. TRIBE v2는 현재 benchmark 축이 아님

TRIBE v2는 fMRI를 입력으로 받는 brain encoder가 아닙니다.

TRIBE v2는:

```text
video/audio/text stimulus -> predicted brain response
```

를 수행하는 **stimulus-to-brain encoding model**입니다.

따라서 TRIBE v2는 현재 `Dataset x BFM x Task` benchmark가 끝난 뒤 다음처럼 씁니다.

- stimulus-only baseline
- stimulus-to-brain teacher
- SwiFT latent와 alignment할 대상
- multimodal context feature extractor

즉, TRIBE v2는 현재 BFM benchmark의 모델 축이 아니라, 이후 BFM 결과를 해석하거나
확장하기 위한 stimulus-side component입니다.

### 3. 첫 산출물은 거대한 조합표

초기 작업의 핵심은 순차적인 roadmap이 아니라 모든 조합을 펼친 master matrix입니다.

```text
Dataset x BFM x Task
```

각 cell은 `RUN`, `CHECK`, `NA`로 표시하고, 실행된 cell에는 target, split, metric,
statistical floor, BFM score, status, decision을 채웁니다.

### 4. Emotion Foundation Model이라고 바로 주장하지 않음

아직은 "Emotion Foundation Model을 만들었다"고 말하면 과합니다.

지금 단계에서는 더 정확하게 다음처럼 표현합니다.

- emotion-specific brain representation model
- emotion-aware fMRI foundation-model strategy
- SwiFT-based emotion representation learning framework

최종적으로는 emotion representation을 잘 담아내는 brain foundation model에
가까워지는 것이 목표입니다. 다만 그 주장은 benchmark, pretraining/adaptation,
multimodal control/alignment 실험을 거쳐 증거가 쌓인 뒤에 해야 합니다.

## 세부 설명은 어디서 보나?

`README_KR.md`는 입구 문서라서 최소 설명만 둡니다. 이름만 보고 헷갈리면 아래를 봅니다.

| 알고 싶은 것 | 볼 파일 |
|---|---|
| Horikawa, Emo-FilM, Affective Videos, IAPS가 무슨 dataset인지 | `reference/datasets.md` |
| SwiFT, Brain-JEPA, NeuroSTORM, BrainLM이 무슨 모델인지 | `reference/code_resources.md`, `reference/papers.md` |
| binary/regression/multiclass/high-dimensional task가 뭔지 | `reference/task.md` |
| 현재 거대한 `Dataset x BFM x Task` 표 | `notes/benchmark_design.md` |
| matrix를 채운 뒤 adapter/pretraining/alignment를 어떻게 할지 | `reference/training_strategy.md`, `ACTION_PLAN.md` |

---

## 전체 폴더 구조

현재 NetFeeliX는 이렇게 구성되어 있습니다.

```text
NetFeeliX/
├── README.md
├── README_KR.md
├── ACTION_PLAN.md
├── ONBOARDING.md
├── CONTEXT_NETFEELIX.md
├── CLAUDE.md
├── CODEX.md
├── Paper/
├── reference/
├── notes/
├── templates/
├── workflows/
├── scripts/
├── reports/
├── code/
└── setup/
```

각 폴더의 역할은 아래와 같습니다.

## `Paper/`

논문/제안서 수준의 큰 프레임워크를 저장하는 곳입니다.

중요 파일:

- `framework_EN.md`
- `framework_KR.md`
- `methodology.md`

여기에 들어가는 내용:

- 전체 연구 내러티브
- 외부 공유 가능한 연구 방향
- methodology
- model-development track
- benchmark-to-model-development 전략

주의:

> project brief, proposal outline, narrative 같은 중복 파일을 새로 만들지 말고, 큰 프레임워크는 항상 `framework_EN.md`, `framework_KR.md`에 합칩니다.

## `reference/`

문헌, dataset, task, model/code resource를 정리하는 곳입니다.

중요 파일:

- `datasets.md`
- `task.md`
- `training_strategy.md`
- `systematic_reference_map.md`
- `papers.md`
- `code_resources.md`

각 파일 역할:

| 파일 | 역할 |
|---|---|
| `datasets.md` | dataset을 기능별로 정리 |
| `task.md` | 어떤 task를 할 수 있는지 정리 |
| `training_strategy.md` | SwiFT-first 학습 전략 |
| `systematic_reference_map.md` | 문헌 흐름 지도 |
| `papers.md` | 개별 논문 메모 |
| `code_resources.md` | 관련 GitHub/code resource |

## `templates/`

앞으로 새 내용을 만들 때 쓰는 양식입니다.

예를 들어:

- 새 논문을 정리할 때: `paper_note.md`
- 새 dataset을 평가할 때: `dataset_card.md`
- 새 실험 아이디어를 만들 때: `experiment_card.md`
- 새 모델을 검토할 때: `model_card.md`
- red-team review를 할 때: `review_card.md`
- 중요한 결정을 기록할 때: `decision_log.md`

이 폴더의 목적은:

> AI가 마음대로 이상한 `.md` 파일을 늘리지 않고, 정해진 형식으로 연구 산출물을 만들게 하는 것입니다.

## `workflows/`

AI와 함께 연구를 운영하는 절차를 적어둔 곳입니다.

중요 파일:

- `literature_sota_workflow.md`
- `experiment_planning_workflow.md`
- `red_blue_team_review.md`
- `weekly_update_workflow.md`

각 workflow의 의미:

| Workflow | 언제 사용? |
|---|---|
| literature/SOTA | 새 논문, dataset, model을 조사할 때 |
| experiment planning | 실험 아이디어를 runnable experiment로 바꿀 때 |
| red-blue team review | 모델 전략이나 주장을 비판적으로 검토할 때 |
| weekly update | 프로젝트 상태를 주간 단위로 요약할 때 |

## `scripts/`

project-operation 자동화 스크립트만 둡니다. 실험 실행 스크립트는 `setup/code/`에 둡니다.

현재 스크립트:

| Script | 역할 |
|---|---|
| `check_md_completeness.py` | 문서 구조와 필수 항목이 빠지지 않았는지 검사 |
| `build_project_status.py` | 현재 프로젝트 상태 보고서 생성 |
| `generate_experiment_cards.py` | experiment card 자동 생성 |

자주 쓰는 명령:

```bash
python3 scripts/check_md_completeness.py
python3 scripts/build_project_status.py
python3 scripts/generate_experiment_cards.py --id NFx-001 --title "Frozen SwiFT Horikawa probe"
```

## `setup/code/`

실제 setup 또는 실험성 실행 스크립트를 둡니다.

| Script | 역할 |
|---|---|
| `build_horikawa_window_manifest.py` | Horikawa 2185 stimuli 기준 window manifest 생성 |
| `run_tribe_horikawa.py` | TRIBE v2를 Horikawa stimulus에 적용 |
| `run_tribe_horikawa.sh` | TRIBE batch wrapper |

## `reports/`

AI가 생성한 상태 보고서, 리뷰 결과, 주간 업데이트를 저장하는 곳입니다.

구조:

```text
reports/
├── status/
├── reviews/
└── weekly/
```

예를 들어 `build_project_status.py`를 실행하면:

```text
reports/status/PROJECT_STATUS.md
```

가 생성됩니다. 이 파일은 자동 생성물이므로 Git에는 저장하지 않습니다.

## `setup/`

실제 실험을 시작하기 전에 데이터, 타깃, baseline 가능성을 확인하는 준비 작업 공간입니다.

`setup`은 최종 논문의 study가 아니라, 아이디어 정리 단계에서 실제 실험 단계로 넘어가기 위한 준비 폴더입니다.

역할:

- dataset inventory
- target construction
- `Dataset x BFM x Task` master matrix
- statistical floor
- frozen BFM feature extraction/probing
- Horikawa / Emo-FilM first benchmark

구조:

```text
setup/
├── code/
├── data/
├── logs/
└── results/
```

자세한 설명은 `setup/README.md`에 있습니다.

---

## 앞으로 작업은 어떻게 하면 되나?

### 문헌을 더 찾고 싶을 때

사용자 요청:

```text
TRIBE v2랑 affective LLM 쪽 [deep search] 해줘
```

AI가 따라야 할 workflow:

```text
workflows/literature_sota_workflow.md
```

결과는 가능하면 다음에 반영합니다.

- `reference/papers.md`
- `reference/code_resources.md`
- `reference/systematic_reference_map.md`

### 실험 아이디어를 정리하고 싶을 때

사용자 요청:

```text
Horikawa에서 frozen SwiFT baseline 실험 [experiment card] 만들어줘
```

그러면 `templates/experiment_card.md` 형식으로 실험 카드가 만들어져야 합니다.

자동 생성 예시:

```bash
python3 scripts/generate_experiment_cards.py --id NFx-001 --title "Frozen SwiFT Horikawa probe"
```

### 모델 전략을 비판적으로 보고 싶을 때

사용자 요청:

```text
HCP movie pretraining 전략 [red team] 해줘
```

AI가 다음 reviewer 관점으로 공격합니다.

- fMRI methods reviewer
- affective neuroscience reviewer
- ML foundation-model reviewer
- data/compute feasibility reviewer
- skeptical project reviewer

### 프로젝트 상태를 보고 싶을 때

사용자 요청:

```text
NetFeeliX [weekly status] 정리해줘
```

AI가 다음을 확인합니다.

- 최근 git 변경
- 새 문헌/데이터셋
- 결정사항
- 막힌 것
- 다음 3개 action

---

## 지금 당장 해야 할 연구 작업

현재 가장 현실적인 순서는 다음입니다.

1. **Master matrix**
   - `notes/benchmark_design.md`의 `Dataset x BFM x Task` 표 확정
   - 각 cell을 `RUN`, `CHECK`, `NA`로 표시
   - matrix 안의 dataset/BFM/task quick 설명은 `notes/benchmark_design.md`를 봅니다.

2. **Dataset**
   - Horikawa, Emo-FilM, Affective Videos, IAPS fMRI 우선
   - NeuroEmo, Koide-Majima, REELMO / Jojo Rabbit fMRI는 확인 후 확장
   - 각 dataset의 subject, stimulus, target, risk, source는
     `reference/datasets.md`를 봅니다.

3. **BFM**
   - SwiFT, Brain-JEPA, NeuroSTORM, BrainLM
   - 각 BFM의 input format, first checks, risk, source는
     `reference/code_resources.md`와 `reference/papers.md`를 봅니다.

4. **Task**
   - binary, regression, multiclass, multi-label/vector, dynamic/component
   - task 정의와 metric은 `reference/task.md`를 봅니다.

5. **Statistical floor**
   - logistic regression, ridge regression, ROI/voxel ridge

6. **그 이후**
   - SwiFT adapter/fine-tuning
   - HCP/CNeuroMod/StudyForrest/Narratives pretraining
   - stimulus-only video/audio/text control
   - TRIBE/stimulus-brain alignment
   - benchmark 이후 training/adaptation 전략은 `reference/training_strategy.md`를 봅니다.

---

## 핵심만 다시 요약

NetFeeliX는 이제 이렇게 운영됩니다.

```text
ACTION_PLAN.md
    = 지금 해야 할 실행 계획

CONTEXT_NETFEELIX.md
    = 프로젝트 방향 압축본 / agent memory

Paper/
    = 외부 공유 가능한 큰 프레임워크

reference/
    = 논문, dataset, task, training strategy

templates/
    = 새 연구 산출물을 만들 때 쓰는 양식

workflows/
    = AI와 함께 연구를 굴리는 절차

scripts/
    = 문서/상태/실험 카드 자동화만

setup/
    = 첫 실행 묶음: 데이터 확인, target construction, baseline, runnable setup scripts
```

가장 중요한 문장:

> NetFeeliX의 첫 목표는 `Dataset x BFM x Task` master matrix를 채워서, 어떤
> brain foundation model이 어떤 emotion fMRI target에서 실제로 쓸 만한지 확인하는 것입니다.
