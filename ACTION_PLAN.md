# NetFeeliX 실행 계획

이 문서는 NetFeeliX의 **현재 실행 계획**입니다.

큰 연구 방향은 `Paper/`와 `reference/`에 정리되어 있고, 이 문서는 조금 더 실무적으로
"지금 무엇을 확인하고, 어떤 순서로 실험을 시작할 것인가"를 정리합니다.

## 현재 목표

2개월 안에 완성된 emotion foundation model을 주장하는 것이 목표가 아닙니다.

현재 목표는 다음 질문에 답할 수 있는 실험 기반을 만드는 것입니다.

```text
SwiFT를 emotion-specific brain representation model로 발전시키려면
어떤 데이터셋, 타깃, 학습 전략이 가장 유망한가?
```

즉, 지금은 거대한 모델을 바로 만드는 단계가 아니라,

```text
데이터 확인 → 첫 baseline → SwiFT probe → 모델 수정 방향 결정
```

으로 가야 합니다.

## 실행 원칙

### 1. SwiFT를 기본 brain backbone으로 둔다

NetFeeliX는 SwiFT-first 프로젝트입니다.

처음에는 frozen SwiFT feature와 간단한 head로 시작하되, 결과에 따라 다음 방향으로
확장합니다.

- adapter tuning
- subject adapter
- emotion-specific multi-task head
- affective token / query pooling
- HCP movie-watching fMRI continued pretraining
- stimulus model 또는 TRIBE v2와 alignment

### 2. TRIBE v2는 대체제가 아니라 보조 축이다

TRIBE v2는 fMRI를 입력으로 받는 SwiFT식 brain encoder가 아닙니다.

TRIBE v2는 다음을 위한 component입니다.

- stimulus-only baseline
- stimulus-to-brain teacher
- predicted brain response 생성
- SwiFT latent와 alignment할 stimulus-side representation

따라서 비교 구도는:

```text
SwiFT vs TRIBE v2
```

가 아니라:

```text
brain-only / stimulus-only / brain-stimulus aligned model
```

입니다.

### 3. 작은 실험으로 다음 투자를 결정한다

처음부터 full 4D pretraining이나 복잡한 multimodal model을 만들지 않습니다.

먼저 확인해야 할 것은 다음입니다.

- 데이터가 실제로 접근 가능한가?
- fMRI shape과 timing이 맞는가?
- emotion target matrix를 만들 수 있는가?
- simple baseline이 어느 정도 되는가?
- frozen SwiFT가 simple baseline보다 나은가?

이 결과를 보고 SwiFT adapter, HCP movie pretraining, TRIBE-SwiFT alignment 중 어디에
힘을 줄지 결정합니다.

## 0단계: 프로젝트 운영 기반

상태: 대부분 완료.

| 할 일 | 산출물 | 상태 |
|---|---|---|
| 한국어 안내 문서 작성 | `README_KR.md` | 완료 |
| 프로젝트 방향 압축 문서 작성 | `CONTEXT_NETFEELIX.md` | 완료 |
| 연구 운영 절차 정리 | `workflows/` | 완료 |
| 템플릿 정리 | `templates/` | 완료 |
| 문서 구조 검사 스크립트 작성 | `scripts/check_md_completeness.py` | 완료 |
| 실행 계획 작성 | `ACTION_PLAN.md` | 진행 중 |

검증 명령:

```bash
python3 scripts/check_md_completeness.py
```

## 1단계: 데이터 접근성과 타깃 구성 확인

목표는 실제 실험 가능한 데이터셋과 emotion target matrix를 확보하는 것입니다.

우선 확인할 데이터셋:

1. Horikawa / Cowen emotional video fMRI
2. Emo-FilM
3. HCP Young Adult 7T movie
4. Affective Videos / IAPS fMRI

해야 할 일:

| 할 일 | 산출물 | 저장 위치 |
|---|---|---|
| 데이터 local path 확인 | 데이터 접근성 표 | `setup/data/` |
| fMRI shape / TR / timing 확인 | shape/timing report | `setup/results/` |
| emotion target matrix 생성 | target `.csv` 또는 `.npz` | `setup/data/` |
| train/validation/test split 정의 | split metadata | `setup/data/` |
| 막힌 데이터셋 정리 | blocked resource list | `setup/results/` |

결정 기준:

- Horikawa target이 바로 구성되면 첫 baseline으로 이동합니다.
- Emo-FilM의 timing/annotation 처리가 복잡하면 Horikawa와 Affective Videos를 먼저 진행합니다.
- HCP movie는 emotion label이 없으므로 downstream target이 아니라 pretraining source로 둡니다.

## 2단계: 첫 baseline 만들기

목표는 fMRI와 emotion target 사이에 최소한의 예측 신호가 있는지 확인하는 것입니다.

모델 순서:

1. ROI/parcel ridge baseline
2. dynamic FC baseline
3. frozen SwiFT feature + linear/ridge/MLP head
4. stimulus-only baseline

첫 실험 후보:

| ID | 실험 | 데이터셋 | 모델 | 타깃 |
|---|---|---|---|---|
| NFx-001 | Frozen SwiFT Horikawa probe | Horikawa | SwiFT frozen + head | high-dimensional emotion vector |
| NFx-002 | ROI ridge Horikawa baseline | Horikawa | ROI/parcel ridge | high-dimensional emotion vector |
| NFx-003 | Affective Videos sanity check | ds000205 | ridge / frozen SwiFT | arousal, valence |
| NFx-004 | IAPS beta-map adaptation check | IAPS NeuroVault | beta-map adapter | positive/neutral/negative |

실험 카드 생성 예:

```bash
python3 scripts/generate_experiment_cards.py \
  --id NFx-001 \
  --title "Frozen SwiFT Horikawa probe"
```

## 3단계: SwiFT를 emotion-specific하게 수정하기

목표는 frozen SwiFT가 부족할 경우, 어떤 작은 수정이 효과적인지 확인하는 것입니다.

후보:

- emotion-specific multi-task head
- subject adapter
- adapter tuning
- late-block partial fine-tuning
- affective token / query pooling
- temporal pooling head

결정 기준:

- frozen SwiFT가 simple baseline보다 좋으면 adapter와 emotion head를 확장합니다.
- frozen SwiFT가 simple baseline보다 나쁘면 preprocessing, target timing, feature extraction을 먼저 점검합니다.
- arousal만 안정적으로 예측되면 dynamic/physiology-aware objective를 우선합니다.

## 4단계: HCP movie로 continued pretraining 하기

목표는 SwiFT를 resting-state/general fMRI에서 naturalistic movie fMRI 쪽으로 이동시키는 것입니다.

후보 학습 목표:

- masked fMRI modeling
- temporal contrastive learning
- JEPA-style future latent prediction
- subject-invariant learning
- stimulus-conditioned prediction

시작 방식:

1. parcel-level 또는 ROI-level temporal model로 작게 시작합니다.
2. transfer target은 Horikawa와 Emo-FilM으로 둡니다.
3. transfer improvement가 보이면 4D SwiFT continued pretraining으로 확장합니다.

## 5단계: TRIBE v2 + SwiFT alignment

목표는 stimulus context가 emotion representation에 얼마나 중요한지 확인하는 것입니다.

비교 조건:

| 조건 | Brain input | Stimulus input | 목적 |
|---|---|---|---|
| brain-only | observed fMRI | 없음 | SwiFT emotion decoding |
| stimulus-only | 없음 | video/audio/text | label이 stimulus만으로 설명되는지 확인 |
| TRIBE teacher | 없음 | TRIBE-predicted brain | stimulus-to-brain prior 확인 |
| aligned | observed fMRI | stimulus latent | brain-stimulus-emotion shared latent |

가능한 loss:

- regression alignment
- contrastive matching
- CKA/RSA geometry alignment
- retrieval loss
- optional fMRI encoding loss

## 6단계: context / affective LLM-VLM 확장

목표는 emotion label이 단순 category가 아니라 context와 rationale을 포함할 때 brain
representation이 어떻게 바뀌는지 확인하는 것입니다.

사용 가능 source:

- Emo-FilM component/appraisal annotations
- REELMO affect trajectories
- MLLM-derived captions, cue labels, rationale embeddings

주의:

- Horikawa를 reasoning dataset으로 쓰지 않습니다.
- 이 단계는 first baseline 이후에 진행합니다.

## 지금 가장 중요한 다음 5개 작업

1. Horikawa local data path와 target format 확인
2. Emo-FilM access, timing, annotation format 확인
3. HCP 7T movie 접근 가능 여부와 preprocessing format 확인
4. `setup`에 dataset availability report 생성
5. NFx-001, NFx-002 experiment card 작성

## 자동화 명령

문서 구조 검사:

```bash
python3 scripts/check_md_completeness.py
```

프로젝트 상태 보고서 생성:

```bash
python3 scripts/build_project_status.py
```

실험 카드 생성:

```bash
python3 scripts/generate_experiment_cards.py --id NFx-001 --title "Frozen SwiFT Horikawa probe"
```

## `setup`은 무엇인가?

`setup`은 첫 번째 논문이나 최종 study라는 뜻이 아닙니다.

지금 단계에서 필요한 **첫 실행 묶음**입니다.

`setup`의 역할:

- dataset availability 확인
- target construction
- first baselines
- frozen SwiFT probe
- Horikawa / Emo-FilM / Affective Videos / IAPS의 최소 실행 가능성 확인

즉 `setup`은:

```text
아이디어 정리 단계에서 실제 실험 단계로 넘어가기 위한 첫 작업 공간
```

입니다.

나중에 실험이 커지면 목적별 폴더로 나눌 수 있습니다.

| 폴더 | 역할 |
|---|---|
| `setup/` | data inventory, target construction, first baselines |
| `hcp_pretraining/` | HCP movie continued pretraining |
| `swift_adaptation/` | emotion downstream fine-tuning |
| `tribe_alignment/` | TRIBE-SwiFT alignment |
| `affective_llm_vlm/` | affective LLM/VLM brain-tuning extension |
