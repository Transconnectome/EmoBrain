# Brain-Tuning V-JEPA2 for Emotion: Full Research Plan

**Last updated:** 2026-04-06  
**Status:** Planning phase (post-CCN 2026 abstract submission)  
**Target venue:** NeurIPS 2026 / ICLR 2027

---

## 0. 연구 서사 (Narrative Arc)

```
CCN 2026 (2-page abstract) — 이미 제출
  "V-JEPA2의 뇌 예측 가능 서브스페이스는 범주 감정으로 조직된다"
  → V-JEPA2가 이미 일부 감정 구조를 인코딩
  → 그러나 이건 self-supervised 학습의 우연한 부산물

                    ↓

Full Paper (이 계획)
  "뇌 반응으로 fine-tune하면 V-JEPA2가 더 잘 감정을 표상한다"
  → Brain supervision이 행동 기반 supervision보다 우월하다
  → 특히 범주 감정에서 (CCN의 mechanistic 근거와 연결)
  → 더 많은 뇌 데이터 = 더 나은 감정 예측 (scaling law)
```

**핵심 주장:**  
뇌는 visual AI 모델에게 없는 **affective supervision signal**을 제공한다.  
이 신호로 fine-tuning하면 독립적인 감정 예측 벤치마크에서 성능이 향상된다.

---

## 1. 핵심 연구 질문 (Research Questions)

**RQ1 (main):** 감정 fMRI로 fine-tune된 V-JEPA2는 vanilla V-JEPA2보다 감정 예측을 더 잘하는가?

**RQ2 (mechanism):** 이 향상이 연속 감정 차원(valence/arousal)보다 범주 감정에서 더 크게 나타나는가? (CCN과 연결)

**RQ3 (supervision source):** Brain supervision이 behavioral supervision보다 더 효과적인가?

**RQ4 (scaling):** 더 많은 참여자(5 → 30 → 75명)의 뇌 데이터를 사용하면 성능이 scaling하는가?

**RQ5 (method):** Raw fMRI vs Brain-JEPA embedding을 supervision target으로 사용하는 것 중 어느 것이 더 나은가? (methodological contribution)

---

## 2. 기존 데이터 및 상태

### 2.1 이미 있는 것 (Horikawa)

| 파일 | 형태 | 설명 |
|------|------|------|
| `video_embeddings/vjepa2_embeddings.npy` | (2196, 1408) | V-JEPA2 ViT-G 임베딩, 이미 추출됨 |
| `video_embeddings/clip_embeddings.npy` | (2196, 512) | CLIP baseline, 이미 추출됨 |
| `brain_embeddings/brain_jepa_embeddings.npy` | (5, 2196, 768) | Brain-JEPA 임베딩, 이미 추출됨 |
| `raw_fmri_results/fmri_raw.npy` | (5, 2196, 450) | 450-parcel 파셀화된 raw fMRI |
| `feature/category.mat` | (2196, 34) | 34 감정 범주 행동 rating |
| `feature/dimension.mat` | (2196, 2+) | Valence, Arousal 행동 rating |

→ **Horikawa용 brain-tuning 즉시 시작 가능**

### 2.2 추가 획득 필요 (Emo-FilM, NeuroEmo)

- Emo-FilM, NeuroEmo fMRI 데이터 확보 필요
- 각 데이터에 대해 Brain-JEPA 임베딩 추출 필요
- 각 데이터 자극 비디오에 대한 V-JEPA2 임베딩 추출 필요
- 두 데이터셋의 파셀화(450-parcel Schaefer 등) 확인 필요

---

## 3. 데이터셋 (전체)

### 3.1 Brain-Tuning Training Data

#### Horikawa 2020 (확보됨)
- **참여자:** 5명 (건강한 성인, 일본)
- **자극:** 2,196개 단편 비디오 클립 (~3초, 정서 유발 콘텐츠)
- **fMRI:** 전뇌, 3T, TR=1s, 전처리 완료
- **감정 레이블:** 34 감정 범주 + valence/arousal (Cowen & Keltner 2017)
- **강점:** 34-category 세분화 라벨, 이미 완전히 처리됨
- **약점:** n=5로 매우 작음, 일반화 한계
- **용도:** pilot brain-tuning, conceptual proof + comparison baseline

#### Emo-FilM 2025 (확보 예정)
- **참여자:** ~30명
- **자극:** 영화 클립 기반 감정 유발 자극
- **fMRI:** 전뇌
- **특징:** 자연주의적 영화 자극, V-JEPA2와 궁합 좋음 (시네마틱 콘텐츠)
- **감정 레이블:** 확인 필요 (VA 연속 혹은 범주)
- **용도:** scale-up brain-tuning training data (n=5 → n=35)

#### NeuroEmo (확보 예정)
- **참여자:** ~40명
- **자극:** 감정 유발 비디오
- **fMRI:** 전뇌
- **용도:** scale-up training data (n=5 → n=75 with all three datasets)

#### Combined (목표)
- **총 참여자:** ~75명
- **비교 포인트:** Moussa & Toneva (88명) 수준에 근접
- **예상 자극 수:** 수천 개 비디오

---

### 3.2 Downstream Evaluation Benchmarks (독립적, training과 무관)

#### Primary: VideoEmotion-8 (VE-8)
- **출처:** Jiang et al. (2014). Predicting emotions in user-generated videos. AAAI.
- **규모:** 1,101 web videos
- **레이블:** 8 Ekman 범주 (anger, anticipation, disgust, fear, joy, sadness, surprise, trust)
- **특징:** crowdsourced 감정 레이블, 웹 비디오 → 완전히 독립적인 도메인
- **평가 방법:**  
  - Linear probe: V-JEPA2 features (vanilla vs brain-tuned) → 8-way classification  
  - Reported metric: top-1 accuracy, macro F1

#### Secondary: EMDB (European Movie Database)
- **출처:** Fasching et al. (2024). EMDB: The Emotional Movie Database. *Behavior Research Methods*.
- **규모:** 1,102 short movie clips
- **레이블:** continuous valence + arousal from multiple raters
- **특징:** 영화 기반 → Emo-FilM과 도메인 유사하지만 독립 데이터셋
- **평가 방법:**  
  - Linear probe: features → valence regression, arousal regression  
  - Reported metric: Pearson r (predicting continuous VA from features)
- **중요성:** RQ2 검증 — 범주 감정 향상 > 연속 감정 향상?

#### Tertiary: Held-out Horikawa behavioral ratings
- **설정:** Horikawa 2196 비디오 중 10%(~220개)를 brain-tuning에서 완전히 제외
- **레이블:** 34 범주 감정 rating + VA rating (이미 있음)
- **평가 방법:**  
  - Brain-tuning: 1976 videos fMRI (train), 220 videos 완전 held-out  
  - Linear probe on held-out: features → 34-way classification  
  - 핵심: brain-tuning이 held-out 비디오의 감정 예측을 향상시키는가?
- **중요성:** Same taxonomy evaluation — CCN 결과와 직접 연결

#### Additional: Cross-Participant Brain Prediction (Generalization)
- **설정:** Brain-tuning on subjects 1-4, test brain prediction on subject 5 (leave-one-out)
- **평가 방법:** Ridge regression encoding model, Pearson r normalized by noise ceiling
- **Moussa & Toneva와의 비교:** 동일한 evaluation protocol 사용
- **중요성:** RQ4 — 참여자 일반화 능력

#### Ablation: Behavior-Tuned Baseline
- **설정:** V-JEPA2 + LoRA, fine-tuned to predict behavioral emotion ratings (not fMRI)
- **Loss:** L2 between predicted and actual 34-category ratings
- **중요성:** RQ3 — Brain supervision이 behavioral supervision보다 나은가?
- **예상 가설:** Brain supervision이 더 나음, 특히 범주 감정에서

---

## 4. 방법론 (상세)

### 4.1 전체 파이프라인

```
[Stage 0] Pre-extraction (이미 완료 for Horikawa)
    비디오 → V-JEPA2 (frozen) → (N_videos, 1408) 저장
    fMRI → Brain-JEPA (frozen) → (N_subj, N_videos, 768) 저장
    fMRI → Parcelization → (N_subj, N_videos, 450) 저장

[Stage 1] Brain-Tuning Fine-tuning
    V-JEPA2 backbone (frozen except LoRA)
        + LoRA rank-8 (transformer attention layers)
        + Projection head → supervision target
    Training loop: 각 참여자 independent backprop (Moussa 방식)
    Supervision targets: (A) Raw fMRI parcels OR (B) Brain-JEPA embeddings

[Stage 2] Feature Extraction (post fine-tuning)
    Brain-tuned V-JEPA2 → extract features for all downstream videos
    Vanilla V-JEPA2 → extract features for all downstream videos

[Stage 3] Downstream Evaluation
    Linear probe (frozen features → emotion labels)
    Multiple benchmarks: VE-8, EMDB, held-out Horikawa
```

### 4.2 Brain-Tuning 아키텍처 (상세)

```python
# V-JEPA2 backbone
vjepa2 = load_vjepa2("facebook/vjepa2-vitg-fpc64-256")  # 1B+ params, frozen

# LoRA injection (attention layers만)
# rank=8, alpha=16, dropout=0.1
# 전체 파라미터의 ~0.625%만 학습

# Projection head (unified across all participants)
# Moussa 방식: shared head, not participant-specific
projection_A = Linear(1408, 450)   # → raw fMRI prediction
projection_B = Linear(1408, 768)   # → Brain-JEPA embedding prediction

# Training
for batch in dataloader:
    video, fmri_parcel, brain_jepa, subject_id = batch
    
    video_feat = vjepa2(video)     # (B, 1408)
    
    # Method A: raw fMRI supervision
    pred_fmri = projection_A(video_feat)   # (B, 450)
    loss_A = F.mse_loss(pred_fmri, fmri_parcel)
    
    # Method B: Brain-JEPA supervision
    pred_bj = projection_B(video_feat)     # (B, 768)
    loss_B = F.mse_loss(pred_bj, brain_jepa)  # 또는 cosine loss
    
    # Per-participant independent backprop (Moussa et al. 방식)
    loss.backward()
```

### 4.3 Brain-Tuning 방법론 비교 (Ablation)

| 조건 | 학습 신호 | Projection target | 비고 |
|------|-----------|------------------|------|
| **Vanilla V-JEPA2** | 없음 | — | Baseline |
| **BT-rawfMRI** | Raw fMRI (450-parcel) | (1408→450) | Moussa 방식 |
| **BT-BrainJEPA** | Brain-JEPA embedding | (1408→768) | **Novel contribution** |
| **BT-Contrastive** | Brain-JEPA (InfoNCE loss) | (1408→768) | CLIP-style alignment |
| **BT-Behavior** | Behavior ratings (34-cat) | (1408→34) | Behavior supervision baseline |
| **BT-BrainJEPA-Multi** | Multi-participant BrainJEPA | (1408→768) | Scale-up version |

### 4.4 Brain-JEPA를 Supervision Target으로 쓰는 이유 (핵심 기여)

**Raw fMRI 문제점:**
- 30K voxel → 너무 고차원, 노이즈 많음
- Participant-specific → 개인차가 학습을 방해
- Anatomical misalignment → 참여자 간 correspondence 불완전

**Brain-JEPA 장점:**
- 768차원 → 저차원, 구조화된 표상
- Subject-invariant → 이미 개인차 제거됨 (공유 구조만)
- Semantic → 감정 관련 뇌 패턴만 포착
- **Multi-participant training이 더 깔끔해짐** → 모든 참여자가 같은 target space 공유

**이것이 Moussa & Toneva와의 핵심 차별점:**
- Moussa: 원시 fMRI 예측 (30K voxels → parcellated)
- 우리: Brain Foundation Model 임베딩 예측 → cleaner, more semantic supervision

### 4.5 Multi-Participant Training (Scale-Up)

```
Horikawa (5명) → Emo-FilM (30명) → NeuroEmo (40명)

각 데이터셋마다:
1. V-JEPA2 임베딩 추출 (각 데이터셋 비디오에 대해)
2. Brain-JEPA 임베딩 추출 (각 데이터셋 fMRI에 대해)
3. 통합 training set 구성

Multi-dataset training:
- Shared LoRA weights + shared projection head (모든 데이터셋 공통)
- 각 참여자 독립 backprop (Moussa 방식)
- 데이터셋 간 비디오 종류가 달라도 OK (domain-agnostic)
```

**Scaling Experiment (RQ4):**
```
5명 (Horikawa만)
35명 (Horikawa + Emo-FilM)
75명 (Horikawa + Emo-FilM + NeuroEmo)
```
→ scaling curve: 참여자 수 vs downstream emotion prediction accuracy

---

## 5. 실험 조건 전체 설계

### 5.1 Model Conditions

```
V1: Vanilla V-JEPA2 (no fine-tuning)
V2: CLIP (별도 baseline)
V3: BT-rawfMRI-5subj (Horikawa only, raw fMRI supervision)
V4: BT-BrainJEPA-5subj (Horikawa only, Brain-JEPA supervision)      ← proposed
V5: BT-Contrastive-5subj (Horikawa only, contrastive loss)
V6: BT-Behavior-5subj (Horikawa only, behavioral ratings)            ← comparison
V7: BT-BrainJEPA-35subj (+Emo-FilM)                                  ← scale-up
V8: BT-BrainJEPA-75subj (+NeuroEmo)                                  ← full scale
```

### 5.2 Evaluation Matrix

| Benchmark | V1 | V2 | V3 | V4 | V5 | V6 | V7 | V8 |
|-----------|----|----|----|----|----|----|----|----|
| VE-8 accuracy | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| EMDB valence r | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| EMDB arousal r | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Horikawa-holdout 34-cat | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| Cross-subject fMRI prediction | ✓ | ✓ | ✓ | ✓ | — | — | ✓ | ✓ |

### 5.3 Category vs V-A Analysis (RQ2 — CCN 연결)

각 downstream benchmark에서:
- Category emotion score 변화 (V1 대비 Δ)
- Valence prediction score 변화 (V1 대비 Δ)
- Arousal prediction score 변화 (V1 대비 Δ)

**예상 결과:**  
Brain-tuning이 category 향상 > VA 향상 → CCN의 "brain-predictable subspace는 categorically organized" 와 일관됨

---

## 6. Compute 계획 (NERSC Scratch)

### 6.1 저장 구조

```
/pscratch/sd/s/sjmoon/EmoFM/braintuning/
├── embeddings/
│   ├── horikawa/
│   │   ├── vjepa2_embeddings.npy          (2196, 1408) — 이미 있음, 링크
│   │   ├── brain_jepa_embeddings.npy      (5, 2196, 768) — 이미 있음
│   │   └── raw_fmri_parcels.npy           (5, 2196, 450) — 이미 있음
│   ├── emofilm/
│   │   ├── vjepa2_embeddings.npy          (N_stim, 1408) — 추출 필요
│   │   └── brain_jepa_embeddings.npy      (30, N_stim, 768) — 추출 필요
│   └── neuroemo/
│       ├── vjepa2_embeddings.npy          (N_stim, 1408) — 추출 필요
│       └── brain_jepa_embeddings.npy      (40, N_stim, 768) — 추출 필요
├── downstream/
│   ├── ve8/
│   │   ├── videos/                         — VE-8 비디오
│   │   ├── labels.csv                      — 8-category labels
│   │   └── embeddings/                     — 각 모델 조건 임베딩
│   └── emdb/
│       ├── clips/                          — EMDB 클립
│       ├── ratings.csv                     — VA ratings
│       └── embeddings/
├── checkpoints/
│   ├── bt_rawfmri_5subj/                  — ~2GB per checkpoint
│   ├── bt_brainjepa_5subj/
│   ├── bt_brainjepa_35subj/
│   └── bt_brainjepa_75subj/
├── results/
│   ├── downstream_ve8.csv
│   ├── downstream_emdb.csv
│   ├── scaling_curve.csv
│   └── cat_vs_va_analysis.csv
└── logs/
    └── training_logs/
```

### 6.2 저장 용량 추정

| 항목 | 예상 크기 |
|------|-----------|
| V-JEPA2 임베딩 (Horikawa, 이미 있음) | ~12 MB |
| V-JEPA2 임베딩 (Emo-FilM + NeuroEmo 비디오) | ~50-100 MB |
| Brain-JEPA 임베딩 (모든 데이터셋) | ~100-200 MB |
| LoRA checkpoint (1개, ViT-G) | ~200-500 MB (LoRA만, backbone 제외) |
| 모든 checkpoint (8개 조건) | ~2-4 GB |
| Downstream 비디오 (VE-8, EMDB) | ~10-20 GB |
| 총 예상 | **~30-40 GB** (pscratch 충분) |

### 6.3 계산 비용 추정

**Stage 0 (V-JEPA2 임베딩 추출):**
- GPU: V-JEPA2 ViT-G, batch=8, A100 1장
- Emo-FilM + NeuroEmo: ~2-4시간

**Stage 1 (Brain-Tuning Fine-tuning):**
- V-JEPA2 ViT-G (1B+) + LoRA rank-8
- 배치 구성: video → V-JEPA2 특징 (미리 추출된 것 사용 가능, 빠름!)
- **핵심 최적화:** V-JEPA2 임베딩을 미리 추출해 저장하면 backbone 통과 불필요
  - 저장된 (N, 1408) 임베딩 → LoRA transformation → projection head
  - 이 경우 LoRA가 임베딩 공간에서 학습하는 adapter 역할
  - 훨씬 가벼운 학습 (backbone inference 없음)
- **대안:** V-JEPA2를 실시간으로 통과시키고 LoRA 그래디언트 계산 (더 정확하지만 메모리 集중)
- 예상: A100 1-2장, ~6-12시간/조건

**Stage 2 (Downstream Evaluation):**
- Linear probe: CPU로도 가능, <30분
- Feature extraction: GPU 1장, ~1시간

### 6.4 NERSC Job 전략

```bash
# pscratch: 빠른 병렬 I/O, 20TB 할당
# 임시 데이터, 체크포인트 → pscratch
# 최종 결과, 코드 → $HOME 또는 $CFS

# 추천 job 구성:
# 1. embedding extraction: 1 A100, 4h
# 2. brain-tuning (조건별): 2 A100, 12h each → --array=0-7
# 3. downstream eval: CPU batch, 1h
```

---

## 7. Brain-JEPA 활용 전략 (심화)

### 7.1 Brain-JEPA란?

- **Bedel et al. (2024)**: BrainJEPA — 뇌 활동 표상 학습을 위한 joint-embedding predictive architecture
- **입력:** 450-parcel fMRI (Schaefer parcellation)
- **출력:** 768-dim subject-invariant embedding
- **특징:** 여러 참여자의 fMRI에서 공통 구조 학습 → 개인차 제거

### 7.2 왜 Brain-JEPA가 더 나은 supervision target인가?

```
Raw fMRI (450-dim, participant-specific)
   문제: 개인 해부학적 차이, 생리적 노이즈, 비-감정적 분산

Brain-JEPA (768-dim, subject-invariant)
   장점 1: 참여자 간 공통 신호만 포착
   장점 2: 감정 관련 뇌 패턴이 더 명확하게 구조화됨
   장점 3: Multi-participant training이 통합된 target space 공유
   장점 4: 노이즈 감소 → V-JEPA2가 더 선명한 supervision 받음
```

### 7.3 Brain-JEPA 활용 방법 3가지

**방법 A: Regression Supervision (메인)**
```
V-JEPA2(video) → LoRA → projection(1408→768) → L2 loss vs Brain-JEPA(fMRI)
```

**방법 B: Contrastive Alignment (추가 실험)**
```
V-JEPA2(video) → proj_v(1408→D)
Brain-JEPA(fMRI) → proj_b(768→D) [frozen]
InfoNCE loss: maximize sim(video_i, brain_i) vs sim(video_i, brain_j≠i)
```
→ CLIP-style video-brain alignment
→ Zero-shot emotion retrieval 가능 (video → brain space → nearest emotion category)

**방법 C: Representational Alignment Loss (탐색적)**
```
L_RSA = 1 - r(RSM_vjepa2(batch), RSM_brain_jepa(batch))
비디오 쌍의 유사성 구조를 뇌 쌍 유사성 구조와 맞춤
```
→ 임베딩 값이 아니라 구조(geometry)를 supervision

### 7.4 Frozen Brain-JEPA vs Fine-tuning Brain-JEPA

**권장: Brain-JEPA frozen** (적어도 처음에는)
- Brain-JEPA는 이미 subject-invariant representation 학습됨
- Fine-tuning하면 이 특성이 무너질 수 있음
- V-JEPA2만 조정하는 것이 더 깔끔한 실험

**탐색적: Joint training**
- V-JEPA2(LoRA) + Brain-JEPA(LoRA) 동시에 fine-tune
- 비디오-뇌 공통 표상 공간 학습
- 리스크: 더 복잡, 해석 어려움

---

## 8. 예상 결과 및 주장

### 8.1 Main Result (예상)

```
                VE-8 Acc.   EMDB-V r   EMDB-A r   Horikawa-34cat
Vanilla V-JEPA2   baseline    baseline   baseline    baseline
CLIP              ±           ±          ±           ±
BT-rawfMRI        +Δ1         +δ1        +δ1         +Δ1
BT-BrainJEPA      +Δ2         +δ2        +δ2         +Δ2  (Δ2 > Δ1)
BT-Behavior       +Δ3         +δ3        +δ3         +Δ3  (Δ2 ≈ Δ3 or Δ2 > Δ3)
BT-BrainJEPA-35   +Δ4         +δ4        +δ4         —    (Δ4 > Δ2)
BT-BrainJEPA-75   +Δ5         +δ5        +δ5         —    (Δ5 > Δ4, scaling)
```

### 8.2 Category vs. V-A Result (RQ2, CCN 연결)

```
Brain-tuning으로 인한 향상:
  Category emotion 향상 > Valence/Arousal 향상

이것이 의미하는 것:
  뇌가 제공하는 고유 신호 = 감정 범주 구조
  연속 차원(VA)은 행동 측정으로도 충분히 포착됨
  범주 감정은 뇌 신호 없이는 잘 안 잡힘
```

### 8.3 논문의 핵심 Claim

1. **뇌는 행동과 다른 affective supervision signal을 제공한다**  
   — BT-Brain이 BT-Behavior보다 좋은 경우, 특히 범주 감정에서

2. **Brain-JEPA supervision이 raw fMRI supervision보다 효과적이다**  
   — BT-BrainJEPA > BT-rawfMRI → foundation model을 supervision target으로 쓰는 것의 가치

3. **더 많은 뇌 데이터 = 더 나은 감정 표상 (scaling)**  
   — 5 → 35 → 75 참여자 scaling curve

4. **이 모든 것이 CCN 발견과 일관된다**  
   — 뇌 예측 가능 서브스페이스의 범주 조직화 → 뇌 supervision이 범주 감정을 개선

---

## 9. Figure 계획

### Figure 1: Conceptual Overview
```
패널 A: CCN 발견 요약 (motivation)
  → V-JEPA2 brain-predictable subspace는 categorically organized
패널 B: Brain-tuning pipeline 도식
  → Video → V-JEPA2(+LoRA) → projection → Brain-JEPA(fMRI) → L2 loss
  → Scale: 5 → 35 → 75 participants
패널 C: Evaluation framework 도식
  → VE-8 / EMDB / Horikawa holdout
```

### Figure 2: Main Result
```
패널 A: VE-8 accuracy (8-category)
  → 모든 조건 bar chart
  → Vanilla / BT-rawfMRI / BT-BrainJEPA / BT-Behavior
패널 B: EMDB valence + arousal Pearson r
  → 동일 조건 bar chart
패널 C: Horikawa holdout 34-category
  → 34개 감정 sorted, 조건별 비교
```

### Figure 3: Category vs. V-A Analysis (CCN 연결)
```
패널 A: Category gain vs V-A gain (scatter per condition)
  → BT-BrainJEPA가 오른쪽 위 (category gain 큼)
패널 B: Category / V-A ratio (CCN Fig 2B 스타일)
  → Brain-pred subspace (CCN) vs Brain-tuned (이 논문) 비교
```

### Figure 4: Scaling Analysis
```
패널 A: Downstream accuracy vs n_participants (scaling curve)
  → 5 / 35 / 75 점
  → VE-8 + EMDB average
패널 B: Cross-subject brain prediction (generalization)
  → n_participants vs brain alignment
  → Moussa & Toneva와 비교 가능한 포맷
```

### Figure 5: Supervision Method Comparison
```
패널 A: Raw fMRI vs Brain-JEPA supervision 비교
패널 B: Contrastive vs Regression supervision 비교
패널 C: LoRA rank ablation (rank 4/8/16/32)
```

---

## 10. 논문 구조 (예상)

```
Abstract

1. Introduction
   - Visual models lack affective supervision
   - Brain encodes emotion categorically (CCN finding)
   - Brain-tuning as affective supervision injection
   - Contributions: (1) method, (2) Brain-JEPA target, (3) scaling, (4) category-specific improvement

2. Related Work
   - Brain-model alignment (encoding models)
   - Self-supervised video models (V-JEPA2)
   - Brain-tuning (Moussa & Toneva 2025)
   - Emotion in AI (categorical vs dimensional)
   - Brain Foundation Models (Brain-JEPA)

3. Methods
   3.1 V-JEPA2 and LoRA fine-tuning
   3.2 Brain Foundation Model as supervision target
   3.3 Multi-participant training procedure
   3.4 Datasets (Horikawa + Emo-FilM + NeuroEmo)
   3.5 Downstream benchmarks

4. Results
   4.1 Brain-tuning improves emotion prediction (RQ1)
   4.2 Category gains exceed dimensional gains (RQ2)
   4.3 Brain supervision vs behavioral supervision (RQ3)
   4.4 Scaling with more brain data (RQ4)
   4.5 Brain-JEPA vs raw fMRI as supervision (RQ5)

5. Discussion
   - Mechanistic interpretation (CCN 연결)
   - Brain as affective supervisor for visual AI
   - Limitations: domain specificity, stimuli overlap risk
   - Future: other modalities, real-time brain-tuning

6. Conclusion

References
```

---

## 11. 즉시 해야 할 일 (Action Items)

### Phase 1: Proof of Concept (Horikawa only, 5명)

- [ ] **Script 작성:** `braintuning/01_braintune_horikawa.py`
  - 기존 임베딩 로드 (vjepa2_embeddings.npy, brain_jepa_embeddings.npy)
  - LoRA adapter 정의 (임베딩 공간에 적용, backbone inference 불필요)
  - Projection head (1408→768)
  - L2 loss, per-participant backprop
  - 조건 V3 (rawfMRI), V4 (BrainJEPA), V6 (Behavior)

- [ ] **Script 작성:** `braintuning/02_downstream_eval.py`
  - Linear probe on VE-8 (download VE-8 먼저)
  - Linear probe on Horikawa held-out
  - Category vs V-A analysis

- [ ] **VE-8 데이터 확보:**
  - Jiang et al. (2014) 데이터셋 다운로드
  - V-JEPA2 임베딩 추출 (각 비디오)

- [ ] **EMDB 데이터 확보:**
  - Fasching et al. 데이터셋 다운로드
  - V-JEPA2 임베딩 추출

### Phase 2: Scale-Up (Emo-FilM + NeuroEmo 추가)

- [ ] Emo-FilM fMRI 데이터 접근 및 전처리
- [ ] Brain-JEPA 임베딩 추출 (Emo-FilM)
- [ ] V-JEPA2 임베딩 추출 (Emo-FilM 비디오)
- [ ] 동일 반복 for NeuroEmo

### Phase 3: Full Experiment

- [ ] Multi-dataset joint training
- [ ] Scaling curve 실험
- [ ] Ablation: LoRA rank, loss type, frozen vs tuned Brain-JEPA
- [ ] Cross-dataset generalization 실험

---

## 12. 핵심 리스크 및 대응

| 리스크 | 가능성 | 대응 |
|--------|--------|------|
| Brain-tuning이 전혀 효과 없음 | 낮음 | Moussa et al. 선례 있음. 효과가 작으면 negative result로도 출판 가능 |
| BT-BrainJEPA ≤ BT-rawfMRI | 중간 | BrainJEPA 자체가 noise smoothed raw라서 가능. 이 경우 방법 비교 논문으로 재프레이밍 |
| BT-Brain ≤ BT-Behavior | 중간 | "뇌가 필요 없다"는 반증. 하지만 범주/VA 분리 분석 여전히 흥미로움 |
| Emo-FilM/NeuroEmo 파셀화 방식 불일치 | 중간 | Brain-JEPA는 다양한 파셀화 지원 여부 확인 필요 |
| VE-8이 너무 작아서 linear probe 불안정 | 낮음 | K-fold CV 사용, EMDB로 보완 |
| Catastrophic forgetting (downstream 성능 저하) | 낮음 | Moussa 논문에서 "never underperforms" 확인됨. LoRA + frozen backbone |

---

## 13. 참고문헌

- Moussa, O., & Toneva, M. (2025). Brain-tuning improves generalizability and efficiency of brain alignment in speech models. *NeurIPS 2025*. arXiv:2510.21520
- Bedel, H. A., et al. (2024). BrainJEPA: Representation learning for brain activity using joint-embedding predictive architecture. arXiv:2409.19407
- Horikawa, T., et al. (2020). The neural representation of visually evoked emotion is high-dimensional, categorical, and distributed across transmodal brain regions. *iScience*, 23(5).
- Assran, M., et al. (2025). V-JEPA 2: Self-supervised video models enable understanding, prediction and planning. arXiv:2506.09985
- Jiang, Y. G., et al. (2014). Predicting emotions in user-generated videos. *AAAI 2014*. [VideoEmotion-8]
- Fasching, M., et al. (2024). EMDB: The Emotional Movie Database. *Behavior Research Methods*.
- Hu, E. J., et al. (2022). LoRA: Low-rank adaptation of large language models. *ICLR 2022*.
- Cowen, A. S., & Keltner, D. (2017). Self-report captures 27 distinct categories of emotion. *PNAS*.
