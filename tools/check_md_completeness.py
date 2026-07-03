#!/usr/bin/env python3
"""Project-level checks for EmoBrain Markdown operations."""

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "README_KR.md",
    "ACTION_PLAN.md",
    "ONBOARDING.md",
    "CONTEXT_EMOBRAIN.md",
    "CLAUDE.md",
    "CODEX.md",
    "Paper/framework_EN.md",
    "Paper/framework_KR.md",
    "Paper/methodology.md",
    "docs/reference/datasets.md",
    "docs/reference/task.md",
    "docs/reference/training_strategy.md",
    "docs/reference/systematic_reference_map.md",
    "docs/workflows/README.md",
    "docs/workflows/literature_sota_workflow.md",
    "docs/workflows/experiment_planning_workflow.md",
    "docs/workflows/red_blue_team_review.md",
    "docs/workflows/weekly_update_workflow.md",
    "docs/templates/paper_note.md",
    "docs/templates/dataset_card.md",
    "docs/templates/experiment_card.md",
    "docs/templates/model_card.md",
    "docs/templates/review_card.md",
    "docs/templates/decision_log.md",
]

DATASET_REQUIRED_BLOCKS = [
    ("**Role in EmoBrain**", "**Role**"),
    ("**Dataset content**", "**Dataset content"),
    ("**Risks**",),
]

OLD_REFERENCES = [
    "docs/reference/literature_map.md",
    "docs/reference/emotion_foundation_model_landscape.md",
    "docs/notes/" + "pi" + "lot_benchmark_design.md",
    "NARRATIVE_KR.md",
    "scripts/audit_emode_design.py",
    "scripts/audit_emode_extraction.py",
    "scripts/run_emode_clean_linear.py",
    "scripts/run_tribe_horikawa.py",
    "scripts/build_horikawa_window_manifest.py",
]

GENERATED_MARKDOWN = {
    "docs/reports/status/PROJECT_STATUS.md",
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
    path = ROOT / "docs" / "reference" / "datasets.md"
    if not path.exists():
        failures.append("missing docs/reference/datasets.md")
        return
    sections = dataset_sections(path.read_text(encoding="utf-8"))
    for title, body in sections.items():
        for block_variants in DATASET_REQUIRED_BLOCKS:
            if not any(v in body for v in block_variants):
                failures.append("dataset %s missing %s" % (title, block_variants[0]))
        if "**Source**" not in body and "**Sources**" not in body:
            failures.append("dataset %s missing source block" % title)


def check_trigger_visibility(failures):
    context = read("CONTEXT_EMOBRAIN.md")
    workflow = read("docs/workflows/README.md")
    for trigger in ["[deep search]", "[experiment card]", "[red team]", "[weekly status]", "[verification]"]:
        if trigger not in context or trigger not in workflow:
            failures.append("trigger not visible in context/workflows: %s" % trigger)


def check_agent_memory_links(failures):
    for rel in ["CLAUDE.md", "CODEX.md"]:
        text = read(rel)
        if "CONTEXT_EMOBRAIN.md" not in text:
            failures.append("%s must point to CONTEXT_EMOBRAIN.md" % rel)


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
        print("EmoBrain project checks failed:\n")
        for failure in failures:
            print("- " + failure)
        return 1

    print("OK: EmoBrain project docs and workflow scaffolding are complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
