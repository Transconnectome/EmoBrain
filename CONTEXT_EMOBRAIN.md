# EmoBrain Compact Context

Agent / 협업자 가 빠르게 참조할 single source of truth. 자세한 내용은 각 reference 파일.

## 정체성

**EmoBrain.** 한 paper. **Title.** *EmoBrain. Decoding fine-grained emotion from human brain activity.*

**Spine.** Framework novelty path. 5 novelty (NV0-NV4) 의 결합 = multi-modal LLM-based brain emotion decoder.

**Repo path.** `/pscratch/sd/s/sjmoon/EmoBrain/`.

## 5 Novelty

| ID | Name | 한 줄 |
|----|------|-------|
| NV0 | LLM-based brain emotion decoder | Emotion 분야 의 LLM 통합 fine-grained brain decoder 의 first instrument |
| NV1 | 3-modality LLM fusion | brain + video + caption 을 single LLM forward 의 token sequence 로 통합 |
| NV2 | MindCaptioning bridge | Human-written neutral caption (MindCaptioning, Horikawa) 의 brain-context bridge + 우리 generated caption 비교 |
| NV3 | Modular brain encoder | E1 raw ROI (control) / E2 Ridge / E3 BFM frozen / E4 VLM hidden (image pretrain + fMRI fine-tune) 의 4 swappable adapter. 공통 patchify 없음. Encoder 순위 자체 는 spine 아님 |
| NV4 | 34D independent emotion regression + curriculum | 34 감정 은 독립 점수 (bittersweet 예). Per-emotion MSE (curriculum stage 별 subset), z-score 필수. Softmax / sum-to-1 / KL 금지. Curriculum (top-1 → top-2 → top-k → full 34D) 은 stepwise validation. 실행 = Track A (direct) → Track B (distillation) × sub-stage 1-4 |

NV0 = spine framing axis. NV1-NV4 = 그 구성 component.

## Architecture (요약)

```
INPUT
  fMRI  →  Brain encoder (raw ROI / Ridge / BFM / VLM)       →  brain token
  Video →  Vision encoder (CLIP / V-JEPA2 / VideoMAE)        →  video token
  Caption  (MindCaptioning human + 우리 generated)          →  text token
  Prompt  (task instruction + 34-cat inventory)              →  instruction token

FUSION
  [brain | video | text | instruction]  →  Qwen3-VL LLM (LoRA)
                                          또는 POYO (ablation)
                                          →  fused hidden

OUTPUT (NV4. 34D independent emotion regression + curriculum)
  34D linear regression head. Softmax / sum-to-1 / KL 금지.
  각 감정 은 독립 점수 (bittersweet 예).
  Preprocess = z-score per emotion (mean 0, std 1, training set fit).
  Curriculum (per-emotion MSE 원리 유지, subset A 만 다름)
    1 top-1     A = {자극 별 rating 1위}
    2 top-2     A = {상위 2}
    3 top-k     A = {rating > threshold}
    4 full 34D  A = {1..34}
  Loss (Track A direct)     L_main = sum_{k ∈ A} (pred_k - target_k)^2
  Loss (Track B distill)    L_total = L_main + λ × L_distill (teacher 34D MSE 재현)
```

상세 spec 은 `docs/notes/architecture_design_20260629.md`. Spine narrative 는 `Paper/framework_EN.md` + `Paper/framework_KR.md`. Chronological decision 은 `docs/notes/project_decisions.md`.

## Data

| Source | Subjects | Stim | Rating | 특성 | 상태 |
|--------|----------|------|--------|------|------|
| **Horikawa** naturalistic video fMRI | 5 | 2185 unique (fMRI 2196 presentation 중 11 중복 제외) | Cowen 34-cat + 14-dim + V/A continuous | visual feature 위주 | 사용 중 |
| **Emo-FilM** | TBD | TBD | TBD | narratives + temporal dynamics | 다운로드 예정 (cross-cohort 평가 후보) |

부수 데이터. MindCaptioning human-written caption (Horikawa stim 매칭). Qwen-VL caption (2185 stim, 우리 generated). V-JEPA2 / CLIP / DINOv2 / VideoMAE pretrained + scratch (Horikawa).

## 디렉토리

```
EmoBrain/
├── project/
│   ├── shared/                        (공통 data + baseline)
│   ├── code/                          (main code)
│   │   ├── adapters/                  (brain/video → LLM token adapter)
│   │   ├── brain_encoder/             (raw ROI / Ridge / BFM / VLM modular)
│   │   ├── vision_encoder/            (CLIP / V-JEPA2 / VideoMAE)
│   │   ├── caption_loader/            (MindCaptioning human + 우리 generated)
│   │   ├── fusion/                    (multi-modal LLM wrapper)
│   │   ├── training/                  (4 stage curriculum)
│   │   └── evaluation/                (variance partitioning + ceiling + dissociation)
│   ├── config/  sample_scripts/  output/
├── archive/                           (이전 framing 보존, 현 작업 과 무관)
├── external/  docs/  Paper/  tools/
└── 7 root .md
```

### Code 위치 quick reference

- **Main**. `project/code/{adapters,brain_encoder,vision_encoder,caption_loader,fusion,training,evaluation}/`.
- **Shared**. `project/shared/code/{probes,bfm_embeddings,ssl_pretrain,analysis,tools}/`.

## 환경

- **Compute**. NERSC Perlmutter m4641. CPU queue (probe), GPU queue (LLM fusion, LoRA).
- **Python env**. `/pscratch/sd/s/sjmoon/tribev2/.venv` (probe, 분석). `/pscratch/sd/s/sjmoon/brainvlm_qwen_env` (LLM fusion).

## Operating Rules

- Root .md 7 개 유지 (README, README_KR, CONTEXT_EMOBRAIN, ONBOARDING, CLAUDE, CODEX, ACTION_PLAN). 새 root .md 추가 금지.
- Forward plan / phase report 는 `docs/` 와 `docs/reports/` 에만.
- Narrative 는 `Paper/framework_EN.md`, `framework_KR.md` (framework_EN 가 spine). Methodology 는 `Paper/methodology.md`.
- Decision log 는 `docs/notes/project_decisions.md` (chronological, 가장 최신 위).
- Sbatch 명령은 사용자 사전 승인 후.
- 모든 .py 는 .sh 동반. Bash 명령은 절대경로.

## Go-to docs

- **Code 구현 명세**. `docs/notes/implementation_spec_20260702.md` (Claude Code 대상, DECIDED / OPEN / CAUTION, Acceptance, 34개 감정 순서). Code 시작 시 canonical spec.
- **Spine narrative**. `Paper/framework_EN.md` + `framework_KR.md`.
- **Architecture design**. `docs/notes/architecture_design_20260629.md` (NV ↔ component 매핑, token budget, 4 stage curriculum spec, evaluation framework, open question).
- **Decision log**. `docs/notes/project_decisions.md`.
- **Action plan**. `ACTION_PLAN.md` (S7-S11 ground-level weekly action).
- **34 감정 canonical 순서**. `project/shared/data/cowen34_order.txt`.

## Cross-subject caveat

MindCaptioning external test 는 **cross-subject 이지만 cross-stimulus 는 아님** (subject 6 명 이 Horikawa 5 명 과 안 겹치지만 stimulus 는 Cowen 계열 과 겹침). 리포트 마다 "cross-subject external test, NOT cross-stimulus" 를 명시. Cross-stimulus 평가 는 Horikawa 내부 held-out stimuli split (별도).

## Framework 검증 축 (2026-07-03 확정)

두 축 을 명확히 구분.

| 축 | 실험 위치 |
|----|-----------|
| Encoder 순위 확정 | Track A 에서 E1-E4 각각 학습 (brain + question only) |
| Context lift (framework primary) | Track B 에서 **Track A best encoder 1 개 만** distillation |

Track B 는 E1-E4 각각 진행 아님. Track A best 하나 만. Framework 검증 의 primary question 은 **"context (video + caption) 가 brain-only 예측 을 얼마나 끌어 올리는가"** 이지 "어느 encoder 가 distillation 과 잘 맞는가" 가 아님.

## Workflow triggers

| Trigger | 용도 | Workflow |
|---------|------|----------|
| `[deep search]` | 외부 논문 / code / data 검색 후 reference doc 갱신 | `docs/workflows/literature_sota_workflow.md` |
| `[experiment card]` | 모델 아이디어 를 구조화 된 experiment card 로 | `docs/workflows/experiment_planning_workflow.md` |
| `[red team]` | Multi-reviewer critique + blue-team 응답 | `docs/workflows/red_blue_team_review.md` |
| `[weekly status]` | Git 변경 + canonical doc 기반 status report | `docs/workflows/weekly_update_workflow.md` |
| `[verification]` | Path / completeness / overclaim check (tools/) | `python3 tools/check_md_completeness.py` |
