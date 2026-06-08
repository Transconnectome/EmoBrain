# EmoBrain Masterplan v3

Branch `sj_NEW_20260608_perlmutter`. Forward plan for the EmoBrain framing.

**Structure.**
- **Background**. Phase 1 benchmark (frozen BFM 한계 확정, completed).
- **Direction 1**. BrainVLM (main).
- **Direction 2**. Multimodal Alignment (main).
- **Application**. Hackathon (5 일 demo).
- **Output**. Paper + Submission.

Two directions 는 complementary 이며 둘 다 main scope.

## 1. Research Question

Brain 에서 mixed / complex emotion 의 구조는 어떻게 나타나는가? 이를 잘 포착하기 위한 model 과 task design 은 무엇인가?

### Sub-questions

- SQ1. **VLM / LLM bridge 의 emotion-relevant gain (Direction 1)**. fMRI 를 VLM token 으로 주입하고 LoRA fine-tune 으로 multi-task emotion 출력했을 때, frozen BFM 단독 대비 V/A 와 Cat34 task 의 의미있는 향상이 있는가?
- SQ2. **Brain unique contribution (Direction 2)**. Brain encoder + V-JEPA2 video encoder 의 contrastive alignment 위에서 brain 이 video baseline 위에 추가하는 unique emotion variance 가 존재하는가?
- SQ3. **Mixed / complex emotion 의 표현**. Cat34 multilabel + soft distribution + mixed valence 의 fine structure 를 두 axis 가 각각 어떻게 잡는가?
- SQ4 (optional, cross-dataset). 두 direction 의 학습된 표상이 Horikawa 외 다른 dataset (Emo-FilM, CineBrain, StudyForrest) 으로 transfer 되는가?

## 2. Background. Phase 1 Benchmark (Completed)

세부는 `archive/v4_20260602/docs/masterplan_v2.md` 의 Phase 1 과 동일. 결과 + audit 은 `reports/phase1_audit_20260604/`.

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

## 4. Direction 2. Multimodal Alignment

**Architecture**. Brain encoder (Brain-JEPA frozen 또는 학습 가능 BFM) + V-JEPA2 video feature + projection head (공통 embedding space) + InfoNCE symmetric contrastive loss.

**Optional**. Subject-invariant 학습 (같은 자극의 다른 subject brain 도 가까워지도록).

**Evaluation**. Variance partitioning. Brain unique variance = Joint - Video-only.

**Reference**. TRIBE 2025, VIBE 2025, CineBrain 2025, Doerig 2024, BraVL 2023.

**Gate**. Brain unique variance 가 paired bootstrap p < 0.05 이고 Pearson r 향상 +0.05 이상이면 Direction 2 main path 확정.

Action 상세는 `ACTION_PLAN.md` Direction 2 (Action 2.1 ~ 2.3).

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

세부 결정은 `notes/project_decisions.md` 의 시간순 log.
