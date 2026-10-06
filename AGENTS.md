# EmoBrain project instructions

_Current working rules · 2026-10-06_

---

## 📍 Authority and scope

Start with [docs/current/00_README.md](docs/current/00_README.md). Current explicit user decisions take precedence over an approved freeze manifest, then the accepted principles in docs/current. Proposals and unresolved entries are not automatically approved. Record changes to an actual preregistration as amendments, not retroactive freezes.

The former root rules, paper_logic_merged, project contracts and September review are historical. Their archived instructions do not govern new work. Reference literature and existing code do not independently define the current protocol.

Read [implementation status](docs/current/08_IMPLEMENTATION_STATUS.md) before execution. A documentation update is not evidence of implementation or successful validation. Inspect the server's actual commit and uncommitted changes before changing it. Preserve other contributors' work.

## 🎯 Rationale before inclusion

Before adding or changing a model, feature, target, loss, control, analysis, statistical test, visualization or interpretation, answer:

1. What scientific question does it answer?
2. What alternative explanation remains without it?
3. Which literature or verified data supports it?
4. Why choose it over plausible alternatives?
5. Which result would change its inclusion or interpretation?
6. What cannot be claimed from it?

Without these answers, do not add it to the primary design. Novelty, popularity, capacity or performance alone is not a rationale. Distinguish architecture, objective, training data and capacity differences from psychological constructs. Evaluate claims neutrally; distinguish verified facts, user reports, proposals and uncertainty. State the evidence that changes a judgment.

## 🔐 Execution boundaries

- Protect canonical stimulus/run boundaries, nested teacher OOF and train-only transforms.
- Do not substitute normative labels for scanned participants' self-reports.
- Do not infer learned content or neural causality from prediction/attention alone.
- No imagery, new LLM backbone or foundation-model construction without a new scope decision.
- GPU jobs are user-run unless explicitly authorized. No full training, test-driven selection, new downloads or raw-data uploads as part of documentation maintenance.
- Do not overwrite server changes, delete original data/results or silently reuse old caches under new protocol names.

## 🏠 Repository hygiene

- Maintain one source of study truth in docs/current with stable filenames.
- Put superseded design material in docs/archive; use Git history for ordinary revisions.
- Do not create dated current-document copies, duplicated all-in-one files, ZIPs, backup files or reports in the repository root.
- Store server audit outputs together under project/output/audits; link evidence rather than duplicating data.
- Keep root README, CLAUDE and CONTEXT as navigation, not competing specifications.
- Keep replies and README prose concise. Omit obvious visual descriptions, editing commentary and repetitive caveats; keep methodological qualifications in the relevant design documents.
- Write newly created or revised README-style contributor documentation in English first, followed by a clearly separated Korean version in the same file. Use matching section order, preserve equivalent technical meaning, and update both languages together; the Korean version must not omit caveats or unresolved status. Do not create separate translation files or rewrite archived originals just for translation.
- This work uses a temporary local checkout; do not create a persistent Mac project checkout or rearrange the user's local research folder.
- Continue documentation, code and experiment-related work on `docs/unify-study-design-20261006`. Keep main unchanged until experiments have been run, major design decisions and results have been reviewed, and the user explicitly approves a merge. Do not create a PR without authorization.
