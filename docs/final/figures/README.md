# Figures for the research design

The Markdown reads its eight PNGs from this folder. The [standalone HTML](../07_research_design.html) embeds the same PNGs and the linked PDF and SVG downloads.

| Figure | Filename stem (prefix `emobrain_`) | What it shows |
|---|---|---|
| 1 | `ridge_overview` | How analyses ③, ④ and ⑥ use the same heads |
| 2 | `videomae_methods` | VideoMAE blocks and the point of head readout or masking |
| 3a | `head_layers` | Head selection and location within 12 blocks |
| 3b | `head_captions` | Seven combinations of visual features, object names and captions |
| 3c (appendix) | `chase_head_roi` | A worked example using one caption word |
| 4a | `roi_partition` | Unique and shared regional predictions from heads and ratings |
| 4b | `regional_alignment` | RSA and voxel encoding with intact or masked features |
| 5 | `brain_decoding` | Subject-specific feature decoding and the fixed readout |

The [methods PDF](emobrain_methods_figures.pdf) puts the six main methods panels first and appendix figure 3c last. The [head analysis PDF](emobrain_head_interpretation.pdf) contains 3a and 3b.

## Rebuild

Install Poppler (`pdftoppm`) and the Python dependencies below. Run from the repository root. The reference figures use Apple SD Gothic Neo and Arial on macOS. On other systems, set `EMOBRAIN_FIGURE_FONT_NORMAL` and `EMOBRAIN_FIGURE_FONT_BOLD` to Korean TrueType font files and `EMOBRAIN_FIGURE_ARIAL` to the directory containing `Arial.ttf`, `Arial Bold.ttf` and `Arial Italic.ttf`. Other fonts can change text widths.

```sh
python3 -m pip install matplotlib fonttools pymupdf reportlab beautifulsoup4
python3 docs/final/figures/src/build_all.py
```

The command redraws all eight figures, assembles the PDFs and updates the images embedded in the HTML. Pass `--out /path/to/preview` to render figures separately for inspection.

---

# 연구설계 통합문서 그림

Markdown은 이 폴더에서 그림 8개의 PNG를 불러온다. [단일 파일 HTML](../07_research_design.html)에는 같은 PNG와 본문에서 내려받는 PDF, SVG가 들어 있다.

| 그림 | 파일 이름 (`emobrain_` 뒤) | 내용 |
|---|---|---|
| 1 | `ridge_overview` | ③, ④, ⑥에서 같은 head가 어떻게 쓰이는가 |
| 2 | `videomae_methods` | VideoMAE 구조와 head를 읽거나 가리는 위치 |
| 3a | `head_layers` | 정서별로 선택한 head와 12개 블록에서의 위치 |
| 3b | `head_captions` | 저수준 시각, 물체 이름, 전체 캡션의 일곱 조합 |
| 3c (부록) | `chase_head_roi` | 캡션 단어 하나로 읽는 예시 |
| 4a | `roi_partition` | head 특징과 사람 평정이 영역별 뇌 반응을 따로 또는 함께 설명하는 몫 |
| 4b | `regional_alignment` | 온전한 모델과 head를 가린 모델의 RSA 및 복셀 예측 |
| 5 | `brain_decoding` | 참가자별 ridge로 복원한 특징과 고정된 정서 판독기 |

[방법론 그림 PDF](emobrain_methods_figures.pdf)는 본문 패널 6개 다음에 부록 그림 3c를 싣는다. [head 분석 그림 PDF](emobrain_head_interpretation.pdf)에는 3a와 3b가 들어 있다.

## 다시 그리기

Poppler(`pdftoppm`)를 설치하고 저장소 루트에서 위의 Python 명령 두 줄을 실행한다. 원본 글꼴은 macOS의 Apple SD Gothic Neo와 Arial이다. 다른 환경에서는 `EMOBRAIN_FIGURE_FONT_NORMAL`과 `EMOBRAIN_FIGURE_FONT_BOLD`에 한글 TrueType 파일을, `EMOBRAIN_FIGURE_ARIAL`에 `Arial.ttf`, `Arial Bold.ttf`, `Arial Italic.ttf`가 있는 폴더를 지정한다. 글꼴을 바꾸면 글자 폭이 달라질 수 있다.

기본 명령은 그림 8개와 PDF 묶음을 만들고 HTML 안의 그림까지 갱신한다. `--out /path/to/preview`를 주면 별도 폴더에서 그림을 검토할 수 있다.
