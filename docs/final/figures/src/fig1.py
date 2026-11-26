import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from style import *
from fig5 import feat, lock
import numpy as np

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SEL = [(3, 7), (8, 2), (9, 4), (9, 9)]


def tag(ax, x, y, s, c):
    t = txt(ax, x, y, s, size=5.0, c='white', w='bold', ha='left')
    t.set_bbox(dict(boxstyle='round,pad=0.25,rounding_size=0.6', fc=c, ec='none'))


def fig1():
    W, H = 180, 104
    fig, ax = canvas(W, H)
    txt(ax, 3, H - 3.0, 'Selected attention heads link stimulus information, regional brain responses and brain-only decoding',
        size=7.2, w='bold', ha='left')

    # ---------------- preparation row: 1 and 2 ----------------
    yp = H - 17
    box(ax, 3, yp - 7.5, 64, 15, fc=MODEL_F, ec=MODEL, lw=0.6)
    num(ax, 7, yp + 4.0, 1, c=MODEL)
    txt(ax, 10.5, yp + 4.0, 'Emotion lens (VCE)', size=6.4, c=MODEL, w='bold', ha='left')
    # two checkpoints
    for i, (lab, sub) in enumerate((('video-only', 'masked video SSL'), ('+ emotion', 'fine-tuned on 27 ratings'))):
        x0 = 7 + i * 30
        for b in range(6):
            rect(ax, x0 + b * 1.6, yp - 5.2, 1.2, 6.2, fc='white' if i == 0 else '#C9D6E4', ec=MODEL, lw=0.4)
        txt(ax, x0 + 10.5, yp - 0.8, lab, size=5.8, c=MODEL, w='bold', ha='left')
        txt(ax, x0 + 10.5, yp - 3.8, sub, size=5.0, c=GREY, ha='left')
    arrow(ax, 27.5, yp - 2.1, 36, yp - 2.1, c=MODEL, lw=0.6, ms=4)

    arrow(ax, 67.5, yp, 73.5, yp, lw=0.7)
    box(ax, 74, yp - 7.5, 66, 15, fc=HEAD_F, ec=HEAD, lw=0.6)
    num(ax, 78, yp + 4.0, 2, c=HEAD)
    txt(ax, 81.5, yp + 4.0, 'Head selection (VCE validation videos)', size=6.4, c=HEAD, w='bold', ha='left')
    head_grid(ax, 78, yp - 6.3, cell=0.72, gap=0.16, selected=SEL, lw=0.2)
    txt(ax, 90, yp - 0.6, 'ablate random halves of the 144 heads;', size=5.2, ha='left')
    txt(ax, 90, yp - 3.4, 'fix one list of K heads per emotion', size=5.2, ha='left')
    txt(ax, 90, yp - 6.0, '(selectivity tested on VCE test videos)', size=4.8, c=GREY, ha='left')

    # legend (colour roles)
    lx = 144
    for i, (c, s) in enumerate(((HEAD, 'selected head output'), (RATE, 'human emotion ratings'),
                                (BRAIN, 'fMRI'), (POOL, 'last-layer 768-d feature'))):
        rect(ax, lx, yp + 4.4 - i * 3.5, 2.4, 2.0, fc=c, ec='none')
        txt(ax, lx + 3.4, yp + 5.4 - i * 3.5, s, size=5.0, ha='left')

    # ---------------- three columns ----------------
    top = yp - 17
    cols = [(3, 56), (61, 58), (123, 54)]
    heads = [(3, 'What explains the selected heads?', 'representative', HEAD),
             (4, 'Which regions do heads and ratings explain?', 'representative', HEAD),
             (6, 'Can fMRI alone recover the heads?', 'reverse test', MODEL)]
    for (x0, w), (n, title, t, tc) in zip(cols, heads):
        box(ax, x0, 21, w, top - 21, fc='white', ec='#CFCFCF', lw=0.5)
        num(ax, x0 + 4, top - 4.0, n)
        txt(ax, x0 + 7.5, top - 4.0, title, size=6.2, w='bold', ha='left')
        tag(ax, x0 + 7.5, top - 8.6, t, tc)

    # col 3: L/O/S -> two targets
    x0 = 3
    yy = top - 15
    frames(ax, x0 + 3, yy - 5, w=9, h=6.5)
    txt(ax, x0 + 7.5, yy - 7.8, 'Cowen videos\n+ 20 captions', size=4.9, c=GREY, va='top', linespacing=1.15)
    for i, (k, c, d) in enumerate((('L', C_L, 'luminance, colour, motion'), ('O', C_O, 'object nouns'), ('S', C_S, 'full caption'))):
        y = yy + 1.5 - i * 4.2
        ax.add_patch(Circle((x0 + 18.5, y), 1.4, fc=c, ec='none', zorder=6))
        txt(ax, x0 + 18.5, y - 0.05, k, size=5.4, c='white', w='bold', z=7)
        txt(ax, x0 + 21, y, d, size=5.0, ha='left')
    txt(ax, x0 + 18, yy - 12.6, '7 combinations, banded ridge, held-out videos', size=5.0, c=GREY, ha='left')
    # two targets with unique/shared bars
    ty = 28.5
    for j, (lab, c, vals) in enumerate((('human fear rating', RATE, (0.04, 0.02, 0.10, 0.14)),
                                        ('fear-head output', HEAD, (0.08, 0.04, 0.05, 0.11)))):
        y = ty + 5.2 - j * 5.0
        txt(ax, x0 + 3, y, lab, size=5.2, c=c, ha='left', w='bold')
        xx = x0 + 25
        for v, cc in zip(vals, (C_L, C_O, C_S, SHARED)):
            rect(ax, xx, y - 1.3, v * 95, 2.6, fc=cc, ec='white', lw=0.3, z=4)
            xx += v * 95
    txt(ax, x0 + 25, ty - 3.6, 'unique L, O, S | shared', size=4.8, c=GREY, ha='left')

    # col 4: H, E -> brain -> partition
    x0 = 61
    yy = top - 16
    rect(ax, x0 + 4, yy - 2.5, 7, 6, fc=HEAD_F, ec=HEAD, lw=0.6)
    txt(ax, x0 + 7.5, yy + 0.5, 'H', size=6, c=HEAD, w='bold')
    rect(ax, x0 + 4, yy - 10.5, 4, 6, fc=RATE_F, ec=RATE, lw=0.6)
    txt(ax, x0 + 6, yy - 7.5, 'E', size=6, c=RATE, w='bold')
    txt(ax, x0 + 13, yy + 0.5, 'head output', size=4.9, c=HEAD, ha='left')
    txt(ax, x0 + 13, yy - 7.5, '27 ratings', size=4.9, c=RATE, ha='left')
    arrow(ax, x0 + 27, yy - 3.5, x0 + 32, yy - 3.5, lw=0.6)
    brain(ax, x0 + 32.5, yy - 7.8, w=11, h=8)
    txt(ax, x0 + 38, yy - 10.2, 'voxels of one ROI,\none HK participant', size=4.8, c=BRAIN, va='top', linespacing=1.15)
    vx, vy = x0 + 50, yy - 3.5
    ax.add_patch(Circle((vx - 2.2, vy), 4.0, fc=HEAD, alpha=0.25, ec=HEAD, lw=0.6, zorder=4))
    ax.add_patch(Circle((vx + 2.2, vy), 4.0, fc=RATE, alpha=0.25, ec=RATE, lw=0.6, zorder=4))
    txt(ax, vx, vy - 6.2, 'H, E, H+E', size=4.8, c=GREY)
    # analysis 5 box
    box(ax, x0 + 3, 24, 52, 10.5, fc='#FFFBF6', ec=HEAD, lw=0.5)
    num(ax, x0 + 7, 29.25, 5, c=HEAD, r=1.8, size=5.8)
    txt(ax, x0 + 10.5, 31.4, 'Ablate the same heads: extra drop in', size=5.2, ha='left')
    txt(ax, x0 + 10.5, 27.8, 'RSA and encoding vs matched random heads', size=5.2, ha='left')
    txt(ax, x0 + 10.5, 25.9, 'last-layer 768-d feature', size=4.6, c=POOL, ha='left', va='top')

    # col 6: fMRI -> ridge -> features -> readout -> 27
    x0 = 123
    yy = top - 17
    brain(ax, x0 + 3, yy - 4, w=10, h=7)
    arrow(ax, x0 + 13.6, yy - 0.5, x0 + 17, yy - 0.5, lw=0.6, ms=4)
    box(ax, x0 + 17.3, yy - 3.3, 9, 5.6, fc=BRAIN_F, ec=BRAIN)
    txt(ax, x0 + 21.8, yy - 0.5, 'ridge', size=5.2, c=BRAIN)
    arrow(ax, x0 + 26.6, yy - 0.5, x0 + 30, yy - 0.5, lw=0.6, ms=4)
    feat(ax, x0 + 30.5, yy - 3.8, w=6, h=6.6, dashed=True)
    arrow(ax, x0 + 37.5, yy - 0.5, x0 + 40.5, yy - 0.5, lw=0.6, ms=4)
    box(ax, x0 + 40.8, yy - 3.3, 10.5, 5.6, fc=RATE_F, ec=RATE)
    txt(ax, x0 + 46, yy - 0.5, 'readout', size=5.0, c=RATE)
    lock(ax, x0 + 50.8, yy + 3.0, RATE)
    txt(ax, x0 + 3, yy - 9.0, 'per-participant ridge recovers the head output;\nthe VCE-fitted readout is frozen', size=5.0, ha='left', va='top', linespacing=1.25)
    rng = np.random.default_rng(5)
    for i in range(27):
        v = 0.15 + 0.8 * rng.random()
        rect(ax, x0 + 4 + i * 0.75, 32.5, 0.55, 6 * v, fc=RATE if i == 10 else '#BDB3D9', ec='none', z=4)
    txt(ax, x0 + 26, 30.7, '27 predicted ratings vs Cowen ratings', size=4.9, c=RATE, va='top')
    txt(ax, x0 + 3, 27.2, 'direct ridge fMRI → ratings as a reference;\nHK cross-validation, then 72 MC test videos', size=4.8, c=GREY, ha='left', va='top', linespacing=1.25)

    # ---------------- the thread ----------------
    yt = top + 4.2
    line(ax, [12, 176], [yt, yt], c=HEAD, lw=1.6)
    arrow(ax, 107, yp - 7.5, 107, yt + 0.2, c=HEAD, lw=1.0, ms=5)
    for x in (12, 64, 126, 176):
        pass
    for x in (30, 92, 150):
        arrow(ax, x, yt, x, top + 0.3, c=HEAD, lw=0.9, ms=4.5)
    txt(ax, 12, yt + 1.6, 'fixed head lists: the same head outputs per video (videos × 64K)', size=5.3, c=HEAD, ha='left', va='bottom', w='bold')
    txt(ax, 3, 17.6, 'The head outputs are the target in analysis 3, the encoding input in 4, the ablated units in 5 and the reconstruction target in 6. '
                     'Explained-variance values from 3 are never fed into 4 or 6.', size=5.0, c=GREY, ha='left', va='top')

    # ---------------- data strip ----------------
    ds = [('VCE', '61,046 silent videos, 27 ratings (50k train, 11k test)', MODEL),
          ('Cowen', '2,185 videos; rater proportions; 20 captions per video', RATE),
          ('HK fMRI', '5 participants, 2,181 videos, 370 ROIs, single viewing', BRAIN),
          ('MC fMRI', '6 participants; 72 test videos × 5 repeats', BRAIN)]
    for i, (k, d, c) in enumerate(ds):
        x = 3 + i * 44.3
        box(ax, x, 2.5, 42.5, 8.5, fc='white', ec=c, lw=0.5)
        txt(ax, x + 2, 8.7, k, size=5.6, c=c, w='bold', ha='left')
        txt(ax, x + 2, 5.1, d, size=4.6, ha='left')
    save(fig, 'emobrain_ridge_overview', OUT)
    return fig


if __name__ == '__main__':
    fig1()
