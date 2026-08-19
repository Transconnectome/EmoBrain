> ⚠️ **ARCHIVED — 역사 기록. 현행 문서가 아니다.**
> 현행 논증 = `docs/paper_logic_merged.md` (대전제 · RQ · 가설 H1–H4). 운영 규칙 = `CLAUDE.md`.
>
> 아래 내용 중 다음은 **뒤집혔다.** (a) Qwen3-VL 등 LLM backbone 사용 — 금지.
> (b) open-vocabulary / cross-taxonomy 전이를 headline novelty 로 삼는 프레임 — 폐기.
> (c) 학습에 없던 감정 zero-shot — 폐기(원칙적 분할 기준 없음, RQ 와 무관).
> (d) "EmoBrain 과 EmoViS 는 별도 논문 2편" — 현재는 **한 편의 논문**.
> (e) "EmoBrain 은 cortical location 을 주장하지 않는다" — 현재 **H3 이 cortical location 주장**이다.

# EmoBrain Architecture Design (Historical)

> Superseded on 2026-07-22 by
> `docs/notes/implementation_spec_20260702.md`. This file preserves design
> history and is not a current implementation contract.

작성 2026-06-29. Single project framework novelty path 의 architectural spec. spine 결정 의 source 는 `project_decisions.md` 의 2026-06-29 entry, narrative 는 `Paper/framework_EN.md` + `framework_KR.md`.

본 문서 = 5 novelty (NV0-NV4) 의 architectural component, modular brain encoder spec, fusion strategy, 4 stage curriculum, evaluation framework, token budget, open implementation question 의 full spec.

---

## 1. Spine question (neuroscientific)

> Naturalistic video 가 일으키는 fine-grained emotion 의 분포 표상이, 단일 humanbrain 의 BOLD 신호 안에 multi-modal context (video + caption) 와 함께 decode 가능 한가? 그 decode 의 가능 여부 와 한계 가 emotion 표상의 *populational* vs *idiosyncratic* component 의 어떤 부분 에 attributable 한가?

이 질문은 EmoMind (Mohammed et al. 2026) 의 *per-subject* endpoint 와 EmoBrain 의 *5-subject pooled, multi-modal context-bridged* endpoint 의 spectrum 위에 위치. *fine-grained* = 34 categorical emotion (Cowen) 의 distribution. *brain activity* = Horikawa naturalistic video fMRI (5 subj × 2185 stim). *multi-modal context* = video clip + MindCaptioning human caption.

기존 단일 modality 접근 (frozen BFM, BrainVLM token-output, vanilla ridge) 가 baseline 못 넘은 결과 가 본 spine 의 motivation. 자세 한 evidence 는 `docs/reports/d1_brainvlm_va_negative_result_20260628.md` 와 `docs/reports/phase1_audit_20260604/`.

---

## 2. Architecture diagram

```
================================================================================
                              EmoBrain v6 Architecture
================================================================================

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                              MODALITY INPUT                              │
  └─────────────────────────────────────────────────────────────────────────┘

   fMRI BOLD                Video clip               Caption text
   (5 subj × 2185 stim)     (silent, 8 sec)         (MindCaptioning human
   shape (T, ROI)            T=8 frames@4Hz          + 우리 generated, 1-2 sent)
        │                          │                          │
        ▼                          ▼                          ▼
  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐
  │ Brain encoder│         │Vision encoder│         │Caption loader│
  │  (modular)   │         │  (selectable)│         │  (NV2 dual)  │
  │              │         │              │         │              │
  │ raw ROI      │         │ CLIP         │         │ MindCap human│
  │ Ridge embed  │         │ V-JEPA2      │         │ Our generated│
  │ BFM (6 변종) │         │ VideoMAE     │         │              │
  │ VLM hidden   │         │              │         │              │
  └──────┬───────┘         └──────┬───────┘         └──────┬───────┘
         │ brain token            │ video token            │ text token
         │ (Nb tokens)            │ (Nv tokens)            │ (Nc tokens)
         ▼                        ▼                        ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                         ADAPTER (NV0 + NV1 + NV2)                        │
  │                                                                          │
  │   brain → LLM token shape         video → LLM token shape                │
  │   text encoder (LLM tokenizer)    instruction (task + 34-cat inventory)  │
  │                                                                          │
  │   Token assembler. ordered concat with modality position embedding       │
  │   [<brain_start> Tb ... <brain_end> <video_start> Tv ... <video_end>     │
  │    <text_start>  Tc ... <text_end>  <inst_start>  Ti ... <inst_end>]     │
  └────────────────────────────────────┬─────────────────────────────────────┘
                                       │ unified token sequence (Nb+Nv+Nc+Ni)
                                       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                     FUSION LLM (NV0 + NV1 의 core)                       │
  │                                                                          │
  │     Qwen3-VL backbone (default 4B, ablation 2B/8B)                       │
  │     LoRA on {qkv attention, vision projector, output head}               │
  │     causal mask + modality cross-attention                               │
  │                                                                          │
  │     POYO 형 sequence model 은 ablation slot                              │
  └────────────────────────────────────┬─────────────────────────────────────┘
                                       │ fused hidden state (D=embed dim)
                                       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │              OUTPUT HEAD (NV4. 34D independent regression + curriculum)  │
  │                                                                          │
  │     34-D linear regression (NO softmax, NO sum-to-1, NO KL).             │
  │     각 감정 은 서로 경쟁 하지 않는 독립 점수 (bittersweet 예).           │
  │     학습 전 z-score per emotion (mean 0, std 1) 필수 전처리.             │
  │                                                                          │
  │     Curriculum sub-stage (per-emotion MSE 원리 유지, subset target).     │
  │       1 (top-1)    A={자극 별 rating 1위 감정}      sanity                │
  │       2 (top-2)    A={rating 상위 2}                mixed emotion         │
  │       3 (top-k)    A={rating > threshold, 가변 k}   sparse profile        │
  │       4 (full 34D) A={1..34}                        전체 profile          │
  │     각 stage loss = sum_{k ∈ A} (pred_k - target_k)^2                   │
  │                                                                          │
  │     Optional auxiliary. hidden → ROI mean reconstruction (NV3 anchor)    │
  └─────────────────────────────────────────────────────────────────────────┘
```

Token order = brain → video → text → instruction. ablation slot 의 변경 가능. modality 별 position embedding 의 분리 학습.

---

## 3. 5 Novelty 의 architecture component 매핑

| Novelty | Component | 구체 위치 |
|---------|-----------|-----------|
| NV0. LLM-based brain emotion decoder | Fusion LLM + Output head 의 통합 | `project/code/fusion/llm_wrapper.py`, `project/code/training/trainer.py` |
| NV1. 3-modality LLM fusion | Adapter + Token assembler | `project/code/adapters/{brain_to_llm,video_to_llm}.py`, `project/code/fusion/token_assembler.py` |
| NV2. MindCaptioning bridge | Caption loader 의 dual source | `project/code/caption_loader/{mindcaptioning,generated}.py` |
| NV3. Modular brain encoder | Brain encoder 의 4 modular | `project/code/brain_encoder/{raw_roi,ridge_embedding,bfm,vlm}.py` |
| NV4. 34-distribution curriculum | Output head + Trainer 의 4 stage | `project/code/fusion/dist_head.py`, `project/code/training/trainer.py` |

NV0 는 spine 의 *framing* 이라 하나 의 component 가 아닌 *system 통합* 의 결과. 다른 4 NV 가 NV0 의 구성 요소.

---

## 4. Modular brain encoder spec (NV3)

같은 fusion stack 이 4 변종 모두 받음. 출력 shape 통일 (sequence of brain token, dimension 일관). 각 encoder 의 token sequence length Nb 가 다름 → token assembler 의 modality position embedding 이 정렬.

**중요. 공통 patchify frontend 없음.** fMRI 가 곧장 각 encoder 로 들어가고 patchify 는 encoder 안 에서 발생. ViT 계열 은 ViT patch embedding, SwiFT 는 Swin 4D window, Brain-JEPA 는 또 다른 patch 방식 을 각자 사용. 공통 인 것 은 output 이 brain token 이라는 사실 뿐. 진짜 변수 는 사전 학습 유무 와 fMRI 적응 설계.

**Ablation 축 재정의 (2026-06-30 summary 반영).** "어떤 encoder 가 best 인가" 가 spine question 아님. Framework 자체 (multi-modal 학습 + brain-only 추론 비대칭) 가 novelty 이고, E1-E4 는 그 framework 가 열어주는 후속 질문. E3 vs E4 의 진짜 축 = fMRI 대규모 pretrain frozen transfer (E3) vs image pretrain 출발 후 fMRI fine-tune adaptation (E4).

### 4.1 E1. No pretrain, no adaptation (control)

- **Label**. control. 사전 학습 없음, fMRI 적응 없음.
- **Input**. (T_brain, N_ROI) tensor. T_brain = Horikawa 자극별 BOLD length (median 5 TR), N_ROI = Schaefer-400 + Tian-50 = 450.
- **Encoder**. 단순 projector (linear 또는 얕은 MLP). LLM 텍스트 공간 으로 사영.
- **학습**. projector 만 학습, backbone 은 downstream 학습 에 의존.
- **역할**. framework 자체 의 lower bound. 사전 학습 없이 도 framework 가 brain-only 에서 신호 를 뽑는지 의 sanity floor.

### 4.2 E2. Task-specific, no LLM pretrain (Ridge latent)

- **Label**. task-specific, non-LLM.
- **Input**. Phase 1 의 ROI mean + Ridge 의 *prediction latent* (예측 직전 의 D=128 latent vector). emotion task 별 separate Ridge.
- **Encoder**. Ridge closed-form 학습. LLM 사전 학습 을 못 씀.
- **Token**. 각 task 의 latent 를 1 token 으로 concat. Nb = N_task (현재 4).
- **역할**. Phase 1 의 strong baseline 의 inductive bias 를 그대로 framework 안 에 가져 옴. task-bound 라 24D 구조 손실 위험.

### 4.3 E3. fMRI 전용 pretrain frozen (Brain-JEPA / NeuroSTORM / SwiFT)

- **Label**. fMRI 대규모 pretrain, frozen transfer.
- **Input**. Phase 1 의 frozen BFM embedding. shape (T_brain, D_bfm).
- **Encoder**. Brain-JEPA / NeuroSTORM / SwiFT 의 사전 학습 hidden state. Encoder frozen, projector 만 학습 (probing).
- **Token**. BFM token 그대로 또는 light linear projection (D_bfm → D_token). Nb = T_brain.
- **역할**. E4 와 의 진짜 질문. "fMRI 대규모 pretrain 의 frozen transfer" vs "image pretrain 출발 후 fMRI fine-tune adaptation" 중 어느 쪽 이 framework 안 에서 더 강한지.
- **변종**. BJ resting / BJ scratch / NS / SwiFT NewE96 / SwiFT 변종 6 종 selectable.

### 4.4 E4. Image pretrain 후 fMRI fine-tune (VLM-derived)

- **Label**. image pretrain, fMRI fine-tune 적응.
- **Input**. D1 BrainVLM 의 fine-tuned hidden state (V/A 또는 Cat34 task 의 LoRA-tuned backbone 의 brain patch 위치 의 last layer hidden). Image 사전 학습 만 있는 원본 Qwen3-VL vision encoder 를 fMRI 로 fine-tune 한 후 hidden state 를 추출.
- **Encoder**. D1 학습 시 fine-tune, 추출 후 frozen. projector 만 downstream 학습.
- **Token**. hidden 의 token sequence 그대로. Nb = N_brain_patch (Qwen3-VL patchify config 의존).
- **역할**. E3 와 의 pretrain source 비교. UMBRAE 계 (image → fMRI fine-tune) 의 논리 를 우리 조건 (2 천 trial 급) 에서 검증.
- **주의**. 원본 UMBRAE 는 NSD 급 (subj 당 2-3 만 trial) 에서 효과. 우리 조건 은 2 천 trial 이라 pretrained BFM (E3) 이 유리 할 가능성. 결과 는 open.

### 4.5 Projector 의 두 목적

Brain 과 video 는 embedding 이라 LLM 이 바로 못 먹음. modality 별 projector (MLP 또는 Q-Former 계) 로 LLM token 공간 에 사영. Projector 는 단순 크기 맞추기 가 아니라 두 가지 학습 된 사상.

- **차원 정합**. encoder 출력 차원 → LLM token 공간 차원. linear 또는 얕은 MLP.
- **표상 정렬**. LLM token 분포 와 의 정렬. 학습 이 여기 서 발생.

이 지점 이 encoder frozen (E3) vs encoder co-train (E4 downstream 재 fine-tune) 을 가르는 결정 축. 또한 embedding 을 몇 token 으로 압축 하는가 (token 병목) 가 34D 고차원 구조 보존 과 직결. token 을 너무 적게 뽑으면 34D 구조 가 이 배관 에서 깎임.

### 4.6 Encoder ablation grid

S11 evaluation 에서 4 encoder × 3 vision encoder × 2 caption source = 24 condition. sparse, *full multi-modal × encoder 4* + *encoder 1 best × vision 3* + *encoder 1 best × caption 2* 의 marginal sweep 만 학습. Encoder 순위 자체 가 spine result 가 아니라 framework 의 modularity 검증.

---

## 5. Vision encoder choices

| Encoder | Output shape | 특징 |
|---------|--------------|------|
| CLIP ViT-L/14 | (Nv=N_frame, D=768) | semantic-rich, NSD 의 정착 baseline |
| V-JEPA2 ViT-L | (Nv=N_frame × N_patch_spatial, D=1024) | TRIBE (Algonauts 2025 1 위) 의 backbone. temporal dynamics 강. |
| VideoMAE-L | (Nv=N_frame × N_patch_spatial, D=1024) | self-supervised video pretrain. cheaper. |

Default = V-JEPA2 (TRIBE evidence). ablation = CLIP + VideoMAE.

Adapter `video_to_llm.py` 가 모두 동일 token shape (D=D_LLM) 으로 변환.

---

## 6. Caption sources (NV2)

### 6.1 MindCaptioning human caption (main)

- **Source**. Horikawa & Kamitani Mind Captioning paper (Science Advances 2025) 의 publicly released dataset. 2185 stim 의 human-written neutral caption.
- **형식**. 1-2 sentence English description. "neutral" = emotion label 직접 mention 없음.
- **역할**. brain-context bridge. brain 신호 와 emotion label 사이 의 semantic anchor. NV2 의 main argument.

### 6.2 우리 model-generated caption (비교)

- **Source**. Qwen-VL (또는 Qwen3-VL) 의 video clip → caption generation. 우리 batch 로 2185 stim 모두 cover.
- **형식**. 1-2 sentence English description. neutral filtering (emotion label mention 제거).
- **역할**. NV2 의 *human vs generated caption 의 효과 비교*. publishability 의 angle. publishable framing 의 한 contribution.

### 6.3 Caption generation pipeline (우리 generated)

- **Step 1**. Horikawa 자극 (mp4) 의 frame sample (8 frame uniform).
- **Step 2**. Qwen-VL prompt = "Describe this short video clip in 1-2 neutral sentences. Do not mention any emotion words.".
- **Step 3**. Output 의 emotion word filter (Cowen 34 + V/A 단어 list 의 substring match 제거 또는 rephrase).
- **Step 4**. Length 통일 (max 40 token).

`project/code/caption_loader/generate_captions.py` + `project/sample_scripts/generate_captions_qwen_vl.sh`.

---

## 7. Fusion. Prompt schema + token order + LoRA target

### 7.1 Prompt schema

Stage 별 task instruction 의 미세 차이 있지만 base template 통일.

```
<system>
You are an emotion analysis model trained on naturalistic video fMRI.
Use the brain signal, video, and caption together to identify the emotion distribution.
</system>

<brain_start>
{brain_tokens}
<brain_end>

<video_start>
{video_tokens}
<video_end>

<caption_start>
{caption_text}
<caption_end>

<inst_start>
Output the top-{k} emotion category(ies) from the 34-category inventory:
[admiration, adoration, ..., sadness, ..., triumph].
Format. JSON array of strings, sorted by likelihood.
<inst_end>

<output>
```

Stage 4 의 instruction 은 "Output the 34-dim probability distribution as JSON object" 으로 교체. Output 의 parse 는 grammar-constrained decoding (lm-format-enforcer) 또는 dedicated softmax head 의 forward (training 시 softmax head 만 사용, inference 시 token decode 도 grammar 강제).

### 7.2 Token order (2026-07-02 implementation_spec 로 확정)

- **Teacher sequence**. `video tokens → Caption field → brain tokens → Question field`. Video 를 앞 에 두어 시각 context 를 anchor, brain 을 Question 직전 에 두어 마지막 latent 가 brain 신호 를 반영.
- **Student sequence**. `brain tokens → Question field`. Video / caption 없음.
- 이전 default (`brain → video → caption → instruction`) 는 폐기. Ablation slot 은 config 로 변경 가능 (`prompt.token_order`).

### 7.3 Modality position embedding

각 modality 의 start/end marker token (`<brain_start>` 등) 의 embedding 을 fresh learnable. backbone 의 BOS/EOS 와 분리.

### 7.4 LoRA target

| Layer | LoRA rank | Justification |
|-------|-----------|---------------|
| Q, K, V projection (모든 layer) | r=16 | standard |
| O (output projection, 모든 layer) | r=16 | EmoMind 의 LoRA target 참조 |
| Vision projector (Qwen3-VL 의 vision-to-text projection) | r=32 | brain modality 의 새 token type → vision projector 의 adaptation 더 필요 |
| Output head | full fine-tune | 34-D output 의 새 task |

LoRA target list 는 `project/config/lora_target.yaml`.

### 7.5 Prompt structure. caption field vs question field

Prompt = caption field + question field 로 분리.

- **Caption field**. MindCaptioning human caption (main NV2 source) + 우리 generated Qwen-VL caption 이 들어가는 자리. Student 학습 시 확률적 으로 dropout.
- **Question field**. Task instruction + 34-category inventory 가 들어가는 자리. 모든 sample 에서 동일한 fixed 문자열. Question 자체 는 label 을 구별 할 정보 가 없어 shortcut 이 되지 않음.
- **차이 의 의미**. 매 sample 마다 달라지며 정답 과 상관 이 높은 것 은 caption. 진짜 shortcut 위험 은 question 이 아니라 caption 이 brain 을 대신 하는 경로.

### 7.6 Teacher vs student prompt asymmetry

Teacher 와 student 의 prompt 구조 가 다름 → distribution shift → 방치 하면 student 의 추론 성능 저하.

| 시점 | Prompt 구조 | 벡터 입력 |
|------|------------|-----------|
| 학습 (teacher) | caption field + question field | brain + video |
| 학습 (student) | question field, caption 은 확률적 dropout | brain (+ 일부 배치 에서 video) |
| 추론 (student) | question field only | brain only |

**Caption dropout 의 이중 효과.**
1. Student 가 caption 없는 prompt 에 미리 익숙 해짐 → 추론 시 의 distribution shift 완화.
2. Student 가 caption 을 못 기대 하게 됨 → brain-only 신호 를 학습 하도록 강제.

Dropout 확률 은 open decision (OD-P, 0.5 / 0.7 / 0.9 grid 후 결정).

### 7.7 ICL or single-trial decision

D1 의 v1/v2 = ICL 3-round (cross-subject ref). 본 spine 에서는 **single-trial default**. ICL 은 ablation.

근거. ICL 의 *학습 시 의 SNR 약화* 가 D1 의 한 cause 후보 (negative result report §3.2 (b)). 새 spine 에서 brain + video + caption 의 3-modality 가 *trial-level context* 를 이미 충분히 제공. ICL 의 cross-subject reference 는 *transfer evaluation* (LOSO) 에서만 사용.

---

## 8. NV4. 34D independent emotion regression + practical curriculum (2026-06-30 재정의)

**핵심 원칙.** 34 개 감정 은 서로 경쟁 하지 않는 독립 점수. Softmax / sum-to-1 / KL divergence / cross-entropy 사용 금지. Loss 는 per-emotion MSE (해당 stage 의 active target subset 합산). Distillation 도 동일 원칙.

**Curriculum 은 practical stepwise validation 으로 유지.** 34 개 전부 를 한 번 에 학습 가능 한지 는 open. Curriculum staging (top-1 → top-2 → top-k → full 34D) 을 통해 하나 라도 학습 되는지 부터 sanity check 후 dimension 확장. 각 stage 는 여전히 per-emotion independent MSE (softmax / KL / CE 금지, section 9 원칙 준수). 이전 formulation 에서 폐기 된 것 은 "softmax head + KL divergence + class weighting" 이지 stage 진행 자체 는 유지.

**차이 명확화.**
- 이전 (폐기). Stage 1 top-1 CE + Stage 4 34D KL on softmax distribution.
- 지금 (유지). Stage 1 top-1 subset MSE + Stage 4 34D independent MSE. Softmax 없음, KL 없음, class weighting 없음. Z-score 필수.

### 8.1 정답 형식

- **Horikawa Cowen-Keltner rating**. 영상 당 34 개 감정 을 1-9 Likert 로 rating. 각 감정 은 독립 rating (bittersweet 처럼 기쁨 과 슬픔 이 둘 다 높을 수 있음).
- **Raw target (per stimulus)**. `y ∈ R^34`, 각 원소 = rater 평균 rating (1-9 unnormalized).
- **처리 없이 사용 하면 안 됨**. 클래스 별 rating 분포 차이 가 큼. 어떤 감정 은 대부분 7-8, 어떤 감정 은 대부분 1-2.

### 8.2 필수 전처리. per-emotion z-score

```
z_k = (y_k - mean_k) / std_k     for each emotion k = 1..34
```

- `mean_k`, `std_k` 는 training set 에서 감정 별 로 계산 (test set 에 fit 하지 않음).
- 결과. 각 감정 이 mean 0, std 1 로 rescale → MSE 가 감정 별 로 균등 가중.
- **필수 이유**. 정규화 안 하면 큰 값 감정 이 loss 를 지배 → 드문 감정 무시. Rare-emotion recovery 를 primary metric 으로 둔 이상 z-score 는 선택 이 아니라 필수.

### 8.3 Loss. Per-emotion MSE (subset sum, curriculum stage 별)

Base form.

```
L_main(pred, target; A) = sum_{k ∈ A} (pred_k - target_k)^2
```

- `A` = 해당 curriculum stage 의 active target subset.
- 각 stage 는 A 의 크기 만 다름. 원리 는 항상 per-emotion independent MSE.
- Softmax 사용 금지. Sum-to-1 constraint 없음.
- KL divergence, cross-entropy, multi-label BCE 모두 금지 (34D 를 distribution 으로 취급).
- Class weighting 불필요 (z-score 가 이미 균등 가중).

#### 8.3.1 Curriculum stage 별 active target subset A

| Stage | Active target A (per stimulus) | Loss size | Rationale |
|-------|-------------------------------|-----------|-----------|
| 1 (top-1) | 자극 별 rating 최고 감정 1 개 만 | 1 항 | 감정 하나 라도 학습 되는지 sanity check |
| 2 (top-2) | 자극 별 rating 상위 2 감정 | 2 항 | Mixed emotion (예. bittersweet) 학습 되는지 |
| 3 (top-k) | 자극 별 rating > threshold (예. z-score > 0.5) 감정 집합, 평균 5-8 개 | 가변 | 자극 별 emotion profile 의 sparse 부분 학습 |
| 4 (full 34D) | 34 개 전부 | 34 항 | Section 9 의 최종 formulation. Per-stimulus profile shape 전체 학습 |

**Stage 1-3 의 non-active 감정 처리.** Loss 계산 에서 masked (gradient 없음). Prediction 은 그래도 34D 로 출력 (head 는 항상 34-dim). 다만 학습 시 그 dim 은 update 안 됨.

**Stage transition.** 이전 stage 의 checkpoint 에서 weight load. Head dimension 은 항상 34 (변경 없음). Adapter / fusion / backbone LoRA 는 누적 학습.

**Curriculum 의 status.** Practical stepwise validation tool. Stage 4 (full 34D) 가 실행 가능 하다고 확인 되면 향후 curriculum 없이 direct 34D 로 통합 가능. 각 stage 에서 학습 실패 시 원인 진단 (예. Stage 2 에서 실패 = mixed emotion 학습 이 근본 어려움).

### 8.4 Distillation loss (Stage 2 에서 얹음)

Teacher soft label 도 34D 독립 점수 로 caching. Student 가 teacher 의 34D 를 재현.

```
L_distill(student_pred, teacher_pred) = sum_{k=1..34} (student_pred_k - teacher_pred_k)^2
```

- 같은 MSE 원리. Softmax 금지.
- Total loss = L_main + λ × L_distill. λ 는 OD-D2 (0.5 / 1.0 / 2.0 grid, S9 smoke 후 결정).

### 8.5 Optional auxiliary reconstruction loss

`L_total = L_main + λ_recon × L_recon`. L_recon = LLM hidden (brain segment) → ROI mean (Schaefer-400+Tian-50) 의 MSE. λ_recon = 0.1 (S9 smoke 후 결정).

이 auxiliary 가 NV3 의 brain modality 의 *representational anchor*. brain signal 의 정보 가 fusion 안 에서 *희석* 되는 것 방지.

### 8.6 Metric (headline)

- **Loss 와 metric 은 다름**. Loss 는 학습 을 굴리는 연료, metric 은 결과 를 채점 하는 성적표.
- **Headline metric = per-stimulus 34D profile shape similarity**. 개별 감정 점수 정확도 가 아니라, 영상 하나 에 대한 34 개 숫자 의 전체 모양 이 정답 모양 과 닮았는지.
  - Per-stimulus Pearson r 34D vector correlation → mean across test stimulus.
  - Per-stimulus cosine similarity → mean.
  - Interpretation. "이 영상 은 기쁨 과 향수 가 높고 공포 는 낮다" 라는 윤곽 을 맞히는 것 이 목표.
- **부가 metric**.
  - Per-emotion Pearson r (감정 별 로 stimulus 간 correlation).
  - Rare-emotion recovery (frequency 하위 10 감정 의 profile shape 정확도).
  - 34×34 inter-dimension correlation matrix 의 Frobenius norm (predicted vs target).
  - Dimension compression curve (k 차원 reduction 후 성능 저하 곡선).

자세한 evaluation framework 는 §9.

---

## 8.5 Stage 0 noise ceiling protocol (2026-06-30 추가)

목적. Stage 1 의 encoder ablation 의 진입 *전* 에 brain signal 의 noise ceiling 을 estimate. R0 risk (ceiling 자체 가 ridge 와 가까움) 의 직접 test. Encoder competition 의 meaningful headroom 의 width 확정.

### 8.5.1 ISC (Inter-Subject Correlation)

5 subject 의 같은 stimulus 의 brain response 의 cross-subject correlation. 각 ROI / 각 TR 의 ISC 계산 → mean ISC = inter-subject signal consistency 의 upper bound estimator.

구현. Per ROI per TR 의 Pearson r across subject pair (C(5,2)=10 pair). Mean across pair → ROI 별 ISC map → mean over ROI = global ISC.

### 8.5.2 Repeated-trial split-half reliability

Horikawa test set 의 56 stim × 24 repeat 의 within-subject split-half. Trial 을 random 으로 두 set 으로 split → 각 set 의 mean response → 두 set 의 Pearson r. Spearman-Brown correction 으로 full reliability estimate.

구현. Per subject per ROI per stim 의 split-half. Bootstrap 1000 회 의 mean.

### 8.5.3 Analytical noise ceiling (Lage-Castellanos 2019)

Lage-Castellanos et al. 2019 (PLoS Comp Bio, DOI 10.1371/journal.pcbi.1006397) 의 analytical formula. Signal variance 와 noise variance 의 분리 estimation 으로 model 의 max achievable performance 의 upper bound 계산.

```
NC_analytical = sigma_signal^2 / (sigma_signal^2 + sigma_noise^2 / n_repeat)
```

### 8.5.4 Cowen-Keltner concordance (참고 값, NOT ICC — 2026-07-07 정정)

**원문 검증 (PMC5617253).** "75% of the videos elicited significant concordance for at least one category of emotion across raters (FDR < 0.05), with concordance averaging 54% (chance level being 27%)".

- **ICC 아님.** Concordance = 한 영상 에 같은 emotion category 를 고른 rater 비율 (평균 54%, chance 27%). 이전 서술 "inter-rater ICC ≈ 0.54" 는 오류.
- 영상 당 9-17 rater 가 34 category yes/no 판단. 우리 label = crowd 동의 비율 (proportion).
- **Continuous metric ceiling 으로 직접 못 씀.** Categorical 일치율 (54%) 과 우리 continuous 34D Pearson 은 단위 다름. 참고 값 으로만.

### 8.5.5 Consensus + headroom width

Noise ceiling 은 측정 가능 한 estimator (brain cross-subject ISC, repeated-trial split-half, label crowd split-half, Lage-Castellanos analytical) 의 consensus. **Cowen concordance 54% 는 여기 estimator 로 넣지 않음** (categorical 이라 continuous 와 mixing 불가). Ridge baseline (E2) 의 위치 가 headroom width 의 lower bound. (noise_ceiling - ridge) 의 absolute 값 이 encoder competition 의 meaningful range.

---

## 8.6 Training paradigm details (2026-06-30 late-3 lock)

이전 lock (KL / cross-entropy + student-side dropout) 은 (a) NV4 재정의 로 KL 폐기, (b) red-team recommendation 18 에 따라 modality dropout 을 teacher 로 이동 하여 정정.

### 8.6.1 P2-B teacher/student distillation (main)

**Teacher.**
- Input. brain + video + caption 의 3-modality. **Teacher 학습 중 P2-A modality dropout (video / caption 각각 확률 p=0.3, mask + padding 으로 같은 position 유지)** 적용. Grid p ∈ {0.1, 0.3, 0.5} 후 결정.
- Backbone. Qwen3-VL (4B default) + LoRA-A.
- Target. 34D Cowen-Keltner independent emotion score (§8, per-emotion MSE, softmax / KL / CE 금지). Curriculum stage 별 subset MSE.
- 학습 후 convergence 의 시점 에 weight lock.

**Soft label caching.**
- Convergence 된 teacher 의 forward 를 모든 (brain, video, caption) tuple (+ modality mask 조합) 에 대해 run.
- Output 의 34D raw score (softmax 없음) 을 caching.
- Caching 위치. `project/shared/output/teacher_soft_labels/{track_stage}/`.
- Student 학습 시 teacher 의 inference 불필요 → student step time 이 단일 model 과 유사.

**Student.**
- Input. brain-only. Modality dropout 없음 (student 는 이미 brain-only 이므로 무의미). Caption dropout (§7.6) 은 별개 로 유지 (prompt shift 완화 용).
- Backbone. 같은 Qwen3-VL (weight 공유) + LoRA-B (LoRA weight 만 분리).
- Loss = `L_main (subset per-emotion MSE on z-scored target) + λ × L_distill (subset per-emotion MSE on teacher 34D)`. λ = OD-D2 (0.5 / 1.0 / 2.0 grid). Softmax / KL / CE 금지.
- 학습 후 student 가 inference 시 의 main model.

**LoRA-A vs LoRA-B 분리 의 의의.**
- 두 model 이 같은 backbone weight 공유 → memory 절감.
- LoRA 만 swap 으로 teacher inference (LoRA-A active) 와 student forward (LoRA-B active) 의 분리.
- Backbone 의 frozen 유지 → LLM body 의 knowledge 보존.

### 8.6.2 Caption dropout on teacher (2026-07-02 implementation_spec 반영)

**Scope 축소 (2026-07-02).** Implementation_spec §8-2 는 caption dropout 만 유지, video dropout 은 제거. 이유. Video 는 modality dominance 의 원흉 이므로 dropout 으로 다양성 만드는 것 이 아니라 아예 학습 시 caption 을 확률 적 으로 빼서 teacher 가 caption 없이도 video+brain 만으로 잘 학습 되도록 강제. Video 는 teacher 에서 항상 유지.

- **구현 위치**. Teacher 학습 loop (§8.6.1 teacher input). Student 도 학습 시 caption 을 받는 상황 (rare, config option) 이면 동일 적용.
- **확률**. p_drop=0.5 default (sweep {0.0, 0.3, 0.5, 0.7}).
- **Mask + padding**. Position 유지 (caption field 를 masked padding token 으로 대체).
- **이중 목적**. (a) Teacher 가 caption 없는 forward pass 도 잘 하도록 훈련 (student 추론 form 이 caption 없음), (b) Student 가 teacher 의 다양성 을 흡수 하여 caption 없는 학습 신호 를 실질 적 으로 받음.
- **Video dropout 은 제외**. Red-team recommendation 18 의 "video+caption 둘 다" 는 caption 만 으로 축소 (implementation_spec 이 canonical). Video 를 학습 시 빼면 teacher 의 시각 anchor 가 흔들려 학습 자체 가 불안정.

**이전 spec (late-3, superseded).** Video / caption 각각 p=0.3 mask. 폐기.

### 8.6.3 P2-C alignment 의 exclusion rationale

- P2-A (teacher-side dropout) = teacher 가 video 에만 기대지 않도록 만드는 장치.
- P2-C alignment = brain representation 을 video representation 에 가깝게 당기는 장치.
- 두 force 의 방향 정반대 → structural conflict.
- Phase 1 의 video 의 0.97 dominance (CLIP video probe valence AUROC) 상황 에서 alignment → brain encoder 가 video 흉내 표현 으로 수렴 → 입력 leakage 의 차단 이 representation 정렬 로 우회 → leakage 부활.
- Brain 의 unique contribution 보존 이 목표 인데 P2-C 는 brain 을 video 의 그림자 로 만드는 가장 위험한 장치.
- 향후 video 가 약한 modality 의 setting 에서 재고.

### 8.6.4 Sanity comparison (red-team recommended)

Student-from-teacher (P2-B) vs student-from-hard-label (Track A A4) 을 같은 brain-only input 으로 비교. Tie within noise 면 distillation 이 overhead 로 판정, P2-B 자체 재고.

---

## 8.7 Pre-registered success criterion (2026-06-30 lock)

### 8.7.1 gap_filled formula

```
gap_filled = (best_encoder_brainonly - ridge) / (noise_ceiling - ridge)
```

- `best_encoder_brainonly`. Stage 1 의 E1-E4 중 best 의 brain-only accuracy (high-D structure preservation metric).
- `ridge`. Phase 1 의 E2 ROI ridge 의 같은 34D task 의 accuracy.
- `noise_ceiling`. Stage 0 의 4 estimator 의 consensus value.

### 8.7.2 Case I/II/III pre-registered thresholds

| Case | Condition | Outcome | Action |
|------|-----------|---------|--------|
| I | noise_ceiling - ridge < 0.05 | R0 realized | Framework reframing 필요. Negative outcome 도 R0 의 실증 으로 publishable. |
| II | noise_ceiling - ridge = 0.05 - 0.15 | Narrow headroom | Encoder competition 진행 하되 effect size 보고 시 reservation 명시. |
| III | noise_ceiling - ridge > 0.15 | Wide headroom | Encoder competition 정상 진행. gap_filled 의 ranking 이 main result. |

학습 시작 *전* 에 lock. Post-hoc threshold reframing 금지.

### 8.7.3 Primary metric 의 변경

절대 accuracy 가 아닌 *high-D structure preservation* 이 primary.
- Per-emotion correlation (34 category 의 prediction-target Pearson r).
- Rare-emotion recovery (frequency-imbalance 하 의 rare category 의 recovery rate).
- Inter-dimension correlation preservation (predicted vs target 의 34×34 correlation matrix 의 Frobenius norm).
- Dimension compression curve (k 차원 의 reduction 의 성능 저하).

### 8.7.4 Ridge baseline reframing

Ridge 는 *sanity-check reference* on same 34D task. *Floor to beat 아님*. Ridge 0.72 (valence binary) 는 우리 34D task 의 metric 과 같은 자 위에 있지 않음.

### 8.7.5 Negative outcome reporting spec

Distillation 의 boost 가 near-zero 가능. 그 경우 의 publishability 의 minimum.
- Variance partitioning. Teacher 의 accuracy 의 modality 별 unique contribution decomposition.
- Transfer gap analysis vs noise ceiling. Student 의 brain-only accuracy 와 teacher 의 brain-only accuracy 의 gap 의 noise ceiling 대비 비율.

---

## 8.8 Caption-video overlap 대응 (2026-06-30 추가)

Caption 과 video 는 같은 사건 을 서로 다른 추상화 수준 에서 기술 → 일부 겹침 은 구조적, 결함 아님. Video 의 고유 기여 는 얼굴 표정 / 움직임 / 구도 같은 저수준 지각 표상. Caption 의 고유 기여 는 인물 관계 / 사회적 상황 같은 고차 의미. 두 modality 가 완전 히 직교 하면 오히려 둘 중 하나 가 불필요 하다는 뜻.

**진짜 리스크.** Caption 의 시각 관련 성분 이 이미 강한 video 와 합쳐져 teacher 가 시각 으로 과결 을 내고, brain 고유 기여 가 학습 신호 에서 지워지는 것.

### 8.8.1 검증 절차

1. **Video residualize on caption.** Caption embedding 에서 video 로 예측 가능한 성분 을 linear regression 으로 제거 → 잔차 만 caption slot 에 입력. 잔차 조건 의 성능 이 원본 caption 조건 과 유사 하면 caption 의 고유 기여 가 살아 있음, 크게 떨어지면 겹침 이 지배적.
2. **Modality ablation.** Full (brain+video+caption), no-caption (brain+video), no-video (brain+caption), brain-only 의 4 조건 학습. 각 조건 별 gap_filled 계산. Caption 을 뺐을 때 성능 이 얼마나 떨어지 는지 = caption 의 고유 기여.
3. **초기 layer 하강 은 회피.** 겹침 을 줄인 다고 video 를 low-level layer embedding (e.g., VGG19 초기) 으로 내리면 감정 관련 시각 정보 자체 를 잃음. CCN 결과 (brain-aligned subspace 는 V-JEPA2 마지막 hidden state 에서 나옴, 저수준 residualize 후 에도 categorical 연속 성 유지) 가 이 결정 을 뒷받침. 고차 layer 유지 + 잔차 분석 이 옳은 방향.

### 8.8.2 Caption 중립성 검증

MindCaptioning 은 감정 / 해석 없는 중립 서술 로 규정. 그러나 규정 인용 만 으로 는 부족. Caption sample 을 실제 로 읽어 감정 단어 / 명시적 해석 부여 를 표본 검증. 검증 스크립트 `project/shared/code/tools/verify_caption_neutrality.py` (S7 에서 작성 예정, Cowen 34 + V/A vocabulary substring match + sample 인간 검토 100 개).

---

## 8.9 2-stage validation order (2026-06-30 추가)

Framework 의 검증 은 두 단계 로 분리. Context (video + caption) 의 boost 를 논하기 전 에 context 없이 도 encoder 별 신호 가 나오는지 를 먼저 확인.

**Naming 명확화.** Track A / Track B (상위) 와 curriculum sub-stage (하위) 를 구분.

- **Track A. Direct supervised (context 없음, brain-only)**. Track A 안 에서 curriculum stage 1 → 2 → 3 → 4 순차.
- **Track B. Distillation (teacher context + student brain-only)**. Track B 안 에서 도 curriculum stage 1 → 2 → 3 → 4 순차 (teacher 도 동일 curriculum).

### 8.9.1 Track A. Teacher context 없이 direct supervised MSE (E1-E4 encoder ablation)

- Teacher / student 구분 없음. E1-E4 각 encoder 를 brain-only 입력 으로 학습.
- Loss = subset per-emotion MSE (§8.3), z-score preprocessing (§8.2) 후 학습.
- Curriculum sub-stage.
  - A1. Top-1 subset MSE. 자극 별 1 개 감정 만 target. Sanity.
  - A2. Top-2 subset MSE.
  - A3. Top-k subset MSE (k 가변, rating threshold 기반).
  - A4. Full 34D independent MSE. Section 9 의 최종 target.
- Video / caption 는 입력 에서 완전히 제거. brain-only.
- 목적. Encoder 효과 만 순수 하게 측정. Leakage 근본 차단. Encoder 순위 자체 를 단독 발표 가능. Curriculum 은 stepwise validation.
- 산출. E1-E4 의 gap_filled (Stage 0 noise ceiling 기준, A4 결과 기준) + per-stimulus profile shape similarity.

### 8.9.2 Track B. Distillation 추가 (Track A best encoder 1 개 만, 2026-07-03 scope 확정)

**Scope**. E1-E4 각각 Track B 를 돌리지 않음. Track A 에서 확정 된 **best encoder 1 개** 만 Track B 로 진입. Spec §13 은 이론 매트릭스, 실행 은 여기 규정 이 우선.

**Framework 검증 축**. Track B 의 primary question 은 "context (video + caption) 가 brain-only 예측 을 얼마나 끌어 올리는가". "어느 encoder 가 distillation 과 잘 맞는가" 가 아님. Encoder 순위 는 Track A 에서 이미 확정.

- Track A 의 best encoder 위 에 teacher (brain+video+caption) 학습.
- Teacher 도 curriculum B1 → B4 순차. 각 stage 의 teacher 34D soft label caching.
- Student (brain-only) 가 teacher 34D 를 MSE 로 재현 (§8.4). Student 도 curriculum 순차.
- 목적. Context 가 brain-only 를 얼마나 끌어올리는지 를 별도 로 검증. 끌어 올리지 못하면 P2-B 자체 의 실증 이 부정적 결과 로 publishable.
- 산출. Student 의 gap_filled (B4 기준) vs Track A best 의 direct-supervised (A4 기준) 의 delta = **context lift** (framework 검증 의 headline).

**Track B 성공 판정 = context lift + distillation 검증 둘 다 (2026-07-07 추가, 필수).**

Context lift (성능 상승) 만 으로 는 부족. B2 baseline 에서 video (CLIP 0.60) >> brain (0.30) 이 확인 됨. Distillation 이 student 를 brain 자체 정보 로 학습 시키는지, 아니면 video 지식 을 우회 주입 하는지 를 반드시 구분. Video 우회 주입 을 "brain decoding" 으로 오인 하면 spine 붕괴.

- **검증 A. Variance partitioning.** Student 예측 성능 을 brain 설명 부분 vs video 설명 부분 으로 분해. Distillation 이 brain 고유 성분 을 키웠는지, video 공유 성분 만 키웠는지 판정.
- **검증 B. Brain-ablated student.** Brain 을 shuffle / 제거 한 student 의 남는 성능. 크게 안 떨어지면 student 가 brain 을 안 쓴다는 경고 (video 우회 주입 신호).
- 두 검증 을 통과 해야 Track B 성공. §9.2 variance partitioning 과 연결.

### 8.9.3 Publishability guarantee

Stage 1 만 성공 하면 modular encoder ablation + high-D readout 이 하나 의 contribution 으로 발표 가능. Stage 2 가 실패 해도 P2-B distillation 의 limits 가 별도 의 findings 로 정리.

---

## 9. Evaluation framework

### 9.0 Primary metric 의 위치

절대 accuracy 가 primary 아님. Primary 는 **1차. 고차원 구조 보존 (headline = per-stimulus 34D profile shape) + LOSO cross-subject 일반화**. 2 차 가 절대 accuracy 와 ridge sanity check.

**Loss ≠ metric.** Loss (MSE) 는 학습 을 굴리는 연료. Metric 은 결과 를 채점 하는 성적표. Headline metric 은 개별 감정 점수 정확도 가 아니라 영상 하나 에 대한 34 개 숫자 의 전체 모양 이 정답 모양 과 닮았는지.

| 우선순위 | 지표 | 이유 |
|---------|------|------|
| 1차 headline | Per-clip 34D profile correlation. **Pearson r 과 Spearman ρ 둘 다** 계산 후 clip 평균 (implementation_spec §9-1) | 이 영상 이 어떤 감정 윤곽 을 가지는지 를 맞히는 것 이 우리 가 원하는 것. 두 지표 를 함께 보고 하여 rank 안정성 도 검증 |
| 1차 | Per-emotion Pearson r (감정 별 로 stimulus 간 correlation) | 감정 별 로 signal 잡히는지 |
| 1차 | Rare-emotion recovery (frequency 하위 10 감정 의 profile shape 정확도) | z-score 로 rare emotion 신호 살아 있는지 실증 |
| 1차 | 34×34 inter-dimension correlation matrix Frobenius norm (predicted vs target) | 감정 간 관계 (기쁨-슬픔 상관 등) 보존 |
| 1차 | Cross-subject 일반화 (LOSO) | 공통 감정 표적. 5 subject pool 안 에 갇히면 spine question 이 안 성립 |
| 2차 | Dimension compression curve (k 차원 reduction 후 성능 저하) | 고차원 성분 이 실제 로 유의한지 |
| 2차 | 절대 accuracy (참조 값) | Ridge 와 같은 자 위 |
| 2차 | ROI ridge sanity check | Framework 가 ridge 가 못 잡는 차원 독립 고차원 구조 를 잡는지. Ridge 를 이기는 것 자체 가 목표 아님 |

Ridge 0.72 는 valence binary 특정 숫자, 34D task 의 floor 아님. Ridge 는 같은 34D task 위 에서 함께 보고 하는 참조 baseline, framework 가 반드시 이겨야 하는 대상 이 아니다.

### 9.1 Baseline ladder

| Baseline | 설명 | 위치 |
|----------|------|------|
| Chance | Label permutation 의 평균 metric | `project/code/evaluation/chance_baseline.py` |
| ROI mean + Ridge | Phase 1 의 best baseline | 재활용 `project/shared/code/probes/run_unified_probe.py` |
| Phase 1 best BFM (BJ resting + Ridge) | Phase 1 의 BFM 의 best frozen probe | 재활용 |
| Video-only | Vision encoder + classifier head (brain 제외) | `project/code/evaluation/video_only.py` |
| Caption-only | LLM (text-only, brain + video 제외) | `project/code/evaluation/caption_only.py` |
| Brain-only (new spine encoder) | NV3 encoder + LLM (video + caption 제외) | trainer 의 modality mask |
| Brain + Video | brain + video, caption 제외 | trainer 의 modality mask |
| Brain + Caption | brain + caption, video 제외 | trainer 의 modality mask |
| Video + Caption | video + caption, brain 제외 | trainer 의 modality mask |
| **Full multi-modal** | brain + video + caption (NV1 main) | trainer 의 default |

### 9.2 Variance partitioning

7 modality combination 의 각 metric 차이 → unique vs shared vs joint variance 의 decomposition. 자극 (stim) level + subject level 2 방향.

N=5 의 subject d.f. 의 statistical power limit 을 method section + limitation 에 명시. claim 은 *trend-level* 로.

### 9.3 Ceiling anchor

- **Inter-rater ceiling**. Cowen 34 rater 의 half-split agreement. 자극 별 distribution 의 noise ceiling.
- **Inter-subject ceiling (brain side)**. 5 subj 의 brain RDM 의 mean cross-subject Spearman r.
- Model performance 의 ceiling 대비 비율 reporting.

### 9.4 Dissociation

- **Decoding accuracy vs RSA correlation**. EmoMind 의 결과 (decode 0.97 vs RSA 0.09) 와 의 비교. dissociation 의 우리 result 의 자체 측정.
- **Visual confound vs emotion-specific**. variance partitioning 의 부산물 + visual feature (CLIP feature) 의 control regression.

### 9.5 LOSO

5-fold by subject. 4 subj train → 1 subj zero-shot. ICL ref 를 *cross-subject* 로만 (transfer evaluation 의 ICL slot).

### 9.6 Cross-subject external test (MindCaptioning, 2026-07-02 정정)

**Cross-subject 이지만 cross-stimulus 는 아님.** Implementation_spec §5-4, §9-4 반영.

- MindCaptioning (Horikawa 2024 Science Advances 2025) = **6 subject, 약 2108 clip**, 중립 caption. Horikawa 2020 (5 subject) 과 subject 가 겹치지 않으므로 cross-subject.
- **그러나 stimulus 는 Cowen 계열 과 상당 부분 겹침** → cross-stimulus 아님.
- **리포트 필수 caveat**. 평가 리포트 마다 "cross-subject external test, NOT cross-stimulus" 를 명시 출력. 이 구분 을 흐리면 over-claim.
- 절차 (§5-4). MindCaptioning clip ↔ Cowen clip 대응 표 → 겹치는 clip 에만 Cowen 34D 라벨 매핑 → 겹치지 않는 clip 제외 (제외 수 로그 필수) → train 통계 로 z-score (test 통계 사용 금지).

### 9.7 Cross-stimulus 평가 (optional)

Horikawa 내부 에서 stimulus level held-out split (config `data.holdout_stimuli`). Cross-stimulus 일반화 검증 은 이 slot 에서. MindCaptioning 은 이 slot 에 해당 하지 않음.

### 9.8 Cross-cohort (Emo-FilM, stretch)

Horikawa → Emo-FilM. 자체 학습 후 zero-shot transfer + per-cohort fine-tune 의 두 condition. Emo-FilM 의 다운로드 + preprocessing 이 prerequisite (S11 후반).

---

## 10. Token budget + attention cost + training time

### 10.1 Estimated prompt length (per trial)

| Component | Token count (estimate) |
|-----------|------------------------|
| System prompt | 80 |
| Brain start/end + brain tokens | 5 + Nb |
| Video start/end + video tokens | 5 + Nv |
| Caption start/end + caption text | 5 + Nc |
| Instruction start/end + instruction | 5 + Ni |
| Output | 10-50 |

Nb (raw ROI) ≈ 5-10 (T_brain median). Nb (BFM) ≈ 5-10. Nv (V-JEPA2, 8 frame × 16 patch) ≈ 128. Nc ≈ 40. Ni ≈ 200 (34-cat inventory).

**Per-trial total ≈ 80 + 10 + 130 + 50 + 210 + 30 ≈ 510 token**. ICL 사용 시 × ICL_rounds.

### 10.2 Attention cost

Qwen3-VL 4B 의 attention. seq 510 + batch 4 + 32 layer × 32 head × 128 head_dim. flash-attn 2 가정 시 step time ≈ 0.4 sec (A100). gradient checkpoint 권장 (memory 50%).

### 10.3 Training time estimate

| Stage | Trial 수 | Epoch | Batch | Step | Wall (A100, 1 GPU) |
|-------|----------|-------|-------|------|---------------------|
| Stage 1 | 10925 | 25 | 4 | 68281 | ~7.6 hour |
| Stage 2 | 10925 | 17 | 4 | 46431 | ~5.2 hour |
| Stage 3 | 10925 | 17 | 4 | 46431 | ~5.2 hour |
| Stage 4 | 10925 | 40 | 4 | 109250 | ~12 hour |

4 stage 의 sequential = ~30 hour per encoder × vision × caption combination. encoder 4 변종 × vision 1 default × caption 1 default = ~120 hour. ablation 추가 시 GPU month scale.

S11 의 ablation 은 *sparse marginal sweep* 으로만 실행.

---

## 11. Open implementation questions

각 question 은 S7-S11 의 specific gate 에서 decision point.

1. **Token assembler 의 modality position embedding 의 sharing 정책**. fresh learnable per modality 가 default. backbone 의 token embedding 의 weight tying 시도 여부.
2. **Brain token 의 dimensionality reduction.** raw ROI 의 450 → D_LLM (예. 3584 for Qwen3-VL 4B) 의 linear projection vs MLP. linear default, MLP 의 effect 측정 필요.
3. **Video frame 의 temporal alignment.** Horikawa 의 8 sec clip 의 frame uniform 8 sample vs HRF-aligned. brain 의 BOLD lag 와 의 alignment 의 effect.
4. **Caption length 의 cutoff.** MindCaptioning 의 length 분포 vs 우리 generated 의 length 분포 가 다름. cutoff 통일 의 effect.
5. **Stage transition 의 weight inheritance.** Stage 1 checkpoint 의 LoRA + adapter 의 100% inherit vs Stage 1 의 backbone + Stage 2 의 new LoRA 의 reset.
6. **Class weighting 의 stage 별 변화.** Stage 1-3 의 hard class weight vs Stage 4 의 KL 의 implicit weighting 의 균형.
7. **Auxiliary L_recon 의 λ 값.** 0.0 / 0.1 / 0.3 의 grid 의 S9 smoke 후 결정.
8. **ICL ablation 의 trigger 조건.** Single-trial default 의 성능 이 baseline 못 넘으면 ICL 시도. 또는 LOSO setting 에서만 ICL 사용.
9. **POYO ablation 의 priority.** S8 main 에 포함 vs supplementary appendix. publishability 의 marginal contribution 평가 필요.
10. **MindCaptioning vs 우리 generated 의 simultaneous use.** 한 trial 에 둘 다 input 으로 줄지 (text token 의 concat), 둘 중 하나만 줄지 (condition switch). 둘 다 = redundancy 증가 + token cost.
11. **Stage 4 의 KL target smoothing.** Dirichlet prior alpha=0.1 vs alpha=0.01 vs none. minority class 의 학습 안정성 vs target sharpness 의 trade-off.
12. **Cross-cohort 의 Emo-FilM 의 rating schema 정합성.** Cowen 34 의 schema 와 의 mapping 가능 여부. mapping 안 되면 cross-cohort 의 *transferable subset* 으로 축소.
13. **Caption neutral 의 검증** (2026-06-30 추가, pending). MindCaptioning 의 caption 의 affect leakage 여부 의 sample 검증. Cowen 34 + V/A vocabulary 의 substring match. strict factual ("a man walks") = leakage 작음, affect-laden ("joyful walking") = leakage 큼. 검증 전 까지 caption leakage 의 risk 는 미정.
14. **Stage 0 timing** (2026-06-30 추가, 2026-07-07 정정). Noise ceiling estimation 의 실행 시점 = Stage 1 의 학습 *전*. Estimator = brain cross-subject ISC + repeated-trial split-half + label crowd split-half + Lage-Castellanos 2019 formula. **Cowen concordance 54% 는 estimator 에서 제외** (categorical 일치율 이라 continuous metric 과 mixing 불가, §8.5.4). Output 의 consensus 가 noise_ceiling 의 value.
15. **gap_filled threshold values 의 확정** (2026-06-30 추가, preliminary). Case I (< 0.05) / Case II (0.05-0.15) / Case III (> 0.15) 의 boundary 는 preliminary. Stage 0 의 estimator variance + literature consensus 의 review 후 final lock. 학습 시작 전 의 lock 가 필수.
16. **Projector token 개수 (bottleneck width)** (2026-06-30 추가). Brain / video embedding 을 몇 token 으로 압축 하는가 가 34D 고차원 구조 보존 과 직결. Nb, Nv 각각 (8 / 32 / 128) grid 의 S9 smoke 후 결정. Token 이 너무 적 으면 34D 구조 가 배관 에서 깎임.
17. **Caption dropout 확률** (2026-06-30 추가, OD-P). Student 학습 시 caption field 를 확률적 으로 dropout. 0.5 / 0.7 / 0.9 grid 후 결정. Teacher-student prompt asymmetry 완화 와 brain-only 강제 학습 의 이중 목적.
18. **Video residualize on caption 절차** (2026-06-30 추가). Caption embedding 에서 video 예측 가능 성분 제거 방법. Linear regression fit 위치 (training set only) + 잔차 조건 vs 원본 caption 조건 의 성능 delta 로 caption 고유 기여 판정. Layer 는 고차 유지, 초기 layer 하강 회피.
19. **Stage 1 vs Stage 2 sequential vs parallel** (2026-06-30 추가). Stage 1 (context 없는 direct 34D supervised) 완료 를 gate 로 삼아 Stage 2 (distillation) 진입 vs 두 stage 병행. Sequential 이 default (Stage 1 만 성공 해도 publishable, Stage 2 실패 도 별도 finding).

각 question 의 decision 은 `project_decisions.md` 의 후속 entry 에 추가.

---

## 12. Cross-references

- **Code 구현 명세**. `docs/notes/implementation_spec_20260702.md` (DECIDED / OPEN / CAUTION, config schema, repo layout, Acceptance 기준, 34개 감정 순서). Code implementation 시 canonical spec.
- Spine narrative. `Paper/framework_EN.md`, `Paper/framework_KR.md`.
- Decision log. `docs/notes/project_decisions.md`.
- Negative result evidence. `docs/reports/d1_brainvlm_va_negative_result_20260628.md`.
- Phase 1 audit. `docs/reports/phase1_audit_20260604/`.
- Action plan. `ACTION_PLAN.md`.
- Compact context. `CONTEXT_EMOBRAIN.md`.
- 34 감정 canonical 순서. `project/shared/data/cowen34_order.txt`.
