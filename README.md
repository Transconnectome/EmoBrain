# EmoBrain

정서 영상을 볼 때의 fMRI 반응에서 장면의 시각 정보와 의미 정보를 읽고, 그 정보를 써서 정서 평정 34개를 예측하는 연구의 코드와 결과 저장소다.

- **처음 시작하는 연구원 안내 (5분 요약·서버 경로·후속 과제)**: **[ONBOARDING.md](ONBOARDING.md)**
- **연구 질문·데이터·조건 요약**: **[OVERVIEW.md](OVERVIEW.md)**
- **`b300-01` 본실험(`S1`~`S6`) 및 `S9`·`S10` 정량 결과·논문 그림 6종**: **[results/b300_hk_6fold/MASTER_RESULTS_SUMMARY.md](results/b300_hk_6fold/MASTER_RESULTS_SUMMARY.md)**
- **설계 원문과 작업 지시서**: **[docs/final/01_integrated_document.md](docs/final/01_integrated_document.md)** · **[docs/final/04_claude_code_workorder.md](docs/final/04_claude_code_workorder.md)**

## 디렉토리

```
ONBOARDING.md        새 참여자용 5분 시작 가이드, b300-01 경로, 남은 과제 안내
README.md            디렉토리와 단계별 사용법 (이 파일)
OVERVIEW.md          연구 질문, 자료, 모델, 평가 요약
configs/             서버별 경로와 실행 환경, S6 실행 설정
  paths.example.yaml   → paths.yaml로 복사해 사용 (git 밖; b300용은 scripts/b300/configs/ 참고)
  env.example.sh       → env.sh로 복사해 사용 (git 밖; b300용은 scripts/b300/configs/ 참고)
  s6/                  뇌 모델 실행 설정 JSON
splits/hk_dev_v4/    6-fold 분할 원본 표 두 개와 실행 단위별 영상 목록
manifests/           단계마다 만든 작은 표와 출처 해시 (s1, s2, s3, s6)
data/                작은 입력 표 (정서 평정 34개, 캡션, 자극 목록과 번호 대응)
src/                 핵심 파이프라인 코드 (s1_ ~ s6_)
scripts/             단계별 실행 스크립트
  s1_*.sh ~ s6_*.sh    단계별 표준 실행 스크립트
  b300/                b300-01 서버 전용 Slurm(.sbatch) 래퍼 및 환경 점검 스크립트
  s9_s10/              저장된 모델 사후 분석(S9) 및 통계 검정·논문 그림 생성(S10) 스크립트
results/             추적 가능한 경량 결과 번들 (표·판정표·벡터 그림 PDF/PNG)
  b300_hk_6fold/       b300-01 HK 6-fold 본실험 S4~S10 요약표와 그림 6종
tests/               합성 자료 단위 시험 (실제 정답과 뇌 반응을 읽지 않음)
docs/final/          동결 설계 문서(01~05)와 참고문헌
archive/             이전 설계의 코드와 문서 (현재 분석에 쓰지 않음)
external/            외부 레포 (git submodule)
```

큰 산출물(특징 배열, 체크포인트 `.pt`, 대용량 예측 `.npz`)은 `configs/paths.yaml`의 `output_root`에 쓰며 git에 올리지 않는다(`b300-01`에서는 `/scratch/emobrain/outputs/`).

## 설치와 설정

1. Python 3.11+ 환경(`b300-01`에서는 `/scratch/envs/centaur/bin/python`을 그대로 쓴다).
   - GPU 단계(S3~S6): PyTorch, NumPy, pandas, SciPy, scikit-learn, transformers, h5py
   - CPU·시각화 단계(S1, S2, S9, S10): NumPy, pandas, SciPy, scikit-learn, nibabel, matplotlib
   - S3 저수준 특징: [pymoten](https://github.com/gallantlab/pymoten), h264 복호기가 있는 `ffmpeg`
2. 설정 파일 두 개를 만든다(`b300-01` 서버에서는 `scripts/b300/configs/`의 파일을 복사한다).
   ```bash
   cp scripts/b300/configs/paths.b300.yaml configs/paths.yaml   # 타 서버는 configs/paths.example.yaml 수정
   cp scripts/b300/configs/env.b300.sh configs/env.sh           # 타 서버는 configs/env.example.sh 수정
   ```
3. `video_root`에 자극 영상 2,196개, `data_root` 아래에 원자료(`Horikawa/sub-XX/v3_qc/`, `MindCaptioning/sub-XX/v2_qc/`, `atlas_sources/`)를 둔다(`b300-01`에서는 `/scratch/emobrain/data/`에 모두 준비되어 있다).

## 분할

`splits/hk_dev_v4/`가 분할의 전부다.

| 파일 | 내용 |
|---|---|
| `split_hk_dev.tsv` | 개발 영상 2,109개와 fold 번호(1~6). 원본 |
| `fold_roles.tsv` | 바깥 fold k를 시험으로 쓸 때 검증 fold와 학습 fold. 원본 |
| `outer_fold<k>/{train,val,test}.txt` | 실행 단위별 영상 번호 목록. 한 줄에 `video_id` 하나 |
| `final_for_mc/{train,val,test}.txt` | MC 전이용 최종 모델(시험 없음) |

목록 파일은 `bash scripts/s2_split_files.sh`가 원본 표 두 개에서 만들고 손으로 고치지 않는다. MindCaptioning 최종 시험 영상 72개와 같은 내용의 영상은 어느 목록에도 없다.

## 단계별 실행

모든 명령은 레포 최상위에서 실행한다. **GPU 작업은 반드시 Slurm(`sbatch` / `srun`)으로만 제출하며 로그인 노드(SSH/tmux)에서 직접 실행하지 않는다.** `b300-01` 서버에서는 `scripts/b300/*.sbatch`를 사용한다(기본 `scripts/s*.sh`의 `#SBATCH` 헤더는 NERSC Perlmutter 기준이므로 `b300-01`에서는 `scripts/b300/` 래퍼를 쓴다). `S4` 이후 단계는 설계 동결 커밋(`f5c8569`)을 인자로 받으며, 끝난 실행은 해시가 같을 때 자동으로 건너뛴다.

| 단계 | 스크립트 | 하는 일 | 출력 |
|---|---|---|---|
| S1 | `scripts/s1_*.sh` | 라벨 열 대조, MC 최종 시험 72개 목록, 이상 block 기록, 공개 ROI 370개 정렬, 피질하 ROI 재구성과 점검 (CPU) | `manifests/s1/` |
| S2 | `scripts/s2_manifest.sh`, `s2_split_files.sh`, `s2_roi_cells.sh` | 분할, 내용 구역, 이름표 짝, ROI별 voxel 열, CAB-NP 13묶음, MC 표, 일치도, 8칸 좌표 (CPU) | `splits/hk_dev_v4/`, `manifests/s2/`, `<output_root>/s2_manifest/` |
| S3 | `scripts/s3_{vision,text,lowlevel,collect}.sh` | `V-JEPA 2`(40블록), `DeBERTa-large`(24층), 비교용 `VideoMAE`·`TimeSformer`·`CLIP`·`MPNet`·저수준 시각 특징 추출 (GPU) | `<output_root>/s3_features/` |
| S4 | `scripts/s4_{feature_model,ridge,window_change,collect}.sh` | 뇌 없는 Stimulus Model, 증류용 fold 밖 예측, `K1a` 14차원판, 정서어 제거판, 구역 제외, 비교용 특징판 (GPU) | `<output_root>/s4_no_brain/`, `<output_root>/s4_collect/` |
| S5 | `scripts/s5_{decoding,baselines,collect}.sh`, `scripts/b300/s5_mlbvae_b300.sbatch` | 뇌→64층 선형 복원 및 정서 기준선(`ridge`, `soft_bce`, `mlp`, `h2020`, `GED`, `ML-BVAE`, `EmoGrowth` 등) (GPU) | `<output_root>/s5_ridge/`, `<output_root>/s5_collect/` |
| S6 | `scripts/b300/s6_train_b300.sbatch`, `scripts/s6_train.sh` | 뇌 모델 학습 (`outer_fold1~6`, `zone_block<b>_fold<k>_{excluded,control}`, `final_for_mc`) (GPU) | `<output_root>/s6_brain/` |
| S9 | `scripts/s9_s10/s9_{interchange_and_pairs,pathway_k1_k1a,network_perturbation}.py` | 저장된 모델로 바꿔 끼우기(`2-2, 1-1`), 결합 지표 `I`(`1-2`), 쌍 비교(`O33`), `K1/K1a` 경로 평가, 13개 네트워크 교란(`6-4b`) (CPU) | `<output_root>/s9_analysis/`, `results/b300_hk_6fold/s9_summary/` |
| S10 | `scripts/s9_s10/{s10_metrics_and_tests,s10_finish_table7,s10_verdict_and_figures,generate_master_summary}.py` | `Table 1~7` 집계·부트스트랩 검정, `6-1` 사전등록 통합 판정표, 순수 벡터 논문 그림 6종 및 종합 요약 생성 (CPU) | `<output_root>/s10_tables_figures/`, `results/b300_hk_6fold/` |

### 뇌 모델 조건 이름

결과 폴더는 코드 이름을 쓰고, 논문과 결과 표는 묶음 이름(`A`~`E`)을 쓴다(`src/s6_common.py`의 `DISPLAY`).

| 묶음 | 이름 | 코드 이름 | Input → Output |
|---|---|---|---|
| A. 장면 정보를 쓰지 않음 | A-1 / A-2 | `brain_only` / `brain_only_distill` | Brain → Emotion (`-2`는 distillation 추가) |
| B. 특징을 학습 신호로만 | B-1 | `brain_only_featdec` | Brain → Emotion + Vision + Caption |
| C. 복원 특징 투입 (공유 encoder) | C-1 / C-2 | `brain_decoded` / `brain_decoded_distill` | Brain + Decoded Feature → Emotion |
| D. 특징 전용 고정 encoder 2 | D-1 / D-2 | `brain_decoded_sep` / `brain_decoded_sep_distill` | Brain + Decoded Feature → Emotion [separate encoder] |
| | D-3 / D-3 짝 | `brain_features_only` / `brain_features_only_paired` | Decoded Feature → Emotion [no direct path] |
| | D-4 | `brain_frozen_feature_encoder` | Brain → Emotion [frozen feature encoder] |
| E. 중간 표현 전달 | E-고정 / E-학습 | `brain_only_repr_frozen` / `brain_only_repr_trained` | Brain → Emotion [multimodal representation] |
| 변형·대조군·준비 모델 | — | `brain_decoded_additive`, `brain_decoded_grad`, `brain_only_pool`, `brain_decoded_pool`, `control_label_smoothing`, `control_stimulus_shuffle`, `control_feature_shuffle`, `feature_encoder`, `multimodal` | 상세 설명은 [OVERVIEW.md](OVERVIEW.md) 참고 |

## 단위 시험 및 그림·표 재생성 확인

```bash
# 1) 순수 합성 자료 단위 시험 (원자료·서버 경로 불필요, 클론 직후 바로 실행 가능)
bash scripts/s4_tests.sh
bash scripts/s5_tests.sh

# 2) 서버 환경 설정(configs/paths.yaml) 뒤 실행하는 단위 시험
bash scripts/s6_tests.sh   # <output_root>/s2_manifest/roi_voxels 필요
bash scripts/s3_tests.sh   # video_root 자극 영상, ffprobe, 오프라인 HF 캐시 필요

# 3) 추적된 요약표에서 S10 판정표·논문 그림 6종·MASTER_RESULTS_SUMMARY.md 재생성 확인
python3 scripts/s9_s10/s10_verdict_and_figures.py --base-dir results/b300_hk_6fold --mode all
python3 scripts/s9_s10/generate_master_summary.py --base-dir results/b300_hk_6fold
```
