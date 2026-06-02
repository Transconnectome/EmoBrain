# FEELIN Compact Context

Agent/협업자가 빠르게 참조할 single source of truth. 자세한 내용은 각 reference 파일.

## 정체성

FEELIN = **Transferable Emotion Brain Foundation Model**.

**Big Question (Masterplan v4, 2026-06-02)**:
Naturalistic fMRI 로부터 학습한 multi-dimensional emotion brain representation 이, 단일 dataset 과 label taxonomy 에 종속되지 않고 새로운 subject, 자극, emotion 어휘로 transfer 되는 emotion brain foundation model 이 될 수 있는가?

<sub>운영 정의 (operationalization, FEELIN testbed): Horikawa naturalistic fMRI 로 학습한 multi-dimensional emotion brain representation 이, metadata 가 풍부하지 않은 independent dataset / 새 subject / 다른 emotion taxonomy 로 transfer 되는 emotion brain foundation model 이 될 수 있는가? 그리고 어떤 supervision (scalar V/A vs Cowen 34-category vs 14-dimension vs open-vocabulary description) 과 어떤 brain encoder 가 가장 transferable 한 표상을 만드는가? supervision 과 encoder 비교는 SQ2 와 encoder-swap 축에서 다룬다.</sub>

이 프로젝트는 emotion theory paper 가 아니라 **model-development project**. contribution 은 "brain 이 video 를 이기나" 가 아니라 representation 의 **transfer / generalization / data-efficiency / universality** 다.

## Scope: 두 질문의 분리

| | 질문 A (측정 완료) | 질문 B (본 plan) |
|---|---|---|
| 묻는 것 | 같은 stimulus 에서 brain 이 video feature 를 이기나? | brain emotion representation 이 새 subject / dataset / taxonomy 로 transfer 되나? |
| video | 경쟁자 (brain 패배 = trivial) | teacher / oracle (새 fMRI 엔 적용 불가, 경쟁자 아님) |

Phase 1 + Phase 2 joint 가 질문 A 에 "넘지 못한다" 로 답했다. 이유는 crowd-sourced V/A label 이 stimulus 속성이라 video 가 이기는 게 trivial 하기 때문. **근거 (Horikawa 2020, iScience)**: emotion category 표상이 affective dimension 보다, transmodal region 에서 visual / semantic covariate (video feature) 를 능가. 그래서 scalar V/A 가 아닌 high-dimensional categorical target 이 올바른 전장.

## Target hierarchy (multi-dim 승격)

| Tier | Target | 비고 |
|---|---|---|
| Primary | Cowen 34-category, Cowen 14-dimension, OV emotion-text embedding | brain 고유 신호 + cross-dataset 호환 |
| Reference | V/A binary / regression | video 가 이기는 게 알려진 axis, floor / sanity 로만 |

## Cross-dataset evaluation (metadata 빈곤 해결)

1. **Shared text-embedding zero-shot** (main): brain → emotion-text space 사영, 새 dataset 의 native label 이름만으로 zero-shot retrieval.
2. **Label-space intersection** (안전 baseline): target dataset 이 가진 축만 잘라 평가.
3. **MLLM universal annotator**: OV-MER / AffectGPT 로 모든 dataset stimulus 에 OV 라벨 생성. Horikawa 는 Cowen gold, OV 는 norm 없는 target 에만.
4. **Representational alignment** (label-free): RSA / ISC ceiling.

## Brain encoder 후보 (SQ1 / SQ2 swap 축)

SwiFT (NewE96 + 5 변종), Brain-JEPA, NeuroSTORM. BrainLM 은 490 TR × A424 고정으로 Horikawa 비호환, 제외.

자세한 sub-question (SQ1 transfer / SQ2 supervision richness / SQ3 geometry / SQ4 data-efficiency / SQ5 where) 와 go-no-go 는 [`docs/masterplan_v2.md`](docs/masterplan_v2.md).

## Canonical Data

- Horikawa/Cowen stimulus 수: **2185**
- Horikawa subject: **5명 (sub-01..05)** 모두 동일 자극 본 fMRI
- Split: stimulus-stratified (V quartile × A quartile) 80/10/10, 같은 자극 → 모든 subject 동일 split
- 5 TR 캐시 (`Horikawa_embedding/...`) 는 reference 만, 본 분석에 사용 X

## Canonical 파일

| 파일 | 역할 |
|---|---|
| `README.md`, `README_KR.md` | 사람 entry point (Big Q + 3-tier + phase status) |
| `docs/masterplan_v2.md` | **forward-looking masterplan** (phase, sub-question, go-no-go) |
| `reports/phase1_foundation.md` | 현재 진행 phase 보고서 |
| `Paper/framework_KR.md`, `framework_EN.md` | canonical narrative |
| `Paper/methodology.md` | canonical 실험 방법 |
| `notes/benchmark_design.md` | Dataset × BFM × Task 매트릭스 디테일 |
| `notes/project_decisions.md` | 영구 decision log |
| `reference/{datasets, task, papers, code_resources, training_strategy}.md` | 각 axis 별 reference |
| `ACTION_PLAN.md` | v1 legacy 실행 plan (week-level detail) |
| `workflows/README.md` | operating workflow 안내 |

## 운영 규칙

- Root markdown 새로 만들지 말 것. Narrative 는 `Paper/framework_*.md`, methods 는 `Paper/methodology.md`, 실행은 `docs/masterplan_v2.md` + `reports/phase{N}_*.md`.
- 약어 (BFM/VLM/RSA/CKA 같은 약어) 첫 등장 시 풀어쓰기.
- 통계 vs measured 명확히 분리.

## Workflow trigger

| Trigger | 의미 |
|---|---|
| `[deep search]` | literature/code/dataset 검색, reference 업데이트 |
| `[experiment card]` | 아이디어를 구조화된 experiment card 로 |
| `[red team]` | 모델/데이터/주장/계획 비판 |
| `[weekly status]` | decision/change/blocker/next action 요약 |
| `[verification]` | citation/path/completeness/overclaim 검증 |
