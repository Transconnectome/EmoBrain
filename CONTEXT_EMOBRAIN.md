# EmoBrain Current Context (2026-08-19)

**논증: `docs/paper_logic_merged.md`.** 아래는 요약과 수치 정본.

## 지금 확정된 것

- EmoViS 와 **한 편의 논문**. EmoViS = 뇌 분석(H1–H3), EmoBrain = 모델과 H4.
- **Main theme**: 고차원 감정 공간의 구조는 시각-의미 처리의 구조다.
- **분석 단위는 감정 범주가 아니라 34차원 프로파일**이고, 자극 간 관계는 프로파일 간 거리다.
- 모델 = brain + video + caption 을 한 공간에 통합해 34차원 프로파일을 회귀. LLM 없음.
- **모델의 정당화는 H4 하나.** H1–H3 는 모델 없이 검정된다.

## 수치 정본 (문서마다 달라 혼동됐던 것)

**자극 수.** 제시 **2196** = 고유 **2185** + 신뢰도 확인용 **11** 회 반복 제시.
분석은 2185 기준. (선행연구 중 "2196 = 2181 + 15" 로 쪼갠 곳이 있는데 우리 분해와 다르므로 인용 시
구분해 적는다.) 분할 = train 1748 / val 217 / test 220 자극 → 5명 pooling 시 8740 / 1085 / 1100.

**R0 (ROI-mean 감정 디코딩 천장).** 네 숫자가 돌아다니는데 서로 다른 양이다.
| 값 | 무엇 |
|---|---|
| **0.294** | linear ridge, ROI-mean 450, per-clip 34D Pearson. **기본 baseline** |
| 0.2961 | 위와 같은 조건의 재측정 (build_log cycle 22). 0.294 와 같은 양 |
| 0.313 | kernel ridge. 비선형 여유분 |
| 0.280 | Cat34_soft mean Pearson (BFM 계열, **다른 지표**). R0 과 같은 양이 아님 |
→ 인용 시 **ridge 0.294 / kernel 0.313** 을 쓰고, 0.280 은 섞지 않는다.

**라벨 희소성.** 34D crowd 비율에서 **73.8% 가 0**, 자극당 평균 활성 범주 1.7개. `log1p_z` 범위 약 [-1, +4].

**시간평균이 신호를 버리지 않았다는 근거.** roi_mean(450) 0.2961 vs mean+std+max+min(1800-dim) 0.2854
— 요약통계를 늘려도 나아지지 않았다.

## 폐기된 것

Qwen3-VL backbone (teacher 0.553 ≈ cheap fusion 0.533, student 0.154 < ridge 0.294) ·
open-vocabulary / cross-taxonomy 전이를 headline novelty 로 삼는 프레임 ·
학습에 없던 감정으로의 zero-shot (원칙적 근거 없음, RQ 와 무관) ·
감정별 sensory:semantic 조성 가설 (EmoViS 에서 0/34 Bonferroni, split reliability −0.95~−1.00) ·
시각 모델 layer→영역 위계 추론.

## 열린 사항

- 감정 RDM 거리 지표 정본 (Euclidean vs cosine — 결과를 크게 바꿈). 데이터를 보고 정하면 사후선택이
  되므로 **원리로** 정해야 한다.
- EmoViS 쪽 미실행 분석 — 클린 3-band banded ridge encoding, `sem_3_semantic_unique`,
  양방향 conflict test(전 임계값 5/10/20% 보고), 숫자 정합(CLIP 0.106 vs 0.137).
- bag-of-words 통제 사다리 — 단어평균 / 범주어만 / 명사만 / 뒤섞은 문장.
