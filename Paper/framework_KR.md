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

### NV4. 34D independent emotion regression + practical curriculum (2026-06-30 재정의)

Cowen-Keltner 34 category 를 서로 경쟁 하지 않는 독립 점수 로 output. 34D linear regression head, per-emotion MSE loss, z-score preprocessing (mean 0, std 1 per emotion) 필수. Softmax / sum-to-1 / KL / cross-entropy 사용 금지 (34 감정 은 distribution 이 아님, bittersweet 처럼 여러 감정 이 동시 에 높을 수 있음). 기존 work (EmoMind, Saarimäki, Horikawa) 는 single-task (caption rewriting, top-1 classification, individual category MVPA) 만. *34D independent readout on same forward pass* 의 emotion fMRI first. Distillation (Track B) 도 동일 원칙 (softmax 금지, per-emotion MSE 로 teacher 34D 재현).

**Curriculum staging 은 practical stepwise validation 으로 유지.** Curriculum (top-1 → top-2 → top-k → full 34D) 을 통해 하나 라도 학습 되는지 부터 sanity check 후 dimension 확장. 각 sub-stage 는 여전히 per-emotion independent MSE (softmax / KL 없음, subset target 만 다름). 이전 formulation 에서 폐기 된 것 은 "softmax head + KL divergence + class weighting" 이지 stage 진행 자체 는 유지.

실행 구조 (계층 정리).
- **Track A. Direct supervised** (context 없음, brain-only). Track A 안 curriculum A1 → A2 → A3 → A4.
- **Track B. Distillation** (teacher context + student brain-only). Track B 안 curriculum B1 → B2 → B3 → B4.

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
| E1. Raw ROI (no pretrain, no adaptation, control) | Schaefer-400 + Tian-S3-50 의 450 region × 16 TR mean BOLD, 단순 projector | Projector 만 학습 | Cowen-Keltner 2017 MVPA, Saarimäki 2018 |
| E2. Ridge latent (task-specific, LLM pretrain 없음) | ROI BOLD → Ridge regression → low-dim embedding | Ridge 학습 | Phase 1 의 winning baseline |
| E3. BFM embedding (fMRI pretrain frozen) | Brain-JEPA / NeuroSTORM / SwiFT 의 frozen embedding (rsfMRI large-scale pretrain) | Frozen | Phase 1 (6 variant 모두 측정 됨) |
| E4. Image pretrain + fMRI fine-tune | Qwen3-VL vision encoder → D1 BrainVLM 의 fMRI fine-tune (LoRA + projector) 의 hidden state | D1 학습 시 학습, 추출 후 frozen | D1 BrainVLM v1/v2 (token output limit), 본 paper 의 new variant |

E3 와 E4 의 진짜 질문. rsfMRI 의 large-scale pretrain 의 frozen transfer 가 강한 가, image pretrain 에서 출발 해 task-specific N 으로 fMRI fine-tune 한 adaptation 이 강한 가. E4 의 label 을 "image pretrain + fMRI fine-tune" 으로 고정 (D1 의 fMRI 적응 단계 가 가려지지 않도록).

**중요. 공통 patchify frontend 없음.** ViT 계열 은 ViT patch embedding, SwiFT 는 Swin 4D window, Brain-JEPA 는 또 다른 방식 을 각자 사용. 공통 인 것 은 결과 로 brain token 이 나온다 는 사실 뿐. 진짜 변수 는 사전 학습 유무 와 fMRI 적응 설계.

**Encoder 순위 자체 는 spine result 가 아님.** Framework (multi-modal 학습 + brain-only 추론 비대칭 + 34D 고차원 readout) 가 novelty. E1-E4 는 modularity 검증 이며 framework 가 열어주는 후속 질문.

Phase 1 의 evidence base. Frozen BFM (E3) < Ridge baseline (E2). D1 v1/v2 의 evidence base. Trained VLM token output (E4 의 token-output variant) < Ridge baseline (E2). 본 paper 의 new test. E4 의 hidden-state output variant + multi-modal fusion + curriculum 의 condition 에서 ranking 이 어떻게 바뀌 는지.

각 encoder × 4 task definition (Stage 1-4) = 16 cell 의 fair comparison matrix.

---

## Multi-modal fusion

### Token 의 concatenation

```
[brain_tokens (E_var)] | [video_tokens (V_enc)] | [human_caption_tokens] | [model_caption_tokens] | [instruction_tokens]
```

Brain encoder variant 에 따라 brain token 의 수 가 가변. Video encoder 의 frame downsample 후 token 수 ~256. Human caption ~ 50 token, model caption ~ 50 token. Instruction ~ 20 token (stage-specific task tag).

**Token 순서 (2026-07-02 implementation_spec 반영).**

Teacher.
```
[video_tokens (V_enc)] | [Caption field] | [brain_tokens (E_var)] | [Question field]
```

Student.
```
[brain_tokens (E_var)] | [Question field]
```

Video 를 앞 에 두어 시각 context anchor, brain 을 Question 직전 에 두어 마지막 hidden state 가 brain 신호 를 반영. Student 는 video / caption 없이 brain + Question 만. 이전 default (`brain → video → caption → instruction`) 는 폐기.

각 modality 의 token 앞 에 modality 의 special token (`<BRAIN>`, `<VIDEO>`, `<CAPTION>`, `<TASK>`) 의 attach 로 LLM 이 modality boundary 를 학습.

### Prompt 의 caption field 와 question field

Prompt 는 두 slot 으로 구성. Caption field 와 question field.

- **Caption field**. 매 sample 마다 달라지는 자연어 서술. MindCaptioning human caption (main) + 우리 model caption (parallel). Student 학습 시 확률적 dropout.
- **Question field**. 모든 sample 에서 동일한 fixed 문자열 (task instruction + 34-category inventory). 매 sample 이 같으므로 question 자체 는 label 을 구별 할 shortcut 이 없음.
- **의미**. 진짜 shortcut 위험 은 question 이 아니라 caption 이 brain 을 대신 하는 경로. 그래서 caption 만 dropout, question 은 항상 유지.

### Teacher 와 student 의 prompt 비대칭 + caption dropout

Teacher (학습) 와 student (추론) 의 prompt 구조 가 다름. 방치 하면 distribution shift 로 student 추론 성능 저하.

| 시점 | Prompt 구조 | 벡터 입력 |
|------|-------------|-----------|
| 학습 (teacher) | caption field + question field | brain + video |
| 학습 (student) | question field, caption 은 확률적 dropout | brain (일부 배치 에서 video 도) |
| 추론 (student) | question field only | brain only |

Caption dropout 이 두 문제 를 동시 해결. (1) Student 가 caption 없는 prompt 에 미리 익숙 해짐, (2) Student 가 caption 을 못 기대 하게 되어 brain-only 신호 를 강제 학습. Dropout 확률 은 open decision (OD-P, 0.5 / 0.7 / 0.9 grid 후 결정).

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

## 34D independent emotion regression (NV4, 2026-06-30 재정의)

### 정답 형식

- Horikawa Cowen-Keltner rating. 영상 당 34 개 감정 을 1-9 Likert 로 rating. 각 감정 은 독립 rating.
- Raw target `y ∈ R^34`, 각 원소 = rater 평균 rating (1-9 unnormalized).
- 34 감정 은 서로 경쟁 하지 않음. Bittersweet 처럼 기쁨 과 슬픔 이 둘 다 높을 수 있음. → distribution 아님, softmax / sum-to-1 금지.

### 필수 전처리. per-emotion z-score

```
z_k = (y_k - mean_k) / std_k     for each emotion k = 1..34
```

Mean 과 std 는 training set 에서 감정 별 로 계산. Test set 에 fit 하지 않음. z-score 안 하면 큰 값 감정 이 loss 를 지배 → 드문 감정 무시. Rare-emotion recovery 를 primary metric 으로 둔 이상 필수.

### Loss. Per-emotion MSE (subset sum, curriculum stage 별)

```
L_main(pred, target; A) = sum_{k ∈ A} (pred_k - target_k)^2
```

`A` = 해당 curriculum stage 의 active target subset. 원리 는 항상 per-emotion independent MSE, stage 별 로 A 의 크기 만 다름. Softmax / KL / cross-entropy / multi-label BCE 사용 금지. Class weighting 불필요 (z-score 가 이미 균등 가중).

**Curriculum stage 별 A**.

| Stage | Active target A (per stimulus) | Loss size | Rationale |
|-------|-------------------------------|-----------|-----------|
| 1 (top-1) | 자극 별 rating 최고 감정 1 개 | 1 항 | 감정 하나 라도 학습 되는지 sanity |
| 2 (top-2) | 자극 별 rating 상위 2 | 2 항 | Mixed emotion 학습 되는지 |
| 3 (top-k) | 자극 별 rating > threshold, 평균 5-8 개 | 가변 | Sparse profile |
| 4 (full 34D) | 34 개 전부 | 34 항 | 최종 formulation |

Stage 1-3 의 non-active 감정 은 loss 계산 에서 masked (gradient 없음). Prediction head 는 항상 34-dim 유지. Stage 4 (full 34D) 가 안정 적 으로 실행 되면 향후 curriculum 없이 direct 34D 로 통합 가능.

### Distillation loss (Stage 2 에서 얹음)

Teacher soft label 도 34D 독립 점수 로 caching. Student 가 teacher 34D 를 MSE 로 재현.

```
L_distill(student_pred, teacher_pred) = sum_{k=1..34} (student_pred_k - teacher_pred_k)^2
```

Total loss = L_main + λ × L_distill (λ = 0.5 / 1.0 / 2.0 grid, S9 후 결정).

### Optional brain-reconstruction auxiliary

Brain encoder 의 trained variant (E4) 의 경우 brain token → reconstructed BOLD 의 auxiliary task. Brain signal 의 information preservation 의 regularizer. λ_recon = 0.1 (S9 smoke 후 결정).

### Loss ≠ metric

Loss (MSE) 는 학습 을 굴리는 연료. Metric 은 결과 를 채점 하는 성적표. Headline metric 은 개별 감정 점수 정확도 가 아니라 영상 하나 에 대한 34 개 숫자 의 전체 profile shape 이 정답 profile 과 닮았는지 (§Evaluation).

### 이전 formulation 의 폐기 부분 vs 유지 부분

**폐기 (2026-06-30)**.
- Softmax head + KL divergence with 34D distribution target (34D 를 probability distribution 으로 오해).
- Class weighting (inverse frequency) (z-score 가 이미 균등 가중).
- Stage 4 target = rater empirical distribution (sum-to-1).

**유지**.
- Curriculum staging (top-1 → top-2 → top-k → full 34D) 자체 는 practical stepwise validation tool 로 유지.
- Stage 진행 시 checkpoint 의 weight inheritance.

실행 계층 은 (Track A direct / Track B distillation) × (curriculum sub-stage 1-4) 의 2-level 구조 로 정리 (Two-stage execution section).

---

## Training paradigm (2026-06-30 late-3 lock)

Training paradigm 의 결정. P2-A (random modality dropout, **teacher side**), P2-B (knowledge distillation), P2-C (auxiliary alignment) 중에서 다음과 같이 lock. 이전 lock (P2-B main + KL / cross-entropy + student-side dropout) 은 (a) NV4 재정의 로 KL 폐기, (b) red-team recommendation 18 에 따라 modality dropout 을 teacher 로 이동 하여 정정.

### P2-B knowledge distillation 이 본명 (main)

Teacher 와 student 의 두 단계 학습. Loss 는 모두 per-emotion MSE (§NV4, softmax / KL / CE 금지).

- **Teacher**. Brain + video + caption 의 3-modality 로 학습. Backbone = Qwen3-VL + LoRA-A. Loss = subset per-emotion MSE (curriculum stage 별). **Teacher 학습 중 P2-A modality dropout (video / caption 을 random 확률 로 mask + padding, p=0.3 each)** 적용 → soft label 이 다양한 modality 조합 에서 생성 → student 의 inference-time OOD 완화.
- **Student**. Brain-only 입력 만. 같은 Qwen3-VL backbone + LoRA-B (LoRA weight 만 분리, backbone 공유). Loss = `L_main (subset MSE on z-scored target) + λ × L_distill (subset MSE on teacher 34D)`. Softmax / KL / CE 사용 금지.
- **Soft label caching**. Teacher 의 convergence 후 각 (brain, video, caption) tuple 의 34D raw score (softmax 없음) 을 caching. Student 학습 시 teacher forward 불필요.

핵심 leakage 차단 mechanism. Student 가 video 의 raw feature 를 직접 보지 않고 teacher 의 34D 출력 만 본다. Context 의 도움 이 정답 에 가까운 34D score 형태 로 전달, brain 이 video 를 흉내 내는 통로 가 원천 차단.

구현 cost. Teacher 와 student 가 같은 backbone 공유 + LoRA 만 분리 → 두 model 동시 hosting 의 부담 없음. Teacher 는 한 번 학습 후 soft label cache → student 학습 cost 가 단일 model 과 유사.

### P2-A teacher-side modality dropout (P2-B 안에 통합)

**Red-team correction (2026-06-30 late-3)**. 이전 spec 에서 student 에 dropout 을 두었 던 것 은 잘못. Student 는 항상 brain-only 이므로 modality dropout 이 무의미. Modality dropout 은 teacher 에 위치 해야 (a) teacher 가 다양한 modality 조합 에서 soft label 을 생성, (b) student 가 teacher 의 다양성 을 흡수 하여 inference-time distribution 이 학습 시 이미 노출 됨.

- Teacher 학습 시 매 step 마다 video / caption 을 각각 확률 p=0.3 (grid 0.1 / 0.3 / 0.5) 으로 mask + padding (같은 position 유지).
- Student 는 modality dropout 없음. Brain-only + caption dropout (§7.6) 은 유지 (student prompt shift 완화 용).

### P2-C alignment 는 제외 (excluded)

Structural conflict 으로 exclude.
- P2-A teacher dropout = teacher 가 video 에만 기대지 않도록 만드는 장치.
- P2-C alignment = brain representation 을 video representation 에 가깝게 당기는 장치.
- 방향 의 정반대.

Phase 1 의 video 의 0.97 dominance (CLIP video probe 의 valence AUROC) 의 상황 에서 brain 을 video 에 정렬 → brain encoder 가 video 흉내 의 표현 으로 수렴 → 입력 에서 막은 leakage 가 representation 의 정렬 로 되돌아 옴. Brain 이 emotion 을 담고 있음 을 보이는 것 이 목표 인데 P2-C 는 brain 을 video 의 그림자 로 만드는 가장 위험한 장치. 향후 video 가 약한 modality 의 setting 에서 재고.

### Sanity comparison (red-team recommended)

Student-from-teacher (P2-B) vs student-from-hard-label (Track A A4) 을 같은 brain-only input 으로 비교. 만약 *tie within noise* 면 distillation 이 overhead 로 판정, P2-B 자체 를 재고.

---

## Two-stage execution (2026-06-30 lock)

### Stage 0. Noise ceiling estimation (Stage 1 의 전)

목적. Encoder 의 competition 이 *의미 있는 headroom* 위 에서 진행 되는지 의 pre-check. R0 risk (noise ceiling 자체 가 낮음) 의 직접 test.

4 의 estimator.
- **ISC (Inter-Subject Correlation).** 5 subject 의 brain response 의 cross-subject correlation. 같은 stimulus 의 brain signal 의 *consistency* 의 upper bound estimator.
- **Repeated-trial split-half reliability.** Horikawa test set 의 56 stim × 24 repeat 의 split-half correlation. Within-subject 의 *signal vs noise* ratio.
- **Analytical noise ceiling (Lage-Castellanos 2019 formula).** PLoS Comp Bio 2019, DOI 10.1371/journal.pcbi.1006397. Signal variance estimation 의 analytical upper bound.
- **Task-specific upper bound.** Cowen-Keltner 의 ICC 0.54 = 34D self-report rating 의 theoretical max.

이 4 의 consensus 가 noise ceiling. 그 위 에서 ridge baseline 의 위치 가 headroom 의 width.

Naming 정리. Track A / Track B (상위) 와 curriculum sub-stage (하위) 를 구분.

### Track A. Brain-only direct supervised (E1-E4 의 encoder ablation)

Teacher 없음, context 없음. Brain encoder E1-E4 를 brain-only 입력 으로 학습. Loss = subset per-emotion MSE (curriculum stage 별), z-score preprocessing 후 학습.

Curriculum sub-stage.
- **A1**. Top-1 subset MSE. 자극 별 1 개 감정 만 target. Sanity.
- **A2**. Top-2 subset MSE.
- **A3**. Top-k subset MSE (k 가변, rating threshold 기반).
- **A4**. Full 34D independent MSE. 최종 target.

Leakage 위험 원천 차단, encoder ranking 가 가장 깨끗. Track A 만 으로 발표 가능 한 결과 (A4 결과 를 gap_filled 계산 base 로).

### Track B. P2-B distillation (context contribution 의 측정)

Track A 의 best encoder 위 에 P2-B distillation 을 layered. Teacher (brain+video+caption) 도 curriculum B1 → B4 순차. 각 stage 의 teacher 34D soft label caching 후 student (brain-only) 가 MSE 로 재현.

Teacher 의 context 가 student 의 brain-only 성능 을 끌어 올리는지 의 *별도* 질문. Encoder 효과 (Track A) 와 context 효과 (Track A → Track B delta) 의 귀속 분리.

---

## Evaluation framework

### Stage 0 noise ceiling estimation (Stage 1 전, ceiling-anchored framing)

Stage 0 의 4 estimator (ISC + split-half + analytical + theoretical) 의 consensus 가 noise ceiling 으로 lock. Ridge baseline 의 위치 가 headroom 의 width 를 결정.

### Pre-registered success criterion (ceiling-anchored gap_filled)

평가 의 primary criterion. Ridge 를 "넘어야 할 floor" 가 아닌 *sanity-check reference* 로 reframe. 진짜 질문 은 ridge 와 noise ceiling 사이 의 *gap 의 얼마 만큼* 을 best encoder 가 채우는 가.

```
gap_filled = (best_encoder_brainonly_accuracy - ridge_accuracy) / (noise_ceiling - ridge_accuracy)
```

Pre-registered case 의 3 분기.
- **Case I. noise_ceiling - ridge < 0.05.** R0 realized. Headroom 자체 가 너무 좁아 encoder 의 competition 무의미. Framework 의 reframing 필요. Negative outcome 도 R0 의 실증 으로 publishable.
- **Case II. noise_ceiling - ridge = 0.05 - 0.15.** Narrow headroom. Encoder 의 competition 진행 하되 effect size 의 보고 시 reservation 명시.
- **Case III. noise_ceiling - ridge > 0.15.** Wide headroom. Encoder 의 competition 정상 진행, gap_filled 의 ranking 이 main result.

이 criterion 은 학습 시작 *전* 에 lock. 결과 의 본 후 의 post-hoc threshold reframing 금지.

### Primary metric. Per-stimulus 34D profile shape similarity (headline)

Loss (MSE) 는 학습 을 굴리는 연료, metric 은 결과 를 채점 하는 성적표. Headline metric 은 개별 감정 점수 정확도 가 아니라 영상 하나 에 대한 34 개 숫자 의 전체 profile shape 이 정답 profile 과 닮았는지.

- **Per-clip 34D profile correlation. Pearson r 과 Spearman ρ 둘 다** (implementation_spec §9-1). Predicted 34D vector vs target 34D vector, test clip 마다 계산 후 mean. 두 지표 를 함께 보고 하여 rank 안정성 검증.
- **Interpretation**. "이 영상 은 기쁨 과 향수 가 높고 공포 는 낮다" 라는 윤곽 을 맞히는 것 이 목표. 개별 숫자 를 조금 틀려도 profile shape 이 닮았 으면 성공.

### Primary metric (부가). High-D structure preservation

34D Cowen-Keltner profile 의 *고차원 구조 보존* 이 1차 지표. Ridge 는 차원 별 독립 선형 회귀 라 이 고차원 구조 를 구조적 으로 잡지 못함. Framework 가 그것 을 잡으면 그것 이 ridge 가 못 하는 것 을 한다 는 novelty 의 실증.

4 의 metric.
- **Per-emotion correlation.** 34 의 category 각각 의 prediction-target Pearson r. Distribution 의 각 dimension 의 fidelity.
- **Rare-emotion recovery.** Frequency-imbalance 하 의 rare category (예. "embarrassment", "guilt") 의 recovery rate. Ridge 의 inverse-frequency weighting 의 한계 의 측정.
- **Inter-dimension correlation preservation.** Predicted 34D 의 dimension 간 correlation matrix 가 target 의 correlation matrix 와 의 Frobenius norm. Dimension 간 dependency 의 보존.
- **Dimension compression curve.** Output 또는 brain-aligned subspace 를 k 차원 으로 줄이며 성능 저하 측정. Framework 의 이득 이 *저차원 모델 이 잃는 차원* 에 집중 되는지 의 정량.

절대 accuracy (top-1 acc 등) 은 secondary. 어려운 34D task 에서 ridge 든 framework 든 점수 가 낮게 나올 수 있고, 거기 에서 의 몇 점 차이 는 본질 아님.

### Ridge baseline 의 reframing

Ridge 0.72 (Phase 1 의 V binary balAcc) 는 valence 이진 의 쉬운 task 의 값. 우리 34D task 와 *같은 자 위 에 있지 않음*. "0.72 를 넘어라" 의 비교 자체 가 성립 안 함.

Ridge 의 새 역할.
- *Sanity-check reference* on same 34D task.
- *고차원 구조 의 dissociation evidence*. Ridge 가 차원 독립 이라 못 잡는 구조 를 framework 가 잡는지 의 reference.
- *Not a floor to beat*. 절대 점수 의 우열 의 비교 가 main 이 아님.

### Negative outcome 의 reporting (publishability spec)

Distillation 의 boost 가 near-zero 의 가능성 (cross-modal large-gap distillation 의 known difficulty). Negative outcome 의 publishability 의 spec.

요구 사항.
- **Variance partitioning.** Teacher 의 accuracy 를 modality (brain / video / caption) 의 unique contribution 으로 decompose. Teacher 자체 의 video 의존 비율 의 정량.
- **Transfer gap analysis vs noise ceiling.** Student 의 brain-only accuracy 와 teacher 의 brain-only accuracy 의 gap 을 noise ceiling 대비 비율 로 보고. Transfer gap 의 nature (capacity vs information loss).

Negative outcome 의 단독 보고 (= "distillation 의 효과 없음") 금지. 위 두 분석 의 *explanation* 의 동반 이 publishability 의 minimum.

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

### Cross-subject external test (MindCaptioning, 2026-07-02 정정)

**중요 caveat.** Cross-subject 이지만 cross-stimulus 아님.

- MindCaptioning (Horikawa 2024 Science Advances) = **6 subject × 약 2108 clip**, 중립 caption. Horikawa 2020 (5 subj) 과 subject 가 겹치지 않으므로 cross-subject.
- **그러나 stimulus 는 Cowen 계열 과 상당 부분 겹침** → cross-stimulus 아님.
- **리포트 필수 caveat**. 평가 리포트 마다 "cross-subject external test, NOT cross-stimulus" 를 명시 출력. Cross-subject 를 cross-stimulus 로 서술 하면 over-claim.
- 절차. MindCaptioning clip ↔ Cowen clip 대응 표 → 겹치는 clip 에만 Cowen 34D 라벨 매핑 → 겹치지 않는 clip 제외 (제외 수 로그 필수) → train 통계 로 z-score (test 통계 사용 금지).

Cross-stimulus 평가 는 별도. Horikawa 내부 held-out stimuli split (config `data.holdout_stimuli`) 의 slot.

### Cross-cohort stretch (Emo-FilM)

Emo-FilM cross-cohort evaluation. EmoBrain 학습 (Horikawa 5 subj) 후 Emo-FilM 의 zero-shot or light-finetune. Emo-FilM 다운로드 + Cowen 34 schema mapping 이 prerequisite. 성공 시 cohort-invariant brain affect code 의 evidence. 실패 시 cohort-specific factor 의 boundary 정의.

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

### SC6. Ceiling-anchored gap_filled (pre-registered 2026-06-30)

Stage 0 의 noise ceiling estimation 후 의 pre-registered criterion. Best brain-only encoder (Stage 1 의 winner) 의 accuracy 와 ridge baseline 의 gap 이 noise_ceiling - ridge 의 fraction 으로 정의 되는 gap_filled.

```
gap_filled = (best_encoder_brainonly - ridge) / (noise_ceiling - ridge)
```

Pre-registered case 의 3 분기.
- **Case I. noise_ceiling - ridge < 0.05.** R0 realized. Framework 의 reframing 필요. Negative outcome 도 R0 의 실증 으로 publishable.
- **Case II. noise_ceiling - ridge = 0.05 - 0.15.** Narrow headroom. Encoder 의 competition 진행 하되 reservation 명시.
- **Case III. noise_ceiling - ridge > 0.15.** Wide headroom. Encoder 의 competition 정상, gap_filled 의 ranking 이 main result.

Null result 의 interpretation. gap_filled ≤ 0 (best encoder 가 ridge 못 넘음) 의 경우 = framework 의 *fine-grained gain* 없음. Ridge 가 차원 독립 으로 도 sufficient 의 finding. Modality fusion (Stage 2) 의 추가 contribution 이 의미 있는 lift 의 last 가능성.

---

## Caption-video overlap 대응 (2026-06-30 추가)

Caption 과 video 는 같은 사건 을 서로 다른 추상화 수준 에서 기술 → 일부 겹침 은 구조적 이고 결함 아님. Video 의 고유 기여 는 얼굴 표정 / 움직임 / 구도 같은 저수준 지각. Caption 의 고유 기여 는 인물 관계 / 사회적 상황 같은 고차 의미.

**진짜 리스크**. Caption 의 시각 관련 성분 이 이미 강한 video 와 합쳐져 teacher 가 시각 으로 과결 을 내고, brain 고유 기여 가 학습 신호 에서 지워지는 것. VA binary 에서 video probe AUROC 0.97 vs ROI ridge 0.72 는 이 지배 가 실제 로 관측 됨 을 보인 증거.

**검증 절차**.
1. **Video 를 caption 위 에 residualize**. Caption embedding 에서 video 로 예측 가능 한 성분 을 linear regression 으로 제거 → 잔차 만 caption slot 에 입력. 잔차 조건 성능 이 원본 caption 조건 과 유사 하면 caption 고유 기여 살아 있음, 크게 떨어지면 겹침 이 지배.
2. **Modality ablation**. Full / no-caption / no-video / brain-only 의 4 조건 학습. Caption 을 뺐을 때 gap_filled 감소 폭 = caption 의 고유 기여.
3. **초기 layer 하강 회피**. 겹침 을 줄인 다고 video 를 low-level layer embedding (예. VGG19 초기) 으로 내리면 감정 관련 시각 정보 자체 를 잃음. CCN 결과 (brain-aligned subspace 는 V-JEPA2 마지막 hidden state 에서 나옴, 저수준 residualize 후 에도 categorical 연속 성 유지) 가 이 결정 을 뒷받침. 고차 layer 유지 + 잔차 분석 이 옳은 방향.

**Caption 중립성 검증**. MindCaptioning 은 감정 / 해석 없는 중립 서술 로 규정. 그러나 규정 인용 만 으로 는 부족. Caption sample 을 실제 로 읽어 감정 단어 / 명시적 해석 부여 를 표본 검증 (`project/shared/code/tools/verify_caption_neutrality.py`, S7 에서 작성 예정).

---

## Risks

### R0. Noise ceiling 자체 가 낮음 (high prior probability, 2026-06-30 추가)

Brain signal 의 noise ceiling 자체 가 ridge 와 가까워 어떤 encoder 도 의미 있는 lift 못 만드는 risk. Encoder 의 choice 자체 가 moot.

High prior probability 의 근거.
- Phase 1 의 evidence. 6 BFM variant 모두 ROI ridge 못 넘음. Encoder 의 capacity 추가 가 의미 있는 lift 안 만듦 의 reproducible evidence.
- D1 v1/v2 의 evidence. 3 backbone size (2B / 4B / 8B) 의 plateau. Capacity 가 issue 아닌 ceiling 자체 의 한계 의심.
- Cowen-Keltner ICC 0.54. Self-report 의 inter-rater agreement 자체 가 절반. Brain decoding 의 absolute ceiling 이 0.54.

Stage 0 의 noise ceiling estimation 이 R0 의 직접 test. Case I 의 outcome = R0 의 실증 = framework 의 reframing 또는 alternative path 의 trigger.

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
