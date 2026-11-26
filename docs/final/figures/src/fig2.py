import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import *

FR = ['cowen_1374_f3.png', 'cowen_1374_f4.png', 'cowen_1374_f1.png']


def fig2():
    W, H = 180, 98
    fig, ax = canvas(W, H)

    # ---------------- a: two training stages ----------------
    panel(ax, 1, H - 1, 'a')
    T(ax, 7, H - 3.6, 'Two training stages on VCE videos (example clip shown)', size=8, w='bold', ha='left')
    # stage 1
    y1 = 76
    T(ax, 7, y1 + 13.5, 'Stage 1  masked video SSL', size=7, c=MODEL, w='bold', ha='left')
    img(ax, 'cowen_1374_tubemask.png', 7, y1 - 8, 17, 17)
    T(ax, 15.5, y1 - 10.6, '90% tubes hidden', size=5.8, c=GREY)
    arrow(ax, 24.5, y1 + 0.5, 28.5, y1 + 0.5)
    trapezoid(ax, 29, y1 - 7, 15, 15, 'encoder', size=6.8)
    fire(ax, 42.6, y1 + 6.6, 0.75)
    arrow(ax, 44.5, y1 + 0.5, 47.5, y1 + 0.5)
    trapezoid(ax, 48, y1 - 7, 12, 15, 'decoder', narrow='left', size=6.8)
    fire(ax, 58.6, y1 + 6.6, 0.75)
    arrow(ax, 60.5, y1 + 0.5, 64.5, y1 + 0.5)
    img(ax, 'cowen_1374_f3.png', 65, y1 - 8, 17, 17)
    T(ax, 73.5, y1 - 10.6, 'pixels restored', size=5.8, c=GREY)
    # stage 2
    x2 = 92
    T(ax, x2, y1 + 13.5, 'Stage 2  emotion fine-tuning', size=7, c=MODEL, w='bold', ha='left')
    stack(ax, FR, x2, y1 - 8, 13, dx=1.6, dy=1.6)
    T(ax, x2 + 8, y1 - 10.6, '16 frames', size=5.8, c=GREY)
    arrow(ax, x2 + 17.5, y1 + 0.5, x2 + 21.5, y1 + 0.5)
    trapezoid(ax, x2 + 22, y1 - 7, 15, 15, 'encoder', size=6.8)
    fire(ax, x2 + 35.6, y1 + 6.6, 0.75)
    arrow(ax, x2 + 37.5, y1 + 0.5, x2 + 41, y1 + 0.5)
    tensor(ax, x2 + 41.5, y1 - 7.5, 4.2, 16, '', fc=POOL, ec=POOL)
    T(ax, x2 + 43.6, y1 + 10.6, '768', size=6.4, c=POOL, w='bold')
    T(ax, x2 + 43.6, y1 - 10.6, 'token mean', size=5.6, c=POOL)
    arrow(ax, x2 + 46.2, y1 + 0.5, x2 + 49.5, y1 + 0.5)
    block(ax, x2 + 50, y1 - 4, 11, 9, 'linear', fc=MODEL_F, ec=MODEL, size=6.6)
    fire(ax, x2 + 60, y1 + 4.6, 0.65)
    arrow(ax, x2 + 61.5, y1 + 0.5, x2 + 65, y1 + 0.5)
    T(ax, x2 + 63.2, y1 + 3.0, 'σ', size=7)
    rng = np.random.default_rng(3)
    v = np.clip(rng.gamma(1.2, 0.1, 27), 0.03, 0.6)
    v[16] = 0.75
    bars(ax, x2 + 65.5, y1 - 6, v, w=0.62, gap=0.18, hmax=14, hi=16)
    T(ax, x2 + 76.3, y1 - 10.6, '27 emotions (BCE)', size=5.8, c=RATE)
    T(ax, W - 58, 56.5, 'analyses 2 to 6 use the fine-tuned model, frozen', size=6.0, c=ICE, ha='left')
    snow(ax, W - 60.5, 56.5, 1.2)
    line(ax, [3, W - 3], [52.5, 52.5], c='#DDDDDD', lw=0.6)

    # ---------------- b: read / ablate a head ----------------
    panel(ax, 1, 50, 'b')
    T(ax, 7, 47.4, 'Reading or ablating one attention head', size=8, w='bold', ha='left')
    yb = 22
    img(ax, 'cowen_1374_grid.png', 6, yb - 9, 19, 19)
    T(ax, 15.5, yb - 11.8, '2 × 16 × 16 px → 1 token', size=5.6, c=GREY)
    arrow(ax, 25.5, yb + 0.5, 29.5, yb + 0.5)
    tensor(ax, 30, yb - 4, 17, 9, '1568 × 768', size=6.6)
    T(ax, 38.5, yb - 6.6, 'tokens', size=5.6, c=GREY)
    arrow(ax, 47.5, yb + 0.5, 51.5, yb + 0.5)
    # 12 blocks
    for b in range(12):
        x = 52 + b * 2.6
        on = (b == 8)
        ax.add_patch(Rectangle((x, yb - 8), 2.0, 17, fc=HEAD_F if on else MODEL_F, ec=HEAD if on else MODEL, lw=0.9 if on else 0.5, zorder=4))
    T(ax, 67.3, yb + 11.2, '12 Transformer blocks', size=6.2, c=MODEL)
    T(ax, 52 + 8 * 2.6 + 1, yb - 10.4, '9', size=6, c=HEAD, w='bold')
    # zoom
    zx = 89
    line(ax, [52 + 8 * 2.6 + 2.0, zx], [yb + 9, yb + 17], c=HEAD, lw=0.5, ls=(0, (2, 1.2)))
    line(ax, [52 + 8 * 2.6 + 2.0, zx], [yb - 8, yb - 16], c=HEAD, lw=0.5, ls=(0, (2, 1.2)))
    rbox(ax, zx, yb - 16, 50, 33, fc='#FFFBF5', ec=HEAD, lw=0.8)
    T(ax, zx + 2, yb + 14.5, 'block 9: multi-head self-attention', size=6.2, c=HEAD, ha='left', w='bold')
    for h in range(12):
        x = zx + 3 + h * 3.0
        on = (h == 3)
        ax.add_patch(Rectangle((x, yb - 8), 2.3, 18, fc=HEAD if on else 'white', ec=INK if on else MODEL, lw=0.8 if on else 0.45, zorder=5))
        T(ax, x + 1.15, yb - 10.0, str(h + 1), size=5.0, c=HEAD if on else GREY, w='bold' if on else 'normal')
    T(ax, zx + 25, yb - 13.4, r'head$_h$ = softmax($QK^{\top}$/' + '√64' + r')$V$, 64 values per token', size=5.6, c=GREY)
    # read path
    hx = zx + 3 + 3 * 3.0 + 1.15
    arrow(ax, zx + 40, yb + 6, 144.5, yb + 6, c=HEAD, lw=1.0)
    line(ax, [hx, hx, zx + 40], [yb + 10, yb + 12, yb + 12], c=HEAD, lw=1.0)
    line(ax, [zx + 40, zx + 40], [yb + 12, yb + 6], c=HEAD, lw=1.0)
    tensor(ax, 145, yb + 1.5, 15, 9, '1568 × 64', fc=HEAD_F, ec=HEAD, c=HEAD, size=6.4)
    T(ax, 152.5, yb + 13.0, 'read', size=6.6, c=HEAD, w='bold')
    arrow(ax, 160.5, yb + 6, 164.5, yb + 6, c=HEAD)
    tensor(ax, 165, yb + 1.5, 11, 9, '64', fc=HEAD_F, ec=HEAD, c=HEAD, size=6.6)
    T(ax, 170.5, yb - 0.9, 'mean over tokens\nand clips; K heads\n→ 64K per video', size=5.4, c=GREY, va='top', linespacing=1.15)
    # ablate path
    T(ax, 152.5, yb - 6.5, 'ablate', size=6.6, c=INK, w='bold')
    T(ax, 152.5, yb - 10.0, 'set to 0, all tokens', size=5.6, c=GREY)
    line(ax, [zx + 40, 144], [yb - 3, yb - 3], c=INK, lw=0.8)
    T(ax, 146.5, yb - 3, '× 0', size=7.5, c=INK, w='bold', ha='left')
    save(fig, 'emobrain_videomae_methods')
    return fig


if __name__ == '__main__':
    fig2()
