# FEEL 연구 프레임워크 (v4 final, 2026-06-02)

## v4 final Framing (2026-06-02, universal emotion code)

FEEL 는 **brain 에 paradigm, label taxonomy, subject 의 surface variation 을 가로지르는 universal emotion code 가 존재하는지를 multi-source naturalistic emotion fMRI 의 SSL pretrain + adaptation 으로 학습하고 검증하는 project** 다. Emotion theory 논문이 아니라 model-development + scientific evidence 의 결합. Naming 은 internal 에서 "Foundation Model for Emotion Embedding Learning" 유지하되, paper title 에서는 "Universal Emotion Code in Naturalistic Brain Data" 또는 "Transferable Emotion Brain Foundation Model" 로 표현 (Bommasani 2021 정의 scale 미달 reviewer bias 회피).

### Big Question

> Brain 에 paradigm, label taxonomy, subject 의 surface variation 을 가로지르는 *universal emotion code* 가 존재하는가? Multi-source naturalistic emotion fMRI 의 adaptation 으로 그 universal code 를 학습하고 검증할 수 있는가?

핵심 scientific bet. Wager-style universal pain signature 시도의 emotion 판. Affective neuroscience 의 미해결 질문 (universal vs idiosyncratic emotion representation) 에 falsifiable evidence.

### Sub-claims (falsifiable)

1. **Multi-source pretrain invariance**. Universal code 가 존재한다면 multi-source pretrain (Horikawa + Emo-FilM + StudyForrest + Affective Videos) 의 representation 이 single-source pretrain 보다 cross-dataset transfer 에서 더 invariant.
2. **ROI localization**. Universal code 는 brain 의 특정 ROI / network 에 localize. Cowen 2020 transmodal 가설과 align 또는 disagree.
3. **Subject-invariant alignment**. Universal code 는 subject-invariant SSL 후 같은 stim 의 다른 subject 의 representation 의 alignment.
4. **Null**. 위 모두 acquisition floor 안 → "universal code 없음" 결론, negative result paper.

### 2 Main Track + 1 Supplementary

| Track | 답하는 sub-Q | Universal code 측정 |
|---|---|---|
| **Track A (main). BFM SSL pretrain + LoRA adaptation** | Multi-source SSL 이 emotion-relevant invariance emerge? | Cross-dataset invariance metric (subject align, paradigm align, ROI-wise) |
| **Track B (main). Brain+Video framework + task 재설계** | Brain unique 의 universal component? | Joint - video baseline = brain unique. Cross-dataset RSA preservation |
| **Track C (supplementary). BrainVLM generative** | Universal code 의 generative 표현? | Phase 3a parsing fix. Supplementary figure 만 |

**BrainVLM 이 supplementary 인 이유**. (a) LLM visual semantic bias 가 invariance 측정 가림 (Phase 2 video saturate 와 같은 함정), (b) generation noise 가 reliability 낮춤, (c) Phase 3a inference 자체 약함 (V_reg r = NaN, MAE 2.55, scale mismatch), (d) Multi-source 확장 자원 부담 큼.

Track A + Track B 의 **converging evidence** 가 paper 의 강점.

### Track A SSL pretrain 후보 (priority 순)

**Priority 1 (main, 반드시)**
- (1) **Subject-invariant SSL**. 같은 video 의 5 subject 의 brain response 의 contrastive alignment. InfoNCE. Universal code 의 subject invariance evidence. 자원 GPU 며칠.
- (2) **Multi-source SSL (masked autoencoder)**. 4 dataset 의 fMRI 의 30% ROI mask 후 MSE 예측. Paradigm invariance evidence. 자원 GPU 1-2 주.

**Priority 2 (main, 가능하면)**
- (3) **Brain-stimulus contrastive (TRIBE-style)**. Brain ↔ video (V-JEPA2 / CLIP) alignment. Universal code 의 stimulus-driven 측면. 자원 GPU 며칠.

**Priority 3 (optional)**
- (4) Curriculum (resting → naturalistic → emotion 3-stage)
- (5) Distillation

### Target hierarchy (multi-dim 승격, V/A 강등)

| Tier | Target | 비고 |
|---|---|---|
| **Primary** | Cross-dataset emotion-text alignment + Cowen 34-cat multilabel + 14-dim + OV description retrieval | Universal code invariance 측정 |
| **Reference (floor)** | V/A binary + regression | Phase 1-2 에서 video saturate 확정. Floor only |

### Build recipe

5 subj × 2185 stim 으론 from-scratch FM 불가. **Pretrained brain backbone + 소수 multi-source SSL pretrain + emotion-text space adaptation** 이 honest scope.

```
fMRI ─► 450-ROI parcel (Schaefer-400 + Tian-50)
        ▼ BFM backbone, default Brain-JEPA (pretrained ABCD resting)
        ▼ Track A SSL pretrain
            (1) Subject-invariant contrastive  ← priority 1
            (2) Multi-source masked AE          ← priority 1
            (3) Brain-stimulus alignment        ← priority 2
        ▼ LoRA adaptation
        ▼ projection
        z_emo ─► frozen emotion-text embedding space (sentence-transformer / CLIP-text)
                  target = embed(Cowen 34-cat + 14-dim or OV description)
                  loss  = InfoNCE + 보조 regression + caption baseline delta
        ▼ multi-source pooling
        ▼ 평가 (freeze 후)
            Track A invariance metric (subject align, paradigm align, ROI-wise)
            Track B brain unique cross-dataset RSA (Brain+Video framework reuse)
            Track C BrainVLM parsing fix (supplementary)
```

Foundation 의 출처. brain backbone (수만 subject pretrained) × emotion-text space (수천 emotion 개념 geometry) × multi-source SSL pretrain. FEEL 기여 = universal code 의 measurement methodology.

### Cross-dataset evaluation 4 전략

| 전략 | 방법 | 역할 |
|---|---|---|
| 1. Shared text-embedding zero-shot (main) | brain → emotion-text space, native label 이름만으로 zero-shot retrieval | 어느 dataset 의 어느 label 도 학습 없이 평가 |
| 2. Label-space intersection (안전) | target dataset 의 축만 잘라 | 가장 보수적 sanity baseline |
| 3. MLLM universal annotator | OV-MER pipeline 의 local LLM (Qwen2.5-72B / Llama-3.3-70B) frozen artifact | norm 없는 dataset, frozen artifact release |
| 4. Representational alignment (label-free) | RSA / ISC ceiling | NNDb 등 label-free dataset |

### Phase 1-2 measurement 가 framing 의 근거

- Phase 1 frozen probe. ROI mean V_binary AUROC 0.7889 > all BFM (best 0.7402) ≫ Video CLIP 0.9708.
- Phase 2 trained integration. D late fusion 0.9718, CLIP-only 0.9708 → Δ = +0.001 (noise). 4 fusion architecture 모두 video baseline 못 넘음. Brain group-level 추가 contribution = 0.
- Phase 3a BrainVLM. Fold 1 완료, V_reg r = NaN, MAE 2.55. Track C supplementary.
- **의의**. Group-level V/A 는 video saturate. Brain unique signal 은 invariance / cross-dataset preservation 의 4 축. **Universal emotion code 가 그 invariance 의 scientific 표현**. v4 final 의 Track A/B 가 이 4 축 측정.

### 옛 frame 명시적 탈피

- ❌ "Brain + video fusion 으로 video 를 넘는다" (Phase 2 결과로 falsified)
- ❌ BrainVLM token integration 을 main path 로 (Track C supplementary 로 demote)
- ❌ 4 fusion architecture 비교가 main contribution
- ❌ "Brain 이 video 를 이긴다" framing 자체

대신.
- ✅ Universal emotion code 의 존재 검증
- ✅ Brain backbone 의 emotion-specialized adaptation
- ✅ Multi-source SSL pretrain 의 invariance emergence
- ✅ Caption baseline 대비 brain unique variance

### Critic 7 hit 통합

emovi-method-critic 의 적대적 검토에서 식별된 7 weakness 를 모두 반영.

1. **Q2 (decomposability) tautological**. → universal code 는 W 와 무관, invariance metric 으로 직접 측정.
2. **Cross-dataset acquisition confound** (Sripada 2020). → Track A 의 ComBat + 2σ null baseline 의무화.
3. **5 subj power 부족**. → multi-source 로 subject pool 사실상 확장. Open-vocab 강등.
4. **FM naming bias** (Bommasani 2021). → Paper retreat ("Universal Emotion Code" / "Transferable Emotion Brain Foundation Model"), internal FEEL 유지.
5. **Caption baseline 부재** (Doerig 2025). → Track A/B variance partitioning 의무화.
6. **OV-MER GPT-3.5 dependency**. → 전략 3 의 local LLM frozen artifact.
7. **Cowen 34-cat transmodal 한정** (Cowen 2020). → Track A ROI-wise transfer matrix + Sub-claim 2 의 ROI localization.

자세한 phase 별 task / go-no-go / agent review schedule 은 [`docs/masterplan_v2.md`](../docs/masterplan_v2.md) (v4 final) 참고.

---

## Canonical 방향 (v3 narrative, v4 의 supporting context 로 보존)

> 아래 sections (Canonical 방향 ~ 핵심 레퍼런스) 은 v3 framing 때 작성한 narrative. v4 의 Big Q / SQ1-5 와 build recipe 가 우선하지만, literature landscape 와 model development tracks 의 deep discussion 은 v4 에서도 supporting context 로 보존.

FEEL는 **emotion-aware brain representation learning을 위한 모델 개발 프로젝트**다. Emotion theory 논문이 아니다. Emotion theory는 target design을 위한 짧은 제약으로만 사용한다. 즉, emotion label은 noisy하고 dynamic하며 stimulus-dependent이고 multi-component이므로, 모델은 단일 고정 라벨이 아니라 arousal, valence, discrete category, high-dimensional emotion vector에서 평가되어야 한다.

한 문장 프레임 (v3):

**FEEL는 감정 표현을 brain dynamics, naturalistic stimulus dynamics, affective annotation이 만나는 모델 개발 문제로 보고, initial benchmark 결과를 바탕으로 개발할 architecture와 training objective를 결정한다.**

(v4 update. 위 문장의 "benchmark 결과를 바탕으로 architecture/objective 결정" 부분은 Phase 1-2 에서 측정 완료. 결과로 fusion architecture / BrainVLM token 은 emotion 에 효과 없음이 확정. v4 는 그 evidence 위에서 "transfer 와 multi-dim representation" 으로 reframe.)

## 모델 개발 문제 정의

핵심 질문은 "emotion이 무엇인가?"가 아니다. 핵심 질문은 다음이다.

```text
작은 downstream emotion fMRI dataset 조건에서,
어떤 model architecture와 learning objective가 가장 transferable한
brain-based emotion representation을 만드는가?
```

FEEL는 이 질문을 여덟 개의 모델링 질문으로 나눈다.

| 질문 | 모델링 해석 | 첫 실험 |
|---|---|---|
| Generic BFM이 emotion으로 전이되는가? | 넓은 fMRI representation 안에 emotion-relevant structure가 이미 있을 수 있다. | Frozen BFM probe, adapter tuning. |
| 어떤 neural representation이 중요한가? | Whole-brain 4D가 최선이 아닐 수 있다. 특정 voxel, parcel, ROI, network, dynamic connectivity가 더 직접적인 emotion signal을 가질 수 있다. | whole-brain SwiFT/NeuroSTORM vs ROI/parcel ridge vs voxel-weighted sparse model vs network-restricted model. |
| SwiFT는 어떤 temporal window length를 써야 하는가? | Emotion은 짧은 evoked response, delayed hemodynamics, 긴 context 중 어디에서 더 잘 잡힐 수 있다. 또한 pretrained SwiFT는 checkpoint-native sequence length 제약이 있다. | Horikawa all observed windows, standardized SL5/SL10/SL20/SL40, pretrained-native SL20/SL40, scratch SL5/SL10/SL20/SL40. |
| Naturalistic fMRI pretraining이 도움이 되는가? | emotion target은 vision, audio, language, social cue, narrative context가 시간 속에서 결합될 때 생긴다. | resting/generic SwiFT vs HCP/CNeuroMod/StudyForrest-style pretraining. |
| Emotion-labeled pretraining이 필요한가? | naturalistic SSL만으로는 emotion target structure를 직접 배우지 못할 수 있다. | Horikawa/Emo-FilM/Affective Videos/IAPS/NeuroEmo multi-task pretraining과 held-out transfer. |
| 어떤 pretraining curriculum이 좋은가? | stimulus dynamics를 먼저 배울지, emotion label structure를 먼저 배울지, 두 단계를 섞을지 결정해야 한다. | naturalistic-only vs emotion-labeled-only vs naturalistic-to-emotion two-stage comparison. |
| Stimulus-brain alignment가 도움이 되는가? | Emotion은 stimulus dynamics와 brain dynamics 사이의 shared structure일 수 있다. | TRIBE-style stimulus feature와 fMRI latent alignment. |
| Affective AI를 brain-tune할 수 있는가? | LLM/VLM emotion feature가 neural response로 regularize될 수 있다. | Brain-aligned adapter 또는 distillation. |

프로젝트는 비교적이어야 한다. Arousal, valence, discrete emotion, high-dimensional category vector가 서로 다른 architecture와 brain representation을 선호할 수 있다. 따라서 단일 winning model뿐 아니라 failure pattern 자체도 중요한 결과다. SwiFT-first는 출발점이지 고정 결론이 아니다. SwiFT가 충분하지 않으면 그 결과를 인정하고 더 좋은 neural representation 또는 architecture로 pivot한다.

## 모델 개발을 위한 문헌 지형

### fMRI Brain Foundation Models

SwiFT, BrainLM, Brain-JEPA, NeuroSTORM, Omni-fMRI, Brain-DiT 계열은 brain-side foundation-model space를 정의한다. FEEL는 **SwiFT-first**로 간다. SwiFT는 우리 연구실 backbone이므로 구조 수정, continued pretraining, emotion-specific head, multimodal architecture 안의 brain module로 가장 적극적으로 개발할 수 있다. 다른 BFM들은 비교점이다.

- **SwiFT**: 4D fMRI spatiotemporal window attention.
- **BrainLM**: brain activity recording의 masked prediction.
- **Brain-JEPA**: spatiotemporal masking 기반 joint-embedding predictive learning.
- **NeuroSTORM**: 대규모 raw 4D fMRI pretraining과 lightweight adaptation.
- **Omni-fMRI / Brain-DiT**: atlas-free 또는 multi-state pretraining의 future reference.
- **SwiFUN**: resting-state에서 task activation을 예측하는 bridge model. Emotion-related task contrast가 포함되어 있어 중요하다.

FEEL에서 이 모델들은 최종 해답이 아니라, generic brain representation이 emotion-relevant information을 이미 담고 있는지 확인하는 screening baseline이다.

### Stimulus-to-Brain Encoding and Alignment

TRIBE와 TRIBE v2는 SwiFT나 BrainLM 같은 의미의 fMRI encoder가 아니다. 이들은 **stimulus-to-brain encoding model**이다. 즉 video, audio, language feature로부터 fMRI response를 예측한다. 이 차이는 중요하지만, 비교가 불가능하다는 뜻은 아니다.

FEEL는 TRIBE-style model과 SwiFT-style model을 공통 interface로 변환해서 비교한다.

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
5. **Bidirectional FEEL**: stimulus-to-brain encoding과 brain-to-emotion decoding을 shared latent에서 함께 학습한다.

### Affective Computing Foundation Models

Affective computing에서는 foundation model 흐름이 빠르게 커지고 있다. LLM/VLM/MLLM 기반 emotion recognition, emotion reasoning, multimodal affective benchmark, affective generation이 등장했고, Schuller et al.은 이를 affective computing의 foundation-model disruption으로 설명한다. MMAFFBen 같은 benchmark는 text, image, video, language 전반에서 affective reasoning을 평가한다.

여기서 FEEL의 빈틈이 생긴다. Affective AI에는 큰 외부 모델이 있지만 brain grounding이 부족하다. fMRI BFM에는 brain representation이 있지만 emotion을 중심으로 pretraining objective를 설계한 경우가 드물다. FEEL는 emotional/naturalistic stimulus에 대한 brain response가 affective AI representation을 regularize할 수 있는지 묻는다.

최근 MME-Emotion, EmoBench-M, Beyond Emotion Recognition, EIBench 같은 MLLM benchmark는 affective computing이 단순한 "어떤 emotion label인가?"에서 emotional understanding, trigger inference, contextual reasoning으로 이동하고 있음을 보여준다. FEEL가 이 benchmark를 그대로 따라갈 필요는 없지만, stimulus-side affective embedding과 auxiliary target을 더 풍부하게 설계하는 데 쓸 수 있다.

Task 설정도 단순하지 않다. Affective computing은 대체로 다음 ladder를 쓴다.

| Task type | Output | FEEL에서의 의미 |
|---|---|---|
| Sentiment/valence classification | positive/neutral/negative 또는 ordinal class | IAPS/Affective Videos식 낮은 난이도 check |
| Discrete emotion classification | anger, fear, joy 같은 single label | baseline이지만 mixed emotion을 과하게 단순화할 수 있음 |
| Multi-label / distribution prediction | 여러 emotion label 또는 emotion probability vector | Horikawa high-dimensional vector와 가장 잘 맞는 방향 |
| Dimensional regression | arousal, valence, dominance, intensity | fMRI에서 가장 먼저 확인할 sanity ladder |
| Continuous-time affect tracking | frame/window-level affect trajectory | Emo-FilM, REELMO, movie fMRI window 설계와 연결 |
| Cue/cause/reasoning | trigger, intent, appraisal, rationale | stimulus-side auxiliary target 또는 alignment target |
| Affective captioning / QA | 자연어 emotion description, QA answer | fMRI가 직접 문장을 생성한다기보다 embedding/retrieval target으로 사용 |

따라서 FEEL의 task 설계는 classification vs regression 중 하나를 고르는 문제가 아니다. 처음에는 arousal/valence/category로 안정성을 확인하고, 핵심은 multi-label/high-dimensional emotion geometry와 component/trajectory target으로 이동하며, reasoning/caption은 stimulus-side representation을 풍부하게 만드는 auxiliary target으로 둔다.

Top conference 흐름을 보면 이 방향이 더 분명하다. ICML 2025 AffectGPT는 multimodal emotion recognition을 descriptive emotion understanding, fine-grained emotion caption, unified benchmark 문제로 재정의한다. NeurIPS 2025 VidEmo는 affective-tree reasoning guidance로 emotion-centric video foundation model을 학습한다. ICLR 2026 AVERE, MME-Emotion, EmotionHallucer, HitEmotion은 audiovisual cue grounding, emotion hallucination, emotional-intelligence evaluation, Theory-of-Mind-guided multimodal emotion reasoning을 다룬다. FEEL가 배울 점은 emotion model이 label만 맞히는 것이 아니라, temporal context와 affective cue에 grounded된 representation을 만들어야 한다는 것이다.

### Brain-Tuning and Brain-Aligned AI

Brain-Score Vision, Brain-Score Language, EEG representational alignment, brain-tuning speech/language model, multi-participant brain-tuning, fMRI language-encoding scaling law는 neural data가 AI model을 평가하는 데 그치지 않고 tuning 또는 regularization signal로도 쓰일 수 있음을 보여준다. FEEL에서는 이를 다음처럼 조심스럽게 확장한다.

```text
affective LLM/VLM representation + emotional stimulus에 대한 fMRI response
    -> brain-aligned affective adapter 또는 distilled affective embedding
```

fMRI 데이터는 작기 때문에 full LLM/VLM fine-tuning이 아니라 adapter, contrastive alignment, distillation이 현실적이다.

SED-GPT는 fMRI, long-sequence semantic decoding, emotion distribution, LLM-style prior를 결합한 가까운 precedent다. 다만 이것은 fMRI emotion foundation model이 이미 있다는 증거가 아니라, semantic/emotional fMRI decoding이 early-stage 수준에서 가능하다는 근거로 인용하는 것이 맞다.

### Gap Statement

아직 mature한 fMRI emotion foundation model 방향은 없다. 기존 fMRI BFM은 대체로 generic하고, neural-signal FM은 emotion을 downstream benchmark 중 하나로만 포함하는 경우가 많으며, affective computing FM은 brain grounding이 약하고, stimulus-to-brain model은 emotion representation보다는 fMRI encoding을 주로 최적화한다. FEEL는 이 빈틈에서 **emotion-aware brain/stimulus representation을 위한 screening-benchmark-driven model development**를 핵심 목표로 둔다.

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
| REELMO | time-resolved affect reports; fMRI participants watched Jojo Rabbit | optional | planned | limited one-movie fMRI | optional | strong stimulus-side supervision |
| HCP 7T movie | pretraining objective | planned | planned features | planned | planned | naturalistic pretraining source |

## Horikawa와 Reasoning/Context Understanding의 관계

Horikawa에 reasoning/context story를 전부 억지로 얹으면 어색하다. Horikawa의 강점은 많은 short video에 대한 high-dimensional visually evoked emotion space와 fMRI response다. 따라서 FEEL에서 Horikawa는 **brain-side affect geometry probe**로 두는 것이 가장 자연스럽다.

Reasoning과 context understanding은 더 긴 temporal context, cue grounding, narrative structure, natural-language rationale이 필요하다. 이 부분은 다른 source에서 가져오는 것이 맞다.

- **Emo-FilM**: component/appraisal-style annotation과 naturalistic film context.
- **REELMO**: 긴 movie trajectory, 20 emotion label, stimulus feature, subtitle, 그리고 Jojo Rabbit 1편의 fMRI subset.
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

Decision rule: frozen/adapted BFM이 arousal 이상의 target에서도 simple baseline을 넘으면 adapter/fine-tuning을 우선한다. 반대로 ROI/parcel ridge, voxel-weighted linear model, network-restricted model, 다른 BFM, stimulus-aligned model이 같은 split과 target에서 더 안정적으로 좋으면 SwiFT 중심 개발은 축소하거나 폐기한다. FEEL의 목적은 SwiFT를 지키는 것이 아니라 emotion representation을 잘 학습하는 모델과 neural representation을 찾는 것이다.

### Track A0: Neural Representation Search

목표는 어떤 brain representation이 emotion prediction과 affective geometry에 실제로 중요한지 확인하는 것이다. Whole-brain 4D input이 가장 정보가 많아 보이지만, small fMRI dataset에서는 noise와 subject variability 때문에 특정 ROI, parcel, network, voxel weighting이 더 나을 수 있다.

비교할 representation은 다음과 같다.

| Representation | 예시 | 검증 이유 |
|---|---|---|
| Whole-brain 4D volume | SwiFT, NeuroSTORM | distributed spatiotemporal pattern 보존 |
| Parcel/ROI time series | Schaefer/Tian, HCP-MMP, emotion/salience/visual ROI | 빠르고 안정적이며 cross-dataset harmonization이 쉬움 |
| Voxel-weighted model | ridge, elastic-net, sparse linear model, stability selection | 어떤 voxel이 emotion target에 기여하는지 확인 |
| Network-restricted model | visual, auditory, salience, DMN, limbic/control network | whole-brain 대신 어떤 system이 중요한지 테스트 |
| Dynamic connectivity | sliding-window FC, temporal graph feature | arousal/context dynamics가 FC에 더 잘 잡히는지 확인 |
| Subject-adapted representation | subject adapter, hyperalignment, shared response model | 개인차와 shared affect structure를 분리 |
| Stimulus-aligned latent | TRIBE/V-JEPA/audio/text와 fMRI latent alignment | emotion이 brain-stimulus shared structure에서 더 잘 잡히는지 확인 |

이 track의 산출물은 성능표뿐 아니라 interpretability table이어야 한다. 즉 어떤 target에서 어떤 region/network/time window/stimulus modality가 중요한지 기록한다.

### Track A1: SwiFT Temporal-Length and Padding Comparison

목표는 emotion representation이 짧은 event-level response, 더 긴 temporal context,
혹은 checkpoint-native SwiFT sequence length 중 어디에서 가장 잘 학습되는지
결정하는 것이다.

이 track이 필요한 이유는 Horikawa를 exactly-5TR dataset처럼 취급하면 안 되기
때문이다. Local preprocessing에는 variable-length response window가 존재한다.
기존 5TR setup은 loader/split 설계에서 생긴 legacy subset이지, 전체 dataset
정의가 아니다.

비교 조건은 다음과 같다.

| 조건 | Length | 이유 |
|---|---|---|
| all observed windows | observed 5-47 frames | 모델이 지원할 수 있으면 가용 데이터를 모두 사용한다 |
| standardized windows | SL5, SL10, SL20, SL40 | temporal context를 통제해서 비교한다 |
| pretrained-native SwiFT | matching checkpoint가 있으면 SL20, SL40 | checkpoint-compatible fine-tuning의 기준 조건 |
| pretrained SwiFT with short observed windows | observed 5/10/20 frames를 native SL로 pad/crop | short-window adaptation과 padding sensitivity 확인 |
| scratch SwiFT | SL5, SL10, SL20, SL40 | pretrained weight 제약 없이 sequence-length effect 확인 |

Rule: pretrained SwiFT fine-tuning은 원칙적으로 checkpoint-native sequence length를
유지해야 한다. Downstream window가 더 짧거나 길면 그것은 동일 실험이 아니라
padding/mask/crop이 명시된 adaptation experiment로 기록해야 한다.

### Track B: Pretraining Source and Curriculum

목표는 어떤 pretraining source와 curriculum이 emotion transfer를 개선하는지 확인하는 것이다. 이 track은 "movie가 rest보다 당연히 좋다"는 주장도 아니고, emotion label만 많이 넣으면 된다는 주장도 아니다. 정확한 가설은 작은 emotion-labeled fMRI dataset으로 바로 학습하기 전에, SwiFT가 visual, auditory, language, social, narrative cue에 의해 유도되는 stimulus-locked brain dynamics를 먼저 배워야 하는지, 아니면 Horikawa/Emo-FilM/Affective Videos/IAPS/NeuroEmo 같은 emotion-labeled dataset으로 target-aware affect structure를 먼저 배워야 하는지 비교하는 것이다.

따라서 pretraining은 세 갈래로 비교한다.

1. naturalistic SSL pretraining: movie/story fMRI에서 stimulus-locked dynamics를 학습한다.
2. emotion-labeled pretraining: emotion label, high-dimensional vector, component/appraisal target으로 multi-task supervised 또는 weakly supervised learning을 한다.
3. two-stage pretraining: naturalistic dynamics를 먼저 배우고, emotion-labeled dataset으로 specialization한다.

처음에는 parcel-level time series로 시작한다. Simple pipeline이 안정화되기 전에는 raw 4D volume으로 바로 가지 않는다.

Dataset 선택은 가설별로 한다.

| Source | 역할 | 검증 질문 |
|---|---|---|
| HCP 7T movie | large-subject continued pretraining | stimulus-locked pretraining이 Horikawa/Emo-FilM transfer를 개선하는가 |
| CNeuroMod / Algonauts | multimodal encoding/alignment | video/audio/transcript-to-fMRI alignment가 emotion target에 도움이 되는가 |
| StudyForrest | long-film continuity | 긴 audiovisual narrative가 temporal representation에 주는 이득이 있는가 |
| Narratives | language/story context | visual cue 없이 narrative context alignment가 도움이 되는가 |
| 101 Dalmatians | modality control | visual-only, auditory-only, audiovisual condition 차이가 emotion transfer에 중요한가 |
| Horikawa / Emo-FilM / Affective Videos / IAPS / NeuroEmo | emotion-labeled pretraining | supervised affective pretraining이 held-out emotion transfer를 개선하는가 |

후보 objective:

- masked fMRI segment modeling,
- temporal contrastive learning,
- JEPA-style latent prediction,
- subject-invariant contrastive learning,
- future brain-state prediction,
- optional stimulus-conditioned prediction,
- multi-task emotion label/vector/component prediction,
- emotion geometry alignment across datasets.

Decision rule: naturalistic-pretrained encoder가 Horikawa/Emo-FilM에서 generic BFM transfer를 넘고, 단순 arousal이나 low-level visual/audio shortcut을 넘어 high-dimensional/component target에도 이득을 보이면 movie/story pretraining을 확장한다. Emotion-labeled pretraining이 held-out emotion dataset transfer를 개선하면 multi-dataset affective pretraining과 task-specific head를 확장한다. Two-stage pretraining이 가장 좋으면 naturalistic dynamics first, emotion specialization second curriculum을 우선한다. 이득이 없거나 visual shortcut만 보이면 emotion-specific head, subject adapter, TRIBE-style alignment, target 재설계를 우선한다.

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
