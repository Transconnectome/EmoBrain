# 서버 AI 시작 지시문

_첨부 패키지와 함께 전달할 작업 요청 · 2026-10-04_

---

## 🎯 연구 목적

EmoBrain 연구를 이어서 진행해줘. 이 연구는 감정 decoding 최고 성능을 만드는 것이 아니라, 뇌 반응과 visual/semantic content가 어떤 관계를 이루며 teacher와 brain-only student가 그 관계를 무엇으로 학습하고 실제 affect prediction에 어떻게 사용하는지 검정하는 neuroscience 연구다.

Teacher는 training 시 brain + video + caption을 받는다. Student는 training과 inference 모두 brain-only이며 label과 OOF teacher output으로 학습한다. Visual/semantic probe는 기본적으로 학습 loss가 아닌 사후 held-out 평가다. Normative affect annotation은 fMRI 참가자의 자기보고가 아니다. 34-D, 14-D, VA-2, VAD-3는 codebook 확인 후 별도 모델로 학습하며 공동학습하지 않는다.

## 📚 먼저 읽을 문서

패키지의 `AGENTS.md`, `00_README.md`, `01_STORY_AND_DESIGN.md`, `04_DECISION_REGISTER.md`, `02_IMPLEMENTATION_SPEC.md`, `03_ACTION_ITEMS.md`, `05_REFERENCES.md`를 읽어줘. 통합본 `EmoBrain_Server_Handoff_ALL.md` 하나를 받았다면 그 안에 같은 내용이 모두 들어 있다.

기존 설계를 무조건 새로 구현하거나 이미 실행한 결과를 버리지 말고, 현재 코드·데이터·로그와 대조해줘. 이번 패키지의 ‘권고/미확정’을 사용자 승인된 확정값으로 바꾸지 마. 이미 실제 preregistration이 있다면 변경을 amendment 또는 exploratory로 기록해줘.

## 🔍 첫 번째 작업 범위

1. 서버 프로젝트와 데이터·cache·checkpoint·실험 결과의 실제 위치 및 현재 실행 상태를 조사해줘.
2. 각 작업을 `재사용 가능 / 수정 필요 / 확인 못 함`으로 분류하고 근거 파일을 연결해줘. 미체크 문서만 보고 미실행이라고 판단하지 마.
3. Canonical stimulus, 두 cohort mapping, duplicates/repeats, presentation/run order, coordinate space, target codebook, caption을 감사해줘.
4. Nested OOF 경계와 train-only preprocessing을 검사해줘. Outer test 또는 student inner validation label을 teacher가 간접 사용한 cache는 유효한 결과로 취급하지 마.
5. P00–P08에 해당하는 audit와 작은 자동 QA를 수행해줘. 원자료·기존 결과는 보존해줘.
6. 개발 자료에서 B-only baseline, encoding, 최소 teacher/student pilot을 실행할 준비가 됐는지 판단하고 필요한 수정과 예상 계산량을 알려줘.
7. Split K, small-n inference, replication 방식 등 결정이 필요한 항목은 근거와 추천안을 묶어서 제시해줘. 본실험을 시작하기 전에 freeze할 항목은 임의 확정하지 마.

추가 자원 구매, 원자료 외부 업로드, 파괴적 삭제, 대규모 전체 실험은 이번 첫 작업 범위가 아니야. 감사와 누출 검사, 기존 결과 재현에 필요한 작은 확인부터 진행해줘.

## ⚠️ 반드시 지킬 해석 규칙

- Teacher 성능 또는 brain-only student 성공만으로 teacher가 brain을 사용했다고 결론 내리지 마.
- BVS–VS와 brain-swap은 각각 조건부 예측 이득과 frozen-model dependence를 묻는 다른 검사야.
- 전체 brain state나 final latent의 clean 복원은 QA이지 독립 기전 증거가 아니야.
- 서로 다른 OOF teacher의 latent를 동일 joint coordinate처럼 섞지 마.
- B-only 실패를 ‘뇌에 정보가 없다’로, 비유의를 ‘같다’로 해석하지 마.
- 작은 참가자 수 문제를 seed/fold/stimulus를 독립 참가자로 세어 해결하지 마.
- 같은 영상의 새 참가자 cohort는 participant replication이지 새로운 자극 분포의 검증이 아니야.
- 새로운 model/loss/control을 추가하기 전에 질문·대안 설명·근거·선택 이유·반례·주장 한계를 밝혀줘.

## 📦 첫 보고서

다섯 파일 또는 동등한 구조로 보고해줘.

- `server_status.md`: 현재 구현·데이터·실험 상태와 재사용 가능한 산출물
- `data_audit.md`: 확인한 사실과 미확인 전제, 실제 수치·경로·codebook
- `split_audit.md`: 누출 위험, run/duplicate/repeat 처리, nested OOF 검사
- `decision_queue.md`: 사용자가 결정해야 할 사항과 근거 있는 추천
- `next_actions.md`: 바로 할 일 3–5개, 산출물·완료 기준·계산량

끝에는 ‘지금 확인된 것 / 아직 모르는 것 / 다음 한 단계’를 짧게 정리해줘. 분석을 실행하지 않았으면 결과를 만들어 쓰지 마.

