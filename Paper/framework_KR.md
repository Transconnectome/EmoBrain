# NetFeeliX 연구 프레임워크

## Canonical 방향

NetFeeliX는 **emotion-aware brain representation learning을 위한 모델 개발 프로젝트**다. Emotion theory 논문이 아니다. Emotion theory는 target design을 위한 짧은 제약으로만 사용한다. 즉, emotion label은 noisy하고 dynamic하며 stimulus-dependent이고 multi-component이므로, 모델은 단일 고정 라벨이 아니라 arousal, valence, discrete category, high-dimensional emotion vector에서 평가되어야 한다.

한 문장 프레임:

**NetFeeliX는 감정 표현을 brain dynamics, naturalistic stimulus dynamics, affective annotation이 만나는 모델 개발 문제로 보고, initial benchmark 결과를 바탕으로 개발할 architecture와 training objective를 결정한다.**

외부 공유용 요약:

> NetFeeliX는 처음부터 완성형 emotion foundation model을 주장하지 않겠습니다. 먼저 SwiFT, naturalistic movie/story fMRI dataset, TRIBE v2-style stimulus-to-brain model, affective LLM/VLM representation을 하나의 initial benchmark에서 비교하겠습니다. Benchmark는 어떤 정보원이 어떤 emotion target에 도움이 되는지 확인하는 단계이고, 그 결과에 따라 SwiFT emotion adaptation, naturalistic fMRI continued pretraining, TRIBE-SwiFT stimulus-brain alignment, brain-tuned affective LLM/VLM adapter 중 어떤 model-development track을 밀지 결정하겠습니다.

## 모델 개발 문제 정의

핵심 질문은 "emotion이 무엇인가?"가 아니다. 핵심 질문은 다음이다.

```text
작은 downstream emotion fMRI dataset 조건에서,
어떤 model architecture와 learning objective가 가장 transferable한
brain-based emotion representation을 만드는가?
```

NetFeeliX는 이 질문을 네 개의 모델링 질문으로 나눈다.

| 질문 | 모델링 해석 | 첫 실험 |
|---|---|---|
| Generic BFM이 emotion으로 전이되는가? | 넓은 fMRI representation 안에 emotion-relevant structure가 이미 있을 수 있다. | Frozen BFM probe, adapter tuning. |
| Naturalistic fMRI pretraining이 도움이 되는가? | emotion target은 vision, audio, language, social cue, narrative context가 시간 속에서 결합될 때 생긴다. | resting/generic SwiFT vs HCP/CNeuroMod/StudyForrest-style pretraining. |
| Stimulus-brain alignment가 도움이 되는가? | Emotion은 stimulus dynamics와 brain dynamics 사이의 shared structure일 수 있다. | TRIBE-style stimulus feature와 fMRI latent alignment. |
| Affective AI를 brain-tune할 수 있는가? | LLM/VLM emotion feature가 neural response로 regularize될 수 있다. | Brain-aligned adapter 또는 distillation. |

프로젝트는 비교적이어야 한다. Arousal, valence, discrete emotion, high-dimensional category vector가 서로 다른 architecture를 선호할 수 있다. 따라서 단일 winning model뿐 아니라 failure pattern 자체도 중요한 결과다.

## 모델 개발을 위한 문헌 지형

### fMRI Brain Foundation Models

SwiFT, BrainLM, Brain-JEPA, NeuroSTORM, Omni-fMRI, Brain-DiT 계열은 brain-side foundation-model space를 정의한다. NetFeeliX는 **SwiFT-first**로 간다. SwiFT는 우리 연구실 backbone이므로 구조 수정, continued pretraining, emotion-specific head, multimodal architecture 안의 brain module로 가장 적극적으로 개발할 수 있다. 다른 BFM들은 비교점이다.

- **SwiFT**: 4D fMRI spatiotemporal window attention.
- **BrainLM**: brain activity recording의 masked prediction.
- **Brain-JEPA**: spatiotemporal masking 기반 joint-embedding predictive learning.
- **NeuroSTORM**: 대규모 raw 4D fMRI pretraining과 lightweight adaptation.
- **Omni-fMRI / Brain-DiT**: atlas-free 또는 multi-state pretraining의 future reference.
- **SwiFUN**: resting-state에서 task activation을 예측하는 bridge model. Emotion-related task contrast가 포함되어 있어 중요하다.

NetFeeliX에서 이 모델들은 최종 해답이 아니라, generic brain representation이 emotion-relevant information을 이미 담고 있는지 확인하는 screening baseline이다.

### Stimulus-to-Brain Encoding and Alignment

TRIBE와 TRIBE v2는 SwiFT나 BrainLM 같은 의미의 fMRI encoder가 아니다. 이들은 **stimulus-to-brain encoding model**이다. 즉 video, audio, language feature로부터 fMRI response를 예측한다. 이 차이는 중요하지만, 비교가 불가능하다는 뜻은 아니다.

NetFeeliX는 TRIBE-style model과 SwiFT-style model을 공통 interface로 변환해서 비교한다.

| Interface | 입력 | 모델 형태 | Objective |
|---|---|---|---|
| Brain-only decoding | fMRI | SwiFT/BFM encoder + emotion head | emotion prediction |
| Stimulus-only decoding | video/audio/text | TRIBE-style fusion + emotion head | emotion prediction |
| Encoding-regularized brain model | fMRI + training-time stimulus | fMRI encoder + stimulus auxiliary loss | emotion + alignment |
| Bidirectional aligned model | fMRI and/or stimulus | shared brain-stimulus latent | emotion + fMRI prediction + contrastive/JEPA loss |

따라서 올바른 표현은 "TRIBE와 SwiFT는 비교할 수 없다"가 아니다. 올바른 표현은 **native input-output direction이 다르므로, harmonized target, split, head를 가진 modified variants로 비교해야 한다**이다.

구체적인 model-surgery variant는 다음과 같다.

1. **SwiFT-decoder baseline**: fMRI에서 emotion을 예측한다.
2. **TRIBE-emotion baseline**: video/audio/text에서 emotion을 예측한다.
3. **TRIBE-to-SwiFT distillation**: fMRI encoder가 stimulus-derived latent structure를 학습한다.
4. **SwiFT-to-TRIBE alignment**: fMRI latent와 TRIBE-style stimulus latent를 정렬한다.
5. **Bidirectional NetFeeliX**: stimulus-to-brain encoding과 brain-to-emotion decoding을 shared latent에서 함께 학습한다.

### Affective Computing Foundation Models

Affective computing에서는 foundation model 흐름이 빠르게 커지고 있다. LLM/VLM/MLLM 기반 emotion recognition, emotion reasoning, multimodal affective benchmark, affective generation이 등장했고, Schuller et al.은 이를 affective computing의 foundation-model disruption으로 설명한다. MMAFFBen 같은 benchmark는 text, image, video, language 전반에서 affective reasoning을 평가한다.

여기서 NetFeeliX의 빈틈이 생긴다. Affective AI에는 큰 외부 모델이 있지만 brain grounding이 부족하다. fMRI BFM에는 brain representation이 있지만 emotion을 중심으로 pretraining objective를 설계한 경우가 드물다. NetFeeliX는 emotional/naturalistic stimulus에 대한 brain response가 affective AI representation을 regularize할 수 있는지 묻는다.

최근 MME-Emotion, EmoBench-M, Beyond Emotion Recognition, EIBench 같은 MLLM benchmark는 affective computing이 단순한 "어떤 emotion label인가?"에서 emotional understanding, trigger inference, contextual reasoning으로 이동하고 있음을 보여준다. NetFeeliX가 이 benchmark를 그대로 따라갈 필요는 없지만, stimulus-side affective embedding과 auxiliary target을 더 풍부하게 설계하는 데 쓸 수 있다.

Top conference 흐름을 보면 이 방향이 더 분명하다. ICML 2025 AffectGPT는 multimodal emotion recognition을 descriptive emotion understanding, fine-grained emotion caption, unified benchmark 문제로 재정의한다. NeurIPS 2025 VidEmo는 affective-tree reasoning guidance로 emotion-centric video foundation model을 학습한다. ICLR 2026 AVERE, MME-Emotion, EmotionHallucer, HitEmotion은 audiovisual cue grounding, emotion hallucination, emotional-intelligence evaluation, Theory-of-Mind-guided multimodal emotion reasoning을 다룬다. NetFeeliX가 배울 점은 emotion model이 label만 맞히는 것이 아니라, temporal context와 affective cue에 grounded된 representation을 만들어야 한다는 것이다.

### Brain-Tuning and Brain-Aligned AI

Brain-Score Vision, Brain-Score Language, EEG representational alignment, brain-tuning speech/language model, multi-participant brain-tuning, fMRI language-encoding scaling law는 neural data가 AI model을 평가하는 데 그치지 않고 tuning 또는 regularization signal로도 쓰일 수 있음을 보여준다. NetFeeliX에서는 이를 다음처럼 조심스럽게 확장한다.

```text
affective LLM/VLM representation + emotional stimulus에 대한 fMRI response
    -> brain-aligned affective adapter 또는 distilled affective embedding
```

fMRI 데이터는 작기 때문에 full LLM/VLM fine-tuning이 아니라 adapter, contrastive alignment, distillation이 현실적이다.

SED-GPT는 fMRI, long-sequence semantic decoding, emotion distribution, LLM-style prior를 결합한 가까운 precedent다. 다만 이것은 fMRI emotion foundation model이 이미 있다는 증거가 아니라, semantic/emotional fMRI decoding이 early-stage 수준에서 가능하다는 근거로 인용하는 것이 맞다.

### Gap Statement

아직 mature한 fMRI emotion foundation model 방향은 없다. 기존 fMRI BFM은 대체로 generic하고, neural-signal FM은 emotion을 downstream benchmark 중 하나로만 포함하는 경우가 많으며, affective computing FM은 brain grounding이 약하고, stimulus-to-brain model은 emotion representation보다는 fMRI encoding을 주로 최적화한다. NetFeeliX는 이 빈틈에서 **emotion-aware brain/stimulus representation을 위한 screening-benchmark-driven model development**를 핵심 목표로 둔다.

## Initial Benchmark 전략

첫 단계는 비싼 end-to-end architecture를 주장하는 것이 아니라, dataset, model, target을 공정하게 비교할 수 있는 benchmark surface를 만드는 것이다.

Benchmark 질문:

1. 접근성, preprocessing, temporal alignment를 고려했을 때 실제로 쓸 수 있는 dataset과 target은 무엇인가?
2. Non-deep brain baseline은 어느 정도 성능을 내는가?
3. Frozen BFM representation이 arousal, valence, discrete category, high-dimensional emotion vector를 예측하는가?
4. 어떤 target에서는 stimulus-only feature가 brain-only feature보다 강한가?
5. Brain-stimulus alignment가 high-dimensional target 또는 cross-dataset transfer를 개선하는가?
6. 2개월 model development에서 어떤 방향을 밀어야 하는가?

최소 benchmark table:

| Dataset | Target | Brain-only baseline | Stimulus-only baseline | Existing BFM | Alignment model | Notes |
|---|---|---|---|---|---|---|
| Horikawa | high-dimensional emotion vector | planned | planned | planned | planned | core downstream |
| Emo-FilM | emotion/appraisal/component ratings | planned | planned | planned | planned | modern naturalistic benchmark |
| Affective Videos | valence/arousal | planned | optional | planned | optional | lightweight sanity check |
| REELMO | time-resolved affect reports | optional | planned | optional fMRI subset | optional | strong stimulus-side supervision |
| HCP 7T movie | pretraining objective | planned | planned features | planned | planned | naturalistic pretraining source |

## Horikawa와 Reasoning/Context Understanding의 관계

Horikawa에 reasoning/context story를 전부 억지로 얹으면 어색하다. Horikawa의 강점은 많은 short video에 대한 high-dimensional visually evoked emotion space와 fMRI response다. 따라서 NetFeeliX에서 Horikawa는 **brain-side affect geometry probe**로 두는 것이 가장 자연스럽다.

Reasoning과 context understanding은 더 긴 temporal context, cue grounding, narrative structure, natural-language rationale이 필요하다. 이 부분은 다른 source에서 가져오는 것이 맞다.

- **Emo-FilM**: component/appraisal-style annotation과 naturalistic film context.
- **REELMO**: 긴 movie trajectory, 20 emotion label, stimulus feature, subtitle, fMRI subset.
- **HCP/CNeuroMod/StudyForrest/Narratives movie-story data**: naturalistic fMRI pretraining, modality/context ablation, stimulus-brain alignment experiment.
- **Affective MLLM benchmark/model**: descriptive emotion caption, cue-emotion QA, rationale embedding, hallucination diagnostic.

연결은 단계적으로 한다.

1. Horikawa로 brain encoder가 high-dimensional affective geometry를 잡는지 본다.
2. Emo-FilM/REELMO로 temporal context와 appraisal/component target이 representation을 개선하는지 본다.
3. MLLM-derived rationale 또는 cue embedding을 stimulus-side auxiliary target으로 만든다.
4. 먼저 fMRI latent를 emotion label embedding과 align하고, 이후 context/rationale embedding과 align한다.
5. Short-window, long-window, stimulus-ablation model을 비교해 context 효과를 평가한다.

이렇게 하면 프로젝트가 덜 흔들린다. Horikawa는 "brain representation이 rich emotion geometry를 잡는가?"를 묻고, reasoning/context track은 "naturalistic stimulus-brain alignment가 affective state가 왜 시간 속에서 생기는지 설명할 수 있는가?"를 묻는다.

## Model Development Tracks

### Track A: SwiFT-first BFM Transfer

목표는 SwiFT와 관련 pretrained brain model이 emotion-relevant structure를 이미 갖고 있는지 확인하는 것이다.

순서:

1. Frozen encoder + ridge/linear/MLP head.
2. 지원되는 경우 adapter 또는 LoRA-style tuning.
3. 안정적인 probe 결과가 나온 뒤 partial/full fine-tuning.

주요 모델: SwiFT. 비교 모델: BrainLM, Brain-JEPA, SwiFUN, code/weight 접근이 가능하면 NeuroSTORM.

Decision rule: frozen/adapted BFM이 arousal 이상의 target에서도 simple baseline을 넘으면 adapter/fine-tuning을 우선한다.

### Track B: Naturalistic Movie/Story Pretraining

목표는 naturalistic stimulus-driven fMRI pretraining이 emotion transfer를 개선하는지 확인하는 것이다. 이 track은 "movie가 rest보다 당연히 좋다"는 주장이 아니다. 정확한 가설은 작은 emotion-labeled fMRI dataset으로 바로 학습하기 전에, SwiFT가 visual, auditory, language, social, narrative cue에 의해 유도되는 stimulus-locked brain dynamics를 먼저 배워야 하는지 검증하는 것이다.

처음에는 parcel-level time series로 시작한다. Simple pipeline이 안정화되기 전에는 raw 4D volume으로 바로 가지 않는다.

Dataset 선택은 가설별로 한다.

| Source | 역할 | 검증 질문 |
|---|---|---|
| HCP 7T movie | large-subject continued pretraining | stimulus-locked pretraining이 Horikawa/Emo-FilM transfer를 개선하는가 |
| CNeuroMod / Algonauts | multimodal encoding/alignment | video/audio/transcript-to-fMRI alignment가 emotion target에 도움이 되는가 |
| StudyForrest | long-film continuity | 긴 audiovisual narrative가 temporal representation에 주는 이득이 있는가 |
| Narratives | language/story context | visual cue 없이 narrative context alignment가 도움이 되는가 |
| 101 Dalmatians | modality control | visual-only, auditory-only, audiovisual condition 차이가 emotion transfer에 중요한가 |

후보 objective:

- masked fMRI segment modeling,
- temporal contrastive learning,
- JEPA-style latent prediction,
- subject-invariant contrastive learning,
- future brain-state prediction,
- optional stimulus-conditioned prediction.

Decision rule: naturalistic-pretrained encoder가 Horikawa/Emo-FilM에서 generic BFM transfer를 넘고, 단순 arousal이나 low-level visual/audio shortcut을 넘어 high-dimensional/component target에도 이득을 보이면 movie/story pretraining을 확장한다. 이득이 없거나 visual shortcut만 보이면 emotion-specific head, subject adapter, TRIBE-style alignment, target 재설계를 우선한다.

### Track C: Stimulus-Brain-Emotion Alignment

목표는 naturalistic stimulus와 brain dynamics 사이의 shared latent로 emotion을 학습하는 것이다.

후보 architecture:

```text
Stimulus path:
    video/audio/text -> TRIBE-style temporal fusion -> z_stim

Brain path:
    fMRI window -> SwiFT/BFM/temporal encoder -> z_brain

Shared latent:
    align(z_stim, z_brain)

Heads:
    z_brain -> emotion
    z_stim -> emotion
    z_stim -> predicted fMRI
    z_brain -> future/reconstructed fMRI
```

후보 feature:

- video: V-JEPA2, VideoMAE, CLIP frame features,
- audio: Wav2Vec2/Wav2Vec-BERT, Whisper, spectrogram baseline,
- text: subtitle/caption + sentence-transformer 또는 LLM embedding.

Decision rule: stimulus-only feature나 alignment loss가 high-dimensional target에서 이득을 보이면 brain-only pretraining보다 TRIBE-style model surgery를 우선한다.

### Track D: Brain-Tuned Affective LLM/VLM

목표는 brain response를 external affective model의 biological alignment signal로 사용하는 것이다.

현실적인 첫 variant:

1. Affective VLM/LLM embedding이 fMRI latent를 예측하도록 작은 adapter를 학습한다.
2. Emotion classifier에 brain-geometry regularizer를 추가한다.
3. Shared stimulus-brain latent를 lightweight affective embedding에 distill한다.
4. fMRI-derived arousal 또는 high-dimensional estimate를 movie segment의 auxiliary pseudo-label로 사용한다.

Decision rule: stimulus-side affective embedding이 강하거나 brain-stimulus alignment가 유의미하면 이 track을 활성화한다.

## 데이터 전략

| 역할 | 데이터셋 | 목적 |
|---|---|---|
| Naturalistic pretraining | HCP 7T movie, CNeuroMod/Algonauts, StudyForrest, Narratives, 101 Dalmatians | stimulus-locked fMRI dynamics, modality/context ablation, alignment 가설 검증 |
| Core emotion downstream | Horikawa, Emo-FilM | high-dimensional/naturalistic emotion transfer 평가 |
| Lightweight emotion downstream | Affective Videos, IAPS fMRI, NeuroEmo, 접근 가능하면 Koide-Majima | valence/arousal/category screening benchmark |
| Static-image affect extension | NSD, OASIS labels, image affect models | large static-image fMRI representation과 affective pseudo-labeling |
| Stimulus-side affective supervision | REELMO, MMAFFBen/MMAFFIn, affective LLM/VLM | stimulus emotion trajectory 생성/검증 |
| Auxiliary encoding | BOLD Moments, CNeuroMod, Algonauts 2025, future expansion으로 Spacetop | video/audio/text-to-fMRI alignment와 physiology-rich transfer 검증 |

Naturalistic pretraining과 Horikawa/Emo-FilM downstream evaluation이 중심이다. HCP는 첫 후보지만 유일한 후보가 아니다. 다른 dataset은 "더 많이 쓰기 위해서"가 아니라 modality, narrative context, alignment, low-level shortcut 같은 benchmark matrix의 불확실성을 줄일 때 추가한다.

## Evaluation Ladder

Target은 난이도 계단으로 보고한다.

1. **Arousal regression**: early sanity check. 가장 전이 가능성이 높다.
2. **Valence regression**: 더 어려운 affective dimension.
3. **Discrete emotion prediction**: category-like structure.
4. **High-dimensional emotion vector prediction**: rich representation의 핵심 테스트.
5. **Cross-dataset transfer**: dataset shortcut이 아니라 emotion-relevant representation을 학습했다는 강한 증거.

Metrics:

- regression: Pearson r, Spearman r, MAE/MSE, subject-wise confidence interval,
- classification/multi-label: macro F1, AUROC, balanced accuracy, top-k accuracy,
- representation: RSA/CKA, retrieval, explained variance,
- fMRI encoding: parcel/voxel correlation, 가능하면 noise-ceiling-normalized score.

## 기대 기여

- Generic BFM transfer, naturalistic movie/story fMRI pretraining, stimulus-brain alignment를 emotion prediction 관점에서 체계적으로 비교한다.
- 2개월 안에 의미 있는 결과를 낼 수 있는 benchmark-to-model-development roadmap을 만든다.
- fMRI encoder, stimulus-to-brain encoding model, emotion-aware aligned representation model을 구분하는 taxonomy를 제공한다.
- Affective computing foundation model과 affective neuroscience 사이의 model-development bridge를 제안한다.
- Adapter, naturalistic pretraining, TRIBE-style alignment, brain-tuned affective VLM/LLM 중 무엇을 밀지 결정하는 rule을 제공한다.

## 핵심 레퍼런스

| 영역 | 레퍼런스 | 역할 |
|---|---|---|
| fMRI BFM | SwiFT, SwiFUN, BrainLM, Brain-JEPA, NeuroSTORM, Omni-fMRI, Brain-OF | brain-side baseline과 pretraining precedent |
| Stimulus-to-brain | TRIBE, TRIBE v2, VIBE, Algonauts 2025, Hu and Mohsenzadeh | multimodal alignment와 fMRI response prediction |
| Naturalistic fMRI | HCP 7T movie, CNeuroMod, StudyForrest, Narratives, 101 Dalmatians, BOLD Moments | movie/story pretraining, modality/context ablation, naturalistic dynamics |
| Emotion fMRI | Horikawa, Koide-Majima, Emo-FilM, Ke et al., Affective Videos, NeuroEmo, REELMO | downstream target과 target difficulty |
| Affective FM | Schuller et al., LLM affect survey, MLLM emotion reasoning survey, MMAFFBen, MME-Emotion, EmoBench-M, EIBench | external affective AI와 emotion-reasoning trend |
| Top-conference affective reasoning | ICML 2025 AffectGPT; NeurIPS 2025 VidEmo; ICLR 2026 AVERE, EmotionHallucer, HitEmotion/MME-Emotion | label prediction에서 cue grounding, rationale, context, hallucination control로 이동하는 흐름 |
| Brain tuning | Brain-Score Vision/Language, EEG representational alignment, brain-tuning speech LMs, scaling laws, SED-GPT | brain-aligned AI와 fMRI semantic/emotion decoding precedent |
