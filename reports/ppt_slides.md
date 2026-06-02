# FEELIN PPT Slides (7 슬라이드)

스타일은 첨부 스크린샷의 1) Data / 2) Task / 3) 모델 / 4) ablation 형식.
각 슬라이드 = 텍스트 압축 + figure 1 ~ 2 장.

figure 경로
  ppt_slides_figs/                  = 이 PPT 용 신규 생성
  reports/phase2_wrapup/figs/       = Phase 2 paper figure 재사용


-----------------------------------------------------------------------------
Slide 1. Ablation 4 축 (Phase 1)
-----------------------------------------------------------------------------

텍스트

  1) Data: Horikawa 5 subjects (sub-01 ~ 05), 2,185 stimuli each
  2) Task: Level 1 - V/A binary classification
     - V binary: Valence Q4 (top 25%) vs Q1 (bottom 25%), 중간 50% 제외 → 1,131 stim
     - A binary: Arousal Q4 vs Q1 → 1,107 stim
     - Split: stimulus-stratified, 80 / 10 / 10. 같은 자극은 모든 subject 동일 split
  3) 모델 (frozen feature extractor)
     - SwiFT NewE96 (ver11, embed_dim 768, ~9.4M backbone) 우선 진행
     - 두 init 비교. resting-pretrained vs scratch
  4) Ablation 4 축
     - Padding (SL=20 input 만들 때): replicate / zero / mean
     - Head: Linear (L2 logistic) / MLP (SwiFT vendored 9.4M)
     - Pre-training 효과: Resting / Scratch
     - Subject mode (공통 신호 vs 개인별): Pooled / Per-subject

figure
  ppt_slides_figs/ablation_4axes.png
  (각 막대 = 그 축 값에서 다른 3 축 best 조건. 평균 아님. V_binary 파랑, A_binary 주황 paired)

발표 한 줄
  - Padding: zero ≈ mean > replicate. zero (V 0.688 / A 0.605), replicate (V 0.650 / A 0.573)
    → zero-padding 채택 (znorm_minback pretrain 과도 일치)
  - Head: linear > MLP. linear (V 0.688 / A 0.607), MLP (V 0.632 / A 0.584)
    → 작은 N 에서 단순 head 가 강함
  - Pre-training: resting > scratch. resting (V 0.688 / A 0.607), scratch (V 0.657 / A 0.582)
    → pretrain weight 효과 V/A 모두 +0.03 AUROC
  - Subject mode: pooled ≈ per-subject (V/A 모두 0.02 이내 차이)
  - A_binary 가 V_binary 보다 모든 축에서 0.08 ~ 0.10 낮음
    → arousal 이 valence 보다 brain frozen 으로 잡기 어려운 task
  → 어느 축도 brain frozen 천장 (~0.74) 못 뚫음. encoder 자체가 binding constraint


-----------------------------------------------------------------------------
Slide 2. Brain Foundation Model 비교 (V/A + Cat34)
-----------------------------------------------------------------------------

텍스트

  1) Data: 같은 Horikawa 5 subj × 2,185 stim
     - 각 stim 은 짧은 video clip (5 ~ 15 TR ≒ 10 ~ 30 sec 길이)
     - 같은 stim 을 5 명이 다 봄. brain response 는 subj 마다 다름

  2) Task: 6 종 (4 V/A + 2 Cat34)
     - V_binary (1,131 stim): Valence 점수의 상위 25% (Q4) vs 하위 25% (Q1) 이진 분류
       metric = AUROC. chance = 0.5
     - A_binary (1,107 stim): Arousal Q4 vs Q1 이진 분류. AUROC. chance = 0.5
     - V_reg (2,185 stim): Valence 점수 (1 ~ 5 연속값) 회귀
       metric = Pearson r. chance = 0
     - A_reg (2,185 stim): Arousal 점수 (1 ~ 5 연속값) 회귀. Pearson r. chance = 0
     - 원본 라벨 (Cowen et al. 2017 PNAS 가 만든 외부 데이터, 우리는 averaged 점수만 받아 씀)
       · 영상마다 34 개 감정 카테고리 (재미/기쁨/슬픔/놀람/분노/두려움/...) 각각에 점수 (0 ~ 1) 가 매겨져 있음
       · 점수가 클수록 그 영상이 그 감정을 더 강하게 유발
       · 예. 영상 1 → [재미 0.50, 기쁨 0.33, 놀람 0.17, 나머지 31 개 = 0]
       · 한 영상에 평균 9 카테고리가 nonzero (영상 1 개가 여러 감정 자극 가능)

     - Cat34_multilabel (2,185 stim)
       · 점수 → binary 로 변환. 점수가 0.15 이상이면 "있음 (1)", 아니면 "없음 (0)"
       · 영상 1 → [재미=1, 기쁨=1, 놀람=1, 슬픔=0, 분노=0, ...] 34-dim binary vector
       · 평균 한 영상에 4 개 카테고리가 "있음"
       · 모델 task. 뇌 신호 (또는 뇌+영상) 입력 → 34 개 yes/no 동시 예측
       · loss. sigmoid + BCE (binary cross-entropy)
       · metric. 34 카테고리 각각의 AUROC 평균 (macro AUROC). 높을수록 좋음. chance 0.5

     - Cat34_soft (2,185 stim)
       · 원본 점수 그대로 라벨. 영상 1 → [0.50, 0.33, 0.17, 0, ...] 34-dim 확률 분포
       · 모델 task. 뇌 신호 입력 → 34-dim 확률 분포 직접 예측 (각 감정의 강도까지)
       · loss. KL divergence (모델 분포와 정답 분포 사이의 거리)
       · metric. 34 카테고리 각각의 Pearson r 평균. 높을수록 좋음. chance 0
       · 보조 metric. top-1 acc (argmax 카테고리 맞히기), mean KL

     - 두 task 차이 한 줄
       · multilabel = 각 감정의 "있다 / 없다" 결정 위주
       · soft = 각 감정의 "얼마나 세게" 정량 예측

  3) 모델 3 종 (모두 frozen extractor, training 없음)
     - SwiFT NewE96 (ver11, embed_dim 768, ~9.4M backbone)    4D Swin Transformer + RoPE
     - Brain-JEPA (embed_dim 768, JEPA-style spatiotemporal masking)
     - NeuroSTORM (4D Swin-UNETR variant, embed_dim 768)

  4) 통일된 setting (Slide 1 ablation 으로 결정한 zero-padding 채택)
     - Padding = zero (3 BFM 공통)
     - Init = resting-pretrained vs scratch 둘 다 비교
     - Probe = linear (L2 logistic / Ridge) + MLP (SwiFT 9.4M) 둘 다
     - Mode = pooled + per-subject 둘 다
     - 5-fold stim-stratified CV
     - 각 BFM × task 의 "최강 조건" (head + mode + init 조합) 만 추려서 비교

figure (두 장 좌우 배치)
  좌. ppt_slides_figs/bfm_comparison.png       (4 V/A task)
  우. ppt_slides_figs/bfm_cat34.png            (Cat34 multilabel + soft)

발표 한 줄
  - V/A: NeuroSTORM 가 V_binary (0.729) 미세 우위, Brain-JEPA 가 V_reg (0.304), A_reg (0.207) 우위
  - Cat34: Brain-JEPA 가 두 task 모두 1 위 (multilabel 0.679, soft 0.237)
  - 3 BFM 차이 0.05 이내. ablation 4 축 효과 (Slide 1) 와 비슷한 크기
  → brain frozen 천장. V_binary ~0.74, Cat34 multilabel ~0.68. BFM 종류 바꿔도 그 이상 못 올림


-----------------------------------------------------------------------------
Slide 3. Video Foundation Model 예측 성능
-----------------------------------------------------------------------------

텍스트

  1) Data: 같은 Horikawa 2,185 stim (video clip)
  2) Task: 같은 4 V/A task
  3) Video encoder 5 종 (모두 frozen, pretrained, 학습 없음)
     - CLIP ViT-L/14
       · 영상의 frame 들을 sampling 해서 ViT 통과 → frame embedding 평균 → 768-dim feature
       · pretrain. 4억 (image, caption) pair 의 contrastive learning (영상-텍스트 정렬)

     - DINOv2 giant
       · 같은 방식 (frame 통과 → embedding 평균) → 1536-dim feature
       · pretrain. self-distillation. label 없이 image 자체에서 학습

     - V-JEPA2 ViT-G/64
       · 영상을 64 frame clip 단위로 통과 → 비디오 embedding → 1408-dim feature
       · pretrain. JEPA (Joint Embedding Predictive Architecture, masked target prediction)

     - VideoMAE-v2 giant
       · 같은 방식 → 1408-dim feature
       · pretrain. masked video autoencoder (마스킹된 cube 재구성)

     - Qwen-VL caption + text embedding
       · Step 1. 각 영상을 Qwen-VL (vision-language model) 에 넣음
       · Step 2. Qwen-VL 이 영상을 보고 자연어 caption 생성
         (예. "A man is laughing while playing with a dog in a park.")
       · Step 3. 생성된 caption text 를 sentence transformer (all-mpnet-base-v2) 에 넣어
         text embedding 추출 → 768-dim feature
       · 즉 "영상 → 자연어 → text embedding" 우회 경로. CLIP 처럼 직접 영상 encode 가 아님

  4) Probe (Phase 1 의 공통 setting)
     - linear (L2 logistic / Ridge) + MLP (SwiFT vendored 9.4M) 둘 다
     - 5-fold stim-stratified CV
     - per-subject 없음 (video feature 는 subj 무관, 영상마다 1 개)

figure
  ppt_slides_figs/video_comparison.png

발표 한 줄
  - CLIP 단독이 모든 task 최강. V_binary 0.971, A_binary 0.800, V_reg 0.764, A_reg 0.423
  - 영상-텍스트 정렬된 모델 (CLIP, Qwen-VL caption) > 영상 only SSL (V-JEPA2, VideoMAE)
  → brain frozen 천장 (~0.74) vs video frozen 천장 (CLIP ~0.97). gap 약 0.23 AUROC


-----------------------------------------------------------------------------
Slide 4. 학습 방식 (Phase 2) - V/A
-----------------------------------------------------------------------------

텍스트

  1) Data: 같은 Horikawa. 같은 5-fold CV. 같은 4 V/A task (V_binary, A_binary, V_reg, A_reg).

  2) Frozen feature 고정 (Phase 1 최강 조합 둘 다 사용. 둘 다 학습 안 함)
     - brain feature: Brain-JEPA, resting-pretrained, zero padding
       · 각 (subj, stim) 마다 768-dim vector
     - video feature: CLIP ViT-L/14 pretrained
       · 각 stim 마다 768-dim vector (subj 무관, 영상 하나에 1 vector)
     - 이 두 feature 를 input 으로 받고, 위에 작은 학습 layer 만 얹는 방식

  3) Phase 1 이 답하지 못한 두 질문
     Q1. brain feature 만 input 으로 받을 때, 학습 방식을 똑똑하게 하면 0.74 천장 뚫리나?
         → brain-only 4 종 (I, II, III, IV) 로 답
     Q2. brain + video 같이 input 으로 받으면 video 단독 (CLIP 0.97) 동급은 유지되나?
         → joint 4 종 (A, B, C, D) 로 답

  4) 학습 방식 8 종 (오직 이것만 변화. brain 도 video 도 안 건드림)

     Joint 4 종 (inference 때도 brain + video 둘 다 input)

       A. Token attention (transformer 기반)
          · brain vector + video vector 를 2 개 token 으로 transformer encoder 에 입력
          · [CLS] 토큰을 앞에 붙임. transformer 2 layer 통과 후 [CLS] 만 뽑아 readout
          · 학습 가능. 두 input 의 projection layer + transformer + CLS embedding + linear head
          · 직관. brain ↔ video 사이의 비선형 상호작용까지 학습

       B. Cross attention (양방향 attention)
          · brain 이 video 를 "보고" update, video 가 brain 을 "보고" update (양방향 cross-attention)
          · 두 update 된 vector 를 concat → linear readout
          · 학습 가능. Q/K/V projection + attention + linear head
          · 직관. brain 쪽 representation 을 video 정보로 보강

       C. Contrastive alignment (CLIP 스타일)
          · Step 1. brain projection + video projection 을 InfoNCE loss 로 같은 공간에 정렬
                    같은 stim 의 (brain, video) pair = positive, 다른 stim = negative
                    이 단계에선 V/A label 안 씀. label-free
          · Step 2. 정렬된 후 그 위에 linear probe 박아 V/A 예측
          · 두 가지 readout 보고
            - joint readout. brain projection + video projection concat 한 위
            - brain-only readout. brain projection 만 (video 빼고)
          · 직관. brain 과 video 를 같은 의미 공간으로 모은 다음 그 위에서 task 풀기

       D. Late linear fusion (가장 단순)
          · brain vector 와 video vector 를 concat 한 다음 sklearn LogisticRegression / Ridge
          · 학습 가능. closed-form linear classifier 만 (transformer 같은 거 없음)
          · 직관. 가장 단순한 fusion baseline. 이걸 다른 fusion 들이 이겨야 의미 있음

     Brain-only 4 종 (inference 때 brain 만 input. video 는 학습 신호로만 사용)

       I. Supervised MLP
          · brain vector → 2-layer MLP → V/A 예측
          · 학습 신호. V/A 정답 라벨만
          · 가장 단순한 brain-only 학습. 다른 brain-only 방식들이 이걸 이겨야 의미 있음

       II. Distillation (지식 증류)
          · "선생님 모델" 만들고, "학생 모델 (brain MLP)" 이 선생님을 흉내내게 학습
          · 선생님 = CLIP video feature 로 학습한 classifier (V/A prediction)
          · 학생 = brain MLP. 학생은 brain 만 입력으로 받지만 학습 시 선생님의 예측 분포를 KL loss 로 따라하기
          · loss = 0.5 × (V/A 정답 cross-entropy) + 0.5 × (선생님과 KL divergence, T=4)
          · 직관. video 가 잘 푸는 걸 brain 한테 간접적으로 가르치기

       III. Multitask (두 task 동시 학습)
          · brain vector → shared backbone → 2 개 head
            - V/A head. V/A 정답 예측
            - video reconstruction head. CLIP video feature 그 자체 재구성 시도
          · loss = (V/A loss) + 0.3 × (video reconstruction MSE)
          · 직관. brain representation 이 video 도 만들어낼 수 있게 압박 → video-aware brain encoding 학습

       IV. Subject-aware
          · brain vector 옆에 "이 데이터가 sub-01 거냐 sub-05 거냐" subject ID 를 16-dim learnable embedding 으로 만들어 concat
          · concat 된 (brain + subject embedding) → 2-layer MLP → V/A
          · 학습 신호. V/A 정답 + subject embedding 자체도 함께 학습됨
          · 직관. 5 명의 brain response 분포가 다르니 개인차를 명시적으로 condition

figure
  reports/phase2_wrapup/figs/method_heatmap.png   (9 method × 4 V/A task, 위 4 = joint, 아래 5 = brain-only)

발표 한 줄 (Q1 / Q2 답)
  Q1 답. brain-only 4 종 V_binary 0.717 ~ 0.724 로 다 비슷. 방식 차이 0.01 이내
         → 어떤 학습 방식 (distillation, multitask, subject-aware) 도 supervised baseline 보다 의미있게 안 나음
         → Phase 1 frozen probe 천장 (~0.74) 못 뚫음

  Q2 답. joint 4 종 다 video frozen 천장 (CLIP V_binary 0.971) 회복
         · binary 최강. D late fusion (V_binary 0.972, A_binary 0.802)
         · regression 최강. A token attention (V_reg 0.763, A_reg 0.424)
         → fusion 종류는 task 따라 다름. binary 는 단순 concat 만으로 충분, regression 은 attention 필요

  추가 관찰. C contrastive 의 brain branch 만 따로 보면 (joint 안 쓰고 brain projection 만)
         brain-only 4 종 (0.72) 보다 더 낮음 (0.71). V_reg 에서 -0.03 r
         → InfoNCE alignment 가 brain side 의 emotion 정보 일부 깎음 (shared structure 만 살아남는 현상)


-----------------------------------------------------------------------------
Slide 5. BrainVLM 구조 (Phase 3)
-----------------------------------------------------------------------------

텍스트

  1) Data
     - 같은 Horikawa fold 1 만 사용 (Phase 1/2 의 5-fold CV 와 동일한 fold 분할)
     - 분할
       · train. 3 fold (~60%) = 1,311 stim/subj × 5 subj = 6,555 sample
       · val.   1 fold (~20%) = 437 stim/subj × 5 subj = 2,185 sample (현재 학습에선 안 씀, upstream eval 버그 회피로 skip)
       · test.  1 fold (~20%) = 437 stim/subj × 5 subj = 2,185 sample (inference 평가용)
     - 한 sample = (한 명 subject, 한 영상)
       · 입력 fMRI volume. shape (1, 1, 96, 96, 96, 20) = (batch, channel, D, H, W, T)
         · 공간 96^3 (74×91×81 원본 + zero padding)
         · 시간 20 frame (stim 당 5~15 frame + zero padding)
       · 정답 라벨. Cowen 의 V/A 점수 (V_reg, A_reg 와 동일)
     - 한 fold 만 한 이유. fold 당 학습이 ~3.7 hour 라 5-fold 다 돌리면 ~18 hour. 일단 fold 1 만 보고 5-fold 확장은 다음

  2) Task: V/A regression. 출력 형식 = autoregressive XML
     - 입력. fMRI volume + prompt ("predict valence/arousal from this fMRI")
     - 출력. <Emotion_Analysis><Valence>2.22</Valence><Arousal>5.56</Arousal></Emotion_Analysis>
     - Loss. causal LM (assistant turn 의 token 에만 적용)

  3) Backbone (모두 frozen, ~2.2B 파라미터, 학습 안 함)
     - Qwen3-VL-2B-Instruct (HuggingFace 공개 weight)
       · Vision Tower (ViT, 700M)
       · LLM (1.5B)

  4) Trainable (~42M, Qwen3-VL 의 2%)
     - PatchEmbedQwen.fMRI (~30M)
       · tri-planar patch (16, 16, 16, 5) → vision token sequence (N, 1152)
     - CustomNoPoolingTriPlanarMerger (~12M)
       · vision 1152 → LLM 2048 projection (pool 안 함, spatial info 보존)

figure
  ppt_slides_figs/brainvlm_architecture.png

발표 한 줄
  - Phase 1 / 2 는 brain encoder frozen. 천장 거기서 결정
  - Phase 3 는 brain encoder 의 일부 (PatchEmbedQwen + Merger) 까지 학습
  - frozen feature 의 한계를 뚫을 가능성 있음


-----------------------------------------------------------------------------
Slide 6. BrainVLM 학습 결과 (NEW)
-----------------------------------------------------------------------------

텍스트

  1) Setup: fold 1, 3 epoch, batch 1 × grad accum 8 (effective batch 8)
     LR 3e-4, AdamW, bf16, gradient checkpointing
     6,555 sample × 3 epoch = 2,460 step. 총 3.7 시간 (1 GPU)
  2) 학습 loss
     start 1.94 (epoch 0.01) → end 0.151 (epoch 3.0)
     epoch 0.1 부근에서 빠르게 plateau. 이후 정체
     → 모델이 V/A XML 출력 format 은 빨리 학습, V/A 값 매핑은 천천히
  3) 생성 sample (test set 의 한 stim)
     GT: <Valence>1.22</Valence><Arousal>6.22</Arousal>
     PD: <Valence>6.82</Valence><Arousal>5.12</Arousal>
     → 형식 학습 완료, 숫자 예측은 large error (V 5 point off)
  4) 다음 단계
     - test fold 전체에서 generate → V/A regression 측정 (TBD)
     - Phase 2 best joint (A token attention. V_reg 0.763, A_reg 0.424) 와 비교
     - 5-fold 확장. 현재 fold 1 만

figure
  ppt_slides_figs/brainvlm_loss_curve.png

발표 한 줄
  - 학습 자체는 수렴 (loss 1.94 → 0.15)
  - XML 형식은 학습됨. V/A 값 정확도는 inference 평가 후 확정
  - fold 1 만 끝났음. 5-fold 확장 + Phase 2 best 와 비교가 다음


-----------------------------------------------------------------------------
부록. figure 한 눈
-----------------------------------------------------------------------------

Slide 1  ppt_slides_figs/ablation_4axes.png            Phase 1 ablation 4 축
Slide 2  ppt_slides_figs/bfm_comparison.png            3 BFM × 4 V/A task
         ppt_slides_figs/bfm_cat34.png                  3 BFM × 2 Cat34 task
Slide 3  ppt_slides_figs/video_comparison.png          5 video × 4 V/A task
Slide 4  reports/phase2_wrapup/figs/method_heatmap.png  Phase 2 9 method × 4 V/A task
Slide 5  ppt_slides_figs/brainvlm_architecture.png     BrainVLM dataflow
Slide 6  ppt_slides_figs/brainvlm_loss_curve.png       BrainVLM training loss


-----------------------------------------------------------------------------
한 페이지 takeaway (마지막에 박을 수도)
-----------------------------------------------------------------------------

Phase 1
  brain frozen 천장 V_binary 0.74 / Cat34 multilabel 0.68
  video CLIP frozen 천장 V_binary 0.97 / V_reg 0.76
  BFM 종류 / padding / head / mode 어느 ablation 축도 brain 천장 못 뚫음

Phase 2 (V/A + Cat34 둘 다)
  brain-only 4 종 다 brain 천장 근방 (방식 차이 없음)
  joint 4 종 다 video 천장 회복
  contrastive brain branch 가 emotion 정보 손실 (V/A, Cat34 둘 다 재현)

Phase 3
  BrainVLM fold 1 3 epoch 학습 완료 (loss 1.94 → 0.15)
  V/A inference + 5-fold 확장이 다음
