> ⚠️ **ARCHIVED — 역사 기록. 현행 문서가 아니다.**
> 현행 논증 = `docs/paper_logic_merged.md` (대전제 · RQ · 가설 H1–H4). 운영 규칙 = `CLAUDE.md`.
>
> 아래 내용 중 다음은 **뒤집혔다.** (a) Qwen3-VL 등 LLM backbone 사용 — 금지.
> (b) open-vocabulary / cross-taxonomy 전이를 headline novelty 로 삼는 프레임 — 폐기.
> (c) 학습에 없던 감정 zero-shot — 폐기(원칙적 분할 기준 없음, RQ 와 무관).
> (d) "EmoBrain 과 EmoViS 는 별도 논문 2편" — 현재는 **한 편의 논문**.
> (e) "EmoBrain 은 cortical location 을 주장하지 않는다" — 현재 **H3 이 cortical location 주장**이다.

# FEEL Task Inventory

This document defines the task space for FEEL. The main goal is not to maximize one emotion prediction score, but to identify which tasks reveal useful **emotion-specific brain representation learning**.

## Affective Computing Task Landscape

Affective computing does not define emotion as only one classification problem.
The field uses a ladder of tasks, from simple label prediction to continuous
affect tracking and, more recently, multimodal reasoning/generation. FEEL
should borrow this task ladder, but translate it carefully into fMRI-compatible
targets.

| Task family | Typical output | Usual metric | Examples | FEEL interpretation |
|---|---|---|---|---|
| Sentiment / valence classification | positive, neutral, negative, or ordinal valence class | accuracy, macro F1, ordinal correlation | SemEval Affect in Tweets, IAPS-style categories | fast low-dimensional check; not sufficient for emotion representation |
| Discrete emotion classification | one emotion label from a fixed taxonomy | accuracy, macro F1, balanced accuracy | IEMOCAP, MELD, DFEW/MAFW-style video emotion sets | useful baseline, but risks forcing one label onto mixed affective states |
| Multi-label / emotion distribution prediction | multiple emotion labels or probability vector | macro/micro F1, AUROC, KL/correlation | GoEmotions, MAFW, MME-Emotion multi-label tasks | closer to Horikawa high-dimensional emotion vectors |
| Dimensional affect regression | continuous arousal, valence, dominance/power, expectancy, intensity | Pearson/Spearman r, CCC, MAE/MSE | AVEC, SemEval intensity regression, MuSe-style affect modeling | essential sanity ladder for fMRI because arousal often transfers first |
| Continuous-time affect tracking | affect trace over frames/utterances/time windows | CCC, time-lagged correlation, dynamic error | AVEC fully continuous challenge, REELMO trajectories | relevant for Emo-FilM and movie fMRI windows |
| Emotion recognition in conversation | utterance-level emotion with context and speaker state | accuracy, macro F1 | IEMOCAP, MELD, ERC tasks | conceptual precedent for context-window modeling; not directly Horikawa |
| Multimodal emotion recognition | emotion from video/audio/text/physiology, often with missing/noisy modalities | task-specific F1, correlation, robustness metrics | MER/MuSe challenges, AffectGPT benchmarks | motivates stimulus-only and multimodal alignment baselines |
| Emotion cause / trigger / interpretation | why the emotion occurs; cue, cause, intent, appraisal, rationale | QA score, human/LLM judge, retrieval, explanation quality | EIBench, MME-Emotion reasoning score, emotion-cause extraction | should be stimulus-side or alignment target, not direct fMRI "reasoning" claim |
| Descriptive affective captioning | natural-language emotion description, fine-grained caption, rationale | caption metrics, LLM judge, retrieval, human preference | AffectGPT / MER-Caption, EmoBench-M generation | can provide embedding targets for brain-stimulus alignment |
| Affective interaction/generation | empathetic response, emotional speech, adaptive dialogue/action | human preference, task success, safety metrics | emotional TTS, empathetic dialogue, affective agents | later extension only; not core FEEL fMRI task |

Key lesson:

```text
Label prediction is the entry point, but modern affective computing increasingly
evaluates intensity, temporal dynamics, multimodal cue grounding, cause/intent,
and free-form affective descriptions.
```

For FEEL, this means the first fMRI tasks should remain measurable
classification/regression problems, while later model-development tracks can use
stimulus-side affective captions, cue labels, and rationale embeddings as
alignment targets.

## Task Groups

| Group | Task | Input | Target/output | Primary dataset | Main model use |
|---|---|---|---|---|---|
| Emotion prediction | Arousal regression | fMRI, stimulus, or aligned latent | continuous arousal | Affective Videos, Emo-FilM, REELMO, Ke datasets | fast sanity check |
| Emotion prediction | Valence regression | fMRI, stimulus, or aligned latent | continuous valence | Affective Videos, IAPS fMRI, Emo-FilM | harder affect dimension |
| Emotion prediction | Emotion intensity regression / ordinal classification | fMRI, stimulus, or aligned latent | per-emotion intensity score or ordinal bin | Emo-FilM, Horikawa-derived ratings, SemEval-style stimulus targets | bridge between category and continuous affect |
| Emotion prediction | Valence category | fMRI beta map or time window | positive/neutral/negative | IAPS fMRI | quick category benchmark |
| Emotion prediction | Discrete emotion prediction | fMRI or stimulus window | emotion category/multi-label vector | Horikawa, Emo-FilM, NeuroEmo | category-like affect structure |
| Emotion prediction | Emotion distribution prediction | fMRI or stimulus window | probability/rating vector over emotion categories | Horikawa, Emo-FilM, MLLM-derived stimulus targets | richer than single-label classification |
| Emotion prediction | High-dimensional emotion vector | fMRI or stimulus window | emotion rating vector | Horikawa, Koide-Majima | affect geometry benchmark |
| Emotion prediction | Appraisal/component prediction | fMRI + stimulus context | component ratings | Emo-FilM | bridge to context understanding |
| Representation learning | Masked fMRI modeling | movie/story fMRI | reconstructed masked segments | HCP 7T movie, CNeuroMod, StudyForrest | SwiFT continued pretraining |
| Representation learning | Contrastive fMRI learning | augmented fMRI windows | matched latent views | HCP, CNeuroMod, Horikawa, Emo-FilM | robust fMRI representation |
| Representation learning | JEPA/future latent prediction | fMRI history window | future or held-out latent | HCP 7T movie, StudyForrest, Narratives | predictive brain dynamics |
| Representation learning | Temporal-window-length comparison | fMRI windows of 5/10/20/40 TR or all valid observed windows | same emotion target under matched splits | Horikawa, Emo-FilM, HCP-derived windows | decide whether emotion needs short evoked response or longer temporal context |
| Representation learning | Subject-invariant learning | multi-subject fMRI | subject-shared latent | HCP, Emo-FilM | transfer across participants |
| Alignment/encoding | fMRI-to-emotion decoding | fMRI | emotion target | Horikawa, Emo-FilM, Affective Videos | SwiFT emotion head |
| Alignment/encoding | stimulus-to-emotion prediction | video/audio/text/image | emotion target | Horikawa, Emo-FilM, REELMO | TRIBE v2/stimulus baseline |
| Alignment/encoding | stimulus-to-fMRI encoding | video/audio/text | fMRI response | CNeuroMod, HCP, Emo-FilM if aligned | TRIBE v2 auxiliary objective |
| Alignment/encoding | brain-stimulus latent matching | fMRI + stimulus | matched latent/retrieval | HCP, Emo-FilM, Horikawa | shared representation |
| Alignment/encoding | TRIBE-teacher distillation | TRIBE-predicted brain response | SwiFT latent or fMRI target | CNeuroMod/HCP-style data | transfer stimulus-brain structure into SwiFT |
| Reasoning/context | short vs long context | local and extended stimulus windows | emotion target | Emo-FilM, REELMO | context sensitivity |
| Reasoning/context | rationale embedding alignment | stimulus + MLLM rationale | rationale/cue embedding | Emo-FilM, REELMO | explanation-aware latent |
| Reasoning/context | cue grounding | audiovisual/text cues | cue-emotion association | REELMO, MLLM-generated targets | avoid label-only shortcut |
| Reasoning/context | emotion cause / trigger interpretation | stimulus, annotations, optional aligned fMRI latent | cause, trigger, intent, or appraisal explanation | EIBench-style targets, MME-Emotion, EmoBench-M | stimulus-side reasoning target; fMRI used for alignment, not direct explanation |
| Reasoning/context | affective caption embedding | stimulus + optional brain latent | descriptive emotion caption or embedding | AffectGPT/MER-Caption-style targets, REELMO | free-form affect target converted to embedding/retrieval objective |
| Reasoning/context | MLLM-derived affect targets | movie/image stimulus | caption, appraisal, cause, intensity | REELMO, Emo-FilM, NSD/OASIS | stimulus-side supervision |
| Transfer | cross-subject transfer | train subjects -> held-out subject | same target | all fMRI datasets | population generalization |
| Transfer | cross-stimulus/movie transfer | train clips/movies -> held-out clips/movies | same target | Horikawa, Emo-FilM, REELMO | content generalization |
| Transfer | cross-dataset transfer | source dataset -> target dataset | compatible affect target | Affective Videos, Emo-FilM, Horikawa | representation robustness |

## Recommended Stage Order

### Stage 0: Feasibility Benchmark

Purpose: determine which datasets and targets are runnable.

Tasks:

1. dataset access and metadata check,
2. fMRI shape and timing check,
3. target construction check,
4. minimal ridge/linear baseline.

Outputs:

- dataset availability table,
- target construction table,
- first baseline metric table,
- blocked-resource list.

### Stage 1: SwiFT Emotion Specificity

Purpose: test whether SwiFT can be made more emotion-specific.

Tasks:

1. SwiFT frozen features + linear/ridge/MLP emotion head,
2. SwiFT sequence-length comparison for SL5, SL10, SL20, and SL40,
3. pretrained SwiFT native-SL fine-tuning versus scratch SwiFT at the same SL,
4. SwiFT adapter or partial fine-tuning,
5. SwiFT continued pretraining on HCP movie first, then other naturalistic sources if they answer a specific alignment/context/modality question,
6. emotion-specific head comparison: arousal/valence, discrete emotion, high-dimensional vector, appraisal/component.

Primary targets:

- Horikawa high-dimensional vector,
- Emo-FilM component/appraisal ratings,
- Affective Videos or IAPS fMRI valence/arousal/category.

### Stage 2: TRIBE v2 and Stimulus-Side Comparison

Purpose: test how much emotion is explained by stimulus context.

Tasks:

1. TRIBE v2 stimulus features -> emotion head,
2. TRIBE v2 predicted brain response -> emotion head,
3. V-JEPA2/CLIP/Whisper/LLM features -> emotion head,
4. stimulus-only vs fMRI-only vs aligned comparison.

Key question:

```text
Does fMRI add emotion-relevant information beyond stimulus features,
or does stimulus context explain most observed emotion labels?
```

### Stage 3: Shared Latent and Context

Purpose: build the FEEL model direction.

Tasks:

1. fMRI and stimulus latent matching,
2. contrastive retrieval between brain windows and stimulus windows,
3. shared latent with emotion and fMRI-response heads,
4. short-window vs long-window context,
5. rationale/cue embedding alignment.

## Task-to-Dataset Mapping

| Dataset | Best first task | Secondary task | Avoid overclaiming |
|---|---|---|---|
| Horikawa | high-dimensional affect geometry | stimulus-only vs fMRI-only comparison | natural-language reasoning |
| Emo-FilM | component/appraisal emotion prediction | context/rationale alignment | large-scale foundation model claims |
| HCP 7T movie | SwiFT continued pretraining | stimulus-conditioned fMRI prediction | direct emotion prediction without labels |
| Affective Videos | valence/arousal sanity check | simple fMRI/stimulus comparison | broad transfer claims |
| IAPS fMRI | valence-category beta-map benchmark | static image affect comparison | temporal dynamics |
| REELMO | context/rationale trajectory targets; Jojo Rabbit dynamic fMRI if accessible | stimulus-side long-context targets | assuming the 60-movie behavioral scale is also fMRI scale |
| NSD | static-image fMRI representation | affective pseudo-label transfer | native emotion labels |
| OASIS | affect label calibration | image affect pseudo-labeling | fMRI analysis |

## Horikawa Rule

Horikawa should be written as a **high-dimensional affect geometry benchmark**, not as a reasoning/context dataset. It is ideal for testing whether SwiFT or a modified fMRI encoder captures rich emotion-category structure from brain activity. It should not be artificially limited to the legacy 5TR subset unless that condition is explicitly being used as a short-window control. Reasoning/context tasks should be tested with Emo-FilM, REELMO, movie datasets, and MLLM-derived cue/rationale embeddings.

## Temporal Window Rule

For fMRI tasks, the target is not only "which model wins?" The target is also
"which temporal window definition lets the model learn emotion-relevant
representation?"

Use these conditions as the default ladder:

1. **All valid observed windows**: use every valid stimulus-response window
   available in preprocessing.
2. **Standardized SL5/SL10/SL20/SL40**: force comparable inputs across models.
3. **Pretrained-native SL**: fine-tune pretrained SwiFT at the sequence length
   used during pretraining.
4. **Scratch matched SL**: train SwiFT from scratch at each length to separate
   architecture length effects from pretrained-transfer effects.
5. **Padding/masking sensitivity**: when short windows are padded into longer
   models, report whether padded frames affect attention and pooling.

## FEEL Task Design Rule

The affective-computing task ladder should be used in order:

1. **Low-dimensional sanity targets**: arousal, valence, positive/neutral/negative.
2. **Category and multi-label targets**: discrete emotion, multi-label vectors,
   emotion distributions.
3. **High-dimensional geometry**: Horikawa/Cowen-style emotion vector prediction
   and RSA/CKA with emotion rating spaces.
4. **Temporal and component targets**: Emo-FilM appraisal/component trajectories,
   REELMO-like affect trajectories if usable.
5. **Reasoning/cue/caption targets**: use MLLM-generated or curated stimulus-side
   targets as embeddings or retrieval labels; do not claim fMRI directly
   generates explanations until there is explicit evidence.

Sources:

- AVEC continuous affect: https://portal.fis.tum.de/en/publications/avec-2012-the-continuous-audiovisual-emotion-challenge
- SemEval Affect in Tweets: https://publications-cnrc.canada.ca/eng/view/object/?id=560b602a-37a5-47be-b306-4b80277382ea
- GoEmotions: https://aclanthology.org/2020.acl-main.372/
- MME-Emotion: https://mme-emotion.github.io/
- EmoBench-M: https://github.com/Emo-gml/EmoBench-M
- AffectGPT: https://icml.cc/virtual/2025/poster/43565
- EIBench / Why We Feel: https://openaccess.thecvf.com/content/CVPR2025W/NeXD/html/Lin_Why_We_Feel_Breaking_Boundaries_in_Emotional_Reasoning_with_Multimodal_CVPRW_2025_paper.html
- MuSe 2025: https://www.muse-challenge.org/
