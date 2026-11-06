# 본 실험 코드 (docs/final 설계, 2026-11-03~)

설계 기준은 `docs/final/01_integrated_document.md`, 단계와 기록 칸은 `docs/final/04_claude_code_workorder.md`이다.
10월 사전 분석 코드는 `../prelim_2026-10/`에 있고 이 폴더와 섞지 않는다.

| 파일 | 단계 | 내용 | 출력 |
|---|---|---|---|
| `s1_labels_mc72.py`, `.sh` | S1 | 34개 라벨 열을 원 범주 이름 파일(category.mat)과 대조하고, MC 최종 시험 72개 목록과 그 중복, 개발 영상 수를 만든다 (CPU, 수 초) | `manifests/label_map_34.tsv`, `manifests/mc_test72.tsv` |
| `s1_sets_raters_runs.py`, `.sh` | S1 | 중복 15개의 구성, 평정자 수 역산, MC 학습 run 구성, 8초 반복 종료 시점(블록 길이) (CPU, 수십 초) | `manifests/duplicates_15.tsv`, `rater_count_inferred.tsv`, `mc_train_runs.tsv`, `presentation_length.tsv` |
| `s1_abnormal_blocks.py`, `.sh` | S1 | HK 이상 block과 이상 run 목록을 0단계와 같은 정의로, 개발 블록(MC 72개와 나중 중복 제외)만으로 다시 만든다. B6 결정(11/3)에 따라 빼지 않고 기록으로만 쓴다 (CPU, 피험자당 1~2분, 로그 `project/output/final_2026-11/logs/`) | `manifests/abnormal_blocks_hk.tsv` |
| `s1_abnormal_motion.py`, `.sh` | S1 | 위 블록 5개와 sub-03 run 31~33의 FD, DVARS를 다른 블록, run과 비교한다(B6 재결정 전 확인) (CPU, 수 초) | `manifests/abnormal_motion_check.tsv` |
| `s1_public_checks.py`, `.sh` | S1 | 참가자별 voxel 수, 원 논문 공개 코드의 피질하 10개 정의와 fold 배정, 이름표 73개와 34개 범주의 공개 파일 대조 (CPU, 수 초) | `manifests/voxel_counts.tsv`, `subcortex_definition.tsv`, `original_folds.tsv` |
| `s1_original_rois.py`, `.sh` | S1 | 공개 자료의 참가자별 ROI 370개를 읽어 우리 T1w 격자로 옮기고 QC mask 안의 voxel 수를 센다. 내려받은 큰 파일은 지운다 (통신 위주, 약 20분, 결과 npz는 `project/output/final_2026-11/s1_original_rois/`) | `manifests/original_roi_voxels.tsv`, `original_roi_grid.tsv`, `original_roi_sources.tsv` |
| `s1_original_roi_align.py`, `.sh` | S1 | 공개 ROI가 FreeSurfer aseg와 해부학적으로 맞는지(11명), Talairach Daemon 두 판 중 어느 쪽과 맞는지(HK 5명) (CPU, 약 10분) | `manifests/original_roi_alignment.tsv`, `td_version_check.tsv` |
| `s1_subcortex_rebuild.py`, `.sh` | S1 | 피질하 10개를 PickAtlas에서 11명 모두 새로 만들어 저자 공개 mask, aseg와 위치로 비교한다(04 정할 것 5, 7). 뇌 반응은 읽지 않는다 (CPU, 3명씩 병렬, 약 12분, 결과 `project/output/final_2026-11/s1_subcortex_rebuild/`) | `manifests/subcortex_rebuild_check.tsv` |
| `s1_subcortex_size_check.py`, `.sh` | S1 | 저자 피질하 mask가 새 mask보다 큰 이유가 경계 처리인지 선형 보간 문턱별로 잰다. 뇌 반응은 읽지 않는다 (CPU, 약 2분) | `manifests/subcortex_size_check.tsv` |
| `s1_roi_final_check.py`, `.sh` | S1 | 제안한 ROI 370개를 실제로 묶어 열 번호 연결, 공통 ROI, 겹침, 시상하부와 BA34 위치, 등록 이상을 점검한다 (CPU, 약 1분) | `manifests/roi_final_check.tsv` |
| `s2_manifest.py`, `.sh` | S2 | 분할(v1 + 1363 이동), 세션 검사, 내용 구역, 학습량 대조 표본, 이름표 짝, ROI별 voxel 열 번호, CAB-NP 13묶음, MC 표, HK 일치도와 반복 신뢰도, 열 순서 점검, 확인 기준 검사 (`--stage split, blocks, pairs, roi, mc, brain, order, check`, CPU, 약 10분) | `manifests/s2/`, `project/output/final_2026-11/s2_manifest/` |

`manifests/`의 작은 표는 다음 단계(S2 manifest)의 입력이라 git에 넣는다. 큰 산출물은 `project/output/` 아래에 둔다(M3).
| `s3_common.py`, `s3_vision.py`, `.sh` | S3 | 참가자가 본 영상을 재현해 V-JEPA 2, VideoMAE, TimeSformer, CLIP 특징을 뽑는다 (GPU, 끊기면 이어서) | `project/output/final_2026-11/s3_features/<모델>/` |
| `s3_text.py`, `.sh` | S3 | DeBERTa, 정서어 제거 DeBERTa, MPNet 캡션 특징 (GPU) | 같은 폴더 |
| `s3_lowlevel.py`, `.sh` | S3 | 움직임 에너지 6,555개와 RGB 중앙값 3개 (CPU 노드) | 같은 폴더 |
| `s3_collect.py`, `.sh` | S3 | 영상별 조각을 파일로 모으고 차원, 영상 수, NaN을 확인하고 추출 기록을 쓴다 (가벼움) | 같은 폴더 |
| `s3_tests.py`, `.sh` | S3 | 반복 경계, 화면 순서, 출처, 수집 검사의 회귀 시험 (CPU, 약 2분) | 없음 |
| `s3_author_check.py`, `.sh` | S3 | DeBERTa와 TimeSformer를 저자 공개 특징과 비교 (본 추출 뒤) | `manifests/s3/author_feature_check.tsv` |
| `s4_common.py`, `s4_feature_model.py`, `.sh` | S4 | 특징 모델 T_VS와 nested OOF, K1 head, K1a, 정서어 제거판, 구역 제외 (GPU, 설계 동결 뒤, 끊기면 이어서) | `project/output/final_2026-11/s4_no_brain/` |
| `s4_ridge.py`, `.sh` | S4 | D12와 정서어 제거판의 뇌 없는 ridge (GPU, 설계 동결 뒤) | 같은 폴더 |
| `s4_window_change.py`, `.sh` | S4 | 긴 영상의 창 사이 변화량 (CPU, 가벼움, 설계 동결 뒤) | 같은 폴더 |
| `s4_collect.py`, `.sh` | S4 | 분할 경계 점검과 요약 표 (가벼움) | `manifests/s4/`, 같은 폴더의 `summary/` |
| `s4_tests.py`, `.sh` | S4 | 합성 자료 시험. 실제 정답과 뇌 반응을 읽지 않음 (CPU, 수 분) | 없음 |
