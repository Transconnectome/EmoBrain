> ⚠️ **ARCHIVED — 역사 기록. 현행 문서가 아니다.**
> 현행 논증 = `docs/paper_logic_merged.md` (대전제 · RQ · 가설 H1–H4). 운영 규칙 = `CLAUDE.md`.
>
> 아래 내용 중 다음은 **뒤집혔다.** (a) Qwen3-VL 등 LLM backbone 사용 — 금지.
> (b) open-vocabulary / cross-taxonomy 전이를 headline novelty 로 삼는 프레임 — 폐기.
> (c) 학습에 없던 감정 zero-shot — 폐기(원칙적 분할 기준 없음, RQ 와 무관).
> (d) "EmoBrain 과 EmoViS 는 별도 논문 2편" — 현재는 **한 편의 논문**.
> (e) "EmoBrain 은 cortical location 을 주장하지 않는다" — 현재 **H3 이 cortical location 주장**이다.

# Reference Folder

This folder contains the literature, dataset, and code-resource map for FEEL.

## Files

- `papers.md`: paper-by-paper reference index.
- `systematic_reference_map.md`: canonical role-based reference map for proposal writing.
- `datasets.md`: canonical function-based dataset inventory. Use this when a
  benchmark table names Horikawa, Emo-FilM, Affective Videos, IAPS, NeuroEmo,
  Koide-Majima/Nishimoto, or REELMO and you need to know what the dataset is.
- `task.md`: canonical task and target inventory.
- `training_strategy.md`: post-benchmark SwiFT/BFM training and model-development strategy.
- `code_resources.md`: repository and implementation resources. Use this when a
  benchmark table names SwiFT, Brain-JEPA, NeuroSTORM, BrainLM, TRIBE, or other
  models and you need to know what the model is.
- `search_log_2026-05-08.md`: initial web-search log.

## Detail Map

| Question | Read |
|---|---|
| What is Horikawa / Emo-FilM / Affective Videos / IAPS? | `reference/datasets.md` |
| What is SwiFT / Brain-JEPA / NeuroSTORM / BrainLM? | `reference/code_resources.md` and `reference/papers.md` |
| What does binary/regression/multiclass/high-dimensional mean? | `reference/task.md` |
| What happens after the BFM benchmark? | `reference/training_strategy.md` |
| What is the current benchmark table? | `notes/benchmark_design.md` |

## Update Rule

When adding a new paper or codebase, record:

- what it is,
- what it claims,
- how it matters for FEEL,
- source URL or DOI,
- next action.

Avoid creating additional reference-map markdown files. Add synthesis to `systematic_reference_map.md` and individual entries to `papers.md`, `datasets.md`, or `code_resources.md`.
