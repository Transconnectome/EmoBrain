# EmoBrain implementation

_Code navigation and migration boundary · 2026-10-06_

---

## 📍 Current specification

Use [the study index](../docs/current/00_README.md),
[implementation specification](../docs/current/02_IMPLEMENTATION_SPEC.md) and
[implementation status](../docs/current/08_IMPLEMENTATION_STATUS.md).
The former project contract is preserved in the [archive](../docs/archive/pre-handoff-2026-10-06/project/README.md).

## ⚠️ Existing code is not the current pipeline

| Path | Existing role | Current-design status |
| --- | --- | --- |
| `code/decoder/` | Emotion-label-query decoder | Historical implementation / possible baseline, not brain-query teacher |
| `code/fusion/`, `code/training/`, `code/configs/` | Qwen-era teacher/cache/student | Legacy; not nested OOF |
| `data/` | Horikawa ROI-mean, 34-D normalization, captions | Needs current cohort / voxel / target / manifest adapters |
| `scripts/` | Prior training, gates and QC | Audit before reuse; old launch commands are not endorsed |
| `evaluation/` | Profile metrics and ISC | Reuse only after target, scale and estimand checks |
| `tests/` | Earlier core tests | Current split / OOF / content-access tests still required |
| `shared/`, `output/`, `legacy/` | Existing assets, experiments and records | Preserve; do not silently relabel as current results |

No source code, feature cache, checkpoint or experiment result is migrated by this documentation change.
Do not launch the old training script merely because documentation now points at the new specification.

## 🔐 Before implementation

1. Inventory the server commit, local modifications, data manifests and prior test exposure.
2. Resolve canonical IDs and run/content grouping before fitting transforms or teachers.
3. Implement scoped data contracts and leakage tests before full experiments.
4. Preserve old baselines with their original preprocessing, split and target provenance.
5. Keep run outputs outside maintained design documents; create no backup copies in the repository root.
