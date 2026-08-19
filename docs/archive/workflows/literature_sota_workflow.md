> ⚠️ **ARCHIVED — 역사 기록. 현행 문서가 아니다.**
> 현행 논증 = `docs/paper_logic_merged.md` (대전제 · RQ · 가설 H1–H4). 운영 규칙 = `CLAUDE.md`.
>
> 아래 내용 중 다음은 **뒤집혔다.** (a) Qwen3-VL 등 LLM backbone 사용 — 금지.
> (b) open-vocabulary / cross-taxonomy 전이를 headline novelty 로 삼는 프레임 — 폐기.
> (c) 학습에 없던 감정 zero-shot — 폐기(원칙적 분할 기준 없음, RQ 와 무관).
> (d) "EmoBrain 과 EmoViS 는 별도 논문 2편" — 현재는 **한 편의 논문**.
> (e) "EmoBrain 은 cortical location 을 주장하지 않는다" — 현재 **H3 이 cortical location 주장**이다.

# Literature And SOTA Workflow

Purpose: keep FEEL literature, dataset, and code references current without
spreading notes across random files.

## Inputs

- Search topic or question.
- Current canonical docs:
  - `CONTEXT_EMOBRAIN.md`
  - `reference/papers.md`
  - `reference/datasets.md`
  - `reference/code_resources.md`
  - `reference/systematic_reference_map.md`

## Steps

1. Define the search scope.
   - model: SwiFT, SwiFUN, BFM, JEPA, NeuroSTORM, TRIBE v2,
   - data: HCP, Horikawa, Emo-FilM, REELMO, NSD, IAPS, OASIS,
   - method: naturalistic pretraining, stimulus-brain alignment, affective
     LLM/VLM, brain tuning.
2. Search primary sources first.
   - Papers, official project pages, OpenNeuro/NeuroVault, official GitHub
     repositories.
3. Extract structured notes using `docs/templates/paper_note.md`,
   `docs/templates/dataset_card.md`, or `docs/templates/model_card.md`.
4. Update canonical reference docs only when the item changes decisions.
   - paper claims -> `reference/papers.md` or `systematic_reference_map.md`
   - datasets -> `reference/datasets.md`
   - code/models -> `reference/code_resources.md`
5. Add a decision if the result changes the project direction.
   - use `docs/templates/decision_log.md`
   - append the conclusion to `notes/project_decisions.md`.

## Output Format

```markdown
## Search Summary

## New Papers

## New Datasets

## New Code / Models

## FEEL Decisions

## Open Questions
```

## Verification

- Every citation has URL/DOI.
- No paper is added only because it sounds relevant.
- No "foundation model" claim is made without pretraining/transfer evidence.
- `python3 scripts/check_md_completeness.py` passes.
