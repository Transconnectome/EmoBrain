> ⚠️ **ARCHIVED — 역사 기록. 현행 문서가 아니다.**
> 현행 논증 = `docs/paper_logic_merged.md` (대전제 · RQ · 가설 H1–H4). 운영 규칙 = `CLAUDE.md`.
>
> 아래 내용 중 다음은 **뒤집혔다.** (a) Qwen3-VL 등 LLM backbone 사용 — 금지.
> (b) open-vocabulary / cross-taxonomy 전이를 headline novelty 로 삼는 프레임 — 폐기.
> (c) 학습에 없던 감정 zero-shot — 폐기(원칙적 분할 기준 없음, RQ 와 무관).
> (d) "EmoBrain 과 EmoViS 는 별도 논문 2편" — 현재는 **한 편의 논문**.
> (e) "EmoBrain 은 cortical location 을 주장하지 않는다" — 현재 **H3 이 cortical location 주장**이다.

# Experiment Planning Workflow

Purpose: convert broad model ideas into runnable experiments with clear decision
rules.

## Inputs

- Model idea or dataset question.
- `reference/datasets.md`
- `reference/task.md`
- `reference/training_strategy.md`
- `Paper/methodology.md`

## Steps

1. Choose the dataset function.
   - direct emotion-labeled fMRI,
   - movie-watching pretraining,
   - stimulus-to-brain alignment,
   - static-image affect transfer,
   - physiology/context extension.
2. Choose the target.
   - arousal, valence, discrete category, high-dimensional vector,
     appraisal/component, retrieval/alignment.
3. Define comparable model conditions.
   - simple baseline,
   - frozen SwiFT,
   - adapted SwiFT,
   - stimulus-only,
   - TRIBE-teacher or aligned model.
4. Define the split and metric before running.
5. Create an experiment card from `docs/templates/experiment_card.md`.
6. Store planned cards under `reports/status/` until code is ready.
7. Initial runnable scripts go into `project/shared/code/`; outputs go to `project/shared/data/`,
   `project/shared/output/logs/`, and `project/shared/results/`.

## Required Decision Rule

Every experiment must answer one of:

- continue SwiFT frozen/adapted transfer,
- invest in naturalistic movie/story continued pretraining,
- prioritize TRIBE-SwiFT alignment,
- use stimulus-side affective LLM/VLM supervision,
- stop because dataset/target is not useful.

## Output

- one experiment card,
- one short decision entry in `notes/project_decisions.md` when the experiment
  changes priorities.
