# EmoBrain 설계 보강 변경 기록

_2026-10-06 · 2026-10-04 전달본의 후속 버전_

---

## 📋 변경 내용

### Preprocessing evidence and server-AI handoff / 전처리 근거·서버 전달 — 2026-10-07

- English: Added a focused bilingual `09_PREPROCESSING_HANDOFF.md`, linked from current navigation, server prompt and estimator review. Reconciled the two reported QC summaries and subsequent Claude Code/Codex replies; separated low signal, intersection-mask exclusion and localization uncertainty. Corrected MC-to-HK displacement extrapolation, 11/12-parcel coverage mixing, one-run tSNR generalization and blanket “no other issues” claims. Recorded targeted mask/SDC audits, proposed no-GM sensitivity, temporal-source preservation, motion/timing/atlas/split/provenance checks and six-question rationales. No server files/jobs, model code, primary settings, main branch or actual preregistration were changed.
- 한국어: 전처리 전용 영한 `09_PREPROCESSING_HANDOFF.md`를 추가하고 current 목차·서버 시작 지시·estimator 검토에서 연결했다. 두 QC 보고와 Claude Code/Codex 후속 답변을 대조해 저신호·교집합 제외·위치 불확실성을 분리했다. MC→HK 변위 외삽, 11/12-parcel coverage 혼용, 한 run tSNR 일반화, ‘나머지 문제없음’을 정정했다. 표적 mask/SDC 감사, no-GM sensitivity 제안, 시계열 보존, motion/timing/atlas/split/provenance 검사와 여섯 질문 근거를 기록했다. 서버 파일·job·모델 코드·primary 설정·main·실제 preregistration은 변경하지 않았다.

### Joint-first learning and iterative experimentation / 학습 방향·탐색 원칙 — 2026-10-06

- English: Recorded Joint as the default and optional Brain-first → Joint as D20. Kept shared Affect Head auxiliary training as proposal D21. Added scope-safe warm-up, supervision/geometry interpretation, budget/provenance and P11b tasks. Corrected the blanket ban on result-driven revisions: models may be revised/selected through exploration, with original runs and selection exposure preserved and independent validation distinguished. Synchronized handoff, story, specification, decisions, actions, references, server prompt, implementation status and bilingual figure notes. No code, PNG, experiment, main branch or preregistration was changed.
- 한국어: Joint 기본과 선택적 Brain-first → Joint를 D20으로 기록하고 공유 Affect Head 보조 학습은 D21 제안으로 남겼다. Warm-up 범위·supervision/geometry 해석·학습량/provenance와 P11b 작업을 추가했다. 결과 기반 수정 자체의 금지를 철회하고 기존 run·선택 노출을 보존하며 독립 검증을 구분하도록 정정했다. 인수인계·스토리·명세·결정·작업·문헌·서버 지시·구현 상태·영한 도식 설명을 동기화했다. 코드·PNG·실험·main·실제 preregistration은 변경하지 않았다.

### Two-panel model figure and brain-use clarification — 2026-10-06

- English: Replaced the duplicate inference panel with Training / After Training; capitalized component labels and restored Fused State (Joint Latent). Updated the bilingual figure source and README links. Clarified existing BVS/VS, brain-swap and limited rescue interpretations; recorded Frank et al. (2021). No new primary objective, training run, architecture freeze or mandatory VS-guided student was introduced.
- 한국어: 중복 추론 패널을 없애고 Training / After Training으로 구성했으며 구성요소 대문자와 Fused State (Joint Latent) 표기를 적용했다. 영한 도식 원본과 README 링크를 갱신했다. 기존 BVS/VS·brain swap·제한된 rescue의 해석을 보강하고 Frank et al. (2021)을 기록했다. 새 primary loss·학습 실행·구조 동결·VS-guided student 필수화는 하지 않았다.

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

## 🔄 날짜 포함 작업 브랜치 — 2026-10-06

- 사용자 요청으로 작업 브랜치 이름을 `docs/unify-study-design`에서 `docs/unify-study-design-20261006`으로 변경한다. 이전 커밋과 문서 이력은 그대로 보존한다.
- 이후 문서·코드·실험 관련 변경은 날짜가 붙은 브랜치에서 계속한다. 실험 실행과 주요 설계·결과 검토 후 사용자 명시 승인 전까지 main은 변경하지 않는다.
- 루트 README, AGENTS와 서버 AI 전달문에 이 방침을 반영했다. 모델 코드나 실험 결과는 변경하지 않았다.

## 🌐 Bilingual README policy / README 이중 언어 원칙 — 2026-10-06

- English: Updated the root and project READMEs to place English first and a complete Korean version below a separator, with language navigation links. Added the same-file bilingual maintenance rule to AGENTS. No model code, study design or archived originals changed.
- 한국어: 루트와 project README를 영어 본문 다음에 구분선과 전체 한국어 본문이 오는 형식으로 바꾸고 언어 이동 링크를 추가했다. AGENTS에 같은 파일에서 양쪽 언어를 함께 갱신하는 원칙을 기록했다. 모델 코드, 연구 설계, 보관된 과거 원문은 변경하지 않았다.

## 📊 Current study overview / 최신 연구 개요 그림 — 2026-10-06

- English: Added `docs/assets/study_overview.png` and its bilingual source/scope/prompt record, with inline images and captions in both README language sections. The three panels include 1a/1b, 2a–d plus affect-neighborhood retrieval, and independent affect readouts/replication. Teacher–student training is shared preparation; the bridge remains pending validation. Illustrative graphics are not data. No scientific decisions were newly frozen and no experiment was run.
- 한국어: `docs/assets/study_overview.png`와 영한 원본·범위·프롬프트 기록을 추가하고 README 양쪽 언어에 그림과 설명을 연결했다. 1a/1b, 2a–d와 정서 이웃 내 retrieval, 독립 정서 target·재현성을 세 패널로 나타냈다. Teacher–student 학습은 공통 준비이고 bridge는 검증 전이다. 설명용 그림은 데이터가 아니며, 과학적 결정을 새로 동결하거나 실험을 실행하지 않았다.

## 📊 Concept-first overview / 개념 중심 Overview 수정 — 2026-10-06

- English: Replaced the method-first image after user feedback. Panel a now presents the conceptual motivation; panels b–d show the three complementary analyses. Training moved into a small Analysis 2 inset. Personal experience and unmeasured individual factors are explicitly out of measurement scope. Updated both README captions, figure source/prompt and amendment figure status. No new scientific analysis or result was added; earlier art remains in Git history.
- 한국어: 사용자 피드백에 따라 방법론 중심 그림을 교체했다. 상단 a는 연구 동기와 개념적 틀, 하단 b–d는 세 상보적 분석이며 학습 절차는 분석 2의 작은 영역으로 내렸다. 개인 경험과 측정하지 않은 개인 요인은 측정 범위 밖으로 명시했다. README 양쪽 설명, 도식 원본·프롬프트, 보강 문서의 그림 상태를 함께 수정했다. 새 과학적 분석이나 결과는 추가하지 않았고 이전 도안은 Git 이력에 남아 있다.

## 📊 Expanded model panel / 모델 패널 확장 — 2026-10-06

- English: Removed the figure title/subtitle/date strip, enlarged the layout to 4:3 and color-coded the three analyses. Expanded Analysis 2 to show the candidate brain-query teacher, separate brain-only student and output-only nested OOF guidance without removing post-training tests. Updated bilingual captions and source/prompt; no model code, design freeze or experiment changed.
- 한국어: 그림의 제목·부제·날짜 줄을 제거하고 4:3 지면과 분석별 색상을 적용했다. 분석 2에 후보 brain-query teacher, 별도 brain-only student, 출력 수준 중첩 OOF 지도를 확장해 표시하면서 학습 후 검정을 유지했다. 영한 설명과 원본·프롬프트를 갱신했으며 모델 코드·설계 동결·실험은 변경하지 않았다.
