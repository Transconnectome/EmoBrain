# 작업별 프롬프트

[`WORKPLAN.md`](WORKPLAN.md)의 각 작업에 대응하는 프롬프트다. AI 코딩 에이전트
(Claude Code, Cursor 등)에 **코드블록 안을 그대로 붙여넣으면** 된다.

경로는 전부 저장소 루트 기준이고 **2026-09-07에 존재를 확인**했다.

## 쓰기 전에 — 모든 프롬프트에 공통으로 붙일 규칙

아래 블록을 각 프롬프트 앞이나 뒤에 붙여라. 이걸 빼면 에이전트가 그럴듯한 숫자를
지어내거나, 실패를 조용히 넘기거나, 결과를 보고 기준을 바꾼다.

```
[공통 규칙]
- 숫자를 추측하거나 예시값으로 채우지 마라. 계산해서 나온 값만 쓴다.
- 파일이 없거나 형태가 예상과 다르면 멈추고 보고하라. 대체 데이터를 만들지 마라.
- 결과를 보고 나서 임계값·제외 기준·모델 설정을 바꾸지 마라. 바꿔야 한다면
  왜 바꾸는지 먼저 보고하고 승인을 받아라.
- 감정 차원별 결과를 다루면 반드시 docs/review_2026-09/verify_label_order.py 의
  check_order() 를 먼저 호출하라. 라벨 CSV에는 감정 이름이 없다.
- 피험자는 5명뿐이다. bootstrap/순열은 subject-clustered로 한다.
  자극 단위 resampling은 신뢰구간을 지나치게 좁게 만든다.
- 상관계수를 보고할 때는 noise ceiling(0.678) 대비 %를 반드시 병기하라.
- 마지막에 "확실하지 않은 점" 항목을 만들어 스스로 못 미더운 부분을 적어라.
```

---

## P1. H1 감쇠 보정 등가 검정

```
EmoBrain 프로젝트의 H1 가설 검정을 감쇠 보정 + 등가 검정으로 다시 구현해줘.

[배경]
H1은 "시각-의미 내용 특징이 감정 평정만큼 뇌 표상 기하를 설명한다"는 등가 주장이다.
문제: 감정 평정은 crowd 측정값이라 신뢰도가 0.673(cosine RDM 기준)인데,
영상 특징은 영상의 결정적 함수라 신뢰도가 1.0이다. 따라서 관측 상관에서
영상 특징이 약 22% 유리하게 출발한다. 지금 설계는 가설이 원하는 방향으로 편향돼 있다.

[입력]
- project/shared/data/cowen_horikawa_labels.csv  (2185 x 34, score_0..score_33)
- project/shared/data/cowen34_order.txt          (감정 이름 정본 순서)
- docs/review_2026-09/emotion_dimension_reliability.csv  (감정 34차원별 신뢰도)
- docs/review_2026-09/emotion_rdm_reliability.json       (RDM 전체 신뢰도)
- 뇌/자극 특징은 기존 ridge 파이프라인이 쓰던 경로를 그대로 사용
  (참고 구현: project/legacy/ridge_diagnostics/loso_representation_comparison.py)

[해야 할 것]
1. 거리 지표는 cosine을 정본으로 쓴다 (신뢰도 0.673, Euclidean 0.612보다 높다).
   Euclidean은 보조로 병기.
2. 감정 측 상관을 sqrt(0.673)=0.821 로 나눠 감쇠 보정한다.
   신뢰구간은 평정자 단위 bootstrap으로 전파한다. 평정자 수는 영상마다 다르므로
   (중위 13, 범위 7-32) endorsement 비율의 분모에서 역산해 쓴다.
3. 보완 조건으로, 영상 특징에 잡음을 더해 신뢰도를 0.673에 맞춘 "reliability-matched"
   조건도 함께 보고한다. 두 방식의 결론이 다르면 그 사실을 보고하라.
4. "유의하지 않았다"가 아니라 등가 검정으로 진술한다. TOST 또는 Bayes factor.
   등가 마진은 코드를 돌리기 전에 정해서 파일에 기록하고, 그 후 바꾸지 마라.
5. 34차원별로도 보고한다. emotion_dimension_reliability.csv 에서 rho<0.5 인 5개
   (guilt 0.187, envy 0.291, contempt 0.305, satisfaction 0.423, disappointment 0.473)는
   사전 제외하거나 신뢰도 가중을 건다. 어느 쪽을 택했는지 명시하라.

[출력]
- project/shared/results/h1_equivalence.json : 보정 전/후 상관, CI, TOST/BF 결과,
  34차원별 표, 사용한 등가 마진
- 짧은 마크다운 요약: 보정 후에도 결론이 유지되는지 한 문장으로

[하지 말 것]
- 감정 측만 보정하고 끝내지 마라. 보정 전 값도 같이 보여야 리뷰어가 검증할 수 있다.
- 등가 마진을 결과가 잘 나오는 쪽으로 고르지 마라.
```

---

## P2. H2 측정오차 보정 변량분해 (쌍 선택 폐기)

```
EmoBrain H2를 쌍 선택 없이 전체 쌍 변량분해로 다시 구현해줘.

[배경]
현재 H2는 |rank(내용거리) - rank(감정거리)| 상위 N% 쌍을 골라 뇌 반응을 본다.
이 설계는 식별 불가다. 감정 RDM 신뢰도가 0.673이라, 평정자를 절반으로 나눠
같은 규칙을 각각 돌리면 선택된 쌍 집합의 Jaccard 겹침이 0.077-0.258뿐이다.
게다가 방향성 편향이 있어서, 논문 자신이 전제한 영역(내용-감정 결합 r=0.7)에서는
"감정이 비슷한 쌍"으로 뽑은 집합의 감정 거리가 독립 측정에서 -1.52 SD -> +0.47 SD 로
부호가 뒤집힌다. 즉 뇌가 감정을 완벽히 따라도 H2가 자동으로 "확인"된다.
근거 데이터: docs/review_2026-09/h2_pair_selection_stability.csv,
             docs/review_2026-09/h2_directional_bias.csv

[해야 할 것]
쌍 선택 단계를 완전히 제거하고, 전체 2,386,020개 쌍(2185 자극)에 대해
측정오차를 보정한 변량분해를 수행한다.

1. 세 개의 RDM을 만든다: 뇌 RDM, 내용(시각-의미) RDM, 감정 RDM. 거리는 cosine.
2. 감정 RDM에는 측정오차가 있다. errors-in-variables 회귀 또는
   disattenuated commonality analysis 로 보정한다.
   - 감정 RDM의 신뢰도는 평정자 hypergeometric 분할 + Spearman-Brown 으로 추정한다
     (재현 방법은 docs/review_2026-09/README.md 참조, 값은 0.673)
   - 보정 전/후를 모두 보고한다
3. 변량분해 결과를 네 성분으로 낸다: 내용 고유 / 감정 고유 / 공유 / 잔차
4. 통계는 subject-clustered bootstrap. 자극 단위 resampling 금지.

[출력]
- project/shared/results/h2_variance_partition.json : 네 성분 + CI, 보정 전/후
- 쌍 선택 설계와의 대조를 짧게: 선택 설계에서는 왜 해석이 불가능했는지 1문단

[참고 - 대안]
지도교수가 쌍 선택 유지를 결정하면, 그때는 평정자 풀을 A/B로 쪼개서
A로 쌍을 고르고 B의 감정 거리로 뇌 검정을 하며, cross-half Jaccard를
필수 진단 지표로 함께 보고해야 한다. 기본은 위의 변량분해 방식이다.
```

---

## P3. H3 신뢰도 정규화 + 기능 구배 연속 검정

```
EmoBrain H3의 모든 뇌 지도를 ROI별 noise ceiling으로 정규화하고,
경계를 기능 구배 상의 연속 위치로 검정하도록 다시 구현해줘.

[배경]
per-ROI ISC가 최고 0.514 / 중위 0.127로 4.05배 차이가 난다
(project/shared/results/noise_ceiling/brain_isc.json).
관측 설명량은 대략 ROI 신뢰도에 비례하므로, 피질 전체에 균일한 효과가 있어도
시각피질에서 4배 강하게 보인다. H3의 주장 형태("시각피질을 넘어 이어지되 거기서는
부분적으로만 설명된다")는 신뢰도 구배 하나만으로 그대로 재현되는 모양이다.
반대 결과도 마찬가지다. 즉 지금 H3는 어느 쪽이 나와도 신뢰도 해석과 구별되지 않는다.

[해야 할 것]
1. 모든 H3 설명량 지도를 per-ROI noise ceiling으로 나눈다.
   정규화 전/후 지도를 모두 저장한다.
2. per-ROI ISC 지도를 같은 figure의 동반 패널로 반드시 만든다.
3. 경계를 이항 라벨(visual / transmodal)로 검정하지 말고,
   주요 기능 구배(principal functional gradient) 상의 연속 위치에 대한
   회귀로 검정한다. 구배는 기존 파싱(Schaefer-400 + Tian-S3 50)에서 계산하거나
   published gradient를 쓴다 - 어느 쪽인지 명시하라.
4. ROI별 검정력을 계산해 표로 낸다. ISC가 낮은 영역의 null은
   "설명 안 됨"이 아니라 "이 신뢰도에서는 판정 불가"로 분류한다.
   이 두 범주를 지도에서 다른 색으로 구분하라.
5. (여유 있으면) 신뢰도-매칭 ROI 부분표집을 보조 분석으로 추가.

[출력]
- project/shared/results/h3_ceiling_normalized.json
- figure: 정규화된 설명량 지도 + ISC 동반 패널 + 판정불가 영역 마스크
- ROI별 검정력 표 (CSV)

[하지 말 것]
- 정규화하지 않은 지도만 논문에 싣지 마라.
- ISC가 낮은 영역의 null을 "이 영역은 설명되지 않는다"로 서술하지 마라.
```

---

## P4. §5 감정어 제거 후 재임베딩

```
caption에서 감정 어휘를 제거하고 재임베딩한 뒤 H1을 다시 돌려줘.
paper_logic_merged.md §5 통제 사다리에 한 칸을 추가하는 작업이다.

[배경]
human-written caption 43,920개(2,196 영상 x 20명) 중 9.3%가 감정 어휘를 포함하고,
영상 기준으로는 46.4%가 감정 어휘 caption을 최소 하나 갖는다.
최빈 누출 토큰: kissing/kiss(1370), happy/happily(255), beautiful(244),
scared(197), surprised(161), scary(96), startled(93), crying(84).
즉 caption 임베딩이 감정 정보를 직접 담고 있을 수 있고, 이건 리뷰어가
이름을 대서 요구할 통제다.

[입력]
- project/shared/data/caption_ck20.csv  (video_id, description)
- docs/review_2026-09/caption_emotion_lexicon.json  (34개 감정 x 185개 어간,
  cowen34_order.txt 순서 키)

[해야 할 것]
1. lexicon의 어간에 걸리는 토큰을 caption에서 제거한다.
   - 어간 매칭은 word-boundary + 접미사 허용 (\b(stem)\w*)
   - 제거 후 문장이 비거나 3단어 미만이면 그 caption을 통계에서 뺀다.
     몇 개가 빠졌는지 보고하라
2. 기존과 동일한 인코더로 재임베딩한다
   (sentence-transformers/all-mpnet-base-v2, mean pooling + L2 정규화 -
   project/shared/data/emotion_query/emotion_query_mpnet.json 과 동일 설정)
3. 원본 caption 임베딩과 감정어 제거 임베딩으로 H1을 각각 돌려 대조한다.
4. 부수로, 감정어를 제거하기 전/후 임베딩의 코사인 유사도 분포를 보고하라.
   변화가 거의 없다면 제거가 실질적으로 작동하지 않은 것이다.

[출력]
- project/shared/data/stimulus_features/caption_embed_noemo.npy
- project/shared/results/h1_caption_ablation.json : 원본 vs 제거 조건 H1 결과
- 제거된 토큰 수, 탈락 caption 수

[판정]
감정어를 빼도 H1 결과가 유지되면 강한 방어다.
무너지면 그것도 반드시 보고할 결과다. 숨기지 마라.
```

---

## P5. 피질 vs 피질+피질하 ablation

```
ROI ridge를 피질만 / 피질+피질하 두 조건으로 돌려 대조해줘.

[배경]
현재 파싱은 Schaefer-400 17-network(피질) + Tian S3 50(피질하) = 450 ROI인데,
피질하가 얼마나 기여하는지 보고한 적이 없다. 감정 연구에서 편도체·선조체·시상의
기여는 리뷰어가 반드시 묻는 항목이고, 지금 이 ablation이 없다.

[해야 할 것]
1. 조건 A: Schaefer-400만 (400 ROI)
   조건 B: Schaefer-400 + Tian-S3 50 (450 ROI, 현재 기본값)
2. 나머지는 전부 동일하게: 같은 split, 같은 alpha 선택 절차, 같은 지표
   (per-clip 34D profile Pearson). 참고 구현은
   project/legacy/ridge_diagnostics/loso_representation_comparison.py
3. pooled / within-subject / LOSO 세 regime 모두에서 보고
4. 차이의 subject-clustered bootstrap CI
5. 여유가 되면 조건 C: Tian-S3 50만 (피질하 단독)도 추가하면 해석이 쉬워진다

[출력]
- project/shared/results/cortex_subcortex_ablation.json
- 결과를 noise ceiling(0.678) 대비 %로 병기

[해석 주의]
ROI 수가 다르므로(400 vs 450) 자유도 차이가 있다. ridge alpha가 이를 흡수하지만,
차이가 작을 때는 ROI 수를 맞춘 대조(피질에서 50개 무작위 제거)도 함께 보고하라.
```

---

## P6. cheap fusion 두 대비 분리 + CI 확인

```
project/scripts/cheap_fusion_and_floor.py 의 결과를 두 대비로 분리해 보고하도록
정리하고, bootstrap CI가 subject-clustered인지 확인해줘.

[배경]
이 스크립트는 서로 다른 두 값을 계산하는데 지금 구분 없이 인용될 위험이 있다.
  fusion_vs_stimulus_only  = mlp_fusion - ridge_stimulus        = +0.040 (ceiling의 5.9%)
  brain_marginal_in_fusion = mlp_fusion - mlp_fusion_brainshuffle = +0.028 (ceiling의 4.1%)
두 번째가 맞는 추정치다. 첫 번째는 "뇌 있음/없음"과 "MLP/ridge"를 섞지만,
두 번째는 같은 MLP·같은 입력 차원에서 뇌 행만 permute하므로 모델 용량이 통제된다.

[해야 할 것]
1. 스크립트의 bootstrap_ci 구현을 읽고, resampling 단위가 무엇인지 확인하라.
   자극 단위라면 피험자 5명을 고려해 subject-clustered로 바꿔라.
   바꾼 전후 CI 폭을 모두 보고하라.
2. 결과 JSON을 두 대비가 명확히 구분되는 스키마로 저장한다.
   각 대비에 정의 문자열을 함께 넣어 나중에 혼동되지 않게 하라.
3. 논문 본문용 표를 만든다:
   floor / ridge_brain_shuffle / ridge_brain / ridge_stimulus /
   mlp_fusion_brainshuffle / mlp_fusion, 각각 r 과 ceiling 대비 %

[주의]
mlp_fusion_brainshuffle 의 절대값이 결과에 명시적으로 없다면 계산해서 넣어라
(mlp_fusion - 0.028 = 약 0.505로 역산되지만, 역산값이 아니라 실제 값을 써라).
```

---

## P7. 정렬 assert 배선

```
docs/review_2026-09/verify_label_order.py 의 check_order() 를
감정 차원별 결과를 다루는 모든 스크립트 진입점에 배선해줘.

[배경]
project/shared/data/cowen_horikawa_labels.csv 에는 감정 이름이 없고
score_0..score_33 만 있다. 이름은 project/shared/data/cowen34_order.txt 와
project/shared/data/emotion_query/emotion_query_mpnet.json 에만 있다.
세 파일의 순서가 어긋나면 34개 감정별 결과 전체가 조용히 뒤섞이고,
에러 없이 그럴듯한 숫자가 나온다.

매핑 score_j = cowen34_order.txt[j] 는 2026-09 검토에서 caption 프로브 8개로
경험적으로 확인됐다 (6/8이 정답 인덱스 1위, fear와 surprise는 3위/34이고
둘 다 1위가 amusement - 이 코퍼스의 놀람 영상이 실제로 장난·점프스케어라
amusement 평정이 높기 때문).

[해야 할 것]
1. project/ 아래에서 score_ 컬럼이나 34차원 감정 배열을 다루는 스크립트를 모두 찾는다
2. 각 진입점에서 check_order() 를 호출하도록 추가한다
3. 감정별 결과를 저장할 때는 인덱스가 아니라 이름을 키로 쓰도록 바꾼다
4. 가능하면 cowen_horikawa_labels.csv 에 감정 이름 헤더를 추가한 파생 파일을 만든다
   (원본은 건드리지 말고 새 파일로)

[출력]
- 변경한 파일 목록과 각 변경 위치
- check_order() 가 실패하는 곳이 있으면 그것이 가장 중요한 발견이다. 즉시 보고하라
```

---

## B1. μP multiplier 검증 (BFM 최우선)

```
SwiFT 체크포인트의 muP(muTransfer) parameterization이 임베딩 추출 시
올바르게 적용되고 있는지 검증해줘.

[배경 - 왜 의심하는가]
project/shared/code/bfm_embeddings/_lib/SETTINGS_swift_master.md 에
SwiFT 5개 모델 공통으로 use_MuTransfer=True 가 적혀 있다.
muP 가중치는 추론 시 올바른 output/attention multiplier를 적용해야 하고,
표준 parameterization forward에 그냥 로드하면 활성값이 조용히 틀어진다.

결정적 증거: project/shared/results/loso_representation_comparison.json 에서
UAH 계열 3개가 랜덤 초기화(scratch)보다 나쁘다.
  swift_UAH_5M_SL20_resting  0.0732 vs scratch 0.1220  (-0.0489)
  swift_UAH_51M_SL20_resting 0.0866 vs scratch 0.1330  (-0.0464)
  swift_UAH_202M_SL20_resting 0.1286 vs scratch 0.1558 (-0.0272)
랜덤 가중치는 가장 "안 맞춰진" 상태다. 그보다 나쁘다는 것은 overfitting으로
설명되지 않고, 입력 분포가 체크포인트가 기대하는 것과 다르다는 지문이다.

[해야 할 것]
1. 임베딩 추출 코드가 체크포인트를 로드하는 경로를 읽고,
   muP multiplier(output multiplier, attention scale, embedding scale 등)를
   적용하는지 확인한다. 적용하지 않는다면 그것이 원인일 가능성이 높다.
2. SwiFT 5개 체크포인트 각각에 대해 muP 적용 / 미적용 두 조건으로
   임베딩을 재추출하고, 같은 ridge 프로토콜로 비교한다.
3. 진단 지표를 함께 낸다: 임베딩의 rank, 차원별 분산, 자극 간 분산 대 전체 분산 비.
   muP가 잘못 적용되면 활성이 포화되거나 붕괴하므로 여기서 먼저 드러난다.

[부수 확인 - 반드시 할 것]
결과 파일의 모델 이름과 SETTINGS의 모델 목록이 일치하지 않는다.
  결과:     UAH_5M, UAH_51M, UAH_202M, NewE36, NewE96, NewE192
  SETTINGS: UAH_P2_51M, UAH_P3_806M, NewUAH_newE36(~9M),
            NewUAH_newE96(~66M), NewUAH_newE192(~264M)
UAH_5M 과 UAH_202M 은 SETTINGS에 없고, 806M 은 결과에 없다.
어느 체크포인트가 어느 숫자를 냈는지 먼저 확정하라. 이걸 못 맞추면
아래 모든 분석이 무의미하다.

[판정]
- muP 적용 후 UAH의 resting<scratch 가 사라지면: SwiFT 숫자 전체를 폐기하고
  재추출한다. 양수 델타를 낸 NewE 계열도 포함이다.
- 사라지지 않으면: 다른 원인(입력 정규화, TR/voxel size 불일치, 전처리 차이)을 찾는다.

[출력]
- project/shared/results/swift_mup_verification.json
- 판정과 근거를 3문장 이내로
```

---

## B2. 패딩 제거 — 연속 run 인코딩

```
BFM 임베딩 추출을 자극별 20프레임 패딩 방식에서
연속 run 슬라이딩 인코딩 방식으로 바꿔줘.

[배경 - 문제의 크기]
Horikawa 자극 길이 분포 (SETTINGS_brain_jepa.md 에 기재):
  T=5 프레임: 1,573개 (72.0%),  T<=20: 2,178개 (99.1%),  T>20: 19개 (0.9%)
그런데 모델 입력은 20프레임 고정이다. 게다가 4D volumetric 모델
(SwiFT, NeuroSTORM)은 공간 패딩까지 붙는다: (74,91,81) -> (96,96,96),
즉 부피의 38.3%가 배경이다.

결과적으로 T=5 자극에서
  4D volumetric 모델: 입력 텐서의 84.6%가 패딩 (실제 데이터 15.4%)
  ROI time series 모델: 75%가 패딩 (공간축은 전부 실제)
이 입력은 UKB/ABCD 연속 resting 20-TR 윈도우로 사전학습된 모델에게 완전한 OOD다.

방증: padding 방식만 바꿔도 SwiFT NewE96 성능이 0.134(zero) -> 0.171(spatial_only)로
0.037 움직인다. 이 폭은 사전학습 효과 중위(+0.043)와 맞먹는다.

[먼저 확인할 것 - 막힐 수 있는 지점]
현재 전처리 산출물은 이미 자극 단위로 잘려 있다:
  Brain-JEPA:  horikawa_preprocess_JEPA_ROI/time_series/sub-XX/stimulus_YYY/
  NeuroSTORM:  horikawa_filtered_MNI_to_TRs/img/sub-XX_stimulus_YYY/frame_*.pt
즉 연속 run 시계열이 이 단계에는 남아 있지 않을 수 있다.
착수 전에 (a) 자극 분할 이전의 run 단위 산출물이 남아 있는지,
(b) 없다면 어느 전처리 단계부터 다시 돌려야 하는지를 먼저 확인하고 보고하라.
이 확인 없이 코드부터 쓰지 마라. 없으면 이 작업의 비용이 크게 달라진다.

[해야 할 것]
1. 자극별로 20프레임을 조립하지 말고, 각 피험자의 연속 run 전체를
   모델 native 윈도우(20 TR)로 슬라이딩 인코딩한다.
2. 각 자극 구간에 해당하는 프레임/토큰 임베딩만 골라 pool한다.
   pool 방식(mean / attention-weighted / 마지막 프레임)을 조건으로 비교하라.
3. 자극 경계에서 윈도우가 걸치는 문제를 어떻게 처리했는지 명시하라
   (예: 자극 구간이 윈도우의 절반 이상일 때만 사용).
4. 기존 패딩 방식 결과와 head-to-head 비교한다. 같은 ridge 프로토콜, 같은 split.

[대상]
Brain-JEPA, NeuroSTORM, SwiFT NewE96 최소 3개. B1이 끝난 뒤에 하라
(muP 문제가 남아 있으면 SwiFT 결과를 해석할 수 없다).

[출력]
- 새 임베딩 (기존 경로를 덮어쓰지 말고 _continuous 접미사로 분리)
- project/shared/results/continuous_vs_padded.json : 인코더 x pool방식 x 조건
- 각 조건의 실제 데이터 비율(패딩 비율)을 메타데이터로 함께 저장

[관전 포인트]
현재 spatial_only(시간 정보 완전 제거)가 세 인코더 모두에서 같거나 더 낫다
(brain_jepa_LEGACY -0.0010, neurostorm -0.0004, swift_NewE96 -0.0036).
즉 지금은 시간축이 기여를 못 하고 있다. 패딩을 없앤 뒤에도 그런지가 핵심이다.
그대로라면 시간축 무기여는 데이터의 성질이고, 바뀌면 패딩이 원인이었던 것이다.
```

---

## B3. 차원 정합 비교

```
BFM 인코더 비교를 공통 차원으로 정합해서 다시 돌려줘.

[배경]
현재 비교는 입력 표상 / 사전학습 목표 / 출력 차원 세 가지가 동시에 변한다.
  NeuroSTORM 288, Brain-JEPA 768, NewE96 768, NewE192 1536, UAH_P3 3072
따라서 "SwiFT이 나쁘다"를 아키텍처 탓으로 돌릴 수 없다.

[해야 할 것]
1. 모든 인코더 임베딩을 공통 d(예: 256)로 PCA 축소한 뒤 동일 ridge로 비교한다.
   PCA는 train split에서만 적합하고 val/test에 적용한다 (누출 금지).
2. d를 여러 개(64, 128, 256, 512) 돌려 곡선으로 보고한다.
   차원이 아니라 표상이 원인인지 확인하려면 곡선의 모양이 필요하다.
3. ROI-mean 450 baseline도 같은 절차로 PCA해서 같은 곡선에 올린다.

[출력]
- project/shared/results/dimension_matched_comparison.json
- 인코더 x d 곡선 figure
```

---

## B0. (선택) 임베딩 성질 진단 — B1 전에 하루면 됨

```
frozen BFM 임베딩이 무엇을 담고 있는지 진단해줘.
GPU 학습 없이 이미 저장된 임베딩만 쓴다.

[왜]
BFM이 ROI-mean ridge에 못 미치는 이유가 (a) 도메인 불일치(resting으로 학습해서)인지
(b) 사전학습 목표가 자극 고정 성분을 버려서인지 가려야 한다.
(a)라면 자연주의 데이터로 domain-adaptive SSL이 고친다. (b)라면 데이터를 바꿔도
같은 목표로는 안 고쳐지고 목표 함수를 바꿔야 한다. 이 판정이 다음 GPU 예산을 정한다.

[해야 할 것]
1. 각 인코더 임베딩의 분산을 분해한다:
   자극 간 분산 / 피험자 간 분산 / 잔차. 자극 간 분산 비율이 핵심 지표다.
2. resting 임베딩과 scratch 임베딩의 표상 유사도를 CKA로 잰다.
   사전학습이 무엇을 추가했는지 본다.
3. 각 BFM 임베딩에서 ROI-mean 450을 선형 재구성해보고 R^2를 낸다.
   BFM이 ROI-mean의 어떤 성분을 버렸는지 본다.

[대상] Brain-JEPA, NeuroSTORM, SwiFT NewE96 (resting/scratch 각각)

[참고 - 사전 예측]
자매 프로젝트 BEACON-T에서 frozen BFM 임베딩 분산의 95.4-99.95%가 시간 불변으로
측정된 바 있다 (frame-to-frame: Brain-JEPA 0.003%, SwiFT 0.05-0.15%,
NeuroMamba 3.6-4.6%). 다만 그건 연속 영화의 frame-to-frame 대비이고
여기는 이산 자극 간 대비이므로 직접 비교가 아니다. EmoBrain 임베딩에서
독립적으로 확인하라. 그 수치를 가정하고 시작하지 마라.

[출력]
- project/shared/results/embedding_diagnostics.json
- 판정: (a) 도메인 불일치 우세 / (b) 목표 함수 문제 우세 / (c) 판정 불가
  중 하나와 근거
```

---

## 지도교수 판단이 필요한 항목

프롬프트로 처리할 수 없고 사람이 결정해야 하는 것들이다.

1. **H2를 변량분해로 흡수할 것인가** — 가설이 넷에서 셋으로 준다
2. **H4를 3월 논문에 넣을 것인가** — cross-dataset이 Emo-FilM에 막혀 완결 불가
3. **시나리오 A(3월, 중상위 저널) vs B(2027년, Nature 계열)** — advisory_review.md §10
4. **BFM 음성 결과를 별도 단편으로 먼저 낼 것인가** — 지금이 가장 값이 높다
5. **스캔 피험자 본인 평정을 수집할 것인가** — 비용 대비 가치가 크고 2단계 질문과 직결
