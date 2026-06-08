# EmoBrain Action Plan

Branch `sj_NEW_20260608_perlmutter`. Two main directions = BrainVLM + Multimodal Alignment.

이 문서는 ground-level weekly action (어느 .py 파일, 어느 dataset, 어느 GPU job).
High-level (motivation, two axes, tasks) 는 `README.md` 와 `CONTEXT_FEEL.md`.
Forward plan (Direction 별 deliverable + gate) 은 `docs/masterplan_v3_emobrain.md`.

## 한 줄 요약

Direction 1 (BrainVLM) + Direction 2 (Multimodal Alignment) 의 두 axis 를 병행. 5 일 hackathon 단위로 pilot + 평가, 이후 paper.

## 자원 환경

| 자원 | 위치 | 용도 |
|------|------|------|
| Perlmutter GPU | NERSC m4641 (gpu queue, A100 80GB) | Direction 1 LoRA fine-tune, Direction 2 alignment 학습 |
| Perlmutter CPU | NERSC m4641 (cpu queue) | Probe, chance baseline, ROI baseline |
| Python env (general) | `/pscratch/sd/s/sjmoon/tribev2/.venv` | Probe, 분석, Direction 2 |
| Python env (BrainVLM) | `/pscratch/sd/s/sjmoon/brainvlm_qwen_env` | Direction 1 only |
| Data | `/pscratch/sd/s/sjmoon/FEELIN/data/` | Splits, target matrix, stim feature |
| BFM embeddings | `/pscratch/sd/s/sjmoon/FEELIN/output/embeddings/` | Direction 2 의 brain encoder 후보 (Brain-JEPA / SwiFT NewE96 / NeuroSTORM, zero padding) |
| Results | `/pscratch/sd/s/sjmoon/FEELIN/results/` | CSV, figure |

모든 .py 는 .sh 동반 (NERSC SLURM submission).

---

## Background. Phase 1 Benchmark (Completed)

EmoBrain framing 의 evidence base. Frozen BFM 의 한계를 측정으로 확정.

- [x] Brain-JEPA / NeuroSTORM / SwiFT 6 변종 의 zero padding embedding 추출 (5 subj × 2185 stim).
- [x] Linear (sklearn) + MLP (SwiftMLP) probe 의 V/A binary + V/A reg + Cat34 multilabel + Cat34 soft 측정.
- [x] ROI baseline (Schaefer400 + Tian S3 50, time-mean) + chance baseline.
- [x] Phase 1 audit (`reports/phase1_audit_20260604/` 1A-1D).
- [x] Cat34 multilabel threshold 0.10 (= 1/10 raters, 자연 단위) 재측정 + ROI + chance baseline 보강.
- [x] Phase 1 method + result PDF (`reports/phase1_audit_20260604/_pdf/main.pdf`, 10 page).

**핵심 발견**. Frozen BFM (BJ resting 0.738 V_binary AUROC) 이 simple ROI mean baseline (0.789) 을 못 넘음. V/A binary, V/A reg, Cat34 multilabel, Cat34 soft 4 task 모두 일관. 원인은 Horikawa 자극의 짧은 T 분포 (median 5 TR, 71.6% T=5) + BFM input 의 평균 63 ~ 70% zero padding.

이 결과가 Direction 1 + Direction 2 의 motivation.

---

## Direction 1. BrainVLM (Main)

**Goal**. Qwen3-VL backbone 위에 Horikawa fMRI 를 token 으로 주입하는 minimum viable pipeline. Emotion VQA / V/A score / Cat34 distribution 의 multi-task 자연어 + numeric 출력.

### Action 1.1. BrainVLM env + fMRI patchify

- [ ] `/pscratch/sd/s/sjmoon/brainvlm_qwen_env` 환경 verify.
- [ ] UMBRELLA_qwen ABCD-pretrained checkpoint loader (`code/dir1_brainvlm/load_brainvlm.py`).
- [ ] Horikawa fMRI 의 2D ROI-based representation 설계 (Schaefer parcellation 의 2D grid layout, 또는 ROI × time matrix). 코드 `code/dir1_brainvlm/fmri_patchify.py`.
- [ ] Token distribution 분석 (ABCD pretrained 와 Horikawa 의 KL divergence). `results/brainvlm/token_kl.csv`.

### Action 1.2. Emotion VQA prompt + multi-task head

- [ ] Emotion VQA prompt template 설계 (V/A score 자연어 vs special token, Cat34 distribution 출력 형식).
- [ ] Multi-task loss = CE (VQA caption) + MSE (V/A) + KL (Cat34 soft distribution).
- [ ] LoRA target 결정 (vision tower / LLM body / both). 초기는 vision tower + cross-attention.

### Action 1.3. Pilot 학습 + 평가

- [ ] Horikawa fold 1 만 pilot 학습. 5 subj pooled. 코드 `code/dir1_brainvlm/train_pilot.py`.
- [ ] V/A regression / Cat34 multilabel / Cat34 soft 평가, Phase 1 ROI baseline 과 비교.
- [ ] Free-form emotion caption 생성 sample 확인. `results/brainvlm/pilot_metrics.csv` + sample notebook.

### Gate (Direction 1)

- V/A Pearson r 가 Phase 1 ROI baseline (V 0.40, A 0.23) 보다 의미있게 높으면 Direction 1 main path 확정.
- 낮으면 prompt / LoRA position / patchify layout ablation 추가 후 재평가.

---

## Direction 2. Multimodal Alignment (Main)

**Goal**. Brain encoder 와 V-JEPA2 video feature 의 contrastive alignment. Brain unique variance 정량화.

### Action 2.1. Brain encoder 선정

- [ ] 후보 1. Brain-JEPA resting frozen embedding (768-dim). Phase 1 best frozen BFM.
- [ ] 후보 2. ROI mean BOLD (450-dim). Phase 1 best baseline, padding 영향 없음.
- [ ] 후보 3. SwiFT NewE96 resting frozen embedding (768-dim).
- [ ] Pilot 에서는 BJ resting 으로 시작.

### Action 2.2. Video encoder + alignment loss

- [ ] V-JEPA2 pretrained feature (1408-dim, EmoViS symlink). Phase 1 video probe 에서 이미 확인.
- [ ] Brain (768 또는 450) + Video (1408) projection head 로 공통 embedding space (예: 512-dim).
- [ ] InfoNCE symmetric loss 학습. 같은 자극의 brain-video pair 가 다른 자극보다 가까워지도록.
- [ ] Subject-invariant 추가 옵션. 같은 자극의 다른 subject brain 끼리도 가까워지도록.

### Action 2.3. Variance partitioning + emotion task 평가

- [ ] Brain 만 / Video 만 / Joint 의 emotion task 결과 측정 (V/A regression, Cat34 multilabel).
- [ ] Brain unique variance = Joint − Video-only. Paired bootstrap 으로 p-value.
- [ ] Cross-subject generalization (held-out subject) 도 같은 protocol.
- [ ] `results/multimodal/pilot_metrics.csv`.

### Gate (Direction 2)

- Brain unique variance 가 paired bootstrap p < 0.05 이고 절대값이 의미있는 수준 (Pearson r 향상 +0.05 이상) 이면 Direction 2 main path 확정.
- 약하면 brain encoder 후보 변경 + alignment loss 조정.

---

## Hackathon (5 일 demo)

5 일 hackathon 의 day-by-day plan. 발표 / 데모 위주.

| Day | 작업 |
|-----|------|
| 1 | 환경 setup, data pipeline 통합. Direction 1 의 BrainVLM env + Direction 2 의 V-JEPA2 feature 확인. |
| 2 | Direction 1 BrainVLM LoRA fine-tune pilot (fold 1, 5 subj pooled). |
| 3 | Direction 2 Brain + V-JEPA2 contrastive alignment 학습 + brain unique variance 측정. |
| 4 | 평가표 작성 + Gradio web demo + UMAP / heatmap visualization + 발표 자료. |
| 5 | Demo day 발표 |

### Day 4 Demo deliverable

- Web 데모 (Gradio). fMRI 자극 입력 → BrainVLM 의 emotion caption + V/A score 출력.
- 평가표. V/A Pearson r, Cat34 macro AUROC 의 BrainVLM vs Multimodal vs ROI baseline vs chance 4-way 비교.
- Visualization. Brain-video joint embedding 의 UMAP cluster + ROI-wise brain unique contribution heatmap.

---

## Paper + Submission (Hackathon 후)

- [ ] Paper draft. EmoBrain 의 두 axis (BrainVLM + Multimodal) 의 결과 통합.
- [ ] Mixed valence categorization (Vaccaro 2024) 추가 측정.
- [ ] Cross-dataset evaluation (Emo-FilM, CineBrain).
- [ ] Submission venue 결정 (Nature Communications / NeurIPS / Cell Reports / ICLR).

상세 deliverable 은 `docs/masterplan_v3_emobrain.md`.
