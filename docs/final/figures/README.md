# 연구설계 그림 (07_research_design.md)

`07_research_design.md`가 상대 경로 `figures/`로 참조하는 그림이다. 파일 이름과 그림 번호는 문서의 링크와 같다.

| 문서 그림 | 파일 | 내용 |
|---|---|---|
| 그림 1 | `emobrain_ridge_overview` | 선택 head가 분석 3, 4, 5, 6을 잇는 전체 흐름 |
| 그림 2 | `emobrain_videomae_methods` | VideoMAE 구조와 head를 읽거나 제거하는 위치 |
| 그림 3a | `emobrain_head_layers` | 선택 head의 층 분포, 순위 추정, 시험 영상의 선택성 대비 |
| 그림 3b | `emobrain_head_captions` | L, O, S 일곱 조합과 고유분·공유분 |
| 그림 3c | `emobrain_chase_head_roi` | ‘쫓다’ 단어 예시(보조) |
| 그림 4a | `emobrain_roi_partition` | head 특징과 27개 평정의 영역별 분할 |
| 그림 4b | `emobrain_regional_alignment` | 온전한 모델과 제거 모델의 RSA와 encoding |
| 그림 5 | `emobrain_brain_decoding` | 참가자별 특징 복원과 고정 판독기 |
| 그림 2~5 묶음 | `emobrain_methods_figures.pdf` | 방법론 그림 한 파일 |
| 그림 3a, 3b 묶음 | `emobrain_head_interpretation.pdf` | head 해석 그림 한 파일 |

## 형식

- 학술지 양식: 폭 180 mm(두 단), Liberation Sans(Arial 호환) 5~7 pt, 굵은 소문자 패널 기호.
- 색의 역할은 모든 그림에서 고정했다.
  - 주황: 선택 head 출력, 읽기·제거 위치
  - 녹색: 마지막 층 768차원 벡터
  - 보라: 사람 정서 평정
  - 붉은색: fMRI
  - 파랑, 갈색, 자주: L, O, S
- 가상 예시 수치는 그림마다 "Values illustrative"로 표시했다. 그림 3b의 수치는 본문 예시(0.30 − 0.20 = 0.10, 0.28 − 0.23 = 0.05, 공유분 합 0.14와 0.11)와 맞춘 하나의 분해에서 계산했다.
- PDF와 SVG는 글자를 텍스트로 남겨 편집할 수 있다. PNG는 300 dpi다.

## 다시 그리기

```bash
pip install matplotlib
```

```bash
python3 docs/final/figures/src/build_all.py
```
