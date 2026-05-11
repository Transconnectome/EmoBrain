# NetFeeliX Claude Instructions

Read `CONTEXT_NETFEELIX.md` first. It is the compact project memory and should
not be duplicated here.

## Operating Rules

- Keep root files minimal. Do not create new brief/proposal/narrative markdown
  files unless explicitly requested.
- Canonical narrative lives in `Paper/framework_EN.md` and
  `Paper/framework_KR.md`.
- Canonical methodology lives in `Paper/methodology.md`.
- Active Korean execution plan lives in `ACTION_PLAN.md`.
- Project-operation scripts live in `scripts/`.
- Runnable setup/experiment scripts live in `setup/code/`.
- Generated data/logs/results live in `setup/data/`, `setup/logs/`, and
  `setup/results/`.
- Do not overwrite raw data, model checkpoints, embeddings, or experiment
  outputs.

## Scientific Rules

- NetFeeliX is model-development, not emotion theory.
- Use SwiFT first, but pivot if matched benchmarks favor another neural
  representation or model.
- Treat TRIBE v2 as stimulus-to-brain teacher/baseline/alignment component, not
  an fMRI encoder replacement.
- Treat old EmoDe caches as reference only.
- Use `2185` as the canonical Horikawa/Cowen stimulus count.
- Keep claims separated from measured results.

## Required Checks

After structural documentation edits:

```bash
python3 scripts/check_md_completeness.py
```

To refresh generated status:

```bash
python3 scripts/build_project_status.py
```
