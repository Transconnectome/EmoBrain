# 화면·시간 조작에 대한 시각 모델 정서 예측의 민감도 (2026-10-31)

같은 영상의 채도·밝기 등을 바꿨을 때, 원래 영상으로 학습한 정서 예측기(그 영상이 학습에 없는 fold)의 34개 예측이 얼마나 움직이는지 본다.
모델이 배운 연관의 민감도이며, 조작한 영상에 대한 사람 평정은 없다.

## quick/ (빠른 확인판, `perlmutter/perturb_quick.py` · `.sh`, 그림 `perturb_quick_figures.py`)

- 영상 79개: 4초 이하이고 한 감정이 가장 높은 비율(≥ 0.4)을 받은 영상, 감정 10개에서 8개씩 (calmness 7개). `videos.tsv`
- 조작: 채도 0·0.5·1.5·2 배, 밝기 0.5·0.75·1.25·1.5 배. 특징은 기존과 같은 프레임 3장 평균 (원본 재계산과 저장 특징의 r 중앙값 0.997, `feature_check_*.tsv`)
- `predictions_<모델>.tsv`, `shift_summary.tsv` (변화량 = 원본 예측의 영상 사이 SD 단위, 영상 평균과 t), `fig_quick_perturbation.png`
- CLIP: 흑백 평균 |변화| 0.13 SD, 밝기 절반 0.10 SD, 나머지 0.03~0.06 SD. 흑백은 nostalgia·horror 를 올리고 awe·joy·amusement 를 내림, 어둡게 하면 boredom·horror·sadness 가 오르고 amusement·awe·joy 가 내림. 방향은 영상 사이에서 일관되지만 (t 4~8) 크기는 작다.

- 모델 비교 (`perlmutter/perturb_quick_models.py`, 새 추출 경로, GPU): 흑백일 때 34개 평균 |변화| 는 DINOv2 0.03, CLIP 0.13, VideoMAE 0.16, V-JEPA 2 0.22~0.27 SD. DINOv2 는 색·밝기에 거의 반응하지 않는다. 방향의 모델 간 일치는 r 0.2~0.66. 공통 방향은 흑백 → horror 상승, amusement 하락. nostalgia 는 CLIP 에서 오르고 VideoMAE 에서 내려 모델마다 다르다. V-JEPA 2·CLIP 의 흑백 → romance·sexual desire 상승은 자극 세트의 흑백 영상 (캡션 기준 10개, entrancement·boredom·aesthetic appreciation·calmness 가 높고 romance 는 −0.18 SD) 으로 설명되지 않아, 예측기가 학습 범위 밖 입력에서 외삽한 결과로 본다.

## 전체판 (예정)

`features/build_video_model_features.py --perturb` (영상 240개 × 조작 12종, 시간 조작 포함) 와 `perlmutter/perturbation_readout.py`.
