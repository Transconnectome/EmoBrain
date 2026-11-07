# 서버 AI 시작 지시문

_첨부 패키지와 함께 전달할 작업 요청 · 2026-10-06_

---

## 📍 Current development entry / 현재 개발 시작점 — 2026-10-08

For the user's current request to implement code and small pilots while SDC comparison continues, follow [10_PILOT_IMPLEMENTATION_HANDOFF.md](10_PILOT_IMPLEMENTATION_HANDOFF.md) and the coordination board. Its final section contains separate prompts for Claude Code and Codex. The design documents below remain authoritative; this changes the immediate work order, not the scientific scope.

SDC 비교 중 코드와 소규모 pilot을 준비하는 현재 요청은 [10_PILOT_IMPLEMENTATION_HANDOFF.md](10_PILOT_IMPLEMENTATION_HANDOFF.md)와 작업판에 따라 진행한다. 마지막 절에 Claude Code·Codex별 전달 프롬프트가 있다. 아래 연구 기준은 유지하며 당장 할 일의 순서를 구체화한 것이지 연구 범위를 바꾼 것이 아니다.

## 🎯 연구 목적

Latest encoder/feature detail: read 01 §9.1a–9.2c, 02 §3a–3c, D22–D24 and P07b/P08b/P11c. Do not load externally pretrained brain weights. MLP and ROI-token Transformer are architecture candidates; JEPA-style is a proposed auxiliary objective, not a third pretrained backbone. Keep Participant Map separate from Brain Encoder in both teacher and student. Frozen V-JEPA/text backbones remain in scope. Layer/window/pooling numbers are development proposals pending QA; this documentation update does not authorize downloads or jobs.

최신 encoder/feature 상세는 01 §9.1a–9.2c, 02 §3a–3c, D22–D24, P07b/P08b/P11c를 읽는다. 외부 pretrained brain weight를 로드하지 않는다. MLP·ROI-token Transformer는 구조 후보, JEPA-style은 보조 목적함수 제안이다. Teacher와 student 모두 Participant Map과 Brain Encoder를 구분한다. Frozen V-JEPA/text backbone은 유지한다. Layer/window/pooling 숫자는 QA 전 개발안이며 문서 갱신만으로 다운로드·job을 실행하지 않는다.

EmoBrain 연구를 이어서 진행해줘. 이 연구는 감정 decoding 최고 성능을 만드는 것이 아니라, 뇌 반응과 visual/semantic content가 어떤 관계를 이루며 teacher와 brain-only student가 그 관계를 무엇으로 학습하고 실제 affect prediction에 어떻게 사용하는지 검정하는 neuroscience 연구다.

Teacher는 training 시 brain + video + caption을 받는다. Student는 training과 inference 모두 brain-only이며 label과 OOF teacher output으로 학습한다. Visual/semantic probe는 기본적으로 학습 loss가 아닌 사후 held-out 평가다. Normative affect annotation은 fMRI 참가자의 자기보고가 아니다. 34-D, 14-D, VA-2, VAD-3는 codebook 확인 후 별도 모델로 학습하며 공동학습하지 않는다.

## 📚 먼저 읽을 문서

작업 브랜치는 `docs/unify-study-design-20261006`이야. 이후 문서·코드·실험 관련 변경은 이 브랜치에서 이어가고, 실험 실행과 주요 설계·결과 검토가 끝난 뒤 사용자가 명시적으로 승인할 때만 main에 병합해. 브랜치 전환 전 서버의 미커밋 변경과 실행 중인 작업을 확인하고 보존해. 이 지침 자체가 GPU 작업 실행이나 PR 생성을 승인하는 것은 아니야.

저장소 루트의 `AGENTS.md`와 `docs/current/00_README.md`부터 읽어줘. 이어 같은 폴더의 `01_STORY_AND_DESIGN.md`, `04_DECISION_REGISTER.md`, `02_IMPLEMENTATION_SPEC.md`, `03_ACTION_ITEMS.md`, `05_REFERENCES.md`, `06_NEURAL_VALIDATION_AMENDMENT.md`, `07_RESPONSE_ESTIMATION_REVIEW.md`, `08_IMPLEMENTATION_STATUS.md`를 읽어줘. `docs/current`만 유지·편집하고 과거 H1–H4, 날짜별 handoff, 통합본·ZIP은 역사 자료로 취급해줘. 문서 브랜치를 받았다고 main을 병합하거나 진행 중인 서버 작업을 덮어쓰지 마.

기존 설계를 무조건 새로 구현하거나 이미 실행한 결과를 버리지 말고, 현재 코드·데이터·로그와 대조해줘. 이번 패키지의 ‘권고/미확정’을 사용자 승인된 확정값으로 바꾸지 마. 이미 실제 preregistration이 있다면 변경을 amendment 또는 exploratory로 기록해줘.

2026-10-06 보강은 1b의 content–affect 뇌 설명력과 2d의 독립 뇌 검증이야. 방향은 승인되었지만 D16/D17의 세부 구현·family는 pilot과 freeze가 필요해. Affect-neighborhood retrieval은 후속 요청으로 Analysis 2의 보조 분석에 포함 승인됐어. D18의 거리·후보 수·null 규칙을 동결하고 affect-output-only control과 함께 수행하되, primary 승격이나 완료로 오인하지 마. 2026-10-04 패키지 대신 이 업데이트본을 기준으로 차이를 확인해줘. 07_RESPONSE_ESTIMATION_REVIEW.md에 전처리 검토도 추가했어. blocks_mcap이 4초 지연, 휴지기, nuisance, run 정규화를 어떻게 적용했는지 먼저 확인해줘. 자극별 한 벡터가 단순 평균을 강제하지 않으며, 시계열은 보존하고 Brain-JEPA나 GLMsingle을 자동 도입하지 마.

## 🔍 첫 번째 작업 범위

**Preprocessing/QC update — 2026-10-07:** Read [09_PREPROCESSING_HANDOFF.md](09_PREPROCESSING_HANDOFF.md) before deciding on masks, OFC pooling or Horikawa SDC. Preserve v2 and active authorized work. Separate low signal, mask exclusion and localization uncertainty. MindCaptioning displacement is not a Horikawa measurement. The no-GM comparison is a proposed limited sensitivity, not a new primary pipeline or automatic job authorization.

**전처리/QC 갱신 — 2026-10-07:** Mask·OFC pooling·Horikawa SDC를 결정하기 전에 [09_PREPROCESSING_HANDOFF.md](09_PREPROCESSING_HANDOFF.md)를 읽어줘. v2와 기존 승인 작업을 보존하고 저신호·마스크 제외·위치 불확실성을 구분해줘. MindCaptioning 변위는 Horikawa 실측값이 아니야. No-GM 비교는 제한된 sensitivity 제안이지 새 primary나 자동 실행 승인이 아니야.

최신 학습 방향은 **Joint 기본, Brain-first → Joint 추가 비교 가능**이야(D20). Brain-first를 모든 fit의 필수 단계로 넣지 말고, 같은 최종 joint 모델의 선택적 학습 전략으로 다뤄줘. 정해진 실패 gate 없이도 이유 있는 탐색·비교를 제안할 수 있어. 공유 Affect Head의 `L_joint + η L_brain`은 D21 제안이지 기본 loss로 승인된 것이 아니야. Teacher warm-up을 시도한다면 초기화 단계부터 recipient/inner validation/outer test를 제외하고 checkpoint provenance를 검사해줘. 세부 구현은 02 §4, 작업은 P11b를 따라줘.

결과를 보고 학습법·최종 선택 모델을 바꾸는 것 자체는 금지가 아니야. 이전 run과 변경 이유·선택에 사용한 데이터·metric·시점을 보존하고, 이미 선택에 쓰인 test 결과를 독립 최종 검증으로 부르지 마. Prereg amendment와 exploratory/independent-validation 지위를 구분해줘. 이 탐색 원칙이 현재 첫 작업 범위 밖의 GPU 실행·예산 확대를 승인하는 것은 아니야.

1. 서버 프로젝트와 데이터·cache·checkpoint·실험 결과의 실제 위치 및 현재 실행 상태를 조사해줘.
2. 각 작업을 `재사용 가능 / 수정 필요 / 확인 못 함`으로 분류하고 근거 파일을 연결해줘. 미체크 문서만 보고 미실행이라고 판단하지 마.
3. Canonical stimulus, 두 cohort mapping, duplicates/repeats, presentation/run order, coordinate space, target codebook, caption을 감사해줘.
4. Nested OOF 경계와 train-only preprocessing을 검사해줘. Outer test 또는 student inner validation label을 teacher가 간접 사용한 cache는 유효한 결과로 취급하지 마.
5. P00–P08에 해당하는 audit와 작은 자동 QA를 수행해줘. 원자료·기존 결과는 보존해줘.
6. 개발 자료에서 B-only baseline, encoding, 최소 teacher/student pilot을 실행할 준비가 됐는지 판단하고 필요한 수정과 예상 계산량을 알려줘.
7. 1b 공통 score와 2d discovery/calibration/test 경계 및 bridge feasibility를 개발 범위에서 점검할 준비를 해줘. 독립 validation의 평가 predictor가 test brain/affect를 입력받지 않게 해줘.
8. Split K, small-n inference, replication 방식과 D16–D18 등 결정이 필요한 항목은 근거와 추천안을 묶어서 제시해줘. 본실험을 시작하기 전에 freeze할 항목은 임의 확정하지 마. D19의 ROI increment는 검토 후보이지 실행 승인이나 primary 편입이 아니야.

추가 자원 구매, 원자료 외부 업로드, 파괴적 삭제, 대규모 전체 실험은 이번 첫 작업 범위가 아니야. 감사와 누출 검사, 기존 결과 재현에 필요한 작은 확인부터 진행해줘.

## ⚠️ 반드시 지킬 해석 규칙

- Teacher 성능 또는 brain-only student 성공만으로 teacher가 brain을 사용했다고 결론 내리지 마.
- BVS–VS와 brain-swap은 각각 조건부 예측 이득과 frozen-model dependence를 묻는 다른 검사야.
- 전체 brain state나 final latent의 clean 복원은 QA이지 독립 기전 증거가 아니야.
- 서로 다른 OOF teacher의 latent를 동일 joint coordinate처럼 섞지 마.
- B-only 실패를 ‘뇌에 정보가 없다’로, 비유의를 ‘같다’로 해석하지 마.
- 작은 참가자 수 문제를 seed/fold/stimulus를 독립 참가자로 세어 해결하지 마.
- 같은 영상의 새 참가자 cohort는 participant replication이지 새로운 자극 분포의 검증이 아니야.
- Shared predictive component를 감정 생성의 인과적 매개로, q=g(content)를 실제 student latent 또는 새로운 정보로 해석하지 마.
- 2d에서 calibration한 target-cohort readout을 zero-shot transfer라고 부르지 마. Target cohort의 test ID를 discovery에서도 학습하지 마.
- 새로운 model/loss/control을 추가하기 전에 질문·대안 설명·근거·선택 이유·반례·주장 한계를 밝혀줘.

## 📦 첫 보고서

다섯 파일 또는 동등한 구조의 단일 보고서로 작성하고 `project/output/audits/` 안에 모아줘. 루트에 보고서·백업·새 handoff 사본을 만들지 마.

- `server_status.md`: 현재 구현·데이터·실험 상태와 재사용 가능한 산출물
- `data_audit.md`: 확인한 사실과 미확인 전제, 실제 수치·경로·codebook
- `split_audit.md`: 누출 위험, run/duplicate/repeat 처리, nested OOF 검사
- `decision_queue.md`: 사용자가 결정해야 할 사항과 근거 있는 추천
- `next_actions.md`: 바로 할 일 3–5개, 산출물·완료 기준·계산량

끝에는 ‘지금 확인된 것 / 아직 모르는 것 / 다음 한 단계’를 짧게 정리해줘. 분석을 실행하지 않았으면 결과를 만들어 쓰지 마.
