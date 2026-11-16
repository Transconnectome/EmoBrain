# EmoBrain 온보딩 가이드

새로 합류하거나 작업을 이어받는 연구원이 5분 안에 프로젝트를 파악하고 안전하게 실행할 수 있도록 정리한 문서다.

> **[2026-11-16 정본 통합(`431c1bc`)]**: `src/`, `configs/s6/`, `scripts/s[4-9]_*.sh`, `scripts/s10_*.sh`, `tests/` 전체가 공식 설계 브랜치 `origin/design/emobrain-final-2026-11-03`(`431c1bc`)과 100% 동일하게 동기화되었다(`src/` 차이 0바이트). Perlmutter에서 완료된 정본 `s10_stats/` 요약표 반입 및 잔여 GPU 과업(`D/E`, `S8 6-2 / 6-4a / MC 6-3` 등) `b300-01` 분담 실행 시 이 `431c1bc` 정본 코드를 그대로 사용한다.

---

## 1. 무엇을 하는 프로젝트인가

정서 영상을 볼 때 찍은 전뇌 fMRI 반응(Horikawa 외 2020, 참가자 5명, 개발 영상 2,109개, 피질·피질하 ROI 370개)에서 영상의 규범 정서 평정 34개와 평가 차원 14개를 예측하는 연구다. 뇌 신호에서 장면의 시각 특징(`V-JEPA 2`, 5,632차원)과 캡션 의미 특징(`DeBERTa-large`, 4,096차원)을 복원하고, 복원한 특징 경로를 정서 예측에 연결했을 때 예측 성능과 정보 사용 방식이 어떻게 달라지는지 검증한다.

## 2. 왜 하는가

뇌 반응에서 정서 점수만 바로 예측하는 모델로는 뇌 신호 안의 시각 정보와 장면 의미 정보가 정서 예측에 어떻게 쓰이는지 나누어 보기 어렵다. 이 파이프라인은 동일한 6-fold 분할 위에서 ① 전뇌 선형 예측 및 고정 자극 규칙 매개(`S5 Ridge`, `K1`, `K1a + B4`), ② 뇌만으로 예측(`A`), ③ 장면 특징 보조 손실(`B`), ④ 복원 특징 결합(`C`, `D`), ⑤ 자극 모델 증류(`-2`) 및 대조군을 나란히 비교하고, 특징 바꿔 끼우기와 뇌 묶음 분석으로 실제 경로 의존을 검증한다.

## 3. 지금 어디까지 완료됐는가 (데이터 정합성 기준 구분)

- **100% 정품 확정 완료 (`재실행 불필요`)**:
  - `S1`·`S2` 분할·매니페스트, `S3` 자극 특징 8종 전체(`V-JEPA 2`, `DeBERTa`, `DeBERTa_noemo`, `CLIP`, `VideoMAE`, `TimeSformer`, `MPNet`, `lowlevel`), `S4` 뇌 없는 자극 모델 전체(`s4_stimulus = 0.4766`, `s4_noemo = 0.4810`, `s4_clip = 0.5595`, `s4_k1a` 등), `S5` 영상 기준선(`length`, `lowlevel`).
- **정품 `roi_voxels` 교체 즉시 갱신 대상 (`Step 1` · `Step 2`)**:
  - 초기 `b300-01` 이관 당시 Perlmutter의 정품 `roi_voxels`(`Glasser HCP360 + PickAtlas`, `manifests/s2/provenance.json` 기록본) 대신 구형 근사 파일(`60.3%` 복셀 커버리지)이 놓여 있었음이 감사에서 확인되었다.
  - 그 보수적 하한 조건에서도 전뇌 선형 `S5` 64개 층 복원(`[사전] 2-1`), `K1`(`0.2952`), `K1a`(`0.4530 > B4 0.3712`)는 5명 전원 유의하게 확인되었으나, 정품 `roi_voxels` 11개 반입 직후 **Step 1(`S5`+심화 3종, `<1시간`)** 및 **Step 2(`S6` 핵심 11개 조건, `~5시간`)**로 깔끔하게 정품 갱신한다. (`ML-BVAE` 부분 실행분은 합산에서 제외한다.)
- **현재 요약 보고서 및 상세 로드맵**:
  - 수치·사전등록 판정표·논문 그림 6종: [results/b300_hk_6fold/MASTER_RESULTS_SUMMARY.md](results/b300_hk_6fold/MASTER_RESULTS_SUMMARY.md)
  - 핵심 4단계 실행 계획 및 생략 목록(`Cut List`): [docs/FUTURE_RESEARCH_PLAN.md](docs/FUTURE_RESEARCH_PLAN.md)

## 4. 바로 이어서 진행하는 핵심 4단계 과제 ([docs/FUTURE_RESEARCH_PLAN.md](docs/FUTURE_RESEARCH_PLAN.md))

> **중요 안전 게이트**: Perlmutter 정품 `roi_voxels/*.npz` 11개가 `b300-01:/scratch/emobrain/outputs/s2_manifest/roi_voxels/`에 복사되어 `verify_s2_roi_voxels.py` 검증(`exit 0`)을 통과하기 전에는 **모든 GPU 학습(`S5`/`S6`/`S7`/`S8`) 제출을 보류**한다(sbatch 스크립트가 자동으로 차단함).

| 단계 | 과제 | 예상 소요 | 실행 스크립트 / 핵심 규칙 |
|---|---|---|---|
| **Step 0** | **정품 `roi_voxels` 11개 반입 및 SHA256 검증** | 즉시 (~15 MB 복사) | Perlmutter `final_2026-11/s2_manifest/roi_voxels/{hk_sub-01..05,mc_sub-01..06}.npz` 반입 후 `python scripts/b300/verify_s2_roi_voxels.py` 통과 확인 |
| **Step 1** | **전뇌 선형 핵심 사슬 정품 재실행 + 심화 3종 (`K1_noemo`, `K1_zone`, 13네트워크 `LONO`)** | 1 GPU `< 1시간` | `sbatch scripts/b300/step1_linear_core_b300.sbatch` (`S8 6-2` 구역 일반화 및 `6-4` 네트워크 분석을 교란 없는 전뇌 선형 분석으로 일괄 수행) |
| **Step 2** | **`S6` 핵심 11개 조건 압축 재실행 + `S9/S10` 전체 갱신** | 6 GPUs `~5시간` | `sbatch scripts/b300/step2_s6_core_b300.sbatch` 완료 후 `sbatch scripts/b300/step2_post_s9_s10_b300.sbatch` (`[2-1]`, `[2-2]`, `[2-3(가)~(바)]` 전수 포함, 비핵심 조건 60% 절감) |
| **Step 3** | **`S7` MindCaptioning 외부 데이터셋(`mc_test72`) 단판 전이 (`6-3`)** | 1 GPU `< 1.5시간` | `L10` 고정 설정(`--fixed-selected`) 및 `O28`~`O30` 단 1회(`1-shot`) 시험 채점 준수 (`S5 Ridge + K1/K1a`, `A-1_pool`, Step 2 최우수 모델 3종) |

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

### B. `b300-01` 서버에서 본 파이프라인 실행하기

> **필수 서버 규칙 (`b300-01`)**
> 1. **GPU 작업은 반드시 Slurm(`sbatch` 또는 `srun`)으로만 실행한다.** SSH 로그인 셸이나 `tmux` 안에서 GPU 학습·추론을 직접 띄우지 않는다.
> 2. **모든 Slurm 작업에 `--nodelist=b300-01`을 넣는다.** `/scratch/emobrain`은 `b300-01` 노드의 로컬 NVMe 디스크다.
> 3. **`src/` 디렉토리는 수정하지 않는다.** `S4`~`S6` 실행 코드는 설계 동결 커밋(`f5c8569`)의 `START_CODE` SHA256을 강제 검증한다. 개인 시험 시 공용 산출물 덮어쓰기를 막으려면 `S5_OUT`·`S6_OUT` 환경변수로 본인 출력 경로를 분리한다.

#### `b300-01` 서버 경로 요약

| 구분 | 경로 | 설명 |
|---|---|---|
| Python 환경 | `/scratch/envs/centaur/bin/python` | Python 3.12, PyTorch 2.15+cu132, 필요 패키지 설치 완료 |
| 코드 기준본 | `/scratch/emobrain/code` | 공용 기준 클론 (개인 작업은 본인 폴더에 별도 클론해 사용) |
| 원자료 | `/scratch/emobrain/data` | `Horikawa/`(5명), `MindCaptioning/`(6명), `stimuli/`(영상 2,196개), `manifests/`, `metadata/` |
| 본실험 산출물 | `/scratch/emobrain/outputs` | `s2_manifest/`, `s3_features/`, `s4_no_brain/`, `s5_ridge/`, `s6_brain/`, `s9_analysis/`, `s10_tables_figures/` |
| v1 백업 경로 | `/scratch/emobrain/outputs_v1_synthetic_roi` | 정품 `roi_voxels` 교체 시 기존 구형 근사 기반 `S5`/`S6` 산출물 자동 백업 위치 |

#### 복사해서 바로 쓰는 실행 명령 (`b300-01`)

```bash
# 1) 본인 작업 폴더에 레포 클론 및 b300 경로·환경 설정 파일 복사
git clone -b feat/b300-s1-s10-onboarding https://github.com/Transconnectome/EmoBrain.git
cd EmoBrain
cp scripts/b300/configs/paths.b300.yaml configs/paths.yaml
cp scripts/b300/configs/env.b300.sh configs/env.sh
mkdir -p outputs/logs

# 2) 환경·경로 및 정품 S2 roi_voxels SHA256 게이트 점검 (로그인 노드 CPU에서 즉시 확인)
/scratch/envs/centaur/bin/python scripts/b300/verify_b300_env.py
/scratch/envs/centaur/bin/python scripts/b300/verify_s2_roi_voxels.py

# 3) 공용 산출물을 읽어 본인 폴더(outputs/s10_repro_<JOBID>/)에 판정표·그림 6종 재생성 확인 (CPU Slurm)
sbatch scripts/b300/s9_s10_cpu_b300.sbatch

# 4) [정품 roi_voxels 반입 완료(verify_s2_roi_voxels.py exit 0) 후] 핵심 Step 1 · Step 2 제출
STEP1_JID=$(sbatch --parsable scripts/b300/step1_linear_core_b300.sbatch)
STEP2_JID=$(sbatch --parsable scripts/b300/step2_s6_core_b300.sbatch)
sbatch --dependency=afterok:${STEP1_JID}:${STEP2_JID} scripts/b300/step2_post_s9_s10_b300.sbatch
```

---

## 6. 읽을 문서 순서

1. **[ONBOARDING.md](ONBOARDING.md)** (이 문서): 전체 현황, 안전 게이트, 5분 시작 명령
2. **[docs/FUTURE_RESEARCH_PLAN.md](docs/FUTURE_RESEARCH_PLAN.md)**: 정품 ROI 복구 및 핵심 4단계 실행·가지치기 공식 계획서
3. **[OVERVIEW.md](OVERVIEW.md)**: 연구 질문 1·2, 데이터셋, 모델 조건 `A`~`E` 요약
4. **[results/b300_hk_6fold/MASTER_RESULTS_SUMMARY.md](results/b300_hk_6fold/MASTER_RESULTS_SUMMARY.md)**: `S1`~`S10` 결과 수치(`Table 1` 43행 전체 포함), 사전등록 `6-1` 판정표, 논문 그림 6종 안내
5. **[docs/final/01_integrated_document.md](docs/final/01_integrated_document.md)** · **[docs/final/04_claude_code_workorder.md](docs/final/04_claude_code_workorder.md)**: 설계 근거 원문과 단계별 세부 규격
