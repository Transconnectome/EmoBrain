# 시각 특징과 캡션 특징의 겹침 (2026-10-30, 자극 수준)

코드: `project/analysis/prelim_2026-10/perlmutter/feature_overlap.py` · `.sh`. 분석 행 2,181개 영상, fold 는 `horikawa_rungroup6_v1`.

| 파일 | 내용 |
|---|---|
| `cka.tsv` | 특징 쌍의 linear CKA 와 영상 순서를 섞은 null (20회 평균) |
| `rsa.tsv` | 1 − Pearson 거리 RDM 끼리의 Spearman 상관 |
| `cross_prediction.tsv` | 한 특징으로 다른 특징을 ridge 로 예측했을 때 대상 특징 분산 중 설명된 비율 (6겹 OOF) |
| `emotion_partition.tsv` | 34개 범주 비율 R² (학습 fold 평균 대비): 시각만, 의미만, 둘 다 (stacking) 의 설명력과 시각에만 있는 정보·캡션에만 있는 정보·둘 다 가진 정보 |
| `emotion_partition_by_category.tsv` | 위를 범주별로 |
| `emotion_partition_lowlevel.tsv` | 저수준 특징(EmoViS Sadeghi 방식 142차원, 정지 화면) 과 사람 캡션의 감정별 설명력 (`feature_content_map.py`) |
| `concept_prediction.tsv` | 장면 개념 73개를 V-JEPA 2·캡션·저수준 특징으로 예측한 r |
| `fig_emotion_partition.png` · `fig_concepts.png` | 감정별 V-JEPA 2 에만 있는 정보 / 둘 다 / 캡션에만 있는 정보, 장면 개념 예측 비교 (`feature_content_figures.py`) |
| `fig_visual_models.png` | 시각 모델 다섯 개 (V-JEPA 2, VideoMAE, DINOv2, CLIP, VGG19 fc8) 비교: 감정별 캡션 위에 더하는 정보, 장면 개념별 r(모델) − r(캡션) |
| `action_object_words.tsv` · `action_object_summary.tsv` | 사람 캡션의 동작 단어(-ing) 52개와 물체 단어를 시각 특징으로 예측한 r (`action_object_test.py`) |
| `caption_noemo_partition*.tsv` · `evaluative_words.tsv` | 평가어·정서어 181개를 지운 캡션과 원 캡션 비교, 시각 특징의 평가어(cute, scary 등) 예측 (`evaluative_words_test.py`) |
| `layerwise.tsv` | V-JEPA 2 (블록 4~40) · CLIP (블록 2~24) 층별 사람 캡션 CKA, VideoMAE CKA, 정서 R², 캡션 위에 더하는 정보·둘 다 가진 정보 (`layer_overlap.py`). 층별 특징은 EmoViS study1_19·20 의 블록 출력 공간 평균이며 마지막 정규화 전이라 위 CKA 표와 값의 크기를 직접 비교하지 않는다 주의: 단독 보정을 고치기 전 방식이라 '캡션 위에 더하는 정보' 가 0.005~0.01 정도 크게 나왔을 수 있다. 다시 계산 예정 |

## 요약

- 전체 표상은 부분적으로 겹친다. 사람 캡션과의 CKA 는 V-JEPA 2 0.33, VideoMAE 0.44, DINOv2 0.49, CLIP 0.51 (null 0.01~0.08).
- 정서 예측 정보는 많이 겹친다. 사람 캡션 + V-JEPA 2: R² 시각 0.237, 캡션 0.392, 둘 다 0.406, 시각에만 있는 정보 0.014, 캡션에만 있는 정보 0.170, 둘 다 가진 정보 0.222. 시각 모델이 정서를 예측하는 정보의 87~97% 가 캡션에도 있다 (2026-10-30 재계산: 단독 모델도 stacking 과 같은 보정을 거치게 고침. 고치기 전에는 설명력이 0 근처인 감정에서 결합 이득이 부풀려졌다).
- VLM 캡션 v1 은 CLIP 위에 거의 더하지 않고 사람 캡션은 CLIP 위에 0.068 을 더한다 (재계산 값은 emotion_partition.tsv).
- 한계: 비율에 대한 ridge R² (soft BCE·r 아님), 분할 하나, MC test 72개 포함 (자극 수준이라 영향은 작음).
- 층별: V-JEPA 2 는 어느 층에서도 캡션과의 CKA 가 0.03~0.07 로 낮고 깊어져도 오르지 않는다. CLIP 은 18층부터 오른다 (24층 0.50). V-JEPA 2 의 정서 R² 는 32~36층에서 가장 높고 (0.25, 캡션 위에 더하는 정보 0.026) 40층은 조금 낮다 (0.22, 캡션 위에 더하는 정보 0.022). 깊어질수록 늘어나는 정서 정보는 대부분 캡션도 가진 정보다.
- V-JEPA 2 에만 있는 정서 정보는 nostalgia·boredom·entrancement·aesthetic appreciation·calmness 에 몰린다. 장면 개념으로는 낮/밤, 실내/실외, 구름, 군중, 텔레비전 화면, 옛날 영상처럼 장면 전체의 분위기를 V-JEPA 2 가 캡션보다 잘 맞히고, 총·토사물·군인·국기·병·노인·곤충·피·시신처럼 작지만 의미가 큰 대상은 캡션이 훨씬 잘 맞힌다. 저수준 특징은 aesthetic appreciation (R² 0.18) 등을 예측하지만 캡션 위에 더하는 정보는 0.01 이하다.
- 재계산 후 V-JEPA 2 에만 있는 정서 정보가 뚜렷한 감정은 nostalgia (0.074), boredom (0.047), entrancement (0.047), aesthetic appreciation (0.028), calmness (0.022) 이다. envy·guilt 의 큰 값은 보정 효과였고 사라졌다. 저수준 특징이 캡션 위에 더하는 정보는 모든 감정에서 0.01 이하다. 아직 신뢰구간이 없다.
- 시각 모델 다섯 개: 캡션 위에 더하는 정서 정보는 CLIP 이 거의 모든 감정에서 가장 크다 (대부분 0.03~0.08, nostalgia 0.30). 영상 모델 (V-JEPA 2, VideoMAE) 은 nostalgia·boredom·entrancement·aesthetic appreciation·calmness 에 몰리고, VGG19 fc8 은 거의 더하지 않는다. 장면 개념 평균 r 은 캡션 0.75, CLIP 0.70, DINOv2 0.67, VideoMAE 0.57, V-JEPA 2 0.56, VGG19 0.46. 작은 물체 (총: V-JEPA 2 0.23, DINOv2 0.54, CLIP 0.46, 캡션 0.81) 는 이미지 모델이 영상 모델보다 훨씬 잘 맞혀서, 영상 모델의 약점이 평균 pooling 만의 문제는 아닐 가능성이 크다.
- 기존 시각 특징의 입력: CLIP·DINOv2 는 프레임 3장(25·50·75%) CLS 평균, V-JEPA 2·VideoMAE 는 클립 전체에 흩은 16프레임을 한 번에 넣고 시공간 token 전체 평균. VideoMAE 는 Kinetics 동작 라벨로 미세조정된 모델이다.
- 동작 단어 대 물체 단어 (평균 r): CLIP 0.27 대 0.36, DINOv2 0.23 대 0.35, V-JEPA 2 0.22 대 0.27, VideoMAE 0.23 대 0.28, VGG19 0.15 대 0.21. 영상 모델은 물체에 비해 동작을 상대적으로 잘 맞히고 (차이 −0.05 대 이미지 −0.09~−0.12), spinning·rotating 은 V-JEPA 2, kissing·hugging·driving 은 VideoMAE 가 가장 높다. 평균 수준에서는 CLIP 이 동작도 가장 높다.
- 같은 시간 정보로 다시 뽑는 스크립트: `features/build_video_model_features.py` (2026-10-30, 결과 대기).
- 평가어·정서어 181개 (cute, adorable, beautiful, scary 포함) 를 지운 캡션: 34개 범주 R² 0.392 → 0.390, V-JEPA 2 대비 캡션에만 있는 정보 0.170 → 0.169. adoration 0.606 → 0.604, 가장 크게 준 horror 도 −0.017. 캡션의 우위는 평가어가 아니라 서술된 상황에서 온다.
- 시각 특징의 평가어 예측 (r): beautiful 0.51~0.59, cute 0.26~0.34, dangerous 0.18~0.36, scary 0.16~0.35. sick·dirty 는 이미지 모델 0.23~0.46, 영상 모델 0.06~0.13. 평균 CLIP 0.30, DINOv2 0.26, V-JEPA 2 0.19.
- 저수준에 움직임을 더한 경우 (`emotion_partition_lowlevel_motion.tsv`, 색·밝기·선명도·움직임 28 + 정지 화면 142): 저수준만으로 34개 평균 R² 0.059 (aesthetic appreciation 0.21, entrancement 0.18, sexual desire 0.13, surprise 0.12). 정서어 지운 캡션 위에 더하는 정보는 평균 0.002, 가장 큰 감정 boredom 0.014, entrancement 0.012, nostalgia 0.010, surprise 0.009. 신뢰구간은 아직 없다.
- 14개 차원 (`dimension14_partition_lowlevel.tsv`, 영상 2,174개): 캡션 설명력은 valence 0.65·control 0.65·safety 0.66 으로 높고 arousal 0.21·attention 0.18·dominance 0.18 로 낮다. 저수준 (움직임 포함) 이 캡션 위에 더하는 정보는 평균 0.001 (arousal 0.002) 로 범주와 다르지 않다. V-JEPA 2 가 캡션 위에 더하는 정보는 평균 0.006 이고 arousal 이 0.019 로 가장 크다. 각성은 말로 가장 덜 담기는 차원이며, 말로 담기지 않은 부분은 단순 저수준 통계가 아니라 영상 모델의 학습된 시공간 표현에 일부 있다.
