> ⚠️ **ARCHIVED — 역사 기록. 현행 문서가 아니다.**
> 현행 논증 = `docs/paper_logic_merged.md` (대전제 · RQ · 가설 H1–H4). 운영 규칙 = `CLAUDE.md`.
>
> 아래 내용 중 다음은 **뒤집혔다.** (a) Qwen3-VL 등 LLM backbone 사용 — 금지.
> (b) open-vocabulary / cross-taxonomy 전이를 headline novelty 로 삼는 프레임 — 폐기.
> (c) 학습에 없던 감정 zero-shot — 폐기(원칙적 분할 기준 없음, RQ 와 무관).
> (d) "EmoBrain 과 EmoViS 는 별도 논문 2편" — 현재는 **한 편의 논문**.
> (e) "EmoBrain 은 cortical location 을 주장하지 않는다" — 현재 **H3 이 cortical location 주장**이다.

# EmoBrain Masterplan v3 (SUPERSEDED 2026-06-29)

> **STATUS. SUPERSEDED.** 이 v3 masterplan 은 Three Directions (D1 BrainVLM + D2 fMRI-LM + D3 CCN) framing 을 전제. 2026-06-29 pivot 으로 single project + 5 novelty (NV0-NV4) framing 으로 전환. 아래 내용은 참조/역사용 이며 active forward plan 아님.
>
> **Current forward plan.**
> - Spine narrative. `../Paper/framework_EN.md`, `../Paper/framework_KR.md`.
> - Architecture spec. `notes/architecture_design_20260629.md`.
> - Ground-level weekly action. `../ACTION_PLAN.md` (S7-S11).
> - Red-team synthesis. `notes/redteam_review_20260630.md` (7 blocker + 12 recommendation).
> - Chronological decision. `notes/project_decisions.md`.
>
> **Archive.** Three Directions 시절 code / doc 은 `../archive/v5_direction_split_20260628/`.

---

Branch `sj_NEW_20260608_perlmutter`. Forward plan for the EmoBrain framing (v3, historical).

**Structure.**
- **Background**. Phase 1 benchmark (frozen BFM 한계 확정, Horikawa, completed).
- **Direction 1**. BrainVLM (main paper).
- **Direction 2**. fMRI-LM (main paper, Wei 2026 architecture 차용).
- **Direction 3**. CCN. Brain-Video alignment + context clustering (별도 workshop 발표).
- **Application**. Hackathon (5 일 demo).
- **Output**. Paper + Submission (D1 + D2 의 2 × 2 grid) + CCN workshop poster (D3).

D1 + D2 가 main paper 의 2 axis. D3 는 별도 발표 path (`project/dir3_ccn/`).
Dataset 2 개. Horikawa + Emo-FilM (다운로드 예정).

## 1. Research Question

Brain 에서 mixed / complex emotion 의 구조는 어떻게 나타나는가? 이를 잘 포착하기 위한 model 과 task design 은 무엇인가?

### Sub-questions

- SQ1 (D1). **VLM bridge 의 emotion-relevant gain**. Qwen3-VL 위 LoRA fine-tune 으로 emotion multi-task 출력했을 때 frozen BFM 단독 대비 V/A 와 Cat34 의 향상이 있는가?
- SQ2 (D2). **fMRI-LM 의 emotion 적응**. Wei 2026 의 architecture (LLM tokenizer + 3-stage tuning) 가 emotion task 에서 D1 보다 더 효과적인가?
- SQ3 (D3). **Context clustering in brain**. Video embedding 위 learning clustering 이 emotion 1 개 안에서 context 별 sub-cluster 를 emerge 시키고, 그 context 가 brain 표상에서도 나타나는가?
- SQ4 (cross-dataset). 두 dataset (Horikawa + Emo-FilM) 의 D1 + D2 + D3 결과가 transfer 되는가? 새 task design 에 어떤 label 이 universal 한가?

## 2. Background. Phase 1 Benchmark (Completed)

세부는 `archive/v4_20260602/docs/masterplan_v2.md` 의 Phase 1 과 동일. 결과 + audit 은 `docs/reports/phase1_audit_20260604/`.

**결론**. Frozen BFM 이 simple ROI baseline 을 못 넘음. EmoBrain framing 의 motivation.

| Task | Best BFM (BJ resting) | ROI baseline | Chance |
|------|------------------------|--------------|--------|
| V_binary AUROC | 0.738 | **0.789** | 0.500 |
| A_binary AUROC | 0.662 | **0.678** | 0.500 |
| V_reg Pearson r | 0.330 | **0.396** | 0.000 |
| A_reg Pearson r | 0.221 | **0.233** | 0.000 |
| Cat34_multilabel (t=0.10) macro AUROC | 0.669 | **0.699** | 0.500 |
| Cat34_soft mean Pearson r | 0.237 | **0.280** | -0.004 |

## 3. Direction 1. BrainVLM

**Architecture**. UMBRELLA_qwen (Qwen3-VL backbone) 의 fMRI patchifier + 2D ROI-based brain representation + LoRA fine-tune + multi-task output head.

**Output**. (a) Emotion VQA / caption 자연어, (b) V/A continuous score, (c) Cat34 distribution.

**Loss**. CE (caption) + MSE (V/A) + KL (Cat34 soft).

**Reference**. MindLLM 2025, UMBRAE 2024, Mind Captioning 2025, MedBLIP 2023, BLIP-2 2023, LLaVA 2023.

**Gate**. V/A Pearson r 가 Phase 1 ROI baseline 보다 의미있게 높으면 Direction 1 main path 확정.

Action 상세는 `ACTION_PLAN.md` Direction 1 (Action 1.1 ~ 1.3).

## 4. Direction 2. fMRI-LM (main paper)

**Architecture**. Wei 2026 (arXiv 2511.21760) 의 fMRI-LM 3-stage pipeline 을 차용 후 emotion specific 으로 발전.

- Stage 1. Brain-JEPA-like ViT tokenizer + Vector Quantizer → fMRI discrete token. SigLIP + GRL + reconstruction.
- Stage 2. GPT-2 / Qwen3-0.6B LLM + F2F + F2T + T2T 3-objective (L_F2T + 0.1 L_F2F + 0.5 L_T2T).
- Stage 3. Instruction tuning + LoRA.

**Synthetic descriptor corpus**. Horikawa 의 V/A + Cat34 + Qwen-VL caption → template + LLM rewrite. paired fMRI-text 의 자연 부재 우회.

**Reference**. fMRI-LM (Wei 2026, arXiv 2511.21760).

**Gate**. V/A Pearson r + Cat34 macro AUROC 가 Phase 1 ROI baseline 보다 의미있게 높음. D1 BrainVLM 과의 비교 (어느 architecture 가 emotion 잡는데 더 적합).

Action 상세는 `ACTION_PLAN.md` Direction 2 (Action 2.1 ~ 2.5).

## 4.5. Direction 3. CCN. Brain-Video Alignment + Context Clustering (workshop 별도)

**위치**. `project/dir3_ccn/` (이전 CCN_Emotion + alignment_pilot + legacy_phase2 통합).

**Architecture**. Brain encoder + V-JEPA2 video encoder + projection (SigLIP + GRL) + learning clustering on video embedding.

**Goal**. Video embedding 위 learning clustering → context 반영된 cluster 가 emerge 하는지. **같은 emotion (예: joy) 안에서 context 별 sub-cluster 가 brain 표상에서도 나타나는지** 검증.

**Evaluation**.
- Cluster emergence (전체 자극의 video embedding 위에서 cluster 가 얼마나 명확히 분리되는가).
- 감정 1 개로 세팅 (예: joy stim 만으로 sub-cluster 확인).
- Independent dataset transfer (cross-dataset universal context structure).

**Gate**. Cluster emergence + cross-dataset preservation 의미있으면 CCN workshop poster. 결과 강하면 paper 까지.

**Reference**. TRIBE 2025, VIBE 2025, CineBrain 2025, Doerig 2024, BraVL 2023, Aligning machine and human visual representations across abstraction levels (2025).

Action 상세는 `ACTION_PLAN.md` Direction 3 (Action 3.1 ~ 3.3).

## 5. Standard Baseline Suite

모든 결과는 다음과 함께 reporting.

| Baseline | 측정 상태 |
|----------|-----------|
| Chance (DummyClassifier stratified + most_frequent, DummyRegressor mean + median) | Phase 1 측정 완료 |
| ROI mean + Ridge / Logistic L2 | Phase 1 측정 완료 |
| ROI mean + MLP | Phase 1 측정 완료 |
| Frozen BFM (BJ resting) reference | Phase 1 측정 완료 |
| Video baseline (Qwen-VL caption / V-JEPA2 pretrained) | Phase 1 측정 완료 |

## 6. Tasks

| Task | Phase 1 측정 | Direction 1 평가 | Direction 2 평가 |
|------|---------------|--------------------|--------------------|
| V/A Binary | 완료 | yes | yes |
| V/A Regression | 완료 | yes | yes |
| Cat34 Multilabel (threshold 0.10) | 완료 | yes | yes |
| Cat34 Soft Distribution | 완료 | yes | yes |
| Mixed Valence Categorization | 미측정 | yes | yes |
| Caption Embedding Regression | 미측정 | yes | (n/a) |
| Emotion VQA | 미측정 | yes (Direction 1 specific) | (n/a) |

## 7. Data

### Main dataset
- Horikawa naturalistic video fMRI (5 subj × 2185 stim, Cowen 34-cat + 14-dim + V/A continuous rating).

### Paper 단계 cross-dataset 확장 후보
- Emo-FilM, StudyForrest, CineBrain, NNDb, Affective Videos.

## 8. Risk + Mitigation

| Risk | Mitigation |
|------|------------|
| Direction 1 의 BrainVLM 이 Gate 통과 못 함 (V/A r < ROI) | Prompt template + LoRA position ablation 후 재평가. fail 시 Direction 2 main path 로 통합. |
| Direction 2 의 brain unique variance 가 noise 수준 | Brain encoder 변경 (BJ → ROI mean → fine-tuned 학습) + multi-loss balance 재조정. |
| Horikawa 의 짧은 T 분포 (median 5) 가 두 direction 모두에서 한계 | Cross-dataset 확장으로 더 긴 T 의 자극 확보 (Emo-FilM, CineBrain). |
| Compute quota 한계 | Direction 별 pilot 은 fold 1 만으로 시작. Full grid 는 paper 단계. |

## 9. Branch Strategy

- `main`. v4 framing 의 안정판. 보존만.
- `v4_20260602_perlmutter`. v4 main + subject-invariant SSL pretrain 작업물.
- `sj_NEW_20260608_perlmutter`. **current**. EmoBrain framing 의 active branch.
- `archive/v4_20260602/`. v4 의 .md 문서 보존.

## 10. Reference Decisions

세부 결정은 `docs/notes/project_decisions.md` 의 시간순 log.
