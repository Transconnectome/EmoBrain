# FEELIN 실행 계획 (Action Items)

> Phase 1 Benchmark — 8주 안에 할 일

---

## 이번 주 (Week 1)

**1. 데이터셋 접근 확인 및 다운로드**
- Emo-FilM (OpenNeuro ds004892): aws s3로 NERSC scratch에 동기화
- Affective Videos (OpenfMRI ds000205): BIDS 다운로드
- IAPS fMRI (NeuroVault collection 16284): beta map 일괄 다운로드
- NeuroEmo (OpenNeuro ds005700): BIDS 다운로드
- Koide-Majima / REELMO / HCP movie: access 가능 여부 사전 확인 (Phase 2용)
- 산출물: dataset 별 경로 / 파일 수 / 디스크 사용량 정리한 access table

**2. Horikawa 노이즈 한계 (ISC) 계산**
- 5명 피험자 간 같은 stimulus 응답의 inter-subject correlation 측정
- 각 task target (V/A, 34 카테고리, 14 dimensions) 별로 따로 계산
- 이 값이 BFM 성능 해석의 상한선 (ceiling) 이 됨
- 산출물: noise_ceilings.csv

**3. Horikawa split 정의 및 manifest 생성**
- stimulus-stratified split: 같은 stimulus ID는 모든 5명 피험자에서 같은 split에 배정
- train 1748 stim × 5 sub = 8,740 / val 219 × 5 = 1,095 / test 218 × 5 = 1,090
- 산출물: horikawa_split.csv

**4. Statistical floor 모델 4종 구현**
- Logistic regression (binary 용)
- Ridge regression (continuous regression 용)
- Multinomial logistic (multi-class 용)
- Multi-output ridge (multi-label / 고차원 vector 용)
- 입력은 모두 Schaefer 400 + Tian S3 50 = 450 ROI features
- 산출물: setup/code/floor_*.py

---

## Week 2 — 전처리 통일 및 노이즈 한계 정리

**1. 5개 데이터셋 모두 같은 atlas로 parcellation**
- Schaefer 400 17-network (피질) + Tian S3 50 (피질하) = 450 ROI 통일
- Horikawa는 이미 됨, 나머지 4개는 새로 작성
- dataset 별 parcellate_*.py + sbatch 작성

**2. BFM 입력 형식 변환 파이프라인 작성**
- SwiFT / NeuroSTORM 입력: 96×96×96×SL volumetric 형식
- Brain-JEPA 입력: ROI time series (450 features × time)
- dataset 별 입력 shape 정리

**3. Task target matrix 생성**
- 5개 dataset × 5 task level 별로 ground truth target 행렬 만들기
- Horikawa 예시: V/A 이진화 (median split), V/A 연속 점수, top-1 카테고리, 34D 점수
- 산출물: target_matrices/{dataset}_targets.npz

**4. 5개 dataset 모두 split manifest 작성 및 ISC 계산**
- 각 dataset 별 적절한 split 정의 (stimulus / film / subject 단위)
- 각 dataset 별 ISC noise ceiling 계산

---

## Week 3 ~ 4 — Horikawa benchmark 채우기

**1. Horikawa Statistical floor 결과 산출**
- 4개 floor 모델 × Horikawa × 5 random seeds = 20 runs
- 산출물: horikawa_floor_results.csv

**2. BFM 임베딩 추출 (6 conditions)**
- SwiFT resting-pretrained / SwiFT scratch 두 번
- Brain-JEPA resting / Brain-JEPA scratch 두 번
- NeuroSTORM resting / NeuroSTORM scratch 두 번
- 각 모델별 (8,740 + 1,095 + 1,090) stimuli × embedding dim
- 산출물: embeddings/{model}_{init}_horikawa.npz

**3. Horikawa 24 cells 채우기**
- 6 model conditions × 4 task levels (L0, L1, L2, L3) = 24 cells
- 각 cell × 5 random seeds = 120 BFM runs
- 각 cell마다 frozen embedding → ridge / logistic / softmax head 학습 → metric 측정

**4. Pass / Fail 분류**
- 각 cell이 floor를 의미 있게 이기는지 자동 분류
- WIN / MARGINAL / PAR / LOSE / FAIL 라벨 부여
- 산출물: horikawa_classification.md

---

## Week 5 ~ 6 — 나머지 4 dataset benchmark 채우기

**1. Emo-FilM (24 cells)**
- 6 model conditions × 4 task levels (L0, L1, L3, L4) = 24 cells
- L4 (continuous dynamics) 는 sliding-window head 별도 작성

**2. Affective Videos (18 cells)**
- 6 conditions × 3 task levels (L0, L1, L2 의 4 quadrants) = 18 cells
- 같은 clip의 4 반복은 같은 split에 묶기 (data leakage 방지)

**3. IAPS fMRI (12 cells)**
- 6 conditions × 2 task levels (L0, L2) = 12 cells
- SwiFT / NeuroSTORM은 beta map을 pseudo-time (1 frame) 으로 변환해서 입력

**4. NeuroEmo (6 cells)**
- 6 conditions × 1 task level (L2 5-class) = 6 cells
- 200 task volumes / 5 class 라 sparse, 강한 regularization 사용

**5. Pretraining 전략 사전 조사 (병렬 진행)**
- HCP movie continued pretraining 자원 / 시간 가늠
- naturalistic SSL (masked / contrastive / JEPA-style future latent prediction) 비교
- emotion-labeled supervised pretraining 후보 정리
- two-stage curriculum (naturalistic → emotion) 가능성 검토

---

## Week 7 — 결과 통합 및 Phase 2 방향 결정

**1. 102 cells 결과 통합**
- 모든 dataset master table 합치기
- WIN / MARGINAL / PAR / LOSE 분포 시각화
- 산출물: MASTER_CLASSIFICATION.md

**2. 패턴 분석**
- Resting-state pretrained 가 scratch 보다 나은가? (H1 검증)
- BFM 간 ranking은 어떤가? (어느 BFM이 가장 많은 WIN)
- Task level별 안정성 (L0 V/A는 쉬운가, L3 multi-label은 어려운가)
- Dataset 별 robust signal 패턴

**3. Phase 2 두 갈래 중 선택**
- Branch A (Pretraining + Adaptation): movie/task pretraining + adapter / affective head
- Branch B (Multimodal Brain–Stimulus): TRIBE-style alignment + video/audio/text feature fusion
- Phase 1 결과 패턴이 어느 branch에 더 강한 신호를 주는지 결정

---

## Week 8 — Workshop preprint draft 작성

**1. Venue 결정 및 abstract**
- NeurIPS workshop / ICLR workshop / arXiv preprint 중 선택
- 1 페이지 abstract 작성

**2. 결과 figure 4종 생성**
- Master matrix heatmap (102 cells × class)
- Resting vs Scratch 비교 plot
- BFM ranking per task plot
- Noise-ceiling normalized scores

**3. Methods + Results section draft**
- benchmark protocol 기술
- pass/fail 기준 명시
- 결과 요약 + Phase 2 plan 기술

---

## Phase 2 분기 (Phase 1 결과에 따라)

| Phase 1 결과 패턴 | Phase 2 Branch |
|---|---|
| Resting-pretrained 이 scratch 보다 일관되게 나음 | **Branch A**: movie / task fMRI pretraining 본격화 |
| Resting ≈ Scratch | **Branch A**: target-aware adapter 와 multi-task head 중심 |
| BFM 들이 floor 와 비슷함 | **Branch A 재설계**: input / window / pooling 부터 다시 |
| L3 / L4 같은 rich target 에서 BFM 이 약함 | **Branch B**: stimulus context 추가 (TRIBE alignment) |
| 특정 BFM 이 dominant | **Branch A scale**: 그 BFM 중심으로 adapter / fine-tuning |

---

FEELIN | Action Items | 2026
