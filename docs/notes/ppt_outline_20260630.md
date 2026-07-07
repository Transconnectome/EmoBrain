# EmoBrain. PPT slide deck (working draft, 2026-06-30)

발표 의 length 가 15-25 분 의 가정. 약 20-22 slide. academic / lab meeting talk 의 standard.

각 slide 의 의 *visual cue + speaker note + bullet text + figure spec* 의 4 component. PPT 생성 시 의 reference.

---

## SLIDE 1. Title

**Title.**
> **EmoBrain. Decoding fine-grained emotion from human brain activity.**

**Sub-title (optional).** *A multi-modal LLM-based foundation model for naturalistic emotion fMRI.*

**Footer.** Author + Affiliation + Date.

**Visual cue.** Brain (Schaefer-400 parcellation 의 cortical surface render) + emotion 의 wordcloud (Cowen-Keltner 34 category) + LLM 의 schematic. 세 element 의 결합.

**Speaker note.**
> "오늘 발표 의 주제 는 EmoBrain 입니다. 인간 의 brain activity 의 fMRI 로 부터 fine-grained 한 emotion 의 representation 을 decoding 하 는 LLM 기반 multi-modal foundation model 입니다."

---

## SLIDE 2. Motivation 1. Emotion 의 high-D nature

**Title.** Emotion 은 high-dimensional + distributed.

**Bullet text.**
- 기존 frame. 기쁨 / 슬픔 의 *몇 개 의 basic emotion* (Ekman 1992).
- 또는 *valence + arousal* 의 2 차원 (Russell 1980).
- **최근 의 finding.** 인간 의 *수십 개* 의 distinct emotion category 의 사용. *27 emotion 의 distinct cluster + continuous gradient* (Cowen-Keltner 2017 PNAS).
- 그 emotion 의 *brain representation 도 high-D + categorical + multiple transmodal region 의 distributed* (Horikawa 2020 iScience).
- **함의.** *손 으로 만든 몇 개 의 feature* 의 emotion decoding 의 한계. *data-driven + high-D* 의 approach 필수.

**Figure spec.**
- Cowen-Keltner 의 27-emotion 의 t-SNE 또는 UMAP plot (논문 의 Figure 1 의 reference, 직접 reuse 가능).
- 또는 emotion 34 category 의 *colored network*.

**Speaker note.**
> "감정 은 단순 하 지 않 습니다. 옛 frame 의 *기본 감정 몇 개* 가 아니라, 사람 들 이 *수십 개 의 distinct emotion* 을 사용 함 의 evidence. 그리고 그 emotion 의 brain representation 도 *high-D + distributed*. 이 풍부 한 structure 를 손 으로 만든 feature 로 잡 기 어렵 습니다."

**Citation.**
- Cowen & Keltner 2017. PNAS. DOI 10.1073/pnas.1702247114.
- Horikawa 2020. iScience. DOI 10.1016/j.isci.2020.101060.
- Russell 1980. JPSP.
- Ekman 1992. Cognition and Emotion.

---

## SLIDE 3. Motivation 2. Naturalistic emotion fMRI 의 data scarcity

**Title.** Naturalistic emotion fMRI = data 의 scarcity.

**Bullet text.**
- 분야 의 표준 dataset.
  - Horikawa 2020. **5 subject × 2185 silent video clip**. *largest naturalistic emotion fMRI*.
  - Emo-FilM (Morgenroth 2025). 9 film, 30 subject. *story-level*.
  - 그 외. 대부분 *5-30 subject* 의 scale.
- 비교. Vision 의 large-scale dataset (ImageNet) 의 *1.4 M image*. NLP 의 *수십억 token* corpus.
- **함의.** 우리 의 *연구 별 처음 부터 학습 의 overfit 의 fundamental risk*. 또한 high-D emotion 의 학습 의 *fundamental statistical limit*.

**Figure spec.**
- Bar chart. Dataset size 의 비교 (Horikawa 2185 vs ImageNet 1.4M vs etc.).
- 또는 표 의 형식. dataset 별 의 subject + stim + scale.

**Speaker note.**
> "Naturalistic emotion fMRI 의 데이터 는 적습니다. Horikawa 2020 의 5 명 + 2185 자극 이 분야 의 *largest*. Vision 의 ImageNet 의 백만 단위 와 비교 의 *수천 배 의 차이*. 이 적은 데이터 로 *high-D emotion 의 학습* 의 fundamental statistical limit."

---

## SLIDE 4. Motivation 3. Foundation model 의 기대 + limit

**Title.** Foundation model 의 기대 + 분야 의 현 limit.

**Bullet text.**
- **기대.** 수십 만 건 의 large-scale 의 pretrain → 범용 representation → 개별 연구 의 *적은 데이터 의 활용*.
- 분야 의 fMRI foundation model.
  - **Brain-JEPA** (Yu 2024). UK Biobank resting fMRI (10k+ subject) 의 ViT pretrain.
  - **SwiFT** (Kim 2023). HCP resting fMRI 의 Swin transformer.
  - **NeuroSTORM** (Wang 2026 Nat Biomed Eng). 50k+ subject 의 multi-cohort fMRI pretrain.
- **단 limit.** 분야 의 BFM 의 *resting-state* pretrain. *naturalistic task* + *emotion task* 의 *transfer 의 unproven*.
- 우리 의 Phase 1 의 evidence. *모든 frozen BFM 이 simple ROI mean + Ridge baseline 을 못 넘음*.

**Figure spec.**
- Bar chart. Phase 1 의 frozen BFM 6 variant 의 V binary balanced accuracy + ROI ridge baseline. 결과 = 모든 BFM 의 ridge 의 *아래*.
- 또는 dot plot + error bar.

**Speaker note.**
> "Foundation model 의 기대 는 *큰 데이터 의 pretrain 후 의 범용 표현* 의 활용. 단 분야 의 fMRI BFM 의 대부분 이 *resting-state* pretrain. naturalistic emotion task 의 transfer 의 unproven. 우리 의 Phase 1 의 실측 의 *모든 BFM 이 simple ROI ridge baseline 을 못 넘 음* 의 evidence."

**Citation.**
- Brain-JEPA. Yu et al. 2024.
- SwiFT. Kim et al. 2023.
- NeuroSTORM. Wang et al. 2026. Nat Biomed Eng. DOI 10.1038/s41551-026-01666-y.

---

## SLIDE 5. Research question. EmoBrain 의 spine

**Title.** Research question.

**Bullet text.**
- **Fine-grained emotion (Cowen-Keltner 34 category 의 distribution + V/A continuous)** 의 representation 이 *human brain* 에서 *얼마나 decoding 가능* 한가.
- 그리고 그 decoding 이 *brain activity 의 unique* 한 contribution 인가 (= same stimulus 의 visual content + caption content 를 control 한 후 의 brain 의 residual contribution).
- 이 question 의 *fMRI foundation model + multi-modal context* 의 도구 로 답.

**Sub-question 4 (4 component).**
- (a) **Decoding ceiling.** Brain decoding 의 도달 정도. Ceiling 은 brain ISC / label split-half 로 측정. (Cowen concordance 54% 는 참고 값, ICC 아니고 직접 ceiling 아님 — 2026-07-07 정정.)
- (b) **Brain-unique vs shared contribution.** Brain only 의 decoding accuracy 와 brain + video + caption joint 의 decoding accuracy 의 *delta* 의 source.
- (c) **Modular encoder hierarchy.** Raw ROI vs Ridge vs frozen BFM vs trained VLM 의 *which preserves fine-grained affect signal*.
- (d) **Behavioral-brain dissociation.** Semantic decoding (Tang/Huth 2023, Horikawa 2025) 의 success vs affect decoding 의 ceiling-bound 의 *same architecture 의 dissociation*.

**Figure spec.**
- 4 sub-question 의 box diagram. 각자 의 instrument 의 hint.

**Speaker note.**
> "EmoBrain 의 spine question. 인간 의 brain 으로 부터 fine-grained emotion 의 decoding 의 정도 + brain 의 unique contribution 의 분리. 4 sub-question 으로 분해."

---

## SLIDE 6. Approach. 5 Novelty 의 overview

**Title.** Approach. 5 Novelties (NV0-NV4).

**Bullet text + table.**

| NV | Name | One-line |
|---|---|---|
| NV0 | LLM-based brain emotion decoder | Emotion 분야 의 LLM 통합 의 first instrument |
| NV1 | 3-modality LLM fusion | brain + video + caption 의 token sequence 의 단일 LLM forward 의 통합 |
| NV2 | MindCaptioning bridge | Human-written neutral caption 의 brain-context bridge |
| NV3 | Modular brain encoder | raw ROI / Ridge / BFM / VLM 의 swappable |
| NV4 | 34-distribution curriculum | top-1 → top-2 → top-k → full 34D KL 의 4 stage |

NV0 = framing axis. NV1-NV4 = component.

**Figure spec.**
- 5 NV 의 *concept diagram*. NV0 = center, NV1-NV4 = surrounding.

**Speaker note.**
> "EmoBrain 의 approach 의 5 novelty. NV0 의 LLM 기반 framework 의 first 가 axis. NV1-NV4 의 4 component 의 결합."

---

## SLIDE 7. Architecture overview

**Title.** Architecture.

**Figure (ASCII 또는 visual).**

```
INPUT
  fMRI (5 subj × 2185 stim pooled)
      → Brain encoder (modular. E1-E4)                → brain tokens
  Video (Horikawa silent clip)
      → Vision encoder (CLIP / V-JEPA2 / VideoMAE)    → video tokens
  Caption
      MindCaptioning human-written neutral caption     → text tokens
      + our Qwen-VL generated caption (비교)
  Prompt (task-specific instruction + 34-cat inventory)
      → instruction tokens

FUSION
  [brain | video | text | instruction] tokens
      → Qwen3-VL LLM (LoRA fine-tune)
      → fused hidden state

OUTPUT (4 stage curriculum)
  Stage 1   top-1 emotion           Cross-Entropy
  Stage 2   top-2 emotion           Multi-label CE
  Stage 3   top-k (k=5)             k-hot sparse CE
  Stage 4   full 34D distribution   KL to soft target
```

**Bullet text (right side).**
- Backbone. Qwen3-VL (2B or 4B, LoRA).
- Brain encoder = 4 modular variant.
- Curriculum = 4 stage 의 progressive.

**Speaker note.**
> "Architecture 의 한 view. 3 modality 의 input + LLM fusion + 4 stage curriculum 의 output."

---

## SLIDE 8. NV3. Modular brain encoder

**Title.** NV3. Modular brain encoder.

**Bullet text + table.**

| Variant | Label | Source | Trainable? |
|---|---|---|---|
| **E1** | No pretrain (control) | raw ROI mean (Schaefer-400 + Tian-S3-50 = 450 region) + simple projector | projector only |
| **E2** | Task-specific, no LLM pretrain | ROI Ridge regression 의 latent | Ridge trained |
| **E3** | fMRI pretrain frozen | Brain-JEPA / SwiFT / NeuroSTORM 의 frozen embedding | frozen |
| **E4** | Image pretrain + fMRI fine-tune | Qwen3-VL vision encoder (image pretrain) → D1 BrainVLM fMRI fine-tune (LoRA + projector) 의 hidden state | trained during D1, then frozen |

**Key question.**
- E3 (rsfMRI 의 large-scale pretrain frozen) vs E4 (image pretrain + fMRI fine-tune) 의 *어느 게 brain 의 fine-grained affect signal 의 better preserves*.

**Figure spec.**
- 4 encoder 의 box diagram. 각자 의 pretrain source + adaptation step.

**Speaker note.**
> "NV3 의 modular brain encoder. 4 variant 의 fair 비교. 같은 fusion stack + 같은 head + 같은 evaluation. 핵심 question = rsfMRI pretrain 의 transfer 가 강 한 가 vs image pretrain + fMRI fine-tune 의 adaptation 이 강 한 가."

---

## SLIDE 9. NV1. 3-modality LLM fusion + NV2. MindCaptioning bridge

**Title.** NV1 + NV2. Multi-modal LLM fusion with caption bridge.

**Bullet text.**
- **NV1.** 3 modality (brain + video + caption) 의 LLM token sequence 통합 fusion. 한 LLM forward pass.
- **NV2.** MindCaptioning (Horikawa 2024, Science Advances) 의 *human-written neutral caption*.
  - Crowd-sourced, affect-neutral content description.
  - Per video 의 brain-context bridge.
  - 우리 generated caption (Qwen-VL) 도 parallel comparison.
- Token assembly (대략).
  - brain ~900 token + video ~256 token + caption ~20 token + prompt ~30 token = ~1200 token.

**Figure spec.**
- Token sequence 의 horizontal bar. 각 modality 의 비중.
- 또는 caption sample 의 예시 (MindCaptioning 의 1-2 sentence + 우리 generated 의 1-2 sentence).

**Speaker note.**
> "NV1 의 3 modality LLM 통합. NV2 의 MindCaptioning 의 human-written caption 의 brain-context anchor. 우리 generated caption 도 비교 의 reference 로 동시 활용."

**Citation.**
- Horikawa 2024. MindCaptioning. Science Advances. DOI 10.1126/sciadv.adw1464.

---

## SLIDE 10. NV4. 4-stage curriculum

**Title.** NV4. 34-distribution output via 4-stage curriculum.

**Bullet text + diagram.**

```
Stage 1. top-1 emotion           (easiest)
   ├ Cross-entropy
   ├ Argmax of 34 class
   └ Metric. balanced accuracy

Stage 2. top-2 emotion
   ├ Multi-label CE
   ├ Top 2 per stimulus
   └ Metric. F1 + accuracy

Stage 3. top-k (k = 5)            
   ├ k-hot sparse CE  
   ├ Top 5 per stimulus
   └ Metric. macro AUROC + per-class recall

Stage 4. full 34D distribution    (hardest)
   ├ KL divergence to soft target
   ├ rater empirical distribution
   └ Metric. KL + dim-wise Pearson r + high-D structure preservation
```

**Loss schedule.**
- Stage 1-3. Cross-entropy + class weighting (Cowen 34 의 imbalance).
- Stage 4. KL + class weighting.
- Optional. Brain-reconstruction auxiliary loss (LLM hidden → ROI mean 복원).

**Speaker note.**
> "NV4 의 4 stage curriculum. Top-1 의 easy 부터 full 34D distribution 의 hard 까지 의 progressive. 각 stage 의 loss + metric 의 정의."

---

## SLIDE 11. Training paradigm. Knowledge distillation (P2-B)

**Title.** Training paradigm. P2-B knowledge distillation.

**Bullet text + diagram.**

```
Stage 1 (Teacher 학습).
  Input. brain + video + caption + prompt.
  Output. 34D emotion distribution.
  Loss. CE + KL (depending on curriculum stage).
  → Teacher checkpoint.

Stage 2 (Soft label caching).
  Teacher 의 inference 의 *모든 학습 sample* 의 soft label 의 save.

Stage 3 (Student 학습).
  Input. brain + prompt only (video / caption 제거).
  Output. 34D emotion distribution.
  Loss = α × CE_ground_truth + (1-α) × KL_distillation_target.
  → Student checkpoint.

Inference. Student 의 brain-only forward.
```

**Why P2-B.**
- Teacher 의 *rich context (video + caption)* 의 학습 signal 의 student 의 *brain only inference* 의 transfer 의 명확 한 mechanism.
- *Leakage 없음*. student 가 video 의 직접 input 안 봄.
- Teacher / Student 의 같은 Qwen3-VL backbone + LoRA 만 다름 → 학습 cost 의 single model 수준.

**Light P2-A auxiliary.** Random modality dropout 의 약 한 비율 의 추가 가능 (robustness).

**P2-C excluded.** Structural conflict 의 risk (alignment 가 brain 의 video mimicry 의 leakage 의 back-door).

**Speaker note.**
> "P2-B knowledge distillation 의 paradigm. Teacher 의 rich context 학습 + Student 의 brain-only 학습. Inference 시 brain only 의 자연. Teacher / Student 의 backbone 공유 의 cost 작 음."

---

## SLIDE 12. Three-stage execution (0 → 1 → 2)

**Title.** Three-stage execution plan.

**Bullet text + flow chart.**

```
Stage 0. Noise ceiling estimation (NEW)
  ├ ISC across 5 subjects
  ├ Repeated-trial split-half (Horikawa test set 56 stim × 24 repeat)
  ├ Analytical noise ceiling (Lage-Castellanos 2019)
  └ Task-specific upper bound (Cowen-Keltner ICC 54%)
       ↓
  [Decision. Headroom > 0.05?]
       ↓ Yes
       
Stage 1. Brain-only direct supervised encoder ablation
  ├ E1, E2, E3, E4 의 4 encoder
  ├ Simple 34D head, no teacher, no context
  ├ Clean encoder comparison
  └ Metric. ceiling-anchored gap_filled
       ↓
       
Stage 2. P2-B distillation for context contribution
  ├ Teacher (brain + video + caption) → soft label
  ├ Student (brain only) → distillation
  ├ Context contribution = Student 의 Stage 1 baseline 의 향상 정도
  └ Inference paradigm. brain only
```

**Why this order.**
- Stage 0 의 ceiling 의 *NV3 의 채울 공간 존재 확인*. R0 의 risk 의 사전 차단.
- Stage 1 의 *encoder 효과 의 깨끗 한 측정*. distillation 없는 brain only 의 fair 비교.
- Stage 2 의 *context 효과 의 별도 측정*. encoder + context 의 *결과 귀속 의 separation*.

**Speaker note.**
> "Three stage 의 execution. Stage 0 의 noise ceiling 의 사전 측정. Stage 1 의 brain-only encoder 의 fair 비교. Stage 2 의 distillation 의 context contribution. 각 단계 의 결과 귀속 의 separation."

---

## SLIDE 13. Pre-registered success criterion

**Title.** Pre-registered success criterion (cherry-pick 회피).

**Bullet text + formula.**

```
Primary metric (ceiling-anchored).

  gap_filled = (best_encoder_brainonly - ridge_baseline) /
               (noise_ceiling - ridge_baseline)

Pre-registered Case I / II / III (Stage 0 의 결과 의 분기).

  Case I.   noise_ceiling - ridge < 0.05
            → R0 의 실현. Framework 의 reframing.
            → Paper 의 "Brain 신호 의 fundamental ceiling 의 demonstration".
            
  Case II.  noise_ceiling - ridge = 0.05-0.15
            → Narrow headroom. Stage 1 의 결과 의 careful 평가.
            → Stage 2 의 진행 의 결정.
            
  Case III. noise_ceiling - ridge > 0.15
            → Wide headroom. NV3 의 main test 의 정상 진행.
            → Stage 1 + Stage 2 의 sequential.

High-D structure preservation (1차 지표, not absolute accuracy).
  ├ Per-emotion correlation
  ├ Rare-emotion recovery
  ├ Inter-dimension correlation preservation
  └ Dimension compression curve
```

**Speaker note.**
> "Pre-registered success criterion 의 정의. cherry-pick 회피. Stage 0 의 ceiling 의 결과 의 3 case 의 사전 분기. 1차 지표 = absolute accuracy 가 아닌 high-D structure 의 preservation."

---

## SLIDE 14. Evaluation framework

**Title.** Evaluation framework.

**Bullet text + table.**

| Component | Method | Reference |
|---|---|---|
| Baseline ladder | chance + ROI ridge + frozen BFM + per-modality + joint fusion | Phase 1 + new measurement |
| Modular encoder ablation | E1-E4 × 4 task definition matrix | 1 단계 의 main |
| Modality variance partitioning | brain / video / caption / joint 의 7 condition | 2 단계 의 main |
| Noise ceiling anchor | ISC + repeated-trial + analytical (Lage-Castellanos) | 0 단계 |
| Behavioral-brain dissociation | semantic (Tang/Huth) vs affect 의 same architecture | dissociation analysis |
| Cross-subject LOSO | 5-fold by subject | transfer |
| Cross-cohort (stretch) | Horikawa → Emo-FilM | external validation |

**Speaker note.**
> "Evaluation framework 의 7 component. 각 component 의 *spine question 의 sub-question 의 1:1 답*."

---

## SLIDE 15. Risk + mitigations (R0, R1, R2)

**Title.** Pre-registered risks + mitigations.

**Bullet text + table.**

| Risk | Description | Prior probability | Mitigation |
|---|---|---|---|
| **R0** | Noise ceiling 자체 가 ridge 의 근처. NV3 의 채울 공간 없 음. | **High** (Phase 1 + D1 evidence) | Stage 0 의 사전 측정. Case I 면 framework reframing. |
| R1 | Stage 1 의 brain-only direct supervised 의 D1 박살 의 reproduce. | Medium | Setup 의 정정 (token output 폐기 + simple head). |
| R2 | Stage 2 의 distillation 의 boost 의 unproven. Cross-modal large-gap distillation = boost 약. | Medium-High | Negative outcome 의 *honest finding* 의 framing. Transfer gap 분석 의 의의 evidence. |

**Negative outcome publishability spec.**
- Negative ≠ failure. "왜 negative" 의 *explanation* 의 의무.
- Variance partitioning of teacher's accuracy by modality unique contribution.
- Transfer gap analysis vs noise ceiling.

**Speaker note.**
> "3 risk 의 사전 인정. R0 가 가장 fundamental. Stage 0 의 결과 가 R0 의 의 test. Negative outcome 도 *honest explanation* 의 publishable."

---

## SLIDE 16. Related work + EmoMind positioning

**Title.** Related work + nearest competitor positioning.

**Bullet text.**

- **Brain-to-text decoding.**
  - Tang & Huth 2023. semantic continuous reconstruction (Nat Neurosci).
  - MindCaptioning (Horikawa 2024, Sci Adv). brain → caption.
  - UMBRAE (Xia 2024, ECCV). cross-subject multimodal.
  - MindLLM (Qiu 2025, ICML). subject-agnostic LLM decoder.
- **Brain emotion decoding.**
  - Cowen-Keltner 2017 PNAS. emotion taxonomy.
  - Horikawa 2020 iScience. 27-emotion brain decoding.
  - EmoMind (Mohammed 2026, arXiv 2605.16739v2, NeurIPS 2026 submission). brain → affective caption.
- **fMRI foundation model.**
  - Brain-JEPA, SwiFT, NeuroSTORM (rsfMRI pretrain).
  - fMRI-LM (Wei 2026, arXiv 2511.21760).

**EmoMind positioning paragraph.**
> "EmoMind establishes that continuous brain-decoded affect produces cleaner caption rewriting than categorical-label prompting, evaluated on a single caption-generation task with a per-subject ridge pipeline. EmoBrain takes the diagnostic toolkit and extends it along three orthogonal dimensions the per-subject paradigm could not access. (1) multi-task prediction suite with 34D distribution, (2) modular brain encoder with fair ablation, (3) explicit noise-ceiling anchor for high-D structure preservation."

**Speaker note.**
> "Related work 의 main competitor 와 의 positioning. EmoMind 와 의 *complementary* framing."

---

## SLIDE 17. Preliminary evidence. Phase 1 result

**Title.** Preliminary evidence. Phase 1 BFM benchmark.

**Bullet text + table.**

| Encoder | V binary balAcc | V regression Pearson r |
|---|---|---|
| Chance | 0.500 | 0.000 |
| **ROI mean + Ridge (pooled)** | **0.720** | **0.416** |
| Brain-JEPA (best BFM, frozen, linear probe) | 0.677 | 0.330 |
| NeuroSTORM (linear, per-subject) | 0.668 | 0.312 |
| SwiFT_UAH_202M (linear, per-subject) | 0.665 | 0.311 |

**Key finding.** *모든 frozen BFM 의 ROI ridge baseline 의 아래*. rsfMRI BFM 의 task-fMRI naturalistic emotion transfer 의 *unproven*.

**Figure spec.**
- Bar chart. Phase 1 의 모든 BFM + Ridge + Chance 의 balAcc.

**Speaker note.**
> "Phase 1 의 evidence. 6 BFM 의 모두 의 ROI ridge baseline 의 아래. rsfMRI BFM 의 naturalistic emotion transfer 의 limit 의 직접 demonstration."

---

## SLIDE 18. Preliminary evidence. D1 BrainVLM negative result

**Title.** Preliminary evidence. D1 BrainVLM 의 token-output 의 한계.

**Bullet text + table.**

| Setup | best token_acc | actual Pearson r |
|---|---|---|
| D1 v1 (2B, lr 5e-4, epoch 50, XML token) | 0.638 | **0.035** |
| D1 v2 (4B, lr 1e-4, epoch 10) | 0.624 | **0.008** |
| D1 v2 (8B) | 0.606 (binary) | exact_match 0.03 (chance 0.25) |

**Key finding.**
- *4 backbone size 의 모두 동일 plateau*. capacity 의 issue 가 아닌 *output formulation 의 limit*.
- token_acc 0.6 = XML boilerplate 의 match 의 noise. 실제 numeric 의 prediction 거의 random.
- **함의.** Token output 의 *fundamental limit*. Direct regression head + multi-modal context 의 필요.

**Figure spec.**
- Bar chart 의 backbone size × actual Pearson r. 모든 거 의 zero 근처.

**Speaker note.**
> "D1 BrainVLM 의 token output 의 limit 의 evidence. 4 backbone 의 모두 동일 plateau. capacity 가 아닌 output formulation 의 source. 새 framework 의 distillation + 34D distribution 의 motivation."

---

## SLIDE 19. Timeline. 12-16 week build phase

**Title.** Timeline. 12-16 week build phase (S7-S11).

**Bullet text + gantt-style timeline.**

```
Stage 0 (week 0-1).      Noise ceiling estimation
                         |---|

S7 (week 1-3).           3-modality adapter + dataset
                              |-----|

S8 (week 4-6).           Multi-modal LLM fusion + trainer
                                    |-----|

S9 (week 7).             SMOKE test + launch
                                          |-|

S10 (week 8-12).         Stage 1 + Stage 2 학습
                                             |---------|

S11 (week 13-16).        Evaluation + paper draft
                                                       |--------|
```

**Open items.**
- OD-B. POYO ablation timing.
- OD-C. Emo-FilM cross-cohort.
- OD-E. Stage 4 KL target smoothing.
- OD-G. Video temporal alignment.

**Speaker note.**
> "12-16 week 의 build phase. Stage 0 의 ceiling 의 사전 측정. S7-S11 의 sequential. Open decision 4 의 진행 중 결정."

---

## SLIDE 20. Summary

**Title.** Summary.

**Bullet text.**
- **EmoBrain.** Single LLM-based foundation model 의 fine-grained emotion 의 decoding from human brain.
- **5 NV.** LLM-based decoder (NV0) + multi-modal fusion (NV1) + MindCaptioning bridge (NV2) + modular brain encoder (NV3) + 4-stage curriculum (NV4).
- **Knowledge distillation paradigm (P2-B).** Teacher 의 multi-modal 학습 → Student 의 brain-only inference.
- **Three-stage execution.** Stage 0 (ceiling) → Stage 1 (encoder ablation) → Stage 2 (context contribution).
- **Pre-registered.** ceiling-anchored gap_filled metric + Case I/II/III outcomes + R0/R1/R2 risks.
- **Primary metric.** High-D structure preservation, not absolute accuracy.

**Closing.**
> "Inference 의 brain only 의 clinical utility + multi-modal teacher 의 rich learning signal + modular encoder 의 fair ablation 의 결합. fMRI foundation model 의 emotion 분야 의 first systematic instrument."

**Speaker note.**
> "EmoBrain 의 핵심 summary. 5 NV 의 결합 + P2-B distillation + three stage execution + pre-registered criterion."

---

## SLIDE 21. Q&A

**Title.** Q&A.

**Pre-emptive Q&A 의 후보 (speaker note).**

- Q. "왜 rsfMRI BFM 의 transfer 가 안 됨?"
- A. "Resting state 의 brain signal 의 *task-fMRI 의 active emotion* 의 distribution mismatch. 우리 의 Phase 1 의 6 variant 의 evidence."

- Q. "Knowledge distillation 의 boost 의 expectation?"
- A. "Cross-modal + large modality gap (video 0.97 vs brain) 의 *structural limit*. 일반 distillation 의 5-15% prior 의 naive 적용 invalid. Negative outcome 도 *honest finding*."

- Q. "Inference 의 brain only 의 clinical utility?"
- A. "Clinical setup 의 실 사용. Video / caption 의 unavailability 의 가정. Brain 의 single source 의 emotion estimation."

- Q. "Sample size (N=5 subject) 의 statistical power?"
- A. "Subject 의 N 의 limit 의 인정. Stim 의 N (2185) 의 within-subject 의 power. paired bootstrap + cluster-robust SE. Cross-cohort (Emo-FilM 30 subj) 의 stretch."

---

## (PPT 생성 의 prompt 의 별도. PPT 의 GPT / Claude 의 직접 input 용)

> 다음 의 .md 의 slide deck (한국어 + 영어 mixed, technical academic talk, 15-25 분, 약 20-22 slide) 를 .pptx 의 PowerPoint 의 변환. 각 slide 의 layout = title + bullet text + figure (right side or below).
>
> Style.
> - Background. White or very light gray.
> - Font. Sans-serif (Arial / Helvetica / Calibri). Title 의 24-32 pt, bullet 의 18-22 pt.
> - Color. Title 의 dark blue (#1F4E79). Bullet 의 black. Highlight 의 red.
> - Figure 의 *spec* 의 placeholder ([FIGURE SPEC. ...]) 의 별도 image insertion 의 indicator.
> - Citation 의 footer 의 small (10-12 pt).
> - Speaker note 의 PowerPoint 의 notes section 의 직접 paste.
>
> ASCII diagram 의 *visual diagram* 의 변환 의 필요 (PowerPoint 의 SmartArt 또는 별도 image generation 의 합리).
>
> 표 의 *PowerPoint 의 native table* 의 변환.
>
> 모든 *slide 의 marker* (## SLIDE N) 의 new slide 의 separator.
>
> 결과 = single .pptx file. 각 slide 의 *명확 한 hierarchy* (title → bullet → figure → footer).
