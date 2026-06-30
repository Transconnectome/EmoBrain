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
| NV3 | Modular brain encoder | raw ROI / Ridge / BFM / VLM 의 swappable adapter |
| NV4 | 34-distribution curriculum | top-1 → top-2 → top-k → full 34D KL 의 4 stage |

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

OUTPUT (4 stage curriculum)
  Stage 1  top-1    34-class CE
  Stage 2  top-2    multi-label CE
  Stage 3  top-k    k-hot sparse CE
  Stage 4  full 34D KL  (rater empirical distribution target)
```

상세 spec 은 `docs/notes/architecture_design_20260629.md`. Spine narrative 는 `Paper/framework_EN.md` + `Paper/framework_KR.md`. Chronological decision 은 `docs/notes/project_decisions.md`.

## Data

| Source | Subjects | Stim | Rating | 특성 | 상태 |
|--------|----------|------|--------|------|------|
| **Horikawa** naturalistic video fMRI | 5 | 2185 | Cowen 34-cat + 14-dim + V/A continuous | visual feature 위주 | 사용 중 |
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

- **Spine narrative**. `Paper/framework_EN.md` + `framework_KR.md`.
- **Architecture design**. `docs/notes/architecture_design_20260629.md` (NV ↔ component 매핑, token budget, 4 stage curriculum spec, evaluation framework, open question).
- **Decision log**. `docs/notes/project_decisions.md`.
- **Action plan**. `ACTION_PLAN.md` (S7-S11 ground-level weekly action).
