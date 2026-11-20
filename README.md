# EmoBrain

정서 영상을 볼 때의 fMRI 반응에서 장면의 시각 정보와 의미 정보를 읽고, 그 정보를 써서 정서 평정 34개를 예측하는 연구의 코드다.
연구 내용은 [OVERVIEW.md](OVERVIEW.md), 설계 전체는 [docs/final/01_integrated_document.md](docs/final/01_integrated_document.md)에 있다.

## 디렉토리

```
README.md            디렉토리와 사용법 (이 파일)
OVERVIEW.md          연구 질문, 자료, 모델, 평가
configs/             서버마다 다른 경로와 실행 환경, 실행 설정
  paths.example.yaml   → paths.yaml로 복사해 고친다 (git 밖)
  env.example.sh       → env.sh로 복사해 고친다 (git 밖)
  s6/                  뇌 모델 실행 설정
splits/hk_dev_v4/    분할. 원본 표 두 개와 실행 단위별 영상 목록
manifests/           단계마다 만든 작은 표 (s1, s2, s3, s6)
data/                작은 입력 표 (정서 평정, 캡션, 자극 목록과 번호 대응)
src/                 코드. 단계 이름이 파일 앞에 붙는다 (s1_ ~ s6_)
scripts/             단계별 실행 스크립트 (.sh). 모두 레포 최상위에서 실행한다
tests/               합성 자료 시험. 실제 정답과 뇌 반응을 읽지 않는다
docs/final/          설계 문서(01~05)와 작업 기록
archive/             이전 설계의 코드와 문서. 지금 분석에 쓰지 않는다
external/            외부 레포 (git submodule)
```

큰 산출물(특징, 학습 결과, 로그)은 `configs/paths.yaml`의 `output_root`에 쓴다. 기본값은 레포의 `outputs/`이고 git에 올리지 않는다.

### 결과 폴더

`output_root`의 폴더 이름은 코드의 단계 번호(s1~s10)를 따르고, 폴더마다 README.md가 그 폴더가 무슨 분석인지, 무엇이 저장되는지, 안쪽 구조를 설명한다. README와 정리는 `bash scripts/output_layout.sh [--dry-run]`가 만든다(GPU 없음, 몇 초).

- `s6_brain_model/`: 뇌 모델 결과를 조건 이름으로 찾는 폴더. 주 비교(`main/`), 대조군(`control/`), 모델 한 부분만 바꾼 판(`ablation/`), 질문 하나를 위해 다시 학습한 것(`analysis/`)으로 나누고, 안의 fold 폴더는 학습 결과 폴더로 가는 상대 링크다
- `s9_saved_model_tests/`, `s10_stats/`: 질문마다 폴더 하나(ex) `6-4b_perturb/`)
- `checks/`: 논문에 쓰지 않는 점검 실행, `notes/`: 메모, `logs/`: 실행 기록
- 학습 결과 원본(`s6_brain_*`)과 s1~s5 폴더는 학습이 모두 끝난 뒤 같은 스크립트의 2단계로 옮긴다. 돌고 있는 학습이 그 경로를 읽고 쓰기 때문이다

## 설치와 설정

1. Python 3.11과 아래 패키지. 확인한 판은 괄호 안이다.
   - GPU 단계(S3~S6): PyTorch (2.11), NumPy (2.4), pandas (2.2), SciPy (1.15), scikit-learn (1.7), transformers (4.57), h5py
   - CPU 단계(S1, S2): NumPy (2.2), pandas (3.0), SciPy (1.17), scikit-learn (1.8), nibabel (5.4)
   - S3 저수준 특징: [pymoten](https://github.com/gallantlab/pymoten) 소스 폴더, h264 복호기가 있는 ffmpeg
2. 설정 파일 두 개를 만든다.
   ```bash
   cp configs/paths.example.yaml configs/paths.yaml   # data_root, output_root 등
   cp configs/env.example.sh configs/env.sh           # 단계별 Python 경로
   ```
3. `video_root`에 자극 영상 2,196개(`data/stimuli.tsv`의 path가 이 폴더 기준), `data_root` 아래에 원자료를 둔다: `Horikawa/sub-XX/v3_qc/`(fMRI 반응과 block 표), `MindCaptioning/sub-XX/v2_qc/`, `atlas_sources/`(공개 ROI와 지도). 원자료는 이 레포에 없다.

## 분할

`splits/hk_dev_v4/`가 분할의 전부다.

| 파일 | 내용 |
|---|---|
| `split_hk_dev.tsv` | 개발 영상 2,109개와 fold 번호(1~6). 원본 |
| `fold_roles.tsv` | 바깥 fold k를 시험으로 쓸 때 검증 fold와 학습 fold. 원본 |
| `outer_fold<k>/{train,val,test}.txt` | 실행 단위별 영상 번호 목록. 한 줄에 video_id 하나 |
| `final_for_mc/{train,val,test}.txt` | MC 전이용 최종 모델(시험 없음) |

목록 파일은 `bash scripts/s2_split_files.sh`가 원본 표 두 개에서 만들고 손으로 고치지 않는다. `--check`는 목록과 원본이 같은지만 본다. 뇌 모델(S6)은 목록 파일을 읽고 원본과 다르면 멈춘다. MindCaptioning 최종 시험 영상 72개와 같은 내용의 영상은 어느 목록에도 없다.

## 단계별 실행

모든 명령은 레포 최상위에서 실행한다. GPU 단계는 `sbatch scripts/<이름>.sh <인자>`로 낸다. Slurm으로 할당받은 compute node 안(salloc 등)에서는 `bash scripts/<이름>.sh <인자>`로 돌려도 된다. S6 본실험은 `scripts/s6_dispatch.sh`가 짧은 학습 묶음을 login node GPU에, 긴 묶음을 sbatch로 나눠 낸다(11/10). 그 밖의 GPU 단계는 sbatch로 낸다. 실제 결과를 내는 단계(S4 이후)는 설계 동결 커밋을 마지막 인자로 받고, 커밋되지 않은 코드로는 돌지 않는다. 끝난 실행은 코드, 입력, 설정이 같을 때만 건너뛰고, 다르면 섞지 않고 멈춘다.

| 단계 | 스크립트 | 하는 일 | 출력 |
|---|---|---|---|
| S1 | `s1_*.sh` | 라벨 열 대조, MC 최종 시험 72개 목록, 이상 block 기록, 공개 ROI 370개를 우리 격자로 옮기기, 피질하 ROI 다시 만들기와 점검 (CPU) | `manifests/s1/` |
| S2 | `s2_manifest.sh <stage>` | 분할, 내용 구역, 이름표 짝, ROI별 voxel 열, CAB-NP 13묶음, MC 표, 일치도 (CPU, 약 10분) | `splits/hk_dev_v4/`, `manifests/s2/` |
| S2 | `s2_split_files.sh [--check]` | 분할 원본에서 실행 단위별 목록 만들기 | `splits/hk_dev_v4/` |
| S2 | `s2_roi_cells.sh [--check]` | ROI마다 voxel 좌표 범위를 축마다 둘로 나눈 8칸의 칸 번호(입력층 점검의 칸 평균, CPU) | `<output_root>/s2_manifest/roi_cells/` |
| S3 | `s3_vision.sh`, `s3_text.sh`, `s3_lowlevel.sh`, `s3_collect.sh` | 영상과 캡션의 특징 추출. V-JEPA 2(block 40개), DeBERTa-large(층 24개), 비교용 VideoMAE, TimeSformer, CLIP, MPNet, 저수준 시각 특징 (GPU, 끊기면 이어서) | `<output_root>/s3_features/` |
| S4 | `s4_feature_model.sh <과제> <커밋>` | 뇌 없는 모델. Stimulus Model(Vision + Caption → Emotion)과 distillation용 fold 밖 예측, 14개 차원판, 정서어 제거판, 구역 제외, 비교용 특징판 (GPU) | `<output_root>/s4_no_brain/` |
| S4 | `s4_ridge.sh`, `s4_window_change.sh`, `s4_collect.sh` | V-JEPA 2 block별 ridge, 긴 영상의 window 변화, 점검과 요약 | 같은 폴더, `<output_root>/s4_collect/` |
| S5 | `s5_decoding.sh <참가자> <커밋>` | 뇌 → 층별 feature ridge decoding (GPU) | `<output_root>/s5_ridge/` |
| S5 | `s5_roi_map.sh <참가자> <커밋> [fold 목록]` | 370개 ROI 지도. ROI마다 그 ROI voxel만으로 정서 34개, Vision feature, Caption feature를 ridge로 decoding (GPU) | `<output_root>/s5_ridge/roi_map/` |
| S5 | `s5_baselines.sh <과제> <참가자> <커밋>` | 정서 기준선: ridge, soft BCE 선형, 영상 길이, 저수준, 뇌 전체 신호, Horikawa 2020 복셀 선택 ridge (GPU) | 같은 폴더 |
| S6 | `s6_train.sh <분할> <조건> <설정> <커밋>` | 뇌 모델 학습. 분할은 `outer_fold<k>`, `pilot_fold<k>`, `final_for_mc`, `zone_block<b>_fold<k>_<방식>` (GPU) | `<output_root>/s6_brain/` |
| S6 | `s6_weight_counts.sh <d 목록>` | 조건별 학습 가중치 수 (CPU) | `manifests/s6/weight_counts.tsv` |
| S6 | `s6_dispatch.sh <tag> <run worktree> <커밋> --variant <이름:설정:출력 폴더> [--conditions <조건>] [--dry-run]` | 본실험 조건을 fold와 변형마다 stream 4개로 나누고, 앞 조건의 선택이 나오는 대로 띄운다. 어림 시간이 짧은 stream은 빈 login node GPU에, 긴 stream은 청구 시간 상한 안에서 sbatch로 낸다. 상태 표로 다시 켜서 잇고, 실패한 stream은 다른 node에서 한 번 다시 띄운다. 의존과 나누는 규칙은 `scripts/s6_dispatch.py` 머리말 (CPU, 오래 도는 프로세스) | `<output_root>/logs/s6_dispatch_state_<tag>.tsv` |
| S6 | `s6_grid.sh <run worktree> <커밋> <설정> <출력 폴더> [--split 1e-05=2] [--together] [--dry-run]` | A-1 후보 grid(learning rate × 입력층 weight decay)를 learning rate별 묶음으로 나눠 빈 login node GPU에 띄운다. 같은 실행 번호로 돌려 dispatcher의 brain_only stream이 끝난 후보를 건너뛰고 선택만 한다. 규칙은 `scripts/s6_grid.py` 머리말 (CPU, 오래 도는 프로세스) | `<output_root>/logs/s6_grid_<출력 폴더 이름>/state.json` |
| S6 | `s6_queue.sh <tag> <run worktree> <커밋> <작업 TSV> [--nodes 17-40] [--share-own [--stack-mib 9000]] [--dry-run]` | 분할 여러 개(6-2 구역 분할, 6-4a 묶음, HK 최종 모델)를 빈 login node GPU에 차례로 띄운다. --share-own이면 우리 다른 작업이 있는 GPU도 메모리가 남으면 같이 쓰고, --stack-mib(작업 하나의 메모리 어림)를 주면 GPU 메모리 여유를 계산해 같은 GPU에 여러 작업을 올린다. 작업 하나가 s6_train 한 번이고, 사라진 작업은 한 번만 다시 띄운다. 24시간 넘는 작업은 받지 않는다. 규칙은 `scripts/s6_queue.py` 머리말 (CPU, 오래 도는 프로세스) | `<output_root>/logs/s6_queue_<tag>/state.json` |
| S6 | `s6_candidates.sh <run worktree> --plan <분할> --conditions <조건> --config <설정> --design-freeze <커밋> --target <조건>:<id>,<id>` | 한 조건의 후보 일부만 같은 실행 번호로 학습한다. src를 고치면 실행 번호가 바뀌므로 src 밖에서 run worktree의 s6_train을 불러 쓴다. `s6_grid.py --target`이 부른다 (GPU) | `<output_root>/<출력 폴더>/` |
| S6 | `s6_merge_lr.sh <본 실행 폴더> <learning rate 1e-4 실행 폴더> <합친 폴더> [--folds 1-6] [--conditions AC\|DE]` | 두 실행(learning rate 1e-3, 1e-4)을 조건과 fold마다 검증 r로 합친다. A-1은 본 실행 그대로, C-2는 합친 C-1의, D-2는 합친 D-1의 실행을 따른다. 한 실행에만 선택이 있으면 합치지 않고 missing으로 남긴다. 원래 결과는 옮기지 않고 symlink와 selected.json, merge_record.tsv를 만든다. 규칙은 `scripts/s6_merge_lr.py` 머리말 (CPU, 몇 초) | `<output_root>/<합친 폴더>/` |
| S8 | `s8_mc_transfer.sh <HK 최종 모델 폴더> <출력 폴더> <커밋> [조건] [seed] [참가자]` | 6-3 MC 시청 전이. HK 최종 모델(final_for_mc)의 공유 가중치를 고정하고 MC 참가자마다 입력층만 학습(O29의 검증 run으로 입력층 weight decay 선택)한 뒤 시험 영상 72개의 반복 평균 반응으로 채점한다. 규칙은 `src/s8_mc_transfer.py` 머리말 (GPU) | `<output_root>/<출력 폴더>/<조건>/seed<k>/mc-0X/` |
| S9 | `s9_saved_models.sh <swap|perturb> <S6 결과 폴더> <커밋> [fold 목록]` | 저장된 모델로 하는 분석. swap은 C-1의 바꿔 끼우기와 같은 크기의 무작위 변경 대조(2-2, 1-1, 1-2), perturb는 A-1과 C-1의 네트워크 13묶음, ROI 370개 입력 교란(6-4b). perturb는 참가자별 합과 함께 S10 재표집용 영상별 예측(float32, 6 fold 약 22 GB)을 쓴다. 결과 위치는 `S9_OUT`으로 바꾼다 (GPU, 학습 없음) | `<S9_OUT 또는 output_root/s9_saved_models>/<swap|perturb>/<S6 결과 폴더 이름>/` |
| S9 | `s9_path_eval.sh <S5 decoding 폴더> <S6 결과 폴더> <출력 폴더> <커밋> [--partial-check]` | 경로 평가(K1)와 14개 차원판(K1a)의 예측. 실제 특징으로 학습해 고정한 Stimulus Model(`s4_no_brain`)의 더하기 head와 상호작용 head에 ridge decoded features와 C-1 decoded features(selected.json의 seed)만 넣는다. 보정 전과 N8 보정판(H2 검증 fold 통계, 평균만 옮긴 차원 수), 읽은 head가 S4 저장 출력과 같은지 확인, 입력과 출력 sha256. 뇌 모델과 Stimulus Model은 더 학습하지 않는다. 규칙은 `src/s9_path_eval.py` 머리말 (CPU, 학습 없음, 몇 분) | `<출력 폴더>/units/`, `n8_counts.tsv`, `head_check.tsv`, `done.json` |
| S9 | `s9_stimulus_swap.sh <합친 S6 폴더> <출력 폴더> <커밋> [--brain-swap-dir <뇌 모델 S9 swap 폴더>]` | 바꿔 끼우기의 Stimulus Model 기준선(11/16). 2-2와 같은 짝, 같은 대조(같은 seed의 C 영상), 같은 지표로 실제 Vision feature와 Caption feature를 넣은 Stimulus Model(S4)을 바꿔 끼운다. 두 특징 표현 자체가 정서 예측을 얼마나 움직이는지의 기준이다. 더하기판과 상호작용판을 따로 내고, 뇌 모델 2-2와 짝과 대조 영상이 같은지 확인한다. 통계는 `s10_swap.sh`로 낸다. 규칙은 `src/s9_stimulus_swap.py` 머리말 (CPU, 학습 없음) | `<출력 폴더>/<additive\|interaction>/outer_fold<k>_seed0/` |
| S10 | `s10_performance.sh <S6 결과 폴더> <출력 폴더> <커밋> --dk-mean <participant\|rows\|videos> [--split-content-pairs]` | 저장된 시험 예측으로 주 지표(참가자마다 정서별 r, 6 fold를 모아 한 번), R², MAE(평정 0과 0 초과), 평균 예측 대비 오차 감소, bootstrap 구간, 2-3 [사전] 여섯 비교와 보조 비교, 0행 전제 검정(순열, Holm 2개), 5명 공통 영상판, seed 평균과 표준편차, 그림. --dk-mean과 --split-content-pairs는 문서가 정하지 않은 선택이라 기본값이 없다. 규칙은 `src/s10_performance.py` 머리말 (CPU, 몇 분) | `<출력 폴더>/{all,common5}/`, `prereg_pvalues.tsv` |
| S10 | `s10_feature_decoding.sh <S5 decoding 폴더> <출력 폴더> <커밋> [--s6-dir <S6 결과 폴더>]` | 2-1 [사전] 2개. ridge decoding(층 예측을 이어 붙인 Vision feature, Caption feature)의 차원별 r 평균 대 순열 기준(실제 특징 벡터를 같은 fold, 같은 run 안에서 섞음), bootstrap 구간, 같은 fold 안 영상 식별. --s6-dir면 C-1 decoded features도 같은 지표로 낸다. 규칙은 `src/s10_feature_decoding.py` 머리말 (CPU, 참가자당 몇 분) | `<출력 폴더>/decoding_scores.tsv`, `prereg_pvalues.tsv` |
| S10 | `s10_swap.sh <S9 swap 폴더> <출력 폴더> <커밋>` | 2-2 [사전] 3개(시각만, 캡션만, 둘 다 교체 대 같은 크기 무작위 변경), 1-1 정서별 경로 효과 차이, 1-2 (나) 결합 지표, Kragel 묶음 보조 비교. 짝 연결 묶음 bootstrap, 묶음 크기 분포. 규칙은 `src/s10_swap.py` 머리말 (CPU, 몇 분) | `<출력 폴더>/swap_scores.tsv`, `prereg_pvalues.tsv` |
| S10 | `s10_zone.sh <S6 구역 결과 폴더> <출력 폴더> <커밋> [--constant-prediction-scope participant\|all]` | 6-2 [사전] 처음 보는 장면. 구역별 평가 정서, 다섯 구역 평균 성능, 학습량 대조 대비 하락폭, 두 모델 차이(더 높다, 덜 떨어진다를 따로), 정서별 0이 아닌 학습 영상 수, 시험 쪽 평정 분포, C-1 decoded features. 분할이 모두 있어야 최종 표를 낸다 (CPU, 1분 안팎) | `<출력 폴더>/zone_summary.tsv`, `prereg_pvalues.tsv` |
| S10 | `s10_network.sh <S6 작업 TSV> <출력 폴더> <커밋> --network-bh-family by_model\|pooled` | 6-4a 묶음만으로 학습한 A-1, C-1의 성능과 순열 p, 1-3 [사전] 3개(Visual1, Visual2, Default), 나머지 탐색 BH, C-1 decoded features, 묶음 일치도. BH 묶음은 문서가 정하지 않아 기본값이 없다 (CPU, 몇 분) | `<출력 폴더>/network_scores.tsv`, `prereg_pvalues.tsv` |
| S10 | `s10_perturb.sh <S9 perturb 폴더> <출력 폴더> <커밋> --repeat-handling fixed\|resample --drop-bh-family by_model\|pooled [--s6-dir <S6 결과 폴더>]` | 6-4b 13묶음과 ROI 370개 교란의 모델별 성능 하락과 하락폭 차이(C-1 − A-1). S9의 영상별 예측으로 1부와 같은 영상 단위 bootstrap 구간과 중심 맞춘 p, 13묶음 하락폭 차이 Holm(5명 평균, 참가자마다), 나머지 탐색 BH(ROI판, 묶음 안 정서별, 각 모델 하락)와 보정 묶음. 두 선택은 문서가 정하지 않아 기본값이 없다. 6 fold가 모두 있어야 최종 표를 낸다 (CPU node 권장, sbatch) | `<출력 폴더>/network_drops.tsv`, `network_confirmed.tsv`, `roi_drops.tsv` |
| S10 | `s10_mc.sh <S8 결과 폴더> <출력 폴더> <커밋> [--constant-prediction-scope unit\|all]` | 6-3 MC 시청 전이. 참가자, seed마다 72개 영상의 정서별 r, 평정 상수 정서 제외, 순열 기준과 두 모델 차이(보정 없음), seed 평균과 표준편차, C-1 decoded features. S8 확인용 실행은 거절한다 (CPU, 몇 초) | `<출력 폴더>/mc_scores.tsv`, `mc_comparison.tsv` |
| S10 | `s10_sensitivity.sh <출력 폴더> <커밋> --pair "이름\|A 폴더\|A 조건\|B 폴더\|B 조건" ...` | 다른 S6 결과 폴더의 두 모델을 같은 시험 행에서 비교한다(F7 ROI token 평균판 대 emotion query판, F3 block 2개, 4개 대 1개). 정서별 r의 차이, 참가자 점수 차이, 영상 단위 bootstrap 구간과 중심 맞춘 p, 정서별 BH(탐색). Holm 15개에 넣지 않는다 (CPU, 몇 분) | `<출력 폴더>/per_emotion.tsv`, `scores.tsv` |
| S10 | `s10_k1.sh <S9 경로 평가 폴더> <S6 결과 폴더> <S5 ridge 폴더> <출력 폴더> <커밋>` | K1: A-1과 경로 평가(ridge판, C-1판 × head 둘 × 보정 전과 보정판)의 정서별 r과 참가자 점수, 경로 평가 − A-1의 차이와 구간(p와 비율 없음). 14개 차원 표 하나: (1) B4 ridge, (2) 실제 특징 Stimulus Model, (3) decoded features Stimulus Model과 (3) − (1)의 차이, 구간, BH(14개), 평정 신뢰도 [미확인]. seed는 selected.json이 적은 것(A-1과 C-1이 같아야 함), seed 평균과 표준편차(2개 이상일 때). fold나 seed가 아닌 입력이 빠지면 최종 표를 내지 않는다 (CPU, 1분 안팎) | `<출력 폴더>/k1_*.tsv`, `dimensions14.tsv` |
| S10 | `s10_geometry.sh fit <출력 폴더> <커밋> <참가자>`, `s10_geometry.sh summarize <출력 폴더> <커밋>` | 네트워크별 정서 표현 형식 탐색(11/16, 결과를 본 뒤 더한 탐색). 네트워크 13개마다 ridge로 정서 34개와 차원 14개를 바깥 fold와 6-2 구역 분할에서 맞히고, (a) 내용을 넘는 일반화, (b) VA를 거치는 길, (c) VA 최근접 짝과 이름표 최근접 짝의 구분, 평정만의 기준을 낸다. 규칙은 `src/s10_geometry.py` 머리말 (CPU, 참가자당 15분 안팎) | `<출력 폴더>/fit/sub-0X.npz`, `a_content_generalization.tsv`, `b_dimension_route.tsv`, `c_matched_pairs.tsv`, `rating_reference.tsv` |
| S10 | `sbatch --export=ALL,OUT=<출력 폴더>,FREEZE=<커밋> scripts/s10_geometry_checks.sh`(참가자 × 변형 25개 배열), `s10_geometry_checks.sh summarize <출력 폴더> <커밋>` | geometry 확인(11/16). 네트워크 13개의 valence, arousal 일반화에 구간(같은 내용 영상 묶음 bootstrap), 뇌 전체 신호 제거, 크기 맞춤(가장 작은 네트워크 크기로 세 번)을 더하고, 내용 구역 5개 × 차원 높음, 낮음의 10개 조건으로 CCGP와 shattering dimensionality(Bernardi 외, 2020)를 낸다. 규칙은 `src/s10_geometry_checks.py` 머리말 (CPU, fit 하나 30~40분) | `<출력 폴더>/fit/sub-0X_<변형>.npz`, `a_drop.tsv`, `ccgp_sd.tsv`, `pairwise.tsv`, `dichotomies.tsv` |
| S10 | `s10_rating_parts.sh parts <출력 폴더> <커밋>`, `s10_rating_parts.sh fit <출력 폴더> <커밋> <참가자>`, `s10_rating_parts.sh summarize <출력 폴더> <커밋>` | 평정을 부분으로 나눠 영역마다 읽기(01 6-4c, 11/16). valence를 Vision feature로 예측되는 부분과 나머지(그 가운데 Caption feature로 예측되는 부분)로, 정서 범주를 valence, arousal로 예측되는 부분과 나머지(Caption feature, Vision feature로 예측되는 부분)로 나누고, 네트워크 13개마다 각 부분을 ridge로 읽는다. 규칙은 바깥 fold마다 D_k로만 정한다. 미리 적은 가설과 대비는 `src/s10_rating_parts.py` 머리말 (CPU, 참가자당 몇 분) | `<출력 폴더>/parts.npz`, `parts_features_only.tsv`, `parts_brain.tsv`, `parts_brain_emotion_mean.tsv`, `contrast.tsv` |
| S10 | `s10_beyond_scene.sh targets <출력 폴더> <커밋>`, `s10_beyond_scene.sh fit <출력 폴더> <커밋> <참가자>`, `s10_beyond_scene.sh summarize <출력 폴더> <커밋>` | 장면 표현으로 선형으로 얻어지지 않는 정서 평정 정보(01 6-4d, 11/17). 장면 표현(motion energy + 이름표 73개, Vision feature, Caption feature, 넷 모두)으로 교차 예측한 부분을 뺀 정서 평정(범주 34개, valence, arousal)을 네트워크 13개와 뇌 전체에서 ridge로 읽는다. 판정 규칙과 예측은 계산 전에 `src/s10_beyond_scene.py` 머리말에 적었다 (CPU, 참가자당 10~20분) | `<출력 폴더>/targets.npz`, `features_only.tsv`, `fit/sub-0X.npz`, `scores.tsv`, `counts.tsv`, `predictions.tsv` |
| S10 | `s10_mc_ridge.sh <s8_mc 폴더> <출력 폴더> <커밋>` | 6-3의 ridge 기준선(11/17). MC 참가자마다 자기 시청 학습 자료로 맞춘 voxel ridge와 ROI 평균 ridge, HK에서 맞춘 ROI 평균 ridge를 MC에 그대로 적용한 전이를, 같은 72개 영상에서 A-1, C-1 전이와 비교한다. 규칙은 `src/s10_mc_ridge.py` 머리말 (CPU, 몇 분) | `<출력 폴더>/scores.tsv`, `comparison.tsv`, `per_emotion.tsv` |
| S8 | `s8_mc_individual.sh train <s6_brain_final_for_mc> <출력 폴더> <커밋> <참가자>`, `s8_mc_individual.sh perturb ...` | 공통과 개인차(11/17). MC 참가자마다 같은 구조의 개인 모델(A-1, C-1)을 그 사람 자료로만 학습하고, 6-3의 공통(전이) 모델과 함께 네트워크 교란을 걸어 개인 모델이 더 기대는 네트워크를 찾는다. 예측과 판정은 `src/s8_mc_individual.py` 머리말 (GPU, 참가자당 1~2시간) | `<출력 폴더>/<조건>/seed0/mc-0X/`, `perturb_drops.tsv`, `perturb_difference.tsv`, `prediction.tsv` |
| S6, S8 | `nohup bash scripts/s6_final_for_mc_b1_d_chain.sh <run worktree> <커밋> > <log> &`, 그다음 `s8_mc_transfer.py --final <s6_brain_final_for_mc_b1_d> --conditions brain_only_featdec,brain_decoded_sep,brain_features_only,brain_frozen_feature_encoder --seeds 0` | MC 전이를 B-1, D-1, D-3, D-4로 넓힘(11/17, 01 6-3). HK 전체 모델을 seed 0으로 학습하고(설정 configs/s6/run_config_final_for_mc_b1_d.json, fold 밖 encoder 2 다섯), MC 입력층을 HK에서 배운 목표와 같게 맞춘다. 규칙은 `src/s8_mc_transfer.py` 머리말 (GPU, HK 약 1일, MC 약 100 GPU 시간) | `<s6_brain_final_for_mc_b1_d>/final_for_mc/`, `<s8 출력>/<조건>/seed0/mc-0X/`, `<s8 출력>/encoder2*/` |
| S10 | `s10_imagery_prereg.sh [출력 폴더]` | 회상 질문 3의 예측 변수(01 6-3). 정서 34개마다 Vision feature만, Caption feature만으로 사람 평정을 예측한 r(6-4d의 beyond_scene/features_only.tsv)의 비. 뇌 자료 없음. 11/17에 고정한 파일이 있으면 덮어쓰지 않고 바이트 단위로 같은지만 확인한다 (CPU, 1초) |
| S10 | `s10_imagery.sh <s6_brain_final_for_mc> <s8_mc> <회상 반응 폴더> <V/C 지수 파일> <출력 폴더> <커밋>` | MC 회상 분석(11/17, 01 6-3). 6-3 전이 모델(A-1, C-1, seed 3개, 입력층까지 고정)에 회상 블록 반응(QC 통과 반복 평균)을 넣어 Q1~Q3를 판정하고, 네트워크 ablation(Q4)과 단서 구간(보조)을 낸다. 회상 반응은 레포 밖에서 시청 v2와 같은 계산으로 만든다 (CPU, 수십 분) | `<출력 폴더>/q1.tsv`, `q2.tsv`, `q3.tsv`, `ablation.tsv`, `cue.tsv` |
| S10 | `s10_per_emotion.sh <S6 최종 결과 폴더> <s8_mc 폴더> <V/C 지수 파일> <출력 폴더> <커밋>` | 정서별 모델 비교(11/17, 01 6-4e (가)). A-1에 대해 B-1, C-1, D-1, D-3, D-4, E-고정, E-학습의 정서별 차이(HK)와 C-1 − A-1(MC), 두 자료에서 정서별 차이가 재현되는지(판정 있음), Vision 대 Caption 지수와의 관계. 저장된 예측만 읽음. 규칙은 `src/s10_per_emotion.py` 머리말 (CPU, 몇 분) | `<출력 폴더>/differences.tsv`, `counts.tsv`, `replication.tsv`, `vc_index.tsv` |
| S10 | `s10_residual_ceiling.sh` | 6-4d 잔차의 noise ceiling(11/18). 평정자 수(추정)로 영상마다 이항 표본 잡음 분산을 내고, 판(평정 그대로, Sw, V, C, Sall 잔차)과 범주마다 잡음이 아닌 분산의 비율과 r 상한, 6-4d 뇌 decoding r의 상한 대비 비율 (CPU, 수 초) | `<s10_stats>/beyond_scene/residual_ceiling/ceiling.tsv`, `ceiling_with_decoding.tsv`, `summary.tsv` |
| S10 | `s10_mc_dgroup.sh` | MC 전이 확장의 D-3, D-4를 A-1, C-1(seed 0)과 비교(11/18, 01 6-3의 결과 전 읽는 규칙). 34개판과 27개판, 72개 영상 단위 bootstrap 구간, 같은 방향 참가자 수, 판정 (CPU, 1분 안쪽) | `<s10_stats>/6-3_mc_dgroup/scores.tsv`, `differences.tsv`, `per_emotion.tsv` |
| S10 | `s10_key_test.sh` | 핵심 시험 첫 판(11/18, 06 4절). 정서 27개마다 뇌 없이 낸 r(캡션 → 평정) − r(Sw → 평정)과, 뇌가 읽은 r(Sw 잔차) − r(캡션 잔차), 기준선 r × √(1 − R²). 6-4d 저장값만 씀. 정서 이름표 순열 (CPU, 수 초) | `<s10_stats>/key_test_v1/`, `key_test_v2_N_C/`, `key_test_v2_N_NA/`, `key_test_v2_NA_C/`의 `points.tsv`, `summary.tsv` |
| S3 | `s3_caption_levels.sh prep`, `s3_caption_levels.sh embed` | 캡션을 내용 수준으로 나눈 Caption feature(11/18). `graph`, `graph_levels`, `embed_graph`는 scene graph parser 판(물체, 물체 + 속성, object relations까지)과 단어를 섞은 판을 만든다. 물체(명사), 물체 + 속성(+ 형용사, 수사) 단어만 남기고 정서어를 뺀 캡션을 DeBERTa-large 6/12/18/24층으로 임베딩. prep은 spaCy 환경(CPU), embed는 GPU | `<s3_features>/deberta_objects/target.npy`, `deberta_objattr/target.npy`, `caption_levels_work/` |
| S2 | `s2_caption_blocks.sh` | Dec-바 캡션 구역(11/18). Caption feature 정서어 제거판의 PCA 50개에서 k-means 5개, 4-3과 같은 분할, 학습량 대조 표본, 거리 점검. 대표 캡션 원문은 레포 밖에 쓴다 (CPU, 1분 안쪽) | `manifests/s2/caption_blocks_assignment.tsv`, `caption_block_control_samples.tsv`, `caption_block_distance.tsv` 등, `<output_root>/s2_manifest/caption_blocks_samples.tsv` |
| S6 | `s6_train.sh capzone_block<b>_fold<k>_<excluded\|control> brain_only <configs/s6/run_config_capzone.json> <커밋>` | Dec-바 상황 묶음 빼고 시험(11/18). 6-2와 같은 규칙에 캡션 구역을 쓴다. 60개는 `scripts/s6_queue.py`로 띄운다 (GPU, 하나 약 1~1.5시간) | `<S6_OUT=s6_brain_capzone>/capzone_block<b>_fold<k>_<kind>/brain_only/` |
| S9 | `s9_untrained_encoder.sh train <fold 번호들> <run_config_grid_main.json> <s6_brain_grid_main> <출력 폴더>`, `s9_untrained_encoder.sh summarize <s6_brain_grid_main> <출력 폴더>` | D-4 대조(11/18). 학습하지 않은 encoder 2를 고정하고 D-4와 같은 짝, 후보, head 학습. HK 주 비교의 코드판(1bca774) 위에서만 돌고 실행 번호가 D-4 선택과 다르면 멈춘다. 규칙은 `src/s9_untrained_encoder.py` 머리말 (GPU, fold 하나 약 30분) | `<출력 폴더>/outer_fold<k>/brain_frozen_untrained_encoder/`, `summary/` |
| S10 | `S10_LEVELS=1 s10_beyond_scene.sh targets|fit|summarize <출력 폴더> <커밋> [참가자]` | 6-4d에 캡션 내용 수준 판(N, NA)을 더한 판(11/18). 기존 판정 규칙 그대로, 새 판은 함께 보고 (CPU, 참가자당 2~3분) | `<출력 폴더>`(beyond_scene과 같은 구성) |
| S9 | `CUDA_VISIBLE_DEVICES=<번호> s9_perturb_models.sh <S6 최종> <s6_brain_depth2> <s6_brain_depth4> <출력 폴더> <커밋>` | 네트워크 교란의 모델 확장과 정서 head 입력 표현 저장(11/17, 01 6-4e (나), (다)). A-1, C-1, B-1, D-4, E-고정, E-학습에 6-4b와 같은 13묶음 교란, A-1 depth2, depth4는 표현 기준으로만. 규칙은 `src/s9_perturb_models.py` 머리말 (GPU 1장, 약 1시간) | `<출력 폴더>/outer_fold<k>_seed0/pred.npz`, `perturbed_<조건>.npy`, `repr.npz` |
| S10 | `s10_perturb_models.sh <s9_perturb_models 출력> <6-4b S9 폴더> <출력 폴더> <커밋>` | 위 결과의 하락, 하락폭 차이(모델 − A-1), D-4 예측 판정, 모델 쌍의 CKA와 판정. 질문과 판정은 `src/s10_perturb_models.py` 머리말 (CPU, 수십 분) | `<출력 폴더>/network_drops.tsv`, `prediction.tsv`, `cka.tsv`, `cka_decision.tsv` |
| S10 | `s10_holm15.sh <출력 파일> <p 파일>... [--seed 0] [--alpha <값>]` | [사전] 15개의 Holm 보정(5명 평균, 참가자마다). 15개가 다 모이지 않으면 없는 것을 적고 보정 값을 내지 않는다 (CPU, 몇 초) | `<출력 파일>`, `*_missing.tsv`, `*_counts.tsv` |

S6의 결과 폴더 구조와 저장 형식은 [src/s6_train.py](src/s6_train.py) 머리말에 있다.

### 뇌 모델 조건 이름

결과 폴더는 코드 이름을 쓰고, 논문과 결과 표는 묶음 이름(A~E)을 쓴다. 대응은 `src/s6_common.py`의 `DISPLAY`에 있다. 조건의 Input, Output, loss는 [OVERVIEW.md](OVERVIEW.md)와 01의 5-A에 있다.

| 묶음 | 이름 | 코드 이름 | Input → Output |
|---|---|---|---|
| A. 장면 정보를 쓰지 않음 | A-1 | `brain_only` | Brain → Emotion |
| | A-2 | `brain_only_distill` | Brain → Emotion [distillation] |
| B. feature를 학습 신호로만 | B-1 | `brain_only_featdec` | Brain → Emotion + Vision + Caption |
| C. decoded feature를 정서 계산에, 공유 encoder | C-1 | `brain_decoded` | Brain + Decoded Feature → Emotion |
| | C-2 | `brain_decoded_distill` | Brain + Decoded Feature → Emotion [distillation] |
| D. 장면 특징으로만 학습해 고정한 encoder 2 | D-1 | `brain_decoded_sep` | Brain + Decoded Feature → Emotion [separate feature encoder] |
| | D-2 | `brain_decoded_sep_distill` | Brain + Decoded Feature → Emotion [separate feature encoder, distillation] |
| | D-3 | `brain_features_only` | Decoded Feature → Emotion [separate feature encoder, no direct path] |
| | D-4 | `brain_frozen_feature_encoder` | Brain → Emotion [frozen feature encoder] |
| | D-3 짝(비교용) | `brain_features_only_paired` | D-3을 D-4와 같은 짝 방식으로 학습한 판 |
| E. 중간 표현 전달 | E-고정 | `brain_only_repr_frozen` | Brain → Emotion [representation, frozen head] |
| | E-학습 | `brain_only_repr_trained` | Brain → Emotion [representation, trained head] |

-2는 같은 묶음의 -1에 distillation(Stimulus Model 예측)을 더한 조건이다. 변형, 대조군, 준비 모델은 다음과 같다.

| 이름 | 코드 이름 |
|---|---|
| C-1 더하기 head, C-1 손실 흐름 허용판(stop-gradient 없음, 성능 비교에만) | `brain_decoded_additive`, `brain_decoded_grad` |
| A-1, C-1 ROI token 평균판(emotion query 34개 대신 ROI token 370개 평균. 정서마다 그 평균 벡터의 선형 함수) | `brain_only_pool`, `brain_decoded_pool` |
| A-2 대조군(label smoothing, Stimulus 예측 섞기), B-1 대조군(feature 짝 섞기) | `control_label_smoothing`, `control_stimulus_shuffle`, `control_feature_shuffle` |
| encoder 2(feature만 학습. D 묶음이 같이 씀). 학습 fold 하나씩 뺀 fold 밖 encoder 2 넷은 `feature_encoder_oof/`에 저장 | `feature_encoder` |
| Multimodal Model(Brain + Vision + Caption → Emotion. E의 준비) | `multimodal` |

## 시험

```bash
bash scripts/s3_tests.sh   # 약 1분
bash scripts/s4_tests.sh   # 약 2분
bash scripts/s5_tests.sh   # 약 2분
bash scripts/s6_tests.sh   # 약 2분
python tests/s6_dispatch_tests.py   # 약 2분. S6 dispatcher의 의존 순서, 다시 켜기, 실패 처리, 동결 확인. ssh와 GPU를 쓰지 않는다
python tests/s6_merge_tests.py   # 몇 초. 두 실행을 합치는 규칙(검증 r, 같으면 작은 learning rate, 0 후보, C-2와 D-2가 앞 조건을 따름, 짝 학습 D-4, 한쪽만 끝난 조건)
python tests/s6_queue_tests.py   # 몇 초. 분할 실행기의 작업 목록 확인, 빈 node에만 띄우기, 끝남 판정, 한 번만 다시 띄우기, GPU 같이 쓰기(--share-own)
python tests/s8_tests.py   # src에서 실행. 몇 초. MC 전이의 공유 가중치 고정, 입력층만 학습, 시험 반복 평균, 빠진 run 행, MC 72개 경계, 후보 선택
python tests/s9_tests.py   # 몇 분. ROI 입력 교체와 token 교체가 같음, 다른 영상 배정표, 13묶음과 ROI 370개, 합으로 낸 r, 영상별 예측(float32)의 합이 저장된 합과 같음, 쓰는 중인 fold 감지, 바꿔 끼우기
python tests/s9_stimulus_swap_tests.py   # src에서 실행. 1분 안팎. Stimulus Model 바꿔 끼우기 기준선의 더하기 head I = 0, 대조 길이, 대조 영상 C, Δy, 저장 형식
python tests/s10_geometry_checks_tests.py   # src에서 실행. 몇 초. 무게 AUC, kernel ridge = main_version, dichotomy 126개와 조건 쌍, 전역 신호 회귀, 크기 맞춤 뽑기
python tests/s10_rating_parts_tests.py   # src에서 실행. 몇 초. 시험 fold 평정이 규칙에 들어가지 않음, literature_version과 같음, 안쪽 겹 바깥 예측
python tests/s10_beyond_scene_tests.py   # src에서 실행. 몇 초. band 하나 = crossfit, band 무게, 상수 열, 시험 fold 평정 무관, 판정 규칙
python tests/s10_mc_ridge_tests.py   # src에서 실행. 몇 초. ROI 평균, 표준화, ridge = main_version
python tests/s10_per_emotion_tests.py   # 몇 초. 순위 상관, 이름표 순열, 편상관
python tests/s10_mc_dgroup_tests.py   # 몇 초. 판정 규칙, 구간, 27개판, 조건 사이 사람 평정 불일치에서 멈춤
python tests/s10_perturb_models_tests.py   # 몇 초. CKA 불변성, CKA 판정
bash scripts/s10_tests.sh   # 약 3분. 1부: 모은 r과 계산 불가, R²와 MAE 정의, bootstrap 구간과 p의 식, block 안 순열, Holm과 BH, 합친 S6 폴더 끝에서 끝까지(0 후보 fold, D-4 ensemble, 빠진 fold), [사전] 15개 Holm, 그림. 2부: 특징 순열과 짝 열 가중 r, 2-1, 2-2(audition_codex와 같은 효과, 묶음 재표집), 6-4b(영상별 예측의 재표집, Holm 13, BH 묶음), 6-2, 6-4a, 6-3의 규칙과 빠진 입력 거절. K1과 14개 차원: decoded features의 눈금 바꾸기와 head 출력의 손 계산, N8 보정과 평균만 옮기는 차원, head 출처 확인, selected.json의 seed와 A-1, C-1 seed 대조, 같은 seed 짝, K1에 p가 없음, (3) − (1) 차이와 BH 묶음, 출처 대조와 빠진 입력 거절
```

합성 자료로 자료 경계(시험 영상, MC 72개), 후보값, 선택 규칙, 출처 기록, 저장 형식을 확인한다. 실제 정답과 뇌 반응은 읽지 않는다.

## 문서

- [OVERVIEW.md](OVERVIEW.md): 연구 내용 요약
- [docs/final/01_integrated_document.md](docs/final/01_integrated_document.md): 설계와 결정의 근거
- [docs/final/04_claude_code_workorder.md](docs/final/04_claude_code_workorder.md): 단계별 작업 지시와 실행 기록
