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

모든 명령은 레포 최상위에서 실행한다. GPU 단계는 `sbatch scripts/<이름>.sh <인자>`로 낸다. Slurm으로 할당받은 compute node 안(salloc 등)에서는 `bash scripts/<이름>.sh <인자>`로 돌려도 된다. login node에서 학습을 돌리지 않는다(NERSC 정책). 실제 결과를 내는 단계(S4 이후)는 설계 동결 커밋을 마지막 인자로 받고, 커밋되지 않은 코드로는 돌지 않는다. 끝난 실행은 코드, 입력, 설정이 같을 때만 건너뛰고, 다르면 섞지 않고 멈춘다.

| 단계 | 스크립트 | 하는 일 | 출력 |
|---|---|---|---|
| S1 | `s1_*.sh` | 라벨 열 대조, MC 최종 시험 72개 목록, 이상 block 기록, 공개 ROI 370개를 우리 격자로 옮기기, 피질하 ROI 다시 만들기와 점검 (CPU) | `manifests/s1/` |
| S2 | `s2_manifest.sh <stage>` | 분할, 내용 구역, 이름표 짝, ROI별 voxel 열, CAB-NP 13묶음, MC 표, 일치도 (CPU, 약 10분) | `splits/hk_dev_v4/`, `manifests/s2/` |
| S2 | `s2_split_files.sh [--check]` | 분할 원본에서 실행 단위별 목록 만들기 | `splits/hk_dev_v4/` |
| S3 | `s3_vision.sh`, `s3_text.sh`, `s3_lowlevel.sh`, `s3_collect.sh` | 영상과 캡션의 특징 추출. V-JEPA 2(block 40개), DeBERTa-large(층 24개), 비교용 VideoMAE, TimeSformer, CLIP, MPNet, 저수준 시각 특징 (GPU, 끊기면 이어서) | `<output_root>/s3_features/` |
| S4 | `s4_feature_model.sh <과제> <커밋>` | 뇌 없는 모델. Stimulus Model(Vision + Caption → Emotion)과 distillation용 fold 밖 예측, 14개 차원판, 정서어 제거판, 구역 제외, 비교용 특징판 (GPU) | `<output_root>/s4_no_brain/` |
| S4 | `s4_ridge.sh`, `s4_window_change.sh`, `s4_collect.sh` | V-JEPA 2 block별 ridge, 긴 영상의 window 변화, 점검과 요약 | 같은 폴더, `<output_root>/s4_collect/` |
| S5 | `s5_decoding.sh <참가자> <커밋>` | 뇌 → 층별 feature ridge decoding (GPU) | `<output_root>/s5_ridge/` |
| S5 | `s5_baselines.sh <과제> <참가자> <커밋>` | 정서 기준선: ridge, soft BCE 선형, 영상 길이, 저수준, 뇌 전체 신호, Horikawa 2020 복셀 선택 ridge (GPU) | 같은 폴더 |
| S6 | `s6_train.sh <분할> <조건> <설정> <커밋>` | 뇌 모델 학습. 분할은 `outer_fold<k>`, `pilot_fold<k>`, `final_for_mc`, `zone_block<b>_fold<k>_<방식>` (GPU) | `<output_root>/s6_brain/` |
| S6 | `s6_weight_counts.sh <d 목록>` | 조건별 학습 가중치 수 (CPU) | `manifests/s6/weight_counts.tsv` |

S6의 결과 폴더 구조와 저장 형식은 [src/s6_train.py](src/s6_train.py) 머리말에 있다.

### 뇌 모델 조건 이름

결과 폴더는 코드 이름을 쓴다. 조건의 Input과 Output은 [OVERVIEW.md](OVERVIEW.md)와 01의 5-A에 있다.

| 코드 이름 | 논문 이름 |
|---|---|
| `brain_only` | 조건 1. Brain → Emotion |
| `brain_only_featdec` | 조건 2. Brain → Emotion + Vision + Caption |
| `brain_decoded` | 조건 3. Brain + Decoded Feature → Emotion (상호작용 head) |
| `brain_decoded_additive` | 조건 3의 더하기 head |
| `brain_only_distill` | 조건 4. Brain → Emotion [distillation] |
| `brain_decoded_distill` | 조건 5. Brain + Decoded Feature → Emotion [distillation] |
| `multimodal` | Multimodal Model (Brain + Vision + Caption → Emotion, 조건 6, 7의 준비) |
| `brain_only_repr_frozen` | 조건 6. Brain → Emotion [representation, frozen head] |
| `brain_only_repr_trained` | 조건 7. Brain → Emotion [representation, trained head] |
| `brain_decoded_grad` | 조건 3에서 stop-gradient를 뺀 판 (성능 비교에만) |
| `control_label_smoothing`, `control_stimulus_shuffle`, `control_feature_shuffle` | 대조군 셋 |
| `brain_only_pool`, `brain_decoded_pool` | 평균 pooling판 |

## 시험

```bash
bash scripts/s3_tests.sh   # 약 1분
bash scripts/s4_tests.sh   # 약 2분
bash scripts/s5_tests.sh   # 약 2분
bash scripts/s6_tests.sh   # 약 2분
```

합성 자료로 자료 경계(시험 영상, MC 72개), 후보값, 선택 규칙, 출처 기록, 저장 형식을 확인한다. 실제 정답과 뇌 반응은 읽지 않는다.

## 문서

- [OVERVIEW.md](OVERVIEW.md): 연구 내용 요약
- [docs/final/01_integrated_document.md](docs/final/01_integrated_document.md): 설계와 결정의 근거
- [docs/final/04_claude_code_workorder.md](docs/final/04_claude_code_workorder.md): 단계별 작업 지시와 실행 기록
