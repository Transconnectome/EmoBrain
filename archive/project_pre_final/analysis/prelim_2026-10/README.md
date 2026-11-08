# 사전 분석 코드 사본 (랩서버, 2026-10-22 ~ 10-24)

결과와 설명은 [`docs/reports/prelim_2026-10/`](../../../docs/reports/prelim_2026-10/README.md) 에 있다. 이 폴더는 실행한 코드의 사본이며, 원본은 랩서버 `/storage/bigdata/EmoBrain_response/code/` 이다. 입력·출력 경로가 랩서버 기준으로 고정돼 있어 다른 서버에서는 경로를 바꿔야 한다. 실행 환경은 `/usr/anaconda3/bin/python3` + `PYTHONPATH=/storage/bigdata/Horikawa/preprocessing_code_v2/pylib` (NumPy 1.17, SciPy 1.3, pandas 0.25, scikit-learn 0.21, nibabel).

| 파일 | 하는 일 |
|---|---|
| `prelim/label_structure.py` | 0-1~0-4, 0-9: 라벨 상관·차원, 34↔14, 드문 감정, 평정자 수 역산·신뢰도, 영상 길이 설명력 |
| `prelim/label_distribution.py` | 라벨 분포 표와 그림 |
| `prelim/confound_and_block_check.py` | 0-5 라벨 × 무관 요인, 0-7 블록·run 품질 (`run_block_check.sbatch`) |
| `prelim/lowlevel_features.py` | 0-6 저수준 시각 특징 33개 추출(ffmpeg, node1)과 라벨 설명력 |
| `prelim/brain_reliability.py` | 0-8 영역 평균 반응 저장, 반복 신뢰도, 피험자 간 일치도 (`run_brain_reliability*.sbatch`) |
| `prelim/report_figures.py`, `build_report_pdf.py` | 0단계 그림과 PDF |
| `splits/make_horikawa_split.py` | 분할 `horikawa_rungroup6_v1` 생성 |
| `stage1/stage1_setup.py` | task 계약, target 사전, 인계·준비 상태 표 |
| `stage1/brain_baseline.py` | 핵심 3 뇌 단독 기준선과 기준선 4종 (`run_brain_baseline.sbatch`) |
| `stage1/content_ladder.py` | 내용 → 정서, 뇌 → 내용, 뇌 → 내용 → 정서, 뇌 + 내용 (`run_content_ladder.sbatch`) |
| `stage1/learning_curve.py` | 학습 곡선 (`run_learning_curve.sbatch`) |
| `stage1/baseline_figure.py`, `ladder_lc_figures.py` | 1단계 그림 |
