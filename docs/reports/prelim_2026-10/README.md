# EmoBrain 사전 분석 결과 (랩서버, 2026-10-22 ~ 10-24)

_작성: 랩서버(node1, `/scratch/connectome/seokjin14`)의 Claude Code 세션 · 브랜치 `prelim/labserver-20261026` · 결과 보고 문서이며 설계 결정이 아님_

이 폴더는 랩서버에서 수행한 **0단계(데이터·라벨 점검)**와 **1단계(뇌 단독 기준선, 비교 사다리, 학습 곡선)**의 보고서, 그림, 요약표를 모은 것이다.
원예측·영역 평균 반응·npy 같은 큰 산출물은 저장소 규칙(`.gitignore`, AGENTS.md)에 따라 올리지 않았다. 서버 경로는 아래에 적었다.

## 데이터와 역할

- **주 데이터(개발): Horikawa 2020, 5명.** 입력은 QC 후 `v3_qc`(fieldmap 없는 보정 SyN-SDC, common36 블록 반응, run 안 z).
- **재현 데이터: MindCaptioning, 6명.** 0단계 점검에서만 함께 기술했고, 1단계의 설정 선택에는 쓰지 않았다.
- 정서 라벨: 34개 범주 비율(A34, Cowen & Keltner 2017 미국 평정자, `cowen34_order.txt` 알파벳 순), 14개 척도(A14, `cowen_horikawa_labels.csv`).

## 폴더 안내

| 경로 | 내용 |
|---|---|
| `stage0/PRELIM_STAGE0_REPORT.md`, `.pdf` | 0단계 보고서 (라벨 분포·구조·신뢰도, 무관 요인, 뇌 자료 품질·안정성, 핵심 해석) |
| `stage0/fig_*.png` | 0단계 그림 5장 |
| `stage0/tables/` | 0단계 요약표 (라벨, 무관 요인, 블록 품질, 신뢰도·일치도) |
| `stage1/01_task/` | task 계약 (`task_contract.yaml`), target 사전, 기존 결과와의 호환표 |
| `stage1/00_status/` | 입력 목록, 0단계 인계표, 분석별 준비 상태, 결정 기록 |
| `stage1/02_brain/` | 핵심 3: 뇌 단독 기준선 (차원별·프로필 지표, 요약, 해석) |
| `stage1/03_stimulus/` | 내용 특징 → 정서 (영상 단위) |
| `stage1/04_brain_features/` | 비교 사다리: 뇌 → 내용, 뇌 → 내용 → 정서, 뇌 + 내용 |
| `stage1/05_learning_curve/` | 학습 곡선 (학습 영상 수에 따른 성능) |
| `stage1/figures/` | 1단계 그림 3장 |
| `splits/` | 이번 분석의 분할 `horikawa_rungroup6_v1` 과 규칙 |
| `decisions_proposed.md` | 이번 작업에서 정했거나 제안한 사항 (결정 기록 04 에는 아직 번호를 붙이지 않음) |
| `../../../project/analysis/prelim_2026-10/` | 분석 코드 사본 |

## 핵심 결과 요약

**0단계**
- 34개 범주는 고차원(분산 80%에 주성분 19개)이고 0점 영상이 대부분이며, 범주마다 자료량과 라벨 신뢰도 추정이 크게 다르다(0.28~0.96).
- 라벨과 얽힌 요인은 영상 길이뿐이다(surprise +0.24 등). run 안 순서, 세션, 머리 움직임은 무관하다. 저수준 시각 특징은 대부분 라벨에서 1% 안팎을 설명한다.
- 뇌 자료 품질에는 문제가 없다. 같은 영상에 대한 반응은 시각·배측 주의 영역에서 안정적이고, Limbic·피질하·시상하부에서는 거의 재현되지 않는다.

**1단계** (Horikawa 5명, 469개 영역 평균, 피험자별 모델, 분할 `horikawa_rungroup6_v1`)

| 비교 | A34 (구별되는 27개 평균 r) | A14 (평균 r) |
|---|---|---|
| 뇌 단독 | 0.37 (34개 전체 0.33) | 0.36 |
| 저수준 시각 / 영상 길이 / 뇌 전체 신호 | 0.16 / 0.03 / 0.04 (34개 기준 0.14 / 0.02 / 0.03) | 0.15 / 0.00 / 0.03 |
| 내용만: 의미 73 / 시각 1000 | 0.61 / 0.41 | 0.60 / 0.36 |
| 뇌 → 의미 73 → 정서 | 0.35 | 0.36 |
| 뇌 + 의미 73 | 0.59 | 0.58 |

- 뇌 단독 예측은 48개 차원 모두에서 5명 전원 양수다. 길이·뇌 전체 신호로는 설명되지 않는다.
- 이 선형 모델 기준으로, 뇌의 정서 평정 정보는 뇌가 담은 영상 내용(특히 사람 annotation 의미 특징)과 대부분 겹친다.
- 학습 곡선: 학습 영상 609개에서 전체 대비 84%, 924개에서 91%, 1,215개에서 95%(영상당 스캔 약 13.2초).

## 재현

- 코드 원본: 랩서버 `/storage/bigdata/EmoBrain_response/code/{prelim,stage1,splits}/` (이 저장소에는 사본). 경로는 랩서버 기준으로 고정돼 있다.
- 실행: CPU job 은 node4 sbatch (`run_*.sbatch`). 가벼운 표 계산은 로그인 노드에서 실행했다.
- git 에 없는 산출물 (랩서버):
  - 0단계: `/storage/bigdata/EmoBrain_response/prelim/` (블록별 통계 `block_stats_*`, 영역 평균 반응 `roi_blocks/`, 저수준 특징 `lowlevel_video_features.tsv`, MindCaptioning voxel 신뢰도 지도 `reliability/*.nii.gz`)
  - 1단계: `/storage/bigdata/EmoBrain_response/stage1/` (원예측 `02_brain/predictions/*.tsv.gz`, `03_stimulus/predictions/`, `04_brain_features/predictions/`)

## 상태와 한계

- 결과 보고 수준이다. 다른 서버·다른 AI 가 재검산하지 않았다.
- **분할 `horikawa_rungroup6_v1` 은 이번 분석용이며, 사용자 계획에 따라 분할은 다시 만들 예정이다.** 기존 무작위 분할 파일(`project/shared/data/horikawa_5fold.csv`, `horikawa_split.csv`)은 61개 run 모두에 fold 가 섞여 뇌 모델에 쓰지 않았다. 그 파일들은 이 브랜치에서 건드리지 않았다.
- 입력이 469개 영역 평균이다. voxel 패턴, ROI 단독(편도체·시각 피질), 비선형 모델은 아직 보지 않았다.
- 의미 73 은 사람(평정자 12명) annotation 이라 순수한 자극 정보가 아니다. V-JEPA·caption 문장 표현으로의 재확인이 필요하다.
- 뇌 + 내용은 이어 붙인 입력에 규제 강도 하나를 썼다. 입력 묶음별 규제(banded ridge)로 다시 볼 예정이다.

## T004 와의 관계

원격의 T004(Perlmutter Claude Code, `project/baseline/brain_decoding/`)는 Horikawa sub-01 의 소규모 개발 부분집합(fit 8 / tune 2 / evaluate 2 run, voxel dual ridge)으로 loader·split·scaling 을 점검하는 pilot 이다. 이 폴더의 1단계는 5명 전체, 469개 영역 평균, run 묶음 6겹 교차검증의 기준선으로, 목적과 범위가 다르다. 둘을 대체 관계로 보지 않으며, 분할과 입력을 맞출지는 분할을 다시 정할 때 함께 결정한다.
