# 공정 비교 baseline (문헌 방법과 같은 자료·분할·지표로 비교, 2026-10-28)

같은 Horikawa 자료로 감정 평정을 뇌에서 디코딩한 문헌(GED, ML-BVAE, AESL)과 우리 모델을 같은 조건에서 비교한다.
문헌 수치는 참가자별 무작위 10겹(같은 run·같은 내용이 학습과 평가에 섞임)이고, GED 공개 코드에는 검증 세트가 없다.
그래서 두 프로토콜에서 같은 지표로 모두 평가한다.

## 구성

| 파일 | 하는 일 |
|---|---|
| `make_protocols.py` · `.sh` | 분할표 `runs/protocols/{ours,lit}_sub-XX.tsv`. ours = run 묶음 6겹 (중복 제외, `horikawa_rungroup6_v1`), lit = 참가자별 무작위 10겹 (중복 포함) |
| `build_subroi_features.py` · `.sh` | GED 식 영역 하위 구역 평균 (469개 영역 × 4³, `runs/features/`) |
| `run_baselines.py` · `run_baselines.sh` | ridge, MLP, GED. 입력 roi469 (영역 평균) · subroi4 (하위 구역). 결과 `runs/<protocol>/<입력>_<모델>/` |
| `summarize_baselines.py` | 모든 예측에 지표 묶음 (`project/analysis/prelim_2026-10/perlmutter/metrics_panel.py`) + GED 식 정규화 MAE, GED 의 평가 세트 선택 MAE |
| `third_party/GED/` | GED 공개 코드 (https://github.com/zhongyu1998/GED, commit 3ea8492, MIT). git 에 넣지 않음. 모델 `models/graphcnn.py` 를 그대로 쓰고, 간선 생성 `utils.load_adj` 는 `run_baselines.ged_edges` 로 옮김 |

## 원칙

- 같은 입력 행, 같은 target (34개 범주 평정자 비율, 14개 차원 평균 평정), 같은 지표.
- epoch·규제 강도는 학습 자료 안 검증으로 고른다. GED 를 문헌처럼 평가 세트로 고른 값은 차이를 보이기 위해서만 기록한다.
- GED 는 연속 target 을 감정마다 전체 영상의 최소~최대로 정규화했다. 우리는 비율 그대로 학습하고, 비교용으로 정규화 MAE 를 함께 낸다.
- GED 는 GPU 가 빠르다 (`--device cuda`). GPU 실행은 사용자가 한다.

## 실행 순서

```
bash /pscratch/sd/s/sjmoon/EmoBrain/project/baseline/literature_comparison/make_protocols.sh
bash /pscratch/sd/s/sjmoon/EmoBrain/project/baseline/literature_comparison/build_subroi_features.sh
bash /pscratch/sd/s/sjmoon/EmoBrain/project/baseline/literature_comparison/run_baselines.sh ridge
bash /pscratch/sd/s/sjmoon/EmoBrain/project/baseline/literature_comparison/run_baselines.sh mlp
bash /pscratch/sd/s/sjmoon/EmoBrain/project/baseline/literature_comparison/run_baselines.sh ged cuda
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python /pscratch/sd/s/sjmoon/EmoBrain/project/baseline/literature_comparison/summarize_baselines.py
```
