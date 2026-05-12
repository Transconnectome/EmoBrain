# FEELIN 실행 계획 (v2)

Last updated: 2026-05-11

이 문서는 현재 해야 할 일을 한글로 정리한 active action plan입니다. 완성된 논문
개요는 `Paper/framework_KR.md`, 방법론은 `Paper/methodology.md`, 데이터/모델
상세 reference는 `reference/`에 둡니다.

## 0. 핵심 원칙

FEELIN의 목표는 SwiFT를 무조건 살리는 것도, benchmark table 하나를 만드는
것도 아닙니다. 목표는 **emotion representation을 잘 담아내는
emotion-specific brain foundation model / brain model을 개발하는 것**입니다.

따라서 운영 원칙은 다음입니다.

1. SwiFT-first지만 SwiFT-locked는 아니다.
2. old EmoDe cache는 참고만 하고, 새 실험은 canonical manifest에서 다시 시작한다.
3. Horikawa/Cowen 기준은 `2185` stimuli다.
4. 모든 모델은 같은 target, split, metric에서 비교한다.
5. prediction 성능뿐 아니라 어떤 neural representation이 중요한지도 본다.
6. 먼저 Brain Foundation Model benchmark를 넓게 돌려 search space를 줄이고,
   그 다음에 pretraining/adaptation branch와 multimodal framework branch를
   실험한다.

## 0.5 Benchmark Scope (v2 확정)

`Dataset × (BFM × Init) × Task` 3축 매트릭스. 자세한 명세는
`notes/benchmark_design.md`.

### Dataset axis (5개)

| Dataset | Status | 첫 역할 |
|---|---|---|
| Horikawa/Cowen | HAVE | high-dim affect geometry, V/A sanity |
| Emo-FilM | DOWNLOAD | naturalistic component/appraisal/dynamic |
| Affective Videos (ds000205) | DOWNLOAD | fast V/A sanity |
| IAPS fMRI (NeuroVault) | DOWNLOAD | static valence category |
| NeuroEmo (ds005700) | DOWNLOAD | cross-cultural multi-class |

Koide-Majima, REELMO, HCP movie 등은 Phase 2.

### Model × Init axis (6 conditions)

3 BFM × 2 init.

| BFM | Resting-pretrained init | Scratch init |
|---|---|---|
| SwiFT | Transconnectome lab checkpoint | random init |
| Brain-JEPA | `jepa-ep300.pth` (ABCD) | random init |
| NeuroSTORM | `pt_neurostorm_mae_ratio0.5.ckpt` | random init |

BrainLM은 Horikawa 비호환 (490 timepoint 고정)으로 제외 (EmoDe에서 검증됨).

### Task axis (5 레벨)

| Level | Task | Output | Primary metric |
|---|---|---|---|
| L0 | High/Low V/A binary | binary class | AUROC |
| L1 | V/A regression | continuous | Pearson r |
| L2 | One-hot classification | top-1 label | balanced accuracy |
| L3 | Multi-label classification | multi-emotion prob | macro F1 |
| L4 | Continuous dynamics | trajectory | CCC |

### Statistical floors

각 task에 BFM 없는 baseline 1개.

| Task | Floor | Input |
|---|---|---|
| L0 | Logistic regression | Schaefer400+Tian50 = 450 ROI features |
| L1 | Ridge regression | 같은 ROI features |
| L2 | Multinomial logistic | 같은 |
| L3 | Multi-output ridge | 같은 |
| L4 | Sliding-window ridge | dynamic FC features |

### Pass/fail threshold (사전 정의)

BFM이 "WIN"으로 분류되려면 세 조건 모두 만족:

1. Δ(BFM - floor) > 2 × pooled SE
2. Δ(BFM - floor) > 0.02 absolute
3. Permutation test p < 0.05

라벨: `WIN` / `MARGINAL` / `PAR` / `LOSE` / `FAIL`.

### Phase 1에서 제외 (Phase 2 이후)

- TRIBE/stimulus-only baseline
- HCP/CNeuroMod/StudyForrest pretraining
- Adapter/LoRA/fine-tuning variants (frozen probe만)
- Window length sweep (SL5/10/20/40)
- Stimulus-brain alignment
- Affective LLM/VLM brain-tuning

---

## 1. Week 1: Data Download + Access Verification

### Action items

- [ ] `setup/code/check_dataset_access.py` 작성 (각 dataset 경로/파일 수/디스크 사용량 측정)
- [ ] Emo-FilM 다운로드
  - `aws s3 sync --no-sign-request s3://openneuro.org/ds004892 /pscratch/sd/s/sjmoon/datasets/EmoFilM/`
- [ ] Affective Videos 다운로드 (OpenfMRI ds000205)
  - `/pscratch/sd/s/sjmoon/datasets/AffectiveVideos/`
- [ ] IAPS fMRI 다운로드 (NeuroVault collection 16284)
  - `/pscratch/sd/s/sjmoon/datasets/IAPS_fMRI/`
- [ ] NeuroEmo 다운로드 (OpenNeuro ds005700)
  - `/pscratch/sd/s/sjmoon/datasets/NeuroEmo/`
- [ ] `reports/status/dataset_access_2026-05-11.md` 작성 (YES/NO/PARTIAL, 경로, 디스크 사용량)
- [ ] HCP movie access 확인 (Phase 2 대비 — Data Use Agreement 상태)

### Deliverable

- `setup/data/dataset_access.csv`
- `reports/status/dataset_access_2026-05-11.md`

---

## 2. Week 2: Preprocessing + Noise Ceiling

### 2.1 Parcellation 통일 (Schaefer 400 + Tian S3 50)

- [ ] Horikawa는 이미 적용됨 (`/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_preprocess_JEPA_ROI/`)
- [ ] `setup/code/parcellate_emofilm.py` + `.sh`
- [ ] `setup/code/parcellate_affective_videos.py` + `.sh`
- [ ] `setup/code/parcellate_iaps.py` + `.sh` (beta map용)
- [ ] `setup/code/parcellate_neuroemo.py` + `.sh`

### 2.2 BFM 입력 형식 변환

- [ ] `setup/code/convert_to_swift_input.py` (96×96×96×SL 변환)
- [ ] Brain-JEPA는 parcellated ROI time series 그대로 사용
- [ ] dataset별 입력 shape table → `reports/status/bfm_input_shapes.md`

### 2.3 Target matrix 생성

- [ ] Horikawa
  - L0: V/A median split → binary
  - L1: V/A continuous score
  - L2: top-1 emotion (34 categories argmax)
  - L3: 34D continuous scores
- [ ] Emo-FilM target matrix (50 items, TR-level smoothed)
- [ ] Affective Videos (4 quadrants → V/A binary + continuous)
- [ ] IAPS (pos/neu/neg + pos/neg binary)
- [ ] NeuroEmo (5-class)
- [ ] 모두 `setup/data/target_matrices/{dataset}_targets.npz`

### 2.4 Split manifest

- [ ] Horikawa stimulus-stratified
  - train: stim 1~1748 × 5 sub = 8740
  - val: stim 1749~1967 × 5 = 1085
  - test: stim 1968~2185 × 5 = 1085
  - `setup/data/horikawa_split.csv`
- [ ] Emo-FilM film-stratified (13 train film + 1 test film, rotation)
- [ ] Affective Videos trial-level (4 repetition을 같은 split에 묶기)
- [ ] IAPS subject-stratified (50/3/3)
- [ ] NeuroEmo subject-stratified (32/4/4)

### 2.5 ISC noise ceiling

- [ ] `setup/code/compute_isc.py` 작성
- [ ] 각 dataset × 각 task별 ISC 계산
- [ ] `setup/results/noise_ceilings.csv`

### Deliverable

- 모든 dataset의 parcellated time series
- 모든 dataset × task의 target matrix
- `setup/data/*_split.csv`
- `setup/results/noise_ceilings.csv`

---

## 3. Week 3-4: Horikawa 전체 cell

### 3.1 Statistical floor 먼저 (4 cells)

- [ ] `setup/code/floor_logistic_binary.py` (L0)
- [ ] `setup/code/floor_ridge_regression.py` (L1)
- [ ] `setup/code/floor_multinomial.py` (L2)
- [ ] `setup/code/floor_multioutput_ridge.py` (L3)
- [ ] 각 floor × Horikawa × 5 seeds → 20 runs
- [ ] `reports/results/horikawa_floor_results.csv`

### 3.2 BFM frozen probe pipeline

- [ ] `setup/code/extract_swift_embeddings.py` + `.sh`
  - resting init, scratch init 두 번
  - 8740 + 1085 + 1085 stimuli × 768-dim embedding
- [ ] `setup/code/extract_jepa_embeddings.py` + `.sh`
  - resting (`jepa-ep300.pth`), scratch
  - ROI time series 입력
- [ ] `setup/code/extract_neurostorm_embeddings.py` + `.sh`
  - resting ckpt, scratch
  - 96×96×96×SL 입력
- [ ] `setup/code/probe_head_train.py` (embedding → task head, 모든 task type 지원)

### 3.3 Horikawa × 6 models × 4 tasks = 24 cells

- [ ] 각 cell × 5 seeds = 120 runs
- [ ] sbatch array job으로 병렬화
- [ ] `reports/results/horikawa_master.csv`

### 3.4 Pass/fail 분류

- [ ] `setup/code/classify_results.py` (Δ, SE, perm p 계산 → WIN/MARGINAL/PAR/LOSE/FAIL)
- [ ] `reports/results/horikawa_classification.md`

### Deliverable

- 120 frozen probe runs + 20 floor runs = 140 runs
- Horikawa master result table + classification report

---

## 4. Week 5-6: 나머지 4 dataset cell

### 4.1 Emo-FilM × 6 × 4 = 24 cells

- [ ] L0/L1/L3에 같은 pipeline 적용
- [ ] L4 (continuous dynamics) — sliding-window head 별도 처리
- [ ] `reports/results/emofilm_master.csv`

### 4.2 Affective Videos × 6 × 3 = 18 cells

- [ ] L0/L1/L2 (4 quadrants)
- [ ] 4 repetition 같은 split 보장
- [ ] `reports/results/affective_videos_master.csv`

### 4.3 IAPS × 6 × 2 = 12 cells

- [ ] L0/L2
- [ ] SwiFT/NeuroSTORM: beta map → pseudo-time (1 frame) 변환
- [ ] `reports/results/iaps_master.csv`

### 4.4 NeuroEmo × 6 × 1 = 6 cells

- [ ] L2 (5-class)
- [ ] 200 task volume / 5 class → sparse, regularization 강화
- [ ] `reports/results/neuroemo_master.csv`

### Deliverable

- 60 frozen probe cells × 5 seeds = 300 runs
- 5 dataset master tables + classification reports

---

## 5. Week 7: Decision Table + Phase 2 Track Choice

### 5.1 통합 결과

- [ ] `setup/code/aggregate_master_results.py`
- [ ] 102 cells × class 통합 → `reports/results/MASTER_CLASSIFICATION.md`

### 5.2 Pattern 분석

- [ ] Resting-pretrained vs scratch
  - 같은 (dataset, task)에서 Δ > 2×SE인 cell 수 → H1 검증
- [ ] BFM 간 ranking
  - 어느 BFM이 가장 많은 WIN?
- [ ] Task별 안정성
  - L0~L4에서 WIN 비율 → H3 검증 (arousal 가장 안정?)
- [ ] Dataset별 패턴
  - cross-dataset robustness

### 5.3 Phase 2 Track decision

| Phase 1 패턴 | Phase 2 track |
|---|---|
| Resting > scratch consistently | Pretraining: movie/task pretraining 확장 |
| Resting ≈ scratch | Adaptation: target-aware pretraining + adapter |
| BFMs ≈ floors broadly | Representation: input/window/pooling 재검토 |
| L3/L4에서 BFMs LOSE | Multimodal: stimulus context 추가 |
| 특정 BFM dominates | Scale: 그 BFM 중심 adapter/fine-tune |

- [ ] `reports/status/PHASE2_TRACK_DECISION.md`

---

## 6. Week 8: Writeup

- [ ] Workshop venue 결정 (NeurIPS workshop / ICLR workshop / arXiv preprint)
- [ ] `Paper/abstract.md`
- [ ] 결과 figure 4개
  - Fig 1: master matrix heatmap (102 cells × class)
  - Fig 2: resting vs scratch
  - Fig 3: BFM ranking per task
  - Fig 4: noise-ceiling normalized scores
- [ ] `Paper/methods_v1.md`
- [ ] `Paper/results_v1.md`
- [ ] Discussion: Phase 2 plan

### Deliverable

- Workshop preprint draft
- 4 figures
- Phase 2 plan

---

## 7. 오늘 당장 시작할 수 있는 5개

다른 dataset download 기다리는 동안 Horikawa로 미리 시작 가능:

1. [ ] `setup/code/check_dataset_access.py` 작성 + 실행
2. [ ] Emo-FilM/Affective Videos/IAPS/NeuroEmo 다운로드 sbatch job 제출
3. [ ] `setup/code/compute_isc.py` 작성 (Horikawa noise ceiling 계산)
4. [ ] `setup/data/horikawa_split.csv` 생성 (stimulus-stratified)
5. [ ] `setup/code/floor_ridge_regression.py` 작성 — Horikawa L1 V/A regression이 가장 단순

---

## 8. 산출물 목록

### Phase 1 끝났을 때 있어야 할 파일

```
setup/data/
├── horikawa_split.csv
├── emofilm_split.csv
├── affective_videos_split.csv
├── iaps_split.csv
├── neuroemo_split.csv
├── target_matrices/
│   ├── horikawa_targets.npz
│   ├── emofilm_targets.npz
│   ├── affective_videos_targets.npz
│   ├── iaps_targets.npz
│   └── neuroemo_targets.npz
└── parcellated/
    ├── emofilm/  (각 sub × stim 또는 sub × TR)
    ├── affective_videos/
    ├── iaps/  (beta maps)
    └── neuroemo/

setup/results/
├── noise_ceilings.csv
├── embeddings/
│   ├── swift_resting_{dataset}.npz
│   ├── swift_scratch_{dataset}.npz
│   ├── jepa_resting_{dataset}.npz
│   ├── jepa_scratch_{dataset}.npz
│   ├── neurostorm_resting_{dataset}.npz
│   └── neurostorm_scratch_{dataset}.npz
└── (per-cell raw scores)

reports/results/
├── horikawa_master.csv
├── emofilm_master.csv
├── affective_videos_master.csv
├── iaps_master.csv
├── neuroemo_master.csv
├── horikawa_classification.md
├── emofilm_classification.md
├── ...
└── MASTER_CLASSIFICATION.md

reports/status/
├── dataset_access_2026-05-11.md
├── bfm_input_shapes.md
└── PHASE2_TRACK_DECISION.md

Paper/
├── abstract.md
├── methods_v1.md
├── results_v1.md
└── figures/  (4 figs)
```

---

## 9. Risk Register

| 위험 | 임팩트 | 대응 |
|---|---|---|
| Emo-FilM access 거부/지연 | 24 cells 누락 | NeuroEmo/Affective Videos 비중 ↑ |
| BFM checkpoint 호환성 실패 | 특정 cell 실패 | FAIL 마킹, 진행 |
| NERSC GPU 할당 부족 | 102 cells 완료 못함 | seeds 5→3, parcel-only로 후퇴 |
| ISC ceiling < 0.1 | 모든 BFM이 PAR | dataset 자체 문제 가능, target 재정의 |
| Parcellation 변환 오류 | cascade 영향 | Week 2 sanity visualization 필수 |
| BrainLM 호환성 (재고려 시) | A424 atlas, 490 TR 고정 | Phase 1에서 제외 (확정) |

---

## 10. 성공 기준

8주 후 다음을 결정할 수 있으면 Phase 1 성공:

1. 어느 BFM × init이 어느 (dataset, task)에서 floor 위인가
2. Resting-state pretraining이 emotion 학습에 도움인가
3. 어느 dataset이 robust signal을 주는가
4. Phase 2 어느 track으로 갈 것인가 (pretraining / multimodal / adaptation / representation / scale)
5. 완성형 emotion BFM을 어떻게 설계할지 (Phase 2 시작점)
