# FEELIN Masterplan v4, Transferable Emotion Brain Foundation Model

작성: 2026-06-02 (v4 reframing). 이전 v3 (2026-05-19, "emotion-aware multimodal foundation model, brain+video fusion") 의 핵심 질문을 교체. v3 의 측정 결과 (Phase 1 frozen-probe benchmark + Phase 2 joint inference) 가 v4 의 출발점이다. 파일명은 link 호환을 위해 `masterplan_v2.md` 로 유지한다.

약어 (첫 등장): BFM (brain foundation model, 뇌 파운데이션 모델), VLM (vision-language model), MLLM (multimodal large language model), V/A (valence / arousal), OV (open-vocabulary, 개방 어휘), MER (multimodal emotion recognition), RSA (representational similarity analysis), CKA (centered kernel alignment), ISC (inter-subject correlation).


## 0. 한 줄 요약

Horikawa naturalistic emotion fMRI 로 **transfer 가능한 multi-dimensional emotion brain representation** 을 학습하고, metadata 가 빈약한 independent dataset / 새 subject / 다른 label taxonomy 로 일반화되는지를 측정해 emotion brain foundation model 을 만든다.


## 0.1 v3 → v4 가 바뀐 이유 (두 개의 다른 질문 분리)

v3 의 Big Question 은 "fMRI + video fusion 이 video-only baseline 을 넘는가" 였다. Phase 1 (frozen probe benchmark) 과 Phase 2 joint inference 가 이 질문에 거의 결론적으로 답했다. **넘지 못한다.** 그 이유는 model 실패가 아니라 target 의 성질이다. crowd-sourced V/A label 은 정의상 stimulus (영상) 의 속성이라 CLIP 같은 video encoder 가 이기는 게 trivial 하다.

그래서 두 질문을 명확히 분리한다.

| | 질문 A (v3, 측정 완료) | 질문 B (v4, 본 plan) |
|---|---|---|
| 묻는 것 | 같은 stimulus 에서 brain 이 video feature 보다 emotion 을 잘 예측하나? | Horikawa 로 학습한 brain emotion representation 이 새 subject / dataset / taxonomy 로 transfer 되나? |
| video 의 역할 | 경쟁자 (그래서 brain 패배) | teacher / supervision oracle (새 fMRI dataset 의 brain data 엔 적용 불가하므로 경쟁자가 아님) |
| 결과 해석 | brain 패배 = trivial | representation 의 transferability 가 측정 대상 |

foundation model 논문의 contribution 은 "무엇이 emotion 인가" 도 "brain 이 video 를 이기나" 도 아니다. **representation 의 속성 (transfer / generalization / data-efficiency / universality)** 이다. video 가 training set 에서 이기는 것은 teacher 가 student 보다 잘하는 것과 같아서 질문 B 와 무관하다.

**과학적 근거 (Horikawa, Cowen, Keltner, Kamitani 2020, iScience)**: 데이터셋 원논문은 emotion **category** 표상이 affective **dimension** (valence 등) 보다 cortical / subcortical 반응을 잘 예측하고, transmodal region 에서 **visual / semantic covariate (즉 video feature) 를 능가**한다고 보고했다. 즉 scalar V/A 는 video 가 이기는 게 당연한 잘못된 전장이고, high-dimensional categorical / appraisal target 이 brain 고유 신호가 사는 올바른 전장이다. multi-dimensional target 으로의 이동은 이 결과로 정당화된다.


## 1. Big Question

> **Naturalistic fMRI 로부터 학습한 multi-dimensional emotion brain representation 이, 단일 dataset 과 label taxonomy 에 종속되지 않고 새로운 subject, 자극, emotion 어휘로 transfer 되는 emotion brain foundation model 이 될 수 있는가?**

<sub>운영 정의 (operationalization, FEELIN testbed): Horikawa naturalistic fMRI 로 학습한 multi-dimensional emotion brain representation 이, metadata 가 풍부하지 않은 independent dataset / 새 subject / 다른 emotion taxonomy 로 transfer 되는 emotion brain foundation model 이 될 수 있는가? 그리고 어떤 supervision (scalar V/A vs Cowen 34-category vs 14-dimension vs open-vocabulary description) 과 어떤 brain encoder 가 가장 transferable 한 표상을 만드는가? supervision 과 encoder 비교는 SQ2 와 encoder-swap 축에서 다룬다.</sub>


## 2. Sub-questions (각각 측정 가능, go / no-go 명확)

모든 SQ 는 emotion theory 질문이 아니라 representation 질문이다. 어느 것도 "brain 이 video 를 이겨야" 를 전제로 하지 않는다.

### SQ1. Transfer (foundation model 의 정의적 질문, main contribution)

Horikawa 에서 학습한 brain emotion representation 이 retrain 없이 새 dataset / subject / scanner / taxonomy 로 일반화되는가?

- 측정: zero-shot (전략 1, 4.1) + few-shot scaling curve (전략 2, 4.2) on Emo-FilM / Affective Videos / IAPS / NeuroEmo.
- **Go**: 최소 한 개의 independent dataset 에서 zero-shot 이 chance 를, few-shot (k≤32) 이 from-scratch 를 통계적으로 유의하게 넘음 (paired bootstrap p < 0.05).
- **Pivot**: transfer 가 전혀 없으면 → Horikawa-specific decoder 로 결론을 좁히고, cross-dataset 은 representational alignment (전략 4) 만으로 보고.

### SQ2. Supervision richness (multi-dimensional 의 정당화)

scalar V/A 로 학습한 표상 vs high-dimensional category (Cowen 34) / dimension (Cowen 14) / open-vocabulary description 으로 학습한 표상 중, 어느 쪽이 더 transferable 하고 더 풍부한 brain emotion 구조를 잡는가?

- 측정: 같은 brain encoder, supervision 만 바꿔 SQ1 transfer + SQ3 geometry 비교.
- **Go**: rich supervision 이 scalar V/A supervision 대비 transfer 또는 geometry 에서 유의한 향상.
- **Pivot**: 향상 없으면 → "현재 fMRI regime 에서는 low-dim supervision 으로 충분" 의 honest 결과로 보고.

### SQ3. Representation geometry / universality

학습된 brain emotion space 가 Horikawa 2020 의 알려진 구조 (high-dimensional, category > dimension, transmodal 분산) 를 복원하는가? 단일 universal emotion code 인가, subject / task 별로 다른가?

- 측정: model representation 과 emotion rating space 간 RSA / CKA. transmodal vs early-visual region-restricted 분석. cross-task probe transfer.
- **Go**: model emotion space 가 behavioral emotion space 와 RSA 유의 정렬, transmodal restriction 에서 video feature 대비 정렬 우위.
- **Pivot**: 정렬이 early-visual 에만 있으면 → "표상이 low-level visual 에 머문다" 로 명시 보고.

### SQ4. Data efficiency

Pretrained brain emotion FM 이 새 emotion dataset 에서 from-scratch 대비 몇 배 적은 데이터로 같은 성능에 도달하는가? (foundation model 의 표준 selling point)

- 측정: few-shot scaling curve (k = 1, 2, 4, 8, 16, 32, full) on 각 target dataset. pretrained vs scratch.
- **Go**: pretrained 가 동일 성능에 도달하는 데 필요한 label 수가 scratch 대비 유의하게 적음.
- **Pivot**: 차이 없으면 → pretraining 이 data-efficiency 를 주지 못한다는 결과.

### SQ5. Where (label-free 안전망)

이 emotion 정보가 brain 의 어디에 있는가? label 이 빈약한 dataset 에서도 측정 가능한 분석.

- 측정: network-restricted probe (visual / auditory / salience / DMN / limbic / control), region-wise RSA, ISC 기반 noise ceiling.
- **Go / 의미**: emotion-relevant 신호의 anatomical 분포가 Horikawa 2020 의 transmodal 분산과 일관. label 이 없어도 보고 가능해 cross-dataset 평가의 fallback.


## 3. Target hierarchy (multi-dimensional 승격, V/A 강등)

v3 는 V/A 를 main target, Cat34 / Dim14 를 "extracted but not focus" 로 두었다. v4 는 이를 뒤집는다 (SQ2 + Horikawa 2020 근거).

| Tier | Target | 역할 | 비고 |
|---|---|---|---|
| **Primary** | Cowen 34-category (top-1 + multi-label distribution) | brain 고유 신호가 사는 전장 | Horikawa gold label |
| **Primary** | Cowen 14 affective dimension (multi-output) | high-dim geometry | Horikawa gold label |
| **Primary** | OV emotion-text embedding | open-vocabulary, cross-dataset 호환 (4.1) | brain → emotion text space projector 의 target |
| Reference | V/A binary / regression | video 가 이기는 게 알려진 axis. floor / sanity 로만 | Phase 1 에서 측정 완료 |

**OV emotion-text embedding 의 정의**: 각 stimulus 의 emotion label / description 을 frozen sentence encoder (또는 CLIP-text) 로 embedding 한 vector. brain encoder 가 이 vector 를 회귀하도록 학습 → label 이 아니라 emotion **text space** 를 target 으로 삼아 open-vocabulary / cross-taxonomy zero-shot 을 가능케 한다 (4.1).


## 4. Cross-dataset evaluation protocol (v4 의 핵심 신규 섹션)

문제: independent test dataset (Emo-FilM / Affective Videos / IAPS / NeuroEmo) 은 Horikawa 처럼 34-cat × 14-dim metadata 가 없다. multi-dimensional model 을 어떻게 평가하나? 네 전략을 난이도 / 안전성 순으로 묶어 dataset metadata 풍부도와 무관하게 평가표를 채운다.

### 4.1 전략 1, Shared text-embedding space 로 zero-shot transfer (main)

brain encoder 를 "label 분류" 가 아니라 **fMRI → emotion-text embedding space** 사영으로 학습한다 (3. Primary). 그러면 새 dataset 은 그 dataset 의 native label 이름만 있으면 된다. 그 이름을 같은 text encoder 로 encode 해 nearest-neighbor retrieval 로 zero-shot 분류. ds000205 가 V/A 만, NeuroEmo 가 5-class 만 있어도, label 이름을 text 로 넣으면 분류 가능. CLIP 의 open-vocabulary zero-shot 을 brain emotion 에 옮긴 것이고, OV-MER 의 철학과 정합. label space 가 dataset 마다 달라도 된다.

### 4.2 전략 2, Label-space intersection (안전 baseline)

multi-dim 출력 중 target dataset 이 가진 축만 잘라 평가. ds000205 엔 V/A subspace, IAPS 엔 valence 축. claim 이 보수적이라 reviewer 가 반박하기 어렵다. 전략 1 의 fallback.

### 4.3 전략 3, MLLM 을 universal annotator 로 (metadata 빈곤 자체 해결)

OV-MER / AffectGPT (Lian et al. 2025, AffectGPT-R1 2025) 를 **모든 dataset 의 stimulus 에 돌려** 공통 open-vocabulary 라벨을 생성 → 이질적 dataset 이 같은 target space 공유. cross-dataset 의 LLM-embedding label alignment (arXiv 2410.11522) 가 방법론적 근거.

**주의 (질문 A 함정 재발 방지)**: OV 라벨도 stimulus 에서 뽑으니 "brain 이 MLLM 을 이긴다" 로 framing 하면 안 된다. "brain 이 MLLM 이 정의한 rich emotion 구조를 decode 하고 transfer 한다" 로 쓴다.

**분업 원칙**: Horikawa 는 Cowen 34 / 14 gold norm 을 training target 으로 쓰고 (LLM pseudo-label 보다 깨끗함), OV-MER / AffectGPT 는 **norm 이 없는 target dataset 에만** harmonization 도구로 쓴다.

**도메인 mismatch 사전 점검 (first action)**: AffectGPT 는 발화 있는 영화 / TV (MER2023) 로 학습됐는데 Horikawa clip 은 짧고 (대부분 T=5, 약 2초) 무음 / 비발화가 많다. audio + text branch 가 무력해져 visual branch 만 남으면 richness 이득이 사라진다. → **결정 전에 Horikawa 몇 clip 에 AffectGPT 를 돌려 실제 출력 sanity check** 한다.

### 4.4 전략 4, Representational alignment (label 거의 불필요)

label 이 정말 없으면, target dataset 에서 brain representation 의 similarity 구조 (RSA) 가 stimulus 의 emotion-space 구조와 정렬되는지, 또는 ISC 를 noise ceiling 으로 측정. label 없이 "emotion geometry 가 보존되는가" 를 답함. SQ3 / SQ5 와 연결.

**운영**: 전략 1 = main, 전략 2 = 안전 baseline, 전략 3 = 라벨 생성 도구, 전략 4 = label-free 보강.


## 5. Architecture, design space

### 5.1 통합 architecture (v4 의 main): brain → emotion-text embedding projector

```
fMRI (B, T, 96, 96, 96)
   │
   ▼  brain encoder (SwiFT / Brain-JEPA / NeuroSTORM swap-in)
   z_brain
   │
   ▼  projection head
   z_emo  ──────────────────────► emotion-text embedding space (frozen sentence / CLIP-text encoder)
                                   target = embed( Cowen 34/14 label or OV description )
   │
   ▼  평가
   - zero-shot / few-shot cross-dataset (4.1, 4.2)
   - RSA / CKA geometry (SQ3)
   - region-restricted (SQ5)
```

이 단일 architecture 가 OV-MER + multi-dimensional + cross-dataset 을 한 번에 묶는다. brain encoder 는 SQ1 / SQ2 의 swap 축.

### 5.2 보조 / legacy: 4 fusion option (v3 의 design space)

| Option | 설명 | v4 위치 |
|---|---|---|
| A. LLM token (BrainVLM) | fMRI → patches → LLM token. Qwen3-VL backbone | generative track. token-level V/A probe gate 미측정 상태 (Risk) |
| B. Cross-attention | fMRI embedding → LLM cross-attn key/value | 보조 |
| C. Contrastive alignment | brain-video shared latent | 5.1 의 brain-text 버전이 우선 |
| D. Late fusion | concat / element-wise | Phase 2 에서 측정 완료 (video saturate) |

fusion option 은 질문 A 에 해당하므로 v4 의 main path 가 아니다. BrainVLM (A) 은 generative caption / VQA novelty track 으로만 유지하되, 학습 결과 한 줄이 나오기 전까지는 main contribution 으로 적지 않는다.

### 5.3 Brain encoder 후보

SwiFT (NewE96 + 변종) / Brain-JEPA / NeuroSTORM = fMRI 를 model 입력으로 변환하는 인코더 후보, SQ1 / SQ2 의 swap 축. BrainLM 은 490 timepoint × A424 atlas 고정이라 Horikawa 비호환으로 scope 제외.


## 6. 자원 분배

### Brain foundation model 3 종

| Model | 추출 상태 | 역할 |
|---|---|---|
| SwiFT NewE96 (+ NewE36 / NewE192 / UAH 5M / 51M / 202M) | 6 변종 zero padding 추출 완료 | encoder 후보 1 |
| Brain-JEPA | 추출 완료 (zero / mean padding, NUM_FRAMES 16 center-crop) | encoder 후보 2 |
| NeuroSTORM | 추출 완료 | encoder 후보 3 |

### Stimulus features (EmoViS reuse, `data/stimulus_features/`)

caption_embed.npy (2185, 768), captions.json, vjepa2 / clip / dinov2 / videomae (pretrained + scratch). teacher / OV embedding 생성에 활용.

### MLLM annotator (신규)

OV-MER / AffectGPT (github zeroQiaoba/AffectGPT). 역할: target dataset stimulus 에 open-vocabulary emotion 라벨 생성 (4.3). first action = Horikawa clip sanity check.

### 평가 datasets

Horikawa (train source, 5 subj × 2185), Emo-FilM / Affective Videos (ds000205) / IAPS / NeuroEmo (independent transfer targets). 자세한 매트릭스는 `notes/benchmark_design.md`.


## 7. Phase plan (revised)

### 7.0 측정 완료 결과 (보존, 질문 A evidence)

v4 reframe 는 아래 결과를 **폐기하지 않는다**. 전부 보존되며, 질문 A ("brain 이 stimulus-property V/A label 에서 video 를 이기나") 의 측정 증거이자 Phase 4 fallback 논문 ("crowd-labeled naturalistic emotion fMRI 는 video-prediction task 임") 의 본문이다. 원본 산출물: `reports/phase1_wrapup/{main,supplementary}.pdf`, `reports/phase1_foundation.md`, `reports/weekly/2026-06-01.md`, `results/{phase1,padding_ablation,main_grid_3bfm}/` CSV (전부 유지).

**Phase 1 frozen probe benchmark (V_binary AUROC / V_reg Pearson r, best per category)**

| Feature | V_binary | A_binary | V_reg | A_reg |
|---|---|---|---|---|
| CLIP_pretrained (video ceiling) | 0.971 | 0.800 | 0.765 | 0.423 |
| ROI Schaefer400+Tian50 (brain floor) | 0.789 | 0.678 | 0.416 | 0.233 |
| Brain-JEPA (best BFM) | 0.740 | 0.662 | 0.330 | 0.221 |
| NeuroSTORM | 0.729 | 0.637 | 0.312 | 0.191 |
| SwiFT NewE96 / UAH 5M~264M | 0.66~0.69 | 0.60~0.62 | 0.21~0.26 | 0.12~0.16 |

- ROI mean 이 모든 frozen BFM 을 이김. SwiFT 5M→264M scaling 효과 거의 무.
- padding ablation: zero / mean / spatial_only / cyclic_replicate 4 mode 가 overall 0.001 이내 동률 (frozen 이 시간정보 안 씀). replicate 만 약 0.03 worse.
- resting vs scratch init 차이 +0.03~0.06 (작지만 일관).

**Phase 2 joint inference (4 fusion arch, pooled, main metric)**

| Arch | V_binary | A_binary | V_reg | A_reg |
|---|---|---|---|---|
| D late fusion | 0.972 | 0.803 | 0.589 | 0.268 |
| A token transformer | 0.967 | 0.792 | 0.763 | 0.424 |
| B cross-attention | 0.966 | 0.786 | 0.745 | 0.396 |
| C joint probe | 0.961 | 0.770 | 0.712 | 0.352 |
| C brain_only probe | 0.712 | 0.648 | 0.295 | 0.221 |

- joint 가 CLIP 단독 (V_binary 0.97) 위로 추가 향상 없음 → 질문 A 종료.

**Phase 2 brain-only smoke (V_binary fold1 seed0, vs BJ frozen 0.74 reference)**

| Method | I supervised | II distillation | III multitask | IV subject-aware |
|---|---|---|---|---|
| V_binary | 0.711 | 0.715 | 0.714 | 0.711 |

- full benchmark (5 fold × 3 seed × 4 task × 4 method) 진행 중. v4 에서는 여기에 Cat34 / Dim14 / OV-text target 을 추가해 재측정한다 (결과 append, 기존 V/A row 유지).

### Phase 1: Foundation benchmark (W1-6), 완료

frozen probe benchmark (Tier 1 ROI floor / Tier 2 BFM / Tier 3 video) + SwiFT padding ablation + 6 SwiFT variants. 결과: `reports/phase1_wrapup/main.pdf`. 핵심: frozen BFM 어떤 변종도 ROI mean / video 못 넘음, frozen 은 시간정보 안 씀. (질문 A 의 floor 측정)

### Phase 2: Target promotion + brain-only representation (W7-12), 진행 중

- 완료: 4 fusion arch (D/A/B/C) joint inference → video saturate 확인 (질문 A 종료).
- 진행 중: brain-only 4 method (supervised / distillation / multitask / subject-aware) 학습.
- **신규 (v4)**: target 을 Cat34 / Dim14 / OV-text-embedding 으로 승격 (3). brain → emotion-text projector (5.1) prototype. AffectGPT Horikawa sanity check (4.3).
- **Go (Phase 3 진입)**: Horikawa 내 Cat34 / Dim14 에서 brain representation 이 chance + ROI floor 를 유의하게 넘음.

### Phase 3: Cross-dataset transfer (W13-18)

- W13-14: emotion-text projector 로 zero-shot transfer (전략 1) on Emo-FilM / ds000205.
- W15-16: few-shot scaling curve (전략 2, SQ4). label-space intersection 평가.
- W17: RSA / CKA geometry (SQ3), region-restricted (SQ5), representational alignment (전략 4).
- W18: SQ1-SQ5 결과표 + go/no-go.

### Phase 4: Synthesis + submission (W19-24)

cross-evaluation 통합, paper draft, code release. target venue: NeurIPS D&B / Imaging Neuroscience / Nat Commun. fallback 논문 = Phase 1 benchmark + Phase 2 joint negative ("crowd-labeled naturalistic emotion fMRI 는 video-prediction task 임") 단독으로도 publishable.


## 8. Critical files

기존 재사용:
- `code/bfm_embeddings/_lib/{swift,brain_jepa,neurostorm}.py`, `output/embeddings/`
- `code/probes/run_unified_probe.py`, `code/phase2/`

v4 에 만들 새 파일:
- `code/transfer/emotion_text_projector.py`, brain → emotion-text embedding 학습 (5.1)
- `code/transfer/zero_shot_eval.py`, cross-dataset zero-shot retrieval (4.1)
- `code/transfer/fewshot_scaling.py`, few-shot curve (4.2, SQ4)
- `code/annotator/affectgpt_horikawa_sanity.py`, AffectGPT Horikawa 출력 점검 (4.3 first action)
- `code/analysis/geometry_rsa.py`, RSA / CKA geometry (SQ3)

참고용 외부:
- `/pscratch/sd/s/sjmoon/BrainVLM/UMBRELLA_qwen/` (Option A, generative track)
- `/pscratch/sd/s/sjmoon/EmoViS/study1/results/` (stimulus features)


## 9. Risk register

| Risk | Probability | Impact | Mitigation |
|------|------|--------|------------|
| Cross-dataset transfer 전혀 없음 (SQ1 fail) | Med | Critical | 전략 4 (label-free RSA) 로 최소 보고. Horikawa-specific decoder 로 결론 축소 |
| Per-subject self-rating 부재로 subject-specific 분석 불가 | High | High | Horikawa 원 데이터에 per-subject rating 존재 여부 우선 확인. 없으면 group-label + ISC ceiling 으로 재설계 |
| AffectGPT 가 Horikawa 무음 short clip 에서 빈약한 라벨 | Med | Med | first action sanity check. 빈약하면 Cowen norm gold 만 사용, OV 는 target dataset 에만 |
| rich supervision 이 transfer 향상 없음 (SQ2 fail) | Med | Med | honest negative 로 보고. low-dim 으로 충분하다는 결과도 기여 |
| 5 subject 통계 검정력 부족 | High | Med | within-subject + bootstrap CI. cross-dataset transfer 로 N 확장 |
| BrainVLM (Option A) generative track 미완 | Med | Low | main contribution 아님. 5.1 projector 가 main. Phase 4 로 미룸 |
