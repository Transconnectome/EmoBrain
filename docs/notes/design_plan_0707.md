# EmoBrain 전체 설계 + 진행 상세 (2026-07-07)

다른 AI / 협업자 와 논의 하기 위한 self-contained 상세 문서. 프로젝트 의 전체 맥락 (배경 → framework → 지금까지 구현 → 앞으로 설계) 을 빠짐없이 정리. `report_0707.md` 가 "결과 중심" 이라면 이 문서 는 "설계/계획 중심 + 전체 이력".

읽는 순서. §1 배경 → §2 framework → §3 데이터 → §4 지금까지 (Cycle 1-15) → §5 앞으로 (Step 4-8 설계) → §6 열린 질문 → §7 파일 지도.

---

## 1. 프로젝트 배경 과 정체성

### 1.1 한 줄

Human brain fMRI 에서 fine-grained emotion (Cowen-Keltner 34-category) 을 decode 하는 multi-modal LLM framework. 학습 때는 brain + video + caption 을 쓰는 teacher, 추론 때는 brain-only student 가 distillation 으로 이어받는 비대칭 구조. **Novelty 는 특정 encoder 가 아니라 framework 자체** (멀티모달 학습 + brain-only 추론 비대칭 + modality 역할 분리 + 34D 고차원 readout).

### 1.2 이전 framing 의 폐기 이력 (왜 지금 구조 인가)

이 프로젝트 는 여러 pivot 을 거쳤다. 현재 구조 를 이해 하려면 왜 이전 것 을 버렸는지 알아야 한다.

- **v3 (2026-05-27, individual difference).** Frozen BFM (Brain-JEPA, NeuroSTORM, SwiFT) 가 개인차 를 못 잡음 → 폐기.
- **v4 (2026-06-02, universal emotion code, FEEL).** Universal code framing. archive/v4_20260602/ 보존.
- **v5 (2026-06-08~06-28, Three Directions).** D1 BrainVLM + D2 fMRI-LM + D3 CCN 의 3-direction split. archive/v5_direction_split_20260628/ 보존.
- **현재 (2026-06-29 pivot, single project + 5 NV).** Three Directions 를 폐기 하고 하나의 통합 pipeline 으로.

**핵심 motivation evidence (Phase 1 audit, 2026-06-04).** Frozen BFM 6 변종 (Brain-JEPA resting/scratch, NeuroSTORM, SwiFT NewE96 등) 이 모두 단순 ROI ridge baseline 을 못 넘었다. 즉 "더 큰 사전학습 brain model 을 얹어도 emotion decoding 이 안 는다". 이게 "framework (멀티모달 + 비대칭) 로 접근 해야 한다" 는 근거.

**D1 BrainVLM 의 negative result (2026-06-28).** Qwen3-VL + LoRA + ICL 로 V/A binary/regression 을 학습 했으나 실패 (Pearson r 0.008-0.035 vs ROI ridge 0.42). Token output 형식 의 한계 로 판단 → hidden-state 활용 (E4) 으로 재구성.

### 1.3 Spine question (핵심 과학 질문)

> Fine-grained emotion (34 Cowen-Keltner category) 의 표상 이 human brain 에서 얼마나 decodable 한가. 그리고 그 decoding 이 brain activity 고유 의 기여 인가 (video 의 visual content 와 caption 의 semantic content 를 control 한 후 의 brain residual).

4 sub-question.
- (a) **Affect decoding ceiling.** Brain decoding 이 얼마까지 도달 가능 한가. 진짜 ceiling 은 brain ISC / label crowd split-half 로 측정 (Cowen concordance 54% 는 categorical 이라 continuous ceiling 아님).
- (b) **Brain-unique vs shared.** Brain-only accuracy 와 brain+video+caption joint accuracy 의 delta 가 어느 modality 로 설명 되나.
- (c) **Modular encoder hierarchy.** E1-E4 중 어느 것 이 fine-grained affect 를 잘 보존 하나.
- (d) **Behavioral-brain dissociation.** Semantic decoding (well-decoded) vs affect decoding (ceiling-bound) 의 dissociation 을 같은 architecture 에서 reproduce 하나.

### 1.4 Subject pooling = universal emotion code 학습 (중요, 2026-07-07 확정)

5 subject 를 pool 로 학습 하는 목적 은 **데이터 증강 이 아니라 universal (subject-공통) emotion code 만 학습** 하려는 것. 개인차 극복 이 아니라 개인차 를 의도적 으로 배제. Spine question 이 "사람 일반 의 뇌 에서 감정 이 어떻게 표상 되나" 이므로.

- **Within > Pooled > LOSO 는 예상 된 결과** (실측 §4.6). Within 이 높은 건 개인 특화 학습, 그건 우리 관심 아님 (subject-specific 질문). Within 은 우리 spine 과 성능 비교 대상 이 아님.
- **개인차 는 다음 step** (별도/future work). Universal 확립 이 먼저.

---

## 2. Framework 상세 (5 NV + 학습 구조)

### 2.1 5 Novelty

| ID | 이름 | 내용 |
|----|------|------|
| NV0 | LLM-based brain emotion decoder | Emotion 분야 LLM 통합 fine-grained brain decoder 의 first instrument (framing axis) |
| NV1 | 3-modality LLM fusion | brain + video + caption 을 single LLM forward 의 token sequence 로 통합 |
| NV2 | MindCaptioning bridge | Human-written neutral caption 을 brain-context bridge 로 (+ 우리 generated caption 비교) |
| NV3 | Modular brain encoder | E1-E4 swappable adapter. 공통 patchify 없음, 진짜 변수 = 사전학습 유무 + fMRI 적응 |
| NV4 | 34D independent regression + curriculum | 34 감정 독립 회귀 (softmax/KL 금지), per-emotion MSE, curriculum stepwise |

NV0 이 spine framing, NV1-NV4 가 구성 component.

### 2.2 Architecture 전체 흐름

```
Teacher (학습 전용):
  fMRI  → brain encoder(E) → brain projector(E) → N_b brain tokens ┐
  video → video FM          → video projector    → N_v video tokens ┤
  caption(text) ─────────────→ LLM tokenizer      → caption tokens   ┼→ LLM → 34D head → 34D (z-space)
  question(text) ────────────→ LLM tokenizer      → question tokens  ┘

Student (학습 + 추론):
  fMRI  → brain encoder(E) → brain projector(E) → N_b brain tokens ┐
  question(text) ────────────→ LLM tokenizer      → question tokens ┴→ LLM(frozen)+LoRA → 34D head → 34D

Token 순서 (implementation_spec).
  Teacher:  [video] [Caption field] [brain] [Question field]
  Student:  [brain] [Question field]
```

### 2.3 Brain encoder E1-E4 (NV3)

공통 patchify frontend 없음. fMRI 가 곧장 각 encoder 로 들어가고 patchify 는 encoder 안 에서. 진짜 변수 = 사전학습 유무 + fMRI 적응 설계.

| Variant | 정의 | 학습 여부 |
|---------|------|----------|
| E1 | Raw ROI projection (control, no pretrain, no adaptation). 단순 MLP | projector 만 |
| E2 | Ridge latent (task-specific, no LLM pretrain). ROI ridge 의 latent | ridge 학습 |
| E3 | BFM frozen (fMRI 대규모 pretrain). SwiFT / Brain-JEPA / NeuroSTORM | frozen |
| E4 | Image pretrain + fMRI fine-tune. Qwen vision encoder → D1 BrainVLM fMRI fine-tune hidden | D1 학습시, 추출후 frozen |

E3 vs E4 의 진짜 질문 = "fMRI 대규모 pretrain frozen transfer" vs "image pretrain 출발 + fMRI fine-tune adaptation" 중 어느 쪽. **Encoder 순위 자체 는 spine result 가 아님** (framework modularity 검증).

### 2.4 Projector 의 두 목적

Brain/video 는 embedding 이라 LLM 이 못 먹음 → projector (MLP 또는 Q-Former) 로 LLM token 공간 에 사영. 단순 크기 맞추기 가 아니라 (a) 차원 정합 + (b) 표상 정렬 의 학습된 사상.
- Frozen encoder + projector 만 학습 = probing (E3).
- Encoder + projector 동시 = fine-tune (E4).
- Token 수 (N_b, N_v) 가 병목. 너무 적으면 34D 고차원 구조 가 압축 에서 손실. Sweep 대상.

### 2.5 NV4. 34D independent regression (loss)

**핵심 원칙.** 34 감정 은 서로 배타적 아님 (bittersweet = joy + sadness 동시 가능). Softmax / sum-to-1 / KL / cross-entropy 금지. 각 감정 독립 회귀.

- **정답.** 영상당 34D crowd proportion (0-1, 각 감정 을 고른 rater 비율).
- **전처리 (필수).** per-emotion log1p_z (log1p 후 z-score, train fit only). Heavy-tail 완화. 확정 2026-07-07.
- **Loss.** `L_main = sum_{k in A} (pred_k - target_k)^2`. A = curriculum stage 의 active subset.
- **Curriculum.** top-1 → top-2 → top-k → full 34D 의 subset MSE (stepwise validation, distribution 오해 아님).
- **Structure loss (optional, 기본 OFF).** 34×34 correlation matrix matching. 감정 간 관계 를 명시 강제. 기본 은 model shared representation 에 맡김.

### 2.6 학습 paradigm (P2-B distillation)

Training-inference 비대칭.

- **Teacher.** brain + video + caption + question. LoRA-A. 34D 지도학습. **teacher-side modality dropout (caption p=0.3)** 로 caption 없는 forward 도 학습.
- **Student.** brain + question only. 같은 backbone + LoRA-B. Loss = per-emotion MSE (hard label) + λ × distillation MSE (teacher soft label 재현).
- **왜 distillation.** B2 baseline 에서 video (CLIP 0.60) >> brain (0.30). Teacher 에 video 직접 주고 joint 학습 하면 model 이 video 에 의존, brain 무시 → spine 붕괴. Student 는 raw video 안 봄, teacher 의 34D 출력 만 → video 지배 원천 차단.
- **P2-C alignment 제외.** Brain 을 video 에 정렬 하면 leakage 부활 (structural conflict).

### 2.7 실행 구조. Track A / Track B (2-level)

- **Track A.** Brain-only encoder ablation (E1-E4). Context 없이 34D 직접 지도학습. Curriculum A1-A4. Encoder 순위 확정. Leakage 원천 차단.
- **Track B.** Track A best encoder **1개 만** distillation (E1-E4 각각 안 함, scope 확정 2026-07-03). Teacher → soft label → student. Curriculum B1-B4.
  - **Framework 검증 primary question = context lift** (Track A best A4 → Track B best B4 delta). "어느 encoder 가 distillation 과 잘 맞나" 가 아님.
  - **Track B 성공 판정 = context lift + distillation 검증 둘 다 (2026-07-07 필수).**
    - 검증 A. Variance partitioning (brain 고유 성분 vs video 공유 성분).
    - 검증 B. Brain-ablated student (brain 제거 후 남는 성능 → video 우회 주입 경고).

### 2.8 Metric (loss ≠ metric)

Loss = MSE (학습 연료). Metric = 성적표. **Headline 3축 함께** (하나만 보면 속음).
- **Pearson r** (모양). 값을 절반 눌러도 1.0 (scale-blind).
- **CCC (Concordance Correlation Coefficient)** (모양 + 값). `2ρσxσy/(σx²+σy²+(μx−μy)²)`. shape + scale/bias 동시 penalize. 감정 인식 (AVEC) 표준. 2026-07-07 추가.
- **MSE/MAE/R2** (절대 오차). Label 73.8% zero 라 무딤, 보조.

부가. per-emotion Pearson/CCC, RSA (same-space 34×34), dim-compression, sparse retrieval (p@k).

---

## 3. 데이터 명세

| 항목 | 값 |
|------|-----|
| fMRI | Horikawa 2020. 5 subject. ROI mean (Schaefer-400 + Tian-S3-50 = 450). |
| Stimulus | **2185 unique**. fMRI session 2196 presentation 중 11 개 는 reliability check 중복 (두 번 제시). Unique = 2196 − 11 = 2185. |
| Label | 34D Cowen-Keltner crowd proportion (0-1, 영상당 9-17 rater yes/no 의 평균). 73.8% zero (영상당 평균 1.7 category 활성). Sparse 는 본질. |
| 전처리 | per-emotion log1p_z (train fit). zscore mode 도 파일 유지. |
| Split | stimulus-level. train 1748 / val 217 / test 220 (합 2185). Pooled = 5 subj × stim (train 8740 / val 1085 / test 1100). |
| Video/caption feature | stimulus-level embedding. CLIP (1024) / V-JEPA2 (1408) / VideoMAE (1280) / DINOv2 (1536), caption (768). 각 pretrained + scratch. |
| Cross-subject test | MindCaptioning (Horikawa, Science Advances 2025; bioRxiv 2024). cross-subject 이지만 cross-stimulus 아님 (stimulus 겹침). |

**Cowen concordance 주의 (2026-07-07 문헌 재검증).** Cowen 2017 원문 (PMC5617253). "concordance averaging 54% (chance 27%)". ICC 아님. Categorical 일치율 이라 우리 continuous metric 의 직접 ceiling 으로 못 씀. 이전 문서 의 "ICC 0.54" 는 오류 정정.

---

## 4. 지금까지 구현 (Cycle 1-15 상세)

모든 사이클 은 pre-framing (what/process/outcome/narrative) 후 코드 + `.sh` 동반 + smoke/sanity. 결과 는 화면 + json. 실행 은 CPU bash (LLM 학습 아직 없음).

### 4.1 Cycle 1-5. Data 모듈 (Step 1)

**Cycle 1. Label z-score (`project/data/labels.py`).**
`Cowen34Normalizer` class (sklearn StandardScaler 관례 를 torch native 로). mode = zscore / log1p_z. fit (train만) / transform / save / load. Output `norm_stats/cowen34_train_{mode}.pt`. Sanity. train transform 후 per-emotion mean ~0, std ~1.

**Cycle 2. Dataset (`project/data/datasets.py`).**
`HorikawaDataset` pool 5-subj × 2185-stim. (subject, stim) 개별 sample. Label 은 stimulus-level (subject-invariant), fMRI 는 subject-specific. Split 개수 train 8740 / val 1085 / test 1100. 같은 stim 이 5 subject 에 identical label 검증.

**Cycle 3. ROI time-series pt (`project/scripts/build_roi_timeseries.py`).**
Raw ROI CSV (Schaefer 400 + Tian 50) → subject 별 통합 pt. `roi_timeseries (2185, T_max=47, 450)` right zero-pad + `roi_mean (2185, 450)` + `mask` + `original_T`. Sanity. regenerated mean == 기존 reference (float32 tol), padding-invariance (padding 을 noise 로 덮어도 masked mean 동일).

**Cycle 4. FmriAdapter (`project/data/fmri_adapter.py`).**
5 pt 를 memory load. `get(subject, stim, mode="mean"|"timeseries")`. Dataset 의 placeholder zeros → 실제 fMRI. Cross-subject variance 검증 (같은 stim 이 subject 별 fMRI 다름, std 0.18).

**Cycle 5. CaptionMap (`project/data/caption_map.py`).**
`caption_ck20.csv` (2196 stim × 20 rater human caption). Rater 정책 = 옵션 3 (train epoch별 random, val/test fixed seed → 재현성 + 다양성). Mapping = stim_num == video_id (Cowen filename 기준 확정). Qwen-VL caption 은 부정확 발견 (stim 457 gun 을 seashells 로) → skip, 재검증 대기.

### 4.2 Cycle 6-7. Loss + Metric (Step 2)

**Cycle 6. Loss (`project/models/losses/`).**
`supervised.py` (per-emotion MSE, curriculum active mask, per-emotion weight). `structure.py` (34×34 correlation matching, 기본 OFF, batch<4 reject). Sanity. perfect→0, +1std off→정확히 34, active top-1→1.0.

**Cycle 7. Metric (`project/evaluation/metrics.py`).**
profile_correlation (headline), per_emotion, rsa, dim_compression, sparse_retrieval, error (MSE/MAE/R2). Constant clip skip. Dispatcher `compute_metrics`.

### 4.3 Cycle 8. B1 baseline + label 진단 (Step 3 시작)

B1 brain ROI ridge. Metric 확장 (error + sparse). Label 3-preprocessing 비교 (zscore/log1p_z/zscore_clip, 차이 미미). **Label 진단.** 73.8% zero 는 정상 (yes/no 응답 sparse), "전부 0 MSE ~1" 은 z-score 수학. 감정별 편차 (sexual desire 0.46 ~ guilt 0.10).

### 4.4 Cycle 9. Cowen 문헌 검증 (문서 정정)

"ICC 0.54" 오류 확정 (원문 = concordance 54%, categorical). 34D label = crowd proportion 확정 (k/n, rater 9-17). Noise ceiling estimator 에서 concordance 제외.

### 4.5 Cycle 10-11. Noise ceiling 진단

**Cycle 10. Brain ISC (`project/evaluation/noise_ceiling.py`).** spatial ISC 0.23, per-ROI 0.15. 뇌 신호 subject 간 idiosyncratic. 시각 영역만 공통.

**Cycle 11. Subject regime.** within 0.305 / pooled 0.294 / LOSO 0.232. Within > Pooled > LOSO. LOSO chance 0.001 (permutation), real 15.3 SD 위 = universal code 존재. **Universal framing 확정** (§1.4).

### 4.6 Cycle 12. Label 전처리 확정

log1p_z 확정 (rare emotion 이득 + 극단 완화, clip 처럼 순위 손실 없음). 두 mode 별도 파일. LOSO chance permutation 확정.

### 4.7 Cycle 13. B2 modality solo (baseline ladder)

| Modality | Pearson | CCC | RSA |
|----------|---------|-----|-----|
| Brain | 0.296 | 0.173 | 0.777 |
| Video V-JEPA2 | 0.449 | 0.343 | 0.796 |
| Video CLIP | 0.597 | 0.506 | 0.868 |
| Caption | 0.479 | 0.377 | 0.835 |

**Video 지배 34D 에서도 명확** (CLIP 0.60 >> brain 0.30). Distillation 설계 정당화.

### 4.8 Cycle 14. CCC metric 추가

Pearson (모양) + CCC (모양+값) + MSE (절대). Half-scale 에서 Pearson 1.0 vs CCC 0.80 검증. **Pearson-CCC gap 이 핵심** (brain -42%, ridge 가 진폭 못 살림).

### 4.9 Cycle 15. report 외부 검토 반영

RSA 비교 철회 (apples-to-oranges), MindCaptioning 2025, label 스케일 명시, ISC ceiling 표현 정정, **distillation 검증 을 Track B 필수 로 승격**. stimulus 2185 unique 재확인 (2196 = presentation, 11 중복).

### 4.10 Baseline ladder 종합

```
                          Pearson   CCC
chance (permutation)       ~0.00     ~0.00
Brain ROI ridge (B1)        0.30      0.17   ← 우리 뇌 baseline
Video V-JEPA2 solo          0.45      0.34
Caption solo                0.48      0.38
Video CLIP solo             0.60      0.51   ← modality 최고
--- 참고 (다른 축) ---
Brain cross-subject ISC     0.23             (뇌 신호 subject 간 신뢰도, decoding ceiling 아님)
LOSO universal transfer     0.23             (새 subject, chance 대비 15 SD)
within-subject ridge        0.31             (개인 특화 포함, 우리 관심 아님)
```

### 4.11 현재 판단 요약

1. Brain-only 34D decoding 어렵다 (Pearson 0.30, CCC 0.17). Chance 대비 신호 지만 값 (진폭) 을 절반 못 맞춤.
2. Universal emotion code 존재 (LOSO 0.23, 15.3 SD).
3. Video/caption 이 brain 크게 앞섬 (0.60 vs 0.30). Leakage 위험 실증 → distillation 필수.
4. RSA (same-space) 0.78 높음. 개선 여지 = profile 절대값 + 고차원 + sparse + rare emotion + CCC (진폭).
5. Framework 가치 = context lift. 뇌 만 0.30 한계, teacher context 가 얼마나 올리나.

---

## 5. 앞으로 설계 (Step 4-8)

지금까지 는 세팅 (data + loss + metric) + baseline/진단 (ridge). LLM model 은 아직 없음. Step 4 부터 신경망.

### 5.1 Step 4. Models (encoder E1-E4 + projector + prompt + LLM backbone)

**빌드 순서 제안.** ridge 와 자연 스럽게 이어지도록 단순 → 복잡.

1. **E1 (raw ROI + neural head).** ROI mean (450) → 작은 MLP → 34D. "ridge 를 신경망 으로 바꾸면?" 첫 비교. LLM 없이 가능. GPU 가벼움.
2. **E2 (ridge latent + head).** Phase 1 ridge latent → head.
3. **Projector.** ROI/BFM embedding → LLM token 공간. MLP 기본, Q-Former 옵션. Token 수 sweep (N_b 8/16/32).
4. **Prompt 조립 (`prompt.py`).** Caption field + Question field. Question 은 고정 지시문 (implementation_spec §8-3). Vector token 은 placeholder 위치 삽입, text 는 tokenizer 한 번.
5. **LLM backbone (`llm_backbone.py`).** Qwen3-VL (2B/4B) + LoRA + 34D linear head (z-space, activation 없음, softmax 금지). E3-E4 부터 LLM fusion 필요.

**결정 필요 (Step 4 진입 전).**
- E1-E2 는 LLM 없이 (projection → head) 도 되는가, 아니면 처음부터 LLM 통과?
- Token 수 (N_b) 기본값.
- Backbone size 먼저 (2B smoke → 4B).
- Smoke 는 CPU/bash, 학습 은 sbatch (사용자 사전 승인 필수).

### 5.2 Step 5. Track A. Brain-only encoder ablation

각 encoder (E1-E4) 를 brain + question only 로 34D 직접 지도학습 (teacher/student 구분 없음, context 없음). Curriculum A1 (top-1) → A4 (full 34D). Loss = subset per-emotion MSE, log1p_z.

**산출.** E1-E4 의 Pearson + CCC ranking (A4 기준). Baseline (ridge 0.30/0.17) 대비 얼마나 개선. **Leakage 원천 차단** (video/caption 없음). Track A 만 성공 해도 modular encoder ablation + high-D readout 이 하나의 contribution.

### 5.3 Step 6. Teacher + video encoder

Track A best encoder 위 에 teacher (brain + video + caption + question). Video encoder (V-JEPA2 default, 마지막 hidden). Teacher-side caption dropout (p=0.3). Curriculum B1-B4. 34D soft label caching.

**주의.** Video 는 마지막 hidden layer (고차 semantic). 초기 layer 금지 (감정 관련 시각 정보 는 고차 layer, CCN 결과 근거).

### 5.4 Step 7. Student + distillation. Track B

Student (brain + question) 가 teacher 34D soft label 을 MSE 로 재현. Curriculum B1-B4. λ (distill weight) grid, caption dropout grid.

**Track B 성공 판정 (필수 3조건).**
1. Context lift. Track A best A4 → Track B best B4 delta > 0.
2. **검증 A. Variance partitioning.** Student 성능 을 brain 설명 vs video 설명 으로 분해. Distillation 이 brain 고유 성분 을 키웠나.
3. **검증 B. Brain-ablated student.** Brain shuffle/제거 후 남는 성능. 크게 안 떨어지면 video 우회 주입 경고.

Context lift (성능) 만 으로 는 부족. Video (B2 0.60 >> brain 0.30) 우회 주입 을 "brain decoding" 으로 오인 방지.

### 5.5 Step 8. Evaluation 확장

- Variance partitioning (brain / video / caption unique + shared).
- Cross-subject external test (MindCaptioning, cross-stimulus 아님 caveat 명시).
- Mixed emotion 분석 (bittersweet 사례).
- Cross-cohort (Emo-FilM, stretch).
- LOSO transfer (universal code 정량).

### 5.6 병렬 진행 전략 (사용자 제안)

Baseline/encoder 실험 은 학습 시간 길다 → sbatch 로 던져놓고 그 사이 다음 architecture 코드 구현. 단 baseline (ridge) 은 CPU 몇 분 이라 이미 끝. Encoder (E1-E4 LLM) 부터 병렬 이득. Sbatch 는 사용자 사전 승인 필수.

---

## 6. 열린 질문 (다른 AI 논의 요청)

1. **Noise ceiling 정밀화.** ISC/LOSO 는 상한 직접 대리 아님 (뇌 신호 신뢰도 축). 진짜 감정 decoding 상한 을 어떻게? Cowen rater-level 확보 시 crowd split-half.
2. **Video dominance 대응 (최대 날카로운 질문).** Distillation 이 brain 정보 vs video 우회 주입 중 무엇? 검증 A/B 로 충분한가, 더 강한 방법?
3. **Pooling trade-off.** Within (0.31) > Pooled (0.29). Universal framing 으로 정당화 하는데, reviewer 설득 되나?
4. **절대 수준 해석.** Brain Pearson 0.30 / CCC 0.17. 의미 있는 신호 인가 발표 불가 인가. 같은 정의 의 비교 벤치마크?
5. **Label 정의.** Crowd proportion 을 continuous target 으로 (Cowen 원논문 도 averaged proportion). 대안 (binary threshold, ordinal)?
6. **34D independent regression.** Softmax/KL 금지 + per-emotion MSE. 감정 non-exclusive 를 제대로 다루나. Structure loss 를 default on 해야 하나?
7. **Encoder E1-E4 설계.** E4 (image pretrain + fMRI fine-tune) 가 우리 조건 (2185 stim, 소량) 에서 E3 (BFM frozen) 를 이길까? UMBRAE 는 NSD 급 (2-3만 trial) 에서 효과.
8. **Curriculum.** top-1 → top-2 → top-k → 34D 가 34D 직접 학습 보다 나은가. 아니면 처음부터 34D?

---

## 7. 파일 지도

**Framework / 설계.**
- `Paper/framework_EN.md`, `framework_KR.md` — spine narrative + 5 NV + evaluation + sub-claims.
- `docs/notes/architecture_design_20260629.md` — architecture 상세 spec (NV↔component, token budget, curriculum, training paradigm, Stage 0, success criterion).
- `docs/notes/implementation_spec_20260702.md` — code 구현 명세 (DECIDED/OPEN/CAUTION, config schema, repo layout, 34 감정 순서).

**진행 / 결정.**
- `docs/notes/build_log.md` — Cycle 1-15 코드 로그 (최신 위).
- `docs/notes/project_decisions.md` — 결정 로그 (framework pivot, NV4 재정의, Track B scope, Cowen 정정 등).
- `docs/reports/report_0707.md` — 결과 중심 외부 검토 report.
- `docs/notes/design_plan_0707.md` — 이 문서 (설계/계획 중심).

**코드 (project/, single pipeline).**
- `data/` — labels, datasets, fmri_adapter, caption_map.
- `models/` — encoders/ (E1-E4), projector, video_encoder, prompt, llm_backbone, teacher, student. losses/ (supervised, structure, distillation).
- `training/` — train_baseline_ridge, train_modality_solo, (앞으로) train_teacher/student.
- `evaluation/` — metrics, noise_ceiling, (앞으로) cross_subject, ablation, mixed_emotion.
- `scripts/` — 각 .py 의 .sh entry + smoke.
- `shared/` — data (labels csv, split, roi_timeseries pt, norm_stats, stimulus_features), results.

**환경.** NERSC m4641. Python probe/분석 `/pscratch/sd/s/sjmoon/tribev2/.venv`, LLM `/pscratch/sd/s/sjmoon/brainvlm_qwen_env`. Sbatch 사용자 사전 승인.

---

## 8. 한 줄 현황

세팅 (Step 1-2) + baseline/진단 (Step 3) 완료. Brain ridge 0.30/0.17, video 지배 확인, universal code 존재 확인, CCC 도입. LLM model (Step 4~) 은 아직 없음. Baseline 이 앞으로 모든 LLM 결과 의 참조점. 다음 = Step 4 (encoder E1 부터).
