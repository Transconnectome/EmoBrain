# EmoBrain 연구 개요

설계의 근거와 결정 기록은 [docs/final/01_integrated_document.md](docs/final/01_integrated_document.md)에 있다. 이 문서는 그 요약이고, 둘이 다르면 01을 따른다. 결과는 논문 공개 뒤에 더한다.

## 무엇을 묻나

정서는 장면의 시각 정보와 그 장면의 의미가 함께 처리되어 생긴다는 전제에서 출발한다. 그렇다면 정서 영상을 볼 때의 뇌 반응에도 두 정보와의 연결이 있어야 한다.

- **질문 1 (정서 신경과학).** 시각 자극을 볼 때 나타나는 정서 관련 뇌 반응은, 장면의 시각적 특성과 의미에 어떻게 연결되어 있는가?
  - 1-1. 정서마다 어느 정보와 더 강하게 연결되는가
  - 1-2. 두 정보는 따로 보태는가, 서로에 따라 달라지는가
  - 1-3. 그 연결의 정보는 어느 뇌 영역에 있는가
  - 1-4. 처음 보는 종류의 장면에서도 그 연결이 유지되는가
- **질문 2 (모델).** 이러한 장면 정보와의 연결을 학습에 활용하면, 뇌만으로 정서 점수를 예측하는 방식은 어떻게 달라지며, 처음 보는 장면에서는 어떤 정보를 이용해 예측하는가?
  - 2-1. 뇌 모델은 뇌 반응에서 장면 정보를 decoding하는가
  - 2-2. 정서를 예측할 때 decoding한 장면 정보를 쓰는가
  - 2-3. 그렇게 학습하면 예측과 일반화가 나아지는가
  - 2-4. 모델은 어느 영역에 기대는가

정서는 스캔 참가자가 느낀 정서가 아니라, 다른 사람들이 그 영상에 매긴 평정(34개 범주, 평정자 비율 0~1)이다. 그래서 "정서 관련 뇌 반응"이라고 쓴다.

## 자료

| 자료 | 내용 | 쓰임 |
|---|---|---|
| Horikawa 외 2020 (HK) | 5명, 정서 영상 2,196개 시청 fMRI, 정서 34개 평정 | 학습과 개발. MC 최종 시험과 같은 내용의 영상을 빼고 2,109개 |
| MindCaptioning (MC) | 다른 참가자 6명, 같은 영상 묶음 시청 fMRI, 영상마다 사람 캡션 20개 | 캡션의 출처, 마지막 일반화 시험(시험 영상 72개는 튜닝과 선택에 쓰지 않음) |

뇌 반응은 ROI 370개(HCP360 피질 360개와 피질하 10개, 저자 공개 ROI)로 나눈 voxel 값이다. 분할은 run 묶음 단위의 6 fold이고, 정서 평정과 영상 길이로 층화했다(`splits/hk_dev_v4/`).

## 장면 정보를 나타내는 두 feature

뇌 신호에는 "이것이 시각 정보다"라는 이름표가 없어서, 출처가 다른 두 표현을 기준으로 쓴다. 두 모델은 학습하지 않고 feature를 한 번 뽑아 둔다.

- **Vision feature:** 영상 → V-JEPA 2 (block 10, 20, 30, 40의 평균, 5,632차원). 보이는 것
- **Caption feature:** 사람이 쓴 캡션 → DeBERTa-large (층 6, 12, 18, 24, 4,096차원). 사람이 이해한 내용. MindCaptioning이 같은 영상에서 고른 언어 모델이다

두 feature는 정보 종류를 깨끗이 나눈 측정이 아니라 출처가 다른 두 표현이다. 캡션도 영상을 보고 쓴 글이라 시각 정보를 담는다.

## 모델

**Stimulus Model (뇌 없음).** Input: Vision + Caption → Output: Emotion

```
logit = a(v) + b(c) + U[(Av) ⊙ (Bc)]      r = 0이면 더하기만 남는다
```

영상만으로 정서를 얼마나 맞히는지 보고, 그 예측을 distillation의 목표로 쓴다.

**뇌 모델 (시험 입력은 뇌뿐).**

```
ROI 370개의 voxel → ROI마다 선형 변환 → token 370개
→ Transformer block (token끼리 self-attention)
→ emotion query 34개가 cross attention → 정서 점수 g
→ (조건에 따라) feature query 2개 → decoded Vision v̂, decoded Caption ĉ
```

조건은 장면 정보를 쓰는 정도에 따라 여섯 묶음으로 나눈다. -2는 같은 구조에 distillation(Stimulus Model 예측을 정답에 섞기)을 더한 것이다.

| 묶음 | 조건 | Output과 정서 계산 | 학습 목표 |
|---|---|---|---|
| A. 장면 정보를 쓰지 않음 | A-1. Brain → Emotion | 정서 = g | 사람 평정 |
| | A-2. Brain → Emotion [distillation] | A-1과 같음 | 사람 평정과 Stimulus Model 예측을 섞은 값 |
| B. 학습 신호로만 | B-1. Brain → Emotion + Vision + Caption | 정서 = g. v̂, ĉ는 손실에만 | 사람 평정 + Vision, Caption feature 맞히기 |
| C. 뇌 경로 + 장면 경로, 공유 encoder | C-1. Brain + Decoded Feature → Emotion | 정서 = g + a(v̂) + b(ĉ) + U[(Av̂) ⊙ (Bĉ)] | B-1과 같음. v̂, ĉ에는 stop-gradient |
| | C-2. … [distillation] | C-1과 같음 | C-1 + A-2의 정답 |
| D. 뇌 경로 + 장면 경로, 분리 encoder | D-1. … [separate feature encoder] | C-1의 식에 feature만 학습한 encoder 2의 v̂₂, ĉ₂를 넣음 | C-1과 같음. encoder 2는 feature 손실만 |
| | D-2. … [separate feature encoder, distillation] | D-1과 같음 | D-1 + A-2의 정답 |
| E. 장면 경로만 | E-1. Decoded Feature → Emotion | 정서 = a(v̂₂) + b(ĉ₂) + U[(Av̂₂) ⊙ (Bĉ₂)]. g 없음 | 고정한 encoder 2 위에 정서 head만 사람 평정으로 |
| F. 중간 표현 전달 | F-고정, F-학습. Brain → Emotion [representation] | 정서 = Multimodal Model에서 가져온 head(중간 표현) | 사람 평정 + Multimodal Model(Brain + Vision + Caption)의 중간 표현 맞히기. head를 고정(F-고정)하거나 함께 학습(F-학습) |

C, D의 v̂, ĉ에는 정서 손실이 decoding 쪽으로 흐르지 않게 막는다. 그래야 v̂를 다른 영상의 것으로 바꿔 끼웠을 때 정서 예측이 따라 움직이는지(질문 2-2) 검사할 수 있다. D는 v̂₂, ĉ₂를 정서 평정을 보지 않은 encoder 2에서 만들어, 공유 encoder를 거쳐 정서 학습의 영향이 섞이는 길도 끊는다. 그래도 뇌 반응 자체의 정서 신호가 섞일 수는 있다.

## 평가와 분석

- **성능:** 정서별 Pearson r을 시험 영상에 걸쳐 내고 34개 정서와 참가자에 걸쳐 평균한다. 설정은 검증 fold로 고르고 시험 fold는 평가에만 쓴다.
- **기준선:** 뇌 → 정서 ridge, soft BCE 선형, 영상 길이, 저수준 시각 특징, Horikawa 2020 복셀 선택 ridge, 외부 모델(GED, ML-BVAE, EmoGrowth)
- **대조군:** label smoothing(평균 쪽으로만 부드럽게), Stimulus 예측을 다른 영상과 섞기, feature 짝을 섞기
- **바꿔 끼우기 (2-2, 1-1):** 학습한 모델에서 v̂ 또는 ĉ만 다른 영상의 것으로 바꿨을 때 정서 예측 변화가 두 영상의 평정 차이에 대응하는지
- **더하기 대 상호작용 (1-2):** 더하기 head와 상호작용 head의 정서별 비교
- **영역 (1-3, 2-4):** CAB-NP 13개 네트워크마다 그 입력만으로 다시 학습하기, 학습한 모델에서 네트워크 입력 교란하기
- **처음 보는 장면 (1-4, 2-3):** 내용 구역 하나를 학습에서 통째로 빼고 그 구역 영상으로 시험, 같은 양을 무작위로 뺀 대조와 비교
- **MC 전이:** 다른 참가자 6명이 본 시험 영상 72개에서 마지막 일반화 값

## 주장의 범위

결과는 뇌 신호에 담긴 정보와 모델이 그 정보를 쓰는 방식에 대한 것이다. 뇌 안의 계산 방식이나 어느 영역이 정서를 만든다는 주장으로 넓히지 않는다. 모델 구조가 다른 구조보다 낫다는 주장도 하지 않는다.
