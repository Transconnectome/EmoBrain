# FEELIN Compact Context

Agent/협업자가 빠르게 참조할 single source of truth. 자세한 내용은 각 reference 파일.

## 정체성

FEELIN = **Brain Foundation Model for Emotion-aware Experience Learning In Naturalistic Data**.

**Big Question (Masterplan v2.0, 2026-05-19)**:
Naturalistic emotional experience 의 brain representation 을 context-aware foundation model 로 어떻게 잘 잡아낼 수 있는가 — 단일 stimulus snapshot, multimodal stimulus 표상, 혹은 language-grounded VLM 통합 중 어느 축이 emotion 을 결정하는가?

이 프로젝트는 emotion theory paper 가 아니라 **model-development project**. 세 가지 representation tier (statistical floor / brain foundation model ceiling / multimodal-VLM upper bound) 를 동일 protocol 로 비교해 emotion 의 organizing principle 을 찾는다.

## Three-Tier Baseline

| Tier | Name | Models | Role |
|---|---|---|---|
| **T1** Floor | Statistical | Schaefer 200/400/1000 ROI mean + Ridge / Logistic | Minimum performance |
| **T2** BFM Ceiling | Brain Foundation Model | SwiFT (NewE96 + 5 변종), Brain-JEPA, NeuroSTORM | BFM-class ceiling (BrainLM 은 490 TR × A424 고정으로 Horikawa 비호환, 제외) |
| **T3** Multimodal / VLM | Visual-semantic + VLM | VideoMAE / DINOv2 / V-JEPA2 / CLIP + Qwen-VL caption + BrainVLM + TRIBE v2 | Context-aware upper bound |

## 4 Sub-Questions

1. **Floor**: 통계적 baseline (Schaefer ROI + Ridge / Logistic) 으로 V/A 와 6-class 가 어디까지 잡히는가?
2. **BFM Consistency**: 서로 다른 brain foundation model 들이 동일 evaluation 에서 같은 ranking 으로 정렬되는가, 아니면 모델 architecture 마다 잘 잡는 emotion 측면이 다른가?
3. **Representation Axis**: discrete label / visual-semantic feature ladder / multimodal language-grounded representation 중 brain RSA 와 가장 잘 정렬되는 것은?
4. **Context Integration**: ABCD pretrained BrainVLM 의 fMRI tokenizer 를 Horikawa fMRI 에 zero-shot transfer 한 후 emotion VQA 가 가능한가?

자세한 motivation / experiment / go-no-go 는 [`docs/masterplan_v2.md`](docs/masterplan_v2.md).

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
