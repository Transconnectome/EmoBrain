# FEELIN Masterplan v3 — Brain-conditioned Emotion-VLM

작성: 2026-05-19
사용자 결정 + 3 agent search 종합. 이전 v2.1 전면 교체.


## 0. 한 줄 요약

fMRI 와 video 를 함께 입력으로 받아 그 사람이 영상에서 느낀 emotion 을 자연어로 묘사하는 model 을 만든다. fMRI 인코더로 어떤 brain foundation model (SwiFT, Brain-JEPA, NeuroSTORM, BrainLM) 을 쓰면 가장 좋은지 비교한다.


## 1. Big Question

> **fMRI 와 video 를 함께 받는 model 이 그 사람이 영상에서 느낀 emotion 을 자연어로 묘사할 수 있는가? 그리고 fMRI 를 어떻게 인코딩해야 (어떤 brain foundation model 을 쓰면) 묘사가 가장 잘 되는가?**


## 2. Sub-questions (각각 측정 가능, go/no-go 명확)

### Sub-question 1. Caption 의 affect 정확도

Brain + video 를 받아 생성한 emotion caption 에서 RoBERTa-emotion / sentiment classifier 로 V/A 를 추출했을 때, 그 점수가 같은 자극에 대한 그 subject 의 self-rating 과 within-subject Pearson r 0.4 이상으로 일치하는가? 그리고 video-only caption baseline 보다 유의하게 높은가?

**Go**: within-subject Pearson r ≥ 0.4 AND brain-conditioned > video-only paired bootstrap p < 0.05.
**Pivot**: r < 0.4 또는 baseline 과 구별 없음 → brain conditioning 이 작동 안 함, fMRI 인코더 / fine-tune 방식 재검토.

### Sub-question 2. Brain swap 의 caption 변화

같은 영상에 subject A 의 brain 을 conditioning 한 caption 과 subject B 의 brain 을 conditioning 한 caption 의 affect tone 차이가, 같은 subject A 의 다른 영상 caption 의 affect tone 차이보다 systematically 큰가? 이게 성립하면 brain 이 caption 의 affect 를 실제로 driving 하고 있다는 직접 증거.

**Go**: same-video / different-brain affect distance > 0.5 × same-subject / different-video affect distance (paired bootstrap p < 0.05).
**Pivot**: 차이 없음 → caption 이 brain 이 아니라 video 또는 VLM prior 에 의해 결정됨. Brain encoder 또는 cross-attention 재설계 필요.

### Sub-question 3. Stimulus retrieval

생성된 caption 으로 원래 자극을 retrieval 했을 때 정확도가 Horikawa Mind Captioning baseline 의 80% 이상을 유지하는가? 즉 affect 에 집중한 결과 visual content grounding 을 너무 잃지 않았는지 확인.

**Go**: caption → stimulus top-5 retrieval accuracy ≥ Mind Captioning baseline × 0.8.
**Pivot**: 80% 미만이면 affect 와 stimulus content 의 trade-off 가 너무 큼. Loss balance 또는 video grounding 강화.


## 3. Architecture

### Base

```
fMRI (B, T, 96, 96, 96)
   │
   ▼
fMRI encoder (BFM swap-in 후보: SwiFT / Brain-JEPA / NeuroSTORM / BrainLM)
   │
   ▼ z_brain (B, D_brain)
   ┌────────────────────────────────────────┐
   │   linear projection or cross-attention  │
   └────────────────────────────────────────┘
              │
              ▼  as prefix / soft prompt
       Brain-VLM (UMBRELLA_qwen, Qwen3-VL backbone)
              ▲
              │ as cross-attention key/value
              │
       Video frames (16-frame uniform sampled)
              │
              ▼
       free-form emotion caption
              │
              ├─► caption affect classifier (RoBERTa-emotion) → V/A → SQ1
              ├─► counterfactual subject swap → SQ2
              └─► caption → stimulus retrieval → SQ3
```

### Vision tower swap 의 3 수준 (각각 go/no-go gate)

| 수준 | 설명 | 시점 |
|---|---|---|
| **L1. Frozen embedding 주입** | BFM 으로 미리 추출한 embedding (2185, D) 을 linear projection 으로 BrainVLM 에 주입. BFM freeze. 안전, 우리 BFM extraction 결과 즉시 활용 | Phase 1 W5-8 |
| **L2. Vision tower 교체 + freeze** | BrainVLM 의 patchify layer 자체를 BFM 으로 교체. BFM freeze. 더 deep integration | L1 결과 보고 → Phase 2 W9-12 |
| **L3. Vision tower + LoRA fine-tune** | BFM + projection 모두 LoRA fine-tune. 가장 deep, 가장 risk | L2 결과 보고 → Phase 3 W13-18 |

각 수준의 go/no-go: 다음 수준으로 가려면 현재 수준에서 SQ1 의 baseline (video-only caption) 을 넘어야 함.


## 4. 자원 분배

### Brain foundation model 4 종 (우리 추출 작업이 직접 활용)

| Model | 추출 상태 | 역할 |
|---|---|---|
| SwiFT NewE96 (+ NewE36 / NewE192 / UAH 51M / UAH 806M) | NewE96 부분 완료, 나머지 추출 대기 | vision tower 후보 1 |
| Brain-JEPA | 추출 완료 (spatial_only padding, proper mean 재추출 진행 중) | vision tower 후보 2 |
| NeuroSTORM | 추출 완료 (spatial_only padding, proper mean 재추출 진행 중) | vision tower 후보 3 |
| BrainLM | 추출 인프라 확인 필요 (atlas 호환성 문제 가능) | vision tower 후보 4 (가능 시) |

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


## 5. EmoViS 와의 분업

EmoViS 는 brain ↔ visual-semantic model alignment 분석 (descriptive: 어떤 model representation 이 brain emotion 과 align?). FEELIN 은 brain 을 받아 emotion 을 generate 하는 model 구축 (transformative).

| 작업 | 어디서 |
|---|---|
| Stimulus feature 추출 (V-JEPA2, CLIP, DINOv2, VideoMAE, Qwen-VL caption) | EmoViS (이미 완료, FEELIN 이 symlink 로 reuse) |
| Brain RDM, brain-stimulus RSA / CKA | EmoViS |
| Brain foundation model embedding 추출 | FEELIN |
| Brain-conditioned caption generation | FEELIN |
| Brain swap counterfactual | FEELIN |

CCN (사용자 발표) 의 결과는 참고하지 않음. CCN 의 아이디어 (video-brain alignment 가 emotion-relevant 할 수 있다) 만 동기로 사용.

EmoViS branch 가 FEELIN main 과 나중에 merge 될 가능성 열어둠. Phase 3 끝 (W18) 시점에 두 결과 비교 후 결정.


## 6. Phase plan (6 month, 4 phase)

### Phase 1: Foundation (Week 1-6)

병행 3 트랙:

**Track 1. Brain-VLM 환경 + transfer test (Critical path)**
- W1-2: BrainVLM env setup, ABCD checkpoint load, fMRI patchify 동작 확인
- W3-4: Horikawa fMRI → BrainVLM token. Token distribution 비교 (ABCD vs Horikawa KL)
- W5-6: Zero-shot emotion linear probe (token → V/A regression). Brain-VLM transfer 가능성 정량화

**Track 2. Brain foundation model 추출 완성 (병행)**
- 진행 중: proper mean padding 으로 NewE96 + Brain-JEPA + NeuroSTORM × 5 subject × 2 init = 30 cell
- W3-4 시작: SwiFT 나머지 4 변종 (NewE36, NewE192, UAH 51M, UAH 806M) 추출
- W5-6: BrainLM 인프라 점검 (atlas 호환 가능?)

**Track 3. Stimulus feature + reference caption 통합 (가벼움)**
- W1: EmoViS feature symlink 확인 (이미 완료)
- W2-3: FEELIN 용 unified feature loader 작성
- W4-5: Caption reference 데이터 분석 (Qwen-VL caption 의 affect 분포)

**W6 Phase 1 종료 task list**

체크리스트:
- [ ] Brain-VLM transfer 검증: ABCD vs Horikawa token KL 측정 + token linear probe V/A r 측정
- [ ] BFM 4 종 × 5 subject 추출본 100% 확인 (proper mean padding)
- [ ] BrainLM 추출 가능 여부 결정
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


## 7. Critical files

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


## 8. Risk register

| Risk | Probability | Impact | Mitigation |
|------|------|--------|------------|
| BrainVLM transfer fail (Phase 1 gate) | Med-High | Critical | Phase 1 W5-6 에 zero-shot 측정으로 일찍 노출. Fail 시 BrainVLM 직접 fine-tune 으로 우회 |
| Caption 의 affect 가 video / VLM prior 에 묶임 (SQ2 fail) | Med | High | Counterfactual swap 으로 직접 측정. Fail 시 brain encoder 또는 cross-attention 재설계 |
| 5 subject 통계 검정력 부족 | High | Med | Within-subject + bootstrap CI 강조. Subject-level claim 자제 |
| BrainLM atlas 비호환 | High | Low | 4 BFM 대신 3 BFM 으로 진행 (SwiFT + Brain-JEPA + NeuroSTORM) |
| EmoViS branch divergence | Low | Med | W12 시점 alignment meeting |
| Reviewer "BrainChat reskin" 격하 | Med | Med | Counterfactual subject swap + L1/L2/L3 BFM 비교를 직접 차별화 |
| 6 month budget overrun | Med | Med | Phase 3 의 L3 (LoRA) 가 미완 가능 — Phase 4 로 미루기 |
