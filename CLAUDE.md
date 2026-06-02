# FEELIN Claude Instructions

Read `CONTEXT_FEELIN.md` first. Active forward plan is `docs/masterplan_v2.md`.

## Operating Rules

- Root .md 파일 새로 만들지 않음. 7개 (README.md, README_KR.md, CONTEXT_FEELIN.md, ONBOARDING.md, CLAUDE.md, CODEX.md, ACTION_PLAN.md) 로 유지.
- Forward plan / phase report 은 `docs/` 와 `reports/` 에만 추가.
- Narrative 는 `Paper/framework_EN.md`, `framework_KR.md`.
- Methodology 는 `Paper/methodology.md`.
- Decision log 는 `notes/project_decisions.md`.
- 실험 코드는 `code/` 아래 (`bfm_embeddings/`, `probes/`, `analysis/`, `tools/`).
- 입력 데이터 (splits, target matrices) 는 `data/`.
- 추출된 features / logs 는 `output/`.
- 분석 결과 (CSV, figure, slide text) 는 `results/`.
- 모델 checkpoints 는 `baseline/`.
- 추출된 raw data / checkpoint / output 덮어쓰지 않음.

## Scientific Rules

- FEELIN 은 model-development project. Emotion theory paper 아님.
- 세 tier baseline 비교가 본 framing: T1 statistical floor, T2 brain foundation model ceiling, T3 multimodal + vision-language upper bound.
- Tier 2 brain foundation model: SwiFT (NewE96 + 변종), Brain-JEPA, NeuroSTORM. (BrainLM 은 490 timepoint × A424 atlas 고정으로 Horikawa 비호환, scope 제외.)
- Tier 1 floor 는 본 model axis 가 아닌 minimum baseline.
- Horikawa stimulus 수 = 2185 canonical.
- Claim 과 measured result 분리. Over-claim 금지.
- 약어 (BFM, VLM, RSA, CKA) 첫 등장 시 풀어쓰기.

## Required Checks

문서 구조 변경 후:
```bash
python3 scripts/check_md_completeness.py
python3 scripts/build_project_status.py
```
