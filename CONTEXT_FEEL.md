# EmoBrain Compact Context

Agent / 협업자가 빠르게 참조할 single source of truth. 자세한 내용은 각 reference 파일.

## 정체성

**EmoBrain** = Active brain decoding for emotion. **Three Directions** (D1 BrainVLM + D2 fMRI-LM main paper; D3 CCN 별도 발표).
**Branch**. `sj_NEW_20260608_perlmutter`.
**Repo name 보존**. 기존 path `/pscratch/sd/s/sjmoon/EmoBrain/` 그대로 유지.
**이전 framing (v4 universal emotion code)** 은 `archive/v4_20260602/` 에 보존.

## Three Directions

| Direction | 핵심 method | 주요 reference |
|-----------|--------------|----------------|
| **D1. BrainVLM** | Qwen3-VL backbone + fMRI 2D ROI patchify + LoRA fine-tune. emotion VQA / V/A / Cat34 distribution 자연어 + numeric 출력. | MindLLM 2025, UMBRAE 2024, Mind Captioning 2025, MedBLIP 2023, BLIP-2 2023, LLaVA 2023 |
| **D2. fMRI-LM** | Wei 2026 paper architecture (Brain-JEPA-like tokenizer + GPT-2/Qwen3 LLM + SigLIP + GRL + F2F+F2T+T2T) 차용 후 emotion specific 으로 발전. LLM tokenizer 활용. | fMRI-LM (Wei 2026, arXiv 2511.21760) |
| **D3. CCN. Contextualized representation + 새 task design** (별도 axis) | Video model embedding → learning clustering → context 반영된 clustering → brain 이 그 context 학습. 같은 emotion 안에서 context 별 sub-cluster emergence 검증. | TRIBE 2025, VIBE 2025, CineBrain 2025, Doerig 2024, BraVL 2023 |

D1 + D2 는 main paper. D3 는 CCN workshop 발표 (결과 좋으면 paper 까지).

## 2 × 2 grid (Direction × Dataset, D1+D2)

| | Horikawa | Emo-FilM |
|--|----------|------------|
| **D1. BrainVLM** | pilot 단계 | 다운로드 후 |
| **D2. fMRI-LM** | pilot 단계 | 다운로드 후 |

## Tasks (3 종류)

| 종류 | 설명 | 적용 dataset |
|------|------|----------------|
| **A. 기존 언어 task (공통)** | V/A binary (Q1 vs Q4), V/A regression, categorical classification (threshold 기준 선택) | Horikawa + Emo-FilM 둘 다 |
| **B. 새로운 공통 task (공통)** | independent dataset 에도 적용되는 label 을 어떻게 만들 것인가. clustering 등 design 결정 중. | Horikawa + Emo-FilM 둘 다 |
| **C. 개별 dataset task** | Horikawa = visual feature 위주. Emo-FilM = narratives + temporal dynamics. | dataset 특화 |

**Phase 1 Background benchmark 완료** (Horikawa 만, frozen BFM). V/A binary, V/A reg, Cat34 multilabel (threshold 0.10), Cat34 soft. ROI + chance baseline.

## Phase 1 Background 결과 (Frozen BFM 의 한계)

| Task | Best BFM (BJ resting) | ROI baseline | Chance |
|------|------------------------|--------------|--------|
| V_binary AUROC | 0.738 | **0.789** | 0.500 |
| A_binary AUROC | 0.662 | **0.678** | 0.500 |
| V_reg Pearson r | 0.330 | **0.396** | 0.000 |
| A_reg Pearson r | 0.221 | **0.233** | 0.000 |
| Cat34_multilabel macro AUROC | 0.669 | **0.699** | 0.500 |
| Cat34_soft mean Pearson r | 0.237 | **0.280** | -0.004 |

ROI 가 모든 task 에서 BFM 보다 일관되게 높음. 원인은 Horikawa 자극의 짧은 T 분포 (median 5, 71.6% T=5) + BFM input 의 평균 63-70% zero padding. 이 결과가 D1 + D2 + D3 모두의 motivation.

## Data (2 datasets)

| Source | Subjects | Stim | Rating | 특성 | 상태 |
|--------|----------|------|--------|------|------|
| **Horikawa** naturalistic video fMRI | 5 | 2185 | Cowen 34-cat + 14-dim + V/A continuous | visual feature 위주 | 사용 중 |
| **Emo-FilM** | TBD | TBD | TBD | narratives + temporal dynamics | 다운로드 예정 |

부수 데이터. Qwen-VL caption embedding (Horikawa 2185 자극). V-JEPA2 / CLIP / DINOv2 / VideoMAE pretrained + scratch (Horikawa).

## Repository layout (2026-06-12 updated for 3-direction)

```
EmoBrain/
├── project/                ← 모든 분석 활동
│   ├── dir1_brainvlm/{code,data,output,results,docs}/   ← D1
│   ├── dir2_fmri_lm/{code,data,output,results,docs}/    ← D2 (Wei 2026 architecture)
│   ├── dir3_ccn/                                         ← D3 (이전 CCN_Emotion + alignment_pilot + legacy_phase2)
│   │   ├── code/
│   │   │   ├── alignment_pilot/   (SigLIP + GRL Brain-Video alignment 의 minimal pipeline)
│   │   │   └── legacy_phase2/     (v4 Brain+Video framework reference)
│   │   ├── data/        (1.8G CCN dataset)
│   │   ├── study1/, study2_thesis/   (이전 CCN_Emotion 의 main 연구)
│   │   ├── ccn2026_template/, Paper/, notes/
│   │   └── ...
│   └── shared/{code,data,output,results}/   ← 두 direction 공유 (BFM embedding, Horikawa splits, background 결과 등)
├── external/               ← vendored repos + checkpoints/ (pretrained model weight)
├── docs/
│   ├── masterplan_v3_emobrain.md  (forward plan)
│   ├── notes/                     (decision log)
│   ├── reports/                   (Phase 1 audit PDF)
│   ├── reference/                 (외부 paper PDF, BrainVLM_emotion + Aligning visual representations 등)
│   ├── templates/, workflows/, figures/
├── Paper/                  ← paper draft workspace (framework, methodology)
├── archive/                ← v4 framing + legacy_archive + weekly + v4_results
├── tools/                  ← project-wide maintenance utility
└── 7 root .md
```

### Code 위치 quick reference

- **D1 BrainVLM**. `project/dir1_brainvlm/code/` (scaffolding 예정).
- **D2 fMRI-LM**. `project/dir2_fmri_lm/code/` (scaffolding 예정).
- **D3 CCN**. `project/dir3_ccn/code/alignment_pilot/` (SigLIP + GRL pilot 완료, sbatch 대기) + `code/legacy_phase2/` (v4 reference) + `study1/`, `study2_thesis/` (CCN_Emotion 의 본문 연구).
- **Shared**. `project/shared/code/{probes,bfm_embeddings,ssl_pretrain,analysis,tools}/`.

## 환경

- **Compute**. NERSC Perlmutter m4641. CPU queue (probe), GPU queue (D1 LoRA, D2 LLM tuning).
- **Python env**. `/pscratch/sd/s/sjmoon/tribev2/.venv` (probe + D3 alignment + 일반 분석). `/pscratch/sd/s/sjmoon/brainvlm_qwen_env` (D1, D2 의 LLM 부분).

## Operating Rules

- Root .md 파일은 7 개 유지 (README, README_KR, CONTEXT_FEEL, ONBOARDING, CLAUDE, CODEX, ACTION_PLAN).
- Forward plan / phase report 는 `docs/` 와 `docs/reports/` 에만.
- Narrative 는 `Paper/framework_EN.md`, `framework_KR.md`. Methodology 는 `Paper/methodology.md`.
- Decision log 는 `docs/notes/project_decisions.md`.
- Sbatch 명령은 사용자 사전 승인 후 ([[feedback-slurm-submit-permission]]).
- 모든 .py 는 .sh 동반. Bash 명령은 절대경로.

## Go-to docs

- 결과 정합성 + Phase 1 audit. `docs/reports/phase1_audit_20260604/`
- Phase 1 method + result PDF. `docs/reports/phase1_audit_20260604/_pdf/main.pdf`
- Forward plan. `docs/masterplan_v3_emobrain.md`
- Decision log. `docs/notes/project_decisions.md`
- Action plan. `ACTION_PLAN.md` (root)
