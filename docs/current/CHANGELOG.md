# EmoBrain 설계 보강 변경 기록

_2026-10-06 · 2026-10-04 전달본의 후속 버전_

---

## 📋 변경 내용

- Analysis 1a 유지, 1b에 content–affect의 실제 fMRI 공유/조건부 설명력 비교 추가.
- Analysis 2a–c 유지, 2d에 독립 neural validation 원칙과 개발용 content-side bridge 권고 추가.
- Analysis 3은 같은 모델의 readout·cohort replication으로 유지.
- 최초 작성 시 보조 제안이었던 affect-neighborhood retrieval을 후속 사용자 요청으로 채택된 Analysis 2 보조 분석으로 갱신. 감정 threshold·공동학습 없음.
- 스토리, 구현 명세, 작업 목록, 결정 기록, 참고문헌, 서버 시작 지시를 동기화.
- P13b, P19b 추가. P17b는 채택된 보조 retrieval의 feasibility·평가·보고. D16–D18에 미확정 실행 설정을 명시.
- 각 새 항목의 여섯 질문 rationale, 해석 변경 기준, 주장 불가 범위는 06 문서에 수록.

## 🔐 보존·상태

- 이전 2026-10-04 폴더와 ZIP은 변경하지 않는다.
- paper_v15.md, prereg_v2.md, implementation_v2.md, action_items_v1.md 원본은 변경하지 않는다. 이 전달본은 실행 설계의 후속본이며 원고·실제 prereg amendment 반영은 P26에서 별도 수행한다.
- Nature-style overview v1 PNG는 보강 전 도안으로 보존한다. 새 버전의 PNG를 생성했다는 뜻이 아니다.
- 서버 실험, 수치 검증, 모델 학습을 실행하지 않았다.
- 새 보강의 방향 승인과 본실험 통계·split·family 동결은 다르다.
- 2d 구현 권고와 채택된 보조 분석을 이미 검증된 방법/결과로 서술하지 않는다.
- 07 전처리 검토 추가: lagged block mean 출발점 권고, 시계열 보존, D04 미동결, 원본 영상/제시 block 구분, Brain-JEPA와 GLMsingle 자동 도입 금지.
- 원문 methods와 로컬 prereg B1의 근거를 확인했으나 서버 blocks_mcap·runz를 검증하지 않았다.

## 📍 읽을 곳

[연구 스토리](01_STORY_AND_DESIGN.md) → [보강 상세](06_NEURAL_VALIDATION_AMENDMENT.md) → [작업 목록](03_ACTION_ITEMS.md).

이전 handoff는 통합본을 제공했다. 저장소 단일화 이후에는 아래 정책을 따른다: `docs/current`의 분리본만 편집하며 통합본·ZIP을 중복 관리하지 않는다.

## 🔍 검수 범위

기존 handoff 제작 단계에서는 SHA256 manifest와 ZIP 무결성을 확인했다. 저장소 단일화에서는 current 내부 링크, 문서 구조, 코드 fence, archive 보존과 diff 범위를 검사하며 새 ZIP/통합본/manifest 사본을 만들지 않는다. 이 검수는 실험 코드의 누출 test나 실제 분석 효과 검증을 대체하지 않는다. Mermaid의 문법 기본 요소를 정적으로 점검하지만 별도 렌더러의 시각 검수는 수행하지 않는다.

## 🔄 저장소 기준 단일화 — 2026-10-06

- 사용자 승인에 따라 `docs/unify-study-design` 브랜치에서 `docs/current`를 단일 편집 기준으로 설정했다. Main 병합 또는 PR 생성은 이 작업에 포함하지 않는다.
- 루트 README·CLAUDE·CONTEXT·project README를 current로 연결하고, 이전 본문·H1–H4 논증·실행 안내·September review·decision/build history를 `docs/archive/pre-handoff-2026-10-06`에 보존했다. 주요 옛 진입점은 짧은 redirect로 남겼다.
- 루트 AGENTS에 rationale, 권한/해석 경계, 파일 정리 규칙을 통합했다. 날짜별 current 복제·ZIP·통합본을 만들지 않는다. Mac 프로젝트에는 새 저장소나 파일을 만들지 않는다.
- `08_IMPLEMENTATION_STATUS.md`에 정적 코드 감사의 근거와 미확인 서버 범위를 기록했다. 핵심 Python 코드·데이터·결과·환경은 변경하지 않았다.
- 전처리 보고를 수신한 사실과 사용자의 ‘후보 비교 중’ 정정을 07 문서에 기록했다. 실제 최종 test 기반 선택이 이루어졌다고 단정하지 않는다.
- ROI 추가 효과 질문은 D19/R15의 검토 후보로만 기록하고 문헌을 추가했다. 기존 ROI reliance와 subset별 재학습을 구분했으며, primary 편입·실행·가설 동결은 하지 않았다.
- 기존 승인된 세 분석, target별 독립 학습, nested OOF, output-only guidance를 유지했다. 미확정 결정을 승인된 것으로 승격하지 않았다.
