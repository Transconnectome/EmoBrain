# EmoBrain `project/` Quick Reference

EmoBrain 의 active 분석 work 가 모두 모이는 폴더. Single unified pipeline (5 novelty framework, 2026-06-29 pivot) 의 entry point 와 공통 자원 정리.

Spine narrative 는 `../Paper/framework_EN.md`, `../Paper/framework_KR.md`.
Architecture spec 은 `../docs/notes/architecture_design_20260629.md`.
Ground-level weekly action 은 `../ACTION_PLAN.md`.
Red-team synthesis 는 `../docs/notes/redteam_review_20260630.md`.

## 1. Framing at a glance

**Single project.** Multi-modal LLM (brain + video + caption) 을 single forward pass 에서 통합 fusion, modular brain encoder (raw ROI / Ridge / BFM / VLM) 로 backbone 의 fair ablation, 4-stage curriculum (top-1 → top-2 → top-k → full 34D KL) 으로 Cowen-Keltner 34-category distribution + V/A continuous fine-grained output.

**5 Novelty.**

| ID | Name | 한 줄 |
|----|------|-------|
| NV0 | LLM-based brain emotion decoder | Emotion 분야 LLM 통합 fine-grained brain decoder 의 first instrument |
| NV1 | 3-modality LLM fusion | brain + video + caption 을 single LLM forward 의 token sequence 로 통합 |
| NV2 | MindCaptioning bridge | Human-written neutral caption (MindCaptioning, Horikawa) 의 brain-context bridge |
| NV3 | Modular brain encoder | raw ROI / Ridge / BFM / VLM 의 swappable adapter |
| NV4 | 34-distribution curriculum | top-1 → top-2 → top-k → full 34D KL 의 4 stage |

이전 Three Directions (D1 BrainVLM + D2 fMRI-LM + D3 CCN, 2026-06-08~06-28) framing 은 폐기. `../archive/v5_direction_split_20260628/` 에 보존.

## 2. Directory 구조 (project/)

```
project/
├── shared/                           (공통 자원)
│   ├── code/
│   │   ├── probes/                   (Ridge / linear probe, baseline)
│   │   ├── bfm_embeddings/           (Brain-JEPA / NeuroSTORM / SwiFT embedding 추출)
│   │   ├── ssl_pretrain/             (self-supervised pretrain wrapper)
│   │   ├── analysis/                 (variance partitioning, RSA, dissociation)
│   │   └── tools/                    (data build, va_quartile_split 등)
│   ├── data/                         (splits, target matrix, ROI csv, stimulus feature)
│   │   ├── horikawa_5fold.csv
│   │   ├── horikawa_split.csv
│   │   ├── cowen_horikawa_labels.csv
│   │   └── stimulus_features/        (Qwen-VL caption, V-JEPA2/CLIP/DINOv2/VideoMAE)
│   ├── output/
│   │   ├── embeddings/               (BFM hidden state, Brain-JEPA 5subj × 10cell, NS, SwiFT 6 변종)
│   │   ├── logs/                     (baseline run log)
│   │   └── slurm/                    (SLURM 출력)
│   └── results/
│       └── background/               (Phase 1 baseline CSV, figure)
├── code/                             (main unified pipeline, single project)
│   ├── adapters/                     (brain ↔ LLM token, video ↔ LLM token)
│   ├── brain_encoder/                (raw_roi / ridge_embedding / bfm / vlm 의 4 modular NV3)
│   ├── vision_encoder/               (clip / vjepa2 / videomae selectable)
│   ├── caption_loader/               (mindcaptioning human + qwen_vl generated NV2)
│   ├── fusion/                       (token_assembler + llm_wrapper Qwen3-VL + poyo_alt + dist_head)
│   ├── training/                     (dataset + trainer 4 stage curriculum + smoke)
│   └── evaluation/                   (variance partitioning + ceiling + dissociation + LOSO + cross-cohort)
├── config/                           (YAML hyperparam, dataset.yaml, train_curriculum.yaml, model registry)
├── sample_scripts/                   (SLURM .sh entry point)
└── output/                           (training log, checkpoint, prediction)
```

`code/` 하위 7 개 subdir 는 skeleton 만 생성 됨 (2026-06-29). 실제 implementation 은 S7 부터 (`../ACTION_PLAN.md`).

## 3. Architecture (요약)

```
INPUT
  fMRI (5 subj × 2185 stim pooled)
      → Brain encoder (modular. raw ROI / Ridge / BFM / VLM)         → brain tokens
  Video (Horikawa silent clip)
      → Vision encoder (CLIP / V-JEPA2 / VideoMAE selectable)        → video tokens
  Caption (MindCaptioning human + Qwen-VL generated)
      → text encoder (LLM tokenizer)                                  → text tokens
  Prompt (task-specific instruction + 34-cat label inventory)
      → instruction tokens

FUSION
  [brain | video | text | instruction] tokens
      → Qwen3-VL LLM (LoRA fine-tune, main)
      또는 POYO 형 sequence model (ablation)
      → fused hidden state

OUTPUT (NV4. 34D independent emotion regression + curriculum)
  34-D linear regression head. Softmax / sum-to-1 / KL 금지.
  각 감정 은 독립 점수 (bittersweet 예). Preprocess = z-score per emotion.
  Curriculum (subset per-emotion MSE, stage 별 target 만 다름).
    1 top-1     A = {자극 별 rating 1위}
    2 top-2     A = {상위 2}
    3 top-k     A = {rating > threshold}
    4 full 34D  A = {1..34}
  Loss (Track A direct)     L_main = sum_{k ∈ A} (pred_k - target_k)^2
  Loss (Track B distill)    L_total = L_main + λ × L_distill (teacher 34D MSE 재현)
```

상세 spec 은 `../docs/notes/architecture_design_20260629.md`.

## 4. 데이터 schema

### 4.1 shared/data/ (present, 2026-06-30 기준)

실제 존재 하는 파일.

- `horikawa_5fold.csv` — per-stim 5 fold split.
- `horikawa_split.csv` — canonical train/val/test split.
- `cowen_horikawa_labels.csv` — Cowen 34 rating (Horikawa 매칭). Raw 1-9 Likert, z-score 전처리 필요 (S7 에서 fit).
- `horikawa_L0_V_binary_subset.csv` — Phase 1 valence Q1 vs Q4 binary subset.
- `horikawa_L0_A_binary_subset.csv` — Phase 1 arousal Q1 vs Q4 binary subset.
- `feelin_canonical_stimuli.csv` — canonical stimulus index (FEELIN v3 시절 유지, 2185 stim reference).
- `stimulus_features/captions.json` — per-stim 자연어 (우리 generated Qwen-VL, S7 에 verify 예정).
- `stimulus_features/caption_embed.npy` — caption embedding.
- `stimulus_features/stim_idx.npy` — stim index alignment.
- `stimulus_features/{clip,vjepa2,dinov2,videomae}_{pretrained,scratch}.npy` — video embedding 8 종.

### 4.2 shared/data/ (S7 생성 예정)

Framework 가 요구 하지만 아직 파일 없는 것.

- `roi_timeseries_schaefer400tian50/sub-XX_<stim>.npy` — (T, 450) ROI mean time series. Raw fMRI → ROI 추출 pipeline 필요 (S7.2 참조).
- `cowen34_zscored/` — z-scored 34D target (per-emotion mean/std fit on training set, apply on test). `project/code/training/preprocess.py` 로 생성 (S7 or S8.2).
- `va_continuous_z.csv` — per-stim `valence_z`, `arousal_z` + quartile 컬럼. `shared/code/tools/va_quartile_split.py` 로 생성.
- `cat34_soft_distribution.csv` — 이전 formulation (sum=1 soft distribution) 은 폐기 (NV4 재정의). Raw independent scores 는 `cowen_horikawa_labels.csv` 에서 z-score 후 사용.

### 4.3 shared/output/embeddings/ (partial present)

- Brain-JEPA (BJ) resting / scratch, NeuroSTORM (NS), SwiFT 6 변종. Frozen probe baseline 자원.
- `shared/output/embeddings/` 하위 실제 구조 는 `ls shared/output/embeddings/` 로 확인.

### 4.4 MindCaptioning caption (NV2 main bridge, S7 fetch 예정)

- 위치 TBD (S7 에서 fetch). Human-written neutral caption, Horikawa stim 매칭. OpenNeuro ds005191 + figshare 에서 fetch. Framework spine 의 NV2 main source.

## 5. Task 목록

| Task | 종류 | Label 정의 | Loss | Metric |
|------|------|------------|------|--------|
| V_reg | regression | `valence_z` continuous | MSE | Pearson r, MAE |
| A_reg | regression | `arousal_z` continuous | MSE | Pearson r, MAE |
| V_binary (Q1 vs Q4) | binary | `valence_quartile` in {Q1, Q4} (OTHER masked) | BCE (masked) | AUROC, balanced acc |
| A_binary (Q1 vs Q4) | binary | `arousal_quartile` in {Q1, Q4} (OTHER masked) | BCE (masked) | AUROC, balanced acc |
| Cat34_multilabel | multilabel | `cat34_soft >= 0.10` (Stage 2/3) | BCE / k-hot CE | macro AUROC |
| Cat34_soft | distribution | `cat34_soft` (sum=1, Stage 4) | KL divergence | mean Pearson r, top1 acc |
| Cat34_top1 | 34-class | `argmax(cat34_soft)` (Stage 1) | CE + class weighting | top1 acc, macro F1 |

Phase 1 의 4 task (V/A binary + V/A reg + Cat34 multilabel + Cat34 soft) 와 정의 일관. Curriculum 의 stage 별 loss 는 `../docs/notes/architecture_design_20260629.md` §4-stage curriculum.

## 6. 환경

| 자원 | 위치 | 용도 |
|------|------|------|
| Python (general) | `/pscratch/sd/s/sjmoon/tribev2/.venv` | probe, baseline, dataset adapter, evaluation |
| Python (LLM) | `/pscratch/sd/s/sjmoon/brainvlm_qwen_env` | Qwen3-VL LoRA, fusion training |
| Submodule (VLM reference) | `../external/repos/BrainVLM/` | UMBRELLA_qwen 의 patch_embed + merger 참조 (NV3 의 VLM-derived encoder) |
| Submodule (fMRI LLM reference) | `../external/repos/fMRI-LM/` | Wei 2026 tokenizer + LLM tuning 참조 |
| Compute | NERSC m4641 (cpu / gpu queue) | A100 80GB |

## 7. 협업자 onboarding

Clone.
```bash
git clone --recursive git@github.com:Transconnectome/EmoBrain.git
cd EmoBrain && git submodule update --init --recursive
```

읽을 순서.
1. `../README.md` / `../README_KR.md` — 5 NV + architecture.
2. `../CONTEXT_EMOBRAIN.md` — compact single-source-of-truth.
3. `../Paper/framework_EN.md` + `framework_KR.md` — spine narrative.
4. `../docs/notes/architecture_design_20260629.md` — architecture spec.
5. `../docs/notes/redteam_review_20260630.md` — 4 panel red-team 의 7 blocker + 12 recommendation (training start 전 gate).
6. `../ACTION_PLAN.md` — S7-S11 weekly action.
7. `../CLAUDE.md` — operating + scientific rule.

## 8. 운영 규칙

- 모든 .py 는 .sh 동반 (NERSC sbatch 진입점).
- Bash 명령은 절대경로. cd + relative 금지.
- Sbatch 는 사용자 사전 승인 필수.
- 결과 / output / checkpoint 는 `project/output/` (main pipeline) 또는 `project/shared/` (공통).
- 추출된 raw data / checkpoint / output 덮어쓰지 않음.
- 모든 main claim 은 standard baseline suite (chance / ROI Ridge / BFM frozen reference / Video baseline) + noise ceiling anchor 와 함께 reporting.

## 9. Status (2026-06-30)

- Framework lock (2026-06-29 pivot). NV3 P2-B knowledge distillation main paradigm (2026-06-30).
- Red-team 완료. 4 panel, 7 blocker, 12 recommendation. `../docs/notes/redteam_review_20260630.md`.
- Week 0 engineering sprint 대기 (training start 전 gate). Stage 0 noise ceiling 측정, factored 3-phase sweep (30 run) 준비.
- Sbatch training on hold. Week 0 완료 + 사용자 승인 후 launch.
- Background Phase 1 완료. Frozen BFM 한계 확정. `../docs/reports/phase1_audit_20260604/`.
- `project/code/{adapters,brain_encoder,vision_encoder,caption_loader,fusion,training,evaluation}/` skeleton 만 존재. Implementation S7 부터.
