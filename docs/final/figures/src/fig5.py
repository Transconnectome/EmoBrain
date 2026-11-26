import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from style import *
from fig4 import matrix
import numpy as np

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def lock(ax, x, y, c=INK):
    rect(ax, x - 1.1, y - 1.0, 2.2, 1.6, fc=c, ec=c, z=8)
    from matplotlib.patches import Arc
    ax.add_patch(Arc((x, y + 0.6), 1.5, 1.8, theta1=0, theta2=180, color=c, lw=0.6, zorder=8))


def feat(ax, x, y, w=8, h=9, dashed=False, k=3):
    for j in range(k):
        rect(ax, x + j * (w / k), y, w / k - 0.4, h, fc=HEAD_F, ec=HEAD, lw=0.6, z=4)
    if dashed:
        rect(ax, x - 0.8, y - 0.8, w + 1.2, h + 1.6, fc='none', ec=HEAD, lw=0.5, z=5).set_linestyle((0, (2, 1.2)))


def fig5():
    W, H = 180, 92
    fig, ax = canvas(W, H)

    # ---- a: two mappings fitted separately ----
    panel(ax, 1.5, H - 1.5, 'a')
    txt(ax, 6, H - 3.2, 'Two mappings are fitted separately, then frozen', size=7, w='bold', ha='left')
    # lane 1: model side (VCE)
    y1 = H - 15
    txt(ax, 6, y1 + 6.5, 'VCE training videos (no brain data)', size=5.8, c=MODEL, w='bold', ha='left')
    frames(ax, 6, y1 - 4, w=10, h=7)
    arrow(ax, 19, y1, 25, y1, lw=0.6)
    feat(ax, 25.5, y1 - 4.5)
    txt(ax, 29.5, y1 - 6.8, 'true head output\n(64 × K)', size=5.0, c=HEAD, va='top')
    arrow(ax, 35, y1, 42, y1, lw=0.6)
    box(ax, 42.5, y1 - 4, 18, 8, fc=RATE_F, ec=RATE)
    txt(ax, 51.5, y1 + 1.2, 'linear readout', size=5.6, c=RATE, w='bold')
    txt(ax, 51.5, y1 - 1.8, 'one per emotion', size=5.0, c=RATE)
    lock(ax, 60.5, y1 - 5.2, RATE)
    arrow(ax, 61, y1, 67, y1, lw=0.6)
    txt(ax, 68, y1 + 0.9, 'VCE rating', size=5.6, c=RATE, ha='left')
    txt(ax, 68, y1 - 2.0, 'of emotion e', size=5.0, c=GREY, ha='left')
    txt(ax, 6, y1 - 13.4, 'penalty chosen on VCE validation videos; scaling and weights frozen',
        size=5.0, c=GREY, ha='left')

    # lane 2: brain side (HK outer-training)
    y2 = H - 44
    txt(ax, 6, y2 + 6.5, 'HK outer-training videos, one participant', size=5.8, c=BRAIN, w='bold', ha='left')
    brain(ax, 6, y2 - 4.2, w=11.5, h=8)
    arrow(ax, 19, y2, 25, y2, lw=0.6)
    box(ax, 25.5, y2 - 4, 16, 8, fc=BRAIN_F, ec=BRAIN)
    txt(ax, 33.5, y2 + 1.2, 'ridge', size=5.6, c=BRAIN, w='bold')
    txt(ax, 33.5, y2 - 1.8, 'per participant', size=5.0, c=BRAIN)
    lock(ax, 41.5, y2 - 5.2, BRAIN)
    arrow(ax, 42, y2, 48, y2, lw=0.6)
    feat(ax, 48.5, y2 - 4.5)
    txt(ax, 52.5, y2 - 6.8, 'target: true head output\nof the same videos', size=5.0, c=HEAD, va='top')
    txt(ax, 6, y2 - 13.4, 'no ratings used; penalty chosen on inner folds by feature reconstruction',
        size=5.0, c=GREY, ha='left')

    # ---- b: brain-only test ----
    bx = 82
    panel(ax, bx - 2.5, H - 1.5, 'b')
    txt(ax, bx + 2, H - 3.2, 'Brain-only test on held-out videos', size=7, w='bold', ha='left')
    yb = H - 22
    brain(ax, bx + 2, yb - 4.2, w=11.5, h=8)
    txt(ax, bx + 7.75, yb - 6.6, 'fMRI only', size=5.2, c=BRAIN, va='top')
    arrow(ax, bx + 14.5, yb, bx + 19.5, yb, lw=0.7)
    box(ax, bx + 20, yb - 3.5, 11, 7, fc=BRAIN_F, ec=BRAIN)
    txt(ax, bx + 25.5, yb, 'ridge', size=5.6, c=BRAIN)
    lock(ax, bx + 31, yb + 4.1, BRAIN)
    arrow(ax, bx + 31.5, yb, bx + 36.5, yb, lw=0.7)
    feat(ax, bx + 37.5, yb - 4.5, dashed=True)
    txt(ax, bx + 41.5, yb - 7.4, 'reconstructed\nhead output', size=5.0, c=HEAD, va='top')
    arrow(ax, bx + 47, yb, bx + 52, yb, lw=0.7)
    box(ax, bx + 52.5, yb - 3.5, 13, 7, fc=RATE_F, ec=RATE)
    txt(ax, bx + 59, yb, 'readout', size=5.6, c=RATE)
    lock(ax, bx + 65.5, yb + 4.1, RATE)
    arrow(ax, bx + 66, yb, bx + 71, yb, lw=0.7)
    # 27 predictions
    rng = np.random.default_rng(5)
    for i in range(27):
        v = 0.15 + 0.8 * rng.random()
        rect(ax, bx + 71.5 + i * 0.6, yb - 3.5, 0.45, 7 * v, fc=RATE if i == 10 else '#BDB3D9', ec='none', z=4)
    txt(ax, bx + 79.5, yb + 5.6, '27 ratings', size=5.4, c=RATE)
    txt(ax, bx + 2, yb - 13.3, 'Score: Pearson r across held-out videos, per emotion and participant, against Cowen ratings.\n'
                               'HK: six run-grouped outer folds. MC: mappings refitted on 2,108 development videos,\n'
                               'tested once on 72 videos (5 repeats averaged).', size=5.1, ha='left', va='top', linespacing=1.3)

    # ---- c: what is reported ----
    cy = 37
    panel(ax, bx - 2.5, cy + 2, 'c')
    txt(ax, bx + 2, cy, 'Reported per emotion (none is subtracted from another)', size=7, w='bold', ha='left')
    items = [
        ('i', 'true head output → frozen readout', 'reference: does the VCE readout transfer to Cowen?', RATE, '-'),
        ('ii', 'fMRI → reconstructed vs true head output', 'reconstruction accuracy, per coordinate', HEAD, '-'),
        ('iii', 'fMRI → reconstructed output → frozen readout', 'main brain-only prediction', INK, '-'),
        ('iv', 'fMRI → 27 ratings, direct ridge (Cowen targets)', 'reference, not an upper bound', GREY, '--'),
        ('v', 'same reconstruction → readout refitted on Cowen', 'matched-target control for (iii) vs (iv)', GREY, ':'),
    ]
    for i, (k, a, b, c, ls) in enumerate(items):
        y = cy - 6.5 - i * 6.0
        ax.add_patch(Circle((bx + 3.5, y), 2.0, fc='white', ec=c, lw=0.7, zorder=6))
        txt(ax, bx + 3.5, y - 0.05, k, size=5.2, c=c, w='bold', z=7)
        txt(ax, bx + 7.5, y + 1.0, a, size=5.4, ha='left')
        txt(ax, bx + 7.5, y - 1.7, b, size=4.9, c=GREY, ha='left')
    # left bottom note: per-participant
    txt(ax, 6, 24.5, 'Participant A gets its own ridge; participant B gets another.\n'
                     'The ridge is the only participant-specific transform; the readout\n'
                     'is shared across participants and never sees fMRI or MC ratings.',
        size=5.1, c=GREY, ha='left', va='top', linespacing=1.3)
    save(fig, 'emobrain_brain_decoding', OUT)
    return fig


def fig3c():
    W, H = 180, 66
    fig, ax = canvas(W, H)
    rng = np.random.default_rng(21)

    # ---- a: captions vs fear ratings ----
    panel(ax, 1.5, H - 1.5, 'a')
    txt(ax, 6, H - 3.2, 'Captions and fear ratings', size=7, w='bold', ha='left')
    sx, sy, sw, sh = 12, 12, 40, 36
    line(ax, [sx, sx + sw], [sy, sy], c=INK, lw=0.5)
    line(ax, [sx, sx], [sy, sy + sh], c=INK, lw=0.5)
    n = 90
    x = np.clip(rng.exponential(0.12, n), 0, 1)
    x[rng.random(n) < 0.45] = 0
    y = np.clip(0.10 + 0.55 * x + rng.normal(0, 0.10, n), 0, 1)
    for xv, yv in zip(x, y):
        ax.add_patch(Circle((sx + 1 + xv * (sw - 2) / 0.8, sy + 1 + yv * (sh - 2)), 0.6, fc=C_S, ec='white', lw=0.25, alpha=0.75, zorder=5))
    ex, ey = 0.40, 0.42
    ax.add_patch(Circle((sx + 1 + ex * (sw - 2) / 0.8, sy + 1 + ey * (sh - 2)), 1.1, fc='white', ec=INK, lw=0.8, zorder=6))
    txt(ax, sx + 1 + ex * (sw - 2) / 0.8 + 2, sy + 1 + ey * (sh - 2) + 2.5, '8 of 20 captions\nuse “chase”', size=5.0, ha='left', linespacing=1.2)
    for t in (0, 0.4, 0.8):
        txt(ax, sx + 1 + t * (sw - 2) / 0.8, sy - 1.6, f'{t:.1f}', size=5.0, c=GREY)
    for t in (0, 0.5, 1.0):
        txt(ax, sx - 1.2, sy + 1 + t * (sh - 2), f'{t:.1f}', size=5.0, c=GREY, ha='right')
    txt(ax, sx + sw / 2, sy - 4.6, 'fraction of captions using “chase” (per video)', size=5.4)
    txt(ax, sx - 7.5, sy + sh / 2, 'fraction of raters choosing fear', size=5.4, rotation=90)
    txt(ax, sx + 2, sy + sh - 1, 'one point = one Cowen video', size=4.9, c=GREY, ha='left', va='top')

    # ---- b: which fear heads track 'chase' beyond L and O ----
    bx = 63
    panel(ax, bx - 2.5, H - 1.5, 'b')
    txt(ax, bx + 2, H - 3.2, 'Fear heads that track “chase” beyond L and O', size=7, w='bold', ha='left')
    heads = ['3-7', '8-2', '9-4', '9-9']
    dr2 = [0.004, 0.006, 0.031, 0.009]
    ci = [0.006, 0.007, 0.010, 0.007]
    base, sc = 14, 900
    for i, (hh, v, e) in enumerate(zip(heads, dr2, ci)):
        x0 = bx + 8 + i * 11
        hit = (hh == '9-4')
        rect(ax, x0, base, 6, v * sc, fc=HEAD if hit else HEAD_F, ec=C_S if hit else HEAD, lw=1.1 if hit else 0.5, z=4)
        line(ax, [x0 + 3, x0 + 3], [base + (v - e) * sc, base + (v + e) * sc], c=INK, lw=0.6, z=5)
        txt(ax, x0 + 3, base - 2.2, hh, size=5.2, c=HEAD, w='bold' if hit else 'normal')
    rl = 0.012
    line(ax, [bx + 6, bx + 52], [base + rl * sc] * 2, c=GREY, lw=0.6, ls=(0, (2, 1.2)))
    txt(ax, bx + 52.5, base + rl * sc, 'layer-matched\nrandom, 95th pct.', size=4.8, c=GREY, ha='left', linespacing=1.15)
    line(ax, [bx + 6, bx + 52], [base, base], c=INK, lw=0.5)
    txt(ax, bx + 29, base - 5.6, 'selected fear heads (block-head)', size=5.3)
    txt(ax, bx + 3.2, base + 20, 'ΔR² on held-out videos:\n(L, O, covariates + “chase”)\n− (L, O, covariates)', size=4.9, ha='left', va='top', linespacing=1.25)

    # ---- c: same head and voxels ----
    cx = 126
    panel(ax, cx - 2.5, H - 1.5, 'c')
    txt(ax, cx + 2, H - 3.2, 'Head 9-4 output → voxels', size=7, w='bold', ha='left')
    regions = ['occipital\nvisual', 'temporo-parietal\nassociation']
    sel = [0.030, 0.026]
    rnd_mu = [0.028, 0.012]
    base, sc = 20, 800
    for i, (rg, s_, m_) in enumerate(zip(regions, sel, rnd_mu)):
        x0 = cx + 10 + i * 22
        pts = np.clip(rng.normal(m_, 0.004, 40), 0, None)
        for p in pts:
            ax.add_patch(Circle((x0 + rng.uniform(-2.2, 2.2), base + p * sc), 0.45, fc='#BBBBBB', ec='none', zorder=4))
        ax.add_patch(Circle((x0 + 6, base + s_ * sc), 1.0, fc=HEAD, ec=C_S, lw=1.0, zorder=6))
        txt(ax, x0 + 3, base - 3.0, rg, size=5.0, va='top', linespacing=1.15)
    line(ax, [cx + 5, cx + 50], [base, base], c=INK, lw=0.5)
    txt(ax, cx + 3.0, base + 14, 'test R² (encoding)', size=5.0, c=GREY, rotation=90)
    line(ax, [cx + 5, cx + 5], [base, base + 30], c=INK, lw=0.5)
    ax.add_patch(Circle((cx + 6, 9.2), 0.45, fc='#BBBBBB', ec='none', zorder=4))
    txt(ax, cx + 7.5, 9.2, 'layer-matched random heads', size=4.9, c=GREY, ha='left')
    ax.add_patch(Circle((cx + 6, 5.8), 0.9, fc=HEAD, ec=C_S, lw=1.0, zorder=6))
    txt(ax, cx + 7.5, 5.8, 'head 9-4; regions compared within participant', size=4.9, ha='left')
    txt(ax, W - 2, 1.4, 'Values and regions illustrative; this example is not part of the completion criteria', size=5.0, c=GREY, ha='right', style='italic')
    save(fig, 'emobrain_chase_head_roi', OUT)
    return fig


if __name__ == '__main__':
    fig5()
    fig3c()
