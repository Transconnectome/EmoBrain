# EmoBrain Canonical Rules (v7, 2026-08-19)

**논증 문서 (authoritative): `docs/paper_logic_merged.md`** — 대전제·RQ·가설 H1–H4.
결정 기록: `docs/notes/project_decisions.md`. 빌드 사이클: `docs/notes/build_log.md`.
수치 정본·열린 사항: `CONTEXT_EMOBRAIN.md`. 모델·데이터 계약: `project/README.md`.

**Codex 등 다른 agent 도 이 파일을 따른다.** compact context 는 `CONTEXT_EMOBRAIN.md` 를 먼저 읽는다.

⚠️ **`docs/archive/` 아래 문서는 전부 역사 기록이다.** 폐기된 프레임(LLM backbone, open-vocabulary,
zero-shot, 별도 논문 2편)을 현행처럼 서술하므로 **현재 방침의 근거로 인용하지 않는다.** 각 파일 상단에
무엇이 뒤집혔는지 배너가 있다. `archive/` (루트) 는 대용량 결과 트리와 문헌 원본 corpus 이며 별개다.

## 무엇을 하는 프로젝트인가

EmoViS 와 **한 편의 논문**으로 합친다. 감정 디코딩 성능 논문이 아니다.

**Main theme.** 감정 영상을 볼 때 뇌가 만드는 표상 구조는, 감정 라벨이 아니라 시각-의미 내용을
따른다. 그리고 그 조직은 시각피질을 넘어 transmodal 연합피질까지 이어진다.

**RQ.** 감정 영상을 볼 때 뇌의 감정 표상은 시각 처리 및 의미 처리와 어떤 관계에 있는가?
이 둘로부터 구성되는가, 아니면 환원되지 않는 별도의 것인가? 그 구성은 피질의 어디에서 일어나는가?

**대전제.** (1) 감정 경험은 고차원이다 — 자극 하나 → 여러 감정의 혼합 프로파일. (2) 프로파일들이
자극 간에 만드는 구조는 상당 부분 시각-의미 내용이 만드는 구조다. (3) 감정 단어 하나에 대응하는 고유한
뇌 표상이 따로 있는 것이 아니다. (4) 따라서 감정 전용 영역을 찾는 게 아니라, 시각-의미 처리가
어디서·어떻게 감정 프로파일을 지지하는 구조로 조직되는지를 찾는다.

**가설.** H1 설명력 대등 · H2 어긋나는 쌍에서 뇌 반응이 다름 · H3 transmodal 까지 이어짐 ·
H4 셋이 한 공간으로 통합됨. **네 가설 모두 반대 결과도 발표 가능한 주장이다** (문서 §3 참조).

## 모델

`project/code/decoder/` — LLM-free label-query decoder. **셋(brain + video + caption)을 한 memory 에
넣고 34개 감정 query 로 읽는다.** 출력 = 34개 연속 점수(log1p_z, softmax 없음). task = 자극별 34차원
프로파일 회귀.

**모델의 자리.** H1–H3 는 encoding/RSA 로 검정되며 모델을 필요로 하지 않는다. **모델이 논문에서 자리를
얻는 근거는 H4** (셋의 공동 통합 — 분석이 원리적으로 못 하는 일).

## 금지

- **자극을 감정 범주로 묶지 않는다.** top-1·임계값·그룹핑 금지. 전부 연속 프로파일 간 거리.
- **성능·SOTA 주장 금지.** "자극이 뇌보다 잘 디코딩한다"는 near-trivial motivation 이지 결과가 아니다.
- **경쟁 프레임 금지.** "probe 가 ratings 를 이긴다" 식 서술. 분해(decomposition)로 쓴다.
- LLM 을 모델 backbone 으로 재도입하지 않는다.
- **2차 출처(Perspective·리뷰 요약)로 방법을 서술하지 않는다.** 본 프로젝트에서 요약이 원논문의 기록
  양상과 약물을 둘 다 틀리게 전한 사례가 있었다.
- 파일명으로 논문을 인용하지 않는다. 저자·제목·venue 를 원문에서 확인한다.

## 실행

GPU job 은 사용자가 돌린다. 단일 절대경로 `bash ...sh` 명령으로 제공한다.
val 로 checkpoint 선택, 건드리지 않은 stimulus-held-out test 를 보고한다.
