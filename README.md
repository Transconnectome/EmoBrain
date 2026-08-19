# EmoBrain

**When people watch emotional videos, how does the brain's emotion representation relate to visual
processing and semantic processing?** Is it constituted by them, or is it something not reducible to
them? And where in cortex does that construction happen?

> **Authoritative argument: [`docs/paper_logic_merged.md`](docs/paper_logic_merged.md)**
> — premises, RQ, hypotheses H1–H4, the model's role, and the counter-evidence to address.
> Operating rules: [`CLAUDE.md`](CLAUDE.md) · Compact context: [`CONTEXT_EMOBRAIN.md`](CONTEXT_EMOBRAIN.md)

---

## English

**Main theme.** The structure of the high-dimensional emotion space is the structure of visual-semantic
processing.

EmoBrain and its sister project **EmoViS** form **one paper**, not two. EmoViS carries the brain-side
analysis (H1–H3); EmoBrain carries the model derived from that analysis and the test it makes possible
(H4).

### Premises

1. Emotional experience is **high-dimensional**. One stimulus does not evoke one emotion; it evokes a
   blended profile over many. The unit of analysis is the profile, not the category, and the relation
   between stimuli is the distance between profiles.
2. The structure those profiles impose across stimuli is, to a substantial degree, the structure imposed
   by the stimuli's **visual-semantic content**.
3. There is **no distinct brain representation corresponding to a single emotion word**. Emotion words
   name regions of a continuous space.
4. Therefore, looking for emotion in the brain is not looking for an emotion-dedicated region. It is
   asking **where and how visual-semantic processing is organized into a structure that supports emotion
   profiles**.

### Model

`project/code/decoder/` — an **LLM-free label-query decoder**. Brain (per-ROI tokens), video, and caption
enter one shared memory; 34 emotion queries (initialized from emotion-word semantic embeddings)
cross-attend to it and a shared scalar head reads out **34 continuous scores** (`log1p_z`, no softmax).
The task is per-stimulus regression of the 34-dimensional emotion profile.

The contribution concerns **how emotion relates to visual and semantic processing**, not decoding
accuracy.

### What this repository is not

A performance leaderboard, an emotion-category classifier, or an LLM-based decoder. The earlier
direction (Qwen3-VL backbone, open-vocabulary transfer) was **discarded**; those results are kept only
as the evidence that justified discarding it. See [`docs/archive/`](docs/archive/).

---

## 한국어

**Main theme.** 고차원 감정 공간의 구조는 시각-의미 처리의 구조다.

EmoBrain 과 자매 프로젝트 **EmoViS** 는 **두 편이 아니라 한 편의 논문**이다. EmoViS 가 뇌에서의
분석(H1–H3)을, EmoBrain 이 그 분석에서 유도된 모델과 그 모델이 가능케 하는 검정(H4)을 맡는다.

### 대전제

1. 감정 경험은 **고차원**이다. 자극 하나가 감정 하나를 일으키지 않고 여러 감정의 혼합 프로파일을
   일으킨다. 분석 단위는 범주가 아니라 프로파일이고, 자극 간 관계는 프로파일 간 거리다.
2. 그 프로파일들이 자극들 사이에 만드는 구조는, 상당 부분 그 자극들의 **시각-의미 내용**이 만드는
   구조다.
3. **감정 단어 하나에 대응하는 고유한 뇌 표상이 따로 있는 것이 아니다.** 감정 단어는 연속 공간의 어느
   영역을 가리키는 이름이다.
4. 따라서 뇌에서 감정 표상을 찾는 일은 감정 전용 영역을 찾는 일이 아니라, **시각-의미 처리가 어디서·
   어떻게 감정 프로파일을 지지하는 구조로 조직되는지**를 찾는 일이다.

### 모델

`project/code/decoder/` — **LLM 없는 label-query decoder**. brain(ROI별 토큰) + video + caption 이 하나의
memory 에 들어가고, 34개 감정 query(감정 이름 의미 임베딩으로 초기화)가 거기 cross-attend 한 뒤 공유
scalar head 가 **34개 연속 점수**(`log1p_z`, softmax 없음)를 읽는다. task 는 자극별 34차원 감정 프로파일
회귀다.

기여는 **감정이 시각·의미 처리와 맺는 관계**에 대한 것이지 디코딩 성능이 아니다.

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
docs/paper_logic_merged.md   ← authoritative argument (premises, RQ, H1–H4)
docs/notes/                  ← project_decisions.md (decision log), build_log.md (code cycles)
docs/reference/              ← papers.md, datasets.md, du_fu_group_review_0707.md, papers/*.pdf
docs/archive/                ← historical records; every file carries a SUPERSEDED banner
project/                     ← the only active pipeline (see project/README.md)
archive/                     ← large historical result trees and the local literature corpus
```
