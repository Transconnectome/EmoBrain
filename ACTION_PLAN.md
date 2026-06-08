# EmoBrain Action Plan

Branch `sj_NEW_20260608_perlmutter`. Two main directions = BrainVLM + Brain-Video Multimodal.

이 문서는 ground-level weekly action (어느 .py 파일, 어느 dataset, 어느 GPU job).
High-level (motivation, two axes, tasks) 는 `README.md` 와 `CONTEXT_FEEL.md`.
Forward plan (Phase 별 deliverable + gate) 은 `docs/masterplan_v3_emobrain.md` (작성 예정).

## 한 줄 요약

Direction 1 (BrainVLM) + Direction 2 (Brain-Video Multimodal) 의 pilot 학습 + emotion task 평가 까지 5 일 hackathon 단위로 진행 후 paper 작성.

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

## Phase 1 (완료). Frozen BFM 측정 + Audit

Phase 1 의 결론: frozen BFM 이 simple ROI baseline 을 넘지 못함. Direction 1 + 2 의 motivation 확정.

- [x] Brain-JEPA / NeuroSTORM / SwiFT 6 변종 의 zero padding embedding 추출 (5 subj × 2185 stim).
- [x] Linear (sklearn) + MLP (SwiftMLP) probe 의 V/A binary + V/A reg + Cat34 multilabel + Cat34 soft 측정.
- [x] ROI baseline (Schaefer400 + Tian S3 50, time-mean) + chance baseline.
- [x] Phase 1 audit (`reports/phase1_audit_20260604/` 1A-1D).
- [x] Cat34 의 ROI + chance baseline 보강 launch (`cat34_probe_ROI_linear.csv`, `chance_cat34.csv`).
- [ ] Cat34 threshold 0.10 (= 1/10 raters, 자연 단위) 재측정 진행 중. `cat34_*_t010.sh` launch 됨. 결과 정리 + PDF 업데이트 대기.

---

## Phase 2. Direction 1 (BrainVLM) Pilot

**Goal**. Qwen3-VL backbone 위에 Horikawa fMRI 를 token 으로 주입하는 minimum viable pipeline 구축. Emotion VQA / V/A score / Cat34 distribution 의 multi-task 출력.

### Action 2.1. BrainVLM env + fMRI patchify

- [ ] `/pscratch/sd/s/sjmoon/brainvlm_qwen_env` 환경 verify.
- [ ] UMBRELLA_qwen ABCD-pretrained checkpoint loader (`code/brainvlm/load_brainvlm.py`).
- [ ] Horikawa fMRI 의 2D ROI-based representation 설계 (Schaefer parcellation 의 2D grid layout, 또는 ROI × time matrix). 코드 `code/brainvlm/fmri_patchify.py`.
- [ ] Token distribution 분석 (ABCD pretrained 와 Horikawa 의 KL divergence). `results/phase2/brainvlm_token_kl.csv`.

### Action 2.2. Emotion VQA prompt + multi-task head

- [ ] Emotion VQA prompt template 설계 (V/A score 자연어 vs special token, Cat34 distribution 출력 형식).
- [ ] Multi-task loss = CE (VQA caption) + MSE (V/A) + KL (Cat34 soft distribution).
- [ ] LoRA target 결정 (vision tower 만 / LLM body 만 / both). 초기는 vision tower + cross-attention 만.

### Action 2.3. Pilot 학습 + 평가

- [ ] Horikawa fold 1 만 pilot 학습. 5 subj pooled. 코드 `code/brainvlm/train_pilot.py`.
- [ ] V/A regression / Cat34 multilabel / Cat34 soft 평가, ROI baseline 과 비교.
- [ ] Free-form emotion caption 생성 sample 확인. `results/phase2/brainvlm_pilot_metrics.csv` + sample notebook.

### Gate (Phase 2)

- V/A Pearson r 가 Phase 1 ROI baseline (V 0.40, A 0.23) 보다 의미있게 높으면 Direction 1 main path 로 확정.
- 낮으면 prompt / LoRA position / patchify layout 의 ablation 추가 후 재평가.

---

## Phase 3. Direction 2 (Brain-Video Multimodal) Pilot

**Goal**. Brain encoder 와 V-JEPA2 video feature 의 contrastive alignment 학습. Brain unique variance 정량화.

### Action 3.1. Brain encoder 선정

- [ ] 후보 1. Brain-JEPA resting frozen embedding (768-dim). Phase 1 의 best frozen BFM.
- [ ] 후보 2. ROI mean BOLD (450-dim). Phase 1 의 best baseline. 단순하지만 padding 영향 없음.
- [ ] 후보 3. SwiFT NewE96 resting frozen embedding (768-dim).
- [ ] Phase 3 pilot 에서는 BJ resting 으로 시작.

### Action 3.2. Video encoder + alignment loss

- [ ] V-JEPA2 pretrained feature (1408-dim, EmoViS symlink). Phase 1 video probe 에서 이미 확인.
- [ ] Brain (768) + Video (1408) projection head 로 공통 embedding space (예: 512-dim).
- [ ] InfoNCE symmetric loss 학습. 같은 자극의 brain-video pair 가 다른 자극보다 가까워지도록.
- [ ] Subject-invariant 추가 옵션. 같은 자극의 다른 subject 의 brain 끼리도 가까워지도록 (multi-loss).

### Action 3.3. Variance partitioning + emotion task 평가

- [ ] Brain 만 / Video 만 / Joint 의 emotion task 결과 측정 (V/A regression, Cat34 multilabel).
- [ ] Brain unique variance = Joint − Video-only. Paired bootstrap 으로 p-value.
- [ ] Cross-subject generalization (held-out subject) 도 같은 protocol 로 측정.
- [ ] `results/phase3/multimodal_pilot_metrics.csv`.

### Gate (Phase 3)

- Brain unique variance 가 paired bootstrap p < 0.05 이고 절대값이 의미있는 수준 (Pearson r 향상 +0.05 이상) 이면 Direction 2 main path 확정.
- 약하면 brain encoder 후보 변경 + alignment loss 조정.

---

## Phase 4. Hackathon Demo (5 일 단위)

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
- 평가표. V/A Pearson r, Cat34 macro AUROC 의 BrainVLM vs Brain-Video Multimodal vs ROI baseline vs chance 4-way 비교.
- Visualization. Brain-video joint embedding 의 UMAP cluster + ROI-wise brain unique contribution heatmap.

---

## Phase 5. Paper + Submission (Hackathon 후)

- [ ] Paper draft. EmoBrain 의 두 axis (BrainVLM + Multimodal) 의 결과 통합.
- [ ] Mixed valence categorization (Vaccaro 2024) 추가 측정.
- [ ] Cross-dataset evaluation (Emo-FilM, CineBrain).
- [ ] Submission venue 결정 (Nature Communications / NeurIPS / Cell Reports / ICLR).

상세는 `docs/masterplan_v3_emobrain.md` 에 작성 예정.
