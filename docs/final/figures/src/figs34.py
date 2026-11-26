import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import *
from fig1 import P1374, FEAR, SEL

REG = {'rating': dict(L=0.04, O=0.02, S=0.10, LO=0.02, LS=0.03, OS=0.07, LOS=0.02),
       'head': dict(L=0.08, O=0.04, S=0.05, LO=0.03, LS=0.04, OS=0.02, LOS=0.02)}


def r2(reg, bands):
    return sum(v for k, v in reg.items() if set(k) & set(bands))


def illus(ax, W, y=1.6):
    T(ax, W - 2, y, 'values illustrative', size=5.4, c=GREY, ha='right', st='italic')


# ---------------------------------------------------------------- 3a
def fig3a():
    W, H = 180, 70
    fig, ax = canvas(W, H)
    rng = np.random.default_rng(7)
    panel(ax, 1, H - 1, 'a')
    T(ax, 7, H - 3.6, 'Rank heads on VCE validation videos', size=8, w='bold', ha='left')
    y = H - 30
    tensor(ax, 4, y + 3, 13, 10, 'validation\nvideos', size=6.0)
    arrow(ax, 17.5, y + 8, 21.5, y + 8)
    for k in range(3):
        x0 = 22 + k * 13
        masked = [(b + 1, h + 1) for b in range(12) for h in range(12) if rng.random() < 0.5]
        head_grid(ax, x0, y + 2.5, cell=0.85, gap=0.1, masked=masked)
        T(ax, x0 + 5.6, y + 0.4, ['mask 1', 'mask 2', 'mask M'][k], size=5.6, c=GREY)
        T(ax, x0 + 5.6, y - 3.0, ['r = 0.41', 'r = 0.33', 'r = …'][k], size=6.0, c=RATE)
    T(ax, 22 + 3 * 13 - 1.2, y + 7.6, '…', size=9, c=GREY)
    T(ax, 22, y + 16.6, 'each mask: 72 of 144 heads set to 0 (grey) for all videos', size=6.0, c=GREY, ha='left')
    T(ax, 22, y - 7.4, 'r = Pearson r for fear across validation videos', size=5.8, c=GREY, ha='left')
    # formula + ranked bars
    T(ax, 4, y - 13, r'contribution$(h)$ = mean $r$ (masks keeping $h$) − mean $r$ (masks ablating $h$)', size=6.4, ha='left')
    vals = np.sort(rng.gamma(1.4, 0.004, 144))[::-1]
    vals[:4] += 0.012
    for i, v in enumerate(vals[:56]):
        ax.add_patch(Rectangle((4 + i * 1.45, 4), 1.1, 300 * v, fc=HEAD if i < 4 else '#C9CFD6', ec='none', zorder=4))
    line(ax, [3.6, 4 + 56 * 1.45], [4, 4], c=INK, lw=0.5)
    T(ax, 10.5, 4 + 300 * vals[0] + 1.6, 'top K for fear', size=6.0, c=HEAD, ha='left', va='bottom')
    T(ax, 4 + 56 * 1.45, 5.2, 'heads ranked', size=5.6, c=GREY, ha='right', va='bottom')

    # b: selected heads
    bx = 92
    panel(ax, bx - 3, H - 1, 'b')
    T(ax, bx + 3, H - 3.6, 'Selected fear heads', size=8, w='bold', ha='left')
    gw, gh = head_grid(ax, bx + 4, 24, cell=2.2, gap=0.45, sel=SEL)
    for b in range(12):
        T(ax, bx + 4 + b * 2.65 + 1.1, 24 + gh + 1.6, str(b + 1), size=5.4, c=HEAD if b + 1 in (3, 8, 9) else GREY, w='bold' if b + 1 in (3, 8, 9) else 'normal')
    T(ax, bx + 4 + gw / 2, 24 + gh + 4.8, 'block (input → output)', size=6.0, c=MODEL)
    T(ax, bx + 1.6, 24 + gh / 2, 'head', size=6.0, c=GREY, rotation=90)
    yd = 19.5
    line(ax, [bx + 4, bx + 4 + gw], [yd, yd], c='#CCCCCC', lw=0.5)
    for b, n in {3: 1, 8: 1, 9: 2}.items():
        for k in range(n):
            ax.add_patch(Circle((bx + 4 + (b - 1) * 2.65 + 1.1, yd + k * 2.1), 0.8, fc=HEAD, ec=INK, lw=0.4, zorder=6))
    T(ax, bx + 4 + gw / 2, 13.6, 'heads per block (example)', size=6.0, c=GREY)
    T(ax, bx + 4 + gw / 2, 9.8, 'depth is not read as abstraction', size=5.6, c=GREY, st='italic')

    # c: selectivity test
    cx = 136
    panel(ax, cx - 3, H - 1, 'c')
    T(ax, cx + 3, H - 3.6, 'Test videos: specific to fear?', size=8, w='bold', ha='left')
    emos = ['fear', 'anxiety', 'horror', 'amuse.', 'awe', 'joy']
    sel_drop = [0.12, 0.05, 0.04, 0.01, 0.0, 0.01]
    rnd_drop = [0.03, 0.02, 0.02, 0.01, 0.01, 0.01]
    base, sc = 20, 230
    for i, (e, s_, r_) in enumerate(zip(emos, sel_drop, rnd_drop)):
        x = cx + 5 + i * 6.6
        ax.add_patch(Rectangle((x, base), 2.4, s_ * sc, fc=HEAD, ec='none', zorder=4))
        ax.add_patch(Rectangle((x + 2.6, base), 2.4, r_ * sc, fc='#BDBDBD', ec='none', zorder=4))
        T(ax, x + 2.5, base - 2.4, e, size=5.6, c=RATE if e == 'fear' else INK, w='bold' if e == 'fear' else 'normal')
    line(ax, [cx + 4, cx + 44], [base, base], c=INK, lw=0.5)
    line(ax, [cx + 4, cx + 4], [base, base + 32], c=INK, lw=0.5)
    T(ax, cx + 2.2, base + 16, 'drop in r', size=5.8, c=GREY, rotation=90)
    ax.add_patch(Rectangle((cx + 20, base + 30), 2, 2, fc=HEAD, ec='none', zorder=4))
    T(ax, cx + 22.8, base + 31, 'fear list', size=5.6, ha='left')
    ax.add_patch(Rectangle((cx + 20, base + 26.4), 2, 2, fc='#BDBDBD', ec='none', zorder=4))
    T(ax, cx + 22.8, base + 27.4, 'layer-matched random', size=5.6, ha='left')
    T(ax, cx + 2, 11.4, 'selectivity = own-list drop − mean other-list', size=5.8, ha='left')
    T(ax, cx + 2, 8.0, 'drop (each after subtracting random)', size=5.8, ha='left')
    illus(ax, W)
    save(fig, 'emobrain_head_layers')
    return fig


# ---------------------------------------------------------------- 3b
def fig3b():
    W, H = 180, 96
    fig, ax = canvas(W, H)
    panel(ax, 1, H - 1, 'a')
    T(ax, 7, H - 3.6, 'Three kinds of stimulus information predict two targets (Cowen video 1374)', size=8, w='bold', ha='left')
    y = H - 13
    stack(ax, ['cowen_1374_f3.png', 'cowen_1374_f4.png', 'cowen_1374_f1.png'], 4, y - 25, 16, dx=1.8, dy=1.8)
    T(ax, 13.5, y - 28, 'video', size=6.0, c=GREY)
    # L
    arrow(ax, 24, y - 4, 30, y - 2)
    img(ax, 'cowen_1374_motion.png', 30.5, y - 8, 11, 11)
    badge(ax, 46, y - 2.5, 'L', c=C_L, r=1.9, size=6.4, fc='white')
    T(ax, 49, y - 1.3, 'luminance, colour,', size=6.0, ha='left')
    T(ax, 49, y - 4.3, 'motion energy', size=6.0, ha='left')
    # captions
    caption_box(ax, 30.5, y - 33, 50, 18, '"A large lizard chases a woman\nin a kimono ... runs away."\n'
                                           '"A woman runs while holding a rope\nand is chased by a large reptile."\n...  (20 captions)', size=5.6)
    arrow(ax, 24, y - 16, 30, y - 22)
    badge(ax, 85, y - 18.5, 'O', c=C_O, r=1.9, size=6.4)
    T(ax, 88, y - 18.5, 'nouns: woman, lizard, rope', size=6.0, ha='left')
    badge(ax, 85, y - 27.5, 'S', c=C_S, r=1.9, size=6.4)
    T(ax, 88, y - 27.5, 'full sentences', size=6.0, ha='left')
    arrow(ax, 81, y - 21, 83, y - 19.5, lw=0.6)
    arrow(ax, 81, y - 26, 83, y - 27.2, lw=0.6)
    trapezoid(ax, 116, y - 33, 13, 16, 'DeBERTa', 'large', size=6.0)
    snow(ax, 127.2, y - 19.2, 1.0)
    arrow(ax, 112, y - 23, 115.5, y - 25)
    T(ax, 122.5, y - 35.5, 'emotion words removed from S', size=5.4, c=GREY)
    # banded ridge
    arrow(ax, 129.5, y - 25, 136.5, y - 16)
    arrow(ax, 74, y - 2.5, 136.5, y - 9)
    block(ax, 137, y - 18, 16, 11, 'banded', 'ridge', fc='white', ec=INK, size=6.6, subsize=6.6)
    fire(ax, 152, y - 7.8, 0.7)
    arrow(ax, 153.5, y - 10, 157.5, y - 5)
    arrow(ax, 153.5, y - 14, 157.5, y - 19)
    tensor(ax, 158, y - 9, 19, 8, 'N × 64K', fc=HEAD_F, ec=HEAD, c=HEAD, size=6.4)
    T(ax, 167.5, y + 1.2, 'fear-head output', size=6.0, c=HEAD, w='bold')
    tensor(ax, 158, y - 25, 19, 8, 'N × 1', fc=RATE_F, ec=RATE, c=RATE, size=6.4)
    T(ax, 167.5, y - 27.6, 'Cowen fear rating', size=6.0, c=RATE, w='bold')
    line(ax, [3, W - 3], [y - 39, y - 39], c='#DDDDDD', lw=0.6)

    # b: seven combinations
    panel(ax, 1, y - 40.5, 'b')
    T(ax, 7, y - 43.2, 'Test R² of the seven combinations', size=8, w='bold', ha='left')
    combos = ['L', 'O', 'S', 'LO', 'LS', 'OS', 'LOS']
    x0 = 8
    for i, cmb in enumerate(combos):
        xx = x0 + i * 13
        for k, (b, c) in enumerate(zip('LOS', (C_L, C_O, C_S))):
            on = b in cmb
            ax.add_patch(Circle((xx + 1.2 + k * 2.4, 4.0), 0.95, fc=c if on else 'white', ec=c if on else '#BBBBBB', lw=0.5, zorder=6))
        for j, (tgt, c) in enumerate((('head', HEAD), ('rating', RATE))):
            v = r2(REG[tgt], cmb)
            ax.add_patch(Rectangle((xx + j * 4.0, 7.0), 3.4, v * 80, fc=c, ec='none', zorder=4, alpha=0.95 if cmb == 'LOS' else 0.6))
    line(ax, [x0 - 1, x0 + 7 * 13 - 3], [7, 7], c=INK, lw=0.5)
    ax.add_patch(Rectangle((x0 + 62, 38.6), 2, 2, fc=HEAD, ec='none', zorder=4))
    T(ax, x0 + 64.8, 39.6, 'head output', size=5.8, ha='left')
    ax.add_patch(Rectangle((x0 + 79, 38.6), 2, 2, fc=RATE, ec='none', zorder=4))
    T(ax, x0 + 81.8, 39.6, 'fear rating', size=5.8, ha='left')

    # c: unique and shared
    cx = 104
    panel(ax, cx - 3, y - 40.5, 'c')
    T(ax, cx + 3, y - 43.2, 'Unique and shared parts', size=8, w='bold', ha='left')
    T(ax, cx + 3, y - 47.6, r'unique S = $R^2$(L,O,S) − $R^2$(L,O):  head 0.05, rating 0.10', size=5.8, ha='left')
    parts = ['L', 'O', 'S', 'LO', 'LS', 'OS', 'LOS']
    labs = ['L', 'O', 'S', 'L∩O', 'L∩S', 'O∩S', 'all']
    cols = [C_L, C_O, C_S, '#B5B5B5', '#B5B5B5', '#B5B5B5', '#8A8A8A']
    for i, (p, lb, c) in enumerate(zip(parts, labs, cols)):
        xx = cx + 5 + i * 10
        for j, (tgt, ec) in enumerate((('head', HEAD), ('rating', RATE))):
            v = REG[tgt][p]
            ax.add_patch(Rectangle((xx + j * 3.6, 7), 3.2, v * 160, fc=c, ec=ec, lw=0.9, zorder=4))
        T(ax, xx + 3.4, 4.2, lb, size=5.8, c=c if i < 3 else INK, w='bold' if i < 3 else 'normal')
    line(ax, [cx + 4, cx + 74], [7, 7], c=INK, lw=0.5)
    T(ax, cx + 3, 31.6, 'outline: orange = head, purple = rating', size=5.6, c=GREY, ha='left')
    illus(ax, W, 1.4)
    save(fig, 'emobrain_head_captions')
    return fig


# ---------------------------------------------------------------- 3c
def fig3c():
    W, H = 180, 62
    fig, ax = canvas(W, H)
    rng = np.random.default_rng(21)
    panel(ax, 1, H - 1, 'a')
    T(ax, 7, H - 3.6, '“chase” in captions vs fear ratings', size=8, w='bold', ha='left')
    sx, sy, sw, sh = 12, 10, 40, 38
    line(ax, [sx, sx + sw], [sy, sy], c=INK, lw=0.5)
    line(ax, [sx, sx], [sy, sy + sh], c=INK, lw=0.5)
    n = 110
    x = np.clip(rng.exponential(0.10, n), 0, 1)
    x[rng.random(n) < 0.5] = 0
    yv = np.clip(0.08 + 0.45 * x + rng.normal(0, 0.10, n), 0, 1)
    for a, b in zip(x, yv):
        ax.add_patch(Circle((sx + 1 + a * (sw - 2) / 0.8, sy + 1 + b * (sh - 2)), 0.55, fc='#D99BB5', ec='white', lw=0.2, zorder=5))
    px, py = sx + 1 + 0.65 * (sw - 2) / 0.8, sy + 1 + 0.545 * (sh - 2)
    ax.add_patch(Circle((px, py), 1.1, fc=C_S, ec=INK, lw=0.8, zorder=7))
    img(ax, 'cowen_1374_f3.png', px - 12, py + 2.5, 9, 9, z=8)
    T(ax, px - 7.5, py + 13.2, 'video 1374', size=5.4, c=INK)
    T(ax, px + 1.8, py - 2.8, '13/20 captions,\nfear 0.55 (real)', size=5.4, ha='left', linespacing=1.15)
    for t in (0, 0.4, 0.8):
        T(ax, sx + 1 + t * (sw - 2) / 0.8, sy - 1.8, f'{t:.1f}', size=5.4, c=GREY)
    for t in (0, 0.5, 1.0):
        T(ax, sx - 1.2, sy + 1 + t * (sh - 2), f'{t:.1f}', size=5.4, c=GREY, ha='right')
    T(ax, sx + sw / 2, sy - 5.0, 'fraction of captions using “chase”', size=6.0)
    T(ax, sx - 7.0, sy + sh / 2, 'fraction choosing fear', size=6.0, rotation=90)

    # b
    bx = 63
    panel(ax, bx - 3, H - 1, 'b')
    T(ax, bx + 3, H - 3.6, 'Which fear heads track “chase”?', size=8, w='bold', ha='left')
    heads = ['3-7', '8-2', '9-4', '9-9']
    d = [0.004, 0.006, 0.031, 0.009]
    base, sc = 12, 900
    for i, (hh, v) in enumerate(zip(heads, d)):
        xx = bx + 8 + i * 11
        hit = hh == '9-4'
        ax.add_patch(Rectangle((xx, base), 6, v * sc, fc=HEAD if hit else HEAD_F, ec=C_S if hit else HEAD, lw=1.2 if hit else 0.6, zorder=4))
        T(ax, xx + 3, base - 2.4, hh, size=6.0, c=HEAD, w='bold' if hit else 'normal')
    line(ax, [bx + 6, bx + 53], [base + 0.012 * sc] * 2, c=GREY, lw=0.6, ls=(0, (2, 1.2)))
    T(ax, bx + 6, base + 0.012 * sc + 2.0, 'random heads, 95th pct.', size=5.4, c=GREY, ha='left')
    line(ax, [bx + 6, bx + 53], [base, base], c=INK, lw=0.5)
    T(ax, bx + 29, base - 6.0, 'fear heads (block-head)', size=6.0)
    T(ax, bx + 5, H - 9.5, 'ΔR² when “chase” is added to L, O', size=6.0, c=GREY, ha='left')

    # c
    cx = 122
    panel(ax, cx - 3, H - 1, 'c')
    T(ax, cx + 3, H - 3.6, 'Head 9-4 → voxels', size=8, w='bold', ha='left')
    img(ax, 'cortex_vis_assoc.png', cx + 2, 36, 26, border=False, trim=True)
    ax.add_patch(Rectangle((cx + 35, 45), 2, 2, fc='#1B9E77', ec='none', zorder=4))
    T(ax, cx + 37.8, 46, 'occipital', size=5.8, ha='left')
    ax.add_patch(Rectangle((cx + 35, 41), 2, 2, fc='#C2477A', ec='none', zorder=4))
    T(ax, cx + 37.8, 42, 'temporo-parietal', size=5.8, ha='left')
    base, sc = 9, 480
    for i, (col, s_, m_) in enumerate((('#1B9E77', 0.030, 0.028), ('#C2477A', 0.026, 0.012))):
        x0 = cx + 10 + i * 22
        for p in np.clip(rng.normal(m_, 0.004, 35), 0, None):
            ax.add_patch(Circle((x0 + rng.uniform(-2.0, 2.0), base + p * sc), 0.42, fc='#BDBDBD', ec='none', zorder=4))
        ax.add_patch(Circle((x0 + 5.5, base + s_ * sc), 1.0, fc=HEAD, ec=col, lw=1.2, zorder=6))
    line(ax, [cx + 5, cx + 46], [base, base], c=INK, lw=0.5)
    T(ax, cx + 26, 4.6, 'grey: random heads; orange: head 9-4', size=5.4, c=GREY)
    illus(ax, W, 1.4)
    save(fig, 'emobrain_chase_head_roi')
    return fig


# ---------------------------------------------------------------- 4a
def fig4a():
    W, H = 180, 74
    fig, ax = canvas(W, H)
    rng = np.random.default_rng(11)
    panel(ax, 1, H - 1, 'a')
    T(ax, 7, H - 3.6, 'Three encoding models, same held-out voxels', size=8, w='bold', ha='left')
    rows = [('H', HEAD, HEAD_F, 'N × 64K', 'head output'), ('E', RATE, RATE_F, 'N × 27', 'ratings'), ('H + E', INK, '#F2F2F2', '', 'both')]
    for i, (k, c, fc, s, d) in enumerate(rows):
        y = H - 16 - i * 13
        if k == 'H + E':
            tensor(ax, 5, y - 4, 9, 8, 'H', fc=HEAD_F, ec=HEAD, c=HEAD, size=6.2)
            tensor(ax, 14.5, y - 4, 7, 8, 'E', fc=RATE_F, ec=RATE, c=RATE, size=6.2)
        else:
            tensor(ax, 5, y - 4, 16.5, 8, s, fc=fc, ec=c, c=c, size=6.2)
        T(ax, 13.2, y - 6.4, d, size=5.6, c=c if k != 'H + E' else GREY)
        arrow(ax, 22, y, 26, y)
        block(ax, 26.5, y - 4, 13, 8, 'ridge', fc='white', ec=INK, size=6.4)
        fire(ax, 38.6, y + 3.4, 0.6)
        arrow(ax, 40, y, 44, y)
        T(ax, 45, y, ['$R^2_H$', '$R^2_E$', '$R^2_{HE}$'][i], size=7.6, c=c, ha='left')
    line(ax, [53, 53], [H - 16, H - 42], c=BRAIN, lw=0.7)
    for i in range(3):
        line(ax, [51.5, 53], [H - 16 - i * 13] * 2, c=BRAIN, lw=0.7)
    arrow(ax, 53, H - 29, 56, H - 29, c=BRAIN, lw=0.7)
    img(ax, 'cortex_roi.png', 56.5, H - 37, 30, border=False, trim=True)
    T(ax, 71.5, H - 41.0, 'voxels of one ROI, one participant', size=5.6, c=BRAIN)
    T(ax, 5, 18, 'Same test videos, voxels and baseline for all three.\nE is shared by all emotions; fitted once per fold.', size=5.8, c=GREY, ha='left', va='top', linespacing=1.3)

    # b: partition
    bx = 92
    panel(ax, bx - 3, H - 1, 'b')
    T(ax, bx + 3, H - 3.6, 'Partition', size=8, w='bold', ha='left')
    vx, vy = bx + 14, H - 22
    ax.add_patch(Circle((vx - 4.2, vy), 7.4, fc=HEAD, alpha=0.28, ec=HEAD, lw=0.9, zorder=4))
    ax.add_patch(Circle((vx + 4.2, vy), 7.4, fc=RATE, alpha=0.28, ec=RATE, lw=0.9, zorder=4))
    T(ax, vx - 7.4, vy, 'head\nonly', size=5.8, c=HEAD, w='bold')
    T(ax, vx, vy, 'shared', size=5.6, c='#2A7F75', w='bold')
    T(ax, vx + 7.4, vy, 'ratings\nonly', size=5.8, c=RATE, w='bold')
    T(ax, bx + 30, H - 14, r'head only $= R^2_{HE} - R^2_E$', size=6.4, c=HEAD, ha='left')
    T(ax, bx + 30, H - 20, r'ratings only $= R^2_{HE} - R^2_H$', size=6.4, c=RATE, ha='left')
    T(ax, bx + 30, H - 26, r'shared $= R^2_H + R^2_E - R^2_{HE}$', size=6.4, ha='left')
    T(ax, bx + 30, H - 31.5, 'the three add up to $R^2_{HE}$; negatives kept', size=5.6, c=GREY, ha='left')

    # c: map
    panel(ax, bx - 3, 38, 'c')
    T(ax, bx + 3, 35.4, 'Fear, one participant', size=7.5, w='bold', ha='left')
    img(ax, 'cortex_partition.png', bx + 2, 4, 36, border=False, trim=True)
    for k, (lab, c) in enumerate((('head only', HEAD), ('shared', '#2A9D8F'), ('ratings only', RATE))):
        ax.add_patch(Rectangle((bx + 2 + k * 13, 2.0), 2.0, 2.0, fc=c, ec='none', zorder=4))
        T(ax, bx + 4.8 + k * 13, 3.0, lab, size=5.6, ha='left')

    # d: 27 emotions
    dx0 = 140
    panel(ax, dx0 - 3, 38, 'd')
    T(ax, dx0 + 3, 35.4, 'Across 27 emotions', size=7.5, w='bold', ha='left')
    sx, sy, sw, sh = dx0 + 8, 8, 28, 22
    line(ax, [sx, sx + sw], [sy, sy], c=INK, lw=0.5)
    line(ax, [sx, sx], [sy, sy + sh], c=INK, lw=0.5)
    xs = rng.uniform(0, 1, 27)
    ys = 0.15 + 0.55 * xs + rng.normal(0, 0.12, 27)
    for a, b in zip(xs, ys):
        ax.add_patch(Circle((sx + 1 + a * (sw - 2), sy + 1 + b * (sh - 3)), 0.6, fc=HEAD, ec='white', lw=0.3, zorder=5))
    line(ax, [sx + 1, sx + sw - 1], [sy + 1 + 0.15 * (sh - 3), sy + 1 + 0.70 * (sh - 3)], c=INK, lw=0.8)
    T(ax, sx + sw / 2, sy - 2.4, 'caption-unique R² of heads (3)', size=5.6)
    T(ax, sx - 2.4, sy + sh / 2, 'association − visual\nhead only (4)', size=5.4, rotation=90, linespacing=1.15)
    illus(ax, W, 1.0)
    save(fig, 'emobrain_roi_partition')
    return fig


# ---------------------------------------------------------------- 4b
def rdm(ax, x, y, s, seed, cmap, c):
    rng = np.random.default_rng(seed)
    z = rng.normal(size=(9, 3))
    d = np.linalg.norm(z[:, None] - z[None], axis=-1)
    d /= d.max()
    ax.imshow(d, extent=[x, x + s, y, y + s], cmap=cmap, vmin=-0.2, vmax=1.1, zorder=4, interpolation='nearest')
    ax.add_patch(Rectangle((x, y), s, s, fc='none', ec=c, lw=0.8, zorder=5))


def fig4b():
    W, H = 180, 66
    fig, ax = canvas(W, H)
    panel(ax, 1, H - 1, 'a')
    T(ax, 7, H - 3.6, 'Same videos, three model conditions', size=8, w='bold', ha='left')
    stack(ax, ['cowen_1374_f3.png', 'cowen_0055_f5.png', 'cowen_0366_f1.png'], 4, H - 36, 14, dx=1.8, dy=1.8)
    T(ax, 12.5, H - 39, 'Cowen videos', size=6.0, c=GREY)
    conds = [('intact', None), ('fear heads ablated', HEAD), ('random heads ablated', '#9A9A9A')]
    for i, (name, c) in enumerate(conds):
        y = H - 15 - i * 13
        arrow(ax, 22, H - 27, 27.5, y, lw=0.6)
        trapezoid(ax, 28, y - 5, 16, 10, 'VideoMAE', size=6.0)
        snow(ax, 42.6, y + 3.8, 1.0)
        T(ax, 28, y + 6.6, name, size=5.8, c=c or INK, ha='left')
        arrow(ax, 44.5, y, 48.5, y)
        tensor(ax, 49, y - 4, 13, 8, 'N × 768', fc=POOL_F, ec=POOL, c=POOL, size=6.0)
    T(ax, 4, 12.4, 'Features are read at the same last-layer position.\nRandom lists match layer, count and the size of the\nrepresentational change on VCE validation videos.', size=5.6, c=GREY, ha='left', va='top', linespacing=1.3)

    # b: RSA
    bx = 70
    panel(ax, bx - 3, H - 1, 'b')
    T(ax, bx + 3, H - 3.6, 'Distance structure (RSA)', size=8, w='bold', ha='left')
    rdm(ax, bx + 4, H - 34, 20, 1, 'Greens', POOL)
    T(ax, bx + 14, H - 11.6, 'model RDM', size=6.2, c=POOL, w='bold')
    rdm(ax, bx + 32, H - 34, 20, 2, 'Reds', BRAIN)
    T(ax, bx + 42, H - 11.6, 'ROI RDM', size=6.2, c=BRAIN, w='bold')
    T(ax, bx + 28, H - 24, 'vs', size=7, c=GREY)
    T(ax, bx + 28, H - 39, 'Spearman ρ of the upper triangles', size=6.0)
    img(ax, 'cortex_roi.png', bx + 15, 8, 24, border=False, trim=True)

    # c: encoding
    cx = 130
    panel(ax, cx - 3, H - 1, 'c')
    T(ax, cx + 3, H - 3.6, 'Voxel prediction (encoding)', size=8, w='bold', ha='left')
    tensor(ax, cx + 2, H - 30, 11, 16, 'N × 768', fc=POOL_F, ec=POOL, c=POOL, size=5.6)
    arrow(ax, cx + 13.5, H - 22, cx + 17.5, H - 22)
    block(ax, cx + 18, H - 26, 12, 8, 'ridge', fc='white', ec=INK, size=6.4)
    fire(ax, cx + 29.2, H - 18.6, 0.6)
    arrow(ax, cx + 30.5, H - 22, cx + 34.5, H - 22)
    tensor(ax, cx + 35, H - 30, 12, 16, 'N ×\nvoxels', fc=BRAIN_F, ec=BRAIN, c=BRAIN, size=5.6)
    T(ax, cx + 24, H - 36, 'refit for each condition on training folds;\ntest R² on held-out videos', size=5.6, c=GREY, linespacing=1.2)
    # extra drop
    rbox(ax, cx - 1, 6, 49, 15, fc='#FFFBF5', ec=HEAD, lw=0.7)
    T(ax, cx + 23.5, 17.4, 'analysis 5, per ROI and emotion', size=6.2, c=HEAD, w='bold')
    T(ax, cx + 23.5, 12.6, 'extra drop = (intact − fear ablated)', size=6.0)
    T(ax, cx + 23.5, 9.0, '− mean (intact − random ablated)', size=6.0)
    save(fig, 'emobrain_regional_alignment')
    return fig


if __name__ == '__main__':
    for f in (fig3a, fig3b, fig3c, fig4a, fig4b):
        f()
