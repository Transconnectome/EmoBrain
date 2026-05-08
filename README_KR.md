# NetFeeliX 한국어 가이드

**NetFeeliX**는 감정 이론 프로젝트가 아니라, **SwiFT를 emotion/affect task에 더 잘 맞게 만드는 모델 개발 프로젝트**입니다.

정식 이름은 다음과 같습니다.

```text
Neural nETwork For Emotion rEpresentation Learning and Inference in NeuroX
```

한 줄로 말하면:

> NetFeeliX는 SwiFT를 기본 brain backbone으로 두고, 자연주의적 fMRI, emotion annotation, stimulus model을 이용해 emotion-specific brain representation을 학습하는 프로젝트입니다.

---

## 제일 먼저 보면 되는 파일

처음 들어왔을 때는 아래 순서대로 보면 됩니다.

1. `README_KR.md`
   - 지금 읽는 파일입니다. 전체 구조를 한국어로 설명합니다.
2. `ONBOARDING.md`
   - 새 연구자나 AI agent가 어떤 문서를 읽어야 하는지 정리한 파일입니다.
3. `CONTEXT_NETFEELIX.md`
   - NetFeeliX의 핵심 방향만 압축한 single source of truth입니다.
4. `NARRATIVE_KR.md`
   - NetFeeliX의 전체 연구 내러티브를 한국어로 풀어쓴 문서입니다.
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
SwiFT를 어떻게 emotion-specific brain encoder로 만들 수 있는가?
```

여기서 중요한 점은 세 가지입니다.

### 1. SwiFT-first

SwiFT는 우리 연구실 모델이기 때문에 NetFeeliX의 기본 brain backbone입니다.

단순히 pretrained weight를 가져와서 linear probe만 하는 것이 아니라, 다음을 모두 고려합니다.

- frozen SwiFT feature + linear/ridge/MLP head
- SwiFT adapter tuning
- subject adapter
- affective token
- emotion-specific multi-task head
- HCP movie-watching fMRI continued pretraining
- TRIBE v2 또는 stimulus model과 alignment

### 2. TRIBE v2는 SwiFT 대체제가 아님

TRIBE v2는 fMRI를 입력으로 받는 brain encoder가 아닙니다.

TRIBE v2는:

```text
video/audio/text stimulus -> predicted brain response
```

를 수행하는 **stimulus-to-brain encoding model**입니다.

따라서 NetFeeliX에서는 TRIBE v2를 다음처럼 씁니다.

- stimulus-only baseline
- stimulus-to-brain teacher
- SwiFT latent와 alignment할 대상
- multimodal context feature extractor

즉, TRIBE v2는 SwiFT를 대체하는 모델이 아니라, **SwiFT를 emotion-specific하게 만드는 데 도움을 주는 stimulus-side component**입니다.

### 3. Emotion Foundation Model이라고 바로 주장하지 않음

아직은 "Emotion Foundation Model을 만들었다"고 말하면 과합니다.

지금 단계에서는 더 정확하게 다음처럼 표현합니다.

- emotion-specific brain representation model
- emotion-aware fMRI foundation-model strategy
- SwiFT-based emotion representation learning framework

---

## 전체 폴더 구조

현재 NetFeeliX는 이렇게 구성되어 있습니다.

```text
NetFeeliX/
├── README.md
├── README_KR.md
├── NARRATIVE_KR.md
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

자동화 스크립트가 들어 있습니다.

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
- baseline probes
- frozen SwiFT feature extraction
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

1. **Horikawa**
   - high-dimensional affect geometry task
   - frozen SwiFT + linear/ridge/MLP head

2. **Emo-FilM**
   - naturalistic emotion/component/appraisal target
   - subject adapter, multi-task head 검토

3. **HCP 7T movie**
   - SwiFT continued pretraining
   - masked fMRI, contrastive, JEPA/future latent objective

4. **Affective Videos / IAPS fMRI**
   - valence/arousal/category sanity check

5. **TRIBE v2**
   - stimulus-only baseline
   - predicted brain response teacher
   - SwiFT latent alignment

---

## 핵심만 다시 요약

NetFeeliX는 이제 이렇게 운영됩니다.

```text
ACTION_PLAN.md
    = 지금 해야 할 실행 계획

NARRATIVE_KR.md
    = 전체 연구 내러티브

CONTEXT_NETFEELIX.md
    = 프로젝트 방향 압축본

Paper/
    = 외부 공유 가능한 큰 프레임워크

reference/
    = 논문, dataset, task, training strategy

templates/
    = 새 연구 산출물을 만들 때 쓰는 양식

workflows/
    = AI와 함께 연구를 굴리는 절차

scripts/
    = 문서/상태/실험 카드 자동화

setup/
    = 첫 실행 묶음: 데이터 확인, target construction, baseline
```

가장 중요한 문장:

> NetFeeliX는 SwiFT를 emotion-specific brain representation model로 발전시키기 위한 SwiFT-first model-development project입니다.
