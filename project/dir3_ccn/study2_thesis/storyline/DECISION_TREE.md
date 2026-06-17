# Emotion Foundation Model — Decision Tree

**방향성과 모든 의사결정 지점을 정리한 문서**  
**Last updated:** 2026-04-10

---

## Goal

> **Emotion Foundation Model 개발: 사람의 감정을 잘 포착하는 모델을 만든다. 뇌 데이터를 활용해서.**

## 프레임워크: 세 축

```
        Stimulus (AI model)
       /                    \
      /    Chapter 1          \   Chapter 4 (Brain-Tuning)
     /     S → B               \  S + Brain → Better S → B
    /                           \
Brain (fMRI) ──────────── Behavior (emotion rating)
             Chapter 2                = OUTPUT
             Brain → B
        
Chapter 3: Variance Partitioning (S + Brain → B)
```

**Behavior = output.** 34 categories + 14 affective dimensions.

---

# 1. STIMULUS 축 Decisions

## 1a. 어떤 모델을 쓸 것인가?

| 모델 | 종류 | 학습 방식 | 차원 | Temporal | 코드/체크포인트 |
|------|------|----------|------|---------|--------------|
| V-JEPA2 | Video | Self-supervised (masked prediction) | 1408 | ✓ | ✓ 있음 |
| CLIP (ViT-L) | Image+Text | Contrastive (language) | 512 | ✗ | ✓ 있음 |
| DINOv2 (ViT-G) | Image | Self-supervised (distillation) | 1536 | ✗ | ✓ 있음 |
| VideoMAE v2 | Video | Self-supervised (masked autoencoder) | 1408 | ✓ | ✓ 있음 |
| InternVideo2 | Video | Multi-modal | 1408 | ✓ | ✓ 있음 |
| SigLIP | Image+Text | Sigmoid contrastive | 1152 | ✗ | ✓ 있음 |

### 선택 기준

```
(a) Self-supervised (감정 라벨 없이 학습) → brain supervision 효과를 보려면 필요
    → CLIP, SigLIP은 language supervision 있음 → 비교군으로
(b) Video 처리 (temporal) → Horikawa가 3초라 약하지만, 긴 자극에서 중요
(c) 뇌와의 alignment → Chapter 1에서 실험으로 확인
(d) Conwell (2025) 재현 가능 → VA prediction 비교
```

### Decision

```
확정: V-JEPA2 (메인), CLIP (비교군) — 이미 임베딩 있음
추가 필요: DINOv2, VideoMAE — 임베딩 추출 필요
→ 4개 모델 비교 후 best를 brain-tuning의 base로 사용
```

### 미결정

```
? Image vs Video 비교를 어디까지 할 건지
  → Horikawa가 3초(image-like)라 차이 안 날 수 있음
  → 하지만 Emo-FilM/ReelMo에서는 차이날 것
  → 일단 Horikawa에서 4개 비교하고 판단

? Conwell (2025)의 180개 모델 중 일부를 재현할 건지
  → 시간 걸림. 핵심 4개면 충분할 수 있음
```

## 1b. 임베딩 추출 방법

```
V-JEPA2: 16 frames sampled, ViT-G, CLS token or spatial average → (1408,)
CLIP: 첫 프레임 or 중간 프레임 → (512,)
DINOv2: 첫 프레임 → (1536,)
VideoMAE: 16 frames → (1408,)

결정 필요:
  ? 여러 프레임 평균 vs 단일 프레임 vs temporal aggregation
  ? Horikawa 3초 = ~5프레임이라 차이 작을 수 있음
```

---

# 2. BRAIN 축 Decisions

## 2a. 뇌 표상 선택지

### 사용 가능한 Brain Foundation Models

| 모델 | 학습 데이터 | 규모 | 입력→출력 | 체크포인트 | 비고 |
|------|-----------|------|---------|----------|------|
| **Raw fMRI** | — | — | 원본 (450 parcels) | ✓ 있음 | 노이즈, 신호 손실 없음 |
| **Brain-JEPA** | UK Biobank resting (40K subj) | 768-dim | fMRI→embedding | ✓ 있음 | Task 신호 절반 손실 (확인됨) |
| **SwiFT** | 다양한 fMRI | Swin4D | 4D fMRI volumes | ✓ 코드 있음 ([GitHub](https://github.com/Transconnectome/SwiFT)) | SNU 출신 모델. pretrained weight 공개 예정 |
| **BrainLM** | UK Biobank resting (6700h) | Transformer | fMRI→embedding | △ 코드+weight 공개 예정 ([ICLR 2024](https://openreview.net/forum?id=RwI7ZEfR27)) | Resting-state only |
| **BrainSN** | Resting + naturalistic task (1256h) | Transformer | fMRI→embedding | ✗ 접근 불가 | Task 포함, 하지만 못 씀 |
| **fMRI-LM** | Resting + task | Transformer+VQ | fMRI→LLM tokens | △ 코드 있음 ([arXiv](https://arxiv.org/abs/2511.21760)) | LLM space alignment |
| **LCM** | HCP 등 (10K scans) | 1.2B params | Connectome | ✓ weight 공개 ([arXiv](https://arxiv.org/html/2510.18910)) | 가장 큰 brain FM |
| **TRIBE v2** | Naturalistic task (451h, 25 subj) | Multi-modal | 자극→predicted fMRI | ✓ HuggingFace | Encoding model (방향 다름) |

### 핵심 분류

```
학습 데이터 기준:
  Resting-state only: Brain-JEPA, BrainLM
  Resting + Task:     BrainSN (못 씀), LCM
  Task only:          TRIBE v2 (encoding 방향)
  
모델 방향 기준:
  Brain encoder (fMRI→embedding): Brain-JEPA, BrainLM, BrainSN, SwiFT
  LLM alignment (fMRI→tokens):    fMRI-LM
  Brain decoder (stimulus→fMRI):  TRIBE v2
```

## 2b. 공정한 비교 문제

```
문제: 
  Brain-JEPA = UK Biobank 40K subjects로 학습
  만약 다른 모델을 HCP 176명으로 학습하면 → 데이터 크기 차이
  → 모델 차이인지 데이터 차이인지 구분 불가

해결 방안들:

방안 1: 같은 모델, 다른 입력
  Brain-JEPA(Horikawa fMRI) → embedding → 감정 예측: X
  Raw fMRI(Horikawa fMRI) → 직접 → 감정 예측: Y
  → 모델의 효과를 봄 (Brain-JEPA가 도움 vs 방해)

방안 2: 여러 foundation model 비교 (현실적으로 가능한 것만)
  Raw fMRI vs Brain-JEPA vs SwiFT vs fMRI-LM
  → 각각 Horikawa fMRI에 적용 → 동일 기준 비교
  → 모델 학습 데이터가 다르지만, "현실에서 사용 가능한 best option은?"

방안 3: 같은 아키텍처, 다른 pretrain 데이터
  SwiFT(pretrain 없이) vs SwiFT(HCP pretrain) vs SwiFT(UK Biobank pretrain)
  → 가장 공정하지만, pretrain 시간/자원 필요
  
방안 4: 포기하고 Raw fMRI만 쓴다
  → 가장 단순. Raw가 이미 가장 좋은 결과.
  → "foundation model은 현 단계에서 감정에 도움 안 됨" = negative finding이지만 의미 있음
```

### Decision

```
확정:
  ✓ Raw fMRI = 메인 (신호 손실 없음, Horikawa도 이걸 씀)
  ✓ Brain-JEPA = resting-state 비교군 (이미 있고, 한계 보여주기)
  ✓ ROI selection = theory-driven (Lindquist 2012, Kober 2008)

추가 탐색:
  ? SwiFT — SNU 모델이고 코드 있음. pretrained weight 확인 필요
  ? fMRI-LM — LLM token 방식이 brain-tuning에 쓸 수 있음
  ? LCM — 1.2B, weight 공개, HCP 포함 학습 → 확인 필요

확인해야 할 것:
  - SwiFT pretrained weight 실제 다운로드 가능한지
  - fMRI-LM 코드 실행 가능한지 (450 ROI 호환)
  - LCM이 Horikawa fMRI에 적용 가능한지
```

## 2c. Resting vs Task 비교 — 이게 킥

```
이미 확인된 것:
  Raw fMRI (task): 6 brain-pred PCs, Cat/VA = 1.68
  Brain-JEPA (resting pretrain): 3 brain-pred PCs, Cat/VA = 1.44
  → Resting 모델이 task 신호 절반 손실

이걸 더 발전시키려면:
  Raw fMRI에서 Brain-JEPA가 설명하는 부분 제거 → task residual
  task residual → 감정 디코딩 → 이게 "resting에 없는 감정 신호"

만약 여러 foundation model로 비교하면:
  Resting-only model (Brain-JEPA, BrainLM) → 감정 예측 R²
  Resting+Task model (LCM, SwiFT-pretrained) → 감정 예측 R²
  Raw fMRI → 감정 예측 R²
  
  → "task 데이터가 pretrain에 포함되면 감정 신호가 보존되는가?"
  → 이게 brain foundation model 분야에 대한 메시지
```

---

# 3. BEHAVIOR 축 Decisions

## 3a. 타겟 변수

```
확정:
  ✓ 34 emotion categories (Cowen & Keltner 2017)
  ✓ 14 affective dimensions:
    - Arousal, Valence, Dominance (기본 3)
    - Approach, Attention, Certainty, Commitment, Control,
      Effort, Fairness, Identity, Obstruction, Safety, Upswing (추가 11)
  = 총 48 targets
```

## 3b. Scaling

```
문제:
  34 categories: 0~1, sparse (74% zeros)
  14 dimensions: 1~9, dense

방법:
  ✓ Z-score: 각 target을 mean=0, std=1 → R² 비교 공정
  ✓ Rank transform: 분포 차이 완전 제거 → robustness check
  → 둘 다 하고 비교
  
Cowen 방식:
  동일 수의 PCA components로 축소 후 비교
  → 34 cat PCA(k) vs 14 dim PCA(k) → 같은 차원에서 예측력 비교
```

## 3c. 디코딩 방법

```
확정:
  Regression: Ridge regression, 5-fold CV
    Metrics: R², Pearson r, MSE, Spearman ρ
  
  Classification: binary (상위 25% vs 하위 25%)
    Metrics: AUC-ROC, balanced accuracy, F1

  Cross-validation:
    (1) 5-fold CV on videos
    (2) Leave-one-subject-out CV
    
미결정:
  ? Multi-label 할 건지 (34개 동시)
  ? Non-linear model (MLP, RF) 시도할 건지
  → 일단 Ridge로 하고, 결과 보고 판단
```

---

# 4. BRAIN-TUNING Decisions

## 4a. 방법론 선택지

```
방법 A: Direct prediction (Moussa 방식)
  V-JEPA2(1408) → adapter → predict fMRI(450) → L2 loss
  장점: 단순, 빠름, 선례 (Moussa 2025)
  단점: L2가 최적인지 모름, fMRI 공간이 좋은 target인지 모름

방법 B: LLM token alignment (fMRI-LM 방식)
  fMRI(450) → fMRI-LM tokenizer → LLM token space
  Video → captioning → text → LLM token / 또는 Video → projection → LLM space
  → contrastive + domain-adversarial loss
  장점: LLM space가 감정 의미를 이미 인코딩, 의미적으로 풍부
  단점: 복잡, video→LLM 변환도 결정 필요
  
  Video → LLM 변환 선택지:
    B1. Video → BLIP-2/LLaVA → caption text → LLM tokens
    B2. Video → V-JEPA2 → linear projection → LLM space
    B3. Video → GPT-4V → description → LLM tokens

방법 C: Contrastive alignment (CLIP-like)
  V-JEPA2(1408) → proj → shared space
  fMRI(450) → proj → shared space  
  InfoNCE loss
  장점: 단순하면서도 구조적, CLIP에서 증명된 방법
  단점: negative sampling 설계 필요

방법 D: Brain-inspired module (VCA 방식)
  V-JEPA2 backbone + amygdala-like module (trainable)
  fMRI로 amygdala module만 학습
  장점: 생물학적 해석 가능, VCA 논문 확장
  단점: 구현 복잡, 편도체만으로 충분한지 (전뇌 distributed인데)
```

### Decision

```
확정:
  ✓ Stage 1: 방법 A (Moussa 방식)로 proof of concept
    → brain-tuning이 되는지 빠르게 확인
    → 5가지 조건: vanilla / brain(raw) / brain(BJ) / behavior(cat) / behavior(VA)

나중에 결정:
  ? Stage 2: A가 되면 → B or C or D로 개선
  ? B의 video→LLM 방법: caption? projection?
  ? D의 amygdala module 설계: VCA 따라할지 변형할지
```

---

# 5. 분석 구조 — Chapter별

## Chapter 1: Stimulus → Behavior

```
"AI 모델만으로 감정을 얼마나 예측할 수 있는가?"

입력: V-JEPA2 / CLIP / DINOv2 / VideoMAE embedding
출력: 48 targets (34 cat + 14 dim)
방법: Ridge regression, 5-fold CV
비교: 모델 간, category vs dimension, VA vs category

Conwell (2025) 재현+확장:
  VA에서 ~67% 재현되는가?
  34 범주에서는?
  14 dim에서는?
  어떤 모델이 가장 좋은가?
```

## Chapter 2: Brain → Behavior

```
"뇌만으로 감정을 얼마나 예측할 수 있는가?"

입력: Raw fMRI / Brain-JEPA / (SwiFT? LCM? fMRI-LM?)
출력: 48 targets
방법: Ridge regression, 5-fold CV + leave-one-subject-out
비교: Raw vs foundation models, 전뇌 vs emotion ROIs

Horikawa (2020) 재현+확장:
  원본 결과와 일치하는가?
  14 dim 추가하면?
  Brain-JEPA가 Raw보다 나은가 못한가? (이미 답: 못함)
  ROI별 차이는?
```

## Chapter 3: Stimulus + Brain → Behavior

```
"뇌를 추가하면 감정 예측이 좋아지는가?"

Variance Partitioning (48 targets 각각):
  R²(Stimulus alone)
  R²(Brain alone)
  R²(Both)
  → Stimulus unique / Brain unique / Shared 분해

Brain unique가 큰 감정 = brain-tuning으로 가장 개선될 감정
Brain unique가 0인 감정 = Stimulus만으로 충분

Partial Mantel: r(Brain, Behavior | Stimulus) → Raw fMRI로 재실행
```

## Chapter 4: Brain-Tuning

```
"뇌의 고유 정보를 AI 모델에 주입하면?"

Stage 1: Moussa 방식 proof of concept
  5가지 조건 비교 → 48 targets

핵심 질문:
  Brain-tuned > Vanilla? → brain-tuning 자체의 효과
  Brain-tuned > Behavior-tuned? → 뇌가 행동 rating보다 나은가?
  Brain(raw) > Brain(JEPA)? → 어떤 뇌 표상이 best?
  범주에서 더 향상? VA에서 더 향상? → Cat/VA 변화

Stage 2 (시간 되면): LLM token alignment or contrastive
```

---

# 6. 데이터 관련 Decisions

## 현재 데이터

```
✓ Horikawa: 5 subj, 2196 videos, 34 cat + 14 dim, Raw fMRI + Brain-JEPA
→ 모든 Chapter의 메인 데이터
```

## 추가 데이터 (나중에)

```
Emo-FilM: 30 subj, 14 films, 50 emotion items → 재현 + scaling
ReelMo: 20 subj (fMRI), Jojo Rabbit, moment-by-moment → temporal dynamics
HCP-movie: 176 subj, 7T → 규모 + 개인차
→ 지금은 Horikawa만으로 Chapter 1-4 완성 → 추가 데이터는 그 다음
```

---

# 7. 즉시 행동 (Action Items)

```
이번 주:
  1. SwiFT pretrained weight 확인 (GitHub)
  2. fMRI-LM 코드 실행 가능한지 확인
  3. LCM weight 다운로드 + 적용 가능한지 확인
  4. DINOv2, VideoMAE 임베딩 추출 시작
  5. Horikawa GitHub에서 원본 결과 가져오기
  6. 14 dim 포함한 Chapter 1 통합 스크립트 작성

다음 주:
  7. Chapter 1 실행 (4개 모델 × 48 targets)
  8. Chapter 2 실행 (Raw vs Brain-JEPA × 48 targets + ROI)
  9. Chapter 3 실행 (Variance Partitioning)

그 다음:
  10. Chapter 4 Stage 1 (Brain-tuning proof of concept)
```
