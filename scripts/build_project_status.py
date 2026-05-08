#!/usr/bin/env python3
"""Build a compact NetFeeliX project status report."""

import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "status" / "PROJECT_STATUS.md"


def run_git(args):
    try:
        return subprocess.check_output(
            ["git"] + args,
            cwd=str(ROOT),
            universal_newlines=True,
        ).strip()
    except subprocess.CalledProcessError:
        return ""


def count_dataset_entries():
    text = (ROOT / "reference" / "datasets.md").read_text(encoding="utf-8")
    return sum(1 for line in text.splitlines() if line.startswith("### "))


def count_reference_rows(path):
    if not (ROOT / path).exists():
        return 0
    text = (ROOT / path).read_text(encoding="utf-8")
    rows = len([line for line in text.splitlines() if line.startswith("|")])
    return max(0, rows - 2)


def main():
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    branch = run_git(["branch", "--show-current"]) or "unknown"
    last_commit = run_git(["log", "--oneline", "-1"]) or "none"
    status = run_git(["status", "--short"])
    recent = run_git(["log", "--oneline", "--max-count", "5"])

    dataset_count = count_dataset_entries()
    paper_rows = count_reference_rows("reference/papers.md")
    model_rows = count_reference_rows("reference/code_resources.md")

    dirty = status if status else "clean"

    body = """# NetFeeliX Project Status

Generated: {now}

## Git

- Branch: `{branch}`
- Last commit: `{last_commit}`
- Working tree: `{dirty}`

## Canonical Direction

- SwiFT is the default brain backbone.
- TRIBE v2 is a stimulus-to-brain teacher/baseline/alignment component.
- HCP 7T movie is the main naturalistic fMRI continued-pretraining source.
- Horikawa and Emo-FilM are the primary downstream emotion datasets.

## Inventory Counts

- Dataset entries in `reference/datasets.md`: {dataset_count}
- Approximate paper table rows in `reference/papers.md`: {paper_rows}
- Approximate code-resource table rows in `reference/code_resources.md`: {model_rows}

## Recent Commits

```text
{recent}
```

## Next Operating Checks

```bash
python3 scripts/check_md_completeness.py
python3 scripts/build_project_status.py
```
""".format(
        now=now,
        branch=branch,
        last_commit=last_commit,
        dirty=dirty,
        dataset_count=dataset_count,
        paper_rows=paper_rows,
        model_rows=model_rows,
        recent=recent,
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(body, encoding="utf-8")
    print("Wrote %s" % OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
