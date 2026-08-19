> ⚠️ **ARCHIVED — 역사 기록. 현행 문서가 아니다.**
> 현행 논증 = `docs/paper_logic_merged.md` (대전제 · RQ · 가설 H1–H4). 운영 규칙 = `CLAUDE.md`.
>
> 아래 내용 중 다음은 **뒤집혔다.** (a) Qwen3-VL 등 LLM backbone 사용 — 금지.
> (b) open-vocabulary / cross-taxonomy 전이를 headline novelty 로 삼는 프레임 — 폐기.
> (c) 학습에 없던 감정 zero-shot — 폐기(원칙적 분할 기준 없음, RQ 와 무관).
> (d) "EmoBrain 과 EmoViS 는 별도 논문 2편" — 현재는 **한 편의 논문**.
> (e) "EmoBrain 은 cortical location 을 주장하지 않는다" — 현재 **H3 이 cortical location 주장**이다.

# EmoBrain NV3 framework. Redteam Review 종합 정리

작성. 2026-06-30. 4 critic agent 의 adversarial review 전부를 한글로 정리한다.

목적. 우리 framework 의 *진짜 상태* 에 대한 honest documentation 과 12 redesign 권고의 evidence base.

대상. 사용자, 협업자, (future) paper review 의 reviewer 를 위한 self-defense reference.

---

## 0. Executive Summary

2026-06-29 NV3 framework lock 발표 후, 2026-06-30 에 4 round 의 추가 adversarial review (Architecture, Training stability, Inference paradigm, RoPE position-shift) 를 진행했다. 4 critic 모두 redesign 을 권고했다. 우리의 "framework lock" 표현이 *over-claim* 이었음을 인정한다.

핵심 결론.

- **Methodology 와 evaluation framework 만 lock**. Architecture spec, training paradigm, inference paradigm 은 *deeper redesign 이 필요*하다.
- 4 critic 의 *수렴* = 7 critical blocker + 12 redesign 권고.
- Framework 의 *현재 state* 는 다른 사람에게 보여 줄 *준비가 안 됐다*. 12 redesign 적용 후 *2 차 review 가 필요*하다.
- 우리의 *진짜 next step* = engineering sprint (1-2 주), validation experiment (mandatory), factored sweep, dual main branch.

---

## 1. Background. 4 Critic Agent 의 spawn

### 1.1 동기

사용자가 2026-06-30 에 제기한 의문.

> "우리가 model architecture 를 다듬는 중인데 LOSO evaluation detail 이 갑자기 나옴. 우선 순위가 혼란스럽다. 지금 model architecture 가 확정된 것인가?"

이 의문은 정당하다. Framework 의 *high-level spec* 은 lock 됐지만 *implementation detail* 의 상당 부분이 unresolved 상태였다. 그래서 진짜 architecture-level redteam 을 spawn 했다.

### 1.2 4 Critic 의 spawn

| Critic | 영역 | Approach |
|---|---|---|
| Architecture critic | Token shape, memory, integration, grid size | Mode 2 adversarial |
| Training stability critic | Mode collapse, KL stability, curriculum transition | Adversarial |
| Inference paradigm critic | OOD risk, cross-modal distillation limit | Adversarial |
| RoPE position-shift critic | Prompt position drift, attention regime | Specific deep dive |

모두 *parallel background spawn*. 결과는 *수렴 evaluation* 으로 정리한다.

---

## 2. Critic 1. Architecture Critic 상세

### 2.1 Verdict

**"Architecture has fundamental issues requiring redesign in specific places, plus fixable gaps elsewhere."**

4 blocker + 1 high (fixable) + 1 medium-high.

### 2.2 8 concern 상세

#### C1. Token shape unification 미정 (BLOCKER)

E1 (~900 token) vs E2 (~50-100 token) vs E3 (~256 token, variable) vs E4 (~900 token). 4 variant 의 *token 수가 wildly heterogeneous* 하다. 3 option 각자에 문제가 있다.

- **Padding option.** E2 / E3 를 900 token 으로 pad 하고 attention mask 적용. 단점. E2/E3 의 compute 중 89% 가 낭비된다. NV3 ablation 의 *fairness* 가 distortion 된다 (E2 vs E1 의 "fewer token 으로 얻는 efficiency" 의의가 사라진다).
- **Project to fixed N option.** Perceiver resampler 로 256 token 으로 통일. 단점. Resampler 가 *learnable confounder* 가 된다. E3 의 BFM feature 자체의 효과와 Resampler 의 smoothing effect 가 *분리되지 않는다*.
- **Variable-length per variant.** 단점. Loss weight, batch packing, gradient norm 이 *differ across runs* 한다. Fair comparison 의 *identical compute budget* 가정을 잃는다.

**Recommended fix.** Perceiver-style cross-attention resampler 로 fixed 256 token 통일. 모든 E1-E4 가 동일 shape. Resampler 의 *per-variant independent weight* 가 share 보다 capacity matched. 단 *confound 를 명시적으로 documentation 해야 한다*.

#### C2. Memory budget OOM risk (BLOCKER)

Qwen3-VL 8B (32 layer) + N=3000 token + batch 4 + FP16.

빠른 계산.
- Self-attention activation per layer. `batch × heads × N² × bytes = 4 × 32 × 3000² × 2 = 2.3 GB per layer`.
- 32 layer = **73 GB 가 attention score 만**.
- Plus KV cache + MLP activation + optimizer state for LoRA.

Single A100 80GB 에서 *immediate OOM*. FlashAttention-2 의 도움이 있어도 *backward pass on 32-layer 8B at N=3000, batch 4* 는 tight 하다. 현실적으로 batch 1 은 *throughput killer*.

추정 throughput. Qwen3-VL 8B + N=3000 = 0.5-1.5 sec per sample on A100. 10925 trial × 4 stage × 5 epoch = 218k step. 즉 30-90 GPU-hour per single (E × V × caption) condition.

**Recommended fix.**
- Qwen3-VL 2B 또는 4B 로 ablation. 8B 는 final 1 condition 만.
- Total token hard-cap 1500. Aggressive video temporal pooling + brain token resample to ~128.
- Gradient checkpointing + DeepSpeed ZeRO-2 day 1.
- Smoke test on 1 batch on A100 80GB *before* 24-condition grid commitment.

#### C3. Dual LoRA on shared backbone (HIGH, fixable)

PEFT 의 multi-adapter 지원 (`model.add_adapter()` + `model.set_adapter()`). 단.

- Switching adapter mid-training. Teacher forward + student forward 의 sequential 진행은 fine.
- *Gradient accumulation across both in same step* 은 fragile. Base shared weight 의 unfrozen layer 에서 *gradient conflict* risk.
- Loading both at inference. `peft.PeftModel` 이 support (PEFT >= 0.7). 검증됨.
- 진짜 risk. Teacher (LoRA-A) vs student (LoRA-B) 의 *rank tuning rabbit hole*. Teacher 는 4 modality 의 more capacity 가 필요. Student 는 fewer modality 의 underfit risk at high rank.

**Recommended fix.** LoRA-A rank=32 (teacher), LoRA-B rank=16 (student). Base 는 완전 freeze. Sequential forward, teacher first (gradient detached for soft label) + student second (gradient computed).

#### C4. Brain encoder integration interface (BLOCKER)

가장 underspecified 한 부분. 3 option 각자에 consequence 가 있다.

- **Replace Qwen3-VL vision patches.** Brain token 이 video frame patch slot 자리를 차지. Pro. Qwen3-VL image-token machinery 재사용. Con. Brain 과 video 가 *same image slot 에서 competition*. 둘 다 동시에 못 들어간다.
- **Prefix tokens before text.** Brain token 을 LLM hidden_size 로 project 한 후 special token 으로 prepend. Pro. Brain 과 video 가 coexist. Con. Tokenizer 에 *new special token 추가* 가 필요하고 *cold start* (Qwen3-VL pretrain 에서 안 본 pattern).
- **Modality-specific cross-attention layer.** Brain token 이 *input sequence 에 안 들어감*. *Added cross-attention* 으로 injection. Pro. Cleanest separation. Con. *Untrained cross-attention module 추가* = LoRA 보다 much more.

E3 의 specific issue. **256-dim 의 fixed vector** 가 Qwen3-VL image projector 의 *patch embedding sequence* expectation 과 mismatch. Option.
- (a) Vector 를 tile 해서 가짜 patch sequence 생성 (semantically meaningless).
- (b) Image projector 를 bypass (E3 가 E1/E4 와 다른 integration path = ablation fairness breakdown).

**Recommended fix.** Prefix token path 채택. `<brain_start>` 와 `<brain_end>` special token 정의. E1-E4 모두 per-variant MLP 로 LLM hidden_size 로 project 후 insert. 통일된 integration interface 에서 encoder choice 만 variable.

#### C5. 4-stage curriculum 의 weight inheritance (HIGH)

Head architecture 가 stage 별로 다르다.
- Stage 1. Top-1 softmax over 34 = 34-dim logit.
- Stage 2. Top-2 sigmoid 34-dim.
- Stage 3. Top-5 k-hot 34-dim.
- Stage 4. 34-dim distribution KL.

모두 *34-dim logit head*. 구조적으로 identical. Weight inheritance 가 feasible.

만약 stage 별로 *different head* 를 의도한다면 *4 separate model 학습* 이 된다. "Curriculum" 이라는 표현이 *misnomer*.

**Recommended fix.** Single 34-dim logit head 유지하고 loss 만 stage 별로 변경 (CE on top-1 mask → BCE on top-2 mask → BCE on top-5 mask → KL on full distribution). 즉 *loss curriculum*. Weight inherited.

#### C6. Inference-time OOD from train-vs-test token-count mismatch (MEDIUM-HIGH)

Student 의 학습 = brain + prompt only (~950 token). Inference 도 동일. **Student 는 OOD 가 없다**.

단 *teacher* 학습 = 4 modality (~1200-3000 token). Teacher evaluation 은 *upper bound* 용으로 fine. 단 만약 teacher 가 deployed-in-held-out (modality missing) 상황이면 OOD.

표준 distillation 의 *teacher 에 modality dropout* (random masking of video / caption during training, p=0.3) 이 fix. 우리 spec 의 *student 에 dropout* 은 잘못. **Modality dropout 은 teacher side 에 위치해야 맞다**.

더 깊은 concern. Student 가 *never learn video/caption attention pattern*. Distilling from teacher (4 modality) = "mimic output without input". 이것이 *standard distillation 의 의도* 이지만 *soft label 이 informative 한지 여부* 가 prerequisite.

**Recommended fix.** Modality dropout 을 teacher 에 적용 (p=0.3 for video + caption each). Soft label 의 비교 test. *Student-from-teacher vs Student-from-hard-label* 을 same brain-only input 으로 비교. 만약 *tie within noise* 면 distillation 이 *overhead with no benefit*.

#### C7. Cross-product 의 NERSC limit 초과 (BLOCKER)

48 model condition × 4 stage = 192 run. 30-90 GPU-hour per run = **5700-17000 GPU-hour**. NERSC m4641 에서 *generous QoS 라 해도* 2 month 의 continuous use.

**Recommended fix.** Factored grid (cross-product 안 함).
- Phase 1. V=CLIP, caption=MindCaptioning 고정. E1-E4 sweep. 4 × 4 stage = 16 run. → Winner E*.
- Phase 2. E=E*, caption=MC 고정. V=CLIP/V-JEPA2/VideoMAE sweep. 3 × 4 = 12 run.
- Phase 3. E=E*, V=V* 고정. Caption source sweep. 2 run.
- Final. (E*, V*, caption*) 의 full 4 stage + teacher+student distillation.

총 ~30 run. ~1500-3000 GPU-hour. *Feasible*.

#### C8. "Architecture finalized" claim 이 false (BLOCKER, meta-issue)

C1, C2, C4, C5, C6 의 implementation detail 이 미정. *Engineering minutiae 가 아니라 architecture viability 를 결정하는 사항*.

"Architecture finalized" 표현은 *category error*.

**Recommended fix.** Claim 을 demote. "Methodology + evaluation framework 가 lock. Architecture spec 은 *design level*. Integration detail (brain-token entry point, token-count unification, memory budget) 은 *1-week pre-training engineering sprint* 가 필요."

### 2.3 Top 3 critical blocker (학습 시작 전에 resolve 필요)

1. **C2 (memory).** Smoke test on Qwen3-VL 2B/4B + N=1500 + batch=1 + full backward on A100 80GB. Peak memory 와 step time 측정. > 70 GB 또는 > 5 sec/step 이면 scale down.
2. **C4 (brain token entry point).** 3 option 중 1 결정 후 *one batch forward pass* 의 end-to-end run 으로 confirm.
3. **C7 (grid factoring).** 24 cross-product → 3-phase sequential sweep 으로 변경.

---

## 3. Critic 2. Training Stability Critic 상세

### 3.1 Verdict

**"Training paradigm carries high mode-collapse risk requiring redesign."**

6 redesign 필수 항목.

### 3.2 9 concern 상세

#### S1. Mode collapse 재발 risk (HIGH)

D1 v1/v2 의 token-output collapse 의 root cause = LLM head 가 *VA 4-token space 의 majority token 으로 collapse*. 즉 *brain encoder→LLM bottleneck 의 effective SNR 이 chance 수준*. 결과적으로 *decoder 가 prior (label marginal) 로 회귀*.

새 framework 의 Stage 1 에서 동일 mechanism. 34-class softmax + CE 상황에서 brain feature 가 uninformative 면 cross-entropy gradient (`p_pred - p_true`) 가 *weighted noise 만 증폭*. AdamW 의 second moment 가 noise 를 normalize 한다. 결과 = *majority class logit 이 marginal log-frequency 로 수렴하는 trivial solution*.

**Recommended fix.** Stage 0 추가. Brain-only contrastive pretraining (CLIP-style, brain vs caption embedding) 으로 *brain encoder 가 stimulus identity 를 separate 할 능력* 을 증명. Precedent. Tang et al. Nature Neuroscience 2023 (semantic decoding from fMRI) 도 *GPT prior 위에 brain→text decoder 학습 전에 brain encoder 의 semantic feature 추출 능력을 verify*.

#### S2. 34D KL 의 peaky target 의 stability (HIGH)

KL(p||q) = Σ p_i log(p_i/q_i). p 가 peaky (joy=0.7) 이면 gradient `∂KL/∂logit_j` 의 norm 이 majority class 에서 ~0.7, minority 에서 ~0.001. AdamW second moment 가 majority 쪽으로 saturate 되면서 *effective learning rate 가 minority class 에서 사실상 0*. **Stage 4 는 Stage 1 의 weighted version 일 뿐, 새 information 이 0**.

게다가 rater empirical distribution 의 N_rater (~10-20) 가 작으면 tail probability 가 noisy. KL 은 *tail noise 에 sensitive* (log term). Model 이 *noisy tail 을 fit 하다가 head pattern 을 잘못 학습*.

**Recommended fix.**
- Label smoothing. 0.9 × p_empirical + 0.1 × uniform.
- KL 대신 JS divergence (symmetric, bounded gradient).
- 또는 Stage 4 를 weighted CE on rank-k targets 로 유지하고 KL 제거. Stage 4 = "Stage 3 + soft weighting".

#### S3. Curriculum transition 의 optimizer state (MEDIUM-HIGH)

Stage 1 (single-label softmax CE) → Stage 2 (multi-label sigmoid BCE) 의 loss function 의 normalization 변화. Softmax 는 logit 간 competition. Sigmoid 는 independent.

같은 head weight 를 inherit. Stage 1 에서 majority class logit 이 매우 큰 값이면 Stage 2 의 sigmoid 에서 *majority 가 saturate to 1* + *minority gradient 가 다시 dead*.

AdamW moment 상속은 더 worse. v_t (second moment) 가 Stage 1 distribution 에 adapted 된 상태에서 Stage 2 의 *wrong-scaled update*.

**Recommended fix.**
- (a) Head re-init 또는 head reset (encoder 는 유지).
- (b) Optimizer state reset.
- (c) Lr warmup (stage 길이의 10%).
- 또는 curriculum 을 *stage 아닌 loss schedule 로 reformulate*. L = w_1(t) × CE_top1 + w_2(t) × BCE_top2 + ... 처럼 weight 만 시간에 따라 변화. Discontinuity 가 없다. Precedent. Multi-task learning literature (Kendall et al. CVPR 2018 uncertainty weighting).

#### S4. Class weighting 의 stage-specific 정의 부재 (MEDIUM)

"Top-1 frequency 기반 weighting" 은 *Stage 1 만 정의*. Stage 2 의 top-2 pair (C(34,2)=561 pair) 는 *다른 imbalance pattern*. Stage 4 의 KL 은 *class assignment 가 아닌 distribution 간 거리* 라서 class weighting 의 의의가 사라진다.

**Recommended fix.**
- Stage 4 에서 KL 사용 시. Per-class KL contribution 의 weight 를 `KL = Σ_c w_c · p_c log(p_c/q_c)` 처럼. *비표준* 이므로 명시 필요.
- 또는 §S2 의 권고로 Stage 4 redefine.

#### S5. Distillation α 미명시 (MEDIUM)

α 는 *sensitive hyperparameter*. Hinton et al. NeurIPS 2014 W 의 KD 는 same-modality teacher-student. Cross-modal 의 경우.
- Gupta et al. CVPR 2016 (RGB→Depth distillation). α=0.5 + T=4.
- Tian et al. ICLR 2020 (CRD). Contrastive distillation 으로 KL 자체를 사용하지 않음.

**Recommended fix.** α 와 T 를 *Phase 1 gate 의 일부로 명시*. 최소 {α=0.3, 0.5, 0.7} × {T=1, 4} grid sweep 의 결과 없이 본 training 진입 금지.

#### S6. Cross-modal distillation gap (HIGH, **가장 critical**)

Standard KD assumption (teacher/student same input) 이 깨진다. Student (brain only) 가 teacher (brain+video+caption) 의 soft label 을 mimic. 단 *brain signal 이 video/caption information 을 carry 하지 않으면 student 가 teacher 의 marginal label distribution 만* 학습.

= **Distillation 이 unconditional prior matching 으로 degenerate**.

문헌 evidence. Aytar et al. NeurIPS 2016 (SoundNet, video→audio distillation) = student modality 가 teacher information 의 *subset* 인지 verify.

fMRI emotion 의 경우. Brain signal 로 video pixel / caption text 를 reconstruct 한 *published evidence 가 매우 약*. Horikawa & Kamitani 2017 = *category level*, frame-level 아님.

**Recommended fix.** Distillation 전에 mutual information check. `I(brain; teacher_soft_label | ground_truth) > 0` 을 empirical 측정. 만약 brain 이 teacher soft label 중 ground truth 외 information 을 거의 못 받으면 *Distillation 이 redundant + noise만 추가*. 이 case 면 P2-B 를 drop.

#### S7. Brain reconstruction auxiliary (MEDIUM)

"Optional" 은 *결정 회피*. 두 경로 모두 문제.

**On 일 때.** 450-D ROI reconstruction loss 가 LLM hidden state 를 brain-like representation 으로 pull. 그러나 LLM 의 task 는 emotion classification. 두 objective 의 gradient 가 conflict (Sener & Koltun NeurIPS 2018 multi-task gradient conflict). Reconstruction loss weight 가 *과 큼* 이면 LLM 이 *emotion 보다 brain signal 의 nuisance variability (motion, scanner drift) 를 학습*.

**Off 일 때.** Brain encoder 의 output 이 emotion classification 에 useful 하다는 보장 없음. LLM 의 강한 prior (label marginal) 가 brain encoder gradient 를 vanish 시켜 encoder 가 *random feature 를 output*. LLM 이 prior 로 답. 이것이 **D1 v1/v2 의 collapse mechanism 과 정확히 일치**.

**Recommended fix.** Reconstruction 대신 *brain encoder output 의 contrastive loss* (different stimuli 의 brain feature 를 separate). λ_contrastive 의 ablation 으로 결정.

#### S8. N=5 statistical reality (MEDIUM, but separate)

Training stability 아닌 inference reliability 의 문제. Pooled 10925 trial 의 training 수렴은 가능해도 cross-subject generalization claim 은 5 subject 의 mean ± SE 의 reporting 에 의존.

Cohen's d 검정력 분석. 5 subject 에서 medium effect (d=0.5) 의 detection power = ~0.20. 즉 *대부분의 진짜 effect 를 못 잡음*.

**Recommended fix.** Subject 를 *random effect 로 modeling*. Linear mixed model 또는 hierarchical Bayes 로 *within-subject variance 와 between-subject variance 를 분리*. 단순 paired t-test on 5 means 는 *금지*.

#### S9. THE CRITICAL QUESTION (HIGH)

"Simpler 가 실패했는데 왜 more complex 가 성공?"

**정직한 답. 명확한 published precedent 없음.**

검색 결과.
- fMRI emotion category decoding. Kragel & LaBar Neuroimage 2015 (7 emotion, ~50% accuracy). 34-category 시도 없음.
- Cross-modal KD for fMRI. 없음 (vision-language KD 는 많지만 fMRI 는 data 부족).
- 4-stage emotion curriculum. 없음. Curriculum learning (Bengio et al. ICML 2009) = difficulty ordering 이지 *label granularity ordering* 이 아님. Label granularity curriculum 은 hierarchical classification literature (Deng et al. CVPR 2014 ImageNet hierarchy) 에 있지만 emotion 에 적용된 사례는 없음.

새 framework 의 *complexity 자체에 D1 collapse 를 해결할 mechanism 이 없음*. 해결 mechanism 후보는 (a) §S1 의 Stage 0 brain-encoder pretraining 으로 separation prior 확보, (b) §S6 의 teacher 의 additional supervision signal. 단 (b) 는 cross-modal gap 의 의문, (a) 는 현재 framework 에 *없음*.

### 3.3 Top 3 unresolved question

1. **Brain encoder 가 stimulus 간 discriminative feature 를 output 하는가?** D1 collapse 의 root cause 일 가능성. Stage 0 contrastive pretrain 없이 진입하면 v3 도 collapse. Phase 1 gate. *brain-only stimulus identity decoding accuracy ≥ chance × 5* 미달 시 STOP.

2. **Teacher soft label 의 ground truth 외 information 이 brain 으로 transfer 가능한가?** Cross-modal KD 의 의의는 `I(brain; teacher_label | gt) > 0`. 측정 안 하면 P2-B 가 *noise*.

3. **Stage transition 의 optimizer/head 상속 정책.** 명시 안 됨. Inherit-all 은 sigmoid saturation. Reset-all 은 curriculum 효과 0. *어느 weight 를 inherit, 어느 state 를 reset* 인지 명시 필수.

---

## 4. Critic 3. Inference Paradigm Critic 상세

### 4.1 Verdict

**"Inference paradigm carries fundamental cross-modal limits requiring partial redesign."**

2 critical + 4 high + 3 medium-low.

### 4.2 9 concern 상세

#### I1. Soft-label transfer 의 이론적 상한 (CRITICAL-1)

Paradigm 의 *ceiling 정의*.

Hinton 2015 KD 는 teacher 와 student 가 *same input* 이라는 가정. Soft label 이 teacher 의 confidence 구조를 전달. 단 그 confidence 는 teacher 가 본 input distribution 에 conditional.

정보 이론적으로. Teacher 의 video + caption + brain → 34D soft label 생성 = `H(emotion | V, C, B)` 의 posterior 반영. Student 가 `H(emotion | B)` 만으로 그 posterior 를 재현. 두 distribution 의 일치 = *video / caption 이 brain 에 conditionally independent 인 경우만*. 곧 *"stimulus 의 brain response 가 fully encoded"* 라는 가정. 이 가정이 참이면 처음부터 teacher 에 video / caption 을 넣을 이유가 0.

→ **Paradigm 의 motivation 과 ceiling 이 *같은 가정에 동시 의존하는 모순***.

구체적으로. Teacher 의 video 가 disambiguation (valence 가 동일한 두 emotion 의 구분) 하지만 brain 이 reflect 안 하면 student 의 soft label fit 이 brain noise 에 그 정보를 *wrong routing*. Stanton et al. 2021 "Does Knowledge Distillation Really Work?" 의 관찰과 일치.

**Validation experiment.** Teacher 의 video-only input soft label 과 brain-only input soft label 의 KL divergence. KL 이 크면 cross-modal gap 이 크고, student 가 그 gap 을 brain 만으로 못 채움. KL 이 작으면 처음부터 video 자체가 불필요.

**Redesign trigger.** KL 이 두 방향 모두 의의가 없는 영역 = distillation 포기. Brain-only end-to-end 로 가야 한다.

#### I2. Prompt position drift on RoPE backbone (CRITICAL-2)

**"Inference 가 기술적으로는 run 되지만 attention pattern 이 OOD".**

Brain token 의 position 1-900 은 invariant. 단 prompt 가 ~1180 → ~901 로 ~280 position 이동. M-RoPE 의 query-key dot product 는 *위치별 rotation*. Brain (1-900) 과 prompt (901-930) 의 attention rotation 이 학습 시의 brain (1-900) ↔ prompt (1178-1207) attention rotation 과 *다른 frequency mixing*.

학습 시 attention head 가 *"brain position 450 이 prompt position 1185 의 question word 에 attend"* 를 학습. Inference 에서 *"brain 450 ↔ prompt 905"* 로 evaluation. 이 query-key relative position 이 *학습 분포에 한 번도 등장 안 함*.

"Lost in the middle" (Liu et al. 2023, arXiv:2307.03172) = 같은 prompt 의 *위치만 변화시켜도 instruction following 이 무너짐*. EmoBrain 은 더 극단적. 학습 분포에서 prompt = *항상 후반 절대 위치*. Inference = *항상 중간*.

= **Train-test distribution mismatch 의 정의 자체**.

기술적으로는 run 됨 (shape mismatch 없음 + M-RoPE 의 length 가변 처리). 단 *attention pattern 이 OOD* 이므로 output 이 *학습 신호와 무관할 risk*.

**Validation experiment.** 학습된 model 에 (a) 학습 형태 input, (b) inference 형태 input 으로 forward 후 *prompt token 위치의 attention map (brain region 의 attention weight 분포)* 비교. 분포에 큰 차이 = OOD 확정.

**Redesign.** P2-A (modality dropout) 로 회귀. 학습 시 *random video/caption mask + padding 으로 같은 위치 유지* = prompt position 이 학습 시부터 다양해져서 inference position 이 분포 안. P2-B 의 핵심 장점 (teacher capacity) 을 일부 포기. 단 OOD 제거.

#### I3. Clinical inference distribution 미정의 (HIGH)

학습 = Horikawa 2020 의 *video-exposed brain* (passive viewing 의 fMRI). 임상 정당화 시나리오 (spontaneous emotion, imagined emotion, mood-state monitoring) 는 모두 *stimulus-evoked 가 아닌 brain state*. fMRI 문헌 기준 spontaneous vs exposed emotion 의 representational geometry 는 *일치하지 않음* (Kragel & LaBar 2014).

= **Inference distribution 이 학습 distribution 과 *다른 OOD 가 한 번 더 추가***.

Paper framing 의 "clinical use case justifies brain-only inference" 에 대해 reviewer 가 "그러면 clinical-distribution brain data 의 validation?" 이라 물으면 답 = "안 했음" = motivation 의 *무력화*.

**해결.** Clinical motivation 의 *framing 을 약화* 하거나 paragraph 한두 줄의 future work 로. Horikawa 분포 안에서 validation 완료 후 "domain transfer to clinical settings is future work" 로 명시.

#### I4. MindCaptioning bridge 가 inference 에서 vacuous (HIGH)

NV2 의 contribution = "caption 이 brain ↔ context bridge". Deployed model 의 forward graph 에는 caption node 가 *없음*. *학습 시에만 존재하고 deployed 에서 사라지는* 정직한 기술이 필요.

현재 framing 은 "brain 이 caption space 를 거쳐 emotion 으로 mapped" 처럼 들린다. 단 정확한 claim 은 "training-time auxiliary supervision via caption-derived soft labels improves brain-only emotion decoding".

= NeurIPS / Nature Comm. 류 reviewer 가 *catch*. Contribution 이 *부풀음* 이면 신뢰도가 *크게 깎인다*.

**해결.** Framing 재작성. "Caption is used during training as auxiliary modality whose information is compressed into student weights via distillation. At inference, the student model uses brain alone." 로 정직화하면 contribution 유효.

#### I5. Standard distillation diagnostic 사용 불가 (HIGH)

표준 KD 는 (teacher logit, student logit) 의 same input 비교로 distillation loss curve / agreement rate / sharpness matching. EmoBrain 은 두 model 이 *다른 input* 이라 진단 전체가 *무력화*. Student 가 "teacher 를 잘 모방" 한다는 *객관 metric 이 없다*.

가능한 우회.
1. Teacher 에 brain-only input (video/caption mask) 으로 forward = brain-only-teacher logit. Student logit 과 비교. 단 *teacher 가 학습 시 안 본 input* 이므로 teacher 자체가 OOD.
2. Held-out trial 에서 student predicted label 분포 와 teacher predicted label 분포 의 *marginal agreement*. *Trial-level matching 은 못 함*.

**Validation experiment.** Teacher 와 student 의 trial-level confusion matrix 비교. 분포가 비슷 = distillation 이 "category-level statistics" 를 잡는 약한 evidence. Trial-level mismatch = cross-modal gap 의 직접 측정.

#### I6. Backup plan 의 회귀성 (MEDIUM)

P2-B 의 inference-time OOD 가 실패. Fallback = (a) symmetric inference (4-modality input at test) = motivation 무력화 / (b) P2-A (modality dropout) = P2-B 의 차별성 무력화.

= **Paradigm 이 binary**. 작동 또는 원점.

= **Paper 의 위험이 크다**. P2-A 의 baseline 을 *미리 실험에 포함* 하면 P2-B 의 실패 시 "P2-A vs zero-shot 비교" 가 남는다. 현재 design 에서 P2-A 를 auxiliary 로 강등한 것이 *위험 분산상 의문*.

**해결.** P2-A 와 P2-B 를 *equal main experiment branch* 로. Ablation 으로 비교.

#### I7. N=5 subjects 의 통계적 floor (MEDIUM)

Cross-modal KD literature 의 5-10% boost 는 보통 ImageNet 규모 (>1M sample) 의 reporting. N=5 × 2185 stim = 10925 trial pooled 의 fMRI 에서 *same boost 의 재현 prior 가 매우 약*. fMRI 의 trial-to-trial noise SNR 이 음수에 가까워 soft label 의 fine-grained 정보가 noise 위로 떠오를 *신호 대 잡음 비가 낮음*.

구체적 risk. Student 가 distillation loss 를 minimize 하기 위해 *brain signal 학습이 아닌 prompt token 의 prior label 분포 학습 (degenerate)* 으로 갈 가능성. Representation probing 으로만 확인 가능.

**Validation.** Trained student 에 *brain token 의 random shuffle 또는 zero-mask input* 으로 inference. Accuracy 가 거의 안 떨어짐 = student 가 *brain 을 사용 안 하고 prompt prior 만 사용*. Hewitt & Manning 2019 probing 류 진단의 변형.

#### I8. Teacher 의 자체 OOD (MEDIUM)

Teacher 학습 = brain + video + caption + prompt. 단 N=5 의 brain 만으로 teacher 가 *vision/language 정보로 답을 풀 수 있게* 학습되면서 *teacher 가 brain 을 사용 안 함* 으로 학습될 수 있다 (modality shortcut. Cadene et al. 2019 "RUBi" + Geirhos et al. 2020 shortcut learning). 이 case 면 teacher 의 soft label 에 *brain-specific 정보가 거의 없음*. Student 가 *video+caption-derived label 을 brain 으로 재구성하는 무망한 task*.

**Validation.** Teacher 학습 후 modality ablation (video mask, caption mask, brain mask). 각 modality 제거 시 teacher accuracy drop. Brain mask 의 drop 이 0 에 가까움 = teacher 가 *brain 을 학습 안 한 shortcut*. 이 case 면 student 의 distill 에서 *brain 학습이 안 일어남*.

#### I9. 기술적 forward-pass 안정성 (LOW)

Qwen3-VL 의 가변 길이 input 처리. Inference 에서 video 부재 시 shape error 안 남. Attention mask + M-RoPE position id 계산이 inference-time 에 올바른 길이로 생성되는지 verify 만 하면 forward 통과. *Mechanical issue 라 unit test 한 번이면 해결*.

### 4.3 Top 3 unresolved (배포 차단)

1. **Cross-modal soft-label transfer ceiling 의 실제 값은 얼마인가?** Teacher 의 video-only soft label 과 brain-only soft label 의 KL 을 측정하지 않으면 paradigm 의 ceiling 을 모른다. 결과에 따라 paradigm 자체가 무의미할 수 있다.

2. **Prompt-position drift 의 attention pattern 이 in-distribution 인가?** 학습과 추론에서 동일 prompt token 의 attention map 비교가 없으면 student 의 학습 행동이 inference 에서 재현된다는 보장이 없다.

3. **Student 가 brain 을 실제로 사용하는가?** Brain mask 또는 shuffle 한 input 으로 inference 시 accuracy drop 이 없으면 student 가 *prompt prior 만 학습*. N=5 fMRI 에서 실제로 우려.

---

## 5. Critic 4. RoPE Position-Shift Critic 상세

### 5.1 Verdict

**"Revise. Position-invariance argument 가 partially true 이고 rhetorically overextended."**

### 5.2 3 critical issue 상세

#### R1. RoPE 의 *relative in dot product 이지만 absolute in construction*

Su et al. 2021 (arXiv:2104.09864) 의 q_m · k_n 이 (m-n) 에만 의존하는 것은 *fixed pair*. 단 prompt 와 brain token 의 interaction 이 *distance ~280 (training) vs ~1 (inference)* 라는 *다른 relative geometry*. Brain-position-invariant framing 은 *sleight of hand*. **Attention 은 pairwise**.

#### R2. "Lost in the Middle" evidence

Liu et al. 2023 (arXiv:2307.03172) = identical content 이라도 *different absolute position 에서 >30% accuracy swing* (RoPE-based LLM). U-shape 는 RoPE 의 long-term decay 가 일부 attribution. Prompt 의 near-end (1180/1200) → near-end (901/950) 가 *다른 relative context*. Prompt 의 serial-position role 이 *"last after multimodal evidence"* → *"immediate continuation of brain stream"* 으로 변경.

#### R3. M-RoPE bookkeeping 의 mismatch

Qwen2.5-VL (HF transformers `modeling_qwen2_5_vl.py`) 가 *same (t, h, w) index 를 text token 에 assign*. 단 *temporal axis 가 missing video block 만큼 advance* (training). Inference 에서 no video = prompt 의 *temporal coordinate 가 학습과 다름*. 1D index 가 같아도 의의가 다름. Peng et al. 2023 YaRN (arXiv:2309.00071) + Ding et al. 2024 LongRoPE (arXiv:2402.13753) 에 *small frequency-dimension occupancy mismatch 가 performance degrade* 한다는 evidence.

### 5.3 Counter-argument (steelman against invariance claim)

학습에서 prompt 의 attention 이 *[caption][video][brain] 의 video-mediated routing to brain* 으로 학습된 head 가 *expect*. Inference 에서 head 가 *prompt→brain 의 direct routing*. *학습 안 된 head pattern*. **Interpolation 이 아닌 novel attention regime**.

### 5.4 Falsification test (mandatory)

```
Test. Cosine similarity of last-layer hidden state at first prompt token between
      (a) train-format with zeroed video/caption embeddings but original positions
      (b) inference-format

Threshold. Mean cos < 0.85 across 100 held-out trial = regime 의 not interchangeable.

Pair with. Attention-entropy delta on brain-token key from prompt query > 0.3 nat = failure.
```

Skip 하면 reviewer 가 ask 했을 때 defense 가 없다.

---

## 6. 4 Critic 의 수렴 결론. 7 Critical Blocker

4 critic 의 *공통* 항목 추출.

### B1. Architecture detail 미정 (Architecture critic)

Token shape unification (E1-E4 의 50/256/900 통일) + Memory budget (Qwen3-VL 8B + N=3000 의 OOM) + Brain encoder integration (E3 fixed vector 와 image projector 의 mismatch) + Cross-product 의 192 run 이 NERSC limit 초과.

### B2. D1 collapse 의 v3 reproduce risk (Training critic)

Brain encoder uninformative + LLM prior dominance mechanism 에 v3 가 *explicit 회피 mechanism 부재*. Published precedent 없음.

### B3. Cross-modal KD 의 unproven assumption (Training + Inference critic 의 합의)

Student (brain only) 가 teacher (4 modality) 의 soft label 을 fit 하는데 *brain 이 video / caption information 을 carry 한다는 가정* 이 unproven. **Paradigm 의 motivation 과 ceiling 이 *같은 가정에 동시 의존하는 모순***.

### B4. RoPE position-shift 의 attention regime OOD (RoPE + Inference critic 의 합의)

학습 prompt position ~1180 vs inference ~901 의 *attention regime mismatch*. "Lost in the middle" evidence 의 30% accuracy swing. M-RoPE 의 temporal axis mismatch.

### B5. Stage 0 추가 필요 (Training + Inference critic 의 합의)

- Brain encoder 의 separation pretraining (contrastive prior).
- Cross-modal KD validation (KL of video-only-teacher vs brain-only-teacher soft label).
- Teacher modality ablation (shortcut detection).

### B6. P2-A 의 main branch regression 필요 (Inference critic)

P2-B 만 가는 것은 *binary risk* (works or doesn't). P2-A modality dropout 을 *equal main branch* 로 fallback. P2-B 만의 design = paper 의 *위험 분산상 의문*.

### B7. MindCaptioning bridge framing 이 vacuous (Inference critic)

"Bridge" 를 *training-only auxiliary supervision* 으로 정확하게 framing 해야 한다. Paper claim 을 정직화. "Caption is used during training as auxiliary modality whose information is compressed into student weights via distillation. At inference, the student model uses brain alone."

---

## 7. 12 Redesign 권고

### 즉시 진행 가능 (cheap, doc edit)

1. **"Architecture finalized" claim 철회.** Methodology + evaluation framework 만 lock. Architecture spec 은 design-level.
2. **Prompt position 의 fixed padding strategy.** Video / caption 의 padding token 으로 prompt 의 *학습-inference 의 same position*.
3. **MindCaptioning bridge framing 정확화.** 정직한 statement.
4. **Clinical motivation 약화.** Future work 으로.

### Pre-training validation experiment (mandatory)

5. **Cross-modal KD validation.** KL (video-only-teacher soft label, brain-only-teacher soft label). High KL = video 가 brain 에 안 닿음 = distillation noise. Low KL = video 가 처음부터 불필요 = paradigm 정당화 약화.
6. **Teacher modality ablation.** Brain mask 시 teacher accuracy drop 측정. Drop 이 0 에 가까움 = teacher 의 *brain shortcut learning*.
7. **Student brain shuffle 의 accuracy drop.** Drop 이 0 = student 가 *prompt prior 만 사용*.
8. **RoPE OOD falsification.** 학습-format hidden state vs inference-format hidden state 의 cosine similarity (threshold 0.85).

### Architecture redesign

9. **Token shape unification.** Perceiver-style cross-attention resampler 로 fixed 256 token.
10. **Brain encoder integration.** Prefix token. `<brain_start>` + `<brain_end>` special token. 모든 E1-E4 의 projection MLP 통일.
11. **Cross-product grid 를 factored 3-phase sweep 으로.** 192 → 30 runs.

### Training redesign

12. **Stage 0 추가.** Noise ceiling + brain encoder contrastive pretraining + KD validation 의 3 단계.
13. **Curriculum 을 loss schedule 로 reformulate.** Stage discrete → continuous loss weight schedule.
14. **Stage 4 KL → JS divergence 또는 weighted soft-CE.**
15. **Brain reconstruction → brain feature contrastive.**
16. **P2-A 를 main branch 로 격상.** P2-B 와 equal.
17. **α, T, λ 의 small grid sweep commit.**
18. **Modality dropout 을 teacher 에 적용** (현재 student 에 잘못 적용됨).

---

## 8. 우리의 next step

### Week 0 (NEW, mandatory pre-training engineering sprint, 1-2 주)

- Stage 0 noise ceiling (ISC + repeated-trial + analytical).
- Brain encoder contrastive pretrain 의 smoke test (separation prior verify).
- Cross-modal KD validation (KL of teacher 의 video-only soft label vs brain-only soft label).
- Teacher modality ablation (shortcut learning detection).
- Smoke test (memory budget on Qwen3-VL 2B/4B + N=1500).
- Prompt position falsification (RoPE OOD test).
- Token unification design (Perceiver resampler).
- Brain encoder integration test (prefix token strategy).
- Caption neutral verify (MindCaptioning sample).

### Week 3+ (factored 3-phase sweep)

- Phase 1. E1-E4 encoder sweep (V=CLIP, caption=MC 고정). 16 runs.
- Phase 2. V=CLIP/V-JEPA2/VideoMAE sweep (E*=best 고정). 12 runs.
- Phase 3. Caption source sweep. 2 runs.
- Final. (E*, V*, caption*) full 4-stage + dual main branch (P2-A + P2-B).

### 평가

- Ceiling-anchored gap_filled metric.
- High-D structure preservation (per-emotion correlation + rare-emotion recovery + inter-dim correlation + dimension compression curve).
- Subject 의 random effect modeling (linear mixed model).
- Cross-modal validation diagnostic (Section 7 의 mandatory 4).

---

## 9. Honest 평가. Framework 의 *현재 상태*

### Q. Framework 가 다른 사람에게 보여 줄 수준인가?

**A. NO.**

### 이유

1. **4 critic 모두 redesign 권고**. "Framework lock" claim 이 *4 lens 의 critique 를 받음*.
2. **7 critical blocker 가 unresolved.** Token unification, memory budget, brain encoder integration, Stage 0, RoPE OOD, cross-modal KD validation, grid factoring 의 design 과 implementation 이 미정.
3. **12 redesign 권고가 미적용**. Doc, framework, architecture spec 의 update 가 필요.
4. **D1 collapse mechanism 의 v3 reproduce risk 에 explicit 회피 mechanism 부재**. *Published precedent 없음* 이 evidence.

### 다른 사람에게 보여 줄 수준 도달의 prerequisite

- **Week 0** 의 mandatory pre-training validation 완료. 4 validation experiment 의 결과 confirm.
- **12 redesign** 의 doc + framework + architecture spec update.
- **2 차 redteam review** spawn. Week 0 결과 + 12 redesign 적용에 대한 validation.

이후 framework 가 *다른 사람에게 보여 줄 수준*.

### 정직한 timeline

- Week 0 engineering sprint = 1-2 주.
- 12 redesign 의 doc update = 1 주.
- 2 차 redteam = 1 주.
- 총 **3-4 주 후가 framework 의 *준비 완료* 시점**.

---

## 10. 종합 결론

EmoBrain NV3 framework 의 2026-06-29 lock 표현은 **over-claim**. 4 critic 의 *수렴 결론* 은 *partial redesign + extensive validation 이 mandatory* 라는 권고다.

진짜 next step.

1. **즉시.** 본 redteam review 의 documentation 과 *honest acknowledgement*.
2. **Week 0.** Engineering sprint + validation experiment (4 mandatory test + Stage 0 noise ceiling + smoke test).
3. **Week 3.** 12 redesign 의 framework + architecture spec update.
4. **Week 4.** 2 차 redteam review spawn. Week 0 결과 + 12 redesign 적용 evaluation.
5. **Week 5+.** Factored 3-phase sweep 시작 (E1-E4 → V sweep → caption sweep → final dual main branch).

이것이 *진짜 honest path*. *12-16 주 build phase* 에 *4 주 mandatory prep 가 추가*.

GPU hour cost 가 *부담 없는* user 입장에서 *time-wise 로 추가 4 주는 acceptable*.

---

## 11. Open question (사용자 결정 필요)

(Q1) 본 redteam review *모두 수락* + 12 redesign 진행. (recommended)

(Q2) 일부만 수락 + 다른 부분은 push back. (어느 critic 이 over-stated 인지 specific evidence 와 함께 사용자 의견 필요)

(Q3) Framework 의 *현재 state* 를 *다른 사람에게 보여 주는* 결정 (위의 honest 평가 NO 를 over-ride).

---

## Reference

- 본 review 의 source. 2026-06-30 의 4 critic agent 의 parallel adversarial review.
- Framework decision. `docs/notes/project_decisions.md` 의 2026-06-30 entry.
- Framework spec. `Paper/framework_EN.md` + `Paper/framework_KR.md`.
- Architecture spec. `docs/notes/architecture_design_20260629.md`.
- 외부 reference framework decision. `/pscratch/sd/s/sjmoon/NV3_framework_decision.md` (별도 user 작성).

---

(끝.)
