# EmoBrain 온보딩 가이드

새로 합류하거나 작업을 이어받는 연구원이 5분 안에 프로젝트를 파악하고 실행해 볼 수 있도록 정리한 문서다.

---

## 1. 무엇을 하는 프로젝트인가

정서 영상을 볼 때 찍은 전뇌 fMRI 반응(Horikawa 외 2020, 참가자 5명, 개발 영상 2,109개, 피질·피질하 ROI 370개)에서 영상의 규범 정서 평정 34개를 예측하는 연구다. 뇌 신호에서 장면의 시각 특징(`V-JEPA 2`, 5,632차원)과 캡션 의미 특징(`DeBERTa-large`, 4,096차원)을 복원하고, 복원한 특징 경로를 정서 예측에 연결했을 때 예측 성능과 정보 사용 방식이 어떻게 달라지는지 검증한다.

## 2. 왜 하는가

뇌 반응에서 정서 점수만 바로 예측하는 모델로는 뇌 신호 안의 시각 정보와 장면 의미 정보가 정서 예측에 어떻게 쓰이는지 나누어 보기 어렵다. 이 파이프라인은 동일한 6-fold 분할 위에서 ① 뇌만으로 예측(`A`), ② 장면 특징을 보조 손실로만 학습(`B`), ③ 복원한 특징을 정서 계산에 투입(`C`, `D`), ④ 자극 모델 증류(`-2`) 및 대조군을 나란히 비교하고, 특징 바꿔 끼우기와 네트워크 교란으로 실제 경로 의존을 확인한다.

## 3. 지금 어디까지 완료됐는가

`b300-01` 서버에서 Horikawa(HK) 6-fold 본실험(`S1`~`S6`)과 사후 분석·시각화(`S9`~`S10`)를 완료했다.
- **완료된 단계**: `S1`·`S2`(전처리·370개 ROI·6-fold 분할), `S3`(자극 특징 8종 추출), `S4`(뇌 없는 자극 모델·구간 분석), `S5`(64개 층 선형 복원·기준선 `GED`·`EmoGrowth`·`H2020` 등 완료; `ML-BVAE` 잔여 18개 fold 제외), `S6`(뇌 모델 `A`~`E` 21개 조건 전체 학습), `S9`(바꿔 끼우기·쌍 비교·`K1/K1a`·13개 네트워크 교란), `S10`(통계 검정 `Table 1~7`·사전등록 `6-1` 판정표·벡터 그림 6종).
- **결과 문서와 그림**: 전체 정량 수치, 사전등록 가설 판정표, 논문용 그림 6종(`PDF`/`PNG`)은 [results/b300_hk_6fold/MASTER_RESULTS_SUMMARY.md](results/b300_hk_6fold/MASTER_RESULTS_SUMMARY.md)에 수록되어 있다. 설계 원문은 [docs/final/01_integrated_document.md](docs/final/01_integrated_document.md)에 있다.

## 4. 바로 이어서 맡을 수 있는 작업

남아 있는 실험과 원고 연결 과제는 아래 다섯 가지다. 작업 지시 상세는 [docs/final/04_claude_code_workorder.md](docs/final/04_claude_code_workorder.md)의 `S5`·`S7`·`S8` 절에 있다.

| 우선순위 | 과제 | 코드 준비 상태 | 시작 지점 |
|---|---|---|---|
| 1 | **`S8` 처음 보는 장면 구역 제외 재학습 (`6-2`)** | **코드 완성 (즉시 제출 가능)** | 5개 내용 구역 × 6 fold × 2 방식(`excluded`, `control`) = 60개 분할에서 `brain_only`(`A-1`), `brain_decoded`(`C-1`) 실행 (`scripts/b300/s6_train_b300.sbatch`, 동시 실행은 GPU 2~4장 이하로 제한) |
| 2 | **`S8` 단일 네트워크 단독 재학습 (`6-4a` / `1-3`)** | **짧은 옵션 추가 필요** | `manifests/s2/cabnp_groups.tsv` 기준 특정 네트워크(`Visual1`, `Visual2`, `Default` 등 13묶음) ROI token만 입력으로 남기는 인자를 별도 브랜치에서 `src/s6_train.py`에 추가하고 `git commit` 후 실행 |
| 3 | **`S7` MindCaptioning 외부 전이 평가 (`6-3`)** | **전반부 완성 / 후반부 추가** | ① HK 전체 학습(`--plan final_for_mc`)은 즉시 실행 가능. ② 고정된 공유 가중치 위에 MC 6명(`mc_sub-01..06`)의 입력 선형층 `W(s,r), b(s,r)`만 학습해 시험 영상 72개를 채점하는 전이 스크립트 작성(`manifests/s2/mc_blocks.tsv`, `mc_test_repeats.tsv` 준비 완료) |
| 4 | **`S5` 외부 기준선 `ML-BVAE` 잔여 실행** | **코드 완성 (즉시 재개 가능)** | 30개 `(참가자, fold)` 중 시간 상한으로 남은 18개를 `sbatch scripts/b300/s5_mlbvae_b300.sbatch`로 재개 (완료된 12개는 자동 건너뜀) |
| 5 | **논문 본문·보조자료 표·그림 통합** | **산출물 준비 완료** | `results/b300_hk_6fold/figures/` 벡터 PDF 6종과 `tables/` 요약표를 [docs/final/05_writing_guide.md](docs/final/05_writing_guide.md) 기준 본문에 연결하고 `S7`·`S8` 완료 후 수치 갱신 |

---

## 5. 5분 안에 시작하고 돌려보는 방법

### A. 개인 노트북·로컬에서 2분 안에 확인하기 (원자료·GPU 불필요)

레포에 경량 요약표(`results/b300_hk_6fold/`)와 합성 자료 시험이 들어 있어, fMRI 원자료 없이도 클론 직후 동작을 바로 확인할 수 있다(사전 요구 패키지: `Python 3.11+`, `numpy`, `pandas`, `scipy`, `scikit-learn`, `torch`, `matplotlib`).

```bash
# 1) 저장소 클론 및 브랜치 이동
git clone -b feat/b300-s1-s10-onboarding https://github.com/Transconnectome/EmoBrain.git
cd EmoBrain

# 2) 외부 파일 의존이 없는 순수 합성 자료 단위 시험 (각 10~60초)
bash scripts/s4_tests.sh
bash scripts/s5_tests.sh

# 3) 요약표에서 사전등록 6-1 판정표, 벡터 그림 6종, 종합 요약문 즉시 재생성 (약 10초)
python3 scripts/s9_s10/s10_verdict_and_figures.py --base-dir results/b300_hk_6fold --mode all
python3 scripts/s9_s10/generate_master_summary.py --base-dir results/b300_hk_6fold
```

### B. `b300-01` 서버에서 본 파이프라인 실행하기 (원자료·체크포인트 준비 완료)

> **필수 서버 규칙 (`b300-01`)**
> 1. **GPU 작업은 반드시 Slurm(`sbatch` 또는 `srun`)으로만 실행한다.** SSH 로그인 셸이나 `tmux` 안에서 GPU 학습·추론을 직접 띄우지 않는다.
> 2. **모든 Slurm 작업에 `--nodelist=b300-01`을 넣는다.** `/scratch/emobrain`은 `b300-01` 노드의 로컬 NVMe 디스크다.
> 3. `S4`~`S6` 본 실행 코드는 설계 동결 커밋(`f5c8569`)을 조상으로 두고 `src/s[456]_*.py`가 깨끗한 커밋 상태일 때만 돈다. 무수정 상태로 돌리는 과제(#1, #3-1, #4)와 `src/`를 수정하는 과제(#2)는 브랜치를 나누고 반드시 `git commit` 후 제출한다.

#### `b300-01` 서버 경로 요약

| 구분 | 경로 | 설명 |
|---|---|---|
| Python 환경 | `/scratch/envs/centaur/bin/python` | Python 3.12, PyTorch 2.15+cu132, 필요 패키지 설치 완료 |
| 코드 기준본 | `/scratch/emobrain/code` | 공용 기준 클론 (개인 작업은 본인 폴더에 별도 클론해 사용) |
| 원자료 | `/scratch/emobrain/data` | `hk/`(Horikawa 5명), `mc/`(MindCaptioning 6명), `stimuli/`(영상 2,196개), `atlas_sources/` |
| 본실험 산출물 | `/scratch/emobrain/outputs` | `s2_manifest/`, `s3_features/`, `s4_no_brain/`, `s5_ridge/`, `s6_brain/`, `s9_analysis/`, `s10_tables_figures/` |

#### 복사해서 바로 쓰는 실행 명령 (`b300-01`)

```bash
# 1) 본인 작업 폴더에 레포 클론 및 b300 경로·환경 설정 파일 복사
git clone -b feat/b300-s1-s10-onboarding https://github.com/Transconnectome/EmoBrain.git
cd EmoBrain
cp scripts/b300/configs/paths.b300.yaml configs/paths.yaml
cp scripts/b300/configs/env.b300.sh configs/env.sh
mkdir -p outputs/logs

# 2) 환경·경로 점검 및 단위 시험 (로그인 노드 CPU에서 실행 가능)
/scratch/envs/centaur/bin/python scripts/b300/verify_b300_env.py
bash scripts/s4_tests.sh
bash scripts/s6_tests.sh

# 3) 공용 산출물을 읽어 본인 폴더(outputs/s10_repro_<JOBID>/)에 판정표·그림 6종 재생성 확인 (CPU Slurm)
sbatch scripts/b300/s9_s10_cpu_b300.sbatch

# 4) 후속 GPU 실험 제출 예시 (반드시 sbatch 사용; 타 사용자 작업 방해 방지를 위해 동시 GPU 2~4장 이내 유지)
#    예: S8 처음 보는 장면 구역 1, fold 1 제외 학습 (6-2)
sbatch scripts/b300/s6_train_b300.sbatch zone_block1_fold1_excluded brain_only,brain_decoded

#    예: S7 MindCaptioning 전이용 HK 전체 모델 학습 (6-3 전반부)
sbatch scripts/b300/s6_train_b300.sbatch final_for_mc brain_only,brain_decoded

#    예: S5 ML-BVAE 잔여 fold 이어서 학습 (최대 2 GPU 동시 실행 설정됨)
sbatch scripts/b300/s5_mlbvae_b300.sbatch
```

---

## 6. 읽을 문서 순서

1. **[ONBOARDING.md](ONBOARDING.md)** (이 문서): 전체 현황, 남은 일, 5분 시작 명령
2. **[OVERVIEW.md](OVERVIEW.md)**: 연구 질문 1·2, 데이터셋, 모델 조건 `A`~`E` 요약 (89줄)
3. **[results/b300_hk_6fold/MASTER_RESULTS_SUMMARY.md](results/b300_hk_6fold/MASTER_RESULTS_SUMMARY.md)**: `S1`~`S10` 완료 결과 수치, 사전등록 `6-1` 판정표, 논문 그림 6종 안내
4. **[README.md](README.md)**: 디렉토리 구조, 분할 표, 단계별(`S1`~`S10`) 스크립트 명세
5. **[docs/final/01_integrated_document.md](docs/final/01_integrated_document.md)** · **[docs/final/04_claude_code_workorder.md](docs/final/04_claude_code_workorder.md)**: 설계 근거 원문과 단계별 세부 규격
