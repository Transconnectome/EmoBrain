import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from style import *
import numpy as np

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def matrix(ax, x, y, w, h, c, fc, label, sub, nrow=7, ncol=5, ls='-', lab_side='below'):
    rect(ax, x, y, w, h, fc=fc, ec=c, lw=0.7, z=3)
    for i in range(1, nrow):
        line(ax, [x, x + w], [y + h * i / nrow] * 2, c=c, lw=0.25, z=4)
    for j in range(1, ncol):
        line(ax, [x + w * j / ncol] * 2, [y, y + h], c=c, lw=0.25, z=4)
    if lab_side == 'below':
        txt(ax, x + w / 2, y - 1.8, label, size=5.8, c=c, w='bold', va='top')
        if sub:
            txt(ax, x + w / 2, y - 4.6, sub, size=5.0, c=GREY, va='top')
    else:
        txt(ax, x + w / 2, y + h + 1.6, label, size=5.8, c=c, w='bold', va='bottom')
        if sub:
            txt(ax, x + w / 2, y + h + 4.4, sub, size=5.0, c=GREY, va='bottom')


def fig4a():
    W, H = 180, 84
    fig, ax = canvas(W, H)
    rng = np.random.default_rng(11)

    # ---- a: three encoding models ----
    panel(ax, 1.5, H - 1.5, 'a')
    txt(ax, 6, H - 3.2, 'Three encoding models for the same held-out voxels', size=7, w='bold', ha='left')
    rows = [('H', 'selected fear heads', 'videos × 64K', HEAD, HEAD_F),
            ('E', '27 human ratings', 'videos × 27', RATE, RATE_F),
            ('H + E', 'both, separate ridge penalties', '(banded ridge)', INK, '#F4F4F4')]
    y0 = H - 17
    for i, (k, d, sub, c, fc) in enumerate(rows):
        y = y0 - i * 15
        if k == 'H + E':
            rect(ax, 6, y - 3.5, 5, 7, fc=HEAD_F, ec=HEAD, lw=0.6)
            rect(ax, 11.4, y - 3.5, 3.2, 7, fc=RATE_F, ec=RATE, lw=0.6)
        else:
            rect(ax, 6, y - 3.5, 8.6 if k == 'H' else 4.0, 7, fc=fc, ec=c, lw=0.6)
        txt(ax, 17, y + 1.2, k, size=6.4, c=c, w='bold', ha='left')
        txt(ax, 17, y - 1.8, d, size=5.3, ha='left')
        txt(ax, 17, y - 4.3, sub, size=5.0, c=GREY, ha='left')
        arrow(ax, 47, y, 54, y, lw=0.6)
        box(ax, 54.5, y - 3, 11, 6, fc='white', ec=INK)
        txt(ax, 60, y, 'ridge', size=5.6)
        arrow(ax, 65.8, y, 71, y, lw=0.6)
        txt(ax, 72, y, ['$R^2_H$', '$R^2_E$', '$R^2_{HE}$'][i], size=6.8, ha='left', c=c)
    # target
    yt = y0 - 15
    line(ax, [80.5, 80.5], [y0, y0 - 30], c=BRAIN, lw=0.6)
    for i in range(3):
        line(ax, [79.2, 80.5], [y0 - i * 15] * 2, c=BRAIN, lw=0.6)
    arrow(ax, 80.5, yt, 83.5, yt, c=BRAIN, lw=0.6, ms=4)
    brain(ax, 84, yt - 4.2, w=12, h=8.5)
    txt(ax, 90, yt - 6.6, 'same held-out\nvoxels', size=5.0, c=BRAIN, va='top', linespacing=1.2)
    txt(ax, 90, yt - 11.4, 'one ROI,\none participant', size=4.8, c=GREY, va='top', linespacing=1.2)
    txt(ax, 6, 22.5, 'Same test videos, same voxels and the same fold-wise\ntraining-mean baseline for all three models. '
                     'Fit, scaling and\npenalty choice use outer-training videos only.', size=5.2, c=GREY, ha='left', va='top', linespacing=1.3)
    txt(ax, 6, 10.0, 'E is shared by all 27 emotions and fitted once per fold.', size=5.2, c=GREY, ha='left', va='top')

    # ---- b: partition ----
    bx = 100
    panel(ax, bx - 2.5, H - 1.5, 'b')
    txt(ax, bx + 2, H - 3.2, 'Partition per voxel, then averaged in the ROI', size=7, w='bold', ha='left')
    vx, vy, rr = bx + 14, H - 20, 8
    ax.add_patch(Circle((vx - 4.5, vy), rr, fc=HEAD, alpha=0.25, ec=HEAD, lw=0.8, zorder=4))
    ax.add_patch(Circle((vx + 4.5, vy), rr, fc=RATE, alpha=0.25, ec=RATE, lw=0.8, zorder=4))
    txt(ax, vx - 8.2, vy, 'head\nunique', size=5.3, c=HEAD, w='bold')
    txt(ax, vx, vy, 'shared', size=5.3, c=INK, w='bold')
    txt(ax, vx + 8.2, vy, 'rating\nunique', size=5.3, c=RATE, w='bold')
    tx = bx + 33
    txt(ax, tx, H - 13, r'head unique $= R^2_{HE} - R^2_{E}$', size=6.0, ha='left', c=HEAD)
    txt(ax, tx, H - 18, r'rating unique $= R^2_{HE} - R^2_{H}$', size=6.0, ha='left', c=RATE)
    txt(ax, tx, H - 23, r'shared $= R^2_{H} + R^2_{E} - R^2_{HE}$', size=6.0, ha='left')
    txt(ax, tx, H - 28, 'the three parts add up to $R^2_{HE}$;\nnegative values are kept', size=5.2, ha='left', va='top', c=GREY)

    # ---- c: ROI groups stacked bars (illustrative) ----
    cx0 = bx
    panel(ax, cx0 - 2.5, 50, 'c')
    txt(ax, cx0 + 2, 48.3, 'Fear, one participant', size=6.5, w='bold', ha='left')
    groups = ['Vis', 'DAN', 'PMM', 'VMM', 'FPN', 'DMN', 'OAN']
    hu = [0.020, 0.012, 0.010, 0.008, 0.004, 0.003, 0.002]
    sh = [0.010, 0.010, 0.014, 0.012, 0.008, 0.010, 0.006]
    ru = [0.002, 0.003, 0.006, 0.008, 0.006, 0.010, 0.009]
    base, sc, bw = 9, 700, 3.6
    for i, g in enumerate(groups):
        x = cx0 + 4 + i * 5.6
        y = base
        for v, c in ((hu[i], HEAD), (sh[i], SHARED), (ru[i], RATE)):
            rect(ax, x, y, bw, v * sc, fc=c, ec='white', lw=0.3, z=4)
            y += v * sc
        txt(ax, x + bw / 2, base - 2.0, g, size=4.9, c=INK)
    line(ax, [cx0 + 3, cx0 + 4 + 7 * 5.6], [base, base], c=INK, lw=0.4)
    for t in (0, 0.02, 0.04):
        line(ax, [cx0 + 2.4, cx0 + 3], [base + t * sc] * 2, c=INK, lw=0.4)
        txt(ax, cx0 + 2.1, base + t * sc, f'{t:.2f}', size=4.6, ha='right', c=GREY)
    txt(ax, cx0 + 4, 3.4, 'Vis visual; DAN dorsal attention; PMM/VMM posterior/ventral multimodal;\n'
                          'FPN frontoparietal; DMN default; OAN orbito-affective (pre-specified groups)', size=4.5, c=GREY, ha='left', va='center', linespacing=1.25)

    # ---- d: slope contrast ----
    dx0 = 145
    panel(ax, dx0 - 2.5, 50, 'd')
    txt(ax, dx0 + 2, 48.3, 'Linking analysis 3 to 4', size=6.5, w='bold', ha='left')
    sx, sy, sw, sh_ = dx0 + 6, 11, 26, 30
    rect(ax, sx, sy, sw, sh_, fc='none', ec='none')
    line(ax, [sx, sx + sw], [sy, sy], c=INK, lw=0.5)
    line(ax, [sx, sx], [sy, sy + sh_], c=INK, lw=0.5)
    xs = rng.uniform(0.0, 1.0, 27)
    ys = 0.15 + 0.55 * xs + rng.normal(0, 0.12, 27)
    for xv, yv in zip(xs, ys):
        ax.add_patch(Circle((sx + 1 + xv * (sw - 2), sy + 1 + yv * (sh_ - 4)), 0.55, fc=HEAD, ec='white', lw=0.3, zorder=5, alpha=0.9))
    line(ax, [sx + 1, sx + sw - 1], [sy + 1 + 0.15 * (sh_ - 4), sy + 1 + 0.70 * (sh_ - 4)], c=INK, lw=0.7)
    txt(ax, sx + sw / 2, sy - 2.2, 'caption-unique R² of the head list (an. 3)', size=4.9, va='top')
    txt(ax, sx - 2.3, sy + sh_ / 2, 'head unique:\nassociation − visual (an. 4)', size=4.9, rotation=90, linespacing=1.2)
    txt(ax, sx + 1.5, sy + sh_ - 1.0, '27 emotions; slope with\njoint video/run bootstrap', size=4.7, c=GREY, ha='left', va='top', linespacing=1.2)
    txt(ax, W - 2, 1.4, 'Values illustrative', size=5.0, c=GREY, ha='right', style='italic')
    save(fig, 'emobrain_roi_partition', OUT)
    return fig


def rdm(ax, x, y, s, seed, c_map, title, c):
    rng = np.random.default_rng(seed)
    n = 8
    z = rng.normal(size=(n, 3))
    d = np.linalg.norm(z[:, None] - z[None], axis=-1)
    d = d / d.max()
    cs = s / n
    for i in range(n):
        for j in range(n):
            col = mpl.colors.to_hex(c_map(0.15 + 0.75 * d[i, j]))
            rect(ax, x + j * cs, y + (n - 1 - i) * cs, cs, cs, fc=col, ec='white', lw=0.2, z=3)
    rect(ax, x, y, s, s, fc='none', ec=c, lw=0.6, z=4)
    txt(ax, x + s / 2, y + s + 1.6, title, size=5.6, c=c, w='bold')


def fig4b():
    W, H = 180, 64
    fig, ax = canvas(W, H)

    # ---- a: three model conditions ----
    panel(ax, 1.5, H - 1.5, 'a')
    txt(ax, 6, H - 3.2, 'Same videos, three model conditions', size=7, w='bold', ha='left')
    frames(ax, 5, H - 25, w=12, h=8.5)
    txt(ax, 11, H - 28.5, 'Cowen videos', size=5.4)
    conds = [('intact', None), ('selected heads ablated', HEAD), ('layer-matched random ablated', GREY)]
    for i, (name, c) in enumerate(conds):
        y = H - 13 - i * 10.5
        arrow(ax, 20, H - 20.5, 27, y, lw=0.5, ms=4)
        box(ax, 27.5, y - 3.6, 26, 7.2, fc=MODEL_F, ec=MODEL)
        # mini 12x12 with marks
        for b in range(12):
            for h in range(12):
                on = False
                if c == HEAD and (b, h) in [(2, 6), (7, 1), (8, 3), (8, 8)]:
                    on = True
                if c == GREY and (b, h) in [(2, 1), (7, 9), (8, 0), (8, 5)]:
                    on = True
                rect(ax, 29 + b * 0.5, y - 3.0 + h * 0.5, 0.42, 0.42, fc=(c if on else 'white'), ec='#B7C1CC', lw=0.12, z=4)
        txt(ax, 36.5, y, 'VideoMAE', size=5.6, c=MODEL, ha='left')
        txt(ax, 27.5, y + 4.9, name, size=5.2, c=c or INK, ha='left')
        arrow(ax, 54, y, 59.5, y, lw=0.6, ms=4.5)
        rect(ax, 60, y - 3.2, 9, 6.4, fc=POOL_F, ec=POOL, lw=0.6)
        for k in range(1, 5):
            line(ax, [60, 69], [y - 3.2 + k * 1.28] * 2, c=POOL, lw=0.2)
    txt(ax, 64.5, H - 38.6, 'videos × 768\n(last layer)', size=5.0, c=POOL, va='top')
    txt(ax, 6, 15.5, 'Features are re-extracted at the same last-layer\nposition after every ablation. Random lists match\n'
                     'layer, count and the representational change\nmeasured on VCE validation videos.', size=5.1, c=GREY, ha='left', va='top', linespacing=1.3)

    # ---- b: RSA ----
    bx = 78
    panel(ax, bx - 2.5, H - 1.5, 'b')
    txt(ax, bx + 2, H - 3.2, 'Distance structure (RSA)', size=7, w='bold', ha='left')
    rdm(ax, bx + 4, H - 31, 18, 1, plt.cm.Greens, 'model RDM', POOL)
    rdm(ax, bx + 31, H - 31, 18, 2, plt.cm.Reds, 'ROI RDM', BRAIN)
    txt(ax, bx + 26.5, H - 22, 'vs', size=6.5, c=GREY)
    txt(ax, bx + 26.5, H - 36, 'Spearman ρ between upper triangles\n(1 − Pearson distances between videos)', size=5.2, va='top', linespacing=1.3)

    # ---- c: encoding ----
    cx = 132
    panel(ax, cx - 2.5, H - 1.5, 'c')
    txt(ax, cx + 2, H - 3.2, 'Voxel prediction (encoding)', size=7, w='bold', ha='left')
    matrix(ax, cx + 3, H - 30, 9, 16, POOL, POOL_F, 'features', 'train videos', nrow=6, ncol=3)
    arrow(ax, cx + 13, H - 22, cx + 18.5, H - 22, lw=0.6)
    box(ax, cx + 19, H - 25, 10, 6, fc='white', ec=INK)
    txt(ax, cx + 24, H - 22, 'ridge', size=5.6)
    arrow(ax, cx + 29.4, H - 22, cx + 34.5, H - 22, lw=0.6)
    matrix(ax, cx + 35, H - 30, 9, 16, BRAIN, BRAIN_F, 'voxels', 'test videos', nrow=6, ncol=4)
    txt(ax, cx + 24, H - 39.5, 'refit for every condition on training folds;\n'
                               'test R² against a fold training-mean baseline', size=5.2, va='top', linespacing=1.3)

    # ---- d: analysis-5 contrast bar ----
    dy = 13
    box(ax, bx, 3, 98, 15.5, fc='#FFFBF6', ec=HEAD, lw=0.6)
    txt(ax, bx + 2.5, dy + 3.8, 'Analysis 5, per ROI and emotion', size=6.2, c=HEAD, w='bold', ha='left')
    txt(ax, bx + 2.5, dy - 0.4, 'extra drop = (intact − selected ablated) − mean over matched random lists (intact − random ablated)', size=5.3, ha='left')
    txt(ax, bx + 2.5, dy - 4.4, 'compared directly between ROIs and between emotions; the same for RSA and encoding', size=5.0, c=GREY, ha='left')
    save(fig, 'emobrain_regional_alignment', OUT)
    return fig


if __name__ == '__main__':
    fig4a()
    fig4b()
