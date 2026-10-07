# EmoBrain

**When people watch emotional videos, how does the brain's emotion representation relate to sensory
processing and semantic processing?** Is it constituted by them, or is it something not reducible to
them? And where in cortex does that construction happen?

> **Authoritative argument: [`docs/paper_logic_merged.md`](docs/paper_logic_merged.md)**
> — premises, RQ, hypotheses H1–H4, the model's role, dataset roles, and the counter-evidence to address.
> Operating rules: [`CLAUDE.md`](CLAUDE.md) · Compact context: [`CONTEXT_EMOBRAIN.md`](CONTEXT_EMOBRAIN.md)

---

## English

**Main theme.** When people watch emotional videos, the representational structure the brain builds
follows sensory-semantic content rather than emotion labels, and that organization extends beyond
visual cortex into transmodal association cortex.

**Scope of the sensory axis.** The general claim is sensory-semantic. Because the stimuli here are
silent videos, the axis actually tested is **vision alone**. Results are therefore claims about
visual-semantic content, not about sensory processing in general. Silence is a design advantage, not a
limitation: it rules out soundtrack, dialogue, and sound design as the source of the profile structure
without any additional control. Extension to audition is deferred.

EmoBrain and its sister project **EmoViS** form **one paper**, not two. EmoViS carries the brain-side
analysis (H1–H3); EmoBrain carries the model derived from that analysis and the test it makes possible
(H4).

### Premises

1. Emotional experience is **high-dimensional**. One stimulus does not evoke one emotion; it evokes a
   blended profile over many. The unit of analysis is the profile, not the category, and the relation
   between stimuli is the distance between profiles.
2. The structure those profiles impose across stimuli is, to a substantial degree, the structure imposed
   by the stimuli's **sensory-semantic content**.
3. There is **no distinct brain representation corresponding to a single emotion word**. Emotion words
   name regions of a continuous space.
4. Therefore, looking for emotion in the brain is not looking for an emotion-dedicated region. It is
   asking **where and how sensory-semantic processing is organized into a structure that supports
   emotion profiles**.

### Model

`project/code/decoder/` — an **LLM-free label-query decoder**. Inputs enter one shared memory; 34
emotion queries (initialized from emotion-word semantic embeddings) cross-attend to it and a shared
scalar head reads out **34 continuous scores** (`log1p_z`, no softmax). The task is per-stimulus
regression of the 34-dimensional emotion profile.

The deliverable is a **brain-only student**. Two teachers are trained, and the contrast between them is
itself a result:

| | Inputs | Role |
|---|---|---|
| **content teacher** | video + caption | canonical condition for H4 |
| **full teacher** | brain + video + caption | performance condition; direction for later emotion-model work |

The student sees **brain only** and is trained on hard labels plus cached teacher outputs. A
label-only student with identical initialization and seed is the mandatory comparison.

The contribution concerns **how emotion relates to sensory and semantic processing**, not decoding
accuracy.

### Datasets

| Dataset | Role |
|---|---|
| **Horikawa** (5 subjects, 2181 unique silent clips, CK34 + 14 dimensions) | **main** — H1–H4 |
| **MindCaptioning** (ds005191, 6 subjects, same clips) | **independent cohort on the same stimuli** — replication of H1–H3, raises subject count to 11 |
| **Emo-FilM** (ds004872, films) | **cross-dataset test for H4 only**; not yet acquired |

MindCaptioning is not a cross-dataset test: the stimuli are the same, so it cannot speak to whether the
organization survives a change of stimulus set. Emo-FilM is not the main dataset: it has audio, its
segments share content within a film, and its label set is 13 discrete emotions. See
[`docs/paper_logic_merged.md`](docs/paper_logic_merged.md) §8.

### What this repository is not

A performance leaderboard, an emotion-category classifier, or an LLM-based decoder. The earlier
direction (Qwen3-VL backbone, open-vocabulary transfer) was **discarded**; those results are kept only
as the evidence that justified discarding it. See [`docs/archive/`](docs/archive/).

---

## 한국어

**Main theme.** 감정 영상을 볼 때 뇌가 만드는 표상 구조는, 감정 라벨이 아니라 감각-의미 내용을
따른다. 그리고 그 조직은 시각피질을 넘어 transmodal 연합피질까지 이어진다.

**감각 축의 검정 범위.** 일반 주장은 감각-의미다. 다만 여기서 쓰는 자극이 무음 영상이므로 실제로
검정하는 축은 **시각 하나**다. 따라서 결과는 감각 처리 일반이 아니라 시각-의미 내용에 대한 것이다.
무음은 제약이 아니라 설계상의 이점이다. 감정 프로파일 구조를 사운드트랙·대사·음향이 만들었을
가능성이 추가 통제 없이 배제된다. 청각으로의 확장은 미룬다.

EmoBrain 과 자매 프로젝트 **EmoViS** 는 **두 편이 아니라 한 편의 논문**이다. EmoViS 가 뇌에서의
분석(H1–H3)을, EmoBrain 이 그 분석에서 유도된 모델과 그 모델이 가능케 하는 검정(H4)을 맡는다.

### 대전제

1. 감정 경험은 **고차원**이다. 자극 하나가 감정 하나를 일으키지 않고 여러 감정의 혼합 프로파일을
   일으킨다. 분석 단위는 범주가 아니라 프로파일이고, 자극 간 관계는 프로파일 간 거리다.
2. 그 프로파일들이 자극들 사이에 만드는 구조는, 상당 부분 그 자극들의 **감각-의미 내용**이 만드는
   구조다.
3. **감정 단어 하나에 대응하는 고유한 뇌 표상이 따로 있는 것이 아니다.** 감정 단어는 연속 공간의 어느
   영역을 가리키는 이름이다.
4. 따라서 뇌에서 감정 표상을 찾는 일은 감정 전용 영역을 찾는 일이 아니라, **감각-의미 처리가 어디서·
   어떻게 감정 프로파일을 지지하는 구조로 조직되는지**를 찾는 일이다.

### 모델

`project/code/decoder/` — **LLM 없는 label-query decoder**. 입력이 하나의 memory 에 들어가고, 34개 감정
query(감정 이름 의미 임베딩으로 초기화)가 거기 cross-attend 한 뒤 공유 scalar head 가 **34개 연속
점수**(`log1p_z`, softmax 없음)를 읽는다. task 는 자극별 34차원 감정 프로파일 회귀다.

최종 산물은 **뇌만 보는 student** 다. teacher 는 두 조건으로 학습하며, 둘의 대비 자체가 결과다.

| | 입력 | 역할 |
|---|---|---|
| **content teacher** | 영상 + 설명글 | H4 의 정본 조건 |
| **full teacher** | 뇌 + 영상 + 설명글 | 성능 조건이자 후속 감정 모델 개발의 방향 |

student 는 **뇌만** 보고, 라벨과 cached teacher 출력을 함께 학습한다. 동일 초기화·동일 seed 의
라벨-only student 가 필수 비교 대상이다.

기여는 **감정이 감각·의미 처리와 맺는 관계**에 대한 것이지 디코딩 성능이 아니다.

### 데이터셋

| 데이터셋 | 역할 |
|---|---|
| **Horikawa** (5명, 2181 고유 무음 클립, CK34 + 14차원) | **메인** — H1–H4 |
| **MindCaptioning** (ds005191, 6명, 같은 클립) | **같은 자극 독립 코호트** — H1–H3 재현, 피험자 5 → 11 |
| **Emo-FilM** (ds004872, 영화) | **H4 의 cross-dataset 검정 전용**, 미확보 |

MindCaptioning 은 cross-dataset 이 아니다. 자극이 같으므로 조직이 자극 집합을 넘어 유지되는지를 재지
못한다. Emo-FilM 은 메인이 아니다. 소리가 있고, 한 영화 안의 구간들이 내용을 공유하며, 라벨이 13개
이산 감정이다. [`docs/paper_logic_merged.md`](docs/paper_logic_merged.md) §8 참조.

### 이 저장소가 아닌 것

성능 경쟁, 감정 범주 분류기, LLM 기반 디코더. 이전 방향(Qwen3-VL backbone, open-vocabulary 전이)은
**폐기**되었고 그 결과들은 폐기의 근거로만 보존한다. [`docs/archive/`](docs/archive/) 참조.

---

## Environment / 환경

| | |
|---|---|
| Python (probe, 분석) | `/pscratch/sd/s/sjmoon/tribev2/.venv` |
| Python (LLM fusion, LoRA — LEGACY) | `/pscratch/sd/s/sjmoon/brainvlm_qwen_env` |
| Compute | **NERSC m5187** (cpu queue; gpu queue A100 80GB) |
| Submodule — BrainVLM reference | `external/repos/BrainVLM` |
| Submodule — fMRI-LM reference | `external/repos/fMRI-LM` |

```bash
cd EmoBrain && git submodule update --init --recursive
```

GPU job 은 사용자가 직접 실행한다. 자세한 내용은 [`project/README.md`](project/README.md).

## Repository layout

```text
docs/paper_logic_merged.md   ← authoritative argument (premises, RQ, H1–H4, datasets)
docs/notes/                  ← project_decisions.md (decision log), build_log.md (code cycles)
docs/reference/              ← papers.md, datasets.md, du_fu_group_review_0707.md, papers/*.pdf
docs/archive/                ← historical records; every file carries a SUPERSEDED banner
project/                     ← the only active pipeline (see project/README.md)
archive/                     ← large historical result trees and the local literature corpus
```