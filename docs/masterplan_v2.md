# FEELIN Masterplan v3 — Emotion-aware Multimodal Foundation Model

작성: 2026-05-19 (v3.1 framing refinement)
사용자 결정 + 3 agent search 종합. 이전 v2.1 전면 교체.


## 0. 한 줄 요약

fMRI 와 video 를 함께 활용해 emotion-aware multimodal foundation model 을 만든다. fMRI 를 어떤 방식으로 인코딩 / 통합해야 (어떤 architecture × 어떤 brain encoder) 그 model 의 emotion 이해 능력이 가장 잘 형성되는지 비교한다.


## 1. Big Question

> **fMRI 와 video 를 함께 활용해 emotion-aware multimodal foundation model 을 만들 수 있는가? 그리고 fMRI 를 어떻게 인코딩 / 통합해야 (어떤 architecture × 어떤 brain encoder) model 의 emotion 이해 능력이 가장 잘 형성되는가?**


## 2. Sub-questions (각각 측정 가능, go/no-go 명확)

### Sub-question 1. fMRI 통합 방법 + brain encoder 선택 (main contribution)

어떤 architecture (아래 4 option) 와 어떤 brain encoder (SwiFT / Brain-JEPA / NeuroSTORM) 의 조합이 emotion-aware multimodal foundation model 에 가장 적합한가? (BrainLM 은 490 timepoint × A424 atlas 고정으로 Horikawa 비호환, scope 제외.)

| Option | 설명 |
|---|---|
| **A. LLM token 화** | fMRI → patches → LLM token 으로 직접 주입. BrainVLM (UMBRELLA_qwen) architecture |
| **B. Cross-attention** | fMRI embedding 을 LLM 의 cross-attention key/value 로 주입 |
| **C. Contrastive alignment** | fMRI embedding 과 video / caption embedding 을 shared latent 로 contrastive 학습 후 downstream |
| **D. Late fusion** | Brain 과 video 를 각자 처리 후 concat / element-wise |

각 option 안에서 brain encoder 3 종을 swap-in.

**Go**: 4 option × 3 encoder = 12 cell 중 best 가 video-only baseline 대비 emotion task (V/A regression + 27-cat 분류) 에서 통계적으로 유의한 향상.
**Pivot**: 모든 cell 이 baseline 과 구별 없음 → "brain conditioning 자체가 emotion 정보 추가 못 함" 결론. 다음 phase 는 brain encoder fine-tune 으로.

### Sub-question 2. Emotion 표상의 evidence (multi-channel)

학습된 model 안에 emotion 표상이 실제로 형성되었는가? 여러 emotion task 에서 측정.

- (a) V/A continuous regression: within-subject Pearson r ≥ 0.4 (self-rating 과)
- (b) Cowen 27/34-category classification: balanced accuracy
- (c) Cowen 14 affective dimension multi-output regression: mean Pearson r
- (d) (Phase 2+) Free-form caption 의 affect accuracy: RoBERTa-emotion 으로 caption 에서 V/A 추출 → self-rating 과 비교

**Go**: 위 channel 들에서 video-only baseline 대비 통계적으로 유의한 향상 (paired bootstrap p < 0.05).
**Pivot**: 1-2 channel 만 향상이면 어느 emotion 측면이 brain 에 의해 잡히는지 specific reporting.

#### Evaluation protocol (모든 probe 공통)

- **5-fold stim-stratified CV** (`data/horikawa_5fold.csv`, V × A quartile joint stratification)
- 각 outer fold k: test = fold k, val = (k%5)+1, train = 나머지 3 fold
- 6 task: V_binary, A_binary, V_reg, A_reg, Cat34_top1, Dim14_multi
- 2 head: Linear (deterministic, 1 seed) + MLP (1 seed screening, final paper 시 3 seed)
- BFM probe 는 추가로 pooled vs per_subject 2 mode
- CSV schema 통일: BFM / Video probe 모두 동일 column (fold + mode + subject 등)

#### Sub-question 2 의 evaluation pipeline 별 scientific question

각 probe 실행은 독립된 scientific question 에 답함:

| Probe | Scientific question | 답하는 것 |
|---|---|---|
| **BFM frozen probe** (`run_unified_probe.py`) | 각 brain foundation model 의 frozen embedding 이 emotion 의 어떤 측면을 capture 하는가? Architecture × init × subject mode 의 어느 조합이 어느 task 에 강한가? | Tier 2 ceiling 측정, sub-question 1 의 BFM 부분 |
| **Video-only probe** (`run_video_probe.py`) | 자극 (영상) 자체의 feature 만으로 emotion 이 어디까지 예측되는가? Brain 없이 video model 의 ceiling 은? | "Brain 이 video 위에 얼마나 추가하는가" 의 reference baseline. Reviewer 의 가장 큰 challenge 에 대한 직접 답 |
| (Phase 2) **Late fusion** | Brain + video 결합이 단독 대비 향상이 있는가? | Architecture D 의 결과, brain unique contribution evidence |
| (Phase 2-3) **Contrastive alignment** | Brain-video shared latent 학습이 emotion 표상 capture 를 향상시키나? | Architecture C 의 결과 |
| (Phase 3) **LLM-token (BrainVLM-style)** | fMRI 를 LLM token 으로 주입한 model 이 emotion 의 자연어 표현 (caption) 을 생성하나? | Architecture A 의 generative novelty |

### Sub-question 3. Brain 의 causal 기여 (counterfactual subject swap)

Model 안의 emotion 표상이 brain signal 을 실제 driver 로 쓰는가, 아니면 video 만 쓰고 brain 은 ornament 인가?

같은 video × subject A brain vs subject B brain → model output 의 차이가 systematic 한가? 그리고 그 차이가 video swap 의 차이 대비 신호 가치가 있는가?

**Go**: Brain swap 으로 인한 emotion output 차이의 effect size > 0 with p < 0.05 (paired bootstrap). 차이 방향이 subject A 와 B 의 actual self-rating 차이와 correlate.
**Pivot**: Brain swap 에 model output 변화 없음 → brain 무시되는 architecture, SQ1 design 재검토.

### Sub-question 4. Content grounding 보존 (defensive lower bound)

Emotion 에 집중하면서도 자극 content 를 잡고 있는가? Caption 생성 능력으로 stimulus retrieval 측정.

**Go**: Caption → stimulus top-5 retrieval accuracy ≥ Horikawa Mind Captioning baseline × 0.8.
**Pivot**: 80% 미만이면 affect 와 content 의 trade-off 가 너무 큼. Loss balance 또는 video grounding 강화.


## 3. Architecture — design space

### Common pipeline

```
fMRI (B, T, 96, 96, 96)
   │
   ▼
fMRI encoder (brain encoder 3 종 swap-in: SwiFT / Brain-JEPA / NeuroSTORM)
   │
   ▼ z_brain
   ┌─────────────────────────────────────────┐
   │  fMRI 통합 방법 4 option (SQ1 비교 axis) │
   │  A: LLM token (BrainVLM)                  │
   │  B: Cross-attention key/value             │
   │  C: Contrastive alignment + downstream    │
   │  D: Late fusion (concat / element-wise)   │
   └─────────────────────────────────────────┘
              │
              ▼  + video features (V-JEPA2 / CLIP / DINOv2 from EmoViS)
                  + (optional) reference caption supervision
   ┌─────────────────────────────────────────┐
   │  Foundation model (LLM 또는 transformer)  │
   │  Qwen3-VL (BrainVLM) / Llama / etc.       │
   └─────────────────────────────────────────┘
              │
              ▼
   Multi-channel output:
   - V/A continuous regression
   - 27-cat classification
   - Free-form emotion caption (SQ4 retrieval 도)
   - Latent embedding (counterfactual swap)
```

### Vision tower swap 의 3 수준 (Option A 안에서 깊이)

Option A (LLM token) 를 채택하면 그 안에서 다시 3 수준의 swap depth 비교.

| 수준 | 설명 | 시점 |
|---|---|---|
| **L1. Frozen embedding 주입** | brain encoder 로 미리 추출한 embedding (2185, D) 을 linear projection 으로 LLM token space 에 주입. encoder freeze. 안전, 우리 추출 결과 즉시 활용 | Phase 2 W7-10 |
| **L2. Vision tower 교체 + freeze** | BrainVLM 의 patchify layer 자체를 brain encoder 로 교체. encoder freeze. 더 deep integration | L1 결과 보고 → Phase 2 W11-12 |
| **L3. Vision tower + LoRA fine-tune** | encoder + projection 모두 LoRA fine-tune. 가장 deep, 가장 risk | L2 결과 보고 → Phase 3 W13-18 |

각 수준의 go/no-go: 다음 수준으로 가려면 현재 수준에서 video-only baseline 을 넘어야 함.

Option B/C/D 는 Phase 2 의 Option A 결과 보고 결정 — A 가 충분히 잘 working 하면 부수 비교로, A 가 fail 하면 main path 로 전환.


## 4. 자원 분배

### Brain foundation model 3 종 (우리 추출 작업이 직접 활용)

| Model | 추출 상태 | 역할 |
|---|---|---|
| SwiFT NewE96 (+ NewE36 / NewE192 / UAH 5M / UAH 51M / UAH 202M) | NewE96 완료, 5 변종 padding ablation 결정 후 추출 | vision tower 후보 1 |
| Brain-JEPA | 추출 완료 (proper mean padding) | vision tower 후보 2 |
| NeuroSTORM | 추출 완료 (proper mean padding) | vision tower 후보 3 |

**BrainLM 제외**: 490 timepoint 와 A424 atlas 가 고정 입력으로 강제돼 Horikawa 자극 (T=5-15) 와 비호환. Scope 밖.

### Stimulus features (EmoViS 에서 reuse, FEELIN 에서 추출 안 함)

위치: `data/stimulus_features/` (EmoViS `/pscratch/sd/s/sjmoon/EmoViS/study1/results/` symlink)

| 파일 | shape | 용도 |
|---|---|---|
| `caption_embed.npy` | (2185, 768) | Qwen-VL caption embedding |
| `captions.json` | dict, 2185 | Free-form caption (training reference) |
| `vjepa2_pretrained.npy` | (2185, 1408) | V-JEPA2 pretrained video feature |
| `vjepa2_scratch.npy` | (2185, 1408) | V-JEPA2 scratch (control) |
| `clip_pretrained.npy`, `clip_scratch.npy` | (2185, D) | CLIP image feature |
| `dinov2_pretrained.npy`, `dinov2_scratch.npy` | (2185, D) | DINOv2 image feature |
| `videomae_pretrained.npy`, `videomae_scratch.npy` | (2185, D) | VideoMAE video feature |
| `stim_idx.npy` | (2185,) | Stimulus index 0..2184 |

### Brain-VLM 자체

- Source: `/pscratch/sd/s/sjmoon/BrainVLM/UMBRELLA_qwen` (Qwen3-VL 2B backbone, ABCD pretrained on BMI + sex classification)
- Frozen LLM, trainable patchifier + vision tower + projection + optional LoRA
- Phase 1 의 첫 task = 우리 데이터에 transfer 되는지 검증


## 5. Phase plan (6 month, 4 phase)

### Phase 1: Foundation (Week 1-6)

병행 3 트랙:

**Track 1. Brain-VLM 환경 + transfer test (Critical path)**
- W1-2: BrainVLM env setup, ABCD checkpoint load, fMRI patchify 동작 확인
- W3-4: Horikawa fMRI → BrainVLM token. Token distribution 비교 (ABCD vs Horikawa KL)
- W5-6: Zero-shot emotion linear probe (token → V/A regression). Brain-VLM transfer 가능성 정량화

**Track 2. Brain foundation model 추출 완성 (병행)**
- 진행 중: proper mean padding 으로 NewE96 + Brain-JEPA + NeuroSTORM × 5 subject × 2 init = 30 cell
- W3-4 시작: SwiFT padding ablation 결과의 best padding 으로 SwiFT 5 변종 (NewE36, NewE192, UAH 5M, UAH 51M, UAH 202M) 추출

**Track 3. Stimulus feature + reference caption 통합 (가벼움)**
- W1: EmoViS feature symlink 확인 (이미 완료)
- W2-3: FEELIN 용 unified feature loader 작성
- W4-5: Caption reference 데이터 분석 (Qwen-VL caption 의 affect 분포)

**W6 Phase 1 종료 task list**

체크리스트:
- [ ] Brain-VLM transfer 검증: ABCD vs Horikawa token KL 측정 + token linear probe V/A r 측정
- [ ] BFM 3 종 × 5 subject 추출본 100% 확인 (proper mean padding)
- [ ] EmoViS feature 9 종 로딩 sanity check
- [ ] Caption reference 분석 결과 표
- [ ] Phase 2 진입 결정: token linear probe V/A r ≥ 0.3 → Go, < 0.3 → BrainVLM 직접 fine-tune 으로 우회

---

### Phase 2: Brain-conditioned VLM 학습 (Week 7-12)

Vision tower swap **L1 수준 (frozen embedding 주입)** 으로 4 BFM 비교.

- W7-8: Linear projection 학습 (각 BFM embedding → BrainVLM 의 token space). Caption generation 학습 시작
- W9-10: 4 BFM × emotion target (V/A regression + caption generation joint) 학습
- W11: SQ1 (caption affect 정확도) 측정. 4 BFM 비교 figure
- W12: Phase 2 종료 결정. L1 best BFM 결정 + L2 (vision tower 교체) 진입 여부

**W12 Phase 2 task list**

- [ ] 4 BFM × L1 학습 완료
- [ ] SQ1 측정: within-subject caption-affect r per BFM
- [ ] Best BFM 결정 + L2 진입 여부 (best L1 result 가 video-only baseline 보다 높은가)
- [ ] EmoViS branch 와 first comparison meeting

---

### Phase 3: Vision tower deep integration (Week 13-18)

L2 (vision tower 교체 + freeze) → L3 (LoRA fine-tune).

- W13-14: L2 — best BFM 을 BrainVLM 의 patchifier 로 직접 교체, freeze. Caption + V/A joint fine-tune
- W15-16: L3 — LoRA 추가, deeper fine-tune. 
- W17: SQ2 측정 (counterfactual subject swap). SQ3 측정 (stimulus retrieval)
- W18: Phase 3 종료. L1 / L2 / L3 비교 figure

**W18 Phase 3 task list**

- [ ] L2 학습 완료, SQ1 재측정 (L1 대비 향상?)
- [ ] L3 학습 완료, SQ1 재측정
- [ ] SQ2 (counterfactual swap) 측정
- [ ] SQ3 (retrieval) 측정
- [ ] 3 수준 비교 표 + go/no-go 결정 (어느 수준이 best)

---

### Phase 4: Synthesis + submission (Week 19-24)

- W19-20: Cross-evaluation + EmoViS branch 결과 통합 검토
- W21-22: Paper draft
- W23: Infographic, README, code release
- W24: Submission target 결정 (NeurIPS / Nat Commun / Imaging Neuroscience)


## 6. Critical files

**기존 작업 재사용**:
- `code/bfm_embeddings/_lib/{swift,brain_jepa,neurostorm}.py` — BFM extraction
- `output/embeddings/` — BFM embedding .pt 파일 (proper mean 진행 중)

**Phase 1 에 만들 새 파일**:
- `code/brainvlm/load_brainvlm.py` — UMBRELLA_qwen checkpoint loader
- `code/brainvlm/zero_shot_transfer.py` — Horikawa fMRI → BrainVLM token + distribution analysis
- `code/brainvlm/data_loader.py` — fMRI + video + caption 통합 loader (EmoViS feature 활용)
- `data/stimulus_features/` — EmoViS symlinks (완료)
- `reports/phase1_foundation.md` — Phase 1 진행 보고 (v3 framing 으로 재작성 필요)

**Phase 2 에 만들 새 파일**:
- `code/brainvlm/train_l1.py` — L1 (frozen embedding 주입) 학습
- `code/brainvlm/eval_caption.py` — SQ1 caption affect 평가

**Phase 3**:
- `code/brainvlm/train_l2_l3.py` — L2 (vision tower 교체) + L3 (LoRA) 학습
- `code/brainvlm/eval_counterfactual.py` — SQ2 brain swap 평가
- `code/brainvlm/eval_retrieval.py` — SQ3 stimulus retrieval

**참고용 외부**:
- `/pscratch/sd/s/sjmoon/BrainVLM/UMBRELLA_qwen/project/model/patch_embed.py` — fMRI patchifier
- `/pscratch/sd/s/sjmoon/EmoViS/study1/results/` — stimulus features


## 7. Risk register

| Risk | Probability | Impact | Mitigation |
|------|------|--------|------------|
| BrainVLM transfer fail (Phase 1 gate) | Med-High | Critical | Phase 1 W5-6 에 zero-shot 측정으로 일찍 노출. Fail 시 BrainVLM 직접 fine-tune 으로 우회 |
| Caption 의 affect 가 video / VLM prior 에 묶임 (SQ2 fail) | Med | High | Counterfactual swap 으로 직접 측정. Fail 시 brain encoder 또는 cross-attention 재설계 |
| 5 subject 통계 검정력 부족 | High | Med | Within-subject + bootstrap CI 강조. Subject-level claim 자제 |
| Reviewer "BrainChat reskin" 격하 | Med | Med | Counterfactual subject swap + L1/L2/L3 BFM 비교를 직접 차별화 |
| 6 month budget overrun | Med | Med | Phase 3 의 L3 (LoRA) 가 미완 가능 — Phase 4 로 미루기 |
