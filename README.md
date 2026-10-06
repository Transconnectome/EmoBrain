# EmoBrain

_Brain–content relations and normative affect readout · current design imported 2026-10-06_

---

## 📍 Start here

The single maintained study specification is [docs/current/00_README.md](docs/current/00_README.md).
It supersedes the former H1–H4 argument and earlier server handoff copies as the working design.
Approved principles, proposals and unresolved decisions remain distinct; importing documents does not freeze a protocol.

For contributors and AI agents, read [AGENTS.md](AGENTS.md), then the current specification.
[Implementation status](docs/current/08_IMPLEMENTATION_STATUS.md) records the gap between that design and this repository's code.

## 🎯 Research question

How are neural responses to emotionally evocative scenes related to their sensory–semantic content,
and how are these brain–content relations learned and used for high-dimensional normative affect readout?

This is a neuroscience study of learned content and model use, not an emotion-decoding leaderboard.
Normative affect annotations are not the scanned participants' self-reports.

| Analysis | Question |
| --- | --- |
| 1a / 1b | Do content and affect annotations explain held-out brain responses, and where do their predictions overlap? |
| 2a–c / 2d | What brain–content relations are learned and used, and are content-related representations supported by independent brain measurements? |
| 3 | Can independent affect targets be read out, and do the effects replicate across participant cohorts? |

Teacher training uses brain + video + descriptive captions. The student receives brain only during training and inference, with nested out-of-fold teacher **output guidance** during training.
Content probes, CKA and selective perturbations are evaluations, not student content-reconstruction losses.
See the [story](docs/current/01_STORY_AND_DESIGN.md) for rationale and interpretation limits.

## ⚠️ Implementation state

The October design is **not yet implemented end to end** in the inherited code.
The existing label-query decoder, log1p-z/MSE training and single-teacher cache are earlier implementations,
not a runnable reference for the current protocol. No full training command is endorsed by this documentation update.

First reconcile the server's actual code and data with the [implementation specification](docs/current/02_IMPLEMENTATION_SPEC.md).
Use the [server prompt](docs/current/SERVER_PROMPT.md) and [action items](docs/current/03_ACTION_ITEMS.md).
Training, preprocessing changes, test-set selection and publication of results are separate actions.

## 📚 Repository layout

```text
docs/current/    maintained study design, decisions, actions and implementation status
docs/archive/    superseded research plans and historical review records
docs/reference/ literature and dataset evidence; not an alternative protocol
project/        existing code and outputs; migration status is explicit
tools/          existing repository utilities
archive/        pre-existing historical results and literature corpus
external/       pre-existing external references
```

Keep current filenames stable and use Git history instead of new dated copies, ZIPs or all-in-one duplicates.
Do not reorganize raw data, results or external repositories as part of documentation maintenance.
Earlier top-level entry points are retained only as short navigation files.

## 🔄 Branch workflow

The active working branch is `docs/unify-study-design-20261006`, based on main commit
`a5285044ce417945685e0eb044ac77f68d487af0`.
This branch does not make old results evidence for the new design.
Continue documentation, code and experiment-related work on this branch. Keep main unchanged until experiments have been run, major design decisions and results have been reviewed, and the user explicitly approves a merge. Do not overwrite server work or run jobs merely on checkout.
