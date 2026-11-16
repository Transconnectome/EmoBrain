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
| S10 | `s10_performance.sh <S6 결과 폴더> <출력 폴더> <커밋> --dk-mean <participant\|rows\|videos> [--split-content-pairs]` | 저장된 시험 예측으로 주 지표(참가자마다 정서별 r, 6 fold를 모아 한 번), R², MAE(평정 0과 0 초과), 평균 예측 대비 오차 감소, bootstrap 구간, 2-3 [사전] 여섯 비교와 보조 비교, 0행 전제 검정(순열, Holm 2개), 5명 공통 영상판, seed 평균과 표준편차, 그림. --dk-mean과 --split-content-pairs는 문서가 정하지 않은 선택이라 기본값이 없다. 규칙은 `src/s10_performance.py` 머리말 (CPU, 몇 분) | `<출력 폴더>/{all,common5}/`, `prereg_pvalues.tsv` |
| S10 | `s10_feature_decoding.sh <S5 decoding 폴더> <출력 폴더> <커밋> [--s6-dir <S6 결과 폴더>]` | 2-1 [사전] 2개. ridge decoding(층 예측을 이어 붙인 Vision feature, Caption feature)의 차원별 r 평균 대 순열 기준(실제 특징 벡터를 같은 fold, 같은 run 안에서 섞음), bootstrap 구간, 같은 fold 안 영상 식별. --s6-dir면 C-1 decoded features도 같은 지표로 낸다. 규칙은 `src/s10_feature_decoding.py` 머리말 (CPU, 참가자당 몇 분) | `<출력 폴더>/decoding_scores.tsv`, `prereg_pvalues.tsv` |
| S10 | `s10_swap.sh <S9 swap 폴더> <출력 폴더> <커밋>` | 2-2 [사전] 3개(시각만, 캡션만, 둘 다 교체 대 같은 크기 무작위 변경), 1-1 정서별 경로 효과 차이, 1-2 (나) 결합 지표, Kragel 묶음 보조 비교. 짝 연결 묶음 bootstrap, 묶음 크기 분포. 규칙은 `src/s10_swap.py` 머리말 (CPU, 몇 분) | `<출력 폴더>/swap_scores.tsv`, `prereg_pvalues.tsv` |
| S10 | `s10_zone.sh <S6 구역 결과 폴더> <출력 폴더> <커밋> [--constant-prediction-scope participant\|all]` | 6-2 [사전] 처음 보는 장면. 구역별 평가 정서, 다섯 구역 평균 성능, 학습량 대조 대비 하락폭, 두 모델 차이(더 높다, 덜 떨어진다를 따로), 정서별 0이 아닌 학습 영상 수, 시험 쪽 평정 분포, C-1 decoded features. 분할이 모두 있어야 최종 표를 낸다 (CPU, 1분 안팎) | `<출력 폴더>/zone_summary.tsv`, `prereg_pvalues.tsv` |
| S10 | `s10_network.sh <S6 작업 TSV> <출력 폴더> <커밋> --network-bh-family by_model\|pooled` | 6-4a 묶음만으로 학습한 A-1, C-1의 성능과 순열 p, 1-3 [사전] 3개(Visual1, Visual2, Default), 나머지 탐색 BH, C-1 decoded features, 묶음 일치도. BH 묶음은 문서가 정하지 않아 기본값이 없다 (CPU, 몇 분) | `<출력 폴더>/network_scores.tsv`, `prereg_pvalues.tsv` |
| S10 | `s10_perturb.sh <S9 perturb 폴더> <출력 폴더> <커밋> --repeat-handling fixed\|resample --drop-bh-family by_model\|pooled [--s6-dir <S6 결과 폴더>]` | 6-4b 13묶음과 ROI 370개 교란의 모델별 성능 하락과 하락폭 차이(C-1 − A-1). S9의 영상별 예측으로 1부와 같은 영상 단위 bootstrap 구간과 중심 맞춘 p, 13묶음 하락폭 차이 Holm(5명 평균, 참가자마다), 나머지 탐색 BH(ROI판, 묶음 안 정서별, 각 모델 하락)와 보정 묶음. 두 선택은 문서가 정하지 않아 기본값이 없다. 6 fold가 모두 있어야 최종 표를 낸다 (CPU node 권장, sbatch) | `<출력 폴더>/network_drops.tsv`, `network_confirmed.tsv`, `roi_drops.tsv` |
| S10 | `s10_mc.sh <S8 결과 폴더> <출력 폴더> <커밋> [--constant-prediction-scope unit\|all]` | 6-3 MC 시청 전이. 참가자, seed마다 72개 영상의 정서별 r, 평정 상수 정서 제외, 순열 기준과 두 모델 차이(보정 없음), seed 평균과 표준편차, C-1 decoded features. S8 확인용 실행은 거절한다 (CPU, 몇 초) | `<출력 폴더>/mc_scores.tsv`, `mc_comparison.tsv` |
| S10 | `s10_sensitivity.sh <출력 폴더> <커밋> --pair "이름\|A 폴더\|A 조건\|B 폴더\|B 조건" ...` | 다른 S6 결과 폴더의 두 모델을 같은 시험 행에서 비교한다(F7 평균 pooling판 대 query판, F3 block 2개 대 1개). 정서별 r의 차이, 참가자 점수 차이, 영상 단위 bootstrap 구간과 중심 맞춘 p, 정서별 BH(탐색). Holm 15개에 넣지 않는다 (CPU, 몇 분) | `<출력 폴더>/per_emotion.tsv`, `scores.tsv` |
| S10 | `s10_k1.sh <S9 경로 평가 폴더> <S6 결과 폴더> <S5 ridge 폴더> <출력 폴더> <커밋>` | K1: A-1과 경로 평가(ridge판, C-1판 × head 둘 × 보정 전과 보정판)의 정서별 r과 참가자 점수, 경로 평가 − A-1의 차이와 구간(p와 비율 없음). 14개 차원 표 하나: (1) B4 ridge, (2) 실제 특징 Stimulus Model, (3) decoded features Stimulus Model과 (3) − (1)의 차이, 구간, BH(14개), 평정 신뢰도 [미확인]. seed는 selected.json이 적은 것(A-1과 C-1이 같아야 함), seed 평균과 표준편차(2개 이상일 때). fold나 seed가 아닌 입력이 빠지면 최종 표를 내지 않는다 (CPU, 1분 안팎) | `<출력 폴더>/k1_*.tsv`, `dimensions14.tsv` |
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
| A-1, C-1 평균 pooling판 | `brain_only_pool`, `brain_decoded_pool` |
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
bash scripts/s10_tests.sh   # 약 3분. 1부: 모은 r과 계산 불가, R²와 MAE 정의, bootstrap 구간과 p의 식, block 안 순열, Holm과 BH, 합친 S6 폴더 끝에서 끝까지(0 후보 fold, D-4 ensemble, 빠진 fold), [사전] 15개 Holm, 그림. 2부: 특징 순열과 짝 열 가중 r, 2-1, 2-2(audition_codex와 같은 효과, 묶음 재표집), 6-4b(영상별 예측의 재표집, Holm 13, BH 묶음), 6-2, 6-4a, 6-3의 규칙과 빠진 입력 거절. K1과 14개 차원: decoded features의 눈금 바꾸기와 head 출력의 손 계산, N8 보정과 평균만 옮기는 차원, head 출처 확인, selected.json의 seed와 A-1, C-1 seed 대조, 같은 seed 짝, K1에 p가 없음, (3) − (1) 차이와 BH 묶음, 출처 대조와 빠진 입력 거절
```

합성 자료로 자료 경계(시험 영상, MC 72개), 후보값, 선택 규칙, 출처 기록, 저장 형식을 확인한다. 실제 정답과 뇌 반응은 읽지 않는다.

## 문서

- [OVERVIEW.md](OVERVIEW.md): 연구 내용 요약
- [docs/final/01_integrated_document.md](docs/final/01_integrated_document.md): 설계와 결정의 근거
- [docs/final/04_claude_code_workorder.md](docs/final/04_claude_code_workorder.md): 단계별 작업 지시와 실행 기록
