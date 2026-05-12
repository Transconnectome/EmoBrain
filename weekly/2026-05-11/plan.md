# Weekly Plan: 2026-05-11

> FEELIN Phase 1 Benchmark — Week 1

## 이번 주 목표

FEELIN Phase 1 benchmark 실행을 위한 데이터/도구 셋업. Week 2 부터 본격 cell 채우기 시작 가능한 상태로 만든다.

## Action Items

### 1. 데이터셋 접근 확인 및 다운로드
- [ ] Emo-FilM (OpenNeuro ds004892) NERSC scratch에 동기화
- [ ] Affective Videos (OpenfMRI ds000205) BIDS 다운로드
- [ ] IAPS fMRI (NeuroVault collection 16284) beta map 다운로드
- [ ] NeuroEmo (OpenNeuro ds005700) BIDS 다운로드
- [ ] Koide-Majima / REELMO / HCP movie access 가능 여부 사전 확인 (Phase 2용)
- [ ] `reports/status/dataset_access_2026-05-11.md` 작성

### 2. Horikawa noise ceiling (ISC) 계산
- [ ] `setup/code/compute_isc.py` 작성
- [ ] 5명 피험자 간 같은 stimulus 응답의 inter-subject correlation 계산
- [ ] 각 task target (V/A, 34 카테고리, 14 dimensions) 별로 따로
- [ ] `setup/results/noise_ceilings.csv` 산출

### 3. Horikawa stimulus-stratified split 정의
- [ ] train: stimulus 1~1748 × 5 sub = 8,740
- [ ] val: stimulus 1749~1967 × 5 sub = 1,095
- [ ] test: stimulus 1968~2185 × 5 sub = 1,090
- [ ] `setup/data/horikawa_split.csv` 생성

### 4. Statistical floor 모델 4종 구현
- [ ] `setup/code/floor_logistic_binary.py` (L0 binary)
- [ ] `setup/code/floor_ridge_regression.py` (L1 regression)
- [ ] `setup/code/floor_multinomial.py` (L2 one-hot)
- [ ] `setup/code/floor_multioutput_ridge.py` (L3 multi-label)
- [ ] 입력 표준: Schaefer 400 + Tian S3 50 = 450 ROI features

## 의존성 / 막힐 수 있는 것

- Emo-FilM/HCP access 가 막히면 Phase 1 dataset 후보 축소 (NeuroEmo/Affective Videos 비중 ↑)
- NERSC scratch 디스크 공간 (5 dataset 다운로드 시 확인 필요)
- Brain-JEPA / NeuroSTORM checkpoint 호환성 사전 검증
