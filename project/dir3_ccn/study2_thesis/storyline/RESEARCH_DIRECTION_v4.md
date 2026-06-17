# EmoFM: Emotion Foundation Model
## Research Direction — 전체 청사진 v4

**Last updated:** 2026-04-12

---

## 중심축 (한 문장)

> **"인간 뇌의 시각적 감정 표상에서 AI가 설명하지 못하는 고유 성분을 발견하고,
> 그 성분이 어떤 뇌 영역에서 오며 어떻게 조직되는지 규명하고,
> 이를 AI에 전달하여 감정 예측 모델을 향상시킨다."**

---

## 전체 흐름

```
Chapter 1                Chapter 2                Chapter 3                Chapter 4
─────────────────        ─────────────────        ─────────────────        ─────────────────
Brain → Emotion          AI 렌즈로 뇌 분해         AI-unique 성분           감정 예측 모델
(기준선 확립)             (shared/unique 분리)      정체 규명                (Brain-tuning +
                                                                           Brain+Video)

"뇌가 감정을             "AI가 설명 못하는          "범주적이고               "그걸 AI에 심으면
 어떤 영역에서            부분이 있다"               transmodal에서 온다"       예측이 향상된다"
 인코딩하는가"                                      ← ROI 분석이 킥
      ↓                        ↓                        ↓                        ↓
   Baseline +            전제 확인 ⚠️              구조 + 위치 규명          Existence proof
   ROI 지도
```

**ROI 분석의 역할:**
- Ch1: "어떤 영역이 감정을 인코딩하는가" → 감정 표상 지도 (baseline)
- Ch3: "AI-unique 성분이 어느 영역에서 오는가" → **핵심 킥**
- Ch4: "Brain+Video에서 Brain 기여가 큰 ROI = Ch3 AI-unique 영역?" → 검증

**⚠️ Chapter 2의 AI-unique residual R² > 0 이 전체 프로젝트의 전제.**

---

## 논문별 상세 활용 계획

### 1. Horikawa et al. (2020) — *iScience*
**"The Neural Representation of Visually Evoked Emotion Is High-Dimensional, Categorical, and Distributed across Transmodal Brain Regions"**

**핵심 발견:**
- 2,185개 감정 비디오, 5명 fMRI
- 34 emotion category > 14 affective dimension (cat > dim)
- 감정 표상이 transmodal 영역 (STS, TPJ, PG 등)에 분산
- 뇌 활동 패턴이 cluster-like 구조 (27개 클러스터)

**우리가 가져올 것:**
- 데이터셋 (동일 데이터 사용 — Horikawa fMRI + emotion ratings)
- cat > dim 결과: Ch1의 재현 대상 (Cat/VA ratio)
- transmodal 분산 표상: Ch3에서 AI-unique 위치 예측의 근거
- 27개 클러스터 구조: Ch3의 감정 조직화 분석에 활용
- 방법론 (RSA, encoding/decoding, UMAP): 일부 차용

**우리가 확장하는 것:**
- Horikawa는 cat > dim을 보였지만 "왜"를 설명 못함
  → 우리는 AI 렌즈로 "지각적(AI-shared) vs 뇌 고유(AI-unique)"로 설명
- Horikawa는 transmodal이 중요하다고 했지만 기능적 설명 없음
  → 우리는 AI-unique 성분이 transmodal에서 크다는 것으로 설명
- 14 affective dimension을 본격적으로 분석 (Horikawa는 cat 위주)

**포지셔닝:** Ch1의 재현 대상이자 Ch2-3의 출발점

---

### 2. Cowen & Keltner (2017) — *PNAS*
**"Self-report captures 27 distinct categories of emotion bridged by continuous gradients"**

**핵심 발견:**
- 2,185개 비디오, 34 emotion category + 14 affective dimension 체계 확립
- 27개 distinct emotion 존재
- 범주 감정이 affective dimension보다 self-report를 더 잘 설명
- 범주들이 연속적 gradient로 연결됨

**우리가 가져올 것:**
- 34 cat + 14 dim 레이블 체계: 우리 분석의 target variable
- "cat > dim" 주장: Ch1-3의 이론적 배경
- 27개 distinct emotion: Ch1의 클러스터 분석 기준 (k=27)
- SH-CCA 방법론: 우리 CCA 분석에 활용

**우리가 확장하는 것:**
- Cowen은 행동(self-report)에서 cat > dim을 보임
  → 우리는 뇌(fMRI)에서, 특히 AI-unique 성분에서 cat > dim을 보임
- "cat이 dim보다 좋은 이유"를 뇌-AI 분리로 설명

**포지셔닝:** 분석의 이론적 프레임워크 + 레이블 체계 제공

---

### 3. Du et al. (2023) — *iScience*
**"Topographic representation of visually evoked emotional experiences in the human cerebral cortex"**

**핵심 발견:**
- Horikawa 데이터로 voxel-wise encoding model 구축
- 피질에서 "fundamental affective space" 발견
- 감정 표상이 smooth gradient로 피질 전체에 분포
- 14 hypothesized affective dimension 중 다수가 fundamental space에 포착됨
- affective gradient가 DMN 전체에 분포

**우리가 가져올 것:**
- fundamental affective space의 존재: Ch1에서 재현 + 확장
- 14 dim과 뇌 공간의 관계: Ch1-D, Ch3-E에서 참조
- DMN에서의 affective gradient: Ch3-B에서 AI-unique ROI와 비교
- voxel-wise encoding 방법론: 부분 차용

**우리가 확장하는 것:**
- Du는 "어떤 affective space가 있다"를 보임
  → 우리는 "그 space를 AI-shared vs AI-unique로 분해"
- Du는 encoding 방향 (자극→뇌)
  → 우리는 decoding 방향 (뇌→감정) + AI 렌즈

**포지셔닝:** Ch1의 선행 연구 + Ch3에서 우리 결과와 비교

---

### 4. Du et al. (2025) — *preprint*
**"Bridging the behavior-neural gap: A multimodal AI reveals the brain's geometry of emotion more accurately than human self-reports"**

**핵심 발견:**
- MLLM (Qwen2-VL)의 triplet similarity judgment가
  인간 self-report보다 뇌 활동을 더 잘 예측
- "behavior-neural gap = rating 방법론의 한계" 주장
- MLLM embedding이 30차원 affective space를 형성
- 감각적 grounding (vision)이 신경 정렬에 중요

**우리가 가져올 것:**
- behavior-neural gap 개념: Ch2의 motivation으로 인용
- MLLM > human self-report 결과: "AI가 많은 걸 설명한다"는 근거
- 30차원 affective space: Ch1-3에서 비교 reference
- 감각 grounding의 중요성: V-JEPA2 선택 근거

**우리가 반박/확장하는 것:**
- Du: "gap = 측정 문제"
  → 우리: "gap의 일부는 진짜 뇌 고유 정보" (AI-unique > 0이면)
- Du: encoding 방향 (AI→뇌 예측)
  → 우리: decoding 방향 (뇌→감정) + AI-unique 분리
- Du는 MLLM (language 있음) 사용
  → 우리는 V-JEPA2 (language 없음) — 순수 시각 표상

**⚠️ 중요:** Ch2 residual 결과에 따라 Du와의 관계 결정
- residual R² > 0 → Du에 반론
- residual R² ≈ 0 → Du 지지, 스토리 수정

**포지셔닝:** 직접적 비교 대상 + 우리 주장의 필요성 근거

---

### 5. Conwell et al. (2025) — *PNAS*
**"The perceptual primacy of feeling: Affectless visual machines explain a majority of variance in human visually evoked affect"**

**핵심 발견:**
- 180개 vision model로 인간의 arousal, valence, beauty 예측
- 감정 없는 순수 지각 모델이 explainable variance의 majority 설명
- CLIP 등 language-supervised 모델이 best
- 깊은 레이어, self-supervised 모델이 좋은 성능
- "지각 계산이 감정 유발에 핵심" 주장

**우리가 가져올 것:**
- "지각이 감정의 대부분 설명": Ch2 motivation
  ("그렇다면 나머지는 어디에 있는가?" → AI-unique)
- 180개 모델 비교 접근법: 우리의 다중 렌즈 분석 설계에 영향
- "deeper layers, self-supervised better": V-JEPA2, CLIP 선택 근거
- linear decoding from features: 우리 방법론과 동일

**우리가 확장하는 것:**
- Conwell은 image 데이터 + VA만 봄
  → 우리는 video + 34 cat + fMRI
- Conwell은 "지각이 얼마나 설명하는가"를 물음
  → 우리는 "설명 못하는 부분이 뇌 어디에 있는가"를 물음
- Conwell은 behavior(rating) 기준
  → 우리는 brain(fMRI) 기준으로 decompose

**포지셔닝:** Ch2의 핵심 motivation ("나머지 33-47%는 어디에?")

---

### 6. Moussa & Toneva (2025) — *ICLR 2025*
**"Improving Semantic Understanding in Speech Language Models via Brain-tuning"**
*(파일명: _2026__IMPROVING_SEMANTIC_UNDERSTANDING...)*

**핵심 발견:**
- Speech model (Wav2Vec2, HuBERT, Whisper)을 fMRI로 fine-tune
- Brain-tuning → semantic brain region alignment 향상
- Brain-tuning → downstream semantic task 성능 향상
- Low-level feature 의존도 감소
- "뇌 신호가 semantic understanding을 향상시킨다"

**우리가 가져올 것:**
- Brain-tuning 방법론 전체: Ch4-A의 핵심 방법
  (fMRI로 pretrained model fine-tune하는 파이프라인)
- "brain-tuning → downstream task 향상" 결과:
  우리도 emotion task에서 같은 효과 예측
- Low-level vs semantic 분리 방법:
  우리의 AI-shared vs AI-unique 분리에 영향
- Speech → Vision/Emotion 확장: 우리 contribution의 핵심

**우리가 확장하는 것:**
- Moussa: speech + language domain
  → 우리: visual emotion domain (video + 34 cat)
- Moussa: brain alignment 향상이 목적
  → 우리: emotion prediction 향상이 목적
- Moussa: semantic task 향상
  → 우리: emotion category prediction 향상
  + AI-unique 감정에서 향상이 클 것 (Ch3 연결)

**포지셔닝:** Ch4-A의 방법론적 선례. "speech에서 됐으니 emotion에서도 될 것"

---

### 7. Moussa et al. (2025) — *NeurIPS 2025*
**"Brain-tuning Improves Generalizability and Efficiency of Brain Alignment in Speech Models"**

**핵심 발견:**
- Multi-participant brain-tuning으로 일반화 향상
- 5배 data efficiency (새 참여자에게 1/5 데이터로 동일 성능)
- 50% alignment 향상
- Multi-brain-tuning > Single-brain-tuning (특히 새 참여자)
- Brain-tuning이 downstream task 성능도 향상

**우리가 가져올 것:**
- Multi-participant brain-tuning 방법: Ch4에서 5명 → multi-subject 학습
- Data efficiency 결과: n=5의 한계를 극복하는 전략
- 일반화 검증 방법: LOSO CV 설계에 활용
- "brain data는 noise가 아닌 signal": Ch4 논거

**우리가 확장하는 것:**
- Moussa: generalization of brain alignment
  → 우리: generalization of emotion prediction

**포지셔닝:** Ch4의 multi-subject 전략 근거

---

### 8. Margulies et al. (2016) — *PNAS*
**"Situating the default-mode network along a principal gradient of macroscale cortical organization"**

**핵심 발견:**
- 피질의 principal gradient 발견
  (Gradient 1: unimodal sensory/motor → transmodal DMN)
- DMN이 gradient의 transmodal end에 위치
- 이 gradient가 피질 기능 조직화의 핵심 축

**우리가 가져올 것:**
- Principal gradient: Ch1-D, Ch3-C의 x축
- "unimodal → transmodal" 축: AI-unique 분포 예측
- DMN = transmodal end: AI-unique가 여기서 클 것
- 각 parcel의 gradient 위치값: 실제 분석에서 covariate로 사용

**우리가 확장하는 것:**
- Margulies는 구조적 gradient만 보임
  → 우리는 "이 gradient를 따라 감정 표상이
     지각적(AI-shared)에서 뇌 고유(AI-unique)로 변환된다"는
     기능적 해석 추가

**포지셔닝:** Ch3-C의 분석 프레임워크. 가장 강한 neuroscience 주장의 근거

---

### 9. Kragel & Ma (2026) — *Nature Communications*
**"Map-like representations of emotion knowledge in hippocampal-prefrontal systems"**

**핵심 발견:**
- Emo-FilM 데이터 사용 (n=29)
- 해마(Hippocampus)가 감정 개념을 hierarchical structure로 표상
- vmPFC가 valence-arousal 공간에서 위치를 추적 (grid-like code)
- 해마-vmPFC가 감정 knowledge를 map-like으로 표상
- TEM (Tolman-Eichenbaum Machine)으로 계산적 설명

**우리가 가져올 것:**
- Hippocampus + vmPFC를 ROI에 추가: Ch1-C, Ch3-B에 포함
- "해마 = 감정 개념의 위계적 표상" → AI-unique 영역 예측
- Emo-FilM 데이터 활용: 우리도 Ch1-3 재현에 Emo-FilM 사용
- TEM 연결: Ch3의 감정 조직화 해석에 이론적 배경

**우리가 확장하는 것:**
- Kragel: 해마-vmPFC의 map-like 표상 발견
  → 우리: 이 영역이 AI-unique 성분을 담는가?
  → "map-like 표상 = AI가 포착 못하는 고차 표상"?

**포지셔닝:** Ch3-B의 ROI 예측 근거 + Emo-FilM 활용 정당화

---

### 10. Kragel et al. (2019) — *Science Advances*
**"Emotion schemas are embedded in the human visual system"**

**핵심 발견:**
- EmoNet: AlexNet 기반 모델로 감정 카테고리 예측
- Visual system (CNN)이 감정 schema를 인코딩
- 시각 모델의 중간 레이어가 감정 관련 뇌 영역과 정렬
- 감정 schema가 visual system에 embedded되어 있음

**우리가 가져올 것:**
- "감정이 시각 모델에 embedded": AI-shared 성분의 근거
- Visual system이 감정을 인코딩: Ch2 motivation
  ("AI가 감정을 어느 정도 설명할 수 있다")
- EmoNet 방법론: Ch4의 비교 baseline으로 활용 가능

**우리가 확장하는 것:**
- Kragel: CNN이 감정 schema를 캡처
  → 우리: V-JEPA2가 더 풍부한 표상 + 뇌 고유 성분 분리
- Kragel: visual system에 embedded된 감정만 봄
  → 우리: visual system이 못 보는 감정(AI-unique)에 집중

**포지셔닝:** AI-shared 성분의 이론적 근거

---

### 11. Kragel et al. (2015) — *Social Cognitive and Affective Neuroscience*
**"Multivariate neural biomarkers of emotional states are categorically distinct"**

**핵심 발견:**
- fMRI 패턴이 감정 카테고리별로 구별됨
- Multivariate pattern analysis로 감정 분류 가능
- 감정 표상이 distributed pattern

**우리가 가져올 것:**
- "감정이 범주적으로 구별된다": Ch1의 cat > dim 논거
- Multivariate decoding 방법론: Ch1의 방법론 근거

**포지셔닝:** Ch1의 이론적 배경

---

### 12. DMN & Discrete Emotion (2019) — *Frontiers in Human Neuroscience*
**"The Default Mode Network's Role in Discrete Emotion"**

**핵심 발견:**
- DMN이 discrete emotion 처리에 관여
- 감정 경험 시 DMN 활성화
- DMN = 자기참조적 처리, 사회적 인지, 기억과 연결

**우리가 가져올 것:**
- DMN이 감정 처리에 관여: Ch3-B에서 AI-unique 영역 예측
- DMN = transmodal region: Margulies gradient와 연결
- "DMN이 discrete emotion에 특화": AI-unique가 범주적인 근거

**포지셔닝:** Ch3의 AI-unique ROI 예측 근거

---

### 13. Thieu et al. (2024) — *iScience*
**"Visual looming is a primitive for human emotion"**

**핵심 발견:**
- Looming (접근하는 물체)이 감정의 primitive
- Superior colliculus가 looming을 인코딩
- Shallow CNN (Drosophila 시각계 기반)이
  인간 infant의 defensive blinking과 adult의 arousal 예측
- 생존 관련 시각 자극 → 감정의 subcortical 경로

**우리가 가져올 것:**
- "단순 시각 특성이 감정 예측": AI-shared 성분의 예시
  (looming = purely perceptual → AI가 캡처 가능)
- Arousal이 perceptual primitive와 연결: AI-shared가 VA 편향 예측
- Subcortical (superior colliculus) vs cortical 경로:
  Ch3의 ROI 분석에서 subcortical 포함 근거

**포지셔닝:** AI-shared의 구체적 예시 + subcortical ROI 분석 근거

---

### 14. Khosla et al. (2021) — *Science Advances*
**"Cortical response to naturalistic stimuli is largely predictable with deep neural networks"**

**핵심 발견:**
- HCP 7T fMRI + movie watching
- DNN encoding model로 피질 반응의 대부분 예측
- 계층적 처리, 시간적 통합, 멀티모달 통합 반영 시 성능 향상
- STS, angular gyrus 등 멀티모달 영역에서도 예측 가능
- Encoding model이 high-level concept에 일반화

**우리가 가져올 것:**
- "피질이 DNN으로 예측 가능": AI-shared 성분 존재 근거
- HCP movie 데이터: Ch4 확장에서 사용
- ROI별 encoding 성능 차이: Ch1-C 방법론 참고
- "encoding model → high-level task 일반화":
  brain-tuning의 downstream 향상 예측 근거

**포지셔닝:** Ch2의 "AI가 뇌를 얼마나 설명하는가" baseline 연구

---

### 15. Fu et al. (2025) — *eLife*
**"Comprehensive Neural Representations of Naturalistic Stimuli through Multimodal Deep Learning"**

**핵심 발견:**
- VALOR (video-text alignment model)로 HCP fMRI 예측
- Unimodal (AlexNet, WordNet) < CLIP < VALOR 순서
- 멀티모달 + temporal = 더 좋은 뇌 예측
- Semantic dimension을 자동으로 매핑 (annotation 없이)
- Predictive coding gradient 발견 (미래 예측 시간 척도)

**우리가 가져올 것:**
- 멀티모달 temporal 모델이 best: V-JEPA2 선택 근거
- "semantic dimensions 자동 매핑": Ch1의 14 dim 분석 방향
- Predictive coding gradient: Ch3-D의 14 dim 분석에서 참조
- HCP + naturalistic fMRI 접근: Ch4 확장에서 활용

**우리가 확장하는 것:**
- Fu: encoding (자극→뇌), AI 성능 최대화
  → 우리: decoding (뇌→감정) + AI-unique 분리
- Fu: V-A 등 semantic dimension 자동 발견
  → 우리: 34 cat + 14 dim으로 명시적 감정 구조 분석

**포지셔닝:** 멀티모달 temporal 모델 우월성 근거 + HCP 활용 정당화

---

### 16. Sartzetaki et al. (2025) — *ICLR 2025*
**"One Hundred Neural Networks and Brains Watching Videos: Lessons from Alignment"**

**핵심 발견:**
- 99개 video/image model의 fMRI alignment 대규모 벤치마크
- Temporal modeling → early visual region alignment
- Action recognition task → late region alignment
- CNN vs Transformer: 층별 alignment 패턴 차이
- 계산 복잡도(FLOPs)와 alignment 음의 상관 (효율적 모델이 더 brain-like)

**우리가 가져올 것:**
- V-JEPA2 선택 근거: self-supervised video model이 temporal modeling 강함
- Temporal modeling이 초기 시각 영역에 중요:
  Ch1에서 early visual ROI 분석 시 video model 특성 고려
- 계산 효율 vs alignment: brain-tuning 모델 선택 시 고려
- 99개 모델 비교 결과: 우리의 다중 렌즈 선택 근거

**우리가 확장하는 것:**
- Sartzetaki: 뇌 alignment 비교 (alignment가 목적)
  → 우리: 감정 예측 (emotion decoding이 목적)
- Sartzetaki: emotion을 안 봄
  → 우리: emotion에 특화된 분석

**포지셔닝:** 모델 선택 근거 + 우리가 채우는 gap 설명

---

### 17. Layer-specific modulation (2022) — *NeuroImage*
**"Layer-specific, retinotopically-diffuse modulation in human visual cortex in response to viewing emotionally expressive faces"**

**핵심 발견:**
- 감정적 얼굴이 시각 피질의 layer-specific modulation 유발
- 초기 시각 피질에서도 감정 조절 신호 있음
- Retinotopic 구조와 무관한 diffuse modulation

**우리가 가져올 것:**
- 초기 시각 피질도 감정에 반응: Ch1 ROI 분석에서 V1/V2 포함 근거
- Feedback modulation의 존재: AI-unique가 V1에도 있을 수 있음
- Top-down emotion signal의 근거

**포지셔닝:** Ch1-C, Ch3-B에서 early visual ROI 분석 근거

---

### 18. Encoding in childhood/adolescence (2023)
**"Large-scale encoding of emotion concepts becomes increasingly similar between individuals from childhood to adolescence"**

**핵심 발견:**
- 감정 개념의 신경 인코딩이 청소년기 동안 개인 간 유사해짐
- 감정 표상의 발달적 변화

**우리가 가져올 것:**
- 감정 표상의 individual difference 측면: Ch4에서 개인차 분석 배경
- 감정 인코딩의 학습 의존성: brain-tuning의 이론적 배경

**포지셔닝:** Ch4의 개인차 분석 배경 + brain-tuning 정당화

---

### 19. VCA — Biologically Inspired DNN (2025) — *bioRxiv*
**"Biologically Inspired Deep Neural Network Models for Visual Emotion Processing"**

**핵심 발견:**
- CLIP-ViT + amygdala 모방 모듈 (LA, AB, B, CeA)
- IAPS 이미지에서 Valence r≈0.9, Arousal r≈0.7
- 학습 후 amygdala fMRI와 alignment 증가
- 해부학적 제약 + self-attention이 성능에 중요

**우리가 가져올 것:**
- amygdala ROI의 중요성: Ch1-C에 포함
- RSA 방법론으로 model-brain alignment 측정: 부분 차용
- VA 예측 baseline: Ch4의 비교 대상

**우리가 차별화하는 것:**
- VCA: image + amygdala only + VA + post-hoc alignment
  → 우리: video + 전뇌 + 34 cat + direct brain supervision

**포지셔닝:** Ch4의 비교 baseline

---

## 방법론: Decoding 방식 고민 및 결정

### 배경: 두 방식의 비교

우리 프로젝트에서 디코딩 방법론은 핵심 선택이다.
Horikawa (2020)의 방식과 우리 방식이 다르며,
각각 장단점이 있다.

---

### Horikawa (2020) 방식

```
방법: Pearson r + Video Identification
  - 각 감정 dimension의 decoded value vs true value → Pearson r
  - Video identification: N-way forced-choice classification
    (decoded brain pattern이 어느 비디오에서 왔는지 맞추기)
    정확도 = chance (1/N)보다 높은가?

질문: "뇌가 자극(비디오)을 감정적으로 구별할 수 있는가?"
방향: Brain → "어떤 자극?" (identification)
단위: trial-level (개별 시청 단위)

장점:
  - 직관적 해석 (N-way 맞추기 정확도)
  - 선행 연구와 직접 수치 비교 가능
  - 개별 trial 신호 활용

단점:
  - 반복 측정 많이 필요 (Horikawa: 5명 × 5회 반복)
  - 감정 강도의 연속적 변화 못 포착
  - AI-unique 분리(Variance Partitioning)에 부적합
  - Cat/VA ratio 계산 번거로움
```

---

### 우리 방식 (Ridge R²)

```
방법: Ridge Regression + Cross-Validation R²
  - fMRI features → emotion rating 예측
  - 5-fold CV R² (또는 Pearson r)

질문: "뇌에서 감정 강도를 읽을 수 있는가?"
방향: Brain → "감정이 얼마나?" (regression)
단위: stimulus-level (비디오 단위 평균)

장점:
  - 연속값 예측 → 감정 강도 포착
  - 34 cat + 14 dim 동시 분석
  - AI-unique 분리(Variance Partitioning)에 자연스러움
  - Cat/VA ratio 직접 계산
  - Ch2-4 전체에 일관된 framework

단점:
  - 선행 연구(Horikawa)와 직접 수치 비교 어려움
  - R² 절대값이 낮게 나올 수 있음
    (crowd-sourced rating noise + n=5 한계)
```

---

### 결정: 둘 다 쓰되 역할 분리

```
Ch1 (Horikawa 재현):
  Horikawa 방식 (Pearson r + identification) → 재현 figure
  Ridge R²                                   → 우리 방식 figure
  두 결과 일치 → "우리 방식도 valid" 방법론 정당화

Ch2-4 (우리 분석):
  Ridge R² 메인
  (Variance Partitioning은 Ridge 기반이므로 필수)
```

---

### 평가 Metric 체계 (전체)

단일 metric에 의존하지 않고 다층적으로 평가한다.

#### Tier 1: 핵심 Metric (모든 분석에 공통)

**① Ridge R² (5-fold CV)**
```
의미: 감정 강도 예측 분산 설명량
범위: 0 ~ 1 (음수는 0으로 clip)
용도: Ch1-4 전체 메인 metric
계산: 1 - SS_res / SS_tot (cross-validated)

주의: 절대값이 낮아도 의미있을 수 있음
  → noise ceiling으로 정규화 필요 (아래 참조)
```

**② Pearson r (5-fold CV)**
```
의미: 예측값-실제값 선형 상관
범위: -1 ~ 1
용도: Horikawa 방식과 직접 비교
장점: R²보다 직관적, 음수가 의미있음
```

**③ Spearman ρ (5-fold CV)**
```
의미: 예측값-실제값 순위 상관
범위: -1 ~ 1
용도: non-linear 관계 포착, outlier에 robust
특히 유용: 감정 rating이 skewed distribution일 때
```

#### Tier 2: 보완 Metric

**④ Noise Ceiling 비율 ★★ (중요)**
```
의미: "이론적 최대치 대비 몇 %를 달성했는가"
계산:
  Upper NC = 5명 평균 fMRI로 나머지 5명 평균 예측
             (모든 subject-level 분산 설명 가능)
  Lower NC = leave-one-out 방식으로 추정

정규화된 R² = R² / Upper_NC × 100 (%)

왜 중요한가:
  Raw R² = 0.05 → "낮다"
  NC = 0.07 → 정규화 R² = 71% → "이론적 최대의 71%"
  
  crowd-sourced rating noise, n=5 noise 등이
  Upper NC에 이미 반영되므로
  Raw R²보다 훨씬 의미있는 비교 가능

ROI별 비교:
  Amygdala NC vs STS NC가 다름
  → 정규화 없이 비교하면 NC 차이를 모델 성능 차이로 착각
  → 정규화 필수

참고: Horikawa (2020), Sartzetaki (2025) 동일 방식 사용
```

**⑤ AUC-ROC (이진 분류)**
```
의미: 감정 강도 상위 25% vs 하위 25% 구별
계산: 각 감정을 binary로 변환
      Ridge score → AUC
용도: 
  - 연속 R²가 낮은 감정도 이진으로는 구별 가능한지
  - 특히 Joy, Fear 등 희소 감정에 유용
    (데이터 극히 적어 regression 어려움)
  - Ch3에서 AI-unique 감정 목록 검증에 활용
```

**⑥ Video Identification (Horikawa 방식)**
```
의미: N-way forced-choice에서 정확도
계산: decoded pattern의 correlation이 
      자신의 비디오에서 가장 높은가?
용도: Ch1 Horikawa 재현 figure에서만 사용
참고: n=5, 10회 반복 필요 → Horikawa 데이터 직접 활용
```

#### Tier 3: 추가 분석용

**⑦ Balanced Accuracy / F1 (다중분류)**
```
용도: 34 cat 동시 예측 (multi-label)
특히: 불균형 레이블 (Joy 0%, Amusement 30%)에서 필요
```

**⑧ Hamming Loss**
```
용도: 34 cat multi-label 예측의 전체 오류율
```

---

### Metric별 챕터 활용 계획

| Metric | Ch1 | Ch2 | Ch3 | Ch4 |
|--------|-----|-----|-----|-----|
| Ridge R² | ✓ 메인 | ✓ 메인 | ✓ 메인 | ✓ 메인 |
| Pearson r | ✓ Horikawa 비교 | ✓ 보완 | ✓ 보완 | ✓ 보완 |
| Spearman ρ | ✓ 보완 | ✓ 보완 | — | ✓ 보완 |
| **Noise Ceiling 비율** | ✓✓ 핵심 | ✓✓ 핵심 | ✓✓ 핵심 | ✓ 참고 |
| AUC-ROC | ✓ 희소 감정 | ✓ AI-unique 검증 | ✓ 감정 목록 | ✓ 평가 |
| Video Identification | ✓ 재현 전용 | — | — | — |
| Balanced Acc / F1 | — | — | ✓ 클러스터 | ✓ 평가 |

---

### Noise Ceiling 계산 방법 (구체적)

```python
# Upper Noise Ceiling
def upper_noise_ceiling(fmri):
    # fmri: (n_subjects, n_videos, n_parcels)
    nc_scores = []
    for s in range(n_subjects):
        mean_all = fmri.mean(axis=0)  # 전체 평균
        r = pearsonr(mean_all.flatten(), fmri[s].flatten())
        nc_scores.append(r)
    return np.mean(nc_scores)

# Lower Noise Ceiling (LOO)
def lower_noise_ceiling(fmri):
    nc_scores = []
    for s in range(n_subjects):
        others = np.delete(fmri, s, axis=0).mean(axis=0)
        r = pearsonr(others.flatten(), fmri[s].flatten())
        nc_scores.append(r)
    return np.mean(nc_scores)

# 정규화
normalized_r2 = model_r2 / upper_nc * 100  # %
```

**해석 기준:**
```
정규화 R² > 80%: 거의 upper bound 달성
정규화 R² 50-80%: 좋은 성능
정규화 R² 20-50%: 중간
정규화 R² < 20%: 개선 여지 있음

ROI별로 NC가 다르므로 반드시 per-ROI 계산
```

---

### Cross-Validation 전략

**Primary: 5-fold CV (video-level split) — 모든 main result**
```
방법: 2196 비디오를 5개 fold로 분할
  - 같은 비디오가 train/test에 동시 들어가지 않도록
  - random seed 고정
  - 5명 평균 fMRI 사용 (group-level)

사용처:
  Ch1-4 모든 main analysis
  Ridge R², Pearson r, Spearman ρ, AUC-ROC 전부
```

**Secondary: Subject-level variability 보고 — 보조적**
```
방법: 5명 각각에서 동일 분석 반복
  → mean ± SEM 보고

⚠️ LOSO CV 한계 (n=5):
  문제:
    LOSO = train 4명, test 1명
    n=5로는 fold 5개뿐 → variance 추정 불안정
    inter-subject variability 크면 결과 매우 낮게 나옴
    일부 subject에서 음수 R² 가능

  결론:
    LOSO를 "일반화 능력 검증"으로 쓰지 않음
    대신 "subject variability 보고"로 framing 변경
    → "5명 각각에서도 일관된 패턴이 나오는가?"
    → main claim을 지지하는 보조 증거로만 사용

  진짜 일반화 검증:
    → Emo-FilM (n=30)에서 수행
       Horikawa로 학습 → Emo-FilM으로 테스트
       또는 반대 방향
    → n=30이면 LOSO도 의미 있음

사용처:
  Noise Ceiling 계산 (반드시 subject-level)
  ROI별 mean ± SEM 보고
  Cat/VA ratio의 individual consistency 확인
  결과의 stability 확인 (주장 강화용)
```

---

### 통계 검증

```
유의성 검증: Permutation test (n=1,000)
  - emotion label을 shuffle → null distribution
  - observed R² vs null → p-value
  - FDR correction (Benjamini-Hochberg, q < 0.05)

모델 간 비교:
  - Paired t-test (5명 × 34 감정)
  - Wilcoxon signed-rank test (non-parametric)
  - Bonferroni correction for multiple comparisons

Effect size:
  - Cohen's d
  - R² difference (absolute)
  - Noise ceiling 정규화 후 차이
```

---

### Individual Subject vs Group Average 기준

분석마다 어떤 수준의 fMRI를 사용하는지 명시한다.

```
Group-level (5명 평균):
  사용처:
    Ch1-A: 전체 뇌 디코딩 메인 분석
    Ch2:   Variance Partitioning 메인
    Ch3:   AI-unique 분포 지도 (피질 표면 매핑)
  이유:
    - noise 감소 (ISC 기반 공통 신호 추출)
    - 34 cat + 14 dim 디코딩에서 안정적
    - n=5의 한계를 일부 보완

Subject-level (5명 개별):
  사용처:
    Noise Ceiling 계산 (반드시 subject-level)
    LOSO CV (일반화 검증)
    Ch1-C ROI 분석 (subject variability 보고)
    Cat/VA ratio의 individual stability 검증
  이유:
    - NC는 inter-subject variability를 이용하므로 필수
    - 개인차 분석

명시 원칙:
  모든 figure/table에 "group-level" 또는 "subject-level" 표기
  subject-level 분석은 mean ± SEM 보고
```

---

### Encoding vs Decoding 방향 명확화

**두 방향이 Ch2에서 혼재하므로 명시적으로 구분한다.**

```
Encoding 방향 (자극 → 뇌):
  정의: AI model embedding으로 fMRI를 예측
  질문: "AI가 뇌 반응을 얼마나 설명하는가?"
  사용처:
    Ch2 Step 1: V-JEPA2 → fMRI (AI-shared 추출)
    Ch2 다중 렌즈: 각 AI model → fMRI
  방법: Ridge regression (V-JEPA2 → fMRI)
  산출물: predicted fMRI (AI-shared), residual fMRI (AI-unique)

Decoding 방향 (뇌 → 감정):
  정의: fMRI로 감정 레이블을 예측
  질문: "뇌에서 감정 정보를 읽을 수 있는가?"
  사용처:
    Ch1:    fMRI 전체 → 34 cat + 14 dim
    Ch2 Step 2: AI-unique residual → 34 cat + 14 dim
    Ch3:    AI-unique 성분 구조 분석
    Ch4:    brain-tuned model → emotion
  방법: Ridge regression (fMRI → emotion rating)
  산출물: R², Pearson r, Noise Ceiling 비율

Ch2의 두 단계:
  Step 1 (Encoding): V-JEPA2 → fMRI → residual 추출
  Step 2 (Decoding): residual → emotion → AI-unique 존재 확인
  → 이 두 단계를 논문에서 명시적으로 구분하여 기술
```

---

### RSA (Representational Similarity Analysis) 방법론

Horikawa (2020)의 핵심 방법론 중 하나.
Ridge decoding으로 놓치는 **표상의 기하학적 구조**를 포착.

**RSA의 역할:**

```
Ridge decoding: "뇌에서 감정 강도를 예측할 수 있는가?" (scalar)
RSA:           "뇌의 감정 표상 구조가 
                AI/행동 구조와 얼마나 닮았는가?" (geometry)

둘은 보완 관계:
  Ridge → 개별 감정의 예측력
  RSA   → 34 감정 전체의 표상 구조 유사성
```

**RSA 계산 방법:**

```
Step 1: RDM (Representational Dissimilarity Matrix) 구성
  Brain RDM:
    각 비디오 쌍의 fMRI 패턴 간 거리 (1 - Pearson r)
    크기: (2196 × 2196)
    
  AI RDM:
    각 비디오 쌍의 V-JEPA2 embedding 간 거리
    크기: (2196 × 2196)
    
  Emotion RDM:
    각 비디오 쌍의 34 cat rating 간 거리 (Euclidean)
    크기: (2196 × 2196)
    
  VA RDM:
    각 비디오 쌍의 VA rating 간 거리
    크기: (2196 × 2196)

Step 2: RDM 간 유사성 계산
  Spearman ρ between upper triangles of two RDMs
  → "Brain RDM이 AI RDM과 얼마나 닮았는가?"
  → "Brain RDM이 Emotion RDM과 AI RDM 중 어느 것과 더 닮았는가?"

Step 3: 통계 검증
  Permutation test on RDM entries
  Bonferroni correction
```

**RSA 활용 계획:**

```
Ch1:
  Brain RDM vs Emotion RDM (34 cat)
  Brain RDM vs VA RDM
  → Cat RSA > VA RSA? → Horikawa 재현
  ROI별 Brain RDM vs Emotion/VA RDM
  → 감정 구조가 어느 영역에서 가장 뚜렷?

Ch2:
  AI-shared fMRI RDM vs AI RDM vs Emotion RDM
  AI-unique fMRI RDM vs AI RDM vs Emotion RDM
  → AI-unique RDM이 Emotion RDM과 더 가까운가?
  → AI-unique RDM의 Cat/VA 편향

Ch3:
  AI-unique RDM의 클러스터 구조 (UMAP 시각화)
  → Horikawa의 27개 클러스터와 비교
  ROI별 AI-unique RDM vs Emotion RDM
  → transmodal에서 더 높은 RSA?

Ch4:
  Brain-tuned model의 RDM vs Brain RDM
  → brain-tuning 후 표상 구조가 뇌에 가까워졌는가?
```

**RSA의 장점 (Ridge 대비):**

```
1. 개별 감정 예측력이 아닌 전체 구조 포착
2. 34 감정의 관계 (클러스터, 연속성) 시각화 가능
3. UMAP으로 2D 감정 지도 생성 가능
4. Horikawa (2020)과 직접 방법론 비교
5. AI RDM, Brain RDM, Behavior RDM 삼각 비교
```

---

### 다중 AI 렌즈 임베딩 추출 계획

현재 보유: V-JEPA2 (2196, 1408), CLIP (2196, 512)
추가 필요: DINOv2, VideoMAE

```
공통 전처리 (Horikawa 비디오 기준):
  비디오: ~3초, ~5프레임
  해상도: 모델별 요구 해상도로 resize
  temporal: 전체 프레임 추출 후 mean pooling

V-JEPA2 (이미 있음):
  레이어: final hidden state
  temporal pooling: mean over tokens
  차원: 1408
  특징: self-supervised, video, no language

CLIP (이미 있음):
  레이어: visual encoder final layer
  temporal pooling: frame별 임베딩 → mean
  차원: 512
  특징: language-supervised, image-level

DINOv2 (추출 필요):
  모델: dinov2_vitg14 (largest)
  레이어: final [CLS] token
  temporal pooling: frame별 → mean
  차원: 1536
  특징: self-supervised, image, no language
  추출 시기: Ch2 시작 전 (5월)

VideoMAE (추출 필요):
  모델: VideoMAE-v2-giant (or large)
  레이어: final encoder output mean pooling
  temporal pooling: 내장
  차원: 1408 (giant)
  특징: self-supervised, video, masked autoencoding
  추출 시기: Ch2 시작 전 (5월)

다중 렌즈 해석 매트릭스:
  V-JEPA2 unique → CLIP도 unique:  언어로도 설명 안 됨 (진짜 뇌 고유)
  V-JEPA2 unique → CLIP shared:    언어/의미가 그 감정에 필요
  V-JEPA2 shared → DINOv2도 shared: 정적 시각으로 충분
  V-JEPA2 unique → VideoMAE shared: temporal 정보가 핵심
```

---

### 플랜 B: Ch2 전제 무너질 경우 (AI-unique R² ≈ 0)

**전제 실패 기준:**
```
AI-unique residual → 34 emotion 디코딩에서
모든 R² < 0.01 (Permutation test 비유의)
= "fMRI에서 V-JEPA2를 제거하면 감정 정보가 없다"
```

**플랜 B가 지지하는 것:**
```
Conwell (2025): "지각이 감정의 대부분을 설명한다"
Du (2025): "behavior-neural gap = 측정 방법론 문제"
→ 우리 결과가 이를 video + fMRI domain에서 재확인
```

**플랜 B 스토리라인:**

```
새 중심축:
"Self-supervised video model이 인간 뇌의 감정 표상 공간을
 대부분 설명하며, brain-tuning으로 나머지를 포착한다."

Ch1 (유지):
  Brain → Emotion 기준선
  ROI별 디코딩 지도
  → 동일하게 진행

Ch2 (수정):
  AI가 설명하는 부분 분석 (AI-unique 분리 대신)
  Brain-predictable subspace 분석으로 대체:
    V-JEPA2에서 뇌가 읽는 부분(PC1-6)의 감정 구조
    Cat/VA ratio = 1.68 → "공유 공간이 범주적"
    CCA로 뇌-AI 공유 구조의 풍부함 입증
    → 이미 보유한 결과 활용 가능

Ch3 (수정):
  "AI-unique의 정체"가 아닌
  "AI가 설명하는 뇌 공간의 감정 구조"로 전환:
    Brain-predictable subspace의 ROI별 분포
    → transmodal에서 brain-predictable이 더 범주적?
    Principal gradient × brain-predictable 강도
    뇌-AI 공유 차원의 Cat/VA ratio 구조

Ch4 (유지):
  Brain-tuning은 어차피 진행 가능
  "AI-unique를 전달"이 아닌
  "brain-predictable 공간을 강화"로 framing 변경:
    brain-tuned model → 감정 예측 향상?
    향상이 있으면: "뇌가 AI에 additional signal 제공"
    → 이것 자체가 "AI-unique가 0이 아님"의 약한 형태 evidence

새 주장:
  "V-JEPA2와 뇌가 공유하는 compact한 공간이
   감정을 범주적으로 인코딩하며,
   이 공유 공간을 활용한 brain-tuning이
   감정 예측을 향상시킨다."

플랜 B의 강점:
  - 이미 보유한 결과 (Cat/VA=1.68, CCA 27개)가 메인
  - Conwell, Du와 일관된 스토리
  - brain-tuning은 여전히 novelty

플랜 B의 약점:
  - "뇌 고유 정보" 주장이 없어짐
  - Du (2025)와 차별화가 약해짐
  - Neuroscience 기여가 줄어듦
```

**결정 트리:**
```
오늘 실험 결과
      ↓
AI-unique R² > 0.01?
  YES → 플랜 A (현재 청사진) 진행
  NO  →
      다중 렌즈로 재시도
      (CLIP, DINOv2로 residual 분석)
        ↓
      어떤 렌즈로도 R² ≈ 0?
        YES → 플랜 B로 피벗
        NO  → "V-JEPA2 specific AI-unique" 존재
              → 플랜 A 유지, 렌즈 특이성 추가
```

---

## Chapter 1: Brain → Emotion (기준선 확립)

### 핵심 질문
뇌가 감정을 얼마나, 어떻게, **어디서** 인코딩하는가?

### 방법

**1-A. 전체 뇌 디코딩**
```
Input:  Raw fMRI (450 Schaefer parcel, 5명 평균)
Output: 34 emotion categories + 14 affective dimensions
Method: Ridge regression, 5-fold CV + LOSO CV
Metric: R², Pearson r, Spearman ρ
```
*근거: Horikawa (2020) 재현, Cowen (2017) 레이블 체계*

**1-B. Cat vs VA 비교 (Cat/VA ratio)**
```
34 cat mean R²  vs  Valence/Arousal R²
→ Cat/VA ratio
→ Horikawa 재현: cat > dim 확인
→ 14 affective dimension 전체 분석 (확장)
```
*근거: Horikawa (2020), Cowen (2017)*

**1-C. ROI별 감정 디코딩 지도 ★**
```
Theory-driven ROIs:
  감각 처리:  V1, V2, V3, Auditory Cortex
  감정 핵심:  Amygdala, Anterior Insula, ACC, OFC
  고차 처리:  mPFC, vmPFC, STS, TPJ,
              Hippocampus, Angular Gyrus, DMN

각 ROI에서:
  (a) 감정별 디코딩 R²
  (b) Cat/VA ratio
  (c) Top 5 감정

산출물: 감정 × ROI 히트맵
```
*근거: Lindquist (2012), Kober (2008), Kragel & Ma (2026),
      DMN & Discrete Emotion (2019), Thieu (2024)*

**1-D. Principal Gradient와의 관계 ★**
```
각 parcel의 gradient 위치 vs 디코딩 성능
→ Cat/VA ratio가 gradient 축을 따라 변하는가?

Group-level: 450 parcel scatter plot
Subject-level: 5명 개별 → 일관성 확인

예상:
  unimodal: 낮은 R², VA 편향
  transmodal: 높은 R², 범주 편향
```
*근거: Margulies (2016), Horikawa (2020)*

**1-E. RSA (Horikawa 재현용)**
```
방법: Horikawa (2020)과 동일한 RSA 파이프라인
  Brain RDM vs Emotion (34 cat) RDM → Spearman ρ
  Brain RDM vs VA RDM               → Spearman ρ
  → ρ_cat > ρ_VA? (Horikawa 재현)

ROI별 RSA:
  각 ROI의 Brain RDM vs Emotion RDM
  → 어느 ROI가 감정 구조와 가장 유사?

UMAP 시각화:
  Brain RDM → 2D → Horikawa Figure 6 재현

단위:
  Group-level (5명 평균 fMRI) 메인
  Subject-level (개별) → Noise Ceiling 계산에 활용
```
*근거: Horikawa (2020), Kriegeskorte (2008)*

**Individual vs Group 기준 (Ch1 전체)**
```
Group-level (메인):
  1-A, 1-B, 1-C, 1-D, 1-E 모두 5명 평균 fMRI 사용
  → noise 감소, 안정적 디코딩
  → 모든 main result에 사용

Subject-level (보조):
  Noise Ceiling 계산: 반드시 개별 사용
  ROI 분석: mean ± SEM 보고 (stability 확인)
  RSA: 개별 RDM → NC 추정 + individual consistency
  
  ⚠️ LOSO는 "일반화 검증"이 아닌 "패턴 일관성 확인"으로만
     (n=5 한계 — 방법론 섹션 참조)
  진짜 일반화: Emo-FilM (n=30)에서 수행
```

### 기여
- Horikawa (2020) 완전 재현 (RSA + Video Identification)
- 14 affective dimension 확장 (기존 cat 위주에서)
- 감정별 × 영역별 디코딩 지도 (Ch3 비교 baseline)
- Principal gradient와 감정 표상 관계
- Noise Ceiling 정규화 도입 → ROI 간 공정 비교

---

## Chapter 2: AI 렌즈로 뇌 분해

### 핵심 질문
뇌의 감정 표상에서 AI가 설명하는 부분(지각적)과
못하는 부분(뇌 고유)을 분리할 수 있는가?

---

### 2-0. Motivation: Video-Brain Embedding Alignment

**Ch2 본분석(Variance Partitioning)에 앞서,
뇌와 AI의 관계를 세 가지 방식으로 먼저 조망한다.**

이 분석들은 "왜 Variance Partitioning이 필요한가"를 동기화하고,
이미 보유한 결과를 Ch2의 서두로 재활용한다.

```
세 분석의 관계:

분석               축 정의         질문                          결과
──────────────────────────────────────────────────────────────────
Forward PCA+Ridge  V-JEPA2 단독   "V-JEPA2 축 중 뇌가 읽는 것?" 6개 유의
Reverse PCA+Ridge  Brain 단독     "뇌 축 중 AI가 읽는 것?"      0개 유의
CCA                양쪽 공동      "공유 축은 무엇인가?"          88개 유의

→ Forward는 되고 Reverse는 안 된다 = 비대칭
→ "뇌가 AI를 읽지만, AI는 뇌를 못 읽는다"
→ AI가 뇌의 중요한 부분을 놓치고 있다
→ Variance Partitioning으로 그 부분을 분리해야 한다
```

**2-0A. Forward PCA+Ridge (이미 보유)**
```
방법:
  V-JEPA2 (2196, 1408) → PCA → 100 PCs
  Brain-JEPA / Raw fMRI → Ridge → V-JEPA2 PC_i 예측
  Permutation test (n=1000) + FDR correction

결과 (보유):
  Brain-JEPA 기준: PC1-3 유의 (R²=0.373, 0.075, 0.088)
  Raw fMRI 기준:   PC1-6 유의 (R²=0.354, 0.227, 0.307...)
  Cat/VA ratio of brain-pred subspace = 1.68 (Raw)

해석:
  V-JEPA2의 주요 분산 축 중 일부를 뇌가 읽을 수 있음
  그 brain-predictable 공간이 범주적으로 조직됨
  → "뇌가 V-JEPA2의 감정 관련 구조를 포착"

Raw fMRI 재실행 여부:
  Brain-JEPA 결과 이미 보유
  Raw fMRI 기준으로 재실행 권장 (더 강한 결과 예상)
  → 오늘 또는 이번 주
```
*근거: 기존 SJMOON 논문 결과 재활용, Conwell (2025)*

**2-0B. Reverse PCA+Ridge (이미 보유)**
```
방법:
  Brain-JEPA / Raw fMRI → PCA → 100 Brain PCs
  V-JEPA2 → Ridge → Brain PC_j 예측
  Permutation test + FDR correction

결과 (보유):
  Brain-JEPA 기준: 0개 유의 (모든 R²=0.000)
  Raw fMRI 기준:   0개 유의 (모든 R²=0.000)

해석:
  V-JEPA2가 뇌의 주요 분산 축을 전혀 예측 못함
  뇌의 분산 대부분 = 주의, 기억, 자기참조 등
  → V-JEPA2는 외부 자극만 봄 → 뇌 내적 처리 모름

Forward vs Reverse 비대칭:
  Forward:  뇌 → AI PC (유의)
  Reverse:  AI → 뇌 PC (비유의)
  → "뇌가 AI를 읽지만, AI는 뇌를 못 읽는다"
  → AI가 뇌의 본질적인 부분을 놓치고 있음
  → brain-tuning이 필요한 이유 (Ch4 motivation)
```
*근거: 기존 SJMOON 논문 결과 재활용*

**2-0C. CCA — 공유 공간의 구조 탐색 (재실행 필요)**
```
방법:
  V-JEPA2 (2196, 1408) → PCA(100) → (2196, 100)
  Raw fMRI (2196, 450) → PCA(100) → (2196, 100)
  CCA(100 components)
  Permutation test (n=1000) + FDR correction

  ⚠️ Brain embedding 선택:
    메인: Raw fMRI (450 parcel → PCA100)
          이유: task fMRI 신호 손실 없음
    비교: Brain-JEPA (이미 보유)
          이유: "resting-state FM이 공유 구조를 얼마나 보존?"

재실행 계획:
  오늘: Raw fMRI + V-JEPA2 CCA
  비교: 기존 Brain-JEPA CCA 결과와 대조
  소요 시간: ~30분

기존 결과 (Brain-JEPA 기준):
  유의 CC: 88/100 (r>0.3인 CC: 27개)
  CC1 r=0.774: Annoyance, Interest, Anxiety (불쾌/관심 축)
  CC2 r=0.679: Aesthetic appreciation, Excitement (미학/흥분 축)
  CC4 r=0.608: Uncomfortable, Sadness (불편/슬픔 축)
  CC8 r=0.494: Adoration, Awe (사랑/경외 축)
  CC9 r=0.460: Empathic pain, Nostalgia, Sympathy (공감 축)
  Cat/VA: PCA brain-pred(1.51) > CCA 전체(1.12)
  CC1 subject stability: 0.719 ± 0.013

핵심 분석:
  (1) CC별 감정 프로필 → 공유 축의 감정 의미
  (2) Cat/VA ratio of CCA space → 공유 공간도 범주적?
  (3) 27개 CC ≈ Cowen (2017) 27 범주 (suggestive)
  (4) Raw vs Brain-JEPA CCA 비교 → FM 신호 보존율

Forward/Reverse와의 관계:
  Forward brain-pred subspace (6 PCs, Cat/VA=1.68)
  vs CCA shared space (27 CCs, Cat/VA=1.12)
  → brain-pred가 더 범주적 → "뇌가 선택적으로 읽는 부분이 더 감정적"
```
*근거: Cowen (2017) SH-CCA, Horikawa (2020)*

**세 분석의 종합 해석 (Ch2 Motivation 결론):**
```
Forward:  뇌가 V-JEPA2에서 감정 관련 축을 선택적으로 읽음
Reverse:  AI는 뇌의 내적 처리를 전혀 못 읽음
CCA:      공유 공간이 ~27개 감정 축으로 조직됨

→ "뇌와 AI는 감정을 부분적으로 공유하지만
   뇌에는 AI가 접근 못하는 고유 영역이 있다"
→ 이 고유 영역을 Variance Partitioning으로 분리 (2-A~C)
→ 이 고유 영역을 AI에 전달 (Ch4 brain-tuning)
```

---

### 방법

**2-A. Step 1 — Encoding 방향: fMRI를 AI로 분해**
```
방향: AI embedding → fMRI (Encoding)
질문: "AI가 뇌 반응을 얼마나 설명하는가?"

방법: Banded Ridge Regression (Variance Partitioning)
  - V-JEPA2 embedding → fMRI 예측 (5-fold CV)
  - predicted fMRI = AI-shared 성분
  - residual fMRI  = AI-unique 성분 (= fMRI - predicted)
  - 통계적으로 엄밀한 독립 기여도 추정

산출물:
  fMRI_shared  (2196, 450): AI가 설명하는 성분
  fMRI_unique  (2196, 450): AI가 설명 못하는 성분
```
*근거: Horikawa (2020), Du (2023) 방법론*

**2-B. Step 2 — Decoding 방향: 세 성분에서 감정 예측**
```
방향: fMRI 성분 → emotion (Decoding)
질문: "각 성분이 감정 정보를 얼마나 담고 있는가?"

세 가지 input 비교:
  (A) fMRI 전체     → 34 cat + 14 dim  (Ch1 baseline)
  (B) fMRI_shared   → 34 cat + 14 dim  (지각적 감정)
  (C) fMRI_unique   → 34 cat + 14 dim  (뇌 고유 감정)

Metric: Ridge R², Pearson r, Noise Ceiling 비율, AUC-ROC
Cat/VA ratio 비교:
  (B) AI-shared → VA 편향 예상 (Conwell: 지각=차원적)
  (C) AI-unique → 범주 편향 예상 (Horikawa: 뇌=범주적)

⚠️ (C)의 R² > 0 이면: "뇌에 AI가 모르는 감정 정보 있음"
⚠️ (C)의 R² ≈ 0 이면: 플랜 B로 전환 (아래 참조)
```
*근거: Conwell (2025), Du (2025)*

**2-C. RSA 분석**
```
Brain RDM (full/shared/unique) vs Emotion RDM vs AI RDM
Spearman ρ between upper triangles

핵심 비교:
  Brain_unique RDM vs Emotion (34 cat) RDM
  Brain_unique RDM vs VA RDM
  → AI-unique 성분이 범주 구조를 갖는가?

삼각 비교:
  Brain RDM ↔ AI RDM:       뇌-AI 공유 구조
  Brain RDM ↔ Emotion RDM:  뇌-감정 구조
  AI RDM    ↔ Emotion RDM:  AI-감정 구조
```
*근거: Horikawa (2020) RSA 방법론, Kriegeskorte (2008)*

**2-D. CCA — AI-shared 공간의 구조 탐색 ★**
```
목적: Variance Partitioning(2-A~B)이 AI-unique에 집중한다면,
      CCA는 뇌-AI 공유 공간(AI-shared)의 내부 구조를 탐색

방법:
  V-JEPA2 (2196, 1408) → PCA(100) → (2196, 100)
  Raw fMRI (2196, 450) → PCA(100) → (2196, 100)
  CCA(100 components) → 양쪽에서 동시에 상관 최대화

  ⚠️ Brain embedding 선택:
    메인: Raw fMRI (450 parcel → PCA100)
          이유: task fMRI 신호 손실 없음, 감정 신호 최대 보존
    비교: Brain-JEPA (768 → PCA100)
          이유: Raw vs Foundation model 비교 → 부산물 contribution
          (Brain-JEPA가 공유 구조를 얼마나 보존하는가?)

  통계: Permutation test (n=1000) + FDR correction

이미 보유한 결과 (Brain-JEPA 기준):
  유의 CC: 88/100 (r > 0.3인 CC: 27개)
  CC1 r=0.774: Annoyance, Interest, Anxiety (불쾌/관심 축)
  CC2 r=0.679: Aesthetic appreciation, Excitement (미학/흥분 축)
  CC4 r=0.608: Uncomfortable, Sadness (불편/슬픔 축)
  CC8 r=0.494: Adoration, Awe (사랑/경외 축)
  CC9 r=0.460: Empathic pain, Nostalgia, Sympathy (공감 축)
  CC1 subject stability: 0.719 ± 0.013

→ Raw fMRI로 재실행 필요 (오늘 가능)

핵심 분석:
  (1) CC별 감정 프로필
      → 공유 공간이 어떤 감정 축으로 구성되는가?
  (2) Cat/VA ratio of CCA space
      → CCA 공유 공간도 범주적인가?
  (3) CCA 27개 CC ≈ Cowen (2017) 27 범주?
      → "뇌-AI 공유 차원 수 = 감정 범주 수" (suggestive)
  (4) Raw fMRI CCA vs Brain-JEPA CCA 비교
      → foundation model의 공유 구조 보존율

Ch3과의 연결:
  CCA CC별 감정 구조 vs AI-unique의 감정 구조 비교
  → "공유 공간에는 없고 AI-unique에만 있는 감정 축"
  → AI-unique의 정체를 더 선명하게 규명
```
*근거: Cowen (2017) SH-CCA 방법론, Horikawa (2020)*

**⏱️ CCA 실행 타이밍:**
```
오늘 (내일 발표 전):
  Raw fMRI + V-JEPA2 CCA 재실행
  (Brain-JEPA 버전은 이미 있으므로 Raw만 추가)
  → 내일 발표에서 "Raw fMRI 기반 CCA" 결과 보여줄 수 있음
  → 약 30분 소요 예상

Brain-JEPA CCA (이미 있음):
  기존 결과 그대로 비교군으로 사용

주의:
  CCA는 n=102(test set)이 아닌 전체 2196 비디오 사용
  → 결과의 의미와 CV 방식 명시 필요
```

**2-E. 다중 AI 렌즈**
```
렌즈 1: V-JEPA2  (self-supervised, video, no language)  [보유]
렌즈 2: CLIP     (language-supervised, image+text)      [보유]
렌즈 3: DINOv2   (self-supervised, image)               [추출 필요, 5월]
렌즈 4: VideoMAE (self-supervised, video, masked)       [추출 필요, 5월]

각 렌즈로 Step 1-2 반복 → AI-unique 비교
각 렌즈로 CCA 반복 → AI-shared 구조 비교

해석 매트릭스 (Variance Partitioning):
  V-JEPA2 unique & CLIP unique  → 진짜 뇌 고유
  V-JEPA2 unique & CLIP shared  → 언어/의미가 그 감정에 필요
  V-JEPA2 shared & DINOv2 unique→ temporal 정보가 핵심
  모든 렌즈 unique               → 어떤 AI도 못 보는 것

해석 매트릭스 (CCA):
  V-JEPA2 CCA > CLIP CCA (CC 수, r값)
  → V-JEPA2가 뇌와 더 풍부한 공유 구조?
  → 아니면 CLIP이 언어 덕분에 더 풍부?
```
*근거: Sartzetaki (2025), Conwell (2025), Fu (2025)*

### ⚠️ 전제 확인 및 오늘 실험 순서

```
오늘 실행 순서:

[1] AI-unique residual 분석 (20-30분) ← 최우선
    V-JEPA2 → Raw fMRI (5-fold CV) → residual
    residual → 34 emotion → R² 확인
    결과: 플랜 A or 플랜 B 결정

[2] Raw fMRI CCA 재실행 (30분) ← 오늘 가능
    Raw fMRI PCA100 + V-JEPA2 PCA100 → CCA
    CC별 감정 프로필 + Cat/VA ratio
    Brain-JEPA 결과와 비교

[3] 내일 발표 슬라이드 구성
    [1] 결과: AI-unique 존재 여부 → 플랜 A/B
    [2] 결과: Raw CCA vs Brain-JEPA CCA 비교
```

*Conwell (2025): 지각이 67% 설명 → 나머지가 AI-unique 후보*
*Du (2025): gap = 측정 문제? → 우리는 뇌 고유 정보로 반박*

---

## Chapter 3: AI-unique 성분의 정체 규명

### 핵심 질문
뇌 고유 감정 성분(???)은 **어디서 오고**,
**어떤 감정을 담으며**, **어떻게 조직되는가**?

### 방법

**3-A. 감정별 AI-unique 크기 (Decoding)**
```
입력: fMRI_unique (Ch2 Step 1 산출물)
방법: Ridge R² + Noise Ceiling 비율 + AUC-ROC
단위: Group-level (5명 평균) + Subject-level 검증

각 감정의 AI-unique R² 순위:
  예상 높을 것 (뇌가 필요한 감정):
    Empathic pain, Uncomfortable, Nostalgia,
    Sympathy, Guilt, Horror (사회적·내적 감정)
  예상 낮을 것 (지각으로 충분):
    Aesthetic appreciation, Excitement, Amusement

AUC-ROC 보완:
  Joy, Fear 등 희소 감정 (Ridge R² 불안정)에 적용
  상위 25% vs 하위 25% 이진 분류

산출물: "지각적 감정" vs "뇌 고유 감정" 분류표
        + Noise Ceiling 정규화 비율 포함
```
*근거: Kragel (2019), Conwell (2025), Cowen (2017)*

**3-B. RSA 구조 분석 ★★**
```
Ridge로 못 보는 표상의 기하학적 구조를 RSA로 포착

RDM 구성:
  Brain_unique RDM: fMRI_unique의 비디오 간 거리
  Emotion (cat) RDM: 34 cat rating의 비디오 간 거리
  VA RDM: Valence/Arousal의 비디오 간 거리
  AI RDM: V-JEPA2 embedding의 비디오 간 거리

핵심 비교 (Spearman ρ):
  Brain_unique RDM vs Emotion RDM  →  ρ_cat
  Brain_unique RDM vs VA RDM       →  ρ_VA
  → ρ_cat > ρ_VA? → AI-unique = 범주적 구조

삼각 비교:
  Brain RDM ↔ AI RDM:       뇌-AI 공유 구조
  Brain RDM ↔ Emotion RDM:  뇌-감정 구조 (전체)
  Unique RDM ↔ Emotion RDM: 뇌 고유-감정 구조

UMAP 시각화:
  Brain_unique RDM → 2D map
  → Horikawa (2020) Figure 6 방식으로 27개 클러스터 확인
  → AI-unique 공간에서도 범주 클러스터 나타나는가?

Group vs Subject:
  Group-level RDM (5명 평균) 메인
  Subject-level RDM (개별) → 일관성 확인
```
*근거: Horikawa (2020) RSA+UMAP, Kriegeskorte (2008), Cowen (2017)*

**3-C. 영역별 AI-unique 분포 ★★ (킥)**
```
Group-level 분석:
  각 ROI의 AI-unique R² / total R² = AI-unique 비율
  → 피질 표면에 매핑 (450 parcel)

Subject-level 검증:
  5명 개별 → mean ± SEM
  Paired t-test: transmodal ROI vs unimodal ROI

예상 패턴:
  V1, V2, V3:              AI-unique 비율 낮음 (~0%)
  Amygdala, Insula:        중간
  STS, TPJ, mPFC, Hippo:  AI-unique 비율 높음 (>50%?)

산출물: "AI가 설명 못하는 뇌 영역 지도"
  → ROI × 감정 히트맵 (AI-unique R²)
  → 피질 표면 컬러 맵
```
*근거: Horikawa (2020) transmodal, Margulies (2016),
      Kragel & Ma (2026), DMN & Discrete Emotion (2019)*

**3-D. Principal Gradient × AI-unique ★★**
```
Group-level:
  x축: 각 parcel의 gradient 1 위치 (unimodal→transmodal)
  y축: AI-unique R² 비율
  → scatter plot + linear fit (Pearson r + p-value)

Subject-level:
  5명 개별 scatter → 일관성 확인

Ch1-D와 통합:
  x축: gradient 위치
  y축 1: 전체 fMRI Cat/VA ratio (Ch1-D)
  y축 2: AI-unique R² 비율 (Ch3-D)
  → 두 지표가 gradient를 따라 함께 증가?

전체 프로젝트의 가장 강한 주장:
  "unimodal → 낮은 Cat/VA & 낮은 AI-unique (지각적·차원적)
   transmodal → 높은 Cat/VA & 높은 AI-unique (범주적·뇌 고유)
   이 변환이 피질의 principal gradient를 따라 연속적으로 일어난다"
```
*근거: Margulies (2016), Du (2023) DMN affective gradient*

**3-E. Cat/VA 구조 이중 검증 (Ridge + RSA)**
```
Ridge 방법:
  AI-unique Cat R² / VA R² = Cat/VA ratio
  AI-shared Cat R² / VA R² = Cat/VA ratio (비교)

RSA 방법:
  AI-unique RDM vs cat Emotion RDM → ρ_cat
  AI-unique RDM vs VA RDM          → ρ_VA
  ρ_cat / ρ_VA ratio

두 방법의 일치:
  Ridge Cat/VA > 1 && RSA ρ_cat/ρ_VA > 1
  → "방법론 무관하게 AI-unique = 범주적"
  → Barrett vs Cowen 논쟁에 강력한 증거

Subject-level: 5명 개별 → mean ± SEM
```
*근거: Cowen (2017), Horikawa (2020), Du (2023)*

**3-F. 14 Affective Dimension과의 관계**
```
AI-unique fMRI → 14 dim 각각 Ridge 예측
→ valence/arousal보다 높은 R²를 보이는 dimension?

예상:
  approach/avoidance, social relevance,
  cognitive appraisal, identity/self-relevance

Group-level 메인, Subject-level 검증
```
*근거: Cowen (2017) 14 dim 체계, Du (2023) 14 dim-뇌 관계*

**3-G. 다중 렌즈 × ROI 교차 분석**
```
각 렌즈(V-JEPA2, CLIP, DINOv2, VideoMAE)의
AI-unique가 큰 ROI 비교

렌즈 × ROI 매트릭스:
  모든 렌즈 unique인 ROI: 진짜 뇌 고유 영역
  V-JEPA2만 unique인 ROI: temporal 처리 특화
  CLIP shared인 ROI:      언어적 의미로 설명됨

Subject-level: 5명 개별 → 패턴 일관성 확인
```

### Figure 구성 (Ch3)
```
Figure 3A: 감정별 AI-unique R² + Noise Ceiling 비율
           (지각적 감정 vs 뇌 고유 감정 분류표)
Figure 3B: AI-unique RDM UMAP 시각화
           (Horikawa 방식 차용, 27개 클러스터 비교)
Figure 3C: 피질 표면의 AI-unique 비율 지도 ← 킥 figure
           (Group-level + Subject-level SEM)
Figure 3D: Principal gradient × AI-unique scatter
           + Ch1-D Cat/VA 결과 통합 (두 패널)
Figure 3E: AI-shared vs AI-unique Cat/VA ratio
           (Ridge + RSA 두 방법 동시 검증)
Figure 3F: 렌즈 × ROI 교차 분석 히트맵
```

### 핵심 주장
```
"감정의 지각적 성분(AI-shared)은
 unimodal cortex에서 차원적으로 표상되고 (Barrett 지지),
 뇌 고유 성분(AI-unique)은
 transmodal cortex에서 범주적으로 표상된다 (Cowen 지지).
 이 변환은 피질의 principal gradient를 따라 연속적으로 일어난다."
```

---

## Chapter 4: 감정 예측 모델

### 방향 A: Brain-tuning

**방법 A-1: Moussa 방식 (LoRA fine-tuning)**
```
V-JEPA2 → LoRA fine-tune with fMRI loss
```
*근거: Moussa (2025 ICLR, 2025 NeurIPS)*

**방법 A-2: LLM Token Space**
```
fMRI → Transformer + VQ → LLM tokens
V-JEPA2 → 같은 LLM space
```
*근거: fMRI-LM (문서 내 언급), Moussa (2025)*

**핵심 검증:**
```
Ch3 AI-unique 큰 감정 → brain-tuning 향상폭 클 것
→ 상관관계 분석
```
*근거: Moussa (2025 ICLR) "brain-tuning → semantic 향상"*

### 방향 B: Brain+Video → Emotion

**Brain Foundation Model 비교**
| 모델 | 학습 | 역할 |
|------|------|------|
| Raw fMRI | — | **메인** |
| Brain-JEPA | Resting-state | 비교군 (신호 손실 한계) |
| SWIFT | Naturalistic task | 비교군 |
| NeuroStorm | 대규모 fMRI | 비교군 |
| fMRI-LM | Resting+task | **방향 A-2 핵심** |
| BrainLM | 다양한 task | 비교군 |
| BrainMT | Multi-task | 비교군 |

**결합 모델:**
```
Brain FM output + V-JEPA2 → Emotion
→ Ch3 AI-unique 영역에서 Brain 기여가 클 것
```
*근거: Khosla (2021) multimodal > unimodal,
      Fu (2025) VALOR > CLIP,
      Kragel & Ma (2026) 해마-vmPFC 기여*

---

## 기존 분석 결과 재포지셔닝

| 기존 분석 | 수치 | 새 역할 | 챕터 | 비고 |
|----------|------|---------|------|------|
| Raw fMRI Cat/VA=1.68 | — | Main result | Ch1 | Horikawa (2020) |
| **Forward PCA+Ridge (Brain-JEPA)** | PC1-3 유의, R²=0.373 | Ch2-0A motivation 비교군 | **Ch2-0A** | 기존 보유 |
| **Forward PCA+Ridge (Raw fMRI)** | PC1-6 유의 | **Ch2-0A motivation 메인** | **Ch2-0A** | 재실행 권장 |
| **Reverse PCA+Ridge (둘 다)** | R²=0.000 전부 | Ch2-0B: AI가 뇌를 못 읽음 | **Ch2-0B + Ch4** | 기존 보유 |
| **CCA 88개 CC (Brain-JEPA)** | CC1 r=0.774 | Ch2-0C AI-shared 구조 비교군 | **Ch2-0C** | 기존 보유 |
| **CCA Raw fMRI (재실행)** | 오늘 결과 | **Ch2-0C AI-shared 구조 메인** | **Ch2-0C** | 오늘 실행 |
| **CCA 27개 CC ≈ Cowen 27 범주** | r>0.3 | 공유 차원 수 = 감정 범주 수 | **Ch2-0C** | suggestive |
| **Forward brain-pred Cat/VA** | 1.68 > CCA 1.12 | brain-pred가 더 범주적 | **Ch2-0** | — |
| AV regress out 97.6% | — | 범주 ≠ VA → Ch3 근거 | Ch3 | 기존 보유 |
| V-JEPA2 vs CLIP | 3 vs 6 PCs | 다중 렌즈 근거 | Ch2 | 기존 보유 |
| Brain-JEPA vs Raw | 절반 손실 | FM 한계 → Raw 메인 근거 | Ch2 | 기존 보유 |

**Forward/Reverse/CCA 삼각 구조의 Ch2 내 서사:**
```
2-0A Forward:  "뇌가 AI의 감정 축을 선택적으로 읽는다" (동기)
2-0B Reverse:  "AI는 뇌를 전혀 못 읽는다" (비대칭 확인)
2-0C CCA:      "공유 공간이 ~27개 감정 축으로 구성된다" (구조 탐색)
     ↓
2-A~C VP:      "AI-unique 성분을 통계적으로 분리한다" (본분석)

이 순서로 논문/발표 서사 구성:
  "뇌와 AI가 비대칭적 관계를 갖는다
   → 공유하는 부분이 있지만 (CCA)
   → AI가 못 보는 부분도 있다 (Forward 비대칭)
   → 그 부분을 정확히 분리하면 (VP)
   → 뭔지 알 수 있다 (Ch3)"
```

---

## 데이터 역할 분담

| 데이터셋 | n | 자극 | 레이블 | 역할 | 근거 |
|---------|---|------|--------|------|------|
| **Horikawa (2020)** | 5 | 2,196 비디오 (~3초) | 34 cat + 14 dim (crowd) | **Ch1-4 전체** | Horikawa (2020) |
| **Emo-FilM (2025)** | 30 | 14 단편영화 (2.5시간) | 50 항목 (본인) | Ch1-3 재현·확장 | Kragel & Ma (2026) |
| **ReelMo (2025)** | 20 | Jojo Rabbit (2시간) | 20 cat (moment) | Ch3 시간 역학 | — |
| **HCP-movie** | 176 | 영화 클립 (1시간) | 없음 (LLM 생성) | Ch4 개인차 | Khosla (2021), Fu (2025) |

---

## 포지셔닝 요약

| 연구 | 우리와의 관계 | 우리가 가져오는 것 | 우리가 넘어서는 것 |
|------|-------------|-----------------|-----------------|
| Horikawa (2020) | 재현 + 확장 | 데이터, cat>dim, transmodal | AI 렌즈, AI-unique |
| Cowen (2017) | 프레임워크 | 34cat+14dim, 27범주 | 뇌에서 검증 |
| Du (2023) | 선행 + 비교 | affective space, 14dim | AI 렌즈로 분해 |
| Du (2025) | 반론 대상 | gap 개념, MLLM 결과 | AI-unique 존재 |
| Conwell (2025) | motivation | 지각이 67% 설명 | 나머지 33% 규명 |
| Moussa (2025 ICLR) | 방법론 선례 | brain-tuning 파이프라인 | emotion 도메인 |
| Moussa (2025 NeurIPS) | 방법론 확장 | multi-participant 전략 | emotion 도메인 |
| Margulies (2016) | 분석 프레임 | principal gradient | 기능적 해석 추가 |
| Kragel & Ma (2026) | ROI 근거 | 해마-vmPFC, Emo-FilM | AI-unique 연결 |
| Kragel (2019) | AI-shared 근거 | emotion in visual system | AI-unique 분리 |
| Sartzetaki (2025) | 모델 선택 근거 | video model 벤치마크 | emotion 특화 |
| Khosla (2021) | 방법론 참고 | encoding model, ROI | decoding + emotion |
| Fu (2025) | 모델 선택 근거 | multimodal > unimodal | emotion 특화 |
| Thieu (2024) | AI-shared 예시 | looming = perceptual primitive | 범주 감정 확장 |
| VCA (2025) | 비교 baseline | amygdala, VA | 전뇌, 34cat, brain-tuning |

---

## 최우선 실험 (오늘)

```python
# Raw fMRI AI-unique residual 분석
fmri_predicted = cross_val_predict(Ridge(), vjepa2, fmri_mean)
fmri_residual  = fmri_mean - fmri_predicted

for version in [fmri_mean, fmri_predicted, fmri_residual]:
    r2 = cross_val_score(Ridge(), version, emotion_ratings)

# R² > 0.01 → 청사진 진행
# R² ≈ 0    → 스토리 수정
```

---

## Future Plan: External Dataset 확장

핵심 원칙: **Horikawa가 메인. 외부 데이터는 재현·확장·검증.**
각 데이터셋은 Horikawa의 특정 한계를 보완하거나
새로운 분석 차원을 추가하는 역할을 한다.

---

### 데이터셋 전체 개요

```
                    Video    Image    n      감정 레이블          fMRI 품질    주요 가치
────────────────────────────────────────────────────────────────────────────────────────
Horikawa (2020)     ✓        ✗       5      34cat+14dim(crowd)   3T          메인, 감정 특화
Emo-FilM (2025)     ✓        ✗       30     50항목(본인rating)    3T          n↑, 본인rating
ReelMo (2025)       ✓        ✗       20     20cat(moment)        3T          시간 역학
HCP-movie           ✓        ✗       176    없음(LLM생성가능)     7T          규모, 개인차
THINGS-fMRI         ✗        ✓       3      없음(LLM생성가능)     3T          대규모 image
NSD                 ✗        ✓       8      VA(LLM생성가능)      7T          초고밀도 image
IAPS-fMRI           ✗        ✓       56     VA (3조건)           3T          표준 자극, n↑
Algonauts 2023      ✗        ✓       8      없음                  7T          벤치마크, NSD 기반
```

---

### 1. Emo-FilM (2025)

| 항목 | 내용 |
|------|------|
| 참여자 | 30명 (fMRI) + 44명 (independent rater) |
| 자극 | 14개 단편 영화, 총 2.5시간 |
| fMRI | 3T, whole-brain, resting-state 포함 |
| 감정 레이블 | 50항목: discrete emotions + appraisal + motivation + expression + feeling |
| 특징 | **fMRI 참여자 본인이 직접 rating** (crowd-sourced 아님) |
| 추가 데이터 | physiological (ECG, GSR) |
| 공개 | https://github.com/MIPLabCH/Emo-FilM |

**Horikawa 대비 보완점:**
```
n: 5 → 30 (6배)
자극 길이: ~3초 → 2.5시간 (narrative context)
rating: crowd-sourced → 본인 직접
감정 수: 34 → 50 (appraisal, motivation 포함)
physiological data 추가
```

**활용 계획:**
- **Ch1-3 재현:** 동일 분석을 Emo-FilM에서 반복
  → Horikawa 결과가 데이터셋에 무관하게 robust한지 검증
- **Ch2 핵심 활용:** crowd-sourced vs 본인 rating 비교
  → Du (2025)의 "gap = 측정 문제" 주장 직접 검증
  → 본인 rating에서 AI-unique가 더 작아지는가?
    (Yes → Du 지지 / No → 우리 주장 지지)
- **Ch3:** appraisal, motivation dimension이 AI-unique와 관련?
- **Ch4:** n=30으로 brain-tuning 학습 데이터 확장
  → Horikawa n=5 한계 극복
- **Kragel & Ma (2026)와 연결:** 동일 데이터셋 사용

**우선순위:** 높음 (Ch2 핵심 검증에 필수)

---

### 2. ReelMo (2025)

| 항목 | 내용 |
|------|------|
| 참여자 | 20명 (fMRI) + 161명 (행동, 60편 영화) |
| 자극 | fMRI: Jojo Rabbit 풀타임 (2시간), 행동: 60편 영화 |
| fMRI | 3T, 40시간 분량 |
| 감정 레이블 | 20개 감정, **moment-by-moment** rating (연속 시계열) |
| 특징 | 유일하게 풀타임 영화 + 시간 연속 annotation |
| 공개 | https://www.nature.com/articles/s41597-025-05159-6 |

**고유 가치 (다른 데이터셋에 없는 것):**
```
moment-by-moment 감정 annotation → 시간 역학 분석 가능
감정 전환점 분석
내러티브 효과 분석 (감정이 이야기 맥락에 따라 변하는가?)
```

**활용 계획:**
- **Ch3 확장:** AI-unique 성분이 감정 전환 시점에서 더 큰가?
  → "예측하지 못한 감정 변화 = 뇌 고유 처리"
- **Ch3 temporal 분석:** AI-unique R²가 자극 시작 후 시간이 지남에 따라 변하는가?
  → "내러티브가 쌓일수록 뇌 고유 성분이 증가"
- **Ch4B:** moment-by-moment fMRI + video → 연속 감정 예측
  → 감정 예측 모델의 temporal 일반화 검증
- V-JEPA2의 temporal modeling이 ReelMo에서도 AI-shared를 잘 설명하는가?

**우선순위:** 중간 (Ch3 확장, temporal dynamics)

---

### 3. HCP Movie-Watching

| 항목 | 내용 |
|------|------|
| 참여자 | **176명** |
| 자극 | 영화 클립 (독립 + 할리우드), 1-4.3분, 총 ~1시간 |
| fMRI | **7T** (고해상도, 2mm isotropic) |
| 감정 레이블 | **없음** (NEO-FFI 성격, 인지 능력 등 trait만) |
| 추가 데이터 | 다양한 행동/인지 검사 (HCP battery) |
| 공개 | https://github.com/datalad-datasets/hcp_movies |

**고유 가치:**
```
n=176 → 개인차 분석 (다른 데이터셋은 n≤30)
7T → 공간 해상도 최고 (ROI 분석 정밀도 향상)
HCP battery → 성격, 인지, 감정 trait과 연결 가능
```

**활용 계획:**
- **감정 레이블 생성:** LLM (GPT-4, Qwen2-VL)으로
  각 영화 클립의 감정 annotation 자동 생성
  → Du (2025) 방식 차용
- **Ch4B 확장:** n=176으로 Brain+Video 결합 모델 학습
  → 대규모 학습으로 성능 상한 탐색
- **개인차 분석:** AI-unique 성분이 개인차 (성격, 인지)와 연결?
  → "뇌 고유 감정 = 개인적 경험 반영"
- **7T ROI 분석:** Ch3의 ROI 분석을 7T 고해상도로 재현
  → Amygdala subregion 수준의 분석 가능
- **Brain Foundation Model 학습:** 대규모 데이터로 brain representation 품질 향상
- Khosla (2021), Fu (2025)와 동일 데이터셋 → 직접 비교 가능

**우선순위:** 중간 (Ch4 확장, 개인차)

---

### 4. THINGS-fMRI

| 항목 | 내용 |
|------|------|
| 참여자 | 3명 |
| 자극 | **22,248장** THINGS 객체 이미지 (1,854 concept × 12) |
| fMRI | 3T, 전뇌 |
| 감정 레이블 | **없음** (LLM으로 생성 가능) |
| 추가 데이터 | THINGS behavior (similarity judgment), MEG |
| 공개 | https://things-initiative.org |

**고유 가치:**
```
가장 넓은 object concept 커버리지 (1,854개 개념)
THINGS behavior dataset과 연결 (similarity structure)
MEG data 있음 → 시간 해상도 분석 가능
image 데이터 → video와 비교 가능
```

**활용 계획:**
- **Image vs Video 비교 (Ch2):**
  THINGS image fMRI vs Horikawa video fMRI에서
  AI-unique 패턴이 다른가?
  → "video만의 뇌 고유 성분이 있는가?"
- **Object-emotion 관계 (Ch3):**
  특정 객체 카테고리에서 AI-unique가 큰가?
  → "뱀, 얼굴 등 진화적 자극 → AI-unique 높을 것" (Thieu 2024 연결)
- **DINOv2 렌즈 검증:**
  THINGS는 DINOv2가 잘 설명하는 데이터셋
  → Ch2 다중 렌즈 비교에서 DINOv2의 설명력 기준점
- **MEG 활용:** 감정 처리의 시간 역학 분석
  → fMRI의 낮은 시간 해상도 한계 보완

**우선순위:** 낮음-중간 (image vs video 비교, MEG 분석)

---

### 5. NSD (Natural Scenes Dataset)

| 항목 | 내용 |
|------|------|
| 참여자 | **8명** |
| 자극 | **73,000장** COCO 이미지 (각 참여자 10,000장, 1,000장 공유) |
| fMRI | **7T**, 30-40 세션/참여자 |
| 감정 레이블 | **VA annotation 있음** (COCO 기반) |
| 추가 데이터 | CLIP, DINO 등 다양한 model embedding 제공 |
| 공개 | https://naturalscenesdataset.org |

**고유 가치:**
```
초고밀도 (73,000 자극) → 뇌 표상 공간을 조밀하게 샘플링
7T + 반복 측정 → 신호 품질 최고
VA annotation 있음 → 직접 활용 가능
Algonauts 2023 기반 데이터셋 → 기존 벤치마크와 비교
다양한 AI model embedding 이미 제공 → 우리 분석 바로 적용
```

**활용 계획:**
- **Ch2 Image 버전:**
  NSD fMRI에서 AI-shared / AI-unique 분리
  → Horikawa (video)와 NSD (image) 비교
  → "video에서만 나타나는 AI-unique가 있는가?"
- **VA annotation 활용:**
  NSD의 VA로 Ch1-B (Cat/VA ratio)를 image domain에서 검증
  → image에서도 AI-unique가 범주 편향?
- **AI model embedding 활용:**
  NSD가 이미 제공하는 CLIP, DINO 등 embedding → 다중 렌즈 분석 바로 가능
- **Cross-modal 일반화 (Ch4):**
  Horikawa로 brain-tuned model이 NSD image에서도 감정 예측 향상?
  → brain-tuning의 cross-modal 일반화 검증
- **Conwell (2025)과 직접 연결:**
  Conwell이 NSD 계열 image 사용 → 우리 결과와 직접 비교

**우선순위:** 중간 (image vs video 비교, cross-modal)

---

### 6. IAPS-fMRI (Hsiao et al. 2024)

| 항목 | 내용 |
|------|------|
| 참여자 | **56명** |
| 자극 | 90 IAPS 이미지 |
| fMRI | 3T |
| 감정 레이블 | VA (positive / negative / neutral 3조건) |
| 특징 | 표준화된 자극 (수십 년간 감정 연구에 사용) |
| 공개 | https://neurovault.org/collections/16284/ |

**고유 가치:**
```
n=56 → 통계적 파워 높음
IAPS = 감정 연구 gold standard 자극
VA annotation 있음 (3조건이지만)
VCA (2025) 논문과 동일 자극 → 직접 비교
```

**활용 계획:**
- **Ch1 Image baseline:**
  56명 IAPS fMRI에서 VA 디코딩 → 통계적으로 강건한 결과
- **VCA (2025)와 비교 (Ch4):**
  VCA가 IAPS에서 Valence r≈0.9, Arousal r≈0.7 달성
  → 우리 Brain+Video 결합 모델과 직접 비교
- **Image vs Video (Ch2):**
  IAPS image AI-unique vs Horikawa video AI-unique
  → static vs dynamic 자극에서 AI-unique 차이?
- **n=56 활용:** small-sample (n=5) 한계를 image domain에서 보완

**우선순위:** 낮음-중간 (VCA 비교, image baseline)

---

### 7. Algonauts 2023

| 항목 | 내용 |
|------|------|
| 참여자 | 8명 (NSD와 동일) |
| 자극 | NSD 이미지 subset (training: 8,859, test: 395) |
| fMRI | 7T (NSD 데이터) |
| 감정 레이블 | **없음** (object/scene recognition 태스크) |
| 특징 | 공식 벤치마크 챌린지, 표준화된 평가 프로토콜 |
| 공개 | http://algonauts.csail.mit.edu |

**고유 가치:**
```
표준화된 벤치마크 → 다른 연구와 직접 비교 가능
NSD 기반 → NSD 활용과 시너지
챌린지 leaderboard → 모델 성능 객관적 비교
brain alignment 평가 메트릭 표준화
```

**활용 계획:**
- **Ch4 Brain+Video 모델 벤치마크:**
  Algonauts 2023 test set에서 brain alignment 평가
  → 우리 모델이 기존 submission과 비교해서 어느 수준?
  → emotion에 특화된 표상이 general brain alignment도 향상?
- **Brain-tuning 효과 검증 (Ch4A):**
  brain-tuned V-JEPA2의 Algonauts 점수 변화
  → "emotion에 특화된 brain-tuning이 general alignment도 향상"
  → Moussa (2025)의 "downstream 향상" 결과를 vision domain에서 재현
- **메서드 비교:**
  Algonauts 상위권 방법들과 우리 방법 비교
  → 우리 contribution의 객관적 위치 확인

**우선순위:** 중간 (모델 벤치마킹, 객관적 평가)

---

### 데이터셋 역할 분담 요약

```
핵심 (지금 해야 함):
  Horikawa    → Ch1-4 전체 메인

우선순위 높음 (Ch2 검증에 필요):
  Emo-FilM    → n↑, 본인 rating, Ch2 Du 반박 검증

우선순위 중간 (Ch3-4 확장):
  ReelMo      → 시간 역학, 감정 전환
  HCP-movie   → n=176 개인차, 7T, Ch4 확장
  NSD         → image vs video, cross-modal 일반화
  Algonauts   → 벤치마크, 객관적 평가

우선순위 낮음 (특수 분석):
  THINGS      → image vs video, MEG, object-emotion
  IAPS-fMRI   → VCA 비교, image baseline, n=56
```

---

### 데이터셋별 핵심 분석 매트릭스

| 분석 | Horikawa | Emo-FilM | ReelMo | HCP | NSD | IAPS | THINGS | Algonauts |
|------|---------|---------|--------|-----|-----|------|--------|-----------|
| Ch1 Brain→Emotion | **메인** | 재현 | 재현 | LLM레이블 | VA만 | VA만 | LLM레이블 | — |
| Ch2 AI-unique 분리 | **메인** | Du 반박 | — | — | image 비교 | image 비교 | image 비교 | — |
| Ch3 ROI × unique | **메인** | 재현 | temporal | 7T ROI | image ROI | — | MEG timing | — |
| Ch4A Brain-tuning | 학습 | 학습(n↑) | — | 학습(n↑) | cross-modal | — | — | 벤치마크 |
| Ch4B Brain+Video | **메인** | n↑ 검증 | temporal | n=176 | image 버전 | VCA 비교 | — | 벤치마크 |
| Video vs Image | — | — | — | — | **비교** | **비교** | **비교** | — |
| 개인차 | — | 일부 | — | **메인** | — | — | — | — |
| 시간 역학 | — | — | **메인** | — | — | — | MEG | — |

---

## Future Plan: Brain Foundation Model 발전 방향

### 현재 상황과 한계

```
현재 사용: Brain-JEPA (resting-state fMRI로 학습)
  - UK Biobank resting-state data로 pretraining
  - checkpoint weight 직접 사용 (fine-tune 없음)
  - 문제: task fMRI 신호를 절반 이상 손실
           감정 관련 신호가 resting-state에 약함
  - 결과: CCA에서 비교군으로만 사용 가능
           Raw fMRI가 메인이어야 하는 이유

현재 strategy:
  Raw fMRI (450 parcel) → 메인
  Brain-JEPA embedding → 비교군 (신호 보존율 측정)
```

---

### 단계적 발전 방향

**Step 1 (현재): Raw fMRI 메인**
```
Raw fMRI (450 Schaefer parcel) 직접 사용
→ 신호 손실 없음
→ 감정 정보 최대 보존
→ 이것이 모든 분석의 gold standard
```

**Step 2 (중기 Future): Task-Pretrained Brain FM**
```
문제의식:
  Brain-JEPA는 resting-state 학습 → 감정 task 신호 약함
  다른 Brain FM들도 대부분 resting-state or 일반 task

해결:
  Naturalistic task fMRI로 pretrain된 모델 활용
  또는 기존 모델을 Horikawa / Emo-FilM으로 fine-tune

후보 모델:
  SWIFT (naturalistic task 포함 학습)
  BrainSN (resting + naturalistic 1,256h)
  TRIBE v2 (naturalistic task 451h)
  → 이들이 Raw fMRI보다 나은가?

평가 방법:
  동일 CCA / Variance Partitioning 파이프라인에서
  Raw fMRI vs 각 Foundation Model 비교
  → "task fMRI로 학습한 FM이 감정 신호를 더 잘 보존하는가?"
  → 이것 자체가 brain FM 비교 contribution
```

**Step 3 (장기 Future): Emotion Fine-tuned Brain FM**
```
아이디어:
  기존 Brain FM (Brain-JEPA, BrainSN 등)을
  감정 레이블이 있는 fMRI 데이터로 fine-tune

데이터:
  Horikawa (n=5, 34 cat) + Emo-FilM (n=30, 50 항목)
  → 합쳐서 multi-dataset fine-tuning

방법:
  Option A: Supervised fine-tuning
    Brain FM → emotion prediction head → 34 cat loss
  Option B: Contrastive fine-tuning
    Brain FM embedding vs emotion rating embedding
    → InfoNCE loss
  Option C: Brain-tuning 방식 (Moussa)
    V-JEPA2를 fMRI로 fine-tune한 것처럼
    Brain FM을 emotion label로 fine-tune

기대 효과:
  emotion fine-tuned FM → 감정 관련 뇌 신호에 특화
  → CCA에서 더 많은 감정 축 발견
  → Ch4B Brain+Video에서 더 강력한 brain representation
```

**Step 4 (long-term vision): Emotion Brain Foundation Model**
```
최종 목표:
  "Emotion Brain Foundation Model"
  = 감정 처리에 특화된 뇌 표상 학습 모델

특성:
  Input: fMRI (임의의 참여자, 임의의 감정 자극)
  Output: emotion-aligned brain embedding
  학습: 대규모 multi-dataset (Horikawa + Emo-FilM +
         ReelMo + HCP + NSD + IAPS + THINGS)
  특화: 감정 예측에 최적화된 뇌 표상

차별점 vs 기존 Brain FM:
  Brain-JEPA: resting-state 일반 표상
  우리 Emotion Brain FM: 감정 특화 표상
  → "감정을 위한 뇌 표상 모델"

잠재적 응용:
  - 임상: 감정 장애 (우울증, PTSD) 진단 보조
  - BCI: 실시간 감정 디코딩
  - 신경과학: 감정 처리 메커니즘 이해

논문화 가능성:
  현재 프로젝트의 자연스러운 후속 연구
  Ch4의 brain-tuning 결과가 이것의 타당성 근거
```

---

### Brain FM 비교 실험 계획 (Ch4 내 포함)

```
동일 파이프라인, 다른 Brain FM:

  (1) Raw fMRI (450 parcel)          ← gold standard
  (2) Brain-JEPA (resting-state)     ← 현재 보유, 비교군
  (3) SWIFT (naturalistic task)      ← 중기 추가
  (4) BrainSN (resting+naturalistic) ← 중기 추가
  (5) fMRI-LM (LLM token space)      ← Ch4-A2 핵심
  (6) BrainLM (task fMRI)            ← 중기 추가
  (7) BrainMT (multi-task)           ← 중기 추가
  (8) Emotion fine-tuned FM          ← 장기 목표

평가:
  각 FM으로 CCA → CC 수, r값, Cat/VA ratio
  각 FM으로 Ch4B Brain+Video → emotion R²
  → "어떤 brain representation이 감정 예측에 최적?"
  → "task-pretraining이 resting보다 나은가?"
  → "emotion fine-tuning이 추가로 도움이 되는가?"

이 비교 자체가 독립적인 contribution:
  "Brain Foundation Model의 감정 예측 유용성 비교"
```

---

## 타임라인 (업데이트)

```
4월 (오늘 ~ 이번 주)
  ├─ [오늘 1순위] AI-unique residual 분석 (20-30분)
  │   → 플랜 A or B 결정
  ├─ [오늘 2순위] Raw fMRI CCA 재실행 (30분)
  │   → Brain-JEPA CCA vs Raw fMRI CCA 비교
  │   → 내일 발표 자료
  └─ Ch1 완성 (Raw fMRI + ROI 분석)

5월
  ├─ Ch2 완성
  │   Variance Partitioning (메인)
  │   CCA 분석 (AI-shared 구조, 다중 렌즈)
  │   CLIP, DINOv2, VideoMAE 임베딩 추출
  └─ Emo-FilM 데이터 다운로드 + 임베딩 추출

6월
  ├─ Ch3 완성
  │   ROI × AI-unique 지도
  │   Principal gradient × AI-unique
  │   RSA + UMAP (AI-unique 감정 구조)
  └─ Emo-FilM Ch1-3 재현 시작

7월
  ├─ Ch4A (Brain-tuning, Moussa LoRA 방식)
  ├─ Emo-FilM Ch1-3 완성
  └─ SWIFT, BrainSN 등 task-pretrained FM 비교 시작

8월
  ├─ Ch4A 완성 (LLM token space 방식 추가)
  ├─ Ch4B 시작 (Brain+Video 결합)
  ├─ Brain FM 비교 완성
  └─ HCP-movie 데이터 준비

9월
  ├─ Ch4B 완성
  ├─ HCP-movie 확장 (n=176)
  ├─ Algonauts 벤치마크
  └─ 논문 작성

10월
  └─ 제출

──────────── 이후 (후속 연구) ────────────

Emotion fine-tuned Brain FM 개발
NSD / THINGS → Image vs Video 비교
ReelMo → Temporal dynamics
IAPS-fMRI → VCA 비교
Emotion Brain Foundation Model (장기 비전)
```
