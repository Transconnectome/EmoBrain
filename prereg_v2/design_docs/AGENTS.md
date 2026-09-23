# EmoBrain project instructions

## Rationale-before-inclusion rule

모델, feature, target, loss, control, 분석, 통계 검정, 시각화 또는 해석을 새로 설정하거나 논문에 포함하기 전에 반드시 **왜 필요한가**를 명시한다. 단순히 최신 방법, 높은 성능, 관행, 유명 논문 사용, 또는 fancy함은 포함 근거가 아니다.

각 항목은 다음 여섯 질문에 답해야 한다.

1. 이 항목이 답하는 과학적 질문은 무엇인가?
2. 이 항목이 없으면 어떤 대안 설명을 배제할 수 없는가?
3. 선택의 근거는 어떤 기존 문헌 또는 데이터인가?
4. 가능한 대안 가운데 왜 이것을 선택했는가?
5. 어떤 결과가 나오면 이 항목을 제거하거나 해석을 바꿀 것인가?
6. 이 항목으로 주장할 수 없는 것은 무엇인가?

위 답이 없는 항목은 primary design에 넣지 않는다. 필요하다면 baseline, robustness 또는 supplementary analysis로 격하한다. 서로 다른 모델을 심리적·신경과학적 구성개념으로 해석할 때는 architecture, objective, training data, supervision과 capacity의 차이가 구성개념 차이와 혼동되지 않는지 먼저 검토한다.

모든 설명에서 확인한 근거와 아직 확인하지 못한 전제를 구분한다. 판단을 변경할 때는 새 근거 또는 논증 중 무엇이 변경을 일으켰는지 명시한다.
