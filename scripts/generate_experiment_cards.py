#!/usr/bin/env python3
"""Generate an experiment-card Markdown file from the template."""

import argparse
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "experiment_card.md"
OUT_DIR = ROOT / "reports" / "status"


def slugify(text):
    chars = []
    for ch in text.lower():
        if ch.isalnum():
            chars.append(ch)
        elif ch in {" ", "-", "_"}:
            chars.append("_")
    slug = "".join(chars).strip("_")
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug or "experiment"


def main():
    parser = argparse.ArgumentParser(description="Create a FEELIN experiment card.")
    parser.add_argument("--id", required=True, help="Experiment ID, e.g. NFx-001")
    parser.add_argument("--title", required=True, help="Experiment title")
    parser.add_argument("--owner", default="sjmoon", help="Owner name")
    parser.add_argument("--out-dir", default=str(OUT_DIR), help="Output directory")
    args = parser.parse_args()

    template = TEMPLATE.read_text(encoding="utf-8")
    today = datetime.utcnow().strftime("%Y-%m-%d")
    text = template
    text = text.replace("- Experiment ID:", "- Experiment ID: %s" % args.id)
    text = text.replace("- Title:", "- Title: %s" % args.title)
    text = text.replace("- Owner:", "- Owner: %s" % args.owner)
    text = text.replace("- Created:", "- Created: %s" % today)

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / ("%s_%s.md" % (args.id, slugify(args.title)))
    if out_path.exists():
        raise SystemExit("Refusing to overwrite existing file: %s" % out_path)
    out_path.write_text(text, encoding="utf-8")
    try:
        display = out_path.relative_to(ROOT)
    except ValueError:
        display = out_path
    print("Wrote %s" % display)


if __name__ == "__main__":
    main()
