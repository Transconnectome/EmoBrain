#!/usr/bin/env python3
"""Check that reference/datasets.md keeps complete dataset entries.

This is intentionally lightweight: the dataset inventory is still readable
Markdown, but this script catches entries that are missing the sections needed
for planning experiments.
"""

import re
import sys
from pathlib import Path
from typing import Dict


REQUIRED_BLOCKS = (
    "**Role in NetFeeliX**",
    "**Dataset content**",
    "**NetFeeliX task design**",
    "**SwiFT use**",
    "**TRIBE v2 / stimulus use**",
    "**Risks**",
)

SOURCE_BLOCKS = ("**Source**", "**Sources**")

def dataset_sections(markdown):
    pattern = re.compile(r"^### (.+)$", re.MULTILINE)
    matches = list(pattern.finditer(markdown))
    sections = {}  # type: Dict[str, str]

    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        body = markdown[start:end]
        sections[title] = body

    return sections


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    path = repo_root / "reference" / "datasets.md"
    markdown = path.read_text(encoding="utf-8")
    sections = dataset_sections(markdown)

    failures = []
    for title, body in sections.items():
        for block in REQUIRED_BLOCKS:
            if block not in body:
                failures.append(f"{title}: missing {block}")

        if not any(block in body for block in SOURCE_BLOCKS):
            failures.append(f"{title}: missing source block")

    if failures:
        print("Dataset inventory is incomplete:\n")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"OK: {len(sections)} dataset entries contain required planning fields.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
