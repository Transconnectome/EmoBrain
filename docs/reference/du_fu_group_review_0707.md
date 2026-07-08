# Du / Fu / He 그룹 (CAS) 논문 review (2026-07-07, PDF 원문 확인 2026-07-07)

Changde Du, Kaicheng Fu, Zhongyu Huang, Huiguang He 등 Institute of Automation, Chinese Academy of Sciences 그룹 이 **우리 와 같은 Horikawa 2020 정서 영상 fMRI** 를 쓴 선행 연구 군. EmoBrain 의 가장 직접적 경쟁/선행 이므로 정식 정리. 1차 web 조사 (2026-07-07, 6 parallel agent) 후, **4편 (GED MICCAI, GED TMI, ML-BVAE, EmoGrowth) 은 PDF 원문 으로 재확인** (`docs/reference/papers/Du1-4.pdf`). iScience / Information Fusion / TAFFC 3편 은 아직 web 기반.

**PDF 확인 후 web 조사 대비 정정 (중요).**
1. **GED metric = MAE 만. Pearson 아님.** 1차 web 조사 가 "MAE + Pearson" 이라 했으나 오류. GED (MICCAI Eq.3, TMI Eq.3) 는 **MAE (34 감정 합산, stimulus 평균) 단일 metric**. Pearson 은 논문 전체 에 없음.
2. **GED stimulus = 2196 (dedup 안 함).** MICCAI 는 이를 "2181 unique + 15 duplicate" 라 서술 했으나 **이 서술 은 Horikawa 원본 과 불일치**. Horikawa 배포 label (`categcontinuous.mat`, 2026-07-07 실측) = 2196 presentation 중 **2185 unique + 정확히 11 repeat** (presentation 2185~2195 = 0~10 재제시). 우리 2185 canonical 이 Horikawa 원본 과 정확히 일치. Du 는 어차피 2196 전체 를 dedup 없이 학습 하므로 "unique" 서술 은 파이프라인 에 무관.
3. **GED target = 우리 와 동일 (crowd proportion 0-1).** rater 가 binary yes/no, 평균 내 [0,1]. TMI 의 "binarized 0/1" 서술 은 MICCAI 가 "averaged, ranging 0-1" 로 해소. → **GED 는 우리 와 같은 target·같은 metric(MAE) 으로 비교 가능** (우리 도 MAE 를 34 합산 방식 으로 계산 하면 직접 대조).
4. **ML-BVAE / EmoGrowth 숫자 web 조사 값 과 일치** (miF1 0.505, mAP 0.448 / Brain27 mAP 44.2, oracle ERG r=0.86). EmoGrowth 차용 3항목 (arctanh Eq.12, affective-dim RSM teacher, oracle ERG Pearson) PDF 로 확정.

**핵심 결론 먼저.**
- 이 그룹 이 Horikawa 5-subject 데이터 로 fine-grained emotion decoding 을 여러 번 발표. **우리 가 "새 데이터/새 task" 를 하는 게 아니라, 이들 이 이미 개척한 데이터 위 에서 새 framework (multi-modal LLM + brain-only distillation + universal pooling) 를 얹는 것.** Related work 에서 이들 을 정면 으로 다뤄야 함.
- **직접 숫자 비교 가능한 논문 은 GED (TMI 2023 / MICCAI 2022) 하나** — 우리 와 같은 34D continuous regression, **같은 target (0-1 proportion), MAE metric**. 우리 도 MAE 를 34-합산 방식 으로 계산 하면 GED 표 와 직접 대조 가능. 나머지 는 binarize 분류 (F1/mAP) 라 숫자 비교 불가.
- **우리 차별점.** (1) subject-pooled universal code (그들 은 전부 per-subject), (2) multi-modal LLM fusion (그들 은 brain-only 또는 brain→model 단방향), (3) 34D independent regression + CCC metric, (4) teacher-student distillation 비대칭.

---

## 1. GED — Graph Emotion Decoding (MICCAI 2022 → TMI 2023) ★ 가장 직접 비교

**MICCAI 2022 (origin).** Huang, Du, Wang, He. "Graph Emotion Decoding from Visually Evoked Neural Responses." LNCS 13438, pp. 396-405. DOI 10.1007/978-3-031-16452-1_38. Code https://github.com/zhongyu1998/GED.

**TMI 2023 (journal extension).** Huang, Du, Wang, **Fu**, He. "Graph-Enhanced Emotion Neural Decoding." IEEE TMI 42(8):2262-2273. DOI 10.1109/TMI.2023.3246220. PMID 37027550. (Kaicheng Fu 추가, baseline 확장, "generalizes emotion graphs and brain networks" 이론 framing.)

- **데이터 (PDF 확인).** Horikawa (Dataset 1) 5 subject, **2196 presentation 을 dedup 없이 그대로** (MICCAI 는 "2181 unique + 15 dup" 라 서술 하나 원본 실측 = 2185 unique + 11 repeat, 그들 서술 부정확), **34 category continuous** (Appendix A 목록 = 우리 cowen34_order 와 동일 순서), **370 brain region = 360 HCP cortical + 10 subcortical**. Per-subject **10-fold CV (1976 train / 220 test per fold)**. (별도 Dataset 2 = Koide-Majima, 80 emotion, Horikawa 아님.)
- **Target (PDF 확인).** rater binary yes/no → 평균 [0,1] proportion. **우리 crowd-proportion target 과 동일.**
- **Task.** 34D emotion-score vector regression. Binarize 안 함. **우리 와 정확히 같은 setting.**
- **Metric (PDF 확인, 정정).** **MAE 만** (Eq.3). 감정 34개 **합산** (평균 아님, "most scores are zeros → sum operation 사용"), stimulus 평균. **Pearson 없음** (web 조사 오류 정정).
- **Exact 숫자 (PDF 확인).**
  - Within-subject (subject 1-5): FNN 2.05-2.08 / GCN ~1.82 / BrainNetCNN 1.72-1.74 / BrainGNN 1.68-1.69 / **GED-4 1.643-1.674 / GED-5(TMI best) 1.641-1.671**.
  - Cross-subject LOSO (TMI Table III, Dataset 1): FNN 2.384 / GCN 1.826 / BrainNetCNN 1.762 / BrainGNN 1.727 / **GED 1.689±0.015**.
  - GED 는 cross-subject 도 함 (edge-filtering 으로 subject-specific edge 제거). 우리 LOSO 와 개념 대응.
- **방법.** Emotion-brain **bipartite graph** (노드 = 감정 34 + ROI 370, 엣지 = 감정별 top-활성 ROI voting 연결, 5-layer MEAN-aggregator GNN embedding propagation, sigmoid 출력, MSE loss). 감정 embedding 과 ROI embedding 이 서로 refine. Baseline (FNN, GCN, GIN, BrainNetCNN, BrainGNN) 다 이김. TMI Theorem 1 = bipartite graph 가 emotion graph + brain network 를 generalize.
- **우리 와 관계.**
  - **우리 brain ridge (raw MAE 0.054 × 34 ≈ 1.84 합산 환산) 의 nearest external anchor.** GED-4 (1.64) < 우리 pooled ridge (~1.84) ≈ GCN (1.82). 단 그들 per-subject 10-fold, 우리 pooled + 다른 split. **직접 대조 하려면 우리 예측 에 GED 식 MAE (sum-over-34, raw target) 를 재계산 해야 함** (target·metric 동일 하므로 가능).
  - **그들 graph 는 bipartite (emotion×ROI), 우리 structure loss 는 emotion-emotion (34×34).** 그들 주장 = "emotion-only graph 는 부족, emotion↔ROI 함께 모델링 하면 더 낫다". 우리 34×34 는 그들 framing 에서 emotion-side projection (특수 case).
  - **Relation prior 가 decoding 을 돕는다는 존재 증명** (같은 데이터 에서 GED-2 이상 이 FNN/GCN/brain-network baseline 다 이김, layer 늘릴수록 개선 GED-5 까지). → 우리 structure loss 를 default OFF 로 두는 게 맞나 재고 근거. 더 나아가려면 bipartite emotion×ROI graph 가 principled upgrade.

## 2. ML-BVAE — Multi-view Multi-label Fine-grained Emotion Decoding (TNNLS 2022)

Fu, Du, Wang, He. IEEE TNNLS. arXiv 2211.02629. Code https://github.com/KaichengFu1997/ML-BVAE. (PDF 원문 확인.)

- **데이터 (PDF 확인).** **MEMO27 = Horikawa 5 subject** (figshare 11988351 = Horikawa 2020). 2196 instance, 115070 voxel, **HCP360 (360 ROI)**, ROI-pooling (ROI 를 sub-cuboid 로 나눠 평균). Cowen 34 rating 중 **27 선택 (Cowen 2017 기준) + 0.1 threshold binarize** → multi-label. Label = voting ratio (crowd proportion) 를 threshold. (별도 MEMO80 = Koide-Majima audiovisual, 8 subject, 5400 sample, 80 emotion, Destrieux 148 ROI, Horikawa 아님.)
- **Task.** **Multi-label binary 분류** (continuous 를 binarize). 우리 continuous regression 과 근본 다름.
- **Metric (PDF 확인, 5-subject avg).** OneE 0.302 / RL 0.186 / **miF1 0.505 / maF1 0.398** / e-AP 0.619 / **mAP 0.448**. **Pearson/CCC 없음.** 비교군 = LR (Horikawa 식 per-emotion 선형회귀 binarize, **mAP 0.246**) / Benchmark MLP 0.434 / ML-GCN 0.422 / CA2E / SIMM / GARDIS. ML-BVAE 가 primary metric (miF1/maF1/mAP) 에서 전부 1위.
- **방법.** Multi-view VAE (좌뇌 / 우뇌 / L−R 3 view, product-of-experts Gaussian 융합) + label-aware module (label 별 emotion-specific representation) + **masked self-attention (emotion co-occurrence mask, A_jk = N_jk/N_j)** + asymmetric focal loss. Per-subject 10-fold.
- **우리 와 관계.**
  - **숫자 비교 불가** (F1/mAP vs MAE/Pearson, 27 vs 34, binarize vs continuous).
  - **가장 강한 fine-grained decoding 선행 on Horikawa** — 우리 regression-vs-그들 classification 구분, 그리고 우리 는 27 축소 안 하고 **34 전체 continuous** 를 contribution 으로 명시. (그들 LR baseline mAP 0.246 → 우리 대비 Horikawa 선형 baseline 이 얼마나 약한지 실증.)
  - **그들 은 co-occurrence (masked self-attention) 로 감정 관계 모델링.** 우리 independent MSE 는 관계 안 씀 → reviewer 가 "왜 co-occurrence 안 쓰냐" 물을 것. 우리 structure loss (optional) 로 방어 준비.
  - Borrowable. Hemispheric view (L/R/L−R, product-of-experts) 는 저비용 brain-side ablation. Bi-hemisphere ablation 이 miF1/maF1 개선 을 실증 (그들 Fig.10).

## 3. EmoGrowth — Incremental Multi-label Emotion Decoding (ICML 2025)

Fu, Du, Peng, Wang, Zhao, Chen, He. PMLR v267 (ICML 2025). arXiv 2405.20600 (구 제목 "Multi-label Class Incremental Emotion Decoding with Augmented Emotional Semantics Learning", 방법명 = AESL). Code https://github.com/ChangdeDu/EmoGrowth. (PDF 원문 확인.)

- **데이터 (PDF 확인).** **Brain27 = Horikawa 5 subject**, 2196 clip, **27 category + 14 affective dimension** (Approach/Arousal/Valence 등), 0.1 threshold binarize. Feature = **2880-dim ROI-pooling (360 HCP ROI × 8 sub-volume)**. Per-subject train 1800 / test 396. (별도 Video27 = Cowen 2017 원본 영상 VGG19 feature, Audio28 = Cowen 2020 음악 MFCC+ResNet18, 둘 다 Horikawa 아님.)
- **Task.** **Incremental (class-incremental) multi-label 분류** (protocol B0-I9 / B0-I3 / B15-I3 / B15-I2, 감정 을 알파벳 순 으로 순차 추가). Continual learning. 우리 static 34D regression 과 안 맞음.
- **Metric (PDF 확인).** mAP (primary) / maF1 / miF1. Brain27 subject1 AESL Avg mAP **44.2 / 43.8 / 41.9 / 39.5** (4 protocol). "9.6% relative mAP 개선 vs 2위 (AGCN/KRT-R)". 5 subject 다 유사.
- **방법.** Augmented Emotional Relation Graph (ERG). 노드 = emotion, 엣지 = conditional co-occurrence **A_ij = P(ℓi|ℓj) = N_ij/N_j**. Graph autoencoder (**GIN** encoder + pairwise decoder) + graph-based label disambiguation (label propagation β=0.95) + **affective-dimension RSM distillation (RKD, two teacher = old model + affective space)**.
- **우리 와 관계.**
  - Continual 기계장치 (soft-label disambiguation, anti-forgetting, past/future-missing partial label) 는 우리 problem 아님. Import 안 함.
  - **structure loss 에 직접 borrowable 3개 (PDF 확정).** (a) **arctanh reparameterization (Eq. 12)** — RSM correlation 을 MSE match 전 `arctanh` 변환 해 (−1,1)→(−∞,∞) Gaussian 화. 우리 34×34 loss 에 바로 사용. (b) **affective-dimension RSM as second teacher (RKD)** — Horikawa 14 affective dim 을 같은 자극 에 갖고 있으니 저비용 auxiliary teacher. 모델 feature RSM 을 affective-dim RSM 에 정렬. (c) **oracle-vs-learned ERG Pearson (RKD 있을 때 r=0.86 vs 없을 때 r=0.75)** — 우리 학습된 34×34 구조 가 ground-truth co-occurrence 복원 하는지 검증 template.
  - **우리 NV0 (LLM decoder) 에 중요한 negative result (PDF).** EmoGrowth ablation 에서 **LLaMA 3.1-8B sentence embedding 을 emotion label embedding 으로 쓴 게 오히려 학습된 embedding 보다 나빴음** ("+SE" variant 가 base 보다 mAP 하락). 그들 해석 = "embedding 품질 만 아니라 semantic-guided decoupling 의 구조적 정렬 이 핵심". → 우리 가 LLM 을 단순 label/text encoder 로 naive 하게 붙이면 안 된다는 경고. LLM 은 fusion·decoding 구조 안 에서 써야 함 (우리 framework 방향 과 정합, 단 naive text-embedding 은 피할 것).

## 4. iScience 2023 — Topographic Representation (encoding, 표상 연구)

Du, Fu (공동 1저자), Wen, He. iScience 26(9):107571. DOI 10.1016/j.isci.2023.107571. OSF https://osf.io/9uyn2/. (Open access PMC10470388.)

- **데이터.** Horikawa 5 subject, 2196 video, **34 category** + 14 dimension. 우리 와 동일.
- **Goal.** Encoding-direction 표상/topography 연구 (decoding accuracy 아님). Locationism vs constructionism 판정.
- **방법.** Voxel-wise encoding (34 emotion rating → brain), banded ridge (motion-energy vs semantic vs emotion 분리), group encoding weight PCA → 4 PC, cortical topographic map, RSA.
- **핵심 발견 (우리 에 강력 citable).**
  - **Distributed, not localized.** 전체 cortex 21% significant, locationism 기각. 우리 "emotion is high-dimensional + distributed" 근거.
  - **ROI 우선순위.** 감정 신호 최강 = TPJ (~62% significant voxel), IPL (~50%), lateral-occipital LO (51-67%), precuneus/DMPFC/DLPFC. V1 최저. → 우리 modular encoder 가 temporoparietal+prefrontal up-weight 근거.
  - **Feature dissociation.** occipital/higher-visual = semantic-dominant, temporoparietal+prefrontal = emotion-dominant.
  - **Behavioral-brain dissociation (우리 sub-question d).** Neural affective space cross-subject consistency 0.56 vs behavioral 0.20-0.25. 둘 안 맞음 (valence 가 brain 에서 approach 로 붕괴). 우리 decode≠structure + EmoMind dissociation 과 수렴.
  - **Valence 는 primary neural axis 아님** (approach 와 collinear r≈0.9). Citable.
- **주의.** Encoding-only, per-emotion decoding accuracy 없음. 우리 per-emotion Pearson (0.09-0.47) 과 직접 숫자 비교 불가. Regional significant-voxel % 로 인용.

## 5. Information Fusion 2025 — Hierarchical Emotional Areas (Horikawa 아님)

Huang, Du, Li, Fu, He. Information Fusion (Elsevier) 2025. arXiv 2408.00525. PII S1566253524003919. (DOI 10.1016/j.inffus.2024.102613 는 미확인, 인용 전 재확인.)

- **데이터.** **Horikawa 아님.** StudyForrest (Forrest Gump 영화, 15 subject, 6 basic emotion) + Vimeo (8 subject, 80 emotion). Power atlas 264 ROI. 사용자 추측 (같은 정서 fMRI) 은 틀림.
- **Goal.** Functional-connectivity 트리 의 정보전파 깊이 로 hierarchical emotional area 식별.
- **방법.** Brain tree (FC spanning tree) → node influence (random walk) → longest shortest path 반복 추출 로 level 분해 → HEmoN (LSTM per level). Metric = MAE.
- **핵심 발견.** 3-level 위계. Level 1 = emotion perception (sensory/visual/auditory/DMN), Level 2 = basic psychological operations (+ Broca/Wernicke, 언어), Level 3 = cognitive integration. Psychological constructionist (Barrett/Lindquist) 지지. Distributed + hierarchical.
- **우리 와 관계.**
  - "감정 은 distributed + hierarchical (sensory→psychological→cognitive)" 근거. 우리 modular encoder + sensory→semantic 위계 동기 에 인용 가능.
  - **주의 (중요).** (a) **visual system 이 Level 1/2/3 모두 재등장** → "visual = 저차 전용" 단순 서사 를 오히려 완화. 우리 ISC (visual 높음) 인용 시 "visual 저차 주도 하나 상위 통합 재참여" 로 정확히. (b) 그들 위계 (FC 트리 깊이) ≠ 우리 ISC (cross-subject 신뢰도) ≠ 우리 sub-question (CK34 decoding 보존). "분산·위계 상위 명제 에서 수렴" 수준 으로만 인용. (c) Power 264 → 14 system 이라 fine visual 하위 gradient 없음. 우리 ROI-level encoder 가 더 세밀 (차별점).
  - iScience 2023 의 hierarchy follow-up 격 이지만 **데이터 가 다름** (iScience = Horikawa, Info Fusion = StudyForrest). 자매 논문 이나 substrate 구분 필수.

## 6. TAFFC 2023/2024 — CNN-Brain Alignment (우리 CCN 라인)

Fu, Du, Wang, He. IEEE TAFFC 15(3):1026-1040 (online 2023). DOI 10.1109/TAFFC.2023.3316173. Code https://osf.io/ucx57.

- **데이터.** Brain = Horikawa 5 subject (code path `iScience`, RSA tensor [5, batch, batch] 확인). Video task = VideoEmotion-8 (1101 video, 8 cat) + Ekman-6 (~1637 video, 6 cat). Brain 과 video task 는 별개 자극.
- **Goal.** Brain RSM 을 video CNN 에 inductive bias 로 주입 (**brain → CNN 단방향**). 추론 시 fMRI 불필요.
- **방법.** RSA auxiliary loss. Brain RSM (voxel Gram, banded ridge voxel selection) vs CNN RSM (multi-layer softmax-weighted, learnable gamma). Fisher-z (atanh) matching. Total = CE + α·RSA (α=25). Lightweight 3D CNN (SqueezeNet/ResNet/ShuffleNet/MobileNet, Kinetics pretrain, VAANet 기반).
- **Result.** Brain-alignment 가 모든 architecture + 양 benchmark 에서 개선 (SOTA among comparable). Secondary snippet 상 VE8 ~50.6%, EK6 ~51.8% (미확인). Exact table paywall.
- **우리 와 관계 (CCN 라인 과 가장 가까움).**
  - **같은 alignment target** (video model ↔ brain emotion RSM). 우리 SigLIP video-brain alignment 와 같은 shape. Borrowable = learnable per-layer RSM weight (softmax gamma) + Fisher-z matching + banded ridge voxel selection.
  - **방향 반대.** 그들 = brain 을 model 에 주입 (brain teacher, CNN student). 우리 distillation = context 를 brain-only student 에 주입 (context teacher, brain student). Teacher/student 역할 swap.
  - **Tension 해소.** "brain improves lightweight CNN" (그들) vs "strong CLIP out-predicts brain 0.60 vs 0.30" (우리 B2) 는 model capacity regime 이 달라 모순 아님. 그들 은 SqueezeNet 급, 우리 는 CLIP/SigLIP 급. 즉 "brain 이 약한 model 은 돕지만, 강한 VLM 은 이미 brain 을 앞선다" 로 정합.
  - Foil value. "brain-regularizes-model" (그들) vs "model-out-predicts-brain / distill-context-into-brain" (우리) 를 같은 Horikawa 데이터 에서 대비. CCN related-work 에 명시.

---

## 7. 종합. 우리 positioning

**같은 데이터 (Horikawa 5-subject CK34) 를 쓴 논문 6편 (Info Fusion 제외 시 5편).** 이 그룹 이 이 데이터 의 fine-grained emotion decoding 을 사실상 개척. 우리 는 그 위 에서 3 가지 새 축.

| 축 | Du/Fu 그룹 | EmoBrain (우리) |
|----|-----------|-----------------|
| Subject | 전부 per-subject | **pooled universal code** |
| Modality | brain-only (GED, ML-BVAE) 또는 brain→model (TAFFC) | **multi-modal LLM (brain+video+caption teacher, brain-only student)** |
| Task/output | binarize 분류 (F1/mAP) 또는 34D regression (GED) | **34D independent regression + CCC** |
| Emotion 관계 | graph (bipartite emotion×ROI, co-occurrence) | independent MSE + optional 34×34 structure loss |
| 학습 구조 | 단일 model | **teacher-student distillation 비대칭** |

**Related work 에서 반드시.**
1. GED (TMI 2023) 를 nearest continuous-regression baseline 으로 인용 + **MAE 비교** (Pearson 아님. 우리 MAE 를 GED 식 34-합산 으로 재계산 하면 직접 대조 GED-4 1.64 vs 우리 pooled ~1.84).
2. ML-BVAE (TNNLS 2022) 를 fine-grained decoding 선행 으로, 우리 regression-vs-classification + 27→34 확장 구분. (LR baseline mAP 0.246 = Horikawa 선형 이 약함을 그들 이 이미 실증.)
3. iScience 2023 을 ROI 우선순위 + high-D distributed + dissociation 근거 로.
4. TAFFC 2023 을 CCN alignment 라인 의 방향-반대 foil 로.
5. EmoGrowth (ICML 2025) 의 arctanh + affective-dim RSM 을 structure loss 에 차용 검토. + LLM naive label-embedding 실패 를 우리 NV0 설계 경고 로.

**Reviewer 예상 질문 대비.**
- "이 그룹 이 이미 Horikawa 로 decoding 했는데 novelty?" → multi-modal LLM + pooled universal + distillation 비대칭. Encoder 순위 가 아니라 framework.
- "왜 emotion co-occurrence/graph 안 쓰냐?" → structure loss (optional) 로 준비, GED bipartite 는 future upgrade.
- "GED 대비 우리 얼마?" → GED metric = MAE (Pearson 아님). 우리 예측 에 GED 식 MAE (sum-over-34, raw 0-1 target) 를 재계산 해 대조. per-subject(GED) vs pooled(우리) + split 차이 명시. 우리 headline (Pearson/CCC) 는 GED 가 안 보고 한 축 이라 오히려 complementary.

**미확인 (인용 전 확인 필요).**
- **확정됨 (PDF).** GED MAE 표 (within 1.64 / LOSO 1.689), ML-BVAE table (mAP 0.448 등), EmoGrowth 차용 3항목 + LLM 실패, GED target = crowd proportion, GED stimulus 2196=2181+15.
- **아직 미확인 (web only, PDF 없음).** iScience 2023 regional significant-voxel % (TPJ 62% 등). TAFFC VE8/EK6 정확 수치 (paywall). Information Fusion DOI. → 이 3편 은 PDF 확보 후 재검증 권장.
