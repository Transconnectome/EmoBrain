# EmoBrain Onboarding

새 협업자 또는 AI agent 가 처음 읽을 파일. EmoBrain 의 현재 framing (single project + 5 novelty, 2026-06-29 pivot) 과 읽을 순서를 정리.

## 프로젝트 정체성

**Title.** *EmoBrain. Decoding fine-grained emotion from human brain activity.*

**Spine.** 한 paper, 한 model. Multi-modal LLM (brain + video + caption) 을 single forward pass 에서 통합 fusion, modular brain encoder 로 backbone 의 fair ablation, 4-stage curriculum 으로 Cowen-Keltner 34-category distribution + V/A continuous 의 fine-grained output.

**Core novelty.** Framework 자체 (multi-modal LLM fusion + modular brain encoder + 34-distribution curriculum) 와 "emotion 은 high-dimensional 이다" 라는 output 형태. "어떤 encoder 가 제일 좋은가" 가 spine 이 아님.

**5 Novelty.**

| ID | Name | 한 줄 |
|----|------|-------|
| **NV0** | LLM-based brain emotion decoder | Emotion 분야 LLM 통합 fine-grained brain decoder 의 first instrument |
| **NV1** | 3-modality LLM fusion | brain + video + caption 을 single LLM forward 의 token sequence 로 통합 |
| **NV2** | MindCaptioning bridge | Human-written neutral caption (MindCaptioning, Horikawa) 의 brain-context bridge |
| **NV3** | Modular brain encoder | raw ROI / Ridge / BFM / VLM-derived brain token 의 swappable adapter |
| **NV4** | 34-distribution curriculum | top-1 → top-2 → top-k → full 34D KL 의 4 stage |

NV0 가 spine 의 framing axis, NV1-NV4 가 architectural component.

## 이전 framing 의 archive

- **v3** (2026-05-27, individual difference). `archive/v4_20260602/`.
- **v4** (2026-06-02, universal emotion code, FEEL). `archive/v4_20260602/`.
- **v5** (2026-06-08~06-28, Three Directions. D1 BrainVLM + D2 fMRI-LM + D3 CCN). `archive/v5_direction_split_20260628/`.

Three Directions framing 은 폐기. D1/D2/D3 split 이 아닌 single unified pipeline.

## 환경 + clone

```bash
git clone --recursive git@github.com:Transconnectome/EmoBrain.git
# 이미 clone 했다면
cd EmoBrain && git submodule update --init --recursive
```

| 항목 | 위치 |
|------|------|
| Python (probe, 분석) | `/pscratch/sd/s/sjmoon/tribev2/.venv` |
| Python (LLM fusion, LoRA) | `/pscratch/sd/s/sjmoon/brainvlm_qwen_env` |
| Compute | NERSC m4641 (cpu queue, gpu queue A100 80GB) |
| Submodule. BrainVLM reference | `external/repos/BrainVLM` |
| Submodule. fMRI-LM reference | `external/repos/fMRI-LM` |

## 읽을 순서

1. **README.md / README_KR.md** — 프로젝트 한눈에 (5 NV + architecture + directory).
2. **CONTEXT_EMOBRAIN.md** — Compact single-source-of-truth. agent 가 빠르게 reference.
3. **Paper/framework_EN.md, framework_KR.md** — Canonical narrative (spine + 4 sub-question + 5 NV + evaluation framework + sub-claim + risk).
4. **docs/notes/implementation_spec_20260702.md** — **Code 구현 명세**. Claude Code 대상, DECIDED / OPEN / CAUTION, Acceptance 기준, config schema, repo layout, 34개 감정 순서. Code 시작 시 canonical spec.
5. **docs/notes/architecture_design_20260629.md** — Architecture design 의 상세 spec (NV ↔ component 매핑, token budget, 4 stage curriculum, Stage 0 noise ceiling gate, training paradigm, pre-registered success criterion, open question).
6. **docs/notes/redteam_review_20260630.md** — 4-panel red-team 의 comprehensive synthesis (Architecture / Training stability / Inference paradigm / RoPE position-shift, 7 blocker, 12 redesign recommendation). Read 필수 (training start 전 gate).
7. **docs/notes/ppt_outline_20260630.md** — 21-slide presentation outline.
8. **docs/notes/project_decisions.md** — Chronological decision log (2026-06-29 pivot + 2026-06-30 NV3 framework lock + 2026-07-02 implementation_spec 반영 포함).
9. **ACTION_PLAN.md** — Ground-level S7-S11 build phase (12-16 주).
10. **CLAUDE.md** — Operating rule + scientific rule + Implementation CAUTION (claim/result 분리, baseline 의무, softmax 금지 등).
11. **docs/reports/phase1_audit_20260604/** — Phase 1 background benchmark (frozen BFM 한계 audit + PDF report).

## Directory structure

```
EmoBrain/
├── project/
│   ├── shared/                        (공통 data + baseline)
│   │   ├── code/{probes,bfm_embeddings,ssl_pretrain,analysis,tools}/
│   │   ├── data/                      (Horikawa splits, target matrices, ROI csv)
│   │   ├── output/                    (BFM embeddings, logs)
│   │   └── results/background/        (baseline CSV, figure)
│   ├── code/                          (main code, single pipeline)
│   │   ├── adapters/                  (brain ↔ LLM, video ↔ LLM token adapter)
│   │   ├── brain_encoder/             (raw ROI / Ridge / BFM / VLM 의 4 modular)
│   │   ├── vision_encoder/            (CLIP / V-JEPA2 / VideoMAE selectable)
│   │   ├── caption_loader/            (MindCaptioning human + Qwen-VL generated)
│   │   ├── fusion/                    (multi-modal token assembler + LLM wrapper)
│   │   ├── training/                  (4 stage curriculum trainer, distillation)
│   │   └── evaluation/                (variance partitioning + ceiling + dissociation)
│   ├── config/                        (YAML hyperparam, model registry)
│   ├── sample_scripts/                (SLURM .sh)
│   └── output/                        (training log, checkpoint, prediction)
├── archive/                           (이전 framing 보존)
│   ├── v4_20260602/                   (v3, v4)
│   └── v5_direction_split_20260628/   (D1/D2/D3 split)
├── external/                          (vendored repos + pretrained checkpoint)
├── docs/                              (note + report + reference)
├── Paper/                             (framework_EN/KR, methodology)
├── tools/
└── 7 root .md (README, README_KR, CONTEXT_EMOBRAIN, ONBOARDING, CLAUDE, CODEX, ACTION_PLAN)
```

## 새 파일 추가 전 체크

1. Root .md 는 7 개 (README, README_KR, CONTEXT_EMOBRAIN, ONBOARDING, CLAUDE, CODEX, ACTION_PLAN) 만. 새로 추가 금지.
2. Forward plan / phase report 는 `docs/` 와 `docs/reports/` 에만.
3. Narrative 는 `Paper/framework_{EN,KR}.md`.
4. Methodology 는 `Paper/methodology.md`.
5. Decision log 는 `docs/notes/project_decisions.md` (chronological, 가장 최신 위).
6. 실험 코드는 `project/code/{adapters,brain_encoder,vision_encoder,caption_loader,fusion,training,evaluation}/` (main) 또는 `project/shared/code/` (공통).
7. 검증.
   ```bash
   python3 tools/check_md_completeness.py
   python3 tools/build_project_status.py
   ```

## 주요 workflow

| 의도 | Workflow |
|---|---|
| 새 논문 / 데이터셋 찾기 | `docs/workflows/literature_sota_workflow.md` |
| 아이디어를 실험으로 | `docs/workflows/experiment_planning_workflow.md` |
| 전략 / 모델 주장 stress-test | `docs/workflows/red_blue_team_review.md` |
| 진척도 정리 | `docs/workflows/weekly_update_workflow.md` |

## 현재 진행 상황 (2026-06-30 기준)

- **Framework lock.** 5 NV framework 확정 (2026-06-29 pivot). NV3 modular brain encoder 의 P2-B knowledge distillation 을 main training paradigm 으로 lock (2026-06-30).
- **Track B scope 확정 (2026-07-03).** Track B (distillation) 은 Track A best encoder 1 개 만. E1-E4 각각 Track B 안 함. Framework 검증 primary question = "context lift" (Track A best A4 → Track B best B4 delta).
- **Red-team review 완료.** 4-panel adversarial review (Architecture / Training stability / Inference paradigm / RoPE position-shift) 로 7 blocker + 12 redesign recommendation 확정. `docs/notes/redteam_review_20260630.md`.
- **Week 0 engineering sprint 대기.** Training start 전 gate. 7 blocker resolve, Stage 0 noise ceiling 측정, factored 3-phase sweep (30 run) 준비.
- **Background (Phase 1) 완료.** Frozen BFM (Brain-JEPA, NeuroSTORM, SwiFT 6 변종) 가 ROI ridge baseline 못 넘음을 audit 으로 확정. `docs/reports/phase1_audit_20260604/`.
- **Datasets.** Horikawa (5 subj × 2185 stim, pooled) 사용 중. Emo-FilM cross-cohort 후보 (다운로드 예정).
- **Sbatch training on hold.** Week 0 sprint 완료 + 사용자 사전 승인 후 launch.

## Operating rules (요약)

- 모든 .py 는 .sh 동반.
- Bash 명령은 절대경로. cd + relative 금지.
- Sbatch 는 사용자 사전 승인 필수.
- 결과 reporting 은 standard baseline suite (chance / ROI Ridge / BFM frozen reference / Video baseline) 와 함께.
- 응답 언어 한국어 (기술적 고유명사 영어 유지 가능).
- Em dash 사용 금지, 학술 산문 에서 colon 회피.

자세한 내용은 `CLAUDE.md`.
