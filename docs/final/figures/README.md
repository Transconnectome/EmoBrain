# 연구설계 그림 (07_research_design.md)

`07_research_design.md`가 상대 경로 `figures/`로 참조하는 그림이다. 파일 이름과 그림 번호는 문서의 링크와 같다.

| 문서 그림 | 파일 | 내용 |
|---|---|---|
| 그림 1 | `emobrain_ridge_overview` | VCE 학습과 head 선택, 같은 head 출력이 분석 3, 4, 5, 6으로 이어지는 흐름. ⑥은 4번 줄의 encoding 모델로 본 영상을 맞히고 정서를 추정한다(11/27) |
| 그림 2 | `emobrain_videomae_methods` | 두 학습 단계와 head를 읽거나 제거하는 위치 |
| 그림 3a | `emobrain_head_layers` | 공포 목록 고르기(켜진 마스크와 꺼진 마스크의 평균 r 차이 예시), 목록의 층 위치, 시험 영상의 두 결론(무작위 대조, 다른 정서 목록 대조) |
| 그림 3b | `emobrain_head_captions` | 전체 캡션이 움직임과 물체 이름을 고려한 뒤 더하는 설명력: 두 예측 경로, L+O 대 L+O+S, 고유분과 공유분. S는 캡션을 고치지 않고 쓴다(11/27 결정 8) |
| 보충 그림 S1 | `emobrain_chase_head_roi` | ‘쫓다’ 예시(부록, 11/26에 그림 3c에서 이름을 바꿈) |
| 그림 4a | `emobrain_roi_partition` | 한 영역에서 세 모형의 예측, 분할 계산 예시, 영역별 세 값, 그림 3b와의 연결 |
| 그림 4b | `emobrain_regional_alignment` | 비교하는 모델 판(학습 전후, 공포 목록 head와 무작위 head를 끔), RSA와 encoding, 추가 하락 예시 |
| 그림 5 | `emobrain_brain_decoding` | 분석 6의 주 분석(11/27 결정 7): 참가자별 encoding 모델 적합, 본 영상 맞히기, 가장 닮은 후보 영상들의 평정으로 한 정서 추정, 보고할 값. 이전 판(특징 복원과 고정 판독기)은 git 기록에 있다 |
| 그림 2~5 묶음 | `emobrain_methods_figures.pdf` | 방법론 그림 한 파일 |
| 그림 3a, 3b 묶음 | `emobrain_head_interpretation.pdf` | head 해석 그림 한 파일 |

이전 그림 묶음(글 상자 중심, 커밋 abf6eee3)과 그 코드는 git 기록에 남아 있다. 11/26 석진 님 결정으로 실제 영상 프레임과 뇌 그림을 쓰는 이 묶음으로 바꿨다. 같은 날 그림 3a, 3b, 4a, 4b는 그림 하나가 질문 하나에 답하도록 숫자 예시 중심으로 다시 그렸다(이전 판은 커밋 36c34a5d). 그 뒤 공개 레포에 Cowen 영상의 실제 프레임을 싣지 않기로 해(석진 님 결정), 영상 프레임 자리는 같은 크기의 도식(회색 사각형, 재생 기호, 짧은 글)으로 바꿨다.

## 실제 이미지의 출처

- 영상 프레임: 실제 프레임을 쓰지 않고 도식(`kit.py`의 `frame_icon`)으로 그린다. 예시 영상은 Cowen과 Keltner(2017)의 자극 영상 1374(공포, ‘쫓다’ 캡션 13/20)다. 그림 코드는 영상 파일을 내려받거나 읽지 않는다.
- 캡션 문장: 프로젝트의 MindCaptioning 캡션 파일(`data/caption_ck20.csv`)에서 영상 1374의 실제 문장.
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
pip install matplotlib nilearn
```

```bash
python3 docs/final/figures/src/fetch_assets.py
```

```bash
EMOBRAIN_FIG_OUT=docs/final/figures python3 docs/final/figures/src/build_all.py
```

그림을 다시 만든 뒤 07의 HTML 판(그림을 base64로 품은 한 파일)도 다시 만든다. Python-Markdown이 필요하다.

```bash
python3 docs/final/figures/src/build_07_html.py
```
