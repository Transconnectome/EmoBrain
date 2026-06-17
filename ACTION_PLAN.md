# EmoBrain Action Plan

Branch `sj_NEW_20260608_perlmutter`. Three Directions = D1 BrainVLM + D2 fMRI-LM (main paper) + D3 CCN (workshop 발표 별도).

이 문서는 ground-level weekly action.
High-level (motivation, three directions, tasks) 는 `README.md` 와 `CONTEXT_EMOBRAIN.md`.
Forward plan (Direction 별 deliverable + gate) 은 `docs/masterplan_v3_emobrain.md`.

## 한 줄 요약

D1 + D2 의 2 × 2 grid (2 model × 2 dataset Horikawa + Emo-FilM) 가 main paper. D3 (CCN) 는 별도 workshop 발표 path (Brain-Video alignment + context clustering).

## 자원 환경

| 자원 | 위치 | 용도 |
|------|------|------|
| Perlmutter GPU | NERSC m4641 (gpu queue, A100 80GB) | D1 LoRA, D2 LLM tuning, D3 alignment |
| Perlmutter CPU | NERSC m4641 (cpu queue) | Probe, baseline |
| Python env (general) | `/pscratch/sd/s/sjmoon/tribev2/.venv` | Probe, 분석, D3 alignment pilot |
| Python env (LLM) | `/pscratch/sd/s/sjmoon/brainvlm_qwen_env` | D1 BrainVLM, D2 fMRI-LM 의 LLM 부분 |
| Data (Horikawa) | `/pscratch/sd/s/sjmoon/EmoBrain/project/shared/data/` | Splits, target matrix, stim feature |
| Data (Emo-FilM) | 다운로드 예정 | 두 번째 dataset |
| BFM embeddings | `/pscratch/sd/s/sjmoon/EmoBrain/project/shared/output/embeddings/` | BJ resting/scratch, NS, SwiFT 6 변종 |
| CCN dataset (D3) | `/pscratch/sd/s/sjmoon/EmoBrain/project/dir3_ccn/data/` | 1.8G |
| Results | `/pscratch/sd/s/sjmoon/EmoBrain/project/{dir1,dir2,dir3,shared}/results/` | per-direction CSV, figure |

모든 .py 는 .sh 동반.

---

## Background. Phase 1 Benchmark (Completed, Horikawa)

EmoBrain framing 의 evidence base. Frozen BFM 의 한계를 측정으로 확정.

- [x] Brain-JEPA / NeuroSTORM / SwiFT 6 변종 의 zero padding embedding 추출 (5 subj × 2185 stim).
- [x] Linear + MLP probe 의 V/A binary + V/A reg + Cat34 multilabel + Cat34 soft 측정.
- [x] ROI baseline + chance baseline.
- [x] Phase 1 audit (`docs/reports/phase1_audit_20260604/` 1A-1D).
- [x] Cat34 multilabel threshold 0.10 재측정.
- [x] Phase 1 method + result PDF.

**핵심 발견**. Frozen BFM 이 simple ROI mean baseline 을 못 넘음. D1/D2/D3 의 motivation.

---

## Direction 1. BrainVLM (main paper, 2 dataset)

**Goal**. Qwen3-VL backbone 위에 fMRI 를 token 으로 주입하는 minimum viable pipeline. emotion VQA / V/A / Cat34 distribution 의 multi-task 출력.

### Action 1.1. BrainVLM env + fMRI patchify (Horikawa)

- [ ] `/pscratch/sd/s/sjmoon/brainvlm_qwen_env` 환경 verify.
- [ ] UMBRELLA_qwen ABCD-pretrained checkpoint loader (`project/dir1_brainvlm/code/load_brainvlm.py`).
- [ ] Horikawa fMRI 의 2D ROI-based representation 설계 (`project/dir1_brainvlm/code/fmri_patchify.py`).
- [ ] Token distribution 분석.

### Action 1.2. Emotion VQA prompt + multi-task head

- [ ] Prompt template 설계 (V/A 자연어 vs special token, Cat34 distribution 출력 형식).
- [ ] Multi-task loss = CE (caption) + MSE (V/A) + KL (Cat34 soft).
- [ ] LoRA target 결정.

### Action 1.3. Pilot 학습 + 평가 (Horikawa)

- [ ] Horikawa fold 1 pilot 학습 (5 subj pooled).
- [ ] V/A regression / Cat34 multilabel / Cat34 soft 평가, Phase 1 ROI baseline 비교.
- [ ] Free-form emotion caption sample.

### Action 1.4. Emo-FilM 적용

- [ ] Emo-FilM 다운로드 + preprocessing.
- [ ] 동일 pipeline 으로 학습 + 평가.
- [ ] 두 dataset 의 결과 비교 (cross-dataset generalization).

### Gate (D1)

V/A Pearson r 가 Phase 1 ROI baseline (V 0.40, A 0.23) 보다 의미있게 높으면 main path 확정.

---

## Direction 2. fMRI-LM (main paper, 2 dataset)

**Goal**. fMRI-LM (Wei 2026, arXiv 2511.21760) architecture 를 차용한 emotion-specific brain LM. Brain-JEPA-like tokenizer + GPT-2/Qwen3 LLM + SigLIP + GRL + F2F+F2T+T2T 3-objective tuning.

### Action 2.1. fMRI-LM checkpoint + architecture 확보

- [ ] fMRI-LM (Wei 2026) 의 official checkpoint / repo 존재 확인 (arXiv 2511.21760).
- [ ] 우리 환경 호환성 (Schaefer-400+Tian-50 ROI, T=160 vs Horikawa T=5 median 차이).
- [ ] 차용 가능 여부 + 적용 방법 (직접 weight load vs scratch 재구현).

### Action 2.2. Stage 1. fMRI tokenizer

- [ ] Brain-JEPA-like ViT + Vector Quantizer 의 fMRI → discrete token.
- [ ] Synthetic descriptor corpus 합성 (Horikawa 의 V/A + Cat34 + Qwen-VL caption → template + LLM rewrite).
- [ ] SigLIP contrastive + GRL domain-adversarial loss 로 fMRI token ↔ text embedding 정렬.

### Action 2.3. Stage 2. LLM fine-tuning

- [ ] GPT-2 또는 Qwen3-0.6B backbone 선택.
- [ ] F2F (fMRI next-step) + F2T (fMRI → text) + T2T (random text LM, catastrophic forgetting 방지) 3-objective.
- [ ] Loss balance L_F2T + 0.1 L_F2F + 0.5 L_T2T.

### Action 2.4. Stage 3. Instruction tuning + emotion task 평가

- [ ] Single-Q/A + multi-Q/A + open-ended 3 paradigm + LoRA.
- [ ] V/A regression, Cat34 multilabel, Cat34 soft 평가, Phase 1 ROI baseline 비교.

### Action 2.5. Emo-FilM 적용

- [ ] Emo-FilM 으로 동일 pipeline 적용 (D1 의 Action 1.4 와 병렬).
- [ ] 두 dataset 결과 비교.

### Gate (D2)

V/A Pearson r 가 Phase 1 ROI baseline 보다 의미있게 높음 + D1 BrainVLM 과의 비교 (어느 architecture 가 emotion 잡는데 더 적합).

---

## Direction 3. CCN. Brain-Video Alignment + Context Clustering (workshop 발표, 별도 axis)

**위치**. `project/dir3_ccn/` (이전 CCN_Emotion + alignment_pilot + legacy_phase2 통합).

**Goal**. Video model 의 embedding 으로 learning clustering → context 반영된 clustering → brain 이 그 context 학습. **같은 emotion (예: joy) 안에서 context 별 sub-cluster 가 brain 표상에서도 나타나는지** 검증.

### Action 3.1. Alignment pilot (현재 진행)

- [x] BrainVideoDataset + ProjBrain/ProjVideo + SigLIP + GRL scaffolding 완료.
- [x] Local smoke test PASS.
- [ ] **Pilot 학습 launch** (sbatch, fold 1, BJ resting + scratch 2 variant, 약 30 분/variant).
  - 위치. `project/dir3_ccn/code/alignment_pilot/scripts/train_pilot_{resting,scratch}.sh`
- [ ] Variance partitioning (Brain-only / Video-only / Joint) emotion task 평가.

### Action 3.2. Context clustering 학습

- [ ] V-JEPA2 embedding 위 learning clustering. cluster 가 context 를 반영하는지.
- [ ] 같은 emotion (1 개 선택, 예: joy) 안에서 context 별 sub-cluster emergence 검증.
- [ ] Brain 이 그 context cluster 를 학습할 수 있는지.

### Action 3.3. Independent dataset transfer

- [ ] Emo-FilM 또는 CCN 의 별도 dataset 으로 동일 clustering 검증.
- [ ] Cross-dataset universal context structure 확인.

### Gate (D3)

Cluster emergence + cross-dataset preservation 의미있게 보이면 CCN workshop poster. 결과 강하면 paper 까지.

---

## Hackathon (5 일 demo, 별도)

별도 진행. D1 + D2 의 minimal pilot + 발표.

상세는 `docs/masterplan_v3_emobrain.md` 의 Hackathon section.

---

## Paper + Submission

- [ ] Paper draft. D1 + D2 의 2 × 2 grid (2 model × 2 dataset) 결과 통합.
- [ ] Task 3 종류 (공통 언어 + 공통 새 task + 개별 특화) 결과.
- [ ] Cross-dataset evaluation (Horikawa ↔ Emo-FilM).
- [ ] Submission venue 결정.

상세는 `docs/masterplan_v3_emobrain.md`.
