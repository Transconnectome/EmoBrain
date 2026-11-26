"""Drawing kit for the v2 (MindEye-style) EmoBrain figures: real images, tensor boxes, frozen/trained icons."""
import os
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, FancyArrowPatch, Polygon, PathPatch
from matplotlib.path import Path

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.environ.get('EMOBRAIN_FIG_ASSETS', os.path.join(HERE, 'assets'))
OUT = os.environ.get('EMOBRAIN_FIG_OUT', os.path.join(HERE, 'out'))
MM = 1 / 25.4

mpl.rcParams.update({
    'font.family': 'Liberation Sans', 'font.size': 7, 'pdf.fonttype': 42, 'svg.fonttype': 'none',
    'mathtext.fontset': 'custom', 'mathtext.rm': 'Liberation Sans', 'mathtext.it': 'Liberation Sans:italic',
    'mathtext.bf': 'Liberation Sans:bold', 'savefig.dpi': 600,
})

INK = '#1F1F1F'
GREY = '#7A7A7A'
TENSOR = '#D4D4D4'
TENSOR_INK = '#3A3A3A'
MODEL, MODEL_F = '#3F6E9E', '#DCE8F5'
HEAD, HEAD_F = '#E07B00', '#FDE3C3'
POOL, POOL_F = '#2E8B57', '#D7EEDF'
RATE, RATE_F = '#6A4FA3', '#E7E0F4'
BRAIN, BRAIN_F = '#B83B3B', '#F5D9D7'
C_L, C_O, C_S = '#3D7FC1', '#9C6B2E', '#B8336A'
ICE, FIRE = '#4A90D9', '#E4572E'


def canvas(w, h):
    fig = plt.figure(figsize=(w * MM, h * MM))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis('off')
    return fig, ax


def T(ax, x, y, s, size=7, c=INK, ha='center', va='center', w='normal', st='normal', z=8, **kw):
    return ax.text(x, y, s, fontsize=size, color=c, ha=ha, va=va, fontweight=w, fontstyle=st, zorder=z, **kw)


def rbox(ax, x, y, w, h, fc='white', ec=INK, lw=0.8, r=1.2, z=3, ls='-'):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f'round,pad=0,rounding_size={r}', fc=fc, ec=ec, lw=lw, zorder=z, ls=ls)
    ax.add_patch(p)
    return p


def block(ax, x, y, w, h, title, sub=None, fc=MODEL_F, ec=MODEL, size=7.5, subsize=6.2, c=None, z=3):
    rbox(ax, x, y, w, h, fc=fc, ec=ec, lw=0.9, z=z)
    if sub:
        T(ax, x + w / 2, y + h / 2 + 1.5, title, size=size, c=c or INK, z=z + 2)
        T(ax, x + w / 2, y + h / 2 - 2.0, sub, size=subsize, c=GREY, z=z + 2)
    else:
        T(ax, x + w / 2, y + h / 2, title, size=size, c=c or INK, z=z + 2)


def tensor(ax, x, y, w, h, s, fc=TENSOR, ec='#555555', c=TENSOR_INK, size=7.5, ls='-', z=4):
    rect = Rectangle((x, y), w, h, fc=fc, ec=ec, lw=0.8, zorder=z, ls=ls)
    ax.add_patch(rect)
    T(ax, x + w / 2, y + h / 2, s, size=size, c=c, z=z + 1)


def arrow(ax, x1, y1, x2, y2, c=INK, lw=0.9, ms=6, ls='-', rad=0.0, z=6, style='-|>'):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=ms, color=c, lw=lw, ls=ls,
                                 connectionstyle=f'arc3,rad={rad}', zorder=z, shrinkA=0, shrinkB=0))


def line(ax, xs, ys, c=INK, lw=0.9, ls='-', z=5):
    ax.plot(xs, ys, color=c, lw=lw, ls=ls, zorder=z, solid_capstyle='round')


def img(ax, name, x, y, w, h=None, border=True, z=4, lw=0.6, trim=False):
    im = mpimg.imread(os.path.join(ASSETS, name))
    if trim and im.shape[-1] == 4:
        a = im[..., 3] > 0.02
        ys, xs = np.where(a)
        im = im[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    if h is None:
        h = w * im.shape[0] / im.shape[1]
    ax.imshow(im, extent=[x, x + w, y, y + h], zorder=z, interpolation='antialiased')
    if border:
        ax.add_patch(Rectangle((x, y), w, h, fc='none', ec=INK, lw=lw, zorder=z + 1))
    return h


def stack(ax, names, x, y, w, dx=2.2, dy=2.2, z=4):
    """Stacked frames, first name on top-front."""
    for k, n in reversed(list(enumerate(names))):
        img(ax, n, x + k * dx, y + k * dy, w, w, z=z + (len(names) - k) * 2)


def snow(ax, x, y, r=1.7, c=ICE, lw=0.8, z=12):
    for a in range(3):
        t = np.pi / 3 * a
        dx, dy = r * np.cos(t), r * np.sin(t)
        line(ax, [x - dx, x + dx], [y - dy, y + dy], c=c, lw=lw, z=z)
        for s in (-1, 1):
            bx, by = x + s * dx * 0.62, y + s * dy * 0.62
            for b in (-1, 1):
                tb = t + b * np.pi / 4 + (0 if s > 0 else np.pi)
                line(ax, [bx, bx + 0.45 * r * np.cos(tb)], [by, by + 0.45 * r * np.sin(tb)], c=c, lw=lw * 0.8, z=z)


def fire(ax, x, y, s=1.0, z=12):
    """Small flame icon centred at (x, y)."""
    verts = [(0, -1.6), (1.1, -1.0), (1.2, 0.2), (0.5, 1.0), (0.6, 1.9), (-0.2, 1.0), (-0.9, 1.6), (-1.2, 0.2), (-1.1, -1.0), (0, -1.6)]
    codes = [Path.MOVETO] + [Path.CURVE3, Path.CURVE3] * 4 + [Path.LINETO]
    pts = [(x + vx * s, y + vy * s) for vx, vy in verts]
    ax.add_patch(PathPatch(Path(pts, codes[:len(pts)]), fc=FIRE, ec='#B33A16', lw=0.4, zorder=z))
    inner = [(x + vx * s * 0.5, y - 0.45 * s + vy * s * 0.5) for vx, vy in verts]
    ax.add_patch(PathPatch(Path(inner, codes[:len(inner)]), fc='#FFC24B', ec='none', zorder=z + 1))


def trapezoid(ax, x, y, w, h, title, sub=None, fc=MODEL_F, ec=MODEL, narrow='right', inset=0.22, size=8):
    if narrow == 'right':
        pts = [(x, y), (x + w, y + h * inset), (x + w, y + h * (1 - inset)), (x, y + h)]
    else:
        pts = [(x, y + h * inset), (x + w, y), (x + w, y + h), (x, y + h * (1 - inset))]
    ax.add_patch(Polygon(pts, closed=True, fc=fc, ec=ec, lw=1.0, zorder=3))
    if sub:
        T(ax, x + w / 2, y + h / 2 + 1.8, title, size=size, c=INK)
        T(ax, x + w / 2, y + h / 2 - 2.0, sub, size=6.2, c=GREY)
    else:
        T(ax, x + w / 2, y + h / 2, title, size=size, c=INK)


def caption_box(ax, x, y, w, h, s, size=6.2):
    rbox(ax, x, y, w, h, fc='#EDEDED', ec='#EDEDED', lw=0.5, r=0.8, z=3)
    T(ax, x + w / 2, y + h / 2, s, size=size, c='#333333', family='Liberation Mono', linespacing=1.25)


def bars(ax, x, y, vals, w=0.55, gap=0.25, hmax=8, colors=None, hi=None, base=True, z=5):
    for i, v in enumerate(vals):
        c = colors[i] if colors else '#BDB3D9'
        if hi is not None and i == hi:
            c = RATE
        ax.add_patch(Rectangle((x + i * (w + gap), y), w, max(0.15, v * hmax), fc=c, ec='none', zorder=z))
    if base:
        line(ax, [x - 0.3, x + len(vals) * (w + gap)], [y, y], c=INK, lw=0.5, z=z)


def head_grid(ax, x, y, cell=0.9, gap=0.15, sel=(), masked=(), ec='#9AA8B8', lw=0.25, z=4):
    S, M = set(sel), set(masked)
    for b in range(12):
        for h in range(12):
            xx, yy = x + b * (cell + gap), y + (11 - h) * cell
            fc = HEAD if (b + 1, h + 1) in S else ('#A3ABB5' if (b + 1, h + 1) in M else 'white')
            ax.add_patch(Rectangle((xx, yy), cell, cell, fc=fc, ec=ec if fc == 'white' else INK, lw=lw if fc == 'white' else 0.4, zorder=z))
    return 12 * (cell + gap) - gap, 12 * cell


def panel(ax, x, y, s, size=10):
    T(ax, x, y, s, size=size, w='bold', ha='left', va='top')


def save(fig, stem):
    os.makedirs(OUT, exist_ok=True)
    for ext in ('pdf', 'svg'):
        fig.savefig(os.path.join(OUT, f'{stem}.{ext}'))
    fig.savefig(os.path.join(OUT, f'{stem}.png'), dpi=300)


def badge(ax, x, y, n, c=INK, r=1.9, size=7, fc='white', z=12):
    ax.add_patch(Circle((x, y), r, fc=fc, ec=c, lw=0.9, zorder=z))
    T(ax, x, y - 0.05, str(n), size=size, c=c, w='bold', z=z + 1)


def head(ax, x, y, n, s, c=INK, size=7.5):
    badge(ax, x + 1.9, y, n, c=c)
    T(ax, x + 4.8, y, s, size=size, w='bold', ha='left')
