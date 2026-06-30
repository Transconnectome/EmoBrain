# EmoBrain Action Plan

한 paper. Spine = framework novelty path (NV0-NV4).

이 문서는 ground-level weekly action.
High-level (spine, 5 novelty, architecture) 는 `README.md`, `README_KR.md`, `CONTEXT_EMOBRAIN.md`.
Spine narrative 는 `Paper/framework_EN.md` + `framework_KR.md`.
Architecture spec 은 `docs/notes/architecture_design_20260629.md`.
Chronological decision log 는 `docs/notes/project_decisions.md`.

## 한 줄 요약

12-16 주 build phase (S7-S11). brain + video + caption 의 multi-modal LLM fusion + 34-distribution 4-stage curriculum 의 구축.

## 자원 환경

| 자원 | 위치 | 용도 |
|------|------|------|
| Perlmutter GPU | NERSC m4641 (gpu queue, A100 80GB) | LLM fusion training, LoRA, vision encoder fine-tune |
| Perlmutter CPU | NERSC m4641 (cpu queue) | Probe, baseline ladder, post-hoc analysis |
| Python env (general) | `/pscratch/sd/s/sjmoon/tribev2/.venv` | Probe, evaluation, dataset 통합 |
| Python env (LLM) | `/pscratch/sd/s/sjmoon/brainvlm_qwen_env` | Qwen3-VL fine-tune, LoRA |
| Data (Horikawa) | `/pscratch/sd/s/sjmoon/EmoBrain/project/shared/data/` | Splits, target matrix, ROI csv |
| Data (Emo-FilM) | 다운로드 예정 | Cross-cohort 평가 (S11) |
| BFM embeddings | `/pscratch/sd/s/sjmoon/EmoBrain/project/shared/output/embeddings/` | BJ resting/scratch, NS, SwiFT 6 변종 |
| MindCaptioning caption | TBD (S7 에서 fetch) | NV2 main bridge source |
| 우리 generated caption | `/pscratch/sd/s/sjmoon/EmoBrain/project/shared/data/captions/qwen_vl/` | NV2 비교 자원 |
| Results | `/pscratch/sd/s/sjmoon/EmoBrain/project/output/` | per-stage CSV, figure |

모든 .py 는 .sh 동반. Bash 명령은 절대경로. Sbatch 제출 전 사용자 확인.

---

## 12-16 week Build Phase (S7-S11)

5 novelty (NV0-NV4) 의 architectural component 구축 + 학습 + 평가 + paper draft.

### S7. 3-modality adapter + dataset 통합 (week 1-3)

**Goal**. brain + video frame + caption (MindCaptioning human + 우리 generated) 의 unified dataset. 각 modality 의 token adapter scaffolding.

#### S7.1. Caption source 정리
- [ ] MindCaptioning human-written caption 의 fetch (Horikawa stim 매칭 verify, `project/shared/data/captions/mindcaptioning/`).
- [ ] 우리 generated caption (Qwen-VL) 의 batch 확인 + missing 자극 fill.
- [ ] Caption 형식 통일 (token length, prompt format).

#### S7.2. Brain encoder adapter (NV3)
- [ ] `project/code/brain_encoder/raw_roi.py`. 5 subj × 2185 stim × ROI mean tensor → brain token.
- [ ] `project/code/brain_encoder/ridge_embedding.py`. ROI ridge prediction 의 latent 활용.
- [ ] `project/code/brain_encoder/bfm.py`. BJ resting / scratch, NS, SwiFT 6 변종 embedding loader.
- [ ] `project/code/brain_encoder/vlm.py`. VLM-derived brain token wrapper.
- [ ] `project/code/adapters/brain_to_llm.py`. 4 encoder 모두 동일 token shape 으로 변환.

#### S7.3. Vision encoder selectable
- [ ] `project/code/vision_encoder/clip.py`, `vjepa2.py`, `videomae.py`. 동일 interface 로 frame → token.
- [ ] `project/code/adapters/video_to_llm.py`. video token → LLM 입력 형식.

#### S7.4. Caption loader (NV2)
- [ ] `project/code/caption_loader/mindcaptioning.py`. human caption loader.
- [ ] `project/code/caption_loader/generated.py`. 우리 generated loader.
- [ ] 두 source 동시 활용 의 batch 구성 strategy.

#### S7.5. Unified dataset
- [ ] `project/code/training/dataset.py`. brain + video + caption + label 의 4-tuple dataset (5 subj × 2185 stim pooled).
- [ ] Stim level stratified split (8 fold).
- [ ] `project/config/dataset.yaml`. modality on/off switch + encoder selection.

### S8. Multi-modal LLM fusion + trainer (week 4-6)

**Goal**. NV1 (3-modality LLM fusion) + NV4 (4-stage curriculum) 의 main model + trainer.

#### S8.1. Fusion module
- [ ] `project/code/fusion/token_assembler.py`. [brain | video | text | instruction] token sequence 의 ordered concat + attention mask.
- [ ] `project/code/fusion/llm_wrapper.py`. Qwen3-VL backbone + LoRA hook. main backbone.
- [ ] `project/code/fusion/poyo_alt.py`. POYO 형 sequence model. ablation.

#### S8.2. 34-distribution head (NV4)
- [ ] `project/code/fusion/dist_head.py`. LLM hidden → 34D distribution head (softmax for stage 1-3, soft target for stage 4).
- [ ] Class weighting (Cowen 34 의 imbalance, top-1 frequency 기반).

#### S8.3. Trainer (4 stage curriculum)
- [ ] `project/code/training/trainer.py`. unified trainer. stage 별 loss / scheduler / metric switch.
- [ ] Stage 1. top-1 CE. baseline 형성.
- [ ] Stage 2. top-2 multi-label CE. label sparsity.
- [ ] Stage 3. top-k k-hot CE. (k = 자극별 active category 수, threshold 0.10).
- [ ] Stage 4. full 34D KL with rater empirical distribution target.
- [ ] Optional auxiliary loss. LLM hidden → ROI mean reconstruction (NV3 의 brain modality 의 representational anchor).

#### S8.4. Config + smoke harness
- [ ] `project/config/train_curriculum.yaml`. 4 stage 의 LR / epoch / batch / scheduler / class weight.
- [ ] `project/code/training/smoke.py`. 100 trial subset 의 4 stage smoke run.

### S9. SMOKE test + 사용자 launch (week 7)

**Goal**. 100 trial × 1 epoch smoke 가 학습 곡선 + memory profile + token budget 확인.

- [ ] Smoke run (CPU, 100 trial). NaN / shape / loss decrease.
- [ ] GPU 1 epoch (5 subj × 100 stim subset, A100). memory + step time + token attention budget.
- [ ] **사용자 confirm 후 full launch** (모든 sbatch 명령 절대경로).

### S10. 4 stage curriculum 학습 (week 8-12)

**Goal**. 5 subj × 2185 stim pooled 에서 4 stage 순차 학습. brain encoder 4 변종 × vision encoder 3 변종 × caption source 2 (MindCaptioning vs 우리) 의 modular ablation.

- [ ] Stage 1 학습 (top-1). 1-2 주 (각 backbone × 각 encoder combination).
- [ ] Stage 2 학습 (top-2). 1 주.
- [ ] Stage 3 학습 (top-k). 1 주.
- [ ] Stage 4 학습 (full 34D KL). 1-2 주.
- [ ] Ablation grid. (brain encoder 4) × (vision encoder 3) × (caption source 2). 24 condition (sparse, top combination 만 학습).
- [ ] Checkpoint save 정책 (best per metric + last per stage).

### S11. Evaluation + paper draft (week 13-16)

**Goal**. variance partitioning + ceiling anchor + dissociation + LOSO + cross-cohort 의 full evaluation suite + paper draft.

#### S11.1. Baseline ladder
- [ ] Chance baseline (label permutation).
- [ ] ROI mean + Ridge baseline.
- [ ] Best BFM frozen probe.
- [ ] Video-only baseline (vision encoder + classifier head, brain 제외).
- [ ] Caption-only baseline (text-only LLM, brain + video 제외).
- [ ] Full multi-modal (brain + video + caption).

#### S11.2. Variance partitioning
- [ ] Brain-only / Video-only / Caption-only / Brain+Video / Brain+Caption / Video+Caption / Full 의 7 condition.
- [ ] Unique vs shared vs joint variance 의 emotion task 별 decomposition.
- [ ] N=5 subject 의 statistical power limit 명시.

#### S11.3. Ceiling anchor
- [ ] Inter-rater agreement (Cowen 34 의 rater split).
- [ ] Inter-subject brain similarity (RSA).
- [ ] Model performance 의 ceiling 대비 비율 reporting.

#### S11.4. Dissociation
- [ ] Decoding vs structural similarity (RSA) 의 dissociation.
- [ ] Visual-confound vs emotion-specific variance 의 분리.

#### S11.5. LOSO + cross-cohort
- [ ] LOSO (5-fold by subject). zero-shot transfer.
- [ ] Cross-cohort (Horikawa → Emo-FilM). 다운로드 + preprocessing 의 prerequisite.

#### S11.6. Paper draft
- [ ] Section 1. Intro + 5 NV 의 contribution box.
- [ ] Section 2. Related work (LLM-based brain decoding, MindCaptioning, BFM survey, multimodal alignment).
- [ ] Section 3. Method (architecture + 4 stage curriculum).
- [ ] Section 4. Modular brain encoder ablation.
- [ ] Section 5. Main result (full multi-modal vs baseline ladder).
- [ ] Section 6. Analysis (variance partitioning, ceiling, dissociation, LOSO, cross-cohort).
- [ ] Section 7. Discussion + limitation + future work.
- [ ] Submission venue 결정.

---

## Open decisions

상세 list 는 `docs/notes/architecture_design_20260629.md` 의 §Open Implementation Questions 와 `Paper/framework_EN.md` 의 §Open Decisions. 본 ACTION_PLAN 의 timeline 에 영향 큰 항목.

- ~~OD-A.~~ **[2026-06-29 RESOLVED]** Backbone size = **Qwen3-VL 2B + 4B 둘 다** ablation. 8B 보류.
- OD-B. POYO ablation 의 priority (S8 main 에 포함 vs supplementary).
- OD-C. Cross-cohort (Emo-FilM) 의 inclusion 시점.
- ~~OD-D.~~ **[2026-06-29 RESOLVED]** Caption source = **(a) MindCaptioning only + (b) MindCaptioning + 우리 generated dual** 둘 다 ablation.
- OD-E. Stage 4 의 KL target distribution 의 smoothing (Dirichlet prior 적용 여부).
- OD-F. Hackathon 5 일 path 의 별도 진행 여부 (현 build phase 와 분리).
- **OD-G [NEW].** Q3 의 video frame temporal alignment (uniform sample vs HRF-aligned). 미정 (S7 시작 전 결정).

---

## Pointer

- Spine narrative. `Paper/framework_EN.md` + `Paper/framework_KR.md`.
- Architecture spec. `docs/notes/architecture_design_20260629.md`.
- Chronological decision. `docs/notes/project_decisions.md`.
