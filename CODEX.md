# NetFeeliX Codex Instructions

This file gives coding-agent instructions for NetFeeliX.

## Working Style

- Read `README.md`, `CLAUDE.md`, `Paper/framework_EN.md`, `Paper/framework_KR.md`, and `notes/project_decisions.md` before making structural changes.
- Use `rg` or `rg --files` for search.
- Keep edits scoped. Do not reorganize folders without updating this file and `CLAUDE.md`.
- Never overwrite existing user data or experiment outputs.
- When creating scripts, put them under `study{N}/code/` and create a companion `.md` file explaining inputs, outputs, assumptions, and example usage.
- Do not create new planning/proposal/brief Markdown files unless explicitly asked. Merge framing into `Paper/framework_EN.md` and `Paper/framework_KR.md`; merge method details into `Paper/methodology.md`.
- Remember that NetFeeliX is primarily a model-development project. Keep emotion theory minimal and subordinate to model/dataset/evaluation decisions.

## Code Locations

- `code/`: shared utilities or planning notes used by multiple studies.
- `study1/code/`: first-pass baselines and data indexing.
- Future studies should follow the same shape: `study{N}/code`, `study{N}/data`, `study{N}/logs`, `study{N}/results`.

## Study Naming

Recommended study split:

- `study1`: data inventory, target construction, baseline probes.
- `study2`: HCP movie pretraining.
- `study3`: emotion downstream fine-tuning.
- `study4`: stimulus-brain-emotion alignment.
- `study5`: brain-tuned affective LLM/VLM adapters, only if screening benchmark results justify it.

## Experiment Hygiene

Every runnable script should record:

- Input paths.
- Output paths.
- Dataset split.
- Model checkpoint or commit hash if available.
- Random seed.
- Main hyperparameters.
- Runtime environment.

Logs should go to `study{N}/logs/`. Tables, plots, and metrics should go to `study{N}/results/`. Intermediate arrays should go to `study{N}/data/`.

## Scientific Hygiene

- Distinguish measured results from planned analyses.
- Cite paper claims in `reference/papers.md`.
- Add newly discovered repositories to `reference/code_resources.md`.
- Add newly discovered datasets to `reference/datasets.md`.
- Keep the canonical project narrative in `Paper/framework_EN.md` and `Paper/framework_KR.md` so context compaction does not scatter the framing.
- Keep NetFeeliX framed as screening-benchmark-driven model development. The benchmark decides between SwiFT adaptation, HCP movie pretraining, TRIBE-SwiFT alignment, and brain-tuned affective LLM/VLM.
- Treat SwiFT as the default brain backbone. TRIBE v2 is a multimodal stimulus-to-brain component, teacher, and alignment path, not a replacement for SwiFT.
- Avoid informal exploratory-benchmark wording in project prose. Use "initial benchmark", "screening benchmark", "feasibility benchmark", or "Stage 0/1".

## Minimal Baseline Order

1. Ridge/elastic-net on parcel or ROI summary features.
2. Dynamic FC arousal/valence baseline.
3. Frozen pretrained BFM linear probe.
4. Small temporal transformer trained from scratch.
5. HCP movie-pretrained temporal transformer.
6. Stimulus feature and stimulus-brain alignment models.
7. Brain-tuned affective LLM/VLM adapter or distillation, only after stimulus-side or alignment benchmarks are promising.

## Avoid

- Starting with expensive 4D volume pretraining before a parcel-level baseline exists.
- Mixing train/test subjects across datasets without documenting it.
- Treating TRIBE as an fMRI encoder. TRIBE is primarily stimulus-to-brain encoding.
- Comparing models without harmonized targets and splits.
- Letting emotion theory dominate the project narrative.
- Creating redundant Markdown files for brief/proposal/narrative content.
