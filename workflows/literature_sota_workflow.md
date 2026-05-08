# Literature And SOTA Workflow

Purpose: keep NetFeeliX literature, dataset, and code references current without
spreading notes across random files.

## Inputs

- Search topic or question.
- Current canonical docs:
  - `CONTEXT_NETFEELIX.md`
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
3. Extract structured notes using `templates/paper_note.md`,
   `templates/dataset_card.md`, or `templates/model_card.md`.
4. Update canonical reference docs only when the item changes decisions.
   - paper claims -> `reference/papers.md` or `systematic_reference_map.md`
   - datasets -> `reference/datasets.md`
   - code/models -> `reference/code_resources.md`
5. Add a decision if the result changes the project direction.
   - use `templates/decision_log.md`
   - append the conclusion to `notes/project_decisions.md`.

## Output Format

```markdown
## Search Summary

## New Papers

## New Datasets

## New Code / Models

## NetFeeliX Decisions

## Open Questions
```

## Verification

- Every citation has URL/DOI.
- No paper is added only because it sounds relevant.
- No "foundation model" claim is made without pretraining/transfer evidence.
- `python3 scripts/check_md_completeness.py` passes.
