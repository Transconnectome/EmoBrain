# 본 실험 코드 (docs/final 설계, 2026-11-03~)

설계 기준은 `docs/final/01_integrated_document.md`, 단계와 기록 칸은 `docs/final/04_claude_code_workorder.md`이다.
10월 사전 분석 코드는 `../prelim_2026-10/`에 있고 이 폴더와 섞지 않는다.

| 파일 | 단계 | 내용 | 출력 |
|---|---|---|---|
| `s1_labels_mc72.py`, `.sh` | S1 | 34개 라벨 열을 원 범주 이름 파일(category.mat)과 대조하고, MC 최종 시험 72개 목록과 그 중복, 개발 영상 수를 만든다 (CPU, 수 초) | `manifests/label_map_34.tsv`, `manifests/mc_test72.tsv` |
| `s1_sets_raters_runs.py`, `.sh` | S1 | 중복 15개의 구성, 평정자 수 역산, MC 학습 run 구성, 8초 반복 종료 시점(블록 길이) (CPU, 수십 초) | `manifests/duplicates_15.tsv`, `rater_count_inferred.tsv`, `mc_train_runs.tsv`, `presentation_length.tsv` |
| `s1_abnormal_blocks.py`, `.sh` | S1 | HK 이상 block과 이상 run 목록을 0단계와 같은 정의로 다시 만든다(B6) (CPU, 피험자당 1~2분, 로그 `project/output/final_2026-11/logs/`) | `manifests/abnormal_blocks_hk.tsv` |

`manifests/`의 작은 표는 다음 단계(S2 manifest)의 입력이라 git에 넣는다. 큰 산출물은 `project/output/` 아래에 둔다(M3).
