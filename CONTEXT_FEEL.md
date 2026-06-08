# EmoBrain Compact Context

Agent / 협업자가 빠르게 참조할 single source of truth. 자세한 내용은 각 reference 파일.

## 정체성

**EmoBrain** = Active brain decoding for emotion via Vision-Language Models and Brain-Video Multimodal alignment.
**Branch**. `sj_NEW_20260608_perlmutter` (2026-06-08 framing pivot).
**Repo name 보존**. 기존 path `/pscratch/sd/s/sjmoon/FEELIN/` 그대로 유지 (rename 안 함).
**이전 framing (v4 universal emotion code, Track A SSL pretrain main)** 은 `archive/v4_20260602/` 에 보존.

## Two Axes (둘 다 main)

| Axis | 답하는 question | 핵심 method | 주요 reference |
|------|------------------|--------------|----------------|
| **Direction 1. BrainVLM** | fMRI 를 VLM / LLM 의 token modality 로 통합하면 emotion 의 multi-task (V/A score + Cat34 distribution + caption) 를 한 모델이 자연어로 출력 가능한가? | Qwen3-VL backbone + fMRI 2D ROI map patchify + LoRA fine-tune | MindLLM 2025, UMBRAE 2024, Mind Captioning 2025 (Horikawa Science Advances), MedBLIP 2023, BLIP-2 ICML 2023, LLaVA NeurIPS 2023 |
| **Direction 2. Brain-Video Multimodal** | Brain 이 video baseline 위에 추가하는 unique emotion variance 는 무엇이고, subject-invariant 표상으로 학습 가능한가? | Brain encoder (Brain-JEPA 또는 학습된 BFM) + V-JEPA2 video feature 의 InfoNCE contrastive alignment + variance partitioning | TRIBE 2025 (Meta FAIR, Algonauts 2025 1 위), VIBE 2025, Multi-modal brain encoding 2025, CineBrain 2025, Doerig 2024, BraVL TPAMI 2023 |

두 axis 는 complementary. BrainVLM 이 generative + multi-task, Multimodal 이 brain 의 정량적 contribution. BFM 자체는 main scope 에서 제외되었으나 Direction 2 의 brain encoder 로 활용 가능.

## Phase 1 결과 요약 (Frozen BFM 한계의 확인)

| Task | Best BFM (BJ resting) | ROI baseline | Chance |
|------|------------------------|--------------|--------|
| V_binary AUROC | 0.738 | **0.789** | 0.500 |
| A_binary AUROC | 0.662 | **0.678** | 0.500 |
| V_reg Pearson r | 0.330 | **0.396** | 0.000 |
| A_reg Pearson r | 0.221 | **0.233** | 0.000 |
| Cat34_multilabel macro AUROC | 0.679 | **0.711** | 0.500 |
| Cat34_soft mean Pearson r | 0.237 | **0.280** | -0.004 |

ROI mean + Ridge 가 모든 task 에서 BFM 보다 일관되게 높음. 원인 (Phase 1 audit `docs/reports/phase1_audit_20260604/` 참조).
1. Horikawa 자극의 시간 길이 T 중앙값 5 TR, 71.6% 가 T=5. BFM input (BJ 16, NS/SwiFT 20 TR) 의 평균 63-70% 가 zero padding.
2. BFM 의 spatial-temporal joint dynamics 강점이 짧은 input regime 에서 활용 못 됨.
3. ROI 의 시간축 평균 (450,) 은 padding 영향 없는 깨끗한 baseline.

이 결과가 Direction 1 (BrainVLM 의 active fine-tune) + Direction 2 (Video 정보 보완) 의 motivation.

## Field Trend (motivation 보강)

- **Frozen BFM 단독 결과의 한계**가 broader field 에서 공통. MindLLM, UMBRAE, Mind Captioning 같은 brain-to-text decoding 의 SOTA 가 모두 LLM/VLM 을 prior 로 사용. BFM frozen embedding 단독은 거의 안 보고됨.
- **VLM / LLM 기반 brain decoding 의 paradigm**. "fMRI → frozen semantic manifold (LLM/VLM embedding) → 생성" 의 3-stage pipeline 이 표준. Brain-side adapter (linear projection 또는 Q-Former) 만 학습.
- **Multimodal brain alignment 의 standard evaluation**. Variance partitioning (multimodal vs unimodal). Algonauts 2025 winner 들이 공통으로 사용. Brain unique contribution 의 quantification 이 contribution 의 강점.
- **Emotion specific gap**. 위 trend 의 main paper 들은 image / text reconstruction 중심. **Emotion 의 fine structure (Cat34 multilabel, mixed valence) 를 active VLM / multimodal 로 학습한 사례는 비어있음**. EmoBrain 의 novelty.

## Tasks

| Task | Phase | Metric |
|------|-------|--------|
| V/A Binary | 측정 완료 | AUROC + balanced accuracy |
| V/A Regression | 측정 완료 | Pearson r + MAE + MSE |
| Cat34 Multilabel (threshold 0.10) | 측정 완료 | macro AUROC + macro F1 |
| Cat34 Soft Distribution | 측정 완료 | mean Pearson r + top1 accuracy |
| Mixed Valence (Vaccaro 2024) | 미측정, Direction 1 + 2 둘 다 적용 | 3-way classification balanced accuracy |
| Caption Embedding Regression | 미측정, Direction 1 specific | Pearson r averaged over caption dim |
| Emotion VQA | 미측정, Direction 1 specific | Free-form caption emotion accuracy |

## Data

| Source | Subjects | Stim | Rating | 상태 |
|--------|----------|------|--------|------|
| Horikawa naturalistic video fMRI | 5 | 2185 | Cowen 34-cat + 14-dim + V/A continuous | 사용 중 |
| Qwen-VL caption embeddings | n/a | 2185 | n/a | 추출 완료 |
| Video features (CLIP, DINOv2, VideoMAE, V-JEPA2) | n/a | 2185 | n/a | 추출 완료 (EmoViS symlink) |
| Emo-FilM, StudyForrest, CineBrain, Affective Videos | future | future | future | cross-dataset 확장 후보 |

## Repository layout (2026-06-08 reorganized)

```
FEELIN/
├── project/                ← 모든 분석 활동
│   ├── dir1_brainvlm/{code,data,output,results}/   ← Direction 1 self-contained
│   ├── dir2_multimodal/{code,data,output,results}/ ← Direction 2 self-contained
│   │   └── code/legacy_phase2/   (v4 Brain+Video framework, Direction 2 reuse base)
│   └── shared/{code,data,output,results}/   ← 두 direction 공유 (BFM embedding, Horikawa splits, background 결과 등)
├── external/               ← vendored repos + checkpoints/ (pretrained model weight, 이전 baseline/)
├── docs/
│   ├── masterplan_v3_emobrain.md  (forward plan)
│   ├── notes/                     (decision log)
│   ├── reports/                   (Phase 1 audit PDF)
│   ├── reference/                 (외부 paper PDF)
│   ├── templates/                 (.md 작성 템플릿)
│   ├── workflows/                 (작업 가이드)
│   └── figures/                   (architecture 그림 등)
├── Paper/                  ← paper draft workspace (framework_EN/KR, methodology)
├── archive/                ← v4 framing + legacy_archive + weekly + v4_results 통합
├── tools/                  ← project-wide maintenance utility (build_status, check_md, scientist_ai)
└── 7 root .md
```

### Code 위치 quick reference

- 두 direction 공유. `project/shared/code/probes/` (frozen feature probe), `project/shared/code/bfm_embeddings/` (BFM 추출), `project/shared/code/ssl_pretrain/`, `project/shared/code/analysis/`, `project/shared/code/tools/`.
- Direction 1 specific. `project/dir1_brainvlm/code/` (BrainVLM scaffolding 예정).
- Direction 2 specific. `project/dir2_multimodal/code/` (alignment + variance partitioning scaffolding 예정) + `code/legacy_phase2/` (v4 reference).

## 환경

- **Compute**. NERSC Perlmutter m4641 account. CPU queue (probe), GPU queue (BrainVLM LoRA fine-tune).
- **Python env**. `/pscratch/sd/s/sjmoon/tribev2/.venv` (probe + 일반 분석). `/pscratch/sd/s/sjmoon/brainvlm_qwen_env` (Direction 1 BrainVLM).
- **Pretrained checkpoint paths**. UMBRELLA_qwen ABCD-pretrained checkpoint, Brain-JEPA jepa-ep300.pth, V-JEPA2 (EmoViS 추출).

## Operating Rules (CLAUDE.md 와 일관)

- Root .md 파일은 7 개 유지 (README, README_KR, CONTEXT_FEEL, ONBOARDING, CLAUDE, CODEX, ACTION_PLAN).
- Forward plan / phase report 는 `docs/` 와 `docs/reports/` 에만 추가.
- Narrative 는 `Paper/framework_EN.md`, `framework_KR.md`.
- Methodology 는 `Paper/methodology.md`.
- Decision log 는 `docs/notes/project_decisions.md`.
- Sbatch 명령은 사용자 사전 승인 후 실행 ([[feedback-slurm-submit-permission]]).
- 모든 .py 는 .sh 동반 ([[feedback-always-make-sh]]).
- Bash 명령은 절대경로 ([[feedback-bash-absolute-path]]).

## Go-to docs

- 결과 정합성 + Phase 1 audit. `docs/reports/phase1_audit_20260604/`
- Phase 1 method + result PDF. `docs/reports/phase1_audit_20260604/_pdf/main.pdf`
- Forward plan. `docs/masterplan_v3_emobrain.md`
- Decision log. `docs/notes/project_decisions.md`
- Action plan. `ACTION_PLAN.md` (root)
