# 자문 검토 2026-09 — 산출물과 작업 리스트

`docs/paper_logic_merged.md` (H1–H4 프레임, 2026-08-19 확정)과 저장소 실제 상태를 대조한
외부 자문 검토. 전체 논증은 [`advisory_review.md`](advisory_review.md).

이 디렉터리의 모든 수치는 **이 저장소에 커밋된 데이터로 재계산 가능**하다. 재현 코드가
필요한 항목은 각 절에 방법을 적어 두었다.

---

## 1. 이번 검토가 끝낸 것 — 그대로 쓰면 되는 결과

| 산출물 | 내용 | 해당 action item |
|---|---|---|
| [`emotion_rdm_reliability.json`](emotion_rdm_reliability.json) | 감정 RDM 신뢰도 **cosine 0.673 / Euclidean 0.612**. 평정자 hypergeometric 분할 ×3 + Spearman-Brown | **§8 첫 미결정 항목 종결 — cosine을 정본으로** |
| [`emotion_dimension_reliability.csv`](emotion_dimension_reliability.csv) | **감정 34차원별 신뢰도.** split-half(SB) + 이항 분산성분 두 방식 | #4 후반 |
| [`h2_pair_selection_stability.csv`](h2_pair_selection_stability.csv) | H2 쌍 선택의 평정자 절반 간 Jaccard = 0.077–0.258 | #3 |
| [`h2_directional_bias.csv`](h2_directional_bias.csv) | H2 방향성 선택 편향 0.72–1.99 SD (r=0.7에서 부호 역전) | #3 |
| [`caption_leakage.json`](caption_leakage.json) | caption 감정 어휘 누출 **9.3% / 영상 46.4%** | #5 근거 |
| [`caption_emotion_lexicon.json`](caption_emotion_lexicon.json) | 34개 감정 × 185개 어간, 정본 순서 키. **§5 통제 사다리의 "감정어 제거 후 재임베딩" 항목에 그대로 투입** | #5 실행 |
| [`verify_label_order.py`](verify_label_order.py) | `score_j ↔ cowen34_order.txt[j]` 정렬 assert. **경험적으로 검증됨** (아래) | #12 |
| [`bfm_pretraining_effect.csv`](bfm_pretraining_effect.csv) | resting−scratch 17개 짝 대비 | BFM 진단 |
| [`emobrain_review_metrics.csv`](emobrain_review_metrics.csv) | 지적 근거 16개 값, 측정/저장소 출처 구분 | 전체 |
| [`figures/`](figures) | 진단 4패널 + BFM 사전학습 효과 | 전체 |

### 1-1. 감정 이름 매핑 — 경험적으로 확인했다

`cowen_horikawa_labels.csv`에는 감정 이름이 없고 `score_0`…`score_33`만 있다.
순서를 **가정하지 않고** caption 증거로 검정했다: 모호하지 않은 감정어 프로브 8개
(romance/sadness/fear/amusement/disgust/surprise/joy/craving)를 `caption_ck20.csv`
43,700행에서 잡아 34개 score 컬럼 각각의 상승폭을 쟀다.

- **6/8**은 정답 인덱스가 1위
- fear, surprise는 3위 — 두 경우 모두 1위가 `amusement`. 이 코퍼스의 놀람 영상이
  실제로 장난·점프스케어라 amusement 평정이 높다. 둘 다 top-3 안에 정답이 있다

→ `score_j = cowen34_order.txt[j]` (알파벳순) 확정. `verify_label_order.py`가 이를 고정한다.

### 1-2. 감정별 신뢰도 — H1 결론을 끌고 갈 수 있는 차원이 있다

중위 ρ = **0.695**, 범위 **0.187–0.953**.

**ρ < 0.5인 5개 차원: guilt (0.187), envy (0.291), contempt (0.305), satisfaction (0.423),
disappointment (0.473).** 전부 endorsement가 희소한 차원이다 (평균 0.005–0.041, 영값 64–95%).
guilt의 감쇠 계수는 √0.187 = 0.43 — 참값이 관측치의 2.3배여야 한다. **이 차원들의 개별 결과는
사실상 측정 불가이므로, 사전 등록 단계에서 제외하거나 신뢰도 가중 분석을 쓸 것.**

가장 높은 6개: sexual desire 0.953, craving 0.941, romance 0.939, disgust 0.914,
nostalgia 0.872, amusement 0.850 — 시각적으로 명시적인 범주들이다. 이 구배 자체가
H1의 "내용이 감정 구조를 설명한다"에 대한 방증이므로 본문에 넣을 가치가 있다.

---

## 2. 다음 작업 — 디스크의 데이터만 있으면 되는 것 (외부 의존 없음)

우선순위 순. 전부 NERSC의 기존 산출물로 실행 가능하다.

1. **H1 감쇠 보정 등가 검정.** 감정 측 상관을 √ρ로 보정(cosine ρ=0.673), CI는 평정자 단위
   bootstrap으로 전파. TOST 또는 Bayes factor, 등가 마진은 사전 등록. 34차원별 결과는
   `emotion_dimension_reliability.csv`로 가중하거나 ρ<0.5 5개를 제외
2. **H2 재설계.** 쌍 선택을 버리고 전체 2,386,020 쌍에 errors-in-variables 변량분해.
   선택을 유지한다면 평정자 절반 A로 고르고 절반 B로 검정 + cross-half Jaccard 필수 보고
3. **§5 통제 사다리에 감정어 제거 조건 추가.** `caption_emotion_lexicon.json` 투입,
   재임베딩 후 H1 재실행
4. **H3 지도 전부 per-ROI noise ceiling 정규화** + ISC 지도 동반 패널. 경계를 이항 라벨이
   아니라 주요 기능 구배 상 연속 위치로 검정. ROI별 검정력 명시 (ISC 중위 0.127에서
   탐지 가능한 효과크기는 크다 — 그 영역의 null은 "설명 안 됨"이 아니라 "판정 불가")
5. **cheap fusion 두 대비 분리 보고.** `fusion_vs_stimulus_only` +0.040(모델 급 혼입) vs
   **`brain_marginal_in_fusion` +0.028 = ceiling의 4.1%(용량 통제, 이것을 인용)**.
   bootstrap CI가 subject-clustered인지 확인 — 5명 pooling에서 stimulus-level이면 anti-conservative
6. **피질만 vs 피질+피질하 ablation.** Schaefer-400 vs +Tian-S3 50으로 ridge 대조.
   "whole brain이 감정에 도움" 직관의 직접 검정이고 현재 이 ablation이 없다. 반나절
7. **`verify_label_order.py`를 파이프라인 진입점에 배선**

## 3. BFM 진단 — 순서를 지킬 것

`advisory_review.md` §5와 `bfm_pretraining_effect.csv` 참조. 사전학습 효과(중위 +0.043,
최대 +0.099)는 지금까지 뇌 측에서 얻은 **가장 큰 효과**다 (아키텍처 +0.008, 해상도 +0.006).
그러나 최고 BFM 0.245는 ROI-mean ridge 0.296에 **0.051 미달**이다.

1. **μP multiplier 검증 — 최우선, 반나절.** `SETTINGS_swift_master.md`에 SwiFT 5개 모델
   공통 `use_MuTransfer=True`. μP 가중치를 표준 parameterization forward에 로드하면 활성값이
   조용히 틀어진다. UAH 3개가 **랜덤 초기화보다 나쁘다**(−0.027 ~ −0.049)는 것은 overfitting으로
   설명되지 않고 config mismatch의 지문이다. 여기서 원인이 잡히면 SwiFT 숫자 전체를 재추출해야 한다
   - 부수: 결과 파일 이름(UAH_5M/51M/202M)과 SETTINGS(UAH_P2_51M/UAH_P3_806M/NewE36 9M/
     NewE96 66M/NewE192 264M)이 **불일치**. 어느 체크포인트가 어느 숫자를 냈는지 확정 불가
2. **패딩 제거 — 학습 불필요, 가장 큰 이득.** T=5 자극이 72.0%인데 입력은 20프레임 고정,
   volumetric은 공간 패딩까지 붙어 **입력의 84.6%가 패딩**(ROI 모델은 75%). 자극별로 20프레임을
   만들지 말고 **연속 run을 native 윈도우로 인코딩한 뒤 자극 구간 프레임을 pool**할 것.
   사전학습 분포(연속 신호)와 일치하게 된다
3. **차원 정합.** 현재 288/768/1536/3072가 섞여 비교되고 있다. 공통 d로 PCA 후 ridge
4. **그다음 NeuroMamba 추가.** 같은 개발자 모델이므로 사전학습 코퍼스·전처리가 SwiFT과
   공유되어 **아키텍처/목표만 바꾸는 대조**가 된다. SwiFT의 부진이 파이프라인 탓인지
   Swin+SimMIM 탓인지 가른다. 시간축 귀납편향(SSM vs Swin attention)도 직접 검정된다

**시간축에 대한 관측:** `spatial_only`(실제 TR 평균 1개를 20회 복제 = 시간 정보 완전 제거)가
세 인코더 모두에서 같거나 더 낫다 — brain_jepa_LEGACY −0.0010, neurostorm −0.0004,
swift_NewE96 −0.0036. SwiFT은 zero 0.134 → replicate 0.144 → cyclic 0.159 → mean 0.167 →
spatial_only 0.171로 **시간축을 죽일수록 단조 개선**된다. 자극당 시간 동역학이 34D 감정 프로파일
판독에 기여하지 않고 있다.

## 4. 문서·전략 작업

1. **`project/README.md`(teacher/student = LEGACY)와 `paper_logic_merged.md` §4-A(teacher→cache→student = 고정)
   모순 해소.** LLM teacher 폐기와 teacher/student 폐기는 다른 결정인데 구분이 기록돼 있지 않다
2. **`build_log.md`의 중복 "Cycle 26" 정리** (2026-08-17, 2026-07-21 (3)). 사이클 번호가
   결과 provenance 키로 쓰이므로 충돌은 반드시 사고를 낸다
3. 1단계↔2단계 미설명분 소유권, H4↔3-1 cross-dataset 소유권 경계를 양쪽 문서에 문장으로 명시
4. **"Soderberg, Ma, Riels, Kragel (2026, Trends Open)" DOI 확인 — 이번 검토에서 확인 실패.**
   3-2 전체가 이 인용 위에 서 있다
5. 경쟁 문헌 반영해 novelty 진술 재작성 (아래)
6. H1 등가 검정 OSF 사전 등록
7. 스캔 피험자 본인 평정 수집 가능성 조사. 불가 시 독립 crowd 표본으로 taxonomy 안정성 측정

### 확인된 경쟁 문헌 (PubMed / arXiv API로 서지 확인 완료)

- **Ma Y, Kragel PA. "Map-like representations of emotion knowledge in hippocampal-prefrontal
  systems." Nat Commun. 2026 Jan 26;17(1):1518.** doi 10.1038/s41467-025-68240-z ·
  PMID 41588009. **제1저자 Ma가 3-2가 근거로 삼은 리뷰의 그 Ma다** — 해당 저자군이 감정
  표상 기하로 이미 Nature 계열 원저를 냈다
- **arXiv:2606.07707** (2026-06-05, 8인). 연속 다차원 감정 프로파일 회귀. "34D 연속 프로파일,
  softmax 없음" 프레이밍과 겹친다 — **연속 프로파일 회귀는 더 이상 novelty가 아니다**
- **arXiv:2602.04512** (2026-02-04, 4인) BrainVista. 4단계 영역이 점유되기 시작했다

## 5. 인프라 — 단일 최우선 블로커

**Emo-FilM (ds004872)** 미확보 하나가 H4 cross-dataset + 로드맵 2단계 전체 + 3단계 전이
검정을 동시에 막고 있다. 과제를 "데이터셋 데이터베이스 구축"이 아니라
**"Emo-FilM을 Schaefer-400 + Tian-S3 동일 공간으로 전처리·parcellation 완료, 하드 기한 명시"**로
재정의할 것. git-annex 설치 가능성 / 132GB 여유 / 전처리 비용 세 항목에 각각 담당자와 날짜.

---

## 6. 저널 판단 — 두 시나리오

N=5, 스캔 피험자 본인이 아닌 crowd 평정, headline이 경계/한계 결과인 논문은
Nature Neuroscience / NHB 급이 아니다.

- **A (빠르게):** 1단계 = H1+H3만. 감쇠 보정 등가 검정 + 신뢰도 정규화된 경계 지도.
  H2는 변량분해로 흡수, H4 제외. 3월 투고, Imaging Neuroscience / Communications Psychology.
  손에 있는 데이터로 완결 가능하고 Emo-FilM 블로커에 걸리지 않는다
- **B (천장 높여):** 1+2단계 병합, Emo-FilM 추가, cross-dataset 포함. 2027년 9월경,
  Nature Communications / NHB. **1단계 단독은 Nature 계열 스토리가 아니다**

A → B 순서를 권하되 §4-3의 경계 진술을 먼저 문서에 박을 것. 세 번째 선택지로, BFM 음성 결과
("resting-pretrained BFM이 감정 프로파일 판독에서 ridge를 못 이긴다" + 포화 분석)를 A보다 먼저
단편으로 내는 것도 실질적이다 — 지금이 가장 값이 나가고 시간이 갈수록 떨어진다.
