# 심사 대비: 왜 분리 학습인가 (2026-11-25)

전문을 읽은 문헌만 근거로 썼다. 원자료와 인용 위치는 작업 기록(scratchpad sepjoint/result.json)에 있다.

## 심사 답변 초안

자극 모델과 뇌 디코더를 따로 학습하지 않고, 뇌·영상·캡션을 하나의 다중양식 모델로 함께 학습하는 설계도 가능하다는 지적에 동의합니다. 그럼에도 본 연구가 분리 학습을 택한 이유는 다음과 같습니다.

첫째, 본 설계에서 크게 학습되는 모델은 하나뿐입니다. VCE 영상 약 61k개와 27개 정서 강도로 학습한 VideoMAE ViT-B만이 비선형 대형 모델입니다. 뇌 쪽은 피험자별 선형 ridge 디코더이고, 최종 판독기는 VCE에서 학습한 뒤 고정한 정서 head입니다. Doerig 등(The neuroconnectionist research programme, preprint v1, p.21)이 지적하듯 "the number of parameters is a poor proxy of model complexity in ANNs"입니다.

둘째, 본 연구의 질문은 정서 평정이라는 학습 목표가 어떤 시각 단서를 만들어 내고, 그 단서가 뇌 반응에 나타나는가입니다. 이 질문에서 뇌와의 대응이 증거가 되려면 자극 모델은 뇌 자료를 보지 않아야 합니다.
- Yamins & DiCarlo(2016, Nature Neuroscience, p.360)는 목표 기반 모델의 뇌 예측력이 의미를 갖는 근거로 모델이 "not exposed to neural data at all during the training procedure"였다는 점을 들었습니다.
- Kanwisher, Khosla & Dobs(2023, Trends in Neurosciences, p.242)도 과제로만 학습한 망이 뇌와 맞는다는 사실이 "non-obvious and important"하다고 썼습니다.
- 본 연구가 따르는 Kragel 등(2019, Science Advances, Results 'Decoding model representations of emotions from patterns of human brain activity')도 "Treating EmoNet as a model of the brain"이라는 틀에서, 자극만으로 학습한 모델의 표상을 뇌에서 해독했습니다.

뇌 반응을 학습 손실에 넣으면 head 제거로 찾은 단서와 뇌 영역의 대응이 검정할 바로 그 자료에 일부 맞춰집니다. 그래서 저희는 공동 학습이 이 질문에는 맞지 않는다고 판단했습니다.

셋째, 자료 규모입니다.
- Horikawa 등(2020, iScience)의 자료는 피험자당 2,181개 영상이고, 저자들은 "each stimulus was presented only once"라고 밝혔습니다(Discussion).
- Yamins & DiCarlo(p.359)는 이 규모의 fMRI 자료가 심층망을 제약하기에 "several orders of magnitude too little"이라고 했습니다.
- Takagi & Nishimoto(2023, CVPR, p.14454)는 fMRI로 생성 모델을 학습한 선행 연구의 한계를 "partly because the number of samples in neuroscience is small"로 설명했습니다.
- Shen 등(2019, Frontiers in Computational Neuroscience, Introduction)은 이 분야가 "avoid training a DNN model directly on the fMRI data because of limited dataset size in fMRI studies"한다고 정리했습니다.

실제 공동 학습 모델도 같은 제약을 따릅니다.
- BraVL(Du 등 2023, IEEE TPAMI; arXiv:2210.06756)은 영상·텍스트 추출기를 사전학습된 상태로 고정하고 2층 MLP만 함께 학습했습니다. 저자들은 그보다 깊은 비선형 변환이 "prone to over-fitting"이었다고 보고했습니다(§4.3.4).
- 정서 영역의 공동 학습 모델인 Gryshchuk 등(2025, ICMI)은 "As we work on a low data regime"이라는 이유로 이미지 encoder를 고정했습니다(§4.1). 그리고 "The Brain-supervised model achieves higher classification results than BALE across all datasets and data-splitting strategies"라고 보고했습니다(§6.1).

넷째, 결과를 어디에 귀속할 수 있느냐의 문제입니다.
- Horikawa(2025, Science Advances, Discussion)는 뇌에서 출력으로 직접 사상하는 방식이 "requiring large-scale brain data and introducing architectural complexity that complicates attribution"이라며 선형 두 단계 경로를 택했습니다.
- Kamitani, Tanaka & Shirakawa(2025, Annual Review of Vision Science, p.622)는 선형 translator가 "the risk of falsely attributing neural encoding to spurious model features"를 줄인다고 정리했습니다. 같은 리뷰는 시각 특징과 의미 특징을 한 잠재공간에 합치는 일이 "must be handled carefully to prevent spurious reconstructions"라고 경고합니다(pp.621-622).

공동 학습이 원리적으로 잘못되었다는 뜻은 아닙니다. Doerig 등(p.9)은 신경 자료에 직접 맞춘 학습을 "a way to test hypotheses about which architectures are capable of reproducing neural dynamics"로 인정하는데, 이는 본 연구와 다른 질문에 답하는 방식입니다. 또 Shen 등(2019, Discussion)이 지적했듯 특징 병목은 정보를 잃을 수 있습니다("if enough training samples are available, direct mapping may help in preventing this information loss"). 그래서 저희는 같은 자료와 같은 fold에서 뇌에서 정서 평정으로 바로 가는 ridge 디코더를 함께 보고합니다. 이로써 단서 특징을 거치는 경로가 뇌가 지닌 정서 평정 정보 중 얼마를 담고 얼마를 놓치는지를 분해 형식으로 제시합니다.

끝으로, 뇌 자료 없이 학습한 자극 모델의 특징을 선형으로 해독한 뒤 자극에서만 학습한 판독기를 적용하는 구조는 이 분야에서 확립된 경로입니다. Horikawa & Kamitani(2017, Nature Communications)는 "None of the categories in the candidate set were used for decoder training"인 판독 집합을 썼고, VanRullen & Reddy(2019, Communications Biology, Discussion)는 "the burden of absorbing the complexity of human face representations should lie in the generation of the latent space, rather than in the brain decoder"라고 했습니다.

## 가장 가까운 선례

결론부터: 우리 설계와 똑같이 한 논문은 찾지 못했습니다. 이번에 전문을 읽은 범위 안에서의 결론이며, 망라적 검색은 아닙니다.

우리 설계의 요소는 여섯 가지입니다.
- (a) 뇌 자료 없이 자극과 정서 평정으로 학습한 자극 모델
- (b) 모델 내부 단위(head) 제거로 정서별 단서 특정
- (c) 단서와 뇌 영역의 대응
- (d) 뇌 → 단서 특징(선형) → VCE에서 학습해 고정한 readout → 정서 프로파일 (Koh 2020식 독립 병목)
- (e) 같은 자료, 같은 fold에서 뇌 → 정서 직접 ridge 비교
- (f) 손상 정도를 맞춘 무작위 head 대조

이 여섯 가지를 모두 가진 연구는 없습니다. 특히 (b)+(d)+(e)+(f)의 조합, 즉 "뇌에서 해독한 단서 특징 → 고정 정서 readout"을 같은 자료의 직접 디코더와 나란히 놓고 단위 제거로 검정한 사례는 정서 분야에도, 다른 분야에도 없었습니다.

가까운 순서는 다음과 같습니다.

1. Kragel, Reddan, LaBar & Wager 2019, Science Advances 5:eaaw4358 (PubMed PMID 31355334로 서지 확인; DOI https://doi.org/10.1126/sciadv.aaw4358). 프레임은 가장 가깝지만 3단계 구조는 중간 정도입니다.
- 가진 것 (a): EmoNet은 AlexNet에서 fc8만 Cowen 영상 프레임으로 재학습했습니다. Methods: "We fixed all but the last fully connected layer of AlexNet".
- 가진 것 (d)의 일부: 뇌 → EmoNet fc8 출력(PLS)입니다. Results: "we used PLS to regress patterns in EmoNet's emotion category layer onto patterns of fMRI responses to the same images". 다만 평가 대상이 사람 평정이 아니라 모델 출력이고, 중간 단서 특징을 거쳐 readout으로 가는 경로가 아닙니다.
- (e)의 직접 디코더는 다른 자료에서 했습니다. "in an independent dataset [n = 32; see (15)]", 7범주 PLS-DA입니다.
- 없는 것: (b), (f).
- 피할 것: argmax 혼동행렬("the EmoNet unit with the highest correlation was taken as the best-guess emotion category")은 프로젝트 규칙상 따라 하면 안 됩니다.
- 주의: EmoNet이 Horikawa 2020 클립의 원천인 Cowen 영상으로 학습된 것과 같은 누수 위험이 우리 쪽(VCE와 Cowen/Horikawa 클립)에도 있습니다.

2. Horikawa & Kamitani 2017, Nature Communications 8:15037. 3단계 구조로는 가장 가깝습니다.
- 자극 CNN과 단위별 SLR 디코더가 있습니다.
- readout은 fMRI에 쓰지 않은 ImageNet 이미지로 만든 범주 평균 특징입니다. "None of the categories in the candidate set were used for decoder training."
- 실제 자극 특징을 기준으로 한 식별 결과(Supplementary Fig. 17)를 함께 보고했습니다.
- CNN 학습 클래스와 겹친 20개 범주를 빼고 재분석했습니다. "the identification accuracy with the other 30 non-overlapping categories alone was qualitatively similar".
- 한계: 정서가 아니고, top-1 식별이며, 직접 디코더 비교가 없습니다.

3. VanRullen & Reddy 2019, Communications Biology 2:193.
- 자극에서만 만든 readout이 있습니다. CelebA 남녀 각 10,000장으로 계산한 gender 축을 뇌에서 해독한 latent에 적용했습니다.
- 상한도 함께 보고했습니다. 실제 latent 85%("This is the classifier's ceiling performance")와 뇌 해독 latent 70%입니다.
- 한계: 정서가 아니고, 같은 자료의 직접 디코더 없이 선행 MVPA 수치(<60%)만 인용했습니다.

4. Horikawa 2025, Mind captioning, Science Advances 11:eadw1464.
- 같은 영상 집합, 같은 연구 계보입니다.
- 구조는 뇌 → 고정 LM 특징(L2 선형) → 고정 MLM 생성기입니다.
- 직접 사상을 피한 이유를 명시했습니다("complicates attribution", "enabling localization of potential information loss").
- 한계: 표적이 텍스트이고 직접 디코더 기준선이 없습니다.

5. Du, Fu, Li & He 2023 (BraVL), IEEE TPAMI. 서지는 arXiv:2210.06756v2 comments 기준입니다.
- 이름은 공동 학습이지만, 구조는 고정 추출기와 2층 MLP입니다.
- 마지막 단계는 자극 쪽 latent로 SVM을 학습해 고정한 뒤 뇌 latent에 적용합니다. "Note that the encoders Ev and Et are frozen in this step." 같은 He 그룹의 '고정 readout' 선례입니다.
- 한계: 물체 범주이고, 분리 선형 디코더 기준선이 없습니다.

6. Shen, Dwivedi, Majima, Horikawa & Kamitani 2019, Frontiers in Computational Neuroscience 13:21. 같은 자료에서 직접(end-to-end) 방식과 두 단계 방식을 정면 비교한 유일한 사례입니다.
- 픽셀 상관은 비슷했지만("ours 78.1 vs. 76.1%"), 사람 판단은 end-to-end가 낮았습니다(95.7 vs 99.1%).
- end-to-end 모델도 고정된 사전학습 comparator에 의존했습니다.
- 우리 직접 ridge 비교를 분해로 쓸 때 인용할 근거입니다.

7. Pereira 등 2018 (Nature Communications 9:963)와 Takagi & Nishimoto 2023 (CVPR)은 일반적인 분리 설계(코퍼스/생성 모델은 고정, 뇌 쪽은 선형)입니다. readout 비교와 직접 디코더가 없습니다.

분리 설계가 아닌 것:
- Gao, Ajith & Peelen 2025 (Communications Biology 8:697; PubMed PMID 40325234로 서지 확인; DOI https://doi.org/10.1038/s42003-025-08145-1): 모델 층 → 평정과 ROI → 평정(PLSR)을 따로 맞추고 글로만 연결했습니다.
- Horikawa 등 2020 (iScience 23:101060; PubMed PMID 32353765로 서지 확인; DOI https://doi.org/10.1016/j.isci.2020.101060): 뇌에서 정서를 직접 해독했습니다.
- Gryshchuk 등 2025 (ICMI)와 Palazzo 등 (arXiv:1810.10974v2): 공동 학습입니다.

함의:
- (d)+(e)+(b) 조합은 새로울 수 있습니다. 다만 그만큼 이 비교를 왜 하는지를 논문 안에서 정당화해야 합니다.
- 아래 leads 중 Cammarota 등(NeurIPS 2025, 의미 병목)과 Fu 등 2023 TAFFC를 읽기 전에는 "최초"라는 표현을 쓰면 안 됩니다.

## 무게 배치 (Kragel 2019, Gao 2025의 절 구성)

0. 먼저 확인할 것: "큰 모델 2개"라는 지적이 그대로 맞는 경우가 있습니다.
- docs/notes/methods_spec_2026-11-25/story_v4.md 3단계의 1순위는 EmoBrain 디코더입니다. 370개 영역 토큰에 self-attention을 걸고, 정서 query가 cross-attention으로 읽으며, 시각·캡션 feature head를 둡니다.
- 이것은 뇌에서 학습하는 두 번째 비선형 모델이고, 사실상 뇌+영상+캡션 다중양식 모델입니다. 이 경우 심사위원 질문이 정확히 맞고, 위 답변의 "뇌 쪽은 선형" 논거는 쓸 수 없습니다.
- 근거 문헌도 이 규모에서는 깊은 뇌 학습 모델에 불리합니다.
  - BraVL: 2층보다 깊으면 과적합.
  - Gryshchuk: 단일 제시 fMRI에서 뇌만으로 지도학습한 모델보다 낮음.
  - Yamins & DiCarlo p.359: "several orders of magnitude too little".
- 권고:
  - 이번 원고의 3단계는 선형 병목 경로로 확정합니다.
  - EmoBrain 디코더는 이번 원고에서 뺍니다.
  - 넣는다면 "셋이 한 공간으로 통합되는가"라는 별도 질문(CLAUDE.md의 H4 자리)으로 분리합니다. Doerig 등의 기준인 "which aspects of cognition can only be modeled jointly"가 이 자리입니다.
  - decisions.md의 열린 결정("뇌 → 정서 디코더가 이 대응을 어떻게 쓰는지")과 CLAUDE.md v7의 H4 서술이 서로 다르므로, 사용자가 정해야 합니다.

1. Kragel 2019의 배치 (scratchpad kragel2019.txt; 줄 번호는 로컬 텍스트 기준)
- 서론에서 하나의 가설에서 세 예측을 끌어냅니다(l.9): "First, models constructed from image features alone should be able to (i) predict normative ratings of emotion category made by humans and (ii) differentiate multiple emotion categories. Second, representations in these models should map onto distinct patterns of brain activity in sensory (i.e., visual) cortices. Third, sensory areas, and particularly visual cortex, should be sufficient to decode multiple emotion categories." ... "Here, we test each of these hypotheses."
- Results 절 순서: 모델 3개 다음 뇌 2개입니다.
  - "Classifying visual images into multiple emotion categories" (l.17)
  - "Modeling valence and arousal as combinations of emotion-related features" (l.29)
  - "Classifying the genre of movie trailers based on their emotional content" (l.39)
  - "Decoding model representations of emotions from patterns of human brain activity" (l.49)
  - "Classifying patterns of visual cortex activity into multiple distinct emotion categories" (l.61)
- 뇌 절의 첫 문장은 같은 주장에서 나온 조건문입니다(l.51): "If emotion schemas are afforded by visual scenes, then it should be possible to decode emotion category–related representations in EmoNet from activity in the human visual system."
- 직접 디코더 절은 보강 증거로 자리매김합니다(l.63): "To provide additional evidence that visual cortical representations are emotion category–specific, we tested whether visual cortical activity was sufficient to decode the category of emotional videos in an independent dataset".
- 같은 뇌 절 안에서 영역 비교(후두엽 대 전뇌 대 개별 시각 영역, l.59)로 국소화까지 합니다.
- Discussion 첫 문단은 예측 번호 순서로 결과를 정리합니다(l.71): "Consistent with our prediction that image features alone are sufficient ... Supporting our second prediction ... Last, our third prediction was supported by the observation that patterns of occipital lobe activity were sufficient for decoding".
- 뇌 해독은 PLS 한 계열뿐입니다(l.135, l.163). 제목도 주장 하나입니다(Emotion schemas are embedded in the human visual system).

2. Gao 2025의 배치 (scratchpad gao2025.txt)
- Results는 모델 3개, 뇌 1개입니다.
  - "Object representations in deep neural networks predict emotion ratings of daily-life scenes" (l.17)
  - "Emotion information is processed in hierarchical stages of the object recognition system" (l.41)
  - "Representational similarity of emotional information is greater within than between object categories" (l.55)
  - "Activity patterns in object-selective cortex predict emotion ratings" (l.63)
- 뇌 절은 앞 절 결과를 요약하고 그것을 예측으로 바꾸며 시작합니다(l.65): "The previous analyses showed that object category representations reliably predict emotion ratings of daily-life scenes ... If emotion recognition relies primarily on the visual object recognition system, we would expect the object-selective visual cortex (i.e., the LOC) to outperform all other visual regions".
- 뇌 절은 모델 결과로 되돌아가며 끝납니다(l.79): "These findings are consistent with previous findings showing that successive layers in AlexNet lead to significant improvements in predicting emotion ratings. These results suggest that emotion ratings are driven by object representations encoded in the LOC region".
- Discussion도 같은 방식으로 묶습니다(l.91): "Together with the demonstrated link between object categories and emotion and the findings of hierarchical processing of emotional information in AlexNet, these results collectively illustrate that emotion processing in everyday scenes and objects depends on the visual object recognition system."
- 서론 요약에서도 뇌 결과는 한 구절입니다(l.13): "with the lateral occipital complex (LOC) playing a particularly prominent role."
- 뇌 쪽 검정은 정확도 자체가 아니라 영역 대비(LOC 대 다른 영역, Heschl 대조)입니다. 방법도 PLSR 하나입니다(l.71). 한계 절에서 인과가 아님을 밝힙니다(l.95).

3. 두 논문에서 가져올 규칙
- (i) 제목·초록에는 주장을 하나만 둡니다. 예: "정서마다 영상 모델이 의존하는 시각 단서가 다르고, 그 단서는 서로 다른 피질 영역의 반응을 설명하며, 뇌에서 해독한 그 단서만으로 정서 프로파일이 복원된다". decisions.md 결정 2에 디코딩을 세 번째 예측으로 붙인 형태입니다.
- (ii) 서론 끝에 예측 P1(1단계), P2(2단계), P3(3단계)을 번호로 적습니다. Discussion 첫 문단도 그 번호대로 씁니다(Kragel 방식).
- (iii) 3단계는 Results의 마지막 한 절, 본문 그림 한 장으로 둡니다. 뇌 절의 비중은 Kragel 5절 중 2절, Gao 4절 중 1절입니다.
- (iv) 그 절의 첫 문장은 조건문으로, 마지막 문장은 1·2단계 결과로 되돌아가게 씁니다. 예시 첫 문장(영문 원고용): "If each emotion's rating profile depends on the cue information identified by head removal, then cue features decoded from brain activity should recover the rating profile through a readout learned from VCE alone, and removing emotion k's dependent heads should reduce the decoded profile most for emotion k."
- (v) 방법은 선형 ridge 한 계열로 통일합니다. 성능 표나 순위는 넣지 않습니다. 보고 지표는 상한 대비 비율과 대각 우위입니다.
- (vi) 정서별·영역별 디코딩 자체는 Horikawa 2020이 이미 했습니다(decisions.md). 따라서 3단계는 "같은 주장의 세 번째 검정"일 때만 무게를 얻습니다.

4. 최소 3단계 세트 (본문)
- (1) 병목 경로
  - 피험자별 ridge로 뇌 → VideoMAE 단서 특징을 해독합니다. 뇌 입력은 전뇌, 또는 2단계 영역 묶음을 학습 fold 안에서 고른 것입니다. 특징은 2단계에서 고정한 위치의 pooled 특징입니다.
  - 해독한 특징을 고정 VCE readout에 넣어 27차원 프로파일을 얻습니다.
  - held-out 클립의 평정과 연속 프로파일 상관·거리로 평가합니다. top-1이나 범주화는 쓰지 않습니다.
- (2) 상한
  - 같은 held-out 클립의 실제 자극 특징을 같은 readout에 넣은 값을 함께 보고합니다.
  - 뇌 경로는 이 상한 대비 비율로 씁니다(VanRullen & Reddy Fig. 6의 85% 대 70%, Horikawa & Kamitani의 true-feature 분석 방식).
- (3) 직접 ridge
  - 같은 fold에서 뇌 → 27개 평정을 직접 맞춥니다.
  - 병목 경로와 공유하는 분산과 직접 경로에만 있는 분산으로 분해해 보고합니다. "이긴다/진다"로 쓰지 않습니다.
  - 해석 근거는 Shen 2019의 "information in the decoded features is not all the visual information that can be decoded from the brain"입니다.
- (4) 대각 우위 검정. 3단계를 같은 주장에 묶는 핵심입니다.
  - 정서 k의 의존 head를 제거한 특징 공간으로 같은 병목 경로를 다시 돌리면, 해독된 정서 k 점수가 다른 정서보다 더 떨어져야 합니다. 1단계의 27×27 하락 행렬과 같은 형식입니다.
  - 대조는 손상 정도를 맞춘 무작위 head 집합입니다.
  - story_v4의 영역 지도 기반 대각 우위(정서 k 지도 영역에서 정서 k가 더 잘 해독됨)는 2단계와 겹치므로 보충으로 돌리거나, 둘 중 하나만 본문에 둡니다.
- (5) 필수 대조 (보충 자료)
  - readout-prior 대조: 클립 짝을 섞은 해독 특징을 readout에 넣습니다. Kamitani 등 p.626의 원리입니다.
  - VCE와 Horikawa/Cowen 클립의 중복 점검, 그리고 비중복 클립 재분석: Horikawa & Kamitani 2017, Kamitani 등 p.623.
  - MindCaptioning 6명 재현.

5. 뺄 것
- 이번 원고에서 EmoBrain transformer 디코더.
- 여러 디코더나 공동 학습 모델과의 비교 표.
- Kragel식 argmax 혼동행렬.
- "디코딩 성능" 문장.
- BrainCLIP의 "BraVL보다 낫다"식 비교 인용. 비심사 preprint이고 경쟁 프레임입니다.

이렇게 두면 디코딩은 별도 기여가 아니라 1·2단계 주장의 세 번째 검정이 됩니다. 무게는 1단계(단서 특정)와 2단계(영역 대응)에 남습니다.

## 읽지 못한 단서 (새로움 주장 전에 확인)

- Cammarota S, Ferrante M, Toschi N. Bridging Brains and Concepts: Interpretable Visual Decoding from fMRI with Semantic Bottlenecks (NeurIPS 2025로 검색 결과에만 표기, 서지 미확인). OpenReview PDF 차단으로 검색 스니펫만 봄. 뇌 -> 해석 가능한 개념 병목 구조로, 우리 독립 병목과 가장 가까울 가능성. '최초' 주장 전에 반드시 전문 확인.
- Fu K, Du C, Wang S, He H. Improved Video Emotion Recognition with Alignment of CNN and Human Brain Representations. IEEE Transactions on Affective Computing 2023 (doi 10.1109/TAFFC.2023.3316173, 검색 스니펫 기준으로 미검증). 전문 미확보(arXiv 없음; IEEE Xplore, osf.io, bohrium 차단; Drive 없음). 같은 정서 영상 자료에서 자극 모델을 뇌에 정렬한 He 그룹 연구로 보여, 심사위원이 비교 대상으로 들 가능성이 가장 큼.
- Du C, Lu Y, Huang Z, Sun Y, Zhou Z, Qin S, He H. Bridging the behavior-neural gap: A multimodal AI reveals the brain's geometry of emotion more accurately than human self-reports. arXiv:2509.24298 (2025). 이번 작업에서는 초록만 읽음. decisions.md에는 이전 세션의 검토 기록이 있으나 이번 근거로는 쓰지 않음.
- Fu K, Du C, Wang S, He H. Multi-view Multi-label Fine-grained Emotion Decoding from Human Brain Activity. arXiv:2211.02629 (comments상 IEEE TNNLS 채택). 초록만 읽음. Drive fileId 18j3eHeJ1PYEsqZX36RMSyu9EWKYnAnb_에 PDF 있음. 정서 자료에서 뇌만으로 학습한 깊은 디코더의 자료 요구량 판단에 필요.
- Du C, Fu K, Wen H, He H. 2023 iScience 정서 지형도 논문 (decisions.md에 미독으로 기록됨).
- Nishida S, Nishimoto S. 2018 NeuroImage, 그리고 Palatucci M 등 2009 NeurIPS (zero-shot 뇌 디코딩). 전문 접근 불가.
- Palazzo 등 블록 설계 교란을 지적한 후속 비판 논문들 (미독). Palazzo를 인용하기 전에 확인 필요.
- Doerig 등 The neuroconnectionist research programme 정식 출판본 (preprint v1만 읽음; 인용 문구가 출판본에서 달라졌을 수 있음).
- 읽지 않은 보충 자료: Kragel 2019 Supplementary Text 및 fig. S6; Horikawa & Kamitani 2017 Supplementary Figs. 15, 17; Mind captioning figs. S5-S10; Gryshchuk 2025 Supplementary Material; Takagi & Nishimoto 2023 Appendix A-C; Gao 2025 Supplementary information. 본문에서 언급된 내용만 인용함.

## 추가: Fu 등 2024 (전문 확인, 2026-11-25)

Fu, K., Du, C., Wang, S., & He, H. (2024). Improved video emotion recognition with alignment of CNN and human brain representations. IEEE Transactions on Affective Computing, 15(3), 1026-1040. https://doi.org/10.1109/TAFFC.2023.3316173 (2023년 9월 온라인 공개). 본문 pp.1026-1039를 읽었고 부록은 보지 못했다. 코드: https://osf.io/ucx57

**무엇을 했나**
- 같은 자료다. Horikawa 2020의 2,196개 영상, 5명(S01-S05)을 쓰고, 2,181개 고유 영상을 공동 학습에 썼다.
- Kinetics로 사전학습한 3D CNN 여섯 종과 VAANet-V를 다른 영상 정서 자료(VideoEmotion8 1,101개, Ekman6 1,637개)로 분류 학습하면서, 같은 망에 HK 영상을 넣어 얻은 층별 유사도 행렬을 뇌 유사도 행렬에 맞추는 손실을 더했다: "L = Lcls + αLsim" (식 8).
- 뇌 쪽 신호는 banded ridge encoding으로 만든다. 34개 정서 평정과 motion energy 6,555개를 함께 넣어 맞춘 뒤, "Compute the prediction of the banded ridge model with only emotion features X1 as input to obain denoised fMRI" (Algorithm 1)이고, 정서 encoding 정확도가 문턱(p<0.01, FDR)을 넘는 voxel만 쓴다.
- 결과: 뇌 정렬 학습이 두 영상 자료의 분류 정확도를 높였다. 영역별로는 TPJ와 DMPFC가 가장 도움이 되었고, 전뇌 정서 관련 voxel이 개별 영역보다 나았으며, VMPFC는 encoding 정확도가 낮아 빠졌다. 학습 후 망의 유사도 행렬이 뇌와 더 닮았다(Spearman ρ 0.55 대 0.46, 0.53 대 0.47).
- 저자들의 목표: "our goal here is not to achieve SOTA video emotion classification performance, but rather to determine whether and how we could use the brain to guide the training of ANN".
- 저자들의 한계: "a lack of data hinders the application of our framework to larger models".

**우리 설계와의 관계**
- 같은 자료에서 뇌 정렬 학습(앞서 뺀 (ㄴ))을 한 직접 선례다. 심사위원이 "왜 뇌와 함께 학습하지 않았나"를 물을 때 가장 먼저 들 논문이다.
- 방향이 반대다. Fu는 뇌를 교사로 써서 모델을 고치고, 다른 영상 자료의 범주 분류(top-1)로 평가한다. 우리는 뇌를 보지 않은 모델이 쓰는 단서를 단위 조작으로 찾고, 그 단서와 뇌 영역의 대응, 뇌에서 해독한 단서로 정서 프로파일이 복원되는지를 본다.
- 구조상 주의할 점(우리의 읽기): Fu의 "denoised fMRI"는 34개 정서 평정으로 맞춘 encoding 모형의 예측값이다. 따라서 정렬 대상 유사도 행렬에는 평정의 구조가 voxel 가중치를 거쳐 들어 있다. 저자들은 뇌 신호가 행동 평정보다 낫다고 해석했지만, 두 신호가 독립은 아니다.
- 쓸 수 있는 근거: 영역 결과(TPJ, DMPFC, 전뇌 정서 voxel)와 motion energy를 함께 넣어 시각 정보를 떼어 내는 banded ridge 절차는 우리 2단계의 예상 영역과 분해 방식에 대한 선행 근거다. "a lack of data hinders..." 문장은 분리 학습 답변의 자료 규모 논거에 더한다.
