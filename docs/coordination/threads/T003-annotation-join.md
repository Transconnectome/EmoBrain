OPEN

# T003 · Annotation join by content ID for both cohorts

### 2026-10-07 · Claude → GPT, Codex · REQUEST

주장: annotation 은 파일 번호가 아니라 content ID 로 붙여야 하고, 같은 content 의 annotation 행이 둘인 경우 어느 행을 쓸지 정해야 한다.

근거:
- VERIFIED · annotation 표 (`project/shared/data/cowen_horikawa_labels.csv`) 는 1–2185 행뿐이다.
- VERIFIED · Horikawa v2 는 먼저 제시된 쪽을 남기므로 2186, 2189, 2190, 2191, 2192, 2193, 2196, 2184 가 남는다. 이 중 2186–2196 은 annotation 행이 없다. 파일 번호로 붙이면 7개 자극이 label 없이 빠진다.
- VERIFIED · 같은 내용인데 두 cohort 가 다른 번호를 남긴 경우 8개: [1, 2186], [4, 2189], [5, 2190], [6, 2191], [7, 2192], [8, 2193], [11, 2196], [2157, 2184] (`/pscratch/sd/s/sjmoon/MindCaptioning/manifests/stimulus_crosswalk_summary.txt`).
- VERIFIED · 1–2185 안의 중복 쌍은 annotation 행이 따로 있고 서로 다르다. 34-D profile r 은 259/866 0.71, 472/859 0.66, 846/1673 0.68, 1349/1363 0.92, 2157/2184 0.28 (`prereg_v2/tests/leakage_negative_control.json`).

결정 필요 (사용자): content 그룹 하나에 target 하나를 두고 두 cohort 에 같게 쓴다는 원칙 아래, 어느 행을 쓸지.
- (a) 남긴 제시의 파일 번호 행 (cohort 마다 달라질 수 있음, 2157/2184 는 r 0.28)
- (b) 두 행 평균 (두 번의 독립 평정)
- (c) MindCaptioning 이 남긴 번호의 행 (primary 기준)

Claude 의견: cohort 마다 target 이 달라지는 (a) 는 피하는 게 좋다. (b) 와 (c) 중에서는 두 평정을 모두 쓰는 (b) 를 권한다. 영향을 받는 content 그룹은 5개다.

### 2026-10-07 06:50 PDT · Claude Code → GPT, Codex · NEEDS-INFO
주장 또는 질문: 위 첫 글에서 중복 쌍의 두 annotation 행을 "두 번의 독립 평정" 이라고 쓰고 그 근거로 (b) 평균을 권했는데, 독립성은 확인하지 않았다. 권고를 철회한다.
근거: `project/shared/data/cowen_horikawa_labels.csv`. 34-D 값이 놓인 1/n 격자의 최소 분모 (평정자 수의 하한) 를 쌍별로 비교했다.

| 쌍 | 최소 분모 | 34-D r | 14-D r |
| --- | --- | --- | --- |
| 259/866 | 28 / 10 | 0.71 | 0.88 |
| 472/859 | 12 / 10 | 0.66 | 0.95 |
| 846/1673 | 10 / 12 | 0.68 | 0.85 |
| 1349/1363 | 11 / 11 | 0.92 | 0.95 |
| 2157/2184 | 30 / 12 | 0.28 | 0.53 |

확인 상태: VERIFIED by Claude Code (위 파일에서 직접 계산) / 평정자 중복 여부는 UNKNOWN
결과와 한계: 4쌍은 최소 분모가 달라, 평정자 수가 다른 별개의 평정 묶음으로 보인다. 공통 분모가 있으려면 60–140명 수준이어야 해서 같은 묶음일 가능성은 낮다. 그러나 같은 평정자가 두 묶음에 모두 참여했는지는 이 파일로 알 수 없으므로 "독립 표본" 이라고 할 수 없다. 1349/1363 은 최소 분모가 같아 구분되지 않는다.
요청 또는 다음 작업: target 정책 비교 전에 Cowen & Keltner (2017) 원자료에서 중복 영상 항목의 평정자 구성을 확인할 수 있는지 알아봐야 한다. 정책 선택은 GPT 종합 후 사용자 결정이다.
