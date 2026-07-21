# Narrative v2 (2026-05-26)

## 인정해야 할 trivial 사실

V-JEPA2는 비디오 시각 입력만 본다. 따라서 Brain-JEPA ↔ V-JEPA2 alignment는 **정의상 visual statistics**다. "Alignment가 visual이다" 라는 것은 발견이 아니라 setup의 귀결이다.

흥미로운 질문은 alignment가 visual이냐가 아니라 **어떤 종류의 visual structure가 brain-readable한가**이다.

## Anchor 논문 — Sartzetaki et al. (2025, ICLR)

"One Hundred Neural Networks and Brains Watching Videos: Lessons from Alignment." 99개 NN × 10명 human brain × 17 ROI 비디오 alignment 벤치마크. Across-model 수준에서 "alignment의 의미"를 가장 깊게 해부한 최근 작업.

핵심 발견:
- Temporal processing 능력 → early visual cortex alignment에 결정적
- Action classification 훈련 → late visual cortex alignment에 결정적
- FLOPs와 alignment는 음의 상관 ("scale = alignment" 반박)
- 같은 brain 데이터에서 model family가 다르면 alignment의 locus가 다름

**CCN_Emotion이 Sartzetaki의 within-model dual:**

Sartzetaki는 "어떤 model 특성이 brain alignment를 만드는가"를 100개 모델 풀에서 본다. CCN_Emotion은 같은 logic을 **single-model 내부**에서 본다. V-JEPA2 안에서 어떤 component (어떤 PC, 어떤 layer, 어떤 visual content) 가 brain-aligned 인가?

이 framing이 가지는 효과:
1. "alignment가 visual이다"는 trivial 사실을 우회하지 않고 직시한다 (Sartzetaki도 모든 비교가 visual이다)
2. 답할 수 있는 질문으로 옮긴다 (어떤 visual?)
3. EmoViS의 model-spectrum 주장과 직접 연결된다 (EmoViS = across-model spectrum, CCN_Emotion = within-V-JEPA2 component)
4. "Self-supervised spontaneously" 같은 over-claim 없이도 nontrivial한 발견을 제시할 수 있다 (V-JEPA2의 brain-aligned subset이 generic visual baseline으로 흡수되지 않는다는 것 자체가 nontrivial)

## CCN_Emotion이 Sartzetaki에 더하는 것

| 차원 | Sartzetaki 2025 | CCN_Emotion |
|---|---|---|
| 자극 | Bold Moments (일반 영상) | Cowen-Keltner (감정 영상) |
| Brain side | raw BOLD, 17 ROI | Brain-JEPA whole-brain embedding |
| Model side | 100개 모델 비교 | V-JEPA2 단일 모델 내부 component 분해 |
| 질문 | 어떤 model 특성이 alignment를 만드는가 | V-JEPA2의 어떤 internal axis가 brain-readable인가 |
| 감정 차원 | 없음 | categorical vs dimensional emotion |

따라서 CCN_Emotion = "Sartzetaki의 within-model, affective extension".

## 세 pillar narrative

### Pillar 1. Existence
> V-JEPA2 100-PC 공간에서 Brain-JEPA로 linearly predictable한 부분공간이 존재하고, 그것은 저차원이다 (3 PCs survive FDR).

이미 abstract에 있음. 추가 작업 불필요.

### Pillar 2. Specificity (가장 중요한 새 작업)
> 이 brain-predictable 부분공간의 categorical-vs-dimensional 비율은 generic visual baseline (low-level statistics, object recognition, scene categorization, motion energy) 을 통제한 후에도 유지된다.

테스트할 baseline:
- **Low-level visual**: Sadeghi 2024 139-feature set (color, spatial frequency, symmetry, AlexNet variances). Sadeghi가 이미 affective valence를 설명한다고 보임 → 통제 후 잔존 effect가 SSL-affective 진짜 기여.
- **Object recognition**: DINOv2 ViT-G (1024-dim). 자기지도지만 object-centric.
- **Scene categorization**: Places365 ResNet50 features (2048-dim).
- **Motion energy**: 클립별 optical flow 통계 (Farnebäck 또는 RAFT). "temporal"이라는 V-JEPA2의 차별점을 직접 검증.

각 baseline에 대해 partial R² (V-JEPA2 PC | baseline) 계산. 이게 0이면 brain-readable structure가 baseline에 흡수된 것. 0보다 크면 generic vision 이상의 무엇인가가 있는 것.

### Pillar 3. Self-supervised contribution
> Untrained ViT 및 supervised ViT baseline은 같은 brain-aligned categorical structure를 만들지 않는다.

테스트할 모델:
- **Untrained V-JEPA2** (random init, same architecture). SSL pretraining 자체의 contribution 분리.
- **ImageNet-supervised ViT-L** (e.g., timm `vit_large_patch14_clip_224`). Supervised vision baseline.
- **VideoMAE** (다른 self-supervised video model). Architecture 효과 vs SSL 효과 분리.
- (Optional) **CLIP image-only** (text supervision은 다르지만 SSL과 supervised의 중간).

각각에 대해 동일 pipeline (100 PCs → ridge → ratio metric). Ratio가 같거나 더 높으면 V-JEPA2 specific 주장 무너짐. Ratio가 V-JEPA2보다 낮으면 SSL+video 조합의 specific contribution.

## Accepted abstract의 두 leap (2026-05-26 확정)

페이퍼가 "aligned component = affective subspace"로 framing 했지만, 그건 두 단계 점프다.

**Leap 1 (명명)**: "category-friendly brain-aligned visual subspace" → "affective subspace"
- 측정한 것: 3 개 PC 위에서 비디오들이 emotion category label 과 잘 정렬됨
- 점프: 그래서 "affective"
- 빠진 것: PCs 가 정의상 visual feature axes 다. Cowen-Keltner 자극 셋의 visual category coherence (얼굴, 장면, 모션) 가 trivially category-friendly clustering 을 만들 수 있음. 이걸 배제하려면 generic visual baseline 통제 (Pillar 2) 필요.

**Leap 2 (메커니즘)**: "affective subspace" → "emotion schemas embedded in visual statistics" (Kragel 2019 + Conwell 2025 인용)
- Kragel 2019: supervised emotion classifier on still image. Categorical structure가 by construction 으로 만들어짐. 자기지도 모델에 대한 주장 아님.
- Conwell 2025: 행동만, brain 측정 없음. 자기지도 비디오 모델 specific 아님.
- 따라서 두 논문 인용으로 Leap 2 를 정당화하는 건 약함. 정당화하려면 Pillar 3 (untrained, supervised baseline) 필요.

### 두 leap 의 진실값 (현재 데이터로는 미정)

| Leap | 검증 방법 | 현재 상태 |
|---|---|---|
| Leap 1 | Pillar 2 통제 후 ratio 잔존 여부 | 부분 테스트만 있음 (VGG19+semantic, "attenuated but preserved", 수치 없음) |
| Leap 2 | Pillar 3 untrained / supervised 비교 | 미검증 |

### 현 상태에서 정직한 명명

"Affective subspace" 대신: **"category-friendly visual readout channel between V-JEPA2 and the subject-invariant brain response."**

이게 데이터가 받쳐주는 정확한 표현. Pillar 2 통과하면 "category-friendly" 가 generic vision으로 환원 안 됨이 추가됨. Pillar 3 통과하면 "self-supervised video pretraining 의 emergent property" 가 추가됨. 그러면 비로소 "affective"라는 단어를 쓸 수 있다 (또는 그 단어가 정당화되지 않으면 안 쓰면 된다).

## 다섯 가지 위험 framing (사용 금지)

1. "Self-supervised learning spontaneously produces a categorical affective subspace" — Pillar 3 검증 전.
2. "The brain is categorical" — 우리는 visual→brain 매핑을 보고 있고 brain 자체의 organization은 아니다.
3. "Subjective emotion is categorical" — 행동/주관 측정 0개.
4. "Alignment proves V-JEPA2 learned emotion" — V-JEPA2는 emotion supervision 없음. 명확히 SSL 학습 visual statistics다.
5. "Brain reads out emotion structure from V-JEPA2" — "emotion structure"가 무엇인지 정의 안 되면 over-claim. "categorically-organized visual structure"로 표현.

## EmoViS와의 logical 관계

EmoViS H1: 뇌의 stimulus-level geometry가 emotion ratings (post-categorization) 보다 visual-semantic 모델 (pre-categorization) 과 더 잘 align됨.

CCN_Emotion Pillar 2: V-JEPA2 brain-aligned 부분공간의 categorical structure가 generic vision baseline으로 흡수 안 됨.

두 주장은 같은 logical move의 다른 수준:
- EmoViS는 model family 차원 (V-JEPA2 vs ratings).
- CCN_Emotion은 V-JEPA2 내부 차원 (brain-aligned vs other vision baselines).

따라서 narrative는 통합 가능: "brain's emotion-relevant readout from visual representations is not reducible to standard visual category baselines, neither across model families (EmoViS) nor within a single self-supervised video model (CCN_Emotion)."

## 다음 단계 (작업 순서)

Tier 0. 카메라 레디 (6/11). Major revision 금지. Text framing 약화만:
- Abstract "spontaneously" → "the brain-readable subset of V-JEPA2 ... carries more categorical than dimensional emotion information than the full V-JEPA2 space"
- Discussion 1문장으로 baseline 부재 한계 명시

Tier 1. Pillar 2 baseline 통제 (5/26 ~ 6/2):
- DINOv2, Places365, optical flow features 추출
- Partial R² 계산
- 결과를 포스터에 supplementary로 (camera-ready 본문 변경 없음)

Tier 2. Pillar 3 baseline 모델 (6/3 ~ 6/16):
- Untrained V-JEPA2, ImageNet ViT-L, VideoMAE embedding 추출
- 동일 pipeline → ratio 비교
- 포스터에 추가

Tier 3. Mechanistic depth (6/17 ~ 8/3 포스터 발표 전):
- V-JEPA2 layer-wise (블록 4, 8, ..., 40)
- Brain region-wise (parcel/network)
- PC1 interpretation (top/bottom 20 videos)
- Noise ceiling (split-half)

Tier 4. 풀 페이퍼 작업 (포스터 후):
- Cross-validation 재설계, cross-dataset replication, decoding accuracy, 이론 framing 정리
