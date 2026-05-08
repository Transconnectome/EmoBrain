# NetFeeliX 연구 내러티브

이 문서는 NetFeeliX의 전체 연구 내러티브를 한국어로 설명합니다.

`Paper/framework_KR.md`가 연구 프레임워크와 방법론을 정리한 문서라면, 이 문서는
"왜 이 프로젝트가 필요한가", "왜 SwiFT-first인가", "왜 TRIBE v2와 HCP movie가
나오는가", "결국 어떤 모델 개발로 이어지는가"를 하나의 흐름으로 설명합니다.

## 1. 출발점: 감정 예측 문제가 아니라 representation 문제다

NetFeeliX의 출발점은 단순한 emotion prediction이 아닙니다.

물론 최종적으로는 fMRI로부터 arousal, valence, discrete emotion, high-dimensional
emotion vector, appraisal/component target을 예측해야 합니다. 하지만 이 프로젝트의
핵심 질문은 "어떤 classifier가 emotion label을 가장 잘 맞히는가?"가 아닙니다.

핵심 질문은 다음입니다.

```text
fMRI brain dynamics에서 emotion-relevant representation을 더 잘 학습하려면
어떤 모델 구조와 학습 전략이 필요한가?
```

이 차이가 중요합니다.

작은 emotion fMRI dataset에 단순 classifier를 붙이면 어떤 score는 얻을 수 있습니다.
하지만 그렇게 얻은 score가 정말 emotion-specific brain representation을 의미하는지,
혹은 stimulus identity, subject effect, preprocessing artifact, low-level arousal만 잡은
것인지는 불분명합니다.

따라서 NetFeeliX는 "emotion label을 맞히는 모델"이 아니라,

```text
brain dynamics + naturalistic stimulus dynamics + affective annotation
```

이 세 가지가 만나는 지점에서 emotion representation을 학습하는 모델을 개발하려는
프로젝트입니다.

## 2. 기존 brain foundation model만으로는 부족할 수 있다

최근 fMRI와 neural signal 분야에서도 foundation model 흐름이 생기고 있습니다.
SwiFT, BrainLM, Brain-JEPA, NeuroSTORM, Omni-fMRI 같은 모델들은 대규모 brain
activity에서 transferable representation을 학습하려고 합니다.

이 흐름은 NetFeeliX의 중요한 출발점입니다.

하지만 기존 brain foundation model에는 한계가 있습니다.

첫째, 많은 모델은 resting-state 또는 general task distribution에서 학습됩니다. 감정은
자연주의적 stimulus, 시간적 맥락, subject-specific response, appraisal, bodily response와
강하게 얽혀 있는데, generic fMRI pretraining만으로 이 구조가 충분히 학습되었는지는
확실하지 않습니다.

둘째, 기존 brain foundation model은 emotion을 중심 목표로 설계된 경우가 드뭅니다.
Emotion task는 downstream benchmark 중 하나로 들어갈 수는 있지만, emotion-specific
representation을 만들기 위한 architecture나 objective가 명시적으로 설계된 것은 아닙니다.

셋째, fMRI emotion dataset은 대부분 작고 이질적입니다. Horikawa, Emo-FilM, Affective
Videos, IAPS fMRI, NeuroEmo 등은 stimulus, target, timing, preprocessing 방식이 다릅니다.
따라서 하나의 dataset에서 높은 score가 나와도 그것이 일반화 가능한 emotion
representation인지 판단하기 어렵습니다.

그래서 NetFeeliX는 기존 brain foundation model을 그대로 가져와서 "성능 비교"만 하지
않습니다. 기존 모델을 출발점으로 삼되, 그 한계를 확인하고, 필요하면 emotion-specific
하게 수정하는 방향으로 갑니다.

## 3. 왜 SwiFT-first인가

NetFeeliX의 기본 brain backbone은 SwiFT입니다.

그 이유는 단순히 이미 존재하는 모델이라서가 아닙니다. SwiFT는 4D fMRI를 직접 다루는
spatiotemporal transformer 계열 모델이고, NetFeeliX가 관심 있는 naturalistic fMRI와
emotion dynamics를 다루기 위한 출발점으로 적합합니다.

SwiFT-first라는 말은 다음을 뜻합니다.

```text
SwiFT를 baseline으로만 쓰지 않고,
emotion-specific brain encoder로 발전시키는 방향을 먼저 탐색한다.
```

구체적으로는 다음 가능성을 봅니다.

- frozen SwiFT feature에 linear/ridge/MLP emotion head를 붙이는 것
- emotion-specific multi-task head를 붙이는 것
- subject adapter를 넣는 것
- affective token 또는 query pooling을 추가하는 것
- late block 또는 adapter만 fine-tuning하는 것
- HCP movie-watching fMRI로 continued pretraining하는 것
- stimulus model과 SwiFT latent를 alignment하는 것

즉 NetFeeliX는 "SwiFT weight를 가져와서 한번 돌려보자"가 아닙니다.

더 정확한 내러티브는:

```text
SwiFT를 emotion-specific naturalistic fMRI encoder로 키울 수 있는가?
```

입니다.

## 4. 왜 HCP movie pretraining이 필요한가

Emotion은 정적인 label 하나로 끝나지 않습니다. 자연주의적 영화나 영상에서 감정은
시간 속에서 전개됩니다. 장면, 얼굴, 목소리, 음악, 대사, 맥락, 예측, 기억이 함께 작동합니다.

하지만 emotion-labeled fMRI dataset은 규모가 작습니다. Horikawa는 high-dimensional
emotion geometry를 볼 수 있지만 short video 중심이고, Emo-FilM은 매우 유용하지만 규모가
충분히 크지는 않습니다. 이런 dataset만으로 4D fMRI model을 크게 학습하는 것은 위험합니다.

그래서 HCP Young Adult 7T movie-watching fMRI가 중요합니다.

HCP movie는 직접적인 emotion label은 없지만, 자연주의적 movie-watching fMRI를 제공합니다.
즉, emotion downstream task에 바로 쓰는 데이터가 아니라,

```text
SwiFT를 naturalistic fMRI dynamics에 적응시키기 위한 pretraining source
```

입니다.

여기서 할 수 있는 학습은 다음과 같습니다.

- masked fMRI segment modeling
- temporal contrastive learning
- JEPA-style future latent prediction
- subject-invariant representation learning
- stimulus-conditioned fMRI prediction

핵심은 HCP movie pretraining이 Horikawa나 Emo-FilM으로 전이되는지를 보는 것입니다.

만약 HCP movie-pretrained SwiFT가 generic SwiFT보다 emotion downstream에서 좋아진다면,
NetFeeliX는 자연주의적 fMRI pretraining이 emotion representation에 중요하다는 근거를
얻습니다.

반대로 이득이 없다면, 무작정 큰 pretraining을 밀기보다 target design, subject adaptation,
stimulus alignment 쪽으로 방향을 바꿔야 합니다.

## 5. 왜 TRIBE v2가 필요한가

TRIBE v2는 SwiFT와 같은 종류의 모델이 아닙니다.

SwiFT는 fMRI를 입력으로 받아 brain representation을 만드는 모델입니다.

반면 TRIBE v2는 video, audio, text 같은 stimulus feature를 입력으로 받아 brain response를
예측하는 stimulus-to-brain encoding model입니다.

따라서 NetFeeliX에서 TRIBE v2는 SwiFT의 대체제가 아닙니다.

TRIBE v2는 다음 질문을 던지기 위해 필요합니다.

```text
emotion label은 fMRI에서만 예측되는가,
아니면 stimulus context만으로도 상당 부분 설명되는가?
```

이 질문은 매우 중요합니다.

예를 들어 어떤 emotion target이 stimulus-only model로도 잘 예측된다면, brain model이 높은
성능을 내더라도 그것이 brain-specific emotion representation인지 조심스럽게 해석해야 합니다.

반대로 brain-only model이 stimulus-only model보다 특정 target에서 더 강하거나, brain-stimulus
alignment가 high-dimensional emotion vector에서 이득을 준다면, fMRI가 단순 stimulus feature를
넘어서는 emotion-relevant 정보를 제공한다고 볼 수 있습니다.

그래서 NetFeeliX의 비교 구도는 다음과 같습니다.

| 조건 | 의미 |
|---|---|
| brain-only | fMRI만으로 emotion target 예측 |
| stimulus-only | video/audio/text만으로 emotion target 예측 |
| TRIBE teacher | stimulus로부터 예측된 brain response를 teacher로 사용 |
| aligned model | SwiFT brain latent와 stimulus latent를 shared space에서 정렬 |

이렇게 하면 TRIBE v2와 SwiFT를 억지로 같은 모델로 비교하지 않으면서도, 공통 downstream
emotion target에서 의미 있는 비교를 할 수 있습니다.

## 6. 데이터셋은 역할별로 다르게 쓴다

NetFeeliX의 데이터셋은 단순 우선순위 목록이 아닙니다. 각 데이터셋은 서로 다른 역할을
합니다.

### Horikawa / Cowen emotional video fMRI

Horikawa는 reasoning dataset이 아닙니다.

NetFeeliX에서 Horikawa의 역할은:

```text
high-dimensional affect geometry를 brain representation이 잡는지 보는 핵심 downstream task
```

입니다.

짧은 emotional video에 대한 fMRI response와 rich emotion category rating이 있으므로,
SwiFT가 단순 arousal이 아니라 더 복잡한 emotion geometry를 잡는지 확인하는 데 적합합니다.

### Emo-FilM

Emo-FilM은 naturalistic film context, fMRI, physiology, emotion/component/appraisal annotation이
함께 있는 중요한 데이터셋입니다.

NetFeeliX에서 Emo-FilM은:

```text
naturalistic emotion dynamics와 appraisal/component target을 평가하는 dataset
```

입니다.

Horikawa가 affect geometry라면, Emo-FilM은 naturalistic affective process와 component-level
target을 보는 역할입니다.

### HCP 7T movie

HCP movie는 emotion label이 없는 pretraining source입니다.

역할은:

```text
SwiFT를 movie-evoked naturalistic fMRI dynamics에 적응시키는 것
```

입니다.

### Affective Videos / IAPS fMRI

이들은 빠른 sanity check용입니다.

역할은:

- arousal/valence가 어느 정도 예측되는지 확인
- positive/neutral/negative beta-map adaptation이 가능한지 확인
- preprocessing과 target construction이 정상적으로 작동하는지 확인

### REELMO, NSD, OASIS

이들은 core fMRI emotion downstream이라기보다는 확장 축입니다.

- REELMO: long-context affect trajectory와 rationale/cue target
- NSD: large static-image fMRI representation
- OASIS: image affect label calibration

즉, 처음부터 모두 다 하려는 것이 아니라, core baseline 결과에 따라 필요한 방향으로 붙입니다.

## 7. 첫 실행은 `setup`에서 시작한다

NetFeeliX에는 `setup/` 폴더가 있습니다.

이 폴더는 최종 논문의 study가 아닙니다. 이름 그대로 setup입니다.

역할은 다음입니다.

```text
데이터 접근성 확인
target matrix 구성
split 정의
simple baseline
frozen SwiFT probe
막힌 resource 정리
```

이 단계에서 대답해야 하는 질문은 명확합니다.

1. 어떤 데이터셋이 실제로 지금 실행 가능한가?
2. 어떤 emotion target이 깨끗하게 구성되는가?
3. simple baseline은 어느 정도 되는가?
4. frozen SwiFT는 simple baseline보다 나은가?
5. 다음 투자는 SwiFT adaptation인가, HCP movie pretraining인가, TRIBE-SwiFT alignment인가?

따라서 `setup`은 작은 단계가 아니라, 프로젝트의 방향을 결정하는 중요한 단계입니다.

## 8. 모델 개발은 단계적으로 간다

NetFeeliX의 모델 개발은 다음 순서로 진행됩니다.

### 1단계: simple baseline

ROI/parcel ridge, dynamic FC, simple MLP 같은 baseline을 먼저 봅니다.

이 단계는 화려하지 않지만 중요합니다. Simple baseline이 어느 정도 되는지 알아야 SwiFT나
alignment model의 의미를 해석할 수 있습니다.

### 2단계: frozen SwiFT probe

기존 SwiFT representation에 emotion head를 붙입니다.

이 단계에서 보는 것은:

```text
generic SwiFT feature 안에 emotion-relevant structure가 이미 있는가?
```

입니다.

### 3단계: SwiFT emotion adaptation

Frozen SwiFT가 일부 신호를 잡지만 충분하지 않다면, adapter, subject module,
emotion-specific head, affective token 같은 작은 수정을 시도합니다.

### 4단계: HCP movie continued pretraining

Naturalistic movie fMRI pretraining이 emotion transfer를 개선하는지 봅니다.

이 단계는 compute가 크기 때문에, 작은 parcel-level 실험에서 신호가 보일 때 확장합니다.

### 5단계: TRIBE-SwiFT alignment

Stimulus latent와 fMRI latent를 정렬합니다.

이 단계의 목표는:

```text
emotion representation이 brain dynamics와 stimulus context의 shared latent에서 더 잘 학습되는가?
```

를 확인하는 것입니다.

### 6단계: affective LLM/VLM 확장

마지막으로 emotion caption, rationale, cue grounding, appraisal embedding 같은 richer target을
사용해 brain representation을 정렬합니다.

이 단계는 처음부터 주장하지 않고, baseline과 alignment 결과가 유망할 때 진행합니다.

## 9. NetFeeliX가 만들고 싶은 결과

NetFeeliX의 결과는 하나의 최종 모델만이 아닐 수 있습니다.

오히려 중요한 결과는 다음입니다.

1. 어떤 emotion target이 fMRI에서 안정적으로 예측되는가?
2. 기존 SwiFT representation은 어디까지 전이되는가?
3. HCP movie pretraining은 실제로 도움이 되는가?
4. Stimulus-only model이 너무 강한 target은 무엇인가?
5. Brain-stimulus alignment가 필요한 target은 무엇인가?
6. 어떤 모델 수정이 sample-efficient한가?

즉, NetFeeliX는 단순히 "모델 하나 만들기"가 아니라,

```text
emotion-specific fMRI representation learning을 위한 모델 개발 지도 만들기
```

에 가깝습니다.

## 10. 한 문장 내러티브

NetFeeliX의 전체 내러티브를 한 문장으로 줄이면 다음입니다.

> NetFeeliX는 SwiFT를 기본 brain backbone으로 두고, Horikawa와 Emo-FilM 같은
> emotion-labeled fMRI, HCP movie-watching fMRI pretraining, TRIBE v2-style
> stimulus-to-brain alignment를 단계적으로 결합해, naturalistic fMRI에서
> emotion-specific brain representation을 더 잘 학습하는 모델 개발 전략을 찾는
> 프로젝트입니다.

## 아주 짧은 버전

```text
SwiFT를 emotion-specific brain encoder로 키운다.
HCP movie로 naturalistic fMRI pretraining을 확인한다.
TRIBE v2는 stimulus-side teacher/alignment component로 쓴다.
Horikawa와 Emo-FilM으로 emotion representation transfer를 평가한다.
결과에 따라 adapter, pretraining, alignment 중 어느 모델 개발 방향을 밀지 결정한다.
```
