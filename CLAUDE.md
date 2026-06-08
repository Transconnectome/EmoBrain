# EmoBrain Claude Instructions

Read `CONTEXT_FEEL.md` first. Active forward plan is `docs/masterplan_v3_emobrain.md`.

Project name = EmoBrain (since 2026-06-08). Repo path `/pscratch/sd/s/sjmoon/FEELIN/` preserved. Previous v4 framing archived under `archive/v4_20260602/`.

## Operating Rules

- Root .md 파일 새로 만들지 않음. 7개 (README.md, README_KR.md, CONTEXT_FEEL.md, ONBOARDING.md, CLAUDE.md, CODEX.md, ACTION_PLAN.md) 로 유지.
- Forward plan / phase report 은 `docs/` 와 `docs/reports/` 에만 추가.
- Narrative 는 `Paper/framework_EN.md`, `framework_KR.md`.
- Methodology 는 `Paper/methodology.md`.
- Decision log 는 `docs/notes/project_decisions.md`.
- 실험 코드는 `project/shared/code/` 아래 (`probes/`, `bfm_embeddings/`, `dir1_brainvlm/` (Direction 1), `dir2_multimodal/` (Direction 2, `legacy_phase2/` 포함), `ssl_pretrain/`, `analysis/`, `tools/`).
- 입력 데이터 (splits, target matrices) 는 `project/shared/data/`.
- 추출된 features / logs 는 `project/shared/output/`.
- 분석 결과 (CSV, figure, slide text) 는 `project/shared/results/`.
- 모델 checkpoints 는 `external/checkpoints/`.
- 추출된 raw data / checkpoint / output 덮어쓰지 않음.

## Scientific Rules

- EmoBrain 은 active brain decoding for emotion 의 model-development project. Emotion theory paper 아님.
- 두 main axis 가 EmoBrain framing: **Direction 1 BrainVLM** (Qwen3-VL backbone + LoRA fine-tune) + **Direction 2 Multimodal Alignment** (Brain encoder + V-JEPA2 contrastive alignment). BFM 은 main scope 아님 (Direction 2 의 brain encoder 후보로만).
- Background benchmark (Phase 1) 의 frozen BFM (SwiFT NewE96 + 5 변종, Brain-JEPA, NeuroSTORM) 결과는 ROI baseline 못 넘음을 확정. EmoBrain framing 의 motivation evidence.
- Horikawa stimulus 수 = 2185 canonical.
- Claim 과 measured result 분리. Over-claim 금지.
- 약어 (BFM, VLM, LLM, ROI, RSA, CKA) 첫 등장 시 풀어쓰기.
- **Baseline 의무**. 모든 task 결과는 standard baseline suite (chance / ROI mean + Ridge / Phase 1 best BFM frozen reference / Video baseline) 와 함께 reporting. Baseline 없는 result 는 unreliable. 자세히 `docs/masterplan_v3_emobrain.md` Section 5 + `ACTION_PLAN.md`.

## Required Checks

문서 구조 변경 후:
```bash
python3 scripts/check_md_completeness.py
python3 scripts/build_project_status.py
```
