# 사전 분석 1단계의 Perlmutter 실행 (2026-10-27~28)

랩서버 1단계 코드(`../stage1/`)의 모델·분할·선택 절차를 그대로 쓰고, 입력을 Perlmutter 자료로 바꿔 실행한다. 모두 login node 에서 bash 로 실행한다. 결과는 git 에 올리지 않는 `project/output/prelim_2026-10/` 에 쓴다.

| 파일 | 하는 일 | 결과 폴더 (`project/output/prelim_2026-10/`) |
|---|---|---|
| `run_stage1.py` · `run_stage1.sh` | v3_qc 에서 469개 영역 평균을 만들고, 피험자별 같은 행에서 뇌만·내용만·뇌 → 내용 → 정서·뇌 + 내용 비교. 랩서버 뇌 기준선 재현 대조 | `roi_blocks/`, `04_brain_features/` |
| `linear_distill.py` · `linear_distill.sh` | 선형 teacher–student pilot (ridge). `--labelpca` 는 내용 없는 라벨 smoothing 대조 | `06_linear_distill/<teacher>/`, `06_linear_distill/labelpca/` |
| `teacher_controls.sh` | teacher 변형 대조 (V 만, S 만, 감정어 지운 S, pairing shuffle). `linear_distill.py --teacher ... [--shuffle]` | `06_linear_distill/<teacher>[_shuffled]/` |
| `teacher_cache.py` | 내용 teacher 의 교차검증 밖 예측을 피험자별로 한 번 계산해 저장 | `07_students/cache/` |
| `softbce_student.py` | 34개 범주 soft BCE 선형 student (w = 0 은 랩서버 기준선) | `07_students/softbce/` |
| `mlp_student.py` | 작은 MLP student (내용 teacher, 라벨 smoothing 대조, 뇌 단독) | `07_students/mlp/` |
| `students.sh` | 위 세 파일을 피험자 5명 병렬로 실행하고 요약 | 위와 같음 |
| `roi_networks.py` · `roi_networks.sh` | 영역 묶음별(7개 네트워크, 소뇌, 편도체, 해마, 그 밖 피질하, 시상하부·뇌간) 직접 예측, 캡션 경로, V-JEPA 2 위 추가분 | `08_roi_networks/` |

입력 특징(V-JEPA 2, 캡션 임베딩)은 `../features/build_lab_features.py`, 감정어를 지운 캡션은 `../features/build_caption_noemo.py` 가 `/pscratch/sd/s/sjmoon/transfer/emobrain_lab_features_20261026/` 에 만든다.
로그는 `project/output/prelim_2026-10/logs/<분석>/` 에 쓴다.
