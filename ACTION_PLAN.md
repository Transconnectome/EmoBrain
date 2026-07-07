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

#### S8.2. 34D independent regression head (NV4)
- [ ] `project/code/fusion/regression_head.py`. LLM hidden → 34D linear regression head. Softmax 없음, sum-to-1 없음.
- [ ] `project/code/training/preprocess.py`. Per-emotion z-score fit (training set only) + apply (test set 에 transform 만).
- [ ] Rating raw (1-9) → z-scored target 저장 (`project/shared/data/cowen34_zscored/`).

#### S8.3. Trainer (Track A direct + Track B distillation, 각 track 안 curriculum 1-4)
- [ ] `project/code/training/trainer.py`. Unified trainer.
- [ ] Track A loss = subset per-emotion MSE (stage 별 active target A). Class weighting 없음 (z-score 로 균등 가중).
- [ ] Track B loss = subset per-emotion MSE (Track A 와 동일 stage 별 A) + λ × distillation MSE (teacher 34D 재현). λ grid (0.5 / 1.0 / 2.0).
- [ ] Curriculum sub-stage handler. stage 별 active target set A 계산 (자극 별 top-1 / top-2 / top-k / full 34).
- [ ] Non-active 감정 은 loss 계산 에서 masked (gradient 없음). Prediction head 는 항상 34-dim.
- [ ] Optional auxiliary loss. LLM hidden → ROI mean reconstruction. λ_recon 0.1 (S9 smoke 후 결정).
- [ ] Softmax / sum-to-1 / KL divergence / cross-entropy 사용 금지 (regression head 로 강제).
- [ ] Stage transition. 이전 stage checkpoint 에서 weight load. Head dim 변경 없음.

#### S8.4. Config + smoke harness
- [ ] `project/config/train.yaml`. Track A (direct MSE) + Track B (distillation) × curriculum sub-stage 1-4 의 LR / epoch / batch / scheduler.
- [ ] `project/code/training/smoke.py`. 100 trial subset 의 Track A curriculum A1 (top-1 subset MSE) smoke run.
- [ ] Sanity check. Prediction 이 z-scored 공간 에서 mean 0 근처, std 1 근처 (initialization 후).

### S7.6. Caption neutrality + video-caption overlap 사전 검증

- [ ] `project/shared/code/tools/verify_caption_neutrality.py`. MindCaptioning caption 의 Cowen 34 + V/A vocabulary substring match + 100 개 sample 인간 검토.
- [ ] Caption sample 실제 열람 (100 개 최소). 감정 단어 / 명시적 해석 부여 여부 표본 검증.
- [ ] 우리 generated Qwen-VL caption 도 동일 검증.
- [ ] Video embedding 에서 caption embedding 을 예측 하는 linear regression fit (`shared/code/tools/video_caption_residualize.py`). 잔차 caption 생성.

### S9. SMOKE test + 사용자 launch (week 7)

**Goal**. 100 trial × 1 epoch smoke 가 학습 곡선 + memory profile + token budget 확인.

- [ ] Smoke run (CPU, 100 trial). NaN / shape / loss decrease.
- [ ] GPU 1 epoch (5 subj × 100 stim subset, A100). memory + step time + token attention budget.
- [ ] Projector token count grid smoke (Nb / Nv 각각 8 / 32 / 128 grid). 34D 고차원 구조 보존 vs token cost trade-off.
- [ ] **사용자 confirm 후 full launch** (모든 sbatch 명령 절대경로).

### Stage 0. Noise ceiling estimation (S10 진입 gate)

**Goal**. Encoder competition 이 의미 있는 headroom 위 에서 진행 되는지 pre-check. Case I/II/III 판정.

- [ ] ISC (Inter-Subject Correlation). 5 subj × same stim 의 cross-subject correlation. per ROI per TR.
- [ ] Repeated-trial split-half reliability. Horikawa test set 56 stim × 24 repeat. bootstrap 1000 회.
- [ ] Analytical noise ceiling (Lage-Castellanos 2019). signal / noise variance 분리 estimation.
- [ ] Label crowd split-half reliability (rater-level 데이터 확보 시). Cowen concordance 54% 는 참고 값 (categorical, 직접 ceiling 아님 — 2026-07-07 정정).
- [ ] 4 estimator consensus → noise ceiling lock.
- [ ] gap_filled threshold Case I/II/III boundary final lock. 학습 시작 전 사전 등록.

### S10. Two-stage validation 학습 (week 8-14)

**Goal**. Stage 1 (context 없는 direct 34D supervised) 완료 를 gate 로 삼아 Stage 2 (P2-B distillation) 진입.

#### S10.1. Track A. Brain-only direct supervised MSE (E1-E4 encoder ablation, curriculum A1-A4)

Teacher 없음, video / caption 완전 제거. 각 encoder 를 brain-only 로 curriculum 순차 학습. Loss = subset per-emotion MSE, z-score 전처리 필수. Leakage 원천 차단, encoder ranking 가장 깨끗.

- [ ] Z-score fit (training set only). Per-emotion mean / std 계산 및 저장. Test set 에 transform 만.
- [ ] Sanity check. Prediction 이 z-scored 공간 에서 mean 0 근처 (initialization), std 1 근처 (수렴 후).
- [ ] Track A curriculum, 각 encoder (E1-E4) × 각 stage.
  - **A1**. Top-1 subset MSE (자극 별 rating 최고 1 감정 만). 1-2 주. 감정 하나 라도 학습 되는지 sanity.
  - **A2**. Top-2 subset MSE (자극 별 rating 상위 2). 1 주. Mixed emotion 학습.
  - **A3**. Top-k subset MSE (자극 별 rating threshold > 0.5 z-score 기준, 평균 5-8 감정). 1-2 주.
  - **A4**. Full 34D independent MSE. 2-3 주. 최종 target.
- [ ] 각 sub-stage 는 이전 stage checkpoint 에서 weight inherit.
- [ ] Track A 결과 = E1-E4 의 gap_filled ranking (A4 기준) + per-stimulus 34D profile shape similarity. Framework 의 modularity 검증 완료.

#### S10.2. Track B. P2-B distillation (Track A best encoder 1 개 만, context lift 정량)

**Scope (2026-07-03 확정).** E1-E4 각각 Track B 를 돌리지 않음. Track A 에서 확정 된 **best encoder 1 개** 만 Track B 로. Framework 검증 의 primary question = **"context 가 brain-only 를 얼마나 끌어 올리는가" (context lift)**, "어느 encoder 가 distillation 과 잘 맞는가" 가 아님.

Track A best encoder 위 에 teacher (brain+video+caption) 학습 → 34D soft label cache → student (brain-only) 가 teacher 34D 를 MSE 로 재현. Teacher / student 모두 curriculum B1-B4 순차.

- [ ] Teacher 학습 (brain+video+caption). Track A best encoder × curriculum B1-B4 순차. Per-emotion subset MSE. 각 stage 마다 34D soft label cache 생성 (`project/shared/output/teacher_soft_labels/B{stage}/`). Softmax 없음, raw 34D score caching.
- [ ] Student 학습 (brain-only). Track A best encoder × curriculum B1-B4 순차. Loss = L_main (subset MSE on z-scored target) + λ × L_distill (MSE on teacher 34D). λ grid (0.5 / 1.0 / 2.0). Caption dropout 확률 grid (0.5 / 0.7 / 0.9).
- [ ] Modality ablation (Full / no-caption / no-video / brain-only 4 조건, B4 기준). Caption-video overlap 검증.
- [ ] Video-on-caption residualize 조건 vs 원본 caption 조건 비교 (B4 기준). Caption 고유 기여 판정.
- [ ] Track A best A4 → Track B best B4 delta = **context lift** (framework 검증 headline). Positive / null / negative 모두 publishable.
- [ ] **Distillation 검증 A. Variance partitioning (필수, 2026-07-07).** Student 성능 을 brain 설명 부분 vs video 설명 부분 으로 분해. Distillation 이 brain 고유 성분 을 키웠는지 판정.
- [ ] **Distillation 검증 B. Brain-ablated student (필수).** Brain shuffle / 제거 후 남는 성능. 크게 안 떨어지면 video 우회 주입 경고.
- [ ] **Track B 성공 판정 = context lift + 검증 A/B 둘 다 통과.** Video (B2 에서 CLIP 0.60 >> brain 0.30) 우회 주입 을 "brain decoding" 으로 오인 방지.

#### S10.3. Ablation grid (sparse)

- [ ] (brain encoder 4) × (vision encoder 3) × (caption source 2) = 24 condition. sparse marginal sweep (Stage 1 best × vision 3, Stage 1 best × caption 2, full × encoder 4).
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
- ~~OD-E.~~ **[2026-06-30 SUPERSEDED]** Stage 4 KL target smoothing 은 KL 자체 를 폐기 하여 (34D independent MSE regression 으로 대체) 무효.
- **OD-D2 [NEW 2026-06-30]**. Distillation loss weight λ. Stage 2 의 L_total = L_main + λ × L_distill (per-emotion MSE 로 teacher 34D 재현). 0.5 / 1.0 / 2.0 grid 후 결정.
- OD-F. Hackathon 5 일 path 의 별도 진행 여부 (현 build phase 와 분리).
- **OD-G.** Q3 의 video frame temporal alignment (uniform sample vs HRF-aligned). 미정 (S7 시작 전 결정).
- **OD-P [NEW 2026-06-30]**. Caption dropout 확률 (student 학습). 0.5 / 0.7 / 0.9 grid 후 결정. Teacher-student prompt asymmetry 완화 + brain-only 강제 학습.
- **OD-T [NEW 2026-06-30]**. Projector token 개수 (bottleneck width). Nb / Nv 각각 8 / 32 / 128 grid 후 결정. 34D 고차원 구조 보존 과 직결.
- **OD-R [NEW 2026-06-30]**. Video-on-caption residualize 절차. Linear regression fit 위치 (training set only) + 잔차 조건 vs 원본 조건 delta 로 caption 고유 기여 판정.
- **OD-V [NEW 2026-06-30]**. Stage 1 vs Stage 2 sequential vs parallel. Sequential default (Stage 1 만 성공 해도 publishable, Stage 2 실패 도 별도 finding).

---

## Repo layout crosswalk (implementation_spec vs 현재 skeleton)

Implementation_spec §11 은 `emobrain/` 하위 root layout (`data/`, `models/`, `losses/`, `train/`, `eval/`, `utils/`, `scripts/`, `configs/`) 을 제안. 현재 skeleton 은 `project/code/{adapters, brain_encoder, vision_encoder, caption_loader, fusion, training, evaluation}/`. 다음 crosswalk 로 매핑.

| implementation_spec | 현재 skeleton |
|---------------------|---------------|
| `emobrain/data/{datasets, labels, caption_map, fmri_adapter}.py` | `project/code/{caption_loader, adapters}/` + 신설 필요 |
| `emobrain/models/encoders/{e1_projection, e2_ridge_encoder, e3_bfm, e4_vit}.py` | `project/code/brain_encoder/{raw_roi, ridge_embedding, bfm, vlm}.py` |
| `emobrain/models/{projector, video_encoder, prompt, llm_backbone}.py` | `project/code/{adapters, vision_encoder, fusion}/` |
| `emobrain/models/{teacher, student}.py` | `project/code/fusion/` + 신설 필요 |
| `emobrain/losses/{supervised, distillation, structure}.py` | `project/code/training/` + 신설 |
| `emobrain/train/*.py` | `project/code/training/*.py` |
| `emobrain/eval/*.py` | `project/code/evaluation/*.py` |
| `emobrain/configs/` | `project/config/` |
| `emobrain/scripts/run_experiment.py` | `project/sample_scripts/` |

S7 진입 시 위 crosswalk 로 mapping. Implementation_spec 의 module 명 은 현재 skeleton 내 파일 명 으로 alias.

## Config schema

전체 config schema 는 `docs/notes/implementation_spec_20260702.md` §10. `project/config/train.yaml` 은 이 spec 을 따름.

## Pointer

- **Code 구현 명세**. `docs/notes/implementation_spec_20260702.md` (Claude Code 대상, DECIDED / OPEN / CAUTION, Acceptance, 34개 감정 순서).
- 34 감정 canonical 순서. `project/shared/data/cowen34_order.txt`.
- Spine narrative. `Paper/framework_EN.md` + `Paper/framework_KR.md`.
- Architecture spec. `docs/notes/architecture_design_20260629.md`.
- Chronological decision. `docs/notes/project_decisions.md`.
