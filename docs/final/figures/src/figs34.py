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
        elif labels:
            T(ax, xx + w / 2, y + h + 1.5, f'{v:.2f}', size=size - 0.6, c=c, z=6)
        xx += w
    return xx


def mini_map(ax, x, y, w, h, seed, cmap, ec):
    rng = np.random.default_rng(seed)
    m = rng.normal(size=(4, 7))
    ax.imshow(m, extent=[x, x + w, y, y + h], cmap=cmap, vmin=-2.2, vmax=2.2, zorder=4, interpolation='nearest', aspect='auto')
    ax.add_patch(Rectangle((x, y), w, h, fc='none', ec=ec, lw=0.7, zorder=5))


# ---------------------------------------------------------------- 3a
def ring(ax, x, y, cell, gap, b, h, c=HEAD, lw=1.1):
    """Outline one cell of a head_grid drawn at (x, y)."""
    xx, yy = x + (b - 1) * (cell + gap), y + (11 - (h - 1)) * cell
    ax.add_patch(Rectangle((xx - 0.15, yy - 0.15), cell + 0.3, cell + 0.3, fc='none', ec=c, lw=lw, zorder=8))


def fig3a():
    W, H = 180, 112
    fig, ax = canvas(W, H)
    rng = np.random.default_rng(7)
    title(ax, 3, H - 3.5, 'Which heads does the model rely on when it predicts fear across videos?')

    # ---- a: rank on validation videos
    panel(ax, 1, H - 8, 'a')
    sub(ax, 7, H - 10.4, 'Rank all 144 heads on VCE validation videos (illustrative values)')
    y = H - 35
    tensor(ax, 4, y + 3, 13, 10, 'validation\nvideos', size=6.0)
    arrow(ax, 17.5, y + 8, 21.5, y + 8)
    hb, hh = 9, 4          # example head h = block 9, head 4 (one of the fear-list heads in b)
    keep_h = [True, False, True]
    mrng = np.random.default_rng(70)
    cell, gap = 0.85, 0.1
    for k in range(3):
        x0 = 22 + k * 13
        others = [(b + 1, q + 1) for b in range(12) for q in range(12) if (b + 1, q + 1) != (hb, hh)]
        n_off = 72 if keep_h[k] else 71          # exactly 72 of 144 heads off in every mask
        masked = [others[i] for i in mrng.choice(143, n_off, replace=False)] + ([] if keep_h[k] else [(hb, hh)])
        head_grid(ax, x0, y + 2.5, cell=cell, gap=gap, masked=masked)
        ring(ax, x0, y + 2.5, cell, gap, hb, hh)
        T(ax, x0 + 5.6, y + 0.4, ['mask 1', 'mask 2', 'mask M'][k], size=5.6, c=GREY)
        T(ax, x0 + 5.6, y - 3.0, ['r = 0.41', 'r = 0.33', 'r = 0.39'][k], size=6.0, c=RATE)
        T(ax, x0 + 5.6, y - 5.9, ['h on', 'h off', 'h on'][k], size=5.4, c=HEAD)
    T(ax, 61.4, y + 7.6, '…', size=7, c=GREY)
    T(ax, 22, y + 19.8, 'Each mask switches off 72 of 144 heads (grey) for all validation videos.', size=5.8, c=GREY, ha='left')
    T(ax, 22, y + 16.6, 'r = Pearson r between predicted and rated fear across those videos.', size=5.8, c=GREY, ha='left')
    # worked example for head h
    ex = 64
    T(ax, ex, y + 9.0, 'one head h (orange outline)', size=6.0, c=HEAD, w='bold', ha='left')
    T(ax, ex, y + 5.0, 'masks with h on:   mean r = 0.40', size=5.8, ha='left')
    T(ax, ex, y + 1.6, 'masks with h off:  mean r = 0.34', size=5.8, ha='left')
    T(ax, ex, y - 2.6, 'contribution of h = 0.40 − 0.34 = 0.06', size=6.0, ha='left', w='bold')
    T(ax, ex, y - 6.4, '0 means "as useful as an average head\nwhen half are off", not "no effect"',
      size=5.2, c=GREY, ha='left', va='top', linespacing=1.2)
    # ranked bars
    yr = y - 26.5
    vals = np.sort(rng.gamma(1.4, 0.004, 144))[::-1]
    vals[:4] += 0.012
    vals = vals - vals.mean()                     # contributions average to 0 over the 144 heads
    bw = 81.0 / 144
    for i, v in enumerate(vals):
        h = 300 * v
        ax.add_patch(Rectangle((4 + i * bw, yr if h >= 0 else yr + h), bw * 0.8, abs(h), fc=HEAD if i < 4 else '#C9CFD6',
                               ec='none', zorder=4))
    line(ax, [3.6, 4 + 144 * bw], [yr, yr], c=INK, lw=0.5)
    T(ax, 4 + 144 * bw + 1.0, yr, '0 = average head', size=5.2, c=GREY, ha='left')
    T(ax, 10.5, yr + 300 * vals[0] + 1.6, 'top K = fear list (candidates)', size=6.0, c=HEAD, ha='left', va='bottom')
    T(ax, 4 + 144 * bw, yr + 4.6, 'all 144 heads, ranked by contribution', size=5.6, c=GREY, ha='right', va='bottom')

    # ---- b: where the list sits
    bx = 100
    panel(ax, bx - 3, H - 8, 'b')
    sub(ax, bx + 3, H - 10.4, 'Where the fear-list heads sit (example)')
    gy = H - 50
    gw, gh = head_grid(ax, bx + 8, gy, cell=2.1, gap=0.45, sel=SEL)
    ring(ax, bx + 8, gy, 2.1, 0.45, hb, hh, c=INK, lw=0.9)
    for b in range(12):
        T(ax, bx + 8 + b * 2.55 + 1.05, gy + gh + 1.6, str(b + 1), size=5.4, c=HEAD if b + 1 in (3, 8, 9) else GREY,
          w='bold' if b + 1 in (3, 8, 9) else 'normal')
    T(ax, bx + 8 + gw / 2, gy + gh + 4.8, 'layer (input → output)', size=6.0, c=MODEL)
    T(ax, bx + 5.6, gy + gh / 2, '12 heads per layer', size=5.6, c=GREY, rotation=90)
    yd = gy - 4.5
    line(ax, [bx + 8, bx + 8 + gw], [yd, yd], c='#CCCCCC', lw=0.5)
    for b, n in {3: 1, 8: 1, 9: 2}.items():
        for k in range(n):
            ax.add_patch(Circle((bx + 8 + (b - 1) * 2.55 + 1.05, yd + k * 2.0), 0.75, fc=HEAD, ec=INK, lw=0.4, zorder=6))
    T(ax, bx + 8 + gw + 1.5, gy + gh - 7.2, 'black outline\n= head h in a', size=5.0, c=GREY, ha='left', va='top', linespacing=1.15)
    T(ax, bx + 8 + gw / 2, yd - 3.4, 'heads per layer: 1 in layer 3, 1 in layer 8, 2 in layer 9', size=5.4, c=GREY)
    T(ax, bx + 8 + gw / 2, yd - 6.6, 'Depth is not read as abstraction.', size=5.4, c=GREY, st='italic')
    line(ax, [3, W - 3], [H - 66, H - 66], c='#DDDDDD', lw=0.6)

    # ---- c: two claims on new videos
    yc = H - 68
    panel(ax, 1, yc, 'c')
    sub(ax, 7, yc - 2.4, 'Check on new VCE test videos, with the intact model: two separate claims (illustrative values)')
    # c1
    sc1 = 130
    T(ax, 7, yc - 8.2, '1. Did the fear list contribute?', size=6.4, w='bold', ha='left')
    T(ax, 7, yc - 11.2, 'drop in fear r when the list is switched off', size=5.4, c=GREY, ha='left')
    b0, sc = 11.5, 160
    for j, (lab, v, fc) in enumerate((('fear list off', 0.12, HEAD), ('matched random\nlists off', 0.03, '#C9C9C9'))):
        xx = 12 + j * 14
        ax.add_patch(Rectangle((xx, b0), 8, v * sc1, fc=fc, ec='none', zorder=4))
        T(ax, xx + 4, b0 + v * sc1 + (4.0 if j == 1 else 1.4), f'{v:.2f}', size=5.4)
        T(ax, xx + 4, b0 - 1.6, lab, size=5.2, va='top', linespacing=1.1)
    rr = np.random.default_rng(31)
    dv = rr.normal(0, 0.008, 14)
    for v2 in 0.03 + dv - dv.mean():
        ax.add_patch(Circle((26 + 4 + rr.uniform(-3, 3), b0 + v2 * sc1), 0.35, fc='#555555', ec='none', zorder=6))
    line(ax, [10, 38], [b0, b0], c=INK, lw=0.5)
    T(ax, 42, b0 + 15, 'same layers and number;', size=5.4, c=GREY, ha='left')
    T(ax, 42, b0 + 12, 'many lists (dots), bar = mean', size=5.4, c=GREY, ha='left')
    T(ax, 42, b0 + 6.5, 'fear list drops more →', size=5.8, ha='left')
    T(ax, 42, b0 + 3.3, '"the list contributed to', size=5.8, ha='left', w='bold')
    T(ax, 42, b0 + 0.3, 'fear prediction"', size=5.8, ha='left', w='bold')
    # c2
    cx = 92
    T(ax, cx, yc - 8.2, '2. Is it special to fear?', size=6.4, w='bold', ha='left')
    T(ax, cx, yc - 11.2, 'still evaluating fear r: switch off each emotion\'s list, after subtracting its random drop',
      size=5.4, c=GREY, ha='left')
    # mini 27 x 27 table icon
    mx, my, ms = cx + 1, b0 + 1, 2.0
    for i in range(6):
        for j in range(6):
            fc = '#F3E3CF' if j == 0 else '#F2F2F2'
            ax.add_patch(Rectangle((mx + j * ms, my + (5 - i) * ms), ms, ms, fc=fc, ec='white', lw=0.4, zorder=4))
    ax.add_patch(Rectangle((mx, my), ms, 6 * ms, fc='none', ec=HEAD, lw=0.9, zorder=5))
    T(ax, mx + 3 * ms, my + 6 * ms + 1.6, 'fear column', size=5.0, c=HEAD)
    T(ax, mx + 3 * ms, my - 1.6, 'list off × emotion', size=4.8, c=GREY, va='top')
    T(ax, mx + 3 * ms, my - 3.8, '(27 × 27)', size=4.8, c=GREY, va='top')
    lists = [('fear', 0.09), ('anxiety', 0.05), ('horror', 0.04), ('amuse.', 0.01), ('awe', 0.00), ('joy', 0.01)]
    lx = cx + 17
    for i, (nm, v) in enumerate(lists):
        xx = lx + i * 6.6
        ax.add_patch(Rectangle((xx, b0), 5, max(0.25, v * sc), fc=HEAD if i == 0 else '#E8C9A3', ec='none', zorder=4))
        T(ax, xx + 2.5, b0 + v * sc + 1.4, f'{v:.2f}', size=5.0)
        T(ax, xx + 2.5, b0 - 1.6, nm + '\nlist', size=5.0, va='top', linespacing=1.05, c=HEAD if i == 0 else INK)
    T(ax, lx + 6 * 6.6 - 0.6, b0 + 7, '…', size=8, c=GREY)
    line(ax, [lx - 1, lx + 6 * 6.6 + 2], [b0, b0], c=INK, lw=0.5)
    tx = lx + 6 * 6.6 + 4
    T(ax, tx, b0 + 15, 'own list 0.09', size=5.6, ha='left')
    T(ax, tx, b0 + 12, '− others\' mean 0.02', size=5.6, ha='left')
    T(ax, tx, b0 + 8.6, '= 0.07 →', size=5.8, ha='left')
    T(ax, tx, b0 + 5.4, '"especially important', size=5.8, ha='left', w='bold')
    T(ax, tx, b0 + 2.4, 'for fear"', size=5.8, ha='left', w='bold')
    T(ax, cx, 1.8, 'The test for claim 2 is fixed before testing; by list relabelling, one emotion alone cannot pass correction.',
      size=5.2, c=GREY, ha='left')
    save(fig, 'emobrain_head_layers')
    return fig


# ---------------------------------------------------------------- 3b
def fig3b():
    W, H = 180, 110
    fig, ax = canvas(W, H)
    title(ax, 3, H - 3.5, 'Does the full caption explain the fear-list heads beyond motion and object names?')
    # ---- a: inputs and two predictions
    panel(ax, 1, H - 8, 'a')
    sub(ax, 7, H - 10.4, 'Inputs from each Cowen video, two separate predictions')
    ytop = H - 16
    stack(ax, ['cowen_1374_f3.png', 'cowen_1374_f4.png', 'cowen_1374_f1.png'], 5, ytop - 17, 15, dx=1.6, dy=1.6)
    T(ax, 13.5, ytop - 19.8, 'video 1374', size=5.8, c=GREY)
    caption_box(ax, 3, ytop - 41, 32, 17, '"A large lizard chases\na woman in a kimono ..."\n'
                                          '"A woman runs while\nholding a rope ..."\n... 20 captions', size=5.2)
    rows = [('L', C_L, 'low-level visual', 'brightness, colour, motion energy', ytop - 3),
            ('O', C_O, 'object names', 'nouns: woman, lizard, rope', ytop - 14),
            ('S', C_S, 'full sentences', 'whole captions, as written', ytop - 25),
            ('C', GREY, 'common variables', 'caption length; emotion words undecided', ytop - 36)]
    for k, c, name, ex, y in rows:
        badge(ax, 44, y, k, c=c, r=2.2, size=7)
        T(ax, 47.6, y + 1.5, name, size=6.6, c=c, w='bold', ha='left')
        T(ax, 47.6, y - 1.8, ex, size=5.6, c=GREY, ha='left')
    arrow(ax, 22, ytop - 6, 41.2, ytop - 3.2, lw=0.6)
    arrow(ax, 35.5, ytop - 30, 41.2, ytop - 14.5, lw=0.6)
    arrow(ax, 35.5, ytop - 32, 41.2, ytop - 25.2, lw=0.6)
    arrow(ax, 35.5, ytop - 35, 41.2, ytop - 36, lw=0.6)
    T(ax, 47.6, ytop - 40.6, 'O and S: frozen DeBERTa-large, mean over the 20 captions.\n'
                             'C: in every model;\nthe baseline model has C only.', size=5.0, c=GREY, ha='left',
      va='top', linespacing=1.2)
    # bracket from inputs to the two ridges
    bx = 90
    line(ax, [bx, bx], [ytop - 1, ytop - 38], c=INK, lw=0.7)
    for k, c, name, ex, y in rows:
        line(ax, [bx - 1.5, bx], [y, y], c=INK, lw=0.7)
    lanes = [(ytop - 9, HEAD, HEAD_F, 'activity of the fear-list heads', 'intact VideoMAE on this video;\nhead list from Fig. 3a'),
             (ytop - 27, RATE, RATE_F, 'fear rating', 'share of Cowen raters who chose fear')]
    for y, c, cf, tgt, note in lanes:
        arrow(ax, bx, y, bx + 4.5, y, lw=0.8)
        block(ax, bx + 5, y - 4, 13, 8, 'banded', 'ridge', fc='white', ec=INK, size=6.2, subsize=6.2)
        fire(ax, bx + 17, y + 3.4, 0.6)
        arrow(ax, bx + 18.5, y, bx + 22.5, y, lw=0.8)
        rbox(ax, bx + 23, y - 4.5, 29, 9, fc='white', ec=c, lw=0.9, ls=(0, (2.5, 1.2)))
        T(ax, bx + 37.5, y + 1.4, 'predicted', size=5.8, c=c)
        T(ax, bx + 37.5, y - 1.8, tgt, size=5.8, c=c, w='bold')
        T(ax, bx + 54.2, y, 'vs', size=6.2, c=GREY)
        rbox(ax, bx + 56.5, y - 4.5, 29, 9, fc=cf, ec=c, lw=0.9)
        T(ax, bx + 71, y + 1.4, 'actual', size=5.8, c=c)
        T(ax, bx + 71, y - 1.8, tgt, size=5.8, c=c, w='bold')
        T(ax, bx + 71, y - 5.6, note, size=5.2, c=GREY, va='top', linespacing=1.15)
    T(ax, bx + 11, ytop - 40.6, 'Cowen videos except the 72 MC test videos.\n'
                               'Each model is fitted on training videos; R² is computed on new videos.', size=5.4, c=INK,
      st='italic', ha='left', va='top', linespacing=1.2)
    line(ax, [3, W - 3], [ytop - 49, ytop - 49], c='#DDDDDD', lw=0.6)

    # ---- b: the key comparison
    yb = ytop - 51
    panel(ax, 1, yb, 'b')
    sub(ax, 7, yb - 2.4, 'Key comparison: add the full sentences last (illustrative values)')
    y0, hh, vmax = 9, 28, 0.35
    yaxis(ax, 16, y0, hh, vmax, (0, 0.1, 0.2, 0.3), 'test R² on new videos')
    groups = [('fear-list heads', 'head', HEAD, HEAD_F, 22), ('fear rating', 'rating', RATE, RATE_F, 52)]
    for name, key, c, cf, gx in groups:
        a, b = r2(REG[key], 'LO'), r2(REG[key], 'LOS')
        ax.add_patch(Rectangle((gx, y0), 8, a / vmax * hh, fc=cf, ec=c, lw=0.8, zorder=4))
        ax.add_patch(Rectangle((gx + 11, y0), 8, b / vmax * hh, fc=c, ec=c, lw=0.8, zorder=4))
        T(ax, gx + 4, y0 + a / vmax * hh + 1.6, f'{a:.2f}', size=5.6)
        T(ax, gx + 15, y0 + b / vmax * hh + 1.6, f'{b:.2f}', size=5.6)
        T(ax, gx + 4, y0 - 2.2, 'C + L + O', size=5.4)
        T(ax, gx + 15, y0 - 2.2, 'C + L + O + S', size=5.4)
        T(ax, gx + 9.5, y0 - 5.6, name, size=6.4, c=c, w='bold')
        ya, yb2 = y0 + a / vmax * hh, y0 + b / vmax * hh
        line(ax, [gx + 8.2, gx + 20.8], [ya, ya], c=GREY, lw=0.5, ls=(0, (1.5, 1)))
        xg = gx + 21.6
        line(ax, [xg, xg], [ya, yb2], c=C_S, lw=1.0)
        line(ax, [xg - 0.6, xg], [ya, ya], c=C_S, lw=1.0)
        line(ax, [xg - 0.6, xg], [yb2, yb2], c=C_S, lw=1.0)
        T(ax, xg + 1.0, (ya + yb2) / 2 + 1.2, 'S adds', size=5.6, c=C_S, ha='left')
        T(ax, xg + 1.0, (ya + yb2) / 2 - 1.6, f'{b - a:.2f}', size=6.2, c=C_S, ha='left', w='bold')
    line(ax, [16, 84], [y0, y0], c=INK, lw=0.5)

    # ---- c: where the full R2 comes from
    cx = 96
    panel(ax, cx - 3, yb, 'c')
    sub(ax, cx + 3, yb - 2.4, 'Where the full R² comes from (illustrative values)')
    T(ax, cx + 3, yb - 6.6, 'unique = what is lost when only that input is removed;\nbaseline R² with C only is 0.00 in this example',
      size=5.4, c=GREY, ha='left', va='top', linespacing=1.2)
    scale = 190
    for i, (name, key, c) in enumerate((('fear-list heads', 'head', HEAD), ('fear rating', 'rating', RATE))):
        y = yb - 19 - i * 10
        reg = REG[key]
        shared = reg['LO'] + reg['LS'] + reg['OS'] + reg['LOS']
        T(ax, cx + 13.5, y + 2.5, name, size=6.0, c=c, w='bold', ha='right')
        end = hstack(ax, cx + 15, y, 5, [(reg['L'], C_L, 'L'), (reg['O'], C_O, 'O'), (reg['S'], C_S, 'S'), (shared, SHARED_C, 'shared')], scale)
        T(ax, end + 1.2, y + 2.5, f'= {r2(reg, "LOS"):.2f}', size=5.8, ha='left')
    ly = 11.5
    for k, (lab, c) in enumerate((('unique L', C_L), ('unique O', C_O), ('unique S', C_S), ('shared by two or more', SHARED_C))):
        xx = cx + 15 + [0, 15, 30, 45][k]
        ax.add_patch(Rectangle((xx, ly - 1), 2.2, 2.2, fc=c, ec='none', zorder=5))
        T(ax, xx + 3, ly + 0.1, lab, size=5.6, ha='left')
    T(ax, cx + 15, 7.0, 'The results table splits the shared part into\nL and O, L and S, O and S, and all three.',
      size=5.2, c=GREY, ha='left', va='top', linespacing=1.2)
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
    W, H = 180, 104
    fig, ax = canvas(W, H)
    title(ax, 3, H - 3.5, 'In one brain region, how much do the fear-list heads and the 27 ratings explain, separately and together?',
          size=8.2)
    # ---- a
    panel(ax, 1, H - 8, 'a')
    sub(ax, 7, H - 10.4, 'Predict the same voxels on new videos in three ways')
    img(ax, 'cortex_roi.png', 3, H - 38, 22, border=False, trim=True)
    T(ax, 14, H - 40.5, 'one region,\none participant', size=5.4, c=BRAIN, va='top', linespacing=1.15)
    rows = [('H', 'fear-list head activity', HEAD, HEAD_F, 0.10, 13), ('E', '27 Cowen ratings', RATE, RATE_F, 0.08, 23),
            ('H+E', 'both together', INK, '#F2F2F2', 0.13, 33)]
    for i, (k, name, c, cf, v, seed) in enumerate(rows):
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
        mini_map(ax, 76.5, y - 3, 11, 6, seed, 'Greys', GREY)
        T(ax, 90, y, 'vs', size=5.8, c=GREY)
        mini_map(ax, 92.5, y - 3, 11, 6, 4, 'Reds', BRAIN)
        T(ax, 106, y, '→', size=7, c=INK)
        T(ax, 108.5, y, f'$R^2_{{{k.replace("+", "")}}}$ = {v:.2f}', size=6.8, c=c, ha='left')
    yb = H - 17 - 2 * 10.5 - 6.5
    T(ax, 82, yb, 'predicted', size=5.4, c=GREY)
    T(ax, 98, yb, 'actual voxels', size=5.4, c=BRAIN)
    T(ax, 90, yb - 2.6, '(new videos × voxels)', size=5.0, c=GREY)
    T(ax, 44, yb - 6.2, 'Ridge fitted on training videos. R² on the same new videos and voxels, against the training-video mean.\n'
                        'E is the same for every emotion. Ratings are Cowen raters\', not the participant\'s.',
      size=5.2, c=GREY, ha='left', va='top', linespacing=1.2)
    # ---- b: split
    bx = 130
    panel(ax, bx - 3, H - 8, 'b')
    sub(ax, bx + 3, H - 10.4, 'Split into three parts')
    vx, vy = bx + 11, H - 24
    ax.add_patch(Circle((vx - 3.7, vy), 6.5, fc=HEAD, alpha=0.25, ec=HEAD, lw=0.9, zorder=4))
    ax.add_patch(Circle((vx + 3.7, vy), 6.5, fc=RATE, alpha=0.25, ec=RATE, lw=0.9, zorder=4))
    T(ax, vx - 6.8, vy, '0.05', size=6.0, c=HEAD, w='bold')
    T(ax, vx, vy, '0.05', size=6.0, c='#4A4A4A', w='bold')
    T(ax, vx + 6.8, vy, '0.03', size=6.0, c=RATE, w='bold')
    T(ax, vx - 6.5, vy - 8.6, 'head only', size=5.4, c=HEAD)
    T(ax, vx, vy + 8.4, 'shared', size=5.4, c='#4A4A4A')
    T(ax, vx + 6.5, vy - 8.6, 'ratings only', size=5.4, c=RATE)
    tx = bx + 25
    T(ax, tx, H - 16.5, 'head only', size=5.8, c=HEAD, ha='left', w='bold')
    T(ax, tx, H - 19.7, r'$= R^2_{HE} - R^2_{E}$ = 0.13 − 0.08', size=5.6, ha='left')
    T(ax, tx, H - 24.2, 'ratings only', size=5.8, c=RATE, ha='left', w='bold')
    T(ax, tx, H - 27.4, r'$= R^2_{HE} - R^2_{H}$ = 0.13 − 0.10', size=5.6, ha='left')
    T(ax, tx, H - 31.9, 'shared', size=5.8, c='#4A4A4A', ha='left', w='bold')
    T(ax, tx, H - 35.1, r'$= R^2_{H} + R^2_{E} - R^2_{HE}$', size=5.6, ha='left')
    T(ax, tx, H - 38.1, '= 0.10 + 0.08 − 0.13', size=5.6, ha='left')
    T(ax, bx + 3, H - 42.0, 'The three add up to 0.13. "Shared" is overlap\nwith all 27 ratings, not only with fear.\nNegative values are kept.',
      size=5.2, c=GREY, ha='left', va='top', linespacing=1.25)
    line(ax, [3, W - 3], [H - 57, H - 57], c='#DDDDDD', lw=0.6)

    # ---- c: repeat for regions, bars side by side
    yc = H - 59
    panel(ax, 1, yc, 'c')
    sub(ax, 7, yc - 2.4, 'Repeat in every region (fear, one participant, illustrative values)')
    regs = [('visual\nregion 1', 'visual', (0.07, 0.04, 0.02)), ('visual\nregion 2', 'visual', (0.05, 0.04, 0.03)),
            ('association\nregion 1 (in a)', 'association', (0.05, 0.05, 0.03)),
            ('association\nregion 2', 'association', (0.03, -0.01, 0.06))]
    z0, sc = 15, 260
    line(ax, [10, 104], [z0, z0], c=INK, lw=0.5)
    T(ax, 9, z0, '0', size=5.2, ha='right')
    for i, (nm, grp, vals) in enumerate(regs):
        gx = 14 + i * 23
        for j, (v, c) in enumerate(zip(vals, (HEAD, SHARED_C, RATE))):
            xx = gx + j * 5.6
            h = v * sc
            ax.add_patch(Rectangle((xx, z0 if h >= 0 else z0 + h), 4.6, abs(h), fc=c, ec='none', zorder=4))
            T(ax, xx + 2.3, z0 + h + (1.3 if h >= 0 else -1.5), f'{v:.2f}', size=4.8)
        T(ax, gx + 7.9, z0 - 5.2, nm, size=5.4, c='#1B9E77' if grp == 'visual' else '#C2477A', va='top', linespacing=1.1)
    for k, (lab, c) in enumerate((('head only', HEAD), ('shared', SHARED_C), ('ratings only', RATE))):
        xx = 60 + k * 15
        ax.add_patch(Rectangle((xx, yc - 8.0), 2.2, 2.2, fc=c, ec='none', zorder=5))
        T(ax, xx + 3, yc - 6.9, lab, size=5.4, ha='left')
    T(ax, 10, 2.4, 'Every region keeps all three numbers side by side; values can be negative.', size=5.2, c=GREY, ha='left')

    # ---- d: link to 3b
    dx0 = 112
    panel(ax, dx0 - 3, yc, 'd')
    sub(ax, dx0 + 3, yc - 2.4, 'Link to Fig. 3b across the 27 emotions')
    rng = np.random.default_rng(11)
    sx, sy, sw, sh = dx0 + 14, 11, 34, 28
    xmax, ylo, yhi = 0.12, -0.05, 0.07
    X = lambda v: sx + v / xmax * sw
    Y = lambda v: sy + (v - ylo) / (yhi - ylo) * sh
    line(ax, [sx, sx + sw], [sy, sy], c=INK, lw=0.5)
    line(ax, [sx, sx], [sy, sy + sh], c=INK, lw=0.5)
    line(ax, [sx, sx + sw], [Y(0), Y(0)], c=GREY, lw=0.5, ls=(0, (2, 1.2)))
    T(ax, sx + 0.8, Y(0) + 1.2, '0', size=5.0, ha='left', c=GREY)
    xs = rng.uniform(0.005, 0.115, 26)
    ys = -0.045 + 0.7 * xs + rng.normal(0, 0.012, 26)
    for a, b in zip(xs, ys):
        ax.add_patch(Circle((X(a), Y(b)), 0.6, fc='#F2B56B', ec='white', lw=0.3, zorder=5))
    fx, fy = 0.05, (0.05 + 0.03) / 2 - (0.07 + 0.05) / 2
    ax.add_patch(Circle((X(fx), Y(fy)), 0.85, fc=HEAD, ec=INK, lw=0.5, zorder=6))
    T(ax, X(fx) + 1.4, Y(fy) - 1.6, 'fear', size=5.4, c=HEAD, w='bold', ha='left')
    line(ax, [X(0.0), X(0.12)], [Y(-0.045), Y(-0.045 + 0.7 * 0.12)], c=INK, lw=0.8)
    T(ax, sx + sw / 2, sy - 2.6, 'what full sentences add to the heads (as in Fig. 3b, b)', size=5.4)
    T(ax, sx - 3.6, sy + sh / 2, 'head only:\nassociation − visual (c)', size=5.4, rotation=90, linespacing=1.15)
    T(ax, sx + sw + 1, sy + sh, 'one dot = one\nemotion\'s list', size=5.0, c=GREY, ha='left', va='top', linespacing=1.15)
    T(ax, sx + sw + 1, sy + sh - 7, 'x: training\nvideos\ny: new videos', size=5.0, c=GREY, ha='left', va='top', linespacing=1.15)
    T(ax, sx + sw + 1, sy + sh - 16.5, 'slope within\neach participant\nand fold', size=5.0, c=GREY, ha='left', va='top', linespacing=1.15)
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


# one matched random list: same layers and number as SEL = [(3, 7), (8, 2), (9, 4), (9, 9)], no overlap
RAND = [(3, 11), (8, 6), (9, 1), (9, 12)]


def fig4b():
    W, H = 180, 106
    fig, ax = canvas(W, H)
    title(ax, 3, H - 3.5, 'Comparing a model with a brain region, and what happens when the fear-list heads are switched off')
    # ---- a: model versions
    panel(ax, 1, H - 8, 'a')
    sub(ax, 7, H - 10.4, 'Model versions, all fed the same Cowen videos')
    T(ax, 7, H - 16, 'Analysis 4, supplementary comparison (before vs after emotion training)', size=6.0, c=MODEL, w='bold', ha='left')
    for i, (nm, note) in enumerate((('video only', 'self-supervised on VCE'), ('emotion-trained', 'fine-tuned on 27 ratings'))):
        x = 9 + i * 38
        trapezoid(ax, x, H - 29, 13, 9, '', size=6)
        snow(ax, x + 11.6, H - 21.2, 0.9)
        T(ax, x + 15, H - 22.5, nm, size=6.0, ha='left', w='bold')
        T(ax, x + 15, H - 25.5, note, size=5.2, c=GREY, ha='left')
    T(ax, 7, H - 35, 'Analysis 5 (emotion-trained model, heads set to 0)', size=6.0, c=HEAD, w='bold', ha='left')
    conds = [('intact', (), ()), ('fear-list heads off', SEL, ()), ('matched random list off', (), RAND)]
    for i, (nm, sel, msk) in enumerate(conds):
        x = 9 + i * 24
        head_grid(ax, x, H - 53, cell=1.25, gap=0.15, sel=sel, masked=msk)
        T(ax, x + 8.3, H - 55.8, nm, size=5.6, c=HEAD if i == 1 else (GREY if i == 2 else INK), w='bold')
    T(ax, 7, H - 59.6, '12 layers (columns) × 12 heads. Orange: fear-list heads. Grey: one matched\n'
                     'random list (same layers and number, similar size of change on VCE validation\n'
                     'videos). Many such lists are drawn.', size=5.2, c=GREY, ha='left', va='top', linespacing=1.2)
    T(ax, 7, H - 69.3, 'Every version gives one 768-value vector per video from the last layer.', size=5.6, c=POOL, ha='left')

    # ---- b: two comparisons
    bx = 86
    panel(ax, bx - 3, H - 8, 'b')
    sub(ax, bx + 3, H - 10.4, 'Two ways to compare one version with one region')
    T(ax, bx + 3, H - 16, 'RSA: do model and region find the same video pairs similar?', size=6.0, w='bold', ha='left')
    rdm(ax, bx + 5, H - 34, 14, 1, 'Greens', POOL)
    T(ax, bx + 12, H - 36.5, 'model', size=5.6, c=POOL)
    T(ax, bx + 23.5, H - 27, 'vs', size=6, c=GREY)
    rdm(ax, bx + 28, H - 34, 14, 2, 'Reds', BRAIN)
    T(ax, bx + 35, H - 36.5, 'region', size=5.6, c=BRAIN)
    T(ax, bx + 44, H - 27, '→  Spearman ρ', size=6.2, ha='left')
    T(ax, bx + 5, H - 40.5, 'videos × videos; each cell = how different two videos are', size=5.2, c=GREY, ha='left')
    T(ax, bx + 3, H - 47, 'Encoding: can the vectors predict each voxel across new videos?', size=6.0, w='bold', ha='left')
    rbox(ax, bx + 5, H - 58, 12, 7, fc=POOL_F, ec=POOL, lw=0.8)
    T(ax, bx + 11, H - 53.4, '768 values', size=5.2, c=POOL)
    T(ax, bx + 11, H - 56.0, 'per video', size=5.0, c=POOL)
    arrow(ax, bx + 17.5, H - 54.5, bx + 20.5, H - 54.5, lw=0.7)
    block(ax, bx + 21, H - 58, 10, 7, 'ridge', fc='white', ec=INK, size=6.0)
    fire(ax, bx + 30.2, H - 51.4, 0.5)
    arrow(ax, bx + 31.5, H - 54.5, bx + 34.5, H - 54.5, lw=0.7)
    mini_map(ax, bx + 35, H - 57.5, 10, 6, 5, 'Greys', GREY)
    T(ax, bx + 47.5, H - 54.5, 'vs', size=5.8, c=GREY)
    mini_map(ax, bx + 50, H - 57.5, 10, 6, 6, 'Reds', BRAIN)
    T(ax, bx + 62, H - 54.5, '→  R²', size=6.2, ha='left')
    T(ax, bx + 47.5, H - 59.8, 'new videos × voxels', size=5.0, c=GREY)
    T(ax, bx + 5, H - 63.5, 'ridge refitted for each version on training videos; R² per voxel across new videos,\naveraged over the region',
      size=5.2, c=GREY, ha='left', va='top', linespacing=1.2)
    line(ax, [3, W - 3], [H - 72, H - 72], c='#DDDDDD', lw=0.6)

    # ---- c: analysis 5 readout
    yc = H - 74
    panel(ax, 1, yc, 'c')
    sub(ax, 7, yc - 2.4, 'Analysis 5, worked example (illustrative values): extra drop = fear-list drop − mean matched-random drop')
    y0, hh, vmax = 8.5, 12.5, 0.22
    groups = [('association region', (0.20, 0.12, 0.17)), ('visual region', (0.18, 0.15, 0.16))]
    for g, (gname, (vi, vf, vr)) in enumerate(groups):
        gx = 9 + g * 88
        T(ax, gx, y0 + hh + 4.6, gname, size=6.2, ha='left', w='bold', c='#C2477A' if g == 0 else '#1B9E77')
        rr = np.random.default_rng(20 + g)
        for v2 in vr + rr.normal(0, 0.012, 14):
            ax.add_patch(Circle((gx + 18 + 3.25 + rr.uniform(-2.2, 2.2), y0 + v2 / vmax * hh), 0.35, fc='#555555', ec='none', zorder=6))
        for j, (lab, v, fc, ec) in enumerate((('intact', vi, POOL_F, POOL), ('fear-list off', vf, HEAD, HEAD),
                                               ('random off', vr, '#C9C9C9', '#8A8A8A'))):
            xx = gx + j * 9
            ax.add_patch(Rectangle((xx, y0), 6.5, v / vmax * hh, fc=fc, ec=ec, lw=0.7, zorder=4))
            T(ax, xx + 3.25, y0 - 2.0, lab, size=5.0)
            T(ax, xx + 3.25, y0 + v / vmax * hh + (3.0 if j == 2 else 1.4), f'{v:.2f}', size=5.0)
        line(ax, [gx - 0.5, gx + 26], [y0, y0], c=INK, lw=0.5)
        tx = gx + 30
        T(ax, tx, y0 + 11, f'drop, fear-list off = {vi - vf:.2f}', size=5.8, ha='left', c=HEAD)
        T(ax, tx, y0 + 7, f'mean drop, random off = {vi - vr:.2f}', size=5.8, ha='left', c='#6E6E6E')
        T(ax, tx, y0 + 2.6, f'extra drop = {(vi - vf) - (vi - vr):.2f}', size=6.2, ha='left', w='bold')
    T(ax, 9, y0 - 5.6, 'Dots: individual matched random lists (bar = their mean). Computed for RSA (ρ) and for encoding (R²);'
      ' regions are compared by subtracting their extra drops.', size=5.2, c=GREY, ha='left')
    illus(ax, W, 1.0)
    save(fig, 'emobrain_regional_alignment')
    return fig


if __name__ == '__main__':
    for f in (fig3a, fig3b, fig3c, fig4a, fig4b):
        f()
