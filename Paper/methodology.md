# EmoBrain Methodology

(Branch `sj_NEW_20260608_perlmutter` 의 EmoBrain framing. 이전 v4 methodology 는 `archive/v4_20260602/Paper/methodology.md`.)

본 문서는 EmoBrain 의 두 axis (BrainVLM + Brain-Video Multimodal) 의 method 를 정리. Phase 1 의 frozen BFM probe method 는 `reports/phase1_audit_20260604/_pdf/main.pdf` 에 상세.

## 1. Data

### Horikawa Naturalistic Video fMRI

- 5 subject (sub-01 ~ sub-05).
- 2185 canonical video stimulus.
- 각 자극당 fMRI 시계열 길이 T (median 5 TR, max 47, 71.6% 자극이 T=5).
- 각 자극당 Cowen 의 34 emotion category score (rater 비율) + 14 affective dimension rating + continuous V (1 ~ 9) + continuous A (2 ~ 8.67).

### 5-fold Stim-stratified CV

- V quartile × A quartile 의 4 × 4 = 16 joint label 로 sklearn.StratifiedKFold (5 fold, seed 0) split.
- 같은 자극은 모든 subject 에서 같은 fold (stim-level leakage 없음).
- 각 fold k 에서 test = fold k, val = (k mod 5) + 1, train = 나머지 3.

### Stimulus features

- Brain side. Brain-JEPA / NeuroSTORM / SwiFT 6 변종의 zero padding embedding (Phase 1 추출). ROI Schaefer400 + Tian S3 50 mean BOLD.
- Video side. CLIP, DINOv2, VideoMAE, V-JEPA2 의 pretrained + scratch embedding (자극당 1 vector). Qwen-VL caption embedding (768-dim).

## 2. Direction 1. BrainVLM

### 2.1. fMRI Patchify

- Input. Horikawa 의 4D fMRI volume (74 × 91 × 81 × T).
- 2D ROI-based 변환. Schaefer 17n400p (400 cortical) + Tian S3 50 (50 subcortical) 의 ROI 단위로 BOLD 시계열을 2D grid layout 으로 재배열. 또는 ROI × time matrix 형태.
- Token 화. UMBRELLA_qwen (Qwen3-VL backbone) 의 fMRI patchifier 통과 → LLM context 의 vision token.

### 2.2. Model Architecture

- Backbone. UMBRELLA_qwen (ABCD-pretrained, Qwen3-VL).
- fMRI vision tower. frozen 또는 LoRA target.
- LLM. Qwen3 family. LoRA fine-tune (rank 8 ~ 16, alpha 16 ~ 32).
- Multi-task output head.
  - Caption / VQA. LLM 의 standard text generation.
  - V/A score. 별도 numeric head (또는 자연어 generation 후 parse).
  - Cat34 distribution. 별도 34-dim regression head.

### 2.3. Training

- Loss = CE (caption / VQA) + λ_1 MSE (V/A) + λ_2 KL (Cat34 soft).
- Optimizer. AdamW. Learning rate scheduler (cosine with warmup).
- Batch size 4 ~ 8 (memory-limited).
- Pilot 학습. Horikawa fold 1 만, 5 subject pooled. 약 1 ~ 2 epoch.

### 2.4. Evaluation

- V/A regression. Pearson r, MAE, MSE.
- Cat34 multilabel. macro AUROC, macro F1.
- Cat34 soft distribution. mean Pearson r, top1 accuracy.
- Caption quality (optional). BLEU, BERTScore, 또는 emotion-relevance metric.
- ROI baseline 과 chance 와 비교.

## 3. Direction 2. Brain-Video Multimodal

### 3.1. Encoder 선정

- Brain encoder. Phase 1 의 best frozen BFM (Brain-JEPA resting, 768-dim) 으로 시작. 또는 ROI mean BOLD (450-dim) 의 단순 baseline.
- Video encoder. V-JEPA2 pretrained (1408-dim, EmoViS 추출).

### 3.2. Projection + Alignment

- Projection head. Brain (768 또는 450) → 512-dim, Video (1408) → 512-dim 의 lightweight MLP (2-layer, GELU, LayerNorm).
- Alignment loss. Symmetric InfoNCE. Temperature 0.07.
- Optional subject-invariant. 같은 자극의 다른 subject brain 끼리 추가 InfoNCE.

### 3.3. Variance Partitioning

- Brain only. Brain projection 만으로 emotion task 학습 / 평가.
- Video only. Video projection 만으로 emotion task 학습 / 평가.
- Joint. Brain + Video concat (또는 cross-attention fusion) 으로 emotion task 학습 / 평가.
- Brain unique variance = Joint metric − Video-only metric.
- Paired bootstrap (10K iteration) 으로 p-value.

### 3.4. Evaluation

- V/A regression. Pearson r.
- Cat34 multilabel. macro AUROC.
- Cat34 soft distribution. mean Pearson r.
- Mixed valence 3-way. balanced accuracy.
- Subject-invariant 학습 시 cross-subject generalization (held-out subject) 도.

## 4. Tasks

### Task 1. V/A Binary Classification (Q1 vs Q4)

- Quartile-based label (v_quartile, a_quartile 의 0 ~ 3).
- v_quartile ∈ {0, 3} 자극 (Q1 vs Q4) 1131 개로 V_binary. a_quartile 유사로 A_binary 1107 개.
- Linear: Logistic Regression L2 balanced. MLP: SwiftMLP.

### Task 2. V/A Regression

- Continuous V (1 ~ 9), A (2 ~ 8.67). 전체 2185 자극.
- Linear: Ridge. MLP: SwiftMLP. Y standardize for MLP convergence.

### Task 3. Cat34 Multilabel Classification

- 자극당 34 score → threshold 0.10 (= 1/10 raters, 자연 단위) → 34-dim 0/1 vector.
- Linear: per-cat L2 logistic balanced. MLP: SwiftMLP 의 (B, 34) BCEWithLogitsLoss.
- Threshold 0.10 의 근거. zero-label 자극 0, min cat 양성률 0.007 (= 15 자극 / 5-fold = 3/fold 안정), 자연 rater fraction.

### Task 4. Cat34 Soft Distribution Regression

- 자극당 34 score 를 sum 1 normalize → 34-dim distribution.
- Linear: MultiOutputRegressor(Ridge) + clip + normalize. MLP: log_softmax + KLDivLoss.
- mean Pearson r + top1 accuracy.

### Task 5. Mixed Valence Categorization (Vaccaro 2024)

- (Vaccaro 2024 의 정확한 정의는 reference 확정 후 명시.)
- Positive / Negative / Mixed 의 3-way classification.
- Linear: LogisticRegression multinomial. MLP: SwiftMLP CE.
- balanced accuracy.

### Task 6. Caption Embedding Regression (Direction 1)

- Brain embedding → Qwen-VL caption text embedding (768-dim) mapping.
- Linear: MultiOutputRegressor(Ridge). 또는 MLP.
- mean Pearson r averaged over 768 dim, 또는 cosine similarity.

### Task 7. Emotion VQA (Direction 1)

- BrainVLM 의 free-form 자연어 응답.
- Evaluation. caption → V/A score parse + Cat34 distribution parse 의 metric.

## 5. Baselines

- Chance. DummyClassifier (stratified, most_frequent) + DummyRegressor (mean, median).
- Tier 1 ROI. Schaefer400 + Tian50 mean BOLD + Ridge / Logistic.
- Tier 2 frozen BFM. Phase 1 benchmark 의 best (Brain-JEPA resting). EmoBrain 의 두 direction 결과 reporting 시 reference baseline 으로만 인용 (main scope 아님).
- Tier 3 video baseline. CLIP / DINOv2 / VideoMAE / V-JEPA2 pretrained embedding + Ridge / Logistic.

## 6. Statistical Procedures

- 5-fold cross-validation 의 fold 별 metric mean ± std.
- Paired bootstrap (10K iteration) 으로 두 model 의 metric 차이 p-value.
- FDR correction 시 Benjamini-Hochberg.
