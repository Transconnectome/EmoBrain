import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from style import *
import numpy as np

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SEL = [(3, 7), (8, 2), (9, 4), (9, 9)]  # (block, head), illustrative fear list


def fig3a():
    W, H = 180, 76
    fig, ax = canvas(W, H)

    # ---- a: where the selected heads sit ----
    panel(ax, 1.5, H - 1.5, 'a')
    txt(ax, 6, H - 3.2, 'Where do the heads that support fear predictions sit?', size=7, w='bold', ha='left')
    gx, gy, cell, gap = 12, 31, 2.0, 0.55
    step = head_grid(ax, gx, gy, cell=cell, gap=gap, selected=SEL)
    gw = 12 * step - gap
    for b in range(12):
        txt(ax, gx + b * step + cell / 2, gy + 12 * cell + 1.6, str(b + 1), size=5.3, c=HEAD if b + 1 in (3, 8, 9) else GREY,
            w='bold' if b + 1 in (3, 8, 9) else 'normal')
    txt(ax, gx + gw / 2, gy + 12 * cell + 4.8, 'Transformer block (input → output)', size=5.8, c=MODEL)
    for h in (1, 4, 9, 12):
        txt(ax, gx - 1.0, gy + (12 - h) * cell + cell / 2, str(h), size=5.0, c=GREY, ha='right')
    txt(ax, gx - 5.2, gy + 6 * cell, 'head', size=5.6, c=GREY, rotation=90)
    # dot strip: selected heads per block
    yd = gy - 4.5
    line(ax, [gx, gx + gw], [yd, yd], c='#CCCCCC', lw=0.4)
    counts = {3: 1, 8: 1, 9: 2}
    for b, n in counts.items():
        for k in range(n):
            ax.add_patch(Circle((gx + (b - 1) * step + cell / 2, yd + k * 2.0), 0.75, fc=HEAD, ec=INK, lw=0.4, zorder=6))
    txt(ax, 6, yd - 3.6, 'Dots: selected heads per block (example: 1 in block 3, 1 in block 8, 2 in block 9).\n'
                         'Depth is reported as the model\'s layer dependence,\nnot as abstraction or a brain processing stage.',
        size=5.3, c=GREY, ha='left', va='top', linespacing=1.3)

    # zoom on block 9
    zx = gx + gw + 8
    b9x = gx + 8 * step
    line(ax, [b9x + cell, zx], [gy + 12 * cell, gy + 12 * cell + 2], c=HEAD, lw=0.45, ls=(0, (2, 1.2)))
    line(ax, [b9x + cell, zx], [gy, gy - 2], c=HEAD, lw=0.45, ls=(0, (2, 1.2)))
    box(ax, zx, gy - 2, 25, 12 * cell + 4, fc='#FFFBF6', ec=HEAD, lw=0.6)
    txt(ax, zx + 12.5, gy + 12 * cell + 4.6, 'block 9', size=6, c=HEAD, w='bold')
    for h in range(1, 13):
        on = h in (4, 9)
        yy = gy + (12 - h) * cell
        rect(ax, zx + 3.4, yy + 0.2, 9, cell - 0.4, fc=HEAD if on else 'white', ec=INK if on else MODEL, lw=0.5)
        txt(ax, zx + 2.6, yy + cell / 2, str(h), size=4.8, c=HEAD if on else GREY, ha='right', w='bold' if on else 'normal')
    for h in (4, 9):
        yy = gy + (12 - h) * cell + cell / 2
        arrow(ax, zx + 12.7, yy, zx + 16.7, yy, c=HEAD, lw=0.6, ms=4)
        txt(ax, zx + 17.2, yy, '64', size=5.2, c=HEAD, ha='left')
    txt(ax, zx + 12.5, gy - 3.8, 'read or ablate at\nthe proj input (Fig. 2b)', size=5.2, c=HEAD, va='top')

    # ---- b: ranking procedure ----
    bx = 97
    panel(ax, bx - 2.5, H - 1.5, 'b')
    txt(ax, bx + 2, H - 3.2, 'Rank heads on held-out VCE validation videos', size=7, w='bold', ha='left')
    rng = np.random.default_rng(7)
    yy = H - 9.5
    for k in range(3):
        x0 = bx + 2 + k * 12.5
        m = np.zeros(144, bool)
        m[rng.choice(144, 72, replace=False)] = True
        for i in range(144):
            b, h = i // 12, i % 12
            rect(ax, x0 + b * 0.78, yy - h * 0.78, 0.66, 0.66, fc='#9AA3AD' if m[i] else 'white', ec='#B7C1CC', lw=0.2, z=3)
        txt(ax, x0 + 4.6, yy - 10.4, ['mask 1', 'mask 2', 'mask M'][k], size=5.0, c=GREY)
        txt(ax, x0 + 4.6, yy - 13.0, ['r = 0.41', 'r = 0.33', 'r = …'][k], size=5.0, c=RATE)
    txt(ax, bx + 37.5, yy - 4.5, '…', size=8, c=GREY)
    txt(ax, bx + 42, yy + 0.3, '72 of 144 heads ablated (grey)\nper mask; each mask is applied\nto the whole validation set and\n'
                                'gives one Pearson r per emotion\nacross videos', size=5.2, ha='left', va='top', linespacing=1.3)
    fy = yy - 17.6
    txt(ax, bx + 2, fy, r'contribution$(h)$ = mean $r$ (masks keeping $h$) − mean $r$ (masks ablating $h$)', size=5.6, ha='left')
    vals = np.sort(rng.gamma(1.4, 0.004, 144))[::-1]
    vals[:4] += 0.012
    x0, ybase = bx + 2, fy - 12.5
    for i, v in enumerate(vals[:60]):
        rect(ax, x0 + i * 1.2, ybase, 0.9, 400 * v * 0.22, fc=HEAD if i < 4 else '#C7CED6', ec='none', z=3)
    line(ax, [x0 - 0.3, x0 + 60 * 1.2], [ybase, ybase], c=INK, lw=0.4)
    txt(ax, x0 + 5.5, ybase + 88 * vals[0] + 1.2, 'top K for fear', size=5.3, c=HEAD, ha='left', va='bottom')
    txt(ax, x0 + 72, ybase + 1.0, 'heads ranked (first 60 of 144)', size=5.0, c=GREY, ha='right', va='bottom')

    # ---- c: test design ----
    cy0 = ybase - 5.5
    panel(ax, bx - 2.5, cy0 + 1.5, 'c')
    txt(ax, bx + 2, cy0, 'Test videos: is the drop specific to the selected emotion?', size=7, w='bold', ha='left')
    mx, my, n, cs = bx + 2, 3.0, 9, 1.75
    vals = rng.normal(0, 0.25, (n, n))
    for i in range(n):
        vals[i, i] += 0.9
    for i in range(n):
        for j in range(n):
            v = np.clip(vals[i, j], -1, 1)
            c = mpl.colors.to_hex(plt.cm.Blues(0.08 + 0.8 * max(0.0, (v + 0.3) / 1.3)))
            rect(ax, mx + j * cs, my + (n - 1 - i) * cs, cs, cs, fc=c, ec='white', lw=0.3, z=3)
    jf = 4
    rect(ax, mx + jf * cs, my, cs, n * cs, fc='none', ec=INK, lw=0.9, z=5)
    txt(ax, mx + n * cs / 2, my + n * cs + 1.6, 'evaluated emotion f', size=5.0, c=GREY)
    txt(ax, mx - 1.2, my + n * cs / 2, 'list g', size=5.0, c=GREY, rotation=90, ha='right')
    tx = mx + n * cs + 4
    txt(ax, tx, my + n * cs - 0.2, 'each cell: E[g,f] = drop of f after ablating list g\n'
                                   '                − mean drop for layer-matched random lists', size=5.2, ha='left', va='top', linespacing=1.3)
    txt(ax, tx, my + n * cs - 7.4, r'selectivity of f:  $S_f = E[f,f] - \mathrm{mean}_{g \neq f}\,E[g,f]$', size=5.6, ha='left', va='top')
    txt(ax, tx, my + 2.2, 'one column at a time (outlined); 27 × 27 in the study', size=5.0, c=GREY, ha='left', va='top')
    txt(ax, W - 2, 1.4, 'Values illustrative', size=5.0, c=GREY, ha='right', style='italic')
    save(fig, 'emobrain_head_layers', OUT)
    return fig


# consistent illustrative decomposition (Venn regions a..g) for the two targets
REG = {
    'rating': dict(L=0.04, O=0.02, S=0.10, LO=0.02, LS=0.03, OS=0.07, LOS=0.02),
    'head': dict(L=0.08, O=0.04, S=0.05, LO=0.03, LS=0.04, OS=0.02, LOS=0.02),
}


def r2(reg, bands):
    bands = set(bands)
    return sum(v for k, v in reg.items() if set(k) & bands)


def fig3b():
    W, H = 180, 84
    fig, ax = canvas(W, H)
    panel(ax, 1.5, H - 1.5, 'a')
    txt(ax, 6, H - 3.2, 'Seven feature combinations predict two targets on the same held-out videos', size=7, w='bold', ha='left')

    # input strip
    frames(ax, 6, H - 22, w=12, h=8.5)
    cx = 26
    def chip(y, c, k, desc):
        ax.add_patch(Circle((cx, y), 1.6, fc=c, ec='none', zorder=6))
        txt(ax, cx, y - 0.05, k, size=5.8, c='white', w='bold', z=7)
        txt(ax, cx + 3, y, desc, size=5.4, ha='left')
    chip(H - 9.5, C_L, 'L', 'low-level visual: luminance, colour, motion energy (measured on the video)')
    chip(H - 14.0, C_O, 'O', 'object nouns: “dog”, “person” (noun-only captions)')
    chip(H - 18.5, C_S, 'S', 'full caption: “a dog chases a person” (emotion words removed)')
    txt(ax, cx + 3, H - 23.2, 'O and S use the same frozen DeBERTa-large (20 captions per video averaged).\n'
                               'Caption length and emotion-word rate enter every model.', size=5.0, c=GREY, ha='left', linespacing=1.3)

    # table of seven combinations
    combos = ['L', 'O', 'S', 'LO', 'LS', 'OS', 'LOS']
    names = ['L', 'O', 'S', 'L+O', 'L+S', 'O+S', 'L+O+S']
    ty0, rh = H - 33, 5.6
    colx = {'L': 12, 'O': 17, 'S': 22}
    for k, c in zip('LOS', (C_L, C_O, C_S)):
        txt(ax, colx[k], ty0 + 3.4, k, size=5.8, c=c, w='bold')
    bx1, bx2, blen = 32, 76, 34
    txt(ax, bx1, ty0 + 3.4, 'human fear rating (Cowen), test R²', size=5.6, c=RATE, ha='left', w='bold')
    txt(ax, bx2, ty0 + 3.4, 'fear-head output, test R²', size=5.6, c=HEAD, ha='left', w='bold')
    for i, (cmb, nm) in enumerate(zip(combos, names)):
        y = ty0 - i * rh
        if i % 2 == 0:
            rect(ax, 5, y - rh / 2 + 0.3, 108, rh - 0.6, fc='#F7F7F7', ec='none', z=1)
        for k, c in zip('LOS', (C_L, C_O, C_S)):
            on = k in cmb
            ax.add_patch(Circle((colx[k], y), 1.15, fc=c if on else 'white', ec=c if on else '#BBBBBB', lw=0.5, zorder=5))
        for (x0, tgt, c) in ((bx1, 'rating', RATE), (bx2, 'head', HEAD)):
            v = r2(REG[tgt], cmb)
            rect(ax, x0, y - 1.5, blen * v / 0.32, 3.0, fc=c, ec='none', z=3, alpha=0.9 if cmb == 'LOS' else 0.55)
            txt(ax, x0 + blen * v / 0.32 + 1.0, y, f'{v:.2f}', size=5.4, ha='left')
    yl = ty0 - 6.5 * rh
    txt(ax, 6, yl - 1.2, 'Baseline (covariates only) R² = 0.00 in this example', size=5.0, c=GREY, ha='left', va='top')

    # ---- b: unique and shared ----
    bx = 118
    panel(ax, bx - 2.5, H - 1.5, 'b')
    txt(ax, bx + 2, H - 3.2, 'Unique and shared parts', size=7, w='bold', ha='left')
    # small Venn
    vx, vy, rr = bx + 12, H - 19, 5.2
    for (dx, dy, c, k) in ((-2.6, 1.8, C_L, 'L'), (2.6, 1.8, C_O, 'O'), (0, -2.4, C_S, 'S')):
        ax.add_patch(Circle((vx + dx, vy + dy), rr, fc=c, ec=c, alpha=0.22, lw=0.7, zorder=4))
        txt(ax, vx + dx * 2.3, vy + dy * 2.6, k, size=6, c=c, w='bold')
    txt(ax, bx + 25, H - 12.5, 'unique S = R²(L,O,S) − R²(L,O)', size=5.4, ha='left')
    txt(ax, bx + 25, H - 16.5, 'rating: 0.30 − 0.20 = 0.10', size=5.4, ha='left', c=RATE)
    txt(ax, bx + 25, H - 20.0, 'head:   0.28 − 0.23 = 0.05', size=5.4, ha='left', c=HEAD)
    txt(ax, bx + 25, H - 24.5, 'negative estimates are reported as is', size=5.0, ha='left', c=GREY, style='italic')

    # grouped bars
    parts = ['L', 'O', 'S', 'LO', 'LS', 'OS', 'LOS']
    labels = ['L', 'O', 'S', 'L∩O', 'L∩S', 'O∩S', 'L∩O∩S']
    cols = [C_L, C_O, C_S, SHARED, SHARED, SHARED, '#8C8C8C']
    by0, bw, bg = 13, 2.3, 2.6
    base = by0
    scale = 300
    txt(ax, bx + 4, H - 34, 'unique', size=5.6, c=INK, ha='left', w='bold')
    txt(ax, bx + 2 + 3 * (2 * bw + bg) + 1, H - 34, 'shared (sum 0.14 / 0.11)', size=5.6, c=INK, ha='left', w='bold')
    for i, (p, lab, c) in enumerate(zip(parts, labels, cols)):
        x = bx + 2 + i * (2 * bw + bg) + (1.0 if i >= 3 else 0)
        for j, (tgt, ec) in enumerate((('rating', RATE), ('head', HEAD))):
            v = REG[tgt][p]
            rect(ax, x + j * bw, base, bw - 0.2, v * scale, fc=c, ec=ec, lw=0.8, z=4)
        txt(ax, x + bw, base - 2.4, lab, size=5.0, c=INK if i >= 3 else c, w='bold' if i < 3 else 'normal')
    line(ax, [bx + 1, bx + 2 + 7 * (2 * bw + bg) + 1], [base, base], c=INK, lw=0.4)
    for t in (0, 0.05, 0.10):
        line(ax, [bx + 0.6, bx + 1.2], [base + t * scale] * 2, c=INK, lw=0.4)
        txt(ax, bx + 0.3, base + t * scale, f'{t:.2f}', size=4.8, ha='right', c=GREY)
    # legend for edge colours
    rect(ax, bx + 4, 3.2, 2.2, 2.2, fc='white', ec=RATE, lw=0.8)
    txt(ax, bx + 7, 4.3, 'rating', size=5.2, ha='left', c=RATE)
    rect(ax, bx + 17, 3.2, 2.2, 2.2, fc='white', ec=HEAD, lw=0.8)
    txt(ax, bx + 20, 4.3, 'head', size=5.2, ha='left', c=HEAD)
    txt(ax, W - 2, 1.6, 'Values illustrative', size=5.0, c=GREY, ha='right', style='italic')
    save(fig, 'emobrain_head_captions', OUT)
    return fig


if __name__ == '__main__':
    fig3a()
    fig3b()
