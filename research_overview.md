# NetFeeliX: Research Overview for Abstract & Presentation

> **목적**: 팀 공유용 연구 overview → abstract / presentation / experiment planning의 기반 문서
> **형식**: Background → Rationale → Gap → Research Question → Methods → Expected Results → Future
> **GitHub**: https://github.com/Transconnectome/NetFeeliX  
> **last-synced**: 2026-05-08
> **canonical docs**: `Paper/framework_KR.md`, `Paper/framework_EN.md`, `reference/datasets.md`, `reference/task.md`, `reference/training_strategy.md`

---

## 0. One-Sentence Summary

**NetFeeliX**는 SwiFT를 기본 brain backbone으로 두고, emotion-labeled fMRI,
naturalistic movie/story fMRI pretraining, TRIBE v2-style stimulus-to-brain
alignment, affective LLM/VLM representation을 결합해 **emotion-specific brain
representation을 더 잘 학습하는 모델 개발 전략**을 찾는 프로젝트이다.

정식 이름:

```text
Neural nETwork For Emotion rEpresentation Learning and Inference in NeuroX
```

핵심 질문:

```text
SwiFT를 emotion-specific fMRI representation model로 발전시키려면,
어떤 dataset, target, training objective, architecture modification,
stimulus-brain alignment 전략이 필요한가?
```

현재 목표는 완성형 "Emotion Foundation Model"을 바로 주장하는 것이 아니다.
현재 목표는 **2개월 안에 model-development decision을 내릴 수 있는 benchmark와
실험 기반을 구축하는 것**이다.

---

## 1. Background & Significance

### 1.1 Brain Foundation Models의 등장

최근 fMRI와 neural signal 분야에서도 foundation model 흐름이 빠르게 생기고 있다.
SwiFT, BrainLM, Brain-JEPA, NeuroSTORM, Omni-fMRI, Brain-OF, Brain-DiT 계열은
대규모 brain activity에서 transferable representation을 학습하려는 모델들이다.

| Model family | 예시 | 입력 | 핵심 아이디어 | NetFeeliX에서의 역할 |
|---|---|---|---|---|
| 4D fMRI backbone | SwiFT | 4D fMRI volume | spatiotemporal window attention | 기본 brain backbone |
| fMRI masked modeling | BrainLM | ROI/time-series fMRI | masked brain activity prediction | BFM transfer baseline |
| JEPA-style BFM | Brain-JEPA | fMRI time series | latent prediction / spatiotemporal masking | objective precedent |
| Large-scale 4D fMRI FM | NeuroSTORM | raw 4D fMRI | large-scale fMRI representation | 비교 모델 후보 |
| Rest-to-task bridge | SwiFUN | resting fMRI | task activation prediction | emotion-related task contrast 참고 |
| Omnifunctional neural FM | Brain-OF / Omni-fMRI | fMRI/EEG/MEG or atlas-free fMRI | multi-task neural representation | future reference |

이 흐름은 NetFeeliX의 중요한 출발점이다. 하지만 대부분의 BFM은 emotion을 중심으로
설계된 모델이 아니다. Emotion task가 downstream benchmark 중 하나로 포함될 수는
있지만, emotion-specific representation을 잘 만들기 위한 objective나 architecture가
명시적으로 설계된 경우는 드물다.

### 1.2 왜 Emotion은 단순 Label Prediction 문제가 아닌가

많은 machine learning task에서는 emotion을 다음처럼 다룬다.

```text
image/video/audio/text/fMRI -> anger / fear / joy / sadness / neutral
```

이 접근은 필요하지만 충분하지 않다. Emotion은 다음 요소들이 동시에 얽혀 있다.

- **Dimensional**: arousal, valence, dominance, intensity
- **Categorical**: fear, joy, sadness, anger, disgust, awe 등
- **Multi-label**: 여러 감정이 동시에 존재 가능
- **Dynamic**: 영화나 이야기 속에서 시간에 따라 변화
- **Componential**: appraisal, motivation, expression, physiology, feeling
- **Context-dependent**: 같은 얼굴/장면도 서사 맥락에 따라 달라짐
- **Stimulus-dependent**: visual, auditory, language, social cue가 함께 작동
- **Subject-dependent**: 같은 stimulus라도 개인마다 반응이 다름

따라서 NetFeeliX의 질문은 단순히:

```text
fMRI로 emotion label을 맞힐 수 있는가?
```

가 아니다.

더 정확한 질문은:

```text
fMRI brain dynamics에서 emotion-relevant representation을 더 잘 학습하려면
어떤 모델 구조와 학습 전략이 필요한가?
```

이다.

### 1.3 Affective Computing의 Task 변화

Affective computing에서도 emotion task는 단순 classification에서 점점 확장되고 있다.
최근 LLM/VLM/MLLM 기반 affective computing은 emotion recognition뿐 아니라 emotion
reasoning, cue grounding, cause/trigger inference, affective captioning, multimodal
emotion understanding까지 다룬다.

| Task type | Output | 대표 metric | NetFeeliX에서의 의미 |
|---|---|---|---|
| Sentiment / valence classification | positive / neutral / negative | accuracy, macro F1 | IAPS/Affective Videos식 낮은 난이도 check |
| Discrete emotion classification | anger, fear, joy 등 single label | balanced accuracy, macro F1 | baseline task |
| Multi-label emotion prediction | 여러 emotion label 또는 probability vector | macro/micro F1, AUROC | Horikawa-style high-dimensional target과 가까움 |
| Dimensional affect regression | arousal, valence, dominance, intensity | Pearson r, Spearman r, CCC, MAE/MSE | fMRI에서 가장 먼저 확인할 sanity ladder |
| Continuous affect tracking | window/frame-level affect trajectory | CCC, time-lagged correlation | Emo-FilM / REELMO / movie-window 설계와 연결 |
| Emotion in conversation | utterance-level emotion + speaker/context | macro F1 | context modeling precedent |
| Multimodal emotion recognition | video/audio/text/physiology -> emotion | task-specific F1/correlation | stimulus-only baseline과 alignment 필요성 |
| Emotion cause / trigger reasoning | cue, cause, intent, appraisal, rationale | QA, retrieval, human/LLM judge | stimulus-side auxiliary target |
| Affective captioning / QA | natural-language emotion description | caption metric, LLM judge, retrieval | fMRI latent와 embedding alignment target |

NetFeeliX는 이 task ladder를 fMRI-compatible하게 번역해야 한다.

첫 단계에서는 측정 가능한 regression/classification/multi-label task를 사용한다. 이후에는
MLLM-derived caption, rationale, cue embedding을 stimulus-side auxiliary target으로 사용한다.
단, fMRI가 직접 natural-language reasoning을 한다고 주장하지 않는다.

### 1.4 왜 SwiFT-first인가

NetFeeliX의 기본 brain backbone은 SwiFT다.

이유는 두 가지다.

첫째, SwiFT는 local lab backbone이므로 가장 적극적으로 수정할 수 있다. Frozen feature를
뽑는 데서 끝나는 것이 아니라, emotion-specific head, subject adapter, affective token,
continued pretraining, stimulus-brain alignment module까지 실질적으로 개발할 수 있다.

둘째, SwiFT는 4D fMRI를 직접 다루는 spatiotemporal transformer 계열이다. Emotion은
자연주의적 stimulus, time-varying context, subject-specific response와 연결되어 있으므로,
4D fMRI encoder를 emotion-specific하게 발전시키는 질문이 NetFeeliX의 중심이 된다.

SwiFT-first의 의미:

```text
SwiFT를 단순 baseline으로만 쓰지 않고,
emotion-specific naturalistic fMRI encoder로 발전시키는 방향을 먼저 탐색한다.
```

---

## 2. Rationale

### 2.1 핵심 테제

NetFeeliX의 핵심 테제는 다음이다.

> **Emotion fMRI modeling은 단순 emotion label prediction이 아니라, brain dynamics,
> naturalistic stimulus dynamics, affective annotation이 만나는 representation learning
> 문제이다.**

작은 emotion fMRI dataset에 classifier를 붙이면 점수는 얻을 수 있다. 그러나 그 점수가
정말 emotion-specific brain representation을 의미하는지는 불분명하다. 높은 성능은 다음
shortcut에서 나올 수 있다.

- stimulus identity
- subject identity
- low-level visual motion
- luminance / scene cut
- audio energy / speech onset
- generic arousal / attention
- HRF timing artifact
- preprocessing artifact
- label imbalance

따라서 NetFeeliX는 단일 score가 아니라 다음 증거를 함께 봐야 한다.

1. simple ROI/ridge baseline 대비 개선
2. frozen SwiFT 대비 adapter/fine-tuning 개선
3. stimulus-only baseline 대비 brain-specific signal
4. arousal뿐 아니라 valence, multi-label, high-dimensional target 성능
5. representation geometry와 emotion rating geometry의 정렬
6. subject/stimulus split에서의 일반화
7. cross-dataset transfer
8. low-level visual/audio shortcut control

### 2.2 Four-Axis NetFeeliX Framework

NetFeeliX는 네 개의 축으로 정리할 수 있다.

```text
Axis 1: Brain backbone
    SwiFT / BrainLM / Brain-JEPA / NeuroSTORM / other BFMs

Axis 2: Naturalistic fMRI pretraining
    resting/generic BFM -> movie/story stimulus-locked fMRI representation

Axis 3: Stimulus-brain alignment
    video/audio/text stimulus -> brain response -> shared emotion latent

Axis 4: Affective AI target richness
    label -> intensity -> distribution -> trajectory -> cue/rationale/caption embedding
```

이 네 축의 조합이 NetFeeliX의 모델 개발 공간이다.

### 2.3 왜 Naturalistic Movie/Story fMRI인가

Naturalistic movie/story fMRI를 쓰는 이유는 단순히 "movie가 resting-state보다 더
현실적이다"가 아니다. 그 말은 너무 약하다.

정확한 가설은:

```text
작은 emotion-labeled fMRI dataset으로 바로 fine-tuning하기 전에,
SwiFT가 visual, auditory, language, social, narrative cue에 의해 유도되는
stimulus-locked brain dynamics를 먼저 학습해야 하는가?
```

Resting-state fMRI는 intrinsic connectivity, subject trait, baseline network structure를
학습하는 데 유리하다. 하지만 emotion during naturalistic experience는 외부 stimulus가
시간 속에서 펼쳐질 때 만들어진다.

Movie/story fMRI는 다음 정보를 제공한다.

- face / body motion
- scene transition
- visual saliency
- voice / speech onset
- music / auditory intensity
- semantic context
- social interaction
- narrative buildup
- expectation / surprise
- emotional arc

따라서 naturalistic pretraining은 emotion label이 많아서 쓰는 것이 아니라, emotion target을
만드는 stimulus-evoked brain dynamics를 미리 학습하기 위해 사용한다.

### 2.4 HCP는 첫 후보이지 전체 전략이 아니다

HCP Young Adult 7T movie는 scale, 표준화, 7T quality, resting/movie가 함께 있는 구조 때문에
첫 continued-pretraining 후보가 될 수 있다. 하지만 HCP 하나로 모든 naturalistic
pretraining 논리를 정당화할 수는 없다.

Dataset 선택은 model hypothesis별로 해야 한다.

| Dataset / source | 왜 쓰는가 | NetFeeliX에서 확인할 질문 |
|---|---|---|
| HCP 7T movie | large-subject movie fMRI | stimulus-locked pretraining이 Horikawa/Emo-FilM transfer를 개선하는가 |
| CNeuroMod / Algonauts 2025 | video/audio/transcript + fMRI encoding resource | TRIBE-style alignment가 emotion target에 도움이 되는가 |
| StudyForrest | long coherent film | long-film continuity가 temporal representation에 도움이 되는가 |
| Narratives | spoken story + transcript | visual cue 없이 language/narrative context를 align할 수 있는가 |
| 101 Dalmatians | audiovisual/auditory/visual conditions | modality별 contribution을 분리할 수 있는가 |
| Emo-FilM | fMRI + emotion/component annotation | naturalistic pretraining의 downstream validation |
| REELMO | long affect trajectories | stimulus-side affect trajectory / rationale target |

### 2.5 Naturalistic Pretraining의 위험

Movie/story pretraining은 강력하지만 위험하다. 모델이 emotion representation을 배운 것이
아니라 다음 shortcut을 배울 수 있다.

- low-level visual motion
- luminance
- scene cut
- face/object category
- auditory energy
- speech onset
- music intensity
- stimulus identity
- subject synchronization
- generic arousal

그래서 모든 naturalistic pretraining은 반드시 control을 포함해야 한다.

| Control | 의미 |
|---|---|
| resting/generic SwiFT vs naturalistic-pretrained SwiFT | naturalistic fMRI가 transfer value를 주는지 |
| low-level visual/audio feature control | motion/luminance/audio shortcut인지 |
| vision-only/audio-only/text-only ablation | 어떤 modality가 transfer를 담당하는지 |
| stimulus-only baseline | label이 stimulus만으로 설명되는지 |
| arousal-only vs high-dimensional target | 단순 arousal 개선인지 rich emotion representation인지 |
| Horikawa vs Emo-FilM transfer | short video geometry와 film component target 모두에 통하는지 |

### 2.6 왜 TRIBE v2인가

TRIBE v2는 SwiFT의 대체제가 아니다.

Native direction은 다르다.

```text
SwiFT:
    observed fMRI -> brain latent -> emotion

TRIBE v2:
    video/audio/language stimulus -> predicted brain response
```

즉 TRIBE v2는 fMRI encoder가 아니라 **stimulus-to-brain encoding model**이다. 그러나 바로
그 점 때문에 NetFeeliX에 중요하다.

TRIBE v2가 던지는 질문:

```text
emotion target은 observed fMRI에서만 예측되는가,
아니면 video/audio/text stimulus context만으로도 상당 부분 설명되는가?
```

TRIBE v2 활용 방식:

| Use mode | Input | Output | NetFeeliX role |
|---|---|---|---|
| stimulus-only baseline | video/audio/text | emotion target | label이 stimulus만으로 설명되는지 확인 |
| frozen teacher | video/audio/text | predicted brain response | stimulus-to-brain prior |
| teacher distillation | TRIBE-predicted brain latent/map | SwiFT latent target | stimulus-brain structure를 SwiFT에 전달 |
| dual encoder | stimulus latent + fMRI latent | shared latent | brain-stimulus-emotion representation |
| auxiliary encoding loss | stimulus feature | fMRI response | emotion training regularization |

### 2.7 왜 Affective LLM/VLM인가

Affective computing의 최근 흐름은 label prediction을 넘어 cue grounding, emotion
captioning, cause/trigger reasoning, multimodal emotional intelligence benchmark로 이동하고
있다.

NetFeeliX가 이 흐름에서 배울 점:

- emotion target을 단순 category로만 두지 않는다.
- stimulus-side affect representation을 더 풍부하게 만든다.
- caption/rationale/cue embedding을 fMRI latent와 align할 수 있다.
- brain response를 affective AI representation의 biological alignment signal로 사용할 수 있다.

단, 주장은 조심해야 한다.

가능한 주장:

```text
fMRI response can regularize or evaluate affective stimulus representations.
```

아직 피해야 할 주장:

```text
fMRI directly performs natural-language emotional reasoning.
```

---

## 3. Gap in the Literature

### Gap 1. Existing fMRI BFMs are generic, not emotion-organized

SwiFT, BrainLM, Brain-JEPA, NeuroSTORM 등은 brain-side foundation model space를 만든다.
그러나 대부분의 pretraining objective는 emotion-specific하지 않다. Emotion은 downstream
task로 포함될 수 있지만, emotion representation을 중심으로 architecture와 objective를
설계한 경우는 드물다.

NetFeeliX gap:

```text
SwiFT-style fMRI encoder를 emotion-specific하게 발전시키는
model-development framework가 부족하다.
```

### Gap 2. Affective computing foundation models lack brain grounding

Affective computing에서는 LLM/VLM/MLLM 기반 emotion recognition, reasoning, captioning,
benchmark가 빠르게 늘고 있다. 그러나 이 모델들은 보통 external label, human judgment,
stimulus-only benchmark로 평가된다. Emotional stimulus에 대한 fMRI response와 직접 연결되는
경우는 드물다.

NetFeeliX gap:

```text
Can brain responses provide biological grounding for affective AI representations?
```

### Gap 3. Stimulus-to-brain models optimize encoding, not emotion representation

TRIBE, TRIBE v2, VIBE, Algonauts-style models는 naturalistic stimulus로 fMRI response를
예측한다. 하지만 native objective는 fMRI encoding이지 emotion representation learning이
아니다.

NetFeeliX gap:

```text
Can stimulus-to-brain encoding models be modified into
emotion-representation components?
```

### Gap 4. Emotion fMRI datasets are small and heterogeneous

Emotion fMRI dataset은 매우 가치 있지만 규모와 형식이 제각각이다.

| Dataset | 강점 | 한계 |
|---|---|---|
| Horikawa / Cowen | high-dimensional emotion geometry | short video, small fMRI N |
| Emo-FilM | film context + component/appraisal annotation | limited fMRI N, timing/annotation complexity |
| Affective Videos | arousal/valence quick check | small N, short clips |
| IAPS fMRI | positive/neutral/negative beta maps | not raw 4D time series |
| NeuroEmo | cross-cultural emotion clips | label mapping and stimulus access 확인 필요 |
| Koide-Majima / Nishimoto | emotional movie fMRI candidate | access-dependent |

NetFeeliX gap:

```text
작은 dataset 하나에 end-to-end model을 바로 학습하기보다,
dataset/model/task를 공정하게 비교하는 benchmark surface가 먼저 필요하다.
```

### Gap 5. Emotion task design is often too narrow

Emotion을 single-label classification으로만 보면 다음 구조를 놓친다.

- intensity
- mixed emotion
- high-dimensional affect geometry
- component/appraisal structure
- continuous trajectory
- stimulus cue / cause / rationale

NetFeeliX gap:

```text
Emotion fMRI modeling에는 single target이 아니라 task ladder가 필요하다.
```

---

## 4. Research Question

### 4.1 Main Question

```text
Which model architecture and learning objective best support transferable
emotion representation learning from fMRI?
```

한국어로 풀면:

```text
작은 emotion fMRI dataset 조건에서,
어떤 model architecture와 training objective가
가장 transferable한 emotion-relevant brain representation을 만드는가?
```

### 4.2 Sub-Questions

1. **BFM transfer**
   - 기존 SwiFT/BFM representation이 emotion target으로 전이되는가?
   - Simple ROI/ridge baseline보다 좋은가?

2. **SwiFT emotion specificity**
   - Frozen SwiFT가 충분하지 않다면 어떤 수정이 필요한가?
   - Multi-task head, adapter, subject adapter, affective token, temporal pooling 중 무엇이 유망한가?

3. **Naturalistic pretraining**
   - HCP/CNeuroMod/StudyForrest/Narratives-style movie/story fMRI pretraining이
     Horikawa/Emo-FilM transfer를 개선하는가?
   - 개선이 단순 arousal이나 low-level visual/audio shortcut을 넘는가?

4. **Stimulus-only explanation**
   - Video/audio/text feature만으로 emotion target이 얼마나 설명되는가?
   - Brain model 성능을 brain-specific signal로 해석할 수 있는가?

5. **Stimulus-brain alignment**
   - SwiFT latent와 TRIBE/stimulus latent를 align하면 high-dimensional emotion target이 개선되는가?
   - Encoding loss가 emotion representation에도 도움이 되는가?

6. **Brain-tuned affective AI**
   - Affective LLM/VLM embedding을 fMRI response로 regularize할 수 있는가?
   - Caption/rationale/cue embedding이 brain-stimulus-emotion latent를 풍부하게 하는가?

### 4.3 Working Hypotheses

| Hypothesis | 기대되는 결과 | 반례 / 주의 |
|---|---|---|
| H1. Frozen SwiFT는 일부 emotion signal을 담고 있다. | arousal/category에서 ROI baseline 이상 | ROI/ridge가 계속 더 좋으면 preprocessing과 timing 확인 |
| H2. Rich target에는 emotion-specific adaptation이 필요하다. | adapter/head가 valence/high-dimensional/component target 개선 | frozen feature만으로 충분하면 architecture 복잡화 보류 |
| H3. Naturalistic pretraining은 transfer될 때만 의미 있다. | Horikawa/Emo-FilM high-dimensional/component target 개선 | visual/audio/arousal만 개선되면 emotion-specific claim 금지 |
| H4. Stimulus-only baseline은 일부 target에서 강할 것이다. | V-JEPA/CLIP/audio/text feature가 label을 잘 예측 | brain-specific 해석을 보수적으로 해야 함 |
| H5. Alignment는 high-dimensional target에서 유용할 수 있다. | RSA/CKA/retrieval/multi-label prediction 개선 | encoding만 좋아지고 emotion은 안 좋아질 수 있음 |
| H6. Affective LLM/VLM은 target richness를 제공한다. | caption/rationale embedding alignment 개선 | fMRI가 직접 reasoning한다고 주장하지 않음 |

---

## 5. Methods

### 5.1 Experimental Design Overview

NetFeeliX는 처음부터 큰 end-to-end model을 주장하지 않는다. 먼저 comparable benchmark
surface를 만든 뒤, 결과에 따라 model-development track을 선택한다.

```text
Phase 0: Setup and feasibility
Phase 1: Initial benchmark
Phase 2: SwiFT emotion adaptation
Phase 3: Naturalistic movie/story fMRI pretraining
Phase 4: TRIBE v2 + SwiFT alignment
Phase 5: Brain-tuned affective LLM/VLM extension
Phase 6: Consolidation and paper direction
```

### 5.2 Phase 0: Setup and Feasibility

**Goal**: 실제로 어떤 dataset과 target을 지금 실행할 수 있는지 확인한다.

해야 할 일:

1. dataset local path 확인
2. fMRI shape / TR / timing 확인
3. event file과 HRF lag 가정 확인
4. emotion target matrix 생성
5. train/validation/test split 정의
6. blocked resource list 작성
7. compute requirement 추정

우선 확인할 dataset:

- Horikawa / Cowen emotional video fMRI
- Emo-FilM
- Affective Videos
- IAPS fMRI NeuroVault
- HCP 7T movie
- CNeuroMod / Algonauts
- StudyForrest / Narratives는 access와 역할 정리부터

산출물:

- `setup/results/dataset_availability.md`
- `setup/results/target_construction.md`
- split metadata
- blocked resource list
- first experiment cards

Decision rule:

- Horikawa target이 바로 구성되면 NFx-001/NFx-002로 이동한다.
- Emo-FilM timing이 복잡하면 Horikawa/Affective Videos/IAPS를 먼저 진행한다.
- HCP는 downstream target이 아니라 pretraining-readiness source로 둔다.

### 5.3 Phase 1: Initial Benchmark

**Goal**: fMRI와 emotion target 사이에 최소한의 예측 신호가 있는지 확인한다.

Baseline order:

1. ROI/parcel ridge baseline
2. dynamic FC baseline
3. frozen SwiFT feature + linear/ridge/MLP head
4. stimulus-only baseline

첫 실험 후보:

| ID | Dataset | Model | Target | Purpose |
|---|---|---|---|---|
| NFx-001 | Horikawa | frozen SwiFT + head | high-dimensional emotion vector | BFM transfer 확인 |
| NFx-002 | Horikawa | ROI/parcel ridge | high-dimensional emotion vector | simple baseline |
| NFx-003 | Affective Videos | ridge / frozen SwiFT | arousal, valence | sanity check |
| NFx-004 | IAPS fMRI | beta-map adapter | positive/neutral/negative | static affect check |
| NFx-005 | Emo-FilM | ridge / frozen SwiFT | component/appraisal | naturalistic target readiness |

Decision rule:

- frozen SwiFT가 simple baseline보다 좋으면 adapter/head 확장
- simple baseline이 더 좋으면 preprocessing, HRF timing, feature extraction 점검
- stimulus-only가 너무 강하면 brain-specific claim을 조심하고 alignment/residual analysis 우선

### 5.4 Phase 2: SwiFT Emotion Adaptation

**Goal**: SwiFT를 small emotion fMRI dataset에 맞게 emotion-specific하게 수정한다.

후보 수정:

| Modification | 설명 | 언제 필요한가 |
|---|---|---|
| linear/ridge head | frozen feature readout | 첫 baseline |
| MLP emotion head | shallow nonlinear readout | frozen feature에 신호가 있을 때 |
| multi-task head | arousal/valence/category/vector/component separate heads | heterogeneous target |
| subject adapter | subject embedding or adapter | subject variation이 클 때 |
| dataset/domain adapter | dataset-specific small module | cross-dataset training |
| affective token/query pooling | affect readout token | 4D feature pooling 개선 |
| late-block fine-tuning | late SwiFT block만 update | adapter가 underfit일 때 |
| LoRA-style tuning | attention projection update | 구현 가능할 때 |

Primary targets:

- Horikawa high-dimensional vector
- Emo-FilM component/appraisal target
- Affective Videos arousal/valence
- IAPS category

Decision rule:

- adapter/head가 high-dimensional/component target을 개선하면 SwiFT adaptation track 유지
- arousal만 개선되면 physiology/dynamic objective 고려
- overfitting하면 trainable parameter를 줄이고 split validation 강화

### 5.5 Phase 3: Naturalistic Movie/Story fMRI Pretraining

**Goal**: stimulus-locked fMRI pretraining이 emotion transfer를 개선하는지 검증한다.

Pretraining sources:

| Source | 역할 |
|---|---|
| HCP 7T movie | first large-subject continued pretraining |
| CNeuroMod / Algonauts | multimodal encoding/alignment |
| StudyForrest | long-film continuity |
| Narratives | language/story context |
| 101 Dalmatians | modality control |

Candidate objectives:

- masked fMRI segment modeling
- temporal contrastive learning
- JEPA-style future latent prediction
- subject-invariant contrastive learning
- stimulus-conditioned fMRI prediction
- cross-view retrieval between fMRI and stimulus windows

Evaluation:

- transfer to Horikawa
- transfer to Emo-FilM
- arousal/valence sanity check
- high-dimensional/component target transfer
- low-level visual/audio control
- feature geometry with emotion rating space

Decision rule:

- high-dimensional/component target까지 개선되면 naturalistic pretraining 확장
- arousal나 visual target만 개선되면 sensory adaptation으로 해석
- transfer benefit이 없으면 emotion-specific head, subject adapter, target redesign, alignment 우선

### 5.6 Phase 4: TRIBE v2 + SwiFT Alignment

**Goal**: stimulus dynamics와 fMRI dynamics를 shared latent에서 정렬한다.

Candidate architecture:

```text
Stimulus path:
    video/audio/text -> TRIBE v2 or component encoders -> z_stim

Brain path:
    fMRI window -> SwiFT -> z_brain

Shared latent:
    align(z_brain, z_stim)

Heads:
    z_brain -> emotion
    z_stim  -> emotion
    z_stim  -> predicted fMRI
    z_brain -> future/reconstructed fMRI
```

Candidate loss:

```text
L = L_emotion(z_brain, y_emotion)
  + lambda_1 * L_emotion(z_stim, y_emotion)
  + lambda_2 * L_align(z_brain, z_stim)
  + lambda_3 * L_encoding(z_stim, fMRI)
  + lambda_4 * L_ssl(z_brain)
```

Alignment options:

- regression alignment
- contrastive InfoNCE
- CKA/RSA geometry alignment
- JEPA-style cross-view prediction
- synchronized retrieval

Surface/volume mismatch:

- SwiFT: volumetric 4D fMRI
- TRIBE v2: cortical surface prediction

First solution:

```text
common parcellation or latent-only alignment
```

Decision rule:

- alignment이 high-dimensional emotion 또는 cross-dataset transfer를 개선하면 TRIBE-SwiFT model surgery 우선
- encoding만 좋아지고 emotion은 안 좋아지면 auxiliary로 유지
- stimulus-only가 brain-only를 압도하면 brain-specific residual 분석 필요

### 5.7 Phase 5: Brain-Tuned Affective LLM/VLM Extension

**Goal**: affective LLM/VLM representation을 fMRI response로 regularize한다.

입력:

- affective caption
- cue/rationale label
- appraisal embedding
- VLM/LLM stimulus embedding
- fMRI latent

Candidate model:

```text
stimulus -> affective LLM/VLM -> z_affect
fMRI     -> SwiFT             -> z_brain

loss = contrastive(z_brain, z_affect)
     + emotion_loss
     + optional retrieval / RSA loss
```

주의:

- 이 track은 stimulus-side representation을 풍부하게 만드는 extension이다.
- fMRI가 직접 reasoning을 한다고 주장하지 않는다.
- Alignment나 stimulus-side baseline이 유망할 때만 활성화한다.

### 5.8 Task and Metric Design

NetFeeliX task ladder:

| Level | Task | Dataset candidates | Metric |
|---|---|---|---|
| L0 | data/timing sanity | all | shape/timing report |
| L1 | arousal regression | Affective Videos, Emo-FilM | Pearson/Spearman, CCC |
| L2 | valence regression/category | Affective Videos, IAPS, Emo-FilM | correlation, balanced accuracy |
| L3 | discrete/multi-label emotion | Horikawa, Emo-FilM, NeuroEmo | macro F1, AUROC |
| L4 | high-dimensional emotion vector | Horikawa, Koide-Majima | RSA, CKA, vector correlation |
| L5 | appraisal/component prediction | Emo-FilM | target-wise correlation |
| L6 | continuous affect trajectory | Emo-FilM, REELMO | time-lagged correlation, CCC |
| L7 | cue/rationale/caption embedding | MLLM/REELMO targets | retrieval, contrastive score |

Critical controls:

| Control | 목적 |
|---|---|
| subject split | subject leakage 방지 |
| stimulus split | stimulus identity shortcut 방지 |
| temporal lag sweep | HRF alignment 점검 |
| low-level visual/audio control | sensory shortcut 점검 |
| stimulus-only baseline | brain-specific signal 해석 |
| ROI/ridge baseline | deep model value 확인 |
| frozen vs adapted SwiFT | architecture modification 필요성 |
| generic vs naturalistic-pretrained SwiFT | movie/story SSL transfer 확인 |
| cross-dataset test | dataset-specific shortcut 방지 |

---

## 6. Expected Results

### 6.1 Expected Pattern 1: Frozen SwiFT shows partial transfer

예상:

- arousal 또는 coarse category에서는 frozen SwiFT가 어느 정도 신호를 보일 수 있다.
- high-dimensional emotion vector나 component target에서는 frozen feature만으로 부족할 수 있다.

해석:

- frozen SwiFT가 일부 generic emotion-relevant structure를 갖고 있으면 adapter/head track이 유망하다.
- frozen SwiFT가 simple baseline보다 나쁘면 preprocessing, HRF timing, readout 설계를 먼저 점검해야 한다.

### 6.2 Expected Pattern 2: Arousal transfers more easily than valence or high-dimensional emotion

예상:

| Target | Expected difficulty | 해석 |
|---|---|---|
| arousal | easiest | generic attention/physiology/salience와 연결 |
| valence | harder | stimulus semantics와 appraisal 필요 |
| category | medium-hard | label taxonomy와 dataset bias 영향 |
| high-dimensional vector | core challenge | rich emotion geometry 필요 |
| component/appraisal | hardest but important | context와 interpretation 필요 |

주의:

- arousal만 잘 되는 것은 성공이 아니다.
- high-dimensional target이나 component target에서 개선되어야 emotion representation claim이 강해진다.

### 6.3 Expected Pattern 3: Naturalistic pretraining may help, but only under strict controls

성공적인 결과:

- naturalistic-pretrained SwiFT > generic/resting SwiFT
- improvement appears on Horikawa and Emo-FilM
- improvement appears beyond arousal
- low-level visual/audio control 후에도 signal이 남음

약한 결과:

- movie pretraining이 fMRI reconstruction만 개선하고 emotion transfer는 개선하지 않음
- arousal만 개선됨
- visual-only target에서만 개선됨

해석:

- 강한 결과라면 naturalistic pretraining track을 확장한다.
- 약한 결과라면 sensory adaptation으로 해석하고, emotion-specific head나 alignment로 전환한다.

### 6.4 Expected Pattern 4: Stimulus-only model may be strong

Emotion labels이 group-level stimulus annotations이면 stimulus-only model이 강할 수 있다.

예상:

- Horikawa video stimulus feature만으로도 일부 emotion vector를 예측할 수 있음
- Emo-FilM film stimulus feature가 arousal/component 일부를 설명할 수 있음

이것은 실패가 아니다. 오히려 중요한 해석 기준이다.

```text
stimulus-only가 강한 target에서 brain-only 성능을 brain-specific emotion representation으로
과대해석하면 안 된다.
```

Brain model의 가치가 강해지는 경우:

- brain-only가 stimulus-only보다 특정 target에서 강함
- aligned model이 둘보다 좋음
- brain residual이 subject-specific variation이나 component target을 설명함

### 6.5 Expected Pattern 5: Alignment helps high-dimensional targets more than simple labels

예상:

- positive/neutral/negative 같은 coarse label에서는 alignment 이득이 작을 수 있다.
- high-dimensional emotion vector, component target, representation geometry에서는 alignment가 더 유리할 수 있다.

이유:

- rich emotion representation은 stimulus semantics와 brain dynamics가 함께 필요할 가능성이 높다.
- TRIBE-style model은 video/audio/text temporal fusion에 강점이 있다.
- SwiFT는 observed fMRI dynamics를 담는다.
- 둘을 shared latent에서 결합하면 richer target에서 이득이 날 수 있다.

### 6.6 Scenario-Based Interpretation

| 결과 패턴 | 해석 | 다음 방향 |
|---|---|---|
| frozen SwiFT가 좋음 | generic BFM에 emotion signal 존재 | adapter/head refinement |
| adapter가 크게 개선 | emotion-specific modification 필요 | parameter-efficient SwiFT adaptation |
| naturalistic pretraining이 개선 | stimulus-locked fMRI dynamics 중요 | movie/story pretraining 확장 |
| stimulus-only가 압도 | label이 stimulus-driven | alignment 또는 residual brain analysis |
| alignment가 개선 | emotion은 brain-stimulus shared structure | TRIBE-SwiFT dual encoder |
| arousal만 됨 | low-dimensional affect 중심 | physiology/dynamic objective |
| 전부 약함 | target/preprocessing mismatch 가능 | target construction 재검토 |

---

## 7. Future

### 7.1 Two-Month Roadmap

#### Weeks 1-2: Dataset and Target Readiness

목표:

- 실험 가능한 dataset과 target을 확정한다.

Action:

- Horikawa local path 확인
- Horikawa fMRI shape/TR/event timing 확인
- Horikawa target matrix 생성
- Emo-FilM access와 annotation format 확인
- Affective Videos / IAPS fMRI sanity dataset 확인
- HCP 7T movie access/preprocessing 확인
- CNeuroMod/StudyForrest/Narratives 후보 역할 정리

Deliverable:

- dataset availability report
- target construction report
- blocked resource list
- NFx-001 / NFx-002 experiment card

#### Weeks 3-4: Baselines and Frozen SwiFT

목표:

- simple baseline과 frozen SwiFT transfer를 확인한다.

Action:

- ROI/parcel ridge baseline
- dynamic FC baseline
- frozen SwiFT feature extraction
- frozen SwiFT + linear/ridge/MLP head
- stimulus-only feature 후보 정리

Deliverable:

- first benchmark table
- brain-only vs stimulus-only preliminary comparison
- target-wise failure report

#### Weeks 5-6: SwiFT Adaptation and Naturalistic Readiness

목표:

- SwiFT를 emotion-specific하게 수정할지, naturalistic pretraining으로 갈지 결정한다.

Action:

- multi-task emotion head 설계
- subject adapter 설계
- affective token/query pooling 검토
- HCP naturalistic pretraining minimum viable objective 설계
- low-level shortcut control 설계

Deliverable:

- adapter/head comparison plan
- naturalistic pretraining readiness report
- compute estimate

#### Weeks 7-8: TRIBE-SwiFT Alignment Prototype and Decision Report

목표:

- stimulus-brain alignment 방향의 가능성을 확인한다.

Action:

- TRIBE v2 usage mode 결정
- common parcellation vs latent-only alignment 선택
- stimulus-only vs brain-only vs aligned model 설계
- first alignment experiment card 작성

Deliverable:

- model-development decision table
- go/no-go for naturalistic pretraining
- go/no-go for TRIBE-SwiFT alignment
- abstract/presentation draft outline

### 7.2 Immediate Action Items

#### Dataset / Target

- [ ] Horikawa local data path 확인
- [ ] Horikawa fMRI shape, TR, event timing 확인
- [ ] Horikawa high-dimensional emotion target matrix 생성
- [ ] Emo-FilM access 확인
- [ ] Emo-FilM annotation timing / smoothing strategy 정리
- [ ] Affective Videos access 및 arousal/valence label 확인
- [ ] IAPS fMRI NeuroVault beta map 다운로드 가능 여부 확인
- [ ] HCP 7T movie preprocessing format 확인
- [ ] CNeuroMod/Algonauts, StudyForrest, Narratives, 101 Dalmatians access requirement 정리

#### Baseline

- [ ] ROI/parcel ridge baseline 설계
- [ ] dynamic FC baseline 가능 여부 확인
- [ ] frozen SwiFT feature extraction 가능 여부 확인
- [ ] frozen SwiFT + linear/ridge/MLP head 설계
- [ ] stimulus-only baseline feature 후보 정리
- [ ] NFx-001: Frozen SwiFT Horikawa probe card 작성
- [ ] NFx-002: ROI/ridge Horikawa baseline card 작성
- [ ] NFx-003: Affective Videos arousal/valence card 작성
- [ ] NFx-004: IAPS beta-map category card 작성

#### Model Development

- [ ] emotion-specific multi-task head 설계
- [ ] subject adapter 설계
- [ ] affective token/query pooling 설계
- [ ] adapter vs late-block fine-tuning comparison 정의
- [ ] naturalistic pretraining minimum viable objective 정의
- [ ] TRIBE v2 integration point 결정: feature extractor / teacher / alignment target

#### Stimulus / Alignment

- [ ] Horikawa stimulus availability 확인
- [ ] Emo-FilM stimulus availability 확인
- [ ] video encoder 후보 정리: V-JEPA2, VideoMAE, CLIP
- [ ] audio encoder 후보 정리: Wav2Vec-BERT, Whisper, spectrogram baseline
- [ ] text encoder 후보 정리: sentence-transformer, LLM embedding
- [ ] low-level visual/audio controls 정의
- [ ] common parcellation vs latent-only alignment 결정

#### Documentation / Operations

- [ ] `setup/results/dataset_availability.md` 생성
- [ ] `setup/results/target_construction.md` 생성
- [ ] experiment card template로 NFx 실험 카드 작성
- [ ] 결과가 나올 때마다 decision log 작성
- [ ] framework 변경은 `Paper/framework_KR.md`, `Paper/framework_EN.md`에 반영
- [ ] dataset 변경은 `reference/datasets.md`에 반영
- [ ] task 변경은 `reference/task.md`에 반영
- [ ] training 변경은 `reference/training_strategy.md`에 반영
- [ ] structural edit 후 `python3 scripts/check_md_completeness.py` 실행

### 7.3 Expected Contributions

#### Benchmark contribution

- Emotion fMRI에서 brain-only, stimulus-only, BFM transfer, naturalistic pretraining,
  stimulus-brain alignment를 같은 target/split 기준으로 비교하는 benchmark surface.

#### Model-development contribution

- SwiFT를 emotion-specific fMRI encoder로 발전시키기 위한 adaptation / pretraining /
  alignment roadmap.

#### Conceptual contribution

- fMRI encoder, stimulus-to-brain encoding model, emotion decoding head,
  brain-stimulus aligned model, brain-tuned affective AI adapter를 구분하는 taxonomy.

#### Empirical contribution

- 어떤 emotion target이 fMRI에서 안정적으로 예측되는지 확인.
- naturalistic movie/story pretraining이 emotion transfer에 실제로 도움이 되는지 확인.
- stimulus-only feature가 emotion label을 얼마나 설명하는지 확인.

#### Practical contribution

- dataset cards, experiment cards, decision logs, verification scripts, status
  reports를 포함한 reusable project scaffold.

### 7.4 Possible Paper Directions

결과에 따라 paper framing은 달라질 수 있다.

| 결과 | 가능한 paper framing |
|---|---|
| frozen/adapted SwiFT가 잘 됨 | SwiFT-based emotion fMRI representation learning |
| naturalistic pretraining이 도움 | Naturalistic fMRI pretraining for emotion transfer |
| alignment가 도움 | Brain-stimulus alignment for affective representation |
| stimulus-only가 강함 | Disentangling stimulus-driven and brain-specific emotion representations |
| arousal만 안정적 | Limits of current BFMs for rich emotion geometry |
| dataset/task 문제가 큼 | Benchmark and target-design framework for emotion fMRI modeling |

---

## 8. Short Team Post Version

NetFeeliX는 SwiFT를 기본 brain backbone으로 두고, emotion-labeled fMRI,
naturalistic movie/story fMRI pretraining, TRIBE v2-style stimulus-brain alignment를
결합해 emotion-specific brain representation을 더 잘 학습하는 모델 개발 프로젝트입니다.

핵심은 단순 emotion label prediction이 아니라, arousal/valence, discrete emotion,
multi-label emotion distribution, high-dimensional emotion vector, appraisal/component,
trajectory, cue/rationale embedding까지 이어지는 task ladder에서 어떤 model strategy가
가장 transferable한지를 보는 것입니다.

초기에는 Horikawa, Emo-FilM, Affective Videos, IAPS fMRI로 runnable benchmark를 만들고,
ROI/ridge baseline, frozen SwiFT probe, stimulus-only baseline을 비교합니다. 이후 결과에
따라 SwiFT adapter, subject adapter, affective token, naturalistic pretraining,
TRIBE-SwiFT alignment 중 어떤 방향을 밀지 결정합니다.

HCP movie는 첫 naturalistic pretraining 후보일 뿐이고, CNeuroMod/Algonauts,
StudyForrest, Narratives, 101 Dalmatians는 각각 multimodal alignment, long-film continuity,
language context, modality control이라는 구체적 질문이 있을 때 사용합니다.

Immediate action은 dataset availability, target construction, first baseline, frozen SwiFT
probe, experiment cards입니다.

---

## 9. Key References and Resources

### Project

- NetFeeliX GitHub: https://github.com/Transconnectome/NetFeeliX
- SwiFT: https://github.com/Transconnectome/SwiFT
- TRIBE v2: https://github.com/facebookresearch/tribev2

### Core Emotion fMRI

- Horikawa/Cowen OpenNeuro: https://openneuro.org/datasets/ds002425
- Horikawa/Cowen paper: https://www.sciencedirect.com/science/article/pii/S2589004220302455
- Horikawa data mirror: https://data.mendeley.com/datasets/jbk2r73mzh
- Emo-FilM paper: https://www.nature.com/articles/s41597-025-04803-5
- Emo-FilM OpenNeuro: https://openneuro.org/datasets/ds004892
- Affective Videos: https://www.openfmri.org/dataset/ds000205/
- IAPS fMRI NeuroVault: https://neurovault.org/collections/16284/
- NeuroEmo: https://github.com/OpenNeuroDatasets/ds005700

### Naturalistic fMRI and Alignment

- HCP 7T protocol: https://www.humanconnectome.org/hcp-protocols-ya-7t-imaging
- CNeuroMod datasets: https://www.cneuromod.ca/gallery/datasets/
- Algonauts 2025 brain data: https://algonautsproject.com/2025/braindata.html
- StudyForrest: https://www.studyforrest.org/
- StudyForrest OpenfMRI: https://openfmri.org/dataset/ds000113
- Narratives OpenNeuro: https://openneuro.org/datasets/ds002345
- BOLD Moments: https://www.nature.com/articles/s41467-024-50310-3

### Affective Computing and Task Design

- GoEmotions: https://aclanthology.org/2020.acl-main.372/
- AVEC continuous affect: https://portal.fis.tum.de/en/publications/avec-2012-the-continuous-audiovisual-emotion-challenge
- SemEval Affect in Tweets: https://publications-cnrc.canada.ca/eng/view/object/?id=560b602a-37a5-47be-b306-4b80277382ea
- MME-Emotion: https://mme-emotion.github.io/
- EmoBench-M: https://github.com/Emo-gml/EmoBench-M
- AffectGPT: https://github.com/zeroQiaoba/AffectGPT
- MuSe Challenge: https://www.muse-challenge.org/

### Brain Foundation Models and Brain-Aligned AI

- BrainLM: https://sciety.org/articles/activity/10.1101/2023.09.12.557460
- Brain-JEPA: https://huggingface.co/papers/2409.19407
- NeuroSTORM: https://www.nature.com/articles/s41551-026-01666-y
- Brain-Score Vision: https://github.com/brain-score/vision
- Brain-Score Language: https://github.com/brain-score/language
