import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import *
from fig1 import P1374, FEAR, SEL

REG = {'rating': dict(L=0.04, O=0.02, S=0.10, LO=0.02, LS=0.03, OS=0.07, LOS=0.02),
       'head': dict(L=0.08, O=0.04, S=0.05, LO=0.03, LS=0.04, OS=0.02, LOS=0.02)}


def r2(reg, bands):
    return sum(v for k, v in reg.items() if set(k) & set(bands))


SHARED_C = '#BDBDBD'


def illus(ax, W, y=1.6):
    T(ax, W - 2, y, 'values illustrative', size=5.4, c=GREY, ha='right', st='italic')


def title(ax, x, y, s, size=8.6):
    T(ax, x, y, s, size=size, w='bold', ha='left')


def sub(ax, x, y, s, size=7.2):
    T(ax, x, y, s, size=size, w='bold', ha='left')


def yaxis(ax, x, y0, h, vmax, ticks, label, size=5.4):
    line(ax, [x, x], [y0, y0 + h], c=INK, lw=0.5)
    for t in ticks:
        yy = y0 + t / vmax * h
        line(ax, [x - 0.8, x], [yy, yy], c=INK, lw=0.5)
        T(ax, x - 1.3, yy, f'{t:.1f}'.rstrip('0').rstrip('.') if t else '0', size=size, ha='right')
    T(ax, x - 6.5, y0 + h / 2, label, size=size, rotation=90)


def hstack(ax, x, y, h, parts, scale, labels=True, size=5.6):
    """Horizontal stacked bar. parts = [(value, colour, label)]."""
    xx = x
    for v, c, lab in parts:
        w = v * scale
        ax.add_patch(Rectangle((xx, y), w, h, fc=c, ec='white', lw=0.6, zorder=5))
        if labels and w > 4.5:
            T(ax, xx + w / 2, y + h / 2, f'{v:.2f}', size=size, c='white' if c not in (SHARED_C, HEAD_F, RATE_F) else INK, z=6)
        xx += w
    return xx


def mini_map(ax, x, y, w, h, seed, cmap, ec):
    rng = np.random.default_rng(seed)
    m = rng.normal(size=(4, 7))
    ax.imshow(m, extent=[x, x + w, y, y + h], cmap=cmap, vmin=-2.2, vmax=2.2, zorder=4, interpolation='nearest', aspect='auto')
    ax.add_patch(Rectangle((x, y), w, h, fc='none', ec=ec, lw=0.7, zorder=5))


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
    W, H = 180, 104
    fig, ax = canvas(W, H)
    title(ax, 3, H - 3.5, 'Does the full caption explain the fear heads beyond motion and object names?')
    # ---- a: inputs and two predictions
    panel(ax, 1, H - 8, 'a')
    sub(ax, 7, H - 10.4, 'Three inputs from each Cowen video, two separate predictions')
    ytop = H - 16
    stack(ax, ['cowen_1374_f3.png', 'cowen_1374_f4.png', 'cowen_1374_f1.png'], 5, ytop - 17, 15, dx=1.6, dy=1.6)
    T(ax, 13.5, ytop - 19.8, 'video 1374', size=5.8, c=GREY)
    caption_box(ax, 3, ytop - 40, 32, 17, '"A large lizard chases\na woman in a kimono ..."\n'
                                          '"A woman runs while\nholding a rope ..."\n... 20 captions', size=5.2)
    # three input rows
    rows = [('L', C_L, 'low-level visual', 'brightness, colour, motion energy', ytop - 4),
            ('O', C_O, 'object names', 'nouns: woman, lizard, rope', ytop - 18),
            ('S', C_S, 'full sentences', 'whole captions, emotion words removed', ytop - 32)]
    for k, c, name, ex, y in rows:
        badge(ax, 44, y, k, c=c, r=2.2, size=7)
        T(ax, 47.6, y + 1.5, name, size=6.6, c=c, w='bold', ha='left')
        T(ax, 47.6, y - 1.8, ex, size=5.6, c=GREY, ha='left')
    arrow(ax, 22, ytop - 6, 41.2, ytop - 4.2, lw=0.6)
    arrow(ax, 35.5, ytop - 29, 41.2, ytop - 18.5, lw=0.6)
    arrow(ax, 35.5, ytop - 32, 41.2, ytop - 32, lw=0.6)
    T(ax, 47.6, ytop - 39.6, 'O and S: frozen DeBERTa-large, mean over the 20 captions', size=5.2, c=GREY, ha='left')
    # bracket from inputs to the two ridges
    bx = 90
    line(ax, [bx, bx], [ytop - 2, ytop - 34], c=INK, lw=0.7)
    for y in (ytop - 4, ytop - 18, ytop - 32):
        line(ax, [bx - 1.5, bx], [y, y], c=INK, lw=0.7)
    # two lanes
    lanes = [(ytop - 9, HEAD, HEAD_F, 'activity of the fear heads', 'read from VideoMAE (Fig. 3a)'),
             (ytop - 27, RATE, RATE_F, 'fear rating', 'share of Cowen raters who chose fear')]
    for y, c, cf, tgt, note in lanes:
        arrow(ax, bx, y, bx + 4.5, y, lw=0.8)
        block(ax, bx + 5, y - 4, 13, 8, 'banded', 'ridge', fc='white', ec=INK, size=6.2, subsize=6.2)
        fire(ax, bx + 17, y + 3.4, 0.6)
        arrow(ax, bx + 18.5, y, bx + 22.5, y, lw=0.8)
        rbox(ax, bx + 23, y - 4.5, 28, 9, fc='white', ec=c, lw=0.9, ls=(0, (2.5, 1.2)))
        T(ax, bx + 37, y + 1.4, 'predicted', size=5.8, c=c)
        T(ax, bx + 37, y - 1.8, tgt, size=6.0, c=c, w='bold')
        T(ax, bx + 53.5, y, 'vs', size=6.2, c=GREY)
        rbox(ax, bx + 56, y - 4.5, 28, 9, fc=cf, ec=c, lw=0.9)
        T(ax, bx + 70, y + 1.4, 'actual', size=5.8, c=c)
        T(ax, bx + 70, y - 1.8, tgt, size=6.0, c=c, w='bold')
        T(ax, bx + 70, y - 7.0, note, size=5.2, c=GREY)
    T(ax, bx + 47, ytop - 38.5, 'Each combination of inputs is fitted on training videos; R² is computed on new videos.',
      size=5.6, c=INK, st='italic')
    line(ax, [3, W - 3], [ytop - 43, ytop - 43], c='#DDDDDD', lw=0.6)

    # ---- b: the key comparison
    yb = ytop - 45
    panel(ax, 1, yb, 'b')
    sub(ax, 7, yb - 2.4, 'Key comparison: add the full sentences last')
    y0, hh, vmax = 9, 30, 0.35
    yaxis(ax, 16, y0, hh, vmax, (0, 0.1, 0.2, 0.3), 'test R² on new videos')
    groups = [('fear heads', 'head', HEAD, HEAD_F, 22), ('fear rating', 'rating', RATE, RATE_F, 52)]
    for name, key, c, cf, gx in groups:
        a, b = r2(REG[key], 'LO'), r2(REG[key], 'LOS')
        ax.add_patch(Rectangle((gx, y0), 8, a / vmax * hh, fc=cf, ec=c, lw=0.8, zorder=4))
        ax.add_patch(Rectangle((gx + 11, y0), 8, b / vmax * hh, fc=c, ec=c, lw=0.8, zorder=4))
        T(ax, gx + 4, y0 + a / vmax * hh + 1.6, f'{a:.2f}', size=5.6)
        T(ax, gx + 15, y0 + b / vmax * hh + 1.6, f'{b:.2f}', size=5.6)
        T(ax, gx + 4, y0 - 2.2, 'L + O', size=5.8)
        T(ax, gx + 15, y0 - 2.2, 'L + O + S', size=5.8)
        T(ax, gx + 9.5, y0 - 5.6, name, size=6.4, c=c, w='bold')
        # gain bracket
        ya, yb2 = y0 + a / vmax * hh, y0 + b / vmax * hh
        line(ax, [gx + 8.2, gx + 20.8], [ya, ya], c=GREY, lw=0.5, ls=(0, (1.5, 1)))
        xg = gx + 21.6
        line(ax, [xg, xg], [ya, yb2], c=C_S, lw=1.0)
        line(ax, [xg - 0.6, xg], [ya, ya], c=C_S, lw=1.0)
        line(ax, [xg - 0.6, xg], [yb2, yb2], c=C_S, lw=1.0)
        T(ax, xg + 1.0, (ya + yb2) / 2 + 1.2, f'S adds', size=5.6, c=C_S, ha='left')
        T(ax, xg + 1.0, (ya + yb2) / 2 - 1.6, f'{b - a:.2f}', size=6.2, c=C_S, ha='left', w='bold')
    line(ax, [16, 84], [y0, y0], c=INK, lw=0.5)

    # ---- c: where the full R2 comes from
    cx = 96
    panel(ax, cx - 3, yb, 'c')
    sub(ax, cx + 3, yb - 2.4, 'Where the full R² comes from')
    T(ax, cx + 3, yb - 6.6, 'unique = what is lost when only that input is removed', size=5.6, c=GREY, ha='left')
    scale = 190
    for i, (name, key, c) in enumerate((('fear heads', 'head', HEAD), ('fear rating', 'rating', RATE))):
        y = yb - 17 - i * 11
        reg = REG[key]
        shared = reg['LO'] + reg['LS'] + reg['OS'] + reg['LOS']
        T(ax, cx + 13, y + 2.5, name, size=6.2, c=c, w='bold', ha='right')
        end = hstack(ax, cx + 15, y, 5, [(reg['L'], C_L, 'L'), (reg['O'], C_O, 'O'), (reg['S'], C_S, 'S'), (shared, SHARED_C, 'shared')], scale)
        T(ax, end + 1.2, y + 2.5, f'= {r2(reg, "LOS"):.2f}', size=5.8, ha='left')
    # legend
    ly = 10.5
    for k, (lab, c) in enumerate((('unique L', C_L), ('unique O', C_O), ('unique S', C_S), ('shared by two or more', SHARED_C))):
        xx = cx + 15 + [0, 15, 30, 45][k]
        ax.add_patch(Rectangle((xx, ly - 1), 2.2, 2.2, fc=c, ec='none', zorder=5))
        T(ax, xx + 3, ly + 0.1, lab, size=5.6, ha='left')
    T(ax, cx + 15, 5.4, 'The shared part is split into L–O, L–S, O–S and all three in the results table.', size=5.2, c=GREY, ha='left')
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
    W, H = 180, 100
    fig, ax = canvas(W, H)
    title(ax, 3, H - 3.5, 'In one brain region, what do the fear heads explain that the 27 human ratings do not?')
    # ---- a
    panel(ax, 1, H - 8, 'a')
    sub(ax, 7, H - 10.4, 'Predict the same voxels on new videos in three ways')
    img(ax, 'cortex_roi.png', 3, H - 38, 22, border=False, trim=True)
    T(ax, 14, H - 40.5, 'one region,\none participant', size=5.4, c=BRAIN, va='top', linespacing=1.15)
    rows = [('H', 'fear-head activity', HEAD, HEAD_F, 0.10), ('E', '27 human ratings', RATE, RATE_F, 0.08),
            ('H+E', 'both together', INK, '#F2F2F2', 0.13)]
    for i, (k, name, c, cf, v) in enumerate(rows):
        y = H - 17 - i * 10.5
        if k == 'H+E':
            rbox(ax, 44, y - 3.5, 6.5, 7, fc=HEAD_F, ec=HEAD, lw=0.8)
            T(ax, 47.25, y, 'H', size=6.4, c=HEAD)
            rbox(ax, 51, y - 3.5, 6.5, 7, fc=RATE_F, ec=RATE, lw=0.8)
            T(ax, 54.25, y, 'E', size=6.4, c=RATE)
        else:
            rbox(ax, 44, y - 3.5, 13.5, 7, fc=cf, ec=c, lw=0.8)
            T(ax, 50.75, y, k, size=6.4, c=c, w='bold')
        T(ax, 42.5, y, name, size=5.8, c=c if k != 'H+E' else INK, ha='right')
        arrow(ax, 57.8, y, 60.5, y, lw=0.7)
        if k == 'H+E':
            block(ax, 61, y - 3.5, 11, 7, 'banded', 'ridge', fc='white', ec=INK, size=5.8, subsize=5.8)
        else:
            block(ax, 61, y - 3.5, 11, 7, 'ridge', fc='white', ec=INK, size=6.2)
        fire(ax, 71.2, y + 3.0, 0.5)
        arrow(ax, 72.5, y, 76, y, lw=0.7)
        mini_map(ax, 76.5, y - 3, 11, 6, 3, 'Greys', GREY)
        T(ax, 90, y, 'vs', size=5.8, c=GREY)
        mini_map(ax, 92.5, y - 3, 11, 6, 3 + 1, 'Reds', BRAIN)
        T(ax, 106, y, '→', size=7, c=INK)
        T(ax, 108.5, y, f'$R^2_{{{k.replace("+", "")}}}$ = {v:.2f}', size=6.8, c=c, ha='left')
    yb = H - 17 - 2 * 10.5 - 6.5
    T(ax, 82, yb, 'predicted', size=5.4, c=GREY)
    T(ax, 98, yb, 'actual voxels', size=5.4, c=BRAIN)
    T(ax, 44, yb - 4.2, 'Same new videos, same voxels and the same baseline for all three. E is the same for every emotion.',
      size=5.4, c=GREY, ha='left')
    # ---- b: split
    bx = 130
    panel(ax, bx - 3, H - 8, 'b')
    sub(ax, bx + 3, H - 10.4, 'Split into three parts')
    vx, vy = bx + 13, H - 24
    ax.add_patch(Circle((vx - 4.0, vy), 7.0, fc=HEAD, alpha=0.25, ec=HEAD, lw=0.9, zorder=4))
    ax.add_patch(Circle((vx + 4.0, vy), 7.0, fc=RATE, alpha=0.25, ec=RATE, lw=0.9, zorder=4))
    T(ax, vx - 7.2, vy, '0.05', size=6.2, c=HEAD, w='bold')
    T(ax, vx, vy, '0.05', size=6.2, c='#4A4A4A', w='bold')
    T(ax, vx + 7.2, vy, '0.03', size=6.2, c=RATE, w='bold')
    T(ax, vx - 8.5, vy - 9.4, 'head only', size=5.6, c=HEAD)
    T(ax, vx, vy + 9.0, 'shared', size=5.6, c='#4A4A4A')
    T(ax, vx + 8.5, vy - 9.4, 'ratings only', size=5.6, c=RATE)
    tx = bx + 28
    T(ax, tx, H - 17, 'head only', size=5.8, c=HEAD, ha='left', w='bold')
    T(ax, tx, H - 20, '= 0.13 − 0.08', size=5.8, ha='left')
    T(ax, tx, H - 24.5, 'ratings only', size=5.8, c=RATE, ha='left', w='bold')
    T(ax, tx, H - 27.5, '= 0.13 − 0.10', size=5.8, ha='left')
    T(ax, tx, H - 32, 'shared', size=5.8, c='#4A4A4A', ha='left', w='bold')
    T(ax, tx, H - 35, '= 0.10 + 0.08 − 0.13', size=5.8, ha='left')
    T(ax, bx + 3, H - 40.5, 'The three add up to 0.13. "Shared" is overlap\nwith all 27 ratings, not only with fear.\nNegative values are kept.',
      size=5.2, c=GREY, ha='left', va='top', linespacing=1.25)
    line(ax, [3, W - 3], [H - 50, H - 50], c='#DDDDDD', lw=0.6)

    # ---- c: repeat for regions
    yc = H - 52
    panel(ax, 1, yc, 'c')
    sub(ax, 7, yc - 2.4, 'Repeat in every region (fear, one participant)')
    regs = [('visual region 1', 'visual', (0.07, 0.04, 0.02)), ('visual region 2', 'visual', (0.05, 0.04, 0.03)),
            ('association region 1', 'association', (0.02, 0.05, 0.05)), ('association region 2', 'association', (0.03, 0.04, 0.06))]
    scale = 300
    for i, (nm, grp, (ho, sh, ro)) in enumerate(regs):
        y = yc - 11 - i * 7.2
        T(ax, 36, y + 2, nm, size=5.8, ha='right', c='#1B9E77' if grp == 'visual' else '#C2477A')
        hstack(ax, 38, y, 4, [(ho, HEAD, ''), (sh, SHARED_C, ''), (ro, RATE, '')], scale, size=5.2)
    for k, (lab, c) in enumerate((('head only', HEAD), ('shared', SHARED_C), ('ratings only', RATE))):
        xx = 38 + k * 18
        ax.add_patch(Rectangle((xx, 6.0), 2.2, 2.2, fc=c, ec='none', zorder=5))
        T(ax, xx + 3, 7.1, lab, size=5.6, ha='left')
    T(ax, 38, 2.6, 'Every region keeps all three numbers; no region is labelled by one part.', size=5.2, c=GREY, ha='left')

    # ---- d: link to 3b
    dx0 = 112
    panel(ax, dx0 - 3, yc, 'd')
    sub(ax, dx0 + 3, yc - 2.4, 'Link to Fig. 3b across the 27 emotions')
    rng = np.random.default_rng(11)
    sx, sy, sw, sh = dx0 + 14, 11, 36, 25
    line(ax, [sx, sx + sw], [sy, sy], c=INK, lw=0.5)
    line(ax, [sx, sx], [sy, sy + sh], c=INK, lw=0.5)
    xs = rng.uniform(0, 1, 27)
    ys = 0.15 + 0.55 * xs + rng.normal(0, 0.12, 27)
    for a, b in zip(xs, ys):
        ax.add_patch(Circle((sx + 1 + a * (sw - 2), sy + 1 + b * (sh - 3)), 0.65, fc=HEAD, ec='white', lw=0.3, zorder=5))
    line(ax, [sx + 1, sx + sw - 1], [sy + 1 + 0.15 * (sh - 3), sy + 1 + 0.70 * (sh - 3)], c=INK, lw=0.8)
    T(ax, sx + sw / 2, sy - 2.6, 'what full sentences add to the heads (Fig. 3b, b)', size=5.4)
    T(ax, sx - 3.0, sy + sh / 2, 'head only:\nassociation − visual (c)', size=5.4, rotation=90, linespacing=1.15)
    T(ax, sx + sw + 1, sy + sh - 1, 'one dot =\none emotion', size=5.2, c=GREY, ha='left', va='top', linespacing=1.15)
    T(ax, sx + sw + 1, sy + sh - 7.5, 'slope per\nparticipant', size=5.2, c=GREY, ha='left', va='top', linespacing=1.15)
    illus(ax, W, 1.2)
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


RAND = [(2, 5), (3, 9), (5, 2), (8, 11), (9, 7), (10, 1)]


def fig4b():
    W, H = 180, 106
    fig, ax = canvas(W, H)
    title(ax, 3, H - 3.5, 'Comparing a model with a brain region, and what happens when the fear heads are removed')
    # ---- a: model versions
    panel(ax, 1, H - 8, 'a')
    sub(ax, 7, H - 10.4, 'Model versions, all fed the same Cowen videos')
    T(ax, 7, H - 16, 'Analysis 4 (before vs after emotion training)', size=6.2, c=MODEL, w='bold', ha='left')
    for i, (nm, note) in enumerate((('video only', 'self-supervised on VCE'), ('emotion-trained', 'fine-tuned on 27 ratings'))):
        x = 9 + i * 38
        trapezoid(ax, x, H - 29, 13, 9, '', size=6)
        snow(ax, x + 11.6, H - 21.2, 0.9)
        T(ax, x + 15, H - 22.5, nm, size=6.0, ha='left', w='bold')
        T(ax, x + 15, H - 25.5, note, size=5.2, c=GREY, ha='left')
    T(ax, 7, H - 35, 'Analysis 5 (emotion-trained model, heads set to 0)', size=6.2, c=HEAD, w='bold', ha='left')
    conds = [('intact', (), ()), ('fear heads off', SEL, ()), ('matched random off', (), RAND)]
    for i, (nm, sel, msk) in enumerate(conds):
        x = 9 + i * 24
        head_grid(ax, x, H - 53, cell=1.25, gap=0.15, sel=sel, masked=msk)
        T(ax, x + 8.3, H - 55.8, nm, size=5.8, c=HEAD if i == 1 else (GREY if i == 2 else INK), w='bold')
    T(ax, 7, H - 60, '12 layers (columns) × 12 heads. Orange: fear heads; grey: random heads matched in layer, number\nand size of the change on VCE validation videos.',
      size=5.2, c=GREY, ha='left', va='top', linespacing=1.25)
    T(ax, 7, H - 67.5, 'Every version gives one 768-value vector per video from the last layer.', size=5.6, c=POOL, ha='left')

    # ---- b: two comparisons
    bx = 86
    panel(ax, bx - 3, H - 8, 'b')
    sub(ax, bx + 3, H - 10.4, 'Two ways to compare one version with one region')
    T(ax, bx + 3, H - 16, 'RSA: are the same videos similar?', size=6.2, w='bold', ha='left')
    rdm(ax, bx + 5, H - 34, 14, 1, 'Greens', POOL)
    T(ax, bx + 12, H - 36.5, 'model', size=5.6, c=POOL)
    T(ax, bx + 23.5, H - 27, 'vs', size=6, c=GREY)
    rdm(ax, bx + 28, H - 34, 14, 2, 'Reds', BRAIN)
    T(ax, bx + 35, H - 36.5, 'region', size=5.6, c=BRAIN)
    T(ax, bx + 44, H - 27, '→  Spearman ρ', size=6.2, ha='left')
    T(ax, bx + 5, H - 40.5, 'each cell = how different two videos are', size=5.2, c=GREY, ha='left')
    T(ax, bx + 3, H - 47, 'Encoding: can the vector predict the voxels?', size=6.2, w='bold', ha='left')
    rbox(ax, bx + 5, H - 58, 12, 7, fc=POOL_F, ec=POOL, lw=0.8)
    T(ax, bx + 11, H - 54.5, '768 values', size=5.4, c=POOL)
    arrow(ax, bx + 17.5, H - 54.5, bx + 20.5, H - 54.5, lw=0.7)
    block(ax, bx + 21, H - 58, 10, 7, 'ridge', fc='white', ec=INK, size=6.0)
    fire(ax, bx + 30.2, H - 51.4, 0.5)
    arrow(ax, bx + 31.5, H - 54.5, bx + 34.5, H - 54.5, lw=0.7)
    mini_map(ax, bx + 35, H - 57.5, 10, 6, 5, 'Greys', GREY)
    T(ax, bx + 47.5, H - 54.5, 'vs', size=5.8, c=GREY)
    mini_map(ax, bx + 50, H - 57.5, 10, 6, 6, 'Reds', BRAIN)
    T(ax, bx + 62, H - 54.5, '→  R²', size=6.2, ha='left')
    T(ax, bx + 5, H - 62, 'ridge refitted for each version on training videos; scored on new videos', size=5.2, c=GREY, ha='left')
    line(ax, [3, W - 3], [H - 71, H - 71], c='#DDDDDD', lw=0.6)

    # ---- c: analysis 5 readout
    yc = H - 73
    panel(ax, 1, yc, 'c')
    sub(ax, 7, yc - 2.4, 'Analysis 5 result for one emotion: extra drop = drop with fear heads off − drop with matched random heads off')
    y0, hh, vmax = 8.5, 12.5, 0.22
    groups = [('association region', (0.20, 0.12, 0.17)), ('visual region', (0.18, 0.15, 0.16))]
    for g, (gname, (vi, vf, vr)) in enumerate(groups):
        gx = 9 + g * 88
        T(ax, gx, y0 + hh + 4.6, gname, size=6.2, ha='left', w='bold', c='#C2477A' if g == 0 else '#1B9E77')
        rr = np.random.default_rng(20 + g)
        for v2 in vr + rr.normal(0, 0.012, 14):
            ax.add_patch(Circle((gx + 18 + 3.25 + rr.uniform(-2.2, 2.2), y0 + v2 / vmax * hh), 0.35, fc='#555555', ec='none', zorder=6))
        for j, (lab, v, fc, ec) in enumerate((('intact', vi, POOL_F, POOL), ('fear off', vf, HEAD, HEAD), ('random off', vr, '#C9C9C9', '#8A8A8A'))):
            xx = gx + j * 9
            ax.add_patch(Rectangle((xx, y0), 6.5, v / vmax * hh, fc=fc, ec=ec, lw=0.7, zorder=4))
            T(ax, xx + 3.25, y0 - 2.0, lab, size=5.0)
            T(ax, xx + 3.25, y0 + v / vmax * hh + (3.0 if j == 2 else 1.4), f'{v:.2f}', size=5.0)
        line(ax, [gx - 0.5, gx + 26], [y0, y0], c=INK, lw=0.5)
        tx = gx + 30
        T(ax, tx, y0 + 11, f'drop, fear off = {vi - vf:.2f}', size=5.8, ha='left', c=HEAD)
        T(ax, tx, y0 + 7, f'drop, random off = {vi - vr:.2f}', size=5.8, ha='left', c='#6E6E6E')
        T(ax, tx, y0 + 2.6, f'extra drop = {(vi - vf) - (vi - vr):.2f}', size=6.2, ha='left', w='bold')
    T(ax, 9, y0 - 5.6, 'Dots: individual matched random lists (bar = their mean). Computed for RSA (ρ) and for encoding (R²);'
      ' regions are compared by subtracting their extra drops.', size=5.2, c=GREY, ha='left')
    illus(ax, W, 1.0)
    save(fig, 'emobrain_regional_alignment')
    return fig


if __name__ == '__main__':
    for f in (fig3a, fig3b, fig3c, fig4a, fig4b):
        f()
