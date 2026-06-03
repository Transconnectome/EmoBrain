# FEEL Masterplan v4 final (Universal Emotion Code)

작성. 2026-06-02 v4 final.
Branch `v4_20260602_perlmutter`. Driver = 교수님 면담 + emovi-method-critic 적대적 검토 + labserver branch framing 통합 + 사용자의 "video baseline 넘는 게 big Q 가 아니다, dataset-specific SQ 가 잘못" 지적 + 사용자의 "FM 과 연결되는 깊은 science question" 요구.

---

## 0. 한 줄 요약

Brain 에 paradigm, label, subject 의 surface variation 을 가로지르는 universal emotion code 가 존재하는지를 multi-source naturalistic emotion fMRI 의 SSL pretrain + adaptation 으로 학습하고 검증한다.

Naming dual-track. 내부 / repo / 연구실 = FEEL = Foundation Model for Emotion Embedding Learning. Paper title = "Universal Emotion Code in Naturalistic Brain Data" 또는 "Transferable Emotion Brain Foundation Model" (Bommasani 2021 FM 정의 scale 미달 reviewer bias 회피).

---

## 1. Big Question

> Brain 에 paradigm, label taxonomy, subject 의 surface variation 을 가로지르는 *universal emotion code* 가 존재하는가? Multi-source naturalistic emotion fMRI 의 adaptation 으로 그 universal code 를 학습하고 검증할 수 있는가?

핵심 scientific bet. Wager-style universal pain signature 시도의 emotion 판. Affective neuroscience 의 미해결 질문 (universal vs idiosyncratic emotion representation) 에 falsifiable evidence.

"Brain 이 video 를 이겨야" 전제 없음. Phase 1-2 measurement 에서 group-level V/A 의 video saturation 이 이미 확정됐음. Universal code 가 존재한다면 group-level emotion attribute 가 아니라 invariance / cross-dataset preservation 의 axis 에 있어야 함.

---

## 2. Sub-claims (falsifiable)

1. **Multi-source pretrain invariance**. Universal code 가 존재한다면 multi-source pretrain (Horikawa + Emo-FilM + StudyForrest + Affective Videos) 의 representation 이 single-source pretrain (Horikawa only) 보다 cross-dataset transfer 에서 의미 있게 더 invariant 해야 한다.
2. **ROI localization**. Universal code 는 brain 의 특정 ROI / network 에 localize 되어야 한다. Cowen 2020 의 transmodal (STS, TPJ, mPFC) 가설과 align 또는 disagree.
3. **Subject-invariant alignment**. Universal code 는 subject-invariant SSL 후 같은 stim 의 다른 subject 의 representation 이 의미 있게 alignment 되어야 한다.
4. **Null hypothesis**. 위 세 metric 모두 acquisition floor 안 → "universal code 없음, emotion 은 paradigm/context/subject-specific representation" 결론. 그 자체로 publishable negative result.

---

## 3. 2 Main Track + 1 Supplementary

### Track A (main). BFM SSL pretrain + LoRA adaptation

**Sub-question**. Multi-source SSL pretrain 이 emotion-relevant invariance 를 emerge 시키는가? Subject-invariant / multi-source masked / brain-stimulus contrastive 의 marginal contribution?

**Universal code 측정 방식**.
- Pretrain 후 representation 의 cross-dataset invariance metric
- Subject alignment metric (학습 후 같은 stim 의 다른 subject 의 representation cosine)
- Paradigm alignment metric (Horikawa vs Emo-FilM vs StudyForrest 의 같은 emotion category 의 RDM preservation)
- ROI-wise transfer matrix

**SSL pretrain 후보 5 (우선순위 명확)**.

**Priority 1 (둘 다 main, 반드시 진행)**

(1) **Subject-invariant SSL**.
- 뭘 하나. 같은 video 를 본 5 subject 의 brain response 가 서로 비슷해지도록 contrastive 학습.
- 구체. Stimulus k 를 subject A 가 보고 → brain_Ak. 같은 k 를 subject B 가 봐서 → brain_Bk. 다른 stim m 의 brain_Am. Loss. brain_Ak ↔ brain_Bk cosine ↑, brain_Ak ↔ brain_Am cosine ↓. InfoNCE.
- Universal code 연결. Subject 간 invariance = universal code 의 정의. 학습 후 subject alignment 가 직접 evidence.
- 자원. GPU 며칠.

(2) **Multi-source SSL (masked autoencoder, BrainLM-style)**.
- 뭘 하나. Horikawa + Emo-FilM + StudyForrest + Affective Videos 의 fMRI 모두 모음. Brain 의 일부 ROI / time window 가리고 예측.
- 구체. 450 ROI 중 30% 가린 후 나머지 70% 로 예측. MSE loss. 4 dataset 같은 model. Dataset 별 헤더 (token embedding).
- Universal code 연결. Paradigm 간 invariance evidence. Single-source vs multi-source 의 representation invariance 차이가 universal code 의 multi-paradigm 존재 증거.
- 자원. GPU 1-2 주.

**Priority 2 (main, 가능하면 진행)**

(3) **Brain-stimulus contrastive (TRIBE-style)**.
- 뭘 하나. Brain representation 과 video representation (V-JEPA2 / CLIP) 의 alignment.
- 구체. Brain_k 의 encoder output 과 Video_k 의 V-JEPA2 feature 의 cosine ↑, 다른 stim ↓. Brain-video pair contrastive.
- Universal code 연결. Universal code 가 stimulus-driven 이면 alignment emerge. Brain unique 가 stimulus 와 분리된 axis 면 alignment 안 됨. 두 경우의 분리 측정.
- 자원. GPU 며칠.

**Priority 3 (optional, 시간 남으면)**

(4) **Curriculum pretrain**. Resting (Brain-JEPA prior) → naturalistic movie SSL (HCP 7T movie) → emotion-aware (Horikawa Cowen) 3-stage. Stage 별 prior contribution ablation.

(5) **Distillation**. 큰 BFM 의 representation 을 작은 specialized model 로. 부수적, universal code 의 효율적 표현 방법.

**Adaptation**. SSL pretrain 후 Brain-JEPA backbone 위에 LoRA. Emotion-text space (sentence-transformer mpnet-base 또는 CLIP-text) 와 contrastive alignment. Multi-task supervision (V/A + 34-cat + OV description).

**Go**. Multi-source pretrain 후 single-source pretrain 대비 cross-dataset invariance metric 의 의미 있는 향상 + 적어도 transmodal ROI 에서 subject alignment positive.

**Pivot**. Multi-source 의 invariance 이득 = 0 → "paradigm-specific representation" 결론. Negative result paper.

### Track B (main). Brain+Video framework + task 재설계

**Sub-question**. Brain unique contribution 의 universal component 가 무엇인가? Video 가 못 잡는 brain emotion variance 가 cross-dataset 으로 preserve 되는가?

**Universal code 측정 방식**.
- Phase 2 의 4 architecture (A/B/C/D joint) framework 그대로 reuse
- 단 task 가 V/A 가 아니라 *universal code probe*. 예시.
  - Task 1. Cross-dataset emotion-text alignment. Brain → emotion-text space 의 사영이 다른 dataset 에서도 같은 axis 로
  - Task 2. Same-emotion RDM preservation. 같은 emotion label 의 다른 source (Horikawa vs Emo-FilM) 의 brain representation 의 RSA / CKA
  - Task 3. ROI-wise universal map. 어느 ROI 가 multi-source 위에서 invariant
- Brain-only vs Brain+Video 차이 = universal code 의 *brain-unique* component 의 직접 evidence

**Phase 2 measurement 의 의미**. 이미 group-level V/A 에선 joint Δ = +0.001 (noise). 즉 group-level V/A 의 universal code 는 brain unique 가 아니라 video shared. New task design 으로 multi-dim / cross-dataset axis 의 brain unique 를 다시 측정.

**Go**. New task 에서 Brain+Video joint 가 video-only baseline 보다 의미 있게 향상 + 그 차이가 cross-dataset 으로 preserve.

**Pivot**. New task 에서도 joint = video → brain unique universal component 없음. Group-level emotion 의 brain unique 가 어떤 axis 에도 없음 결론.

### Track C (supplementary). BrainVLM generative path

**Sub-question**. Universal code 가 generative 표현 가능한가? Free-form caption / OV label 의 cross-dataset consistency?

**Universal code 측정 방식**.
- Phase 3a 의 fold 1 학습 그대로
- Inference parsing fix (V_reg r = NaN 의 XML parsing 문제 해결)
- Generated caption 의 OV label / Cowen 34-cat 매핑 + cross-dataset consistency 측정
- Supplementary figure 1-2 개. Main contribution 아님.

**왜 supplementary 인가**.
(a) LLM 의 visual semantic bias 가 brain invariance 측정 가림
(b) Generation noise 가 reliability 낮춤
(c) Phase 3a inference 자체 약함 (V_reg r = NaN, MAE 2.55, scale mismatch)
(d) Multi-source 확장 자원 부담 큼

본격 진행은 risk 대비 evidence 약함. Supplementary 로 demote.

---

## 4. Build recipe (Track A + B 공통 backbone)

5 subj × 2185 stim 으로는 emotion brain FM 을 from-scratch pretrain 불가. **Pretrained brain backbone + 소수 multi-source SSL pretrain + emotion-text space adaptation** 이 honest scope.

### Architecture (5 block)

```
fMRI ─► [A] 450-ROI parcel (Schaefer-400 + Tian-50, scanner / dataset 무관 substrate)
        │
        ▼ [B] Brain-JEPA backbone (pretrained on ABCD resting)
        │
        ▼ [C] Track A SSL pretrain
            (1) Subject-invariant contrastive  ← priority 1
            (2) Multi-source masked AE          ← priority 1
            (3) Brain-stimulus alignment        ← priority 2
        │
        ▼ [D] LoRA adaptation
        │
        ▼ projection
        z_emo ─► [E] frozen emotion-text embedding space (sentence-transformer / CLIP-text)
                  target = embed(Cowen 34-cat + 14-dim 문장화 또는 OV description from MLLM)
                  loss  = contrastive InfoNCE (brain ↔ matched emotion-text)
                        + 보조 regression (V/A, 34-dim)
                        + caption baseline 대비 brain-only delta (confound control)
        │
        ▼ multi-source pooling
        ▼ 평가 (freeze 후)
            Track A invariance metric (subject align, paradigm align, ROI-wise)
            Track B brain unique cross-dataset RSA (Brain+Video framework reuse)
            Track C BrainVLM Phase 3a parsing fix (supplementary)
```

### Block 별 design choice

| Block | Choice | 이유 |
|---|---|---|
| **A. 입력** | Schaefer-400 + Tian-50 = 450 ROI parcel | Acquisition / dataset 무관 substrate. ComBat harmonization 적용 표면. 4D volume (SwiFT, NeuroSTORM) 도 비교 axis 로 유지 |
| **B. Backbone** | Brain-JEPA (default) | Pretrained on ABCD resting. SwiFT 6 변종, NeuroSTORM 도 swap axis |
| **C. SSL pretrain** | (1) + (2) + (3) | Track A 의 핵심. 우선순위 1 둘은 main, 3 은 가능하면 |
| **D. Adaptation** | LoRA (rank 8-16) | Pretrain prior 보존하며 emotion-specialized reshape. Small data fit |
| **E. Target space** | sentence-transformer (mpnet-base) 또는 CLIP-text (ViT-L/14) frozen | 수천 emotion 개념 geometry. Native label 이름만으로 zero-shot retrieval 가능 |

### Loss (adaptation 단계)

```
L = α · InfoNCE(z_emo, embed(matched_emotion_text))         # contrastive 핵심
  + β · MSE(z_emo @ W_VA, V/A_target)                        # 보조 V/A regression
  + γ · MSE(z_emo @ W_34, Cowen34_target)                    # 보조 34-cat regression
  + δ · KL(softmax(z_emo @ W_34) || Cowen34_soft)            # soft distribution
  + ε · |z_emo - z_caption_baseline|^2                       # caption baseline confound control
```

Default α = 1.0, β = 0.1, γ = 0.5, δ = 0.3, ε = 0.0 (default off, ablation 으로 on).

### Brain encoder 후보 (Block B swap)

| Backbone | 역할 | 상태 |
|---|---|---|
| Brain-JEPA | ROI default (450 in, 768 out) | 추출 완료 (proper mean padding) |
| SwiFT NewE96 | 4D volume default | 완료 (5 padding × 5 subj × 2 init) |
| SwiFT NewE36 / NewE192 / UAH 5M / 51M / 202M | 4D volume size/depth ablation | 진행 중 |
| NeuroSTORM | 4D volume default | 추출 완료 |
| BrainLM | 제외 | 490 TR × A424 atlas 고정 → Horikawa 비호환 |

### 옛 frame 명시적 탈피 (Phase 1-2 measurement 반영)

- ❌ "Brain + video fusion 으로 video 를 넘는다" (Phase 2 D late fusion Δ = +0.001 = noise 로 falsified)
- ❌ BrainVLM token integration 을 main path 로 (V_reg parsing failure, MAE 2.55, scale mismatch → Track C supplementary 로 demote)
- ❌ Late fusion 으로 emotion classification 향상
- ❌ 4 fusion architecture 의 V/A 비교가 main contribution
- ❌ "Brain 이 video 를 이긴다" framing 자체

대신 v4 final.

- ✅ Universal emotion code 의 존재 검증 (Track A SSL pretrain invariance + Track B brain unique cross-dataset preservation)
- ✅ Brain backbone 의 emotion-specialized adaptation (Brain-JEPA + LoRA)
- ✅ Multi-source pretrain 의 invariance emergence (Subject-invariant + Multi-source masked + optional brain-stimulus)
- ✅ Multi-dim emotion-text space 와 contrastive alignment
- ✅ Caption baseline 대비 brain unique variance

---

## 5. Cross-dataset evaluation 4 전략 (metadata 빈곤 해결)

### 전략 1. Shared text-embedding zero-shot (main)

Brain → emotion-text space 사영 후 native label 이름만으로 zero-shot retrieval. 어떤 dataset 의 어떤 label 도 학습 없이 평가 가능.

```
brain_X ─► encoder ─► z_X    (Track A adaptation 후 encoder, frozen)
label_X = ["happy", "sad", ...] ─► sentence-transformer ─► t_X
retrieval = argmax_X cos(z_X, t_X)
metric = top-1 / top-5 accuracy, mean reciprocal rank
```

### 전략 2. Label-space intersection (안전)

Target dataset 의 axis 만 잘라서 평가. 가장 보수적, reviewer-friendly.
- Emo-FilM 13 discrete + 42 CPM 중 Cowen 34-cat 과 closest mapping
- StudyForrest 의 V/A
- Within-dataset Pearson r

### 전략 3. MLLM universal annotator (frozen artifact)

OV-MER (Lian 2025 ICML) 의 label generation pipeline 을 local LLM (Qwen2.5-72B-VL 또는 Llama-3.3-70B-VL) 으로 frozen artifact 화. GPT-3.5 dependency 제거.

```
Step 1. Horikawa 2185 video 각각에 local LLM 으로 CLUE-Multi 생성
        (text + visual + audio cue 통합 description)
Step 2. 같은 local LLM 으로 CLUE-Multi → open-vocab label set (평균 3-5 개)
Step 3. Frozen artifact 로 release (Hugging Face dataset, hash 명시)
Step 4. 동일 pipeline 을 Emo-FilM / StudyForrest / NNDb 의 video 에 적용
Step 5. FEEL prediction 을 OV label 로 보조 supervision
Step 6. 평가는 set-based F-score (Appendix only)
```

### 전략 4. Representational alignment (label-free)

Stimulus 매칭만 있으면 label 없이 가능. NNDb 같은 label-free dataset.
- Brain RDM (subject × stim) vs caption-derived RDM
- ISC ceiling (subject 간 brain signal 의 inter-subject correlation)

---

## 6. Independent dataset

| Dataset | Subj × Stim | Label | OpenNeuro | 역할 |
|---|---|---|---|---|
| **Horikawa** | 5 × 2185 (1 min clips) | Cowen 34-cat behavioral consensus | Yes | Base / Track A pretrain source / Track B testbed |
| **Emo-FilM** (Cordoni 2025 Nat SciData) | 30 × 14 films (2.5h) | 13 discrete + 42 CPM, 1 Hz, 0-100 | Yes (BIDS) | Track A multi-source pretrain + cross-dataset transfer test |
| **StudyForrest** | 20 × Forrest Gump 2h | 8 portrayed emotion + V/A | Yes | Track A multi-source pretrain + cross-dataset transfer test |
| **NNDb** (Aliko 2020) | 86 × 10 movies | 없음 (label-free) | Yes | 전략 4 RSA (Appendix) |
| **Affective Videos** (ds000205) | 11 × 32×4 trials | V/A | Yes | Track A multi-source pretrain |
| **Koide-Majima** | 옵션 | 80 emotion labels | 접근 의존 | Track A multi-source pretrain (가능 시) |

다운로드 위치 = `data/independent/{emo_film, study_forrest, nndb, affective_videos}/`. Phase 3b W15 에 BIDS 검증 + preprocessing pipeline.

---

## 7. Phase plan (6 month, 4 phase)

### Phase 1. Foundation (Week 1-6) ✅ 완료

3 트랙 병행. 결과 `reports/phase1_wrapup/main.pdf` + `results/phase1/`.

**Finding (numeric)**.
- ROI Schaefer400+Tian50 mean (linear, pooled) V_binary AUROC 0.7889 ± 0.0119
- Best BFM (Brain-JEPA resting zero linear) 0.7402 ± 0.0365
- Best video (CLIP_pretrained) 0.9708
- 결론. ROI mean > all BFM. Brain 정교화 (SwiFT 5M~264M, padding 4 mode) 가 group-level emotion 에 effect 없음.

### Phase 2. 통합 학습 (Week 7-12) ✅ 측정 완료

L1 frozen embedding 주입 으로 3 BFM × 4 architecture 학습 + brain-only 4 method 비교.

**Finding (numeric)**.
- V_binary AUROC. D late fusion 0.9718, A 0.9670, B 0.9663, C 0.9606. CLIP-only 0.9708. **Δ vs CLIP = +0.001 (noise)**
- V_reg Pearson r. A 0.7628 vs CLIP 0.7645 = -0.002
- A_binary AUROC. D 0.8025 vs CLIP 0.8003 = +0.002
- Brain-only best (multitask) V_binary 0.7235
- 결론. 4 fusion architecture 어느 것도 video baseline 위 향상 없음.

**Pivot decision**. "Brain + video fusion 으로 group-level emotion 잡는다" framing 폐기. Universal emotion code 의 invariance / cross-dataset preservation 으로 reframe.

### Phase 3a. BrainVLM (Week 13-15) 🔄 Track C supplementary

Fold 1 학습 완료 (loss 1.94 → 0.151). Inference V_reg r = NaN (parsing), MAE 2.55, scale mismatch.

**Phase 3a 추가 작업 (Track C supplementary 한정)**.
- Inference parsing fix (XML parsing 문제 해결)
- Scale mismatch fix (prompt 1-5 → 1-9 with Cowen 의 actual range)
- Generated caption 의 OV label 매핑 + cross-dataset consistency 측정
- Supplementary figure 1-2 개로 reporting

추가 학습 없음. Main path 아님.

### Phase 3b. Track A SSL pretrain + adaptation (Week 15-20) 🆕 v4 main

**Track 1 (W15). Foundation prep**
- [ ] Independent dataset 다운로드 + BIDS 검증 (Emo-FilM, StudyForrest, NNDb, Affective Videos)
- [ ] 같은 preprocessing pipeline 적용 (Schaefer-400 + Tian-50 parcel)
- [ ] ComBat harmonization (Fortin 2018) wrapper (`code/cross_dataset/combat_wrapper.py`)
- [ ] Acquisition null baseline generator (phase-scrambled + trivial ROI mean)
- [ ] Emotion-text space loader (sentence-transformer mpnet-base + CLIP-text ViT-L/14)

**Track 2 (W16-17). SSL pretrain (1) Subject-invariant**
- [ ] `code/ssl_pretrain/subject_invariant.py` 작성
- [ ] Horikawa 5 subj × 2185 stim 으로 학습
- [ ] InfoNCE loss, brain_Ak ↔ brain_Bk positive
- [ ] 학습 후 subject alignment metric 측정

**Track 3 (W16-18). SSL pretrain (2) Multi-source masked AE**
- [ ] `code/ssl_pretrain/multi_source_masked.py` 작성
- [ ] 4 dataset 통합 dataloader, dataset 헤더 token
- [ ] 30% ROI mask + MSE reconstruction
- [ ] 학습 후 paradigm alignment metric 측정 (Horikawa vs Emo-FilM vs StudyForrest 의 same-emotion RDM)

**Track 4 (W18). SSL pretrain (3) Brain-stimulus contrastive (optional)**
- [ ] `code/ssl_pretrain/brain_stimulus_contrastive.py` 작성
- [ ] V-JEPA2 / CLIP feature 와 brain encoder output 의 contrastive
- [ ] Universal code 가 stimulus-driven 인지의 측정

**Track 5 (W18-19). LoRA adaptation + emotion-text space**
- [ ] `code/cross_dataset/adapt_lora.py`
- [ ] Pretrained backbone + LoRA + emotion-text contrastive
- [ ] 4 supervision target 동시 학습 (V/A + 34-cat + 14-dim + OV)

**Track 6 (W19-20). Universal code 측정**
- [ ] 전략 1 shared text-embedding zero-shot retrieval
- [ ] 전략 2 label-space intersection probe
- [ ] 전략 3 MLLM universal annotator (local LLM frozen artifact)
- [ ] 전략 4 RSA / ISC ceiling
- [ ] ROI-wise transfer matrix (Schaefer-400 17-network)
- [ ] Acquisition null baseline 2σ 검증

**W20 Phase 3b task list (Track A)**
- [ ] 4 dataset preprocessing + ComBat 완료
- [ ] SSL pretrain (1) + (2) 학습 완료, invariance metric 측정
- [ ] (3) brain-stimulus 학습 (가능 시)
- [ ] LoRA adaptation 학습 완료
- [ ] 4 cross-dataset 전략 결과
- [ ] Phase 3b 보고서 (`reports/phase3b_track_a.md`)

### Phase 3c. Track B Brain+Video framework + task 재설계 (Week 15-18) 🆕 v4 main (병행)

**Track 1 (W15-16). Task 재설계**
- [ ] Phase 2 의 4 architecture (A/B/C/D) framework 그대로 reuse
- [ ] Task 가 V/A 가 아니라 universal code probe 로 변경
  - Cross-dataset emotion-text alignment task
  - Same-emotion RDM preservation task
  - ROI-wise universal map task
- [ ] `code/phase2/task_universal_code.py` 신설 (기존 _lib.py 확장)

**Track 2 (W16-18). Brain unique cross-dataset preservation**
- [ ] Brain-only vs Brain+Video joint 의 차이 측정 (universal code probe task 에서)
- [ ] 그 차이의 cross-dataset RSA preservation
- [ ] Caption baseline 비교 (Doerig 2025 control)

**W18 Phase 3c task list (Track B)**
- [ ] Universal code probe task 학습 완료
- [ ] Brain unique 의 cross-dataset preservation 결과
- [ ] Caption baseline variance partitioning
- [ ] Phase 3c 보고서 (`reports/phase3c_track_b.md`)

### Phase 4. Synthesis + submission (Week 19-24)

- W19-20. Cross-evaluation. Track A + Track B 통합 표. EmoViS branch 결과 통합 검토
- W21-22. Paper draft. Skill `scientific-writing` + `peer-review`
- W23. Infographic, README, code release v1.0
- W24. Submission target 결정

**Submission target 후보**.
- Nat Hum Behav, Nat Commun (universal code evidence 강하면)
- NeurIPS main track (multi-source SSL pretrain + universal code 의 methodological novelty)
- NeurIPS dataset & benchmark track (multi-source emotion fMRI 통합 + 4 cross-dataset 전략 + MLLM annotator artifact release)
- Imaging Neuroscience (engineering + cross-dataset)

Paper title 후보 (naming retreat).
- "Universal Emotion Code in Naturalistic Brain Data via Multi-source Self-supervised Adaptation"
- "Transferable Multi-dimensional Emotion Representation from Naturalistic fMRI"
- "Cross-dataset Emotion-aware Brain Encoder via Emotion-Text Alignment"

---

## 8. Critic 7 hit 통합 self-check

| Critic hit | v4 final 의 대응 위치 |
|---|---|
| 1. Q2 (decomposability) 는 tautological | SQ3 W refit 폐기. Universal code 는 W 와 무관, invariance metric 으로 직접 측정 |
| 2. Cross-dataset transfer 의 acquisition confound (Sripada 2020) | Track A 의 acquisition control + Track B 의 ComBat 의무화 |
| 3. 5 subj power 부족 | Open-vocab generalization 강등 (Appendix). Universal code 자체는 multi-source 로 사실상 subject pool 확장 |
| 4. FM naming bias (Bommasani 2021) | Paper title 에서 "foundation model" 명사 자제. Internal FEEL 유지 |
| 5. Caption baseline 부재 (Doerig 2025) | Track A/B 모두 caption baseline 의무화. Brain unique variance 측정 |
| 6. OV-MER GPT-3.5 dependency | 전략 3 local LLM frozen artifact |
| 7. Cowen 34-cat transmodal 한정 | Track A 의 ROI-wise transfer matrix + Sub-claim 2 의 ROI localization |

---

## 9. Go/No-Go Decision Tree

```
Phase 3b (W20 Track A gate)
├── Multi-source SSL invariance metric > single-source SSL 의미 있게
│   AND Subject-invariant SSL 후 subject alignment positive
│   AND Transmodal ROI 에서 universal code emerge
│   → Track A strong positive
├── Multi-source ~ single-source (invariance 이득 없음)
│   → Multi-source SSL fail, paradigm-specific representation 결론
│   → Track A negative result (Sub-claim 1, 2 false)
└── Subject-invariant SSL alignment = 0
    → Subject-specific representation, universal subject code 없음
    → Sub-claim 3 false

Phase 3c (W18 Track B gate)
├── New task (universal code probe) 에서 Brain+Video joint > video-only baseline
│   AND 그 차이가 cross-dataset preserved
│   → Track B strong positive
├── New task 에서도 joint = video
│   → Brain unique universal component 없음
│   → Track B negative
└── Joint > video but cross-dataset 안 preserve
    → Horikawa-specific brain unique. Universal 아님

Phase 4 (W24)
├── Track A + Track B 둘 다 strong positive → Nat Hum Behav / Nat Commun (universal code 존재의 강한 evidence)
├── 하나만 positive → NeurIPS main track / Imaging Neuroscience (partial evidence)
├── 둘 다 weak but methodologically novel → NeurIPS dataset/benchmark track (multi-source SSL recipe + 4 cross-dataset 전략 + frozen MLLM artifact 자체가 contribution)
└── 둘 다 negative → Negative result paper (universal code 없음, emotion 의 paradigm/subject-specific representation evidence)
```

---

## 10. Agent review schedule

| Week | Phase | Agent | Focus |
|---|---|---|---|
| W15 | P3b kickoff | emovi-method-critic | Build recipe + SSL pretrain 1+2+3 의 design choice + ComBat 적정성 |
| W17 | P3b | scientific-critical-thinking | Multi-source SSL 의 invariance metric 의 statistical 적절성 |
| W18 | P3b | emovi-method-critic | Subject-invariant SSL 의 contrastive loss design 의 confound 검토 |
| W18 | P3c | emovi-method-critic | Track B new task 의 brain-only vs joint 의 measurement equivalence |
| W19 | P3b/3c | chavis-antisyc | 결과의 over-claim 방지, transmodal-한정 결과 정직성 |
| W20 | P3b/3c gate | peer-review + chavis-antisyc | Track A/B 결과 종합 over-claim 방지 |
| W21 | P4 | scientific-writing | Draft writing |
| W23 | P4 | peer-review + emovi-review | Manuscript review |
| W24 | P4 | scholar-evaluation | Venue 결정 |

---

## 11. Critical files

### 기존 작업 재사용 (보존)

- `code/bfm_embeddings/_lib/{swift,brain_jepa,neurostorm}.py`. BFM extraction
- `output/embeddings/`. BFM .pt (proper mean)
- `code/probes/run_unified_probe.sh`. Phase 1 unified frozen probe
- `code/phase2/{architectures,brain_only}/`. Phase 2 학습 pipeline (Track B framework reuse)
- `code/brainvlm/{train_brainvlm.py,inference_brainvlm.py}`. Phase 3a (Track C supplementary)
- `results/phase1/*.csv`, `results/phase2/*.csv`. measurement 결과
- `reports/phase{1,2}_wrapup/main.pdf`. Phase 1/2 보고서

### Phase 3b 에 만들 새 파일 (Track A, NEW)

- `code/ssl_pretrain/subject_invariant.py`. SSL (1) subject-invariant contrastive
- `code/ssl_pretrain/multi_source_masked.py`. SSL (2) masked autoencoder
- `code/ssl_pretrain/brain_stimulus_contrastive.py`. SSL (3) brain-video alignment
- `code/ssl_pretrain/_lib_dataloader.py`. Multi-source dataloader (Horikawa + Emo-FilM + StudyForrest + Affective Videos)
- `code/cross_dataset/adapt_lora.py`. LoRA adaptation
- `code/cross_dataset/emotion_text_space.py`. sentence-transformer + CLIP-text loader + Cowen 34-cat 문장화
- `code/cross_dataset/supervision_targets.py`. 4 supervision target generator
- `code/cross_dataset/combat_wrapper.py`. ComBat harmonization
- `code/cross_dataset/null_baseline.py`. Phase-scrambled + trivial ROI mean null
- `code/cross_dataset/eval_strategy1_zero_shot.py`. Shared text-embedding retrieval
- `code/cross_dataset/eval_strategy2_intersection.py`. Label-space intersection probe
- `code/cross_dataset/eval_strategy3_mllm.py`. OV-MER pipeline (frozen local LLM)
- `code/cross_dataset/eval_strategy4_rsa.py`. RSA + ISC ceiling
- `code/cross_dataset/eval_caption_baseline.py`. Caption baseline variance partitioning
- `code/cross_dataset/ov_mer_pipeline.py`. Local LLM open-vocab label generator (frozen artifact)
- `data/independent/{emo_film, study_forrest, nndb, affective_videos}/`. OpenNeuro downloads

### Phase 3c 에 만들 새 파일 (Track B, NEW)

- `code/phase2/task_universal_code.py`. Universal code probe task (cross-dataset alignment / same-emotion RDM / ROI map)
- `code/phase2/train_universal_code_joint.py`. Phase 2 framework 의 universal code task 학습

### 새 결과 디렉토리

- `results/phase3_universal_code/track_a/`. Track A SSL pretrain + invariance metric
- `results/phase3_universal_code/track_b/`. Track B brain unique cross-dataset preservation
- `results/phase3_universal_code/track_c_supp/`. BrainVLM parsing fix + OV label consistency

### 새 보고서

- `reports/phase3b_track_a.md`. Phase 3b (Track A SSL pretrain + adaptation) 보고서
- `reports/phase3c_track_b.md`. Phase 3c (Track B framework + task 재설계) 보고서

### 참고용 외부

- `/pscratch/sd/s/sjmoon/BrainVLM/UMBRELLA_qwen/project/model/patch_embed.py`. fMRI patchifier (Track C)
- `/pscratch/sd/s/sjmoon/EmoViS/study1/results/`. stimulus features
- Cowen 2017 PNAS supplementary
- Fortin et al. 2018 NeuroImage (ComBat)
- Lian et al. 2025 ICML (OV-MER)

---

## 12. Risk register

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Phase 1-2 의 brain group-level emotion 효과 없음 (이미 확인) | (Realized) | (반영됨) | Universal code framing 으로 pivot. Group-level 가 아닌 invariance / cross-dataset preservation 축 |
| Multi-source SSL pretrain 의 dataset preprocessing 부담 | High | High | Phase 3b W15 에서 BIDS 검증 + ComBat 우선. Emo-FilM 우선, Affective Videos 다음 |
| Subject-invariant SSL 의 contrastive loss collapse | Med | Med | LoRA rank ablation. Hard negative sampling. Temperature tuning |
| Cross-dataset transfer 의 acquisition confound (Sripada 2020) | High | Critical | Track A 의 ComBat + 2σ null baseline 의무화 |
| Caption baseline 이 brain-only 와 equivalent (Doerig 2025) | Med-High | Critical | Track A/B 모두 variance partitioning. Negative result 도 정직 reporting |
| OV-MER GPT-3.5 deprecation | Med | Med | Local LLM frozen artifact |
| BrainVLM 추가 학습 risk | (Realized) | Low | Track C supplementary 로 demote, parsing fix 만 |
| 6 month 안에 Track A SSL pretrain 자원 부족 | Med | High | Priority 1 (subject-invariant + multi-source masked) 우선. Priority 2-3 시간 남으면 |
| Cowen 34-cat transmodal 한정 (Cowen 2020) | Med | Med | Track A ROI-wise transfer matrix + Sub-claim 2 의 ROI localization |
| "Foundation Model" naming bias | Med | Med | Paper retreat ("Universal Emotion Code" / "Transferable Emotion Brain Foundation Model"), internal FEEL 유지 |

---

## 13. 교수님 피드백 + critic 7 hit + 사용자 push back self-check

### 교수님 피드백
- **F1 scientific question**. Big Q = "universal emotion code 존재 여부" 가 scientific question. Sub-claim 1-4 가 falsifiable.
- **F2 multi-dimensional representation**. Target hierarchy 에서 V/A 강등, Cowen 34/14/OV-text 승격. Universal code 가 multi-dim invariance 의 brain evidence.
- **F3 independent dataset transfer**. 4 cross-dataset 전략 + multi-source SSL pretrain 자체가 cross-dataset 통합.
- **F4 foundation model**. Build recipe (Section 4) 의 "Pretrained brain backbone + multi-source SSL pretrain + adaptation" 가 FM 의 honest 출처. Naming dual-track.

### Critic 7 hit
1. ✅ Q2 tautological → universal code 는 W 와 무관, invariance 로 직접 측정
2. ✅ Acquisition confound → Track A ComBat + 2σ null
3. ✅ Power 부족 → multi-source 로 subject pool 확장, open-vocab 강등
4. ✅ FM naming bias → paper retreat, internal 유지
5. ✅ Caption baseline 부재 → Track A/B variance partitioning
6. ✅ OV-MER GPT-3.5 → 전략 3 local LLM frozen
7. ✅ Cowen 34-cat transmodal 한정 → Track A ROI-wise matrix

### 사용자 push back
- ✅ "Video 를 이기는가" framing 폐기 → Universal code 의 invariance/preservation 축
- ✅ Dataset-specific SQ 폐기 → 모든 sub-claim 이 dataset-agnostic representation question
- ✅ "FM 과 연결되는 깊은 science question" → Universal emotion code 가 FM 의 methodology 와 1:1 mapping (multi-source pretrain = universal code discovery machinery)
- ✅ Small-data pretrain 방법 명시 → SSL pretrain 후보 5 + priority
- ✅ BrainVLM feasibility 정직 평가 → Track C supplementary 로 demote
- ✅ 3 측면 모두 진행 → Track A (main) + Track B (main) + Track C (supplementary)
- ✅ Git workflow branch-based → `v4_20260602_perlmutter` branch

---

## 14. Future Extensions (post-submission, v5 candidates)

v4 final 의 main 은 **universal emotion code** (foundation model 의 본질 = generalization). 그 위에 추후 추가할 2 extension. 6 month 안에는 Appendix / future work 로만 명시, post-submission 의 v5 cycle 에서 본격 진행.

### Extension 1. Context-aware emotion (text 형식)

**왜 추가**. Universal code 는 "context-invariant" 측면. 그러나 실제 emotion 은 context-conditioned (같은 stimulus, 다른 narrative position 에서 다른 felt emotion). 이 modulation 을 brain 에서 어떻게 capture 하는지가 다음 단계.

**Form**. Text-based context.
- 영화의 subtitle / narrative description / scene caption 을 text 로 표현
- Qwen-VL 또는 BLIP-2 로 video → caption 생성 (이미 EmoViS 추출본 있음)
- Context text → sentence-transformer embedding (Universal code 의 emotion-text space 와 같은 space)
- Brain emotion = Universal code (Track A SSL 학습) × Context-text modulation (영화의 surrounding narrative)

**측정 방법**.
- StudyForrest 의 2h Forrest Gump narrative. Same character 의 다른 narrative time 의 brain representation 분해 = Universal code (character emotion identity) + Context-conditional (narrative position)
- Emo-FilM 의 1 Hz continuous rating + scene caption. 시간별 brain trajectory 분해
- Brain RDM = α × Universal code RDM + β × Context-text RDM 의 partial RSA

**연결**. v2 (2026-05) 의 "context-aware emotion FM" framing 의 정직한 후속.

### Extension 2. Individual differences (subject embedding + residual analysis)

**왜 추가**. Universal code 는 "subject-invariant" 측면. 그러나 실제 emotion 은 individual mapping 의 변이 (subject 마다 같은 stimulus 의 다른 felt experience). v3 (2026-05-27) 의 individual difference 방향의 정직한 후속.

**Form 두 가지**.

(a) **Subject embedding (TRIBE v2 / Défossez 2023 style)**.
- 각 subject 마다 learnable vector
- Brain encoder 의 input/output 에 concat 또는 modulation
- Universal code × subject embedding 으로 subject-conditioned emotion 표현
- BrainVLM (Track C) 의 caption generation 에서 subject-conditioned caption 으로 활용 가능

(b) **Residual analysis (Track A 의 byproduct, low cost)**.
- Subject-invariant SSL (Track A priority 1, Action 5) 학습 후 *align 안 된 residual* 을 PCA
- Residual axis 의 subject 별 분포 = individual differences 의 brain evidence
- Subject 별 행동 metric (Cowen 34-cat rating 분포의 subject 별 차이) 와 residual axis 의 correlation 으로 validate

**측정 방법**.
- (a) Subject embedding 추가 학습. Track A 의 LoRA adaptation 단계에서 subject embedding 추가
- (b) Track A Action 6 (subject alignment metric) 의 extension. 이미 학습된 SSL representation 의 *non-aligned* component 의 PCA + 행동 correlation

**Brain emotion 의 완전 분해 schema**.

```
Brain emotion representation =
    Universal code              (v4 main, Track A priority 1)
  + Context-conditional         (Extension 1, text-based modulation)
  + Individual differences      (Extension 2, subject embedding + residual)
  + Acquisition noise           (control, ComBat)
```

### Priority

- v4 main (6 month 안). Universal code 만 (foundation model 의 generalization 본질)
- v5 (post-submission). Extension 1 + 2 의 정직한 추가
- v6 (next cycle). 4 component 의 통합 paper (universal + context + individual + control)

### Action items (post-submission)

- Action 31. Context-text embedding 추출 pipeline (`code/context_aware/text_extraction.py`)
- Action 32. Subject embedding 추가 학습 (`code/individual_diff/subject_embedding.py`)
- Action 33. Residual analysis pipeline (`code/individual_diff/residual_pca.py`)
- Action 34. Brain RDM 의 partial RSA decomposition (`code/decomposition/partial_rsa.py`)
- Action 35. Extension paper (v5) draft

이 4 extension actions 는 v4 main paper 의 submission (W24) 후 시작. 본 masterplan v2.md 는 v4 main 중심.
