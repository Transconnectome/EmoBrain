# Scientist Analysis: CCN_Emotion
**분석일**: 2026-05-26
**분석 대상**: V-JEPA2 ↔ Brain-JEPA alignment pipeline (study1/code/19_permutation_test.py, 23_reverse_pca_ridge.py)
**컨텍스트**: framework_EN.md, narrative_v2.md, accepted CCN abstract

---

## 0. 한 줄 요약

분석 코드는 시각적 의미를 brain readout 으로 해석하는 데 다섯 개 핵심 가정을 만들고 있으며, 그중 두 개 (R² clipping 으로 인한 biased null, subject-averaging 이전 alignment 의 부재) 는 통계 결과 자체에 영향을 줄 수 있는 수준이다.

---

## 1. Decision Points (카테고리별)

### A. 입력 형식

**[stimulus_count = 2196]**
- 현재 설정: 전체 2196 비디오 사용 (`brain_raw.shape = (5, 2196, 768)`)
- 옵션 공간: 2185 (EmoViS 처럼 11 개 repeat clip 제외) vs 2196 (현재)
- 과학적 의미: stimulus 2186-2196 은 repeated clips. 같은 비디오를 두 번 본 fMRI 응답이 섞여 들어가면 자극-반응 mapping 에 데이터 누수 가능.
- 제약 조건: meta CSV 의 stim_idx 가 0-2195 까지. Repeat clip 의 indexing 확인 필요.
- 암묵적 가정: "2196 개 모두 독립 자극으로 다뤄도 무방"
- 파생 RQ: repeat clip 을 제외하면 ratio 1.44 가 어떻게 변하는가? EmoViS 와 일관성 검증.

**[subject_aggregation = mean(axis=0) BEFORE analysis]**
- 현재 설정: `brain_mean = brain_raw.mean(axis=0)` — 5 명 subject Brain-JEPA embedding 을 평균낸 후 ridge.
- 옵션 공간: (a) per-subject ridge + 결과 평균, (b) mixed-effects (subject random effect), (c) leave-one-subject-out.
- 과학적 의미: subject 평균 전에 alignment 가 안 되어 있으면 평균이 의미 없다. Brain-JEPA cross-subject r=0.347 (Spearman) 이라서 절반 이상 변동성이 개인-특이. 평균 시 noise cancellation 이 일어남.
- 제약 조건: per-subject ridge 는 통계 power 가 1/5 로 감소. n=5 라서 mixed-effects 도 문제.
- 암묵적 가정: "Brain-JEPA 의 subject-invariance (Pearson r=0.986 on embedding) 가 충분히 높아서 단순 평균 가능"
- 파생 RQ: Per-subject ridge 의 5 개 R² 분포를 보면, 평균 R² 가 그 분포의 중앙값인가, 아니면 outlier 가 끌어올린 것인가?

**[HRF_lag = 미적용]**
- 현재 설정: V-JEPA2 embedding (시간 t 비디오) ↔ Brain-JEPA embedding (시간 t fMRI) 직접 매칭. HRF 보정 없음.
- 옵션 공간: 0, 2, 4, 6, 8 초 lag.
- 과학적 의미: BOLD 신호는 시각 자극 후 5-6 초 peak. 짧은 emotion 비디오 (5-10초) 에서는 자극 onset 과 BOLD peak 의 시차가 핵심.
- 제약 조건: Horikawa 데이터셋이 이미 어떤 preprocessing 을 적용했는가에 의존. Brain-JEPA pretraining 이 어떤 시간 정렬을 가정하는가도 영향.
- 암묵적 가정: "Horikawa fMRI 가 이미 HRF-aligned 처리되어 들어왔거나, Brain-JEPA 가 시간 invariant 표상을 학습했음"
- 파생 RQ: lag 를 0/2/4/6 으로 sweep 했을 때 brain-predictable PC 수와 ratio 가 어떻게 변하는가?

### B. 아키텍처 (분석 pipeline)

**[PCA n_components = 100]**
- 현재 설정: V-JEPA2 (1408-dim) → top 100 PCs. Brain-JEPA (768-dim) 도 reverse 분석에서는 100 PCs.
- 옵션 공간: 50, 100, 200, 500, no-PCA (full 1408).
- 과학적 의미: variance 기준 top 100 이 brain-relevance 기준 top K 와 일치한다는 보장 없음. 저차 PC 들이 noise 의 dominant 방향이고, 고차 PC 가 affective signal 을 담을 가능성도 있음.
- 제약 조건: ridge 가 N=2196 samples 에 D=1408 features 면 underdetermined. PCA 가 regularization 역할도 함.
- 암묵적 가정: "Top-100 variance 가 affective information 의 majority 를 포함"
- 파생 RQ: full 1408-dim 위에서 직접 ridge (강한 alpha) 했을 때 brain-readable feature 가 PC space 와 같은 영역인가?

**[ridge alpha = 1.0 (fixed)]**
- 현재 설정: `Ridge(alpha=1.0)` — 모든 PC 에 동일, 고정.
- 옵션 공간: GridSearchCV 로 inner-fold tuning, 또는 RidgeCV.
- 과학적 의미: alpha 가 너무 작으면 overfit, 너무 크면 underfit. PC 별로 분산 scale 이 다른데 (PC1 vs PC100), alpha=1.0 이 동일하게 적합한지 불확실.
- 제약 조건: per-PC tuning 은 multiple comparison 위험.
- 암묵적 가정: "alpha=1.0 이 모든 PC 에 대해 reasonable"
- 파생 RQ: alpha sweep [0.01, 0.1, 1, 10, 100] 했을 때 ratio 1.44 의 robustness 어떤가?

**[cross-validation = sklearn default KFold(5)]**
- 현재 설정: `cross_val_score(..., cv=5)`. Default 가 stratified 안 되어 있고, shuffle=False (sequential).
- 옵션 공간: KFold(shuffle=True, random_state=...), GroupKFold (subject-level), StratifiedKFold (emotion category).
- 과학적 의미: stimulus 가 dataset 안에서 어떤 순서로 들어가 있는지에 따라 fold 가 systematic 하게 다른 emotion category 를 담을 수 있음. 자극 순서가 category-clustered 면 leakage.
- 제약 조건: Horikawa 데이터셋이 randomized 순서로 들어와 있는지 직접 확인 필요.
- 암묵적 가정: "stimulus 순서가 random 이거나, sequential split 이 leak 안 함"
- 파생 RQ: shuffle=True 적용 시 R²=0.373 (PC1) 이 변하는가?

### C. 통계 전략

**[R² clipping = max(R², 0.0)] — 가장 risky**
- 현재 설정: `r2_obs[i] = max(scores_r2.mean(), 0.0)` — 음수 R² 를 0 으로 clip. Null distribution 도 동일하게 clipped.
- 옵션 공간: (a) clipping 없이 raw R², (b) sklearn `explained_variance_score`, (c) per-fold R² 의 median.
- 과학적 의미: Clipping 은 null distribution 의 분포 shape 을 왜곡한다. Observed R² 가 작을수록 (PC2/PC3 R²=0.075/0.088) clipping 효과가 커진다. Null 의 mass 가 0 에 쌓이면 p-value 가 inflated.
- 제약 조건: 음수 R² 는 model 이 mean baseline 보다 나쁨을 의미 — 의미있는 정보 없음. 직관적으로 0 clip 이 reasonable 해 보임.
- 암묵적 가정: "음수 R² 와 0 R² 는 동일한 'no information' 상태"
- 파생 RQ: clipping 없이 raw R² 로 permutation test 했을 때 PC2, PC3 의 p-value 가 어떻게 변하는가? **이건 즉시 검증해야 함.**

**[permutation count = 1000]**
- 현재 설정: n_perm=1000.
- 옵션 공간: 1000, 10000, 100000.
- 과학적 의미: 1000 permutations 의 minimum p-value = 0.001. FDR 보정 후 q=0.05 를 달성하려면 raw p < 0.05/100 (Bonferroni-like) = 0.0005 가 필요한 경우도 있는데, 1000 permutations 로는 해상도 부족.
- 제약 조건: 계산 시간. 10000 permutations × 100 PCs = 100만 ridge fits.
- 암묵적 가정: "p=0.001 해상도가 충분"
- 파생 RQ: PC2, PC3 의 p-value 가 1000 vs 10000 permutations 에서 stable 한가?

**[FDR correction = Benjamini-Hochberg over 100 PCs]**
- 현재 설정: 100 PCs 모두에 BH-FDR.
- 옵션 공간: nonzero R² PCs 에만 적용 (예 5-10 개), 또는 stratified FDR.
- 과학적 의미: 0 R² PCs 는 p=1.0 으로 자동 들어가서 BH-FDR 의 분모를 키운다. 이게 정직한 multiple comparison correction 인지, 아니면 over-conservative 인지 미정.
- 제약 조건: FDR over k tests 의 정의에 따름.
- 암묵적 가정: "0 R² PCs 도 test 의 일부로 계산"
- 파생 RQ: nonzero R² PCs 에만 FDR 적용하면 어떻게 변하는가?

### D. 평가

**[baseline = full V-JEPA2 100-PC space, ratio = 1.26]**
- 현재 설정: brain-predictable 3 PCs 의 ratio 1.44 vs full 100-PC space ratio 1.26 비교.
- 옵션 공간: (a) untrained ViT, (b) ImageNet ViT, (c) shuffled-brain, (d) brain-unpredictable PCs.
- 과학적 의미: 1.44 vs 1.26 비교는 "같은 V-JEPA2 안에서" within-model contrast 다. 외부 baseline 없이는 V-JEPA2 자체의 효과인지 알 수 없음. (이게 narrative 의 Pillar 3 missing part.)
- 제약 조건: 외부 baseline 추출에 compute 필요.
- 암묵적 가정: "Within-model contrast 만으로 'self-supervised contribution' 주장 가능"
- 파생 RQ: framework 의 H3 가 정확히 이걸 묻는다.

**[noise ceiling = 미정의]**
- 현재 설정: 측정 없음.
- 옵션 공간: split-half reliability of Brain-JEPA embedding across subjects.
- 과학적 의미: R²=0.373 (PC1) 의 절대값이 가능한 max 의 몇 % 인지 모르면 effect size 평가 불가.
- 제약 조건: Horikawa dataset 에 repeat session 이 있는지 확인 필요.
- 암묵적 가정: "R²=0.373 이 의미있게 크다"
- 파생 RQ: split-half 로 Brain-JEPA reliability 계산했을 때 noise ceiling 어떤가?

**[per-subject stability test = post-hoc]**
- 현재 설정: 18_subjectwise_claim_check.py 별도 스크립트로 5 명 ratio 가 모두 >1 임을 확인.
- 옵션 공간: (a) 현재처럼 후행 확인, (b) primary analysis 가 per-subject 부터 시작, (c) mixed-effects.
- 과학적 의미: "5 명 모두 ratio > 1" 은 sign-only test. Magnitude variability 무시. 통계적 power 약함.
- 제약 조건: n=5, Wilcoxon signed-rank 의 minimum p-value = 0.0625 (one-sided).
- 암묵적 가정: "Sign-only consistency 가 generalization 의 충분 증거"
- 파생 RQ: 5 명 ratio 의 분포가 1.44 주변에 tight 한가, 아니면 widely spread 한가?

---

## 2. Blind Spots (연구 계획에 없는 것)

### B.1 — Stimulus level

**B.1.1 Repeat clip 처리 미명시.** Stimulus 2186-2196 (11 clips) 이 repeat 인지, 그래서 fMRI 응답이 within-subject 평균인지, 분석에서 어떻게 다뤄지는지 framework 와 abstract 어디에도 명시 안 됨. EmoViS 는 명시적으로 2185 만 사용. 일관성 깨짐.

**B.1.2 자극 길이 변동성.** Cowen-Keltner 비디오는 길이가 다양 (5-10초 범위). V-JEPA2 가 16 프레임 uniform sampling 하는데, 5초 비디오는 3.2 fps, 10초 비디오는 1.6 fps. 같은 16 프레임이 매우 다른 temporal resolution. Brain-JEPA 측에서도 비디오 길이별로 BOLD window 가 다를 텐데 어떻게 정렬했는지 미명시.

### B.2 — Pipeline level

**B.2.1 PCA-then-ridge 의 정당성 분석 부재.** "100 PCs 로 줄인 후 ridge" 가 "full 1408-dim ridge with high alpha" 와 같다는 robustness check 없음. Cumulative variance ratio 도 결과에 보고 안 됨.

**B.2.2 V-JEPA2 layer 선택 의도 미서술.** Final hidden state 의 mean-pool 만 사용. Layer-wise 추출 코드가 archive/extraction_infra/03_extract_layer_embeddings.py 에 있지만 사용 안 됨. "어떤 layer 가 affect-relevant 한가"는 Sartzetaki 2025 핵심 질문 중 하나이고 직접 관련.

**B.2.3 V-JEPA2 16-frame sampling 의 temporal coverage.** Uniform sampling 이 emotion arc 의 어느 부분을 잡는가? 시작/끝/middle 의 비중이 균일하지 않다면 trajectory 정보 부족.

### B.3 — Statistical level

**B.3.1 Ratio metric 의 통계 검정 미명시.** "1.44 vs 1.26" 의 통계적 difference 가 paired test 로 검증되지 않음. Bootstrap CI for ratio difference 도 없음. Abstract 의 "exceed" 라는 표현이 inferential statistic 으로 받쳐지지 않음.

**B.3.2 Multiple comparison: 34 categories vs 2 V-A.** 34 개 mean R² 와 2 개 mean R² 의 비교는 sample size 가 17:1. Mean 의 변동성도 17 배 차이. ratio 차이가 sampling effect 아닌지 명시적 test 없음.

**B.3.3 Cross-validation leakage 점검 부재.** Cowen-Keltner 비디오가 dataset 안에서 어떻게 ordered 되어 있는지, KFold(shuffle=False) 가 emotion category 별로 split 되는지 확인 없음.

### B.4 — Interpretation level

**B.4.1 PC1 의 시각적 의미 미해석.** R²=0.373 으로 압도적인 PC1 이 어떤 visual feature 를 인코딩하는지 — 자극을 PC1 score 로 정렬해서 top/bottom 10 비디오를 보는 것 — 분석 코드에 없음. "그냥 얼굴 유무인가, 밝기인가, 모션인가" 의 답이 없으면 leap 1 (visual → affective) 를 검증 불가.

**B.4.2 Brain region attribution 부재.** Brain-JEPA embedding 은 whole-brain summary. 어느 영역 (visual cortex vs limbic vs DMN) 이 alignment 에 기여하는지 미분석. "Affective subspace" 주장이면 limbic / DMN 이 핵심이어야 하는데 확인 없음.

**B.4.3 Negative control 부재.** Shuffled-brain (target permute) 또는 unrelated stimulus set 에서 같은 pipeline 돌렸을 때 ratio 가 1.0 으로 떨어지는지 확인 없음. False positive rate validation.

### B.5 — Theoretical level

**B.5.1 Brain-JEPA 가 task-fMRI 에서 emotion variance 를 보존하는지 직접 검증 없음.** Brain-JEPA 는 UK Biobank rest-fMRI 로 pretrain. Horikawa task-fMRI 의 emotion-related variance 가 Brain-JEPA latent 에 살아남는지 직접 test 안 됨. "Brain-JEPA category decoding accuracy from group-mean embedding" 같은 baseline 측정 누락.

**B.5.2 Cowen-Keltner taxonomy 자체의 visual coherence 측정 없음.** 34 categories 가 visual feature space 에서 얼마나 separable 한지 (예: V-JEPA2 raw embedding 으로 silhouette score) baseline. Categorical R²=0.055 가 taxonomy 자체의 visual coherence 의 trivial 반영인지 분리 안 됨.

---

## 3. 실험 트리

```
[Decision: HRF lag]
├── 옵션 A: 0초 (현재, default 가정) → 검증 질문: brain BOLD 가 이미 HRF-corrected 상태로 들어왔다고 전제하면 결과 변화 없음
├── 옵션 B: 4-6초 lag → 검증 질문: V-JEPA2 input 을 4-6초 shift 했을 때 R²=0.373 어떻게 변하는가
└── 권고: [즉시 결정] Horikawa preprocessing 명세 확인. 만약 raw BOLD 면 lag 분석 필수.

[Decision: R² clipping]
├── 옵션 A: 현재 max(R², 0) → 검증 질문: null distribution 이 0 에 mass 가 쌓이는지 plot
├── 옵션 B: clipping 없음 → 검증 질문: PC2 (R²=0.075), PC3 (R²=0.088) 의 p-value 가 clipping 없을 때 어떻게 변하는가
└── 권고: [즉시 결정] 두 방식을 둘 다 돌려서 supplementary table 로 비교. PC2/PC3 의 유의성이 clipping 에 sensitive 하면 그게 paper conclusion 의 fragility.

[Decision: subject aggregation]
├── 옵션 A: mean(axis=0) before ridge (현재) → 검증 질문: 평균 후 신호의 SNR
├── 옵션 B: per-subject ridge + 5 R² 평균 → 검증 질문: 5 명 R² 의 분포 width
├── 옵션 C: leave-one-subject-out → 검증 질문: generalization across subjects
└── 권고: [1라운드] 옵션 B 를 18_subjectwise_claim_check.py 의 확장으로 primary metric 화. 옵션 A 는 robustness 로 supplementary.

[Decision: PCA n_components]
├── 옵션 A: 100 (현재) → 검증 질문: top-100 이 brain-relevant signal 의 99% 를 포함하는가
├── 옵션 B: 200, 500, no-PCA → 검증 질문: 더 많은 PC 를 포함시키면 추가 brain-readable PC 가 출현하는가
└── 권고: [2라운드] 200 PC 까지 확장 1 회 실행. 만약 PC 4-10 중 누군가 survive 하면 "3 PC 가 다" 라는 abstract claim 약화 필요.

[Decision: 외부 baseline 모델]
├── 옵션 A: untrained V-JEPA2 (random init) → 검증 질문: SSL pretraining 의 effect
├── 옵션 B: ImageNet ViT-L → 검증 질문: supervised vs SSL
├── 옵션 C: VideoMAE → 검증 질문: temporal SSL 의 architecture vs objective
└── 권고: [1라운드] Pillar 3 의 핵심. 카메라 레디 후 즉시 시작. 결과를 8월 포스터에 추가.

[Decision: visual baseline partial out]
├── 옵션 A: VGG19 + 73-dim semantic (현재 partial 만) → 검증 질문: 이미 사용된 baseline 이 정확히 무엇을 통제하는가
├── 옵션 B: DINOv2 (object), Places365 (scene), optical flow (motion), Sadeghi 139 → 검증 질문: 각 baseline 별 partial ratio
└── 권고: [1라운드] Pillar 2 의 핵심. 카메라 레디 보강 statistical 수치 일부로 활용.

[Decision: PC1 stimulus interpretation]
├── 옵션 A: PC1 score 로 정렬한 top/bottom 10 비디오 manual inspection → 검증 질문: PC1 이 어떤 visual property
├── 옵션 B: PC1 score 와 face detection, motion energy, scene class probability 의 correlation → 검증 질문: standard visual feature 와의 overlap
└── 권고: [즉시 결정] 옵션 B 는 baseline 추출 진행 중 자동 결정. 옵션 A 는 1 시간 작업. 포스터 figure 후보.

[Decision: brain region attribution]
├── 옵션 A: Brain-JEPA latent → Schaefer parcel inverse projection → 어느 parcel 의 variance 가 PC1 에 기여
├── 옵션 B: Per-network analysis (DMN, visual, salience) → 검증 질문: alignment 가 어느 network 에 가장 강한가
└── 권고: [2라운드] Brain-JEPA 의 inverse projection 가능성 (decoder weights 사용 가능?) 확인 후 결정.

[Decision: V-JEPA2 layer-wise]
├── 옵션 A: 현재 final layer 만 → 검증 질문: middle layer 가 더 affect-relevant 한가
├── 옵션 B: blocks 4, 12, 20, 28, 36, 40 → 검증 질문: depth gradient
└── 권고: [2라운드] extraction_infra/03_extract_layer_embeddings.py 이미 있음. 비용 적당.

[Decision: noise ceiling]
├── 옵션 A: split-half Brain-JEPA reliability → 검증 질문: R²=0.373 이 max 가능 R² 의 어디
├── 옵션 B: Horikawa repeat clip (있다면) 의 within-subject test-retest reliability → 검증 질문: stimulus-level reliability
└── 권고: [1라운드] 옵션 A 는 추가 데이터 없이 가능. 즉시 측정.

[Decision: Brain-JEPA emotion preservation 검증]
├── 옵션 A: Brain-JEPA group-mean 으로 34 emotion category classification → 검증 질문: Brain-JEPA 가 emotion 변동성을 보존하나
├── 옵션 B: Raw fMRI vs Brain-JEPA 의 categorical decoding 비교 → 검증 질문: 압축의 정보 손실
└── 권고: [1라운드] Brain-JEPA 가 task-fMRI 에서 작동하는지의 prerequisite test. 안 하면 모든 결과의 foundation 이 흔들림.
```

---

## 4. 즉시 결정 필요 항목

다음 다섯 개는 **카메라 레디 (6/11) 또는 그 직후 1 주 안에** 결정해야 한다. 결정 안 하면 reviewer 또는 본인 self-doubt 에 답 못함.

1. **R² clipping 검증**. Clipping 없는 raw R² 로 permutation test 재실행. PC2 (R²=0.075), PC3 (R²=0.088) 가 여전히 survive 하는가? 그 결과를 supplementary 또는 본문에 1 줄.

2. **Cross-validation shuffle 검증**. KFold(shuffle=True, random_state=42) 로 재실행. R²=0.373 이 ±0.01 이내에서 변하는가? 변하면 ordering leakage 있다.

3. **HRF 처리 확인**. Horikawa dataset 의 preprocessing 명세 (paper 또는 metadata) 에서 BOLD 가 HRF-corrected 인지 확인. 만약 raw 라면 lag 분석 필수.

4. **Brain-JEPA emotion preservation test**. Brain-JEPA group-mean embedding 만으로 34 category 또는 V-A 의 simple linear decoding accuracy 측정. 만약 raw fMRI 보다 못 하면 분석의 motivation 자체가 흔들림.

5. **PC1 stimulus interpretation**. Top/bottom 20 비디오의 manual + face detector / scene classifier 로 PC1 이 잡는 visual feature 정체 1 차 파악. 포스터 figure 후보.

---

## 5. 연구 계획 업데이트 권고

### framework_EN.md 에 추가할 절들

**"Methodological transparency" 섹션 신설** (Hypotheses 이후, References 이전):
- HRF lag handling
- Subject aggregation rationale + alternatives
- R² clipping policy + its effect on null distribution
- Cross-validation split policy + leakage check

이 섹션이 없으면 reviewer 가 카메라 레디 또는 포스터에서 1 번 질문에 답이 막힌다.

### narrative_v2.md 에 추가할 항

"두 leap" 위에 "**측정의 기술적 fragility**" 한 절 추가. 다음 항목들:
- PC2/PC3 의 유의성이 R² clipping 에 sensitive 한지 미검증
- Subject mean before ridge 의 SNR effect 미정량
- KFold shuffle 효과 미확인
이게 leap 1 보다 우선해서 fix 해야 할 technical 위험.

### CLAUDE.md 에 추가할 rule

```
## 측정의 fragility check (2026-05-26 추가)

다음 5 개 항목은 카메라 레디 또는 풀 페이퍼 진입 전에 반드시 검증되어 있어야 한다.
어느 하나라도 fragile 한 것으로 판명되면 abstract 의 main finding 표현을 약화 또는 한정한다.

1. R² clipping 의 null distribution 영향
2. KFold shuffle 효과
3. HRF lag handling 일관성
4. Brain-JEPA 가 task-fMRI emotion variance 보존하는지
5. Subject mean before ridge 의 SNR vs per-subject ridge
```

---

## 6. 비판 — 직설적으로

이 분석에서 발견한 다섯 가지 중요한 위험.

**위험 1 (가장 큰 것)**: R² max-clipping 이 null distribution 의 mass 를 0 에 쌓고, observed R² 가 작은 PC (PC2, PC3) 의 p-value 를 inflate 시킬 가능성. 만약 clipping 없이 PC2, PC3 의 p-value 가 0.05 이상으로 올라가면 "3 PC subspace" 라는 핵심 framing 이 무너지고 사실상 "PC1-only" 가 된다. PC1 만 살아있으면 ratio 1.44 의 의미가 다른 해석으로 변한다. **즉시 검증**.

**위험 2**: HRF 처리 미명시. 만약 Horikawa preprocessing 이 HRF 보정을 안 했고 Brain-JEPA pretraining 도 시간 정렬을 가정 안 한다면, V-JEPA2 (t) ↔ Brain-JEPA (t) 매칭이 4-6 초 misalignment 를 안고 가는 것. 이 경우 R²=0.373 이 underestimate. 더 강력한 결과 가능성도 있고, 반대로 다른 lag 에서 다른 PC 들이 align 될 수도 있다.

**위험 3**: Subject mean before ridge 의 잠재적 information loss. EmoViS 데이터로 검증 가능: per-subject ridge 의 5 R² 가 0.373 의 mean 인지, 또는 큰 분산을 가지는지.

**위험 4**: PC1 dominance. R²=0.373 (PC1) 이 PC2/PC3 (0.075/0.088) 의 5 배. "3-PC subspace" 라는 표현은 통계적으로는 맞지만 실질적으로는 1-PC 효과 + 약한 2-PC. 만약 PC2, PC3 가 위험 1 에 의해 invalidated 되면 single-PC story 다.

**위험 5**: Cross-validation 가 자극 순서를 따라가는 경우 데이터 leak. 검증 안 됨.

---

## 7. 강점 — 공정하게

너무 비판만 하지 않게.

**강점 1**: Permutation test + FDR. 표준 multiple comparison 처리. 1000 perm 이 다소 적지만 procedure 자체는 깨끗.

**강점 2**: 5-fold cross-validation. Out-of-sample R² 보고. Hold-out 은 없지만 CV 가 적당.

**강점 3**: Per-subject stability 분석 별도 진행 (18_subjectwise_claim_check.py). 모든 5 명에서 ratio > 1 확인. sign-only 지만 generalization 의 기본 증거.

**강점 4**: Partial confound regression 시도 (VGG19 + semantic). 부분적이지만 시도는 있음. 카메라 레디에서 수치 보강하면 됨.

**강점 5**: Forward + reverse 두 방향 분석. 23_reverse_pca_ridge.py 에 Brain → V-JEPA 와 V-JEPA → Brain 양방향 결과 비교. 단일 방향만 본 분석보다 robust.

---

## 결론

전체 narrative 의 흐름은 잘 잡혀 있다 (framework_EN.md, README.md). 하지만 그 흐름이 받쳐주는 **실제 코드 단계**에 다섯 개의 measurement fragility 가 있고, 그중 R² clipping 검증이 가장 시급. 이건 Pillar 2/Pillar 3 baseline 추출보다 먼저 (또는 병렬로) 해야 한다. 만약 PC2/PC3 가 clipping 없이 살아남지 못한다면, 전체 abstract 의 framing 이 "PC1-driven 단일 axis" 로 후퇴해야 하고, 그건 Pillar 2/3 baseline 작업의 motivation 자체를 바꾸기 때문이다.

순서:
1. **R² clipping 재검증** (1 일 작업)
2. **HRF / CV shuffle / Brain-JEPA emotion preservation** 3 개 fragility check (1 주 작업)
3. **Pillar 2 visual baseline 추출** (1 주)
4. **Pillar 3 model baseline 추출** (2 주)
5. **PC1 interpretation + brain region attribution** (1 주)
6. **노이즈 ceiling, layer-wise 등 depth 분석** (병렬)
