"""Shared drawing helpers for the EmoBrain methods figures (Nature-style schematics)."""
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, FancyArrowPatch, Polygon, Ellipse

MM = 1 / 25.4

mpl.rcParams.update({
    'font.family': 'Liberation Sans',
    'font.size': 6.5,
    'axes.linewidth': 0.5,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'svg.fonttype': 'none',
    'savefig.dpi': 600,
    'lines.linewidth': 0.6,
    'mathtext.fontset': 'custom',
    'mathtext.rm': 'Liberation Sans',
    'mathtext.it': 'Liberation Sans:italic',
    'mathtext.bf': 'Liberation Sans:bold',
    'xtick.major.width': 0.5, 'ytick.major.width': 0.5,
    'xtick.major.size': 2, 'ytick.major.size': 2,
    'xtick.labelsize': 6, 'ytick.labelsize': 6,
    'axes.labelsize': 6.5, 'axes.titlesize': 7,
    'legend.fontsize': 6, 'legend.frameon': False,
})

# palette (colour-blind safe, muted). Roles are fixed across all figures.
INK = '#222222'
GREY = '#8A8A8A'
LIGHT = '#F2F2F2'
MODEL = '#4C6A8A'      # VideoMAE / model structure
MODEL_F = '#E7EDF4'
HEAD = '#E8871E'       # selected attention heads, read / ablate position
HEAD_F = '#FCE9D2'
POOL = '#3A9E5F'       # last-layer pooled 768-d vector
POOL_F = '#DCEFE3'
RATE = '#6E5AA8'       # human emotion ratings (VCE / Cowen)
RATE_F = '#ECE8F5'
BRAIN = '#C0504D'      # fMRI / brain
BRAIN_F = '#F6E1E0'
C_L = '#4A86C5'        # low-level visual (L)
C_O = '#A0773E'        # object nouns (O)
C_S = '#C2477A'        # full caption (S)
SHARED = '#B8B8B8'


def canvas(w_mm, h_mm):
    fig = plt.figure(figsize=(w_mm * MM, h_mm * MM))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w_mm)
    ax.set_ylim(0, h_mm)
    ax.axis('off')
    return fig, ax


def box(ax, x, y, w, h, fc='white', ec=INK, lw=0.6, r=1.2, z=2, ls='-', alpha=1.0):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f'round,pad=0,rounding_size={r}',
                       fc=fc, ec=ec, lw=lw, zorder=z, ls=ls, alpha=alpha)
    ax.add_patch(p)
    return p


def rect(ax, x, y, w, h, fc='white', ec=INK, lw=0.5, z=2, hatch=None, alpha=1.0):
    p = Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, zorder=z, hatch=hatch, alpha=alpha)
    ax.add_patch(p)
    return p


def arrow(ax, x1, y1, x2, y2, c=INK, lw=0.7, ms=5.5, style='-|>', ls='-', rad=0.0, z=4, sa=0, sb=0):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=ms, color=c, lw=lw,
                        ls=ls, connectionstyle=f'arc3,rad={rad}', zorder=z, shrinkA=sa, shrinkB=sb)
    ax.add_patch(a)
    return a


def line(ax, xs, ys, c=INK, lw=0.6, ls='-', z=3):
    ax.plot(xs, ys, color=c, lw=lw, ls=ls, zorder=z, solid_capstyle='butt')


def txt(ax, x, y, s, size=6.5, c=INK, ha='center', va='center', w='normal', style='normal', z=6, **kw):
    return ax.text(x, y, s, fontsize=size, color=c, ha=ha, va=va, fontweight=w, fontstyle=style,
                   zorder=z, **kw)


def panel(ax, x, y, letter, size=9):
    txt(ax, x, y, letter, size=size, w='bold', ha='left', va='top')


def num(ax, x, y, n, c=INK, r=2.0, size=6.5, fc='white'):
    ax.add_patch(Circle((x, y), r, fc=fc, ec=c, lw=0.7, zorder=7))
    txt(ax, x, y - 0.05, str(n), size=size, c=c, w='bold', z=8)


def frames(ax, x, y, w=10, h=7.5, n=3, dx=1.3, dy=1.1, ec=INK, fc='#FFFFFF', scene=True):
    """Stacked video frames with a tiny abstract scene."""
    for i in range(n - 1, -1, -1):
        xx, yy = x + i * dx, y + i * dy
        rect(ax, xx, yy, w, h, fc=fc, ec=ec, lw=0.5, z=3 + (n - i))
    if scene:
        xx, yy = x, y
        # ground, a figure and a dog-like blob (abstract)
        rect(ax, xx, yy, w, h * 0.28, fc='#E9E4D8', ec='none', z=3 + n + 1)
        ax.add_patch(Circle((xx + w * 0.30, yy + h * 0.62), h * 0.09, fc='#7A7A7A', ec='none', zorder=3 + n + 2))
        rect(ax, xx + w * 0.27, yy + h * 0.28, w * 0.06, h * 0.26, fc='#7A7A7A', ec='none', z=3 + n + 2)
        ax.add_patch(Ellipse((xx + w * 0.68, yy + h * 0.36), w * 0.22, h * 0.14, fc='#A47C52', ec='none', zorder=3 + n + 2))
        ax.add_patch(Circle((xx + w * 0.80, yy + h * 0.44), h * 0.07, fc='#A47C52', ec='none', zorder=3 + n + 2))


def brain(ax, x, y, w=12, h=8.5, fc=BRAIN_F, ec=BRAIN, lw=0.7, roi=True, roi_c=None):
    """Simple lateral brain silhouette."""
    import numpy as np
    t = np.linspace(0, 2 * np.pi, 200)
    bx = x + w / 2 + (w / 2) * np.cos(t) * (1 + 0.08 * np.cos(2 * t))
    by = y + h / 2 + (h / 2) * np.sin(t) * (0.92 + 0.10 * np.sin(t))
    ax.add_patch(Polygon(np.c_[bx, by], closed=True, fc=fc, ec=ec, lw=lw, zorder=4))
    # temporal lobe notch / cerebellum
    ax.add_patch(Ellipse((x + w * 0.78, y + h * 0.10), w * 0.26, h * 0.22, fc=fc, ec=ec, lw=lw, zorder=3))
    # sulci
    for (a, b, c, d) in [(0.25, 0.75, 0.42, 0.55), (0.45, 0.85, 0.55, 0.62), (0.30, 0.45, 0.65, 0.40)]:
        ax.plot([x + w * a, x + w * c], [y + h * b, y + h * d], color=ec, lw=0.4, zorder=5)
    if roi:
        ax.add_patch(Ellipse((x + w * 0.70, y + h * 0.52), w * 0.20, h * 0.20,
                             fc=roi_c or BRAIN, ec='none', alpha=0.85, zorder=6))


def head_grid(ax, x, y, cell=1.6, gap=0.35, n_blocks=12, n_heads=12, selected=(), ec='#9AA8B8',
              fc='white', sel_fc=HEAD, lw=0.35):
    """12 x 12 grid: columns = blocks (layers), rows = heads. selected = list of (block, head), 1-based."""
    sel = set(selected)
    for b in range(1, n_blocks + 1):
        for h in range(1, n_heads + 1):
            xx = x + (b - 1) * (cell + gap)
            yy = y + (n_heads - h) * cell
            on = (b, h) in sel
            rect(ax, xx, yy, cell, cell, fc=sel_fc if on else fc, ec=INK if on else ec, lw=0.6 if on else lw, z=4 if on else 3)
    return (cell + gap)


def bars_h(ax, x, y, vals, maxv, length, height, colors, gap=0.6):
    for i, (v, c) in enumerate(zip(vals, colors)):
        yy = y - i * (height + gap)
        rect(ax, x, yy, length, height, fc=LIGHT, ec='none', z=2)
        rect(ax, x, yy, length * v / maxv, height, fc=c, ec='none', z=3)


def save(fig, stem, outdir):
    import os
    os.makedirs(outdir, exist_ok=True)
    fig.savefig(os.path.join(outdir, stem + '.pdf'))
    fig.savefig(os.path.join(outdir, stem + '.svg'))
    fig.savefig(os.path.join(outdir, stem + '.png'), dpi=300)
