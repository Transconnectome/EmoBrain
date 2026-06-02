# FEELIN Weekly Report — 2026-06-01

> Phase 1 완료 + Phase 2 진행 중. Brain-only paradigm 학습 단계.

---

## 큰 그림 한 줄

> "Frozen brain foundation model 은 video baseline 못 넘는다 (당연. label 이 crowd-sourced video attribute)." Phase 1 종료. Phase 2 진행 중 = "어떤 학습 paradigm 이 brain 만으로도 emotion 예측을 향상시키나" 측정.

---

## 지난 주 한 일

### Phase 1 마무리 (✅)

| 항목 | 산출물 |
|---|---|
| SwiFT padding ablation 5-way (mean / replicate / zero / spatial_only / cyclic_replicate) × 4 task | `swift_padding_ablation_*.csv`, `swift_padding_cyclic_only_*.csv` |
| SwiFT 6 variants (NewE36, NewE96, NewE192, UAH 5M, UAH 51M, UAH 202M) × 4 task | `bfm_probe_SwiFT_<variant>_zero_<task>.csv` (총 24 cells) |
| Brain-JEPA NUM_FRAMES 20 → 16 + center-crop 으로 재추출 | `output/embeddings/brain_jepa_*_pad-{zero,mean}/` |
| Zero padding 통일 (모든 BFM 에서 main grid default = zero, znorm_minback 정합성) | `run_unified_probe.py` FEATURES update |
| Phase 1 wrap-up paper (15 page main + 11 page supplementary, LaTeX) | `reports/phase1_wrapup/main.pdf`, `supplementary.pdf` |
| Sartzetaki et al. ICLR 2025 citation 통합 (temporal modeling 관련) | `reference/papers.md`, `Paper/methodology.md`, `main.tex` |
| Phase 1 unified analysis pipeline (Nature-style figures, brain/video category split) | `code/analysis/phase1_*.py`, `figures/phase1/*.png` |

### Phase 2 v1 — Joint inference (✅)

4 architecture (D late fusion / A token transformer / B cross-attention / C contrastive) × 4 V/A task

| Arch | V_binary | A_binary | V_reg | A_reg |
|---|---|---|---|---|
| D late fusion | 0.972 | 0.803 | 0.589 | 0.268 |
| A token transformer | 0.967 | 0.792 | **0.763** | **0.424** |
| B cross-attention | 0.966 | 0.786 | 0.745 | 0.396 |
| C joint probe | 0.961 | 0.770 | 0.712 | 0.352 |
| C brain_only probe | 0.712 | 0.648 | 0.295 | 0.221 |

**Reference (Phase 1)**: CLIP linear V_binary 0.97 / V_reg 0.68 / A_reg 0.34. Brain-JEPA frozen V_binary 0.74.

### 핵심 발견 (지난 주)

1. **Phase 1 SwiFT scaling 효과 무**: 5M → 264M 변종 across, V_binary 0.66~0.69 안에 분포. Sartzetaki et al. 의 "FLOPs ↑ alignment ↓" 와 일관 (visual domain → emotion 으로 transfer)
2. **Phase 1 padding ablation**: mean / zero / spatial_only / cyclic_replicate 모두 0.001 이내 동률 (frozen SwiFT 가 시간 정보 사실상 안 씀). Replicate 만 명백히 worst.
3. **Phase 2 joint inference 도 video baseline saturation**: brain 추가 효과 0. **Crowd-sourced V/A label 의 video-attributable 성질**이 framing 의 핵심 (user-driven insight)
4. **Off-by-one bug 발견 + fix**: `stim_idx.npy` 0-indexed vs `stimulus_num` 1-indexed 의 misalignment. Phase 1 video probe 의 convention 으로 통일

### Phase 2 v2 — Brain-only paradigm (🔄 진행 중)

Reframe (user-driven): "CLIP 단독 넘는 게 목적이 아닌, brain 의 emotion 예측력 향상이 목적". Test 때 brain 만 보는 4 method 학습 중.

| Method | 설명 | Smoke (V_binary fold 1 seed 0) | Phase 1 BJ frozen reference |
|---|---|---|---|
| I supervised MLP | BJ feature 위에 직접 MLP supervised | 0.711 | 0.74 |
| II CLIP → brain distillation | CLIP teacher 의 logits 을 student 가 KL distill | 0.715 | 0.74 |
| III multitask brain | V/A + video feature recon multi-task | 0.714 | 0.74 |
| IV subject-aware brain | Brain + subject embedding | 0.711 | 0.74 |

Full benchmark (5 fold × 3 seed × 4 task × 4 method = 240 fit) launch 단계. 결과 후 unified analysis.

### BrainVLM infrastructure (✅, 학습은 안 함)

| 항목 | 상태 |
|---|---|
| Env (`brainvlm_qwen_env`) + Qwen3-VL-2B HF backbone | ✅ |
| Horikawa fMRI → BrainVLM `(1,1,96,96,96,20)` 변환 (10925 .pt) | ✅ |
| Emotion VQA conversation JSONL (75 파일 = 5 fold × 3 split × 5 subj) | ✅ |
| Random-init smoke test (PatchEmbedQwen forward) | ✅ |
| Path B / Path C skeleton 코드 | ✅ |
| **학습 loop** | ❌ next week 진입 |

**학습 결정**: Lab ABCD ckpt 안 와도 진행. PatchEmbedQwen + Merger random init → 우리 Horikawa 데이터로 직접 학습 (Qwen3-VL backbone frozen). 다음 주 첫 시도 fold 1 smoke 부터.

---

## Repo state

| Branch | Last commit | 비고 |
|---|---|---|
| main | dcab4cd (이번 주, weekly commit 포함 6 ahead of weekly/2026-05-18) | |
| weekly/2026-06-01 | main 의 snapshot | |

이번 주 push 한 5 commit
- `fe98c59` Phase 1 wrap-up: benchmark report (15p PDF) + analysis scripts
- `fd5a771` Phase 1 extension: SwiFT 6 variants + 5-way padding ablation + zero default across BFMs
- `00ec2bd` BrainVLM infrastructure (Path B + Path C skeletons, awaiting actual training)
- `3809a47` Phase 2: 4 fusion architectures (D/A/B/C) + 4 brain-only methods (I/II/III/IV)
- `0a79469` Top-level docs: Phase 1 ✅ / Phase 2 🔄 status + scope refinements

---

## Open questions / decisions

1. **CV split**: Phase 1 + Phase 2 모두 stim-stratified 5-fold 사용. LOSO 는 N=5 라 statistical power 약함, 채택 안 함. Subject 일반화는 Phase 3 counterfactual swap 으로 측정 예정.
2. **BrainVLM 학습 방향**: random init → Horikawa supervised training 으로 갈 예정 (lab ABCD ckpt 도착 안 기다림). 첫 fold 1 smoke 부터.
3. **Phase 2 brain-only 결과의 framing**: 만약 4 method 모두 frozen probe (0.74) 못 넘으면 → "brain encoder 학습 자체가 5 subj × 2185 stim regime 에서 어려움" 의 honest evidence. 통과하면 winner method 로 Phase 3 진입.

---

## 다음 주 plan

### Week of 2026-06-02

1. **Phase 2 brain-only 4 method full benchmark 마무리** + unified analysis
2. **Phase 2 wrap-up paper draft 시작** (Phase 1 PDF format 재활용 가능)
3. **BrainVLM training loop 작성 + fold 1 smoke run** (1 epoch, train loss 떨어지는지, generation 형식 따르는지)
4. **BrainVLM full train (fold 1, 3 epoch)** + emotion VQA inference + Phase 2 결과와 비교
5. (시간 여유 시) **Subject-conditioned variability 분석** — Phase 2 의 trained model 위에서 같은 stim 의 5 subj output variance 측정

---

## Risk / blocker

- 없음. 외부 의존 (lab ABCD ckpt) 은 wait list 에서 빼고 우리 자체 학습으로 진행.
- BrainVLM 학습 비용 (GPU 시간) 이 5 subj × 2185 sample × 3 epoch 에서 어떻게 나오는지 W1 smoke 후 결정.
