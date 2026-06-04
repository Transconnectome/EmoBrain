# FEEL Action Plan (v4 final, 2026-06-02)

Branch `v4_20260602_perlmutter`. Big Q = universal emotion code 의 존재 검증.

이 문서는 ground-level weekly action (어느 .py 파일, 어느 dataset, 어느 GPU job).
High-level (Big Q, sub-claim, tracks, go-no-go) 는 [`docs/masterplan_v2.md`](docs/masterplan_v2.md).

## 한 줄 요약

Track A (BFM SSL pretrain + LoRA) + Track B (Brain+Video framework reuse + task 재설계) 를 main, Track C (BrainVLM parsing fix) 를 supplementary 로 병행. paper + submission.

## 자원 환경

| 자원 | 위치 | 용도 |
|---|---|---|
| Perlmutter GPU | NERSC m4641 cpu/gpu queue | Track A SSL pretrain, Track B 학습, Track C parsing |
| Python env | `/pscratch/sd/s/sjmoon/tribev2/.venv` | Track A/B/C |
| BrainVLM env | `/pscratch/sd/s/sjmoon/brainvlm_qwen_env` | Track C only |
| Data | `/pscratch/sd/s/sjmoon/FEEL/data/` | Splits, stim features |
| BFM embeddings | `/pscratch/sd/s/sjmoon/FEEL/output/embeddings/` | Brain-JEPA / SwiFT / NeuroSTORM (proper mean) |
| Results | `/pscratch/sd/s/sjmoon/FEEL/results/` | CSV / figure |
| Independent datasets | `/pscratch/sd/s/sjmoon/FEEL/data/independent/` (NEW) | Emo-FilM / StudyForrest / NNDb / Affective Videos |

모든 .py 는 .sh 동반 (NERSC SLURM submission, [[feedback_always_make_sh]]).

---

## Phase 3a (Track C supplementary). BrainVLM parsing fix only

추가 학습 없음. Phase 3a fold 1 inference parsing fix 만.

### Action 1. Inference parsing fix

**파일**. `code/brainvlm/inference_brainvlm.py`, `code/brainvlm/inference_brainvlm.sh`
**문제**. 현재 fold 1 inference V_reg r = NaN, MAE 2.55. XML parsing failure 의심.
**작업**.
- [ ] `<Valence>X</Valence>` regex 의 failure 모드 진단
- [ ] Scale mismatch (prompt 1-5 vs Cowen 1-9) 의 prompt 수정 또는 inverse mapping
- [ ] Re-inference on fold 1 test set
- [ ] V_reg r, A_reg r, MAE 결과 reporting
**Deliverable**. `results/brainvlm/fold1_test_preds_metrics_fixed.csv`, Supplementary figure (Appendix only).
**자원**. GPU (low) (re-inference 2-3 시간 + figure).

---

## Phase 3b (Track A main). BFM SSL pretrain + LoRA adaptation

### Foundation prep

**Action 0. Standard baseline suite (모든 task 의 의무)**

새 task 학습 결과의 *맥락* 을 만들기 위한 표준 baseline. 모든 main result 와 *반드시 함께* 보고. Phase 1 의 일부 baseline 은 이미 측정 (CSV 보존).

| Baseline | 목적 | Pipeline |
|---|---|---|
| **Chance / Label permutation** | Null distribution, p-value 계산 | Label shuffle → same training → empirical null (100 permutation) |
| **Class proportion (majority)** | 최소 floor | Most-frequent-class predictor (classification) / mean predictor (regression) |
| **ROI mean + Ridge** | Linear regression baseline | 450 ROI mean time-series → L2 ridge regression |
| **ROI mean + Logistic** | Binary classification baseline | 450 ROI mean → L2 logistic regression |
| **ROI mean + Multinomial logistic** | Multi-class baseline (34-cat top-1) | 450 ROI mean → multinomial logistic |
| **ROI mean + Multi-output Ridge** | Multi-target baseline (14-dim, 34-cat soft) | 450 ROI mean → multi-output ridge |
| **Random Forest on ROI** | Nonlinear baseline | 450 ROI mean → 500-tree RF |
| **Phase 1 best BFM frozen** | BFM baseline (no SSL pretrain) | Brain-JEPA resting zero linear (V_binary 0.7402, 이미 측정) |
| **Video baseline (CLIP)** | Group-level emotion ceiling | CLIP_pretrained frozen + linear head (V_binary 0.9708, 이미 측정) |

Optional advanced baseline (시간 되면).
- SVM on ROI mean (RBF kernel)
- Network-restricted (Schaefer 17-network 별) + ridge
- Voxel-wise ridge with stability selection

**작업**.
- [ ] `code/baselines/baseline_suite.py`. 9 baseline 일괄 학습 pipeline
- [ ] `code/baselines/baseline_suite.sh`. SLURM submission
- [ ] Standardized output format. `results/baselines/{task}_{baseline}_{dataset}.csv` (metric, fold, seed 별)
- [ ] Permutation test 의 null distribution generator
- [ ] Standardized report template. 모든 main result 옆에 baseline column

**파일**. `code/baselines/baseline_suite.py` + `.sh`, `code/baselines/_lib_baselines.py`
**Deliverable**. `results/baselines/` 의 standardized CSV + `reports/baseline_reference.md` (Phase 1 result 와 통합 표)
**자원**. CPU (medium, 모든 baseline 학습. parallel 가능)

**Action 1. Independent dataset 다운로드**
- [ ] Emo-FilM (OpenNeuro `ds004982`). 30 subj × 14 films
- [ ] StudyForrest (OpenNeuro `ds000113`). 20 subj × Forrest Gump 2h
- [ ] NNDb (OpenNeuro `ds002837`). 86 subj × 10 movies
- [ ] Affective Videos (OpenNeuro `ds000205`). 11 subj × 32×4 trials
- [ ] BIDS validation 각 dataset
**파일**. `code/cross_dataset/download_independent.sh`, `data/independent/`
**Deliverable**. 4 dataset 의 BIDS 구조 + metadata table
**자원**. 다운로드 1-2 일 (NERSC scratch 100GB+ 필요)

**Action 2. Preprocessing pipeline 통일**
- [ ] Schaefer-400 + Tian-50 parcel 추출 (4 dataset 동일)
- [ ] Time series 추출 (TR 별 정렬 + slice timing correction)
- [ ] Robust scaling (Brain-JEPA preprocessing 과 동일)
**파일**. `code/cross_dataset/preprocess_independent.py` + .sh
**Deliverable**. `data/independent/{dataset}/parcels.npz`
**자원**. CPU (medium) (parallel 가능)

**Action 3. ComBat harmonization wrapper**
- [ ] Fortin 2018 ComBat 구현 (또는 `neuroCombat` 사용)
- [ ] Site = dataset, covariate = age / sex / TR
- [ ] Multi-site 적용 후 effect plot
**파일**. `code/cross_dataset/combat_wrapper.py` + .sh
**Deliverable**. `data/independent/{dataset}/parcels_combat.npz`
**자원**. CPU (low)

**Action 4. Acquisition null baseline generator**
- [ ] Phase-scrambled brain signal (spectral 유지, emotion 구조 제거)
- [ ] Trivial ROI mean encoder (acquisition mismatch 만 통과)
**파일**. `code/cross_dataset/null_baseline.py`
**Deliverable**. `data/independent/{dataset}/null_phase_scrambled.npz`, `null_roi_mean.npz`
**자원**. CPU (low)

### SSL pretrain (1) Subject-invariant

**Action 5. Subject-invariant SSL 학습 코드**
- [ ] InfoNCE loss. positive = same stim 의 다른 subject, negative = 다른 stim
- [ ] Brain-JEPA backbone 위에 학습
- [ ] Horikawa 5 subj × 2185 stim 의 (stim, subj_A, subj_B) triplet
- [ ] Temperature, hard negative sampling ablation
**파일**. `code/ssl_pretrain/subject_invariant.py` + .sh
**Deliverable**. `output/ssl_pretrain/subject_invariant_checkpoint.pt`
**자원**. GPU (medium)

**Action 6. Subject alignment metric 측정**
- [ ] 학습 후 같은 stim 의 subject 간 representation 의 cosine similarity
- [ ] Pre-pretrain baseline 과 비교
- [ ] ROI-wise alignment map
**파일**. `code/ssl_pretrain/eval_subject_alignment.py` + .sh
**Deliverable**. `results/phase3_universal_code/track_a/subject_alignment.csv`, figure
**자원**. GPU (low)

### SSL pretrain (2) Multi-source masked AE (병행)

**Action 7. Multi-source dataloader**
- [ ] 4 dataset (Horikawa + Emo-FilM + StudyForrest + Affective Videos) 통합 dataloader
- [ ] Dataset 별 token (헤더)
- [ ] Per-batch dataset mixing
**파일**. `code/ssl_pretrain/_lib_dataloader.py`
**Deliverable**. Dataloader test passing
**자원**. CPU (low)

**Action 8. Multi-source masked AE 학습 코드**
- [ ] 450 ROI 중 30% mask
- [ ] MSE reconstruction
- [ ] Brain-JEPA backbone 위에
- [ ] Single-source (Horikawa only) vs multi-source 비교
**파일**. `code/ssl_pretrain/multi_source_masked.py` + .sh
**Deliverable**. `output/ssl_pretrain/multi_source_masked_checkpoint.pt`, `output/ssl_pretrain/single_source_masked_checkpoint.pt`
**자원**. GPU (high)

**Action 9. Paradigm alignment metric 측정**
- [ ] Horikawa vs Emo-FilM vs StudyForrest 의 같은 emotion category 의 RDM
- [ ] Multi-source vs single-source 의 cross-dataset RDM correlation 차이
**파일**. `code/ssl_pretrain/eval_paradigm_alignment.py` + .sh
**Deliverable**. `results/phase3_universal_code/track_a/paradigm_alignment.csv`, figure
**자원**. GPU (low)

### SSL pretrain (3) Brain-stimulus contrastive (optional)

**Action 10. Brain-stimulus contrastive 학습 코드 (가능하면)**
- [ ] Brain encoder output ↔ V-JEPA2 feature 의 contrastive
- [ ] EmoViS 의 V-JEPA2 추출본 reuse
**파일**. `code/ssl_pretrain/brain_stimulus_contrastive.py` + .sh
**Deliverable**. `output/ssl_pretrain/brain_stimulus_checkpoint.pt`
**자원**. GPU (low)

### LoRA adaptation + emotion-text space

**Action 11. Emotion-text space loader (3 후보 ablation)**

3 emotion-text encoder 를 모두 추출해서 ablation 으로 비교. Default 는 mpnet-base.

| 후보 | 모델 | 특징 |
|---|---|---|
| **Default** | sentence-transformers/all-mpnet-base-v2 | Generic semantic, 768-d. 표준 |
| **Vision-language** | CLIP-text ViT-L/14 (openai/clip-vit-large-patch14) | Video-text joint pretrain. Cowen evoked-emotion paradigm 과 자연 match |
| **Emotion-specialized** | LEIA/LEIA-LM-base (Aroyehun et al. 2023 EPJ Data Science) | BERTweet 기반, 6.3M Vent post 로 emotion-aware masked pretrain |

- [ ] 3 encoder 각각 frozen 로딩
- [ ] Cowen 34-cat 의 문장화 (e.g. "a video that evokes admiration")
- [ ] Cowen 14-dim 의 문장화
- [ ] OV description (전략 3 의 출력)
- [ ] 3 encoder × 3 target (34cat / 14dim / OV) = 9 embedding 셋트
**파일**. `code/cross_dataset/emotion_text_space.py`
**Deliverable**. `data/emotion_text_space/{mpnet, clip, leia}_{34cat, 14dim, ov}_embeddings.npz`
**자원**. GPU (medium, embedding 생성)

**Action 12. LoRA adaptation 학습 (Linear + MLP 둘 다 ablation)**

Phase 1 finding 에서 frozen probe 의 표준 = Linear > MLP. 우리 setup 은 LoRA + contrastive 라 다를 수 있어 ablation.

- [ ] SSL pretrained backbone + LoRA (rank 8 default, ablation 16)
- [ ] **Projection head ablation**. (a) Linear (768 → 256) = default. (b) MLP (2-layer, hidden 512, ReLU, dropout 0.1)
- [ ] Loss = α InfoNCE (brain ↔ emotion-text) + β V/A regression + γ 34-cat regression + δ soft KL + ε caption baseline Δ
- [ ] Default α=1.0, β=0.1, γ=0.5, δ=0.3, ε=0.0
- [ ] Caption baseline confound control. ε=0.1 ablation (Doerig 2025)
- [ ] 3 emotion-text encoder × 2 projection head = 6 condition × backbone (BFM)
**파일**. `code/cross_dataset/adapt_lora.py` + .sh
**Deliverable**. `output/cross_dataset/lora_{encoder}_{head}_checkpoint.pt` × 6
**자원**. GPU (high, multiple ablation condition)

### Universal code 평가 (4 cross-dataset 전략)

**Action 13. 전략 1. Shared text-embedding zero-shot**
- [ ] Brain → emotion-text space 사영
- [ ] Native label 이름으로 zero-shot retrieval
- [ ] Top-1 / top-5 accuracy, mean reciprocal rank
- [ ] 4 dataset 각각 + multi-source pooled
**파일**. `code/cross_dataset/eval_strategy1_zero_shot.py` + .sh
**Deliverable**. `results/phase3_universal_code/track_a/strategy1_zero_shot.csv`
**자원**. GPU 1-2 일

**Action 14. 전략 2. Label-space intersection**
- [ ] Emo-FilM 13-discrete + 42 CPM 의 Cowen 34-cat closest mapping
- [ ] StudyForrest V/A
- [ ] Within-dataset Pearson r
**파일**. `code/cross_dataset/eval_strategy2_intersection.py` + .sh
**Deliverable**. `results/phase3_universal_code/track_a/strategy2_intersection.csv`
**자원**. GPU (low)

**Action 15. 전략 3. MLLM universal annotator (OV-MER local LLM)**
- [ ] Qwen2.5-72B-VL 또는 Llama-3.3-70B-VL setup
- [ ] OV-MER 의 CLUE-Multi generation prompt 그대로
- [ ] Horikawa 2185 + Emo-FilM + StudyForrest + NNDb 의 video 에 적용
- [ ] Set-based F-score
- [ ] Frozen artifact 로 release
**파일**. `code/cross_dataset/ov_mer_pipeline.py` + `eval_strategy3_mllm.py` + .sh
**Deliverable**. `results/phase3_universal_code/track_a/ov_labels_{dataset}.jsonl`, `strategy3_mllm.csv`
**자원**. GPU (low) (LLM forward)

**Action 16. 전략 4. RSA / ISC ceiling (label-free)**
- [ ] Brain RDM (Schaefer-400 ROI-wise) per dataset
- [ ] Cross-dataset RDM correlation
- [ ] NNDb 의 86 subj × 10 movies 에 적용
- [ ] ISC ceiling (subject 간 brain signal correlation)
**파일**. `code/cross_dataset/eval_strategy4_rsa.py` + .sh
**Deliverable**. `results/phase3_universal_code/track_a/strategy4_rsa.csv`, figure
**자원**. CPU (low)

**Action 17. ROI-wise transfer matrix**
- [ ] Schaefer-400 17-network 별 transfer 성능
- [ ] Transmodal vs sensory 비교
**파일**. `code/cross_dataset/eval_roi_wise.py` + .sh
**Deliverable**. `results/phase3_universal_code/track_a/roi_wise_transfer.csv`, heatmap
**자원**. CPU (low)

**Action 18. Acquisition null 2σ 검증**
- [ ] 모든 transfer 결과를 acquisition null 의 2σ 와 비교
- [ ] Prespecified 한 threshold 위만 의미 있다고 reporting
**파일**. `code/cross_dataset/eval_null_check.py`
**Deliverable**. `results/phase3_universal_code/track_a/null_check.csv`
**자원**. CPU (low)

**Action 19. Caption baseline variance partitioning**
- [ ] Qwen-VL caption → text embedding probe → B_caption
- [ ] Brain-only B_brain
- [ ] Joint B_joint
- [ ] Brain unique = B_joint - B_caption
- [ ] Paired bootstrap p
**파일**. `code/cross_dataset/eval_caption_baseline.py` + .sh
**Deliverable**. `results/phase3_universal_code/track_a/caption_baseline.csv`, figure
**자원**. GPU 1-2 일

**Action 20. Phase 3b 보고서 (Track A)**
- [ ] LaTeX `reports/phase3b_track_a/main.tex`
- [ ] Sub-claim 1-4 별 evidence summary
- [ ] All figures + tables
**파일**. `reports/phase3b_track_a/main.tex`, `figs/`
**Deliverable**. `reports/phase3b_track_a/main.pdf`
**자원**. CPU (low)

---

## Phase 3c (Track B main). Brain+Video framework + task 재설계 ( 병행)

### Task 재설계

**Action 21. Universal code probe task design**
- [ ] Task 1. Cross-dataset emotion-text alignment. Brain → emotion-text space 의 사영
- [ ] Task 2. Same-emotion RDM preservation. 같은 emotion 의 다른 source 의 brain RDM 비교
- [ ] Task 3. ROI-wise universal map. ROI 별 invariance
- [ ] Phase 2 의 _lib.py 의 task type 확장
**파일**. `code/phase2/task_universal_code.py`
**Deliverable**. Task loader test passing
**자원**. CPU (low)

### Brain unique cross-dataset preservation

**Action 22. Universal code probe task 학습 (Phase 2 framework reuse)**
- [ ] 4 architecture (A/B/C/D) × universal code probe task
- [ ] Brain-only vs Brain+Video joint 비교
- [ ] Acquisition control 적용
**파일**. `code/phase2/train_universal_code_joint.py` + .sh
**Deliverable**. `results/phase3_universal_code/track_b/joint_vs_brainonly.csv`
**자원**. GPU (medium)

**Action 23. Cross-dataset preservation 측정**
- [ ] Brain unique (joint - video) 의 cross-dataset RSA
- [ ] Track A 의 invariance metric 과 cross-reference
**파일**. `code/phase2/eval_cross_dataset_preservation.py` + .sh
**Deliverable**. `results/phase3_universal_code/track_b/cross_dataset_rsa.csv`, figure
**자원**. CPU (low)

**Action 24. Phase 3c 보고서 (Track B)**
- [ ] LaTeX `reports/phase3c_track_b/main.tex`
- [ ] Brain unique cross-dataset preservation evidence
**파일**. `reports/phase3c_track_b/main.tex`, `figs/`
**Deliverable**. `reports/phase3c_track_b/main.pdf`
**자원**. CPU (low)

---

## Phase 4 (Synthesis + submission, )

### Cross-evaluation + integration

**Action 25. Track A + Track B 통합 표**
- [ ] Universal code evidence 통합 (Track A invariance metric + Track B cross-dataset preservation)
- [ ] Sub-claim 1-4 별 verdict
**Deliverable**. `reports/phase4_integration/integration_table.csv`, summary figure
**자원**. CPU (low)

**Action 26. EmoViS branch 결과 통합 검토**
- [ ] EmoViS 의 cortical gradient + cross-modal alignment 결과와 FEEL 의 universal code evidence 의 cross-reference
**Deliverable**. `reports/phase4_integration/feelin_emovis_alignment.md`
**자원**. CPU (low)

### Paper draft

**Action 27. Paper draft**
- [ ] LaTeX `Paper/main.tex`
- [ ] Methods + Results + Discussion
- [ ] Skill `scientific-writing` + `peer-review` 사용
**Deliverable**. `Paper/main.pdf` v1.0
**자원**. CPU + 사용자 작업

### Infographic + README + code release

**Action 28. Infographic**
- [ ] Skill `infographics` 사용
- [ ] Big Q → Track A/B → 결과 → submission
**Deliverable**. `figures/infographic/feelin_overview.png`

**Action 29. README + code release v1.0**
- [ ] README.md final
- [ ] Code release tag `v1.0-submission`
**자원**. CPU (low)

### Submission

**Action 30. Submission target 결정**
- [ ] Skill `scholar-evaluation` 사용
- [ ] Nat Hum Behav / Nat Commun / NeurIPS / Imaging Neuroscience 중 결정
**Deliverable**. `docs/submission_target.md`, submission PDF

---

## Agent review schedule (masterplan 의 Section 10)

| Phase | Agent | Focus |
|---|---|---|
| | emovi-method-critic | Build recipe + SSL pretrain 1+2+3 + ComBat 적정성 |
| | scientific-critical-thinking | Multi-source SSL invariance metric statistical 적절성 |
| | emovi-method-critic | Subject-invariant SSL contrastive loss confound + Track B task equivalence |
| | chavis-antisyc | 결과 over-claim 방지 |
| | peer-review + chavis-antisyc | Track A/B 종합 over-claim |
| | scientific-writing | Draft writing |
| | peer-review + emovi-review | Manuscript review |
| | scholar-evaluation | Venue 결정 |

---

## Critical dependency

- Action 1 (independent dataset 다운로드) → Action 2-4 (preprocessing) → Action 5-12 (SSL + adaptation) → Action 13-19 (cross-dataset eval)
- Action 7 (multi-source dataloader) → Action 8 (multi-source SSL)
- Action 11 (emotion-text space) → Action 12 (LoRA adaptation)
- Action 21 (universal code probe task) → Action 22 (Brain+Video framework reuse)
- Action 20, 24 (Phase 3b/3c 보고서) → Action 25 (integration)

## Risk + mitigation

| Risk | Mitigation |
|---|---|
| Emo-FilM / StudyForrest 다운로드 못 함 | OpenNeuro API + scratch 100GB+ allocation 사전 확보 |
| Multi-source SSL collapse | Hard negative sampling + temperature tuning + LoRA rank ablation |
| Cross-dataset acquisition confound | Action 18 의 null check 의무 |
| Caption baseline 이 brain-only equivalent | Action 19 의 variance partitioning 의 negative result 도 정직 reporting |
| 6 month 안에 Track A SSL 1+2+3 전부 못 함 | Priority 1 (subject-invariant + multi-source masked) 만 보장. (3) brain-stimulus 가능하면 |
| BrainVLM parsing fix 후에도 결과 약함 | Track C 의 supplementary 위치 유지, paper 의 Appendix 만 |

## Tracker

- 진행 상황은 `reports/weekly/{YYYY-MM-DD}.md` 에 weekly 기록
- 매주 끝 `[weekly status]` trigger 로 update
- `notes/project_decisions.md` 에 framing pivot 결정 발생 시 entry 추가

---

## Phase 5 (Future Extensions, post-submission)

v4 main paper submission  후 시작. 자세히 `docs/masterplan_v2.md` Section 14.

### Extension 1. Context-aware emotion (text 형식)

**Action 31. Context-text embedding 추출 pipeline**
- [ ] StudyForrest narrative description / subtitle 추출
- [ ] Emo-FilM scene caption (Qwen-VL 또는 BLIP-2 로 video → text)
- [ ] 추출된 text 를 sentence-transformer 로 embedding (emotion-text space 와 같은 space)
**파일**. `code/context_aware/text_extraction.py`, `code/context_aware/text_embedding.py`
**Deliverable**. `data/context/{dataset}/text_embeddings.npz`
**자원**. GPU (medium) (Qwen-VL caption 생성)

**Action 32. Universal × Context decomposition**
- [ ] Brain RDM 의 partial RSA. Universal code RDM 과 Context-text RDM 의 partial contribution
- [ ] Same-stimulus 의 narrative position 별 brain trajectory 분해
**파일**. `code/decomposition/partial_rsa.py`
**Deliverable**. `results/phase5_context/partial_rsa.csv`, figure
**자원**. CPU (medium)

### Extension 2. Individual differences

**Action 33. Subject embedding 추가 학습**
- [ ] TRIBE v2 / Défossez 2023 style. 각 subject 별 learnable vector
- [ ] Brain encoder 의 input/output 에 concat 또는 modulation
- [ ] Universal code × subject embedding 으로 subject-conditioned emotion
**파일**. `code/individual_diff/subject_embedding.py`
**Deliverable**. `output/individual_diff/subject_embedding_checkpoint.pt`
**자원**. GPU (medium)

**Action 34. Residual analysis pipeline**
- [ ] Track A 의 subject-invariant SSL representation 의 *non-aligned residual*
- [ ] Residual axis 의 subject 별 PCA
- [ ] Subject 별 행동 metric (Cowen 34-cat rating 분포의 차이) 와 residual axis correlation
**파일**. `code/individual_diff/residual_pca.py`
**Deliverable**. `results/phase5_individual_diff/residual_analysis.csv`, figure
**자원**. CPU (low)

### Action 35. Extension paper (v5) draft

- [ ] v5 paper draft. Universal code + Context-aware + Individual differences 의 통합
- [ ] 4 component 분해 schema 의 evidence
**파일**. `Paper_v5/main.tex`
**Deliverable**. `Paper_v5/main.pdf`
**자원**. CPU + 사용자 작업

---

## Phase priority summary

| Phase | Time | Tracks | Status |
|---|---|---|---|
| Phase 1 | | Foundation (frozen probe) | ✅ 완료 |
| Phase 2 | | 통합 학습 (4 architecture + brain-only) | ✅ 측정 완료 |
| Phase 3a | | BrainVLM (Track C supp) | 🔄 parsing fix |
| Phase 3b | | Track A SSL pretrain + LoRA | 🆕 v4 main |
| Phase 3c | | Track B Brain+Video framework | 🆕 v4 main |
| Phase 4 | | Synthesis + submission | 대기 |
| Phase 5 | post-submission | Context-aware + Individual differences | 🔮 v5 |

