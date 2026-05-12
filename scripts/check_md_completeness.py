#!/usr/bin/env python3
"""Project-level checks for FEELIN Markdown operations."""

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "README_KR.md",
    "ACTION_PLAN.md",
    "ONBOARDING.md",
    "CONTEXT_FEELIN.md",
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
    "setup/README.md",
    "templates/paper_note.md",
    "templates/dataset_card.md",
    "templates/experiment_card.md",
    "templates/model_card.md",
    "templates/review_card.md",
    "templates/decision_log.md",
]

DATASET_REQUIRED_BLOCKS = [
    "**Role in FEELIN**",
    "**Dataset content**",
    "**FEELIN task design**",
    "**SwiFT use**",
    "**TRIBE v2 / stimulus use**",
    "**Risks**",
]

OLD_REFERENCES = [
    "reference/literature_map.md",
    "reference/emotion_foundation_model_landscape.md",
    "notes/" + "pi" + "lot_benchmark_design.md",
    "NARRATIVE_KR.md",
    "scripts/audit_emode_design.py",
    "scripts/audit_emode_extraction.py",
    "scripts/run_emode_clean_linear.py",
    "scripts/run_tribe_horikawa.py",
    "scripts/build_horikawa_window_manifest.py",
]

GENERATED_MARKDOWN = {
    "reports/status/PROJECT_STATUS.md",
}


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
        rel = str(path.relative_to(ROOT))
        if rel in GENERATED_MARKDOWN:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
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
    context = read("CONTEXT_FEELIN.md")
    workflow = read("workflows/README.md")
    for trigger in ["[deep search]", "[experiment card]", "[red team]", "[weekly status]", "[verification]"]:
        if trigger not in context or trigger not in workflow:
            failures.append("trigger not visible in context/workflows: %s" % trigger)


def check_agent_memory_links(failures):
    for rel in ["CLAUDE.md", "CODEX.md"]:
        text = read(rel)
        if "CONTEXT_FEELIN.md" not in text:
            failures.append("%s must point to CONTEXT_FEELIN.md" % rel)


def check_no_redundant_root_docs(failures):
    forbidden = [
        "project_brief",
        "proposal_outline",
        "narrative",
    ]
    for path in ROOT.glob("*.md"):
        name = path.name.lower()
        if path.name in {"README.md", "README_KR.md"}:
            continue
        for token in forbidden:
            if token in name:
                failures.append("avoid redundant root markdown file: %s" % path.name)


def main():
    failures = []
    check_required_files(failures)
    check_old_references(failures)
    check_dataset_inventory(failures)
    check_trigger_visibility(failures)
    check_agent_memory_links(failures)
    check_no_redundant_root_docs(failures)

    if failures:
        print("FEELIN project checks failed:\n")
        for failure in failures:
            print("- " + failure)
        return 1

    print("OK: FEELIN project docs and workflow scaffolding are complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
