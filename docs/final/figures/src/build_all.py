"""Draw the eight design figures and assemble the two multipage PDFs."""

import argparse
import os
from pathlib import Path
import subprocess
import sys

import pymupdf

from embed_html import embed

SOURCE = Path(__file__).resolve().parent
MODULES = (
    'overview_partition.py', 'architecture_alignment_decoding.py',
    'head_layers_captions.py', 'word_example.py',
)
METHODS = (
    ('그림 2. VideoMAE', 'videomae_methods'),
    ('그림 3a. head와 층', 'head_layers'),
    ('그림 3b. 자극 정보', 'head_captions'),
    ('그림 4a. 영역별 분할', 'roi_partition'),
    ('그림 4b. RSA와 encoding', 'regional_alignment'),
    ('그림 5. 뇌 단독 디코딩', 'brain_decoding'),
    ('부록 그림 3c. 단어 예시', 'chase_head_roi'),
)


def bundle(out, name, pages):
    with pymupdf.open() as pdf:
        toc = []
        for title, stem in pages:
            with pymupdf.open(out / f'emobrain_{stem}.pdf') as page:
                toc.append([1, title, len(pdf) + 1])
                pdf.insert_pdf(page)
        pdf.set_toc(toc)
        pdf.save(out / f'emobrain_{name}.pdf', garbage=4, deflate=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=SOURCE.parent)
    out = parser.parse_args().out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, EMOBRAIN_FIGURE_OUT=str(out))
    for module in MODULES:
        subprocess.run([sys.executable, str(SOURCE / module)], check=True, env=env)
    bundle(out, 'head_interpretation', METHODS[1:3])
    bundle(out, 'methods_figures', METHODS)
    if out == SOURCE.parent:
        embed(out.parent / '07_research_design.html', out)


if __name__ == '__main__':
    main()
