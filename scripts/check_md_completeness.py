#!/usr/bin/env python3
"""Project-level checks for NetFeeliX Markdown operations."""

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "README_KR.md",
    "ACTION_PLAN.md",
    "ONBOARDING.md",
    "CONTEXT_NETFEELIX.md",
    "CLAUDE.md",
    "CODEX.md",
    "Paper/framework_EN.md",
    "Paper/framework_KR.md",
    "Paper/methodology.md",
    "reference/datasets.md",
    "reference/task.md",
    "reference/training_strategy.md",
    "reference/systematic_reference_map.md",
    "workflows/README.md",
    "workflows/literature_sota_workflow.md",
    "workflows/experiment_planning_workflow.md",
    "workflows/red_blue_team_review.md",
    "workflows/weekly_update_workflow.md",
    "study1/README.md",
    "templates/paper_note.md",
    "templates/dataset_card.md",
    "templates/experiment_card.md",
    "templates/model_card.md",
    "templates/review_card.md",
    "templates/decision_log.md",
]

DATASET_REQUIRED_BLOCKS = [
    "**Role in NetFeeliX**",
    "**Dataset content**",
    "**NetFeeliX task design**",
    "**SwiFT use**",
    "**TRIBE v2 / stimulus use**",
    "**Risks**",
]

OLD_REFERENCES = [
    "reference/literature_map.md",
    "reference/emotion_foundation_model_landscape.md",
    "notes/pilot_benchmark_design.md",
]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def markdown_files():
    ignored = {".git"}
    for path in ROOT.rglob("*.md"):
        if any(part in ignored for part in path.parts):
            continue
        yield path


def check_required_files(failures):
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).exists():
            failures.append("missing required file: %s" % rel)


def check_old_references(failures):
    for path in markdown_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = str(path.relative_to(ROOT))
        for old in OLD_REFERENCES:
            if old in text:
                failures.append("%s references old path %s" % (rel, old))


def dataset_sections(text):
    matches = list(re.finditer(r"^### (.+)$", text, flags=re.MULTILINE))
    sections = {}
    for idx, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        sections[title] = text[start:end]
    return sections


def check_dataset_inventory(failures):
    path = ROOT / "reference" / "datasets.md"
    if not path.exists():
        failures.append("missing reference/datasets.md")
        return
    sections = dataset_sections(path.read_text(encoding="utf-8"))
    for title, body in sections.items():
        for block in DATASET_REQUIRED_BLOCKS:
            if block not in body:
                failures.append("dataset %s missing %s" % (title, block))
        if "**Source**" not in body and "**Sources**" not in body:
            failures.append("dataset %s missing source block" % title)


def check_trigger_visibility(failures):
    context = read("CONTEXT_NETFEELIX.md")
    workflow = read("workflows/README.md")
    for trigger in ["[deep search]", "[experiment card]", "[red team]", "[weekly status]", "[verification]"]:
        if trigger not in context or trigger not in workflow:
            failures.append("trigger not visible in context/workflows: %s" % trigger)


def main():
    failures = []
    check_required_files(failures)
    check_old_references(failures)
    check_dataset_inventory(failures)
    check_trigger_visibility(failures)

    if failures:
        print("NetFeeliX project checks failed:\n")
        for failure in failures:
            print("- " + failure)
        return 1

    print("OK: NetFeeliX project docs and workflow scaffolding are complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
