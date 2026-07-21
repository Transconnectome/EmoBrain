# 연구 발표 스토리라인

## 1. Introduction

### 1.1 감정의 구조
**Cowen & Keltner (2017):** 2185개 감정 비디오, 감정 = VA 2차원이 아니라 **27개 범주**로 조직. Split-half CCA로 재현 가능 차원 수 확인. 범주들은 연속적 gradient로 연결. 34 emotion categories + 14 affective dimensions(arousal, valence, dominance, approach, attention, certainty, commitment, control, effort, fairness, identity, obstruction, safety, upswing) 측정. **핵심: cat > dim, 감정 공간은 고차원**
**Kragel & LaBar (2015):** 영화/음악 유발 fMRI 다변량 분류. 범주적 모델(7개)이 차원적 모델(VA)보다 뇌 활동을 더 잘 설명 → 범주 vs 차원 논쟁의 초기 신경과학 증거

### 1.2 뇌의 감정 표상
**Horikawa et al. (2020):** 같은 자극 2196 비디오, 5명 fMRI. 수십 개 감정이 뇌에서 정확히 디코딩. **Category > Dimension**: 범주가 차원보다 뇌 반응을 잘 예측. **Distributed**: transmodal brain regions(TPJ, mPFC, STS)에 분산. Visual/semantic confound 통제 후에도 유의. Margulies PG 활용: transmodal에서 감정 encoding 강함. **핵심: 뇌 감정 = 고차원, 범주적, 전뇌 분산**
**Du et al. (2023):** 같은 데이터. Voxel-wise encoding model → PCA → "fundamental affective space" 발견(PC1-4). 뇌 공간 ≠ 행동 공간(다른 구조). 14 affective dim의 hybrid. 감정이 cortex에 smooth gradients로 분포. Banded ridge로 emotion/visual/semantic 분리. **핵심: 뇌에 자체적 감정 좌표계 존재**
**Margulies et al. (2016):** Principal Gradient — unimodal(V1,S1,A1) ↔ transmodal(DMN) 축. DMN이 모든 감각 영역에서 최대 거리. 기능 스펙트럼: 지각/행동 → 주의/제어 → 사회인지/자서전적기억. **핵심: cortex의 대규모 조직 원리**
**Ma & Kragel (2026):** 해마가 감정 개념을 계층적으로 표상, vmPFC가 2D VA 공간 추적. 감정 지식이 spatial map처럼 조직. **핵심: 범주(해마)와 차원(vmPFC) 둘 다 존재하되 영역이 다름**

### 1.3 AI와 감정
**Du et al. (2025):** MLLM(Qwen2-VL)로 700만+ triplet odd-one-out judgment → SPoSE 30dim embedding. **MLLM > Human self-report > LLM** → 뇌 예측. TPJ, IPL, MTC, hippocampus에서 MLLM 우위. 30 components: 범주적이면서 차원적 혼합 = "hybrid coding". Sensory grounding 중요(MLLM>LLM). **핵심: AI가 인간 self-report보다 뇌 감정 기하 구조를 잘 포착. 하지만 encoding 방향(AI→Brain)만 봄**
**Conwell et al. (2025):** 180개 비전 모델(감정 학습 없음) → VA의 ~67% 설명. "Perceptual primacy of feeling" — 감정은 지각에 기반. **핵심: 나머지 33%는 무엇인가?**
**VCA (2025):** CLIP-ViT + amygdala-mimetic module → VA 예측(valence r≈0.9, arousal r≈0.7) + 편도체 fMRI alignment. **한계: image only, amygdala only, VA only, post-hoc alignment**
**ICLR (2025) 100 models:** 99개 video model 뇌 alignment 벤치마킹. Temporal modeling→초기시각 alignment, classification task→고수준. Complexity↔alignment 음의 상관. **한계: emotion 안 봄**
**Moussa & Toneva (2025):** Speech model(HuBERT) brain-tuning. Multi-participant fMRI로 LoRA fine-tune. Alignment 50%↑, data efficiency 5x, downstream 유지. **한계: speech 도메인, emotion 아님**

### 1.4 남은 질문
- AI가 설명하는 67%와 못하는 33%의 정체는?
- Du (2025)는 AI→Brain(encoding) 방향만 봤는데, Brain→Behavior(decoding)에서 AI가 놓치는 것은?
- 뇌에서 감정으로 가는 변환 과정에서 AI가 포착 못하는 **뇌 고유 감정 정보**는 무엇인가?
- 그 고유 정보를 AI에 전달할 수 있는가?

**추가 배경:** (2019) 감정 스키마가 시각 피질에 내장 | (2022) 편도체→V1 피드백, 층 특이적 | (2024) Visual looming = 감정의 진화적 원시 | (2023) 감정 개념 인코딩이 발달 과정에서 개인 간 수렴 (5-15세)

## 2. Research Question / Goal / Hypothesis

**Research Question:** 뇌가 시각 자극을 감정으로 변환하는 과정에서, AI 모델이 포착하지 못하는 뇌 고유의 감정 정보(???)는 무엇인가?
**Framework:** Stimulus(AI model=렌즈) — Brain(fMRI=input) — Behavior(emotion rating=output). Brain → ??? → Behavior
**Primary Goal:** ???를 밝힌다. AI model을 렌즈로 사용하여 뇌 표상에서 지각적 성분(AI-shared)과 뇌 고유 성분(AI-unique)을 분리하고, 고유 성분의 정체를 규명
**Sub Goal:** Brain-tuning으로 ???를 AI에 전달 → ???의 existence proof + Video→Emotion 예측 모델 개선 + Emotion Foundation Model 방향 제시

**H1:** 뇌의 감정 표상 = AI-shared(지각적) + AI-unique(???)로 분해됨. AI-unique 잔차에서 감정 디코딩 유의하면 지지
**H2:** ???는 범주적 감정에서 더 큼 (VA와 독립적인 범주 고유 정보)
**H3:** ???는 transmodal regions(TPJ, mPFC, DMN)에서 주로 옴 (Horikawa PG + Margulies gradient)
**H4:** V-JEPA2(self-supervised, vision only, no language)에서도 감정 지각 성분 emerge → language 불필요 (Conwell perceptual primacy)
**H5:** Brain-tuning으로 ??? 전달 → 감정 예측 향상, ???가 큰 감정에서 더 크게 향상 → 메커니즘적 검증

## 3. Methods
**Data:** 2196 비디오(~3초, Cowen & Keltner stimuli), 5명 fMRI(3T), 48 targets(34 cat + 14 dim, crowd-sourced)
**Brain representations:** Raw fMRI — Glasser 360+10=370 (Horikawa 호환) + Schaefer 400+50=450 (Brain-JEPA 호환). Brain-JEPA(768, resting-state pretrained)는 비교군
**Stimulus representations:** V-JEPA2(1408, self-supervised video) | CLIP(512, vision+language) | DINOv2(1536, self-supervised image) — 여러 "렌즈"로 뇌 분해
**Analysis 1 (Ch.1) Brain→Behavior baseline:** Ridge regression, 5-fold CV + LOSO CV. 48 targets 전부. ROI별(theory-driven: amygdala, insula, ACC, mPFC, TPJ, OFC, STS). Cat vs Dim 비교. Horikawa 재현 + 14 dim 확장
**Analysis 2 (Ch.2) AI 렌즈 분해:** **Banded Ridge Regression**(Horikawa/Du 방식)으로 AI-shared vs AI-unique variance 엄밀 분리. 단순 residual 빼기가 아닌 통계적 variance partitioning. A:전체→Emotion B:AI-shared→Emotion C:AI-unique(???)→Emotion. 48 targets × 여러 렌즈 × ROI별
**Analysis 3 (Ch.3) ??? 정체:** 감정별(어떤 감정에서 ??? 큰가) | 영역별(transmodal vs unimodal) | 차원별(14 dim 중 관련 깊은 것) | 구조별(Cat/Dim ratio in ???)
**Analysis 4 (Ch.4) Brain-tuning (sub goal):** V-JEPA2→adapter→predict fMRI→L2 loss (감정 label 안 씀, 순수 뇌 supervision). 비교: vanilla / brain-tuned / behavior-tuned(34cat) / VA-tuned. ???가 큰 감정에서 brain-tuned 향상 크면 = ??? existence proof
**Statistics:** Permutation(n=1000), FDR(BH q<0.05), Z-score+Rank transform(robustness), Banded ridge(confound control). 디코딩: R², Pearson r, AUC-ROC

## 4. Preliminary Results (CCN 2026 + 추가 분석)
**Forward/Reverse 비대칭:** Brain→V-JEPA2 PC: Raw fMRI 6개 유의(R² up to 0.354), Brain-JEPA 3개(R² up to 0.373) | V-JEPA2→Brain PC: 전부 R²=0.000 (Raw에서도 동일) → 비대칭은 Brain-JEPA artifact 아닌 진짜 구조적 차이. **뇌에 AI가 모르는 무언가(???) 존재**
**범주성:** Brain-pred subspace Cat/VA ratio = 1.44(BJ), 1.68(Raw). AV regress out 후 97.6% 유지 → **범주 정보가 VA와 독립적.** Cowen (2017) 강하게 지지
**CCA (PCA100→CCA100):** CC1=0.774, 88/100 유의(FDR<0.05), 27개 r>0.3(substantial). CC들이 구체적 범주 감정과 연결(CC1=Annoyance, CC2=Aesthetic apprec.). 27 ≈ Cowen의 27 범주 + 감정 rating PCA 95%분산=23차원. Subject-level CC1=0.719±0.013(안정)
**Raw fMRI > Brain-JEPA:** brain-pred 6 vs 3 PCs, Cat/VA 1.68 vs 1.44. **Resting-state brain FM이 task-specific 감정 신호 절반 손실** → Raw fMRI를 메인으로
**해석 분석:** R²-Std r=0.48(부분 confound, 77% 진짜 신호). Rank normalize 후 순서 불변(r=0.97). 6 basic emotion 실패 = 데이터 희소성(Joy 0개, Fear 0개). Variance partitioning(preliminary): brain unique 작지만 Brain-JEPA 한계 가능성 → Raw fMRI로 재실행 필요

## 5. 앞으로 할 분석
1. **Ch.1 완성:** 48 targets baseline (Raw fMRI, Glasser+Schaefer, ROI별) ← 진행 중
2. **Ch.2 핵심:** Banded ridge variance partitioning으로 AI-shared vs AI-unique 엄밀 분리
3. **Ch.3:** ??? 정체 규명 (감정별 × 영역별 × 차원별)
4. **추가 렌즈:** DINOv2, VideoMAE 임베딩 추출 → 다중 렌즈 비교
5. **Cowen 연결:** Varimax rotation, SH-CCA 재현

## 6. Future Plan
**본 분석 완성:** ???의 감정별×영역별×차원별 brain necessity map. 다중 AI 렌즈(V-JEPA2/CLIP/DINOv2) 비교. Du(2023) fundamental affective space와 비교
**Brain-Tuning (Sub Goal):** fMRI로 V-JEPA2 fine-tune(Moussa 방식, emotion 도메인 최초). ???가 큰 감정에서 더 향상되면 existence proof. Brain-tuning은 label-free(감정 label 안 씀) → 뇌가 implicit emotion supervision
**데이터 확장:** Emo-FilM(30명, 14 films, 50 emotion items) | ReelMo(20명 fMRI, Jojo Rabbit, 20 emotions moment-by-moment)
**방법론 발전 가능성:** fMRI-LM(LLM token alignment) | VCA 확장(전뇌+범주) | Cross-cultural validation

## 차별점 요약
| 기존 | 우리 |
|------|------|
| Du (2025): encoding (AI→Brain) | **decoding (Brain→Behavior), AI를 "렌즈"로** |
| 단순 residual 분리 | **Banded ridge variance partitioning** |
| MLLM (language 있음) | **V-JEPA2 (language 없음, self-supervised)** |
| 한 모델만 | **다중 렌즈 비교 (V-JEPA2/CLIP/DINOv2)** |
| Post-hoc alignment 확인 | **Brain-tuning으로 능동적 전달** |
| Cat or Dim 한쪽만 | **48 targets (34 cat + 14 dim) 전부** |
| Encoding 방향 only | **Forward/Reverse 비대칭 발견 (최초)** |

## Take-home Message
> AI 비전 모델은 감정의 지각적 성분을 잘 포착하지만, 뇌에는 AI가 놓치는 고유한 감정 정보(???)가 있다. 이 정보는 transmodal regions에서 오며 범주적으로 조직된다. Brain-tuning을 통해 이 정보를 AI에 전달하면 감정 예측이 향상될 수 있다.
