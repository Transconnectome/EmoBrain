import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from style import *
import numpy as np

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def fig2():
    W, H = 180, 104
    fig, ax = canvas(W, H)

    # ---------------- panel a: pipeline ----------------
    panel(ax, 1.5, H - 1.5, 'a')
    txt(ax, 6, H - 3.2, 'VideoMAE ViT-B/16: from a video clip to 27 emotion predictions', size=7, w='bold', ha='left')
    yc = 78
    frames(ax, 5, yc - 6, w=14, h=10)
    txt(ax, 13, yc - 10.5, 'Input clip', size=6.5)
    txt(ax, 13, yc - 13.3, '16 frames, 224 × 224 px', size=5.8, c=GREY)

    arrow(ax, 23, yc, 28, yc)
    box(ax, 28.5, yc - 8.5, 25.5, 17, fc=MODEL_F, ec=MODEL)
    txt(ax, 41.25, yc + 5.3, 'Tubelet embedding', size=6.5, w='bold', c=MODEL)
    # small token cube
    for i in range(4):
        for j in range(3):
            rect(ax, 33 + i * 2.1, yc - 3.2 + j * 2.1, 1.8, 1.8, fc='white', ec=MODEL, lw=0.35, z=4)
    rect(ax, 33 + 1 * 2.1, yc - 3.2 + 1 * 2.1, 1.8, 1.8, fc=MODEL, ec=MODEL, lw=0.35, z=5)
    txt(ax, 47.6, yc - 0.1, '2 × 16 × 16\n→ 1 token', size=5.4, c=INK)
    txt(ax, 41.25, yc - 6.6, '1,568 tokens + position', size=5.6, c=GREY)

    arrow(ax, 54.5, yc, 58.5, yc)
    # 12 blocks
    bx0, bw, bg = 59, 2.7, 1.05
    for b in range(12):
        x = bx0 + b * (bw + bg)
        is9 = (b == 8)
        rect(ax, x, yc - 10, bw, 20, fc=HEAD_F if is9 else MODEL_F, ec=HEAD if is9 else MODEL, lw=0.8 if is9 else 0.5, z=3)
        txt(ax, x + bw / 2, yc - 12, str(b + 1), size=5.2, c=HEAD if is9 else GREY, w='bold' if is9 else 'normal')
    xb_end = bx0 + 12 * (bw + bg) - bg
    txt(ax, (bx0 + xb_end) / 2, yc + 12.6, '12 Transformer blocks (12 heads each)', size=6.3, c=MODEL, w='bold')
    txt(ax, bx0 - 1.2, yc - 12, 'block', size=5.2, c=GREY, ha='right')

    arrow(ax, xb_end + 1, yc, xb_end + 6, yc)
    x = xb_end + 6.5
    box(ax, x, yc - 6.5, 14, 13, fc='white', ec=INK)
    txt(ax, x + 7, yc + 2.2, 'token mean', size=5.8)
    txt(ax, x + 7, yc - 0.6, '+', size=6)
    txt(ax, x + 7, yc - 3.3, 'LayerNorm', size=5.8)

    xg = x + 19
    arrow(ax, x + 14.5, yc, xg - 0.5, yc)
    rect(ax, xg, yc - 10, 3.4, 20, fc=POOL, ec=POOL, z=4)
    txt(ax, xg + 1.7, yc + 12.6, '768-d', size=6.3, c=POOL, w='bold')
    txt(ax, xg + 1.7, yc - 12.6, 'pooled\nfeature', size=5.4, c=POOL)

    xl = xg + 8
    arrow(ax, xg + 3.9, yc, xl - 0.5, yc)
    box(ax, xl, yc - 6.5, 12.5, 13, fc=MODEL_F, ec=MODEL)
    txt(ax, xl + 6.25, yc + 2.0, 'linear', size=5.8, c=MODEL)
    txt(ax, xl + 6.25, yc - 1.2, '768 → 27', size=5.6, c=MODEL)
    txt(ax, xl + 6.25, yc - 4.0, 'logits', size=5.4, c=GREY)

    xs = xl + 17
    arrow(ax, xl + 13, yc, xs - 0.5, yc)
    txt(ax, xs - 2.3, yc + 2.3, 'σ', size=7, c=INK)
    # 27 predictions bar chart
    rng = np.random.default_rng(3)
    vals = np.clip(rng.gamma(1.3, 0.12, 27), 0.02, 0.85)
    vals[10] = 0.78  # e.g. fear
    for i, v in enumerate(vals):
        rect(ax, xs + i * 0.62, yc - 8, 0.5, 16 * v, fc=RATE if i == 10 else '#BDB3D9', ec='none', z=4)
    line(ax, [xs - 0.3, xs + 27 * 0.62], [yc - 8, yc - 8], c=INK, lw=0.4)
    txt(ax, xs + 8.4, yc + 12.6, '27 emotions', size=6.3, c=RATE, w='bold')
    txt(ax, xs + 9.5, yc - 9.6, 'sigmoid, one clip', size=5.0, c=GREY, va='top')

    # annotations under pooled feature / head
    ya = 60.2
    txt(ax, xg + 1.7, ya, 'Analysis 1: a new linear readout on the frozen\n768-d feature of each checkpoint', size=5.4, c=POOL, ha='center', va='top')
    txt(ax, xl + 6.25, yc - 9.0, 'fine-tuned with BCE\non VCE ratings', size=5.0, c=MODEL, ha='center', va='top')

    # zoom guides from block 9 to panel b
    x9 = bx0 + 8 * (bw + bg)
    line(ax, [x9, 30], [yc - 13.6, 49.5], c=HEAD, lw=0.5, ls=(0, (2.5, 1.5)))
    line(ax, [x9 + bw, 104], [yc - 13.6, 49.5], c=HEAD, lw=0.5, ls=(0, (2.5, 1.5)))

    # ---------------- panel b: one block ----------------
    panel(ax, 1.5, 51.5, 'b')
    box(ax, 6, 3, 171, 46.5, fc='#FFFBF6', ec=HEAD, lw=0.7, r=2)
    txt(ax, 12, 46.3, 'Inside one block (here block 9): where a head output is read or ablated', size=7, w='bold', ha='left')

    yr = 37.5  # residual stream
    line(ax, [10, 172], [yr, yr], c=INK, lw=0.9)
    txt(ax, 11, yr + 2.3, 'tokens in\n(1,568 × 768)', size=5.4, ha='left', va='bottom', c=GREY)
    arrow(ax, 166, yr, 173, yr, lw=0.9)
    txt(ax, 172, yr + 2.3, 'tokens out', size=5.4, ha='right', va='bottom', c=GREY)

    # branch 1: LN -> MHSA -> proj -> add
    def add_node(xc):
        ax.add_patch(Circle((xc, yr), 1.6, fc='white', ec=INK, lw=0.7, zorder=6))
        txt(ax, xc, yr - 0.1, '+', size=7, z=7)

    line(ax, [20, 20], [yr, 31], c=INK, lw=0.6)
    box(ax, 15.5, 25, 9, 6, fc='white', ec=INK)
    txt(ax, 20, 28, 'LN', size=6)
    arrow(ax, 24.6, 28, 28.4, 28)

    # MHSA box
    mx, my, mw, mh = 28.5, 6.5, 78, 26.5
    box(ax, mx, my, mw, mh, fc=MODEL_F, ec=MODEL, lw=0.6)
    txt(ax, mx + 2, my + mh - 2.4, 'Multi-head self-attention', size=6.3, c=MODEL, w='bold', ha='left')
    txt(ax, mx + mw - 2, my + mh - 2.4, r'$\mathrm{head}_h=\mathrm{softmax}(Q_hK_h^{\top}\,/\,$' + '√64' + r'$)\,V_h$', size=6.2, c=INK, ha='right')
    hx0, hw, hg = mx + 8, 3.4, 1.2
    for h in range(12):
        x = hx0 + h * (hw + hg)
        on = (h == 3)
        rect(ax, x, my + 5.5, hw, 13.5, fc=HEAD if on else 'white', ec=INK if on else MODEL, lw=0.7 if on else 0.45, z=4)
        txt(ax, x + hw / 2, my + 3.6, str(h + 1), size=5.2, c=HEAD if on else GREY, w='bold' if on else 'normal')
    hx_end = hx0 + 12 * (hw + hg) - hg
    txt(ax, hx0 - 0.5, my + 3.6, 'head', size=5.2, c=GREY, ha='right')
    txt(ax, (hx0 + hx_end) / 2, my + 20.8, '12 heads × 64 values per token', size=5.6, c=MODEL)

    # concat -> read position -> proj
    cx = hx_end + 2.2
    arrow(ax, hx_end + 0.4, my + 12.3, cx + 3.2, my + 12.3, lw=0.6)
    txt(ax, cx + 1.4, my + 14.9, 'concat', size=5.2, c=GREY)
    # orange read/ablate marker
    rx = cx + 4.6
    line(ax, [rx, rx], [my + 4.2, my + 21.5], c=HEAD, lw=1.1)
    ax.add_patch(Polygon([[rx - 1.2, my + 22.6], [rx + 1.2, my + 22.6], [rx, my + 21.2]], closed=True, fc=HEAD, ec=HEAD, zorder=7))

    px = mx + mw + 3
    arrow(ax, rx + 0.3, my + 12.3, px - 0.4, my + 12.3, lw=0.6)
    box(ax, px, my + 8.8, 9, 7, fc='white', ec=INK)
    txt(ax, px + 4.5, my + 12.3, 'proj', size=6)
    add1 = px + 16
    line(ax, [px + 9, add1], [my + 12.3, my + 12.3], c=INK, lw=0.6)
    arrow(ax, add1, my + 12.3, add1, yr - 1.7, lw=0.6)
    add_node(add1)

    # branch 2: LN -> MLP -> add
    line(ax, [add1 + 6, add1 + 6], [yr, 33], c=INK, lw=0.6)
    box(ax, add1 + 1.5, 27.5, 9, 5.5, fc='white', ec=INK)
    txt(ax, add1 + 6, 30.25, 'LN', size=6)
    arrow(ax, add1 + 6, 27.5, add1 + 6, 25.6, lw=0.6)
    box(ax, add1 + 1.5, 19.6, 24, 6, fc=MODEL_F, ec=MODEL)
    txt(ax, add1 + 13.5, 22.6, 'MLP 768 → 3,072 → 768', size=5.6, c=MODEL)
    add2 = add1 + 32
    line(ax, [add1 + 25.5, add2], [22.6, 22.6], c=INK, lw=0.6)
    arrow(ax, add2, 22.6, add2, yr - 1.7, lw=0.6)
    add_node(add2)

    # read / ablate callout
    bx_, by_, bw_, bh_ = 119.5, 4.2, 53.5, 13.6
    box(ax, bx_, by_, bw_, bh_, fc='white', ec=HEAD, lw=0.7)
    txt(ax, bx_ + 2, by_ + bh_ - 1.3, 'At the proj input (orange)', size=6.0, c=HEAD, w='bold', ha='left', va='top')
    txt(ax, bx_ + 2, by_ + bh_ - 4.6, 'read: head h output, 64 values per token\n'
                          'ablate: set those 64 values to 0 for all tokens\n'
                          'importance draw: one random mask ablates 72 of 144 heads',
        size=5.3, ha='left', va='top', linespacing=1.35)
    line(ax, [rx, rx], [my + 4.2, 8.2], c=HEAD, lw=0.5, ls=(0, (2, 1.2)))
    line(ax, [rx, bx_], [8.2, 8.2], c=HEAD, lw=0.5, ls=(0, (2, 1.2)))
    save(fig, 'emobrain_videomae_methods', OUT)
    return fig


if __name__ == '__main__':
    fig2()
