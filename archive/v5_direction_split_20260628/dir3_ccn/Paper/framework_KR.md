# CCN_Emotion — 이론적 프레임워크 (한국어)

**최종 수정 2026-05-26**
**포지셔닝: Conwell/Bao 의 affectless machines 가설의 brain validation.**

> 자기지도 시각 모델은 어떤 emotion supervision 없이 자연 시각 통계로부터 emotion 관련 표상을 emergent 로 발달시킨다. 인간 뇌의 시각 처리가 감정 영상을 다룰 때 이 emergent 표상을 실제로 사용하는지는 미해결.

---

## 1. Background — 이야기

### 1.1 affective neuroscience 의 standing question

뇌가 감정 영상을 처리할 때, 뇌의 시각 표상은 무엇으로 organize 되는가? 두 관점이 경쟁한다.

**Reentry 관점 (고전)**: 시각 피질은 일반 visual feature (객체, 장면, 모션) 를 추출한다. Emotion category 는 reentrant feedback 을 통해 limbic / prefrontal 영역이 사후적으로 할당. 시각 처리 자체는 affect-neutral.

**Intrinsic 관점 (Kragel et al., 2019)**: 시각 피질이 이미 emotion 관련 구조를 인코딩한다. Kragel 등은 emotion category 라벨로 학습한 CNN 의 internal 표상이 visual cortex fMRI 와 정렬됨을 보였고, 15+ emotion category 가 visual cortex 만으로 디코딩 가능함을 입증. 시각 처리가 본질적으로 affect-relevant.

Kragel 증거에 circularity 문제가 있다. CNN 이 explicit emotion 라벨로 학습됐다. Visual cortex 가 emotion 구조와 정렬되는 이유가 자연 시각 통계 자체에 그 구조가 있어서인지, supervised 학습이 모델에 부과한 것인지 분리 불가.

### 1.2 Intrinsic 관점을 지지하는 최근 증거

두 최근 발견이 debate 를 움직인다. 둘 다 intrinsic 관점 방향. 둘 다 brain validation 까지는 도달 안 함.

**Bao et al. (2024, PLoS Computational Biology)** — emotion supervision 없이 object recognition 만 학습한 CNN 의 internal 뉴런이 emotion-selective 반응을 자발적으로 발달. 자연 통계 + object-recognition 목표로 emergent 하는 시각 hierarchy 가 부산물로 emotion-relevant computation 을 포함.

**Conwell et al. (2025, PNAS)** "The perceptual primacy of feeling" — emotion supervision 없이 학습된 180 개 visual model 을 인간 arousal/valence rating 에 대해 테스트. Affectless model 이 인간 affective behavior 분산의 majority 를 설명 — emotion-supervised model 만큼 잘. 결론: emotion-free 학습으로 발달한 시각 표상이 인간이 이미지에 대해 느끼는 것을 설명하기에 충분한 구조를 담는다.

이 둘이 **affectless machines hypothesis** 를 확립: emergent emotion-relevant 표상이 emotion supervision 없는 시각 학습 시스템에서 자발적으로 나타난다.

### 1.3 더 넓은 맥락 — 표상 alignment 라는 research paradigm

Affectless machines 발견들은 더 크고 빠르게 성장하는 *representational alignment* 연구 흐름 안에 위치한다 — model 표상과 인간 인지 구조의 체계적 비교 + 능동적 정렬 (Sucholutsky et al., 2023). Muttenthaler et al. (2025, *Nature*) 가 vision foundation model 들이 인간이 쓰는 multi-level conceptual hierarchy (animal vs vehicle vs furniture, 그 안에서 dog vs bird, 그 안에서 poodle vs golden retriever) 를 자연스럽게 잡지 못한다는 점을 보였고, human-similarity-distilled supervision (AligNet) 으로 fine-tune 하면 misalignment 가 수리되며 동시에 downstream ML 성능도 향상됨을 입증. 그들의 발견 — 자연 model 표상이 인간 관련 구조와 명시적 intervention 없이는 sparse 하게만 align 된다 — 이 우리의 sparse brain-alignment 관찰 (100 개 중 3 개만 brain-aligned) 을 더 큰 패턴의 일부로 위치시킨다.

남는 질문은 그 작은 brain-aligned subspace 가 sparse 함에도 불구하고 emotion-specific 정보를 담는가 다. 그게 이 프로젝트가 다루는 질문.

### 1.4 빠진 자리

Bao 2024 는 model 내부를 봤다. Conwell 2025 는 행동을 봤다. 둘 다 brain 은 안 봤다. 결정적 질문 — affectless model 의 emergent emotion 표상이 인간 뇌의 시각 emotion 처리에 실제로 사용되는가 — 는 미해결.

**Brain 이 이 emergent 표상을 사용한다면**: affectless machines 가설이 model 내부 + 행동에서 신경 표상까지 확장. Visual cortex 가 emotion 학습 (supervised 든 아니든) 없이도 affectless model 이 발달시키는 emergent emotion-relevant 구조와 같은 종류의 구조에 의존 가능.

**Brain 이 이 emergent 표상을 사용하지 않는다면**: affectless emotion 구조는 model 과 행동의 속성이지만 신경 표상의 속성은 아님. Visual cortex 가 emotional video 를 다른 dimension 으로 처리하고, Bao 와 Conwell 이 관찰한 emergent emotion 구조가 model 특이적이고 biologically grounded 되지 않음.

이 질문에 답한 연구가 없다. CCN_Emotion 이 직접 답한다.

---

## 2. Research Question

> **자기지도 및 visual-text foundation model 에서 발달하는 emergent emotion 표상이 인간 뇌가 감정 영상을 처리할 때 사용하는 시각 표상과 일치하는가, 그리고 학습 패러다임에 따라 다른가.**

두 primary model 을 병렬로 분석. **V-JEPA2** (자기지도 비디오, language 없음) + **CLIP** (image-text contrastive). 이 비교는 EmoBrain 프로젝트의 경험적 관찰에 의해 motivated 됨 — CLIP 이 모든 emotion prediction probe 에서 V-JEPA2 보다 우월 (Valence regression Pearson r 0.683 vs 0.470, Cat34 top-1 balanced accuracy 0.383 vs 0.293). 질문: brain-aligned subspace 와 emotion-encoding subspace 의 overlap 이 두 학습 패러다임 사이에 다른가, 그 차이가 text supervision 이 pure visual SSL 이 못 만드는 emotion-relevant 구조를 만든다는 것을 보여주는가.

조작적으로, 이건 단일 video model 의 두 subspace 사이 관계 질문이 된다.

- **Brain-aligned subspace of V-JEPA2**: Brain-JEPA fMRI 표상 (또는 secondary track 의 raw BOLD) 으로부터 선형 예측 가능한 V-JEPA2 표상의 principal components.
- **Emotion-encoding subspace of V-JEPA2**: emotion rating (카테고리 라벨 + arousal-valence 차원) 을 선형 예측하는 V-JEPA2 표상의 principal components.

경험적 질문은 두 subspace 가 겹치는가다. 겹치면 brain 이 emergent emotion 표상을 validate. 겹치지 않으면 affectless emotion 구조가 model 특이적 발견에 머무름.

분석이 답할 수 있는 한 문장으로 표현: **감정 영상에 대한 뇌의 시각 처리가 emotion 을 인코딩하는 dimension 으로 video 를 organize 하는가, 아니면 emotion 인코딩과 독립적인 dimension 으로 organize 하는가.**

---

## 3. Hypotheses

세 primary 가설, M1/M2/M3 framework 로 검정 가능하게 정식화.

**H1 (Brain 이 model 에서 sparse 하게 select)**. V-JEPA2 principal components 의 작은 subset 만이 brain 표상으로부터 선형 예측 가능. 모델 전체 표상은 1,408 dimension; brain-aligned dimension 은 sparse.
*조작적 측정*: M1 — Brain-JEPA → V-JEPA2 PC ridge regression + permutation-based FDR.
*현재 상태*: Accept 된 CCN abstract 에서 입증 (3/100 PCs survive; R² clipping robustness check Exp 29 진행).

**H2 (Model 의 일부 dimension 이 emotion 을 인코딩)**. V-JEPA2 principal components 의 subset 이 emotion 정보를 잘 인코딩한다, 학습에 emotion supervision 이 없었음에도. 이게 affectless machines 가설의 V-JEPA2 within-model instantiation (Conwell et al., 2025; Bao et al., 2024).
*조작적 측정*: M2 — V-JEPA2 PCs → emotion ratings ridge regression + decoding (continuous R², top-k accuracy, ROC-AUC).
*현재 상태*: 미측정. Exp 30 대기.

**H3 (Brain-aligned subspace 와 emotion-encoding subspace 가 overlap)**. Brain 이 V-JEPA2 에서 read 하는 principal components 가 V-JEPA2 안에서 emotion 을 인코딩하는 components 와 같다. 두 subspace 가 disjoint 가 아니라 overlap.
*조작적 측정*: M3 — set intersection, Jaccard coefficient, brain-aligned PC ranking 과 emotion-encoding PC ranking 사이의 Spearman rank correlation.
*현재 상태*: M1 과 M2 둘 다 필요. 프로젝트의 핵심 테스트.

자기지도 비디오 pretraining 의 specificity 를 테스트하는 보충 가설.

**H4 (Self-supervised contribution)**. H3 overlap 이 V-JEPA2 (자기지도 비디오 모델) 에서 특별히 크고, untrained ViT, ImageNet-supervised ViT-L, VideoMAE 에서는 그렇지 않다. 모든 visual model 에서 overlap 이 비슷하면 emergent emotion 구조는 시각 학습 일반의 속성이지 자기지도 비디오 학습에 특이하지 않다.
*현재 상태*: Architecture baseline embedding 추출 필요. Exp 31 시리즈 대기.

---

## 4. Outcome 해석

M3 해석이 프로젝트의 핵심. 세 principal outcome 이 세 distinct 과학적 결론에 대응.

**Outcome A — High overlap (brain-aligned ⊆ emotion-encoding, 또는 large Jaccard)**.
*Statement*: Brain 이 V-JEPA2 의 emotion 을 인코딩하는 components 를 정확히 read. Brain 이 emotional video 를 differentiate 하는 dimension 이 emotion 을 decode 할 수 있는 dimension.
*Implication*: Affectless machines 가설이 brain 까지 확장. 자기지도 시각 학습의 emergent emotion 표상이 biologically grounded; visual cortex 가 emotional video 처리 시 같은 종류의 emergent 구조를 사용. Kragel et al. (2019) 가 supervision circularity 제거된 채로 강화.

**Outcome B — Disjoint subspaces (low Jaccard, low rank correlation)**.
*Statement*: Brain 이 emotion 을 잘 인코딩하지 않는 V-JEPA2 components 를 read. Emotion-encoding components 가 V-JEPA2 에 존재하지만 brain 은 다른 dimensions 에 주목.
*Implication*: Affectless machines 가설이 model 내부와 behavior 에 한정; brain 까지 확장 안 됨. Visual cortex 가 emotional video 를 emotion-relevant variation 과 다른 dimensions 로 처리, reentry 관점 (emotion 이 시각 처리 downstream 에서 구성) 과 일치.

**Outcome C — Partial overlap**.
*Statement*: Brain 이 emotion-encoding 과 emotion-orthogonal components 의 혼합을 read.
*Implication*: 혼합 지지. 시각 처리가 emotion 처리에 부분 기여하지만 완전히 그것으로 organize 되지는 않음. H4 baseline 과의 quantitative 비교로 partial overlap 이 자기지도 비디오에 특이한지 시각 학습 일반인지 결정.

세 outcome 모두 과학적으로 정보 제공. 프로젝트는 어떤 outcome 에서도 informative 하도록 설계됨.

---

## 5. Method overview

### 5.1 Data

Horikawa et al. (2020) 데이터셋: 5 명 참가자, **2,185 개 감정 유발 영상** (canonical Horikawa master index, 반복 클립 11 개 (stim_idx 2185-2195) 제외 후), 영상별 34 카테고리 + 14 affective dimension 연속 emotion rating. 자극 수는 동일 group 의 EmoViS, EmoBrain 프로젝트와 일관.

### 5.2 Representations

**Dual primary video models** (둘 다 full M1/M2/M3 pipeline 으로 분석):

- **V-JEPA2** (Assran et al., 2025): emotion 라벨 없이 1M+ 시간 비디오로 학습한 자기지도 비디오 foundation model. ViT-G, 비디오당 1,408 차원 embedding, uniform 16 프레임, spatial token 평균. Affectless machines 가설 instance.
- **CLIP** (Radford et al., 2021): visual-text contrastive pretraining. `openai/clip-vit-large-patch14`, image encoder only (이 연구에서 text tower 미사용), 1,024 차원, 25/50/75% 위치의 3 프레임 평균. Text-mediated emotion 가설 instance.

두 embedding 모두 EmoViS extraction pipeline 의 산물 (2185 stimuli, 동일 sampling, 동일 master index).

**Brain side**:
- **Brain-JEPA** (Dong et al., 2024): UK Biobank pretrained fMRI foundation model, 비디오당 768 차원 subject-invariant 표상. Primary track.
- **Raw BOLD (secondary track)**: 450-parcel Schaefer parcellation, BFM-encoding robustness 테스트용 alternative brain 표상.

**Pillar 3 baselines** (EmoViS 에서 재사용 가능): untrained V-JEPA2 (random init), untrained CLIP, DINOv2 (object SSL), VideoMAE (다른 video SSL). 모두 primary model 과 일관된 (2185, *) 형식.

### 5.3 세 측정

**M1 — Brain-aligned subspace 식별**. V-JEPA2 를 100 PCs 로 축소. 각 PC 를 subject-mean Brain-JEPA 표상에 5-fold cross-validation ridge regression. Permutation test (n=1,000) + FDR. Survive 한 PCs 가 brain-aligned subspace.

**M2 — Emotion-encoding subspace 식별**. 각 V-JEPA2 PC 에 대해, 34 emotion category rating 과 2 arousal-valence dimension 을 ridge regression + decoding 으로 예측. 다중 metric:
- Continuous regression: ridge R², Pearson r (mean rater score 에 대해)
- Categorical decoding: top-1 accuracy, top-5 accuracy, ROC-AUC (영상별 top-rated category 에 대해)
Emotion-encoding 성능으로 PCs ranking.

**M3 — Subspace overlap**. M1 과 M2 사이 관계 정량화:
- Set intersection: |M1 PCs ∩ top-K M2 PCs|
- Jaccard coefficient
- PC ordering 사이 Spearman rank correlation (brain-aligned R² vs emotion-encoding accuracy)
- Permutation null: observed overlap 을 random PC selection 과 비교

### 5.4 Controls

**Visual baseline partial-out (Pillar 2)**: V-JEPA2 PCs 에서 DINOv2 (object), Places365 (scene), optical flow (motion), Sadeghi 139 (저수준 통계) 를 partial out 후 M1, M2, M3 재계산. Overlap 이 일반 visual category 구조로 환원 가능한지 테스트.

**Architecture baselines (Pillar 3)**: untrained V-JEPA2 (random init), ImageNet-supervised ViT-L, VideoMAE 에 대해 전체 M1/M2/M3 pipeline 반복. Overlap 이 자기지도 비디오 pretraining 에 특이한지 테스트.

**Brain representation track (Pillar 4)**: brain side 로 raw BOLD (450 parcels) 반복. Overlap 이 BFM-encoded brain 에 특이한지 raw fMRI 에도 일반화하는지 테스트.

---

## 6. Accepted abstract 의 leap 문제

Accept 된 CCN abstract 는 brain-aligned subspace 를 "affective subspace" 로 명명하고 "emotion schemas embedded within statistical regularities of the visual environment" (Kragel 2019, Conwell 2025 인용) 로 해석한다. 둘 다 abstract 의 데이터만으로는 지지되지 않는 interpretive move.

**Leap 1 (명명)**: V-JEPA2 PCs 는 정의상 visual feature axis. Brain-aligned PCs 를 "affective" 라 부르려면 그 PCs 가 일반 visual category 통계가 아닌 emotion-relevant 정보를 인코딩함을 보여야 한다. Abstract 는 이를 직접 테스트 안 함. M2 가 채우는 자리.

**Leap 2 (인용을 통한 메커니즘)**: Kragel 2019 는 supervised emotion classifier; Conwell 2025 는 행동만. 어느 쪽도 자기지도 model 의 emergent emotion 표상이 brain 안에서 사용되는지 직접 테스트하지 않음. 그들을 우리 finding 의 메커니즘으로 인용하려면 그들에게 없던 M3 overlap 분석이 필요.

현재 framework 는 이 leap 들을 interpretive 가정에서 testable 가설로 변환. H2 가 Leap 1 (model emotion-encoding) 테스트. H3 가 Leap 2 (brain-emotion overlap) 테스트. H4 가 추가 specificity claim 테스트.

M1, M2, M3 모두 측정되고 overlap 정량화되기 전까지, brain-aligned subspace 는 emotion attribution 없이 **brain-aligned visual subspace of V-JEPA2** 로 가장 정직하게 기술된다.

---

## 7. EmoViS 와의 차별화

EmoViS, 동일 Horikawa 데이터셋을 쓰는 별개 프로젝트, 는 Barrett 구성주의 framework 의 테스트. 그 central claim 은 brain 의 stimulus-level 표상 기하 구조가 observers 가 사후적으로 부여하는 이산 emotion rating 보다 자극의 연속 sensory-semantic 구조를 따른다는 것. 이론적 anchor 는 Barrett (2017) 와 Lindquist & Barrett (2012); 비교는 sensory-to-semantic model 스펙트럼 (VideoMAE → DINOv2 → V-JEPA2 → CLIP → Caption-LLM) 과 emotion ratings 사이, brain geometry 의 경쟁 설명으로.

CCN_Emotion 은 다른 이론적 anchor 를 가진다: Conwell et al. (2025) 와 Bao et al. (2024) 의 affectless machines 가설. Central claim 은 자기지도 시각 학습의 emergent emotion 표상이 biologically grounded — brain 이 emotional video 처리 시 이 emergent 표상을 실제로 사용한다는 것. 비교는 model family across 가 아니라 단일 자기지도 비디오 모델 (V-JEPA2) 내부에서, brain-aligned 와 emotion-encoding subspace 가 일치하는지를 묻는다.

| | EmoViS | CCN_Emotion |
|---|---|---|
| 이론적 anchor | Barrett 2017 구성주의 | Conwell 2025 + Bao 2024 affectless machines |
| 중심 debate | Brain emotion-geometry 가 sensory-semantic ingredient 로 organize 되는가, 언어적 categorization 으로 organize 되는가? | Brain 이 affectless model 의 emergent emotion 표상을 validate 하는가? |
| 비교 구조 | Across model family (visual-semantic 스펙트럼 vs ratings) | Within-model subspace overlap (brain-aligned vs emotion-encoding) |
| Brain side | Raw BOLD stimulus-level RDM | Brain-JEPA (track A) + raw BOLD (track B) |
| 다른 outcome 이 말하는 것 | Brain 이 ingredient 를 따르는가 (H1) + 영역별로 어떻게 변하는가 (H2) | Affectless machines 가설이 brain 까지 확장하는가 (H3) + SSL 비디오가 specific 책임인가 (H4) |

두 프로젝트는 dataset 과 한 모델 (V-JEPA2) 를 분석 자원으로 공유하지만 다른 이론적 전통에서의 질문에 답한다.

---

## 8. Contribution

### 8.1 Method-level contribution (outcome 독립)

자기지도 model 의 emergent representation 의 brain validation 을 테스트하는 framework. Brain-aligned subspace 식별 + emotion-encoding subspace 식별 + subspace overlap 분석 은 일반 패턴, target capability 에 대한 supervision 없이 학습된 어떤 모델에든 적용 가능, brain 이 emergent target representation 을 사용하는지 묻는다.

이 패턴은 Sartzetaki et al. (2025, ICLR) 의 자연스러운 within-model dual. 그들이 100 개 비디오 모델 across brain alignment 를 분해하고 어떤 model 속성이 alignment 를 만드는지 식별. CCN_Emotion 은 alignment 를 단일 모델 내부에서 분해하고 brain-aligned components 가 target capability (emotion) 를 carry 하는지 묻는다.

### 8.2 Finding-level contribution (outcome 의존)

Outcome 별 세 principal contribution:

**Outcome A (high overlap) 시**: Affectless machines 가설 (Conwell 2025, Bao 2024) 의 신경 표상 확장에 대한 첫 brain-direct 증거. 자기지도 비디오 pretraining 이 visual cortex 가 사용하는 emotion-relevant 시각 구조를 생성. Kragel et al. (2019) 의 intrinsic-emotion finding 이 supervision circularity 없이 replicated.

**Outcome B (disjoint) 시**: Affectless machines 가설이 model 내부와 행동에 한정된다는 첫 입증. Brain 이 emotional video 를 model 에서 emotion 을 인코딩하는 dimensions 와 다른 dimensions 로 처리. Emotion 이 시각 처리 downstream 에서 구성된다는 reentry 관점 지지.

**Outcome C (partial) 시**: Partial overlap 의 quantitative characterization. H4 baseline 과 함께 어떤 visual 표상이 brain emotion 처리에 더 기여하는지 식별.

세 outcome 모두 publishable, 질문 framework 에 calibrated.

---

## 9. 금지 표현

Accept 된 abstract 에서 leap 문제를 만든 drift 를 막기 위해.

- "Brain-aligned subspace 가 affective subspace 다" — H2 + H3 가 필요, M1 만으로 안 됨.
- "자기지도 학습이 spontaneously affective representation 을 생성한다" — H4 (SSL 비디오에 specific) 가 H2+H3 위에 추가로 필요.
- "Brain 이 V-JEPA2 로부터 emotion structure 를 read out 한다" — "V-JEPA2 의 brain-aligned PCs 가 emotion-encoding signal 을 담는다/안 담는다" 로 대체, M3 outcome 에 따라.
- "Brain 이 emotion 에 대해 categorical 하다" — out of scope. 분석은 visual-to-brain mapping 에 대한 것이지 brain organization 전반이 아님.
- "Subjective emotional experience 가 categorical 하다" — out of scope. 분석에 행동 또는 phenomenology 없음.
- "Brain 이 X 를 따라간다 / track 한다" — 정확한 용어로 대체: "X 가 brain 표상으로부터 선형 예측 가능" 또는 "brain 표상이 X 로부터 선형 예측 가능".

---

## 10. 핵심 References

| 논문 | 역할 |
|---|---|
| Conwell et al. (2025, *PNAS*) | 핵심 이론적 anchor — affectless visual machines 가 affective behavior 설명 |
| Bao et al. (2024, *PLoS Comp Bio*) | Object-recognition CNN 의 affectless emotion-selectivity emergence |
| Kragel et al. (2019, *Science Advances*) | Visual cortex 의 intrinsic emotion — supervised, 우리 프로젝트가 supervision circularity 제거 |
| Horikawa et al. (2020, *iScience*) | 데이터셋, brain categorical organization baseline |
| Cowen & Keltner (2017, *PNAS*) | Emotion taxonomy, 자극 pool |
| Assran et al. (2025) | V-JEPA 2 (분석 대상 자기지도 비디오 모델) |
| Dong et al. (2024, NeurIPS) | Brain-JEPA fMRI foundation model |
| Sartzetaki et al. (2025, *ICLR*) | 방법론적 anchor — across-model alignment 분해; 우리는 그 within-model dual |
| Doerig et al. (2025, *Nat Mach Intell*) | Generic scene 에 대한 caption-LLM brain alignment; ML-to-brain pipeline 선례 |
| Kornblith et al. (2019, *ICML*) | CKA representational similarity metric |
| Kriegeskorte et al. (2008, *Frontiers Sys Neurosci*) | RSA 기초 |
| Lindquist & Barrett (2012) | Background reference — emotion construction 의 reentry 관점 |
| Sadeghi et al. (2024) | Pillar 2 partial-out 의 저수준 visual feature baseline |
| Muttenthaler et al. (2025, *Nature*) | Representational alignment paradigm; model 이 자연스럽게 multi-level human-relevant 구조를 놓치지만 fine-tuning 으로 수리 가능; brain-tuning 변형 (Moussa et al., 2025) 이 future direction |
| Sucholutsky et al. (2023, *arXiv*) | "Getting aligned on representational alignment" — 우리 프로젝트가 속한 더 넓은 research program 정의 |
| Moussa et al. (2025, *ICLR*) | Speech model 의 brain-tuning — M3 가 disjoint subspace 보이면 future brain-side intervention 의 방법론적 analog |
