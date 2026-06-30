# EmoBrain Project Decisions Log

Decision 기록은 시간순. 가장 최신이 위.

---

## 2026-06-29. Spine pivot. Direction 폐기 + single project + framework novelty path

**결정.**

1. **EmoBrain 의 project framing 의 변경.** D1 BrainVLM / D2 fMRI-LM / D3 CCN 의 3 direction split 폐기. **single project = 한 paper**.
2. **Title lock.** *"EmoBrain: Decoding fine-grained emotion from human brain activity."*
3. **Spine = framework novelty path** (R-full-new). 5 novelty 의 결합 의 multi-modal foundation model.
    - NV0. LLM-based brain emotion decoder. emotion 분야 의 LLM 통합 의 first instrument.
    - NV1. 3-modality (brain + video + caption) 의 LLM 통합 fusion.
    - NV2. MindCaptioning 의 human-written neutral caption 의 brain-context bridge.
    - NV3. Modular brain encoder (raw / Ridge / BFM / VLM 의 swappable).
    - NV4. 34-distribution output 의 4 stage curriculum (top-1 → top-2 → top-k → full distribution KL).
4. **기존 작업 (Phase 1, D1, D2, D3) 의 보존.** Section 4 (modular brain encoder ablation) 의 evidence 로 활용. 결과 의 *날리지 않음*.

**근거.**

2026-06-29 의 Mode 3 panel (literature + methodology + publishability 의 3 agent parallel) 의 수렴 verdict.

(a) **Reframe option A/B/C/D 의 evaluation.** 모두 약 함 또는 redesign 필요. spine reframe 의 진짜 답 = 새 framework novelty path 의 R-full-new.

(b) **EmoMind 의 NeurIPS 의 borderline-to-reject 의 predicted verdict** (literature + publishability agent 의 수렴). 단 framework novelty path 의 *path 자체* 는 publishable. 우리 도 같은 path.

(c) **우리 의 4 backbone 의 plateau 의 결과.** capacity 의 issue 가 아닌 *output formulation + multi-modal 의 부족* 의 의심. 새 framework 의 5 NV 의 결합 의 시도 의 의미.

(d) **사용자 의 design 의 결정.** "fMRI → Brain Encoder (modular) + Video → Vision encoder + MindCaptioning caption + Prompt → LLM 통합 fusion → 34D distribution output" 의 architecture 가 emotion 분야 의 first.

**영향.**

- 새 directory `project/code/` 생성 (adapters/brain_encoder/vision_encoder/caption_loader/fusion/training/evaluation 의 subdirectories).
- `archive/v5_direction_split_20260628/` 생성. 기존 dir1_brainvlm/dir2_fmri_lm/dir3_ccn 의 symlink reference (학습 종료 후 진짜 mv).
- `Paper/framework_EN.md` + `framework_KR.md` 통째 rewrite (직전 의 D1/D2/D3 framing 폐기, single project + 5 NV 의 spine).
- `README.md` + `README_KR.md` + `CONTEXT_EMOBRAIN.md` + `ACTION_PLAN.md` update.
- 기존 D1 의 학습 (REG variant 의 VA binary + regression) 의 *그대로 진행*. 결과 는 paper 의 Section 4 의 modular encoder ablation 의 일부 로 활용.

**다음 step (12-16 주 의 큰 build).**

- S7. 3-modality adapter (brain + video frame + MindCaptioning caption + 우리 generated caption) 의 dataset 통합.
- S8. Multi-modal model 의 main + trainer (LLM 의 multi-modal token fusion + 34D head + soft KL target).
- S9. SMOKE test + 사용자 launch.
- S10. 4 stage curriculum 학습.
- S11. Evaluation (variance partitioning + ceiling anchor + dissociation) + paper draft.

---

## 2026-06-28. D1 BrainVLM VA task 2/2 FAIL 확정 + Option B + C 병렬 진행

**결정.**
1. D1 BrainVLM 의 *XML token output + cross-entropy* setup 의 fundamental limit 확정. Plan A (Qwen3-VL family size sweep, 2B/4B/8B/v1+v2) 의 학습 종료.
2. **Option B (Plan C). Regression head 직접 attach** code 작성 시작. main_umbrella_training_qwen 의 새 variant. backbone hidden state → small MLP → scalar 직접 numeric output. cross-entropy 대신 MSE.
3. **Option C. D2 fMRI-LM (Wei 2026 architecture)** code 작성 시작 (병렬). 3-stage (ViT tokenizer + paired alignment + instruction tuning).
4. 두 옵션 의 학습 결과 비교 1 주 후 + spine 의 next iteration 결정.

**근거.**

(a) **2/2 VA task FAIL + 4 backbone size 모두 동일 plateau.**

| Backbone | VA binary best token_acc | VA regression best V Pearson r |
|---|---|---|
| 2B (v1, lr 5e-4 epoch 50) | 0.597 (vs baseline 0.720) | 0.035 (vs baseline 0.416) |
| 4B (v2, lr 1e-4 epoch 10) | 0.586 | 0.008 |
| 8B (v2, lr 1e-4 epoch 10) | 0.606 | (학습 안 됨) |

token_acc 0.6 plateau = XML boilerplate token 의 match 의 noise. 실제 numeric Pearson r 의 학습 거의 없음 (baseline 의 1/10 ~ 1/20).

backbone size 의 increase 가 *전혀 차이 안 만듦* = backbone capacity 의 issue 가 아님 = *output formulation 의 fundamental limit*.

(b) **Root cause = token-level autoregressive output 의 형식 한계.** Model 이 number 를 *digit by digit token* 으로 출력 → cross-entropy loss 가 *digit-level token distribution* 학습 → brain signal 의 continuous nature 와 mapping 안 됨.

(c) **EmoMind 의 paradigm 의 시사.** EmoMind (Mohammed et al., 2026) 도 stage 1 에서 *ridge regression 으로 brain → 34D vector 의 continuous mapping 직접 학습* + stage 2 에서 token output 은 *condition 으로 만* 사용. 우리 도 *token output 의 mapping 학습 폐기 + continuous head 직접 attach* 의 paradigm 으로 가야 함.

**영향.**

- `docs/reports/d1_brainvlm_va_negative_result_20260628.md` 작성 = 본 결정 의 evidence base.
- `Paper/framework_EN.md` + `Paper/framework_KR.md` 의 §Status section update. VA 박살 + 4 backbone size FAIL + Option B+C plan.
- `project/dir1_brainvlm/code/` 에 새 variant `main_umbrella_training_qwen_NoPool_REG.py` 작성 (Option B).
- `project/dir2_fmri_lm/code/` 시작 (Option C).
- 1 주 후 두 옵션 의 결과 비교 + spine 의 next iteration (SC1 의 재시도 또는 reframe).

**Lessons learned.**

- token_acc 같은 *string-level metric* 은 *task-native metric* (Pearson r, balanced acc, AUROC) 과 분리 reporting. token_acc 0.638 의 *misleading appearance* 의 trap 회피.
- Baseline 의 *exact 비교 가능 한 metric* 학습 *전* 에 확정. learning curve 의 *진짜 의미* 가 학습 중 보이게.
- 50 epoch full training 의 cost (24-48 hr/task) 전에 *5 epoch pilot* 으로 actual metric (Pearson r) 확인.
- Backbone size sweep 의 진단 가치 (size 의 issue 인지 output formulation 의 issue 인지 분리).

---

## 2026-06-24. Spine rewrite. SQ 4 component + Model 3 trick + VA binary FAIL

**결정.** Framework 의 spine 을 이전 SC1-3 (outcome 위주 framing) 에서 **SQ 4 component + Model novelty 3 trick + Status** 의 3 축 spine 으로 재구성.

**SQ 4 component.**
- (a) Universal region map. 같은 영상 의 5 brain 의 model attention 일치 ROI.
- (b) Idiosyncratic region map. attention 갈 림 ROI.
- (c) Stimulus law. 영상 별 prediction error 와 영상 property 의 correlation.
- (d) Cross-subject transfer. 4 subj train → 5th subj zero-shot via ICL.

**Model novelty 3 trick.**
- T1. Multi-image ICL with cross-subject pool. 여러 사람 brain 한 prompt. SQ-(d) instrument.
- T2. Subject ID embedding tag. 사람 별 path 분리. SQ-(a)(b) instrument.
- T3. ROI-attention readout head. 학습 부산물 로 region map. SQ-(a)(b) instrument.

**근거.**
1. **이전 candidate spine = NQ3 (caption 을 brain emotion decoding 실패 mechanism evidence 로 사용 하는 trial-level variance decomposition) 폐기.** 2026-06-24 의 3-panel red-team review (literature critic + methodology critic + publishability critic 의 parallel spawn) 의 fatal flaw 3 개 수용.
    - Caption circular instrument. caption 이 same LoRA downstream, prediction 과 같은 weight 산물, brain evidence 가 model internal consistency 와 분리 불가.
    - N=5 subject d.f.=4 underpowered. variance decomposition 의 dominance 주장 통계 적 불가.
    - Story coherence mismatch. 6 task suite + LoRA + ICL 의 train objective 가 multi-task generalization, variance decomposition 아님.
2. **위 SQ 4 component 가 우리 자산 + model design 과 perfect align.** Story coherence 확보.
3. **Bush 2018 / EmoMind / MindCaptioning 의 어느 paper 도 4 component 통합 측정 안 함.** 진짜 incremental novelty (literature critic 의 verdict "marginally new, but integration novel").
4. **EmoMind 와 의 spectrum framing 유지.** EmoMind = per-subject endpoint, EmoBrain = universal endpoint. 정면 충돌 X.

**Model novelty 의 EmoMind 대응.** EmoMind 의 axis matrix A (34×768) + classifier-free guidance + 2-stage retrieval+rewriter 와 의 architectural 대응 = 우리 의 T1 + T2 + T3.

**Video form decision.**
- Main paper = brain only. Horikawa silent video 의 visual content 는 input 으로 안 넣음.
- Supplementary = brain + video raw frame. 학습 후 추가 학습 1 form 만. SC3 의 multi-modal lift 측정 용.
- CLIP feature / caption / low-level feature = 안 함 (scope creep 회피).

**SC revised.**
- SC1. Universal code existence. pooled VLM ≥ Phase 1 ROI ridge baseline.
- SC2. Cross-subject transfer. LOSO setting 의 zero-shot 평가.
- SC3. Multi-modal lift (supplementary). brain+video vs brain-only.
- SC4. Multi-task consistency. 6 task output internal consistency.

**Status. VA Binary FAIL 의 1 차 evidence.**
- D1 BrainVLM 의 V/A binary 학습 완료 (50 epoch, 1750 step).
- Best ckpt = step 200 (epoch 5.7), token acc 0.597.
- **Phase 1 ROI mean + Ridge baseline (balanced acc 0.720) 못 넘 음. SC1 의 first task FAIL.**
- Final ckpt 의 acc 0.49 (chance 아래). epoch 6 peak 후 collapse. 심한 overfit.
- 원인 후보. LR 5e-4 너무 큼 / LoRA capacity mismatch / token-level prediction 의 형식 한계 / ICL ref random 의 noise.
- VA regression 학습 진행 중. 결과 가 SC1 운명 결정.

**영향.**
- `Paper/framework_EN.md` + `Paper/framework_KR.md` rewrite (SQ 4 component + Model 3 trick + revised SC + Status section + EmoMind positioning + open decision 6).
- `docs/notes/paper_spine_v1.md` + `docs/notes/evaluation_framework_v1.md` 폐기 (CLAUDE.md rule "narrative 는 Paper/framework_EN.md, framework_KR.md" 위반 file. 합의 내용 모두 framework_EN/KR 로 이전 후 제거).
- `ACTION_PLAN.md` 의 stale reference (paper_spine_v1.md, evaluation_framework_v1.md) 정리 + framework_EN reference.
- 다음 action. (1) VA regression 결과 대기, (2) Plan B hyperparameter tuning 의 trigger 결정 (regression 도 FAIL 인 경우), (3) Cat34 학습 진행.

---

## 2026-06-08 (today). Framing pivot v4 → EmoBrain (sj_NEW_20260608_perlmutter)

**결정**. 기존 v4 framing (universal emotion code 검증, Track A SSL pretrain main + Track B Multimodal main + Track C BrainVLM supplementary) 를 EmoBrain framing (BrainVLM main + Brain-Video Multimodal main 의 2 axis) 로 전환.

**근거**.
1. Phase 1 측정 결과 (`reports/phase1_audit_20260604/`) 가 frozen BFM (BJ, NS, SwiFT 6 변종) 이 simple ROI baseline 을 못 넘음을 확정. V/A binary, V/A reg, Cat34 multilabel, Cat34 soft 모든 task 에서 일관. 원인은 Horikawa 자극의 짧은 T 분포 (median 5 TR, 71.6% 가 T=5) 와 BFM 입력의 평균 63-70% zero padding.
2. Broader field trend 가 frozen BFM 단독 대비 VLM / LLM 기반 brain decoding 의 우세를 보여줌. MindLLM (2025) subject-agnostic fMRI-to-text, UMBRAE (ECCV 2024), Mind Captioning (Horikawa Science Advances 2025) 모두 frozen LLM/VLM 을 prior 로 활용. BFM frozen embedding 단독은 거의 안 보고됨.
3. Multimodal brain alignment 의 standard evaluation 정착. TRIBE (Meta FAIR, Algonauts 2025 1 위) 의 frozen large encoder + transformer fusion + variance partitioning 이 표준. EmoBrain 의 Direction 2 가 그 framework 의 emotion specific 확장.

**영향**.
- Branch `sj_NEW_20260608_perlmutter` 신설. 이전 framing 은 `archive/v4_20260602/` 에 보존.
- BFM 의 main 작업 (Track A SSL pretrain, subject-invariant SSL 학습) 은 main scope 제외. 단 Direction 2 의 brain encoder 후보로 활용 가능.
- 새 main = Direction 1 BrainVLM + Direction 2 Brain-Video Multimodal. 둘 다 main, complementary.
- EmoFM 이라는 name 후보가 BFM 의미와 충돌하므로 EmoBrain 으로 전환.

**문서 update**.
- `README.md`, `README_KR.md`, `CONTEXT_EMOBRAIN.md`, `ACTION_PLAN.md` 모두 EmoBrain framing 으로 재작성.
- `docs/masterplan_v3_emobrain.md` 작성 예정.
- `Paper/framework_EN.md`, `framework_KR.md`, `methodology.md` 재작성 예정.
- 이전 .md 는 `archive/v4_20260602/` 에 보존.

---

## 2026-06-07. Cat34 multilabel threshold 변경 0.15 → 0.10

**결정**. Cat34 multilabel task 의 threshold 를 `0.15` 에서 `0.10` (= 1/10 raters, 자연 단위) 으로 변경.

**근거**. Threshold sensitivity 분석 (`reports/phase1_audit_20260604/` 의 Cat34 audit).
1. **자연 단위**. 0.10 = "rater 의 10% (= 10 명 중 1 명) 이상 평가" 의 명확한 의미. 0.15 는 1/8 과 1/6 사이 임의 round number, 자연 단위 아님.
2. **모든 자극이 supervision 받음**. 0.10 에서 zero-label 자극 = 0 (모든 자극이 적어도 1 category 양성). 0.167 부터 일부 자극에서 양성 없음.
3. **Minority category 안정성**. 0.10 에서 가장 minority category 의 양성 비율 0.007 (= 약 15 자극). 5-fold CV 에서 fold 당 3 자극, 학습 안정. 0.15 는 0.0037 (= 8 자극) 으로 fragile.
4. **mixed emotion 의 적절한 표현**. 0.10 에서 평균 자극당 4.93 cat 양성. Vaccaro 2024 의 mixed valence framework 와 일관.

**영향**.
- `project/shared/code/probes/run_unified_probe.py:147`, `project/shared/code/probes/run_chance_cat34.py:41`, `project/dir3_ccn/code/legacy_phase2/_lib.py:41` 의 `CAT34_MULTILABEL_THRESHOLD` 변경.
- Cat34_multilabel + Cat34_soft 재측정 launch. 결과 CSV 는 `_t010` suffix 로 저장 (기존 0.15 결과 보존).
- 발표 / paper 의 method section 에 threshold 선택 근거 명시.

---

## 2026-06-04. Phase 1 audit + BFM 의 한계 확정

**결정**. Phase 1 의 5 단계 deep audit (1A 임베딩 → 1B video features → 1C probing code → 1D task definitions → 1E results consistency) 진행. 모든 audit 결과는 `reports/phase1_audit_20260604/` 에.

**주요 발견**.
- E1 (BFM 의 T 처리 정책 모델별 상이). BJ center crop 16 TR, NS/SwiFT first 20 truncate.
- E2 (BJ pretrained checkpoint adaptation). pos_embed 10 time patches → 1 평균 + patch_embed kernel linear interp.
- E3 (Horikawa T 분포 짧음). median 5, 71.6% T=5, BFM 입력의 평균 63-70% zero.
- F8 / F13 (Cat34_top1 broken folds). 일부 fold 에서 minority class 가 train 에 없음. 결과 unreliable, 제외 권고.
- F_C5 (NeuroSTORM wrapper 중복). single + split 둘 다 존재, 어느 게 main 인지 확인 필요.
- F_C6 (Cat34 multilabel / soft 의 MLP 결과 없음). `--skip_mlp` 로 launch.

**Phase 1 결론**. Frozen BFM 이 simple ROI baseline 을 넘지 못함. EmoBrain framing pivot 의 evidence base.

---

## 2026-06-04. Phase 1 method + result PDF 작성

**결정**. Phase 1 의 method (data, split, BFM extraction, probing protocol, tasks, baselines) + result (V/A binary, V/A reg, Cat34 multilabel + soft 의 BFM vs ROI vs chance 비교) 를 한국어 + LaTeX 로 정리한 self-contained PDF 작성.

**위치**. `reports/phase1_audit_20260604/_pdf/main.pdf` (10 page).

**의의**. 발표 / hackathon / paper 의 reference 자료.

---

## 2026-06-04. Cat34 baseline 보강 (ROI + chance)

**결정**. Cat34_multilabel + Cat34_soft 의 ROI baseline 과 chance baseline 이 phase 1 launch 에서 누락된 점 발견. 보강 launch (`cat34_roi.sh` + `cat34_chance.sh`). 코드 `project/shared/code/probes/run_chance_cat34.py` 신설.

**결과**. Cat34_multilabel macro AUROC: ROI 0.711, BJ resting 0.679, NS 0.669, SwiFT NewE96 0.629, chance 0.500. ROI 가 모든 BFM 보다 높음, Phase 1 의 V/A 패턴과 동일.

---

## 2026-06-04. Zero padding only 결정

**결정**. Phase 1 의 BFM embedding 분석 scope 를 zero padding 만 사용으로 통일.

**근거**. mean padding 과 spatial_only padding 의 결과가 cosine 0.9999 이상으로 사실상 동일 (mean padding 재추출 의도 안 됨). Replicate / cyclic_replicate 도 mean 과 매우 가까움. Zero padding 만 명확히 다른 representation 산출. Padding 변종 ablation 의 단순화.

**영향**. Audit 보고서 (`reports/phase1_audit_20260604/1A_embeddings.md`) 의 scope 갱신.

---

## 2026-06-02. v4 framing 정리 (이전 framing, 현재 archive)

이전 framing 의 decision log 는 `archive/v4_20260602/notes/project_decisions.md` 에 보존.
