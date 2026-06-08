# EmoBrain Masterplan v3

Branch `sj_NEW_20260608_perlmutter`. Forward plan for the EmoBrain framing (BrainVLM + Brain-Video Multimodal 의 2 main axis).

## 1. Research Question

Brain 에서 mixed / complex emotion 의 구조는 어떻게 나타나는가? 이를 잘 포착하기 위한 model 과 task design 은 무엇인가?

### Sub-questions

- SQ1. **VLM / LLM bridge 의 emotion-relevant gain**. fMRI 를 VLM token 으로 주입하고 LoRA fine-tune 으로 multi-task emotion 출력했을 때, frozen BFM 단독 대비 V/A 와 Cat34 task 의 의미있는 향상이 있는가?
- SQ2. **Brain unique contribution**. Brain encoder + Video encoder (V-JEPA2) 의 contrastive alignment 위에서 brain 이 video baseline 위에 추가하는 unique emotion variance 가 존재하는가?
- SQ3. **Mixed / complex emotion 의 표현**. Cat34 multilabel + soft distribution + mixed valence 의 fine structure 를 두 axis 가 각각 어떻게 잡는가?
- SQ4 (optional, cross-dataset). Direction 1 + 2 의 학습된 표상이 Horikawa 외 다른 dataset (Emo-FilM, CineBrain, StudyForrest) 으로 transfer 되는가?

## 2. Two Axes

### Direction 1. BrainVLM

**Architecture**. UMBRELLA_qwen (Qwen3-VL backbone) 의 fMRI patchifier + 2D ROI-based brain representation + LoRA fine-tune + multi-task output head.

**Output**. (a) Emotion VQA / caption 자연어, (b) V/A continuous score, (c) Cat34 distribution.

**Loss**. CE (caption) + MSE (V/A) + KL (Cat34 soft).

**Reference**. MindLLM 2025, UMBRAE 2024, Mind Captioning 2025, MedBLIP 2023, BLIP-2 2023, LLaVA 2023.

### Direction 2. Brain-Video Multimodal

**Architecture**. Brain encoder (Brain-JEPA frozen 또는 학습 가능 BFM) + V-JEPA2 video feature + projection head (공통 embedding space) + InfoNCE symmetric contrastive loss.

**Optional**. Subject-invariant 학습 (같은 자극의 다른 subject brain 도 가까워지도록).

**Evaluation**. Variance partitioning. Brain unique variance = Joint - Video-only.

**Reference**. TRIBE 2025, VIBE 2025, CineBrain 2025, Doerig 2024, BraVL 2023.

## 3. Phases

### Phase 1 (완료). Frozen BFM 측정 + Audit

세부는 `archive/v4_20260602/docs/masterplan_v2.md` 의 Phase 1 과 동일. 결과 + audit 은 `reports/phase1_audit_20260604/`.

**결론**. Frozen BFM 이 simple ROI baseline 을 못 넘음. EmoBrain framing 의 motivation.

### Phase 2. Direction 1 (BrainVLM) Pilot

세부는 `ACTION_PLAN.md` Phase 2 의 Action 2.1 ~ 2.3.

**Gate**. V/A Pearson r 가 Phase 1 ROI baseline 보다 의미있게 높으면 Direction 1 main path 확정.

### Phase 3. Direction 2 (Brain-Video Multimodal) Pilot

세부는 `ACTION_PLAN.md` Phase 3 의 Action 3.1 ~ 3.3.

**Gate**. Brain unique variance 가 paired bootstrap p < 0.05 이고 Pearson r 향상 +0.05 이상이면 Direction 2 main path 확정.

### Phase 4. Hackathon Demo (5 일)

5 일 hackathon 의 day-by-day plan. `ACTION_PLAN.md` Phase 4.

### Phase 5. Paper + Submission

- Mixed valence categorization (Vaccaro 2024) 추가 측정.
- Cross-dataset evaluation (Emo-FilM, CineBrain).
- Submission venue 결정.

## 4. Standard Baseline Suite (Phase 1 의 결정 유지)

모든 task 결과는 다음과 함께 reporting.

| Baseline | 측정 상태 |
|----------|-----------|
| Chance (DummyClassifier stratified + most_frequent, DummyRegressor mean + median) | Phase 1 측정 완료 |
| ROI mean + Ridge / Logistic L2 | Phase 1 측정 완료 |
| ROI mean + MLP | Phase 1 측정 완료 |
| Phase 1 best frozen BFM (BJ resting) | Phase 1 측정 완료 |
| Video baseline (Qwen-VL caption / V-JEPA2 pretrained) | Phase 1 측정 완료 |

## 5. Tasks

| Task | Phase 1 측정 | Phase 2+ 계획 |
|------|---------------|----------------|
| V/A Binary | 완료 | Direction 1 + 2 모두 평가 |
| V/A Regression | 완료 | Direction 1 + 2 모두 평가 |
| Cat34 Multilabel (threshold 0.10) | 재측정 진행 중 | Direction 1 + 2 모두 평가 |
| Cat34 Soft Distribution | 재측정 진행 중 | Direction 1 + 2 모두 평가 |
| Mixed Valence Categorization | 미측정 | Direction 1 + 2 모두 평가 |
| Caption Embedding Regression | 미측정 | Direction 1 specific |
| Emotion VQA | 미측정 | Direction 1 specific |

## 6. Data

### Main dataset
- Horikawa naturalistic video fMRI (5 subj × 2185 stim, Cowen 34-cat + 14-dim + V/A continuous rating).

### Phase 5 cross-dataset 확장 후보
- Emo-FilM (continuous V/A on movie clips).
- StudyForrest (Forrest Gump fMRI).
- CineBrain (audiovisual + fMRI + EEG).
- NNDb, Affective Videos (additional).

## 7. Risk + Mitigation

| Risk | Mitigation |
|------|------------|
| Direction 1 의 BrainVLM 이 Phase 2 gate 통과 못 함 (V/A r < ROI) | Prompt template + LoRA position ablation 후 재평가. fail 시 Direction 2 main path 로 통합. |
| Direction 2 의 brain unique variance 가 noise 수준 | Brain encoder 변경 (BJ → ROI mean → fine-tuned 학습) + multi-loss balance 재조정. |
| Horikawa 의 짧은 T 분포 (median 5) 가 두 direction 모두에서 한계 | Cross-dataset 확장으로 더 긴 T 의 자극 확보 (Emo-FilM, CineBrain). |
| Compute quota 한계 | Direction 별 pilot 은 fold 1 만으로 시작. Full grid 는 Phase 5 paper 단계. |

## 8. Branch Strategy

- `main`. v4 framing 의 안정판 (Phase 1 complete + universal code direction). 보존만.
- `v4_20260602_perlmutter`. v4 main + 추가 작업 (subject-invariant SSL pretrain Track A 의 작업물).
- `sj_NEW_20260608_perlmutter`. **current**. EmoBrain framing 의 active branch.
- `archive/v4_20260602/`. v4 의 .md 문서 보존 (이 branch 안에서 reference 용).

## 9. Reference Decisions

세부 결정은 `notes/project_decisions.md` 의 시간순 log.
