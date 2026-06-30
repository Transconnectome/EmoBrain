# EmoBrain. Framework (KR)

(2026-06-29 pivot 반영. 이전 direction-split framing (D1 BrainVLM / D2 fMRI-LM / D3 CCN) 폐기. Single project + framework novelty path 의 5 NV spine. 이전 version 은 `archive/v5_direction_split_20260628/Paper/framework_KR.md` 에 보존.)

## 제목

**EmoBrain. Decoding fine-grained emotion from human brain activity.**

(Title 은 locked. Sub-title 의 detail 은 별도 working draft. 본 title 이 paper / talk / repo 모두 의 공식 name.)

---

## 한 줄 요지

하나 의 LLM 기반 foundation model 이 human brain activity 로 부터 fine-grained emotion (V/A 점수, Cat34 top-1 / top-2 / top-k / 34D distribution) 을 decoding 한다. 한 forward pass 안 에서 brain token + naturalistic video token + human-written neutral caption token 의 3-modality 통합 fusion. Brain encoder backbone (raw ROI / Ridge / BFM / VLM) 이 swappable 한 modular 구조 로 fair architectural ablation 가능.

이전 frozen BFM single-modality decoder 의 ceiling 한계 (Phase 1 의 결과) 와 token-output VLM 의 numeric mapping 한계 (D1 v1/v2 negative result) 를 evidence 로 활용 하 여, *왜 single-modality 만 으로 는 fine-grained emotion decoding 이 안 되는지* 의 boundary 를 정의 한 다음, 3-modality fusion + 4-stage curriculum + modular encoder ablation 으로 그 boundary 를 *넘는 가* 를 first systematic test.

---

## Spine question (척추 질문)

**Foundation model 이 답 해야 하는 neuroscientific question.**

Fine-grained emotion (Cowen-Keltner 34 category 의 distribution + V/A 의 continuous) 의 representation 이 human brain 에서 *얼마나 decoding 가능* 한가. 그리고 그 decoding 이 *brain activity 의 unique* 한 contribution 인가. 즉 같은 stimulus 의 video 의 visual content 와 human caption 의 semantic content 를 *control* 한 후 의 brain 의 residual contribution.

이 질문 은 model design 의 질문 이 아니다. Foundation model 은 *answering instrument* 다. Decoding 의 ceiling 자체 = inter-rater concordance (Cowen-Keltner 2017 의 ICC ≈ 0.54). Brain 의 unique contribution 자체 = modality variance partitioning 의 unique-brain term. 둘 다 *측정 가능 한 neuroscientific quantity*.

Model 의 design choice (3-modality fusion, modular encoder, 4-stage curriculum) 는 이 질문 의 *resolution + denoising* instrument 다. 질문 자체 와 conflate 하지 않는다.

### 4 sub-question (척추 질문 의 분해)

- **(a) Affect decoding ceiling.** Cowen-Keltner inter-rater ICC 0.54 의 ceiling 대비 brain decoding 이 얼마 까지 도달 가능 한가. 도달 못 한다 면 그 *gap* 의 nature 가 무엇 인지 (noise vs irreducible individual difference vs missing modality).
- **(b) Brain-unique vs shared contribution.** Brain only 의 decoding accuracy 와 brain + video + caption joint 의 accuracy 의 *delta* 가 video / caption 의 어느 dimension 에 의해 explain 되는가.
- **(c) Modular encoder hierarchy.** Raw ROI vs Ridge vs frozen BFM vs trained VLM 의 4 backbone 의 *which one best preserves fine-grained affect signal*. Phase 1 의 frozen BFM ceiling 한계 가 다른 backbone 에서 도 동일 한지.
- **(d) Behavioral-brain dissociation.** Semantic decoding (Tang/Huth 2023, Horikawa 2024) 은 brain 에서 well-decoded. Affect decoding 은 ceiling-bound. 같은 architecture 에서 두 task 의 *dissociation* 을 reproduce 할 수 있는가. 이는 brain 의 affect code 의 *structural difference* 의 evidence.

각 sub-question 은 §Evaluation framework 의 component 와 1:1 매핑.

---

## Novelty (5 NV)

본 paper 의 contribution. 5 의 novelty 의 *결합* 이 emotion fMRI 분야 의 first systematic instrument.

### NV0. LLM-based brain emotion decoder

Emotion fMRI 분야 에서 LLM (large language model) 을 *fine-grained emotion decoding instrument* 로 통합 한 first paper. 기존 work (Bush 2018 brain states, Saarimäki 2018 cat-specific patterns, Horikawa 2020 27-cat decoding) 은 모두 classical decoder (ridge / SVM / shallow MLP). EmoMind (Mohammed 2026) 이 LLM 을 활용 하지만 evaluation 이 caption-rewriting 의 single task. EmoBrain 은 V/A + Cat34 의 multi-task fine-grained decoding 의 LLM-first instrument.

### NV1. 3-modality LLM fusion

Brain + video + caption 의 *3 modality 모두 의 LLM token sequence 통합 fusion* 의 first emotion fMRI paper. 기존 multi-modal brain encoding (TRIBE Algonauts 2025, Singh 2025 multi-modal) 은 transformer fusion 의 표준 framework 이지만 emotion 의 evaluation 안 함. UMBRAE (ECCV 2024), MindLLM (2025) 의 brain + text fusion 은 *brain-to-text generation* 이지 emotion decoding 아님. 3-modality + emotion 의 결합 이 unique.

### NV2. MindCaptioning human-written neutral caption as bridge

Horikawa 2024 (Science Advances DOI 10.1126/sciadv.adw1464) 의 MindCaptioning 의 human-written neutral caption (per video, crowd-sourced, affect-neutral content description) 을 brain-context bridge 로 활용. Brain token 의 *semantic anchor* 역할. 우리 가 자체 생성 한 model-generated caption (frozen Qwen3-VL 의 video → text) 도 *parallel comparison* 으로 추가, human vs model caption 의 affect-decoding 의 contribution 비교 분석.

### NV3. Modular brain encoder

같은 framework 안 에서 brain encoder backbone 의 4 variant (raw ROI / Ridge embedding / BFM embedding (Brain-JEPA / NeuroSTORM / SwiFT) / trained VLM token) 의 *swappable architecture*. 기존 work 는 한 paper 가 한 encoder choice 만 보고. 우리 는 *같은 fusion + 같은 head + 같은 evaluation* 의 condition 에서 4 encoder 의 fair comparison. Phase 1 의 evidence (frozen BFM < ROI ridge) 가 *generalize* 되는지 측정.

### NV4. 34-distribution output via 4-stage curriculum

Cowen-Keltner 34 category 의 *full distribution* 의 KL-target output 의 4 stage curriculum 학습. Stage 1 top-1 (cross-entropy, easiest), Stage 2 top-2, Stage 3 top-k (k=5), Stage 4 34D distribution (soft KL). 기존 work (EmoMind, Saarimäki, Horikawa) 는 single-task (caption rewriting, top-1 classification, individual category MVPA) 만. *Distribution-level decoding + curriculum* 의 emotion fMRI first.

---

## Architecture

```
INPUT
  fMRI (Horikawa)      -> [Brain encoder (modular)]               -> brain tokens
                          {raw ROI / Ridge / BFM / VLM} swappable
  Video frames         -> [Vision encoder]                        -> video tokens
  (Horikawa stimuli)     {CLIP / V-JEPA2 / VideoMAE}
  Caption              -> [Text tokenizer]                        -> text tokens
  (MC human neutral
   + ours generated)
  Prompt (stage instr) -> [Text tokenizer]                        -> instruction tokens

FUSION
  [brain tokens | video tokens | text tokens | instruction tokens]
  -> [Qwen3-VL LLM with LoRA, OR POYO (ablation)]
  -> fused hidden state

OUTPUT (curriculum)
  Stage 1.  argmax top-1 emotion          (cross-entropy)
  Stage 2.  argmax top-2 emotion          (cross-entropy, multi-label)
  Stage 3.  top-k (k=5) emotion           (cross-entropy, k-hot)
  Stage 4.  34D full distribution         (KL to soft target)

LOSS
  cross-entropy (stage 1-3) + KL to soft target (stage 4)
  + class weighting (label imbalance)
  + optional brain-reconstruction auxiliary (regularizer)
```

학습 = LoRA + projector + brain encoder (variant 에 따라 trainable 또는 frozen). LLM body = frozen.

---

## Modular brain encoder ablation

4 의 brain encoder variant. 같은 fusion + 같은 head + 같은 evaluation 의 condition 에서 fair comparison.

| Variant | Representation | 학습 여부 | 대응 prior work |
|---|---|---|---|
| E1. Raw ROI | Schaefer-400 + Tian-S3-50 의 450 region × 16 TR mean BOLD | 학습 없음 | Cowen-Keltner 2017 MVPA, Saarimäki 2018 |
| E2. Ridge embedding | ROI BOLD → Ridge regression → low-dim embedding | Ridge 학습 | Phase 1 의 winning baseline |
| E3. BFM embedding | Brain-JEPA / NeuroSTORM / SwiFT 의 frozen embedding | Frozen | Phase 1 (6 variant 모두 측정 됨) |
| E4. VLM token | ROI patchify → projector → LLM input slot 의 trainable token | LoRA + projector 학습 | D1 BrainVLM v1/v2 (token output limit), 본 paper 의 new variant |

Phase 1 의 evidence base. Frozen BFM (E3) < Ridge baseline (E2). D1 v1/v2 의 evidence base. Trained VLM token output (E4 의 token-output variant) < Ridge baseline (E2). 본 paper 의 new test. E4 의 hidden-state output variant + multi-modal fusion + curriculum 의 condition 에서 ranking 이 어떻게 바뀌 는지.

각 encoder × 4 task definition (Stage 1-4) = 16 cell 의 fair comparison matrix.

---

## Multi-modal fusion

### Token 의 concatenation

```
[brain_tokens (E_var)] | [video_tokens (V_enc)] | [human_caption_tokens] | [model_caption_tokens] | [instruction_tokens]
```

Brain encoder variant 에 따라 brain token 의 수 가 가변. Video encoder 의 frame downsample 후 token 수 ~256. Human caption ~ 50 token, model caption ~ 50 token. Instruction ~ 20 token (stage-specific task tag).

각 modality 의 token 앞 에 modality 의 special token (`<BRAIN>`, `<VIDEO>`, `<CAPTION_H>`, `<CAPTION_M>`, `<TASK>`) 의 attach 로 LLM 이 modality boundary 를 학습.

### Why MindCaptioning human caption specifically

MindCaptioning (Horikawa 2024, Science Advances) 은 Horikawa 2020 의 *같은 2185 video 의 superset* (2196 video) 에 대해 *human crowd-source* 의 *affect-neutral content description* 을 수집 한 dataset. "A woman is walking on a beach at sunset" 같은 *what happens* 의 description 이지 *how it feels* 의 description 이 아님.

이 caption 의 가치.
- *Semantic anchor*. Brain token 의 noisy signal 을 caption 의 semantic content 가 anchor. LLM 의 fusion 의 *brain signal 의 interpretation* 의 prior.
- *Affect-neutral by construction*. Caption 자체 에 affect label 의 leak 가 없음. Fusion 의 affect prediction 이 *caption alone* 으로 가능 하지 않음 의 guarantee. → modality variance partitioning 의 *unique-brain* term 의 정량 가능.
- *Cross-cohort overlap*. MC 의 11 subject × 2196 video 와 Horikawa 의 5 subject × 2185 video 가 stimulus pool 의 100 % overlap → cross-cohort transfer 의 direct evaluation.
- *Human written = ground-truth-like semantic*. Model-generated caption 의 hallucination / bias 와 비교 의 reference.

### Our model-generated caption (비교 용)

Frozen Qwen3-VL (fine-tune 없음) 의 video → caption pipeline 으로 *같은 2185 video* 의 model caption 생성. Human caption 과 *parallel input* 으로 fusion.

용도.
- *Human vs model caption 의 fusion contribution* 의 ablation. Model caption 이 affect decoding 의 *signal carrier* 인지 *noise* 인지 측정.
- *Scalability 의 future-proof*. 새 dataset (Emo-FilM 등) 의 human caption 없음 → model caption 으로 *generalize* 가능 의 evidence base.
- *Failure mode 의 diagnostic*. Model caption 의 hallucination case 가 brain prediction 의 error case 와 correlate 하는지 분석.

---

## 4-stage curriculum

### Stage progression 의 rationale

Stage 1 top-1 (easiest) → Stage 4 34D distribution (hardest) 의 *progressive task difficulty*. 각 stage 의 output space 가 점진 적 으로 expand.

| Stage | Output | Target | Loss | Rationale |
|---|---|---|---|---|
| 1 | top-1 emotion | one-hot (argmax of crowd 34D) | Cross-entropy | Easiest. Model 의 *gross categorization* 학습. Prior work 의 single-label classification 과 직접 비교 가능. |
| 2 | top-2 emotion | two-hot (top-2 of crowd 34D) | Cross-entropy (multi-label) | Mixed emotion 의 first level recognition. Vaccaro 2024 mixed valence framework 와 align. |
| 3 | top-k (k=5) | k-hot (top-5 of crowd 34D) | Cross-entropy (k-label) | Distribution shape 의 partial capture. Mid-curriculum 의 stabilizer. |
| 4 | 34D distribution | soft target (crowd 34D distribution) | KL to soft target | Full fine-grained distribution. EmoBrain 의 main contribution. |

### Loss schedule

각 stage 에서 *previous stage loss term 의 weight 점진 감소*. Stage 1 의 learning 이 backbone 의 *gross emotion category space* 학습 → Stage 2-3 의 multi-label 학습 이 *category boundary refinement* → Stage 4 의 KL 학습 이 *distribution shape* 학습. 학습 시 catastrophic forgetting 회피.

Class weighting. Cowen-Keltner 34 cat 의 frequency imbalance ("amusement" 같은 frequent vs "embarrassment" 같은 rare) 보정. Inverse-frequency or median-frequency balancing.

Optional brain-reconstruction auxiliary. Brain encoder 의 *trained variant* (E4) 의 경우 *brain token → reconstructed BOLD* 의 auxiliary task. Brain signal 의 *information preservation* 의 regularizer.

---

## Evaluation framework

### Baseline ladder (사다리)

| Tier | Baseline | Purpose |
|---|---|---|
| 0 | Chance | Lower bound |
| 1 | Per-class majority + frequency prior | Trivial baseline |
| 2 | ROI ridge (E2, Phase 1 winning baseline) | Classical strong baseline |
| 3 | Frozen BFM (E3, Phase 1 의 6 variant) | Foundation-model baseline (frozen) |
| 4 | Per-modality only (brain / video / caption) | Single-modality baseline |
| 5 | Joint fusion (full EmoBrain) | Our target |
| C | Cowen-Keltner ICC ceiling (0.54) | Upper bound |

각 tier 의 result 의 *gap* 자체 가 finding 의 component. Tier 5 - Tier 2 = *novelty 의 lift*, Tier C - Tier 5 = *remaining gap to ceiling*.

### Modality variance partitioning

4 의 condition. Brain only / Video only / Caption only / Joint.

Variance decomposition. Joint 의 explained variance R² 를 4 component 로 분해.
- *Unique brain*. Brain only 에서 만 보이는 R².
- *Unique video*. Video only 에서 만 보이는 R².
- *Unique caption*. Caption only 에서 만 보이는 R².
- *Shared*. 둘 이상 의 modality 에서 보이는 R².

SC2 (brain-unique contribution) 의 직접 instrument. Unique-brain 의 정량 = brain 의 *stimulus content 를 넘는 information* 의 양.

### Cowen-Keltner inter-rater concordance ceiling anchor

Cowen-Keltner 2017 PNAS 의 inter-rater ICC ≈ 0.54 (34-category 의 mean). Single video 의 affect rating 의 *human-human agreement* 의 upper limit. 이 ceiling 은 *task 의 irreducible noise* 의 양. Brain decoding 의 absolute ceiling.

우리 의 evaluation. Stage 4 의 34D distribution accuracy 의 KL divergence 또는 spearman correlation 을 0.54 ICC ceiling 의 fraction 으로 normalize 해서 report. "Brain decoding 이 ceiling 의 N % 달성" 의 form.

### Behavioral-brain dissociation

Semantic decoding (Tang & Huth 2023 Nature Neuroscience DOI 10.1038/s41593-023-01304-9, Horikawa 2024 Science Advances DOI 10.1126/sciadv.adw1464) 은 brain 에서 well-decoded. Pearson r 0.5 이상, language-like generation quality 높음.

Affect decoding 은 *동일 architecture* 에서 도 ceiling-bound (Phase 1 의 0.42 r 의 V/A 등). 두 task 의 dissociation 을 *우리 framework 안 에서 reproduce* = brain affect code 의 *structural difference* 의 evidence.

Test. Stage 4 의 EmoBrain 학습 후 *같은 backbone + 같은 brain encoder* 로 caption-generation task (semantic decoding 의 proxy) 의 evaluation. Two task 의 accuracy gap 의 정량.

### Cross-subject LOSO transfer

5 subject pooled training 의 fold 구조 를 *4 subject train + 1 subject zero-shot* 의 5 fold 로 변경. 4 fold 학습 후 5th subject 의 brain 만 fusion 에 attach (re-training 없음, ICL only 또는 projector zero-shot). Cross-subject generalization 의 정량.

SC3 의 직접 instrument.

### Cross-cohort stretch

MindCaptioning 11 subject × 2196 video (Horikawa 2024) 의 *cross-cohort* evaluation. EmoBrain 의 학습 (Horikawa 5 subj) 후 MC 11 subj 의 brain 의 *zero-shot or light-finetune* evaluation.

Stretch goal. 성공 시 *cohort-invariant brain affect code* 의 evidence. 실패 시 cohort-specific factor 의 boundary 정의.

---

## Sub-claims (falsifiable)

### SC1. Modality fusion lift

3-modality joint fusion 의 Stage 4 accuracy 가 *best single-modality baseline* (brain only or video only or caption only 중 max) 보다 *paired bootstrap p < 0.05* 로 유의. Threshold. R² 의 absolute delta ≥ 0.02 또는 Spearman r 의 absolute delta ≥ 0.05.

Null result 의 interpretation. 3-modality fusion 의 lift 가 없다 면 = *brain modality 의 information 이 video + caption 에 의해 fully captured* = "brain decoding 의 unique contribution 없음" 의 boundary 정의. *Publishable negative result*. EmoMind 의 "brain better than label" 의 claim 의 partial refutation.

### SC2. Brain-unique R²

Modality variance partitioning 의 *unique-brain* R² 가 *unique-video* R² 와 *unique-caption* R² 의 *합* 보다 적어도 한 task (V binary, V regression, Cat34 top-1, 34D KL 중) 에서 유의 하게 큼. Threshold. unique-brain R² ≥ 0.05 (absolute), bootstrap 95% CI 가 zero 를 포함 하지 않음.

Null result 의 interpretation. unique-brain 이 video / caption 보다 작 다 면 = "brain 이 stimulus content 의 redundant carrier 일 뿐" 의 finding. Affect 의 brain representation 의 *uniqueness* 의 부재. fMRI affect 분야 의 boundary marker.

### SC3. Modular encoder ranking generalization

E1 raw ROI / E2 ridge / E3 BFM / E4 VLM 의 ranking 이 Stage 1-4 의 4 task 에서 *consistent*. Phase 1 의 E2 > E3 의 ranking 이 multi-modal fusion + curriculum 의 condition 에서 도 hold 하는지. Threshold. Spearman rank correlation 0.7 이상 across stage.

Null result 의 interpretation. Ranking 의 inconsistency = encoder choice 가 *task-dependent* = "encoder universality 없음" 의 finding. Modular encoder design 의 *necessity* 의 evidence (한 encoder choice 가 all task 에 best 가 아님).

### SC4. Cross-subject LOSO transfer

5 fold LOSO 의 zero-shot 5th subject 의 Stage 1 accuracy 가 *ROI ridge baseline* 과 *동등 이상* (paired bootstrap p < 0.05). Threshold. Δ ≥ 0 vs Tier 2 baseline.

Null result 의 interpretation. LOSO 의 fail = subject-pooled fusion 의 *new-subject generalization 의 한계*. Cross-subject universal code 의 부재 의 evidence. Per-subject finetune 의 *necessity* 의 boundary.

### SC5. Behavioral-brain dissociation 의 reproduction

같은 backbone + 같은 brain encoder 의 semantic decoding (caption generation) 과 affect decoding (Stage 4) 의 accuracy 의 gap 이 *Tang/Huth 2023 + Horikawa 2024 의 reported semantic-affect dissociation 의 magnitude* 와 *consistent* (within 20 % relative difference). Threshold. semantic R² / affect R² 의 ratio 가 prior work 의 range (2x-5x) 안.

Null result 의 interpretation. Dissociation 안 보임 = 두 task 가 *similar brain code* 를 사용 한다 는 finding. Affect 가 *semantic 의 subset* 의 evidence. Theoretical 으로 의미 있는 result.

---

## Status as of 2026-06-29

본 pivot 의 시점 의 *preserved evidence base*. 5 NV framework 의 Section 4 (modular encoder ablation) 의 evidence 로 re-frame. 결과 의 *날리지 않음*.

### Phase 1 evidence (preserved)

Frozen BFM (E3 family) 의 ceiling 한계. Brain-JEPA / NeuroSTORM / SwiFT 의 6 variant 모두 ROI ridge baseline (E2) 못 넘 음.

| Task | E2 ROI ridge | E3 best BFM | Gap |
|---|---|---|---|
| V binary balAcc | 0.720 | 0.677 (Brain-JEPA) | -0.043 |
| V regression Pearson r | 0.416 | 0.330 (Brain-JEPA) | -0.086 |
| Cat34 multilabel macro AUROC | 0.711 | 0.679 (Brain-JEPA resting) | -0.032 |

Section 4 의 *E3 row 의 evidence*. BFM 6 variant 모두 E2 못 넘 음 = frozen BFM 의 *ceiling 한계* 의 reproducible evidence.

### D1 BrainVLM v1/v2 evidence (preserved)

E4 의 *XML token output + cross-entropy* variant 의 ceiling 한계. 4 backbone size (2B / 4B / 8B) 모두 동일 plateau.

| Task | Backbone | Best result | Phase 1 ROI ridge baseline | 결과 |
|---|---|---|---|---|
| VA binary token_acc | 2B v1 (5e-4 / 50 ep) | 0.597 | 0.720 balAcc | FAIL |
| VA binary token_acc | 4B v2 (1e-4 / 10 ep) | 0.586 | 0.720 balAcc | FAIL |
| VA binary token_acc | 8B v2 (1e-4 / 10 ep) | 0.606 | 0.720 balAcc | FAIL |
| VA regression V Pearson r | 2B v1 | 0.035 | 0.416 | FAIL |
| VA regression V Pearson r | 4B v2 | 0.008 | 0.416 | FAIL |

진단. Token output formulation 의 fundamental limit. 4 backbone size 모두 plateau = capacity issue 가 아님. Section 4 의 *E4 의 token-output variant 의 negative result*. Backbone 의 hidden state 의 직접 사용 (current REG variant + new EmoBrain fusion) 의 motivation evidence.

### D1 REG variant (running)

Backbone hidden state + MLP regression head + MSE / BCE loss. Token output 폐기. *Current EmoBrain framework 의 fusion 전 stage 의 head architecture 의 prototype*. 결과 가 E4 의 *hidden-state variant* row 의 evidence 가 됨.

### D2 fMRI-LM adapter (pending)

Wei 2026 (arXiv 2511.21760) 의 3-stage architecture. Adapter code 완료, training script pending. EmoBrain framework 안 에 통합 시 *brain encoder variant 의 한 후보* (E4 의 sub-variant) 로 활용.

### Re-framing summary

| 이전 framing | EmoBrain Section |
|---|---|
| Phase 1 frozen BFM | Section 4 의 E3 row 의 evidence |
| D1 BrainVLM v1/v2 token-output | Section 4 의 E4 token-output sub-variant 의 negative result |
| D1 REG variant | Section 4 의 E4 hidden-state sub-variant + 본 fusion 의 head prototype |
| D2 fMRI-LM | Section 4 의 E4 의 alternative tokenizer 의 sub-variant |

5 NV 의 spine 안 에서 모든 prior work 가 *positive evidence (E2 strong baseline)* 또는 *boundary evidence (E3, E4 token-output 의 limit)* 의 role 로 재배치.

---

## Relation to nearest competitors

### EmoMind (Mohammed, Gu, Fang 2026, arXiv 2605.16739v2)

EmoMind 는 LLM-based brain emotion decoding 의 nearest published competitor. Per-subject ridge stage 1 + axis matrix A (34×768) + CFG + 2-stage retrieval+rewriter 의 architecture. Single task (caption rewriting) 의 single subject pipeline.

2026-06-29 의 3-panel literature review 의 predicted verdict. *NeurIPS 2026 borderline-to-reject*. Framework novelty path 자체 는 publishable 하지만 EmoMind 의 specific instantiation 의 evaluation 의 limitation (single task, single subject, weak baseline) 이 reject risk.

**우리 의 differentiation.**
- *3-modality fusion vs single brain modality*. 우리 = brain + video + caption, EmoMind = brain only.
- *Subject-pooled vs per-subject*. 우리 = pooled + LOSO transfer, EmoMind = per-subject endpoint.
- *Multi-task curriculum vs single caption rewriting*. 우리 = Stage 1-4 의 V/A + Cat34 distribution, EmoMind = caption.
- *Modular encoder ablation vs single encoder*. 우리 = E1-E4 의 4 variant, EmoMind = ridge only.
- *Cowen-Keltner ICC ceiling anchor vs no ceiling*. 우리 = absolute ceiling-normalized report, EmoMind = relative comparison only.
- *Behavioral-brain dissociation evidence vs no comparison*. 우리 = semantic vs affect dissociation in same architecture, EmoMind = single decoding task.

같은 framework novelty path 의 viable path. EmoMind 의 boundary 의 *systematic extension* 의 paper position.

### MindCaptioning (Horikawa 2024 Science Advances)

MindCaptioning 은 *semantic decoding* 의 strong reference. Brain → caption 의 generation quality 가 *language-level coherence* 와 *semantic accuracy* 모두 strong. 11 subject × 2196 video 의 large cohort.

**우리 의 활용.**
- *Human-written caption 의 source*. 우리 NV2 의 caption input 의 origin.
- *Semantic decoding 의 reference baseline*. SC5 의 dissociation 의 *semantic side* 의 published quantity 의 reference.
- *Cross-cohort stretch 의 target*. 11 subject 의 cross-cohort transfer evaluation 의 dataset.

Competitor 가 아닌 *complementary*. 우리 paper 의 *semantic-affect dissociation* 의 evidence base.

---

## Datasets

- **Horikawa 2020 naturalistic video fMRI (main).** 5 subj × 2185 silent video. Cowen-Keltner 34-cat + 14-dim + V/A. iScience DOI 10.1016/j.isci.2020.101060. ROI parcellation = Schaefer-400 + Tian-S3-50 (= 450 region).
- **MindCaptioning (Horikawa 2024) (cross-cohort stretch + human caption 의 source).** 11 subj × 2196 video. Cowen-Keltner 2196 과 100 % stim overlap. Human-written caption per video. Science Advances DOI 10.1126/sciadv.adw1464.
- **Emo-FilM (optional, Phase 5 stretch).** Cross-dataset robustness 의 추가 testbed. Human caption 없음 → model-generated caption 만 사용 가능.

---

## Reference list

- Cowen, A. S., & Keltner, D. (2017). Self-report captures 27 distinct categories of emotion bridged by continuous gradients. *PNAS*, 114(38), E7900-E7909. DOI 10.1073/pnas.1702247114.
- Horikawa, T., Cowen, A. S., Keltner, D., & Kamitani, Y. (2020). The neural representation of visually evoked emotion is high-dimensional, categorical, and distributed across transmodal brain regions. *iScience*, 23(5), 101060. DOI 10.1016/j.isci.2020.101060.
- Horikawa, T. (2024). Mind captioning: Evolving descriptive text of mental content from human brain activity. *Science Advances*. DOI 10.1126/sciadv.adw1464.
- Tang, J., LeBel, A., Jain, S., & Huth, A. G. (2023). Semantic reconstruction of continuous language from non-invasive brain recordings. *Nature Neuroscience*, 26(5), 858-866. DOI 10.1038/s41593-023-01304-9.
- Mohammed, A., Gu, X., & Fang, M. (2026). EmoMind. *arXiv* 2605.16739v2.
- Perez, E., Strub, F., de Vries, H., Dumoulin, V., & Courville, A. (2018). FiLM. Visual Reasoning with a General Conditioning Layer. *AAAI*.
- Ho, J., & Salimans, T. (2022). Classifier-free diffusion guidance. *NeurIPS Workshop*. *arXiv* 2207.12598.
- Xia, W., et al. (2024). UMBRAE. Unified multi-modal brain decoding. *ECCV*.
- Qiu, W., et al. (2025). MindLLM. Subject-agnostic fMRI-to-text decoding. *arXiv* 2502.15786.
- Wei, et al. (2026). fMRI-LM. *arXiv* 2511.21760.
- Brain-JEPA (2024). Self-supervised foundation model for fMRI. (DOI / venue 확인 필요, 본 paper 의 ref 통합 시 보완.)
- Wang, et al. (2026). NeuroSTORM. *Nature Biomedical Engineering*. (DOI 확인 필요.)
- Lane, et al. (2026). BrainMarks. *ICML*. (DOI 확인 필요.)
- Bush, K. A., et al. (2018). Brain states that encode perceived emotion are reproducible but their classification accuracy is stimulus-dependent. *Frontiers in Human Neuroscience*. DOI 10.3389/fnhum.2018.00262.
- Vaccaro, A. G., et al. (2024). Mixed valence neural pattern consistency. *Cerebral Cortex*. DOI 10.1093/cercor/bhae122.
- Lage-Castellanos, A., et al. (2019). Methods for computing the maximum performance of computational models of fMRI responses. *PLoS Computational Biology*. DOI 10.1371/journal.pcbi.1006397.
- Allen, E. J., et al. (2022). A massive 7T fMRI dataset to bridge cognitive neuroscience and artificial intelligence (NSD + GLMsingle). *Nature Neuroscience*. DOI 10.1038/s41593-021-00962-x.
- Saarimäki, H., et al. (2018). Discrete neural signatures of basic emotions. *Cerebral Cortex*. (Cat-specific MVPA 의 reference.)

---

## Open decisions

- **OD1. POYO ablation timing.** Qwen3-VL 의 LLM body 의 *alternative ablation* 으로 POYO (neural sequence model) 의 통합 시점. EmoBrain main result 후 의 supplementary 인지, 처음 부터 main ablation 인지.
- **OD2. Brain encoder which to compare first.** Section 4 의 4 variant 의 학습 order. E2 (ridge) + E4 (VLM) 만 먼저 vs E1 + E3 도 함께. 학습 cost 의 trade-off.
- **OD3. MindCaptioning human caption license.** Horikawa 2024 의 caption 의 *redistribution / reproduction* license 확인. 우리 paper 의 figure 에 caption 일부 인용 가능 한지. Author 에 contact 필요 한지.
- **OD4. Our generated caption pipeline.** Frozen Qwen3-VL 의 video → caption 의 *prompt design + temperature + length cap*. Reproducibility 의 spec 확정 timing.
- **OD5. Video encoder which one.** CLIP / V-JEPA2 / VideoMAE 중 main + ablation 의 choice. V-JEPA2 가 SOTA 지만 compute heavy.
- **OD6. Fusion architecture detail.** Token concatenation 의 order, special token 의 design, attention mask 의 modality-specific masking 여부. Pilot 의 ablation 필요.
- **OD7. Evaluation order.** Stage 1-4 의 학습 + evaluation 의 sequence. Stage 1 만 먼저 모든 encoder × all modality combination 의 16 cell 확정 후 Stage 2-4, vs Stage 1-4 의 sequential 학습 의 main path 만.
- **OD8. Paper venue.** NeurIPS 2026 (March deadline) vs ICML 2027 (Jan deadline) vs Nature Communications. 학습 + evaluation 의 timeline 의 venue fit.
