import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import *

# real Cowen & Keltner (2017) profile of video 1374 on the 27 shared categories (proportion of raters)
EMO27 = ['admiration', 'adoration', 'aesthetic appreciation', 'amusement', 'anger', 'anxiety', 'awe', 'awkwardness',
         'boredom', 'calmness', 'confusion', 'craving', 'disgust', 'empathic pain', 'entrancement', 'excitement', 'fear',
         'horror', 'interest', 'joy', 'nostalgia', 'relief', 'romance', 'sadness', 'satisfaction', 'sexual desire', 'surprise']
P1374 = [0.0, 0.0, 0.0, 0.273, 0.0, 0.273, 0.0, 0.0, 0.0, 0.0, 0.182, 0.0, 0.0, 0.0, 0.0, 0.091, 0.545, 0.273, 0.091,
         0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.182]
FEAR = EMO27.index('fear')
SEL = [(3, 7), (8, 2), (9, 4), (9, 9)]


def fig1():
    W, H = 180, 122
    fig, ax = canvas(W, H)

    # ---------------- stage 1: VCE ----------------
    rbox(ax, 2, 97, 176, 23, fc='#F6F8FB', ec='#C9D3DE', lw=0.6, r=2, z=1)
    T(ax, 5, 117.4, 'VCE (no brain data)', size=7.5, w='bold', c=MODEL, ha='left')
    tensor(ax, 6, 101.5, 20, 11, '44,584\ntraining videos', size=6.6)
    arrow(ax, 26.5, 107, 31.5, 107)
    trapezoid(ax, 32, 100, 22, 14, 'VideoMAE', 'ViT-B/16', size=7.5)
    fire(ax, 52.5, 112.5, 0.9)
    T(ax, 43, 98.0, 'masked SSL, then fine-tuning', size=5.8, c=GREY)
    arrow(ax, 54.5, 107, 59.5, 107)
    tensor(ax, 60, 102.5, 13, 9, 'N × 27', fc=RATE_F, ec=RATE, c=RATE)
    T(ax, 66.5, 99.6, 'ratings (BCE)', size=5.8, c=RATE)
    badge(ax, 78.5, 107, 1, c=MODEL)
    # head ablation
    arrow(ax, 82, 107, 87, 107)
    rbox(ax, 87.5, 99.5, 52, 15.5, fc='white', ec=HEAD, lw=0.9)
    rng = np.random.default_rng(2)
    masked = [(b + 1, h + 1) for b in range(12) for h in range(12) if rng.random() < 0.5]
    head_grid(ax, 89.5, 101.3, cell=0.95, gap=0.12, masked=masked)
    T(ax, 104.5, 113.2, 'mask 72/144 heads', size=5.6, c=GREY, ha='left')
    T(ax, 104.5, 109.6, 'many random masks', size=5.6, c=GREY, ha='left')
    T(ax, 104.5, 105.0, 'r per emotion', size=6.4, ha='left')
    T(ax, 104.5, 101.6, 'on validation videos', size=5.6, c=GREY, ha='left')
    arrow(ax, 125, 107, 128.5, 107, c=HEAD)
    head_grid(ax, 128.8, 101.3, cell=0.75, gap=0.08, sel=SEL)
    T(ax, 133.8, 98.0, 'K heads per emotion', size=5.8, c=HEAD)
    badge(ax, 143, 107, 2, c=HEAD)
    snow(ax, 150, 109, 1.6)
    T(ax, 153, 109, 'model frozen\nfrom here on', size=6.2, c=ICE, ha='left', linespacing=1.15)
    fire(ax, 150, 102.6, 0.75)
    T(ax, 153, 102.6, 'trained', size=6.2, c=FIRE, ha='left')

    # ---------------- stage 2: Cowen + HK ----------------
    T(ax, 5, 93.0, 'Cowen video 1374 (one of 2,181 viewed in the scanner)', size=7.5, w='bold', ha='left')
    stack(ax, 3, 5, 63, 22, dx=2.4, dy=2.2)
    caption_box(ax, 4, 49, 36, 9.5, '"A large lizard chases\na woman ... runs away."', size=6.0)
    T(ax, 22, 46.8, '1 of 20 human captions', size=5.6, c=GREY)
    # real ratings
    bars(ax, 6, 36, P1374, w=0.85, gap=0.32, hmax=11, hi=FEAR)
    T(ax, 6 + FEAR * 1.17 + 0.4, 36 + P1374[FEAR] * 11 + 1.3, 'fear', size=5.8, c=RATE)
    T(ax, 22, 33.6, 'Cowen ratings, 27 emotions', size=5.8, c=RATE)
    # brain
    img(ax, 'mni_sagittal.png', 7, 6, 20)
    T(ax, 17, 3.2, 'HK fMRI, 5 participants', size=6.2, c=BRAIN)

    # VideoMAE frozen -> head outputs
    arrow(ax, 32, 74, 42.5, 74)
    trapezoid(ax, 43, 64, 17, 20, 'VideoMAE', 'frozen', size=7.2)
    snow(ax, 58.5, 81.5, 1.4)
    arrow(ax, 60.5, 74, 64.5, 74)
    tensor(ax, 65, 69.5, 15, 9, 'N × 64K', fc=HEAD_F, ec=HEAD, c=HEAD)
    T(ax, 72.5, 66.8, 'head outputs', size=6.2, c=HEAD, w='bold')
    T(ax, 72.5, 64.0, '(K heads × 64)', size=5.6, c=GREY)

    # trunk
    tx = 85
    line(ax, [80.5, tx], [74, 74], c=HEAD, lw=1.6)
    line(ax, [tx, tx], [24, 88], c=HEAD, lw=1.6)

    # ---- row 3 ----
    y3 = 78
    head(ax, 89, 91.5, 3, 'What explains the head outputs?')
    line(ax, [tx, 152], [88, 88], c=HEAD, lw=1.2)
    arrow(ax, 152, 88, 152, 84.6, c=HEAD, lw=1.2)
    T(ax, 153, 86.4, 'target', size=5.4, c=HEAD, ha='left')
    # L, O, S chips
    frame_icon(ax, 90.5, 72, 9, 9, label='motion\nmap', symbol=None)
    T(ax, 95, 69.8, 'L  motion', size=5.8, c=C_L, w='bold')
    caption_box(ax, 101.5, 76, 19, 5, 'woman, lizard', size=5.8)
    T(ax, 111, 73.6, 'O  object nouns', size=5.8, c=C_O, w='bold')
    caption_box(ax, 101.5, 66.6, 19, 5, 'full caption', size=5.8)
    T(ax, 111, 64.3, 'S  sentence', size=5.8, c=C_S, w='bold')
    arrow(ax, 121.5, 75, 125.5, 75)
    block(ax, 126, 70.5, 15, 9, 'banded', 'ridge', fc='white', ec=INK, size=6.4, subsize=6.4)
    fire(ax, 140, 79, 0.65)
    arrow(ax, 141.5, 75, 145.5, 75)
    # stacked bars (illustrative, same numbers as figure 3b)
    parts = [('L', C_L), ('O', C_O), ('S', C_S), ('shared', '#AFAFAF')]
    for j, (lab, c, vals) in enumerate((('fear-head output', HEAD, (0.08, 0.04, 0.05, 0.11)),
                                         ('human fear rating', RATE, (0.04, 0.02, 0.10, 0.14)))):
        yy = 79 - j * 7.5
        T(ax, 146, yy + 2.6, lab, size=5.8, c=c, ha='left', w='bold')
        xx = 146
        for (pl, pc), v in zip(parts, vals):
            ax.add_patch(Rectangle((xx, yy - 1.6), v * 90, 3.0, fc=pc, ec='white', lw=0.3, zorder=5))
            xx += v * 90
    for k, (pl, pc) in enumerate(parts):
        ax.add_patch(Rectangle((146 + k * 7.6, 64.2), 1.8, 1.8, fc=pc, ec='none', zorder=5))
        T(ax, 148.4 + k * 7.6, 65.1, pl, size=5.4, ha='left')
    T(ax, 176, 61.6, 'unique and shared test R² (illustrative)', size=5.2, c=GREY, ha='right', st='italic')

    # ---- row 4 ----
    head(ax, 89, 57.2, 4, 'Which regions do heads and ratings explain?')
    arrow(ax, tx, 48.5, 89, 48.5, c=HEAD, lw=1.2)
    tensor(ax, 89.5, 45.5, 13, 6, 'N × 64K', fc=HEAD_F, ec=HEAD, c=HEAD, size=6.4)
    tensor(ax, 89.5, 37.5, 13, 6, 'N × 27', fc=RATE_F, ec=RATE, c=RATE, size=6.4)
    T(ax, 96, 35.3, 'ratings', size=5.6, c=RATE)
    arrow(ax, 103, 48.5, 107.5, 45.0)
    arrow(ax, 103, 40.5, 107.5, 43.0)
    block(ax, 108, 39.5, 15, 9, 'encoding', 'ridge', fc='white', ec=INK, size=6.4, subsize=6.4)
    fire(ax, 122, 47.8, 0.65)
    arrow(ax, 123.5, 44, 127.5, 44)
    img(ax, 'cortex_partition.png', 128, 36.5, 24, border=False, trim=True)
    for k, (lab, c) in enumerate((('head only', HEAD), ('shared', '#2A9D8F'), ('ratings only', RATE))):
        ax.add_patch(Rectangle((155, 52.0 - k * 3.6), 2.0, 2.0, fc=c, ec='none', zorder=5))
        T(ax, 157.8, 53.0 - k * 3.6, lab, size=5.8, ha='left')
    T(ax, 176, 34.6, 'per voxel, then per ROI (illustrative map)', size=5.2, c=GREY, ha='right', st='italic')
    # 5
    rbox(ax, 155, 36.2, 22, 6.6, fc='white', ec=HEAD, lw=0.6, ls=(0, (2, 1.2)))
    badge(ax, 157.6, 39.5, 5, c=HEAD, r=1.5, size=6)
    T(ax, 167.2, 39.5, 'ablate heads:\nvs random', size=5.4, c=HEAD, linespacing=1.15)

    # ---- row 6 ----
    head(ax, 89, 30.2, 6, 'Can fMRI alone recover them and predict emotion?')
    line(ax, [27.5, 30, 30], [16, 16, 16], c=BRAIN, lw=1.0)
    arrow(ax, 27.5, 16, 89, 16, c=BRAIN, lw=1.0)
    T(ax, 60, 18.0, 'voxels of held-out videos', size=5.8, c=BRAIN)
    block(ax, 89.5, 11.5, 13, 9, 'ridge', 'per person', fc=BRAIN_F, ec=BRAIN, size=6.6, subsize=5.6)
    fire(ax, 101.5, 19.6, 0.65)
    arrow(ax, 103, 16, 107, 16)
    tensor(ax, 107.5, 11.5, 15, 9, 'N × 64K', fc='white', ec=HEAD, c=HEAD, ls=(0, (2.2, 1.2)), size=6.6)
    T(ax, 115, 8.8, 'reconstructed', size=5.6, c=HEAD)
    arrow(ax, tx, 24, 115, 21, c=HEAD, lw=0.8, ls=(0, (2, 1.4)), rad=-0.15)
    T(ax, 102, 25.4, 'target', size=5.4, c=HEAD)
    arrow(ax, 123, 16, 127, 16)
    block(ax, 127.5, 11.5, 14, 9, 'readout', 'fit on VCE', fc=RATE_F, ec=RATE, size=6.6, subsize=5.6)
    snow(ax, 140.5, 19.6, 1.2)
    arrow(ax, 142, 16, 146, 16)
    rng = np.random.default_rng(9)
    pred = np.clip(np.array(P1374) * 0.7 + rng.normal(0.05, 0.04, 27), 0.01, None)
    bars(ax, 146.5, 12, pred, w=0.75, gap=0.2, hmax=10, hi=FEAR)
    T(ax, 159, 8.6, '27 predicted ratings', size=5.8, c=RATE)
    T(ax, 176, 4.0, 'scored against Cowen ratings; direct ridge fMRI → ratings as reference', size=5.2, c=GREY, ha='right', st='italic')
    save(fig, 'emobrain_ridge_overview')
    return fig


if __name__ == '__main__':
    fig1()
