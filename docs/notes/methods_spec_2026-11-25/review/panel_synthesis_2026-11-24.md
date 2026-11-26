# 연구설계 패널 통합 권고 (PI 종합)

## 1. 결론

**추천하는 구성.** 네 설계의 비판에서 공통으로 살아남은 핵심은 하나다. VCE(독립 영상, 독립 평정자)에서 자극→정서 렌즈를 학습하고, Cowen 평정이나 뇌 데이터를 보기 전에 고정(freeze)한다. 그 뒤 이 고정 렌즈를 세 곳에 적용한다.
- Cowen 평정: 구성개념 전이 검사.
- HK 뇌: 라벨을 보지 않는 특징 디코딩 경로와, 같은 구성개념의 직접 경로로 분해.
- 외부 검사: MC는 고정 metric RSA, Emo-FilM은 측정된 뇌.

이 위에 설계별로 다음을 가져온다.
- **A**: 같은 아키텍처·같은 diet에서 학습 목적(objective)만 바꾸는 대조. 사용자 목표 3("brain-like")의 모델 쪽 지렛대로 쓴다. 고정 예산, 3개 이상 seed, drift 매칭을 추가한다.
- **B**: 라벨 없는(label-blind) 뇌측 특징 디코딩 경로.
- **C**: 영역 인코딩 부분공간이 VCE 정서를 조직하는지를 PCA-k null과 대조하는 검사. 보조 분석으로만 둔다.
- **D**: 순서 원칙(자극 readout 먼저, 뇌는 나중)과 자극측 ceiling.

다음은 버리거나 강등한다.
- 수준별 27차원 "정서 부분공간"을 뇌 분해의 단위로 쓰는 것(A, B). 세 수준이 같은 목표의 잡음 추정치로 붕괴하므로 식별되지 않는다.
- 평정 잔차로 "환원 불가능한 정서 코드"를 주장하는 것(B의 A4, C의 P2).
- brain-tuning, TRIBE v2를 "독립 뇌 재현"으로 쓰는 것(C).
- 선형 readout을 lesion하는 것(A~D 공통). 동어반복이다.
- in silico screening을 헤드라인으로 내세우는 것(A~D 공통). 새 뇌 데이터 없이는 모델의 성질일 뿐이다.
- MC 응답으로 디코더를 학습하는 imagery 디코딩(B, D). AffectLab 규칙 위반이다.

수정해서 남기는 것도 있다.
- "situation" 수준은 VCE에 진짜 텍스트가 없으면 "언어정렬 시각 표상(PE-Core)"으로 이름을 바꾼다.
- 감정별 조성(per-emotion composition)은 EmoBrain에서 이미 폐기된 가설이므로, 추정기 감사를 통과하기 전에는 탐색적으로만 둔다.

**패널이 엇갈린 지점과 해소 방식.**
- VCE의 situation 대리변수: A/B/D는 PE-Core, C는 Kinetics+Places logit을 썼다. 검증 결과 둘 다 situation이 아니다. 이름을 바꾸고, 선택지로 인간 캡션 부분집합을 둔다.
- 주 모델: A는 V-JEPA 2와 AlexNet 미세조정, C는 brain-tuning, D는 frozen probe를 제안했다. 비용과 이미 갖춰진 코드를 근거로 VCE 저자 VideoMAE fork를 objective 대조의 주 모델로 고른다.
- MC 사용: B/D는 규칙 변경을 요구했고 A/C는 고정 RSA를 택했다. 엄격 규칙을 기본으로 한다.
- 등차원 PCA: 네 설계 모두 썼지만 비판자 전원이 불필요하다고 봤다. 전체 차원 banded ridge를 주 분석으로, PCA는 민감도 분석으로 둔다.
- 디코더: PLS, SLiR, ridge가 섞여 있었다. ridge를 주로, PLS를 민감도로 둔다.
- 차원: 27과 34가 섞여 있었다. VCE 경로는 27, Horikawa 재현용 평정 band는 34로 한다.

## 2. 사용자 생각 중 근거상 교정이 필요한 부분

1. **"VCE는 큰 수확이다"는 절반만 맞다.** 독립성과 규모는 진짜 이점이다. 그러나 구성개념이 다르다.
   - VCE 라벨은 평균 강도 0-1이고, 예시 값이 1/120의 배수다. 이는 P(선택)×강도일 가능성을 시사하지만 추론이다.
   - Cowen은 34개 선택지 중 각 범주를 고른 평정자의 비율이다.
   - VCE 평정자가 소리를 들었는지는 미검증이다. HK/MC는 무음으로 제시했다.
   - VCE에는 캡션이 없다(README 검증).
   - 평균 길이는 약 14.1 s다(NeurIPS 검색 snippet 수준). Cowen과의 중복도 미검증이다.

   따라서 "VCE→Cowen 전이 실패 = HK 효과가 Cowen 특이적"이라는 해석은 성립하지 않는다. 결합된 shift 하의 전이로만 서술한다.
   근거: Mazeika et al., "How Would The Viewer Feel? Estimating Wellbeing From Video Scenarios", NeurIPS 2022 D&B; emodiversity README.

2. **"Kragel처럼"이 품은 순환성 프레임은 틀렸다.** Kragel의 fMRI 검사는 IAPS/GAPED 이미지와 영화 클립으로 했고, Cowen/HK 영상은 쓰지 않았다. 따라서 "EmoNet과 HK가 독립이 아니었다"는 gap 서술은 사실이 아니다(패널 판정 misrepresented).
   올바른 gap은 이것이다: 독립 영상·독립 평정자로 학습한 정서 모델을 HK/MC에 검사한 적이 없다.
   또한 Kragel은 top-1 범주에 softmax를 걸었으므로, 이 프로젝트에서는 "Kragel 설계를 연속 목표(BCE/MSE)로 변형"했다고 명시해야 한다.
   근거: Kragel, Reddan, LaBar & Wager, "Emotion schemas are embedded in the human visual system", Science Advances 2019 (PMC 전문); emonet-pytorch models.py의 Softmax와 top-1 ID 목록.

3. **"Gao처럼 object가 정서를 끌고 간다"는 이 자극에 그대로 옮길 수 없다.** Gao는 일상 장면에서 AlexNet > EmoNet을 보였지만, Cowen 프레임 같은 명시적 유발 자극에서는 EmoNet이 우세했다. 따라서 VCE/Cowen에서는 object band가 약할 것으로 예상해야 하고, objective 대조의 "차이 없음" 결과를 "Gao와 일치"라고 쓸 수 없다.
   근거: Gao, Ajith & Peelen, "Object representations drive emotion schemas across a large and diverse set of daily-life scenes", Communications Biology 2025.

4. **"모델 표상이 뇌와 비슷해진다"는 절대 점수로 판단할 수 없다.**
   - 224개 모델 중 126개가 veRSA r=0.1 안에 몰려 있고, 아키텍처나 목적보다 training diet가 지배적이다.
   - 같은 diet에서 시각 contrastive와 언어정렬 contrastive는 거의 같았다. D가 이 논문을 "band를 objective로 정의하는 근거"로 쓴 것은 misrepresented다.
   - 따라서 brain-likeness는 같은 아키텍처·같은 diet의 짝 대조로만 추론한다.
   - seed만 달라도 표상이 달라지므로 seed 반복이 필요하다.

   근거: Conwell, Prince, Kay, Alvarez & Konkle, "A large-scale examination of inductive biases shaping high-level visual representation in brains and machines", Nature Communications 2024 (PMC 전문); Mehrer, Spoerer, Kriegeskorte & Kietzmann, Nature Communications 2020 (PubMed 검증).

5. **"모델을 조작해 간접 검증(Liu처럼)"에는 조건이 있다.** Liu는 별도 이미지에서 d' 선택성으로 고른 내부 unit을 lesion했고, 하류에 비선형 층이 있었다. 선형 readout의 행공간을 제거하는 것은 정의상 출력을 없애는 동어반복이다.
   근거: Liu, Bo, Ding & Fang, "Emergence of Emotion Selectivity in Deep Neural Networks Trained to Recognize Visual Objects", PLoS Computational Biology 2024.

6. **"어떤 정보가 어떤 감정·영역과 연결되는지 셋을 같이 본다"에는 선행 실패와 선행연구가 있다.**
   - EmoBrain에서 이미 실패했다: 감정별 sensory:semantic 조성은 0/34 Bonferroni, split reliability −0.95 ~ −1.00. 시각모델 layer→영역 위계도 약했다(CONTEXT_EMOBRAIN.md). −1에 가까운 reliability는 표본 잡음이 아니라 추정기 구조 문제를 시사한다. 표본을 늘려서 해결되지 않는다.
   - 같은 HK 데이터로 motion energy·semantic·emotion band의 banded ridge를 한 선행연구가 있다: Du, Fu, Wen & He, "Topographic representation of visually evoked emotional experiences in the human cerebral cortex", iScience 2023 (PubMed/PMC 검증).
   - Horikawa 2020도 principal gradient를 따라 visual→semantic→emotion 이동을 이미 보였다.
   - 따라서 주 추론은 profile·영역 수준으로 하고, 감정별 셀은 val에서 정한 reliability gate를 통과할 때만 탐색적으로 본다.

7. **"situation 정보"의 실체를 다시 봐야 한다.**
   - MC 캡션은 영상을 본 사람이 쓴 해석이고 정서어가 섞여 있다(smiling 402, scared 197, laughing 174, crying 84 등; caption_ck20.csv 집계). 엄밀히는 자극 계산량이 아니다. "인간 장면 기술"로 부르고, 정서 lexicon rung을 추가한다.
   - PE-Core의 encode_video는 프레임별 CLIP 임베딩의 평균이다(코드 검증). situation이 아니라 언어정렬 시각 표상이다.

8. **"Kragel, Gao처럼 새 방법으로 예측을 보인다"의 한계.**
   - Gao에는 생성이나 시연이 없다.
   - Ratan Murty et al. 2021과 Gu et al. 2023은 선별 자극을 새 fMRI로 검증했다.
   - 새 뇌 데이터 없는 VCE screening의 T[r,e]는 닫힌형 모델 성질(w_r^T Σ β_e)이다. 가설 생성기로만 쓴다.

   근거: Ratan Murty, Bashivan, Abate, DiCarlo & Kanwisher, Nature Communications 2021; Gu, Jamison, Sabuncu & Kuceyeski, Communications Biology 2023.

9. **MC imagery를 정서 독립 증거로 쓰기 어렵다.**
   - 회상 cue는 같은 영상의 20개 캡션 중 하나다.
   - 매 imagery 직후 실제 영상을 다시 보여준다.
   - 피험자가 영상-cue 쌍을 사전 연습했다.
   - 정서를 "내용 디코딩 → 고정 readout"으로 만들면 "내용은 되는데 정서는 안 된다"는 결과가 구조상 나올 수 없다.
   - MC 응답으로 디코더를 학습하면 AffectLab 규칙 위반이다.

   근거: Horikawa, "Mind captioning: Evolving descriptive text of mental content from human brain activity", Science Advances 2025 (PMC12588295 전문); AffectLab AGENTS.md.

10. **"27로 고정"은 VCE 경로에만 적용한다.** 27의 1차 근거는 Cowen & Keltner, "Self-report captures 27 distinct categories of emotion bridged by continuous gradients", PNAS 2017이다(초록 검증). 그러나 Horikawa 2020의 범주 고유 transmodal 분산을 재현할 때는 34를 유지해야 한다. 빠지는 7개(contempt, guilt, pride, sympathy 등)가 사회적·자기의식 정서라 transmodal 분산을 가질 수 있다.

11. **"git clone만"과 "최신 모델" 제약은 상충한다.**
    - emonet-pytorch에는 ImageNet fc8 가중치와 학습 코드가 없다. torchvision AlexNet은 다른 변형이다.
    - DeBERTa, PE, V-JEPA 가중치는 HF/CDN에서 받는다.
    - 최신성으로 보면 V-JEPA 2.1(같은 repo, 2026-03)이 있다. AlexNet은 Gao와의 연속성 때문에만 정당화된다.

12. **HK로 brain-tuning을 하기에는 데이터 조건이 맞지 않는다.** HK는 영상당 1회 제시이고, 저자들도 noise ceiling을 추정할 수 없다고 밝혔다. brain-tuning의 noise-ceiling voxel mask를 만들 수 없고, 1,748 block 평균 샘플로는 ViT-L을 움직이기 어렵다.
    근거: Horikawa, Cowen, Keltner & Kamitani, iScience 2020 (PMC 전문); brain-tuning repo의 NC 로딩 코드.

13. **"HK test는 untouched"가 아니다.** EmoBrain 1748/217/220 split의 결과(0.294 등)가 이미 보고됐다. AffectLab 문서도 이후의 새 분석을 탐색적으로 기록하라고 한다. confirmatory 검사는 MC(고정 RSA)와 Emo-FilM뿐이다.

## 3. 추천 구성의 뼈대

### Part 0. 전제조건 (어떤 결과도 읽기 전에)
- **중복 제거.** pHash에 V-JEPA/PE 임베딩 최근접 탐색과 수작업 확인을 더한다. 대상은 다섯 방향이다: VCE↔Cowen, VCE train↔test, Cowen↔Cowen(MC가 제외한 16개 중복 목록과 대조), 그리고 MC-72를 최우선으로.
- **새 split.** MC-72와 그 near-duplicate를 HK·Cowen의 모든 개발 단계에서 뺀 새 split을 `/home/user/AffectLab/01_AffectModels/splits`에 만들고 provenance를 기록한다. HK 분석은 탐색적(또는 피험자 내 재현 기준)으로 라벨링한다.
- **분석 상수 사전 고정.** profile 거리 metric, 등가성 경계(SESOI), ROI 집합, 34→27 규칙을 미리 정한다.
  - ROI: HK의 HCP-MMP에서 10-15개 a priori ROI. transmodal은 Margulies principal gradient 상위로 정의한다(Horikawa 2020 방식).
  - 34→27: 재정규화하지 않는다. 탈락 질량은 연속 공변량으로 넣는다. Cowen 행의 99.5%가 합 > 1이어서 multi-select와 정합적이다.
- **VCE 라벨 정리.** topK 필드와 fork의 argmax 코드 경로를 제거한다.

### Part 1. 자극→정서 (AffectProcess 축; 목표 1, 4, 5의 절반)
- **무엇을 하는가.**
  - VCE train에서 band별 특징과 결합 특징으로 27차원 강도를 예측하는 readout을 학습하고, VCE test(11,046)에서 보고한다.
  - 같은 readout을 고정한 채 Cowen 전체에 적용한다. 평가는 감정별로 rank를 매긴 뒤의 profile 거리, 감정별 Spearman, 그리고 Cowen-trained nested-CV readout 대비 비율로 한다.
- **Band 구성.**
  - L: pymoten motion energy, 색 히스토그램, 공간 power spectrum.
  - O: AlexNet fc7/fc8 logit. softmax posterior는 쓰지 않는다.
  - S: Cowen에서는 MC 캡션 DeBERTa-large. 통제 사다리는 단어평균, 명사만, 섞은 문장, 정서 lexicon 마스킹이다.
  - VCE에서는 PE-Core를 "언어정렬 시각"이라는 이름으로 쓴다.
  - 같은 diet 대조를 위해 Cowen에서 PE의 vision tower(영상)와 text tower(캡션)를 비교한다. 같은 모델, 같은 공간에서 "인간 기술이 시각 tower에 더하는 것"을 본다.
- **분해.**
  - 전체 차원 banded ridge(himalaya)를 주 분석으로 한다. 분해 방식은 product measure(Dupré la Tour 2022)와 set-theoretic 7분할(Lescroart, Stansbury & Gallant 2015, 7개 부분모델 별도 적합) 중 하나를 사전에 고정한다.
  - 공유 분산이 큰 결과 자체를 결론으로 보고한다.
  - 감정별 조성은 kill-test 2(합성 감사)를 통과할 때만 탐색적으로 본다.
- **repo (검증됨).** github.com/hendrycks/emodiversity, gallantlab/pymoten, gallantlab/himalaya, facebookresearch/perception_models, horikawa-t/MindCaptioning, ecco-laboratory/emonet-pytorch(MATLAB 계열 AlexNet conv-fc7; fc8은 별도 변환이 필요).
- **근거.** Kragel 2019(저수준 통제), Gao 2025(object 조작화), Nishimoto et al. 2011 Current Biology(motion energy), Horikawa 2025(캡션 인코딩), Doerig, Kietzmann et al., "High-level visual representations in the human brain are aligned with large language models", Nature Machine Intelligence 2025(bag-of-words 사다리; "권고"가 아니라 그들이 실행한 통제), Conwell, Graham, Boccagno & Vessel, PNAS 2025(동기 부여로만), Westfall & Yarkoni, PLoS ONE 2016("unique ≠ 순수").

### Part 2. 자극모델↔뇌 (목표 2, 3)
- **2a. Objective 대조 (A의 핵심, 수정판).**
  - 주 모델: VCE 저자 fork(JunShern/VideoMAE, K400 자기지도 ViT-B, BCE soft 27-d가 이미 구현됨).
  - 세 갈래를 같은 영상·같은 고정 step/LR schedule로 학습한다:
    - (i) VCE 정서 BCE.
    - (ii) 비정서 목표. PE-Core 임베딩 distillation, 또는 같은 recipe의 K400 supervised fine-tune.
    - (iii) 라벨 순열. 열화 참조로만 쓴다.
  - 갈래당 seed 3개 이상. drift는 M0 대비 CKA로 보고, 정렬은 step별 궤적으로 보고한다.
  - 1차 대조는 (i)−(ii)다.
  - HK에서 층별 정렬을 두 방식으로 잰다: 가중치 없는 cRSA와 적합된 encoding. 부호가 둘 다에서 일치할 때만 "기하적"이라고 쓰고, 적합 방식에서만 나오면 "선형 접근 가능"이라고 쓴다.
  - 영역 특이성은 대조 × ROI 상호작용이 있어야 인정한다.
- **2b. Gao 복제(저비용).** MATLAB AlexNet fc8 대 VCE로 학습한 EmoNet 헤드(마지막 FC만, 연속 목표)를 HK ROI에서 비교한다. Cowen과 독립적이다.
- **2c. 영역별 band 지도.** HK encoding에 L/O/S band와 34-d 평정 band를 넣는다. Horikawa 2020의 범주 고유 분산이 현대 특징 아래에서도 남는지 본다. 위 Du et al. 2023 iScience와 직접 대비해 서술한다.
- **repo.** JunShern/VideoMAE(emodiversity submodule), facebookresearch/vjepa2(V-JEPA 2.1 frozen 특징을 참조 모델로), ColinConwell/DeepNSD(cRSA 로직만), KamitaniLab/EmotionVideoNeuralRepresentationPython(HK 로딩, ROI).
- **근거.** Conwell 2024(통제 비교), Gao 2025, Kragel 2019, Mehrer 2020(seed), Kanwisher, Khosla & Dobs, Trends in Neurosciences 2023과 Doerig et al., "The neuroconnectionist research programme", Nature Reviews Neuroscience 2023(프레임만, 초록 수준).
- **버린 것과 이유.**
  - brain-tuning(Moussa, Klakow & Toneva, ICLR 2025)과 ReAlnet 보존항: noise ceiling이 없고, 보존항이 CE-argmax이며, ReAlnet 상관항에 gradient가 없다. 수 GPU-week 비용이다.
  - TRIBE v2: V-JEPA 2 vitg backbone을 공유하므로 독립 재현이 아니다. Llama 경로가 있고, CC-BY-NC이며, 학습 데이터에 정서적 영화가 들어 있다.
  - C의 Tier B(축소계수 부분공간): "brain-like 모델"이 아니다. 2d로 이름을 바꿔 보조 분석으로 둔다.
- **2d. 영역 인코딩 부분공간 검사 (C의 살릴 핵심, 보조).** 피험자별·영역별로 최적 층을 고르고, HK encoding의 예측 반응 공간이 VCE 정서 profile을 조직하는지 본다. 비교 대상은 같은 특징의 PCA-k와 자극 순열 반응으로 적합한 인코더(각 영역의 자기 α)다. 작은 n의 learning curve와 정렬 강도 조건부 비교로 판단한다. 감정 라벨은 쓰지 않는다.

### Part 3. 뇌→정서 (EmoBrain 축; 목표 4, 5)
- **라벨 없는 경로 (B의 핵심).** 각 ROI에서 band 특징으로 가는 ridge 디코더를 학습한다(HK train, val 선택은 특징 정확도로만). 디코딩된 특징을 고정 VCE readout에 통과시켜 27-d profile을 얻는다.
- **같은 구성개념의 직접 경로 (C, D 비판 반영).**
  - brain→Cowen 27-d를 HK train에서 학습한다.
  - brain→band→readout 경로도 HK-train의 Cowen 27-d로 학습한 판을 함께 둔다. 두 경로의 목표 구성개념을 맞추기 위해서다.
  - VCE readout 경로는 전이 검사로 병기한다.
- **자극측 ceiling (D).** 고정 readout을 같은 test 자극의 실제 Cowen 특징에 적용한 값을 ceiling으로 둔다. 뇌 경로는 ceiling 대비 비율로 보고한다. 이렇게 해야 구성개념 손실과 뇌 정보가 분리된다.
- **분해.** cross-fitted partial correlation을 쓴다: 자극 예측을 통제한 뇌 예측, 그리고 그 역. 결합 가중치는 val에서만 적합한다. 잔차 주장은 "특징집합 F를 넘어"로만 쓰고 "환원 불가능"이라고 쓰지 않는다.
- **목표 5 "관계 자체를 학습"에 대한 정직한 답.** 학습된 관계는 영역→특징(HK)과 특징→정서(VCE)의 합성이다. 뇌에 정서 loss를 직접 거는 공동학습은 라벨 없는 성질을 깨므로 H4 디코더 쪽에 둔다(결정 Q2).
- **추론.**
  - 피험자별로 test 자극 순열과 ROI 간 max-statistic을 쓴다.
  - 5명 각각의 효과를 모두 보고한다.
  - RDM에는 subject×stimulus 2요인 bootstrap을 쓴다(Schütt et al. 2023 eLife; partially).
  - 감정별 셀은 val에서 support 수와 reliability gate를 통과한 것만 본다.
  - 디코딩 정확도를 영역 간 비교할 때는 voxel 수를 맞추고, 영역 주장은 forward encoding(2c)에 둔다.
- **근거.** Horikawa & Kamitani, "Generic decoding of seen and imagined objects using hierarchical visual features", Nature Communications 2017; Kragel 2019(뇌→모델 출력 방향); Horikawa 2025(L2 선형 디코더); Kriegeskorte, Simmons, Bellgowan & Baker, Nature Neuroscience 2009; Lakens, "Equivalence tests", Social Psychological and Personality Science 2017.

### Part 4. 참신한 시연 (목표 6)
- **4a. Emo-FilM 외부 뇌 검사 (유일하게 측정된 다른 자극셋).** HK에서 고정한 파이프라인과 VCE 렌즈로 parcel 시계열을 예측하거나, 영화 단위 leave-one-film-out으로 within-dataset 디코더를 만든다(둘 중 하나를 사전에 정한다).
  - 주의: 소리가 있는 상태로 시청했고, 13개 이산 정서 항목과는 부분적으로만 겹치며, 평정자 3-4명에 일치도는 약 0.38이다.
  - 근거: Morgenroth et al., Scientific Data 2025 (PMC 전문).
- **4b. MC 고정 metric RSA (사전등록, confirmatory).**
  - 렌즈 RDM(갈래별, band별)과 MC-72 지각 ROI RDM을 비교한다. ROI는 atlas로 정의하고, MC 응답으로 아무것도 적합하지 않는다.
  - 저자가 run별로 z-score한 데이터를 쓰는 것이 규칙상 허용되는지는 사용자 판정이 필요하다.
  - imagery는 탐색적으로 둔다. cue 캡션 RDM을 공변량으로 넣고, "cued recall에서 가용한 구조"로만 서술하며, ROI×조건 상호작용을 직접 검정한다.
- **4c. VCE in silico screening (가설 생성기).**
  - null: 자극 순열 반응으로 적합한 인코더(자기 α).
  - 주장은 영역 간 차이로만 한다.
  - 영역별 상하위 VCE 영상을 사전등록해, 향후 전향적 fMRI 예측으로 남긴다(Gu et al. 2023 방식).
- **4d. Kragel식 저비용 시연.** 렌즈 출력과 Cowen 14개 정서 차원(valence, arousal 포함)의 RSA를 본다(Kragel의 IAPS valence/arousal 시연에 대응). VCE README에 있는 V2V pairwise 판단 데이터(26,670개 영상, README 수준 정보라 직접 확인 필요)와의 일치도도 본다.
- **강등하거나 뺀 것.**
  - 선형 readout lesion은 뺀다.
  - Liu식 unit lesion은 선택 사항으로 둔다. 조건: VCE-val 반응 선택성으로 unit을 고르고, 중간층에서 하며, 분산을 맞춘 무작위 unit과 비교하고, 2개 이상 모델에서 재현될 때만 주장한다.

## 4. 양방향 예측

- **Part 1 전이.**
  - 높으면: 자극→정서 관계가 데이터셋이나 평정 구성개념이 아니라 내용에 속한다.
  - 낮으면: 결합 shift(구성개념, 도메인, 오디오) 아래에서 전이되지 않는다. 이후 뇌 분석은 Cowen-trained readout으로 하고, 독립성 주장은 철회한다.
  - band 분해에서 공유 분산이 지배적이면: 정서 profile이 수준을 가로지르는 공통 내용 기하를 탄다(대전제 2를 지지). 감정별 고유 조성이 신뢰성 있게 나오면: 감정별 "레시피"가 존재한다.
- **Part 2a objective 대조 (i)−(ii).**
  - transmodal에 집중된 양의 효과: 독립 영상에서 배운 정서 목적이 내용 diet 이상의 구조를 만들고, transmodal 피질이 그것을 공유한다. HK 2020의 transmodal 주장을 순환성 없이 지지한다.
  - 등가성 경계 안: 피질의 정서 기하가 내용 학습 표상에 이미 있다(Conwell 2025와 정합). Gao의 유발 자극 결과와는 긴장 관계로 서술한다.
  - 음: 평정을 가장 잘 맞추는 코드와 피질 코드가 다르다.
  - 미결론: seed 분산 안에 있으면 "현 데이터로 분리 불가"로 보고한다.
- **Part 2c.**
  - 평정 band의 transmodal 고유 분산이 현대 L/O/S 아래에서 사라지면: Horikawa 2020의 범주 고유성은 그때 특징의 한계였다.
  - 남으면: 그 위치를 지도화한다(Du 2023과 대비).
- **Part 3.**
  - 뇌 경로가 자극측 ceiling의 큰 비율을 회복하면: 뇌의 정서 정보는 대부분 다른 사람이 쓰는 내용 경로로 운반된다.
  - 직접 경로가 내용을 통제한 뒤에도 유의하면: 특징집합 F 밖의 정서 관련 조직이 있고, 위치를 특정할 수 있다.
  - 효과가 0이면 등가성 검정을 통과한 경우에만 "F로 설명된다"고 쓴다.
- **Part 4.**
  - Emo-FilM에서 전이되면: 조직이 자극셋을 넘어 일반화된다. 실패하면: HK/Cowen 자극셋 특이적이다(오디오라는 경계를 명시).
  - MC RSA가 양이면: 새 피험자로 일반화된다.
  - imagery에서 cue 공변량 이후에도 정렬이 남으면: cued recall에서 정서 관련 기하가 재현된다. 사라지면: 지각에 묶인 구조이거나 cue로 설명된다.
  - screening은 결과와 무관하게 "모델 예측"으로만 서술한다.

## 5. 최우선 저비용 kill-test 3개

1. **K1. 중복 스캔과 VCE→Cowen 동결 전이.**
   - 방법: CPU 중복 스캔(MC-72 우선)을 하고, VCE 5k 부분집합과 Cowen에서 기존 파이프라인 특징(중간 프레임 CLIP bigG, V-JEPA 2)을 GPU로 추출한다(사용자 실행).
   - 판정: VCE readout의 Cowen 성능이 같은 특징의 Cowen-trained nested-CV readout의 사전고정 비율(예: 0.5, 사용자가 고정)에 못 미치거나 순열 렌즈와 구분되지 않으면, Part 1은 독립 결과로만 남긴다. Part 3·4의 렌즈는 Cowen-trained로 바꾸고 독립성 주장을 철회한다.
   - 추가 판정: 중복이 광범위하면 독립성 프레임 자체를 포기한다.
2. **K2. 분해 추정기 합성 감사.**
   - 방법: CPU, 기존 데이터. 정답 조성을 심은 합성 데이터와 합성 뇌(영역×수준 배정을 심음)에서 파이프라인이 그것을 회수하는지 확인한다. EmoViS의 −0.95 ~ −1.00 reliability를 재현해 원인을 찾는다.
   - 판정: 구조적 반상관(상보적 몫)이 원인이면 감정별 조성 가설은 영구 폐기하고 profile 수준만 남긴다. 회수에 실패하면 영역×수준 분해를 2c의 encoding 분해로 한정한다.
3. **K3. HK 검정력·특이성 점검 (CPU, MC-72 제외 train/val만).**
   - 방법: 기존 V-JEPA 2 / CLIP 특징과 pymoten으로 (a) 영역×band 상호작용, (b) 2d 부분공간을 PCA-k 및 순열 인코더 null과 비교, (c) 현실적 효과크기에서 subject×stimulus 검정력 시뮬레이션을 한다.
   - 판정: 대다수 피험자에서 어느 영역도 PCA-k와 순열 null을 넘지 못하거나 검정력이 부족하면, Part 2a의 미세조정 갈래(GPU 비용 큼)를 축소하거나 보류한다. 그 경우 2b(헤드만)와 Part 3에 집중한다.

## 6. 사용자가 결정할 질문

1. **MC 규칙.**
   - 선택지: (a) atlas ROI 고정 metric RSA만 허용, imagery는 탐색적. (b) MC 학습 지각 응답으로 디코더 적합을 허용하고, 그 대신 MC를 외부 검사에서 제외. (c) 저자가 run별로 z-score한 데이터의 허용 여부를 별도 판정.
   - 추천: (a). 이유: 규칙과 통합 문서(PROPOSAL_INTEGRATION_2026-11-14 §5)가 이 경우를 예상하고 금지한다. (b)를 택하면 MC가 독립 검사 자격을 잃는다. (c)는 "사전 처리된 공개 데이터는 허용"으로 명시해 기록하기를 권한다.
2. **모델의 자리 (H4).**
   - 선택지: (a) 27-query LabelQueryDecoder를 H4 모델로 유지하고 video branch를 VCE 렌즈로 교체, Part 1-4는 분석층으로. (b) H4를 이 분해 경로로 대체.
   - 추천: (a). 이유: CLAUDE.md v7에서 모델의 존재 근거는 H4뿐이다. 다만 H4의 교차 자극셋 요건은 Emo-FilM이 있어야 충족된다. 어느 쪽이든 34→27 전환을 포함해 docs/notes/project_decisions.md에 먼저 기록한다. H2(어긋난 쌍)는 연속 거리로 Part 2c에 추가한다.
3. **VCE의 situation 수준.**
   - 선택지: (a) PE-Core를 "언어정렬 시각"으로 정직하게 명명. (b) VCE 층화 부분집합 2-3k개에 MC 지침으로 인간 캡션 수집. (c) VLM 생성 캡션(annotator 역할).
   - 추천: 예산이 있으면 (b), 없으면 (a). (c)는 LLM 규칙의 회색지대이고 정서어 누출 위험이 있어 비추천.
4. **주 정서 모델과 GPU 예산.**
   - 선택지: (a) VideoMAE fork ViT-B 전체 미세조정 3갈래 × 3 seed(갈래당 단일 노드 GPU-day 수준). (b) V-JEPA 2/2.1 ViT-L last-N 해제(fine-tuning 루프를 새로 작성해야 하고, run당 수 GPU-day). (c) frozen probe만.
   - 추천: (a). V-JEPA 2.1 frozen 특징은 참조로 둔다.
   - 함께 결정: AlexNet ImageNet 가중치(MATLAB/BVLC 변환, torchvision과 다름)와 HF 가중치를 "git clone" 범위로 인정할지.
5. **Emo-FilM 다운로드 (약 132 GB, git-annex).**
   - 선택지: 지금 시작 / 보류.
   - 추천: 지금 시작. 이유: 측정된 뇌로 하는 유일한 교차 자극셋 검사이고 H4 요건이다. 13개 항목명(Supplementary Table 1)과 27 차원의 대응은 메타데이터만으로 먼저 확인한다.
6. **분석 상수.**
   - 선택지: 차원 27 단일 / 27 + 34 병행. 거리: Euclidean / cosine / 감정별 rank 후 correlation. SESOI 수치.
   - 추천: VCE 경로는 27, Horikawa 재현용 평정 band는 34로 병행. 데이터셋 간 비교는 감정별 rank 변환 후 correlation 거리(척도 불변), Euclidean은 보조. SESOI는 HK 신규 결과를 보기 전에 고정. 0.294 등 기존 수치는 27-d 새 split에서 단일 metric으로 재계산한다(패널 안에서 0.294가 감정별 평균 Pearson인지 per-clip profile Pearson인지 서술이 엇갈렸다).

## 7. 검증 상태 표

| 문헌 / 사실 | 상태 | 비고 및 처리 |
|---|---|---|
| Kragel, Reddan, LaBar & Wager, Science Advances 2019 | verified (PMC) | 마지막 FC만 재학습, 저수준 통제, IAPS r=0.88/0.85 |
| "EmoNet과 HK가 독립이 아니었다" (A의 gap 서술) | **misrepresented** | Kragel의 뇌 검사는 IAPS/GAPED와 영화 클립. 추천에서 gap을 재정의 |
| "Kragel과 정확히 같게" 재학습 (A) | partially | Kragel은 top-1 softmax. 연속 목표 변형으로 명시 |
| Gao, Ajith & Peelen, Communications Biology 2025 | verified / partially | 유발 자극에서는 EmoNet 우세. "등가 = Gao와 일치"는 철회 |
| Conwell, Prince, Kay, Alvarez & Konkle, Nature Communications 2024 | verified (PMC) | diet 지배, cRSA와 veRSA |
| "Conwell 2024가 band를 objective로 정의하는 근거" (D) | **misrepresented** | 언어정렬은 거의 동등, diet가 지배. 추천에서 제거 |
| Conwell, Graham, Boccagno & Vessel, PNAS 2025 | partially (초록) | 정지 이미지, valence/arousal/beauty만. 동기로만 사용 |
| Liu, Bo, Ding & Fang, PLoS Comput Biol 2024 | verified (초록+context) | unit 단위 d' 선택. 부분공간과 readout lesion은 변형이므로 강등 |
| Ratan Murty et al., Nature Communications 2021 | verified | 새 fMRI로 검증. screening은 가설 생성기로 |
| Gu, Jamison, Sabuncu & Kuceyeski 2023; NeuroGen 2022; BrainDiVE NeurIPS 2023 | verified (context) | 모두 정지 이미지. 전향 검증의 선례로만 |
| Jang & Kragel, J Neurosci 2025 | verified (context) | in silico 합성 |
| Jang et al. 2026 bioRxiv | partially (초록만) | 방법 서술 금지 |
| Horikawa & Kamitani, Nature Communications 2017 | verified | 피험자 내, 정지 이미지 |
| Horikawa, Cowen, Keltner & Kamitani, iScience 2020 | verified (PMC) | 1회 제시라 noise ceiling 없음, HCP-MMP, Margulies gradient |
| Horikawa, Science Advances 2025 (MC) | verified (PMC) | cue는 20 캡션 중 하나, imagery 뒤 영상 재시청, run별 z-score, test 중앙값 2.90 s이고 10 s 미만은 반복 재생 |
| "MC 피험자가 매 시청 후 기술을 판단" (D) | **misrepresented** | run당 3-4개 평가 block. 수정 |
| MC trainPerception 표본 수 (2,108 vs 2,180) | 패널 불일치 | 2,180 고유 중 test 영상 run 제외로 2,108일 가능성. figshare에서 확인 필요 |
| Nishimoto et al., Current Biology 2011 | verified | block 평균은 시간 구조를 잃음 |
| Dupré la Tour et al., NeuroImage 2022 | verified (PMC) | 내장 분해는 product measure |
| Lescroart, Stansbury & Gallant, Front Comput Neurosci 2015 | partially (초록) | 7분할 variance partitioning |
| Doerig, Kietzmann et al., Nature Machine Intelligence 2025 | verified (PMC) | "권고"가 아니라 실행한 통제, MPNet. 정서어 마스킹 rung은 선례 없음 |
| Kriegeskorte et al., Nature Neuroscience 2009 | verified | |
| Westfall & Yarkoni, PLoS ONE 2016 | verified (초록) | |
| Lakens, SPPS 2017 | verified (초록) | |
| Margulies et al., PNAS 2016 | verified (초록) | |
| Cowen & Keltner, PNAS 2017 | verified (초록) | 27 범주. multi-select는 로컬 데이터로 정합(행 합 > 1이 99.5%)이나 Methods 미확인 |
| Schaefer et al. 2018; Tian et al. 2020 | verified (메타데이터) | |
| Mehrer et al., Nature Communications 2020 | verified (PubMed) | seed 효과 |
| Du, Fu, Wen & He, iScience 2023 | verified (PubMed/PMC) | 같은 HK에서 banded ridge. 신규성 비교 대상 |
| Fu, Du, Wang & He, IEEE TAFFC 2023 | unverified (web 수준) | PDF 확인 전 인용 보류 |
| Du et al. arXiv 2509.24298 | unverified (INDIRECT) | 신규성 주장 전 원문 필요 |
| St-Yves et al., Nature Communications 2023 | partially (비판자의 PubMed) | |
| Schütt et al., eLife 2023 | partially (PMID만) | 2요인 bootstrap |
| Cameron, Gelbach & Miller 2008; Allefeld et al. 2016; Haufe et al. 2014; Zhang et al. 2017; Nieuwenhuis et al. 2011; Pizzi et al. 2022 (SSCD); Goh et al. 2021; Mohammad 2018 (NRC VAD); Warriner et al. 2013 | unverified | 인용 전 1차 확인 필요. 방법 결정은 이들에 의존하지 않게 구성 |
| Kanwisher et al. 2023; Doerig et al. 2023 (NRN) | partially (초록) | 프레임으로만 |
| Mazeika et al., NeurIPS 2022 D&B (VCE) | partially | 61,046 / 50k / 11,046, 27 강도 0-1(README 검증). 평정자 약 13명, 평균 14.1 s(snippet). 오디오·중복·라벨 집계 방식(1/120)은 미검증 |
| VCE fork 학습 recipe | verified (코드) | K400 자기지도 ViT-B 전체 미세조정, BCE, argmax 평가. "last-N"은 그들의 recipe가 아님 |
| Emo-FilM (Morgenroth et al., Scientific Data 2025) | verified (PMC) | 소리 있음, 13개 항목명 미확인 |
| V-JEPA 2 (Assran et al. 2025) / V-JEPA 2.1 | partially (repo) | frozen probe는 CE. 미세조정 루프 없음 |
| Perception Encoder (Bolya et al. 2025) | partially (repo, 코드) | encode_video는 프레임 평균 |
| DeBERTa (He et al., ICLR 2021) | partially (검색) | MC repo에서 사용 확인 |
| TRIBE v2 (d'Ascoli et al. 2026) | partially | "학습 뇌가 정서 영상을 본 적 없다"는 과장(Friends, 장편영화 포함). backbone 공유로 주 분석에서 제외 |
| Brain-IT (Beliy et al., ICLR 2026) | partially (repo) | "region-level"은 부정확(기능적 GMM cluster). 선택 사항 |
| brain-tuning (Moussa et al., ICLR 2025); ReAlnet (Lu, Wang & Golomb 2026) | partially | "모든 loss가 이미 존재"는 과장(보존항은 CE-argmax, 상관항에 gradient 없음). 제외 |
| Places365 (Zhou et al., TPAMI 2018) | partially | 장면이지 situation이 아님. 제외 |
| 로컬 수치: Cowen 34D 중 73.8%가 0, 자극당 평균 1.7개 범주; 2,196 = 2,185 + 11 | verified (로컬 문서) | |
| 로컬 결과: CLIP bigG 0.505, V-JEPA 2 0.425, ROI 0.294 / 0.313 | 로컬 보고, metric 정의는 패널 불일치 | 27-d 새 split에서 재계산 |
| MC 캡션의 정서어 빈도 (smiling 402 등) | verified (로컬 csv 집계) | 다만 D 검증자의 regex로는 약 2.6%. 정의에 따라 다르므로 lexicon을 사전 고정 |
| emonet-pytorch에 ImageNet fc8 없음, torchvision과 다른 AlexNet | verified (repo) | M0와 O band 출처를 결정해야 함 |

**misrepresented로 판정된 항목은 위 표에서 굵게 표시했고 모두 추천에서 고쳤다.** (1) Kragel 순환성 gap, (2) Conwell 2024를 objective 정의 근거로 쓴 것, (3) MC 평가 block 빈도. 과장 판정 항목(TRIBE v2 "정서 영상 미시청", ReAlnet/brain-tuning "모든 loss 존재", Brain-IT "region-level", fork "last-N recipe")은 제외하거나 표현을 바꿨다. not_found 판정은 패널에 없었다.
