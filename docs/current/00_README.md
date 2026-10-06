# EmoBrain 서버 AI 인수인계

_2026-10-06 · 유지·편집하는 단일 연구 기준 · 결과 보고서가 아닌 실행 계획_

---

## 📋 먼저 알아야 할 것

이 연구는 **감정 예측 성능 경쟁이 아니라, 뇌–장면 내용 관계를 모델이 무엇으로 학습하고 실제 예측에 어떻게 사용하는지 검정하는 연구**다. Teacher는 학습 시 brain + video + caption을 받고, student는 학습·추론 시 fMRI만 입력받는다. Teacher의 출력으로 student를 안내하지만, 그 사실만으로 teacher의 joint representation이 student에 전달되었다고 간주하지 않는다.

세 분석은 다음 질문으로 이어진다.

1. 장면의 시각·의미 표상이 새로운 자극의 뇌 반응을 설명하며, 그 설명력은 정서 주석의 설명력과 어떻게 겹치고 구별되는가? (1a·1b)
2. Teacher와 brain-only student가 어떤 brain–content 관계를 학습하고 사용하며, 발견한 내용 관련 표현이 독립 뇌 측정에서도 지지되는가? (2a–d)
3. 그 표현에서 normative affect profile을 읽을 수 있으며, 다른 참가자 cohort에서도 재현되는가?

본 전달본은 2026-10-04 패키지의 업데이트다. 이전 폴더·ZIP과 원본 4종은 보존했다. 서버에는 이 날짜의 패키지를 전달한다. Analysis 1b와 2d 보강 방향은 승인되었지만, 세부 구현·primary family·통계 동결은 아직 필요하다. Affect-neighborhood retrieval은 후속 사용자 요청으로 Analysis 2의 정식 보조 분석에 포함한다. 채택은 승인되었고 거리·후보 수·null 및 평가 규칙은 D18에서 동결한다. Primary 승격이나 실행 완료를 뜻하지 않는다.

서버의 실제 코드·데이터·로그는 직접 확인하지 않았다. 이후 GitHub main의 정적 코드 검토는 수행했으며 [구현 상태](08_IMPLEMENTATION_STATUS.md)에 범위를 기록했다. 사용자가 전달한 전처리 산출물 보고는 보고된 사실이지 서버 재검증 결과가 아니다. 기존 체크리스트의 미체크 상태를 ‘미실행’의 증거로 취급하지 말고, 먼저 서버 현황을 조사한다.

## Latest training decision / 최신 학습 방향 — 2026-10-06

Joint B/V/S training remains the default. Brain-first → Joint is an optional additional strategy, not a mandatory second study. A shared Affect Head auxiliary loss is still a proposal. Result-driven iteration is allowed; preserve runs and distinguish selection-exposed results from independent validation. See D20/D21 and C10/C11 in the [decision register](04_DECISION_REGISTER.md), §4 of the [specification](02_IMPLEMENTATION_SPEC.md), and P11b in the [action items](03_ACTION_ITEMS.md). This update does not launch training.

Joint B/V/S 학습이 기본이다. Brain-first → Joint는 추가 전략이며 별도 연구 두 벌을 의무화하지 않는다. 공유 Affect Head 보조 loss는 아직 제안이다. 결과 기반 수정·탐색은 허용하고, 기존 run을 보존하며 선택에 사용한 결과와 독립 검증을 구분한다. 상세는 결정 기록 D20/D21·C10/C11, 구현 명세 §4, 작업 목록 P11b에 있다. 이번 문서 갱신은 학습 실행이 아니다.

## 📍 읽는 순서

| 순서 | 문서 | 역할 |
|---|---|---|
| 1 | [연구 스토리와 설계](01_STORY_AND_DESIGN.md) | 무엇을 왜 하는가 |
| 보강 우선 | [뇌 검증 보강과 추가 후보](06_NEURAL_VALIDATION_AMENDMENT.md) | 1b·2d 방향 승인, 내용 구별 보조 분석 채택 |
| 전처리 검토 | [자극별 반응과 시계열 입력](07_RESPONSE_ESTIMATION_REVIEW.md) | 블록 평균 권고의 근거·정정·미확인 항목 |
| 2 | [결정·정정 기록](04_DECISION_REGISTER.md) | 확정·제안·미확정 구분 |
| 3 | [구현 명세](02_IMPLEMENTATION_SPEC.md) | 데이터·분할·모델·loss·평가 |
| 4 | [상세 실행 목록](03_ACTION_ITEMS.md) | 순서·산출물·완료 기준 |
| 5 | [참고문헌과 근거](05_REFERENCES.md) | 선택의 근거와 한계 |
| 시작 지시 | [서버 AI에 전달할 프롬프트](SERVER_PROMPT.md) | 첫 작업 범위 |
| 코드 대조 | [구현 상태와 이행 경계](08_IMPLEMENTATION_STATUS.md) | 기존 코드와 최신 설계의 차이 |

저장소의 `docs/current`만 유지·편집한다. 과거 날짜별 전달 폴더, ZIP, 통합본은 당시의 export이며 독립적인 최신 원본이 아니다. 이 저장소에는 통합본·ZIP·날짜별 current 복사본을 추가하지 않는다. 작업 지침은 루트 [AGENTS.md](../../AGENTS.md)에 있다.

## 📌 상태와 문서 우선순위

- **유지:** 대화에서 명시한 연구 방향 또는 기존 설계의 핵심 원칙.
- **권고:** 이번 정리에서 제안한 운영 방법. 연구책임자의 승인 또는 사전 정의된 개발 절차가 필요하다.
- **미확정:** 데이터 확인·통계 검토·사용자 선택이 있어야 정할 수 있다.
- **확인:** 원문 또는 로컬 문서에서 확인한 범위. 서버 데이터까지 확인했다는 뜻은 아니다.

현재 사용자의 명시적 결정 → 승인된 freeze manifest → 본 패키지의 확정 원칙 → 기존 문서 순으로 해석한다. 본 패키지에서 ‘권고/미확정’인 내용은 자동 승인된 것으로 바꾸지 않는다. 기존 문서와 충돌하는 누출 방지 및 잘못된 해석은 [결정 기록](04_DECISION_REGISTER.md)에 적힌 안전 규칙을 우선한다. 기존 preregistration이 실제 등록되어 있다면 소급 변경하지 말고 amendment와 exploratory 표시를 남긴다.

본 문서군은 `Server_Handoff_2026-10-06`에서 가져왔다. 그 이전 원본 `paper_v15.md`, `prereg_v2.md`, `implementation_v2.md`, `action_items_v1.md` 및 로컬 전달본은 삭제하거나 덮어쓰지 않았다. 사용자가 문서 기준 단일화를 승인함에 따라 이 브랜치에서는 `docs/current`가 후속 편집 기준이다. 과거 GitHub README·CLAUDE·H1–H4 논증·September review는 [역사 기록](../archive/README.md)으로 이동/보존했다. 이번 변경은 연구 설계 전체가 이미 동결되었거나 코드가 구현되었다는 뜻이 아니다.

## ✍️ 서버의 첫 작업

먼저 기존 구현과 결과의 상태를 확인하고, 데이터·분할·OOF 누출 검사를 준비한다. 이어서 개발 데이터 안에서만 작은 brain-only baseline과 encoding pilot을 실행할 수 있는지 판단한다. 미확정 통계·split·replication 규칙을 임의로 확정한 대규모 본실험은 시작하지 않는다.

첫 반환물은 `server_status.md`, `data_audit.md`, `split_audit.md`, `decision_queue.md`, `next_actions.md` 또는 같은 내용을 담은 단일 보고서다. `project/output/audits/` 안에 모으고 루트에 흩어 놓지 않는다. 각 주장에 실제 경로, 로그, 설정 또는 검사 결과를 붙인다. 보고서 제목만 만들고 내용을 추측해서 채우지 않는다.

## ⚠️ 전달 시 주의

이 패키지에는 원본 fMRI·동영상·caption, 실행 결과, 모델 weight가 포함되어 있지 않다. 서버 AI는 서버의 실제 경로를 찾아 별도 manifest로 기록해야 한다. 로컬 Mac 경로를 서버 경로로 그대로 사용하지 않는다. 기존 overview v1 PNG는 이번 보강 전 도안이며 수정하지 않았다. 1b·2d가 반영된 도식으로 오인하지 않는다. 새 연구 흐름의 편집 원본은 06 문서의 Mermaid이며, 이미지 속 수식이나 gate가 최신 결정 기록보다 우선하지 않는다.
