# 연구설계 그림 (07_research_design.md)

`07_research_design.md`가 상대 경로 `figures/`로 참조하는 그림이다. 파일 이름과 그림 번호는 문서의 링크와 같다.

| 문서 그림 | 파일 | 내용 |
|---|---|---|
| 그림 1 | `emobrain_ridge_overview` | VCE 학습과 head 선택, 같은 head 출력이 분석 3, 4, 5, 6으로 이어지는 흐름 |
| 그림 2 | `emobrain_videomae_methods` | 두 학습 단계와 head를 읽거나 제거하는 위치 |
| 그림 3a | `emobrain_head_layers` | head 순위 추정, 선택 head 위치, 시험 영상의 선택성 |
| 그림 3b | `emobrain_head_captions` | L, O, S가 두 대상을 예측하는 경로, 일곱 조합, 고유분과 공유분 |
| 그림 3c | `emobrain_chase_head_roi` | ‘쫓다’ 예시(보조) |
| 그림 4a | `emobrain_roi_partition` | head 출력과 27개 평정의 영역별 분할 |
| 그림 4b | `emobrain_regional_alignment` | 온전한 모델과 제거 모델의 RSA와 encoding |
| 그림 5 | `emobrain_brain_decoding` | 참가자별 특징 복원과 고정 판독기 |
| 그림 2~5 묶음 | `emobrain_methods_figures.pdf` | 방법론 그림 한 파일 |
| 그림 3a, 3b 묶음 | `emobrain_head_interpretation.pdf` | head 해석 그림 한 파일 |

## 실제 이미지의 출처

- 영상 프레임: Cowen과 Keltner(2017)의 자극 영상 1374(공포, ‘쫓다’ 캡션 13/20), 366, 55. 저자의 공개 미리보기 사이트(bsil.berkeley.edu)에서 받았고 설명용으로만 쓴다.
- 캡션 문장: 프로젝트의 MindCaptioning 캡션 파일(`project/shared/data/caption_ck20.csv`)에서 영상 1374의 실제 문장.
- 평정: 영상 1374의 실제 Cowen 평정(27개 범주). 예측값과 R² 등은 가상 예시이며 그림마다 "values illustrative"로 표시했다.
- 뇌: MNI152 표준 뇌(T1)와 fsaverage5 피질 표면. 둘 다 nilearn에 들어 있다. 표면 위의 영역 색은 설명용이다.

## 형식

- 폭 180 mm(두 단), Liberation Sans(Arial 호환).
- 블록 안에 자료의 모양을 적었다. 예: N × 64K, N × 27, 1568 × 768.
- 불꽃 표시는 학습하는 부분, 눈송이 표시는 고정된 부분이다.
- 색의 역할은 모든 그림에서 같다.
  - 주황: 선택 head 출력
  - 녹색: 마지막 층 768차원 벡터
  - 보라: 사람 정서 평정
  - 붉은색: fMRI
  - 파랑, 갈색, 자주: L, O, S
- PDF와 SVG는 글자를 텍스트로 남겨 편집할 수 있다. PNG는 300 dpi다.

## 다시 그리기

```bash
pip install matplotlib nilearn opencv-python-headless
```

```bash
python3 docs/final/figures/src/fetch_assets.py
```

```bash
EMOBRAIN_FIG_OUT=docs/final/figures python3 docs/final/figures/src/build_all.py
```
