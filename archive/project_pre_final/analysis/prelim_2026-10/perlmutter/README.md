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
| `mlp_student.sh` | MLP student 만 다시 실행 (cache 재사용) | `07_students/mlp/` |
| `mlp_pooled.sh` | 5명 통합 MLP student (`mlp_student.py --pooled-fold`, 공통 유효 영역 466개 + 피험자 표시) | `07_students/mlp_pooled/` |
| `softbce_student.sh` | soft BCE student 만 다시 실행 (가중치 저장, `--effect-size` 로 bootstrap·효과 크기) | `07_students/softbce/` |
| `roi_networks_distill.sh` | 영역 묶음별 선형 teacher–student (`roi_networks.py --distill`) | `08_roi_networks/distill/` |
| `interpret_students.py` | 피험자·감정별 차이, 영상별 변화, 네트워크별 내용/잔차 분해, 가중치 활성 패턴 (저장된 결과만 읽음) | `09_interpretation/` |
| `vision_ladder.sh` | 시각 특징(Horikawa VGG19, CLIP, DINOv2, VideoMAE) 비교 사다리 단위 실행 | `04_brain_features/` |
| `metrics_panel.py` | 저장된 예측에서 지표 약 26개 계산 (Pearson, R², soft BCE, CCC, AUC, mAP, MAE 합산, F1, 프로필, 짝 구별 등) | `10_metrics/` |
| `feature_decoding_metrics.py` · `.sh` | 저장된 뇌 → 특징 OOF 예측으로 차원별 r·R², 영상별 프로필 상관, 두 영상 식별, 100개 중 top-1·top-5 (재학습 없음) | `04_brain_features/feature_decoding_metrics*.tsv` |
| `feature_overlap.py` · `.sh` | 시각·캡션 특징 겹침: CKA·RSA, 서로 예측, 34개 범주 정서 예측의 시각 고유·캡션 고유·공유 (자극 수준) | `12_feature_overlap/` |
| `layer_overlap.py` · `.sh` | V-JEPA 2·CLIP 층별 캡션 겹침과 정서 예측 기여 (EmoViS 층별 특징 사용) | `12_feature_overlap/layerwise.tsv` |
| `feature_content_map.py` · `feature_content_figures.py` · `.sh` | V-JEPA 2·캡션이 각각 잡아낸 것: 저수준 특징 대 캡션 감정별 비교, 장면 개념 73개 예측, 그림 두 장 (그림은 swift_PTL2 환경의 matplotlib) | `12_feature_overlap/` |
| `action_object_test.py` · `.sh` | 캡션의 동작 단어 대 물체 단어를 시각 특징으로 예측 (영상 모델의 시간 정보 확인) | `12_feature_overlap/action_object_*.tsv` |
| `evaluative_words_test.py` · `.sh` | 평가어를 지운 캡션과의 비교, 시각 특징의 평가어 예측 | `12_feature_overlap/` |
| `perturbation_readout.py` · `.sh` | 밝기·채도·대비·색조·흐림·시간 순서 조작 전후 시각 모델 정서 예측 변화 (`../features/build_video_model_features.py --perturb` 결과 사용) | `13_perturbation/` |
| `perturb_quick.py` · `perturb_quick_figures.py` · `.sh` | 채도·밝기 조작 빠른 확인판 (영상 79개, CLIP·DINOv2, CPU) | `13_perturbation/quick/` |
| `semantic_matched_pairs.py` · `.sh` | 의미를 맞춘 영상 쌍에서 정서 차이를 저수준·층별 시각 특징 차이가 설명하는지 (34개 감정) | `14_matched_pairs/` |
| `within_context_lowlevel.py` · `.sh` | 같은 대상(맥락) 안에서 저수준 특징이 정서를 가르는지, 캡션 뒤에도 남는지 (맥락 8개 × 감정 4개, null 200회) | `15_within_context/` |
| `hierarchy_components.py` · `hierarchy_figures.py` · `.sh` | 정서 평정을 시각에만·둘 다·캡션에만·나머지로 나눈 뒤 뇌 영역 묶음 24개마다 디코딩, 피질 위계 순서로 비교 (그림은 swift_PTL2) | `16_hierarchy/` |
| `khbm_pilot.py` · `khbm_pilot.sh` · `khbm_pilot_resume.sh` | KHBM 초록용 빠른 예비 분석 (MC 72개 제외, 선형, 공유 MLP 조건 비교, 바꿔 끼우기, 영역 분해) | `17_khbm_pilot/` |
| `roi_networks.py` · `roi_networks.sh` | 영역 묶음별(7개 네트워크, 소뇌, 편도체, 해마, 그 밖 피질하, 시상하부·뇌간) 직접 예측, 캡션 경로, V-JEPA 2 위 추가분 | `08_roi_networks/` |

입력 특징(V-JEPA 2, 캡션 임베딩)은 `../features/build_lab_features.py`, 감정어를 지운 캡션은 `../features/build_caption_noemo.py` 가 `/pscratch/sd/s/sjmoon/transfer/emobrain_lab_features_20261026/` 에 만든다.
VLM 생성 캡션 점검은 `../features/caption_vlm_qc.py` · `.sh` 이고 결과는 `11_caption_qc/` 에 있다.
영상 입력 VLM 캡션 생성은 `../features/build_caption_vlm_video.py` · `.sh` (pilot → all → merge) 이고, 캡션은 특징 폴더의 `caption_vlm_video/<모델 태그>/`, 임베딩은 `caption_<모델 태그>_mpnet.npy` 로 저장된다.
색·밝기·선명도·움직임 저수준 특징 28개는 `../features/build_lowlevel_motion.py` · `.sh` (특징 폴더 `lowlevel_motion.npy`).
영상·이미지 모델 특징을 같은 시간 정보(영상 모델은 2초 창 + 시간 4구간 × 공간 2×2, 이미지 모델은 초당 2장 + 시간 4구간)로 다시 뽑는 스크립트는 `../features/build_video_model_features.py` · `.sh` 이고, 결과는 특징 폴더의 `video_models/<모델>/` 에 저장된다.
로그는 `project/output/prelim_2026-10/logs/<분석>/` 에 쓴다.
